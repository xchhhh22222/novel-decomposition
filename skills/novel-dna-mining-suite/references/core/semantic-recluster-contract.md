# V1.6.5 跨书语义重聚类可靠性契约

本契约约束所有 FULL_DNA / SUPPLEMENTAL_MATERIAL 的跨书 full recluster。V1.6.5 在 V1.6.4 基础上新增两个核心要求：

1. **禁止把 `actual_operation` 原文完全相同当作语义等价的必要条件**；
2. **historical whole-record → fine-grained unit 的 lineage 必须支持 1→N 映射，不能因为候选多于 1 个就自动 HOLD。**

目标不是“尽量少聚类”，也不是“尽量多聚类”，而是在可追溯证据下尽量发现真正可复用的同机制与变体，给后续写书提供更多可靠参考。

## 1. Retrieval 只负责召回，不负责裁决

禁止把单一 lexical top-2/top-3 当作完整候选空间。

候选集合至少是以下三路并集：

1. lexical retrieval：字符 bigram / token cosine 等只负责召回；
2. controlled-structural blocking：共享受控结构事实、枚举字段、schema-compatible slots；
3. operation/structural blocking：共享输入、处理链、角色接口、权限、目标、输出、因果链、失败边界等运行结构；
4. mechanism-signature blocking：先把 unit 证据抽成结构化 mechanism signature，再按操作链/目标/效果等核心槽位召回不同措辞的疑似等价 pair。

默认 lexical top-k 不低于 8；若专项规模允许，应 exhaustive 扫描全部跨书 schema-compatible pair 的结构 blocking。

同时必须做 expanded-K 审计，例如 K=8 与 K=16/32。扩大 K 新发现大量可接受 support edge 时，RETRIEVAL_RECALL_AUDIT 不得 PASS。

## 2. 关键词只能找“疑似 pair”，不能决定语义等价

关键词、substring normalization、embedding/cosine、字符重合度、题材标签，都只能用于：

- candidate retrieval；
- near-miss / suspicious pair 标记；
- 人读解释。

它们不能直接决定 MERGE/SUBTYPE，也不能直接决定 KEEP_SEPARATE。

任何候选 pair 一旦出现下列任一信号，都必须进入 **paraphrase-equivalence adjudication**：

- controlled_structural retrieval；
- operation_structural retrieval；
- `same_structure`；
- `same_semantic_operation`；
- `partial_semantic_operation`；
- 其它明确的结构近似信号。

不得因为“原句不同”直接淘汰。

## 3. 语义等价必须比较结构化 mechanism signature

每个需要语义裁决的 pair 必须构造并比较可证据化的 `mechanism_signature`。至少包含：

- `actor_or_role`：谁/什么角色在执行；
- `trigger_or_input`：由什么条件、信息、资源或事件触发；
- `operation_chain`：真正发生的操作链；
- `target_or_object`：作用对象；
- `output_or_effect`：产生什么结果、权限、资源、状态变化；
- `constraints_or_boundary`：代价、限制、失败条件、不可替代边界；
- `evidence_refs`：左右双方各自证据。

**允许不同措辞映射到同一个结构化 mechanism signature。**

例如：

- A：先现场验证主角提供的信息，再由有权限的队长开放岗位、任务许可和路线准入；
- B：由先锋队长验证路线判断，再通过编队权限、清场能力和行动许可开放团队入口；

两者原文不同，但都可能抽象为：

`authority_holder → verify information/route → grant operational access/resources`

这类 pair 必须进入语义等价/子型审核，不能因为 raw text 不相同而自动 KEEP_SEPARATE。

## 4. Raw-text equality 只能是“加分证据”，不能是必要条件

每条 MERGE/SUBTYPE 的 `decision_audit` 必须显式满足：

- `retrieval_score_used_for_decision=false`
- `keyword_count_used_for_decision=false`
- `raw_operation_text_equality_required=false`
- `exact_raw_text_match_used_as_required_condition=false`
- `structural_support_independent_of_keyword=true`
- `non_keyword_support_dimensions=[...]`
- `paraphrase_equivalence_review={...}`

`paraphrase_equivalence_review` 至少包含：

- `reviewed=true`
- `method=structured_operation_signature | evidence_grounded_structured_paraphrase | canonical_mechanism_signature`
- `raw_text_equality_required=false`
- `signature_fields_compared=[...]`
- `shared_mechanism_invariants=[...]`
- `critical_conflicts=[...]`
- `semantic_differences=[...]`
- `result=EQUIVALENT | SUBTYPE | NOT_EQUIVALENT | HOLD`
- 左右两侧独立 `evidence_refs`

若 review 结论为 EQUIVALENT/SUBTYPE，则最终 pair 不得仍是 KEEP_SEPARATE。
若 review 结论为 HOLD，则最终 pair 不得强制 KEEP_SEPARATE。
若 review 结论为 NOT_EQUIVALENT，则必须写出具体冲突或机制差异。

## 5. 必须做 Semantic False-Negative Audit

新增：

`qa/semantic-false-negative-audit.json`

至少包含：

- `status`
- `exact_raw_text_equality_required=false`
- `paraphrase_equivalence_supported=true`
- `suspicious_rejected_pair_count`
- `reviewed_suspicious_rejected_pairs`
- `potential_equivalent_rejections=[]`
- `unresolved_false_negative_pairs=[]`
- `method`

所有“结构/operation 上疑似接近、最终却 KEEP_SEPARATE/HOLD”的 pair 必须被复核。

