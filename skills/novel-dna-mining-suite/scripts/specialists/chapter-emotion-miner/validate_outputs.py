#!/usr/bin/env python3
"""Validate canonical chapter-emotion records and derived emotion outputs.

The canonical chapter overlay is intentionally validated separately from the
derived-output envelope.  This prevents the adapter contract from silently
changing the authoritative chapter-emotion schema.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any


CANONICAL_REQUIRED = {
    "schema_version",
    "record_id",
    "status",
    "book_id",
    "chapter",
    "chapter_ref",
    "chapter_title",
    "evidence_path",
    "source_fingerprint",
    "chapter_role",
    "main_reader_emotion",
    "secondary_reader_emotions",
    "emotion_object",
    "expectation_source",
    "pressure_source",
    "pressure_level",
    "turning_point",
    "payoff_level",
    "visible_payoff_evidence",
    "aftermath",
    "ending_aftertaste",
    "hook_type",
    "promise_opened",
    "promise_paid",
    "plot_lines_advanced",
    "qa_status",
    "confidence",
    "generated_at",
}
CANONICAL_ENVELOPE_FIELDS = {"record_type", "book_ids", "evidence_refs", "unknowns"}
ROLES = {"立承诺", "蓄压", "加压", "转机", "兑现", "余震", "过渡", "换档"}
PAYOFF_LEVELS = {"无兑现-继续蓄压", "局部兑现", "阶段小兑现", "本章强兑现", "兑现后余震"}
STRONG_PAYOFFS = {"阶段小兑现", "本章强兑现", "兑现后余震"}
CONFIDENCE = {"HIGH", "MEDIUM", "LOW"}
QA_STATUS = {"PASS", "HOLD", "FAIL"}
DERIVED_TYPES = {"per_book", "nearest_neighbor", "cluster", "qa", "handoff", "gap"}
DERIVED_REQUIRED = {
    "record_type",
    "schema_version",
    "record_id",
    "status",
    "evidence_refs",
    "unknowns",
    "confidence",
    "qa_status",
}
CHAPTER_HEADING_RE = re.compile(r"^# 第([0-9]+)章：(.+)$", re.MULTILINE)
FINGERPRINT_RE = re.compile(r"^[0-9a-f]{64}$")


def parse_range(value: str) -> set[int]:
    try:
        start_text, end_text = value.split("-", 1)
        start, end = int(start_text), int(end_text)
    except (ValueError, AttributeError) as exc:
        raise ValueError("expected range must look like 1-120") from exc
    if start < 1 or end < start:
        raise ValueError("expected range must look like 1-120")
    return set(range(start, end + 1))


def validate_completion_manifest(path: Path, expected_books: set[str]) -> list[str]:
    """Require explicit per_book/gap coverage before cross-book emotion output."""
    errors: list[str] = []
    covered: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except OSError as exc:
        return [f"completion manifest cannot be read: {exc}"]
    for number, raw in enumerate(lines, 1):
        if not raw.strip():
            errors.append(f"completion manifest line {number}: empty line")
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"completion manifest line {number}: invalid JSON: {exc}")
            continue
        if not isinstance(row, dict) or row.get("record_type") not in {"per_book", "gap"}:
            errors.append(f"completion manifest line {number}: record_type must be per_book or gap")
            continue
        book_id = row.get("book_id")
        if not is_nonempty_string(book_id):
            errors.append(f"completion manifest line {number}: book_id is required")
            continue
        if row.get("status") != "candidate":
            errors.append(f"completion manifest line {number}: status must be candidate")
        if row.get("qa_status") not in QA_STATUS:
            errors.append(f"completion manifest line {number}: qa_status must be PASS/HOLD/FAIL")
        covered.append(book_id)
    duplicates = sorted({book for book in covered if covered.count(book) > 1})
    if duplicates:
        errors.append(f"completion manifest duplicate books: {', '.join(duplicates)}")
    missing = sorted(expected_books - set(covered))
    unexpected = sorted(set(covered) - expected_books)
    if missing:
        errors.append(f"completion manifest missing target books: {', '.join(missing)}")
    if unexpected:
        errors.append(f"completion manifest unexpected books: {', '.join(unexpected)}")
    return errors


def canonical_contract_drift() -> list[str]:
    """Compare canonical constants with the orchestrator's authoritative validator."""
    upstream = Path(__file__).resolve().parents[3] / "scripts" / "core" / "validate_chapter_emotions.py"
    if not upstream.exists():
        return ["canonical contract source is unavailable: orchestrator validator not found"]
    spec = importlib.util.spec_from_file_location("orchestrator_chapter_emotions", upstream)
    if spec is None or spec.loader is None:
        return ["canonical contract source could not be loaded"]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    errors: list[str] = []
    for name in ("REQUIRED", "ROLES", "PAYOFF_LEVELS", "CONFIDENCE"):
        local = globals().get("CANONICAL_REQUIRED" if name == "REQUIRED" else name)
        remote = getattr(module, name, None)
        if local != remote:
            errors.append(f"canonical contract drift in {name}; update adapter or orchestrator schema together")
    return errors


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def contains_unknown(value: Any) -> bool:
    return "UNKNOWN" in json.dumps(value, ensure_ascii=False)


