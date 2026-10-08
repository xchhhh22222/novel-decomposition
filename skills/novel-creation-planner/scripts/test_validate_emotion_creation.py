#!/usr/bin/env python3
"""Regression tests: real source closure, three QA axes, emotion causality."""
from __future__ import annotations

import copy
import hashlib
import json
import tempfile
from pathlib import Path

from validate_emotion_creation import validate_draft


def fixture(root: Path) -> dict:
    package = root / "shared-v1"
    package.mkdir()
    specs = [
        ("worldbuilding", "03_世界观", "WB:BOOK:BOOK_A", "BOOK_A", "task", "money"),
        ("golden_finger", "02_金手指", "GF:BOOK:BOOK_B", "BOOK_B", "money", "growth"),
        ("cultivation_system", "04_修炼体系", "CS:BOOK:BOOK_C", "BOOK_C", "growth", "rank"),
    ]
    paths = {}
    hashes = {}
    mats = []
    for module, dirname, rid, book, inp, out in specs:
        rel = f"DNA素材/{dirname}/per_book/{book}.jsonl"
        path = package / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        row = {"record_id": rid, "book_id": book, "record_type": "per_book",
               "status": "candidate", "qa_status": "PASS",
               "evidence_refs": [f"{book}:CHAPTER:0001"], "unknowns": []}
        path.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
        paths[rid] = rel
        hashes[rid] = hashlib.sha256(path.read_bytes()).hexdigest()
        mats.append({
            "material_id": rid,
            "source": {"source_path": rel, "record_id": rid, "book_id": book,
                       "module": module, "evidence_refs": [f"{book}:CHAPTER:0001"],
                       "source_qa_status": "PASS"},
            "interface": {"inputs": [inp], "outputs": [out],
                          "dependencies": [], "constraints": [], "unknowns": []},
            "interface_readiness": "READY",
            "interface_reason": "Full causal interface evidenced in source",
        })
    (package / "manifest.json").write_text(json.dumps({
        "package_id": "nova-shared-dna-library",
        "status": "ACTIVE_SHARED_LIBRARY", "active": True,
        "artifact_paths": paths, "artifact_sha256": hashes,
    }, ensure_ascii=False), encoding="utf-8")
    ids = [x["material_id"] for x in mats]
    pattern = {"pattern_id": "EMO:01", "source_kind": "ORIGINAL_DESIGN",
               "reader_promise": "Earn contested qualification through action",
               "beats": [
                   {"reader_emotion": e, "expectation": "public validation", "causal_event": ev,
                    "character_agency": "active choice", "state_change": "new relevant state",
                    **({"depends_on_prior": "previous choice has consequences"} if n else {})}
                   for n, (e, ev) in enumerate([("pressure", "denied entry"),
                                                 ("hope", "tries a legitimate route"),
                                                 ("payoff", "earns new access")])
               ], "visible_payoff": "access changes", "aftermath": "new obligations"}
    return {
        "schema_version": 1, "design_mode": "EMOTION_FIRST", "status": "DRAFT",
        "shared_library_root": str(package), "emotion_patterns": [pattern],
        "materials": mats,
        "options": [{
            "option_id": "A", "status": "READY_FOR_HUMAN_REVIEW",
            "emotion_pattern_ids": ["EMO:01"], "deliverables": ["growth_loop"],
            "slots": [{"slot_id": f"SLOT:{m['source']['module']}", "module": m["source"]["module"],
                       "material_ids": [m["material_id"]], "gap": None} for m in mats],
            "compatibility_checks": [
                {"from_material_id": ids[0], "to_material_id": ids[1],
                 "source_output": "money", "target_input": "money",
                 "result": "DIRECT_FIT", "reason": "exact resource type"},
                {"from_material_id": ids[1], "to_material_id": ids[2],
                 "source_output": "growth", "target_input": "growth",
                 "result": "DIRECT_FIT", "reason": "matching growth asset"},
            ]
        }],
    }


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        base = fixture(Path(tmp))
        cases = [("valid closure", base, True)]
        def add(name: str, mutate, should_pass=False):
            value = copy.deepcopy(base)
            mutate(value)
            cases.append((name, value, should_pass))
        add("source path not declared", lambda d: d["materials"][0]["source"].update(source_path="DNA素材/03_世界观/per_book/FORGED.jsonl"))
        add("fake record id", lambda d: d["materials"][0]["source"].update(record_id="WB:FAKE"))
        add("false qa pass", lambda d: d["materials"][0]["source"].update(source_qa_status="HOLD"))
        add("missing growth module", lambda d: d["options"][0]["slots"].pop(0))
        add("missing first3 opening module", lambda d: d["options"][0]["deliverables"].append("opening"))
        add("missing plotline module", lambda d: d["options"][0]["deliverables"].append("story_spine"))
        add("missing emotion causality", lambda d: d["emotion_patterns"][0]["beats"][1].pop("depends_on_prior"))
        add("bad emotional source promotion", lambda d: d["emotion_patterns"][0].update(source_kind="RESEARCH_VERIFIED", source_publication_status="ACTIVE_SHARED_LIBRARY", source_evidence_refs=["BOOK_A:CHAPTER:0001"], research_evidence_check="VERIFIED"))
        add("false direct fit", lambda d: d["options"][0]["compatibility_checks"][0].update(target_input="growth"))
        add("unsupported crossbook bridge", lambda d: d["options"][0]["compatibility_checks"][0].update(result="ADAPTABLE"))
        def bridge(d):
            d["options"][0]["compatibility_checks"][0].update(result="ADAPTABLE",bridge={
                "new_rule": "task claims can settle to money", "cost_or_constraint": "tax charge",
                "changed_state": "money balance", "why_causal": "world institution allows conversion",
                "provenance": "ORIGINAL_DESIGN"})
        add("grounded adaptation", bridge, True)
        def research_case(d):
            research = Path(tmp) / "research-artifacts"
            rel = "books/BOOK_A/01_章节情绪/chapter_emotion.jsonl"
            path = research / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            rows = [
                {"chapter_ref": f"BOOK_A:CHAPTER:{i:04}", "qa_status": "PASS"}
                for i in (1, 2, 3)
            ]
            path.write_text("\n".join(json.dumps(x) for x in rows) + "\n", encoding="utf-8")
            d["research_root"] = str(research)
            d["emotion_patterns"][0].update(
                source_kind="RESEARCH_VERIFIED",
                source_publication_status="RESEARCH_NOT_ACTIVE",
                research_source_path=rel,
                research_file_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                source_evidence_refs=[x["chapter_ref"] for x in rows],
            )
        add("real research evidence closure", research_case, True)
        def research_false_hash(d):
            research_case(d)
            d["emotion_patterns"][0]["research_file_sha256"] = "0"*64
        add("research file hash mismatch", research_false_hash)
        def research_fake_ref(d):
            research_case(d)
            d["emotion_patterns"][0]["source_evidence_refs"].append("BOOK_A:CHAPTER:9999")
        add("fake research emotion evidence", research_fake_ref)
        add("non-ready interface", lambda d: d["materials"][1].update(interface_readiness="PARTIAL"))
        add("unexplained gap", lambda d: d["options"][0]["slots"][0].update(material_ids=[],gap={"type":"CREATIVE_OPEN_CHOICE","reason":"original","next_action":"design"}))
        failures = []
        for name, data, expected in cases:
            result = validate_draft(data)
            if result["ok"] != expected:
                failures.append({"name": name, "expected": expected, "errors": result["errors"]})
        print(json.dumps({"cases": len(cases), "passed": len(cases)-len(failures),
                          "failures": failures}, ensure_ascii=False, indent=2))
        return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
