#!/usr/bin/env python3
"""
Baut die statische Testseite aus quellen/ nach site/.

  python3 werkzeuge/seiten_bauen.py

Was passiert:
- Jede Datei in quellen/seiten/ wird zu einer Seite. quellen/seiten/leistungen/treppen.html
  landet als site/leistungen/treppen/index.html (Adresse /leistungen/treppen/).
  index.html bleibt index.html, 404.html bleibt 404.html.
- Kopf, Navigation, Footer, Consent-Banner und GTM-Snippet kommen aus diesem Skript.
  GTM-ID, Firmendaten und Consent-Modus stehen in quellen/einstellungen.json.
- Shop-Produktseiten entstehen aus quellen/produkte.json, Stellenanzeigen aus quellen/stellen.json.
- Zusätzlich: site/assets/js/produkte.js, sitemap.xml, robots.txt, _headers.

Nur Python-Standardbibliothek, läuft ab Python 3.9.
"""

import hashlib
import html
import json
import re
import shutil
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
QUELLEN = WURZEL / "quellen"
ZIEL = WURZEL / "site"

E = json.loads((QUELLEN / "einstellungen.json").read_text(encoding="utf-8"))
F = E["firma"]
P = json.loads((QUELLEN / "produkte.json").read_text(encoding="utf-8"))
S = json.loads((QUELLEN / "stellen.json").read_text(encoding="utf-8"))

LEISTUNGEN = [
    ("kuechen-nach-mass", "Küchen nach Maß", "nav-kuechen"),
    ("einbauschraenke", "Einbauschränke", "nav-einbauschraenke"),
    ("treppen", "Treppen", "nav-treppen"),
    ("innentueren", "Innentüren", "nav-innentueren"),
]

STANDORTE = [
    ("Hamburg-Bahrenfeld", "Werkstatt & Hauptsitz", "Werkstattweg 14, 22761 Hamburg", "040 66969 100", "+494066969100"),
    ("Norderstedt", "Niederlassung Nord", "Am Sägewerk 3, 22844 Norderstedt", "040 66969 200", "+494066969200"),
    ("Ahrensburg", "Ausstellung Ost", "Hobelweg 7, 22926 Ahrensburg", "040 66969 300", "+494066969300"),
]


def version(rel):
    """Kurzer Inhalts-Hash als ?v=…, damit Browser nach Änderungen nicht die alte Datei aus dem Cache nehmen."""
    datei = ZIEL / rel.lstrip("/")
    if not datei.exists():
        return rel
    return f"{rel}?v={hashlib.md5(datei.read_bytes()).hexdigest()[:8]}"


def euro(wert):
    return f"{wert:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def e(text):
    return html.escape(str(text), quote=True)


# ---------------------------------------------------------------------------
# Platzhalter {{firma.name}}, {{gtm_id}} ...
# ---------------------------------------------------------------------------
def platzhalter(text):
    werte = {k: v for k, v in E.items() if isinstance(v, str)}
    werte.update({f"firma.{k}": v for k, v in F.items()})
    werte["jahr"] = "2026"
    return re.sub(r"\{\{\s*([\w.]+)\s*\}\}", lambda m: str(werte.get(m.group(1), m.group(0))), text)


# ---------------------------------------------------------------------------
# Bausteine
# ---------------------------------------------------------------------------
LOGO_SVG = """<svg class="logo-zeichen" viewBox="0 0 48 48" aria-hidden="true"><rect x="1" y="1" width="46" height="46" rx="10" fill="#23372d"/><path d="M8 16c10-5 22 5 32 0M8 24c10-5 22 5 32 0M8 32c10-5 22 5 32 0" fill="none" stroke="#c89b62" stroke-width="2.4" stroke-linecap="round"/><path d="M15 12v24M33 12v24" stroke="#f7f3ec" stroke-width="3.2" stroke-linecap="round"/></svg>"""

KORB_SVG = """<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M3 4h2l2.4 10.2a2 2 0 0 0 2 1.6h7.7a2 2 0 0 0 1.9-1.4L21 8H6.2" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><circle cx="10" cy="20" r="1.4" fill="currentColor"/><circle cx="17" cy="20" r="1.4" fill="currentColor"/></svg>"""


