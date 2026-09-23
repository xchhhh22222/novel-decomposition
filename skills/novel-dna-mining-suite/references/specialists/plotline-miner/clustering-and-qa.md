# 剧情线专项 QA 与跨书比较规则

## 1. 适用范围与质量目标

本文件只定义 `novel-plotline-miner` 的单书线路识别 QA、九段生命周期 QA、父子线一致性 QA、节奏疲劳 QA 和跨书比较规则，不新增或修改 `schema.md` 字段，也不替代上位总控和相邻专项的正式业务判断。

所有判断必须同时遵守：

- `../../../SKILL.md`；
- `../../core/horizontal-specialist-contract.md`；
- `../../core/integration-and-qa.md`；
- `guidance.md`；
- `schema.md`。

QA 的目标不是把章节事件串得更长，而是确认：

1. 线路确实由实际事件、目标、阻力和证据启动；
2. 九段生命周期的每一段承担独立作用；
3. 节点、选择和代价会真实改变线路推进；
4. payoff 能回溯到前置目标、承诺或未决问题；
5. state_change 与 next_entry 不是 payoff 的重复描述；
6. 父子线关系有真实服务、阻碍或改变证据；
7. 跨书比较的是线路运行结构和生命周期，而不是复仇、考试、升级或救人等题材名称；
8. 所有结果仍是 `candidate`，不写正式线路资料或素材库。

## 2. QA 结果与证据分级

### 2.1 单项结果

每项检查使用：

- `PASS`：证据充分，结构和边界清楚，可以作为当前范围内的 candidate 继续流转；
- `HOLD`：存在关键缺口、争议或边界不清，保留 `UNKNOWN`、`partial` 或 `gap`；
- `FAIL`：存在虚构触发/目标/兑现、事件冒充线路、生命周期矛盾、父子线循环、跨书阶段门违规或相邻专项越界。

`HOLD` 不等于线路不存在，只表示当前证据不足以支撑更强的生命周期判断。`FAIL` 不得支撑高置信近邻或聚类。

### 2.2 置信度规则

- `HIGH`：九段核心链条、关键生命周期结局、父子线关系和跨专项接口均有章节/阶段证据，且没有会改变结论的关键 `UNKNOWN`；
- `MEDIUM`：线路核心推进可追溯，但部分代价、兑现后的状态或下一入口仍需人工确认；
- `LOW`：只能确认事件或局部目标，无法确认稳定线路、完整生命周期或兑现关系。

以下情况不得使用 `HIGH`：

- 线路主要来自书名、简介、题材标签、章节标题、人物名字或模型记忆；
- `trigger` 只有背景首次出现，没有实际启动/唤醒事件；
- `goal` 只有“变强”“复仇”“活下去”等抽象词，没有当前边界和成功条件；
- `resistance` 只是敌人、困难或场景列表，没有改变推进、资源、信息、风险或选择的后果；
- `node` 缺少 `before_state` 或 `after_state`；
- `choice` 没有真实替代路径或取舍；
- `cost` 只是普通损耗、受伤、战斗结果或剧情推进，没有与选择/推进的因果联系；
- `payoff` 无法回溯到 prior goal、promise 或 unresolved question；
- `state_change` 只是重复 payoff，或 `next_entry` 由作者后续剧情倒推而没有状态变化证据；
- `line_lifecycle` 的 paid、failed、abandoned、paused 或 redirected 缺少对应依据；
- 父子线关系只有共享人物、地点或敌人，没有服务/阻碍/改变证据；
- 全部目标书尚未完成单书 QA，却已经生成跨书结论。

## 3. 第一层：单书线路识别 QA

### 3.1 输入范围与来源冻结

开始单书 QA 前必须确认：

- 目标 `book_id`、章节/阶段范围和允许来源由 orchestrator 冻结；
- 覆盖范围、分片边界、已知缺口和禁止输出已登记；
- 没有把书名、简介、人物目录、章节标题或模型记忆当作未声明证据；
- 情绪 overlay 只是已有接口，不被重写成线路状态；
- 多书批处理的书籍和分片互不重叠。

范围不通过时只能输出 `HOLD` 或 `gap`，不得继续生成高置信线路或跨书聚类。

### 3.2 line identity 与真实 trigger

逐条检查 `line_identity` 和 `trigger`：

