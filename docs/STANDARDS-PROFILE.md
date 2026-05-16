# Standards Profile — Gemeinwert / BIM CVP

**Purpose.** Fixes which versions of which buildingSMART and ISO standards the pilot uses exactly, with reasoning per choice. Based on the deep research from May 2026 and the CDE market research (`docs/cde-research.md`).

**Principle.** Not generic "IFC4" or "BCF" — but exact pinned versions. Otherwise the pilot drifts into incompatibilities and the NIP draft has no test vectors.

---

## 1. Canonical model format: IFC 4.3.2.0

- **Version:** IFC 4.3.2.0 (official schema designation)
- **Released:** April 2024
- **Status:** official buildingSMART standard, semantically identical to ISO 16739-1:2024 (the published 4.3.2.0 documentation adds examples and typo corrections)
- **Reason:** the current official core for buildings and infrastructure. First IFC release that covers bridges, road, rail, tunnels and ports. Still fully compatible with IFC4 workflows for buildings.

**Legacy read paths (read-only):**

- **IFC 4.0.2.1 (IFC4 ADD2 TC1)**, October 2017 — widely used in building toolchains, ISO 16739-1:2018
- **IFC 2x3 TC1**, July 2007 — required for legacy FM stock
- IFC 4.1.0.0 (June 2018) and 4.2.0.0 (April 2019) are withdrawn — read path optional

**Not for use:** IFC 4.4.x dev and IFC 5 dev are not production-ready. Keep watch, but no pilot use.

**Tag value normalization at code level:** in the `schema` tag we use toolchain-common labels `IFC4X3_ADD2` (for IFC 4.3.2.0), `IFC4_ADD2_TC1` (for 4.0.2.1), `IFC2X3_TC1` (for 2x3 TC1).

---

## 2. Standard exchange profile: Reference View 1.2

- **MVD:** Reference View 1.2 for IFC4 ADD2 TC1
- **Status:** official, Final
- **Reason:** broadest interoperability for reference-based exchange in buildings and most of infrastructure. This is the "safest" default for a CDE.

**Special MVDs that need conditional support:**

| MVD | IFC base | When | Status |
|---|---|---|---|
| Reference View 1.2 | IFC4 ADD2 TC1 | building default | Final |
| Alignment Based View 1.0 | IFC 4.3 | road, rail, tunnel — infrastructure projects | in formal review 2025 |
| Design Transfer View | IFC4 ADD2 TC1 | one-way authoring-tool-to-tool transfer | never cleanly finalized by buildingSMART — not a primary target |
| IFC4Precast | IFC4 ADD2 TC1 | precast — explicitly separate from RV | Final |
| Quantity Takeoff View | IFC4 ADD2 TC1 | BOQ / quantities linkage (parking lot) | Draft |
| Energy Analysis View | IFC4 ADD2 TC1 | EPBD recast energy reports | Draft |
| Product Library View | IFC4 ADD2 TC1 | manufacturer PDTs (`kind:30850` later) | Draft |
| IFC2x3 Coordination View | IFC 2x3 TC1 | legacy coordination | Final |
| IFC2x3 Basic FM Handover View | IFC 2x3 TC1 | CAFM/CMMS handover to legacy tools | Final |

**Pilot default:** Reference View 1.2. Other MVDs only when the specific use case forces them. For infrastructure projects use Alignment Based View 1.0 once production and tool-validated.

**MVD formalization:** all MVDs are defined in `mvdXML`, a buildingSMART-standardised format for formal IFC schema subset description.

---

## 3. Information requirements: IDS 1.0

- **Version:** IDS 1.0
- **Released:** 1 June 2024
- **Status:** official buildingSMART standard, Final (pre-1.0 versions were not official)
- **Reason:** the first Final standard for machine-readable information requirements with clear IFC binding. Replaces informal EIR PDFs with machine-checkable specs.

**What IDS can check:** requirements on properties, quantities/attributes, materials, classifications, entity types, and `partOf` dependencies.

**What IDS does not cover:** geometry requirements. Those stay with MVD + LOIN.

**Practical consequence:** IDS today is often the more effective lever than purely textual specifications, because it is machine-checkable and versionable like code. EIR/AIA texts can remain attachments; operational requirements move into IDS.

---

