# novel-plot-mechanism-miner canonical schema

本文件冻结剧情机制专项的记录结构，不覆盖总控契约，也不修改剧情线、篇章、开篇、人物、情绪、世界观、修炼体系或金手指的 canonical schema。机制记录必须回答：多个有证据的剧情实例为什么能够按相近的运行结构反复工作。

所有抽象结论必须能回到章节或阶段证据。单次实例可以作为 `mechanism_candidate` 的证据，但不能单凭一次实例证明 `repeatability`。可复用性必须来自实际多次运行证据、文本中明确可复用的规则/条件证据，或二者的组合；没有这些证据时保留 `UNKNOWN`、`partial`、`gap` 或 `HOLD`。

本 schema 不设置固定 operation 步骤数，不设置“至少出现 N 次”的机械阈值，不引入 `mechanism_type` 的题材标签枚举，不引入 mechanism score、grade 或 tier。具体某个候选是否应合并、是否真正可复用，由后续 QA 与人工审核判断，不能靠关键词自动归类。

## 1. 统一 envelope

每条 JSONL 记录必须包含：

```json
{
  "record_type": "per_book|gap|nearest_neighbor|cluster|qa|handoff",
  "schema_version": 1,
  "record_id": "PM:...",
  "status": "candidate",
  "book_id": "BOOK_01",
  "book_ids": ["BOOK_01", "BOOK_02"],
  "evidence_refs": ["BOOK_01:CHAPTER:0001"],
  "unknowns": [],
  "confidence": "HIGH|MEDIUM|LOW",
  "qa_status": "PASS|HOLD|FAIL"
}
```

约束：

- `record_type` 必须与输出 kind 一致；`schema_version` 当前为 `1`；
- `record_id` 在同一冻结批次内唯一；
- 所有结果保持 `status: candidate`，不得写 `active`、`deprecated` 或正式素材状态；
- `per_book`、`gap`、`qa` 使用 `book_id`；`nearest_neighbor`、`cluster`、`handoff` 使用 `book_ids`；二者互斥；
- `evidence_refs` 是章节、阶段或允许来源的结构化引用；没有证据不能用空数组伪装完成；
- `unknowns` 记录尚未核验的关键缺口；`HIGH` 置信度不能带关键 `UNKNOWN`；
- `partial`、`UNKNOWN`、`gap`、`HOLD` 可以合法存在，不能为了通过校验删除不确定性；
- 所有相邻专项只通过 reference/interface 连接，不嵌入其完整正式对象。

## 2. 共享引用结构

### 2.1 `observed_instance_ref`

机制可以引用多个实例，但实例不是本专项重新复制的 plotline、人物、世界或章节对象：

```json
{
  "instance_id": "PM:INSTANCE:BOOK_01:001",
  "book_id": "BOOK_01",
  "chapter_or_stage_scope": "第12—15章",
  "instance_summary": "只描述本次机制运行的必要观察，不写完整剧情摘要",
  "mechanism_candidate_relation": "supports|contrasts|unclear|UNKNOWN",
  "evidence_refs": ["BOOK_01:CHAPTER:0012"],
  "unknowns": []
}
```

`instance_summary` 只保留触发、运行、选择、约束、结果和状态变化的观察证据，不复制完整剧情线生命周期或相邻专项对象。

### 2.2 `adjacent_interfaces`

每个相邻接口元素只能是引用字符串，或以下引用对象：

```json
{
  "record_id": "PL:LINE:001",
  "interface_type": "该结果如何作为机制输入、约束、角色接口或结果证据",
  "evidence_refs": ["BOOK_01:CHAPTER:0012"],
  "note": "只保留与当前机制运行直接相关的说明",
  "unknowns": []
}
```

接口对象不得复制 plotline、arc、opening、character、emotion、world、cultivation、golden-finger 或其它机制对象的完整字段。

## 3. 单书机制对象

以下对象共同构成 `per_book.mechanisms[]` 中的一个机制候选。一本书可以同时保留多个独立机制；除 `mechanism_identity` 和 `repeatability` 外，重复运行对象通常使用数组，以保留多实例、多步骤、多路径和多种失败模式；本 schema 不规定数组的固定长度。

### 3.1 `mechanism_identity`

```json
{
  "mechanism_id": "PM:MECHANISM:001",
  "mechanism_label": "描述运行方式的功能性名称",
  "mechanism_description": "可复用运行结构的简洁定义",
  "reusable_operation": "它如何在不同实例中保持核心运转",
  "applicability_scope": "适用的章节、阶段、角色关系或条件范围",
  "core_invariants": ["必须保持的触发、操作、约束或结果关系"],
  "excluded_surface_labels": ["比赛", "考试"],
  "distinction_boundary": "与相近机制候选的运行差异",
  "evidence_refs": ["BOOK_01:CHAPTER:0012"],
  "unknowns": []
}
```

