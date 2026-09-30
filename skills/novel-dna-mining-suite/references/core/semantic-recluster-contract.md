# V1.6.4 跨书语义重聚类可靠性契约

本契约约束所有 FULL_DNA / SUPPLEMENTAL_MATERIAL 的跨书 full recluster。目标是防止“脚本形式 PASS，但语义召回、簇一致性或 lineage 实际不可靠”。

## 1. 候选召回不能等同于 lexical top-k

禁止把单一 lexical top-2/top-3 当作完整候选空间。

候选集合至少是以下三路并集：

1. lexical retrieval：字符 bigram / token cosine 等只负责召回；
2. controlled-structural blocking：共享受控结构事实、枚举字段、schema-compatible operation slots；
3. operation/structural blocking：共享可验证运行结构、输入/处理/输出、关系发动机、因果链、替代性绑定、主角接口等。

默认 lexical top-k 不低于 8；若专项规模允许，应直接 exhaustive 比较全部跨书 schema-compatible pair。

必须同时做 expanded-K 审计，例如主运行 K=8、审计 K=16/32。若扩大 K 新发现大量可接受 MERGE/SUBTYPE，说明主运行召回不足，RETRIEVAL_RECALL_AUDIT 不得 PASS。

输出 qa/retrieval-recall-audit.json，至少包含：

- candidate_generation_modes
- lexical_top_k
- expanded_lexical_top_k
- baseline_pair_count
- expanded_pair_count
- new_support_edges_at_expanded_k
- unresolved_missed_support_edges
- unexplained_uncovered_units
- status

只有 unresolved_missed_support_edges=[] 且 unexplained_uncovered_units=[] 才可 PASS。

## 2. 检索分数和关键词不能决定 MERGE/SUBTYPE

retrieval_score、关键词命中数、字符重合度只能用于候选召回或辅助说明。

每条 MERGE/SUBTYPE 必须在 decision_audit 中显式给出：

- retrieval_score_used_for_decision=false
- keyword_count_used_for_decision=false
- structural_support_independent_of_keyword=true
- non_keyword_support_dimensions=[...]

至少一项非泛化的受控结构/运行机制证据必须独立成立。

“identity_bound”“replaceable”“same schema”“都是导师/反派/队友”等泛化 token 不能单独支撑聚类。

关键词归一化概念只允许作为辅助证据；若移除关键词映射后 MERGE/SUBTYPE 就无法成立，则必须 KEEP_SEPARATE 或 HOLD。

## 3. 禁止 hardcoded QA 计数

HARDCODED_CLUSTER_MEMBERSHIP 和 KEYWORD_ONLY_CLUSTER_DECISIONS 等 gate 不得在代码中直接写 0 再 PASS。

validator 必须实际遍历：

- 所有 MERGE/SUBTYPE pair；
- 所有 cluster member；
- 所有 support path；
- 所有 cluster-global invariant。

最终报告必须输出 inspected count、violations 和 method。

## 4. Cluster 必须有全局共同不变量

禁止仅用 connected components / single-link 把 A-B、B-C 自动组成 A-B-C。

每个 cluster 必须包含 cluster_global_invariants[]，其中至少一个 non_generic=true 且 structural_support_independent_of_keyword=true，并且 member_support 覆盖全部成员。

三成员以上 cluster 额外必须有 bridge_chaining_audit：

- status=PASS
- unsupported_member_pairs=[]
- 说明所有成员为何属于同一个共同机制，而不是通过中间节点拼接。

只有 identity_bound / replaceable / same unit type 等泛化不变量时，不得成簇。

## 5. linked context 必须先去重

canonicalization 前，应按“结构化 identity + canonical payload”去重 linked function / relationship / interface 等上下文。

完全重复项只能保留一次；同 identity 不同 payload 必须报告 conflicting_duplicate_identities，不能静默覆盖。

输出 qa/linked-context-dedup-validation.json。

## 6. NEW 不是“没进 lexical top-k”

只有完成多路候选召回和 expanded-K recall audit 后，仍无可接受 MERGE/SUBTYPE 的 unit，才能标 NEW/unclustered。

run-validation 中的 NEW 数量不得被解释成“真实语义上全部独立”，除非 RETRIEVAL_RECALL_AUDIT=PASS。

## 7. Lineage 必须解决命名空间

历史 run 的 member_record_ids 与新 run 的 fine-grained member_unit_ids 如果不是同一 ID namespace，禁止直接做 set intersection。

必须先生成显式 historical-member → fine-unit migration map，依据至少两类信息：

- book_id / source locator；
- canonical identity / schema identity；
- source record path or index；
- semantic structural correspondence。

输出 qa/lineage-namespace-validation.json，至少包含：

- historical_member_count
- migration_mapping_records
- lineage_decisions_using_raw_id_intersection=0
- direct_cross_namespace_id_intersections=0
- unresolved_mapping_errors=[]
- status

无法安全映射时 lineage 必须 HOLD，不得把旧 cluster 大量 disappeared/new 当作已验证事实。

## 8. 强制机器门

每个 full recluster 在生成最终 run-validation 前必须运行：

```bash
python skills/novel-dna-orchestrator/scripts/validate_semantic_recluster.py <RUN_DIR>
```

或 suite 内镜像：

```bash
python skills/novel-dna-mining-suite/scripts/core/validate_semantic_recluster.py <RUN_DIR>
```

必须通过：

- RETRIEVAL_RECALL_AUDIT
- KEYWORD_ONLY_CLUSTER_DECISIONS
- HARDCODED_CLUSTER_MEMBERSHIP
- CLUSTER_GLOBAL_COHERENCE_GATE
- LINKED_CONTEXT_DEDUP_GATE
- LINEAGE_NAMESPACE_COMPATIBILITY_GATE

任一 FAIL 时：

- PLANNER_PROVISIONAL_USE=HOLD
- PLANNER_FINAL_MATERIAL_GATE=HOLD
- ACTIVE_PROMOTION=NOT_RUN

不得通过降低阈值、强行保留历史 cluster count、删除反例或把 HOLD 改 PASS 来获得通过。

## 9. 人工复核仍然保留

机器 PASS 只表示“算法没有已知结构性漏洞”，不表示 cluster 已经被人工语义批准。

最终仍需人工检查：

- 每个 cluster_global_invariant 是否确实表达可复用共同机制；
- 是否存在单链桥接、表面同义或题材皮肤混同；
- 新增/消失 lineage 是否合理；
- 扩大 K 后新增支持边是否改变结论。

人工未批准前，candidate-only，不得 promotion。