只有：

`potential_equivalent_rejections=[]`

且

`unresolved_false_negative_pairs=[]`

才能 PASS。

## 6. 等价 pair 本身就是可复用素材

V1.6.5 不要求只有“形成 cluster”才算有价值。

每条被接受的 MERGE/SUBTYPE support edge 都必须同步写入：

`candidate/equivalent_pairs.jsonl`

记录至少包含：

- `comparison_id`
- 左右 `unit_ids`
- `shared_mechanism_signature`
- `shared_mechanism_invariants`
- `variation_boundary`
- 左右独立 `evidence_refs`
- `decision`

这样后续写书时，可以看到：

“同一个机制在不同书里有哪些实现变体”。

**等价 pair 是参考池；cluster 是更高一层的全局归纳。**

不得为了“成簇”而牺牲 pair-level 的可解释参考。

## 7. Cluster 继续要求全局一致性

禁止仅用 connected components / single-link 把 A-B、B-C 自动组成 A-B-C。

每个 cluster 必须：

- 所有 member pair 都有可接受 support edge；
- 至少一个非泛化 `cluster_global_invariant` 被全部成员独立证据支持；
- 3+ member 必须通过 bridge/chaining audit；
- 不能仅依赖 `identity_bound`、same schema、same role label 等泛化 token。

Pair 可以语义等价而暂不成 cluster；这是允许且推荐的保守状态。

## 8. linked context 必须去重

canonicalization 前，linked function / relationship / interface 等上下文必须按：

`structured identity + canonical payload`

去重。

完全重复只保留一次；同 identity 不同 payload 必须报告 conflict。

## 9. NEW 不能表示“没有完全相同原文”

一个 unit 只有在：

1. 多路 retrieval 完成；
2. expanded-K audit 完成；
3. suspicious/near-miss pair 的 paraphrase-equivalence review 完成；
4. 没有 MERGE/SUBTYPE support；
5. 没有 unresolved false-negative；

之后，才可标 NEW/unclustered。

## 10. Lineage 必须支持 historical 1→N fine-unit migration

历史 run 常见 whole-record member，新 run 常见 fine-grained unit。两者不能 raw ID intersection，也不能要求 historical member 只能对应恰好一个新 unit。

必须支持：

`historical_member → [fine_unit_1, fine_unit_2, ...]`

依据至少组合以下信息：

- book_id；
- source path / source record id；
- source internal identity；
- evidence overlap；
- semantic structural correspondence；
- mechanism signature correspondence。

候选多于 1 个本身**不是** unresolved 的理由。

`qa/lineage-namespace-validation.json` 至少包含：

- `one_to_many_mapping_supported=true`
- `candidate_multiplicity_is_not_resolution_blocker=true`
- `unresolved_due_to_multiple_candidates_count=0`
- `historical_member_count`
- `migration_mapping_records`
- `resolved_mapping_records`
- `resolved_fine_unit_link_count`
- `lineage_decisions_using_raw_id_intersection=0`
- `direct_cross_namespace_id_intersections=0`
- `unresolved_mapping_errors=[]`
- `status`

每条 migration record 可以有多个 `resolved_fine_unit_ids`。

若仍 unresolved，必须说明真正缺失的是哪一种证据，而不能写“因为候选不止一个”。

## 11. 禁止 hardcoded QA 数字

HARDCODED_CLUSTER_MEMBERSHIP、KEYWORD_ONLY_CLUSTER_DECISIONS、false-negative count、lineage unresolved count 等，不得写死后 PASS。

validator 必须从实际 pair / cluster / migration artifacts 重新计算。

## 12. 强制 V1.6.5 独立机器门

每个 full recluster 在最终人工审核前必须运行：

```bash
python skills/novel-dna-orchestrator/scripts/validate_semantic_recluster.py <RUN_DIR>
```

或 suite 镜像：

```bash
python skills/novel-dna-mining-suite/scripts/core/validate_semantic_recluster.py <RUN_DIR>
```

必须通过：

- RETRIEVAL_RECALL_AUDIT
- KEYWORD_ONLY_CLUSTER_DECISIONS
- SEMANTIC_PARAPHRASE_EQUIVALENCE_GATE
- SEMANTIC_FALSE_NEGATIVE_AUDIT
- HARDCODED_CLUSTER_MEMBERSHIP
- CLUSTER_GLOBAL_COHERENCE_GATE
- LINKED_CONTEXT_DEDUP_GATE
- LINEAGE_NAMESPACE_COMPATIBILITY_GATE

任一 FAIL 时：

- `PLANNER_PROVISIONAL_USE=HOLD`
- `PLANNER_FINAL_MATERIAL_GATE=HOLD`
- `ACTIVE_PROMOTION=NOT_RUN`

## 13. 人工审核边界

机器 PASS 只表示：

- 没有已知的 retrieval 漏召回结构；
- 没有关键词直接决策；
- 没有 exact raw text 必须相同的假语义门；
- 没有明显 false-negative near-miss 遗漏；
- cluster 全局一致；
- lineage namespace 处理可审计。

机器 PASS 不代表用户已经批准 cluster。

人工仍需检查：

- shared mechanism signature 是否真的是“同机制”而不是过度抽象；
- variation boundary 是否足以让写书时产生多个不同实现；
- 哪些 equivalent pair 值得作为创作参考；
- cluster 是否值得进入正式素材层；
- lineage 是否足够可信。

人工未批准前保持 candidate-only。