def kopfbereich(meta, pfad):
    titel = e(meta.get("titel", F["name"]))
    beschreibung = e(meta.get("beschreibung", ""))
    seitendaten = {"seitentyp": meta.get("seitentyp", "sonstige"),
                   "inhaltsgruppe": meta.get("inhaltsgruppe", "Sonstiges")}
    if meta.get("leistung"):
        seitendaten["leistung"] = meta["leistung"]

    consent = ""
    if E["consent_modus"] == "eigener_banner":
        consent = """
// Consent Mode V2: Grundeinstellung, bevor GTM lädt. Gespeicherte Auswahl wird sofort übernommen.
gtag('consent', 'default', {
  ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied',
  analytics_storage: 'denied', functionality_storage: 'granted', security_storage: 'granted',
  wait_for_update: 500
});
(function () {
  var c = null;
  try { c = JSON.parse(localStorage.getItem('hh_consent')); } catch (err) {}
  if (!c) return;
  var m = c.marketing ? 'granted' : 'denied';
  gtag('consent', 'update', {
    analytics_storage: c.statistik ? 'granted' : 'denied',
    ad_storage: m, ad_user_data: m, ad_personalization: m
  });
})();"""
    cookiebot = ""
    if E["consent_modus"] == "cookiebot" and E.get("cookiebot_id"):
        cookiebot = (f'<script id="Cookiebot" src="https://consent.cookiebot.com/uc.js" '
                     f'data-cbid="{e(E["cookiebot_id"])}" data-blockingmode="auto" type="text/javascript"></script>\n')

    sc = ""
    if E.get("search_console_meta"):
        sc = f'<meta name="google-site-verification" content="{e(E["search_console_meta"])}">\n'

    gtm = E["gtm_id"]
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titel}</title>
<meta name="description" content="{beschreibung}">
<meta name="robots" content="noindex, nofollow">
{sc}<link rel="canonical" href="{e(E['basis_url'].rstrip('/') + pfad)}">
<link rel="icon" href="/assets/bilder/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{version('/assets/css/stil.css')}">
<script>
window.dataLayer = window.dataLayer || [];
function gtag() {{ dataLayer.push(arguments); }}{consent}
// Seitendaten für GTM-Variablen (Datenschichtvariable) und Inhaltsgruppen
dataLayer.push({json.dumps(seitendaten, ensure_ascii=False)});
</script>
{cookiebot}<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
}})(window,document,'script','dataLayer','{gtm}');</script>
<!-- End Google Tag Manager -->
</head>
<body class="{e(meta.get('koerperklasse', ''))}">
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={gtm}"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
"""


def navigation(aktiv):
    def cls(name):
        return ' class="aktiv"' if aktiv == name else ""

    unter = "\n".join(
        f'          <li><a id="{nid}" href="/leistungen/{slug}/">{e(name)}</a></li>' for slug, name, nid in LEISTUNGEN)
    return f"""<a class="sprung" href="#inhalt">Zum Inhalt springen</a>
<div class="oberleiste">
  <div class="wrap oberleiste-innen">
    <span>{e(F['oeffnungszeiten'])}</span>
    <span class="oberleiste-kontakt">
      <a id="kopf-telefon" href="tel:{F['telefon_link']}">Tel. {e(F['telefon'])}</a>
      <a id="kopf-mail" href="mailto:{F['email']}?subject=Anfrage%20%C3%BCber%20die%20Website">{e(F['email'])}</a>
    </span>
  </div>
