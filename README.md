# 小说拆解

一套用于长篇网文拆解、专项提取、证据审计、素材迁移和开书组装的 Codex Skills 与工作流。

当前版本：**拆解 V1.3**

## V1.3 的核心思路

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
  novel-worldbuilding-miner/              # 世界观
  novel-cultivation-system-miner/         # 修炼体系
  novel-plotline-miner/                   # 主线与支线
  novel-opening-miner/                    # 开篇结构
  novel-arc-structure-miner/              # 篇章阶段、大小高潮与大故事线
  novel-plot-mechanism-miner/             # 剧情机制
  fanqie-material-curator/                # 素材入库、去重、索引与调用
  novel-creation-planner/                 # 从拆书素材组装原创开书方案
```

## 使用建议

1. 将完整拆解包放入 `workflow/_模板/` 复制出的新批次目录。
2. 用 `novel-dna-orchestrator` 规划专项顺序和证据合同。
3. 用对应 specialist Skill 生成候选记录。
4. 用 `fanqie-material-curator` 完成原子化、查重、审核和迁移。
5. 用 `novel-creation-planner` 将通过审核的组件重组为原创开书候选。

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
