# QA and acceptance

## Machine gates

`validate_emotion_arc_research.py` reports structural, source-reference, promise-crosswalk, claim-binding, weave-evidence, and macro/handoff gates. Under `CLAIM_EVIDENCE_V2`, a successful binding gate says only that each claim reaches a real canonical record field. Causal and literary meaning remains `NEEDS_SEMANTIC_REVIEW` until a reviewer records a decision.

The 21-case negative suite also covers four R2 failure modes: a real citation paired with a false causal explanation; co-occurrence presented as causation; a newly opened line presented as a qualified macro; and a new line used to cancel the prior macro payoff. The first two intentionally return `NEEDS_SEMANTIC_REVIEW` rather than fabricated PASS. The latter two are structural FAILs.

## Acceptance state meanings

- `PASS`: the specific machine gate found no structural/reference violation.
- `HOLD`: the format is usable, but an explicit evidence or review gap remains.
- `FAIL`: a contract violation exists.
- `PENDING_INDEPENDENT_REVIEW`: no literary or architecture acceptance has been granted.
- `NEEDS_SEMANTIC_REVIEW`: references and fields resolve, but the interpretation is outside machine authority.

Exit code zero never means literary PASS, active material publication, creation approval, or production readiness.

## Pilot stop gate

Delivery ends after both research branches are committed and pushed, new tests pass, legacy tests regress cleanly, the real BOOK_001 pilot report is preserved with honest HOLDs, and the final report says `STOP_FOR_INDEPENDENT_REVIEW`.
