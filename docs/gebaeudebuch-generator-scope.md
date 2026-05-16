# Gebäudebuch-Generator — Scope

**Premisse.** Sobald die Projektdaten als signierte Nostr-Events vorliegen, ist das Gebäudebuch keine Schreibarbeit mehr, sondern eine Filter-Abfrage plus Template. Ein HTML-Prototyp reicht für den Demo-Climax des Sprints, und der reale Markt steht hinter Tür drei: EU-EPBD-Recast, Digital Product Passport, AT-Bauwerksbuch.

---

## Was ein Gebäudebuch ist

Lebenslange strukturierte Dokumentation eines Bauwerks: Stammdaten, Modelle, Materialien, Bauphase, Anlagen, Energiedaten, Wartung, Beteiligte. Synonyme: Bauwerksbuch (AT), Gebäudedokumentation (DE), Building Logbook (EU), Fascicolo del Fabbricato (IT, regional).

Regulatorische Hooks 2026–2027:

- **EU-EPBD-Recast (Richtlinie 2024/1275), Artikel 19** — Building Renovation Passport + Building Logbook werden Pflicht.
- **EU-ESPR (Verordnung 2024/1781)** — Digital Product Passport für Bauprodukte ab 2027.
- **AT-Bauwerksbuch** — verpflichtend für bestimmte Bauwerksklassen.
- **DGNB / ÖGNI / KlimaAktiv** — Zertifizierungen brauchen umfassende Materialdoku.

Heute wird das manuell zusammengeklöppelt. 2 – 4 Wochen Schreibarbeit am Projektende, durch verschiedene Plattformen. Mit signierten Events: ein Knopfdruck plus Review.

---

## Scope v1 (in den SE-Sprint einbaubar)

