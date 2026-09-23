# 女主人物卡候选库

## 用途与路径

从已拆章节中提取可供开书时比较的女主个体，不以“美貌、身份、强战力、喜欢主角”代替人物。用户授权保存候选后，每本书写 `DNA素材/05_人物功能与标签/derived/heroine/BOOK_XX.jsonl`，每位人物一条；未授权只在对话展示。旧的 `derived/BOOK_XX_characters.jsonl` 可读，不自动迁移或覆盖。

## 入选与证据

先明确“原作文本把她写成什么角色”与“研究者认为可借鉴什么”，二者分开。只有已核验章节中出现自主目标、至少两次有后果的主动选择，并与主线或主角形成持续作用，才做完整卡。覆盖不足时输出 `partial/UNKNOWN`，不凭最终配对、简介或人物标签补造。完成核查但没有合格对象时，在同目录记录该书 `record_type: derived_gap`、`view_type: heroine_character`、`coverage_status: checked_no_qualifying` 的 gap；证据不足用 `coverage_status: insufficient_evidence`，不要用空库表示已检查。多位女性可以分别建卡，不能预设谁是唯一女主。

记录：来源书与人物 ID、核验章节范围、出场阶段、公开处境与信息边界；独立目标和不可退让点；能力、资源、限制与代价；两次以上“局面→可选行动→本人选择→直接后果→后续变化”的证据链；没有主角时仍会推进的事；与主角的合作/竞争/冲突如何双向改变；关系阶段的可见行动，而非好感数值；在所拆大故事线及后续阶段中的主动作用；个人弧线、读者期待、已兑现与未兑现承诺、可能的扁平化风险。

## 性格与不得不接近的关系理由

性格必须写成可观察的决策规律：她在资源不足、秘密暴露、利益冲突或他人受损时如何权衡，哪些行为反复出现，何时出现反例或变化。每项核心性格判断给出至少两处不同情境的行动/对白/代价证据；证据不足就写 `UNKNOWN`，不以“高冷、傲娇、善良、疯批”代替分析。

拆清她与主角为何必须接近、合作或暂时敌对：双方各自想得到什么，对方控制着什么不可替代的资源、信息、权限或承诺；直接离开、换人、一次性交易为何不能解决；什么条件会解除绑定或使关系转向。不能仅写“命运相遇”“主角救了她”或“互有好感”。无法证明不得不接近时，如实写为偶然同行或弱绑定，并标记适配风险。

## 记录格式与验收

每条 JSONL 顶层至少有 `record_type: heroine_character`、`schema_version: 1`、`status: candidate`、`record_id`、`book_id`、`character_id`、`title`、`chapters_covered`、`qa_status`、`confidence`、`unknowns`、`independent_goal`、`personality_evidence`、`boundaries`、`resources_and_limits`、`key_choices`、`forced_proximity_reason`、`alternative_paths_and_why_blocked`、`binding_break_condition`、`relationship_changes`、`storyline_roles`、`evidence_refs`。关键选择和关系变化应有章节证据；缺证据填 `UNKNOWN`，不能空想补齐。`qa_status: PASS` 仅表示候选卡可用，不是正式素材卡或新书人物。

跨书比较只抽象“独立目标、边界、行动与关系发动机”，不按校花、冷艳、女帝等外观身份标签归类。新书使用时至少重设背景、目标、资源、关系、关键选择、结果中的三项，并核对本书单女主等既有硬约束。
