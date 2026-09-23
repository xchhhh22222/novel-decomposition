# 人物功能横向拆解专项输出契约

## 1. 权威关系与统一 envelope

本文件是 `novel-character-function-miner` 的专项记录契约，不覆盖总控契约，也不修改人物库、章节事实或其它专项的 canonical schema。所有记录必须同时满足：

- `skills/novel-dna-orchestrator/SKILL.md` 的总控要求；
- `skills/novel-dna-orchestrator/references/horizontal-specialist-contract.md` 的派生记录要求；
- `skills/novel-dna-orchestrator/references/integration-and-qa.md` 的证据、状态和阶段门要求；
- `skills/novel-character-function-miner/SKILL.md` 的人物功能边界。

除上位契约明确规定的 canonical 权威记录外，本专项所有机器可读记录都使用统一 envelope：

```json
{
  "record_type": "per_book|nearest_neighbor|cluster|qa|handoff|gap",
  "schema_version": 1,
  "record_id": "CF:<TYPE>:<STABLE_ID>",
  "status": "candidate",
  "book_id": "BOOK_01",
  "book_ids": ["BOOK_01", "BOOK_02"],
  "evidence_refs": ["BOOK_01:CHAPTER:0001", "BOOK_01:STAGE:01"],
  "unknowns": [],
  "confidence": "HIGH|MEDIUM|LOW",
  "qa_status": "PASS|HOLD|FAIL"
}
```

实际记录按作用只使用 `book_id` 或 `book_ids` 其中之一，不要求同时出现：

- `per_book`、`qa`、`handoff` 和 `gap` 通常使用 `book_id`；
- `nearest_neighbor` 和 `cluster` 通常使用 `book_ids`。

统一约束：

1. `status` 只能为 `candidate`，本文件不定义 `active`、`deprecated` 或正式素材库写入字段；
2. `evidence_refs` 必须能回到章节、阶段或已存在的情绪 overlay；
3. `unknowns` 只记录真实缺口，不能把模型推测填入缺口；
4. `HIGH` 不得包含会改变人物功能、关系发动机、功能转变或替代性判断的关键 `UNKNOWN`；
5. `partial`、`UNKNOWN`、`gap`、`HOLD` 和 `FAIL` 必须显式保留，不得用空字符串伪装确定；
6. 单个功能、关系功能或关系发动机都可以有多个证据引用；单次行为不足以自动形成长期功能或长期发动机。

## 2. 八类专项记录

人物专项的最小分析单位不是姓名、性格或身份，而是“人物如何持续改变故事运行”。`per_book` 必须分别承载以下八类对象，避免退化成传统人物卡。

### 2.1 `identity_facts`

`identity_facts` 只用于定位人物和解释证据背景，不直接等于剧情功能：

```json
{
  "fact_id": "CF:IDENTITY:001",
  "person_id": "PERSON_01",
  "fact": "有章节证据支持的公开身份、阵营或特殊身份",
  "fact_scope": "公开身份|阵营|特殊身份|与主角的定位关系",
  "evidence_refs": ["BOOK_01:CHAPTER:0003"],
  "unknowns": []
}
```

职业、头衔、血缘、阵营、性格和实力可以作为事实或定位信息，但不能仅凭这些字段生成 `narrative_functions`、`relationship_functions` 或 `relationship_engines`。

### 2.2 `narrative_functions`

同一人物可以有多条 `narrative_functions`。每条功能必须说明人物实际做了什么、作用于谁以及适用的阶段或当前状态：

```json
{
  "function_id": "CF:FUNCTION:001",
  "person_id": "PERSON_01",
  "function_type": "mentor|rival|obstacle|validator|resource_entry|information_entry|threat_generator|protector|emotion_bearer|other",
  "actual_operation": "该人物通过什么可观察行为推动、阻碍、验证或改变剧情",
  "target": "主角、另一人物、线路目标、资源流或信息流",
  "phase_scope": "章节或阶段范围；不清楚时为 UNKNOWN",
  "function_state": "observed|emerging|weakened|ended|UNKNOWN",
  "evidence_refs": ["BOOK_01:CHAPTER:0010", "BOOK_01:CHAPTER:0014"],
  "unknowns": []
}
```

