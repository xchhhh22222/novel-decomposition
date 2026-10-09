#!/usr/bin/env python3
"""Validate the isolated NOVA Emotion Arc V2 research contract.

This validator checks structure, frozen Git snapshot closure, reference integrity,
crosswalk declarations, and the *declared* evidence shape for line/weave/macro/
handoff records.  It deliberately does not decide whether an emotional reading is
literarily or semantically correct, and it never promotes research data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable


BOOK_RE = re.compile(r"^BOOK_\d{3}$")
CHAPTER_RE = re.compile(r"^(BOOK_\d{3}):CHAPTER:(\d{4})$")
RECORD_PATTERNS = {
    "emotion_line": re.compile(r"^EL:(BOOK_\d{3}):(\d{3})$"),
    "emotion_weave": re.compile(r"^EW:(BOOK_\d{3}):(\d{3})$"),
    "macro_emotion_arc": re.compile(r"^MA:(BOOK_\d{3}):(\d{3})$"),
    "arc_handoff": re.compile(r"^AH:(BOOK_\d{3}):(\d{3})$"),
}
FILES = {
    "emotion_line": "emotion-lines.jsonl",
    "emotion_weave": "emotion-weaves.jsonl",
    "macro_emotion_arc": "macro-emotion-arcs.jsonl",
    "arc_handoff": "arc-handoffs.jsonl",
}
COMMON_FIELDS = {
    "schema_version", "record_type", "record_id", "book_id", "status",
    "qa_status", "origin_kind", "source_snapshot_ref", "source_evidence_refs",
    "source_component_refs", "evidence_gaps", "confidence", "semantic_review",
}
LINE_FUNCTIONS = {
    "OPEN", "PRESSURIZE", "CHOICE", "PARTIAL_PAYOFF", "PAYOFF", "SETBACK",
    "REFRAME", "AFTERMATH", "SUSPEND", "FAIL", "ABANDON",
}
LINE_STATES = {
    "ACTIVE", "SUSPENDED", "PARTIALLY_PAID", "PAID", "FAILED",
    "ABANDONED", "UNKNOWN",
}
WEAVE_TYPES = {
    "PARALLEL_ONLY", "SHARED_EVENT", "CAUSES_PRESSURE", "ENABLES_CHOICE",
    "CONFLICTS_WITH", "PAYOFF_OPENS", "CO_PAYOFF",
}
DIRECTED_WEAVES = {"CAUSES_PRESSURE", "ENABLES_CHOICE", "PAYOFF_OPENS"}
CAUSAL_WEAVES = DIRECTED_WEAVES | {"CONFLICTS_WITH"}
NONCAUSAL_WEAVES = {"PARALLEL_ONLY", "SHARED_EVENT", "CO_PAYOFF"}
RESOLUTION_STATES = {
    "EXACT_SEMANTIC_MATCH", "PARTIAL_RELATION", "DISTINCT_PROMISE", "UNRESOLVED",
}
MACRO_STATES = {"ACTIVE", "PARTIALLY_PAID", "PAID", "FAILED", "ABANDONED", "UNKNOWN"}
MACRO_PAYOFF_STATES = {
    "NOT_YET_OBSERVED", "PARTIAL_OBSERVED", "OBSERVED_PAID", "FAILED", "UNKNOWN",
}
HANDOFF_RESULTS = {
    "OBSERVED_OVERLAP", "OBSERVED_SEQUENTIAL", "CANDIDATE_UNVERIFIED", "NO_EVIDENCE",
}
CONFIDENCE = {"LOW", "MEDIUM", "HIGH"}
REVIEW = {"PENDING_REVIEW", "PASS", "HOLD", "FAIL"}
CLAIM_EVIDENCE_PROFILE = "CLAIM_EVIDENCE_V2"
EVIDENCE_SCOPE = "REPRESENTATIVE_SUMMARY"
FULL_EVIDENCE_VIEWS = {
    "emotion_line": "beats[].evidence_refs",
    "emotion_weave": "evidence_bindings",
    "macro_emotion_arc": "evidence_bindings",
    "arc_handoff": "evidence_bindings",
    "promise_resolution": "source_evidence_refs",
}
SHA1_RE = re.compile(r"[0-9a-f]{40}")
SHA256_RE = re.compile(r"[0-9a-f]{64}")
SOURCE_AUDIT_REQUIRED_FIELDS = {
    "audit_id", "research_claim_ids", "canonical_record_id", "canonical_field_path",
    "canonical_claim", "source_repo", "source_commit_sha", "source_path",
    "source_line_start", "source_line_end", "source_fact", "consistency",
    "affected_record_ids", "required_correction", "review_status",
}


def issue(items: list[dict[str, str]], code: str, where: str, message: str) -> None:
    items.append({"code": code, "where": where, "message": message})


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: Any, *, allow_empty: bool = True) -> bool:
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(nonempty(item) for item in value)
    )


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: JSON root must be an object")
    return value


def parse_jsonl_bytes(content: bytes, label: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(content.decode("utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError as exc:
            raise ValueError(f"{label}:{line_no}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{label}:{line_no}: JSONL row must be an object")
        rows.append(row)
    return rows


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return parse_jsonl_bytes(path.read_bytes(), str(path))


def git_root(start: Path) -> Path:
    result = subprocess.run(
        ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
        check=True, capture_output=True, text=True, encoding="utf-8",
    )
    return Path(result.stdout.strip()).resolve()


def git_blob(repo: Path, commit: str, rel: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), "show", f"{commit}:{rel}"],
        check=False, capture_output=True,
    )
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise OSError(detail or f"git blob unavailable: {commit}:{rel}")
    return result.stdout


def chapter_number(ref: Any) -> int | None:
    match = CHAPTER_RE.fullmatch(str(ref))
    return int(match.group(2)) if match else None


def collect_ids(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if (key == "record_id" or key.endswith("_id")) and nonempty(child):
                found.add(child)
            found.update(collect_ids(child))
    elif isinstance(value, list):
        for child in value:
            found.update(collect_ids(child))
    return found


def field_at(value: Any, path: str) -> Any:
    current = value
    for name, index in re.findall(r"([^.[\]]+)|\[(\d+)\]", path):
        current = current[name] if name else current[int(index)]
    return current


def unique_records(
    rows: list[dict[str, Any]], key: str, label: str, errors: list[dict[str, str]],
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        ident = row.get(key)
        where = f"{label}[{index}]"
        if not nonempty(ident):
            issue(errors, "MISSING_ID", where, f"{key} is required")
        elif ident in result:
            issue(errors, "DUPLICATE_ID", where, f"duplicate {key}={ident}")
        else:
            result[ident] = row
    return result


def validate_common(
    row: dict[str, Any], expected_type: str, where: str, book_id: str,
    chapter_rows: dict[str, dict[str, Any]], component_ids: set[str],
    errors: list[dict[str, str]], warnings: list[dict[str, str]],
    claim_evidence_mode: bool = False,
    source_text_audit_ids: set[str] | None = None,
    contradicted_canonical_fields: dict[tuple[str, str], set[str]] | None = None,
) -> None:
    source_text_audit_ids = source_text_audit_ids or set()
    contradicted_canonical_fields = contradicted_canonical_fields or {}
    missing = sorted(COMMON_FIELDS - set(row))
    if missing:
        issue(errors, "MISSING_REQUIRED_FIELDS", where, f"missing: {', '.join(missing)}")
    pattern = RECORD_PATTERNS[expected_type]
    match = pattern.fullmatch(str(row.get("record_id")))
    if not match or match.group(1) != book_id:
        issue(errors, "INVALID_RECORD_ID", where, f"invalid {expected_type} stable ID")
    if row.get("schema_version") != 1 or row.get("record_type") != expected_type:
        issue(errors, "INVALID_RECORD_TYPE", where, "schema_version=1 and matching record_type required")
    if row.get("book_id") != book_id:
        issue(errors, "BOOK_ID_MISMATCH", where, "record book_id differs from manifest")
    if row.get("status") != "candidate":
        issue(errors, "STATUS_PROMOTION_FORBIDDEN", where, "research status must remain candidate")
    if row.get("origin_kind") != "OBSERVED_SOURCE":
        issue(errors, "ORIGIN_LAYER_CONFLICT", where, "pilot source files accept OBSERVED_SOURCE only")
    if row.get("source_snapshot_ref") != "source-manifest.json":
        issue(errors, "SNAPSHOT_REF_MISMATCH", where, "source_snapshot_ref must be source-manifest.json")
    if row.get("confidence") not in CONFIDENCE:
        issue(errors, "INVALID_CONFIDENCE", where, "confidence must be LOW/MEDIUM/HIGH")
    review = row.get("semantic_review")
    if not isinstance(review, dict) or review.get("status") not in REVIEW:
        issue(errors, "INVALID_SEMANTIC_REVIEW", where, "semantic_review status is invalid")
        review = {}
    if row.get("qa_status") == "PASS" and (
        review.get("status") != "PASS"
        or not nonempty(review.get("reviewer"))
        or not nonempty(review.get("notes"))
    ):
        issue(errors, "STATUS_PROMOTION_FORBIDDEN", where, "QA PASS needs recorded independent semantic approval")
    elif row.get("qa_status") not in {"HOLD", "PASS", "FAIL"}:
        issue(errors, "INVALID_QA_STATUS", where, "qa_status must be HOLD/PASS/FAIL")
    refs = row.get("source_evidence_refs")
    if not string_list(refs, allow_empty=False):
        issue(errors, "MISSING_SOURCE_EVIDENCE", where, "source_evidence_refs must be nonempty")
        refs = []
    for ref in refs:
        source = chapter_rows.get(ref)
        if source is None:
            issue(errors, "MISSING_EVENT_REF", where, f"chapter evidence does not resolve: {ref}")
        elif source.get("qa_status") != "PASS":
            issue(errors, "SOURCE_QA_NOT_PASS", where, f"chapter evidence is not QA PASS: {ref}")
    components = row.get("source_component_refs")
    if not string_list(components):
        issue(errors, "INVALID_COMPONENT_REFS", where, "source_component_refs must be a string array")
    else:
        for ref in components:
            if ref not in component_ids:
                issue(errors, "MISSING_COMPONENT_REF", where, f"component reference does not resolve: {ref}")
    if not isinstance(row.get("evidence_gaps"), list):
        issue(errors, "INVALID_EVIDENCE_GAPS", where, "evidence_gaps must be an array")
    if claim_evidence_mode and row.get("source_evidence_scope") != EVIDENCE_SCOPE:
        issue(
            errors, "EVIDENCE_POLICY_INVALID", where,
            f"source_evidence_scope must be {EVIDENCE_SCOPE} under {CLAIM_EVIDENCE_PROFILE}",
        )
    bindings = row.get("evidence_bindings", [])
    if not isinstance(bindings, list):
        issue(errors, "INVALID_EVIDENCE_BINDINGS", where, "evidence_bindings must be an array")
        bindings = []
    requires_bindings = claim_evidence_mode and (
        expected_type in {"macro_emotion_arc", "arc_handoff"}
        or (expected_type == "emotion_weave" and row.get("weave_type") in CAUSAL_WEAVES)
    )
    if requires_bindings and not bindings:
        issue(
            errors, "CLAIM_BINDINGS_REQUIRED", where,
            "causal weave, macro transition, and handoff records need claim-level evidence bindings",
        )
    seen_claims: set[str] = set()
    for index, binding in enumerate(bindings if isinstance(bindings, list) else []):
        loc = f"{where}.evidence_bindings[{index}]"
        if not isinstance(binding, dict) or any(
            not nonempty(binding.get(key))
            for key in ("claim", "chapter_ref", "source_record_id", "field_path", "interpretation")
        ):
            issue(
                errors, "INVALID_EVIDENCE_BINDING", loc,
                "claim/chapter_ref/source_record_id/field_path/interpretation required",
            )
            continue
        if binding["claim"] in seen_claims:
            issue(errors, "INVALID_EVIDENCE_BINDING", loc, "claim text must be unique within a record")
        seen_claims.add(binding["claim"])
        source = chapter_rows.get(binding["chapter_ref"])
        if source is None or source.get("record_id") != binding["source_record_id"]:
            issue(errors, "MISSING_SOURCE_RECORD", loc, "source chapter or source record ID does not resolve")
            continue
        try:
            field_at(source, binding["field_path"])
        except (KeyError, IndexError, TypeError, ValueError):
            issue(errors, "MISSING_SOURCE_FIELD", loc, "field_path does not resolve in canonical source record")
        audit_ref = binding.get("source_text_audit_ref")
        if audit_ref is not None and audit_ref not in source_text_audit_ids:
            issue(errors, "MISSING_SOURCE_TEXT_AUDIT_REF", loc, "source_text_audit_ref does not resolve")
        contradicted_by = contradicted_canonical_fields.get((binding["source_record_id"], binding["field_path"]), set())
        if contradicted_by and audit_ref not in contradicted_by:
            issue(
                errors, "CONTRADICTED_CANONICAL_BINDING_UNACKNOWLEDGED", loc,
                "binding uses a canonical field contradicted by targeted source-text audit without acknowledging that audit",
            )
    if requires_bindings and review.get("status") != "PASS":
        issue(
            warnings, "SEMANTIC_CLAIM_UNVERIFIED", where,
            "claim bindings resolve structurally; causal/macro/handoff interpretation still needs independent review",
        )


def validate_pilot(pilot: Path, repo: Path | None = None) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    pilot = pilot.resolve()
    try:
        manifest = read_json(pilot / "source-manifest.json")
    except (OSError, ValueError) as exc:
        return {
            "ok": False, "machine_check": "NOT_RUN", "structural_gate": "FAIL", "source_reference_gate": "FAIL",
            "crosswalk_gate": "NOT_CHECKED", "weave_causality_evidence_gate": "NOT_CHECKED",
            "claim_binding_gate": "NOT_CHECKED", "source_text_audit_gate": "NOT_CHECKED",
            "macro_handoff_gate": "NOT_CHECKED",
            "source_trust": {"reference_status": "FAIL", "source_text_status": "UNKNOWN"},
            "semantic_review": "PENDING_INDEPENDENT_REVIEW", "test_summary": {},
            "errors": [{"code": "MANIFEST_UNREADABLE", "where": "source-manifest.json", "message": str(exc)}],
            "warnings": [],
        }

    book_id = manifest.get("book_id")
    chapter_range = manifest.get("chapter_range")
    contract_profile = manifest.get("research_contract_profile", "LEGACY_V1")
    claim_evidence_mode = contract_profile == CLAIM_EVIDENCE_PROFILE
    if contract_profile not in {"LEGACY_V1", CLAIM_EVIDENCE_PROFILE}:
        issue(errors, "INVALID_MANIFEST", "source-manifest.json", "unknown research_contract_profile")
    if claim_evidence_mode:
        evidence_policy = manifest.get("evidence_policy")
        if not isinstance(evidence_policy, dict):
            issue(errors, "EVIDENCE_POLICY_INVALID", "source-manifest.json", "evidence_policy object required")
        else:
            if evidence_policy.get("top_level_source_evidence_refs") != EVIDENCE_SCOPE:
                issue(
                    errors, "EVIDENCE_POLICY_INVALID", "source-manifest.json.evidence_policy",
                    f"top-level references must declare {EVIDENCE_SCOPE}",
                )
            if evidence_policy.get("full_evidence_views") != FULL_EVIDENCE_VIEWS:
                issue(
                    errors, "EVIDENCE_POLICY_INVALID", "source-manifest.json.evidence_policy",
                    "full_evidence_views must unambiguously name the complete evidence field for each record type",
                )
    if manifest.get("schema_version") != 1 or not BOOK_RE.fullmatch(str(book_id)):
        issue(errors, "INVALID_MANIFEST", "source-manifest.json", "schema_version=1 and BOOK_NNN book_id required")
    if not isinstance(chapter_range, dict) or not all(isinstance(chapter_range.get(k), int) for k in ("start", "end")):
        issue(errors, "INVALID_MANIFEST", "source-manifest.json", "chapter_range.start/end integers required")
        start, end = 1, 0
    else:
        start, end = chapter_range["start"], chapter_range["end"]
        if start < 1 or end < start:
            issue(errors, "INVALID_MANIFEST", "source-manifest.json", "invalid chapter range")
    commit = manifest.get("source_commit_sha")
    if not re.fullmatch(r"[0-9a-f]{40}", str(commit)):
        issue(errors, "INVALID_MANIFEST", "source-manifest.json", "40-hex source_commit_sha required")
    if not nonempty(manifest.get("source_repo")) or not isinstance(manifest.get("known_gaps"), list):
        issue(errors, "INVALID_MANIFEST", "source-manifest.json", "source_repo and known_gaps required")
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        issue(errors, "INVALID_MANIFEST", "source-manifest.json", "nonempty files[] required")
        files = []
    try:
        repo = repo.resolve() if repo else git_root(pilot)
    except (OSError, subprocess.SubprocessError) as exc:
        issue(errors, "SOURCE_REPO_UNAVAILABLE", "source-manifest.json", str(exc))
        repo = pilot

    source_by_role: dict[str, bytes] = {}
    seen_paths: set[str] = set()
    for index, entry in enumerate(files):
        where = f"source-manifest.json.files[{index}]"
        if not isinstance(entry, dict) or any(not nonempty(entry.get(k)) for k in ("path", "role", "sha256_or_unavailable")):
            issue(errors, "INVALID_MANIFEST_FILE", where, "path/role/sha256_or_unavailable required")
            continue
        rel, role, expected = entry["path"], entry["role"], entry["sha256_or_unavailable"]
        if Path(rel).is_absolute() or ".." in Path(rel).parts or rel in seen_paths:
            issue(errors, "INVALID_MANIFEST_FILE", where, "source path must be unique confined repository-relative path")
            continue
        seen_paths.add(rel)
        try:
            content = git_blob(repo, str(commit), rel)
        except OSError as exc:
            issue(errors, "SOURCE_SNAPSHOT_MISSING", where, str(exc))
            continue
        actual = hashlib.sha256(content).hexdigest()
        if expected != "UNAVAILABLE" and expected != actual:
            issue(errors, "SOURCE_SNAPSHOT_HASH_MISMATCH", where, f"expected {expected}, got {actual}")
        if role in source_by_role:
            issue(errors, "DUPLICATE_SOURCE_ROLE", where, f"duplicate source role: {role}")
        else:
            source_by_role[role] = content

    required_roles = {
        "chapter_emotion", "promise_ledger", "chapter_emotion_qa",
        "character_function", "plotline", "arc_structure",
    }
    missing_roles = sorted(required_roles - set(source_by_role))
    if missing_roles:
        issue(errors, "MISSING_SOURCE_ROLE", "source-manifest.json", f"missing roles: {', '.join(missing_roles)}")

    def rows_for(role: str) -> list[dict[str, Any]]:
        try:
            return parse_jsonl_bytes(source_by_role.get(role, b""), role)
        except ValueError as exc:
            issue(errors, "SOURCE_JSONL_INVALID", role, str(exc))
            return []

    chapter_list = rows_for("chapter_emotion")
    chapter_rows = unique_records(chapter_list, "chapter_ref", "chapter_emotion", errors)
    ledger_rows = unique_records(rows_for("promise_ledger"), "record_id", "promise_ledger", errors)
    qa_rows = rows_for("chapter_emotion_qa")
    component_docs: list[dict[str, Any]] = []
    for role in ("character_function", "plotline", "arc_structure"):
        component_docs.extend(rows_for(role))
    component_ids = collect_ids(component_docs)

    expected_refs = {f"{book_id}:CHAPTER:{chapter:04}" for chapter in range(start, end + 1)}
    actual_scope = {ref for ref in chapter_rows if chapter_number(ref) is not None and start <= int(ref[-4:]) <= end}
    for ref in sorted(expected_refs - actual_scope):
        issue(errors, "MISSING_CHAPTER_COVERAGE", "chapter_emotion", f"missing frozen chapter: {ref}")
    for ref in sorted(actual_scope):
        row = chapter_rows[ref]
        if row.get("book_id") != book_id or row.get("qa_status") != "PASS":
            issue(errors, "SOURCE_QA_NOT_PASS", "chapter_emotion", f"frozen chapter not QA PASS: {ref}")
    if not any(row.get("qa_status") == "PASS" and row.get("book_id") == book_id for row in qa_rows):
        issue(errors, "SOURCE_QA_NOT_PASS", "chapter_emotion_qa", "book-level chapter emotion QA PASS record missing")

    unavailable_fingerprints = sorted(
        ref for ref in actual_scope if chapter_rows[ref].get("source_fingerprint") == "UNAVAILABLE"
    )
    coverage = manifest.get("coverage")
    if not isinstance(coverage, dict):
        issue(errors, "INVALID_MANIFEST", "source-manifest.json.coverage", "coverage object required")
        coverage = {}
    declared_verification = coverage.get("source_text_verification_status")
    if unavailable_fingerprints and declared_verification not in {
        "SOURCE_TEXT_VERIFICATION_PARTIAL", "SOURCE_TEXT_NOT_VERIFIED",
    }:
        issue(errors, "PROVENANCE_OVERCLAIM", "source-manifest.json.coverage", "UNAVAILABLE chapter fingerprints forbid VERIFIED/FULL source text claim")
    if unavailable_fingerprints:
        issue(warnings, "SOURCE_FINGERPRINT_PARTIAL", "chapter_emotion", f"{len(unavailable_fingerprints)} in-scope chapter fingerprints are UNAVAILABLE")

    source_text_audit_ids: set[str] = set()
    contradicted_canonical_fields: dict[tuple[str, str], set[str]] = {}
    source_text_audit_enabled = False
    audit_path_value = manifest.get("source_text_audit_path")
    if "source_text_blob_sha256" in coverage and (claim_evidence_mode or audit_path_value is not None):
        issue(
            errors, "SOURCE_CHECKSUM_LABEL_INVALID", "source-manifest.json.coverage",
            "Git blob OID and file SHA-256 must be recorded separately; source_text_blob_sha256 is ambiguous",
        )
    if audit_path_value is not None:
        source_text_audit_enabled = True
        git_blob_meta = coverage.get("source_text_git_blob")
        file_checksum = coverage.get("source_text_file_checksum")
        if (
            not isinstance(git_blob_meta, dict)
            or git_blob_meta.get("algorithm") != "git-sha1"
            or not isinstance(git_blob_meta.get("oid"), str)
            or not SHA1_RE.fullmatch(git_blob_meta["oid"])
        ):
            issue(errors, "SOURCE_CHECKSUM_FORMAT_INVALID", "source-manifest.json.coverage.source_text_git_blob", "git-sha1 OID must be 40 lowercase hex characters")
        if (
            not isinstance(file_checksum, dict)
            or file_checksum.get("algorithm") != "sha256"
            or not isinstance(file_checksum.get("value"), str)
            or not SHA256_RE.fullmatch(file_checksum["value"])
        ):
            issue(errors, "SOURCE_CHECKSUM_FORMAT_INVALID", "source-manifest.json.coverage.source_text_file_checksum", "SHA-256 must be 64 lowercase hex characters")
        if not isinstance(audit_path_value, str) or not audit_path_value or Path(audit_path_value).is_absolute() or ".." in Path(audit_path_value).parts:
            issue(errors, "SOURCE_TEXT_AUDIT_INVALID", "source-manifest.json.source_text_audit_path", "audit path must be a relative in-pilot path")
            audit_rows: list[dict[str, Any]] = []
        else:
            try:
                audit_rows = read_jsonl(pilot / audit_path_value)
            except (OSError, ValueError) as exc:
                issue(errors, "SOURCE_TEXT_AUDIT_INVALID", audit_path_value, str(exc))
                audit_rows = []
        for index, audit in enumerate(audit_rows):
            where = f"{audit_path_value}[{index}]"
            if not isinstance(audit, dict) or SOURCE_AUDIT_REQUIRED_FIELDS - set(audit):
                issue(errors, "SOURCE_TEXT_AUDIT_INVALID", where, "source-text audit row is missing required fields")
                continue
            audit_id = audit.get("audit_id")
            if not isinstance(audit_id, str) or not audit_id.startswith(f"STA:{book_id}:R3:") or audit_id in source_text_audit_ids:
                issue(errors, "SOURCE_TEXT_AUDIT_INVALID", where, "audit_id must be unique STA:<book>:R3:<nnn>")
                continue
            source_text_audit_ids.add(audit_id)
            if (
                not string_list(audit.get("research_claim_ids"), allow_empty=False)
                or not string_list(audit.get("affected_record_ids"), allow_empty=False)
                or not all(nonempty(audit.get(key)) for key in (
                    "canonical_record_id", "canonical_field_path", "canonical_claim", "source_repo",
                    "source_commit_sha", "source_path", "source_fact", "required_correction", "review_status",
                ))
                or audit.get("consistency") not in {"CONSISTENT", "PARTIAL", "CONTRADICTED"}
                or audit.get("review_status") != "REVIEWED_R3"
                or not isinstance(audit.get("source_line_start"), int)
                or not isinstance(audit.get("source_line_end"), int)
                or audit["source_line_start"] <= 0
                or audit["source_line_end"] < audit["source_line_start"]
                or audit.get("source_repo") != coverage.get("source_text_repo")
                or audit.get("source_commit_sha") != coverage.get("source_text_commit_sha")
            ):
                issue(errors, "SOURCE_TEXT_AUDIT_INVALID", where, "audit provenance, line range, arrays, consistency, or review status is invalid")
            if audit.get("consistency") == "CONTRADICTED":
                key = (str(audit.get("canonical_record_id")), str(audit.get("canonical_field_path")))
                contradicted_canonical_fields.setdefault(key, set()).add(audit_id)
            canonical_source = next(
                (row for row in chapter_rows.values() if row.get("record_id") == audit.get("canonical_record_id")),
                None,
            )
            if canonical_source is None:
                issue(errors, "SOURCE_TEXT_AUDIT_INVALID", where, "canonical_record_id does not resolve")
            else:
                try:
                    field_at(canonical_source, str(audit.get("canonical_field_path")))
                except (KeyError, IndexError, TypeError, ValueError):
                    issue(errors, "SOURCE_TEXT_AUDIT_INVALID", where, "canonical_field_path does not resolve")

    typed_rows: dict[str, list[dict[str, Any]]] = {}
    all_stable_ids: dict[str, str] = {}
    for record_type, filename in FILES.items():
        path = pilot / filename
        try:
            rows = read_jsonl(path)
        except (OSError, ValueError) as exc:
            issue(errors, "RESEARCH_FILE_UNREADABLE", filename, str(exc))
            rows = []
        typed_rows[record_type] = rows
        for index, row in enumerate(rows):
            where = f"{filename}[{index}]"
            validate_common(
                row, record_type, where, str(book_id), chapter_rows, component_ids,
                errors, warnings, claim_evidence_mode, source_text_audit_ids, contradicted_canonical_fields,
            )
            ident = row.get("record_id")
            if nonempty(ident):
                if ident in all_stable_ids:
                    issue(errors, "DUPLICATE_ID", where, f"duplicate ID already seen in {all_stable_ids[ident]}")
                all_stable_ids[ident] = where

    lines = unique_records(typed_rows["emotion_line"], "record_id", "emotion-lines.jsonl", errors)
    line_chapters: dict[str, set[str]] = {}
    for ident, row in lines.items():
        where = f"emotion-lines.jsonl.{ident}"
        for key in ("reader_expectation", "emotion_target", "causal_generator"):
            if not nonempty(row.get(key)):
                issue(errors, "LINE_REQUIRED_FIELDS", where, f"{key} required")
        line_start, line_end = row.get("start_chapter"), row.get("end_chapter_observed")
        if not isinstance(line_start, int) or not isinstance(line_end, int) or not start <= line_start <= line_end <= end:
            issue(errors, "LINE_TEMPORAL_CONFLICT", where, "line chapter range must stay inside frozen range")
        if row.get("lifecycle_status") not in LINE_STATES:
            issue(errors, "LINE_INVALID_STATE", where, "invalid lifecycle_status")
        beats = row.get("beats")
        if not isinstance(beats, list) or not beats:
            issue(errors, "LINE_REQUIRED_FIELDS", where, "nonempty beats[] required")
            beats = []
        seen_beats: set[str] = set()
        last_chapter = -1
        chapters_for_line: set[str] = set()
        for index, beat in enumerate(beats):
            loc = f"{where}.beats[{index}]"
            if not isinstance(beat, dict):
                issue(errors, "LINE_REQUIRED_FIELDS", loc, "beat must be object")
                continue
            beat_id = beat.get("beat_id")
            if not nonempty(beat_id) or not str(beat_id).startswith(f"{ident}:B") or beat_id in seen_beats:
                issue(errors, "LINE_BEAT_ID_INVALID", loc, "stable unique line-prefixed beat_id required")
            seen_beats.add(str(beat_id))
            ref = beat.get("chapter_ref")
            number = chapter_number(ref)
            if number is not None and not start <= number <= end:
                issue(errors, "OUT_OF_SCOPE_REF", loc, f"beat chapter outside frozen range: {ref}")
            elif ref not in chapter_rows or number is None:
                issue(errors, "MISSING_EVENT_REF", loc, f"beat chapter does not resolve: {ref}")
            elif isinstance(line_start, int) and not line_start <= number <= line_end:
                issue(errors, "OUT_OF_SCOPE_REF", loc, f"beat chapter outside declared scope: {ref}")
            elif number < last_chapter:
                issue(errors, "LINE_TEMPORAL_CONFLICT", loc, "beats must not move backward in time")
            else:
                last_chapter = number
                chapters_for_line.add(ref)
            if beat.get("function") not in LINE_FUNCTIONS:
                issue(errors, "LINE_BEAT_INVALID", loc, "invalid beat function")
            for key in ("reader_expectation_change", "character_agency", "state_change"):
                if not nonempty(beat.get(key)):
                    issue(errors, "LINE_BEAT_INVALID", loc, f"{key} required")
            evidence = beat.get("evidence_refs")
            if not string_list(evidence, allow_empty=False) or ref not in evidence:
                issue(errors, "LINE_BEAT_INVALID", loc, "beat evidence_refs must include chapter_ref")
        line_chapters[ident] = chapters_for_line
        payoff = row.get("payoff_contract")
        if not isinstance(payoff, dict) or any(not nonempty(payoff.get(k)) for k in ("expected_observable_result", "observed_result", "state")):
            issue(errors, "LINE_PAYOFF_CONTRACT_INVALID", where, "payoff contract fields required")
        elif row.get("lifecycle_status") == "PAID" and payoff.get("state") != "PAID":
            issue(errors, "LINE_PAYOFF_CONTRACT_INVALID", where, "PAID line needs PAID payoff contract")
        for key in ("related_plotline_refs", "related_component_refs", "promise_resolution_refs", "unresolved_expectations"):
            if not string_list(row.get(key)):
                issue(errors, "LINE_REQUIRED_FIELDS", where, f"{key} must be a string array")

    try:
        crosswalk_list = read_jsonl(pilot / "promise-resolution.jsonl")
    except (OSError, ValueError) as exc:
        issue(errors, "RESEARCH_FILE_UNREADABLE", "promise-resolution.jsonl", str(exc))
        crosswalk_list = []
    crosswalk = unique_records(crosswalk_list, "resolution_id", "promise-resolution.jsonl", errors)
    unresolved_crosswalk = 0
    for ident, row in crosswalk.items():
        where = f"promise-resolution.jsonl.{ident}"
        if not re.fullmatch(r"PR:BOOK_\d{3}:\d{3}", str(ident)):
            issue(errors, "CROSSWALK_INVALID_ID", where, "resolution_id must be PR:BOOK_NNN:nnn")
        locator = row.get("chapter_promise_locator")
        if not isinstance(locator, dict):
            issue(errors, "CROSSWALK_LOCATOR_INVALID", where, "chapter_promise_locator required")
            continue
        ref, source_field, array_index = locator.get("chapter_ref"), locator.get("source_field"), locator.get("array_index")
        source = chapter_rows.get(ref)
        if source is None or source_field != "promise_opened" or not isinstance(array_index, int):
            issue(errors, "CROSSWALK_LOCATOR_INVALID", where, "locator must resolve promise_opened array")
        else:
            values = source.get(source_field)
            if not isinstance(values, list) or not 0 <= array_index < len(values) or values[array_index] != locator.get("raw_value"):
                issue(errors, "CROSSWALK_LOCATOR_INVALID", where, "raw_value does not match canonical chapter field")
        candidates = row.get("candidate_ledger_record_ids")
        if not string_list(candidates):
            issue(errors, "CROSSWALK_CANDIDATES_INVALID", where, "candidate ledger IDs must be a string array")
            candidates = []
        for candidate in candidates:
            if candidate not in ledger_rows:
                issue(errors, "CROSSWALK_LEDGER_MISSING", where, f"ledger record does not resolve: {candidate}")
        state = row.get("resolution_status")
        if state not in RESOLUTION_STATES:
            issue(errors, "CROSSWALK_STATUS_INVALID", where, "invalid resolution_status")
        if state == "UNRESOLVED":
            unresolved_crosswalk += 1
            issue(warnings, "CROSSWALK_UNRESOLVED", where, "unresolved mapping retained as research gap")
        elif state in {"EXACT_SEMANTIC_MATCH", "PARTIAL_RELATION"} and not candidates:
            issue(errors, "CROSSWALK_CANDIDATES_INVALID", where, "matched relation requires ledger candidate")
        if (
            book_id == "BOOK_001" and ref == "BOOK_001:CHAPTER:0001"
            and str(locator.get("raw_value", "")).startswith("P001:")
            and "BOOK_001:PROMISE:001" in candidates
            and state == "EXACT_SEMANTIC_MATCH"
        ):
            issue(errors, "UNSUPPORTED_PROMISE_IDENTITY", where, "known local P001 and ledger PROMISE:001 semantic conflict cannot be linked by suffix")
        if not nonempty(row.get("evidence_summary")):
            issue(errors, "CROSSWALK_REQUIRED_FIELDS", where, "evidence_summary required")
        linked = row.get("linked_emotion_line_ids")
        if not string_list(linked):
            issue(errors, "CROSSWALK_REQUIRED_FIELDS", where, "linked_emotion_line_ids must be string array")
        else:
            for line_id in linked:
                if line_id not in lines:
                    issue(errors, "CROSSWALK_LINE_MISSING", where, f"linked line does not resolve: {line_id}")
        refs = row.get("source_evidence_refs")
        if not string_list(refs, allow_empty=False) or ref not in refs:
            issue(errors, "CROSSWALK_REQUIRED_FIELDS", where, "source_evidence_refs must include locator chapter")

    for ident, row in lines.items():
        for ref in row.get("promise_resolution_refs", []) if isinstance(row.get("promise_resolution_refs"), list) else []:
            if ref not in crosswalk:
                issue(errors, "CROSSWALK_REFERENCE_MISSING", f"emotion-lines.jsonl.{ident}", f"promise resolution does not resolve: {ref}")

    weaves = unique_records(typed_rows["emotion_weave"], "record_id", "emotion-weaves.jsonl", errors)
    causal_count = 0
    noncausal_count = 0
    for ident, row in weaves.items():
        where = f"emotion-weaves.jsonl.{ident}"
        members = row.get("member_line_ids")
        if not string_list(members, allow_empty=False) or len(set(members)) < 2 or any(member not in lines for member in members):
            issue(errors, "INVALID_MEMBERS", where, "at least two distinct existing line IDs required")
            members = []
        weave_type = row.get("weave_type")
        if weave_type not in WEAVE_TYPES:
            issue(errors, "WEAVE_TYPE_INVALID", where, "invalid weave_type")
        event = row.get("event_chapter_ref")
        if event not in chapter_rows:
            issue(errors, "MISSING_EVENT_REF", where, f"event chapter does not resolve: {event}")
        else:
            number = chapter_number(event)
            if number is None or not start <= number <= end:
                issue(errors, "OUT_OF_SCOPE_REF", where, f"event chapter outside frozen range: {event}")
            for member in members:
                if event not in line_chapters.get(member, set()):
                    issue(errors, "WEAVE_EVENT_NOT_IN_MEMBER", where, f"event is not a beat of member line {member}")
        if not nonempty(row.get("trigger_event")):
            issue(errors, "WEAVE_REQUIRED_FIELDS", where, "trigger_event required")
        before_after = row.get("before_after")
        if not isinstance(before_after, dict) or any(not nonempty(before_after.get(k)) for k in ("before", "after")):
            issue(errors, "CAUSAL_LINK_UNSUPPORTED", where, "before_after.before/after required")
        if weave_type in CAUSAL_WEAVES:
            causal_count += 1
            if weave_type in DIRECTED_WEAVES:
                direction = row.get("direction")
                if not isinstance(direction, dict) or direction.get("from_line_id") not in members or direction.get("to_line_id") not in members or direction.get("from_line_id") == direction.get("to_line_id"):
                    issue(errors, "CAUSAL_LINK_UNSUPPORTED", where, "directed weave requires valid distinct from/to members")
            if not nonempty(row.get("causal_explanation")):
                issue(errors, "CAUSAL_LINK_UNSUPPORTED", where, "causal_explanation required")
            evidence = row.get("causal_evidence")
            if not isinstance(evidence, dict) or any(
                not nonempty(evidence.get(key))
                for key in ("from_state_change", "to_pressure_or_choice", "bridge_observation")
            ):
                issue(errors, "CAUSAL_LINK_UNSUPPORTED", where, "structured causal_evidence required; co-occurrence text is insufficient")
        elif weave_type in NONCAUSAL_WEAVES:
            noncausal_count += 1
            if row.get("direction") is not None:
                issue(errors, "NONCAUSAL_DIRECTION_FORBIDDEN", where, "noncausal weave direction must be null")
            if not nonempty(row.get("noncausal_note")):
                issue(errors, "WEAVE_REQUIRED_FIELDS", where, "noncausal_note required")

    macros = unique_records(typed_rows["macro_emotion_arc"], "record_id", "macro-emotion-arcs.jsonl", errors)
    macro_start: dict[str, int] = {}
    macro_payoff: dict[str, int | None] = {}
    macro_qualified_at: dict[str, int | None] = {}
    for ident, row in macros.items():
        where = f"macro-emotion-arcs.jsonl.{ident}"
        for key in ("reader_macro_promise", "macro_question", "progression_summary", "irreversible_state_change"):
            if not nonempty(row.get(key)):
                issue(errors, "MACRO_REQUIRED_FIELDS", where, f"{key} required")
        window = row.get("observed_window")
        if not isinstance(window, dict) or not all(isinstance(window.get(k), int) for k in ("start", "end")) or not start <= window.get("start", 0) <= window.get("end", 0) <= end:
            issue(errors, "MACRO_TEMPORAL_CONFLICT", where, "observed_window must stay inside manifest range")
            macro_start[ident] = end + 1
        else:
            macro_start[ident] = window["start"]
        trigger = row.get("start_trigger_chapter_ref")
        if trigger not in chapter_rows or chapter_number(trigger) != macro_start[ident]:
            issue(errors, "MACRO_TEMPORAL_CONFLICT", where, "start trigger must resolve to observed_window.start")
        members = row.get("member_line_ids")
        if not string_list(members, allow_empty=False) or any(member not in lines for member in members):
            issue(errors, "MACRO_INVALID_MEMBERS", where, "macro needs existing member line IDs")
            members = []
        elif len(set(members)) == 1:
            issue(warnings, "MACRO_SINGLE_LINE_PARTIAL", where, "single-line macro requires human review of organizing value")
        if claim_evidence_mode:
            qualification = row.get("macro_qualification")
            qualified_at: int | None = None
            if not isinstance(qualification, dict):
                issue(errors, "MACRO_ORGANIZATION_UNPROVEN", where, "macro_qualification object required")
            else:
                qualified_ref = qualification.get("qualification_chapter_ref")
                qualified_at = chapter_number(qualified_ref)
                sustained = qualification.get("sustained_progression_evidence_refs")
                organized = qualification.get("organized_line_ids")
                sustained_chapters = [chapter_number(ref) for ref in sustained] if isinstance(sustained, list) else []
                organized_have_in_window_beats = (
                    isinstance(organized, list)
                    and qualified_at is not None
                    and isinstance(window, dict)
                    and all(
                        any(
                            (beat_chapter := chapter_number(beat.get("chapter_ref"))) is not None
                            and window.get("start", 0) <= beat_chapter <= qualified_at
                            for beat in lines.get(line_id, {}).get("beats", [])
                            if isinstance(beat, dict)
                        )
                        for line_id in organized
                    )
                )
                if (
                    qualified_ref not in chapter_rows
                    or qualified_at is None
                    or not isinstance(window, dict)
                    or not window.get("start", 0) <= qualified_at <= window.get("end", 0)
                    or not string_list(sustained, allow_empty=False)
                    or len(set(sustained)) < 2
                    or any(ref not in chapter_rows for ref in sustained)
                    or any(
                        chapter is None or not window.get("start", 0) <= chapter <= qualified_at
                        for chapter in sustained_chapters
                    )
                    or not string_list(organized, allow_empty=False)
                    or len(set(organized)) < 2
                    or any(line_id not in members for line_id in organized)
                    or not organized_have_in_window_beats
                    or not nonempty(qualification.get("organization_explanation"))
                ):
                    issue(
                        errors, "MACRO_ORGANIZATION_UNPROVEN", where,
                        "macro qualification needs 2+ in-window progression refs and 2+ member lines with beats by the qualification chapter",
                    )
            macro_qualified_at[ident] = qualified_at
        else:
            macro_qualified_at[ident] = macro_start.get(ident)
        if row.get("current_status") not in MACRO_STATES:
            issue(errors, "MACRO_INVALID_STATE", where, "invalid current_status")
        payoff = row.get("payoff_contract")
        payoff_refs: list[str] = []
        if not isinstance(payoff, dict) or not nonempty(payoff.get("criterion")) or payoff.get("status") not in MACRO_PAYOFF_STATES:
            issue(errors, "MACRO_PAYOFF_INVALID", where, "payoff criterion/status required")
        else:
            payoff_refs = payoff.get("observed_evidence_refs")
            if not string_list(payoff_refs):
                issue(errors, "MACRO_PAYOFF_INVALID", where, "observed_evidence_refs must be a string array")
                payoff_refs = []
            for ref in payoff_refs:
                if ref not in chapter_rows:
                    issue(errors, "MISSING_PAYOFF_EVIDENCE", where, f"payoff evidence does not resolve: {ref}")
        if row.get("current_status") == "PAID" and (
            not isinstance(payoff, dict) or payoff.get("status") != "OBSERVED_PAID" or not payoff_refs
        ):
            issue(errors, "MISSING_PAYOFF_EVIDENCE", where, "PAID macro requires observed payoff evidence")
        macro_payoff[ident] = max((chapter_number(ref) or 0 for ref in payoff_refs), default=None)
        for key in ("related_story_arc_refs", "related_plotline_refs", "next_macro_candidates"):
            if not string_list(row.get(key)):
                issue(errors, "MACRO_REQUIRED_FIELDS", where, f"{key} must be a string array")

    handoffs = unique_records(typed_rows["arc_handoff"], "record_id", "arc-handoffs.jsonl", errors)
    handoff_hold = False
    for ident, row in handoffs.items():
        where = f"arc-handoffs.jsonl.{ident}"
        source_id, target_id = row.get("from_macro_id"), row.get("to_macro_id")
        if source_id not in macros or target_id not in macros or source_id == target_id:
            issue(errors, "HANDOFF_INVALID_MACROS", where, "distinct existing from/to macro IDs required")
        trigger = row.get("handoff_trigger_chapter_ref")
        if trigger not in chapter_rows:
            issue(errors, "MISSING_EVENT_REF", where, f"handoff trigger does not resolve: {trigger}")
        for key in ("bridge_type", "causal_bridge", "reader_expectation_at_handoff", "old_arc_status_at_entry", "new_arc_status_at_entry"):
            if not nonempty(row.get(key)):
                issue(errors, "HANDOFF_REQUIRED_FIELDS", where, f"{key} required")
        evidence = row.get("handoff_evidence")
        if row.get("handoff_conclusion") != "NO_EVIDENCE" and (
            not isinstance(evidence, dict) or any(
                not nonempty(evidence.get(key))
                for key in ("prior_state_change", "new_promise_trigger", "distinct_constraint")
            )
        ):
            issue(errors, "HANDOFF_REQUIRED_FIELDS", where, "structured handoff_evidence required; a new-enemy label is insufficient")
        conclusion = row.get("handoff_conclusion")
        if conclusion not in HANDOFF_RESULTS:
            issue(errors, "HANDOFF_REQUIRED_FIELDS", where, "invalid handoff_conclusion")
        overlap = row.get("has_observed_overlap")
        if not isinstance(overlap, bool):
            issue(errors, "HANDOFF_REQUIRED_FIELDS", where, "has_observed_overlap must be boolean")
        if conclusion == "OBSERVED_OVERLAP" and overlap is not True:
            issue(errors, "HANDOFF_TEMPORAL_CONFLICT", where, "OBSERVED_OVERLAP requires has_observed_overlap=true")
        if overlap is True and source_id in macro_payoff and target_id in macro_start:
            paid_at = macro_payoff[source_id]
            if paid_at is not None and macro_start[target_id] > paid_at:
                issue(errors, "HANDOFF_TEMPORAL_CONFLICT", where, "new macro starts after prior macro observed payoff")
            if (
                claim_evidence_mode and conclusion == "OBSERVED_OVERLAP" and paid_at is not None
                and (
                    macro_qualified_at.get(target_id) is None
                    or macro_qualified_at[target_id] > paid_at
                )
            ):
                issue(
                    errors, "HANDOFF_TEMPORAL_CONFLICT", where,
                    "target macro must demonstrate organizing capacity no later than prior macro payoff",
                )
        prior = row.get("prior_arc_payoff_check")
        if not isinstance(prior, dict) or any(not nonempty(prior.get(k)) for k in ("criterion", "observed_result", "status")):
            issue(errors, "HANDOFF_REQUIRED_FIELDS", where, "prior_arc_payoff_check fields required")
        elif prior.get("status") == "PENDING":
            handoff_hold = True
            issue(warnings, "PRIOR_ARC_PAYOFF_PENDING", where, "prior macro payoff remains pending independent review")
        elif claim_evidence_mode and prior.get("status") in {"CANCELLED", "REPLACED", "WAIVED"}:
            issue(
                errors, "PRIOR_PAYOFF_CONTRACT_CANCELLED", where,
                "a new line or macro cannot cancel, replace, or waive the prior payoff contract",
            )
        elif claim_evidence_mode and prior.get("status") == "OBSERVED_PAID":
            prior_refs = prior.get("observed_evidence_refs")
            if not string_list(prior_refs, allow_empty=False) or any(ref not in chapter_rows for ref in prior_refs):
                issue(
                    errors, "HANDOFF_REQUIRED_FIELDS", where,
                    "OBSERVED_PAID prior payoff needs resolvable observed_evidence_refs",
                )
        if conclusion in {"CANDIDATE_UNVERIFIED", "NO_EVIDENCE"}:
            handoff_hold = True
            issue(warnings, "HANDOFF_UNVERIFIED", where, f"handoff conclusion retained as {conclusion}")

    source_codes = {
        "SOURCE_REPO_UNAVAILABLE", "SOURCE_SNAPSHOT_MISSING", "SOURCE_SNAPSHOT_HASH_MISMATCH",
        "MISSING_SOURCE_ROLE", "SOURCE_JSONL_INVALID", "MISSING_CHAPTER_COVERAGE", "SOURCE_QA_NOT_PASS",
        "PROVENANCE_OVERCLAIM", "MISSING_SOURCE_RECORD", "MISSING_SOURCE_FIELD", "MISSING_COMPONENT_REF",
        "SOURCE_CHECKSUM_LABEL_INVALID", "SOURCE_CHECKSUM_FORMAT_INVALID", "SOURCE_TEXT_AUDIT_INVALID",
        "MISSING_SOURCE_TEXT_AUDIT_REF", "CONTRADICTED_CANONICAL_BINDING_UNACKNOWLEDGED",
    }
    crosswalk_codes = {code for code in (entry["code"] for entry in errors) if code.startswith("CROSSWALK") or code == "UNSUPPORTED_PROMISE_IDENTITY"}
    weave_codes = {entry["code"] for entry in errors if entry["code"] in {
        "INVALID_MEMBERS", "WEAVE_TYPE_INVALID", "CAUSAL_LINK_UNSUPPORTED", "NONCAUSAL_DIRECTION_FORBIDDEN",
        "WEAVE_REQUIRED_FIELDS", "WEAVE_EVENT_NOT_IN_MEMBER",
    }}
    macro_codes = {
        entry["code"] for entry in errors if entry["code"].startswith("MACRO")
        or entry["code"].startswith("HANDOFF")
        or entry["code"] in {"MISSING_PAYOFF_EVIDENCE", "PRIOR_PAYOFF_CONTRACT_CANCELLED"}
    }
    claim_binding_codes = {
        entry["code"] for entry in errors if entry["code"] in {
            "EVIDENCE_POLICY_INVALID", "CLAIM_BINDINGS_REQUIRED", "INVALID_EVIDENCE_BINDINGS",
            "INVALID_EVIDENCE_BINDING", "MISSING_SOURCE_RECORD", "MISSING_SOURCE_FIELD",
            "MISSING_SOURCE_TEXT_AUDIT_REF", "CONTRADICTED_CANONICAL_BINDING_UNACKNOWLEDGED",
        }
    }
    source_failed = any(entry["code"] in source_codes for entry in errors)
    semantic_statuses = {
        row.get("semantic_review", {}).get("status")
        for rows in typed_rows.values() for row in rows if isinstance(row.get("semantic_review"), dict)
    }
    structural_exclusions = source_codes | crosswalk_codes | weave_codes | macro_codes | claim_binding_codes
    structural_failed = any(entry["code"] not in structural_exclusions for entry in errors)
    semantic_pending = semantic_statuses != {"PASS"}
    weave_gate = "FAIL" if weave_codes or claim_binding_codes else "PASS"
    macro_gate = "FAIL" if macro_codes or claim_binding_codes else "HOLD" if handoff_hold else "PASS"
    if claim_evidence_mode and semantic_pending:
        if weave_gate == "PASS" and causal_count:
            weave_gate = "NEEDS_SEMANTIC_REVIEW"
        if macro_gate == "PASS" and (macros or handoffs):
            macro_gate = "NEEDS_SEMANTIC_REVIEW"

    return {
        "ok": not errors,
        "machine_check": (
            "STRUCTURE_REFERENCE_AND_CLAIM_BINDING_RESOLUTION_ONLY"
            if claim_evidence_mode else "STRUCTURE_REFERENCE_AND_DECLARED_CAUSAL_EVIDENCE_ONLY"
        ),
        "structural_gate": "FAIL" if structural_failed else "PASS",
        "source_reference_gate": "FAIL" if source_failed else "PASS",
        "source_text_audit_gate": (
            "FAIL" if any(entry["code"] in {
                "SOURCE_CHECKSUM_LABEL_INVALID", "SOURCE_CHECKSUM_FORMAT_INVALID", "SOURCE_TEXT_AUDIT_INVALID",
                "MISSING_SOURCE_TEXT_AUDIT_REF", "CONTRADICTED_CANONICAL_BINDING_UNACKNOWLEDGED",
            } for entry in errors) else "PASS" if source_text_audit_enabled else "NOT_ENABLED"
        ),
        "crosswalk_gate": "FAIL" if crosswalk_codes else "HOLD" if unresolved_crosswalk else "PASS",
        "claim_binding_gate": "FAIL" if claim_binding_codes else "PASS" if claim_evidence_mode else "NOT_ENABLED",
        "weave_causality_evidence_gate": weave_gate,
        "macro_handoff_gate": macro_gate,
        "source_trust": {
            "reference_status": "FAIL" if source_failed else "REFERENCE_RESOLVED",
            "source_text_status": "SOURCE_TEXT_VERIFICATION_PARTIAL" if unavailable_fingerprints else "NO_MISSING_FINGERPRINT_REPORTED",
            "source_commit_sha": commit,
            "targeted_source_text_audit": "REVIEWED_R3" if source_text_audit_enabled else "NOT_ENABLED",
        },
        "semantic_review": "PENDING_INDEPENDENT_REVIEW" if semantic_pending else "PASS_RECORDED",
        "creation_approval": "NOT_GRANTED",
        "production_promotion": "NOT_RUN",
        "test_summary": {
            "book_id": book_id,
            "chapter_range": {"start": start, "end": end},
            "chapters_with_qa_pass": len(actual_scope),
            "emotion_lines": len(lines),
            "weaves_causal": causal_count,
            "weaves_noncausal": noncausal_count,
            "macro_arcs": len(macros),
            "handoffs": len(handoffs),
            "promise_crosswalk_unresolved": unresolved_crosswalk,
        },
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate isolated NOVA Emotion Arc V2 research data.")
    parser.add_argument("pilot_root", type=Path)
    parser.add_argument("--repo-root", type=Path, help="Override Git repository used to resolve source_commit_sha blobs")
    args = parser.parse_args()
    try:
        report = validate_pilot(args.pilot_root, args.repo_root)
    except (OSError, ValueError, TypeError, subprocess.SubprocessError) as exc:
        report = {
            "ok": False, "structural_gate": "FAIL", "source_reference_gate": "FAIL",
            "crosswalk_gate": "NOT_CHECKED", "weave_causality_evidence_gate": "NOT_CHECKED",
            "source_text_audit_gate": "NOT_CHECKED", "macro_handoff_gate": "NOT_CHECKED",
            "source_trust": {"reference_status": "FAIL"},
            "semantic_review": "PENDING_INDEPENDENT_REVIEW", "test_summary": {},
            "errors": [{"code": "VALIDATOR_EXCEPTION", "where": "runtime", "message": str(exc)}],
            "warnings": [],
        }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
