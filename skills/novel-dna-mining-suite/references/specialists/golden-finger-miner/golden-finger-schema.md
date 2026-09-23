# 金手指单书证据包

## JSONL记录

每本书输出一条 `record_type: per_book`：

```json
{
  "schema_version": 1,
  "record_type": "per_book",
  "record_id": "GF:BOOK_01",
  "status": "candidate",
  "book_id": "BOOK_01",
  "title": "书名",
  "chapters_covered": "1-91",
  "mechanic_name_in_book": "原书称呼",
  "normalized_category": "养成类",
  "normalized_archetype": "返祖进化",
  "core_formula": {
    "input": "满足条件的养成对象与材料",
    "process": "触发返祖规则并沿隐藏路线进化",
    "output": "更高血脉、能力或形态"
  },
  "ownership": "主角独有/共享规则中的独有优势/待确认",
  "activation_conditions": [],
  "hard_limits": [],
  "costs": [],
  "failure_modes": [],
  "initial_capabilities": [],
  "growth_stages": [],
  "system_growth_mode": "规则升级/产物累积/混合/UNKNOWN",
  "resource_loop": "资源如何获得、消耗并反哺下一轮",
  "world_dependencies": [],
  "system_interfaces": [],
  "plot_engines": [],
  "reader_promise": "读者最初被承诺会爽在哪里",
  "first_reveal": {"chapter_ref": "BOOK_01:CHAPTER:0001", "event_order": 1, "function": "展示存在"},
  "first_validation": {"chapter_ref": "BOOK_01:CHAPTER:0002", "event_order": 1, "visible_evidence": "规则第一次被证实"},
  "first_strong_payoff": {"chapter_ref": "BOOK_01:CHAPTER:0005", "event_order": 1, "visible_evidence": "收益和反应真正落地"},
  "emotion_pattern": "期待→试错或蓄压→选择→验证→收益余震",
  "emotion_evidence_mode": "overlay/provisional",
  "payoff_evidence_types": [],
  "fatigue_risks": [],
  "refresh_methods_observed": [],
  "evidence_refs": [],
  "qa_sources": [],
  "qa_status": "PASS/HOLD/FAIL",
  "source_numbering_notes": [],
  "unknowns": [],
  "confidence": "MEDIUM"
}
```

## 核心字段说明

### core_formula

必须压缩为 `INPUT → PROCESS → OUTPUT`。输入是触发所需，处理是独有规则，输出是实际得到的能力、资源、信息或状态。

### ownership

区分：

- 主角独有外挂；
- 世界共有机制，但主角拥有独特访问权、效率或信息差；
- 种族天赋被主角用成核心发动机；
- 尚不能确认是否独有。

### hard_limits 与 costs

限制回答“不能做什么或何时失效”；代价回答“使用后要付出什么”。冷却、资源门槛、目标条件、暴露风险和成长上限不能混写成一个空泛的“有限制”。

### growth_stages

每个阶段记录：章节范围、增加了什么规则、解决了什么旧问题、打开了什么新剧情权限、制造了什么新限制。只有数值变大但玩法不变时，标记为数值扩张，不伪装成新阶段。

`system_growth_mode` 必须区分：系统规则新增或扩权、既有规则产物长期累积、两者混合。剧情进入新阶段不自动等于系统升级。

### reader_promise 与 emotion_pattern

金手指不是独立于节奏的设定。必须说明：

- 最初给读者什么期待；
- 何时第一次证实不是噱头；
- 如何通过选择、风险或资源缺口蓄压；
- 用何种可见证据完成兑现；
- 重复几次后会疲劳，原书怎样换验证场景或提高代价。

`emotion_evidence_mode` 为 `overlay` 时，情绪依据来自已通过QA的逐章情绪层；为 `provisional` 时，只是从旧章节拆解中的爽点、信息差、钩子与状态变化临时提取，置信度不得标HIGH。

### evidence_refs

推荐格式：

```text
BOOK_01:CHAPTER_005
BOOK_01:STAGE_02
BOOK_01:EMOTION_005
```

引用BOOK DNA时写 `BOOK_01:BOOK_DNA:<字段>`，但核心机制至少还需要一个章节或阶段证据。

章节证据统一使用展示章号的 `BOOK_ID:CHAPTER:四位数`。源文件分隔段与正文章号错位时，把物理文件和分隔段写入 `source_numbering_notes`，不改写稳定的 `chapter_ref`。

同一章可以先展示、后验证。`event_order` 表示本章内事件顺序，不要求展示和验证落在不同章节。

## 默认输出

- `素材库/DNA素材/02_金手指/per_book/<BOOK_ID>.jsonl`
- `素材库/DNA素材/02_金手指/candidate/clusters.jsonl`
- `素材库/DNA素材/02_金手指/qa/qa_report.md`

未取得写入授权时，只在对话中展示，不创建这些文件。

## 明确缺口记录

目标书没有足够证据时，不省略该书，输出一条：

```json
{
  "schema_version": 1,
  "record_type": "gap",
  "record_id": "GF:GAP:BOOK_01",
  "status": "candidate",
  "book_id": "BOOK_01",
  "reason": "无法确认中后期成长规则",
  "known_evidence": ["仅确认开篇卖点"],
  "unknowns": ["硬限制", "成长阶段"],
  "evidence_refs": ["BOOK_01:CHAPTER:0001"],
  "confidence": "LOW"
}
```

`per_book` 与 `gap` 对同一本书只能出现一种，用于让批次校验判断目标书单是否完整覆盖。

## 置信度

- `HIGH`：核心规则、限制、成长与首次兑现均有明确证据，没有关键UNKNOWN。
- `MEDIUM`：核心规则可靠，但限制、中后期成长或独有性存在缺口。
- `LOW`：只确认卖点或早期表现，无法判断持续循环。
