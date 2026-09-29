#!/usr/bin/env python3
"""Validate V1.6.3 combat-expression semantic readiness.

This gate is intentionally stricter than the generic derived-material schema gate.
It does not judge whether prose is "good"; it enforces that PASS means the record
is structurally comparable enough for cross-book clustering.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

UNKNOWN = "UNKNOWN"
CORE_FIELDS = (
    "asset_name",
    "function_slot",
    "trigger",
    "operation",
    "action_pattern",
    "output",
    "combat_role",
    "visual_expression",
)
CONSTRAINT_FIELDS = ("cost", "limit", "counterplay")
COMBAT_FIELDS = (
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
)
NONCANONICAL_UNKNOWN_PREFIXES = (
    "UNKNOWN——",
    "UNKNOWN—",
    "UNKNOWN（",
    "UNKNOWN(",
    "未知",
    "不适用/未知",
    "不适用（未知",
)
ABSENCE_ONLY_RE = re.compile(
    r"^(?:无|没有|无需|无直接代价|无直接消耗).*"
    r"(?:原文未|未展示|未描述|未明示|未给出|未量化|未见)"
)


def load_collection(path: Path) -> list[dict[str, Any]]:
    obj = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(obj, dict):
        raise ValueError(f"{path}: top level must be an object")
    assets = obj.get("assets")
    if not isinstance(assets, list) or any(not isinstance(x, dict) for x in assets):
        raise ValueError(f"{path}: assets must be a flat list of objects")
    return assets


def unknown_like(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    text = value.strip()
    return any(text.startswith(prefix) for prefix in NONCANONICAL_UNKNOWN_PREFIXES)


def is_unknown(value: Any) -> bool:
    return isinstance(value, str) and value.strip() == UNKNOWN


def has_field_reason(unknowns: Any, field: str) -> bool:
    if not isinstance(unknowns, list):
        return False
    prefixes = (f"{field}：", f"{field}:", f"{field} ")
    return any(
        isinstance(item, str) and item.strip().startswith(prefixes)
        for item in unknowns
    )


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Validate V1.6.3 combat semantic PASS/HOLD readiness."
    )
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--books", required=True, help="comma-separated BOOK IDs")
    args = parser.parse_args()

    books = [x.strip() for x in args.books.split(",") if x.strip()]
    errors: list[str] = []
    per_book: dict[str, dict[str, int]] = {}
    pass_ids: list[str] = []
    hold_ids: list[str] = []

    for book_id in books:
        path = (
            args.root
            / "books"
            / book_id
            / "04_修炼体系"
            / "derived"
            / "combat_expression_assets.json"
        )
        if not path.exists():
            continue

        try:
            rows = load_collection(path)
        except Exception as exc:
            errors.append(str(exc))
            continue

        pass_count = 0
        hold_count = 0
        for index, row in enumerate(rows, 1):
            rid = row.get("record_id")
            where = f"{path} record[{index}] {rid!r}"

            for field in COMBAT_FIELDS:
                value = row.get(field)
                if unknown_like(value):
                    errors.append(
                        f"{where}.{field}: unknown values must be exactly 'UNKNOWN'; "
                        "move the explanation into unknowns[]"
                    )

            unknowns = row.get("unknowns")
            if not isinstance(unknowns, list):
                errors.append(f"{where}.unknowns must be a list")
                unknowns = []

            for item in unknowns:
                if not isinstance(item, str):
                    continue
                normalized = item.strip().upper()
                if normalized.startswith("EVIDENCE_CORRECTION") or "OLD_REF=" in normalized or "NEW_REF=" in normalized:
                    errors.append(
                        f"{where}.unknowns: evidence-correction audit logs do not belong in unknowns[]"
                    )

            literal_unknown_fields = [
                field for field in COMBAT_FIELDS if is_unknown(row.get(field))
            ]
            for field in literal_unknown_fields:
                if not has_field_reason(unknowns, field):
                    errors.append(
                        f"{where}.{field}: literal UNKNOWN requires an unknowns[] entry "
                        f"starting with '{field}：' or '{field}:'"
                    )

            for field in CONSTRAINT_FIELDS:
                value = row.get(field)
                if isinstance(value, str) and ABSENCE_ONLY_RE.search(value.strip()):
                    errors.append(
                        f"{where}.{field}: absence of evidence cannot prove 'none'; "
                        "use literal UNKNOWN unless source text positively supports absence/non-applicability"
                    )

            qa_status = row.get("qa_status")
            if qa_status == "PASS":
                pass_count += 1
                if isinstance(rid, str):
                    pass_ids.append(rid)

                missing_core = [field for field in CORE_FIELDS if is_unknown(row.get(field))]
                if missing_core:
                    errors.append(
                        f"{where}: PASS forbidden with UNKNOWN core fields: "
                        + ", ".join(missing_core)
                    )

                if all(is_unknown(row.get(field)) for field in CONSTRAINT_FIELDS):
                    errors.append(
                        f"{where}: PASS requires at least one evidenced constraint among "
                        "cost/limit/counterplay; all three are UNKNOWN"
                    )

                if unknowns and row.get("confidence") == "HIGH":
                    errors.append(
                        f"{where}: PASS with non-empty unknowns cannot use confidence=HIGH"
                    )

            elif qa_status == "HOLD":
                hold_count += 1
                if isinstance(rid, str):
                    hold_ids.append(rid)
            else:
                errors.append(f"{where}.qa_status must be PASS or HOLD")

        per_book[book_id] = {
            "records": len(rows),
            "pass": pass_count,
            "hold": hold_count,
        }

    result = {
        "gate": "COMBAT_SEMANTIC_GATE_V1_6_3",
        "status": "PASS" if not errors else "FAIL",
        "books": books,
        "per_book": per_book,
        "pass_record_ids": pass_ids,
        "hold_record_ids": hold_ids,
        "records": len(pass_ids) + len(hold_ids),
        "pass": len(pass_ids),
        "hold": len(hold_ids),
        "errors": errors,
        "ok": not errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
