# 小说开篇横向拆解专项输出契约

## 1. 权威关系与统一 envelope

本文件是 `novel-opening-miner` 的专项记录契约，不覆盖总控契约，也不修改章节事实、逐章情绪记录、剧情线、人物、世界观、修炼体系、金手指或篇章结构的 canonical schema。所有记录必须同时满足：

- `skills/novel-dna-orchestrator/SKILL.md` 的总控要求；
- `skills/novel-dna-orchestrator/references/horizontal-specialist-contract.md` 的派生记录要求；
- `skills/novel-dna-orchestrator/references/integration-and-qa.md` 的证据、状态和阶段门要求；
- `skills/novel-opening-miner/SKILL.md` 的开篇观察窗口与边界。

除上位契约明确规定的 canonical 权威记录外，本专项所有机器可读记录都使用统一 envelope：

```json
{
  "record_type": "per_book|nearest_neighbor|cluster|qa|handoff|gap",
  "schema_version": 1,
  "record_id": "OP:<TYPE>:<STABLE_ID>",
  "status": "candidate",
  "book_id": "BOOK_01",
  "book_ids": ["BOOK_01", "BOOK_02"],
  "evidence_refs": ["BOOK_01:CHAPTER:0001", "BOOK_01:WINDOW:03"],
  "unknowns": [],
  "confidence": "HIGH|MEDIUM|LOW",
  "qa_status": "PASS|HOLD|FAIL"
}
```

实际记录按作用只使用 `book_id` 或 `book_ids` 其中之一：

- `per_book`、`qa`、`handoff` 和 `gap` 通常使用 `book_id`；
- `nearest_neighbor` 和 `cluster` 通常使用 `book_ids`。

统一约束：

1. `status` 只能为 `candidate`；本专项不定义 `active`、`deprecated` 或正式素材库写入字段；
2. `evidence_refs` 必须能回到章节、阶段或已有 reader-emotion overlay；
3. `unknowns` 只记录真实证据缺口，不得把推测写入缺口；
4. `HIGH` 不得包含会改变开篇运行判断、卖点验证、承诺回收或窗口结论的关键 `UNKNOWN`；
5. `partial`、`UNKNOWN`、`gap`、`HOLD` 和 `FAIL` 必须显式保留；
6. 书名、简介、标签、宣传语和模型记忆不能替代章节或阶段证据。

## 2. 累计观察窗口

开篇使用四个累计 checkpoint，而不是四份互相独立的章节摘要：

```json
{
  "window_id": "OP:WINDOW:03",
  "checkpoint": 3,
  "chapters_covered": "1-3",
  "completed_opening_functions": ["entry", "protagonist_establishment"],
  "incomplete_or_unknown_functions": ["first_payoff"],
  "changes_since_prior_window": "相对前一可用窗口新增或改变的开篇运行内容；首个窗口可写 INITIAL",
  "evidence_refs": ["BOOK_01:CHAPTER:0001", "BOOK_01:CHAPTER:0003"],
  "unknowns": []
}
```

### 2.1 checkpoint 约束

- `checkpoint` 只能是 `3`、`5`、`10` 或 `20`；
- `chapters_covered` 必须表达从开篇起点到该 checkpoint 的累计范围；
- 四个窗口不是四套摘要，不能把每章事件逐条复制进去；
- `completed_opening_functions` 记录截止窗口已经有证据支持的观察对象，不代表整本书完成；
- `incomplete_or_unknown_functions` 记录尚未完成、未出现或证据不足的对象；
- `changes_since_prior_window` 必须说明相对上一可用窗口发生的新增、变化、延迟或回收；
- 缺少正文或章节事实时，允许窗口保留 `UNKNOWN`、`gap` 或低置信，不得用后文倒推；
- 不设置任何窗口评分、综合分数或强制通过等级。

## 3. 十二类开篇对象

### 3.1 `entry`

```json
{
  "entry_id": "OP:ENTRY:001",
  "reader_entry_mechanism": "scene|problem|anomaly|desire|risk|promise|information_gap|mixed|UNKNOWN",
  "entry_event_or_scene": "读者实际进入故事的场面、问题、异常、欲望、风险或承诺",
  "created_problem_anomaly_desire_risk_or_promise": "它让读者开始关心什么",
  "continued_expectation": "进入后由什么期待维持阅读",
  "applicable_window": 3,
  "evidence_refs": ["BOOK_01:CHAPTER:0001"],
  "unknowns": []
}
```

