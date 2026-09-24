# 高潮目标核与前100章倒推 V1.2

默认目标：**先设计前100章约2个大高潮，再从高潮往前倒推。**

百万字级5—6个大高潮可以保留方向种子，但素材与世界尚未成熟时不要假装已经能精确规划100万字。

## 1. 普通资源与战略目标物分开

### 普通成长资源

晶核、丹药、修炼液、材料、积分、学分、军功、货币、兑换资格等，负责日常成长循环：

`获取 → 消耗 → 变强/兑换 → 接更高等级任务`

### 战略目标物 `strategic_target`

战略目标物是能把主角、竞争者和多方势力拉进同一场争夺的“高潮目标核”。

可以是秘典/传承、神兵/法宝、稀有核心、圣果/神血/遗骨、秘境钥匙、唯一资格、禁忌技术、世界秘密、特殊身份或开启下一地图的线索。

名字要有期待感，但不能只剩“听起来牛逼”。

## 2. 战略目标物契约

```json
{
  "target_id": "TARGET:001",
  "name": "候选专名",
  "target_type": "manual|inheritance|artifact|rare_resource|access_key|qualification|secret|technology|identity|other",
  "reader_promise": "读者为什么期待主角拿到",
  "known_function": "当前阶段已知功能；可以只知道一部分",
  "unknown_potential": "允许保留的更大未知",
  "protagonist_need": "主角为什么必须要",
  "rival_needs": ["别人为什么也要"],
  "clue_entry": "最早如何得知它",
  "access_gate": "进入争夺前必须满足什么",
  "location_or_holder": "在哪/谁控制",
  "competing_factions": [],
  "failure_cost": "拿不到会失去什么",
  "payoff_if_obtained": "拿到后立刻改变什么",
  "irreversible_change": "对身份、关系、势力位置或能力路线的不可逆改变",
  "next_stage_seed": "它如何推出下一阶段",
  "material_refs": []
}
```

允许前期只知道“这东西能解决主角当前最致命的问题”，不要求第一章公布完整功能百科。

## 3. 目标物如何从素材库产生

战略目标物是**创造层对象**，不是要求拆书库已有同名物品。

可以组合：

- `artifact` 的成长/激活结构；
- `technique/manual` 的能力承诺；
- `resource` 的稀缺与获取结构；
- worldbuilding 的 faction/resource control；
- arc_structure 的高潮争夺结构；
- plot_mechanism 的竞争、资格、秘境等机制。

必须保留素材来源，但新目标要重新命名、重新设定世界来源和冲突接口。

## 4. 势力先于高潮落位

设计高潮前，先建立实际需要的势力池，例如官方机构、军方、学院、民间公司/集团/财团、家族、公会、地下组织和敌对组织。

不要求每种都存在。

每个核心势力至少回答：

`控制什么 → 想要什么 → 能动用什么筹码 → 与谁冲突 → 何时进入故事`

## 5. 默认两个大高潮

若用户没有指定，前100章默认：

- 高潮1：约第30—45章；
- 高潮2：约第80—100章。

允许按赛道节奏调整，但必须有明确章节窗口。

第二高潮必须由第一高潮的结果推出，而不是重新开一条无关故事。

## 6. 单个高潮契约

```json
{
  "climax_id": "CLIMAX:01",
  "chapter_window": "32-40",
  "strategic_target_id": "TARGET:001",
  "protagonist_goal": "这一阶段必须实现什么",
  "why_now": "为什么不能以后再做",
  "qualification_or_access_gate": "进入最终争夺前的门槛",
  "competing_factions": [],
  "named_rivals_or_roles": [],
  "obstacles": [],
  "information_disadvantages": [],
  "resource_constraints": [],
  "relationship_pressures": [],
  "pre_climax_state": {
    "identity": "",
    "power": "",
    "resources": "",
    "relationships": "",
    "information": ""
  },
  "payoff": "高潮明确兑现",
  "cost": "赢了也付出的代价",
  "irreversible_change": "高潮结束后回不到之前的什么状态",
  "next_stage_seed": "如何自然推出下一阶段",
  "previous_climax_dependency": "第一个高潮写 ROOT；后续高潮写由上一高潮的什么结果推出",
  "material_refs": [],
  "benchmark_lesson_ids": [],
  "backward_beats": []
}
```

高潮不能只是“打一场大的”。至少同时发生三类变化中的两类：重要目标物、身份/势力位置、人物关系、世界信息、能力路线、新敌人/新地图。

