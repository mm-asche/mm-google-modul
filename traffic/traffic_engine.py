#!/usr/bin/env python3
"""
Traffic-Engine v2 für die mehrseitige Testseite (Holzwerk Hanssen).

Eigenständige Weiterentwicklung der Engine der einseitigen Tischlerei-Testseite. Die alte
Engine bleibt unverändert. Neu in v2:
- Besuche sind „Reisen“ über mehrere Seiten (Einstiegsseite -> Klicks -> Formular …).
  Das liefert Daten für Pfad- und Trichteranalysen und Zielgruppen wie „mehrere Seiten besucht“.
- Jede Reise hat eigene Einstiegsseiten und passende Traffic-Quellen
  (z. B. Google/CPC auf Leistungsseiten, Jobportale auf der Karriereseite).
- Mehrstufige Formulare mit Abbruchquote je Schritt (Formular begonnen, nicht abgeschickt).
- Shop: Produkte ansehen, in den Warenkorb legen, Kauf abschließen oder abbrechen.
- Einwilligung: Anteil „Alle akzeptieren“, „Nur notwendige“ und „Banner ignoriert“.
- Unterschiedliche Lesetiefe (Scrolltiefe) und Absprünge.
- Menü auf dem Handy wird automatisch geöffnet, wenn ein Link nur dort erreichbar ist.

Formulare werden standardmäßig im Browser abgefangen: GTM misst die Einsendung,
bei Netlify kommt nichts an (schont das Kontingent von 100 Einsendungen/Monat).

NUR FÜR DIE EIGENE TESTSEITE MIT EIGENER GA4-TEST-PROPERTY.

Aufrufe (im Ordner mit konfiguration.json):
  python traffic_engine.py --probe                     1 Besuch, Browser sichtbar
  python traffic_engine.py --probe --reise NAME        1 Besuch mit bestimmter Reise
  python traffic_engine.py --alle-reisen               jede Reise einmal (Funktionstest), unsichtbar
  python traffic_engine.py --besuche 10                10 Besuche am Stück
  python traffic_engine.py --fenster vormittag         ein Zeitfenster aus der Konfiguration, heute
  python traffic_engine.py --alle-fenster [--taeglich] alle Zeitfenster von heute (jeden Tag)
  python traffic_engine.py --takt 15                   für GitHub Actions: anteilige Besuche im Zeitfenster
  python traffic_engine.py --takt 15 --nur-pruefen     gibt nur die Anzahl aus, ohne Browser
  DEBUG=1 python traffic_engine.py --probe …           zeigt bei Fehlern die vollständige Fehlermeldung
"""

import argparse
import json
import os
import random
import sys
import time
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode, urlparse
from zoneinfo import ZoneInfo

BERLIN = ZoneInfo("Europe/Berlin")

ORDNER = Path.cwd()
MAX_PRO_TAG = 300  # Schutzgrenze
WOCHENTAGE = ["mo", "di", "mi", "do", "fr", "sa", "so"]
TRACKING_HOSTS = ("google-analytics.com", "googletagmanager.com", "doubleclick.net", "google.com",
                  "googleadservices.com", "googlesyndication.com", "youtube.com", "cookiebot.com",
                  "facebook.com", "facebook.net", "clarity.ms", "bing.com", "linkedin.com", "licdn.com")

DESKTOP_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36")
MOBIL_UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 "
            "(KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1")
VORNAMEN = ["Anna", "Jonas", "Sabine", "Mehmet", "Laura", "Peter", "Julia", "Tobias", "Nele", "Ole"]


class BesuchEnde(Exception):
    """Besucher verlässt die Seite planmäßig (Abbruch). Kein Fehler."""


