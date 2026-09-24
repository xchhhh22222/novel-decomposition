# 实时赛道对标与开篇结构学习 V1.2

本文件负责：

`同赛道新书榜 Top10 → 前10章全样本结构比较 → 选3本结构强样本 → 前20章深拆 → 提取可迁移结构`

它学习的是**结构和节奏**，不是参考书的具体剧情、人物、专名或独特设定组合。

## 1. 赛道输入

用户只需要先给赛道，例如“都市高武”。此阶段不得先假设我们自己的书会是什么设定，也不得按未来故事相似度筛书。

标准样本固定是：**该赛道同一快照的新书榜 Top10。**

Top10 是市场结构样本池，不是“与用户创意最相似的10本”。

## 2. 第一轮：Top10 前10章全比较

在合法可访问范围内，对 Top10 每本都尝试取得第1—10章正文。无法合法读取的书保留榜单位置并标记 `metadata_only / partial / failed`，不得偷偷用榜外书替换。

只有实际读过正文的章节才能进入结构分析。

每本书至少抽取：

```text
sample_id
chapters_analyzed
first_conflict_chapter
first_clear_goal_chapter
golden_finger_reveal_chapter
golden_finger_first_validation_chapter
first_visible_payoff_chapter
first_major_hook_chapter
chapter_1_3_payoff_chain
chapter_4_10_story_loop
goal_relay_pattern
emotion_curve
hook_chain
supporting_character_usage
structure_strengths
structure_weaknesses
evidence_locations
```

没有金手指的作品，相应字段写 `NOT_APPLICABLE`，不能硬套。

## 3. 结构观察维度

### 3.1 冲突启动速度

记录第一场真正改变主角处境的冲突在哪一章出现。只抽象“问题—反应—兑现间隔”，不保留具体人物与事件。

### 3.2 首次兑现速度

“觉醒能力”不自动等于兑现。首次兑现必须有可观察结果：赢下冲突、获得资格、公开结果变化、他人认知改变、拿到阶段资源或真正解决生死危机。

### 3.3 目标接力

检查：`当前目标完成 → 新目标是否立即出现`。

好的快速开篇往往不是“每章都有大事”，而是读者始终知道下一件值得等的事是什么。

### 3.4 情绪链

每章记录主情绪及其来源，例如：`压迫 → 期待 → 爽 → 新危机`、`危险 → 找解法 → 反杀 → 更大危险`。

### 3.5 钩子链

章末钩子至少归类为：

- `unresolved_danger`：危险未解；
- `imminent_payoff`：奖励/兑现马上到；
- `new_goal`：新目标出现；
- `information_reveal`：重要信息只揭一部分；
- `identity_exposure`：身份/秘密将暴露；
- `stronger_actor_entry`：更高层人物或势力介入；
- `relationship_shift`：关系即将变化；
- `countdown`：明确时间窗；
- `cost_reveal`：胜利后代价浮现。

除了“钩子是什么”，还必须写“为什么读者需要点下一章才能得到答案”。

## 4. Top10 横向矩阵

完成前10章后生成 `benchmark_matrix`，按结构学习价值比较：

1. `conflict_latency`；
2. `payoff_latency`；
3. `goal_relay`；
4. `hook_strength`；
5. `emotion_progression`；
6. `chapter_4_10_loop`；
7. `supporting_character_efficiency`；
8. `structural_clarity`。

评分只服务筛选，不代表文学价值。

## 5. 选择3本深拆书

从 Top10 里选3本的标准是：**结构最值得学，并且三本尽量提供互补长处。**

例如：A 节奏最快；B 章末钩子最稳定；C 目标接力或情绪兑现最好。

三本在内容上可以完全不同，只要属于目标赛道。不得因为“设定和我们想写的相似”而优先入选。

每本保存：

```text
sample_id
selected_reason
primary_strength
secondary_strength
what_not_to_copy
deep_dive_status
```

## 6. 第二轮：3本前20章深拆

对选中的3本继续取得第11—20章。若无法合法访问，保留该书但标 `partial`；不得虚构深拆结果。

每章固定拆：

```json
{
  "chapter": 1,
  "protagonist_goal": "这一章主角现在要什么",
  "obstacle": "什么具体阻止他",
  "protagonist_action": "主角主动做了什么",
  "supporting_character_functions": [
    {"role": "配角/群体", "function": "制造阻碍|提供信息|权威验证|关系推进|资源入口|对照|抬高期待|其它"}
  ],
  "payoff": "这一章兑现了什么",
  "reader_emotion": "主要读者情绪与来源",
  "hook": "章末留下的问题",
  "hook_type": "new_goal|danger|reward|reveal|exposure|actor_entry|relationship|countdown|cost|other",
  "next_click_reason": "为什么必须看下一章",
  "state_change": "这一章结束后什么已经不可逆地不同",
  "evidence_locations": []
}
```

核心四项永远不能缺：`主角目的 / 阻碍 / 配角作用 / 钩子`。

## 7. 从内容抽到结构

来源书可能是：

`武测资格 → 老师质疑 → 主角打破纪录 → 校长单独召见`

可迁移结构只能写成：

`资格目标 → 权威阻碍 → 公开验证 → 超预期兑现 → 更高层入口`

可以学习事件顺序、兑现间隔、情绪节拍、钩子功能、配角功能和目标接力方式。

不得复制人物姓名、原组织名、标志性能力名、独特物品名、连续事件链的具体包装或独特表达。

## 8. 三书横向结构结论

最终输出 `structural_lessons[]`：

```json
{
  "lesson_id": "MK:LESSON:001",
  "pattern": "承诺→两章内首次可见兑现→立即打开更高层目标",
  "observed_in_sample_ids": ["S01", "S04"],
  "best_use_window": "1-3",
  "retention_reason": "旧问题被解决时新问题已经出现",
  "adaptation_rule": "换掉冲突对象、验证场、奖励和新目标，只保留节奏关系",
  "copy_boundary": "禁止复刻原事件链"
}
```

这些 lesson 才能进入我们的新书设计。原书具体事件只保留在证据包里。

## 9. 完成门

完整市场对标要求：

- Top10 排名位置全部保留；
- 至少6本具有完整前10章正文，才能宣称结构横评较充分；
- 选出3本有明确结构长处的深拆书；
- 3本都完成前20章时为 `complete`；
- 少于3本完成20章时为 `partial`；
- 每条结构结论能回指 sample_id 和章节证据；
- 三书选择理由是结构优势，不是内容相似。

市场对标不足不禁止继续使用素材库构思，但必须标记“市场结构验证不完整”。


## 10. 保存契约

需要落盘时，`market_benchmark.json` 顶层至少为：

```json
{
  "schema_version": 1,
  "benchmark_id": "MK:YYYYMMDD:都市高武",
  "status": "complete",
  "category": "都市高武",
  "snapshot_at": "YYYY-MM-DD",
  "selection_rule": "structural_learning_not_similarity",
  "top10": [],
  "selected_deep_dives": [],
  "structural_lessons": []
}
```

其中：

- `top10` 必须恰好10条，rank 为1—10；
- `selected_deep_dives` 必须恰好3条；
- `deep_dive_status=pass` 时必须真实覆盖1—20章，并提供20条 `chapter_structures`；
- `status=complete` 时至少6本 Top10 样本完整分析1—10章，并且3本深拆都完成1—20章；
- `selection_rule` 必须固定为 `structural_learning_not_similarity`。

校验：

```powershell
python -X utf8 scripts/validate_v12_artifacts.py benchmark market_benchmark.json
```
