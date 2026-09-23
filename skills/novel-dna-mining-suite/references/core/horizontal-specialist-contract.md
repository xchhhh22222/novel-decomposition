# 横向专项代理契约

## 单一职责

专项代理只回答一种问题，例如：

- 金手指怎样输入、处理、输出、成长并制造情绪；
- 世界规则怎样持续制造敌人、资源和地图；
- 修炼体系怎样控制成长与剧情权限；
- 人物承担什么功能；
- 主支线如何启动、交汇和阶段收束。

不得因为相关性高而替另一个专项生成母卡。允许记录接口字段，例如金手指依赖什么世界资源，但这些字段只表示依赖，不等于完成世界观拆解。

## 输入包

总控应提供：

```yaml
batch_id:
specialty:
book_ids:
allowed_sources:
chapter_ranges:
emotion_overlay_paths:
output_root:
forbidden_outputs:
known_gaps:
```

专项代理不自行扩大书单或章节范围。

## 输出包

每个专项必须同时交付：

1. `per_book`：每本书一条规范化证据包；证据不足时以同书唯一一条 `gap` 代替；
2. `nearest_neighbor`：每条候选最相近的既有母型或本批候选；
3. `cluster`：大类、母型、子型、变体候选；
4. `qa`：覆盖率、UNKNOWN、证据缺口、争议合并与待确认项；
5. `handoff`：可交给素材整理器审核的候选清单。

以上五类交付均属于专项派生产物；每条派生记录必须含：`record_type`、`schema_version`、`status`、`evidence_refs`、`confidence`。

进入 `nearest_neighbor` 或 `cluster` 前，必须用 completion manifest 证明目标书单中每本书恰好出现一次，且记录类型只能是 `per_book` 或 `gap`。声明完成的布尔字段不能代替 manifest；缺书、重复书、意外书或跨书引用污染均阻断横向聚类。

若专项同时输出由上位 canonical schema 明确定义的权威记录，该记录优先严格服从其 canonical schema，不得为了满足派生 envelope 强行注入未定义字段。当前实例是 `chapter_emotion.jsonl`：它必须服从 `chapter-emotion-schema.md`，不得注入 `record_type`、`evidence_refs`、`unknowns` 等派生字段。这个例外只适用于被上位契约明确定义的 canonical record；专项 Skill 不得自行宣布其它例外。未来新增 canonical record 类型时，也必须先由上位契约明确指定。

## 并发与汇收

- 专项代理可以按书籍分批抽取，但所有批次必须使用同一 schema。
- 工作分片不能共同写一个文件；先写独立分片，再由专项总结合并。
- 聚类在全部目标书抽取完成后进行，不能边看第一本边建立正式母型。
- 子代理完成一个专项后即停止，不继续分析未授权模块。

## 失败条件

- 只根据书名或 BOOK DNA 的一句话卖点判断机制；
- 结论没有章节或阶段证据；
- 用专名差异制造新母型；
- 把单书变体直接当作跨书高频母型；
- 忽略章节情绪层，无法说明机制如何蓄压、兑现和产生余震；
- 输出了本专项以外的正式卡。
