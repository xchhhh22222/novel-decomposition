# Cross-domain Narrative Mechanism Ontology Contract (V1.7.0)

This contract governs optional comparison between already stable reusable mechanism families from different domains. It never compares raw cards directly, never merges domain families, and never changes family membership.

## 1. Eligibility and normalized signatures

Only `family_status = STABLE` families that passed the reusable mechanism family contract may enter ontology comparison. Each input must expose a normalized signature containing:

- domain and family ID;
- trigger semantics;
- transformation semantics;
- state variable changed;
- feedback or recurrence driver;
- validity basis and constraints;
- termination condition;
- hard invariants and exclusion boundary.

Raw mechanism cards, family hypotheses, HOLD families, legacy clusters, and uncalibrated lanes cannot provide positive ontology support.

## 2. Identity relations

Cross-domain identity review uses only:

```text
META_EQUIVALENT
META_SPECIALIZATION_CANDIDATE
STRUCTURAL_ANALOGY
DISTINCT
HOLD
```

`META_EQUIVALENT` has a high threshold: corresponding trigger semantics, transformation semantics, changed state variable, recurrence logic, termination, and negative boundary. A shared causal shape or shared final outcome is insufficient.

`META_SPECIALIZATION_CANDIDATE` means the families plausibly instantiate a nontrivial common abstract mechanism while retaining domain-specific specialization. It does not create a parent automatically.

`STRUCTURAL_ANALOGY` preserves useful cross-domain comparison without identity. Its evidence remains in `structural_analogy_pair_ids`, never positive membership support.

Every formal ontology identity pair must connect two different domains. Same-domain pairs remain domain-level evidence and cannot support cross-domain ontology.

## 3. Composition relations

Composition is recorded separately from identity:

```text
LEFT_CAN_FEED_RIGHT
RIGHT_CAN_FEED_LEFT
BIDIRECTIONAL_POSSIBLE
NONE
HOLD
```

One mechanism's output may become another's input. This is a production or sequencing relation, not identity, subtype, or membership. Composition must have `membership_effect = NONE` and cannot modify either family record.

An ontology pair review must store identity and composition in distinct fields. Neither relation may be inferred from the other.

An executable composition link records `link_id`, `source_family_id`, `target_family_id`, `source_output`, `target_trigger_or_input`, `bridge_condition`, `composition_relation`, `membership_effect=NONE`, and `identity_effect=NONE`. Both families must exist, be STABLE, and differ.

## 4. Ontology concept schema

A candidate ontology record contains at least:

```json
{
  "ontology_id": "",
  "status": "PASS | HOLD",
  "concept_name": "",
  "abstract_core": "",
  "one_sentence_core": "",
  "required_invariants": {
    "trigger": "",
    "transformation": "",
    "state_change": "",
    "feedback": "",
    "termination": ""
  },
  "domain_realizations": [],
  "allowed_variations": [],
  "exclusion_boundary": [],
  "false_positive_tests": [],
  "positive_support_pair_ids": [],
  "negative_boundary_pair_ids": [],
  "structural_analogy_pair_ids": [],
  "composition_reference_pair_ids": [],
  "why_this_is_not_a_family_merge": "",
  "non_triviality_test": "",
  "confidence": ""
}
```

The provenance arrays have different roles and must remain separate. A mixed `source_pair_ids` array is not an acceptable substitute.

A PASS concept has at least two existing STABLE family realizations from at least two distinct domains. Every realization domain must match both the family and normalized signature. Every positive-support pair must be `META_EQUIVALENT` or `META_SPECIALIZATION_CANDIDATE`, cross domains, use STABLE families, and have both families listed in `domain_realizations`.

## 5. Nontriviality gate

The following are too generic to PASS:

```text
input → output
state-change loop
feedback loop
growth loop
action produces result
information causes action
resources produce growth
```

A PASS ontology concept must specify:

- the semantic kind of trigger;
- the transformation performed and its validity basis;
- the precise state variable changed;
- the recurrence driver;
- the termination condition;
- at least one exclusion or negative boundary that rules out a plausible false positive.

The state variable cannot be a vague word such as “state,” “progress,” “growth,” or “result.” It must identify what actually changes, for example credibility, access eligibility, actionable knowledge, resource stock, identity standing, threat level, or commitment strength.

## 6. Provenance and boundary roles

Use these separate roles:

```text
positive_support
negative_boundary
structural_analogy
composition_reference
```

A pair cannot be counted as both positive support and negative boundary for the same concept. HOLD family pairs cannot be positive support. Structural analogies may inform false-positive design but never ontology identity membership.

Every provenance ID must resolve to a real pair. Negative-boundary IDs require a compatible `DISTINCT` or `HOLD` relation; structural-analogy IDs require `STRUCTURAL_ANALOGY`; composition-reference IDs require a non-`NONE` composition relation. Incompatible role overlap is a hard failure.

## 7. Family immutability

Ontology work creates a reference layer above domain families. It must not:

- add, remove, or rewrite family members;
- convert an ANALOGOUS card into a family member;
- reuse an ontology ID as a family ID;
- use composition to justify family identity;
- merge two domain families into one cross-domain family.

Every concept must explain `why_this_is_not_a_family_merge`. Family membership before and after ontology validation must be byte-for-byte or semantically identical.

Whenever an ontology document contains a concept or composition link, both `family_membership_before` and `family_membership_after` snapshots are mandatory. Omitting both snapshots does not bypass the immutability gate.

## 8. Review and promotion gates

`CROSS_DOMAIN_ONTOLOGY` is optional and begins only after stable family inputs exist. A PASS validator result is still candidate-only. Human approval is required before any planner-facing or production use.

Any core ontology gate failure forces:

```text
PIPELINE_STATUS = HOLD
DOMAIN_FULL = NOT_RUN
FULL_LIBRARY = NOT_RUN
ACTIVE_PROMOTION = NOT_RUN
```

Ontology coverage is not a KPI. `DISTINCT` and `HOLD` are valid outcomes, and no target concept count is required.

