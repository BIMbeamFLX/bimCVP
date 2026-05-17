# ──────────────────────────────────────────────────────────────────────────────
#  Bulk_Classify_IFC_NoInputs.py — VARIANT A (no Dynamo inputs needed)
#
#  Bimbeam — Building HVAC — IFC classification automation
#  Engine: CPython3
#
#  Two-stage classification:
#    1. Linear classification (LIN_CLASSIFICATION_LINEAR) -> linear-to-ifc-mapping.csv
#    2. Fallback: family-name pattern -> family-to-ifc-mapping.csv
#       (catches standard Revit families such as CHW-WL, AHU components,
#        Panel Tempering Circuit etc. that carry no Linear parameter)
#
#  Usage:
#    1. Open Dynamo, create a Python Script node, engine CPython3
#    2. Paste this entire content into the editor
#    3. Connect the output port to a Watch node
#    4. Click Run
#
#  Toggle dry-run vs. production:
#    Set DRY_RUN in the CONFIG section below to True (safe) or False,
#    save the script, click Run again.
#
#  As of 2026-05-16 — Bimbeam — Felix Hitthaler — CC BY 4.0
# ──────────────────────────────────────────────────────────────────────────────

# ╔════════════════════════════════════════════════════════════════════════════╗
# ║  CONFIG                                                                    ║
# ╚════════════════════════════════════════════════════════════════════════════╝

MAPPING_CSV = r"G:\projekte\buildingClaude\Rohrmassen\IDS\linear-to-ifc-mapping.csv"
FAMILY_CSV  = r"G:\projekte\buildingClaude\Rohrmassen\IDS\family-to-ifc-mapping.csv"
LOG_CSV     = r"G:\projekte\buildingClaude\Rohrmassen\IDS\classify_log.csv"
DRY_RUN     = True   # True = write nothing, only log
                     # False = actually classify

# ╔════════════════════════════════════════════════════════════════════════════╗
# ║  Code                                                                      ║
# ╚════════════════════════════════════════════════════════════════════════════╝

import clr
import csv
import os
import traceback

clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import (
    FilteredElementCollector,
    BuiltInCategory,
    ElementMulticategoryFilter,
    StorageType,
    Element,
)
from System.Collections.Generic import List

doc = DocumentManager.Instance.CurrentDBDocument

LIN_CLASS_PARAM_NAME = "LIN_CLASSIFICATION_LINEAR"

IFC_EXPORT_AS_NAMES = [
    "IfcExportAs[Type]",
    "Typ in IFC exportieren als",
    "IfcExportAs",
]
IFC_EXPORT_TYPE_NAMES = [
    "IfcExportType[Type]",
    "Typ Vordefinierter IFC-Typ",
    "IfcExportType",
]

HKLS_CATEGORIES = [
    BuiltInCategory.OST_PipeCurves,
    BuiltInCategory.OST_PipeFitting,
    BuiltInCategory.OST_PipeAccessory,
    BuiltInCategory.OST_PipeInsulations,
    BuiltInCategory.OST_DuctCurves,
    BuiltInCategory.OST_DuctFitting,
    BuiltInCategory.OST_DuctAccessory,
    BuiltInCategory.OST_DuctTerminal,
    BuiltInCategory.OST_DuctInsulations,
    BuiltInCategory.OST_MechanicalEquipment,
    BuiltInCategory.OST_PlumbingFixtures,
    BuiltInCategory.OST_Sprinklers,
]


def load_mapping(csv_path):
    """Linear class -> IfcExportAs/IfcExportType"""
    mapping = {}
    if not os.path.exists(csv_path):
        raise IOError("Mapping CSV not found: {}".format(csv_path))
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row.get("LIN_CLASSIFICATION_LINEAR") or "").strip()
            if not key:
                continue
            mapping[key] = {
                "IfcExportAs":   (row.get("IfcExportAs") or "").strip(),
                "IfcExportType": (row.get("IfcExportType") or "").strip(),
            }
    return mapping


def load_family_mapping(csv_path):
    """Family pattern -> IfcExportAs/IfcExportType. List preserves order."""
    patterns = []
    if not os.path.exists(csv_path):
        return patterns
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row.get("family_pattern") or "").strip()
            if not key:
                continue
            patterns.append({
                "pattern":       key,
                "pattern_lower": key.lower(),
                "IfcExportAs":   (row.get("IfcExportAs") or "").strip(),
                "IfcExportType": (row.get("IfcExportType") or "").strip(),
            })
    return patterns


