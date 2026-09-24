#!/usr/bin/env python3
"""Validate the structural gates of a novel creation plan JSON file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


PHASES = ("1-3", "4-10", "11-30", "31-60", "61-120", "121-200", "201-300")
PLAN_FIELDS = {
    "schema_version",
    "plan_id",
    "status",
    "creation_mode",
    "plan_mode",
    "brief",
    "shared_library_root",
    "market_evidence",
    "library_usage",
    "concept_options",
    "recommendation",
    "architecture_concept_id",
    "architecture_300",
    "longline_engine_summary",
    "debt_ledgers",
    "material_gap_orders",
    "pending_decisions",
}
CONCEPT_FIELDS = {
    "concept_id",
    "positioning",
    "reader_promise",
    "protagonist",
    "golden_finger",
    "relationship_topology",
    "world_cultivation_resource_loop",
    "named_story_bible",
    "opening_1_10",
    "story_engine",
    "longline_engine_summary",
    "market_signal_ids",
    "material_mapping",
    "differentiation_signature",
    "originality_changes",
    "risks",
    "score",
    "score_breakdown",
    "hard_gate",
}
PHASE_FIELDS = {
    "range",
    "central_question",
    "protagonist_goal",
    "conflict",
    "characters",
    "growth_and_resources",
    "emotion_payoff",
    "mainline_progress",
    "fatigue_refresh",
    "structure_refresh",
    "irreversible_change",
    "material_support",
}
SCORE_WEIGHTS = {
    "market_reader_promise": 15,
    "opening_1_10": 15,
    "long_engine_61_300": 20,
    "mechanic_world_resource_fit": 15,
    "relationship_sustainability": 10,
    "emotion_pacing": 10,
    "originality_distance": 10,
    "material_feasibility": 5,
}
DEBT_KEYS = {
    "emotion",
    "growth",
    "resource",
    "relationship",
    "world_rule",
    "antagonist",
    "mainline_foreshadowing",
}
SIGNATURE_FIELDS = {
    "reader_promise",
    "protagonist_identity_goal",
    "golden_finger_logic",
    "relationship_topology",
    "central_conflict",
    "resource_loop",
    "world_institution",
    "longline_mystery",
}
OPENING_FIELDS = {"chapter", "primary_event", "emotion", "payoff", "hook"}
MARKET_SIGNAL_FIELDS = {"signal_id", "signal_type", "claim", "evidence_sample_ids"}
MARKET_SAMPLE_FIELDS = {"sample_id", "rank", "title", "content_status", "analyzed_chapters", "opening_analysis"}
DEBT_ITEM_FIELDS = {
    "debt_id",
    "opened_phase",
    "promise",
    "payoff_window",
    "visible_evidence",
    "status",
    "planned_payoff",
    "overdue_risk",
}
ANTAGONIST_DEBT_FIELDS = {
    "antagonist_goal",
    "pressure_escalation",
    "stage_failure_or_payoff",
    "exit_window",
}
GAP_ORDER_FIELDS = {
    "gap_order_id",
    "needed_function",
    "target_phase",
    "target_emotion",
    "prerequisites",
    "acceptance_evidence",
    "forbidden_patterns",
}
DISPATCH_FIELDS = {
    "status",
    "slots",
    "source_concentration_risks",
    "compatibility_checks",
    "stop_reason",
}
DISPATCH_SLOT_FIELDS = {
    "slot_id",
    "role",
    "required",
    "wave",
    "modules",
    "component_types",
    "query_groups",
    "target_candidates",
    "source_strategy",
    "selected_refs",
    "rejected_refs",
    "gap_reason",
}
DISPATCH_REF_FIELDS = {
    "material_id",
    "material_kind",
    "module",
    "record_id",
    "qa_status",
}
COMPATIBILITY_FIELDS = {
    "check_id",
    "materials",
    "dimension",
    "result",
    "reason",
}


def require_keys(errors: list[str], value: Any, keys: set[str], where: str) -> None:
    if not isinstance(value, dict):
        errors.append(f"{where} must be an object")
        return
    missing = sorted(keys - set(value))
    if missing:
        errors.append(f"{where} missing: {', '.join(missing)}")


def is_empty(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def normalized(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Validate a candidate novel creation plan.")
    parser.add_argument("target", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.target.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "errors": [str(exc)]}, ensure_ascii=False, indent=2))
        return 1

    errors: list[str] = []
    require_keys(errors, data, PLAN_FIELDS, "plan")
    if not isinstance(data, dict):
        print(json.dumps({"ok": False, "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    schema_version = data.get("schema_version")
    if schema_version not in {1, 2}:
        errors.append("schema_version must be 1 or 2")
    if schema_version == 2 and "material_dispatch" not in data:
        errors.append("schema_version 2 requires material_dispatch")
    if data.get("status") != "candidate":
        errors.append("plan.status must remain candidate until user confirmation")
    creation_mode = data.get("creation_mode")
    if creation_mode not in {"greenfield", "existing_project"}:
        errors.append("creation_mode must be greenfield or existing_project")
    shared_library_root = data.get("shared_library_root")
    if not isinstance(shared_library_root, str) or not shared_library_root.strip():
        errors.append("shared_library_root must be a non-empty absolute path")
    elif not Path(shared_library_root).is_absolute():
        errors.append("shared_library_root must be an absolute path")
    plan_mode = data.get("plan_mode")
    if plan_mode not in {"preliminary", "full"}:
        errors.append("plan_mode must be preliminary or full")

    library_usage = data.get("library_usage")
    require_keys(errors, library_usage, {"formal_card_ids", "dna_candidate_ids", "gaps"}, "library_usage")
    if isinstance(library_usage, dict):
        for key in ("formal_card_ids", "dna_candidate_ids", "gaps"):
            if not isinstance(library_usage.get(key), list):
                errors.append(f"library_usage.{key} must be a list")
        if not any(library_usage.get(key) for key in ("formal_card_ids", "dna_candidate_ids", "gaps")):
            errors.append("library_usage must contain a material reference or an explicit gap")


    if schema_version == 2:
        dispatch = data.get("material_dispatch")
        require_keys(errors, dispatch, DISPATCH_FIELDS, "material_dispatch")
        if isinstance(dispatch, dict):
            if dispatch.get("status") not in {"complete", "partial", "hold"}:
                errors.append("material_dispatch.status must be complete, partial, or hold")
            slots = dispatch.get("slots")
            if not isinstance(slots, list) or not slots:
                errors.append("material_dispatch.slots must be a non-empty list")
            else:
                slot_ids: set[str] = set()
                for index, slot in enumerate(slots):
                    where = f"material_dispatch.slots[{index}]"
                    require_keys(errors, slot, DISPATCH_SLOT_FIELDS, where)
                    if not isinstance(slot, dict):
                        continue
                    slot_id = slot.get("slot_id")
                    if is_empty(slot_id):
                        errors.append(f"{where}.slot_id cannot be empty")
                    elif str(slot_id) in slot_ids:
                        errors.append(f"{where}.slot_id must be unique")
                    else:
                        slot_ids.add(str(slot_id))
                    if is_empty(slot.get("role")):
                        errors.append(f"{where}.role cannot be empty")
                    if not isinstance(slot.get("required"), bool):
                        errors.append(f"{where}.required must be boolean")
                    if slot.get("wave") not in {1, 2, 3, 4}:
                        errors.append(f"{where}.wave must be 1..4")
                    for field in ("modules", "component_types", "query_groups", "selected_refs", "rejected_refs"):
                        if not isinstance(slot.get(field), list):
                            errors.append(f"{where}.{field} must be a list")
                    target_candidates = slot.get("target_candidates")
                    if not isinstance(target_candidates, int) or not 1 <= target_candidates <= 12:
                        errors.append(f"{where}.target_candidates must be an integer 1..12")
                    if slot.get("source_strategy") not in {"cross_book", "same_source_bundle", "either"}:
                        errors.append(f"{where}.source_strategy is invalid")
                    selected_refs = slot.get("selected_refs")
                    if isinstance(selected_refs, list):
                        for ref_index, ref in enumerate(selected_refs):
                            ref_where = f"{where}.selected_refs[{ref_index}]"
                            require_keys(errors, ref, DISPATCH_REF_FIELDS, ref_where)
                            if not isinstance(ref, dict):
                                continue
                            for field in DISPATCH_REF_FIELDS:
                                if is_empty(ref.get(field)):
                                    errors.append(f"{ref_where}.{field} cannot be empty")
                            kind = ref.get("material_kind")
                            if kind not in {"formal_card", "dna_record", "dna_component"}:
                                errors.append(f"{ref_where}.material_kind is invalid")
                            material_id = str(ref.get("material_id") or "")
                            if isinstance(library_usage, dict) and material_id:
                                if kind == "formal_card":
                                    allowed = set(map(str, library_usage.get("formal_card_ids", [])))
                                    if material_id not in allowed:
                                        errors.append(f"{ref_where}.material_id absent from library_usage.formal_card_ids")
                                elif kind in {"dna_record", "dna_component"}:
                                    allowed = set(map(str, library_usage.get("dna_candidate_ids", [])))
                                    if material_id not in allowed:
                                        errors.append(f"{ref_where}.material_id absent from library_usage.dna_candidate_ids")
                            if kind == "dna_component" and is_empty(ref.get("record_id")):
                                errors.append(f"{ref_where}: dna_component requires source record_id")
                    if slot.get("required") and not slot.get("selected_refs") and is_empty(slot.get("gap_reason")):
                        errors.append(f"{where}: required slot needs selected_refs or gap_reason")
            risks = dispatch.get("source_concentration_risks")
            if not isinstance(risks, list):
                errors.append("material_dispatch.source_concentration_risks must be a list")
            checks = dispatch.get("compatibility_checks")
            if not isinstance(checks, list):
                errors.append("material_dispatch.compatibility_checks must be a list")
            else:
                for index, check in enumerate(checks):
                    where = f"material_dispatch.compatibility_checks[{index}]"
                    require_keys(errors, check, COMPATIBILITY_FIELDS, where)
                    if not isinstance(check, dict):
                        continue
                    if not isinstance(check.get("materials"), list) or len(check.get("materials", [])) < 2:
                        errors.append(f"{where}.materials must contain at least two material ids")
                    if check.get("result") not in {"PASS", "HOLD", "FAIL"}:
                        errors.append(f"{where}.result must be PASS, HOLD, or FAIL")
                    for field in ("check_id", "dimension", "reason"):
                        if is_empty(check.get(field)):
                            errors.append(f"{where}.{field} cannot be empty")
            if dispatch.get("status") in {"complete", "partial"} and is_empty(dispatch.get("stop_reason")):
                errors.append("material_dispatch.stop_reason is required for complete/partial status")

    evidence = data.get("market_evidence")
    sample_ids: set[str] = set()
    signal_ids: set[str] = set()
    complete_text_samples = 0
    if isinstance(evidence, dict):
        for key in ("as_of", "sources", "samples", "signals", "coverage_status", "bias_notes"):
            if key not in evidence:
                errors.append(f"market_evidence.{key} is required")
        for key in ("as_of", "sources", "samples"):
            if not evidence.get(key):
                errors.append(f"market_evidence.{key} cannot be empty")
        samples = evidence.get("samples")
        if not isinstance(samples, list):
            errors.append("market_evidence.samples must be a list")
        else:
            for index, sample in enumerate(samples):
                require_keys(errors, sample, MARKET_SAMPLE_FIELDS, f"market_evidence.samples[{index}]")
                if not isinstance(sample, dict):
                    continue
                if is_empty(sample.get("sample_id")):
                    errors.append(f"market_evidence.samples[{index}].sample_id cannot be empty")
                else: sample_ids.add(str(sample["sample_id"]))
                if sample.get("content_status") not in {"pass", "partial", "metadata_only", "failed"}:
                    errors.append(f"market_evidence.samples[{index}].content_status is invalid")
                chapters = sample.get("analyzed_chapters")
                if not isinstance(chapters, list):
                    errors.append(f"market_evidence.samples[{index}].analyzed_chapters must be a list")
                if sample.get("content_status") == "pass":
                    if chapters != list(range(1, 11)):
                        errors.append(f"market_evidence.samples[{index}] pass requires analyzed_chapters [1..10]")
                    if is_empty(sample.get("opening_analysis")):
                        errors.append(f"market_evidence.samples[{index}] pass requires opening_analysis")
                    if chapters == list(range(1, 11)) and not is_empty(sample.get("opening_analysis")):
                        complete_text_samples += 1
            if len(sample_ids) != len(samples):
                errors.append("market_evidence sample_id values must be unique")
            if len(samples) != 10:
                errors.append("market_evidence.samples must preserve the ranking top 10")
        signals = evidence.get("signals")
        if not isinstance(signals, list) or not signals:
            errors.append("market_evidence.signals must be a non-empty list")
        else:
            for index, signal in enumerate(signals):
                require_keys(errors, signal, MARKET_SIGNAL_FIELDS, f"market_evidence.signals[{index}]")
                if not isinstance(signal, dict):
                    continue
                for key in MARKET_SIGNAL_FIELDS:
                    if is_empty(signal.get(key)):
                        errors.append(f"market_evidence.signals[{index}].{key} cannot be empty")
                if signal.get("signal_id"):
                    signal_ids.add(str(signal["signal_id"]))
                refs = signal.get("evidence_sample_ids")
                if not isinstance(refs, list) or not refs:
                    errors.append(f"market_evidence.signals[{index}].evidence_sample_ids must be a non-empty list")
                else:
                    missing_refs = sorted({str(item) for item in refs} - sample_ids)
                    if missing_refs:
                        errors.append(f"market_evidence.signals[{index}] unknown sample ids: {', '.join(missing_refs)}")
            if len(signal_ids) != len(signals):
                errors.append("market_evidence signal_id values must be unique")
        coverage_status = evidence.get("coverage_status")
        if coverage_status not in {"complete", "partial"}:
            errors.append("market_evidence.coverage_status must be complete or partial")
        if isinstance(samples, list) and len(samples) < 6:
            if coverage_status != "partial" or not evidence.get("bias_notes"):
                errors.append("fewer than 6 samples requires coverage_status=partial and non-empty bias_notes")
    else:
        errors.append("market_evidence must be an object")

    concepts = data.get("concept_options")
    concept_ids: list[str] = []
    if not isinstance(concepts, list) or len(concepts) != 3:
        errors.append("concept_options must contain exactly three concepts")
    else:
        signatures: list[dict[str, Any]] = []
        for index, concept in enumerate(concepts):
            require_keys(errors, concept, CONCEPT_FIELDS, f"concept_options[{index}]")
            if not isinstance(concept, dict):
                continue
            concept_id = concept.get("concept_id")
            if isinstance(concept_id, str):
                concept_ids.append(concept_id)
            for key in CONCEPT_FIELDS - {"score", "score_breakdown", "hard_gate"}:
                if is_empty(concept.get(key)):
                    errors.append(f"concept_options[{index}].{key} cannot be empty")
            if concept.get("hard_gate") not in {"PASS", "HOLD", "FAIL"}:
                errors.append(f"concept_options[{index}].hard_gate must be PASS, HOLD, or FAIL")
            opening = concept.get("opening_1_10")
            if not isinstance(opening, list) or len(opening) != 10:
                errors.append(f"concept_options[{index}].opening_1_10 must contain exactly 10 chapter objects")
            else:
                observed_chapters: list[Any] = []
                for chapter_index, chapter in enumerate(opening):
                    require_keys(errors, chapter, OPENING_FIELDS, f"concept_options[{index}].opening_1_10[{chapter_index}]")
                    if isinstance(chapter, dict):
                        observed_chapters.append(chapter.get("chapter"))
                        for key in OPENING_FIELDS - {"chapter"}:
                            if is_empty(chapter.get(key)):
                                errors.append(f"concept_options[{index}].opening_1_10[{chapter_index}].{key} cannot be empty")
                if observed_chapters != list(range(1, 11)):
                    errors.append(f"concept_options[{index}].opening_1_10 chapter values must be 1..10")
            signals = concept.get("market_signal_ids")
            if not isinstance(signals, list) or not signals or any(is_empty(item) for item in signals):
                errors.append(f"concept_options[{index}].market_signal_ids must be a non-empty list")
            elif not set(map(str, signals)).issubset(signal_ids):
                errors.append(f"concept_options[{index}].market_signal_ids contains unknown ids")
            mapping = concept.get("material_mapping")
            require_keys(errors, mapping, {"formal_card_ids", "dna_candidate_ids", "gaps"}, f"concept_options[{index}].material_mapping")
            if isinstance(mapping, dict):
                for key in ("formal_card_ids", "dna_candidate_ids", "gaps"):
                    if not isinstance(mapping.get(key), list):
                        errors.append(f"concept_options[{index}].material_mapping.{key} must be a list")
                if not any(mapping.get(key) for key in ("formal_card_ids", "dna_candidate_ids", "gaps")):
                    errors.append(f"concept_options[{index}].material_mapping must contain a material reference or gap")
                if isinstance(library_usage, dict):
                    for key in ("formal_card_ids", "dna_candidate_ids", "gaps"):
                        values = mapping.get(key)
                        allowed = library_usage.get(key)
                        if isinstance(values, list) and isinstance(allowed, list) and not set(map(str, values)).issubset(set(map(str, allowed))):
                            errors.append(f"concept_options[{index}].material_mapping.{key} contains ids absent from library_usage")
            signature = concept.get("differentiation_signature")
            require_keys(errors, signature, SIGNATURE_FIELDS, f"concept_options[{index}].differentiation_signature")
            if isinstance(signature, dict):
                for key in SIGNATURE_FIELDS:
                    if is_empty(signature.get(key)):
                        errors.append(f"concept_options[{index}].differentiation_signature.{key} cannot be empty")
                signatures.append(signature)
            changes = concept.get("originality_changes")
            if not isinstance(changes, list) or len(changes) < 4:
                errors.append(f"concept_options[{index}].originality_changes must contain at least 4 changes")
            score = concept.get("score")
            if not isinstance(score, (int, float)) or not 0 <= score <= 100:
                errors.append(f"concept_options[{index}].score must be 0..100")
            breakdown = concept.get("score_breakdown")
            if not isinstance(breakdown, dict):
                errors.append(f"concept_options[{index}].score_breakdown must be an object")
            else:
                missing_scores = sorted(set(SCORE_WEIGHTS) - set(breakdown))
                if missing_scores:
                    errors.append(f"concept_options[{index}].score_breakdown missing: {', '.join(missing_scores)}")
                subtotal = 0
                for key, maximum in SCORE_WEIGHTS.items():
                    value = breakdown.get(key)
                    if not isinstance(value, (int, float)) or not 0 <= value <= maximum:
                        errors.append(f"concept_options[{index}].score_breakdown.{key} must be 0..{maximum}")
                    else:
                        subtotal += value
                if isinstance(score, (int, float)) and subtotal != score:
                    errors.append(f"concept_options[{index}].score must equal score_breakdown total")
        if len(set(concept_ids)) != len(concept_ids):
            errors.append("concept_id values must be unique")
        if len(signatures) == 3:
            for left in range(3):
                for right in range(left + 1, 3):
                    differences = sum(
                        normalized(signatures[left].get(key)) != normalized(signatures[right].get(key))
                        for key in SIGNATURE_FIELDS
                    )
                    if differences < 4:
                        errors.append(
                            f"concept_options[{left}] and concept_options[{right}] must differ in at least 4 signature fields"
                        )

    recommendation = data.get("recommendation")
    if isinstance(recommendation, dict):
        selected = recommendation.get("concept_id")
        outcome = recommendation.get("outcome")
        if selected not in concept_ids:
            errors.append("recommendation.concept_id must reference one concept option")
        if outcome not in {"RECOMMEND", "HOLD"}:
            errors.append("recommendation.outcome must be RECOMMEND or HOLD")
        if outcome == "RECOMMEND":
            chosen = next((item for item in concepts or [] if item.get("concept_id") == selected), {})
            if chosen.get("hard_gate") != "PASS" or chosen.get("score", 0) < 80:
                errors.append("RECOMMEND requires hard_gate PASS and score >= 80")
            if complete_text_samples < 6:
                errors.append("RECOMMEND requires at least 6 samples with analyzed chapters 1-10")
    else:
        errors.append("recommendation must be an object")
    recommended_id = recommendation.get("concept_id") if isinstance(recommendation, dict) else None

    architecture = data.get("architecture_300")
    if plan_mode == "preliminary":
        if not data.get("longline_engine_summary"):
            errors.append("preliminary mode requires non-empty longline_engine_summary")
        if architecture not in (None, []):
            errors.append("preliminary mode architecture_300 must be empty or omitted as an empty list")
    elif not isinstance(architecture, list) or len(architecture) != len(PHASES):
        errors.append("full mode architecture_300 must contain seven phase objects")
    else:
        if data.get("architecture_concept_id") != recommended_id:
            errors.append("architecture_concept_id must match recommendation.concept_id")
        observed: list[str] = []
        refresh_count = 0
        referenced_gap_ids: set[str] = set()
        for index, phase in enumerate(architecture):
            require_keys(errors, phase, PHASE_FIELDS, f"architecture_300[{index}]")
            if isinstance(phase, dict):
                observed.append(str(phase.get("range")))
                for key in PHASE_FIELDS - {"range", "structure_refresh"}:
                    if is_empty(phase.get(key)):
                        errors.append(f"architecture_300[{index}].{key} cannot be empty")
                if phase.get("structure_refresh"):
                    refresh_count += 1
                supports = phase.get("material_support")
                if not isinstance(supports, list) or not supports:
                    errors.append(f"architecture_300[{index}].material_support must be a non-empty list")
                else:
                    for support in supports:
                        if not isinstance(support, dict):
                            errors.append(f"architecture_300[{index}].material_support entries must be objects")
                            continue
                        status = support.get("status")
                        if status not in {"SUPPORTED", "ADAPTABLE", "GAP"}:
                            errors.append(f"architecture_300[{index}] material support status is invalid")
                        elif status == "GAP":
                            gap_id = support.get("gap_order_id")
                            if not gap_id:
                                errors.append(f"architecture_300[{index}] GAP support requires gap_order_id")
                            else:
                                referenced_gap_ids.add(str(gap_id))
                                if isinstance(library_usage, dict) and str(gap_id) not in set(map(str, library_usage.get("gaps", []))):
                                    errors.append(f"architecture_300[{index}] GAP id absent from library_usage.gaps")
                        elif not support.get("material_id"):
                            errors.append(f"architecture_300[{index}] {status} support requires material_id")
                        elif isinstance(library_usage, dict):
                            allowed_key = "formal_card_ids" if status == "SUPPORTED" else "dna_candidate_ids"
                            allowed_ids = set(map(str, library_usage.get(allowed_key, [])))
                            if str(support["material_id"]) not in allowed_ids:
                                errors.append(f"architecture_300[{index}] {status} material_id absent from library_usage.{allowed_key}")
        if tuple(observed) != PHASES:
            errors.append(f"architecture_300 ranges must be: {', '.join(PHASES)}")
        if refresh_count < 2:
            errors.append("full plan requires at least two non-empty structure_refresh entries")

        ledgers = data.get("debt_ledgers")
        require_keys(errors, ledgers, DEBT_KEYS, "debt_ledgers")
        if isinstance(ledgers, dict):
            for key in DEBT_KEYS:
                items = ledgers.get(key)
                if not isinstance(items, list) or not items:
                    errors.append(f"debt_ledgers.{key} must be a non-empty list")
                    continue
                required = DEBT_ITEM_FIELDS | (ANTAGONIST_DEBT_FIELDS if key == "antagonist" else set())
                for index, item in enumerate(items):
                    require_keys(errors, item, required, f"debt_ledgers.{key}[{index}]")
                    if isinstance(item, dict):
                        for field in required:
                            if is_empty(item.get(field)):
                                errors.append(f"debt_ledgers.{key}[{index}].{field} cannot be empty")

        orders = data.get("material_gap_orders")
        order_ids: set[str] = set()
        if not isinstance(orders, list):
            errors.append("material_gap_orders must be a list")
        else:
            for index, order in enumerate(orders):
                require_keys(errors, order, GAP_ORDER_FIELDS, f"material_gap_orders[{index}]")
                if isinstance(order, dict):
                    for key in GAP_ORDER_FIELDS:
                        if is_empty(order.get(key)):
                            errors.append(f"material_gap_orders[{index}].{key} cannot be empty")
                    if order.get("gap_order_id"):
                        order_ids.add(str(order["gap_order_id"]))
        missing_orders = sorted(referenced_gap_ids - order_ids)
        if missing_orders:
            errors.append(f"GAP material support missing orders: {', '.join(missing_orders)}")

    result = {"ok": not errors, "errors": errors}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
