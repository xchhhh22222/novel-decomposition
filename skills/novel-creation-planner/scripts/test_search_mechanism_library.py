#!/usr/bin/env python3
"""Smoke tests for the RMF mechanism-library adapter (search_mechanism_library.py).

Covers the five human-approved integration cases (A-E), the four negative cases
(N1-N4), held/dropped exclusion, format handling, and planner backward
compatibility via validate_creation_plan.py. Self-contained fixture: no
machine-specific paths, no external dependencies.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SEARCH = Path(__file__).with_name("search_mechanism_library.py")
VALIDATOR = Path(__file__).with_name("validate_creation_plan.py")

R1 = "RMF:CHARACTER_FUNCTION:2fd0415e3b3081ae"
R2 = "RMF:CHARACTER_FUNCTION:45237559c05a719c"
R3 = "RMF:CHARACTER_FUNCTION:ebe864d97777d842"
R4 = "RMF:CHARACTER_FUNCTION:37eab9cea129a77d"
R5 = "RMF:CHARACTER_FUNCTION:80489c4dab35983c"
GFC1 = "RMF:GOLDEN_FINGER:5af403fc21b018c1"
P1 = "RMF:PLOTLINE:e577d366837ff977"
P2 = "RMF:PLOTLINE:1fa763261ef73f40"
GFA1 = "RMF:GOLDEN_FINGER:9be257f192a1ee94"
HELD_GFC = "RMF:GOLDEN_FINGER:0524302913550212"
HELD_GFA = "RMF:GOLDEN_FINGER:3deeb325ec7e09a2"

FAMILIES = [
    {"family_id": fid, "family_name": name, "domain": dom, "comparison_lane": lane,
     "one_sentence_core": core,
     "minimum_definition": {"trigger": core[:12], "transformation": "deterministic", "recurrence": "loop"},
     "hard_invariants": ["invariant-1"], "exclusion_boundary": ["boundary-1"],
     "termination_condition": "termination-1"}
    for fid, name, dom, lane, core in [
        (R1, "异常验证后受约束准入", "character_function", "relationship_engine", "待承认异常 → 产生新证据的验证 → 风险价值重估 → 开放受约束行动入口"),
        (R2, "不可替代筹码互需谈判", "character_function", "relationship_engine", "双方互持不可替代输入 → 试探要价 → 有限交换 → 新筹码生成下一轮谈判"),
        (R3, "公开评价场中的对手互证与位置重定价", "character_function", "relationship_engine", "公开评价压力 → 对手制造真实表现 → 结果公开结算 → 排名资格资源位置重新定价"),
        (R4, "共同目标下的固定能力补位协作", "character_function", "relationship_engine", "共同目标产生功能缺口 → 固定角色功能接口 → 联合结果 → 下一任务继续调用接口"),
        (R5, "反复越界侵入造成的主体自主性侵蚀", "character_function", "relationship_engine", "另一能动主体跨越主体边界 → 身份灵魂控制层侵入 → 自主完整性退化 → 未决控制争议继续生成侵入反抗"),
        (GFC1, "可支配资源经确定规则压缩或放大成长", "golden_finger", "GF_CORE", "取得可支配输入 → 确定规则消耗转换获得可复投成长资产 → 更强行动获得下一轮输入"),
        (P1, "公开门槛战果重估能力并打开更高资格", "plotline", "plotline_progression_engine", "资格估值受限 → 公开门槛交付战果 → 制度重估 → 开放更高资格资源 → 更高门槛继续验证"),
        (P2, "局部高风险谜题求解生成更大真相入口", "plotline", "plotline_progression_engine", "高风险局部未知 → 试探规则纠正解释取证 → 获得可行动实证 → 实证暴露更大未知 → 下一调查"),
        (GFA1, "陈述真伪判定", "golden_finger", "GF_ABILITY", "目标产生陈述 → 判断陈述真实性欺骗状态 → 输出真伪判定 → 获得信息优势"),
    ]
]

RECIPES = [
    {"recipe_id": "REC-001", "status": "CANDIDATE_NOT_PROMOTED",
     "recipe_name": "成长 → 证明 → 新资源 → 再成长（长期成长—资格双循环）",
     "family_sequence": [GFC1, P1], "source_family_ids": [GFC1, P1],
     "composition_link_ids": ["CL-006", "CL-007"],
     "slot_roles": ["金手指核心：资源转换主体", "剧情推进：公开门槛挑战者"],
     "entry_condition": "主角持有可支配可消耗规则可知的转换输入，且存在公开可结算的能力评价制度",
     "creative_value": "跨章节长线升级主轴；将抽象战力成长落成可公开验证的剧情事件",
     "recurrence_loop": "双循环：GFC1 --CL-006--> P1 --CL-007--> GFC1",
     "joint_bridge_conditions": ["回流资源必须是 GFC1 认可的可支配输入"],
     "failure_modes": ["资源回流被写成直接变强而绕过确定转换规则"],
     "variation_axes": ["转换规则形态", "公开门槛载体"]},
    {"recipe_id": "REC-002", "status": "CANDIDATE_NOT_PROMOTED",
     "recipe_name": "测谎 → 解谜 → 更大谜题（真伪判定驱动的调查链）",
     "family_sequence": [GFA1, P2], "source_family_ids": [GFA1, P2],
     "composition_link_ids": ["CL-008"], "slot_roles": ["金手指能力：真伪判定者", "剧情推进：调查主体"],
     "entry_condition": "调查中存在高风险局部未知，且关键节点依赖对某一具体陈述的真伪判断",
     "creative_value": "悬疑主线的证据引擎：给调查节奏一个硬性的真伪锚点",
     "recurrence_loop": "递归循环：P2 的更大未知成为下一轮调查入口",
     "joint_bridge_conditions": ["self-deception blind spot 必须保留为破局限制", "真伪判定不等于完整谜题答案"],
     "failure_modes": ["真伪判定被当成万能破解器直接给出答案", "忽略 self-deception 使主角无懈可击"],
     "variation_axes": ["判定触发方式", "未知风险维度"]},
    {"recipe_id": "REC-003", "status": "CANDIDATE_NOT_PROMOTED",
     "recipe_name": "调查 → 筹码 → 交换 → 新调查（调查—谈判双循环）",
     "family_sequence": [P2, R2], "source_family_ids": [P2, R2],
     "composition_link_ids": ["CL-009", "CL-010"], "slot_roles": ["剧情推进：调查者", "关系引擎：情报持有对手"],
     "entry_condition": "调查者已获得对其对手短期不可绕过的实证或秘密，且双方互持必需输入",
     "creative_value": "悬疑+权谋复合主线：让情报既驱动解谜又驱动博弈",
     "recurrence_loop": "双循环：P2 --CL-009--> R2 --CL-010--> P2",
     "joint_bridge_conditions": ["筹码必须满足 mutual need 不可替代性：对方短期无法绕过", "每次交换有限保留剩余筹码"],
     "failure_modes": ["把有信息直接当成筹码而不管对方是否必需"],
     "variation_axes": ["筹码类型", "对手关系"]},
    {"recipe_id": "REC-004", "status": "CANDIDATE_NOT_PROMOTED",
     "recipe_name": "异常验证 → 准入 → 正式门槛 → 更高资格（评价重估接入链）",
     "family_sequence": [R1, P1], "source_family_ids": [R1, P1],
     "composition_link_ids": ["CL-001"], "slot_roles": ["关系引擎：待承认异常主体", "剧情推进：资格竞争者"],
     "entry_condition": "主角携带尚未被制度承认的异常能力，且存在通往正式公开评价制度的路径",
     "creative_value": "升级流开局的合法性引擎：解释主角为什么能进场凭什么被承认",
     "recurrence_loop": "复合循环：每级正式资格制造新的未验证异常",
     "joint_bridge_conditions": ["R1 的受约束准入不等于 P1 的正式资格"],
     "failure_modes": ["把 R1 准入直接当成 P1 资格而跳过战果交付"],
     "variation_axes": ["异常性质", "把关人立场"]},
    {"recipe_id": "REC-005", "status": "CANDIDATE_NOT_PROMOTED",
     "recipe_name": "对手评价 → 成长资源 → 更强表现 → 再评价（竞争成长飞轮）",
     "family_sequence": [R3, GFC1], "source_family_ids": [R3, GFC1],
     "composition_link_ids": ["CL-013", "CL-014"], "slot_roles": ["关系引擎：公开评价场竞争者", "金手指核心：资源转换主体"],
     "entry_condition": "存在公开评价制度且其结算奖励是可支配资源",
     "creative_value": "竞技学院职场流的成长发动机：竞争压力直接燃料化",
     "recurrence_loop": "飞轮：R3 --CL-013--> GFC1 --CL-014--> R3",
     "joint_bridge_conditions": ["结算奖励必须真的是 GFC1 输入不变量认可的资源"],
     "failure_modes": ["奖励是空头荣誉却仍触发转换"], "variation_axes": ["评价场类型", "对手弧线"]},
    {"recipe_id": "REC-006", "status": "CANDIDATE_NOT_PROMOTED",
     "recipe_name": "正式任务 → 固定协作 → 团队战果 → 更高任务（团队升级主轴）",
     "family_sequence": [P1, R4], "source_family_ids": [P1, R4],
     "composition_link_ids": ["CL-015", "CL-016"], "slot_roles": ["剧情推进：任务发布资格制度", "关系引擎：固定协作团队"],
     "entry_condition": "资格重估开放的正式任务要求两个以上不可互换的功能槽位",
     "creative_value": "团队型升级主线：把人际关系稳定化和剧情升级绑在同一条轨道",
     "recurrence_loop": "复合循环：P1 --CL-015--> R4 --CL-016--> P1",
     "joint_bridge_conditions": ["任务的功能缺口必须真实对应 R4 的固定接口，两个槽位不可互换",
                                  "联合结果必须是第三方制度可观察可结算的形态"],
     "failure_modes": ["槽位可互换退化成普通组队"], "variation_axes": ["功能分工类型", "团队张力"]},
    {"recipe_id": "REC-007", "status": "CANDIDATE_NOT_PROMOTED",
     "recipe_name": "控制争议 → 有界谜题（身份威胁驱动调查）",
     "family_sequence": [R5, P2], "source_family_ids": [R5, P2],
     "composition_link_ids": ["CL-012"], "slot_roles": ["关系引擎：被侵蚀主体", "剧情推进：调查主体"],
     "entry_condition": "身份控制完整性争议的原因规则与控制者均未知，且具有现实紧迫风险",
     "creative_value": "暗黑悬疑主线：内在威胁与外部解谜同构",
     "recurrence_loop": "双线并行：侵蚀进程与调查进程交替推进",
     "joint_bridge_conditions": ["争议必须自带边界（时间窗/范围/风险上限），构成有界高风险未知"],
     "failure_modes": ["把侵蚀写成纯恐怖氛围而不构成可调查的未知"], "variation_axes": ["侵入形态", "揭示节奏"]},
]

SHORT = {
    R1: "R1 异常验证准入", R2: "R2 筹码谈判", R3: "R3 评价场重定价", R4: "R4 固定协作", R5: "R5 自主性侵蚀",
    GFC1: "GFC1 资源成长", P1: "P1 公开门槛资格", P2: "P2 谜题调查", GFA1: "GFA1 真伪判定",
}

LINKS = [
    {"link_id": f"CL-{i:03d}", "source_family_id": s, "target_family_id": t,
     "composition_relation": rel,
     "source_output": f"{SHORT[s]} 的可结算输出",
     "target_trigger_or_input": f"{SHORT[t]} 所需输入",
     "bridge_condition": f"CL-{i:03d}：{SHORT[s]} 输出在 bridge 条件下接入 {SHORT[t]} 触发（{rel}）"}
    for i, (s, t, rel) in enumerate([
        (R1, P1, "LEFT_CAN_FEED_RIGHT"), (P2, R1, "BIDIRECTIONAL_POSSIBLE"), (R1, P2, "BIDIRECTIONAL_POSSIBLE"),
        (P2, R1, "BIDIRECTIONAL_POSSIBLE"), (R1, P2, "BIDIRECTIONAL_POSSIBLE"), (GFC1, P1, "BIDIRECTIONAL_POSSIBLE"),
        (P1, GFC1, "BIDIRECTIONAL_POSSIBLE"), (GFA1, P2, "LEFT_CAN_FEED_RIGHT"), (P2, R2, "BIDIRECTIONAL_POSSIBLE"),
        (R2, P2, "BIDIRECTIONAL_POSSIBLE"), (P1, R2, "LEFT_CAN_FEED_RIGHT"), (R5, P2, "LEFT_CAN_FEED_RIGHT"),
        (R3, GFC1, "BIDIRECTIONAL_POSSIBLE"), (GFC1, R3, "BIDIRECTIONAL_POSSIBLE"), (R4, P1, "BIDIRECTIONAL_POSSIBLE"),
        (P1, R4, "BIDIRECTIONAL_POSSIBLE"),
    ], start=1)
]

DROPPED_REC_008 = {"recipe_id": "REC-008", "status": "DROPPED_FROM_PROMOTION_SET",
                    "recipe_name": "评价场 → 调查 → 再评价（公开结算与真相互锁）",
                    "family_sequence": [R3, P2], "source_family_ids": [R3, P2],
                    "composition_link_ids": ["CL-004", "CL-005"], "slot_roles": [],
                    "entry_condition": "评价场中存在可疑未知", "creative_value": "评价场×调查",
                    "recurrence_loop": "循环", "joint_bridge_conditions": [], "failure_modes": [],
                    "variation_axes": []}


def build_package(root: Path, *, active: bool = False, include_dropped: bool = False,
                  leak_held_into_stable: bool = False) -> None:
    root.mkdir(parents=True, exist_ok=True)
    families = list(FAMILIES)
    if leak_held_into_stable:
        families = families + [{"family_id": HELD_GFA, "family_name": "接触式目标能力获取（LEAKED）",
                                 "domain": "golden_finger", "comparison_lane": "GF_ABILITY",
                                 "one_sentence_core": "接触式目标能力获取", "minimum_definition": {},
                                 "hard_invariants": [], "exclusion_boundary": [], "termination_condition": ""}]
    (root / "stable-families.json").write_text(json.dumps({"families": families}, ensure_ascii=False), encoding="utf-8")
    (root / "held-families.json").write_text(json.dumps({
        "held_families": [{"family_id": HELD_GFC}, {"family_id": HELD_GFA}]}, ensure_ascii=False), encoding="utf-8")
    (root / "composition-links.jsonl").write_text(
        "".join(json.dumps(l, ensure_ascii=False) + "\n" for l in LINKS), encoding="utf-8")
    recipes = RECIPES + ([DROPPED_REC_008] if include_dropped else [])
    (root / "composition-recipes.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recipes), encoding="utf-8")
    (root / "mechanism-slot-index.json").write_text(json.dumps({
        "slots": {"golden_finger_core": {"candidate_family_ids": [GFC1]},
                   "golden_finger_ability": {"candidate_family_ids": [GFA1]},
                   "plotline": {"candidate_family_ids": [P1, P2]},
                   "relationship_engine": {"candidate_family_ids": [R1, R2, R3, R4, R5]}},
        "retrieval_tags": {"resource_growth": [GFC1], "truth_detection": [GFA1], "investigation": [P2],
                            "negotiation": [R2], "teamwork": [R4], "identity_control_threat": [R5]},
    }, ensure_ascii=False), encoding="utf-8")
    (root / "composition-adjacency-index.json").write_text(json.dumps({
        "families": {f["family_id"]: {"outbound_link_ids": [], "inbound_link_ids": []} for f in FAMILIES}},
        ensure_ascii=False), encoding="utf-8")
    (root / "manifest.json").write_text(json.dumps({
        "package_id": "nova-mechanism-library", "package_version": "1.7.0",
        "status": "ACTIVE" if active else "INSTALLATION_STAGING_NOT_PROMOTED",
        "active_promotion": active,
        "excluded_assets": [{"asset_id": "REC-008", "reason": "DROPPED_INVALID_PROVENANCE"},
                             {"asset_ids": [HELD_GFC, HELD_GFA], "reason": "HELD_FAMILIES_OUTSIDE_ACTIVE_REGISTRY"}],
    }, ensure_ascii=False), encoding="utf-8")


def run_search(library: Path, *args: str) -> tuple[int, dict | str]:
    result = subprocess.run([sys.executable, str(SEARCH), "--library", str(library), *args],
                            capture_output=True, text=True, encoding="utf-8")
    try:
        return result.returncode, json.loads(result.stdout)
    except json.JSONDecodeError:
        return result.returncode, result.stdout


def main() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        staging = tmp / "staging-package"
        build_package(staging, active=False, include_dropped=True, leak_held_into_stable=True)
        active = tmp / "active-package"
        build_package(active, active=True, include_dropped=True, leak_held_into_stable=True)

        def check(name: str, cond: bool, detail: str = "") -> None:
            if not cond:
                failures.append(f"{name}: {detail}")

        # N3: unavailable root
        code, out = run_search(tmp / "does-not-exist", "--query", "x", "--allow-staging")
        check("N3 unavailable gap", code == 2 and isinstance(out, dict) and out.get("gap") == "MECHANISM_LIBRARY_UNAVAILABLE", str(out)[:120])

        # N4: staging package without --allow-staging must GAP, not silently act as active
        code, out = run_search(staging, "--query", "升级")
        check("N4 not-active gap", code == 3 and isinstance(out, dict) and out.get("gap") == "MECHANISM_LIBRARY_NOT_ACTIVE", str(out)[:120])

        # N4 + staging flag: integration/verification mode works
        code, out = run_search(staging, "--query", "升级", "--allow-staging")
        check("N4 allow-staging runs", code == 0 and isinstance(out, dict) and out.get("library_status") == "STAGING", str(out)[:120])

        # active package runs without the flag
        code, out = run_search(active, "--query", "升级")
        check("active runs without flag", code == 0 and isinstance(out, dict) and out.get("library_status") == "ACTIVE", str(out)[:120])

        def q(query: str) -> dict:
            code, out = run_search(active, "--query", query, "--allow-staging" if False else "--allow-staging")
            if code != 0 or not isinstance(out, dict):
                raise AssertionError(f"search failed for {query!r}: {out}")
            return out

        # TEST A
        r = q("我要一个升级爽文长线循环")
        recipes = [x["recipe_id"] for x in r["results"]["recipe"]]
        fams = {x["family_id"] for x in r["results"]["family"]}
        check("A: REC-001 top", recipes and recipes[0] == "REC-001", str(recipes))
        check("A: GFC1 recalled", GFC1 in fams, str(fams))
        check("A: P1 recalled", P1 in fams, str(fams))

        # TEST B
        r = q("我要悬疑调查 + 特殊能力，但不能直接破案")
        recipes = [x["recipe_id"] for x in r["results"]["recipe"]]
        fams = {x["family_id"] for x in r["results"]["family"]}
        rec2 = next((x for x in r["results"]["recipe"] if x["recipe_id"] == "REC-002"), {})
        text = json.dumps(rec2, ensure_ascii=False)
        check("B: REC-002 top", recipes and recipes[0] == "REC-002", str(recipes))
        check("B: GFA1 recalled", GFA1 in fams, str(fams))
        check("B: P2 recalled", P2 in fams, str(fams))
        check("B: self-deception limitation surfaced", "self-deception" in text, text[:200])

        # TEST C
        r = q("我要调查中不断和敌对角色交换情报")
        recipes = [x["recipe_id"] for x in r["results"]["recipe"]]
        fams = {x["family_id"] for x in r["results"]["family"]}
        rec3 = json.dumps(next((x for x in r["results"]["recipe"] if x["recipe_id"] == "REC-003"), {}), ensure_ascii=False)
        check("C: REC-003 top", recipes and recipes[0] == "REC-003", str(recipes))
        check("C: P2 recalled", P2 in fams and R2 in fams, str(fams))
        check("C: mutual need bridge", "mutual need" in rec3 and "不可替代" in rec3, rec3[:200])

        # TEST D
        r = q("我要团队型主线升级")
        recipes = [x["recipe_id"] for x in r["results"]["recipe"]]
        fams = {x["family_id"] for x in r["results"]["family"]}
        rec6 = json.dumps(next((x for x in r["results"]["recipe"] if x["recipe_id"] == "REC-006"), {}), ensure_ascii=False)
        check("D: REC-006 top", recipes and recipes[0] == "REC-006", str(recipes))
        check("D: R4+P1 recalled", R4 in fams and P1 in fams, str(fams))
        check("D: non-interchangeable + settleable bridges", "不可互换" in rec6 and "可结算" in rec6, rec6[:200])

        # TEST E
        r = q("我要身份/寄生控制威胁带动谜题")
        recipes = [x["recipe_id"] for x in r["results"]["recipe"]]
        fams = {x["family_id"] for x in r["results"]["family"]}
        rec7 = json.dumps(next((x for x in r["results"]["recipe"] if x["recipe_id"] == "REC-007"), {}), ensure_ascii=False)
        check("E: REC-007 top", recipes and recipes[0] == "REC-007", str(recipes))
        check("E: R5+P2 recalled", R5 in fams and P2 in fams, str(fams))
        check("E: bounded unknown bridge", "有界" in rec7, rec7[:200])

        # N1: dropped REC-008 must never be returned (it exists in the raw fixture payload)
        for query in ("评价场 调查 真相", "评价场", "调查 真相"):
            r = q(query)
            ids = [x["recipe_id"] for x in r["results"]["recipe"]]
            all_ids = [x["recipe_id"] for x in r["results"]["recipe"]] + [x.get("recipe_id") for x in r["results"]["family"]]
            check(f"N1 no REC-008 ({query!r})", "REC-008" not in ids and "REC-008" not in all_ids, str(ids))

        # N2: held families must never be returned (one is even leaked into the stable payload)
        for query in ("升级", "调查", "接触式目标能力获取", "身份 侵入"):
            r = q(query)
            fams = [x["family_id"] for x in r["results"]["family"]]
            check(f"N2 no held ({query!r})", HELD_GFC not in fams and HELD_GFA not in fams, str(fams))
            assert isinstance(r["results"], dict)
        check("N2 excluded list present", set(r["excluded"]["held_family_ids"]) == {HELD_GFC, HELD_GFA}, str(r["excluded"]))

        # formats
        code, out = run_search(active, "--query", "升级", "--format", "md", "--allow-staging")
        check("md format", code == 0 and isinstance(out, str) and "REC-001" in out, str(out)[:120])
        code, out = run_search(active, "--query", "升级", "--format", "jsonl", "--allow-staging")
        lines = [l for l in out.strip().splitlines() if l.strip()] if isinstance(out, str) else []
        check("jsonl format", code == 0 and lines and all(json.loads(l).get("asset_type") for l in lines), str(out)[:120])

        # asset-types filter
        code, out = run_search(active, "--query", "成长 接入", "--asset-types", "link", "--allow-staging")
        check("asset-types filter", code == 0 and isinstance(out, dict)
              and out["results"]["recipe"] == [] and out["results"]["family"] == [] and out["results"]["link"], str(out)[:120])

        # slots routing
        code, out = run_search(active, "--query", "故事怎么跑", "--slots", "longline_engine", "--allow-staging")
        check("slots longline_engine promotes recipes", code == 0 and isinstance(out, dict)
              and out["results"]["recipe"], str(out)[:160])

        # ---- planner backward compatibility: existing plan validation unaffected ----
        sys.path.insert(0, str(Path(__file__).parent))
        from test_validate_creation_plan import valid_plan, validate  # reuse the full approved fixture

        code, output = validate(valid_plan())
        check("legacy plan still validates", code == 0, output[:300])

        # mechanism-extended plan: mechanism_library_root + new library_usage ids + new material_kind
        mech_plan = valid_plan()
        mech_plan["mechanism_library_root"] = str(active)
        mech_plan["library_usage"]["mechanism_family_ids"] = [GFC1, P1]
        mech_plan["library_usage"]["composition_recipe_ids"] = ["REC-001"]
        mech_plan["library_usage"]["composition_link_ids"] = ["CL-006"]
        mech_plan["material_dispatch"]["slots"].append({
            "slot_id": "SLOT:MECHANISM_ENGINE", "role": "mechanism_engine", "required": True, "wave": 1,
            "modules": [], "component_types": [], "query_groups": ["story engine"], "target_candidates": 2,
            "source_strategy": "mechanism_library",
            "selected_refs": [{"material_id": "REC-001", "material_kind": "composition_recipe",
                                 "module": "mechanism_library", "record_id": "REC-001",
                                 "component_type": "", "book_id": "", "qa_status": "PASS"}],
            "rejected_refs": [], "gap_reason": ""})
        code, output = validate(mech_plan)
        check("mechanism-extended plan validates", code == 0, output[:300])

        # invalid mechanism reference must be rejected
        bad_plan = valid_plan()
        bad_plan["mechanism_library_root"] = str(active)
        bad_plan["library_usage"]["composition_recipe_ids"] = ["REC-999"]
        code, output = validate(bad_plan)
        check("invalid recipe id rejected", code != 0, output[:200])

        # legacy plan without mechanism root but with stray mechanism kinds must still be rejected
        stray = valid_plan()
        stray["material_dispatch"]["slots"][0]["selected_refs"][0]["material_kind"] = "composition_recipe"
        code, output = validate(stray)
        check("stray mechanism kind without root rejected", code != 0, output[:200])

    print(json.dumps({"ok": not failures, "failures": failures}, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
