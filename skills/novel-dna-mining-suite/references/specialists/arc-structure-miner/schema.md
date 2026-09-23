# 篇章阶段结构横向拆解专项输出契约

## 1. 权威关系与统一 envelope

本文件是 `novel-arc-structure-miner` 的专项记录契约，不覆盖总控契约，也不修改章节事实、剧情线、开篇、人物、情绪、世界观、修炼体系、金手指或剧情机制的 canonical schema。所有记录必须同时满足：

- `../../../SKILL.md` 的总控要求；
- `../../core/horizontal-specialist-contract.md` 的派生记录要求；
- `../../core/integration-and-qa.md` 的证据、状态和阶段门要求；
- `guidance.md` 的阶段结构边界和十类观察对象。

除上位契约明确规定的 canonical 权威记录外，本专项所有机器可读记录都使用统一 envelope：

```json
{
  "record_type": "per_book|nearest_neighbor|cluster|qa|handoff|gap",
  "schema_version": 1,
  "record_id": "AR:<TYPE>:<STABLE_ID>",
  "status": "candidate",
  "book_id": "BOOK_01",
  "book_ids": ["BOOK_01", "BOOK_02"],
  "evidence_refs": ["BOOK_01:CHAPTER:0001", "BOOK_01:STAGE:01"],
  "unknowns": [],
  "confidence": "HIGH|MEDIUM|LOW",
  "qa_status": "PASS|HOLD|FAIL"
}
```

实际记录按作用只使用 `book_id` 或 `book_ids` 其中之一：

- `per_book`、`qa` 和 `gap` 通常使用 `book_id`；
- `nearest_neighbor`、`cluster` 和 `handoff` 通常使用 `book_ids`。

统一约束：

1. `status` 只能为 `candidate`；本专项不定义 `active`、`deprecated` 或正式素材库写入字段；
2. `evidence_refs` 必须能回到章节、阶段或已有专项接口；
3. `unknowns` 只记录真实证据缺口，不得把推测写入缺口；
4. `HIGH` 不得包含会改变 arc 边界、阶段结局、状态变化、下一入口或嵌套关系的关键 `UNKNOWN`；
5. `partial`、`UNKNOWN`、`gap`、`HOLD` 和 `FAIL` 必须显式保留；
6. 卷名、地图名、境界名、时间段和章节范围只能作定位，不能独立证明 arc。

## 2. Arc identity 与阶段生命周期

### 2.1 `arc_identity`

```json
{
  "arc_id": "AR:ARC:001",
  "arc_label": "仅作定位的功能性名称",
  "arc_scope": "章节、阶段、地图或全局结构范围",
  "arc_purpose": "在当前证据范围内追踪的阶段结构作用",
  "arc_kind": "main|sub|parallel|UNKNOWN",
  "parent_arc_id": "AR:ARC:000 或 UNKNOWN",
  "evidence_refs": ["BOOK_01:CHAPTER:0001"],
  "unknowns": []
}
```

`arc_label`、卷名、地图名和题材名只用于定位，不参与近邻或聚类标签；`arc_kind` 不能替代结构证据。

### 2.2 `arc_lifecycle`

正式状态必须区分阶段的启动、推进、转向和不同收束结局：

```json
{
  "current_state": "not_started|active|paused|redirected|resolved|failed|abandoned|unresolved|UNKNOWN",
  "state_history": [
    {
      "state": "active",
      "trigger_or_reason": "进入该阶段状态的结构事件、目标、压力、转折或收束原因",
      "phase_scope": "章节或阶段范围",
      "evidence_refs": ["BOOK_01:CHAPTER:0003"],
      "unknowns": []
    }
  ],
  "unknowns": []
}
```

`resolved` 表示阶段任务或结构作用得到确认的收束；`failed` 表示阶段目标或结构任务失败；`abandoned` 表示人物、势力或叙事方向主动放弃；`redirected` 表示阶段方向被结构性改变；`unresolved` 表示阶段仍有关键结构问题未收束。不得用一个模糊状态合并成功、失败、放弃、转向和未决。

