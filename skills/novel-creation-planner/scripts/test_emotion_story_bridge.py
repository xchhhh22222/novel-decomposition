#!/usr/bin/env python3
"""Regression tests for the sparse Emotion-to-Story Bridge pilot fixture."""

from __future__ import annotations

import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
FIXTURE = REPO_ROOT / "research" / "emotion-arc-v2" / "fixtures" / "sparse-family-protection"
RUNTIME = FIXTURE / "runtime-output"
sys.path.insert(0, str(SCRIPT_DIR))

from run_emotion_story_bridge_pilot import validate_sparse_brief  # noqa: E402
from validate_emotion_story_bridge import validate_output  # noqa: E402


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class EmotionStoryBridgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "runtime-output"
        shutil.copytree(RUNTIME, self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def codes(self) -> set[str]:
        return {item["code"] for item in validate_output(self.root)["errors"]}

    def mutate_enhanced(self, callback) -> None:
        path = self.root / "enhanced-options.json"
        payload = read(path)
        callback(payload)
        write(path, payload)

    def test_real_fixture_passes_structural_gate(self) -> None:
        report = validate_output(self.root)
        self.assertTrue(report["ok"], report["errors"])
        self.assertEqual("PENDING_INDEPENDENT_REVIEW", report["creative_quality"])

    def test_premature_reader_knowledge_fails(self) -> None:
        def change(payload: dict) -> None:
            transition = payload["options"][0]["emotion_lines"][0]["state_transitions"][0]
            transition["reader_knowledge_added"] = ["尚未由该节点揭示的幕后结论"]

        self.mutate_enhanced(change)
        self.assertIn("PREMATURE_READER_KNOWLEDGE", self.codes())

    def test_new_arc_cannot_cancel_old_contract(self) -> None:
        self.mutate_enhanced(
            lambda payload: payload["options"][0]["handoff"].__setitem__(
                "old_arc_contract_retained", "新弧启动，因此旧弧无需兑现"
            )
        )
        self.assertIn("OLD_ARC_CONTRACT_CANCELLED", self.codes())

    def test_unretrieved_emotion_record_fails(self) -> None:
        self.mutate_enhanced(
            lambda payload: payload["options"][0]["emotion_source_uses"][0].__setitem__(
                "record_id", "EL:BOOK_001:FAKE"
            )
        )
        self.assertIn("EMOTION_SOURCE_NOT_RETRIEVED", self.codes())

    def test_options_cannot_be_name_only_variants(self) -> None:
        def change(payload: dict) -> None:
            payload["options"][1]["causal_signature"] = copy.deepcopy(
                payload["options"][0]["causal_signature"]
            )

        self.mutate_enhanced(change)
        self.assertIn("OPTIONS_ONLY_RENAMED", self.codes())

    def test_blanket_material_attachment_fails(self) -> None:
        def change(payload: dict) -> None:
            option = payload["options"][0]
            uses = []
            for slot in option["material_slots"]:
                selected = slot.get("selected_ref")
                if selected:
                    uses.append({
                        "slot_id": slot["slot_id"],
                        "material_ref": selected["material_id"],
                        "role_at_node": "无差别挂载",
                        "effect_on_action": "无差别挂载",
                    })
            for node in option["story_nodes"]:
                node["material_uses"] = copy.deepcopy(uses)

        self.mutate_enhanced(change)
        self.assertIn("BLANKET_MATERIAL_ATTACHMENT", self.codes())

    def test_sparse_brief_rejects_prefilled_story(self) -> None:
        brief = read(FIXTURE / "sparse-brief.json")
        brief["monster"] = "预先写死的妖魔"
        with self.assertRaisesRegex(ValueError, "non-brief story fields"):
            validate_sparse_brief(brief)

    def test_fixture_retains_real_rejection_and_original_gap(self) -> None:
        enhanced = read(self.root / "enhanced-options.json")["options"]
        rejected = [
            item
            for option in enhanced
            for slot in option["material_slots"]
            for item in slot.get("rejected_refs", [])
        ]
        self.assertTrue(any(item.get("source_record_id") == "GF:BOOK_005" for item in rejected))
        original = [
            slot
            for option in enhanced
            for slot in option["material_slots"]
            if slot.get("decision") == "ORIGINAL_DESIGN"
        ]
        self.assertTrue(any(slot.get("module") == "cultivation_system" and slot.get("gap_reason") for slot in original))


if __name__ == "__main__":
    unittest.main(verbosity=2)