- `line_id` 是否只用于定位，没有被专名或题材标签代替；
- `actual_start_event` 是否是实际启动或唤醒线路的事件、承诺、危机、任务、关系变化或资源门槛；
- 背景设定第一次出现是否被误当成 line started；
- 线路重新出现时，是否有 reopen、阶段重启或新的触发证据；
- 是否因事件很多、人物出场多或章节跨度长就自动判定线路存在。

“背景首次出现 ≠ 线路开始”。只有实际目标、承诺、危机、任务接入或行动约束被启动，才可能通过 trigger QA。

### 3.3 goal 与 resistance

检查 `goals`：

- `goal_statement` 是否是当前可追踪的目标；
- `subject`、`phase_scope` 和 `success_condition` 是否明确；
- 是否把抽象愿望直接写成完整线路目标；
- 目标变更时，是否根据证据判断为同线 `redirected`、新阶段、父子线或新线路，而不是机械拆分或强行合并；
- `goal_status` 是否与线的生命周期区分。

检查 `resistances`：

- 阻力是否确实妨碍目标或迫使线路改变路径；
- 敌人存在是否真的造成推进、资源、信息、风险或选择变化；
- 阻力是否在后续重复、升级、转移或改变形态；
- 是否把某个角色的功能、世界规则、修炼门槛或金手指效果完整复制进线路记录，而不是保留接口。

敌人存在 ≠ 有效阻力。只有实际改变线路推进，才能作为 resistance。

## 4. 第二层：九段 lifecycle 有效性 QA

### 4.1 trigger / goal / resistance

九段前置链必须成立：

`trigger → goal → resistance`

触发必须解释为什么现在开始；目标必须解释当前要达成什么；阻力必须解释什么持续阻止目标。任何一段只有抽象词或背景名词，都使用 `HOLD` 或 `gap`。

### 4.2 nodes

每条 `node` 必须具备：

- `before_state`：节点前线路、人物、目标、资源、信息、关系、风险或权限状态；
- `node_event`：实际造成改变的事件或行动；
- `after_state`：节点后真实变化；
- `line_effect`：变化如何影响目标、阻力、选择、代价、兑现或下一入口；
- `evidence_refs`：可回溯到章节或阶段。

普通事件、移动、重复训练、无后果对话、背景说明和连续战斗过程不能为了填满结构而全部升级为 node。连续大量 node 但 goal、状态和推进没有变化，属于假节点堆积风险。

### 4.3 choices

每条 `choice` 必须检查：

- 是否存在真实可选路径、不同目标优先级或风险取舍；
- `chosen_action` 是否是人物或主角实际作出的行动；
- `rejected_or_foregone_alternative` 即使为 `UNKNOWN`，也不能让 `available_paths` 变成空泛列表；
- `choice_effect` 是否改变后续目标、阻力、资源、风险、关系、身份或线路方向；
- 被迫执行唯一动作、作者直接替人物决定的结果或单纯战斗动作是否被误写成 choice。

被迫执行唯一动作 ≠ 真实 choice。

### 4.4 costs

每个代价都要能回答“它由哪个选择、节点或推进动作造成，并如何影响后续”：

- 普通损耗、战斗受伤、奖励减少或场景结束不能自动成为选择代价；
- 代价可落在资源、关系、身份、风险、信息、时间、机会、债务或其它可观察维度；
- 线路存在选择但当前没有可观察代价时，`costs` 可以为空或 `UNKNOWN`，不能强制造价；
- 连续选择都没有任何后续代价，是线路平衡和重复风险，不应靠补写抽象心理代价解决。

### 4.5 payoff

每条 `payoff` 必须核验：

- 是否有 prior goal、promise 或 unresolved question；
- `payoff_result` 是否确实对应前置对象；
- `payoff_state` 是否区分 paid、partial、failed 和 UNKNOWN；
- 升级、击杀、战斗胜利、资源到账或高潮发生是否被错误自动算成 payoff；
- 没有前置目标、承诺或未决问题时，是否错误地声称已经兑现。

普通结果 ≠ payoff。升级、击杀、胜利或资源到账只有在真实完成线路前置目标时，才可能成为 payoff 的一部分。

### 4.6 state_change 与 next_entry

检查 `state_changes`：

- 是否来自 payoff 或失败，而不是重复描述 payoff；
- `changed_domains` 是否落到目标、关系、资源、身份、认知、风险、局势或行动权限；
- `before_state` 与 `after_state` 是否能观察到实际差异；
- 是否把下一入口偷塞进 `after_state` 而没有说明状态改变。

