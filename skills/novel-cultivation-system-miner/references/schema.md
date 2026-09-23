# 修炼成长系统横向拆解输出契约

本文件是 `novel-cultivation-system-miner` 的专项记录契约，服从上位横向专项契约、阶段门契约和本专项 `SKILL.md` 的八层职责边界。

本专项的最小分析单位不是一个等级名或一场胜负，而是可追溯的成长运行关系：

`公共规则 → 成长条件 → 状态变化 → 能力验证 → 代价/限制 → 下一步权限`

境界、实际战力、技能熟练度、装备资源和身份权限必须分栏、分证据、分状态，任何一个层次都不能代替另一个层次。

## 1. 统一 envelope

除未来由上位契约明确指定的 canonical 权威记录外，本专项所有机器可读派生记录使用统一 envelope：

```json
{
  "record_type": "per_book|nearest_neighbor|cluster|qa|handoff|gap",
  "schema_version": 1,
  "record_id": "CS:<TYPE>:<STABLE_ID>",
  "status": "candidate",
  "book_id": "BOOK_01",
  "book_ids": ["BOOK_01", "BOOK_02"],
  "evidence_refs": ["BOOK_01:CHAPTER:0001", "BOOK_01:STAGE:01"],
  "unknowns": [],
  "confidence": "HIGH|MEDIUM|LOW",
  "qa_status": "PASS|HOLD|FAIL"
}
```

实际记录按作用只使用 `book_id` 或 `book_ids` 其中之一：`per_book`、`qa`、`gap` 使用 `book_id`；`nearest_neighbor`、`cluster`、`handoff` 使用 `book_ids`。所有记录的 `status` 固定为 `candidate`，不定义 `active`、`deprecated` 或正式素材库写入字段。`evidence_refs` 必须能回到章节、阶段或已有情绪 overlay；`unknowns` 只能记录真实缺口。关键未知存在时不得使用 `HIGH`。

## 2. 八层记录边界

### 2.1 通用修炼体系 `universal_system`

记录所有或大多数修炼者共享的公共规则，不写主角独有外挂：

```json
{
  "scope": "适用人群、区域或时代",
  "public_rules": [
    {
      "rule_id": "CS:RULE:001",
      "rule_statement": "公共修炼规则",
      "training_path": "训练、学习、吸收或验证方式",
      "growth_loop": "条件→训练/转化→验证→下一阶段",
      "resource_requirements": ["公共资源门槛"],
      "validation_methods": ["如何被体系或剧情确认"],
      "constraints_and_costs": ["限制、失败和代价"],
      "evidence_refs": ["BOOK_01:CHAPTER:0001"],
      "unknowns": []
    }
  ],
  "common_permissions": ["公共成长权限或资格"],
  "unknowns": []
}
```

社会如何生产、分配和垄断资源属于 worldbuilding；这里只记录公共修炼规则如何使用这些资源、限制成长或验证结果。

### 2.2 境界体系 `realm_system`

境界记录必须把名义阶段、突破条件和直接变化证据分开：

```json
{
  "realm_order": [
    {
      "realm_id": "CS:REALM:001",
      "name_in_book": "原书阶段名",
      "order": 1,
      "stage_difference": "与前后阶段可观察的稳定差异",
      "direct_evidence_refs": ["BOOK_01:CHAPTER:0002"]
    }
  ],
  "transition_events": [
    {
      "event_id": "CS:REALM_CHANGE:001",
      "person_id": "PROTAGONIST",
      "before": "前一正式境界或 UNKNOWN",
      "trigger_or_condition": "突破触发与完成条件",
      "after": "后一正式境界或 UNKNOWN",
      "change_type": "formal_realm_change|UNKNOWN",
      "direct_evidence_refs": ["BOOK_01:CHAPTER:0010"],
      "costs_or_risks": ["突破代价或失败风险"],
      "unknowns": []
    }
  ],
  "break_conditions": ["已证实或明确未知的突破条件"],
  "realm_limits": ["阶段上限、门槛或不可跨越条件"],
  "unknowns": []
}
```

硬规则：

1. 正式境界变化必须有直接证据；
2. 缺少直接证据时，`after` 不得由击杀、胜负、称号、装备、权限或资源结果推导，应写 `UNKNOWN` 并保留缺口；
3. “突破”“变强”“越级”“击杀强敌”不是自动的 `formal_realm_change`；
4. 技能熟练度、装备加成、短时 buff、规则克制和环境优势不能写进 `transition_events` 充当境界变化。

### 2.3 主角构筑 `protagonist_build`

记录主角实际选择和取舍，不把选择本身写成世界通用规则：

