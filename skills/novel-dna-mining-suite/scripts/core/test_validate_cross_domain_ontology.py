#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SCRIPT = Path(__file__).with_name("validate_cross_domain_ontology.py")
ORCHESTRATOR = ROOT / "skills" / "novel-dna-orchestrator" / "scripts" / "validate_cross_domain_ontology.py"
FIXTURE = ROOT / "tests" / "fixtures" / "cross_domain_ontology_qa_cases.json"


def load(path: Path):
    spec = importlib.util.spec_from_file_location("portable_ontology_validator", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


validator = load(SCRIPT)


class PortableOntologyRegression(unittest.TestCase):
    def test_six_ontology_cases(self):
        cases = json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"]
        self.assertEqual(6, len(cases))
        for case in cases:
            with self.subTest(case=case["case_id"]):
                self.assertEqual(case["expected_status"], validator.validate_ontology_case(case)["status"])

    def test_failure_locks_promotion(self):
        report = validator.validate_document({
            "families": [],
            "normalized_signatures": [],
            "pair_reviews": [],
            "ontology_concepts": [{
                "ontology_id": "ONTO:TRIVIAL",
                "status": "PASS",
                "concept_name": "Feedback",
                "abstract_core": "feedback loop",
                "one_sentence_core": "feedback loop",
                "required_invariants": {},
                "domain_realizations": [],
                "allowed_variations": [],
                "exclusion_boundary": [],
                "false_positive_tests": [],
                "positive_support_pair_ids": [],
                "negative_boundary_pair_ids": [],
                "structural_analogy_pair_ids": [],
                "composition_reference_pair_ids": [],
                "why_this_is_not_a_family_merge": "",
                "non_triviality_test": "",
                "confidence": "LOW",
            }],
            "composition_links": [],
        })
        self.assertEqual("HOLD", report["pipeline_status"])
        self.assertEqual("NOT_RUN", report["runtime"]["ACTIVE_PROMOTION"])

    def test_mirror_matches_orchestrator(self):
        self.assertEqual(SCRIPT.read_bytes(), ORCHESTRATOR.read_bytes())


if __name__ == "__main__":
    unittest.main()

