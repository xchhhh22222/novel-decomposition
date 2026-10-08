# 情绪优先、因果支撑的创作调度契约 (EMOTION_FIRST_V1)

## 范围和优先级

本契约仅约束 `novel-creation-planner` 创作层；不修改源书事实、01 章节情绪 canonical schema、02–09 拆解 schema、V1.7 RMF family 定义或生产包。用户给出明确题材/情绪/禁区时始终优先；市场和来源素材不能覆盖用户约束。

**目标**：先定义读者期待的情绪体验，再选择能在世界制度、人物选择、金手指和剧情机制中实现该体验的来源组件。不是将事件因果替换为情绪标签。

生产现实：`Shared DNA v1.0.0` 当前仅发布 02–09；`01_章节情绪` 存在于部分 research books，但未进入 active Shared DNA 生产包。任何本契约下的情绪来源必须区分：
- `ORIGINAL_DESIGN`：本次创作明确提出的新情绪设计，不是外部证据；
- `RESEARCH_VERIFIED`：只读研究资产，经 source/QA 检查后可用于**研究参考**，不得称 ACTIVE_SHARED_LIBRARY；
- 未来如出现真正另行审核的 active emotion package，须单独做 manifest/runtime/source admission，不得仅更改字符串绕过。

没有 01 情绪库生产入口时，仍可使用原创情绪模板 + 02–09 active 材料开始创作；必须披露 `EMOTION_LIBRARY_ACTIVE = NO`。

## 1. 情绪模式的最小可复用单位

**不允许**把 `低→低→高`、连续 pressure_level 数值、相同主情绪词或表面相似章尾钩子，当作已经抽出的可复用模式。

最小单位是一个有证据的**承诺—因果—兑现窗口**：

```text
读者承诺 / 期待对象
→ 具体压力或利益损失
→ 主角/关键人物的主动选择
→ 因选择产生的局势变化 / 第二次压力
→ 前置优势与已付代价共同促成的转折
→ 读者可观察的兑现证据
→ 资源/身份/关系/规则/信息等不可逆变化
→ 余震与下一剧情输入
```

情绪窗口可以覆盖 3–5 章，也可以跨 10–40 章，但不强制固定章数；结构上的「拍」不必逐拍映射成一章。一章可多拍，多章也可共享一拍。

## 2. 三层检索，防止情绪空转

1. `EMOTION_CONTOUR`：读者体验，如压制→加压→热血兑现、怀疑→证据→认知反转、竞争→互证→关系升温、惊奇→试验→收获。
2. `EMOTION_GENERATOR`：真实因果驱动，如稀缺/身份拒绝、资源归属争议、对手主动反制、错误认知、困难选择、公开验证或角色利益冲突。
3. `PAYOFF_STATE_CHANGE`：兑现到底改变了什么，如资源、身份、能力、关系、信息、目标、制度；改变必须能为下一次事件提供输入。

有轮廓而没有 generator 或状态变化的，只能作为 `EMOTION_IDEA`，不得标为可重用完整模板。

## 3. Emotion Wave / Mechanism Wave / DNA Waves

### E0 — 用户意图及读者承诺

冻结用户原始 brief，不得把 Planner 补出的「公开验证、固定协作、资格争夺」写成用户原话。保存 `raw_brief` 与 `working_hypotheses` 两条不同查询来源。

选择 2–3 种候选读者承诺及其目标情绪、失败代价和变化方式；用户未确定时保持 `OPEN_DESIGN_SPACE`。

### E1 — 情绪窗口候选

从合规来源或本次原创推演构造 `emotion_patterns[]`。每个包含：
- `pattern_id / source_kind / reader_promise`；
- 至少三拍 `beats[]`，每拍含 `reader_emotion / expectation / causal_event / character_agency / state_change`；
- 第二拍起的 `depends_on_prior`；
- `visible_payoff / aftermath`；
- 如果来自 research，附 `source_evidence_refs / research_source_path / research_file_sha256 / source_publication_status=RESEARCH_NOT_ACTIVE`；draft 根必须填写 `research_root` 绝对路径，校验器实际读取 chapter_emotion.jsonl，核对源文件 SHA-256 和所有引用章节的 `qa_status=PASS`。

研究模式还须保留具体 `BOOK/CHAPTER`、证据范围、承诺账本和 QA。当前验证器能核对**本地挂载的研究源文件**及逐章 QA，但不能自动证实远端 git commit 身份，也不能从结构证据自动证明读者情绪判断正确。研究情绪只能标为非 active 参考。

### M0 — 机制选型（非锚定）

再根据 `raw_brief` 与 `emotion_patterns` 查询 RMF，分别保存原始查询和扩展查询，避免扩写污染 Wave 0 排名。

机制库解释「什么能长期重复」，情绪窗口解释「读者为什么期待重复」。任何 RMF recipe / link 都必须逐项检查输出—输入桥接、成员身份及 failure modes；不能用“剧情差不多”替代接口。

### D1 — 由情绪需求派生创作槽位

