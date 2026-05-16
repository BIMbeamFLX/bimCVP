# Kind Registry — Gemeinwert / BIM CVP Pilot

**Status.** Internal allocation, not a NIP yet. Maintained alongside pilot code. NIP proposal only after 3+ project validations.

**Principle.** Use existing kinds where they fit. Own range only where there is a NIP gap + replaceable need. Document tag conventions cleanly so future self and contributors don't have to guess.

**Reference to standards.** The version choices (which IFC, which BCF, which MVD …) are centrally fixed in `STANDARDS-PROFILE.md`. This registry describes only how the Nostr events are structured. When a standard version bumps, `STANDARDS-PROFILE.md` is updated; the corresponding tag value ranges follow here.

---

## Own range 30900–30999 (parameterized replaceable)

| Kind | Name | `d`-Tag | Content | Status |
|---|---|---|---|---|
| 30900 | BCF Topic | topic-guid | current state | in testing |
| 30901 | BCF Viewpoint | viewpoint-guid | camera + components | in testing |
| 30902 | BCF Project | project-guid | project metadata | in testing |
| 30903 | Document Reference | doc-guid | external document | reserved |
| 30904 | IFC File Reference | file-guid | IFC or other model | in testing |
| 30810 | IDS Specification | spec-guid | Information Delivery Spec | reserved |
| 30811 | LOIN Definition | loin-id | Level of Information Need | reserved |
| 30850 | Product Data Template (PDT) | template-id | manufacturer datasheet | reserved |
| 30880 | PIR / Owner Information Requirements | spec-id | Project Information Requirements | reserved |
| 30881 | Room Book Entry | room-id | DIN 18205 compliant room | reserved |
| 30930 | Document Record | doc-id | ISO 19650 lifecycle document | reserved |
| 30940 | LCA Study reference | study-id | EN 15804/15978 LCA report, CAM 1.3.2 | reserved |
| 30941 | LCC Study reference | study-id | EN 16627 LCC report | reserved |
| 30942 | Level(s) Indicator Set | period-id | EU reporting snapshot | reserved |
| 30960 | Construction Diary Entry | YYYY-MM-DD | OTS-anchored | reserved |
| 30962 | Maintenance Cycle | cycle-id | maintenance event per CAM 2.3.16 | reserved |
| 30970 | Approval (single or multi-sig) | approval-id | plan / phase release | reserved |
| 30971 | Deconstruction Plan Approval | plan-id | CAM 2.3.17, 70% reuse target | reserved |
| 30972 | Export Authorization | export-id | publish-to-external-CDE manifest | reserved |

## Own range 1170–1179 (regular, immutable)

| Kind | Name | Content |
|---|---|---|
| 1170 | BCF Comment | comment text on topic |
| 1171 | BCF Audit Event | field change (status, priority, assignee) |
| 1172 | BCF Reaction | quick ack ("seen", "working on it") |

## Own range 1180–1189 (regular, immutable)

| Kind | Name | Content |
|---|---|---|
| 1180 | IDS Validation Result | pass/fail with report ref |
| 1190 | Sustainability Indicator Snapshot | Level(s) indicator point-in-time, CAM reporting |
| 1230 | HVAC Telemetry | sensor data point |

## Used existing kinds

| Kind | NIP | Usage |
|---|---|---|
| 0 | NIP-01 | profile metadata per stakeholder |
| 1 | NIP-01 | demo notes, tribe-level comments |
| 1063 | NIP-94 | file metadata for IFCs, snapshots, attachments |
| 9735 | NIP-57 | zaps (bounty, donations) |
| 9734 | NIP-57 | zap requests |
| 30023 | NIP-23 | long-form: reports, justifications, annexes |
| 9000 / 9007 | NIP-29 | group management |
| 30009 | NIP-58 | badge awards for role attestation |

---

## Tag conventions (binding for the pilot)

