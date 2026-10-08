#!/usr/bin/env python3
"""Validate EMOF draft records against existing 01 canonical + promise ledger.

Exit 0 means machine structure and exact references pass; it does not grant
semantic review, cross-book family membership, publication, or creation approval.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ID = re.compile(r"^EMOF:(BOOK_\d{3}):(\d{4})-(\d{4}):(\d{2})$")
CHAPTER = re.compile(r"^(BOOK_\d{3}):CHAPTER:(\d{4})$")
GATES = {"PASS", "PARTIAL", "HOLD", "FAIL"}
REVIEW = {"PENDING_REVIEW", "PASS", "HOLD", "FAIL"}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    for line_num, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except ValueError as exc:
            raise ValueError(f"{path}:{line_num}: invalid JSON: {exc}") from exc
        if not isinstance(record, dict):
            raise ValueError(f"{path}:{line_num}: JSONL line must be an object")
        records.append(record)
    return records


def required_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(root: Path, cards: list[dict[str, Any]]) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    seen: set[str] = set()
    fingerprints_missing: set[str] = set()
    books: dict[str, tuple[dict[str, dict], dict[str, dict]]] = {}
    for i, card in enumerate(cards):
        loc = f"cards[{i}]"
        ident = card.get("record_id")
        match = ID.fullmatch(str(ident))
        if not match:
            errors.append(f"{loc}: canonical record_id EMOF:BOOK_NNN:xxxx-yyyy:nn required")
            continue
        book, start_txt, end_txt, _ = match.groups()
        start, end = int(start_txt), int(end_txt)
        if ident in seen:
            errors.append(f"{loc}: duplicate record_id={ident}")
        seen.add(ident)
        if (start < 1 or end < start or card.get("source_book_id") != book
                or card.get("chapter_span") != {"start": start, "end": end}):
            errors.append(f"{loc}: book/chapter_span not consistent with record_id")
        if (card.get("schema_version") != 1
                or card.get("record_type") != "emotion_function_card"
                or card.get("status") != "candidate"):
            errors.append(f"{loc}: requires schema_version=1, emotion_function_card, candidate")
        if card.get("qa_status") not in GATES:
            errors.append(f"{loc}: qa_status must be PASS/PARTIAL/HOLD/FAIL")

        if book not in books:
            base = root / "books" / book / "01_章节情绪"
            ch_path, pr_path = base / "chapter_emotion.jsonl", base / "promise_ledger.jsonl"
            try:
                chapter_rows = read_jsonl(ch_path)
                promise_rows = read_jsonl(pr_path)
                chapters = {}
                for r in chapter_rows:
                    key = r.get("chapter_ref")
                    if key in chapters:
                        errors.append(f"{book}: duplicate canonical chapter_ref {key}")
                    chapters[key] = r
                promises = {}
                for r in promise_rows:
                    key = r.get("record_id")
                    if key in promises:
                        errors.append(f"{book}: duplicate ledger id {key}")
                    promises[key] = r
                books[book] = (chapters, promises)
            except (OSError, ValueError) as exc:
                errors.append(f"{book}: source canonical/ledger unreadable: {exc}")
                books[book] = ({}, {})
        chapters, promises = books[book]

        chapter_refs = card.get("source_chapter_refs")
        evidence_refs = card.get("source_evidence_refs")
        if (not isinstance(chapter_refs, list) or not chapter_refs
                or len(chapter_refs) != len(set(map(str, chapter_refs)))):
            errors.append(f"{loc}: source_chapter_refs must be nonempty unique array")
            chapter_refs = []
        if (not isinstance(evidence_refs, list) or not evidence_refs
                or len(evidence_refs) != len(set(map(str, evidence_refs)))):
            errors.append(f"{loc}: source_evidence_refs must be nonempty unique array")
            evidence_refs = []
        for label, refs in (("source_chapter_refs", chapter_refs), ("source_evidence_refs", evidence_refs)):
            for ref in refs:
                m = CHAPTER.fullmatch(str(ref))
                if not m or m.group(1) != book or not start <= int(m.group(2)) <= end:
                    errors.append(f"{loc}.{label}: invalid or out-of-window ref {ref}")
                    continue
                row = chapters.get(ref)
                if row is None:
                    errors.append(f"{loc}.{label}: reference not found {ref}")
                elif row.get("qa_status") != "PASS":
                    errors.append(f"{loc}.{label}: canonical chapter not QA PASS: {ref}")
                elif row.get("source_fingerprint") == "UNAVAILABLE":
                    fingerprints_missing.add(str(ref))
        if not set(evidence_refs).issubset(set(chapter_refs)):
            errors.append(f"{loc}: all evidence_refs must belong to source_chapter_refs")

        promise_refs = card.get("source_promise_refs")
        if not isinstance(promise_refs, list) or any(not required_string(x) for x in promise_refs):
            errors.append(f"{loc}: source_promise_refs must be an array of ledger IDs")
            promise_refs = []
        elif len(promise_refs) != len(set(promise_refs)):
            errors.append(f"{loc}: duplicate promise refs")
        if not promise_refs and not card.get("evidence_gaps"):
            errors.append(f"{loc}: no promise linkage requires an explicit evidence_gaps explanation")
        for p in promise_refs:
            ledger = promises.get(p)
            if ledger is None or ledger.get("book_id") != book:
                errors.append(f"{loc}: nonexistent/mismatched ledger promise {p}")
            elif not set(evidence_refs).intersection(ledger.get("evidence_refs") or []):
                errors.append(f"{loc}: ledger {p} has no chapter evidence overlap with window")

        facts = card.get("source_facts")
        if not isinstance(facts, dict):
            errors.append(f"{loc}: source_facts must be object")
            facts = {}
        for key in ("initiating_event", "pressure_event", "observed_result"):
            if not required_string(facts.get(key)):
                errors.append(f"{loc}.source_facts: {key} required")
        if not isinstance(facts.get("decisive_actions"), list) or not all(
            required_string(x) for x in facts["decisive_actions"]
        ) or not facts["decisive_actions"]:
            errors.append(f"{loc}.source_facts: nonempty decisive_actions required")

        func = card.get("emotional_function")
        if not isinstance(func, dict):
            errors.append(f"{loc}: emotional_function must be object")
            func = {}
        for key in (
            "reader_expectation", "trigger_function", "pressure_logic",
            "agency_function", "payoff_function", "aftermath_function"
        ):
            if not required_string(func.get(key)):
                errors.append(f"{loc}.emotional_function: {key} required")
        trajectory = func.get("emotion_trajectory")
        if (not isinstance(trajectory, list) or len(trajectory) < 2
                or not all(required_string(x) for x in trajectory)):
            errors.append(f"{loc}: emotion_trajectory requires 2+ meaningful stages")
        invariants = func.get("invariants")
        if (not isinstance(invariants, list) or not invariants
                or not all(required_string(x) for x in invariants)):
            errors.append(f"{loc}: invariants require substantive conditions")
        slots = func.get("replacement_slots")
        if not isinstance(slots, list) or len(slots) < 2:
            errors.append(f"{loc}: at least two replaceable slots required")
            slots = []
        keys = set()
        for j, slot in enumerate(slots):
            if not isinstance(slot, dict) or any(
                not required_string(slot.get(k))
                for k in ("slot", "observed", "replacement_rule")
            ):
                errors.append(f"{loc}.replacement_slots[{j}]: incomplete")
                continue
            key = slot["slot"]
            if key in keys:
                errors.append(f"{loc}: duplicate replacement slot {key}")
            keys.add(key)
        limits = func.get("limitations")
        if not isinstance(limits, list) or not all(required_string(x) for x in limits):
            errors.append(f"{loc}: limitations must be array (empty allowed)")
        if not isinstance(card.get("evidence_gaps"), list):
            errors.append(f"{loc}: evidence_gaps must be array")
        review = card.get("semantic_review")
        if not isinstance(review, dict) or review.get("status") not in REVIEW:
            errors.append(f"{loc}: semantic_review status invalid")
            review = {}
        elif review.get("status") == "PASS" and (
            not required_string(review.get("reviewer"))
            or not required_string(review.get("notes"))
        ):
            errors.append(f"{loc}: semantic PASS requires named independent reviewer and notes")
        if card.get("qa_status") == "PASS" and review.get("status") != "PASS":
            errors.append(f"{loc}: QA PASS impossible without independent semantic review PASS")
    for ref in sorted(fingerprints_missing):
        warnings.append(f"{ref}: FINGERPRINT_UNAVAILABLE; chapter QA provenance is not a verified source text fingerprint")

    return {
        "ok": not errors,
        "machine_check": "STRUCTURAL_AND_CANONICAL_REFERENCE_ONLY",
        "source_trust": "FAIL" if errors else "PARTIAL" if fingerprints_missing else "TRACEABLE",
        "source_text_fingerprint": "PARTIAL" if fingerprints_missing else "NO_MISSING_FINGERPRINT_REPORTED",
        "interface_readiness": "FAIL" if errors else "STRUCTURE_READY_SEMANTICS_UNVERIFIED",
        "current_compatibility": "NOT_APPLICABLE",
        "creation_approval": "NOT_GRANTED",
        "semantic_approval": "NOT_GRANTED_BY_MACHINE",
        "cards_checked": len(cards),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate emotion-function derived cards (read-only).")
    parser.add_argument("cards", type=Path)
    parser.add_argument("--library-root", type=Path, required=True, help="Material-library working tree, not production-package root")
    args = parser.parse_args()
    try:
        if not args.library_root.is_dir():
            raise OSError(f"library root unavailable: {args.library_root}")
        report = validate(args.library_root, read_jsonl(args.cards))
    except (OSError, ValueError) as exc:
        report = {"ok": False, "errors": [str(exc)]}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
