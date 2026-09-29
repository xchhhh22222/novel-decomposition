# Derived Material Contract V1.6.3

本契约只规范 V1.6 新增的 5 类补充素材派生视图，不改 01—09 specialist 的 canonical schema。

覆盖：

1. ability_assets
2. dungeon_rule_assets
3. relationship_engine_assets
4. charismatic_antagonist_assets
5. combat_expression_assets

目标：消除字段漂移、ID 漂移、证据引用漂移、嵌套数组和批次计数不一致，使这些派生素材可以安全进入后续跨书聚类。

---

## 1. 总原则

所有 V1.6.1 derived records：

- `status` 固定为 `candidate`；
- `schema_version` 固定为 `2`；
- 必须有唯一 `record_id`；
- 必须有 `book_id` 与 `view`；
- 必须有非空 `evidence_refs`；
- `evidence_refs` 只允许精确章节引用，不允许区间；
- 证据区间另写 `chapter_span`；
- 必须有 `unknowns`、`confidence`、`qa_status`；
- `unknowns` 非空时，`confidence` 不得为 `HIGH`；
- 不允许未声明的临时字段名；
- 不允许同义字段在不同书里各自出现。

canonical evidence ref：

```text
BOOK_010:CHAPTER:0003
BOOK_014:CHAPTER:2021
```

禁止：

```text
ch16-57
ch222
BOOK_011:CHAPTER:0001-1002
BOOK_011:CHAPTER:16-57
```

章节范围只允许放在：

```json
"chapter_span": "16-57"
```

---

## 2. Record ID

统一使用：

```text
DA:<VIEW>:<BOOK_ID>:<NNN>
```

其中 VIEW：

- ABILITY
- DUNGEON
- RELATIONSHIP
- ANTAGONIST
- COMBAT

例如：

```text
DA:ABILITY:BOOK_015:001
DA:DUNGEON:BOOK_011:003
DA:RELATIONSHIP:BOOK_016:002
DA:ANTAGONIST:BOOK_013:004
DA:COMBAT:BOOK_014:008
```

编号规则：

- 同一本书、同一 view 内从 001 顺序递增；
- 按现有记录稳定顺序，不因名称排序重新编号；
- normalization 时如果旧 ID 改写，使用可选 `legacy_record_id` 保留旧值；
- 不允许两个记录共用同一 `record_id`。

---

## 3. 公共字段

所有 5 类记录都必须包含：

```json
{
  "record_type": "derived_asset",
  "schema_version": 2,
  "record_id": "DA:ABILITY:BOOK_015:001",
  "status": "candidate",
  "book_id": "BOOK_015",
  "view": "ability_assets",
  "evidence_refs": ["BOOK_015:CHAPTER:0001"],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "PASS"
}
```

允许的公共可选字段：

- `legacy_record_id`
- `notes`

`confidence` 只允许：

- HIGH
- MEDIUM
- LOW

`qa_status` 只允许：

- PASS
- HOLD

如果关键字段无法从现有证据确认：

- 字段仍必须存在；
- 写 `UNKNOWN`；
- 同时在 `unknowns` 中说明原因；
- 不允许为了通过 validator 编造值。

---

## 4. ability_assets

文件：

```text
02_金手指/derived/ability_assets.jsonl
```

每行一条 JSON record。

除公共字段外，必须恰好包含：

- `name_in_book`
- `ability_core`
- `trigger`
- `input`
- `operation`
- `output`
- `limit`
- `cost`
- `growth`
- `first_showcase`
- `appeal_hook`
- `immediate_fantasy`
- `combat_value`
- `social_value`
- `plot_generation`
- `combination_interfaces`
- `counterplay`
- `fatigue_risk`

禁止别名：

- `asset_id`
- `ability_name`
- `core`

必须改为：

- `record_id`
- `name_in_book`
- `ability_core`

---

## 5. dungeon_rule_assets

文件：

```text
03_世界观/derived/dungeon_rule_assets.jsonl
```

每行一条 JSON record。

除公共字段外，必须包含：

- `dungeon_name`
- `chapter_span`
- `entry_condition`
- `surface_rules`
- `hidden_rules`
- `rule_reliability`
- `victory_condition`
- `failure_condition`
- `death_or_penalty`
- `resource_pressure`
- `information_asymmetry`
- `roles`
- `team_structure`
- `conflict_structure`
- `loophole`
- `discovery_process`
- `escalation`
- `turning_point`
- `exit_condition`
- `reward`
- `mainline_connection`
- `reuse_pattern`
- `fatigue_risk`