检查 `next_entries`：

- `source_state_change_id` 是否真实存在；
- 打开的目标、阻力、任务、选择或子线是否由该状态变化产生；
- 是否有章节/阶段证据；
- 是否由作者后续剧情倒推一个当前并未打开的入口；
- 是否把 payoff 原文重复写成 next entry。

`payoff → state_change → next_entry` 是连续但独立的三步。多次 payoff 后没有 state_change，或 state_change 后没有 next_entry 却声称线路继续推进，必须进入 `HOLD` 或疲劳风险。

## 5. 第三层：生命周期、父子线与跨章一致性 QA

### 5.1 生命周期状态

逐条检查 `line_lifecycle`：

- `not_started → active` 必须有 trigger；
- `paused` 必须有暂停依据，不能因为暂时没出现就判暂停；
- `redirected` 必须有目标、阻力、方向或成功条件的实质变化；
- `paid` 必须有合法 payoff；
- `failed` 必须有目标失败、不可达或明确失败结果证据；
- `abandoned` 必须有主动或明确放弃证据；
- `UNKNOWN` 可以保留，不得用猜测代替；
- 暂时没有后续章节不等于 failed 或 abandoned；
- 已 paid、failed 或 abandoned 的线路若重新推进，必须判断是 reopen、新阶段还是新线路，不能无解释复活。

成功兑现、失败收束和主动放弃必须保持不同状态。任何把三者压成 `closed` 的记录都应 `FAIL`。

### 5.2 父子线关系

逐条检查 `parent_child_relations`：

- child 是否说明如何 `service`、`obstacle` 或 `change` parent；
- child paid ≠ parent paid；
- child failed ≠ parent failed；
- parent paused ≠ child 自动 paused；
- 子线若完全不改变父线，要重新核验它是否真的应该挂为 child；
- 不允许循环父子引用；
- 同一 line 不能成为自己的 parent 和 child；
- 共享人物、地点、敌人或资源不能单独证明父子关系；
- 子线完成可以只是父线的节点、代价、资源入口、信息入口或 next entry。

父线和子线的目标、阻力、节点、代价、兑现和生命周期必须分别取证，不得把父线结论批量传播给子线。

### 5.3 跨章状态连续性

跨章节检查：

- 线路状态是否与前一节点、选择、代价或兑现的结果相容；
- 已被证据证明失效的目标、阻力或状态是否仍被无条件使用；
- 线路转向是否有明确节点或选择，而不是章节跳跃；
- 代价是否在后续兑现或产生约束，而不是写完即消失；
- next entry 是否真正进入后续目标/阻力/选择；
- 线路暂停、失败或放弃后是否有合法重启或新线证据。

## 6. 剧情线节奏与疲劳 QA

在单书 QA 中额外检查：

- 长时间只有 resistance，没有 node、choice 或 state_change；
- 连续大量 node，但 goal 未变化、状态未变化或没有线路推进；
- 连续 choice 没有真实代价，选择只改变措辞不改变后果；
- payoff 长期缺失，但线路不断加压、追加敌人或扩大任务；
- 多次 payoff 后没有 state_change，兑现没有改变人物、关系、资源、身份、认知、风险或目标；
- state_change 后没有 next_entry，线路却继续推进或反复制造同一悬念；
- 多条子线不断开启但不回收、不反哺父线，也不改变父线状态；
- 同类“任务 → 战斗 → 奖励”线路反复出现，但触发、阻力、选择、代价和兑现方式没有变化；
- 线路越来越多，但主角目标、资源、风险、认知、关系或行动窗口没有同步变化；
- 线路名称更换却没有目标、生命周期或运行结构的真实差异。

疲劳 QA 不要求每条线路都完全独特，而要求差异能落到触发、阻力维持、节点类型、选择空间、代价、兑现回收、状态变化或下一入口。无法区分时标记 `HOLD`、`insufficient_evidence` 或建议合并候选，不强行增加线路数量。

## 7. 第四层：跨书 nearest-neighbor / clustering QA

### 7.1 跨书阶段门

只有同时满足以下条件，才允许生成 `nearest_neighbor` 或 `cluster`：

