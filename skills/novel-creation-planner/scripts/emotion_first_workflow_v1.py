#!/usr/bin/env python3
"""Model-in-the-loop research workflow; never invokes a model or promotes assets.

prepare freezes sparse input and source retrieval; a Skill-hosted model authors TWO
separate composition fragments; finalize joins/validates them with existing bridge.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

SCHEMA = "nova_emotion_first_workflow_v1"
COMPOSITION_SCHEMA = "emotion_story_semantic_composition_v1"


def load(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(obj, dict):
        raise ValueError(f"expected JSON object: {path}")
    return obj


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def digest(obj: Any) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def assert_sparse(brief: dict[str, Any]) -> None:
    required = {"schema_version", "brief_id", "input_mode", "status", "genre", "core_reader_expectation", "emotion_contour", "required_emotion_weaves", "longform_requirement"}
    allowed = required | {"forbidden_prefill"}
    if set(brief) - allowed or required - set(brief):
        raise ValueError("sparse brief has missing or forbidden story fields")
    if brief["schema_version"] != "sparse_emotion_brief_v1" or brief["input_mode"] != "SPARSE_EMOTION_BRIEF" or brief["status"] != "candidate":
        raise ValueError("research sparse brief required")
    # Phase 1 keeps the current research retrieval/bridge input contract.
    # Wider genres and contours require an explicit, tested V2 contract change.
    if brief["genre"] != ["玄幻", "高武"] or brief["emotion_contour"] != ["DOWN", "DOWN", "UP"]:
        raise ValueError("Phase 1 supports only the existing 高武 DOWN/DOWN/UP research route")
    if not isinstance(brief["required_emotion_weaves"], list) or len(brief["required_emotion_weaves"]) != 4 or not all(isinstance(s, str) and s.strip() for s in brief["required_emotion_weaves"]):
        raise ValueError("Phase 1 needs exactly four high-level weave dimensions")
    if not all(isinstance(brief[k], str) and brief[k].strip() for k in ("brief_id", "core_reader_expectation", "longform_requirement")):
        raise ValueError("brief ID, expectation and long-form rule must be nonempty")


def corpus_ids(retrieval: dict[str, Any]) -> dict[str, set[str]]:
    return {role: {str(x.get("record_id")) for x in retrieval.get(key, [])} for role, key in (("line", "line_matches"), ("weave", "weave_matches"), ("macro", "macro_matches"), ("handoff", "handoff_matches"))}


def prompt(mode: str, brief: dict[str, Any], retrieval: dict[str, Any] | None) -> str:
    shared = f"""# Independent {mode} creative pass (RESEARCH ONLY)

Same frozen sparse brief for both passes (SHA-256 canonical JSON: {digest(brief)}).

{json.dumps(brief, ensure_ascii=False, indent=2)}

You are the SEMANTIC COMPOSER, not the source validator. Produce a standalone JSON
fragment with exactly: schema_version='emotion_story_composer_fragment_v1',
brief_id, mode='{mode}', status='candidate', semantic_composer={{'kind':
'MODEL_AUTHORED_RESEARCH_CANDIDATE','model_family':<truthful model name>,
'literary_approval':'NOT_GRANTED'}}, material_profiles, options (at least two).

Each option must meet the EXISTING emotion-story-bridge contract: ≥7 causal nodes,
nine-stage Story Spine, concrete 1–50 chapter phases, 02–09 functional slots, node-local
material effects, independent relationships and realistic costs. Both options must
have substantively different causal engines, not mere names. Use existing bridge
fixtures ONLY as schema examples; never transplant their story premises.

Work with existing 02–09 search tools from material-dispatch.md. Source IDs you
select/reject must really occur in the search results; do not invent. Missing or
incompatible sources become explicit ORIGINAL_DESIGN gaps. Every material has
an actionable role at specified story nodes. Keep candidates HOLD, no prose.

