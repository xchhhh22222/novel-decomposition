# 跨书共享素材库（V1.1 调度入口）

素材库是创作基础设施，不属于任何一本小说。推荐目录：

共享素材库路径由项目配置或用户当前指定；本文档统一记为 `<SHARED_LIBRARY_ROOT>`。

```text
<网文创作公共资产>/
├─ 素材库/                 # 正式 active 卡、索引、DNA candidate
├─ 拆书入库区/             # 其他 Agent 的候选产物，未审核前不进入正式库
├─ 市场样本/               # 按日期保存的榜单和公开开篇，禁止混入正式素材
└─ 归档/                   # 迁移快照与弃用版本
```

## 路径解析

1. 用户本次明确给出的素材库路径；
2. 当前创作任务配置中声明的 `shared_library_root`；
3. 已确认的公共资产目录；
4. 都不存在时停止正式检索并请求路径，不得自动把当前小说的 `素材库/` 当成公共库。

运行命令必须传入绝对路径：

```powershell
python "<material-curator>/scripts/material_library.py" search --library "<共享素材库绝对路径>" --query "<功能词>" --modules "<模块>" --limit 12
python "<novel-creation-planner>/scripts/search_dna_candidates.py" --library "<共享素材库绝对路径>" --query "<功能词>" --modules "<模块>" --include-per-book --limit 12 --format json
```

## 迁移规则

移动正式库前先审计所有引用、索引内路径、工具脚本和项目配置。优先采用“复制到公共目录 → 只读审计 → 修改调用方 → 前向检索测试 → 用户确认后停用旧库”，不要直接剪切。市场样本与拆书候选不得并入正式 active 卡目录。

每本小说只保存自身状态：总纲、世界观、人物、章节、伏笔、成长时间线和素材调用记录；跨书套路卡、BOOK DNA 与拆书证据只保存在公共资产目录。


## V1.4 组件检索约定

创造层检索 `03_世界观` 时，优先区分规则链与 `factions`；检索 `04_修炼体系` 时，优先读取 `schema_version: 2` 的 `cultivation_systems`、`system_relations`、`techniques`、`artifacts`、`resource_assets`。

跨书组合时必须保留每个组件的来源 `book_id / record_id / chapters_covered / qa_status`。组合后的新设定属于创作项目，不得回写共享库中的来源 `per_book`。


## V1.1 调度纪律

共享库不是一次性全文读取的数据仓。创造层先读取 `material-dispatch.md` 建立槽位，再按槽位调用：

- 正式套路卡：适合情绪、叙事机制和经过审核的原子结构；
- cluster：适合先找“运行母型”；
- per_book：适合核验来源与完整上下文；
- component：适合直接找 faction / system / realm / technique / artifact / resource。

默认使用“先宽后窄”的检索阶梯，不直接遍历全部 JSONL。

组件级检索返回的 `component_id` 仍必须保留其 `source_record_id / book_id / path`，因为组件脱离来源后可能丢失兼容前提。
