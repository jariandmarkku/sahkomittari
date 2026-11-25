// Spotpuls Multi-Country, DSO & Municipality SSR Handler: /, /:country/, /verkkoyhtiot/:slug.html, /paikkakunnat/:slug.html
// Injects live spot prices, today's date, KPI summary, transfer fees, and 24h price table directly into HTML
// for instant Googlebot / AI crawler indexing and higher search CTR, cached at Vercel Edge CDN.

import fs from 'fs';
import path from 'path';
import { buildSpotpulsZoneResponse } from './v1/prices.js';

const COUNTRY_SSR = {
    fi: { zone: 'FI', unit: 'snt/kWh', comma: true, tpl: (d, n, m) => `Pörssisähkö tänään ${d}: nyt ${n} snt/kWh (halvin ${m} snt) | Spotpuls`, desc: (d, n, a, ch, m, ph, x) => `Pörssisähkön hinta tänään ${d}: nyt ${n} snt/kWh, keskihinta ${a} snt/kWh, halvin ${ch} (${m} snt) ja kallein ${ph} (${x} snt). 7 vrk ennuste & siirtohintalaskuri.`, nowLbl: 'Nyt', avgLbl: 'Keskiarvo', minLbl: 'Halvin', maxLbl: 'Kallein' },
    en: { zone: 'DE-LU', unit: 'ct/kWh', comma: false, tpl: (d, n, m) => `Electricity Spot Price Today ${d}: Now ${n} ct/kWh (Min ${m} ct) | Spotpuls`, desc: (d, n, a, ch, m, ph, x) => `Day-ahead electricity spot price today ${d}: now ${n} ct/kWh, avg ${a} ct/kWh, cheapest ${ch} (${m} ct), peak ${ph} (${x} ct). 7-day forecast & open API.`, nowLbl: 'Now', avgLbl: 'Avg', minLbl: 'Cheapest', maxLbl: 'Peak' },
    se: { zone: 'SE3', unit: 'öre/kWh', comma: true, tpl: (d, n, m) => `Elpris timme för timme & timspotpris ${d} (SE3): ${n} öre/kWh | Spotpuls`, desc: (d, n, a, ch, m, ph, x) => `Elpris timme för timme, timspotpris & spotpris el idag ${d} (SE1–SE4): nu ${n} öre/kWh, snitt ${a} öre/kWh, billigast ${ch} (${m} öre), dyrast ${ph} (${x} öre).`, nowLbl: 'Nu', avgLbl: 'Snitt', minLbl: 'Billigast', maxLbl: 'Dyrast' },
    no: { zone: 'NO1', unit: 'øre/kWh', comma: true, tpl: (d, n, m) => `Strømpris time for time ${d} (NO1): nå ${n} øre/kWh (lavest ${m} øre) | Spotpuls`, desc: (d, n, a, ch, m, ph, x) => `Strømpris time for time & spotpris strøm idag ${d} (NO1–NO5): nå ${n} øre/kWh, snitt ${a} øre/kWh, billigst ${ch} (${m} øre), dyrest ${ph} (${x} øre). 7-dagers strømprognose.`, nowLbl: 'Nå', avgLbl: 'Snitt', minLbl: 'Billigst', maxLbl: 'Dyrest' },
    dk: { zone: 'DK2', unit: 'øre/kWh', comma: true, tpl: (d, n, m) => `Elpriser time for time & pris på el lige nu ${d}: ${n} øre/kWh | Spotpuls`, desc: (d, n, a, ch, m, ph, x) => `Elpriser Danmark (DK1–DK2) & pris på el lige nu i dag ${d}: nu ${n} øre/kWh, snit ${a} øre/kWh, billigst ${ch} (${m} øre), dyrest ${ph} (${x} øre).`, nowLbl: 'Nu', avgLbl: 'Snit', minLbl: 'Billigst', maxLbl: 'Dyrest' },
    ee: { zone: 'EE', unit: 'senti/kWh', comma: true, tpl: (d, n, m) => `Börsielekter täna ${d}: praegu ${n} senti/kWh (soodsaim ${m}) | Spotpuls`, desc: (d, n, a, ch, m, ph, x) => `Elektri börsihind täna ${d} (EE): praegu ${n} senti/kWh, keskmine ${a}, odavaim ${ch} (${m}), kalleim ${ph} (${x}). 7 päeva prognoos.`, nowLbl: 'Praegu', avgLbl: 'Keskmine', minLbl: 'Odavaim', maxLbl: 'Kalleim' },
    lv: { zone: 'LV', unit: 'centi/kWh', comma: true, tpl: (d, n, m) => `Elektrības biržas cena pa stundām šodien ${d}: ${n} centi/kWh (min ${m}) | Spotpuls`, desc: (d, n, a, ch, m, ph, x) => `Elektrības biržas cena pa stundām šodien ${d} (LV): tagad ${n} centi/kWh, vidējā ${a}, lētākā ${ch} (${m}), dārgākā ${ph} (${x}). 7 dienu prognoze.`, nowLbl: 'Tagad', avgLbl: 'Vidējā', minLbl: 'Lētākā', maxLbl: 'Dārgākā' },
    lt: { zone: 'LT', unit: 'ct/kWh', comma: true, tpl: (d, n, m) => `Elektros kaina šiandien ${d}: dabar ${n} ct/kWh (min ${m}) | Spotpuls`, desc: (d, n, a, ch, m, ph, x) => `Elektros biržos kaina šiandien ${d} (LT): dabar ${n} ct/kWh, vidurkis ${a}, pigiausia ${ch} (${m}), brangiausia ${ph} (${x}). 7 dienų prognozė.`, nowLbl: 'Dabar', avgLbl: 'Vidurkis', minLbl: 'Pigiausia', maxLbl: 'Brangiausia' },
    de: { zone: 'DE-LU', unit: 'ct/kWh', comma: true, tpl: (d, n, m) => `Strompreis heute ${d}: aktuell ${n} ct/kWh (ab ${m} ct) | Spotpuls`, desc: (d, n, a, ch, m, ph, x) => `Börsenstrompreis Deutschland heute ${d} (EPEX): aktuell ${n} ct/kWh, Schnitt ${a} ct/kWh, günstigste Stunde ${ch} (${m} ct), Spitze ${ph} (${x} ct). 7-Tage-Prognose.`, nowLbl: 'Jetzt', avgLbl: 'Schnitt', minLbl: 'Tiefstwert', maxLbl: 'Spitze' },
    at: { zone: 'AT', unit: 'ct/kWh', comma: true, tpl: (d, n, m) => `Strompreis Österreich heute ${d}: ${n} ct/kWh (ab ${m} ct) | Spotpuls`, desc: (d, n, a, ch, m, ph, x) => `Börsenpreis Strom Österreich heute ${d} (AT): aktuell ${n} ct/kWh, Schnitt ${a} ct/kWh, günstigste Stunde ${ch} (${m} ct), Spitze ${ph} (${x} ct).`, nowLbl: 'Jetzt', avgLbl: 'Schnitt', minLbl: 'Tiefstwert', maxLbl: 'Spitze' },
    ch: { zone: 'CH', unit: 'Rp./kWh', comma: false, tpl: (d, n, m) => `Strompreis Schweiz heute ${d}: ${n} Rp./kWh (ab ${m} Rp.) | Spotpuls`, desc: (d, n, a, ch, m, ph, x) => `Strompreis Börse Schweiz heute ${d} (CH): aktuell ${n} Rp./kWh, Schnitt ${a}, tiefste Stunde ${ch} (${m}), höchste ${ph} (${x}). 7-Tage-Prognose.`, nowLbl: 'Jetzt', avgLbl: 'Schnitt', minLbl: 'Tiefstwert', maxLbl: 'Spitze' },
    nl: { zone: 'NL', unit: 'ct/kWh', comma: true, tpl: (d, n, m) => `Actuele stroomprijzen ${d}: nu ${n} ct/kWh (EPEX voorspelling) | Spotpuls`, desc: (d, n, a, ch, m, ph, x) => `Actuele stroomprijzen & EPEX voorspelling Nederland vandaag ${d}: nu ${n} ct/kWh, gemiddeld ${a} ct/kWh, goedkoopst ${ch} (${m} ct), duurste ${ph} (${x} ct). 7-daagse verwachting.`, nowLbl: 'Nu', avgLbl: 'Gemiddeld', minLbl: 'Goedkoopst', maxLbl: 'Duurste' },
    be: { zone: 'BE', unit: 'ct/kWh', comma: true, tpl: (d, n, m) => `Actuele stroomprijs België (EPEX / Belpex) ${d}: nu ${n} ct/kWh (min ${m} ct) | Spotpuls`, desc: (d, n, a, ch, m, ph, x) => `Actuele stroomprijs België (EPEX / Belpex) vandaag ${d}: nu ${n} ct/kWh, gemiddeld ${a}, goedkoopst ${ch} (${m} ct), duurste ${ph} (${x} ct).`, nowLbl: 'Nu', avgLbl: 'Gemiddeld', minLbl: 'Goedkoopst', maxLbl: 'Duurste' },
    fr: { zone: 'FR', unit: 'ct/kWh', comma: true, tpl: (d, n, m) => `Prix électricité aujourd'hui ${d}: ${n} ct/kWh (min ${m} ct) | Spotpuls`, desc: (d, n, a, ch, m, ph, x) => `Prix spot EPEX France aujourd'hui ${d}: maintenant ${n} ct/kWh, moyenne ${a} ct/kWh, heure la moins chère ${ch} (${m} ct), pic ${ph} (${x} ct).`, nowLbl: 'Maintenant', avgLbl: 'Moyenne', minLbl: 'Min', maxLbl: 'Max' },
    gb: { zone: 'GB', unit: 'p/kWh', comma: false, tpl: (d, n, m) => `Current UK Electricity Price per kWh Today ${d}: ${n} p/kWh (Min ${m} p) | Spotpuls`, desc: (d, n, a, ch, m, ph, x) => `Current UK electricity price per kWh & UK power prices today ${d}: now ${n} p/kWh, avg ${a} p/kWh, cheapest ${ch} (${m} p), peak ${ph} (${x} p). 7-day forecast.`, nowLbl: 'Now', avgLbl: 'Avg', minLbl: 'Cheapest', maxLbl: 'Peak' },
    ie: { zone: 'IE-SEM', unit: 'c/kWh', comma: false, tpl: (d, n, m) => `Ireland Electricity Price Today ${d}: ${n} c/kWh (SEMOpx) | Spotpuls`, desc: (d, n, a, ch, m, ph, x) => `Ireland IE-SEM hourly electricity price today ${d}: now ${n} c/kWh, avg ${a} c/kWh, cheapest ${ch} (${m} c), peak ${ph} (${x} c).`, nowLbl: 'Now', avgLbl: 'Avg', minLbl: 'Cheapest', maxLbl: 'Peak' },
    es: { zone: 'ES', unit: 'cént./kWh', comma: true, tpl: (d, n, m) => `Precio de la luz hoy hora a hora ${d}: ${n} cént./kWh (OMIE / PVPC) | Spotpuls`, desc: (d, n, a, ch, m, ph, x) => `Precio de la luz hoy hora a hora & precio kilovatio hora hoy ${d} (OMIE/PVPC): ahora ${n} cént./kWh, media ${a}, hora valle más barata ${ch} (${m}), más cara ${ph} (${x}).`, nowLbl: 'Ahora', avgLbl: 'Media', minLbl: 'Más barata', maxLbl: 'Más cara' },
    pt: { zone: 'PT', unit: 'cênt./kWh', comma: true, tpl: (d, n, m) => `OMIE spot hoje e preço da eletricidade ${d}: ${n} cênt./kWh | Spotpuls`, desc: (d, n, a, ch, m, ph, x) => `OMIE spot hoje e preço da eletricidade em Portugal ${d}: agora ${n} cênt./kWh, média ${a}, mais barata ${ch} (${m}), mais cara ${ph} (${x}). Previsão 7 dias.`, nowLbl: 'Agora', avgLbl: 'Média', minLbl: 'Mínimo', maxLbl: 'Máximo' },
    it: { zone: 'IT-North', unit: 'cent./kWh', comma: true, tpl: (d, n, m) => `Prezzo energia oggi ${d} (PUN / GME): ${n} cent./kWh | Spotpuls`, desc: (d, n, a, ch, m, ph, x) => `Prezzo zonale orario GME e PUN oggi ${d}: ora ${n} cent./kWh, media ${a}, ora più economica ${ch} (${m}), picco ${ph} (${x}).`, nowLbl: 'Ora', avgLbl: 'Media', minLbl: 'Minimo', maxLbl: 'Massimo' },
    pl: { zone: 'PL', unit: 'gr/kWh', comma: true, tpl: (d, n, m) => `Cena prądu dziś ${d}: teraz ${n} gr/kWh (TGE / RDN) | Spotpuls`, desc: (d, n, a, ch, m, ph, x) => `Godzinowa cena prądu TGE dziś ${d} (PL): teraz ${n} gr/kWh, średnia ${a}, najtaniej ${ch} (${m}), najdrożej ${ph} (${x}). Prognoza 7 dni.`, nowLbl: 'Teraz', avgLbl: 'Średnia', minLbl: 'Najtaniej', maxLbl: 'Najdrożej' },
    cz: { zone: 'CZ', unit: 'Kč/kWh', comma: true, tpl: (d, n, m) => `Spotová cena elektřiny dnes (Cena OTE) ${d}: ${n} Kč/kWh | Spotpuls`, desc: (d, n, a, ch, m, ph, x) => `Spotová cena elektřiny dnes (Cena OTE) ${d} (CZ): nyní ${n} Kč/kWh, průměr ${a}, nejlevnější ${ch} (${m}), nejdražší ${ph} (${x}).`, nowLbl: 'Nyní', avgLbl: 'Průměr', minLbl: 'Nejlevnější', maxLbl: 'Nejdražší' },
    sk: { zone: 'SK', unit: 'ct/kWh', comma: true, tpl: (d, n, m) => `Spotové ceny elektriny dnes (OKTE) ${d}: ${n} ct/kWh | Spotpuls`, desc: (d, n, a, ch, m, ph, x) => `Spotové ceny elektriny dnes (OKTE) ${d} (SK): teraz ${n} ct/kWh, priemer ${a}, najlacnejšia ${ch} (${m}), najdrahšia ${ph} (${x}).`, nowLbl: 'Teraz', avgLbl: 'Priemer', minLbl: 'Najlacnejšia', maxLbl: 'Najdrahšia' },
    hu: { zone: 'HU', unit: 'Ft/kWh', comma: true, tpl: (d, n, m) => `Áramár ma ${d} (HUPX): ${n} Ft/kWh (min ${m} Ft) | Spotpuls`, desc: (d, n, a, ch, m, ph, x) => `Órás HUPX áramár ma ${d} (HU): most ${n} Ft/kWh, átlag ${a}, legolcsóbb ${ch} (${m}), legdrágább ${ph} (${x}). 7 napos előrejelzés.`, nowLbl: 'Most', avgLbl: 'Átlag', minLbl: 'Legolcsóbb', maxLbl: 'Legdrágább' },
    ro: { zone: 'RO', unit: 'bani/kWh', comma: true, tpl: (d, n, m) => `Preț PZU OPCOM & spot energie electrică ${d}: ${n} bani/kWh | Spotpuls`, desc: (d, n, a, ch, m, ph, x) => `Preț PZU OPCOM & spot energie electrică azi ${d} (RO): acum ${n} bani/kWh, medie ${a}, cea mai ieftină ${ch} (${m}), vârf ${ph} (${x}). Prognoză 7 zile.`, nowLbl: 'Acum', avgLbl: 'Medie', minLbl: 'Minim', maxLbl: 'Maxim' },
    bg: { zone: 'BG', unit: 'ст./kWh', comma: true, tpl: (d, n, m) => `IBEX цени (ИБЕКС) & цена на тока ден напред ${d}: ${n} ст./kWh | Spotpuls`, desc: (d, n, a, ch, m, ph, x) => `IBEX цени (ИБЕКС БГ) & цена на тока ден напред днес ${d}: сега ${n} ст./kWh, средно ${a}, най-евтино ${ch} (${m}), пик ${ph} (${x}).`, nowLbl: 'Сега', avgLbl: 'Средно', minLbl: 'Мин', maxLbl: 'Макс' },
    si: { zone: 'SI', unit: 'c/kWh', comma: true, tpl: (d, n, m) => `Cena elektrike danes & omrežnina ${d} (BSP SouthPool): ${n} c/kWh | Spotpuls`, desc: (d, n, a, ch, m, ph, x) => `Cena elektrike danes & omrežnina BSP SouthPool ${d} (SI): zdaj ${n} c/kWh, povprečje ${a}, najceneje ${ch} (${m}), najdražje ${ph} (${x}).`, nowLbl: 'Zdaj', avgLbl: 'Povprečje', minLbl: 'Najceneje', maxLbl: 'Najdražje' },
    hr: { zone: 'HR', unit: 'c/kWh', comma: true, tpl: (d, n, m) => `CROPEX cijena struje i električne energije ${d}: ${n} c/kWh | Spotpuls`, desc: (d, n, a, ch, m, ph, x) => `CROPEX cijena struje i električne energije danas ${d} (HR): sada ${n} c/kWh, prosjek ${a}, najjeftinije ${ch} (${m}), najskuplje ${ph} (${x}).`, nowLbl: 'Sada', avgLbl: 'Prosjek', minLbl: 'Najjeftinije', maxLbl: 'Najskuplje' },
    gr: { zone: 'GR', unit: 'λεπτά/kWh', comma: true, tpl: (d, n, m) => `Τιμή ρεύματος σήμερα ${d} (HEnEx): ${n} λεπτά/kWh | Spotpuls`, desc: (d, n, a, ch, m, ph, x) => `Ωριαία τιμή ηλεκτρικού ρεύματος HEnEx σήμερα ${d} (GR): τώρα ${n} λεπτά/kWh, μέσος όρος ${a}, φθηνότερη ${ch} (${m}), ακριβότερη ${ph} (${x}).`, nowLbl: 'Τώρα', avgLbl: 'Μέσος', minLbl: 'Ελάχιστο', maxLbl: 'Μέγιστο' }
};

