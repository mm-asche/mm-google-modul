# Tracking-Plan – Holzwerk Hanssen (Demo-Website)

Welche Elemente der Seite sich mit GTM messen lassen, mit welchem Trigger, und wofür sie im Kurs gebraucht werden.
Die Seite schreibt bewusst **nur drei Dinge selbst** in den dataLayer: Seitendaten, Consent und Shop-Ereignisse.
Alles andere (Klicks, Formulare, Scrolltiefe, Video) muss GTM selbst erfassen – das ist der Übungsstoff.

---

## 1. Was die Seite von sich aus liefert

### Seitendaten (auf jeder Seite, vor GTM)
```js
dataLayer.push({ seitentyp: "leistung", inhaltsgruppe: "Leistungen", leistung: "kuechen" });
```
| Schlüssel | Werte | Nutzen |
|---|---|---|
| `seitentyp` | startseite, leistungsuebersicht, leistung, kontakt, anfrage, danke, karriere, stelle, ratgeber_uebersicht, ratgeber_artikel, whitepaper, shop_liste, produkt, warenkorb, kasse, bestellbestaetigung, ueber_uns, rechtliches, fehler_404 | Datenschichtvariable, Trigger-Bedingung, Custom Dimension |
| `inhaltsgruppe` | Startseite, Leistungen, Kontakt, Conversion, Karriere, Ratgeber, Shop, Unternehmen, Rechtliches, Fehlerseite | GA4-Parameter `content_group` → Bericht „Seiten und Bildschirme“ nach Inhaltsgruppe |
| `leistung` | kuechen, einbauschraenke, treppen, innentueren (nur auf passenden Seiten) | Zielgruppen „hat Küchenseiten gesehen“, Custom Dimension |

### Consent (eigener Banner, `consent_modus: eigener_banner`)
- Vor GTM: `gtag('consent','default', {… alles 'denied' …, wait_for_update: 500})`
- Bei gespeicherter Wahl sofort `gtag('consent','update', …)`
- Nach Klick im Banner: `consent update` + Ereignis
```js
{ event: "consent_aktualisiert", consent_art: "alle|notwendig|auswahl", consent_statistik: "ja|nein", consent_marketing: "ja|nein" }
```
- IDs: `#consent-alle`, `#consent-ablehnen`, `#consent-einstellungen`, `#consent-speichern`, Footer-Link `#cookie-einstellungen`
- Umschaltbar auf Cookiebot (`consent_modus: cookiebot` + `cookiebot_id`) oder ganz aus (`aus`) → Vergleich Weg 1 / Weg 2 in P2.11.2

### Shop (GA4-E-Commerce nach Google-Empfehlung)
Vor jedem Ereignis `dataLayer.push({ecommerce: null})`. Währung EUR, `value` = Warenwert brutto ohne Versand.

| Ereignis | Wann | Seite |
|---|---|---|
| `view_item_list` | Produktliste sichtbar (Listen: „Shop Übersicht“, „Startseite Shop-Teaser“, „Produktseite Empfehlungen“) | /shop/, /, Produktseiten |
| `select_item` | Klick auf Produktkarte `.js-produkt-link` | Listen |
| `view_item` | Produktseite geladen | /shop/&lt;produkt&gt;/ |
| `add_to_cart` | Button `.js-in-warenkorb` oder `#produkt-in-warenkorb`, Menge erhöht | Listen, Produkt, Warenkorb |
| `remove_from_cart` | Entfernen / Menge verringert | /shop/warenkorb/ |
| `view_cart` | Warenkorb geöffnet | /shop/warenkorb/ |
| `begin_checkout` | Kasse geöffnet | /shop/kasse/ |
| `add_shipping_info` | Versandart gewählt (spätestens beim Absenden), `shipping_tier` | /shop/kasse/ |
| `add_payment_info` | Zahlungsart gewählt (spätestens beim Absenden), `payment_type` | /shop/kasse/ |
| `purchase` | Bestätigungsseite, **einmal je Bestellnummer** (Neuladen löst keinen zweiten Kauf aus) | /shop/bestellung-bestaetigt/ |

GTM: GA4-Ereignis-Tag, Ereignisname `{{Event}}`, Option „E-Commerce-Daten senden → Datenschicht“, Trigger „Benutzerdefiniertes Ereignis“ mit Regex `^(view_item_list|select_item|view_item|add_to_cart|remove_from_cart|view_cart|begin_checkout|add_shipping_info|add_payment_info|purchase)$`.
Google-Ads-Conversion „Kauf“: Wert aus Datenschichtvariable `ecommerce.value`, Transaktions-ID aus `ecommerce.transaction_id`.

---

## 2. Conversions

