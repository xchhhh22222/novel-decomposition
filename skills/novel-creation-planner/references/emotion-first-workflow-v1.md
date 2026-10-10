# NOVA Emotion-First Workflow V1 — Research-only Skill orchestration

**Status:** `RESEARCH_WORKFLOW / MODEL_IN_THE_LOOP / candidate / HOLD`.

**Purpose:** Turn a *short emotional intent* into two distinct **original** structures with traceable EL/EW/MA/AH evidence and node-specific 02–09 material assembly, without requiring the user to author `semantic-composition.json`. Preserve the original nine-stage Story Spine, existing validators, production schema, and all R3 HOLDs.

This is an agent Skill protocol, not a standalone generative Python program. The **host model** performs semantic selection/composition; Python only freezes inputs, searches existing evidence, verifies source/contract/state fields, and invokes the existing Bridge. Never describe a standalone deterministic run as creative intelligence.

## Activation and trust

Activate only when the user explicitly wants Emotion Arc V2 research or Emotion-First creative experimentation. Default production Planner route, market-research requirements, RMF restrictions, and `E0/E1/M0/D1–D4` remain unchanged.

**Input:** the user's plain-language emotion request. The host model first drafts `sparse-brief.json` containing *only* `schema_version=sparse_emotion_brief_v1`, `brief_id`, `input_mode=SPARSE_EMOTION_BRIEF`, `status=candidate`, `genre`, `core_reader_expectation`, `emotion_contour`, `required_emotion_weaves`, `longform_requirement`, and optional `forbidden_prefill`. Never invent user preferences: hypotheses must be explicit and reviewable. Story facts (names, monster, faction, abilities, plot nodes, next-arc theme) are forbidden in this brief.

**V1 scope:** to avoid silently breaking the existing Bridge and search adapter, its runnable pilot accepts `genre=["玄幻","高武"]`, `emotion_contour=["DOWN","DOWN","UP"]`, four high-level weave requirements. Broader genres/contours need an independently tested adapter revision. Do not claim universal genre support.

**Research source:** the existing BOOK_001 candidate/HOLD derived emotion package (EL/EW/MA/AH plus R3 provenance), and a separately frozen active shared 02–09 material package. Do **not** promote emotion cards or replace them with invented lookalikes. Record snapshot commits.

## The actual agent sequence

1. **Clarify only essential constraints.** Turn the short user request into a sparse brief. Do not precompose a story. The user need not supply JSON; the host model writes it.
2. **PREPARE**: call the CLI below. It checks sparse constraints, calls the real `search_emotion_arc_library.search_library`, freezes the brief/retrieval hashes, and writes two distinct prompts and a `session.json` checkpoint.
3. **LEGACY pass first, in an isolated model context if supported**: open `01-legacy-prompt.md`, access the same 02–09 source interface as enhanced, and write a complete **model-authored** `legacy-fragment.json`. Do not read the emotion retrieval file or enhanced draft; log isolation honestly. Do not weaken the legacy model or its execution budget merely to improve E2/E3.
4. **ENHANCED pass second in a fresh context**: open `02-enhanced-prompt.md` containing retrieved EL/EW/MA/AH records with real source IDs, their strengths and limitations. Actively choose some patterns and reject others. Use the same 02–09 source interface. Design at least two causally different original options and write `enhanced-fragment.json`.
5. **CHECK/FINALIZE**: call the CLI below. It checks frozen inputs, separately model-authored fragments, actual retrieved emotion citations, the original A payoff contract, and *PAID witness timing*. It then creates `semantic-composition.generated.json` (machine-assembled, not supplied by user) and invokes the established `run_emotion_story_bridge_pilot.py`. The existing validator enforces research provenance, material selection, state transitions and node-local effects.
6. **REPAIR**: on nonzero return, read `model-repair-request.json` or the validator errors. Ask the model to repair only the affected fragment. **Maximum two repair attempts per model pass.** If still failing, stop at HOLD. Never relax tests, forge sources, alter canonical, or silently change the original reader promise.
7. **HUMAN REVIEW**: present two enhanced original directions, the independent baseline, source/rejection and adaptation tables, macro payoff witness table, and pending risks. `ok=true` means *structural research validation only*, not originality, quality, reader retention or production approval.

**CLI from `skills/novel-creation-planner` repo root:**