## 3. 十类阶段结构对象

### 3.1 `arc_boundary`

边界必须保存前后结构差异：

```json
{
  "boundary_id": "AR:BOUNDARY:001",
  "before_structure": "边界前的目标、压力、线路组织、权限、地图、关系或全局结构",
  "after_structure": "边界后的目标、压力、线路组织、权限、地图、关系或全局结构",
  "triggering_change": "造成阶段边界的实际变化、收束余波、重心迁移或权限变化",
  "chapter_or_stage_scope": "章节或阶段范围",
  "structural_difference": "为什么前后已经不是同一个结构阶段",
  "evidence_refs": ["BOOK_01:CHAPTER:0030"],
  "unknowns": []
}
```

卷名变化、日期跳转、地图切换、章节编号或境界提升如果没有 `structural_difference`，不能单独成立 `arc_boundary`。

### 3.2 `arc_goal`

阶段目标是组织多条线路和结构压力的主推进方向：

```json
{
  "goal_id": "AR:GOAL:001",
  "primary_goal_or_structural_task": "阶段承担的主目标或结构任务",
  "serves_or_organizes": ["被组织的线路、人物目标、资源门槛或读者承诺"],
  "phase_scope": "章节或阶段范围",
  "completion_condition": "什么结构证据可以确认阶段目标或任务得到结果",
  "invalidation_or_failure_condition": "什么证据会使目标失效、失败、放弃或转向",
  "goal_status": "open|shifted|resolved|failed|abandoned|UNKNOWN",
  "evidence_refs": ["BOOK_01:CHAPTER:0032"],
  "unknowns": []
}
```

`primary_goal_or_structural_task` 不能只复制某条剧情线的单一目标；阶段可以包含多个局部目标，但需要说明它们如何服务或改变阶段主目标。

### 3.3 `arc_pressure`

阶段压力必须说明运作方式和可观察影响：

```json
{
  "pressure_id": "AR:PRESSURE:001",
  "pressure_source_or_type": "资源、制度、敌对势力、时间、关系、身份、地图、成长门槛或目标冲突",
  "operation": "压力如何持续施加、提高门槛、限制权限或迫使阶段改变推进方式",
  "affected_targets": ["阶段目标、线路、人物、资源、关系或全局局势"],
  "observable_effect": "目标、资源、信息、风险、权限、线路重心或选择发生的可观察改变",
  "phase_scope": "章节或阶段范围",
  "evidence_refs": ["BOOK_01:CHAPTER:0035"],
  "unknowns": []
}
```

敌人名单、困难列表、地点或场景不能在没有持续作用时直接成为 arc pressure。

### 3.4 `arc_progression`

推进不是事件数组，而是阶段状态前后变化：

```json
{
  "progression_id": "AR:PROGRESSION:001",
  "before_stage_state": "推进步骤发生前的阶段目标、压力、线路组织、资源或全局状态",
  "progression_step": "造成推进的实际事件、选择、线路交汇、验证、扩张或收缩",
  "after_stage_state": "推进步骤之后的阶段目标、压力、线路组织、资源或全局状态",
  "structural_effect": "这一步如何升级、扩张、验证、转向、重组或收束阶段",
  "phase_scope": "章节或阶段范围",
  "evidence_refs": ["BOOK_01:CHAPTER:0040"],
  "unknowns": []
}
```

重复战斗、章节数量、地图面积、敌人数量或事件密度不能自动替代 `before_stage_state → progression_step → after_stage_state → structural_effect`。

### 3.5 `arc_turning_points`

每个阶段可以有多个转折，但每个转折都必须体现阶段级方向变化：

