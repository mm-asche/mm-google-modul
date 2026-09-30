# Einrichtung: Repository, Netlify, GTM und automatischer Traffic

Dauer: ca. 30 Minuten. Voraussetzung: GitHub-Konto, Netlify-Konto, eigener GTM-Container und eigene GA4-Test-Property.

---

## 1. GTM-ID eintragen und Seite bauen

1. `quellen/einstellungen.json` öffnen, `"gtm_id": "GTM-XXXXXXX"` durch die eigene Container-ID ersetzen.
2. Im Terminal im Projektordner:
   ```bash
   python3 werkzeuge/seiten_bauen.py
   ```
3. Lokal ansehen (optional):
   ```bash
   python3 -m http.server 8765 --directory site
   ```
   Dann im Browser `http://localhost:8765` öffnen.

Weitere Schalter in `einstellungen.json`:

| Schalter | Werte | Wofür |
|---|---|---|
| `consent_modus` | `eigener_banner` · `cookiebot` · `aus` | Consent Mode V2 per eigenem Banner (Weg 2), per Cookiebot (Weg 1, `cookiebot_id` nötig) oder ohne Banner |
| `video_modus` | `direkt` · `nach_einwilligung` | YouTube sofort laden oder erst nach Marketing-Einwilligung |
| `search_console_meta` | Code aus der Search Console | Verifizierung per HTML-Tag (trotz `noindex` möglich) |
| `basis_url` | z. B. `https://holzwerk-hanssen.netlify.app` | für Canonical-Links und `sitemap.xml` |

Nach jeder Änderung neu bauen.

**PDFs ändern:** Die Vorlagen liegen in `werkzeuge/pdf/*.html`. Im Browser öffnen, als PDF drucken (A4, ohne Kopf-/Fußzeilen, Hintergrundgrafiken an) und nach `site/downloads/` speichern.

## 2. Repository anlegen

Am einfachsten mit GitHub Desktop oder im Terminal:
```bash
git init
```
```bash
git add .
```
```bash
git commit -m "Holzwerk Hanssen Demo-Website"
```
Dann auf github.com ein neues Repository anlegen (Empfehlung: **Public**, dann sind Actions-Minuten unbegrenzt kostenlos) und den Anweisungen „push an existing repository“ folgen.

> Beim Hochladen per Browser werden versteckte Ordner wie `.github` nicht mitgenommen. Dann die Datei `.github/workflows/testseiten-traffic.yml` auf GitHub über **Add file → Create new file** anlegen und den Inhalt hineinkopieren.

## 3. Netlify mit dem Repository verbinden

1. Netlify → **Add new project → Import an existing project → GitHub** → Repository wählen.
2. Build-Einstellungen: Build-Befehl leer lassen, Veröffentlichungsordner `site` (steht auch in `netlify.toml`).
3. Nach dem ersten Deploy die Adresse (z. B. `…netlify.app`) kopieren, unter **Project configuration → Change project name** einen sprechenden Namen vergeben.
4. **Formulare:** Netlify erkennt die fünf Formulare automatisch (`kontakt`, `rueckruf-ajax`, `projekt-anfrage`, `whitepaper`, `bewerbung`). Gegebenenfalls unter **Forms** die Formularerkennung einschalten. Im kostenlosen Tarif gilt ein Monatskontingent für Einsendungen. Der Simulator fängt deshalb alle Formulare im Browser ab.

Die Menübezeichnungen in Netlify ändern sich gelegentlich. Wenn etwas anders heißt, sinngemäß suchen.

Danach `basis_url` in `einstellungen.json` auf die echte Adresse setzen, neu bauen, committen und pushen. Netlify veröffentlicht automatisch.

## 4. Traffic-Simulator einrichten

1. `traffic/konfiguration.json` → `"url"` auf die Netlify-Adresse setzen, committen, pushen.
2. GitHub → **Actions** → Workflows aktivieren → **Testseiten-Traffic** → **Run workflow** (3 Besuche).
3. Im Lauf den Schritt **Besuche ausführen** öffnen. Jede Zeile zeigt Gerät, Quelle, Reise, Seitenzahl, Consent-Wahl und GA4-Treffer.
4. Gegenprobe in GA4 unter **Berichte → Echtzeit**.

**Zeitplan:** Mo–Fr 9–12 Uhr (15–20 Besuche) und 13–15 Uhr (12–18), täglich 18–21 Uhr (8–12). Ändern in `konfiguration.json` → `zeitfenster`. Neue Uhrzeiten müssen auch in der Workflow-Datei im UTC-Bereich der `cron`-Zeilen liegen.

**Lokal testen** (einmalig `pip install playwright` und `python -m playwright install chromium`):
```bash
cd traffic
```
```bash
python traffic_engine.py --probe --reise shop_kauf
```
`--alle-reisen` läuft jede Reise einmal durch, als Funktionstest nach Änderungen an der Seite. Mit `DEBUG=1` davor erscheinen vollständige Fehlermeldungen.

### Was die Engine v2 anders macht als die alte

| | Engine v1 (alte Testseite) | Engine v2 (dieses Projekt) |
|---|---|---|
| Besuch | 1 Seite, 1 Aktion | „Reise“ über mehrere Seiten |
| Einstieg | immer Startseite | je Reise gewichtete Einstiegsseiten |
| Quellen | global gewichtet | je Reise passende Quellen (z. B. Jobportale nur auf Karriere) |
| Formulare | abschicken | abschicken **oder** abbrechen, mehrstufig mit Abbruch je Schritt |
| Consent | – | Anteil „alle“ / „nur notwendige“ / „ignoriert“ |
| Shop | – | Produkt ansehen, Warenkorb, Kauf oder Abbruch |
| Handy | Seite im Handyformat | zusätzlich Handy-Menü und feste Handy-Leiste berücksichtigt |

### Reisen (in `konfiguration.json`, Gewichte relativ)
`absprung` · `leistung_umsehen` · `leistung_anruf` · `anfrage_komplett` · `anfrage_abbruch` · `kontakt_formular` · `rueckruf_ajax` · `kontakt_klicks` · `whitepaper` · `ratgeber_lesen` · `shop_kauf` · `shop_abbruch` · `karriere_bewerbung` · `karriere_umsehen` · `ueber_uns_video` · `mehrseiten_tour` · `kaputter_link`

Schrittarten: `lesen`, `warten`, `aufruf`, `zurueck`, `klick`, `seite`, `formular_standard`, `formular_ajax`, `formular_mehrstufig`, `video`.
Optionen je Schritt: `chance` (Schritt nur mit dieser Wahrscheinlichkeit), `ende_chance` (Besuch endet vorher), `optional` (Fehler überspringen), `zufall` (zufälliges Element aus der Selektorliste), `abbruch` (Formular ausfüllen, aber nicht abschicken).

## Grenzen

- **Standort in GA4:** Besuche aus GitHub Actions kommen aus Rechenzentren, meist USA.
- **Organische Suche** lässt sich nicht simulieren, Google/CPC nur per UTM (echte Klicks mit `gclid` entstehen nur durch live geschaltete Anzeigen, die hier bewusst nicht vorgesehen sind).
- **60-Tage-Regel:** GitHub schaltet Zeitpläne in öffentlichen Repositorys nach 60 Tagen ohne Commit ab. Dann unter Actions wieder aktivieren.
- **Nur für diese Testseite** verwenden, nie für Seiten von Kunden oder Partnern.
