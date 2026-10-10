# Emotion-first Workflow V1 — Phase 1 首次真实运行报告

## 1. 运行边界

- 日期：2026-10-10（Asia/Shanghai）
- 代码仓：`xchhhh22222/novel-decomposition`
- 分支：`research/emotion-first-skill-workflow-v1`
- 运行前基线：`a3c544770e53755df7bf5518b2406249e3d2e0f6`
- 输入：`research/emotion-arc-v2/fixtures/emotion-first-phase1/sparse-brief.json`
- 02–09 冻结素材仓：`xchhhh22222/nova-material-library@1e10e6e3ffb70eda94a400073155fd89db724ce9`
- 情绪研究包：BOOK_001 `book001-derived`，保持 `candidate/HOLD/RESEARCH_NOT_ACTIVE`
- 未修改：`main`、canonical、RMF、production、冻结素材仓；未创作小说正文。

本次严格先运行新增单元测试，再执行 `prepare`。旧版语义任务完成并保存后，才读取增强版 prompt 与情绪检索结果。该执行顺序由人工操作遵守；机器状态仍诚实记录为 `REQUESTED_NOT_MACHINE_PROVEN`。

## 2. Prepare 与输入冻结

执行入口：

```text
python scripts/emotion_first_workflow_v1.py prepare \
  --brief research/emotion-arc-v2/fixtures/emotion-first-phase1/sparse-brief.json \
  --workspace research/emotion-arc-v2/runs/emotion-first-phase1-real-20261010 \
  --emotion-library <book001-derived>
```

结果：

- phase：`WAITING_FOR_MODEL`
- brief SHA-256：`400ff445aa7ae0b6336a78c022dcd395aff2daeb399ebcb8225474ea86fe3116`
- emotion retrieval SHA-256：`6d265220ac4f7d708a60b43a46c7aa049478c3cb07a28e3f213b3b4d296cd65f`
- 旧版 prompt 不包含情绪检索内容；增强版 prompt 携带真实 EL/EW/MA/AH 记录。
- 运行目录内保留冻结输入、两个 prompt、检索快照和 session。

## 3. 两次隔离语义编排

### 3.1 旧版 Planner 基线

旧版只依据相同 sparse brief 和 02–09 素材检索结果完成，不读取 BOOK_001 情绪检索包。

| ID | 方案 | 核心因果结构 | 大弧入口 |
|---|---|---|---|
| `LEGACY:QUARANTINE_WELL` | 雾井封户 | 水源污染证据、家庭配水与伤害公开权互相制约；主角以不可快速恢复的毒素承载换取检测窗口 | 城区统一水纹指向上游共同源 |
| `LEGACY:ECHO_HUNT` | 裂弓还契 | 传统猎仪会触发血亲回响；主角拒绝旧仪式并承担共享伤势，推动家庭共同改写狩猎契约 | 回响顺序暴露外部诱导信号 |

两案均为本轮新构思，没有复用《九灯旧巷》或《背山迁途》的现成剧情，也不是仅替换专名的同一因果结构。

### 3.2 E2/E3 增强版

增强版在旧版产物落盘后，使用真实 BOOK_001 情绪索引及 EL/EW/MA/AH 研究记录进行抽象迁移。

| ID | 方案 | 核心因果结构 | MA-A 兑现 | MA-B 提前启动 |
|---|---|---|---|---|
| `ENHANCED:ASH_SEED` | 灰穗封仓 | 主角烧毁受染仓格，因“毁掉冬种”被误解；以封闭修炼支路为代价承载灰谱，家人掌握种谱、灌溉和仓权并改变方案 | `ES7`：净种、冬粮、能力公共验证、家庭监督权和冬储合同同时具有见证节点 | `ES5`：跨地盐封批号异常；只揭示受限线索，不预支责任结论 |
| `ENHANCED:SILENT_BELL` | 断钟静守 | 主角割断会招兽的警钟绳，因“切断求援”被误解；以持续听损承载回响，家人掌握路线、信号与户籍并改变撤离方案 | `EB7`：家庭安全、能力代价、共同决策和正式静默协议具有独立见证 | `EB5`：官图与现场兽迹矛盾；只开启核查义务，不提前公布调查答案 |

两案均显式保留四条独立情绪线：家庭保护、成长代价、人物关系行动权、长期制度/势力压力。新宏弧没有取消旧宏弧的完整兑现合同；AH 复用只作为重叠候选，仍为 `CANDIDATE_UNVERIFIED`。

## 4. 情绪来源与素材适配

增强方案实际引用 BOOK_001 的 `EL001/EL002/EL003/EL005` 及相关 `EW/MA/AH` 研究记录；每条引用均写明相似原因、可迁移抽象和禁止复制的具体事件链。未经验证的接力记录没有被表述为成功范例。

每个增强方案分别建立一套 02–09 功能槽，按功能需求检索后再选择，不把八个素材 ID 无差别挂到所有节点。主要选择如下：