允许可选：

- `dungeon_type`
- `gate_no`

`chapter_span` 可以记录区间，但 `evidence_refs` 必须拆成精确章节。

---

## 6. relationship_engine_assets

文件：

```text
05_人物功能与标签/derived/relationship_engine_assets.jsonl
```

每行一条 JSON record。

除公共字段外，必须包含：

- `engine_name`
- `sides`
- `engine_type`
- `binding_reason`
- `first_exchange`
- `shared_interest`
- `conflicting_interest`
- `information_boundary`
- `active_choices`
- `progression_states`
- `break_condition`
- `reconciliation_condition`
- `replaceability`
- `protagonist_interface`

`sides` 必须为至少两个非空字符串组成的数组。

禁止：

- `conflicting_information`
- `conflicting_information_boundary`

这两个旧临时字段必须在 normalization 时回填到：

- `conflicting_interest`
- `information_boundary`

如果无法无损拆分，则对应字段写 `UNKNOWN` 并记录 `unknowns`。

---

## 7. charismatic_antagonist_assets

文件：

```text
05_人物功能与标签/derived/charismatic_antagonist_assets.jsonl
```

每行一条 JSON record。

除公共字段外，必须包含：

- `person_id`
- `name_in_book`
- `role_kind`
- `goal`
- `values`
- `resource_domain`
- `faction`
- `competence`
- `threat_source`
- `charisma_source`
- `reader_respect_source`
- `mirror_to_protagonist`
- `cooperation_possibility`
- `hostility_reason`
- `boundary`
- `scene_stealing_pattern`
- `escalation_path`
- `defeat_or_exit_condition`
- `failure_continuation`
- `reader_memory_why`
- `long_term_tension`

禁止别名：

- `long_term_tension_with_protagonist`
- `boundary_and_failure_story_potential`
- `failure_continuity_placeholder`

这些旧字段不能继续存在。

如果一个旧字段混合了两个概念，只允许基于现有文本拆分；无法可靠拆分时，对无法确认的目标字段写 `UNKNOWN`。

---

## 8. combat_expression_assets

文件继续使用：

```text
04_修炼体系/derived/combat_expression_assets.json
```

canonical 顶层格式：

```json
{
  "schema_version": 2,
  "record_type": "derived_asset_collection",
  "book_id": "BOOK_014",
  "view": "combat_expression_assets",
  "asset_count": 8,
  "assets": [
    {
      "record_type": "derived_asset",
      "schema_version": 2,
      "record_id": "DA:COMBAT:BOOK_014:001",
      "status": "candidate",
      "book_id": "BOOK_014",
      "view": "combat_expression_assets",
      "asset_name": "规则战与机制杀",
      "function_slot": "rule_counter",
      "trigger": "...",
      "input": "...",
      "operation": "...",
      "range": "...",
      "action_pattern": "...",
      "output": "...",
      "cost": "...",
      "limit": "...",
      "counterplay": "...",
      "visual_expression": "...",
      "combat_role": "...",
      "combination_interface": "...",
      "compatible_system": "...",
      "user_archetype": "...",
      "evidence_refs": ["BOOK_014:CHAPTER:0074"],
      "unknowns": [],
      "confidence": "MEDIUM",
      "qa_status": "PASS"
    }
  ]
}
```

`assets` 必须是**一维数组**。

禁止：

```json
"assets": [[{...}, {...}]]
```

每条 combat asset 必须包含：

- `asset_name`
- `function_slot`
- `trigger`
- `input`
- `operation`
- `range`
- `action_pattern`
- `output`
- `cost`
- `limit`
- `counterplay`
- `visual_expression`
- `combat_role`
- `combination_interface`
- `compatible_system`
- `user_archetype`

旧字段：

- `asset_id`
- `label`
- `description`

不得作为 V1.6.1 canonical 输出继续存在。

normalize 时：
- `asset_id` → `legacy_record_id`（若需要）
- `label` → `asset_name`
- `description` 只能用于回填已有事实；
- 不能仅靠一句 description 猜出 cost / limit / counterplay 等字段；
- 无法确认的字段写 `UNKNOWN`。

顶层 `asset_count` 必须等于 `len(assets)`。

---

## 9. 允许的字段类型

描述字段可以是：

- 非空字符串；
- 非空字符串数组。

禁止：
- null；
- 空字符串；
- 空数组；
- 未声明对象；
- 用不同字段名表达同一概念。