# ---------------------------------------------------------------------------
def lade_konfiguration(pfad):
    with open(pfad, encoding="utf-8") as f:
        k = json.load(f)
    k.setdefault("quellen", [{"name": "direkt", "gewicht": 100, "utm_source": None}])
    k.setdefault("mobil_anteil", 0.5)
    k.setdefault("wiederkehr_anteil", 0.25)
    k.setdefault("formulare_abfangen", True)
    k.setdefault("einwilligung", None)
    k.setdefault("menue_selektor", None)
    k.setdefault("zeitfenster", [])
    k["url"] = k["url"].rstrip("/")
    if not k.get("reisen"):
        sys.exit("Keine Reisen in der Konfiguration.")
    namen = {q["name"] for q in k["quellen"]}
    for r in k["reisen"]:
        for q in r.get("quellen", []):
            if q not in namen:
                sys.exit(f"Reise '{r['name']}' nennt unbekannte Quelle '{q}'.")
    return k


def log(text):
    print(f"[{datetime.now(BERLIN):%H:%M:%S}] {text}", file=sys.stderr, flush=True)


def warte(von, bis):
    time.sleep(random.uniform(von, bis))


def gewichtet(liste):
    return random.choices(liste, weights=[e.get("gewicht", 1) for e in liste], k=1)[0]


def spanne(wert, standard):
    """[min, max] oder Zahl -> Zufallswert"""
    if wert is None:
        wert = standard
    if isinstance(wert, list):
        return random.uniform(wert[0], wert[1])
    return wert


def protokolliere(zeile):
    datei = ORDNER / "protokoll.csv"
    neu = not datei.exists()
    with datei.open("a", encoding="utf-8") as f:
        if neu:
            f.write("zeit;quelle;geraet;besucher;reise;einstieg;seiten;ga4_treffer;status\n")
        f.write(";".join(str(x) for x in zeile) + "\n")


def waehle_quelle(k, reise):
    erlaubt = reise.get("quellen")
    kandidaten = [q for q in k["quellen"] if not erlaubt or q["name"] in erlaubt]
    return gewichtet(kandidaten)


def waehle_einstieg(reise):
    e = reise.get("einstieg", "/")
    if isinstance(e, str):
        return e
    return gewichtet([x if isinstance(x, dict) else {"pfad": x[0], "gewicht": x[1]} for x in e])["pfad"]


def baue_url(k, pfad, quelle):
    url = k["url"] + pfad
    if not quelle.get("utm_source"):
        return url, "direkt"
    parameter = {"utm_source": quelle["utm_source"], "utm_medium": quelle.get("utm_medium", "referral")}
    for feld in ("utm_campaign", "utm_content", "utm_term"):
        if quelle.get(feld):
            parameter[feld] = quelle[feld]
    trenner = "&" if "?" in url else "?"
    return url + trenner + urlencode(parameter), f"{quelle['utm_source']}/{quelle.get('utm_medium', '')}"


# ---------------------------------------------------------------------------
# Formulare abfangen: jeder POST außer an Tracking-Dienste wird im Browser beantwortet
# ---------------------------------------------------------------------------
def abfangen(context):
    def behandle(route, request):
        host = urlparse(request.url).netloc
        if request.method != "POST" or any(host.endswith(t) for t in TRACKING_HOSTS):
            return route.continue_()
        if request.is_navigation_request():
            try:
                antwort = context.request.get(request.url)
                return route.fulfill(status=200, content_type="text/html; charset=utf-8", body=antwort.text())
            except Exception:
                return route.fulfill(status=200, content_type="text/html", body="<html><body>OK</body></html>")
        return route.fulfill(status=200, content_type="application/json", body='{"ok":true}')

    context.route("**/*", behandle)


# ---------------------------------------------------------------------------
# Element in die Bildschirmmitte holen – sonst verdecken feste Leisten (Handy-Leiste,
# Cookie-Banner, klebender Kopf) Felder und Knöpfe, und der Klick landet daneben.
# ---------------------------------------------------------------------------
def mittig(loc):
    try:
        loc.evaluate("e => e.scrollIntoView({block: 'center', inline: 'nearest'})")
        time.sleep(0.3)
    except Exception:
        pass


