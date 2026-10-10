#!/usr/bin/env python3
"""Search a reviewed Emotion Arc V2 research package without promoting it.

The search is intentionally deterministic and modest: it resolves real EL/EW/MA/AH
records, ranks them against high-level emotion dimensions, and exposes the source
mechanism and its limits. Literary selection remains a semantic-composer decision.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


FILES = {
    "line": "emotion-lines.jsonl",
    "weave": "emotion-weaves.jsonl",
    "macro": "macro-emotion-arcs.jsonl",
    "handoff": "arc-handoffs.jsonl",
}

DIMENSION_TERMS = {
    "FAMILY_PROTECTION": ["家庭", "家人", "保护", "安全", "照护", "资源"],
    "GROWTH_COST": ["成长", "力量", "能力", "代价", "限制", "资源", "验证"],
    "RELATIONSHIP_AGENCY": ["关系", "伙伴", "家人", "选择", "互助", "共同", "边界"],
    "LONG_TERM_FACTION_PRESSURE": ["势力", "制度", "压力", "权限", "责任", "公开", "位置"],
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def read_jsonl(path: Path) -> list[tuple[dict[str, Any], str, int]]:
    rows: list[tuple[dict[str, Any], str, int]] = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not raw.strip():
            continue
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ValueError(f"expected object at {path}:{line_no}")
        rows.append((value, raw, line_no))
    return rows


def flatten(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(flatten(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(flatten(item) for item in value)
    return "" if value is None else str(value)


def normalize_terms(values: list[str]) -> list[str]:
    terms: list[str] = []
    for value in values:
        terms.extend(part for part in re.split(r"[\s,，;；/→]+", value) if len(part) >= 2)
    return list(dict.fromkeys(terms))


def validate_library(root: Path) -> dict[str, Any]:
    package = read_json(root / "skill-package.json")
    if package.get("schema_version") != "emotion_arc_skill_package_v1":
        raise ValueError("not an Emotion Arc V2 skill package")
    if package.get("status") != "candidate" or package.get("qa_status") != "HOLD":
        raise ValueError("emotion library must remain candidate/HOLD")
    if package.get("production_promotion") != "NOT_RUN":
        raise ValueError("promoted emotion package is forbidden in this research entry")
    for filename in FILES.values():
        if not (root / filename).is_file():
            raise ValueError(f"emotion package file missing: {filename}")
    return package


def dimensions_from_brief(brief: dict[str, Any]) -> list[dict[str, Any]]:
    required = brief.get("required_emotion_weaves")
    if not isinstance(required, list) or len(required) != 4:
        raise ValueError("SPARSE_EMOTION_BRIEF requires exactly four high-level emotion weave requirements")
    if brief.get("emotion_contour") != ["DOWN", "DOWN", "UP"]:
        raise ValueError("pilot emotion contour must be DOWN/DOWN/UP")
    ids = list(DIMENSION_TERMS)
    return [
        {
            "dimension_id": dimension_id,
            "source_requirement": str(required[index]),
            "derived_search_terms": DIMENSION_TERMS[dimension_id],
            "derivation_status": "PLANNER_WORKING_HYPOTHESIS_NOT_USER_STORY_FACT",
        }
        for index, dimension_id in enumerate(ids)
    ]


def score(text: str, terms: list[str]) -> tuple[int, list[str]]:
    matched = [term for term in terms if term in text]
    return sum(3 if len(term) >= 4 else 2 for term in matched), matched


def provenance(filename: str, line_no: int, raw: str, package: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_book_id": package.get("source_book_id"),
        "source_commit_sha": package.get("source_commit_sha"),
        "record_file": filename,
        "record_line": line_no,
        "record_line_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "source_publication_status": "RESEARCH_NOT_ACTIVE",
        "source_text_audit": package.get("source_text_audit"),
    }


def limits(row: dict[str, Any], extra: list[str] | None = None) -> list[str]:
    values = [
        "candidate/HOLD research record; not a production-approved template",
        "semantic similarity and transferability require independent review",
    ]
    values.extend(str(item) for item in row.get("evidence_gaps", []) if item)
    values.extend(str(item) for item in row.get("unresolved_expectations", []) if item)
    if extra:
        values.extend(extra)
    return list(dict.fromkeys(values))


def search_library(root: Path, brief: dict[str, Any], line_limit: int = 4) -> dict[str, Any]:
    root = root.resolve()
    package = validate_library(root)
    dimensions = dimensions_from_brief(brief)
    records = {kind: read_jsonl(root / filename) for kind, filename in FILES.items()}

    line_rows: list[dict[str, Any]] = []
    selected_line_ids: set[str] = set()
    for dimension in dimensions:
        ranked = []
        for row, raw, line_no in records["line"]:
            haystack = flatten([
                row.get("reader_expectation"), row.get("emotion_target"), row.get("causal_generator"),
                row.get("payoff_contract"), row.get("unresolved_expectations"),
            ])
            points, matched = score(haystack, dimension["derived_search_terms"])
            if points:
                ranked.append((points, row["record_id"], matched, row, raw, line_no))
        for points, _, matched, row, raw, line_no in sorted(ranked, key=lambda item: (-item[0], item[1]))[:line_limit]:
            selected_line_ids.add(row["record_id"])
            line_rows.append({
                "record_id": row["record_id"],
                "record_role": "SINGLE_EMOTION_LINE",
                "matched_dimension": dimension["dimension_id"],
                "similarity_score": points,
                "similarity_reason": f"matched source mechanisms/expectations: {', '.join(matched)}",
                "reader_expectation": row.get("reader_expectation"),
                "transferable_parts": {
                    "causal_generator": row.get("causal_generator"),
                    "payoff_mechanism": row.get("payoff_contract", {}).get("expected_observable_result"),
                    "lifecycle_shape": row.get("lifecycle_status"),
                },
                "limits": limits(row),
                "provenance": provenance(FILES["line"], line_no, raw, package),
            })

    def related_matches(kind: str) -> list[dict[str, Any]]:
        output: list[dict[str, Any]] = []
        all_terms = normalize_terms([brief.get("core_reader_expectation", ""), *brief.get("required_emotion_weaves", [])])
        for row, raw, line_no in records[kind]:
            member_ids = set(row.get("member_line_ids", []))
            member_hits = sorted(member_ids & selected_line_ids)
            text_score, matched = score(flatten(row), all_terms)
            points = text_score + len(member_hits) * 4
            if kind == "handoff":
                points += 4
            if not points:
                continue
            base = {
                "record_id": row["record_id"],
                "similarity_score": points,
                "similarity_reason": (
                    f"links retrieved lines {member_hits or 'none'}; matched terms {matched or 'none'}"
                ),
                "limits": limits(row),
                "provenance": provenance(FILES[kind], line_no, raw, package),
            }
            if kind == "weave":
                base.update({
                    "record_role": "OBSERVED_WEAVE_CANDIDATE",
                    "relation_type": row.get("weave_type"),
                    "member_line_ids": row.get("member_line_ids", []),
                    "transferable_parts": {
                        "relation_type": row.get("weave_type"),
                        "causal_bridge_shape": row.get("causal_explanation"),
                        "before_after_shape": row.get("before_after"),
                    },
                })
            elif kind == "macro":
                base.update({
                    "record_role": "OBSERVED_MACRO_ARC_CANDIDATE",
                    "member_line_ids": row.get("member_line_ids", []),
                    "transferable_parts": {
                        "macro_promise_shape": row.get("reader_macro_promise"),
                        "settlement_contract_shape": row.get("payoff_contract", {}).get("criterion"),
                        "organization_shape": row.get("macro_qualification", {}).get("organization_explanation"),
                    },
                })
            else:
                base.update({
                    "record_role": "UNVERIFIED_HANDOFF_REFERENCE_ONLY",
                    "from_macro_id": row.get("from_macro_id"),
                    "to_macro_id": row.get("to_macro_id"),
                    "transferable_parts": {
                        "overlap_shape": row.get("causal_bridge"),
                        "old_contract_preservation": row.get("handoff_evidence", {}).get("distinct_constraint"),
                    },
                    "observed_overlap": row.get("has_observed_overlap"),
                    "handoff_conclusion": row.get("handoff_conclusion"),
                })
                base["limits"] = limits(row, [
                    "observed overlap does not prove narrative-dominance transfer",
                    "must remain CANDIDATE_UNVERIFIED when reused",
                ])
            output.append(base)
        return sorted(output, key=lambda item: (-item["similarity_score"], item["record_id"]))

    # Deduplicate the same line retrieved by more than one dimension while retaining all reasons.
    grouped: dict[str, dict[str, Any]] = {}
    for match in line_rows:
        record_id = match["record_id"]
        if record_id not in grouped:
            match["matched_dimensions"] = [match.pop("matched_dimension")]
            grouped[record_id] = match
        else:
            grouped[record_id]["matched_dimensions"].append(match["matched_dimension"])
            grouped[record_id]["similarity_score"] = max(grouped[record_id]["similarity_score"], match["similarity_score"])
            grouped[record_id]["similarity_reason"] += "; " + match["similarity_reason"]

    return {
        "schema_version": "emotion_arc_library_retrieval_v1",
        "status": "candidate",
        "qa_status": "HOLD",
        "production_promotion": "NOT_RUN",
        "brief_id": brief.get("brief_id"),
        "library": {
            "package_name": root.name,
            "source_book_id": package.get("source_book_id"),
            "source_commit_sha": package.get("source_commit_sha"),
            "package_status": package.get("status"),
            "semantic_review": package.get("semantic_review"),
        },
        "query_dimensions": dimensions,
        "line_matches": sorted(grouped.values(), key=lambda item: (-item["similarity_score"], item["record_id"])),
        "weave_matches": related_matches("weave"),
        "macro_matches": related_matches("macro"),
        "handoff_matches": related_matches("handoff"),
        "retrieval_interpretation": "deterministic source resolution and similarity hints only; semantic composer chooses and adapts",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Search an Emotion Arc V2 research package.")
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--brief", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--line-limit", type=int, default=4)
    args = parser.parse_args()
    try:
        brief = read_json(args.brief)
        result = search_library(args.library, brief, args.line_limit)
        rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
