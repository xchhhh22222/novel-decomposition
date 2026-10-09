# QA and acceptance

## Machine gates

`validate_emotion_arc_research.py` reports structural, source-reference, crosswalk, declared weave-evidence, and macro/handoff gates. It also reports layered source trust and fixed `PENDING_INDEPENDENT_REVIEW` / `NOT_GRANTED` / `NOT_RUN` decisions.

The negative suite covers duplicate IDs, the known P001 mismatch, honest unresolved mappings, invalid members, unsupported causal declarations, missing and out-of-scope events, unsupported paid macros, child/macro separation, false overlap, incomplete handoffs, pending prior payoff, forbidden promotion, origin-layer conflict, and provenance overclaim. Same-label lines are retained independently. Handoff semantics remain a human review item.

## Acceptance state meanings

- `PASS`: the specific machine gate found no structural/reference violation.
- `HOLD`: the format is usable, but an explicit evidence or review gap remains.
- `FAIL`: a contract violation exists.
- `PENDING_INDEPENDENT_REVIEW`: no literary or architecture acceptance has been granted.

Exit code zero never means literary PASS, active material publication, creation approval, or production readiness.

## Pilot stop gate

Delivery ends after both research branches are committed and pushed, new tests pass, legacy tests regress cleanly, the real BOOK_001 pilot report is preserved with honest HOLDs, and the final report says `STOP_FOR_INDEPENDENT_REVIEW`.
