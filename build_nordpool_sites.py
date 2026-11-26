# -*- coding: utf-8 -*-
"""
Generoi Spotpuls (https://spotpuls.app) kansainväliset kieliversiot (28 kieltä / 40 Euroopan sähköpörssialuetta)
sekä kattavan kehittäjädokumentaatiosivun (/api-docs/index.html) avoimelle REST API -rajapinnalle.
"""

import html
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from global_markets_config import (
    SITE_URL,
    BIDDING_ZONES,
    MARKET_LOCALES,
    render_hreflang_tags,
    render_language_options_html,
    render_zone_options_html,
    render_open_api_section_html,
    build_market_schema_graph,
    render_seo_ai_head_tags,
)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def build_localized_faqs(cid: str, loc: dict, z_code: str, exchange_name: str, pub_time: str, tz_name: str, zones_str: str, vat_pct: str):
    unit = loc["unit"]
    api_url = f"https://spotpuls.app/api/v1/prices?zone={z_code}&vat=1"
    u = {"cid": cid, "z": z_code, "ex": exchange_name, "pub": pub_time, "tz": tz_name, "zs": zones_str, "vat": vat_pct, "unit": unit, "api": api_url}
    CUSTOM = {
        "es": (
            f"PREGUNTAS FRECUENTES: PRECIO DE LA LUZ HOY ({z_code})",
            [
                ("¿Cuál es el precio de la luz hoy hora a hora y a qué hora se publica el de mañana?", f"El precio de la luz hoy hora a hora en España ({zones_str}) según {exchange_name} (tarifa luz hoy PVPC / OMIE) se muestra en {unit} con y sin IVA ({vat_pct} %). Los precios del día siguiente se publican cada día hacia las {pub_time} ({tz_name})."),
                ("¿Cuáles son las horas de luz más baratas hoy y la hora valle?", f"En el gráfico interactivo y en el optimizador superior puedes ver al instante la hora valle de la luz hoy y las horas más baratas en {unit} ({vat_pct} % IVA). Además, Spotpuls calcula el precio del kilovatio hora (kWh) hoy para los próximos 7 días con velocidad del viento, radiación solar y temperatura."),
                ("¿Hay API gratuita para consultar la tarifa de luz hoy por horas?", f"Sí. El endpoint abierto con CORS ({api_url}) no requiere clave y devuelve datos en JSON, Home Assistant, Shelly, evcc, CSV, iCal y Markdown."),
            ],
        ),
        "pt": (
            f"PERGUNTAS FREQUENTES: OMIE SPOT HOJE ({z_code})",
            [
                ("Como ver o preço da eletricidade hoje e os preços OMIE por kWh?", f"O preço spot horário OMIE hoje para Portugal ({zones_str}) é apresentado em {unit} com IVA ({vat_pct} %) ou sem IVA. Os preços do dia seguinte na bolsa OMIE são publicados diariamente por volta das {pub_time} ({tz_name})."),
                ("Como funciona a previsão de 7 dias do preço spot da energia?", f"O Spotpuls combina um modelo regional para {z_code} com vento a 100 m, radiação solar, temperatura e aprendizagem contínua para prever 168 horas de preço spot em {unit}."),
                ("Existe uma API gratuita para o preço spot de energia?", f"Sim. A API REST pública e gratuita ({api_url}) suporta JSON, Home Assistant, Shelly, evcc, CSV, iCal e Markdown sem necessidade de chave."),
            ],
        ),
        "gb": (
            f"FAQ: CURRENT UK ELECTRICITY PRICE PER KWH TODAY ({z_code})",
            [
                ("What is the current UK electricity price per kWh today and when are tomorrow's rates published?", f"Spotpuls tracks hourly UK spot electricity prices ({zones_str}) in {unit} (incl. {vat_pct}% VAT or VAT-free). Tomorrow's day-ahead auction rates on {exchange_name} are published daily around {pub_time} ({tz_name})."),
                ("How do electricity prices in the UK today compare with the 7-day forecast?", f"Spotpuls forecasts 168 hourly UK power prices using 100 m wind speeds, solar generation, temperature, and self-learning NLMS error correction, showing min-max probability intervals in {unit}."),
                ("Is there a free UK spot electricity price API for smart homes?", f"Yes. Query {api_url} with no API key required for JSON, Home Assistant, Shelly, evcc, Victron, CSV, iCal, and Markdown."),
            ],
        ),
        "dk": (
            f"OFTE STILLEDE SPØRGSMÅL: ELPRISER TIME FOR TIME ({z_code})",
            [
                ("Hvad er pris på el lige nu, og hvornår kommer morgendagens elpriser i Danmark?", f"Her ser du elpriser time for time i Danmark ({zones_str}) fra {exchange_name} i {unit} inkl. {vat_pct} % moms eller uden moms. Morgendagens elpriser offentliggøres dagligt omkring kl. {pub_time} ({tz_name})."),
                ("Hvordan beregnes 7 dages prognosen for elpriser i Danmark (DK1 / DK2)?", f"Spotpuls kombinerer vindstyrke i 100 m højde, solindstråling, temperatur og selvlærende NLMS-korrektion til en 168-timers prognose for både DK1 og DK2."),
                ("Kan jeg hente danske elpriser time for time via en gratis API?", f"Ja. Den åbne API på {api_url} kræver ingen API-nøgle og understøtter JSON, Home Assistant, Shelly, evcc, CSV, iCal og Markdown."),
            ],
        ),
        "se": (
            f"VANLIGA FRÅGOR: ELPRIS TIMME FÖR TIMME ({z_code})",
            [
                ("Vad är spotpris el nu och när släpps morgondagens elpris timme för timme?", f"Spotpuls visar timspotpris för Sverige ({zones_str}) från {exchange_name} i {unit} med {vat_pct} % moms eller exkl. moms. Morgondagens priser publiceras varje dag omkring kl. {pub_time} ({tz_name})."),
                ("Hur räknar Spotpuls ut 7 dygns elprognos för SE1–SE4?", f"Modellen väger in 100 m vindhastighet, solstrålning, temperatur och självlärande NLMS-kalibrering för att beräkna 168 timmars elprisprognos och intervall i {unit}."),
                ("Finns det ett gratis API för timspotpris till Home Assistant och Shelly?", f"Ja, {api_url} är helt öppet utan API-nyckel och levererar JSON, Home Assistant, Shelly, evcc, Victron, CSV och Markdown."),
            ],
        ),
        "no": (
            f"OFTE STILTE SPØRSMÅL: STRØMPRIS TIME FOR TIME ({z_code})",
            [
                ("Hva er strømpris time for time i dag og når kommer prisene for i morgen?", f"Spotpuls viser spotpris strøm i dag for Norge ({zones_str}) fra {exchange_name} i {unit} (inkl. eller eks. {vat_pct} % MVA). Morgendagens priser publiseres daglig rundt kl. {pub_time} ({tz_name})."),
                ("Hvordan fungerer 7-dagers strømprognose for NO1–NO5?", f"Modellen bruker 100 m vind, temperatur, solforhold og selvlærende feilkorreksjon for å beregne 168 timer med sannsynlige prisintervall i {unit}."),
                ("Kan jeg bruke et gratis API for strømpris time for time?", f"Ja, {api_url} krever ingen API-nøkkel og fungerer direkte med Home Assistant, Shelly, evcc, Tibber-alternativer, JSON og CSV."),
            ],
        ),
        "lv": (
            f"BIEŽĀK UZDOTIE JAUTĀJUMI: ELEKTRĪBAS BIRŽAS CENA PA STUNDĀM ({z_code})",
            [
                ("Cik maksā 1 kWh un kad tiek publicēta elektrības biržas cena pa stundām rītdienai?", f"Spotpuls rāda Nord Pool elektrības cenu biržā pa stundām Latvijā ({zones_str}) vienībās {unit} (ar {vat_pct} % PVN vai bez PVN). Rītdienas cenas tiek publicētas ap plkst. {pub_time} ({tz_name})."),
                ("Kā strādā elektrības kalkulators un 7 dienu biržas cenas prognoze?", f"Elektrības kalkulators un slodzes optimizētājs palīdz atrast lētākās secīgās stundas, bet 7 dienu modelis analizē vēja ātrumu 100 m augstumā, saules starojumu un temperatūru."),
                ("Vai ir bezmaksas API elektrības cenām biržā pa stundām?", f"Jā. Brīvais REST API ({api_url}) darbojas bez atslēgas un atbalsta JSON, Home Assistant, Shelly, CSV un Markdown."),
            ],
        ),
        "ee": (
            f"KORDUMA KIPPUVAD KÜSIMUSED: BÖRSIHINNAD TÄNA ({z_code})",
            [
                ("Millal avaldatakse homsed elektri börsihinnad täna ja kuidas leida soodus elekter täna?", f"Spotpuls kuvab {exchange_name} Eesti ({zones_str}) börsihinnad täna ühikus {unit} (koos {vat_pct} % käibemaksuga või ilma). Homsed hinnad avaldatakse iga päev umbes kell {pub_time} ({tz_name})."),
                ("Kuidas arvutatakse 7 päeva elektrihinna prognoos?", f"Mudel ühendab 100 m tuulekiiruse, päikesekiirguse, õhutemperatuuri ja iseõppiva NLMS-korrektsiooni 168 tunni prognoosiks."),
                ("Kas elektri börsihinna API on tasuta saadaval?", f"Jah, avatud API ({api_url}) ei vaja võtit ning toetab JSON-, Home Assistanti, Shelly, evcc, CSV ja Markdowni vorminguid."),
            ],
        ),
        "lt": (
            f"DAŽNIAUSI KLAUSIMAI: ELEKTROS KAINA BIRŽOJE ({z_code})",
            [
                ("Kokia elektros kaina dabar ir kada skelbiamas rytojaus elektros kainos biržoje grafikas?", f"Spotpuls rodo Lietuvos ({zones_str}) {exchange_name} kainas vienetais {unit} su {vat_pct} % PVM arba be PVM. Rytojaus kainos skelbiamos kasdien apie {pub_time} ({tz_name})."),
                ("Kaip sudaroma 7 dienų elektros kainos prognozė?", f"7 dienų (168 val.) prognozė skaičiuojama pagal 100 m vėjo greitį, saulės spinduliuotę, temperatūrą ir savimokį klaidų koregavimą."),
                ("Ar galima gauti elektros kainas per nemokamą API?", f"Taip, atviras API ({api_url}) nereikalauja rakto ir palaiko JSON, Home Assistant, Shelly, CSV bei Markdown."),
            ],
        ),
        "nl": (
            f"VEELGESTELDE VRAGEN: ACTUELE STROOMPRIJZEN & EPEX VOORSPELLING ({z_code})",
            [
                ("Wanneer worden nieuwe EPEX spot prijzen Nederland gepubliceerd?", f"De actuele stroomprijzen per uur voor Nederland ({zones_str}) op {exchange_name} worden dagelijks rond {pub_time} ({tz_name}) gepubliceerd in {unit} (incl. of excl. {vat_pct} % btw)."),
                ("Hoe werkt de EPEX voorspelling voor de komende 7 dagen?", f"Spotpuls berekent voor {z_code} een 7-daagse (168 uur) EPEX voorspelling op basis van wind op 100 m hoogte, zoninstraling, temperatuur en zelflerende NLMS-correctie."),
                ("Kan ik de EPEX prijzen NL gratis ophalen via een API?", f"Ja, de open CORS-API ({api_url}) werkt zonder API-sleutel en ondersteunt JSON, Home Assistant, Shelly, evcc, Victron, CSV en Markdown."),
            ],
        ),
        "be": (
            f"VEELGESTELDE VRAGEN: ACTUELE STROOMPRIJS BELGIË / BELPEX ({z_code})",
            [
                ("Wanneer komen de nieuwe Belpex / EPEX spot België prijzen online?", f"De actuele stroomprijs België ({zones_str}) op EPEX SPOT / Belpex wordt dagelijks rond {pub_time} ({tz_name}) bekendgemaakt in {unit} (incl. {vat_pct} % btw of excl. btw)."),
                ("Hoe werkt de 7-daagse voorspelling van Spot Belpex prijzen?", f"Het {z_code}-model gebruikt wind op 100 m, zonne-instraling, temperatuur en zelflerende NLMS-foutcorrectie voor 168 uur aan waarschijnlijke prijsintervallen."),
                ("Is er een gratis API voor Belgische dynamische stroomprijzen (o.a. Elexys-vergelijking)?", f"Ja, via {api_url} haal je zonder API-sleutel live EPEX/Belpex uurprijzen op voor Home Assistant, Shelly, evcc en spreadsheets."),
            ],
        ),
        "de": (
            f"HÄUFIGE FRAGEN: DAY-AHEAD STROMPREIS & EEX / EPEX ({z_code})",
            [
                ("Wann erscheint der Day-Ahead Strompreis für morgen an der Strombörse?", f"Der Day-Ahead Strompreis (EPEX / EEX Strompreis) für Deutschland ({zones_str}) wird täglich gegen {pub_time} Uhr ({tz_name}) in {unit} (inkl. {vat_pct} % MwSt. oder netto) veröffentlicht."),
                ("Wie funktioniert die 7-Tage-Prognose und der Tarifrechner Strom?", f"Spotpuls berechnet für {z_code} 168 Stundenprognosen aus 100-m-Windgeschwindigkeit, Solarstrahlung, Temperatur und selbstlernender NLMS-Korrektur – inklusive negativer Börsenpreise."),
                ("Gibt es eine kostenlose API für Day-Ahead-Börsenstrompreise?", f"Ja, {api_url} erfordert keinen API-Key und liefert JSON, Home Assistant, Shelly, evcc, Victron, CSV, iCal und Markdown."),
            ],
        ),
        "at": (
            f"HÄUFIGE FRAGEN: STROMPREIS ÖSTERREICH & EXAA / EPEX ({z_code})",
            [
                ("Wann werden die Day-Ahead Strompreise für Österreich (AT) veröffentlicht?", f"Die stündlichen Börsenstrompreise für Österreich ({zones_str}) auf {exchange_name} erscheinen täglich um ca. {pub_time} Uhr ({tz_name}) in {unit} (inkl. {vat_pct} % MwSt.)."),
                ("Wie entsteht die 7-Tage-Strompreisprognose für Österreich?", f"Spotpuls kombiniert Wind-, Solar- und Temperaturdaten mit einem selbstlernenden NLMS-Modell für 168 Stunden im Voraus."),
                ("Kann ich die österreichischen Spotpreise kostenlos per API abrufen?", f"Ja, über {api_url} stehen JSON, Home Assistant, Shelly, evcc, CSV und Markdown ohne API-Schlüssel bereit."),
            ],
        ),
        "ch": (
            f"HÄUFIGE FRAGEN: STROMPREIS BÖRSE SCHWEIZ ({z_code})",
            [
                ("Wann erscheinen die stündlichen Strompreise der Börse Schweiz (CH)?", f"Der Day-Ahead Strompreis für die Schweiz ({zones_str}) an der {exchange_name} wird täglich gegen {pub_time} Uhr ({tz_name}) in {unit} (inkl. {vat_pct} % MwSt. oder netto) veröffentlicht."),
                ("Wie berechnet Spotpuls den Strommarkt Schweiz 7 Tage im Voraus?", f"Das regionale CH-Modell kombiniert Wind, Sonnenstrahlung, Wasserkraft-Saisonalität und Temperatur zu einer 168-Stunden-Prognose samt Bandbreite."),
                ("Gibt es eine kostenlose API für den Schweizer Spotmarkt?", f"Ja, {api_url} liefert kostenlose JSON-, Home-Assistant-, Shelly-, evcc-, CSV- und Markdown-Feeds ohne Anmeldung."),
            ],
        ),
        "ro": (
            f"ÎNTREBĂRI FRECVENTE: PREȚ PZU OPCOM ENERGIE ELECTRICĂ ({z_code})",
            [
                ("La ce oră se publică prețul PZU OPCOM pentru ziua următoare?", f"Prețurile spot pe Piața pentru Ziua Următoare (preț PZU OPCOM, grafic PZU și prețuri PZU) pentru România ({zones_str}) se publică zilnic în jurul orei {pub_time} ({tz_name}) în {unit} (cu sau fără TVA {vat_pct} %)."),
                ("Cum funcționează prognoza pe 7 zile pentru preț energie electrică?", f"Spotpuls analizează viteza vântului la 100 m, radiația solară, temperatura și corecția adaptivă NLMS pentru 168 de ore de prognoză spot în România."),
                ("Există un API gratuit pentru prețurile PZU OPCOM?", f"Da, endpoint-ul deschis {api_url} funcționează fără cheie API în formate JSON, Home Assistant, Shelly, CSV și Markdown."),
            ],
        ),
        "bg": (
            f"ЧЕСТО ЗАДАВАНИ ВЪПРОСИ: IBEX ЦЕНИ И ЦЕНА НА ТОКА ДЕН НАПРЕД ({z_code})",
            [
                ("В колко часа се публикуват IBEX цени (ИБЕКС БГ) за ден напред?", f"Почасовите цени на тока ден напред на борсата {exchange_name} (ИБЕКС цени / IBEX цени) за България ({zones_str}) се публикуват ежедневно около {pub_time} ({tz_name}) в {unit} с {vat_pct} % ДДС или без ДДС."),
                ("Как се изчислява 7-дневната прогноза за цената на тока ден напред?", f"Моделът на Spotpuls за {z_code} комбинира скорост на вятъра на 100 м, слънчева радиация, температура и самообучаваща се NLMS корекция за 168 часа напред."),
                ("Мога ли да извличам IBEX цени автоматично чрез безплатно API?", f"Да, отвореният REST API на {api_url} не изисква ключ и поддържа JSON, Home Assistant, Shelly, CSV и Markdown."),
            ],
        ),
        "si": (
            f"POGOSTA VPRAŠANJA: CENA ELEKTRIKE DANES & OMREŽNINA ({z_code})",
            [
                ("Kdaj so objavljene borzne cene BSP SouthPool za jutri?", f"Dnevne cene elektrike na borzi {exchange_name} za Slovenijo ({zones_str}) so objavljene vsak dan okoli {pub_time} ({tz_name}) v {unit} (z vključenim {vat_pct} % DDV ali brez DDV)."),
                ("Kako Spotpuls pomaga pri načrtovanju porabe glede na ceno elektrike in omrežnino?", f"Optimizator obremenitve poišče najcenejše ure za polnjenje EV ali ogrevanje vode v naslednjih 24–36 urah, kar pomaga uskladiti porabo z nizko borzno ceno in časovnimi bloki za omrežnino."),
                ("Ali je na voljo brezplačen API za borzno ceno elektrike BSP SouthPool?", f"Da, na naslovu {api_url} brez API ključa dobite JSON, Home Assistant, Shelly, evcc, CSV in Markdown vire."),
            ],
        ),
        "hr": (
            f"ČESTA PITANJA: CROPEX CIJENA STRUJE I ELEKTRIČNE ENERGIJE ({z_code})",
            [
                ("Kada se objavljuje CROPEX cijena električne energije za sutra?", f"Satna CROPEX cijena struje ({zones_str}) za Hrvatsku na burzi {exchange_name} objavljuje se svakodnevno oko {pub_time} ({tz_name}) u {unit} (s {vat_pct} % PDV-a ili bez PDV-a)."),
                ("Kako Spotpuls izračunava 7-dnevnu prognozu CROPEX cijene struje?", f"Regionalni {z_code} model koristi podatke o vjetru na 100 m, sunčevom zračenju, temperaturi i samoučeću NLMS korekciju za 168 sati unaprijed."),
                ("Mogu li preuzeti CROPEX cijene struje putem besplatnog API-ja?", f"Da, {api_url} je besplatan CORS REST API bez potrebe za ključem (JSON, Home Assistant, Shelly, CSV, Markdown)."),
            ],
        ),
        "cz": (
            f"ČASTÉ DOTAZY: SPOTOVÁ CENA ELEKTŘINY & CENA OTE ({z_code})",
            [
                ("Kdy se zveřejňuje spotová cena elektřiny OTE na zítra?", f"Hodinová spotová cena elektřiny (cena OTE) pro Česko ({zones_str}) na burze {exchange_name} vychází každý den přibližně v {pub_time} ({tz_name}) v {unit} (vč. {vat_pct} % DPH nebo bez DPH)."),
                ("Jak vzniká 7denní predikce spotových cen elektřiny v ČR?", f"Spotpuls spojuje vítr ve výšce 100 m, sluneční osvit, teplotu a samoučící NLMS korekci do 168hodinového výhledu v {unit}."),
                ("Nabízí Spotpuls bezplatné API pro cenu OTE?", f"Ano, bezplatné API na adrese {api_url} funguje bez klíče a podporuje JSON, Home Assistant, Shelly, evcc, CSV a Markdown."),
            ],
        ),
        "sk": (
            f"ČASTÉ OTÁZKY: ČO JE SPOTOVÁ CENA ELEKTRINY & OKTE ({z_code})",
            [
                ("Čo je spotová cena elektriny a kedy sú známe zajtrajšie ceny OKTE?", f"Spotová cena elektriny je hodinová trhová cena elektriny na dennom trhu {exchange_name} ({zones_str}). Zajtrajšie spotové ceny elektriny sa zverejňujú denne okolo {pub_time} ({tz_name}) v {unit} (vrátane {vat_pct} % DPH alebo bez DPH)."),
                ("Ako sa počíta 7-dňová predikcia spotovej ceny elektriny pre Slovensko?", f"Model kombinuje rýchlosť vetra v 100 m, slnečné žiarenie, teplotu a samoučiacu NLMS korekciu pre 168 hodín dopredu."),
                ("Je k dispozícii bezplatné API pre spotové ceny elektriny OKTE?", f"Áno, endpoint {api_url} nevyžaduje API kľúč a podporuje JSON, Home Assistant, Shelly, CSV aj Markdown."),
            ],
        ),
        "pl": (
            f"NAJCZĘSTSZE PYTANIA: TGE100 & CENA PRĄDU DZIŚ ({z_code})",
            [
                ("Kiedy publikowane są ceny RDN / TGE dla Polski?", f"Godzinowa cena prądu na Towarowej Giełdzie Energii ({exchange_name}, TGE / RDN, indeksy typu TGE100 / TGeBase) dla Polski ({zones_str}) pojawia się codziennie około {pub_time} ({tz_name}) w {unit} (z {vat_pct} % VAT lub netto)."),
                ("Jak działa 7-dniowa prognoza cen prądu RDN?", f"Spotpuls analizuje wiatr na wysokości 100 m, nasłonecznienie, temperaturę oraz adaptacyjną korekcję NLMS dla 168 godzin naprzód."),
                ("Czy API z cenami prądu TGE jest darmowe?", f"Tak, otwarte API ({api_url}) nie wymaga klucza i obsługuje JSON, Home Assistant, Shelly, evcc, CSV i Markdown."),
            ],
        ),
        "hu": (
            f"GYAKORI KÉRDÉSEK: HUPX DAM ÁRAK & ÁRAMÁR MA ({z_code})",
            [
                ("Mikor jelennek meg a holnapi HUPX DAM árak?", f"A magyarországi ({zones_str}) órás {exchange_name} HUPX DAM árak minden nap körülbelül {pub_time} ({tz_name}) körül jelennek meg {unit} mértékegységben ({vat_pct} % ÁFA-val vagy nettó)."),
                ("Hogyan készül a 7 napos magyar áramár-előrejelzés?", f"A modell 100 m-es szélsebességet, napsugárzást, hőmérsékletet és öntanuló NLMS korrekciót használ a következő 168 óra megbecslésére."),
                ("Van ingyenes API a HUPX áramárakhoz?", f"Igen, a {api_url} kulcs nélkül elérhető JSON, Home Assistant, Shelly, CSV és Markdown formátumban."),
            ],
        ),
        "fr": (
            f"FOIRE AUX QUESTIONS : PRIX SPOT ÉLECTRICITÉ EPEX ({z_code})",
            [
                ("À quelle heure sont publiés les prix électricité spot en France ?", f"Les prix horaires EPEX SPOT pour la France ({zones_str}) sont publiés chaque jour vers {pub_time} ({tz_name}) en {unit} (TTC {vat_pct} % ou HT)."),
                ("Comment fonctionne la prévision à 7 jours du prix spot ?", f"Spotpuls associe vent à 100 m, rayonnement solaire, température et apprentissage NLMS sur 168 heures (y compris prix négatifs)."),
                ("Existe-t-il une API gratuite pour le prix électricité spot ?", f"Oui, {api_url} est accessible sans clé API en JSON, Home Assistant, Shelly, evcc, CSV et Markdown."),
            ],
        ),
        "it": (
            f"DOMANDE FREQUENTI: PUN OGGI & PREZZO ZONALE ORARIO GME ({z_code})",
            [
                ("Quando vengono pubblicati PUN oggi e prezzi zonali orari GME?", f"Il prezzo zonale orario GME (e PUN) per l'Italia ({zones_str}) sulla borsa {exchange_name} viene pubblicato ogni giorno intorno alle {pub_time} ({tz_name}) in {unit} (IVA {vat_pct} % inclusa o esclusa)."),
                ("Come viene calcolata la previsione oraria a 7 giorni per l'Italia?", f"Spotpuls elabora vento a 100 m, irradiazione solare, temperatura e correzione adattiva NLMS su 168 ore per ciascuna delle 6 zone GME."),
                ("Esiste un'API gratuita per prezzi orari GME / PUN?", f"Sì, {api_url} è aperta senza chiave API in JSON, Home Assistant, Shelly, CSV e Markdown."),
            ],
        ),
        "ie": (
            f"FAQ: IRELAND SEMOPX ELECTRICITY SPOT PRICE TODAY ({z_code})",
            [
                ("When are tomorrow's Ireland SEMOpx day-ahead prices published?", f"Hourly SEMOpx electricity spot prices for Ireland ({zones_str}) are published daily around {pub_time} ({tz_name}) in {unit} (incl. or excl. {vat_pct}% VAT)."),
                ("How does the 7-day forecast for IE-SEM work?", f"Spotpuls uses 100 m wind speed, temperature, and self-learning error correction tailored to Ireland's high wind penetration."),
                ("Can I fetch IE-SEM spot prices with a free API?", f"Yes. Query {api_url} with no API key for JSON, Home Assistant, Shelly, CSV, and Markdown."),
            ],
        ),
        "gr": (
            f"ΣΥΧΝΕΣ ΕΡΩΤΗΣΕΙΣ: ΤΙΜΗ KWH ΣΗΜΕΡΑ HENEX ({z_code})",
            [
                ("Πότε δημοσιεύεται η τιμή kWh σήμερα και αύριο στο HEnEx;", f"Οι ωριαίες τιμές ηλεκτρικής ενέργειας στο {exchange_name} ({zones_str}) δημοσιεύονται καθημερινά περίπου στις {pub_time} ({tz_name}) σε {unit} (με ΦΠΑ {vat_pct} % ή χωρίς ΦΠΑ)."),
                ("Πώς υπολογίζεται η 7ήμερη πρόβλεψη τιμής ρεύματος;", f"Το μοντέλο για το {z_code} συνδυάζει ταχύτητα ανέμου στα 100 μ., ηλιακή ακτινοβολία, θερμοκρασία και αυτοεκπαιδευόμενη διόρθωση NLMS για 168 ώρες."),
                ("Υπάρχει δωρεάν API για τις τιμές HEnEx;", f"Ναι, το {api_url} λειτουργεί χωρίς κλειδί API σε JSON, Home Assistant, Shelly, CSV και Markdown."),
            ],
        ),
    }
    if cid in CUSTOM:
        return CUSTOM[cid]
    return (
        f"FAQ — {loc['countryName']} ({z_code})",
        [
            (
                f"When are tomorrow's {loc['countryName']} ({z_code}) electricity spot prices published?",
                f"Day-ahead hourly prices for {loc['countryName']} ({zones_str}) on {exchange_name} are published daily around {pub_time} ({tz_name}). Spotpuls updates automatically with both VAT-inclusive ({vat_pct} %) and VAT-free prices in {unit}.",
            ),
            (
                f"How does the Spotpuls 7-day electricity price forecast work for {z_code}?",
                f"Spotpuls combines a dedicated {z_code} Log-Merit + Hist-GBDT model with 100 m wind speed, solar radiation, temperature, and self-learning NLMS residual correction to forecast 168 hourly prices (including negative price regimes and min-max probability bands).",
            ),
            (
                f"Can I fetch {loc['countryName']} spot prices and 7-day forecasts via a free API?",
                f"Yes. The open CORS-enabled endpoint {api_url} requires no API key and outputs JSON, Home Assistant, Shelly, EVCC, Victron, CSV, iCal, Prometheus, Markdown, and live SVG badges.",
            ),
        ],
    )


