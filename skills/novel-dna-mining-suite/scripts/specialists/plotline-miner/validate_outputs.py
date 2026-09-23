#!/usr/bin/env python3
"""Validate derived JSONL records from novel-plotline-miner.

The validator enforces deterministic structure and explicit lifecycle gates.
Semantic judgments such as whether an event truly starts a plotline remain in
clustering-and-qa.md and are intentionally not inferred here.
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
START_MODES = {"new", "reopened", "UNKNOWN"}
GOAL_STATES = {"open", "shifted", "paid", "failed", "abandoned", "UNKNOWN"}
PAYOFF_STATES = {"paid", "partial", "failed", "UNKNOWN"}
LIFECYCLE_STATES = {"not_started", "active", "paused", "redirected", "paid", "failed", "abandoned", "UNKNOWN"}
RELATION_TYPES = {"service", "obstacle", "change", "UNKNOWN"}
ENTRY_TYPES = {"goal", "resistance", "task", "choice", "child_line", "UNKNOWN"}
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
ADJACENT_KEYS = {
    "character_function",
    "arc_structure",
    "plot_mechanism",
    "opening",
    "cultivation",
    "worldbuilding",
    "golden_finger",
    "chapter_emotion",
}
INTERFACE_KEYS = {
    "goals",
    "choices",
    "resources",
    "risks",
    "cognition_information",
    "relationships",
    "action_window",
    "evidence_refs",
    "unknowns",
}
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


def validate_nested_refs(obj: Any, prefix: str, errors: list[str], *, required: bool = True) -> None:
    if not isinstance(obj, dict):
        errors.append(f"{prefix} must be an object")
        return
    if "evidence_refs" in obj and not ref_list(obj["evidence_refs"], allow_empty=not required):
        errors.append(f"{prefix}.evidence_refs must be a structured-ref list")
    if "unknowns" in obj and not string_list(obj["unknowns"]):
        errors.append(f"{prefix}.unknowns must be a list of strings")


def validate_line_identity(value: Any, prefix: str, errors: list[str]) -> str | None:
    if not isinstance(value, dict):
        errors.append(f"{prefix}.line_identity must be an object")
        return None
    required = {"line_id", "line_label", "line_scope", "line_purpose", "line_kind", "evidence_refs", "unknowns"}
    missing = sorted(required - set(value))
    if missing:
        errors.append(f"{prefix}.line_identity missing {', '.join(missing)}")
    for field in ("line_id", "line_label", "line_scope", "line_purpose", "line_kind"):
        if field in value and not nonempty_string(value[field]):
            errors.append(f"{prefix}.line_identity.{field} must be non-empty")
    validate_nested_refs(value, f"{prefix}.line_identity", errors)
    return value.get("line_id") if nonempty_string(value.get("line_id")) else None


def validate_trigger(value: Any, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix}.trigger must be an object")
        return
    required = {"trigger_id", "actual_start_event", "chapter_or_stage", "start_mode", "evidence_refs", "unknowns"}
    missing = sorted(required - set(value))
    if missing:
        errors.append(f"{prefix}.trigger missing {', '.join(missing)}")
    for field in ("trigger_id", "actual_start_event", "chapter_or_stage"):
        if field in value and not nonempty_string(value[field]):
            errors.append(f"{prefix}.trigger.{field} must be non-empty")
    if value.get("start_mode") not in START_MODES:
        errors.append(f"{prefix}.trigger.start_mode must be new/reopened/UNKNOWN")
    if "evidence_refs" in value and not ref_list(value["evidence_refs"]):
        errors.append(f"{prefix}.trigger.evidence_refs must be non-empty structured refs")
    if "unknowns" in value and not string_list(value["unknowns"]):
        errors.append(f"{prefix}.trigger.unknowns must be a list of strings")


def validate_goals(value: Any, prefix: str, errors: list[str]) -> set[str]:
    goal_ids: set[str] = set()
    if not isinstance(value, list):
        errors.append(f"{prefix}.goals must be a list")
        return goal_ids
    required = {"goal_id", "goal_statement", "subject", "phase_scope", "success_condition", "goal_status", "evidence_refs", "unknowns"}
    for index, item in enumerate(value):
        item_prefix = f"{prefix}.goals[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_prefix} must be an object")
            continue
        missing = sorted(required - set(item))
        if missing:
            errors.append(f"{item_prefix} missing {', '.join(missing)}")
        for field in ("goal_id", "goal_statement", "subject", "phase_scope", "success_condition"):
            if field in item and not nonempty_string(item[field]):
                errors.append(f"{item_prefix}.{field} must be non-empty")
        if item.get("goal_status") not in GOAL_STATES:
            errors.append(f"{item_prefix}.goal_status is not controlled")
        if not ref_list(item.get("evidence_refs")):
            errors.append(f"{item_prefix}.evidence_refs must be non-empty structured refs")
        if not string_list(item.get("unknowns")):
            errors.append(f"{item_prefix}.unknowns must be a list of strings")
        goal_id = item.get("goal_id")
        if nonempty_string(goal_id):
            if goal_id in goal_ids:
                errors.append(f"{item_prefix}: duplicate goal_id={goal_id}")
            goal_ids.add(goal_id)
    return goal_ids


def validate_resistances(value: Any, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append(f"{prefix}.resistances must be a list")
        return
    required = {"resistance_id", "resistance_type", "operation", "target_goal_id", "phase_scope", "observable_effect", "evidence_refs", "unknowns"}
    for index, item in enumerate(value):
        item_prefix = f"{prefix}.resistances[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_prefix} must be an object")
            continue
        missing = sorted(required - set(item))
        if missing:
            errors.append(f"{item_prefix} missing {', '.join(missing)}")
        for field in ("resistance_id", "resistance_type", "operation", "target_goal_id", "phase_scope", "observable_effect"):
            if field in item and not nonempty_string(item[field]):
                errors.append(f"{item_prefix}.{field} must be non-empty")
        if not ref_list(item.get("evidence_refs")):
            errors.append(f"{item_prefix}.evidence_refs must be non-empty structured refs")
        if not string_list(item.get("unknowns")):
            errors.append(f"{item_prefix}.unknowns must be a list of strings")


def validate_nodes(value: Any, prefix: str, errors: list[str]) -> set[str]:
    node_ids: set[str] = set()
    if not isinstance(value, list):
        errors.append(f"{prefix}.nodes must be a list")
        return node_ids
    required = {"node_id", "node_type", "before_state", "node_event", "after_state", "line_effect", "phase_scope", "evidence_refs", "unknowns"}
    for index, item in enumerate(value):
        item_prefix = f"{prefix}.nodes[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_prefix} must be an object")
            continue
        missing = sorted(required - set(item))
        if missing:
            errors.append(f"{item_prefix} missing {', '.join(missing)}")
        for field in ("node_id", "node_type", "before_state", "node_event", "after_state", "line_effect", "phase_scope"):
            if field in item and not nonempty_string(item[field]):
                errors.append(f"{item_prefix}.{field} must be non-empty")
        if not ref_list(item.get("evidence_refs")):
            errors.append(f"{item_prefix}.evidence_refs must be non-empty structured refs")
        if not string_list(item.get("unknowns")):
            errors.append(f"{item_prefix}.unknowns must be a list of strings")
        node_id = item.get("node_id")
        if nonempty_string(node_id):
            if node_id in node_ids:
                errors.append(f"{item_prefix}: duplicate node_id={node_id}")
            node_ids.add(node_id)
    return node_ids


def validate_choices(value: Any, prefix: str, errors: list[str]) -> set[str]:
    choice_ids: set[str] = set()
    if not isinstance(value, list):
        errors.append(f"{prefix}.choices must be a list")
        return choice_ids
    required = {"choice_id", "decision_maker", "available_paths", "chosen_action", "rejected_or_foregone_alternative", "choice_effect", "phase_scope", "evidence_refs", "unknowns"}
    for index, item in enumerate(value):
        item_prefix = f"{prefix}.choices[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_prefix} must be an object")
            continue
        missing = sorted(required - set(item))
        if missing:
            errors.append(f"{item_prefix} missing {', '.join(missing)}")
        for field in ("choice_id", "decision_maker", "chosen_action", "rejected_or_foregone_alternative", "choice_effect", "phase_scope"):
            if field in item and not nonempty_string(item[field]):
                errors.append(f"{item_prefix}.{field} must be non-empty or UNKNOWN")
        if not string_list(item.get("available_paths"), allow_empty=False):
            errors.append(f"{item_prefix}.available_paths must be a non-empty list of strings")
        if not ref_list(item.get("evidence_refs")):
            errors.append(f"{item_prefix}.evidence_refs must be non-empty structured refs")
        if not string_list(item.get("unknowns")):
            errors.append(f"{item_prefix}.unknowns must be a list of strings")
        choice_id = item.get("choice_id")
        if nonempty_string(choice_id):
            if choice_id in choice_ids:
                errors.append(f"{item_prefix}: duplicate choice_id={choice_id}")
            choice_ids.add(choice_id)
    return choice_ids


def validate_costs(value: Any, prefix: str, errors: list[str]) -> set[str]:
    cost_ids: set[str] = set()
    if not isinstance(value, list):
        errors.append(f"{prefix}.costs must be a list")
        return cost_ids
    required = {"cost_id", "caused_by_choice_or_node", "cost_type", "actual_cost", "downstream_constraint", "phase_scope", "evidence_refs", "unknowns"}
    for index, item in enumerate(value):
        item_prefix = f"{prefix}.costs[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_prefix} must be an object")
            continue
        missing = sorted(required - set(item))
        if missing:
            errors.append(f"{item_prefix} missing {', '.join(missing)}")
        for field in ("cost_id", "caused_by_choice_or_node", "cost_type", "actual_cost", "downstream_constraint", "phase_scope"):
            if field in item and not nonempty_string(item[field]):
                errors.append(f"{item_prefix}.{field} must be non-empty or UNKNOWN")
        if not ref_list(item.get("evidence_refs")):
            errors.append(f"{item_prefix}.evidence_refs must be non-empty structured refs")
        if not string_list(item.get("unknowns")):
            errors.append(f"{item_prefix}.unknowns must be a list of strings")
        cost_id = item.get("cost_id")
        if nonempty_string(cost_id):
            if cost_id in cost_ids:
                errors.append(f"{item_prefix}: duplicate cost_id={cost_id}")
            cost_ids.add(cost_id)
    return cost_ids


def validate_payoffs(value: Any, prefix: str, errors: list[str]) -> tuple[set[str], bool]:
    payoff_ids: set[str] = set()
    has_valid_line_payoff = False
    if not isinstance(value, list):
        errors.append(f"{prefix}.payoffs must be a list")
        return payoff_ids, has_valid_line_payoff
    required = {"payoff_id", "prior_goal_ids", "prior_promise_or_unresolved_question", "payoff_result", "payoff_state", "is_line_payoff", "phase_scope", "evidence_refs", "unknowns"}
    for index, item in enumerate(value):
        item_prefix = f"{prefix}.payoffs[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_prefix} must be an object")
            continue
        missing = sorted(required - set(item))
        if missing:
            errors.append(f"{item_prefix} missing {', '.join(missing)}")
        if not nonempty_string(item.get("payoff_id")):
            errors.append(f"{item_prefix}.payoff_id must be non-empty")
        if not string_list(item.get("prior_goal_ids")):
            errors.append(f"{item_prefix}.prior_goal_ids must be a list of strings")
        if not nonempty_string(item.get("prior_promise_or_unresolved_question")):
            errors.append(f"{item_prefix}.prior_promise_or_unresolved_question must be non-empty or UNKNOWN")
        if not nonempty_string(item.get("payoff_result")):
            errors.append(f"{item_prefix}.payoff_result must be non-empty")
        if item.get("payoff_state") not in PAYOFF_STATES:
            errors.append(f"{item_prefix}.payoff_state is not controlled")
        if not isinstance(item.get("is_line_payoff"), bool):
            errors.append(f"{item_prefix}.is_line_payoff must be boolean")
        if not nonempty_string(item.get("phase_scope")):
            errors.append(f"{item_prefix}.phase_scope must be non-empty")
        if not ref_list(item.get("evidence_refs")):
            errors.append(f"{item_prefix}.evidence_refs must be non-empty structured refs")
        if not string_list(item.get("unknowns")):
            errors.append(f"{item_prefix}.unknowns must be a list of strings")
        prior_goal_ids = item.get("prior_goal_ids") if isinstance(item.get("prior_goal_ids"), list) else []
        prior_question = item.get("prior_promise_or_unresolved_question")
        has_prior = bool(prior_goal_ids) or (nonempty_string(prior_question) and prior_question != "UNKNOWN")
        if item.get("is_line_payoff") is True and not has_prior:
            errors.append(f"{item_prefix}: is_line_payoff=true requires prior_goal_ids or prior promise/question")
        if item.get("is_line_payoff") is True and has_prior and nonempty_string(item.get("payoff_result")):
            has_valid_line_payoff = True
        payoff_id = item.get("payoff_id")
        if nonempty_string(payoff_id):
            if payoff_id in payoff_ids:
                errors.append(f"{item_prefix}: duplicate payoff_id={payoff_id}")
            payoff_ids.add(payoff_id)
    return payoff_ids, has_valid_line_payoff


def validate_state_changes(value: Any, prefix: str, errors: list[str]) -> set[str]:
    state_ids: set[str] = set()
    if not isinstance(value, list):
        errors.append(f"{prefix}.state_changes must be a list")
        return state_ids
    required = {"state_change_id", "caused_by_payoff_or_failure", "changed_domains", "before_state", "after_state", "line_effect", "evidence_refs", "unknowns"}
    for index, item in enumerate(value):
        item_prefix = f"{prefix}.state_changes[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_prefix} must be an object")
            continue
        missing = sorted(required - set(item))
        if missing:
            errors.append(f"{item_prefix} missing {', '.join(missing)}")
        if not nonempty_string(item.get("state_change_id")):
            errors.append(f"{item_prefix}.state_change_id must be non-empty")
        if not nonempty_string(item.get("caused_by_payoff_or_failure")):
            errors.append(f"{item_prefix}.caused_by_payoff_or_failure must be non-empty")
        if not string_list(item.get("changed_domains"), allow_empty=False):
            errors.append(f"{item_prefix}.changed_domains must be a non-empty list of strings")
        for field in ("before_state", "after_state", "line_effect"):
            if field in item and not nonempty_string(item[field]):
                errors.append(f"{item_prefix}.{field} must be non-empty")
        if not ref_list(item.get("evidence_refs")):
            errors.append(f"{item_prefix}.evidence_refs must be non-empty structured refs")
        if not string_list(item.get("unknowns")):
            errors.append(f"{item_prefix}.unknowns must be a list of strings")
        state_id = item.get("state_change_id")
        if nonempty_string(state_id):
            if state_id in state_ids:
                errors.append(f"{item_prefix}: duplicate state_change_id={state_id}")
            state_ids.add(state_id)
    return state_ids


def validate_next_entries(value: Any, prefix: str, errors: list[str], state_ids: set[str]) -> None:
    if not isinstance(value, list):
        errors.append(f"{prefix}.next_entries must be a list")
        return
    required = {"next_entry_id", "source_state_change_id", "entry_type", "opened_goal_or_task", "opened_resistance", "opened_choice", "target_line_id", "evidence_refs", "unknowns"}
    entry_ids: set[str] = set()
    for index, item in enumerate(value):
        item_prefix = f"{prefix}.next_entries[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_prefix} must be an object")
            continue
        missing = sorted(required - set(item))
        if missing:
            errors.append(f"{item_prefix} missing {', '.join(missing)}")
        for field in ("next_entry_id", "source_state_change_id", "opened_goal_or_task", "opened_resistance", "opened_choice", "target_line_id"):
            if field in item and not nonempty_string(item[field]):
                errors.append(f"{item_prefix}.{field} must be non-empty or UNKNOWN")
        if item.get("entry_type") not in ENTRY_TYPES:
            errors.append(f"{item_prefix}.entry_type is not controlled")
        source_id = item.get("source_state_change_id")
        if nonempty_string(source_id) and source_id != "UNKNOWN" and source_id not in state_ids:
            errors.append(f"{item_prefix}.source_state_change_id must reference a local state_change")
        if not ref_list(item.get("evidence_refs")):
            errors.append(f"{item_prefix}.evidence_refs must be non-empty structured refs")
        if not string_list(item.get("unknowns")):
            errors.append(f"{item_prefix}.unknowns must be a list of strings")
        entry_id = item.get("next_entry_id")
        if nonempty_string(entry_id):
            if entry_id in entry_ids:
                errors.append(f"{item_prefix}: duplicate next_entry_id={entry_id}")
            entry_ids.add(entry_id)


def validate_lifecycle(value: Any, prefix: str, errors: list[str], has_valid_line_payoff: bool) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix}.line_lifecycle must be an object")
        return
    required = {"current_state", "state_history", "unknowns"}
    missing = sorted(required - set(value))
    if missing:
        errors.append(f"{prefix}.line_lifecycle missing {', '.join(missing)}")
    if value.get("current_state") not in LIFECYCLE_STATES:
        errors.append(f"{prefix}.line_lifecycle.current_state is not controlled")
    history = value.get("state_history")
    if not isinstance(history, list):
        errors.append(f"{prefix}.line_lifecycle.state_history must be a list")
    else:
        for index, item in enumerate(history):
            item_prefix = f"{prefix}.line_lifecycle.state_history[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{item_prefix} must be an object")
                continue
            required_history = {"state", "trigger_or_reason", "phase_scope", "evidence_refs", "unknowns"}
            missing_history = sorted(required_history - set(item))
            if missing_history:
                errors.append(f"{item_prefix} missing {', '.join(missing_history)}")
            if item.get("state") not in LIFECYCLE_STATES:
                errors.append(f"{item_prefix}.state is not controlled")
            for field in ("trigger_or_reason", "phase_scope"):
                if field in item and not nonempty_string(item[field]):
                    errors.append(f"{item_prefix}.{field} must be non-empty")
            if not ref_list(item.get("evidence_refs")):
                errors.append(f"{item_prefix}.evidence_refs must be non-empty structured refs")
            if not string_list(item.get("unknowns")):
                errors.append(f"{item_prefix}.unknowns must be a list of strings")
    if not string_list(value.get("unknowns")):
        errors.append(f"{prefix}.line_lifecycle.unknowns must be a list of strings")
    if value.get("current_state") == "paid" and not has_valid_line_payoff:
        errors.append(f"{prefix}: lifecycle=paid requires a valid line payoff")
    if value.get("current_state") in {"failed", "abandoned"} and isinstance(history, list):
        terminal_state = value.get("current_state")
        if not any(isinstance(item, dict) and item.get("state") == terminal_state for item in history):
            errors.append(
                f"{prefix}: lifecycle={terminal_state} requires matching structural evidence in state_history"
            )


def validate_parent_child_relations(value: Any, prefix: str, errors: list[str], line_ids: set[str]) -> list[tuple[str, str]]:
    edges: list[tuple[str, str]] = []
    if not isinstance(value, list):
        errors.append(f"{prefix}.parent_child_relations must be a list")
        return edges
    required = {"parent_line_id", "child_line_id", "relation_type", "how_child_affects_parent", "child_completion_effect", "pause_relationship", "evidence_refs", "unknowns"}
    for index, item in enumerate(value):
        item_prefix = f"{prefix}.parent_child_relations[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_prefix} must be an object")
            continue
        missing = sorted(required - set(item))
        if missing:
            errors.append(f"{item_prefix} missing {', '.join(missing)}")
        for field in ("parent_line_id", "child_line_id", "how_child_affects_parent", "child_completion_effect", "pause_relationship"):
            if field in item and not nonempty_string(item[field]):
                errors.append(f"{item_prefix}.{field} must be non-empty or UNKNOWN")
        if item.get("relation_type") not in RELATION_TYPES:
            errors.append(f"{item_prefix}.relation_type is not controlled")
        parent = item.get("parent_line_id")
        child = item.get("child_line_id")
        if nonempty_string(parent) and nonempty_string(child):
            if parent == child:
                errors.append(f"{item_prefix}: parent_line_id and child_line_id cannot be equal")
            if line_ids and parent not in line_ids:
                errors.append(f"{item_prefix}.parent_line_id must reference a local line")
            if line_ids and child not in line_ids:
                errors.append(f"{item_prefix}.child_line_id must reference a local line")
            edges.append((parent, child))
        if not ref_list(item.get("evidence_refs")):
            errors.append(f"{item_prefix}.evidence_refs must be non-empty structured refs")
        if not string_list(item.get("unknowns")):
            errors.append(f"{item_prefix}.unknowns must be a list of strings")
    return edges


def has_graph_cycle(edges: list[tuple[str, str]]) -> bool:
    graph: dict[str, list[str]] = {}
    for parent, child in edges:
        graph.setdefault(parent, []).append(child)
        graph.setdefault(child, [])
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        if any(visit(child) for child in graph.get(node, [])):
            return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in graph)


def validate_protagonist_interface(value: Any, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix}.protagonist_interface must be an object")
        return
    required = INTERFACE_KEYS
    missing = sorted(required - set(value))
    if missing:
        errors.append(f"{prefix}.protagonist_interface missing {', '.join(missing)}")
    extra = sorted(set(value) - INTERFACE_KEYS)
    if extra:
        errors.append(f"{prefix}.protagonist_interface has unsupported fields: {', '.join(extra)}")
    for field in INTERFACE_KEYS - {"evidence_refs", "unknowns"}:
        if field in value and not nonempty_string(value[field]):
            errors.append(f"{prefix}.protagonist_interface.{field} must be non-empty or UNKNOWN")
    if not ref_list(value.get("evidence_refs")):
        errors.append(f"{prefix}.protagonist_interface.evidence_refs must be non-empty structured refs")
    if not string_list(value.get("unknowns")):
        errors.append(f"{prefix}.protagonist_interface.unknowns must be a list of strings")


def validate_adjacent_interfaces(value: Any, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix}.adjacent_interfaces must be an object")
        return
    missing = sorted(ADJACENT_KEYS - set(value))
    extra = sorted(set(value) - ADJACENT_KEYS)
    if missing:
        errors.append(f"{prefix}.adjacent_interfaces missing {', '.join(missing)}")
    if extra:
        errors.append(f"{prefix}.adjacent_interfaces has unsupported keys {', '.join(extra)}")
    allowed_reference_keys = {"record_id", "interface_type", "evidence_refs", "note", "unknowns"}
    for key in ADJACENT_KEYS & set(value):
        entries = value[key]
        if not isinstance(entries, list):
            errors.append(f"{prefix}.adjacent_interfaces.{key} must be a list")
            continue
        for index, entry in enumerate(entries):
            item_prefix = f"{prefix}.adjacent_interfaces.{key}[{index}]"
            if isinstance(entry, str):
                if not nonempty_string(entry):
                    errors.append(f"{item_prefix} must be a non-empty reference string")
                continue
            if not isinstance(entry, dict):
                errors.append(f"{item_prefix} must be a reference string or object")
                continue
            unsupported = sorted(set(entry) - allowed_reference_keys)
            if unsupported:
                errors.append(f"{item_prefix} contains non-reference fields: {', '.join(unsupported)}")
            if "record_id" in entry and not nonempty_string(entry["record_id"]):
                errors.append(f"{item_prefix}.record_id must be non-empty")
            if "evidence_refs" not in entry or not ref_list(entry.get("evidence_refs")):
                errors.append(f"{item_prefix}.evidence_refs must be non-empty structured refs")
            if "unknowns" in entry and not string_list(entry["unknowns"]):
                errors.append(f"{item_prefix}.unknowns must be a list of strings")


def validate_line(line_record: Any, prefix: str, errors: list[str]) -> tuple[str | None, list[tuple[str, str]]]:
    if not isinstance(line_record, dict):
        errors.append(f"{prefix} must be an object")
        return None, []
    required = {
        "line_identity",
        "trigger",
        "goals",
        "resistances",
        "nodes",
        "choices",
        "costs",
        "payoffs",
        "state_changes",
        "next_entries",
        "line_lifecycle",
        "parent_child_relations",
        "protagonist_interface",
        "adjacent_interfaces",
        "evidence_refs",
        "unknowns",
    }
    missing = sorted(required - set(line_record))
    if missing:
        errors.append(f"{prefix} missing {', '.join(missing)}")

    line_id = validate_line_identity(line_record.get("line_identity"), prefix, errors)
    validate_trigger(line_record.get("trigger"), prefix, errors)
    goal_ids = validate_goals(line_record.get("goals"), prefix, errors)
    validate_resistances(line_record.get("resistances"), prefix, errors)
    validate_nodes(line_record.get("nodes"), prefix, errors)
    validate_choices(line_record.get("choices"), prefix, errors)
    validate_costs(line_record.get("costs"), prefix, errors)
    _, has_valid_line_payoff = validate_payoffs(line_record.get("payoffs"), prefix, errors)
    payoffs = line_record.get("payoffs")
    if isinstance(payoffs, list):
        for index, payoff in enumerate(payoffs):
            if not isinstance(payoff, dict):
                continue
            prior_goal_ids = payoff.get("prior_goal_ids")
            if isinstance(prior_goal_ids, list):
                for goal_id in prior_goal_ids:
                    if nonempty_string(goal_id) and goal_id != "UNKNOWN" and goal_id not in goal_ids:
                        errors.append(
                            f"{prefix}.payoffs[{index}].prior_goal_ids must reference local goals"
                        )
    state_ids = validate_state_changes(line_record.get("state_changes"), prefix, errors)
    validate_next_entries(line_record.get("next_entries"), prefix, errors, state_ids)
    validate_lifecycle(line_record.get("line_lifecycle"), prefix, errors, has_valid_line_payoff)
    validate_protagonist_interface(line_record.get("protagonist_interface"), prefix, errors)
    validate_adjacent_interfaces(line_record.get("adjacent_interfaces"), prefix, errors)
    if not ref_list(line_record.get("evidence_refs")):
        errors.append(f"{prefix}.evidence_refs must be non-empty structured refs")
    if not string_list(line_record.get("unknowns")):
        errors.append(f"{prefix}.unknowns must be a list of strings")
    if "goals" in line_record and isinstance(line_record.get("resistances"), list):
        for index, resistance in enumerate(line_record["resistances"]):
            if isinstance(resistance, dict):
                target = resistance.get("target_goal_id")
                if nonempty_string(target) and target != "UNKNOWN" and target not in goal_ids:
                    errors.append(f"{prefix}.resistances[{index}].target_goal_id must reference a local goal")
    return line_id, []


def validate_per_book(row: dict[str, Any], path: Path, line: int, errors: list[str]) -> None:
    required = {"book_id", "title", "chapters_covered", "plotlines", "emotion_overlay_links", "source_numbering_notes"}
    add_missing(errors, path, line, row, required)
    for field in ("title", "chapters_covered"):
        if field in row and not nonempty_string(row[field]):
            errors.append(f"{path}:{line}: {field} must be non-empty")
    plotlines = row.get("plotlines")
    if not isinstance(plotlines, list):
        errors.append(f"{path}:{line}: plotlines must be a list")
        return
    if not plotlines:
        errors.append(f"{path}:{line}: per_book requires at least one plotline; use record_type=gap when evidence is insufficient")
        return
    if not isinstance(row.get("emotion_overlay_links"), list):
        errors.append(f"{path}:{line}: emotion_overlay_links must be a list")
    if not isinstance(row.get("source_numbering_notes"), list):
        errors.append(f"{path}:{line}: source_numbering_notes must be a list")

    line_ids: set[str] = set()
    all_edges: list[tuple[str, str]] = []
    for index, line_record in enumerate(plotlines):
        prefix = f"{path}:{line}: plotlines[{index}]"
        line_id, _ = validate_line(line_record, prefix, errors)
        if line_id is not None:
            if line_id in line_ids:
                errors.append(f"{prefix}: duplicate line_id={line_id}")
            line_ids.add(line_id)

    for index, line_record in enumerate(plotlines):
        if isinstance(line_record, dict):
            relations = line_record.get("parent_child_relations")
            if isinstance(relations, list):
                relation_prefix = f"{path}:{line}: plotlines[{index}]"
                all_edges.extend(validate_parent_child_relations(relations, relation_prefix, errors, line_ids))
    if has_graph_cycle(all_edges):
        errors.append(f"{path}:{line}: parent_child_relations contains a cycle")


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
    required = {"comparison_ids", "comparison_dimensions", "similarities", "difference_boundary", "surface_labels_excluded", "decision", "reason"}
    add_missing(errors, path, line, row, required)
    book_ids = row.get("book_ids")
    if isinstance(book_ids, list) and len(set(book_ids)) < 2:
        errors.append(f"{path}:{line}: nearest_neighbor requires at least two distinct book_ids")
    if not string_list(row.get("comparison_ids"), allow_empty=False):
        errors.append(f"{path}:{line}: comparison_ids must be a non-empty list of strings")
    dimensions = row.get("comparison_dimensions")
    required_dimensions = {
        "trigger_and_goal_formation",
        "resistance_maintenance",
        "node_choice_cost",
        "payoff_state_next_entry",
        "parent_child_structure",
        "lifecycle_outcomes",
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
    required = {"member_record_ids", "cluster_level", "label", "shared_operation", "payoff_state_entry_pattern", "parent_child_pattern", "boundary_conditions", "supporting_book_count", "nearest_neighbor_record_ids", "merge_decision"}
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
    for field in ("cluster_level", "label", "shared_operation", "payoff_state_entry_pattern", "parent_child_pattern"):
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
        "nine_stage_chain",
        "trigger_goal_resistance",
        "node_state_change",
        "choice_and_cost",
        "payoff_boundary",
        "state_change_next_entry",
        "parent_child_lines",
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
    parser = argparse.ArgumentParser(description="Validate novel-plotline-miner JSONL outputs.")
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
