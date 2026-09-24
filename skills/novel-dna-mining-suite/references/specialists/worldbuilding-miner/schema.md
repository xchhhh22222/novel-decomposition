# 世界观横向拆解专项输出契约 V1.4

## 1. 权威关系与统一 envelope

本文件是 `novel-worldbuilding-miner` 的专项记录契约，不覆盖总控契约，也不修改 `chapter-emotion-schema.md`。世界观记录必须同时满足：

- `skills/novel-dna-orchestrator/references/horizontal-specialist-contract.md` 的派生记录要求；
- `skills/novel-dna-orchestrator/references/integration-and-qa.md` 的阶段门、证据和状态要求；
- 本文件规定的世界观因果链与边界。

除上位契约明确规定的 canonical 权威记录外，所有本专项机器可读记录都使用统一 envelope：

```json
{
  "record_type": "per_book|nearest_neighbor|cluster|qa|handoff|gap",
  "schema_version": 2,
  "record_id": "WB:<TYPE>:<STABLE_ID>",
  "status": "candidate",
  "book_id": "BOOK_01",
  "book_ids": ["BOOK_01", "BOOK_02"],
  "evidence_refs": ["BOOK_01:CHAPTER:0001", "BOOK_01:STAGE:01"],
  "unknowns": [],
  "confidence": "HIGH|MEDIUM|LOW",
  "qa_status": "PASS|HOLD|FAIL"
}
```

实际记录按作用只使用 `book_id` 或 `book_ids` 其中之一，不要求同时出现：

- `per_book`、`qa`、`handoff` 和 `gap` 通常使用 `book_id`；
- `nearest_neighbor` 和 `cluster` 通常使用 `book_ids`。

`evidence_refs` 必须能回到章节或阶段；`unknowns` 只能记录真实缺口，不能把推测填进去。所有记录的 `status` 固定为 `candidate`，不定义 `active`、`deprecated` 或正式素材库写入字段。关键未知存在时不得使用 `HIGH`。

## 2. 世界观因果链

世界观专项的最小分析单位不是“一个设定名词”，而是一条可追溯的运行链：

`规则 → 稀缺 → 利益/制度 → 冲突 → 剧情入口 → 读者情绪`

每条 `rule_chain` 记录建议使用以下字段：

```json
{
  "chain_id": "WB:RULE:001",
  "completeness": "complete|partial|UNKNOWN",
  "rule_statement": "可被章节事实支持的规则描述",
  "scope": "适用的人群、区域、机构或阶段",
  "scarcity": "规则制造或放大的稀缺对象",
  "resource_flow": "资源如何产生、分配、获得、消耗或回流",
  "interests_and_institutions": "受益者、受损者、组织和制度安排",
  "constraints": "对普通人、组织或主角的限制与代价",
  "conflict_engine": "规则、稀缺和利益关系如何持续制造冲突",
  "plot_entry": "该规则如何进入具体剧情并改变行动选择",
  "information_ownership": "谁知道、谁不知道、谁控制解释权",
  "map_or_region_effect": "区域、权限或地图开放如何改变规则运行",
  "recurring_threat": "世界规则如何持续产生威胁或压力",
  "emotion_overlay_links": [
    {"emotion_record_id": "BOOK_01:EMOTION:0001", "function": "规则首次验证的读者期待证据"}
  ],
  "evidence_refs": ["BOOK_01:CHAPTER:0001"],
  "unknowns": []
}
```

字段的共同要求：

1. `rule_statement` 必须是可核验的规则或制度事实，不能只是氛围形容；
2. `completeness` 允许 `partial` 或 `UNKNOWN`，链条缺失时不能用推测补齐；
3. `scarcity`、`resource_flow`、`interests_and_institutions`、`conflict_engine`、`plot_entry` 至少要能用证据说明其中已发生的部分；
4. `emotion_overlay_links` 只保存已有情绪记录的引用及其作用，不复制 `main_reader_emotion`、`payoff_level` 或其它章节情绪字段；
5. `evidence_refs` 只引用真实章节、阶段或既有 overlay 记录；
6. 具体专名、人物名和地图名只在证据定位需要时出现，不参与母型命名。

## 2.5 V1.4 势力组件 `factions`

`factions` 用于回答“这个世界有哪些真正能持续行动的势力、各自控制什么、为什么冲突”，不是组织名词表。

