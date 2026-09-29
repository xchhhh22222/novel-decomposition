#!/usr/bin/env python3
"""Regression tests for V1.6.1 derived-material validator."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

VALIDATOR = Path(__file__).with_name("validate_derived_materials.py")


def common(view: str, rid: str, book: str) -> dict:
    return {
        "record_type": "derived_asset",
        "schema_version": 2,
        "record_id": rid,
        "status": "candidate",
        "book_id": book,
        "view": view,
        "evidence_refs": [f"{book}:CHAPTER:0001"],
        "unknowns": [],
        "confidence": "MEDIUM",
        "qa_status": "PASS",
    }


def ability(book: str) -> dict:
    row = common("ability_assets", f"DA:ABILITY:{book}:001", book)
    for key in [
        "name_in_book","ability_core","trigger","input","operation","output","limit","cost",
        "growth","first_showcase","appeal_hook","immediate_fantasy","combat_value",
        "social_value","plot_generation","combination_interfaces","counterplay","fatigue_risk",
    ]:
        row[key] = f"{key} value"
    return row


def combat(book: str) -> dict:
    row = common("combat_expression_assets", f"DA:COMBAT:{book}:001", book)
    for key in [
        "asset_name","function_slot","trigger","input","operation","range","action_pattern",
        "output","cost","limit","counterplay","visual_expression","combat_role",
        "combination_interface","compatible_system","user_archetype",
    ]:
        row[key] = f"{key} value"
    return row


def write_fixture(root: Path, *, bad_alias: bool = False, nested: bool = False, bad_ref: bool = False) -> None:
    book = "BOOK_010"
    b = root / "books" / book
    (b / "02_金手指" / "derived").mkdir(parents=True)
    (b / "04_修炼体系" / "derived").mkdir(parents=True)

    a = ability(book)
    if bad_alias:
        a["core"] = a["ability_core"]
    if bad_ref:
        a["evidence_refs"] = ["ch1-10"]
    (b / "02_金手指" / "derived" / "ability_assets.jsonl").write_text(
        json.dumps(a, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    c = combat(book)
    assets = [[c]] if nested else [c]
    collection = {
        "schema_version": 2,
        "record_type": "derived_asset_collection",
        "book_id": book,
        "view": "combat_expression_assets",
        "asset_count": 1,
        "assets": assets,
    }
    (b / "04_修炼体系" / "derived" / "combat_expression_assets.json").write_text(
        json.dumps(collection, ensure_ascii=False), encoding="utf-8"
    )

    manifest = {
        "outputs": {
            "derived_views": [
                {"view": "ability_assets", "records": 1},
                {"view": "combat_expression_assets", "records": 1},
            ]
        }
    }
    (b / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")


def run_case(**kwargs) -> bool:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        write_fixture(root, **kwargs)
        p = subprocess.run(
            [sys.executable, str(VALIDATOR), "--root", str(root), "--books", "BOOK_010"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return p.returncode == 0


def main() -> int:
    cases = [
        ("valid", {}, True),
        ("legacy alias rejected", {"bad_alias": True}, False),
        ("nested combat assets rejected", {"nested": True}, False),
        ("range evidence rejected", {"bad_ref": True}, False),
    ]
    failures = [name for name, args, expected in cases if run_case(**args) != expected]
    print(json.dumps({"ok": not failures, "cases": len(cases), "failures": failures}, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