```json
{
  "turning_point_id": "AR:TURN:001",
  "turning_event": "真正造成阶段重心变化的事件、选择、失败、揭示或权限变化",
  "before_direction_or_priority": "转折前阶段目标、重心、路线、压力或权限",
  "after_direction_or_priority": "转折后阶段目标、重心、路线、压力或权限",
  "structural_effect": "它如何改变阶段组织、线路关系、风险、地图、身份或下一步",
  "phase_scope": "章节或阶段范围",
  "evidence_refs": ["BOOK_01:CHAPTER:0048"],
  "unknowns": []
}
```

普通高潮、一次升级、一次战斗或单个反转只有造成上述阶段级差异时，才可以记录为 turning point。

### 3.6 `arc_climax_or_resolution`

高点和收束必须区分结局类型：

```json
{
  "resolution_id": "AR:RESOLUTION:001",
  "climax_or_resolution_event": "达到高点、完成任务、失败、放弃、转向或留下未决的事件",
  "resolution_outcome": "resolved|failed|abandoned|redirected|unresolved|UNKNOWN",
  "resolved_or_unresolved_structure": "阶段解决了什么、失败了什么、转向了什么或留下什么问题",
  "affected_arc_goal_ids": ["AR:GOAL:001"],
  "phase_scope": "章节或阶段范围",
  "evidence_refs": ["BOOK_01:CHAPTER:0055"],
  "unknowns": []
}
```

局部剧情线的 payoff 不自动等于 arc resolution；阶段也不要求必须以胜利高潮结束。

### 3.7 `arc_state_change`

状态变化独立于收束结果：

```json
{
  "state_change_id": "AR:STATE:001",
  "caused_by_resolution_or_turning_point": "AR:RESOLUTION:001 或 AR:TURN:001",
  "changed_domains": ["goal", "resource", "identity", "relationship", "cognition", "map", "permission", "risk", "faction_balance", "situation"],
  "before_global_state": "阶段转折或收束前全局相关状态",
  "after_global_state": "阶段转折或收束后全局相关状态",
  "structural_effect": "全局状态如何改变后续阶段的目标、压力、权限、线路或读者期待",
  "evidence_refs": ["BOOK_01:CHAPTER:0056"],
  "unknowns": []
}
```

不能只写“进入下一卷”“换地图”或“开始新任务”；必须说明阶段前后目标、资源、身份、关系、认知、地图、权限、风险、势力或局势的实际差异。

### 3.8 `next_arc_entry`

下一阶段入口必须来自已有阶段状态变化：

```json
{
  "entry_id": "AR:ENTRY:001",
  "source_state_change_id": "AR:STATE:001",
  "opened_next_arc_goal_or_task": "下一阶段打开的目标、任务或结构问题",
  "opened_pressure_or_risk": "随入口出现的压力、风险、制度门槛或资源问题",
  "opened_map_permission_or_question": "新地图、权限、信息问题或结构入口；没有时为 UNKNOWN",
  "next_arc_reference": "被打开的 arc 或 sub-arc；不确定时为 UNKNOWN",
  "entry_reason": "为什么上一阶段状态变化自然产生这个下一入口",
  "evidence_refs": ["BOOK_01:CHAPTER:0057"],
  "unknowns": []
}
```

`source_state_change_id` 不能缺失或凭空指向不存在的状态变化；同一收束事件不能只改名后重复写成 next entry。

### 3.9 `arc_function`

```json
{
  "function_id": "AR:FUNCTION:001",
  "structural_function": "establish|expand|validate|upgrade|reverse|expose|reorganize|transition|resolve|ending_setup|other|UNKNOWN",
  "function_description": "该阶段在全书结构中承担的具体作用",
  "affected_global_expectation": "阶段如何改变全书主线、读者期待、风险或后续结构",
  "phase_scope": "章节或阶段范围",
  "evidence_refs": ["BOOK_01:CHAPTER:0020"],
  "unknowns": []
}
```

学院、秘境、战争、考试等名称只能作定位，不能替代 `structural_function`。

