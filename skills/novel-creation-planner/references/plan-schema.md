# 创造计划机器契约

只有用户要求保存计划包时才落盘 JSON。所有未确认计划保持 `status: candidate`。

## 顶层

```json
{
  "schema_version": 1,
  "plan_id": "PLAN_...",
  "status": "candidate",
  "creation_mode": "greenfield",
  "plan_mode": "preliminary",
  "brief": {},
  "shared_library_root": "",
  "market_evidence": {
    "as_of": "YYYY-MM-DD",
    "sources": [],
    "samples": [],
    "signals": [],
    "coverage_status": "complete",
    "bias_notes": []
  },
  "library_usage": {
    "formal_card_ids": [],
    "dna_candidate_ids": [],
    "gaps": []
  },
  "concept_options": [],
  "recommendation": {"concept_id": "A", "outcome": "RECOMMEND"},
  "architecture_concept_id": "A",
  "architecture_300": [],
  "longline_engine_summary": "",
  "debt_ledgers": {},
  "material_gap_orders": [],
  "pending_decisions": []
}
```

`preliminary` 模式允许 `architecture_300: []`，但必须填写 `longline_engine_summary`。`full` 模式必须提供七阶段结构。正文样本少于6本时使用 `coverage_status: partial`，并在 `bias_notes` 明确偏差。

`creation_mode` 只允许 `greenfield / existing_project`。`greenfield` 不得引用当前工作目录中的小说资料；`existing_project` 必须记录用户明确指定的项目。`shared_library_root` 使用共享素材库绝对路径，不得用当前小说目录的相对 `素材库/` 冒充公共库。

`market_evidence.samples` 固定保留榜单前10名，每项至少包含 `sample_id / rank / title / content_status / analyzed_chapters / opening_analysis`。`content_status=pass` 时必须实际分析第1—10章，并在 `opening_analysis` 保存前三章爆点与第4—10章持续性证据；不能用简介或书名代填。至少6本 pass 才允许 `RECOMMEND`。`market_evidence.signals` 每项包含 `signal_id / signal_type / claim / evidence_sample_ids`，其中证据样本 ID 必须真实存在于 `samples`。每案的 `market_signal_ids` 只能引用这个信号集合。

## 三案

每案包含：

```text
concept_id
positioning
reader_promise
protagonist
golden_finger
relationship_topology
world_cultivation_resource_loop
named_story_bible（书名、人物、机构、世界、修炼、资源的候选专名与规则）
opening_1_10
story_engine
longline_engine_summary
market_signal_ids（至少1项）
material_mapping（formal_card_ids / dna_candidate_ids / gaps，至少1项非空）
differentiation_signature
originality_changes（至少4项）
risks
hard_gate（PASS/HOLD/FAIL）
score
score_breakdown
```

`opening_1_10` 必须是10项列表，章号严格为1—10，每项包含 `chapter / primary_event / emotion / payoff / hook`。

`differentiation_signature` 固定包含：

```text
reader_promise
protagonist_identity_goal
golden_finger_logic
relationship_topology
central_conflict
resource_loop
world_institution
longline_mystery
```

三案两两比较时，上述八项至少四项实质不同。`market_signal_ids` 必须引用本计划的市场信号；`material_mapping` 只记本案实际使用的正式卡、DNA candidate 或明确缺口。

`score_breakdown` 固定键与上限：

```text
market_reader_promise: 15
opening_1_10: 15
long_engine_61_300: 20
mechanic_world_resource_fit: 15
relationship_sustainability: 10
emotion_pacing: 10
originality_distance: 10
material_feasibility: 5
```

总分必须等于八项之和。`RECOMMEND` 只允许引用 `hard_gate: PASS` 且总分不低于80的方案。

## 完整模式

`architecture_concept_id` 必须等于推荐方案ID。`architecture_300` 范围固定为：

`1-3 / 4-10 / 11-30 / 31-60 / 61-120 / 121-200 / 201-300`

每阶段包含：

```text
range
central_question
protagonist_goal
conflict
characters
growth_and_resources
emotion_payoff
mainline_progress
fatigue_refresh
structure_refresh
irreversible_change
material_support
```

完整规划至少两阶段具有非空 `structure_refresh`。`material_support` 中状态为 `GAP` 的项目必须引用 `gap_order_id`。

`material_support` 必须是对象列表。每项 `status` 只能是 `SUPPORTED / ADAPTABLE / GAP`；前两者必须提供 `material_id`，`GAP` 必须提供 `gap_order_id`。

`debt_ledgers` 固定覆盖：`emotion / growth / resource / relationship / world_rule / antagonist / mainline_foreshadowing`，完整模式下每项都必须有至少1条。通用字段为 `debt_id / opened_phase / promise / payoff_window / visible_evidence / status / planned_payoff / overdue_risk`。`antagonist` 条目额外要求 `antagonist_goal / pressure_escalation / stage_failure_or_payoff / exit_window`。

引用必须闭环：方案级 `material_mapping` 必须是顶层 `library_usage` 的子集；阶段级 `SUPPORTED` 只能引用顶层正式卡，`ADAPTABLE` 只能引用顶层 DNA candidate，`GAP` 只能引用实际存在的缺口工单。

每个 `material_gap_orders` 项包含：`gap_order_id / needed_function / target_phase / target_emotion / prerequisites / acceptance_evidence / forbidden_patterns`。

保存后运行：

```powershell
python -X utf8 scripts/validate_creation_plan.py <plan.json>
```
