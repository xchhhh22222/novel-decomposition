# 修炼成长系统横向拆解输出契约 V1.4

本文件是 `novel-cultivation-system-miner` 的 V1.4 专项记录契约，服从上位横向专项契约与阶段门契约。V1.4 使用 `schema_version: 2`；validator 同时保留对历史 `schema_version: 1` 的兼容。

本专项的最小分析单位不是一个等级名或一场胜负，而是可追溯的成长运行关系：

`公共规则 → 成长条件 → 状态变化 → 能力验证 → 代价/限制 → 下一步权限`

境界、实际战力、技能熟练度、装备资源和身份权限必须分栏、分证据、分状态，任何一个层次都不能代替另一个层次。

## 1. 统一 envelope

除未来由上位契约明确指定的 canonical 权威记录外，本专项所有机器可读派生记录使用统一 envelope：

```json
{
  "record_type": "per_book|nearest_neighbor|cluster|qa|handoff|gap",
  "schema_version": 2,
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

## 2. V1.4 组件记录边界

### 2.1 共享成长前提 `shared_foundations`

只记录多套体系共同服从且有证据的公共规则；没有共同规则时允许为空对象或保留 `UNKNOWN`。

```json
{
  "scope": "适用人群、区域或时代",
  "shared_rules": [],
  "shared_resources": [],
  "shared_validation": [],
  "shared_constraints": [],
  "evidence_refs": [],
  "unknowns": []
}
```

### 2.2 修炼体系 `cultivation_systems[]`

一本书实际存在几套就记录几套，不预设数量。

```json
{
  "system_id": "CS:SYSTEM:001",
  "name_in_book": "原书体系名",
  "system_type": "body|energy|spirit|bloodline|summoning|artifact|hybrid|other|UNKNOWN",
  "population_scope": "谁能进入",
  "entry_condition": "入门条件",
  "energy_or_power_source": "力量来源",
  "training_method": "主要修炼方式",
  "growth_loop": "条件→训练/转化→验证→下一阶段",
  "realm_system": {
    "realm_order": [],
    "transition_events": [],
    "break_conditions": [],
    "realm_limits": [],
    "unknowns": []
  },
  "resource_requirements": [],
  "validation_methods": [],
  "combat_expression": "如何表现能力",
  "strengths": [],
  "hard_limits": [],
  "evidence_refs": ["BOOK_01:CHAPTER:0002"],
  "unknowns": []
}
```

每个 `realm_order` 与 `transition_events` 沿用 V1.3 的直接证据标准，但只存在于所属 `system_id` 内。正式突破仍必须有 `direct_evidence_refs`。

### 2.3 体系关系 `system_relations[]`

只有同书存在两套以上体系时才记录：

```json
{
  "relation_id": "CS:SYSTEM_REL:001",
  "system_a": "CS:SYSTEM:001",
  "system_b": "CS:SYSTEM:002",
  "relation_type": "parallel|exclusive|complementary|convertible|counter|dependency|hybrid|UNKNOWN",
  "can_dual_cultivate": "true|false|UNKNOWN",
  "shared_resources": [],
  "exclusive_or_competing_resources": [],
  "conversion_rule": "UNKNOWN",
  "power_mapping_or_validation": "UNKNOWN",
  "synergy_or_conflict": "互补或冲突如何发生",
  "evidence_refs": ["BOOK_01:CHAPTER:0020"],
  "unknowns": []
}
```

`system_a/system_b` 必须引用本书已有 system；单体系作品该数组必须为空。跨体系战力对位没有直接证据时只能写 `UNKNOWN`。

### 2.4 功法/武技 `techniques[]`

```json
{
  "technique_id": "CS:TECHNIQUE:001",
  "name_in_book": "原书名称",
  "category": "cultivation_manual|combat_art|movement|secret_art|spirit_art|body_art|support|forbidden|other|UNKNOWN",
  "compatible_system_ids": ["CS:SYSTEM:001"],
  "prerequisites": [],
  "training_method": "如何练",
  "progression_or_stages": [],
  "core_effect": "核心效果",
  "secondary_effects": [],
  "costs": [],
  "risks": [],
  "hard_limits": [],
  "source_and_access": "获得渠道",
  "evidence_refs": ["BOOK_01:CHAPTER:0007"],
  "unknowns": []
}
```

功法本体与人物熟练度分离；仅确认存在时不得补造完整运行机制。

### 2.5 法宝/装备 `artifacts[]`

```json
{
  "artifact_id": "CS:ARTIFACT:001",
  "name_in_book": "原书名称",
  "category": "weapon|armor|artifact|spirit_item|technology|space_item|support_item|special_item|other|UNKNOWN",
  "compatible_system_ids": ["CS:SYSTEM:001"],
  "quality_or_grade": "已证实等级或 UNKNOWN",
  "activation_or_use": "如何使用",
  "core_effect": "核心效果",
  "energy_or_resource_cost": [],
  "hard_limits": [],
  "growth_or_upgrade": "成长、升级、修复或 UNKNOWN",
  "ownership_or_duration": "归属与持续性",
  "source_and_access": "来源",
  "evidence_refs": ["BOOK_01:CHAPTER:0015"],
  "unknowns": []
}
```

装备等级与人物境界严格分离。

### 2.6 成长资源 `resource_assets[]`

```json
{
  "resource_id": "CS:RESOURCE:001",
  "name_in_book": "原书名称",
  "resource_kind": "medicine|material|currency|points|core|consumable|training_resource|other|UNKNOWN",
  "compatible_system_ids": ["CS:SYSTEM:001"],
  "source_and_access": "如何获得",
  "use_or_conversion": "如何进入训练、装备或功法",
  "scarcity_or_cost": "稀缺、价格或风险",
  "consumption_or_loss": "如何消耗",
  "observable_growth_effect": "可观察效果",
  "permanent_self_change_proven": false,
  "evidence_refs": ["BOOK_01:CHAPTER:0015"],
  "unknowns": []
}
```

资源到账不等于永久成长；世界层的生产、垄断和价格结构仍归 worldbuilding。

### 2.7 主角构筑 `protagonist_build`

```json
{
  "person_id": "PROTAGONIST",
  "system_ids": ["CS:SYSTEM:001"],
  "selected_attributes": [],
  "route_choices": [],
  "technique_ids": ["CS:TECHNIQUE:001"],
  "artifact_ids": [],
  "tradeoffs": [],
  "build_change_events": [],
  "evidence_refs": [],
  "unknowns": []
}
```

### 2.8 技能熟练度 `skill_proficiency`

只追踪人物对 `technique_id` 的 `obtained → learning → practiced → mastered → proficient → evolved` 状态，不再用技能名重新定义第二份功法对象。

### 2.9 实际战力 `actual_combat_power`

沿用“名义境界 + 修正来源 + 可观察表现”的边界，并增加 `system_id` 和可选组件引用。装备、功法、资源、环境、克制、情报和金手指都只能作为 modifier，不能反推正式境界。

### 2.10 身份权限与金手指接口

`identity_permissions` 沿用 V1.3 规则。V1.4 的 `golden_finger_interfaces.affected_layer` 允许：

`system|realm|build|technique|artifact|combat_power|resource|permission`

不得复制金手指专项的完整输入/处理/输出。

## 3. 单书 `per_book` 记录

每本目标书必须有一条 `per_book` 或一条 `gap`。V1.4 单书记录只拆来源书实际存在的组件：

```json
{
  "record_type": "per_book",
  "schema_version": 2,
  "record_id": "CS:BOOK:BOOK_01",
  "status": "candidate",
  "book_id": "BOOK_01",
  "title": "书名",
  "chapters_covered": "1-120",
  "shared_foundations": {},
  "cultivation_systems": [],
  "system_relations": [],
  "techniques": [],
  "artifacts": [],
  "resource_assets": [],
  "protagonist_build": {},
  "golden_finger_interfaces": [],
  "actual_combat_power": {},
  "skill_proficiency": {},
  "identity_permissions": {},
  "milestones": {
    "first_system_display": {},
    "first_direct_realm_change": {},
    "first_technique_validation": {},
    "first_artifact_validation": {},
    "first_cross_system_relation_validation": {}
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

硬规则：

1. `cultivation_systems` 数量只由来源证据决定；
2. 每套体系拥有自己的 `realm_system`；
3. `system_relations`、`compatible_system_ids` 与主角构筑引用只能指向本书已有 ID；
4. 单体系作品保持 `system_relations=[]`；
5. 无法确认任何体系运行方式时使用 `gap`，不得补造；
6. 跨书拼装只发生在创造层，绝不能污染单书记录。

## 4. `gap` 缺口记录

证据不足以确认某书的修炼体系或正式境界时，保留缺口而不补造规则：

```json
{
  "record_type": "gap",
  "schema_version": 2,
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
  "schema_version": 2,
  "record_id": "CS:NEIGHBOR:001",
  "status": "candidate",
  "book_ids": ["BOOK_01", "BOOK_02"],
  "comparison_ids": ["CS:BOOK:BOOK_01", "CS:BOOK:BOOK_02"],
  "comparison_dimensions": {
    "system_training_and_growth": "各体系的输入、训练、成长和验证结构",
    "realm_and_breakthrough": "各体系境界、突破条件与直接证据",
    "technique_operation": "功法/武技的训练、效果和限制",
    "artifact_operation": "法宝/装备的激活、消耗、效果和成长",
    "resource_conversion": "资源如何进入训练、装备或突破",
    "multi_system_relation": "并行、兼修、互斥、转化、克制或融合",
    "protagonist_build_and_power": "构筑选择与名义境界/实际战力的关系",
    "interfaces": "金手指、世界观和权限如何影响成长"
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
  "schema_version": 2,
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
  "schema_version": 2,
  "record_id": "CS:QA:BOOK_01:1-120",
  "status": "candidate",
  "book_id": "BOOK_01",
  "scope": "BOOK_01:1-120",
  "checks": {
    "coverage": "PASS|HOLD|FAIL",
    "evidence_traceability": "PASS|HOLD|FAIL",
    "source_only_extraction": "PASS|HOLD|FAIL",
    "multi_system_boundary": "PASS|HOLD|FAIL",
    "realm_ownership": "PASS|HOLD|FAIL",
    "system_relation_integrity": "PASS|HOLD|FAIL",
    "technique_artifact_boundary": "PASS|HOLD|FAIL",
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
  "schema_version": 2,
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
