#!/usr/bin/env python3
"""Validate the optional research-only E2/E3 Planner output."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


MODULES = {
    "golden_finger", "worldbuilding", "cultivation_system", "character_function",
    "plotline", "opening", "arc_structure", "plot_mechanism",
}
SPINE_STAGES = ["trigger", "goal", "resistance", "nodes", "choice", "cost", "payoff", "state_change", "next_entry"]


def issue(items: list[dict[str, str]], code: str, where: str, message: str) -> None:
    items.append({"code": code, "where": where, "message": message})


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def verify_source_ref(ref: dict[str, Any], plan: dict[str, Any], repo: Path, errors: list[dict[str, str]], where: str) -> None:
    snapshot = plan.get("material_source", {})
    commit = snapshot.get("commit")
    package_subdir = snapshot.get("package_subdir")
    rel = ref.get("path")
    line = ref.get("line")
    if not all(nonempty(value) for value in (commit, package_subdir, rel)) or not isinstance(line, int) or line < 1:
        issue(errors, "MATERIAL_SOURCE_REF_INVALID", where, "snapshot commit/package/path/line required")
        return
    git_path = f"{str(package_subdir).rstrip('/')}/{str(rel).lstrip('/')}"
    run = subprocess.run(["git", "show", f"{commit}:{git_path}"], cwd=repo, capture_output=True)
    if run.returncode:
        issue(errors, "MATERIAL_SOURCE_MISSING", where, git_path)
        return
    lines = run.stdout.decode("utf-8-sig").splitlines()
    if line > len(lines):
        issue(errors, "MATERIAL_SOURCE_LINE_MISSING", where, f"line {line} outside {git_path}")
        return
    raw = lines[line - 1]
    try:
        row = json.loads(raw)
    except json.JSONDecodeError:
        issue(errors, "MATERIAL_SOURCE_ROW_INVALID", where, "selected source line is not JSON")
        return
    if row.get("record_id") != ref.get("source_record_id", ref.get("record_id")):
        issue(errors, "MATERIAL_SOURCE_ID_MISMATCH", where, "record_id does not match frozen source row")
    if hashlib.sha256(raw.encode("utf-8")).hexdigest() != ref.get("source_line_sha256"):
        issue(errors, "MATERIAL_SOURCE_HASH_MISMATCH", where, "source line digest mismatch")


def validate_plan(plan: dict[str, Any], source_repo: Path | None = None) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    required = {
        "schema_version", "plan_id", "status", "qa_status", "origin_kind", "mode", "pipeline",
        "material_source", "story_spine", "quality_gates", "production_promotion", "creation_approval",
    }
    missing = sorted(required - set(plan))
    if missing:
        issue(errors, "MISSING_FIELDS", "plan", ", ".join(missing))
    if plan.get("schema_version") != "emotion_arc_planner_v2_research" or plan.get("status") != "candidate":
        issue(errors, "RESEARCH_ENVELOPE_INVALID", "plan", "research schema and candidate status required")
    if plan.get("qa_status") != "HOLD" or plan.get("production_promotion") != "NOT_RUN" or plan.get("creation_approval") != "NOT_GRANTED":
        issue(errors, "PROMOTION_FORBIDDEN", "plan", "research output must remain HOLD/NOT_RUN/NOT_GRANTED")
    if plan.get("origin_kind") != "ORIGINAL_DESIGN":
        issue(errors, "ORIGIN_LAYER_INVALID", "plan", "Planner output must be ORIGINAL_DESIGN")

    spine = plan.get("story_spine", {})
    stages = spine.get("stages") if isinstance(spine, dict) else None
    if not isinstance(stages, list) or [item.get("stage") for item in stages if isinstance(item, dict)] != SPINE_STAGES:
        issue(errors, "STORY_SPINE_INVALID", "story_spine.stages", "exact nine-stage Story Spine required")

    enabled = plan.get("mode") == "E2_E3_ENABLED"
    pipeline = plan.get("pipeline", {})
    if enabled:
        for key in ("e0", "e1", "e2", "e3", "m0", "d1", "d2", "d3", "d4"):
            if key not in pipeline:
                issue(errors, "PIPELINE_STAGE_MISSING", f"pipeline.{key}", "required optional-route stage missing")
        e2, e3 = pipeline.get("e2", {}), pipeline.get("e3", {})
        macros = e2.get("macro_arcs", []) if isinstance(e2, dict) else []
        lines = e3.get("emotion_lines", []) if isinstance(e3, dict) else []
        handoff = e3.get("handoff", {}) if isinstance(e3, dict) else {}
        if len(macros) < 2 or len(lines) < 3:
            issue(errors, "E2_E3_INCOMPLETE", "pipeline", "two macros and at least three independent lines required")
        if macros and handoff:
            old_contract = macros[0].get("settlement_contract")
            if handoff.get("old_arc_contract_retained") != old_contract:
                issue(errors, "OLD_ARC_CONTRACT_CANCELLED", "pipeline.e3.handoff", "handoff must retain macro A settlement contract verbatim")
        if handoff.get("dominance_transfer_status") != "CANDIDATE_UNVERIFIED":
            issue(errors, "HANDOFF_OVERCLAIM", "pipeline.e3.handoff", "dominance transfer must remain unverified")

        assembly = plan.get("material_assembly", {})
        slots = assembly.get("slots", []) if isinstance(assembly, dict) else []
        seen_modules = {slot.get("module") for slot in slots if isinstance(slot, dict)}
        if seen_modules != MODULES:
            issue(errors, "MATERIAL_MODULE_COVERAGE", "material_assembly.slots", f"expected 02-09 modules, got {sorted(seen_modules)}")
        for index, slot in enumerate(slots):
            where = f"material_assembly.slots[{index}]"
            selected = slot.get("selected_ref")
            gap = slot.get("gap")
            if selected is None and not nonempty(gap):
                issue(errors, "MATERIAL_SELECTION_UNEXPLAINED", where, "selected_ref or explicit gap required")
            if selected is not None:
                if selected.get("qa_status") == "FAIL" or selected.get("usage_status") == "HOLD":
                    issue(errors, "INELIGIBLE_MATERIAL_SELECTED", where, "FAIL/HOLD source cannot be selected")
                if source_repo is not None:
                    verify_source_ref(selected, plan, source_repo, errors, where)
            if slot.get("selection_order") != "FUNCTION_FIRST_SOURCE_SECOND":
                issue(errors, "SELECTION_ORDER_INVALID", where, "function-first derivation marker required")
        if any(slot.get("selected_ref") is None for slot in slots):
            issue(warnings, "MATERIAL_GAP_RETAINED", "material_assembly", "one or more slots remain GAP/HOLD")
    else:
        if "e2" in pipeline or "e3" in pipeline or "material_assembly" in plan:
            issue(errors, "LEGACY_PATH_POLLUTED", "plan", "disabled path must not emit E2/E3 or V2 material assembly")

    if plan.get("quality_gates", {}).get("semantic_review") != "NEEDS_SEMANTIC_REVIEW":
        issue(errors, "SEMANTIC_AUTOPASS_FORBIDDEN", "quality_gates.semantic_review", "semantic review cannot be machine-approved")
    return {
        "ok": not errors,
        "structural_gate": "PASS" if not errors else "FAIL",
        "semantic_review": "NEEDS_SEMANTIC_REVIEW",
        "production_promotion": "NOT_RUN",
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate research-only Emotion Arc V2 Planner output.")
    parser.add_argument("plan", type=Path)
    parser.add_argument("--source-repo", type=Path)
    args = parser.parse_args()
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8-sig"))
        report = validate_plan(plan, args.source_repo.resolve() if args.source_repo else None)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        report = {"ok": False, "structural_gate": "FAIL", "errors": [{"code": "INPUT_ERROR", "where": "runtime", "message": str(exc)}], "warnings": []}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
