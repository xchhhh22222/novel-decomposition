# Emotion Arc V2 research contract

Status: `ARCHITECTURE_PROPOSAL / RESEARCH_ONLY`. This is a read-only derivative layer over canonical chapter emotion and approved component sources.

## Dataset layout

A pilot directory contains `source-manifest.json`, `promise-resolution.jsonl`, `emotion-lines.jsonl`, `emotion-weaves.jsonl`, `macro-emotion-arcs.jsonl`, `arc-handoffs.jsonl`, and human-readable review files. A pilot that performs targeted raw-text verification may also declare `source_text_audit_path` for a claim-level JSONL audit.

Every one of the four core JSONL record types requires:

`schema_version, record_type, record_id, book_id, status, qa_status, origin_kind, source_snapshot_ref, source_evidence_refs, source_component_refs, evidence_gaps, confidence, semantic_review`.

Observed pilot records must remain `status=candidate`, `qa_status=HOLD` unless independent approval is recorded, and `origin_kind=OBSERVED_SOURCE`. Stable ID prefixes are `EL:`, `EW:`, `MA:`, and `AH:`; IDs do not encode mutable chapter ranges and never reuse `EMOF:`, `PL:`, or `AR:` namespaces.

The opt-in R2 profile is declared by `research_contract_profile=CLAIM_EVIDENCE_V2`; legacy validation is unchanged. Under this profile every record declares `source_evidence_scope=REPRESENTATIVE_SUMMARY`: top-level `source_evidence_refs` are a compact navigation set, not the complete evidence union. Complete evidence is unambiguous by record type:

- emotion line: `beats[].evidence_refs`
- causal weave: `evidence_bindings`
- macro arc: `evidence_bindings`
- handoff: `evidence_bindings`
- promise crosswalk: `source_evidence_refs`

Each critical binding requires `claim`, `chapter_ref`, `source_record_id`, `field_path`, and `interpretation`. The validator resolves the chapter record and field. If a targeted source-text audit marks the canonical field `CONTRADICTED`, the binding must also provide the corresponding `source_text_audit_ref`; this acknowledges the conflict but does not make the interpretation true. The validator cannot decide whether the cited field proves the prose claim; unresolved semantics must report `NEEDS_SEMANTIC_REVIEW`.

## Emotion line

Required business fields are `reader_expectation`, `emotion_target`, `causal_generator`, observed range, lifecycle status, ordered beats, payoff contract, plotline/component/crosswalk references, and unresolved expectations. Beat functions are `OPEN`, `PRESSURIZE`, `CHOICE`, `PARTIAL_PAYOFF`, `PAYOFF`, `SETBACK`, `REFRAME`, `AFTERMATH`, `SUSPEND`, `FAIL`, `ABANDON`. A beat describes a change, agency, and evidence; it is not a repeated label.

## Emotion weave

Allowed types are `PARALLEL_ONLY`, `SHARED_EVENT`, `CAUSES_PRESSURE`, `ENABLES_CHOICE`, `CONFLICTS_WITH`, `PAYOFF_OPENS`, and `CO_PAYOFF`. At least two existing member lines must contain the event as a beat. Directed types require `direction`; causal types require `before_after`, `causal_explanation`, and structured `causal_evidence`. Co-occurrence types are not counted as causal.

## Macro emotion arc

Required fields include the macro promise/question, trigger, observed window, member lines, story/plot mappings, progression, independent payoff contract, irreversible state change, current status, and next candidates. Under R2, `macro_qualification` must identify an in-window qualification chapter, at least two progression references, at least two organized member lines, and an explanation. A new line opening is not macro qualification. A paid line cannot automatically close a macro arc.

## Arc handoff

Required fields include distinct from/to macro IDs, trigger, bridge type, causal bridge, new reader expectation, both entry statuses, an independent prior-payoff check, overlap flag, conclusion, and structured handoff evidence. Conclusions are `OBSERVED_OVERLAP`, `OBSERVED_SEQUENTIAL`, `CANDIDATE_UNVERIFIED`, or `NO_EVIDENCE`.

For an R2 `OBSERVED_OVERLAP` candidate, the target must demonstrate macro qualification no later than the prior macro's observed payoff. A new line or macro may not cancel, replace or waive the prior payoff contract. These are structural preconditions only; the record remains `qa_status=HOLD` until independent semantic acceptance.

## Provenance and review

The manifest freezes a Git commit and hashes each declared source blob. A raw source file's Git object identity and byte checksum are different claims and must be recorded separately as `source_text_git_blob={algorithm: git-sha1, oid: ...}` and `source_text_file_checksum={algorithm: sha256, value: ...}`. `REFERENCE_RESOLVED` only means referenced QA records were found. `SOURCE_TEXT_VERIFICATION_PARTIAL` must be retained when chapter source fingerprints are unavailable. Machine validation never grants semantic approval or production promotion. `claim_binding_gate=PASS` means only that the claimed evidence locations resolve and the required shape is complete.

Run:

```text
python skills/novel-dna-mining-suite/scripts/core/validate_emotion_arc_research.py <pilot-directory>
```
