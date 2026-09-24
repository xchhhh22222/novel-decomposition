#!/usr/bin/env python3
"""Heuristic Chinese-fiction dialogue audit.

This script locates wording patterns for human/LLM review. It never edits input.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


SUPPORTED_SUFFIXES = {".md", ".txt"}

PATTERNS: dict[str, list[tuple[str, re.Pattern[str]]]] = {
    "exposition_connector": [
        (
            "首先／其次／最后",
            re.compile(r"(?:^|[“‘\"'])\s*(?:首先|其次|最后)[，,：:]"),
        ),
        ("也就是说", re.compile(r"也就是说")),
        ("这意味着", re.compile(r"这意味着")),
        ("你要明白", re.compile(r"你要明白")),
        ("你需要知道", re.compile(r"你需要知道")),
        ("只有……才能……", re.compile(r"只有[^。！？\n]{0,32}才(?:能|会)")),
        ("不是……而是……", re.compile(r"不是[^。！？\n]{0,32}而是")),
    ],
    "dialogue_tag": [
        (
            "扩展对白标签",
            re.compile(r"(?:说道|问道|回答道|开口道|出声道|淡淡道|缓缓道|沉声道|冷声道|笑着说道)"),
        )
    ],
    "stock_action": [
        ("点头", re.compile(r"点(?:了)?点头")),
        ("皱眉", re.compile(r"皱(?:了)?皱眉")),
        ("挑眉", re.compile(r"挑(?:了)?挑眉")),
        ("摸鼻子", re.compile(r"摸(?:了)?摸鼻子")),
        ("耸肩", re.compile(r"耸(?:了)?耸肩")),
        ("瞳孔收缩", re.compile(r"瞳孔(?:猛地|骤然)?(?:一缩|收缩)")),
        ("青筋暴起", re.compile(r"青筋(?:暴起|凸起)")),
        ("眸光微闪", re.compile(r"眸光(?:微微)?一?闪")),
    ],
    "emotion_translation": [
        (
            "动作后直译情绪",
            re.compile(r"(?:显然|明显|足以看出)[^。！？\n]{0,20}(?:愤怒|生气|紧张|害怕|震惊|尴尬|不满)"),
        )
    ],
}


@dataclass(frozen=True)
class Finding:
    file: str
    line: int
    category: str
    pattern: str
    excerpt: str


def iter_files(inputs: Iterable[str]) -> list[Path]:
    files: list[Path] = []
    for raw in inputs:
        path = Path(raw).expanduser()
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
            files.append(path)
        elif path.is_dir():
            files.extend(
                item
                for item in path.rglob("*")
                if item.is_file() and item.suffix.lower() in SUPPORTED_SUFFIXES
            )
        else:
            print(f"warning: skipped unsupported or missing path: {path}", file=sys.stderr)
    return sorted(set(files), key=lambda item: str(item).lower())


def read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise UnicodeError(f"unable to decode {path}")


def shorten(line: str, start: int, end: int, width: int = 88) -> str:
    compact = re.sub(r"\s+", " ", line.strip())
    if len(compact) <= width:
        return compact
    midpoint = max(0, min(len(compact), (start + end) // 2))
    left = max(0, midpoint - width // 2)
    right = min(len(compact), left + width)
    prefix = "…" if left else ""
    suffix = "…" if right < len(compact) else ""
    return prefix + compact[left:right] + suffix


def audit_file(path: Path) -> tuple[list[Finding], int]:
    text = read_text(path)
    findings: list[Finding] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for category, entries in PATTERNS.items():
            for label, pattern in entries:
                for match in pattern.finditer(line):
                    findings.append(
                        Finding(
                            file=str(path.resolve()),
                            line=line_number,
                            category=category,
                            pattern=label,
                            excerpt=shorten(line, match.start(), match.end()),
                        )
                    )
    return findings, len(text)


def markdown_report(findings: list[Finding], file_count: int, char_count: int) -> str:
    lines = [
        "# Dialogue audit",
        "",
        f"Scanned {file_count} file(s), {char_count} characters; found {len(findings)} heuristic hit(s).",
        "",
        "> Hits are review prompts, not automatic errors. Judge them in context.",
    ]
    if not findings:
        return "\n".join(lines)

    summary = Counter((item.category, item.pattern) for item in findings)
    lines.extend(["", "## Summary", "", "| Category | Pattern | Hits |", "| --- | --- | ---: |"])
    for (category, pattern), count in sorted(summary.items(), key=lambda row: (-row[1], row[0])):
        lines.append(f"| {category} | {pattern} | {count} |")

    lines.extend(["", "## Locations", ""])
    for item in findings:
        lines.append(
            f"- `{item.file}:{item.line}` [{item.category}/{item.pattern}] {item.excerpt}"
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Locate possible AI-like patterns in Chinese fiction dialogue without editing files."
    )
    parser.add_argument("paths", nargs="+", help="Markdown/text file or directory")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown")
    args = parser.parse_args()

    files = iter_files(args.paths)
    if not files:
        print("error: no supported .md or .txt files found", file=sys.stderr)
        return 2

    all_findings: list[Finding] = []
    total_chars = 0
    for path in files:
        try:
            findings, char_count = audit_file(path)
        except (OSError, UnicodeError) as exc:
            print(f"warning: {exc}", file=sys.stderr)
            continue
        all_findings.extend(findings)
        total_chars += char_count

    if args.json:
        payload = {
            "files_scanned": len(files),
            "characters_scanned": total_chars,
            "finding_count": len(all_findings),
            "findings": [asdict(item) for item in all_findings],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(markdown_report(all_findings, len(files), total_chars))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
