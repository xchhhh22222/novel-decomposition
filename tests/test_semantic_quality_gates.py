#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "novel-chapter-emotion-miner" / "scripts" / "audit_semantics.py"
FIXTURES = json.loads((ROOT / "tests" / "fixtures" / "semantic_qa_cases.json").read_text(encoding="utf-8"))


def load_module():
    spec = importlib.util.spec_from_file_location("semantic_qa", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def review(chapters: int, failure: int | None = None) -> dict:
    count = max(10, (chapters + 9) // 10)
    selected = list(range(1, min(chapters, count) + 1))
    if chapters not in selected:
        selected.append(chapters)
    return {
        "reviewer": "SOL",
        "opening_window_end": min(3, chapters),
        "arc_turn_chapters": [min(3, chapters)],
        "samples": [
            {"chapter": chapter, "result": "FAIL" if chapter == failure else "PASS", "note": "manual comparison"}
            for chapter in selected
        ],
    }


def base_row(chapter: int) -> dict:
    return {
        "chapter": chapter,
        "chapter_title": f"标题{chapter}",
        "emotion_object": f"读者关心第{chapter}次选择能否改变目标",
        "expectation_source": f"前一阶段留下的目标{chapter}尚未解决",
        "pressure_source": f"规则门槛{chapter}限制当前行动",
        "turning_point": f"人物在节点{chapter}主动更换执行路径",
        "visible_payoff_evidence": [f"旁观者确认结果{chapter}已经生效"],
        "aftermath": f"行动权限{chapter}发生可见变化",
        "ending_aftertaste": f"新的风险{chapter}迫使下一步重新选择",
        "hook_type": "风险升级",
        "notes": "依据完整正文提炼",
    }


class SemanticQualityGateTests(unittest.TestCase):
    def run_audit(self, rows: list[dict], endings: list[str], review_data: dict) -> dict:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            emotion = root / "emotion.jsonl"
            source = root / "source.txt"
            manual = root / "review.json"
            emotion.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
            source.write_text("\n\n".join(f"第{i}章 标题{i}\n正文内容。\n{ending}" for i, ending in enumerate(endings, 1)), encoding="utf-8")
            manual.write_text(json.dumps(review_data, ensure_ascii=False), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), str(emotion), "--source-file", str(source), "--source-review", str(manual)],
                text=True,
                encoding="utf-8",
                capture_output=True,
            )
            return json.loads(completed.stdout)

    def test_raw_ending_copied_into_six_fields_fails(self):
        case = FIXTURES["raw_ending_extraction"]
        rows = []
        for chapter in range(1, case["chapters"] + 1):
            row = base_row(chapter)
            for field in ("emotion_object", "pressure_source", "turning_point", "visible_payoff_evidence", "aftermath", "ending_aftertaste"):
                row[field] = [case["ending"]] if field == "visible_payoff_evidence" else f"正文结尾证据：{case['ending']}"
            rows.append(row)
        result = self.run_audit(rows, [case["ending"]] * case["chapters"], review(case["chapters"]))
        self.assertEqual(result["gates"][case["expected_gate"]], case["expected_status"])

    def test_normalized_template_skeleton_fails(self):
        case = FIXTURES["normalized_template"]
        rows = []
        for chapter in range(1, case["chapters"] + 1):
            row = base_row(chapter)
            row["ending_aftertaste"] = f"事件{chapter}{case['fixed_suffix']}"
            rows.append(row)
        result = self.run_audit(rows, [f"本章以不同动作{chapter}结束。" for chapter in range(1, 13)], review(12))
        self.assertEqual(result["gates"][case["expected_gate"]], case["expected_status"])

    def test_manual_source_contradiction_fails(self):
        case = FIXTURES["source_contradiction"]
        rows = [base_row(chapter) for chapter in range(1, 13)]
        rows[0]["aftermath"] = case["analysis_claim"]
        endings = [case["source_fact"]] + [f"第{chapter}章事实结束。" for chapter in range(2, 13)]
        result = self.run_audit(rows, endings, review(12, failure=case["chapter"]))
        self.assertEqual(result["gates"][case["expected_gate"]], case["expected_status"])

    def test_hook_type_and_notes_repetition_are_not_semantic_inputs(self):
        module = load_module()
        rows = [base_row(chapter) for chapter in range(1, 13)]
        self.assertTrue(all(row["hook_type"] == "风险升级" for row in rows))
        self.assertTrue(all(row["notes"] == "依据完整正文提炼" for row in rows))
        hit_fields = {hit["field"] for hit in module.template_flags(rows)}
        self.assertNotIn("hook_type", hit_fields)
        self.assertNotIn("notes", hit_fields)

    def test_missing_manual_review_requires_source_sample_review(self):
        module = load_module()
        status, errors, _details = module.audit_source_review(None, [base_row(chapter) for chapter in range(1, 13)])
        self.assertEqual(status, "SOURCE_SAMPLE_REVIEW_REQUIRED")
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
