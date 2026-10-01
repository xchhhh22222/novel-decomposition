#!/usr/bin/env python3
from __future__ import annotations

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

    def test_mirror_matches_orchestrator(self):
        self.assertEqual(SCRIPT.read_bytes(), ORCHESTRATOR.read_bytes())


if __name__ == "__main__":
    unittest.main()