`mechanism_label` 不能直接使用“考试机制”“秘境机制”等题材名词；身份要描述可复用的运行方式和边界。

### 3.2 `trigger_conditions`

```json
{
  "condition_id": "PM:TRIGGER:001",
  "condition_kind": "necessary|optional|enabling|UNKNOWN",
  "condition_description": "启动前必须或可能满足的条件",
  "source_state": "启动前的目标、压力、资源、信息、关系或权限状态",
  "trigger_observation": "文本中观察到机制开始运转的证据",
  "evidence_refs": ["BOOK_01:CHAPTER:0012"],
  "unknowns": []
}
```

多个必要条件、可选条件和使能条件应分别保留；偶然发生的单个事件不能自动替代完整触发条件。

### 3.3 `actors_and_roles`

```json
{
  "actor_role_id": "PM:ROLE:001",
  "actor_reference": "人物、群体、制度或可观察行动主体的引用",
  "mechanism_role": "施压|响应|试探|验证|阻断|竞争|见证|兑现|改变条件|UNKNOWN",
  "actual_operation": "该主体在本机制中实际做了什么",
  "response_or_dependency": "该角色如何依赖或改变其他角色、输入或约束",
  "evidence_refs": ["BOOK_01:CHAPTER:0013"],
  "unknowns": []
}
```

这里记录机制运行角色，不复制 `character-function-miner` 的人物功能、关系发动机或人物卡。

### 3.4 `inputs`

```json
{
  "input_id": "PM:INPUT:001",
  "input_kind": "information|resource|identity|rule|risk|relationship|time|permission|expectation|other|UNKNOWN",
  "input_description": "机制需要的输入及其具体状态",
  "required_or_optional": "required|optional|enabling|UNKNOWN",
  "consumed_or_retained": "consumed|retained|transformed|UNKNOWN",
  "provided_by_or_source": "输入由谁、什么制度、什么事件或什么前置状态提供",
  "evidence_refs": ["BOOK_01:CHAPTER:0012"],
  "unknowns": []
}
```

输入可以来自相邻专项，但只保留它在本机制中的接口作用，不复制来源系统。

### 3.5 `operations`

```json
{
  "operation_id": "PM:OPERATION:001",
  "order_or_dependency": "顺序、依赖或并行关系；不要求固定编号数量",
  "operation": "机制实际执行的步骤或结构动作",
  "required_input_or_state": "本步骤所需输入或前置状态",
  "resulting_intermediate_state": "本步骤完成后出现的中间状态",
  "depends_on_operation_ids": ["PM:OPERATION:000"],
  "evidence_refs": ["BOOK_01:CHAPTER:0013"],
  "unknowns": []
}
```

`operations` 必须体现有顺序或依赖关系的运行步骤，不能只是事件名称列表；不设置固定步骤数。

### 3.6 `decision_points`

```json
{
  "decision_id": "PM:DECISION:001",
  "decision_maker": "作出选择的主体引用",
  "decision_context": "选择发生时的压力、信息、资源和限制",
  "available_paths": ["可观察的路径 A", "可观察的路径 B"],
  "chosen_or_observed_path": "实际选择或文本观察到的路径",
  "path_consequence": "该路径如何改变操作、风险、资源、关系、权限或结果",
  "evidence_refs": ["BOOK_01:CHAPTER:0014"],
  "unknowns": []
}
```

没有真实可行路径分叉时不得伪造 `decision_point`；被动受伤、单纯反转或事件发生本身不等于选择。

### 3.7 `constraints`

```json
{
  "constraint_id": "PM:CONSTRAINT:001",
  "constraint_kind": "rule|resource|time|permission|identity|relationship|information|risk|other|UNKNOWN",
  "constraint_operation": "该约束如何限制、提高门槛、迫使改道或改变代价",
  "affected_step_or_role": "受影响的 operation、decision point 或运行角色",
  "observable_effect": "可观察的路径、选择、资源、风险、权限或结果变化",
  "evidence_refs": ["BOOK_01:CHAPTER:0014"],
  "unknowns": []
}
```

约束不是世界规则清单；必须说明它怎样作用于机制的具体步骤或角色。

### 3.8 `escalation_logic`

