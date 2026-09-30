#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
VALIDATOR = ROOT / "skills" / "novel-dna-mining-suite" / "scripts" / "core" / "validate_semantic_recluster.py"


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")


def support_review(result: str = "SUBTYPE") -> dict:
    return {
        "reviewed": True,
        "method": "evidence_grounded_structured_paraphrase",
        "adjudication_source": "primary_object_semantic_review",
        "keyword_hint_used_as_support": False,
        "linked_context_only_support": False,
        "raw_text_equality_required": False,
        "signature_fields_compared": [
            "actor_or_role",
            "trigger_or_input",
            "operation_chain",
            "target_or_object",
            "output_or_effect",
            "constraints_or_boundary",
        ],
        "shared_mechanism_invariants": ["authority_holder -> verify -> grant_access"],
        "critical_conflicts": [],
        "semantic_differences": ["surface wording differs"],
        "result": result,
        "evidence_refs": {"left": ["EV:A"], "right": ["EV:B"]},
    }


def build_valid_run(root: Path) -> None:
    qa = root / "qa"
    write_json(qa / "retrieval-recall-audit.json", {
        "status": "PASS",
        "candidate_generation_modes": ["lexical", "controlled_structural", "operation_structural", "mechanism_signature_hint"],
        "lexical_top_k": 8,
        "expanded_lexical_top_k": 16,
        "unresolved_missed_support_edges": [],
        "unexplained_uncovered_units": [],
    })
    write_json(qa / "mechanism-signature-provenance.json", {
        "status": "PASS",
        "accepted_support_edge_count": 1,
        "primary_object_supported_edge_count": 1,
        "keyword_hints_used_for_support": [],
        "linked_context_only_support_edges": [],
        "method": "keyword/lexicon atoms retrieve only; accepted support is bilateral primary-object evidence",
    })
    write_json(qa / "semantic-false-negative-audit.json", {
        "status": "PASS",
        "exact_raw_text_equality_required": False,
        "paraphrase_equivalence_supported": True,
        "suspicious_rejected_pair_count": 0,
        "reviewed_suspicious_rejected_pairs": 0,
        "potential_equivalent_rejections": [],
        "unresolved_false_negative_pairs": [],
        "method": "review every suspicious rejected pair using structured operation signatures",
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
        "historical_member_count": 1,
        "migration_mapping_records": 1,
        "resolved_mapping_records": 1,
        "resolved_fine_unit_link_count": 2,
        "one_to_many_mapping_supported": True,
        "candidate_multiplicity_is_not_resolution_blocker": True,
        "unresolved_due_to_multiple_candidates_count": 0,
        "lineage_decisions_using_raw_id_intersection": 0,
        "direct_cross_namespace_id_intersections": 0,
        "unresolved_mapping_errors": [],
    })
    write_jsonl(root / "10_总索引" / "historical-member-migration-map.jsonl", [{
        "record_id": "MIG:001",
        "historical_member_id": "OLD:BOOK_001",
        "candidate_fine_units": [
            {"unit_id": "U:A", "resolution_basis": ["book_scoped_evidence_overlap", "mechanism_signature_correspondence"]},
            {"unit_id": "U:B", "resolution_basis": ["source_internal_identity"]},
        ],
        "resolved_fine_unit_ids": ["U:A", "U:B"],
        "migration_status": "RESOLVED",
        "resolution_basis": ["book_id", "source_path", "evidence_overlap", "mechanism_signature_hint"],
        "candidate_multiplicity_blocked_resolution": False,
    }])
    write_jsonl(root / "05_人物功能" / "candidate" / "nearest_neighbors.jsonl", [{
        "record_id": "NN:001",
        "decision": "SUBTYPE",
        "comparison_ids": ["U:A", "U:B"],
        "candidate_retrieval": {
            "method": "lexical+controlled_structural+operation_structural",
        },
        "comparison_dimensions": {
            "protagonist_interface": {"relation": "partial_semantic_operation"},
        },
        "decision_audit": {
            "retrieval_score_used_for_decision": False,
            "keyword_count_used_for_decision": False,
            "structural_support_independent_of_keyword": True,
            "non_keyword_support_dimensions": ["protagonist_interface"],
            "raw_operation_text_equality_required": False,
            "exact_raw_text_match_used_as_required_condition": False,
            "support_provenance": {
                "keyword_hint_used_as_support": False,
                "linked_context_only_support": False,
                "semantic_adjudication_method": "evidence_grounded_primary_object_paraphrase",
                "primary_unit_support": {
                    "left": ["U:A#primary.actual_operation", "EV:A"],
                    "right": ["U:B#primary.actual_operation", "EV:B"],
                },
                "corroborating_linked_context": {"left": [], "right": []},
            },
            "paraphrase_equivalence_review": support_review(),
        },
    }])
    write_jsonl(root / "05_人物功能" / "candidate" / "equivalent_pairs.jsonl", [{
        "comparison_id": "NN:001",
        "unit_ids": ["U:A", "U:B"],
        "decision": "SUBTYPE",
        "shared_mechanism_signature": {
            "operation_chain": ["verify", "grant_access"],
            "target_or_object": "protagonist operational access",
            "output_or_effect": "permission/resource gateway",
        },
        "shared_mechanism_invariants": ["authority_holder -> verify -> grant_access"],
        "variation_boundary": {
            "left": "official task permission",
            "right": "vanguard team permission",
        },
        "evidence_refs": {"left": ["EV:A"], "right": ["EV:B"]},
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

    def test_keyword_hint_cannot_supply_support(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td) / "run"
            build_valid_run(run)
            p = run / "05_人物功能" / "candidate" / "nearest_neighbors.jsonl"
            row = json.loads(p.read_text(encoding="utf-8").strip())
            row["decision_audit"]["support_provenance"]["keyword_hint_used_as_support"] = True
            write_jsonl(p, [row])
            code, result = self.run_validator(run)
            self.assertNotEqual(code, 0)
            self.assertEqual(result["checks"]["SEMANTIC_PARAPHRASE_EQUIVALENCE_GATE"]["status"], "FAIL")

    def test_linked_context_only_support_fails(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td) / "run"
            build_valid_run(run)
            p = run / "05_人物功能" / "candidate" / "nearest_neighbors.jsonl"
            row = json.loads(p.read_text(encoding="utf-8").strip())
            row["decision_audit"]["support_provenance"]["linked_context_only_support"] = True
            write_jsonl(p, [row])
            code, result = self.run_validator(run)
            self.assertNotEqual(code, 0)
            self.assertEqual(result["checks"]["LINKED_CONTEXT_SUPPORT_ISOLATION_GATE"]["status"], "FAIL")

    def test_provenance_artifact_must_match_support_count(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td) / "run"
            build_valid_run(run)
            p = run / "qa" / "mechanism-signature-provenance.json"
            data = json.loads(p.read_text(encoding="utf-8"))
            data["primary_object_supported_edge_count"] = 0
            write_json(p, data)
            code, result = self.run_validator(run)
            self.assertNotEqual(code, 0)
            self.assertEqual(result["checks"]["MECHANISM_SIGNATURE_PROVENANCE_GATE"]["status"], "FAIL")

    def test_raw_text_equality_requirement_fails(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td) / "run"
            build_valid_run(run)
            p = run / "05_人物功能" / "candidate" / "nearest_neighbors.jsonl"
            row = json.loads(p.read_text(encoding="utf-8").strip())
            row["decision_audit"]["raw_operation_text_equality_required"] = True
            row["decision_audit"]["paraphrase_equivalence_review"]["raw_text_equality_required"] = True
            write_jsonl(p, [row])
            code, result = self.run_validator(run)
            self.assertNotEqual(code, 0)
            self.assertEqual(result["checks"]["SEMANTIC_PARAPHRASE_EQUIVALENCE_GATE"]["status"], "FAIL")

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

    def test_suspicious_keep_separate_requires_paraphrase_review(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td) / "run"
            build_valid_run(run)
            p = run / "05_人物功能" / "candidate" / "nearest_neighbors.jsonl"
            support = json.loads(p.read_text(encoding="utf-8").strip())
            rejected = {
                "record_id": "NN:002",
                "decision": "KEEP_SEPARATE",
                "comparison_ids": ["U:C", "U:D"],
                "candidate_retrieval": {"method": "operation_structural"},
                "comparison_dimensions": {"operation": {"relation": "partial_semantic_operation"}},
                "decision_audit": {
                    "retrieval_score_used_for_decision": False,
                    "keyword_count_used_for_decision": False,
                    "raw_operation_text_equality_required": False,
                },
            }
            write_jsonl(p, [support, rejected])
            q = run / "qa" / "semantic-false-negative-audit.json"
            audit = json.loads(q.read_text(encoding="utf-8"))
            audit["suspicious_rejected_pair_count"] = 1
            audit["reviewed_suspicious_rejected_pairs"] = 0
            write_json(q, audit)
            code, result = self.run_validator(run)
            self.assertNotEqual(code, 0)
            self.assertEqual(result["checks"]["SEMANTIC_FALSE_NEGATIVE_AUDIT"]["status"], "FAIL")

    def test_equivalent_review_cannot_remain_keep_separate(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td) / "run"
            build_valid_run(run)
            p = run / "05_人物功能" / "candidate" / "nearest_neighbors.jsonl"
            support = json.loads(p.read_text(encoding="utf-8").strip())
            rejected = {
                "record_id": "NN:002",
                "decision": "KEEP_SEPARATE",
                "comparison_ids": ["U:C", "U:D"],
                "candidate_retrieval": {"method": "operation_structural"},
                "comparison_dimensions": {"operation": {"relation": "partial_semantic_operation"}},
                "decision_audit": {
                    "retrieval_score_used_for_decision": False,
                    "keyword_count_used_for_decision": False,
                    "raw_operation_text_equality_required": False,
                    "exact_raw_text_match_used_as_required_condition": False,
                    "paraphrase_equivalence_review": support_review("EQUIVALENT"),
                },
            }
            write_jsonl(p, [support, rejected])
            q = run / "qa" / "semantic-false-negative-audit.json"
            audit = json.loads(q.read_text(encoding="utf-8"))
            audit["suspicious_rejected_pair_count"] = 1
            audit["reviewed_suspicious_rejected_pairs"] = 1
            write_json(q, audit)
            code, result = self.run_validator(run)
            self.assertNotEqual(code, 0)
            self.assertEqual(result["checks"]["SEMANTIC_FALSE_NEGATIVE_AUDIT"]["status"], "FAIL")

    def test_lineage_source_record_plus_evidence_alone_is_not_enough(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td) / "run"
            build_valid_run(run)
            p = run / "10_总索引" / "historical-member-migration-map.jsonl"
            row = json.loads(p.read_text(encoding="utf-8").strip())
            row["candidate_fine_units"][0]["resolution_basis"] = ["source_record_id", "book_scoped_evidence_overlap"]
            write_jsonl(p, [row])
            code, result = self.run_validator(run)
            self.assertNotEqual(code, 0)
            self.assertEqual(result["checks"]["LINEAGE_NAMESPACE_COMPATIBILITY_GATE"]["status"], "FAIL")

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

    def test_candidate_multiplicity_cannot_block_lineage_resolution(self):
        with tempfile.TemporaryDirectory() as td:
            run = Path(td) / "run"
            build_valid_run(run)
            p = run / "qa" / "lineage-namespace-validation.json"
            data = json.loads(p.read_text(encoding="utf-8"))
            data["candidate_multiplicity_is_not_resolution_blocker"] = False
            data["unresolved_due_to_multiple_candidates_count"] = 1
            write_json(p, data)
            code, result = self.run_validator(run)
            self.assertNotEqual(code, 0)
            self.assertEqual(result["checks"]["LINEAGE_NAMESPACE_COMPATIBILITY_GATE"]["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
