# Emotion Arc V2 — Skill Integration Pilot

Status: `RESEARCH_EXECUTABLE / candidate / HOLD / STOP_FOR_INDEPENDENT_REVIEW`.

This pilot connects the accepted R3 research contract to the decomposition Skill and Creator Planner without changing production schemas, canonical data, RMF cards, the active shared package or Story Spine definitions.

## 1. Decomposition Skill entry

```text
python skills/novel-dna-mining-suite/scripts/core/build_emotion_arc_skill_package.py --pilot-root <material-repo>/research/emotion-arc-v2/pilot-book001 --source-repo <frozen-material-snapshot> --output <material-repo>/research/emotion-arc-v2/skill-integration/book001-derived --force
```

The command consumes the existing V2 pilot plus its R3 source-text audit, invokes the existing V2 validator, and emits the reviewed records plus a searchable `reader-expectation-index.jsonl`. Actual run: 6 lines, 13 weaves, 2 macro arcs, 1 handoff and 6 expectation-index rows. Structural/source-reference/source-text-audit/claim-binding gates pass; crosswalk and macro-handoff remain HOLD, and causal semantics remain `NEEDS_SEMANTIC_REVIEW`.

## 2. Emotion-first retrieval and assembly

```text
python skills/novel-creation-planner/scripts/run_emotion_arc_v2_research.py --brief research/emotion-arc-v2/fixtures/hypothetical-demon-family/pilot-input.json --output-dir research/emotion-arc-v2/fixtures/hypothetical-demon-family/runtime-output/e2-e3-enabled --material-snapshot-repo <frozen-material-repo> --material-snapshot-commit 1e10e6e3ffb70eda94a400073155fd89db724ce9 --material-package-subdir packages/shared-dna-library/v1.0.0 --force
```

The command derives eight functional slots first, then calls the existing 02–09 search interface. It exports manifest-declared Git blobs directly to preserve exact hashes on Windows and leaves the integrity gate unchanged. The fixture resolved 8/8 real candidates with commit/path/line/record/hash provenance. All selections remain `CANDIDATE_NEEDS_SEMANTIC_REVIEW`; BOOK_005 occupying four slots is a reported source-concentration risk, not an automatic PASS.

## 3. E2/E3 and Story Spine

The executed plan retains E0/E1/M0/D1–D4 and inserts:

- E2: two independent macro arcs and settlement contracts;
- E3: four independent emotion lines, three causal weave candidates and one overlap/handoff candidate;
- active state: both macro contracts remain pending, and B cannot cancel A;
- action layer: all nine existing Story Spine stages remain in the original order.

`AH:PILOT:A-B` is deliberately `CANDIDATE_UNVERIFIED / HOLD`; the adapter does not machine-approve dominance transfer.

## 4. Old-path regression

```text
python skills/novel-creation-planner/scripts/run_emotion_arc_v2_research.py --brief research/emotion-arc-v2/fixtures/hypothetical-demon-family/pilot-input.json --output-dir research/emotion-arc-v2/fixtures/hypothetical-demon-family/runtime-output/legacy-disabled --disable-emotion-arcs --force
```

The disabled output contains E0/E1/M0/D1–D4 and exactly nine Story Spine stages, with no E2/E3 or material assembly fields. Existing production validators are unchanged.

## 5. Capability evaluation

The evaluator compares behaviors, not file counts. For this fixture it observes improved explicitness in four independent payoff contracts, relationship agency attached to action choices, preservation of both macro obligations, causal continuation entry, function-first use of all eight material modules, and unchanged Story Spine stage names. The conclusion is `MATERIAL_IMPROVEMENT_OBSERVED`, still under `NEEDS_INDEPENDENT_REVIEW`.

## 6. Non-promotion boundaries

- No novel prose was generated.
- No existing research fixture was promoted by status change; the runtime begins from a separate `pilot-input.json` and produces new research output.
- No canonical, production schema, RMF, active package or main branch was modified.
- R3 HOLDs, source-text conflicts and `AH001` unverified dominance transfer remain intact.
- Production blockers are tracked in `planner-runtime-gap-list.md`.

## 7. Executed quality gates

| Check | Actual result |
| --- | --- |
| Existing Emotion Arc V2 validator regression | 24/24 PASS |
| New Skill Integration adapter tests | 7/7 PASS, including explicit material-gap HOLD and disabled legacy path |
| Actual BOOK_001 derivation | structural/reference/source-text-audit/claim-binding PASS; semantic and handoff HOLD retained |
| Actual enhanced Planner plan + frozen source verification | PASS; 8/8 source rows resolved; semantic review pending |
| Actual disabled Planner path | PASS; legacy compatibility PASS; no E2/E3 leakage |
| DNA candidate search regression | PASS |
| Shared-package integrity/status regression | 10/10 PASS, including tamper/missing/path-escape failures |
| Mechanism-library search regression | PASS under forced UTF-8 process mode on Windows |
| Existing creation plan validator | 13/13 PASS |
| Existing emotion-creation validator | 17/17 PASS |
| Existing V1.2 artifact validators | 6/6 PASS |
| R3 source-fact regressions | 6/6 PASS |

The first mechanism-library test attempt inherited a non-UTF-8 Windows console code page and failed while decoding subprocess output; rerunning unchanged code with `PYTHONUTF8=1` passed. No validator, fixture or acceptance threshold was changed to obtain that result.