</div>
<header class="kopf">
  <div class="wrap kopf-innen">
    <a class="logo" id="logo" href="/">{LOGO_SVG}<span><strong>{e(F['name'])}</strong><small>{e(F['zusatz'])}</small></span></a>
    <nav id="hauptnav" class="hauptnav" aria-label="Hauptnavigation">
      <ul>
        <li class="hat-unter"><a id="nav-leistungen" href="/leistungen/"{cls('leistungen')}>Leistungen</a>
          <ul class="unter">
{unter}
          </ul>
        </li>
        <li><a id="nav-shop" href="/shop/"{cls('shop')}>Shop</a></li>
        <li><a id="nav-ratgeber" href="/ratgeber/"{cls('ratgeber')}>Ratgeber</a></li>
        <li><a id="nav-karriere" href="/karriere/"{cls('karriere')}>Karriere</a></li>
        <li><a id="nav-ueber-uns" href="/ueber-uns/"{cls('ueber-uns')}>Über uns</a></li>
        <li><a id="nav-kontakt" href="/kontakt/"{cls('kontakt')}>Kontakt</a></li>
      </ul>
      <a id="nav-cta-anfrage" class="btn btn-klein" href="/anfrage/">Angebot anfragen</a>
    </nav>
    <a id="kopf-warenkorb" class="warenkorb-link" href="/shop/warenkorb/" aria-label="Warenkorb">{KORB_SVG}<span id="warenkorb-zahl" class="warenkorb-zahl" hidden>0</span></a>
    <button id="nav-toggle" class="nav-toggle" type="button" aria-expanded="false" aria-controls="hauptnav"><span></span><span></span><span></span><em>Menü</em></button>
  </div>
</header>
"""


def consent_banner():
    if E["consent_modus"] != "eigener_banner":
        return ""
    return """
<div id="consent-banner" class="consent" role="dialog" aria-modal="true" aria-labelledby="consent-titel" hidden>
  <div class="consent-box">
    <h2 id="consent-titel">Ihre Privatsphäre</h2>
    <p>Wir nutzen Cookies und ähnliche Technologien. Notwendige Cookies halten die Seite am Laufen. Mit Ihrer Einwilligung messen wir außerdem die Nutzung (Google Analytics) und den Erfolg unserer Werbung (Google Ads). Mehr dazu in der <a href="/datenschutz/">Datenschutzerklärung</a>. Sie können Ihre Wahl jederzeit im Footer unter „Cookie-Einstellungen“ ändern.</p>
    <div id="consent-details" class="consent-details" hidden>
      <label class="check"><input type="checkbox" checked disabled> <span><strong>Notwendig</strong><br>Warenkorb, Ihre Cookie-Auswahl, Formularschutz</span></label>
      <label class="check"><input type="checkbox" id="consent-statistik"> <span><strong>Statistik</strong><br>Google Analytics 4: anonyme Auswertung der Seitennutzung</span></label>
      <label class="check"><input type="checkbox" id="consent-marketing"> <span><strong>Marketing</strong><br>Google Ads: Conversion-Messung und Remarketing, YouTube-Videos</span></label>
    </div>
    <div class="consent-knoepfe">
      <button id="consent-ablehnen" class="btn btn-zweit" type="button">Nur notwendige</button>
      <button id="consent-einstellungen" class="btn btn-zweit" type="button">Einstellungen</button>
      <button id="consent-speichern" class="btn btn-zweit" type="button" hidden>Auswahl speichern</button>
      <button id="consent-alle" class="btn" type="button">Alle akzeptieren</button>
    </div>
  </div>
</div>"""


def footer():
    leist = "\n".join(
        f'        <li><a id="footer-{slug}" href="/leistungen/{slug}/">{e(name)}</a></li>' for slug, name, _ in LEISTUNGEN)
    orte = "\n".join(
        f'        <li><strong>{e(o)}</strong> · {e(art)}<br>{e(adr)}<br><a id="footer-telefon-{i}" href="tel:{tl}">{e(tel)}</a></li>'
        for i, (o, art, adr, tel, tl) in enumerate(STANDORTE, 1))
    cookie = ('<a id="cookie-einstellungen" href="#cookie-einstellungen">Cookie-Einstellungen</a>'
              if E["consent_modus"] == "eigener_banner" else "")
    return f"""
