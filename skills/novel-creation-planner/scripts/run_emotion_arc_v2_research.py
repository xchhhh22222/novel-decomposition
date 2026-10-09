#!/usr/bin/env python3
"""Execute the optional research-only Emotion Arc V2 Planner adapter.

The adapter preserves E0/E1/M0/D1-D4 and inserts E2/E3 only when enabled. It
derives functional requirements before invoking the existing 02-09 search CLI,
resolves every selected row from the frozen package, and emits a nine-stage Story
Spine. It does not write the production plan schema or promote any fixture.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from validate_emotion_arc_v2_research_plan import validate_plan


MODULE_ORDER = (
    "golden_finger", "worldbuilding", "cultivation_system", "character_function",
    "plotline", "opening", "arc_structure", "plot_mechanism",
)
MODULE_LABELS = {
    "golden_finger": "金手指", "worldbuilding": "世界观", "cultivation_system": "修炼体系",
    "character_function": "人物功能", "plotline": "主线", "opening": "开篇",
    "arc_structure": "篇章结构", "plot_mechanism": "剧情机制",
}
SPINE_STAGES = ("trigger", "goal", "resistance", "nodes", "choice", "cost", "payoff", "state_change", "next_entry")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError("brief must be a JSON object")
    return value


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def require_scenario(brief: dict[str, Any]) -> dict[str, Any]:
    scenario = brief.get("scenario")
    required = {
        "protagonist_role", "threatened_group", "home", "threat", "initial_failure", "pressure_steps",
        "active_choice", "rescue_cost", "immediate_payoff", "irreversible_change", "family_choice",
        "ability_constraint", "institution_failure", "evidence_trigger", "protection_authority",
        "next_macro_question", "next_macro_payoff", "resistance", "nodes", "institution_nodes",
    }
    if not isinstance(scenario, dict) or required - set(scenario):
        raise ValueError(f"scenario missing fields: {sorted(required - set(scenario or {}))}")
    if not isinstance(scenario["pressure_steps"], list) or len(scenario["pressure_steps"]) < 2:
        raise ValueError("pressure_steps requires at least two pressure events")
    if not isinstance(scenario["nodes"], list) or not isinstance(scenario["institution_nodes"], list):
        raise ValueError("nodes and institution_nodes must be arrays")
    return scenario


def export_package(repo: Path, commit: str, package_subdir: str, destination: Path) -> Path:
    """Materialize manifest-declared Git blobs without checkout EOL conversion.

    The package manifest hashes Git object bytes. On Windows, a normal checkout
    (and some archive extraction paths) can apply CRLF conversion and therefore
    must not be treated as the frozen source. Exporting every declared artifact
    with ``git show`` preserves the committed bytes while retaining the existing
    integrity gate unchanged.
    """
    package = destination / Path(package_subdir)
    package.mkdir(parents=True, exist_ok=True)

    def git_blob(relative: str) -> bytes:
        run = subprocess.run(
            ["git", "-C", str(repo), "show", f"{commit}:{package_subdir}/{relative}"],
            capture_output=True,
        )
        if run.returncode:
            detail = run.stderr.decode("utf-8", errors="replace").strip()
            raise ValueError(detail or f"frozen Git blob missing: {relative}")
        return run.stdout

    manifest_bytes = git_blob("manifest.json")
    try:
        manifest = json.loads(manifest_bytes.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"frozen package manifest invalid: {exc}") from exc
    artifact_paths = manifest.get("artifact_paths")
    artifact_hashes = manifest.get("artifact_sha256")
    if not isinstance(artifact_paths, dict) or not artifact_paths:
        raise ValueError("frozen package artifact_paths missing")
    if not isinstance(artifact_hashes, dict) or set(artifact_paths) != set(artifact_hashes or {}):
        raise ValueError("frozen package path/hash inventory mismatch")

    (package / "manifest.json").write_bytes(manifest_bytes)
    root = package.resolve()
    for name, relative in artifact_paths.items():
        if not isinstance(relative, str):
            raise ValueError(f"artifact path must be a string: {name}")
        target = (root / Path(relative)).resolve()
        if target == root or root not in target.parents:
            raise ValueError(f"unsafe artifact path in manifest: {relative}")
        payload = git_blob(relative)
        actual = hashlib.sha256(payload).hexdigest()
        if actual != artifact_hashes[name]:
            raise ValueError(f"frozen Git blob hash mismatch: {relative}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
    return package


def derive_functional_requirements(brief: dict[str, Any], scenario: dict[str, Any]) -> list[dict[str, Any]]:
    queries = brief.get("query_terms", {})
    if not isinstance(queries, dict):
        raise ValueError("query_terms must be an object")
    definitions = {
        "golden_finger": ("SLOT:ABILITY:COSTLY_RESCUE", f"给{scenario['protagonist_role']}提供一次能改变救援条件、但保留{scenario['ability_constraint']}的能力接口"),
        "worldbuilding": ("SLOT:WORLD:PROTECTION_RULE", f"让{scenario['protection_authority']}控制预警/保护资源，并能因{scenario['institution_failure']}承担责任"),
        "cultivation_system": ("SLOT:SYSTEM:RESCUE_COST", f"把救援输出、资源消耗和{scenario['rescue_cost']}放入可验证成长体系"),
        "character_function": ("SLOT:RELATIONSHIP:FAMILY_AGENCY", f"让{scenario['threatened_group']}通过{scenario['family_choice']}真实改变撤离或防守结果"),
        "plotline": ("SLOT:PLOTLINE:ATTACK_TO_INQUIRY", f"把{scenario['threat']}、主动反击、救援结算和制度追查组织成连续因果线"),
        "opening": ("SLOT:OPENING:FAILED_PROTECTION_PROMISE", f"用{scenario['initial_failure']}建立保护承诺，并尽快给出可执行反击入口"),
        "arc_structure": ("SLOT:ARC:SETTLEMENT_AND_RELAY", f"先兑现{scenario['immediate_payoff']}，再由{scenario['evidence_trigger']}开启下一阶段而不取消旧合同"),
        "plot_mechanism": ("SLOT:MECHANISM:EVIDENCE_ACCOUNTABILITY", f"让可检查证据、权限限制和资源责任反复制造选择与后果"),
    }
    defaults = {
        "golden_finger": "保护 救援 代价 限制", "worldbuilding": "保护 权限 资源 责任",
        "cultivation_system": "救援 成长 资源 代价", "character_function": "家庭 保护 选择 关系",
        "plotline": "袭击 救援 追查 责任", "opening": "家人 危机 承诺 反击",
        "arc_structure": "保护 高潮 状态变化 下一阶段", "plot_mechanism": "权限 证据 资源 责任",
    }
    slots = []
    for module in MODULE_ORDER:
        slot_id, function = definitions[module]
        query = queries.get(module, defaults[module])
        if not isinstance(query, str) or not query.strip():
            raise ValueError(f"query_terms.{module} must be nonempty")
        slots.append({
            "slot_id": slot_id,
            "module": module,
            "function_required": function,
            "query": query,
            "required": True,
            "selection_order": "FUNCTION_FIRST_SOURCE_SECOND",
            "derivation_origin": "ORIGINAL_DESIGN",
        })
    return slots


def run_search(search_script: Path, library: Path, slot: dict[str, Any]) -> dict[str, Any]:
    run = subprocess.run([
        sys.executable, str(search_script), "--library", str(library), "--query", slot["query"],
        "--modules", MODULE_LABELS[slot["module"]], "--include-per-book", "--max-per-book", "1",
        "--limit", "5", "--format", "json",
    ], capture_output=True, text=True, encoding="utf-8")
    if run.returncode:
        try:
            detail = json.loads(run.stdout)
        except json.JSONDecodeError:
            detail = {"gap": "RETRIEVAL_FAILURE", "detail": run.stdout or run.stderr}
        return {"returned": 0, "results": [], "retrieval_gap": detail}
    return json.loads(run.stdout)


def selected_source(library: Path, result: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    path = library / result["path"]
    raw_lines = path.read_text(encoding="utf-8-sig").splitlines()
    raw = raw_lines[int(result["line"]) - 1]
    row = json.loads(raw)
    source_id = result.get("source_record_id", result.get("record_id"))
    if row.get("record_id") != source_id:
        raise ValueError(f"retrieval source ID mismatch at {result['path']}:{result['line']}")
    ref = {
        "material_id": result.get("component_id") or result.get("record_id"),
        "module": result["module"],
        "record_id": result.get("record_id"),
        "source_record_id": source_id,
        "component_id": result.get("component_id"),
        "component_path": result.get("component_path"),
        "book_id": result.get("book_id"),
        "qa_status": result.get("qa_status"),
        "usage_status": result.get("usage_status"),
        "path": result["path"],
        "line": result["line"],
        "source_line_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "title": result.get("title"),
        "summary": result.get("summary"),
        "evidence_refs": result.get("evidence_refs", row.get("evidence_refs", [])),
    }
    return ref, row


def assemble_materials(slots: list[dict[str, Any]], search_script: Path, library: Path) -> dict[str, Any]:
    output = []
    for slot in slots:
        retrieval = run_search(search_script, library, slot)
        eligible = [row for row in retrieval.get("results", []) if row.get("qa_status") != "FAIL" and row.get("usage_status") != "HOLD"]
        selected_ref = None
        source_shape: dict[str, Any] = {}
        gap = ""
        if eligible:
            selected_ref, source_row = selected_source(library, eligible[0])
            source_shape = {
                "interface_status": "PARTIAL",
                "available_fields": sorted(source_row),
                "declared_unknowns": source_row.get("unknowns", []),
                "semantic_limit": "automatic retrieval proves provenance and lexical/function proximity, not final compatibility",
            }
        else:
            gap = json.dumps(retrieval.get("retrieval_gap", {"gap": "NO_COMPATIBLE_CANDIDATE"}), ensure_ascii=False)
        output.append({
            **slot,
            "candidate_count": len(retrieval.get("results", [])),
            "selected_ref": selected_ref,
            "source_interface": source_shape,
            "selection_basis": "TOP_RANKED_FUNCTION_QUERY_CANDIDATE" if selected_ref else "NO_ELIGIBLE_CANDIDATE",
            "compatibility": "CANDIDATE_NEEDS_SEMANTIC_REVIEW" if selected_ref else "MATERIAL_GAP",
            "compatibility_explanation": (
                f"来源候选“{selected_ref.get('title') or selected_ref.get('source_record_id')}”与功能查询存在词项/功能邻近；"
                "当前只批准把该候选作为抽象接口参照，不证明其规则、代价或因果链已满足本槽位。"
                "人物、专名、表面包装与完整事件链不得复用，具体兼容性须独立语义审核。"
                if selected_ref else "检索未返回可用真实候选；不以模型原创伪装素材来源。"
            ),
            "gap": gap,
        })
    source_counts: dict[str, int] = {}
    for slot in output:
        selected = slot.get("selected_ref") or {}
        book_id = selected.get("book_id")
        if book_id:
            source_counts[book_id] = source_counts.get(book_id, 0) + 1
    concentrated = {book: count for book, count in source_counts.items() if count > 2}
    return {
        "status": "COMPLETE" if all(slot["selected_ref"] for slot in output) else "HOLD_WITH_GAPS",
        "status_semantics": "COMPLETE means every function slot has a provenance-verified candidate; it does not mean semantic compatibility is approved",
        "selection_order": "FUNCTION_FIRST_SOURCE_SECOND",
        "slots": output,
        "source_concentration_review": {
            "status": "NEEDS_SEMANTIC_REVIEW" if concentrated else "NO_AUTOMATIC_CONCENTRATION_FLAG",
            "selected_candidate_counts_by_book": source_counts,
            "books_above_two_slots": concentrated,
            "interpretation": "候选来源集中只触发审核，不自动拒绝，也不证明已获得剧情多样性。",
        },
    }


def build_e2_e3(s: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    macro_a_contract = f"{s['immediate_payoff']}，并可见记录{s['rescue_cost']}，不能只用击退敌人替代家庭安全结算"
    macro_b_contract = f"{s['next_macro_payoff']}；必须改变至少一项保护权限、责任或资源流"
    e2 = {"macro_arcs": [
        {
            "macro_id": "MA:PILOT:A", "label": "家园守护", "origin_kind": "ORIGINAL_DESIGN",
            "reader_promise": f"经历{s['initial_failure']}后，{s['protagonist_role']}能否让{s['threatened_group']}获得真实、可持续的保护结果",
            "start_condition": s["institution_failure"], "settlement_contract": macro_a_contract,
            "irreversible_change": s["irreversible_change"], "status": "DESIGNED_NOT_OBSERVED", "qa_status": "HOLD",
        },
        {
            "macro_id": "MA:PILOT:B", "label": "保护秩序追索", "origin_kind": "ORIGINAL_DESIGN",
            "reader_promise": s["next_macro_question"], "start_condition": s["evidence_trigger"],
            "settlement_contract": macro_b_contract,
            "irreversible_change": f"{s['protagonist_role']}从家庭救援者变成保护规则争议的当事人",
            "status": "DESIGNED_NOT_OBSERVED", "qa_status": "HOLD",
        },
    ]}
    lines = [
        {"line_id": "EL:PILOT:FAMILY", "expectation": f"{s['threatened_group']}不只是人质，能以{s['family_choice']}影响结果", "payoff_condition": f"{s['family_choice']}实际改变安全状态", "macro_ids": ["MA:PILOT:A"], "state": "ACTIVE"},
        {"line_id": "EL:PILOT:GROWTH", "expectation": f"主角能否在失败后取得足以救援、但受{s['ability_constraint']}限制的能力", "payoff_condition": f"能力通过救援验证，同时兑现{s['rescue_cost']}", "macro_ids": ["MA:PILOT:A"], "state": "ACTIVE"},
        {"line_id": "EL:PILOT:RELATIONSHIP", "expectation": "家人和协作者是否拥有独立目标并迫使主角调整方案", "payoff_condition": "至少一次他人选择改变节点、成本或撤离结果", "macro_ids": ["MA:PILOT:A", "MA:PILOT:B"], "state": "ACTIVE"},
        {"line_id": "EL:PILOT:ACCOUNTABILITY", "expectation": s["next_macro_question"], "payoff_condition": macro_b_contract, "macro_ids": ["MA:PILOT:B"], "state": "PENDING_TRIGGER"},
    ]
    e3 = {
        "emotion_lines": lines,
        "weaves": [
            {"weave_id": "EW:PILOT:001", "type": "ENABLES_CHOICE", "from_line_id": "EL:PILOT:GROWTH", "to_line_id": "EL:PILOT:FAMILY", "event": s["active_choice"], "causal_bridge": "能力输出必须改变家人的可行选择，而非只增加战斗数值"},
            {"weave_id": "EW:PILOT:002", "type": "CAUSES_PRESSURE", "from_line_id": "EL:PILOT:RELATIONSHIP", "to_line_id": "EL:PILOT:FAMILY", "event": s["family_choice"], "causal_bridge": "家人的主动决定改变撤离/防守方案及主角成本"},
            {"weave_id": "EW:PILOT:003", "type": "PAYOFF_OPENS", "from_line_id": "EL:PILOT:FAMILY", "to_line_id": "EL:PILOT:ACCOUNTABILITY", "event": s["evidence_trigger"], "causal_bridge": "证据在救援过程中出现，但不能替代家园守护的独立结算"},
        ],
        "handoff": {
            "handoff_id": "AH:PILOT:A-B", "from_macro_id": "MA:PILOT:A", "to_macro_id": "MA:PILOT:B",
            "trigger": s["evidence_trigger"], "overlap_design": True,
            "old_arc_contract_retained": macro_a_contract, "new_arc_contract": macro_b_contract,
            "dominance_transfer_status": "CANDIDATE_UNVERIFIED", "qa_status": "HOLD",
        },
    }
    return e2, e3


def build_spine(s: dict[str, Any], material_ids: dict[str, str] | None = None) -> dict[str, Any]:
    ids = material_ids or {}
    values = {
        "trigger": (f"{s['institution_failure']}，{s['threat']}抵达{s['home']}", ["EL:PILOT:FAMILY"], ["MA:PILOT:A"]),
        "goal": (f"让{s['threatened_group']}进入可防守状态并恢复真实保护", ["EL:PILOT:FAMILY"], ["MA:PILOT:A"]),
        "resistance": (s["resistance"], ["EL:PILOT:FAMILY", "EL:PILOT:GROWTH"], ["MA:PILOT:A"]),
        "nodes": (" → ".join(s["nodes"]), ["EL:PILOT:FAMILY", "EL:PILOT:RELATIONSHIP"], ["MA:PILOT:A"]),
        "choice": (s["active_choice"], ["EL:PILOT:GROWTH", "EL:PILOT:RELATIONSHIP"], ["MA:PILOT:A"]),
        "cost": (s["rescue_cost"], ["EL:PILOT:GROWTH"], ["MA:PILOT:A"]),
        "payoff": (s["immediate_payoff"], ["EL:PILOT:FAMILY"], ["MA:PILOT:A"]),
        "state_change": (s["irreversible_change"], ["EL:PILOT:FAMILY", "EL:PILOT:ACCOUNTABILITY"], ["MA:PILOT:A", "MA:PILOT:B"]),
        "next_entry": (f"{s['evidence_trigger']}；后续节点：{' → '.join(s['institution_nodes'])}", ["EL:PILOT:ACCOUNTABILITY"], ["MA:PILOT:B"]),
    }
    return {"contract": "EXISTING_NINE_STAGE_STORY_SPINE", "stages": [
        {"stage": stage, "story_task": values[stage][0], "emotion_line_ids": values[stage][1], "macro_arc_ids": values[stage][2], "material_refs": sorted(ids.values())}
        for stage in SPINE_STAGES
    ]}


def build_legacy_plan(brief: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "emotion_arc_planner_v2_research", "plan_id": brief["plan_id"] + ":LEGACY",
        "status": "candidate", "qa_status": "HOLD", "origin_kind": "ORIGINAL_DESIGN",
        "mode": "E2_E3_DISABLED_BASELINE", "runtime_status": "EXECUTED_RESEARCH_PIPELINE",
        "creation_approval": "NOT_GRANTED", "production_promotion": "NOT_RUN",
        "material_source": {"mode": "NOT_USED_BY_BASELINE"},
        "pipeline": {
            "e0": {"brief": brief.get("emotion_request")}, "e1": {"action_premise": scenario["threat"]},
            "m0": {"rmf": "NOT_SELECTED"}, "d1": {"mode": "LEGACY_EVENT_SLOTS"},
            "d2": {"mode": "LEGACY_NO_E2_E3_ASSEMBLY"}, "d3": {"mode": "LEGACY_ORIGINAL_DESIGN"},
            "d4": {"review": "PENDING"},
        },
        "story_spine": build_spine(scenario),
        "quality_gates": {"structural": "PASS", "semantic_review": "NEEDS_SEMANTIC_REVIEW", "legacy_compatibility": "PASS"},
    }


def build_enabled_plan(
    brief: dict[str, Any], scenario: dict[str, Any], library: Path, source_meta: dict[str, Any], search_script: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    requirements = derive_functional_requirements(brief, scenario)
    assembly = assemble_materials(requirements, search_script, library)
    e2, e3 = build_e2_e3(scenario)
    material_ids = {
        slot["module"]: slot["selected_ref"]["material_id"] for slot in assembly["slots"] if slot["selected_ref"]
    }
    plan = {
        "schema_version": "emotion_arc_planner_v2_research", "plan_id": brief["plan_id"],
        "status": "candidate", "qa_status": "HOLD", "origin_kind": "ORIGINAL_DESIGN",
        "mode": "E2_E3_ENABLED", "runtime_status": "EXECUTED_RESEARCH_PIPELINE",
        "creation_approval": "NOT_GRANTED", "production_promotion": "NOT_RUN",
        "material_source": source_meta,
        "pipeline": {
            "e0": {"emotion_request": brief.get("emotion_request")},
            "e1": {"causal_window": [scenario["initial_failure"], *scenario["pressure_steps"], scenario["active_choice"], scenario["immediate_payoff"]]},
            "e2": e2, "e3": e3,
            "m0": {"rmf": "NOT_SELECTED", "status": "OPTIONAL_RESEARCH_GAP"},
            "d1": {"functional_requirements": [slot["slot_id"] for slot in requirements]},
            "d2": {"material_assembly_status": assembly["status"]},
            "d3": {"implementation_origin": "ORIGINAL_DESIGN", "adapter_policy": "SOURCE_FACT_TO_FUNCTION_TO_NEW_DESIGN"},
            "d4": {"review": "PENDING_INDEPENDENT_REVIEW"},
        },
        "material_assembly": assembly,
        "story_spine": build_spine(scenario, material_ids),
        "active_emotion_state": {
            "active_macro_arcs": ["MA:PILOT:A", "MA:PILOT:B"],
            "active_emotion_lines": [line["line_id"] for line in e3["emotion_lines"]],
            "pending_payoff_contracts": [arc["settlement_contract"] for arc in e2["macro_arcs"]],
            "current_reader_knowledge": [scenario["initial_failure"], scenario["evidence_trigger"]],
            "state_constraints": [scenario["ability_constraint"], scenario["rescue_cost"]],
            "chosen_story_beats": [stage["stage"] for stage in build_spine(scenario)["stages"]],
            "material_adapter_refs": sorted(material_ids.values()),
        },
        "quality_gates": {
            "runtime_execution": "PASS", "function_before_source": "PASS",
            "material_retrieval": "PASS" if assembly["status"] == "COMPLETE" else "HOLD",
            "story_spine_preserved": "PASS", "old_arc_contract_retained": "PASS",
            "semantic_review": "NEEDS_SEMANTIC_REVIEW", "production": "NOT_RUN",
        },
    }
    return plan, {"slots": requirements}, assembly


def main() -> int:
    parser = argparse.ArgumentParser(description="Run optional Emotion Arc V2 research Planner adapter.")
    parser.add_argument("--brief", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--material-library", type=Path)
    parser.add_argument("--material-snapshot-repo", type=Path)
    parser.add_argument("--material-snapshot-commit")
    parser.add_argument("--material-package-subdir")
    parser.add_argument("--disable-emotion-arcs", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        brief = read_json(args.brief)
        if not isinstance(brief.get("plan_id"), str):
            raise ValueError("plan_id required")
        scenario = require_scenario(brief)
        output = args.output_dir.resolve()
        if output.exists() and any(output.iterdir()) and not args.force:
            raise ValueError("output directory is not empty; pass --force")
        output.mkdir(parents=True, exist_ok=True)

        if args.disable_emotion_arcs:
            plan = build_legacy_plan(brief, scenario)
            report = validate_plan(plan)
            write_json(output / "legacy-plan.json", plan)
            write_json(output / "validation-report.json", report)
        else:
            search_script = Path(__file__).with_name("search_dna_candidates.py")
            with tempfile.TemporaryDirectory(prefix="nova-emotion-arc-material-") as tmp:
                if args.material_snapshot_repo:
                    if not args.material_snapshot_commit or not args.material_package_subdir:
                        raise ValueError("snapshot repo requires --material-snapshot-commit and --material-package-subdir")
                    library = export_package(
                        args.material_snapshot_repo.resolve(), args.material_snapshot_commit,
                        args.material_package_subdir, Path(tmp),
                    )
                    remote = subprocess.run(
                        ["git", "config", "--get", "remote.origin.url"], cwd=args.material_snapshot_repo.resolve(),
                        capture_output=True, text=True, encoding="utf-8",
                    ).stdout.strip()
                    source_meta = {
                        "mode": "FROZEN_GIT_SNAPSHOT", "repository": remote or "LOCAL_GIT_SNAPSHOT",
                        "commit": args.material_snapshot_commit, "package_subdir": args.material_package_subdir,
                    }
                    source_repo = args.material_snapshot_repo.resolve()
                elif args.material_library:
                    library = args.material_library.resolve()
                    source_meta = {"mode": "LOCAL_PACKAGE", "repository": "", "commit": "", "package_subdir": ""}
                    source_repo = None
                else:
                    raise ValueError("material library or frozen material snapshot required")
                plan, requirements, assembly = build_enabled_plan(brief, scenario, library, source_meta, search_script)
                report = validate_plan(plan, source_repo)
                write_json(output / "emotion-arc-plan.json", plan)
                write_json(output / "functional-requirements.json", requirements)
                write_json(output / "material-assembly.json", assembly)
                write_json(output / "emotion-arc-planning-table.json", plan["pipeline"]["e2"])
                write_json(output / "active-emotion-line-table.json", {"emotion_lines": plan["pipeline"]["e3"]["emotion_lines"], **plan["active_emotion_state"]})
                write_json(output / "weave-handoff-table.json", {"weaves": plan["pipeline"]["e3"]["weaves"], "handoff": plan["pipeline"]["e3"]["handoff"]})
                write_json(output / "story-spine.json", plan["story_spine"])
                write_json(output / "validation-report.json", report)
        print(json.dumps({"ok": report.get("ok"), "output_dir": str(output), "mode": plan["mode"], "quality_gates": plan["quality_gates"], "validation": report}, ensure_ascii=False, indent=2))
        return 0 if report.get("ok") else 1
    except (OSError, ValueError, json.JSONDecodeError, subprocess.SubprocessError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
