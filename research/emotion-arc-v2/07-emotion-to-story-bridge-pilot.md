# NOVA V2 — Emotion-to-Story Bridge Pilot

Status: `candidate / HOLD / STOP_FOR_INDEPENDENT_REVIEW`.

This pilot addresses the gap left by the Skill Integration Pilot: the Planner now consumes the real BOOK_001 emotion index and associated EL/EW/MA/AH records before composing candidates, and real 02–09 material choices are attached only where they change a story action or payoff. It does not modify canonical data, production schemas, RMF cards, frozen packages, Story Spine definitions or novel prose.

## 1. Sparse input and execution

The frozen `SPARSE_EMOTION_BRIEF` contains only:

- genre: 玄幻 / 高武;
- expectation: a weak protagonist ultimately becomes able to protect family;
- contour: `DOWN → DOWN → UP`;
- required weave dimensions: family protection, growth cost, relationship agency and long-term faction pressure;
- long-form rule: a later macro promise may open before the old one pays, but cannot cancel the old contract.

It contains no monster, character, power, object, faction, concrete conflict, story node, macro arc or next-arc theme. The runner rejects any such prefill.

Executed entry:

```text
python skills/novel-creation-planner/scripts/run_emotion_story_bridge_pilot.py --brief research/emotion-arc-v2/fixtures/sparse-family-protection/sparse-brief.json --semantic-composition research/emotion-arc-v2/fixtures/sparse-family-protection/semantic-composition.json --emotion-library ../nova-material-library/research/emotion-arc-v2/skill-integration/book001-derived --material-snapshot-repo ../source-stage4-readonly --material-snapshot-commit 1e10e6e3ffb70eda94a400073155fd89db724ce9 --material-package-subdir packages/shared-dna-library/v1.0.0 --output-dir research/emotion-arc-v2/fixtures/sparse-family-protection/runtime-output --force
```

Result: structural/source/state/contract gates PASS. This is not a literary-quality PASS.

## 2. Actual emotion-library consumption

The deterministic retrieval resolved all six BOOK_001 emotion lines, all thirteen observed weave candidates, both macro candidates and `AH:BOOK_001:001`. Each result includes source book/commit/file/line/hash, similarity reason, transferable abstraction and limitations.

The semantic composer then cited only retrieved records:

| Candidate | EL records actually used | EW records actually used | MA/AH records actually used |
| --- | --- | --- | --- |
| A — 九灯旧巷 | EL001 family, EL002 growth, EL005 relationship, EL003 institution | EW001, EW006, EW013 | MA001, MA002, AH001 |
| B — 背山迁途 | EL001 family, EL002 growth, EL005 relationship, EL003 institution | EW007, EW006, EW008 | MA001, MA002, AH001 |

`AH001` is used only as an overlap warning/reference. Both candidates keep dominance transfer at `CANDIDATE_UNVERIFIED`; observed overlap is not represented as a successful handoff template.

## 3. Two causally different original candidates

### Candidate A — 九灯旧巷

A demoted ward-household apprentice must repair a fixed neighborhood defense system. The conflict is public-defense fuel and repair authority captured by vested interests. His ability reads broken ward patterns and trades meridian burns for short re-engraving. Family members know the lamp-link order and force him to choose between protecting one household and widening the defense. Public review and repair qualification make protection observable and institutional rather than a private combat win. The next arc opens from a discrepancy between fuel batches and registration records, without disclosing the supplier chain.

### Candidate B — 背山迁途

A household excluded from safe-migration quotas must earn actual passage. The conflict is monopoly over routes and quotas rather than repair of a fixed home. The protagonist freezes part of his cultivation channel to create a capacity-limited road anchor, while a migrant council controls convoy order and may veto resource use. Protection succeeds only if the family and other migrants become decision-makers in the convoy. The next arc opens when the officially safe route contradicts old road markers, without revealing who altered the route or why.

The two candidates differ in central conflict, ability/cost logic, relationship topology, institution engine and next-arc trigger; the validator rejects equal causal signatures even if titles and nouns differ.

## 4. Material selection, rejection and adaptation

Both candidates derive eight functional slots before querying 02–09. Every accepted source carries frozen commit/path/line/hash and a resolved internal component when one is selected. Every adapted slot records an `ORIGINAL_DESIGN` bridge and ability/resource/world/character compatibility checks.

