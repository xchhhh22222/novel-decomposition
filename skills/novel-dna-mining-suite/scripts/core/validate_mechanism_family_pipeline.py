#!/usr/bin/env python3
"""Validate the V1.7.0 staged reusable mechanism-family pipeline."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

STAGES = [
    "MECHANISM_CARD_EXTRACTION",
    "READINESS_NORMALIZATION",
    "PAIR_CALIBRATION",
    "FAMILY_PILOT",
    "BOUNDARY_STRESS_TEST",
    "DOMAIN_EXPANSION",
    "DOMAIN_FULL",
    "CROSS_DOMAIN_ONTOLOGY",
    "FULL_LIBRARY",
]
READINESS = {"READY", "READY_WITH_BOUNDARY", "HOLD_CORE_UNKNOWN"}
PAIR_DECISIONS = {"SAME_MECHANISM", "SUBTYPE", "ANALOGOUS", "DIFFERENT", "HOLD"}
MEMBER_RESULTS = {
    "PASS_SAME",
    "PASS_SUBTYPE",
    "OUTSIDE_ANALOGOUS",
    "OUTSIDE_DIFFERENT",
    "HOLD",
}
VALIDATED_LANES = {
    ("character_function", "relationship_engine"),
    ("golden_finger", "GF_CORE"),
    ("plotline", "plotline_progression_engine"),
}
CALIBRATION_CATEGORIES = {
    "OBVIOUS_SAME",
    "PARAPHRASE_EQUIVALENT",
    "SAME_SURFACE_DIFFERENT_MECHANISM",
    "LIKELY_SUBTYPE",
    "ANALOGOUS",
    "DIFFERENT",
    "BOUNDARY_OR_HOLD",
}
CALIBRATION_DECISIONS = {
    "OBVIOUS_SAME": {"SAME_MECHANISM"},
    "PARAPHRASE_EQUIVALENT": {"SAME_MECHANISM"},
    "SAME_SURFACE_DIFFERENT_MECHANISM": {"DIFFERENT", "ANALOGOUS"},
    "LIKELY_SUBTYPE": {"SUBTYPE"},
    "ANALOGOUS": {"ANALOGOUS"},
    "DIFFERENT": {"DIFFERENT"},
    "BOUNDARY_OR_HOLD": {"HOLD", "DIFFERENT", "ANALOGOUS"},
}
MANDATORY_PREDECESSORS = {
    "MECHANISM_CARD_EXTRACTION": [],
    "READINESS_NORMALIZATION": ["MECHANISM_CARD_EXTRACTION"],
    "PAIR_CALIBRATION": ["MECHANISM_CARD_EXTRACTION", "READINESS_NORMALIZATION"],
    "FAMILY_PILOT": ["MECHANISM_CARD_EXTRACTION", "READINESS_NORMALIZATION", "PAIR_CALIBRATION"],
    "BOUNDARY_STRESS_TEST": ["MECHANISM_CARD_EXTRACTION", "READINESS_NORMALIZATION", "PAIR_CALIBRATION", "FAMILY_PILOT"],
    "DOMAIN_EXPANSION": ["MECHANISM_CARD_EXTRACTION", "READINESS_NORMALIZATION", "PAIR_CALIBRATION", "FAMILY_PILOT", "BOUNDARY_STRESS_TEST"],
    "DOMAIN_FULL": ["MECHANISM_CARD_EXTRACTION", "READINESS_NORMALIZATION", "PAIR_CALIBRATION", "FAMILY_PILOT", "BOUNDARY_STRESS_TEST", "DOMAIN_EXPANSION"],
    "CROSS_DOMAIN_ONTOLOGY": ["MECHANISM_CARD_EXTRACTION", "READINESS_NORMALIZATION", "PAIR_CALIBRATION", "FAMILY_PILOT", "BOUNDARY_STRESS_TEST", "DOMAIN_EXPANSION", "DOMAIN_FULL"],
    "FULL_LIBRARY": ["MECHANISM_CARD_EXTRACTION", "READINESS_NORMALIZATION", "PAIR_CALIBRATION", "FAMILY_PILOT", "BOUNDARY_STRESS_TEST", "DOMAIN_EXPANSION", "DOMAIN_FULL"],
}
HISTORY_REVIEW_STAGES = {
    "PAIR_CALIBRATION",
    "FAMILY_PILOT",
    "BOUNDARY_STRESS_TEST",
    "DOMAIN_EXPANSION",
    "DOMAIN_FULL",
}
CARD_FIELDS = {
    "card_id",
    "domain",
    "comparison_lane",
    "source_primary_object",
    "trigger_or_input",
    "actor_or_operating_subject",
    "core_operation_chain",
    "target_object",
    "resulting_state",
    "feedback_or_growth_loop",
    "failure_or_stop_condition",
    "primary_evidence_refs",
    "corroborating_evidence_refs",
    "unknown_classification",
    "comparison_readiness",
    "derived_commentary",
}
FAMILY_FIELDS = {
    "family_id",
    "domain",
    "family_status",
    "family_name",
    "core_mechanism_definition",
    "one_sentence_core",
    "minimum_definition",
    "hard_invariants",
    "allowed_variations",
    "exclusion_boundary",
    "termination_condition",
    "why_it_recurs",
    "same_members",
    "subtype_members",
    "analogous_references",
    "hold_boundary_references",
    "false_positive_examples",
    "member_definition_tests",
    "positive_support_pair_ids",
    "negative_boundary_pair_ids",
    "structural_analogy_pair_ids",
}
MINIMUM_FIELDS = {"trigger", "transformation", "state_change", "recurrence", "termination"}
REVIEW_STOP_STAGES = {
    "PAIR_CALIBRATION",
    "FAMILY_PILOT",
    "BOUNDARY_STRESS_TEST",
    "DOMAIN_EXPANSION",
}


def _nonempty(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip()) and value.strip().upper() != "UNKNOWN"
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return bool(value)
    return value is not None


def _list(value: Any) -> List[Any]:
    return list(value) if isinstance(value, list) else []


def _gate(errors: List[str]) -> Dict[str, Any]:
    return {"status": "PASS" if not errors else "FAIL", "errors": errors}


def _ids(values: Iterable[Any]) -> set[str]:
    result: set[str] = set()
    for value in values:
        if isinstance(value, str):
            result.add(value)
        elif isinstance(value, Mapping):
            member_id = value.get("card_id") or value.get("member_id")
            if isinstance(member_id, str):
                result.add(member_id)
    return result


def validate_document(document: Mapping[str, Any]) -> Dict[str, Any]:
    cards = _list(document.get("cards"))
    pairs = _list(document.get("pairs"))
    families = _list(document.get("families"))
    controls = document.get("run_controls") if isinstance(document.get("run_controls"), Mapping) else {}
    phase = document.get("phase")
    gates: Dict[str, Dict[str, Any]] = {}

    errors: List[str] = []
    history = _list(document.get("stage_history"))
    seen: Dict[str, List[Mapping[str, Any]]] = {}
    previous_rank = -1
    expansion_ids: set[str] = set()
    for index, entry in enumerate(history):
        if not isinstance(entry, Mapping):
            errors.append(f"stage_history[{index}] must be an object")
            continue
        stage = entry.get("stage")
        if stage not in STAGES:
            errors.append(f"stage_history[{index}] has invalid stage {stage}")
            continue
        rank = STAGES.index(stage)
        if rank < previous_rank:
            errors.append(f"stage_history[{index}] is out of stage order")
        previous_rank = max(previous_rank, rank)
        if entry.get("status") != "PASS":
            errors.append(f"stage_history[{index}] predecessor status must be PASS")
        if not _nonempty(entry.get("artifact_id")):
            errors.append(f"stage_history[{index}] requires artifact_id")
        seen.setdefault(stage, []).append(entry)
        if stage != "DOMAIN_EXPANSION" and len(seen[stage]) > 1:
            errors.append(f"stage {stage} may not be duplicated")
        if stage == "DOMAIN_EXPANSION":
            batch_id = entry.get("batch_id") or entry.get("artifact_id")
            if not _nonempty(batch_id):
                errors.append(f"stage_history[{index}] expansion requires batch_id or artifact_id")
            elif str(batch_id) in expansion_ids:
                errors.append(f"duplicate DOMAIN_EXPANSION artifact/batch id: {batch_id}")
            else:
                expansion_ids.add(str(batch_id))
    for predecessor in MANDATORY_PREDECESSORS.get(str(phase), []):
        entries = seen.get(predecessor, [])
        if not entries:
            errors.append(f"{phase} missing mandatory predecessor {predecessor}")
            continue
        if predecessor in HISTORY_REVIEW_STAGES:
            if not any(entry.get("human_review") == "APPROVED" for entry in entries):
                errors.append(f"{predecessor} predecessor requires APPROVED human review")
    if phase == "DOMAIN_FULL":
        approved_expansions = [
            entry for entry in seen.get("DOMAIN_EXPANSION", [])
            if entry.get("status") == "PASS" and entry.get("human_review") == "APPROVED"
        ]
        if not approved_expansions:
            errors.append("DOMAIN_FULL requires an approved DOMAIN_EXPANSION history record")
        declared_count = controls.get("successful_expansion_count")
        if declared_count is not None and declared_count != len(approved_expansions):
            errors.append("successful_expansion_count does not match approved expansion history")
    if phase == "FULL_LIBRARY":
        approved_domain_full = [
            entry for entry in seen.get("DOMAIN_FULL", [])
            if entry.get("status") == "PASS" and entry.get("human_review") == "APPROVED"
        ]
        if not approved_domain_full:
            errors.append("FULL_LIBRARY requires an approved DOMAIN_FULL history record")
    gates["STAGE_TRANSITION_GATE"] = _gate(errors)

    errors = []
    card_by_id: Dict[str, Mapping[str, Any]] = {}
    for index, card in enumerate(cards):
        if not isinstance(card, Mapping):
            errors.append(f"cards[{index}] must be an object")
            continue
        missing = sorted(CARD_FIELDS - set(card))
        if missing:
            errors.append(f"{card.get('card_id', index)} missing fields: {', '.join(missing)}")
        card_id = card.get("card_id")
        if not isinstance(card_id, str) or not card_id:
            errors.append(f"cards[{index}] has no card_id")
        elif card_id in card_by_id:
            errors.append(f"duplicate card_id: {card_id}")
        else:
            card_by_id[card_id] = card
        if card.get("comparison_readiness") not in READINESS:
            errors.append(f"{card_id}: invalid comparison_readiness")
        if not isinstance(card.get("core_operation_chain"), list) or not card.get("core_operation_chain"):
            errors.append(f"{card_id}: core_operation_chain must be non-empty")
        if not isinstance(card.get("source_primary_object"), Mapping) or not card.get("source_primary_object"):
            errors.append(f"{card_id}: source_primary_object must be non-empty")
    gates["MECHANISM_CARD_SCHEMA_GATE"] = _gate(errors)

    errors = []
    approvals = set(_list(controls.get("human_approvals")))
    lanes = {
        (str(card.get("domain")), str(card.get("comparison_lane")))
        for card in cards
        if isinstance(card, Mapping) and card.get("domain") and card.get("comparison_lane")
    }
    if phase in {"DOMAIN_EXPANSION", "DOMAIN_FULL", "FULL_LIBRARY"}:
        for domain, lane in sorted(lanes):
            approval = f"APPROVE_LANE_VALIDATION:{domain}:{lane}"
            if (domain, lane) not in VALIDATED_LANES and approval not in approvals:
                errors.append(f"{domain}/{lane} is CALIBRATION_REQUIRED and lacks {approval}")
    gates["VALIDATED_SCOPE_GATE"] = _gate(errors)

    errors = []
    for card in cards:
        if not isinstance(card, Mapping):
            continue
        unknown = card.get("unknown_classification")
        if not isinstance(unknown, Mapping):
            errors.append(f"{card.get('card_id')}: unknown_classification must be an object")
            continue
        core = _list(unknown.get("core_mechanism_unknowns"))
        peripheral = _list(unknown.get("peripheral_unknowns"))
        readiness = card.get("comparison_readiness")
        if core and readiness != "HOLD_CORE_UNKNOWN":
            errors.append(f"{card.get('card_id')}: core unknowns require HOLD_CORE_UNKNOWN")
        if not core and peripheral and readiness == "HOLD_CORE_UNKNOWN":
            errors.append(f"{card.get('card_id')}: peripheral unknowns alone cannot force HOLD")
        if not core and peripheral and readiness not in {"READY_WITH_BOUNDARY", "READY"}:
            errors.append(f"{card.get('card_id')}: peripheral unknown readiness is invalid")
    gates["CORE_VS_PERIPHERAL_UNKNOWN_GATE"] = _gate(errors)

    errors = []
    for card in cards:
        if not isinstance(card, Mapping):
            continue
        cid = card.get("card_id")
        primary = _list(card.get("primary_evidence_refs"))
        corroborating = _list(card.get("corroborating_evidence_refs"))
        if card.get("comparison_readiness") != "HOLD_CORE_UNKNOWN" and not primary:
            errors.append(f"{cid}: comparison-ready card needs primary evidence")
        if not primary and corroborating and card.get("comparison_readiness") != "HOLD_CORE_UNKNOWN":
            errors.append(f"{cid}: corroborating evidence cannot replace primary evidence")
        support_roles = set(_list(card.get("semantic_support_roles")))
        if "derived_commentary" in support_roles or "corroborating_context_only" in support_roles:
            errors.append(f"{cid}: non-primary material used as semantic support")
    for pair in pairs:
        if isinstance(pair, Mapping):
            support = pair.get("support_provenance")
            if isinstance(support, Mapping):
                if support.get("keyword_hint_used_as_support") is True:
                    errors.append(f"{pair.get('pair_id')}: keyword hint used as support")
                if support.get("linked_context_only_support") is True:
                    errors.append(f"{pair.get('pair_id')}: linked context only support")
                if support.get("derived_commentary_used_as_support") is True:
                    errors.append(f"{pair.get('pair_id')}: derived commentary used as support")
    gates["PRIMARY_EVIDENCE_ISOLATION_GATE"] = _gate(errors)

    errors = []
    underlying_primary: Dict[str, str] = {}
    for card in cards:
        if not isinstance(card, Mapping):
            continue
        role = card.get("projection_semantic_role")
        cid = card.get("card_id")
        if role == "CORROBORATING_VIEW" and card.get("comparison_pool_eligible") is True:
            errors.append(f"{cid}: corroborating projection cannot enter comparison pool")
        underlying = card.get("underlying_mechanism_id")
        if role == "PRIMARY_MECHANISM" and isinstance(underlying, str):
            if underlying in underlying_primary:
                errors.append(f"{cid}: duplicate primary projection for {underlying}")
            underlying_primary[underlying] = str(cid)
        if role == "INDEPENDENT_MECHANISM" and not _list(card.get("primary_evidence_refs")):
            errors.append(f"{cid}: independent projection requires its own primary evidence")
    gates["PROJECTION_DUPLICATION_GATE"] = _gate(errors)

    errors = []
    for pair in pairs:
        if not isinstance(pair, Mapping):
            errors.append("pair must be an object")
            continue
        left = card_by_id.get(pair.get("left_card_id"))
        right = card_by_id.get(pair.get("right_card_id"))
        if left is None or right is None:
            errors.append(f"{pair.get('pair_id')}: pair card not found")
            continue
        if left.get("domain") != right.get("domain") or left.get("comparison_lane") != right.get("comparison_lane"):
            errors.append(f"{pair.get('pair_id')}: cross-domain or cross-lane pair")
        if left.get("comparison_readiness") == "HOLD_CORE_UNKNOWN" and pair.get("decision") != "HOLD":
            errors.append(f"{pair.get('pair_id')}: core-unknown left card requires HOLD")
        if right.get("comparison_readiness") == "HOLD_CORE_UNKNOWN" and pair.get("decision") != "HOLD":
            errors.append(f"{pair.get('pair_id')}: core-unknown right card requires HOLD")
    gates["COMPARISON_LANE_ISOLATION_GATE"] = _gate(errors)

    errors = []
    required_pair_fields = {
        "pair_id",
        "left_card_id",
        "right_card_id",
        "decision",
        "mechanism_core_layer",
        "downstream_effect_layer",
        "transfer_dimension",
        "reason",
    }
    for pair in pairs:
        if not isinstance(pair, Mapping):
            continue
        missing = sorted(required_pair_fields - set(pair))
        if missing:
            errors.append(f"{pair.get('pair_id')}: missing pair fields: {', '.join(missing)}")
        if pair.get("decision") not in PAIR_DECISIONS:
            errors.append(f"{pair.get('pair_id')}: invalid decision")
        if pair.get("decision") == "SUBTYPE" and not _nonempty(pair.get("transfer_dimension")):
            errors.append(f"{pair.get('pair_id')}: SUBTYPE requires transfer_dimension")
        if pair.get("selection_basis") in {"RANDOM_ONLY", "KEYWORD_ONLY", "EMBEDDING_ONLY"}:
            errors.append(f"{pair.get('pair_id')}: unrepresentative selection basis")
        category = pair.get("calibration_category")
        if category not in CALIBRATION_CATEGORIES:
            errors.append(f"{pair.get('pair_id')}: invalid or missing calibration_category")
        elif pair.get("decision") not in CALIBRATION_DECISIONS[category]:
            errors.append(f"{pair.get('pair_id')}: decision is incompatible with calibration_category {category}")
    derived_categories = {
        pair.get("calibration_category")
        for pair in pairs
        if isinstance(pair, Mapping) and pair.get("calibration_category") in CALIBRATION_CATEGORIES
    }
    declared_categories = set(_list(controls.get("pair_coverage_categories")))
    if phase == "PAIR_CALIBRATION" and not CALIBRATION_CATEGORIES.issubset(derived_categories):
        errors.append("pair calibration real records do not cover all required categories")
    if declared_categories and declared_categories != derived_categories:
        errors.append("pair_coverage_categories summary does not match categories derived from real pairs")
    gates["PAIR_CALIBRATION_GATE"] = _gate(errors)

    errors = []
    for pair in pairs:
        if not isinstance(pair, Mapping):
            continue
        if not _nonempty(pair.get("mechanism_core_layer")):
            errors.append(f"{pair.get('pair_id')}: missing mechanism_core_layer")
        if not _nonempty(pair.get("downstream_effect_layer")):
            errors.append(f"{pair.get('pair_id')}: missing downstream_effect_layer")
        if pair.get("decision_basis") == "DOWNSTREAM_EFFECT":
            errors.append(f"{pair.get('pair_id')}: downstream effect cannot decide identity")
    gates["MECHANISM_CORE_VS_DOWNSTREAM_GATE"] = _gate(errors)

    errors = []
    for family in families:
        if not isinstance(family, Mapping):
            continue
        members = _ids(_list(family.get("same_members")) + _list(family.get("subtype_members")))
        analogous = _ids(_list(family.get("analogous_references")))
        overlap = members & analogous
        if overlap:
            errors.append(f"{family.get('family_id')}: analogous references in membership: {sorted(overlap)}")
        for test in _list(family.get("member_definition_tests")):
            if isinstance(test, Mapping) and test.get("result") == "OUTSIDE_ANALOGOUS" and test.get("member_id") in members:
                errors.append(f"{family.get('family_id')}: OUTSIDE_ANALOGOUS member admitted")
    gates["ANALOGOUS_MEMBERSHIP_ISOLATION_GATE"] = _gate(errors)

    errors = []
    for family in families:
        if not isinstance(family, Mapping):
            errors.append("family must be an object")
            continue
        missing = sorted(FAMILY_FIELDS - set(family))
        if missing:
            errors.append(f"{family.get('family_id')}: missing family fields: {', '.join(missing)}")
        minimum = family.get("minimum_definition")
        if not isinstance(minimum, Mapping):
            errors.append(f"{family.get('family_id')}: minimum_definition must be an object")
        else:
            empty = sorted(k for k in MINIMUM_FIELDS if not _nonempty(minimum.get(k)))
            if empty:
                errors.append(f"{family.get('family_id')}: incomplete minimum definition: {', '.join(empty)}")
        for field in ("core_mechanism_definition", "one_sentence_core", "termination_condition", "why_it_recurs"):
            if not _nonempty(family.get(field)):
                errors.append(f"{family.get('family_id')}: empty {field}")
        if not _list(family.get("hard_invariants")):
            errors.append(f"{family.get('family_id')}: hard_invariants required")
    gates["FAMILY_MINIMUM_DEFINITION_GATE"] = _gate(errors)

    errors = []
    for family in families:
        if not isinstance(family, Mapping):
            continue
        same = _ids(_list(family.get("same_members")))
        subtype = _ids(_list(family.get("subtype_members")))
        tests = {
            test.get("member_id"): test.get("result")
            for test in _list(family.get("member_definition_tests"))
            if isinstance(test, Mapping)
        }
        for member in same:
            if tests.get(member) != "PASS_SAME":
                errors.append(f"{family.get('family_id')}: {member} lacks PASS_SAME")
        for member in subtype:
            if tests.get(member) != "PASS_SUBTYPE":
                errors.append(f"{family.get('family_id')}: {member} lacks PASS_SUBTYPE")
        invalid = sorted(set(tests.values()) - MEMBER_RESULTS)
        if invalid:
            errors.append(f"{family.get('family_id')}: invalid member test results: {invalid}")
    gates["MEMBER_INDEPENDENT_DEFINITION_TEST_GATE"] = _gate(errors)

    errors = []
    for family in families:
        if not isinstance(family, Mapping):
            continue
        if family.get("membership_basis") not in {None, "INDIVIDUAL_DEFINITION_TEST"}:
            errors.append(f"{family.get('family_id')}: membership basis is not independent definition tests")
        if family.get("single_link_chaining") is True or family.get("auto_connected_components") is True:
            errors.append(f"{family.get('family_id')}: single-link chaining is prohibited")
    gates["CHAINING_PROHIBITION_GATE"] = _gate(errors)

    errors = []
    for family in families:
        if not isinstance(family, Mapping):
            continue
        if not _list(family.get("exclusion_boundary")):
            errors.append(f"{family.get('family_id')}: exclusion_boundary required")
        if not _list(family.get("negative_boundary_pair_ids")):
            errors.append(f"{family.get('family_id')}: negative boundary pair required")
        if not _list(family.get("false_positive_examples")):
            errors.append(f"{family.get('family_id')}: false-positive example required")
    gates["FAMILY_NEGATIVE_BOUNDARY_GATE"] = _gate(errors)

    errors = []
    pair_by_id = {
        pair.get("pair_id"): pair
        for pair in pairs
        if isinstance(pair, Mapping) and isinstance(pair.get("pair_id"), str)
    }
    for family in families:
        if not isinstance(family, Mapping):
            continue
        fid = family.get("family_id")
        same = _ids(_list(family.get("same_members")))
        subtypes = _ids(_list(family.get("subtype_members")))
        positive_members = same | subtypes
        analogous = _ids(_list(family.get("analogous_references")))
        hold = _ids(_list(family.get("hold_boundary_references")))
        if same & subtypes:
            errors.append(f"{fid}: same_members and subtype_members overlap")
        for member_id in sorted(positive_members):
            if member_id not in card_by_id:
                errors.append(f"{fid}: positive member does not exist: {member_id}")
        if positive_members & analogous:
            errors.append(f"{fid}: analogous reference appears in positive membership")
        if positive_members & hold:
            errors.append(f"{fid}: HOLD reference appears in positive membership")
        canonical = family.get("canonical_member_id")
        tests = {
            test.get("member_id"): test.get("result")
            for test in _list(family.get("member_definition_tests"))
            if isinstance(test, Mapping)
        }
        if canonical is not None:
            if canonical not in card_by_id or canonical not in positive_members:
                errors.append(f"{fid}: canonical member must exist in positive membership")
            if tests.get(canonical) not in {"PASS_SAME", "PASS_SUBTYPE"}:
                errors.append(f"{fid}: canonical member lacks an independent PASS definition test")

        positive_pairs = set(_list(family.get("positive_support_pair_ids")))
        negative_pairs = set(_list(family.get("negative_boundary_pair_ids")))
        analogy_pairs = set(_list(family.get("structural_analogy_pair_ids")))
        if positive_pairs & (negative_pairs | analogy_pairs):
            errors.append(f"{fid}: positive pair provenance overlaps a boundary/analogy role")
        if negative_pairs & analogy_pairs:
            errors.append(f"{fid}: negative and structural-analogy provenance overlap")
        for pair_id in positive_pairs:
            pair = pair_by_id.get(pair_id)
            if pair is None:
                errors.append(f"{fid}: nonexistent positive support pair {pair_id}")
                continue
            decision = pair.get("decision")
            subtype_allowed = decision == "SUBTYPE" and pair.get("family_support_role") == "SUBTYPE_SUPPORT"
            if decision != "SAME_MECHANISM" and not subtype_allowed:
                errors.append(f"{fid}: pair {pair_id} is not valid positive family support")
            pair_members = {pair.get("left_card_id"), pair.get("right_card_id")}
            if not (pair_members & positive_members):
                errors.append(f"{fid}: pair {pair_id} does not reference this family's positive members")
        for pair_id in negative_pairs:
            pair = pair_by_id.get(pair_id)
            if pair is None:
                errors.append(f"{fid}: nonexistent negative boundary pair {pair_id}")
                continue
            left_id = pair.get("left_card_id")
            right_id = pair.get("right_card_id")
            left_positive = left_id in positive_members or left_id == canonical
            right_positive = right_id in positive_members or right_id == canonical
            if left_positive == right_positive:
                errors.append(f"{fid}: negative pair {pair_id} must connect one positive member to one outside candidate")
            if pair.get("decision") not in {"ANALOGOUS", "DIFFERENT", "HOLD"}:
                errors.append(f"{fid}: pair {pair_id} judgment is incompatible with negative-boundary role")
        for pair_id in analogy_pairs:
            pair = pair_by_id.get(pair_id)
            if pair is None:
                errors.append(f"{fid}: nonexistent structural analogy pair {pair_id}")
                continue
            explicit_role = pair.get("family_support_role") == "STRUCTURAL_ANALOGY"
            if pair.get("decision") != "ANALOGOUS" and not explicit_role:
                errors.append(f"{fid}: pair {pair_id} is not a structural analogy")
    gates["FAMILY_PROVENANCE_INTEGRITY_GATE"] = _gate(errors)

    errors = []
    for family in families:
        if not isinstance(family, Mapping) or family.get("family_status") != "STABLE":
            continue
        fid = family.get("family_id")
        members = _ids(_list(family.get("same_members")) + _list(family.get("subtype_members")))
        tests = {
            test.get("member_id"): test.get("result")
            for test in _list(family.get("member_definition_tests"))
            if isinstance(test, Mapping)
        }
        books = {
            card_by_id[mid].get("source_primary_object", {}).get("book_id")
            for mid in members
            if mid in card_by_id and isinstance(card_by_id[mid].get("source_primary_object"), Mapping)
        }
        books.discard(None)
        if len(books) < 2:
            errors.append(f"{fid}: stable family needs positive members from at least two books")
        pattern_a = False
        for pair_id in _list(family.get("positive_support_pair_ids")):
            pair = pair_by_id.get(pair_id)
            if not pair or pair.get("decision") != "SAME_MECHANISM":
                continue
            left = card_by_id.get(pair.get("left_card_id"), {})
            right = card_by_id.get(pair.get("right_card_id"), {})
            left_book = left.get("source_primary_object", {}).get("book_id") if isinstance(left.get("source_primary_object"), Mapping) else None
            right_book = right.get("source_primary_object", {}).get("book_id") if isinstance(right.get("source_primary_object"), Mapping) else None
            pair_members = {pair.get("left_card_id"), pair.get("right_card_id")}
            if pair_members.issubset(members) and left_book and right_book and left_book != right_book:
                pattern_a = True
                break
        canonical = family.get("canonical_member_id")
        subtypes = _ids(_list(family.get("subtype_members")))
        canonical_valid = canonical in members and canonical in card_by_id and tests.get(canonical) in {"PASS_SAME", "PASS_SUBTYPE"}
        subtype_tests_valid = len(subtypes) >= 2 and all(tests.get(member) == "PASS_SUBTYPE" for member in subtypes)
        pattern_b = bool(
            canonical_valid
            and subtype_tests_valid
            and len(books) >= 2
            and family.get("boundary_stress_passed") is True
            and _list(family.get("hard_invariants"))
        )
        if not (pattern_a or pattern_b):
            exception = f"APPROVE_HOLD_FAMILY_EXCEPTION:{fid}"
            if exception not in approvals:
                errors.append(f"{fid}: stable family lacks Pattern A or Pattern B support")
    gates["STABLE_FAMILY_GATE"] = _gate(errors)

    errors = []
    for family in families:
        if not isinstance(family, Mapping):
            continue
        if family.get("family_status") in {"HOLD", "HOLD_FAMILY_HYPOTHESIS"} and family.get("promotion_status") not in {None, "NOT_RUN", "HOLD"}:
            errors.append(f"{family.get('family_id')}: HOLD family cannot be promoted")
    if controls.get("active_promotion") not in {None, False, "NOT_RUN"} and "APPROVE_PROMOTION" not in approvals:
        errors.append("active promotion lacks APPROVE_PROMOTION")
    gates["HOLD_FAMILY_PROMOTION_GATE"] = _gate(errors)

    errors = []
    if phase not in STAGES:
        errors.append(f"invalid phase: {phase}")
    card_count = len(cards)
    source_population = controls.get("source_population_size")
    if phase in {"MECHANISM_CARD_EXTRACTION", "READINESS_NORMALIZATION"} and controls.get("initial_calibration", True):
        valid_small_source = isinstance(source_population, int) and source_population < 30 and card_count == source_population
        if not (30 <= card_count <= 50 or valid_small_source):
            errors.append("initial calibration must use 30-50 cards or all of a smaller source")
    if phase == "PAIR_CALIBRATION" and not 10 <= len(pairs) <= 15:
        errors.append("pair calibration must use 10-15 representative pairs")
    if phase == "FAMILY_PILOT" and len(families) > 3:
        errors.append("first family pilot may create at most 3 hypotheses")
    if phase == "BOUNDARY_STRESS_TEST":
        for family in families:
            if isinstance(family, Mapping):
                count = family.get("stress_case_count", 0)
                if not isinstance(count, int) or count < 1:
                    errors.append(f"{family.get('family_id')}: boundary stress must be nonzero")
                if count < 5 and not _nonempty(family.get("reduced_stress_reason")):
                    errors.append(f"{family.get('family_id')}: reduced stress set needs a reason")
    if phase == "DOMAIN_EXPANSION":
        batch_size = controls.get("expansion_batch_size", card_count)
        if not isinstance(batch_size, int) or not 25 <= batch_size <= 50:
            errors.append("domain expansion batch must contain 25-50 cards")
    if phase == "DOMAIN_FULL":
        if controls.get("major_definition_drift") is True:
            errors.append("DOMAIN_FULL blocked by major definition drift")
        if "APPROVE_DOMAIN_FULL" not in approvals:
            errors.append("DOMAIN_FULL lacks APPROVE_DOMAIN_FULL")
    if phase == "FULL_LIBRARY" and "APPROVE_FULL_LIBRARY" not in approvals:
        errors.append("FULL_LIBRARY lacks APPROVE_FULL_LIBRARY")
    if controls.get("domain_full") is True and phase not in {"DOMAIN_FULL", "CROSS_DOMAIN_ONTOLOGY", "FULL_LIBRARY"}:
        errors.append("domain_full cannot run during an earlier phase")
    if controls.get("full_library") is True and phase != "FULL_LIBRARY":
        errors.append("full_library cannot run before FULL_LIBRARY")
    gates["PHASE_SCALE_GATE"] = _gate(errors)

    errors = []
    if phase in REVIEW_STOP_STAGES and document.get("next_state") != "STOP_FOR_HUMAN_REVIEW":
        errors.append(f"{phase} must stop for human review")
    if phase == "DOMAIN_FULL" and "APPROVE_DOMAIN_FULL" not in approvals:
        errors.append("human approval required before DOMAIN_FULL")
    if phase == "FULL_LIBRARY" and "APPROVE_FULL_LIBRARY" not in approvals:
        errors.append("human approval required before FULL_LIBRARY")
    gates["HUMAN_REVIEW_STOP_GATE"] = _gate(errors)

    errors = []
    for card in cards:
        if isinstance(card, Mapping) and "cluster_id" in card:
            errors.append(f"{card.get('card_id')}: legacy cluster_id present")
    for family in families:
        if not isinstance(family, Mapping):
            continue
        if "cluster_id" in family:
            errors.append(f"{family.get('family_id')}: cluster_id cannot identify a family")
        if family.get("legacy_membership_used_as_support") is True:
            errors.append(f"{family.get('family_id')}: legacy membership used as support")
    gates["LEGACY_CLUSTER_ISOLATION_GATE"] = _gate(errors)

    errors = []
    pattern = re.compile(r"^RMF:[A-Z0-9_]+:[a-f0-9]{8,64}$")
    for family in families:
        if not isinstance(family, Mapping):
            continue
        fid = family.get("family_id")
        if not isinstance(fid, str) or not pattern.match(fid):
            errors.append(f"{fid}: invalid RMF namespace")
        if family.get("fingerprint_basis") == "MEMBER_ORDER":
            errors.append(f"{fid}: fingerprint cannot depend on member order")
        if family.get("definition_changed") is True and family.get("family_id_unchanged") is True:
            errors.append(f"{fid}: changed definition requires a new family ID")
    gates["FAMILY_ID_NAMESPACE_GATE"] = _gate(errors)

    failed = [name for name, gate in gates.items() if gate["status"] == "FAIL"]
    status = "PASS" if not failed else "HOLD"
    return {
        "schema_version": "1.7.0",
        "pipeline_status": status,
        "gates": gates,
        "failed_gates": failed,
        "runtime": {
            "PIPELINE_STATUS": status,
            "DOMAIN_FULL": "NOT_RUN" if failed or phase != "DOMAIN_FULL" else "ELIGIBLE",
            "FULL_LIBRARY": "NOT_RUN" if failed or phase != "FULL_LIBRARY" else "ELIGIBLE",
            "ACTIVE_PROMOTION": "NOT_RUN",
        },
    }


def validate_calibration_case(case: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate one compact synthetic QA case used by regression fixtures."""
    errors: List[str] = []
    decision = case.get("decision")
    if decision not in PAIR_DECISIONS:
        errors.append("invalid decision")
    if not _nonempty(case.get("mechanism_core_layer")):
        errors.append("missing mechanism_core_layer")
    if not _nonempty(case.get("downstream_effect_layer")):
        errors.append("missing downstream_effect_layer")
    if decision == "SUBTYPE" and not _nonempty(case.get("transfer_dimension")):
        errors.append("SUBTYPE requires transfer_dimension")
    if case.get("left_lane") != case.get("right_lane"):
        errors.append("comparison lane mismatch")
    if case.get("core_unknown") and decision != "HOLD":
        errors.append("core unknown requires HOLD")
    if case.get("peripheral_unknown") and case.get("comparison_readiness") == "HOLD_CORE_UNKNOWN":
        errors.append("peripheral unknown alone cannot force HOLD_CORE_UNKNOWN")
    if case.get("semantic_support") in {"LINKED_CONTEXT_ONLY", "DERIVED_COMMENTARY_ONLY", "KEYWORD_ONLY"}:
        errors.append("invalid semantic support source")
    if decision == "ANALOGOUS" and case.get("membership") is not False:
        errors.append("ANALOGOUS requires membership=false")
    if case.get("projection_semantic_role") == "CORROBORATING_VIEW" and case.get("membership") is not False:
        errors.append("corroborating projection cannot be a member")
    if case.get("expected_outside_member") and case.get("expected_outside_member") in set(_list(case.get("family_members"))):
        errors.append("chaining trap member was auto-admitted")
    if case.get("decision_basis") == "DOWNSTREAM_EFFECT":
        errors.append("downstream effect cannot decide identity")
    if case.get("surface_only_same") and decision in {"SAME_MECHANISM", "SUBTYPE"}:
        errors.append("surface similarity cannot establish mechanism identity")
    return {"status": "PASS" if not errors else "HOLD", "errors": errors}


def _load(path: Path) -> Mapping[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise ValueError("root JSON value must be an object")
    return value


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        report = validate_document(_load(args.input))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        report = {
            "schema_version": "1.7.0",
            "pipeline_status": "HOLD",
            "failed_gates": ["INPUT_GATE"],
            "gates": {"INPUT_GATE": {"status": "FAIL", "errors": [str(exc)]}},
            "runtime": {
                "PIPELINE_STATUS": "HOLD",
                "DOMAIN_FULL": "NOT_RUN",
                "FULL_LIBRARY": "NOT_RUN",
                "ACTIVE_PROMOTION": "NOT_RUN",
            },
        }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["pipeline_status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())