| Conversion | Messung (Empfehlung) | Alternative / Übung | Kurs |
|---|---|---|---|
| **Projektanfrage** (mehrstufig) | Seitenaufruf `/danke-anfrage/` + Referrer enthält `/anfrage/` | Trigger „Formularsendung“ auf `#form-anfrage` | P2.8, P5.2 |
| **Kontaktformular** | Formularsendung `#form-standard` (Form ID `form-standard`) | Seitenaufruf `/danke-anfrage/` mit Referrer `/kontakt/` | P2.8, P4.3 |
| **Rückruf (AJAX)** | Listener-Tag auf `demoform:gesendet` → `dataLayer.push({event:'ajax_form_erfolg'})` → Benutzerdefiniertes Ereignis | Klick-Trigger auf `#ajax-button` (zeigt, warum das falsch zählt) | P2.8.1 |
| **Anruf** | Klick – Nur Links, `Click URL` beginnt mit `tel:` | nach Position trennen: `#kopf-telefon`, `#mobil-anrufen`, `#cta-leistung-telefon`, `#link-telefon`, `#footer-telefon-1..3`, `#standort-telefon-*` | P2.9 |
| **Whitepaper-Lead** | Seitenaufruf `/danke-whitepaper/` | zusätzlich Download `#link-whitepaper` als Ereignis | P4.5 |
| **Kauf** | `purchase` aus dem dataLayer, mit Wert | – | P3.7, P5.8, P6.9 |
| **Bewerbung** (sekundär!) | Seitenaufruf `/danke-bewerbung/` | Formularsendung `#form-bewerbung` | P4.5 (Ausschluss) |

> **Wichtig für Google Ads:** Bewerbungen nie als primäre Conversion importieren – sonst optimiert Smart Bidding auf Bewerber statt auf Kunden. Sie gehören in eine eigene Zielgruppe und werden im Kunden-Remarketing ausgeschlossen.

---

## 3. Klicks und Interaktionen

### Kontaktwege
| Element | Selektor | Art |
|---|---|---|
| Telefon (Kopf, Footer, Leistung, Kontakt, Standorte, Handy-Leiste) | `a[href^="tel:"]`, IDs s. o. | tel:-Link |
| E-Mail | `#kopf-mail`, `#link-mail`, `#link-initiativbewerbung` | mailto:-Link |
| WhatsApp | `#link-whatsapp`, `#cta-leistung-whatsapp`, `#link-whatsapp-footer` | externer Link wa.me |
| Google Maps | `#link-maps`, `#standort-maps-*` | externer Link |
| Instagram | `#link-instagram` | externer Link |
| Hersteller Blum | `#link-hersteller-blum` (Küchenseite) | externer Link (Outbound) |

### CTAs (für Trigger nach ID / CSS-Klasse, P2.7, P4.3)
- Namensschema: `cta-<ort>-<ziel>`, z. B. `#cta-hero-anfrage`, `#cta-leistung-anfrage`, `#cta-leistung-anfrage-unten`, `#cta-band-anfrage`, `#nav-cta-anfrage`, `#mobil-anfrage`
- Navigation: `#nav-leistungen`, `#nav-kuechen` …, `#nav-shop`, `#nav-ratgeber`, `#nav-karriere`, `#nav-ueber-uns`, `#nav-kontakt`, `#nav-toggle` (Handy-Menü)
- Footer: `#footer-<ziel>`
- Teaser/Karten: `#teaser-*`, `#uebersicht-*`, `#verwandt-*`, `#ratgeber-artikel-*`, `#stelle-<slug>`
- FAQ-Akkordeon: `<details id="faq-…">` – Klick auf `summary` (Trigger „Alle Elemente“, Click Element matcht CSS-Selektor `details[id^="faq-"] summary`)

### Downloads
| Datei | Link | Besonderheit |
|---|---|---|
| `/downloads/ratgeber-kuechenkosten.pdf` | `#link-whitepaper` (nur auf Danke-Seite) | mit `download`-Attribut, hinter Formular |
| `/downloads/pflegeanleitung-massivholz.pdf` | `#footer-pflegeanleitung`, `#link-pflegeanleitung`, `#ratgeber-pflegeanleitung`, `#artikel-pflegeanleitung` | frei, **teils ohne `download`-Attribut** (öffnet im Browser) |
| `/downloads/preisliste-leistungen.pdf` | `#link-preisliste` | frei, mit `download` |

GA4-Erweiterte Messung erkennt PDF-Downloads automatisch als `file_download` – gut für den Vergleich „automatisch vs. selbst gebaut“.

