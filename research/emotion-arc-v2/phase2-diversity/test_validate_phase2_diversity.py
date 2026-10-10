#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from validate_phase2_diversity import validate


PHASE1 = HERE.parent / "runs" / "emotion-first-phase1-real-20261010" / "attempts" / "attempt-01" / "result" / "enhanced-options.json"


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text(encoding="utf-8"))


class Phase2DiversityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.research = load("phase2-diversity-research.json")
        self.longform = load("longform-pressure-test.json")
        self.material = load("phase2-material-retrieval.json")
        self.review = load("literary-quality-review.json")
        self.phase1 = json.loads(PHASE1.read_text(encoding="utf-8"))
        self.phase1_hash = hashlib.sha256(PHASE1.read_bytes()).hexdigest()

    def run_gate(self):
        return validate(
            self.research,
            self.longform,
            self.material,
            self.review,
            self.phase1,
            self.phase1_hash,
        )

    def test_real_phase2_artifacts_pass_structural_gate(self):
        self.assertTrue(self.run_gate()["ok"])

    def test_duplicate_causal_engine_fails(self):
        self.research["handoff_candidates"][1]["causal_engine_family"] = self.research["handoff_candidates"][0]["causal_engine_family"]
        self.assertFalse(self.run_gate()["ok"])

    def test_new_arc_cannot_cancel_phase1_b(self):
        self.research["handoff_candidates"][0]["retained_phase1_b_obligation"]["cancellation"] = True
        self.assertFalse(self.run_gate()["ok"])

    def test_ah001_cannot_be_verified_handoff(self):
        self.research["emotion_evidence_policy"]["handoff_reference_status"] = "VERIFIED_HANDOFF"
        self.assertFalse(self.run_gate()["ok"])

    def test_every_line_needs_counterfactual_effect(self):
        self.research["handoff_candidates"][0]["counterfactual_tests"].pop()
        self.assertFalse(self.run_gate()["ok"])

    def test_longform_window_needs_choice(self):
        self.longform["chapters_51_100_windows"][2]["character_choice"] = ""
        self.assertFalse(self.run_gate()["ok"])

    def test_phase2_macro_cannot_claim_full_paid(self):
        self.research["handoff_candidates"][0]["proposed_ma_b"]["state_transitions"][-1]["to"] = "PAID"
        self.assertFalse(self.run_gate()["ok"])

    def test_material_source_must_resolve_with_hash(self):
        self.material["queries"][0]["selected_ref"]["source_line_sha256"] = ""
        self.assertFalse(self.run_gate()["ok"])

    def test_creative_quality_cannot_auto_pass(self):
        self.review["overall"]["creative_quality"] = "PASS"
        self.assertFalse(self.run_gate()["ok"])

    def test_comparison_material_ids_must_match_retrieval(self):
        self.research["planner_path_comparison"]["paths"][0]["material_selected_ids"][0] = "FAKE:SOURCE"
        self.assertFalse(self.run_gate()["ok"])

    def test_frozen_ma_a_contract_cannot_change(self):
        self.research["handoff_candidates"][0]["frozen_ma_a"]["settlement_contract"] = "lowered contract"
        self.assertFalse(self.run_gate()["ok"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
