#!/usr/bin/env python3
"""Smoke tests for validate_creation_plan.py without external dependencies."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path


VALIDATOR = Path(__file__).with_name("validate_creation_plan.py")
SCORE = {
    "market_reader_promise": 13,
    "opening_1_10": 13,
    "long_engine_61_300": 18,
    "mechanic_world_resource_fit": 13,
    "relationship_sustainability": 9,
    "emotion_pacing": 9,
    "originality_distance": 9,
    "material_feasibility": 4,
}
PHASES = ("1-3", "4-10", "11-30", "31-60", "61-120", "121-200", "201-300")
DEBT_KEYS = ("emotion", "growth", "resource", "relationship", "world_rule", "antagonist", "mainline_foreshadowing")


def concept(concept_id: str, signal_id: str, material_key: str, material_id: str) -> dict:
    prefix = concept_id.lower()
    signature_keys = (
        "reader_promise",
        "protagonist_identity_goal",
        "golden_finger_logic",
        "relationship_topology",
        "central_conflict",
        "resource_loop",
        "world_institution",
        "longline_mystery",
    )
    mapping = {"formal_card_ids": [], "dna_candidate_ids": [], "gaps": []}
    mapping[material_key] = [material_id]
    return {
        "concept_id": concept_id,
        "positioning": f"position-{prefix}",
        "reader_promise": f"promise-{prefix}",
        "protagonist": f"protagonist-{prefix}",
        "golden_finger": f"golden-finger-{prefix}",
        "relationship_topology": f"relationships-{prefix}",
        "world_cultivation_resource_loop": f"loop-{prefix}",
        "named_story_bible": {
            "titles": [f"title-{prefix}"],
            "protagonist_name": f"name-{prefix}",
            "golden_finger_name": f"ability-{prefix}",
            "world_terms": [f"institution-{prefix}", f"resource-{prefix}"],
        },
        "opening_1_10": [
            {"chapter": chapter, "primary_event": f"event-{prefix}-{chapter}", "emotion": "anticipation", "payoff": "visible result", "hook": "new question"}
            for chapter in range(1, 11)
        ],
        "story_engine": f"engine-{prefix}",
        "longline_engine_summary": f"longline-{prefix}",
        "market_signal_ids": [signal_id],
        "material_mapping": mapping,
        "differentiation_signature": {key: f"{prefix}-{key}" for key in signature_keys},
        "originality_changes": ["cause", "goal", "resource", "payoff"],
        "risks": ["fatigue"],
        "score": sum(SCORE.values()),
        "score_breakdown": SCORE,
        "hard_gate": "PASS",
    }


def debt(key: str) -> dict:
    item = {
        "debt_id": f"DEBT:{key}",
        "opened_phase": "1-3",
        "promise": "promise",
        "payoff_window": "11-30",
        "visible_evidence": "observable consequence",
        "status": "OPEN",
        "planned_payoff": "planned result",
        "overdue_risk": "reader fatigue",
    }
    if key == "antagonist":
        item.update(
            antagonist_goal="block protagonist",
            pressure_escalation="raise institutional cost",
            stage_failure_or_payoff="lose one resource node",
            exit_window="31-60",
        )
    return item


def valid_plan() -> dict:
    samples = [
        {
            "sample_id": f"S{i}",
            "rank": i,
            "title": f"book-{i}",
            "content_status": "pass",
            "analyzed_chapters": list(range(1, 11)),
            "opening_analysis": {"first_scene": f"scene-{i}", "chapter_4_10_loop": f"loop-{i}", "evidence_locations": ["chapter-1", "chapter-10"]},
        }
        for i in range(1, 11)
    ]
    signals = [
        {"signal_id": f"SIG:{letter}", "signal_type": "opening", "claim": f"claim-{letter}", "evidence_sample_ids": [f"S{index}"]}
        for index, letter in enumerate(("A", "B", "C"), start=1)
    ]
    architecture = []
    for index, phase in enumerate(PHASES):
        architecture.append(
            {
                "range": phase,
                "central_question": "question",
                "protagonist_goal": "goal",
                "conflict": "conflict",
                "characters": ["character"],
                "growth_and_resources": "growth",
                "emotion_payoff": "payoff",
                "mainline_progress": "progress",
                "fatigue_refresh": "refresh",
                "structure_refresh": "new structure" if index in (0, 3) else "",
                "irreversible_change": "change",
                "material_support": [{"status": "SUPPORTED", "material_id": "CARD:1"}],
            }
        )
    return {
        "schema_version": 1,
        "plan_id": "PLAN:TEST",
        "status": "candidate",
        "creation_mode": "greenfield",
        "plan_mode": "full",
        "brief": {},
        "shared_library_root": "D:/shared/novel-material-library",
        "market_evidence": {"as_of": "2026-09-19", "sources": ["ranking"], "samples": samples, "signals": signals, "coverage_status": "complete", "bias_notes": []},
        "library_usage": {"formal_card_ids": ["CARD:1"], "dna_candidate_ids": ["DNA:1"], "gaps": []},
        "concept_options": [
            concept("A", "SIG:A", "formal_card_ids", "CARD:1"),
            concept("B", "SIG:B", "dna_candidate_ids", "DNA:1"),
            concept("C", "SIG:C", "formal_card_ids", "CARD:1"),
        ],
        "recommendation": {"concept_id": "A", "outcome": "RECOMMEND"},
        "architecture_concept_id": "A",
        "architecture_300": architecture,
        "longline_engine_summary": "longline",
        "debt_ledgers": {key: [debt(key)] for key in DEBT_KEYS},
        "material_gap_orders": [],
        "pending_decisions": [],
    }


def validate(plan: dict) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as temp_dir:
        target = Path(temp_dir) / "plan.json"
        target.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), str(target)],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return result.returncode, result.stdout


def main() -> int:
    base = valid_plan()
    cases = [("valid", base, True)]

    empty_core = copy.deepcopy(base)
    empty_core["concept_options"][0]["reader_promise"] = ""
    cases.append(("empty concept core", empty_core, False))

    unknown_signal = copy.deepcopy(base)
    unknown_signal["concept_options"][0]["market_signal_ids"] = ["SIG:UNKNOWN"]
    cases.append(("unknown market signal", unknown_signal, False))

    unknown_material = copy.deepcopy(base)
    unknown_material["architecture_300"][0]["material_support"][0]["material_id"] = "CARD:UNKNOWN"
    cases.append(("unknown material", unknown_material, False))

    empty_debt = copy.deepcopy(base)
    empty_debt["debt_ledgers"]["antagonist"] = []
    cases.append(("empty antagonist debt", empty_debt, False))

    bad_support = copy.deepcopy(base)
    bad_support["architecture_300"][0]["material_support"] = "CARD:1"
    cases.append(("invalid material support type", bad_support, False))

    titles_only = copy.deepcopy(base)
    for sample in titles_only["market_evidence"]["samples"]:
        sample["content_status"] = "metadata_only"
        sample["analyzed_chapters"] = []
        sample["opening_analysis"] = {}
    cases.append(("ranking titles without text analysis cannot recommend", titles_only, False))

    too_few_analyzed = copy.deepcopy(base)
    for sample in too_few_analyzed["market_evidence"]["samples"][5:]:
        sample["content_status"] = "partial"
        sample["analyzed_chapters"] = [1, 2, 3]
        sample["opening_analysis"] = {"first_scene": "partial"}
    cases.append(("fewer than six complete opening samples cannot recommend", too_few_analyzed, False))

    failures = []
    for name, payload, should_pass in cases:
        returncode, output = validate(payload)
        passed = returncode == 0
        if passed != should_pass:
            failures.append({"case": name, "output": output})
    print(json.dumps({"ok": not failures, "cases": len(cases), "failures": failures}, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