<footer class="fuss">
  <div class="wrap fuss-raster">
    <div>
      <a class="logo logo-hell" href="/">{LOGO_SVG}<span><strong>{e(F['name'])}</strong><small>{e(F['zusatz'])}</small></span></a>
      <p>Maßanfertigung aus Massivholz und Plattenwerkstoffen. Seit {F['gruendung']} in Hamburg, heute mit 14 Leuten in Werkstatt, Planung und Montage.</p>
      <p class="fuss-social">
        <a id="link-instagram" href="{F['instagram']}" target="_blank" rel="noopener">Instagram</a>
        <a id="link-maps" href="{F['google_maps']}" target="_blank" rel="noopener">Anfahrt (Google Maps)</a>
        <a id="link-whatsapp-footer" href="https://wa.me/{F['whatsapp_link']}" target="_blank" rel="noopener">WhatsApp</a>
      </p>
    </div>
    <div>
      <h3>Leistungen</h3>
      <ul>
{leist}
        <li><a id="footer-leistungen" href="/leistungen/">Alle Leistungen</a></li>
      </ul>
    </div>
    <div>
      <h3>Service</h3>
      <ul>
        <li><a id="footer-anfrage" href="/anfrage/">Angebot anfragen</a></li>
        <li><a id="footer-shop" href="/shop/">Shop für Holzpflege & Zubehör</a></li>
        <li><a id="footer-whitepaper" href="/ratgeber/kuechen-kosten/">Ratgeber: Was kostet eine Küche?</a></li>
        <li><a id="footer-pflegeanleitung" href="/downloads/pflegeanleitung-massivholz.pdf">Pflegeanleitung (PDF)</a></li>
        <li><a id="footer-karriere" href="/karriere/">Jobs & Ausbildung</a></li>
      </ul>
    </div>
    <div>
      <h3>Standorte</h3>
      <ul class="fuss-orte">
{orte}
      </ul>
    </div>
  </div>
  <div class="wrap fuss-unten">
    <span>© {{{{jahr}}}} {e(F['rechtsform'])}</span>
    <span><a id="footer-impressum" href="/impressum/">Impressum</a> <a id="footer-datenschutz" href="/datenschutz/">Datenschutz</a> {cookie}</span>
    <span class="demo-hinweis">Fiktives Unternehmen · Demo-Website für Tracking-Schulungen</span>
  </div>
</footer>
<div class="mobil-leiste">
  <a id="mobil-anrufen" href="tel:{F['telefon_link']}">Anrufen</a>
  <a id="mobil-anfrage" href="/anfrage/">Angebot anfragen</a>
</div>
"""


def seite_zusammensetzen(meta, inhalt, pfad):
    def js(name):
        return f'<script src="{version("/assets/js/" + name + ".js")}" defer></script>'

    skripte = [js("seite")]
    for s in meta.get("skripte", "").split():
        if s == "shop":
            skripte.insert(0, js("produkte"))
            skripte.append(js("shop"))
        else:
            skripte.append(js(s))
    teile = [kopfbereich(meta, pfad), navigation(meta.get("nav", "")),
             '<main id="inhalt">\n', inhalt.strip(), "\n</main>\n", footer(), consent_banner(),
             "\n" + "\n".join(skripte), "\n</body>\n</html>\n"]
    return platzhalter("".join(teile))


# ---------------------------------------------------------------------------
# Seiten aus Fragmenten
# ---------------------------------------------------------------------------
KOPF_RE = re.compile(r"^\s*<!--(.*?)-->", re.S)


def lies_fragment(datei):
    text = datei.read_text(encoding="utf-8")
    meta = {}
    m = KOPF_RE.match(text)
    if m:
        for zeile in m.group(1).strip().splitlines():
            if ":" in zeile:
                k, v = zeile.split(":", 1)
                meta[k.strip()] = v.strip()
        text = text[m.end():]
    return meta, text


def zielpfad(rel):
    """quellen/seiten/a/b.html -> (site/a/b/index.html, /a/b/)"""
    teile = list(rel.with_suffix("").parts)
    if teile[-1] == "404":
        return ZIEL / "404.html", "/404.html"
    if teile[-1] == "index":
        teile = teile[:-1]
    ordner = ZIEL.joinpath(*teile)
    url = "/" + "/".join(teile) + ("/" if teile else "")
    return ordner / "index.html", url


def schreibe(ziel, text):
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------------------
# Shop
# ---------------------------------------------------------------------------
def produktkarte(p, liste, index):
    return f"""<article class="produkt-karte">
  <a class="js-produkt-link" id="produkt-link-{p['slug']}" href="/shop/{p['slug']}/" data-produkt="{p['id']}" data-liste="{e(liste)}" data-index="{index}">
    <img src="/assets/bilder/{p['bild']}" alt="{e(p['name'])}" loading="lazy">
    <span class="produkt-kat">{e(p['kategorie'])}</span>
    <h3>{e(p['name'])}</h3>
  </a>
  <p>{e(p['kurz'])}</p>
  <div class="produkt-fuss">
    <strong>{euro(p['preis'])}</strong>
    <button class="btn btn-klein js-in-warenkorb" id="in-warenkorb-{p['slug']}" type="button" data-produkt="{p['id']}" data-liste="{e(liste)}">In den Warenkorb</button>
  </div>
