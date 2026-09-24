# 素材调度协议 V1.1

本文件定义 `novel-creation-planner` 如何从共享素材库中“调度”素材，而不是只做关键词搜索。

核心目标：

```text
创作需求
→ 拆成素材槽位
→ 为每个槽位选择正确模块/组件
→ 小批量召回
→ 下钻来源
→ 兼容性检查
→ 跨书组合
→ 新书候选
```

## 1. 调度与检索的区别

“检索”只回答：库里有哪些记录和关键词相近。

“调度”必须进一步回答：

- 当前创作阶段真正缺什么；
- 该缺口属于哪个模块、哪个组件层；
- 应先看 cluster/正式卡，还是直接看 per_book；
- 一次取几条候选；
- 哪些组件必须先保持同源理解；
- 哪些组件适合跨书重组；
- 何时应该停止继续搜索；
- 何时应输出 GAP 而不是硬凑。

V1.1 禁止“把整个素材库都读一遍再想故事”。

## 2. 素材槽位

根据用户任务，只建立必要槽位，不要求每次全部填满。

### A. 故事骨架槽位

- `reader_promise`：读者承诺与核心情绪；
- `golden_finger`：金手指运行机制；
- `world_premise`：世界核心前提与持续问题；
- `primary_system`：主修炼体系；
- `secondary_system`：可选副体系；
- `resource_loop`：核心资源来源—争夺—消耗—回流；
- `first_major_climax`：第一大高潮的蓄压—触发—兑现；
- `longline_engine`：60章以后仍能持续的主线发动机。

### B. 世界冲突槽位

- `faction_ecology`：核心势力与利益关系；
- `institution_pressure`：制度/资格/权限如何制造限制；
- `threat_generator`：持续威胁从哪里来；
- `map_expansion`：新地图如何改变资源、制度和风险；
- `information_control`：秘密、解释权与信息差。

### C. 成长组件槽位

- `realm_structure`：境界与突破验证；
- `technique`：功法/武技；
- `artifact`：法宝/装备；
- `growth_resource`：丹药、晶核、材料、积分等；
- `system_relation`：多体系兼修、互斥、互补、转化或克制。

### D. 人物与剧情槽位

- `relationship_engine`：人物关系持续制造选择的机制；
- `heroine`：女主个体目标、资源和主动行动；
- `antagonist`：长线反派目标、筹码和压力升级；
- `plotline`：持续主/支线；
- `plot_mechanism`：可重复剧情机制；
- `opening`：前三章承诺、首次验证与4—10章循环；
- `emotion_payoff`：情绪蓄压、兑现与余震。

## 3. 槽位 → 素材源路由

| 槽位 | 首选素材源 | 下钻源 |
|---|---|---|
| reader_promise / emotion_payoff | 正式套路卡、章节情绪、opening | 对应 per_book |
| golden_finger | 02_金手指 cluster / per_book | 金手指原记录 |
| world_premise | 03_世界观 rule_chain | per_book |
| faction_ecology | 03_世界观 `factions` | 所属 per_book |
| primary/secondary_system | 04_修炼体系 `cultivation_system` | 所属 per_book |
| realm_structure | 04_修炼体系 `realm` | 所属 system |
| technique | 04_修炼体系 `technique` | 所属 system / per_book |
| artifact | 04_修炼体系 `artifact` | 所属 system / per_book |
| growth_resource | 04_修炼体系 `resource_asset` + 03_世界观资源循环 | 两边原记录 |
| system_relation | 04_修炼体系 `system_relation` | 同书相关 systems |
| relationship_engine | 05_人物功能与标签 | per_book / derived |
| heroine / antagonist | 05_人物派生卡 | 原人物记录 |
| plotline | 06_主线与支线 | per_book |
| opening | 07_开篇 + 市场样本 | per_book / opening cards |
| first_major_climax | 08_篇章结构 | arc / major storyline |
| plot_mechanism | 09_剧情机制 + 正式套路卡 | per_book |

正式套路卡代表经过审核的“原子机制”；DNA candidate/per_book 代表来源书中的结构与证据。两者不能混成同一种可信度。

## 4. 四波调度

### Wave 1：骨架召回

先填：

`reader_promise → world_premise → primary_system → golden_finger → first_major_climax`

每槽默认只保留 3—5 个候选。目标是确定故事骨架，不是填满设定百科。

如果这一步都无法闭环，禁止提前大量搜索功法、法宝和配角。

### Wave 2：冲突与供给

骨架成立后再填：

`faction_ecology → resource_loop → antagonist → relationship_engine → plotline`

检查“谁控制资源、谁阻碍主角、为什么必须行动”。

### Wave 3：表现层

再根据已经选定的骨架有条件地检索：

`realm_structure → technique → artifact → growth_resource → opening → plot_mechanism`

功法和法宝必须服务已选体系、资源与剧情，不因为素材库里“看起来酷”就强塞。

### Wave 4：验证与补洞

最后才：

- 回查选中组件所属 per_book；
- 检查证据与 QA；
- 检查同源依赖；
- 检查跨书兼容；
- 检查来源集中度；
- 输出 GAP 与缺口订单。

## 5. Cluster → Per-book → Component 三段检索

### 5.1 先宽后窄

需要“找方向”时：

1. 先检索正式套路卡或 cluster，找到运行母型；
2. 再检索对应 per_book；
3. 对 V1.4 世界观/修炼体系再下钻到具体 component。

需要“找具体部件”时可以直接 component search，但仍必须保留来源记录。

