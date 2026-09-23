# 原子素材卡规范 v3

仅在新增、迁移、合并或审核素材卡时读取本文件。

## 设计目标

- 一卡一机制；卡片负责解释“事件怎样制造情绪”，紧凑索引负责召回。
- 机器可筛选字段放在 frontmatter，长证据与辨析放在正文。
- 不为填字段编造内容；不确定值写 `待确认` 或空数组。
- 新卡正文建议控制在800—1800个汉字。复杂来源辨析可以更长，但不得重复解释同一结论。

## Frontmatter

~~~yaml
---
schema_version: 3
card_id: TR_BATTLE_031
name: 借环境机关分割怪潮
primary_module: 战斗
secondary_modules: [学校, 钩子]
story_functions: [环境破局, 团队协作, 积分反超]
emotion_targets: [紧张, 智斗爽, 团队认可]
emotion_functions: [蓄压, 兑现, 余震]
applicable_stages: [开局成长期, 校园试炼]
preconditions: [存在可验证的环境机关, 敌群可被地形分割]
emotion_preconditions: [读者已知道队伍积分落后, 队友曾质疑旧机关能否使用]
forbidden_when: [机关来源无法解释, 主角未获得相关信息]
agency_type: 主动布局
payoff_types: [智斗爽, 效率爽, 团队认可]
payoff_latency: 本章兑现
tension_shape: 围困加压→分工冒险→机关反杀
payoff_evidence: [公开积分反超, 队友主动服从下一次指挥]
aftermath_types: [队内信任升级, 竞争者重新定价主角]
hook_types: [战果结算, 异常线索]
tags: [环境机制, 怪潮, 分割战场, 团队分工]
summary: 主角用已铺垫的环境机关分割怪潮，以高风险分工换取批量清场和可见战果。
support_level: C
source_book_count: 1
source_occurrence_count: 1
status: active
---
~~~

### 必填字段

v3必填：`schema_version`、`card_id`、`name`、`primary_module`、`story_functions`、`emotion_targets`、`emotion_functions`、`applicable_stages`、`preconditions`、`emotion_preconditions`、`agency_type`、`payoff_types`、`payoff_latency`、`tension_shape`、`payoff_evidence`、`aftermath_types`、`tags`、`summary`、`support_level`、`source_book_count`、`source_occurrence_count`、`status`。

现有v1/v2卡继续有效，按收益渐进迁移；不得因为缺少v3字段而批量推断或回写情绪信息。

### 字段约束

- `summary`：一句话，建议不超过120个汉字，包含触发、行动与兑现。
- `story_functions`：作者层功能，不写具体人物名。
- `emotion_targets`：希望读者实际产生的情绪，优先使用受控词，如紧张、压抑、热血、感动、心疼、轻松、惊奇、打脸爽、智斗爽、成长爽、收获爽、认可爽、守护爽、掌控爽。
- `emotion_functions`：该机制在情绪链中的位置，使用 `蓄压`、`加压`、`转机`、`兑现`、`余震` 中的一项或多项。
- `preconditions`：缺一即不能使用的条件。
- `emotion_preconditions`：情绪成立前读者必须已经看见或相信什么，例如持续低估、明确损失、未兑现承诺或关系裂痕。
- `forbidden_when`：会造成逻辑破坏、降智或越级的禁用条件。
- `agency_type`：优先使用 `主动布局`、`主动选择`、`被迫应对后反制`、`被动获益`。被动获益卡必须明确补足主动性的组合建议。
- `payoff_latency`：`本章兑现`、`1—3章兑现`、`阶段兑现`、`整卷兑现`。
- `tension_shape`：用箭头写出蓄压、转机、兑现的顺序，不只列事件。
- `payoff_evidence`：读者能直接观察到的兑现证据，不能只写“很爽”“震惊众人”。
- `aftermath_types`：兑现后留下的关系、认知、资源、身份、目标或风险变化。
- `status`：`active`、`candidate`、`deprecated`、`merged`。`merged` 必须指明归并目标。
- `support_level`：S=至少5本，A=3—4本，B=2本，C=1本；无可靠来源时用 `candidate` 状态，不虚构书数。

模块沿用项目现有六域：`升级`、`资源`、`学校`、`战斗`、`人物关系`、`钩子`。新域只有在至少三张独立卡无法归入现有域时才考虑增加。

情绪不是第七模块，而是横跨六域的检索维度。标签继续描述题材与机制细节，不用大量近义情绪词制造一次性标签。

## 正文模板

~~~markdown
# 套路名称

## 抽象机制
用150—300字说明：由什么触发，主角做什么，阻力如何升级，最终通过哪些可见证据兑现目标情绪。

## 情绪链
1. 读者期待从哪里产生；
2. 怎样蓄压或加压；
3. 何时给出转机；
4. 用什么人物反应、公开结果或代价回响完成兑现；
5. 兑现后留下什么余震。

## 最小事件链
1. 触发与目标；
2. 主角选择及代价；
3. 阻力升级；
4. 局部或最终兑现；
5. 后续状态变化。

## 组合接口
- 适合作为主机制：
- 可搭配的辅助机制：
- 可搭配的钩子：

## 迁移轴
列出至少三个需要在新作品中重设的要素。

## 失败条件与重复风险
说明何时会降智、空转、越级或与现有卡重复。

## 来源证据
- 《书名》章节范围：只写支持该抽象机制的简述。
~~~

## 原子性判定

用三个问题判断是否应拆卡：

1. 两部分能否在不同章节独立成立？能则倾向拆分。
2. 两部分是否拥有不同触发、主角目标或爽点来源？是则必须拆分。
3. 去掉其中一部分后，另一部分仍是完整因果链吗？是则拆分。
4. 两部分服务的主情绪或兑现证据完全不同吗？是则优先拆分。

同一机制只有地图、敌人或名词变化时不新建；补入原卡的来源证据与变体即可。
