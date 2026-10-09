# Architecture contract

This pilot implements the V2 proposal without changing its ontology.

## Objects

- `EMOTION_LINE` tracks one reader expectation with its own observable payoff condition across chapters.
- `EMOTION_WEAVE` records a shared event or evidenced relation among at least two independent lines.
- `MACRO_EMOTION_ARC` organizes several line changes around a stage-level reader promise; it is not a renamed story arc.
- `ARC_HANDOFF` records the explicit bridge and settlement status between two macro emotion arcs.
- `promise-resolution.jsonl` is a derived uncertainty-preserving crosswalk. It never edits canonical promises.

All observed-source records use schema version 1, stable type-specific IDs, `status=candidate`, `qa_status=HOLD`, `origin_kind=OBSERVED_SOURCE`, a frozen snapshot reference, chapter evidence, gaps, confidence, and an independent semantic-review slot.

## Separation rules

1. Same emotion word, person, chapter, or numeric suffix never proves identity.
2. Chapter evidence proves that an event record exists and passed source QA; machine validation does not prove the interpretation.
3. Directed weave types need direction, a before/after state, a causal explanation, and structured causal evidence. Non-causal types must not be counted as causal.
4. A paid child line does not close its macro arc. A paid macro needs evidence for its own payoff criterion.
5. An overlapping handoff needs verified temporal overlap. If the source window cannot show prior-arc settlement, the handoff remains `CANDIDATE_UNVERIFIED` and the gate is `HOLD`.
6. Research data cannot be promoted by changing a status string or by a validator exit code.

The normative field contract is published at `skills/novel-dna-mining-suite/references/core/emotion-arc-research-contract.md`.