## 4. Coordination: BCF API 3.0 + BCF XML 3.0

- **BCF API 3.0:** Final, released **17 June 2021**
- **BCF XML 3.0:** Final, released **18 June 2021**
- **Fallback BCF API 2.1:** Final, released **16 January 2017**
- **Fallback BCF XML 2.1:** Final
- **Reason:** BCF 3.0 builds on 2.1, extends OpenCDE integration and introduces `ServerAssignedId`, `DocumentReferences`, `ViewSetupHints`, `Coloring`, `Bitmaps`. Required for ISO-19650-compliant workflows. Auth/authorization with per-entity authorization and project extensions is much cleaner for CDE operation than 2.1.

**Practice note:** existing tools often still speak BCF 2.1. Our adapter must read/write both directions (round-trip tests mandatory).

**Tool compatibility (vendor-self-reported, as of 2026):**

| Tool | BCF XML 2.0/2.1/3.0 | BCF API 2.0/2.1/3.0 |
|---|---|---|
| Archicad | 2.0 / 2.1 / 3.0 | 2.0 / 2.1 / 3.0 |
| Solibri Office | 2.0 / 2.1 / 3.0 | 2.0 / 2.1 / 3.0 |
| ALLPLAN | (not declared) | 2.0 / 2.1 |
| BIMcollab Zoom | 2.0 / 2.1 | 2.0 / 2.1 |
| DESITE BIM | 2.1 / 3.0 | 3.0 |
| usBIM | 2.0 / 2.1 / 3.0 | 3.0 |
| Quadri | 2.1 | 2.1 |

Conclusion: 2.1 is everywhere, 3.0 is not. Our stack must speak **3.0 natively as server** and **2.1 import/export** for backwards compatibility.

---

## 5. OpenCDE API stack

- **Foundation API:** 1.1 (released together with Documents API 1.0)
- **Documents API:** 1.0 Final, **21 December 2023**
- **Dictionary API:** bSDD-compatible (live service)
- **BCF API:** 3.0 (see above)

**Foundation 1.1 enforces:**

- OAuth2-based authentication
- TLS minimum 1.2 (HTTPS-only)
- standardized error objects
- **ETags** for cache and change control
- full PUT updates
- CORS
- date/time per RFC3339
- versioning / service discovery
- paging / sorting / filtering via **OData**
- **Client Credentials Grant explicitly not supported** (no user identity transferable) — aligns with our npub-first principle.

**Documents API 1.0 specifics:**

- selection / download / upload of files including metadata
- callback URL for upload workflows
- external storage targets supported (exactly the adapter pattern we need for `nodrive://`)
- recommended: short, random, **single-use URLs** for selection and upload workflows
- malware scanning, MIME check, controlled binary uploads as mandatory

**Linking BCF API ↔ Documents API:** BCF topics can reference Documents API files via `open-cde-documents://…` URIs without carrying the binary itself.

---

## 6. Classification: bSDD URIs

- **Service:** buildingSMART Data Dictionary, live
- **Use:** referenced URIs of the form `https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/prop/...`
- **Reason:** stable, multilingual terms for classes, properties, materials. Referenceable in IFC properties and IDS specifications.

**Pilot position:** we do not build our own dictionary, we reference bSDD URIs. Own classifications are exclusively project-specific and embedded in property sets.

---

## 7. Process model: ISO 19650 + Swiss default profile

**Technical layer** is DACH-neutral.
**Process layer** follows the Swiss profile as default, with adapters for DE and AT.

### 7.1 Why Swiss profile as default

| Switzerland | Germany | Austria |
|---|---|---|
| Best **operational artifacts**: KBOB contract annexes "Application of the BIM method", BIM Abwicklungsmodell, LOIN guides per SN EN 17412-1 (2026), AIM basics, BIM2FM data field catalog, openBIM.ch workflow sheets, national glossary by buildingSMART Switzerland | Strongest **governance line**: BIM Deutschland + DIN EN ISO 19650 + VDI 2552 Blatt 5 + AIA/BAP/BIM4INFRA templates | Strongest **normative consolidation**: **ÖNORM A 6241-1:2025** (published 15.10.2025) + A 6241-2 (Level-3 iBIM) |
| **Directly usable for product design** | More program- and template-driven than operational | Strong in training (BIMcert), strong infrastructure operators (ASFINAG, ÖBB) |
| **SIA 2051 retired end of 2024** — consolidation toward ISO 19650 ongoing | KBOB provides explicit **orientation guide to SN EN ISO 19650 part 1** | ASFINAG and ÖBB are strong public BIM drivers |

