# CAM Edilizia 2025 — Strategische Analyse für Sovereign AEC

**Quelldokument:** `cam_edilizia_11_25.pdf` (123 Seiten, Italienisch, MASE-Ministerium, registriert 25.11.2025 unter Nr. 0221911.25-11-2025)

**Vollständiger Titel:** „Criteri Ambientali Minimi per l'affidamento del servizio di progettazione e direzione lavori di interventi edilizi e opere di ingegneria civile, esecuzione di lavori, inclusi gli interventi di costruzione, ristrutturazione, manutenzione e adeguamento"

**Status:** verpflichtend für alle italienischen öffentlichen Bauaufträge (Stazioni Appaltanti, Concessionari, private Bauträger mit Erschließungsverpflichtung). Rechtsbasis: Codice dei Contratti Pubblici (D.Lgs. 36/2023) Art. 57 Abs. 2 + Correttivo (D.Lgs. 209/2024).

---

## Executive Summary

CAM Edilizia 2025 ist der **stärkste regulatorische Rückenwind**, den wir bisher gesehen haben. Italien zwingt mit dieser Pflicht-Richtlinie für öffentliche Bauvergabe genau jene Praktiken in den Markt, die der Sovereign-AEC-Stack technisch unterstützt:

- BIM-Modelle mit eingebetteten Umwelt-/Materialdaten als Pflicht (Sektion 2.1.3)
- Lebenszyklus-Doku (Manutenzione + Decostruzione) im BIM-Format archiviert (Sektion 2.3.16, 2.3.17)
- Material-Pässe für Wiederverwendung/Recycling, 70-%-Reuse-Ziel (Sektion 2.3.17)
- LCA/LCC nach EN 15804 / EN 15978 / EN 16627 obligatorisch (Sektion 1.3.2, 2.6.3, 3.2.4)
- EPD-Referenzen pro Bauprodukt (mehrfach durchgängig)
- Level(s)-Framework als Default-Reporting (Sektion 1.3.2)

Anders gesagt: was unser **Gebäudebuch-Generator**, **PDT-NIP** (Product Data Templates) und **Material-Pass-Markt** liefern, ist ab sofort **gesetzliche Pflicht** für die italienische öffentliche Hand. Provinz Bozen muss CAM Edilizia anwenden, oder ihre Vergaben sind angreifbar.

---

## 1. BIM-Pflicht erweitert um Umweltdaten (Sektion 2.1.3)

Wortlaut Sektion 2.1.3:

> Il progettista aggiudicatario, qualora il progetto ricada nell'applicazione del comma 1 o del comma 2 dell'art. 43 del Codice dei Contratti, implementa la base dati del BIM comprensiva delle informazioni ambientali relative alle specifiche tecniche di cui al capitolo „2 Criteri per l'affidamento del servizio di progettazione di interventi edilizi".

Auf Deutsch:

- Wo Art. 43 D.Lgs. 36/2023 BIM verlangt (also bei allen öffentlichen Bauaufträgen ≥ 2 Mio. €), muss das BIM-Modell **alle Umwelt-/Materialdaten** der CAM-Spezifikationen enthalten.
- Bezug auf **EU-Verordnung 2486/2023** zu Taxonomie-Vaglio-Kriterien für „Übergang zur Kreislaufwirtschaft".
- Materialien und Komponenten müssen **für künftige Wartung, Wiederverwendung und Recycling** im BIM hinterlegt werden.
- Explizite Empfehlung: **EN ISO 22057:2022** für Environmental Product Declarations (EPD) im BIM-Modell.

**Verifizierungs-Mechanismus:** der Planer macht in seinem Angebot einen Vorschlag zur „gestione informativa" mit Umwelt-Spezifikationen. Nach Genehmigung durch Stazione Appaltante wird das in den **Piano di Gestione Informativa** (= BEP nach UNI 11337) konsolidiert.

**Mapping auf Sovereign AEC:**

