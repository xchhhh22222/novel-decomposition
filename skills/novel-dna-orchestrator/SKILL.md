---
name: novel-dna-orchestrator
description: 统筹批量小说拆解成果、逐章读者情绪、横向专项候选、大小高潮脉络、人物个体卡与小说 DNA 总索引。用户要求规划或维护拆书流水线、补章节情绪层、提取高潮脉络、汇总人物候选或把拆书结果整理成可辅助开书的索引时使用；不代替专项元素拆解，也不直接把候选写成正式套路卡。
---

# 小说 DNA 拆书总控

## 目标

把已有或新增的拆书证据组织成可追溯的四层系统：

`源文与章节事实 → 逐章情绪层 → 横向专项候选 → 人工可审的总索引`

本 Skill 负责边界、位置、状态、依赖和验收，不包办金手指、世界观等专项分析。专项内容由对应 Skill 生成候选；正式入库继续交给 `fanqie-material-curator` 审核。

## 模式路由

- **初始化目录、任务清单或总索引**：读取 [references/library-layout.md](references/library-layout.md) 与 [references/integration-and-qa.md](references/integration-and-qa.md)。
- **补逐章情绪层或审计节奏**：读取 [references/chapter-emotion-schema.md](references/chapter-emotion-schema.md) 与 [references/integration-and-qa.md](references/integration-and-qa.md)。
- **只校验情绪覆盖文件**：运行 `scripts/validate_chapter_emotions.py <jsonl> --expected-book <BOOK_ID> --expected-range <起章-止章>`。草稿确需保留HOLD/FAIL时额外使用 `--allow-nonpass`，但该结果不能通过G2。
- **调度金手指、世界观、人物等专项代理**：读取 [references/horizontal-specialist-contract.md](references/horizontal-specialist-contract.md)。
- **只查看现有拆解覆盖度**：运行 `scripts/build_master_index.py --library <素材库路径>`；不必加载全部 reference。
- **女主、长线反派、大故事线**：分别路由到 `novel-character-card-miner` 的 `heroine-library.md`、`long-arc-villain-library.md`，以及 `novel-arc-structure-miner` 的 `major-storyline.md`；最后用总索引检查三库覆盖，不从人物功能或阶段记录冒充已拆卡。

不要为了保险一次读取所有 reference。

## 专项注册表与依赖顺序

总控派发时必须按下表选择唯一主执行 Skill；相邻专项只作为引用接口，不得互相代写。若某个 Skill 不可用，记录缺口并停止该专项，不得让其他专项凭模型记忆补齐。

| 层级 | 唯一主执行 Skill | 默认目录 | 必要上游 |
| --- | --- | --- | --- |
| 逐章情绪 | `novel-chapter-emotion-miner` | `01_章节情绪/` | G1 章节事实 |
| 金手指 | `novel-golden-finger-miner` | `02_金手指/` | G1；情绪接口优先使用 G2 |
| 世界观 | `novel-worldbuilding-miner` | `03_世界观/` | G1 |
| 修炼体系 | `novel-cultivation-system-miner` | `04_修炼体系/` | G1 |
| 人物功能与标签 | `novel-character-function-miner` | `05_人物功能与标签/` | G1 |
| 主线与支线 | `novel-plotline-miner` | `06_主线与支线/` | G1 |
| 开篇 | `novel-opening-miner` | `07_开篇/` | G1 与冻结的开篇范围 |
| 篇章结构 | `novel-arc-structure-miner` | `08_篇章结构/` | G1 与阶段边界证据 |
| 剧情机制 | `novel-plot-mechanism-miner` | `09_剧情机制/` | G1；可引用已完成的线路/阶段接口 |

推荐顺序为 `G1 → 逐章情绪 → 八个横向专项的单书包 → 各专项横向近邻/聚类 → 总索引`。八个横向专项的单书抽取可并行，但跨书聚类必须等待该专项所有目标书均有且仅有一条 `per_book` 或 `gap` 完成声明。逐章情绪是节奏主轴，不替代世界观、人物、线路或机制证据；其它专项也不得反向改写 canonical 章节情绪记录。

