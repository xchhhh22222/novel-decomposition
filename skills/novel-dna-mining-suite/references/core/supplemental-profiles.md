# Supplemental Material Profiles V1.6

Profiles 只帮助中控选择已有 specialist 和 derived views，不替代 specialist 内部契约。

## PROFILE_ABILITY_GOLDEN_FINGER

适用：每日新能力、复制、随机、抽奖、规则能力、能力组合、废能力开发。

默认 target_specialties：
- golden_finger
- cultivation_system
- plot_mechanism

默认 derived_views：
- ability_assets
- combat_expression_assets

推荐字段：
- ability_core
- trigger
- input
- operation
- output
- limit
- cost
- growth
- first_showcase
- appeal_hook
- immediate_fantasy
- combat_value
- social_value
- plot_generation
- combination_interfaces
- counterplay
- fatigue_risk
- evidence_refs

核心问题：
- 为什么这个能力第一眼有吸引力？
- 第一次展示如何兑现？
- 它能持续制造什么剧情？
- 它和其它能力如何组合？
- 长期使用会不会疲劳？

## PROFILE_DUNGEON_RULE

适用：副本、秘境、规则怪谈、试炼、无限流、封闭博弈。

默认 target_specialties：
- worldbuilding
- plotline
- arc_structure
- plot_mechanism

可选：
- character_function

默认 derived_views：
- dungeon_rule_assets

推荐字段：
- entry_condition
- surface_rules
- hidden_rules
- rule_reliability
- victory_condition
- failure_condition
- death_or_penalty
- resource_pressure
- information_asymmetry
- roles
- team_structure
- conflict_structure
- loophole
- discovery_process
- escalation
- turning_point
- exit_condition
- reward
- mainline_connection
- reuse_pattern
- fatigue_risk
- evidence_refs

## PROFILE_HEROINE_RELATIONSHIP

适用：多女主、关系发动机强、女性角色具备独立线。

默认 target_specialties：
- character_function
- plotline
- arc_structure

默认 derived_views：
- heroine_character
- relationship_engine

推荐字段：
- independent_goal
- resource_domain
- faction
- binding_reason
- first_exchange
- shared_interest
- conflicting_interest
- information_boundary
- active_choices
- progression_states
- break_condition
- reconciliation_condition
- replaceability
- protagonist_interface
- evidence_refs

核心问题：
- 她离开主角后能否自己推动剧情？
- 为什么不能被另一个女主替代？
- 主角与她之间有什么可重复运行的关系发动机？

## PROFILE_CHARISMATIC_ANTAGONIST

适用：魅力反派、亦敌亦友、长期竞争者、灰色阵营人物。

默认 target_specialties：
- character_function
- plotline
- arc_structure

可选：
- plot_mechanism

默认 derived_views：
- long_arc_villain
- charismatic_antagonist_assets

推荐字段：
- goal
- values
- resource_domain
- faction
- competence
- threat_source
- charisma_source
- reader_respect_source
- mirror_to_protagonist
- cooperation_possibility
- hostility_reason
- boundary
- scene_stealing_pattern
- escalation_path
- defeat_or_exit_condition
- evidence_refs

## PROFILE_COMBAT_EXPRESSION

适用：战斗丰富、武技表现强、装备构筑丰富、能力组合多。

默认 target_specialties：
- cultivation_system

默认 derived_views：
- combat_asset_inventory
- combat_expression_assets
- non_protagonist_combat_coverage

必须扫描：
- 主角
- 女主
- 反派
- 重要配角

可迁移资产：
- 功法
- 身法
- 爆发
- 防御
- 控制
- 远程
- 破防
- 反制
- 召唤
- 领域
- 形态变化
- 团队协同
- 越阶方式
- 装备效果
- 设施
- 战术组合

推荐字段：
- function_slot
- trigger
- input
- operation
- range
- action_pattern
- output
- cost
- limit
- counterplay
- visual_expression
- combat_role
- combination_interface
- compatible_system
- user_archetype
- evidence_refs

## PROFILE_CUSTOM

只有前述 profile 无法表达用户目标时使用。

要求：
- purpose 必须明确；
- target_specialties 必须显式；
- derived_views 必须显式；
- excluded_specialties 必须显式；
- 不允许以 CUSTOM 为理由越过 specialist schema/QA；
- 不允许扩大章节范围或书单。
