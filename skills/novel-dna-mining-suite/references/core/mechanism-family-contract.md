# Reusable Mechanism Family Contract (V1.7.0)

This is the canonical contract for new cross-book mechanism research. It replaces one-shot full semantic clustering as the default architecture, while leaving the V1.6.x semantic recluster contract available for legacy validation only.

The purpose is to establish an auditable answer to “what counts as the same reusable narrative mechanism?” on a small sample before scope expands. It does not prescribe a target family count and does not require every card to be assigned. The production-proven execution SOP is documented in `mechanism-family-workflow.md` in the mining-suite core references; this contract remains the normative semantic and stage-gate authority.

## 1. Stage state machine

New runs use these ordered stages:

```text
MECHANISM_CARD_EXTRACTION
→ READINESS_NORMALIZATION
→ PAIR_CALIBRATION
→ FAMILY_PILOT
→ BOUNDARY_STRESS_TEST
→ DOMAIN_EXPANSION
→ DOMAIN_FULL
→ optional CROSS_DOMAIN_ONTOLOGY
→ FULL_LIBRARY
```

Additional terminal/control states are `HOLD` and `STOP_FOR_HUMAN_REVIEW`. A run must not skip stages. In particular, card extraction cannot jump to `DOMAIN_FULL`, and pair calibration cannot jump to `FULL_LIBRARY`.

Default mandatory stops:

- after `PAIR_CALIBRATION`;
- after `FAMILY_PILOT`;
- after `BOUNDARY_STRESS_TEST`;
- after every `DOMAIN_EXPANSION` batch;
- before `DOMAIN_FULL`, which requires explicit `APPROVE_DOMAIN_FULL`;
- before `FULL_LIBRARY`, which requires explicit `APPROVE_FULL_LIBRARY`;
- before promotion, which requires explicit `APPROVE_PROMOTION`.

Without the corresponding approval:

```text
PLANNER_PROVISIONAL_USE = HOLD
PLANNER_FINAL_MATERIAL_GATE = HOLD
ACTIVE_PROMOTION = NOT_RUN
```

Every run persists an auditable `stage_history`. Each completed predecessor records `stage`, `status=PASS`, a non-empty `artifact_id`, and `human_review=APPROVED` when that stage has a review stop. Stages must remain in legal order; only `DOMAIN_EXPANSION` may repeat, and every expansion requires a unique artifact or batch ID. `DOMAIN_FULL` requires a real approved expansion history record, not a naked success counter. `FULL_LIBRARY` requires an approved `DOMAIN_FULL` history record. `CROSS_DOMAIN_ONTOLOGY` remains optional.

### 1.1 Stage artifact scope

`STAGE_TRANSITION_GATE` proves that predecessors exist. `STAGE_ARTIFACT_SCOPE_GATE` separately proves that the current artifact does not claim semantics belonging to a later stage.

- `PAIR_CALIBRATION` may contain pair records and draft family previews only. Preview families use `family_status=HYPOTHESIS|HOLD`. Any preliminary boundary material must declare `boundary_analysis_status=PREVIEW_ONLY_NOT_STAGE_GATE_EVIDENCE`. It cannot emit `STABLE`, claim `boundary_stress_passed=true`, or record completed `FAMILY_PILOT` / `BOUNDARY_STRESS_TEST` stages.
- `FAMILY_PILOT` may contain hypotheses, HOLD families, and candidate member-definition tests. It cannot claim `boundary_stress_passed=true`, completed boundary stress, or domain expansion.
- `BOUNDARY_STRESS_TEST` is the first stage at which a family may become `STABLE`. A STABLE family must also pass the independent stable-family gate and record `boundary_stress_passed=true`.
- `DOMAIN_EXPANSION` requires approved `PAIR_CALIBRATION`, `FAMILY_PILOT`, and `BOUNDARY_STRESS_TEST` history. Later stages may carry forward an already stable family, but no earlier-stage run may emit operational STABLE status.

The phase name, stage history, and emitted artifact semantics must therefore agree; a correct predecessor list does not excuse a later-stage claim inside an earlier-stage document.