def ankreuzen(loc):
    mittig(loc)
    try:
        loc.check(timeout=4000)
    except Exception:
        try:
            loc.check(force=True, timeout=4000)
        except Exception:
            loc.evaluate("e => { e.checked = true; e.dispatchEvent(new Event('change', {bubbles: true})); }")


# ---------------------------------------------------------------------------
# Felder automatisch mit Testdaten füllen (nur sichtbare Felder im Container)
# ---------------------------------------------------------------------------
def fuelle_felder(page, container):
    felder = page.locator(f"{container} input, {container} textarea, {container} select")
    radios_erledigt = set()
    for i in range(felder.count()):
        f = felder.nth(i)
        try:
            if not f.is_visible():
                continue
            tag = f.evaluate("e => e.tagName.toLowerCase()")
            typ = (f.get_attribute("type") or "text").lower()
            name = (f.get_attribute("name") or f.get_attribute("id") or "").lower()
            if typ in ("hidden", "submit", "button", "reset", "file", "image"):
                continue
            mittig(f)
            if tag == "select":
                werte = f.evaluate("e => [...e.options].filter(o => o.value && !o.disabled).map(o => o.value)")
                if werte:
                    f.select_option(random.choice(werte))
            elif typ == "checkbox":
                # optionale Häkchen (Newsletter) nur manchmal, Pflicht-Häkchen immer
                if f.evaluate("e => e.required") or random.random() < 0.4:
                    ankreuzen(f)
            elif typ == "radio":
                if name in radios_erledigt:
                    continue
                radios_erledigt.add(name)
                gruppe = page.locator(f'{container} input[type="radio"][name="{f.get_attribute("name")}"]')
                if gruppe.evaluate_all("l => l.some(e => e.checked)"):
                    continue  # schon vorbelegt (z. B. ?leistung=… oder Standard-Versand)
                ankreuzen(gruppe.nth(random.randrange(gruppe.count())))
            elif tag == "textarea":
                f.fill("Automatischer Testbesuch – bitte ignorieren.")
            elif typ == "email" or "mail" in name:
                f.fill("test@example.com")
            elif typ == "tel" or "telefon" in name or "phone" in name:
                f.fill("040 66969 999")
            elif typ == "number":
                continue  # Mengenfelder behalten ihren Wert
            elif typ == "date":
                f.fill((datetime.now() + timedelta(days=random.randint(14, 90))).strftime("%Y-%m-%d"))
            elif "plz" in name or "zip" in name:
                f.fill(random.choice(["22761", "22765", "22844", "22926", "20095", "22303"]))
            elif name in ("ort", "stadt", "city"):
                f.fill("Hamburg")
            elif "strasse" in name:
                f.fill("Teststraße 1")
            elif "firma" in name or "company" in name:
                f.fill("Testfirma")
            else:
                f.fill(f"{random.choice(VORNAMEN)} Test")
            warte(0.3, 1.0)
        except Exception:
            continue


# ---------------------------------------------------------------------------
# Hilfen für Klickziele
# ---------------------------------------------------------------------------
def finde(page, k, selektoren, zufall=False):
    """Erstes sichtbares Element aus einer Selektorliste. Öffnet bei Bedarf das Handy-Menü.
    Mit zufall=True wird unter allen sichtbaren Treffern zufällig gewählt."""
    if isinstance(selektoren, str):
        selektoren = [selektoren]

    def sichtbare():
        treffer = []
        for s in selektoren:
            loc = page.locator(s)
            for i in range(min(loc.count(), 30)):
                if loc.nth(i).is_visible():
                    treffer.append(loc.nth(i))
                    if not zufall:
                        return treffer
        return treffer

    treffer = sichtbare()
    if not treffer and k.get("menue_selektor"):
        menue = page.locator(k["menue_selektor"])
        if menue.count() and menue.first.is_visible():
            menue.first.click()
            warte(0.6, 1.2)
            treffer = sichtbare()
            if not treffer:
                menue.first.click()  # Menü wieder schließen, sonst verdeckt es die Seite
                warte(0.4, 0.8)
    if not treffer:
        raise LookupError(f"Nicht gefunden: {', '.join(selektoren)}")
    return random.choice(treffer) if zufall else treffer[0]