### Formulare (Übersicht)
| Formular | Element | Absenden | Netlify-Name | Felder für Enhanced Conversions |
|---|---|---|---|---|
| Kontakt | `form#form-standard` | Submit → `/danke-anfrage/` | `kontakt` | `#kontakt-email`, `#kontakt-telefon` |
| Rückruf | `div#form-ajax` (kein form!) | `#ajax-button`, Erfolg `#ajax-erfolg` | `rueckruf-ajax` | `#rueckruf-telefon` |
| Projektanfrage | `form#form-anfrage`, 3 Schritte | Submit in Schritt 3 → `/danke-anfrage/` | `projekt-anfrage` | `#anfrage-email`, `#anfrage-telefon`, `#anfrage-name` |
| Whitepaper | `form#form-whitepaper` | → `/danke-whitepaper/` | `whitepaper` | `#whitepaper-email`, `#whitepaper-vorname` |
| Bewerbung | `form#form-bewerbung` (je Stelle) | → `/danke-bewerbung/` | `bewerbung` | – (nicht für Ads) |
| Kasse | `form#form-kasse` | JS → `/shop/bestellung-bestaetigt/` | – (kein Versand) | `#kasse-email`, `#kasse-telefon`, `#kasse-vorname`, `#kasse-nachname` |

### Mehrstufige Anfrage (Trichter, P5.2 / Zielgruppe „Formular angefangen“, P4.5)
- Schritt 2 und 3 setzen den URL-Anker `#schritt-2`, `#schritt-3` → GTM-Trigger **Verlaufsänderung**, Variable *History New URL Fragment*
- Buttons: `#anfrage-weiter-1`, `#anfrage-weiter-2`, `#anfrage-zurueck-2`, `#anfrage-zurueck-3`, `#anfrage-absenden`
- Vorbelegung per `?leistung=kuechen|einbauschraenke|treppen|innentueren` (Links von den Leistungsseiten) → Parameter lässt sich als Variable (URL → Abfrage) auslesen
- Vorschlag Ereignisse: `anfrage_schritt` mit Parameter `schritt` (1–3), dazu `generate_lead` auf der Danke-Seite

### Scrolltiefe (P4.3, P5.6)
Lange Seiten: Startseite, alle Leistungsseiten, Ratgeber-Artikel, Stellenanzeigen. Trigger „Scrolltiefe“ vertikal 25/50/75/90 %.

### Video (P5.6)
- `/ueber-uns/`: YouTube-Einbettung mit `enablejsapi=1` (`#youtube-ueber-uns`), Video „Wege im Handwerk » Tischler*in“ (Handwerkskammer Flensburg, ID `hj0zx09EoEg`)
- `video_modus: direkt` (Standard) oder `nach_einwilligung` (Zwei-Klick-Lösung, Button `#video-laden`) in `quellen/einstellungen.json`

### Fehlerseite
`404.html` mit `seitentyp: fehler_404` und Seitentitel „Seite nicht gefunden (404)“. Der Simulator ruft gelegentlich einen alten Newsletter-Link `/angebote-herbst-2025/` auf.

---

## 4. Bewusst eingebaute Übungsfallen (P5.10 Debugging)
1. **Button-Text in `<span>`**: `#cta-hero-anfrage`, `#cta-leistung-anfrage`, `#cta-stelle-bewerben`, `#cta-karriere-stellen` – ein Klick auf den Text liefert als Click Element das `span`, nicht den Link. Lösung: „Klick – Nur Links“ oder Selektor `#id, #id *`.
2. **AJAX-Formular ohne `<form>`**: Formularsendungs-Trigger feuert nie, Klick-Trigger zählt auch Fehlversuche.
3. **PDF-Links ohne `download`-Attribut**: Der Browser öffnet die Datei statt sie zu speichern – Trigger auf Click URL endet mit `.pdf` statt auf Attribut.
4. **Gleiches Ziel, viele Links**: Telefon an 10+ Stellen – mit Click ID oder Positions-Parameter unterscheiden.
5. **Kasse ohne Formularversand**: `#form-kasse` verhindert das Absenden per JavaScript (`preventDefault`) – „Formularsendung“ mit „Auf Validierung prüfen“ zeigt den Unterschied.
6. **Neuladen der Bestätigungsseite**: `purchase` wird nur einmal gemeldet. Wer stattdessen auf den Seitenaufruf der Bestätigungsseite triggert, zählt doppelt.
7. **Handy-Menü**: Links in der Navigation sind auf dem Handy erst nach `#nav-toggle` sichtbar.

---

## 5. Empfohlene GA4-Einstellungen
- Erweiterte Messung an (Scrollen, ausgehende Klicks, Dateidownloads, Formularinteraktionen, Videointeraktionen)
- Benutzerdefinierte Dimensionen (ereignisbezogen): `seitentyp`, `leistung`, `formular_name`, `kontakt_position`
- Schlüsselereignisse: `generate_lead` (Anfrage/Kontakt/Rückruf), `purchase`, `whitepaper_download`; `bewerbung` nur als normales Ereignis
- Datenaufbewahrung auf 14 Monate stellen (für Looker-Vergleiche)
- Zielgruppen-Vorschläge: „Leistungsseite Küchen besucht“, „Anfrage begonnen, nicht abgeschickt“, „Warenkorb ohne Kauf“, „3+ Seiten in einer Sitzung“, „Karriere-Besucher“ (Ausschluss), „Käufer der letzten 30 Tage“ (Ausschluss)
