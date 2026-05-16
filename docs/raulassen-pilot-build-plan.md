# Raulassen Pilot — Build Plan

**Premisse.** Wir haben echte IFCs von Revit, ArchiCAD und Allplan eines komplettierten Projekts. Damit lässt sich der gesamte Sovereign-AEC-Stack mit Realdaten instrumentieren — kein Demo-Mock, sondern Projekt-Replay. Die Multi-Tool-Konstellation ist nicht Komplikation, sondern das wertvollste Demo-Asset: openBIM-Interoperabilität, das buildingSMART seit zwanzig Jahren verspricht, gelebt in einem signierten Workflow.

**Spirit.** First running, then standardized. Bestehende Nostr-Kinds + eigene 30xxx-Range. NIP-PRs erst, wenn das Schema sich in der Praxis bewährt hat.

---

## Phase 0 — Foundation (Tag 1–5)

### Datenkatalog
Inventur aller Raulassen-IFCs:

- Pro Datei: Authoring-Tool, IFC-Schema (IFC2x3 / IFC4 / IFC4.3), Größe, `IfcProject`-GUID, Entity-Count, Stand
- Klassifikation: Architektur / Tragwerk / MEP / Sonderdisziplinen
- Validierung jedes IFC (IfcOpenShell + bSI-Validator)
- Vergleichs-Matrix Revit ↔ ArchiCAD ↔ Allplan: Property-Sets, Geometry-Representations, Quirks

### Stakeholder-Cast
- **Synthetic** für SE-Sprint-Demo (Markus / Alice / Bob / Sarah / Heidi mit deterministischen Keys, reproduzierbar)
- **Real** für Provinz-Bozen-Pitch danach (mit Einwilligung)

### Storage-Entscheidung
- **A — Google Drive Adapter** (sofort starten, Files bleiben dort, Hash+URL als kind:1063)
- **B — lokaler Blossom** (Docker, sauberer, Files unter eigener Kontrolle)
- **C — hashtree** (Roadmap, `npub/tree/path`-Adressierung)
- Empfehlung: A für Sprint, B parallel aufsetzen.

### Privacy-Pass
- Adress-Daten raus, Sub-Auftragnehmer pseudonymisieren
- IFC-Inhalte bleiben original (technisch, nicht personenbezogen)
- Hybrid: Private strfry-Relay mit Vollddaten + öffentliches Demo-Relay mit anonymisierter Replica

---

## Phase 1 — IFC Ingestion + Provenance (Woche 1–2)

Pro IFC ein **kind:1063** NIP-94 file-metadata Event:

```
tags: [
  ["url", "<google-drive-or-blossom-url>"],
  ["m", "application/x-step"],
  ["x", "<sha256>"],
  ["size", "<bytes>"],
  ["schema", "IFC4X3"],
  ["authoring-tool", "Revit|ArchiCAD|Allplan"],
  ["discipline", "architecture|structural|mep"],
  ["a", "<project-ref>"],
  ["ots", "<base64-opentimestamps-proof>"]
]
```

Plus **kind:30904** BCF-File-Reference (replaceable), das auf das NIP-94-Event verweist und IfcProject + IfcSpatialStructure ergänzt.

**Deliverable.** Python-Skript `ingest.py` (IfcOpenShell + nostr-tools). Relay enthält für jeden Raulassen-IFC ein vollständiges Provenance-Bundle.

---

## Phase 2 — Multi-Tool Viewer (Woche 2–3)

- web-ifc + Three.js
- Drei Modelle gleichzeitig (Federated View)
- Color-Coding nach Authoring-Tool (Debugging + Demo-Visualisierung)
- Element-Auswahl per IFC-GUID → Property-Panel
- Camera-Bookmark = Viewpoint (BCF-kompatibel)

**Killer-Moment.** Wenn alle drei IFCs sauber laden und gemeinsam klickbar sind, ist der Stack toolagnostisch bewiesen.

**Deliverable.** Single-Page Viewer auf Cloudflare Pages.

---

## Phase 3 — Coordination Replay (Woche 3–4)

Zwei Pfade je nach Datenlage:

**a) Vorhandene BCFs importieren.** `bcf2nostr.py` läuft über alle `.bcfzip`, jeder Topic → kind:30900, Comment → kind:1170, History → kind:1171.

**b) Neu generieren via Clash Detection.** Solibri oder IfcOpenShell-eigene Logik, jede Clash → Auto-Topic mit p-Tag auf zuständige Disziplin.