`function_type` 是检索和比较用的功能分类，不是凭标签自动赋值的名单。`actual_operation`、`target` 和 `evidence_refs` 缺一时，不能把该记录升级为确定功能。`function_state` 只描述该功能在当前证据范围中的观察状态，不改变统一 envelope 的 `status`。

### 2.3 `relationship_functions`

`relationship_functions` 描述人物在一段具体关系中实际承担的作用，不等同于人物对主角的静态态度：

```json
{
  "relationship_function_id": "CF:REL_FUNCTION:001",
  "relation_id": "CF:RELATION:001",
  "person_id": "PERSON_01",
  "counterparty_id": "PROTAGONIST",
  "function_type": "pressure_source|access_gate|validator|protector|competitor|information_filter|resource_broker|emotional_anchor|other",
  "relational_operation": "这段关系中人物实际施加、提供、阻断或验证了什么",
  "observable_change": "关系行为造成的选择、资源、信息、风险、目标或状态变化",
  "phase_scope": "章节或阶段范围",
  "evidence_refs": ["BOOK_01:CHAPTER:0018"],
  "unknowns": []
}
```

“喜欢”“讨厌”“亲属”“同队”“上下级”可以作为关系事实或证据背景，但不能单独充当 `relationship_function`，更不能自动充当 `relationship_engine`。

### 2.4 `function_combinations`

`function_combinations` 记录同一人物多个功能如何联动，禁止强制一人一个标签：

```json
{
  "combination_id": "CF:COMBINATION:001",
  "person_id": "PERSON_01",
  "function_ids": ["CF:FUNCTION:001", "CF:FUNCTION:002"],
  "combined_operation": "多个功能如何互相强化、冲突或在同一事件中共同改变剧情",
  "trigger_or_condition": "组合同时生效所需的已观察条件",
  "observable_outputs": ["主角被迫改变选择", "信息验证与资源交换同时发生"],
  "evidence_refs": ["BOOK_01:CHAPTER:0022"],
  "unknowns": []
}
```

只有一个功能的记录不应伪装成组合。若多个标签只是模型把身份、性格或出场频率重复命名，必须退回 `qa` 或 `gap`，不能形成组合候选。

### 2.5 `function_transitions`

功能转变必须保存“前状态 → 触发事件 → 后状态 → 证据”的链条：

```json
{
  "transition_id": "CF:TRANSITION:001",
  "person_id": "PERSON_01",
  "before_function": "竞争者",
  "trigger_event": "有证据的事件、选择、冲突结果或关系变化",
  "after_function": "验证者",
  "stage_scope": "章节或阶段范围",
  "protagonist_interface_change": "转变如何改变主角的选择、资源、风险、认知、目标或反馈",
  "evidence_refs": ["BOOK_01:CHAPTER:0026", "BOOK_01:CHAPTER:0027"],
  "unknowns": []
}
```

不能只写“后来变成盟友”“关系变好了”或“人物成长了”。若触发事件、行为变化或关系后果缺乏章节/阶段证据，转变必须标为 `UNKNOWN` 或进入 `gap`，不得凭主观概括补齐。

### 2.6 `replaceability`

替代性是功能判断，不是人物价值评分。至少区分：

```json
{
  "replaceability_id": "CF:REPLACEABILITY:001",
  "person_id": "PERSON_01",
  "function_id": "CF:FUNCTION:001",
  "replaceability": "replaceable|identity_bound|non_replaceable|UNKNOWN",
  "substitution_condition": "同类人物能够替代该功能所需的条件；不确定时为 UNKNOWN",
  "binding_features": ["特定身份", "独有秘密", "专属资源", "权力位置", "血缘", "历史关系"],
  "reasoning": "依据哪些剧情事实判断该功能可以替代或绑定于此人",
  "evidence_refs": ["BOOK_01:CHAPTER:0031"],
  "unknowns": []
}
```

