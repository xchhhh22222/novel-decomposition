#!/usr/bin/env python3
"""Regression tests for V1.6.3 combat semantic gate."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

VALIDATOR = Path(__file__).with_name("validate_combat_semantics.py")


def record(*, qa="PASS", cost="有明确消耗", limit="有明确限制", counterplay="有明确反制", unknowns=None):
    return {
        "record_type": "derived_asset",
        "schema_version": 2,
        "record_id": "DA:COMBAT:BOOK_010:001",
        "status": "candidate",
        "book_id": "BOOK_010",
        "view": "combat_expression_assets",
        "asset_name": "测试战斗机制",
        "function_slot": "rule_counter",
        "trigger": "触发条件",
        "input": "输入",
        "operation": "运作机制",
        "range": "中距离",
        "action_pattern": "动作链",
        "output": "战斗结果",
        "cost": cost,
        "limit": limit,
        "counterplay": counterplay,
        "visual_expression": "视觉表达",
        "combat_role": "攻坚",
        "combination_interface": "组合接口",
        "compatible_system": "兼容体系",
        "user_archetype": "角色类型",
        "evidence_refs": ["BOOK_010:CHAPTER:0001"],
        "unknowns": unknowns or [],
        "confidence": "MEDIUM",
        "qa_status": qa,
    }


def run(row: dict) -> tuple[int, dict]:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        d = root / "books" / "BOOK_010" / "04_修炼体系" / "derived"
        d.mkdir(parents=True)
        payload = {
            "schema_version": 2,
            "record_type": "derived_asset_collection",
            "book_id": "BOOK_010",
            "view": "combat_expression_assets",
            "asset_count": 1,
            "assets": [row],
        }
        (d / "combat_expression_assets.json").write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8"
        )
        p = subprocess.run(
            [sys.executable, str(VALIDATOR), "--root", str(root), "--books", "BOOK_010"],
            capture_output=True, text=True, encoding="utf-8"
        )
        return p.returncode, json.loads(p.stdout)


def main() -> int:
    failures: list[str] = []

    cases = []

    cases.append(("valid pass", record(), True))

    bad = record(cost="UNKNOWN——原文未展示代价", unknowns=["cost：原文未展示代价"])
    cases.append(("prefixed UNKNOWN rejected", bad, False))

    bad = record(cost="UNKNOWN", limit="UNKNOWN", counterplay="UNKNOWN",
                 unknowns=["cost：未知", "limit：未知", "counterplay：未知"])
    cases.append(("PASS all constraints UNKNOWN rejected", bad, False))

    bad = record()
    bad["trigger"] = "UNKNOWN"
    bad["unknowns"] = ["trigger：原文未能确认"]
    cases.append(("PASS core UNKNOWN rejected", bad, False))

    bad = record(cost="无——原文未展示使用代价")
    cases.append(("absence-only inference rejected", bad, False))

    bad = record(unknowns=["EVIDENCE_CORRECTION：old_ref=A new_ref=B"])
    cases.append(("evidence audit log rejected from unknowns", bad, False))

    good_hold = record(
        qa="HOLD",
        cost="UNKNOWN",
        limit="UNKNOWN",
        counterplay="UNKNOWN",
        unknowns=["cost：未知", "limit：未知", "counterplay：未知"],
    )
    cases.append(("HOLD may keep all constraints UNKNOWN", good_hold, True))

    for name, row, expected in cases:
        code, result = run(row)
        actual = code == 0 and result.get("status") == "PASS"
        if actual != expected:
            failures.append(name)

    print(json.dumps({"ok": not failures, "cases": len(cases), "failures": failures}, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
