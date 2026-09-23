# 剧情机制聚类与 QA 规则

本文件只审核 `novel-plot-mechanism-miner` 对可复用剧情运行结构的识别、证据、复用条件、变体、失败模式和跨书比较。它不把单次事件包装成机制，不替剧情线、篇章、开篇、人物、情绪、世界观、修炼或金手指完成专项分析，也不通过综合评分给机制候选分级。

## 1. 总原则

剧情机制的 QA 核心是：

> 这套结构是否由可观察的触发、输入、角色施力、操作、决策、约束、升级、输出和状态变化组成，并且有证据说明它为什么还能在条件变化后再次运行？

必须持续区分：

- 一次 `observed_instance` 是证据，不是机制本身；
- 表面事件相同不代表运行结构相同；
- 表面事件不同不排除运行结构同构；
- 事件重复不等于机制可复用；
- 世界规则存在不等于机制约束成立；
- output 不自动等于 payoff；
- state transition 不自动等于 payoff；
- 只有单次实例且没有复用规则/条件时，必须保留 `partial`、`UNKNOWN`、`gap` 或 `HOLD`；
- 不设置“出现 2 次/3 次才算机制”的机械阈值，复用证据可以来自多次运行、明确规则、或二者结合。

所有判断必须基于 `evidence_refs` 和允许来源。书名、简介、卷名、地图名、场景名、题材标签和模型记忆不能独立支撑机制身份或聚类。

## 2. QA 输入与状态门

QA 只能读取 orchestrator 冻结的批次包，以及其中允许的章节、阶段和相邻接口。至少记录：

- 目标书与章节/阶段范围；
- 观察到的实例引用；
- 允许使用的章节事实和阶段事实；
- 上游 chapter facts、plotline、opening、character、emotion、world、cultivation、golden-finger QA 状态；
- 当前候选的缺口、争议和禁止输出；
- 是否已经完成全部目标书的单书提取与单书 QA。

状态边界：

- 单书字段缺证据时保留 `UNKNOWN` 或 `partial`；
- 复用依据不足时可以输出 `gap` 或 `HOLD`；
- `qa_status: FAIL` 的单书结果不能支撑高置信跨书聚类；
- 所有结果只能是 `candidate`；
- nearest-neighbor 和 cluster 必须等待全部目标书单书 QA 完成并通过 cross-book completion gate；
- QA 不得通过删除 `UNKNOWN`、伪造实例、补写路径分叉或把一次事件改名来强行过检。

## 3. 第一层：单书 mechanism candidate QA

### 3.1 实例覆盖与来源

检查：

1. 每个机制候选是否至少引用一个具体实例；
2. 每个实例是否能回到章节或阶段证据；
3. `instance_summary` 是否只记录机制运行所需观察，而没有复制完整剧情线、章节摘要或相邻专项对象；
4. 是否把同一事件的不同描述误当成多个独立实例；
5. 是否把不同实例合并时保留了各自的输入、角色、路径、结果和状态变化差异；
6. 是否把未核验的实例标为 `UNKNOWN`、`partial` 或 `HOLD`。

失败信号：

- 只有题材标签、标题或简介，没有章节/阶段证据；
- 只有一个场景名，却没有运行步骤和状态变化；
- 用另一部书的实例补足当前书缺失证据；
- 把一场戏拆成许多“实例”以制造虚假重复性。

### 3.2 mechanism_identity 与边界

`mechanism_identity` 必须说明：

- 可复用的核心运行方式；
- 适用范围和核心不变量；
- 与相邻候选的运行差异；
- 被排除的表面标签及排除理由。

以下不能单独作为 identity：

- “考试机制”“比赛机制”“任务机制”“追杀机制”“秘境机制”；
- “主角打脸”“反派挑衅”“危机升级”；
- 某个具体人物、组织、地点、异兽或道具；
- 单次误会、一次救援、一次胜利或一次测试。

身份 QA 要问：如果替换人物、地图和表面任务，哪些运行关系仍然成立？如果没有答案，应降为单次实例或场景模板候选。

### 3.3 最小运行链

候选至少应能沿证据回答：

`trigger_conditions → inputs/actors_and_roles → operations → decision_points/constraints → escalation_logic → outputs → state_transition`

不是每次运行都需要所有对象都有多项证据，但缺失的关键环节必须进入 `unknowns`、`gap` 或 `HOLD`，不能用空数组伪装为已完成分析。

QA 逐项核对：

