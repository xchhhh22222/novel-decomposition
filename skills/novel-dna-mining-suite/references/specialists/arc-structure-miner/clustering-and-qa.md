# 篇章阶段结构横向拆解：聚类与 QA 规则

## 1. QA 目的与证据边界

本文件只审核 `novel-arc-structure-miner` 对长篇阶段结构的识别、推进、转折、收束、全局状态变化、下一阶段入口和 nested 关系。它不把章节或卷名重新排列成 arc，不替剧情线、开篇、世界观、修炼或剧情机制完成专项分析，也不通过综合评分给作品判定结构好坏。

所有判断必须回到：

1. 已通过 QA 的章节事实、剧情线状态变化、人物行为、冲突结果和阶段资料；
2. 已确认的 opening、chapter-emotion、character-function、worldbuilding、cultivation、golden-finger 或 plot-mechanism 接口证据；
3. 原文回查得到的阶段边界、主目标、持续压力、推进变化、转折、收束、状态变化、下一入口或 nested 位置。

卷名、章节标题、章节范围、时间段、地图名、境界名、简介、题材标签和模型记忆只能用于定位，不能独立支撑 arc 结构结论。证据不足时保留 `UNKNOWN`、`partial`、`gap` 或 `HOLD`；不得用“常见的学院篇/秘境篇/战争篇结构”补造阶段。

QA 必须保持：

- 所有记录 `status: candidate`；
- `HIGH` 不含会改变阶段边界、结局、状态变化、下一入口或 nested 关系的关键 `UNKNOWN`；
- `nearest_neighbor` 与 `cluster` 只有在全部目标书单书抽取和 QA 完成后才允许生成；
- 不写正式素材库、总索引、章节事实、分卷正式资料或相邻专项正式产物；
- QA 失败时输出缺口、争议或阻断项，不通过删掉 UNKNOWN、伪造 evidence 或强行闭合阶段来过检。

## 2. 四层 QA 总览

### 第一层：单书 arc 识别 QA

确认一本书在冻结范围内有可定位的章节事实、来源 QA、阶段资料和可用专项接口。检查：

- 目标范围、已覆盖章节和排除范围是否清楚；
- 阶段候选是否有前后结构差异，而不是只有卷名、地图或时间变化；
- arc identity、goal、pressure、progression、turning point、resolution、state change 和 next entry 是否各自有位置；
- `per_book` 与 `gap` 是否互斥；
- 空数组、`UNKNOWN`、`partial` 和 `HOLD` 是否与证据缺口一致；
- 相邻专项是否仅以 `adjacent_interfaces` 引用，没有复制完整业务对象；
- 是否误把章节摘要、单条剧情线、境界阶段或地图名写成 arc。

### 第二层：arc 生命周期与阶段推进 QA

检查阶段从未启动、启动、推进、暂停、转向到不同收束结局的证据链：

- `arc_boundary`：边界前后结构确实不同；
- `arc_goal`：主目标或结构任务能够组织多条局部线和阶段压力；
- `arc_pressure`：压力持续影响阶段推进、权限、风险、资源、线路或选择；
- `arc_progression`：每个推进步骤都说明 before/step/after 和 structural effect；
- `arc_turning_points`：转折改变阶段级方向、重心、路线、权限、压力或全局局势；
- `arc_climax_or_resolution`：高点或收束区分成功、失败、放弃、转向和未决；
- `arc_state_change`：收束或转折后全局实际发生变化；
- `next_arc_entry`：下一阶段由已有 state change、收束余波、未决任务或重心迁移自然打开；
- `arc_function`：阶段承担的全书结构作用有证据；
- `arc_lifecycle`：状态与边界、目标、转折、收束证据相互一致。

### 第三层：nested arc 与跨阶段一致性 QA

检查父 arc、sub-arc、相邻阶段和已结束阶段之间的关系、传播边界和复活问题。重点防止：

- 普通章节序列、短期事件、同一地图或一条剧情线被自动升级为 sub-arc；
- sub-arc 的完成、失败或暂停被自动传播给 parent；
- parent 与 sub-arc 互相自引用或形成循环；
- arc 收束后没有 state change 却直接换卷或换阶段；
- 状态已 resolved、failed 或 abandoned 的阶段无解释再次出现；
- 新阶段只是旧阶段换地图、换敌人或换卷名，结构功能没有变化。

### 第四层：跨书近邻与聚类 QA

只有所有目标书完成单书抽取、生命周期 QA 和 nested QA 后，才允许生成 `nearest_neighbor` 与 `cluster`。跨书对象是阶段结构如何运行，不是阶段名称或题材皮肤。

## 3. 单书 arc 对象有效性 QA

### 3.1 arc_boundary

