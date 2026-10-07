# V1.7.0 Mechanism Family Discovery — End-to-End Execution Workflow

This document is the operational SOP for the V1.7.0 reusable mechanism-family pipeline. It records the production-proven sequence that was actually used to move from single-book DNA assets to audited cross-book mechanism families and, optionally, to composition-ready production assets.

It is **not** a target-family-count recipe. The reference implementation happened to stabilize a finite set of families; future runs may produce more, fewer, or zero new families. Semantic correctness, boundary quality, provenance, and independent support are the success criteria.

## 0. Core principle

V1.7 does **not** perform one-shot semantic clustering.

The default architecture is:

```text
freeze input
→ extract mechanism cards
→ normalize readiness
→ calibrate purposeful pairs
→ pilot a small number of family hypotheses
→ stress family boundaries
→ validate the lane
→ expand by independent family-definition tests
→ seal the domain
→ optional cross-domain ontology/composition
→ assemble FULL_LIBRARY
→ optional production promotion
```

Keywords, embeddings, dictionaries, lexical overlap, graph connectivity, connected components, and single-link chaining are retrieval aids only. They never decide membership.

The semantic comparison unit is:

```text
trigger/input
→ actor/operator
→ operation chain
→ target
→ state/output change
→ recurrence/feedback
→ termination/failure boundary
```

Every member is tested independently against a family definition. A chain such as `A SAME B` and `B SAME C` does **not** admit C automatically.

## 1. Step 0 — freeze the run

Before semantic work:

1. freeze repository / source HEAD;
2. assign a unique run ID;
3. declare domain and comparison lane;
4. freeze the input population;
5. record the pinned skill/validator commit;
6. record allowed source artifacts and forbidden outputs;
7. require a clean working tree;
8. stop if the expected HEAD changed.

Minimum control fields:

```text
run_id
domain
comparison_lane
starting_head
input_population
skill_commit
validator_source
allowed_sources
forbidden_outputs
```

Historical cluster IDs, old memberships, old family answers, and prior automatic clusters may be used only as `legacy_reference`, never as semantic truth.

## 2. Step 1 — MECHANISM_CARD_EXTRACTION

Convert eligible single-book material into comparison cards.

Each card must preserve at least:

```text
source_primary_object
trigger_or_input
actor_or_operating_subject
core_operation_chain
target_object
resulting_state
feedback_or_growth_loop
failure_or_stop_condition
primary_evidence_refs
corroborating_evidence_refs
comparison_lane
```

Do not cluster at this stage.

### Domain-specific comparison forms

Relationship engine:

```text
action / authority / information / resource interface
→ interaction
→ relationship-state-variable change
→ why the interaction recurs
```

GF_CORE:

```text
input/resource
→ deterministic conversion
→ output/growth asset
→ reinvestment loop
→ limitation/cost
```

GF_ABILITY:

```text
trigger/access condition
→ actor/controller
→ ability operation/transformation
→ target
→ output/state change
→ hard limitation/cost/counterplay
→ reuse/growth mode
```

Plotline progression engine:

```text
current state
→ progress mechanism
→ state change
→ why the next plot entry opens
```

## 3. Step 2 — READINESS_NORMALIZATION

Classify every card before comparison.

Allowed readiness:

```text
READY
READY_WITH_BOUNDARY
HOLD_CORE_UNKNOWN
```

A core unknown affecting trigger, operator, transformation, target, state change, main result, major limitation, recurrence, or termination forces `HOLD_CORE_UNKNOWN`.

Peripheral unknowns do not automatically force HOLD.

Output a complete population accounting:

```text
population_total
eligible_ready
eligible_ready_with_boundary
hold_core_unknown
```

HOLD cards remain visible in inventory but cannot support stable family identity.

## 4. Independence audit — mandatory before family support counting

The pipeline must distinguish:

```text
card count != independent implementation count
```

Audit at least:

```text
source_primary_object
parent_child_relations
underlying_mechanism_id
evidence overlap
same-book dependency
same causal episode
projection/copy lineage
```

The following do **not** automatically count as separate independent implementations:

- parent/child projections of one mechanism;
- copied abilities produced by one copy system;
- composite cards that merely contain the same component;
- evolution stages of the same mechanism;
- multiple views of the same causal episode;
- same-book derivative records with dependent evidence.

A family cannot become stable by inflating support with dependent cards.

## 5. Step 3 — PAIR_CALIBRATION

Purpose: calibrate semantic judgment before creating families.

Default scale: 10–15 deliberately selected pairs.

Required calibration categories:

```text
OBVIOUS_SAME
PARAPHRASE_EQUIVALENT
SAME_SURFACE_DIFFERENT_MECHANISM
LIKELY_SUBTYPE
ANALOGOUS
DIFFERENT
BOUNDARY_OR_HOLD
```

Allowed decisions only:

```text
SAME_MECHANISM
SUBTYPE
ANALOGOUS
DIFFERENT
HOLD
```

Each pair review must separate:

1. mechanism core;
2. downstream effect;
3. transferable subtype dimension, if any;
4. evidence basis;
5. independence status.

At this stage family previews may only be:

```text
HYPOTHESIS
HOLD
```

Never emit `STABLE`.

Any boundary material is preview-only and must be marked:

`PREVIEW_ONLY_NOT_STAGE_GATE_EVIDENCE`.

### Human stop

After PAIR_CALIBRATION:

`STOP_FOR_HUMAN_REVIEW`

Do not continue until the semantic reviewer approves pair calibration.

## 6. Step 4 — FAMILY_PILOT

Purpose: test only a small number of candidate family definitions.

Default: at most 2–3 new hypotheses; zero is valid.

For each candidate family define:

```text
family_name
core_mechanism_definition
one_sentence_core
minimum_definition
hard_invariants
allowed_variations
exclusion_boundary
termination_condition
why_it_recurs
```

Then independently test each candidate card:

```text
PASS_SAME
PASS_SUBTYPE
OUTSIDE_ANALOGOUS
OUTSIDE_DIFFERENT
HOLD
```

Family membership is based on the definition, not the pair graph.

A pilot may remain HOLD because of insufficient cross-book independent support. That is a valid result.

### Human stop

After FAMILY_PILOT:

`STOP_FOR_HUMAN_REVIEW`

Do not claim boundary stress has passed.

## 7. Step 5 — BOUNDARY_STRESS_TEST

This is the **first** stage where `STABLE` may be emitted.

Actively search for plausible false positives:

- same keywords;
- same genre surface;
- same final result;
- same actor label;
- same resource label;
- same feedback shape;
- same growth outcome;
- same “verification / qualification / investigation” vocabulary.

A stable family must demonstrate:

1. complete trigger/transformation/state-change/recurrence/termination semantics;
2. positive independent support from multiple books;
3. per-member definition tests;
4. at least one plausible negative boundary;
5. ANALOGOUS references isolated outside membership;
6. no multi-family positive-membership conflict;
7. no definition drift introduced to rescue weak members.

Stable support may follow the contract’s Pattern A or Pattern B. One canonical implementation plus only one subtype remains HOLD unless explicitly approved otherwise.

### Human stop

After BOUNDARY_STRESS_TEST:

`STOP_FOR_HUMAN_REVIEW`

For a lane that previously had `CALIBRATION_REQUIRED`, record explicit lane validation before expansion:

`APPROVE_LANE_VALIDATION:<domain>:<lane>`

## 8. Step 6 — DOMAIN_EXPANSION

Once a family is stable, expansion is **not** a new all-pairs recluster.

For each eligible card:

```text
candidate retrieval
→ independent frozen-family definition test
→ SAME / SUBTYPE / ANALOGOUS / OUTSIDE / HOLD
```