- 灰穗封仓：`GF:BOOK_007`、`WB:BOOK:BOOK_005`、`CS:BOOK:BOOK_005`、`CF:BOOK:BOOK_016`、`PL:BOOK:BOOK_004`、`OP:BOOK:BOOK_005`、`AR:BOOK:BOOK_007`、`PM:BOOK:BOOK_012`。
- 断钟静守：`DA:ABILITY:BOOK_016:010`、`WB:BOOK:BOOK_001`、`CS:BOOK:BOOK_004`、`CF:BOOK:BOOK_008`、`PL:BOOK:BOOK_006`、`OP:BOOK:BOOK_004`、`AR:BOOK:BOOK_014`、`PM:BOOK_017:001`。
- 明确拒绝示例：灰穗封仓拒绝 `GF:BOOK_005`；断钟静守拒绝 `GF:BOOK_007`。拒绝原因、规则冲突、原创适配桥及其对人物行动/代价/兑现的影响均保存在模型产物中。

直接从普通 Windows checkout 读取冻结包时，行尾转换导致完整性哈希不匹配；本次未绕过门禁，而是由工作流从指定 Git commit 导出 blob 原始字节后检索和验证。最终 manifest 锁定仓库、commit 和 package subdir。

## 5. Finalize

第一次 `finalize` 即通过，未发生模型产物整改：

- attempt：`attempt-01`
- process exit code：`0`
- phase：`VALIDATED_RESEARCH`
- structural gate：`PASS`
- errors：`[]`
- warnings：`[]`
- emotion library consumption：`EXECUTED_RESEARCH`
- material adaptation：`REVIEW_REQUIRED`
- creative quality：`PENDING_INDEPENDENT_REVIEW`
- production promotion：`NOT_RUN`

验证覆盖：情绪来源 ID 与检索集合、02–09 来源与冻结 Git 快照、功能槽约束和适配桥、节点级素材作用、四条情绪线状态转换、宏弧兑现条件及见证节点、新旧宏弧重叠、读者知识时序、九段 Story Spine、1–50 章四阶段规划，以及两个候选的因果签名差异。

Windows 默认编码下，`finalize` 的一个后台输出读取线程报告 UTF-8 解码异常，但主进程返回 0，session、attempt 和 validation report 均完整生成且结构门通过。该问题不影响本次模型产物判定，但作为运行环境问题保留。

## 6. 实际测试结果

| 测试 | 结果 |
|---|---|
| `test_emotion_first_workflow_v1.py -v`（在 prepare 前） | 7/7 PASS |
| `unittest discover`（Phase 1 + Bridge） | 15/15 PASS |
| `test_run_emotion_arc_v2_research.py -v` | 7/7 PASS |
| `test_validate_emotion_creation.py -v` | 17/17 PASS |
| `test_validate_creation_plan.py -v` | 13/13 PASS |
| `test_search_dna_package_gate.py -v` | 10/10 PASS |
| `test_search_dna_candidates.py -v` | PASS，0 failures |
| `test_search_mechanism_library.py -v` | 默认编码首次为环境解码错误；`PYTHONUTF8=1` 原样复跑 PASS，0 failures |
| `test_validate_v12_artifacts.py -v` | 6/6 PASS |
| `quick_validate.py skills/novel-creation-planner` | 默认编码首次为环境解码错误；`PYTHONUTF8=1` 原样复跑 `Skill is valid!` |

没有修改测试、validator 或任何通过阈值。

## 7. 尚未解决与独立审核项

1. 创作质量仍需人工语义审核；确定性指标只证明合同、来源和因果义务显式存在，不证明文学质量或市场效果。
2. 两次模型编排的隔离顺序由人工执行，机器只能记录 `REQUESTED_NOT_MACHINE_PROVEN`。
3. AH001 只可作为重叠/接力候选；完整主导权交接继续 `HOLD`。
4. `material_adaptation` 继续为 `REVIEW_REQUIRED`；需人工检查抽象功能迁移是否自然、是否存在来源集中或隐性规则冲突。
5. Windows 默认编码会让部分 Python 子进程输出读取失败；UTF-8 模式可复现通过，生产化前应统一进程编码，但本轮未修改基础设施。
6. 研究状态不等于正式小说事件状态；不得把本次候选直接转入 production 或 Stage 4。

## 8. 裁决状态

```text
EMOTION_FIRST_WORKFLOW = RESEARCH_EXECUTABLE
EMOTION_LIBRARY_CONSUMPTION = EXECUTED_RESEARCH
MATERIAL_ADAPTATION = REVIEW_REQUIRED
CREATIVE_QUALITY = PENDING_INDEPENDENT_REVIEW
PRODUCTION_PROMOTION = NOT_RUN
STAGE_4_CREATION = HOLD
STOP_FOR_INDEPENDENT_REVIEW
```
