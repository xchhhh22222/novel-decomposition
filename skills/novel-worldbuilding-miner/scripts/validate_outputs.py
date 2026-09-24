#!/usr/bin/env python3
"""Validate derived JSONL records produced by novel-worldbuilding-miner.

This validator intentionally checks structure and explicit contract gates only.
Semantic questions such as whether an institution really changes resource flow
remain in clustering-and-qa.md and are not inferred from surface vocabulary.
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
COMPLETENESS = {"complete", "partial", "UNKNOWN"}
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
FACTION_TYPES = {"official", "military", "academy", "family", "corporation", "guild", "religion", "race", "underground", "regional", "other", "UNKNOWN"}
FACTION_RELATION_TYPES = {"ally", "rival", "enemy", "dependency", "trade", "oversight", "UNKNOWN"}


def validate_factions(row: dict[str, Any], path: Path, line: int, errors: list[str]) -> None:
    factions = row.get("factions")
    if not isinstance(factions, list):
        errors.append(f"{path}:{line}: factions must be a list")
        return

    faction_ids: set[str] = set()
    for index, faction in enumerate(factions):
        prefix = f"{path}:{line}: factions[{index}]"
        if not isinstance(faction, dict):
            errors.append(f"{prefix} must be an object")
            continue
        required = {
            "faction_id", "name_in_book", "faction_type", "public_role", "actual_interest",
            "controlled_resources", "controlled_territories_or_access", "controlled_information_or_rules",
            "recruitment_or_entry", "internal_hierarchy", "relations", "conflict_sources",
            "protagonist_interface", "evidence_refs", "unknowns",
        }
        missing = sorted(required - set(faction))
        if missing:
            errors.append(f"{prefix} missing fields: {', '.join(missing)}")
        faction_id = faction.get("faction_id")
        if not nonempty_string(faction_id):
            errors.append(f"{prefix}.faction_id must be non-empty")
        elif faction_id in faction_ids:
            errors.append(f"{prefix}: duplicate faction_id={faction_id}")
        else:
            faction_ids.add(faction_id)
        if faction.get("faction_type") not in FACTION_TYPES:
            errors.append(f"{prefix}.faction_type is not controlled")
        for field in (
            "controlled_resources", "controlled_territories_or_access", "controlled_information_or_rules",
            "recruitment_or_entry", "internal_hierarchy", "relations", "conflict_sources",
        ):
            if field in faction and not isinstance(faction.get(field), list):
                errors.append(f"{prefix}.{field} must be a list")
        if not ref_list(faction.get("evidence_refs")):
            errors.append(f"{prefix}.evidence_refs must be non-empty")
        if not string_list(faction.get("unknowns")):
            errors.append(f"{prefix}.unknowns must be a list of strings")

    for index, faction in enumerate(factions):
        if not isinstance(faction, dict):
            continue
        for rindex, relation in enumerate(faction.get("relations", []) if isinstance(faction.get("relations"), list) else []):
            prefix = f"{path}:{line}: factions[{index}].relations[{rindex}]"
            if not isinstance(relation, dict):
                errors.append(f"{prefix} must be an object")
                continue
            if relation.get("target_faction_id") not in faction_ids:
                errors.append(f"{prefix}: target_faction_id must reference a local faction")
            if relation.get("relation_type") not in FACTION_RELATION_TYPES:
                errors.append(f"{prefix}.relation_type is not controlled")
            if not nonempty_string(relation.get("observable_basis")):
                errors.append(f"{prefix}.observable_basis must be non-empty")
            if not ref_list(relation.get("evidence_refs")):
                errors.append(f"{prefix}.evidence_refs must be non-empty")

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
BOOK_KINDS = {"per_book", "qa", "gap"}
BOOKS_KINDS = {"nearest_neighbor", "cluster", "handoff"}
CHAIN_CONSEQUENCE_FIELDS = (
    "scarcity",
    "resource_flow",
    "interests_and_institutions",
    "constraints",
    "conflict_engine",
    "plot_entry",
    "information_ownership",
    "map_or_region_effect",
    "recurring_threat",
)


def iter_jsonl(target: Path) -> Iterable[tuple[Path, int, str]]:
    paths = sorted(target.rglob("*.jsonl")) if target.is_dir() else [target]
    for path in paths:
        if not path.exists():
            yield path, 0, ""
            continue
        for number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
            yield path, number, raw


def load_completion_manifest(path: Path, expected_books: set[str]) -> list[str]:
    """Return errors for the explicit cross-book completion manifest.

    A command-line switch alone is not evidence that every target book has
    completed extraction.  The manifest must contain exactly one candidate
    per_book or gap record for every expected book.
    """
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
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(nonempty_string(item) for item in value)
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
        errors.append(f"{path}:{line}: evidence_refs must be a non-empty list of structured refs")
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


def validate_per_book(row: dict[str, Any], path: Path, line: int, errors: list[str]) -> None:
    required = {
        "book_id",
        "title",
        "chapters_covered",
        "world_core_premise",
        "ordinary_life_state",
        "rule_chains",
        "institution_and_interest_patterns",
        "resource_circuits",
        "threat_generators",
        "map_expansion_patterns",
        "information_control_patterns",
        "milestones",
        "interfaces",
        "emotion_overlay_links",
        "revelation_rhythm",
        "fatigue_risks",
        "source_numbering_notes",
    }
    if row.get("schema_version") == 2:
        required.add("factions")
    add_missing(errors, path, line, row, required)
    if row.get("schema_version") == 2:
        validate_factions(row, path, line, errors)
    for field in ("title", "chapters_covered", "world_core_premise", "ordinary_life_state"):
        if field in row and not nonempty_string(row.get(field)):
            errors.append(f"{path}:{line}: {field} must be a non-empty string")
    list_fields = {
        "rule_chains",
        "institution_and_interest_patterns",
        "resource_circuits",
        "threat_generators",
        "map_expansion_patterns",
        "information_control_patterns",
        "emotion_overlay_links",
        "revelation_rhythm",
        "fatigue_risks",
        "source_numbering_notes",
    }
    for field in list_fields:
        if field in row and not isinstance(row.get(field), list):
            errors.append(f"{path}:{line}: {field} must be a list")

    chains = row.get("rule_chains")
    if isinstance(chains, list) and not chains:
        errors.append(f"{path}:{line}: per_book needs at least one rule chain; use record_type=gap when evidence is insufficient")
    if isinstance(chains, list):
        for index, chain in enumerate(chains):
            prefix = f"{path}:{line}: rule_chains[{index}]"
            if not isinstance(chain, dict):
                errors.append(f"{prefix} must be an object")
                continue
            for field in ("chain_id", "completeness", "rule_statement", "evidence_refs", "unknowns"):
                if field not in chain:
                    errors.append(f"{prefix}: missing {field}")
            if chain.get("completeness") not in COMPLETENESS:
                errors.append(f"{prefix}: completeness must be complete/partial/UNKNOWN")
            if not nonempty_string(chain.get("rule_statement")):
                errors.append(f"{prefix}: rule_statement must be non-empty")
            consequence_present = any(
                chain.get(field) is not None
                and (not isinstance(chain.get(field), str) or bool(chain.get(field).strip()))
                and chain.get(field) != "UNKNOWN"
                for field in CHAIN_CONSEQUENCE_FIELDS
            )
            if not consequence_present:
                errors.append(f"{prefix}: requires rule_statement plus at least one observable consequence")
            if "evidence_refs" in chain and not ref_list(chain.get("evidence_refs")):
                errors.append(f"{prefix}: evidence_refs must be a non-empty structured-ref list")
            if "unknowns" in chain and not string_list(chain.get("unknowns")):
                errors.append(f"{prefix}: unknowns must be a list of strings")

    milestones = row.get("milestones")
    if not isinstance(milestones, dict):
        errors.append(f"{path}:{line}: milestones must be an object")
    else:
        for field in ("first_world_display", "first_rule_validation", "first_scale_upgrade"):
            if field not in milestones:
                errors.append(f"{path}:{line}: milestones missing {field}")
            elif not isinstance(milestones[field], dict):
                errors.append(f"{path}:{line}: milestones.{field} must be an object")

    interfaces = row.get("interfaces")
    if not isinstance(interfaces, dict):
        errors.append(f"{path}:{line}: interfaces must be an object")
    else:
        for field in ("golden_finger", "cultivation_system", "other_scoped_interfaces"):
            if field not in interfaces:
                errors.append(f"{path}:{line}: interfaces missing {field}")
            elif not isinstance(interfaces[field], list):
                errors.append(f"{path}:{line}: interfaces.{field} must be a list")


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
    add_missing(
        errors,
        path,
        line,
        row,
        {"comparison_ids", "comparison_dimensions", "similarities", "difference_boundary", "decision", "reason"},
    )
    book_ids = row.get("book_ids")
    if isinstance(book_ids, list) and len(set(book_ids)) < 2:
        errors.append(f"{path}:{line}: nearest_neighbor requires at least two distinct book_ids")
    if "comparison_ids" in row and not string_list(row.get("comparison_ids"), allow_empty=False):
        errors.append(f"{path}:{line}: comparison_ids must be a non-empty list of strings")
    if "similarities" in row and not isinstance(row.get("similarities"), list):
        errors.append(f"{path}:{line}: similarities must be a list")
    if "comparison_dimensions" in row and not isinstance(row.get("comparison_dimensions"), dict):
        errors.append(f"{path}:{line}: comparison_dimensions must be an object")
    for field in ("difference_boundary", "decision", "reason"):
        if field in row and not nonempty_string(row.get(field)):
            errors.append(f"{path}:{line}: {field} must be non-empty")
    if row.get("decision") not in NEIGHBOR_DECISIONS:
        errors.append(f"{path}:{line}: unsupported nearest_neighbor decision")


def validate_cluster(row: dict[str, Any], path: Path, line: int, errors: list[str]) -> None:
    add_missing(
        errors,
        path,
        line,
        row,
        {
            "member_record_ids",
            "cluster_level",
            "label",
            "shared_operation",
            "boundary_conditions",
            "supporting_book_count",
            "nearest_neighbor_record_ids",
            "merge_decision",
        },
    )
    book_ids = row.get("book_ids")
    if isinstance(book_ids, list) and row.get("supporting_book_count") != len(set(book_ids)):
        errors.append(f"{path}:{line}: supporting_book_count must match unique book_ids")
    for field in ("member_record_ids", "boundary_conditions", "nearest_neighbor_record_ids"):
        if field in row and not string_list(row.get(field)):
            errors.append(f"{path}:{line}: {field} must be a list of strings")
    for field in ("cluster_level", "label", "shared_operation"):
        if field in row and not nonempty_string(row.get(field)):
            errors.append(f"{path}:{line}: {field} must be non-empty")
    if row.get("merge_decision") not in CLUSTER_DECISIONS:
        errors.append(f"{path}:{line}: unsupported cluster merge_decision")


def validate_qa(row: dict[str, Any], path: Path, line: int, errors: list[str]) -> None:
    add_missing(errors, path, line, row, {"scope", "checks", "gaps", "disputes", "blocked_outputs"})
    if "scope" in row and not nonempty_string(row.get("scope")):
        errors.append(f"{path}:{line}: scope must be non-empty")
    checks = row.get("checks")
    required_checks = {
        "coverage",
        "evidence_traceability",
        "causal_chain",
        "boundary_check",
        "emotion_overlay_reference",
        "cross_book_gate",
    }
    if row.get("schema_version") == 2:
        required_checks.add("faction_structure")
    if not isinstance(checks, dict):
        errors.append(f"{path}:{line}: checks must be an object")
    else:
        add_missing(errors, path, line, checks, required_checks)
        for field in required_checks:
            if field in checks and checks[field] not in QA_STATUS:
                errors.append(f"{path}:{line}: checks.{field} must be PASS/HOLD/FAIL")
    for field in ("gaps", "disputes", "blocked_outputs"):
        if field in row and not isinstance(row.get(field), list):
            errors.append(f"{path}:{line}: {field} must be a list")


def validate_handoff(row: dict[str, Any], path: Path, line: int, errors: list[str]) -> None:
    add_missing(
        errors,
        path,
        line,
        row,
        {"candidate_record_ids", "recommended_action", "decision_points", "evidence_gaps", "forbidden_automatic_actions"},
    )
    if "candidate_record_ids" in row and not string_list(row.get("candidate_record_ids"), allow_empty=False):
        errors.append(f"{path}:{line}: candidate_record_ids must be a non-empty list of strings")
    for field in ("decision_points", "evidence_gaps", "forbidden_automatic_actions"):
        if field in row and not string_list(row.get(field)):
            errors.append(f"{path}:{line}: {field} must be a list of strings")
    if row.get("recommended_action") not in HANDOFF_ACTIONS:
        errors.append(f"{path}:{line}: unsupported recommended_action")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Validate novel-worldbuilding-miner JSONL outputs.")
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
        if len(covered_books) != len(actual_books):
            duplicates = sorted({book for book in covered_books if covered_books.count(book) > 1})
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
