// Spotpuls SSR Homepage Handler: / (and /index.html)
// Injects live Finnish spot prices, today's date, KPI summary, and 24h price table directly into HTML
// for instant Googlebot / AI crawler indexing and higher search CTR, cached at Vercel Edge CDN.

import fs from 'fs';
import path from 'path';
import { buildSpotpulsZoneResponse } from './v1/prices.js';

let cachedTemplate = null;

function loadTemplate() {
    if (cachedTemplate) return cachedTemplate;
    const p = path.join(process.cwd(), 'templates', 'index.html');
    cachedTemplate = fs.readFileSync(p, 'utf-8');
    return cachedTemplate;
}

function escHtml(s) {
    return String(s || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function fmtFi(val, digits = 2) {
    if (val === null || val === undefined || !Number.isFinite(Number(val))) return '—';
    return Number(val).toFixed(digits).replace('.', ',');
}

function formatFiDate(dateKey) {
    const m = String(dateKey || '').match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if (!m) return '';
    return `${Number(m[3])}.${Number(m[2])}.${m[1]}`;
}

export default async function handler(req, res) {
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    res.setHeader('Cache-Control', 'public, max-age=60, s-maxage=300, stale-while-revalidate=3600');
    res.setHeader('X-Content-Type-Options', 'nosniff');

    let html;
    try {
        html = loadTemplate();
    } catch (err) {
        return res.status(500).send('Spotpuls template unavailable');
    }

    try {
        const result = await Promise.race([
            buildSpotpulsZoneResponse({ zone: 'FI', vat: '1', currency: 'local', window: '3' }),
            new Promise((_, reject) => setTimeout(() => reject(new Error('ssr_timeout')), 2800))
        ]);

        const cur = result?.currentSlot;
        const sum = result?.summary;
        const today = result?.todaySlots || [];

        if (cur && sum && today.length > 0) {
            const fiDate = formatFiDate(cur.dateKey);
            const curStr = fmtFi(cur.spotPrice);
            const minStr = fmtFi(sum.todayMin);
            const avgStr = fmtFi(sum.todayAvg);
            const maxStr = fmtFi(sum.todayMax);

            const cheapSlot = today.reduce((a, b) => (b.spotPrice < a.spotPrice ? b : a), today[0]);
            const peakSlot = today.reduce((a, b) => (b.spotPrice > a.spotPrice ? b : a), today[0]);
            const cheapHr = `${String(cheapSlot.hour).padStart(2, '0')}:00`;
            const peakHr = `${String(peakSlot.hour).padStart(2, '0')}:00`;

            const dynTitle = `Pörssisähkö tänään ${fiDate}: nyt ${curStr} snt/kWh (halvin ${minStr} snt) | Spotpuls`;
            const dynDesc = `Pörssisähkön hinta tänään ${fiDate}: nyt ${curStr} snt/kWh, keskihinta ${avgStr} snt/kWh, halvin tunti ${cheapHr} (${minStr} snt) ja kallein ${peakHr} (${maxStr} snt). 7 vrk ennuste & siirtohintalaskuri.`;

            html = html
                .replace(/<title>[^<]*<\/title>/, `<title>${escHtml(dynTitle)}</title>`)
                .replace(/<meta name="description" content="[^"]*">/, `<meta name="description" content="${escHtml(dynDesc)}">`)
                .replace(/<meta property="og:title" content="[^"]*">/, `<meta property="og:title" content="${escHtml(dynTitle)}">`)
                .replace(/<meta property="og:description" content="[^"]*">/, `<meta property="og:description" content="${escHtml(dynDesc)}">`)
                .replace(/<meta name="twitter:title" content="[^"]*">/, `<meta name="twitter:title" content="${escHtml(dynTitle)}">`)
                .replace(/<meta name="twitter:description" content="[^"]*">/, `<meta name="twitter:description" content="${escHtml(dynDesc)}">`)
                .replace('<strong id="tel-spot">— snt/kWh</strong>', `<strong id="tel-spot">${escHtml(curStr)} snt/kWh</strong>`)
                .replace('<strong id="tel-wind">— MW</strong>', `<strong id="tel-wind">${Math.round(Number(cur.windMw || 0))} MW</strong>`);

            const summaryHtml =
                `<div class="summary-pill"><strong>Tänään ${escHtml(fiDate)} (FI):</strong> Nyt ${escHtml(curStr)} snt/kWh</div>` +
                `<div class="summary-pill">Keskiarvo: <strong>${escHtml(avgStr)} snt/kWh</strong></div>` +
                `<div class="summary-pill">Halvin (${escHtml(cheapHr)}): <strong>${escHtml(minStr)} snt/kWh</strong></div>` +
                `<div class="summary-pill">Kallein (${escHtml(peakHr)}): <strong>${escHtml(maxStr)} snt/kWh</strong></div>`;

            html = html.replace(
                '<div id="first-screen-summary-strip" class="first-screen-summary-strip" aria-live="polite"></div>',
                `<div id="first-screen-summary-strip" class="first-screen-summary-strip" aria-live="polite">${summaryHtml}</div>`
            );

            const rowsHtml = today.map((s) => {
                const h1 = String(s.hour).padStart(2, '0');
                const h2 = String((s.hour + 1) % 24).padStart(2, '0');
                return `<tr><td>${h1}:00 - ${h2}:00</td><td><strong>${escHtml(fmtFi(s.spotPrice))} snt/kWh</strong></td><td>${escHtml(fmtFi(s.minPrice))}–${escHtml(fmtFi(s.maxPrice))} snt/kWh</td><td>${escHtml(fmtFi(s.totalPrice))} snt/kWh</td><td>${Math.round(Number(s.windMw || 0))} MW · ${escHtml(fmtFi(s.tempC, 1))} °C</td></tr>`;
            }).join('');

            html = html.replace(
                '<tr><td colspan="5">Haetaan tuntikohtaista hintataulukkoa...</td></tr>',
                rowsHtml
            );
        }
    } catch (_) {
        // Fallback to static template HTML cleanly on upstream timeout/error
    }

    return res.status(200).send(html);
}
