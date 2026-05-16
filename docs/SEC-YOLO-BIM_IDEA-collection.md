# SEC-YOLO-BIM_IDEA collection

**Vollständige Ideen-Sammlung** für Sovereign Engineering, fokussiert auf den Schnittpunkt Bauwesen / HKLS / BIM × Nostr-Stack × Bitcoin. Stand: Mai 2026.

**Spirit.** Easy Prototypes zuerst, Standards zweitens, Infra drittens. Domänen-Moat (BIM/HKLS) ausspielen, aber in 6 Wochen liefern, was tatsächlich versendbar ist.

---

## Realitätscheck: 6 Wochen

SE-Cohort = 6 Wochen. Das ist halb so viel wie vorher angenommen. Konsequenzen:

- Triplet (BCF-NIP + IDS-NIP + Validation-DVM) ist Phase 2 — zu groß für 6 Wochen mit Spec-Schreibe, PR-Diskussion und Implementation.
- Phase 1 muss aus **kleinen, abgeschlossenen Prototypen** bestehen, die je in 1–2 Wochen stehen.
- Standards-Drafts entstehen aus den Prototypen heraus, nicht umgekehrt: erst Code, dann NIP-PR.

---

## Phase-1-Plan (6 Wochen, easy prototypes)

```
W1   ████  Citadel-Resources Nostr-Erweiterung — Open-Content-Layer
W2   ████  BCF-Prototyp — CLI bcf2nostr + minimaler Web-Viewer
W3   ████  BCF-Prototyp Continuation + erste Tribe-Anbindung
W4   ████  zapviz — Zap-Flow-Visualisierung
W5   ████  adlerhort — [siehe 2.10, Scope final festzurren]
W6   ████  Polishing, Demo-Video, NIP-Draft-Outlines aus Code abgeleitet
```

Alles vier sind eigenständig demonstrierbar. Falls ein Stück hakt, hängt der Rest nicht dran.

---

## Strategische Bewertung in einem Bild

```
                  Phase 1                  Phase 2                 Phase 3
              (SE 6 Wochen)            (Folge-Cohort)             (Vision)
              ─────────────────       ─────────────────       ─────────────────
Easy          Citadel + Nostr         BCF-NIP (full draft)    nodrive-Adapter
Prototypes    BCF-Prototyp            IDS-NIP                 hashtree-Integration
              zapviz                  Validation-DVM          FIPS-Bridge
              adlerhort

Standards     (entstehen aus          OCF-NIP                 nodrive-Spec
              den Prototypen)         PDT-NIP                 Storage-Adapter-NIP
                                      LOIN-NIP

Apps          (in den Prototypen)     Atelier (OCF-Client)    Drive-UX
                                      IDS-Studio              Q&A-Stacker

Markt                                  PlanDVM                Material-Markt
                                      Validation-DVM

Infra         OTS-Bautagebuch         HKLS-Twin               Konferenz
                                      Sensor-Bausatz
```

---

## Bewertungsschema

| Symbol | Bedeutung |
|---|---|
| ★★★ | sehr stark, SE-tauglich, eigenständig pitchbar |
| ★★ | gut, ergänzend, Phase 2 |
| ★ | Spielerei oder Voraussetzung |
| S / M / L | Aufwand: Wochenende / Wochen / Monate |
| 🟢 | Phase 1 — easy prototype, in 6 Wochen drin |
| 🟡 | Phase 2 — Folge-Projekt |
| 🔵 | Phase 3 — Vision / Infrastruktur-Wette |

---

## 1. Phase 1 — Easy Prototypes (SE 6 Wochen)

