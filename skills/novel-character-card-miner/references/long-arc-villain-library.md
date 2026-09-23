# 长线反派人物卡候选库

## 用途与路径

收录在已拆范围内跨多个剧情节点持续推动冲突、策略会随胜负变化的反派。用户授权保存候选后，每本书写 `DNA素材/05_人物功能与标签/derived/long_arc_villain/BOOK_XX.jsonl`；每名反派一条。一次性恶人、只靠职位压人或出场很久却没有主动策略的人，不因篇幅自动入选。

## 入选判定

需要有可核验的个人目标、可调动的资源或制度杠杆，且个人计划跨越多个剧情阶段持续发生作用；至少一次局部胜负后的损失、学习、升级或策略调整真实改变后续行动。一个长期布局可以包含多步和后手，不必硬拆成两个独立计划；但连续数章的同一场追杀、收网或最终决战不能拆成多轮来凑长线，出场时间长而计划不推进也不合格。若只拆到首次交锋，记作 `partial` 或短线对手，不能宣称“长线反派”。反派不必始终比主角强，也不必最终死亡；不要把动机简化为嫉妒主角。完成核查但无合格长线反派时，在同目录记录该书 `record_type: derived_gap`、`view_type: long_arc_villain`、`coverage_status: checked_no_qualifying` 的 gap；证据不足用 `insufficient_evidence`。

记录“目标与正当性来源→与主角利益为何不可兼得→首次施压与试探→双方选择和损失→反派如何调整手段→局部胜负怎样改变下一次交锋条件→高潮中的决定性行动→终局或未决状态”。还要记录其组织/关系网络、行动成本、信息边界、真实能力、阶段性的得失、主角因他而改变的目标或方法，以及读者为何期待其失败、转向或付代价。每个箭头都写章节或阶段证据；先后发生不等于因果。

## 性格、计划与不得不敌对的理由

一张卡必须对应可辨认的个人，不能把“所长→司长→市级势力”的接棒链合并成一个人物。反派性格写成压力下的选择规律，至少用两处不同场景的行动、对白或付出代价的决定验证；只凭恶行或阵营不能推断“残忍、狡诈、傲慢”。

列出反派自己的阶段计划：目标、步骤、依赖资源/人、预期收益、隐蔽条件与失败代价。说明主角哪项行动具体破坏了哪一步，反派损失什么，为什么双方不能简单绕开、和解或换对象；若敌对只是偶然撞上，照实标注，不能写成命定宿敌。每次失败后记录反派如何调整计划；同一计划没有变化的重复追杀不算长线升级。

## 记录格式与验收

每条 JSONL 顶层至少有 `record_type: long_arc_villain`、`schema_version: 1`、`status: candidate`、`record_id`、`book_id`、`character_id`、`title`、`chapters_covered`、`qa_status`、`confidence`、`unknowns`、`villain_goal`、`personality_evidence`、`plan_steps`、`levers_and_limits`、`necessary_opposition_reason`、`alternative_paths_and_why_blocked`、`confrontations`、`plan_disruptions`、`strategy_updates`、`storyline_role`、`outcome_or_open_state`、`evidence_refs`。`confrontations` 必须覆盖跨阶段的计划推进、至少一次有后果的交锋与其后的计划调整；不足时保留缺口或短线对手备注，不造长线记录。原作证据与新书改造建议分开，新书不可复用反派姓名、专名、标志性台词或完整交锋链。