def lies_seite(page, tiefe):
    """Scrollt bis zu einem Anteil der Seitenhöhe (0–1) und verweilt dabei."""
    hoehe = page.evaluate("document.documentElement.scrollHeight - innerHeight")
    ziel = max(0, hoehe * tiefe)
    pos = page.evaluate("scrollY")
    while pos < ziel - 10:
        schritt = random.randint(250, 650)
        page.mouse.wheel(0, schritt)
        pos += schritt
        warte(0.7, 2.0)
    warte(1.5, 4)


# ---------------------------------------------------------------------------
# Schritte einer Reise
# ---------------------------------------------------------------------------
def fuehre_schritt_aus(page, k, s, zaehler):
    art = s["art"]

    if art == "lesen":
        lies_seite(page, spanne(s.get("tiefe"), [0.4, 0.9]))
        warte(*s.get("verweilen", [2, 6]))

    elif art == "warten":
        warte(*s.get("sekunden", [3, 8]))

    elif art == "aufruf":
        page.goto(k["url"] + s["pfad"], wait_until="load", timeout=30000)
        zaehler["seiten"] += 1
        warte(2, 4)

    elif art == "zurueck":
        page.go_back(wait_until="load", timeout=20000)
        warte(2, 4)

    elif art in ("klick", "seite"):
        ziel = finde(page, k, s["selektor"], s.get("zufall", False))
        mittig(ziel)
        warte(0.8, 2.0)
        if art == "klick":
            ziel.click(no_wait_after=True)
            warte(2, 4)
        else:
            with page.expect_navigation(timeout=15000, wait_until="load"):
                ziel.click()
            zaehler["seiten"] += 1
            warte(2, 5)
            if s.get("lesen", True):
                lies_seite(page, spanne(s.get("tiefe"), [0.3, 0.8]))

    elif art == "formular_standard":
        sel = s["selektor"]
        page.locator(sel).first.scroll_into_view_if_needed(timeout=10000)
        fuelle_felder(page, sel)
        if random.random() < s.get("abbruch", 0):
            raise BesuchEnde("Formular ausgefüllt, nicht abgeschickt")
        knopf = s.get("absenden") or f"{sel} button[type=submit], {sel} input[type=submit]"
        warte(1, 2.5)
        try:
            mittig(page.locator(knopf).first)
            with page.expect_navigation(timeout=15000, wait_until="load"):
                page.locator(knopf).first.click()
            zaehler["seiten"] += 1
        except Exception:
            pass
        warte(3, 6)

    elif art == "formular_ajax":
        sel = s["selektor"]
        page.locator(sel).first.scroll_into_view_if_needed(timeout=10000)
        fuelle_felder(page, sel)
        warte(1, 2.5)
        mittig(page.locator(s["absenden"]).first)
        page.locator(s["absenden"]).first.click()
        if s.get("erfolg_selektor"):
            page.wait_for_selector(s["erfolg_selektor"], state="visible", timeout=15000)
        warte(3, 6)

    elif art == "formular_mehrstufig":
        # Schritt-Container: [data-schritt="1"], … ; Abbruchquote je Schritt
        sel = s["selektor"]
        abbruch = s.get("abbruch", {})
        page.locator(sel).first.scroll_into_view_if_needed(timeout=10000)
        for nr in range(1, s.get("schritte", 3) + 1):
            container = f'{sel} [data-schritt="{nr}"]'
            page.wait_for_selector(container, state="visible", timeout=10000)
            warte(1.5, 4)
            fuelle_felder(page, container)
            if random.random() < abbruch.get(str(nr), 0):
                warte(3, 8)
                raise BesuchEnde(f"Anfrage in Schritt {nr} abgebrochen")
            if nr < s.get("schritte", 3):
                knopf = page.locator(f"{container} [data-weiter]").first
                mittig(knopf)
                knopf.click()
            else:
                knopf = page.locator(f"{container} button[type=submit]").first
                mittig(knopf)
                with page.expect_navigation(timeout=15000, wait_until="load"):
                    knopf.click()
                zaehler["seiten"] += 1
        warte(3, 6)

    elif art == "video":
        rahmen = finde(page, k, s.get("selektor", "iframe[src*='youtube']"))
        rahmen.scroll_into_view_if_needed(timeout=10000)
        warte(1.5, 3)
        box = rahmen.bounding_box()
        if box:
            page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        warte(*s.get("sekunden", [20, 60]))

    else:
        raise ValueError(f"Unbekannte Schrittart: {art}")


