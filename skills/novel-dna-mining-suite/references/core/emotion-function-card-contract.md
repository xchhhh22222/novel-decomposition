# Emotion Function Card (EMOF) v1 — Source-Preserving Derived Contract

## 0. Purpose and scope

An **EMOF** card is a **single-book, evidence-grounded, reusable emotional function** extracted *after* canonical chapter emotion and promise ledger work. It is not a cross-book cluster, not a RMF family, not a new chapter schema, and not a new-book plot. Its central question is:

> Which reader expectation does this window build, by what causal pressure and character action, and what observable event pays it off? Which causal requirements survive changes to character identities, places, adversaries, resources and events?

Canonical authorities remain:
- 01 one-row-per-chapter: `references/core/chapter-emotion-schema.md`
- Already approved 02–09 per-book/derived components and source chapter evidence
- Existing v1.7.0 RMF staged family discovery, **unchanged**

**Never** edit `chapter_emotion.jsonl`, `promise_ledger.jsonl`, original chapters, existing 02–09 records, frozen RMF, or active packages just to construct EMOF cards. Separate derived output only.

## 1. Source and draft locations

Source material in material library research branches can be under:
- `books/BOOK_NNN/01_章节情绪/chapter_emotion.jsonl`
- `books/BOOK_NNN/01_章节情绪/promise_ledger.jsonl`
- `books/BOOK_NNN/01_章节情绪/rhythm_audit.md` (where present)
- approved chapter sources and optional 05/06/07/08/09 supporting records

**Do not assume a per_book 01 summary exists**; the corpus may have canonical emotion + ledger while missing a per_book aggregation.

Proposed draft destination in a **new, unpromoted branch**:
`books/BOOK_NNN/01_章节情绪/derived/emotion_function_cards.jsonl`

Do not add these files into `packages/shared-dna-library/v1.0.0` manifest or SHA lists. No active status, no cluster membership, no auto-promotion.

## 2. Card shape (schema_version=1, record_type=emotion_function_card)

One line = one emotional causal window. A card should be a meaningful expectation→pressure→agency→payoff→aftermath unit. 3–5 chapters is an experimental short window, 10–40 chapters a possible longer window; **neither is a quota**. Partial or open-ended windows are allowed, but must not fabricate payoff.

```json
{
  "schema_version": 1,
  "record_type": "emotion_function_card",
  "record_id": "EMOF:BOOK_005:0021-0025:01",
  "status": "candidate",
  "source_book_id": "BOOK_005",
  "chapter_span": {"start": 21, "end": 25},
  "source_chapter_refs": ["BOOK_005:CHAPTER:0021", "BOOK_005:CHAPTER:0022", "BOOK_005:CHAPTER:0024", "BOOK_005:CHAPTER:0025"],
  "source_evidence_refs": ["BOOK_005:CHAPTER:0021", "BOOK_005:CHAPTER:0022", "BOOK_005:CHAPTER:0024", "BOOK_005:CHAPTER:0025"],
  "source_promise_refs": ["BOOK_005:PROMISE:001"],
  "source_facts": {
    "initiating_event": "SOURCE FACT: ...",
    "pressure_event": "SOURCE FACT: ...",
    "decisive_actions": ["SOURCE FACT: actor, choice, consequence"],
    "observed_result": "SOURCE FACT: ..."
  },
  "emotional_function": {
    "reader_expectation": "Reader wants ...",
    "emotion_trajectory": ["tension", "stronger tension", "relief/recognition"],
    "trigger_function": "What creates the expectation",
    "pressure_logic": "Why the problem cannot be solved yet",
    "agency_function": "What choice changes the outcome",
    "payoff_function": "What is visibly satisfied",
    "aftermath_function": "What state is different afterward",
    "invariants": ["abstract necessary condition A", "abstract necessary condition B"],
    "replacement_slots": [
      {"slot": "threat_actor", "observed": "original source fact", "replacement_rule": "what new causal role must still hold"},
      {"slot": "location", "observed": "original source fact", "replacement_rule": "what the new location must enable"}
    ],
    "limitations": ["Conditions under which this function is not transferable"]
  },
  "evidence_gaps": [],
  "semantic_review": {"status": "PENDING_REVIEW", "reviewer": "", "notes": ""},
  "qa_status": "HOLD"
}
```

