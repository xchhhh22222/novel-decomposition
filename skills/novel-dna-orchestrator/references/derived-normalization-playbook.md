# Derived Normalization Playbook V1.6.2

用于把 V1.6 已存在的 supplemental derived outputs 迁移到 V1.6.1 canonical contract。

这不是重新拆书任务。

## 1. 允许修改

只允许修改：

- 五类受控 derived files；
- 对应 manifest 的 derived view 名称、records、validator 状态；
- 批次 source_routes 中 deprecated derived view 名称；
- 批次 totals / normalization report；
- 必要 QA 摘要中的旧 validator 描述。

不允许修改：

- 01—09 parent per_book 的事实内容；
- 原始 TXT；
- 旧 cross-book cluster；
- active 状态；
- BOOK_001—既有 canonical 主书。

## 2. 五类受控 view

- ability_assets
- dungeon_rule_assets
- relationship_engine_assets
- charismatic_antagonist_assets
- combat_expression_assets

必须先读取 `derived-material-contract.md`。

## 3. Normalization 顺序

```text
冻结原 branch HEAD
→ inventory 五类 derived 文件
→ 保存 before counts / record IDs / evidence refs
→ source_routes 规范化
→ 一类 view 一类 view 修复
→ manifests 对账
→ batch totals 重算
→ validate_source_routes.py
→ validate_derived_materials.py
→ parent specialist validators 回归
→ diff 审计
→ normalization report
→ commit/push
```

## 4. 不得重新分析

优先来源：

1. 当前 derived record；
2. 同书对应 parent per_book；
3. 同书 QA；
4. 当前 manifest / batch metadata。

只有 canonical 必填字段无法从以上材料恢复时，才允许最小化回查源文，并记录：

```text
NORMALIZATION_SOURCE_EVIDENCE_REQUIRED
```

不得借 normalization 机会重新扩写、重拆、增加新的资产。

## 5. ID 与旧 ID

新 ID：

```text
DA:<VIEW>:<BOOK_ID>:<NNN>
```

按旧记录顺序稳定编号。

若旧记录已有 record_id / asset_id：

- 新值写入 `record_id`；
- 旧值写入 `legacy_record_id`；
- 不因改名改变资产顺序。

## 6. 字段映射

仅做确定性的 alias migration。

### ability

- asset_id → legacy_record_id
- ability_name → name_in_book
- core → ability_core

缺少 appeal_hook / immediate_fantasy 等字段时，只能从当前已有记录或 parent/QA 中迁移现成信息；否则 UNKNOWN。

### relationship

禁止：
- conflicting_information
- conflicting_information_boundary

必须拆为：
- conflicting_interest
- information_boundary

若旧字段混合两种语义且无法无损拆分，对无法确定的一侧写 UNKNOWN。

### antagonist

- long_term_tension_with_protagonist → long_term_tension（仅在语义完全等价时）
- boundary_and_failure_story_potential 不允许机械复制到两个字段；必须基于已有文本拆分 boundary / failure_continuation，无法拆分则 UNKNOWN。
- failure_continuity_placeholder 删除；真实内容迁入 failure_continuation，否则 UNKNOWN。

### combat

旧 collection 中：
- 双层 assets 数组先展平；
- label → asset_name；
- asset_id → legacy_record_id。

description 不是 16 个 canonical 战斗字段的万能来源。只把其中明确表达的事实迁移到相应字段，其余 UNKNOWN。

## 7. Evidence

旧：

```text
ch16-57
BOOK_011:CHAPTER:0001-1002
```

不能直接保留为 evidence_ref。

处理：

- 范围写进 chapter_span；
- evidence_refs 改为当前 derived/per_book/QA 已经实际定位的精确章节；
- 如果现有文件只有宽范围而无精确节点，必须最小化回查证据，不能凭空选章节。

## 8. 计数

每个 view 修复后同时更新：

- canonical 文件实际记录数；
- manifest.outputs.derived_views[].records；
- combat_expression 顶层 asset_count；
- batch summary totals。

三者必须一致。

## 9. 验证

必须运行：

```bash
python skills/novel-dna-orchestrator/scripts/validate_source_routes.py <source_routes.jsonl>

python skills/novel-dna-orchestrator/scripts/validate_derived_materials.py \
  --root <nova-material-library-root> \
  --books BOOK_010,BOOK_011
```

然后回归运行所有被修改书的 parent specialist validators。

成功时才能报告：

```text
SOURCE_ROUTING_GATE_V1_6_1 = PASS
DERIVED_MATERIAL_CONTRACT_V1_6_1 = PASS
PARENT_SPECIALIST_REGRESSION = PASS
```

## 10. Normalization report

每个迁移批次生成一份报告，至少包含：

- input branch / input HEAD；
- output branch / output HEAD；
- books；
- files changed；
- record ID mapping；
- alias fields removed；
- evidence refs normalized；
- source evidence lookups；
- before/after counts；
- manifest corrections；
- semantic meaning changes：必须为 NONE；若非 NONE，任务不再属于纯 normalization；
- validators；
- remaining HOLD / UNKNOWN。

## 11. 聚类门

Normalization 完成后仍然：

- 不自动 active；
- 不立即 append 旧 cluster；
- 不覆盖历史 run。

只有人工审核通过后，才允许开启受影响专项的 full recluster。


## 12. V1.6.2 批次一致性收尾

Normalization 结束后不能只停在 `validate_derived_materials.py=PASS`。

还必须运行：

```bash
python scripts/validate_supplemental_batch.py \
  --root <nova-material-library-root> \
  --batch-dir batch/<BATCH_ID> \
  --books <BOOK_ID,...>
```

并处理三个结果：

1. ROUTE_OUTPUT_CONSISTENCY_GATE
   - source_route.derived_views 与真实 derived 文件/明确 gap 对账；
   - 历史漏 route 只有在原任务确实授权时才允许 metadata reconciliation。

2. COMPLETION_STATUS_CONSISTENCY_GATE
   - 任一 controlled derived record HOLD → manifest.status 必须 WITH_HOLDS；
   - batch-status 与 manifest.status 完全一致。

3. CLUSTER_ELIGIBILITY_GATE
   - PASS record 可聚类；
   - HOLD record inventory-only；
   - 某 view records>0 且 eligible=0 → full_recluster_ready=false。

Normalization report 必须保存该 gate 输出或其路径。
