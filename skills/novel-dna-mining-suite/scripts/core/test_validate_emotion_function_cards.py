#!/usr/bin/env python3
"""EMOF minimal integration regressions. No external dependencies."""
from __future__ import annotations
import copy
import json
import tempfile
from pathlib import Path
from validate_emotion_function_cards import validate


def setup(root: Path) -> dict:
    base = root / "books" / "BOOK_005" / "01_章节情绪"
    base.mkdir(parents=True)
    chapters = [
        {"book_id": "BOOK_005", "chapter": i, "chapter_ref": f"BOOK_005:CHAPTER:{i:04}",
         "qa_status": "PASS", "source_fingerprint": "UNAVAILABLE" if i == 21 else "1"*64}
        for i in range(21, 26)
    ]
    (base / "chapter_emotion.jsonl").write_text(
        "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in chapters), encoding="utf-8"
    )
    (base / "promise_ledger.jsonl").write_text(
        json.dumps({
            "record_id": "BOOK_005:PROMISE:001",
            "book_id": "BOOK_005", "evidence_refs": [
                "BOOK_005:CHAPTER:0021", "BOOK_005:CHAPTER:0024"
            ],
        }, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return {
        "schema_version": 1, "record_type": "emotion_function_card",
        "record_id": "EMOF:BOOK_005:0021-0025:01", "status": "candidate",
        "source_book_id": "BOOK_005", "chapter_span": {"start": 21, "end": 25},
        "source_chapter_refs": [x["chapter_ref"] for x in chapters],
        "source_evidence_refs": ["BOOK_005:CHAPTER:0021", "BOOK_005:CHAPTER:0024"],
        "source_promise_refs": ["BOOK_005:PROMISE:001"],
        "source_facts": {
            "initiating_event": "An incident occurred", "pressure_event": "More risk",
            "decisive_actions": ["A character made a choice"], "observed_result": "An outcome occurred"
        },
        "emotional_function": {
            "reader_expectation": "Prevent harm to an important person",
            "emotion_trajectory": ["worry", "intensifying pressure", "relief"],
            "trigger_function": "Important person threatened",
            "pressure_logic": "First attempts are insufficient",
            "agency_function": "A key character makes a costly decision",
            "payoff_function": "Threat is visibly removed",
            "aftermath_function": "The relationship and information state change",
            "invariants": ["The threatened person is known to matter"],
            "replacement_slots": [
                {"slot": "threat_actor", "observed": "creature", "replacement_rule": "credible threat"},
                {"slot": "location", "observed": "school", "replacement_rule": "accessible but restrictive setting"}
            ],
            "limitations": ["No payoff if the threat was never established"]
        },
        "evidence_gaps": [],
        "semantic_review": {"status": "PENDING_REVIEW", "reviewer": "", "notes": ""},
        "qa_status": "HOLD"
    }


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        base = setup(root)
        cases = [("valid unreviewed draft", base, True)]
        def bad(name: str, fn):
            row = copy.deepcopy(base)
            fn(row)
            cases.append((name, row, False))
        bad("forged one evidence ref", lambda c: c["source_evidence_refs"].append("BOOK_005:CHAPTER:0099"))
        bad("out of window chapter", lambda c: c["source_chapter_refs"].append("BOOK_005:CHAPTER:0026"))
        bad("unverifiable promise", lambda c: c["source_promise_refs"].append("BOOK_005:PROMISE:FAKE"))
        bad("wrong evidence key", lambda c: c["source_evidence_refs"].append("BOOK_005:CHAPTER:0023"))
        # This is valid because chapter 23 is in source_chapter_refs and canonical.
        cases[-1] = ("valid additional canonical evidence", cases[-1][1], True)
        bad("fabricated PASS without semantic review", lambda c: c.update(qa_status="PASS"))
        bad("no actor agency", lambda c: c["emotional_function"].update(agency_function=""))
        bad("only one replacement slot", lambda c: c["emotional_function"].update(
            replacement_slots=c["emotional_function"]["replacement_slots"][:1]))
        bad("wrong card book identity", lambda c: c.update(source_book_id="BOOK_008"))
        bad("duplicate record", lambda c: c.update(source_evidence_refs=[
            "BOOK_005:CHAPTER:0021", "BOOK_005:CHAPTER:0021"]))
        failures = []
        for name, card, expected in cases:
            report = validate(root, [card])
            if report["ok"] != expected:
                failures.append({"case": name, "actual": report["ok"], "errors": report["errors"]})
            if name == "valid unreviewed draft" and (
                report["source_trust"] != "PARTIAL"
                or report["current_compatibility"] != "NOT_APPLICABLE"
                or report["semantic_approval"] != "NOT_GRANTED_BY_MACHINE"
            ):
                failures.append({"case": "honest source/semantic statuses", "report": report})
        report = validate(root, [base, base])
        if report["ok"] or not any("duplicate record_id" in x for x in report["errors"]):
            failures.append({"case": "cross-row duplicate not detected", "report": report})
        print(json.dumps({"ok": not failures, "cases": len(cases)+1, "failures": failures},
                         ensure_ascii=False, indent=2))
        return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
