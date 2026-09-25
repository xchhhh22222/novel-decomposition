# Codex 批量重拆 Nova 素材库：目标10本

## 0. 任务身份

这是一次 clean rebuild，不是在旧素材上补丁式修修补补。

- 总控/监控代理：优先 GPT-5.6 Sol。
- 工作子代理：优先 GPT-5.6 Luna，通过多个互不覆盖的子代理并发拆书。
- 若当前 Codex 环境不能显式指定模型，保持同样的“Sol总控 / Luna工作代理”角色契约，并在最终报告写明实际可用模型。
- 总控不得亲自把10本顺序拆完；它负责冻结输入、分配书籍/专项、监控覆盖、处理失败分片、最终QA与提交。

## 1. 私有仓库

只读源书：xchhhh22222/nova-source-books
拆书规则：xchhhh22222/novel-decomposition main（要求拆解 V1.5 或更高）
写入目标：xchhhh22222/nova-material-library

源书仓库禁止修改、删除、重命名。不要把TXT复制进素材库。

建议在 nova-material-library 新建分支 nova-rebuild-10-v1.6；从当前 clean pilot 分支 pilot-batch-4-readable-rebuild 或其最新可用等价基线开始。不要覆盖 LEGACY_ARCHIVE。

## 2. 数量预检

目标是10本不同源书。执行前枚举 nova-source-books 根目录 TXT，按真实文件 SHA 冻结书单。

当前写本任务时仓库只有9本TXT：
1. 高武：从临时工到武镇周天！ - 后知后觉丶.txt
2. 一毛一天修为，我靠直播氪穿宇宙 - 轻费.txt
3. 全民英雄协会：开局招募一拳光头 - 少林呱呱.txt
4. 全民法宝：我的人皇幡无限进化！ - 傀儡道人.txt
5. 你管这叫精神病？这分明是先知！ - 要被榨干.txt
6. 全民神祇：我的神域有点不对劲 - 沐沐见长青.txt
7. 猎魔人小姐，我真不是血族 - 爱收集邮票的飞鸟.txt
8. 青梅是天命之女？可我既是天命！ - 风中云雀.txt
9. 高武：看不起斩魄刀，流刃若火呢 - 一叶墨白.txt

如果执行时已出现第10本TXT：纳入批次并拆满10本。
如果仍只有9本：先完整重拆9本，但最终批次状态必须写 SOURCE_COUNT_SHORTFALL: 9/10；禁止复制一本、重复BOOK_ID或从外网私自补一本凑数；跨10本最终聚类保持 HOLD，等待第10本。

## 3. clean rebuild 原则

- 每本只以对应源TXT为事实主源；旧素材库只允许用于路径/BOOK_ID迁移参考，不允许作为内容证据。
- 先做章节审计：章数、连续性、重复章、异常标题、source SHA、行数/字符数。
- 所有结论能回到章节证据；未知写 UNKNOWN/GAP，不补造。
- 强IP衍生书可以保留 canonical 原名用于证据追踪，但 Planner-facing derived 层只能输出抽象机制，必须做IP安全门。

## 4. 每本必跑层

每本至少完成：
01 章节情绪 + promise ledger + rhythm audit
02 金手指
03 世界观/规则/势力生态
04 修炼体系：systems/realms/relations/techniques/artifacts/resources
05 人物功能
05-derived 人物个体卡：heroine_character + long_arc_villain
06 主线与支线
07 开篇
08 篇章结构 + 大故事线/高潮图
09 剧情机制
额外：combat_asset_inventory、combat_expression_assets、非主角战斗能力覆盖、装备/资源成长审计。

### 人物层硬要求

heroine_character：每位合格女主/关键女性单独一张卡，记录独立目标、决策规律、资源与限制、边界、至少两次有后果主动选择、与主角不得不接近/合作/竞争的原因、替代路径为何不成立、绑定解除条件、关系阶段变化、个人弧线与证据。多位女性分别建卡，绝不预设唯一女主。

long_arc_villain：每位合格长线反派单独一张卡，记录目标、资源/杠杆、计划步骤、与主角为何不可兼得、跨阶段交锋、局部损失、失败后的策略调整、结局或未决状态。一次性Boss不硬凑成长线反派。

若某书无合格女主或长线反派：必须写 derived_gap，coverage_status=checked_no_qualifying；证据不足则 insufficient_evidence。不能用空目录表示完成。

建议路径：books/BOOK_xxx/05_人物功能/derived/heroine/BOOK_xxx.jsonl 与 books/BOOK_xxx/05_人物功能/derived/long_arc_villain/BOOK_xxx.jsonl。

## 5. 人读报告

每本固定维护 books/BOOK_xxx/00_给用户看的拆书报告.md。除原有体系/功法/武技/装备/金手指/势力/剧情机制外，必须新增：
- 女主与关键女性：谁合格、她自己的目标、关系发动机、可迁移结构；
- 长线反派：目标、计划、升级方式、与主角的必要冲突；
- 若无合格对象，明确写“已检查，无合格对象”，不能省略。

## 6. 多代理并发

总控先按“书籍”切分第一层子代理，避免多个代理写同一本书同一路径。每个书籍代理内部可再按专项分解只读分析，但最终由该书籍owner合并。

推荐同时保持3—5个Luna工作代理，依据当前代理槽位自动调整，不写死并发数。一个代理失败只重跑它负责的书/专项，不重做其它PASS书。

总控每完成2—3本做一次中间QA：检查章节覆盖、人物卡/gap、combat inventory、source refs、manifest。发现系统性问题立即修流程后再继续，不能等10本全错完。

## 7. 单书完成门

只有同时满足才可 COMPLETE_SINGLE_BOOK：
- source audit PASS；
- 9个canonical模块 PASS；
- chapter emotion 100%覆盖；
- combat_asset_inventory PASS；
- combat_expression_assets PASS；
- heroine_character 有卡或明确gap；
- long_arc_villain 有卡或明确gap；
- 人读报告已同步；
- manifest记录source SHA/章数/模块/人物派生层状态；
- 不存在把人物功能标签冒充人物个体卡的情况。

## 8. 批次完成后

全部目标书完成后再进行跨书近邻/聚类与Planner-facing候选整理。若只有9/10，允许9本单书全部COMPLETE，但十本批次总状态必须HOLD_FOR_SOURCE_10。

最终输出一份 batch QA：每本章节数、所有模块状态、heroine卡数量、long_arc_villain卡数量、combat人物数量、technique/artifact/resource数量、gap、IP风险、commit SHA。

## 9. Git提交

所有内容提交到私有 xchhhh22222/nova-material-library 的批次分支。分书小提交可以存在，但最终必须有一个批次验收提交。不要向 public repo 推送源文或拆出的长篇原文。

最终报告只给：RESULT、TARGET/AVAILABLE、BOOK_STATUS表、QA失败项、分支、最终commit SHA、是否可以进入 Planner V1.6 验收。