`replaceable` 表示已有证据支持“同类角色可以完成”；`identity_bound` 表示功能依赖某项特定身份、秘密、资源、权力、血缘或历史关系；`non_replaceable` 只在证据足以证明替代会破坏核心关系、资源或信息位置时使用。没有依据时使用 `UNKNOWN`，不能用“重要”“核心”“出场多”替代论证。

### 2.7 `protagonist_interface`

`protagonist_interface` 分离记录人物对主角状态的影响类型，但不把这些接口扩写为线路、世界观、修炼或情绪专项的正式业务字段：

```json
{
  "interface_id": "CF:INTERFACE:001",
  "person_id": "PERSON_01",
  "target": "PROTAGONIST",
  "choices": "人物如何迫使、诱导、限制或验证主角的选择",
  "resources": "人物如何提供、阻断、交换或改变资源条件",
  "risks": "人物如何增加暴露、代价、限制或失败风险",
  "cognition_information": "人物如何改变主角的认知、信息差或判断",
  "goals": "人物如何改变主角的目标、优先级或推进路径",
  "relationship_emotional_feedback": "关系行为造成的确认、动摇、压力、债务或兑现反馈",
  "evidence_refs": ["BOOK_01:CHAPTER:0035"],
  "unknowns": []
}
```

每个非空接口字段都必须有可观察后果和证据。`relationship_emotional_feedback` 只能描述对主角的关系反馈，不直接声明读者情绪；读者情绪只通过既有 overlay 引用衔接。

### 2.8 `relationship_engines`

关系发动机解释“为什么这段关系还能继续制造剧情”，而不是给关系贴态度标签：

```json
{
  "engine_id": "CF:ENGINE:001",
  "relation_id": "CF:RELATION:001",
  "relation_sides": ["PERSON_01", "PROTAGONIST"],
  "engine_type": "interest|misunderstanding|competition|protection|debt|secret|identity_gap|shared_goal|complementary_ability|other",
  "sustaining_condition": "使该关系在后续仍会继续产生剧情的条件",
  "recurring_plot_generation": "该发动机如何反复制造行动、冲突、选择、兑现或状态变化",
  "observable_outputs": ["资源交换", "目标冲突", "信息揭示", "风险转移"],
  "engine_state": "recurring|dormant|ended|UNKNOWN",
  "evidence_refs": ["BOOK_01:CHAPTER:0038", "BOOK_01:CHAPTER:0042"],
  "unknowns": []
}
```

一个关系可以有多个发动机，但每个发动机都要单独取证。喜欢、讨厌、亲属、同队、同框、一次帮助或一次争吵本身不能填充 `engine_type`；如果没有持续条件和重复剧情输出，只能记录为一次关系事件或 `UNKNOWN`。

## 3. `per_book` 单书记录

每本目标书必须有一条 `record_type: per_book`，或在无法核验时有一条 `record_type: gap`；同一目标书在同一冻结范围内不能两者并存。

```json
{
  "record_type": "per_book",
  "schema_version": 1,
  "record_id": "CF:BOOK:BOOK_01",
  "status": "candidate",
  "book_id": "BOOK_01",
  "title": "仅作定位，不参与功能聚类",
  "chapters_covered": "1-120",
  "person_scope": ["PERSON_01", "PERSON_02"],
  "identity_facts": [],
  "narrative_functions": [],
  "relationship_functions": [],
  "function_combinations": [],
  "function_transitions": [],
  "replaceability": [],
  "protagonist_interface": [],
  "relationship_engines": [],
  "emotion_overlay_links": [],
  "adjacent_interfaces": {
    "plotline": [],
    "arc_structure": [],
    "plot_mechanism": [],
    "worldbuilding": [],
    "cultivation": [],
    "golden_finger": [],
    "chapter_emotion": []
  },
  "source_numbering_notes": [],
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "PASS"
}
```

字段要求：