## 2. Default scale safety limits

These are safety defaults, not KPIs:

- first calibration for a new domain or lane: 30–50 mechanism cards, or all available cards when the source population is smaller;
- pair calibration: 10–15 deliberately selected pairs covering obvious SAME, paraphrase equivalence, same surface/different mechanism, likely SUBTYPE, ANALOGOUS, DIFFERENT, and boundary/HOLD;
- first family pilot: at most 2–3 new hypotheses; zero is valid;
- boundary stress: normally 5–10 positive, negative, and boundary cases per family; a smaller nonzero set is allowed only when the sample is too small and the reason is recorded;
- domain expansion: 25–50 cards per batch, followed by `STOP_FOR_HUMAN_REVIEW`;
- `DOMAIN_FULL`: only after at least one successful expansion without major family-definition drift and explicit `APPROVE_DOMAIN_FULL`.

The intended process is “prove a few definitions, then expand,” not “force a few clusters and fill them.” `UNCLUSTERED` and `HOLD` are valid long-term states. Neither 100% assignment nor a target family count is a success metric.

## 3. Mechanism card contract

Every domain card preserves at least these semantics:

```json
{
  "card_id": "",
  "domain": "",
  "comparison_lane": "",
  "source_primary_object": {},
  "trigger_or_input": "",
  "actor_or_operating_subject": "",
  "core_operation_chain": [],
  "target_object": "",
  "resulting_state": "",
  "feedback_or_growth_loop": "",
  "failure_or_stop_condition": "",
  "primary_evidence_refs": [],
  "corroborating_evidence_refs": [],
  "unknown_classification": {
    "core_mechanism_unknowns": [],
    "peripheral_unknowns": []
  },
  "comparison_readiness": "READY | READY_WITH_BOUNDARY | HOLD_CORE_UNKNOWN",
  "derived_commentary": {}
}
```

Specialists may add fields but must not delete these semantics. `source_primary_object` identifies the single-book object whose own evidence must establish the mechanism.

### 3.1 UNKNOWN policy

`CORE_MECHANISM_UNKNOWN` means an unknown can change one or more of: trigger/input, actor/controller, operation/conversion chain, target, state change, main result, major limitation, feedback/growth loop, or termination. Any such unknown forces `comparison_readiness = HOLD_CORE_UNKNOWN` and excludes the card from stable pair or family support.

`PERIPHERAL_UNKNOWN` covers origin lore, ultimate ceiling, an unread ending, later extras, or background details that do not change the running chain. Peripheral unknowns alone do not force HOLD; a sufficiently established core may use `READY_WITH_BOUNDARY`.

The obsolete rule “any UNKNOWN means HOLD” is prohibited.

### 3.2 Evidence isolation

`primary_evidence_refs` must prove trigger, operation, state change, and stop/limit semantics on the primary object itself. `corroborating_evidence_refs` may clarify variation or context, but may not manufacture a missing core mechanism.

`derived_commentary` includes creative commentary such as transferable creation value. It is useful for humans but is not semantic evidence for `SAME_MECHANISM`, `SUBTYPE`, family membership, or ontology identity.

Allowed provenance roles are explicit and separate:

```text
positive_support
negative_boundary
structural_analogy
corroborating_context
composition_reference
legacy_reference
```

## 4. Validated scope and lane isolation

The current validated scope is intentionally narrow:

```text
relationship_engine = FAMILY_DISCOVERY_VALIDATED
GF_CORE = FAMILY_DISCOVERY_VALIDATED
GF_ABILITY = FAMILY_DISCOVERY_VALIDATED
plotline_progression_engine = FAMILY_DISCOVERY_VALIDATED

other character projections = CALIBRATION_REQUIRED
other decomposition modules = CALIBRATION_REQUIRED
```

A shared contract does not validate an unpiloted lane. Ordinary family discovery must not compare objects across lanes or granularities. In particular, `GF_CORE` and `GF_ABILITY` remain separate. Cross-granularity analysis requires an explicitly approved ontology research run and still cannot assign family membership across lanes.

