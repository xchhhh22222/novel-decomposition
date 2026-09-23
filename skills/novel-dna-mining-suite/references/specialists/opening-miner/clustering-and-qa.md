# 小说开篇横向拆解：聚类与 QA 规则

## 1. QA 目的与证据边界

本文件只审核 `novel-opening-miner` 对开篇运行结构的抽取、窗口推进、相邻边界和跨书候选。它不把前 20 章重写成摘要，不替相邻专项完成业务对象，也不通过综合评分给作品判定“好开篇”或“坏开篇”。

所有判断必须回到：

1. 已通过 QA 的章节事实、行为、选择、冲突结果和状态变化；
2. 已存在且可核验的逐章 reader-emotion overlay；
3. 已确认的剧情线、人物功能、金手指、世界观、修炼体系或阶段资料中的接口证据；
4. 原文回查得到的首次出现、理解、验证、证明、承诺、回收、冲突启动或信息释放位置。

书名、简介、题材标签、宣传语、章节标题、人物名字和模型记忆只能用于定位，不能独立支撑开篇结构结论。证据不足时保留 `UNKNOWN`、`partial`、`not_yet`、`gap` 或 `HOLD`；不得用常见网文经验补齐缺失窗口、卖点、承诺或回收。

QA 必须保持：

- 所有记录 `status: candidate`；
- `HIGH` 不含会改变开篇判断的关键 `UNKNOWN`；
- `nearest_neighbor` 与 `cluster` 只有在全部目标书单书抽取和 QA 完成后才允许生成；
- 不写正式素材库、总索引、章节事实、逐章情绪记录或相邻专项正式产物；
- QA 失败时输出缺口、争议或阻断项，不通过删掉 UNKNOWN、伪造 evidence 或强行闭合承诺来过检。

## 2. 四层 QA 总览

### 第一层：单书开篇覆盖与证据 QA

确认一本书在冻结范围内有可定位的章节事实、章节范围、来源 QA 和情绪接口。检查：

- 目标范围是否覆盖前 3、5、10、20 章中的哪些累计窗口；
- 缺失章节、章节范围异常或来源 QA 失败是否被显式隔离；
- 每个已有结论是否有章节、阶段或 overlay 证据；
- `per_book` 与 `gap` 是否互斥；
- 四个窗口是否是累计 checkpoint，而不是四套逐章摘要；
- 空数组是否与 `unknowns`、`gap` 或 `HOLD` 结论一致；
- 相邻专项是否仅以 `adjacent_interfaces` 引用，没有复制完整业务对象；
- 是否误把角色心情、世界说明、外挂机制、完整剧情线或篇章结构写成 opening 结论。

### 第二层：3/5/10/20 窗口推进 QA

窗口 QA 观察新增和变化，不重复抄写前一窗口：

- **3 → 5**：检查读者进入和最低理解之后，是否开始出现核心卖点的实际理解、验证或主角差异证明；若尚未发生，保留 `not_yet` 或 `UNKNOWN`，不自动判失败；
- **5 → 10**：检查是否形成可以持续推进的冲突、未来 promise、stakes escalation 或首次有效回收；不能只增加事件数量；
- **10 → 20**：检查是否形成稳定的 continuation driver、可追踪承诺链和卖点运行方式，并识别重复解释、连续准备、反复悬念或卖点失速；
- 后窗口必须能说明相对上一窗口新增、改变、延迟、回收或失速的内容；
- 某对象在后窗口仍未出现，不自动等于作品失败，但必须说明它如何影响当前开篇结论；
- 不得把窗口 checkpoint 当成四个独立成功标准，也不得用窗口数量替代证据质量；
- 不设置窗口分数、综合等级或“达到第几章就合格”的机械门槛。

### 第三层：十二类开篇对象有效性 QA

逐项检查 entry、主角建立、前提暴露、外挂揭示、冲突启动、承诺、卖点证明、风险升级、首次回收、续读驱动、信息节奏和压缩候选的结构与边界。

### 第四层：跨书近邻与聚类 QA

只有所有目标书完成单书抽取、窗口 QA 和单书 QA 后，才允许生成 `nearest_neighbor` 与 `cluster`。跨书对象是开篇运行结构，不是题材标签或专名。

## 3. 单书与窗口 QA 细则

### 3.1 entry

通过条件：

- 有真实场景、问题、异常、欲望、风险、信息缺口或承诺作为入口；
- 能说明读者被要求关心什么，以及后续期待如何延续；
- 有章节或阶段证据。