def resolve_workspace_root(explicit_root: Path | None) -> Path:
    """Resolve the project root, never inferring it from the installed Skill path."""
    root = (explicit_root or Path.cwd()).resolve()
    if not root.is_dir():
        raise RuntimeError(f"WORKSPACE_ROOT_INVALID: not a directory: {root}")
    return root


def recompute_source_fingerprint(row: dict[str, Any], project_root: Path) -> tuple[str | None, str | None]:
    evidence_path = row.get("evidence_path")
    chapter = row.get("chapter")
    if not is_nonempty_string(evidence_path):
        return None, "evidence_path is missing or empty"
    if isinstance(chapter, bool) or not isinstance(chapter, int) or chapter < 1:
        return None, "chapter is not a positive integer"

    source_ref = evidence_path.split("#", 1)[0]
    root_path = project_root.resolve()
    source_path = (root_path / Path(source_ref)).resolve()
    try:
        source_path.relative_to(root_path)
    except ValueError:
        return None, "evidence_path escapes workspace root"
    try:
        source_text = source_path.read_bytes().decode("utf-8-sig")
    except (OSError, UnicodeDecodeError) as exc:
        return None, f"cannot read source {source_path}: {exc}"

    normalized = source_text.replace("\r\n", "\n").replace("\r", "\n")
    headings = list(CHAPTER_HEADING_RE.finditer(normalized))
    matches = [heading for heading in headings if int(heading.group(1)) == chapter]
    if len(matches) != 1:
        return None, f"expected one level-one chapter heading for chapter {chapter}, found {len(matches)}"

    start = matches[0].start()
    later_starts = [heading.start() for heading in headings if heading.start() > start]
    end = min(later_starts) if later_starts else len(normalized)
    chapter_block = normalized[start:end].rstrip("\n") + "\n"
    return hashlib.sha256(chapter_block.encode("utf-8")).hexdigest(), None


def validate_source_fingerprints(
    canonical_rows: list[tuple[int, dict[str, Any], int]],
    project_root: Path,
    errors: list[str],
) -> None:
    for chapter, row, line_number in canonical_rows:
        record_id = row.get("record_id")
        stored = row.get("source_fingerprint")
        if stored == "UNAVAILABLE":
            computed, _reason = recompute_source_fingerprint(row, project_root)
            if computed is not None:
                add_error(
                    errors,
                    line_number,
                    record_id,
                    "SOURCE_FINGERPRINT_UNAVAILABLE: source is readable and the chapter block is uniquely locatable",
                )
            continue
        if not isinstance(stored, str) or not FINGERPRINT_RE.fullmatch(stored):
            add_error(
                errors,
                line_number,
                record_id,
                "SOURCE_FINGERPRINT_FORMAT: expected 64 lowercase hex characters or UNAVAILABLE",
            )
            continue

        computed, reason = recompute_source_fingerprint(row, project_root)
        if computed is None:
            add_error(
                errors,
                line_number,
                record_id,
                f"SOURCE_FINGERPRINT_UNAVAILABLE: {reason}",
            )
        elif stored != computed:
            add_error(
                errors,
                line_number,
                record_id,
                f"SOURCE_FINGERPRINT_MISMATCH: expected {computed}, got {stored}",
            )