- `person_scope` 只列允许来源中实际进入分析范围的人物，不根据简介扩展角色名单；
- `identity_facts` 是定位证据，不能自动复制到 `narrative_functions`；
- 八类专项数组可以为空，但若核心人物功能无法确认，必须在 `unknowns` 或单独 `gap` 说明原因；
- `emotion_overlay_links` 只引用已有情绪记录及其关系效果，不复制章节情绪字段；
- `adjacent_interfaces` 只能存接口或证据引用，不能承载其它专项的正式业务结论；
- `title`、姓名和专名只用于回溯与定位，不参与母型命名、相似度或聚类标签。

## 4. `gap` 缺口记录

证据不足时保留缺口，不用模型常识补齐人物功能：

```json
{
  "record_type": "gap",
  "schema_version": 1,
  "record_id": "CF:GAP:BOOK_01",
  "status": "candidate",
  "book_id": "BOOK_01",
  "evidence_refs": ["BOOK_01:CHAPTER:0001"],
  "unknowns": ["关键人物的持续资源流", "关系发动机是否在后续重复生效"],
  "confidence": "LOW",
  "qa_status": "HOLD",
  "reason": "已有证据只能确认人物出现，不能确认持续剧情功能",
  "known_evidence": ["确认人物在一次冲突中出现"],
  "blocked_outputs": ["高置信 per_book", "nearest_neighbor", "cluster"]
}
```

`gap` 必须说明缺口位置、已知证据和被阻断的下游判断；它不是写入虚构人物卡的占位符。

## 5. `nearest_neighbor` 近邻记录

近邻只能在所有目标书完成同类单书抽取和 QA 后生成，且必须通过 cross-book completion gate。比较的是功能的运行方式：

```json
{
  "record_type": "nearest_neighbor",
  "schema_version": 1,
  "record_id": "CF:NEIGHBOR:001",
  "status": "candidate",
  "book_ids": ["BOOK_01", "BOOK_02"],
  "comparison_ids": ["CF:BOOK:BOOK_01", "CF:BOOK:BOOK_02"],
  "comparison_dimensions": {
    "function_composition": "多个功能如何组合并产生可见剧情效果",
    "relationship_engines": "关系发动机的持续条件和重复输出",
    "function_transitions": "功能转变的触发方式和阶段位置",
    "replaceability": "功能绑定身份/秘密/资源/关系的程度",
    "protagonist_interface": "人物改变主角状态的接口组合"
  },
  "similarities": [],
  "difference_boundary": "决定保持相近但不合并的核心差异",
  "surface_labels_excluded": ["导师", "妹妹", "队友", "反派", "青梅"],
  "decision": "merge_candidate|keep_distinct|insufficient_evidence",
  "reason": "比较理由",
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "PASS"
}
```

不能只因两本书都有导师、妹妹、队友、反派、青梅或同一职业就生成近邻。必须说明功能组合、关系发动机、转变、替代性或主角接口至少一项运行方式的相似与差异。

## 6. `cluster` 聚类候选

聚类必须在所有目标书完成单书 QA 与近邻比较后生成，且只能是 candidate：

```json
{
  "record_type": "cluster",
  "schema_version": 1,
  "record_id": "CF:CLUSTER:001",
  "status": "candidate",
  "book_ids": ["BOOK_01", "BOOK_02"],
  "member_record_ids": ["CF:BOOK:BOOK_01", "CF:BOOK:BOOK_02"],
  "cluster_level": "大类|母型|子型|变体",
  "label": "不复制专名的功能性名称",
  "shared_operation": "功能组合、关系发动机和阶段变化共同形成的运行方式",
  "engine_pattern": "关系如何持续制造行动、冲突、选择、兑现或状态变化",
  "transition_pattern": "功能转变的共同触发条件及其边界",
  "replaceability_boundary": "哪些功能可替代，哪些绑定特定身份/秘密/资源/关系",
  "protagonist_interface_pattern": "人物对主角状态造成的共同影响结构",
  "boundary_conditions": ["与相近候选保持区分的证据条件"],
  "supporting_book_count": 2,
  "nearest_neighbor_record_ids": ["CF:NEIGHBOR:001"],
  "merge_decision": "candidate_merge|candidate_split|new_candidate|insufficient_evidence|keep_distinct",
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "PASS"
}
```

