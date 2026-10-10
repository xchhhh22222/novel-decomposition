#!/usr/bin/env python3
"""Validate the minimal Phase 2 timeline and parallel-promise audit patch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


EXPECTED_NODE_WINDOWS = {
    "ES1": "1-3",
    "ES2": "4-9",
    "ES3": "10-15",
    "ES4": "16-23",
    "ES5": "24-30",
    "ES6": "31-38",
    "ES7": "39-45",
    "ES8": "46-50",
}
EXPECTED_TIMELINE_AUDITS = {f"TL-{number:03d}" for number in range(1, 9)}
EXPECTED_FIRST_TEN = [
    ("1-3", "ES1"),
    ("4-6", "ES2"),
    ("7-9", "ES2"),
    ("10", "ES3"),
]
FORBIDDEN_ES4_MARKERS = (
    "私下合格证明",
    "妹妹以灌溉记录",
    "官方水期记录与本地土温不匹配",
    "重排试种",
)
EXPECTED_MACROS = {"ES:MACRO:A", "ES:MACRO:B", "P2:ES:MACRO:B:COMMONS"}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _ash_seed_option(phase1: dict[str, Any]) -> dict[str, Any]:
    options = phase1.get("options") or phase1.get("enhanced_options") or []
    for option in options:
        if option.get("option_id") == "ENHANCED:ASH_SEED":
            return option
    raise ValueError("ENHANCED:ASH_SEED not found in Phase 1 source")


def validate(
    audit: dict[str, Any], longform: dict[str, Any], phase1: dict[str, Any]
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    try:
        option = _ash_seed_option(phase1)
    except ValueError as exc:
        return [str(exc)], warnings

    if audit.get("scope") != "PLANNED_RESEARCH_STATE_NOT_OBSERVED":
        errors.append("audit scope must remain PLANNED_RESEARCH_STATE_NOT_OBSERVED")
    if audit.get("base_option_id") != "ENHANCED:ASH_SEED":
        errors.append("audit must target ENHANCED:ASH_SEED")

    phase1_nodes = {
        node.get("node_id"): node.get("chapter_range")
        for node in option.get("story_nodes", [])
    }
    if phase1_nodes != EXPECTED_NODE_WINDOWS:
        errors.append("Phase 1 ES1-ES8 windows differ from the frozen baseline")

    consistency = audit.get("timeline_consistency", {})
    audited_windows = {
        item.get("node_id"): item.get("chapter_range")
        for item in consistency.get("frozen_node_windows", [])
    }
    if audited_windows != phase1_nodes:
        errors.append("audit frozen_node_windows do not exactly match Phase 1")

    audit_items = consistency.get("choice_position_audit", [])
    audit_ids = {item.get("audit_id") for item in audit_items}
    if audit_ids != EXPECTED_TIMELINE_AUDITS:
        errors.append("timeline audit must contain exactly TL-001 through TL-008")
    for item in audit_items:
        if item.get("resolution") != "RESTORED_TO_PHASE1":
            errors.append(f"{item.get('audit_id')} is not restored to Phase 1")
        for field in (
            "choice",
            "phase1_position",
            "previous_phase2_position",
            "accepted_position",
            "reason",
            "contract_impact",
        ):
            if not item.get(field):
                errors.append(f"{item.get('audit_id')} lacks {field}")
    if consistency.get("independent_new_pacing_candidates") != []:
        errors.append("no alternative pacing candidate was authorized for this patch")
    if consistency.get("result") != "PASS_PHASE1_BASELINE_RESTORED":
        errors.append("timeline result must record the restored Phase 1 baseline")

    first_ten = longform.get("chapters_1_10_high_precision", [])
    actual_first_ten = [
        (item.get("range"), item.get("phase1_node_ref")) for item in first_ten
    ]
    if actual_first_ten != EXPECTED_FIRST_TEN:
        errors.append("first-ten windows must be ES1 1-3, ES2 4-9, then ES3 opening at 10")
    first_ten_text = json.dumps(first_ten, ensure_ascii=False)
    for marker in FORBIDDEN_ES4_MARKERS:
        if marker in first_ten_text:
            errors.append(f"ES4 choice leaked into chapters 1-10: {marker}")
    chapter_ten = next((item for item in first_ten if item.get("range") == "10"), {})
    chapter_ten_text = json.dumps(chapter_ten, ensure_ascii=False)
    if "尚未完成共同方案" not in chapter_ten_text or "关系线仍为 OPEN" not in chapter_ten_text:
        errors.append("chapter 10 must open ES3 without completing the family plan")
    later_windows = [
        (item.get("range"), item.get("phase1_node_ref"))
        for item in longform.get("chapters_11_50_weaving", [])
    ]
    if later_windows != [
        ("11-15", "ES3"),
        ("16-23", "ES4"),
        ("24-30", "ES5"),
        ("31-38", "ES6"),
        ("39-45", "ES7"),
        ("46-50", "ES8"),
    ]:
        errors.append("chapters 11-50 must preserve the remaining Phase 1 node windows")

    source_macros = {item.get("macro_id"): item for item in option.get("macro_arcs", [])}
    ledgers = {
        item.get("macro_id"): item
        for item in audit.get("parallel_macro_commitment_ledger", [])
    }
    if set(ledgers) != EXPECTED_MACROS:
        errors.append("parallel ledger must contain exactly MA-A, salt-seal MA-B, and commons MA-B")
        return errors, warnings

    for macro_id, item in ledgers.items():
        required = (
            "last_defined_progress_node",
            "last_actual_progress_node",
            "current_state",
            "state_scope",
            "dormancy_reason",
            "next_trigger_condition",
            "stagnation_risk",
        )
        for field in required:
            if not item.get(field):
                errors.append(f"{macro_id} lacks {field}")
        if item.get("last_actual_story_node") is not None:
            errors.append(f"{macro_id} falsely claims an observed story node")
        if item.get("state_scope") != "PLANNED_RESEARCH_STATE_NOT_OBSERVED":
            errors.append(f"{macro_id} state scope must remain research-only")
        if item.get("cancelled") is not False:
            errors.append(f"{macro_id} must not be cancelled")

    ma_a = ledgers["ES:MACRO:A"]
    source_ma_a = source_macros.get("ES:MACRO:A", {})
    if ma_a.get("settlement_contract") != source_ma_a.get("settlement_contract"):
        errors.append("MA-A settlement contract changed")
    if ma_a.get("current_state") != "PAID" or ma_a.get("unpaid_reader_expectations") != []:
        errors.append("MA-A must remain PAID with no unpaid settlement conditions")
    if not str(ma_a.get("last_defined_progress_node", "")).startswith("ES7"):
        errors.append("MA-A last planned progress must remain ES7")

    salt = ledgers["ES:MACRO:B"]
    source_salt = source_macros.get("ES:MACRO:B", {})
    if salt.get("promise") != source_salt.get("macro_promise"):
        errors.append("salt-seal promise changed")
    if salt.get("settlement_contract") != source_salt.get("settlement_contract"):
        errors.append("salt-seal settlement contract changed")
    if salt.get("current_state") != "ACTIVE_HOLD":
        errors.append("salt-seal macro must remain ACTIVE_HOLD")
    if not str(salt.get("last_defined_progress_node", "")).startswith("ES8"):
        errors.append("salt-seal last planned progress must remain ES8")
    if salt.get("absorbed_by") is not None:
        errors.append("salt-seal macro cannot be absorbed by another arc")
    salt_unpaid = salt.get("unpaid_reader_expectations", [])
    for marker in ("来源", "采购决策", "受影响区域", "监督边界"):
        if not any(marker in item for item in salt_unpaid):
            errors.append(f"salt-seal ledger lost unpaid expectation: {marker}")

    commons = ledgers["P2:ES:MACRO:B:COMMONS"]
    if commons.get("current_state") != "PARTIALLY_PAID":
        errors.append("commons macro may be only PARTIALLY_PAID at chapter 100")
    if commons.get("absorbs_macro_ids") != []:
        errors.append("commons macro cannot absorb prior macros")
    if commons.get("separate_from_salt_seal_arc") is not True:
        errors.append("commons and salt-seal responsibilities must remain separate")
    if not commons.get("unpaid_reader_expectations"):
        errors.append("commons macro must retain unpaid cross-season obligations")

    if audit.get("disposition") != "STOP_FOR_INDEPENDENT_REVIEW":
        errors.append("audit must stop for independent review")

    warnings.extend(
        [
            "Structural checks do not establish literary or semantic quality.",
            "All macro states describe planned research structure, not observed novel prose.",
        ]
    )
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--longform", type=Path, required=True)
    parser.add_argument("--phase1", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    errors, warnings = validate(
        load_json(args.audit), load_json(args.longform), load_json(args.phase1)
    )
    report = {
        "validator": "validate_phase2_acceptance_patch.py",
        "result": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
        "checks": {
            "phase1_timeline_restored": not any("first-ten" in item or "ES4" in item for item in errors),
            "parallel_macro_ledger_complete": not any("parallel ledger" in item for item in errors),
            "salt_seal_contract_retained": not any("salt-seal" in item for item in errors),
            "research_state_not_observed": not any("observed story node" in item for item in errors),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