特殊字段：
- `record_id / book_id / view / status / confidence / qa_status` 必须是字符串；
- `schema_version` 必须是整数 2；
- `evidence_refs / unknowns / sides` 必须是字符串数组。

---

## 10. Manifest 计数

如果某个 view 出现在：

```text
manifest.json
→ outputs.derived_views[]
```

则：

```text
records
```

必须与实际 canonical 文件记录数一致。

例如 combat_expression：

```text
manifest records
= top-level asset_count
= len(assets)
```

不允许出现：

```text
实际 8 条
manifest 24
用户报告 19
batch 总计按 1 条统计
```

---

## 11. Normalization 原则

对已有 V1.6 输出做 V1.6.1 normalization 时：

允许：
- 字段重命名；
- ID 重编号；
- 展平错误嵌套数组；
- 把已有信息移动到 canonical 字段；
- 把区间证据改成实际已存在的精确章节证据；
- 修正 manifest / batch count；
- 增加 UNKNOWN / unknowns；
- 增加 qa_status / confidence；
- 增加 legacy_record_id。

禁止：
- 重新拆书；
- 为了填满字段重新创作事实；
- 把模型推断写成源文事实；
- 删除原有证据；
- 用一个宽泛章节区间冒充精确 evidence；
- 因 schema 修复而改变原有 material meaning。

如果仅靠现有 derived/per_book/QA 无法完成规范化：

```text
NORMALIZATION_SOURCE_EVIDENCE_REQUIRED
```

只对缺失字段做最小证据回查，不重跑整本书。

---

## 12. 机器校验

运行：

```bash
python scripts/core/validate_derived_materials.py --root <material-library-root> --books BOOK_010,BOOK_011
```

总控 Skill 中对应命令：

```bash
python scripts/validate_derived_materials.py --root <material-library-root> --books BOOK_010,BOOK_011
```

必须同时通过：

- record schema
- field name whitelist
- record_id
- evidence ref
- confidence/unknown
- nested array
- duplicate record ID
- manifest count consistency

通过后才能报告：

```text
DERIVED_SCHEMA_VALIDATION = PASS
```

在 V1.6.1 以后，不再允许仅用“人工 DERIVED_CONTRACT_CHECK=PASS”替代 dedicated validator。

## V1.6.3 语义加固：UNKNOWN 与 Combat PASS

### 1. UNKNOWN 必须是字面值

当一个 canonical 字段无法由现有证据确认时，字段值必须严格为：

```text
UNKNOWN
```

禁止把解释混进字段值：

```text
UNKNOWN——原文未展示……
UNKNOWN（未说明）
未知
不适用/未知
```

原因写进 `unknowns[]`，并尽量使用字段名前缀：

```json
"cost": "UNKNOWN",
"unknowns": ["cost：原文未给出明确消耗"]
```

`unknowns[]` 只保存当前素材尚未确认的事实，不保存证据迁移日志。诸如 `EVIDENCE_CORRECTION / old_ref / new_ref` 必须放进 backfill/refinement report。

### 2. 不得从“没写”推导“没有”

以下推理禁止：

```text
原文未展示代价 → cost = 无
原文未展示反制 → counterplay = 无
原文未说明限制 → limit = 无限制
```

只有正文存在积极证据支持“无需消耗 / 自动无代价 / 不可反制 / 无限制”等结论，才允许写为已知值；否则必须 `UNKNOWN`。

### 3. Combat PASS 最低语义门

`combat_expression_assets` 一条记录只有满足以下条件才允许 `qa_status=PASS`：

- 以下核心字段全部不是 `UNKNOWN`：
  - asset_name
  - function_slot
  - trigger
  - operation
  - action_pattern
  - output
  - combat_role
  - visual_expression
- `cost / limit / counterplay` 三个约束字段中至少一个有正文支持的真实信息；三者全为 `UNKNOWN` 时必须 HOLD；
- `input / range / combination_interface / compatible_system / user_archetype` 可以 UNKNOWN；
- `unknowns` 非空时 `confidence` 不得 HIGH。

PASS 的含义是“已足以进行跨书机制比较”，不是“所有字段 100% 完整”。

### 4. 机器门

当批次包含 combat_expression_assets 时，除了 `validate_derived_materials.py`，还必须运行：

```bash
python scripts/validate_combat_semantics.py --root <material-library-root> --books <BOOK_ID,...>
```

必须得到：

```text
COMBAT_SEMANTIC_GATE_V1_6_3 = PASS
```

否则 combat PASS record 不得进入聚类。
