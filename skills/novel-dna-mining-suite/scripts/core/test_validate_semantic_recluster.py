#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = ROOT / "skills" / "novel-dna-mining-suite" / "scripts" / "core" / "validate_semantic_recluster.py"


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")


def build_valid_run(root: Path) -> None:
    qa = root / "qa"
    write_json(qa / "retrieval-recall-audit.json", {
        "status": "PASS",
        "candidate_generation_modes": ["lexical", "controlled_structural", "operation_structural"],
        "lexical_top_k": 8,
        "expanded_lexical_top_k": 16,
        "unresolved_missed_support_edges": [],
        "unexplained_uncovered_units": [],
    })
    write_json(qa / "cluster-global-coherence.json", {
        "status": "PASS",
        "unsupported_clusters": [],
    })
    write_json(qa / "linked-context-dedup-validation.json", {
        "status": "PASS",
        "conflicting_duplicate_identities": [],
        "post_dedup_duplicate_contexts": [],
    })
    write_json(qa / "lineage-namespace-validation.json", {
        "status": "PASS",
        "historical_member_count": 2,
        "migration_mapping_records": 2,
        "lineage_decisions_using_raw_id_intersection": 0,
        "direct_cross_namespace_id_intersections": 0,
        "unresolved_mapping_errors": [],
    })
    write_jsonl(root / "05_人物功能" / "candidate" / "nearest_neighbors.jsonl", [{
        "record_id": "NN:001",
        "decision": "SUBTYPE",
        "comparison_ids": ["U:A", "U:B"],
        "decision_audit": {
            "retrieval_score_used_for_decision": False,
            "keyword_count_used_for_decision": False,
            "structural_support_independent_of_keyword": True,
            "non_keyword_support_dimensions": ["protagonist_interface"],
        },
    }])
    write_jsonl(root / "05_人物功能" / "candidate" / "clusters.jsonl", [{
        "cluster_id": "CF:001",
        "member_unit_ids": ["U:A", "U:B"],
        "supporting_comparison_ids": ["NN:001"],
        "cluster_global_invariants": [{
            "name": "permissioned_validation_gateway",
            "non_generic": True,
            "generic_token_only": False,
            "structural_support_independent_of_keyword": True,
            "member_support": {
                "U:A": ["EV:A"],
                "U:B": ["EV:B"],
            },
        }],
    }])


class SemanticReclusterValidatorTests(unittest.TestCase):
    def run_validator(self, run: Path) -> tuple[int, dict]:
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), str(run)],
            text=True,
            encoding="utf-8",
            capture_output=True,
        )
        return completed.returncode, json.loads(completed.stdout)

    def test_valid_run_passes(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td) / "run"
            build_valid_run(run)
            code, result = self.run_validator(run)
            self.assertEqual(code, 0)
            self.assertEqual(result["status"], "PASS")

    def test_tiny_lexical_top2_fails_recall_gate(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td) / "run"
            build_valid_run(run)
            p = run / "qa" / "retrieval-recall-audit.json"
            data = json.loads(p.read_text(encoding="utf-8"))
            data["lexical_top_k"] = 2
            write_json(p, data)
            code, result = self.run_validator(run)
            self.assertNotEqual(code, 0)
            self.assertEqual(result["checks"]["RETRIEVAL_RECALL_AUDIT"]["status"], "FAIL")

    def test_keyword_only_support_edge_fails(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td) / "run"
            build_valid_run(run)
            p = run / "05_人物功能" / "candidate" / "nearest_neighbors.jsonl"
            row = json.loads(p.read_text(encoding="utf-8").strip())
            row["decision_audit"]["structural_support_independent_of_keyword"] = False
            write_jsonl(p, [row])
            code, result = self.run_validator(run)
            self.assertNotEqual(code, 0)
            self.assertEqual(result["checks"]["KEYWORD_ONLY_CLUSTER_DECISIONS"]["status"], "FAIL")

    def test_cluster_without_global_invariant_fails(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td) / "run"
            build_valid_run(run)
            p = run / "05_人物功能" / "candidate" / "clusters.jsonl"
            row = json.loads(p.read_text(encoding="utf-8").strip())
            row["cluster_global_invariants"] = []
            write_jsonl(p, [row])
            code, result = self.run_validator(run)
            self.assertNotEqual(code, 0)
            self.assertEqual(result["checks"]["CLUSTER_GLOBAL_COHERENCE_GATE"]["status"], "FAIL")

    def test_raw_cross_namespace_lineage_fails(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td) / "run"
            build_valid_run(run)
            p = run / "qa" / "lineage-namespace-validation.json"
            data = json.loads(p.read_text(encoding="utf-8"))
            data["lineage_decisions_using_raw_id_intersection"] = 1
            write_json(p, data)
            code, result = self.run_validator(run)
            self.assertNotEqual(code, 0)
            self.assertEqual(result["checks"]["LINEAGE_NAMESPACE_COMPATIBILITY_GATE"]["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