You must create the JSON artifact yourself in the research workspace. The user
must not hand-author a long semantic-composition file.
"""
    if mode == "LEGACY_BASELINE":
        return shared + "\n## Isolation\nThis pass may use 02–09 sources but MUST NOT read EL/EW/MA/AH retrieval, E2/E3 patterns or the enhanced candidate. Compose independently from the sparse brief. `options[*].mode` must be `LEGACY_BASELINE`. Do not add emotion_source_uses/emotion_lines/weaves/macro_arcs/handoff to legacy options.\n"
    if retrieval is None:
        raise ValueError("enhanced prompt requires retrieval")
    return shared + "\nEvery enhanced macro PAID requires `required_settlement_conditions` entries {condition_id, description, witness_node_id}; each witness must occur no later than its PAID transition. Do not use rescue success as proof of later administrative settlement.\n\n## Evidence inventory (candidate/HOLD only; NOT approved templates)\n" + json.dumps(retrieval, ensure_ascii=False, indent=2) + "\n\nUse actual retrieved EL/EW/MA/AH IDs; select relevant patterns and record similarity_reason, transferable_part, reuse_limit. `options[*].mode` must be `E2_E3_ENABLED`; include source-backed emotion_source_uses, independent payoff contracts and honest overlapping macro structure. Never turn AH001 into verified dominance transfer.\n"


def prepare(args: argparse.Namespace) -> None:
    from search_emotion_arc_library import search_library
    brief = load(args.brief)
    assert_sparse(brief)
    workspace = args.workspace.resolve()
    if workspace.exists() and any(workspace.iterdir()):
        raise ValueError("workspace not empty; select a new directory (no silent overwrite)")
    retrieval = search_library(args.emotion_library.resolve(), brief)
    if not retrieval.get("line_matches") or not retrieval.get("weave_matches"):
        raise ValueError("no evidence-backed emotion candidates; stop for review")
    dump(workspace / "brief.json", brief)
    dump(workspace / "emotion-retrieval.json", retrieval)
    (workspace / "01-legacy-prompt.md").write_text(prompt("LEGACY_BASELINE", brief, None), encoding="utf-8")
    (workspace / "02-enhanced-prompt.md").write_text(prompt("E2_E3_ENABLED", brief, retrieval), encoding="utf-8")
    dump(workspace / "session.json", {"schema_version": SCHEMA, "phase": "WAITING_FOR_MODEL", "status": "candidate", "production_promotion": "NOT_RUN", "brief_hash": digest(brief), "retrieval_hash": digest(retrieval), "emotion_package": str(args.emotion_library.resolve()), "model_passes": ["LEGACY_BASELINE", "E2_E3_ENABLED"], "independence": "REQUESTED_NOT_MACHINE_PROVEN", "quality": "NOT_EVALUATED"})
    print(json.dumps({"ok": True, "phase": "WAITING_FOR_MODEL", "workspace": str(workspace)}, ensure_ascii=False))


def check_conditions(option: dict[str, Any]) -> list[str]:
    if option.get("mode") != "E2_E3_ENABLED":
        return []
    errors = []
    nodes = option.get("story_nodes", [])
    positions = {n.get("node_id"): i for i, n in enumerate(nodes)}
    for m in option.get("macro_arcs", []):
        paid = [t for t in m.get("state_transitions", []) if t.get("to") == "PAID"]
        if not paid:
            continue
        conditions = m.get("required_settlement_conditions", [])
        if not isinstance(conditions, list) or not conditions:
            errors.append(f"{m.get('macro_id')}: PAID without explicit settlement witnesses")
            continue
        pos = positions.get(paid[0].get("node_id"))
        if pos is None:
            errors.append(f"{m.get('macro_id')}: PAID at unknown node")
            continue
        for c in conditions:
            cp = positions.get(c.get("witness_node_id"))
            if not c.get("condition_id") or not c.get("description") or cp is None:
                errors.append(f"{m.get('macro_id')}: settlement witness incomplete")
            elif cp > pos:
                errors.append(f"{m.get('macro_id')}: {c.get('condition_id')} occurs after PAID")
    return errors


def finalize(args: argparse.Namespace) -> None:
    workspace = args.workspace.resolve()
    session, brief, retrieval = (load(workspace / x) for x in ("session.json", "brief.json", "emotion-retrieval.json"))
    if session.get("schema_version") != SCHEMA or session.get("phase") != "WAITING_FOR_MODEL":
        raise ValueError("session not prepared or already finalized")
    if digest(brief) != session.get("brief_hash") or digest(retrieval) != session.get("retrieval_hash"):
        raise ValueError("frozen brief/retrieval was changed")
    legacy, enhanced = load(args.legacy), load(args.enhanced)
    for file, mode in ((legacy, "LEGACY_BASELINE"), (enhanced, "E2_E3_ENABLED")):
        if file.get("schema_version") != "emotion_story_composer_fragment_v1" or file.get("brief_id") != brief["brief_id"] or file.get("status") != "candidate" or file.get("mode") != mode:
            raise ValueError(f"invalid or swapped independent model fragment: {mode}")
        if len(file.get("options", [])) < 2:
            raise ValueError(f"{mode}: two original options required")
        if file.get("semantic_composer", {}).get("kind") != "MODEL_AUTHORED_RESEARCH_CANDIDATE":
            raise ValueError(f"{mode}: record truthful model authoring provenance")
    if set(legacy.get("material_profiles", {})) & set(enhanced.get("material_profiles", {})):
        raise ValueError("legacy/enhanced material profile IDs must be separate")
    matches = corpus_ids(retrieval)
    for opt in enhanced["options"]:
        for use in opt.get("emotion_source_uses", []):
            if str(use.get("record_id")) not in matches.get(use.get("record_kind"), set()):
                raise ValueError("semantic composer cited a source absent from frozen retrieval")
        issues = check_conditions(opt)
        if issues:
            dump(workspace / "model-repair-request.json", {"status": "HOLD", "issues": issues, "repair_only": "correct contract witnesses and state; never weaken original conditions"})
            raise ValueError("settlement timing HOLD: " + "; ".join(issues))
    if {o.get("pair_id") for o in legacy["options"]} != {o.get("pair_id") for o in enhanced["options"]}:
        raise ValueError("independent comparison pair IDs differ")
    combined = {"schema_version": COMPOSITION_SCHEMA, "brief_id": brief["brief_id"], "status": "candidate", "semantic_composer": {"kind": "MODEL_AUTHORED_RESEARCH_CANDIDATE", "model_family": "MULTI_PASS_AS_DECLARED", "deterministic_validation_required": True, "literary_approval": "NOT_GRANTED"}, "material_profiles": {**legacy.get("material_profiles", {}), **enhanced.get("material_profiles", {})}, "legacy_options": legacy["options"], "enhanced_options": enhanced["options"]}
    attempts_root = workspace / "attempts"
    previous = sorted(attempts_root.glob("attempt-*")) if attempts_root.exists() else []
    if len(previous) >= 3:
        raise ValueError("three total model validation attempts exhausted; STOP/HOLD")
    attempt = attempts_root / f"attempt-{len(previous) + 1:02d}"
    combined_path = attempt / "semantic-composition.generated.json"
    dump(combined_path, combined)
    script = Path(__file__).with_name("run_emotion_story_bridge_pilot.py")
    run = subprocess.run([sys.executable, str(script), "--brief", str(workspace / "brief.json"), "--semantic-composition", str(combined_path), "--emotion-library", session["emotion_package"], "--material-snapshot-repo", str(args.material_snapshot_repo.resolve()), "--material-snapshot-commit", args.material_snapshot_commit, "--material-package-subdir", args.material_package_subdir, "--output-dir", str(attempt / "result")], capture_output=True, text=True, encoding="utf-8")
    if run.returncode:
        dump(workspace / "model-repair-request.json", {"status": "HOLD", "error": run.stdout[-5000:] or run.stderr[-5000:], "repair_only": "repair model composition, not validator or contract"})
        raise ValueError("bridge validation HOLD; see model-repair-request.json")
    result = load(attempt / "result" / "validation-report.json")
    if not result.get("ok"):
        raise ValueError("bridge returned a nonpassing report")
    session.update(phase="VALIDATED_RESEARCH", quality="PENDING_INDEPENDENT_REVIEW", material_adaptation="REVIEW_REQUIRED", production_promotion="NOT_RUN", final_attempt=str(attempt.relative_to(workspace)))
    (workspace / "model-repair-request.json").unlink(missing_ok=True)
    dump(workspace / "session.json", session)
    print(json.dumps({"ok": True, "phase": "VALIDATED_RESEARCH", "quality": "PENDING_INDEPENDENT_REVIEW", "workspace": str(workspace)}, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser(description="Research-only model-in-the-loop Emotion-First Skill workflow")
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--brief", type=Path, required=True)
    p.add_argument("--emotion-library", type=Path, required=True)
    p.add_argument("--workspace", type=Path, required=True)
    f = sub.add_parser("finalize")
    f.add_argument("--workspace", type=Path, required=True)
    f.add_argument("--legacy", type=Path, required=True)
    f.add_argument("--enhanced", type=Path, required=True)
    f.add_argument("--material-snapshot-repo", type=Path, required=True)
    f.add_argument("--material-snapshot-commit", required=True)
    f.add_argument("--material-package-subdir", default="packages/shared-dna-library/v1.0.0")
    args = parser.parse_args()
    try:
        (prepare if args.action == "prepare" else finalize)(args)
        return 0
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc), "phase": args.action, "status": "HOLD"}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
