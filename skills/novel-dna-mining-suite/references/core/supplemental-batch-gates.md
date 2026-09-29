# Supplemental Batch Gates V1.6.3

V1.6.2 在 V1.6.1 derived schema gate 之后新增三个批次级硬门。目的不是扩大拆解范围，而是阻止“格式合法但状态/路由/聚类资格不一致”的数据进入横向聚类。

---

## 1. ROUTE_OUTPUT_CONSISTENCY_GATE

`source_routes.jsonl[].derived_views` 是 derived output 的授权白名单。

对每本 supplemental source：

- 实际存在的 `*/derived/*.json|*.jsonl` 视图必须出现在 source_route.derived_views；
- route 中声明的 derived view 必须存在实际文件，或存在 manifest 明确的 0-record gap；
- manifest 声明的 derived view 必须与实际文件一致；
- 禁止“先生成，后默认认为已授权”；
- 历史 V1.6 输出如果确实来自已批准任务，但 route 漏记，允许做 metadata reconciliation：补 route，不改素材内容，并记录原因；
- 如果不能证明输出曾被用户/任务授权，不得通过补 route 洗白，必须删除未授权输出或人工复核。

因此：

```text
actual derived output ⊆ route-authorized derived_views
routed derived view → actual file OR explicit checked gap
```

---

## 2. COMPLETION_STATUS_CONSISTENCY_GATE

单书 manifest、batch-status 和 derived record HOLD 必须一致。

规则：

- 任一 V1.6.1 controlled derived record 的 `qa_status=HOLD`：
  - manifest.status 必须是 `COMPLETE_SUPPLEMENTAL_SOURCE_WITH_HOLDS`；
- manifest.status 与 batch-status.books[BOOK_ID] 必须完全一致；
- `COMPLETE_SUPPLEMENTAL_SOURCE` 不允许掩盖 controlled derived HOLD；
- WITH_HOLDS 可以来自 controlled derived、parent specialty 或其它显式已知 HOLD；
- BLOCKED 不得被 batch-status 写成 COMPLETE。

本门只校验状态一致性，不把 HOLD 自动升级为 PASS。

---

## 3. CLUSTER_ELIGIBILITY_GATE

五类 controlled derived views：

- ability_assets
- dungeon_rule_assets
- relationship_engine_assets
- charismatic_antagonist_assets
- combat_expression_assets

聚类资格只由 record 自身 QA 决定：

```text
qa_status = PASS
→ eligible for nearest_neighbor / KEEP_SEPARATE / cluster

qa_status = HOLD
→ inventory-only
→ 禁止进入 nearest_neighbor / cluster 输入
```

不允许：
- 因 schema validator PASS 就把 HOLD 记录送进聚类；
- 把 HOLD 临时改 PASS 只是为了完成聚类；
- 用同 view 的 PASS 记录替 HOLD 记录“代表”它。

### View readiness

- `eligible > 0, held = 0` → READY
- `eligible > 0, held > 0` → READY_PASS_ONLY；只聚类 eligible IDs
- `eligible = 0, records > 0` → BLOCKED_ZERO_ELIGIBLE
- `records = 0 + explicit checked gap` → GAP，不作为聚类失败

如果任一当前需要重聚类的 controlled view 是 `BLOCKED_ZERO_ELIGIBLE`，则整个 supplemental full recluster 不得宣称 ready。可以先处理其它无依赖专项，但不得宣称完整批次 recluster 完成。

---

## 4. 机器入口

Suite：

```bash
python scripts/core/validate_supplemental_batch.py \
  --root <nova-material-library-root> \
  --batch-dir batch/<BATCH_ID> \
  --books BOOK_010,BOOK_011
```

Orchestrator：

```bash
python scripts/validate_supplemental_batch.py \
  --root <nova-material-library-root> \
  --batch-dir batch/<BATCH_ID> \
  --books BOOK_010,BOOK_011
```

输出三个 gate：

