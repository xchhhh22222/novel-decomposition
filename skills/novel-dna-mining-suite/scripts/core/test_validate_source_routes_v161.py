#!/usr/bin/env python3
"""Regression tests for V1.6.1 source-route validator."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

VALIDATOR = Path(__file__).with_name("validate_source_routes.py")
ALL = [
    "chapter_emotion",
    "golden_finger",
    "worldbuilding",
    "cultivation_system",
    "character_function",
    "plotline",
    "opening",
    "arc_structure",
    "plot_mechanism",
]


def base() -> dict:
    target = ["golden_finger", "cultivation_system", "plot_mechanism"]
    return {
        "record_type": "source_route",
        "schema_version": 1,
        "book_id": "BOOK_010",
        "source_file": "book.txt",
        "source_role": "supplemental_material",
        "extraction_mode": "SUPPLEMENTAL_MATERIAL",
        "purpose": ["ability_material"],
        "target_specialties": target,
        "derived_views": ["ability_assets", "combat_expression_assets"],
        "excluded_specialties": [x for x in ALL if x not in target],
        "chapter_scope": "FULL_SOURCE_SCAN",
        "full_book_dna": False,
        "known_gaps": [],
    }


def run(payload: dict) -> bool:
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "routes.jsonl"
        path.write_text(json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8")
        p = subprocess.run(
            [sys.executable, str(VALIDATOR), str(path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return p.returncode == 0


def main() -> int:
    valid = base()
    deprecated = base()
    deprecated["derived_views"] = ["relationship_engine"]
    unknown = base()
    unknown["derived_views"] = ["made_up_view"]
    cases = [
        ("valid", valid, True),
        ("deprecated relationship alias rejected", deprecated, False),
        ("unknown derived view rejected", unknown, False),
    ]
    failures = [name for name, payload, expected in cases if run(payload) != expected]
    print(json.dumps({"ok": not failures, "cases": len(cases), "failures": failures}, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
