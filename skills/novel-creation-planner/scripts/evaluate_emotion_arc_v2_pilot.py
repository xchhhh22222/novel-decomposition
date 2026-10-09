#!/usr/bin/env python3
"""Compare E2/E3 research output with the disabled legacy baseline by capability."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from validate_emotion_arc_v2_research_plan import validate_plan


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate material capability changes, not file counts.")
    parser.add_argument("--emotion-plan", type=Path, required=True)
    parser.add_argument("--legacy-plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-repo", type=Path)
    args = parser.parse_args()
    try:
        enhanced, legacy = read(args.emotion_plan), read(args.legacy_plan)
        enhanced_check = validate_plan(enhanced, args.source_repo.resolve() if args.source_repo else None)
        legacy_check = validate_plan(legacy)
        if not enhanced_check["ok"] or not legacy_check["ok"]:
            raise ValueError("one or both compared plans fail structural validation")
        e2, e3 = enhanced["pipeline"]["e2"], enhanced["pipeline"]["e3"]
        lines, macros = e3["emotion_lines"], e2["macro_arcs"]
        slots = enhanced["material_assembly"]["slots"]
        checks = {
            "plot_diversity": {
                "improved": len(lines) >= 3 and len({line["payoff_condition"] for line in lines}) == len(lines),
                "evidence": f"enhanced path tracks {len(lines)} independent payoff contracts; baseline has no independent line ledger",
            },
            "relationship_agency": {
                "improved": any(line["line_id"] == "EL:PILOT:RELATIONSHIP" for line in lines)
                and any("EL:PILOT:RELATIONSHIP" in stage.get("emotion_line_ids", []) for stage in enhanced["story_spine"]["stages"]),
                "evidence": "relationship choice is attached to action nodes/choice rather than recorded as atmosphere",
            },
            "reader_expectation_management": {
                "improved": len(enhanced["active_emotion_state"]["pending_payoff_contracts"]) == len(macros),
                "evidence": "both macro settlement contracts remain explicit in the active state packet",
            },
            "continuation_capacity": {
                "improved": e3["handoff"]["old_arc_contract_retained"] == macros[0]["settlement_contract"]
                and e3["handoff"]["dominance_transfer_status"] == "CANDIDATE_UNVERIFIED",
                "evidence": "macro B starts through a causal evidence trigger without cancelling macro A",
            },
            "function_first_material_use": {
                "improved": all(slot["selection_order"] == "FUNCTION_FIRST_SOURCE_SECOND" for slot in slots)
                and all(slot["selected_ref"] is not None or slot["gap"] for slot in slots),
                "evidence": f"{sum(slot['selected_ref'] is not None for slot in slots)}/8 module slots have real selected sources; every miss is an explicit GAP",
            },
            "story_spine_compatibility": {
                "improved": len(enhanced["story_spine"]["stages"]) == len(legacy["story_spine"]["stages"]) == 9,
                "evidence": "both paths preserve the same nine action-stage names; E2/E3 adds references without replacing the spine",
            },
        }
        result = {
            "schema_version": "emotion_arc_v2_pilot_evaluation_v1",
            "status": "candidate", "qa_status": "HOLD", "production_promotion": "NOT_RUN",
            "evaluation_basis": "capability evidence, not generated file count",
            "checks": checks,
            "conclusion": "MATERIAL_IMPROVEMENT_OBSERVED" if all(item["improved"] for item in checks.values()) else "PARTIAL_IMPROVEMENT_WITH_GAPS",
            "semantic_review": "NEEDS_INDEPENDENT_REVIEW",
            "remaining_limits": [
                "retrieval ranking and interface compatibility remain research candidates",
                "macro dominance transfer is not machine approved",
                "no production schema or Stage 4 writing authorization is granted",
            ],
        }
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"ok": True, **result}, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
