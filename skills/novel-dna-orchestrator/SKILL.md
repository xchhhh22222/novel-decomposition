---
name: novel-dna-orchestrator
description: V1.6.3 小说 DNA 中控：在 V1.6.2 批次门上继续加固 UNKNOWN 语义、Combat PASS 最低条件与 batch 汇总一致性；防止“格式 PASS、语义不够”和陈旧 HOLD 统计进入聚类。
---

# 小说 DNA 拆书总控 V1.6.3

## 目标

V1.6 的核心变化：**不是每一本来源都默认完整跑 01—09。**

新增来源先回答：

```text
这本书为什么进入 Nova？
→ 它要补哪个素材缺口？
→ 应调用哪些 specialist？
→ 哪些专项明确不运行？
```

完整主书继续走 FULL_DNA；素材增强来源走 SUPPLEMENTAL_MATERIAL。专项内部 schema/QA 不因中控路由而放宽。

把已有或新增的拆书证据组织成可追溯的四层系统：

`源文与章节事实 → 逐章情绪层 → 横向专项候选 → 人工可审的总索引`

本 Skill 负责边界、位置、状态、依赖和验收，不包办金手指、世界观等专项分析。专项内容由对应 Skill 生成候选；正式入库继续交给 `fanqie-material-curator` 审核。

## 模式路由

- **新增来源第一步**：读取 [references/source-role-and-routing.md](references/source-role-and-routing.md) 与 [references/supplemental-profiles.md](references/supplemental-profiles.md)，先输出 routing matrix，未经用户确认不得写正式拆解结果。
- **FULL_DNA**：沿用旧完整主书流程。
- **SUPPLEMENTAL_MATERIAL**：只调度 source_route.target_specialties；未授权专项不得自动补跑。
- **Derived Material V1.6.1**：若路由包含 ability_assets / dungeon_rule_assets / relationship_engine_assets / charismatic_antagonist_assets / combat_expression_assets，必须读取 [references/derived-material-contract.md](references/derived-material-contract.md)，禁止代理自由发明字段。
- **Derived 校验**：运行 `python scripts/validate_derived_materials.py --root <material-library-root> --books <BOOK_ID,...>`；未 PASS 不得进入 supplemental full recluster。
- **V1.6.2 批次一致性门**：读取 [references/supplemental-batch-gates.md](references/supplemental-batch-gates.md)，运行 `python scripts/validate_supplemental_batch.py --root <material-library-root> --batch-dir batch/<BATCH_ID> --books <BOOK_ID,...>`；route/output、manifest/batch status、cluster eligibility 任一不可解释时禁止聚类。
- **V1.6.3 Combat 语义门**：存在 `combat_expression_assets` 时，额外运行 `python scripts/validate_combat_semantics.py --root <material-library-root> --books <BOOK_ID,...>`；UNKNOWN 必须是字面值，PASS 核心字段不得 UNKNOWN，且 cost/limit/counterplay 至少一项有证据。
- **V1.6.3 Batch Summary 门**：`validate_supplemental_batch.py` 还必须对账 `batch-status.derived_hold_records` 与五类 controlled derived 的真实 HOLD 总数，并核对 `derived_totals`。
- **聚类资格**：五类 controlled derived record 只有 `qa_status=PASS` 才能进入 nearest_neighbor / KEEP_SEPARATE / cluster；`qa_status=HOLD` 只保留 inventory。若某个需要重聚类的 view `eligible=0 && records>0`，则 `full_recluster_ready=false`。
- **修复历史 V1.6 supplemental 输出**：读取 [references/derived-normalization-playbook.md](references/derived-normalization-playbook.md)；默认只做 normalization，不重拆正文，不新增资产。
- **Combat HOLD 补强/收口**：读取 [references/combat-evidence-backfill.md](references/combat-evidence-backfill.md)；Evidence Backfill 与 Semantic Refinement 必须分两阶段，不能把“找到更多证据”直接等同于 PASS。
- **路由校验**：运行 `python scripts/validate_source_routes.py <source_routes.jsonl>`；未 PASS 不得派发 specialist。
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

FULL_DNA 推荐顺序仍为 `G1 → 逐章情绪 → 八个横向专项的单书包 → 人物个体卡(heroine/long_arc_villain)派生视图 → 各专项横向近邻/聚类 → 总索引`。

SUPPLEMENTAL_MATERIAL 改为 `routing gate → 授权专项全文扫描 → 必要局部 emotion overlay → target_specialties per_book/derived/QA → 批次结束后受影响专项 full recluster`。跨书聚类只等待“本专项实际路由到的来源集合”，不是等待整批所有书。

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

## 总控工作流 V1.6.3

