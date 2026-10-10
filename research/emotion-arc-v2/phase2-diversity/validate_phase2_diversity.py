#!/usr/bin/env python3
"""Research-only structural gate for the Emotion-First Phase 2 pilot."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


DIMENSIONS = {
    "reader_expectation",
    "emotion_payoff",
    "character_agency",
    "causal_weaving",
    "macro_arc_diversity",
    "longform_sustainability",
    "setting_material_compatibility",
    "originality",
}
LINE_FIELDS = {
    "line_id",
    "reader_expectation",
    "character_goal",
    "accumulated_pressure",
    "available_choices",
    "required_cost",
    "causal_interfaces",
    "stage_payoff",
    "unpaid_promise",
    "next_state",
}
WINDOW_FIELDS = {
    "range",
    "reader_promise_advanced",
    "character_choice",
    "visible_state_change",
    "new_cost_or_unpaid_obligation",
    "causal_links",
    "material_world_links",
}
EXPECTED_STAGES = [
    "trigger",
    "goal",
    "resistance",
    "nodes",
    "choice",
    "cost",
    "payoff",
    "state_change",
    "next_entry",
]


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def paid_transition(macro: dict[str, Any]) -> str | None:
    for item in macro.get("state_transitions", []):
        if item.get("to") == "PAID":
            return item.get("node_id")
    return None


def validate(
    research: dict[str, Any],
    longform: dict[str, Any],
    material: dict[str, Any],
    review: dict[str, Any],
    phase1: dict[str, Any],
    phase1_sha256: str,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if research.get("schema_version") != "emotion_first_phase2_diversity_research_v1":
        errors.append("SCHEMA: phase2 research schema invalid")
    base = research.get("phase1_base", {})
    if base.get("commit") != "fea5272815b50c9a5e9f68866a2e1426a028a32e":
        errors.append("BASE: Phase 1 commit changed")
    if base.get("source_sha256") != phase1_sha256:
        errors.append("BASE: Phase 1 enhanced-options SHA-256 mismatch")

    source_options = {item.get("option_id"): item for item in phase1.get("options", [])}
    candidates = research.get("handoff_candidates", [])
    if len(candidates) != 4:
        errors.append("DIVERSITY: exactly four handoff candidates required")
    base_counts = Counter(item.get("base_option_id") for item in candidates)
    expected_counts = {"ENHANCED:ASH_SEED": 2, "ENHANCED:SILENT_BELL": 2}
    if dict(base_counts) != expected_counts:
        errors.append(f"DIVERSITY: expected two candidates per Phase 1 option, got {dict(base_counts)}")
    engines = [item.get("causal_engine_family") for item in candidates]
    if len(set(engines)) != len(engines) or None in engines:
        errors.append("DIVERSITY: causal engine families must be present and distinct")

    candidate_ids: set[str] = set()
    for candidate in candidates:
        cid = candidate.get("handoff_id", "<missing>")
        candidate_ids.add(cid)
        source = source_options.get(candidate.get("base_option_id"))
        if not source:
            errors.append(f"{cid}: unknown Phase 1 base option")
            continue
        macros = {item.get("macro_id"): item for item in source.get("macro_arcs", [])}
        frozen = candidate.get("frozen_ma_a", {})
        original_a = macros.get(frozen.get("macro_id"))
        if not original_a:
            errors.append(f"{cid}: frozen MA-A does not resolve")
        else:
            if frozen.get("settlement_contract") != original_a.get("settlement_contract"):
                errors.append(f"{cid}: MA-A settlement contract changed")
            if frozen.get("state") != "PAID" or frozen.get("paid_at_node") != paid_transition(original_a):
                errors.append(f"{cid}: MA-A paid state/timing changed")

        retained = candidate.get("retained_phase1_b_obligation", {})
        original_b = macros.get(retained.get("macro_id"))
        if not original_b:
            errors.append(f"{cid}: retained Phase 1 MA-B does not resolve")
        else:
            if retained.get("contract_retained") != original_b.get("settlement_contract"):
                errors.append(f"{cid}: Phase 1 MA-B contract changed")
            if retained.get("cancellation") is not False:
                errors.append(f"{cid}: new arc cancels an old macro obligation")
            if "HOLD" not in str(retained.get("state")):
                errors.append(f"{cid}: unresolved Phase 1 MA-B must retain HOLD")

        evidence = candidate.get("source_evidence", {})
        allowed_ids = {item.get("record_id") for item in source.get("emotion_source_uses", [])}
        used_ids = set(evidence.get("line_ids", [])) | set(evidence.get("weave_ids", [])) | set(evidence.get("macro_ids", []))
        used_ids.add(evidence.get("handoff_id"))
        if None in used_ids or not used_ids.issubset(allowed_ids):
            errors.append(f"{cid}: emotion evidence not present in frozen Phase 1 option")
        if evidence.get("handoff_id") != "AH:BOOK_001:001" or evidence.get("use_status") != "RESEARCH_ANALOGY_ONLY":
            errors.append(f"{cid}: AH001 must remain a research-only analogy")

        proposed = candidate.get("proposed_ma_b", {})
        required = {
            "macro_id", "core_reader_expectation", "trigger", "overlap_with_old_arc",
            "state_transitions", "stage_settlement", "full_settlement", "why_not_quickly_solved",
            "enemy_independence_test", "not_reskin_reason",
        }
        if required - set(proposed):
            errors.append(f"{cid}: proposed MA-B missing fields {sorted(required - set(proposed))}")
        transitions = proposed.get("state_transitions", [])
        if not transitions or transitions[0].get("from") != "NOT_OPENED":
            errors.append(f"{cid}: MA-B must start at NOT_OPENED")
        if any(item.get("to") == "PAID" for item in transitions):
            errors.append(f"{cid}: Phase 2 evidence does not support full PAID")
        if proposed.get("stage_settlement", {}).get("result") != "PARTIALLY_PAID":
            errors.append(f"{cid}: stage settlement must remain PARTIALLY_PAID")
        if proposed.get("full_settlement", {}).get("result") != "NOT_YET_PAID":
            errors.append(f"{cid}: full settlement must remain unpaid")
        if proposed.get("enemy_independence_test", {}).get("passes") is not True:
            errors.append(f"{cid}: no-enemy causal test not passed")

        lines = candidate.get("emotion_lines", [])
        if len(lines) < 3:
            errors.append(f"{cid}: at least three functional emotion lines required")
        line_ids = {line.get("line_id") for line in lines}
        for line in lines:
            missing = LINE_FIELDS - set(line)
            if missing:
                errors.append(f"{cid}/{line.get('line_id')}: missing line fields {sorted(missing)}")
            if len(line.get("available_choices", [])) < 2:
                errors.append(f"{cid}/{line.get('line_id')}: choices are not meaningful")
        graph = candidate.get("causal_graph", [])
        connected: set[str] = set()
        for edge in graph:
            if not edge.get("bridge") or not edge.get("effect"):
                errors.append(f"{cid}: causal edge lacks bridge/effect")
            if edge.get("from") not in line_ids or edge.get("to") not in line_ids:
                errors.append(f"{cid}: causal edge references unknown line")
            connected.update([edge.get("from"), edge.get("to")])
        if connected != line_ids:
            errors.append(f"{cid}: every emotion line must participate in causal weaving")
        tests = candidate.get("counterfactual_tests", [])
        removed = {item.get("remove") for item in tests}
        if removed != line_ids:
            errors.append(f"{cid}: every emotion line needs a counterfactual removal test")
        for item in tests:
            if item.get("decorative") is not False or not item.get("required_story_change"):
                errors.append(f"{cid}: counterfactual test is decorative or incomplete")
        if "VERIFIED" in str(candidate.get("dominance_transfer_status")) and candidate.get("dominance_transfer_status") != "PENDING_INDEPENDENT_REVIEW":
            errors.append(f"{cid}: dominance transfer overclaimed")

    if research.get("emotion_evidence_policy", {}).get("handoff_reference_status") != "CANDIDATE_UNVERIFIED":
        errors.append("AH001: global status must remain CANDIDATE_UNVERIFIED")
    if research.get("provisional_selection", {}).get("status") != "RESEARCH_PROVISIONAL_SELECTION":
        errors.append("SELECTION: must remain research provisional")

    comparison = research.get("planner_path_comparison", {})
    if comparison.get("independence") != "REQUESTED_NOT_MACHINE_PROVEN" or comparison.get("strict_blind_test") is not False:
        errors.append("COMPARISON: isolation/blinding overclaimed")
    comparison_paths = {item.get("path"): item for item in comparison.get("paths", [])}
    if set(comparison_paths) != {"LEGACY_BASELINE", "E2_E3_ENABLED"}:
        errors.append("COMPARISON: both Planner paths are required")
    for path, item in comparison_paths.items():
        if len(item.get("story_nodes", [])) < 6:
            errors.append(f"COMPARISON/{path}: semantic composition is incomplete")
        for node in item.get("story_nodes", []):
            if not node.get("cause") or not node.get("choice") or not node.get("state_change"):
                errors.append(f"COMPARISON/{path}: node lacks cause/choice/state change")
        if item.get("quality_status") != "PENDING_INDEPENDENT_REVIEW":
            errors.append(f"COMPARISON/{path}: quality overclaimed")

    if longform.get("selected_handoff_id") != research.get("provisional_selection", {}).get("handoff_id"):
        errors.append("LONGFORM: pressure test does not match provisional selection")
    windows = longform.get("chapters_51_100_windows", [])
    if [item.get("range") for item in windows] != ["51-60", "61-75", "76-90", "91-100"]:
        errors.append("LONGFORM: required chapter windows missing or reordered")
    for window in windows:
        missing = WINDOW_FIELDS - set(window)
        if missing:
            errors.append(f"LONGFORM/{window.get('range')}: missing {sorted(missing)}")
        if not window.get("character_choice") or not window.get("visible_state_change"):
            errors.append(f"LONGFORM/{window.get('range')}: lacks choice or state change")
    stages = [item.get("stage") for item in longform.get("story_spine", {}).get("stages", [])]
    if stages != EXPECTED_STAGES:
        errors.append("STORY_SPINE: exact nine-stage lifecycle not preserved")
    ledger = {item.get("macro_id"): item for item in longform.get("macro_contract_ledger", [])}
    if ledger.get("ES:MACRO:A", {}).get("state_at_100") != "PAID":
        errors.append("LONGFORM: MA-A paid contract not retained")
    if ledger.get("ES:MACRO:B", {}).get("state_at_100") != "ACTIVE_HOLD":
        errors.append("LONGFORM: Phase 1 MA-B obligation cancelled or overclaimed")
    if ledger.get("P2:ES:MACRO:B:COMMONS", {}).get("state_at_100") != "PARTIALLY_PAID":
        errors.append("LONGFORM: proposed MA-B stage state invalid")
    if not longform.get("post_100_continuation_conditions_only"):
        errors.append("LONGFORM: 101+ continuation conditions missing")

    queries = material.get("queries", [])
    path_counts = Counter(item.get("path") for item in queries)
    if path_counts != Counter({"LEGACY_BASELINE": 8, "E2_E3_ENABLED": 8}):
        errors.append(f"MATERIAL: expected 8 queries per path, got {dict(path_counts)}")
    for query in queries:
        selected = query.get("selected_ref", {})
        identities = {selected.get("record_id"), selected.get("source_record_id"), selected.get("component_id")}
        if query.get("selected_id") not in identities:
            errors.append(f"MATERIAL/{query.get('query_id')}: selected ID did not resolve")
        source_hash = selected.get("source_line_sha256")
        if not isinstance(source_hash, str) or len(source_hash) != 64:
            errors.append(f"MATERIAL/{query.get('query_id')}: source hash missing")
        if not query.get("selection_reason") or not query.get("adaptation_bridge") or not query.get("effect_on_action_or_payoff"):
            errors.append(f"MATERIAL/{query.get('query_id')}: adaptation rationale incomplete")
        if not query.get("rejected_refs") or not query.get("rejection_reason"):
            errors.append(f"MATERIAL/{query.get('query_id')}: real rejection missing")
    if material.get("independence") != "REQUESTED_NOT_MACHINE_PROVEN":
        errors.append("MATERIAL: comparison independence overclaimed")
    if comparison.get("brief_sha256") != material.get("brief_sha256"):
        errors.append("COMPARISON: shared brief hash differs from material run")
    for path, item in comparison_paths.items():
        retrieved_ids = {
            query.get("selected_id") for query in queries if query.get("path") == path
        }
        if set(item.get("material_selected_ids", [])) != retrieved_ids:
            errors.append(f"COMPARISON/{path}: selected material IDs differ from real retrieval")

    reviewed = {item.get("handoff_id"): item for item in review.get("candidate_reviews", [])}
    if set(reviewed) != candidate_ids:
        errors.append("QUALITY: every handoff candidate must be reviewed")
    for cid, item in reviewed.items():
        scores = item.get("scores", {})
        if set(scores) != DIMENSIONS:
            errors.append(f"QUALITY/{cid}: rubric dimensions incomplete")
            continue
        for dimension, entry in scores.items():
            score = entry.get("score")
            if not isinstance(score, int) or not 0 <= score <= 5 or not entry.get("evidence"):
                errors.append(f"QUALITY/{cid}/{dimension}: score/evidence invalid")
        if not item.get("structural_holds"):
            errors.append(f"QUALITY/{cid}: independent-review HOLDs missing")
    overall = review.get("overall", {})
    if overall.get("creative_quality") != "PENDING_INDEPENDENT_REVIEW":
        errors.append("QUALITY: creative quality must remain pending independent review")
    if overall.get("production_promotion") != "NOT_RUN":
        errors.append("QUALITY: production promotion must not run")

    expected_global = {
        "phase_2": "RESEARCH_DELIVERED",
        "macro_arc_diversity": "PENDING_INDEPENDENT_REVIEW",
        "longform_sustainability": "PENDING_INDEPENDENT_REVIEW",
        "material_adaptation": "REVIEW_REQUIRED",
        "creative_quality": "PENDING_INDEPENDENT_REVIEW",
        "production_promotion": "NOT_RUN",
        "stage_4_creation": "HOLD",
    }
    if research.get("global_status") != expected_global:
        errors.append("STATUS: required research-only disposition changed")

    warnings.append("Semantic truth and literary quality remain outside deterministic validation.")
    warnings.append("Model-pass isolation is REQUESTED_NOT_MACHINE_PROVEN, not a strict blind test.")
    return {
        "ok": not errors,
        "structural_gate": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
        "candidate_count": len(candidates),
        "causal_engine_count": len(set(engines)),
        "material_query_count": len(queries),
        "phase_2": "RESEARCH_DELIVERED" if not errors else "HOLD",
        "macro_arc_diversity": "PENDING_INDEPENDENT_REVIEW",
        "longform_sustainability": "PENDING_INDEPENDENT_REVIEW",
        "material_adaptation": "REVIEW_REQUIRED",
        "creative_quality": "PENDING_INDEPENDENT_REVIEW",
        "production_promotion": "NOT_RUN",
        "stage_4_creation": "HOLD",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", type=Path, required=True)
    parser.add_argument("--longform", type=Path, required=True)
    parser.add_argument("--material", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--phase1", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = validate(
            read_json(args.research),
            read_json(args.longform),
            read_json(args.material),
            read_json(args.review),
            read_json(args.phase1),
            sha256(args.phase1),
        )
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["ok"] else 1
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
