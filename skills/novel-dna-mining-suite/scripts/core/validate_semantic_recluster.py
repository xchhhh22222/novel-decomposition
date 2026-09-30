#!/usr/bin/env python3
"""V1.6.5 semantic recluster reliability gate.

This validator independently checks the cross-book run artifacts for:
- multi-route retrieval recall;
- non-keyword, non-retrieval-score support;
- paraphrase-equivalence adjudication that never requires raw operation text equality;
- false-negative review for structurally/semantically suspicious KEEP_SEPARATE pairs;
- cluster-global coherence without single-link bridge chaining;
- linked-context dedup;
- explicit lineage namespace migration with one-to-many resolution support;
- non-hardcoded QA counts.

Machine PASS means the run is structurally auditable. It does not replace human
semantic review and never authorizes active promotion.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

SUPPORT_DECISIONS = {"MERGE", "SUBTYPE", "merge_candidate", "subtype_candidate"}
KEEP_SEPARATE_DECISIONS = {"KEEP_SEPARATE", "keep_separate"}
HOLD_DECISIONS = {"HOLD", "hold"}
REQUIRED_RETRIEVAL_MODES = {"lexical", "controlled_structural", "operation_structural", "mechanism_signature"}
PARAPHRASE_RESULTS_SUPPORT = {"EQUIVALENT", "SUBTYPE", "MERGE", "MECHANISM_EQUIVALENT"}
PARAPHRASE_RESULTS_REJECT = {"NOT_EQUIVALENT", "DIFFERENT"}
PARAPHRASE_RESULTS_HOLD = {"HOLD", "UNRESOLVED"}
MIN_SIGNATURE_FIELDS = {"operation_chain", "target_or_object", "output_or_effect"}
SUSPICIOUS_RELATIONS = {
    "same_semantic_operation",
    "partial_semantic_operation",
    "same_structure",
    "partial",
}
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


def retrieval_modes(row: dict[str, Any]) -> set[str]:
    candidate = row.get("candidate_retrieval")
    modes: set[str] = set()
    if isinstance(candidate, dict):
        method = str(candidate.get("method") or "")
        modes.update(part for part in method.split("+") if part)
        values = candidate.get("candidate_generation_modes")
        if isinstance(values, list):
            modes.update(str(value) for value in values)
    return modes


def suspicious_for_paraphrase_review(row: dict[str, Any]) -> bool:
    modes = retrieval_modes(row)
    if modes.intersection({"controlled_structural", "operation_structural"}):
        return True
    dimensions = row.get("comparison_dimensions")
    if not isinstance(dimensions, dict):
        return False
    for detail in dimensions.values():
        if isinstance(detail, dict) and detail.get("relation") in SUSPICIOUS_RELATIONS:
            return True
    return False


def paraphrase_review(row: dict[str, Any]) -> dict[str, Any] | None:
    audit = row.get("decision_audit")
    if not isinstance(audit, dict):
        return None
    review = audit.get("paraphrase_equivalence_review")
    return review if isinstance(review, dict) else None


def validate_paraphrase_review(
    rid: str,
    decision: str,
    row: dict[str, Any],
    *,
    require_review: bool,
) -> list[str]:
    errors: list[str] = []
    audit = row.get("decision_audit")
    if not isinstance(audit, dict):
        return [f"{rid}: decision_audit missing"]
    if audit.get("raw_operation_text_equality_required") is not False:
        errors.append(f"{rid}: raw_operation_text_equality_required must be false")
    if audit.get("exact_raw_text_match_used_as_required_condition") not in (False, None):
        errors.append(f"{rid}: exact raw-text match must not be a required condition")
    review = paraphrase_review(row)
    if not require_review and review is None:
        return errors
    if review is None:
        errors.append(f"{rid}: paraphrase_equivalence_review required")
        return errors
    if review.get("reviewed") is not True:
        errors.append(f"{rid}: paraphrase_equivalence_review.reviewed must be true")
    if review.get("raw_text_equality_required") is not False:
        errors.append(f"{rid}: paraphrase review must state raw_text_equality_required=false")
    if review.get("method") not in {
        "structured_operation_signature",
        "evidence_grounded_structured_paraphrase",
        "canonical_mechanism_signature",
    }:
        errors.append(f"{rid}: unsupported paraphrase review method")
    fields = review.get("signature_fields_compared")
    if not isinstance(fields, list) or not MIN_SIGNATURE_FIELDS.issubset(set(map(str, fields))):
        errors.append(
            f"{rid}: signature_fields_compared must include {sorted(MIN_SIGNATURE_FIELDS)}"
        )
    result = str(review.get("result") or "")
    evidence = review.get("evidence_refs")
    if not isinstance(evidence, dict) or not all(
        isinstance(evidence.get(side), list) and evidence.get(side)
        for side in ("left", "right")
    ):
        errors.append(f"{rid}: paraphrase review needs left/right evidence_refs")
    shared = review.get("shared_mechanism_invariants")
    conflicts = review.get("critical_conflicts")
    differences = review.get("semantic_differences")
    if result in PARAPHRASE_RESULTS_SUPPORT:
        if decision not in SUPPORT_DECISIONS:
            errors.append(f"{rid}: paraphrase result {result} cannot remain decision={decision}")
        if not isinstance(shared, list) or not shared:
            errors.append(f"{rid}: supported paraphrase equivalence requires shared_mechanism_invariants")
    elif result in PARAPHRASE_RESULTS_REJECT:
        if decision not in KEEP_SEPARATE_DECISIONS:
            errors.append(f"{rid}: paraphrase rejection {result} must map to KEEP_SEPARATE")
        has_boundary = isinstance(conflicts, list) and bool(conflicts)
        has_difference = isinstance(differences, list) and bool(differences)
        if not (has_boundary or has_difference):
            errors.append(f"{rid}: NOT_EQUIVALENT requires a concrete conflict or semantic difference")
    elif result in PARAPHRASE_RESULTS_HOLD:
        if decision not in HOLD_DECISIONS:
            errors.append(f"{rid}: unresolved paraphrase review must map to HOLD")
    else:
        errors.append(f"{rid}: invalid paraphrase review result={result!r}")
    return errors


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Validate V1.6.5 semantic recluster reliability gates.")
    parser.add_argument("run_dir", type=Path, help="Cross-book recluster run directory")
    parser.add_argument("--output", type=Path, help="Optional JSON result path")
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    qa = run_dir / "qa"

    file_errors: list[str] = []
    artifacts: dict[str, dict[str, Any]] = {}
    for key, filename in (
        ("recall", "retrieval-recall-audit.json"),
        ("coherence", "cluster-global-coherence.json"),
        ("lineage", "lineage-namespace-validation.json"),
        ("dedup", "linked-context-dedup-validation.json"),
        ("false_negative", "semantic-false-negative-audit.json"),
    ):
        try:
            artifacts[key] = load_json(qa / filename)
        except Exception as exc:
            artifacts[key] = {}
            file_errors.append(str(exc))

    recall = artifacts["recall"]
    coherence = artifacts["coherence"]
    lineage = artifacts["lineage"]
    dedup = artifacts["dedup"]
    false_negative = artifacts["false_negative"]

    nearest: list[dict[str, Any]] = []
    clusters: list[dict[str, Any]] = []
    migration_rows: list[dict[str, Any]] = []
    equivalent_pairs: list[dict[str, Any]] = []
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
    for path in jsonl_under(run_dir, "historical-member-migration-map.jsonl"):
        try:
            migration_rows.extend(load_jsonl(path))
        except Exception as exc:
            parse_errors.append(str(exc))
    for path in jsonl_under(run_dir, "equivalent_pairs.jsonl"):
        try:
            equivalent_pairs.extend(load_jsonl(path))
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
    if recall.get("unresolved_missed_support_edges") != []:
        recall_errors.append("unresolved_missed_support_edges must be an explicit empty list")
    if recall.get("unexplained_uncovered_units") != []:
        recall_errors.append("unexplained_uncovered_units must be an explicit empty list")

    keyword_errors: list[str] = []
    paraphrase_errors: list[str] = []
    false_negative_errors: list[str] = []
    accepted_edges: dict[str, dict[str, Any]] = {}
    suspicious_rejected = 0
    reviewed_suspicious_rejected = 0
    for index, row in enumerate(nearest, 1):
        decision = normalize_decision(row.get("decision"))
        rid = str(row.get("record_id") or f"<nn-{index}>")
        is_support = decision in SUPPORT_DECISIONS
        suspicious = suspicious_for_paraphrase_review(row)

        if is_support:
            accepted_edges[rid] = row
            audit = row.get("decision_audit")
            if not isinstance(audit, dict):
                keyword_errors.append(f"{rid}: support edge missing decision_audit")
            else:
                if audit.get("retrieval_score_used_for_decision") is not False:
                    keyword_errors.append(f"{rid}: retrieval score must not decide support")
                if audit.get("keyword_count_used_for_decision") is not False:
                    keyword_errors.append(f"{rid}: keyword count must not decide support")
                if audit.get("structural_support_independent_of_keyword") is not True:
                    keyword_errors.append(f"{rid}: structural_support_independent_of_keyword must be true")
                dims = audit.get("non_keyword_support_dimensions") or audit.get("structural_support_dimensions")
                if not isinstance(dims, list) or not dims:
                    keyword_errors.append(f"{rid}: non-keyword structural support dimensions are required")
            paraphrase_errors.extend(validate_paraphrase_review(rid, decision, row, require_review=True))
        elif decision in KEEP_SEPARATE_DECISIONS and suspicious:
            suspicious_rejected += 1
            review = paraphrase_review(row)
            if review is not None and review.get("reviewed") is True:
                reviewed_suspicious_rejected += 1
            false_negative_errors.extend(validate_paraphrase_review(rid, decision, row, require_review=True))
        elif decision in HOLD_DECISIONS and suspicious:
            false_negative_errors.extend(validate_paraphrase_review(rid, decision, row, require_review=True))

    audit_exact_requirement = false_negative.get("exact_raw_text_equality_required")
    if audit_exact_requirement is not False:
        false_negative_errors.append("semantic-false-negative audit must state exact_raw_text_equality_required=false")
    if false_negative.get("paraphrase_equivalence_supported") is not True:
        false_negative_errors.append("semantic-false-negative audit must state paraphrase_equivalence_supported=true")
    if false_negative.get("status") != "PASS":
        false_negative_errors.append("semantic-false-negative audit status must be PASS")
    if false_negative.get("unresolved_false_negative_pairs") != []:
        false_negative_errors.append("unresolved_false_negative_pairs must be an explicit empty list")
    if false_negative.get("potential_equivalent_rejections") != []:
        false_negative_errors.append("potential_equivalent_rejections must be an explicit empty list")
    audited_count = false_negative.get("reviewed_suspicious_rejected_pairs")
    if audited_count != reviewed_suspicious_rejected:
        false_negative_errors.append(
            f"reviewed_suspicious_rejected_pairs mismatch: artifact={audited_count}, actual={reviewed_suspicious_rejected}"
        )
    candidate_count = false_negative.get("suspicious_rejected_pair_count")
    if candidate_count != suspicious_rejected:
        false_negative_errors.append(
            f"suspicious_rejected_pair_count mismatch: artifact={candidate_count}, actual={suspicious_rejected}"
        )

    equivalent_pair_errors: list[str] = []
    if accepted_edges:
        equivalent_by_comparison = {
            str(row.get("comparison_id") or row.get("supporting_comparison_id") or ""): row
            for row in equivalent_pairs
        }
        for rid in accepted_edges:
            if rid not in equivalent_by_comparison:
                equivalent_pair_errors.append(f"{rid}: accepted support edge missing from equivalent_pairs.jsonl")
        for rid, row in equivalent_by_comparison.items():
            if rid not in accepted_edges:
                equivalent_pair_errors.append(f"{rid}: equivalent_pairs entry does not reference an accepted support edge")
                continue
            if not isinstance(row.get("shared_mechanism_signature"), dict):
                equivalent_pair_errors.append(f"{rid}: equivalent pair missing shared_mechanism_signature")
            if not isinstance(row.get("variation_boundary"), dict):
                equivalent_pair_errors.append(f"{rid}: equivalent pair missing variation_boundary")
            evidence = row.get("evidence_refs")
            if not isinstance(evidence, dict) or not all(
                isinstance(evidence.get(side), list) and evidence.get(side)
                for side in ("left", "right")
            ):
                equivalent_pair_errors.append(f"{rid}: equivalent pair requires left/right evidence_refs")

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
            if edge:
                supported_members.update(str(x) for x in edge.get("comparison_ids") or [])
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
            if all(isinstance(refs, list) and refs for refs in support.values()):
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
    if lineage.get("one_to_many_mapping_supported") is not True:
        lineage_errors.append("lineage must support one-to-many historical-member -> fine-unit mapping")
    if lineage.get("candidate_multiplicity_is_not_resolution_blocker") is not True:
        lineage_errors.append("candidate multiplicity must not be a lineage resolution blocker")
    if lineage.get("unresolved_due_to_multiple_candidates_count") not in (0, None):
        lineage_errors.append("unresolved_due_to_multiple_candidates_count must be 0")
    historical = lineage.get("historical_member_count", 0)
    mappings = lineage.get("migration_mapping_records", 0)
    if isinstance(historical, int) and historical > 0 and (not isinstance(mappings, int) or mappings <= 0):
        lineage_errors.append("historical lineage requires explicit migration_mapping_records > 0")
    if lineage.get("unresolved_mapping_errors") != []:
        lineage_errors.append("unresolved_mapping_errors must be an explicit empty list")

    migration_index = {
        str(row.get("record_id") or f"<migration-{i}>"): row
        for i, row in enumerate(migration_rows, 1)
    }
    for rid, row in migration_index.items():
        candidates = row.get("candidate_fine_units")
        resolved = row.get("resolved_fine_unit_ids")
        status = str(row.get("migration_status") or "")
        if not isinstance(candidates, list):
            lineage_errors.append(f"{rid}: candidate_fine_units must be a list")
            continue
        if not isinstance(resolved, list):
            lineage_errors.append(f"{rid}: resolved_fine_unit_ids must be a list")
            continue
        candidate_ids = {
            str(item.get("unit_id"))
            for item in candidates
            if isinstance(item, dict) and item.get("unit_id")
        }
        if any(str(unit_id) not in candidate_ids for unit_id in resolved):
            lineage_errors.append(f"{rid}: resolved_fine_unit_ids must be drawn from candidate_fine_units")
        if status == "RESOLVED":
            if not resolved:
                lineage_errors.append(f"{rid}: RESOLVED migration requires at least one fine unit")
            basis = row.get("resolution_basis")
            if not isinstance(basis, list) or not basis:
                lineage_errors.append(f"{rid}: RESOLVED migration requires resolution_basis")
        if len(candidates) > 1 and row.get("candidate_multiplicity_blocked_resolution") is True:
            lineage_errors.append(f"{rid}: multiple candidates may not block resolution by themselves")

    all_errors = (
        file_errors
        + parse_errors
        + recall_errors
        + keyword_errors
        + paraphrase_errors
        + false_negative_errors
        + equivalent_pair_errors
        + cluster_errors
        + dedup_errors
        + lineage_errors
        + hardcoded_membership_violations
    )

    result = {
        "gate": "SEMANTIC_RECLUSTER_RELIABILITY_V1_6_5",
        "status": "PASS" if not all_errors else "FAIL",
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
            "SEMANTIC_PARAPHRASE_EQUIVALENCE_GATE": {
                "status": gate(paraphrase_errors + equivalent_pair_errors),
                "count": len(paraphrase_errors) + len(equivalent_pair_errors),
                "violations": paraphrase_errors + equivalent_pair_errors,
                "inspected_support_edges": len(accepted_edges),
                "equivalent_pair_records": len(equivalent_pairs),
                "method": "support must be grounded in an evidence-backed structured mechanism signature; raw operation-text equality is forbidden as a required condition",
            },
            "SEMANTIC_FALSE_NEGATIVE_AUDIT": {
                "status": gate(false_negative_errors),
                "count": len(false_negative_errors),
                "violations": false_negative_errors,
                "suspicious_rejected_pairs": suspicious_rejected,
                "reviewed_suspicious_rejected_pairs": reviewed_suspicious_rejected,
                "method": "every KEEP_SEPARATE/HOLD pair with structural/operation retrieval or semantic-structure overlap receives paraphrase-equivalence adjudication",
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
            "equivalent_pair_records": len(equivalent_pairs),
            "clusters": len(clusters),
            "migration_records": len(migration_rows),
        },
        "ok": not all_errors,
    }

    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        output = args.output if args.output.is_absolute() else run_dir / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
