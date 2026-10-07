#!/usr/bin/env python3
"""Package-mode gate tests (D1-D9) for the shared DNA runtime hardening.

Covers VERSIONED_SHARED_DNA_PACKAGE_MODE detection (package_id ==
nova-shared-dna-library), the active/status gate (--allow-staging-library,
exit 3 NOT_ACTIVE / exit 4 MANIFEST_INVALID), deterministic integrity
verification (exit 4 INTEGRITY_MISMATCH, fail closed), and legacy-library
backward compatibility (no manifest -> old behavior unchanged).

Self-contained fixtures: no machine-specific paths, no external dependencies.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SEARCH = Path(__file__).with_name("search_dna_candidates.py")

ROW = {
    "record_id": "GF:TEST:0001",
    "record_type": "golden_finger",
    "book_id": "BOOK_TEST",
    "status": "candidate",
    "qa_status": "PASS",
    "evidence_refs": ["ch01-ch05"],
    "title": "测试金手指",
    "core_mechanic": "资源按确定规则转换为成长资产",
    "chapters_covered": ["ch01-ch05"],
}

failures: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(("PASS " if ok else "FAIL ") + name + (f"  {detail}" if detail and not ok else ""))
    if not ok:
        failures.append(name)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def build_package(root: Path, *, status: str, active: bool, extra_manifest: dict | None = None) -> dict:
    """Minimal but structurally valid shared DNA package with correct hashes."""
    rel = "DNA素材/02_金手指/per_book/BOOK_TEST.jsonl"
    write_jsonl(root / rel, [ROW])
    payload = (root / rel).read_bytes()
    manifest = {
        "schema_version": "1.0.0",
        "package_id": "nova-shared-dna-library",
        "package_version": "1.0.0",
        "status": status,
        "active": active,
        "artifact_paths": {"gf_test": rel},
        "artifact_sha256": {"gf_test": hashlib.sha256(payload).hexdigest()},
    }
    if extra_manifest:
        manifest.update(extra_manifest)
    (root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    return manifest


def run(library: Path, *args: str) -> tuple[int, str]:
    r = subprocess.run(
        [sys.executable, str(SEARCH), "--library", str(library), *args, "--format", "json"],
        check=False, capture_output=True, text=True, encoding="utf-8",
    )
    return r.returncode, (r.stdout or r.stderr)


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)

        # D1 — valid staging package + --allow-staging-library -> search PASS
        root = base / "d1"; root.mkdir()
        build_package(root, status="INSTALLATION_STAGING_NOT_ACTIVE", active=False)
        code, out = run(root, "--query", "资源 成长", "--include-per-book", "--allow-staging-library")
        ok = code == 0 and '"returned": 1' in out.replace(" ", "").replace('"returned":1', '"returned": 1') or (code == 0 and "GF:TEST:0001" in out)
        meta_ok = code == 0 and "VERSIONED_PACKAGE" in out and "INSTALLATION_STAGING_NOT_ACTIVE" in out
        check("D1 staging+flag search PASS", ok and meta_ok, out[:200])

        # D2 — staging package without flag -> NOT_ACTIVE exit 3
        code, out = run(root, "--query", "资源 成长", "--include-per-book")
        try:
            gap = json.loads(out.splitlines()[0]).get("gap")
        except Exception:
            gap = None
        check("D2 staging no-flag exit3 NOT_ACTIVE", code == 3 and gap == "SHARED_DNA_LIBRARY_NOT_ACTIVE", f"code={code} out={out[:150]}")

        # D3 — active valid package -> PASS with ACTIVE metadata
        root = base / "d3"; root.mkdir()
        build_package(root, status="ACTIVE_SHARED_LIBRARY", active=True)
        code, out = run(root, "--query", "资源 成长", "--include-per-book")
        check("D3 active package PASS + ACTIVE status", code == 0 and "ACTIVE_SHARED_LIBRARY" in out and "GF:TEST:0001" in out, out[:200])

        # D4 — tampered payload, manifest hash unchanged -> exit 4 INTEGRITY_MISMATCH
        root = base / "d4"; root.mkdir()
        build_package(root, status="ACTIVE_SHARED_LIBRARY", active=True)
        row = dict(ROW); row["title"] = "被篡改的金手指"
        write_jsonl(root / "DNA素材/02_金手指/per_book/BOOK_TEST.jsonl", [row])
        code, out = run(root, "--query", "资源 成长", "--include-per-book")
        try:
            gap = json.loads(out.splitlines()[0]).get("gap")
        except Exception:
            gap = None
        check("D4 tampered payload exit4 INTEGRITY_MISMATCH", code == 4 and gap == "SHARED_DNA_LIBRARY_INTEGRITY_MISMATCH", f"code={code} out={out[:150]}")

        # D5 — missing declared artifact -> fail closed
        root = base / "d5"; root.mkdir()
        build_package(root, status="ACTIVE_SHARED_LIBRARY", active=True)
        (root / "DNA素材/02_金手指/per_book/BOOK_TEST.jsonl").unlink()
        code, out = run(root, "--query", "资源 成长", "--include-per-book", "--allow-staging-library")
        try:
            gap = json.loads(out.splitlines()[0]).get("gap")
        except Exception:
            gap = None
        check("D5 missing artifact exit4", code == 4 and gap == "SHARED_DNA_LIBRARY_INTEGRITY_MISMATCH", f"code={code} out={out[:150]}")

        # D6 — path escape ../outside.json -> fail closed
        root = base / "d6"; root.mkdir()
        (root / "outside.json").write_text("{}", encoding="utf-8")
        build_package(root, status="ACTIVE_SHARED_LIBRARY", active=True,
                      extra_manifest={"artifact_paths": {"esc": "../outside.json"},
                                      "artifact_sha256": {"esc": hashlib.sha256(b"{}").hexdigest()}})
        code, out = run(root, "--query", "资源 成长", "--include-per-book")
        try:
            gap = json.loads(out.splitlines()[0]).get("gap")
        except Exception:
            gap = None
        check("D6 path escape exit4", code == 4 and gap == "SHARED_DNA_LIBRARY_INTEGRITY_MISMATCH", f"code={code} out={out[:150]}")

        # D7 — active=true + staging status -> MANIFEST_INVALID exit 4
        root = base / "d7"; root.mkdir()
        build_package(root, status="INSTALLATION_STAGING_NOT_ACTIVE", active=True)
        code, out = run(root, "--query", "资源 成长", "--include-per-book")
        try:
            gap = json.loads(out.splitlines()[0]).get("gap")
        except Exception:
            gap = None
        check("D7 flag/status mismatch exit4", code == 4 and gap == "SHARED_DNA_LIBRARY_MANIFEST_INVALID", f"code={code} out={out[:150]}")

        # D8 — artifact_paths / artifact_sha256 keys mismatch -> exit 4
        root = base / "d8"; root.mkdir()
        rel = "DNA素材/02_金手指/per_book/BOOK_TEST.jsonl"
        write_jsonl(root / rel, [ROW])
        (root / "manifest.json").write_text(json.dumps({
            "package_id": "nova-shared-dna-library", "package_version": "1.0.0",
            "status": "ACTIVE_SHARED_LIBRARY", "active": True,
            "artifact_paths": {"gf_test": rel},
            "artifact_sha256": {"different_key": "0" * 64},
        }, ensure_ascii=False), encoding="utf-8")
        code, out = run(root, "--query", "资源 成长", "--include-per-book")
        try:
            gap = json.loads(out.splitlines()[0]).get("gap")
        except Exception:
            gap = None
        check("D8 hash keys mismatch exit4", code == 4 and gap == "SHARED_DNA_LIBRARY_INTEGRITY_MISMATCH", f"code={code} out={out[:150]}")

        # D9 — legacy library: only DNA素材/, no manifest -> old behavior unchanged
        root = base / "d9"; root.mkdir()
        write_jsonl(root / "DNA素材/02_金手指/per_book/BOOK_TEST.jsonl", [ROW])
        code, out = run(root, "--query", "资源 成长", "--include-per-book")
        check("D9 legacy library backward compatible", code == 0 and "GF:TEST:0001" in out and "VERSIONED_PACKAGE" not in out, out[:200])

        # D9b — legacy flag on legacy library is harmless
        code, out = run(root, "--query", "资源 成长", "--include-per-book", "--allow-staging-library")
        check("D9b legacy + flag no-op", code == 0 and "GF:TEST:0001" in out, out[:150])

    print(json.dumps({"ok": not failures, "failures": failures}, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
