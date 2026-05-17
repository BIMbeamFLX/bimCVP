# Choosing the right IDS validator

There are five mainstream IDS-1.0-compatible validators. Different strengths.

## ifctester (CLI / Python)

**What it is:** Reference implementation of IDS validation, part of the ifcopenshell ecosystem.

**Pro:**
- Open source, MIT licensed
- Fastest at scale (validates 15k-element IFC in <10 sec)
- Scriptable — can run in CI, automated pipelines, batch jobs
- Produces HTML report + JSON for programmatic post-processing
- Standardised output format (other tools mostly compatible)

**Con:**
- CLI / API only, no GUI
- Requires Python install (`pip install ifctester ifcopenshell lark`)
- HTML report is functional but not pretty
- For very large IFC (>1 GB) the JSON output can truncate — use HTML + triage-CSV

**Use when:**
- Automating IDS validation (CI, every commit, every CDE upload)
- Validating multiple IFCs against the same IDS
- Producing audit reports programmatically
- Working in headless environments (servers, Cowork, remote SSH)

**Used by this skill** as the underlying engine.

## Bonsai (BlenderBIM Add-on for Blender)

**What it is:** Open source BIM Authoring suite as Blender add-on. Includes full IDS validation.

**Pro:**
- Free, open source, cross-platform
- Visual feedback — click on a failed element to see it in 3D
- Both IDS authoring + validation in one tool
- Industry-standard for openBIM workflows
- Active community development

**Con:**
- Requires Blender install
- For large IFC (>500 MB) Blender becomes sluggish
- Not designed for batch / CI workflows
- IDS validation UI is functional but not optimised for huge result sets

**Use when:**
- Visual deep-dive into a failed element ("which is the actual pipe segment failing?")
- IDS authoring with live validation feedback
- Demo / training context
- Manual project work where you want to see geometry + validation together

## buildingSMART IDS Audit Tool (online)

**What it is:** Official online validator from buildingSMART. https://www.buildingsmart.org/users/services/ids-audit-tool/

**Pro:**
- No install needed, browser-based
- Official reference implementation status
- Output report carries buildingSMART branding (good for handovers)
- Easy to share results (URL or PDF export)

**Con:**
- File upload required (problematic for confidential projects)
- File size limits (typically 100-500 MB)
- Slower than CLI for large files (network upload + remote processing)
- No batch mode

**Use when:**
- Sharing audit results with external parties (architect, client, validator) — official badge
- Quick one-off check without installing anything
- Project allows cloud upload
- Need to convince a skeptical stakeholder ("here is the official tool")

## usBIM.IDSeditor (ACCA, free)

**What it is:** Visual IDS authoring + validation tool from ACCA software (an Italian BIM software vendor).

**Pro:**
- Free download
- Visual IDS author with form-based editing (no XML knowledge needed)
- Integrated with rest of usBIM ecosystem
- Good Italian-localised UX for Italian Capitolato workflows

**Con:**
- ACCA ecosystem lock-in tendency
- Less mainstream than Bonsai or the online tool
- Windows-centric

**Use when:**
- Italian project context, especially with ACCA usBIM downstream
- Author IDS without writing XML
- Italian-localised workflow needed

## Solibri Office (commercial)

**What it is:** Major commercial BIM quality checker. Pre-dated IDS but added IDS support.

**Pro:**
- Most polished UI / Reports
- Combines IDS validation with model-checking (clashes, code compliance)
- Used by large enterprises and public authorities
- Strong support, training, certified workflows

**Con:**
- Expensive (license in the four-figure range)
- Closed source
- Overkill for IDS validation alone
- IDS implementation sometimes extended in Solibri-specific ways

**Use when:**
- Already using Solibri for clash / model checking → IDS as an additional layer
- Large corporation / public client with a Solibri license
- Complex multi-discipline coordination beyond IDS

## Combinations that work well

**Bimbeam standard for building-type projects:**
- **ifctester** for auto-audit on every re-export (5 sec, in CI)
- **Bonsai** for visual inspection of individual failures
- **buildingSMART IDS Audit Tool** for the final handover validation (badge on the delivery note)

**Italian Capitolato workflow:**
- **usBIM.IDSeditor** for IDS authoring (Italian UI)
- **ifctester** for the audit loop
- **buildingSMART** for Capitolato compliance evidence

**DACH architecture-office standard:**
- **Bonsai** for everything (free, complete, visual)
- ifctester only if CI is desired

## Compatibility Notes

All five tools use the official IDS 1.0 XSD schema definition. An IDS file that works with one tool should work with all of them.

Exceptions / edge cases:
- usBIM.IDSeditor sometimes exports with small ACCA extensions that other tools ignore with a warning
- Solibri historically had its own "Quality Information" language; IDS support is newer and sometimes lags a version behind
- ifctester is always at the latest state of the buildingSMART spec

For handovers: ideally use **the same tool chain as the validator**. If the province uses Solibri, run your own validation in Solibri as well — even if ifctester says "green", Solibri's interpretation can differ slightly.
