---
name: novel-dna-mining-suite
description: 可迁移的小说 DNA 拆解套件，统一编排章节情绪、金手指、世界观、修炼体系、人物功能、主支线、开篇、篇章结构、剧情机制与总索引；所有专项候选保持可追溯、candidate-only，并通过统一 validator 阶段门交接。
---

# 小说 DNA 拆解套件

这是一个独立迁移包，入口负责路由和边界，详细规则按需读取 `references/`。不要把候选直接写成正式套路卡，也不要修改源章节或正式素材库。

## 路由

- 总控、输入包、目录、阶段门和总索引：读取 `references/core/`。
- 章节情绪：读取 `references/specialists/chapter-emotion-miner/`，canonical 章节字段唯一服从 `references/core/chapter-emotion-schema.md`。
- 金手指：读取 `references/specialists/golden-finger-miner/`。
- 世界观、修炼体系、人物功能、主支线、开篇、篇章结构、剧情机制：按模块读取对应 specialist 目录的 `guidance.md`、`schema.md` 和 `clustering-and-qa.md`。
- 统一校验：运行 `python scripts/validate.py --specialty <slug> --kind <kind> ...`；该入口只分派包内 validator，不依赖外部 Skill。

## 统一不变量

- 输入必须由总控冻结：`batch_id`、`specialty`、`book_ids`、`allowed_sources`、`chapter_ranges`、`emotion_overlay_paths`、`output_root`、`forbidden_outputs`、`known_gaps`。
- 派生记录固定 `status: candidate`；不得生成 `active`、`deprecated` 或正式素材卡。
- 每条抽象结论必须带结构化 `evidence_refs`；证据不足保留 `UNKNOWN`、`partial`、`gap` 或 `HOLD`。
- 单书覆盖必须是每本恰好一条 `per_book` 或 `gap`；跨书 `nearest_neighbor/cluster` 必须提供 `--expected-books`、`--all-books-complete` 和 `--completion-manifest`。
- `arcs[]` 与 `mechanisms[]` 分别承载一本书的多个篇章阶段和多个剧情机制，不能只保留代表性单条记录。
- 章节情绪 canonical 记录不得追加派生 envelope；情绪 validator 必须同时检查包内权威 validator 的契约一致性。
- 未获得用户明确授权，不落盘到正式素材库；默认输出目录和写入归属见 `references/core/library-layout.md`。

## 交付顺序

先完成章节事实与情绪覆盖，再运行单书专项；全部目标书完成单书 QA 后才能跨书比较。最后用 `scripts/core/build_master_index.py` 构建导航索引，索引只引用路径和 ID，不复制长内容。
