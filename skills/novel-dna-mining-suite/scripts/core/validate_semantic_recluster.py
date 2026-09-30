#!/usr/bin/env python3
"""V1.6.4 semantic recluster reliability gate.

This validator independently checks the cross-book run artifacts that are easy to
fake accidentally in an ad-hoc recluster runner:
- retrieval recall is not limited to tiny lexical top-k;
- MERGE/SUBTYPE edges have non-keyword structural support;
- clusters have one global invariant supported by every member (no single-link bridge);
- lineage uses an explicit historical->fine-unit migration map rather than raw ID equality;
- linked context dedup is audited;
- hardcoded/keyword-only counters are computed from artifacts, not trusted as constants.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

SUPPORT_DECISIONS = {"MERGE", "SUBTYPE", "merge_candidate", "subtype_candidate"}
REQUIRED_RETRIEVAL_MODES = {"lexical", "controlled_structural", "operation_structural"}
GENERIC_INVARIANT_TOKENS = {
    "identity_bound",
    "replaceable",
    "non_replaceable",
    "same_schema",
    "same_type",
    "same_unit_type",
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not raw.strip():
            continue
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{lineno}: expected JSON object")
        rows.append(value)
    return rows


def jsonl_under(run_dir: Path, name: str) -> Iterable[Path]:
    yield from sorted(run_dir.rglob(name))


def gate(errors: list[str]) -> str:
    return "PASS" if not errors else "FAIL"


def normalize_decision(value: Any) -> str:
    return str(value or "").strip()


def invariant_is_non_generic(inv: dict[str, Any]) -> bool:
    if inv.get("non_generic") is not True:
        return False
    statement = json.dumps(inv, ensure_ascii=False).lower()
    if not statement.strip():
        return False
    tokens = {token for token in GENERIC_INVARIANT_TOKENS if token in statement}
    return inv.get("structural_support_independent_of_keyword") is True and (
        not tokens or inv.get("generic_token_only") is False
    )


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Validate V1.6.4 semantic recluster reliability gates.")
    parser.add_argument("run_dir", type=Path, help="Cross-book recluster run directory")
    parser.add_argument("--output", type=Path, help="Optional JSON result path")
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    qa = run_dir / "qa"

    file_errors: list[str] = []
    try:
        recall = load_json(qa / "retrieval-recall-audit.json")
    except Exception as exc:
        recall = {}
        file_errors.append(str(exc))
    try:
        coherence = load_json(qa / "cluster-global-coherence.json")
    except Exception as exc:
        coherence = {}
        file_errors.append(str(exc))
    try:
        lineage = load_json(qa / "lineage-namespace-validation.json")
    except Exception as exc:
        lineage = {}
        file_errors.append(str(exc))
    try:
        dedup = load_json(qa / "linked-context-dedup-validation.json")
    except Exception as exc:
        dedup = {}
        file_errors.append(str(exc))

    nearest: list[dict[str, Any]] = []
    clusters: list[dict[str, Any]] = []
    parse_errors: list[str] = []
    for path in jsonl_under(run_dir, "nearest_neighbors.jsonl"):
        try:
            nearest.extend(load_jsonl(path))
        except Exception as exc:
            parse_errors.append(str(exc))
    for path in jsonl_under(run_dir, "clusters.jsonl"):
        try:
            clusters.extend(load_jsonl(path))
        except Exception as exc:
            parse_errors.append(str(exc))

    recall_errors: list[str] = []
    modes = set(recall.get("candidate_generation_modes") or [])
    exhaustive = recall.get("all_compatible_pairs_exhaustive") is True
    lexical_k = recall.get("lexical_top_k")
    expanded_k = recall.get("expanded_lexical_top_k")
    if recall.get("status") != "PASS":
        recall_errors.append("retrieval recall audit status must be PASS")
    if not exhaustive:
        if not REQUIRED_RETRIEVAL_MODES.issubset(modes):
            recall_errors.append(
                f"candidate_generation_modes must include {sorted(REQUIRED_RETRIEVAL_MODES)}; got {sorted(modes)}"
            )
        if not isinstance(lexical_k, int) or lexical_k < 8:
            recall_errors.append("lexical_top_k must be >= 8 unless all compatible pairs are exhaustive")
        if not isinstance(expanded_k, int) or not isinstance(lexical_k, int) or expanded_k <= lexical_k:
            recall_errors.append("expanded_lexical_top_k must be greater than lexical_top_k")
    unresolved = recall.get("unresolved_missed_support_edges")
    if unresolved != []:
        recall_errors.append("unresolved_missed_support_edges must be an explicit empty list")
    unexplained = recall.get("unexplained_uncovered_units")
    if unexplained != []:
        recall_errors.append("unexplained_uncovered_units must be an explicit empty list")

    keyword_errors: list[str] = []
    accepted_edges: dict[str, dict[str, Any]] = {}
    for row in nearest:
        decision = normalize_decision(row.get("decision"))
        if decision not in SUPPORT_DECISIONS:
            continue
        rid = str(row.get("record_id") or "")
        if not rid:
            keyword_errors.append("support edge missing record_id")
            continue
        accepted_edges[rid] = row
        audit = row.get("decision_audit")
        if not isinstance(audit, dict):
            keyword_errors.append(f"{rid}: support edge missing decision_audit")
            continue
        if audit.get("retrieval_score_used_for_decision") is not False:
            keyword_errors.append(f"{rid}: retrieval score must not decide support")
        if audit.get("keyword_count_used_for_decision") is not False:
            keyword_errors.append(f"{rid}: keyword count must not decide support")
        if audit.get("structural_support_independent_of_keyword") is not True:
            keyword_errors.append(f"{rid}: structural_support_independent_of_keyword must be true")
        dims = audit.get("non_keyword_support_dimensions") or audit.get("structural_support_dimensions")
        if not isinstance(dims, list) or not dims:
            keyword_errors.append(f"{rid}: non-keyword structural support dimensions are required")

    cluster_errors: list[str] = []
    hardcoded_membership_violations: list[str] = []
    for row in clusters:
        cid = str(row.get("cluster_id") or row.get("record_id") or "<unknown-cluster>")
        members = row.get("member_unit_ids")
        if not isinstance(members, list) or len(members) < 2:
            cluster_errors.append(f"{cid}: member_unit_ids must contain at least 2 members")
            continue
        support_ids = row.get("supporting_comparison_ids")
        if not isinstance(support_ids, list) or not support_ids:
            cluster_errors.append(f"{cid}: supporting_comparison_ids required")
            support_ids = []
        support_edges = [accepted_edges.get(str(edge_id)) for edge_id in support_ids]
        if any(edge is None for edge in support_edges):
            missing = [str(edge_id) for edge_id, edge in zip(support_ids, support_edges) if edge is None]
            cluster_errors.append(f"{cid}: invalid/non-support comparison ids: {missing}")
        supported_members: set[str] = set()
        for edge in support_edges:
            if not edge:
                continue
            ids = edge.get("comparison_ids") or []
            supported_members.update(str(x) for x in ids)
        for member in map(str, members):
            if member not in supported_members:
                hardcoded_membership_violations.append(f"{cid}:{member}")

        invariants = row.get("cluster_global_invariants")
        if not isinstance(invariants, list) or not invariants:
            cluster_errors.append(f"{cid}: cluster_global_invariants required")
            continue
        viable = [inv for inv in invariants if isinstance(inv, dict) and invariant_is_non_generic(inv)]
        if not viable:
            cluster_errors.append(f"{cid}: no non-generic keyword-independent global invariant")
            continue
        member_set = set(map(str, members))
        invariant_covers_all = False
        for inv in viable:
            support = inv.get("member_support")
            if not isinstance(support, dict):
                continue
            if set(map(str, support.keys())) != member_set:
                continue
            if all(isinstance(refs, list) and len(refs) > 0 for refs in support.values()):
                invariant_covers_all = True
                break
        if not invariant_covers_all:
            cluster_errors.append(f"{cid}: no global invariant has evidence support from every member")

        if len(members) >= 3:
            bridge = row.get("bridge_chaining_audit")
            if not isinstance(bridge, dict) or bridge.get("status") != "PASS":
                cluster_errors.append(f"{cid}: 3+ member cluster requires bridge_chaining_audit PASS")
            elif bridge.get("unsupported_member_pairs") != []:
                cluster_errors.append(f"{cid}: unsupported_member_pairs must be []")
            if row.get("formation_basis") == "connected_component_only":
                cluster_errors.append(f"{cid}: connected_component_only formation is forbidden")

    if coherence.get("status") != "PASS":
        cluster_errors.append("cluster-global-coherence audit status must be PASS")
    if coherence.get("unsupported_clusters") not in ([], None):
        cluster_errors.append("cluster-global-coherence unsupported_clusters must be empty")

    dedup_errors: list[str] = []
    if dedup.get("status") != "PASS":
        dedup_errors.append("linked-context-dedup validation status must be PASS")
    if dedup.get("conflicting_duplicate_identities") not in ([], None):
        dedup_errors.append("conflicting_duplicate_identities must be empty")
    if dedup.get("post_dedup_duplicate_contexts") not in ([], None):
        dedup_errors.append("post_dedup_duplicate_contexts must be empty")

    lineage_errors: list[str] = []
    if lineage.get("status") != "PASS":
        lineage_errors.append("lineage namespace validation status must be PASS")
    if lineage.get("lineage_decisions_using_raw_id_intersection") not in (0, None):
        lineage_errors.append("lineage_decisions_using_raw_id_intersection must be 0")
    if lineage.get("direct_cross_namespace_id_intersections") not in (0, None):
        lineage_errors.append("direct_cross_namespace_id_intersections must be 0")
    historical = lineage.get("historical_member_count", 0)
    mappings = lineage.get("migration_mapping_records", 0)
    if isinstance(historical, int) and historical > 0:
        if not isinstance(mappings, int) or mappings <= 0:
            lineage_errors.append("historical lineage requires explicit migration_mapping_records > 0")
    if lineage.get("unresolved_mapping_errors") != []:
        lineage_errors.append("unresolved_mapping_errors must be an explicit empty list")

    result = {
        "gate": "SEMANTIC_RECLUSTER_RELIABILITY_V1_6_4",
        "status": "PASS"
        if not (file_errors or parse_errors or recall_errors or keyword_errors or cluster_errors or dedup_errors or lineage_errors or hardcoded_membership_violations)
        else "FAIL",
        "checks": {
            "ARTIFACT_PARSE": {"status": gate(file_errors + parse_errors), "errors": file_errors + parse_errors},
            "RETRIEVAL_RECALL_AUDIT": {"status": gate(recall_errors), "errors": recall_errors},
            "KEYWORD_ONLY_CLUSTER_DECISIONS": {
                "status": gate(keyword_errors),
                "count": len(keyword_errors),
                "violations": keyword_errors,
                "inspected_support_edges": len(accepted_edges),
                "method": "independent inspection of every MERGE/SUBTYPE decision_audit",
            },
            "HARDCODED_CLUSTER_MEMBERSHIP": {
                "status": gate(hardcoded_membership_violations),
                "count": len(hardcoded_membership_violations),
                "violations": hardcoded_membership_violations,
                "inspected_clusters": len(clusters),
                "method": "every member must be covered by an accepted support edge and a cluster-global invariant",
            },
            "CLUSTER_GLOBAL_COHERENCE_GATE": {"status": gate(cluster_errors), "errors": cluster_errors},
            "LINKED_CONTEXT_DEDUP_GATE": {"status": gate(dedup_errors), "errors": dedup_errors},
            "LINEAGE_NAMESPACE_COMPATIBILITY_GATE": {"status": gate(lineage_errors), "errors": lineage_errors},
        },
        "counts": {
            "nearest_neighbor_records": len(nearest),
            "accepted_support_edges": len(accepted_edges),
            "clusters": len(clusters),
        },
        "ok": False,
    }
    result["ok"] = result["status"] == "PASS"

    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        output = args.output if args.output.is_absolute() else run_dir / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
