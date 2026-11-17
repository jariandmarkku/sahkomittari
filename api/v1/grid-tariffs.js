// Spotpuls Public REST API v1: /api/v1/grid-tariffs
// Address / postal-code / coordinate lookup for Finnish Distribution System Operators (DSO / sähköverkkoyhtiöt),
// transfer tariff packages (general, night/time, seasonal), electricity tax, and geocoded coordinates (lat, lon).
// Powered by Spotpuls — https://spotpuls.app

import fs from 'fs';
import path from 'path';

const SITE_URL = 'https://spotpuls.app';
const GEOCODE_CACHE_TTL_MS = 24 * 60 * 60 * 1000;
const MAX_GEOCODE_CACHE = 500;
const RATE_LIMIT_WINDOW_MS = 60 * 1000;
const RATE_LIMIT_MAX_REQ = 30;
const MAX_RATE_BUCKETS = 2000;

let cachedDsoData = null;
const geocodeCache = new Map();
const rateLimitBuckets = new Map();

function loadDsoData() {
    if (cachedDsoData) return cachedDsoData;
    const p = path.join(process.cwd(), 'data', 'dso_data.json');
    cachedDsoData = JSON.parse(fs.readFileSync(p, 'utf-8'));
    return cachedDsoData;
}

function getClientIp(req) {
    const xff = req.headers?.['x-forwarded-for'];
    if (typeof xff === 'string' && xff.trim()) return xff.split(',')[0].trim();
    const realIp = req.headers?.['x-real-ip'];
    if (typeof realIp === 'string' && realIp.trim()) return realIp.trim();
    return req.socket?.remoteAddress || 'unknown';
}

function checkRateLimit(ip) {
    const now = Date.now();
    if (rateLimitBuckets.size > MAX_RATE_BUCKETS) {
        for (const [k, v] of rateLimitBuckets.entries()) {
            if (now >= v.resetAt) rateLimitBuckets.delete(k);
        }
        if (rateLimitBuckets.size > MAX_RATE_BUCKETS) rateLimitBuckets.clear();
    }
    let bucket = rateLimitBuckets.get(ip);
    if (!bucket || now >= bucket.resetAt) {
        bucket = { count: 0, resetAt: now + RATE_LIMIT_WINDOW_MS };
        rateLimitBuckets.set(ip, bucket);
    }
    bucket.count += 1;
    return {
        limited: bucket.count > RATE_LIMIT_MAX_REQ,
        limit: RATE_LIMIT_MAX_REQ,
        remaining: Math.max(0, RATE_LIMIT_MAX_REQ - bucket.count),
        resetEpochSec: Math.ceil(bucket.resetAt / 1000),
        retryAfterSec: Math.max(1, Math.ceil((bucket.resetAt - now) / 1000))
    };
}

function slugifyFi(text) {
    return String(text || '')
        .toLowerCase()
        .trim()
        .replace(/ä/g, 'a')
        .replace(/ö/g, 'o')
        .replace(/å/g, 'a')
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-+|-+$/g, '') || 'index';
}

function normalizePostal(raw) {
    const m = String(raw || '').match(/\b(\d{5})\b/);
    return m ? m[1] : null;
}

function round4(n) {
    return Number(Number(n).toFixed(4));
}

function round2(n) {
    return Number(Number(n).toFixed(2));
}

async function fetchJsonWithTimeout(url, timeoutMs = 3500) {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), timeoutMs);
    try {
        const res = await fetch(url, {
            signal: ctrl.signal,
            headers: {
                'User-Agent': 'Spotpuls/2.0 (+https://spotpuls.app; grid-tariffs-api)',
                'Accept': 'application/json'
            }
        });
        if (!res.ok) return null;
        return await res.json();
    } catch (_) {
        return null;
    } finally {
        clearTimeout(timer);
    }
}

