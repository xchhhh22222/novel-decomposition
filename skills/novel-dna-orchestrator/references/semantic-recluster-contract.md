# V1.6.6 跨书语义重聚类可靠性契约

V1.6.6 继续保留 V1.6.5 的多路召回、paraphrase-equivalence、equivalent-pair、cluster-global coherence、linked-context dedup 和 1→N lineage，但新增两条硬边界：

1. **关键词/词典归一化只能做 retrieval hint，不能换个名字后继续决定语义支持。**
2. **linked context 只能辅助说明 primary unit，不能因为外围关联记录碰巧含有同样词，就把两个 primary units 判成等价。**

目标是同时避免 false negative 和 false positive，并保留真正可用于写书的“同机制不同实现”参考。

## 1. 四路召回仍然保留

candidate generation 至少是：

- lexical
- controlled_structural
- operation_structural
- mechanism_signature_hint

其中 mechanism-signature 的自动词典/substring/规则归一化只能作为 **hint signature**，职责是找疑似 pair。

不得把 hint atom 直接称作已证实的 mechanism invariant。

## 2. 强制区分 hint signature 与 adjudicated signature

每个 unit 必须区分：

- `primary_object_signature_hint`
- `linked_context_signature_hint`
- `adjudicated_primary_mechanism`

前两者可以由关键词、词典、规则、embedding 或其它 deterministic normalizer 产生，只负责召回。

`adjudicated_primary_mechanism` 才能参与 MERGE/SUBTYPE。它必须来自：

- primary source object 自身的结构化字段；
- controlled structural alignment；
- 或冻结的 evidence-grounded semantic review。

禁止：

`MECHANISM_ATOM_RULES + substring match → shared atoms → SUBTYPE`

这种闭环。

## 3. Primary object 必须是语义支持主体

对于 fine-grained unit，primary object 是 `source_internal_object` 指向的那一条 canonical object。

例如人物功能的：

- function_combination
- narrative_function
- replaceability
- protagonist_interface

各自只能先用自己的 primary object 建立核心机制。

linked function / relationship / transition / protagonist interface 可以作为 context，但不能单独供应：

- shared operation-chain invariant；
- shared target invariant；
- shared effect invariant；
- MERGE/SUBTYPE support。

如果去掉 linked context 后，primary objects 本身无法证明同一核心机制，则该 pair 不能因为 linked context 相似而进入 SUBTYPE/MERGE。

## 4. 每条接受边必须写 support provenance

MERGE/SUBTYPE 的 `decision_audit.support_provenance` 至少包含：

- `keyword_hint_used_as_support=false`
- `linked_context_only_support=false`
- `semantic_adjudication_method`
- `primary_unit_support.left=[...]`
- `primary_unit_support.right=[...]`
- `corroborating_linked_context.left=[...]`
- `corroborating_linked_context.right=[...]`

`primary_unit_support` 必须明确到 primary object 的字段/证据，不得只给整个 comparison unit 的总 evidence_refs。

允许的 semantic adjudication method：

- `evidence_grounded_primary_object_paraphrase`
- `controlled_structural_alignment`
- `frozen_semantic_review`

## 5. Paraphrase review 必须独立于 keyword hints

`paraphrase_equivalence_review` 必须至少包含：

- `reviewed=true`
- `method=evidence_grounded_structured_paraphrase | primary_object_mechanism_alignment | controlled_structural_paraphrase`
- `adjudication_source=primary_object_semantic_review | controlled_structural_alignment | frozen_semantic_review`
- `keyword_hint_used_as_support=false`
- `linked_context_only_support=false`
- `raw_text_equality_required=false`
- `signature_fields_compared`
- `shared_mechanism_invariants`
- `critical_conflicts`
- `semantic_differences`
- `result=EQUIVALENT | SUBTYPE | NOT_EQUIVALENT | HOLD`
- 左右 primary evidence

关键词、substring atom、词典 atom 可以触发该 review，但不能决定 review.result。

## 6. 新增 mechanism-signature provenance audit

必须输出：

`qa/mechanism-signature-provenance.json`

至少包含：

- `status`
- `accepted_support_edge_count`
- `primary_object_supported_edge_count`
- `keyword_hints_used_for_support=[]`
- `linked_context_only_support_edges=[]`
- `method`

只有每一条 accepted support edge 都有 bilateral primary-object support 才可 PASS。

