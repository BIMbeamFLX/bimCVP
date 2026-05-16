# Common IDS audit failures and how to fix them

Failure patterns observed across MEP / HKLS projects, mapped to concrete CAD-side fixes. Sorted by frequency (rough estimate from real projects).

## #1 — Pset_*Common properties missing (very common)

**Pattern:** `Property(propertySet=Pset_PipeSegmentCommon; baseName=NominalDiameter)` etc.

**Cause:** The Revit/Archicad/Allplan IFC exporter didn't write the standard buildingSMART property sets. Either the export switch is off, or the CAD parameter names don't match IFC names.

**Fix in Revit:**
1. `File → Export → IFC → Modify Setup → Property Sets`
2. Häkchen **`Export IFC common property sets`** AN
3. Falls einzelne Properties trotzdem leer bleiben: Custom Pset-Datei einbinden, in der das Mapping zwischen Revit-Parametername und IFC-Property-Name spezifiziert ist.

**Fix in Archicad:**
1. `File → Interoperability → IFC → IFC Translators`
2. Wähle / dupliziere passenden Translator (z.B. "General Translator")
3. `Property Mapping for Export` → stelle sicher dass Standard-Psets gemappt sind
4. Falls Properties nicht mit IFC-Namen übereinstimmen: in Property Mapping editor anpassen

**Fix in Allplan:**
1. IFC Export Settings → Property Sets Tab
2. Standard Property Sets aktivieren
3. Optional: Custom Properties Mapping konfigurieren

## #2 — Qto_*BaseQuantities missing (very common)

**Pattern:** `Property(propertySet=Qto_PipeSegmentBaseQuantities; baseName=Length)`, OuterSurfaceArea, GrossWeight, etc.

**Cause:** IFC exporter doesn't write base quantities — typically a single switch.

**Fix in Revit:**
1. `File → Export → IFC → Modify Setup → Property Sets`
2. Häkchen **`Export base quantities`** AN
3. Speichern, neu exportieren

**Fix in Archicad:** Translator → `Geometry Conversion` → `Export Base Quantities` aktivieren.

**Fix in Allplan:** IFC-Settings → Quantities/Mengen → Standard-Mengen aktivieren.

## #3 — Material missing on element types

**Pattern:** `Material()`

**Cause:** Family/Family-Type hat kein Material zugewiesen. Klassischer Linear-Familien-Fehler bei Custom-Templates.

**Fix in Revit:**
1. Pipe Type oder Family-Type öffnen
2. `Edit Type → Identity Data → Material` (oder bei Pipe: `Routing Preferences → Materials per Segment`)
3. Material zuweisen (z.B. "Stahl C-Stahl C235", "PE-X RAUTITAN")

Bei Bulk: Schedule erstellen mit Family + Type + Material, leere Material-Zellen filtern, Material via Schedule eintragen.

## #4 — Classification (Prezzario/Uniclass) missing

**Pattern:** `Classification(system=Prezzario_BZ_2025)` oder ähnlich

**Cause:** IfcClassificationReference wurde nicht im IFC exportiert. Entweder fehlt der Shared Parameter mit dem Code, oder die Classification Settings im IFC-Setup zeigen auf den falschen Parameter.

**Fix in Revit:**
1. Shared Parameter (z.B. `CodicePrezzario_BZ`) am Type-Level binden, alle relevanten Kategorien
2. Wert pro Familientyp füllen (manuell, Schedule, oder via Linear Klassifikations-Werkzeug)
3. `File → Export → IFC → Modify Setup → Classification Settings`
4. Konfigurieren:
   - Source: z.B. "Prezzario Provincia Bolzano 2025"
   - Field Name: `CodicePrezzario_BZ` (Name des Shared Parameters)
5. Neu exportieren

## #5 — Attribute(name=PredefinedType) missing

**Pattern:** `Attribute(name=PredefinedType)`

**Cause:** Familientyp hat keinen IFC-PredefinedType gesetzt. Wird besonders bei nicht-klassifizierten Linear-Familien oder Standard-Revit-Equipment zum Problem.

**Fix in Revit (mit LINEAR Desktop):**
1. `LINEAR Desktop → Werkzeuge → Klassifikation → IFC-Klassifizierung`
2. Familientyp suchen, Spalte `IfcExportAs[Type]` + `IfcExportType[Type]` setzen
3. Anwenden

**Fix in Revit (manuell ohne Linear):**
1. Family Editor öffnen
2. Family Type Properties → IFC parameters
3. `IfcExportAs[Type]` und `IfcExportType[Type]` auf gültige Werte setzen (siehe IFC4 entity cheatsheet)
4. Family neu laden

