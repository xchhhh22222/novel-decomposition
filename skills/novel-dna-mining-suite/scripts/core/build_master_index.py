#!/usr/bin/env python3
"""Read-only by default: inventory BOOK DNA, emotion overlays, and DNA candidates."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


SPECIALTY_DIRS = {
    "02_金手指": "golden_finger",
    "03_世界观": "worldbuilding",
    "04_修炼体系": "cultivation_system",
    "05_人物功能与标签": "character_function",
    "06_主线与支线": "plotline",
    "07_开篇": "opening",
    "08_篇章结构": "arc_structure",
    "09_剧情机制": "plot_mechanism",
}

SPECIALTY_LABELS = {
    "golden_finger": "GF",
    "worldbuilding": "WB",
    "cultivation_system": "CS",
    "character_function": "CF",
    "plotline": "PL",
    "opening": "OP",
    "arc_structure": "AR",
    "plot_mechanism": "PM",
}


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8-sig")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    data: dict[str, str] = {}
    for line in parts[1].splitlines():
        match = re.match(r"^([A-Za-z0-9_]+):\s*(.*?)\s*$", line)
        if match:
            data[match.group(1)] = match.group(2).strip('"\'')
    return data


def count_emotions(root: Path) -> tuple[Counter, Counter, dict[str, str]]:
    records: Counter = Counter()
    usable: Counter = Counter()
    emotions: dict[str, Counter] = {}
    seen: set[str] = set()
    if not root.exists():
        return records, usable, {}
    for path in root.rglob("*.jsonl"):
        for raw in path.read_text(encoding="utf-8-sig").splitlines():
            if not raw.strip():
                continue
            try:
                row = json.loads(raw)
            except json.JSONDecodeError:
                continue
            # Derived emotion records (per_book/qa/cluster/handoff/gap) share
            # this directory but are not one-record-per-chapter overlays.
            if row.get("record_type") is not None:
                continue
            if not {"book_id", "chapter", "chapter_ref", "main_reader_emotion"}.issubset(row):
                continue
            book_id = str(row.get("book_id", "UNKNOWN"))
            record_id = str(row.get("record_id", f"{book_id}:EMOTION:{row.get('chapter', 'UNKNOWN')}"))
            if record_id in seen:
                continue
            seen.add(record_id)
            records[book_id] += 1
            if row.get("qa_status") != "PASS":
                continue
            usable[book_id] += 1
            emotion = str(row.get("main_reader_emotion", "UNKNOWN"))
            emotions.setdefault(book_id, Counter())[emotion] += 1
    dominant = {
        book_id: counts.most_common(1)[0][0]
        for book_id, counts in emotions.items()
        if counts
    }
    return records, usable, dominant


def parse_scope_count(value: str) -> int | None:
    match = re.search(r"(\d+)\s*-\s*(\d+)", value)
    if not match:
        return None
    start, end = int(match.group(1)), int(match.group(2))
    if end < start:
        return None
    count = end - start + 1
    missing = {int(chapter) for chapter in re.findall(r"缺第\s*(\d+)\s*章", value)}
    return count - len(missing)


def load_scopes(root: Path) -> dict[str, dict[str, object]]:
    scopes: dict[str, dict[str, object]] = {}
    if not root.exists():
        return scopes
    for path in root.rglob("*.jsonl"):
        for raw in path.read_text(encoding="utf-8-sig").splitlines():
            if not raw.strip():
                continue
            try:
                row = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if row.get("record_type") == "book_scope" and row.get("book_id"):
                scopes[str(row["book_id"])] = row
    return scopes


def inventory_specialists(
    root: Path,
) -> tuple[Counter, dict[str, list[str]], dict[str, dict[str, Counter]]]:
    cluster_counts: Counter = Counter()
    paths_by_book: dict[str, list[str]] = {}
    coverage: dict[str, dict[str, Counter]] = {}
    seen: set[tuple[str, str]] = set()
    if not root.exists():
        return cluster_counts, paths_by_book, coverage
    for path in root.rglob("*.jsonl"):
        if "01_章节情绪" in path.parts or "10_总索引" in path.parts or "00_任务清单" in path.parts:
            continue
        relative = path.relative_to(root)
        specialty = SPECIALTY_DIRS.get(relative.parts[0]) if relative.parts else None
        if specialty is None:
            continue
        for number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
            if not raw.strip():
                continue
            try:
                row = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if row.get("status") != "candidate":
                continue
            record_type = str(row.get("record_type", "UNKNOWN"))
            record_id = str(row.get("record_id", f"{path}:{number}"))
            book_ids = row.get("book_ids", [row.get("book_id")])
            if not isinstance(book_ids, list):
                continue
            for book_id in book_ids:
                key = (record_id, str(book_id))
                if book_id and key not in seen:
                    normalized_book_id = str(book_id)
                    if record_type == "cluster":
                        cluster_counts[normalized_book_id] += 1
                    coverage.setdefault(normalized_book_id, {}).setdefault(specialty, Counter())[record_type] += 1
                    paths_by_book.setdefault(normalized_book_id, []).append(str(relative))
                    seen.add(key)
    for book_id, paths in paths_by_book.items():
        paths_by_book[book_id] = sorted(set(paths))
    return cluster_counts, paths_by_book, coverage


def render_specialty_coverage(value: dict[str, Counter]) -> str:
    items = []
    for specialty in SPECIALTY_LABELS:
        counts = value.get(specialty)
        if not counts:
            continue
        label = SPECIALTY_LABELS[specialty]
        if counts.get("gap"):
            state = f"G{counts['gap']}"
        elif counts.get("per_book"):
            state = f"P{counts['per_book']}"
        else:
            state = "-"
        if counts.get("cluster"):
            state += f"/C{counts['cluster']}"
        items.append(f"{label}:{state}")
    return ", ".join(items) or "-"


def map_formal_active_cards(library: Path, titles: dict[str, str]) -> dict[str, list[str]]:
    matches: dict[str, list[str]] = {book_id: [] for book_id in titles}
    root = library / "套路素材"
    if not root.exists():
        return matches
    for path in root.rglob("*.md"):
        meta = parse_frontmatter(path)
        if meta.get("status") != "active":
            continue
        text = path.read_text(encoding="utf-8-sig")
        for book_id, title in titles.items():
            if f"《{title}》" in text:
                matches[book_id].append(str(path.relative_to(library)))
    return matches


def build_rows(library: Path) -> list[dict[str, object]]:
    emotion_records, emotion_usable, dominant = count_emotions(library / "DNA素材" / "01_章节情绪")
    candidate_counts, candidate_paths, specialist_coverage = inventory_specialists(library / "DNA素材")
    scopes = load_scopes(library / "DNA素材" / "00_任务清单")
    dna_files = sorted((library / "00_BOOK_DNA").rglob("BOOK_DNA_*.md"))
    metadata = [(path, parse_frontmatter(path)) for path in dna_files]
    titles = {meta.get("book_id", path.stem): meta.get("title", "UNKNOWN") for path, meta in metadata}
    active_paths = map_formal_active_cards(library, titles)
    rows = []
    for path, meta in metadata:
        book_id = meta.get("book_id", path.stem)
        scope = scopes.get(book_id, {})
        target_count = parse_scope_count(str(scope.get("target_range", "")))
        if target_count is not None:
            target_count -= len(set(scope.get("excluded_chapters", [])))
            target_count -= len(set(scope.get("source_missing_chapters", [])))
        if target_count is None:
            target_count = parse_scope_count(meta.get("chapters_covered", "UNKNOWN"))
        usable = emotion_usable.get(book_id, 0)
        rows.append(
            {
                "book_id": book_id,
                "title": meta.get("title", "UNKNOWN"),
                "market_grade": meta.get("market_grade", "UNGRADED"),
                "genre": meta.get("genre", "UNKNOWN"),
                "golden_finger": meta.get("golden_finger_archetype", "UNKNOWN"),
                "world_type": meta.get("world_type", "UNKNOWN"),
                "chapters_covered": meta.get("chapters_covered", "UNKNOWN"),
                "confidence": meta.get("confidence", "UNKNOWN"),
                "qa_status": scope.get("qa_status", "UNKNOWN"),
                "emotion_records": emotion_records.get(book_id, 0),
                "emotion_usable": usable,
                "target_chapters": target_count if target_count is not None else "UNKNOWN",
                "emotion_coverage": f"{usable}/{target_count if target_count is not None else '?'}",
                "dominant_emotion": dominant.get(book_id, "UNKNOWN"),
                "candidate_count": candidate_counts.get(book_id, 0),
                "candidate_paths": candidate_paths.get(book_id, []),
                "specialty_coverage": {
                    specialty: dict(counts)
                    for specialty, counts in specialist_coverage.get(book_id, {}).items()
                },
                "specialty_coverage_summary": render_specialty_coverage(
                    specialist_coverage.get(book_id, {})
                ),
                "active_card_count": len(active_paths.get(book_id, [])),
                "active_card_paths": active_paths.get(book_id, []),
                "active_mapping_note": "仅统计正式active卡中精确《书名》来源匹配；旧卡或简称来源可能未计入",
                "gaps": scope.get("known_gaps", []),
                "path": str(path.relative_to(library)),
            }
        )
    return rows


def render_markdown(rows: list[dict[str, object]]) -> str:
    header = "| book_id | 书名 | 市场级 | QA | 章节范围 | 情绪可用/目标 | 情绪记录 | 主情绪 | 专项覆盖 | 聚类候选 | 正式卡精确命中 | 缺口 | 导航 |\n|---|---|---|---|---|---|---:|---|---|---:|---:|---|---|"
    body = [
        f"| {r['book_id']} | {r['title']} | {r['market_grade']} | {r['qa_status']} | {r['chapters_covered']} | {r['emotion_coverage']} | {r['emotion_records']} | {r['dominant_emotion']} | {r['specialty_coverage_summary']} | {r['candidate_count']} | {r['active_card_count']} | {', '.join(map(str, r['gaps'])) or '-'} | DNA: {r['path']}; 候选: {'; '.join(r['candidate_paths']) or '-'}; 正式: {'; '.join(r['active_card_paths']) or '-'} |"
        for r in rows
    ]
    return "\n".join([header, *body]) + "\n"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", required=True, type=Path)
    parser.add_argument("--format", choices=("md", "jsonl"), default="md")
    parser.add_argument("--output", type=Path, help="Omit for read-only stdout preview.")
    args = parser.parse_args()
    rows = build_rows(args.library.resolve())
    if args.format == "jsonl":
        content = "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + ("\n" if rows else "")
    else:
        content = render_markdown(rows)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8")
    else:
        print(content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