## 7. 新增 linked-context support isolation gate

linked context 允许：

- 扩展 variation boundary；
- 补充人物关系/阶段/风险解释；
- 帮助人工理解为什么两个 primary mechanisms 在剧情中作用相似。

linked context 不允许：

- 给 primary object 补出它本身不存在的核心 operation；
- 用其它 function 的“验证/保护/准入”词把当前 function_combination 伪装成同机制；
- 让不同阶段、不同行为主体的外围记录共同凑出 support threshold。

输出必须保证：

`linked_context_only_support_edges=[]`

## 8. Equivalent pair 仍然优先保留

被接受的 MERGE/SUBTYPE 仍写：

`candidate/equivalent_pairs.jsonl`

但其中 `shared_mechanism_signature` 必须来自 adjudicated primary mechanism，而不是 hint atom intersection。

equivalent pair 是创作参考层，cluster 是更高层归纳；pair 不强制成 cluster。

## 9. Cluster 继续要求 complete-link

保留：

- complete-link all-pair support；
- cluster-global invariant；
- 3+ member bridge/chaining audit；
- candidate-only；
- 不设置 cluster 数量 KPI。

新增要求：

cluster-global invariant 必须来自每个 member 的 primary object adjudicated mechanism。linked context 不能供应 cluster-global 核心 invariant。

## 10. False-negative audit 不能和同一关键词规则自证

`qa/semantic-false-negative-audit.json` 仍要求：

- suspicious rejected pairs 全覆盖；
- potential_equivalent_rejections=[];
- unresolved_false_negative_pairs=[]。

但 V1.6.6 禁止“用同一套 keyword atom 先生成 signature，再用相同 atom 判断 NOT_EQUIVALENT，然后称独立复核”。

false-negative review 必须记录 non-keyword adjudication provenance。

## 11. Lineage 的 source-record match 只负责找候选

historical whole-record → fine unit 可以 1→N，但：

- `book_id`
- `source_record_id`
- `source_path`

只能用于 candidate generation。

每个 `resolved_fine_unit_id` 必须满足以下之一：

1. exact unit/internal identity；或
2. **同时**具备：
   - book-scoped/member-level evidence overlap；
   - non-generic mechanism-signature correspondence。

禁止仅因为：

`same source_record_id + same book + 共用某一章 evidence`

就把该书下所有 narrative_function / relationship_function / transition / replaceability / interface 都标 RESOLVED。

每条 resolved candidate 必须在自己的 `resolution_basis` 中体现上述条件。

## 12. Lineage 事件在映射不可信时保持 HOLD

若 historical member 无法落到具有 member-level evidence + mechanism correspondence 的 fine unit，则保持 unresolved/HOLD。

不得为了降低 unresolved 数量而扩大一对多映射。

`disappeared / moved / new / stable` 只有在对应 resolved links 满足 V1.6.6 link-resolution gate 后才可作为确定 lineage。

## 13. V1.6.6 独立 validator

最终必须运行：

```bash
python skills/novel-dna-orchestrator/scripts/validate_semantic_recluster.py <RUN_DIR>
```

必须通过：

- RETRIEVAL_RECALL_AUDIT
- KEYWORD_ONLY_CLUSTER_DECISIONS
- SEMANTIC_PARAPHRASE_EQUIVALENCE_GATE
- MECHANISM_SIGNATURE_PROVENANCE_GATE
- LINKED_CONTEXT_SUPPORT_ISOLATION_GATE
- SEMANTIC_FALSE_NEGATIVE_AUDIT
- HARDCODED_CLUSTER_MEMBERSHIP
- CLUSTER_GLOBAL_COHERENCE_GATE
- LINKED_CONTEXT_DEDUP_GATE
- LINEAGE_NAMESPACE_COMPATIBILITY_GATE

任一失败：

- PLANNER_PROVISIONAL_USE=HOLD
- PLANNER_FINAL_MATERIAL_GATE=HOLD
- ACTIVE_PROMOTION=NOT_RUN

## 14. 人工审核

机器 PASS 只表示已知算法捷径被挡住。

人工必须抽查：

- equivalent pair 的左右 primary objects 是否真的同机制；
- linked context 是否只是 corroboration；
- cluster-global invariant 是否来自所有 member 自身；
- lineage resolved links 是否真的对应旧 member 的细粒度后继。

人工批准前保持 candidate-only。