### 1.1 Citadel-Resources × Nostr — Open-Content-Layer 🟢 ★★ · S
**Was.** Erweiterung von <https://citadel-resources.com> um Nostr-Integration: Open-Content-Sektion, die Nostr-Artikel (NIP-23) und Tribe-Feeds (NIP-72) aggregiert. Bauwesen/HKLS-Filter optional.
**Warum zuerst.** Sichtbares Output, Community-Hook, klein. Ist gleichzeitig die Hülle, in die spätere Projekte gestöpselt werden können (Bildungs-Sektion „Sovereign AEC").
**Stack.** Fork von citadel-resources oder PR-Beitrag, plus client-seitige Nostr-Subscription (nostr-tools / NDK) für NIP-23-Feeds.
**Deliverable.** Live-Sektion „Open Content" mit kuratierten npubs, deutschsprachig.

### 1.2 BCF-Prototyp — CLI + minimaler Web-Viewer 🟢 ★★★ · M
**Was.** `bcf2nostr` CLI (Import .bcfzip → Nostr-Events, Export Events → .bcfzip) plus dünner Web-Viewer (Topic-Liste, Comment-Threading, Snapshot-Anzeige).
**Warum.** Eigene Domäne, klare Demo, NIP-Draft fällt am Ende fast als Nebenprodukt ab.
**Scope-Disziplin für 6 Wochen.** Keine Viewpoint-3D-Rendering, kein Multi-Project, kein Encryption. Nur Topic + Comment + Status + Snapshot-Link.
**Stack.** TypeScript, NDK, ein Blossom-Test-Server für Snapshots.
**Deliverable.** CLI auf GitHub, Web-Demo auf Vercel/Cloudflare, ein PR-Outline gegen `nostr-protocol/nips`.

### 1.3 zapviz — Zap-Flow-Visualisierung 🟢 ★★ · S
**Was.** Visualisierung von Lightning-Zaps auf Nostr — wer zappt wen, wie viel, wann, für welches Event. Live-Sankey oder Timeline-Heatmap, optional pro Tribe/Topic filterbar.
**Warum.** Schnell, hübsch, demobar. Zeigt Lightning-Aktivität in einer Tribe konkret (auch für BCF-/Bau-Tribes nützlich — wer zahlt für Issues, Bounties, Validation-Jobs).
**Stack.** NIP-57 (Zap-Receipts kind 9735), D3.js oder Recharts, statische Hosting.
**Deliverable.** Web-App, optional einbettbar als iframe in Citadel-Resources.
**Open.** Genauer Scope — Single-User-Dashboard („meine Zaps") oder Public-Explorer? Falls Public: Default-Tribe-Filter sinnvoll.

### 1.4 adlerhort — [Scope final festzurren] 🟢 ★★ · S
**Was.** Arbeitstitel offen — drei plausible Lesarten:
- **a) Relay-/Identitäts-Watchtower:** persönliches Dashboard, das den eigenen npub über alle abonnierten Relays beobachtet (Relay-Erreichbarkeit, Replikations-Lücken, Outbox-Health).
- **b) Bau-Observatorium:** „Vogel-Perspektive" auf ein Bauprojekt — aggregierte BCF-Events, Status-Heatmap, Termin-Risiken aus DueDates.
- **c) Vault-/Backup-Tool:** Adlerhort als sicheres Schlüssel-/Backup-Lager (npub-Backups, Frostr-Shards, Cashu-Tokens in einem Tresor).

**Empfehlung.** Lesart (b) für AEC-Relevanz, weil sie auf BCF-Prototyp (1.2) aufsetzt — minimaler Mehraufwand, doppelter Hebel.
**Stack.** Web-Client, abonniert BCF-Tribes, rendert Dashboard.
**Deliverable.** Web-Demo mit echtem BCF-Datenstrom aus 1.2.
**Felix, klär bitte:** welche Lesart trifft deine Idee?

### 1.5 OTS-Bautagebuch (Wochenend-Spike) 🟢 ★★ · S
**Was.** Tagebucheintrag (Wetter, Personal, Lieferungen, Vorkommnisse) als signiertes Nostr-Event + OpenTimestamps-Anker auf der Timechain. Gerichtsfeste Beweissicherung.
**Warum als Backup.** Falls eines der vier Hauptprototypen kippt — OTS-Bautagebuch ist in einem Wochenende drin und steht eigenständig.
**Stack.** OTS-Client (JS oder CLI), simples Web-Formular.
**Deliverable.** Eintragsformular, OTS-Verifizierungs-Link, Stack als Tutorial.

---

## 2. Phase 2 — Folge-Cohort / nächste Runde

### 2.1 BCF-NIP — full draft 🟡 ★★★ · M
Vollständige NIP-Spec mit allen Event-Kinds (30900–30904, 1170–1172), Round-trip-Garantie, Test-Vektoren, PR gegen `nostr-protocol/nips`. Ausgearbeitet in `bcf-nostr-nip-research.md`.

### 2.2 IDS-NIP — Information Delivery Specification on Nostr 🟡 ★★★ · M
Anforderungs-Specs (bSI IDS 1.0) als kind 30810. Validation-Results als kind 1180. Killer-Andock an Validation-DVM.

### 2.3 Validation-NIP — DVM für IFC-Audit 🟡 ★★★ · M
NIP-90-Schicht: kind 5901 Request, kind 6901 Result. Schließt mit BCF + IDS den ersten dezentralen openBIM-QA-Loop.