**Consequence:** the Swiss KBOB profile with BIM Abwicklungsmodell and LOIN guides becomes the default workflow template. DE projects get DIN/VDI adapter, AT projects get ÖNORM A 6241 adapter, IT projects get UNI 11337 adapter (see section 8.2).

**KBOB minimum requirements for contract annexes** (should be reflected in CDE tenders): openBIM principles, structured data delivery, BIM model plan with IFC class specifications, BEP/BAP as central project steering instrument, data sovereignty + data security + data protection + liability explicitly addressed.

### 7.2 ISO 19650 lifecycle states

Four canonical states, encoded in document and model events as the `iso19650-state` tag:

- **WIP** (Work In Progress) — author works, no one else sees it
- **Shared** — visible to defined team members, not yet final
- **Published** — approved by approver, authoritative
- **Archive** — completed, archived

Transitions are not free write rights, but explicit transition rights with approver authority.

---

## 8. Role model — two axes

We separate **discipline** (what I do) and **project authority** (which rights I have).

### 8.1 Discipline axis (IFC ActorRoleEnum)

From IFC 4.3 ADD2 schema:

`ARCHITECT`, `STRUCTURALENGINEER`, `MECHANICALENGINEER`, `ELECTRICALENGINEER`, `CIVILENGINEER`, `BUILDINGPHYSICIST`, `FIRESAFETYENGINEER`, `CONSTRUCTIONMANAGER`, `CLIENT`, `CONTRACTOR`, `SUBCONTRACTOR`, `CONSULTANT`, `OWNER`, `PROJECTMANAGER`, `BUILDINGOPERATOR`, `RESELLER`, `MANUFACTURER`, `SUPPLIER`, plus `UserDefinedRole`.

### 8.2 Project authority axis (ISO 19650 + practice consolidation)

| Role | Short form | Primary authority |
|---|---|---|
| CDE Administrator | `cde-admin` | technical operation, no functional release |
| Information Manager / CDE Governance | `info-manager` | conventions, container rules, project defaults |
| Lead Appointed Party (overall coordinator) | `lead-appointed` | contractor-side overall coordination |
| Task Team Manager (discipline lead) | `task-team-lead` | discipline team leadership |
| Model Author / Specialist Planner | `model-author` | creates models and documents |
| BIM Coordinator / Reviewer | `bim-coord` | clash and quality review |
| Approver / Release Authority | `approver` | formal release (gate owner) |
| FM / Asset Representative | `fm-rep` | operations / AIM / handover view |
| External Observer / Auditor | `observer` | read-only audit access |

**Italian adapter** (UNI 11337-7) maps to the ISO 19650 layer:

| Italian term | ISO role |
|---|---|
| BIM Manager PA | Information Manager |
| BIM Coordinator PA | BIM Coordinator |
| BIM Specialist PA | Model Author |
| CDE Manager | CDE Administrator |

### 8.3 Encoding in the Nostr event

In the `kind:30902` BCF Project event, members are listed via `p` tags:

```
["p", "<pubkey-hex>", "<relay-hint>", "<discipline>", "<project-authority>"]
```

Multi-assignment possible (a person can combine multiple disciplines or roles) — then multiple `p` tags for the same pubkey.

---

## 9. Rights and policy model

### 9.1 Two-layer architecture

- **RBAC base:** who is fundamentally allowed to act on which resource type — projects, folders, documents, models, topics, comments, viewpoints.
- **ABAC overlay:** under which conditions the access actually applies — phase, stage, status, discipline, responsibility, tenant, confidentiality class, document class, model container, asset type.

### 9.2 BCF-API-compliant rights vocabulary

We use the BCF API action lists directly:

- `project_actions`: `update`, `createTopic`, `createDocument`
- `topic_actions`: `update`, `updateBimSnippet`, `updateRelatedTopics`, `updateDocumentReferences`, `updateFiles`, `createComment`, `createViewpoint`
- `comment_actions`: `update`