| Tag | Meaning | Required? |
|---|---|---|
| `d` | identity for replaceable events (GUID etc.) | yes for 309xx |
| `a` | project reference (format `30902:<pubkey>:<project-guid>`) | yes for 309xx + 1170 + 1171 |
| `h` | NIP-29 group ID (if project in a group) | when present |
| `e` | event reference (topic, viewpoint, file, parent comment) | per relationship |
| `p` | pubkey of a participant (assignee, reporter, watcher) | when applicable |
| `t` | free tag or BCF label | optional |
| `bcf-version` | buildingSMART BCF version that the event semantically represents: `3.0` (default) or `2.1` (fallback) | yes for 309xx |
| `bcf-status` | topic status (BCF 3.0 Project Extensions value list) | yes for 30900 |
| `bcf-type` | topic type (Issue, Clash, RFI, …) | yes for 30900 |
| `bcf-priority` | priority | optional |
| `bcf-due` | unix timestamp due date | optional |
| `bcf-stage` | project phase | optional |
| `bcf-server-assigned-id` | human-readable ID from BCF 3.0 ServerAssignedId | optional |
| `ifc` | IFC element GUID (22-char compressed) | when topic references an element |
| `ifc-file` | event ID of a kind:30904 file ref | when model is referenced |
| `ifc-project` | IfcProject GUID | yes for 30904 |
| `ifc-spatial` | IfcSpatialStructureElement GUID | optional |
| `authoring-tool` | Revit / ArchiCAD / Allplan / Tekla / Vectorworks / DDS-CAD / … | yes for 30904 |
| `discipline` | `architecture` / `structural` / `mep` / `electrical` / `civil` / `buildingPhysics` / `fireSafety` | yes for 30904 |
| `schema` | exact IFC version: `IFC4X3_ADD2` (default), `IFC4_ADD2_TC1`, `IFC2X3_TC1` (legacy) | yes for 30904 |
| `mvd` | Model View Definition: `ReferenceView` (default), `AlignmentBasedView`, `IFC4Precast`, `IFC2x3CoordinationView` … | yes for 30904 |
| `iso19650-state` | lifecycle state: `WIP` / `Shared` / `Published` / `Archive` | yes for 30903, 30904, 30930 |
| `ids-spec-ref` | event ID of a kind:30810 IDS spec being validated against | yes for 1180 |
| `x` | sha256 (hex, lowercase) | yes for file metadata |
| `m` | MIME type | yes for file metadata |
| `size` | bytes | yes for file metadata |
| `ots` | OpenTimestamps proof (base64) | optional |
| `audit-field`, `audit-from`, `audit-to` | field value change | yes for 1171 |
| `client` | producer client (tool name + version) | optional |
| `bcf-action` | BCF API action (`update`, `createComment`, `createViewpoint` …) — relevant for audit events | optional for 1171 |
| `visibility` | `internal` / `team-shared` / `client-ready` — controls export filter | default `team-shared` |
| `remote` | external CDE endpoint (`provincia-bolzano-cde`, `acc-mirror`, etc.) | optional, multiple allowed |

### Honesty tags — data provenance

CAM data is often modelled, not measured. Each sustainability value carries a source marker:

| Tag | Values | Meaning |
|---|---|---|
| `epd-source` | `model` / `verified` / `measured` | EPD industry average / EN-15804-accredited / factory telemetry |
| `lca-source` | `model` / `verified` / `measured` | same for LCA calculations |
| `co2-source` | `model` / `verified` / `measured` | same for CO2 balance values |

Usage example in a `kind:30850` PDT or `kind:30940` LCA event:

```
["epd-uri", "https://epditaly.it/epd/abc123"]
["epd-source", "verified"]
["epd-valid-until", "2029-04-15"]
["co2-source", "model"]
```

Audit trail thus shows what was estimated and what was measured. Over years, `measured` gradually replaces `model` values without structural change.

### Private-layer cross-references (Bitcoin / White Noise / Bitcredit)

Per PRINCIPLES section 4 (Public ledger, private conversation): every signed public event MAY carry references to corresponding off-chain private artifacts. Identity stays `npub`-rooted; both layers share the same actor.