def add_error(errors: list[str], line_number: int, record_id: Any, message: str) -> None:
    location = f"line {line_number}"
    if isinstance(record_id, str) and record_id:
        location += f" record_id={record_id}"
    errors.append(f"{location}: {message}")


def validate_canonical_row(
    row: Any,
    line_number: int,
    expected_book: str | None,
    expected: set[int] | None,
    allow_nonpass: bool,
    errors: list[str],
) -> tuple[int | None, str | None]:
    if not isinstance(row, dict):
        add_error(errors, line_number, None, "record must be a JSON object")
        return None, None

    record_id = row.get("record_id")
    missing = sorted(CANONICAL_REQUIRED - row.keys())
    if missing:
        add_error(errors, line_number, record_id, f"missing canonical fields: {', '.join(missing)}")
    extra_envelope = sorted(CANONICAL_ENVELOPE_FIELDS & row.keys())
    if extra_envelope:
        add_error(
            errors,
            line_number,
            record_id,
            "canonical record must not contain derived envelope fields: " + ", ".join(extra_envelope),
        )

    if row.get("schema_version") != 1:
        add_error(errors, line_number, record_id, "schema_version must be 1")
    if row.get("status") != "candidate":
        add_error(errors, line_number, record_id, "status must be candidate; active/deprecated are not allowed")
    if expected_book is not None and row.get("book_id") != expected_book:
        add_error(errors, line_number, record_id, f"book_id must be {expected_book}")

    chapter = row.get("chapter")
    if isinstance(chapter, bool) or not isinstance(chapter, int) or chapter < 1:
        add_error(errors, line_number, record_id, "chapter must be a positive integer")
        chapter = None
    if expected is not None and isinstance(chapter, int) and chapter not in expected:
        add_error(errors, line_number, record_id, f"chapter {chapter} is outside the requested range")

    if row.get("qa_status") not in QA_STATUS:
        add_error(errors, line_number, record_id, "qa_status must be PASS/HOLD/FAIL")
    elif row.get("qa_status") != "PASS" and not allow_nonpass:
        add_error(errors, line_number, record_id, "non-PASS record requires --allow-nonpass and does not satisfy G2")
    if row.get("confidence") not in CONFIDENCE:
        add_error(errors, line_number, record_id, "confidence must be HIGH/MEDIUM/LOW")

    secondary = row.get("secondary_reader_emotions")
    if not isinstance(secondary, list) or len(secondary) > 2:
        add_error(errors, line_number, record_id, "secondary_reader_emotions allows at most two values")
    pressure = row.get("pressure_level")
    if isinstance(pressure, bool) or not isinstance(pressure, int) or not 0 <= pressure <= 5:
        add_error(errors, line_number, record_id, "pressure_level must be an integer from 0 to 5")
    roles = row.get("chapter_role")
    if not isinstance(roles, list) or not roles or not set(roles).issubset(ROLES):
        add_error(errors, line_number, record_id, "chapter_role contains empty or unsupported values")
    if row.get("payoff_level") not in PAYOFF_LEVELS:
        add_error(errors, line_number, record_id, "unsupported payoff_level")

    for field in (
        "chapter_title",
        "evidence_path",
        "source_fingerprint",
        "main_reader_emotion",
        "emotion_object",
        "expectation_source",
        "pressure_source",
        "turning_point",
        "aftermath",
        "ending_aftertaste",
        "hook_type",
    ):
        if not is_nonempty_string(row.get(field)):
            add_error(errors, line_number, record_id, f"{field} cannot be empty")
    if row.get("payoff_level") in STRONG_PAYOFFS:
        if not row.get("visible_payoff_evidence"):
            add_error(errors, line_number, record_id, "payoff requires visible_payoff_evidence")
        if not row.get("expectation_source"):
            add_error(errors, line_number, record_id, "payoff requires expectation_source")
    if row.get("confidence") == "HIGH" and contains_unknown(row):
        add_error(errors, line_number, record_id, "HIGH confidence cannot contain UNKNOWN")

    if isinstance(chapter, int) and isinstance(row.get("book_id"), str):
        expected_record = f"{row['book_id']}:EMOTION:{chapter:04d}"
        expected_ref = f"{row['book_id']}:CHAPTER:{chapter:04d}"
        if record_id != expected_record:
            add_error(errors, line_number, record_id, f"record_id must be {expected_record}")
        if row.get("chapter_ref") != expected_ref:
            add_error(errors, line_number, record_id, f"chapter_ref must be {expected_ref}")
    return chapter, row.get("chapter_ref") if isinstance(row.get("chapter_ref"), str) else None


