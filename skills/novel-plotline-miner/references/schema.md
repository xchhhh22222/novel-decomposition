# 剧情线横向拆解专项输出契约

## 1. 权威关系与统一 envelope

本文件是 `novel-plotline-miner` 的专项记录契约，不覆盖总控契约，也不修改章节事实、分卷资料、人物库、情绪记录或其它专项的 canonical schema。所有记录必须同时满足：

- `skills/novel-dna-orchestrator/SKILL.md` 的总控要求；
- `skills/novel-dna-orchestrator/references/horizontal-specialist-contract.md` 的派生记录要求；
- `skills/novel-dna-orchestrator/references/integration-and-qa.md` 的证据、状态和阶段门要求；
- `skills/novel-plotline-miner/SKILL.md` 的九段生命周期和边界。

除上位契约明确规定的 canonical 权威记录外，本专项所有机器可读记录都使用统一 envelope：

```json
{
  "record_type": "per_book|nearest_neighbor|cluster|qa|handoff|gap",
  "schema_version": 1,
  "record_id": "PL:<TYPE>:<STABLE_ID>",
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

- `per_book`、`qa`、`handoff` 和 `gap` 通常使用 `book_id`；
- `nearest_neighbor` 和 `cluster` 通常使用 `book_ids`。

统一约束：

1. `status` 只能为 `candidate`，本文件不定义 `active`、`deprecated` 或正式素材库写入字段；
2. `evidence_refs` 必须能回到章节、阶段或已有 reader-emotion overlay；
3. `unknowns` 只记录真实缺口，不得把推测写入缺口；
4. `HIGH` 不得包含会改变九段生命周期、payoff、state_change、next_entry、父子线关系或生命周期结局的关键 `UNKNOWN`；
5. `partial`、`UNKNOWN`、`gap`、`HOLD` 和 `FAIL` 必须显式保留；
6. 升级、击杀、战斗胜利或获得资源不能仅凭结果字段自动成为 `payoff`。

## 2. 九段生命周期记录

每条具体剧情线使用一个 line record 承载以下九段；九段必须各自有位置，不能合并为章节摘要或事件列表。

### 2.1 `line_identity`

`line_identity` 只用于定位线路和限定范围，不以线路名称直接证明线路存在：

```json
{
  "line_id": "PL:LINE:001",
  "line_label": "仅作定位的功能性名称",
  "line_scope": "章节、阶段或地图范围",
  "line_purpose": "这条线在当前证据范围内追踪的目标边界",
  "line_kind": "main|subline|parallel|UNKNOWN",
  "evidence_refs": ["BOOK_01:CHAPTER:0002"],
  "unknowns": []
}
```

`line_label`、章节标题、题材名和专名只用于回溯，不参与近邻或聚类标签。`line_kind` 只作当前证据范围内的定位，不以 main/subline 名称替代父子线证据。

### 2.2 `trigger`

`trigger` 必须记录实际启动或唤醒事件：

```json
{
  "trigger_id": "PL:TRIGGER:001",
  "actual_start_event": "真正启动或重新唤醒线路的事件、承诺、危机、任务、关系变化或资源门槛",
  "chapter_or_stage": "章节或阶段",
  "start_mode": "new|reopened|UNKNOWN",
  "evidence_refs": ["BOOK_01:CHAPTER:0003"],
  "unknowns": []
}
```

背景设定第一次出现、书名、简介、人物早已有的抽象愿望或章节标题不能单独成为 `actual_start_event`。

### 2.3 `goals`

目标可以随阶段变化，因此以数组承载当前可追踪目标及其适用范围：

```json
{
  "goal_id": "PL:GOAL:001",
  "goal_statement": "人物或主角当前试图达成的可追踪目标",
  "subject": "谁在追求该目标",
  "phase_scope": "章节或阶段范围",
  "success_condition": "什么证据可以确认目标得到结果",
  "goal_status": "open|shifted|paid|failed|abandoned|UNKNOWN",
  "evidence_refs": ["BOOK_01:CHAPTER:0004"],
  "unknowns": []
}
```

“变强”“复仇”“获得认可”等抽象词只有在章节证据把它们具体化为当前线路目标、对象、门槛或成功条件时才能使用。目标状态不能替代线路的 `line_lifecycle.current_state`。

### 2.4 `resistances`

阻力必须说明它如何持续改变推进：

```json
{
  "resistance_id": "PL:RESISTANCE:001",
  "resistance_type": "person|resource|information|institution|rule|time|risk|goal_conflict|identity|environment|other",
  "operation": "阻力如何阻止目标、改变路线、提高门槛或迫使选择",
  "target_goal_id": "PL:GOAL:001",
  "phase_scope": "章节或阶段范围",
  "observable_effect": "推进、资源、信息、风险或选择发生的可观察改变",
  "evidence_refs": ["BOOK_01:CHAPTER:0007"],
  "unknowns": []
}
```

敌人名单、困难名词、地点或场景不能在没有实际后果时直接成为阻力。一个阻力可以跨多个节点持续，但每次持续或升级都必须有证据。

### 2.5 `nodes`

节点必须保存状态变化链，而不是普通事件：

```json
{
  "node_id": "PL:NODE:001",
  "node_type": "reveal|threshold|reversal|resource_gate|relationship_shift|risk_escalation|decision_point|other",
  "before_state": "节点发生前线路、人物或目标状态",
  "node_event": "真正造成改变的事件或行动",
  "after_state": "节点发生后线路、人物或目标状态",
  "line_effect": "节点如何改变目标、阻力、选择、代价、兑现或下一入口",
  "phase_scope": "章节或阶段范围",
  "evidence_refs": ["BOOK_01:CHAPTER:0012"],
  "unknowns": []
}
```

普通移动、重复训练、无状态变化的对话、背景说明和单纯战斗过程不能自动成为节点。没有 `before_state` 或 `after_state` 的候选应进入 `HOLD` 或降级为普通事件证据。

### 2.6 `choices`

选择必须存在真实替代路径或取舍：

```json
{
  "choice_id": "PL:CHOICE:001",
  "decision_maker": "人物或主角",
  "available_paths": ["路径 A", "路径 B"],
  "chosen_action": "实际选择的行动",
  "rejected_or_foregone_alternative": "被放弃、延后或无法选择的替代路径；证据不足时为 UNKNOWN",
  "choice_effect": "选择如何改变目标、阻力、资源、风险、关系、身份或后续线路",
  "phase_scope": "章节或阶段范围",
  "evidence_refs": ["BOOK_01:CHAPTER:0015"],
  "unknowns": []
}
```

被动发生的结果、作者替人物决定的单一路径或没有取舍空间的动作不能自动成为 `choice`。`rejected_or_foregone_alternative` 允许 `UNKNOWN`，但 `available_paths`、`chosen_action` 和 `choice_effect` 不能缺失。

### 2.7 `costs`

代价可以不存在或尚未确认，不能因为 schema 有字段就强制编造：

```json
{
  "cost_id": "PL:COST:001",
  "caused_by_choice_or_node": "PL:CHOICE:001",
  "cost_type": "resource|relationship|identity|risk|information|time|opportunity|debt|other|UNKNOWN",
  "actual_cost": "选择或推进实际付出的可观察代价",
  "downstream_constraint": "代价如何形成后续限制、债务或风险",
  "phase_scope": "章节或阶段范围",
  "evidence_refs": ["BOOK_01:CHAPTER:0016"],
  "unknowns": []
}
```

如果当前选择没有可观察代价，`costs` 可以为空；普通结果、战斗结束、拿到奖励或剧情自然推进不能自动叫代价。

### 2.8 `payoffs`

兑现必须关联前置目标、承诺或未决问题：

```json
{
  "payoff_id": "PL:PAYOFF:001",
  "prior_goal_ids": ["PL:GOAL:001"],
  "prior_promise_or_unresolved_question": "被兑现的前置承诺或悬而未决问题；没有时为 UNKNOWN",
  "payoff_result": "目标、承诺或未决问题实际获得的结果",
  "payoff_state": "paid|partial|failed|UNKNOWN",
  "is_line_payoff": true,
  "phase_scope": "章节或阶段范围",
  "evidence_refs": ["BOOK_01:CHAPTER:0021"],
  "unknowns": []
}
```

若 `is_line_payoff` 为 `true`，必须至少存在 `prior_goal_ids` 或有证据支持的 `prior_promise_or_unresolved_question`，并有 `payoff_result` 与 `evidence_refs`。升级、击杀、战斗胜利或获得资源只有在真实完成前置目标/承诺/未决问题时，才能作为 `payoff_result` 的一部分。

### 2.9 `state_changes`

状态变化独立于兑现结果，记录兑现或失败后真正改变的对象：

```json
{
  "state_change_id": "PL:STATE:001",
  "caused_by_payoff_or_failure": "PL:PAYOFF:001",
  "changed_domains": ["goal", "relationship", "resource", "identity", "cognition", "risk", "situation", "action_permission"],
  "before_state": "兑现或失败前的相关状态",
  "after_state": "兑现或失败后的相关状态",
  "line_effect": "状态变化如何改变线路阶段、人物行动或后续约束",
  "evidence_refs": ["BOOK_01:CHAPTER:0022"],
  "unknowns": []
}
```

`changed_domains` 至少要能落到目标、关系、资源、身份、认知、风险、局势或行动权限之一。不能只重复 `payoff_result`，也不能把后续入口写进 `after_state` 而不说明真实变化。

### 2.10 `next_entries`

下一入口必须由某个状态变化实际打开：

```json
{
  "next_entry_id": "PL:ENTRY:001",
  "source_state_change_id": "PL:STATE:001",
  "entry_type": "goal|resistance|task|choice|child_line|UNKNOWN",
  "opened_goal_or_task": "下一阶段目标、任务或子线入口",
  "opened_resistance": "随入口出现的下一阻力；没有时为 UNKNOWN",
  "opened_choice": "下一阶段的选择或取舍；没有时为 UNKNOWN",
  "target_line_id": "被打开的线路或子线；不确定时为 UNKNOWN",
  "evidence_refs": ["BOOK_01:CHAPTER:0023"],
  "unknowns": []
}
```

`source_state_change_id`、`opened_goal_or_task` 和 `evidence_refs` 不能缺失。没有真实状态变化支撑时，不能为了制造悬念凭空追加新危机；同一个 payoff 不能直接重复写成 next entry。

## 3. 生命周期、父子线与主角接口

### 3.1 `line_lifecycle`

本专项正式冻结生命周期状态，但保持成功、失败和放弃的区分：

```json
{
  "current_state": "not_started|active|paused|redirected|paid|failed|abandoned|UNKNOWN",
  "state_history": [
    {
      "state": "active",
      "trigger_or_reason": "进入该状态的事件、选择、兑现、失败或暂停原因",
      "phase_scope": "章节或阶段范围",
      "evidence_refs": ["BOOK_01:CHAPTER:0003"],
      "unknowns": []
    }
  ],
  "unknowns": []
}
```

`paid` 表示线路目标/承诺得到确认的成功兑现；`failed` 表示目标或承诺以失败收束；`abandoned` 表示人物或线路主动放弃；三者不能合并为模糊的 `closed`。`paused` 不自动传递给子线，`redirected` 需要证据说明目标、阻力或方向发生了线路级转向。

### 3.2 `parent_child_relations`

父子线关系独立承载：

```json
{
  "parent_line_id": "PL:LINE:001",
  "child_line_id": "PL:LINE:002",
  "relation_type": "service|obstacle|change|UNKNOWN",
  "how_child_affects_parent": "子线如何服务、阻碍或改变父线",
  "child_completion_effect": "子线完成、失败或放弃对父线的实际影响",
  "pause_relationship": "父线与子线暂停状态是否独立、证据如何显示",
  "evidence_refs": ["BOOK_01:CHAPTER:0025"],
  "unknowns": []
}
```

必须遵守：

- `child paid` 不等于 `parent paid`；
- `parent paused` 不等于 child 自动 `paused`；
- 子线完成可以只是父线的节点、代价、资源入口、信息入口或下一入口；
- 共享人物、地点或敌人不能单独证明父子关系。

### 3.3 `protagonist_interface`

主角接口只记录线路如何改变主角状态，不复制人物、世界观、修炼或情绪专项业务对象：

```json
{
  "goals": "线路如何改变主角目标、优先级或行动方向",
  "choices": "线路如何迫使主角在替代路径间取舍",
  "resources": "线路如何改变主角资源、权限、门槛或消耗",
  "risks": "线路如何改变主角风险、暴露、代价或失败概率",
  "cognition_information": "线路如何改变主角信息、认知或判断",
  "relationships": "线路如何改变主角关系位置、承诺或债务",
  "action_window": "线路如何打开或关闭主角的行动窗口",
  "evidence_refs": ["BOOK_01:CHAPTER:0026"],
  "unknowns": []
}
```

## 4. `per_book` 单书记录

每本目标书必须有一条 `record_type: per_book`，或在无法核验时有一条 `record_type: gap`；同一冻结范围内两者不能并存。

```json
{
  "record_type": "per_book",
  "schema_version": 1,
  "record_id": "PL:BOOK:BOOK_01",
  "status": "candidate",
  "book_id": "BOOK_01",
  "title": "仅作定位，不参与线路聚类",
  "chapters_covered": "1-120",
  "plotlines": [
    {
      "line_identity": {},
      "trigger": {},
      "goals": [],
      "resistances": [],
      "nodes": [],
      "choices": [],
      "costs": [],
      "payoffs": [],
      "state_changes": [],
      "next_entries": [],
      "line_lifecycle": {},
      "parent_child_relations": [],
      "protagonist_interface": {},
      "adjacent_interfaces": {
        "character_function": [],
        "arc_structure": [],
        "plot_mechanism": [],
        "opening": [],
        "cultivation": [],
        "worldbuilding": [],
        "golden_finger": [],
        "chapter_emotion": []
      },
      "evidence_refs": [],
      "unknowns": []
    }
  ],
  "emotion_overlay_links": [],
  "source_numbering_notes": [],
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "PASS"
}
```

字段要求：

- `plotlines` 只列允许来源中有实际生命周期证据的线路，不根据简介或题材标签扩展；
- 每条线必须独立承载九段链条，不能只在书级别给一个总摘要；
- `costs`、`payoffs`、`state_changes` 或 `next_entries` 可以为空，但空数组必须与 `unknowns` 或 QA 结论一致，不能伪装为已完成生命周期；
- `adjacent_interfaces` 只能保存接口或证据引用，不能嵌入相邻专项完整业务对象；
- `emotion_overlay_links` 只引用已有 reader-emotion 记录，不复制章节情绪字段；
- `title`、线路名称和专名只用于定位，不参与母型命名、相似度或聚类标签。

### adjacent interface reference 形式

`adjacent_interfaces` 的每个数组元素只能是引用字符串，或包含少量接口说明的引用对象：

```json
{
  "record_id": "CF:FUNCTION:001",
  "interface_type": "人物如何推动或阻碍该线路",
  "evidence_refs": ["BOOK_01:CHAPTER:0010"],
  "note": "只保留与该线路直接相关的接口说明",
  "unknowns": []
}
```

不得在其中复制人物功能、世界规则、修炼成长、金手指机制、篇章结构或章节情绪的完整正式对象。

## 5. `gap` 缺口记录

缺少足够证据时必须保留缺口：

```json
{
  "record_type": "gap",
  "schema_version": 1,
  "record_id": "PL:GAP:BOOK_01",
  "status": "candidate",
  "book_id": "BOOK_01",
  "evidence_refs": ["BOOK_01:CHAPTER:0001"],
  "unknowns": ["触发事件与当前目标之间的承接", "兑现后的下一入口"],
  "confidence": "LOW",
  "qa_status": "HOLD",
  "reason": "已有证据只能确认事件发生，不能确认完整线路生命周期",
  "known_evidence": ["确认存在一次任务或冲突"],
  "blocked_outputs": ["高置信 per_book", "nearest_neighbor", "cluster"]
}
```

`gap` 不是虚构线路的占位符，必须说明缺口、已有证据和被阻断的下游判断。

## 6. `nearest_neighbor` 近邻记录

近邻只能在全部目标书完成单书抽取和 QA 后生成，并通过 cross-book completion gate。比较的是线路运行结构：

```json
{
  "record_type": "nearest_neighbor",
  "schema_version": 1,
  "record_id": "PL:NEIGHBOR:001",
  "status": "candidate",
  "book_ids": ["BOOK_01", "BOOK_02"],
  "comparison_ids": ["PL:BOOK:BOOK_01", "PL:BOOK:BOOK_02"],
  "comparison_dimensions": {
    "trigger_and_goal_formation": "线路如何启动并形成可追踪目标",
    "resistance_maintenance": "阻力如何持续并改变推进",
    "node_choice_cost": "节点、选择和代价如何推动线路",
    "payoff_state_next_entry": "兑现如何滚入状态变化和下一入口",
    "parent_child_structure": "父线与子线如何服务、阻碍或改变彼此",
    "lifecycle_outcomes": "完成、失败、放弃、暂停和转向如何区分"
  },
  "similarities": [],
  "difference_boundary": "保持相近但不合并的核心线路差异",
  "surface_labels_excluded": ["复仇线", "升级线", "考试线", "学院线", "比赛线", "救人线"],
  "decision": "merge_candidate|keep_distinct|insufficient_evidence",
  "reason": "比较理由",
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "PASS"
}
```

不能只因两本书都叫“复仇线”“考试线”“救人线”“比赛线”就生成近邻。必须说明触发、目标/阻力维持、节点/选择/代价、兑现/状态变化/下一入口或父子线结构的相似运行点与关键差异。

## 7. `cluster` 聚类候选

聚类必须在全部目标书的单书 QA 与近邻比较完成后生成，且只能是 candidate：

```json
{
  "record_type": "cluster",
  "schema_version": 1,
  "record_id": "PL:CLUSTER:001",
  "status": "candidate",
  "book_ids": ["BOOK_01", "BOOK_02"],
  "member_record_ids": ["PL:BOOK:BOOK_01", "PL:BOOK:BOOK_02"],
  "cluster_level": "大类|母型|子型|变体",
  "label": "不复制专名和表面题材的功能性名称",
  "shared_operation": "共同的触发→目标→阻力→节点→选择→代价→兑现→状态变化→下一入口运行方式",
  "payoff_state_entry_pattern": "兑现、状态变化和下一入口如何连续滚动",
  "parent_child_pattern": "父线与子线的共同组织方式及边界",
  "boundary_conditions": ["与相近候选保持区分的证据条件"],
  "supporting_book_count": 2,
  "nearest_neighbor_record_ids": ["PL:NEIGHBOR:001"],
  "merge_decision": "candidate_merge|candidate_split|new_candidate|insufficient_evidence|keep_distinct|unclustered|HOLD",
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "PASS"
}
```

`shared_operation` 必须描述线路如何运行，不能只写“复仇型”“学院比赛”“升级流”或其它题材皮肤。单书候选不能自动升级为高频母型，也不能写成 `active`。

## 8. `qa` 与 `handoff` 记录

### `qa`

```json
{
  "record_type": "qa",
  "schema_version": 1,
  "record_id": "PL:QA:BOOK_01:1-120",
  "status": "candidate",
  "book_id": "BOOK_01",
  "scope": "BOOK_01:1-120",
  "checks": {
    "coverage": "PASS|HOLD|FAIL",
    "nine_stage_chain": "PASS|HOLD|FAIL",
    "trigger_goal_resistance": "PASS|HOLD|FAIL",
    "node_state_change": "PASS|HOLD|FAIL",
    "choice_and_cost": "PASS|HOLD|FAIL",
    "payoff_boundary": "PASS|HOLD|FAIL",
    "state_change_next_entry": "PASS|HOLD|FAIL",
    "parent_child_lines": "PASS|HOLD|FAIL",
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

1. 触发是真实启动事件，而不是背景、简介或标题；
2. 目标可追踪，阻力真实改变推进；
3. 节点有 `before_state → node_event → after_state`；
4. 选择存在真实替代路径或取舍，代价是可观察后果；
5. payoff 绑定前置目标、承诺或未决问题；
6. 升级、击杀、战斗胜利和资源获得没有被自动当成 payoff；
7. state_change 与 next_entry 独立且有证据；
8. 父子线关系、子线完成与父线完成、父线暂停与子线暂停没有混同；
9. 相邻专项只通过 interface/evidence 引用；
10. 跨书结果满足全部目标书完成后的阶段门。

### `handoff`

```json
{
  "record_type": "handoff",
  "schema_version": 1,
  "record_id": "PL:HANDOFF:001",
  "status": "candidate",
  "book_ids": ["BOOK_01"],
  "candidate_record_ids": ["PL:BOOK:BOOK_01"],
  "recommended_action": "保留|合并候选|拆分候选|补证据|暂缓",
  "decision_points": ["需要人工确认的线路边界、兑现或父子线关系"],
  "evidence_summary": ["支持候选的关键生命周期证据"],
  "boundary_warnings": ["可能与章节摘要、剧情机制或篇章结构重叠的接口"],
  "blocked_by": [],
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "HOLD"
}
```

`handoff` 只把候选、证据、争议、边界和待决策项交给人工，不自动把线路写进正式资料或素材库。

## 9. 状态、证据与跨专项边界

- 每条线路必须至少有 `line_identity`、`trigger`、`goals`、`resistances`、`nodes`、`choices`、`costs`、`payoffs`、`state_changes`、`next_entries`、`line_lifecycle` 和证据引用的位置；
- `costs` 可以为空，但不得以空数组掩盖没有检查代价；
- `payoffs` 为空时不能声称线路已 `paid`；
- `state_changes` 和 `next_entries` 不得只复制前一字段的文字；
- `adjacent_interfaces` 只保存 interface/reference，不承载 plotline、arc、character、worldbuilding、cultivation、golden-finger 或 chapter-emotion 的完整业务结论；
- 所有缺失证据进入 `unknowns`、`gap` 或 `HOLD`，不能跨书补齐；
- `nearest_neighbor` 和 `cluster` 只能比较线路运行方式和生命周期结果，不能比较复仇、升级、学院、比赛、感情或救人等表面名词；
- 本专项没有正式素材库写入字段，也不负责状态升级、线路卡合并或总索引重建。

本 schema 只冻结剧情线专项的九段记录结构、生命周期结局、父子线关系、主角接口和五类派生交付。具体聚类评分、QA 判定顺序、validator 硬约束和 agent 调用说明必须在后续文件中分别设计、测试和验收。
