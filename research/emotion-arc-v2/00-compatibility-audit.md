# Emotion Arc V2 compatibility audit

Status: `RESEARCH_ONLY / PENDING_INDEPENDENT_REVIEW`
Frozen code base: `770c5881148fe5079ce9dcb5e5155f2b26dfbf0f`

## Existing interfaces retained

| Layer | Existing evidence | V2 treatment |
| --- | --- | --- |
| Chapter emotion | `chapter-emotion-schema.md` defines one JSONL row per chapter and the promise/QA fields (lines 7, 33–36, 75–77). | Read-only input. No canonical row, promise, or QA change. |
| EMOF | `emotion-function-card-contract.md` keeps 01 as one-row-per-chapter and separates machine closure from semantic acceptance (lines 10, 69, 82). | Optional references only; an emotion line is not an EMOF card. |
| Plotline | `novel-plotline-miner/SKILL.md` fixes the nine-stage lifecycle and candidate-only boundary (lines 21, 41, 180, 266). | Remains the character-action causal execution layer. |
| Story arc | `novel-arc-structure-miner/SKILL.md` distinguishes arc from plotline and requires independent parent/sub-arc evidence (lines 82, 88, 130). | `MA:` is a separate reader-promise layer; it never reuses `AR:` IDs. |
| Planner | `emotion-first-creation.md` retains E0, E1, M0, D1 and D4 (lines 45, 51, 62, 68, 105–119). | Optional E2/E3 guide only; no change to formal plan schema or old validators. |
| Draft/fact boundary | `novel-writer/SKILL.md` lines 14–17, 88–123 and `nova-plus-novel/SKILL.md` lines 27, 42, 65 require explicit confirmation before facts are promoted. | Future active-state packets are read-only; this pilot does not touch a novel project. |

Line numbers are pointers against the frozen base and are supplemented by stable headings so later documentation edits do not silently change the interpretation.

## Missing interfaces supplied by this pilot

- Stable research records for `EMOTION_LINE`, `EMOTION_WEAVE`, `MACRO_EMOTION_ARC`, and `ARC_HANDOFF`.
- A non-destructive local-promise-to-ledger crosswalk with explicit uncertainty.
- Frozen Git source snapshot validation, including file SHA checks distinct from chapter source fingerprints.
- Structural gates for membership, time range, declared causal evidence, macro payoff, and handoff status.
- A Planner-only optional E2/E3 design guide and hypothetical adapter fixture.

## Interfaces deliberately not changed

- Canonical 01 records, promise ledger, 02–09 records, existing EMOF, RMF family/recipe, active packages, and production manifests.
- `plan-schema.md`, `validate_emotion_creation.py`, `validate_creation_plan.py`, and their fixtures.
- Default Planner routing, writer permissions, or official continuity documents.
- Any status promotion from `candidate/HOLD` to active or production.

## Known baseline risks

1. BOOK_001 chapter-level `source_fingerprint` is `UNAVAILABLE`; repository file blobs can be verified, but raw-TXT-to-row provenance remains partial.
2. Local chapter promise `P001` in chapter 1 means institutional registration, while `BOOK_001:PROMISE:001` means the jade-disc growth loop. Numeric suffix matching is invalid.
3. The pilot window ends at chapter 30. It can show a candidate new father-history/tide promise, but cannot prove the prior macro arc's final settlement or a fully verified overlapping handoff.
4. Existing 05/06/08 documents are book-level candidates. Their IDs can provide context but cannot substitute for chapter evidence.
