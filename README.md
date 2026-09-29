# 小说拆解

一套用于长篇网文拆解、专项提取、证据审计、素材迁移、开书组装、正文创作与连续性维护的 Codex Skills 与工作流。

当前版本：**拆解 V1.6.2**

## V1.6.2 的核心思路

完整拆解与可迁移素材分层保存：

```text
完整拆解
  ↓ 证据审计
迁移候选
  ↓ NEW / MERGE / SPLIT / HOLD
人工确认
  ↓
DNA 候选库 / 原子套路卡 / 开书母型
  ↓
索引重建与反向校验
```

- 整书总结、完整人物弧和长线剧情保留在证据层。
- 正式套路卡严格执行“一卡一机制”。
- 人物卡、大故事线、金手指和世界观优先进入 DNA 候选库，不强行改造成套路卡。
- V1.4 将世界与成长系统组件化：世界观新增 factions 势力生态；修炼体系支持来源书实际存在的 1～N 套 system、独立境界、功法、法宝/装备、资源与体系关系。
- **V1.5 把人物个体卡升级为单书必跑派生层**：人物功能之后必须继续拆 heroine_character 与 long_arc_villain；没有合格对象也要写 gap。这样 Planner 能直接构造多女主、长线反派与人物—势力关系，而不是只看到“商业接口/高阶战力/导师”等功能标签。
- **V1.5.1 增加语义 QA 补丁**：章节情绪在 schema validator 之外强制检查原文章末抽取、字段回声、归一化模板骨架和 SOL 源文抽样；剧情线与剧情机制增加 recall/depth audit；模块 HOLD 不得被 manifest 静默提升为 PASS。\n- **V1.5.2 加固语义归一化**：RAW_ENDING 忽略纯标点与过短尾句；模板骨架可从人物/实体文件或显式实体表读取已知中文实体并归一化为 `<ENTITY>`，防止仅替换人名绕过模板检测。
- **V1.6 升级中控路由**：新增 `FULL_DNA` 与 `SUPPLEMENTAL_MATERIAL` 两种来源角色。完整主书继续跑01—09；素材增强来源先说明 purpose，再只调用被授权的专项与 derived views。Supplemental 仍需扫描授权全文范围保证 recall，但不再被强制要求逐章情绪和九专项齐全。
- **V1.6 新增专项素材 Profiles**：能力/金手指、副本规则、多女主关系、魅力反派、战斗表现等来源可以定向拆解；新来源不得直接 append 到旧 cluster，只对受影响专项启动新的 full recluster 并保留 lineage。
- **V1.6.1 加固 Derived Material Contract**：ability / dungeon / relationship / charismatic antagonist / combat expression 五类补充素材统一为 schema_version=2，统一 `DA:<VIEW>:<BOOK_ID>:<NNN>` ID、字段白名单、精确章节 evidence、manifest 计数和 dedicated validator；历史别名、章节区间 evidence、combat 双层数组会直接 FAIL。
- **V1.6.2 加固 Supplemental 批次门**：新增 route/output 一致性、manifest/batch completion status 一致性、cluster eligibility 三个机器 gate；受控 derived 只有 `qa_status=PASS` 才能进入 nearest_neighbor/cluster，HOLD 只留 inventory；某 view 全部 HOLD 时禁止宣称 full recluster ready。
- 拆书层只还原单书来源事实；创造层允许跨书选择组件重新组合，但组合结果必须标为新书候选，不能写回来源记录。
- 所有结论必须回指章节或已审核证据，模型记忆不能写成来源。

## 目录

```text
workflow/
  00_拆解V1.3入库说明.md
  拆解V1.3入库规则.md
  _模板/
  BATCH_20260923_人物与大故事线迁移/   # 审核示例
skills/
  novel-dna-mining-suite/                # 整套拆书入口
  novel-dna-orchestrator/                # 拆书流水线总控
  novel-chapter-emotion-miner/           # 逐章读者情绪
  novel-character-function-miner/        # 人物剧情功能
  novel-character-card-miner/            # 女主/长线反派人物卡
  novel-golden-finger-miner/              # 金手指机制
  novel-worldbuilding-miner/              # 世界规则 + factions 势力生态
  novel-cultivation-system-miner/         # 多修炼体系 + 境界/功法/法宝/资源
  novel-plotline-miner/                   # 主线与支线
  novel-opening-miner/                    # 开篇结构
  novel-arc-structure-miner/              # 篇章阶段、大小高潮与大故事线
  novel-plot-mechanism-miner/             # 剧情机制
  fanqie-material-curator/                # 素材入库、去重、索引与调用
  novel-creation-planner/                 # V1.2 实时赛道结构学习 + 素材调度 + 高潮倒推
  novel-writer/                           # 小说项目、章纲、正文和资料同步总控
  novel-growth-timeline/                  # 成长、收益、爽点与关系节奏账本
  nova-white-dialogue/                    # 都市高武对白生成、重写与审核
  nova-plus-novel/                        # 长篇小说连续性规划、写作与修订
```

## 使用建议

1. 将完整拆解包放入 `workflow/_模板/` 复制出的新批次目录。
2. 用 `novel-dna-orchestrator` 先给新来源做 FULL_DNA / SUPPLEMENTAL_MATERIAL 路由；用户确认 routing matrix 后再执行。
3. 用对应 specialist Skill 生成候选记录；Supplemental 只跑 target_specialties，但专项内部 QA 不降级。若生成五类受控 derived view，先通过 `validate_derived_materials.py`，再通过 `validate_supplemental_batch.py` 对账 route/output、状态和聚类资格。
4. 用 `fanqie-material-curator` 完成原子化、查重、审核和迁移。
5. 用 `novel-creation-planner` 先研究同赛道新书榜结构，再调度素材库，并从战略目标物/大高潮反推前100章。
6. 用 `novel-writer` 管理章纲、工作稿、正式正文和资料同步边界。
7. 用 `novel-growth-timeline` 审计成长收益与情绪兑现节奏。
8. 按任务需要调用 `nova-white-dialogue` 或 `nova-plus-novel` 完成对白和长篇连续性工作。

Skills 可按需复制到 Codex Skills 目录：

```text
%CODEX_HOME%/skills/<skill-name>/
```

每个 Skill 的具体触发条件、输入边界和产物规范以各自的 `SKILL.md` 为准。

## 安全与版权边界

本仓库只保存工作流、Schema、校验脚本、抽象示例和 Skill 说明。

- 不上传 EPUB、TXT、PDF 或整章原文。
- 不复制原作人物、专名、标志性表达或完整事件链作为原创素材。
- 不上传私人素材库、账号信息、密钥、Cookie 或本机绝对路径配置。
- 示例中的 `candidate` 和 `HOLD` 不代表已进入正式调用池。