通过条件：

- 有 `before_structure` 和 `after_structure`；
- 有真实 `triggering_change`；
- 有 `structural_difference` 说明为什么前后不再是同一阶段；
- 有章节或阶段范围和 evidence。

失败或降级条件：

- 只因卷名、章节编号、时间跳转、地图切换或境界突破划界；
- 只有“前期进入中期”“进入新地图”等空泛标签；
- 边界前后目标、压力、线路组织、权限或全局结构没有可观察差异。

### 3.2 arc_goal

通过条件：

- 目标是阶段级主推进方向或结构任务；
- 能说明它组织了哪些局部目标、线路、资源门槛、人物选择或读者承诺；
- 有完成、失效、失败或转向条件。

失败或降级条件：

- 只是某条剧情线的短期目标；
- 只是“变强”“去某地”“打败某人”等脱离阶段组织的事件目标；
- 只有阶段名称，没有目标或结构任务证据。

### 3.3 arc_pressure

通过条件：

- 有压力来源和 operation；
- 有 affected targets；
- 有 observable effect 说明压力如何持续改变阶段推进、风险、权限、资源或选择。

失败或降级条件：

- 只有敌人、困难、地点或制度名词；
- 压力只出现一次，没有持续影响阶段；
- 阶段压力与 arc goal、线路组织或状态变化没有关系。

### 3.4 arc_progression

通过条件：

- 每个 progression step 都具备 before_stage_state、progression_step、after_stage_state 和 structural_effect；
- 前后阶段状态有真实差异；
- 能看出升级、扩张、验证、转向、重组、收缩或收束中的至少一种结构运动。

失败或降级条件：

- 只是事件数组、战斗列表、章节数量或场景地点列表；
- progression step 很多，但 stage state 基本不变；
- 只写主角数值上涨或敌人变强，没有阶段组织变化；
- 把普通剧情线推进直接复制成 arc progression。

### 3.5 arc_turning_points

通过条件：

- 有 turning_event；
- 有 before_direction_or_priority 和 after_direction_or_priority；
- 有 structural_effect 和 evidence。

失败或降级条件：

- 普通高潮、战斗胜利、升级、资源到账或反转没有阶段级后果；
- 事件很强，但阶段目标、路线、压力、权限或全局方向没有改变；
- 把每个局部剧情线节点都升级为 arc turning point。

### 3.6 arc_climax_or_resolution

通过条件：

- `resolution_outcome` 明确为 `resolved`、`failed`、`abandoned`、`redirected`、`unresolved` 或 `UNKNOWN`；
- 有事件、影响的阶段目标和阶段范围；
- 能说明阶段完成、失败、放弃、转向或未决留下的结构后果。

失败或降级条件：

- 只写“主角获胜”“打赢敌人”而没有阶段任务结果；
- 将单条剧情线 payoff 当成整个阶段 resolution；
- 默认所有阶段都必须以胜利高潮结束；
- 用 `closed` 之类模糊状态合并不同结局。

### 3.7 arc_state_change

通过条件：

- 有 `caused_by_resolution_or_turning_point`；
- 有 before_global_state 和 after_global_state；
- 有 changed_domains 和 structural_effect；
- 变化涉及目标、资源、身份、关系、认知、地图、权限、风险、势力或局势中的可观察差异。

失败或降级条件：

- 只重复 resolution 的事件或结果；
- 只写“进入下一卷”“换地图”“开启新任务”；
- 没有全局前后差异或对后续阶段的影响。

### 3.8 next_arc_entry

通过条件：

- `source_state_change_id` 指向已有 state change；
- 有 opened_next_arc_goal_or_task、opened_pressure_or_risk 或结构问题；
- 有 entry_reason 说明为什么入口由前一阶段自然产生。

失败或降级条件：

- 只根据下一卷标题、地图名或新敌人倒推入口；
- 没有状态变化支撑，却凭空接入新阶段；
- 把同一个 resolution 重复改名写成 next entry。

### 3.9 arc_function

通过条件：

- 有受控 structural_function 和 function_description；
- 能说明该功能如何影响全书主线、读者期待、风险、线路组织或后续结构；
- 有阶段证据。

失败或降级条件：

- 只贴“学院篇”“秘境篇”“战争篇”“升级篇”等标签；
- 结构作用与目标、压力、推进、转折或状态变化无关；
- 把阶段发生的表面地点或题材皮肤当功能。

### 3.10 nested_structure

通过条件：

- sub-arc 有独立 goal、pressure、progression、resolution，或至少有明确父阶段作用证据；
- relation_type 是 `service`、`obstacle`、`change` 或 `UNKNOWN`；
- 有 `how_sub_arc_affects_parent`、`sub_arc_completion_effect`、`pause_relationship` 和 evidence；
- parent_arc_id 与 sub_arc_id 不相同，关系图不形成循环。

