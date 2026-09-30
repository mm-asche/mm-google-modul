# Google-Ads-Kampagnen-Blaupause – Holzwerk Hanssen

> **Nur zum Zeigen, nicht veröffentlichen.** Die Kampagnen werden im Kurs aufgebaut, bleiben aber pausiert bzw. im Entwurf. Holzwerk Hanssen ist fiktiv – live geschaltete Anzeigen würden gegen die Google-Richtlinie zu falschen Angaben verstoßen. Paid-Traffic in GA4 kommt ausschließlich vom Simulator (UTM `google/cpc`).
>
> Tipp für die Aufnahme: Kampagnen im Schritt „Veröffentlichen“ nicht abschließen, sondern als Entwurf speichern, oder nach dem Anlegen sofort pausieren. Keine Zahlungsmethode für Live-Schaltung nötig, wenn nur im Entwurf gearbeitet wird (vor der Aufnahme im eigenen Konto prüfen).

Die Kampagnennamen stimmen mit den `utm_campaign`-Werten des Simulators überein. Dadurch passen Ads-Aufbau und GA4-Berichte im Kurs zusammen.

---

## Kampagne 1: `suche_leistungen` (Suche, P1.6–P1.9)
- **Ziel:** Leads · **Standorte:** Standortliste „Einsatzgebiet Hanssen“ (P1.6.1): Hamburg + 40 km, Norderstedt, Ahrensburg
- **Sprache:** Deutsch · **Budget:** 15 €/Tag (≈ 450 €/Monat) · **Gebote:** zuerst „Klicks maximieren“, später „Conversions maximieren“

| Anzeigengruppe | Finale URL | Keywords (Beispiele) |
|---|---|---|
| Küchen | `/leistungen/kuechen-nach-mass/` | [küche nach maß hamburg], "tischler küche", "maßküche hamburg", "küche vom tischler" |
| Einbauschränke | `/leistungen/einbauschraenke/` | [einbauschrank nach maß], "einbauschrank dachschräge", "schrank nach maß hamburg" |
| Treppen | `/leistungen/treppen/` | "holztreppe hamburg", "treppe renovieren", [treppenrenovierung hamburg] |
| Innentüren | `/leistungen/innentueren/` | "innentüren einbauen hamburg", "innentüren mit montage", "zimmertüren tischler" |

**Ausschlusskeywords (Liste „Hanssen Basis“, P3.3):** ikea, gebraucht, ebay, kleinanzeigen, selber bauen, diy, anleitung, ausbildung, gehalt, job, stellenangebot, kostenlos, bauhaus, obi, hornbach

**RSA-Beispiel Küchen (P1.8)**
- Headlines (Auswahl, ≤ 30 Zeichen): Küche nach Maß in Hamburg · Ihre Küche vom Tischler · Kostenloses Aufmaß vor Ort · Festpreis in 10 Werktagen · Eigene Werkstatt seit 1987 · Montage durch eigenes Team · Maßküchen ohne Blenden · Jetzt Beratung anfragen
- Beschreibungen (≤ 90 Zeichen):
  - Maßküchen aus unserer Werkstatt in Hamburg. Kostenloses Aufmaß und 3D-Planung.
  - Keine Standardraster: Wir planen jeden Zentimeter. Jetzt unverbindlich anfragen.

**Anzeigen-Assets (P1.9)**
- Sitelinks: Küchen nach Maß · Einbauschränke · Ratgeber Küchenkosten (`/ratgeber/kuechen-kosten/`) · Kontakt
- Callouts: Kostenloses Aufmaß · Eigene Montage · Seit 1987 · 5 Jahre Gewährleistung
- Anruf-Asset: 040 66969 100 (Film-/Fernsehnummer der Bundesnetzagentur, erreicht niemanden)
- Snippets „Leistungen“: Küchen, Einbauschränke, Treppen, Innentüren

## Kampagne 2: `suche_marke` (Brand-Schutz, P3.9)
- Anzeigengruppe „Marke“: [holzwerk hanssen], "hanssen tischlerei" → Finale URL `/`
- Budget klein (3 €/Tag), eigene Kampagne, damit pMax nicht die Markensuchen übernimmt

## Kampagne 3: `pmax_shop` (Performance Max, P3.6–P3.8)
- **Ziel:** Umsatz · Conversion „Kauf“ (Wert aus `purchase`) · Gebot „Conversion-Wert maximieren“, später Ziel-ROAS
- **Asset-Gruppe „Holzpflege“** – Finale URL `/shop/`, URL-Erweiterung aus, nur `/shop/*`
  - Bilder: `ads-assets/` (Querformat 1,91:1, Quadrat 1:1, Hochformat 4:5), Logo quadratisch und 4:1
  - Headlines: Holzpflege vom Tischler · Hartwachs-Öl für Massivholz · Pflege-Set als Geschenk
  - Lange Headline: Die Pflegeprodukte, die wir selbst in der Werkstatt verwenden
  - Beschreibungen: Versandkostenfrei ab 49 €. Abholung in Hamburg-Bahrenfeld möglich.
  - Video: YouTube-Kanal verknüpfen (P3.7), ohne eigenes Video erstellt Google eins (im Kurs erwähnen)
- **Zielgruppensignal:** GA4-Zielgruppe „Warenkorb ohne Kauf“, Suchbegriffe „möbelöl“, „holzpflege“, „arbeitsplatte ölen“

## Kampagne 4: `retargeting_display` (Display, P4.6–P4.7)
- Zielgruppe: „Anfrage begonnen, nicht abgeschickt“ + „Leistungsseite 2+ Seiten“, Ausschluss: „Konvertierte 30 Tage“, „Karriere-Besucher“
- Responsive Display-Anzeige mit Bildern aus `ads-assets/`, Botschaft: „Ihr Aufmaß ist kostenlos – jetzt Termin sichern“
- Frequency Capping: 3 pro Tag

## Kampagne 5: `demand_gen_kuechen` (Demand Gen, P4.8–P4.10)
- Assets aus pMax wiederverwenden (Rückbezug P4.9), Zielgruppe GA4 „Küchenseiten gesehen“ + Lookalike
- Ziel: Klicks auf `/ratgeber/kuechen-kosten/` (Whitepaper als Einstieg für kalte Zielgruppen)

## RLSA (P4.11)
- In `suche_leistungen` Zielgruppe „Alle Besucher 30 Tage“ auf **Beobachtung**, Gebotsanpassung +30 %

## Recruiting (Abgrenzung)
- Keine Google-Ads-Kampagne im Kurs, aber Simulator-Quellen `indeed/jobs` und `instagram/paid_social` mit `recruiting_*`
- Zeigt in GA4 und Looker Studio, warum Recruiting-Traffic getrennt ausgewertet werden muss

---

## Conversion-Aktionen in Google Ads (P2.8, P2.10)
| Name | Quelle | Primär? | Wert |
|---|---|---|---|
| Lead – Projektanfrage | GTM (Danke-Seite) oder GA4-Import `generate_lead` | ja | kein fester Wert (optional: Wert per Leistung in einem späteren Video diskutieren) |
| Lead – Anruf-Klick | GTM `tel:`-Klick | ja | – |
| Lead – Rückruf | GTM Listener-Ereignis | ja | – |
| Kauf | GTM `purchase` | ja (nur pMax Shop) | dynamisch `ecommerce.value` |
| Whitepaper | GA4-Import | nein (sekundär) | – |
| Bewerbung | – | **nicht importieren** | – |