“第一章发生了什么”不能代替 `entry`；单纯标题、简介或宣传语不能作为唯一证据。

### 3.2 `protagonist_establishment`

```json
{
  "establishment_id": "OP:PROTAGONIST:001",
  "observable_behaviors": ["主角实际做出的可观察行为"],
  "key_choices": ["主角主动选择及其后果；没有时为 UNKNOWN"],
  "initial_situation_or_constraints": "主角开篇所处位置、处境、限制或缺口",
  "ability_or_resource_bounds": "能力、资源、权限或行动边界",
  "established_trait_or_function_impression": "读者被建立出的主角印象或功能理解",
  "observable_consequence": "行为、选择或限制怎样改变后续目标、风险、资源或读者判断",
  "applicable_window": 3,
  "evidence_refs": ["BOOK_01:CHAPTER:0002"],
  "unknowns": []
}
```

旁白称主角聪明、冷静、很强或很惨，不能独立成立 `protagonist_establishment`；必须有行为、选择、限制或后果证据。

### 3.3 `premise_exposure`

```json
{
  "premise_id": "OP:PREMISE:001",
  "core_premise": "开篇需要让读者理解的核心题材、世界条件或主要冲突前提",
  "reader_can_understand": "截至当前阶段读者已经能够理解什么",
  "exposure_basis": "event_result|rule_demonstration|explicit_exposition|mixed|UNKNOWN",
  "exposure_stage_or_window": "章节、阶段或 checkpoint",
  "reader_understanding_status": "partial|understood|UNKNOWN",
  "evidence_refs": ["BOOK_01:CHAPTER:0004"],
  "unknowns": []
}
```

该对象只记录读者是否获得足以进入故事的理解，不要求前 3 章理解完整世界观；世界观说明不自动等于 premise exposure。

### 3.4 `golden_finger_reveal`

金手指或核心差异能力必须把四个里程碑分开。没有传统金手指时，`subject_type` 可以是 `core_selling_point` 或 `none`，不得虚构外挂。

```json
{
  "reveal_id": "OP:GF:001",
  "subject_type": "golden_finger|core_selling_point|none|UNKNOWN",
  "subject_label": "外挂或核心差异能力的定位名称；仅作证据导航",
  "milestones": {
    "appearance": {
      "milestone_status": "observed|partial|not_yet|UNKNOWN",
      "chapter_or_window": "章节或 checkpoint",
      "event_or_scene": "首次出现或被读者/主角接触的事件",
      "what_is_known": "当时读者或主角知道了什么",
      "evidence_refs": ["BOOK_01:CHAPTER:0003"],
      "unknowns": []
    },
    "understanding": {
      "milestone_status": "observed|partial|not_yet|UNKNOWN",
      "chapter_or_window": "章节或 checkpoint",
      "event_or_scene": "首次理解规则、用途或边界的事件",
      "what_is_known": "规则理解达到的程度",
      "evidence_refs": ["BOOK_01:CHAPTER:0005"],
      "unknowns": []
    },
    "validation": {
      "milestone_status": "observed|partial|not_yet|UNKNOWN",
      "chapter_or_window": "章节或 checkpoint",
      "event_or_scene": "规则被行动或结果证实的事件",
      "what_is_known": "验证了什么，仍未知什么",
      "evidence_refs": ["BOOK_01:CHAPTER:0007"],
      "unknowns": []
    },
    "first_proof_or_payoff": {
      "milestone_status": "observed|partial|not_yet|UNKNOWN",
      "chapter_or_window": "章节或 checkpoint",
      "event_or_scene": "核心卖点第一次被实际证明或兑现的事件",
      "observable_result": "读者可观察到的结果、反应、限制或状态变化",
      "evidence_refs": ["BOOK_01:CHAPTER:0010"],
      "unknowns": []
    }
  },
  "evidence_refs": ["BOOK_01:CHAPTER:0003"],
  "unknowns": []
}
```

四个阶段可以跨过前 20 章、部分出现或保持未知，不得因为 schema 有位置就强行填满；获得外挂不自动等于 selling-point proof。

### 3.5 `conflict_activation`

