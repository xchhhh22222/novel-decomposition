#!/usr/bin/env python3
"""Research workflow tests that do not need network or private repo checkout."""
import argparse
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from emotion_first_workflow_v1 import (assert_sparse, check_conditions, digest, finalize, prepare, prompt)


def brief():
    return {"schema_version": "sparse_emotion_brief_v1", "brief_id": "T:01", "input_mode": "SPARSE_EMOTION_BRIEF", "status": "candidate", "genre": ["玄幻", "高武"], "core_reader_expectation": "保护家人", "emotion_contour": ["DOWN", "DOWN", "UP"], "required_emotion_weaves": ["家庭", "成长", "关系", "势力"], "longform_requirement": "保留旧弧合同"}


def retrieval():
    return {"line_matches": [{"record_id": "EL:01"}], "weave_matches": [{"record_id": "EW:01"}], "macro_matches": [{"record_id": "MA:01"}], "handoff_matches": [{"record_id": "AH:01"}]}


class WorkflowTests(unittest.TestCase):
    def test_sparse_brief_rejects_story_prefill(self):
        x = brief()
        x["monster"] = "妖魔"
        with self.assertRaisesRegex(ValueError, "forbidden"):
            assert_sparse(x)

    def test_scope_is_honest(self):
        x = brief(); x["emotion_contour"] = ["UP", "DOWN"]
        with self.assertRaisesRegex(ValueError, "Phase 1"):
            assert_sparse(x)

    def test_baseline_prompt_has_no_emotion_retrieval(self):
        a = prompt("LEGACY_BASELINE", brief(), None)
        b = prompt("E2_E3_ENABLED", brief(), retrieval())
        self.assertNotIn("EL:01", a)
        self.assertIn("EL:01", b)

    def test_paid_requires_witness_before_transition(self):
        opt = {"mode": "E2_E3_ENABLED", "story_nodes": [{"node_id": "N1"}, {"node_id": "N2"}], "macro_arcs": [{"macro_id": "M1", "state_transitions": [{"node_id": "N1", "to": "PAID"}], "required_settlement_conditions": [{"condition_id": "formal_right", "description": "资格生效", "witness_node_id": "N2"}]}]}
        self.assertIn("occurs after PAID", "; ".join(check_conditions(opt)))
        opt["macro_arcs"][0]["state_transitions"][0]["node_id"] = "N2"
        self.assertEqual([], check_conditions(opt))

    def test_empty_settlement_cannot_be_paid(self):
        opt = {"mode": "E2_E3_ENABLED", "story_nodes": [{"node_id": "N1"}], "macro_arcs": [{"macro_id": "M", "state_transitions": [{"node_id": "N1", "to": "PAID"}]}]}
        self.assertIn("without explicit settlement", str(check_conditions(opt)))

    def test_prepare_freezes_and_requires_fresh_workspace(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "brief.json").write_text(json.dumps(brief(), ensure_ascii=False), encoding="utf-8")
            fake = types.ModuleType("search_emotion_arc_library")
            fake.search_library = lambda library, request: retrieval()
            args = argparse.Namespace(brief=root / "brief.json", emotion_library=root / "data", workspace=root / "session")
            with patch.dict(sys.modules, {"search_emotion_arc_library": fake}):
                prepare(args)
            state = json.loads((root / "session" / "session.json").read_text())
            self.assertEqual(digest(brief()), state["brief_hash"])
            self.assertEqual("WAITING_FOR_MODEL", state["phase"])
            with patch.dict(sys.modules, {"search_emotion_arc_library": fake}):
                with self.assertRaisesRegex(ValueError, "not empty"):
                    prepare(args)

    def test_finalize_rejects_unretrieved_id_before_bridge(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            p.joinpath("brief.json").write_text(json.dumps(brief(), ensure_ascii=False), encoding="utf-8")
            p.joinpath("emotion-retrieval.json").write_text(json.dumps(retrieval(), ensure_ascii=False), encoding="utf-8")
            p.joinpath("session.json").write_text(json.dumps({"schema_version": "nova_emotion_first_workflow_v1", "phase": "WAITING_FOR_MODEL", "brief_hash": digest(brief()), "retrieval_hash": digest(retrieval())}), encoding="utf-8")
            for mode, path in [("LEGACY_BASELINE", "legacy.json"), ("E2_E3_ENABLED", "enhanced.json")]:
                options = [{"pair_id": f"P{i}", "mode": mode, "emotion_source_uses": [{"record_kind": "line", "record_id": "EL:FAKE"}]} for i in range(2)]
                val = {"schema_version": "emotion_story_composer_fragment_v1", "brief_id": "T:01", "mode": mode, "status": "candidate", "semantic_composer": {"kind": "MODEL_AUTHORED_RESEARCH_CANDIDATE"}, "material_profiles": {}, "options": options}
                p.joinpath(path).write_text(json.dumps(val), encoding="utf-8")
            args = argparse.Namespace(workspace=p, legacy=p / "legacy.json", enhanced=p / "enhanced.json", material_snapshot_repo=p, material_snapshot_commit="dummy", material_package_subdir="dummy")
            with self.assertRaisesRegex(ValueError, "absent from frozen retrieval"):
                finalize(args)


if __name__ == "__main__":
    unittest.main()
