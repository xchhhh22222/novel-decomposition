# Emotion Arc V2 research contract

Status: `ARCHITECTURE_PROPOSAL / RESEARCH_ONLY`. This is a read-only derivative layer over canonical chapter emotion and approved component sources.

## Dataset layout

A pilot directory contains `source-manifest.json`, `promise-resolution.jsonl`, `emotion-lines.jsonl`, `emotion-weaves.jsonl`, `macro-emotion-arcs.jsonl`, `arc-handoffs.jsonl`, and human-readable review files.

Every one of the four core JSONL record types requires:

`schema_version, record_type, record_id, book_id, status, qa_status, origin_kind, source_snapshot_ref, source_evidence_refs, source_component_refs, evidence_gaps, confidence, semantic_review`.

Observed pilot records must remain `status=candidate`, `qa_status=HOLD` unless independent approval is recorded, and `origin_kind=OBSERVED_SOURCE`. Stable ID prefixes are `EL:`, `EW:`, `MA:`, and `AH:`; IDs do not encode mutable chapter ranges and never reuse `EMOF:`, `PL:`, or `AR:` namespaces.

## Emotion line

Required business fields are `reader_expectation`, `emotion_target`, `causal_generator`, observed range, lifecycle status, ordered beats, payoff contract, plotline/component/crosswalk references, and unresolved expectations. Beat functions are `OPEN`, `PRESSURIZE`, `CHOICE`, `PARTIAL_PAYOFF`, `PAYOFF`, `SETBACK`, `REFRAME`, `AFTERMATH`, `SUSPEND`, `FAIL`, `ABANDON`. A beat describes a change, agency, and evidence; it is not a repeated label.

## Emotion weave

Allowed types are `PARALLEL_ONLY`, `SHARED_EVENT`, `CAUSES_PRESSURE`, `ENABLES_CHOICE`, `CONFLICTS_WITH`, `PAYOFF_OPENS`, and `CO_PAYOFF`. At least two existing member lines must contain the event as a beat. Directed types require `direction`; causal types require `before_after`, `causal_explanation`, and structured `causal_evidence`. Co-occurrence types are not counted as causal.

## Macro emotion arc

Required fields include the macro promise/question, trigger, observed window, member lines, story/plot mappings, progression, independent payoff contract, irreversible state change, current status, and next candidates. A paid line cannot automatically close a macro arc.

## Arc handoff

Required fields include distinct from/to macro IDs, trigger, bridge type, causal bridge, new reader expectation, both entry statuses, an independent prior-payoff check, overlap flag, conclusion, and structured handoff evidence. Conclusions are `OBSERVED_OVERLAP`, `OBSERVED_SEQUENTIAL`, `CANDIDATE_UNVERIFIED`, or `NO_EVIDENCE`.

## Provenance and review

The manifest freezes a Git commit and hashes each declared source blob. `REFERENCE_RESOLVED` only means referenced QA records were found. `SOURCE_TEXT_VERIFICATION_PARTIAL` must be retained when chapter source fingerprints are unavailable. Machine validation never grants semantic approval or production promotion.

Run:

```text
python skills/novel-dna-mining-suite/scripts/core/validate_emotion_arc_research.py <pilot-directory>
```