```json
{
  "conflict_id": "OP:CONFLICT:001",
  "conflict_identity_or_reference": "只作定位的冲突对象或接口引用",
  "actual_activation_event": "真正使持续冲突开始推动故事的事件",
  "involved_goal_or_stakes": "冲突牵涉的目标、风险、资源、身份、关系或时间压力",
  "sustaining_reason": "为什么它能在后续继续制造目标、阻力、选择或代价",
  "first_sustained_window": 5,
  "evidence_refs": ["BOOK_01:CHAPTER:0005"],
  "unknowns": []
}
```

第一次打架、一次争吵或单场危险不能仅凭类型自动成为 `conflict_activation`。

### 3.6 `promise_setup`

```json
{
  "promise_id": "OP:PROMISE:001",
  "promise_statement": "开篇向读者建立的未来可兑现内容",
  "promise_target": "主角、读者、关系、目标、真相、位置或卖点对象",
  "setup_event": "承诺被建立的具体事件、选择、异常或问题",
  "expected_future_payoff_or_unresolved_question": "未来应回收的结果或当前悬而未决的问题",
  "promise_status": "open|partially_paid|paid|broken_or_failed|abandoned|UNKNOWN",
  "setup_window": 3,
  "evidence_refs": ["BOOK_01:CHAPTER:0002"],
  "unknowns": []
}
```

不能用单一 `closed` 合并已兑现、失败和主动放弃；没有前置证据不能制造 promise。

### 3.7 `selling_point_proof`

```json
{
  "proof_id": "OP:PROOF:001",
  "selling_point": "作品核心卖点或差异能力",
  "proof_event": "卖点第一次被实际演示的事件",
  "observable_result": "读者、主角、对手或旁观者可观察到的结果",
  "what_it_proves": "这个结果证明了什么，而不是人物口头宣称了什么",
  "proof_window": 5,
  "evidence_refs": ["BOOK_01:CHAPTER:0006"],
  "unknowns": []
}
```

外挂获得、世界观介绍、主角宣言、人物夸赞或设定说明不能自动成为 proof。

### 3.8 `stakes_escalation`

```json
{
  "escalation_id": "OP:STAKE:001",
  "before_stakes": "升级前主角或读者承担的风险、代价、限制或压力",
  "escalation_event": "造成升级的事件、选择、失败、暴露或时间变化",
  "after_stakes": "升级后新增或提高的后果",
  "affected_dimension": "risk|resource|identity|relationship|time|goal|information|mixed|UNKNOWN",
  "escalation_window": 10,
  "evidence_refs": ["BOOK_01:CHAPTER:0009"],
  "unknowns": []
}
```

普通事件密度、敌人数量、场景变大或数值上涨不能代替 `before_stakes → escalation_event → after_stakes`。

### 3.9 `first_payoff`

```json
{
  "payoff_id": "OP:PAYOFF:001",
  "prior_object_type": "promise|unresolved_question|opening_goal|selling_point|UNKNOWN",
  "prior_object_ref": "OP:PROMISE:001 或可回溯的前置对象引用",
  "payoff_event_or_result": "前置对象第一次获得有效结果的事件或结果",
  "payoff_degree": "partial|substantial|UNKNOWN",
  "payoff_window": 10,
  "aftereffect": "结果如何改变状态、风险、目标、关系、信息或继续阅读期待",
  "evidence_refs": ["BOOK_01:CHAPTER:0010"],
  "unknowns": []
}
```

`first_payoff` 必须绑定已有 `promise_id`、未决问题、opening goal 或卖点证明对象；爆点、高潮、升级、击杀、胜利或资源到账不能仅凭结果字段成为回收。

### 3.10 `continuation_drivers`

```json
{
  "driver_id": "OP:DRIVER:001",
  "driver_source": "unresolved_question|next_goal|risk|promise|state_change|relationship|information_gap|UNKNOWN",
  "unresolved_question_next_goal_risk_or_promise": "要求读者继续阅读的具体对象",
  "why_continuation_is_required": "它为什么不是形式悬念，而是真实推动下一窗口",
  "applicable_window": 5,
  "evidence_refs": ["BOOK_01:CHAPTER:0005"],
  "unknowns": []
}
```

普通章末断句、“他震惊了”、突然来敌人或机械截断不能仅凭形式自动成为有效 `continuation_driver`。