def family_lookup(family_name, type_name, patterns):
    """Finds first pattern match in family or type name (case insensitive, substring)."""
    if not patterns:
        return None
    fname = (family_name or "").lower()
    tname = (type_name or "").lower()
    for p in patterns:
        if p["pattern_lower"] in fname or p["pattern_lower"] in tname:
            return p
    return None


def get_param_by_names(element, names):
    for name in names:
        try:
            p = element.LookupParameter(name)
            if p is not None:
                return p
        except Exception:
            continue
    return None


def read_param_string(element, name):
    p = get_param_by_names(element, [name])
    if p is None:
        return None
    try:
        if p.StorageType != StorageType.String:
            return None
        return p.AsString()
    except Exception:
        return None


def set_param_string(param, value):
    if param is None:
        return False
    try:
        if param.IsReadOnly:
            return False
        if param.StorageType != StorageType.String:
            return False
        param.Set(value or "")
        return True
    except Exception:
        return False


def get_type_name(fs):
    try:
        n = fs.Name
        if n:
            return n
    except Exception:
        pass
    try:
        return Element.Name.GetValue(fs)
    except Exception:
        pass
    return "(?)"


def get_family_name(fs):
    try:
        fn = fs.FamilyName
        if fn:
            return fn
    except Exception:
        pass
    try:
        fam = fs.Family
        if fam is not None:
            return fam.Name or "(?)"
    except Exception:
        pass
    return "(?)"


def get_category_name(fs):
    try:
        cat = fs.Category
        if cat is not None:
            return cat.Name or "(?)"
    except Exception:
        pass
    return "(?)"


def collect_hkls_element_types(doc):
    cat_list = List[BuiltInCategory](HKLS_CATEGORIES)
    cat_filter = ElementMulticategoryFilter(cat_list)
    collector = (FilteredElementCollector(doc)
                 .WherePasses(cat_filter)
                 .WhereElementIsElementType())
    return [e for e in collector if e is not None]


results = {
    "applied_lin": 0,
    "applied_fam": 0,
    "would_apply_lin": 0,
    "would_apply_fam": 0,
    "unmapped": 0,
    "no_match": 0,
    "skipped_param_missing": 0,
    "errors": 0,
}
log_rows = []
transaction_opened = False

