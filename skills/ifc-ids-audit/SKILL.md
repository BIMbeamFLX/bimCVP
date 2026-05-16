---
name: ifc-ids-audit
description: Validate an IFC model against an IDS (Information Delivery Specification) and produce a prioritised, actionable fix list. Use this skill whenever a user mentions IDS validation, IDS audit, ifctester, Bonsai IDS check, BlenderBIM audit, buildingSMART IDS Audit Tool, usBIM.IDSeditor, Solibri IDS, BIMcollab IDS, openBIM quality check, model audit, Capitolato Informativo compliance check, BIM Linee Guida validation, oGI verification, or asks "is my IFC compliant", "does my model pass the standard", "what is wrong with my IFC file". Also trigger when a user has both an .ifc and .ids file and wants to know the gap, or when iterating on a model to reach IDS-green status. Particularly relevant when a Capitolato or Auftraggeber requires IDS conformity for handover.
---

# ifc-ids-audit — IDS validation with prioritised triage

## What this skill does

Runs an IDS (Information Delivery Specification, buildingSMART standard, IDS 1.0 published June 2024) audit against an IFC model and produces:

1. **A machine-readable summary** — pass/fail per specification, total counts
2. **A human-readable HTML report** — detailed per-element failures, openable in any browser
3. **A prioritised fix list** — common failure patterns grouped, with concrete remediation actions ranked by impact (how many elements each fix unlocks)

The skill uses `ifctester` (Python CLI from the ifcopenshell stack) under the hood. ifctester is the reference implementation of IDS validation, used by buildingSMART, Bonsai/BlenderBIM, and many CDE platforms.

## When to use this skill

Trigger this skill when ANY of these appear:

- User has an `.ifc` file AND an `.ids` file and wants to know the compliance gap
- User mentions `ifctester`, Bonsai IDS audit, BlenderBIM IDS check, BlenderBIM model quality
- User mentions buildingSMART IDS Audit Tool, usBIM.IDSeditor, Solibri IDS, BIMcollab IDS, Catenda IDS
- User asks "is my IFC IDS-compliant?", "does my model pass?", "what is failing?", "how do I get the IDS green?"
- User is iterating on a Revit / Archicad / Allplan model and needs to validate the export
- User mentions Capitolato Informativo / Bauherrenanforderungen / BIM Linee Guida / oGI compliance
- User is preparing an openBIM handover and the receiving party requires IDS conformity
- User shows an IDS-Report with many failures and asks "what should I fix first?"