**Form.** Eine HTML-Datei. Input: Projekt-naddr. Output: druckbares HTML-Gebäudebuch („Drucken → als PDF speichern" reicht für v1).

**Sechs Kapitel:**

1. **Stammdaten** — Projekt-Name, Adresse, Eigentümer-npub, Planungs-Team mit Rollen-Badges, Projektzeitraum.
2. **Modelle und Pläne** — Liste aller `kind:30904` IFC-File-Refs (Architektur, Tragwerk, MEP) mit Hash + OTS-Beweis, plus `kind:30903` Document-Refs für Pläne und Berichte.
3. **Materialien und Komponenten (Material Passport)** — Tabelle aller `kind:30850` PDTs, sortiert nach Domäne, mit Hersteller-npub, Produkt, Menge, optional Rezyklat-Anteil und Demontierbarkeit.
4. **Bauphase** — Aggregat aus `kind:30960` Bautagebuch (Zeitstrahl mit Highlights) plus Koordinationshistorie aus `kind:30900` / `kind:1170` / `kind:1171` (Anzahl Topics, Lösungsrate, Top-3-Konflikte).
5. **Beteiligte und Audit** — vollständige npub-Liste mit Rollen, kryptographisch verifizierbar. Auflistung der Approval-Multi-Sigs (`kind:30970`).
6. **Anhang — Event-Index** — naddr-Liste aller Quell-Events, gruppiert nach Kategorie. Damit ist jeder Satz im Bericht auf das Quell-Event zurückführbar.

**Aus v1 draußen:**

- Tiefes Anlagen-Kapitel (Phase 2, braucht IFC-MEP-Parsing)
- Energiekennwerte (Phase 2, braucht IDS-validierte Berechnung oder Telemetrie aus `kind:1230`)
- Wartungsplan (Phase 3, braucht PDT-Wartungs-Metadaten)
- LLM-Narrative (Phase 2 — v1 ist pure Templating)
- DOCX-Export (Phase 2 — v1 ist HTML/PDF)

---

## Architektur (v1)

```
Project naddr (Input)
       │
       v
Nostr-Subscribe via NDK
   filter: { "#a": ["30902:<owner>:<project-guid>"] }
       │
       v
Categorize by kind:
   30902 → Stammdaten
   30904 → Modelle
   30903 → Dokumente
   30850 → Materialien
   30960 → Bautagebuch
   30900 + 1170 + 1171 → Koordination
   30970 → Approvals
   30000 + 30009 → Beteiligte
       │
       v
Render in HTML-Template (Vanilla, CSS-Print-Styles)
       │
       v
gebaeudebuch.html → "Drucken als PDF"
       │
       v
(Optional) kind:30930 Document Record publishen
       e-Tags = alle Quell-Events
       x-Tag  = sha256 des erzeugten PDF
       ots-Tag = OpenTimestamps-Anker
```

**Stack.** Vanilla JS + NDK + ein Print-Stylesheet. Keine Server-Komponente. Kein LLM. Single HTML-Datei. Deploy auf Cloudflare Pages.

---

## Integration in den 6-Wochen-Sprint

**Option A — als W6-Hauptdeliverable.** Polish reduziert sich auf einen halben Tag, der Rest von W6 ist Gebäudebuch-Gen. Das gibt den stärksten Pitch-Climax: in der Demo werden vor den Augen des Publikums die fünf vorigen Prototypen verbraucht, um ein echtes Dokument zu erzeugen.

**Option B — als 7. Prototyp neben W6 polish.** Sauberer, aber Sprint sprengt 6 Wochen leicht.

**Empfehlung.** Option A. Polish kann in W6 nebenher passieren, weil der Generator selbst der Polish-Output ist — er ist das integrierte Showpiece für alle anderen Prototypen.

---

## Phasen-Ausbau

| Version | Inhalt | Aufwand |
|---|---|---|
| v1 (SE-W6) | HTML-Prototyp, 6 Kapitel, pure Templating | 1 Woche |
| v2 (Phase 2) | LLM-Narrative (lokal Ollama), DOCX-Export, vollständige Kapitelstruktur, kind:30930 Audit-Publish | 4–6 Wochen |
| v3 (Phase 3) | Live-Update im Betrieb (Telemetrie), Wartungsplan-Tracking, automatische DPP-Konformitätsprüfung | offen |

---

## Synergien

- **W2/W3 BCF-Prototypen** liefern Koordinations-Daten direkt.
- **W4 OTS-Bautagebuch** liefert Bauphase-Daten direkt.
- **W5 plebbim** liefert Bounty-Historie (nice-to-have im Bauphase-Kapitel: „bei welchen Issues hat der Bauherr nachgeholfen").
- **AdlerHort** indexiert historische Gebäudebücher als Templates, schlägt Texte vor.
- **AI-Report-Pipeline** ist v2 dieses Generators.
- **USD-Baukasten** wird v3-Quelle für Geometrie-Kapitel.

---

## Pitch-Vergleich

| Klassisch | Mit Generator |
|---|---|
| 2–4 Wochen Schreibarbeit | Ein Klick |
| Daten aus 5 Plattformen zusammenklauben | Aus dem Event-Stream gezogen |
| Keine Provenance | Jeder Satz auf signiertes Event zurückführbar |
| PDF im Ordner | naddr-Bundle, abonnierbar, lebend |
| Plattform-Tod = Doku-Verlust | Relays sind austauschbar, Inhalt bleibt |

---

## Offene Entscheidungen

1. **W6 als Generator oder als 7. Prototyp?** Empfehlung A.
2. **Sprache des Outputs.** DE-only, DE/IT bilingual (Südtirol-relevant), oder konfigurierbar via Profil?
3. **Template-Look.** Minimalistisch und modern, oder Behörden-formfertig (AT-Bauwerksbuch-Layout)? Empfehlung: minimalistisch v1, Behördenform v2 als zusätzliches Template.
4. **Genaue Kind-Allokation für `kind:30970` Approval** — eigene NIP oder als Erweiterung des BCF-NIP-Drafts?
5. **OTS-Anker für das Gebäudebuch selbst** standardmäßig oder optional? Empfehlung: standardmäßig, das ist der ganze Witz.
6. **Demo-Datensatz.** Wir seeden eine fiktive Tribe „Pauliplatz 7" mit dem Markus-Alice-Bob-Sarah-Heidi-Datensatz aus dem vorigen Schema-Entwurf?

---

*Lebendes Scope-Dokument. Stand: Mai 2026. v1 ist klein genug, dass es nicht scheitern kann; v2 ist groß genug, dass es ein eigenes Produkt wird.*