### 5.2 组件级命令

V1.1 的 `search_dna_candidates.py` 支持 `--components`：

```powershell
python scripts/search_dna_candidates.py ^
  --library "<共享素材库>" ^
  --query "成长型 武器 消耗" ^
  --modules "修炼体系" ^
  --components "artifact" ^
  --include-per-book ^
  --max-per-book 2 ^
  --limit 8 ^
  --format json
```

常用 component：

`faction / rule_chain / cultivation_system / realm / system_relation / technique / artifact / resource_asset`

没有 `--components` 时保持旧版“记录级检索”兼容。

## 6. 同源理解与跨书组合

### 必须优先同源理解

以下组件耦合较强，第一次检索到时先看它们在原书如何闭环：

- cultivation_system ↔ realm；
- cultivation_system ↔ technique；
- cultivation_system ↔ resource_asset；
- artifact ↔ energy/resource cost；
- faction ↔ controlled_resources / permissions；
- world rule ↔ institution / resource circuit；
- golden_finger ↔ resource input / validation。

“同源理解”不等于“新书必须同源采用”。

### 允许跨书重组

理解原结构后，创造层可以：

```text
A书 world rule
+ B书 primary system
+ C书 secondary system
+ D书 artifact mechanism
+ E书 faction pressure
```

但必须重新设计接口，并把结果标记为【新书候选】。

## 7. 来源集中度

V1.1 不要求“一组件一本书”，也不机械追求来源越分散越好。

但对 greenfield 新书，以下五类核心组件：

`world_premise / golden_finger / primary_system / faction_ecology / first_major_climax`

如果 3 项以上直接来自同一本来源书，必须触发 `SOURCE_CONCENTRATION_RISK`，执行额外原创重设审核。

同书的 system + realm + technique 作为“同一个成长组件包”理解时，不按三次独立借鉴计算；但若连世界、金手指、高潮也沿用同源，则属于高相似风险。

## 8. 候选预算

默认检索预算：

- 每个槽位初筛 3—5 条；
- 不确定槽位最多扩大到 8 条；
- 每个槽位最多精读 2—4 条原记录；
- 同一 book 默认最多保留 2 条结果，除非正在做同源兼容回查；
- 同一问题连续两轮检索没有新增“运行机制差异”，停止继续搜。

禁止为了“有更多素材”无限扩召回数量。

## 9. 选择标准

素材不是按搜索分最高直接采用。最终选择至少检查：

1. **功能匹配**：它是否解决当前槽位问题；
2. **前提匹配**：新书是否具备它需要的世界/人物/资源前提；
3. **接口匹配**：能否接入已选世界、体系、金手指；
4. **证据质量**：QA、unknowns、章节覆盖；
5. **来源集中度**：是否过度依赖单本书；
6. **原创距离**：重设后是否仍像来源书；
7. **剧情产能**：能否持续制造选择、冲突、兑现和后果。

## 10. 停止条件

满足以下条件即可停止继续搜：

- 所有 required 槽位已有至少1个可用候选或明确 GAP；
- 核心闭环成立：世界问题 → 势力/资源 → 修炼门槛 → 金手指 → 人物选择 → 高潮；
- 关键组件兼容性无 FAIL；
- 没有未处理的高来源集中风险；
- 新一轮检索只增加同义项，没有产生新的运行机制。

素材库没有合适内容时输出 GAP，比拿低适配素材硬拼更好。

## 11. 调度记录

保存机器计划时，V1.1 使用 `material_dispatch`：

```json
{
  "status": "complete|partial|hold",
  "slots": [
    {
      "slot_id": "SLOT:PRIMARY_SYSTEM",
      "role": "primary_system",
      "required": true,
      "wave": 1,
      "modules": ["cultivation_system"],
      "component_types": ["cultivation_system"],
      "query_groups": ["低门槛成长 实战验证"],
      "target_candidates": 5,
      "source_strategy": "cross_book|same_source_bundle|either",
      "selected_refs": [
        {
          "material_id": "CS:SYSTEM:001",
          "material_kind": "dna_component",
          "module": "cultivation_system",
          "component_type": "cultivation_system",
          "record_id": "CS:BOOK:BOOK_01",
          "book_id": "BOOK_01",
          "qa_status": "PASS"
        }
      ],
      "rejected_refs": [],
      "gap_reason": ""
    }
  ],
  "source_concentration_risks": [],
  "compatibility_checks": [],
  "stop_reason": "核心槽位已覆盖且继续检索无新增机制"
}
```

调度记录不是来源事实，也不修改素材库。


## 12. V1.2 新增槽位：战略目标物

V1.2 在创造层新增 `strategic_target` 槽位，它不等同于 `resource_asset`。

- `resource_asset`：晶核、丹药、积分、材料等日常成长输入；
- `strategic_target`：能撑起阶段高潮、引发多人/多势力争夺的目标核。

战略目标物没有单一对应的拆书模块，应组合检索：

1. `artifact / technique / resource_asset`：目标本体能做什么；
2. `faction / world_resource_circuit`：谁控制、为什么稀缺；
3. `arc_structure`：争夺如何升级成高潮；
4. `plot_mechanism`：资格、线索、秘境、拍卖、护送、竞争等如何组织。

调度时先定功能，再由创造层重新命名与重设世界来源。不能因为来源书里某个物品很酷，就直接复制专名和完整设定。

默认每个前100章大高潮至少对应一个 `strategic_target` 或功能等价的战略目标（资格、秘密、身份、入口也可以）。