async function geocodeAddress(query, countryCode = 'fi') {
    const key = `s:${countryCode}:${query.toLowerCase().trim()}`;
    const cached = geocodeCache.get(key);
    if (cached && Date.now() - cached.ts < GEOCODE_CACHE_TTL_MS) return cached.data;

    const cc = /^[a-z]{2}$/i.test(countryCode) ? `&countrycodes=${countryCode.toLowerCase()}` : '';
    const url = `https://nominatim.openstreetmap.org/search?format=jsonv2&addressdetails=1&limit=1${cc}&q=${encodeURIComponent(query)}`;
    const rows = await fetchJsonWithTimeout(url, 3500);
    if (!Array.isArray(rows) || rows.length === 0) return null;

    const hit = rows[0];
    const addr = hit.address || {};
    const out = {
        lat: Number(hit.lat),
        lon: Number(hit.lon),
        displayName: hit.display_name || query,
        postalCode: normalizePostal(addr.postcode),
        city: addr.city || addr.town || addr.municipality || addr.village || addr.county || null,
        countryCode: (addr.country_code || countryCode || 'fi').toUpperCase(),
        source: 'nominatim'
    };
    if (geocodeCache.size >= MAX_GEOCODE_CACHE) {
        const oldest = geocodeCache.keys().next().value;
        if (oldest !== undefined) geocodeCache.delete(oldest);
    }
    geocodeCache.set(key, { ts: Date.now(), data: out });
    return out;
}

async function reverseGeocode(lat, lon) {
    const key = `r:${lat.toFixed(4)},${lon.toFixed(4)}`;
    const cached = geocodeCache.get(key);
    if (cached && Date.now() - cached.ts < GEOCODE_CACHE_TTL_MS) return cached.data;

    const url = `https://nominatim.openstreetmap.org/reverse?format=jsonv2&addressdetails=1&lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}`;
    const hit = await fetchJsonWithTimeout(url, 3500);
    if (!hit || hit.error) return null;

    const addr = hit.address || {};
    const out = {
        lat: Number(hit.lat ?? lat),
        lon: Number(hit.lon ?? lon),
        displayName: hit.display_name || null,
        postalCode: normalizePostal(addr.postcode),
        city: addr.city || addr.town || addr.municipality || addr.village || addr.county || null,
        countryCode: (addr.country_code || 'FI').toUpperCase(),
        source: 'nominatim_reverse'
    };
    if (geocodeCache.size >= MAX_GEOCODE_CACHE) {
        const oldest = geocodeCache.keys().next().value;
        if (oldest !== undefined) geocodeCache.delete(oldest);
    }
    geocodeCache.set(key, { ts: Date.now(), data: out });
    return out;
}

function resolveDsoForFinland(dsoData, postalCode, cityHint) {
    const munis = dsoData.municipalities || [];
    const rules = dsoData.postalPrefixRules || [];
    const companies = dsoData.companies || {};

    let primaryId = null;
    let altIds = [];
    let matchedCity = cityHint || null;
    let matchType = 'fallback';

    if (postalCode) {
        const exact = munis.find((m) => m.postal === postalCode);
        if (exact) {
            primaryId = exact.primary;
            altIds = exact.alt || [];
            matchedCity = exact.name;
            matchType = 'postal_exact';
        } else {
            const pNum = Number(postalCode);
            const ranged = munis.find((m) => {
                const parts = String(m.postal_range || '').split(/[-–]/);
                if (parts.length !== 2) return false;
                const lo = Number(parts[0].trim());
                const hi = Number(parts[1].trim());
                return Number.isFinite(lo) && Number.isFinite(hi) && pNum >= lo && pNum <= hi;
            });
            if (ranged) {
                primaryId = ranged.primary;
                altIds = ranged.alt || [];
                matchedCity = ranged.name;
                matchType = 'postal_range';
            }
        }
    }

    if (!primaryId && cityHint) {
        const needle = cityHint.toLowerCase().trim();
        const byCity = munis.find((m) => m.name.toLowerCase() === needle || needle.includes(m.name.toLowerCase()));
        if (byCity) {
            primaryId = byCity.primary;
            altIds = byCity.alt || [];
            matchedCity = byCity.name;
            matchType = 'municipality_name';
        }
    }

    if (!primaryId && postalCode) {
        const pref = postalCode.slice(0, 2);
        const rule = rules.find((r) => r.prefix === pref);
        if (rule) {
            primaryId = rule.dso;
            altIds = rule.alt || [];
            if (!matchedCity) matchedCity = rule.city;
            matchType = 'postal_prefix';
        }
    }

    if (!primaryId) {
        primaryId = 'helen';
        matchedCity = matchedCity || 'Helsinki';
    }

    return {
        primary: companies[primaryId] || companies.helen,
        alternatives: altIds.map((id) => companies[id]).filter(Boolean),
        matchedCity,
        matchType
    };
}