```json
{
  "escalation_id": "PM:ESCALATION:001",
  "before_pressure_or_state": "升级前的压力、风险、资源、信息、权限或关系状态",
  "escalation_change": "造成升级、变形、反转或代价提高的结构变化",
  "after_pressure_or_state": "升级后的状态",
  "structural_effect": "它如何改变机制运行、路径、公开程度、角色关系或结果 stakes",
  "trigger_or_reason": "为什么此时发生升级",
  "evidence_refs": ["BOOK_01:CHAPTER:0015"],
  "unknowns": []
}
```

升级必须保留 `before → change → after → structural_effect`；“敌人更强”“数值更高”“规模更大”单独不足以构成 `escalation_logic`。

### 3.9 `outputs`

```json
{
  "output_id": "PM:OUTPUT:001",
  "output_kind": "result|resource|information|permission|recognition|relationship|risk|failure|other|UNKNOWN",
  "output": "一次机制运行直接产生的结果",
  "observable_evidence": "他人反应、公开结果、资源变化、权限验证、关系动作或可观察后果",
  "affected_targets": ["受到结果影响的目标、角色、线路或状态"],
  "payoff_relation": "not_established|supports|part_of_payoff|UNKNOWN",
  "evidence_refs": ["BOOK_01:CHAPTER:0016"],
  "unknowns": []
}
```

`outputs` 记录结果，但不自动等于 payoff；兑现路径必须在 `payoff_path` 中单独说明。

### 3.10 `state_transition`

```json
{
  "state_transition_id": "PM:STATE:001",
  "before_state": "机制运行前的目标、资源、身份、关系、认知、权限、风险或期待",
  "mechanism_run_or_result": "造成状态变化的运行或结果",
  "after_state": "机制运行后的全局或局部相关状态",
  "changed_domains": ["goal", "resource", "identity", "relationship", "cognition", "permission", "risk", "situation", "expectation"],
  "observable_consequence": "读者或其他角色可观察到的后果",
  "evidence_refs": ["BOOK_01:CHAPTER:0016"],
  "unknowns": []
}
```

`state_transition` 独立于 `outputs`；不能只写“事件结束”“进入下一章”或“进入下一卷”。

### 3.11 `repeatability`

```json
{
  "repeatability_status": "supported|partial|not_supported|UNKNOWN",
  "evidence_basis": "multiple_observed_instances|explicit_reusable_rule|mixed|single_instance_only|UNKNOWN",
  "repeat_conditions": ["再次运行必须满足的触发、输入、角色、约束或状态条件"],
  "reset_retain_or_reacquire": ["再次运行前哪些状态必须重置、保留或重新获得"],
  "core_invariants": ["跨实例必须保持的运行关系"],
  "reusable_scope": "能够再次工作的章节、阶段、角色关系或情境范围",
  "repeatability_evidence_refs": ["BOOK_01:CHAPTER:0020"],
  "unknowns": []
}
```

`repeatability` 不能简化为 `repeatable: true`。`single_instance_only` 只能支持候选或缺口说明，不能单独证明可复用性；schema 不以实例次数设置硬阈值。

### 3.12 `variation_points`

```json
{
  "variation_id": "PM:VARIATION:001",
  "variable_domain": "actor|resource|information|constraint|stakes|path|output|map|relationship|other|UNKNOWN",
  "what_can_change": "再次运行时可以替换或调整的变量",
  "invariant_preserved": "变化后仍需保持的核心运行关系",
  "effect_on_repetition": "该变化如何避免机械重复并改变结果或风险",
  "evidence_refs": ["BOOK_01:CHAPTER:0021"],
  "unknowns": []
}
```

### 3.13 `failure_modes`

```json
{
  "failure_mode_id": "PM:FAILURE:001",
  "failure_condition": "机制无法启动、运行中断、被识破、选择失败或结果反转的条件",
  "break_point": "运行链条在哪一步或哪个约束处断裂",
  "effect": "失败、打断或反转造成的可观察结果",
  "recoverability_or_next_state": "能否恢复、换路径、重新启动或进入什么后续状态",
  "evidence_refs": ["BOOK_01:CHAPTER:0022"],
  "unknowns": []
}
```

失败模式必须说明机制哪一环失效，不能只写“主角失败”。

### 3.14 `payoff_path`