A `CALIBRATION_REQUIRED` lane may execute through `BOUNDARY_STRESS_TEST`. It cannot enter `DOMAIN_EXPANSION`, `DOMAIN_FULL`, or `FULL_LIBRARY` until the run records `APPROVE_LANE_VALIDATION:<domain>:<lane>`.

### 4.1 Relationship engine specialization

A relationship card also preserves `source_actor_sides`, `functional_roles`, `primary_engine_evidence_refs`, and `corroborating_relation_evidence_refs`. Source identities and functional abstractions must not overwrite each other. Names, titles, and social labels are not functional roles by themselves.

Multiple projections of the same underlying relation must declare:

```text
projection_semantic_role =
  PRIMARY_MECHANISM |
  CORROBORATING_VIEW |
  INDEPENDENT_MECHANISM |
  HOLD
```

Only independently evidenced mechanisms enter the comparison pool. A corroborating view cannot become a duplicate member.

### 4.2 Golden-finger specialization

`GF_CORE` comparison follows:

```text
input/resource
→ conversion_process
→ output
→ growth_loop
→ limitation/cost
```

`GF_ABILITY` is a separate validated lane. Matching ability names, output effects, or growth results still do not establish a shared core mechanism; it must remain isolated from `GF_CORE` except in an explicitly approved cross-domain ontology/composition run.

### 4.3 Plotline specialization

`nine_stage_lifecycle` is the evidence layer. `progression_engine` is the comparison layer and contains 3–6 causal steps explaining how the current state generates the next stage. Pair and family judgments compare the progression engine first, then verify it against lifecycle evidence. Shared topics such as examination, battle, investigation, revenge, or growth are not mechanism identity.

## 5. Pair calibration contract

Domain-internal pair decisions are restricted to:

```text
SAME_MECHANISM
SUBTYPE
ANALOGOUS
DIFFERENT
HOLD
```

Every review separates:

- `mechanism_core_layer`: how the mechanism actually runs;
- `downstream_effect_layer`: what it eventually produces; downstream similarity cannot prove SAME;
- `transfer_dimension`: for SUBTYPE, what may vary and what invariant must remain.

Every calibration pair also records one real `calibration_category`: `OBVIOUS_SAME`, `PARAPHRASE_EQUIVALENT`, `SAME_SURFACE_DIFFERENT_MECHANISM`, `LIKELY_SUBTYPE`, `ANALOGOUS`, `DIFFERENT`, or `BOUNDARY_OR_HOLD`. Coverage is derived from pair records; a control-summary claim cannot replace or contradict those records.

`SAME_MECHANISM` requires the same core causal chain while allowing different names, prose, setting skin, institutions, professions, and resource labels. `SUBTYPE` requires a common core plus a stable, describable, transferable variation. `ANALOGOUS` preserves creative reference value while explicitly remaining outside membership. `DIFFERENT` means the transformation semantics differ. `HOLD` preserves unresolved core evidence rather than forcing coverage.

Keywords, dictionaries, substrings, embeddings, and structural signatures are `CANDIDATE_RETRIEVAL_ONLY`. They never decide a pair relation or membership.

## 6. Reusable mechanism family contract

A family record contains at least:

```json
{
  "family_id": "RMF:<DOMAIN>:<SEMANTIC_FINGERPRINT>",
  "domain": "",
  "family_status": "HYPOTHESIS | HOLD | STABLE",
  "family_name": "",
  "core_mechanism_definition": "",
  "one_sentence_core": "",
  "minimum_definition": {
    "trigger": "",
    "transformation": "",
    "state_change": "",
    "recurrence": "",
    "termination": ""
  },
  "hard_invariants": [],
  "allowed_variations": [],
  "exclusion_boundary": [],
  "termination_condition": "",
  "why_it_recurs": "",
  "same_members": [],
  "subtype_members": [],
  "analogous_references": [],
  "hold_boundary_references": [],
  "false_positive_examples": [],
  "member_definition_tests": [],
  "positive_support_pair_ids": [],
  "negative_boundary_pair_ids": [],
  "structural_analogy_pair_ids": []
}
```

Each candidate member must independently receive one of:

