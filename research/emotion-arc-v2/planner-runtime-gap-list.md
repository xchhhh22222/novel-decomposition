# Planner E2/E3 runtime capability gaps

Disposition: `PLANNER_RUNTIME_INTEGRATION = NOT_VERIFIED`.

## Executable check

The existing production command was run against the hypothetical fixture:

```text
python skills/novel-creation-planner/scripts/validate_emotion_creation.py research/emotion-arc-v2/fixtures/hypothetical-demon-family/emotion-arc-draft.json
```

Actual result: `ok=false`. The validator requires production `schema_version=1`, `design_mode=EMOTION_FIRST`, an absolute production `shared_library_root`, and production `emotion_patterns`, `materials`, and `options`. The research fixture intentionally supplies none of those claims.

## Missing runtime capabilities

1. No production schema fields or migration for E2 macro arcs, E3 weave records, handoff contracts, or active-state packets.
2. No Planner command/loader that inserts E2/E3 between E1 and M0 while preserving existing E0/E1/M0/D1–D4 execution.
3. No automated material retrieval that consumes emotion-derived functional slots, selects source candidates and records compatibility decisions.
4. No runtime enforcement that A and B keep independent settlement contracts or that B cannot cancel A.
5. No bridge from the research emotion-arc validator into production Planner validation.
6. No execution engine that emits or updates the proposed active-state packet.
7. No end-to-end regression proving an E2/E3 plan can continue through the existing nine-stage Story Spine and downstream climax/architecture steps.

## What is verified

- The fixture derives character, institution, ability and object slots from emotion/payoff needs before naming source candidates.
- Source candidates carry repository/commit/path/ID, abstract use and compatibility gaps.
- Macro A and B have independent payoff contracts, and the handoff retains A's contract.
- The existing nine Story Spine stages are fully represented for both arcs.
- `OBSERVED_SOURCE` research examples and `ORIGINAL_DESIGN` fixture records are explicitly separated.

These are document/fixture checks, not automated Planner execution.