### 3.11 `information_pacing`

```json
{
  "information_id": "OP:INFO:001",
  "information_item": "被释放、延后或部分释放的信息",
  "disclosure_state": "must_know_now|partially_disclosed|delayed|understood|UNKNOWN",
  "disclosure_window": 3,
  "why_now": "为何此时释放；证据不足时为 UNKNOWN",
  "why_delayed": "为何延后；不得无证据猜作者意图",
  "reader_knowledge_effect": "信息释放怎样改变理解、期待、风险或选择",
  "evidence_refs": ["BOOK_01:CHAPTER:0004"],
  "unknowns": []
}
```

如果无法确认作者为何延后，可以只记录可观察的延迟效果，并将动机保留为 `UNKNOWN`。

### 3.12 `opening_compression`

压缩问题是候选观察，不是自动评分或开篇等级：

```json
{
  "compression_id": "OP:COMPRESSION:001",
  "issue_type": "repeated_explanation|delayed_activation|preparation_without_validation|repeated_setup_without_payoff|selling_point_delay|information_overload|redundant_scene_function|other|UNKNOWN",
  "observed_pattern": "可回到窗口和章节的重复、拖延、堆积或失速模式",
  "affected_windows": [3, 5, 10],
  "reader_or_story_effect": "它如何影响理解、期待、冲突、卖点验证或继续阅读",
  "observation_status": "observed|possible|UNKNOWN",
  "evidence_refs": ["BOOK_01:CHAPTER:0002", "BOOK_01:CHAPTER:0005"],
  "unknowns": []
}
```

不能因为出现若干章节就自动判定“开篇失败”，也不设置综合开篇评价或等级。

## 4. `adjacent_interfaces`

相邻专项只能通过引用或少量接口说明进入开篇记录：

```json
{
  "plotline": [],
  "chapter_emotion": [],
  "character_function": [],
  "golden_finger": [],
  "worldbuilding": [],
  "cultivation": [],
  "arc_structure": [],
  "plot_mechanism": []
}
```

每个数组元素只能是引用字符串，或下列引用对象：

```json
{
  "record_id": "PL:LINE:001",
  "interface_type": "该专项结果如何服务开篇观察",
  "evidence_refs": ["BOOK_01:CHAPTER:0005"],
  "note": "只保留与开篇窗口直接相关的接口说明",
  "unknowns": []
}
```

不得在 `adjacent_interfaces` 中复制相邻专项完整业务对象。

## 5. `per_book` 单书记录

每本目标书必须有一条 `record_type: per_book`，或在无法核验时有一条 `record_type: gap`；同一冻结范围内二者不能并存。

```json
{
  "record_type": "per_book",
  "schema_version": 1,
  "record_id": "OP:BOOK:BOOK_01",
  "status": "candidate",
  "book_id": "BOOK_01",
  "title": "仅作定位，不参与开篇聚类",
  "chapters_covered": "1-20",
  "observation_windows": [],
  "entry": [],
  "protagonist_establishment": [],
  "premise_exposure": [],
  "golden_finger_reveal": [],
  "conflict_activation": [],
  "promise_setup": [],
  "selling_point_proof": [],
  "stakes_escalation": [],
  "first_payoff": [],
  "continuation_drivers": [],
  "information_pacing": [],
  "opening_compression": [],
  "adjacent_interfaces": {
    "plotline": [],
    "chapter_emotion": [],
    "character_function": [],
    "golden_finger": [],
    "worldbuilding": [],
    "cultivation": [],
    "arc_structure": [],
    "plot_mechanism": []
  },
  "emotion_overlay_links": [],
  "source_numbering_notes": [],
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "PASS"
}
```

字段约束：

- `observation_windows` 只能表达累计 checkpoint，不得嵌入逐章摘要；
- 十二类对象各自保留位置，允许数组为空，但空数组必须与 `unknowns` 或 QA 结论一致；
- `golden_finger_reveal` 的四个 milestone 必须独立存在，即使某阶段为 `not_yet` 或 `UNKNOWN`；
- `first_payoff` 为空时不能声称早期承诺已经有效回收；
- `emotion_overlay_links` 只引用已有 reader-emotion 记录，不复制情绪字段；
- `title`、对象名称和专名只用于定位，不参与母型命名、相似度或聚类标签；
- 开篇记录不能借此替代任何相邻专项的完整业务对象。