```json
{
  "person_id": "PROTAGONIST",
  "selected_attributes": ["属性、方向或构筑标签"],
  "route_choices": ["路线、流派或训练偏向"],
  "skill_combinations": ["已被证据支持的组合"],
  "tradeoffs": ["放弃的路线、成本或限制"],
  "build_change_events": [
    {
      "before": "旧构筑",
      "choice_or_trigger": "为何改变",
      "after": "新构筑",
      "evidence_refs": ["BOOK_01:CHAPTER:0020"],
      "unknowns": []
    }
  ],
  "evidence_refs": ["BOOK_01:CHAPTER:0001"],
  "unknowns": []
}
```

主角构筑不等于人物功能、不等于主线动机，也不等于金手指本体。一次获得资源或技能只有在被主角选择、组合、训练或验证后，才可作为构筑证据。

### 2.4 金手指接口 `golden_finger_interfaces`

只记录金手指怎样改变修炼成长，不复制金手指专项的输入/处理/输出字段：

```json
{
  "interface_id": "CS:GF_INTERFACE:001",
  "golden_finger_record_refs": ["GF:BOOK:BOOK_01"],
  "growth_effect": "提供资源入口、选择权、效率、验证场或限制变化",
  "affected_layer": "realm|build|skill|combat_power|resource|permission",
  "boundary": "哪些部分仍属于金手指专项",
  "evidence_refs": ["BOOK_01:CHAPTER:0005"],
  "unknowns": []
}
```

不得把金手指升级重新拆成修炼体系升级；不得把外挂产生的结果自动写成公共规则或正式境界变化。

### 2.5 实际战力 `actual_combat_power`

实际战力必须能够记录“名义境界 + 修正来源 + 观察结果”，但不能反向推导境界：

```json
{
  "assessment_events": [
    {
      "event_id": "CS:POWER_ASSESS:001",
      "person_id": "PROTAGONIST",
      "nominal_realm": "当前已被直接证实的名义境界或 UNKNOWN",
      "observed_capability": "实际表现、可达对手或完成任务",
      "modifiers": [
        {
          "source": "构筑/熟练度/装备/资源/经验/环境/克制/信息/规则优势",
          "effect": "如何改变本次表现",
          "duration": "短时、场景内、长期或 UNKNOWN"
        }
      ],
      "combat_result": "胜负、击杀、逃脱或任务结果",
      "realm_change_proven": false,
      "direct_realm_evidence_refs": [],
      "evidence_refs": ["BOOK_01:CHAPTER:0012"],
      "unknowns": []
    }
  ],
  "power_gap_explanations": ["名义境界与实际表现的差异来源"],
  "unknowns": []
}
```

`combat_result` 只说明一次表现；即使结果很强，也不得把 `realm_change_proven` 自动改为 `true`。短时 buff、装备加成、技巧克制、规则优势和越级战斗必须保留在 `modifiers` 或其接口层。

### 2.6 技能熟练度 `skill_proficiency`

技能必须区分获得、学习、掌握、精通和演化：

```json
{
  "skill_events": [
    {
      "skill_id": "CS:SKILL:001",
      "name_in_book": "技能或功法名",
      "state_transitions": [
        {
          "from_state": "UNKNOWN|obtained|learning|practiced|mastered|proficient|evolved",
          "trigger_or_training": "获得、学习、训练、实战或演化原因",
          "to_state": "obtained|learning|practiced|mastered|proficient|evolved|UNKNOWN",
          "visible_validation": "稳定施展、结果、失败修正或他人反应",
          "evidence_refs": ["BOOK_01:CHAPTER:0007"],
          "unknowns": []
        }
      ],
      "hard_limits": ["技能限制和失效条件"],
      "costs": ["使用代价"],
      "evidence_refs": ["BOOK_01:CHAPTER:0007"],
      "unknowns": []
    }
  ],
  "proficiency_boundaries": ["获得不等于掌握、掌握不等于精通、精通不等于境界突破"]
}
```

一次成功施展不能自动证明长期掌握；技能演化也不能自动证明境界提升。若只确认技能存在而没有掌握证据，保留 `obtained` 或 `UNKNOWN`。

### 2.7 装备与资源 `equipment_resources`

装备、资源、功法和消耗品必须区分短期效果、消耗过程和是否转化为自身永久状态：

```json
{
  "items": [
    {
      "item_id": "CS:ITEM:001",
      "name_in_book": "物品、材料或资源名",
      "item_kind": "equipment|medicine|material|manual|points|consumable|other",
      "effect_mode": "temporary_boost|consumable|long_term_conversion|permanent_self_growth|access_only|UNKNOWN",
      "source_and_access": "如何获得",
      "use_or_conversion": "如何使用、消耗、吸收或转化",
      "duration_or_ownership": "持续时间和归属",
      "growth_effect": "对境界、构筑、技能、战力或权限的实际影响",
      "permanent_self_change_proven": false,
      "evidence_refs": ["BOOK_01:CHAPTER:0015"],
      "unknowns": []
    }
  ],
  "resource_loops": [
    {
      "input": "资源来源",
      "conversion": "进入训练或成长的方式",
      "output": "可观察的状态变化",
      "loss_or_cost": "消耗、风险或失败",
      "evidence_refs": ["BOOK_01:CHAPTER:0015"],
      "unknowns": []
    }
  ]
}
```