try:
    mapping = load_mapping(MAPPING_CSV)
    family_patterns = load_family_mapping(FAMILY_CSV)
    element_types = collect_hkls_element_types(doc)

    if not DRY_RUN:
        TransactionManager.Instance.EnsureInTransaction(doc)
        transaction_opened = True

    for et in element_types:
        fam_name = "(?)"
        type_name = "(?)"
        cat_name = "(?)"
        lin_value = ""
        match_source = ""

        try:
            type_name = get_type_name(et)
            fam_name = get_family_name(et)
            cat_name = get_category_name(et)
            lin_value = read_param_string(et, LIN_CLASS_PARAM_NAME) or ""

            target = None

            # Stage 1: Linear classification
            if lin_value:
                target = mapping.get(lin_value.strip())
                if target:
                    match_source = "linear_class"
                else:
                    # Linear classified it, but we don't recognize the value
                    results["unmapped"] += 1
                    log_rows.append({
                        "status": "UNMAPPED",
                        "source": "",
                        "category": cat_name, "family": fam_name, "type": type_name,
                        "lin_class": lin_value, "ifc_class": "", "ifc_predef": "",
                        "note": "Linear class not in linear-to-ifc-mapping.csv"
                    })
                    continue

            # Stage 2: family-name fallback
            if target is None:
                fp = family_lookup(fam_name, type_name, family_patterns)
                if fp:
                    target = {
                        "IfcExportAs":   fp["IfcExportAs"],
                        "IfcExportType": fp["IfcExportType"],
                    }
                    match_source = "family_pattern:" + fp["pattern"]

            # No match in either stage
            if target is None:
                results["no_match"] += 1
                log_rows.append({
                    "status": "NO_MATCH",
                    "source": "",
                    "category": cat_name, "family": fam_name, "type": type_name,
                    "lin_class": lin_value, "ifc_class": "", "ifc_predef": "",
                    "note": "neither Linear class nor family pattern matched — set manually"
                })
                continue

            p_export_as = get_param_by_names(et, IFC_EXPORT_AS_NAMES)
            p_export_type = get_param_by_names(et, IFC_EXPORT_TYPE_NAMES)

            if p_export_as is None or p_export_type is None:
                results["skipped_param_missing"] += 1
                log_rows.append({
                    "status": "PARAM_MISSING",
                    "source": match_source,
                    "category": cat_name, "family": fam_name, "type": type_name,
                    "lin_class": lin_value,
                    "ifc_class": target["IfcExportAs"], "ifc_predef": target["IfcExportType"],
                    "note": "IfcExportAs[Type] / IfcExportType[Type] not available"
                })
                continue

            if DRY_RUN:
                if match_source.startswith("family_pattern"):
                    results["would_apply_fam"] += 1
                else:
                    results["would_apply_lin"] += 1
                log_rows.append({
                    "status": "WOULD_APPLY",
                    "source": match_source,
                    "category": cat_name, "family": fam_name, "type": type_name,
                    "lin_class": lin_value,
                    "ifc_class": target["IfcExportAs"], "ifc_predef": target["IfcExportType"],
                    "note": "Dry-Run"
                })
            else:
                ok1 = set_param_string(p_export_as, target["IfcExportAs"])
                ok2 = set_param_string(p_export_type, target["IfcExportType"])
                if ok1 and ok2:
                    if match_source.startswith("family_pattern"):
                        results["applied_fam"] += 1
                    else:
                        results["applied_lin"] += 1
                    log_rows.append({
                        "status": "APPLIED",
                        "source": match_source,
                        "category": cat_name, "family": fam_name, "type": type_name,
                        "lin_class": lin_value,
                        "ifc_class": target["IfcExportAs"], "ifc_predef": target["IfcExportType"],
                        "note": ""
                    })
                else:
                    results["skipped_param_missing"] += 1
                    log_rows.append({
                        "status": "PARAM_MISSING",
                        "source": match_source,
                        "category": cat_name, "family": fam_name, "type": type_name,
                        "lin_class": lin_value,
                        "ifc_class": target["IfcExportAs"], "ifc_predef": target["IfcExportType"],
                        "note": "Parameter read-only or not writable"
                    })

        except Exception as ex_inner:
            results["errors"] += 1
            log_rows.append({
                "status": "ERROR",
                "source": match_source,
                "category": cat_name, "family": fam_name, "type": type_name,
                "lin_class": lin_value, "ifc_class": "", "ifc_predef": "",
                "note": "Exception: " + str(ex_inner)
            })

    if transaction_opened:
        TransactionManager.Instance.TransactionTaskDone()
        transaction_opened = False

    log_dir = os.path.dirname(LOG_CSV)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    with open(LOG_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "status", "source", "category", "family", "type",
            "lin_class", "ifc_class", "ifc_predef", "note"
        ])
        writer.writeheader()
        for r in log_rows:
            writer.writerow(r)

    total_would = results["would_apply_lin"] + results["would_apply_fam"]
    total_applied = results["applied_lin"] + results["applied_fam"]

    summary = []
    summary.append("Bimbeam IFC Bulk Classifier — Summary")
    summary.append("=" * 50)
    summary.append("Mode:                {}".format("DRY-RUN (nothing written)" if DRY_RUN else "PRODUCTION (written)"))
    summary.append("Linear mapping:      {} entries".format(len(mapping)))
    summary.append("Family mapping:      {} patterns".format(len(family_patterns)))
    summary.append("ElementTypes checked: {}".format(len(element_types)))
    summary.append("")
    summary.append("Findings:")
    if DRY_RUN:
        summary.append("  via Linear class:  {}".format(results["would_apply_lin"]))
        summary.append("  via family patt.:  {}".format(results["would_apply_fam"]))
        summary.append("  -> would apply:    {} total".format(total_would))
    else:
        summary.append("  via Linear class:  {}".format(results["applied_lin"]))
        summary.append("  via family patt.:  {}".format(results["applied_fam"]))
        summary.append("  -> applied:        {} total".format(total_applied))
    summary.append("  Linear class UNMAPPED: {}".format(results["unmapped"]))
    summary.append("  No match (manual): {}".format(results["no_match"]))
    summary.append("  IFC param missing: {}".format(results["skipped_param_missing"]))
    summary.append("  Errors:            {}".format(results["errors"]))
    summary.append("")
    summary.append("Log:  {}".format(LOG_CSV))
    summary.append("")
    if DRY_RUN:
        summary.append("=> Set DRY_RUN at the top of the script to False and run again once the numbers look right.")
    else:
        summary.append("=> Changes are live. Ctrl+Z in Revit undoes everything.")

    OUT = "\n".join(summary)

except Exception as ex_outer:
    if transaction_opened:
        try:
            TransactionManager.Instance.ForceCloseTransaction()
        except Exception:
            pass
    OUT = "ERROR during run:\n{}\n\nTraceback:\n{}".format(str(ex_outer), traceback.format_exc())
