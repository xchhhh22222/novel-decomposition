#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "novel-dna-orchestrator" / "scripts" / "validate_mechanism_family_pipeline.py"
MIRROR = ROOT / "skills" / "novel-dna-mining-suite" / "scripts" / "core" / "validate_mechanism_family_pipeline.py"
FIXTURES = json.loads((ROOT / "tests" / "fixtures" / "mechanism_family_qa_cases.json").read_text(encoding="utf-8"))


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("mechanism_family_validator", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


validator = load_module(SCRIPT)


def card(number: int, lane: str = "relationship_engine", domain: str = "character_function"):
    return {
        "card_id": f"CARD-{number:03d}",
        "domain": domain,
        "comparison_lane": lane,
        "source_primary_object": {"book_id": f"BOOK-{(number % 4) + 1}", "record_id": f"REL-{number:03d}"},
        "trigger_or_input": "recognized evidence appears",
        "actor_or_operating_subject": "authorized evaluator",
        "core_operation_chain": ["inspect evidence", "update appraisal", "open conditional access"],
        "target_object": "access eligibility",
        "resulting_state": "eligible access",
        "feedback_or_growth_loop": "new access creates another evaluable task",
        "failure_or_stop_condition": "recognized evidence or evaluator authority disappears",
        "primary_evidence_refs": [f"BOOK-{(number % 4) + 1}:CHAPTER:{number:04d}"],
        "corroborating_evidence_refs": [],
        "unknown_classification": {"core_mechanism_unknowns": [], "peripheral_unknowns": []},
        "comparison_readiness": "READY",
        "derived_commentary": {"transferable_creation_value": "not semantic evidence"},
    }


def pair(number: int):
    categories = [
        ("OBVIOUS_SAME", "SAME_MECHANISM"),
        ("SAME_SURFACE_DIFFERENT_MECHANISM", "DIFFERENT"),
        ("PARAPHRASE_EQUIVALENT", "SAME_MECHANISM"),
        ("LIKELY_SUBTYPE", "SUBTYPE"),
        ("ANALOGOUS", "ANALOGOUS"),
        ("DIFFERENT", "DIFFERENT"),
        ("BOUNDARY_OR_HOLD", "HOLD"),
        ("OBVIOUS_SAME", "SAME_MECHANISM"),
        ("PARAPHRASE_EQUIVALENT", "SAME_MECHANISM"),
        ("ANALOGOUS", "ANALOGOUS"),
    ]
    category, decision = categories[number - 1]
    return {
        "pair_id": f"PAIR-{number:03d}",
        "left_card_id": f"CARD-{number * 2 - 1:03d}",
        "right_card_id": f"CARD-{number * 2:03d}",
        "decision": decision,
        "calibration_category": category,
        "mechanism_core_layer": "recognized evidence updates appraisal and conditionally opens access",
        "downstream_effect_layer": "different tasks become available",
        "transfer_dimension": "setting labels may vary",
        "reason": "the core causal chain is the same",
        "decision_basis": "MECHANISM_CORE",
        "selection_basis": "BOUNDARY_CALIBRATION",
        "support_provenance": {
            "keyword_hint_used_as_support": False,
            "linked_context_only_support": False,
            "derived_commentary_used_as_support": False,
        },
    }


def stage_history_for(phase: str):
    completed = [
        {"stage": "MECHANISM_CARD_EXTRACTION", "status": "PASS", "artifact_id": "cards-v1", "human_review": "NOT_REQUIRED"},
        {"stage": "READINESS_NORMALIZATION", "status": "PASS", "artifact_id": "readiness-v1", "human_review": "NOT_REQUIRED"},
        {"stage": "PAIR_CALIBRATION", "status": "PASS", "artifact_id": "pairs-v1", "human_review": "APPROVED"},
        {"stage": "FAMILY_PILOT", "status": "PASS", "artifact_id": "families-v1", "human_review": "APPROVED"},
        {"stage": "BOUNDARY_STRESS_TEST", "status": "PASS", "artifact_id": "stress-v1", "human_review": "APPROVED"},
        {"stage": "DOMAIN_EXPANSION", "status": "PASS", "artifact_id": "expansion-v1", "batch_id": "batch-001", "human_review": "APPROVED"},
        {"stage": "DOMAIN_FULL", "status": "PASS", "artifact_id": "domain-full-v1", "human_review": "APPROVED"},
    ]
    required = validator.MANDATORY_PREDECESSORS[phase]
    return [entry for entry in completed if entry["stage"] in required]


def valid_pair_document():
    categories = [
        "OBVIOUS_SAME",
        "PARAPHRASE_EQUIVALENT",
        "SAME_SURFACE_DIFFERENT_MECHANISM",
        "LIKELY_SUBTYPE",
        "ANALOGOUS",
        "DIFFERENT",
        "BOUNDARY_OR_HOLD",
    ]
    return {
        "phase": "PAIR_CALIBRATION",
        "next_state": "STOP_FOR_HUMAN_REVIEW",
        "stage_history": stage_history_for("PAIR_CALIBRATION"),
        "cards": [card(i) for i in range(1, 21)],
        "pairs": [pair(i) for i in range(1, 11)],
        "families": [],
        "run_controls": {"pair_coverage_categories": categories, "human_approvals": []},
    }


def family_record():
    return {
        "family_id": "RMF:CHARACTER_FUNCTION:abcdef12",
        "domain": "character_function",
        "family_status": "HYPOTHESIS",
        "family_name": "Evidence-appraisal access",
        "core_mechanism_definition": "recognized evidence causes an authorized appraisal update that conditionally opens access",
        "one_sentence_core": "recognized evidence updates appraisal and opens conditional access",
        "minimum_definition": {
            "trigger": "recognized evidence appears",
            "transformation": "authorized appraisal",
            "state_change": "access eligibility changes",
            "recurrence": "new access creates another evaluable task",
            "termination": "authority or evidence disappears",
        },
        "hard_invariants": ["recognized evidence", "authorized appraisal", "conditional access"],
        "allowed_variations": ["institution", "evidence type", "access type"],
        "exclusion_boundary": ["unconditional gift does not qualify"],
        "termination_condition": "authority or recognized evidence disappears",
        "why_it_recurs": "each admitted task creates evidence for a higher gate",
        "same_members": ["CARD-001", "CARD-002"],
        "subtype_members": ["CARD-003"],
        "analogous_references": ["CARD-004"],
        "hold_boundary_references": [],
        "false_positive_examples": ["a mentor gives resources without appraisal"],
        "member_definition_tests": [
            {"member_id": "CARD-001", "result": "PASS_SAME"},
            {"member_id": "CARD-002", "result": "PASS_SAME"},
            {"member_id": "CARD-003", "result": "PASS_SUBTYPE"},
            {"member_id": "CARD-004", "result": "OUTSIDE_ANALOGOUS"},
        ],
        "positive_support_pair_ids": ["PAIR-001"],
        "negative_boundary_pair_ids": ["PAIR-002"],
        "structural_analogy_pair_ids": [],
        "membership_basis": "INDIVIDUAL_DEFINITION_TEST",
        "single_link_chaining": False,
        "promotion_status": "NOT_RUN",
        "fingerprint_basis": "DOMAIN_CORE_INVARIANTS_SEMANTICS",
    }


class MechanismFamilyValidatorTests(unittest.TestCase):
    def test_all_required_gates_exist_and_valid_pair_calibration_passes(self):
        report = validator.validate_document(valid_pair_document())
        required = {
            "MECHANISM_CARD_SCHEMA_GATE",
            "CORE_VS_PERIPHERAL_UNKNOWN_GATE",
            "PRIMARY_EVIDENCE_ISOLATION_GATE",
            "PROJECTION_DUPLICATION_GATE",
            "STAGE_TRANSITION_GATE",
            "VALIDATED_SCOPE_GATE",
            "COMPARISON_LANE_ISOLATION_GATE",
            "PAIR_CALIBRATION_GATE",
            "MECHANISM_CORE_VS_DOWNSTREAM_GATE",
            "ANALOGOUS_MEMBERSHIP_ISOLATION_GATE",
            "FAMILY_MINIMUM_DEFINITION_GATE",
            "MEMBER_INDEPENDENT_DEFINITION_TEST_GATE",
            "CHAINING_PROHIBITION_GATE",
            "FAMILY_NEGATIVE_BOUNDARY_GATE",
            "FAMILY_PROVENANCE_INTEGRITY_GATE",
            "STABLE_FAMILY_GATE",
            "HOLD_FAMILY_PROMOTION_GATE",
            "PHASE_SCALE_GATE",
            "HUMAN_REVIEW_STOP_GATE",
            "LEGACY_CLUSTER_ISOLATION_GATE",
            "FAMILY_ID_NAMESPACE_GATE",
        }
        self.assertEqual("PASS", report["pipeline_status"], report)
        self.assertTrue(required.issubset(report["gates"]))

    def test_fixture_cases_cover_contract_boundaries(self):
        self.assertEqual(12, len(FIXTURES["cases"]))
        for case in FIXTURES["cases"]:
            with self.subTest(case=case["case_id"]):
                report = validator.validate_calibration_case(case)
                self.assertEqual(case["expected_status"], report["status"], report)

    def test_core_failure_locks_all_expansive_runtime_actions(self):
        document = valid_pair_document()
        document["cards"][0]["primary_evidence_refs"] = []
        document["cards"][0]["corroborating_evidence_refs"] = ["BOOK-1:CHAPTER:0001"]
        report = validator.validate_document(document)
        self.assertEqual("HOLD", report["pipeline_status"])
        self.assertEqual("NOT_RUN", report["runtime"]["DOMAIN_FULL"])
        self.assertEqual("NOT_RUN", report["runtime"]["FULL_LIBRARY"])
        self.assertEqual("NOT_RUN", report["runtime"]["ACTIVE_PROMOTION"])
        self.assertEqual("FAIL", report["gates"]["PRIMARY_EVIDENCE_ISOLATION_GATE"]["status"])

    def test_family_members_are_independently_tested_and_analogous_stays_outside(self):
        document = valid_pair_document()
        document["phase"] = "FAMILY_PILOT"
        document["stage_history"] = stage_history_for("FAMILY_PILOT")
        document["families"] = [family_record()]
        report = validator.validate_document(document)
        self.assertEqual("PASS", report["pipeline_status"], report)

        broken = copy.deepcopy(document)
        broken["families"][0]["same_members"].append("CARD-004")
        report = validator.validate_document(broken)
        self.assertEqual("FAIL", report["gates"]["ANALOGOUS_MEMBERSHIP_ISOLATION_GATE"]["status"])

    def test_single_link_chaining_cannot_admit_an_untested_member(self):
        document = valid_pair_document()
        document["phase"] = "FAMILY_PILOT"
        document["stage_history"] = stage_history_for("FAMILY_PILOT")
        document["families"] = [family_record()]
        document["families"][0]["same_members"].append("CARD-005")
        document["families"][0]["single_link_chaining"] = True
        report = validator.validate_document(document)
        self.assertEqual("FAIL", report["gates"]["CHAINING_PROHIBITION_GATE"]["status"])
        self.assertEqual("FAIL", report["gates"]["MEMBER_INDEPENDENT_DEFINITION_TEST_GATE"]["status"])

    def test_stable_family_requires_cross_book_same_or_three_part_subtype_pattern(self):
        document = valid_pair_document()
        document["phase"] = "BOUNDARY_STRESS_TEST"
        document["stage_history"] = stage_history_for("BOUNDARY_STRESS_TEST")
        family = family_record()
        family["family_status"] = "STABLE"
        family["stress_case_count"] = 5
        document["families"] = [family]
        report = validator.validate_document(document)
        self.assertEqual("PASS", report["gates"]["STABLE_FAMILY_GATE"]["status"], report)

        broken = copy.deepcopy(document)
        broken["pairs"][0]["decision"] = "SUBTYPE"
        report = validator.validate_document(broken)
        self.assertEqual("FAIL", report["gates"]["STABLE_FAMILY_GATE"]["status"])

    def test_pattern_b_requires_real_canonical_tests_and_two_tested_subtypes(self):
        document = valid_pair_document()
        document["phase"] = "BOUNDARY_STRESS_TEST"
        document["stage_history"] = stage_history_for("BOUNDARY_STRESS_TEST")
        family = family_record()
        family.update({
            "family_status": "STABLE",
            "same_members": ["CARD-001"],
            "subtype_members": ["CARD-003", "CARD-005"],
            "canonical_member_id": "CARD-001",
            "positive_support_pair_ids": [],
            "boundary_stress_passed": True,
            "stress_case_count": 5,
        })
        family["member_definition_tests"] = [
            {"member_id": "CARD-001", "result": "PASS_SAME"},
            {"member_id": "CARD-003", "result": "PASS_SUBTYPE"},
            {"member_id": "CARD-005", "result": "PASS_SUBTYPE"},
            {"member_id": "CARD-004", "result": "OUTSIDE_ANALOGOUS"},
        ]
        document["families"] = [family]
        report = validator.validate_document(document)
        self.assertEqual("PASS", report["gates"]["STABLE_FAMILY_GATE"]["status"], report)

        broken = copy.deepcopy(document)
        broken["families"][0]["member_definition_tests"] = broken["families"][0]["member_definition_tests"][1:]
        report = validator.validate_document(broken)
        self.assertEqual("FAIL", report["gates"]["STABLE_FAMILY_GATE"]["status"])

    def test_corroborating_projection_cannot_enter_comparison_pool(self):
        document = valid_pair_document()
        document["cards"][0]["projection_semantic_role"] = "CORROBORATING_VIEW"
        document["cards"][0]["comparison_pool_eligible"] = True
        report = validator.validate_document(document)
        self.assertEqual("FAIL", report["gates"]["PROJECTION_DUPLICATION_GATE"]["status"])

    def test_scale_and_human_stop_gates_block_unsafe_progression(self):
        document = valid_pair_document()
        document["pairs"] = document["pairs"][:9]
        document["next_state"] = "DOMAIN_FULL"
        document["run_controls"]["domain_full"] = True
        report = validator.validate_document(document)
        self.assertEqual("FAIL", report["gates"]["PHASE_SCALE_GATE"]["status"])
        self.assertEqual("FAIL", report["gates"]["HUMAN_REVIEW_STOP_GATE"]["status"])

    def test_domain_full_requires_expansion_and_explicit_approval(self):
        document = valid_pair_document()
        document["phase"] = "DOMAIN_FULL"
        document["next_state"] = "STOP_FOR_HUMAN_REVIEW"
        document["stage_history"] = stage_history_for("DOMAIN_FULL")[:-1]
        report = validator.validate_document(document)
        self.assertEqual("HOLD", report["pipeline_status"])
        self.assertEqual("FAIL", report["gates"]["PHASE_SCALE_GATE"]["status"])

    def test_direct_jump_to_family_pilot_without_pair_history_fails(self):
        document = valid_pair_document()
        document["phase"] = "FAMILY_PILOT"
        document["stage_history"] = stage_history_for("PAIR_CALIBRATION")
        report = validator.validate_document(document)
        self.assertEqual("FAIL", report["gates"]["STAGE_TRANSITION_GATE"]["status"])

    def test_fake_successful_expansion_count_cannot_replace_history(self):
        document = valid_pair_document()
        document["phase"] = "DOMAIN_FULL"
        document["stage_history"] = stage_history_for("DOMAIN_EXPANSION")
        document["run_controls"]["successful_expansion_count"] = 99
        document["run_controls"]["human_approvals"] = ["APPROVE_DOMAIN_FULL"]
        report = validator.validate_document(document)
        self.assertEqual("FAIL", report["gates"]["STAGE_TRANSITION_GATE"]["status"])

    def test_unvalidated_gf_ability_cannot_enter_expansion(self):
        document = {
            "phase": "DOMAIN_EXPANSION",
            "next_state": "STOP_FOR_HUMAN_REVIEW",
            "stage_history": stage_history_for("DOMAIN_EXPANSION"),
            "cards": [card(i, "GF_ABILITY", "golden_finger") for i in range(1, 26)],
            "pairs": [],
            "families": [],
            "run_controls": {"expansion_batch_size": 25, "human_approvals": []},
        }
        report = validator.validate_document(document)
        self.assertEqual("FAIL", report["gates"]["VALIDATED_SCOPE_GATE"]["status"])

        document["run_controls"]["human_approvals"] = ["APPROVE_LANE_VALIDATION:golden_finger:GF_ABILITY"]
        report = validator.validate_document(document)
        self.assertEqual("PASS", report["pipeline_status"], report)

    def test_family_cannot_borrow_unrelated_same_pair(self):
        document = valid_pair_document()
        document["phase"] = "FAMILY_PILOT"
        document["stage_history"] = stage_history_for("FAMILY_PILOT")
        family = family_record()
        family["positive_support_pair_ids"] = ["PAIR-003"]
        document["families"] = [family]
        report = validator.validate_document(document)
        self.assertEqual("FAIL", report["gates"]["FAMILY_PROVENANCE_INTEGRITY_GATE"]["status"])

    def test_nonexistent_negative_boundary_pair_fails(self):
        document = valid_pair_document()
        document["phase"] = "FAMILY_PILOT"
        document["stage_history"] = stage_history_for("FAMILY_PILOT")
        family = family_record()
        family["negative_boundary_pair_ids"] = ["PAIR-DOES-NOT-EXIST"]
        document["families"] = [family]
        report = validator.validate_document(document)
        self.assertEqual("FAIL", report["gates"]["FAMILY_PROVENANCE_INTEGRITY_GATE"]["status"])

    def test_control_summary_cannot_fake_pair_coverage(self):
        document = valid_pair_document()
        for calibration_pair in document["pairs"]:
            calibration_pair["calibration_category"] = "OBVIOUS_SAME"
            calibration_pair["decision"] = "SAME_MECHANISM"
        report = validator.validate_document(document)
        self.assertEqual("FAIL", report["gates"]["PAIR_CALIBRATION_GATE"]["status"])

    def test_validator_mirror_is_byte_identical(self):
        self.assertEqual(SCRIPT.read_bytes(), MIRROR.read_bytes())


if __name__ == "__main__":
    unittest.main()

