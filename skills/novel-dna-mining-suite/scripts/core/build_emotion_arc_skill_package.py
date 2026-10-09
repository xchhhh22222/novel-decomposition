#!/usr/bin/env python3
"""Build a read-only, searchable Emotion Arc V2 skill package.

This entry does not infer literary semantics from raw rows. It consumes an already
reviewed V2 candidate overlay, resolves every canonical dependency through the
existing validator, applies the targeted source-text audit gate, and materializes a
portable research package plus a reader-expectation index.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from validate_emotion_arc_research import validate_pilot


CORE_FILES = (
    "promise-resolution.jsonl",
    "emotion-lines.jsonl",
    "emotion-weaves.jsonl",
    "macro-emotion-arcs.jsonl",
    "arc-handoffs.jsonl",
)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not raw.strip():
            continue
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ValueError(f"expected object at {path}:{number}")
        rows.append(value)
    return rows


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows), encoding="utf-8")


def text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(text(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(text(item) for item in value)
    return "" if value is None else str(value)


def build_expectation_index(
    lines: list[dict[str, Any]], weaves: list[dict[str, Any]], macros: list[dict[str, Any]],
    handoffs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    line_to_macro: dict[str, list[str]] = {}
    for macro in macros:
        for line_id in macro.get("member_line_ids", []):
            line_to_macro.setdefault(line_id, []).append(macro["record_id"])
    line_to_weave: dict[str, list[str]] = {}
    for weave in weaves:
        for line_id in weave.get("member_line_ids", []):
            line_to_weave.setdefault(line_id, []).append(weave["record_id"])
    macro_to_handoff: dict[str, list[str]] = {}
    for handoff in handoffs:
        for key in ("from_macro_id", "to_macro_id"):
            macro_to_handoff.setdefault(str(handoff.get(key)), []).append(handoff["record_id"])

    rows: list[dict[str, Any]] = []
    for line in lines:
        line_id = line["record_id"]
        evidence = sorted({ref for beat in line.get("beats", []) for ref in beat.get("evidence_refs", [])})
        macro_ids = sorted(line_to_macro.get(line_id, []))
        rows.append({
            "schema_version": 1,
            "record_type": "emotion_expectation_index",
            "record_id": f"EEI:{line_id}",
            "status": "candidate",
            "qa_status": "HOLD",
            "origin_kind": "OBSERVED_SOURCE",
            "emotion_line_id": line_id,
            "reader_expectation": line.get("reader_expectation"),
            "emotion_target": line.get("emotion_target"),
            "lifecycle_status": line.get("lifecycle_status"),
            "payoff_contract": line.get("payoff_contract"),
            "unresolved_expectations": line.get("unresolved_expectations", []),
            "macro_arc_ids": macro_ids,
            "weave_ids": sorted(line_to_weave.get(line_id, [])),
            "handoff_ids": sorted({hid for mid in macro_ids for hid in macro_to_handoff.get(mid, [])}),
            "evidence_refs": evidence,
            "search_text": text([
                line.get("reader_expectation"), line.get("emotion_target"), line.get("causal_generator"),
                line.get("payoff_contract"), line.get("unresolved_expectations", []),
            ]),
        })
    return rows


def build_package(pilot: Path, source_repo: Path, output: Path, force: bool = False) -> dict[str, Any]:
    pilot, source_repo, output = pilot.resolve(), source_repo.resolve(), output.resolve()
    if output.exists() and any(output.iterdir()) and not force:
        raise ValueError(f"output directory is not empty: {output}; pass --force to replace research output")
    output.mkdir(parents=True, exist_ok=True)

    report = validate_pilot(pilot, source_repo)
    if not report.get("ok"):
        raise ValueError("existing Emotion Arc V2 validator failed; derivation stopped")
    if report.get("source_text_audit_gate") not in {"PASS", "NOT_ENABLED"}:
        raise ValueError("source-text audit gate did not pass")

    records = {name: read_jsonl(pilot / name) for name in CORE_FILES}
    business_rows = [row for name, rows in records.items() if name != "promise-resolution.jsonl" for row in rows]
    if any(row.get("status") != "candidate" or row.get("qa_status") != "HOLD" for row in business_rows):
        raise ValueError("research package may contain only candidate/HOLD Emotion Arc records")

    for name, rows in records.items():
        write_jsonl(output / name, rows)
    shutil.copyfile(pilot / "source-manifest.json", output / "source-manifest.json")
    audit_path = read_json(pilot / "source-manifest.json").get("source_text_audit_path")
    if audit_path:
        shutil.copyfile(pilot / audit_path, output / audit_path)

    index = build_expectation_index(
        records["emotion-lines.jsonl"], records["emotion-weaves.jsonl"],
        records["macro-emotion-arcs.jsonl"], records["arc-handoffs.jsonl"],
    )
    write_jsonl(output / "reader-expectation-index.jsonl", index)

    manifest = read_json(pilot / "source-manifest.json")
    package = {
        "schema_version": "emotion_arc_skill_package_v1",
        "status": "candidate",
        "qa_status": "HOLD",
        "origin_kind": "OBSERVED_SOURCE",
        "production_promotion": "NOT_RUN",
        "source_book_id": manifest.get("book_id"),
        "source_commit_sha": manifest.get("source_commit_sha"),
        "source_text_audit": report.get("source_trust", {}).get("targeted_source_text_audit"),
        "contract_profile": manifest.get("research_contract_profile"),
        "validator_gates": {
            key: report.get(key) for key in (
                "structural_gate", "source_reference_gate", "source_text_audit_gate", "crosswalk_gate",
                "claim_binding_gate", "weave_causality_evidence_gate", "macro_handoff_gate",
            )
        },
        "record_counts": {name: len(rows) for name, rows in records.items()},
        "expectation_index_count": len(index),
        "files": ["source-manifest.json", *CORE_FILES, "reader-expectation-index.jsonl"] + ([audit_path] if audit_path else []),
        "semantic_review": report.get("semantic_review"),
        "known_holds": [warning for warning in report.get("warnings", []) if warning.get("code") in {
            "CROSSWALK_UNRESOLVED", "PRIOR_ARC_PAYOFF_PENDING", "HANDOFF_UNVERIFIED", "SOURCE_FINGERPRINT_PARTIAL",
        }],
    }
    write_json(output / "skill-package.json", package)
    write_json(output / "derivation-report.json", report)
    return package


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a validated Emotion Arc V2 research skill package.")
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--source-repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        result = build_package(args.pilot_root, args.source_repo, args.output, args.force)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"ok": True, **result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
