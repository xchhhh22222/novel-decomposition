#!/usr/bin/env python3
"""Strict validator for V1.6.1 supplemental derived materials."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

BOOK_RE = re.compile(r"^BOOK_\d{3,}$")
EVIDENCE_RE = re.compile(r"^(BOOK_\d{3,}):CHAPTER:(\d{4,})$")
CONFIDENCE = {"HIGH", "MEDIUM", "LOW"}
QA_STATUS = {"PASS", "HOLD"}
COMMON_REQUIRED = {
    "record_type",
    "schema_version",
    "record_id",
    "status",
    "book_id",
    "view",
    "evidence_refs",
    "unknowns",
    "confidence",
    "qa_status",
}
COMMON_OPTIONAL = {"legacy_record_id", "notes"}

VIEW_SPECS: dict[str, dict[str, Any]] = {
    "ability_assets": {
        "kind": "jsonl",
        "path": "02_金手指/derived/ability_assets.jsonl",
        "id_tag": "ABILITY",
        "required": {
            "name_in_book",
            "ability_core",
            "trigger",
            "input",
            "operation",
            "output",
            "limit",
            "cost",
            "growth",
            "first_showcase",
            "appeal_hook",
            "immediate_fantasy",
            "combat_value",
            "social_value",
            "plot_generation",
            "combination_interfaces",
            "counterplay",
            "fatigue_risk",
        },
        "optional": set(),
        "forbidden": {"asset_id", "ability_name", "core"},
    },
    "dungeon_rule_assets": {
        "kind": "jsonl",
        "path": "03_世界观/derived/dungeon_rule_assets.jsonl",
        "id_tag": "DUNGEON",
        "required": {
            "dungeon_name",
            "chapter_span",
            "entry_condition",
            "surface_rules",
            "hidden_rules",
            "rule_reliability",
            "victory_condition",
            "failure_condition",
            "death_or_penalty",
            "resource_pressure",
            "information_asymmetry",
            "roles",
            "team_structure",
            "conflict_structure",
            "loophole",
            "discovery_process",
            "escalation",
            "turning_point",
            "exit_condition",
            "reward",
            "mainline_connection",
            "reuse_pattern",
            "fatigue_risk",
        },
        "optional": {"dungeon_type", "gate_no"},
        "forbidden": set(),
    },
    "relationship_engine_assets": {
        "kind": "jsonl",
        "path": "05_人物功能与标签/derived/relationship_engine_assets.jsonl",
        "id_tag": "RELATIONSHIP",
        "required": {
            "engine_name",
            "sides",
            "engine_type",
            "binding_reason",
            "first_exchange",
            "shared_interest",
            "conflicting_interest",
            "information_boundary",
            "active_choices",
            "progression_states",
            "break_condition",
            "reconciliation_condition",
            "replaceability",
            "protagonist_interface",
        },
        "optional": set(),
        "forbidden": {"conflicting_information", "conflicting_information_boundary"},
    },
    "charismatic_antagonist_assets": {
        "kind": "jsonl",
        "path": "05_人物功能与标签/derived/charismatic_antagonist_assets.jsonl",
        "id_tag": "ANTAGONIST",
        "required": {
            "person_id",
            "name_in_book",
            "role_kind",
            "goal",
            "values",
            "resource_domain",
            "faction",
            "competence",
            "threat_source",
            "charisma_source",
            "reader_respect_source",
            "mirror_to_protagonist",
            "cooperation_possibility",
            "hostility_reason",
            "boundary",
            "scene_stealing_pattern",
            "escalation_path",
            "defeat_or_exit_condition",
            "failure_continuation",
            "reader_memory_why",
            "long_term_tension",
        },
        "optional": set(),
        "forbidden": {
            "long_term_tension_with_protagonist",
            "boundary_and_failure_story_potential",
            "failure_continuity_placeholder",
        },
    },
    "combat_expression_assets": {
        "kind": "collection",
        "path": "04_修炼体系/derived/combat_expression_assets.json",
        "id_tag": "COMBAT",
        "required": {
            "asset_name",
            "function_slot",
            "trigger",
            "input",
            "operation",
            "range",
            "action_pattern",
            "output",
            "cost",
            "limit",
            "counterplay",
            "visual_expression",
            "combat_role",
            "combination_interface",
            "compatible_system",
            "user_archetype",
        },
        "optional": set(),
        "forbidden": {"asset_id", "label", "description"},
    },
}

DESCRIPTIVE_LIST_FIELDS = {"sides", "evidence_refs", "unknowns"}


def is_nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_nonempty_text_or_list(value: Any) -> bool:
    if is_nonempty_text(value):
        return True
    return isinstance(value, list) and bool(value) and all(is_nonempty_text(x) for x in value)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        obj = json.loads(line)
        if not isinstance(obj, dict):
            raise ValueError(f"{path}:{lineno}: JSONL row must be an object")
        rows.append(obj)
    return rows


def load_collection(path: Path, view: str, book_id: str, errors: list[str]) -> list[dict[str, Any]]:
    obj = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(obj, dict):
        errors.append(f"{path}: top level must be object")
        return []
    allowed_top = {"schema_version", "record_type", "book_id", "view", "asset_count", "assets", "notes"}
    unknown_top = sorted(set(obj) - allowed_top)
    if unknown_top:
        errors.append(f"{path}: unknown top-level fields: {', '.join(unknown_top)}")
    if obj.get("schema_version") != 2:
        errors.append(f"{path}: top-level schema_version must be integer 2")
    if obj.get("record_type") != "derived_asset_collection":
        errors.append(f"{path}: record_type must be derived_asset_collection")
    if obj.get("book_id") != book_id:
        errors.append(f"{path}: book_id must equal {book_id}")
    if obj.get("view") != view:
        errors.append(f"{path}: view must equal {view}")
    assets = obj.get("assets")
    if not isinstance(assets, list):
        errors.append(f"{path}: assets must be a list")
        return []
    if any(isinstance(x, list) for x in assets):
        errors.append(f"{path}: assets must be a flat one-dimensional array")
        return []
    if any(not isinstance(x, dict) for x in assets):
        errors.append(f"{path}: every assets item must be an object")
        return []
    if obj.get("asset_count") != len(assets):
        errors.append(f"{path}: asset_count={obj.get('asset_count')} != len(assets)={len(assets)}")
    return assets


def validate_common(
    row: dict[str, Any],
    view: str,
    book_id: str,
    id_tag: str,
    index: int,
    allowed_specific: set[str],
    forbidden: set[str],
    where: str,
    seen_ids: set[str],
    errors: list[str],
) -> None:
    required = COMMON_REQUIRED | allowed_specific
    optional = COMMON_OPTIONAL | VIEW_SPECS[view]["optional"]
    missing = sorted(required - set(row))
    if missing:
        errors.append(f"{where}: missing fields: {', '.join(missing)}")
    forbidden_present = sorted(forbidden & set(row))
    if forbidden_present:
        errors.append(f"{where}: forbidden legacy fields: {', '.join(forbidden_present)}")
    unknown = sorted(set(row) - required - optional)
    if unknown:
        errors.append(f"{where}: unknown fields: {', '.join(unknown)}")

    if row.get("record_type") != "derived_asset":
        errors.append(f"{where}.record_type must be derived_asset")
    if row.get("schema_version") != 2:
        errors.append(f"{where}.schema_version must be integer 2")
    if row.get("status") != "candidate":
        errors.append(f"{where}.status must be candidate")
    if row.get("book_id") != book_id:
        errors.append(f"{where}.book_id must equal {book_id}")
    if row.get("view") != view:
        errors.append(f"{where}.view must equal {view}")

    expected_id = f"DA:{id_tag}:{book_id}:{index:03d}"
    rid = row.get("record_id")
    if rid != expected_id:
        errors.append(f"{where}.record_id must be {expected_id}, got {rid!r}")
    if isinstance(rid, str):
        if rid in seen_ids:
            errors.append(f"{where}: duplicate record_id {rid}")
        seen_ids.add(rid)

    evidence = row.get("evidence_refs")
    if not isinstance(evidence, list) or not evidence:
        errors.append(f"{where}.evidence_refs must be a non-empty list")
    else:
        for ref in evidence:
            if not isinstance(ref, str):
                errors.append(f"{where}.evidence_refs contains non-string")
                continue
            m = EVIDENCE_RE.fullmatch(ref)
            if not m:
                errors.append(f"{where}: non-canonical evidence ref {ref!r}")
            elif m.group(1) != book_id:
                errors.append(f"{where}: evidence ref book mismatch {ref!r}")

    unknowns = row.get("unknowns")
    if not isinstance(unknowns, list) or any(not is_nonempty_text(x) for x in unknowns):
        errors.append(f"{where}.unknowns must be a list of non-empty strings")

    confidence = row.get("confidence")
    if confidence not in CONFIDENCE:
        errors.append(f"{where}.confidence must be HIGH/MEDIUM/LOW")
    if isinstance(unknowns, list) and unknowns and confidence == "HIGH":
        errors.append(f"{where}: confidence HIGH forbidden when unknowns is non-empty")

    if row.get("qa_status") not in QA_STATUS:
        errors.append(f"{where}.qa_status must be PASS or HOLD")

    for field in allowed_specific:
        if field in DESCRIPTIVE_LIST_FIELDS:
            continue
        if field == "sides":
            continue
        if field in row and not is_nonempty_text_or_list(row[field]):
            errors.append(f"{where}.{field} must be non-empty string or non-empty string list")

    if view == "relationship_engine_assets":
        sides = row.get("sides")
        if not isinstance(sides, list) or len(sides) < 2 or any(not is_nonempty_text(x) for x in sides):
            errors.append(f"{where}.sides must contain at least 2 non-empty strings")


def manifest_counts(root: Path, book_id: str) -> tuple[dict[str, int], list[str]]:
    errors: list[str] = []
    path = root / "books" / book_id / "manifest.json"
    if not path.exists():
        return {}, [f"{path}: manifest missing"]
    try:
        manifest = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {}, [f"{path}: manifest parse failed: {exc}"]
    counts: dict[str, int] = {}
    outputs = manifest.get("outputs")
    if not isinstance(outputs, dict):
        return counts, errors
    views = outputs.get("derived_views")
    if not isinstance(views, list):
        return counts, errors
    for item in views:
        if not isinstance(item, dict):
            continue
        view = item.get("view")
        records = item.get("records")
        if view in VIEW_SPECS and isinstance(records, int):
            counts[view] = records
    return counts, errors


def validate_book(root: Path, book_id: str, seen_ids: set[str]) -> tuple[dict[str, int], list[str]]:
    errors: list[str] = []
    counts: dict[str, int] = {}
    manifest_view_counts, manifest_errors = manifest_counts(root, book_id)
    errors.extend(manifest_errors)
    book_root = root / "books" / book_id
    if not book_root.exists():
        errors.append(f"{book_root}: book directory missing")
        return counts, errors

    for view, spec in VIEW_SPECS.items():
        path = book_root / spec["path"]
        manifest_expected = manifest_view_counts.get(view)
        if not path.exists():
            if manifest_expected is not None:
                errors.append(f"{path}: listed in manifest but canonical file missing")
            continue
        try:
            if spec["kind"] == "jsonl":
                rows = load_jsonl(path)
            else:
                rows = load_collection(path, view, book_id, errors)
        except Exception as exc:
            errors.append(f"{path}: parse failed: {exc}")
            continue

        counts[view] = len(rows)
        if manifest_expected is not None and manifest_expected != len(rows):
            errors.append(
                f"{path}: manifest records={manifest_expected} != actual records={len(rows)}"
            )

        for index, row in enumerate(rows, 1):
            validate_common(
                row=row,
                view=view,
                book_id=book_id,
                id_tag=spec["id_tag"],
                index=index,
                allowed_specific=spec["required"],
                forbidden=spec["forbidden"],
                where=f"{path} record[{index}]",
                seen_ids=seen_ids,
                errors=errors,
            )

    return counts, errors


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Validate V1.6.1 derived material contract.")
    parser.add_argument("--root", type=Path, required=True, help="nova-material-library root")
    parser.add_argument(
        "--books",
        required=True,
        help="comma-separated BOOK IDs, e.g. BOOK_010,BOOK_011",
    )
    args = parser.parse_args()

    books = [x.strip() for x in args.books.split(",") if x.strip()]
    errors: list[str] = []
    if not books:
        errors.append("--books must contain at least one BOOK ID")
    for book in books:
        if not BOOK_RE.fullmatch(book):
            errors.append(f"invalid BOOK ID: {book}")

    seen_ids: set[str] = set()
    totals = {view: 0 for view in VIEW_SPECS}
    per_book: dict[str, dict[str, int]] = {}

    if not errors:
        for book in books:
            counts, book_errors = validate_book(args.root, book, seen_ids)
            per_book[book] = counts
            errors.extend(book_errors)
            for view, count in counts.items():
                totals[view] += count

    result = {
        "gate": "DERIVED_MATERIAL_CONTRACT_V1_6_1",
        "status": "PASS" if not errors else "FAIL",
        "books": books,
        "per_book_counts": per_book,
        "totals": totals,
        "unique_record_ids": len(seen_ids),
        "errors": errors,
        "ok": not errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
