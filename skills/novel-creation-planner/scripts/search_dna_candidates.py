#!/usr/bin/env python3
"""Read-only search over novel DNA records, with optional V1.4 component-level retrieval."""

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

COMPONENT_ALIASES = {
    "势力": "faction",
    "组织": "faction",
    "factions": "faction",
    "世界规则": "rule_chain",
    "规则链": "rule_chain",
    "rule": "rule_chain",
    "resource_circuit": "world_resource_circuit",
    "资源循环": "world_resource_circuit",
    "威胁": "threat_generator",
    "地图": "map_expansion",
    "信息控制": "information_control",
    "体系": "cultivation_system",
    "修炼体系": "cultivation_system",
    "system": "cultivation_system",
    "境界": "realm",
    "realm_system": "realm",
    "体系关系": "system_relation",
    "兼修": "system_relation",
    "功法": "technique",
    "武技": "technique",
    "技能": "technique",
    "法宝": "artifact",
    "装备": "artifact",
    "武器": "artifact",
    "成长资源": "resource_asset",
    "修炼资源": "resource_asset",
    "resource": "resource_asset",
}

TITLE_FIELDS = (
    "character_label",
    "label",
    "archetype",
    "normalized_archetype",
    "mechanic_name_in_book",
    "world_core_premise",
    "name_in_book",
    "rule_statement",
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
    "actual_interest",
    "public_role",
    "growth_loop",
    "core_effect",
    "stage_difference",
    "synergy_or_conflict",
    "use_or_conversion",
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
    text = re.sub(r"\s+", " ", flatten(value)).strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


def result_summary(module: str, row: dict[str, Any]) -> str:
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


def normalize_components(raw: str) -> set[str]:
    result: set[str] = set()
    for value in split_values(raw.lower()):
        result.add(COMPONENT_ALIASES.get(value, value))
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


def component_id(parent_id: str, component_type: str, index: int, item: dict[str, Any]) -> str:
    for key in ("faction_id", "chain_id", "system_id", "realm_id", "relation_id", "technique_id", "artifact_id", "resource_id"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return f"{parent_id}#{component_type}:{index + 1}"


def emit_components(module: str, row: dict[str, Any]) -> list[dict[str, Any]]:
    """Explode selected V1.4 nested arrays while preserving source provenance."""
    parent_id = str(row.get("record_id") or "")
    items: list[dict[str, Any]] = []

    def add(component_type: str, values: Any, field: str, parent_component_id: str | None = None) -> None:
        if not isinstance(values, list):
            return
        for index, value in enumerate(values):
            if not isinstance(value, dict):
                continue
            cid = component_id(parent_id, component_type, index, value)
            items.append(
                {
                    "component_type": component_type,
                    "component_id": cid,
                    "parent_component_id": parent_component_id,
                    "component_path": f"{field}[{index}]",
                    "value": value,
                }
            )

    if module == "worldbuilding":
        add("faction", row.get("factions"), "factions")
        add("rule_chain", row.get("rule_chains"), "rule_chains")
        add("world_resource_circuit", row.get("resource_circuits"), "resource_circuits")
        add("threat_generator", row.get("threat_generators"), "threat_generators")
        add("map_expansion", row.get("map_expansion_patterns"), "map_expansion_patterns")
        add("information_control", row.get("information_control_patterns"), "information_control_patterns")

    if module == "cultivation_system":
        systems = row.get("cultivation_systems")
        if isinstance(systems, list):
            for index, system in enumerate(systems):
                if not isinstance(system, dict):
                    continue
                sid = component_id(parent_id, "cultivation_system", index, system)
                items.append(
                    {
                        "component_type": "cultivation_system",
                        "component_id": sid,
                        "parent_component_id": None,
                        "component_path": f"cultivation_systems[{index}]",
                        "value": system,
                    }
                )
                realm_system = system.get("realm_system")
                if isinstance(realm_system, dict):
                    realms = realm_system.get("realm_order")
                    if isinstance(realms, list):
                        for rindex, realm in enumerate(realms):
                            if not isinstance(realm, dict):
                                continue
                            rid = component_id(parent_id, "realm", rindex, realm)
                            items.append(
                                {
                                    "component_type": "realm",
                                    "component_id": rid,
                                    "parent_component_id": sid,
                                    "component_path": f"cultivation_systems[{index}].realm_system.realm_order[{rindex}]",
                                    "value": {**realm, "system_name_in_book": system.get("name_in_book")},
                                }
                            )
        add("system_relation", row.get("system_relations"), "system_relations")
        add("technique", row.get("techniques"), "techniques")
        add("artifact", row.get("artifacts"), "artifacts")
        add("resource_asset", row.get("resource_assets"), "resource_assets")

    return items


def record_title(row: dict[str, Any]) -> str:
    return next((compact(row.get(field), 160) for field in TITLE_FIELDS if row.get(field)), "")


def score_text(title: str, value: Any, terms: list[str]) -> tuple[float, list[str]]:
    full_text = flatten(value).lower()
    title_lower = title.lower()
    why: list[str] = []
    score = 0.0
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
    record_bigrams = bigrams(title + " " + compact(value, 1400))
    if query_bigrams:
        overlap = len(query_bigrams & record_bigrams) / len(query_bigrams)
        score += overlap * 6
        if overlap >= 0.15 and not why:
            why.append(f"语义字组:{round(overlap * 100)}%")
    return score, why


def usage_status(row: dict[str, Any], value: dict[str, Any]) -> str:
    if row.get("qa_status") == "HOLD":
        return "HOLD"
    if row.get("unknowns") or value.get("unknowns"):
        return "ADAPTABLE_WITH_GAPS"
    return "ADAPTABLE"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Search novel DNA candidates without modifying the library.")
    parser.add_argument("--library", type=Path, required=True, help="Material library root containing DNA素材.")
    parser.add_argument("--query", required=True, help="Space/comma separated functional search terms.")
    parser.add_argument("--modules", default="", help="Optional module names/slugs/abbreviations.")
    parser.add_argument("--components", default="", help="Optional component types, e.g. faction,system,realm,technique,artifact,resource.")
    parser.add_argument("--exclude", default="", help="Terms that disqualify a record/component.")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--max-per-book", type=int, default=0, help="0 means unlimited; useful for source diversity.")
    parser.add_argument("--include-per-book", action="store_true")
    parser.add_argument("--record-types", default="", help="Optional comma/space separated record_type filter.")
    parser.add_argument("--format", choices=("jsonl", "json", "md"), default="jsonl")
    args = parser.parse_args()

    root = args.library.resolve() / "DNA素材"
    if not root.exists():
        parser.error(f"DNA素材 not found under {args.library}")

    wanted_modules = normalize_modules(args.modules) if args.modules else set()
    wanted_components = normalize_components(args.components) if args.components else set()
    wanted_types = set(split_values(args.record_types)) if args.record_types else set()
    terms = split_values(args.query.lower())
    excludes = split_values(args.exclude.lower())
    if not terms:
        parser.error("--query must contain at least one term")
    if args.max_per_book < 0:
        parser.error("--max-per-book must be >= 0")

    # Component mode needs per_book/derived records even if caller omitted the flag.
    include_per_book = args.include_per_book or bool(wanted_components)

    results: list[dict[str, Any]] = []
    for module, path in discover_paths(root, include_per_book):
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

            source_record_id = row.get("record_id", row.get("cluster_id", f"{relative}:{number}"))
            book_id = row.get("book_id")
            base = {
                "record_id": source_record_id,
                "record_type": row.get("record_type"),
                "module": module,
                "book_id": book_id,
                "schema_version": row.get("schema_version"),
                "confidence": row.get("confidence"),
                "qa_status": row.get("qa_status"),
                "path": relative,
                "line": number,
            }

            if wanted_components:
                for component in emit_components(module, row):
                    if component["component_type"] not in wanted_components:
                        continue
                    value = component["value"]
                    full_text = flatten(value).lower()
                    if any(term in full_text for term in excludes):
                        continue
                    title = record_title(value) or str(component["component_id"])
                    score, why = score_text(title, value, terms)
                    if score <= 0:
                        continue
                    if row.get("confidence") == "HIGH":
                        score += 1
                    result = {
                        **base,
                        "source_record_id": source_record_id,
                        "component_type": component["component_type"],
                        "component_id": component["component_id"],
                        "parent_component_id": component["parent_component_id"],
                        "component_path": component["component_path"],
                        "title": title,
                        "score": round(score, 2),
                        "why": why,
                        "usage_status": usage_status(row, value),
                        "summary": result_summary(module, value),
                        "evidence_refs": value.get("evidence_refs") or value.get("direct_evidence_refs") or row.get("evidence_refs", []),
                    }
                    results.append(result)
                continue

            title = record_title(row)
            full_text = flatten(row).lower()
            if any(term in full_text for term in excludes):
                continue
            score, why = score_text(title, row, terms)
            if score <= 0:
                continue
            if row.get("confidence") == "HIGH":
                score += 1
            support = row.get("supporting_book_count", row.get("source_count"))
            if isinstance(support, int) and support > 1:
                score += min(support, 5) * 0.2
            results.append(
                {
                    **base,
                    "title": title,
                    "score": round(score, 2),
                    "why": why,
                    "usage_status": usage_status(row, row),
                    "supporting_book_count": support,
                    "summary": result_summary(module, row),
                }
            )

    results.sort(
        key=lambda item: (
            -item["score"],
            item["module"],
            str(item.get("book_id") or ""),
            str(item.get("component_id") or item["record_id"]),
        )
    )

    if args.max_per_book:
        selected: list[dict[str, Any]] = []
        per_book: dict[str, int] = {}
        for item in results:
            book_key = str(item.get("book_id") or "__NO_BOOK__")
            if book_key != "__NO_BOOK__" and per_book.get(book_key, 0) >= args.max_per_book:
                continue
            selected.append(item)
            if book_key != "__NO_BOOK__":
                per_book[book_key] = per_book.get(book_key, 0) + 1
            if len(selected) >= max(1, args.limit):
                break
        results = selected
    else:
        results = results[: max(1, args.limit)]

    payload = {
        "query": args.query,
        "modules": sorted(wanted_modules),
        "components": sorted(wanted_components),
        "component_mode": bool(wanted_components),
        "include_per_book": include_per_book,
        "max_per_book": args.max_per_book,
        "returned": len(results),
        "results": results,
    }

    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif args.format == "md":
        print(f"# DNA候选检索\n\n- query: `{args.query}`\n- returned: {len(results)}\n")
        print("| score | module | book | component | id | title | path |")
        print("|---:|---|---|---|---|---|---|")
        for item in results:
            print(
                f"| {item['score']} | {item['module']} | {item.get('book_id') or ''} | "
                f"{item.get('component_type') or 'record'} | "
                f"{item.get('component_id') or item['record_id']} | {item['title']} | {item['path']} |"
            )
    else:
        print(json.dumps({key: value for key, value in payload.items() if key != "results"}, ensure_ascii=False))
        for item in results:
            print(json.dumps(item, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