```text
PASS_SAME
PASS_SUBTYPE
OUTSIDE_ANALOGOUS
OUTSIDE_DIFFERENT
HOLD
```

All family provenance is referentially checked. SAME/SUBTYPE/canonical member IDs must exist and pass their own definition tests. Positive-support pairs must exist, use SAME or an explicitly marked subtype-support role, and reference the family's own positive members. Negative-boundary pairs must connect a positive/canonical member to an outside candidate with a compatible judgment. Structural-analogy pairs must exist and be ANALOGOUS or explicitly carry that role. Provenance roles do not overlap.

Membership is based on the minimum definition, hard invariants, negative boundary, and known-conflict audit. It is never inferred from graph connectivity. Thus `A SAME B` and `B SAME C` do not admit C unless C independently passes the family definition.

### 6.1 Stable family gate

A stable family requires:

- positive members from at least two books;
- complete trigger, transformation, state-change, recurrence, termination, and exclusion semantics;
- an independent PASS test for every core member;
- at least one plausible-looking negative boundary case;
- ANALOGOUS references isolated outside membership.

Support may use either:

- Pattern A: at least one cross-book `SAME_MECHANISM` pair plus additional member tests; or
- Pattern B: one canonical implementation plus at least two independent cross-book SUBTYPE implementations sharing the same hard invariant and passing boundary stress.

One canonical plus one subtype remains `HOLD_FAMILY_HYPOTHESIS` unless explicit human approval says otherwise.

### 6.2 Expansion behavior

After a family stabilizes, a new card follows:

```text
candidate retrieval
→ independent family-definition test
→ SAME / SUBTYPE / ANALOGOUS / OUTSIDE / HOLD
```

It is not absorbed by a full similarity graph. Unmatched cards remain `UNCLUSTERED`. If enough unmatched mechanisms suggest a new family, the run returns to `PAIR_CALIBRATION → FAMILY_PILOT → BOUNDARY_STRESS_TEST`.

### 6.3 Family identity and lineage

New IDs use `RMF:<DOMAIN>:<SEMANTIC_FINGERPRINT>`. The fingerprint binds domain, core definition, hard invariants, and mechanism semantics—not member order. Adding a conforming member may preserve the ID. Material changes to the definition, invariants, exclusion boundary, split, or redefinition require a new ID and explicit lineage/supersession. Old family versions remain read-only.

Legacy `cluster_id` values are never reused or converted into RMF IDs. A `legacy_reference` may support audit/lineage lookup but cannot provide semantic membership evidence.

## 7. Boundary stress and false positives

Stress tests actively seek cases sharing keywords, final results, genre, actor labels, resource labels, feedback shape, downstream access, growth outcomes, or verification vocabulary. Each case must explain why it passes or fails the minimum definition. Similar surface form is specifically a source of negative tests, not positive proof.

## 8. Legacy and runtime isolation

V1.0–V1.6.6 outputs may be used for regression, audit comparison, and lineage reference. Their membership is never training truth or semantic support for a new family.

Any core validator failure forces:

```text
PIPELINE_STATUS = HOLD
DOMAIN_FULL = NOT_RUN
FULL_LIBRARY = NOT_RUN
ACTIVE_PROMOTION = NOT_RUN
```

### 8.1 Validation binding

Every mechanism-family validation report binds the PASS/HOLD result to the artifacts that were actually read. It records at least:

```text
validator_skill_commit
validator_source_sha256
validated_run_id
validated_run_document_sha256
validated_pair_artifact_sha256
validation_execution_id
```

The validator hashes raw file bytes when invoked from the CLI. When called as a library without file bytes, it hashes canonical JSON and records the hash mode. A separately supplied pair JSON/JSONL artifact must contain the same records as the run document. `--verify-report <old-report.json>` compares the old binding with the current validator, run document, run ID, and pair artifact; any stale or mismatched binding fails `VALIDATION_BINDING_GATE`. A previous PASS report is not reusable after artifact mutation.

The default domain-full method remains retrieval hints followed by independent definition tests. It must not default to an N×N semantic graph. Full-library work means combining validated domain family libraries, incremental expansion, normalized signatures, ontology relations, and composition links—not loading the entire library into one clustering pass.


