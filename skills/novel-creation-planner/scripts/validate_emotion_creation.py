#!/usr/bin/env python3
"""Validate emotion-first candidate composition without redefining source QA.

This is an opt-in, pre-plan validator. Existing creation-plan schema v1/v2 and
their validator remain unchanged. Machine PASS is structural, not literary approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

GAP_TYPES = {
    "SOURCE_GAP", "RETRIEVAL_GAP", "INTERFACE_GAP",
    "ADAPTATION_REQUIRED", "CREATIVE_OPEN_CHOICE",
}
MODULES = {
    "golden_finger": "02_金手指", "worldbuilding": "03_世界观",
    "cultivation_system": "04_修炼体系",
    "character_function": "05_人物功能与标签",
    "plotline": "06_主线与支线", "opening": "07_开篇",
    "arc_structure": "08_篇章结构", "plot_mechanism": "09_剧情机制",
}
REQUIRED_BY_OUTPUT = {
    "growth_loop": {"golden_finger", "worldbuilding", "cultivation_system"},
    "story_spine": {"plotline"},
    "opening": {"opening"},
    "major_climaxes": {"arc_structure"},
    "repeating_plot_engine": {"plot_mechanism"},
    "relationships": {"character_function"},
}
REF_SOURCE_KINDS = {"RESEARCH_VERIFIED", "ORIGINAL_DESIGN"}
STATUS_COMPAT = {"DIRECT_FIT", "ADAPTABLE", "HOLD", "HARD_CONFLICT"}
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:/#-]*$")


def error(errors: list[str], where: str, message: str) -> None:
    errors.append(f"{where}: {message}")


def object_at(value: Any, where: str, errors: list[str]) -> dict:
    if not isinstance(value, dict):
        error(errors, where, "must be an object")
        return {}
    return value


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_array(value: Any) -> bool:
    return isinstance(value, list) and all(nonempty(s) for s in value)


def unique_ids(rows: Any, key: str, where: str, errors: list[str]) -> dict[str, dict]:
    if not isinstance(rows, list):
        error(errors, where, "must be a list")
        return {}
    by_id = {}
    for i, row in enumerate(rows):
        loc = f"{where}[{i}]"
        row = object_at(row, loc, errors)
        ident = row.get(key)
        if not nonempty(ident):
            error(errors, loc, f"missing {key}")
        elif ident in by_id:
            error(errors, loc, f"duplicate {key}={ident}")
        else:
            by_id[ident] = row
    return by_id


def load_active_library(root: Any, errors: list[str]) -> tuple[Path | None, dict]:
    if not nonempty(root):
        error(errors, "shared_library_root", "must be absolute production package path")
        return None, {}
    package = Path(root)
    if not package.is_absolute() or not package.is_dir():
        error(errors, "shared_library_root", "production package directory not accessible")
        return None, {}
    try:
        manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        error(errors, "library_integrity", f"manifest unreadable: {exc}")
        return None, {}
    if (manifest.get("package_id") != "nova-shared-dna-library"
            or manifest.get("status") != "ACTIVE_SHARED_LIBRARY"
            or manifest.get("active") is not True):
        error(errors, "library_integrity", "requires ACTIVE_SHARED_LIBRARY with active=true")
        return None, {}
    from search_dna_candidates import verify_shared_dna_package_integrity
    violations = verify_shared_dna_package_integrity(package, manifest)
    for violation in violations:
        error(errors, "library_integrity", violation)
    return (package if not violations else None), manifest


def locate_record(package: Path, manifest: dict, source: dict, where: str, errors: list[str]) -> dict | None:
    rel = source.get("source_path")
    if not nonempty(rel):
        error(errors, where, "source_path required")
        return None
    if rel not in (manifest.get("artifact_paths") or {}).values():
        error(errors, where, "source_path not declared in active package")
        return None
    path = (package / rel).resolve()
    if package.resolve() not in path.parents or path.suffix != ".jsonl" or "DNA素材" not in path.parts:
        error(errors, where, "source_path is not a package DNA JSONL")
        return None
    try:
        rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    except (OSError, ValueError) as exc:
        error(errors, where, f"unable to read source: {exc}")
        return None
    candidates = [r for r in rows if isinstance(r, dict) and r.get("record_id") == source.get("record_id")]
    if len(candidates) != 1:
        error(errors, where, "record_id absent or ambiguous in declared source_path")
        return None
    row = candidates[0]
    if row.get("book_id") != source.get("book_id"):
        error(errors, where, "book_id does not match source record")
    if row.get("status") != "candidate" or row.get("qa_status") != "PASS":
        error(errors, where, "source record must have status=candidate and qa_status=PASS")
    if source.get("source_qa_status") != row.get("qa_status"):
        error(errors, where, "source_qa_status does not match actual record")
    module = source.get("module")
    if module not in MODULES or MODULES[module] not in path.parts:
        error(errors, where, "module/path mismatch")
    child = row
    selector = source.get("component_path")
    if selector:
        parts = re.findall(r"([^.\[\]]+)|\[(\d+)\]", str(selector))
        reconstructed = "".join(f".{a}" if a else f"[{b}]" for a, b in parts).lstrip(".")
        if reconstructed != selector:
            error(errors, where, "invalid component_path syntax")
            return None
        try:
            for key, index in parts:
                child = child[key] if key else child[int(index)]
        except (KeyError, TypeError, IndexError):
            error(errors, where, "component_path does not resolve in source record")
            return None
        if not isinstance(child, dict):
            error(errors, where, "component_path must select a full component object")
            return None
        cid = source.get("component_id")
        if not nonempty(cid):
            error(errors, where, "component_id required for nested component")
        else:
            identifiers = {
                value for key, value in child.items()
                if key.endswith("_id") and isinstance(value, str) and value
            }
            # Synthetic ids are accepted when parent + path is explicitly anchored.
            if cid not in identifiers and not str(cid).startswith(str(row["record_id"]) + "#"):
                error(errors, where, "component_id not supported by selected component")
    elif source.get("component_id"):
        error(errors, where, "component_id without component_path")
    refs = source.get("evidence_refs")
    available = set(row.get("evidence_refs") or []) | set(child.get("evidence_refs") or [])
    if not string_array(refs) or not refs:
        error(errors, where, "nonempty evidence_refs required")
    elif not set(refs) & available:
        error(errors, where, "evidence_refs do not resolve to source/component evidence")
    return row


def validate_pattern(pid: str, row: dict, errors: list[str]) -> None:
    where = f"emotion_patterns.{pid}"
    kind = row.get("source_kind")
    if kind not in REF_SOURCE_KINDS:
        error(errors, where, "source_kind must be RESEARCH_VERIFIED or ORIGINAL_DESIGN")
    if kind == "RESEARCH_VERIFIED":
        if row.get("source_publication_status") != "RESEARCH_NOT_ACTIVE":
            error(errors, where, "01 emotion research cannot be labeled ACTIVE_SHARED_LIBRARY")
        if not string_array(row.get("source_evidence_refs")) or not row["source_evidence_refs"]:
            error(errors, where, "research pattern needs chapter evidence refs")
        if row.get("research_evidence_check") != "VERIFIED":
            error(errors, where, "research pattern needs separately verified evidence check")
    if not nonempty(row.get("reader_promise")):
        error(errors, where, "reader_promise required")
    beats = row.get("beats")
    if not isinstance(beats, list) or len(beats) < 3:
        error(errors, where, "at least three causal beats required")
        return
    for i, beat in enumerate(beats):
        for field in ("reader_emotion", "expectation", "causal_event", "character_agency", "state_change"):
            if not nonempty(beat.get(field) if isinstance(beat, dict) else None):
                error(errors, f"{where}.beats[{i}]", f"{field} required; emotion labels alone are invalid")
        if i > 0 and not nonempty(beat.get("depends_on_prior") if isinstance(beat, dict) else None):
            error(errors, f"{where}.beats[{i}]", "depends_on_prior required")
    if not nonempty(row.get("visible_payoff")) or not nonempty(row.get("aftermath")):
        error(errors, where, "visible_payoff and aftermath required")


def validate_draft(data: Any) -> dict:
    errors: list[str] = []
    data = object_at(data, "draft", errors)
    if data.get("schema_version") != 1 or data.get("design_mode") != "EMOTION_FIRST":
        error(errors, "draft", "requires schema_version=1, design_mode=EMOTION_FIRST")
    if data.get("status") != "DRAFT":
        error(errors, "draft", "status must be DRAFT; validator does not approve a novel")
    package, manifest = load_active_library(data.get("shared_library_root"), errors)
    patterns = unique_ids(data.get("emotion_patterns"), "pattern_id", "emotion_patterns", errors)
    for pid, row in patterns.items():
        validate_pattern(pid, row, errors)
    materials = unique_ids(data.get("materials"), "material_id", "materials", errors)
    for mid, item in materials.items():
        where = f"materials.{mid}"
        source = object_at(item.get("source"), where+".source", errors)
        if package is not None:
            locate_record(package, manifest, source, where+".source", errors)
        inter = object_at(item.get("interface"), where+".interface", errors)
        for key in ("inputs", "outputs", "dependencies", "constraints", "unknowns"):
            if not string_array(inter.get(key)):
                error(errors, where+".interface", f"{key} must be a string array")
        if not inter.get("outputs"):
            error(errors, where+".interface", "outputs must not be empty")
        if item.get("interface_readiness") not in {"READY", "PARTIAL", "HOLD"}:
            error(errors, where, "interface_readiness invalid")
        if not nonempty(item.get("interface_reason")):
            error(errors, where, "interface_reason required; source QA is not interface QA")
        if item.get("interface_readiness") == "READY" and (not inter.get("inputs") or inter.get("unknowns")):
            error(errors, where, "READY needs explicit inputs and no unresolved interface unknowns")
    options = unique_ids(data.get("options"), "option_id", "options", errors)
    for oid, option in options.items():
        where = f"options.{oid}"
        if option.get("status") not in {"DRAFT", "READY_FOR_HUMAN_REVIEW", "HOLD"}:
            error(errors, where, "status invalid")
        chosen_patterns = option.get("emotion_pattern_ids")
        if not string_array(chosen_patterns) or not chosen_patterns:
            error(errors, where, "emotion_pattern_ids required")
        else:
            for pid in chosen_patterns:
                if pid not in patterns:
                    error(errors, where, f"unknown emotion pattern {pid}")
        outputs = option.get("deliverables")
        if not isinstance(outputs, list) or not set(outputs) <= set(REQUIRED_BY_OUTPUT):
            error(errors, where, "deliverables must name supported outputs")
            outputs = []
        required_modules = set().union(*(REQUIRED_BY_OUTPUT[o] for o in outputs)) if outputs else set()
        slots = unique_ids(option.get("slots"), "slot_id", where+".slots", errors)
        covered = set()
        selected = set()
        for sid, slot in slots.items():
            loc = f"{where}.slots.{sid}"
            module = slot.get("module")
            if module not in MODULES:
                error(errors, loc, "unknown module")
                continue
            ids = slot.get("material_ids")
            if not isinstance(ids, list):
                error(errors, loc, "material_ids must be a list")
                ids = []
            gap = slot.get("gap")
            for mid in ids:
                if mid not in materials:
                    error(errors, loc, f"unknown material_id {mid}")
                elif materials[mid].get("source", {}).get("module") != module:
                    error(errors, loc, f"material {mid} has wrong module")
                else:
                    selected.add(mid)
            if ids and gap:
                error(errors, loc, "cannot claim both selected materials and a gap")
            if not ids:
                if not isinstance(gap, dict) or gap.get("type") not in GAP_TYPES or not nonempty(gap.get("reason")) or not nonempty(gap.get("next_action")):
                    error(errors, loc, "unfilled slot requires typed gap + reason + next_action")
                elif gap["type"] == "CREATIVE_OPEN_CHOICE" and not nonempty(gap.get("original_design")):
                    error(errors, loc, "original-design gap needs explicit original_design")
            covered.add(module)
        for missing in sorted(required_modules - covered):
            error(errors, where, f"required module {missing} absent for declared deliverables")
        links = option.get("compatibility_checks")
        if not isinstance(links, list):
            error(errors, where, "compatibility_checks must be an array")
            links = []
        referenced = set()
        for i, link in enumerate(links):
            loc = f"{where}.compatibility_checks[{i}]"
            if not isinstance(link, dict):
                error(errors, loc, "must be an object")
                continue
            left, right = link.get("from_material_id"), link.get("to_material_id")
            if left not in selected or right not in selected or left == right:
                error(errors, loc, "link endpoints must be distinct selected material_ids")
                continue
            referenced.update((left, right))
            match = link.get("result")
            if match not in STATUS_COMPAT:
                error(errors, loc, "invalid compatibility result")
            if not nonempty(link.get("source_output")) or not nonempty(link.get("target_input")):
                error(errors, loc, "explicit source_output and target_input required")
            if not nonempty(link.get("reason")):
                error(errors, loc, "reason required")
            if match == "DIRECT_FIT":
                outputs_a = materials[left].get("interface", {}).get("outputs", [])
                inputs_b = materials[right].get("interface", {}).get("inputs", [])
                if link.get("source_output") not in outputs_a or link.get("target_input") not in inputs_b:
                    error(errors, loc, "DIRECT_FIT must cite actual source/target interface fields")
                if link.get("source_output") != link.get("target_input"):
                    error(errors, loc, "DIRECT_FIT needs matching interface tokens; else ADAPTABLE")
            if match == "ADAPTABLE":
                bridge = object_at(link.get("bridge"), loc+".bridge", errors)
                for key in ("new_rule", "cost_or_constraint", "changed_state", "why_causal"):
                    if not nonempty(bridge.get(key)):
                        error(errors, loc+".bridge", f"{key} required for original adaptation")
                if bridge.get("provenance") != "ORIGINAL_DESIGN":
                    error(errors, loc+".bridge", "bridge must be marked ORIGINAL_DESIGN, not source fact")
        if len(selected) > 1 and not links:
            error(errors, where, "multiple materials require at least one real compatibility check")
        if option.get("status") == "READY_FOR_HUMAN_REVIEW":
            if any(slot.get("gap") for slot in slots.values()):
                error(errors, where, "READY cannot contain unresolved gaps")
            if any(m.get("interface_readiness") != "READY" for mid, m in materials.items() if mid in selected):
                error(errors, where, "READY cannot use PARTIAL/HOLD interfaces")
            if not links or any(l.get("result") not in {"DIRECT_FIT", "ADAPTABLE"} for l in links if isinstance(l, dict)):
                error(errors, where, "READY needs positive compatibility checks")
            if len(referenced) < len(selected):
                error(errors, where, "READY requires all selected materials to join compatibility graph")
        # DRAFT and HOLD may have unresolved gaps, but never report a successful gate here.
    return {
        "ok": not errors,
        "machine_check": "STRUCTURAL_ONLY",
        "library_integrity": "PASS" if package is not None else "FAIL",
        "source_trust": "PASS" if not any("materials." in e and ".source" in e for e in errors) else "FAIL",
        "interface_readiness": "PASS" if not any("materials." in e and ".interface" in e for e in errors) else "FAIL",
        "current_compatibility": "PASS" if not any("compatibility_checks" in e for e in errors) else "FAIL",
        "emotion_causality": "PASS" if not any("emotion_patterns." in e for e in errors) else "FAIL",
        "creation_approval": "NOT_GRANTED",
        "option_ids": sorted(options),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check emotion-first candidate design and production-source closure.")
    parser.add_argument("target", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.target.read_text(encoding="utf-8-sig"))
        report = validate_draft(data)
    except (OSError, ValueError, TypeError) as exc:
        report = {"ok": False, "errors": [str(exc)]}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
