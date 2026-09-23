# 金手指横向聚类与质检

## 聚类单位

使用三级结构：

`大类 → 母型 → 子型/变体`

- 大类描述主要价值来源，例如复制、选择构筑、信息差、返还、提取、模拟、体质、规则利用。
- 母型描述稳定运行公式。
- 子型改变输入、处理、限制、成长循环或主要情绪中的至少一项。
- 变体只改变题材皮肤、目标对象、资源、表现形式或使用场景。

## 七维比较

每项按 `2=相同、1=部分相同、0=不同`：

1. 输入条件；
2. 核心处理规则；
3. 输出类型；
4. 硬限制与代价；
5. 成长方式；
6. 资源循环；
7. 主要情绪承诺与兑现证据。

总分仅是聚类提示，不代替判断：

- 11—14：优先判断同一母型；
- 7—10：同一大类、不同子型的可能性高；
- 0—6：通常是不同母型。

即使总分高，只要核心处理规则或成长循环实质不同，也不得强行合并。

## 聚类记录

```json
{
  "schema_version": 1,
  "record_type": "cluster",
  "record_id": "GF:CLUSTER:001",
  "status": "candidate",
  "cluster_id": "GF_CANDIDATE_001",
  "category": "信息差类",
  "archetype": "未来情报抢窗",
  "core_formula": {"input": "未来信息", "process": "提前决策", "output": "资源或局势优势"},
  "book_ids": ["BOOK_09", "BOOK_10"],
  "source_count": 2,
  "shared_mechanism": "",
  "subtypes": [],
  "nearest_existing": [],
  "comparison_ids": ["GF:BOOK_09", "GF:BOOK_10"],
  "result_ids": ["GF:ARCHETYPE:FUTURE_INFO"],
  "similarity_score": {
    "input": 0,
    "process": 0,
    "output": 0,
    "limits_costs": 0,
    "growth": 0,
    "resource_loop": 0,
    "emotion_payoff": 0,
    "total": 0,
    "critical_override": ""
  },
  "similarity_decision": "MERGE/SUBTYPE/KEEP_SEPARATE/NEW/SPLIT/HOLD",
  "emotion_pattern": "",
  "payoff_evidence_types": [],
  "world_requirements": [],
  "risks": [],
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM"
}
```

## 支持等级与状态

- 单书出现：默认 `candidate`，只能作为变体或待观察母型。
- 两书独立出现：可以支持母型候选，但仍需查重。
- 三至四书：成熟度较高，不代表适配当前项目。
- 五书以上：高频机制，需重点检查同质化和疲劳风险。

来源书数只表示跨书验证，不代表商业价值。

### 决策含义

- `MERGE`：同一母型，合并证据或变体。
- `SUBTYPE`：同一母型下，输入、限制或兑现形成稳定子型。
- `KEEP_SEPARATE`：同属一个大类且互为近邻，但核心处理或成长循环不同，应保留为并列母型。
- `NEW`：与现有大类/母型都没有合理归属的新机制候选。
- `SPLIT`：已有候选混合了两个可独立运行的机制。
- `HOLD`：证据或边界不足。

七维分数必须写入 `similarity_score`。当核心处理规则或成长循环构成决定性差异时，在 `critical_override` 说明为何不能仅按总分合并。

`comparison_ids` 说明本次究竟比较了哪些单书包或既有母型；`result_ids` 说明执行决策后归入哪些候选母型。`KEEP_SEPARATE` 与 `SPLIT` 至少需要两个 `result_ids`，否则不能表达“分别放到哪里”。

## 质检

逐项检查：

- 目标书单是否全部覆盖；
- `input/process/output`是否具体；
- 独有性、限制、成长和资源循环是否有证据；
- 首次展示、验证、强兑现是否区分；
- 情绪链是否来自逐章证据；
- 是否把题材皮肤当成机制差异；
- 是否给出最近邻而不是直接宣布NEW；
- 是否误写了世界观或人物正式卡；
- HIGH记录是否包含关键UNKNOWN。
- QA结论是否覆盖声明的全部章节范围；分散在多个文件时是否按批次合并；
- 缺章与章号偏移是否写入 `source_numbering_notes`；
- 是否把产物累积误写成系统规则升级。

任何核心规则无法核实的记录改为 `HOLD`，不为凑齐16本而补造。