- trigger 是否说明启动前提，而非只列发生事件；
- inputs 是否区分信息、资源、身份、规则、风险、关系、时间、权限和期待；
- actors 是否说明施压、响应、验证、阻断、兑现等运行角色；
- operations 是否呈现步骤或依赖，而非事件清单；
- decision 是否存在真实可替代路径；
- constraints 是否对角色、步骤、资源、权限、时间或结果产生限制；
- escalation 是否出现结构变化，而非单纯数值增加；
- outputs 是否包含可观察结果；
- state transition 是否描述运行前后的状态差异。

## 4. 第二层：机制有效性与 repeatability QA

### 4.1 复用证据来源

`repeatability` 可以由下列来源支持：

- 实际出现多个运行实例，且共享核心 trigger、input、operation、constraint、result 或 state transition 关系；
- 文本明确给出可重复启动的规则、制度、能力、权限或流程，并且有至少一个实例验证其运作方式；
- 多次实例与明确规则共同支持机制不依赖单次偶然条件。

只有一个实例且没有明确可复用规则时：

- 不得标为已证实的 `supported`；
- `evidence_basis` 应诚实记录 `single_instance_only`；
- 输出 `partial`、`UNKNOWN`、`gap` 或 `HOLD`；
- 不得凭“这种套路通常能再用”补造 repeatability。

不设置固定实例次数阈值。两次事件也可能只是相同场景复现，三次事件也可能只是表面重复；关键是运行结构和可观察条件。

### 4.2 核心不变量

对每个声称可复用的候选，核对跨实例是否至少保留：

- 启动条件的结构作用；
- 输入如何进入运行链；
- 角色施力、响应、验证或阻断的关系；
- operation 的顺序或依赖；
- 约束如何改变选择或代价；
- 升级如何改变压力、路径、资源、风险或 output；
- 运行后状态如何变化；
- payoff 如何由前置压力、承诺或选择回收。

如果每个实例都必须依赖完全相同的人物、地点、事件名称和对白，核验它是否只是场景模板或固定桥段，而非机制。

### 4.3 reset / preserve / reacquire

复用 QA 必须检查 `repeatability` 是否说明：

- 哪些触发条件可以重新出现；
- 哪些资源或权限需要重新获得；
- 哪些压力、关系或信息需要保留；
- 哪些中间状态必须重置；
- 上一次运行的结果是否成为下一次的输入或约束；
- 失败后是否能恢复、换路径或重新启动。

“可以再次使用”但没有 reset、preserve 或 reacquire 条件，不能算完整 repeatability 证据。

### 4.4 复用与机制边界

以下情况应降级或拆分：

- 只有角色名和地图名改变，trigger/input/operation/output 全部固定，却没有 meaningful variation；
- 每次都通过同一 decision point 得到同一结果，没有路径或代价变化；
- 机制只靠数值膨胀，没有结构升级；
- 每次运行都必须复刻同一场景、同一对话和同一事件顺序；
- 候选被拆成“一场戏一个机制”，无法说明跨实例不变量；
- 候选被并成“任务机制”“打怪机制”等过粗类别，掩盖不同的约束、选择、资源流和结果逻辑。

## 5. operations QA

### 5.1 顺序与依赖

每个 operation 应能说明：

- 所需输入或前态；
- 实际发生的结构动作；
- 结果或中间状态；
- 与前后 operation 的顺序、依赖或并行关系；
- 章节/阶段证据。

普通事件列表不能直接当 operation chain。若删除某一步后前后运行结构完全不受影响，要核验这一步是否只是剧情实例细节，而不是机制核心。

### 5.2 不得偷渡相邻对象

以下不属于 operation 本身：

- 一条剧情线的完整节点列表；
- 一组人物功能或关系组合；
- 一套世界规则或金手指输入/处理/输出模型；
- 一段章节摘要；
- 一串没有依赖关系的战斗名称。

可以引用这些对象作为 interface 或 input，但必须说明它们在当前机制操作中的局部作用。

## 6. decision_points QA

`decision_point` 必须有真实可行路径，且选择造成可观察的 `path_consequence`。核对：

- 是否至少存在两个可替代或可拒绝的路径；
- 决策主体是否清楚；
- 选择时的压力、信息、资源和约束是否可回查；
- chosen/observed path 是否与 evidence 一致；
- 选择是否改变后续 operation、风险、资源、关系、权限或 output；
- 是否区分“人物主动选择”和“被迫执行唯一动作”。

以下不自动算 decision point：

- 人物做了一个动作但没有替代路径；
- 被动受伤、被抓、被传送或被迫接受结果；
- 普通反转、揭示或升级没有选择后果；
- 作者直接安排的场景切换。

