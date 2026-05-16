# IDS 1.0 syntax — the parts most often broken

IDS = Information Delivery Specification, published as buildingSMART standard, version 1.0, June 2024. Defines required properties on IFC elements that can be machine-validated.

## Required top-level structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ids xmlns="http://standards.buildingsmart.org/IDS"
     xmlns:xs="http://www.w3.org/2001/XMLSchema"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="http://standards.buildingsmart.org/IDS
                         http://standards.buildingsmart.org/IDS/1.0/ids.xsd">
  <info>
    <title>...</title>
    <version>...</version>
    <description>...</description>
    <author>...@...</author>
    <date>YYYY-MM-DD</date>
    <purpose>...</purpose>
    <milestone>...</milestone>
  </info>
  <specifications>
    <specification ifcVersion="IFC4 IFC4X3_ADD2"
                   name="..."
                   identifier="..."
                   description="..."
                   instructions="...">
      <applicability>
        <entity><name><simpleValue>IFCPIPESEGMENT</simpleValue></name></entity>
      </applicability>
      <requirements>
        ...facets...
      </requirements>
    </specification>
  </specifications>
</ids>
```

## Common mistakes that break the parser

### Mistake 1 — minOccurs / maxOccurs on `<specification>`

```xml
<!-- WRONG -->
<specification minOccurs="1" maxOccurs="unbounded" ifcVersion="IFC4" name="...">

<!-- RIGHT -->
<specification ifcVersion="IFC4" name="...">
```

`minOccurs` and `maxOccurs` are NOT valid attributes on `<specification>` in IDS 1.0. They were in earlier drafts. If you see them in older IDS files, strip them.

### Mistake 2 — minOccurs on `<applicability>`

```xml
<!-- WRONG -->
<applicability minOccurs="1">
  <entity>...</entity>
</applicability>

<!-- RIGHT -->
<applicability>
  <entity>...</entity>
</applicability>
```

Same as above. The `minOccurs` attribute on applicability was a draft feature, removed in IDS 1.0.

### Mistake 3 — Cardinality on facets is required in `<requirements>`

```xml
<!-- WRONG (no cardinality) -->
<requirements>
  <material/>
  <property dataType="IFCLABEL">
    <propertySet><simpleValue>Pset_Foo</simpleValue></propertySet>
    <baseName><simpleValue>Bar</simpleValue></baseName>
  </property>
</requirements>

<!-- RIGHT -->
<requirements>
  <material cardinality="required"/>
  <property cardinality="required" dataType="IFCLABEL">
    <propertySet><simpleValue>Pset_Foo</simpleValue></propertySet>
    <baseName><simpleValue>Bar</simpleValue></baseName>
  </property>
</requirements>
```

In `<requirements>` blocks, every facet (`entity`, `attribute`, `classification`, `property`, `material`, `partOf`) MUST have a `cardinality` attribute. Values: `required` / `optional` / `prohibited`.

Note: in `<applicability>` blocks, facets do NOT take cardinality (applicability just defines "matches what entities").

### Mistake 4 — Values not wrapped in `<simpleValue>`

```xml
<!-- WRONG -->
<entity>
  <name>IFCPIPESEGMENT</name>
</entity>

<!-- RIGHT -->
<entity>
  <name><simpleValue>IFCPIPESEGMENT</simpleValue></name>
</entity>
```

Most facet values (entity name, property propertySet/baseName, classification system/value, etc.) need to be wrapped in either `<simpleValue>` (single value) or `<xs:restriction>` (regex / enumeration). Bare text content is not allowed.

### Mistake 5 — predefinedType on entity facet

```xml
<entity>
  <name><simpleValue>IFCCOVERING</simpleValue></name>
  <predefinedType><simpleValue>INSULATION</simpleValue></predefinedType>
</entity>
```

This IS valid syntax. Used when you want the spec to apply only to a sub-type of an entity (e.g. only IfcCovering instances with PredefinedType=INSULATION). The `<predefinedType>` element comes AFTER `<name>` inside `<entity>`.

### Mistake 6 — dataType attribute on property facet

```xml
<!-- WRONG -->
<property cardinality="required">
  <propertySet><simpleValue>Pset_X</simpleValue></propertySet>
  <baseName><simpleValue>Y</simpleValue></baseName>
</property>

<!-- RIGHT -->
<property cardinality="required" dataType="IFCLABEL">
  ...
</property>
```

`dataType` is required on `<property>` in `<requirements>`. Values are IFC type names: `IFCLABEL`, `IFCTEXT`, `IFCIDENTIFIER`, `IFCBOOLEAN`, `IFCINTEGER`, `IFCREAL`, `IFCLENGTHMEASURE`, `IFCPOSITIVELENGTHMEASURE`, `IFCAREAMEASURE`, `IFCVOLUMEMEASURE`, `IFCMASSMEASURE`, `IFCQUANTITYLENGTH`, `IFCQUANTITYAREA`, `IFCQUANTITYVOLUME`, `IFCQUANTITYWEIGHT`, `IFCQUANTITYCOUNT`, `IFCPRESSUREMEASURE`, `IFCTHERMALCONDUCTIVITYMEASURE`, `IFCVOLUMETRICFLOWRATEMEASURE`, etc.

For quantity properties (in `Qto_*` Psets), the dataType is one of the `IFCQUANTITY*` values.

## Validation checklist before running ifctester

Run through this before audit:
- [ ] No `minOccurs`/`maxOccurs` attributes on `<specification>` or `<applicability>`
- [ ] Every facet in `<requirements>` has `cardinality="required|optional|prohibited"`
- [ ] All facet values wrapped in `<simpleValue>` or `<xs:restriction>`
- [ ] `<property>` facets in `<requirements>` have `dataType="IFC..."`
- [ ] `<specification>` has both `name` and `ifcVersion` attributes
- [ ] `ifcVersion` is one or more of: `IFC2X3`, `IFC4`, `IFC4X3_ADD2` (space-separated for multiple)
- [ ] Root element has correct namespace `xmlns="http://standards.buildingsmart.org/IDS"`

## Referenz-Tools

- buildingSMART online IDS Audit Tool: https://www.buildingsmart.org/users/services/ids-audit-tool/
- ifctester (CLI): part of the ifcopenshell stack, `pip install ifctester`
- usBIM.IDSeditor (ACCA): visual editor for IDS files, free download
- BlenderBIM / Bonsai: built-in IDS authoring + validation
