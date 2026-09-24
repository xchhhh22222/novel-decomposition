#!/usr/bin/env python3
"""Validate V1.2 market-benchmark and climax-backplanning artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


BENCHMARK_TOP_FIELDS = {
    "sample_id", "rank", "title", "content_status", "chapters_analyzed", "structural_card"
}
STRUCTURAL_CARD_FIELDS = {
    "conflict_latency", "payoff_latency", "goal_relay", "hook_strength",
    "emotion_progression", "chapter_4_10_loop", "supporting_character_efficiency",
    "structural_clarity", "evidence_locations",
}
DEEP_DIVE_FIELDS = {
    "sample_id", "selected_reason", "primary_strength", "secondary_strength",
    "what_not_to_copy", "deep_dive_status", "chapters_analyzed", "chapter_structures",
}
CHAPTER_STRUCTURE_FIELDS = {
    "chapter", "protagonist_goal", "obstacle", "protagonist_action",
    "supporting_character_functions", "payoff", "reader_emotion", "hook",
    "hook_type", "next_click_reason", "state_change", "evidence_locations",
}
LESSON_FIELDS = {
    "lesson_id", "pattern", "observed_in_sample_ids", "best_use_window",
    "retention_reason", "adaptation_rule", "copy_boundary",
}

TARGET_FIELDS = {
    "target_id", "name", "target_type", "reader_promise", "known_function",
    "unknown_potential", "protagonist_need", "rival_needs", "clue_entry",
    "access_gate", "location_or_holder", "competing_factions", "failure_cost",
    "payoff_if_obtained", "irreversible_change", "next_stage_seed", "material_refs",
}
FACTION_FIELDS = {
    "faction_id", "name", "role", "controlled_assets_or_permissions",
    "core_interest", "available_leverage", "stage_entry",
}
CLIMAX_FIELDS = {
    "climax_id", "chapter_window", "strategic_target_id", "protagonist_goal",
    "why_now", "qualification_or_access_gate", "competing_factions",
    "named_rivals_or_roles", "obstacles", "information_disadvantages",
    "resource_constraints", "relationship_pressures", "pre_climax_state",
    "payoff", "cost", "irreversible_change", "next_stage_seed",
    "previous_climax_dependency", "material_refs", "benchmark_lesson_ids",
    "backward_beats",
}
PRE_STATE_FIELDS = {"identity", "power", "resources", "relationships", "information"}
BEAT_FIELDS = {
    "beat_id", "chapter_window", "required_state", "objective",
    "obstacle_function", "supporting_character_function", "mini_payoff",
    "hook_function", "leads_to", "benchmark_lesson_ids",
}
SPINE_FIELDS = {
    "chapter_window", "stage_objective", "main_obstacle",
    "supporting_character_functions", "payoff", "emotion_goal", "hook_function",
    "strategic_target_progress", "climax_link", "benchmark_lesson_ids", "state_change",
}
FUTURE_SEED_FIELDS = {
    "seed_id", "stage_name", "potential_target_core", "world_level_change",
    "faction_change", "protagonist_state_change",
}

CONTENT_STATUS = {"pass", "partial", "metadata_only", "failed"}
DEEP_STATUS = {"pass", "partial", "failed"}
HOOK_TYPES = {
    "new_goal", "danger", "reward", "reveal", "exposure", "actor_entry",
    "relationship", "countdown", "cost", "other",
}
TARGET_TYPES = {
    "manual", "inheritance", "artifact", "rare_resource", "access_key",
    "qualification", "secret", "technology", "identity", "other",
}


def missing_fields(value: Any, fields: set[str], where: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{where} must be an object")
        return
    missing = sorted(fields - set(value))
    if missing:
        errors.append(f"{where} missing: {', '.join(missing)}")


def nonempty(value: Any) -> bool:
    return value not in (None, "", [], {})


def string_list(value: Any, allow_empty: bool = True) -> bool:
    return isinstance(value, list) and (allow_empty or bool(value)) and all(
        isinstance(item, str) and item.strip() for item in value
    )


def chapter_window(value: Any) -> tuple[int, int] | None:
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r"\s*(\d+)\s*-\s*(\d+)\s*", value)
    if not match:
        return None
    start, end = map(int, match.groups())
    if start < 1 or end < start:
        return None
    return start, end


def validate_market(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version", "benchmark_id", "status", "category", "snapshot_at",
        "selection_rule", "top10", "selected_deep_dives", "structural_lessons",
    }
    missing_fields(data, required, "benchmark", errors)
    if data.get("schema_version") != 1:
        errors.append("benchmark.schema_version must be 1")
    if data.get("status") not in {"complete", "partial", "hold"}:
        errors.append("benchmark.status must be complete/partial/hold")
    if data.get("selection_rule") != "structural_learning_not_similarity":
        errors.append("benchmark.selection_rule must be structural_learning_not_similarity")
    for key in ("benchmark_id", "category", "snapshot_at"):
        if not nonempty(data.get(key)):
            errors.append(f"benchmark.{key} cannot be empty")

    top10 = data.get("top10")
    sample_ids: set[str] = set()
    pass10 = 0
    if not isinstance(top10, list) or len(top10) != 10:
        errors.append("benchmark.top10 must contain exactly 10 ranked samples")
    else:
        ranks: list[int] = []
        for index, sample in enumerate(top10):
            where = f"benchmark.top10[{index}]"
            missing_fields(sample, BENCHMARK_TOP_FIELDS, where, errors)
            if not isinstance(sample, dict):
                continue
            sid = sample.get("sample_id")
            if not isinstance(sid, str) or not sid.strip():
                errors.append(f"{where}.sample_id cannot be empty")
            elif sid in sample_ids:
                errors.append(f"{where}.sample_id must be unique")
            else:
                sample_ids.add(sid)
            rank = sample.get("rank")
            if not isinstance(rank, int):
                errors.append(f"{where}.rank must be integer")
            else:
                ranks.append(rank)
            if sample.get("content_status") not in CONTENT_STATUS:
                errors.append(f"{where}.content_status invalid")
            chapters = sample.get("chapters_analyzed")
            if not isinstance(chapters, list) or not all(isinstance(x, int) for x in chapters):
                errors.append(f"{where}.chapters_analyzed must be integer list")
            if sample.get("content_status") == "pass":
                if chapters != list(range(1, 11)):
                    errors.append(f"{where}: pass requires chapters 1-10")
                else:
                    pass10 += 1
            card = sample.get("structural_card")
            missing_fields(card, STRUCTURAL_CARD_FIELDS, f"{where}.structural_card", errors)
            if isinstance(card, dict):
                if not isinstance(card.get("evidence_locations"), list):
                    errors.append(f"{where}.structural_card.evidence_locations must be list")
        if sorted(ranks) != list(range(1, 11)):
            errors.append("benchmark.top10 ranks must be exactly 1..10")

    deep = data.get("selected_deep_dives")
    deep_ids: set[str] = set()
    full_deep = 0
    if not isinstance(deep, list) or len(deep) != 3:
        errors.append("benchmark.selected_deep_dives must contain exactly 3 samples")
    else:
        for index, item in enumerate(deep):
            where = f"benchmark.selected_deep_dives[{index}]"
            missing_fields(item, DEEP_DIVE_FIELDS, where, errors)
            if not isinstance(item, dict):
                continue
            sid = item.get("sample_id")
            if sid not in sample_ids:
                errors.append(f"{where}.sample_id must reference top10")
            if isinstance(sid, str):
                if sid in deep_ids:
                    errors.append(f"{where}.sample_id must be unique")
                deep_ids.add(sid)
            for key in ("selected_reason", "primary_strength", "secondary_strength", "what_not_to_copy"):
                if not nonempty(item.get(key)):
                    errors.append(f"{where}.{key} cannot be empty")
            status = item.get("deep_dive_status")
            if status not in DEEP_STATUS:
                errors.append(f"{where}.deep_dive_status invalid")
            chapters = item.get("chapters_analyzed")
            structures = item.get("chapter_structures")
            if not isinstance(chapters, list) or not all(isinstance(x, int) for x in chapters):
                errors.append(f"{where}.chapters_analyzed must be integer list")
                chapters = []
            if not isinstance(structures, list):
                errors.append(f"{where}.chapter_structures must be list")
                structures = []
            observed: list[int] = []
            for cindex, chapter in enumerate(structures):
                cwhere = f"{where}.chapter_structures[{cindex}]"
                missing_fields(chapter, CHAPTER_STRUCTURE_FIELDS, cwhere, errors)
                if not isinstance(chapter, dict):
                    continue
                number = chapter.get("chapter")
                if not isinstance(number, int) or not 1 <= number <= 20:
                    errors.append(f"{cwhere}.chapter must be 1..20")
                else:
                    observed.append(number)
                for key in (
                    "protagonist_goal", "obstacle", "protagonist_action", "payoff",
                    "reader_emotion", "hook", "next_click_reason", "state_change",
                ):
                    if not nonempty(chapter.get(key)):
                        errors.append(f"{cwhere}.{key} cannot be empty")
                if chapter.get("hook_type") not in HOOK_TYPES:
                    errors.append(f"{cwhere}.hook_type invalid")
                if not isinstance(chapter.get("supporting_character_functions"), list):
                    errors.append(f"{cwhere}.supporting_character_functions must be list")
                if not isinstance(chapter.get("evidence_locations"), list):
                    errors.append(f"{cwhere}.evidence_locations must be list")
            if len(observed) != len(set(observed)):
                errors.append(f"{where}.chapter_structures chapter numbers must be unique")
            if status == "pass":
                if chapters != list(range(1, 21)):
                    errors.append(f"{where}: pass requires chapters 1-20")
                if sorted(observed) != list(range(1, 21)):
                    errors.append(f"{where}: pass requires 20 chapter structures")
                else:
                    full_deep += 1

    lessons = data.get("structural_lessons")
    lesson_ids: set[str] = set()
    if not isinstance(lessons, list) or not lessons:
        errors.append("benchmark.structural_lessons must be non-empty list")
    else:
        for index, lesson in enumerate(lessons):
            where = f"benchmark.structural_lessons[{index}]"
            missing_fields(lesson, LESSON_FIELDS, where, errors)
            if not isinstance(lesson, dict):
                continue
            lid = lesson.get("lesson_id")
            if not isinstance(lid, str) or not lid.strip():
                errors.append(f"{where}.lesson_id cannot be empty")
            elif lid in lesson_ids:
                errors.append(f"{where}.lesson_id must be unique")
            else:
                lesson_ids.add(lid)
            refs = lesson.get("observed_in_sample_ids")
            if not isinstance(refs, list) or not refs:
                errors.append(f"{where}.observed_in_sample_ids must be non-empty list")
            elif not set(map(str, refs)).issubset(sample_ids):
                errors.append(f"{where}.observed_in_sample_ids must reference top10")
            for key in ("pattern", "best_use_window", "retention_reason", "adaptation_rule", "copy_boundary"):
                if not nonempty(lesson.get(key)):
                    errors.append(f"{where}.{key} cannot be empty")

    if data.get("status") == "complete":
        if pass10 < 6:
            errors.append("complete benchmark requires at least 6 full top10 samples")
        if full_deep != 3:
            errors.append("complete benchmark requires all 3 deep dives through chapter 20")
    return errors


def validate_climax(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version", "backplan_id", "status", "horizon_chapters",
        "target_major_climax_count", "benchmark_lesson_ids", "faction_pool",
        "strategic_targets", "major_climaxes", "story_spine_1_100",
        "future_climax_seeds",
    }
    missing_fields(data, required, "backplan", errors)
    if data.get("schema_version") != 1:
        errors.append("backplan.schema_version must be 1")
    if data.get("status") not in {"complete", "partial", "hold"}:
        errors.append("backplan.status must be complete/partial/hold")
    if data.get("horizon_chapters") != 100:
        errors.append("backplan.horizon_chapters must be 100")
    target_count = data.get("target_major_climax_count")
    if not isinstance(target_count, int) or not 1 <= target_count <= 4:
        errors.append("backplan.target_major_climax_count must be integer 1..4")
        target_count = 2
    lesson_ids = set(map(str, data.get("benchmark_lesson_ids", []))) if isinstance(data.get("benchmark_lesson_ids"), list) else set()

    factions = data.get("faction_pool")
    faction_ids: set[str] = set()
    if not isinstance(factions, list) or not factions:
        errors.append("backplan.faction_pool must be non-empty list")
    else:
        for index, faction in enumerate(factions):
            where = f"backplan.faction_pool[{index}]"
            missing_fields(faction, FACTION_FIELDS, where, errors)
            if not isinstance(faction, dict):
                continue
            fid = faction.get("faction_id")
            if not isinstance(fid, str) or not fid.strip():
                errors.append(f"{where}.faction_id cannot be empty")
            elif fid in faction_ids:
                errors.append(f"{where}.faction_id must be unique")
            else:
                faction_ids.add(fid)
            for key in FACTION_FIELDS - {"faction_id"}:
                if not nonempty(faction.get(key)):
                    errors.append(f"{where}.{key} cannot be empty")

    targets = data.get("strategic_targets")
    target_ids: set[str] = set()
    if not isinstance(targets, list) or not targets:
        errors.append("backplan.strategic_targets must be non-empty list")
    else:
        for index, target in enumerate(targets):
            where = f"backplan.strategic_targets[{index}]"
            missing_fields(target, TARGET_FIELDS, where, errors)
            if not isinstance(target, dict):
                continue
            tid = target.get("target_id")
            if not isinstance(tid, str) or not tid.strip():
                errors.append(f"{where}.target_id cannot be empty")
            elif tid in target_ids:
                errors.append(f"{where}.target_id must be unique")
            else:
                target_ids.add(tid)
            if target.get("target_type") not in TARGET_TYPES:
                errors.append(f"{where}.target_type invalid")
            for key in (
                "name", "reader_promise", "known_function", "protagonist_need",
                "clue_entry", "access_gate", "location_or_holder", "failure_cost",
                "payoff_if_obtained", "irreversible_change", "next_stage_seed",
            ):
                if not nonempty(target.get(key)):
                    errors.append(f"{where}.{key} cannot be empty")
            if not string_list(target.get("rival_needs"), allow_empty=False):
                errors.append(f"{where}.rival_needs must be non-empty string list")
            if not string_list(target.get("competing_factions"), allow_empty=False):
                errors.append(f"{where}.competing_factions must be non-empty string list")
            else:
                unknown = set(target.get("competing_factions", [])) - faction_ids
                if unknown:
                    errors.append(f"{where}.competing_factions references unknown factions: {', '.join(sorted(unknown))}")
            if not isinstance(target.get("material_refs"), list):
                errors.append(f"{where}.material_refs must be list")

    climaxes = data.get("major_climaxes")
    climax_ids: set[str] = set()
    windows: list[tuple[int, int, str]] = []
    if not isinstance(climaxes, list) or len(climaxes) != target_count:
        errors.append("backplan.major_climaxes count must equal target_major_climax_count")
    else:
        for index, climax in enumerate(climaxes):
            where = f"backplan.major_climaxes[{index}]"
            missing_fields(climax, CLIMAX_FIELDS, where, errors)
            if not isinstance(climax, dict):
                continue
            cid = climax.get("climax_id")
            if not isinstance(cid, str) or not cid.strip():
                errors.append(f"{where}.climax_id cannot be empty")
                cid = f"#{index}"
            elif cid in climax_ids:
                errors.append(f"{where}.climax_id must be unique")
            else:
                climax_ids.add(cid)
            win = chapter_window(climax.get("chapter_window"))
            if win is None or win[1] > 100:
                errors.append(f"{where}.chapter_window must be within 1-100")
            else:
                windows.append((win[0], win[1], str(cid)))
            if climax.get("strategic_target_id") not in target_ids:
                errors.append(f"{where}.strategic_target_id must reference strategic_targets")
            competing = climax.get("competing_factions")
            if not string_list(competing, allow_empty=False):
                errors.append(f"{where}.competing_factions must be non-empty string list")
            else:
                if data.get("status") == "complete" and len(set(competing)) < 2:
                    errors.append(f"{where}: complete climax requires at least 2 competing factions")
                unknown = set(competing) - faction_ids
                if unknown:
                    errors.append(f"{where}.competing_factions references unknown factions: {', '.join(sorted(unknown))}")
            state = climax.get("pre_climax_state")
            missing_fields(state, PRE_STATE_FIELDS, f"{where}.pre_climax_state", errors)
            for key in (
                "protagonist_goal", "why_now", "qualification_or_access_gate",
                "payoff", "cost", "irreversible_change", "next_stage_seed",
                "previous_climax_dependency",
            ):
                if not nonempty(climax.get(key)):
                    errors.append(f"{where}.{key} cannot be empty")
            refs = climax.get("benchmark_lesson_ids")
            if not isinstance(refs, list):
                errors.append(f"{where}.benchmark_lesson_ids must be list")
            elif lesson_ids and not set(map(str, refs)).issubset(lesson_ids):
                errors.append(f"{where}.benchmark_lesson_ids contains unknown lesson")
            beats = climax.get("backward_beats")
            if not isinstance(beats, list) or not 4 <= len(beats) <= 8:
                errors.append(f"{where}.backward_beats must contain 4..8 beats")
                beats = []
            beat_ids: set[str] = set()
            for bindex, beat in enumerate(beats):
                bwhere = f"{where}.backward_beats[{bindex}]"
                missing_fields(beat, BEAT_FIELDS, bwhere, errors)
                if not isinstance(beat, dict):
                    continue
                bid = beat.get("beat_id")
                if not isinstance(bid, str) or not bid.strip():
                    errors.append(f"{bwhere}.beat_id cannot be empty")
                elif bid in beat_ids:
                    errors.append(f"{bwhere}.beat_id must be unique within climax")
                else:
                    beat_ids.add(bid)
                bwin = chapter_window(beat.get("chapter_window"))
                if bwin is None or bwin[1] > 100:
                    errors.append(f"{bwhere}.chapter_window must be within 1-100")
                for key in (
                    "required_state", "objective", "obstacle_function",
                    "supporting_character_function", "mini_payoff", "hook_function", "leads_to",
                ):
                    if not nonempty(beat.get(key)):
                        errors.append(f"{bwhere}.{key} cannot be empty")
                lrefs = beat.get("benchmark_lesson_ids")
                if not isinstance(lrefs, list):
                    errors.append(f"{bwhere}.benchmark_lesson_ids must be list")
                elif lesson_ids and not set(map(str, lrefs)).issubset(lesson_ids):
                    errors.append(f"{bwhere}.benchmark_lesson_ids contains unknown lesson")
        windows.sort()
        for left, right in zip(windows, windows[1:]):
            if right[0] <= left[1]:
                errors.append(f"major climax windows overlap: {left[2]} and {right[2]}")

    spine = data.get("story_spine_1_100")
    if not isinstance(spine, list) or len(spine) < 6:
        errors.append("backplan.story_spine_1_100 must contain at least 6 nodes")
    else:
        for index, node in enumerate(spine):
            where = f"backplan.story_spine_1_100[{index}]"
            missing_fields(node, SPINE_FIELDS, where, errors)
            if not isinstance(node, dict):
                continue
            win = chapter_window(node.get("chapter_window"))
            if win is None or win[1] > 100:
                errors.append(f"{where}.chapter_window must be within 1-100")
            if node.get("climax_link") not in climax_ids:
                errors.append(f"{where}.climax_link must reference major_climaxes")
            refs = node.get("benchmark_lesson_ids")
            if not isinstance(refs, list):
                errors.append(f"{where}.benchmark_lesson_ids must be list")
            elif lesson_ids and not set(map(str, refs)).issubset(lesson_ids):
                errors.append(f"{where}.benchmark_lesson_ids contains unknown lesson")
            for key in (
                "stage_objective", "main_obstacle", "payoff", "emotion_goal",
                "hook_function", "strategic_target_progress", "state_change",
            ):
                if not nonempty(node.get(key)):
                    errors.append(f"{where}.{key} cannot be empty")
            if not isinstance(node.get("supporting_character_functions"), list):
                errors.append(f"{where}.supporting_character_functions must be list")

    seeds = data.get("future_climax_seeds")
    if not isinstance(seeds, list) or len(seeds) > 6:
        errors.append("backplan.future_climax_seeds must be list with at most 6 items")
    else:
        for index, seed in enumerate(seeds):
            where = f"backplan.future_climax_seeds[{index}]"
            missing_fields(seed, FUTURE_SEED_FIELDS, where, errors)
            if isinstance(seed, dict):
                for key in FUTURE_SEED_FIELDS:
                    if not nonempty(seed.get(key)):
                        errors.append(f"{where}.{key} cannot be empty")

    if data.get("status") == "complete":
        if target_count != 2:
            errors.append("complete default V1.2 backplan requires target_major_climax_count=2 unless using a separately documented override")
        if len(target_ids) < target_count:
            errors.append("complete backplan requires at least one strategic target per major climax")
        if len(windows) == 2 and not (windows[0][1] < windows[1][0]):
            errors.append("complete backplan requires climax 2 after climax 1")
    return errors


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact_type", choices=("benchmark", "climax"))
    parser.add_argument("target", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.target.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "errors": [str(exc)]}, ensure_ascii=False, indent=2))
        return 1
    if not isinstance(data, dict):
        errors = ["artifact root must be object"]
    elif args.artifact_type == "benchmark":
        errors = validate_market(data)
    else:
        errors = validate_climax(data)
    print(json.dumps({"ok": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
