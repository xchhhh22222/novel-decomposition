# 总索引、阶段门与验收 V1.6

## 阶段门

### G-1 路由门

所有新增来源在 G0 前必须先完成 source_route。

FULL_DNA：
- 九专项全部授权；
- full_book_dna=true。

SUPPLEMENTAL_MATERIAL：
- purpose 非空；
- target_specialties 非空真子集；
- excluded_specialties 与 target_specialties 互斥且并集覆盖九专项；
- derived_views 显式；
- chapter_scope 显式；
- 用户已经确认 routing matrix。

未通过 G-1，不得开始写 per_book / derived 正式输出。

### G0 证据盘点

通过条件：书籍ID、来源路径、章节范围、QA状态清楚。没有榜单数据不阻断拆书，但市场等级必须为 `UNGRADED`。

### G1 章节事实

通过条件：目标范围无未解释缺章；已有QA中的FAIL已经修复或明确隔离。章节事实未通过时，不生成高置信专项包。

### G2 章节情绪

FULL_DNA：目标范围每章一条 canonical emotion；主情绪、情绪对象、期待来源、兑现级别、可见证据、章末余味齐全；schema validator、RAW_ENDING、FIELD_ECHO、NORMALIZED_TEMPLATE、ANALYSIS_VS_SUMMARY 与 SOL SOURCE_CONTRADICTION_SAMPLE 全部通过。确实没有兑现时允许写“继续蓄压”。

SUPPLEMENTAL_MATERIAL：只有当 chapter_emotion 被列入 target_specialties 时才要求完整 G2；否则允许只为关键首次展示、兑现、关系转折生成局部 emotion overlay。局部 overlay 不能伪装成全章 emotion coverage。

按章或批次隔离QA：PASS计入可用覆盖，HOLD/FAIL只计入记录总数，不支持高置信聚合。

### G3 专项包

通过条件：每本书均有记录或明确缺口；核心结论有证据；没有越界输出。

### G4 横向聚类

通过条件：每个候选给出最近邻、合并/子型/新母型判断和理由；单书候选默认不升级为高频母型。

### G5 总索引

通过条件：能区分证据、候选和正式卡；能从书籍、元素、情绪、阶段四种入口定位内容。

## 总索引建议列

| 列 | 含义 |
| --- | --- |
| book_id / title | 单书入口 |
| market_grade | 市场评级，缺数据为UNGRADED |
| chapters_covered | 已覆盖范围 |
| qa_status | 章节证据是否可用于下游 |
| emotion_coverage | PASS可用章数/目标章数；另列记录总数 |
| dominant_emotion_curve | 主要情绪曲线摘要 |
| golden_finger | 正规化金手指母型或候选 |
| world / system | 世界观与修炼体系接口 |
| protagonist / relationship | 人物与关系入口 |
| mainline / sublines | 线路入口 |
| opening / structure | 开篇与篇章结构入口 |
| specialist_coverage | 各专项的 per_book / gap / cluster 覆盖，不把 QA 与 handoff 冒充业务候选 |
| candidate_count | 未审核的跨书 cluster 候选数量；单书包、QA、handoff 与 gap 不计入 |
| active_card_count | 已确认正式卡数量 |
| gaps | UNKNOWN和待定项 |

## 一致性规则

1. 下游状态不能高于上游证据：章节QA为FAIL时，专项记录最高为LOW/candidate。
2. 同一字段只能有一个权威来源；进度文件、QA报告和BOOK DNA冲突时，先列冲突，不自行挑一个覆盖。
3. 总索引是导航，不复制长内容；每项使用路径或ID指回原文件。
4. 总索引重建不得修改源文件。
5. 任务清单必须显式区分目标范围、排除章节和源文缺章；不得从自由文本静默猜测后覆盖清单。
6. `canonical / per_book / qa / handoff` 任一仍为 HOLD 或等待人工复核时，manifest 不得写 PASS。人工 override 必须同时记录 `manual_review: PASS`、`reviewer: SOL` 和非空 `reason`，并先统一所有状态文件；运行 `scripts/validate_module_status_consistency.py` 复验。
7. batch accepted commit 必须区分 `content_acceptance_commit` 与 `latest_corrective_commit`，不得用一次共享 metadata commit 冒充多本书的内容接受时间。

## V1.6 完成门

### FULL_DNA 完成门

沿用完整主书规则：
- 九专项均有 per_book/gap；
- 01 全章 canonical emotion 通过；
- heroine / long_arc_villain 有卡或明确 gap；
- 各必需 QA/validator 通过；
- 可标 COMPLETE_SINGLE_BOOK。

### SUPPLEMENTAL_MATERIAL 完成门

只检查 source_route 授权范围：
- 每个 target_specialty 有完整 per_book/gap；
- 对应 derived_views 已生成或明确 gap；
- chapter_scope 的全文扫描/授权范围 recall 有证据；
- 对应 specialist validator / semantic audit 通过；
- excluded_specialties 未被误写成“缺失失败”；
- 输出仍为 candidate-only。

允许：
- COMPLETE_SUPPLEMENTAL_SOURCE
- COMPLETE_SUPPLEMENTAL_SOURCE_WITH_HOLDS
- BLOCKED

禁止把 supplemental COMPLETE 解释为九维完整拆书。

### 新来源后的聚类

新增来源不得 append 到旧 cluster。只对受影响专项开启新的 full recluster run，但该专项内部仍必须完成：
`per_book/gap completeness → nearest_neighbors → KEEP_SEPARATE → clusters → QA → handoff → lineage`。

旧 run 作为历史快照保留。

## 冷启动验收

从目标题材随机选择一个开书需求，仅使用总索引和2—4张候选/正式卡完成：

1. 三套“金手指×世界观×修炼体系”组合；
2. 为推荐组合指定主情绪承诺与前10章情绪节奏；
3. 配置主角、女主、竞争者和导师的功能；
4. 给出主线、两条支线和至少两个交汇点；
5. 所有关键设计能回溯到ID或路径；
6. 至少重设触发、人物、资源、场景、兑现、后果中的三项，避免复制参考书。

无法完成时，记录是哪个横向库或情绪字段缺失，而不是用模型记忆补齐。


## V1.6.1 Derived Material Gate

当 source_route.derived_views 包含以下任一视图：

- ability_assets
- dungeon_rule_assets
- relationship_engine_assets
- charismatic_antagonist_assets
- combat_expression_assets

则在单源 COMPLETE 与批次 recluster 之间增加硬门：

```text
parent specialist validator PASS
→ derived canonical normalization
→ validate_derived_materials.py
→ DERIVED_MATERIAL_CONTRACT_V1_6_1 = PASS
→ 才允许进入 full recluster
```

机器门至少检查：

- schema_version=2；
- canonical record_id；
- 字段白名单；
- 历史别名禁止；
- 精确章节 evidence refs；
- unknowns/confidence 关系；
- combat assets 一维数组；
- duplicate record IDs；
- manifest derived record counts 与实际文件一致。

仅有：

```text
DERIVED_CONTRACT_CHECK = PASS
DEDICATED_DERIVED_VALIDATOR = NOT_AVAILABLE
```

不再满足 V1.6.1 的最终 derived gate。

对于 V1.6 历史批次，应先执行 normalization，不要求重新拆书；若无法仅靠已有 derived/per_book/QA 安全补齐字段，标记 `NORMALIZATION_SOURCE_EVIDENCE_REQUIRED` 并只做最小证据回查。
