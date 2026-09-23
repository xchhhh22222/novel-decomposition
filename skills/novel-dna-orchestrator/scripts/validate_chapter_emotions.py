#!/usr/bin/env python3
"""Validate one chapter-emotion JSONL overlay and its chapter coverage."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED = {
    "schema_version",
    "record_id",
    "status",
    "book_id",
    "chapter",
    "chapter_ref",
    "chapter_title",
    "evidence_path",
    "source_fingerprint",
    "chapter_role",
    "main_reader_emotion",
    "secondary_reader_emotions",
    "emotion_object",
    "expectation_source",
    "pressure_source",
    "pressure_level",
    "turning_point",
    "payoff_level",
    "visible_payoff_evidence",
    "aftermath",
    "ending_aftertaste",
    "hook_type",
    "promise_opened",
    "promise_paid",
    "plot_lines_advanced",
    "qa_status",
    "confidence",
    "generated_at",
}
STRONG_PAYOFFS = {"阶段小兑现", "本章强兑现", "兑现后余震"}
ROLES = {"立承诺", "蓄压", "加压", "转机", "兑现", "余震", "过渡", "换档"}
PAYOFF_LEVELS = {"无兑现-继续蓄压", "局部兑现", "阶段小兑现", "本章强兑现", "兑现后余震"}
CONFIDENCE = {"HIGH", "MEDIUM", "LOW"}


def parse_range(value: str) -> set[int]:
    start_text, end_text = value.split("-", 1)
    start, end = int(start_text), int(end_text)
    if start < 1 or end < start:
        raise ValueError("expected range must look like 1-120")
    return set(range(start, end + 1))


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("target", type=Path)
    parser.add_argument("--expected-book", required=True)
    parser.add_argument("--expected-range", required=True)
    parser.add_argument("--exclude", default="", help="Comma-separated known missing chapters.")
    parser.add_argument("--allow-nonpass", action="store_true", help="Allow HOLD/FAIL in draft audits; does not satisfy G2.")
    args = parser.parse_args()
    expected = parse_range(args.expected_range)
    excluded = {int(value) for value in args.exclude.split(",") if value.strip()}
    expected -= excluded
    errors: list[str] = []
    chapters: list[int] = []
    record_ids: list[str] = []
    pass_count = 0
    for number, raw in enumerate(args.target.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"line {number}: invalid JSON: {exc}")
            continue
        missing = sorted(key for key in REQUIRED if key not in row)
        if missing:
            errors.append(f"line {number}: missing {', '.join(missing)}")
        chapter = row.get("chapter")
        if row.get("book_id") != args.expected_book:
            errors.append(f"line {number}: book_id must be {args.expected_book}")
        if not isinstance(chapter, int):
            errors.append(f"line {number}: chapter must be an integer")
        else:
            chapters.append(chapter)
        record_id = row.get("record_id")
        if isinstance(record_id, str):
            record_ids.append(record_id)
        if row.get("qa_status") not in {"PASS", "HOLD", "FAIL"}:
            errors.append(f"line {number}: qa_status must be PASS/HOLD/FAIL")
        elif row.get("qa_status") == "PASS":
            pass_count += 1
        elif not args.allow_nonpass:
            errors.append(f"line {number}: non-PASS record does not satisfy G2")
        if row.get("status") not in {"candidate", "active", "deprecated"}:
            errors.append(f"line {number}: status must be candidate/active/deprecated")
        if isinstance(chapter, int) and row.get("book_id"):
            expected_record = f"{row['book_id']}:EMOTION:{chapter:04d}"
            expected_ref = f"{row['book_id']}:CHAPTER:{chapter:04d}"
            if row.get("record_id") != expected_record:
                errors.append(f"line {number}: record_id must be {expected_record}")
            if row.get("chapter_ref") != expected_ref:
                errors.append(f"line {number}: chapter_ref must be {expected_ref}")
        secondary = row.get("secondary_reader_emotions", [])
        if not isinstance(secondary, list) or len(secondary) > 2:
            errors.append(f"line {number}: secondary_reader_emotions allows at most two")
        pressure = row.get("pressure_level")
        if not isinstance(pressure, int) or not 0 <= pressure <= 5:
            errors.append(f"line {number}: pressure_level must be 0-5")
        roles = row.get("chapter_role")
        if not isinstance(roles, list) or not roles or not set(roles).issubset(ROLES):
            errors.append(f"line {number}: chapter_role contains empty or unsupported values")
        if row.get("payoff_level") not in PAYOFF_LEVELS:
            errors.append(f"line {number}: unsupported payoff_level")
        if row.get("confidence") not in CONFIDENCE:
            errors.append(f"line {number}: confidence must be HIGH/MEDIUM/LOW")
        for field in (
            "chapter_title",
            "evidence_path",
            "source_fingerprint",
            "main_reader_emotion",
            "emotion_object",
            "expectation_source",
            "pressure_source",
            "turning_point",
            "aftermath",
            "ending_aftertaste",
            "hook_type",
        ):
            if not isinstance(row.get(field), str) or not row.get(field).strip():
                errors.append(f"line {number}: {field} cannot be empty")
        if row.get("payoff_level") in STRONG_PAYOFFS:
            if not row.get("visible_payoff_evidence"):
                errors.append(f"line {number}: payoff requires visible_payoff_evidence")
            if not row.get("expectation_source"):
                errors.append(f"line {number}: payoff requires expectation_source")
        if row.get("confidence") == "HIGH" and "UNKNOWN" in json.dumps(row, ensure_ascii=False):
            errors.append(f"line {number}: HIGH confidence cannot contain UNKNOWN")
    duplicates = sorted({chapter for chapter in chapters if chapters.count(chapter) > 1})
    duplicate_ids = sorted({record_id for record_id in record_ids if record_ids.count(record_id) > 1})
    actual = set(chapters)
    result = {
        "records": len(chapters),
        "pass_records": pass_count,
        "expected": len(expected),
        "missing_chapters": sorted(expected - actual),
        "unexpected_chapters": sorted(actual - expected),
        "duplicate_chapters": duplicates,
        "duplicate_record_ids": duplicate_ids,
        "errors": errors,
    }
    result["ok"] = not any(
        (result["missing_chapters"], result["unexpected_chapters"], duplicates, duplicate_ids, errors)
    )
    if not args.allow_nonpass and pass_count != len(expected):
        result["errors"].append("PASS records do not cover the expected range")
        result["ok"] = False
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
