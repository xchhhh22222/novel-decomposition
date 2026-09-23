#!/usr/bin/env python3
"""Validate JSONL outputs from novel-golden-finger-miner."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


COMMON = {"schema_version", "record_type", "record_id", "status", "evidence_refs", "confidence"}
PER_BOOK = {
    "book_id",
    "title",
    "chapters_covered",
    "mechanic_name_in_book",
    "normalized_category",
    "normalized_archetype",
    "core_formula",
    "ownership",
    "activation_conditions",
    "hard_limits",
    "costs",
    "failure_modes",
    "initial_capabilities",
    "growth_stages",
    "system_growth_mode",
    "resource_loop",
    "world_dependencies",
    "system_interfaces",
    "plot_engines",
    "reader_promise",
    "first_reveal",
    "first_validation",
    "first_strong_payoff",
    "emotion_pattern",
    "emotion_evidence_mode",
    "payoff_evidence_types",
    "fatigue_risks",
    "refresh_methods_observed",
    "qa_sources",
    "qa_status",
    "source_numbering_notes",
    "unknowns",
}
GAP = {"book_id", "reason", "known_evidence", "unknowns"}
CLUSTER = {
    "cluster_id",
    "category",
    "archetype",
    "core_formula",
    "book_ids",
    "source_count",
    "nearest_existing",
    "comparison_ids",
    "result_ids",
    "similarity_score",
    "similarity_decision",
    "emotion_pattern",
    "unknowns",
}
CORE_KEYS = {"input", "process", "output"}
EVENT_KEYS = {"chapter_ref", "event_order"}
SCORE_KEYS = {"input", "process", "output", "limits_costs", "growth", "resource_loop", "emotion_payoff", "total", "critical_override"}
DECISIONS = {"MERGE", "SUBTYPE", "KEEP_SEPARATE", "NEW", "SPLIT", "HOLD"}
CONFIDENCE = {"HIGH", "MEDIUM", "LOW"}
SCORE_DIMENSIONS = {"input", "process", "output", "limits_costs", "growth", "resource_loop", "emotion_payoff"}
PER_BOOK_LIST_FIELDS = {
    "activation_conditions",
    "hard_limits",
    "costs",
    "failure_modes",
    "initial_capabilities",
    "growth_stages",
    "world_dependencies",
    "system_interfaces",
    "plot_engines",
    "payoff_evidence_types",
    "fatigue_risks",
    "refresh_methods_observed",
    "qa_sources",
    "source_numbering_notes",
    "unknowns",
}


def iter_jsonl(target: Path):
    paths = sorted(target.rglob("*.jsonl")) if target.is_dir() else [target]
    for path in paths:
        for number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
            if raw.strip():
                yield path, number, raw


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("target", type=Path)
    parser.add_argument("--expected-books", required=True, help="Comma-separated BOOK IDs for this batch.")
    args = parser.parse_args()
    expected_books = {value.strip() for value in args.expected_books.split(",") if value.strip()}
    if not expected_books:
        parser.error("--expected-books cannot be empty")
    errors: list[str] = []
    records = 0
    record_ids: set[str] = set()
    covered_books: list[str] = []
    for path, number, raw in iter_jsonl(args.target):
        records += 1
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}:{number}: invalid JSON: {exc}")
            continue
        kind = row.get("record_type")
        required = COMMON | (PER_BOOK if kind == "per_book" else CLUSTER if kind == "cluster" else GAP if kind == "gap" else set())
        if kind not in {"per_book", "cluster", "gap"}:
            errors.append(f"{path}:{number}: unsupported record_type={kind!r}")
            continue
        missing = sorted(key for key in required if key not in row)
        if missing:
            errors.append(f"{path}:{number}: missing {', '.join(missing)}")
        record_id = row.get("record_id")
        if record_id in record_ids:
            errors.append(f"{path}:{number}: duplicate record_id={record_id}")
        elif isinstance(record_id, str):
            record_ids.add(record_id)
        if row.get("status") != "candidate":
            errors.append(f"{path}:{number}: specialist outputs must remain candidate")
        if row.get("confidence") not in CONFIDENCE:
            errors.append(f"{path}:{number}: confidence must be HIGH/MEDIUM/LOW")
        if kind in {"per_book", "cluster"}:
            formula = row.get("core_formula", {})
            if not isinstance(formula, dict) or not CORE_KEYS.issubset(formula):
                errors.append(f"{path}:{number}: core_formula requires input/process/output")
        if not row.get("evidence_refs"):
            errors.append(f"{path}:{number}: evidence_refs is empty")
        if row.get("confidence") == "HIGH" and row.get("unknowns"):
            errors.append(f"{path}:{number}: HIGH confidence cannot contain unknowns")
        if kind == "per_book":
            covered_books.append(str(row.get("book_id")))
            for field in ("book_id", "title", "chapters_covered", "mechanic_name_in_book", "normalized_category", "normalized_archetype", "ownership", "system_growth_mode", "resource_loop", "reader_promise", "emotion_pattern"):
                if not isinstance(row.get(field), str) or not row.get(field).strip():
                    errors.append(f"{path}:{number}: {field} cannot be empty")
            for field in PER_BOOK_LIST_FIELDS:
                if not isinstance(row.get(field), list):
                    errors.append(f"{path}:{number}: {field} must be a list")
            if row.get("qa_status") not in {"PASS", "HOLD", "FAIL"}:
                errors.append(f"{path}:{number}: qa_status must be PASS/HOLD/FAIL")
            for field in ("first_reveal", "first_validation", "first_strong_payoff"):
                event = row.get(field, {})
                if not isinstance(event, dict) or not EVENT_KEYS.issubset(event):
                    errors.append(f"{path}:{number}: {field} requires chapter_ref/event_order")
                elif not str(event.get("chapter_ref", "")).startswith(f"{row.get('book_id')}:CHAPTER:"):
                    errors.append(f"{path}:{number}: {field} chapter_ref uses another book")
            reveal = row.get("first_reveal")
            if not isinstance(reveal, dict) or not reveal.get("function"):
                errors.append(f"{path}:{number}: first_reveal requires function")
            for field in ("first_validation", "first_strong_payoff"):
                event = row.get(field)
                if not isinstance(event, dict) or not event.get("visible_evidence"):
                    errors.append(f"{path}:{number}: {field} requires visible_evidence")
            if row.get("emotion_evidence_mode") not in {"overlay", "provisional"}:
                errors.append(f"{path}:{number}: emotion_evidence_mode must be overlay/provisional")
            if row.get("emotion_evidence_mode") == "provisional" and row.get("confidence") == "HIGH":
                errors.append(f"{path}:{number}: provisional emotion evidence cannot be HIGH confidence")
        if kind == "gap":
            covered_books.append(str(row.get("book_id")))
            if row.get("confidence") != "LOW":
                errors.append(f"{path}:{number}: gap records must be LOW confidence")
            if not row.get("reason"):
                errors.append(f"{path}:{number}: gap reason cannot be empty")
        if kind == "cluster":
            book_ids = row.get("book_ids", [])
            if not isinstance(book_ids, list) or not book_ids:
                errors.append(f"{path}:{number}: book_ids must be a non-empty list")
            elif row.get("source_count") != len(set(book_ids)):
                errors.append(f"{path}:{number}: source_count does not match unique book_ids")
        if kind == "cluster":
            score = row.get("similarity_score", {})
            if not isinstance(score, dict) or not SCORE_KEYS.issubset(score):
                errors.append(f"{path}:{number}: similarity_score is incomplete")
            elif score.get("total") != sum(score.get(key, 0) for key in SCORE_KEYS - {"total", "critical_override"}):
                errors.append(f"{path}:{number}: similarity_score total is incorrect")
            if isinstance(score, dict):
                for dimension in SCORE_DIMENSIONS:
                    value = score.get(dimension)
                    if not isinstance(value, int) or not 0 <= value <= 2:
                        errors.append(f"{path}:{number}: similarity_score.{dimension} must be 0-2")
            if row.get("similarity_decision") not in DECISIONS:
                errors.append(f"{path}:{number}: unsupported similarity_decision")
            comparisons = row.get("comparison_ids", [])
            results = row.get("result_ids", [])
            nearest = row.get("nearest_existing", [])
            if not isinstance(comparisons, list) or not comparisons:
                errors.append(f"{path}:{number}: comparison_ids cannot be empty")
            if not isinstance(nearest, list) or not nearest:
                errors.append(f"{path}:{number}: nearest_existing cannot be empty; use NONE explicitly if needed")
            if not isinstance(results, list) or not results:
                errors.append(f"{path}:{number}: result_ids cannot be empty")
            decision = row.get("similarity_decision")
            critical_override = score.get("critical_override", "") if isinstance(score, dict) else ""
            if decision in {"KEEP_SEPARATE", "SPLIT"}:
                if not isinstance(comparisons, list) or len(set(comparisons)) < 2:
                    errors.append(f"{path}:{number}: {decision} requires at least two comparison_ids")
                if not isinstance(results, list) or len(set(results)) < 2:
                    errors.append(f"{path}:{number}: {decision} requires at least two result_ids")
                if not str(critical_override).strip():
                    errors.append(f"{path}:{number}: {decision} requires critical_override")
            total = score.get("total") if isinstance(score, dict) else None
            if isinstance(total, int):
                contradicts_band = (total >= 11 and decision in {"KEEP_SEPARATE", "NEW"}) or (total <= 6 and decision in {"MERGE", "SUBTYPE"})
                if contradicts_band and not str(critical_override).strip():
                    errors.append(f"{path}:{number}: decision contradicts score band without critical_override")
    duplicates = sorted({book_id for book_id in covered_books if covered_books.count(book_id) > 1})
    if duplicates:
        errors.append(f"duplicate per_book/gap coverage: {', '.join(duplicates)}")
    actual_books = set(covered_books)
    missing_books = sorted(expected_books - actual_books)
    unexpected_books = sorted(actual_books - expected_books)
    if missing_books:
        errors.append(f"missing target books: {', '.join(missing_books)}")
    if unexpected_books:
        errors.append(f"unexpected books: {', '.join(unexpected_books)}")
    result = {
        "records": records,
        "covered_books": sorted(actual_books),
        "missing_books": missing_books,
        "unexpected_books": unexpected_books,
        "errors": errors,
        "ok": not errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
