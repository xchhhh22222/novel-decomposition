#!/usr/bin/env python3
"""Read-only search over novel DNA candidate/per-book JSONL records."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


MODULES = {
    "02_金手指": "golden_finger",
    "03_世界观": "worldbuilding",
    "04_修炼体系": "cultivation_system",
    "05_人物功能与标签": "character_function",
    "06_主线与支线": "plotline",
    "07_开篇": "opening",
    "08_篇章结构": "arc_structure",
    "09_剧情机制": "plot_mechanism",
}

ALIASES = {
    "金手指": "golden_finger",
    "世界观": "worldbuilding",
    "修炼体系": "cultivation_system",
    "人物": "character_function",
    "女主": "character_function",
    "反派": "character_function",
    "长线反派": "character_function",
    "大故事线": "arc_structure",
    "人物功能": "character_function",
    "主线": "plotline",
    "支线": "plotline",
    "开篇": "opening",
    "篇章": "arc_structure",
    "篇章结构": "arc_structure",
    "剧情机制": "plot_mechanism",
    "机制": "plot_mechanism",
    "gf": "golden_finger",
    "wb": "worldbuilding",
    "cs": "cultivation_system",
    "cf": "character_function",
    "pl": "plotline",
    "op": "opening",
    "ar": "arc_structure",
    "pm": "plot_mechanism",
}

TITLE_FIELDS = (
    "character_label",
    "label",
    "archetype",
    "normalized_archetype",
    "mechanic_name_in_book",
    "world_core_premise",
    "title",
)

SUMMARY_FIELDS = (
    "spine_summary",
    "core_drive",
    "independent_goal",
    "villain_goal",
    "protagonist_gains",
    "plan_disruptions",
    "shared_operation",
    "shared_mechanism",
    "core_formula",
    "world_core_premise",
    "reader_promise",
    "window_progression_pattern",
    "selling_point_promise_payoff_pattern",
    "variation_pattern",
)


def split_values(value: str) -> list[str]:
    return [part.strip() for part in re.split(r"[\s,，;；]+", value) if part.strip()]


def flatten(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(f"{key} {flatten(item)}" for key, item in value.items())
    if isinstance(value, list):
        return " ".join(flatten(item) for item in value)
    return "" if value is None else str(value)


def compact(value: Any, limit: int = 280) -> str:
    text = flatten(value)
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


def result_summary(module: str, row: dict[str, Any]) -> str:
    """Show a useful preview even for per-book modules without a flat summary field."""
    flat = next((compact(row.get(field)) for field in SUMMARY_FIELDS if row.get(field)), "")
    if flat:
        return flat
    if module == "character_function":
        people = row.get("person_scope") or []
        functions = row.get("narrative_functions") or []
        pieces = [compact(people[:4], 140)]
        pieces.extend(compact(item.get("actual_operation"), 100) for item in functions[:2] if isinstance(item, dict))
        return compact("；".join(piece for piece in pieces if piece))
    if module == "arc_structure":
        arcs = row.get("arcs") or []
        pieces = []
        for arc in arcs[:3]:
            if isinstance(arc, dict):
                identity = arc.get("arc_identity") or {}
                pieces.append(f"{identity.get('arc_scope', '?')} {identity.get('arc_label', '')}")
        return compact("；".join(pieces))
    for field in ("plotline_scope", "opening_window", "mechanism_instances", "evidence_refs"):
        if row.get(field):
            return compact(row[field])
    return ""


def bigrams(text: str) -> set[str]:
    normalized = re.sub(r"\s+", "", text.lower())
    return {normalized[index : index + 2] for index in range(max(0, len(normalized) - 1))}


def iter_jsonl(path: Path) -> Iterable[tuple[int, dict[str, Any]]]:
    for number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            yield number, row


def normalize_modules(raw: str) -> set[str]:
    result: set[str] = set()
    for value in split_values(raw.lower()):
        result.add(ALIASES.get(value, value))
    return result


def discover_paths(root: Path, include_per_book: bool) -> Iterable[tuple[str, Path]]:
    for dirname, module in MODULES.items():
        module_root = root / dirname
        cluster = module_root / "candidate" / "clusters.jsonl"
        if cluster.exists():
            yield module, cluster
        if include_per_book:
            per_book = module_root / "per_book"
            if per_book.exists():
                for path in sorted(per_book.glob("*.jsonl")):
                    yield module, path
            derived = module_root / "derived"
            if derived.exists():
                for path in sorted(derived.rglob("*.jsonl")):
                    yield module, path


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Search novel DNA candidates without modifying the library.")
    parser.add_argument("--library", type=Path, required=True, help="Material library root containing DNA素材.")
    parser.add_argument("--query", required=True, help="Space/comma separated functional search terms.")
    parser.add_argument("--modules", default="", help="Optional module names/slugs/abbreviations.")
    parser.add_argument("--exclude", default="", help="Terms that disqualify a record.")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--include-per-book", action="store_true")
    parser.add_argument("--record-types", default="", help="Optional comma/space separated record_type filter.")
    parser.add_argument("--format", choices=("jsonl", "json", "md"), default="jsonl")
    args = parser.parse_args()

    root = args.library.resolve() / "DNA素材"
    if not root.exists():
        parser.error(f"DNA素材 not found under {args.library}")
    wanted_modules = normalize_modules(args.modules) if args.modules else set()
    wanted_types = set(split_values(args.record_types)) if args.record_types else set()
    terms = split_values(args.query.lower())
    excludes = split_values(args.exclude.lower())
    if not terms:
        parser.error("--query must contain at least one term")

    results: list[dict[str, Any]] = []
    for module, path in discover_paths(root, args.include_per_book):
        if wanted_modules and module not in wanted_modules:
            continue
        relative = path.relative_to(args.library.resolve()).as_posix()
        for number, row in iter_jsonl(path):
            if wanted_types and row.get("record_type") not in wanted_types:
                continue
            if row.get("status") != "candidate":
                continue
            if row.get("qa_status") == "FAIL":
                continue
            title = next((compact(row.get(field), 160) for field in TITLE_FIELDS if row.get(field)), "")
            full_text = flatten(row).lower()
            if any(term in full_text for term in excludes):
                continue
            why: list[str] = []
            score = 0.0
            title_lower = title.lower()
            for term in terms:
                title_hits = title_lower.count(term)
                body_hits = full_text.count(term)
                if title_hits:
                    score += 8 + min(title_hits - 1, 2) * 2
                    why.append(f"标题:{term}")
                elif body_hits:
                    score += 3 + min(body_hits - 1, 3)
                    why.append(f"正文:{term}")
            query_bigrams = bigrams("".join(terms))
            record_bigrams = bigrams(title + " " + compact(row, 1200))
            if query_bigrams:
                overlap = len(query_bigrams & record_bigrams) / len(query_bigrams)
                score += overlap * 6
                if overlap >= 0.15 and not why:
                    why.append(f"语义字组:{round(overlap * 100)}%")
            if score <= 0:
                continue
            if row.get("confidence") == "HIGH":
                score += 1
            support = row.get("supporting_book_count", row.get("source_count"))
            if isinstance(support, int) and support > 1:
                score += min(support, 5) * 0.2
            summary = result_summary(module, row)
            results.append(
                {
                    "record_id": row.get("record_id", row.get("cluster_id", f"{relative}:{number}")),
                    "record_type": row.get("record_type"),
                    "module": module,
                    "title": title,
                    "score": round(score, 2),
                    "why": why,
                    "confidence": row.get("confidence"),
                    "qa_status": row.get("qa_status"),
                    "usage_status": "HOLD" if row.get("qa_status") == "HOLD" else ("ADAPTABLE_WITH_GAPS" if row.get("unknowns") else "ADAPTABLE"),
                    "supporting_book_count": support,
                    "summary": summary,
                    "path": relative,
                    "line": number,
                }
            )
    results.sort(key=lambda item: (-item["score"], item["module"], str(item["record_id"])))
    results = results[: max(1, args.limit)]
    payload = {
        "query": args.query,
        "modules": sorted(wanted_modules),
        "include_per_book": args.include_per_book,
        "returned": len(results),
        "results": results,
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif args.format == "md":
        print(f"# DNA候选检索\n\n- query: `{args.query}`\n- returned: {len(results)}\n")
        print("| score | module | record_id | title | path |")
        print("|---:|---|---|---|---|")
        for item in results:
            print(f"| {item['score']} | {item['module']} | {item['record_id']} | {item['title']} | {item['path']} |")
    else:
        print(json.dumps({key: value for key, value in payload.items() if key != "results"}, ensure_ascii=False))
        for item in results:
            print(json.dumps(item, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
