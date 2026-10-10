#!/usr/bin/env python3
"""Validate the research-only Emotion-to-Story Bridge output directory."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


STATES = {"NOT_OPENED", "OPEN", "ACTIVE", "PARTIALLY_PAID", "PAID", "HOLD"}
ALLOWED_TRANSITIONS = {
    "NOT_OPENED": {"OPEN", "HOLD"},
    "OPEN": {"ACTIVE", "PARTIALLY_PAID", "HOLD"},
    "ACTIVE": {"PARTIALLY_PAID", "PAID", "HOLD"},
    "PARTIALLY_PAID": {"ACTIVE", "PAID", "HOLD"},
    "HOLD": {"OPEN", "ACTIVE", "HOLD"},
    "PAID": set(),
}
SPINE_STAGES = ["trigger", "goal", "resistance", "nodes", "choice", "cost", "payoff", "state_change", "next_entry"]
MATERIAL_MODULES = {
    "golden_finger", "worldbuilding", "cultivation_system", "character_function",
    "plotline", "opening", "arc_structure", "plot_mechanism",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def problem(items: list[dict[str, str]], code: str, where: str, message: str) -> None:
    items.append({"code": code, "where": where, "message": message})


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def verify_git_source(ref: dict[str, Any], source: dict[str, Any], repo: Path, errors: list[dict[str, str]], where: str) -> None:
    commit, package, rel, line = source.get("commit"), source.get("package_subdir"), ref.get("path"), ref.get("line")
    if not all(nonempty(value) for value in (commit, package, rel)) or not isinstance(line, int) or line < 1:
        problem(errors, "MATERIAL_PROVENANCE_INVALID", where, "commit/package/path/line required")
        return
    git_path = f"{str(package).rstrip('/')}/{str(rel).lstrip('/')}"
    run = subprocess.run(["git", "show", f"{commit}:{git_path}"], cwd=repo, capture_output=True)
    if run.returncode:
        problem(errors, "MATERIAL_SOURCE_MISSING", where, git_path)
        return
    lines = run.stdout.decode("utf-8-sig").splitlines()
    if line > len(lines):
        problem(errors, "MATERIAL_SOURCE_LINE_MISSING", where, f"{git_path}:{line}")
        return
    raw = lines[line - 1]
    try:
        row = json.loads(raw)
    except json.JSONDecodeError:
        problem(errors, "MATERIAL_SOURCE_ROW_INVALID", where, "source row is not JSON")
        return
    source_id = ref.get("source_record_id", ref.get("record_id"))
    if row.get("record_id") != source_id:
        problem(errors, "MATERIAL_SOURCE_ID_MISMATCH", where, str(source_id))
    if hashlib.sha256(raw.encode("utf-8")).hexdigest() != ref.get("source_line_sha256"):
        problem(errors, "MATERIAL_SOURCE_HASH_MISMATCH", where, str(source_id))


def validate_transitions(
    transitions: Any, node_positions: dict[str, int], nodes: dict[str, dict[str, Any]],
    errors: list[dict[str, str]], where: str,
) -> tuple[str, int | None]:
    state = "NOT_OPENED"
    last_position = -1
    paid_position: int | None = None
    if not isinstance(transitions, list) or not transitions:
        problem(errors, "STATE_TRANSITIONS_MISSING", where, "non-empty transition list required")
        return state, paid_position
    for index, transition in enumerate(transitions):
        point = f"{where}[{index}]"
        node_id = transition.get("node_id") if isinstance(transition, dict) else None
        before, after = transition.get("from"), transition.get("to")
        if node_id not in node_positions:
            problem(errors, "STATE_NODE_UNKNOWN", point, str(node_id))
            continue
        if node_positions[node_id] < last_position:
            problem(errors, "STATE_TIME_REVERSED", point, "state transitions must follow story node order")
        last_position = node_positions[node_id]
        if before != state or before not in STATES or after not in STATES or after not in ALLOWED_TRANSITIONS.get(before, set()):
            problem(errors, "STATE_TRANSITION_INVALID", point, f"expected from={state}, got {before}->{after}")
        additions = transition.get("reader_knowledge_added", [])
        reveals = nodes[node_id].get("reveals", [])
        if not isinstance(additions, list) or any(item not in reveals for item in additions):
            problem(errors, "PREMATURE_READER_KNOWLEDGE", point, "knowledge must be revealed by the same node")
        state = after
        if after == "PAID":
            paid_position = node_positions[node_id]
    return state, paid_position


def validate_materials(option: dict[str, Any], errors: list[dict[str, str]], warnings: list[dict[str, str]], where: str,
                       source_repo: Path | None, material_source: dict[str, Any]) -> None:
    slots = option.get("material_slots", [])
    if not isinstance(slots, list) or not slots:
        problem(errors, "MATERIAL_SLOTS_MISSING", where, "functional slots required")
        return
    modules = {slot.get("module") for slot in slots if isinstance(slot, dict)}
    if modules != MATERIAL_MODULES:
        problem(errors, "MATERIAL_MODULE_COVERAGE", where, f"expected 02-09, got {sorted(str(item) for item in modules)}")
    slot_ids: set[str] = set()
    selected_ids: set[str] = set()
    rejected = 0
    for index, slot in enumerate(slots):
        point = f"{where}.material_slots[{index}]"
        slot_id = slot.get("slot_id")
        if not nonempty(slot_id) or slot_id in slot_ids:
            problem(errors, "MATERIAL_SLOT_ID_INVALID", point, str(slot_id))
        slot_ids.add(slot_id)
        if slot.get("selection_order") != "FUNCTION_FIRST_SOURCE_SECOND":
            problem(errors, "MATERIAL_ORDER_INVALID", point, "function-first marker required")
        decision = slot.get("decision")
        selected = slot.get("selected_ref")
        if decision in {"SELECT_DIRECT", "SELECT_ADAPT"}:
            if not isinstance(selected, dict):
                problem(errors, "MATERIAL_SELECTION_MISSING", point, "selected source required")
            else:
                selected_ids.add(str(selected.get("material_id")))
                if source_repo:
                    verify_git_source(selected, material_source, source_repo, errors, point)
            if decision == "SELECT_ADAPT":
                bridge = slot.get("adaptation_bridge", {})
                for field in ("new_rule", "cost_or_constraint", "changed_state", "why_causal", "provenance"):
                    if not nonempty(bridge.get(field)):
                        problem(errors, "ADAPTATION_BRIDGE_INCOMPLETE", point, field)
                if bridge.get("provenance") != "ORIGINAL_DESIGN":
                    problem(errors, "ADAPTATION_ORIGIN_INVALID", point, "bridge must be ORIGINAL_DESIGN")
        elif decision == "ORIGINAL_DESIGN":
            if selected is not None or not nonempty(slot.get("gap_reason")):
                problem(errors, "ORIGINAL_SLOT_INVALID", point, "original design requires no source and an explicit gap reason")
        else:
            problem(errors, "MATERIAL_DECISION_INVALID", point, str(decision))
        rejects = slot.get("rejected_refs", [])
        if not isinstance(rejects, list):
            problem(errors, "MATERIAL_REJECTIONS_INVALID", point, "rejected_refs must be an array")
        else:
            rejected += len(rejects)
            for reject in rejects:
                if not nonempty(reject.get("reason")):
                    problem(errors, "MATERIAL_REJECTION_UNEXPLAINED", point, "rejection reason required")
        constraints = slot.get("constraint_checks", {})
        if set(constraints) != {"ability", "resource", "world", "character"}:
            problem(errors, "MATERIAL_CONSTRAINTS_INCOMPLETE", point, "ability/resource/world/character checks required")
        if not nonempty(slot.get("effect_on_action_or_payoff")):
            problem(errors, "MATERIAL_EFFECT_MISSING", point, "actual story effect required")

    nodes = option.get("story_nodes", [])
    use_sets: list[frozenset[str]] = []
    for index, node in enumerate(nodes):
        point = f"{where}.story_nodes[{index}]"
        uses = node.get("material_uses", [])
        if not isinstance(uses, list):
            problem(errors, "NODE_MATERIAL_USES_INVALID", point, "array required")
            continue
        ids = frozenset(str(use.get("material_ref")) for use in uses)
        use_sets.append(ids)
        for use in uses:
            if use.get("slot_id") not in slot_ids or not nonempty(use.get("role_at_node")) or not nonempty(use.get("effect_on_action")):
                problem(errors, "NODE_MATERIAL_USE_INVALID", point, "slot, role and effect required")
    nonempty_sets = [item for item in use_sets if item]
    if len(selected_ids) >= 2 and len(nonempty_sets) >= 2 and len(set(nonempty_sets)) == 1 and next(iter(nonempty_sets)) == selected_ids:
        problem(errors, "BLANKET_MATERIAL_ATTACHMENT", where, "all selected materials may not be attached to every node")
    if rejected == 0:
        problem(warnings, "NO_REJECTED_MATERIAL_EXAMPLE", where, "pilot should retain at least one rejected real candidate")


def validate_option(option: dict[str, Any], mode: str, retrieval_ids: dict[str, set[str]], errors: list[dict[str, str]],
                    warnings: list[dict[str, str]], where: str, source_repo: Path | None, material_source: dict[str, Any]) -> None:
    if option.get("mode") != mode or option.get("status") != "candidate" or option.get("qa_status") != "HOLD":
        problem(errors, "OPTION_ENVELOPE_INVALID", where, "mode and candidate/HOLD required")
    if option.get("research_state_scope") != "PLANNED_RESEARCH_STATE_NOT_OBSERVED":
        problem(errors, "RESEARCH_STATE_SCOPE_INVALID", where, "planned state must not masquerade as observed chapters")
    nodes_list = option.get("story_nodes", [])
    if not isinstance(nodes_list, list) or len(nodes_list) < 7:
        problem(errors, "STORY_NODES_TOO_THIN", where, "at least seven causal nodes required")
        return
    node_ids = [node.get("node_id") for node in nodes_list]
    if len(set(node_ids)) != len(node_ids) or any(not nonempty(item) for item in node_ids):
        problem(errors, "STORY_NODE_IDS_INVALID", where, "unique nonempty node IDs required")
    nodes = {node["node_id"]: node for node in nodes_list if nonempty(node.get("node_id"))}
    positions = {node_id: index for index, node_id in enumerate(node_ids)}
    for index, node in enumerate(nodes_list):
        point = f"{where}.story_nodes[{index}]"
        for field in ("chapter_range", "cause", "event", "character_choice", "consequence"):
            if not nonempty(node.get(field)):
                problem(errors, "CAUSAL_NODE_INCOMPLETE", point, field)
        if not isinstance(node.get("decision_makers"), list) or not node.get("decision_makers"):
            problem(errors, "NODE_AGENCY_MISSING", point, "decision makers required")

    phases = option.get("chapter_phases", [])
    if [phase.get("range") for phase in phases] != ["1-10", "11-25", "26-40", "41-50"]:
        problem(errors, "FIFTY_CHAPTER_PHASES_INVALID", where, "exact 1-10/11-25/26-40/41-50 phases required")
    spine = option.get("story_spine", {}).get("stages", [])
    if [stage.get("stage") for stage in spine] != SPINE_STAGES:
        problem(errors, "STORY_SPINE_INVALID", where, "exact nine-stage spine required")
    validate_materials(option, errors, warnings, where, source_repo, material_source)

    if mode == "E2_E3_ENABLED":
        source_uses = option.get("emotion_source_uses", [])
        if not isinstance(source_uses, list) or not source_uses:
            problem(errors, "EMOTION_LIBRARY_UNUSED", where, "enhanced option must consume retrieved EL/EW/MA/AH records")
        else:
            for use in source_uses:
                kind, record_id = use.get("record_kind"), use.get("record_id")
                if record_id not in retrieval_ids.get(kind, set()):
                    problem(errors, "EMOTION_SOURCE_NOT_RETRIEVED", where, f"{kind}:{record_id}")
                for field in ("similarity_reason", "transferable_part", "reuse_limit"):
                    if not nonempty(use.get(field)):
                        problem(errors, "EMOTION_SOURCE_USE_INCOMPLETE", where, field)

        lines = option.get("emotion_lines", [])
        if len(lines) < 4:
            problem(errors, "EMOTION_LINES_TOO_FEW", where, "four independent lines required")
        line_ids = {line.get("line_id") for line in lines}
        domains = [line.get("payoff_domain") for line in lines]
        contracts = [line.get("payoff_contract") for line in lines]
        if len(set(domains)) != len(domains) or len(set(contracts)) != len(contracts):
            problem(errors, "PAYOFF_CONTRACTS_NOT_DISTINCT", where, "line payoffs must remain independent")
        relationship_lines = set()
        for index, line in enumerate(lines):
            point = f"{where}.emotion_lines[{index}]"
            final, _ = validate_transitions(line.get("state_transitions"), positions, nodes, errors, point)
            if line.get("line_role") == "RELATIONSHIP_AGENCY":
                relationship_lines.add(line.get("line_id"))
            if final == "NOT_OPENED":
                problem(errors, "EMOTION_LINE_NEVER_OPENED", point, "line must enter the plan")

        macros = option.get("macro_arcs", [])
        if len(macros) != 2:
            problem(errors, "MACRO_COUNT_INVALID", where, "exactly two macro arcs required")
            return
        macro_positions: list[tuple[int | None, int | None]] = []
        for index, macro in enumerate(macros):
            point = f"{where}.macro_arcs[{index}]"
            _, paid_position = validate_transitions(macro.get("state_transitions"), positions, nodes, errors, point)
            first_position = positions.get(macro.get("state_transitions", [{}])[0].get("node_id")) if macro.get("state_transitions") else None
            macro_positions.append((first_position, paid_position))
        if len(macro_positions) == 2:
            a_paid, b_open = macro_positions[0][1], macro_positions[1][0]
            if a_paid is None or b_open is None or b_open >= a_paid:
                problem(errors, "OVERLAP_NOT_ESTABLISHED", where, "macro B must open before macro A is paid")
        handoff = option.get("handoff", {})
        if handoff.get("old_arc_contract_retained") != macros[0].get("settlement_contract"):
            problem(errors, "OLD_ARC_CONTRACT_CANCELLED", where, "handoff must retain macro A contract verbatim")
        if handoff.get("dominance_transfer_status") != "CANDIDATE_UNVERIFIED":
            problem(errors, "HANDOFF_OVERCLAIM", where, "dominance transfer must remain unverified")
        if not handoff.get("withheld_questions"):
            problem(errors, "NEXT_ARC_OVERDISCLOSED", where, "new arc must retain unresolved questions")

        agency_changed = False
        for weave in option.get("weaves", []):
            if weave.get("from_line_id") not in line_ids or weave.get("to_line_id") not in line_ids or weave.get("node_id") not in nodes:
                problem(errors, "WEAVE_REFERENCE_INVALID", where, str(weave.get("weave_id")))
            if not nonempty(weave.get("causal_bridge")) or not nonempty(weave.get("effect_on_choice")):
                problem(errors, "WEAVE_CAUSALITY_MISSING", where, str(weave.get("weave_id")))
            if weave.get("from_line_id") in relationship_lines or weave.get("to_line_id") in relationship_lines:
                agency_changed = agency_changed or len(nodes.get(weave.get("node_id"), {}).get("decision_makers", [])) >= 2
        if not agency_changed:
            problem(errors, "RELATIONSHIP_AGENCY_DECORATIVE", where, "relationship line must change a multi-actor choice")
    else:
        forbidden = {"emotion_source_uses", "emotion_lines", "weaves", "macro_arcs", "handoff"}
        leaked = sorted(forbidden & set(option))
        if leaked:
            problem(errors, "LEGACY_PATH_POLLUTED", where, f"unexpected E2/E3 fields: {leaked}")


def validate_output(root: Path, source_repo: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    required_files = ["sparse-brief.json", "emotion-library-retrieval.json", "enhanced-options.json", "legacy-options.json", "fair-comparison.json", "run-manifest.json"]
    for filename in required_files:
        if not (root / filename).is_file():
            problem(errors, "OUTPUT_FILE_MISSING", str(root), filename)
    if errors:
        return {"ok": False, "structural_gate": "FAIL", "errors": errors, "warnings": warnings}
    brief, retrieval = load(root / "sparse-brief.json"), load(root / "emotion-library-retrieval.json")
    enhanced, legacy = load(root / "enhanced-options.json"), load(root / "legacy-options.json")
    manifest = load(root / "run-manifest.json")
    if brief.get("input_mode") != "SPARSE_EMOTION_BRIEF":
        problem(errors, "INPUT_MODE_INVALID", "brief", "SPARSE_EMOTION_BRIEF required")
    fingerprint = hashlib.sha256(json.dumps(brief, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    if manifest.get("brief_sha256") != fingerprint:
        problem(errors, "BRIEF_FINGERPRINT_MISMATCH", "run-manifest", "same frozen sparse brief required")
    if manifest.get("emotion_library_consumption") != "EXECUTED_RESEARCH" or manifest.get("production_promotion") != "NOT_RUN":
        problem(errors, "RUN_STATUS_INVALID", "run-manifest", "research consumption and no promotion required")
    retrieval_ids = {
        "line": {item.get("record_id") for item in retrieval.get("line_matches", [])},
        "weave": {item.get("record_id") for item in retrieval.get("weave_matches", [])},
        "macro": {item.get("record_id") for item in retrieval.get("macro_matches", [])},
        "handoff": {item.get("record_id") for item in retrieval.get("handoff_matches", [])},
    }
    material_source = manifest.get("material_source", {})
    enhanced_options = enhanced.get("options", [])
    legacy_options = legacy.get("options", [])
    if len(enhanced_options) < 2 or len(legacy_options) < 2:
        problem(errors, "OPTION_COUNT_INVALID", "options", "both paths require at least two options")
    if {item.get("pair_id") for item in enhanced_options} != {item.get("pair_id") for item in legacy_options}:
        problem(errors, "FAIR_PAIRING_INVALID", "options", "legacy/enhanced pair IDs must match")
    for index, option in enumerate(enhanced_options):
        validate_option(option, "E2_E3_ENABLED", retrieval_ids, errors, warnings, f"enhanced[{index}]", source_repo, material_source)
    for index, option in enumerate(legacy_options):
        validate_option(option, "LEGACY_BASELINE", retrieval_ids, errors, warnings, f"legacy[{index}]", source_repo, material_source)
    signatures = [tuple(option.get("causal_signature", {}).values()) for option in enhanced_options]
    if len(set(signatures)) != len(signatures):
        problem(errors, "OPTIONS_ONLY_RENAMED", "enhanced", "causal signatures must differ")
    comparison = load(root / "fair-comparison.json")
    if comparison.get("creative_quality") != "PENDING_INDEPENDENT_REVIEW" or comparison.get("evaluation_basis") == "field_count":
        problem(errors, "QUALITY_OVERCLAIM", "fair-comparison", "human semantic review must remain pending")
    return {
        "ok": not errors,
        "structural_gate": "PASS" if not errors else "FAIL",
        "emotion_library_consumption": "EXECUTED_RESEARCH" if not errors else "FAILED",
        "material_adaptation": "REVIEW_REQUIRED",
        "creative_quality": "PENDING_INDEPENDENT_REVIEW",
        "production_promotion": "NOT_RUN",
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Emotion-to-Story Bridge research output.")
    parser.add_argument("output_root", type=Path)
    parser.add_argument("--source-repo", type=Path)
    args = parser.parse_args()
    try:
        result = validate_output(args.output_root, args.source_repo.resolve() if args.source_repo else None)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result = {"ok": False, "structural_gate": "FAIL", "errors": [{"code": "INPUT_ERROR", "where": "runtime", "message": str(exc)}], "warnings": []}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
