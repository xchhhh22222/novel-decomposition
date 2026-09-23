# 小说 DNA 素材层级与存放位置

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
│  ├─ 05_人物功能与标签/     # derived/heroine 与 derived/long_arc_villain 分库
│  ├─ 06_主线与支线/
│  ├─ 07_开篇/
│  ├─ 08_篇章结构/          # derived/major_storyline 为大故事线候选库
│  ├─ 09_剧情机制/
│  └─ 10_总索引/
│     ├─ DNA总索引.md
│     ├─ DNA检索索引.jsonl
│     └─ 缺口与待定项.md
└─ 套路素材/                    # 经过人工确认的正式原子卡
```

## 状态分层

- `evidence`：原文、章节事实、经确认的阶段事实。
- `candidate`：专项代理生成、尚未通过正式入库审核的抽象结果。
- `active`：经过来源、去重、情绪和原子性审核，可正式检索调用。
- `deprecated`：保留来源链但不再调用。

目录位置不能代替状态字段。每条候选仍需在 frontmatter 或 JSON 记录中声明 `status`。

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
