#!/usr/bin/env python3
"""Validate V1.6 source routing records before any decomposition writes."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SPECIALTIES = {
    "chapter_emotion",
    "golden_finger",
    "worldbuilding",
    "cultivation_system",
    "character_function",
    "plotline",
    "opening",
    "arc_structure",
    "plot_mechanism",
}
MODES = {"FULL_DNA", "SUPPLEMENTAL_MATERIAL"}
ROLES = {"primary_full_dna", "supplemental_material"}
BOOK_RE = re.compile(r"^BOOK_\d{3,}$")


def load_records(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8-sig")
    try:
        obj = json.loads(text)
        if isinstance(obj, list):
            return obj
        if isinstance(obj, dict):
            return [obj]
        raise ValueError("top-level JSON must be object or array")
    except json.JSONDecodeError:
        out: list[dict[str, Any]] = []
        for line_no, line in enumerate(text.splitlines(), 1):
            if not line.strip():
                continue
            obj = json.loads(line)
            if not isinstance(obj, dict):
                raise ValueError(f"line {line_no}: record must be object")
            out.append(obj)
        return out


def as_set(value: Any, field: str, errors: list[str], where: str) -> set[str]:
    if not isinstance(value, list):
        errors.append(f"{where}.{field} must be a list")
        return set()
    result = {str(x) for x in value if isinstance(x, str) and x.strip()}
    if len(result) != len(value):
        errors.append(f"{where}.{field} must contain unique non-empty strings")
    return result


def validate_record(record: dict[str, Any], index: int) -> list[str]:
    errors: list[str] = []
    where = f"record[{index}]"
    required = {
        "record_type",
        "schema_version",
        "book_id",
        "source_file",
        "source_role",
        "extraction_mode",
        "purpose",
        "target_specialties",
        "derived_views",
        "excluded_specialties",
        "chapter_scope",
        "full_book_dna",
        "known_gaps",
    }
    missing = sorted(required - set(record))
    if missing:
        errors.append(f"{where} missing fields: {', '.join(missing)}")
        return errors

    if record["record_type"] != "source_route":
        errors.append(f"{where}.record_type must be source_route")
    if record["schema_version"] != 1:
        errors.append(f"{where}.schema_version must be 1")
    if not isinstance(record["book_id"], str) or not BOOK_RE.fullmatch(record["book_id"]):
        errors.append(f"{where}.book_id must match BOOK_###")
    if not isinstance(record["source_file"], str) or not record["source_file"].strip():
        errors.append(f"{where}.source_file must be non-empty")
    if record["extraction_mode"] not in MODES:
        errors.append(f"{where}.extraction_mode must be FULL_DNA or SUPPLEMENTAL_MATERIAL")
    if record["source_role"] not in ROLES:
        errors.append(f"{where}.source_role invalid")
    if not isinstance(record["chapter_scope"], str) or not record["chapter_scope"].strip():
        errors.append(f"{where}.chapter_scope must be non-empty")
    if not isinstance(record["full_book_dna"], bool):
        errors.append(f"{where}.full_book_dna must be boolean")

    purpose = as_set(record["purpose"], "purpose", errors, where)
    target = as_set(record["target_specialties"], "target_specialties", errors, where)
    excluded = as_set(record["excluded_specialties"], "excluded_specialties", errors, where)
    as_set(record["derived_views"], "derived_views", errors, where)
    if not isinstance(record["known_gaps"], list):
        errors.append(f"{where}.known_gaps must be a list")
    if not purpose:
        errors.append(f"{where}.purpose cannot be empty")

    unknown_target = sorted(target - SPECIALTIES)
    unknown_excluded = sorted(excluded - SPECIALTIES)
    if unknown_target:
        errors.append(f"{where}.target_specialties unknown: {', '.join(unknown_target)}")
    if unknown_excluded:
        errors.append(f"{where}.excluded_specialties unknown: {', '.join(unknown_excluded)}")
    overlap = sorted(target & excluded)
    if overlap:
        errors.append(f"{where}: target/excluded overlap: {', '.join(overlap)}")

    mode = record["extraction_mode"]
    if mode == "FULL_DNA":
        if record["source_role"] != "primary_full_dna":
            errors.append(f"{where}: FULL_DNA requires source_role=primary_full_dna")
        if record["full_book_dna"] is not True:
            errors.append(f"{where}: FULL_DNA requires full_book_dna=true")
        if target != SPECIALTIES:
            errors.append(f"{where}: FULL_DNA target_specialties must cover all 9 specialties")
        if excluded:
            errors.append(f"{where}: FULL_DNA excluded_specialties must be empty")
    elif mode == "SUPPLEMENTAL_MATERIAL":
        if record["source_role"] != "supplemental_material":
            errors.append(f"{where}: SUPPLEMENTAL_MATERIAL requires source_role=supplemental_material")
        if record["full_book_dna"] is not False:
            errors.append(f"{where}: SUPPLEMENTAL_MATERIAL requires full_book_dna=false")
        if not target:
            errors.append(f"{where}: supplemental target_specialties cannot be empty")
        if target == SPECIALTIES:
            errors.append(f"{where}: supplemental target_specialties must be a true subset of 9 specialties")
        if target | excluded != SPECIALTIES:
            missing_coverage = sorted(SPECIALTIES - (target | excluded))
            errors.append(f"{where}: target + excluded must cover all specialties; missing {', '.join(missing_coverage)}")

    return errors


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Validate V1.6 source_routes JSON/JSONL.")
    parser.add_argument("routes", type=Path)
    args = parser.parse_args()

    try:
        records = load_records(args.routes)
    except Exception as exc:
        print(json.dumps({"ok": False, "errors": [str(exc)]}, ensure_ascii=False, indent=2))
        return 1

    errors: list[str] = []
    seen: set[str] = set()
    for i, record in enumerate(records):
        errors.extend(validate_record(record, i))
        bid = record.get("book_id")
        if isinstance(bid, str):
            if bid in seen:
                errors.append(f"duplicate book_id in routing file: {bid}")
            seen.add(bid)

    result = {
        "gate": "SOURCE_ROUTING_GATE_V1_6",
        "status": "PASS" if not errors else "FAIL",
        "records": len(records),
        "errors": errors,
        "ok": not errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