`shared_operation` 必须描述人物功能和关系发动机如何运行，不能只写“导师型”“校园队友”“反派角色”或其它表面标签。单书候选不能自动升级为高频母型，也不能写成 `active`。

## 7. `qa` 与 `handoff` 记录

### `qa`

```json
{
  "record_type": "qa",
  "schema_version": 1,
  "record_id": "CF:QA:BOOK_01:1-120",
  "status": "candidate",
  "book_id": "BOOK_01",
  "scope": "BOOK_01:1-120",
  "checks": {
    "coverage": "PASS|HOLD|FAIL",
    "identity_function_separation": "PASS|HOLD|FAIL",
    "function_evidence": "PASS|HOLD|FAIL",
    "combination_evidence": "PASS|HOLD|FAIL",
    "transition_chain": "PASS|HOLD|FAIL",
    "relationship_engine_recurrence": "PASS|HOLD|FAIL",
    "replaceability_evidence": "PASS|HOLD|FAIL",
    "protagonist_interface": "PASS|HOLD|FAIL",
    "adjacent_boundary": "PASS|HOLD|FAIL",
    "cross_book_gate": "PASS|HOLD|FAIL"
  },
  "gaps": [],
  "disputes": [],
  "blocked_outputs": [],
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "PASS"
}
```

QA 至少检查：

1. identity facts 是否被误写为功能；
2. 功能是否由行为、选择、资源流、信息流、冲突结果或关系变化支撑；
3. 一个角色的多功能是否分别取证；
4. function transition 是否具备 before → trigger → after → evidence；
5. relationship engine 是否有 sustaining condition 和 recurring plot output；
6. replaceability 是否有替代条件和绑定依据；
7. 主角接口是否记录可见后果而不是空泛态度；
8. 是否越界复制线路、篇章、制度、修炼、金手指或读者情绪结论；
9. 跨书记录是否满足全部目标书完成后的阶段门。

### `handoff`

```json
{
  "record_type": "handoff",
  "schema_version": 1,
  "record_id": "CF:HANDOFF:001",
  "status": "candidate",
  "book_ids": ["BOOK_01"],
  "candidate_record_ids": ["CF:BOOK:BOOK_01"],
  "recommended_action": "保留|合并候选|拆分候选|补证据|暂缓",
  "decision_points": ["需要人工确认的功能或关系边界"],
  "evidence_summary": ["支持候选的关键行为与关系证据"],
  "boundary_warnings": ["可能与相邻专项重叠的接口"],
  "blocked_by": [],
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "HOLD"
}
```

`handoff` 只把候选、证据、争议、边界和待决策项交给人工，不自动把人物功能写进正式人物库或素材库。

## 8. 状态、证据与跨专项边界

- `identity_facts`、`narrative_functions`、`relationship_functions`、`function_combinations`、`function_transitions`、`replaceability`、`protagonist_interface` 和 `relationship_engines` 都必须能回到真实证据；
- 性格、身份、实力、出场频率、名字、简介和人物标签不是功能的替代证据；
- 一次帮助不能自动建立长期 `resource_entry`，一次争吵不能自动建立稳定 `relationship_engine`；
- `relationship_functions` 可以引用线路或情绪的结果，但不重做 `plotline` 生命周期和 `chapter-emotion` 读者情绪；
- 人物所属组织、能力、资源或金手指接口只能作为边界引用，不能改写成世界观、修炼或金手指专项记录；
- 所有缺失证据必须进入 `unknowns`、`gap` 或 `HOLD`，不能用跨书类比补齐；
- `nearest_neighbor` 和 `cluster` 的相似度必须建立在功能组合、关系发动机、功能转变、替代性或主角接口的运行方式上，不能建立在角色名词相同上；
- 本专项没有正式素材库写入字段，也不负责任何状态升级、卡片合并或索引重建。

本 schema 只冻结人物功能专项的记录结构和五类派生交付契约。具体聚类评分、QA 判定顺序、validator 硬约束和 agent 调用说明必须在后续文件中分别设计、测试和验收。