- ROUTE_OUTPUT_CONSISTENCY_GATE
- COMPLETION_STATUS_CONSISTENCY_GATE
- CLUSTER_ELIGIBILITY_GATE

以及：

```text
full_recluster_ready = true | false
```

注意：validator exit 0 表示三类合同可解释且无一致性错误；如果某个 view 全部 HOLD，validator 可以结构性 PASS，但 `full_recluster_ready=false`。

---

## 5. V1.6.1 历史批次修正顺序

```text
V1.6.1 normalization
→ validate_derived_materials.py
→ route/output reconciliation
→ manifest/batch status reconciliation
→ validate_supplemental_batch.py
→ targeted evidence backfill（仅对需要提升的 HOLD）
→ re-run both validators
→ 人工审核
→ full recluster
```

不允许把 route/status 修正和 evidence backfill 混成一次“重新拆书”。

---

## 6. Evidence backfill 边界

当某 controlled view 因大量 UNKNOWN 导致 HOLD 时，可做：

```text
TARGETED_DERIVED_EVIDENCE_BACKFILL
```

只能：
- 针对现有 record；
- 回读 record 已有 evidence_refs 与必要最小邻近窗口；
- 回填 canonical 字段；
- 保留 record_id；
- 不新增资产；
- 不改变原 material identity；
- 无证据字段继续 UNKNOWN/HOLD。

完成后：
- parent per_book 不应改变；
- 重新运行 derived validator；
- 重新运行 supplemental batch validator；
- 只有 qa_status 真正达到 PASS 的 record 才获得聚类资格。

---

## 7. 聚类输入必须可审计

任何后续 nearest_neighbor/cluster run 必须保存：

- source batch id；
- source branch/head；
- validator output；
- 每个 controlled view 的 eligible_record_ids；
- held_record_ids；
- excluded HOLD 数；
- route-authorized books/views；
- recluster run id。

禁止只写“已过滤 HOLD”而不保存具体 ID 列表。


## 8. V1.6.3 BATCH_SUMMARY_CONSISTENCY_GATE

V1.6.2 已能对账 route/status/eligibility，但第一次真实 backfill 暴露了一个新问题：

```text
supplemental-consistency 中真实 HOLD = 25
batch-status.derived_hold_records 仍残留旧值 82
```

因此 V1.6.3 增加批次汇总硬门。

`batch-status.json` 必须满足：

- `derived_hold_records` 为整数；
- `derived_hold_records` 等于五类 controlled derived records 的真实 HOLD 总数；
- `derived_totals.<view>` 必须等于该 view 的真实 records 数；
- 任一 stale total 都使 batch consistency FAIL；
- 不允许手工复制上一次运行的统计值。

机器输出增加：

```text
BATCH_SUMMARY_CONSISTENCY_GATE = PASS / FAIL
```

并记录：

- declared_hold_records
- actual_hold_records

V1.6.3 的 full_recluster_ready 需要同时满足：

- route/output PASS
- completion status PASS
- batch summary PASS
- cluster eligibility PASS
- 没有 BLOCKED_ZERO_ELIGIBLE view

---

## 9. V1.6.3 Combat Semantic Gate

当批次存在 `combat_expression_assets` 时，schema PASS 不足以代表可聚类。

必须额外运行：

```bash
python scripts/validate_combat_semantics.py \
  --root <material-library-root> \
  --books <BOOK_ID,...>
```

只有：

```text
COMBAT_SEMANTIC_GATE_V1_6_3 = PASS
```

才允许把 `qa_status=PASS` 的 combat record 交给 cluster eligibility。

该门强制：

- UNKNOWN 字段必须严格等于 `UNKNOWN`；
- UNKNOWN 原因进入 `unknowns[]`；
- evidence correction 日志不得污染 `unknowns[]`；
- combat PASS 的核心机制字段必须完整；
- cost/limit/counterplay 至少一个必须有证据；
- “原文没写代价”不得推导成“无代价”。

这一步专门防止“validator PASS，但语义上其实不够 PASS”。