1. 所有目标书和冻结章节范围均已处理；
2. 每本书都有 `per_book` 或明确的 `gap`；
3. 每本书的单书和生命周期 QA 已完成；
4. 关键线路没有未标记的 `FAIL`；
5. 输入书籍和分片互不重叠；
6. 未用其它书的线路事实替代缺口书；
7. cross-book completion gate 已明确通过。

任一目标书尚未完成时，只能保留单书 candidate、`gap` 或 `HOLD`，不得先行聚类。

### 7.2 nearest-neighbor 比较维度

近邻必须比较：

- line 如何启动；
- goal/resistance 如何形成和维持；
- node 如何改变状态、方向、门槛、信息或阶段；
- choice/cost 如何制造真实分叉和后续约束；
- payoff 如何回收前置目标、承诺或未决问题；
- state_change 如何滚入 next_entry；
- parent-child 线路如何组织；
- redirected、failed、abandoned、paused 等生命周期如何处理。

每条 `nearest_neighbor` 必须同时提供：

- 相似运行点；
- 关键差异和边界；
- 支撑相似与差异的 `evidence_refs`；
- `decision`：`merge_candidate`、`keep_distinct` 或 `insufficient_evidence`。

以下表面相似不能单独生成近邻：

`复仇线 / 考试线 / 救人线 / 比赛线 / 升级线 / 学院线 / 感情线`

如果相同名称背后的九段运行结构、生命周期结局、状态变化或父子线组织不同，必须 `keep_distinct`。

### 7.3 cluster 聚类规则

聚类必须从已通过单书 QA 的运行结构中提炼：

- `shared_operation`：线路如何触发、形成目标/阻力、制造节点/选择/代价并兑现；
- `payoff_state_entry_pattern`：兑现、状态变化和下一入口如何连续滚动；
- `parent_child_pattern`：父线/子线如何组织和保持边界；
- `boundary_conditions`：与相近候选保持区分的条件；
- 生命周期如何区分成功、失败、放弃、暂停和转向。

允许以下结果：

- `unclustered`：证据不足或运行结构不能稳定归类；
- `insufficient_evidence`：只有表面题材相似，缺少生命周期证据；
- `HOLD`：存在状态冲突、父子线争议、缺口或相邻专项职责冲突；
- candidate cluster：运行结构已经能够描述，但仍等待人工审核。

不强制凑簇。QA 未通过的书或线路不能支撑 `HIGH` cluster；所有 cluster 仍为 `candidate`，不写正式素材库。

## 8. QA 记录与人工交接

QA 结果应回填 `schema.md` 规定的 `qa` 记录字段，不新增平行字段。至少保留：

- 输入范围、覆盖情况和来源冻结检查；
- trigger/goal/resistance 的有效性；
- node 的 before/after 状态变化；
- choice 的真实替代路径与 cost 因果；
- payoff 的 prior goal/promise/unresolved question；
- state_change/next_entry 的独立性和证据；
- line_lifecycle 的状态连续性；
- parent-child 的传播边界和循环检查；
- 节奏/疲劳风险；
- 相邻专项 interface/evidence 边界；
- 跨书阶段门、相似运行点、差异边界和 blocked outputs。

无法解决的判断交给 `handoff`：保留候选线路、关键证据、争议点、边界警告、缺口和建议动作。QA 不修改源章节，不修改线路正式资料，不升级状态，不写正式素材库。

## 9. 禁止将 QA 变成关键词规则

本文件提供的是证据判断边界，不允许仅凭关键词自动推断：

- 看见“任务”就判 trigger 或完整 plotline；
- 看见“敌人”就判 resistance；
- 看见“战斗”就判 node、choice 或 payoff；
- 看见“升级”“击杀”“胜利”“拿资源”就判 payoff；
- 看见“暂停很久”就判 failed 或 abandoned；
- 看见“后来合作”就判 redirected 或 paid；
- 看见相同题材名称就判跨书相似；
- 看见子线共享人物、地点或敌人就判 parent-child。

后续 validator 只应检查可结构化的硬约束，例如字段存在、状态和枚举、证据引用、九段结构、payoff 前置对象、before/after、父子线自引用和循环、`HIGH` 与关键 `UNKNOWN`、cross-book completion gate 等。复杂语义判断仍需证据审阅和人工 QA。

本文件只冻结剧情线专项的 QA、生命周期一致性、父子线边界、节奏疲劳和跨书比较规则，不创建正式素材，不修改 schema，不提供具体书籍线路事实，也不替代其它专项的业务判断。
