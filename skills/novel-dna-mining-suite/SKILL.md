---
name: novel-dna-mining-suite
description: V1.6.4 小说 DNA 拆解套件：新增跨书语义重聚类可靠性契约与独立 validator，禁止 tiny lexical top-k、关键词决策、single-link 链式成簇和跨命名空间 raw-ID lineage。
---

# 小说 DNA 拆解套件 V1.6.4

这是一个独立迁移包，入口负责路由和边界，详细规则按需读取 `references/`。不要把候选直接写成正式套路卡，也不要修改源章节或正式素材库。

## 路由

- **任何新增来源书开始前，必须先读取 `references/core/source-role-and-routing.md`，确定 `FULL_DNA` 或 `SUPPLEMENTAL_MATERIAL`。**
- **若为 SUPPLEMENTAL_MATERIAL，再读取 `references/core/supplemental-profiles.md` 选择 Profile；未经用户确认 routing matrix，不开始正式拆解。**
- **凡 source_route.derived_views 命中 ability_assets / dungeon_rule_assets / relationship_engine_assets / charismatic_antagonist_assets / combat_expression_assets，必须同时读取 `references/core/derived-material-contract.md`；该契约优先于 profile 中的旧“推荐字段”。**
- 路由落盘后先运行 `python scripts/core/validate_source_routes.py <source_routes.jsonl>`；SOURCE_ROUTING_GATE_V1_6_1 未 PASS 时禁止开始拆解。
- 总控、输入包、目录、阶段门和总索引：读取 `references/core/`。
- 章节情绪：读取 `references/specialists/chapter-emotion-miner/`，canonical 章节字段唯一服从 `references/core/chapter-emotion-schema.md`。
- 金手指：读取 `references/specialists/golden-finger-miner/`。
- 世界观：V1.4 同时拆世界规则与 `factions` 势力生态。
- 修炼体系：V1.4 按来源实际存在数量拆 `cultivation_systems / system_relations / techniques / artifacts / resource_assets`，不预设体系数量。
- 人物功能、主支线、开篇、篇章结构、剧情机制：按模块读取对应 specialist 目录的 guidance/schema/QA。
- **人物个体卡为 V1.5 必跑派生层**：每本书在人物功能完成后，额外调用 `novel-character-card-miner`；女主/关键女性写 heroine_character 或明确 gap，长线反派写 long_arc_villain 或明确 gap。禁止用人物功能标签冒充人物个体卡。
- 统一校验：运行 `python scripts/validate.py --specialty <slug> --kind <kind> ...`；该入口只分派包内 validator，不依赖外部 Skill。
- V1.6.1 Derived 硬门：运行 `python scripts/core/validate_derived_materials.py --root <material-library-root> --books <BOOK_ID,...>`；未得到 `DERIVED_MATERIAL_CONTRACT_V1_6_1=PASS`，不得宣称 supplemental 批次可进入聚类。
- V1.6.2 批次硬门：读取 `references/core/supplemental-batch-gates.md`，运行 `python scripts/core/validate_supplemental_batch.py --root <material-library-root> --batch-dir batch/<BATCH_ID> --books <BOOK_ID,...>`；必须对账 route/output、manifest/batch status，并输出 cluster eligible/held IDs。
- V1.6.3 Combat 语义门：存在 combat_expression_assets 时运行 `python scripts/core/validate_combat_semantics.py --root <material-library-root> --books <BOOK_ID,...>`；UNKNOWN 只能写字面值 `UNKNOWN`，PASS 核心字段不得 UNKNOWN，且 cost/limit/counterplay 至少一项有证据。
- V1.6.3 Batch Summary 门：批次 validator 同时核对 `derived_hold_records` 与真实 HOLD 总数、`derived_totals` 与真实 records；陈旧汇总直接 FAIL。
- V1.6.4 Semantic Reclustering 门：任何 full recluster 必须读取 `references/core/semantic-recluster-contract.md`，执行多路召回 + expanded-K recall audit、非关键词结构证据、cluster-global invariant/bridge audit、linked-context dedup 与 lineage migration map；运行 `python scripts/core/validate_semantic_recluster.py <RUN_DIR>`，未 PASS 不得宣称 NEW/MERGE/SUBTYPE/lineage 可靠。
- V1.5.1 语义门：章节情绪结构校验后运行包内 `scripts/specialists/chapter-emotion-miner/audit_semantics.py`；剧情线运行 `audit_recall.py`；剧情机制运行 `audit_depth.py`；manifest 落盘前运行 `scripts/core/validate_module_status_consistency.py`。\n- V1.5.2 语义加固：RAW_ENDING 过滤纯标点/过短尾句；模板骨架支持从人物卡、人物功能或显式实体表读取已知中文实体并归一化为 `<ENTITY>`，避免仅替换人名绕过模板检测。

## 统一不变量

