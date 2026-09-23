#!/usr/bin/env python3
"""Validate deterministic structure in novel-arc-structure-miner JSONL outputs.

This validator deliberately does not decide whether a volume, map, battle, or
goal is *really* an arc. Those semantic judgments belong to clustering-and-qa.md.
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
ARC_KINDS = {"main", "sub", "parallel", "UNKNOWN"}
LIFECYCLE_STATES = {
    "not_started", "active", "paused", "redirected", "resolved", "failed",
    "abandoned", "unresolved", "UNKNOWN",
}
GOAL_STATES = {"open", "shifted", "resolved", "failed", "abandoned", "UNKNOWN"}
RESOLUTION_OUTCOMES = {"resolved", "failed", "abandoned", "redirected", "unresolved", "UNKNOWN"}
RELATION_TYPES = {"service", "obstacle", "change", "UNKNOWN"}
ARC_FUNCTIONS = {
    "establish", "expand", "validate", "upgrade", "reverse", "expose",
    "reorganize", "transition", "resolve", "ending_setup", "other", "UNKNOWN",
}
NEIGHBOR_DECISIONS = {"merge_candidate", "keep_distinct", "insufficient_evidence"}
CLUSTER_DECISIONS = {
    "candidate_merge", "candidate_split", "new_candidate", "insufficient_evidence",
    "keep_distinct", "unclustered", "HOLD",
}
HANDOFF_ACTIONS = {"保留", "合并候选", "拆分候选", "补证据", "暂缓"}
ADJACENT_KEYS = {
    "plotline", "opening", "character_function", "chapter_emotion",
    "worldbuilding", "cultivation", "golden_finger", "plot_mechanism",
}
INTERFACE_KEYS = {"record_id", "interface_type", "evidence_refs", "note", "unknowns"}
ENVELOPE = {
    "record_type", "schema_version", "record_id", "status", "evidence_refs",
    "unknowns", "confidence", "qa_status",
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


def add_missing(errors: list[str], prefix: str, obj: dict[str, Any], fields: set[str]) -> None:
    missing = sorted(fields - set(obj))
    if missing:
        errors.append(f"{prefix}: missing {', '.join(missing)}")


def required_object(value: Any, prefix: str, errors: list[str], fields: set[str]) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{prefix} must be an object")
        return False
    add_missing(errors, prefix, value, fields)
    return True


def validate_text_fields(value: dict[str, Any], prefix: str, errors: list[str], fields: Iterable[str]) -> None:
    for field in fields:
        if field in value and not nonempty_string(value[field]):
            errors.append(f"{prefix}.{field} must be non-empty")


def validate_evidence_unknowns(value: dict[str, Any], prefix: str, errors: list[str], *, required_refs: bool = True) -> None:
    if "evidence_refs" in value and not ref_list(value["evidence_refs"], allow_empty=not required_refs):
        errors.append(f"{prefix}.evidence_refs must be a structured-ref list")
    if "unknowns" in value and not string_list(value["unknowns"]):
        errors.append(f"{prefix}.unknowns must be a list of strings")


def validate_envelope(
    row: dict[str, Any], kind: str, prefix: str, errors: list[str], record_ids: set[str]
) -> None:
    add_missing(errors, prefix, row, ENVELOPE)
    if row.get("record_type") != kind:
        errors.append(f"{prefix}: record_type must be {kind!r}")
    if row.get("schema_version") != 1:
        errors.append(f"{prefix}: schema_version must be 1")
    record_id = row.get("record_id")
    if not nonempty_string(record_id):
        errors.append(f"{prefix}.record_id must be a non-empty string")
    elif record_id in record_ids:
        errors.append(f"{prefix}: duplicate record_id={record_id}")
    else:
        record_ids.add(record_id)
    if row.get("status") != "candidate":
        errors.append(f"{prefix}: status must remain candidate")
    if row.get("confidence") not in CONFIDENCE:
        errors.append(f"{prefix}.confidence must be HIGH/MEDIUM/LOW")
    if row.get("qa_status") not in QA_STATUS:
        errors.append(f"{prefix}.qa_status must be PASS/HOLD/FAIL")
    if not ref_list(row.get("evidence_refs")):
        errors.append(f"{prefix}.evidence_refs must be a non-empty structured-ref list")
    elif nonempty_string(row.get("book_id")):
        foreign = [ref for ref in row["evidence_refs"] if not ref.startswith(f"{row['book_id']}:")]
        if foreign:
            errors.append(f"{prefix}.evidence_refs cite another book: {', '.join(foreign)}")
    if not string_list(row.get("unknowns")):
        errors.append(f"{prefix}.unknowns must be a list of strings")
    if row.get("confidence") == "HIGH" and row.get("unknowns"):
        errors.append(f"{prefix}: HIGH confidence cannot contain unknowns")

    has_book_id = "book_id" in row
    has_book_ids = "book_ids" in row
    if has_book_id == has_book_ids:
        errors.append(f"{prefix}: exactly one of book_id or book_ids is required")
    if kind in BOOK_KINDS and not has_book_id:
        errors.append(f"{prefix}: {kind} requires book_id")
    if kind in BOOKS_KINDS and not has_book_ids:
        errors.append(f"{prefix}: {kind} requires book_ids")
    if has_book_id and not nonempty_string(row.get("book_id")):
        errors.append(f"{prefix}.book_id must be a non-empty string")
    if has_book_ids:
        book_ids = row.get("book_ids")
        if not isinstance(book_ids, list) or not book_ids or not all(nonempty_string(item) for item in book_ids):
            errors.append(f"{prefix}.book_ids must be a non-empty list of strings")
        elif len(set(book_ids)) != len(book_ids):
            errors.append(f"{prefix}.book_ids must not contain duplicates")


def validate_arc_identity(value: Any, prefix: str, errors: list[str]) -> str | None:
    fields = {"arc_id", "arc_label", "arc_scope", "arc_purpose", "arc_kind", "parent_arc_id", "evidence_refs", "unknowns"}
    if not required_object(value, prefix, errors, fields):
        return None
    validate_text_fields(value, prefix, errors, {"arc_id", "arc_label", "arc_scope", "arc_purpose", "parent_arc_id"})
    if value.get("arc_kind") not in ARC_KINDS:
        errors.append(f"{prefix}.arc_kind is not controlled")
    validate_evidence_unknowns(value, prefix, errors)
    arc_id = value.get("arc_id")
    if nonempty_string(arc_id) and not arc_id.startswith("AR:ARC:"):
        errors.append(f"{prefix}.arc_id must use the AR:ARC: reference form")
    return arc_id if nonempty_string(arc_id) else None


def validate_lifecycle(value: Any, prefix: str, errors: list[str], resolution_outcomes: set[str]) -> None:
    fields = {"current_state", "state_history", "unknowns"}
    if not required_object(value, prefix, errors, fields):
        return
    if value.get("current_state") not in LIFECYCLE_STATES:
        errors.append(f"{prefix}.current_state is not controlled")
    if not isinstance(value.get("state_history"), list):
        errors.append(f"{prefix}.state_history must be a list")
    else:
        history_fields = {"state", "trigger_or_reason", "phase_scope", "evidence_refs", "unknowns"}
        for index, item in enumerate(value["state_history"]):
            item_prefix = f"{prefix}.state_history[{index}]"
            if not required_object(item, item_prefix, errors, history_fields):
                continue
            if item.get("state") not in LIFECYCLE_STATES:
                errors.append(f"{item_prefix}.state is not controlled")
            validate_text_fields(item, item_prefix, errors, {"trigger_or_reason", "phase_scope"})
            validate_evidence_unknowns(item, item_prefix, errors)
    if not string_list(value.get("unknowns")):
        errors.append(f"{prefix}.unknowns must be a list of strings")
    current = value.get("current_state")
    if current in {"resolved", "failed", "abandoned", "redirected", "unresolved"}:
        if current not in resolution_outcomes and not any(
            isinstance(item, dict) and item.get("state") == current
            for item in value.get("state_history", [])
        ):
            errors.append(f"{prefix}: {current} lifecycle state lacks matching resolution/history evidence")


def validate_array(value: Any, prefix: str, errors: list[str]) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        errors.append(f"{prefix} must be a list")
        return []
    result: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            errors.append(f"{prefix}[{index}] must be an object")
        else:
            result.append(item)
    return result


def validate_items(
    value: Any,
    prefix: str,
    errors: list[str],
    fields: set[str],
    text_fields: set[str],
    ids: set[str] | None = None,
    id_field: str | None = None,
    enums: dict[str, set[str]] | None = None,
) -> list[dict[str, Any]]:
    items = validate_array(value, prefix, errors)
    for index, item in enumerate(items):
        item_prefix = f"{prefix}[{index}]"
        add_missing(errors, item_prefix, item, fields)
        validate_text_fields(item, item_prefix, errors, text_fields)
        validate_evidence_unknowns(item, item_prefix, errors)
        for field, allowed in (enums or {}).items():
            if field in item and item[field] not in allowed:
                errors.append(f"{item_prefix}.{field} is not controlled")
        if ids is not None and id_field is not None and nonempty_string(item.get(id_field)):
            item_id = item[id_field]
            if item_id in ids:
                errors.append(f"{item_prefix}: duplicate {id_field}={item_id}")
            ids.add(item_id)
    return items


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
                if not nonempty_string(entry) or len(entry.split(":")) < 3 or any(c.isspace() for c in entry):
                    errors.append(f"{item_prefix} must be a structured reference string")
                continue
            if not isinstance(entry, dict):
                errors.append(f"{item_prefix} must be a reference string or object")
                continue
            unsupported = sorted(set(entry) - INTERFACE_KEYS)
            if unsupported:
                errors.append(f"{item_prefix} contains non-reference fields: {', '.join(unsupported)}")
            add_missing(errors, item_prefix, entry, INTERFACE_KEYS)
            validate_text_fields(entry, item_prefix, errors, {"record_id", "interface_type", "note"})
            validate_evidence_unknowns(entry, item_prefix, errors)


def validate_single_arc(row: dict[str, Any], prefix: str, errors: list[str]) -> None:
    required = {
        "book_id", "title", "chapters_covered", "arc_identity", "arc_boundary", "arc_goal",
        "arc_pressure", "arc_progression", "arc_turning_points", "arc_climax_or_resolution",
        "arc_state_change", "next_arc_entry", "arc_function", "nested_structure",
        "arc_lifecycle", "adjacent_interfaces",
    }
    add_missing(errors, prefix, row, required)
    validate_text_fields(row, prefix, errors, {"title", "chapters_covered"})
    arc_id = validate_arc_identity(row.get("arc_identity"), f"{prefix}.arc_identity", errors)

    boundary_fields = {"boundary_id", "before_structure", "after_structure", "triggering_change", "chapter_or_stage_scope", "structural_difference", "evidence_refs", "unknowns"}
    validate_items(row.get("arc_boundary"), f"{prefix}.arc_boundary", errors, boundary_fields, {"boundary_id", "before_structure", "after_structure", "triggering_change", "chapter_or_stage_scope", "structural_difference"}, set(), "boundary_id")
    goal_ids: set[str] = set()
    goal_fields = {"goal_id", "primary_goal_or_structural_task", "serves_or_organizes", "phase_scope", "completion_condition", "invalidation_or_failure_condition", "goal_status", "evidence_refs", "unknowns"}
    goals = validate_items(row.get("arc_goal"), f"{prefix}.arc_goal", errors, goal_fields, {"goal_id", "primary_goal_or_structural_task", "phase_scope", "completion_condition", "invalidation_or_failure_condition"}, goal_ids, "goal_id", {"goal_status": GOAL_STATES})
    for index, goal in enumerate(goals):
        if not string_list(goal.get("serves_or_organizes"), allow_empty=False):
            errors.append(f"{prefix}.arc_goal[{index}].serves_or_organizes must be a non-empty list of strings")

    pressure_fields = {"pressure_id", "pressure_source_or_type", "operation", "affected_targets", "observable_effect", "phase_scope", "evidence_refs", "unknowns"}
    pressures = validate_items(row.get("arc_pressure"), f"{prefix}.arc_pressure", errors, pressure_fields, {"pressure_id", "pressure_source_or_type", "operation", "observable_effect", "phase_scope"}, set(), "pressure_id")
    for index, item in enumerate(pressures):
        if not string_list(item.get("affected_targets"), allow_empty=False):
            errors.append(f"{prefix}.arc_pressure[{index}].affected_targets must be a non-empty list of strings")

    progression_fields = {"progression_id", "before_stage_state", "progression_step", "after_stage_state", "structural_effect", "phase_scope", "evidence_refs", "unknowns"}
    validate_items(row.get("arc_progression"), f"{prefix}.arc_progression", errors, progression_fields, {"progression_id", "before_stage_state", "progression_step", "after_stage_state", "structural_effect", "phase_scope"}, set(), "progression_id")

    turning_fields = {"turning_point_id", "turning_event", "before_direction_or_priority", "after_direction_or_priority", "structural_effect", "phase_scope", "evidence_refs", "unknowns"}
    turning_points = validate_items(row.get("arc_turning_points"), f"{prefix}.arc_turning_points", errors, turning_fields, {"turning_point_id", "turning_event", "before_direction_or_priority", "after_direction_or_priority", "structural_effect", "phase_scope"}, set(), "turning_point_id")
    turning_ids = {item.get("turning_point_id") for item in turning_points if nonempty_string(item.get("turning_point_id"))}

    resolution_fields = {"resolution_id", "climax_or_resolution_event", "resolution_outcome", "resolved_or_unresolved_structure", "affected_arc_goal_ids", "phase_scope", "evidence_refs", "unknowns"}
    resolution_ids: set[str] = set()
    resolutions = validate_items(row.get("arc_climax_or_resolution"), f"{prefix}.arc_climax_or_resolution", errors, resolution_fields, {"resolution_id", "climax_or_resolution_event", "resolved_or_unresolved_structure", "phase_scope"}, resolution_ids, "resolution_id", {"resolution_outcome": RESOLUTION_OUTCOMES})
    resolution_outcomes = {item.get("resolution_outcome") for item in resolutions if item.get("resolution_outcome") in RESOLUTION_OUTCOMES}
    for index, item in enumerate(resolutions):
        if not string_list(item.get("affected_arc_goal_ids"), allow_empty=False):
            errors.append(f"{prefix}.arc_climax_or_resolution[{index}].affected_arc_goal_ids must be a non-empty list")
        else:
            for goal_id in item["affected_arc_goal_ids"]:
                if goal_id != "UNKNOWN" and goal_id not in goal_ids:
                    errors.append(f"{prefix}.arc_climax_or_resolution[{index}].affected_arc_goal_ids must reference local goals")

    state_fields = {"state_change_id", "caused_by_resolution_or_turning_point", "changed_domains", "before_global_state", "after_global_state", "structural_effect", "evidence_refs", "unknowns"}
    state_ids: set[str] = set()
    states = validate_items(row.get("arc_state_change"), f"{prefix}.arc_state_change", errors, state_fields, {"state_change_id", "caused_by_resolution_or_turning_point", "before_global_state", "after_global_state", "structural_effect"}, state_ids, "state_change_id")
    allowed_causes = resolution_ids | turning_ids
    for index, item in enumerate(states):
        if not string_list(item.get("changed_domains"), allow_empty=False):
            errors.append(f"{prefix}.arc_state_change[{index}].changed_domains must be a non-empty list")
        cause = item.get("caused_by_resolution_or_turning_point")
        if nonempty_string(cause) and cause != "UNKNOWN" and cause not in allowed_causes:
            errors.append(f"{prefix}.arc_state_change[{index}].caused_by_resolution_or_turning_point must reference a local resolution or turning point")

    entry_fields = {"entry_id", "source_state_change_id", "opened_next_arc_goal_or_task", "opened_pressure_or_risk", "opened_map_permission_or_question", "next_arc_reference", "entry_reason", "evidence_refs", "unknowns"}
    entries = validate_items(row.get("next_arc_entry"), f"{prefix}.next_arc_entry", errors, entry_fields, {"entry_id", "source_state_change_id", "opened_next_arc_goal_or_task", "opened_pressure_or_risk", "opened_map_permission_or_question", "next_arc_reference", "entry_reason"}, set(), "entry_id")
    for index, item in enumerate(entries):
        source = item.get("source_state_change_id")
        if nonempty_string(source) and source != "UNKNOWN" and source not in state_ids:
            errors.append(f"{prefix}.next_arc_entry[{index}].source_state_change_id must reference a local arc_state_change")

    function_fields = {"function_id", "structural_function", "function_description", "affected_global_expectation", "phase_scope", "evidence_refs", "unknowns"}
    validate_items(row.get("arc_function"), f"{prefix}.arc_function", errors, function_fields, {"function_id", "function_description", "affected_global_expectation", "phase_scope"}, set(), "function_id", {"structural_function": ARC_FUNCTIONS})

    nested_fields = {"relation_id", "parent_arc_id", "sub_arc_id", "relation_type", "how_sub_arc_affects_parent", "sub_arc_completion_effect", "pause_relationship", "evidence_refs", "unknowns"}
    nested = validate_items(row.get("nested_structure"), f"{prefix}.nested_structure", errors, nested_fields, {"relation_id", "parent_arc_id", "sub_arc_id", "how_sub_arc_affects_parent", "sub_arc_completion_effect", "pause_relationship"}, set(), "relation_id", {"relation_type": RELATION_TYPES})
    edges: list[tuple[str, str]] = []
    for index, item in enumerate(nested):
        parent = item.get("parent_arc_id")
        child = item.get("sub_arc_id")
        for field, ref in (("parent_arc_id", parent), ("sub_arc_id", child)):
            if nonempty_string(ref) and ref != "UNKNOWN" and not ref.startswith("AR:ARC:"):
                errors.append(f"{prefix}.nested_structure[{index}].{field} must use AR:ARC: reference form")
        if nonempty_string(parent) and nonempty_string(child) and parent == child:
            errors.append(f"{prefix}.nested_structure[{index}]: parent_arc_id and sub_arc_id must differ")
        if nonempty_string(parent) and nonempty_string(child) and parent != "UNKNOWN" and child != "UNKNOWN":
            edges.append((parent, child))
    if has_cycle(edges):
        errors.append(f"{prefix}.nested_structure contains a cycle")
    if arc_id is not None and any(parent == child == arc_id for parent, child in edges):
        errors.append(f"{prefix}.nested_structure contains a self-reference")

    validate_lifecycle(row.get("arc_lifecycle"), f"{prefix}.arc_lifecycle", errors, resolution_outcomes)
    validate_adjacent_interfaces(row.get("adjacent_interfaces"), f"{prefix}.adjacent_interfaces", errors)


def validate_per_book(row: dict[str, Any], prefix: str, errors: list[str]) -> None:
    """Validate a book bundle containing zero or more independently evidenced arcs."""
    required = {"book_id", "title", "chapters_covered", "arcs", "adjacent_interfaces"}
    add_missing(errors, prefix, row, required)
    validate_text_fields(row, prefix, errors, {"title", "chapters_covered"})
    arcs = row.get("arcs")
    if not isinstance(arcs, list):
        errors.append(f"{prefix}.arcs must be a list")
        return
    if not arcs:
        errors.append(f"{prefix}.arcs must contain at least one arc; use record_type=gap when no arc is evidenced")
        return
    arc_ids: set[str] = set()
    for index, arc in enumerate(arcs):
        item_prefix = f"{prefix}.arcs[{index}]"
        if not isinstance(arc, dict):
            errors.append(f"{item_prefix} must be an object")
            continue
        proxy = dict(arc)
        proxy.setdefault("book_id", row.get("book_id"))
        proxy.setdefault("title", row.get("title"))
        proxy.setdefault("chapters_covered", row.get("chapters_covered"))
        proxy.setdefault("adjacent_interfaces", row.get("adjacent_interfaces"))
        validate_single_arc(proxy, item_prefix, errors)
        identity = arc.get("arc_identity")
        if isinstance(identity, dict) and nonempty_string(identity.get("arc_id")):
            arc_id = identity["arc_id"]
            if arc_id in arc_ids:
                errors.append(f"{item_prefix}: duplicate arc_identity.arc_id={arc_id}")
            arc_ids.add(arc_id)
def has_cycle(edges: list[tuple[str, str]]) -> bool:
    graph: dict[str, set[str]] = {}
    for parent, child in edges:
        graph.setdefault(parent, set()).add(child)
        graph.setdefault(child, set())
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        if any(visit(child) for child in graph.get(node, set())):
            return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in graph)


def validate_gap(row: dict[str, Any], prefix: str, errors: list[str]) -> None:
    add_missing(errors, prefix, row, {"reason", "known_evidence", "blocked_outputs"})
    if row.get("confidence") != "LOW":
        errors.append(f"{prefix}: gap records must be LOW confidence")
    if not nonempty_string(row.get("reason")):
        errors.append(f"{prefix}.reason must be non-empty")
    for field in ("known_evidence", "blocked_outputs"):
        if not string_list(row.get(field), allow_empty=False):
            errors.append(f"{prefix}.{field} must be a non-empty list of strings")


def validate_nearest_neighbor(row: dict[str, Any], prefix: str, errors: list[str]) -> None:
    required = {"comparison_ids", "comparison_dimensions", "similarities", "difference_boundary", "surface_labels_excluded", "decision", "reason"}
    add_missing(errors, prefix, row, required)
    book_ids = row.get("book_ids")
    if isinstance(book_ids, list) and len(set(book_ids)) < 2:
        errors.append(f"{prefix}: nearest_neighbor requires at least two distinct book_ids")
    if not string_list(row.get("comparison_ids"), allow_empty=False):
        errors.append(f"{prefix}.comparison_ids must be a non-empty list of strings")
    dimensions = row.get("comparison_dimensions")
    required_dimensions = {"boundary_and_goal", "pressure_and_progression", "turning_and_resolution", "state_change_and_next_entry", "nested_structure", "adjacent_interfaces"}
    if not isinstance(dimensions, dict):
        errors.append(f"{prefix}.comparison_dimensions must be an object")
    else:
        add_missing(errors, f"{prefix}.comparison_dimensions", dimensions, required_dimensions)
        validate_text_fields(dimensions, f"{prefix}.comparison_dimensions", errors, required_dimensions)
    if not isinstance(row.get("similarities"), list):
        errors.append(f"{prefix}.similarities must be a list")
    if not string_list(row.get("surface_labels_excluded"), allow_empty=False):
        errors.append(f"{prefix}.surface_labels_excluded must be a non-empty list")
    for field in ("difference_boundary", "decision", "reason"):
        if not nonempty_string(row.get(field)):
            errors.append(f"{prefix}.{field} must be non-empty")
    if row.get("decision") not in NEIGHBOR_DECISIONS:
        errors.append(f"{prefix}.decision is not controlled")


def validate_cluster(row: dict[str, Any], prefix: str, errors: list[str]) -> None:
    required = {"member_record_ids", "cluster_level", "label", "shared_operation", "progression_resolution_pattern", "nested_structure_pattern", "boundary_conditions", "supporting_book_count", "nearest_neighbor_record_ids", "merge_decision"}
    add_missing(errors, prefix, row, required)
    book_ids = row.get("book_ids")
    if isinstance(book_ids, list):
        if len(set(book_ids)) < 2:
            errors.append(f"{prefix}: cluster requires at least two distinct book_ids")
        if row.get("supporting_book_count") != len(set(book_ids)):
            errors.append(f"{prefix}.supporting_book_count must match unique book_ids")
    elif not isinstance(row.get("supporting_book_count"), int):
        errors.append(f"{prefix}.supporting_book_count must be an integer")
    for field in ("member_record_ids", "boundary_conditions", "nearest_neighbor_record_ids"):
        if not string_list(row.get(field), allow_empty=False):
            errors.append(f"{prefix}.{field} must be a non-empty list of strings")
    for field in ("cluster_level", "label", "shared_operation", "progression_resolution_pattern", "nested_structure_pattern"):
        if not nonempty_string(row.get(field)):
            errors.append(f"{prefix}.{field} must be non-empty")
    if row.get("merge_decision") not in CLUSTER_DECISIONS:
        errors.append(f"{prefix}.merge_decision is not controlled")


def validate_qa(row: dict[str, Any], prefix: str, errors: list[str]) -> None:
    add_missing(errors, prefix, row, {"scope", "checks", "gaps", "disputes", "blocked_outputs"})
    if not nonempty_string(row.get("scope")):
        errors.append(f"{prefix}.scope must be non-empty")
    required_checks = {"arc_boundary", "goal_and_pressure", "progression", "turning_points", "climax_or_resolution", "state_change", "next_arc_entry", "arc_function", "nested_structure", "adjacent_boundary", "cross_book_gate"}
    checks = row.get("checks")
    if not isinstance(checks, dict):
        errors.append(f"{prefix}.checks must be an object")
    else:
        add_missing(errors, f"{prefix}.checks", checks, required_checks)
        for field in required_checks:
            if field in checks and checks[field] not in QA_STATUS:
                errors.append(f"{prefix}.checks.{field} must be PASS/HOLD/FAIL")
    for field in ("gaps", "disputes", "blocked_outputs"):
        if field in row and not isinstance(row[field], list):
            errors.append(f"{prefix}.{field} must be a list")


def validate_handoff(row: dict[str, Any], prefix: str, errors: list[str]) -> None:
    required = {"candidate_record_ids", "recommended_action", "decision_points", "evidence_summary", "boundary_warnings", "blocked_by"}
    add_missing(errors, prefix, row, required)
    if not string_list(row.get("candidate_record_ids"), allow_empty=False):
        errors.append(f"{prefix}.candidate_record_ids must be a non-empty list of strings")
    for field in ("decision_points", "evidence_summary", "boundary_warnings", "blocked_by"):
        if field in row and not isinstance(row[field], list):
            errors.append(f"{prefix}.{field} must be a list")
    if row.get("recommended_action") not in HANDOFF_ACTIONS:
        errors.append(f"{prefix}.recommended_action is not controlled")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Validate novel-arc-structure-miner JSONL outputs.")
    parser.add_argument("target", type=Path, help="A JSONL file or directory containing JSONL files.")
    parser.add_argument("--kind", required=True, choices=sorted(KINDS))
    parser.add_argument("--expected-books", help="Optional comma-separated books for per_book/gap coverage checks.")
    parser.add_argument("--all-books-complete", action="store_true", help="Acknowledge the explicit completion manifest gate for cross-book records.")
    parser.add_argument("--completion-manifest", type=Path, help="JSONL containing exactly one candidate per_book or gap record for every expected book.")
    args = parser.parse_args()

    if args.kind in {"nearest_neighbor", "cluster"} and not args.all_books_complete:
        print(json.dumps({"records": 0, "errors": ["completion gate required: pass --all-books-complete"], "ok": False}, ensure_ascii=False, indent=2))
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
    if args.kind in {"nearest_neighbor", "cluster"}:
        errors.extend(load_completion_manifest(args.completion_manifest, expected_books))
    covered_books: list[str] = []
    found_file = False
    for path, line, raw in iter_jsonl(args.target):
        found_file = True
        prefix = f"{path}:{line}"
        if not raw.strip():
            errors.append(f"{prefix}: empty JSONL line")
            continue
        records += 1
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"{prefix}: invalid JSON: {exc}")
            continue
        if not isinstance(row, dict):
            errors.append(f"{prefix}: each JSONL record must be an object")
            continue
        validate_envelope(row, args.kind, prefix, errors, record_ids)
        if nonempty_string(row.get("book_id")):
            covered_books.append(row["book_id"])
        if args.kind == "per_book":
            validate_per_book(row, prefix, errors)
        elif args.kind == "gap":
            validate_gap(row, prefix, errors)
        elif args.kind == "nearest_neighbor":
            validate_nearest_neighbor(row, prefix, errors)
        elif args.kind == "cluster":
            validate_cluster(row, prefix, errors)
        elif args.kind == "qa":
            validate_qa(row, prefix, errors)
        elif args.kind == "handoff":
            validate_handoff(row, prefix, errors)

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

    result = {"kind": args.kind, "records": records, "covered_books": sorted(set(covered_books)), "errors": errors, "ok": not errors}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
