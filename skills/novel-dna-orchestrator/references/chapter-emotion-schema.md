# 逐章读者情绪覆盖层

## 目标

章节拆解回答“发生了什么”，情绪层回答“作者希望读者这一章经历什么，以及用什么证据完成”。情绪层是覆盖文件，不覆盖原章节事实。

## 一章一条 JSONL

```json
{
  "schema_version": 1,
  "record_id": "BOOK_01:EMOTION:0001",
  "status": "candidate",
  "book_id": "BOOK_01",
  "chapter": 1,
  "chapter_ref": "BOOK_01:CHAPTER:0001",
  "chapter_title": "章节标题",
  "evidence_path": "书籍拆解/分类/书名/chapters/001-010.md#第1章",
  "source_fingerprint": "sha256或UNAVAILABLE",
  "chapter_role": ["立承诺", "蓄压"],
  "main_reader_emotion": "紧张",
  "secondary_reader_emotions": ["好奇"],
  "emotion_object": "读者担心主角的隐藏身份暴露",
  "expectation_source": "天敌当面试探且身份暴露会致命",
  "pressure_source": "标准鉴定手段与全城封锁",
  "pressure_level": 4,
  "turning_point": "特殊体质使试探失效",
  "payoff_level": "阶段小兑现",
  "visible_payoff_evidence": ["试探者主动排除怀疑"],
  "aftermath": "更大范围的围剿阻断退路",
  "ending_aftertaste": "短暂脱险后的更大危机",
  "hook_type": "目标宣言",
  "promise_opened": ["当夜吸血突破并逃出封锁"],
  "promise_paid": [],
  "plot_lines_advanced": ["成长线", "身份线"],
  "qa_status": "PASS",
  "confidence": "HIGH",
  "generated_at": "YYYY-MM-DDTHH:MM:SS+08:00",
  "notes": ""
}
```

## 受控字段

### chapter_role

可多选：`立承诺`、`蓄压`、`加压`、`转机`、`兑现`、`余震`、`过渡`、`换档`。

### payoff_level

- `无兑现-继续蓄压`
- `局部兑现`
- `阶段小兑现`
- `本章强兑现`
- `兑现后余震`

### pressure_level

使用0—5：0为轻松或纯余震，5为本阶段最高压力。数值只用于比较同一本书相邻章节，不跨书比较绝对强度。

### 常用读者情绪

紧张、压抑、愤怒、期待、好奇、惊奇、轻松、温暖、心疼、感动、热血、打脸爽、智斗爽、成长爽、收获爽、认可爽、守护爽、掌控爽。

不要为了受控词牺牲准确性；确有必要可使用更具体词，但总索引应映射到最近的受控大类。

## 判断规则

1. 记录读者情绪，不把“主角愤怒”直接等同于“读者愤怒”。
2. 一章只指定一个主情绪；辅情绪最多两个。
3. 没有前置期待时不能标记强兑现。
4. 没有可见反应或状态变化时，升级与击杀最多算事件结果。
5. 过渡章仍需说明它在保存哪项期待、缓解哪种压力或把哪条情绪债推向何时兑现。
6. 章末钩子必须来自真实状态变化、目标、风险或信息缺口，不把机械断章当钩子。
7. `promise_opened` 和 `promise_paid` 用简短可识别短语；同一承诺在后章沿用相同名称，便于追踪情绪债。
8. `(book_id, chapter)` 与 `record_id` 都必须唯一。章节标题层级不统一时，以 `chapter_ref` 为稳定锚点，`evidence_path` 只负责定位文件。
9. `qa_status` 使用 `PASS`、`HOLD`、`FAIL`。HOLD/FAIL记录可以保留，但不计入可用情绪覆盖率，也不能支持高置信专项结论。
10. `source_fingerprint` 优先记录所依据章节块的SHA-256；无法生成时写 `UNAVAILABLE` 并在批次QA中说明，不能虚构哈希。

## 阶段节奏审计

每10章或一个自然阶段检查：

- 是否连续5章以上主情绪和兑现方式高度重复；
- 是否只蓄压不兑现，或连续强兑现导致麻木；
- 已开启承诺是否在合理窗口回收；
- 强兑现后是否有余震；
- 关系、身份、资源、认知或目标是否真的改变；
- 章末钩子是否连续同形。

发现问题只记录审计结论，不反向修改原书事实。
