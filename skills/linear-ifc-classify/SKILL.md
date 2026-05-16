---
name: linear-ifc-classify
description: Automatically classify LINEAR-MEP Revit family types for IFC export — sets IfcExportAs[Type] and IfcExportType[Type] on all HKLS/MEP families using LINEAR's own LIN_CLASSIFICATION_LINEAR shared parameter plus a family-name pattern fallback. Use this skill whenever a user mentions LINEAR (linear.eu), Revit MEP, IFC export, IfcExportAs classification, HKLS/TGA/MEP IFC handover, IDS validation prep, openBIM coordination, MEP family classification, or any workflow where Linear-MEP families need to be exported as proper IFC entities (IfcPipeSegment, IfcValve, IfcAirTerminal, IfcChiller, etc.) instead of generic IfcBuildingElementProxy. Even if the user just says "my Revit MEP IFC export is wrong" or "Linear-Familien werden nicht richtig klassifiziert" — trigger this skill. Especially relevant for Italian, DACH, and Swiss BIM workflows where Capitolato Informativo / IDS validation requires correct IFC classification.
---

# linear-ifc-classify — Linear MEP → IFC classification automaton

## What this skill does

This skill takes a Revit project containing LINEAR-MEP families (HKLS/TGA/MEP from linear.eu) and ensures every family type gets the correct `IfcExportAs[Type]` and `IfcExportType[Type]` (PredefinedType) parameters so that IFC export produces specialised IFC entities (`IfcPipeSegment`, `IfcValve`, `IfcAirTerminal`, `IfcChiller`, `IfcDuctFitting`, etc.) instead of the generic `IfcBuildingElementProxy` fallback.

The classification uses two layers:

1. **Linear's semantic classification** (`LIN_CLASSIFICATION_LINEAR` shared parameter, GUID `a5d2216e-b9ef-4f2c-947e-ea6104db0e78`). Linear annotates its MEP families with values like `Thermal.Movement.Pump`, `Water.Other.VentAndAirAdmittanceValve`, `AirHandling.Safety.FireDamper`. This skill maps each Linear classification to the matching IFC entity + PredefinedType using `assets/linear-to-ifc-mapping.csv` (~92 mappings, IFC4 + IFC4X3 ADD2 compatible).

2. **Family-name pattern fallback** for families that don't carry the Linear parameter — standard Revit family types like `CHW-WL` (cooling tower), `AHU Lufterwärmer`, `Panel Tempering Circuit` (underfloor heating circuit), `L_Bogen` (Linear duct fitting), `Rohrtypen` (generic pipe type), `Rechteck`/`Rund`/`Oval` (duct type names), and Italian abbreviations `GRI-EST`, `ESP`, `RIP-GRI`. Map in `assets/family-to-ifc-mapping.csv` (~45 patterns).

Output: every relevant family type in the project gets two parameters set (`Typ in IFC exportieren als` / `IfcExportAs[Type]` and `Typ Vordefinierter IFC-Typ` / `IfcExportType[Type]`), and a CSV log lists every type with classification source (`linear_class`, `family_pattern:<pattern>`, or `NO_MATCH` / `UNMAPPED` for the manual triage cases).

Typical results on a real Linear-Revit MEP project: ~95 % of 500+ family types classified automatically in 1–2 minutes. The remaining 5 % are standard-Revit equipment families (chillers, AHUs, FBH circuits) — listed for manual classification.

## When to use this skill

Trigger this skill when ANY of these appear in the conversation:

- User mentions LINEAR (linear.eu), liNear Building Solutions, Linear-Familien, Linear-MEP, Linear Desktop für Revit/AutoCAD
- User says their Revit MEP IFC export produces `IfcBuildingElementProxy` instead of proper entities
- User mentions HKLS/TGA/MEP IFC handover, openBIM coordination, IDS validation, Capitolato Informativo
- User talks about `IfcExportAs`, `IfcExportType`, `IfcExportAs[Type]`, "Typ in IFC exportieren als", "Vordefinierter IFC-Typ"
- User mentions Italian Provincial-CDE submission, ACDat, oGI (oggetti generici inventariati), BIM Linee Guida
- User mentions Bonsai / ifctester / IDS / IDS Audit for a Revit-exported IFC
- User says the IFC needs to be IDS-compliant or the validator (ACCA / usBIM / BIMcollab / Solibri / Mailand) is rejecting elements

Don't trigger for:
- ArchiCAD or Allplan workflows (LINEAR mostly Revit/AutoCAD context, though Linear has Allplan too — but this skill is Revit-centric)
- Pure architecture IFCs (no MEP families)
- IFC validation that's not about entity classification (geometry, coordinates, schema validation)

## How the skill works — workflow

The skill assumes Revit is open with the project loaded, the LINEAR Desktop add-on is installed, and Dynamo is available. The Bulk_Classify_IFC script runs inside Dynamo's Python Script node (engine: CPython3).

### Step 1 — Locate or stage the mapping CSVs

The skill bundles two reference mappings:
- `assets/linear-to-ifc-mapping.csv` — LIN_CLASSIFICATION_LINEAR → IFC class
- `assets/family-to-ifc-mapping.csv` — family name pattern → IFC class (fallback)

