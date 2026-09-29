# Combat Evidence Backfill & Semantic Refinement V1.6.3

用于修复已经存在、但因为证据不足而 HOLD 的 `combat_expression_assets`。

这不是重新拆书，也不是扩充资产数量。

---

## 1. 两阶段模型

必须把以下两件事分开：

```text
A. TARGETED_DERIVED_EVIDENCE_BACKFILL
   只找证据、回填已有 record

B. COMBAT_SEMANTIC_REFINEMENT
   统一 UNKNOWN、重判 PASS/HOLD、修 batch totals
```

不能把“找到更多正文”直接等同于 PASS。

Backfill 后必须再跑 Semantic Refinement。

---

## 2. Backfill 边界

只允许：

- 保留现有 record_id / asset identity / record order；
- 读取现有 evidence_refs；
- 必要时读取 ±2 邻章；
- 再不足时用现有 asset_name / action_pattern / 角色名 / 能力名做定向全文字符串检索；
- 最多选少量最相关章节做语义核查；
- 回填已有 canonical 字段；
- 修正错误 evidence ref，并把修正历史写入 report。

禁止：

- 重新全文语义拆书；
- 新增 combat asset；
- 合并/拆分现有 asset；
- 为了 PASS 编 cost/limit/counterplay；
- 把“未见”解释成“没有”。

没有 PASS 数量 KPI。57 条审完可能仍有 HOLD，这是正常结果。

---

## 3. Semantic Refinement

Backfill 完成后逐条重判。

### UNKNOWN canonicalization

业务字段未知时必须严格为：

```text
UNKNOWN
```

解释放：

```text
unknowns:
- "cost：原文未给出明确消耗"
```

禁止：

- UNKNOWN——原因
- UNKNOWN（原因）
- 未知
- 不适用/未知

### unknowns 的用途

`unknowns[]` 只描述**当前素材仍未知的事实**。

禁止存：

- EVIDENCE_CORRECTION
- old_ref / new_ref
- agent execution log
- lookup level log

这些属于 backfill/refinement report。

### PASS 最低条件

核心字段全部已知：

- asset_name
- function_slot
- trigger
- operation
- action_pattern
- output
- combat_role
- visual_expression

并且：

```text
cost / limit / counterplay
至少 1 项有正文支持
```

三项全 UNKNOWN → HOLD。

辅助字段允许 UNKNOWN：

- input
- range
- combination_interface
- compatible_system
- user_archetype

只要核心机制足以跨书比较。

---

## 4. “无”需要积极证据

禁止：

```text
原文没写代价
→ cost = 无
```

正确：

```text
cost = UNKNOWN
unknowns += "cost：原文未展示明确消耗"
```

只有正文明确支持“不消耗 / 自动无代价 / 不受限制 / 不可被反制”等结论时，才能把“无”写成已知事实。

---

## 5. Gate 顺序

存在 combat backfill/refinement 时：

```text
validate_derived_materials.py
→ validate_combat_semantics.py
→ validate_supplemental_batch.py
→ 人工审核
→ 才允许 recluster
```

必须分别得到：

```text
DERIVED_MATERIAL_CONTRACT_V1_6_1 = PASS
COMBAT_SEMANTIC_GATE_V1_6_3 = PASS
SUPPLEMENTAL_BATCH_CONSISTENCY_V1_6_3 = PASS
```

---

## 6. Batch totals

Semantic Refinement 后必须从真实 records 重算：

- derived_totals
- derived_hold_records
- 每书 manifest.status
- batch-status.books[]

不得沿用 backfill 前旧统计。

---

## 7. 报告避免 Git SHA 自引用

不要让报告 JSON 声称自己包含“最终包含自身的 commit SHA”，否则修改 SHA 会产生新的 commit，形成递归。

推荐：

```json
{
  "input_head": "...",
  "report_generated_from_head": "<写报告前最后一个业务 commit>",
  "final_branch_head": "OMITTED_SELF_REFERENCE"
}
```

真实最终 remote HEAD 放在用户可见执行结果中，不靠 report 自引用。

---

## 8. 审核输出

至少报告：

- records_reviewed
- before PASS/HOLD
- after PASS/HOLD
- downgraded_record_ids
- unknown_value_normalizations
- absence_inference_corrections
- evidence_refs_added / corrected
- remaining UNKNOWN fields
- controlled HOLD total
- three validator/gate results
- record count / ID / order integrity
- non-combat derived unchanged
- FULL_RECLUSTER = NOT_RUN
- ACTIVE_PROMOTION = NOT_RUN

人工审核通过前，即使 `full_recluster_ready=true` 也不得自动开始聚类。
