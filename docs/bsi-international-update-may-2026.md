# buildingSMART International — Freshness Check May 2026

**Purpose.** Verify that our Standards Profile is not built on outdated information. Latest buildingSMART releases, working group activity, and roadmap updates as of May 2026.

**Bottom line:** the versions we picked (IFC 4.3.2.0, Reference View 1.2, BCF 3.0, IDS 1.0, OpenCDE Foundation 1.1 + Documents 1.0) all stay current and correct. **But** one major new development emerged: **IFC 5 alpha is released**, with USD integration and JSON serialization. This validates our earlier USD intuition and changes the Future Tracking section of `STANDARDS-PROFILE.md`.

---

## 1. What stays current (no change needed)

| Standard | Our pick | Status May 2026 |
|---|---|---|
| IFC core | 4.3.2.0 (ISO 16739-1:2024) | still current official standard |
| IFC legacy | 4.0.2.1 (IFC4 ADD2 TC1), 2x3 TC1 | still legacy read paths |
| MVD | Reference View 1.2 | still Final, recommended |
| Alignment MVD | Alignment Based View 1.0 | still in formal review 2025 |
| Coordination | BCF API 3.0 + XML 3.0 | still current, no BCF 4 in sight |
| Information requirements | IDS 1.0 (June 2024 final) | 1.1 + 2.0 planned, no release dates |
| CDE API | OpenCDE Foundation 1.1 | still current |
| Documents API | OpenCDE Documents 1.0 (Dec 2023) | still current |
| Dictionary | bSDD service | live, no recent version bump |

**Confirmation: STANDARDS-PROFILE.md sections 1–6 remain valid.** No rewrites needed for the chosen versions.

---

## 2. NEW: IFC 5 Alpha released

