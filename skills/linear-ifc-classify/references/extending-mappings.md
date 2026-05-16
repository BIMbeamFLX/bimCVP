# Extending the mapping CSVs

The two mapping CSVs are versioned assets and meant to grow with each project. The goal: every new Linear classification or family naming convention you encounter feeds back into the asset, so the next project starts further along.

## When to extend `linear-to-ifc-mapping.csv`

After a dry-run, look at the log CSV for rows with `status=UNMAPPED`. The `lin_class` column shows what Linear classified the family as. If you recognise it as a real component, add a row.

CSV columns:
- `LIN_CLASSIFICATION_LINEAR` — the value Linear writes into its shared parameter (exact match, case-sensitive)
- `IfcExportAs` — the IFC entity to set on the type
- `IfcExportType` — the PredefinedType (or empty if entity has no enum)
- `PredefinedType_kommentar` — free-text comment for humans

Example row:
```
Thermal.Movement.PumpEndSuction,IfcPump,ENDSUCTION,Kreiselpumpe endgesaugt
```

Validate the PredefinedType against `references/ifc4-entity-cheatsheet.md` before adding — IFC4 enum values are strict, anything outside the list breaks the export.

If you can't find a good PredefinedType, use `NOTDEFINED` and add a note. Better empty than wrong.

## When to extend `family-to-ifc-mapping.csv`

When a family type has no LIN_CLASSIFICATION_LINEAR value, the script falls back to family-name pattern matching. Add patterns for:
- Standard-Revit equipment families that Linear doesn't classify (chillers, cooling towers, generic mechanical equipment)
- Project-specific custom families with consistent naming
- Regional naming conventions (Italian `GRI-EST`/`ESP`, Swiss/Austrian conventions, etc.)
- Linear's own system-family helpers (`L_Bogen`, `L_Stutzen`, `Rohrtypen`, `Rechteck`, `Rund`)

CSV columns:
- `family_pattern` — substring to search in family name OR type name (case-insensitive)
- `IfcExportAs`, `IfcExportType`, `kommentar` — as above

Matching is **first-match-wins** in CSV order. Put more specific patterns ABOVE less specific ones. Example: `Panel Tempering Circuit` must come before any pattern like `Panel` alone.

Patterns are substring matches, so `L_Bogen` matches `L_Bogen_BGE_BGF`, `L_Bogen_Vertikal_Oval`, etc. Good for the L_*-prefix Linear convention.

## When NOT to extend

Skip these as patterns/mappings — they're better handled manually:

- One-off custom families used in a single project (just classify by hand in Type Properties)
- Families with ambiguous IFC mapping (`MIXING` valve vs `REGULATING` valve depending on use) — let humans decide
- Virtual / connector elements Linear adds for its own logic (`PartialNetworkStart`, `Port`) — keep as `IfcVirtualElement` so they're either exported as virtuals or skipped entirely

## Workflow for adding mappings

1. Run dry-run, get the log CSV
2. Filter `status` = `UNMAPPED` (for Linear classes) or `NO_MATCH` (for unmatched families)
3. Group by unique `lin_class` / `family` — focus on the high-count entries first
4. For each: decide the right IFC entity (consult cheatsheet)
5. Add row to the appropriate CSV
6. Re-run dry-run — the previously-flagged types should now show as `WOULD_APPLY`
7. Repeat until the residual `NO_MATCH` / `UNMAPPED` count is low enough (<5 % is fine)
8. Production run

## Committing changes back

The mapping CSVs are bundled with the skill in `assets/`. If you've extended them substantially during a project, copy the modified CSVs back into the skill folder so the next project benefits. This is the asset accretion logic: every project makes the next one faster.

For openBIM projects with diverse non-LINEAR family naming, consider maintaining a project-local copy of `family-to-ifc-mapping.csv` that extends (not replaces) the skill default. The script takes the CSV path as input — point it at the project copy.