# ---------------------------------------------------------------------------
# Ein Besuch
# ---------------------------------------------------------------------------
def einwilligen(page, k, besucher):
    e = k.get("einwilligung")
    if not e or besucher != "neu":
        return "-"
    wahl = random.random()
    try:
        if wahl < e.get("anteil_alle", 0.7):
            page.locator(e["alle"]).first.click(timeout=6000)
            ergebnis = "alle"
        elif wahl < e.get("anteil_alle", 0.7) + e.get("anteil_ablehnen", 0.2):
            page.locator(e["ablehnen"]).first.click(timeout=6000)
            ergebnis = "abgelehnt"
        else:
            ergebnis = "ignoriert"
        warte(1, 2)
        return ergebnis
    except Exception:
        return "banner fehlt"


def ein_besuch(browser, k, reise_name=None):
    stamm = ORDNER / "stammbesucher"
    stamm.mkdir(exist_ok=True)
    mobil = random.random() < k["mobil_anteil"]

    vorhandene = sorted(stamm.glob("*.json"))
    stamm_datei, besucher = None, "neu"
    if vorhandene and random.random() < k["wiederkehr_anteil"]:
        stamm_datei, besucher = random.choice(vorhandene), "wiederkehrend"
    elif len(vorhandene) < 12:
        stamm_datei = stamm / f"besucher_{len(vorhandene) + 1}.json"

    opt = dict(locale="de-DE", timezone_id="Europe/Berlin", accept_downloads=True,
               user_agent=MOBIL_UA if mobil else DESKTOP_UA,
               viewport={"width": 390, "height": 844} if mobil else random.choice(
                   [{"width": 1440, "height": 900}, {"width": 1920, "height": 1080}, {"width": 1366, "height": 768}]),
               is_mobile=mobil, has_touch=mobil, device_scale_factor=3 if mobil else 2)
    if besucher == "wiederkehrend":
        opt["storage_state"] = str(stamm_datei)

    if reise_name:
        reise = next((r for r in k["reisen"] if r["name"] == reise_name), None)
        if not reise:
            sys.exit(f"Reise '{reise_name}' gibt es nicht. Vorhanden: {', '.join(r['name'] for r in k['reisen'])}")
    else:
        reise = gewichtet(k["reisen"])

    context = browser.new_context(**opt)
    if k["formulare_abfangen"]:
        abfangen(context)
    ga4 = []
    context.on("request", lambda r: ga4.append(1) if "/g/collect" in r.url else None)

    quelle = waehle_quelle(k, reise)
    einstieg = waehle_einstieg(reise)
    url, quelle_text = baue_url(k, einstieg, quelle)
    zaehler = {"seiten": 1}
    status = "ok"
    einwilligung = "-"
    page = context.new_page()
    page.on("popup", lambda neu: neu.close())
    page.on("download", lambda d: d.cancel())
    try:
        page.goto(url, wait_until="load", timeout=30000)
        einwilligung = einwilligen(page, k, besucher)
        warte(1.5, 4)
        for nr, schritt in enumerate(reise["schritte"], 1):
            if random.random() < schritt.get("ende_chance", 0):
                raise BesuchEnde(f"verlässt vor Schritt {nr}")
            if random.random() > schritt.get("chance", 1):
                continue
            try:
                fuehre_schritt_aus(page, k, schritt, zaehler)
            except BesuchEnde:
                raise
            except Exception:
                if schritt.get("optional"):
                    continue
                raise
        warte(4, 7)  # GA4 Zeit zum Senden geben
    except BesuchEnde as ende:
        status = f"abbruch: {ende}"
        warte(3, 6)
    except Exception as fehler:  # ein Fehler darf den Lauf nicht stoppen
        if os.environ.get("DEBUG"):
            traceback.print_exc()
        status = f"fehler: {type(fehler).__name__}: {str(fehler).splitlines()[0][:80]}"
    finally:
        if stamm_datei is not None:
            try:
                context.storage_state(path=str(stamm_datei))
            except Exception:
                pass
        context.close()

    geraet = "Handy" if mobil else "Desktop"
    log(f"{geraet:7} | {quelle_text:26} | {besucher:13} | {reise['name']:22} | {zaehler['seiten']} S. | "
        f"Consent: {einwilligung:9} | GA4: {len(ga4):2} | {status}")
    protokolliere([datetime.now().isoformat(timespec="seconds"), quelle_text, geraet, besucher, reise["name"],
                   einstieg, zaehler["seiten"], len(ga4), status])
    return len(ga4)


