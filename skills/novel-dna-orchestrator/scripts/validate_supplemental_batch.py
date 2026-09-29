#!/usr/bin/env python3
"""V1.6.2 batch-level consistency and clustering eligibility gates.

Checks three things that V1.6.1 intentionally did not enforce:
1) source_route.derived_views matches real derived outputs/gaps;
2) per-book manifest status matches HOLD reality and batch-status;
3) only qa_status=PASS controlled derived records are clustering-eligible.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

CONTROLLED_VIEWS = {
    "ability_assets",
    "dungeon_rule_assets",
    "relationship_engine_assets",
    "charismatic_antagonist_assets",
    "combat_expression_assets",
}

COMPLETE = "COMPLETE_SUPPLEMENTAL_SOURCE"
WITH_HOLDS = "COMPLETE_SUPPLEMENTAL_SOURCE_WITH_HOLDS"
BLOCKED = "BLOCKED"
VALID_COMPLETION = {COMPLETE, WITH_HOLDS, BLOCKED}


def load_json(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(obj, dict):
        raise ValueError(f"{path}: expected JSON object")
    return obj


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        obj = json.loads(line)
        if not isinstance(obj, dict):
            raise ValueError(f"{path}:{lineno}: expected JSON object")
        rows.append(obj)
    return rows


def route_map(path: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in load_jsonl(path):
        book_id = row.get("book_id")
        if not isinstance(book_id, str) or not book_id:
            raise ValueError(f"{path}: route without book_id")
        if book_id in out:
            raise ValueError(f"{path}: duplicate route for {book_id}")
        out[book_id] = row
    return out


def manifest_views(manifest: dict[str, Any]) -> tuple[set[str], set[str]]:
    """Return (declared views, explicit zero-record gap views)."""
    declared: set[str] = set()
    gaps: set[str] = set()

    def visit(items: Any) -> None:
        if not isinstance(items, list):
            return
        for item in items:
            if isinstance(item, str) and item:
                declared.add(item)
                continue
            if not isinstance(item, dict):
                continue
            view = item.get("view")
            if not isinstance(view, str) or not view:
                # Historical manifests may use path/profile only. File scan below
                # remains authoritative for actual outputs.
                continue
            declared.add(view)
            records = item.get("records", item.get("record_count"))
            coverage = str(item.get("coverage_status", "")).lower()
            if records == 0 and any(token in coverage for token in ("gap", "insufficient", "checked", "none")):
                gaps.add(view)

    visit(manifest.get("derived_views"))
    outputs = manifest.get("outputs")
    if isinstance(outputs, dict):
        visit(outputs.get("derived_views"))
    return declared, gaps


def actual_derived_views(book_root: Path) -> set[str]:
    views: set[str] = set()
    if not book_root.exists():
        return views
    for path in book_root.rglob("*"):
        if not path.is_file():
            continue
        if path.parent.name != "derived":
            continue
        if path.suffix.lower() not in {".json", ".jsonl"}:
            continue
        views.add(path.stem)
    return views


def controlled_records(book_root: Path, view: str) -> list[dict[str, Any]]:
    matches = [p for p in book_root.rglob(f"{view}.json*") if p.parent.name == "derived"]
    if not matches:
        return []
    if len(matches) > 1:
        raise ValueError(f"{book_root}: multiple files for controlled view {view}: {matches}")
    path = matches[0]
    if path.suffix.lower() == ".jsonl":
        return load_jsonl(path)
    obj = load_json(path)
    if view == "combat_expression_assets":
        assets = obj.get("assets")
        if not isinstance(assets, list):
            raise ValueError(f"{path}: assets must be list")
        if any(not isinstance(x, dict) for x in assets):
            raise ValueError(f"{path}: every asset must be object")
        return assets
    # Defensive fallback for future JSON-based controlled views.
    rows = obj.get("records")
    if isinstance(rows, list) and all(isinstance(x, dict) for x in rows):
        return rows
    raise ValueError(f"{path}: unsupported controlled JSON shape for {view}")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Validate V1.6.2 supplemental route/output/status/cluster eligibility consistency."
    )
    parser.add_argument("--root", type=Path, required=True, help="nova-material-library root")
    parser.add_argument("--batch-dir", required=True, help="batch directory relative to root")
    parser.add_argument("--books", required=True, help="comma-separated BOOK IDs")
    parser.add_argument("--output", type=Path, help="optional JSON result output")
    args = parser.parse_args()

    books = [x.strip() for x in args.books.split(",") if x.strip()]
    root = args.root.resolve()
    batch_dir = root / args.batch_dir
    route_path = batch_dir / "source_routes.jsonl"
    batch_status_path = batch_dir / "batch-status.json"

    route_errors: list[str] = []
    status_errors: list[str] = []
    eligibility_errors: list[str] = []
    per_book: dict[str, Any] = {}
    per_view_totals: dict[str, dict[str, Any]] = {
        view: {"records": 0, "eligible": 0, "held": 0, "eligible_record_ids": [], "held_record_ids": []}
        for view in sorted(CONTROLLED_VIEWS)
    }

    try:
        routes = route_map(route_path)
    except Exception as exc:
        routes = {}
        route_errors.append(str(exc))

    try:
        batch_status = load_json(batch_status_path)
    except Exception as exc:
        batch_status = {}
        status_errors.append(str(exc))
    batch_books = batch_status.get("books") if isinstance(batch_status, dict) else None
    if not isinstance(batch_books, dict):
        status_errors.append(f"{batch_status_path}: books must be an object")
        batch_books = {}

    for book_id in books:
        book_root = root / "books" / book_id
        manifest_path = book_root / "manifest.json"
        if not manifest_path.exists():
            status_errors.append(f"{manifest_path}: missing manifest")
            continue
        try:
            manifest = load_json(manifest_path)
        except Exception as exc:
            status_errors.append(str(exc))
            continue

        route = routes.get(book_id)
        if route is None:
            route_errors.append(f"{book_id}: missing source_route")
            route_views: set[str] = set()
        else:
            raw_route_views = route.get("derived_views")
            if not isinstance(raw_route_views, list) or any(not isinstance(x, str) or not x for x in raw_route_views):
                route_errors.append(f"{book_id}: source_route.derived_views must be non-empty strings")
                route_views = set()
            else:
                route_views = set(raw_route_views)

        declared_views, gap_views = manifest_views(manifest)
        file_views = actual_derived_views(book_root)
        realized_views = file_views | gap_views

        unauthorized_files = sorted(file_views - route_views)
        missing_routed = sorted(route_views - realized_views)
        undeclared_files = sorted(file_views - declared_views) if declared_views else []

        if unauthorized_files:
            route_errors.append(
                f"{book_id}: derived files exist outside source_route authorization: {', '.join(unauthorized_files)}"
            )
        if missing_routed:
            route_errors.append(
                f"{book_id}: routed derived views have neither output file nor explicit zero-record gap: {', '.join(missing_routed)}"
            )
        if undeclared_files:
            route_errors.append(
                f"{book_id}: derived files missing from manifest derived view declarations: {', '.join(undeclared_files)}"
            )

        controlled: dict[str, Any] = {}
        total_holds = 0
        for view in sorted(CONTROLLED_VIEWS & file_views):
            try:
                rows = controlled_records(book_root, view)
            except Exception as exc:
                eligibility_errors.append(str(exc))
                continue
            eligible_ids: list[str] = []
            held_ids: list[str] = []
            for i, row in enumerate(rows, 1):
                rid = row.get("record_id")
                if not isinstance(rid, str) or not rid:
                    eligibility_errors.append(f"{book_id}/{view} record[{i}]: missing record_id")
                    rid = f"{book_id}/{view}/record[{i}]"
                qa_status = row.get("qa_status")
                if qa_status == "PASS":
                    eligible_ids.append(rid)
                elif qa_status == "HOLD":
                    held_ids.append(rid)
                else:
                    eligibility_errors.append(
                        f"{book_id}/{view} {rid}: qa_status must be PASS or HOLD for cluster eligibility"
                    )
            total_holds += len(held_ids)
            controlled[view] = {
                "records": len(rows),
                "eligible": len(eligible_ids),
                "held": len(held_ids),
                "eligible_record_ids": eligible_ids,
                "held_record_ids": held_ids,
            }
            agg = per_view_totals[view]
            agg["records"] += len(rows)
            agg["eligible"] += len(eligible_ids)
            agg["held"] += len(held_ids)
            agg["eligible_record_ids"].extend(eligible_ids)
            agg["held_record_ids"].extend(held_ids)

        manifest_status = manifest.get("status")
        if manifest_status not in VALID_COMPLETION:
            status_errors.append(
                f"{book_id}: manifest.status must be one of {sorted(VALID_COMPLETION)}, got {manifest_status!r}"
            )
        if total_holds > 0 and manifest_status != WITH_HOLDS:
            status_errors.append(
                f"{book_id}: {total_holds} controlled derived HOLD records require manifest.status={WITH_HOLDS}"
            )
        batch_book_status = batch_books.get(book_id)
        if batch_book_status != manifest_status:
            status_errors.append(
                f"{book_id}: batch-status={batch_book_status!r} != manifest.status={manifest_status!r}"
            )

        per_book[book_id] = {
            "route_views": sorted(route_views),
            "manifest_declared_views": sorted(declared_views),
            "actual_file_views": sorted(file_views),
            "explicit_gap_views": sorted(gap_views),
            "unauthorized_file_views": unauthorized_files,
            "missing_routed_views": missing_routed,
            "manifest_status": manifest_status,
            "batch_status": batch_book_status,
            "controlled": controlled,
            "controlled_hold_records": total_holds,
        }

    extra_routes = sorted(set(routes) - set(books))
    if extra_routes:
        route_errors.append(f"source_routes contains unexpected books for this validation scope: {', '.join(extra_routes)}")

    route_status = "PASS" if not route_errors else "FAIL"
    completion_status = "PASS" if not status_errors else "FAIL"

    blocked_views: list[str] = []
    mixed_views: list[str] = []
    ready_views: list[str] = []
    for view, stats in per_view_totals.items():
        if stats["records"] == 0:
            continue
        if stats["eligible"] == 0:
            blocked_views.append(view)
        elif stats["held"] > 0:
            mixed_views.append(view)
        else:
            ready_views.append(view)

    if eligibility_errors:
        eligibility_status = "FAIL"
    else:
        eligibility_status = "PASS"

    full_recluster_ready = (
        route_status == "PASS"
        and completion_status == "PASS"
        and eligibility_status == "PASS"
        and not blocked_views
    )

    result = {
        "gate": "SUPPLEMENTAL_BATCH_CONSISTENCY_V1_6_2",
        "status": "PASS" if route_status == completion_status == eligibility_status == "PASS" else "FAIL",
        "route_output_consistency_gate": {
            "status": route_status,
            "errors": route_errors,
        },
        "completion_status_consistency_gate": {
            "status": completion_status,
            "errors": status_errors,
        },
        "cluster_eligibility_gate": {
            "status": eligibility_status,
            "policy": "ONLY qa_status=PASS records may enter nearest_neighbor/cluster; HOLD stays inventory-only",
            "errors": eligibility_errors,
            "ready_views": ready_views,
            "mixed_views_pass_only": mixed_views,
            "blocked_views_zero_eligible": blocked_views,
            "per_view": per_view_totals,
        },
        "full_recluster_ready": full_recluster_ready,
        "per_book": per_book,
        "ok": route_status == completion_status == eligibility_status == "PASS",
    }

    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        output_path = args.output
        if not output_path.is_absolute():
            output_path = root / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
