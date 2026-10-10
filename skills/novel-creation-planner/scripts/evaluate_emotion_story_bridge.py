#!/usr/bin/env python3
"""Compare paired legacy/enhanced plans by story behavior, never by field count."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def option_metrics(option: dict[str, Any]) -> dict[str, Any]:
    nodes = option.get("story_nodes", [])
    if option.get("mode") == "E2_E3_ENABLED":
        expectations = option.get("emotion_lines", [])
        expectation_contracts = [item.get("payoff_contract") for item in expectations]
        weave_choices = [item.get("effect_on_choice") for item in option.get("weaves", []) if item.get("effect_on_choice")]
        handoff = option.get("handoff", {})
        overlap = bool(handoff.get("trigger_node_id") and handoff.get("withheld_questions"))
    else:
        expectations = option.get("reader_expectations", [])
        expectation_contracts = [item.get("payoff") for item in expectations]
        weave_choices = [node.get("character_choice") for node in nodes if len(node.get("decision_makers", [])) >= 2]
        overlap = any(node.get("opens_next_arc") for node in nodes)
    return {
        "distinct_reader_expectations": len({item for item in expectation_contracts if item}),
        "causal_nodes_with_choice_and_consequence": sum(bool(node.get("cause") and node.get("character_choice") and node.get("consequence")) for node in nodes),
        "multi_actor_choices": sum(len(node.get("decision_makers", [])) >= 2 for node in nodes),
        "emotion_or_relationship_choice_links": len(weave_choices),
        "distinct_payoff_results": len({item for item in expectation_contracts if item}),
        "credible_early_next_arc_entry_present": overlap,
        "nodes_with_targeted_material_use": sum(bool(node.get("material_uses")) for node in nodes),
        "material_uses_with_action_effect": sum(
            bool(use.get("effect_on_action")) for node in nodes for use in node.get("material_uses", [])
        ),
        "rejected_or_conflicted_materials": sum(
            len(slot.get("rejected_refs", [])) + len(slot.get("rule_conflicts", [])) for slot in option.get("material_slots", [])
        ),
        "fifty_chapter_phases": len(option.get("chapter_phases", [])),
        "continuation_conditions": len(option.get("continuation_conditions", [])),
    }


def evaluate(enhanced: dict[str, Any], legacy: dict[str, Any], brief_sha256: str) -> dict[str, Any]:
    enhanced_by_pair = {item["pair_id"]: item for item in enhanced.get("options", [])}
    legacy_by_pair = {item["pair_id"]: item for item in legacy.get("options", [])}
    if set(enhanced_by_pair) != set(legacy_by_pair):
        raise ValueError("paired option IDs differ")
    comparisons = []
    for pair_id in sorted(enhanced_by_pair):
        comparisons.append({
            "pair_id": pair_id,
            "same_sparse_brief_sha256": brief_sha256,
            "legacy": option_metrics(legacy_by_pair[pair_id]),
            "enhanced": option_metrics(enhanced_by_pair[pair_id]),
            "interpretation": (
                "Metrics expose expectation separation, causal choices, payoff independence, early overlap and node-level material use. "
                "They do not establish prose quality, originality, reader response or final literary superiority."
            ),
        })
    return {
        "schema_version": "emotion_story_bridge_comparison_v1",
        "status": "candidate",
        "qa_status": "HOLD",
        "evaluation_basis": "paired story behavior and causal obligations, not field count, hit rate, file count or shared Story Spine names",
        "brief_sha256": brief_sha256,
        "pair_comparisons": comparisons,
        "capability_observation": "E2_E3_EXPLICIT_OBLIGATION_TRACKING_OBSERVED",
        "creative_quality": "PENDING_INDEPENDENT_REVIEW",
        "independent_semantic_review_checklist": [
            "Do the two enhanced concepts differ in causal engine rather than names and surface nouns?",
            "Does every selected emotion-source pattern remain an abstraction rather than a copied event chain?",
            "Do relationship actors alter a feasible choice, cost or result instead of merely reacting?",
            "Does each payoff produce visible safety, capability, relationship or institutional change without substituting for another contract?",
            "Does the second macro arc reveal only a trigger and bounded clue before the first arc pays?",
            "Do selected 02-09 components satisfy their stated interfaces after adaptation, including resource and failure conditions?",
            "Are source-concentration, repeated conflict and suspense-stalling risks acceptable for chapters 1-50?",
            "Can chapters 51+ continue from explicit unresolved conditions rather than a new unrelated crisis?",
        ],
        "failure_cases_retained": [
            "future-premonition candidate rejected where the slot requires earned, cost-bearing protective output",
            "blanket attachment of all material IDs to every node is a validation failure",
            "reader knowledge introduced before its trigger node is a validation failure",
            "a new macro arc cancelling the old settlement contract is a validation failure",
            "a selected source absent from deterministic retrieval/provenance is a validation failure",
            "two options with the same causal signature and renamed surfaces are a validation failure",
        ],
        "material_adaptation": "REVIEW_REQUIRED",
        "production_promotion": "NOT_RUN",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Fairly compare Emotion-to-Story Bridge plans.")
    parser.add_argument("--enhanced", type=Path, required=True)
    parser.add_argument("--legacy", type=Path, required=True)
    parser.add_argument("--brief-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = evaluate(load(args.enhanced), load(args.legacy), args.brief_sha256)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"ok": True, **result}, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