失败或降级条件：

- 只有“第一章发生了某事件”、标题、简介或宣传语，没有读者进入机制；
- 只写作者展示了世界或人物，没有读者期待对象；
- 用第一章 hook 代替整个 opening 入口链。

### 3.2 protagonist_establishment

通过条件：

- 至少有可观察行为、关键选择、初始处境/约束或能力/资源边界中的可核验证据；
- 能说明行为或选择造成了什么后果，或如何改变读者对主角的理解；
- 主角印象不是只来自旁白形容词。

失败或降级条件：

- 只有“聪明、冷静、很强、很惨、特殊”等标签；
- 只有身份介绍，没有主角行动、选择、限制或他人反应；
- 把人物功能、人物百科或关系功能复制成主角建立。

### 3.3 premise_exposure

通过条件：

- 明确核心前提是什么；
- 明确截至当前窗口读者实际能够理解什么；
- 区分事件/结果、规则演示、显式说明或混合来源；
- 允许前 3、5 章只有 `partial` 或 `UNKNOWN`。

失败或降级条件：

- 以设定名词数量或世界观说明篇幅替代读者理解；
- 把作者知道的完整世界规则写成读者已经知道；
- 没有章节证据，仅按题材常识补全 premise。

### 3.4 golden_finger_reveal

四个 milestone 必须分别核验：

1. `appearance`：外挂或核心差异首次出现/接触；
2. `understanding`：主角或读者首次理解用途、规则或边界；
3. `validation`：规则被实际行动或结果证实；
4. `first_proof_or_payoff`：核心卖点首次被实际证明或兑现。

QA 规则：

- 四阶段各自有章节/窗口和 evidence，不能合并成“第几章获得外挂”；
- 阶段可以跨窗口、延后或在前 20 章没有发生；
- `appearance` 不自动推出 `understanding`；
- `understanding` 不自动推出 `validation`；
- `validation` 不自动等于核心卖点已经形成 first proof；
- 没有传统金手指时，应使用 `core_selling_point` 或 `none`，不能虚构外挂；
- 外挂获得、一次展示、人物口头解释或系统提示不自动等于卖点证明。

### 3.5 conflict_activation

通过条件：

- 有实际 activation event；
- 涉及可追踪的目标、风险、资源、身份、关系或时间压力；
- 有证据说明它能在后续持续制造目标、阻力、选择或代价。

失败或降级条件：

- 仅凭第一次打架、一次争吵、一次危险或一个敌人出现判定启动；
- 只记录冲突对象，没有持续推进能力；
- 冲突在下一场景立即消失且没有目标、风险或状态延续，却被写成持续冲突。

### 3.6 promise_setup

通过条件：

- 有可回溯的 setup event；
- 有未来可兑现的 promise、目标、真相、关系、位置、卖点或 unresolved question；
- `promise_status` 区分 `open`、`partially_paid`、`paid`、`broken_or_failed`、`abandoned` 和 `UNKNOWN`。

失败或降级条件：

- 把每个悬念都命名成长期 promise；
- 没有未来兑现对象，只有模糊的“后面会更精彩”；
- 用单一 `closed` 合并兑现、失败和主动放弃；
- 未来状态仅凭回顾性概括而无证据。

### 3.7 selling_point_proof

通过条件：

- 有明确 selling point；
- 有 proof event；
- 有 observable result；
- 能说清结果证明了什么，且与前面建立的核心期待相关。

失败或降级条件：

- 只有主角、旁白、系统或配角口头宣称卖点；
- 只有获得外挂、介绍世界规则、升级或拿资源，没有可观察证明；
- 把卖点可能很强与卖点已经被证明混为一谈。

### 3.8 stakes_escalation

通过条件：

- 有 `before_stakes`；
- 有造成变化的 `escalation_event`；
- 有可观察的 `after_stakes`；
- 明确受影响维度，如风险、资源、身份、关系、时间、目标或信息。

失败或降级条件：

- 只因为章节更多、敌人更多、数值更大、地图更大就判定风险上升；
- 前后状态没有差异；
- 升级只发生在作者解释中，没有主角、读者或局势承担的新后果。

### 3.9 first_payoff

通过条件：

- `prior_object_ref` 指向已有 promise、unresolved question、opening goal 或 selling-point 对象；
- 有实际 payoff event/result；
- 有 `payoff_degree` 和 evidence；
- 能说明回收后目标、信息、风险、关系、资源或 continuation driver 如何变化。

