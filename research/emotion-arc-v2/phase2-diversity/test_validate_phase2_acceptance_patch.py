#!/usr/bin/env python3

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PHASE1 = REPO / "research/emotion-arc-v2/runs/emotion-first-phase1-real-20261010/attempts/attempt-01/result/enhanced-options.json"
AUDIT = HERE / "phase2-minimal-acceptance-audit.json"
LONGFORM = HERE / "longform-pressure-test.json"

SPEC = importlib.util.spec_from_file_location(
    "validate_phase2_acceptance_patch", HERE / "validate_phase2_acceptance_patch.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def read(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class Phase2AcceptancePatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = read(AUDIT)
        cls.longform = read(LONGFORM)
        cls.phase1 = read(PHASE1)

    def validate(self, audit=None, longform=None):
        return MODULE.validate(
            audit if audit is not None else copy.deepcopy(self.audit),
            longform if longform is not None else copy.deepcopy(self.longform),
            copy.deepcopy(self.phase1),
        )[0]

    def test_real_artifacts_pass(self):
        self.assertEqual([], self.validate())

    def test_es4_choice_cannot_leak_into_first_ten(self):
        longform = copy.deepcopy(self.longform)
        longform["chapters_1_10_high_precision"][2]["character_choice"] = "妹妹以灌溉记录重排试种"
        self.assertTrue(any("ES4 choice leaked" in item for item in self.validate(longform=longform)))

    def test_salt_seal_arc_cannot_be_absorbed(self):
        audit = copy.deepcopy(self.audit)
        ledger = next(item for item in audit["parallel_macro_commitment_ledger"] if item["macro_id"] == "ES:MACRO:B")
        ledger["absorbed_by"] = "P2:ES:MACRO:B:COMMONS"
        self.assertTrue(any("cannot be absorbed" in item for item in self.validate(audit=audit)))

    def test_planned_state_cannot_claim_observed_story(self):
        audit = copy.deepcopy(self.audit)
        audit["parallel_macro_commitment_ledger"][2]["last_actual_story_node"] = "chapter 100"
        self.assertTrue(any("falsely claims" in item for item in self.validate(audit=audit)))

    def test_salt_seal_unpaid_expectation_cannot_disappear(self):
        audit = copy.deepcopy(self.audit)
        ledger = next(item for item in audit["parallel_macro_commitment_ledger"] if item["macro_id"] == "ES:MACRO:B")
        ledger["unpaid_reader_expectations"] = ["异常盐封的可核验来源"]
        self.assertTrue(any("lost unpaid expectation" in item for item in self.validate(audit=audit)))

    def test_timeline_discrepancy_cannot_be_silently_removed(self):
        audit = copy.deepcopy(self.audit)
        audit["timeline_consistency"]["choice_position_audit"].pop()
        self.assertTrue(any("TL-001 through TL-008" in item for item in self.validate(audit=audit)))

    def test_paid_ma_a_cannot_be_reopened(self):
        audit = copy.deepcopy(self.audit)
        ledger = next(item for item in audit["parallel_macro_commitment_ledger"] if item["macro_id"] == "ES:MACRO:A")
        ledger["current_state"] = "ACTIVE"
        ledger["unpaid_reader_expectations"] = ["重新证明冬粮安全"]
        self.assertTrue(any("must remain PAID" in item for item in self.validate(audit=audit)))


if __name__ == "__main__":
    unittest.main()