**Source:** [Master IFC 5 site](https://ifc5.technical.buildingsmart.org/), [GitHub buildingSMART/IFC5-development](https://github.com/buildingSMART/IFC5-development)

### Key architectural shifts

- **Component-based architecture (ECS).** Entity Component System pattern — objects defined by combining components (geometry, materials, properties) rather than by inheritance hierarchy.
- **JSON serialization.** Native JSON support, schema published at `ifcx.dev`. This is a fundamental departure from STEP/SPF.
- **USD integration.** Liaison agreement between buildingSMART International and the Alliance for OpenUSD. Pixar's USD becomes a basis for IFC 5 representation.
- **Standard API for IFC 5.** Programmatic access to IFC 5 data designed in from the start, not retrofitted.
- **Modular release strategy.** First a "reduced" version with basic functionality, then incremental module additions over years.

### Naming clarification

The next-generation IFC is sometimes called **"IFC X"** in buildingSMART internal naming (project: "IFC X Core"), and **"IFC 5"** in public materials. The first alpha repo is `IFC5-development`.

### Status

- **Alpha:** released
- **Production-ready:** no
- **Timeline to first stable:** not announced (incremental, "starting with reduced version")
- **For pilot use:** NOT yet — watch and contribute via GitHub, but don't build production workflows on alpha

### Strategic implications for Gemeinwert / BIM CVP

1. **Our USD-Baukasten idea from earlier discussions is now on the official buildingSMART roadmap.** What we were calling "Phase 3 USD layer" is exactly what IFC 5 is heading toward. We were ahead of curve, not in conflict with it.
2. **JSON serialization aligns with our Nostr-event-based thinking.** IFC 5 events as Nostr events becomes structurally natural — both are JSON, both are component-based, both are designed for programmatic access.
3. **Component-based architecture also aligns with our event-kind pattern.** We treat BCF Topics, IDS Specs, PDTs as composable signed events — IFC 5 treats building objects as composable component bundles. Same philosophy.
4. **We don't need to migrate yet.** IFC 4.3.2.0 stays our pilot foundation. But our adapter architecture should leave room for IFC 5 JSON as an additional schema target once stable.

---

## 3. NEW: IFC 4.4 in active development

**Source:** [GitHub buildingSMART/IFC4.4.x-development](https://github.com/buildingSMART/IFC4.4.x-development)

- Minor update of IFC 4.3
- Focus on semantic layer refinements
- Bridge release between 4.3 and 5
- No release date announced

**For us:** monitor, no action needed. When 4.4 lands, evaluate whether it offers anything we don't get from 4.3.2.0.

---

## 4. Implementers Assembly February 2026 — key takeaways

**Source:** [bSI Implementers Assembly Feb 2026 Event Report](https://www.buildingsmart.org/the-buildingsmart-implementers-assembly-february-2026-event-report/)

### Where and when

- Hosted by Bentley in Exton (Pennsylvania, USA)
- 11–12 February 2026

### Sessions

- bSI ↔ ISO/CEN collaboration alignment
- Standards status updates (IFC, IDS, BCF, IFC Validation, Software Certification)
- "Voice of the customers" — real implementer feedback
- **IFC 4.3 Implementation Issues session** — dedicated meetings of the IFC Implementers Forum planned to address these
- **IFC X (next generation) workshop** — breakout groups identified priorities and gaps; input feeds into the IFC X Core project

### Next Implementers Assembly

**Hosted by ACCA software in Bagnoli Irpino, Italy.** Registration open. This is a major strategic opportunity for us:

- ACCA = dominant Italian openBIM software house (usBIM.platform)
- Bagnoli Irpino = inside Italian openBIM heartland
- Our pilot context = Provincia di Bolzano (also Italy)
- If Felix attends the next Implementers Assembly, direct access to: ACCA, italian buildingSMART chapter, peer implementers, IFC X discussion

**Action:** check registration link, evaluate attendance.

---

## 5. BCF, IDS, openCDE — confirmed status

### BCF

- **No BCF 4 in development** visible in 2026.
- BCF 3.0 stays the current target.
- Tools support: still split (Archicad, Solibri, DESITE, usBIM support 3.0; BIMcollab, ALLPLAN, Quadri stay at 2.1).
- Our pilot strategy (server speaks 3.0 native, adapter handles 2.1 fallback) is correct.

### IDS

- **IDS 1.0 stays current** (released 1 June 2024).
- **IDS 1.1 planned** — minor fixes, software implementers agreements. No release date.
- **IDS 2.0 long-term** — improvements collection ongoing. No release date.
- Software ecosystem visibly growing: ids-lib NuGet package at version 1.0.107 (mature library).
- Our pilot stays on IDS 1.0.

### openCDE

- **Foundation 1.1 stays current.**
- **Documents 1.0 (December 2023) stays current.**
- No 2026 updates visible.
- Open CDE workgroup active but no major release in sight.
- Catenda continues as visible openCDE-native vendor — confirms our positioning instinct.

---

## 6. Strategic Roadmap updates

**Source:** [buildingSMART Strategic Roadmap page](https://www.buildingsmart.org/about/strategic-roadmap/)

### Strategic Projects (active)

- IFC Validation Service — strategic project, ongoing
- IFC X Core (next generation IFC) — active, alpha released
- Process Map and Information Lifecycle Management — call for participation
- openBIM for the Water Sector — call for participation
- Fire Safety Engineering — call for participation
- Regulatory Information Requirements — call for participation

### Recently endorsed

- openCDE Documents API Detailed Project Plan — unanimously endorsed by Standards Committee

### Implication

buildingSMART is actively expanding domain coverage (water, fire, regulatory) and infrastructure (validation service). The CDE / collaboration layer is comparatively stable — which is good for us, because we're building on it without moving-target risk.

---

## 7. New URL / resource map

| Resource | URL | Purpose |
|---|---|---|
| Master IFC 5 course | https://ifc5.technical.buildingsmart.org/ | learn the next generation |
| IFC 5 development repo | https://github.com/buildingSMART/IFC5-development | alpha, examples, working drafts |
| IFC 4.4 development repo | https://github.com/buildingSMART/IFC4.4.x-development | minor semantic-layer update |
| IFC 4.3 documentation | https://ifc43-docs.standards.buildingsmart.org/ | current spec docs |
| ifcx.dev | https://ifcx.dev | JSON schema for IFC 5 (when live) |
| Foundation API | https://github.com/buildingSMART/foundation-API | core CDE API |
| Documents API | https://github.com/buildingSMART/documents-API | documents CDE API |
| Implementers Forum | (via Implementers Assembly page) | IFC 4.3 implementation issues |
| Standards Library | https://www.buildingsmart.org/standards/bsi-standards/standards-library/ | all bSI standards index |
| openBIM Hackathon Porto 2026 | https://www.buildingsmart.org/openbim-hackathon-porto-2026/ | community event |
| InfraBIM Open 2026 Paris | (search bSI events) | June 8–10 Paris event |

---

## 8. What we need to update in our documents

### `STANDARDS-PROFILE.md` section 14 "Future tracking"

Current text:

> - **IFC 4.4.x dev:** extensions of 4.3, in planning phase
> - **IFC 5 dev:** next generation, in development — potentially breaks things

Should become:

> - **IFC 4.4.x dev:** minor semantic-layer update of 4.3, active development at `buildingSMART/IFC4.4.x-development`. No release date.
> - **IFC 5 (alpha released) / IFC X:** next generation. Component-based architecture (ECS), JSON serialization at `ifcx.dev`, USD integration via Alliance for OpenUSD liaison. Alpha repo at `buildingSMART/IFC5-development`. Incremental release — first reduced version, then modules. Not production-ready, no stable date. **Our adapter architecture should leave room for IFC 5 JSON as additional schema target once stable.**

### `KIND-REGISTRY.md`

No changes needed — IFC 5 will need new `schema` tag values once production-ready (likely `IFC5_ALPHA`, `IFC5` later), but pilot stays on `IFC4X3_ADD2`.

### `BRAND.md`

No changes — IFC X naming doesn't affect our Gemeinwert / BIM CVP positioning.

### `_handover/claudecode/specs/STANDARDS-PROFILE.md`

Already copied; re-sync after section 14 update.

### Wiki page `web/wiki/modell/ifc.html`

Update the IFC versions table to add IFC 5 alpha as "released, alpha" and IFC 4.4.x as "active development". Already has placeholder entries for both — only the status field needs the refresh.

---

## 9. Decisions that need Felix's call

1. **Implementers Assembly attendance** — Bagnoli Irpino, Italy, registration open. Strategic value: direct access to ACCA + italian bSI chapter + IFC X discussion. Cost: travel + registration. Decision: go or skip.

2. **IFC 5 contribution** — open repo, alpha stage. We could contribute observations from our Nostr-event perspective (component-based + JSON = our natural fit). Decision: engage actively or watch passively.

3. **USD integration timing for Gemeinwert** — IFC 5 puts USD on the official roadmap. Our USD-Baukasten idea moves from "Phase 3 Vision" to "track buildingSMART progress and align". Decision: dedicate exploration effort or wait until IFC 5 stabilizes.

4. **ifcx.dev monitoring** — JSON schema for IFC 5 will live there. Set up monitoring for when first schemas drop. Decision: who watches.

---

## 10. Bottom line for the pilot

**Nothing in our chosen Standards Profile becomes obsolete.** IFC 4.3.2.0, Reference View 1.2, BCF 3.0, IDS 1.0, OpenCDE 1.1+1.0 stay correct for the Building pilot.

**One important new context emerges:** IFC 5 alpha with USD + JSON + component-based architecture is now public. Our Nostr-event architecture aligns with this direction. This is a strategic tailwind, not a course change.

**Three concrete actions:**

1. Update `STANDARDS-PROFILE.md` section 14 with the IFC 5 alpha specifics (small edit, can be done now).
2. Add an entry to the IFC wiki page acknowledging IFC 5 alpha existence (factual update).
3. Consider Bagnoli Irpino Implementers Assembly attendance as strategic outreach.

**Pilot continues as planned.** This research confirms the foundation rather than disrupting it.

---

## Sources

- [buildingSMART Standards page](https://www.buildingsmart.org/standards/)
- [buildingSMART Technical](https://technical.buildingsmart.org/)
- [Master IFC 5](https://ifc5.technical.buildingsmart.org/)
- [IFC 5 GitHub](https://github.com/buildingSMART/IFC5-development)
- [IFC 4.4.x GitHub](https://github.com/buildingSMART/IFC4.4.x-development)
- [Implementers Assembly Feb 2026 Report](https://www.buildingsmart.org/the-buildingsmart-implementers-assembly-february-2026-event-report/)
- [IDS 1.0 Standard page](https://www.buildingsmart.org/standards/bsi-standards/information-delivery-specification-ids/)
- [BCF Technical page](https://technical.buildingsmart.org/standards/bcf/)
- [BibLus — what is IFC 5](https://biblus.accasoftware.com/en/what-is-ifc-5/)
- [GoTo Archi — IFC 5.0 and OpenUSD](https://goto.archi/blog/post/ifc-50-and-openusd)
- [openCDE Documents API project plan endorsed](https://www.buildingsmart.org/the-opencde-documents-api-detailed-project-plan-has-been-reviewed-and-unanimously-been-endorsed/)

---

*Status: May 2026. Refresh this document after every Implementers Assembly (twice yearly) and when major version bumps land.*
