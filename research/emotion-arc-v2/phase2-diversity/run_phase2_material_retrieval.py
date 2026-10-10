#!/usr/bin/env python3
"""Execute the Phase 2 material-selection comparison on a frozen Git package."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
PLANNER_SCRIPTS = REPO_ROOT / "skills" / "novel-creation-planner" / "scripts"
sys.path.insert(0, str(PLANNER_SCRIPTS))

from run_emotion_arc_v2_research import export_package, selected_source  # noqa: E402


MODULE_LABELS = {
    "golden_finger": "金手指",
    "worldbuilding": "世界观",
    "cultivation_system": "修炼体系",
    "character_function": "人物功能",
    "plotline": "主线",
    "opening": "开篇",
    "arc_structure": "篇章结构",
    "plot_mechanism": "剧情机制",
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def find(results: list[dict[str, Any]], wanted: str) -> dict[str, Any] | None:
    for item in results:
        identities = {
            item.get("record_id"), item.get("source_record_id"), item.get("component_id")
        }
        if wanted in identities:
            return item
    return None


def compact(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "record_id": item.get("record_id"),
        "source_record_id": item.get("source_record_id"),
        "component_id": item.get("component_id"),
        "component_path": item.get("component_path"),
        "book_id": item.get("book_id"),
        "title": item.get("title"),
        "qa_status": item.get("qa_status"),
        "usage_status": item.get("usage_status"),
        "path": item.get("path"),
        "line": item.get("line"),
        "source_line_sha256": item.get("source_line_sha256"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--material-repo", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--package-subdir", default="packages/shared-dna-library/v1.0.0"
    )
    args = parser.parse_args()

    try:
        plan = read_json(args.plan)
        search_script = PLANNER_SCRIPTS / "search_dna_candidates.py"
        records: list[dict[str, Any]] = []
        selected_by_path: dict[str, list[str]] = {}
        with tempfile.TemporaryDirectory(prefix="nova-phase2-material-") as temp:
            library = export_package(
                args.material_repo.resolve(), args.commit, args.package_subdir, Path(temp)
            )
            for query in plan.get("queries", []):
                module = query.get("module")
                if module not in MODULE_LABELS:
                    raise ValueError(f"unsupported module: {module}")
                command = [
                    sys.executable,
                    str(search_script),
                    "--library",
                    str(library),
                    "--query",
                    query["query"],
                    "--modules",
                    MODULE_LABELS[module],
                    "--include-per-book",
                    "--max-per-book",
                    "1",
                    "--limit",
                    str(query.get("candidate_limit", 8)),
                    "--format",
                    "json",
                ]
                run = subprocess.run(
                    command, capture_output=True, text=True, encoding="utf-8"
                )
                if run.returncode:
                    raise ValueError(
                        f"retrieval failed for {query.get('query_id')}: {run.stdout or run.stderr}"
                    )
                payload = json.loads(run.stdout)
                results = payload.get("results", [])
                selected = find(results, query["selected_id"])
                if selected is None:
                    raise ValueError(
                        f"selected source not retrieved: {query['query_id']} -> {query['selected_id']}"
                    )
                selected_ref, _ = selected_source(library, selected)
                rejected = []
                for rejected_id in query.get("rejected_ids", []):
                    item = find(results, rejected_id)
                    if item is None:
                        raise ValueError(
                            f"rejected source not retrieved: {query['query_id']} -> {rejected_id}"
                        )
                    rejected_ref, _ = selected_source(library, item)
                    rejected.append(compact(rejected_ref))
                selected_by_path.setdefault(query["path"], []).append(query["selected_id"])
                records.append(
                    {
                        **query,
                        "retrieval_exit_code": run.returncode,
                        "candidate_count": len(results),
                        "candidate_pool": [compact(item) for item in results],
                        "selected_ref": compact(selected_ref),
                        "rejected_refs": rejected,
                    }
                )

        legacy = set(selected_by_path.get("LEGACY_BASELINE", []))
        enhanced = set(selected_by_path.get("E2_E3_ENABLED", []))
        output = {
            "schema_version": "emotion_first_phase2_material_retrieval_v1",
            "status": "candidate",
            "qa_status": "HOLD",
            "brief_ref": plan.get("brief_ref"),
            "brief_sha256": plan.get("brief_sha256"),
            "model_execution": plan.get("model_execution"),
            "independence": "REQUESTED_NOT_MACHINE_PROVEN",
            "material_source": {
                "mode": "FROZEN_GIT_SNAPSHOT",
                "repository": "xchhhh22222/nova-material-library",
                "commit": args.commit,
                "package_subdir": args.package_subdir,
            },
            "same_budget": plan.get("same_budget"),
            "queries": records,
            "selection_overlap": {
                "legacy_selected_count": len(legacy),
                "enhanced_selected_count": len(enhanced),
                "shared_selected_ids": sorted(legacy & enhanced),
                "claim_limit": "different selections do not by themselves prove higher literary quality",
            },
            "material_adaptation": "REVIEW_REQUIRED",
        }
        write_json(args.output, output)
        print(
            json.dumps(
                {
                    "ok": True,
                    "queries": len(records),
                    "legacy_selected": len(legacy),
                    "enhanced_selected": len(enhanced),
                    "shared_selected": sorted(legacy & enhanced),
                    "output": str(args.output.resolve()),
                },
                ensure_ascii=False,
            )
        )
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError, subprocess.SubprocessError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