```json
{
  "faction_id": "WB:FACTION:001",
  "name_in_book": "原书势力名",
  "faction_type": "official|military|academy|family|corporation|guild|religion|race|underground|regional|other|UNKNOWN",
  "public_role": "公开职能或社会身份",
  "actual_interest": "已被证据支持的核心利益或目标",
  "controlled_resources": [],
  "controlled_territories_or_access": [],
  "controlled_information_or_rules": [],
  "recruitment_or_entry": [],
  "internal_hierarchy": [],
  "relations": [
    {
      "target_faction_id": "WB:FACTION:002",
      "relation_type": "ally|rival|enemy|dependency|trade|oversight|UNKNOWN",
      "observable_basis": "由什么行动、制度、资源或冲突证明",
      "evidence_refs": ["BOOK_01:CHAPTER:0010"]
    }
  ],
  "conflict_sources": [],
  "protagonist_interface": "主角如何进入、受益、受限、合作或被针对",
  "evidence_refs": ["BOOK_01:CHAPTER:0005"],
  "unknowns": []
}
```

硬规则：

1. 至少有资源控制、制度权限、领地/入口、信息控制、招募、持续行动或稳定利益之一的证据；
2. 只有组织名、校名、公司名、家族名或种族名不足以建立高置信 faction；
3. `relations.target_faction_id` 必须引用同一本 `per_book` 已存在 faction；
4. 不按“都市高武”常识自动补官方、学校、军方、世家或财团；
5. 跨书拼装势力结构属于创造层，不得写回来源书。

## 3. `per_book` 单书记录

每本目标书必须有一条 `record_type: per_book`，或在无法核验时有一条 `record_type: gap`；同一目标书不能两者并存。

除统一 envelope 外，`per_book` 使用以下专项字段：

```json
{
  "record_type": "per_book",
  "schema_version": 2,
  "record_id": "WB:BOOK:BOOK_01",
  "status": "candidate",
  "book_id": "BOOK_01",
  "title": "书名",
  "chapters_covered": "1-120",
  "world_core_premise": "世界核心异常或基础前提及其证据",
  "ordinary_life_state": "普通人的日常如何被该前提改变",
  "factions": [],
  "rule_chains": [],
  "institution_and_interest_patterns": [],
  "resource_circuits": [],
  "threat_generators": [],
  "map_expansion_patterns": [],
  "information_control_patterns": [],
  "milestones": {
    "first_world_display": {},
    "first_rule_validation": {},
    "first_scale_upgrade": {}
  },
  "interfaces": {
    "golden_finger": [],
    "cultivation_system": [],
    "other_scoped_interfaces": []
  },
  "emotion_overlay_links": [],
  "revelation_rhythm": [],
  "fatigue_risks": [],
  "source_numbering_notes": [],
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "PASS"
}
```

专项字段含义：

- `factions` 逐个保存有持续行动能力的势力、资源/权限控制与已证实关系；
- `institution_and_interest_patterns` 记录跨势力的制度、阶层和利益模式，不替代具体 faction；
- `resource_circuits` 记录世界资源的产生、分配、获取、消耗和回流，但不输出修炼资源循环母型；
- `threat_generators` 记录规则如何持续生产敌人、风险或压力，而不是罗列敌人名单；
- `map_expansion_patterns` 记录区域、权限和冲突层级如何改变；
- `information_control_patterns` 记录知识分布、隐瞒、解释权和认知反转；
- `milestones` 区分世界首次展示、规则首次验证和世界规模首次升级，不把三者合并；
- `interfaces.golden_finger` 和 `interfaces.cultivation_system` 只记录本世界提供的资源、敌人、制度、权限或验证场接口，并带证据，不替对应专项拆解；
- `revelation_rhythm` 和 `fatigue_risks` 记录世界观揭示的节奏风险，不创造新的章节情绪字段。

若某项只有名词或背景介绍，没有规则后果或证据，应放入 `unknowns`、`source_numbering_notes` 或 QA 缺口，不伪造完整数组内容。

## 4. `gap` 缺口记录

目标书或目标范围缺少足够世界观证据时，必须保留缺口：

```json
{
  "record_type": "gap",
  "schema_version": 2,
  "record_id": "WB:GAP:BOOK_01",
  "status": "candidate",
  "book_id": "BOOK_01",
  "evidence_refs": ["BOOK_01:CHAPTER:0001"],
  "unknowns": ["资源分配规则", "制度如何进入剧情"],
  "confidence": "LOW",
  "qa_status": "HOLD",
  "reason": "可读证据不足以确认世界规则的持续运行链",
  "known_evidence": ["仅确认开篇异常前提"],
  "blocked_outputs": ["高置信 per_book", "跨书近邻", "跨书聚类"]
}
```

`gap` 不是虚构内容的占位符，必须写明缺口位置、已有证据和被阻断的下游判断。

## 5. `nearest_neighbor` 近邻记录

近邻只能在所有目标书完成单书抽取和 QA 后生成。近邻比较的是规则运行方式：