## 7. 从高潮倒推

高潮确定后，不从第1章顺推，而从高潮需要的前置状态往回拆：

```text
第38章：拿到战略目标物
↑
第31章：进入争夺地图
↑
第24章：获得资格/钥匙
↑
第18章：确认目标物真实存在
↑
第12章：得到第一条有效线索
↑
第8章：主角发现自己迫切需要解决某问题
↑
第3章：这个问题第一次被验证
↑
第1章：初始困境
```

具体章节可以变，但因果不能倒。

## 8. 倒推锚点 `backward_beats`

每个高潮建立4—8个锚点：

```json
{
  "beat_id": "CLIMAX:01:B03",
  "chapter_window": "18-20",
  "required_state": "主角确认目标物存在且知道进入门槛",
  "objective": "拿到准入信息",
  "obstacle_function": "资格受限",
  "supporting_character_function": "权威验证/竞争者抬压",
  "mini_payoff": "取得部分资格",
  "hook_function": "揭示真正争夺者",
  "leads_to": "CLIMAX:01:B04"
}
```

这里写的是功能，不是照抄对标书事件。

## 9. 注入市场结构 lesson

`structural_lessons` 负责节奏与留存，不提供具体剧情内容。

例如 lesson 是：

`危机在第1章建立 → 第2章给出可执行解法 → 第3章完成首次兑现`

新书只采用这个节奏关系，事件、人物、能力和奖励全部重做。

每个关键倒推锚点可引用1—2个 `benchmark_lesson_ids`。

## 10. 小高潮填充

两个大高潮之间用：

`小目标 → 阻碍 → 主角行动 → 小兑现 → 新问题`

持续接力。

小高潮功能可以是第一次公开验证、获得资格、击败同层竞争者、小型资源争夺、关系变化、揭开更大线索或解决下一地图门槛。

## 11. 前100章故事脊柱

最终输出 `story_spine_1_100`，每个节点至少包含：

`chapter_window / stage_objective / main_obstacle / supporting_character_functions / payoff / emotion_goal / hook_function / strategic_target_progress / climax_link / benchmark_lesson_ids / state_change`。

必须能看出为什么这一段存在、它在为哪个高潮服务、解决后推出什么、主角发生了什么不可逆变化。

## 12. 100章以后

当前素材不足时，只保留3—6个 `future_climax_seeds`：阶段名、潜在目标核、世界层级变化、主要势力变化、主角状态变化。

不要提前伪造详细章纲。等素材库、世界和人物积累足够，再展开百万字级5—6个大高潮。

## 13. 完成门

前100章规划 PASS 至少要求：

- 默认2个大高潮；
- 每个高潮都有战略目标物或等价目标核；
- 主角为什么必须要、竞争者为什么也要均明确；
- 多方势力入局有利益原因；
- 高潮结果有兑现、代价、不可逆变化和下一阶段入口；
- 每个高潮有4—8个倒推锚点；
- 前20章至少能映射到市场结构 lesson；
- 小剧情能回到阶段目标或高潮前置条件；
- 第二高潮由第一高潮后果推出；
- 不复制对标书具体事件链。


## 14. 保存契约

需要落盘时，`climax_backplan.json` 顶层至少为：

```json
{
  "schema_version": 1,
  "backplan_id": "BP:...",
  "status": "complete",
  "horizon_chapters": 100,
  "target_major_climax_count": 2,
  "benchmark_lesson_ids": [],
  "faction_pool": [],
  "strategic_targets": [],
  "major_climaxes": [],
  "story_spine_1_100": [],
  "future_climax_seeds": []
}
```

### faction_pool

每个势力至少保存：

`faction_id / name / role / controlled_assets_or_permissions / core_interest / available_leverage / stage_entry`

### major_climaxes

默认完整模式要求2个高潮；每个高潮：

- 引用一个真实存在的 `strategic_target_id`；
- 完整模式至少有2个有利益动机的 competing factions；
- 有 `previous_climax_dependency`，第一个写 `ROOT`，第二个必须说明由第一高潮什么后果推出；
- 内嵌4—8个 `backward_beats`；
- benchmark lesson 引用只能来自顶层 `benchmark_lesson_ids`。

### story_spine_1_100

至少6个阶段节点，每个节点必须指向某个 `climax_link`，说明该段究竟在为哪个大高潮服务。

校验：

```powershell
python -X utf8 scripts/validate_v12_artifacts.py climax climax_backplan.json
```
