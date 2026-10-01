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

## 7. Family immutability

Ontology work creates a reference layer above domain families. It must not:

- add, remove, or rewrite family members;
- convert an ANALOGOUS card into a family member;
- reuse an ontology ID as a family ID;
- use composition to justify family identity;
- merge two domain families into one cross-domain family.

Every concept must explain `why_this_is_not_a_family_merge`. Family membership before and after ontology validation must be byte-for-byte or semantically identical.

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

