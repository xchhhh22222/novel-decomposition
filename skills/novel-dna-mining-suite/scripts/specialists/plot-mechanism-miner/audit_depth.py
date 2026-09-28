#!/usr/bin/env python3
"""Validate a SOL-reviewed plot-mechanism depth/recall audit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ENGINE_KINDS = {
    "public_repricing",
    "resource_reinvestment",
    "information_asymmetry",
    "relationship_conflict",
    "organization_permission",
    "ability_side_effect",
    "combat_environment_constraint",
    "other",
}


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Validate MECHANISM_RECALL/DEPTH_AUDIT JSON.")
    parser.add_argument("audit", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data = json.loads(args.audit.read_text(encoding="utf-8-sig"))
    errors: list[str] = []
    if data.get("reviewer") != "SOL":
        errors.append("reviewer must be SOL")
    mechanisms = data.get("mechanism_ids")
    if not isinstance(mechanisms, list) or not all(nonempty(item) for item in mechanisms):
        mechanisms = []
        errors.append("mechanism_ids must be a list of strings")
    engines = data.get("causal_engines")
    if not isinstance(engines, list):
        engines = []
        errors.append("causal_engines must be a list")
    qualified_count = 0
    for index, engine in enumerate(engines, 1):
        prefix = f"causal_engine {index}"
        if not isinstance(engine, dict):
            errors.append(f"{prefix}: must be an object")
            continue
        if engine.get("engine_kind") not in ENGINE_KINDS:
            errors.append(f"{prefix}: engine_kind is not controlled")
        evidence = engine.get("evidence_refs")
        if not isinstance(evidence, list) or not evidence or not all(nonempty(item) for item in evidence):
            errors.append(f"{prefix}: evidence_refs must be non-empty strings")
        if engine.get("distinct_across_arcs") is True:
            qualified_count += 1
            mapped = engine.get("mapped_mechanism_ids")
            if not isinstance(mapped, list) or not mapped:
                if not (engine.get("decision") == "not_independent" and nonempty(engine.get("reason"))):
                    errors.append(f"{prefix}: distinct engine is not mapped or explicitly rejected")
            elif any(item not in mechanisms for item in mapped):
                errors.append(f"{prefix}: mapped_mechanism_ids contains an unknown mechanism")
    if qualified_count >= 2 and len(set(mechanisms)) <= 1:
        errors.append("MECHANISM_OVERCOMPRESSION_RISK: multiple distinct causal engines were compressed into one mechanism")
    result = {
        "gate": "MECHANISM_RECALL_GATE",
        "status": "PASS" if not errors else "FAIL",
        "mechanism_count": len(set(mechanisms)),
        "distinct_engine_count": qualified_count,
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
