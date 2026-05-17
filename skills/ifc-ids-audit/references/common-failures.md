# Common IDS audit failures and how to fix them

Failure patterns observed across MEP / HKLS projects, mapped to concrete CAD-side fixes. Sorted by frequency (rough estimate from real projects).

## #1 — Pset_*Common properties missing (very common)

**Pattern:** `Property(propertySet=Pset_PipeSegmentCommon; baseName=NominalDiameter)` etc.

**Cause:** The Revit/Archicad/Allplan IFC exporter didn't write the standard buildingSMART property sets. Either the export switch is off, or the CAD parameter names don't match IFC names.

**Fix in Revit:**
1. `File → Export → IFC → Modify Setup → Property Sets`
2. Check **`Export IFC common property sets`** ON
3. If individual properties still stay empty: include a custom Pset file that specifies the mapping between the Revit parameter name and the IFC property name.

**Fix in Archicad:**
1. `File → Interoperability → IFC → IFC Translators`
2. Select / duplicate a suitable translator (e.g. "General Translator")
3. `Property Mapping for Export` → make sure standard Psets are mapped
4. If properties don't match the IFC names: adjust in the Property Mapping editor

**Fix in Allplan:**
1. IFC Export Settings → Property Sets tab
2. Enable standard property sets
3. Optional: configure custom properties mapping

## #2 — Qto_*BaseQuantities missing (very common)

**Pattern:** `Property(propertySet=Qto_PipeSegmentBaseQuantities; baseName=Length)`, OuterSurfaceArea, GrossWeight, etc.

**Cause:** IFC exporter doesn't write base quantities — typically a single switch.

**Fix in Revit:**
1. `File → Export → IFC → Modify Setup → Property Sets`
2. Check **`Export base quantities`** ON
3. Save, re-export

**Fix in Archicad:** Translator → `Geometry Conversion` → enable `Export Base Quantities`.

**Fix in Allplan:** IFC Settings → Quantities → enable standard quantities.

## #3 — Material missing on element types

**Pattern:** `Material()`

**Cause:** Family/family type has no material assigned. A classic Linear-family error with custom templates.

**Fix in Revit:**
1. Open the pipe type or family type
2. `Edit Type → Identity Data → Material` (or for pipes: `Routing Preferences → Materials per Segment`)
3. Assign a material (e.g. "Steel C-steel C235", "PE-X RAUTITAN")

In bulk: create a schedule with family + type + material, filter empty material cells, enter the material via the schedule.

## #4 — Classification (Prezzario/Uniclass) missing

**Pattern:** `Classification(system=Prezzario_BZ_2025)` or similar

**Cause:** IfcClassificationReference was not exported in the IFC. Either the shared parameter holding the code is missing, or the Classification Settings in the IFC setup point to the wrong parameter.

**Fix in Revit:**
1. Bind a shared parameter (e.g. `CodicePrezzario_BZ`) at type level, for all relevant categories
2. Fill the value per family type (manually, via schedule, or via the Linear classification tool)
3. `File → Export → IFC → Modify Setup → Classification Settings`
4. Configure:
   - Source: e.g. "Prezzario Provincia Bolzano 2025"
   - Field Name: `CodicePrezzario_BZ` (name of the shared parameter)
5. Re-export

## #5 — Attribute(name=PredefinedType) missing

**Pattern:** `Attribute(name=PredefinedType)`

**Cause:** Family type has no IFC PredefinedType set. This becomes a problem especially with unclassified Linear families or standard Revit equipment.

**Fix in Revit (with LINEAR Desktop):**
1. `LINEAR Desktop → Tools → Classification → IFC classification`
2. Find the family type, set the `IfcExportAs[Type]` + `IfcExportType[Type]` columns
3. Apply

**Fix in Revit (manually, without Linear):**
1. Open the Family Editor
2. Family Type Properties → IFC parameters
3. Set `IfcExportAs[Type]` and `IfcExportType[Type]` to valid values (see IFC4 entity cheatsheet)
4. Reload the family

**Skill recommendation:** If many families need classifying, use the `linear-ifc-classify` skill — it does this in bulk in a single Dynamo run.

## #6 — Pset_*.Reference missing

**Pattern:** `Property(propertySet=Pset_PipeSegmentCommon; baseName=Reference)`

**Cause:** `Reference` is typically a bill-of-quantities position, Type Mark, or manufacturer code. It is rarely filled automatically.

**Fix:**
1. Bind the shared parameter `Reference` (or an existing Type Mark) to the type
2. Fill the value per family type — either the bill-of-quantities position from the Capitolato, or an internal reference number
3. Include a custom Pset file that binds `Reference` as a type property to Pset_*Common (for an example mapping, see the Pset definition file from the `linear-ifc-classify` skill)

## #7 — IfcDistributionSystem not set

**Pattern:** Rarely a direct IDS fail, but MEP systems appear as disconnected components

**Cause:** Revit system types have no "System Classification", or the classification doesn't map to IfcDistributionSystem.PredefinedType.

**Fix in Revit:**
1. `Manage → MEP Settings → Mechanical Settings → Pipe/Duct Systems`
2. Check "System Classification" per system type (e.g. "Hydronic Supply" → becomes HEATING in the IFC, "Domestic Cold Water" → DOMESTICCOLDWATER, etc.)
3. Keep system names clean ("H_Supply" instead of "Heating Supply 1") — becomes IfcDistributionSystem.Name

## #8 — GUID instability

**Pattern:** On repeated exports the IfcGUIDs change, BCF markups become invalid.

**Cause:** In the Revit IFC setup, "Store IFC GUID in file after export" is not enabled.

**Fix:**
1. `File → Export → IFC → Modify Setup → Advanced`
2. **"Store the IFC GUID in the file after export"** ON
3. Save, re-export

This fixes GUIDs per type/element and keeps them stable across re-exports.

## #9 — Geometry representation missing

**Pattern:** Pset/Qto are present, but components have no visible body in the IFC viewer.

**Cause:** Reference View 1.2 has geometry as mesh, but at extreme detail levels or for non-geometry families the body can stay empty.

**Fix:**
1. Setup → Level of Detail → "Level of detail for geometry" = **High**
2. Tessellated Geometry as Triangulation = ON
3. For non-geometry families (Linear PartialNetworkStart etc.): this is expected, nothing to fix

## #10 — Schema-Mismatch IFC4 vs IFC4X3

**Pattern:** IDS verlangt `ifcVersion="IFC4X3_ADD2"` aber IFC ist `IFC4`.

**Cause:** Export was to IFC4 (common — IFC4X3 ADD2 not yet stable everywhere), but the IDS requires 4.3.

**Fix:**
- Either set the IDS to `ifcVersion="IFC4 IFC4X3_ADD2"` (accepts both)
- Or install the latest version of the Revit open-source IFC exporter (supports IFC4X3 ADD2)
- For critical handovers: use IFC4 as the default, switch to 4X3 only when all tools in the workflow can handle it

## Failure order for the iteration strategy

Tackling the top 3 failures per iteration, it typically goes like this:

- **Iter 1:** Classification (PredefinedType + IfcExportAs) → 50-70% of elements from "BuildingElementProxy" to specific classes
- **Iter 2:** Enable common Psets + base quantities → 70-85% pass
- **Iter 3:** Fill material + reference → 85-95% pass
- **Iter 4:** Fill classification codes (Prezzario etc.) → 90-98% pass
- **Iter 5:** Edge cases manually — 95-100%

Per iteration typically 30-60 min effort on the CAD side + 5 min for the audit re-run.