## 6. `gap` 缺口记录

证据不足时必须明确阻断原因：

```json
{
  "record_type": "gap",
  "schema_version": 1,
  "record_id": "OP:GAP:BOOK_01",
  "status": "candidate",
  "book_id": "BOOK_01",
  "evidence_refs": ["BOOK_01:CHAPTER:0001"],
  "unknowns": ["前5章缺失，无法确认卖点证明与持续冲突"],
  "confidence": "LOW",
  "qa_status": "HOLD",
  "reason": "已有证据不足以判断累计开篇窗口的运行变化",
  "known_evidence": ["只能确认首章存在某个异常场面"],
  "blocked_outputs": ["高置信 per_book", "nearest_neighbor", "cluster"]
}
```

`gap` 不是虚构开篇结构的占位符，必须说明已知证据、缺口和被阻断的下游判断。

## 7. `nearest_neighbor` 近邻记录

近邻只能在全部目标书完成单书抽取和 QA 后生成，并通过 `cross-book completion gate`：

```json
{
  "record_type": "nearest_neighbor",
  "schema_version": 1,
  "record_id": "OP:NEIGHBOR:001",
  "status": "candidate",
  "book_ids": ["BOOK_01", "BOOK_02"],
  "comparison_ids": ["OP:BOOK:BOOK_01", "OP:BOOK:BOOK_02"],
  "comparison_dimensions": {
    "reader_entry": "读者如何进入并形成初始期待",
    "protagonist_establishment": "主角如何通过行为、选择和限制被建立",
    "premise_exposure": "核心前提如何变得可理解",
    "golden_finger_reveal": "四阶段如何分离或合并、证据如何出现",
    "conflict_promise_payoff": "持续冲突、承诺与首次回收如何运行",
    "selling_point_and_stakes": "卖点证明和风险升级如何推进",
    "continuation_and_information": "续读驱动、信息节奏与压缩问题如何形成"
  },
  "similarities": [],
  "difference_boundary": "相近但不合并的开篇运行差异",
  "surface_labels_excluded": ["系统开局", "穿越", "第一章战斗", "退婚", "学院考试"],
  "decision": "merge_candidate|keep_distinct|insufficient_evidence",
  "reason": "基于窗口推进和可观察证据的比较理由",
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "PASS"
}
```

不能只因为题材皮肤、外挂名称、第一章打斗或开局标签相同就生成近邻。

## 8. `cluster` 聚类候选

聚类必须在全部目标书单书 QA 和近邻比较完成后生成，且只能是 candidate；同样受 `cross-book completion gate` 约束：

```json
{
  "record_type": "cluster",
  "schema_version": 1,
  "record_id": "OP:CLUSTER:001",
  "status": "candidate",
  "book_ids": ["BOOK_01", "BOOK_02"],
  "member_record_ids": ["OP:BOOK:BOOK_01", "OP:BOOK:BOOK_02"],
  "cluster_level": "大类|母型|子型|变体",
  "label": "不复制专名和表面题材的功能性名称",
  "shared_operation": "读者进入→主角建立→前提理解→卖点证明→冲突承诺→早期回收→续读驱动的共同运行方式",
  "window_progression_pattern": "3→5→10→20 窗口之间的共同推进或差异",
  "selling_point_promise_payoff_pattern": "卖点、承诺、首次回收如何连接",
  "information_and_compression_boundary": "信息节奏与拖延问题的共同边界",
  "boundary_conditions": ["与相近候选保持区分的证据条件"],
  "supporting_book_count": 2,
  "nearest_neighbor_record_ids": ["OP:NEIGHBOR:001"],
  "merge_decision": "candidate_merge|candidate_split|new_candidate|insufficient_evidence|keep_distinct|unclustered|HOLD",
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "PASS"
}
```

`shared_operation` 必须描述开篇怎样运行，不能只写“系统流”“退婚开局”“学院考试”或其它题材皮肤。单书候选不能自动升级为高频母型。

## 9. `qa` 与 `handoff` 记录

### 9.1 `qa`