def validate_derived_row(
    row: Any,
    line_number: int,
    expected_type: str | None,
    all_books_complete: bool,
    errors: list[str],
) -> None:
    if not isinstance(row, dict):
        add_error(errors, line_number, None, "record must be a JSON object")
        return
    record_id = row.get("record_id")
    missing = sorted(DERIVED_REQUIRED - row.keys())
    if missing:
        add_error(errors, line_number, record_id, f"missing derived envelope fields: {', '.join(missing)}")
    record_type = row.get("record_type")
    if record_type not in DERIVED_TYPES:
        add_error(errors, line_number, record_id, "unsupported derived record_type")
    if expected_type is not None and record_type != expected_type:
        add_error(errors, line_number, record_id, f"record_type must be {expected_type}")
    if row.get("schema_version") != 1:
        add_error(errors, line_number, record_id, "schema_version must be 1")
    if row.get("status") != "candidate":
        add_error(errors, line_number, record_id, "status must be candidate; active/deprecated are not allowed")

    has_book_id = is_nonempty_string(row.get("book_id"))
    book_ids = row.get("book_ids")
    has_book_ids = isinstance(book_ids, list) and bool(book_ids) and all(is_nonempty_string(item) for item in book_ids)
    if has_book_id == has_book_ids:
        add_error(errors, line_number, record_id, "provide exactly one non-empty book_id or book_ids")
    if "evidence_refs" in row and (
        not isinstance(row.get("evidence_refs"), list) or not row.get("evidence_refs")
    ):
        add_error(errors, line_number, record_id, "evidence_refs must be a non-empty list")
    elif isinstance(row.get("evidence_refs"), list):
        malformed = [
            ref for ref in row["evidence_refs"]
            if not isinstance(ref, str) or not ref.strip() or len(ref.split(":")) < 3 or any(char.isspace() for char in ref)
        ]
        if malformed:
            add_error(errors, line_number, record_id, "evidence_refs must use structured BOOK_ID:TYPE:VALUE references")
        if is_nonempty_string(row.get("book_id")):
            foreign = [ref for ref in row["evidence_refs"] if isinstance(ref, str) and not ref.startswith(f"{row['book_id']}:")]
            if foreign:
                add_error(errors, line_number, record_id, f"evidence_refs cite another book: {', '.join(foreign)}")
    if "unknowns" in row and not isinstance(row.get("unknowns"), list):
        add_error(errors, line_number, record_id, "unknowns must be a list")
    if row.get("confidence") not in CONFIDENCE:
        add_error(errors, line_number, record_id, "confidence must be HIGH/MEDIUM/LOW")
    if row.get("qa_status") not in QA_STATUS:
        add_error(errors, line_number, record_id, "qa_status must be PASS/HOLD/FAIL")
    if row.get("confidence") == "HIGH" and (contains_unknown(row) or row.get("qa_status") != "PASS"):
        add_error(errors, line_number, record_id, "HIGH confidence requires qa_status PASS and no UNKNOWN")

    if record_type in {"nearest_neighbor", "cluster"} and not all_books_complete:
        refs = row.get("evidence_refs", [])
        gate_in_refs = isinstance(refs, list) and any("ALL_BOOKS_COMPLETE" in str(ref) for ref in refs)
        if row.get("all_books_complete") is not True and not gate_in_refs:
            add_error(
                errors,
                line_number,
                record_id,
                "cross-book record requires --all-books-complete or an ALL_BOOKS_COMPLETE evidence ref",
            )