const templateCache = new Map();
let cachedDsoData = null;

function loadDsoData() {
    if (cachedDsoData) return cachedDsoData;
    const p = path.join(process.cwd(), 'data', 'dso_data.json');
    cachedDsoData = JSON.parse(fs.readFileSync(p, 'utf-8'));
    return cachedDsoData;
}

function loadTemplateByKey(cacheKey, relPath) {
    if (templateCache.has(cacheKey)) return templateCache.get(cacheKey);
    const p = path.join(process.cwd(), 'templates', relPath);
    const html = fs.readFileSync(p, 'utf-8');
    templateCache.set(cacheKey, html);
    return html;
}

function escHtml(s) {
    return String(s || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function fmtNum(val, comma = true, digits = 2) {
    if (val === null || val === undefined || !Number.isFinite(Number(val))) return '—';
    const str = Number(val).toFixed(digits);
    return comma ? str.replace('.', ',') : str;
}

function formatDateEu(dateKey) {
    const m = String(dateKey || '').match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if (!m) return '';
    return `${Number(m[3])}.${Number(m[2])}.${m[1]}`;
}

export default async function handler(req, res) {
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    res.setHeader('Cache-Control', 'public, max-age=60, s-maxage=300, stale-while-revalidate=3600');
    res.setHeader('X-Content-Type-Options', 'nosniff');

    const rawDso = req.query?.dso ? String(req.query.dso).toLowerCase().replace(/[^a-z0-9-]/g, '') : '';
    const rawMuni = req.query?.muni ? String(req.query.muni).toLowerCase().replace(/[^a-z0-9-]/g, '') : '';
    const rawCountry = String(req.query?.country || 'fi').toLowerCase().replace(/[^a-z]/g, '');

    const isDsoOrMuni = Boolean(rawDso || rawMuni);
    const cid = isDsoOrMuni ? 'fi' : (COUNTRY_SSR[rawCountry] ? rawCountry : 'fi');
    const cfg = COUNTRY_SSR[cid];

    let html;
    try {
        if (rawDso) {
            html = loadTemplateByKey(`dso:${rawDso}`, path.join('verkkoyhtiot', `${rawDso}.html`));
        } else if (rawMuni) {
            html = loadTemplateByKey(`muni:${rawMuni}`, path.join('paikkakunnat', `${rawMuni}.html`));
        } else {
            const rel = cid === 'fi' ? 'index.html' : path.join(cid, 'index.html');
            html = loadTemplateByKey(`country:${cid}`, rel);
        }
    } catch (_) {
        return res.status(404).send('Page not found');
    }

    try {
        let totalFixedTransfer = null;
        let dsoComp = null;
        if (isDsoOrMuni) {
            const dsoMatch = html.match(/data-preset-dso="([^"]+)"/);
            if (dsoMatch) {
                const dsoData = loadDsoData();
                dsoComp = dsoData.companies?.[dsoMatch[1]] || null;
                if (dsoComp) {
                    totalFixedTransfer = Number((Number(dsoComp.general_c_kwh) + Number(dsoData.electricityTaxInclVat)).toFixed(2));
                }
            }
        }

        const priceQuery = { zone: cfg.zone, vat: '1', currency: 'local', window: '3' };
        if (totalFixedTransfer !== null) {
            priceQuery.transfer = String(totalFixedTransfer);
        }

        const result = await Promise.race([
            buildSpotpulsZoneResponse(priceQuery),
            new Promise((_, reject) => setTimeout(() => reject(new Error('ssr_timeout')), 2800))
        ]);

        const cur = result?.currentSlot;
        const sum = result?.summary;
        const today = result?.todaySlots || [];

        if (cur && sum && today.length > 0) {
            const dateStr = formatDateEu(cur.dateKey);
            const curStr = fmtNum(cur.spotPrice, cfg.comma);
            const curTotStr = fmtNum(cur.totalPrice, cfg.comma);
            const minStr = fmtNum(sum.todayMin, cfg.comma);
            const avgStr = fmtNum(sum.todayAvg, cfg.comma);
            const maxStr = fmtNum(sum.todayMax, cfg.comma);

            const cheapSlot = today.reduce((a, b) => (b.spotPrice < a.spotPrice ? b : a), today[0]);
            const peakSlot = today.reduce((a, b) => (b.spotPrice > a.spotPrice ? b : a), today[0]);
            const cheapHr = `${String(cheapSlot.hour).padStart(2, '0')}:00`;
            const peakHr = `${String(peakSlot.hour).padStart(2, '0')}:00`;
            const unit = result.unitLabel || cfg.unit;

            if (!isDsoOrMuni) {
                const dynTitle = cfg.tpl(dateStr, curStr, minStr);
                const dynDesc = cfg.desc(dateStr, curStr, avgStr, cheapHr, minStr, peakHr, maxStr);
                html = html
                    .replace(/<title>[^<]*<\/title>/, `<title>${escHtml(dynTitle)}</title>`)
                    .replace(/<meta name="description" content="[^"]*">/, `<meta name="description" content="${escHtml(dynDesc)}">`)
                    .replace(/<meta property="og:title" content="[^"]*">/, `<meta property="og:title" content="${escHtml(dynTitle)}">`)
                    .replace(/<meta property="og:description" content="[^"]*">/, `<meta property="og:description" content="${escHtml(dynDesc)}">`)
                    .replace(/<meta name="twitter:title" content="[^"]*">/, `<meta name="twitter:title" content="${escHtml(dynTitle)}">`)
                    .replace(/<meta name="twitter:description" content="[^"]*">/, `<meta name="twitter:description" content="${escHtml(dynDesc)}">`);
            }

            if (cid === 'fi') {
                html = html
                    .replace('<strong id="tel-spot">— snt/kWh</strong>', `<strong id="tel-spot">${escHtml(curStr)} snt/kWh</strong>`)
                    .replace('<strong id="tel-wind">— MW</strong>', `<strong id="tel-wind">${Math.round(Number(cur.windMw || 0))} MW</strong>`);
                if (totalFixedTransfer !== null) {
                    html = html.replace(
                        '<strong id="tel-transfer">— snt/kWh</strong>',
                        `<strong id="tel-transfer">${escHtml(fmtNum(totalFixedTransfer, true))} snt/kWh</strong>`
                    );
                }
            }

            const totalPill = totalFixedTransfer !== null && dsoComp
                ? `<div class="summary-pill">Yht. (${escHtml(dsoComp.short_name)}): <strong>${escHtml(curTotStr)} ${escHtml(unit)}</strong></div>`
                : '';

            const summaryHtml =
                `<div class="summary-pill"><strong>${escHtml(dateStr)} (${escHtml(cfg.zone)}):</strong> ${escHtml(cfg.nowLbl)} ${escHtml(curStr)} ${escHtml(unit)}</div>` +
                totalPill +
                `<div class="summary-pill">${escHtml(cfg.avgLbl)}: <strong>${escHtml(avgStr)} ${escHtml(unit)}</strong></div>` +
                `<div class="summary-pill">${escHtml(cfg.minLbl)} (${escHtml(cheapHr)}): <strong>${escHtml(minStr)} ${escHtml(unit)}</strong></div>` +
                `<div class="summary-pill">${escHtml(cfg.maxLbl)} (${escHtml(peakHr)}): <strong>${escHtml(maxStr)} ${escHtml(unit)}</strong></div>`;

            html = html.replace(
                '<div id="first-screen-summary-strip" class="first-screen-summary-strip" aria-live="polite"></div>',
                `<div id="first-screen-summary-strip" class="first-screen-summary-strip" aria-live="polite">${summaryHtml}</div>`
            );

            const rowsHtml = today.map((s) => {
                const h1 = String(s.hour).padStart(2, '0');
                const h2 = String((s.hour + 1) % 24).padStart(2, '0');
                return `<tr><td>${h1}:00 - ${h2}:00</td><td><strong>${escHtml(fmtNum(s.spotPrice, cfg.comma))} ${escHtml(unit)}</strong></td><td>${escHtml(fmtNum(s.minPrice, cfg.comma))}–${escHtml(fmtNum(s.maxPrice, cfg.comma))} ${escHtml(unit)}</td><td>${escHtml(fmtNum(s.totalPrice, cfg.comma))} ${escHtml(unit)}</td><td>${Math.round(Number(s.windMw || 0))} MW · ${escHtml(fmtNum(s.tempC, cfg.comma, 1))} °C</td></tr>`;
            }).join('');

            html = html.replace(
                /<tr><td colspan="5">[^<]*<\/td><\/tr>/,
                rowsHtml
            );
        }
    } catch (_) {
        // Fallback cleanly to static template HTML
    }

    return res.status(200).send(html);
}
