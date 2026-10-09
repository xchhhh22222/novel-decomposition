#!/usr/bin/env python3
"""Integration tests for the research-only E2/E3 adapter."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
RUNNER = HERE / "run_emotion_arc_v2_research.py"
VALIDATOR = HERE / "validate_emotion_arc_v2_research_plan.py"
MODULE_DIRS = {
    "golden_finger": "02_金手指", "worldbuilding": "03_世界观", "cultivation_system": "04_修炼体系",
    "character_function": "05_人物功能与标签", "plotline": "06_主线与支线", "opening": "07_开篇",
    "arc_structure": "08_篇章结构", "plot_mechanism": "09_剧情机制",
}


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_library(root: Path, omit: str | None = None) -> Path:
    package = root / "library"
    artifacts: dict[str, str] = {}
    hashes: dict[str, str] = {}
    query_text = "保护 救援 代价 限制 权限 资源 责任 成长 家庭 选择 关系 袭击 追查 危机 承诺 反击 高潮 状态变化 下一阶段 证据"
    for module, dirname in MODULE_DIRS.items():
        if module == omit:
            continue
        rel = f"DNA素材/{dirname}/per_book/BOOK_TEST.jsonl"
        path = package / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        row = {
            "record_type": "per_book", "schema_version": 1, "record_id": f"TEST:{module}",
            "status": "candidate", "qa_status": "PASS", "confidence": "HIGH", "book_id": "BOOK_TEST",
            "title": f"{module} functional candidate", "summary": query_text,
            "evidence_refs": ["BOOK_TEST:CHAPTER:0001"], "unknowns": [],
        }
        path.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
        artifacts[rel] = rel
        hashes[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = {
        "package_id": "nova-shared-dna-library", "package_version": "test", "status": "ACTIVE_SHARED_LIBRARY",
        "active": True, "artifact_paths": artifacts, "artifact_sha256": hashes,
    }
    write_json(package / "manifest.json", manifest)
    return package


def build_brief(path: Path) -> None:
    write_json(path, {
        "plan_id": "PILOT:TEST:001",
        "emotion_request": "家人受到欺压，主角保护失败，积累压力后主动反击",
        "scenario": {
            "protagonist_role": "年轻守卫", "threatened_group": "家人", "home": "边镇家园", "threat": "妖魔袭击",
            "initial_failure": "第一次预警失效且主角救援失败", "pressure_steps": ["家人被迫分散", "防线资源被截留"],
            "active_choice": "主角使用受限能力打开撤离路线", "rescue_cost": "能力反噬与资源债",
            "immediate_payoff": "家人脱离即时威胁且防线恢复", "irreversible_change": "能力暴露并留下授权证据",
            "family_choice": "家人选择分组撤离并保留证据", "ability_constraint": "短时使用和恢复期",
            "institution_failure": "保护机构错误分配预警资源", "evidence_trigger": "救援记录显示授权被篡改",
            "protection_authority": "边镇守备署", "next_macro_question": "谁从保护漏洞获利并如何改变规则",
            "next_macro_payoff": "获利链被证据化且保护规则改变", "resistance": "失效防线、资源短缺和妖魔封锁",
            "nodes": ["核实威胁", "取得通道", "家人选择", "主动反击", "恢复防线"],
            "institution_nodes": ["保存记录", "定位权限链", "迫使披露", "改变规则"],
        },
    })


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(RUNNER), *args], capture_output=True, text=True, encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        brief = root / "brief.json"
        build_brief(brief)
        library = build_library(root / "full")
        enhanced_dir = root / "enhanced"
        result = run("--brief", str(brief), "--material-library", str(library), "--output-dir", str(enhanced_dir))
        if result.returncode:
            failures.append(f"enabled path failed: {result.stdout or result.stderr}")
        else:
            plan = json.loads((enhanced_dir / "emotion-arc-plan.json").read_text(encoding="utf-8"))
            if len(plan["material_assembly"]["slots"]) != 8 or any(slot["selected_ref"] is None for slot in plan["material_assembly"]["slots"]):
                failures.append("enabled path did not retrieve all 02-09 slots")
            if len(plan["story_spine"]["stages"]) != 9:
                failures.append("enabled path did not preserve nine-stage spine")
            if plan["pipeline"]["e3"]["handoff"]["old_arc_contract_retained"] != plan["pipeline"]["e2"]["macro_arcs"][0]["settlement_contract"]:
                failures.append("old macro contract was not retained")

        legacy_dir = root / "legacy"
        legacy = run("--brief", str(brief), "--output-dir", str(legacy_dir), "--disable-emotion-arcs")
        if legacy.returncode:
            failures.append(f"legacy path failed: {legacy.stdout or legacy.stderr}")
        else:
            plan = json.loads((legacy_dir / "legacy-plan.json").read_text(encoding="utf-8"))
            if "e2" in plan["pipeline"] or "e3" in plan["pipeline"] or len(plan["story_spine"]["stages"]) != 9:
                failures.append("legacy path was polluted by E2/E3 or lost Story Spine")

        gap_library = build_library(root / "gap", omit="plot_mechanism")
        gap_dir = root / "gap-output"
        gap_run = run("--brief", str(brief), "--material-library", str(gap_library), "--output-dir", str(gap_dir))
        if gap_run.returncode:
            failures.append(f"explicit-gap path should remain structurally valid: {gap_run.stdout or gap_run.stderr}")
        else:
            gap_plan = json.loads((gap_dir / "emotion-arc-plan.json").read_text(encoding="utf-8"))
            missing = next(slot for slot in gap_plan["material_assembly"]["slots"] if slot["module"] == "plot_mechanism")
            if missing["selected_ref"] is not None or not missing["gap"] or gap_plan["quality_gates"]["material_retrieval"] != "HOLD":
                failures.append("missing source did not remain an explicit GAP/HOLD")

        if not failures:
            validate = subprocess.run([sys.executable, str(VALIDATOR), str(enhanced_dir / "emotion-arc-plan.json")], capture_output=True, text=True, encoding="utf-8")
            if validate.returncode:
                failures.append(f"standalone validator failed: {validate.stdout or validate.stderr}")

    print(json.dumps({"ok": not failures, "cases": 7, "passed": 7 - len(failures), "failures": failures}, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