def validate_file(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    errors: list[str] = []
    if args.kind == "canonical":
        errors.extend(canonical_contract_drift())
    if args.kind in {"nearest_neighbor", "cluster"}:
        if args.expected_books is None or args.completion_manifest is None:
            return {
                "ok": False,
                "errors": ["cross-book validation requires --expected-books and --completion-manifest"],
            }, 1
        errors.extend(validate_completion_manifest(args.completion_manifest, args.expected_books))
    chapters: list[int] = []
    chapter_refs: list[str] = []
    record_ids: list[str] = []
    canonical_rows: list[tuple[int, dict[str, Any], int]] = []
    pass_records = 0
    expected = parse_range(args.expected_range) if args.expected_range else None
    excluded = {int(value) for value in args.exclude.split(",") if value.strip()} if args.exclude else set()
    if expected is not None:
        expected -= excluded

    try:
        lines = args.target.read_text(encoding="utf-8-sig").splitlines()
    except OSError as exc:
        result = {"ok": False, "errors": [f"cannot read {args.target}: {exc}"]}
        return result, 1

    for line_number, raw in enumerate(lines, 1):
        if not raw.strip():
            errors.append(f"line {line_number}: empty JSONL line is not allowed")
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_number}: invalid JSON: {exc.msg} at column {exc.colno}")
            continue

        if args.kind == "canonical":
            chapter, chapter_ref = validate_canonical_row(
                row, line_number, args.expected_book, expected, args.allow_nonpass, errors
            )
            if isinstance(chapter, int):
                chapters.append(chapter)
                if isinstance(row, dict):
                    canonical_rows.append((chapter, row, line_number))
            if isinstance(chapter_ref, str):
                chapter_refs.append(chapter_ref)
            if isinstance(row, dict) and isinstance(row.get("record_id"), str):
                record_ids.append(row["record_id"])
            if isinstance(row, dict) and row.get("qa_status") == "PASS":
                pass_records += 1
        else:
            validate_derived_row(row, line_number, args.kind, args.all_books_complete, errors)
            if isinstance(row, dict) and isinstance(row.get("record_id"), str):
                record_ids.append(row["record_id"])

    if args.kind == "canonical":
        try:
            workspace_root = resolve_workspace_root(args.workspace_root)
        except RuntimeError as exc:
            errors.append(str(exc))
            workspace_root = None

        opened_promises: set[str] = set()
        for chapter, row, line_number in sorted(canonical_rows, key=lambda item: (item[0], item[2])):
            opened = row.get("promise_opened")
            paid = row.get("promise_paid")
            if not isinstance(opened, list):
                add_error(errors, line_number, row.get("record_id"), "promise_opened must be a list")
                opened = []
            if not isinstance(paid, list):
                add_error(errors, line_number, row.get("record_id"), "promise_paid must be a list")
                paid = []

            current_opened: set[str] = set()
            for field_name, values in (("promise_opened", opened), ("promise_paid", paid)):
                seen_in_field: set[str] = set()
                for promise in values:
                    if not isinstance(promise, str) or not promise.strip():
                        add_error(
                            errors,
                            line_number,
                            row.get("record_id"),
                            f"{field_name} must contain non-empty strings",
                        )
                        continue
                    if promise in seen_in_field:
                        add_error(
                            errors,
                            line_number,
                            row.get("record_id"),
                            f"DUPLICATE_{field_name.upper()}: {promise}",
                        )
                    seen_in_field.add(promise)
                    if field_name == "promise_opened":
                        current_opened.add(promise)

            for promise in paid:
                if (
                    isinstance(promise, str)
                    and promise.strip()
                    and promise not in opened_promises
                    and promise not in current_opened
                ):
                    add_error(
                        errors,
                        line_number,
                        row.get("record_id"),
                        "ORPHAN_PROMISE_PAID: "
                        f"{promise} was not opened in an earlier chapter or the current chapter",
                    )
            opened_promises.update(current_opened)
        if workspace_root is not None:
            validate_source_fingerprints(canonical_rows, workspace_root, errors)

    duplicate_chapters = sorted({chapter for chapter in chapters if chapters.count(chapter) > 1})
    duplicate_refs = sorted({ref for ref in chapter_refs if chapter_refs.count(ref) > 1})
    duplicate_ids = sorted({record_id for record_id in record_ids if record_ids.count(record_id) > 1})
    if duplicate_chapters:
        errors.append(f"duplicate chapters: {','.join(map(str, duplicate_chapters))}")
    if duplicate_refs:
        errors.append("duplicate chapter_refs: " + ",".join(duplicate_refs))
    if duplicate_ids:
        errors.append("duplicate record_ids: " + ",".join(duplicate_ids))
    if args.kind == "canonical" and expected is not None:
        actual = set(chapters)
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        if missing:
            errors.append(f"missing chapters: {','.join(map(str, missing))}")
        if unexpected:
            errors.append(f"unexpected chapters: {','.join(map(str, unexpected))}")
    else:
        missing = []
        unexpected = []

    result = {
        "kind": args.kind,
        "file": str(args.target),
        "records": len(record_ids),
        "pass_records": pass_records if args.kind == "canonical" else None,
        "expected": len(expected) if expected is not None else None,
        "missing_chapters": missing,
        "unexpected_chapters": unexpected,
        "duplicate_chapters": duplicate_chapters,
        "duplicate_chapter_refs": duplicate_refs,
        "duplicate_record_ids": duplicate_ids,
        "errors": errors,
    }
    result["ok"] = not errors
    return result, 0 if result["ok"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate canonical chapter-emotion JSONL or derived emotion-envelope JSONL. This command never edits input files."
    )
    parser.add_argument("target", type=Path, help="JSONL file to validate")
    parser.add_argument(
        "--kind",
        choices=("canonical", *sorted(DERIVED_TYPES)),
        required=True,
        help="canonical for chapter_emotion.jsonl; otherwise the derived record type",
    )
    parser.add_argument("--expected-book", help="Expected book_id for canonical records")
    parser.add_argument(
        "--workspace-root",
        type=Path,
        help="Project root used to resolve canonical evidence_path; defaults to the current working directory.",
    )
    parser.add_argument("--expected-range", help="Expected canonical chapter range, e.g. 1-120")
    parser.add_argument("--exclude", default="", help="Comma-separated excluded canonical chapters")
    parser.add_argument(
        "--allow-nonpass",
        action="store_true",
        help="Keep canonical HOLD/FAIL rows for draft validation; they still do not count as usable coverage",
    )
    parser.add_argument(
        "--all-books-complete",
        action="store_true",
        help="Confirm the cross-book extraction/QA gate for nearest_neighbor and cluster records",
    )
    parser.add_argument(
        "--expected-books",
        type=lambda value: {item.strip() for item in value.split(",") if item.strip()},
        help="Comma-separated target BOOK IDs for cross-book validation",
    )
    parser.add_argument(
        "--completion-manifest",
        type=Path,
        help="JSONL containing exactly one candidate per_book or gap record for every expected book",
    )
    return parser


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args()
    if args.kind == "canonical" and not args.expected_book:
        parser.error("--expected-book is required for --kind canonical")
    if args.kind in {"nearest_neighbor", "cluster"} and (not args.all_books_complete or not args.expected_books):
        parser.error("cross-book validation requires --all-books-complete and non-empty --expected-books")
    try:
        result, exit_code = validate_file(args)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
