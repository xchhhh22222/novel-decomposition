# Emotion-to-Story Bridge — sparse research route

Use this route only for an explicitly authorized Emotion Arc V2 research pilot. It consumes the existing candidate/HOLD emotion package; it does not activate that package or replace the Planner's production schema.

## Inputs and boundaries

`SPARSE_EMOTION_BRIEF` may contain genre, reader expectation, coarse emotion contour, required weave dimensions and a long-form overlap requirement. It must not prefill characters, monsters, factions, powers, objects, conflicts, story nodes, macro arcs or a next-arc theme.

Keep three layers separate:

1. deterministic retrieval returns real EL/EW/MA/AH IDs with provenance, similarity hints, transferable abstractions and limitations;
2. a semantic composer proposes original story candidates and material functions;
3. deterministic validation resolves every cited emotion/material source, checks causal/state/contract invariants and retains human review.

Python is not expected to understand literature by keywords alone. A semantic model may compose candidates, but its citations are untrusted until the deterministic resolver confirms they were actually retrieved.

## Executable entry

```text
python scripts/run_emotion_story_bridge_pilot.py \
  --brief <sparse-brief.json> \
  --semantic-composition <model-authored-candidate.json> \
  --emotion-library <book001-derived> \
  --material-snapshot-repo <frozen-material-repo> \
  --material-snapshot-commit <full-commit> \
  --material-package-subdir packages/shared-dna-library/v1.0.0 \
  --output-dir <research-output> --force
```

The run must produce at least two causally distinct enhanced candidates and two fair legacy candidates from the exact same brief. The legacy path remains capable of designing a coherent plot, using 02–09 materials, preserving the nine-stage Story Spine and planning chapters 1–50; it simply lacks E2/E3 library consumption and explicit emotion state/contract machinery.

## Emotion-library consumption

`search_emotion_arc_library.py` validates the package and searches reader-expectation dimensions before expanding to linked weaves, macro arcs and handoffs. Every use records:

- actual record ID and source package commit/file/line/hash;
- why it resembles the requested expectation;
- the abstract part that may transfer;
- limits, including candidate/HOLD and semantic-review status.

Observed overlap may guide a candidate, but an unverified handoff must remain `CANDIDATE_UNVERIFIED`. Never treat source status, retrieval score or an observed co-occurrence as proof of successful creative transfer.

## State and contract rules

Allowed states are `NOT_OPENED`, `OPEN`, `ACTIVE`, `PARTIALLY_PAID`, `PAID`, and `HOLD`. Reader knowledge may be added only at a node that reveals it. A new macro arc may open before the old arc pays, but it cannot disclose all answers or alter/cancel the old settlement contract. Planned research states are labeled `PLANNED_RESEARCH_STATE_NOT_OBSERVED` and are not novel facts.

## Material assembly

Derive a concrete functional slot before each 02–09 search. Each selected/adapted material must name the story node where it acts and how it changes a character choice, cost, causal transition or payoff. Record ability/resource/world/character checks, cross-material conflicts and any `ORIGINAL_DESIGN` adaptation bridge. Retain real rejections. Never attach every retrieved ID to every Story Spine node or optimize for 8/8 selection.

## Evaluation and stop

Run `validate_emotion_story_bridge.py` and `evaluate_emotion_story_bridge.py`. Compare paired legacy/enhanced outputs by distinguishable expectations, choices changed by emotion lines, independent payoffs, credible overlap triggers, node-local material effects, incompatibilities, 50-chapter staging and continuation conditions. File counts, hit rates and identical Story Spine labels are not quality evidence.

Structural success may report `EMOTION_LIBRARY_CONSUMPTION=EXECUTED_RESEARCH`. Material adaptation remains `REVIEW_REQUIRED`; creative quality remains `PENDING_INDEPENDENT_REVIEW`; production promotion remains `NOT_RUN`.
