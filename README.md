# Holzwerk Hanssen – mehrseitige Demo-Website für das Google-Universum

Fiktive Tischlerei aus Hamburg als Übungsobjekt für Google Tag Manager, GA4, Google Ads und Looker Studio.
Eigenständiges Projekt neben der einseitigen „Tischlerei Beispiel“-Testseite (die bleibt unverändert).

**Alles ist erfunden:** Firma, Personen, Adressen. Die Telefonnummern stammen aus dem Bereich 040 66969-xxx, den die Bundesnetzagentur für Film und Fernsehen freihält. Die Seite ist `noindex`, Google-Ads-Kampagnen werden nur aufgebaut, nie veröffentlicht.

## Inhalt

| Ordner | Was |
|---|---|
| `site/` | Fertige Website, wird auf Netlify veröffentlicht (36 Seiten inkl. 9 Produktseiten und 3 Stellenanzeigen) |
| `quellen/` | Inhalte zum Bearbeiten: Seitentexte, `einstellungen.json` (GTM-ID, Consent, Firmendaten), `produkte.json`, `stellen.json` |
| `werkzeuge/seiten_bauen.py` | Baut `site/` aus `quellen/` (Python 3.9+, keine Zusatzpakete) |
| `werkzeuge/pdf/` | Vorlagen der drei PDFs (Whitepaper, Pflegeanleitung, Preisübersicht) |
| `traffic/` | Traffic-Engine v2 + `konfiguration.json` (Quellen, Besuchsreisen, Zeitfenster) |
| `.github/workflows/` | Zeitplan für automatische Besuche über GitHub Actions |
| `ads-assets/` | Bilder und Logos in den Formaten für pMax, Display und Demand Gen |
| `docs/` | Einrichtung, Tracking-Plan, Kursabdeckung, Kampagnen-Blaupause, Bildnachweise |

## Seitenstruktur

```
/                                   Startseite
/leistungen/                        Leistungsübersicht
/leistungen/kuechen-nach-mass/      ┐
/leistungen/einbauschraenke/        │ je eine Landingpage pro Anzeigengruppe
/leistungen/treppen/                │
/leistungen/innentueren/            ┘
/anfrage/                           Projektanfrage in 3 Schritten  → /danke-anfrage/
/kontakt/                           Kontaktformular, AJAX-Rückruf, tel/mail/WhatsApp, 3 Standorte
/karriere/ + 3 Stellenanzeigen      Kurzbewerbung                  → /danke-bewerbung/
/ratgeber/ + 2 Artikel
/ratgeber/kuechen-kosten/           Whitepaper-Formular            → /danke-whitepaper/ (PDF)
/shop/ + 9 Produkte, Warenkorb, Kasse, Bestätigung   (GA4-E-Commerce, keine echte Zahlung)
/ueber-uns/                         Team, YouTube-Video
/impressum/, /datenschutz/, 404
```

## Schnellstart

1. `quellen/einstellungen.json`: GTM-ID und später die Netlify-Adresse (`basis_url`) eintragen
2. `python3 werkzeuge/seiten_bauen.py`
3. Repository auf GitHub anlegen, Netlify mit dem Repository verbinden (Veröffentlichungsordner `site`)
4. `traffic/konfiguration.json`: `url` auf die Netlify-Adresse setzen
5. Unter **Actions** den Workflow „Testseiten-Traffic“ einmal von Hand starten

Ausführlich: [docs/Einrichtung.md](docs/Einrichtung.md)