# ---------------------------------------------------------------------------
# Zeitfenster (wie Engine v1)
# ---------------------------------------------------------------------------
def fenster_laeuft_heute(f):
    tage = [t.lower()[:2] for t in f.get("wochentage", WOCHENTAGE)]
    return WOCHENTAGE[datetime.now(BERLIN).weekday()] in tage


def ein_fenster(browser, k, f):
    von, bis = f["von"], f["bis"]
    lo, hi = f.get("anzahl", [10, 15]) if isinstance(f.get("anzahl"), list) else (f.get("anzahl", 10),) * 2
    n = min(random.randint(lo, hi), MAX_PRO_TAG)
    jetzt = datetime.now()
    start = jetzt.replace(hour=von, minute=0, second=0, microsecond=0)
    ende = jetzt.replace(hour=bis, minute=0, second=0, microsecond=0)
    if not fenster_laeuft_heute(f):
        log(f"Fenster '{f['name']}' ist heute nicht vorgesehen.")
        return
    if jetzt >= ende - timedelta(minutes=10):
        log(f"Fenster '{f['name']}' ({von}-{bis} Uhr) ist heute schon vorbei.")
        return
    if jetzt > start:
        start = jetzt
    dauer = (ende - start).total_seconds() - 300
    plan = sorted(start + timedelta(seconds=random.uniform(0, dauer)) for _ in range(n))
    log(f"Fenster '{f['name']}' {von}-{bis} Uhr: {n} Besuche, erster {plan[0]:%H:%M}, letzter {plan[-1]:%H:%M}.")
    summe = 0
    for nr, t in enumerate(plan, 1):
        pause = (t - datetime.now()).total_seconds()
        if pause > 0:
            log(f"Besuch {nr}/{n} um {t:%H:%M}.")
            time.sleep(pause)
        summe += ein_besuch(browser, k)
    log(f"Fenster '{f['name']}' erledigt: {n} Besuche, {summe} GA4-Treffer.")