def build_country_page(cid: str, loc: dict) -> str:
    z_code = loc.get("defaultZone", "FI")
    z_meta = BIDDING_ZONES.get(z_code, {})
    exchange_name = z_meta.get("exchange", "Nord Pool / ENTSO-E")
    pub_h = int(z_meta.get("pubHour", 13))
    pub_m = int(z_meta.get("pubMin", 0))
    tz_name = z_meta.get("tz", "Europe/Berlin")
    zones_str = ", ".join(loc.get("zones", [z_code]))
    vat_pct = f"{loc.get('vatRate', 0.25) * 100:.1f}".rstrip("0").rstrip(".")

    faq_heading, faq_items = build_localized_faqs(
        cid, loc, z_code, exchange_name, f"{pub_h:02d}:{pub_m:02d}", tz_name, zones_str, vat_pct
    )
    faq_entity = {
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in faq_items
        ],
    }
    faq_html_items = "\n".join(
        f'''                    <details class="faq-item" open style="border-bottom:1px solid #d8d4c7; padding:10px 0;">
                        <summary style="font-weight:700; cursor:pointer; font-size:14px;">{html.escape(q)}</summary>
                        <p style="margin-top:6px; font-size:13.5px; color:#3a3e38; line-height:1.6;">{html.escape(a)}</p>
                    </details>'''
        for q, a in faq_items
    )

    full_schema = build_market_schema_graph(cid, extra_entities=[faq_entity])
    hreflang_html = render_hreflang_tags()
    zone_opts = render_zone_options_html(cid)
    lang_opts = render_language_options_html(cid)
    api_section_html = render_open_api_section_html(cid, prefix="/")
    loc_json = json.dumps({"countryId": cid, **loc}, ensure_ascii=False)
    canonical_url = f"{SITE_URL}{loc['path']}"
    CUSTOM_TITLES = {
        "bg": "IBEX цени (ИБЕКС) & цена на тока ден напред – Прогноза 7 дни | Spotpuls",
        "pt": "OMIE Spot Hoje e Preço da Eletricidade por Hora (Portugal) | Spotpuls",
        "es": "Precio de la luz hoy hora a hora (OMIE / PVPC) y previsión 7 días | Spotpuls",
        "ro": "Preț PZU OPCOM azi & grafic prețuri spot energie electrică | Spotpuls",
        "nl": "Actuele stroomprijzen & EPEX spot prijzen Nederland (7d voorspelling) | Spotpuls",
        "be": "Actuele stroomprijs België vandaag (Belpex / EPEX Spot) | Spotpuls",
        "de": "Strompreis heute (Day-Ahead / EPEX / EEX) & 7-Tage-Prognose | Spotpuls",
        "at": "Strompreis Österreich heute (Day-Ahead / EPEX) & 7-Tage-Prognose | Spotpuls",
        "ch": "Strompreis Börse Schweiz heute (Spotmarkt) & 7-Tage-Prognose | Spotpuls",
        "hr": "CROPEX cijena struje i električne energije danas (7-dnevna prognoza) | Spotpuls",
        "si": "Cena elektrike danes (BSP SouthPool), 7-dnevna napoved & omrežnina | Spotpuls",
        "sk": "Spotové ceny elektriny dnes (OKTE) a 7-dňová predikcia | Spotpuls",
        "cz": "Spotová cena elektřiny dnes (Cena OTE) a 7denní predikce | Spotpuls",
        "pl": "Cena prądu dziś (TGE / RDN / TGE100) i prognoza 7-dniowa | Spotpuls",
        "hu": "HUPX DAM árak & órás áramár ma (7 napos előrejelzés) | Spotpuls",
        "dk": "Elpriser time for time i dag (DK1 / DK2) & 7 dages elprognose | Spotpuls",
        "se": "Elpris timme för timme idag (SE1–SE4) – Timspotpris & 7 dygns prognos | Spotpuls",
        "no": "Strømpris time for time i dag (NO1–NO5) & 7-dagers strømprognose | Spotpuls",
        "lv": "Elektrības biržas cena pa stundām šodien (Nord Pool LV) | Spotpuls",
        "ee": "Börsielekter ja elektri börsihind täna (Nord Pool EE) | Spotpuls",
        "lt": "Elektros kaina biržoje šiandien (Nord Pool LT) ir 7 d. prognozė | Spotpuls",
        "gb": "Current UK Electricity Price per kWh Today & 7-Day Spot Forecast | Spotpuls",
        "ie": "Ireland Electricity Spot Price Today (SEMOpx / IE-SEM) & 7-Day Forecast | Spotpuls",
        "fr": "Prix électricité spot aujourd'hui (EPEX France) & prévision 7 jours | Spotpuls",
        "it": "Prezzo zonale orario GME e PUN oggi (6 zone Italia) & previsione 7gg | Spotpuls",
        "gr": "Τιμή kWh σήμερα (HEnEx) & ωριαία πρόβλεψη ρεύματος 7 ημερών | Spotpuls",
        "en": "European Electricity Spot Prices Today & 7-Day Hourly Forecast (40 Zones) | Spotpuls",
    }
    page_title = CUSTOM_TITLES.get(cid, f"{loc['brandSubtitle']} — {loc['countryName']} | Spotpuls")
    seo_ai_tags = render_seo_ai_head_tags(page_title, loc["transferLead"], canonical_url, loc["lang"], z_code)

    market_links = " ".join(
        f'<a href="{m["path"]}" style="margin-right:10px;">{html.escape(m["languageLabel"])}</a>'
        for m in MARKET_LOCALES.values()
    )

    return f"""<!DOCTYPE html>
<html lang="{loc['lang']}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(page_title)}</title>
    <meta name="description" content="{html.escape(loc['transferLead'])}">
    <meta name="geo.region" content="{loc['geoRegion']}">
    <meta name="content-language" content="{loc['lang']}">
    <link rel="canonical" href="{canonical_url}" />
{hreflang_html}
    <link rel="icon" type="image/svg+xml" href="/favicon.svg?v=37">
    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
    <link rel="manifest" href="/site.webmanifest">
    <link rel="stylesheet" href="/styles.css?v=43">
    <script type="application/ld+json">
{json.dumps(full_schema, ensure_ascii=False, indent=2)}
    </script>
{seo_ai_tags}
    <script>
    window.ACTIVE_COUNTRY_LOCALE = {loc_json};
    </script>
</head>
<body>
    <header class="site-header">
        <div class="header-inner">
            <a href="./" class="brand-link">
                <span class="brand-title"><img src="/favicon.svg?v=37" alt="" width="24" height="24" style="vertical-align:-5px; margin-right:8px;">Spotpuls</span>
                <span class="brand-subtitle">{html.escape(loc['brandSubtitle'])}</span>
            </a>
            <div class="header-right">
                <nav class="main-nav" aria-label="Navigation">
                    <a href="./">{html.escape(loc['navChart'])}</a>
                    <a href="#tuntitaulukko">{html.escape(loc['navTable'])}</a>
                    <a href="#siirtohintalaskuri">{html.escape(loc['navTransfer'])}</a>
                    <a href="#optimoija">{html.escape(loc['navOptimizer'])}</a>
                    <a href="#avoin-api">{html.escape(loc['navApi'])}</a>
                </nav>
                <div class="header-market-controls">
                    <select id="zone-select" class="header-select" aria-label="{html.escape(loc['zoneSelectLabel'])}">
                        {zone_opts}
                    </select>
                    <select id="lang-select" class="header-select" aria-label="{html.escape(loc['langSelectLabel'])}">
                        {lang_opts}
                    </select>
                </div>
            </div>
        </div>
    </header>

    <main class="container">
        <div class="first-screen-stage">
            <section class="hero-chart-box">
                <div id="day-tabs" class="day-tabs"></div>

                <div class="panel-body" style="padding:10px 14px; border-bottom:var(--border-heavy);">
                    <div id="chart-readout-strip" class="chart-readout-strip" style="margin-bottom:8px;">
                        {html.escape(loc['hoverHint'])}
                    </div>

                    <div class="chart-legend" style="padding-top:4px;">
                        <span class="legend-item"><span class="legend-swatch" style="background:#009e3d;"></span> {html.escape(loc['tierCheap'])}</span>
                        <span class="legend-item"><span class="legend-swatch" style="background:#0038ff;"></span> {html.escape(loc['tierNorm'])}</span>
                        <span class="legend-item"><span class="legend-swatch" style="background:#ff3b00;"></span> {html.escape(loc['tierHigh'])}</span>
                        <span class="legend-item"><span class="legend-swatch" style="background:#ffd000;"></span> {html.escape(loc['legendRange'])}</span>
                        <h1 id="chart-view-title" style="font-family:var(--mono); font-size:11.5px; font-weight:700; text-transform:uppercase; margin-left:auto;">{html.escape(loc['chartTitle'])}</h1>
                    </div>
                </div>

                <div class="scroll-down-bar" style="margin-top:0; border:none; border-bottom:var(--border-heavy);">
                    <span>{html.escape(loc['scrollDownText'])}</span>
                    <div class="scroll-down-links">
                        <a href="#tuntitaulukko">{html.escape(loc['navTable'])}</a>
                        <a href="#siirtohintalaskuri">{html.escape(loc['navTransfer'])}</a>
                        <a href="#optimoija">{html.escape(loc['navOptimizer'])}</a>
                        <a href="#avoin-api">{html.escape(loc['navApi'])}</a>
                    </div>
                </div>

                <div class="svg-chart-wrapper">
                    <button type="button" id="chart-prev-day" class="chart-edge-arrow chart-edge-prev" aria-label="Prev">
                        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="square" stroke-linejoin="miter"><polyline points="15 18 9 12 15 6"></polyline></svg>
                    </button>
                    <div id="chart-floating-tooltip" class="chart-floating-tooltip" aria-live="polite"></div>
                    <div id="price-chart" class="svg-chart-container" style="border:none; padding:12px 8px 6px;">
                        ...
                    </div>
                    <button type="button" id="chart-next-day" class="chart-edge-arrow chart-edge-next" aria-label="Next">
                        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="square" stroke-linejoin="miter"><polyline points="9 18 15 12 9 6"></polyline></svg>
                    </button>
                </div>
            </section>

            <div id="first-screen-summary-strip" class="first-screen-summary-strip" aria-live="polite"></div>
        </div>

        <div class="below-fold-section">
            <section class="panel-box" id="tuntitaulukko">
                <div class="panel-head">
                    <h2>{html.escape(loc['tableHeading'])}</h2>
                </div>
                <div class="panel-body">
                    <div class="table-wrap">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>{html.escape(loc['colTime'])}</th>
                                    <th>{html.escape(loc['colSpot'])}</th>
                                    <th>{html.escape(loc['colRange'])}</th>
                                    <th>{html.escape(loc['colTotal'])}</th>
                                    <th>{html.escape(loc['colWeather'])}</th>
                                </tr>
                            </thead>
                            <tbody id="hourly-table-body">
                                <tr><td colspan="5">...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>

            <section class="instrument-strip" id="siirtohintalaskuri">
                <div class="instrument-strip-top">
                    <h2>{html.escape(loc['transferHeading'])}</h2>
                    <p>{html.escape(loc['transferLead'])}</p>
                </div>

                <div class="control-matrix">
                    <form id="postal-search-form" class="control-cell" onsubmit="return false;">
                        <label for="postal-input" class="field-label">{html.escape(loc['postalLabel'])}</label>
                        <div class="postal-input-group">
                            <input type="text" id="postal-input" class="input-control" value="{html.escape(loc['defaultPostal'])}" placeholder="{html.escape(loc['postalPlaceholder'])}">
                            <button type="submit" class="btn-primary">{html.escape(loc['setBtn'])}</button>
                        </div>
                    </form>

                    <div class="control-cell">
                        <span class="field-label">{html.escape(loc['tariffLabel'])}</span>
                        <div class="seg-group">
                            <button type="button" class="seg-btn active" data-tariff-btn="general">{html.escape(loc['tariffGeneral'])}</button>
                            <button type="button" class="seg-btn" data-tariff-btn="time">{html.escape(loc['tariffTime'])}</button>
                        </div>
                    </div>

                    <div class="control-cell">
                        <label for="margin-input" class="field-label">{html.escape(loc['marginLabel'])}</label>
                        <input type="number" id="margin-input" class="input-control" step="0.05" min="0" max="500" value="{loc.get('defaultMargin', 0.45)}">
                    </div>

                    <div class="control-cell">
                        <label for="vat-select" class="field-label">{html.escape(loc['vatLabel'])}</label>
                        <select id="vat-select" class="select-control">
                            <option value="1" selected>{html.escape(loc['vatIncl'])}</option>
                            <option value="0">{html.escape(loc['vatZero'])}</option>
                        </select>
                    </div>
                </div>

                <div id="detected-dso-banner" class="detected-dso-banner"></div>
            </section>

            <div class="desk-grid">
                <section class="panel-box">
                    <div class="panel-head">
                        <h2>{html.escape(loc['receiptNowTitle'])}</h2>
                    </div>
                    <div class="panel-body" id="receipt-ledger-body"></div>
                </section>

                <section class="panel-box" id="optimoija">
                    <div class="panel-head">
                        <h2>{html.escape(loc['navOptimizer'])}</h2>
                    </div>
                    <div class="panel-body">
                        <div class="opt-controls-row">
                            <div style="flex:1; min-width:180px;">
                                <span class="field-label">{html.escape(loc['optDurationLabel'])}</span>
                                <div class="seg-group">
                                    <button type="button" class="seg-btn" data-win-hours="1">1h</button>
                                    <button type="button" class="seg-btn" data-win-hours="2">2h</button>
                                    <button type="button" class="seg-btn active" data-win-hours="3">3h</button>
                                    <button type="button" class="seg-btn" data-win-hours="4">4h</button>
                                    <button type="button" class="seg-btn" data-win-hours="6">6h</button>
                                    <button type="button" class="seg-btn" data-win-hours="8">8h</button>
                                </div>
                            </div>
                            <div style="width:110px;">
                                <label for="appliance-kw-input" class="field-label">{html.escape(loc['optKwLabel'])}</label>
                                <input type="number" id="appliance-kw-input" class="input-control" step="0.1" min="0.1" max="50" value="11">
                            </div>
                        </div>
                        <div id="cheapest-window-result"></div>
                    </div>
                </section>
            </div>

{api_section_html}

            <section class="panel-box" id="faq">
                <div class="panel-head">
                    <h2>{html.escape(faq_heading)}</h2>
                </div>
                <div class="panel-body">
{faq_html_items}
                </div>
            </section>
        </div>
    </main>

    <footer class="site-footer">
        <div class="footer-inner">
            <div>
                <strong style="color:#ffffff;">Spotpuls (spotpuls.app) — {html.escape(loc['countryName'])}</strong>
                <p style="margin-top:6px; max-width:680px;">{html.escape(loc['brandSubtitle'])}</p>
            </div>
            <div class="footer-links">
                <a href="./">{html.escape(loc['navChart'])}</a>
                <a href="#avoin-api">{html.escape(loc['navApi'])}</a>
                <a href="/api-docs/">API Docs</a>
                <a href="/openapi.json">OpenAPI 3.1</a>
                <a href="/llms.txt">llms.txt</a>
                <a href="https://www.laavutkartalla.fi/en.html" target="_blank" rel="noopener">Nordic Shelter Map</a>
            </div>
            <div style="width:100%; padding-top:12px; border-top:1px solid #2b2e28; font-size:11px; line-height:1.8;">
                <span style="color:#ffffff; margin-right:8px;">SPOT MARKETS (28 LANGUAGES / 40 ZONES):</span>
                {market_links}
            </div>
        </div>
    </footer>

    <script src="/dso_data.js"></script>
    <script src="/ml_weights.js"></script>
    <script src="/nordpool_models.js"></script>
    <script src="/app.js?v=45"></script>
</body>
</html>
"""