**Deliverable.** ~100–300 Topics + threaded Comments + Status-Audit + Snapshot-Links auf Blossom.

---

## Phase 4 — Stakeholder + Approvals (Woche 4–5)

- npubs + Profile-Events (kind:0)
- Rollen-Badges (NIP-58): `architect`, `coordinator`, `structural`, `mep`, `client`
- 3–5 Approval-Events (kind:30970), Single-Sig in v1, Frostr-Multi-Sig als v2
- Real-Projekt-Genehmigungs-Historie nachgespielt soweit verfügbar

---

## Phase 5 — Gebäudebuch v1 (Woche 5–6)

Generator aus `gebaeudebuch-generator-scope.md` läuft gegen den Raulassen-Event-Korpus:

- Filter: alle Events mit a-Tag auf Raulassen-Project
- Render in HTML, 6 Kapitel
- „Drucken als PDF" → `raulassen-gebaeudebuch.pdf`
- Jeder Satz auf signiertes Quell-Event zurückführbar (e-Tag-Liste im Anhang)

---

## Phase 6 — Validation + Polish (Woche 6+)

- Generiertes Gebäudebuch gegen reale Projekt-Doku abgleichen
- Lücken → Phase-2-Backlog
- Demo-Video pro Phase (60 s)
- Pilot-Pitch-Deck

---

## Tooling-Stack (konkret)

| Aufgabe | Tool |
|---|---|
| IFC-Parsing + Validierung | IfcOpenShell (Python) |
| Hashing + OTS | hashlib + opentimestamps-client |
| Nostr-Publish (server-side) | nostr-tools (Python) |
| Nostr-Subscribe (client-side) | NDK (Vanilla JS, esm.sh) |
| Web-Viewer | web-ifc + Three.js |
| Relay (lokal) | strfry oder nostr-rs-relay (Docker) |
| Blob-Storage | Blossom-Server (Docker) oder Google Drive (initial) |
| Templating (Gebäudebuch) | Vanilla HTML + CSS Print |
| v2 LLM (später) | Ollama qwen3:14b (lokal, AdlerHort-Hardware) |

---

## Strategische Nebenprodukte

- **Multi-Tool-IFC-Interop-Demo** — allein SE-pitchable
- **NIP-Draft-Material** — nach 6 Wochen weiß man genau, welche Tags fehlen, welche Kinds sich bewähren; Spec schreibt sich quasi selbst
- **AdlerHort-Synergie** — Raulassen-IFCs als Training-Material; doppelter Hebel
- **Bauherrenstack-Vorlauf** — Gebäudebuch ist gleichzeitig erster Bauherrenstack-Use-Case
- **Provinz-Bozen-Türöffner** — fertige Demo + DSFA + Open-Source-Lizenz = wenig Reibung

---

## Kritische Entscheidungen vor Tag 1

1. **Synthetic-Cast oder Real-Stakeholder?** Empfehlung: Synthetic für Sprint, Real für Pitch danach.
2. **Public oder Private Relay?** Empfehlung: privates strfry für Vollddaten + öffentliches Demo-Replay anonymisiert.
3. **Storage:** Google Drive oder lokaler Blossom? Empfehlung: A jetzt, B parallel.
4. **Repo-Struktur:** Mono-Repo `raulassen-pilot/` mit Sub-Folder pro Phase, MIT, Conventional Commits.

---

## Sofortige nächste Schritte (heute/morgen)

1. **Repo aufsetzen.** `raulassen-pilot/` auf GitHub, README mit dieser Phasen-Übersicht.
2. **IFC-Inventur in `inventory.csv`.** Pro Datei: Tool, Schema, Größe, IfcProject-GUID, Pfad.
3. **Erste Validierung.** Ein IFC pro Tool durch IfcOpenShell schicken, Schema-Version + Health-Check.
4. **Privacy-Entscheidung.** Synthetic oder Real?
5. **Storage-Entscheidung.** Google Drive oder lokaler Blossom?
6. **`ingest.py` v0 anfangen.** 50 Zeilen Python reichen, um den ersten IFC durchzuschleusen und einen kind:1063 zu publishen.

2–3 Tage Foundation-Arbeit, dann läuft die Pipeline und wir können sechs Wochen lang Substanz aufbauen statt Demos basteln.

---

*Großwasserkraft-Prinzip: einmal gebaut, immer wieder verwendbar. Jedes nächste Projekt wird schneller, jeder neue Mandant kostet weniger Setup. Templates emergieren aus der Praxis, NIPs aus den Templates.*