- 中控只决定“调用哪些 specialist”，不改变 specialist 自己的 schema / QA / validator。
- FULL_DNA 仍按原完整主书流程执行；SUPPLEMENTAL_MATERIAL 只要求 target_specialties 完整，不要求九专项全部运行。
- SUPPLEMENTAL_MATERIAL 仍必须扫描授权 chapter_scope 的全部正文以保证目标专项 recall；不得把“专项拆解”误解成“随便抽几章”。
- 未授权专项必须显式列入 excluded_specialties，不能静默省略。
- BOOK_ID 继续使用 BOOK_010、BOOK_011...；用 source_role / extraction_mode 区分补充来源，避免破坏现有脚本。
- 输入必须由总控冻结：`batch_id`、`specialty`、`book_ids`、`allowed_sources`、`chapter_ranges`、`emotion_overlay_paths`、`output_root`、`forbidden_outputs`、`known_gaps`。
- 派生记录固定 `status: candidate`；不得生成 `active`、`deprecated` 或正式素材卡。
- V1.6.1 五类补充 derived view 禁止自由字段：只能使用 `derived-material-contract.md` 的 canonical 字段；禁止 `asset_id/ability_name/core/conflicting_information/long_term_tension_with_protagonist` 等历史别名继续流入新结果。
- Derived `evidence_refs` 必须是精确章节引用 `BOOK_xxx:CHAPTER:nnnn`；章节区间只写 `chapter_span`，不得把 `ch16-57` 或 `BOOK_xxx:CHAPTER:0001-1002` 当 evidence ref。
- V1.6.2 路由输出一致性：任何真实 `*/derived/*.json|*.jsonl` 都必须出现在该书 `source_route.derived_views`，或作为明确 0-record checked gap；历史漏记只能在确认原任务确曾授权后做 metadata reconciliation。
- V1.6.2 聚类资格：controlled derived 中 `qa_status=PASS` 才可聚类，`HOLD` 只留 inventory；禁止为了跑聚类把 HOLD 改 PASS。
- V1.6.3 UNKNOWN 规则：未知业务字段必须严格为 `UNKNOWN`，原因写入 `unknowns[]`；禁止 `UNKNOWN——原因`、`未知`、`不适用/未知`，也禁止把 `EVIDENCE_CORRECTION` 审计日志塞进 unknowns。
- V1.6.3 反推禁令：`原文未展示代价/反制/限制` 不能推导成 `无代价/无反制/无限制`；没有积极证据时保持 UNKNOWN。
- 每条抽象结论必须带结构化 `evidence_refs`；证据不足保留 `UNKNOWN`、`partial`、`gap` 或 `HOLD`。
- 单书覆盖必须是每本恰好一条 `per_book` 或 `gap`；跨书 `nearest_neighbor/cluster` 必须提供 `--expected-books`、`--all-books-complete` 和 `--completion-manifest`。
- `arcs[]` 与 `mechanisms[]` 分别承载一本书的多个篇章阶段和多个剧情机制，不能只保留代表性单条记录。
- 章节情绪 canonical 记录不得追加派生 envelope；情绪 validator 必须同时检查包内权威 validator 的契约一致性。
- schema PASS 不能替代 semantic PASS；unique count 只作诊断，缺少 SOL 源文抽样为 `SOURCE_SAMPLE_REVIEW_REQUIRED`。
- 未获得用户明确授权，不落盘到正式素材库；默认输出目录和写入归属见 `references/core/library-layout.md`。
- 拆书层禁止跨书拼装来源事实；跨书拼装只能由创造层生成新的【新书候选】，不得回写来源 `per_book`。

## 交付顺序

### FULL_DNA

保持 V1.5.2 原完整顺序：

```text
章节事实
→ 逐章情绪全覆盖
→ 02—09 单书专项
→ heroine / long_arc_villain 等派生视图
→ 单书 QA
→ 跨书比较
→ 总索引
```

人物功能完成后必须补人物个体卡；缺任一必需视图不得标 COMPLETE_SINGLE_BOOK。

### SUPPLEMENTAL_MATERIAL

先完成 source_route 并等待用户确认：

```text
来源盘点
→ purpose
→ target_specialties
→ derived_views
→ excluded_specialties
→ routing matrix
→ 用户确认
→ 授权专项全文扫描
→ 专项 per_book / derived / QA
→ V1.6.1 derived validator
→ V1.6.3 combat semantic gate（若有 combat）
→ V1.6.3 supplemental batch gates
→ COMPLETE_SUPPLEMENTAL_SOURCE / _WITH_HOLDS
```

SUPPLEMENTAL 不强制全书逐章 emotion canonical，但若目标专项需要“首次展示/兑现/关系转折”的情绪证据，应对对应 evidence window 做局部 overlay。

新 supplemental 来源完成后，不得直接修改旧 cross-book cluster。等该批来源完成后，只对受影响专项开启新的 full recluster run，并保留旧 run lineage。

## 完成状态

FULL_DNA：
- `COMPLETE_SINGLE_BOOK`
- 或现有 HOLD/BLOCKED 状态

SUPPLEMENTAL_MATERIAL：
- `COMPLETE_SUPPLEMENTAL_SOURCE`
- `COMPLETE_SUPPLEMENTAL_SOURCE_WITH_HOLDS`
- `BLOCKED`

若 source_route 包含 V1.6.1 五类受控 derived view，则 COMPLETE 之前额外要求 `DERIVED_MATERIAL_CONTRACT_V1_6_1=PASS`；仅有人工 `DERIVED_CONTRACT_CHECK=PASS` 不再足够。

V1.6.3 若存在 combat_expression_assets，还要求 `COMBAT_SEMANTIC_GATE_V1_6_3=PASS`；并要求 `SUPPLEMENTAL_BATCH_CONSISTENCY_V1_6_3=PASS`。若受控 derived 存在 HOLD，则 manifest 与 batch-status 必须使用 `_WITH_HOLDS`；`batch-status.derived_hold_records` 必须等于真实 HOLD 总数；cluster 只能使用 gate 输出的 PASS record IDs。

SUPPLEMENTAL 的 COMPLETE 只代表“本次授权专项完整”，不得表述为“九维完整拆书”。

