#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "novel-dna-orchestrator" / "scripts" / "validate_cross_domain_ontology.py"
MIRROR = ROOT / "skills" / "novel-dna-mining-suite" / "scripts" / "core" / "validate_cross_domain_ontology.py"
FIXTURES = json.loads((ROOT / "tests" / "fixtures" / "cross_domain_ontology_qa_cases.json").read_text(encoding="utf-8"))


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("ontology_validator", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


validator = load_module(SCRIPT)


def valid_document():
    family_a = {
        "family_id": "RMF:CHARACTER_FUNCTION:aaaabbbb",
        "domain": "character_function",
        "family_status": "STABLE",
        "members": ["CF-1", "CF-2"],
    }
    family_b = {
        "family_id": "RMF:PLOTLINE:ccccdddd",
        "domain": "plotline",
        "family_status": "STABLE",
        "members": ["PL-1", "PL-2"],
    }
    signatures = [
        {
            "family_id": family_a["family_id"],
            "domain": "character_function",
            "trigger_semantics": "recognized evidence is presented to an authorized gatekeeper",
            "transformation_semantics": "the gatekeeper updates a warranted appraisal",
            "state_variable_changed": "access eligibility",
            "feedback_or_recurrence": "new access creates a higher evidence gate",
            "validity_basis": "recognized evidence plus authority",
            "termination_condition": "authority or recognized evidence disappears",
            "hard_invariants": ["authorized appraisal", "conditional access"],
            "exclusion_boundary": ["unconditional help"],
        },
        {
            "family_id": family_b["family_id"],
            "domain": "plotline",
            "trigger_semantics": "verified evidence resolves the current uncertainty",
            "transformation_semantics": "verified evidence updates the actionable model",
            "state_variable_changed": "actionable knowledge",
            "feedback_or_recurrence": "the updated model exposes another unresolved target",
            "validity_basis": "verified evidence and contradiction checks",
            "termination_condition": "the target uncertainty is resolved",
            "hard_invariants": ["verification", "next unresolved target"],
            "exclusion_boundary": ["single lookup with no next entry"],
        },
    ]
    pairs = [
        {
            "pair_id": "ONTO-PAIR-1",
            "left_family_id": family_a["family_id"],
            "right_family_id": family_b["family_id"],
            "identity_relation": "META_SPECIALIZATION_CANDIDATE",
            "composition_relation": "NONE",
            "identity_inferred_from_composition": False,
            "composition_inferred_from_identity": False,
        },
        {
            "pair_id": "ONTO-PAIR-2",
            "left_family_id": family_a["family_id"],
            "right_family_id": family_b["family_id"],
            "identity_relation": "DISTINCT",
            "composition_relation": "NONE",
            "identity_inferred_from_composition": False,
            "composition_inferred_from_identity": False,
        },
    ]
    concept = {
        "ontology_id": "ONTO:CONDITIONAL_STATE_UPDATE:001",
        "status": "PASS",
        "concept_name": "Warranted conditional state update",
        "abstract_core": "recognized evidence authorizes a warranted update to a bounded decision state and exposes the next unresolved gate",
        "one_sentence_core": "validated evidence changes a specific decision state under a validity rule and creates another bounded gate",
        "required_invariants": {
            "trigger": "recognized evidence",
            "transformation": "warranted update under an explicit validity basis",
            "state_change": "access eligibility or actionable knowledge changes",
            "feedback": "the changed state exposes another bounded gate",
            "termination": "the governing uncertainty or authority ends",
        },
        "domain_realizations": [family_a["family_id"], family_b["family_id"]],
        "allowed_variations": ["domain", "evidence type", "state-variable specialization"],
        "exclusion_boundary": ["unconditional grants", "unverified guesses"],
        "false_positive_tests": ["same word verification but no warranted state update"],
        "positive_support_pair_ids": ["ONTO-PAIR-1"],
        "negative_boundary_pair_ids": ["ONTO-PAIR-2"],
        "structural_analogy_pair_ids": [],
        "composition_reference_pair_ids": [],
        "why_this_is_not_a_family_merge": "domain family definitions and memberships remain unchanged",
        "non_triviality_test": "excludes updates without recognized evidence, validity basis, recurrence, or bounded termination",
        "confidence": "MEDIUM",
    }
    return {
        "families": [family_a, family_b],
        "normalized_signatures": signatures,
        "pair_reviews": pairs,
        "ontology_concepts": [concept],
        "composition_links": [],
        "family_membership_before": {
            family_a["family_id"]: list(family_a["members"]),
            family_b["family_id"]: list(family_b["members"]),
        },
        "family_membership_after": {
            family_a["family_id"]: list(family_a["members"]),
            family_b["family_id"]: list(family_b["members"]),
        },
    }


class CrossDomainOntologyValidatorTests(unittest.TestCase):
    def test_valid_document_passes_all_required_gates(self):
        report = validator.validate_document(valid_document())
        required = {
            "STABLE_FAMILY_INPUT_ONLY_GATE",
            "CROSS_DOMAIN_PAIR_GATE",
            "NORMALIZED_SIGNATURE_GATE",
            "IDENTITY_COMPOSITION_SEPARATION_GATE",
            "NONTRIVIAL_PARENT_GATE",
            "STATE_VARIABLE_SEMANTICS_GATE",
            "POSITIVE_NEGATIVE_PROVENANCE_GATE",
            "ONTOLOGY_POSITIVE_SUPPORT_GATE",
            "DOMAIN_REALIZATION_GATE",
            "ONTOLOGY_PROVENANCE_INTEGRITY_GATE",
            "STRUCTURAL_ANALOGY_ISOLATION_GATE",
            "HOLD_ONTOLOGY_ISOLATION_GATE",
            "FAMILY_MEMBERSHIP_IMMUTABILITY_GATE",
            "COMPOSITION_NO_MEMBERSHIP_EFFECT_GATE",
            "COMPOSITION_LINK_INTEGRITY_GATE",
        }
        self.assertEqual("PASS", report["pipeline_status"], report)
        self.assertTrue(required.issubset(report["gates"]))

    def test_fixture_cases_cover_ontology_boundaries(self):
        self.assertEqual(6, len(FIXTURES["cases"]))
        for case in FIXTURES["cases"]:
            with self.subTest(case=case["case_id"]):
                report = validator.validate_ontology_case(case)
                self.assertEqual(case["expected_status"], report["status"], report)

    def test_hold_family_cannot_be_positive_support(self):
        document = valid_document()
        document["families"][0]["family_status"] = "HOLD"
        report = validator.validate_document(document)
        self.assertEqual("FAIL", report["gates"]["STABLE_FAMILY_INPUT_ONLY_GATE"]["status"])
        self.assertEqual("FAIL", report["gates"]["HOLD_ONTOLOGY_ISOLATION_GATE"]["status"])

    def test_identity_and_composition_are_independent(self):
        document = valid_document()
        document["pair_reviews"][0]["composition_relation"] = "LEFT_CAN_FEED_RIGHT"
        document["pair_reviews"][0]["identity_inferred_from_composition"] = True
        report = validator.validate_document(document)
        self.assertEqual("FAIL", report["gates"]["IDENTITY_COMPOSITION_SEPARATION_GATE"]["status"])

    def test_trivial_parent_and_vague_state_are_rejected(self):
        document = valid_document()
        document["ontology_concepts"][0]["abstract_core"] = "feedback loop"
        document["normalized_signatures"][0]["state_variable_changed"] = "state"
        report = validator.validate_document(document)
        self.assertEqual("FAIL", report["gates"]["NONTRIVIAL_PARENT_GATE"]["status"])
        self.assertEqual("FAIL", report["gates"]["STATE_VARIABLE_SEMANTICS_GATE"]["status"])

    def test_mixed_provenance_and_structural_analogy_support_are_rejected(self):
        document = valid_document()
        concept = document["ontology_concepts"][0]
        concept["source_pair_ids"] = ["ONTO-PAIR-1", "ONTO-PAIR-2"]
        document["pair_reviews"][0]["identity_relation"] = "STRUCTURAL_ANALOGY"
        report = validator.validate_document(document)
        self.assertEqual("FAIL", report["gates"]["POSITIVE_NEGATIVE_PROVENANCE_GATE"]["status"])
        self.assertEqual("FAIL", report["gates"]["STRUCTURAL_ANALOGY_ISOLATION_GATE"]["status"])

    def test_composition_never_changes_membership(self):
        document = valid_document()
        document["composition_links"] = [
            {
                "link_id": "COMP-1",
                "composition_relation": "LEFT_CAN_FEED_RIGHT",
                "membership_effect": "ADD_RIGHT_TO_LEFT_FAMILY",
                "identity_effect": "NONE",
            }
        ]
        document["family_membership_after"][document["families"][0]["family_id"]].append("PL-1")
        report = validator.validate_document(document)
        self.assertEqual("FAIL", report["gates"]["COMPOSITION_NO_MEMBERSHIP_EFFECT_GATE"]["status"])
        self.assertEqual("FAIL", report["gates"]["FAMILY_MEMBERSHIP_IMMUTABILITY_GATE"]["status"])
        self.assertEqual("NOT_RUN", report["runtime"]["ACTIVE_PROMOTION"])

    def test_same_domain_ontology_pair_fails(self):
        document = valid_document()
        document["families"][1]["domain"] = "character_function"
        document["normalized_signatures"][1]["domain"] = "character_function"
        report = validator.validate_document(document)
        self.assertEqual("FAIL", report["gates"]["CROSS_DOMAIN_PAIR_GATE"]["status"])

    def test_distinct_and_hold_pairs_cannot_be_positive_support(self):
        for relation in ("DISTINCT", "HOLD"):
            with self.subTest(relation=relation):
                document = valid_document()
                document["pair_reviews"][0]["identity_relation"] = relation
                report = validator.validate_document(document)
                self.assertEqual("FAIL", report["gates"]["ONTOLOGY_POSITIVE_SUPPORT_GATE"]["status"])

    def test_pass_ontology_requires_two_distinct_domains(self):
        document = valid_document()
        document["families"][1]["domain"] = "character_function"
        document["normalized_signatures"][1]["domain"] = "character_function"
        report = validator.validate_document(document)
        self.assertEqual("FAIL", report["gates"]["DOMAIN_REALIZATION_GATE"]["status"])

    def test_positive_support_families_must_appear_in_realizations(self):
        document = valid_document()
        third_family = {
            "family_id": "RMF:GF_CORE:eeeeffff",
            "domain": "golden_finger",
            "family_status": "STABLE",
            "members": ["GF-1", "GF-2"],
        }
        third_signature = {
            "family_id": third_family["family_id"],
            "domain": "golden_finger",
            "trigger_semantics": "bounded resource becomes available",
            "transformation_semantics": "the resource is converted under a fixed rule",
            "state_variable_changed": "growth capacity",
            "feedback_or_recurrence": "growth enables access to another resource tier",
            "validity_basis": "resource balance and conversion rule",
            "termination_condition": "resource or conversion authority ends",
            "hard_invariants": ["bounded input", "rule-governed conversion"],
            "exclusion_boundary": ["unbounded free growth"],
        }
        document["families"].append(third_family)
        document["normalized_signatures"].append(third_signature)
        document["ontology_concepts"][0]["domain_realizations"] = [
            document["families"][0]["family_id"],
            third_family["family_id"],
        ]
        document["family_membership_before"][third_family["family_id"]] = list(third_family["members"])
        document["family_membership_after"][third_family["family_id"]] = list(third_family["members"])
        report = validator.validate_document(document)
        self.assertEqual("FAIL", report["gates"]["ONTOLOGY_POSITIVE_SUPPORT_GATE"]["status"])
        self.assertEqual("FAIL", report["gates"]["DOMAIN_REALIZATION_GATE"]["status"])

    def test_empty_shell_composition_link_fails(self):
        document = valid_document()
        document["composition_links"] = [{}]
        report = validator.validate_document(document)
        self.assertEqual("FAIL", report["gates"]["COMPOSITION_LINK_INTEGRITY_GATE"]["status"])

    def test_membership_snapshots_are_required_when_ontology_exists(self):
        document = valid_document()
        document.pop("family_membership_before")
        document.pop("family_membership_after")
        report = validator.validate_document(document)
        self.assertEqual("FAIL", report["gates"]["FAMILY_MEMBERSHIP_IMMUTABILITY_GATE"]["status"])

        document = valid_document()
        document["family_membership_before"] = {}
        document["family_membership_after"] = {}
        report = validator.validate_document(document)
        self.assertEqual("FAIL", report["gates"]["FAMILY_MEMBERSHIP_IMMUTABILITY_GATE"]["status"])

    def test_all_ontology_provenance_ids_must_exist_and_match_roles(self):
        document = valid_document()
        concept = document["ontology_concepts"][0]
        concept["structural_analogy_pair_ids"] = ["ONTO-PAIR-2"]
        concept["composition_reference_pair_ids"] = ["MISSING-COMPOSITION-PAIR"]
        report = validator.validate_document(document)
        self.assertEqual("FAIL", report["gates"]["ONTOLOGY_PROVENANCE_INTEGRITY_GATE"]["status"])

    def test_validator_mirror_is_byte_identical(self):
        self.assertEqual(SCRIPT.read_bytes(), MIRROR.read_bytes())


if __name__ == "__main__":
    unittest.main()