```json
{
  "record_type": "nearest_neighbor",
  "schema_version": 2,
  "record_id": "WB:NEIGHBOR:001",
  "status": "candidate",
  "book_ids": ["BOOK_01", "BOOK_02"],
  "comparison_ids": ["WB:BOOK:BOOK_01", "WB:BOOK:BOOK_02"],
  "comparison_dimensions": {
    "rule_engine": "相同或不同的规则发动方式",
    "scarcity_and_resource_flow": "稀缺与资源循环的相似和差异",
    "faction_ecology": "势力控制资源/权限的方式与关系网络",
    "institutions_and_power": "制度、组织和阶层流动",
    "conflict_generation": "持续冲突的生成方式",
    "plot_entry_and_map": "进入核心剧情和扩展地图的方式",
    "information_control": "信息差和揭示机制",
    "emotion_evidence": "读者期待、验证和余震的证据差异"
  },
  "similarities": [],
  "difference_boundary": "决定保持相近但不合并的核心差异",
  "decision": "merge_candidate|keep_distinct|insufficient_evidence",
  "reason": "比较理由",
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "PASS"
}
```

不能只因都有学校、军方、秘境、异族、考试或城市，就生成近邻。若核心规则、资源循环或冲突发动机不同，即使表面场景相似，也应 `keep_distinct`。

## 6. `cluster` 聚类候选

聚类必须在全部目标书的单书 QA 与近邻比较完成后生成，且只能是候选：

```json
{
  "record_type": "cluster",
  "schema_version": 2,
  "record_id": "WB:CLUSTER:001",
  "status": "candidate",
  "book_ids": ["BOOK_01", "BOOK_02"],
  "member_record_ids": ["WB:BOOK:BOOK_01", "WB:BOOK:BOOK_02"],
  "cluster_level": "大类|母型|子型|变体",
  "label": "不复制专名的功能性名称",
  "shared_operation": "共同的规则→稀缺→制度→冲突→剧情入口运行方式",
  "boundary_conditions": ["与相近候选保持区分的条件"],
  "supporting_book_count": 2,
  "nearest_neighbor_record_ids": ["WB:NEIGHBOR:001"],
  "merge_decision": "candidate_merge|candidate_split|new_candidate|insufficient_evidence|keep_distinct",
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "PASS"
}
```

`shared_operation` 必须描述因果运行链，不得只写“都市高武”“学校竞争”或其它题材皮肤。单书只能保留为 candidate 变体或待观察母型；任何来源书数都不能自动生成 `active`。

## 7. `qa` 与 `handoff` 记录

### `qa`

```json
{
  "record_type": "qa",
  "schema_version": 2,
  "record_id": "WB:QA:BOOK_01:1-120",
  "status": "candidate",
  "book_id": "BOOK_01",
  "scope": "BOOK_01:1-120",
  "checks": {
    "coverage": "PASS|HOLD|FAIL",
    "evidence_traceability": "PASS|HOLD|FAIL",
    "causal_chain": "PASS|HOLD|FAIL",
    "faction_structure": "PASS|HOLD|FAIL",
    "boundary_check": "PASS|HOLD|FAIL",
    "emotion_overlay_reference": "PASS|HOLD|FAIL",
    "cross_book_gate": "PASS|HOLD|FAIL"
  },
  "gaps": [],
  "disputes": [],
  "blocked_outputs": [],
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "MEDIUM",
  "qa_status": "PASS"
}
```

QA 只报告证据和阻断，不反向修改源章节或世界观记录。覆盖率分母使用冻结的目标章节范围；HOLD/FAIL 不支持高置信跨书聚类。

### `handoff`

```json
{
  "record_type": "handoff",
  "schema_version": 2,
  "record_id": "WB:HANDOFF:001",
  "status": "candidate",
  "book_ids": ["BOOK_01"],
  "candidate_record_ids": ["WB:BOOK:BOOK_01"],
  "recommended_action": "保留|合并候选|拆分候选|补证据|暂缓",
  "decision_points": ["需要人工确认的规则边界"],
  "evidence_gaps": [],
  "forbidden_automatic_actions": ["写入active", "修改canonical情绪Schema", "修改正式素材库"],
  "evidence_refs": [],
  "unknowns": [],
  "confidence": "LOW",
  "qa_status": "HOLD"
}
```

`handoff` 只表示等待人工审核，不代表候选已经通过审核或获得正式入库权限。

## 8. 统一禁止事项

- 不根据书名、简介、题材或模型记忆补造规则；
- 不把名词、背景、地图、组织或种族直接当作世界观机制；
- 不把金手指、修炼、人物、主线、篇章或剧情机制字段复制进本专项；
- 不把情绪 overlay 复制成第二套读者情绪 Schema；
- 不在证据不足时把 `partial` 或 `UNKNOWN` 擅自改成完整链条；
- 不在全部目标书完成前生成正常的近邻或聚类；
- 不把单书候选写成成熟母型、`active`、`deprecated` 或正式素材卡；
- 不修改源章节、既有 canonical 情绪记录、总索引或正式素材库。
