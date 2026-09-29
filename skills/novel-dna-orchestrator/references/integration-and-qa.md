# V1.6 路由覆盖说明

本文件旧版完整拆书门仅对 `FULL_DNA` 强制成立。对 `SUPPLEMENTAL_MATERIAL`，以 `source-role-and-routing.md` 为更高优先级：

- 先通过 routing gate；
- 只检查 target_specialties；
- 未授权专项不算缺失；
- 不强制逐章 emotion，除非 chapter_emotion 被授权；否则只做必要局部 overlay；
- supplemental 完成状态为 COMPLETE_SUPPLEMENTAL_SOURCE / _WITH_HOLDS / BLOCKED；
- 新来源不得 append 到旧 cluster，只对受影响专项启动新的 full recluster。

---

# 总索引、阶段门与验收

## 阶段门

### G0 证据盘点

通过条件：书籍ID、来源路径、章节范围、QA状态清楚。没有榜单数据不阻断拆书，但市场等级必须为 `UNGRADED`。

### G1 章节事实

通过条件：目标范围无未解释缺章；已有QA中的FAIL已经修复或明确隔离。章节事实未通过时，不生成高置信专项包。

### G2 章节情绪

通过条件：目标范围每章一条；主情绪、情绪对象、期待来源、兑现级别、可见证据、章末余味齐全；schema validator、RAW_ENDING、FIELD_ECHO、NORMALIZED_TEMPLATE、ANALYSIS_VS_SUMMARY 与 SOL SOURCE_CONTRADICTION_SAMPLE 全部通过。确实没有兑现时允许写“继续蓄压”。按章或批次隔离QA：PASS计入可用覆盖，HOLD/FAIL只计入记录总数，不支持高置信聚合。

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
| candidate_count | 未审核候选数量 |
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

## 冷启动验收

从目标题材随机选择一个开书需求，仅使用总索引和2—4张候选/正式卡完成：

1. 三套“金手指×世界观×修炼体系”组合；
2. 为推荐组合指定主情绪承诺与前10章情绪节奏；
3. 配置主角、女主、竞争者和导师的功能；
4. 给出主线、两条支线和至少两个交汇点；
5. 所有关键设计能回溯到ID或路径；
6. 至少重设触发、人物、资源、场景、兑现、后果中的三项，避免复制参考书。

无法完成时，记录是哪个横向库或情绪字段缺失，而不是用模型记忆补齐。

## 人物与大故事线派生库

总索引增加 `heroine_cards`、`long_arc_villain_cards`、`major_storyline_cards` 及各自路径。零张时必须区分 `未回填`、`已检查但无合格对象`、`证据不足`，不能只写数字零。女主卡检查独立目标与有代价的行动；长线反派卡检查至少两次有因果连续性的交锋与策略变化；大故事线卡检查目标对抗、反派计划、主角收益、收束状态、下一线入口和逐边证据。派生 QA 不得抬高原章节事实 QA。


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
