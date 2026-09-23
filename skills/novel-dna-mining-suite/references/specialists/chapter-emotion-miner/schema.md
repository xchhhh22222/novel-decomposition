# 逐章读者情绪专项输出契约

## 1. 权威关系

`chapter_emotion.jsonl` 的逐章记录唯一服从：

`../../core/chapter-emotion-schema.md`

本文件是 `novel-chapter-emotion-miner` 的输出契约适配层，不是第二套逐章情绪 Schema。禁止在这里复制、改写或扩展逐章情绪字段；特别禁止增加平行的情绪曲线、读者感受或兑现评分字段。

逐章记录和派生记录分离：

- 逐章记录：使用 canonical chapter-emotion-schema 的既有字段、枚举、唯一性和证据要求；
- 派生记录：用于单书摘要、近邻、聚类、QA 和人工交接，使用本文件规定的统一 envelope；
- 节奏审计和承诺生命周期汇总：属于派生 QA/审计产物，不把字段塞回 `chapter_emotion.jsonl`。

## 2. 统一 envelope

除 canonical 逐章情绪记录外，所有机器可读的派生记录必须包含：

```json
{
  "record_type": "per_book|nearest_neighbor|cluster|qa|handoff|gap",
  "schema_version": 1,
  "record_id": "EMOTION:<TYPE>:<STABLE_ID>",
  "status": "candidate",
  "book_id": "BOOK_01",
  "book_ids": ["BOOK_01", "BOOK_02"],
  "evidence_refs": ["BOOK_01:CHAPTER:0001", "BOOK_01:STAGE:01"],
  "unknowns": [],
  "confidence": "HIGH|MEDIUM|LOW",
  "qa_status": "PASS|HOLD|FAIL"
}
```

实际记录按作用使用 `book_id` 或 `book_ids` 其中之一，不要求两个同时出现。单书记录优先使用 `book_id`，跨书比较和聚类使用 `book_ids`。`evidence_refs` 必须能回到章节或阶段；`unknowns` 不得用推测值填充。关键未知存在时不得标记 `HIGH`。

状态规则：

- 本专项新建记录只能是 `candidate`；
- 不提供从 `candidate` 到 `active` 或 `deprecated` 的自动路径；
- `qa_status` 表示记录质量，不改变 `status`；
- `HOLD`、`FAIL` 和 `gap` 必须保留并显式隔离，不能伪装成通过覆盖。

## 3. canonical 逐章记录

逐章情绪覆盖文件的默认位置为：

```text
<output_root>/<BOOK_ID>/chapter_emotion.jsonl
```

项目默认 `<output_root>` 为：

```text
素材库/DNA素材/01_章节情绪
```

每行恰好一条章节记录，必须直接符合 `chapter-emotion-schema.md`。本适配层不在逐章对象外包 envelope，不把派生记录字段强行追加到 canonical 记录中；需要核验来源时使用 canonical schema 已规定的 `chapter_ref`、`evidence_path`、`source_fingerprint` 和其它既有字段。

逐章文件必须满足：

1. 同一本书的 `(book_id, chapter)`、`chapter_ref` 和 `record_id` 唯一；
2. `status` 保持 `candidate`，`qa_status` 只使用现有枚举；
3. 主情绪、辅情绪、章节作用、期待、压力、转折、兑现、证据、余震、钩子和承诺字段均按 canonical Schema 处理；
4. 没有前置期待或可见证据时，不标记强兑现；
5. 缺章、正文不可读或无法判断的情况进入派生 `gap`/QA 记录，不通过新增字段补齐逐章 Schema；
6. `source_fingerprint` 无法生成时按 canonical Schema 写 `UNAVAILABLE`，并在 QA 中说明原因。

## 4. `per_book` 单书证据包

每本目标书必须有一条 `record_type: per_book` 的派生记录，或有一条明确的 `record_type: gap` 记录，不能静默省略目标书。

默认位置：

```text
<output_root>/<BOOK_ID>/per_book.jsonl
```

`per_book` 记录只汇总覆盖和路径，不复制整套逐章情绪字段。除统一 envelope 外，允许使用：

```json
{
  "chapters_covered": "1-20",
  "chapter_emotion_path": "<BOOK_ID>/chapter_emotion.jsonl",
  "rhythm_audit_path": "<BOOK_ID>/rhythm_audit.md",
  "promise_tracking": "同一目录中的派生承诺追踪或QA记录",
  "coverage_summary": "PASS章数/目标章数，另列记录总数",
  "known_gaps": ["缺失章节或无法核验的范围"],
  "source_numbering_notes": []
}
```

`per_book` 的核心结论必须能够回指逐章或阶段证据。只确认书名、简介或 BOOK DNA 时，使用 `gap`，不生成貌似完整的单书包。

## 5. 承诺追踪与节奏审计

承诺追踪、每十章节奏审计、缺章检查和重复章检查都是派生记录或报告。它们不能扩展 `chapter_emotion.jsonl`。

默认人读报告位置：

```text
<output_root>/<BOOK_ID>/rhythm_audit.md
```

如需机器可读的承诺或 QA 记录，必须使用统一 envelope，并至少说明：

