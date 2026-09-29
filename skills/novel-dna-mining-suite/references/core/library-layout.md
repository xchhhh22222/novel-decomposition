# 小说 DNA 素材层级与存放位置 V1.6

## 设计原则

现有 `书籍拆解/`、`00_BOOK_DNA/` 和 `套路素材/` 继续保留。新增 DNA 层不覆盖它们，而是在 `素材库/DNA素材/` 下建立可迁移、可审计的中间层。

## 推荐目录

```text
素材库/
├─ 书籍拆解/                    # 已有证据层，不因新流程批量重写
├─ 00_BOOK_DNA/                 # 已有单书综合画像
├─ DNA素材/
│  ├─ 00_任务清单/              # 批次、书单、范围、状态和缺口
│  ├─ 01_章节情绪/              # 每本书一份 chapter_emotion.jsonl
│  ├─ 02_金手指/
│  │  ├─ per_book/              # 单书规范化证据包
│  │  ├─ candidate/             # 横向母型、子型、变体候选
│  │  └─ qa/                    # 覆盖与聚类质检
│  ├─ 03_世界观/
│  ├─ 04_修炼体系/
│  ├─ 05_人物功能与标签/
│  ├─ 06_主线与支线/
│  ├─ 07_开篇/
│  ├─ 08_篇章结构/
│  ├─ 09_剧情机制/
│  └─ 10_总索引/
│     ├─ DNA总索引.md
│     ├─ DNA检索索引.jsonl
│     └─ 缺口与待定项.md
└─ 套路素材/                    # 经过人工确认的正式原子卡
```

`03_世界观` 至 `09_剧情机制` 与 `02_金手指` 使用同一层级约定：单书包进入 `per_book/`，跨书近邻与聚类进入 `candidate/`，质量报告进入 `qa/`。机器可读 `handoff` 可以放在 `candidate/` 下或专项根目录，但不得放入 `per_book/` 冒充单书证据。总索引按 `record_type` 区分这些记录，而不是把目录中的所有 candidate 状态文件都计作聚类候选。

## V1.6 来源角色

同一 `BOOK_xxx` ID 体系继续使用，但每本新来源必须通过 metadata 区分：

- `source_role: primary_full_dna`
- `source_role: supplemental_material`

并记录：

- `extraction_mode`
- `purpose[]`
- `target_specialties[]`
- `derived_views[]`
- `excluded_specialties[]`
- `chapter_scope`
- `full_book_dna`

SUPPLEMENTAL 只创建真正运行的专项目录；不要为了目录齐全创建七个空专项。

例如能力补充书：

```text
books/BOOK_010/
├─ 00_给用户看的专项素材报告.md
├─ 02_金手指/
│  ├─ per_book/
│  ├─ derived/ability_assets.jsonl
│  └─ qa/
├─ 04_修炼体系/
│  ├─ per_book/
│  ├─ derived/combat_asset_inventory.json
│  ├─ derived/combat_expression_assets.json
│  ├─ derived/non_protagonist_combat_coverage.json
│  └─ qa/
├─ 09_剧情机制/
│  ├─ per_book/
│  └─ qa/
├─ manifest.json
└─ qa/
```

未运行专项由 source_route 的 `excluded_specialties` 解释，不以空目录表示。

## 状态分层

- `evidence`：原文、章节事实、经确认的阶段事实。
- `candidate`：专项代理生成、尚未通过正式入库审核的抽象结果。
- `active`：经过来源、去重、情绪和原子性审核，可正式检索调用。
- `deprecated`：保留来源链但不再调用。

目录位置不能代替状态字段。每条候选仍需在 frontmatter 或 JSON 记录中声明 `status`。

## source_route 建议位置

每批新增来源建议在任务根目录保存：

```text
00_任务清单/source_routes.jsonl
```

每本一条。正式拆解前先运行 routing validator；路由修改应在正式 per_book 输出前完成。

## 任务清单字段

每批任务至少记录：

任务清单使用 JSONL，一本书一条，便于脚本读取：

```json
{
  "record_type": "book_scope",
  "batch_id": "DNA_YYYYMMDD_01",
  "book_id": "BOOK_01",
  "source_scope": "现有拆解成果",
  "target_range": "1-91",
  "excluded_chapters": [],
  "source_missing_chapters": [],
  "qa_status": "PASS",
  "market_grade": "UNGRADED",
  "specialists": ["golden_finger"],
  "emotion_overlay": "pending",
  "known_gaps": []
}
```

市场等级不能从书名、拆解篇幅或代理主观印象推导。榜单数据缺失时统一使用 `UNGRADED`。

`excluded_chapters` 表示不在本次任务范围内；`source_missing_chapters` 表示本应存在但源文缺失。两者不得混用。

## 写入归属

- 章节情绪代理只写自己书籍的 `chapter_emotion.jsonl` 草稿分片。
- 专项代理只写自身目录下的 `per_book/` 和 `candidate/`。
- 总控只写任务清单、总索引和缺口表。
- `套路素材/` 只由正式入库流程写入。


## V1.6.1 Derived canonical layout

五类受控 supplemental derived view 固定路径：

```text
02_金手指/derived/ability_assets.jsonl
03_世界观/derived/dungeon_rule_assets.jsonl
04_修炼体系/derived/combat_expression_assets.json
05_人物功能与标签/derived/relationship_engine_assets.jsonl
05_人物功能与标签/derived/charismatic_antagonist_assets.jsonl
```

不得因代理不同改名为 `ability.jsonl`、`relationship_engines.jsonl` 或其它临时文件名。

combat_expression_assets.json 顶层必须是 schema_version=2 的 collection，`assets` 为一维数组并带 `asset_count`。

其余四类为 JSONL，一行一条 derived_asset。

具体字段与 ID 服从 `derived-material-contract.md`。Manifest 的 `outputs.derived_views[].records` 必须等于 canonical 文件实际条数。