失败或降级条件：

- 没有前置对象，只凭结果字段声称 first payoff；
- 爆点、高潮、胜利、升级、击杀、资源到账或反转没有回收此前承诺；
- 把普通剧情推进或卖点首次出现当成 promise 已回收。

### 3.10 continuation_drivers

通过条件：

- 有 driver source，如未决问题、下一目标、风险、promise、state change、关系或信息缺口；
- 有具体的继续阅读对象；
- 有理由说明它为何会推动下一窗口，而非只是形式上的截断。

失败或降级条件：

- 只记录“他震惊了”“门后有人”或句号前突然停顿；
- 悬念与前面开篇运行链无关；
- 新危机覆盖了尚未处理的旧承诺，却没有说明两者如何连接。

### 3.11 information_pacing

通过条件：

- 明确信息 item、披露状态和披露窗口；
- 说明读者知识如何发生可观察变化；
- `why_now` 或 `why_delayed` 没有证据时保持 `UNKNOWN`。

失败或降级条件：

- 把作者意图、人物内心或商业目的当作延迟原因；
- 用信息数量替代信息节奏；
- 只列设定，没有说明它如何改变读者理解、期待、风险或选择。

### 3.12 opening_compression

允许报告以下候选结构问题：

- `repeated_explanation`：同一必要信息反复解释但理解没有新增；
- `repeated_setup_without_proof`：反复搭台但没有卖点证明或可见结果；
- `preparation_without_validation`：连续准备、训练或等待，却没有验证；
- `selling_point_delay`：卖点被持续承诺但窗口内迟迟无实际展示；
- `repeated_cliffhanger_without_progression`：悬念反复出现但目标、风险或信息不变化；
- `promise_accumulation_without_payoff`：承诺不断新增而没有合理回收窗口；
- `conflict_reset_without_escalation`：冲突反复重置，没有提高风险或改变目标；
- `information_overload_without_knowledge_gain`：信息大量出现但读者理解没有增加；
- `redundant_scene_function`：多个场景完成同一开篇功能且没有新增状态；
- `event_density_without_opening_progress`：事件密度很高但十二类开篇对象没有推进。

QA 规则：

- 每个问题必须有窗口、章节模式和 evidence；
- 只能写成 `observed`、`possible` 或 `UNKNOWN` 候选观察；
- 不能因为出现一个问题就自动判定开篇失败；
- 不能用综合分数、等级或题材偏好替代结构证据。

## 4. 跨专项边界 QA

每条开篇记录都要检查：

- `plotline` 只引用线路在开篇窗口内的启动、暴露、推进和早期回收，不复制完整九段生命周期；
- `chapter_emotion` 只引用逐章 reader-emotion、承诺和余震，不重新标注主读者情绪；
- `character_function` 只引用关键人物进入开篇并改变主角选择、资源或风险的接口，不复制人物功能组合；
- `golden_finger` 只引用外挂或核心卖点的机制接口，不复制输入—处理—输出—限制—成长；
- `worldbuilding` 只引用读者理解所需的规则、稀缺、制度或冲突接口，不复制世界因果链；
- `cultivation` 只引用成长门槛、升级或战力展示如何服务卖点，不复制修炼体系；
- `arc_structure` 只引用开篇窗口与后续阶段的接口，不把窗口结论升级为全书结构；
- `plot_mechanism` 只引用机制在开篇首次起效或被验证，不复制可复用机制模板。

如果开篇结论无法脱离相邻专项的完整对象独立取证，应降低置信度或写入 `gap/HOLD`，而不是把相邻对象嵌入 schema。

## 5. 跨书近邻与聚类 QA

### 5.1 completion gate

在下列条件全部满足前，禁止生成跨书 `nearest_neighbor` 或 `cluster`：

1. 所有目标书都有 `per_book` 或明确 `gap`；
2. 所有可用单书记录都完成窗口覆盖、十二类对象和边界 QA；
3. 缺失章节、来源 QA、情绪 overlay 和关键 UNKNOWN 的影响已经写入 QA；
4. 没有用一本书的开篇结构补齐另一本文本；
5. 上述状态通过 `cross-book completion gate`，而不是仅凭文件存在。

### 5.2 comparison dimensions

跨书比较至少包括：

