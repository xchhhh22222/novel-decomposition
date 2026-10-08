# WorkBuddy SOP — Non-destructive EMOF backfill to existing material library

**Authorized scope**: historical *derived emotion-function cards only*. No new market research, no reread of whole corpus by default, no cross-book clustering, no novel drafting, no active promotion, no editing existing source facts.

## A. Pin repositories and freeze scope

1. Use `xchhhh22222/novel-decomposition`, **this upgraded main commit** (read newest main after approval). Read:
   - `skills/novel-dna-mining-suite/SKILL.md`
   - `skills/novel-chapter-emotion-miner/SKILL.md`
   - `skills/novel-dna-mining-suite/references/core/chapter-emotion-schema.md`
   - `skills/novel-dna-mining-suite/references/core/emotion-function-card-contract.md`
   - `skills/novel-dna-mining-suite/scripts/core/validate_emotion_function_cards.py`
2. Material repo: `xchhhh22222/nova-material-library`. **Do not start from main** (its current snapshot only has README). Start at existing branch `nova-v1.7.0-shared-dna-production`, pinned base `ed9227c403d5c85c2f594e3291af2c9eff2441e9` or verify the current head and report divergence. Create **new work branch** `emotion-function-backfill-v1`.
3. Before modification, freeze commit, `git status`, source inventory, path-level hashes (existing 01/02–09/package), and any external chapter source availability. Work tree must be clean; stop if uncommitted changes.
4. Existing active `packages/shared-dna-library/v1.0.0/` and v1.7 RMF frozen packages are strictly **read only**. Never modify manifest/status/hash/active flags.

## B. Inventory: reuse-first

Enumerate `books/BOOK_001` ... `books/BOOK_009` using actual files, not assumed names:
- `01_章节情绪/chapter_emotion.jsonl`
- `01_章节情绪/promise_ledger.jsonl`
- `01_章节情绪/rhythm_audit.md` when present
- `01_章节情绪/per_book` **only where it exists**
- 05 characters, 06 plotline, 07 opening, 08 arc, 09 mechanism, chapter facts where available

Produce `emotion-function-backfill/v1/qa/inventory.json` with real counts: chapter coverage/QA, ledger availability, fingerprint `UNAVAILABLE` counts, missing original sources, usable windows/gaps. Keep source names and IDs intact. **Never** change the old QA status to pass a migration.

## C. Pilot: extract without remine

Start with independently verified candidate windows, subject to source facts and ledger:
- BOOK_005 ch21–25 (warning/pressure/visible containment/revised official judgment).
- BOOK_005 ch46–60 (only if one genuine coherent causal window can be supported; else split or HOLD).
- BOOK_001 ch3–6 (only if source evidence and promises establish a complete window).
- BOOK_002 early money-to-growth realization (derive exact span from source, do not assume promise closes in seven chapters).

For each:
1. Read actual canonical 01, corresponding ledger, rhythm audits and chapter/plot evidence where accessible.
2. Create an EMOF record with **separate** `source_facts` and `emotional_function`.
3. Abstract reader expectation, emotional trajectory, trigger, pressure, protagonist/other character agency, payoff and aftermath; mark genuinely necessary causal invariants.
4. `replacement_slots`: include at least two meaningful observed roles + replacement rules (characters, relation, antagonist, threat, environment, resource, resolution). These are **possible substitution roles**, not evidence that any new novel variation already happened.
5. A card is a single-source EMOF candidate. Do not create family IDs, cluster labels, recipe links, or new-book events.
6. Uncertain attribution/meaning must be `evidence_gaps[]`, `qa_status=HOLD` pending independent review; no hallucinated source chapter. Do not force all four examples to PASS.

Output only new files like:
`books/BOOK_005/01_章节情绪/derived/emotion_function_cards.jsonl`

## D. Machine validation, independent semantic review, then optional expansion

From the cloned Skill repo:
```bash
python skills/novel-dna-mining-suite/scripts/core/test_validate_emotion_function_cards.py
python skills/novel-dna-mining-suite/scripts/core/validate_emotion_function_cards.py \
  /path/to/material-library/books/BOOK_005/01_章节情绪/derived/emotion_function_cards.jsonl \
  --library-root /path/to/material-library
```
Run the validator for **each** book card file.

- Machine `ok=true` checks mandatory format and exact existing chapter/ledger linkage, **not** emotional semantics, creativity or completion.
- `FINGERPRINT_UNAVAILABLE` warnings must remain visible. Do not mark original text as hash-verified.
- Obtain independent semantic review with source comparison for every claimed PASS, including whether the extracted function survives changes to actor/relationship, threat, scene and payoff realization.
- Calibration examples: creature threatens family ↔ human enemy threatens family = potentially similar function; sibling romantic choice vs childhood friend's romance has different relationship preconditions; reusing source-specific water tank/eggs/exact clock/freezing-burning sequence is not a new plot. These are *hypothetical test cases*, not evidence from specific books.
- If a reviewer cannot inspect enough approved chapters, HOLD. Do not self-authorize PASS.
- If pilot review shows major systematic defects, STOP, report them, and **do not** scale the batch.

If pilot passes independent review, continue to BOOK_001...BOOK_009. Select 2–4 meaningful windows/book **as a planning range, not quota**; do not invent events to meet card count. Use naturally complete 3–5 / 10–40 chapter episodes; preserve genuine open promises. Submit all output to the same source and semantic checks. Existing 02–09 records remain reference data.

## E. Audits and allowed writes

Allowed:
- `books/BOOK_NNN/01_章节情绪/derived/emotion_function_cards.jsonl` (new files only, for the authorized books).
- `emotion-function-backfill/v1/qa/*.json` and `emotion-function-backfill/v1/reports/*.md` (new audit docs only).

Forbidden:
- Any existing `chapter_emotion.jsonl`, `promise_ledger.jsonl`, original novel chapter, 02–09 per_book/derived, v1.7 RMF mechanism assets, production `packages/**`, active manifests/hashes, old cluster/family membership, existing QA records.
- Do not automatically repair old `UNAVAILABLE` fingerprints, edit historic QA, re-run write-capable legacy scripts or overwrite anything outside allowed files.
- A previously generated EMOF file should not be overwritten silently. Detect it, diff it, and STOP for explicit reconciliation.

Save:
1. `qa/inventory.json` counts and file existence.
2. `qa/validation-results.json` per card/file with gate statuses, warnings, skipped windows.
3. `qa/semantic-review.json` with independent evidence-grounded review and unresolved HOLD.
4. `qa/change-scope.json` files changed, hashes, baseline commit, which original hashes were rechecked unchanged.
5. `reports/emof-backfill-report.md` source reuse rate, ready/hold/fail, missing original text, distinct functions, next-step blockers.

Before commit, verify `git diff` only includes allowed paths, and originally tracked source/production files are unmodified. Commit/push **only** the branch `emotion-function-backfill-v1`; do not merge into production or main, and do not bump shared package versions. If GitHub authentication/permissions block push, report the local branch/commit and exact obstacle.

## F. Final mandatory handoff

Report the true branch/commit/PR link (if created), counts by book and status, validation commands/results, sample 3 cards with canonical refs, original-asset integrity check, source `UNAVAILABLE` limitations, and any proposed minimal source recheck. Stop with:

`EMOF_BACKFILL = REVIEW_REQUIRED`
`CLUSTERING = NOT_RUN`
`CREATION_PLANNER_CHANGES = NOT_RUN`
`ACTIVE_PROMOTION = NOT_RUN`
`STOP_FOR_HUMAN_REVIEW`

**Only after this handoff is reviewed** should a future iteration consider the independent emotion clustering Skill.