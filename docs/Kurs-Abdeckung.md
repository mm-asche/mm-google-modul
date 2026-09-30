# Kursabdeckung – welches Video nutzt welchen Teil der Seite

Bezug: `00-Kurs-Masterdatei.md` (Phasen 0–7). ✅ = direkt zeigbar, ◐ = zeigbar mit Einschränkung.

## Phase 1 – Erste Kampagne (nur Aufbau, nicht veröffentlichen)
| Video | Auf der Seite | |
|---|---|---|
| P1.2 Kampagnen / Anzeigengruppen / Anzeigen | 4 Leistungsseiten = 4 Anzeigengruppen, siehe `Kampagnen-Blaupause.md` | ✅ |
| P1.5 Keyword-Planer | Keyword-Ideen je Leistungsseite (Seitentitel sind keywordnah formuliert) | ✅ |
| P1.5.1 Search Console | Meta-Tag-Platz `search_console_meta`, `sitemap.xml`, Verifizierung über GTM möglich. Wegen `noindex` kaum Leistungsdaten | ◐ |
| P1.6.1 Standortlisten | 3 Standorte: Hamburg-Bahrenfeld, Norderstedt, Ahrensburg | ✅ |
| P1.8 RSA | Nutzenversprechen, Preise ab, USPs auf jeder Leistungsseite | ✅ |
| P1.9 Anzeigen-Assets | Sitelink-Ziele, Callouts, Anrufnummer (Film-Nummer) | ✅ |

## Phase 2 – Tracking
| Video | Auf der Seite | |
|---|---|---|
| P2.3 GTM installieren | Snippet auf allen Seiten, ID zentral in `einstellungen.json` | ✅ |
| P2.6 GA4 via GTM | Seitenaufrufe über 36 Seiten, Seitendaten im dataLayer | ✅ |
| P2.7 Variablen & Klick-Trigger | Einheitliche IDs `cta-*`, `nav-*`, `footer-*`, Klasse `js-in-warenkorb` | ✅ |
| P2.8 Conversion Formular | `/danke-anfrage/`, `#form-standard`, `#form-anfrage` | ✅ |
| P2.8.1 Listener-Tag | AJAX-Rückruf `#form-ajax`, Ereignis `demoform:gesendet` (gleich wie alte Testseite) | ✅ |
| P2.9 Telefon-Conversion | 10+ `tel:`-Links, Handy-Leiste `#mobil-anrufen` für Mobil-vs.-Desktop | ✅ |
| P2.10.1 UTM | Simulator-Quellen mit sauberen UTMs, Kampagnennamen passend zur Blaupause | ✅ |
| P2.11–P2.11.2 Consent Mode V2 | eigener Banner mit Default/Update (Weg 2), umschaltbar auf Cookiebot (Weg 1), 72/18/10 % Zustimmung/Ablehnung/ignoriert im Simulator | ✅ |
| P2.12 Erste Daten lesen | Realistischer Kanal-Mix aus 11 Quellen | ✅ |

## Phase 3 – Optimieren + pMax
| Video | Auf der Seite | |
|---|---|---|
| P3.5 Qualitätsfaktor / Landingpage | Leistungsseiten passend zur Anzeigengruppe vs. Startseite als Negativbeispiel | ✅ |
| P3.7 pMax Asset-Gruppe | `ads-assets/` in allen Formaten, Kauf-Conversion mit Wert aus dem Shop | ✅ |
| P3.9 Search + pMax | Brand-Kampagne `suche_marke` vs. `pmax_shop` im Simulator getrennt | ✅ |
| P3.10 GA4 Akquisition/Engagement | Unterschiedliche Lesetiefe, Absprünge, mehrseitige Besuche | ✅ |

## Phase 4 – Zielgruppen, Retargeting
| Video | Auf der Seite | |
|---|---|---|
| P4.3 Scroll, Formulare, Klicks | lange Seiten, Formular-Start ohne Absenden, CTAs | ✅ |
| P4.4 Erste Zielgruppe | Besucher bestimmter Seiten (`leistung = kuechen`) | ✅ |
| P4.5 Zielgruppen nach Verhalten | Anfrage begonnen/abgebrochen, tiefes Scrollen, 3+ Seiten, Konvertierte ausschließen, **Bewerber ausschließen** | ✅ |
| P4.6–P4.12 Display, Demand Gen, RLSA, 3 Stufen | Zielgruppen-Stufen: Absprung → Leistungsseite → Anfrage begonnen | ✅ (Aufbau) |

## Phase 5 – Tief verstehen
| Video | Auf der Seite | |
|---|---|---|
| P5.2 Trichter | Start → Leistung → Anfrage Schritt 1/2/3 → Danke; Shop: Liste → Produkt → Warenkorb → Kasse → Kauf | ✅ |
| P5.3 Pfadanalyse | Reise `mehrseiten_tour`, Einstiege auf verschiedenen Seiten, Sackgasse 404 | ✅ |
| P5.4 Freies Format | Landingpages × Conversion-Rate, Inhaltsgruppen | ✅ |
| P5.5 / P5.12 Conversion-Pfade, Attribution | Wiederkehrende Besucher (bis 12 Stammbesucher) mit wechselnden Quellen | ◐ (Simulator, kleine Fallzahlen) |
| P5.6 Scroll- und Video-Tracking | YouTube mit `enablejsapi=1` auf `/ueber-uns/` | ✅ |
| P5.8 Smart Bidding / Ziel-ROAS | echte Warenkorbwerte aus dem Shop | ✅ |
| P5.10 Debugging | 7 bewusste Übungsfallen, siehe Tracking-Plan Abschnitt 4 | ✅ |
| P5.11 Custom Dimensions | `seitentyp`, `leistung`, Kundentyp (Neu-/Bestandskunde im Kontaktformular), Kundentyp Privat/Gewerbe in der Anfrage | ✅ |
| P5.13 Predictive Audiences | braucht in GA4 viele Käufe (Mindestzahlen) – Simulatorvolumen reicht dafür voraussichtlich nicht | ◐ |
| GTM Expert: Enhanced Conversions | E-Mail/Telefon-Felder mit stabilen IDs | ✅ |

## Phase 6 – Looker Studio
| Video | Datenbasis | |
|---|---|---|
| P6.3–P6.4 GA4-Quelle, Diagramme | Kanal-Mix, Seiten, Inhaltsgruppen, Geräte | ✅ |
| P6.5 / P6.9 Google Ads + Blending | Keine echten Ads-Kosten (Kampagnen nicht live). Alternative: Kosten als Google-Sheet je `utm_campaign` und Tag, per Blending mit GA4 verbinden | ◐ |
| P6.8 Berechnete Felder | CASE auf `inhaltsgruppe` / Quelle (z. B. „Recruiting“ vs. „Kunden“), Conversion-Rate | ✅ |
| P6.10 Search Console | wegen `noindex` kaum Daten | ◐ |

## Bewusst nicht abgedeckt
- **Echte Google-Ads-Daten** (Klicks, Kosten, Suchbegriffe, `gclid`): nur mit live geschalteten Anzeigen, hier nicht vorgesehen.
- **Organische Suche**: Die Seite ist `noindex`.
- **Cross-Domain und Server-Side-Tagging**: waren als optionale Punkte zurückgestellt.