### 3.10 `nested_structure`

父阶段和子阶段必须分别取证：

```json
{
  "relation_id": "AR:NESTED:001",
  "parent_arc_id": "AR:ARC:001",
  "sub_arc_id": "AR:ARC:002",
  "relation_type": "service|obstacle|change|UNKNOWN",
  "how_sub_arc_affects_parent": "子阶段如何服务、阻碍或改变父阶段的目标、压力、推进或收束",
  "sub_arc_completion_effect": "子阶段完成、失败、放弃或未决对父阶段的实际影响",
  "pause_relationship": "父阶段与子阶段暂停、转向或继续状态是否独立",
  "evidence_refs": ["BOOK_01:CHAPTER:0038"],
  "unknowns": []
}
```

必须遵守：

- sub-arc 完成不等于 parent arc 完成；
- parent arc 暂停不自动暂停所有 sub-arc；
- 共享人物、地点、敌人或卷名不能单独证明 nested 关系；
- 普通章节序列、短期事件或单条剧情线不能自动升级为 sub-arc；
- 禁止自引用和明显循环。

## 4. `per_book` 单书记录

每本目标书必须有一条 `record_type: per_book`，或在无法核验时有一条 `record_type: gap`；同一冻结范围内二者不能并存。

```json
{
  "record_type": "per_book",
  "schema_version": 1,
  "record_id": "AR:BOOK:BOOK_01",
  "status": "candidate",
  "book_id": "BOOK_01",
  "title": "仅作定位，不参与阶段聚类",
  "chapters_covered": "1-120",
  "arcs": [
    {
      "arc_identity": {},
      "arc_boundary": [],
      "arc_goal": [],
      "arc_pressure": [],
      "arc_progression": [],
      "arc_turning_points": [],
      "arc_climax_or_resolution": [],
      "arc_state_change": [],
      "next_arc_entry": [],
      "arc_function": [],
      "nested_structure": [],
      "arc_lifecycle": {}
    }
  ],
  "adjacent_interfaces": {
    "plotline": [],
    "opening": [],
    "character_function": [],
    "chapter_emotion": [],
    "worldbuilding": [],
    "cultivation": [],
    "golden_finger": [],
    "plot_mechanism": []
  },
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "PASS"
}
```

字段约束：

- `arcs` 是单书内多个独立阶段的容器；每个元素的 `arc_identity` 用于定位一个阶段，不能只靠 `arc_label` 证明阶段存在；
- 每个 arc 元素的 `arc_boundary`、`arc_goal`、`arc_pressure`、`arc_progression`、`arc_turning_points`、`arc_climax_or_resolution`、`arc_state_change`、`next_arc_entry`、`arc_function` 和 `nested_structure` 各自保留独立位置；
- 空数组必须与 `unknowns` 或 QA 结论一致，不能伪装为已完成阶段分析；
- `next_arc_entry` 只能引用本地 `arc_state_change.state_change_id`；
- `nested_structure` 只能保存阶段关系和接口说明，不嵌入完整剧情线、人物、世界观或机制对象；
- `title`、阶段名称和专名只用于定位，不参与母型命名、相似度或聚类标签。

### adjacent interface reference 形式

`adjacent_interfaces` 的每个数组元素只能是引用字符串，或下列引用对象：

```json
{
  "record_id": "PL:LINE:001",
  "interface_type": "该专项结果如何服务阶段结构观察",
  "evidence_refs": ["BOOK_01:CHAPTER:0025"],
  "note": "只保留与当前阶段直接相关的接口说明",
  "unknowns": []
}
```

不得在其中复制剧情线、开篇、人物、情绪、世界观、修炼、金手指或剧情机制的完整正式对象。

## 5. `gap` 缺口记录

证据不足时必须说明阻断原因：