</article>"""


def shop_liste(liste="Shop Übersicht", nur=None):
    produkte = [p for p in P["produkte"] if not nur or p["id"] in nur]
    karten = "\n".join(produktkarte(p, liste, i) for i, p in enumerate(produkte))
    return f'<div class="produkt-raster" data-ecommerce-liste="{e(liste)}">\n{karten}\n</div>'


def produktseite(p):
    merkmale = "".join(f"<li>{e(m)}</li>" for m in p["merkmale"])
    versand = ("Digitaler Versand per E-Mail, keine Versandkosten" if p.get("digital")
               else f"Versand {euro(P['versand']['standard'])}, ab {euro(P['versand']['kostenlos_ab'])} versandkostenfrei · Abholung in Bahrenfeld möglich")
    aehnlich = [x["id"] for x in P["produkte"] if x["kategorie"] == p["kategorie"] and x["id"] != p["id"]]
    if len(aehnlich) < 2:
        aehnlich += [x["id"] for x in P["produkte"] if x["id"] != p["id"] and x["id"] not in aehnlich][:3 - len(aehnlich)]
    inhalt = f"""
<nav class="brotkrumen wrap" aria-label="Brotkrumen"><a href="/">Start</a> › <a href="/shop/">Shop</a> › <span>{e(p['name'])}</span></nav>
<section class="wrap produkt-detail" data-produkt-seite="{p['id']}">
  <div class="produkt-bild"><img src="/assets/bilder/{p['bild']}" alt="{e(p['name'])}"></div>
  <div class="produkt-info">
    <span class="produkt-kat">{e(p['kategorie'])}</span>
    <h1>{e(p['name'])}</h1>
    <p class="produkt-preis"><strong>{euro(p['preis'])}</strong> <small>inkl. 19 % MwSt.</small></p>
    <p>{e(p['text'])}</p>
    <ul class="haken">{merkmale}</ul>
    <div class="menge-zeile">
      <label for="produkt-menge">Menge</label>
      <input id="produkt-menge" type="number" min="1" max="20" value="1" inputmode="numeric">
      <button id="produkt-in-warenkorb" class="btn" type="button" data-produkt="{p['id']}">In den Warenkorb</button>
    </div>
    <p id="produkt-hinzugefuegt" class="meldung ok" role="status" hidden>Im Warenkorb. <a href="/shop/warenkorb/" id="produkt-zum-warenkorb">Zum Warenkorb</a></p>
    <p class="klein">{versand}</p>
  </div>
</section>
<section class="wrap abschnitt">
  <h2>Passt dazu</h2>
  {shop_liste('Produktseite Empfehlungen', aehnlich[:3])}
</section>
"""
    meta = {"titel": f"{p['name']} | Shop {F['name']}", "beschreibung": p["kurz"],
            "seitentyp": "produkt", "inhaltsgruppe": "Shop", "nav": "shop", "skripte": "shop"}
    return meta, inhalt


def produkte_js():
    daten = {"versand": P["versand"], "produkte": {
        p["id"]: {"name": p["name"], "kategorie": p["kategorie"], "preis": p["preis"], "slug": p["slug"],
                  "bild": p["bild"], "digital": bool(p.get("digital"))} for p in P["produkte"]}}
    return ("// Automatisch erzeugt aus quellen/produkte.json – nicht von Hand ändern.\n"
            f"window.HH_SHOP = {json.dumps(daten, ensure_ascii=False, indent=1)};\n")


# ---------------------------------------------------------------------------
# Karriere
# ---------------------------------------------------------------------------
def stellen_liste():
    karten = []
    for s in S["stellen"]:
        karten.append(f"""<a class="stelle-karte" id="stelle-{s['slug']}" href="/karriere/{s['slug']}/">
  <span class="stelle-art">{e(s['art'])}</span>
  <h3>{e(s['titel'])}</h3>
  <span class="stelle-ort">{e(s['ort'])}</span>
  <span class="pfeil">Stelle ansehen →</span>
