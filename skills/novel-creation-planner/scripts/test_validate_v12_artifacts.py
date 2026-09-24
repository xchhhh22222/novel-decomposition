#!/usr/bin/env python3
"""Regression tests for V1.2 benchmark/climax artifact validator."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

VALIDATOR = Path(__file__).with_name("validate_v12_artifacts.py")


def run(kind: str, payload: dict) -> bool:
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / f"{kind}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), kind, str(path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        return result.returncode == 0


def chapter_struct(chapter: int) -> dict:
    return {
        "chapter": chapter,
        "protagonist_goal": "goal",
        "obstacle": "obstacle",
        "protagonist_action": "action",
        "supporting_character_functions": [{"role": "support", "function": "pressure"}],
        "payoff": "payoff",
        "reader_emotion": "anticipation",
        "hook": "new unresolved question",
        "hook_type": "new_goal",
        "next_click_reason": "answer requires next chapter",
        "state_change": "state changed",
        "evidence_locations": [f"ch{chapter}"],
    }


def benchmark() -> dict:
    top10 = []
    for rank in range(1, 11):
        top10.append({
            "sample_id": f"S{rank:02d}",
            "rank": rank,
            "title": f"book-{rank}",
            "content_status": "pass",
            "chapters_analyzed": list(range(1, 11)),
            "structural_card": {
                "conflict_latency": "ch1",
                "payoff_latency": "ch2",
                "goal_relay": "continuous",
                "hook_strength": "clear unresolved question",
                "emotion_progression": "pressure-payoff-new pressure",
                "chapter_4_10_loop": "goal-obstacle-payoff-next goal",
                "supporting_character_efficiency": "pressure and validation",
                "structural_clarity": "goal-obstacle-action-payoff-hook",
                "evidence_locations": ["ch1", "ch10"],
            },
        })
    deep = []
    for sid, strength in (("S01", "pace"), ("S02", "hooks"), ("S03", "goal relay")):
        deep.append({
            "sample_id": sid,
            "selected_reason": f"strong {strength}",
            "primary_strength": strength,
            "secondary_strength": "emotion",
            "what_not_to_copy": "names and concrete event chain",
            "deep_dive_status": "pass",
            "chapters_analyzed": list(range(1, 21)),
            "chapter_structures": [chapter_struct(i) for i in range(1, 21)],
        })
    return {
        "schema_version": 1,
        "benchmark_id": "MK:TEST",
        "status": "complete",
        "category": "都市高武",
        "snapshot_at": "2026-09-24",
        "selection_rule": "structural_learning_not_similarity",
        "top10": top10,
        "selected_deep_dives": deep,
        "structural_lessons": [{
            "lesson_id": "MK:LESSON:001",
            "pattern": "conflict then fast payoff then next goal",
            "observed_in_sample_ids": ["S01", "S02"],
            "best_use_window": "1-3",
            "retention_reason": "question relay",
            "adaptation_rule": "replace setting, actors, reward and conflict",
            "copy_boundary": "do not copy concrete events",
        }],
    }


def target(target_id: str, faction_ids: list[str]) -> dict:
    return {
        "target_id": target_id,
        "name": f"target-{target_id}",
        "target_type": "inheritance",
        "reader_promise": "major growth promise",
        "known_function": "solves a current bottleneck",
        "unknown_potential": "larger secret",
        "protagonist_need": "must solve bottleneck now",
        "rival_needs": ["rival also needs advancement"],
        "clue_entry": "early clue",
        "access_gate": "qualification",
        "location_or_holder": "restricted zone",
        "competing_factions": faction_ids,
        "failure_cost": "lose growth window",
        "payoff_if_obtained": "new route opens",
        "irreversible_change": "enters faction attention",
        "next_stage_seed": "reveals next map",
        "material_refs": ["DNA:1"],
    }


def beat(cid: str, i: int, lesson: str) -> dict:
    return {
        "beat_id": f"{cid}:B{i}",
        "chapter_window": f"{1 + (i-1)*5}-{5 + (i-1)*5}",
        "required_state": "required state",
        "objective": "objective",
        "obstacle_function": "gate",
        "supporting_character_function": "pressure",
        "mini_payoff": "partial progress",
        "hook_function": "new goal",
        "leads_to": f"{cid}:B{i+1}" if i < 4 else cid,
        "benchmark_lesson_ids": [lesson],
    }


def climax() -> dict:
    factions = [
        {
            "faction_id": "F1",
            "name": "official",
            "role": "official regulator",
            "controlled_assets_or_permissions": "access",
            "core_interest": "stability",
            "available_leverage": "qualification",
            "stage_entry": "early",
        },
        {
            "faction_id": "F2",
            "name": "group",
            "role": "private group",
            "controlled_assets_or_permissions": "capital and equipment",
            "core_interest": "exclusive gain",
            "available_leverage": "resources",
            "stage_entry": "early",
        },
    ]
    lesson = "MK:LESSON:001"
    c1 = {
        "climax_id": "CLIMAX:01",
        "chapter_window": "35-40",
        "strategic_target_id": "TARGET:001",
        "protagonist_goal": "win target one",
        "why_now": "window closes",
        "qualification_or_access_gate": "qualification",
        "competing_factions": ["F1", "F2"],
        "named_rivals_or_roles": ["rival"],
        "obstacles": ["gate"],
        "information_disadvantages": ["partial clue"],
        "resource_constraints": ["limited supply"],
        "relationship_pressures": ["team conflict"],
        "pre_climax_state": {
            "identity": "rookie", "power": "low", "resources": "limited",
            "relationships": "unstable", "information": "partial",
        },
        "payoff": "wins target",
        "cost": "ability partly exposed",
        "irreversible_change": "enters faction attention",
        "next_stage_seed": "new map revealed",
        "previous_climax_dependency": "ROOT",
        "material_refs": ["DNA:1"],
        "benchmark_lesson_ids": [lesson],
        "backward_beats": [beat("CLIMAX:01", i, lesson) for i in range(1, 5)],
    }
    c2 = copy.deepcopy(c1)
    c2.update({
        "climax_id": "CLIMAX:02",
        "chapter_window": "88-96",
        "strategic_target_id": "TARGET:002",
        "protagonist_goal": "win target two",
        "previous_climax_dependency": "CLIMAX:01 result exposes route and creates new enemy",
    })
    c2["backward_beats"] = [
        {
            **beat("CLIMAX:02", i, lesson),
            "chapter_window": f"{55 + (i-1)*8}-{60 + (i-1)*8}",
        }
        for i in range(1, 5)
    ]
    spine = []
    windows = ["1-3", "4-10", "11-20", "21-34", "35-40", "41-60", "61-80", "81-87", "88-96", "97-100"]
    for index, window in enumerate(windows):
        link = "CLIMAX:01" if index <= 4 else "CLIMAX:02"
        spine.append({
            "chapter_window": window,
            "stage_objective": "stage objective",
            "main_obstacle": "stage obstacle",
            "supporting_character_functions": ["pressure", "validation"],
            "payoff": "visible payoff",
            "emotion_goal": "anticipation",
            "hook_function": "next goal",
            "strategic_target_progress": "progress",
            "climax_link": link,
            "benchmark_lesson_ids": [lesson],
            "state_change": "state changed",
        })
    return {
        "schema_version": 1,
        "backplan_id": "BP:TEST",
        "status": "complete",
        "horizon_chapters": 100,
        "target_major_climax_count": 2,
        "benchmark_lesson_ids": [lesson],
        "faction_pool": factions,
        "strategic_targets": [target("TARGET:001", ["F1", "F2"]), target("TARGET:002", ["F1", "F2"])],
        "major_climaxes": [c1, c2],
        "story_spine_1_100": spine,
        "future_climax_seeds": [],
    }


def main() -> int:
    cases: list[tuple[str, str, dict, bool]] = []
    b = benchmark()
    cases.append(("benchmark valid", "benchmark", b, True))
    bad_rule = copy.deepcopy(b)
    bad_rule["selection_rule"] = "similarity"
    cases.append(("benchmark rejects similarity selection", "benchmark", bad_rule, False))
    shallow = copy.deepcopy(b)
    shallow["selected_deep_dives"][0]["chapters_analyzed"] = list(range(1, 11))
    shallow["selected_deep_dives"][0]["chapter_structures"] = [chapter_struct(i) for i in range(1, 11)]
    cases.append(("complete benchmark requires 20 chapters", "benchmark", shallow, False))

    c = climax()
    cases.append(("climax valid", "climax", c, True))
    too_few_beats = copy.deepcopy(c)
    too_few_beats["major_climaxes"][0]["backward_beats"] = too_few_beats["major_climaxes"][0]["backward_beats"][:3]
    cases.append(("climax requires four beats", "climax", too_few_beats, False))
    unknown_target = copy.deepcopy(c)
    unknown_target["major_climaxes"][0]["strategic_target_id"] = "TARGET:UNKNOWN"
    cases.append(("climax target must exist", "climax", unknown_target, False))

    failures = []
    for name, kind, payload, expected in cases:
        actual = run(kind, payload)
        if actual != expected:
            failures.append(name)
    print(json.dumps({"ok": not failures, "cases": len(cases), "failures": failures}, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