失败或降级条件：

- 只是连续章节、短期事件、同一地图、共享人物或同一卷名；
- sub-arc resolved 就把 parent 直接判 resolved；
- sub-arc failed 就把 parent 直接判 failed；
- parent paused 就把所有 sub-arc 自动判 paused；
- sub-arc resolved ≠ parent resolved；sub-arc failed ≠ parent failed；parent paused ≠ 所有 sub-arc 自动 paused；
- 子阶段对 parent 没有 service、obstacle 或 change 作用，却仍强行挂接。

## 4. 生命周期一致性 QA

### 4.1 状态证据条件

- `not_started → active`：需要真实 boundary、阶段激活事件、主目标或压力接入证据；
- `paused`：需要暂停、延迟、资源冻结、目标搁置或结构切出的证据；
- `redirected`：需要目标、优先级、路线、压力、权限或全局方向发生实质变化；
- `resolved`：需要阶段目标或结构任务完成的证据；
- `failed`：需要阶段任务失败、不可达或以失败收束的证据；
- `abandoned`：需要人物、势力或叙事方向主动放弃的明确依据；
- `unresolved`：需要阶段被结束、切走或转向，但核心结构问题仍未解决的证据；
- `UNKNOWN`：证据不足时合法，不得用猜测替代。

“暂时没有后续章节”不自动等于 `failed` 或 `abandoned`；“已经换卷”不自动等于 `resolved`。

### 4.2 关闭与复活

已 `resolved`、`failed` 或 `abandoned` 的 arc 再次出现时，必须核验：

- 是否是有证据的 `reopened` 或新的阶段状态；
- 是否已经发生目标、压力或结构作用变化，应建立新 arc；
- 是否只是 parent arc 延续或另一个相关阶段；
- 是否有真实 state change 支撑再次推进。

不能无解释地让已结束阶段“复活”，也不能因共享人物、敌人或地图就强行视为同一 arc。

## 5. Arc 专项结构疲劳与失衡

单书 QA 必须检查以下问题，只报告证据化风险，不自动给作品打等级：

- 阶段长期只有事件，没有 progression；
- `event_density_without_progression`：事件密度很高，但阶段状态和结构功能没有推进；
- progression step 很多，但 stage state 基本不变；
- turning point 频繁出现，但阶段方向、优先级、压力或权限没有实际变化；
- arc pressure 长期重复同一种施压方式，既不升级也不转向；
- resolution 后没有 state change；
- state change 后没有 next arc entry，但后续直接进入新阶段；
- sub-arc 不断开启但不收回、不反哺 parent 或不改变 parent；
- 多个 arc 只是换地图、敌人或卷名，结构功能没有变化；
- 阶段长期只承担同一种 function，缺少结构升级或重心迁移；
- 每次阶段转换都依赖新敌人或新地图，目标、压力和全局关系没有改变；
- 阶段边界过密，导致每个小事件都被包装成 arc；
- 阶段边界过稀，导致多个独立目标、压力和收束被强行并成一个 arc。

每条疲劳或失衡记录都应说明：发生在哪个阶段、涉及哪些章节、结构模式是什么、造成什么可观察后果，以及证据是否足够。

## 6. 跨专项边界 QA

每条 arc 记录都要检查：

- `plotline` 只引用具体线路如何在阶段内被组织、交汇、暂停、兑现或改变重心，不复制九段线路对象；
- `opening` 只引用前 3/5/10/20 窗口结果，不重新执行开篇十二类分析；
- `character_function` 只引用人物功能变化作为阶段证据，不复制人物功能组合或关系发动机；
- `chapter_emotion` 只引用 reader-emotion 节奏、蓄压和余震，不重新逐章标情绪；
- `worldbuilding` 只引用规则、制度、地图或资源层级变化作为边界/压力证据，不复制世界因果链；
- `cultivation` 只引用境界、技能、装备或资源门槛作为阶段节点，不把修炼阶段直接当 arc；
- `golden_finger` 只引用外挂权限或规则成长作为阶段升级证据，不复制输入—处理—输出—限制—成长机制；
- `plot_mechanism` 只引用可复用机制如何被安排进阶段，不复制机制模板。

如果 arc 结论只有依靠相邻专项完整对象才能成立，应降低置信度或写入 `gap/HOLD`，而不是把相邻对象嵌入 schema。

## 7. 跨书近邻与聚类 QA

### 7.1 completion gate

在下列条件全部满足前，禁止生成跨书 `nearest_neighbor` 或 `cluster`：