```bash
python scripts/emotion_first_workflow_v1.py prepare \
  --brief <sparse-brief.json> \
  --emotion-library <nova-material-library/.../book001-derived> \
  --workspace <new-empty-research-session>
# Agent reads 01-legacy-prompt.md and writes legacy-fragment.json
# Agent reads 02-enhanced-prompt.md and writes enhanced-fragment.json
python scripts/emotion_first_workflow_v1.py finalize \
  --workspace <research-session> \
  --legacy <research-session>/legacy-fragment.json \
  --enhanced <research-session>/enhanced-fragment.json \
  --material-snapshot-repo <frozen-material-repo> \
  --material-snapshot-commit 1e10e6e3ffb70eda94a400073155fd89db724ce9
```

**Required fragment envelope:**

```json
{
  "schema_version": "emotion_story_composer_fragment_v1",
  "brief_id": "<same frozen brief ID>",
  "status": "candidate",
  "mode": "LEGACY_BASELINE or E2_E3_ENABLED",
  "semantic_composer": {
    "kind": "MODEL_AUTHORED_RESEARCH_CANDIDATE",
    "model_family": "<truthful executing model>",
    "literary_approval": "NOT_GRANTED"
  },
  "material_profiles": {},
  "options": []
}
```

Each pass owns independent profile IDs. Its `options` use the established `semantic-composition.json` schema, including `pair_id`, source-use explanations (enhanced only), eight optional functional module slots with proper gaps, per-node material effects and the same complete nine-stage Story Spine. The `options` must be at least two substantively distinct plans. The model should not mechanically lock to four small emotion lines or precisely two large arcs outside pilot validators; where the pilot forces those counts, explicitly label the scope and log the gap.

## Settlement timing gate

An enhanced macro may enter `PAID` only if all required conditions are witnessed by nodes **at or before** the `PAID` transition. For each paid macro add:

```json
"required_settlement_conditions": [
  {"condition_id": "family_safe", "description": "family is safe", "witness_node_id": "N08"},
  {"condition_id": "formal_qualification", "description": "qualification formally takes effect", "witness_node_id": "N09"}
]
```

`PAID` at N08 fails if qualification only takes effect at N09. A partial result should be `PARTIALLY_PAID`; correct the state timing rather than erase a promised condition. This is a **chronological/structure** gate, not automated proof that a literary sentence is true: the independent reviewer must inspect each witness node's event/consequence and the promised payoff.

## Audit and stop conditions

- The legacy prompt must not contain EL/EW/MA/AH retrieval. Log `independence=REQUESTED_NOT_MACHINE_PROVEN` unless separate invocation histories actually establish isolation. Same brief hash does not by itself establish fair blinded comparison.
- Retrieved candidates are `candidate/HOLD`. `AH:BOOK_001:001` remains an observed overlap/reference with `CANDIDATE_UNVERIFIED`, never an approved dominance-handoff example.
- If no eligible emotion evidence, incompatible materials, changed source hash, invalid candidate citation, breached promise, leaked reveal, or repeated model repair failure: report a specific HOLD; do not auto-promote.
- All output remains research-only; no production schema, formal Planner command, RMF, canonical, 01–09 sources, novel prose, or main-branch mutation.
- `EMOTION_FIRST_WORKFLOW=RESEARCH_EXECUTABLE` can be claimed only after a real host-model pass produces both fragments and finalize passes on the frozen sources. Merely writing prompts or passing unit tests is **`ORCHESTRATION_IMPLEMENTED / END_TO_END_NOT_YET_RUN`**.
- `CREATIVE_QUALITY=PENDING_INDEPENDENT_REVIEW`; `PRODUCTION_PROMOTION=NOT_RUN`; `STAGE_4_CREATION=HOLD`.

## Minimal quality tests

- User sparse input must not contain prewritten plot facts.
- Independent baseline is prompted before enhanced; retrieval never leaks into its prompt.
- Enhanced source IDs must resolve to frozen retrieval.
- Material choices and rejections must resolve to genuine 02–09 candidates or remain `ORIGINAL_DESIGN`.
- Two outputs must differ in causal engines, not only surface nouns.
- A PAID state with an essential settlement witness in a later node must fail.
- Same model/seed/material budget should be used when independently testing any creative superiority claim.
- Successful research execution does not establish 50/500 chapter reader retention.

Use the existing `scripts/test_emotion_story_bridge.py` and the new `scripts/test_emotion_first_workflow_v1.py` before any claim of working integration.
