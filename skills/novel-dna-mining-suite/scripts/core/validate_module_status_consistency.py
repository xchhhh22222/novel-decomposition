#!/usr/bin/env python3
"""Fail when module HOLD states are promoted to manifest PASS without review."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


HOLD_RE = re.compile(r"(?:^|[^A-Z])HOLD(?:$|[^A-Z])|等待人工复核|待人工复核", re.IGNORECASE)
PASS_RE = re.compile(r"^PASS(?:_WITH_EXPLICIT_GAPS)?$", re.IGNORECASE)


def json_values(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for item in value.values():
            yield from json_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from json_values(item)
    elif isinstance(value, str):
        yield value


def module_status_values(value: Any, path: tuple[str, ...] = ()) -> Iterable[str]:
    """Yield module-review values while excluding legitimate cross-book holds."""
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            if "cross_book" in normalized:
                continue
            yield from module_status_values(item, path + (normalized,))
    elif isinstance(value, list):
        for item in value:
            yield from module_status_values(item, path)
    elif isinstance(value, str):
        normalized = value.lower().replace("-", "_")
        if ("cross_book" in normalized or "跨书" in value) and HOLD_RE.search(value):
            return
        yield value


def load_json_or_jsonl(path: Path) -> list[Any]:
    text = path.read_text(encoding="utf-8-sig")
    try:
        return [json.loads(text)]
    except json.JSONDecodeError:
        return [json.loads(line) for line in text.splitlines() if line.strip()]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Validate module/manifest status consistency.")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("status_files", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    errors: list[str] = []
    hold_files: list[str] = []
    for path in args.status_files:
        values = [text for record in load_json_or_jsonl(path) for text in module_status_values(record)]
        if any(HOLD_RE.search(value) for value in values):
            hold_files.append(str(path))
    manifest_values = list(json_values(manifest))
    manifest_pass = any(PASS_RE.fullmatch(value.strip()) for value in manifest_values)
    if hold_files and manifest_pass:
        override = manifest.get("manual_review") == "PASS" and manifest.get("reviewer") == "SOL" and isinstance(manifest.get("reason"), str) and bool(manifest["reason"].strip())
        if not override:
            errors.append("manifest PASS conflicts with module HOLD; SOL override fields are missing")
        else:
            errors.append("override exists but source status files still contain HOLD; unify all status files before PASS")
    result = {
        "gate": "MODULE_STATUS_CONSISTENCY_GATE",
        "status": "PASS" if not errors else "FAIL",
        "hold_files": hold_files,
        "manifest_pass": manifest_pass,
        "errors": errors,
        "ok": not errors,
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
