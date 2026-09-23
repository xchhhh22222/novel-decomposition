#!/usr/bin/env python3
"""Build, audit, and search a compact local fiction-material index.

Only deterministic parsing, indexing, and retrieval happen here. Semantic card
merges, splits, and deletions remain review decisions.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path


SECTION_NAMES = {
    "summary": ["抽象机制", "核心用途", "素材说明"],
    "applicable_stage": ["适用阶段", "节奏"],
    "preconditions": ["使用前提"],
    "protagonist_goal": ["主角目标"],
    "conflict": ["核心冲突", "冲突结构"],
    "payoff": ["爽点机制", "常见奖励"],
    "hook": ["常见章末钩子"],
    "risk": ["使用风险", "失败条件与重复风险", "不应直接复用"],
}

LIST_FIELDS = {
    "tags",
    "secondary_modules",
    "story_functions",
    "applicable_stages",
    "preconditions",
    "forbidden_when",
    "payoff_types",
    "hook_types",
    "emotion_targets",
    "emotion_functions",
    "emotion_preconditions",
    "payoff_evidence",
    "aftermath_types",
}

V2_REQUIRED = {
    "schema_version",
    "card_id",
    "name",
    "primary_module",
    "story_functions",
    "applicable_stages",
    "preconditions",
    "agency_type",
    "payoff_types",
    "payoff_latency",
    "tags",
    "summary",
    "support_level",
    "source_book_count",
    "source_occurrence_count",
    "status",
}

V3_REQUIRED = V2_REQUIRED | {
    "emotion_targets",
    "emotion_functions",
    "emotion_preconditions",
    "tension_shape",
    "payoff_evidence",
    "aftermath_types",
}

SUPPORT_BONUS = {"S": 4.0, "A": 3.0, "B": 2.0, "C": 0.5}

QUERY_EXPANSIONS = {
    "环境破局": ["环境机制", "地形", "机关", "环境引爆"],
    "怪潮围困": ["怪潮", "怪群", "虫潮", "群居", "围困", "聚怪"],
    "团队分工": ["团队协同", "队友", "配合", "分工"],
    "排名反超": ["排名", "反超", "积分", "刷分"],
    "资源获取": ["资源", "奖励", "战果", "结算", "捡漏"],
    "关系推进": ["人物关系", "合作", "竞争", "信任", "共同任务"],
    "章末钩子": ["钩子", "悬念", "危机", "预告", "曝光"],
    "紧张": ["倒计时", "围困", "追击", "暴露", "资源见底", "险情"],
    "压抑": ["受限", "误解", "剥夺", "压制", "无力", "情绪债"],
    "热血": ["并肩", "守护", "担当", "逆境", "共担", "团队"],
    "感动": ["牺牲", "回报", "信任", "兑现承诺", "无声支持"],
    "心疼": ["隐忍", "误解", "损失", "代价", "孤立", "克制"],
    "打脸爽": ["轻视", "低估", "公开验证", "认知反转", "态度逆转"],
    "智斗爽": ["信息差", "布局", "规则", "弱点", "反制", "将计就计"],
    "成长爽": ["训练成果", "突破", "掌握", "实战验证", "前后对比"],
    "收获爽": ["奖励", "结算", "战果", "资源", "一鱼多吃"],
    "认可爽": ["承认", "信任", "重视", "重新定价", "主动邀请"],
    "守护爽": ["救场", "护短", "承担", "保护", "反击"],
    "掌控爽": ["预判", "定策", "调度", "谈判", "局势反转"],
    "期待兑现": ["铺垫", "承诺", "回收", "兑现", "反应"],
    "情绪余震": ["关系变化", "认知变化", "公开结果", "传播", "后果"],
}


def clean_inline(value: str):
    value = value.strip().strip('"\'')
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [x.strip().strip('"\'') for x in inner.split(",") if x.strip()]
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def parse_frontmatter(text: str) -> dict:
    match = re.match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", text, re.S)
    if not match:
        return {}
    data: dict = {}
    active_list = None
    for raw in match.group(1).splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        item = re.match(r"^\s+-\s+(.+)$", raw)
        if item and active_list:
            data.setdefault(active_list, []).append(clean_inline(item.group(1)))
            continue
        field = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", raw)
        if not field:
            active_list = None
            continue
        key, value = field.group(1), field.group(2)
        if value == "":
            data[key] = [] if key in LIST_FIELDS else ""
            active_list = key if key in LIST_FIELDS else None
        else:
            data[key] = clean_inline(value)
            active_list = None
    return data


def normalize_text(value) -> str:
    if isinstance(value, list):
        value = "、".join(str(x) for x in value)
    value = re.sub(r"[`*_>#|]", "", str(value or ""))
    return re.sub(r"\s+", " ", value).strip()


def truncate(value, limit: int) -> str:
    text = normalize_text(value)
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def extract_section(text: str, names: list[str]) -> str:
    for name in names:
        pattern = re.compile(
            rf"^##\s+{re.escape(name)}\s*$\n(.*?)(?=^##\s+|\Z)", re.M | re.S
        )
        match = pattern.search(text)
        if match:
            return normalize_text(match.group(1))
    return ""


def card_files(library: Path) -> list[Path]:
    root = library / "套路素材"
    return sorted(root.glob("*/TR_*.md")) if root.exists() else []


def as_list(value) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [normalize_text(x) for x in value if normalize_text(x)]
    return [x.strip() for x in re.split(r"[,，、]", str(value)) if x.strip()]


def fallback_id(path: Path) -> str:
    match = re.match(r"^(TR_[A-Z]+_\d+)", path.stem)
    return match.group(1) if match else path.stem


def parse_card(path: Path, library: Path) -> dict:
    text = path.read_text(encoding="utf-8-sig")
    fm = parse_frontmatter(text)
    sections = {key: extract_section(text, names) for key, names in SECTION_NAMES.items()}
    summary = fm.get("summary") or sections["summary"]
    applicable = fm.get("applicable_stages") or sections["applicable_stage"]
    preconditions = fm.get("preconditions") or sections["preconditions"]
    payoff_parts = as_list(fm.get("payoff_types"))
    payoff_text = "、".join(payoff_parts) if payoff_parts else sections["payoff"]
    stat = path.stat()
    return {
        "schema_version": int(fm.get("schema_version") or 1),
        "card_id": str(fm.get("card_id") or fm.get("id") or fallback_id(path)),
        "name": normalize_text(fm.get("name") or fm.get("title") or path.stem),
        "module": normalize_text(fm.get("primary_module") or path.parent.name),
        "secondary_modules": as_list(fm.get("secondary_modules")),
        "story_functions": as_list(fm.get("story_functions")),
        "emotion_targets": as_list(fm.get("emotion_targets")),
        "emotion_functions": as_list(fm.get("emotion_functions")),
        "tags": as_list(fm.get("tags")),
        "support_level": normalize_text(fm.get("support_level") or "待确认"),
        "source_book_count": int(fm.get("source_book_count") or 0),
        "source_occurrence_count": int(fm.get("source_occurrence_count") or 0),
        "status": normalize_text(fm.get("status") or "active"),
        "agency_type": normalize_text(fm.get("agency_type")),
        "payoff_latency": normalize_text(fm.get("payoff_latency")),
        "summary": truncate(summary, 180),
        "applicable_stage": truncate(applicable, 120),
        "preconditions": truncate(preconditions, 160),
        "emotion_preconditions": as_list(fm.get("emotion_preconditions")),
        "protagonist_goal": truncate(sections["protagonist_goal"], 120),
        "conflict": truncate(sections["conflict"], 160),
        "payoff": truncate(payoff_text, 150),
        "tension_shape": truncate(fm.get("tension_shape"), 120),
        "payoff_evidence": as_list(fm.get("payoff_evidence")),
        "aftermath_types": as_list(fm.get("aftermath_types")),
        "hook": truncate(sections["hook"], 130),
        "risk": truncate(sections["risk"], 160),
        "forbidden_when": as_list(fm.get("forbidden_when")),
        "hook_types": as_list(fm.get("hook_types")),
        "path": path.relative_to(library).as_posix(),
        "source_size": stat.st_size,
        "source_mtime_ns": stat.st_mtime_ns,
        "content_hash": hashlib.sha256(text.encode("utf-8")).hexdigest()[:16],
        "_frontmatter": fm,
    }


def load_cards(library: Path) -> list[dict]:
    cards = []
    for path in card_files(library):
        try:
            cards.append(parse_card(path, library))
        except Exception as exc:
            cards.append(
                {
                    "card_id": fallback_id(path),
                    "path": path.relative_to(library).as_posix(),
                    "_error": str(exc),
                }
            )
    return cards


def public_row(card: dict) -> dict:
    return {key: value for key, value in card.items() if not key.startswith("_")}


def index_path(library: Path) -> Path:
    return library / "00_索引" / "检索索引.jsonl"


def index_is_fresh(library: Path, rows: list[dict]) -> bool:
    current = {
        path.relative_to(library).as_posix(): path.stat().st_mtime_ns
        for path in card_files(library)
    }
    indexed = {row.get("path"): row.get("source_mtime_ns") for row in rows}
    return current == indexed


def read_index(library: Path) -> tuple[list[dict], bool]:
    path = index_path(library)
    if not path.exists():
        return [], False
    rows = []
    try:
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    except (OSError, json.JSONDecodeError):
        return [], False
    return rows, index_is_fresh(library, rows)


def cjk_bigrams(text: str) -> set[str]:
    result = set()
    for run in re.findall(r"[\u4e00-\u9fff]+", text):
        result.update(run[i : i + 2] for i in range(len(run) - 1))
    return result


def terms(text: str) -> list[str]:
    return [x for x in re.split(r"[\s,，、;；/|]+", text.strip()) if x]


def expanded_terms(query: str) -> list[str]:
    base = terms(query)
    expanded = list(base)
    for item in base:
        expanded.extend(QUERY_EXPANSIONS.get(item, []))
    return list(dict.fromkeys(expanded))


def searchable(card: dict) -> str:
    fields = [
        card.get("name", ""),
        card.get("module", ""),
        card.get("secondary_modules", []),
        card.get("story_functions", []),
        card.get("emotion_targets", []),
        card.get("emotion_functions", []),
        card.get("tags", []),
        card.get("summary", ""),
        card.get("applicable_stage", ""),
        card.get("preconditions", ""),
        card.get("emotion_preconditions", []),
        card.get("protagonist_goal", ""),
        card.get("conflict", ""),
        card.get("payoff", ""),
        card.get("tension_shape", ""),
        card.get("payoff_evidence", []),
        card.get("aftermath_types", []),
        card.get("hook", ""),
        card.get("risk", ""),
        card.get("forbidden_when", []),
    ]
    return normalize_text(" ".join(normalize_text(x) for x in fields)).lower()


def score_card(
    card: dict, query: str, modules: set[str], excluded: list[str]
) -> tuple[float, list[str]]:
    haystack = searchable(card)
    if any(item.lower() in haystack for item in excluded if item):
        return -1.0, []
    score = SUPPORT_BONUS.get(card.get("support_level"), 0.0)
    reasons = []
    module_values = {card.get("module", ""), *card.get("secondary_modules", [])}
    if modules and module_values & modules:
        score += 9.0
        reasons.append("模块命中")
    exact_hits = 0
    query_terms = expanded_terms(query)
    base_terms = set(terms(query))
    for term in query_terms:
        lowered = term.lower()
        if lowered in haystack:
            exact_hits += 1
            weight = 7.0 if term in base_terms else 2.5
            score += weight + min(len(term), 6) * 0.3
            reasons.append(term if term in base_terms else f"扩:{term}")
    query_bigrams = cjk_bigrams(query)
    overlap = 0.0
    if query_bigrams:
        overlap = len(query_bigrams & cjk_bigrams(haystack)) / len(query_bigrams)
        score += overlap * 18.0
        if overlap >= 0.15:
            reasons.append(f"语义字组{overlap:.0%}")
    if query_terms and exact_hits == 0 and overlap < 0.08:
        score -= 8.0
    if card.get("status") not in {"active", "candidate", ""}:
        score -= 20.0
    return score, list(dict.fromkeys(reasons))


def command_build(args) -> int:
    library = Path(args.library).resolve()
    cards = load_cards(library)
    errors = [card for card in cards if card.get("_error")]
    if errors:
        for card in errors:
            print(f"ERROR {card['path']}: {card['_error']}", file=sys.stderr)
        return 2
    target = index_path(library)
    target.parent.mkdir(parents=True, exist_ok=True)
    rows = [public_row(card) for card in cards]
    payload = "\n".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows
    )
    target.write_text(payload + ("\n" if rows else ""), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "built",
                "cards": len(rows),
                "path": str(target),
                "bytes": target.stat().st_size,
            },
            ensure_ascii=False,
        )
    )
    return 0


def command_audit(args) -> int:
    library = Path(args.library).resolve()
    cards = load_cards(library)
    errors = [card for card in cards if card.get("_error")]
    valid = [card for card in cards if not card.get("_error")]
    ids = Counter(card.get("card_id") for card in valid)
    duplicate_ids = sorted(key for key, count in ids.items() if count > 1)
    long_cards = sorted(
        (
            {"card_id": card["card_id"], "bytes": card["source_size"]}
            for card in valid
            if card["source_size"] > 8000
        ),
        key=lambda row: -row["bytes"],
    )
    v2_missing = []
    v3_missing = []
    for card in valid:
        if card.get("schema_version", 1) == 2:
            missing = sorted(V2_REQUIRED - set(card.get("_frontmatter", {})))
            if missing:
                v2_missing.append({"card_id": card["card_id"], "missing": missing})
        elif card.get("schema_version", 1) >= 3:
            missing = sorted(V3_REQUIRED - set(card.get("_frontmatter", {})))
            if missing:
                v3_missing.append({"card_id": card["card_id"], "missing": missing})
    tag_counts = Counter(tag for card in valid for tag in card.get("tags", []))
    rows, fresh = read_index(library)
    report = {
        "checked_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "library": str(library),
        "cards": len(valid),
        "parse_errors": [
            {"path": card["path"], "error": card["_error"]} for card in errors
        ],
        "duplicate_ids": duplicate_ids,
        "schema_v2_cards": sum(
            1 for card in valid if card.get("schema_version", 1) == 2
        ),
        "schema_v2_missing": v2_missing,
        "schema_v3_cards": sum(
            1 for card in valid if card.get("schema_version", 1) >= 3
        ),
        "schema_v3_missing": v3_missing,
        "long_cards_over_8kb": long_cards,
        "tags": len(tag_counts),
        "singleton_tags": sum(1 for count in tag_counts.values() if count == 1),
        "compact_index_exists": bool(rows),
        "compact_index_fresh": fresh,
        "compact_index_rows": len(rows),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors or duplicate_ids or v2_missing or v3_missing else 0


def command_search(args) -> int:
    library = Path(args.library).resolve()
    rows, fresh = read_index(library)
    source = "compact-index"
    if not rows or not fresh:
        rows = [
            public_row(card)
            for card in load_cards(library)
            if not card.get("_error")
        ]
        source = "in-memory"
    modules = set(terms(args.modules))
    excluded = terms(args.exclude)
    ranked = []
    for card in rows:
        score, reasons = score_card(card, args.query, modules, excluded)
        if score >= 0:
            ranked.append((score, card, reasons))
    ranked.sort(key=lambda item: (-item[0], item[1].get("card_id", "")))
    selected = ranked[: max(1, args.limit)]
    print(
        f"source={source}; index_fresh={str(fresh).lower()}; "
        f"candidates={len(rows)}; returned={len(selected)}"
    )
    added_terms = [item for item in expanded_terms(args.query) if item not in terms(args.query)]
    if added_terms:
        print("expanded=" + "、".join(added_terms))
    for score, card, reasons in selected:
        compact = {
            "id": card.get("card_id"),
            "name": card.get("name"),
            "module": card.get("module"),
            "score": round(score, 1),
            "support": card.get("support_level"),
            "why": reasons[:5],
            "emotion_targets": card.get("emotion_targets", []),
            "emotion_functions": card.get("emotion_functions", []),
            "summary": card.get("summary"),
            "tension_shape": card.get("tension_shape", ""),
            "payoff_evidence": card.get("payoff_evidence", []),
            "aftermath_types": card.get("aftermath_types", []),
            "stage": card.get("applicable_stage"),
            "risk": card.get("risk"),
            "path": card.get("path"),
        }
        print(json.dumps(compact, ensure_ascii=False, separators=(",", ":")))
    return 0


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit = subparsers.add_parser("audit", help="Read-only structural audit")
    audit.add_argument("--library", required=True)
    audit.set_defaults(func=command_audit)

    build = subparsers.add_parser(
        "build", help="Rebuild 00_索引/检索索引.jsonl"
    )
    build.add_argument("--library", required=True)
    build.set_defaults(func=command_build)

    search = subparsers.add_parser(
        "search", help="Search compact summaries without reading full cards"
    )
    search.add_argument("--library", required=True)
    search.add_argument("--query", required=True)
    search.add_argument("--modules", default="")
    search.add_argument("--exclude", default="")
    search.add_argument("--limit", type=int, default=12)
    search.set_defaults(func=command_search)
    return parser


def main() -> int:
    args = make_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
