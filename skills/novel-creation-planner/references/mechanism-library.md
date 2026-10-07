# Mechanism Library（RMF 机制库接入）

## 双层素材架构

```text
mechanism_library_root            shared_library_root
  故事发动机 / 怎么跑               具体世界 / 用什么实现
  reusable family                  per-book DNA components
  composition link / recipe        formal cards / derived assets
```

- **机制库决定 `HOW THE STORY RUNS`**：可复用机制 family（跨书稳定）、composition link（A 的输出如何在 bridge 条件下接入 B）、composition recipe（多 family 组合的创作循环）。
- **DNA/素材库决定 `WHAT THE STORY IS MADE OF`**：世界观专名、修炼境界、具体技能、势力、资源、人物、per-book 组件。
- 两层是不同的可信层，**不得混用同一个 root**，不得把 RMF family 伪装成 formal_card / DNA cluster / plot-mechanism card / emotion card。

## 三层资产语义

1. **family**（`stable-families.json`）：人工验证的跨书稳定机制。携带 `family_id`（`RMF:<DOMAIN>:<hash>`）、`minimum_definition`、`hard_invariants`、`exclusion_boundary`、`termination`。Planner 用它回答"这个故事由什么机制驱动"。
2. **composition link**（`composition-links.jsonl`）：`source_family_id` 的输出在明确 `bridge_condition` 下成为 `target_family_id` 的输入。用于解释"为什么 A 能接 B"。`membership_effect = NONE`、`identity_effect = NONE`——link 永远不改变 family 语义。
3. **composition recipe**（`composition-recipes.jsonl`，仅 `REC-001…REC-007`）：多 family 组合的因果循环（entry_condition → causal chain → recurrence → termination），带 `bridge_requirements` 与 `failure_modes`。Recipe 不是新 family。

## 排除资产（永不返回/永不可引用）

- Held families：`RMF:GOLDEN_FINGER:0524302913550212`、`RMF:GOLDEN_FINGER:3deeb325ec7e09a2`——正常创作路径不可见，重新进入需 staged research + human review。
- Dropped recipes：`REC-008`（`DROPPED_INVALID_PROVENANCE`）——不得出现在任何 routing 结果或 plan 引用中。

## 配置

Plan（可选字段，向后兼容）：

```json
{
  "shared_library_root": "/abs/path/shared-material-library",
  "mechanism_library_root": "/abs/path/packages/mechanism-library/v1.7.0",
  "library_usage": {
    "mechanism_family_ids": ["RMF:GOLDEN_FINGER:5af403fc21b018c1"],
    "composition_recipe_ids": ["REC-001"],
    "composition_link_ids": ["CL-006"]
  }
}
```

- `mechanism_library_root` 缺省 → planner 按旧流程运行，行为完全不变。
- 两个 root 语义不同，禁止把 mechanism root 塞进 shared root。

## 检索

```bash
python3 skills/novel-creation-planner/scripts/search_mechanism_library.py \
  --library "$mechanism_library_root" \
  --query "我要一个升级爽文长线循环" \
  --slots "longline_engine" \
  --limit 5 --format json
```

- 确定性检索：关键词 + 受控 tags + slot matching + lexical scoring；**不做 embedding / 聚类**——机制已被人工验证，adapter 只做 retrieval + routing。
- GAPS：`MECHANISM_LIBRARY_UNAVAILABLE`（root/manifest 缺失）、`MECHANISM_LIBRARY_NOT_ACTIVE`（package `active_promotion=false` 且未显式 `--allow-staging`；`--allow-staging` 仅用于 integration test / installation verification）。

## Routing 顺序（Wave 0）

配置了 `mechanism_library_root` 时，在原 Material Dispatch Wave 1 之前增加轻量阶段：

```text
用户需求
→ Wave 0: search_mechanism_library 召回 2–4 个 families / recipes
→ 选一个主 story engine，提取 bridge / preconditions / failure conditions
→ Wave 1 骨架素材召回（DNA library）
→ Wave 2 冲突与供给
→ Wave 3 表现层
→ Wave 4 验证补洞
```

机制层输出的不是素材，而是**素材槽位需求**（例如 `golden_finger_core` 槽位需要"可支配、可消耗、规则可知的输入"），具体实现由 DNA/material library + creative layer 完成，并执行 compatibility / source concentration / originality check。

## Plan 校验

`validate_creation_plan.py` 对 mechanism 扩展的规则：

- `mechanism_library_root`（可选）：提供时必须是非空绝对路径。
- `library_usage.mechanism_family_ids[]` / `composition_recipe_ids[]` / `composition_link_ids[]`（可选）：id 格式分别为 `RMF:<DOMAIN>:<hash>` / `REC-\d{3}` / `CL-\d{3}`；提供任一 id 时必须有 `mechanism_library_root`；package 可读时校验引用闭环（id 必须存在于 package payload，且不得是 held/dropped 资产）。
- `material_dispatch.slots[].selected_refs[].material_kind` 新增合法值：`mechanism_family` / `composition_recipe` / `composition_link`；使用时 plan 必须有 `mechanism_library_root` 且 material_id 必须登记在对应 `library_usage.*_ids` 中；`source_strategy` 新增 `mechanism_library`。
- 未使用 mechanism 字段的旧计划校验行为完全不变。