若路径分叉只存在于模型推测而非文本证据，保留 `UNKNOWN` 或 `HOLD`。

## 7. constraints QA

约束必须实际作用于机制运行，至少说明：

- constraint 的类型和来源；
- 它限制哪个角色、步骤、资源、权限、时间或结果；
- 它通过何种 operation 改变选择空间或代价；
- 产生了什么 observable effect。

世界规则存在本身不等于 mechanism constraint。若规则没有改变角色选择、运行步骤、资源门槛、风险或结果，不应强行写为本机制约束。

## 8. escalation_logic QA

每个有效升级都要检查：

`before_pressure_or_state → escalation_change → after_pressure_or_state → structural_effect`

升级可以改变：

- pressure 或 choice space；
- resource requirement 或 permission threshold；
- 信息公开程度和信息差；
- role relationship、阻断方式或验证对象；
- risk、stakes、失败成本或 output logic；
- 机制从隐性运行转为公开运行，或从单体运行转为群体/制度运行。

以下不能单独构成 escalation：

- 敌人更强；
- 数值更高；
- 人数更多；
- 地图更大；
- 战斗时间更长；
- 场面更热闹。

如果这些变化没有改变运行结构，只能作为实例细节或 evidence，不作为机制升级结论。

## 9. outputs / state_transition / payoff_path QA

三者必须分开：

- `outputs`：一次机制运行直接产生了什么结果；
- `state_transition`：运行前后系统状态如何变化；
- `payoff_path`：前置压力、承诺、选择如何经过机制被回收，并形成可见兑现证据或后续余震。

核对：

1. output 是否有观察结果，而不是作者意图；
2. state transition 是否说明 before/after 差异，而不是“事件结束”或“进入下一章”；
3. payoff 是否能回溯 prior pressure/promise/choice；
4. payoff 是否经过真实 operation 和 decision，而不是凭空奖励；
5. 是否有公开结果、他人反应、关系动作、资源变化、选择验证、代价回响或期待变化等可见证据；
6. output 或 state change 是否被错误地自动标成 payoff。

单纯击杀、升级、拿资源或获得结果不自动构成 payoff；缺少前置压力和可见回收时，保留 `UNKNOWN` 或 `HOLD`。

## 10. variation_points QA

`variation_points` 必须记录机制复用时真正允许变化的变量，例如：

- actor；
- resource；
- information；
- constraint；
- stakes；
- path；
- output；
- relation、map 或 permission。

每个变化点应说明：

- 哪个变量可以改变；
- 核心 operation logic 哪部分保持不变；
- 变化如何产生不同风险、结果、节奏或情绪余震；
- 是否有章节/阶段实例支持。

不能把所有字段都标为 variation；若变化后核心运行关系不可识别，应考虑拆分机制，而不是扩大 variation。

## 11. failure_modes QA

每个 failure mode 至少检查：

- failure condition 是否具体；
- break point 位于哪个步骤、角色或约束；
- effect 是失败、打断、反转、无法启动还是改道；
- recoverability_or_next_state 是否有证据；
- 是否与普通“主角失败”区分；
- 条件缺失、被识破、资源不足、角色拒绝、权限失效、决策错误和结果反转是否被混为一类。

失败后能否恢复必须以文本证据为准；不能因为理论上“还可以再试”就补写恢复路径。

## 12. 机制疲劳与机械重复 QA

除结构完整性外，必须检查候选是否已经退化为机械循环：

- 同一 mechanism 多次运行，但只有人物名或地图名变化；
- trigger、input、operation、output 全部固定，没有 meaningful variation；
- 每次都通过相同 decision point 得到相同结果；
- escalation 只靠数值、敌人等级或人数膨胀；
- failure mode 从不出现，机制长期没有被打断、反转或重新验证；
- payoff path 反复相同，读者预期完全固定；
- 候选越拆越细，退化为“一场戏一个机制”；
- 候选越并越粗，把完全不同的运行结构都塞进“任务机制”“打脸机制”或其它标签。

疲劳检查不是评分，也不自动否定候选。它应输出具体的重复位置、缺少的变化变量、尚未出现的失败边界或需要人工确认的拆分/合并决策。

## 13. 第三层：instance 归并与运行一致性 QA

### 13.1 同类归并

只有当多个实例在以下维度具有可解释的结构同构时，才保留为同一机制候选：

- trigger/input 的功能相近；
- actor roles 的施力与响应关系相近；
- operation chain 的关键依赖相近；
- decision points 造成相近类型的路径分叉；
- constraints 以相近方式限制选择或代价；
- escalation 改变相近的压力、权限、风险或 output；
- state transition 和 payoff path 的运行逻辑相近；
- repeatability 的 reset/preserve/reacquire 条件可以解释。

