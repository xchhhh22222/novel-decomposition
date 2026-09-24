#!/usr/bin/env python3
"""Smoke tests for V1.1 component-level DNA retrieval."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


SEARCH = Path(__file__).with_name("search_dna_candidates.py")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def run_search(library: Path, *args: str) -> dict:
    result = subprocess.run(
        [
            sys.executable,
            str(SEARCH),
            "--library",
            str(library),
            *args,
            "--format",
            "json",
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr or result.stdout)
    return json.loads(result.stdout)


def main() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as temp:
        library = Path(temp)
        write_jsonl(
            library / "DNA素材" / "03_世界观" / "per_book" / "BOOK_01.jsonl",
            [
                {
                    "record_type": "per_book",
                    "schema_version": 2,
                    "record_id": "WB:BOOK:BOOK_01",
                    "status": "candidate",
                    "book_id": "BOOK_01",
                    "confidence": "HIGH",
                    "qa_status": "PASS",
                    "factions": [
                        {
                            "faction_id": "WB:FACTION:001",
                            "name_in_book": "镇武司",
                            "public_role": "官方武者管理",
                            "actual_interest": "控制秘境准入与晶核配额",
                            "evidence_refs": ["BOOK_01:CHAPTER:0005"],
                            "unknowns": [],
                        }
                    ],
                    "rule_chains": [],
                    "resource_circuits": [],
                    "threat_generators": [],
                    "map_expansion_patterns": [],
                    "information_control_patterns": [],
                    "evidence_refs": ["BOOK_01:CHAPTER:0005"],
                    "unknowns": [],
                }
            ],
        )
        write_jsonl(
            library / "DNA素材" / "04_修炼体系" / "per_book" / "BOOK_01.jsonl",
            [
                {
                    "record_type": "per_book",
                    "schema_version": 2,
                    "record_id": "CS:BOOK:BOOK_01",
                    "status": "candidate",
                    "book_id": "BOOK_01",
                    "confidence": "HIGH",
                    "qa_status": "PASS",
                    "cultivation_systems": [
                        {
                            "system_id": "CS:SYSTEM:001",
                            "name_in_book": "源能武道",
                            "growth_loop": "吸收晶核→训练→实战验证",
                            "realm_system": {
                                "realm_order": [
                                    {
                                        "realm_id": "CS:REALM:001",
                                        "name_in_book": "淬体",
                                        "stage_difference": "体魄稳定增强",
                                        "evidence_refs": ["BOOK_01:CHAPTER:0002"],
                                    }
                                ]
                            },
                            "evidence_refs": ["BOOK_01:CHAPTER:0002"],
                            "unknowns": [],
                        }
                    ],
                    "system_relations": [],
                    "techniques": [
                        {
                            "technique_id": "CS:TECHNIQUE:001",
                            "name_in_book": "震骨拳",
                            "core_effect": "近战爆发",
                            "evidence_refs": ["BOOK_01:CHAPTER:0007"],
                            "unknowns": [],
                        }
                    ],
                    "artifacts": [
                        {
                            "artifact_id": "CS:ARTIFACT:001",
                            "name_in_book": "养刃刀",
                            "core_effect": "以晶核供能并随战斗成长",
                            "growth_or_upgrade": "吸收晶核升级",
                            "evidence_refs": ["BOOK_01:CHAPTER:0015"],
                            "unknowns": [],
                        }
                    ],
                    "resource_assets": [
                        {
                            "resource_id": "CS:RESOURCE:001",
                            "name_in_book": "异兽晶核",
                            "use_or_conversion": "修炼与武器供能",
                            "evidence_refs": ["BOOK_01:CHAPTER:0015"],
                            "unknowns": [],
                        }
                    ],
                    "evidence_refs": ["BOOK_01:CHAPTER:0002"],
                    "unknowns": [],
                }
            ],
        )

        artifact = run_search(
            library,
            "--query",
            "成长 晶核 武器",
            "--modules",
            "修炼体系",
            "--components",
            "artifact",
            "--limit",
            "5",
        )
        if artifact.get("returned") != 1:
            failures.append(f"artifact returned={artifact.get('returned')}")
        else:
            row = artifact["results"][0]
            if row.get("component_id") != "CS:ARTIFACT:001":
                failures.append(f"wrong artifact id={row.get('component_id')}")
            if row.get("source_record_id") != "CS:BOOK:BOOK_01":
                failures.append("artifact lost source_record_id")
            if row.get("book_id") != "BOOK_01":
                failures.append("artifact lost book_id")

        faction = run_search(
            library,
            "--query",
            "秘境 准入 晶核",
            "--modules",
            "世界观",
            "--components",
            "势力",
            "--limit",
            "5",
        )
        if faction.get("returned") != 1:
            failures.append(f"faction returned={faction.get('returned')}")
        elif faction["results"][0].get("component_id") != "WB:FACTION:001":
            failures.append("faction component alias failed")

        record = run_search(
            library,
            "--query",
            "源能武道",
            "--modules",
            "修炼体系",
            "--include-per-book",
            "--limit",
            "5",
        )
        if not record.get("results") or record["results"][0].get("component_type"):
            failures.append("record-level backward compatibility failed")

    print(json.dumps({"ok": not failures, "failures": failures}, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
