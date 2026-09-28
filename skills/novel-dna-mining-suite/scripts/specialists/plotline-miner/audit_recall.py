#!/usr/bin/env python3
"""Validate a human-reviewed plotline recall audit.

Recall is cross-module and semantic, so the tool validates that the reverse
search was performed and that every independently qualified line is either
recorded or explicitly rejected by SOL with evidence.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_SOURCES = {
    "arc",
    "character_function",
    "villain_card",
    "promise_ledger",
    "recurring_conflict",
    "recurring_organization",
}


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Validate PLOTLINE_RECALL_AUDIT JSON.")
    parser.add_argument("audit", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data = json.loads(args.audit.read_text(encoding="utf-8-sig"))
    errors: list[str] = []
    if data.get("reviewer") != "SOL":
        errors.append("reviewer must be SOL")
    searched = set(data.get("sources_searched", []))
    missing_sources = sorted(REQUIRED_SOURCES - searched)
    if missing_sources:
        errors.append(f"sources_searched missing: {missing_sources}")
    candidates = data.get("candidates")
    if not isinstance(candidates, list):
        candidates = []
        errors.append("candidates must be a list; use [] when no independent line qualifies")
    for index, candidate in enumerate(candidates, 1):
        prefix = f"candidate {index}"
        if not isinstance(candidate, dict):
            errors.append(f"{prefix}: must be an object")
            continue
        evidence = candidate.get("evidence_refs")
        if not isinstance(evidence, list) or not evidence or not all(nonempty(item) for item in evidence):
            errors.append(f"{prefix}: evidence_refs must be non-empty strings")
        arcs = candidate.get("arc_ids")
        if not isinstance(arcs, list) or len(set(arcs)) < 2:
            errors.append(f"{prefix}: arc_ids must contain at least two distinct arcs")
        qualified = all(bool(candidate.get(field)) for field in ("independent_goal", "independent_resistance", "independent_state_changes"))
        decision = candidate.get("decision")
        if qualified and decision == "recorded":
            if not nonempty(candidate.get("recorded_line_id")):
                errors.append(f"{prefix}: qualified recorded line requires recorded_line_id")
        elif decision == "not_independent":
            if not nonempty(candidate.get("reason")):
                errors.append(f"{prefix}: not_independent requires a reason")
        elif qualified:
            errors.append(f"{prefix}: qualified cross-arc line is omitted")
        elif decision not in {"recorded", "not_independent", "insufficient_evidence"}:
            errors.append(f"{prefix}: decision is not controlled")
    result = {
        "gate": "PLOTLINE_RECALL_GATE",
        "status": "PASS" if not errors else "FAIL",
        "candidates": len(candidates),
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