These actions are published in the project event as extensions, with local exceptions in the `authorization` field on topic / comment.

### 9.3 Status transition rights

Status changes are **separate permissions**, not implied by write rights. Defined per transition:

- `WIP → Shared`: model author themselves
- `Shared → Published`: approver role
- `Published → Archive`: information manager + approver jointly (Frostr multi-sig optional)
- `* → Closed/Resolved`: BCF topic role + approver

---

## 10. Audit and event model

### 10.1 What gets logged (at minimum)

- login / auth events
- rights resolutions
- document upload (with hash)
- version creation
- metadata changes
- status changes (with `audit-field`, `audit-from`, `audit-to`)
- issue creation
- comment
- viewpoint changes
- linking of documents and topics
- approvals
- exports and downloads
- failed attempts

### 10.2 Technical anchoring

- **Foundation API ETags** provide conditional-request audit at server level
- **BCF Topic Events / Comment Events** are the event-stream layer
- **IFC OwnerHistory** at model level
- **Our `kind:1171` audit events** span the Nostr layer over all of it

For tamper resistance: OpenTimestamps anchor on construction-diary and approval events. Optionally on audit events for highly sensitive projects.

---

## 11. Privacy and compliance

### 11.1 Applicable law

- **Switzerland:** revised Federal Act on Data Protection (revDSG), in force since 1 September 2023
- **EU / Italy / Austria / Germany:** Regulation (EU) 2016/679 (GDPR)

### 11.2 Personal data in a BIM CDE

The following fields can be personal and must be handled accordingly:

- usernames / profiles (kind:0)
- free-text comments (kind:1170)
- issue histories (kind:1171)
- snapshots (if persons are recognizable)
- file attachments (if content is personal)
- approval logs
- metadata in models or documents

### 11.3 Mandatory measures

- data minimization in comments and forms
- standardized retention and deletion rules per container / project
- separation of functional documentation and IAM / security logs
- encryption in transit (TLS ≥ 1.2) and at rest (LUKS or similar)
- tenant and project isolation
- exportable audit trails
- location and transfer policies for CH/EU projects
- role-based visibility of sensitive attachments and snapshots

### 11.4 DPIA

For every public pilot project a separate data protection impact assessment. Template in `docs/BACKEND-SETUP.md` section 10 (skeleton).

---

## 12. Integration with authoring tools

| Tool | Integration | Note |
|---|---|---|
| Revit | built-in IFC exporter; Data Management API + Issues API as adapter | adapter onto our canonical BCF / Documents domain, not the other way |
| Archicad | built-in BCF format; Developer API with BCF import/export | very good candidate for deep integration |
| Allplan | IFC export, BCF support | standard path |
| Solibri | BCF Live Connector is BCF-API-compliant | ideal QA / coordination endpoint |
| ACC / BIM 360 | Data Management API + Issues API | external system with adapter, not semantic anchor |
| Tekla, Vectorworks, DDS-CAD | IFC + BCF | via standard paths |

---

## 12a. CAM Edilizia 2025 (Italy) — sustainability mandate

Since 25.11.2025 mandatory for Italian public construction procurement (D.Lgs. 36/2023 art. 57 par. 2). Three sections are technically relevant:

- **2.1.3 Progettazione in BIM** — BIM model must contain environmental and material data, EPDs per EN ISO 22057:2022
- **2.3.16 Piano di manutenzione** — maintenance documentation archived in BIM, IFC-compliant
- **2.3.17 Piano di decostruzione** — new in 2025, at least 70% of building part weight reusable or selectively recyclable, per UNI PdR 75 + UNI 8290-1

LCA / LCC per **EN 15804** (products), **EN 15978** (buildings), **EN 16627** (LCC). Reporting framework **Level(s)** (EU). Full analysis in `docs/cam-edilizia-2025-analyse.md`.

### Honesty tags — source labeling

CAM data are often modeled estimates, not measurements. To keep this visible in the audit trail, we label data provenance per value:

| Tag value | Meaning |
|---|---|
| `model` | industry dataset / generic factor (Ökobaudat, EPD-Italy, EcoPlatform) |
| `verified` | accredited EPD per EN 15804 + EN ISO 14025, third-party verified |
| `measured` | real factory telemetry or sensor data, signed by the producer |