```json
{
  "record_type": "gap",
  "schema_version": 1,
  "record_id": "AR:GAP:BOOK_01",
  "status": "candidate",
  "book_id": "BOOK_01",
  "evidence_refs": ["BOOK_01:CHAPTER:0001"],
  "unknowns": ["阶段边界前后的结构差异无法核验"],
  "confidence": "LOW",
  "qa_status": "HOLD",
  "reason": "已有证据只能确认章节或卷名变化，不能确认阶段级目标、压力与状态变化",
  "known_evidence": ["存在卷名或地图变化"],
  "blocked_outputs": ["高置信 per_book", "nearest_neighbor", "cluster"]
}
```

`gap` 不是虚构 arc 的占位符，必须说明已有证据、具体缺口和被阻断的下游判断。

## 6. `nearest_neighbor` 近邻记录

近邻只能在全部目标书完成单书抽取和 QA 后生成，并通过 `cross-book completion gate`：

```json
{
  "record_type": "nearest_neighbor",
  "schema_version": 1,
  "record_id": "AR:NEIGHBOR:001",
  "status": "candidate",
  "book_ids": ["BOOK_01", "BOOK_02"],
  "comparison_ids": ["AR:BOOK:BOOK_01", "AR:BOOK:BOOK_02"],
  "comparison_dimensions": {
    "boundary_and_goal": "阶段如何划界并形成主目标或结构任务",
    "pressure_and_progression": "持续压力如何维持、升级与改变阶段推进",
    "turning_and_resolution": "转折、高点与成功/失败/未决收束如何运行",
    "state_change_and_next_entry": "阶段状态变化如何打开下一阶段",
    "nested_structure": "父 arc 与 sub-arc 如何服务、阻碍或改变彼此",
    "adjacent_interfaces": "线路、开篇、人物、情绪、世界、修炼、外挂与机制如何被阶段组织"
  },
  "similarities": [],
  "difference_boundary": "相近但不合并的阶段结构差异",
  "surface_labels_excluded": ["学院篇", "秘境篇", "比赛篇", "战争篇"],
  "decision": "merge_candidate|keep_distinct|insufficient_evidence",
  "reason": "基于阶段边界、推进、收束和下一入口证据的比较理由",
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "PASS"
}
```

不能只因为两本书都有学院、秘境、比赛或战争场景就生成近邻；必须说明阶段结构运行方式和差异边界。

## 7. `cluster` 聚类候选

聚类必须在全部目标书单书 QA 与近邻比较完成后生成，且只能是 candidate：

```json
{
  "record_type": "cluster",
  "schema_version": 1,
  "record_id": "AR:CLUSTER:001",
  "status": "candidate",
  "book_ids": ["BOOK_01", "BOOK_02"],
  "member_record_ids": ["AR:BOOK:BOOK_01", "AR:BOOK:BOOK_02"],
  "cluster_level": "大类|母型|子型|变体",
  "label": "不复制卷名和表面题材的功能性名称",
  "shared_operation": "边界→目标/压力→推进→转折→收束→状态变化→下一阶段入口的共同运行方式",
  "progression_resolution_pattern": "阶段如何升级、反转、收束并产生全局后果",
  "nested_structure_pattern": "父 arc 与 sub-arc 的共同组织方式及限制",
  "boundary_conditions": ["与相近候选保持区分的证据条件"],
  "supporting_book_count": 2,
  "nearest_neighbor_record_ids": ["AR:NEIGHBOR:001"],
  "merge_decision": "candidate_merge|candidate_split|new_candidate|insufficient_evidence|keep_distinct|unclustered|HOLD",
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "PASS"
}
```

`shared_operation` 必须描述阶段如何运行，不能只写学院、秘境、比赛、战争或其它表面类别；单书候选不能自动升级为高频母型。

## 8. `qa` 与 `handoff` 记录

### 8.1 `qa`