- 适用书籍和章节范围；
- 开启、蓄压、转折、回收或仍开放的稳定承诺名称；
- 每项结论对应的 `evidence_refs`；
- 缺章、重复、UNKNOWN、HOLD/FAIL 和无法确认的原因；
- 节奏检查命中的窗口和可复核的章节记录 ID。

审计至少覆盖：连续同类情绪、长时间蓄压不兑现、连续强兑现、强兑现后的余震、承诺窗口和同形钩子。审计只报告证据，不反向改写源章节或 canonical 记录。

## 6. `nearest_neighbors` 近邻记录

近邻记录只能在目标书完成逐章抽取和单书 QA 后生成。默认位置：

```text
<output_root>/nearest_neighbors.jsonl
```

每行一条跨书或候选间比较记录，除统一 envelope 外建议包含：

```json
{
  "source_record_ids": ["EMOTION:BOOK:BOOK_01", "EMOTION:BOOK:BOOK_02"],
  "similarity_basis": ["期待来源", "蓄压方式", "兑现证据", "情绪余震"],
  "difference_boundary": "决定保持相近但不合并的关键差异",
  "decision": "merge_candidate|keep_distinct|insufficient_evidence",
  "reason": "比较理由"
}
```

情绪词相同不等于运行机制相同；不得用书名、专名、题材标签或一句卖点制造近邻。

## 7. `clusters` 聚类候选

聚类只能在全部目标书的同类专项包完成后生成。默认位置：

```text
<output_root>/clusters.jsonl
```

每行一条聚类或变体候选，除统一 envelope 外建议包含：

```json
{
  "cluster_level": "大类|母型|子型|变体",
  "label": "可替换的功能性名称，不使用专名复制",
  "member_record_ids": [],
  "nearest_neighbor_record_ids": [],
  "shared_operation": "期待—蓄压—转折—兑现—余震的共同运行方式",
  "boundary_conditions": ["与相近候选保持区分的条件"],
  "supporting_book_count": 2,
  "merge_decision": "candidate_merge|candidate_split|new_candidate|insufficient_evidence"
}
```

单书变体不能直接升级为跨书高频母型；任何 `cluster` 的 `status` 都必须保持 `candidate`。聚类结论至少需要章节或阶段证据，BOOK DNA 只能做导航。

## 8. `qa` 质量记录

默认机器可读位置：

```text
<output_root>/qa.jsonl
```

人读版可另存为：

```text
<output_root>/qa/qa_report.md
```

每条 QA 记录除统一 envelope 外，应说明检查范围、结果和证据，例如：

```json
{
  "scope": "BOOK_01:1-20",
  "checks": {
    "coverage": "PASS|HOLD|FAIL",
    "missing_chapters": [],
    "duplicate_chapters": [],
    "schema_validation": "PASS|HOLD|FAIL",
    "promise_tracking": "PASS|HOLD|FAIL",
    "rhythm_audit": "PASS|HOLD|FAIL"
  },
  "gaps": [],
  "disputes": [],
  "blocking_reasons": []
}
```

QA 的 `qa_status` 不能覆盖事实状态：任何关键证据缺失、章节 QA FAIL 或 Schema 校验失败都必须阻止高置信聚合。

## 9. `handoff` 人工审核交接

默认位置：

```text
<output_root>/handoff.jsonl
```

每行一条待审核交接记录，除统一 envelope 外建议包含：

```json
{
  "candidate_record_ids": [],
  "recommended_action": "保留|合并候选|拆分候选|补证据|暂缓",
  "decision_points": ["需要人工确认的边界或争议"],
  "evidence_gaps": [],
  "forbidden_automatic_actions": ["写入active", "修改canonical schema", "修改正式素材库"]
}
```

`handoff` 只交给人工审核，不代表候选已经通过审核，也不授予任何正式素材库写入权限。

## 10. `gap` 缺口记录

目标书或目标章节没有足够证据时，保留缺口记录：

```json
{
  "schema_version": 1,
  "record_type": "gap",
  "record_id": "EMOTION:GAP:BOOK_01:001",
  "status": "candidate",
  "book_id": "BOOK_01",
  "evidence_refs": ["BOOK_01:CHAPTER:0001"],
  "unknowns": ["缺失章节范围", "承诺是否回收"],
  "confidence": "LOW",
  "qa_status": "HOLD",
  "reason": "无法核验的事实或覆盖缺口",
  "known_evidence": ["实际可读的范围"],
  "blocked_outputs": ["高置信per_book", "跨书聚类"]
}
```

`gap` 不是用来填充虚构内容的占位符；它必须说明缺口位置、已知证据和被阻断的下游判断。

## 11. 交付与状态检查

一个完整批次至少应能定位：

1. 每本书的逐章 canonical 文件、单书 `per_book` 记录和节奏审计；
2. 目标范围的缺章、重复章、承诺追踪和节奏 QA；
3. 全部目标书完成后才生成的 `nearest_neighbors` 和 `clusters`；
4. 带有决策点和证据缺口的 `handoff`；
5. 所有派生记录的统一 envelope、`candidate` 状态和证据引用。

若为了容纳某项派生结果必须修改 `chapter-emotion-schema.md`，应停止并报告冲突，不得自行扩展 canonical Schema。
