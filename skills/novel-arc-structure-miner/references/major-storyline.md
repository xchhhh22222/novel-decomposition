# 大故事线候选库

## 对象与范围

一本书由若干先后相接或交错的大故事线构成。本视图先拆已核验范围内**一条最重要、尽可能有完整收束**的线，以后可按同一格式逐条补齐。大故事线是跨多个节点持续运转的一组目标与对抗，不是单场大事件、全书主线、卷名或机械的前50章区间。前50章可作为首轮寻找故事线的起点；真实起止由触发、目标建立、持续推进、高潮、结算或转向的证据决定。只覆盖部分过程时标 `partial`，不得把未发生的结局写成已兑现。**切分门槛**：若拟定终点之后主角仍追逐同一关键目标、同一资源或同一敌对计划尚未结算，且下一阶段由本阶段直接推进，则当前只是大故事线的子阶段，应向后追到目标真正兑现、失败或明确转向。不能因换地图、敌人接棒或一次副本脱险就提前截线。

## 必答问题

1. **为什么启动**：主角与对手各自要什么；什么利益、资源、身份、规则或承诺使双方无法回避；谁先采取了改变局势的行动。
2. **如何推进**：主角的阶段选择及代价、对手的计划步骤及依赖、双方如何因上一轮结果调整下一步；记录真正改变条件的节点和因果边，删去只在时间上相邻的事件。
3. **如何结算**：主角最终获得或失去什么（能力、资源、身份、关系、信息、权限、目标），哪些收益已被公开验证或实际使用；反派哪项具体计划被破坏、损失了什么、是否还有后手。成功、失败、妥协与未决都允许。
4. **如何衔接下一条线**：结算后的新收益、新敌意、暴露风险、未还代价或新权限，怎样迫使下一条故事线开始；不能仅写“换地图/来更强敌人”。

高潮事件只是故事线的一个节点。筛“最大/最重要”时看它对主角状态、对手计划和后续线路的改变，不看场面大小。若敌人是可替换的组织接棒链，逐个区分具体计划，不虚构一个长期反派个人。

## 证据与结构

优先使用 QA 通过的逐章事实、剧情线、阶段结构、人物选择与情绪记录；关键因果不清时回查原文。先列起止与结算状态，再逆推必要条件，最后顺推各节点。每个节点写 `chapter_range`、`actor`、`goal`、`choice_or_plan_step`、`cost`、`visible_result`、`state_change`、`evidence_refs`；每条边写“上一节点哪项后果让下一节点可能、必要或更困难”。纯时间相邻标 `sequence_only` 并列缺口。

主角收获单列 `protagonist_gains`，按硬收益与软收益记录准确发生章节、直接来源、兑现证据和代价；位阶、新能力、进度数值与关键物品必须回到对应章节逐项核验，不能从阶段摘要合并推算；反派计划单列 `antagonist_plan` 与 `plan_disruptions`，逐项写原计划、主角干预、损失、调整或后手。没有反派个人时可记对手组织/制度，但不生成虚假个人卡。结尾必须有 `next_storyline_entry`，说明实际已发生或在证据范围内明确形成的下一压力；未知则写 `UNKNOWN`。

## 保存与检索

用户授权保存候选后，每本书存 `DNA素材/08_篇章结构/derived/major_storyline/BOOK_XX.jsonl`，每条故事线一条记录，可多条。顶层至少包含 `record_type: major_storyline`、`schema_version: 1`、`status: candidate`、`record_id`、`book_id`、`title`、`chapters_covered`、`storyline_range`、`qa_status`、`confidence`、`unknowns`、`protagonist_goal`、`opponent_goal`、`unavoidable_conflict`、`start_trigger`、`causal_nodes`、`causal_edges`、`climax_or_turn`、`resolution_state`、`protagonist_gains`、`antagonist_plan`、`plan_disruptions`、`next_storyline_entry`、`evidence_refs`。书内多条线使用稳定的 `record_id` 与序号；未拆的线标缺口，不把首条写成全书唯一故事线。

若已核验范围无可判定的大故事线，写 `record_type: derived_gap`、`view_type: major_storyline`、`coverage_status: checked_no_qualifying` 或 `insufficient_evidence`，附章节范围与原因。候选不自动变成正式 active 素材卡。跨书只比较目标冲突、计划被破坏、主角收益与下一线入口的功能结构；新书借鉴必须重设至少三个关键维度，不能复制原作连续事件链。