1. **盘点来源**：列出新 TXT、现有 BOOK_ID、重复来源和源文范围。
2. **路由**：为每本来源生成 source_route，判断 FULL_DNA / SUPPLEMENTAL_MATERIAL、purpose、target_specialties、derived_views、excluded_specialties。
3. **先审 routing matrix**：只展示路由，不写正式拆解结果；等待用户确认。
4. **冻结证据范围**：确认 source file、chapter_scope、allowed_sources、known_gaps。
5. **按路由派发**：
   - FULL_DNA：完整 01—09 + 必要派生视图；
   - SUPPLEMENTAL：只运行 target_specialties；全文扫描授权范围保证 recall。
6. **专项 QA**：每个 specialist 继续执行自己的 schema/validator/semantic gate，证据不足保留 UNKNOWN/gap/HOLD。
7. **派生视图**：按 profile 生成 ability / dungeon / heroine / relationship / antagonist / combat-expression 等被授权 view；其中五类 V1.6.1 受控 derived view 必须严格使用 canonical contract，没有证据则明确 UNKNOWN/gap。
8. **Derived 机器门**：检查字段白名单、record_id、精确 evidence ref、nested array、duplicate ID、manifest count；禁止只用人工 contract check 冒充 dedicated validator。
9. **Combat 语义门**：若存在 combat_expression_assets，检查 UNKNOWN canonicalization、PASS 核心字段、constraint 最低证据与 unknowns 污染；未 PASS 不得聚类。
10. **批次一致性门**：对账 source_route.derived_views 与真实 derived outputs；对账 manifest.status 与 batch-status；生成 controlled derived 的 eligible/held ID 列表。
11. **单源完成判定**：
   - FULL_DNA → COMPLETE_SINGLE_BOOK；
   - SUPPLEMENTAL → COMPLETE_SUPPLEMENTAL_SOURCE / _WITH_HOLDS / BLOCKED。
12. **批次聚类**：等该批 supplemental 来源完成后，只对受影响专项开启新的 full recluster；禁止 append 到旧 cluster。
13. **lineage**：新 run 与上一历史 run 比较 stable / split / merge / moved / disappeared / new。
14. **总索引**：区分 primary_full_dna 与 supplemental_material；candidate 与 active 继续分层。
15. **正式入库**：只有单独 promotion 流程可以写 active。

## 多代理约束

- 当用户明确要求批量并发或专项子代理时，每个代理领取互不重叠的书籍批次或单一专项；不得多人同时修改同一正式文件。
- 工作代理只写各自候选分片；总控在全部分片完成且通过校验后，统一生成聚类和总索引。
- 同一本书的阶段聚合必须等待对应章节事实完成；横向聚类必须等待全部目标书的同类专项包完成。
- 失败分片只重跑其负责范围，不重做已通过的书籍。

## 完成标准 V1.6.3

### FULL_DNA
- 明确章节范围、QA、证据置信度；
- 01 全章 emotion 或明确缺口；
- 02—09 每专项 per_book/gap；
- heroine_character / long_arc_villain 有卡或 gap；
- 必需 validator / semantic gate 通过；
- 可标 COMPLETE_SINGLE_BOOK。

### SUPPLEMENTAL_MATERIAL
- source_route 已确认；
- 每个 target_specialty 在授权范围内完成 recall；
- target_specialty 有 per_book/gap；
- derived_views 有卡/记录或明确 gap；
- 五类受控 derived view 若存在，必须 `DERIVED_MATERIAL_CONTRACT_V1_6_1=PASS`；
- 若存在 combat_expression_assets，必须 `COMBAT_SEMANTIC_GATE_V1_6_3=PASS`；
- 必须通过 `SUPPLEMENTAL_BATCH_CONSISTENCY_V1_6_3`；route/output、manifest/batch status、derived totals 与 HOLD totals 必须一致；
- 聚类输入必须使用 batch gate 输出的 `eligible_record_ids`，不得把 HOLD 记录送入 clustering；
- 被授权专项的 validator / semantic gate 通过；
- excluded_specialties 不被误判为缺失；
- 输出 candidate-only；
- 最终只可标 COMPLETE_SUPPLEMENTAL_SOURCE / _WITH_HOLDS / BLOCKED。

任何模式都不得因为“想让库更丰富”而用模型记忆补造来源事实。

## 三类派生库的验收

盘点及总索引必须分别显示女主人物卡、长线反派卡、大故事线卡的可用数量和缺口。不得用 `05_人物功能与标签/per_book` 的功能记录冒充个体卡，也不得用 `08_篇章结构/per_book` 的阶段结局冒充完整大故事线。三类卡均由对应专项 Skill 负责，默认是 `candidate`；跨书比较要等各目标书完成本类视图或给出明确 gap，未回填的旧书显示 `未回填`。
