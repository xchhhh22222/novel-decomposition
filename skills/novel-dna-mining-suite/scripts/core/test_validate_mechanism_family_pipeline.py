#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SCRIPT = Path(__file__).with_name("validate_mechanism_family_pipeline.py")
ORCHESTRATOR = ROOT / "skills" / "novel-dna-orchestrator" / "scripts" / "validate_mechanism_family_pipeline.py"
FIXTURE = ROOT / "tests" / "fixtures" / "mechanism_family_qa_cases.json"


def load(path: Path):
    spec = importlib.util.spec_from_file_location("portable_mechanism_validator", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


validator = load(SCRIPT)


class PortableMechanismFamilyRegression(unittest.TestCase):
    def test_twelve_calibration_cases(self):
        cases = json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"]
        self.assertEqual(12, len(cases))
        for case in cases:
            with self.subTest(case=case["case_id"]):
                self.assertEqual(case["expected_status"], validator.validate_calibration_case(case)["status"])

    def test_core_failure_is_not_warning_only(self):
        report = validator.validate_document({
            "phase": "PAIR_CALIBRATION",
            "next_state": "DOMAIN_FULL",
            "cards": [],
            "pairs": [],
            "families": [],
            "run_controls": {"domain_full": True, "pair_coverage_categories": []},
        })
        self.assertEqual("HOLD", report["pipeline_status"])
        self.assertEqual("NOT_RUN", report["runtime"]["DOMAIN_FULL"])
        self.assertEqual("NOT_RUN", report["runtime"]["FULL_LIBRARY"])
        self.assertEqual("NOT_RUN", report["runtime"]["ACTIVE_PROMOTION"])

    def test_stage_scope_rejects_stable_family_during_pair_calibration(self):
        document = {
            "phase": "PAIR_CALIBRATION",
            "next_state": "STOP_FOR_HUMAN_REVIEW",
            "stage_history": [],
            "cards": [],
            "pairs": [],
            "families": [{"family_id": "RMF:TEST:abcdef12", "family_status": "STABLE"}],
            "run_controls": {"pair_coverage_categories": []},
        }
        report = validator.validate_document(document)
        self.assertEqual("FAIL", report["gates"]["STAGE_ARTIFACT_SCOPE_GATE"]["status"])

    def test_validation_binding_detects_mutated_document(self):
        document = {
            "run_id": "PORTABLE-BINDING-TEST",
            "phase": "PAIR_CALIBRATION",
            "next_state": "STOP_FOR_HUMAN_REVIEW",
            "stage_history": [],
            "cards": [],
            "pairs": [],
            "families": [],
            "run_controls": {"pair_coverage_categories": []},
        }
        accepted = validator.validate_document(document)
        mutated = copy.deepcopy(document)
        mutated["run_id"] = "PORTABLE-BINDING-TEST-MUTATED"
        report = validator.validate_document(mutated, expected_validation_report=accepted)
        self.assertEqual("FAIL", report["gates"]["VALIDATION_BINDING_GATE"]["status"])

    def test_mirror_matches_orchestrator(self):
        self.assertEqual(SCRIPT.read_bytes(), ORCHESTRATOR.read_bytes())


if __name__ == "__main__":
    unittest.main()

