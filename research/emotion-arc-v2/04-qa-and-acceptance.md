# QA and acceptance

## Machine gates

`validate_emotion_arc_research.py` reports structural, source-reference, source-text-audit, promise-crosswalk, claim-binding, weave-evidence, and macro/handoff gates. Under `CLAIM_EVIDENCE_V2`, a successful binding gate says only that each claim reaches a real canonical record field. When a targeted raw-text audit marks that field `CONTRADICTED`, the binding must acknowledge the matching audit record. Causal and literary meaning remains `NEEDS_SEMANTIC_REVIEW` until a reviewer records a decision.

The 24-case suite also covers the four R2 failure modes and the R3 source-audit regressions. A real citation paired with a false causal explanation and co-occurrence presented as causation intentionally return `NEEDS_SEMANTIC_REVIEW` rather than fabricated PASS. A newly opened line presented as a qualified macro and a new line used to cancel the prior payoff are structural FAILs. A Git blob OID mislabeled as `source_text_blob_sha256`, or use of a contradicted canonical field without its audit acknowledgement, is also a FAIL; acknowledgement restores structural validity but leaves semantics pending.

## Acceptance state meanings

- `PASS`: the specific machine gate found no structural/reference violation.
- `HOLD`: the format is usable, but an explicit evidence or review gap remains.
- `FAIL`: a contract violation exists.
- `PENDING_INDEPENDENT_REVIEW`: no literary or architecture acceptance has been granted.
- `NEEDS_SEMANTIC_REVIEW`: references and fields resolve, but the interpretation is outside machine authority.

Exit code zero never means literary PASS, active material publication, creation approval, or production readiness.

## Pilot stop gate

Delivery ends after both research branches are committed and pushed, new tests pass, legacy tests regress cleanly, the real BOOK_001 pilot report is preserved with honest HOLDs, and the final report says `STOP_FOR_INDEPENDENT_REVIEW`.