1. 所有目标书都有 `per_book` 或明确 `gap`；
2. 所有可用单书记录都完成 arc boundary、goal/pressure、progression、turning point、resolution、state change、next entry 和 nested QA；
3. 缺失章节、来源 QA、相邻接口和关键 UNKNOWN 的影响已写入 QA；
4. 没有用一本书的阶段结构补齐另一本文本；
5. 上述状态通过 `cross-book completion gate`，而不是仅凭文件存在。

### 7.2 comparison dimensions

跨书比较至少包括：

- arc 如何划界，以及边界前后结构差异；
- arc goal 与 arc pressure 如何形成并维持；
- progression 如何升级、扩张、验证、转向或收束；
- turning point 如何改变方向、重心、压力、权限或全局状态；
- resolution 如何处理 resolved、failed、abandoned、redirected 和 unresolved；
- state change 如何打开 next arc entry；
- nested arc 如何服务、阻碍或改变 parent；
- arc function 如何随全书阶段变化；
- opening、线路、人物、情绪、世界、修炼、外挂和机制接口如何被阶段组织。

禁止只按下列表面标签判断相似：

- 学院篇；
- 秘境篇；
- 比赛篇；
- 战争篇；
- 新地图篇。

### 7.3 nearest neighbor

每条 `nearest_neighbor` 必须同时给出：

- 相似的阶段运行点；
- 关键结构差异；
- 支撑相似与差异的 evidence。

如果只能证明篇名、地图或题材标签相同，使用 `insufficient_evidence` 或保持 `HOLD`，不生成强相似结论。

### 7.4 cluster

`cluster` 必须：

- 描述阶段结构如何运行，而不是学院、秘境、比赛、战争等表面名称；
- 保留 `unclustered`、`insufficient_evidence` 和 `HOLD`；
- 不强制所有书进入某个簇；
- 不允许 QA 未通过的书支撑 `HIGH` 置信聚类；
- 保持 `candidate`，不得写入正式素材库或升级为 active；
- 给出支持书目、近邻证据和与相近候选的边界条件。

## 8. QA 输出与阻断规则

### 8.1 PASS

阶段边界、目标、压力、推进、转折、收束、状态变化、下一入口和 nested 关系均有可追溯证据，且没有把章节、卷名、地图、境界或剧情线误当 arc。

### 8.2 HOLD

有阶段候选或结构迹象，但关键证据不足，例如：

- 只有卷名或地图变化，没有前后结构差异；
- 阶段目标存在但压力或收束无法确认；
- 收束发生但全局 state change 或 next entry 不清；
- sub-arc 可能存在但没有独立目标、压力或父阶段作用证据；
- 上游剧情线、开篇、世界观或章节 QA 尚未通过。

### 8.3 FAIL

出现以下任一情况应阻断下游高置信聚合：

- 把章节摘要、卷名、时间段、地图切换或境界突破直接当 arc；
- 把单条剧情线目标、高潮或 payoff 直接当 arc goal 或 resolution；
- 把事件堆积当 progression；
- 把普通高潮、升级、战斗胜利或资源到账当 turning point，却没有阶段级后果；
- 把“进入下一卷”当 state change 或 next entry，却没有全局前后差异；
- 把 resolved、failed、abandoned、redirected 和 unresolved 混成一个结束状态；
- 让 sub-arc 状态自动传播给 parent；
- 使用自引用或循环嵌套；
- 从篇名、简介、地图名或题材标签补造 arc；
- 复制相邻专项完整对象；
- 通过删除 UNKNOWN、伪造 evidence 或强行闭合阶段来满足结构。

QA 失败不等于作品结构失败，而是当前拆解不能作为高置信下游依据。

## 9. 人工交接前检查

`handoff` 交接前必须确认：

- 每个阶段候选都能回到章节/阶段范围和结构证据；
- boundary 有前后差异，goal/pressure 有阶段作用；
- progression 有 before/step/after，turning point 有方向或重心变化；
- resolution 结局类型明确，state change 与 next entry 分开；
- nested 关系有独立阶段证据、父子作用和状态独立性；
- 疲劳/失衡记录说明结构模式和可观察后果，不是综合等级；
- 相邻专项只保留接口；
- `UNKNOWN`、`partial`、`gap` 和 `HOLD` 没有被静默清除；
- 近邻记录有相似运行点、差异和 evidence；
- 聚类允许不成簇，并满足 `cross-book completion gate`；
- 结果仍为 `candidate`，不自动写正式素材库。

本文件只冻结 arc-structure 专项的四层 QA、生命周期一致性、阶段推进、nested 关系、结构疲劳、跨书比较和交接阻断规则。它不新增 schema 字段，不定义量化评分，也不替代 validator 的结构硬约束。