开书复用另加三类**派生视图**，不改上述八专项 canonical schema：`novel-arc-structure-miner` 的 `climax-map.md` 从 arc、线路、情绪证据提取大小高潮因果脉络，并用 `major-storyline.md` 单独提取一条完整大故事线的对抗推进、主角收益、反派计划受损与下一线入口；`novel-character-card-miner` 将女主、长线反派分成两个有行为证据的个体候选库，与人物功能专项互补。三类视图都保留已拆章节范围、QA、证据引用和 `candidate/UNKNOWN` 状态；旧书尚未补齐这些派生视图时，总索引必须标缺口，开书总控不得假装已有完整人物库或全书高潮图。

## 不可省略的边界

1. 保留已通过质检的章节事实，不因格式升级重写全文；新增信息优先写覆盖层或候选层。
2. 读者情绪与角色心情分开记录。每章必须说明读者被要求期待、担心、愤怒、感动、轻松或获得何种爽感，以及可观察的兑现证据。
3. 击杀、升级、拿资源、获奖只是事件结果；没有公开结果、他人反应、关系动作、代价回响或选择验证时，不自动记作情绪兑现。
4. 横向专项代理一次只研究一种元素。世界观依赖可以作为金手指接口字段记录，但不得顺手生成世界观母卡。
5. 专项产物先进入 `candidate`。总控不得把单书推断、无来源结论或尚未聚类的结果升级为 `active`。
6. 所有抽象结论必须带 `evidence_refs`，至少能回到书籍、章节或阶段。证据不足写 `UNKNOWN`，不得补造。
7. `QA FAIL` 会阻断下游聚合。关键字段含 `UNKNOWN` 时，整条记录不得标记 `HIGH` 置信度。
8. 市场等级、研究价值、拆解范围、证据置信度是四个不同字段；缺少榜单数据时使用 `UNGRADED`，不得以拆解深度冒充市场评级。
9. 写入前说明准确路径、操作类型、内容范围和覆盖风险并取得授权。总索引默认只读预览；带 `--output` 才落盘。

## 总控工作流

1. **盘点**：列出书单、现有章节范围、QA状态、BOOK DNA、缺失的情绪层和专项层。
2. **冻结证据范围**：为本批任务记录书籍ID、来源路径、章节范围和已知缺口；不静默扩大范围。
3. **补逐章情绪**：按章节事实生成情绪覆盖记录，不覆盖原章节拆解。优先补前五章，再补全书。
4. **派发专项**：向每个专项代理提供同一书单、允许读取的证据层、输出目录和禁止越界项。并发数量服从当前可用代理槽位，不写死代理数。
5. **汇收候选**：检查专项记录的来源、原子性、置信度、相近母型和 `UNKNOWN`。
6. **建立总索引**：把书籍、逐章情绪覆盖、专项候选、正式卡和缺口放入同一张导航表，但不把候选混成正式事实。
7. **人工决策**：需要合并、拆分、升级为正式素材或改变库结构时，列出待定决策点。
8. **正式入库**：用户确认后，交给 `fanqie-material-curator` 做 `NEW / MERGE / SPLIT / HOLD` 与索引重建。

## 多代理约束

- 当用户明确要求批量并发或专项子代理时，每个代理领取互不重叠的书籍批次或单一专项；不得多人同时修改同一正式文件。
- 工作代理只写各自候选分片；总控在全部分片完成且通过校验后，统一生成聚类和总索引。
- 同一本书的阶段聚合必须等待对应章节事实完成；横向聚类必须等待全部目标书的同类专项包完成。
- 失败分片只重跑其负责范围，不重做已通过的书籍。

## 完成标准

- 每本纳入统筹的书都有明确章节范围、QA状态和证据置信度。
- 每个已覆盖章节都有一条情绪记录，或被明确列入缺口清单。
- 每个专项候选都有书籍来源、章节证据、母型近邻和状态。
- 总索引能区分 `evidence / candidate / active / deprecated`。
- 随机选择一个开书需求时，能够从索引找到金手指、情绪节奏和相关候选，而不必读取全部原文。

## 三类派生库的验收

盘点及总索引必须分别显示女主人物卡、长线反派卡、大故事线卡的可用数量和缺口。不得用 `05_人物功能与标签/per_book` 的功能记录冒充个体卡，也不得用 `08_篇章结构/per_book` 的阶段结局冒充完整大故事线。三类卡均由对应专项 Skill 负责，默认是 `candidate`；跨书比较要等各目标书完成本类视图或给出明确 gap，未回填的旧书显示 `未回填`。
