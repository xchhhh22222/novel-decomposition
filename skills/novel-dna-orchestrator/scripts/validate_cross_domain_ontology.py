#!/usr/bin/env python3
"""Validate V1.7.0 cross-domain ontology candidates built from stable families."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence

IDENTITY_RELATIONS = {
    "META_EQUIVALENT",
    "META_SPECIALIZATION_CANDIDATE",
    "STRUCTURAL_ANALOGY",
    "DISTINCT",
    "HOLD",
}
COMPOSITION_RELATIONS = {
    "LEFT_CAN_FEED_RIGHT",
    "RIGHT_CAN_FEED_LEFT",
    "BIDIRECTIONAL_POSSIBLE",
    "NONE",
    "HOLD",
}
SIGNATURE_FIELDS = {
    "family_id",
    "domain",
    "trigger_semantics",
    "transformation_semantics",
    "state_variable_changed",
    "feedback_or_recurrence",
    "validity_basis",
    "termination_condition",
    "hard_invariants",
    "exclusion_boundary",
}
CONCEPT_FIELDS = {
    "ontology_id",
    "status",
    "concept_name",
    "abstract_core",
    "one_sentence_core",
    "required_invariants",
    "domain_realizations",
    "allowed_variations",
    "exclusion_boundary",
    "false_positive_tests",
    "positive_support_pair_ids",
    "negative_boundary_pair_ids",
    "structural_analogy_pair_ids",
    "composition_reference_pair_ids",
    "why_this_is_not_a_family_merge",
    "non_triviality_test",
    "confidence",
}
INVARIANT_FIELDS = {"trigger", "transformation", "state_change", "feedback", "termination"}
TRIVIAL_CORES = {
    "input output",
    "state change loop",
    "feedback loop",
    "growth loop",
    "action produces result",
    "information causes action",
    "resources produce growth",
}
VAGUE_STATE_VARIABLES = {"", "state", "status", "change", "progress", "growth", "result", "状态", "变化", "进展", "成长", "结果"}


def _list(value: Any) -> List[Any]:
    return list(value) if isinstance(value, list) else []


def _nonempty(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip()) and value.strip().upper() != "UNKNOWN"
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, list):
        return bool(value)
    return value is not None


def _gate(errors: List[str]) -> Dict[str, Any]:
    return {"status": "PASS" if not errors else "FAIL", "errors": errors}


def _normalize(text: Any) -> str:
    value = str(text or "").lower()
    for token in ("→", "->", "-", "_", "/", ":", "，", ",", "。", "."):
        value = value.replace(token, " ")
    return " ".join(value.split())


def validate_document(document: Mapping[str, Any]) -> Dict[str, Any]:
    families = _list(document.get("families"))
    signatures = _list(document.get("normalized_signatures"))
    pairs = _list(document.get("pair_reviews"))
    concepts = _list(document.get("ontology_concepts"))
    compositions = _list(document.get("composition_links"))
    gates: Dict[str, Dict[str, Any]] = {}

    family_by_id = {
        item.get("family_id"): item
        for item in families
        if isinstance(item, Mapping) and isinstance(item.get("family_id"), str)
    }
    signature_by_id = {
        item.get("family_id"): item
        for item in signatures
        if isinstance(item, Mapping) and isinstance(item.get("family_id"), str)
    }
    pair_by_id = {
        item.get("pair_id"): item
        for item in pairs
        if isinstance(item, Mapping) and isinstance(item.get("pair_id"), str)
    }

    errors: List[str] = []
    for pair in pairs:
        if not isinstance(pair, Mapping):
            errors.append("pair review must be an object")
            continue
        for side in ("left_family_id", "right_family_id"):
            fid = pair.get(side)
            family = family_by_id.get(fid)
            if family is None:
                errors.append(f"{pair.get('pair_id')}: unknown {side} {fid}")
            elif family.get("family_status") != "STABLE":
                errors.append(f"{pair.get('pair_id')}: {fid} is not STABLE")
        if pair.get("raw_card_input") is True:
            errors.append(f"{pair.get('pair_id')}: raw cards cannot enter ontology comparison")
    gates["STABLE_FAMILY_INPUT_ONLY_GATE"] = _gate(errors)

    errors = []
    for family_id, family in family_by_id.items():
        if family.get("family_status") != "STABLE":
            continue
        signature = signature_by_id.get(family_id)
        if signature is None:
            errors.append(f"{family_id}: missing normalized signature")
            continue
        missing = sorted(SIGNATURE_FIELDS - set(signature))
        if missing:
            errors.append(f"{family_id}: signature missing {', '.join(missing)}")
        for field in SIGNATURE_FIELDS - {"family_id", "domain"}:
            if not _nonempty(signature.get(field)):
                errors.append(f"{family_id}: empty signature field {field}")
    gates["NORMALIZED_SIGNATURE_GATE"] = _gate(errors)

    errors = []
    for pair in pairs:
        if not isinstance(pair, Mapping):
            continue
        if pair.get("identity_relation") not in IDENTITY_RELATIONS:
            errors.append(f"{pair.get('pair_id')}: invalid identity relation")
        if pair.get("composition_relation") not in COMPOSITION_RELATIONS:
            errors.append(f"{pair.get('pair_id')}: invalid composition relation")
        if pair.get("identity_inferred_from_composition") is True:
            errors.append(f"{pair.get('pair_id')}: composition cannot imply identity")
        if pair.get("composition_inferred_from_identity") is True:
            errors.append(f"{pair.get('pair_id')}: identity cannot imply composition")
        if pair.get("identity_relation") == "META_EQUIVALENT" and pair.get("shared_causal_shape_only") is True:
            errors.append(f"{pair.get('pair_id')}: causal shape alone cannot prove META_EQUIVALENT")
    gates["IDENTITY_COMPOSITION_SEPARATION_GATE"] = _gate(errors)

    errors = []
    for concept in concepts:
        if not isinstance(concept, Mapping):
            errors.append("ontology concept must be an object")
            continue
        missing = sorted(CONCEPT_FIELDS - set(concept))
        if missing:
            errors.append(f"{concept.get('ontology_id')}: missing fields: {', '.join(missing)}")
        core = _normalize(concept.get("abstract_core"))
        sentence = _normalize(concept.get("one_sentence_core"))
        if core in TRIVIAL_CORES or sentence in TRIVIAL_CORES:
            errors.append(f"{concept.get('ontology_id')}: trivial parent concept")
        if concept.get("status") == "PASS":
            for field in ("non_triviality_test", "why_this_is_not_a_family_merge"):
                if not _nonempty(concept.get(field)):
                    errors.append(f"{concept.get('ontology_id')}: missing {field}")
            if not _list(concept.get("exclusion_boundary")) or not _list(concept.get("false_positive_tests")):
                errors.append(f"{concept.get('ontology_id')}: nontrivial concept needs exclusions and false-positive tests")
    gates["NONTRIVIAL_PARENT_GATE"] = _gate(errors)

    errors = []
    for signature in signatures:
        if not isinstance(signature, Mapping):
            continue
        state = _normalize(signature.get("state_variable_changed"))
        if state in VAGUE_STATE_VARIABLES:
            errors.append(f"{signature.get('family_id')}: state variable is too vague")
    for concept in concepts:
        if not isinstance(concept, Mapping):
            continue
        invariants = concept.get("required_invariants")
        if not isinstance(invariants, Mapping):
            errors.append(f"{concept.get('ontology_id')}: required_invariants must be an object")
            continue
        missing = sorted(k for k in INVARIANT_FIELDS if not _nonempty(invariants.get(k)))
        if missing:
            errors.append(f"{concept.get('ontology_id')}: missing invariant semantics: {', '.join(missing)}")
        if _normalize(invariants.get("state_change")) in VAGUE_STATE_VARIABLES:
            errors.append(f"{concept.get('ontology_id')}: state_change is too vague")
    gates["STATE_VARIABLE_SEMANTICS_GATE"] = _gate(errors)

    errors = []
    for concept in concepts:
        if not isinstance(concept, Mapping):
            continue
        if "source_pair_ids" in concept:
            errors.append(f"{concept.get('ontology_id')}: mixed source_pair_ids is prohibited")
        required_arrays = (
            "positive_support_pair_ids",
            "negative_boundary_pair_ids",
            "structural_analogy_pair_ids",
            "composition_reference_pair_ids",
        )
        for field in required_arrays:
            if not isinstance(concept.get(field), list):
                errors.append(f"{concept.get('ontology_id')}: {field} must be an array")
        positive = set(_list(concept.get("positive_support_pair_ids")))
        negative = set(_list(concept.get("negative_boundary_pair_ids")))
        if positive & negative:
            errors.append(f"{concept.get('ontology_id')}: positive and negative provenance overlap")
        if concept.get("status") == "PASS" and (not positive or not negative):
            errors.append(f"{concept.get('ontology_id')}: PASS requires positive and negative provenance")
    gates["POSITIVE_NEGATIVE_PROVENANCE_GATE"] = _gate(errors)

    errors = []
    for concept in concepts:
        if not isinstance(concept, Mapping):
            continue
        positives = set(_list(concept.get("positive_support_pair_ids")))
        analogies = set(_list(concept.get("structural_analogy_pair_ids")))
        overlap = positives & analogies
        if overlap:
            errors.append(f"{concept.get('ontology_id')}: structural analogy used as positive support")
        for pair_id in positives:
            pair = pair_by_id.get(pair_id)
            if pair and pair.get("identity_relation") == "STRUCTURAL_ANALOGY":
                errors.append(f"{concept.get('ontology_id')}: analogy pair {pair_id} is positive support")
    gates["STRUCTURAL_ANALOGY_ISOLATION_GATE"] = _gate(errors)

    errors = []
    for concept in concepts:
        if not isinstance(concept, Mapping):
            continue
        for pair_id in _list(concept.get("positive_support_pair_ids")):
            pair = pair_by_id.get(pair_id)
            if not pair:
                errors.append(f"{concept.get('ontology_id')}: unknown positive pair {pair_id}")
                continue
            for side in ("left_family_id", "right_family_id"):
                family = family_by_id.get(pair.get(side))
                if family and family.get("family_status") != "STABLE":
                    errors.append(f"{concept.get('ontology_id')}: HOLD family used as positive support")
        if concept.get("status") == "HOLD" and concept.get("promotion_status") not in {None, "HOLD", "NOT_RUN"}:
            errors.append(f"{concept.get('ontology_id')}: HOLD ontology cannot be promoted")
    gates["HOLD_ONTOLOGY_ISOLATION_GATE"] = _gate(errors)

    errors = []
    before = document.get("family_membership_before")
    after = document.get("family_membership_after")
    if before is not None or after is not None:
        if before != after:
            errors.append("family membership changed during ontology work")
    for concept in concepts:
        if isinstance(concept, Mapping) and not _nonempty(concept.get("why_this_is_not_a_family_merge")):
            errors.append(f"{concept.get('ontology_id')}: family-merge explanation required")
    gates["FAMILY_MEMBERSHIP_IMMUTABILITY_GATE"] = _gate(errors)

    errors = []
    for link in compositions:
        if not isinstance(link, Mapping):
            errors.append("composition link must be an object")
            continue
        if link.get("composition_relation") not in COMPOSITION_RELATIONS - {"NONE"}:
            errors.append(f"{link.get('link_id')}: invalid composition relation")
        if link.get("membership_effect") != "NONE":
            errors.append(f"{link.get('link_id')}: composition membership_effect must be NONE")
        if link.get("identity_effect") not in {None, "NONE"}:
            errors.append(f"{link.get('link_id')}: composition cannot change identity")
    gates["COMPOSITION_NO_MEMBERSHIP_EFFECT_GATE"] = _gate(errors)

    failed = [name for name, gate in gates.items() if gate["status"] == "FAIL"]
    status = "PASS" if not failed else "HOLD"
    return {
        "schema_version": "1.7.0",
        "pipeline_status": status,
        "gates": gates,
        "failed_gates": failed,
        "runtime": {
            "PIPELINE_STATUS": status,
            "DOMAIN_FULL": "NOT_RUN",
            "FULL_LIBRARY": "NOT_RUN",
            "ACTIVE_PROMOTION": "NOT_RUN",
        },
    }


def validate_ontology_case(case: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate compact synthetic ontology cases."""
    errors: List[str] = []
    identity = case.get("identity_relation")
    composition = case.get("composition_relation", "NONE")
    if identity not in IDENTITY_RELATIONS:
        errors.append("invalid identity relation")
    if composition not in COMPOSITION_RELATIONS:
        errors.append("invalid composition relation")
    if case.get("family_status") == "HOLD" and case.get("positive_support") is True:
        errors.append("HOLD family cannot be positive support")
    if case.get("source_pair_ids_mixed") is True:
        errors.append("mixed source_pair_ids is prohibited")
    if _normalize(case.get("abstract_core")) in TRIVIAL_CORES:
        errors.append("trivial parent concept")
    if _normalize(case.get("state_variable_changed")) in VAGUE_STATE_VARIABLES:
        errors.append("state variable is too vague")
    if composition != "NONE":
        if case.get("membership_effect") != "NONE":
            errors.append("composition must not affect membership")
        if identity == "META_EQUIVALENT" and case.get("identity_basis") == "COMPOSITION":
            errors.append("composition cannot establish identity")
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

