# 创造计划机器契约 V1.1

只有用户要求保存计划包时才落盘 JSON。所有未确认计划保持 `status: candidate`。

## 顶层

```json
{
  "schema_version": 2,
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
  "material_dispatch": {
    "status": "complete",
    "slots": [],
    "source_concentration_risks": [],
    "compatibility_checks": [],
    "stop_reason": ""
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

`schema_version: 2` 是 novel-creation-planner V1.1 的当前写入版本；V1 仅用于兼容旧计划。`creation_mode` 只允许 `greenfield / existing_project`。`greenfield` 不得引用当前工作目录中的小说资料；`existing_project` 必须记录用户明确指定的项目。`shared_library_root` 使用共享素材库绝对路径，不得用当前小说目录的相对 `素材库/` 冒充公共库。

`market_evidence.samples` 固定保留榜单前10名，每项至少包含 `sample_id / rank / title / content_status / analyzed_chapters / opening_analysis`。`content_status=pass` 时必须实际分析第1—10章，并在 `opening_analysis` 保存前三章爆点与第4—10章持续性证据；不能用简介或书名代填。至少6本 pass 才允许 `RECOMMEND`。`market_evidence.signals` 每项包含 `signal_id / signal_type / claim / evidence_sample_ids`，其中证据样本 ID 必须真实存在于 `samples`。每案的 `market_signal_ids` 只能引用这个信号集合。

## 素材调度记录 V1.1

`schema_version: 2` 必须包含 `material_dispatch`。旧版 `schema_version: 1` 计划仍可由 validator 读取。

```json
{
  "material_dispatch": {
    "status": "complete|partial|hold",
    "slots": [
      {
        "slot_id": "SLOT:PRIMARY_SYSTEM",
        "role": "primary_system",
        "required": true,
        "wave": 1,
        "modules": ["cultivation_system"],
        "component_types": ["cultivation_system"],
        "query_groups": ["低门槛成长 实战验证"],
        "target_candidates": 5,
        "source_strategy": "cross_book|same_source_bundle|either",
        "selected_refs": [
          {
            "material_id": "CS:SYSTEM:001",
            "material_kind": "formal_card|dna_record|dna_component",
            "module": "cultivation_system",
            "record_id": "CS:BOOK:BOOK_01",
            "component_type": "cultivation_system",
            "book_id": "BOOK_01",
            "qa_status": "PASS"
          }
        ],
        "rejected_refs": [],
        "gap_reason": ""
      }
    ],
    "source_concentration_risks": [],
    "compatibility_checks": [
      {
        "check_id": "COMPAT:001",
        "materials": ["CS:SYSTEM:001", "CS:ARTIFACT:003"],
        "dimension": "resource_interface",
        "result": "PASS|HOLD|FAIL",
        "reason": "为何可接或为何冲突"
      }
    ],
    "stop_reason": "停止继续检索的原因"
  }
}
```

硬规则：

- required 槽位必须至少有一个 `selected_refs`，或者明确填写 `gap_reason`；
- `wave` 只能为 1—4；
- `target_candidates` 为 1—12；
- `material_kind=formal_card` 的 `material_id` 必须出现在顶层 `library_usage.formal_card_ids`；
- `dna_record / dna_component` 必须出现在 `library_usage.dna_candidate_ids`；
- component 级引用必须保留 `record_id`，不得只有孤立 component_id；
- `source_concentration_risks` 用于记录核心组件过度集中到同一来源书；
- `compatibility_checks` 只记录创造层的适配判断，不反向修改来源书；
- `complete / partial` 必须提供非空 `stop_reason`，说明为何停止继续检索。

`library_usage.dna_candidate_ids` 在 V1.1 中既可保存记录 ID，也可保存被实际采用的 component ID；其完整来源链保存在 `material_dispatch.slots[].selected_refs`。


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


## V1.2 附属规划产物

V1.2 不把 Top10/3本前20章的全部结构证据和前100章倒推脊柱硬塞进主 plan JSON。保存完整开书包时，推荐同目录额外保存：

```text
<plan-package>/
├─ plan.json
├─ market_benchmark.json
├─ climax_backplan.json
└─ deep_dive/
   ├─ <sample_id>_chapter_structure_1_20.jsonl
   └─ ...
```

主 `plan.json` 继续使用现有 creation-plan 契约，并可额外加入不会破坏旧 validator 的引用字段：

```json
{
  "v12_artifacts": {
    "market_benchmark": {
      "benchmark_id": "MK:...",
      "path": "market_benchmark.json",
      "status": "complete"
    },
    "climax_backplan": {
      "backplan_id": "BP:...",
      "path": "climax_backplan.json",
      "status": "complete"
    }
  }
}
```

### market_benchmark.json

正式字段与完成门见 `market-benchmark.md`。机器校验：

```powershell
python -X utf8 scripts/validate_v12_artifacts.py benchmark market_benchmark.json
```

### climax_backplan.json

正式字段与完成门见 `climax-backplanning.md`。机器校验：

```powershell
python -X utf8 scripts/validate_v12_artifacts.py climax climax_backplan.json
```

这两个附属包属于创造项目证据与规划，不得写回共享拆书库的来源 `per_book`。