def build_api_docs_page() -> str:
    lang_opts = render_language_options_html("en")
    zone_rows = []
    for zcode, z in BIDDING_ZONES.items():
        json_href = f"/api/v1/prices?zone={zcode}&vat=1"
        ha_href = f"/api/v1/ha/{zcode}.json"
        shelly_href = f"/api/v1/shelly/{zcode}.json"
        evcc_href = f"/api/v1/evcc/{zcode}.json"
        csv_href = f"/api/v1/prices?zone={zcode}&vat=1&format=csv"
        ical_href = f"/api/v1/ical/{zcode}.ics"
        widget_href = f"/api/v1/widget/{zcode}?theme=light"
        badge_href = f"/api/v1/badge/{zcode}.svg"
        zone_rows.append(
            f"""                            <tr>
                                <td><strong><code>{html.escape(zcode)}</code></strong></td>
                                <td>{html.escape(z['name'])}</td>
                                <td>{html.escape(z['exchange'])}</td>
                                <td><code>{html.escape(z['tz'])}</code></td>
                                <td>{z['windCapMw']} MW / {z['solarCapMw']} MW</td>
                                <td style="white-space:nowrap;">
                                    <a href="{json_href}">JSON</a> &middot;
                                    <a href="{ha_href}">HA</a> &middot;
                                    <a href="{shelly_href}">Shelly</a> &middot;
                                    <a href="{evcc_href}">EVCC</a> &middot;
                                    <a href="{csv_href}">CSV</a> &middot;
                                    <a href="{ical_href}">iCal</a> &middot;
                                    <a href="{widget_href}">Widget</a> &middot;
                                    <a href="{badge_href}">Badge</a>
                                </td>
                            </tr>"""
        )

    market_links = " ".join(
        f'<a href="{m["path"]}" style="margin-right:10px;">{html.escape(m["languageLabel"])}</a>'
        for m in MARKET_LOCALES.values()
    )

    api_schema = {
        "@context": "https://schema.org",
        "@type": "WebAPI",
        "name": "Spotpuls Open Electricity Spot, 7-Day Forecast & Smart Automation REST API",
        "url": f"{SITE_URL}/api/v1/prices",
        "documentation": f"{SITE_URL}/api-docs/",
        "description": "Free CORS-enabled REST API serving official day-ahead electricity spot prices, 7-day Log-Merit + Hist-GBDT regional forecasts, and native Home Assistant, Shelly, EVCC, Victron/Node-RED, ESPHome, CSV, iCal, Prometheus, plain-text, SVG badge, and iframe widget feeds across all 40 European bidding zones.",
        "provider": {"@type": "Organization", "name": "Spotpuls", "url": SITE_URL},
    }

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spotpuls Open REST API — Day-Ahead Electricity Spot Prices &amp; 7-Day Forecast (40 Zones) | Spotpuls</title>
    <meta name="description" content="Free, zero-key, CORS-enabled REST API for live European day-ahead electricity spot prices, 7-day Log-Merit + Hist-GBDT forecasts, and plug-and-play integrations for Home Assistant, Shelly, EVCC, ESPHome, Node-RED, Google Sheets, iCal, Prometheus, and iframe widgets.">
    <link rel="canonical" href="{SITE_URL}/api-docs/" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg?v=37">
    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
    <link rel="manifest" href="/site.webmanifest">
    <link rel="stylesheet" href="/styles.css?v=43">
    <script type="application/ld+json">
{json.dumps(api_schema, ensure_ascii=False, indent=2)}
    </script>
{render_seo_ai_head_tags("Spotpuls Open REST API — Day-Ahead Electricity Spot Prices & 7-Day Forecast (40 Zones) | Spotpuls", "Free, zero-key, CORS-enabled REST API for live European day-ahead electricity spot prices, 7-day Log-Merit + Hist-GBDT forecasts, and plug-and-play integrations for Home Assistant, Shelly, EVCC, ESPHome, Node-RED, Google Sheets, iCal, Prometheus, and iframe widgets.", f"{SITE_URL}/api-docs/", "en_US", "FI")}
</head>
<body>
    <header class="site-header">
        <div class="header-inner">
            <a href="/en/" class="brand-link">
                <span class="brand-title"><img src="/favicon.svg?v=37" alt="" width="24" height="24" style="vertical-align:-5px; margin-right:8px;">Spotpuls</span>
                <span class="brand-subtitle">Open Electricity Spot, 7-Day Forecast &amp; Universal Automation API — 40 European Bidding Zones</span>
            </a>
            <div class="header-right">
                <nav class="main-nav" aria-label="API Navigation">
                    <a href="/">FI</a>
                    <a href="/en/">Dashboard (EN)</a>
                    <a href="#endpoints">Endpoints</a>
                    <a href="#integrations">Integrations</a>
                    <a href="#zones">40 Zones</a>
                    <a href="/openapi.json">OpenAPI 3.1</a>
                </nav>
                <div class="header-market-controls">
                    <select id="lang-select" class="header-select" aria-label="Language" onchange="if(this.value)window.location.href=this.value;">
                        {lang_opts}
                    </select>
                </div>
            </div>
        </div>
    </header>

    <main class="container" style="padding-top:24px;">
        <section class="panel-box" id="endpoints">
            <div class="panel-head">
                <h1>SPOTPULS OPEN REST API (V1) — FREE, NO API KEY, CORS *</h1>
                <a href="/openapi.json" style="color:var(--signal-yellow); font-family:var(--mono); font-size:12px; font-weight:700;">openapi.json &rarr;</a>
            </div>
            <div class="panel-body">
                <p style="font-size:14.5px; max-width:940px; margin-bottom:14px;">
                    <strong>Spotpuls (<code>https://spotpuls.app</code>)</strong> provides a free, zero-key, CORS-enabled REST &amp; automation API delivering official day-ahead electricity spot prices together with an empirically calibrated 7-day (168 h) Log-Merit + Hist-GBDT hourly forecast (including negative price regimes and conformal probability bands) across all 40 European bidding zones. Ten native output formats allow direct integration into Home Assistant, Shelly Gen2/Gen3, ESPHome, EVCC, Node-RED/Victron, Python, calendars, spreadsheets, monitoring stacks, and AI coding assistants.
                </p>

                <div class="api-card" style="margin-bottom:14px; border:2px solid #111210; background:#fffdf2;">
                    <div style="display:flex; justify-content:space-between; align-items:center; gap:10px; flex-wrap:wrap; margin-bottom:8px;">
                        <span class="field-label" style="margin-bottom:0;">BUILDING WITH CHATGPT, CLAUDE OR CURSOR? COPY AI CONTEXT (LLMS.TXT)</span>
                        <button type="button" class="api-copy-btn" onclick="navigator.clipboard&&navigator.clipboard.writeText(document.getElementById('ai-prompt-box').textContent).then(()=>{{this.textContent='Copied!';setTimeout(()=>this.textContent='Copy AI Prompt',1800);}});">Copy AI Prompt</button>
                    </div>
                    <pre id="ai-prompt-box" class="api-pre-block" style="white-space:pre-wrap;">Use Spotpuls (https://spotpuls.app) as the free, no-API-key electricity spot price &amp; 7-day forecast API (40 European zones, CORS *):
- Full JSON + 7-day forecast + cheapestContiguousWindow: https://spotpuls.app/api/v1/prices?zone=FI&amp;vat=1&amp;window=3
- Shelly Gen2/Gen3 (&lt;500 B): https://spotpuls.app/api/v1/shelly/FI.json?window=3 (use data.runContig === 1)
- Home Assistant: https://spotpuls.app/api/v1/ha/FI.json?window=3
- ESPHome / plain text (1/0): https://spotpuls.app/api/v1/plain/FI?field=run_now&amp;window=3
- evcc.io tariff: https://spotpuls.app/api/v1/evcc/DE-LU.json
- Markdown briefing for LLMs: https://spotpuls.app/api/v1/prices?zone=FI&amp;format=markdown
- OpenAPI 3.1: https://spotpuls.app/openapi.json | LLM Spec: https://spotpuls.app/llms.txt
Rate limit: spot prices change once per hour — fetch at the top of each hour (:00:05) and cache responses. Always attribute Spotpuls (https://spotpuls.app).</pre>
                    <div style="margin-top:8px; font-family:var(--mono); font-size:11.5px; display:flex; gap:14px; flex-wrap:wrap;">
                        <span>Ready-to-use examples:</span>
                        <a href="/examples/shelly-gen2-spotpuls.js">Shelly Gen2/3 JS</a>
                        <a href="/examples/home-assistant-configuration.yaml">Home Assistant YAML</a>
                        <a href="/examples/esphome-spotpuls.yaml">ESPHome YAML</a>
                        <a href="/examples/evcc-custom-tariff.yaml">evcc.io YAML</a>
                        <a href="/examples/python_spot_controller.py">Python</a>
                        <a href="/mcp/server.js">MCP Server (mcp/server.js)</a>
                    </div>
                </div>

                <div class="api-panel-grid">
                    <div class="api-card">
                        <span class="field-label">1. HOURLY SPOT + 7-DAY FORECAST + SMART AUTOMATION</span>
                        <pre class="api-pre-block">GET https://spotpuls.app/api/v1/prices?zone=FI&amp;vat=1&amp;window=3&amp;format=json</pre>
                        <ul style="margin:10px 0 0 18px; font-family:var(--mono); font-size:12px; line-height:1.65;">
                            <li><code>zone</code> — Any of 40 European zones (<code>FI</code>, <code>SE1..SE4</code>, <code>NO1..NO5</code>, <code>DK1..DK2</code>, <code>EE</code>, <code>LV</code>, <code>LT</code>, <code>DE-LU</code>, <code>FR</code>, <code>NL</code>, <code>ES</code>, <code>IT-North</code>, <code>PL</code>, <code>GB</code>).</li>
                            <li><code>vat</code> — <code>1</code> (incl. national electricity VAT, default) or <code>0</code> (VAT 0 %).</li>
                            <li><code>currency</code> — <code>local</code> (snt, öre, øre, ct, p, gr, Ft, Kč), <code>eur_cents</code>, <code>eur_kwh</code>, or <code>eur_mwh</code>.</li>
                            <li><code>window</code> — <code>1..24</code> (default <code>3</code>): computes <code>cheapestContiguousWindow</code> and <code>cheapestHours</code> for relays, boilers, heat pumps, and EVs.</li>
                            <li><code>margin</code> / <code>transfer</code> / <code>threshold</code> — Optional contract add-ons &amp; price trigger threshold.</li>
                            <li><code>format</code> — <code>json</code>, <code>compact</code> (<code>shelly</code>), <code>ha</code>, <code>evcc</code>, <code>victron</code>, <code>csv</code>, <code>ical</code>, <code>prometheus</code>, <code>plain</code>, <code>badge</code>, or <code>widget</code>.</li>
                        </ul>
                    </div>

                    <div class="api-card">
                        <span class="field-label">2. CLEAN INTEGRATION SHORTCUT URLS</span>
                        <pre class="api-pre-block">GET https://spotpuls.app/api/v1/zones
GET https://spotpuls.app/api/v1/ha/FI.json?window=3
GET https://spotpuls.app/api/v1/shelly/FI.json?window=3
GET https://spotpuls.app/api/v1/evcc/DE-LU.json
GET https://spotpuls.app/api/v1/ical/FI.ics?window=3
GET https://spotpuls.app/api/v1/metrics?zone=FI
GET https://spotpuls.app/api/v1/plain/FI?field=run_now&amp;window=3
GET https://spotpuls.app/api/v1/grid-tariffs?address=Keskustie+1,+35300+Orivesi&amp;vat=1</pre>
                        <span class="field-label" style="margin-top:12px;">3. LIVE SVG BADGE &amp; IFRAME MINI-CHART WIDGET</span>
                        <div class="api-badge-preview">
                            <img src="/api/v1/badge/FI.svg" alt="Spotpuls FI live badge" width="256" height="28" style="border:1px solid #111210;">
                            <img src="/api/v1/badge/DE-LU.svg" alt="Spotpuls DE-LU live badge" width="256" height="28" style="border:1px solid #111210;">
                        </div>
                        <pre class="api-pre-block">&lt;iframe src="https://spotpuls.app/api/v1/widget/FI?theme=light" width="100%" height="198" style="border:0;max-width:460px;" loading="lazy"&gt;&lt;/iframe&gt;</pre>
                    </div>
                </div>
            </div>
        </section>

        <section class="panel-box" id="integrations">
            <div class="panel-head">
                <h2>READY-TO-USE APPLICATION &amp; HARDWARE INTEGRATIONS</h2>
            </div>
            <div class="panel-body">
                <div class="api-panel-grid">
                    <div class="api-card">
                        <span class="field-label">HOME ASSISTANT (CONFIGURATION.YAML + APEXCHARTS)</span>
                        <pre class="api-pre-block">rest:
  - resource: "https://spotpuls.app/api/v1/ha/FI.json?window=3&amp;transfer=6.80"
    scan_interval: 300
    sensor:
      - name: "Spotpuls Spot Price"
        value_template: "{{{{ value_json.state }}}}"
        unit_of_measurement: "snt/kWh"
        json_attributes:
          - total_price
          - today_min
          - today_max
          - raw_today
          - raw_tomorrow
          - forecast_7d
    binary_sensor:
      - name: "Spotpuls Cheapest 3h Window Active"
        value_template: "{{{{ value_json.run_contiguous_now }}}}"</pre>
                    </div>

                    <div class="api-card">
                        <span class="field-label">SHELLY PLUS / GEN2 / GEN3 / PRO LOCAL RELAY SCRIPT (&lt; 500 B)</span>
                        <pre class="api-pre-block">// Runs on Shelly Plus 1PM / Pro 3EM — switches relay ON during cheapest 3h window
const URL = "https://spotpuls.app/api/v1/shelly/FI.json?window=3";
function pollSpotpuls() {{
  Shelly.call("HTTP.GET", {{ url: URL, timeout: 10 }}, function (res, err) {{
    if (err || !res || res.code !== 200) return;
    const d = JSON.parse(res.body);
    const shouldRun = d.runContig === 1; // or d.runCheap === 1
    Shelly.call("Switch.Set", {{ id: 0, on: shouldRun }});
  }});
}}
pollSpotpuls();
Timer.set(300000, true, pollSpotpuls);</pre>
                    </div>

                    <div class="api-card">
                        <span class="field-label">EVCC.IO DYNAMIC EV &amp; BATTERY CHARGING TARIFF (EVCC.YAML)</span>
                        <pre class="api-pre-block">tariffs:
  currency: EUR
  grid:
    type: custom
    forecast:
      source: http
      uri: https://spotpuls.app/api/v1/evcc/DE-LU.json?vat=1
      jq: .
      cache: 15m</pre>
                    </div>

                    <div class="api-card">
                        <span class="field-label">ESPHOME / ESP32 / APPLE SHORTCUTS / CURL / PLC</span>
                        <pre class="api-pre-block"># Single numeric value (current spot price):
curl -s "https://spotpuls.app/api/v1/plain/FI?field=spot"

# Binary 1 / 0 relay trigger (1 if inside cheapest 4h block):
curl -s "https://spotpuls.app/api/v1/plain/FI?field=run_now&amp;window=4"

# Google Sheets live 192-hour table:
=IMPORTDATA("https://spotpuls.app/api/v1/prices?zone=FI&amp;vat=1&amp;format=csv")

# Apple / Google / Outlook Calendar live subscription URL:
https://spotpuls.app/api/v1/ical/FI.ics?window=3</pre>
                    </div>

                    <div class="api-card">
                        <span class="field-label">JAVASCRIPT / TYPESCRIPT SDK-FREE FETCH</span>
                        <pre class="api-pre-block">const res = await fetch("https://spotpuls.app/api/v1/prices?zone=SE3&amp;vat=1&amp;window=4");
const data = await res.json();
console.log(data.current.spotPrice, data.meta.unit);
console.log("Cheapest 4h:", data.automation.cheapestContiguousWindow);</pre>
                    </div>

                    <div class="api-card">
                        <span class="field-label">PYTHON / PANDAS &amp; PROMETHEUS / GRAFANA</span>
                        <pre class="api-pre-block">import pandas as pd
df = pd.read_csv("https://spotpuls.app/api/v1/prices?zone=FI&amp;vat=1&amp;format=csv", comment="#")
print(df.head())

# Prometheus scrape config (prometheus.yml):
# metrics_path: /api/v1/metrics
# params: {{ zone: ["FI"] }}</pre>
                    </div>
                </div>
            </div>
        </section>

        <section class="panel-box" id="zones">
            <div class="panel-head">
                <h2>ALL 40 SUPPORTED EUROPEAN BIDDING ZONES &amp; REGIONAL FORECAST MODELS</h2>
            </div>
            <div class="panel-body">
                <div class="table-wrap">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Zone Code</th>
                                <th>Region / Bidding Zone</th>
                                <th>Power Exchange</th>
                                <th>IANA Timezone</th>
                                <th>Wind / Solar Cap.</th>
                                <th>Live API &amp; Integration Feeds</th>
                            </tr>
                        </thead>
                        <tbody>
{chr(10).join(zone_rows)}
                        </tbody>
                    </table>
                </div>
            </div>
        </section>
    </main>

    <footer class="site-footer">
        <div class="footer-inner">
            <div>
                <strong style="color:#ffffff;">Spotpuls (spotpuls.app)</strong>
                <p style="margin-top:6px; max-width:680px;">Open European Day-Ahead Electricity Spot Price &amp; Self-Learning 7-Day Regional Forecast Platform.</p>
            </div>
            <div class="footer-links">
                <a href="/">Suomi (FI)</a>
                <a href="/en/">English (EU)</a>
                <a href="/openapi.json">OpenAPI 3.1</a>
                <a href="/.well-known/ai-plugin.json">AI Plugin</a>
                <a href="/llms.txt">llms.txt</a>
                <a href="https://www.laavutkartalla.fi/en.html" target="_blank" rel="noopener">Nordic Shelter Map</a>
            </div>
            <div style="width:100%; padding-top:12px; border-top:1px solid #2b2e28; font-size:11px; line-height:1.8;">
                <span style="color:#ffffff; margin-right:8px;">SPOT MARKETS (28 LANGUAGES / 40 ZONES):</span>
                {market_links}
            </div>
        </div>
    </footer>
</body>
</html>
"""

def main():
    count = 0
    for cid, loc in MARKET_LOCALES.items():
        if cid == "fi":
            continue
        out_dir = os.path.join(ROOT_DIR, cid)
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, "index.html")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(build_country_page(cid, loc))
        count += 1
        print(f"[GENERATED] /{cid}/ ({loc['lang']}) -> {loc['countryName']} | Zones: {', '.join(loc['zones'])}")

    api_docs_dir = os.path.join(ROOT_DIR, "api-docs")
    os.makedirs(api_docs_dir, exist_ok=True)
    with open(os.path.join(api_docs_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_api_docs_page())
    print(f"[GENERATED] /api-docs/index.html + {count} international Spotpuls editions!")


if __name__ == "__main__":
    main()
