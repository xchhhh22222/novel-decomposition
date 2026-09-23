#!/usr/bin/env python3
"""Validate derived JSONL records from novel-character-function-miner.

This validator enforces deterministic structure and explicit contract gates.
Literary judgments such as whether a strong character is truly a mentor remain
in clustering-and-qa.md and are intentionally not inferred here.
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
FUNCTION_STATES = {"observed", "emerging", "weakened", "ended", "UNKNOWN"}
ENGINE_STATES = {"recurring", "dormant", "ended", "UNKNOWN"}
REPLACEABILITY = {"replaceable", "identity_bound", "non_replaceable", "UNKNOWN"}
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
ADJACENT_KEYS = {
    "plotline",
    "arc_structure",
    "plot_mechanism",
    "worldbuilding",
    "cultivation",
    "golden_finger",
    "chapter_emotion",
}
INTERFACE_KEYS = {
    "interface_id",
    "person_id",
    "target",
    "choices",
    "resources",
    "risks",
    "cognition_information",
    "goals",
    "relationship_emotional_feedback",
    "evidence_refs",
    "unknowns",
}
INTERFACE_DIMENSIONS = {
    "choices",
    "resources",
    "risks",
    "cognition_information",
    "goals",
    "relationship_emotional_feedback",
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


def validate_nested_refs(obj: Any, prefix: str, errors: list[str], *, required: bool = True) -> None:
    if not isinstance(obj, dict):
        errors.append(f"{prefix} must be an object")
        return
    if "evidence_refs" in obj:
        if not ref_list(obj["evidence_refs"], allow_empty=not required):
            errors.append(f"{prefix}.evidence_refs must be a structured-ref list")
    if "unknowns" in obj and not string_list(obj["unknowns"]):
        errors.append(f"{prefix}.unknowns must be a list of strings")


def validate_identity_facts(value: Any, path: Path, line: int, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append(f"{path}:{line}: identity_facts must be a list")
        return
    required = {"fact_id", "person_id", "fact", "fact_scope", "evidence_refs", "unknowns"}
    for index, item in enumerate(value):
        prefix = f"{path}:{line}: identity_facts[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        add_missing(errors, path, line, item, required)
        for field in ("fact_id", "person_id", "fact", "fact_scope"):
            if field in item and not nonempty_string(item[field]):
                errors.append(f"{prefix}.{field} must be non-empty")
        validate_nested_refs(item, prefix, errors)


def validate_narrative_functions(value: Any, path: Path, line: int, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append(f"{path}:{line}: narrative_functions must be a list")
        return
    required = {
        "function_id",
        "person_id",
        "function_type",
        "actual_operation",
        "target",
        "phase_scope",
        "function_state",
        "evidence_refs",
        "unknowns",
    }
    for index, item in enumerate(value):
        prefix = f"{path}:{line}: narrative_functions[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        add_missing(errors, path, line, item, required)
        for field in ("function_id", "person_id", "function_type", "actual_operation", "target", "phase_scope"):
            if field in item and not nonempty_string(item[field]):
                errors.append(f"{prefix}.{field} must be non-empty")
        if item.get("function_state") not in FUNCTION_STATES:
            errors.append(f"{prefix}.function_state must be observed/emerging/weakened/ended/UNKNOWN")
        if "evidence_refs" in item and not ref_list(item["evidence_refs"]):
            errors.append(f"{prefix}.evidence_refs must be non-empty structured refs")
        if "unknowns" in item and not string_list(item["unknowns"]):
            errors.append(f"{prefix}.unknowns must be a list of strings")


def validate_relationship_functions(value: Any, path: Path, line: int, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append(f"{path}:{line}: relationship_functions must be a list")
        return
    required = {
        "relationship_function_id",
        "relation_id",
        "person_id",
        "counterparty_id",
        "function_type",
        "relational_operation",
        "observable_change",
        "phase_scope",
        "evidence_refs",
        "unknowns",
    }
    for index, item in enumerate(value):
        prefix = f"{path}:{line}: relationship_functions[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        add_missing(errors, path, line, item, required)
        for field in (
            "relationship_function_id",
            "relation_id",
            "person_id",
            "counterparty_id",
            "function_type",
            "relational_operation",
            "observable_change",
            "phase_scope",
        ):
            if field in item and not nonempty_string(item[field]):
                errors.append(f"{prefix}.{field} must be non-empty")
        if "evidence_refs" in item and not ref_list(item["evidence_refs"]):
            errors.append(f"{prefix}.evidence_refs must be non-empty structured refs")
        if "unknowns" in item and not string_list(item["unknowns"]):
            errors.append(f"{prefix}.unknowns must be a list of strings")


def validate_function_combinations(value: Any, path: Path, line: int, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append(f"{path}:{line}: function_combinations must be a list")
        return
    required = {
        "combination_id",
        "person_id",
        "function_ids",
        "combined_operation",
        "trigger_or_condition",
        "observable_outputs",
        "evidence_refs",
        "unknowns",
    }
    for index, item in enumerate(value):
        prefix = f"{path}:{line}: function_combinations[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        add_missing(errors, path, line, item, required)
        if not nonempty_string(item.get("combination_id")) or not nonempty_string(item.get("person_id")):
            errors.append(f"{prefix}: combination_id and person_id must be non-empty")
        if not string_list(item.get("function_ids"), allow_empty=False) or len(item.get("function_ids", [])) < 2:
            errors.append(f"{prefix}.function_ids must contain at least two function ids")
        for field in ("combined_operation", "trigger_or_condition"):
            if not nonempty_string(item.get(field)):
                errors.append(f"{prefix}.{field} must be non-empty")
        if not string_list(item.get("observable_outputs"), allow_empty=False):
            errors.append(f"{prefix}.observable_outputs must be a non-empty list of strings")
        if not ref_list(item.get("evidence_refs")):
            errors.append(f"{prefix}.evidence_refs must be non-empty structured refs")
        if not string_list(item.get("unknowns")):
            errors.append(f"{prefix}.unknowns must be a list of strings")


def validate_function_transitions(value: Any, path: Path, line: int, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append(f"{path}:{line}: function_transitions must be a list")
        return
    required = {
        "transition_id",
        "person_id",
        "before_function",
        "trigger_event",
        "after_function",
        "stage_scope",
        "protagonist_interface_change",
        "evidence_refs",
        "unknowns",
    }
    for index, item in enumerate(value):
        prefix = f"{path}:{line}: function_transitions[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        add_missing(errors, path, line, item, required)
        for field in (
            "transition_id",
            "person_id",
            "before_function",
            "trigger_event",
            "after_function",
            "stage_scope",
            "protagonist_interface_change",
        ):
            if field in item and not nonempty_string(item[field]):
                errors.append(f"{prefix}.{field} must be non-empty")
        if not ref_list(item.get("evidence_refs")):
            errors.append(f"{prefix}.evidence_refs must be non-empty structured refs")
        if not string_list(item.get("unknowns")):
            errors.append(f"{prefix}.unknowns must be a list of strings")


def validate_replaceability(value: Any, path: Path, line: int, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append(f"{path}:{line}: replaceability must be a list")
        return
    required = {
        "replaceability_id",
        "person_id",
        "function_id",
        "replaceability",
        "substitution_condition",
        "binding_features",
        "reasoning",
        "evidence_refs",
        "unknowns",
    }
    for index, item in enumerate(value):
        prefix = f"{path}:{line}: replaceability[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        add_missing(errors, path, line, item, required)
        for field in ("replaceability_id", "person_id", "function_id"):
            if field in item and not nonempty_string(item[field]):
                errors.append(f"{prefix}.{field} must be non-empty")
        state = item.get("replaceability")
        if state not in REPLACEABILITY:
            errors.append(f"{prefix}.replaceability is not controlled")
        if not nonempty_string(item.get("substitution_condition")):
            errors.append(f"{prefix}.substitution_condition must be non-empty or UNKNOWN")
        if not string_list(item.get("binding_features")):
            errors.append(f"{prefix}.binding_features must be a list of strings")
        if not nonempty_string(item.get("reasoning")):
            errors.append(f"{prefix}.reasoning must be non-empty or UNKNOWN")
        if not ref_list(item.get("evidence_refs")):
            errors.append(f"{prefix}.evidence_refs must be non-empty structured refs")
        if not string_list(item.get("unknowns")):
            errors.append(f"{prefix}.unknowns must be a list of strings")
        if state == "replaceable" and item.get("substitution_condition") == "UNKNOWN":
            errors.append(f"{prefix}: replaceable requires substitution_condition")
        if state in {"identity_bound", "non_replaceable"} and not item.get("binding_features"):
            errors.append(f"{prefix}: {state} requires binding_features")
        if state != "UNKNOWN" and item.get("reasoning") == "UNKNOWN":
            errors.append(f"{prefix}: determined replaceability requires reasoning")


def validate_protagonist_interface(value: Any, path: Path, line: int, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append(f"{path}:{line}: protagonist_interface must be a list")
        return
    required = {
        "interface_id",
        "person_id",
        "target",
        "choices",
        "resources",
        "risks",
        "cognition_information",
        "goals",
        "relationship_emotional_feedback",
        "evidence_refs",
        "unknowns",
    }
    for index, item in enumerate(value):
        prefix = f"{path}:{line}: protagonist_interface[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        add_missing(errors, path, line, item, required)
        extra = sorted(set(item) - INTERFACE_KEYS)
        if extra:
            errors.append(f"{prefix} contains unsupported interface fields: {', '.join(extra)}")
        for field in {"interface_id", "person_id", "target"} | INTERFACE_DIMENSIONS:
            if field in item and not nonempty_string(item[field]):
                errors.append(f"{prefix}.{field} must be non-empty or UNKNOWN")
        if not any(nonempty_string(item.get(field)) and item.get(field) != "UNKNOWN" for field in INTERFACE_DIMENSIONS):
            errors.append(f"{prefix}: at least one protagonist interface dimension must be observed")
        if not ref_list(item.get("evidence_refs")):
            errors.append(f"{prefix}.evidence_refs must be non-empty structured refs")
        if not string_list(item.get("unknowns")):
            errors.append(f"{prefix}.unknowns must be a list of strings")


def validate_relationship_engines(value: Any, path: Path, line: int, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append(f"{path}:{line}: relationship_engines must be a list")
        return
    required = {
        "engine_id",
        "relation_id",
        "relation_sides",
        "engine_type",
        "sustaining_condition",
        "recurring_plot_generation",
        "observable_outputs",
        "engine_state",
        "evidence_refs",
        "unknowns",
    }
    for index, item in enumerate(value):
        prefix = f"{path}:{line}: relationship_engines[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        add_missing(errors, path, line, item, required)
        for field in ("engine_id", "relation_id", "engine_type", "sustaining_condition", "recurring_plot_generation"):
            if field in item and not nonempty_string(item[field]):
                errors.append(f"{prefix}.{field} must be non-empty")
        if not string_list(item.get("relation_sides"), allow_empty=False) or len(item.get("relation_sides", [])) < 2:
            errors.append(f"{prefix}.relation_sides must contain at least two parties")
        if not string_list(item.get("observable_outputs"), allow_empty=False):
            errors.append(f"{prefix}.observable_outputs must be a non-empty list of strings")
        if item.get("engine_state") not in ENGINE_STATES:
            errors.append(f"{prefix}.engine_state must be recurring/dormant/ended/UNKNOWN")
        if not ref_list(item.get("evidence_refs")):
            errors.append(f"{prefix}.evidence_refs must be non-empty structured refs")
        if not string_list(item.get("unknowns")):
            errors.append(f"{prefix}.unknowns must be a list of strings")


def validate_adjacent_interfaces(value: Any, path: Path, line: int, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{path}:{line}: adjacent_interfaces must be an object")
        return
    missing = sorted(ADJACENT_KEYS - set(value))
    extra = sorted(set(value) - ADJACENT_KEYS)
    if missing:
        errors.append(f"{path}:{line}: adjacent_interfaces missing {', '.join(missing)}")
    if extra:
        errors.append(f"{path}:{line}: adjacent_interfaces has unsupported keys {', '.join(extra)}")
    allowed_reference_keys = {"record_id", "evidence_refs", "note", "interface_type", "unknowns"}
    for key in ADJACENT_KEYS & set(value):
        entries = value[key]
        if not isinstance(entries, list):
            errors.append(f"{path}:{line}: adjacent_interfaces.{key} must be a list")
            continue
        for index, entry in enumerate(entries):
            prefix = f"{path}:{line}: adjacent_interfaces.{key}[{index}]"
            if isinstance(entry, str):
                if not nonempty_string(entry):
                    errors.append(f"{prefix} must be a non-empty reference string")
                continue
            if not isinstance(entry, dict):
                errors.append(f"{prefix} must be a reference string or object")
                continue
            unsupported = sorted(set(entry) - allowed_reference_keys)
            if unsupported:
                errors.append(f"{prefix} contains non-reference fields: {', '.join(unsupported)}")
            if "record_id" in entry and not nonempty_string(entry["record_id"]):
                errors.append(f"{prefix}.record_id must be non-empty")
            if "evidence_refs" not in entry or not ref_list(entry.get("evidence_refs")):
                errors.append(f"{prefix}.evidence_refs must be non-empty structured refs")
            if "unknowns" in entry and not string_list(entry["unknowns"]):
                errors.append(f"{prefix}.unknowns must be a list of strings")


def validate_per_book(row: dict[str, Any], path: Path, line: int, errors: list[str]) -> None:
    required = {
        "book_id",
        "title",
        "chapters_covered",
        "person_scope",
        "identity_facts",
        "narrative_functions",
        "relationship_functions",
        "function_combinations",
        "function_transitions",
        "replaceability",
        "protagonist_interface",
        "relationship_engines",
        "emotion_overlay_links",
        "adjacent_interfaces",
        "source_numbering_notes",
    }
    add_missing(errors, path, line, row, required)
    for field in ("title", "chapters_covered"):
        if field in row and not nonempty_string(row[field]):
            errors.append(f"{path}:{line}: {field} must be non-empty")
    if "person_scope" in row and not string_list(row["person_scope"], allow_empty=False):
        errors.append(f"{path}:{line}: person_scope must be a non-empty list of strings")
    for field in ("emotion_overlay_links", "source_numbering_notes"):
        if field in row and not isinstance(row[field], list):
            errors.append(f"{path}:{line}: {field} must be a list")

    validate_identity_facts(row.get("identity_facts"), path, line, errors)
    validate_narrative_functions(row.get("narrative_functions"), path, line, errors)
    validate_relationship_functions(row.get("relationship_functions"), path, line, errors)
    validate_function_combinations(row.get("function_combinations"), path, line, errors)
    validate_function_transitions(row.get("function_transitions"), path, line, errors)
    validate_replaceability(row.get("replaceability"), path, line, errors)
    validate_protagonist_interface(row.get("protagonist_interface"), path, line, errors)
    validate_relationship_engines(row.get("relationship_engines"), path, line, errors)
    validate_adjacent_interfaces(row.get("adjacent_interfaces"), path, line, errors)


def validate_gap(row: dict[str, Any], path: Path, line: int, errors: list[str]) -> None:
    add_missing(errors, path, line, row, {"reason", "known_evidence", "blocked_outputs"})
    if row.get("confidence") != "LOW":
        errors.append(f"{path}:{line}: gap records must be LOW confidence")
    if not nonempty_string(row.get("reason")):
        errors.append(f"{path}:{line}: gap reason must be non-empty")
    for field in ("known_evidence", "blocked_outputs"):
        if field in row and not string_list(row[field], allow_empty=False):
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
        "function_composition",
        "relationship_engines",
        "function_transitions",
        "replaceability",
        "protagonist_interface",
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
        "engine_pattern",
        "transition_pattern",
        "replaceability_boundary",
        "protagonist_interface_pattern",
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
        "engine_pattern",
        "transition_pattern",
        "replaceability_boundary",
        "protagonist_interface_pattern",
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
        "coverage",
        "identity_function_separation",
        "function_evidence",
        "combination_evidence",
        "transition_chain",
        "relationship_engine_recurrence",
        "replaceability_evidence",
        "protagonist_interface",
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
    required = {
        "candidate_record_ids",
        "recommended_action",
        "decision_points",
        "evidence_summary",
        "boundary_warnings",
        "blocked_by",
    }
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
    parser = argparse.ArgumentParser(description="Validate novel-character-function-miner JSONL outputs.")
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