function formatOperatorTariffs(comp, dsoData, includeVat) {
    const vatRate = Number(dsoData.vatRate || 1.255);
    const div = includeVat ? 1.0 : vatRate;
    const taxEnergy = includeVat
        ? Number(dsoData.electricityTaxInclVat || 2.8275)
        : Number(dsoData.electricityTaxVat0 || 2.253);

    const genEnergy = round2(comp.general_c_kwh / div);
    const dayEnergy = round2(comp.day_c_kwh / div);
    const nightEnergy = round2(comp.night_c_kwh / div);
    const winterDayEnergy = round2(comp.winter_day_c_kwh / div);
    const otherEnergy = round2(comp.other_c_kwh / div);

    return {
        operator: {
            id: comp.id,
            name: comp.name,
            shortName: comp.short_name,
            regionDesc: comp.region_desc,
            website: comp.website,
            dashboardUrl: `${SITE_URL}/verkkoyhtiot/${slugifyFi(comp.short_name)}.html`
        },
        electricityTax: {
            energyCentsPerKwh: round4(taxEnergy),
            vat0CentsPerKwh: Number(dsoData.electricityTaxVat0 || 2.253),
            inclVatCentsPerKwh: Number(dsoData.electricityTaxInclVat || 2.8275),
            description: 'Sähkövero luokka I + huoltovarmuusmaksu'
        },
        tariffs: {
            general: {
                id: 'general',
                name: 'Yleissiirto',
                energyCentsPerKwh: genEnergy,
                totalFixedCentsPerKwh: round4(genEnergy + taxEnergy),
                monthlyBaseEur: round2(comp.general_base_eur / div)
            },
            time: {
                id: 'time',
                name: 'Yösiirto (Aikasiirto)',
                dayCentsPerKwh: dayEnergy,
                nightCentsPerKwh: nightEnergy,
                dayHours: '07:00-22:00',
                nightHours: '22:00-07:00',
                totalFixedDayCentsPerKwh: round4(dayEnergy + taxEnergy),
                totalFixedNightCentsPerKwh: round4(nightEnergy + taxEnergy),
                monthlyBaseEur: round2(comp.time_base_eur / div)
            },
            season: {
                id: 'season',
                name: 'Kausisiirto',
                winterDayCentsPerKwh: winterDayEnergy,
                otherCentsPerKwh: otherEnergy,
                winterDayRule: 'Nov 1 - Mar 31, Mon-Sat 07:00-22:00',
                totalFixedWinterDayCentsPerKwh: round4(winterDayEnergy + taxEnergy),
                totalFixedOtherCentsPerKwh: round4(otherEnergy + taxEnergy),
                monthlyBaseEur: round2(comp.season_base_eur / div)
            }
        }
    };
}

