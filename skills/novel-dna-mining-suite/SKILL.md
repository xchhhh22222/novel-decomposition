---
name: novel-dna-mining-suite
description: V1.6 小说 DNA 拆解套件：保留完整主书 FULL_DNA 流程，并新增 SUPPLEMENTAL_MATERIAL 中控路由；先判断一本来源为什么入库，再只调用被授权的专项与派生视图。所有专项继续来源可追溯、candidate-only。
---

# 小说 DNA 拆解套件 V1.6

这是一个独立迁移包，入口负责路由和边界，详细规则按需读取 `references/`。不要把候选直接写成正式套路卡，也不要修改源章节或正式素材库。

## 路由

- **任何新增来源书开始前，必须先读取 `references/core/source-role-and-routing.md`，确定 `FULL_DNA` 或 `SUPPLEMENTAL_MATERIAL`。**
- **若为 SUPPLEMENTAL_MATERIAL，再读取 `references/core/supplemental-profiles.md` 选择 Profile；未经用户确认 routing matrix，不开始正式拆解。**
- 总控、输入包、目录、阶段门和总索引：读取 `references/core/`。
- 章节情绪：读取 `references/specialists/chapter-emotion-miner/`，canonical 章节字段唯一服从 `references/core/chapter-emotion-schema.md`。
- 金手指：读取 `references/specialists/golden-finger-miner/`。
- 世界观：V1.4 同时拆世界规则与 `factions` 势力生态。
- 修炼体系：V1.4 按来源实际存在数量拆 `cultivation_systems / system_relations / techniques / artifacts / resource_assets`，不预设体系数量。
- 人物功能、主支线、开篇、篇章结构、剧情机制：按模块读取对应 specialist 目录的 guidance/schema/QA。
- **人物个体卡为 V1.5 必跑派生层**：每本书在人物功能完成后，额外调用 `novel-character-card-miner`；女主/关键女性写 heroine_character 或明确 gap，长线反派写 long_arc_villain 或明确 gap。禁止用人物功能标签冒充人物个体卡。
- 统一校验：运行 `python scripts/validate.py --specialty <slug> --kind <kind> ...`；该入口只分派包内 validator，不依赖外部 Skill。
- V1.5.1 语义门：章节情绪结构校验后运行包内 `scripts/specialists/chapter-emotion-miner/audit_semantics.py`；剧情线运行 `audit_recall.py`；剧情机制运行 `audit_depth.py`；manifest 落盘前运行 `scripts/core/validate_module_status_consistency.py`。\n- V1.5.2 语义加固：RAW_ENDING 过滤纯标点/过短尾句；模板骨架支持从人物卡、人物功能或显式实体表读取已知中文实体并归一化为 `<ENTITY>`，避免仅替换人名绕过模板检测。

## 统一不变量

- 中控只决定“调用哪些 specialist”，不改变 specialist 自己的 schema / QA / validator。
- FULL_DNA 仍按原完整主书流程执行；SUPPLEMENTAL_MATERIAL 只要求 target_specialties 完整，不要求九专项全部运行。
- SUPPLEMENTAL_MATERIAL 仍必须扫描授权 chapter_scope 的全部正文以保证目标专项 recall；不得把“专项拆解”误解成“随便抽几章”。
- 未授权专项必须显式列入 excluded_specialties，不能静默省略。
- BOOK_ID 继续使用 BOOK_010、BOOK_011...；用 source_role / extraction_mode 区分补充来源，避免破坏现有脚本。
- 输入必须由总控冻结：`batch_id`、`specialty`、`book_ids`、`allowed_sources`、`chapter_ranges`、`emotion_overlay_paths`、`output_root`、`forbidden_outputs`、`known_gaps`。
- 派生记录固定 `status: candidate`；不得生成 `active`、`deprecated` 或正式素材卡。
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
→ COMPLETE_SUPPLEMENTAL_SOURCE
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

SUPPLEMENTAL 的 COMPLETE 只代表“本次授权专项完整”，不得表述为“九维完整拆书”。

