# Gemeinwert — BIM CVP

**BIM CVP — Common Value Protocol.** The open layer for signed construction. *build better with nostr.*

Signed coordination events, platform-neutral storage, fully built on open buildingSMART standards.

**Status.** Pilot phase, May 2026. First real project: Building (Provincia di Bolzano), anonymised here. Not production-grade — pilot loads and demos only.

**License.** MIT. Use, adapt, redistribute freely.

**Brand.** German market: *Gemeinwert*. International / standards: *BIM CVP — Common Value Protocol*. See [`docs/BRAND.md`](docs/BRAND.md).

---

## Repository layout

```
.
├── README.md          # this file
├── LICENSE             # MIT
├── .gitignore
├── docs/               # knowledge and concept docs (EN primary)
├── site/               # public website — multilingual, GitHub Pages ready
├── app/                # interactive HTML tools (identity, admin, wiki)
├── tools/              # CLI and Python ingest pipeline
├── skills/             # IFC classification skills
└── ifc/                # real project data (gitignored, .gitkeep only)
```

The backend (Strfry relay, Blossom, LNbits, Caddy) is not shipped as a compose
file in this pilot repo — it is documented step by step in
[`docs/BACKEND-SETUP.md`](docs/BACKEND-SETUP.md).

---

## Standards stack

Concretely fixed, not generic:

| Layer | Standard | Version | Status |
|---|---|---|---|
| Model | IFC | 4.3.2.0 | Final (April 2024, ISO 16739-1:2024) |
| Model MVD | Reference View | 1.2 | Final |
| Model legacy | IFC4 ADD2 TC1, IFC2x3 TC1 | — | Read-only support |
| Requirements | IDS | 1.0 | Final (June 2024) |
| Coordination | BCF API | 3.0 | June 2021, with 2.1 fallback |
| File exchange | BCF XML | 3.0 | June 2021, with 2.1 fallback |
| CDE API | OpenCDE Foundation | 1.1 | Official release branch |
| Documents API | OpenCDE Documents | 1.0 | Final (December 2023) |
| Classification | bSDD URIs | live | active service |
| Process | ISO 19650 + SN EN 17412-1 | current | Swiss process model as DACH default |
| Sustainability (IT) | CAM Edilizia 2025 | 25.11.2025 | mandatory for Italian public procurement |
| LCA / LCC | EN 15804 / 15978 / 16627 | current | required by CAM 2.3.17 |

Full reasoning in [`docs/STANDARDS-PROFILE.md`](docs/STANDARDS-PROFILE.md).

---

## Quick start

### Browse the website

The public site lives in [`site/`](site/) — open `site/index.html` locally, or
deploy via GitHub Pages (a workflow is included at
`.github/workflows/pages.yml`; enable Pages → "GitHub Actions" in repo settings).

### Use the interactive tools

```bash
# Open locally
xdg-open app/index.html        # or double-click on Windows
```

User journey:

1. `app/index.html` — collection overview (knowledge + tools + docs)
2. `app/character.html` — create your identity (RPG-style onboarding)
3. `app/admin.html` — create a project, invite members
4. More tools once the backend is running

### IFC ingest via CLI

```bash
cd tools
python -m venv .venv && source .venv/bin/activate    # Linux/Mac
python -m venv .venv && .venv\Scripts\activate       # Windows
pip install -r requirements.txt

# Place IFCs in ../ifc/, adjust inventory.csv
export RELAYS="ws://localhost:7777"
export BLOSSOM_URL="http://localhost:3000"
export PROJECT_GUID="building-pilot-2026"
python ingest.py <nsec-hex>

# Verify
python verify.py <npub>
```

Details: [`docs/building-pilot-build-plan.md`](docs/building-pilot-build-plan.md).

---

## Design principles

Three sentences that govern every architecture decision:

1. **We build nothing ourselves.** Mature open-source tools get wired together, not reimplemented.
2. **We address the bureaucracy toaster.** Outlook-level intelligibility is mandatory.
3. **Key backup is delegated in pilot phase.** Browser extension or mobile signer, not our responsibility.

Full text in [`docs/PRINCIPLES.md`](docs/PRINCIPLES.md), including a veto heuristic for new feature ideas.

---

## Key documents

Strategy and background:

- [`docs/PRINCIPLES.md`](docs/PRINCIPLES.md) — design principles
- [`docs/BRAND.md`](docs/BRAND.md) — Gemeinwert / BIM CVP brand identity
- [`docs/STANDARDS-PROFILE.md`](docs/STANDARDS-PROFILE.md) — exact standard versions and DACH reasoning
- [`docs/KIND-REGISTRY.md`](docs/KIND-REGISTRY.md) — Nostr event kinds and tag conventions
- [`docs/building-pilot-build-plan.md`](docs/building-pilot-build-plan.md) — six phases for the first real pilot
- [`docs/gebaeudebuch-generator-scope.md`](docs/gebaeudebuch-generator-scope.md) — scope for the automatic building logbook
- [`docs/cde-research.md`](docs/cde-research.md) — market analysis and competitive landscape
- [`docs/cam-edilizia-2025-analyse.md`](docs/cam-edilizia-2025-analyse.md) — Italian mandatory sustainability criteria

