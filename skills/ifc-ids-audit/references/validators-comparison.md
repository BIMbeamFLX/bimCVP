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
- Sharing audit results with external parties (architect, Auftraggeber, Validator) — official badge
- Quick one-off check without installing anything
- Project allows cloud upload
- Need to convince a skeptical stakeholder ("hier ist das offizielle Tool")

## usBIM.IDSeditor (ACCA, free)

**What it is:** Visual IDS authoring + validation tool from ACCA software (italienischer BIM-Software-Vendor).

**Pro:**
- Free download
- Visual IDS author with form-based editing (no XML knowledge needed)
- Integrated with rest of usBIM ecosystem
- Good Italian-localised UX for italienische Capitolato-Workflows

**Con:**
- ACCA ecosystem lock-in tendency
- Less Mainstream als Bonsai oder online-Tool
- Windows-zentriert

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
- Expensive (Lizenz im 4-stelligen Bereich)
- Closed source
- Overkill für nur IDS-Validation
- IDS-Implementierung manchmal Solibri-spezifisch erweitert

**Use when:**
- Already using Solibri for clash / model checking → IDS als zusätzliche Schicht
- Großer Konzern / öffentliche Auftraggeber mit Solibri-Lizenz
- Complex multi-discipline coordination beyond IDS

## Combinations that work well

**Bimbeam-Standard für Building-artige Projekte:**
- **ifctester** für Auto-Audit bei jedem Re-Export (5 Sek, in CI)
- **Bonsai** für visuelle Inspektion einzelner Failures
- **buildingSMART IDS Audit Tool** für die finale Übergabe-Validierung (Badge im Lieferschein)

**Italian Capitolato workflow:**
- **usBIM.IDSeditor** für IDS-Authoring (italienische UI)
- **ifctester** für Audit-Loop
- **buildingSMART** für Capitolato-Compliance-Beleg

**DACH-Architekturbüro Standard:**
- **Bonsai** für alles (free, vollständig, visuell)
- ifctester nur wenn CI gewünscht

## Compatibility Notes

Alle fünf Tools nutzen die offizielle IDS 1.0 XSD-Schema-Definition. Eine IDS-Datei die mit dem einen Tool funktioniert sollte mit allen funktionieren.

Ausnahmen / Edge Cases:
- usBIM.IDSeditor exportiert manchmal mit kleinen ACCA-Erweiterungen die andere Tools warning-ignorieren
- Solibri hatte historisch eine eigene "Quality Information" Sprache, IDS-Support ist neuer und manchmal hinkt eine Version hinter
- ifctester ist immer am aktuellsten Stand der buildingSMART-Spec

Bei Übergaben: idealerweise **dieselbe Tool-Kette wie der Validator** verwenden. Wenn die Provinz Solibri verwendet, eigene Validierung auch in Solibri durchführen — auch wenn ifctester "grün" sagt, kann Solibri's Interpretation leicht abweichen.