- entry mechanism 及其如何转化为持续期待；
- protagonist establishment sequence，包括行为、选择、限制和后果；
- premise exposure 的时间、证据方式和读者理解增量；
- golden-finger 四阶段的节奏、分离程度和 first proof；
- conflict activation 是否由局部事件变成持续推进；
- promise 建立、stakes escalation 和 first payoff 的连接；
- selling-point proof 的 observable result；
- continuation driver 的来源和 3→5→10→20 推进；
- information pacing 与 opening compression 的差异边界。

禁止只按下列表面标签判断相似：

- 系统开局；
- 穿越；
- 第一章战斗；
- 退婚；
- 学院测试；
- 升级或考试。

### 5.3 nearest neighbor

每条 `nearest_neighbor` 必须同时给出：

- 相似的开篇运行点；
- 关键差异边界；
- 支撑相似与差异的 evidence。

如果只能证明表面标签相同，使用 `insufficient_evidence` 或保持 `HOLD`，不生成强相似结论。

### 5.4 cluster

`cluster` 必须：

- 描述共同的开篇运行方式，而不是题材皮肤；
- 保留 `unclustered`、`insufficient_evidence` 和 `HOLD`；
- 不强制所有书进入某个簇；
- 不允许 QA 未通过的书支撑 `HIGH` 置信聚类；
- 保持 `candidate`，不得写入正式素材库或升级为 active；
- 给出支持书目、近邻证据和与相近候选的边界条件。

## 6. 开篇疲劳与失速审计

单书 QA 必须检查开篇是否出现以下运行疲劳。这里只报告证据化风险，不自动给作品评分：

- 同一解释反复出现，但读者知识没有增加；
- 同一 setup 反复出现，但卖点没有 proof；
- 准备、训练、等待或铺垫持续进行，却没有 validation；
- 卖点被多次预告但没有 observable result；
- cliffhanger 反复出现，但没有新的目标、风险、信息或状态变化；
- promise 不断累积，first payoff 却长期没有合理窗口；
- conflict 每次都重置，既不升级风险也不改变目标；
- 信息量不断增加，但读者实际理解、期待或选择没有提升；
- 多个场景完成相同开篇功能，却没有新的状态、限制、关系或信息；
- 事件密度很高，但 3/5/10/20 窗口中的 opening functions 没有推进；
- 主角长期被动承受事件，行为、选择和能力边界没有建立；
- 第一次有效回收后没有形成新的 continuation driver 或状态余震。

每条疲劳记录都应说明：发生在哪个窗口、涉及哪些章节、重复或失速的运行方式、造成的可观察阅读/结构效果，以及证据是否足够。

## 7. QA 输出与阻断规则

### 7.1 PASS

可观察对象和窗口推进有证据，边界没有越界，缺口已如实保留，且不会把表面事件当成开篇功能。

### 7.2 HOLD

有开篇候选或运行迹象，但关键证据不足，例如：

- 前置章节缺失；
- 卖点出现但未验证；
- 承诺建立但无法确认未来对象；
- chapter-emotion、plotline 或其它接口尚未通过 QA；
- 疲劳风险存在但窗口范围不足。

### 7.3 FAIL

出现以下任一情况应阻断下游高置信聚合：

- 将前 20 章摘要当作 opening analysis；
- 将一次打斗当作持续冲突启动；
- 将外挂获得当作卖点 proof；
- 将爆点、升级、击杀或资源到账当作无前置的 first payoff；
- 将普通断章当作 continuation driver；
- 将旁白形容词当作主角建立的全部证据；
- 复制相邻专项完整对象；
- 从书名、简介或标签补造窗口结构；
- 通过删除 UNKNOWN、伪造 evidence 或强行闭合 promise 来满足结构。

QA 失败不等于作品开篇失败，而是当前拆解不能作为高置信下游依据。

## 8. 人工交接前检查

`handoff` 交接前必须确认：

- 每个候选都能回到累计窗口和章节证据；
- 四个金手指 milestone 的缺失或跨窗口情况已说明；
- first payoff 有合法 prior object；
- continuation driver 不是形式悬念；
- opening compression 是候选问题，不是综合等级；
- 相邻专项只保留接口；
- `UNKNOWN`、`partial`、`not_yet`、`gap` 和 `HOLD` 没有被静默清除；
- 近邻记录有相似运行点、差异和 evidence；
- 聚类允许不成簇，并满足 cross-book completion gate；
- 结果仍为 `candidate`，不自动写正式素材库。

本文件只冻结开篇专项的四层 QA、窗口增量检查、十二类对象有效性、疲劳审计、跨书比较和交接阻断规则。它不新增 schema 字段，不定义综合评分，也不替代 validator 的结构硬约束。