### 2.4 LOIN-NIP 🟡 ★★ · S
DIN EN 17412-1 als kind 30811. Eng mit IDS verzahnt.

### 2.5 PDT-NIP — Product Data Templates 🟡 ★★★ · M
Hersteller-Datenblätter nach ISO 23387 als kind 30850. EU-DPP-Pflicht ab 2027 → starkes Timing-Argument.

### 2.6 UCM-NIP 🟡 ★★ · S
bSI-Use-Cases als kind 30840.

### 2.7 PSD-NIP — Property Set Definitions 🟡 ★★ · S
kind 30821. Vorläufer für bSDD-NIP.

### 2.8 Documents-NIP — openCDE-light 🟡 ★★ · M
kind 30930, ISO-19650-State als Tag.

### 2.9 HKLS-Telemetrie-NIP — Building-Twin live 🟡 ★★★ · M
Sensordaten als kind 1230. ESG/EPBD-Recast-Andock. Stärkster Domain-Moat.

### 2.10 OCF-NIP — Office Collaboration Format 🟡 ★★ · M
BCF-Pattern + NIP-44-Encryption + NIP-29-Workspaces. Markt jenseits AEC.

### 2.11 openCDE-Brücken-NIP 🟡 ★ · M
HTTP-Adapter für ACC/BIMcollab/Solibri → Nostr-Backend.

### 2.12 Storage-Adapter-NIP — `nodrive://` URL-Scheme 🟡 ★ · S
File-Ref-Resolver-Spec. Wird in BCF-NIP-Draft schon als Konvention referenziert.

---

## 3. Phase 2 — Apps

### 3.1 IDS-Studio 🟡 ★★ · M
Editor mit Live-Preview, bSDD-Autocomplete, publiziert als Nostr-Event.

### 3.2 Atelier — OCF-Client 🟡 ★★ · L
Slack/Linear-Hybrid auf OCF-NIP. Markt-Pivot von AEC zu allgemeiner Bürokommunikation.

### 3.3 Stacker-Style Q&A für Engineers 🟡 ★★ · S
Lightning-paid Q&A für normative Fachfragen.

### 3.4 Nostr-Fachartikel-Hub für AEC 🟡 ★ · S
Habla.news-Klon mit AEC-Filter. Andockt direkt an Citadel-Resources-Erweiterung (1.1).

---

## 4. Phase 2 — Marktplatz

### 4.1 PlanDVM 🟡 ★★★ · L
NIP-90-DVMs für Rückhaltebecken, Bewässerung, Fassade, MEP-Punktbemessung. Reputations-Badges (NIP-58), Cashu-Escrow optional.

### 4.2 Validation-DVM 🟡 ★★★ · M
Spezialfall PlanDVM, gekoppelt an IDS-NIP.

### 4.3 Lightning-Bounties für BCF-Issues 🟡 ★ · S
LNbits + BCF-Event-Layer. Issues bekommen Sat-Bounty.

### 4.4 Material-Pass-Marktplatz 🟡 ★★ · L
Plebeian-Style für gebrauchte Bauteile, npub-signierte Pässe.

### 4.5 DLC für Performance-Contracting 🟡 ★★ · L
kWh/m²-Zielwert per DLC, Oracle = Messdienstleister.

### 4.6 Geyser-Crowdfunding für Sanierungen 🟡 ★ · S
PV/Wärmepumpe/Dämmung-Kampagnen.

---

## 5. Phase 3 — Infrastruktur (Vision)

### 5.1 nodrive — sovereign Drive mit Adapter-Layer 🔵 ★★ · L
Nostr-native Control-Plane über jedes Storage-Backend (LocalFS, Blossom, S3, WebDAV, GoogleDrive, hashtree, FIPS-Mesh). Verschlüsselung clientseitig. URL-Scheme schon in Phase 1 verankert (2.12).

### 5.2 hashtree-Adapter 🔵 ★ · M
hashtree als Sovereign-Default unter nodrive.

### 5.3 FIPS-Bridge für offline-first AEC 🔵 ★★ · L
Baustellen-Office ohne Internet.

### 5.4 SSOT-Relay-Stack 🔵 ★ · S
strfry + NIP-29-Patch + Blossom als Docker-Compose. Ein Projekt-CDE in einem Befehl.

### 5.5 Sovereign-Sensor-Bausatz 🔵 ★★ · M
ESP32-Reference, publisht signierte Daten auf Nostr.

