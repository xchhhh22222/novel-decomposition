#!/usr/bin/env python3
"""Validate deterministic structure in novel-plot-mechanism-miner JSONL outputs.

Semantic questions such as whether two instances really form one mechanism are
left to clustering-and-qa.md and human review.
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
BOOK_KINDS = {"per_book", "gap", "qa"}
BOOKS_KINDS = {"nearest_neighbor", "cluster", "handoff"}
CONDITION_KINDS = {"necessary", "optional", "enabling", "UNKNOWN"}
INPUT_KINDS = {"information", "resource", "identity", "rule", "risk", "relationship", "time", "permission", "expectation", "other", "UNKNOWN"}
REQUIRED_OPTIONAL = {"required", "optional", "enabling", "UNKNOWN"}
CONSUMPTION = {"consumed", "retained", "transformed", "UNKNOWN"}
INSTANCE_RELATIONS = {"supports", "contrasts", "unclear", "UNKNOWN"}
OUTPUT_KINDS = {"result", "resource", "information", "permission", "recognition", "relationship", "risk", "failure", "other", "UNKNOWN"}
PAYOFF_RELATIONS = {"not_established", "supports", "part_of_payoff", "UNKNOWN"}
REPEATABILITY_STATUS = {"supported", "partial", "not_supported", "UNKNOWN"}
EVIDENCE_BASIS = {"multiple_observed_instances", "explicit_reusable_rule", "mixed", "single_instance_only", "UNKNOWN"}
VARIATION_DOMAINS = {"actor", "resource", "information", "constraint", "stakes", "path", "output", "map", "relationship", "other", "UNKNOWN"}
ADJACENT_KEYS = {"plotline", "arc_structure", "opening", "character_function", "chapter_emotion", "worldbuilding", "cultivation", "golden_finger"}
INTERFACE_KEYS = {"record_id", "interface_type", "evidence_refs", "note", "unknowns"}
ENVELOPE = {"record_type", "schema_version", "record_id", "status", "evidence_refs", "unknowns", "confidence", "qa_status"}
NEIGHBOR_DECISIONS = {"merge_candidate", "keep_distinct", "insufficient_evidence"}
CLUSTER_DECISIONS = {"candidate_merge", "candidate_split", "new_candidate", "insufficient_evidence", "keep_distinct", "unclustered", "HOLD"}
HANDOFF_ACTIONS = {"保留", "合并候选", "拆分候选", "补证据", "暂缓"}


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
    return isinstance(value, list) and (allow_empty or bool(value)) and all(nonempty_string(item) for item in value)


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
    extra = sorted(set(value) - fields)
    if extra:
        errors.append(f"{prefix} has unsupported fields: {', '.join(extra)}")
    return True


def text_fields(obj: dict[str, Any], prefix: str, errors: list[str], fields: Iterable[str]) -> None:
    for field in fields:
        if field in obj and not nonempty_string(obj[field]):
            errors.append(f"{prefix}.{field} must be non-empty")


def evidence_unknowns(obj: dict[str, Any], prefix: str, errors: list[str], *, required_refs: bool = True) -> None:
    if "evidence_refs" in obj and not ref_list(obj["evidence_refs"], allow_empty=not required_refs):
        errors.append(f"{prefix}.evidence_refs must be a structured-ref list")
    if "unknowns" in obj and not string_list(obj["unknowns"]):
        errors.append(f"{prefix}.unknowns must be a list of strings")


def validate_envelope(row: dict[str, Any], kind: str, prefix: str, errors: list[str], record_ids: set[str]) -> None:
    add_missing(errors, prefix, row, ENVELOPE)
    if row.get("record_type") != kind:
        errors.append(f"{prefix}: record_type must be {kind!r}")
    if row.get("schema_version") != 1:
        errors.append(f"{prefix}.schema_version must be 1")
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


def validate_items(
    value: Any,
    prefix: str,
    errors: list[str],
    fields: set[str],
    required_text: set[str],
    ids: set[str] | None = None,
    id_field: str | None = None,
    enum_fields: dict[str, set[str]] | None = None,
) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        errors.append(f"{prefix} must be a list")
        return []
    items: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        item_prefix = f"{prefix}[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_prefix} must be an object")
            continue
        items.append(item)
        add_missing(errors, item_prefix, item, fields)
        extra = sorted(set(item) - fields)
        if extra:
            errors.append(f"{item_prefix} has unsupported fields: {', '.join(extra)}")
        text_fields(item, item_prefix, errors, required_text)
        evidence_unknowns(item, item_prefix, errors)
        for field, allowed in (enum_fields or {}).items():
            if field in item and item[field] not in allowed:
                errors.append(f"{item_prefix}.{field} is not controlled")
        if ids is not None and id_field is not None and nonempty_string(item.get(id_field)):
            item_id = item[id_field]
            if item_id in ids:
                errors.append(f"{item_prefix}: duplicate {id_field}={item_id}")
            ids.add(item_id)
    return items


def validate_identity(value: Any, prefix: str, errors: list[str]) -> str | None:
    fields = {"mechanism_id", "mechanism_label", "mechanism_description", "reusable_operation", "applicability_scope", "core_invariants", "excluded_surface_labels", "distinction_boundary", "evidence_refs", "unknowns"}
    if not required_object(value, prefix, errors, fields):
        return None
    text_fields(value, prefix, errors, {"mechanism_id", "mechanism_label", "mechanism_description", "reusable_operation", "applicability_scope", "distinction_boundary"})
    for field in ("core_invariants", "excluded_surface_labels"):
        if not string_list(value.get(field), allow_empty=False):
            errors.append(f"{prefix}.{field} must be a non-empty list of strings")
    evidence_unknowns(value, prefix, errors)
    return value.get("mechanism_id") if nonempty_string(value.get("mechanism_id")) else None


def validate_instances(value: Any, prefix: str, errors: list[str]) -> list[dict[str, Any]]:
    fields = {"instance_id", "book_id", "chapter_or_stage_scope", "instance_summary", "mechanism_candidate_relation", "evidence_refs", "unknowns"}
    items = validate_items(value, prefix, errors, fields, {"instance_id", "book_id", "chapter_or_stage_scope", "instance_summary"}, set(), "instance_id", {"mechanism_candidate_relation": INSTANCE_RELATIONS})
    for index, item in enumerate(items):
        if not nonempty_string(item.get("book_id")):
            errors.append(f"{prefix}[{index}].book_id must be non-empty")
    return items


def validate_repeatability(value: Any, prefix: str, errors: list[str], instance_count: int) -> None:
    fields = {"repeatability_status", "evidence_basis", "repeat_conditions", "reset_retain_or_reacquire", "core_invariants", "reusable_scope", "repeatability_evidence_refs", "unknowns"}
    if not required_object(value, prefix, errors, fields):
        return
    if "repeatable" in value:
        errors.append(f"{prefix}: boolean repeatable is not allowed; use repeatability_status and evidence_basis")
    if value.get("repeatability_status") not in REPEATABILITY_STATUS:
        errors.append(f"{prefix}.repeatability_status is not controlled")
    if value.get("evidence_basis") not in EVIDENCE_BASIS:
        errors.append(f"{prefix}.evidence_basis is not controlled")
    text_fields(value, prefix, errors, {"reusable_scope"})
    for field in ("repeat_conditions", "reset_retain_or_reacquire", "core_invariants"):
        if not string_list(value.get(field), allow_empty=False):
            errors.append(f"{prefix}.{field} must be a non-empty list of strings")
    if not ref_list(value.get("repeatability_evidence_refs")):
        errors.append(f"{prefix}.repeatability_evidence_refs must be a non-empty structured-ref list")
    if value.get("repeatability_status") == "supported" and value.get("evidence_basis") == "single_instance_only":
        errors.append(f"{prefix}: single_instance_only cannot support repeatability")
    if value.get("repeatability_status") == "supported" and value.get("evidence_basis") == "multiple_observed_instances" and instance_count < 2:
        errors.append(f"{prefix}: multiple_observed_instances requires at least two observed instance references")


def validate_adjacent(value: Any, prefix: str, errors: list[str]) -> None:
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
                if not nonempty_string(entry) or len(entry.split(":")) < 3 or any(char.isspace() for char in entry):
                    errors.append(f"{item_prefix} must be a structured reference string")
                continue
            if not isinstance(entry, dict):
                errors.append(f"{item_prefix} must be a reference string or object")
                continue
            unsupported = sorted(set(entry) - INTERFACE_KEYS)
            if unsupported:
                errors.append(f"{item_prefix} contains non-reference fields: {', '.join(unsupported)}")
            add_missing(errors, item_prefix, entry, INTERFACE_KEYS)
            text_fields(entry, item_prefix, errors, {"record_id", "interface_type", "note"})
            evidence_unknowns(entry, item_prefix, errors)


def validate_single_mechanism(row: dict[str, Any], prefix: str, errors: list[str]) -> None:
    required = {"book_id", "title", "chapters_covered", "mechanism_identity", "observed_instances", "trigger_conditions", "actors_and_roles", "inputs", "operations", "decision_points", "constraints", "escalation_logic", "outputs", "state_transition", "repeatability", "variation_points", "failure_modes", "payoff_path", "adjacent_interfaces"}
    add_missing(errors, prefix, row, required)
    text_fields(row, prefix, errors, {"title", "chapters_covered"})
    validate_identity(row.get("mechanism_identity"), f"{prefix}.mechanism_identity", errors)
    instances = validate_instances(row.get("observed_instances"), f"{prefix}.observed_instances", errors)
    if not instances:
        errors.append(f"{prefix}.observed_instances must contain at least one evidence reference for per_book")

    trigger_fields = {"condition_id", "condition_kind", "condition_description", "source_state", "trigger_observation", "evidence_refs", "unknowns"}
    validate_items(row.get("trigger_conditions"), f"{prefix}.trigger_conditions", errors, trigger_fields, {"condition_id", "condition_description", "source_state", "trigger_observation"}, set(), "condition_id", {"condition_kind": CONDITION_KINDS})
    actor_fields = {"actor_role_id", "actor_reference", "mechanism_role", "actual_operation", "response_or_dependency", "evidence_refs", "unknowns"}
    validate_items(row.get("actors_and_roles"), f"{prefix}.actors_and_roles", errors, actor_fields, {"actor_role_id", "actor_reference", "mechanism_role", "actual_operation", "response_or_dependency"}, set(), "actor_role_id")
    input_fields = {"input_id", "input_kind", "input_description", "required_or_optional", "consumed_or_retained", "provided_by_or_source", "evidence_refs", "unknowns"}
    validate_items(row.get("inputs"), f"{prefix}.inputs", errors, input_fields, {"input_id", "input_description", "provided_by_or_source"}, set(), "input_id", {"input_kind": INPUT_KINDS, "required_or_optional": REQUIRED_OPTIONAL, "consumed_or_retained": CONSUMPTION})

    operation_fields = {"operation_id", "order_or_dependency", "operation", "required_input_or_state", "resulting_intermediate_state", "depends_on_operation_ids", "evidence_refs", "unknowns"}
    operation_ids: set[str] = set()
    operations = validate_items(row.get("operations"), f"{prefix}.operations", errors, operation_fields, {"operation_id", "order_or_dependency", "operation", "required_input_or_state", "resulting_intermediate_state"}, operation_ids, "operation_id")
    for index, item in enumerate(operations):
        deps = item.get("depends_on_operation_ids")
        if not string_list(deps):
            errors.append(f"{prefix}.operations[{index}].depends_on_operation_ids must be a list of strings")
        elif any(dep != "UNKNOWN" and dep not in operation_ids for dep in deps):
            errors.append(f"{prefix}.operations[{index}].depends_on_operation_ids must reference local operations")

    decision_fields = {"decision_id", "decision_maker", "decision_context", "available_paths", "chosen_or_observed_path", "path_consequence", "evidence_refs", "unknowns"}
    decision_ids: set[str] = set()
    decisions = validate_items(row.get("decision_points"), f"{prefix}.decision_points", errors, decision_fields, {"decision_id", "decision_maker", "decision_context", "chosen_or_observed_path", "path_consequence"}, decision_ids, "decision_id")
    for index, item in enumerate(decisions):
        paths = item.get("available_paths")
        if not string_list(paths, allow_empty=False):
            errors.append(f"{prefix}.decision_points[{index}].available_paths must be a non-empty list of strings")
        chosen = item.get("chosen_or_observed_path")
        if nonempty_string(chosen) and chosen != "UNKNOWN" and isinstance(paths, list) and chosen not in paths:
            errors.append(f"{prefix}.decision_points[{index}].chosen_or_observed_path must be one of available_paths")

    constraint_fields = {"constraint_id", "constraint_kind", "constraint_operation", "affected_step_or_role", "observable_effect", "evidence_refs", "unknowns"}
    validate_items(row.get("constraints"), f"{prefix}.constraints", errors, constraint_fields, {"constraint_id", "constraint_kind", "constraint_operation", "affected_step_or_role", "observable_effect"}, set(), "constraint_id")
    escalation_fields = {"escalation_id", "before_pressure_or_state", "escalation_change", "after_pressure_or_state", "structural_effect", "trigger_or_reason", "evidence_refs", "unknowns"}
    validate_items(row.get("escalation_logic"), f"{prefix}.escalation_logic", errors, escalation_fields, {"escalation_id", "before_pressure_or_state", "escalation_change", "after_pressure_or_state", "structural_effect", "trigger_or_reason"}, set(), "escalation_id")
    output_fields = {"output_id", "output_kind", "output", "observable_evidence", "affected_targets", "payoff_relation", "evidence_refs", "unknowns"}
    outputs = validate_items(row.get("outputs"), f"{prefix}.outputs", errors, output_fields, {"output_id", "output", "observable_evidence"}, set(), "output_id", {"output_kind": OUTPUT_KINDS, "payoff_relation": PAYOFF_RELATIONS})
    for index, item in enumerate(outputs):
        if not string_list(item.get("affected_targets"), allow_empty=False):
            errors.append(f"{prefix}.outputs[{index}].affected_targets must be a non-empty list of strings")

    state_fields = {"state_transition_id", "before_state", "mechanism_run_or_result", "after_state", "changed_domains", "observable_consequence", "evidence_refs", "unknowns"}
    states = validate_items(row.get("state_transition"), f"{prefix}.state_transition", errors, state_fields, {"state_transition_id", "before_state", "mechanism_run_or_result", "after_state", "observable_consequence"}, set(), "state_transition_id")
    for index, item in enumerate(states):
        if not string_list(item.get("changed_domains"), allow_empty=False):
            errors.append(f"{prefix}.state_transition[{index}].changed_domains must be a non-empty list of strings")
    validate_repeatability(row.get("repeatability"), f"{prefix}.repeatability", errors, len(instances))
    variation_fields = {"variation_id", "variable_domain", "what_can_change", "invariant_preserved", "effect_on_repetition", "evidence_refs", "unknowns"}
    validate_items(row.get("variation_points"), f"{prefix}.variation_points", errors, variation_fields, {"variation_id", "what_can_change", "invariant_preserved", "effect_on_repetition"}, set(), "variation_id", {"variable_domain": VARIATION_DOMAINS})
    failure_fields = {"failure_mode_id", "failure_condition", "break_point", "effect", "recoverability_or_next_state", "evidence_refs", "unknowns"}
    validate_items(row.get("failure_modes"), f"{prefix}.failure_modes", errors, failure_fields, {"failure_mode_id", "failure_condition", "break_point", "effect", "recoverability_or_next_state"}, set(), "failure_mode_id")
    payoff_fields = {"payoff_path_id", "prior_pressure_promise_or_choice", "operation_ids", "decision_ids", "payoff_or_recovery_result", "visible_payoff_evidence", "state_or_expectation_effect", "evidence_refs", "unknowns"}
    payoff_paths = validate_items(row.get("payoff_path"), f"{prefix}.payoff_path", errors, payoff_fields, {"payoff_path_id", "prior_pressure_promise_or_choice", "payoff_or_recovery_result", "visible_payoff_evidence", "state_or_expectation_effect"}, set(), "payoff_path_id")
    for index, item in enumerate(payoff_paths):
        for field, allowed in (("operation_ids", operation_ids), ("decision_ids", decision_ids)):
            refs = item.get(field)
            if not string_list(refs, allow_empty=False):
                errors.append(f"{prefix}.payoff_path[{index}].{field} must be a non-empty list of strings")
            elif any(ref != "UNKNOWN" and ref not in allowed for ref in refs):
                errors.append(f"{prefix}.payoff_path[{index}].{field} must reference local objects")
    validate_adjacent(row.get("adjacent_interfaces"), f"{prefix}.adjacent_interfaces", errors)


def validate_per_book(row: dict[str, Any], prefix: str, errors: list[str]) -> None:
    """Validate a book bundle containing independently evidenced mechanisms."""
    required = {"book_id", "title", "chapters_covered", "mechanisms", "adjacent_interfaces"}
    add_missing(errors, prefix, row, required)
    text_fields(row, prefix, errors, {"title", "chapters_covered"})
    mechanisms = row.get("mechanisms")
    if not isinstance(mechanisms, list):
        errors.append(f"{prefix}.mechanisms must be a list")
        return
    if not mechanisms:
        errors.append(f"{prefix}.mechanisms must contain at least one mechanism; use record_type=gap when none is evidenced")
        return
    mechanism_ids: set[str] = set()
    for index, mechanism in enumerate(mechanisms):
        item_prefix = f"{prefix}.mechanisms[{index}]"
        if not isinstance(mechanism, dict):
            errors.append(f"{item_prefix} must be an object")
            continue
        proxy = dict(mechanism)
        proxy.setdefault("book_id", row.get("book_id"))
        proxy.setdefault("title", row.get("title"))
        proxy.setdefault("chapters_covered", row.get("chapters_covered"))
        proxy.setdefault("adjacent_interfaces", row.get("adjacent_interfaces"))
        validate_single_mechanism(proxy, item_prefix, errors)
        identity = mechanism.get("mechanism_identity")
        if isinstance(identity, dict) and nonempty_string(identity.get("mechanism_id")):
            mechanism_id = identity["mechanism_id"]
            if mechanism_id in mechanism_ids:
                errors.append(f"{item_prefix}: duplicate mechanism_identity.mechanism_id={mechanism_id}")
            mechanism_ids.add(mechanism_id)


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
    required_dimensions = {"trigger_and_inputs", "roles_and_operations", "decisions_and_constraints", "escalation_and_outputs", "state_transition_and_repeatability", "variation_and_failure", "payoff_path_and_adjacent_interfaces"}
    dimensions = row.get("comparison_dimensions")
    if not isinstance(dimensions, dict):
        errors.append(f"{prefix}.comparison_dimensions must be an object")
    else:
        add_missing(errors, f"{prefix}.comparison_dimensions", dimensions, required_dimensions)
        text_fields(dimensions, f"{prefix}.comparison_dimensions", errors, required_dimensions)
    if not isinstance(row.get("similarities"), list):
        errors.append(f"{prefix}.similarities must be a list")
    if not string_list(row.get("surface_labels_excluded"), allow_empty=False):
        errors.append(f"{prefix}.surface_labels_excluded must be a non-empty list")
    for field in ("difference_boundary", "reason"):
        if not nonempty_string(row.get(field)):
            errors.append(f"{prefix}.{field} must be non-empty")
    if row.get("decision") not in NEIGHBOR_DECISIONS:
        errors.append(f"{prefix}.decision is not controlled")


def validate_cluster(row: dict[str, Any], prefix: str, errors: list[str]) -> None:
    required = {"member_record_ids", "cluster_level", "label", "shared_operation", "invariants", "variation_pattern", "failure_pattern", "boundary_conditions", "supporting_book_count", "nearest_neighbor_record_ids", "merge_decision"}
    add_missing(errors, prefix, row, required)
    book_ids = row.get("book_ids")
    if isinstance(book_ids, list):
        if len(set(book_ids)) < 2:
            errors.append(f"{prefix}: cluster requires at least two distinct book_ids")
        if row.get("supporting_book_count") != len(set(book_ids)):
            errors.append(f"{prefix}.supporting_book_count must match unique book_ids")
    elif not isinstance(row.get("supporting_book_count"), int):
        errors.append(f"{prefix}.supporting_book_count must be an integer")
    for field in ("member_record_ids", "invariants", "boundary_conditions", "nearest_neighbor_record_ids"):
        if not string_list(row.get(field), allow_empty=False):
            errors.append(f"{prefix}.{field} must be a non-empty list of strings")
    for field in ("cluster_level", "label", "shared_operation", "variation_pattern", "failure_pattern"):
        if not nonempty_string(row.get(field)):
            errors.append(f"{prefix}.{field} must be non-empty")
    if row.get("merge_decision") not in CLUSTER_DECISIONS:
        errors.append(f"{prefix}.merge_decision is not controlled")


def validate_qa(row: dict[str, Any], prefix: str, errors: list[str]) -> None:
    add_missing(errors, prefix, row, {"scope", "checks", "gaps", "disputes", "blocked_outputs"})
    if not nonempty_string(row.get("scope")):
        errors.append(f"{prefix}.scope must be non-empty")
    required_checks = {"instance_coverage", "identity_and_boundary", "trigger_and_inputs", "roles_and_operations", "decision_points", "constraints_and_escalation", "outputs_and_state_transition", "repeatability", "variation_and_failure", "payoff_path", "adjacent_boundary", "cross_book_gate"}
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
    parser = argparse.ArgumentParser(description="Validate novel-plot-mechanism-miner JSONL outputs.")
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