情绪拍中的每一种运行需求下发到 02–09：

| 交付物 | 必须至少检索或显式解释缺口的模块 |
|---|---|
| 成长循环 `growth_loop` | 02 金手指、03 世界、04 修炼 |
| 主线发动机 `story_spine` | 06 主线与支线 |
| 开篇 `opening` | 07 开篇 |
| 阶段高潮 `major_climaxes` | 08 篇章结构 |
| 长期可复用剧情机制 `repeating_plot_engine` | 09 剧情机制 |
| 人物与关系 `relationships` | 05 人物 |

模块覆盖按**实际交付物**判断，不机械要求每个轻任务都查八模块。若声明设计了前3章/两次大高潮/长线剧情，必须覆盖相应 07/08/09；不得仅在三案中随意叙述而不做调度。尚未覆盖需显示 GAP/HOLD，不得报告完成。

生产检索 06–09 时必须用 `--include-per-book`；不将空查询结果直接解释为库中无素材。组件级别的 03/04 使用已有 `--components`，06/08/09 的嵌套数组在当前检索器中还未完整展开，选中父记录后必须读取完整原记录并定位 `component_path`，不得只用扁平化摘要；后续可另行升级细粒度索引。

### D2 — 来源—接口—组合三轴

**Source trust**：通过 production manifest/hash gate，`record_id + book_id + source_path` 严格定位真实 per_book 行；`component_path` 下钻真实组件并校验证据引用；来源 QA=PASS 仅证明可用来比较/创作，不代表与新书兼容。

**Interface readiness**：描述组件实际 `inputs / outputs / dependencies / constraints / unknowns`；判断 `READY / PARTIAL / HOLD`。语义判断要读完整源组件，不能只凭词面排名；来源 QA=PASS 但接口不全可保持 PARTIAL，不能回改源书 QA。

**Current compatibility**：对**本书选中的**两个组件的输出和输入进行逐对检查：
- `DIRECT_FIT`：具体输出 token 与输入 token 相同，且源组件语义成立；
- `ADAPTABLE`：有可执行的原创适配桥，桥必须有 `new_rule / cost_or_constraint / changed_state / why_causal / provenance=ORIGINAL_DESIGN`；
- `HOLD`：关键事实未知或尚需来源回查；
- `HARD_CONFLICT`：两组件核心规则互斥，换素材/改组合；不能改原书事实冒充解决。

`DIRECT_FIT` 的 token 对上只是**机器必要条件**，不是语义充分条件；`ADAPTABLE` 桥满足字段也只是**结构通过**。语义正确性仍需专家/GPT 审核并写理由。机器 validator 禁止在报告中自称给予文学或创作的最终批准。

### D3 — 新书原创实现

保留 `来源事实 → 可复用机制/组件 → 创作适配桥 → 新书实现` 四层区分。来源事实不可被改写；新书原创桥不是来源引用；市场对标只贡献结构 lesson，不进入来源书证据池。

输出 `world + gold_finger + cultivation + plotline` 的可运转组合及其情绪目的，而不是把四段摘要串接。检查资源是真的可支配、可消耗、规则可知；权限或名誉不是自动可消耗的修炼输入。检查人物行动真实改变情绪兑现，不能把女主当旁观器。

### D4 — 机器结构 QA 与人审停点

试作三案时使用 `scripts/validate_emotion_creation.py <emotion_draft.json>`，要求正式活跃包、来源链、接口完整、情绪因果、交付物覆盖及组合桥。结果 `ok=true` 只表示已检查的结构约束 PASS，`creation_approval` 永远是 `NOT_GRANTED`。

要落正式 V1.2 plan 时仍须运行 `scripts/validate_creation_plan.py <plan.json>`；如 `creation_method=EMOTION_FIRST` 则还需通过 `--emotion-draft <emotion_draft.json>` 联合验证（如果使用独立创作候选档，可先单独验，再等用户确认落 plan）。

任何 `SOURCE_GAP`、`RETRIEVAL_GAP`、`INTERFACE_GAP`、`ADAPTATION_REQUIRED`、`CREATIVE_OPEN_CHOICE` 必须有原因与 next_action；只有 `CREATIVE_OPEN_CHOICE` 可带明示原创候选实现。无适配不能反过来更改 source QA 或谎称素材不存在。

## 4. 成功尺度与停点

所谓「80% 自动组合」，用于**人工测量**：目标槽位中有真实来源定位、已理解接口、可执行桥/直接兼容、可交用户修改的比例。不能按命中关键词数、QA=PASS 卡数量或三案字数冒充完成率。

硬条件没有加权抵消：成长回路资源接口、连续剧情因果、主要人物行动、高潮对下一阶段的状态改变，只要有不可解释的核心冲突，不能用其它“80%”掩盖。

候选输出停于 `READY_FOR_BOOK_DIRECTION_SELECTION` + `STOP_FOR_HUMAN_REVIEW`；没有用户批准，不写正式小说资料、章纲、正文。