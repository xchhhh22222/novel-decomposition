#!/usr/bin/env python3
"""Audit chapter-emotion semantics without changing the canonical schema.

The structural validator answers whether a record is legal JSON.  This audit
answers whether the analysis is independently written, source-grounded, and
manually compared with a required source sample.  It deliberately treats
source contradiction as a human-reviewed gate instead of pretending that a
keyword heuristic understands narrative facts.
"""

from __future__ import annotations

import argparse
import difflib
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


RAW_FIELDS = (
    "emotion_object",
    "expectation_source",
    "pressure_source",
    "turning_point",
    "visible_payoff_evidence",
    "aftermath",
    "ending_aftertaste",
)
ECHO_FIELDS = (
    "emotion_object",
    "pressure_source",
    "turning_point",
    "aftermath",
    "ending_aftertaste",
)
TEMPLATE_FIELDS = RAW_FIELDS
CHAPTER_RE = re.compile(r"(?m)^(?:#\s*)?第\s*([0-9]+)\s*(?:章(?:[：:\s].*)?|\s+\S.*)$")
SENTENCE_RE = re.compile(r"[^。！？!?\n]+[。！？!?]?", re.MULTILINE)
QUOTE_RE = re.compile(r"[“\"『「](.*?)[”\"』」]")
NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")
CHAPTER_NUMBER_RE = re.compile(r"第\s*\d+\s*章")
SPACE_RE = re.compile(r"\s+")
BOILERPLATE_RE = re.compile(
    r"(?:正文结尾证据|本章具体对象|本章门槛变化|本章末可见状态|下一章关注|"
    r"具体余震证据|围绕|读者等待|所代表的状态改变|显示的资源/认知门槛|"
    r"完成一次具体选择|带来的具体后果)[:：]?"
)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not raw.strip():
            continue
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ValueError(f"line {number}: expected a JSON object")
        rows.append(value)
    return rows