export default async function handler(req, res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Accept');
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('Cache-Control', 'public, max-age=300, s-maxage=3600, stale-while-revalidate=86400');
    res.setHeader('X-Powered-By-Data', `Spotpuls (${SITE_URL})`);

    if (req.method === 'OPTIONS') return res.status(200).end();
    if (req.method !== 'GET' && req.method !== 'HEAD') {
        res.setHeader('Allow', 'GET, HEAD, OPTIONS');
        return res.status(405).json({ error: 'Method Not Allowed. Use GET.' });
    }

    const rl = checkRateLimit(getClientIp(req));
    res.setHeader('X-RateLimit-Limit', String(rl.limit));
    res.setHeader('X-RateLimit-Remaining', String(rl.remaining));
    res.setHeader('X-RateLimit-Reset', String(rl.resetEpochSec));
    if (rl.limited) {
        res.setHeader('Retry-After', String(rl.retryAfterSec));
        res.setHeader('Cache-Control', 'no-store');
        return res.status(429).json({
            error: 'Too Many Requests',
            message: `Rate limit exceeded (${rl.limit} requests/minute per IP).`,
            retryAfterSeconds: rl.retryAfterSec
        });
    }

    try {
        const q = req.query || {};
        const rawAddress = String(q.address || '').trim();
        const rawPostal = normalizePostal(q.postalCode || q.postal || q.zip || rawAddress);
        const country = String(q.country || 'FI').trim().toUpperCase() || 'FI';
        const includeVat = String(q.vat ?? '1') !== '0';
        const latNum = q.lat !== undefined && q.lat !== '' ? Number(q.lat) : null;
        const lonNum = q.lon !== undefined && q.lon !== '' ? Number(q.lon) : null;
        const hasCoords = Number.isFinite(latNum) && Number.isFinite(lonNum)
            && latNum >= -90 && latNum <= 90 && lonNum >= -180 && lonNum <= 180;

        if (!rawAddress && !rawPostal && !hasCoords) {
            return res.status(400).json({
                status: 'error',
                provider: 'Spotpuls',
                message: 'Provide at least one of: address, postalCode, or lat & lon.',
                example: `${SITE_URL}/api/v1/grid-tariffs?address=Keskustie+1,+35300+Orivesi&vat=1`
            });
        }

        const dsoData = loadDsoData();
        let geo = null;

        if (rawAddress) {
            geo = await geocodeAddress(rawAddress, country);
        } else if (hasCoords) {
            geo = await reverseGeocode(latNum, lonNum);
        } else if (rawPostal) {
            const muniHint = (dsoData.municipalities || []).find((m) => m.postal === rawPostal)?.name || '';
            geo = await geocodeAddress(`${rawPostal} ${muniHint}`.trim(), country);
        }

        const effectiveCountry = (geo?.countryCode || country || 'FI').toUpperCase();
        const effectivePostal = rawPostal || geo?.postalCode || null;
        const effectiveLat = hasCoords ? latNum : (geo?.lat ?? null);
        const effectiveLon = hasCoords ? lonNum : (geo?.lon ?? null);

        if (effectiveCountry !== 'FI') {
            return res.status(200).json({
                status: 'ok',
                supported: false,
                provider: 'Spotpuls',
                location: {
                    query: rawAddress || rawPostal || `${effectiveLat},${effectiveLon}`,
                    country: effectiveCountry,
                    postalCode: effectivePostal,
                    city: geo?.city || null,
                    displayName: geo?.displayName || null,
                    lat: effectiveLat,
                    lon: effectiveLon,
                    coordinatesSource: hasCoords ? 'query' : (geo?.source || null)
                },
                message: 'Detailed postal DSO grid tariff database currently covers Finland (FI). Coordinates were resolved.'
            });
        }

        const resolved = resolveDsoForFinland(dsoData, effectivePostal, geo?.city || null);
        const primaryFormatted = formatOperatorTariffs(resolved.primary, dsoData, includeVat);
        const alternatives = resolved.alternatives.map((alt) => formatOperatorTariffs(alt, dsoData, includeVat));
        const dashUrl = primaryFormatted.operator.dashboardUrl;

        res.setHeader('Link', `<${dashUrl}>; rel="canonical", <${SITE_URL}/openapi.json>; rel="service-desc", <${SITE_URL}/api-docs/>; rel="documentation"`);

        return res.status(200).json({
            status: 'ok',
            supported: true,
            citation: `Source: Spotpuls (${dashUrl})`,
            meta: {
                provider: 'Spotpuls',
                website: SITE_URL,
                vatIncluded: includeVat,
                vatRatePercent: includeVat ? 25.5 : 0,
                unit: 'snt/kWh',
                currency: 'EUR',
                fuseSizeDefault: '3x25A',
                pricesApiUrl: `${SITE_URL}/api/v1/prices?zone=FI&vat=${includeVat ? 1 : 0}`
            },
            location: {
                query: rawAddress || rawPostal || `${effectiveLat},${effectiveLon}`,
                country: 'FI',
                zone: 'FI',
                postalCode: effectivePostal,
                city: resolved.matchedCity || geo?.city || null,
                displayName: geo?.displayName || null,
                lat: effectiveLat,
                lon: effectiveLon,
                coordinatesSource: hasCoords ? 'query' : (geo?.source || null),
                dsoMatchType: resolved.matchType
            },
            operator: primaryFormatted.operator,
            electricityTax: primaryFormatted.electricityTax,
            tariffs: primaryFormatted.tariffs,
            alternatives
        });
    } catch (err) {
        console.error('Spotpuls grid-tariffs error:', err);
        res.setHeader('Cache-Control', 'no-store');
        return res.status(500).json({
            status: 'error',
            provider: 'Spotpuls',
            website: SITE_URL,
            message: 'Unable to resolve grid tariffs right now. Please retry shortly.'
        });
    }
}
