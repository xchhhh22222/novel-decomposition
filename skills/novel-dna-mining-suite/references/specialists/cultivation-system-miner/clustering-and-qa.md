# 修炼成长系统 V1.4 聚类与 QA 规则

本文件只规定 `novel-cultivation-system-miner` 的来源忠实、组件边界、跨书比较和质量审核。正式字段以同目录 `schema.md` 为准。

## 一、最高优先级：来源忠实

审核第一问不是“拆得够不够多”，而是“有没有多拆”。

- 一本书只出现一套体系，拆一套就是正确结果；
- 只出现两套体系，拆两套就是正确结果；
- 不得为了素材库丰富度、未来创作方便或 schema 完整性补造额外体系；
- 不得拿 BOOK_A 的组件补 BOOK_B；
- 创作层重新组合出的内容不得写回来源 `per_book`。

出现跨书污染、题材常识补全、虚构体系或把创作候选倒灌成来源事实时，直接 HOLD/FAIL。

## 二、单书组件 QA

### 2.1 cultivation_systems 数量

体系数量只由证据决定。名称不同但实际共享同一入门、能量、成长、境界和验证路径时，不机械拆成多个 system；存在独立入门、力量来源、成长路径、境界或验证方式时，才考虑独立体系。

### 2.2 realm 归属

每个境界只能存在于所属 `system_id` 的 `realm_system` 中。正式突破必须满足：

`before → trigger_or_condition → after → direct_evidence_refs`

击杀、越级、称号、装备、资源到账、权限提升和短时 buff 都不能替代正式境界证据。

### 2.3 system_relations

只有两套以上 system 才允许正常 relation。

- `system_a/system_b` 必须引用本书已有 system，且不能相同；
- 兼修、互斥、互补、转化、克制、依赖和融合必须有证据；
- `can_dual_cultivate`、`conversion_rule` 与跨体系战力对位不得靠常识推断；
- 单体系作品必须保持空关系数组。

### 2.4 techniques

- 功法/武技本体与人物熟练度分开；
- `compatible_system_ids` 必须引用本书已有 system；
- 获得不等于掌握，掌握不等于精通；
- 一次成功施展不能补全完整功法阶段；
- 只确认“存在某功法”时允许部分字段 UNKNOWN。

### 2.5 artifacts

- 外部装备效果与人物自身境界分离；
- 装备品质/法宝等级不等于修炼境界；
- 装备成长不自动等于人物成长；
- 只有普通武器存在而无特殊机制时，不补造法宝运行规则。

### 2.6 resource_assets

- 到账、持有、消耗、转化、永久自身变化分开；
- `permanent_self_change_proven=true` 必须有直接证据；
- 世界层的生产、定价、垄断和社会分配归 worldbuilding，本专项只记录资源如何进入成长。

### 2.7 protagonist_build / proficiency / combat power

- 主角构筑只能引用本书已有 system/technique/artifact；
- skill_proficiency 只追踪已定义 technique 的人物掌握状态；
- actual_combat_power 不得反推正式 realm；
- identity_permissions 不能冒充修炼等级；
- golden_finger_interfaces 只描述接口，不重拆金手指。

## 三、证据与覆盖

- 每个 `per_book` 必须能沿 `evidence_refs` 回到章节、阶段或已通过 QA 的 overlay；
- 书名、简介、题材标签、宣传语和模型常识不能支撑体系、境界、功法、法宝或兼修关系；
- 缺口使用 `UNKNOWN / partial / gap / HOLD`，不能用相邻组件补齐；
- `HIGH` 不能包含关键 unknowns；
- 同一本书不能同时有正常 `per_book` 与 `gap`。

## 四、跨书 nearest-neighbor 与 clustering

只有全部目标书完成单书抽取和 QA 后才能比较。

优先比较：

1. system 的入门—训练—突破—验证—限制；
2. realm 的阶段差异和突破逻辑；
3. technique 的前置—训练—效果—风险；
4. artifact 的激活—消耗—效果—成长；
5. resource 的获得—转化—消耗；
6. 多体系的兼修、互斥、转化、克制与融合；
7. 主角构筑和实际战力修正。

“都有武道”“都有精神力”“都有剑法”“都有灵器”不能单独支撑聚类。聚类的是运行结构，不是表面名词。

## 五、创作层兼容提醒

拆书聚类只向创造层提供来源组件和结构相似性，不负责生成新世界。

创造层若组合 `BOOK_A.system + BOOK_B.technique + BOOK_C.artifact`，必须重新设计：

- 名称和世界来源；
- 能量与资源接口；
- 兼修/冲突关系；
- 境界验证；
- 功法与法宝适配；
- 限制、代价和剧情后果；
- 原创性边界。

组合结果只能标记为【新书候选】，不能写回来源书。

## 六、QA 结果

- **PASS**：来源忠实，组件引用完整，层级与证据清楚；
- **HOLD**：体系归属、兼修关系、境界或组件证据不足；
- **FAIL**：补造来源事实、跨书污染、关系引用不存在 system、正式突破无直接证据等硬错误。

所有结果保持 `candidate`，不得自动变成 `active` 或正式素材卡。