def text_value(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        return "；".join(item.strip() for item in value if isinstance(item, str) and item.strip())
    return ""


def compact(value: str) -> str:
    return re.sub(r"[^\w\u3400-\u9fff]+", "", value).lower()


def similarity(left: str, right: str) -> float:
    a, b = compact(left), compact(right)
    if not a or not b:
        return 0.0
    if min(len(a), len(b)) >= 10 and (a in b or b in a):
        return min(len(a), len(b)) / max(len(a), len(b))
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def parse_source(path: Path) -> dict[int, str]:
    text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    headings = list(CHAPTER_RE.finditer(text))
    chapters: dict[int, str] = {}
    for index, match in enumerate(headings):
        chapter = int(match.group(1))
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        chapters[chapter] = text[match.end():end].strip()
    return chapters


def final_sentences(chapter_text: str, count: int = 3) -> list[str]:
    lines = [line.strip() for line in chapter_text.splitlines()]
    lines = [line for line in lines if line and not line.startswith("章节更新时间") and set(line) != {"—"}]
    sentences: list[str] = []
    for line in lines:
        sentences.extend(piece.strip() for piece in SENTENCE_RE.findall(line) if piece.strip())
    return sentences[-count:]


def source_candidates(sentences: list[str]) -> list[str]:
    candidates = list(sentences)
    for width in (2, 3):
        if len(sentences) >= width:
            candidates.append("".join(sentences[-width:]))
    return candidates


def raw_ending_flags(rows: list[dict[str, Any]], sources: dict[int, str]) -> list[dict[str, Any]]:
    flags: list[dict[str, Any]] = []
    for row in rows:
        chapter = row.get("chapter")
        if not isinstance(chapter, int) or chapter not in sources:
            continue
        endings = source_candidates(final_sentences(sources[chapter]))
        matched: dict[str, str] = {}
        for field in RAW_FIELDS:
            value = text_value(row.get(field))
            if not value:
                continue
            best = max(endings, key=lambda ending: similarity(value, ending), default="")
            if best and (compact(best) in compact(value) or similarity(value, best) >= 0.72):
                matched[field] = best
        if len(matched) >= 3:
            flags.append({"chapter": chapter, "matched_fields": sorted(matched), "source_endings": sorted(set(matched.values()))})
    return flags


def stripped_analysis(value: str, title: str = "") -> str:
    value = BOILERPLATE_RE.sub("", value)
    value = QUOTE_RE.sub("<QUOTE>", value)
    value = CHAPTER_NUMBER_RE.sub("<CH>", value)
    value = NUMBER_RE.sub("<NUM>", value)
    if title:
        value = value.replace(title, "<TITLE>")
    return SPACE_RE.sub("", value)


def field_echo_flags(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    flags: list[dict[str, Any]] = []
    for row in rows:
        values = {field: stripped_analysis(text_value(row.get(field)), str(row.get("chapter_title", ""))) for field in ECHO_FIELDS}
        values = {field: value for field, value in values.items() if value}
        adjacency: dict[str, set[str]] = defaultdict(set)
        fields = list(values)
        for index, left in enumerate(fields):
            for right in fields[index + 1:]:
                if similarity(values[left], values[right]) >= 0.62:
                    adjacency[left].add(right)
                    adjacency[right].add(left)
        groups: list[set[str]] = []
        seen: set[str] = set()
        for field in fields:
            if field in seen:
                continue
            stack, group = [field], set()
            while stack:
                current = stack.pop()
                if current in group:
                    continue
                group.add(current)
                stack.extend(adjacency[current])
            seen.update(group)
            groups.append(group)
        largest = max(groups, key=len, default=set())
        if len(largest) >= 3:
            flags.append({"chapter": row.get("chapter"), "echo_fields": sorted(largest)})
    return flags


def skeleton(value: str, title: str = "") -> str:
    value = stripped_analysis(value, title)
    # Long quoted/event payloads and variable CJK spans are reduced while
    # retaining stable connective phrases that reveal a template.
    value = re.sub(r"<QUOTE>", "<ENTITY>", value)
    value = re.sub(r"[A-Za-z_]+", "<ENTITY>", value)
    return value


def clusters_for_field(rows: list[dict[str, Any]], field: str) -> list[list[int]]:
    clusters: list[tuple[str, list[int]]] = []
    for row in rows:
        chapter = row.get("chapter")
        value = skeleton(text_value(row.get(field)), str(row.get("chapter_title", "")))
        if not value or not isinstance(chapter, int):
            continue
        placed = False
        for index, (representative, members) in enumerate(clusters):
            if similarity(value, representative) >= 0.78:
                members.append(chapter)
                if len(value) < len(representative):
                    clusters[index] = (value, members)
                placed = True
                break
        if not placed:
            clusters.append((value, [chapter]))
    return [members for _representative, members in clusters]


def has_consecutive_run(chapters: Iterable[int], minimum: int = 5) -> bool:
    values = sorted(set(chapters))
    run = 1
    for previous, current in zip(values, values[1:]):
        run = run + 1 if current == previous + 1 else 1
        if run >= minimum:
            return True
    return len(values) >= minimum and minimum <= 1


def template_flags(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    flags: list[dict[str, Any]] = []
    for field in TEMPLATE_FIELDS:
        for members in clusters_for_field(rows, field):
            if len(members) >= 10 or has_consecutive_run(members, 5):
                flags.append({"field": field, "chapters": members, "count": len(members), "consecutive_5": has_consecutive_run(members, 5)})
    return flags


def audit_source_review(path: Path | None, rows: list[dict[str, Any]]) -> tuple[str, list[str], dict[str, Any]]:
    errors: list[str] = []
    total = len(rows)
    required_count = max(10, math.ceil(total * 0.10))
    details: dict[str, Any] = {"required_sample_count": required_count}
    if path is None or not path.exists():
        return "SOURCE_SAMPLE_REVIEW_REQUIRED", ["manual source review file is required"], details
    review = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(review, dict):
        return "FAIL", ["source review must be a JSON object"], details
    if review.get("reviewer") != "SOL":
        errors.append("reviewer must be SOL")
    samples = review.get("samples")
    if not isinstance(samples, list):
        samples = []
        errors.append("samples must be a list")
    by_chapter = {item.get("chapter"): item for item in samples if isinstance(item, dict) and isinstance(item.get("chapter"), int)}
    details["reviewed_chapters"] = sorted(by_chapter)
    if len(by_chapter) < required_count:
        errors.append(f"reviewed {len(by_chapter)} chapters; require at least {required_count}")
    last = max((row.get("chapter") for row in rows if isinstance(row.get("chapter"), int)), default=None)
    required = {1}
    if last is not None:
        required.add(last)
    opening_end = review.get("opening_window_end")
    if isinstance(opening_end, int):
        required.add(opening_end)
    else:
        errors.append("opening_window_end is required")
    arc_turns = review.get("arc_turn_chapters")
    if isinstance(arc_turns, list) and all(isinstance(value, int) for value in arc_turns):
        required.update(arc_turns)
    else:
        errors.append("arc_turn_chapters must be a list of chapter numbers")
    missing = sorted(required - set(by_chapter))
    if missing:
        errors.append(f"required source-review chapters missing: {missing}")
    contradictions = sorted(chapter for chapter, item in by_chapter.items() if item.get("result") == "FAIL")
    invalid_results = sorted(chapter for chapter, item in by_chapter.items() if item.get("result") not in {"PASS", "FAIL"})
    if invalid_results:
        errors.append(f"sample results must be PASS/FAIL: {invalid_results}")
    if contradictions:
        errors.append(f"source contradictions found: {contradictions}")
    details["contradiction_chapters"] = contradictions
    return ("FAIL" if errors else "PASS"), errors, details


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Audit semantic quality of canonical chapter-emotion JSONL.")
    parser.add_argument("emotion_file", type=Path)
    parser.add_argument("--source-file", type=Path, required=True, help="Full source book used to compare chapter endings.")
    parser.add_argument("--source-review", type=Path, help="SOL manual source-sample review JSON.")
    parser.add_argument("--output", type=Path, help="Optional JSON report path.")
    args = parser.parse_args()

    rows = read_jsonl(args.emotion_file)
    sources = parse_source(args.source_file)
    raw_flags = raw_ending_flags(rows, sources)
    echo_flags = field_echo_flags(rows)
    template_hits = template_flags(rows)
    total = len(rows)
    raw_hard = len(raw_flags) >= max(1, math.ceil(total * 0.10))
    echo_hard = len(echo_flags) >= 10
    template_chapters = sorted({chapter for hit in template_hits for chapter in hit["chapters"]})
    template_hard = len(template_chapters) >= max(1, math.ceil(total * 0.20))
    source_status, source_errors, source_details = audit_source_review(args.source_review, rows)
    gates = {
        "RAW_ENDING_GATE": "FAIL" if raw_hard else "PASS",
        "FIELD_ECHO_GATE": "FAIL" if echo_hard else "PASS",
        "NORMALIZED_TEMPLATE_GATE": "FAIL" if template_hard else "PASS",
        "ANALYSIS_VS_SUMMARY_GATE": "FAIL" if echo_hard else "PASS",
        "SOURCE_CONTRADICTION_GATE": source_status,
    }
    result = {
        "records": total,
        "source_chapters": len(sources),
        "gates": gates,
        "diagnostics": {
            "raw_ending_flag_count": len(raw_flags),
            "raw_ending_flags": raw_flags,
            "field_echo_flag_count": len(echo_flags),
            "field_echo_flags": echo_flags,
            "template_chapter_count": len(template_chapters),
            "template_hits": template_hits,
            "source_review": source_details,
            "source_review_errors": source_errors,
            "unique_counts": {field: len({text_value(row.get(field)) for row in rows}) for field in RAW_FIELDS},
            "unique_counts_are_diagnostic_only": True,
        },
        "ok": all(status == "PASS" for status in gates.values()),
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