**Skill-Empfehlung:** Wenn viele Familien zu klassifizieren sind, das `linear-ifc-classify` Skill verwenden — es macht das in einem Dynamo-Lauf bulk.

## #6 — Pset_*.Reference missing

**Pattern:** `Property(propertySet=Pset_PipeSegmentCommon; baseName=Reference)`

**Cause:** `Reference` ist typisch eine LV-Position, Type Mark, oder Hersteller-Code. Wird selten automatisch befüllt.

**Fix:**
1. Shared Parameter `Reference` (oder bestehender Type Mark) an Type binden
2. Pro Familientyp Wert füllen — entweder die LV-Position aus dem Capitolato, oder eine interne Bezugsnummer
3. Custom Pset-Datei einbinden die `Reference` als Type-Property an Pset_*Common bindet (Mapping siehe Pset-Definition-Datei aus dem `linear-ifc-classify` Skill für ein Beispiel)

## #7 — IfcDistributionSystem nicht gesetzt

**Pattern:** Selten direkt als IDS-Fail, aber MEP-Systeme erscheinen als zusammenhangslose Bauteile

**Cause:** Revit System Types haben keine "System Classification" oder die Klassifikation mappt nicht auf IfcDistributionSystem.PredefinedType.

**Fix in Revit:**
1. `Manage → MEP Settings → Mechanical Settings → Pipe/Duct Systems`
2. Pro System Type "System Classification" prüfen (z.B. "Hydronic Supply" → wird zu HEATING im IFC, "Domestic Cold Water" → DOMESTICCOLDWATER, etc.)
3. System Names sauber halten ("H_Vorlauf" statt "Heizung Vorlauf 1") — wird zu IfcDistributionSystem.Name

## #8 — GUID-Instabilität

**Pattern:** Bei wiederholten Exports ändern sich IfcGUIDs, BCF-Markups werden invalide.

**Cause:** Im Revit-IFC-Setup ist "Store IFC GUID in file after export" nicht aktiviert.

**Fix:**
1. `File → Export → IFC → Modify Setup → Advanced/Erweitert`
2. **"Store the IFC GUID in the file after export"** AN
3. Speichern, neu exportieren

Damit werden GUIDs pro Type/Element fixiert und bleiben über Re-Exports stabil.

## #9 — Geometrie-Repräsentation fehlt

**Pattern:** Pset/Qto sind da, aber Bauteile haben keinen sichtbaren Body im IFC-Viewer.

**Cause:** Reference View 1.2 hat Geometrie als Mesh, aber bei extreme Detail-Level oder bei nicht-Geometry-Familien kann der Body leer bleiben.

**Fix:**
1. Setup → Level of Detail / Detailgenauigkeit → "Level of detail for geometry" = **High**
2. Tessellated Geometry as Triangulation = AN
3. Bei nicht-Geometry-Familien (Linear PartialNetworkStart etc.): das ist erwartet, nicht zu fixen

## #10 — Schema-Mismatch IFC4 vs IFC4X3

**Pattern:** IDS verlangt `ifcVersion="IFC4X3_ADD2"` aber IFC ist `IFC4`.

**Cause:** Export war auf IFC4 (häufig — IFC4X3 ADD2 noch nicht überall stabil), IDS verlangt aber 4.3.

**Fix:**
- Entweder IDS auf `ifcVersion="IFC4 IFC4X3_ADD2"` setzen (akzeptiert beide)
- Oder Revit OS-IFC-Exporter neueste Version installieren (unterstützt IFC4X3 ADD2)
- Bei kritischen Übergaben: IFC4 als Default verwenden, 4X3 erst wenn alle Tools im Workflow es können

## Failure-Reihenfolge für Iter-Strategie

Geht man die Top 3 Failures pro Iter an, klappt es typischerweise so:

- **Iter 1:** Klassifikation (PredefinedType + IfcExportAs) → 50-70% der Elemente von "BuildingElementProxy" zu spezifischen Klassen
- **Iter 2:** Common Psets + Base Quantities aktivieren → 70-85% pass
- **Iter 3:** Material + Reference befüllen → 85-95% pass  
- **Iter 4:** Classification-Codes (Prezzario etc.) befüllen → 90-98% pass
- **Iter 5:** Edge cases manuell — 95-100%

Pro Iter typisch 30-60 Min Aufwand auf der CAD-Seite + 5 Min für Audit-Re-Run.