Default method:

`N eligible cards × K stable families`

not:

`N × N full similarity graph`.

Expansion must also include:

- held-family register;
- residual mechanism assessment;
- recurring same-book hints;
- dependency / copied-output audit;
- composite no-split register where applicable;
- definition drift report;
- fingerprint drift report;
- multi-family conflict report;
- standard disposition accounting.

If unmatched cards form a credible recurring mechanism, do **not** mint a family inside expansion. Return that mechanism to:

```text
PAIR_CALIBRATION
→ FAMILY_PILOT
→ BOUNDARY_STRESS_TEST
```

### Human stop

After every DOMAIN_EXPANSION batch:

`STOP_FOR_HUMAN_REVIEW`

## 9. Step 7 — DOMAIN_FULL

DOMAIN_FULL is a seal/freeze stage, not another research pass.

Requirements:

- prior stages completed and human-approved;
- at least one approved expansion;
- explicit `APPROVE_DOMAIN_FULL`;
- every card has a final disposition;
- stable-family definitions frozen;
- family fingerprints frozen;
- held families isolated;
- residual candidates explicitly accounted for;
- no unresolved multi-family positive conflict;
- no forced coverage.

Use an explicit distribution:

```text
SAME
SUBTYPE
ANALOGOUS
DIFFERENT
HOLD
UNCLUSTERED
```

Do not collapse these into ambiguous counters such as `hold_unclustered_count`.

If PASS:

```text
DOMAIN_FULL = PASS
PRODUCTION_CLUSTERING_READY = YES
FAMILY_DEFINITIONS = FROZEN_READ_ONLY
```

### Human stop

Before running DOMAIN_FULL require `APPROVE_DOMAIN_FULL`. After completion, stop again for human review before any library-level work.

## 10. Step 8 — optional CROSS_DOMAIN_ONTOLOGY

This stage is optional and occurs only after stable family inputs exist.

Its purpose is **not** to merge domains.

First normalize one signature per stable family:

```text
trigger_semantics
transformation_semantics
state_variable_changed
feedback_or_recurrence
termination_condition
hard_invariants
exclusion_boundary
```

Cross-domain reviews must separate two independent questions:

Identity:

```text
META_EQUIVALENT
META_SPECIALIZATION_CANDIDATE
STRUCTURAL_ANALOGY
DISTINCT
HOLD
```

Composition:

```text
LEFT_CAN_FEED_RIGHT
RIGHT_CAN_FEED_LEFT
BIDIRECTIONAL_POSSIBLE
NONE
HOLD
```

A composition link exists only when a source family’s actual output/state change can, under a concrete bridge condition, satisfy the target family’s trigger/input.

“Helpful”, “can make the protagonist stronger”, “provides information”, or “often appears together” is insufficient.

Composition never changes family membership.

Every executable link records:

```text
source_family_id
target_family_id
source_output
target_trigger_or_input
bridge_condition
membership_effect = NONE
identity_effect = NONE
```

Family membership before/after ontology must be identical.

### Human stop

Ontology validator PASS still yields a candidate. Require human approval before FULL_LIBRARY consumes it.

## 11. Step 9 — FULL_LIBRARY

FULL_LIBRARY does **not** recluster all cards.

It assembles approved domain assets:

```text
stable family registries
+ held-family index
+ normalized signatures
+ optional ontology concepts
+ composition links
+ source provenance
```

For creation-facing use it may additionally derive:

- composition recipes;
- mechanism slot index;
- composition adjacency index;
- planner dispatch preview.

Derived recipes are **not** semantic evidence.

Each multi-step recipe must pass `CHAIN_COMPATIBILITY_CHECK`:

1. previous output satisfies the next bridge;
2. intermediate output form is not silently changed;
3. bridge conditions can coexist in one story instance;
4. family identity/membership remains unchanged;
5. “helpful” is not substituted for trigger/input.

