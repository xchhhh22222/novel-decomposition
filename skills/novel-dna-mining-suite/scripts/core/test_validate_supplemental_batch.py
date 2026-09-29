#!/usr/bin/env python3
"""Regression tests for V1.6.2 supplemental batch consistency gates."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

VALIDATOR = Path(__file__).with_name("validate_supplemental_batch.py")


def ability(book: str, n: int, qa: str) -> dict:
    return {
        "record_type": "derived_asset",
        "schema_version": 2,
        "record_id": f"DA:ABILITY:{book}:{n:03d}",
        "status": "candidate",
        "book_id": book,
        "view": "ability_assets",
        "name_in_book": f"A{n}",
        "ability_core": "x",
        "trigger": "x",
        "input": "x",
        "operation": "x",
        "output": "x",
        "limit": "x",
        "cost": "x",
        "growth": "x",
        "first_showcase": "x",
        "appeal_hook": "x",
        "immediate_fantasy": "x",
        "combat_value": "x",
        "social_value": "x",
        "plot_generation": "x",
        "combination_interfaces": "x",
        "counterplay": "x",
        "fatigue_risk": "x",
        "evidence_refs": [f"{book}:CHAPTER:0001"],
        "unknowns": ["hold"] if qa == "HOLD" else [],
        "confidence": "LOW" if qa == "HOLD" else "MEDIUM",
        "qa_status": qa,
    }


def build(
    root: Path,
    *,
    qas: list[str],
    manifest_status: str,
    batch_status: str | None = None,
    route_views: list[str] | None = None,
    extra_view_file: bool = False,
    derived_hold_records: int | None = None,
) -> None:
    book = "BOOK_010"
    batch = root / "batch" / "TEST"
    batch.mkdir(parents=True)
    b = root / "books" / book
    d = b / "02_金手指" / "derived"
    d.mkdir(parents=True)

    rows = [ability(book, i + 1, qa) for i, qa in enumerate(qas)]
    (d / "ability_assets.jsonl").write_text(
        "\n".join(json.dumps(x, ensure_ascii=False) for x in rows) + "\n",
        encoding="utf-8",
    )
    if extra_view_file:
        extra = b / "04_修炼体系" / "derived"
        extra.mkdir(parents=True)
        (extra / "combat_asset_inventory.json").write_text(
            json.dumps({"book_id": book, "characters": []}, ensure_ascii=False),
            encoding="utf-8",
        )

    route = {
        "record_type": "source_route",
        "schema_version": 1,
        "book_id": book,
        "source_file": "book.txt",
        "source_role": "supplemental_material",
        "extraction_mode": "SUPPLEMENTAL_MATERIAL",
        "purpose": ["ability_material"],
        "target_specialties": ["golden_finger"],
        "derived_views": route_views if route_views is not None else ["ability_assets"],
        "excluded_specialties": [
            "chapter_emotion","worldbuilding","cultivation_system","character_function",
            "plotline","opening","arc_structure","plot_mechanism"
        ],
        "chapter_scope": "FULL_SOURCE_SCAN",
        "full_book_dna": False,
        "known_gaps": [],
    }
    (batch / "source_routes.jsonl").write_text(
        json.dumps(route, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    manifest = {
        "book_id": book,
        "status": manifest_status,
        "derived_views": ["ability_assets"] + (["combat_asset_inventory"] if extra_view_file else []),
        "outputs": {
            "derived_views": [
                {"view": "ability_assets", "output": "02_金手指/derived/ability_assets.jsonl", "records": len(rows)}
            ]
        },
    }
    (b / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    actual_holds = sum(1 for qa in qas if qa == "HOLD")
    (batch / "batch-status.json").write_text(
        json.dumps(
            {
                "books": {book: batch_status or manifest_status},
                "derived_totals": {
                    "ability_assets": len(rows),
                    "dungeon_rule_assets": 0,
                    "relationship_engine_assets": 0,
                    "charismatic_antagonist_assets": 0,
                    "combat_expression_assets": 0,
                },
                "derived_hold_records": actual_holds if derived_hold_records is None else derived_hold_records,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def run_case(root: Path) -> tuple[int, dict]:
    p = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--root",
            str(root),
            "--batch-dir",
            "batch/TEST",
            "--books",
            "BOOK_010",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return p.returncode, json.loads(p.stdout)


def main() -> int:
    failures: list[str] = []

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        build(root, qas=["PASS", "HOLD"], manifest_status="COMPLETE_SUPPLEMENTAL_SOURCE_WITH_HOLDS")
        code, result = run_case(root)
        if code != 0 or result["status"] != "PASS" or not result["full_recluster_ready"]:
            failures.append("mixed PASS/HOLD should validate and allow PASS-only clustering")
        per_view = result["cluster_eligibility_gate"]["per_view"]["ability_assets"]
        if per_view["eligible"] != 1 or per_view["held"] != 1:
            failures.append("mixed eligibility counts wrong")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        build(root, qas=["HOLD"], manifest_status="COMPLETE_SUPPLEMENTAL_SOURCE_WITH_HOLDS")
        code, result = run_case(root)
        if code != 0 or result["full_recluster_ready"]:
            failures.append("all-HOLD view should validate structurally but block full recluster")
        if "ability_assets" not in result["cluster_eligibility_gate"]["blocked_views_zero_eligible"]:
            failures.append("all-HOLD view missing from blocked views")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        build(root, qas=["HOLD"], manifest_status="COMPLETE_SUPPLEMENTAL_SOURCE")
        code, result = run_case(root)
        if code == 0 or result["completion_status_consistency_gate"]["status"] != "FAIL":
            failures.append("manifest COMPLETE with HOLD must fail")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        build(
            root,
            qas=["PASS"],
            manifest_status="COMPLETE_SUPPLEMENTAL_SOURCE",
            extra_view_file=True,
        )
        code, result = run_case(root)
        if code == 0 or result["route_output_consistency_gate"]["status"] != "FAIL":
            failures.append("unrouted derived file must fail")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        build(
            root,
            qas=["PASS"],
            manifest_status="COMPLETE_SUPPLEMENTAL_SOURCE",
            batch_status="COMPLETE_SUPPLEMENTAL_SOURCE_WITH_HOLDS",
        )
        code, result = run_case(root)
        if code == 0 or result["completion_status_consistency_gate"]["status"] != "FAIL":
            failures.append("batch/manifest status mismatch must fail")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        build(
            root,
            qas=["PASS", "HOLD"],
            manifest_status="COMPLETE_SUPPLEMENTAL_SOURCE_WITH_HOLDS",
            derived_hold_records=99,
        )
        code, result = run_case(root)
        if code == 0 or result["batch_summary_consistency_gate"]["status"] != "FAIL":
            failures.append("stale derived_hold_records must fail")

    print(json.dumps({"ok": not failures, "cases": 6, "failures": failures}, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