</a>""")
    return '<div class="stellen-raster">\n' + "\n".join(karten) + "\n</div>"


def stellenseite(s):
    def ul(liste):
        return '<ul class="haken">' + "".join(f"<li>{e(x)}</li>" for x in liste) + "</ul>"

    inhalt = f"""
<nav class="brotkrumen wrap" aria-label="Brotkrumen"><a href="/">Start</a> › <a href="/karriere/">Karriere</a> › <span>{e(s['kurztitel'])}</span></nav>
<section class="seitenkopf seitenkopf-bild" style="--bild:url('/assets/bilder/{s['bild']}')">
  <div class="wrap">
    <span class="dachzeile">{e(s['art'])} · {e(s['ort'])}</span>
    <h1>{e(s['titel'])}</h1>
    <a class="btn" id="cta-stelle-bewerben" href="#bewerbung"><span>Jetzt in 2 Minuten bewerben</span></a>
  </div>
</section>
<section class="wrap abschnitt schmal">
  <p class="einleitung">{e(s['einleitung'])}</p>
  <div class="zwei-spalten">
    <div><h2>Ihre Aufgaben</h2>{ul(s['aufgaben'])}</div>
    <div><h2>Das bringen Sie mit</h2>{ul(s['profil'])}</div>
  </div>
  <h2>Was wir bieten</h2>
  {ul(s['vorteile'])}
</section>
<section class="flaeche" id="bewerbung">
  <div class="wrap schmal">
    <h2>Kurzbewerbung – ohne Anschreiben</h2>
    <p>Name, Kontakt und ein paar Eckdaten reichen. Lebenslauf gern, muss aber nicht. Wir melden uns innerhalb von drei Werktagen. Ihr Ansprechpartner: {e(s['kontakt'])}.</p>
    <form class="formular" id="form-bewerbung" name="bewerbung" method="POST" action="/danke-bewerbung/" data-netlify="true" netlify-honeypot="bot-field" enctype="multipart/form-data">
      <input type="hidden" name="form-name" value="bewerbung">
      <input type="hidden" name="stelle" value="{e(s['slug'])}">
      <p class="versteckt"><label>Nicht ausfüllen: <input name="bot-field"></label></p>
      <div class="feld-reihe">
        <label>Vor- und Nachname <input id="bewerbung-name" type="text" name="name" required autocomplete="name"></label>
        <label>E-Mail <input id="bewerbung-email" type="email" name="email" required autocomplete="email"></label>
      </div>
      <div class="feld-reihe">
        <label>Telefon <input id="bewerbung-telefon" type="tel" name="telefon" required autocomplete="tel"></label>
        <label>Berufserfahrung
          <select id="bewerbung-erfahrung" name="erfahrung">
            <option value="">Bitte wählen</option>
            <option value="schueler">Schüler/in bzw. Berufseinstieg</option>
            <option value="0-2">bis 2 Jahre</option>
            <option value="3-9">3 bis 9 Jahre</option>
            <option value="10+">10 Jahre und mehr</option>
          </select>
        </label>
      </div>
      <label>Frühester Starttermin <input id="bewerbung-start" type="date" name="start"></label>
      <label>Lebenslauf (optional, PDF bis 5 MB) <input id="bewerbung-datei" type="file" name="lebenslauf" accept=".pdf"></label>
      <label>Kurz zu Ihnen (optional) <textarea id="bewerbung-nachricht" name="nachricht" rows="3"></textarea></label>
      <label class="check"><input id="bewerbung-datenschutz" type="checkbox" name="datenschutz" required> <span>Ich habe die <a href="/datenschutz/">Datenschutzerklärung</a> gelesen und bin mit der Verarbeitung meiner Daten für das Bewerbungsverfahren einverstanden.</span></label>
      <button class="btn" id="bewerbung-absenden" type="submit">Bewerbung absenden</button>
    </form>
  </div>