| CAM-Anforderung | Sovereign-AEC-Konstrukt |
|---|---|
| BIM mit Umweltdaten je Bauteil | IFC-Property-Sets verknüpft mit bSDD-URIs, eingebettet in `kind:30904` |
| Material-/Komponenten-Pässe | `kind:30850` Product Data Template, Hersteller-npub signiert |
| EPD-Anbindung nach EN ISO 22057 | EPD-Hash + URL als Tag im Material-Pass-Event |
| Gestione informativa als Vertrags-Anhang | `kind:30880` PIR + `kind:30810` IDS mit CAM-Anforderungen als prüfbares Spec |

---

## 2. Lifecycle-Doku im BIM-Format (Sektion 2.3.16)

Wortlaut:

> Ai fini della gestione informativa digitale delle costruzioni in accordo con quanto previsto dall'art. 43 del Codice, l'archiviazione della documentazione tecnica riguardante l'edificio dovrebbe essere resa nella sua rappresentazione BIM, in modo da garantire adeguata interoperabilità in linea con i formati digitali IFC (Industry Foundation Classes) necessari allo scambio dei dati e delle informazioni relative alla rappresentazione digitale del fabbricato.

Auf Deutsch:

- Manutenzione-Plan (Wartungsplan) **muss im BIM archiviert werden**, im IFC-Format.
- Damit ist die digitale Bauwerksdokumentation gesetzlich verbindlich an IFC gekoppelt — nicht an proprietäre Plattformformate.
- Wartungsplan-Inhalte (Manuale d'uso, Manuale di manutenzione, Programma di manutenzione, Prestazions-Monitoring, Grünflächen-Pflegeplan, Radon-Monitoring) müssen mit IFC-Bauteil-GUIDs verknüpft sein.

**Mapping auf Sovereign AEC:**

- Direkter Andock an unseren **Gebäudebuch-Generator** — das Kapitel „Wartung" füllt sich automatisch aus den Property-Sets der jeweiligen Bauteile.
- IFC-File-Reference (`kind:30904`) trägt eine `iso19650-state`-Tag-Erweiterung um „Archiviato-CAM" (= autoritativer Wartungs-Stand).
- Maintenance-Cycle-Events als eigener Event-Typ — siehe Vorschlag in `kind:30962` weiter unten.

---

## 3. Decostruzione-Plan — neuer Pflichtbestandteil (Sektion 2.3.17)

Das ist die wichtigste Neuerung der 2025er-Version und passt perfekt zu unserem Material-Pass-/Gebäudebuch-Konzept.

### Pflichten

- Plan für selektive Dekonstruktion und Demolition am Lebensende der Bauwerks.
- **Mindestens 70 %** (Gewicht) der Bauteile müssen wiederverwendbar oder selektiv recyclierbar sein (außer technischen Anlagen). Rechtsbasis: Art. 181 Abs. 4 lit. b D.Lgs. 152/2006.
- Plan basiert auf Reference Study Period (RSP) aus LCA-LCC-Studie.
- Strukturiert nach **UNI PdR 75** „Decostruzione selettiva — Metodologia per la decostruzione selettiva e il recupero dei rifiuti in un'ottica di economia circolare".
- Terminologie nach **UNI 8290-1** für Bauwerksteile.

### Inhalte des Plans

- Bewertung der Bauwerks-Eigenschaften
- Recycling-Ziele pro Komponente nach Kategorie:
  - destinate al **riuso** (Wiederverwendung)
  - destinate al **riciclo** (Recycling)
  - destinate ad **altra forma di recupero** (z. B. energetische Verwertung)
  - destinate a **smaltimento** (Entsorgung)
- Empfehlungen zu Abbau- und Demolition-Technologien
- Risikobewertung gefährlicher Abfälle
- Quantitative Schätzung der Abfallfraktionen

**Mapping auf Sovereign AEC:**

| CAM-Decostruzione-Anforderung | Sovereign-AEC-Konstrukt |
|---|---|
| Bauteil-Liste mit Wiederverwendungs-Kategorie | `kind:30850` Product Data Template mit Tags `reuse-class`, `recycle-class`, `dismount-method` |
| 70%-Reuse-Ziel als Vertrags-Klausel | IDS-Spezifikation (`kind:30810`) mit CAM-Validation-Regel, automatisch prüfbar |
| Plan als Vertrags-Anhang | Eigener Event-Kind `kind:30970` Approval, der den finalen Decostruzione-Plan attestiert |
| UNI-PdR-75-Konformität | bSDD-URI-Referenz im PDT, dann automatisch tooling-übergreifend lesbar |

**Geschäftsmöglichkeit:** der Decostruzione-Plan muss von einem qualifizierten Planer geschrieben werden — das ist genau die Sorte Dienstleistung, die als **DVM** auf unserer Plattform angeboten werden kann (analog zur Bedarfsplanung-DVM-Idee aus `SEC-YOLO-BIM_IDEA-collection`).

---

## 4. LCA / LCC (Sektion 1.3.2 + 2.6.3 + 3.2.4)

### Anforderung

LCA-Studie nach **EN 15978** (Gebäude) und **EN 15804** (Produkte). LCC-Studie nach **EN 16627**.

Verpflichtende Indikatoren:

- Alle Indikatoren der EN 15804
- Mindestens drei zusätzliche Indikatoren aus Tabelle 8 EN 15978
- Mindestens einer davon: Klimawirkung (Global Warming Potential)

Die LCA muss in der **Relazione di sostenibilità dell'opera** (Art. 11 Allegato I.7 D.Lgs. 36/2023) dokumentiert werden.

### Level(s) als Default-Framework

CAM Edilizia 2025 verweist mehrfach auf **Level(s)** — das EU-Rahmenwerk für Nachhaltigkeits-Indikatoren von Büro- und Wohnbauten. Level(s) ist freiwillig, aber CAM macht es de facto zum Default-Reporting-Schema.

**Mapping auf Sovereign AEC:**

- LCA/LCC-Reports als `kind:30903` Document Reference, gehasht und signiert
- Reference Study Period (RSP) als Tag im Project-Event
- Level(s)-Indikatoren als strukturierte `kind:1190` Sustainability Indicator Events (neu vorgeschlagen)
- EPDs pro Material als `kind:30903` mit Hash + URL zur akkreditierten EPD-Datenbank (EcoPlatform o. ä.)

---

## 5. EPDs als durchgängige Anforderung

Environmental Product Declarations werden in zahlreichen Sektionen verlangt:

- Sektion 2.4.* — alle Bauprodukte (Beton, Stahl, Ziegel, Holz, Dämmstoffe, Trennwände, Mauerwerk, Bodenbeläge, Fliesen, Fenster, Rohrleitungen, Farben, Sanitär, Verglasung)
- Sektion 3.2.7 — Premium-Kriterium für ökologisch verbesserte Materialien

**Konsequenz für Hersteller:** ohne EPD nach EN 15804 + EN ISO 14025 + ggf. PCR (Product Category Rules) sind sie aus öffentlichen Bauvergaben raus.

**Mapping auf Sovereign AEC:**

- EPD wird zum Pflichtfeld in `kind:30850` Product Data Template
- Hersteller-npub kann seine EPDs signiert publishen → automatisch in PDT-Events verlinkt
- Validation-DVM (`kind:5901`/`kind:6901`) prüft EPD-Vorhandensein und -Aktualität im IFC-Modell

---

## 6. Zentrale Geschäftsmöglichkeiten

| Marktchance | Sovereign-AEC-Andock |
|---|---|
| Decostruzione-Plan-Erstellung als Beratungsdienst | PlanDVM `kind:5310` für Decostruzione, Reputations-Badge per NIP-58 |
| EPD-Aggregation und -Verifikation | EPD-Mirror-Aggregator (analog Vergabe-Mirror, signiert publishen) |
| Material-Pass-Marktplatz für Re-Use | PDT-NIP + Plebeian-Style Marktplatz mit Lightning-Settlement |
| LCA/LCC-Reporting-Tool | Auto-Generator aus Nostr-Events analog Gebäudebuch-Generator |
| CAM-Konformitäts-Validierung als DVM | IDS-basierter Compliance-Check pro Projektphase |
| Wartungsplan-Aggregation | Gebäudebuch-Generator Kapitel „Wartung" |
| Stazione-Appaltante-Beratung zu CAM | DVM-Marktplatz für Bauherrenberatung mit CAM-Spezialisierung |

---

## 7. Neue Event-Kinds, die wir reservieren sollten

Auf Basis dieser CAM-Analyse:

| Kind | Zweck | Trigger |
|---|---|---|
| `kind:30940` | LCA-Studie Reference | Sektion 1.3.2 |
| `kind:30941` | LCC-Studie Reference | Sektion 1.3.2 |
| `kind:30942` | Level(s)-Indikator-Set | Sektion 1.3.2 |
| `kind:30962` | Wartungs-Cycle / Maintenance Event | Sektion 2.3.16 |
| `kind:30971` | Decostruzione-Plan Approval | Sektion 2.3.17 |
| `kind:1190` | Sustainability Indicator Snapshot (immutabel, point-in-time) | Level(s)-Reporting |

Alle parameterized replaceable wo Sinn macht, immutabel wo Point-in-Time wichtig ist. Genau Wertebereiche in `STANDARDS-PROFILE.md` und `KIND-REGISTRY.md` aufnehmen sobald der erste Pilot-Test sie validiert hat.

---

## 8. Schlüssel-Zitate aus dem Dokument

### Premessa, Abs. 4 (S. 5)

> L'applicazione delle specifiche tecniche e delle clausole contrattuali è obbligatoria ai sensi dell'articolo 57 comma 2 del Codice.

Übersetzung: technische Spezifikationen und Vertragsklauseln sind verpflichtend.

### Sektion 2.1.3 — BIM mit Umweltdaten

> Il modello BIM dovrà implementare i materiali e i componenti utilizzati, ai fini della manutenzione, del recupero e del riutilizzo futuri, ad esempio applicando la norma EN ISO 22057:2022 per fornire dichiarazioni ambientali di prodotto.

Übersetzung: BIM-Modell muss Materialien und Komponenten für Wartung, Recovery und Reuse implementieren, z. B. mit EN ISO 22057:2022 für EPDs.

### Sektion 2.3.16 — Lifecycle-Doku im BIM

> L'archiviazione della documentazione tecnica riguardante l'edificio dovrebbe essere resa nella sua rappresentazione BIM, in modo da garantire adeguata interoperabilità in linea con i formati digitali IFC.

Übersetzung: technische Dokumentation soll im BIM, IFC-konform, archiviert werden.

### Sektion 2.3.17 — 70-%-Reuse-Ziel

> Almeno il 70% peso/peso dei componenti edilizi e degli elementi utilizzati nel progetto, esclusi gli impianti, … sia riutilizzabile direttamente o sottoponibile, a fine vita, a disassemblaggio, smontaggio, decostruzione, demolizione selettiva.

Übersetzung: mindestens 70 % Gewicht der Bauteile (ohne Anlagen) müssen direkt wiederverwendbar oder selektiv recyclierbar sein.

---

## 9. Implikationen für Sovereign AEC

### Pilot-Strategie

- **Raulassen wird CAM-Konformitäts-Test.** Wenn der Pilot zeigen kann, dass Sovereign-AEC-Workflows die CAM-Sektionen 2.1.3, 2.3.16, 2.3.17 automatisch erfüllen, ist das die stärkste Pitch-Story für die Provinz Bozen, die wir uns wünschen können.
- Decostruzione-Plan als ein konkreter Demo-Output des Gebäudebuch-Generators v1.
- LCA-Indikatoren als Pflichtfelder in unseren PDT-Events.

### Standards-Profil

- `docs/STANDARDS-PROFILE.md` muss um Sektion „CAM Edilizia 2025" erweitert werden — Bezug auf EN 15804, EN 15978, EN 16627, EN ISO 22057, UNI PdR 75, UNI 8290-1, Level(s).
- `docs/KIND-REGISTRY.md` muss um die neuen Kinds (30940, 30941, 30942, 30962, 30971, 1190) erweitert werden, sobald die ersten Pilot-Tests sie validiert haben.

### Wiki-Roadmap

Neue Wiki-Seiten mit hoher Priorität:

- `wiki/regional/it-uni-11337.html` — kombiniert UNI 11337 + CAM Edilizia 2025 + DM 312/2021
- `wiki/lifecycle/lca-lcc.html` — EN 15804/15978/16627 erklärt
- `wiki/lifecycle/decostruzione.html` — UNI PdR 75 und 70-%-Reuse-Ziel
- `wiki/lifecycle/epd.html` — Environmental Product Declarations und ihre Rolle

### Pitch-Verdichtung

Vor CAM Edilizia 2025: „Sovereign AEC kann Gebäudebücher generieren, das wäre nice-to-have."

Nach CAM Edilizia 2025: „Sovereign AEC ist die einfachste Compliance-Maschine für CAM-Pflicht-Anforderungen in italienischer öffentlicher Bauvergabe. Wer Raulassen pilotiert, erfüllt Sektionen 2.1.3, 2.3.16, 2.3.17 automatisch."

Das ist eine andere Tonlage.

---

## 10. Offene Punkte

1. **Welche EPD-Datenbanken sind akkreditiert in Italien?** EcoPlatform, EPD-Italy, weitere? Recherche steht aus.
2. **UNI PdR 75 im Volltext.** Wir brauchen die genaue Decostruzione-Methodologie für unseren Tool-Adapter.
3. **UNI 8290-1 Terminologie.** Die Bauwerksteile-Liste muss in bSDD-URI-Mapping übersetzt werden.
4. **EN ISO 22057:2022 in BIM.** Wie genau wird die EPD-Information in IFC-Property-Sets verankert? Mapping-Studie nötig.
5. **Level(s)-Indikatoren.** Liste der Kern-Indikatoren in `wiki/lifecycle/lca-lcc.html` ausarbeiten.
6. **Verhältnis zu CAM Strade** (D.M. 5 August 2024, GU n. 197 vom 23.08.2024). CAM Strade gilt für Straßeninfrastruktur — für Brücken, Tunnel u. ä. ergänzend. Eventuell zweiter Compliance-Pfad nötig.

---

## 11. Konkrete nächste Aktionen

1. **`docs/STANDARDS-PROFILE.md`** um CAM-Edilizia-Sektion erweitern (LCA-Normen, EPD-Pflicht, Decostruzione-Anforderung).
2. **`docs/KIND-REGISTRY.md`** um Reserve-Tags für CAM-konforme Property-Erweiterungen (`reuse-class`, `recycle-class`, `dismount-method`, `epd-uri`, `epd-valid-until`).
3. **`docs/gebaeudebuch-generator-scope.md`** um neues Kapitel „Decostruzione-Plan" (Anhang automatisch generierbar aus Material-Pass-Events).
4. **`web/wiki/regional/it-uni-11337.html`** schreiben — kombinierte Italien-Wiki-Seite mit UNI 11337 + CAM Edilizia 2025.
5. **Pitch-Material aktualisieren** — CAM Edilizia 2025 als regulatorischer Anker für Provinz-Bozen-Gespräch.

---

*Stand: Mai 2026. Lebendes Dokument. Bei Updates der CAM durch Decreto Correttivo oder ergänzende Allegati hier nachziehen.*