表面事件不同但上述结构同构，可以是同类候选。表面事件相同但 trigger、constraint、decision、resource-flow 或 output logic 不同，不得强行归并。

### 13.2 拆分与保留差异

以下情况需要考虑拆分：

- 只有“都有任务/比赛/追杀”这一表面相似；
- 一个实例依靠信息差反制，另一个依靠资源争夺，且运行关系不同；
- 一个实例有真实选择分叉，另一个没有；
- 一个实例的约束决定结果，另一个约束只作背景；
- 一个实例的 output 是公开认知变化，另一个是资源到账，且无共同 payoff path；
- 复用条件、失败点或状态变化完全不同。

拆分时保留相近候选之间的 `difference_boundary` 和证据，不用新标签掩盖不确定性。

### 13.3 不得把相邻专项对象当归并证据

以下共享不单独证明机制相同：

- 同一人物；
- 同一地图；
- 同一境界；
- 同一组织；
- 同一金手指；
- 同一情绪词；
- 同一剧情线或同一 arc。

这些只能作为 interface 或输入/约束证据，必须回到机制运行结构本身。

## 14. 第四层：跨书 nearest-neighbor / clustering QA

跨书 QA 必须比较：

- trigger conditions；
- inputs；
- actor roles；
- operation chain；
- decision points；
- constraints；
- escalation logic；
- outputs 与 state transition；
- repeatability 与 reset/preserve/reacquire；
- variation points；
- failure modes；
- payoff path。

禁止按以下表面名词聚类：

- 考试；
- 比赛；
- 任务；
- 秘境；
- 追杀；
- 打怪；
- 升级；
- 学院、战争、城市或其它地图/题材名称。

### 14.1 nearest-neighbor

每条近邻记录必须同时提供：

- 相似运行点：哪些 trigger、operation、constraint、escalation、state 或 payoff 结构相近；
- 关键差异：哪些 input、decision、failure、variation 或复用条件不同；
- evidence：每个重要相似点和差异点都能回到证据。

近邻不是合并结论。`merge_candidate` 只能表示需要后续审核，不得直接写正式素材卡。

### 14.2 cluster

聚类必须描述：

- shared operation；
- 跨实例不变量；
- variation pattern；
- failure pattern；
- 与相近候选区分的 boundary conditions；
- 支持该聚类的目标书和实例证据。

聚类允许使用 `unclustered`、`insufficient_evidence` 或 `HOLD`。不得强制凑簇；QA 未通过或关键 unknown 未解决的书不能支撑 `HIGH` cluster。单书候选也不能自动升级为高频母型。

## 15. 共享契约与人工交接

QA 必须维护统一 derived envelope：

`record_type / schema_version / record_id / status / book_id 或 book_ids / evidence_refs / unknowns / confidence / qa_status`

并保持：

- candidate-only；
- `HIGH` 不带关键 `UNKNOWN`；
- `partial`、`UNKNOWN`、`gap`、`HOLD` 合法；
- cross-book completion gate；
- adjacent 专项只通过 interface/reference；
- 不写正式素材库或总索引。

`handoff` 应把以下内容交给人工：

- 候选机制身份和适用范围；
- 支持与反例实例；
- 复用不变量与 reset/preserve/reacquire 条件；
- 变化点、失败模式和机械重复风险；
- 最近邻相似运行点与关键差异；
- 聚类边界、缺口、争议和待确认决策。

本文件不授予机制合并、状态升级、schema 变更、跨专项合并或正式入库权限。

## 16. QA 自检结论

一个可进入候选交接的机制记录，应能通过以下问题：

1. 它是否描述可复用运行结构，而不是题材、标签或单次场景？
2. trigger、input、role、operation、constraint、output 和 state transition 是否各有证据？
3. operations 是否有顺序/依赖，decision 是否有真实分叉？
4. escalation 是否有 before→change→after→structural effect？
5. output、state transition 和 payoff path 是否分开？
6. repeatability 是否来自多次实例或明确规则，而不是模型推测？
7. reset/preserve/reacquire 条件是否清楚？
8. variation points 是否解释复用中的变化，failure modes 是否解释打断和反转？
9. 表面同、结构不同的实例是否被拆开；表面不同、结构同的实例是否保留候选归并？
10. 是否通过四层 QA、相邻边界、证据不确定性和跨书完成门？

任一关键问题只能靠补造事实回答时，结论必须是 `HOLD`、`gap` 或 `NEEDS_REVIEW`，而不是强行生成机制候选。
