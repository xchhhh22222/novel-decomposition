#!/usr/bin/env python3
"""NOVA Emotion Arc V2 validator matrix (T01-T21)."""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from validate_emotion_arc_research import validate_pilot


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def envelope(kind: str, ident: str, refs: list[str]) -> dict:
    return {
        "schema_version": 1, "record_type": kind, "record_id": ident,
        "book_id": "BOOK_001", "status": "candidate", "qa_status": "HOLD",
        "origin_kind": "OBSERVED_SOURCE", "source_snapshot_ref": "source-manifest.json",
        "source_evidence_refs": refs, "source_component_refs": [], "evidence_gaps": [],
        "confidence": "MEDIUM",
        "semantic_review": {"status": "PENDING_REVIEW", "reviewer": "", "notes": ""},
    }


def build_fixture(root: Path) -> tuple[Path, dict[str, list[dict]], dict]:
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Validator Test"], cwd=root, check=True)
    base = root / "books" / "BOOK_001"
    emotion = base / "01_章节情绪"
    chapters = []
    for chapter in range(1, 11):
        opened = ["P001:武者身份登记"] if chapter == 1 else [f"P{chapter:03}:promise-{chapter}"]
        chapters.append({
            "schema_version": 1, "record_id": f"BOOK_001:EMOTION:{chapter:04}",
            "book_id": "BOOK_001", "chapter": chapter,
            "chapter_ref": f"BOOK_001:CHAPTER:{chapter:04}",
            "qa_status": "PASS", "source_fingerprint": "UNAVAILABLE",
            "promise_opened": opened, "promise_paid": [],
            "emotion_object": f"object-{chapter}", "pressure_source": f"pressure-{chapter}",
            "turning_point": f"turn-{chapter}", "visible_payoff_evidence": [f"visible-{chapter}"],
            "aftermath": f"aftermath-{chapter}",
        })
    ledger = [
        {"record_id": "BOOK_001:PROMISE:001", "book_id": "BOOK_001", "promise": "玉碟成长循环", "evidence_refs": ["BOOK_001:CHAPTER:0002"]},
        {"record_id": "BOOK_001:PROMISE:002", "book_id": "BOOK_001", "promise": "家庭安全", "evidence_refs": ["BOOK_001:CHAPTER:0001", "BOOK_001:CHAPTER:0004"]},
    ]
    qa = [{"record_id": "EMOTION:QA:BOOK_001", "book_id": "BOOK_001", "qa_status": "PASS"}]
    cf = [{"record_id": "CF:BOOK:BOOK_001", "book_id": "BOOK_001", "relation_id": "REL1"}]
    pl = [{"record_id": "PL:BOOK:BOOK_001", "book_id": "BOOK_001", "line_id": "L1"}]
    arc = [{"record_id": "AR:BOOK:BOOK_001", "book_id": "BOOK_001", "arc_id": "AR:ARC:1"}]
    source_specs = [
        (emotion / "chapter_emotion.jsonl", chapters, "chapter_emotion"),
        (emotion / "promise_ledger.jsonl", ledger, "promise_ledger"),
        (emotion / "qa" / "qa.jsonl", qa, "chapter_emotion_qa"),
        (base / "05_人物功能" / "per_book" / "BOOK_001.jsonl", cf, "character_function"),
        (base / "06_剧情线" / "per_book" / "BOOK_001.jsonl", pl, "plotline"),
        (base / "08_篇章结构" / "per_book" / "BOOK_001.jsonl", arc, "arc_structure"),
    ]
    for path, rows, _ in source_specs:
        write_jsonl(path, rows)
    subprocess.run(["git", "add", "books"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m", "source snapshot"], cwd=root, check=True, capture_output=True)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True).stdout.strip()
    manifest_files = []
    for path, _, role in source_specs:
        rel = path.relative_to(root).as_posix()
        blob = subprocess.run(
            ["git", "show", f"{commit}:{rel}"], cwd=root, check=True, capture_output=True
        ).stdout
        manifest_files.append({"path": rel, "role": role, "sha256_or_unavailable": hashlib.sha256(blob).hexdigest()})

    pilot = root / "research" / "emotion-arc-v2" / "pilot-book001"
    pilot.mkdir(parents=True)
    manifest = {
        "schema_version": 1, "book_id": "BOOK_001", "chapter_range": {"start": 1, "end": 10},
        "source_repo": "fixture/repo", "source_commit_sha": commit, "files": manifest_files,
        "coverage": {"chapters_expected": 10, "chapters_present": 10, "chapters_qa_pass": 10,
                     "canonical_source_fingerprint_status": "UNAVAILABLE_IN_SCOPE",
                     "source_text_verification_status": "SOURCE_TEXT_VERIFICATION_PARTIAL"},
        "known_gaps": ["chapter fingerprints unavailable"],
    }
    (pilot / "source-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    line1 = envelope("emotion_line", "EL:BOOK_001:001", ["BOOK_001:CHAPTER:0001", "BOOK_001:CHAPTER:0004"])
    line1.update({
        "reader_expectation": "家庭风险得到可见改善", "emotion_target": "family",
        "causal_generator": "资源不足迫使行动", "start_chapter": 1, "end_chapter_observed": 10,
        "lifecycle_status": "ACTIVE",
        "beats": [
            {"beat_id": "EL:BOOK_001:001:B01", "chapter_ref": "BOOK_001:CHAPTER:0001", "function": "OPEN",
             "reader_expectation_change": "expectation opens", "character_agency": "chooses work",
             "state_change": "risk becomes actionable", "evidence_refs": ["BOOK_001:CHAPTER:0001"]},
            {"beat_id": "EL:BOOK_001:001:B02", "chapter_ref": "BOOK_001:CHAPTER:0004", "function": "PARTIAL_PAYOFF",
             "reader_expectation_change": "some safety", "character_agency": "completes task",
             "state_change": "resources improve", "evidence_refs": ["BOOK_001:CHAPTER:0004"]},
        ],
        "payoff_contract": {"expected_observable_result": "safety", "observed_result": "partial", "state": "PARTIAL_PAID"},
        "related_plotline_refs": ["L1"], "related_component_refs": [],
        "promise_resolution_refs": ["PR:BOOK_001:001"], "unresolved_expectations": ["long-term safety"],
    })
    line2 = envelope("emotion_line", "EL:BOOK_001:002", ["BOOK_001:CHAPTER:0004", "BOOK_001:CHAPTER:0008"])
    line2.update({
        "reader_expectation": "取得合法行动资格", "emotion_target": "institution",
        "causal_generator": "permission gates access", "start_chapter": 4, "end_chapter_observed": 10,
        "lifecycle_status": "ACTIVE",
        "beats": [
            {"beat_id": "EL:BOOK_001:002:B01", "chapter_ref": "BOOK_001:CHAPTER:0004", "function": "OPEN",
             "reader_expectation_change": "entry opens", "character_agency": "accepts constraint",
             "state_change": "temporary access", "evidence_refs": ["BOOK_001:CHAPTER:0004"]},
            {"beat_id": "EL:BOOK_001:002:B02", "chapter_ref": "BOOK_001:CHAPTER:0008", "function": "PRESSURIZE",
             "reader_expectation_change": "obligation grows", "character_agency": "reports result",
             "state_change": "scrutiny increases", "evidence_refs": ["BOOK_001:CHAPTER:0008"]},
        ],
        "payoff_contract": {"expected_observable_result": "recognized access", "observed_result": "partial", "state": "PARTIAL_PAID"},
        "related_plotline_refs": ["L1"], "related_component_refs": [],
        "promise_resolution_refs": [], "unresolved_expectations": ["formal status"],
    })
    weave = envelope("emotion_weave", "EW:BOOK_001:001", ["BOOK_001:CHAPTER:0004"])
    weave.update({
        "member_line_ids": ["EL:BOOK_001:001", "EL:BOOK_001:002"], "weave_type": "CAUSES_PRESSURE",
        "direction": {"from_line_id": "EL:BOOK_001:001", "to_line_id": "EL:BOOK_001:002"},
        "event_chapter_ref": "BOOK_001:CHAPTER:0004", "trigger_event": "family need forces permission route",
        "before_after": {"before": "no route", "after": "accepts constrained access"},
        "causal_explanation": "resource need creates institutional pressure", "noncausal_note": "",
        "causal_evidence": {"from_state_change": "resource need becomes urgent", "to_pressure_or_choice": "must accept access rules", "bridge_observation": "same decision changes both states"},
    })
    macro1 = envelope("macro_emotion_arc", "MA:BOOK_001:001", ["BOOK_001:CHAPTER:0001", "BOOK_001:CHAPTER:0004"])
    macro1.update({
        "reader_macro_promise": "turn ability into protection and standing", "macro_question": "can both be achieved",
        "start_trigger_chapter_ref": "BOOK_001:CHAPTER:0001", "observed_window": {"start": 1, "end": 7},
        "member_line_ids": ["EL:BOOK_001:001", "EL:BOOK_001:002"], "related_story_arc_refs": ["AR:ARC:1"],
        "related_plotline_refs": ["L1"], "progression_summary": "need drives constrained entry and partial protection",
        "payoff_contract": {"criterion": "visible protection and standing", "observed_evidence_refs": ["BOOK_001:CHAPTER:0004"], "status": "PARTIAL_OBSERVED"},
        "irreversible_state_change": "temporary access exists", "current_status": "PARTIALLY_PAID",
        "next_macro_candidates": ["MA:BOOK_001:002"],
    })
    macro2 = envelope("macro_emotion_arc", "MA:BOOK_001:002", ["BOOK_001:CHAPTER:0008"])
    macro2.update({
        "reader_macro_promise": "new obligations reveal a larger problem", "macro_question": "what does access now require",
        "start_trigger_chapter_ref": "BOOK_001:CHAPTER:0008", "observed_window": {"start": 8, "end": 10},
        "member_line_ids": ["EL:BOOK_001:002"], "related_story_arc_refs": ["AR:ARC:1"],
        "related_plotline_refs": ["L1"], "progression_summary": "scrutiny and obligations open a new expectation",
        "payoff_contract": {"criterion": "new obligation resolved", "observed_evidence_refs": [], "status": "NOT_YET_OBSERVED"},
        "irreversible_state_change": "UNKNOWN", "current_status": "ACTIVE", "next_macro_candidates": [],
    })
    handoff = envelope("arc_handoff", "AH:BOOK_001:001", ["BOOK_001:CHAPTER:0008"])
    handoff.update({
        "from_macro_id": "MA:BOOK_001:001", "to_macro_id": "MA:BOOK_001:002",
        "handoff_trigger_chapter_ref": "BOOK_001:CHAPTER:0008", "bridge_type": "STATE_CHANGE_OPENS_NEW_PROMISE",
        "causal_bridge": "access creates new obligations", "reader_expectation_at_handoff": "reader awaits consequence",
        "old_arc_status_at_entry": "PARTIALLY_PAID", "new_arc_status_at_entry": "ACTIVE",
        "prior_arc_payoff_check": {"criterion": "visible protection", "observed_result": "partial only", "status": "PENDING"},
        "has_observed_overlap": False, "handoff_conclusion": "CANDIDATE_UNVERIFIED",
        "handoff_evidence": {"prior_state_change": "temporary access", "new_promise_trigger": "new scrutiny",
                             "distinct_constraint": "obligation rather than entry"},
    })
    crosswalk = [{
        "resolution_id": "PR:BOOK_001:001",
        "chapter_promise_locator": {"chapter_ref": "BOOK_001:CHAPTER:0001", "source_field": "promise_opened", "array_index": 0, "raw_value": "P001:武者身份登记"},
        "candidate_ledger_record_ids": ["BOOK_001:PROMISE:002"], "resolution_status": "PARTIAL_RELATION",
        "evidence_summary": "registration pressure relates to safety but is not ledger 001",
        "linked_emotion_line_ids": ["EL:BOOK_001:001"], "source_evidence_refs": ["BOOK_001:CHAPTER:0001"],
    }]
    payload = {
        "emotion-lines.jsonl": [line1, line2], "emotion-weaves.jsonl": [weave],
        "macro-emotion-arcs.jsonl": [macro1, macro2], "arc-handoffs.jsonl": [handoff],
        "promise-resolution.jsonl": crosswalk,
    }
    for name, rows in payload.items():
        write_jsonl(pilot / name, rows)
    return pilot, payload, manifest


def materialize(pilot: Path, payload: dict[str, list[dict]], manifest: dict) -> None:
    (pilot / "source-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    for name, rows in payload.items():
        write_jsonl(pilot / name, rows)


def has_code(report: dict, code: str) -> bool:
    return any(item.get("code") == code for item in report.get("errors", []))


def enable_claim_evidence_v2(payload: dict[str, list[dict]], manifest: dict) -> None:
    manifest["research_contract_profile"] = "CLAIM_EVIDENCE_V2"
    manifest["evidence_policy"] = {
        "top_level_source_evidence_refs": "REPRESENTATIVE_SUMMARY",
        "full_evidence_views": {
            "emotion_line": "beats[].evidence_refs",
            "emotion_weave": "evidence_bindings",
            "macro_emotion_arc": "evidence_bindings",
            "arc_handoff": "evidence_bindings",
            "promise_resolution": "source_evidence_refs",
        },
    }
    for rows in payload.values():
        for row in rows:
            if "record_type" in row:
                row["source_evidence_scope"] = "REPRESENTATIVE_SUMMARY"
                row.setdefault("evidence_bindings", [])
    weave = payload["emotion-weaves.jsonl"][0]
    weave["evidence_bindings"] = [
        {
            "claim": "chapter four contains the declared decision point",
            "chapter_ref": "BOOK_001:CHAPTER:0004",
            "source_record_id": "BOOK_001:EMOTION:0004",
            "field_path": "turning_point",
            "interpretation": "the source field is relevant; causal semantics remain pending review",
        }
    ]
    macro1, macro2 = payload["macro-emotion-arcs.jsonl"]
    macro1["evidence_bindings"] = [
        {
            "claim": "the first macro has an observed partial result",
            "chapter_ref": "BOOK_001:CHAPTER:0004",
            "source_record_id": "BOOK_001:EMOTION:0004",
            "field_path": "visible_payoff_evidence[0]",
            "interpretation": "a visible result exists; macro sufficiency remains pending review",
        }
    ]
    macro1["macro_qualification"] = {
        "qualification_chapter_ref": "BOOK_001:CHAPTER:0004",
        "sustained_progression_evidence_refs": ["BOOK_001:CHAPTER:0001", "BOOK_001:CHAPTER:0004"],
        "organized_line_ids": ["EL:BOOK_001:001", "EL:BOOK_001:002"],
        "organization_explanation": "two distinct line contracts are organized across two observed beats",
    }
    payload["emotion-lines.jsonl"][0]["beats"].append({
        "beat_id": "EL:BOOK_001:001:B03", "chapter_ref": "BOOK_001:CHAPTER:0010",
        "function": "PRESSURIZE", "reader_expectation_change": "old contract remains active",
        "character_agency": "preserves the earlier obligation", "state_change": "the line overlaps the new window",
        "evidence_refs": ["BOOK_001:CHAPTER:0010"],
    })
    macro2["member_line_ids"] = ["EL:BOOK_001:001", "EL:BOOK_001:002"]
    macro2["evidence_bindings"] = [
        {
            "claim": "the second macro candidate continues beyond a single label",
            "chapter_ref": "BOOK_001:CHAPTER:0008",
            "source_record_id": "BOOK_001:EMOTION:0008",
            "field_path": "pressure_source",
            "interpretation": "pressure is observable; organizing capacity remains pending review",
        }
    ]
    macro2["macro_qualification"] = {
        "qualification_chapter_ref": "BOOK_001:CHAPTER:0010",
        "sustained_progression_evidence_refs": ["BOOK_001:CHAPTER:0008", "BOOK_001:CHAPTER:0010"],
        "organized_line_ids": ["EL:BOOK_001:001", "EL:BOOK_001:002"],
        "organization_explanation": "the candidate claims to organize two lines across two chapters",
    }
    handoff = payload["arc-handoffs.jsonl"][0]
    handoff["evidence_bindings"] = [
        {
            "claim": "a new promise trigger exists at the declared handoff",
            "chapter_ref": "BOOK_001:CHAPTER:0008",
            "source_record_id": "BOOK_001:EMOTION:0008",
            "field_path": "promise_opened[0]",
            "interpretation": "the promise exists; handoff quality remains pending review",
        }
    ]


def main() -> int:
    failures: list[dict] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        pilot, base_payload, base_manifest = build_fixture(root)

        def run(name: str, mutate, expected_ok: bool, expected_code: str | None = None, check=None) -> None:
            payload, manifest = copy.deepcopy(base_payload), copy.deepcopy(base_manifest)
            mutate(payload, manifest)
            materialize(pilot, payload, manifest)
            report = validate_pilot(pilot, root)
            good = report.get("ok") == expected_ok
            if expected_code is not None:
                good = good and has_code(report, expected_code)
            if check is not None:
                good = good and bool(check(report))
            if not good:
                failures.append({"case": name, "report": report})

        run("T01 valid structure semantic pending", lambda p, m: None, True, check=lambda r: r["structural_gate"] == "PASS" and r["semantic_review"] == "PENDING_INDEPENDENT_REVIEW")
        run("T02 duplicate ID", lambda p, m: p["emotion-lines.jsonl"].append(copy.deepcopy(p["emotion-lines.jsonl"][0])), False, "DUPLICATE_ID")
        def same_label_distinct(p, _):
            p["emotion-lines.jsonl"][1]["emotion_target"] = p["emotion-lines.jsonl"][0]["emotion_target"]
            p["emotion-lines.jsonl"][1]["reader_expectation"] = "different observable institutional payoff"
        run("T03 same label does not merge", same_label_distinct, True)
        def bad_p001(p, _):
            row = p["promise-resolution.jsonl"][0]
            row["candidate_ledger_record_ids"] = ["BOOK_001:PROMISE:001"]
            row["resolution_status"] = "EXACT_SEMANTIC_MATCH"
        run("T04 unsupported P001 identity", bad_p001, False, "UNSUPPORTED_PROMISE_IDENTITY")
        def unresolved(p, _):
            row = p["promise-resolution.jsonl"][0]
            row["candidate_ledger_record_ids"] = []
            row["resolution_status"] = "UNRESOLVED"
        run("T05 honest unresolved", unresolved, True, check=lambda r: r["crosswalk_gate"] == "HOLD")
        run("T06 invalid weave members", lambda p, m: p["emotion-weaves.jsonl"][0].update(member_line_ids=["EL:BOOK_001:001"]), False, "INVALID_MEMBERS")
        run("T07 causal co-occurrence unsupported", lambda p, m: p["emotion-weaves.jsonl"][0].pop("causal_evidence"), False, "CAUSAL_LINK_UNSUPPORTED")
        run("T08 shared event missing", lambda p, m: p["emotion-weaves.jsonl"][0].update(weave_type="SHARED_EVENT", direction=None, noncausal_note="co-occurrence only", event_chapter_ref="BOOK_001:CHAPTER:9999"), False, "MISSING_EVENT_REF")
        def paid_without_evidence(p, _):
            macro = p["macro-emotion-arcs.jsonl"][1]
            macro["current_status"] = "PAID"
            macro["payoff_contract"]["status"] = "OBSERVED_PAID"
        run("T09 paid macro without evidence", paid_without_evidence, False, "MISSING_PAYOFF_EVIDENCE")
        def child_paid_macro_open(p, _):
            p["emotion-lines.jsonl"][0]["lifecycle_status"] = "PAID"
            p["emotion-lines.jsonl"][0]["payoff_contract"]["state"] = "PAID"
        run("T10 paid child does not close macro", child_paid_macro_open, True)
        def false_overlap(p, _):
            first = p["macro-emotion-arcs.jsonl"][0]
            first["current_status"] = "PAID"
            first["payoff_contract"] = {"criterion": "done", "observed_evidence_refs": ["BOOK_001:CHAPTER:0004"], "status": "OBSERVED_PAID"}
            h = p["arc-handoffs.jsonl"][0]
            h["has_observed_overlap"] = True
            h["handoff_conclusion"] = "OBSERVED_OVERLAP"
        run("T11 false overlap", false_overlap, False, "HANDOFF_TEMPORAL_CONFLICT")
        run("T12 empty handoff semantics", lambda p, m: p["arc-handoffs.jsonl"][0].pop("handoff_evidence"), False, "HANDOFF_REQUIRED_FIELDS")
        run("T13 prior payoff pending is HOLD", lambda p, m: None, True, check=lambda r: r["macro_handoff_gate"] == "HOLD" and any(w["code"] == "PRIOR_ARC_PAYOFF_PENDING" for w in r["warnings"]))
        run("T14 active promotion forbidden", lambda p, m: p["emotion-lines.jsonl"][0].update(status="active"), False, "STATUS_PROMOTION_FORBIDDEN")
        run("T15 out-of-scope chapter", lambda p, m: p["emotion-lines.jsonl"][0]["beats"][1].update(chapter_ref="BOOK_001:CHAPTER:0011", evidence_refs=["BOOK_001:CHAPTER:0011"]), False, "OUT_OF_SCOPE_REF")
        run("T16 origin layer conflict", lambda p, m: p["emotion-lines.jsonl"][0].update(origin_kind="HYPOTHETICAL_DESIGN"), False, "ORIGIN_LAYER_CONFLICT")
        run("T17 provenance overclaim", lambda p, m: m["coverage"].update(source_text_verification_status="SOURCE_TEXT_VERIFIED_FULL"), False, "PROVENANCE_OVERCLAIM")

        def fake_causal_interpretation(p, m):
            enable_claim_evidence_v2(p, m)
            p["emotion-weaves.jsonl"][0]["causal_explanation"] = "a fabricated causal reading with a real chapter reference"
        run(
            "T18 real reference with false causal interpretation needs semantic review",
            fake_causal_interpretation, True,
            check=lambda r: r["claim_binding_gate"] == "PASS"
            and r["weave_causality_evidence_gate"] == "NEEDS_SEMANTIC_REVIEW"
            and r["semantic_review"] == "PENDING_INDEPENDENT_REVIEW",
        )

        def cooccurrence_claimed_causal(p, m):
            enable_claim_evidence_v2(p, m)
            p["emotion-weaves.jsonl"][0]["causal_evidence"] = {
                "from_state_change": "event A is present",
                "to_pressure_or_choice": "event B is present",
                "bridge_observation": "the same chapter mentions both",
            }
        run(
            "T19 co-occurrence declared causal needs semantic review",
            cooccurrence_claimed_causal, True,
            check=lambda r: r["weave_causality_evidence_gate"] == "NEEDS_SEMANTIC_REVIEW",
        )

        def line_start_not_macro(p, m):
            enable_claim_evidence_v2(p, m)
            p["macro-emotion-arcs.jsonl"][1]["macro_qualification"]["organized_line_ids"] = ["EL:BOOK_001:002"]
            p["macro-emotion-arcs.jsonl"][1]["macro_qualification"]["sustained_progression_evidence_refs"] = ["BOOK_001:CHAPTER:0008"]
        run("T20 new line start is not macro capacity", line_start_not_macro, False, "MACRO_ORGANIZATION_UNPROVEN")

        def cancel_old_contract(p, m):
            enable_claim_evidence_v2(p, m)
            p["arc-handoffs.jsonl"][0]["prior_arc_payoff_check"]["status"] = "CANCELLED"
            p["arc-handoffs.jsonl"][0]["prior_arc_payoff_check"]["observed_result"] = "new line replaces old promise"
        run("T21 new line cannot cancel old payoff", cancel_old_contract, False, "PRIOR_PAYOFF_CONTRACT_CANCELLED")

    print(json.dumps({"ok": not failures, "cases": 21, "passed": 21 - len(failures), "failures": failures}, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