Don't trigger for:
- Pure IFC schema validation (not IDS — that's `ifcvalidator`, different tool)
- IFC viewing or geometry inspection (use Bonsai / BIMvision / Solibri directly)
- IDS authoring / writing new IDS specifications from scratch (separate workflow)
- BCF (Building Collaboration Format) — different standard

## How the skill works — workflow

The skill is designed to be runnable headless (no GUI needed) and produces files the user can read in their normal editor / browser. It works equally well in Cowork, Claude Code, or a remote SSH session.

### Step 1 — Ensure ifctester is installed

The skill bundles a small Python script that pip-installs ifctester if not present:

```bash
pip install ifctester ifcopenshell lark --break-system-packages --quiet
```

(The `--break-system-packages` flag is for newer pip versions on managed Python environments. Drop it if working inside a venv.)

### Step 2 — Validate the IDS file is loadable

Before the actual audit, the skill checks the IDS file parses correctly. Common IDS-author errors:

- Invalid attributes on `<specification>` like `minOccurs="1" maxOccurs="unbounded"` — these are NOT in the IDS 1.0 schema, only `cardinality` on facets is valid
- Old `<applicability minOccurs="1">` — also not in IDS 1.0
- PropertySet/baseName outside `<simpleValue>` wrapper

If the IDS fails to load, the skill reports the schema validation error and points the user at `references/ids-spec-format.md` for the IDS 1.0 syntax rules.

### Step 3 — Run the audit

Invokes the bundled `scripts/run_audit.py` which:
1. Opens the IFC with ifcopenshell (fast for ≤200 MB, slow for >500 MB)
2. Loads the IDS
3. Runs `specs.validate(ifc)`
4. Writes three outputs to a configurable directory:
   - `audit_summary.txt` — text overview, per-spec counts
   - `report.html` — full HTML report (openable in browser)
   - `triage.csv` — per-specification failure-pattern aggregation

### Step 4 — Generate the prioritised fix list

The bundled `scripts/triage_audit.py` reads the audit results and produces a ranked list of fix actions, grouped by failure pattern. Each entry shows:
- Failure pattern (e.g., *"Pset_PipeSegmentCommon.NominalDiameter missing"*)
- Affected element count
- Affected specifications
- Recommended fix action (concrete: *"Enable 'Export IFC common property sets' in Revit IFC Export Setup"*)
- Source-of-Truth check (whether the value should come from CAD, from a Pset definition file, from manual entry)

This is what the user actually acts on. The HTML report is for visual deep-dive, the triage list is for *"what do I do next".*

### Step 5 — Iterate

After the user makes the fix (in Revit / Archicad / Allplan), they re-export the IFC and re-run the audit. Each iteration moves the count down. Typically 3–5 iterations to reach green status.

## Files in this skill

```
ifc-ids-audit/
├── SKILL.md                          (this file)
├── scripts/
│   ├── run_audit.py                  (validates IDS, runs ifctester, writes 3 outputs)
│   └── triage_audit.py               (reads audit, produces prioritised fix list)
└── references/
    ├── ids-spec-format.md            (IDS 1.0 syntax — required for fixing invalid IDS files)
    ├── common-failures.md            (common failure patterns + their Revit/Archicad/Allplan fixes)
    └── validators-comparison.md      (when to use ifctester vs Bonsai vs Solibri vs bSI tool)
```

## Read references when

- IDS file won't load with schema error → `references/ids-spec-format.md`
- Audit shows specific failure pattern and the user asks "how do I fix this" → `references/common-failures.md`
- User asks which validation tool to use, or wants to cross-check with another tool → `references/validators-comparison.md`

## Usage example

```bash
# Install dependencies (once)
pip install ifctester ifcopenshell lark --break-system-packages --quiet

# Run the audit
python scripts/run_audit.py \
    --ifc /path/to/model.ifc \
    --ids /path/to/spec.ids \
    --out /path/to/audit-results/

# Inspect the prioritised fix list
python scripts/triage_audit.py /path/to/audit-results/

# Open the HTML report
xdg-open /path/to/audit-results/report.html  # Linux
open /path/to/audit-results/report.html      # macOS
start /path/to/audit-results/report.html     # Windows
```

For Revit users who want to validate without leaving Bonsai: also include a one-liner pointing at the file paths in Bonsai's IDS Audit panel — see `references/validators-comparison.md`.

## Performance expectations

| IFC size | Load time | Validate time | Total |
|---|---|---|---|
| 10–50 MB | <2 s | <5 s | <10 s |
| 50–200 MB | 2–10 s | 5–30 s | 10–60 s |
| 200 MB–1 GB | 10–60 s | 30 s–5 min | 1–10 min |
| >1 GB | flatten first | n/a | n/a |

For >1 GB IFC (typical for Linear-full-detail MEP exports with full geometry + insulations): the skill will warn and recommend re-exporting with reduced detail before auditing — large IFCs aren't a validation problem, they're a CDE/handover problem and need to be addressed upstream.

## Edge cases

- **IDS schema errors**: if the IDS itself doesn't parse against IDS 1.0 schema, the audit can't run. The skill detects this case early and shows the schema validation error with line/column. Common cause: hand-written IDS files using attributes from older drafts of the spec.
- **Empty specifications**: if a spec's applicability matches zero elements in the IFC (e.g., spec requires `IfcCovering` but model has none), it shows `applicable=0`. This is neither pass nor fail — flag in the summary as "no applicable elements".
- **Set vs list returns**: ifctester's `failed_entities` attribute returns a `set`, not a list — the triage script handles both via `list()` conversion.
- **Unicode in IDS values**: works in Python 3 / CPython3, but be careful with Windows-PowerShell encoding when piping output.

## Output formats

- `audit_summary.txt`: plain text, 50-100 lines, human readable
- `report.html`: ~1 MB for 15k-element IFC, openable in any browser, uses standard ifctester HTML template
- `triage.csv`: 1 row per failure pattern, sortable by impact, columns: `pattern`, `affected_count`, `affected_specs`, `recommended_fix`, `fix_source`

Optionally: `report.json` for programmatic post-processing — but be aware that ifctester's JSON output can be very large (40+ MB for a 15k-element IFC) and the JSON writer occasionally truncates for very large outputs. Use HTML + triage.csv as the primary interface.