```json
{
  "payoff_path_id": "PM:PAYOFF:001",
  "prior_pressure_promise_or_choice": "前置压力、承诺、选择或代价",
  "operation_ids": ["PM:OPERATION:001", "PM:OPERATION:002"],
  "decision_ids": ["PM:DECISION:001"],
  "payoff_or_recovery_result": "最终兑现、回收、失败回响或承诺改写",
  "visible_payoff_evidence": "公开结果、他人反应、关系动作、资源变化、选择验证或后续余震",
  "state_or_expectation_effect": "兑现后状态或读者期待如何变化",
  "evidence_refs": ["BOOK_01:CHAPTER:0023"],
  "unknowns": []
}
```

`payoff_path` 不能把普通 output 自动标成 payoff；必须说明前置压力/承诺/选择如何经过运行步骤转化为结果或回收。

## 4. `per_book` 单书记录

每本目标书应有一条 `per_book`，其 `mechanisms` 数组承载该书所有已证据化的独立机制；或在无法核验时有一条 `gap`。同一冻结范围内二者不能并存。

```json
{
  "record_type": "per_book",
  "schema_version": 1,
  "record_id": "PM:BOOK:BOOK_01",
  "status": "candidate",
  "book_id": "BOOK_01",
  "title": "仅作定位",
  "chapters_covered": "1-120",
  "mechanisms": [
    {
      "mechanism_identity": {},
      "observed_instances": [],
      "trigger_conditions": [],
      "actors_and_roles": [],
      "inputs": [],
      "operations": [],
      "decision_points": [],
      "constraints": [],
      "escalation_logic": [],
      "outputs": [],
      "state_transition": [],
      "repeatability": {},
      "variation_points": [],
      "failure_modes": [],
      "payoff_path": []
    }
  ],
  "adjacent_interfaces": {
    "plotline": [],
    "arc_structure": [],
    "opening": [],
    "character_function": [],
    "chapter_emotion": [],
    "worldbuilding": [],
    "cultivation": [],
    "golden_finger": []
  },
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "PASS"
}
```

空数组必须与 `unknowns`、`repeatability` 或 QA 结论一致，不能伪装为没有缺口的完整提取。`observed_instances` 只保存实例引用，不承载完整线路、人物、世界或章节摘要。

## 5. `gap` 缺口记录

```json
{
  "record_type": "gap",
  "schema_version": 1,
  "record_id": "PM:GAP:BOOK_01",
  "status": "candidate",
  "book_id": "BOOK_01",
  "evidence_refs": ["BOOK_01:CHAPTER:0001"],
  "unknowns": ["只有单一实例，无法核验复用条件"],
  "confidence": "LOW",
  "qa_status": "HOLD",
  "reason": "已有证据不足以区分单次事件与可复用机制",
  "known_evidence": ["存在一次带结果的剧情实例"],
  "blocked_outputs": ["高置信 mechanism_identity", "nearest_neighbor", "cluster"]
}
```

`gap` 必须说明已知证据、具体阻断原因和被阻断的下游判断，不得用虚构的 mechanism 填充缺口。

## 6. `nearest_neighbor` 近邻记录

近邻只能在全部目标书完成单书机制提取和 QA 后生成，并通过 `cross-book completion gate`：

```json
{
  "record_type": "nearest_neighbor",
  "schema_version": 1,
  "record_id": "PM:NEIGHBOR:001",
  "status": "candidate",
  "book_ids": ["BOOK_01", "BOOK_02"],
  "comparison_ids": ["PM:BOOK:BOOK_01", "PM:BOOK:BOOK_02"],
  "comparison_dimensions": {
    "trigger_and_inputs": "启动条件与输入结构",
    "roles_and_operations": "角色、操作、信息流与资源流",
    "decisions_and_constraints": "路径分叉与限制方式",
    "escalation_and_outputs": "升级与运行结果",
    "state_transition_and_repeatability": "状态变化与再次运行条件",
    "variation_and_failure": "变体、失效和反转边界",
    "payoff_path_and_adjacent_interfaces": "兑现路径与相邻接口"
  },
  "similarities": [],
  "difference_boundary": "相近但不合并的运行结构差异",
  "surface_labels_excluded": ["比赛", "任务", "追杀"],
  "decision": "merge_candidate|keep_distinct|insufficient_evidence",
  "reason": "基于运行结构、复用条件和差异证据的比较理由",
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "PASS"
}
```

不能仅因为表面事件相同建立近邻；必须比较触发、角色、操作、决策、约束、升级、输出、状态、复用和失败结构。

## 7. `cluster` 聚类候选