资源到账、装备到手或功法获得不等于永久成长。`permanent_self_change_proven` 只有在原文明确显示自身基础状态发生持续变化时才可为 `true`；否则保留 `false` 或 `UNKNOWN`。

### 2.8 身份与权限 `identity_permissions`

权限记录它打开了什么训练、资源、地图或信息入口，但必须与修炼等级分开：

```json
{
  "permission_events": [
    {
      "permission_id": "CS:PERMISSION:001",
      "name_in_book": "军衔、资格、准入或组织权限",
      "issuer_or_owner": "授予者或归属机构",
      "access_unlocked": ["行动或信息范围"],
      "training_entry": ["训练机会"],
      "resource_entry": ["资源机会"],
      "map_entry": ["地图或区域入口"],
      "growth_effect_type": "access_only|changes_condition|formal_growth|UNKNOWN",
      "realm_change_proven": false,
      "direct_realm_evidence_refs": [],
      "evidence_refs": ["BOOK_01:CHAPTER:0020"],
      "unknowns": []
    }
  ],
  "permission_boundaries": ["身份权限不自动等于修炼等级"]
}
```

只有直接证据显示权限改变了突破条件或正式成长状态时，才可记录 `formal_growth`；否则默认属于访问、资源、训练或地图入口变化。

## 3. 单书 `per_book` 记录

每本目标书必须有一条 `record_type: per_book`，或在无法核验时有一条 `record_type: gap`；同一目标书不能两者并存。

```json
{
  "record_type": "per_book",
  "schema_version": 1,
  "record_id": "CS:BOOK:BOOK_01",
  "status": "candidate",
  "book_id": "BOOK_01",
  "title": "书名",
  "chapters_covered": "1-120",
  "universal_system": {},
  "realm_system": {},
  "protagonist_build": {},
  "golden_finger_interfaces": [],
  "actual_combat_power": {},
  "skill_proficiency": {},
  "equipment_resources": {},
  "identity_permissions": {},
  "milestones": {
    "first_system_display": {},
    "first_realm_display": {},
    "first_direct_realm_change": {},
    "first_skill_mastery_validation": {},
    "first_combat_power_validation": {}
  },
  "emotion_overlay_links": [],
  "growth_fatigue_risks": [],
  "source_numbering_notes": [],
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "PASS"
}
```

字段共同要求：每个正式境界变化都必须回到 `transition_events.direct_evidence_refs`；每条成长判断必须说明所属层次；`milestones` 区分体系展示、境界展示、直接境界变化、技能掌握验证和实际战力验证；`emotion_overlay_links` 只引用既有情绪记录；缺少一层证据时写入 `unknowns` 或形成 `gap`，不得用相邻层次替代。

## 4. `gap` 缺口记录

证据不足以确认某书的修炼体系或正式境界时，保留缺口而不补造规则：

```json
{
  "record_type": "gap",
  "schema_version": 1,
  "record_id": "CS:GAP:BOOK_01",
  "status": "candidate",
  "book_id": "BOOK_01",
  "evidence_refs": ["BOOK_01:CHAPTER:0001"],
  "unknowns": ["正式境界变化", "技能掌握证据"],
  "confidence": "LOW",
  "qa_status": "HOLD",
  "reason": "现有范围不足以确认成长系统如何运行",
  "known_evidence": ["仅确认出现修炼名词"],
  "blocked_outputs": ["高置信 per_book", "跨书近邻", "跨书聚类"]
}
```

`gap` 不是空白占位符，必须写明已有证据、缺少层次和被阻断的下游判断。

## 5. `nearest_neighbor` 近邻记录

只有全部目标书完成 `per_book` 抽取和单书 QA 后，才能建立近邻。比较的是成长系统的运行方式：

```json
{
  "record_type": "nearest_neighbor",
  "schema_version": 1,
  "record_id": "CS:NEIGHBOR:001",
  "status": "candidate",
  "book_ids": ["BOOK_01", "BOOK_02"],
  "comparison_ids": ["CS:BOOK:BOOK_01", "CS:BOOK:BOOK_02"],
  "comparison_dimensions": {
    "universal_system": "公共修炼规则如何约束成长",
    "realm_system": "阶段、突破和直接证据如何运行",
    "protagonist_build": "构筑选择与取舍",
    "actual_combat_power": "名义境界与真实战力的修正关系",
    "skill_proficiency": "技能获得、掌握、精通和演化",
    "equipment_resources": "资源如何进入成长、消耗或长期转化",
    "identity_permissions": "权限如何打开路径但不冒充等级",
    "interfaces": "金手指、世界观和主线如何影响成长"
  },
  "similarities": [],
  "difference_boundary": "保持相近但不合并的关键差异",
  "decision": "merge_candidate|keep_distinct|insufficient_evidence",
  "reason": "比较理由",
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "PASS"
}
```

