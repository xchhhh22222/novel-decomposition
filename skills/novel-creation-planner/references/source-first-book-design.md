# 素材先行的开书组装 V1.1

用于从共享素材库主动提出新书方向。V1.1 不直接“搜一堆素材然后拼”，而是先建立素材槽位并按 Wave 1→4 调度。来源书不必整包继承，但每个被选中的组件都必须保留来源与兼容前提。

## 输入分别取证

1. 带日期的新书榜样本：只对实际读过的章节判断开篇和节奏。
2. `DNA素材/02_金手指`：读取输入、处理、输出、限制与首次验证。
3. `DNA素材/03_世界观`：读取世界规则、`factions` 势力、资源控制、威胁、地图和信息结构。
4. `DNA素材/04_修炼体系`：优先读取 schema_version 2 的 `cultivation_systems / system_relations / techniques / artifacts / resource_assets`。
5. `DNA素材/05_人物功能与标签` 及人物个体卡。
6. `DNA素材/08_篇章结构`、高潮脉络与章节情绪。

## 调度前置

先读取 `material-dispatch.md`。至少建立：world_premise、primary_system、golden_finger、first_major_climax 四个骨架槽位；其它槽位按任务需要开启。

第一次检索只为每槽保留少量候选，不追求“库里有什么全看一遍”。

## 组装流程

第一步：每个候选组件保留来源 `book_id / record_id / chapters_covered / qa_status`。

第二步：按功能选材，而不是按整书照搬。例如：A 取资源稀缺逻辑，B 取武道 system，C 取精神 system，D 取成长型 artifact，E 取势力冲突母型。

第三步：建立新书兼容层。选择两套以上 system 时，必须重做 entry_condition、energy_or_power_source、realm、shared/competing resources、can_dual_cultivate、conversion_rule、power mapping、technique/artifact compatibility，以及社会制度与 factions 利益。

第四步：原创重设。来源组件只提供结构启发，不直接复制专名、人物、独特表达和连续事件链。

第五步：结果明确标成【新书候选】，不能写回来源 `per_book`。

## 三案要求

A/B/C 至少在主要 system 组合、多体系关系、核心资源入口、势力冲突、金手指作用层、第一高潮目标、主要人物关系发动机中的两项以上实质不同。

每案至少包含一句话卖点；世界前提与核心势力；1～N 套体系及关系；境界验证；核心功法/法宝/资源；金手指；第一、第二高潮；来源组件与原创重设；三个主要兼容或相似性风险。

## 禁止

- 把跨书拼装结果称为来源事实；
- 只改名字，不改能量、资源、限制、验证和剧情接口；
- 为了炫设定无意义堆很多体系；
- 用来源书未出现的内容反向补全其拆书记录；
- 把 candidate cluster 当成已审核正式事实。