## 9. Production-proven execution checklist

The detailed operational sequence lives in `mechanism-family-workflow.md`. The canonical checklist is:

```text
0. Freeze HEAD / run / lane / population / validator provenance
1. MECHANISM_CARD_EXTRACTION
2. READINESS_NORMALIZATION
3. Independence audit
4. PAIR_CALIBRATION
5. HUMAN REVIEW
6. FAMILY_PILOT
7. HUMAN REVIEW
8. BOUNDARY_STRESS_TEST
9. HUMAN REVIEW + lane approval when required
10. DOMAIN_EXPANSION by independent frozen-family definition tests
11. HUMAN REVIEW after every expansion
12. DOMAIN_FULL seal/freeze
13. optional CROSS_DOMAIN_ONTOLOGY with identity/composition separation
14. HUMAN REVIEW
15. FULL_LIBRARY assembly
16. HUMAN REVIEW
17. explicit production promotion
```

Normative execution rules:

- `card count != independent implementation count`;
- dependent parent/child, projection, copied-output, composite-component, and same-episode records do not automatically add independent support;
- PAIR_CALIBRATION never emits operational `STABLE`;
- BOUNDARY_STRESS_TEST is the first stage allowed to emit `STABLE`;
- expansion is `eligible cards × frozen stable families`, not a full N×N clustering graph;
- residual mechanisms that may form a new family return to pair calibration instead of being minted inside expansion;
- DOMAIN_FULL is a seal/freeze stage and uses explicit `SAME/SUBTYPE/ANALOGOUS/DIFFERENT/HOLD/UNCLUSTERED` accounting;
- cross-domain ontology never changes family membership;
- composition requires a concrete source-output → target-input bridge condition;
- FULL_LIBRARY assembles approved assets and may derive planner recipes/indexes, but those derived artifacts are not semantic evidence;
- recipe link provenance must be audited independently;
- validator PASS never substitutes for required human semantic approval;
- promotion may change packaging/runtime metadata, but never family semantics, membership, link direction, bridge conditions, or approved recipe semantics.

### 9.1 Mandatory human gates

At minimum:

```text
PAIR_CALIBRATION → STOP_FOR_HUMAN_REVIEW
FAMILY_PILOT → STOP_FOR_HUMAN_REVIEW
BOUNDARY_STRESS_TEST → STOP_FOR_HUMAN_REVIEW
each DOMAIN_EXPANSION → STOP_FOR_HUMAN_REVIEW
DOMAIN_FULL ← APPROVE_DOMAIN_FULL
optional CROSS_DOMAIN_ONTOLOGY → STOP_FOR_HUMAN_REVIEW
FULL_LIBRARY ← APPROVE_FULL_LIBRARY
ACTIVE_PROMOTION ← APPROVE_PROMOTION
```

A lane marked `CALIBRATION_REQUIRED` also needs:

`APPROVE_LANE_VALIDATION:<domain>:<lane>`

before it may proceed into DOMAIN_EXPANSION.

### 9.2 Hard semantic stops

Immediately stop when:

- a frozen stable-family definition is widened or materially changed to rescue a member;
- SAME/SUBTYPE lacks primary-object evidence;
- dependent implementations are counted as independent cross-book support;
- ANALOGOUS or HOLD is treated as membership;
- graph connectivity or single-link transitivity decides membership;
- UNCLUSTERED is forced into a family;
- historical cluster membership is inherited as truth;
- a stale validation binding is reused after artifact mutation;
- an ontology composition link is justified only by “helpful / stronger / informative” without an executable bridge;
- a recipe declares families that do not match its referenced composition-link endpoints.

### 9.3 Validated V1.7 reference scope

The production-proven reference implementation has completed the staged flow through DOMAIN_FULL for:

```text
relationship_engine
GF_CORE
GF_ABILITY
plotline_progression_engine
```

It also validated optional cross-domain ontology/composition and FULL_LIBRARY assembly. These results prove the workflow; they are not a required family count or mandatory ontology shape for future runs.