By default these live in the skill folder. The user can also point the script to project-specific copies in a different folder if they've extended the mappings.

### Step 2 — Open Dynamo and paste the script

In Revit: `Manage → Dynamo`. New workspace. Add a `Python Script` node. Switch the node's engine to **CPython3** (default may be IronPython2 — wrong). Paste the full contents of `scripts/Bulk_Classify_IFC_NoInputs.py`. Adjust the three constants at the top to point at the mapping CSVs and the desired log output path. Add a `Watch` node and wire it to the Python node's output port so the user can see the run summary.

### Step 3 — Dry-run first

The script defaults to `DRY_RUN = True`. Run once. The Watch node shows counts:
- `would_apply via Linear-Klass: NNN`
- `would_apply via Family-Patt: NNN`
- `kein LIN-Klass / no_match: NNN`
- `Linear-Klass UNMAPPED: NNN`
- Plus a CSV log at the configured path with every type, its source, and what would be written.

### Step 4 — Triage and extend

If `UNMAPPED` > 0: Linear classified family types we don't have in the mapping yet. Open the log CSV, filter for status `UNMAPPED`, extract unique `lin_class` values, add them to `linear-to-ifc-mapping.csv`. Run the dry-run again.

If `no_match` (the family fallback found nothing either): add patterns to `family-to-ifc-mapping.csv` to catch them by family-name substring (case-insensitive, first-match-wins). Run again.

Typically 2–3 dry-runs are enough to reach >95 % coverage.

### Step 5 — Production run

Flip the constant `DRY_RUN = False` at the top of the script. Run. The script wraps everything in a single Revit transaction — if anything goes wrong the user can `Ctrl+Z` in the Revit main window and the whole change is reversed.

### Step 6 — Verify and export

Pick a few family types in Revit's Project Browser, open Type Properties — `Typ in IFC exportieren als` and `Typ Vordefinierter IFC-Typ` should be filled. Then proceed with IFC export. The exported IFC should now show specialised entities instead of `IfcBuildingElementProxy`.

For validation: run `ifctester <ids-file> <ifc-file> -r Html -o report.html` to get an HTML audit. Open in browser to see per-element pass/fail.

## Files in this skill

```
linear-ifc-classify/
├── SKILL.md                          (this file)
├── scripts/
│   └── Bulk_Classify_IFC_NoInputs.py (the Dynamo Python script — paste into Dynamo)
├── assets/
│   ├── linear-to-ifc-mapping.csv     (92 Linear classifications → IFC class+predef)
│   └── family-to-ifc-mapping.csv     (45 family-name patterns → IFC class+predef)
└── references/
    ├── ifc4-entity-cheatsheet.md     (which IFC entity + PredefinedType is valid for which MEP component)
    ├── extending-mappings.md         (how to add new entries when a project has unmapped families)
    └── failure-modes.md              (common script errors + fixes — CPython3 engine, transactions, parameter binding)
```

## Read references when

- The script raises `TypeError: property cannot be read` or `NameError` → read `references/failure-modes.md`
- A family type has no mapping and you're not sure which IFC entity is right → read `references/ifc4-entity-cheatsheet.md`
- You're adding patterns for a new naming convention (different CAD tool, different MEP add-on) → read `references/extending-mappings.md`

## Verifying success

After the production run, the user should expect:
- 95–100 % of LINEAR MEP families classified
- Standard-Revit equipment families (chillers, AHU components, FBH circuits) listed in the `NO_LIN_CLASS` log — these typically need 5–20 manual classifications via Revit Type Properties
- IFC export uses specialised entities — verify by opening the exported IFC in Bonsai (BlenderBIM) or any IFC viewer, and checking that pipes appear as `IfcPipeSegment`, pumps as `IfcPump`, etc.

For IDS-validation contexts: the classification is a necessary prerequisite. Pset/Qto properties and classification codes (Prezzario / Uniclass / etc.) are separate concerns and not handled by this skill — they need additional Revit-side parameter setup or post-export annotation.

## Edge cases worth knowing

- **Revit's UI language affects parameter names.** German UI shows `Typ in IFC exportieren als`, English shows `IfcExportAs[Type]`. The script tries both — works in any language.
- **LINEAR_PT_CON Connector helpers** (Linear's virtual connection points) are classified as `IfcVirtualElement` by default. The IFC exporter often omits them entirely, which is fine. If they appear in the IFC, they have no geometry.
- **System Family types** (PipeType, DuctType, PipeInsulationType, DuctInsulationType) don't have the LIN_CLASSIFICATION_LINEAR parameter — they fall through to family-name pattern matching (`Rohrtypen`, `Rechteck`, `Rund`, `Rohrdämmung`, etc.).
- **Italian family-name abbreviations** (`GRI-EST` = Griglia di Espulsione, `ESP` = Espulsione, `RIP-GRI` = Ripresa Griglia) are pre-mapped — extend the family CSV for other regional naming conventions.
- **Bulk classification respects existing values.** If `IfcExportAs[Type]` is already set on a family type, the script does not overwrite — this protects manual work.
