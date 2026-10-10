# Independent LEGACY_BASELINE creative pass (RESEARCH ONLY)

Same frozen sparse brief for both passes (SHA-256 canonical JSON: 400ff445aa7ae0b6336a78c022dcd395aff2daeb399ebcb8225474ea86fe3116).

{
  "schema_version": "sparse_emotion_brief_v1",
  "brief_id": "SEB:TRUST_AND_PROTECTION:V1",
  "input_mode": "SPARSE_EMOTION_BRIEF",
  "status": "candidate",
  "genre": [
    "玄幻",
    "高武"
  ],
  "core_reader_expectation": "主角在被亲近之人误解后，通过有代价的行动重建信任，让家人从互相防备转向共同抵御真正的危险",
  "emotion_contour": [
    "DOWN",
    "DOWN",
    "UP"
  ],
  "required_emotion_weaves": [
    "家庭保护的承诺必须形成可见的安全变化",
    "能力成长必须承担可以影响后续选择的代价",
    "家人与主角的关系要能主动改变行动方案",
    "长期势力压力必须由当期决定产生而非空降新敌"
  ],
  "longform_requirement": "本阶段兑现家人的安全与关系变化之前，下一大情绪弧可以留下可信触发，但不可取消原有承诺；先规划50章及后续延续条件",
  "forbidden_prefill": "尚未选择人物姓名、具体敌人、金手指、势力结构、具体故事节点或下一弧主题"
}

You are the SEMANTIC COMPOSER, not the source validator. Produce a standalone JSON
fragment with exactly: schema_version='emotion_story_composer_fragment_v1',
brief_id, mode='LEGACY_BASELINE', status='candidate', semantic_composer={'kind':
'MODEL_AUTHORED_RESEARCH_CANDIDATE','model_family':<truthful model name>,
'literary_approval':'NOT_GRANTED'}, material_profiles, options (at least two).

Each option must meet the EXISTING emotion-story-bridge contract: ≥7 causal nodes,
nine-stage Story Spine, concrete 1–50 chapter phases, 02–09 functional slots, node-local
material effects, independent relationships and realistic costs. Both options must
have substantively different causal engines, not mere names. Use existing bridge
fixtures ONLY as schema examples; never transplant their story premises.

Work with existing 02–09 search tools from material-dispatch.md. Source IDs you
select/reject must really occur in the search results; do not invent. Missing or
incompatible sources become explicit ORIGINAL_DESIGN gaps. Every material has
an actionable role at specified story nodes. Keep candidates HOLD, no prose.

You must create the JSON artifact yourself in the research workspace. The user
must not hand-author a long semantic-composition file.

## Isolation
This pass may use 02–09 sources but MUST NOT read EL/EW/MA/AH retrieval, E2/E3 patterns or the enhanced candidate. Compose independently from the sparse brief. `options[*].mode` must be `LEGACY_BASELINE`. Do not add emotion_source_uses/emotion_lines/weaves/macro_arcs/handoff to legacy options.