Technical specs:

- [`docs/bcf-nostr-nip-research.md`](docs/bcf-nostr-nip-research.md) — full mapping BCF-XML 3.0 ↔ Nostr events
- [`docs/BACKEND-SETUP.md`](docs/BACKEND-SETUP.md) — step-by-step Docker Compose setup
- [`docs/lnbits-integration.md`](docs/lnbits-integration.md) — Lightning and wallet integration

Vision and roadmap:

- [`docs/nodrive-concept.md`](docs/nodrive-concept.md) — phase-3 infrastructure bet
- [`docs/SEC-YOLO-BIM_IDEA-collection.md`](docs/SEC-YOLO-BIM_IDEA-collection.md) — full idea collection with ratings
- [`docs/SEC-6-week-sprint.md`](docs/SEC-6-week-sprint.md) — sprint plan
- [`docs/sovereign-aec-sprint.md`](docs/sovereign-aec-sprint.md) — website content (English)

---

## Two-track strategy

**Track A — open infrastructure (Gemeinwert / BIM CVP).** MIT-licensed, give-it-away. Standards adoption is the goal. We want to be copied by ACCA usBIM, Catenda Hub, Autodesk Construction Cloud, BIMcollab — because when they adopt signed events as native mode, the market we serve emerges.

**Track B — DVM marketplace (Bimbeam).** Felix's commercial service track. NIP-90-based marketplace for HKLS/MEP planning, CAM-Edilizia audit, Bauherrenberatung, BIM setup consulting. Captures economic value on top of the open infrastructure.

Linux + Red Hat pattern. Gemeinwert is the protocol everyone can use. Bimbeam is one accredited service provider on top — others welcome.

---

## Contributors

Currently a solo build by Felix Hitthaler (HKLS/MEP + BIM engineer, South Tyrol).

Contributions welcome especially in:

- **Translations.** English is the source of truth for all dev-related material. German and Italian are sourced from English. We need IT translators (native speakers) for the Bolzano pilot.
- **Knowledge pages** in `site/wiki/` and `app/wiki/`: IFC deep-dives, IDS examples, ISO-19650 details, more regional comparisons.
- **Standards discussion.** Before any NIP PR, we want sondierung with the buildingSMART OSS community.
- **Pilot sponsorship.** NOI Techpark / Eurac as hosting partners for the Provincia di Bolzano real pilot.

Contact: via Nostr (npub TBD, follows once relay is live) or `hitthaler@bimbeam.at`.

---

## What this is explicitly not

- Not a replacement for Revit, ArchiCAD, Allplan or other authoring tools — those stay your authoring software.
- Not a competing pitch to Autodesk ACC, Catenda Hub, ACCA usBIM, or Trimble Connect — we deliver the signed, vendor-free layer for use cases where sovereignty matters.
- Not a promise of production-grade SaaS — pilot means pilot. Next maturity level only after real-project validation.
- Not a Bitcoin or cryptocurrency platform — cryptographic signatures use Schnorr / secp256k1, which is a technical detail. Optional Lightning payments for honoraries are voluntary.

---

## What can go wrong (expectation management)

- **Losing your key in the pilot is OK.** You create a new character, the admin re-adds you.
- **Relay outage self-heals.** Multi-relay outbox pattern, own server plus two public ones.
- **Blossom upload errors.** Usually a malformed auth event; check logs, see `BACKEND-SETUP.md` section 14.
- **IFC file too large.** Default timeout in `ingest.py` is 300 s; raise for files larger than 500 MB.
- **UI bug or missing feature.** GitHub issues. We're in pilot.

---

## Phase progression

- **Phase 1 (now, May/June 2026):** backend running, BCF Quickform prototype functional, first pilot IFCs ingested, character/admin UIs demoable locally.
- **Phase 2 (summer 2026):** OTS construction diary, plebbim bounty board, building logbook generator v1, pilot with real stakeholder circle.
- **Phase 3 (autumn/winter 2026):** owner requirements stack (PIR/EIR/room book), IDS validation DVM, NIP drafts for PR to `nostr-protocol/nips`.
- **Phase 4 (2027):** scale to more projects/clients, optional commercial hosting variant.

---

*Gemeinwert · BIM CVP · Pilot May 2026 · MIT · "Construction is the oldest trade — the open tools for it should be too."*
