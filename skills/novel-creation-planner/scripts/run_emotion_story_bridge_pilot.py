#!/usr/bin/env python3
"""Run the sparse-brief Emotion-to-Story Bridge research pilot.

The semantic composition is a separate, explicitly model-authored candidate file.
This runtime never asks deterministic Python to invent literature. It resolves the
proposed emotion/material IDs, builds node-local assembly, enforces research
states/contracts, and preserves a fair legacy comparison from the same brief.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from evaluate_emotion_story_bridge import evaluate
from run_emotion_arc_v2_research import MODULE_LABELS, export_package, selected_source
from search_emotion_arc_library import search_library
from validate_emotion_story_bridge import validate_output


ALLOWED_BRIEF_FIELDS = {
    "schema_version", "brief_id", "input_mode", "status", "genre", "core_reader_expectation",
    "emotion_contour", "required_emotion_weaves", "longform_requirement", "forbidden_prefill",
}
FORBIDDEN_STORY_FIELDS = {
    "scenario", "characters", "character_names", "antagonist", "monster", "ability", "artifact",
    "faction", "conflict", "next_macro_theme", "story_nodes", "macro_arcs",
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def brief_hash(brief: dict[str, Any]) -> str:
    raw = json.dumps(brief, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def validate_sparse_brief(brief: dict[str, Any]) -> None:
    unknown = set(brief) - ALLOWED_BRIEF_FIELDS
    forbidden = set(brief) & FORBIDDEN_STORY_FIELDS
    if unknown or forbidden:
        raise ValueError(f"sparse brief contains non-brief story fields: {sorted(unknown | forbidden)}")
    if brief.get("schema_version") != "sparse_emotion_brief_v1" or brief.get("input_mode") != "SPARSE_EMOTION_BRIEF":
        raise ValueError("sparse_emotion_brief_v1 / SPARSE_EMOTION_BRIEF required")
    if brief.get("status") != "candidate":
        raise ValueError("sparse brief must remain candidate")
    if brief.get("genre") != ["玄幻", "高武"]:
        raise ValueError("pilot genre must be exactly 玄幻/高武")
    if brief.get("emotion_contour") != ["DOWN", "DOWN", "UP"]:
        raise ValueError("pilot contour must be DOWN/DOWN/UP")
    if not isinstance(brief.get("required_emotion_weaves"), list) or len(brief["required_emotion_weaves"]) != 4:
        raise ValueError("exactly four high-level emotion weave requirements required")


def material_search(search_script: Path, library: Path, slot: dict[str, Any]) -> dict[str, Any]:
    module = slot.get("module")
    if module not in MODULE_LABELS:
        raise ValueError(f"unknown material module: {module}")
    command = [
        sys.executable, str(search_script), "--library", str(library), "--query", slot["query"],
        "--modules", MODULE_LABELS[module], "--include-per-book", "--max-per-book", "1",
        "--limit", str(slot.get("candidate_limit", 12)), "--format", "json",
    ]
    if slot.get("component_types"):
        command.extend(["--components", " ".join(slot["component_types"])])
    run = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    if run.returncode:
        raise ValueError(f"material retrieval failed for {slot.get('slot_id')}: {run.stdout or run.stderr}")
    result = json.loads(run.stdout)
    if not isinstance(result, dict):
        raise ValueError("material search returned non-object")
    return result


def resolve_pointer(row: Any, pointer: str) -> Any:
    value = row
    if not pointer:
        return value
    if not pointer.startswith("/"):
        raise ValueError(f"component_pointer must be JSON Pointer: {pointer}")
    for raw in pointer[1:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(value, list):
            value = value[int(token)]
        elif isinstance(value, dict) and token in value:
            value = value[token]
        else:
            raise ValueError(f"component pointer missing: {pointer}")
    return value


def contains_value(value: Any, expected: str) -> bool:
    if isinstance(value, dict):
        return any(contains_value(item, expected) for item in value.values())
    if isinstance(value, list):
        return any(contains_value(item, expected) for item in value)
    return value == expected


def find_candidate(results: list[dict[str, Any]], source_id: str) -> dict[str, Any] | None:
    return next((item for item in results if source_id in {item.get("record_id"), item.get("source_record_id")}), None)


def enrich_slot(slot: dict[str, Any], search_script: Path, library: Path) -> dict[str, Any]:
    output = copy.deepcopy(slot)
    output["selection_order"] = "FUNCTION_FIRST_SOURCE_SECOND"
    retrieval = material_search(search_script, library, slot)
    results = [item for item in retrieval.get("results", []) if item.get("qa_status") != "FAIL" and item.get("usage_status") != "HOLD"]
    output["candidate_pool"] = [
        {
            "record_id": item.get("record_id"), "source_record_id": item.get("source_record_id"),
            "component_id": item.get("component_id"), "book_id": item.get("book_id"),
            "title": item.get("title"), "qa_status": item.get("qa_status"),
        }
        for item in results
    ]
    output["selected_ref"] = None
    decision = slot.get("decision")
    if decision in {"SELECT_DIRECT", "SELECT_ADAPT"}:
        wanted = slot.get("selected_source_id")
        candidate = find_candidate(results, wanted)
        if candidate is None:
            raise ValueError(f"selected source was not retrieved for {slot.get('slot_id')}: {wanted}")
        ref, source_row = selected_source(library, candidate)
        pointer = slot.get("component_pointer", "")
        component = resolve_pointer(source_row, pointer)
        component_id = slot.get("component_id")
        if component_id and not contains_value(component, component_id):
            raise ValueError(f"component ID does not resolve at {pointer}: {component_id}")
        if component_id:
            ref["material_id"] = component_id
            ref["component_id"] = component_id
            ref["component_path"] = pointer
        ref["source_component_preview"] = json.dumps(component, ensure_ascii=False, separators=(",", ":"))[:800]
        output["selected_ref"] = ref
    rejection_reasons = slot.get("rejection_reasons", {})
    rejected_refs = []
    for source_id in slot.get("rejected_source_ids", []):
        candidate = find_candidate(results, source_id)
        if candidate is None:
            raise ValueError(f"rejected source was not actually retrieved for {slot.get('slot_id')}: {source_id}")
        ref, _ = selected_source(library, candidate)
        rejected_refs.append({
            **ref,
            "reason": rejection_reasons.get(source_id, ""),
            "decision": "REJECT",
        })
    output["rejected_refs"] = rejected_refs
    for transient in ("selected_source_id", "rejected_source_ids", "rejection_reasons", "node_effects"):
        output.pop(transient, None)
    return output


def enrich_option(option: dict[str, Any], search_script: Path, library: Path) -> dict[str, Any]:
    result = copy.deepcopy(option)
    enriched_slots = [enrich_slot(slot, search_script, library) for slot in option.get("material_slots", [])]
    result["material_slots"] = enriched_slots
    nodes = {node["node_id"]: node for node in result.get("story_nodes", [])}
    for node in nodes.values():
        node["material_uses"] = []
    original_slots = {slot["slot_id"]: slot for slot in option.get("material_slots", [])}
    for enriched in enriched_slots:
        original = original_slots[enriched["slot_id"]]
        if enriched.get("decision") not in {"SELECT_DIRECT", "SELECT_ADAPT", "ORIGINAL_DESIGN"}:
            continue
        material_ref = (
            enriched["selected_ref"]["material_id"] if enriched.get("selected_ref")
            else f"ORIGINAL:{enriched['slot_id']}"
        )
        for node_id in original.get("story_node_ids", []):
            if node_id not in nodes:
                raise ValueError(f"material slot references unknown node: {node_id}")
            effect = original.get("node_effects", {}).get(node_id)
            if not effect:
                raise ValueError(f"material slot lacks node-specific effect: {enriched['slot_id']} -> {node_id}")
            nodes[node_id]["material_uses"].append({
                "slot_id": enriched["slot_id"],
                "material_ref": material_ref,
                "role_at_node": enriched.get("abstract_function"),
                "effect_on_action": effect,
            })
    return result


def expand_material_profile(option: dict[str, Any], profiles: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(option)
    profile_id = result.pop("material_profile_id", None)
    bindings = result.pop("material_bindings", {})
    if profile_id not in profiles or not isinstance(bindings, dict):
        raise ValueError(f"material profile/bindings invalid for {result.get('option_id')}: {profile_id}")
    slots = copy.deepcopy(profiles[profile_id])
    for slot in slots:
        binding = bindings.get(slot.get("slot_id"))
        if not isinstance(binding, dict):
            raise ValueError(f"material binding missing: {result.get('option_id')} -> {slot.get('slot_id')}")
        slot["story_node_ids"] = binding.get("story_node_ids", [])
        slot["node_effects"] = binding.get("node_effects", {})
    result["material_slots"] = slots
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Emotion-to-Story Bridge sparse research pilot.")
    parser.add_argument("--brief", type=Path, required=True)
    parser.add_argument("--semantic-composition", type=Path, required=True)
    parser.add_argument("--emotion-library", type=Path, required=True)
    parser.add_argument("--material-snapshot-repo", type=Path, required=True)
    parser.add_argument("--material-snapshot-commit", required=True)
    parser.add_argument("--material-package-subdir", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        brief = read_json(args.brief)
        composition = read_json(args.semantic_composition)
        validate_sparse_brief(brief)
        if composition.get("schema_version") != "emotion_story_semantic_composition_v1":
            raise ValueError("semantic composition schema invalid")
        if composition.get("brief_id") != brief.get("brief_id") or composition.get("status") != "candidate":
            raise ValueError("semantic composition must target the frozen brief and remain candidate")
        output = args.output_dir.resolve()
        if output.exists() and any(output.iterdir()) and not args.force:
            raise ValueError("output directory is not empty; pass --force")
        output.mkdir(parents=True, exist_ok=True)

        retrieval = search_library(args.emotion_library, brief)
        # Do not persist machine-local paths in a committed research artifact.
        retrieval["library"].pop("path", None)
        search_script = Path(__file__).with_name("search_dna_candidates.py")
        with tempfile.TemporaryDirectory(prefix="nova-emotion-story-material-") as tmp:
            source_repo = args.material_snapshot_repo.resolve()
            library = export_package(
                source_repo, args.material_snapshot_commit, args.material_package_subdir, Path(tmp),
            )
            profiles = composition.get("material_profiles", {})
            enhanced_options = [
                enrich_option(expand_material_profile(item, profiles), search_script, library)
                for item in composition.get("enhanced_options", [])
            ]
            legacy_options = [
                enrich_option(expand_material_profile(item, profiles), search_script, library)
                for item in composition.get("legacy_options", [])
            ]

        frozen_hash = brief_hash(brief)
        enhanced = {
            "schema_version": "emotion_story_bridge_options_v1", "mode": "E2_E3_ENABLED",
            "status": "candidate", "qa_status": "HOLD", "brief_sha256": frozen_hash,
            "semantic_composer": composition.get("semantic_composer"), "options": enhanced_options,
        }
        legacy = {
            "schema_version": "emotion_story_bridge_options_v1", "mode": "LEGACY_BASELINE",
            "status": "candidate", "qa_status": "HOLD", "brief_sha256": frozen_hash,
            "semantic_composer": composition.get("semantic_composer"), "options": legacy_options,
        }
        comparison = evaluate(enhanced, legacy, frozen_hash)
        remote = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"], cwd=args.material_snapshot_repo.resolve(),
            capture_output=True, text=True, encoding="utf-8",
        ).stdout.strip()
        manifest = {
            "schema_version": "emotion_story_bridge_run_v1", "status": "candidate", "qa_status": "HOLD",
            "brief_sha256": frozen_hash, "input_mode": "SPARSE_EMOTION_BRIEF",
            "semantic_composer": composition.get("semantic_composer"),
            "material_source": {
                "mode": "FROZEN_GIT_SNAPSHOT", "repository": remote or "LOCAL_GIT_SNAPSHOT",
                "commit": args.material_snapshot_commit, "package_subdir": args.material_package_subdir,
            },
            "emotion_source": {
                "source_book_id": retrieval["library"].get("source_book_id"),
                "source_commit_sha": retrieval["library"].get("source_commit_sha"),
                "package_status": "candidate/HOLD/RESEARCH_NOT_ACTIVE",
            },
            "emotion_library_consumption": "EXECUTED_RESEARCH",
            "material_adaptation": "REVIEW_REQUIRED",
            "creative_quality": "PENDING_INDEPENDENT_REVIEW",
            "production_promotion": "NOT_RUN",
        }
        write_json(output / "sparse-brief.json", brief)
        write_json(output / "emotion-library-retrieval.json", retrieval)
        write_json(output / "enhanced-options.json", enhanced)
        write_json(output / "legacy-options.json", legacy)
        write_json(output / "fair-comparison.json", comparison)
        write_json(output / "run-manifest.json", manifest)
        report = validate_output(output, args.material_snapshot_repo.resolve())
        write_json(output / "validation-report.json", report)
        print(json.dumps({
            "ok": report.get("ok"), "output_dir": str(output),
            "enhanced_options": len(enhanced_options), "legacy_options": len(legacy_options),
            "emotion_library_consumption": report.get("emotion_library_consumption"),
            "material_adaptation": report.get("material_adaptation"),
            "creative_quality": report.get("creative_quality"),
            "production_promotion": report.get("production_promotion"),
            "validation": report,
        }, ensure_ascii=False, indent=2))
        return 0 if report.get("ok") else 1
    except (OSError, ValueError, KeyError, IndexError, json.JSONDecodeError, subprocess.SubprocessError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
