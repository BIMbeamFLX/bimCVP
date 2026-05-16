#!/usr/bin/env python3
"""
run_audit.py — Run an IDS audit against an IFC model.

Usage:
    python run_audit.py --ifc path/to/model.ifc --ids path/to/spec.ids --out path/to/results/

Outputs (in the --out directory):
    audit_summary.txt    plain-text overview per specification
    report.html          full HTML report (openable in browser)
    triage.csv           per-failure-pattern aggregation for prioritised fixes

Dependencies:
    pip install ifctester ifcopenshell lark
"""
import argparse
import csv
import os
import sys
import time
import traceback
from collections import Counter, defaultdict


def main():
    ap = argparse.ArgumentParser(description="Run IDS audit against IFC")
    ap.add_argument("--ifc", required=True, help="Path to IFC file")
    ap.add_argument("--ids", required=True, help="Path to IDS file")
    ap.add_argument("--out", required=True, help="Output directory (created if missing)")
    args = ap.parse_args()

    # Validate inputs
    if not os.path.exists(args.ifc):
        sys.exit(f"ERROR: IFC file not found: {args.ifc}")
    if not os.path.exists(args.ids):
        sys.exit(f"ERROR: IDS file not found: {args.ids}")

    os.makedirs(args.out, exist_ok=True)

    # Lazy import — fail fast if dependencies missing
    try:
        import ifcopenshell
        from ifctester import ids as ids_mod, reporter
    except ImportError as e:
        sys.exit(
            f"ERROR: Missing dependencies. Install with:\n"
            f"  pip install ifctester ifcopenshell lark --break-system-packages\n"
            f"Detail: {e}"
        )

    ifc_size_mb = os.path.getsize(args.ifc) / (1024 * 1024)
    print(f"IFC:  {args.ifc} ({ifc_size_mb:.1f} MB)")
    print(f"IDS:  {args.ids}")
    print(f"Out:  {args.out}")
    if ifc_size_mb > 500:
        print(f"  WARNING: large IFC (>500 MB) — load may take several minutes")
    print()

    # Step 1 — Load IDS (catches schema errors early)
    print("Loading IDS specification...")
    try:
        specs = ids_mod.open(args.ids)
    except Exception as e:
        print(f"\nERROR: IDS file failed to parse against IDS 1.0 schema.")
        print(f"Common causes:")
        print(f"  - minOccurs/maxOccurs on <specification> (not in IDS 1.0)")
        print(f"  - minOccurs on <applicability> (not in IDS 1.0)")
        print(f"  - facets in <requirements> without cardinality attribute")
        print(f"  - missing <simpleValue> wrapper around propertySet/baseName/name values")
        print(f"\nDetail:\n{e}")
        sys.exit(1)
    print(f"  IDS loaded: {len(specs.specifications)} specifications")

    # Step 2 — Load IFC
    t0 = time.time()
    print("Loading IFC (may take a moment for large files)...")
    m = ifcopenshell.open(args.ifc)
    print(f"  IFC loaded in {time.time() - t0:.1f}s · schema: {m.schema}")

    # Step 3 — Run audit
    print("Running IDS validation...")
    t1 = time.time()
    specs.validate(m)
    print(f"  audit done in {time.time() - t1:.1f}s")
    print()

    # Step 4 — Write audit_summary.txt
    summary_lines = []
    summary_lines.append(f"IDS Audit Summary")
    summary_lines.append(f"=" * 80)
    summary_lines.append(f"IFC:  {args.ifc} ({ifc_size_mb:.1f} MB, schema {m.schema})")
    summary_lines.append(f"IDS:  {args.ids}")
    summary_lines.append(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    summary_lines.append(f"")
    summary_lines.append(f"{'ID':<14} {'Name':<55} {'Apl':>6} {'Pass':>6} {'Fail':>6}")
    summary_lines.append(f"-" * 95)

    overall_app = overall_pass = overall_fail = 0
    spec_records = []
    for s in specs.specifications:
        applicable = list(getattr(s, 'applicable_entities', None) or [])
        passed = list(getattr(s, 'passed_entities', None) or [])
        failed = list(getattr(s, 'failed_entities', None) or [])
        n_app = len(applicable)
        n_pass = len(passed)
        n_fail = len(failed)
        overall_app += n_app
        overall_pass += n_pass
        overall_fail += n_fail
        ident = s.identifier or "?"
        name = (s.name or "")[:55]
        summary_lines.append(f"{ident:<14} {name:<55} {n_app:>6} {n_pass:>6} {n_fail:>6}")
        spec_records.append({
            "identifier": ident,
            "name": s.name or "",
            "applicable": n_app,
            "passed": n_pass,
            "failed": n_fail,
            "spec_obj": s,
        })
    summary_lines.append(f"-" * 95)
    pct = 100 * overall_pass / max(overall_app, 1)
    summary_lines.append(
        f"TOTAL  applicable={overall_app}  pass={overall_pass}  fail={overall_fail}  "
        f"pass-rate={pct:.1f}%"
    )
    summary_lines.append(f"")
    if overall_fail == 0 and overall_app > 0:
        summary_lines.append(f"STATUS: ALL GREEN — model is IDS-compliant.")
    elif overall_app == 0:
        summary_lines.append(f"STATUS: NO APPLICABLE ELEMENTS — IDS may not match model content.")
    else:
        summary_lines.append(
            f"STATUS: {overall_fail} elements still failing — see report.html and triage.csv for fixes."
        )

    summary_text = "\n".join(summary_lines)
    print(summary_text)
    print()

    summary_path = os.path.join(args.out, "audit_summary.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary_text)
    print(f"Saved: {summary_path}")

    # Step 5 — Write HTML report
    rep = reporter.Html(specs)
    rep.report()
    html_path = os.path.join(args.out, "report.html")
    rep.to_file(html_path)
    html_size_kb = os.path.getsize(html_path) // 1024
    print(f"Saved: {html_path} ({html_size_kb} KB)")

    # Step 6 — Write triage.csv (per-failure-pattern aggregation)
    triage_path = os.path.join(args.out, "triage.csv")
    triage_rows = []
    for rec in spec_records:
        s = rec["spec_obj"]
        for r in (s.requirements or []):
            failed_for_req = list(getattr(r, 'failed_entities', None) or [])
            if not failed_for_req:
                continue
            facet_type = type(r).__name__
            attrs = []
            for attr in ('propertySet', 'baseName', 'name', 'system', 'value'):
                v = getattr(r, attr, None)
                if v:
                    attrs.append(f"{attr}={v}")
            attr_str = "; ".join(attrs)
            pattern = f"{facet_type}({attr_str})" if attr_str else facet_type
            triage_rows.append({
                "spec_id": rec["identifier"],
                "spec_name": rec["name"],
                "facet_type": facet_type,
                "pattern": pattern,
                "affected_count": len(failed_for_req),
                "details": attr_str,
            })

    # Sort by impact: most-affected first
    triage_rows.sort(key=lambda r: r["affected_count"], reverse=True)

    with open(triage_path, "w", encoding="utf-8", newline="") as f:
        if triage_rows:
            writer = csv.DictWriter(
                f, fieldnames=["spec_id", "spec_name", "facet_type", "pattern", "affected_count", "details"]
            )
            writer.writeheader()
            for row in triage_rows:
                writer.writerow(row)
        else:
            f.write("# No failures — all specs passed.\n")
    print(f"Saved: {triage_path}")
    print()
    print("=" * 80)
    print(f"Audit complete. Next steps:")
    print(f"  1. cat {summary_path}              # quick stats")
    print(f"  2. open {html_path}                # visual deep-dive")
    print(f"  3. python triage_audit.py {args.out}  # prioritised fix list")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nAborted by user.")
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)