| Candidate | Module | Decision and source | Actual use |
| --- | --- | --- | --- |
| A | 02 | adapt `GF:BOOK_009` | turns pattern reading into a cost-bearing repair choice; does not import source names or its connected event chain |
| A | 03 | adapt `WB:BOOK:BOOK_001` | supplies scarcity/registration pressure for the ward system |
| A | 04 | adapt `CS:BOOK:BOOK_009` | makes craft proof and combat proof share a bounded interface |
| A | 05 | adapt `HEROINE:BOOK_008:时雨晴` | maps independent agency to family co-operation and veto, not romance copying |
| A | 06 | adapt `PL:BOOK_008` | maps qualification → resource access → public result |
| A | 07 | adapt `OP:BOOK:BOOK_001` | converts immediate household need into an executable task |
| A | 08 | adapt `AR:BOOK:BOOK_009` | organizes home-defense pressure into a staged settlement |
| A | 09 | adapt `PM:BOOK:BOOK_009` | makes public re-pricing/review change protection rights |
| B | 02 | adapt `GF:BOOK_004` | maps bounded burden transfer to a costly road anchor |
| B | 03 | adapt `WB:BOOK:BOOK_006` | supplies contested commons and route-allocation pressure |
| B | 04 | `ORIGINAL_DESIGN` | creates shared-burden physiology because the retrieved personal-domain system has a hard interface conflict |
| B | 05 | adapt `CF:BOOK:BOOK_006` | makes household organizers and the migrant council real decision-makers |
| B | 06 | adapt `PL:BOOK:BOOK_006` | maps organization under real loss into convoy formation |
| B | 07 | adapt `OP:BOOK:BOOK_006` | opens with scarce starting assets without preassigning the solution |
| B | 08 | adapt `AR:BOOK:BOOK_006` | turns an external route problem into a negotiated contract |
| B | 09 | adapt `PM:BOOK:BOOK_006` | delegates autonomy so the protagonist cannot solve migration alone |

Retained real negative decisions:

- `GF:BOOK_005` future-premonition was retrieved and rejected for A: information advantage does not satisfy an earned, cost-bearing protective output and would front-load knowledge instead of growth proof.
- `CS:BOOK:BOOK_006` was retrieved and rejected for B: its personal-domain authority interface conflicts with bodily, shared-burden migration. The slot remains visibly original rather than forcing an 8/8 source hit.

The runtime maps each material use to named story nodes with a node-specific role and effect. It does not attach all eight IDs to every Story Spine stage; doing so is a regression failure.

## 5. State, macro contracts and 50-chapter shape

Both enhanced candidates use only `NOT_OPENED / OPEN / ACTIVE / PARTIALLY_PAID / PAID / HOLD`. A state transition may add reader knowledge only when the same node lists the reveal. Research states are labeled `PLANNED_RESEARCH_STATE_NOT_OBSERVED`.

Each candidate has four independent emotion lines and payoff domains: family safety, costly capability, relationship agency and institutional/faction pressure. Each also preserves two independent macro settlement contracts. Macro B opens at node 6 while Macro A remains unpaid; Macro A pays at node 8. The handoff withholds culprit, full motive and final institutional conclusion, and repeats Macro A's contract verbatim so the new mystery cannot cancel it.

Both paths cover chapters `1–10`, `11–25`, `26–40`, and `41–50`, retain the exact nine-stage Story Spine, and list explicit chapter-51+ continuation conditions.

## 6. Fair legacy comparison

Legacy and enhanced runs share the exact brief hash `64d5a97605344da6a19e04e73ba4cc6285b8c200ee3945a35ba2b11e0241cc4e`. Legacy receives the same semantic freedom, two options, real 02–09 access, seven causal nodes per option, four reader expectations, four chapter phases, continuation conditions and the full Story Spine. It is not weakened to make E2/E3 look better.

Observed behavior:

- both paths can construct coherent multi-actor plots and credible early next-arc triggers;
- E2/E3 makes source-backed expectation selection, line state, independent payoff contracts, overlap timing and old-contract preservation machine-checkable;
- enhanced options use nine explicit causal nodes versus seven in the paired legacy plans, but this count is diagnostic, not a quality verdict;
- the metrics do not prove originality, reader response, suspense quality or overall superiority.

Conclusion: `E2_E3_EXPLICIT_OBLIGATION_TRACKING_OBSERVED`; creative quality remains `PENDING_INDEPENDENT_REVIEW`.

## 7. Independent semantic review and retained failures

Reviewers must still judge whether abstractions avoid copying source event chains; relationship actors genuinely alter feasible choices; payoffs are emotionally visible and independent; both adaptation bridges are compatible; the next-arc clue does not stall; and chapters 51+ can extend causally.

Regression failures cover:

- unretrieved/fake emotion record cited as source;
- knowledge added before its trigger node;
- new arc cancelling the old contract;
- every material attached to every node;
- two options sharing one causal signature with renamed surfaces;
- a sparse brief prefilled with a monster or other story fact;
- future-premonition retained as a documented rejection and an incompatible system retained as an original-design gap.

## 8. Boundaries and status

- BOOK_001 derived data remains candidate/HOLD; R3 source audit and all prior semantic HOLDs remain intact.
- `AH001` complete dominance transfer remains unverified.
- Material adaptation has deterministic provenance and interface checks, but needs independent semantic review.
- No canonical, production package, formal Planner schema, RMF card, main branch or novel manuscript was changed.

`EMOTION_LIBRARY_CONSUMPTION = EXECUTED_RESEARCH`

`MATERIAL_ADAPTATION = REVIEW_REQUIRED`

`CREATIVE_QUALITY = PENDING_INDEPENDENT_REVIEW`

`PRODUCTION_PROMOTION = NOT_RUN`

`STOP_FOR_INDEPENDENT_REVIEW`
