# 来源角色与拆解路由 V1.6.2

本文件只定义“中控如何决定一本来源书要拆什么”，不替代 01—09 specialist 自己的 guidance / schema / QA。

## 1. 两种 extraction_mode

### FULL_DNA

用于值得进入都市高武完整主库的来源书。

必须运行：
- 01 chapter_emotion
- 02 golden_finger
- 03 worldbuilding
- 04 cultivation_system
- 05 character_function
- 06 plotline
- 07 opening
- 08 arc_structure
- 09 plot_mechanism

并继续派生 heroine_character / long_arc_villain / combat expression 等现有视图。

完成状态仍按完整单书门判断。

### SUPPLEMENTAL_MATERIAL

用于“为了补某类素材而引入”的来源书。

特点：
- 只运行明确授权的 target_specialties；
- 没被授权的专项必须显式写入 excluded_specialties；
- 不因为没有跑满 01—09 而判失败；
- 但 target_specialties 的 recall、证据、QA 必须完整；
- 所有输出仍为 candidate；
- 不允许把补充来源直接晋升 active；
- 不允许把新书直接 append 到旧 cluster。

SUPPLEMENTAL 的完成含义是：

“本次授权专项已完整覆盖并通过对应门”，

不是：

“整本书已完成九维 DNA”。

## 2. 路由先于拆解

拿到新 TXT 后，第一步只能做 ROUTING。

顺序：

```text
列出来源
→ 去重
→ 分配 BOOK_ID
→ 判断 source_role
→ 判断 extraction_mode
→ 说明 purpose
→ 选择 target_specialties
→ 选择 derived_views
→ 明确 excluded_specialties
→ 给出 chapter_scope
→ 用户确认
→ 才允许正式拆解
```

未经用户确认 routing matrix，不写素材库。

## 3. 路由记录

每本来源至少一条 source_route：

```json
{
  "record_type": "source_route",
  "schema_version": 1,
  "book_id": "BOOK_010",
  "source_file": "example.txt",
  "source_role": "supplemental_material",
  "extraction_mode": "SUPPLEMENTAL_MATERIAL",
  "purpose": ["ability_material"],
  "target_specialties": [
    "golden_finger",
    "cultivation_system",
    "plot_mechanism"
  ],
  "derived_views": ["ability_assets"],
  "excluded_specialties": [
    "chapter_emotion",
    "worldbuilding",
    "character_function",
    "plotline",
    "opening",
    "arc_structure"
  ],
  "chapter_scope": "FULL_SOURCE_SCAN",
  "full_book_dna": false,
  "known_gaps": []
}
```

FULL_DNA：
- `source_role = primary_full_dna`
- `extraction_mode = FULL_DNA`
- `full_book_dna = true`
- target_specialties 必须覆盖全部九专项
- excluded_specialties 必须为空

SUPPLEMENTAL_MATERIAL：
- `source_role = supplemental_material`
- `full_book_dna = false`
- target_specialties 必须是九专项的非空真子集
- target_specialties 与 excluded_specialties 不得重叠
- 二者并集必须完整覆盖九专项

## 4. SUPPLEMENTAL 的“全文扫描”含义

SUPPLEMENTAL 不等于只抽几章。

若 chapter_scope 为 FULL_SOURCE_SCAN：

- 必须扫描授权范围全部正文，确保目标专项 recall；
- 只对目标专项写正式输出；
- 必要时回读目标实例前后文；
- 情绪只在目标专项需要兑现/首次展示/关系转折证据时做局部 overlay；
- 不要求生成每章 canonical emotion。

例如“能力素材”来源有 200 章：

正确：
```text
扫描 1—200 章所有能力出现/升级/组合
→ 建 ability inventory
→ 对关键实例回读证据窗口
→ 输出 02/04/09 与 derived ability assets
```

错误：
```text
只读前30章
→ 宣称全书能力素材完整
```

## 5. 与旧主库的关系

BOOK_001—BOOK_009 的完整 canonical 数据保持只读。

新增 supplemental source：
- 继续使用 BOOK_010、BOOK_011...，不另建 SUPP_ 前缀，避免破坏现有 validator/schema；
- 用 source_role / extraction_mode 区分身份；
- 不重写旧书；
- 不修改旧的 cross-book run。

## 6. 聚类边界

新来源加入后，只对“被新来源实际覆盖的专项”开启新的 full recluster run。

例如：
- 新能力书 → 02 / 04 combat / 09（若授权）
- 女主关系书 → 05 / heroine / relationship / 06 / 08（若授权）
- 副本规则书 → 03 / 06 / 08 / 09（若授权）

但每个被影响专项都必须重新：

```text
per_book/gap completeness
→ nearest_neighbors
→ KEEP_SEPARATE
→ clusters
→ QA
→ handoff
→ lineage
```

禁止把新记录直接塞进旧 cluster。

旧 run 保持历史快照。

## 7. 完成状态

FULL_DNA 可使用原完整单书状态。

SUPPLEMENTAL 使用：

- `COMPLETE_SUPPLEMENTAL_SOURCE`
- `COMPLETE_SUPPLEMENTAL_SOURCE_WITH_HOLDS`
- `BLOCKED`

不能因为未运行 excluded_specialties 而降级。

但任何 target_specialty 缺输出、缺 evidence、validator FAIL 或关键未处理 HOLD，都必须反映在最终状态中。


## 8. Derived Material V1.6.1 附加门

如果 source_route.derived_views 包含以下任一：

- ability_assets
- dungeon_rule_assets
- relationship_engine_assets
- charismatic_antagonist_assets
- combat_expression_assets

则该来源即使父专项 validator 已 PASS，也不能直接进入聚类。

必须继续：

```text
derived-material-contract.md
→ canonical normalization
→ validate_derived_materials.py
→ DERIVED_MATERIAL_CONTRACT_V1_6_1=PASS
```

新批次必须直接产出 canonical V1.6.1。旧 V1.6 批次允许做一次纯 normalization；不能为了通过 schema 重写原始含义。


## 9. V1.6.2 路由输出闭环

`source_route.derived_views` 不再只是“计划字段”，而是 derived output 的授权白名单。

批次完成时必须检查：

```text
route declared views
↔ actual */derived/*.json|*.jsonl
↔ manifest derived declarations
```

允许：
- route view 有实际文件；
- route view 因证据不足形成 manifest 明确 0-record checked gap。

禁止：
- 产生未出现在 route 的 derived 文件；
- route 声明了 view，但既没有文件也没有 checked gap；
- 用“profile 默认会生成”替代 source_route 的显式授权。

对历史 V1.6/V1.6.1 批次，如果能从原批准任务证明某 derived view 确实被授权但 route 漏记，可以只补 metadata；必须在 reconciliation 报告中说明，不改素材语义。