```json
{
  "record_type": "qa",
  "schema_version": 1,
  "record_id": "AR:QA:BOOK_01:1-120",
  "status": "candidate",
  "book_id": "BOOK_01",
  "scope": "BOOK_01:1-120",
  "checks": {
    "arc_boundary": "PASS|HOLD|FAIL",
    "goal_and_pressure": "PASS|HOLD|FAIL",
    "progression": "PASS|HOLD|FAIL",
    "turning_points": "PASS|HOLD|FAIL",
    "climax_or_resolution": "PASS|HOLD|FAIL",
    "state_change": "PASS|HOLD|FAIL",
    "next_arc_entry": "PASS|HOLD|FAIL",
    "arc_function": "PASS|HOLD|FAIL",
    "nested_structure": "PASS|HOLD|FAIL",
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

1. 阶段边界有前后结构差异，不由卷名、日期、地图或章节范围独立决定；
2. arc goal 与单条剧情线目标分开，arc pressure 不是敌人名单；
3. progression 有 `before_stage_state → progression_step → after_stage_state → structural_effect`；
4. turning point 有前后方向、优先级、压力、权限或全局重心变化；
5. resolution 区分 resolved、failed、abandoned、redirected 和 unresolved；
6. arc state change 独立且说明阶段前后全局差异；
7. next arc entry 引用已有 state change，不能凭空接入新阶段；
8. arc function 有结构作用证据，不由表面阶段名称代替；
9. nested relation 有父子作用和独立状态，不能自动传播完成或暂停；
10. 相邻专项只通过 interface/reference 引用；
11. 跨书结果满足全部目标书完成后的阶段门。

### 8.2 `handoff`

```json
{
  "record_type": "handoff",
  "schema_version": 1,
  "record_id": "AR:HANDOFF:001",
  "status": "candidate",
  "book_ids": ["BOOK_01"],
  "candidate_record_ids": ["AR:BOOK:BOOK_01"],
  "recommended_action": "保留|合并候选|拆分候选|补证据|暂缓",
  "decision_points": ["需要人工确认的边界、转折、收束、状态变化或 nested 关系"],
  "evidence_summary": ["支持阶段候选的关键结构证据"],
  "boundary_warnings": ["可能与剧情线、开篇、世界观或卷名整理重叠的接口"],
  "blocked_by": [],
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "HOLD"
}
```

`handoff` 只把候选、证据、争议、边界和待决策项交给人工，不自动把阶段写入正式资料或素材库。

## 9. 状态、证据与跨专项边界

- `arc_boundary` 必须保存前后结构差异和触发变化；
- `arc_goal`、`arc_pressure`、`arc_progression`、`arc_turning_points`、`arc_climax_or_resolution`、`arc_state_change` 和 `next_arc_entry` 不得合并成一段阶段摘要；
- `arc_progression` 不是事件列表，`arc_turning_points` 不是普通高潮列表；
- `arc_climax_or_resolution` 区分成功、失败、放弃、转向和未决，不使用模糊的 `closed`；
- `arc_state_change` 与 `next_arc_entry` 独立且可追溯；
- `next_arc_entry.source_state_change_id` 必须引用本地状态变化；
- `nested_structure` 只记录阶段之间的结构作用，不复制剧情线、人物或剧情机制对象；
- sub-arc 完成不自动等于 parent arc 完成，parent 暂停不自动暂停 sub-arc；
- 所有缺失证据进入 `unknowns`、`gap` 或 `HOLD`，不能跨书补齐；
- `nearest_neighbor` 和 `cluster` 只能比较阶段边界、目标/压力、推进、转折、收束、状态变化、下一入口和嵌套方式；
- 本专项没有正式素材库写入字段，也不负责状态升级、阶段合并或总索引重建。

本 schema 只冻结 arc-structure 专项的阶段身份、十类结构对象、生命周期、嵌套关系、相邻接口和五类派生交付。具体 QA 判定顺序、validator 硬约束和 agent 调用说明必须在后续文件中分别设计、测试和验收。