不能只因都有“一境二境”、炼体炼气、技能升级、突破或越级战斗就建立近邻。必须比较至少一个成长运行环节，并同时写出关键差异和证据。

## 6. `cluster` 聚类候选

聚类单位是可复用的成长运行方式，不是等级名、题材标签或战果名：

```json
{
  "record_type": "cluster",
  "schema_version": 1,
  "record_id": "CS:CLUSTER:001",
  "status": "candidate",
  "book_ids": ["BOOK_01", "BOOK_02"],
  "member_record_ids": ["CS:BOOK:BOOK_01", "CS:BOOK:BOOK_02"],
  "cluster_level": "大类|母型|子型|变体",
  "label": "不复制专名的功能性名称",
  "shared_operation": "公共规则→成长条件→状态变化→验证→限制的共同运行方式",
  "boundary_conditions": ["与相近候选保持区分的条件"],
  "supporting_book_count": 2,
  "nearest_neighbor_record_ids": ["CS:NEIGHBOR:001"],
  "merge_decision": "candidate_merge|candidate_split|new_candidate|insufficient_evidence|keep_distinct|unclustered|HOLD",
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "PASS"
}
```

`shared_operation` 必须描述成长系统如何运作，不能只写“等级升级”“炼体流”“技能变强”或其它表面名词。允许 `unclustered`、`insufficient_evidence` 和 `HOLD`，不得为了覆盖率强行归簇。任何来源书数都不能自动生成 `active` 或正式母型。

## 7. `qa` 记录

QA 只报告证据、混淆和阻断，不反向修改原始章节或单书记录：

```json
{
  "record_type": "qa",
  "schema_version": 1,
  "record_id": "CS:QA:BOOK_01:1-120",
  "status": "candidate",
  "book_id": "BOOK_01",
  "scope": "BOOK_01:1-120",
  "checks": {
    "coverage": "PASS|HOLD|FAIL",
    "evidence_traceability": "PASS|HOLD|FAIL",
    "universal_vs_realm_boundary": "PASS|HOLD|FAIL",
    "realm_direct_evidence": "PASS|HOLD|FAIL",
    "skill_state_boundary": "PASS|HOLD|FAIL",
    "combat_power_boundary": "PASS|HOLD|FAIL",
    "resource_permission_boundary": "PASS|HOLD|FAIL",
    "interface_boundary": "PASS|HOLD|FAIL",
    "cross_book_gate": "PASS|HOLD|FAIL"
  },
  "contamination_risks": [],
  "gaps": [],
  "disputes": [],
  "blocked_outputs": [],
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "PASS"
}
```

QA 至少要能指出：是否把战果反推境界、把技能获得写成掌握、把资源到账写成永久成长、把权限写成等级，或把金手指/世界观/主线字段复制进本专项。章节事实 QA 为 FAIL 或关键层为 UNKNOWN 时，不支持高置信跨书聚合。

## 8. `handoff` 交接记录

`handoff` 只把候选、证据、差异和待确认边界交给人工审核：

```json
{
  "record_type": "handoff",
  "schema_version": 1,
  "record_id": "CS:HANDOFF:001",
  "status": "candidate",
  "book_ids": ["BOOK_01"],
  "candidate_record_ids": ["CS:BOOK:BOOK_01"],
  "recommended_action": "保留|合并候选|拆分候选|补证据|暂缓",
  "decision_points": ["需要人工确认的境界、技能、资源或权限边界"],
  "evidence_gaps": [],
  "forbidden_automatic_actions": ["写入active", "把战果改写为境界", "写入正式素材库"],
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "LOW",
  "qa_status": "HOLD"
}
```

交接不代表候选已经通过审核、成为正式母型或获得入库权限。

## 9. 统一禁止事项

- 不根据书名、简介、题材或模型记忆补造修炼规则、境界、突破条件或阶段差异；
- 不把境界、实际战力、技能熟练度、装备资源和身份权限合成一个“成长值”；
- 不以击杀、越级、称号、装备、资源或权限替代正式境界直接证据；
- 不把获得技能直接写成掌握、精通或演化；
- 不把金手指、世界观、人物、主线、开篇、篇章或剧情机制字段复制进本专项；
- 不把不完整记录用常识补成完整记录；
- 不在全部目标书完成单书 QA 前建立正常近邻或聚类；
- 不把单书候选写成 `active`、`deprecated`、正式母型或正式素材卡；
- 不修改源章节、既有 canonical 情绪记录、总索引或正式素材库。