---

## 6. Phase 3 — Community

### 6.1 Frostr-Multisig für Planerkonsortien 🔵 ★ · M
n-of-m-Signatur für Generalplan-Abgaben.

### 6.2 BIM-Tech-Workshops auf Nostr 🔵 ★ · S
NIP-23-Tutorials, NIP-72-Tribe-QA, Lightning-Spende.

### 6.3 Konferenz „Sovereign AEC DACH" 🔵 ★ · L
Wenn die Community groß genug ist.

---

## 7. Verzahnung (Quer-Beziehungen)

| Kombination | Erzeugt |
|---|---|
| Citadel × Nostr + BCF-Prototyp | Reichweite und sofortiger Test-Traffic |
| zapviz + BCF-Tribe | sichtbare Lightning-Aktivität pro Issue |
| adlerhort + BCF | Projekt-Dashboard für Topics + Termine |
| BCF + IDS + Validation (P2) | dezentraler openBIM-QA-Loop |
| BCF + Validation | failed Validation → BCF-Topic |
| BCF + OTS-Bautagebuch | gerichtsfeste Doku |
| PDT + Material-Markt | Circular Economy mit DPP-Andock |
| HKLS-Telemetrie + DLC | Performance-Contracting mit Sat-Settlement |
| OCF + Atelier + nodrive | Sovereign-Office-Komplettpaket |
| Frostr + BCF + OCF | Multi-Sig für jede Abgabe |

---

## 8. Open Questions

1. **adlerhort-Scope** — Lesart (a) Watchtower, (b) Bau-Observatorium oder (c) Vault? Empfehlung: (b), weil Hebel mit BCF.
2. **zapviz-Scope** — Single-User-Dashboard oder Public-Explorer?
3. **Citadel-Erweiterung** — Eigener Fork oder PR ins Original? Empfehlung: PR, weil weniger Pflege-Last.
4. **Sprache** — Citadel-Sektion DE-only, zweisprachig oder EN-only?
5. **NIP-Draft-Strategie** — aus Phase-1-Code rückwärts ableiten oder erst nach Phase 2 publishen?
6. **Pilot-Projekt** — eigenes (Sanierung) oder externes (Verein, Genossenschaft) für Realitätsprüfung?

---

## 9. Parking Lot

- DVM-Bots für Standard-Bemessungen (Heizlast EFH, Sickerschacht DWA-A 138)
- Bündel-DVMs mit Multi-Provider-Stitching
- Cashu-Mint für interne Büro-Buchhaltung
- IFC-on-Nostr für Subset-Modelle (Spatial-Structure-Treemap)
- Tribe „Sovereign AEC DACH" — wenn Community-Grundstein durch Citadel-Erweiterung gelegt
- bSDD-NIP (Phase 3) — Konsens-Problem erst lösen
- Konferenz-Idee siehe 6.3
- ifcOWL-Brücke — eher akademisch, niedrige Priorität
- BimJSON-Reaktivierung — nur falls Mindshare zurückkommt
- Berufshaftpflicht-Pool als Frostr-Multisig — interessante Spielerei, ungelöst rechtlich

---

## 10. Quellen

- buildingSMART openBIM — <https://www.buildingsmart.org/about/openbim/>
- IDS 1.0 — <https://github.com/buildingSMART/IDS>
- BCF — <https://github.com/buildingSMART/BCF-XML>
- openCDE-API — <https://github.com/buildingSMART/OpenCDE-API>
- hashtree — <https://github.com/mmalmi/hashtree>
- gitworkshop — <https://gitworkshop.dev>
- Learn FIPS — <https://learn.fips.network>
- Sovereign Engineering Projects — <https://sovereignengineering.io/projects>
- Nostr NIPs — <https://github.com/nostr-protocol/nips>
- NIP-57 Lightning Zaps — <https://github.com/nostr-protocol/nips/blob/master/57.md>
- citadel-resources — <https://citadel-resources.com>
- Plebeian Market — <https://plebeian.market>
- Geyser — <https://geyser.fund>
- OpenTimestamps — <https://opentimestamps.org>
- einundzwanzig Portal — <https://portal.einundzwanzig.space>

---

*6-Wochen-Realität: Phase 1 muss demobar sein. Standards-Drafts fallen als Nebenprodukt aus Phase-1-Code. Phase 2 ist die nächste Cohort, Phase 3 die Vision im Pitch-Deck. Lebendes Dokument.*
