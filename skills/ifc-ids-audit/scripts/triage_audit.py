#!/usr/bin/env python3
"""
triage_audit.py — Read an audit result directory and produce a prioritised fix list.

Usage:
    python triage_audit.py path/to/audit-results/

Reads:
    audit_summary.txt    (overview)
    triage.csv           (per-failure-pattern aggregation)

Produces (to stdout, redirect to file if wanted):
    Prioritised fix list with concrete actions, ranked by impact.
"""
import argparse
import csv
import os
import re
import sys


# Pattern-to-fix lookup. Most BIM workflows have repeated failure modes;
# this dict maps regex patterns of failure descriptions to concrete fixes.
# Order matters — first match wins.
FIX_PATTERNS = [
    # Pset_*Common properties — typical Revit setup miss
    (
        r"Property\(propertySet=Pset_\w+Common; baseName=\w+\)",
        "Revit IFC-Export: 'Export IFC common property sets' AN (Tab Property Sets). "
        "Falls Property-Namen abweichen: Custom Pset-Datei einbinden mit Mapping Revit-Param → IFC-Name.",
        "Revit export setup",
    ),
    # Qto_*BaseQuantities — quantities missing
    (
        r"Property\(propertySet=Qto_\w+BaseQuantities; baseName=\w+\)",
        "Revit IFC-Export: 'Export base quantities' AN (Tab Property Sets). "
        "Diese Mengen werden automatisch aus der Revit-Geometrie berechnet.",
        "Revit export setup",
    ),
    # Material missing
    (
        r"Material\(",
        "Family Type braucht eine Material-Zuweisung. Im Family Editor oder Type Properties "
        "ein Material zuweisen. Bei Linear-Familien: 'Material'-Parameter am Pipe/Duct-Type setzen.",
        "Revit family type editor",
    ),
    # Classification missing
    (
        r"Classification\(system=\w+",
        "IfcClassificationReference fehlt. Shared Parameter (z.B. 'CodicePrezzario_BZ') "
        "an Type-Level binden, Wert pro Familientyp füllen, und im Revit-IFC-Export "
        "Classification Settings konfigurieren (Field Name = der Shared Parameter).",
        "Revit shared parameter + export setup",
    ),
    # Entity-Attribute (PredefinedType etc.)
    (
        r"Attribute\(name=PredefinedType\)",
        "Family hat keinen PredefinedType gesetzt. Im Klassifikations-Werkzeug (z.B. LINEAR Desktop) "
        "oder direkt im Family Type den Parameter 'Typ Vordefinierter IFC-Typ' / 'IfcExportType[Type]' "
        "auf einen gültigen IFC-Enum-Wert setzen.",
        "Family classification",
    ),
    # Specific Pset properties that are typically calculated
    (
        r"Property\(propertySet=Pset_\w+; baseName=Reference\)",
        "'Reference'-Property fehlt. Das ist typisch ein Type Mark / Bezugscode. "
        "Shared Parameter 'Reference' an Type binden und pro Familientyp füllen "
        "(z.B. mit der LV-Position oder Hersteller-Referenz).",
        "Revit type parameter",
    ),
    # Geometric properties — diameter etc.
    (
        r"Property\(propertySet=Pset_\w+; baseName=NominalDiameter\)",
        "NominalDiameter fehlt im Common Pset. Bei Linear-Familien sollte der Diameter "
        "am Pipe Type automatisch ins Pset_PipeSegmentCommon mapped werden. "
        "Falls nicht: Custom Pset-Datei mit Mapping Revit 'Diameter' → IFC 'NominalDiameter'.",
        "Revit pset mapping",
    ),
]


def find_fix(pattern: str) -> tuple[str, str]:
    """Return (recommended_fix, fix_source) for a failure pattern."""
    for regex, fix, source in FIX_PATTERNS:
        if re.search(regex, pattern):
            return fix, source
    return (
        "Manuelle Analyse erforderlich. Failure-Pattern in references/common-failures.md nachschlagen "
        "oder direkt im HTML-Report die betroffenen Elemente inspizieren.",
        "manual",
    )


def main():
    ap = argparse.ArgumentParser(description="Read audit results and produce prioritised fix list.")
    ap.add_argument("audit_dir", help="Audit results directory (output of run_audit.py)")
    ap.add_argument("--top", type=int, default=15, help="Show top N failure patterns (default 15)")
    args = ap.parse_args()

    if not os.path.isdir(args.audit_dir):
        sys.exit(f"ERROR: not a directory: {args.audit_dir}")

    summary_path = os.path.join(args.audit_dir, "audit_summary.txt")
    triage_path = os.path.join(args.audit_dir, "triage.csv")

    if not os.path.exists(triage_path):
        sys.exit(f"ERROR: triage.csv not found in {args.audit_dir}. Run run_audit.py first.")

    # Read summary
    print("=" * 80)
    print("AUDIT OVERVIEW")
    print("=" * 80)
    if os.path.exists(summary_path):
        with open(summary_path, encoding="utf-8") as f:
            print(f.read())
    print()

    # Read triage and produce prioritised fix list
    with open(triage_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("No failures to triage. Model is IDS-compliant.")
        return

    print("=" * 80)
    print(f"PRIORITISED FIX LIST (top {min(args.top, len(rows))} patterns by impact)")
    print("=" * 80)

    # Aggregate by pattern across all specs (a pattern may fail in multiple specs)
    pattern_agg = {}
    for r in rows:
        key = r["pattern"]
        if key not in pattern_agg:
            pattern_agg[key] = {
                "pattern": key,
                "facet_type": r["facet_type"],
                "details": r["details"],
                "total_affected": 0,
                "spec_ids": set(),
            }
        pattern_agg[key]["total_affected"] += int(r["affected_count"])
        pattern_agg[key]["spec_ids"].add(r["spec_id"])

    aggregated = sorted(
        pattern_agg.values(), key=lambda x: x["total_affected"], reverse=True
    )

    for i, item in enumerate(aggregated[: args.top], 1):
        fix, source = find_fix(item["pattern"])
        spec_list = ", ".join(sorted(item["spec_ids"]))
        print(f"\n#{i} — {item['total_affected']} elements affected  [{source}]")
        print(f"   Pattern: {item['pattern']}")
        print(f"   Specs:   {spec_list}")
        print(f"   Fix:     {fix}")

    if len(aggregated) > args.top:
        rest = sum(x["total_affected"] for x in aggregated[args.top:])
        print(f"\n... and {len(aggregated) - args.top} more patterns with {rest} elements")

    print()
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("1. Fix the top 3 patterns first — they unlock the most elements per action")
    print("2. Re-export IFC from CAD")
    print("3. Re-run: python run_audit.py --ifc <ifc> --ids <ids> --out <out>")
    print("4. Repeat until pass-rate hits target (95-100% for grün)")


if __name__ == "__main__":
    main()