```json
{
  "record_type": "qa",
  "schema_version": 1,
  "record_id": "OP:QA:BOOK_01:1-20",
  "status": "candidate",
  "book_id": "BOOK_01",
  "scope": "BOOK_01:1-20",
  "checks": {
    "window_coverage": "PASS|HOLD|FAIL",
    "entry_and_protagonist": "PASS|HOLD|FAIL",
    "premise_exposure": "PASS|HOLD|FAIL",
    "golden_finger_milestones": "PASS|HOLD|FAIL",
    "conflict_activation": "PASS|HOLD|FAIL",
    "promise_and_first_payoff": "PASS|HOLD|FAIL",
    "selling_point_proof": "PASS|HOLD|FAIL",
    "stakes_escalation": "PASS|HOLD|FAIL",
    "continuation_driver": "PASS|HOLD|FAIL",
    "information_pacing_compression": "PASS|HOLD|FAIL",
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

1. 四个累计窗口有明确章节范围，缺失窗口没有被后文或其它书补齐；
2. entry、主角建立、前提暴露和持续冲突都有章节或阶段证据；
3. 金手指四阶段没有把出现、理解、验证和首次证明混成一件事；
4. promise、selling-point proof 和 first payoff 之间有前置—证明—回收关系；
5. 第一次打架、外挂获得、世界观说明、爆点和章末悬念没有被自动当成对应对象；
6. stakes 有 `before_stakes → escalation_event → after_stakes`；
7. continuation driver 有真实目标、风险、信息缺口、承诺或状态变化来源；
8. information pacing 不猜作者内心动机，opening compression 只是证据化候选观察；
9. 相邻专项只有 interface/reference，没有复制完整业务对象；
10. 跨书结果满足全部目标书完成单书 QA 后的阶段门。

### 9.2 `handoff`

```json
{
  "record_type": "handoff",
  "schema_version": 1,
  "record_id": "OP:HANDOFF:001",
  "status": "candidate",
  "book_ids": ["BOOK_01"],
  "candidate_record_ids": ["OP:BOOK:BOOK_01"],
  "recommended_action": "保留|合并候选|拆分候选|补证据|暂缓",
  "decision_points": ["需要人工确认的窗口边界、卖点证明、承诺回收或聚类差异"],
  "evidence_summary": ["支持候选的关键开篇运行证据"],
  "boundary_warnings": ["可能与剧情线、逐章情绪或篇章结构重叠的接口"],
  "blocked_by": [],
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "HOLD"
}
```

`handoff` 只把候选、证据、争议、边界和待决策项交给人工，不自动写入正式资料或素材库。

## 10. 状态、证据与跨专项边界

- `observation_windows` 是累计 checkpoint，不得变成四份章节摘要；
- `golden_finger_reveal` 四个 milestone 可以部分出现、延后或未知，不要求前 20 章全部完成；
- `promise_status` 区分 `open`、`partially_paid`、`paid`、`broken_or_failed`、`abandoned` 和 `UNKNOWN`，不能用单一 `closed`；
- `first_payoff` 必须引用一个已有前置对象，不能由 payoff_result 自己成立；
- `selling_point_proof` 必须有 observable result；口头宣言、获取外挂和世界观说明不自动算证明；
- `stakes_escalation` 必须说明前状态、升级事件和后状态；
- `continuation_drivers` 必须说明真实续读来源，章末悬念不自动成立；
- `information_pacing` 可以把 why_now 或 why_delayed 保留为 `UNKNOWN`，不能伪造作者动机；
- `opening_compression` 只记录有证据的结构问题候选，不生成综合评分；
- `adjacent_interfaces` 只保存 interface/reference，不承载 plotline、emotion、character、golden-finger、worldbuilding、cultivation、arc 或 plot-mechanism 的完整对象；
- 所有缺失证据进入 `unknowns`、`gap` 或 `HOLD`，不能跨书补齐；
- `nearest_neighbor` 和 `cluster` 只能比较开篇运行结构、窗口推进、卖点验证、承诺回收、信息节奏和续读驱动，不能比较表面题材标签；
- 本专项没有正式素材库写入字段，也不负责状态升级、候选合并或总索引重建。

本 schema 只冻结开篇专项的累计窗口、十二类观察对象、四阶段金手指揭示、承诺与回收边界、相邻接口和五类派生交付。具体 QA 判定顺序、validator 硬约束和 agent 调用说明必须在后续文件中分别设计、测试和验收。