Recipe provenance must be audited: every referenced link endpoint must match the recipe’s declared family set. If not, drop or HOLD the recipe. Do not invent a new link merely to rescue it.

Before FULL_LIBRARY require:

`APPROVE_FULL_LIBRARY`.

A PASS means the unified candidate production library is ready. It does not by itself authorize active runtime promotion.

## 12. Step 10 — production promotion (post-clustering)

Promotion is outside semantic family discovery but is the final productionization step.

Require explicit:

`APPROVE_PROMOTION`.

Promotion must:

- package approved assets as a versioned distribution;
- preserve semantic payload bytes;
- record artifact SHA-256;
- enforce runtime fail-closed integrity checking;
- keep held families and dropped recipes outside normal retrieval;
- preserve backward compatibility of legacy planner/material paths;
- distinguish staging from active status;
- never treat a repository name or arbitrary directory as an approved runtime root.

Production packaging may change metadata and retrieval indexes. It may not change family semantics, membership, link direction, bridge conditions, or approved recipe semantics.

## 13. Human approval map

The normal control flow is:

```text
PAIR_CALIBRATION
→ HUMAN APPROVAL

FAMILY_PILOT
→ HUMAN APPROVAL

BOUNDARY_STRESS_TEST
→ HUMAN APPROVAL

CALIBRATION_REQUIRED lane
→ APPROVE_LANE_VALIDATION

each DOMAIN_EXPANSION
→ HUMAN APPROVAL

DOMAIN_FULL
← APPROVE_DOMAIN_FULL
→ HUMAN APPROVAL

optional CROSS_DOMAIN_ONTOLOGY
→ HUMAN APPROVAL

FULL_LIBRARY
← APPROVE_FULL_LIBRARY
→ HUMAN APPROVAL

ACTIVE_PROMOTION
← APPROVE_PROMOTION
```

A validator PASS never substitutes for a required human semantic approval.

## 14. Hard STOP conditions

Stop and do not continue when any of the following occurs:

- a stable family core definition materially changes;
- a stable family is widened to rescue an outlier;
- SAME/SUBTYPE lacks primary-object evidence;
- one card becomes positive member of multiple stable families without an explicit conflict resolution;
- historical membership is inherited as the answer;
- ANALOGOUS is counted as membership;
- HOLD_CORE_UNKNOWN is used as positive semantic support;
- connected components / single-link / graph transitivity becomes the decision system;
- UNCLUSTERED is forced into a family;
- a new family is based mainly on names, keywords, or surface wording;
- dependent parent/child/copy/projection records are counted as independent implementations;
- three or more obvious recurring residual mechanisms are ignored without review;
- validator binding is stale after artifact mutation;
- current HEAD differs from the frozen starting state.

## 15. Required validation discipline

Mechanism-family runs use:

`scripts/core/validate_mechanism_family_pipeline.py`

Cross-domain ontology runs use:

`scripts/core/validate_cross_domain_ontology.py`

Validation reports bind at least:

```text
validator_skill_commit
validator_source_sha256
validated_run_id
validated_run_document_sha256
validated_pair_artifact_sha256
validation_execution_id
```

After artifact mutation, rerun validation and produce a new binding. Never reuse an old PASS report.

## 16. V1.7 validated reference implementation

The production-proven V1.7 reference has validated these lanes:

```text
relationship_engine
GF_CORE
GF_ABILITY
plotline_progression_engine
```

They reached DOMAIN_FULL and were subsequently assembled into a production library. This proves the workflow, not a required family count.

Other lanes/modules remain `CALIBRATION_REQUIRED` until they independently complete the same staged process.

## 17. Final rule

The shortest correct V1.7 summary is:

```text
Do not cluster everything first.

Prove pair judgments.
Define a small family.
Stress its boundary.
Freeze the definition.
Test every new card independently.
Seal the domain.
Only then compose domains and package for creation.
```
