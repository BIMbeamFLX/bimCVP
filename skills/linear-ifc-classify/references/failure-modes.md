# Failure modes and fixes

Common errors when running `Bulk_Classify_IFC_NoInputs.py` inside Dynamo, and what to do.

## Setup-level errors

### Python engine is wrong

**Symptom:** `ModuleNotFoundError: No module named 'RevitServices'` or `ImportError` for any of the IFC/Revit modules.

**Fix:** The Python Script node must use **CPython3**, not IronPython2. Change at the bottom-right corner of the node header. The script uses Python 3 syntax (f-strings, `with open(..., encoding="utf-8")`) that breaks in IronPython2.

### CSV not found

**Symptom:** `IOError: Mapping CSV not found: <path>`

**Fix:** The path constant at the top of the script points to a file that doesn't exist. Either:
- Adjust the `MAPPING_CSV` and `FAMILY_CSV` constants in the script to the actual paths on the machine
- Copy the bundled CSVs from `<skill>/assets/` to the configured paths

### Family CSV missing (Linear class only)

**Symptom:** Script runs, but `Family mapping: 0 patterns` in the summary. Many `no_match` entries.

**Fix:** `FAMILY_CSV` constant points to a file that doesn't exist. The script tolerates this (returns empty mapping) but falls back to Linear-only classification. Fix the path.

## Runtime errors (CPython3 / pythonnet specifics)

### `TypeError: property cannot be read`

**Symptom:** Stack trace points to `read_param_string` or `set_param_string`, mentions `StorageType`.

**Fix:** In pythonnet, `.NET` enum properties (`Parameter.StorageType`) cannot be compared via `.ToString()` reliably. The script uses direct enum comparison: `if p.StorageType != StorageType.String`. If this still breaks, your IFC-for-Revit version may shadow the parameter type — confirm the `StorageType` import is from `Autodesk.Revit.DB`.

### `NameError: name 'type_name' is not defined`

**Symptom:** Stack trace inside the loop's exception handler.

**Fix:** The script pre-initialises loop variables (`fam_name`, `type_name`, `cat_name`, `lin_value`) before each iteration's `try` block, exactly to avoid this. If it still happens, an earlier version is loaded — re-paste the current `Bulk_Classify_IFC_NoInputs.py` content.

### Transaction errors

**Symptom:** `InvalidOperationException: The transaction does not have a started status` or similar Revit transaction state errors.

**Fix:** This usually means a previous run was aborted mid-transaction. Close Dynamo (don't save), reopen, paste the script fresh. Production run wraps everything in a single `EnsureInTransaction`/`TransactionTaskDone` pair — if interrupted, manual cleanup may be needed via Revit's undo or by closing without saving.

### Some types skipped with `PARAM_MISSING`

**Symptom:** Log CSV shows status `PARAM_MISSING` for some types — the script found a Linear class and a target IFC mapping but couldn't find the `IfcExportAs[Type]` parameter to write.

**Cause:** The family was built without the IFC parameters bound. Common for very old Linear families or for custom families authored without IFC awareness.

**Fix:** Open the family in the Family Editor (`Edit Family`), use `Manage → Project Parameters` or `Manage → Family Types` to bind the shared parameters `IfcExportAs` and `IfcExportType` (and `IfcExportAs[Type]` / `IfcExportType[Type]` for type binding) to the family's category. Save and reload into the project. Re-run dry-run.

## Result anomalies

### `applicable == failed` in IDS validation downstream

**Symptom:** After running the script and exporting IFC, the IDS validation shows every element as failing — even though classification looks right.

**Diagnostic:** The IDS spec probably checks for `Pset_*Common` properties that aren't enabled in the IFC export. Open `File → Export → IFC → Modify Setup → Property Sets` and ensure:
- `Export IFC common property sets` is ON
- `Export base quantities` is ON

Classification alone doesn't fill Psets — they need the export switches.

### Pipe Types have `0 pass` even though classification is set

**Symptom:** All IfcPipeSegment elements fail the IDS check.

**Diagnostic:** Revit's Pipe Type doesn't expose `IfcExportAs[Type]` directly on the Type — it's only at instance level for Pipe Curves. Linear's families typically work because they're Loadable Families, but System Family pipes (the `Rohrtypen` family) need different handling. The family-name pattern `Rohrtypen` → `IfcPipeSegment` ensures the type-level IfcExportAs is set, but Revit may still export pipe instances based on the System Type configuration in Mechanical Settings.

**Fix:** Verify the System Classification per pipe system in `Manage → MEP Settings → Mechanical Settings → Pipe Settings`. Each system type maps to an `IfcDistributionSystem PredefinedType` (Hydronic Supply → HEATING, etc.) — without this, instance-level IFC export may default to proxies regardless of type classification.

### Pumps / cooling towers classified but not in IFC

**Symptom:** Script log shows successful classification for `CHW-WL` family but the exported IFC has no `IfcChiller` entities.

**Diagnostic:** Standard Revit equipment families sometimes need `IfcExportAs` set on BOTH the Type AND the Instance level. The script only sets Type. Some Revit IFC exporter versions take the Type value, others only the Instance.

**Fix:** In the family, define both parameters as Type-bound — that way they cascade to instances automatically. Or add a second pass to the script that propagates Type values to all instances of that type. Or: in the IFC export setup, check that "Use IFC mapping table" is configured with `IfcExportAs` lookup.

## Performance

- Loading 60 MB IFC into ifcopenshell takes 4–8 seconds
- IDS validation of 15.000 elements takes 6–10 seconds with ifctester
- The Bulk_Classify script runs through 500+ family types in <30 seconds typically
- 1 GB+ IFCs (Linear full-detail mode): expect 30–90 seconds for ifcopenshell load alone — use `Lean` export setup (Detail Medium + omit Insulations) to keep IFC under 100 MB

If something runs >5 minutes in Dynamo without producing output: something is hanging. Kill Dynamo, restart Revit, try again.
