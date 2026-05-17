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
        "Revit IFC export: turn 'Export IFC common property sets' ON (Property Sets tab). "
        "If property names differ: include a custom Pset file mapping Revit param -> IFC name.",
        "Revit export setup",
    ),
    # Qto_*BaseQuantities — quantities missing
    (
        r"Property\(propertySet=Qto_\w+BaseQuantities; baseName=\w+\)",
        "Revit IFC export: turn 'Export base quantities' ON (Property Sets tab). "
        "These quantities are calculated automatically from the Revit geometry.",
        "Revit export setup",
    ),
    # Material missing
    (
        r"Material\(",
        "Family type needs a material assignment. Assign a material in the Family Editor "
        "or Type Properties. For Linear families: set the 'Material' parameter on the Pipe/Duct type.",
        "Revit family type editor",
    ),
    # Classification missing
    (
        r"Classification\(system=\w+",
        "IfcClassificationReference is missing. Bind a shared parameter (e.g. 'CodicePrezzario_BZ') "
        "at type level, fill the value per family type, and configure Classification Settings "
        "in the Revit IFC export (Field Name = the shared parameter).",
        "Revit shared parameter + export setup",
    ),
    # Entity-Attribute (PredefinedType etc.)
    (
        r"Attribute\(name=PredefinedType\)",
        "Family has no PredefinedType set. In the classification tool (e.g. LINEAR Desktop) "
        "or directly in the family type, set the 'Type Predefined IFC Type' / 'IfcExportType[Type]' "
        "parameter to a valid IFC enum value.",
        "Family classification",
    ),
    # Specific Pset properties that are typically calculated
    (
        r"Property\(propertySet=Pset_\w+; baseName=Reference\)",
        "'Reference' property is missing. This is typically a Type Mark / reference code. "
        "Bind the shared parameter 'Reference' to the type and fill it per family type "
        "(e.g. with the bill-of-quantities position or manufacturer reference).",
        "Revit type parameter",
    ),
    # Geometric properties — diameter etc.
    (
        r"Property\(propertySet=Pset_\w+; baseName=NominalDiameter\)",
        "NominalDiameter is missing in the common Pset. For Linear families the diameter "
        "on the Pipe type should map automatically into Pset_PipeSegmentCommon. "
        "If not: custom Pset file mapping Revit 'Diameter' -> IFC 'NominalDiameter'.",
        "Revit pset mapping",
    ),
]


def find_fix(pattern: str) -> tuple[str, str]:
    """Return (recommended_fix, fix_source) for a failure pattern."""
    for regex, fix, source in FIX_PATTERNS:
        if re.search(regex, pattern):
            return fix, source
    return (
        "Manual analysis required. Look up the failure pattern in references/common-failures.md "
        "or inspect the affected elements directly in the HTML report.",
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
    print("4. Repeat until pass-rate hits target (95-100% for green)")


if __name__ == "__main__":
    main()
