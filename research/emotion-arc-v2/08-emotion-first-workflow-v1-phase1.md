# Emotion-First Skill Workflow V1 — Phase 1 implementation report

## Scope / base

- Base: `research/emotion-story-bridge-pilot` @ `b23a52a3ec853c40c56f13d6e9abac730addebb2`.
- Branch: `research/emotion-first-skill-workflow-v1`.
- Changes are **code-repo research-only**; no changes to `nova-material-library`, canonical, frozen source TXT, production Schema, active RMF, production package, novel prose, or `main`.
- Stage 4 creation stays `HOLD`.

## Implemented (not a creative-quality approval)

1. Planner Skill routing to `references/emotion-first-workflow-v1.md`; old default Planner and Bridge routes retained.
2. `scripts/emotion_first_workflow_v1.py prepare`: validate truly sparse brief, use the existing Emotion Arc search tool to resolve EL/EW/MA/AH, freeze canonical input/retrieval hashes, generate independent baseline and enhanced model instructions.
3. **Host-model semantic passes**: the Skill, not Python, creates `legacy-fragment.json` and `enhanced-fragment.json`. The user need not prewrite the former 50-KB semantic composition. Baseline prompt must not include the emotion index; the enhanced prompt includes actual evidence + limits. Separate contexts are **requested**, not machine-provable.
4. `finalize`: reject changed frozen input, wrong pass, missing model provenance, unsupported emotion citations, and early macro `PAID`. Combine independently composed model fragments into the existing Bridge's `semantic-composition.generated.json`, and run the existing deterministic Bridge/source validators.
5. Model repair is bounded to two corrections (three total attempts), with each attempted output stored in `attempt-XX` and specific repair requests; no silent validation downgrade.
6. New sparse brief fixture expresses *trust → shared protection* emotional goals only; does not contain novel character names, powers, antagonists, specific plot nodes, or next-arc facts.

## Tests performed

An equivalent locally staged copy of the new Python script and test file was syntax-checked via `python -m py_compile` and run using Python `unittest`: **7/7 PASS**. Cases cover forbidden story prefill, honest fixed pilot scope, legacy prompt evidence isolation, missing/wrong-time payoff witnesses, immutable session preparation and refusal of fabricated source IDs before Bridge invocation.

**Not performed:** no direct private Git clone was available in the isolated test container, so I have not executed the exact GitHub branch against the actual frozen BOOK_001 material library, nor called a host-model semantic pass inside the user's WorkBuddy environment. Existing Bridge integration tests and all prior regressions still need to be rerun in that environment. Do not reinterpret local unit tests as actual end-to-end creative success.

## How to run on WorkBuddy / local repo

```bash
cd skills/novel-creation-planner
python scripts/test_emotion_first_workflow_v1.py -v
python scripts/emotion_first_workflow_v1.py prepare \
  --brief ../../research/emotion-arc-v2/fixtures/emotion-first-phase1/sparse-brief.json \
  --emotion-library <material-repo>/research/emotion-arc-v2/skill-integration/book001-derived \
  --workspace <new-empty-research-session>
# Model executes 01-legacy-prompt.md, writes legacy-fragment.json
# Fresh model context executes 02-enhanced-prompt.md, writes enhanced-fragment.json
python scripts/emotion_first_workflow_v1.py finalize \
  --workspace <research-session> \
  --legacy <research-session>/legacy-fragment.json \
  --enhanced <research-session>/enhanced-fragment.json \
  --material-snapshot-repo <material-repo> \
  --material-snapshot-commit 1e10e6e3ffb70eda94a400073155fd89db724ce9
```

Validate the generated `attempts/attempt-XX/result/validation-report.json` and all returned provenance. On first failure, repair the model fragment without changing the user brief or the validator.

## Explicit limits

- The existing Bridge validator and emotional search currently require the pilot scope `genre=["玄幻","高武"]`, `emotion_contour=["DOWN","DOWN","UP"]`, and exactly four high-level weave dimensions. Broader support requires a **separate** backward-compatible implementation and tests.
- An independent model session is a host-level protocol, not a Python security boundary or proof of blinding.
- A witness reference establishes chronological eligibility for a PAID assertion, not whether the node's contents genuinely fulfill that promise; literary reviewer must still decide.
- Neither model proposal nor source proximity guarantees originality, emotional impact, 50-chapter sustainability or readership.

## Phase 1 disposition

- `SKILL_ORCHESTRATION = IMPLEMENTED_RESEARCH`
- `SPARSE_BRIEF_PROMPTS = IMPLEMENTED`
- `MODEL_OUTPUT_GENERATION = REQUIRES_HOST_EXECUTION`
- `END_TO_END_WITH_FROZEN_LIBRARY = NOT_RUN_IN_THIS_ENVIRONMENT`
- `CREATIVE_QUALITY = PENDING_INDEPENDENT_REVIEW`
- `PRODUCTION_PROMOTION = NOT_RUN`
- `STOP_FOR_INDEPENDENT_REVIEW`
