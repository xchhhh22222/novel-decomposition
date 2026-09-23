#!/usr/bin/env python3
"""Validate derived JSONL records from novel-opening-miner.

The validator checks deterministic structure only. Whether a scene truly
hooks readers, activates a conflict, proves a selling point, or creates a
continuation driver remains a semantic QA judgment.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable


KINDS = {"per_book", "nearest_neighbor", "cluster", "qa", "handoff", "gap"}
CONFIDENCE = {"HIGH", "MEDIUM", "LOW"}
QA_STATUS = {"PASS", "HOLD", "FAIL"}
BOOK_KINDS = {"per_book", "qa", "gap"}
BOOKS_KINDS = {"nearest_neighbor", "cluster", "handoff"}
CHECKPOINTS = {3, 5, 10, 20}
OPENING_FUNCTIONS = {
    "entry",
    "protagonist_establishment",
    "premise_exposure",
    "golden_finger_reveal",
    "conflict_activation",
    "promise_setup",
    "selling_point_proof",
    "stakes_escalation",
    "first_payoff",
    "continuation_driver",
    "information_pacing",
    "opening_compression",
}
ENTRY_MECHANISMS = {
    "scene",
    "problem",
    "anomaly",
    "desire",
    "risk",
    "promise",
    "information_gap",
    "mixed",
    "UNKNOWN",
}
EXPOSURE_BASES = {"event_result", "rule_demonstration", "explicit_exposition", "mixed", "UNKNOWN"}
EXPOSURE_STATUS = {"partial", "understood", "UNKNOWN"}
MILESTONE_STATUS = {"observed", "partial", "not_yet", "UNKNOWN"}
SUBJECT_TYPES = {"golden_finger", "core_selling_point", "none", "UNKNOWN"}
CONFLICT_SOURCES = {"unresolved_question", "next_goal", "risk", "promise", "state_change", "relationship", "information_gap", "UNKNOWN"}
PROMISE_STATES = {"open", "partially_paid", "paid", "broken_or_failed", "abandoned", "UNKNOWN"}
PRIOR_OBJECT_TYPES = {"promise", "unresolved_question", "opening_goal", "selling_point", "UNKNOWN"}
PAYOFF_DEGREES = {"partial", "substantial", "UNKNOWN"}
STAKE_DIMENSIONS = {"risk", "resource", "identity", "relationship", "time", "goal", "information", "mixed", "UNKNOWN"}
DISCLOSURE_STATES = {"must_know_now", "partially_disclosed", "delayed", "understood", "UNKNOWN"}
COMPRESSION_TYPES = {
    "repeated_explanation",
    "repeated_setup_without_proof",
    "preparation_without_validation",
    "selling_point_delay",
    "repeated_cliffhanger_without_progression",
    "promise_accumulation_without_payoff",
    "conflict_reset_without_escalation",
    "information_overload_without_knowledge_gain",
    "redundant_scene_function",
    "event_density_without_opening_progress",
    "other",
    "UNKNOWN",
}
COMPRESSION_STATUSES = {"observed", "possible", "UNKNOWN"}
ADJACENT_KEYS = {
    "plotline",
    "chapter_emotion",
    "character_function",
    "golden_finger",
    "worldbuilding",
    "cultivation",
    "arc_structure",
    "plot_mechanism",
}
INTERFACE_REFERENCE_KEYS = {"record_id", "interface_type", "evidence_refs", "note", "unknowns"}
NEIGHBOR_DECISIONS = {"merge_candidate", "keep_distinct", "insufficient_evidence"}
CLUSTER_DECISIONS = {
    "candidate_merge",
    "candidate_split",
    "new_candidate",
    "insufficient_evidence",
    "keep_distinct",
    "unclustered",
    "HOLD",
}
HANDOFF_ACTIONS = {"保留", "合并候选", "拆分候选", "补证据", "暂缓"}
ENVELOPE = {
    "record_type",
    "schema_version",
    "record_id",
    "status",
    "evidence_refs",
    "unknowns",
    "confidence",
    "qa_status",
}


def iter_jsonl(target: Path) -> Iterable[tuple[Path, int, str]]:
    paths = sorted(target.rglob("*.jsonl")) if target.is_dir() else [target]
    for path in paths:
        if not path.exists():
            yield path, 0, ""
            continue
        for number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
            yield path, number, raw


def load_completion_manifest(path: Path, expected_books: set[str]) -> list[str]:
    """Validate explicit per-book/gap coverage before cross-book comparison."""
    errors: list[str] = []
    covered: list[str] = []
    if not path.exists():
        return [f"completion manifest not found: {path}"]
    for manifest_path, line, raw in iter_jsonl(path):
        if not raw.strip():
            errors.append(f"{manifest_path}:{line}: empty completion-manifest line")
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"{manifest_path}:{line}: invalid completion-manifest JSON: {exc}")
            continue
        if not isinstance(row, dict) or row.get("record_type") not in {"per_book", "gap"}:
            errors.append(f"{manifest_path}:{line}: completion manifest records must be per_book or gap")
            continue
        book_id = row.get("book_id")
        if not nonempty_string(book_id):
            errors.append(f"{manifest_path}:{line}: completion manifest requires book_id")
            continue
        if row.get("status") != "candidate":
            errors.append(f"{manifest_path}:{line}: completion manifest status must be candidate")
        if row.get("qa_status") not in QA_STATUS:
            errors.append(f"{manifest_path}:{line}: completion manifest qa_status must be PASS/HOLD/FAIL")
        covered.append(book_id)
    duplicates = sorted({book for book in covered if covered.count(book) > 1})
    if duplicates:
        errors.append(f"completion manifest duplicate books: {', '.join(duplicates)}")
    missing = sorted(expected_books - set(covered))
    unexpected = sorted(set(covered) - expected_books)
    if missing:
        errors.append(f"completion manifest missing target books: {', '.join(missing)}")
    if unexpected:
        errors.append(f"completion manifest unexpected books: {', '.join(unexpected)}")
    return errors


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: Any, *, allow_empty: bool = True) -> bool:
    return isinstance(value, list) and (allow_empty or bool(value)) and all(
        nonempty_string(item) for item in value
    )


def ref_list(value: Any, *, allow_empty: bool = False) -> bool:
    if not isinstance(value, list) or (not allow_empty and not value):
        return False
    return all(
        isinstance(item, str)
        and bool(item.strip())
        and len(item.split(":")) >= 3
        and not any(char.isspace() for char in item)
        for item in value
    )


def add_missing(errors: list[str], path: Path, line: int, row: dict[str, Any], fields: set[str]) -> None:
    missing = sorted(field for field in fields if field not in row)
    if missing:
        errors.append(f"{path}:{line}: missing {', '.join(missing)}")


def validate_envelope(
    row: dict[str, Any],
    kind: str,
    path: Path,
    line: int,
    errors: list[str],
    record_ids: set[str],
) -> None:
    add_missing(errors, path, line, row, ENVELOPE)
    if row.get("record_type") != kind:
        errors.append(f"{path}:{line}: record_type must be {kind!r}")
    if row.get("schema_version") != 1:
        errors.append(f"{path}:{line}: schema_version must be 1")

    record_id = row.get("record_id")
    if not nonempty_string(record_id):
        errors.append(f"{path}:{line}: record_id must be a non-empty string")
    elif record_id in record_ids:
        errors.append(f"{path}:{line}: duplicate record_id={record_id}")
    else:
        record_ids.add(record_id)

    if row.get("status") != "candidate":
        errors.append(f"{path}:{line}: status must remain candidate")
    if row.get("confidence") not in CONFIDENCE:
        errors.append(f"{path}:{line}: confidence must be HIGH/MEDIUM/LOW")
    if row.get("qa_status") not in QA_STATUS:
        errors.append(f"{path}:{line}: qa_status must be PASS/HOLD/FAIL")
    if not ref_list(row.get("evidence_refs")):
        errors.append(f"{path}:{line}: evidence_refs must be a non-empty structured-ref list")
    elif nonempty_string(row.get("book_id")):
        foreign = [ref for ref in row["evidence_refs"] if not ref.startswith(f"{row['book_id']}:")]
        if foreign:
            errors.append(f"{path}:{line}: evidence_refs cite another book: {', '.join(foreign)}")
    if not string_list(row.get("unknowns")):
        errors.append(f"{path}:{line}: unknowns must be a list of strings")
    if row.get("confidence") == "HIGH" and row.get("unknowns"):
        errors.append(f"{path}:{line}: HIGH confidence cannot contain unknowns")

    has_book_id = "book_id" in row
    has_book_ids = "book_ids" in row
    if has_book_id == has_book_ids:
        errors.append(f"{path}:{line}: exactly one of book_id or book_ids is required")
    if kind in BOOK_KINDS and not has_book_id:
        errors.append(f"{path}:{line}: {kind} requires book_id")
    if kind in BOOKS_KINDS and not has_book_ids:
        errors.append(f"{path}:{line}: {kind} requires book_ids")
    if has_book_id and not nonempty_string(row.get("book_id")):
        errors.append(f"{path}:{line}: book_id must be a non-empty string")
    if has_book_ids:
        book_ids = row.get("book_ids")
        if not isinstance(book_ids, list) or not book_ids or not all(nonempty_string(item) for item in book_ids):
            errors.append(f"{path}:{line}: book_ids must be a non-empty list of strings")


def validate_nested_refs(
    value: Any,
    prefix: str,
    errors: list[str],
    *,
    evidence_required: bool = True,
) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix} must be an object")
        return
    if "evidence_refs" not in value:
        errors.append(f"{prefix}.evidence_refs is required")
    elif not ref_list(value["evidence_refs"], allow_empty=not evidence_required):
        errors.append(f"{prefix}.evidence_refs must be a structured-ref list")
    if "unknowns" not in value:
        errors.append(f"{prefix}.unknowns is required")
    elif not string_list(value["unknowns"]):
        errors.append(f"{prefix}.unknowns must be a list of strings")


def validate_window(value: Any, prefix: str, errors: list[str], seen: set[int]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix} must be an object")
        return
    required = {
        "window_id",
        "checkpoint",
        "chapters_covered",
        "completed_opening_functions",
        "incomplete_or_unknown_functions",
        "changes_since_prior_window",
        "evidence_refs",
        "unknowns",
    }
    missing = sorted(required - set(value))
    if missing:
        errors.append(f"{prefix} missing {', '.join(missing)}")
    if not nonempty_string(value.get("window_id")):
        errors.append(f"{prefix}.window_id must be non-empty")
    checkpoint = value.get("checkpoint")
    if checkpoint not in CHECKPOINTS:
        errors.append(f"{prefix}.checkpoint must be one of 3, 5, 10, 20")
    elif checkpoint in seen:
        errors.append(f"{prefix}.checkpoint is duplicated")
    else:
        seen.add(checkpoint)
    if not nonempty_string(value.get("chapters_covered")):
        errors.append(f"{prefix}.chapters_covered must be non-empty")
    for field in ("completed_opening_functions", "incomplete_or_unknown_functions"):
        items = value.get(field)
        if not string_list(items):
            errors.append(f"{prefix}.{field} must be a list of strings")
        elif any(item not in OPENING_FUNCTIONS for item in items):
            errors.append(f"{prefix}.{field} contains an unsupported opening function")
    completed = set(value.get("completed_opening_functions", []))
    pending = set(value.get("incomplete_or_unknown_functions", []))
    if completed & pending:
        errors.append(f"{prefix}: completed and incomplete opening functions overlap")
    if not nonempty_string(value.get("changes_since_prior_window")):
        errors.append(f"{prefix}.changes_since_prior_window must be non-empty")
    validate_nested_refs(value, prefix, errors)


def validate_entry(value: Any, prefix: str, errors: list[str]) -> set[str]:
    ids: set[str] = set()
    if not isinstance(value, list):
        errors.append(f"{prefix} must be a list")
        return ids
    required = {
        "entry_id",
        "reader_entry_mechanism",
        "entry_event_or_scene",
        "created_problem_anomaly_desire_risk_or_promise",
        "continued_expectation",
        "applicable_window",
        "evidence_refs",
        "unknowns",
    }
    for index, item in enumerate(value):
        item_prefix = f"{prefix}[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_prefix} must be an object")
            continue
        missing = sorted(required - set(item))
        if missing:
            errors.append(f"{item_prefix} missing {', '.join(missing)}")
        for field in (
            "entry_id",
            "entry_event_or_scene",
            "created_problem_anomaly_desire_risk_or_promise",
            "continued_expectation",
        ):
            if not nonempty_string(item.get(field)):
                errors.append(f"{item_prefix}.{field} must be non-empty")
        if item.get("reader_entry_mechanism") not in ENTRY_MECHANISMS:
            errors.append(f"{item_prefix}.reader_entry_mechanism is not controlled")
        validate_window_value(item.get("applicable_window"), f"{item_prefix}.applicable_window", errors)
        validate_nested_refs(item, item_prefix, errors)
        register_id(item.get("entry_id"), ids, item_prefix, errors)
    return ids


def validate_protagonist(value: Any, prefix: str, errors: list[str]) -> set[str]:
    ids: set[str] = set()
    if not isinstance(value, list):
        errors.append(f"{prefix} must be a list")
        return ids
    required = {
        "establishment_id",
        "observable_behaviors",
        "key_choices",
        "initial_situation_or_constraints",
        "ability_or_resource_bounds",
        "established_trait_or_function_impression",
        "observable_consequence",
        "applicable_window",
        "evidence_refs",
        "unknowns",
    }
    for index, item in enumerate(value):
        item_prefix = f"{prefix}[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_prefix} must be an object")
            continue
        missing = sorted(required - set(item))
        if missing:
            errors.append(f"{item_prefix} missing {', '.join(missing)}")
        for field in ("observable_behaviors", "key_choices"):
            if not string_list(item.get(field)):
                errors.append(f"{item_prefix}.{field} must be a list of strings")
        for field in (
            "establishment_id",
            "initial_situation_or_constraints",
            "ability_or_resource_bounds",
            "established_trait_or_function_impression",
            "observable_consequence",
        ):
            if not nonempty_string(item.get(field)):
                errors.append(f"{item_prefix}.{field} must be non-empty")
        validate_window_value(item.get("applicable_window"), f"{item_prefix}.applicable_window", errors)
        validate_nested_refs(item, item_prefix, errors)
        register_id(item.get("establishment_id"), ids, item_prefix, errors)
    return ids


def validate_premise(value: Any, prefix: str, errors: list[str]) -> set[str]:
    ids: set[str] = set()
    if not isinstance(value, list):
        errors.append(f"{prefix} must be a list")
        return ids
    required = {
        "premise_id",
        "core_premise",
        "reader_can_understand",
        "exposure_basis",
        "exposure_stage_or_window",
        "reader_understanding_status",
        "evidence_refs",
        "unknowns",
    }
    for index, item in enumerate(value):
        item_prefix = f"{prefix}[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_prefix} must be an object")
            continue
        missing = sorted(required - set(item))
        if missing:
            errors.append(f"{item_prefix} missing {', '.join(missing)}")
        for field in ("premise_id", "core_premise", "reader_can_understand", "exposure_stage_or_window"):
            if not nonempty_string(item.get(field)):
                errors.append(f"{item_prefix}.{field} must be non-empty")
        if item.get("exposure_basis") not in EXPOSURE_BASES:
            errors.append(f"{item_prefix}.exposure_basis is not controlled")
        if item.get("reader_understanding_status") not in EXPOSURE_STATUS:
            errors.append(f"{item_prefix}.reader_understanding_status is not controlled")
        validate_nested_refs(item, item_prefix, errors)
        register_id(item.get("premise_id"), ids, item_prefix, errors)
    return ids


def validate_milestone(value: Any, prefix: str, errors: list[str], *, proof: bool) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix} must be an object")
        return
    required = {"milestone_status", "chapter_or_window", "event_or_scene", "what_is_known", "evidence_refs", "unknowns"}
    if proof:
        required.add("observable_result")
    missing = sorted(required - set(value))
    if missing:
        errors.append(f"{prefix} missing {', '.join(missing)}")
    status = value.get("milestone_status")
    if status not in MILESTONE_STATUS:
        errors.append(f"{prefix}.milestone_status is not controlled")
    for field in ("chapter_or_window", "event_or_scene", "what_is_known"):
        if not nonempty_string(value.get(field)):
            errors.append(f"{prefix}.{field} must be non-empty or UNKNOWN")
    if proof and not nonempty_string(value.get("observable_result")):
        errors.append(f"{prefix}.observable_result must be non-empty or UNKNOWN")
    evidence_required = status in {"observed", "partial"}
    validate_nested_refs(value, prefix, errors, evidence_required=evidence_required)


def validate_golden_finger(value: Any, prefix: str, errors: list[str]) -> set[str]:
    ids: set[str] = set()
    entries = value if isinstance(value, list) else [value]
    if not isinstance(value, (list, dict)):
        errors.append(f"{prefix} must be a list or object")
        return ids
    required = {"reveal_id", "subject_type", "subject_label", "milestones", "evidence_refs", "unknowns"}
    milestone_keys = {"appearance", "understanding", "validation", "first_proof_or_payoff"}
    for index, item in enumerate(entries):
        item_prefix = f"{prefix}[{index}]" if isinstance(value, list) else prefix
        if not isinstance(item, dict):
            errors.append(f"{item_prefix} must be an object")
            continue
        missing = sorted(required - set(item))
        if missing:
            errors.append(f"{item_prefix} missing {', '.join(missing)}")
        if item.get("subject_type") not in SUBJECT_TYPES:
            errors.append(f"{item_prefix}.subject_type is not controlled")
        if not nonempty_string(item.get("reveal_id")):
            errors.append(f"{item_prefix}.reveal_id must be non-empty")
        if not nonempty_string(item.get("subject_label")):
            errors.append(f"{item_prefix}.subject_label must be non-empty or UNKNOWN")
        milestones = item.get("milestones")
        if not isinstance(milestones, dict):
            errors.append(f"{item_prefix}.milestones must be an object")
        else:
            missing_milestones = sorted(milestone_keys - set(milestones))
            extra_milestones = sorted(set(milestones) - milestone_keys)
            if missing_milestones:
                errors.append(f"{item_prefix}.milestones missing {', '.join(missing_milestones)}")
            if extra_milestones:
                errors.append(f"{item_prefix}.milestones has unsupported keys {', '.join(extra_milestones)}")
            for key in milestone_keys & set(milestones):
                validate_milestone(
                    milestones[key],
                    f"{item_prefix}.milestones.{key}",
                    errors,
                    proof=key == "first_proof_or_payoff",
                )
        validate_nested_refs(item, item_prefix, errors, evidence_required=False)
        register_id(item.get("reveal_id"), ids, item_prefix, errors)
    return ids


def validate_conflict(value: Any, prefix: str, errors: list[str]) -> set[str]:
    return validate_simple_list(
        value,
        prefix,
        errors,
        required={
            "conflict_id",
            "conflict_identity_or_reference",
            "actual_activation_event",
            "involved_goal_or_stakes",
            "sustaining_reason",
            "first_sustained_window",
            "evidence_refs",
            "unknowns",
        },
        text_fields={
            "conflict_id",
            "conflict_identity_or_reference",
            "actual_activation_event",
            "involved_goal_or_stakes",
            "sustaining_reason",
        },
        window_fields={"first_sustained_window"},
    )


def validate_promises(value: Any, prefix: str, errors: list[str]) -> set[str]:
    ids: set[str] = set()
    if not isinstance(value, list):
        errors.append(f"{prefix} must be a list")
        return ids
    required = {
        "promise_id",
        "promise_statement",
        "promise_target",
        "setup_event",
        "expected_future_payoff_or_unresolved_question",
        "promise_status",
        "setup_window",
        "evidence_refs",
        "unknowns",
    }
    for index, item in enumerate(value):
        item_prefix = f"{prefix}[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_prefix} must be an object")
            continue
        missing = sorted(required - set(item))
        if missing:
            errors.append(f"{item_prefix} missing {', '.join(missing)}")
        for field in (
            "promise_id",
            "promise_statement",
            "promise_target",
            "setup_event",
            "expected_future_payoff_or_unresolved_question",
        ):
            if not nonempty_string(item.get(field)):
                errors.append(f"{item_prefix}.{field} must be non-empty")
        if item.get("promise_status") not in PROMISE_STATES:
            errors.append(f"{item_prefix}.promise_status is not controlled")
        validate_window_value(item.get("setup_window"), f"{item_prefix}.setup_window", errors)
        validate_nested_refs(item, item_prefix, errors)
        register_id(item.get("promise_id"), ids, item_prefix, errors)
    return ids


def validate_proofs(value: Any, prefix: str, errors: list[str]) -> set[str]:
    return validate_simple_list(
        value,
        prefix,
        errors,
        required={
            "proof_id",
            "selling_point",
            "proof_event",
            "observable_result",
            "what_it_proves",
            "proof_window",
            "evidence_refs",
            "unknowns",
        },
        text_fields={"proof_id", "selling_point", "proof_event", "observable_result", "what_it_proves"},
        window_fields={"proof_window"},
    )


def validate_stakes(value: Any, prefix: str, errors: list[str]) -> set[str]:
    ids: set[str] = set()
    if not isinstance(value, list):
        errors.append(f"{prefix} must be a list")
        return ids
    required = {
        "escalation_id",
        "before_stakes",
        "escalation_event",
        "after_stakes",
        "affected_dimension",
        "escalation_window",
        "evidence_refs",
        "unknowns",
    }
    for index, item in enumerate(value):
        item_prefix = f"{prefix}[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_prefix} must be an object")
            continue
        missing = sorted(required - set(item))
        if missing:
            errors.append(f"{item_prefix} missing {', '.join(missing)}")
        for field in ("escalation_id", "before_stakes", "escalation_event", "after_stakes"):
            if not nonempty_string(item.get(field)):
                errors.append(f"{item_prefix}.{field} must be non-empty")
        if item.get("affected_dimension") not in STAKE_DIMENSIONS:
            errors.append(f"{item_prefix}.affected_dimension is not controlled")
        validate_window_value(item.get("escalation_window"), f"{item_prefix}.escalation_window", errors)
        validate_nested_refs(item, item_prefix, errors)
        register_id(item.get("escalation_id"), ids, item_prefix, errors)
    return ids


def validate_payoffs(value: Any, prefix: str, errors: list[str], local_refs: set[str]) -> set[str]:
    ids: set[str] = set()
    if not isinstance(value, list):
        errors.append(f"{prefix} must be a list")
        return ids
    required = {
        "payoff_id",
        "prior_object_type",
        "prior_object_ref",
        "payoff_event_or_result",
        "payoff_degree",
        "payoff_window",
        "aftereffect",
        "evidence_refs",
        "unknowns",
    }
    for index, item in enumerate(value):
        item_prefix = f"{prefix}[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_prefix} must be an object")
            continue
        missing = sorted(required - set(item))
        if missing:
            errors.append(f"{item_prefix} missing {', '.join(missing)}")
        for field in ("payoff_id", "prior_object_ref", "payoff_event_or_result", "aftereffect"):
            if not nonempty_string(item.get(field)):
                errors.append(f"{item_prefix}.{field} must be non-empty")
        if item.get("prior_object_type") not in PRIOR_OBJECT_TYPES:
            errors.append(f"{item_prefix}.prior_object_type is not controlled")
        if item.get("payoff_degree") not in PAYOFF_DEGREES:
            errors.append(f"{item_prefix}.payoff_degree is not controlled")
        validate_window_value(item.get("payoff_window"), f"{item_prefix}.payoff_window", errors)
        prior_ref = item.get("prior_object_ref")
        if item.get("prior_object_type") == "UNKNOWN" or prior_ref == "UNKNOWN":
            errors.append(f"{item_prefix}: first payoff requires a concrete prior_object_ref")
        elif nonempty_string(prior_ref):
            if not isinstance(prior_ref, str) or len(prior_ref.split(":")) < 3:
                errors.append(f"{item_prefix}.prior_object_ref must be a structured local reference")
            elif item.get("prior_object_type") == "promise" and prior_ref not in local_refs:
                errors.append(f"{item_prefix}.prior_object_ref must reference a local promise or opening object")
            elif item.get("prior_object_type") in {"opening_goal", "selling_point"} and prior_ref not in local_refs:
                errors.append(f"{item_prefix}.prior_object_ref must reference a local opening object")
        validate_nested_refs(item, item_prefix, errors)
        register_id(item.get("payoff_id"), ids, item_prefix, errors)
    return ids


def validate_drivers(value: Any, prefix: str, errors: list[str]) -> set[str]:
    return validate_simple_list(
        value,
        prefix,
        errors,
        required={
            "driver_id",
            "driver_source",
            "unresolved_question_next_goal_risk_or_promise",
            "why_continuation_is_required",
            "applicable_window",
            "evidence_refs",
            "unknowns",
        },
        text_fields={"driver_id", "unresolved_question_next_goal_risk_or_promise", "why_continuation_is_required"},
        window_fields={"applicable_window"},
        controlled_fields={"driver_source": CONFLICT_SOURCES},
    )


def validate_information(value: Any, prefix: str, errors: list[str]) -> set[str]:
    return validate_simple_list(
        value,
        prefix,
        errors,
        required={
            "information_id",
            "information_item",
            "disclosure_state",
            "disclosure_window",
            "why_now",
            "why_delayed",
            "reader_knowledge_effect",
            "evidence_refs",
            "unknowns",
        },
        text_fields={"information_id", "information_item", "why_now", "why_delayed", "reader_knowledge_effect"},
        window_fields={"disclosure_window"},
        controlled_fields={"disclosure_state": DISCLOSURE_STATES},
    )


def validate_compression(value: Any, prefix: str, errors: list[str]) -> set[str]:
    ids: set[str] = set()
    if not isinstance(value, list):
        errors.append(f"{prefix} must be a list")
        return ids
    required = {
        "compression_id",
        "issue_type",
        "observed_pattern",
        "affected_windows",
        "reader_or_story_effect",
        "observation_status",
        "evidence_refs",
        "unknowns",
    }
    forbidden = {"score", "grade", "tier", "rating"}
    for index, item in enumerate(value):
        item_prefix = f"{prefix}[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_prefix} must be an object")
            continue
        missing = sorted(required - set(item))
        if missing:
            errors.append(f"{item_prefix} missing {', '.join(missing)}")
        extra = sorted(forbidden & set(item))
        if extra:
            errors.append(f"{item_prefix} contains unsupported evaluation fields: {', '.join(extra)}")
        for field in ("compression_id", "observed_pattern", "reader_or_story_effect"):
            if not nonempty_string(item.get(field)):
                errors.append(f"{item_prefix}.{field} must be non-empty")
        if item.get("issue_type") not in COMPRESSION_TYPES:
            errors.append(f"{item_prefix}.issue_type is not controlled")
        if item.get("observation_status") not in COMPRESSION_STATUSES:
            errors.append(f"{item_prefix}.observation_status is not controlled")
        windows = item.get("affected_windows")
        if not isinstance(windows, list) or not windows or any(window not in CHECKPOINTS for window in windows):
            errors.append(f"{item_prefix}.affected_windows must be a non-empty list of 3/5/10/20")
        validate_nested_refs(item, item_prefix, errors)
        register_id(item.get("compression_id"), ids, item_prefix, errors)
    return ids


def validate_simple_list(
    value: Any,
    prefix: str,
    errors: list[str],
    *,
    required: set[str],
    text_fields: set[str],
    window_fields: set[str] | None = None,
    controlled_fields: dict[str, set[str]] | None = None,
) -> set[str]:
    ids: set[str] = set()
    if not isinstance(value, list):
        errors.append(f"{prefix} must be a list")
        return ids
    window_fields = window_fields or set()
    controlled_fields = controlled_fields or {}
    id_field = next((field for field in ("conflict_id", "proof_id", "driver_id", "information_id") if field in required), None)
    for index, item in enumerate(value):
        item_prefix = f"{prefix}[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_prefix} must be an object")
            continue
        missing = sorted(required - set(item))
        if missing:
            errors.append(f"{item_prefix} missing {', '.join(missing)}")
        for field in text_fields:
            if not nonempty_string(item.get(field)):
                errors.append(f"{item_prefix}.{field} must be non-empty")
        for field, allowed in controlled_fields.items():
            if item.get(field) not in allowed:
                errors.append(f"{item_prefix}.{field} is not controlled")
        for field in window_fields:
            validate_window_value(item.get(field), f"{item_prefix}.{field}", errors)
        validate_nested_refs(item, item_prefix, errors)
        if id_field:
            register_id(item.get(id_field), ids, item_prefix, errors)
    return ids


def validate_window_value(value: Any, prefix: str, errors: list[str]) -> None:
    if value not in CHECKPOINTS and value != "UNKNOWN":
        errors.append(f"{prefix} must be one of 3, 5, 10, 20, UNKNOWN")


def register_id(value: Any, ids: set[str], prefix: str, errors: list[str]) -> None:
    if not nonempty_string(value):
        return
    if value in ids:
        errors.append(f"{prefix}: duplicate local id={value}")
    else:
        ids.add(value)


def validate_adjacent_interfaces(value: Any, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix} must be an object")
        return
    missing = sorted(ADJACENT_KEYS - set(value))
    extra = sorted(set(value) - ADJACENT_KEYS)
    if missing:
        errors.append(f"{prefix} missing {', '.join(missing)}")
    if extra:
        errors.append(f"{prefix} has unsupported keys {', '.join(extra)}")
    for key in ADJACENT_KEYS & set(value):
        entries = value[key]
        if not isinstance(entries, list):
            errors.append(f"{prefix}.{key} must be a list")
            continue
        for index, entry in enumerate(entries):
            item_prefix = f"{prefix}.{key}[{index}]"
            if isinstance(entry, str):
                if not nonempty_string(entry):
                    errors.append(f"{item_prefix} must be a non-empty reference string")
                continue
            if not isinstance(entry, dict):
                errors.append(f"{item_prefix} must be a reference string or object")
                continue
            unsupported = sorted(set(entry) - INTERFACE_REFERENCE_KEYS)
            if unsupported:
                errors.append(f"{item_prefix} contains non-reference fields: {', '.join(unsupported)}")
            if "record_id" not in entry or not nonempty_string(entry.get("record_id")):
                errors.append(f"{item_prefix}.record_id must be non-empty")
            if "interface_type" not in entry or not nonempty_string(entry.get("interface_type")):
                errors.append(f"{item_prefix}.interface_type must be non-empty")
            if not ref_list(entry.get("evidence_refs")):
                errors.append(f"{item_prefix}.evidence_refs must be non-empty structured refs")
            if "note" in entry and not nonempty_string(entry.get("note")):
                errors.append(f"{item_prefix}.note must be non-empty")
            if "unknowns" in entry and not string_list(entry["unknowns"]):
                errors.append(f"{item_prefix}.unknowns must be a list of strings")


def validate_per_book(row: dict[str, Any], path: Path, line: int, errors: list[str]) -> None:
    required = {
        "book_id",
        "title",
        "chapters_covered",
        "observation_windows",
        "entry",
        "protagonist_establishment",
        "premise_exposure",
        "golden_finger_reveal",
        "conflict_activation",
        "promise_setup",
        "selling_point_proof",
        "stakes_escalation",
        "first_payoff",
        "continuation_drivers",
        "information_pacing",
        "opening_compression",
        "adjacent_interfaces",
        "emotion_overlay_links",
        "source_numbering_notes",
    }
    add_missing(errors, path, line, row, required)
    for field in ("title", "chapters_covered"):
        if field in row and not nonempty_string(row[field]):
            errors.append(f"{path}:{line}: {field} must be non-empty")

    windows = row.get("observation_windows")
    if not isinstance(windows, list):
        errors.append(f"{path}:{line}: observation_windows must be a list")
    else:
        seen: set[int] = set()
        for index, window in enumerate(windows):
            validate_window(window, f"{path}:{line}: observation_windows[{index}]", errors, seen)

    local_refs: set[str] = set()
    local_refs.update(validate_entry(row.get("entry"), f"{path}:{line}: entry", errors))
    local_refs.update(validate_protagonist(row.get("protagonist_establishment"), f"{path}:{line}: protagonist_establishment", errors))
    local_refs.update(validate_premise(row.get("premise_exposure"), f"{path}:{line}: premise_exposure", errors))
    local_refs.update(validate_golden_finger(row.get("golden_finger_reveal"), f"{path}:{line}: golden_finger_reveal", errors))
    local_refs.update(validate_conflict(row.get("conflict_activation"), f"{path}:{line}: conflict_activation", errors))
    promise_ids = validate_promises(row.get("promise_setup"), f"{path}:{line}: promise_setup", errors)
    local_refs.update(promise_ids)
    proof_ids = validate_proofs(row.get("selling_point_proof"), f"{path}:{line}: selling_point_proof", errors)
    local_refs.update(proof_ids)
    local_refs.update(validate_stakes(row.get("stakes_escalation"), f"{path}:{line}: stakes_escalation", errors))
    local_refs.update(validate_drivers(row.get("continuation_drivers"), f"{path}:{line}: continuation_drivers", errors))
    local_refs.update(validate_information(row.get("information_pacing"), f"{path}:{line}: information_pacing", errors))
    local_refs.update(validate_compression(row.get("opening_compression"), f"{path}:{line}: opening_compression", errors))
    validate_payoffs(row.get("first_payoff"), f"{path}:{line}: first_payoff", errors, local_refs)
    validate_adjacent_interfaces(row.get("adjacent_interfaces"), f"{path}:{line}: adjacent_interfaces", errors)
    for field in ("emotion_overlay_links", "source_numbering_notes"):
        if not isinstance(row.get(field), list):
            errors.append(f"{path}:{line}: {field} must be a list")


def validate_gap(row: dict[str, Any], path: Path, line: int, errors: list[str]) -> None:
    add_missing(errors, path, line, row, {"reason", "known_evidence", "blocked_outputs"})
    if row.get("confidence") != "LOW":
        errors.append(f"{path}:{line}: gap records must be LOW confidence")
    if not nonempty_string(row.get("reason")):
        errors.append(f"{path}:{line}: gap reason must be non-empty")
    for field in ("known_evidence", "blocked_outputs"):
        if not string_list(row.get(field), allow_empty=False):
            errors.append(f"{path}:{line}: {field} must be a non-empty list of strings")


def validate_nearest_neighbor(row: dict[str, Any], path: Path, line: int, errors: list[str]) -> None:
    required = {
        "comparison_ids",
        "comparison_dimensions",
        "similarities",
        "difference_boundary",
        "surface_labels_excluded",
        "decision",
        "reason",
    }
    add_missing(errors, path, line, row, required)
    book_ids = row.get("book_ids")
    if isinstance(book_ids, list) and len(set(book_ids)) < 2:
        errors.append(f"{path}:{line}: nearest_neighbor requires at least two distinct book_ids")
    if not string_list(row.get("comparison_ids"), allow_empty=False):
        errors.append(f"{path}:{line}: comparison_ids must be a non-empty list of strings")
    dimensions = row.get("comparison_dimensions")
    required_dimensions = {
        "reader_entry",
        "protagonist_establishment",
        "premise_exposure",
        "golden_finger_reveal",
        "conflict_promise_payoff",
        "selling_point_and_stakes",
        "continuation_and_information",
    }
    if not isinstance(dimensions, dict):
        errors.append(f"{path}:{line}: comparison_dimensions must be an object")
    else:
        add_missing(errors, path, line, dimensions, required_dimensions)
    if not isinstance(row.get("similarities"), list):
        errors.append(f"{path}:{line}: similarities must be a list")
    if not string_list(row.get("surface_labels_excluded"), allow_empty=False):
        errors.append(f"{path}:{line}: surface_labels_excluded must be a non-empty list")
    for field in ("difference_boundary", "decision", "reason"):
        if not nonempty_string(row.get(field)):
            errors.append(f"{path}:{line}: {field} must be non-empty")
    if row.get("decision") not in NEIGHBOR_DECISIONS:
        errors.append(f"{path}:{line}: unsupported nearest_neighbor decision")


def validate_cluster(row: dict[str, Any], path: Path, line: int, errors: list[str]) -> None:
    required = {
        "member_record_ids",
        "cluster_level",
        "label",
        "shared_operation",
        "window_progression_pattern",
        "selling_point_promise_payoff_pattern",
        "information_and_compression_boundary",
        "boundary_conditions",
        "supporting_book_count",
        "nearest_neighbor_record_ids",
        "merge_decision",
    }
    add_missing(errors, path, line, row, required)
    book_ids = row.get("book_ids")
    if isinstance(book_ids, list):
        if len(set(book_ids)) < 2:
            errors.append(f"{path}:{line}: cluster requires at least two distinct book_ids")
        if row.get("supporting_book_count") != len(set(book_ids)):
            errors.append(f"{path}:{line}: supporting_book_count must match unique book_ids")
    elif "supporting_book_count" in row and not isinstance(row["supporting_book_count"], int):
        errors.append(f"{path}:{line}: supporting_book_count must be an integer")
    for field in ("member_record_ids", "boundary_conditions", "nearest_neighbor_record_ids"):
        if not string_list(row.get(field), allow_empty=False):
            errors.append(f"{path}:{line}: {field} must be a non-empty list of strings")
    for field in (
        "cluster_level",
        "label",
        "shared_operation",
        "window_progression_pattern",
        "selling_point_promise_payoff_pattern",
        "information_and_compression_boundary",
    ):
        if not nonempty_string(row.get(field)):
            errors.append(f"{path}:{line}: {field} must be non-empty")
    if row.get("merge_decision") not in CLUSTER_DECISIONS:
        errors.append(f"{path}:{line}: unsupported cluster merge_decision")


def validate_qa(row: dict[str, Any], path: Path, line: int, errors: list[str]) -> None:
    add_missing(errors, path, line, row, {"scope", "checks", "gaps", "disputes", "blocked_outputs"})
    if not nonempty_string(row.get("scope")):
        errors.append(f"{path}:{line}: scope must be non-empty")
    checks = row.get("checks")
    required_checks = {
        "window_coverage",
        "entry_and_protagonist",
        "premise_exposure",
        "golden_finger_milestones",
        "conflict_activation",
        "promise_and_first_payoff",
        "selling_point_proof",
        "stakes_escalation",
        "continuation_driver",
        "information_pacing_compression",
        "adjacent_boundary",
        "cross_book_gate",
    }
    if not isinstance(checks, dict):
        errors.append(f"{path}:{line}: checks must be an object")
    else:
        add_missing(errors, path, line, checks, required_checks)
        for field in required_checks:
            if field in checks and checks[field] not in QA_STATUS:
                errors.append(f"{path}:{line}: checks.{field} must be PASS/HOLD/FAIL")
    for field in ("gaps", "disputes", "blocked_outputs"):
        if field in row and not isinstance(row[field], list):
            errors.append(f"{path}:{line}: {field} must be a list")


def validate_handoff(row: dict[str, Any], path: Path, line: int, errors: list[str]) -> None:
    required = {"candidate_record_ids", "recommended_action", "decision_points", "evidence_summary", "boundary_warnings", "blocked_by"}
    add_missing(errors, path, line, row, required)
    if not string_list(row.get("candidate_record_ids"), allow_empty=False):
        errors.append(f"{path}:{line}: candidate_record_ids must be a non-empty list of strings")
    for field in ("decision_points", "evidence_summary", "boundary_warnings", "blocked_by"):
        if field in row and not isinstance(row[field], list):
            errors.append(f"{path}:{line}: {field} must be a list")
    if row.get("recommended_action") not in HANDOFF_ACTIONS:
        errors.append(f"{path}:{line}: unsupported recommended_action")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Validate novel-opening-miner JSONL outputs.")
    parser.add_argument("target", type=Path, help="A JSONL file or directory containing JSONL files.")
    parser.add_argument("--kind", required=True, choices=sorted(KINDS))
    parser.add_argument("--expected-books", help="Optional comma-separated books for per_book/gap coverage checks.")
    parser.add_argument(
        "--all-books-complete",
        action="store_true",
        help="Acknowledge the explicit completion manifest gate for cross-book records.",
    )
    parser.add_argument(
        "--completion-manifest",
        type=Path,
        help="JSONL containing exactly one candidate per_book or gap record for every expected book.",
    )
    args = parser.parse_args()

    if args.kind in {"nearest_neighbor", "cluster"} and not args.all_books_complete:
        print(
            json.dumps(
                {"records": 0, "errors": ["completion gate required: pass --all-books-complete"], "ok": False},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    expected_books = None
    if args.expected_books is not None:
        expected_books = {item.strip() for item in args.expected_books.split(",") if item.strip()}
        if not expected_books:
            parser.error("--expected-books cannot be empty")
    if args.kind in {"nearest_neighbor", "cluster"}:
        if expected_books is None:
            parser.error("--expected-books is required for cross-book validation")
        if args.completion_manifest is None:
            parser.error("--completion-manifest is required for cross-book validation")

    errors: list[str] = []
    records = 0
    record_ids: set[str] = set()
    covered_books: list[str] = []
    found_file = False
    if args.kind in {"nearest_neighbor", "cluster"}:
        errors.extend(load_completion_manifest(args.completion_manifest, expected_books))

    for path, line, raw in iter_jsonl(args.target):
        found_file = True
        if not raw.strip():
            errors.append(f"{path}:{line}: empty JSONL line")
            continue
        records += 1
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}:{line}: invalid JSON: {exc}")
            continue
        if not isinstance(row, dict):
            errors.append(f"{path}:{line}: each JSONL record must be an object")
            continue

        validate_envelope(row, args.kind, path, line, errors, record_ids)
        if "book_id" in row and nonempty_string(row.get("book_id")):
            covered_books.append(row["book_id"])

        if args.kind == "per_book":
            validate_per_book(row, path, line, errors)
        elif args.kind == "gap":
            validate_gap(row, path, line, errors)
        elif args.kind == "nearest_neighbor":
            validate_nearest_neighbor(row, path, line, errors)
        elif args.kind == "cluster":
            validate_cluster(row, path, line, errors)
        elif args.kind == "qa":
            validate_qa(row, path, line, errors)
        elif args.kind == "handoff":
            validate_handoff(row, path, line, errors)

    if not found_file:
        errors.append(f"target not found: {args.target}")
    if args.kind in {"per_book", "gap"} and expected_books is not None:
        actual_books = set(covered_books)
        missing = sorted(expected_books - actual_books)
        unexpected = sorted(actual_books - expected_books)
        if missing:
            errors.append(f"missing target books: {', '.join(missing)}")
        if unexpected:
            errors.append(f"unexpected books: {', '.join(unexpected)}")
        duplicates = sorted({book for book in covered_books if covered_books.count(book) > 1})
        if duplicates:
            errors.append(f"duplicate per_book/gap coverage: {', '.join(duplicates)}")

    result = {
        "kind": args.kind,
        "records": records,
        "covered_books": sorted(set(covered_books)),
        "errors": errors,
        "ok": not errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
