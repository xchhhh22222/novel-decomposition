#!/usr/bin/env python3
"""Validate derived JSONL records from novel-cultivation-system-miner.

The validator enforces structural contracts and explicit cross-field relations.
Ambiguous literary judgments remain in clustering-and-qa.md.
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
SKILL_STATES = {"UNKNOWN", "obtained", "learning", "practiced", "mastered", "proficient", "evolved"}
EFFECT_MODES = {
    "temporary_boost",
    "consumable",
    "long_term_conversion",
    "permanent_self_growth",
    "access_only",
    "UNKNOWN",
}
GROWTH_EFFECT_TYPES = {"access_only", "changes_condition", "formal_growth", "UNKNOWN"}
REALM_CHANGE_TYPES = {"formal_realm_change", "UNKNOWN"}
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
SYSTEM_TYPES = {"body", "energy", "spirit", "bloodline", "summoning", "artifact", "hybrid", "other", "UNKNOWN"}
SYSTEM_RELATION_TYPES = {"parallel", "exclusive", "complementary", "convertible", "counter", "dependency", "hybrid", "UNKNOWN"}
TECHNIQUE_CATEGORIES = {"cultivation_manual", "combat_art", "movement", "secret_art", "spirit_art", "body_art", "support", "forbidden", "other", "UNKNOWN"}
ARTIFACT_CATEGORIES = {"weapon", "armor", "artifact", "spirit_item", "technology", "space_item", "support_item", "special_item", "other", "UNKNOWN"}
RESOURCE_KINDS = {"medicine", "material", "currency", "points", "core", "consumable", "training_resource", "other", "UNKNOWN"}
V2_AFFECTED_LAYERS = {"system", "realm", "build", "technique", "artifact", "combat_power", "resource", "permission"}


def validate_v2_realm_system(realm_system: Any, prefix: str, errors: list[str]) -> None:
    if not isinstance(realm_system, dict):
        errors.append(f"{prefix}.realm_system must be an object")
        return
    required = {"realm_order", "transition_events", "break_conditions", "realm_limits", "unknowns"}
    missing = sorted(required - set(realm_system))
    if missing:
        errors.append(f"{prefix}.realm_system missing fields: {', '.join(missing)}")
    for field in ("realm_order", "transition_events", "break_conditions", "realm_limits"):
        if field in realm_system and not isinstance(realm_system.get(field), list):
            errors.append(f"{prefix}.realm_system.{field} must be a list")
    if "unknowns" in realm_system and not string_list(realm_system.get("unknowns")):
        errors.append(f"{prefix}.realm_system.unknowns must be a list of strings")

    realm_ids: set[str] = set()
    for index, realm in enumerate(realm_system.get("realm_order", []) if isinstance(realm_system.get("realm_order"), list) else []):
        item_prefix = f"{prefix}.realm_system.realm_order[{index}]"
        if not isinstance(realm, dict):
            errors.append(f"{item_prefix} must be an object")
            continue
        for field in ("realm_id", "name_in_book", "order", "stage_difference", "direct_evidence_refs"):
            if field not in realm:
                errors.append(f"{item_prefix} missing {field}")
        realm_id = realm.get("realm_id")
        if not nonempty_string(realm_id):
            errors.append(f"{item_prefix}.realm_id must be non-empty")
        elif realm_id in realm_ids:
            errors.append(f"{item_prefix}: duplicate realm_id={realm_id}")
        else:
            realm_ids.add(realm_id)
        if not nonempty_string(realm.get("name_in_book")):
            errors.append(f"{item_prefix}.name_in_book must be non-empty")
        if not isinstance(realm.get("order"), int):
            errors.append(f"{item_prefix}.order must be an integer")
        if not nonempty_string(realm.get("stage_difference")):
            errors.append(f"{item_prefix}.stage_difference must be non-empty or UNKNOWN")
        if not ref_list(realm.get("direct_evidence_refs"), allow_empty=True):
            errors.append(f"{item_prefix}.direct_evidence_refs has invalid structure")

    for index, event in enumerate(realm_system.get("transition_events", []) if isinstance(realm_system.get("transition_events"), list) else []):
        item_prefix = f"{prefix}.realm_system.transition_events[{index}]"
        if not isinstance(event, dict):
            errors.append(f"{item_prefix} must be an object")
            continue
        required_event = {"event_id", "person_id", "before", "trigger_or_condition", "after", "change_type", "direct_evidence_refs", "costs_or_risks", "unknowns"}
        missing = sorted(required_event - set(event))
        if missing:
            errors.append(f"{item_prefix} missing fields: {', '.join(missing)}")
        if event.get("change_type") not in REALM_CHANGE_TYPES:
            errors.append(f"{item_prefix}.change_type must be formal_realm_change/UNKNOWN")
        if not nonempty_string(event.get("before")):
            errors.append(f"{item_prefix}.before must be non-empty or UNKNOWN")
        if not nonempty_string(event.get("trigger_or_condition")):
            errors.append(f"{item_prefix}.trigger_or_condition must be non-empty")
        refs = event.get("direct_evidence_refs")
        if not ref_list(refs, allow_empty=event.get("change_type") != "formal_realm_change"):
            errors.append(f"{item_prefix}.direct_evidence_refs has invalid structure")
        if event.get("change_type") == "formal_realm_change":
            if not nonempty_string(event.get("after")) or event.get("after") == "UNKNOWN":
                errors.append(f"{item_prefix}.after must be determined for formal_realm_change")
            if not ref_list(refs):
                errors.append(f"{item_prefix}: formal realm change requires direct_evidence_refs")
        elif nonempty_string(event.get("after")) and event.get("after") != "UNKNOWN":
            errors.append(f"{item_prefix}: UNKNOWN realm change cannot declare a determined after realm")
        if not string_list(event.get("costs_or_risks")):
            errors.append(f"{item_prefix}.costs_or_risks must be a list of strings")
        if not string_list(event.get("unknowns")):
            errors.append(f"{item_prefix}.unknowns must be a list of strings")


def validate_v2_per_book(row: dict[str, Any], path: Path, line: int, errors: list[str]) -> None:
    required = {
        "book_id", "title", "chapters_covered", "shared_foundations", "cultivation_systems",
        "system_relations", "techniques", "artifacts", "resource_assets", "protagonist_build",
        "golden_finger_interfaces", "actual_combat_power", "skill_proficiency", "identity_permissions",
        "milestones", "emotion_overlay_links", "growth_fatigue_risks", "source_numbering_notes",
    }
    add_missing(errors, path, line, row, required)
    for field in ("title", "chapters_covered"):
        if field in row and not nonempty_string(row.get(field)):
            errors.append(f"{path}:{line}: {field} must be non-empty")

    if not isinstance(row.get("shared_foundations"), dict):
        errors.append(f"{path}:{line}: shared_foundations must be an object")

    list_fields = (
        "cultivation_systems", "system_relations", "techniques", "artifacts", "resource_assets",
        "golden_finger_interfaces", "emotion_overlay_links", "growth_fatigue_risks", "source_numbering_notes",
    )
    for field in list_fields:
        if field in row and not isinstance(row.get(field), list):
            errors.append(f"{path}:{line}: {field} must be a list")

    systems = row.get("cultivation_systems", [])
    if isinstance(systems, list) and not systems:
        errors.append(f"{path}:{line}: schema_version=2 per_book requires at least one evidenced cultivation_system; use gap otherwise")

    system_ids: set[str] = set()
    for index, system in enumerate(systems if isinstance(systems, list) else []):
        prefix = f"{path}:{line}: cultivation_systems[{index}]"
        if not isinstance(system, dict):
            errors.append(f"{prefix} must be an object")
            continue
        required_system = {
            "system_id", "name_in_book", "system_type", "population_scope", "entry_condition",
            "energy_or_power_source", "training_method", "growth_loop", "realm_system",
            "resource_requirements", "validation_methods", "combat_expression", "strengths",
            "hard_limits", "evidence_refs", "unknowns",
        }
        missing = sorted(required_system - set(system))
        if missing:
            errors.append(f"{prefix} missing fields: {', '.join(missing)}")
        system_id = system.get("system_id")
        if not nonempty_string(system_id):
            errors.append(f"{prefix}.system_id must be non-empty")
        elif system_id in system_ids:
            errors.append(f"{prefix}: duplicate system_id={system_id}")
        else:
            system_ids.add(system_id)
        if system.get("system_type") not in SYSTEM_TYPES:
            errors.append(f"{prefix}.system_type is not controlled")
        for field in ("resource_requirements", "validation_methods", "strengths", "hard_limits"):
            if not string_list(system.get(field)):
                errors.append(f"{prefix}.{field} must be a list of strings")
        if not ref_list(system.get("evidence_refs")):
            errors.append(f"{prefix}.evidence_refs must be non-empty")
        if not string_list(system.get("unknowns")):
            errors.append(f"{prefix}.unknowns must be a list of strings")
        validate_v2_realm_system(system.get("realm_system"), prefix, errors)

    relations = row.get("system_relations", [])
    if isinstance(relations, list) and len(system_ids) < 2 and relations:
        errors.append(f"{path}:{line}: system_relations must be empty when fewer than two systems exist")
    for index, relation in enumerate(relations if isinstance(relations, list) else []):
        prefix = f"{path}:{line}: system_relations[{index}]"
        if not isinstance(relation, dict):
            errors.append(f"{prefix} must be an object")
            continue
        required_relation = {
            "relation_id", "system_a", "system_b", "relation_type", "can_dual_cultivate",
            "shared_resources", "exclusive_or_competing_resources", "conversion_rule",
            "power_mapping_or_validation", "synergy_or_conflict", "evidence_refs", "unknowns",
        }
        missing = sorted(required_relation - set(relation))
        if missing:
            errors.append(f"{prefix} missing fields: {', '.join(missing)}")
        if relation.get("system_a") not in system_ids or relation.get("system_b") not in system_ids:
            errors.append(f"{prefix}: relation must reference local system_ids")
        if relation.get("system_a") == relation.get("system_b"):
            errors.append(f"{prefix}: system_a and system_b must differ")
        if relation.get("relation_type") not in SYSTEM_RELATION_TYPES:
            errors.append(f"{prefix}.relation_type is not controlled")
        if relation.get("can_dual_cultivate") not in {True, False, "UNKNOWN"}:
            errors.append(f"{prefix}.can_dual_cultivate must be true/false/UNKNOWN")
        for field in ("shared_resources", "exclusive_or_competing_resources"):
            if not string_list(relation.get(field)):
                errors.append(f"{prefix}.{field} must be a list of strings")
        if not ref_list(relation.get("evidence_refs")):
            errors.append(f"{prefix}.evidence_refs must be non-empty")
        if not string_list(relation.get("unknowns")):
            errors.append(f"{prefix}.unknowns must be a list of strings")

    def validate_components(field: str, id_key: str, category_key: str, allowed: set[str]) -> set[str]:
        ids: set[str] = set()
        items = row.get(field, [])
        for index, item in enumerate(items if isinstance(items, list) else []):
            prefix = f"{path}:{line}: {field}[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{prefix} must be an object")
                continue
            item_id = item.get(id_key)
            if not nonempty_string(item_id):
                errors.append(f"{prefix}.{id_key} must be non-empty")
            elif item_id in ids:
                errors.append(f"{prefix}: duplicate {id_key}={item_id}")
            else:
                ids.add(item_id)
            if item.get(category_key) not in allowed:
                errors.append(f"{prefix}.{category_key} is not controlled")
            compatible = item.get("compatible_system_ids")
            if not string_list(compatible):
                errors.append(f"{prefix}.compatible_system_ids must be a list of strings")
            else:
                foreign = [sid for sid in compatible if sid not in system_ids]
                if foreign:
                    errors.append(f"{prefix}: unknown compatible_system_ids={', '.join(foreign)}")
            if not ref_list(item.get("evidence_refs")):
                errors.append(f"{prefix}.evidence_refs must be non-empty")
            if not string_list(item.get("unknowns")):
                errors.append(f"{prefix}.unknowns must be a list of strings")
        return ids

    technique_ids = validate_components("techniques", "technique_id", "category", TECHNIQUE_CATEGORIES)
    artifact_ids = validate_components("artifacts", "artifact_id", "category", ARTIFACT_CATEGORIES)
    validate_components("resource_assets", "resource_id", "resource_kind", RESOURCE_KINDS)

    for index, resource in enumerate(row.get("resource_assets", []) if isinstance(row.get("resource_assets"), list) else []):
        if isinstance(resource, dict) and not isinstance(resource.get("permanent_self_change_proven"), bool):
            errors.append(f"{path}:{line}: resource_assets[{index}].permanent_self_change_proven must be boolean")

    build = row.get("protagonist_build")
    if not isinstance(build, dict):
        errors.append(f"{path}:{line}: protagonist_build must be an object")
    else:
        for sid in build.get("system_ids", []) if isinstance(build.get("system_ids"), list) else []:
            if sid not in system_ids:
                errors.append(f"{path}:{line}: protagonist_build references unknown system_id={sid}")
        for tid in build.get("technique_ids", []) if isinstance(build.get("technique_ids"), list) else []:
            if tid not in technique_ids:
                errors.append(f"{path}:{line}: protagonist_build references unknown technique_id={tid}")
        for aid in build.get("artifact_ids", []) if isinstance(build.get("artifact_ids"), list) else []:
            if aid not in artifact_ids:
                errors.append(f"{path}:{line}: protagonist_build references unknown artifact_id={aid}")

    interfaces = row.get("golden_finger_interfaces")
    if isinstance(interfaces, list):
        for index, item in enumerate(interfaces):
            prefix = f"{path}:{line}: golden_finger_interfaces[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{prefix} must be an object")
                continue
            if item.get("affected_layer") not in V2_AFFECTED_LAYERS:
                errors.append(f"{prefix}.affected_layer is not controlled")
            if not ref_list(item.get("evidence_refs")):
                errors.append(f"{prefix}.evidence_refs must be non-empty")
            if not string_list(item.get("unknowns")):
                errors.append(f"{prefix}.unknowns must be a list of strings")

    power = row.get("actual_combat_power")
    if not isinstance(power, dict):
        errors.append(f"{path}:{line}: actual_combat_power must be an object")
    else:
        validate_actual_power(power, path, line, errors)
        for index, event in enumerate(power.get("assessment_events", []) if isinstance(power.get("assessment_events"), list) else []):
            if isinstance(event, dict):
                sid = event.get("system_id")
                if sid is not None and sid not in system_ids:
                    errors.append(f"{path}:{line}: actual_combat_power.assessment_events[{index}] references unknown system_id={sid}")

    proficiency = row.get("skill_proficiency")
    if not isinstance(proficiency, dict):
        errors.append(f"{path}:{line}: skill_proficiency must be an object")
    else:
        events = proficiency.get("skill_events")
        if not isinstance(events, list):
            errors.append(f"{path}:{line}: skill_proficiency.skill_events must be a list")
        else:
            for index, event in enumerate(events):
                prefix = f"{path}:{line}: skill_proficiency.skill_events[{index}]"
                if not isinstance(event, dict):
                    errors.append(f"{prefix} must be an object")
                    continue
                if event.get("technique_id") not in technique_ids:
                    errors.append(f"{prefix}: technique_id must reference techniques")
                if not isinstance(event.get("state_transitions"), list):
                    errors.append(f"{prefix}.state_transitions must be a list")
                if not ref_list(event.get("evidence_refs")):
                    errors.append(f"{prefix}.evidence_refs must be non-empty")
                if not string_list(event.get("unknowns")):
                    errors.append(f"{prefix}.unknowns must be a list of strings")
                for tindex, transition in enumerate(event.get("state_transitions", []) if isinstance(event.get("state_transitions"), list) else []):
                    tprefix = f"{prefix}.state_transitions[{tindex}]"
                    if not isinstance(transition, dict):
                        errors.append(f"{tprefix} must be an object")
                        continue
                    if transition.get("from_state") not in SKILL_STATES or transition.get("to_state") not in SKILL_STATES:
                        errors.append(f"{tprefix}: skill state is not controlled")
                    if transition.get("to_state") in {"mastered", "proficient", "evolved"} and not nonempty_string(transition.get("visible_validation")):
                        errors.append(f"{tprefix}: advanced state requires visible_validation")
                    if not ref_list(transition.get("evidence_refs")):
                        errors.append(f"{tprefix}.evidence_refs must be non-empty")
                    if not string_list(transition.get("unknowns")):
                        errors.append(f"{tprefix}.unknowns must be a list of strings")

    validate_permissions(row.get("identity_permissions"), path, line, errors)

    milestones = row.get("milestones")
    if not isinstance(milestones, dict):
        errors.append(f"{path}:{line}: milestones must be an object")
    else:
        for field in ("first_system_display", "first_direct_realm_change", "first_technique_validation", "first_artifact_validation", "first_cross_system_relation_validation"):
            if field not in milestones or not isinstance(milestones.get(field), dict):
                errors.append(f"{path}:{line}: milestones.{field} must be an object")

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
    if row.get("schema_version") not in {1, 2}:
        errors.append(f"{path}:{line}: schema_version must be 1 or 2")
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


def validate_nested_envelope_fields(obj: Any, prefix: str, errors: list[str], *, evidence_required: bool = False) -> None:
    if not isinstance(obj, dict):
        errors.append(f"{prefix} must be an object")
        return
    if "evidence_refs" in obj and not ref_list(obj["evidence_refs"], allow_empty=not evidence_required):
        errors.append(f"{prefix}.evidence_refs must be a structured-ref list")
    if "unknowns" in obj and not string_list(obj["unknowns"]):
        errors.append(f"{prefix}.unknowns must be a list of strings")


def validate_transition_events(realm_system: Any, path: Path, line: int, errors: list[str]) -> None:
    if not isinstance(realm_system, dict):
        errors.append(f"{path}:{line}: realm_system must be an object")
        return
    add_missing(errors, path, line, realm_system, {"realm_order", "transition_events", "break_conditions", "realm_limits", "unknowns"})
    for field in ("realm_order", "transition_events", "break_conditions", "realm_limits"):
        if field in realm_system and not isinstance(realm_system[field], list):
            errors.append(f"{path}:{line}: realm_system.{field} must be a list")
    if "unknowns" in realm_system and not string_list(realm_system["unknowns"]):
        errors.append(f"{path}:{line}: realm_system.unknowns must be a list of strings")

    for index, event in enumerate(realm_system.get("transition_events", []) if isinstance(realm_system.get("transition_events"), list) else []):
        prefix = f"{path}:{line}: realm_system.transition_events[{index}]"
        if not isinstance(event, dict):
            errors.append(f"{prefix} must be an object")
            continue
        required = {"event_id", "person_id", "before", "trigger_or_condition", "after", "change_type", "direct_evidence_refs", "costs_or_risks", "unknowns"}
        add_missing(errors, path, line, event, required)
        if event.get("change_type") not in REALM_CHANGE_TYPES:
            errors.append(f"{prefix}.change_type must be formal_realm_change/UNKNOWN")
        if not nonempty_string(event.get("before")):
            errors.append(f"{prefix}.before must be non-empty or UNKNOWN")
        if not nonempty_string(event.get("trigger_or_condition")):
            errors.append(f"{prefix}.trigger_or_condition must be non-empty")
        direct_refs = event.get("direct_evidence_refs")
        if not ref_list(direct_refs, allow_empty=event.get("change_type") != "formal_realm_change"):
            errors.append(f"{prefix}.direct_evidence_refs has invalid structure")
        after = event.get("after")
        if event.get("change_type") == "formal_realm_change":
            if not nonempty_string(after) or after == "UNKNOWN":
                errors.append(f"{prefix}.after must be a determined realm for formal_realm_change")
            if not ref_list(direct_refs):
                errors.append(f"{prefix}: formal realm change requires direct_evidence_refs")
        elif nonempty_string(after) and after != "UNKNOWN":
            errors.append(f"{prefix}: UNKNOWN realm change cannot declare a determined after realm")
        if not string_list(event.get("costs_or_risks")):
            errors.append(f"{prefix}.costs_or_risks must be a list of strings")
        if not string_list(event.get("unknowns")):
            errors.append(f"{prefix}.unknowns must be a list of strings")

    for index, realm in enumerate(realm_system.get("realm_order", []) if isinstance(realm_system.get("realm_order"), list) else []):
        prefix = f"{path}:{line}: realm_system.realm_order[{index}]"
        if not isinstance(realm, dict):
            errors.append(f"{prefix} must be an object")
            continue
        add_missing(errors, path, line, realm, {"realm_id", "name_in_book", "order", "stage_difference", "direct_evidence_refs"})
        if not nonempty_string(realm.get("realm_id")) or not nonempty_string(realm.get("name_in_book")):
            errors.append(f"{prefix}: realm_id and name_in_book must be non-empty")
        if not isinstance(realm.get("order"), int):
            errors.append(f"{prefix}.order must be an integer")
        if not nonempty_string(realm.get("stage_difference")):
            errors.append(f"{prefix}.stage_difference must be non-empty or UNKNOWN")
        if not ref_list(realm.get("direct_evidence_refs"), allow_empty=True):
            errors.append(f"{prefix}.direct_evidence_refs has invalid structure")


def validate_actual_power(actual: Any, path: Path, line: int, errors: list[str]) -> None:
    if not isinstance(actual, dict):
        errors.append(f"{path}:{line}: actual_combat_power must be an object")
        return
    add_missing(errors, path, line, actual, {"assessment_events", "power_gap_explanations", "unknowns"})
    if not isinstance(actual.get("assessment_events"), list):
        errors.append(f"{path}:{line}: actual_combat_power.assessment_events must be a list")
    if not string_list(actual.get("power_gap_explanations")):
        errors.append(f"{path}:{line}: power_gap_explanations must be a list of strings")
    if not string_list(actual.get("unknowns")):
        errors.append(f"{path}:{line}: actual_combat_power.unknowns must be a list of strings")
    for index, event in enumerate(actual.get("assessment_events", []) if isinstance(actual.get("assessment_events"), list) else []):
        prefix = f"{path}:{line}: actual_combat_power.assessment_events[{index}]"
        if not isinstance(event, dict):
            errors.append(f"{prefix} must be an object")
            continue
        required = {"event_id", "person_id", "nominal_realm", "observed_capability", "modifiers", "combat_result", "realm_change_proven", "direct_realm_evidence_refs", "evidence_refs", "unknowns"}
        add_missing(errors, path, line, event, required)
        if not isinstance(event.get("realm_change_proven"), bool):
            errors.append(f"{prefix}.realm_change_proven must be boolean")
        if not isinstance(event.get("modifiers"), list):
            errors.append(f"{prefix}.modifiers must be a list")
        if not ref_list(event.get("direct_realm_evidence_refs"), allow_empty=True):
            errors.append(f"{prefix}.direct_realm_evidence_refs has invalid structure")
        if not ref_list(event.get("evidence_refs")):
            errors.append(f"{prefix}.evidence_refs must be non-empty")
        if not string_list(event.get("unknowns")):
            errors.append(f"{prefix}.unknowns must be a list of strings")
        proven = event.get("realm_change_proven")
        direct_refs = event.get("direct_realm_evidence_refs", [])
        if proven is False and direct_refs:
            errors.append(f"{prefix}: realm_change_proven=false cannot carry direct_realm_evidence_refs")
        if proven is True and not ref_list(direct_refs):
            errors.append(f"{prefix}: realm_change_proven=true requires direct_realm_evidence_refs")


def validate_skills(skill_data: Any, path: Path, line: int, errors: list[str]) -> None:
    if not isinstance(skill_data, dict):
        errors.append(f"{path}:{line}: skill_proficiency must be an object")
        return
    add_missing(errors, path, line, skill_data, {"skill_events", "proficiency_boundaries"})
    if not isinstance(skill_data.get("skill_events"), list):
        errors.append(f"{path}:{line}: skill_events must be a list")
    if not string_list(skill_data.get("proficiency_boundaries")):
        errors.append(f"{path}:{line}: proficiency_boundaries must be a list of strings")
    for index, skill in enumerate(skill_data.get("skill_events", []) if isinstance(skill_data.get("skill_events"), list) else []):
        prefix = f"{path}:{line}: skill_proficiency.skill_events[{index}]"
        if not isinstance(skill, dict):
            errors.append(f"{prefix} must be an object")
            continue
        add_missing(errors, path, line, skill, {"skill_id", "name_in_book", "state_transitions", "hard_limits", "costs", "evidence_refs", "unknowns"})
        if not nonempty_string(skill.get("skill_id")) or not nonempty_string(skill.get("name_in_book")):
            errors.append(f"{prefix}: skill_id and name_in_book must be non-empty")
        if not isinstance(skill.get("state_transitions"), list):
            errors.append(f"{prefix}.state_transitions must be a list")
        for transition_index, transition in enumerate(skill.get("state_transitions", []) if isinstance(skill.get("state_transitions"), list) else []):
            tprefix = f"{prefix}.state_transitions[{transition_index}]"
            if not isinstance(transition, dict):
                errors.append(f"{tprefix} must be an object")
                continue
            add_missing(errors, path, line, transition, {"from_state", "trigger_or_training", "to_state", "visible_validation", "evidence_refs", "unknowns"})
            if transition.get("from_state") not in SKILL_STATES or transition.get("to_state") not in SKILL_STATES:
                errors.append(f"{tprefix}: state must be UNKNOWN/obtained/learning/practiced/mastered/proficient/evolved")
            if not nonempty_string(transition.get("trigger_or_training")):
                errors.append(f"{tprefix}.trigger_or_training must be non-empty")
            if transition.get("to_state") in {"mastered", "proficient", "evolved"} and not nonempty_string(transition.get("visible_validation")):
                errors.append(f"{tprefix}: advanced state requires visible_validation")
            if not ref_list(transition.get("evidence_refs")):
                errors.append(f"{tprefix}.evidence_refs must be non-empty")
            if not string_list(transition.get("unknowns")):
                errors.append(f"{tprefix}.unknowns must be a list of strings")


def validate_resources(resources: Any, path: Path, line: int, errors: list[str]) -> None:
    if not isinstance(resources, dict):
        errors.append(f"{path}:{line}: equipment_resources must be an object")
        return
    add_missing(errors, path, line, resources, {"items", "resource_loops"})
    for field in ("items", "resource_loops"):
        if not isinstance(resources.get(field), list):
            errors.append(f"{path}:{line}: equipment_resources.{field} must be a list")
    for index, item in enumerate(resources.get("items", []) if isinstance(resources.get("items"), list) else []):
        prefix = f"{path}:{line}: equipment_resources.items[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        required = {"item_id", "name_in_book", "item_kind", "effect_mode", "source_and_access", "use_or_conversion", "duration_or_ownership", "growth_effect", "permanent_self_change_proven", "evidence_refs", "unknowns"}
        add_missing(errors, path, line, item, required)
        if item.get("effect_mode") not in EFFECT_MODES:
            errors.append(f"{prefix}.effect_mode is not controlled")
        if not isinstance(item.get("permanent_self_change_proven"), bool):
            errors.append(f"{prefix}.permanent_self_change_proven must be boolean")
        if item.get("effect_mode") == "permanent_self_growth" and item.get("permanent_self_change_proven") is False:
            errors.append(f"{prefix}: permanent_self_growth requires permanent_self_change_proven=true or UNKNOWN mode")
        if item.get("permanent_self_change_proven") is True and item.get("effect_mode") not in {"long_term_conversion", "permanent_self_growth"}:
            errors.append(f"{prefix}: permanent self change conflicts with effect_mode")
        if not ref_list(item.get("evidence_refs")):
            errors.append(f"{prefix}.evidence_refs must be non-empty")
        if not string_list(item.get("unknowns")):
            errors.append(f"{prefix}.unknowns must be a list of strings")
    for index, loop in enumerate(resources.get("resource_loops", []) if isinstance(resources.get("resource_loops"), list) else []):
        prefix = f"{path}:{line}: equipment_resources.resource_loops[{index}]"
        if not isinstance(loop, dict):
            errors.append(f"{prefix} must be an object")
            continue
        add_missing(errors, path, line, loop, {"input", "conversion", "output", "loss_or_cost", "evidence_refs", "unknowns"})
        if not ref_list(loop.get("evidence_refs")):
            errors.append(f"{prefix}.evidence_refs must be non-empty")
        if not string_list(loop.get("unknowns")):
            errors.append(f"{prefix}.unknowns must be a list of strings")


def validate_permissions(permissions: Any, path: Path, line: int, errors: list[str]) -> None:
    if not isinstance(permissions, dict):
        errors.append(f"{path}:{line}: identity_permissions must be an object")
        return
    add_missing(errors, path, line, permissions, {"permission_events", "permission_boundaries"})
    if not isinstance(permissions.get("permission_events"), list):
        errors.append(f"{path}:{line}: permission_events must be a list")
    if not string_list(permissions.get("permission_boundaries")):
        errors.append(f"{path}:{line}: permission_boundaries must be a list of strings")
    for index, event in enumerate(permissions.get("permission_events", []) if isinstance(permissions.get("permission_events"), list) else []):
        prefix = f"{path}:{line}: identity_permissions.permission_events[{index}]"
        if not isinstance(event, dict):
            errors.append(f"{prefix} must be an object")
            continue
        required = {"permission_id", "name_in_book", "issuer_or_owner", "access_unlocked", "training_entry", "resource_entry", "map_entry", "growth_effect_type", "realm_change_proven", "direct_realm_evidence_refs", "evidence_refs", "unknowns"}
        add_missing(errors, path, line, event, required)
        if event.get("growth_effect_type") not in GROWTH_EFFECT_TYPES:
            errors.append(f"{prefix}.growth_effect_type is not controlled")
        if not isinstance(event.get("realm_change_proven"), bool):
            errors.append(f"{prefix}.realm_change_proven must be boolean")
        for field in ("access_unlocked", "training_entry", "resource_entry", "map_entry"):
            if not string_list(event.get(field)):
                errors.append(f"{prefix}.{field} must be a list of strings")
        direct_refs = event.get("direct_realm_evidence_refs", [])
        if not ref_list(direct_refs, allow_empty=True):
            errors.append(f"{prefix}.direct_realm_evidence_refs has invalid structure")
        if event.get("growth_effect_type") == "access_only" and event.get("realm_change_proven") is True:
            errors.append(f"{prefix}: access_only cannot be a realm change")
        if event.get("growth_effect_type") == "formal_growth" and event.get("realm_change_proven") is not True:
            errors.append(f"{prefix}: formal_growth requires realm_change_proven=true")
        if event.get("realm_change_proven") is False and direct_refs:
            errors.append(f"{prefix}: realm_change_proven=false cannot carry direct_realm_evidence_refs")
        if event.get("realm_change_proven") is True and not ref_list(direct_refs):
            errors.append(f"{prefix}: realm_change_proven=true requires direct_realm_evidence_refs")
        if not ref_list(event.get("evidence_refs")):
            errors.append(f"{prefix}.evidence_refs must be non-empty")
        if not string_list(event.get("unknowns")):
            errors.append(f"{prefix}.unknowns must be a list of strings")


def validate_interfaces(interfaces: Any, path: Path, line: int, errors: list[str]) -> None:
    if not isinstance(interfaces, list):
        errors.append(f"{path}:{line}: golden_finger_interfaces must be a list")
        return
    forbidden_nested_keys = {"input", "process", "output", "core_formula", "activation_conditions", "growth_stages", "resource_loop"}
    for index, item in enumerate(interfaces):
        prefix = f"{path}:{line}: golden_finger_interfaces[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        add_missing(errors, path, line, item, {"interface_id", "golden_finger_record_refs", "growth_effect", "affected_layer", "boundary", "evidence_refs", "unknowns"})
        if not string_list(item.get("golden_finger_record_refs"), allow_empty=False):
            errors.append(f"{prefix}.golden_finger_record_refs must be a non-empty list")
        if item.get("affected_layer") not in {"realm", "build", "skill", "combat_power", "resource", "permission"}:
            errors.append(f"{prefix}.affected_layer is not controlled")
        if forbidden_nested_keys.intersection(item):
            errors.append(f"{prefix}: interface contains forbidden golden-finger business keys")
        if not ref_list(item.get("evidence_refs")):
            errors.append(f"{prefix}.evidence_refs must be non-empty")
        if not string_list(item.get("unknowns")):
            errors.append(f"{prefix}.unknowns must be a list of strings")


def validate_per_book(row: dict[str, Any], path: Path, line: int, errors: list[str]) -> None:
    if row.get("schema_version") == 2:
        validate_v2_per_book(row, path, line, errors)
        return
    required = {
        "book_id", "title", "chapters_covered", "universal_system", "realm_system", "protagonist_build",
        "golden_finger_interfaces", "actual_combat_power", "skill_proficiency", "equipment_resources",
        "identity_permissions", "milestones", "emotion_overlay_links", "growth_fatigue_risks", "source_numbering_notes",
    }
    add_missing(errors, path, line, row, required)
    for field in ("title", "chapters_covered"):
        if field in row and not nonempty_string(row.get(field)):
            errors.append(f"{path}:{line}: {field} must be non-empty")
    validate_transition_events(row.get("realm_system"), path, line, errors)
    for field in ("universal_system", "protagonist_build"):
        if field in row and not isinstance(row.get(field), dict):
            errors.append(f"{path}:{line}: {field} must be an object")
    for field in ("emotion_overlay_links", "growth_fatigue_risks", "source_numbering_notes"):
        if field in row and not isinstance(row.get(field), list):
            errors.append(f"{path}:{line}: {field} must be a list")
    validate_interfaces(row.get("golden_finger_interfaces"), path, line, errors)
    validate_actual_power(row.get("actual_combat_power"), path, line, errors)
    validate_skills(row.get("skill_proficiency"), path, line, errors)
    validate_resources(row.get("equipment_resources"), path, line, errors)
    validate_permissions(row.get("identity_permissions"), path, line, errors)

    milestones = row.get("milestones")
    if not isinstance(milestones, dict):
        errors.append(f"{path}:{line}: milestones must be an object")
    else:
        for field in ("first_system_display", "first_realm_display", "first_direct_realm_change", "first_skill_mastery_validation", "first_combat_power_validation"):
            if field not in milestones or not isinstance(milestones[field], dict):
                errors.append(f"{path}:{line}: milestones.{field} must be an object")


def validate_gap(row: dict[str, Any], path: Path, line: int, errors: list[str]) -> None:
    add_missing(errors, path, line, row, {"reason", "known_evidence", "blocked_outputs"})
    if row.get("confidence") != "LOW":
        errors.append(f"{path}:{line}: gap records must be LOW confidence")
    if not nonempty_string(row.get("reason")):
        errors.append(f"{path}:{line}: gap reason must be non-empty")
    for field in ("known_evidence", "blocked_outputs"):
        if field in row and not string_list(row.get(field)):
            errors.append(f"{path}:{line}: {field} must be a list of strings")


def validate_nearest_neighbor(row: dict[str, Any], path: Path, line: int, errors: list[str]) -> None:
    add_missing(errors, path, line, row, {"comparison_ids", "comparison_dimensions", "similarities", "difference_boundary", "decision", "reason"})
    book_ids = row.get("book_ids")
    if isinstance(book_ids, list) and len(set(book_ids)) < 2:
        errors.append(f"{path}:{line}: nearest_neighbor requires at least two distinct book_ids")
    if not string_list(row.get("comparison_ids"), allow_empty=False):
        errors.append(f"{path}:{line}: comparison_ids must be a non-empty list")
    if not isinstance(row.get("comparison_dimensions"), dict):
        errors.append(f"{path}:{line}: comparison_dimensions must be an object")
    if not isinstance(row.get("similarities"), list):
        errors.append(f"{path}:{line}: similarities must be a list")
    for field in ("difference_boundary", "decision", "reason"):
        if field in row and not nonempty_string(row.get(field)):
            errors.append(f"{path}:{line}: {field} must be non-empty")
    if row.get("decision") not in NEIGHBOR_DECISIONS:
        errors.append(f"{path}:{line}: unsupported nearest_neighbor decision")


def validate_cluster(row: dict[str, Any], path: Path, line: int, errors: list[str]) -> None:
    required = {"member_record_ids", "cluster_level", "label", "shared_operation", "boundary_conditions", "supporting_book_count", "nearest_neighbor_record_ids", "merge_decision"}
    add_missing(errors, path, line, row, required)
    book_ids = row.get("book_ids")
    if isinstance(book_ids, list) and row.get("supporting_book_count") != len(set(book_ids)):
        errors.append(f"{path}:{line}: supporting_book_count must match unique book_ids")
    for field in ("member_record_ids", "boundary_conditions", "nearest_neighbor_record_ids"):
        if not string_list(row.get(field)):
            errors.append(f"{path}:{line}: {field} must be a list of strings")
    for field in ("cluster_level", "label", "shared_operation"):
        if field in row and not nonempty_string(row.get(field)):
            errors.append(f"{path}:{line}: {field} must be non-empty")
    if row.get("merge_decision") not in CLUSTER_DECISIONS:
        errors.append(f"{path}:{line}: unsupported cluster merge_decision")


def validate_qa(row: dict[str, Any], path: Path, line: int, errors: list[str]) -> None:
    add_missing(errors, path, line, row, {"scope", "checks", "contamination_risks", "gaps", "disputes", "blocked_outputs"})
    if not nonempty_string(row.get("scope")):
        errors.append(f"{path}:{line}: scope must be non-empty")
    checks = row.get("checks")
    required_checks = (
        {
            "coverage", "evidence_traceability", "source_only_extraction", "multi_system_boundary",
            "realm_ownership", "system_relation_integrity", "technique_artifact_boundary",
            "combat_power_boundary", "resource_permission_boundary", "interface_boundary", "cross_book_gate",
        }
        if row.get("schema_version") == 2
        else {
            "coverage", "evidence_traceability", "universal_vs_realm_boundary", "realm_direct_evidence",
            "skill_state_boundary", "combat_power_boundary", "resource_permission_boundary", "interface_boundary", "cross_book_gate",
        }
    )
    if not isinstance(checks, dict):
        errors.append(f"{path}:{line}: checks must be an object")
    else:
        add_missing(errors, path, line, checks, required_checks)
        for field in required_checks:
            if field in checks and checks[field] not in QA_STATUS:
                errors.append(f"{path}:{line}: checks.{field} must be PASS/HOLD/FAIL")
    for field in ("contamination_risks", "gaps", "disputes", "blocked_outputs"):
        if field in row and not isinstance(row.get(field), list):
            errors.append(f"{path}:{line}: {field} must be a list")


def validate_handoff(row: dict[str, Any], path: Path, line: int, errors: list[str]) -> None:
    add_missing(errors, path, line, row, {"candidate_record_ids", "recommended_action", "decision_points", "evidence_gaps", "forbidden_automatic_actions"})
    if not string_list(row.get("candidate_record_ids"), allow_empty=False):
        errors.append(f"{path}:{line}: candidate_record_ids must be a non-empty list")
    for field in ("decision_points", "evidence_gaps", "forbidden_automatic_actions"):
        if not string_list(row.get(field)):
            errors.append(f"{path}:{line}: {field} must be a list of strings")
    if row.get("recommended_action") not in HANDOFF_ACTIONS:
        errors.append(f"{path}:{line}: unsupported recommended_action")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Validate novel-cultivation-system-miner JSONL outputs.")
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

    result = {"kind": args.kind, "records": records, "covered_books": sorted(set(covered_books)), "errors": errors, "ok": not errors}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