</section>
<section class="wrap abschnitt">
  <h2>Weitere offene Stellen</h2>
  {stellen_liste()}
</section>
"""
    meta = {"titel": f"{s['titel']} in {s['ort']} | {F['name']}",
            "beschreibung": s["einleitung"][:155], "seitentyp": "stelle",
            "inhaltsgruppe": "Karriere", "nav": "karriere"}
    return meta, inhalt


# ---------------------------------------------------------------------------
# YouTube-Video (Über uns)
# ---------------------------------------------------------------------------
def video_block():
    vid = E.get("youtube_id")
    if not vid:
        return '<div class="video"><div class="video-platzhalter">Kein Video hinterlegt (youtube_id in quellen/einstellungen.json)</div></div>'
    # enablejsapi=1 braucht der GTM-Trigger „YouTube-Video“, um Start, Fortschritt und Ende zu melden
    src = f"https://www.youtube.com/embed/{e(vid)}?enablejsapi=1&amp;rel=0"
    if E.get("video_modus") == "nach_einwilligung":
        return f"""<div class="video" id="video-ueber-uns" data-youtube-src="{src}">
  <div class="video-platzhalter"><div><p>Beim Abspielen werden Daten an YouTube (Google) übertragen.</p>
  <button class="btn" type="button" id="video-laden">Video laden</button></div></div>
</div>"""
    return f"""<div class="video" id="video-ueber-uns">
  <iframe id="youtube-ueber-uns" src="{src}" title="{e(E.get('video_titel', 'Video'))}" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>"""


# ---------------------------------------------------------------------------
def main():
    # alte HTML-Seiten entfernen, Assets behalten
    for alt in list(ZIEL.rglob("index.html")) + [ZIEL / "404.html"]:
        if alt.exists():
            alt.unlink()

    schreibe(ZIEL / "assets" / "js" / "produkte.js", produkte_js())
    urls = []
    ersatz = {"{{shop_liste}}": shop_liste(), "{{stellen_liste}}": stellen_liste(), "{{video_block}}": video_block(),
              "{{shop_teaser}}": shop_liste("Startseite Shop-Teaser", ["HH-PFLEGE-SET", "HH-OEL-500", "HH-GRIFF-128"])}

    for datei in sorted((QUELLEN / "seiten").rglob("*.html")):
        meta, inhalt = lies_fragment(datei)
        for k, v in ersatz.items():
            inhalt = inhalt.replace(k, v)
        ziel, url = zielpfad(datei.relative_to(QUELLEN / "seiten"))
        schreibe(ziel, seite_zusammensetzen(meta, inhalt, url))
        if meta.get("sitemap", "ja") != "nein":
            urls.append(url)

    for p in P["produkte"]:
        meta, inhalt = produktseite(p)
        url = f"/shop/{p['slug']}/"
        schreibe(ZIEL / "shop" / p["slug"] / "index.html", seite_zusammensetzen(meta, inhalt, url))
        urls.append(url)

    for s in S["stellen"]:
        meta, inhalt = stellenseite(s)
        url = f"/karriere/{s['slug']}/"
        schreibe(ZIEL / "karriere" / s["slug"] / "index.html", seite_zusammensetzen(meta, inhalt, url))
        urls.append(url)

    basis = E["basis_url"].rstrip("/")
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sitemap += [f"  <url><loc>{basis}{u}</loc></url>" for u in sorted(set(urls))]
    sitemap.append("</urlset>")
    schreibe(ZIEL / "sitemap.xml", "\n".join(sitemap) + "\n")
    # Kein Disallow: Google muss die Seiten abrufen können, um das noindex zu sehen.
    schreibe(ZIEL / "robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {basis}/sitemap.xml\n")
    # Gilt auch beim Hochladen per Drag-and-drop (netlify.toml wird dabei nicht mitgenommen)
    schreibe(ZIEL / "_headers", "/*\n  X-Robots-Tag: noindex, nofollow\n")

    print(f"Fertig: {len(urls)} Seiten in {ZIEL}")
    if E["gtm_id"] == "GTM-XXXXXXX":
        print("Hinweis: In quellen/einstellungen.json ist noch keine echte GTM-ID eingetragen.")


if __name__ == "__main__":
    main()