The example record is **illustrative**; do not copy its source facts, source_promise_refs, or QA as verified. Source selectors and facts must be derived from actual source records.

- `source_facts`: original-world facts only; source-specific named details are permitted **here**, clearly labeled as source facts.
- `emotional_function`: abstract transferable functional description, no original unique event chain disguised as universal rule.
- `invariants`: only what is needed for an analogous reader expectation/payoff; not all observed steps from the original story.
- `replacement_slots`: actor identity, relationship type, scene, adversary, stakes/resource and resolution *can* change when their replacement_rule remains satisfied. No fixed percent of change, no demand for identical emotion strength.
- `source_chapter_refs`: actual PASS chapters used to understand this window; not assumed every intermediate chapter is PASS.
- `source_evidence_refs`: every claimed evidence ref must be one of those chapters and PASS. More detail needs field-level references in the review narrative; do not launder evidence from an unrelated window.
- `source_promise_refs`: canonical ledger record IDs; if no source ledger match, leave empty and explain in `evidence_gaps`.
- `semantic_review` is only set to PASS by independent, recorded review; `qa_status` remains HOLD for unreviewed drafts. A validator's exit 0 means **machine structure/source closure passed**, not semantic acceptance.

## 3. Independent quality gates

**SOURCE_TRUST** (extraction): actual chapter refs exist in the declared book, source chapters PASS, every ref resolves (not just one overlaps); promise refs exist and refer to the window; chapter source_fingerprint=UNAVAILABLE is visibly flagged as `FINGERPRINT_UNAVAILABLE`, never silently upgraded to full source-text verification. Cross-check actual approved chapters where accessible.

**INTERFACE_READINESS** (derived function): reader expectation + trigger + pressure + character agency + payoff/legitimate open state + aftermath, meaningful invariants, replacement slot rules and known limitations. Preserve the difference between (a) source fact and (b) hypothesis about reader emotion. One-label `low-low-high` is not ready.

**CURRENT_COMPATIBILITY** (new-book candidate): **NOT_APPLICABLE in mining**. Only the planner may claim compatibility after evaluating actual replacement actors, world institutions, ability inputs, conflict pressures and downstream state changes.

Machine QA reports `STRUCTURAL_PASS` and `SOURCE_TRACEABLE` separately from human `SEMANTIC_REVIEW`. Passing a local JSONL schema does not prove originality, emotional effectiveness or cross-book functionality.

Statuses per axis: `PASS / PARTIAL / HOLD / FAIL`; `CURRENT_COMPATIBILITY=NOT_APPLICABLE` in this Skill. A missing chapter/ledger or unsupported inference is HOLD/FAIL as appropriate, not an invented PASS.

## 4. Translation checks (for semantic reviewer, not machine truth)

- **Emotional functional equivalence**, not emotional label equality: expectation, pressure direction and payoff function should remain recognizably similar after replacement; emotional intensity may change.
- **Counterfactual A**: change the central actor/relationship (family→teammate or enemy→rival) while retaining a plausible emotional function.
- **Counterfactual B**: change scene and causal implementation (home→academy, beast threat→human adversary) and verify the revised incentives still work.
- **Negative example**: keep the exact original location + threat carrier + clock + technical resolution + outcome while only renaming nouns; flag **SOURCE_EVENT_CHAIN_RISK**, do not publish it as new novel content.
- Do not invent a novel while mining: reviewer examples are **hypothetical portability probes**, marked as such and excluded from source evidence.

## 5. Historical backfill and coverage

Reuse every available canonical emotion and promise ledger. For historic books, propose only evidence-supported windows; do not re-extract whole chapters by default. Pilot BOOK_005 (21–25, 46–60), BOOK_001 (3–6), optionally BOOK_002 (cash-to-growth early window) **only if source references and ledgers validate**. Incomplete windows receive HOLD and explicit `evidence_gaps` or are skipped with reason. No quota and no automatic mother-family assignment.

`scripts/core/validate_emotion_function_cards.py` validates only draft form and exact canonical link closure. Human semantic audits, fingerprints, provenance and promotion are separate.