```json
{
  "record_type": "cluster",
  "schema_version": 1,
  "record_id": "PM:CLUSTER:001",
  "status": "candidate",
  "book_ids": ["BOOK_01", "BOOK_02"],
  "member_record_ids": ["PM:BOOK:BOOK_01", "PM:BOOK:BOOK_02"],
  "cluster_level": "大类|母型|子型|变体",
  "label": "描述运行方式的功能性名称",
  "shared_operation": "不同实例共享的触发→运行→升级→结果→复用结构",
  "invariants": ["跨书仍保持的核心关系"],
  "variation_pattern": "不同实例的角色、输入、约束、路径或结果如何变化",
  "failure_pattern": "共同的失效、打断或反转边界",
  "boundary_conditions": ["与相近候选区分所需的证据条件"],
  "supporting_book_count": 2,
  "nearest_neighbor_record_ids": ["PM:NEIGHBOR:001"],
  "merge_decision": "candidate_merge|candidate_split|new_candidate|insufficient_evidence|keep_distinct|unclustered|HOLD",
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "PASS"
}
```

`shared_operation` 必须描述机制如何运行，不能只写“考试”“比赛”“追杀”“任务”等表面类别。单书候选不能自动升级为跨书母型。

## 8. `qa` 与 `handoff` 记录

### 8.1 `qa`

```json
{
  "record_type": "qa",
  "schema_version": 1,
  "record_id": "PM:QA:BOOK_01:1-120",
  "status": "candidate",
  "book_id": "BOOK_01",
  "scope": "BOOK_01:1-120",
  "checks": {
    "instance_coverage": "PASS|HOLD|FAIL",
    "identity_and_boundary": "PASS|HOLD|FAIL",
    "trigger_and_inputs": "PASS|HOLD|FAIL",
    "roles_and_operations": "PASS|HOLD|FAIL",
    "decision_points": "PASS|HOLD|FAIL",
    "constraints_and_escalation": "PASS|HOLD|FAIL",
    "outputs_and_state_transition": "PASS|HOLD|FAIL",
    "repeatability": "PASS|HOLD|FAIL",
    "variation_and_failure": "PASS|HOLD|FAIL",
    "payoff_path": "PASS|HOLD|FAIL",
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

QA 至少核对：

1. 是否有多个实例、明确复用规则或诚实的 `single_instance_only` 缺口；
2. mechanism identity 是否描述运行结构而非题材标签；
3. trigger/input/role/operation 是否有证据；
4. operations 是否保留顺序或依赖，而不是事件列表；
5. decision point 是否存在真实路径分叉；
6. constraints 是否影响步骤或角色；
7. escalation 是否有 before→change→after→effect；
8. outputs、state_transition 和 payoff_path 是否分开；
9. variation_points 与 failure_modes 是否能解释复用和失效；
10. 相邻专项是否只通过 interface/reference 连接；
11. 跨书结果是否满足全部目标书完成后的阶段门。

### 8.2 `handoff`

```json
{
  "record_type": "handoff",
  "schema_version": 1,
  "record_id": "PM:HANDOFF:001",
  "status": "candidate",
  "book_ids": ["BOOK_01"],
  "candidate_record_ids": ["PM:BOOK:BOOK_01"],
  "recommended_action": "保留|合并候选|拆分候选|补证据|暂缓",
  "decision_points": ["需要人工确认的机制身份、复用条件、差异或边界"],
  "evidence_summary": ["支持候选的关键实例和运行证据"],
  "boundary_warnings": ["可能与剧情线、篇章、世界规则或金手指接口重叠的地方"],
  "blocked_by": [],
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "HOLD"
}
```

`handoff` 只把候选、证据、争议、边界和待决策项交给人工，不自动把机制写入正式素材库。

## 9. 跨专项边界与完成门

- `plotline`、`arc`、`opening`、`character_function`、`chapter_emotion`、`worldbuilding`、`cultivation` 和 `golden_finger` 只能作为 `adjacent_interfaces`、输入、约束、角色或结果证据；
- `observed_instances` 只能引用实例，不复制完整剧情线、章节摘要、人物功能、世界规则或金手指对象；
- `nearest_neighbor` 和 `cluster` 必须等待全部目标书的单书记录及 QA 完成；
- `gap`、`HOLD`、`UNKNOWN` 或上游 QA 未通过时，不得跨书补齐缺失运行结构；
- 任何 candidate 合并、母型命名、机制状态升级或正式入库都必须交给上位总控和人工审核；
- 本 schema 不提供正式素材库写入字段，也不授权修改任何正式资料。

本 schema 只冻结剧情机制的观察对象、实例引用、单书与派生记录、证据不确定性和相邻接口。具体 QA 判定顺序、重复疲劳检查、近邻/聚类合并规则、validator 硬约束和 agent 调用说明必须在后续文件中分别设计、测试和验收。