| Tag | Values | Meaning |
|---|---|---|
| `white-noise-group` | MLS group identifier | Private team discussion that preceded or accompanies this public event. Allows audit-traceback without disclosure. |
| `bitcredit-note` | Bitcredit note identifier (URI / hash) | Real Bill issued against this event as underwriting substrate. Use on approved Abschlagsrechnung / Lieferantenkredit events. |
| `lnurl-pay` | LNURL-Pay endpoint or Lightning Address | Payment endpoint for service-bound events (DVM marketplace, Bauleistung-Pay-Per-Item). |
| `cashu-mint` | Cashu mint URL | For anonymous reviews or whistleblower channels coupled to this event. |
| `nip-44-key` | hex pubkey | Encryption key for NIP-17 fallback when White Noise unavailable. Per PRINCIPLES §4 production-readiness clause. |
| `fedimint-fed` | Federation invitation code | Shared-treasury context (Bauherrengemeinschaft, planning office liquidity pool). |

Usage example on a `kind:30970` Approval event:

```
["a", "30902:<pubkey>:raulassen-2026"]
["e", "<topic-event-id>"]
["bcf-status", "Closed"]
["white-noise-group", "mls-grp-raulassen-hkls-bauteam"]
["bitcredit-note", "bcr:bn1...subleistung-EG-HKLS"]
["ots", "<base64 timestamp proof>"]
```

The Approval is publicly signed and auditable. The pre-discussion remains in the MLS group. The Real Bill is anchored on Bitcredit and references the same approval as its underwriting source. Three protocols, one event.

### CAM Edilizia 2025 tags

| Tag | Values | Required? |
|---|---|---|
| `reuse-class` | `direct-reuse` / `recycle` / `recovery` / `disposal` | yes for `kind:30850` PDT + 30971 |
| `dismount-method` | free text (screwed, glued, mortared …) | optional, in PDT |
| `uni-8290-code` | building part code per UNI 8290-1 | optional for Italian projects |
| `epd-uri` | URL to accredited EPD | yes for 30850 if present |
| `epd-valid-until` | ISO date | yes for 30850 if epd-uri set |
| `lca-rsp` | Reference Study Period in years | yes for 30940 |
| `level-s-indicator` | indicator name per EU Level(s) framework | yes for 1190 |

---

## Versioning policy

### Two version axes

- **`bcf-version` in the event** references the **buildingSMART BCF version** the event is semantically compatible with (`3.0` as default, `2.1` as fallback). This axis follows buildingSMART, not us.
- **Our pilot schema iteration** is tracked at the repo level: git tag, release notes, `README.md`. This axis describes how our tag conventions mature. Pre-1.0 expects breaking changes; consumers must be tolerant.

### When to bump what

- **buildingSMART version bump** (e.g. BCF 3.0 → 3.1): update `STANDARDS-PROFILE.md`, extend the `bcf-version` value list here, events carry the new version once producers switch.
- **Our tag rename or required-tag change**: repo tag bump to major (e.g. v0.2 → v0.3), consumers need to adjust their parsers.
- **New optional tags**: repo tag bump to minor, old consumers work unchanged.
- **Repo tag 1.0**: only after NIP draft consensus and at least 3 completed pilot projects.

### Current state

- Repo version: 0.1 (pre-release, breaking changes expected)
- BCF default: 3.0
- IFC default: 4.3.2.0 with Reference View MVD
- IDS default: 1.0

---

## Path to NIP

1. **Run through phases 0–6 of the Raulassen pilot** (see `raulassen-pilot-build-plan.md`).
2. **Review the event corpus** — which tags were actually used, which were dead, which were missing.
3. **Run schema validation** over the gathered material, mark inconsistencies.
4. **Write the NIP draft** with real events as test vectors.
5. **Consensus sondierung** with 1–2 other AEC builders before PR.
6. **PR against `nostr-protocol/nips`** with the allocated range reservation.

Earliest Q4 2026, realistically Q1/Q2 2027.

---

*This file lives with the code. Every change in the tag or kind schema = entry here. No tag convention in code that isn't documented here.*