def besuche_im_takt(k, takt_minuten):
    """Anzahl Besuche für einen Aufruf, der alle takt_minuten erfolgt (z. B. per GitHub Actions)."""
    jetzt = datetime.now(BERLIN)
    for f in k["zeitfenster"]:
        if not (f["von"] <= jetzt.hour < f["bis"]):
            continue
        tage = [t.lower()[:2] for t in f.get("wochentage", WOCHENTAGE)]
        if WOCHENTAGE[jetzt.weekday()] not in tage:
            continue
        anz = f.get("anzahl", 10)
        mittel = sum(anz) / 2 if isinstance(anz, list) else anz
        erwartet = mittel * takt_minuten / ((f["bis"] - f["von"]) * 60)
        n = int(erwartet) + (1 if random.random() < erwartet - int(erwartet) else 0)
        log(f"Takt {takt_minuten} Min., Fenster '{f['name']}' läuft: {n} Besuch(e) (Erwartung {erwartet:.2f}).")
        return min(n, 6)
    log(f"Takt: {jetzt:%H:%M} Uhr Berliner Zeit liegt in keinem Zeitfenster.")
    return 0


def alle_fenster(browser, k, taeglich):
    fenster = sorted(k["zeitfenster"], key=lambda f: f["von"])
    if not fenster:
        sys.exit("Keine Zeitfenster in der Konfiguration.")
    while True:
        for f in fenster:
            ein_fenster(browser, k, f)
        if not taeglich:
            return
        morgen = (datetime.now() + timedelta(days=1)).replace(hour=0, minute=5, second=0, microsecond=0)
        log(f"Tagesplan erledigt. Weiter am {morgen:%d.%m.}.")
        time.sleep(max(0, (morgen - datetime.now()).total_seconds()))


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Traffic-Engine v2 für die mehrseitige Testseite")
    ap.add_argument("--konfiguration", default="konfiguration.json")
    ap.add_argument("--probe", action="store_true", help="1 Besuch mit sichtbarem Browser")
    ap.add_argument("--reise", help="bestimmte Reise erzwingen (Name aus der Konfiguration)")
    ap.add_argument("--alle-reisen", action="store_true", help="jede Reise einmal durchlaufen (Funktionstest)")
    ap.add_argument("--besuche", type=int, default=0)
    ap.add_argument("--fenster", help="Name eines Zeitfensters aus der Konfiguration")
    ap.add_argument("--alle-fenster", action="store_true")
    ap.add_argument("--taeglich", action="store_true", help="mit --alle-fenster: jeden Tag wiederholen")
    ap.add_argument("--sichtbar", action="store_true")
    ap.add_argument("--takt", type=int, help="Aufrufabstand in Minuten für Zeitplaner wie GitHub Actions")
    ap.add_argument("--nur-pruefen", action="store_true", help="mit --takt: nur die Anzahl ausgeben")
    a = ap.parse_args()

    k = lade_konfiguration(ORDNER / a.konfiguration)
    if a.takt:
        n = besuche_im_takt(k, a.takt)
        if a.nur_pruefen:
            print(n)
            return
        if n == 0:
            return
        a.besuche = n
    if not (a.probe or a.besuche or a.fenster or a.alle_fenster or a.alle_reisen):
        ap.print_help()
        return

    from playwright.sync_api import sync_playwright  # erst hier, damit --nur-pruefen ohne Playwright läuft
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not (a.probe or a.sichtbar))
        try:
            if a.probe:
                ein_besuch(browser, k, a.reise)
            elif a.alle_reisen:
                for r in k["reisen"]:
                    ein_besuch(browser, k, r["name"])
            elif a.besuche:
                summe = 0
                for i in range(min(a.besuche, MAX_PRO_TAG)):
                    summe += ein_besuch(browser, k, a.reise)
                    if i < a.besuche - 1:
                        warte(5, 20)
                log(f"Fertig: {a.besuche} Besuche, {summe} GA4-Treffer.")
            elif a.fenster:
                f = next((f for f in k["zeitfenster"] if f["name"] == a.fenster), None)
                if not f:
                    sys.exit(f"Zeitfenster '{a.fenster}' fehlt in der Konfiguration.")
                ein_fenster(browser, k, f)
            else:
                alle_fenster(browser, k, a.taeglich)
        except KeyboardInterrupt:
            log("Beendet.")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