Usage in PDT / LCA / EPBD events:

```
["epd-source", "model"]
["lca-source", "verified"]
["co2-source", "measured"]
```

The audit trail can then distinguish estimate from measurement. Over years, `measured` gradually replaces `model` values without changing the doc structure.

---

## 12b. Six CAM-related kind reservations

| Kind | Name | Trigger |
|---|---|---|
| `30940` | LCA study reference | EN 15804/15978, CAM 1.3.2 |
| `30941` | LCC study reference | EN 16627, CAM 1.3.2 |
| `30942` | Level(s) indicator set | EU framework |
| `30962` | Maintenance cycle / maintenance event | CAM 2.3.16 |
| `30971` | Deconstruction plan approval | CAM 2.3.17 |
| `1190` | Sustainability indicator snapshot | point-in-time, immutable |

Value ranges and tag conventions in `KIND-REGISTRY.md`.

---

## 13. What is explicitly not chosen (with reason)

- **proprietary formats** (Revit .rvt, ArchiCAD .pln) — only as authoring source, never as exchange.
- **Closed CDEs as backend** — pilot stays self-hostable.
- **ifcOWL** — semantically attractive, but toolchain thin and not NIP-friendly.
- **BimJSON** — historically interesting, no longer mindshare.
- **STEP phase profiles outside IFC** — out of scope.
- **BIM 5D / 6D / 7D extensions without IFC anchor** — proprietary or unstandardized.
- **NIP-04 for DMs** — cryptographically broken, replaced by NIP-17 + NIP-44.

---

## 14. Future tracking

What we watch closely, but don't include today:

- **IFC 4.4.x dev:** minor semantic-layer update of 4.3, active development at `buildingSMART/IFC4.4.x-development`. No release date.
- **IFC 5 alpha (released May 2026) / IFC X:** next generation. Component-based architecture (Entity Component System), JSON serialization at `ifcx.dev`, USD integration via Alliance-for-OpenUSD liaison. Alpha repo at `buildingSMART/IFC5-development`. Incremental release strategy — first reduced version, then modules. Not production-ready, no stable date. **Our adapter architecture should leave room for IFC 5 JSON as additional schema target once stable.** Strategically aligned with our Nostr-event-based thinking (both JSON, both component-based, both designed for programmatic access).
- **EPBD recast Building Logbook** requirements: finer content obligations from 2027/28
- **EU DPP / ESPR** for construction products from 2027
- **MLS-over-Nostr** for end-to-end encrypted groups with forward secrecy
- **NIP-29 v2** group management on standard relays
- **bSI Implementers Assembly** semi-annual events — next at ACCA Bagnoli Irpino, Italy. Strategic outreach opportunity for the Bolzano pilot context.

---

## 15. References

- buildingSMART Standards Repository (official database)
- buildingSMART IFC 4.3 ADD2 Documentation
- buildingSMART IDS 1.0 Release (2024-06-01)
- buildingSMART BCF Repositories (XML 2.0, 2.1, 3.0; API 2.1, 3.0)
- buildingSMART OpenCDE-API Repository (Foundation 1.1, Documents 1.0)
- buildingSMART Data Dictionary (bSDD) service
- ISO 16739-1:2024 (IFC 4.3 ADD2 as ISO standard)
- ISO 19650 series (Information Management)
- EN 15804 (LCA products) / EN 15978 (LCA buildings) / EN 16627 (LCC)
- EN ISO 22057:2022 (EPDs in BIM)
- EN 17412-1 (LOIN)
- SN EN 17412-1 (Swiss adaptation)
- ÖNORM A 6241-1:2025, A 6241-2 (Austrian standard)
- UNI 11337 (Italian standard, 12 parts)
- UNI PdR 75 (selective deconstruction), UNI 8290-1 (building parts terminology)
- DM 312/2021, D.Lgs. 36/2023, D.Lgs. 209/2024 Correttivo, CAM Edilizia 25.11.2025
- Level(s) — EU framework for sustainability indicators
- Swiss revDSG (in force 2023-09-01)
- EU GDPR (Regulation 2016/679)

---

*Status: May 2026. Living document — version bumps in the listed standards trigger an update. Before any NIP PR to `nostr-protocol/nips`, this profile must align with the test vectors used.*
