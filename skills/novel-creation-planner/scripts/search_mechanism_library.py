#!/usr/bin/env python3
"""Deterministic retrieval over a versioned RMF mechanism-library package.

This adapter is a READ-ONLY retrieval + routing layer over the human-approved
mechanism library (stable families / composition links / composition recipes).
It performs NO re-clustering, NO embedding search, NO semantic regeneration.

Layering contract:
  - mechanism_library_root  -> HOW THE STORY RUNS (families / recipes / bridges)
  - shared_library_root     -> WHAT THE STORY IS MADE OF (per-book DNA material)
The two roots are separate trust layers and must never be conflated.

Backward compatibility: novel-creation-planner runs exactly as before unless a
plan/config explicitly provides ``mechanism_library_root``. The legacy DNA
search (search_dna_candidates.py) is untouched.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Iterable

GAP_UNAVAILABLE = "MECHANISM_LIBRARY_UNAVAILABLE"
GAP_NOT_ACTIVE = "MECHANISM_LIBRARY_NOT_ACTIVE"
GAP_INTEGRITY = "MECHANISM_LIBRARY_INTEGRITY_MISMATCH"
GAP_MANIFEST_INVALID = "MECHANISM_LIBRARY_MANIFEST_INVALID"

EXIT_OK = 0
EXIT_UNAVAILABLE = 2
EXIT_NOT_ACTIVE = 3
EXIT_INTEGRITY = 4
EXIT_USAGE = 64

STATUS_ACTIVE_PROMOTED = "ACTIVE_PROMOTED"

FAMILY = "family"
RECIPE = "recipe"
LINK = "link"
ASSET_TYPES = (FAMILY, RECIPE, LINK)

SLOT_ALIASES = {
    "golden_finger_core": "golden_finger_core",
    "golden_finger_ability": "golden_finger_ability",
    "plotline": "plotline",
    "relationship_engine": "relationship_engine",
    "longline_engine": "__recipes__",
}

WEIGHTS = {
    FAMILY: (("family_name", 3.0), ("tags", 3.0), ("one_sentence_core", 2.0),
             ("core_mechanism_definition", 1.0), ("minimum_definition", 1.0),
             ("domain", 0.5), ("comparison_lane", 0.5), ("family_id", 2.0)),
    RECIPE: (("recipe_name", 3.0), ("entry_condition", 2.0), ("creative_value", 2.0),
             ("slot_roles", 2.0), ("variation_axes", 1.0), ("failure_modes", 1.0),
             ("recurrence_loop", 1.0), ("recipe_id", 2.0)),
    LINK: (("link_id", 2.0), ("source_family_id", 2.0), ("target_family_id", 2.0),
           ("source_output", 1.0), ("target_trigger_or_input", 1.0), ("bridge_condition", 1.0)),
}


def tokenize(text: str) -> set[str]:
    """Deterministic lexical tokens: whitespace words + CJK bigrams."""
    if not text:
        return set()
    text = unicodedata.normalize("NFKC", text).lower()
    tokens: set[str] = set()
    for word in re.split(r"[\s,，。;；:：!！?？、/\\|+\-()（）\[\]【】]+", text):
        if not word:
            continue
        tokens.add(word)
        if re.search(r"[\u4e00-\u9fff]", word):
            for i in range(len(word) - 1):
                tokens.add(word[i:i + 2])
    return tokens


def field_text(asset: dict, field: str) -> str:
    value = asset.get(field)
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        return " ".join(json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v) for v in value)
    return json.dumps(value, ensure_ascii=False)


def score(asset: dict, kind: str, tokens: set[str]) -> float:
    if not tokens:
        return 0.0
    total = 0.0
    for field, weight in WEIGHTS[kind]:
        text = field_text(asset, field).lower()
        if not text:
            continue
        for token in tokens:
            if token in text:
                total += weight
    return total


def load_package(root: Path) -> dict:
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    families_doc = json.loads((root / "stable-families.json").read_text(encoding="utf-8"))
    held_doc = json.loads((root / "held-families.json").read_text(encoding="utf-8"))
    links = [json.loads(l) for l in (root / "composition-links.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    recipes = [json.loads(l) for l in (root / "composition-recipes.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    slot_index = json.loads((root / "mechanism-slot-index.json").read_text(encoding="utf-8"))
    adjacency = json.loads((root / "composition-adjacency-index.json").read_text(encoding="utf-8"))
    return {
        "manifest": manifest,
        "families": families_doc["families"],
        "held": held_doc["held_families"],
        "links": links,
        "recipes": recipes,
        "slot_index": slot_index,
        "adjacency": adjacency,
    }


def verify_package_integrity(root: Path, manifest: dict) -> list[str]:
    """Deterministic fail-closed integrity check: on-disk bytes == approved manifest hashes.

    Runtime must confirm that the package bytes currently on disk are exactly the
    HUMAN APPROVED payload declared by the manifest. Any problem is fatal: no
    warning-and-continue, no hash regeneration, no acceptance of new files.

    Checks:
      1. manifest.artifact_paths present
      2. manifest.artifact_sha256 present
      3. both maps have identical keys
      4. each artifact exists and is a regular file
      5. each artifact resolves inside mechanism_library_root
      6. ``../`` / absolute-path escapes rejected
      7-8. SHA-256 of every artifact == manifest hash
    """
    problems: list[str] = []
    paths = manifest.get("artifact_paths")
    hashes = manifest.get("artifact_sha256")
    if not isinstance(paths, dict) or not paths:
        return ["manifest.artifact_paths missing or empty"]
    if not isinstance(hashes, dict) or not hashes:
        return ["manifest.artifact_sha256 missing or empty"]
    if set(paths) != set(hashes):
        return ["artifact_paths/artifact_sha256 key mismatch: "
                f"missing_in_paths={sorted(set(hashes) - set(paths))} "
                f"missing_in_hashes={sorted(set(paths) - set(hashes))}"]
    root_resolved = root.resolve()
    for name in sorted(paths):
        declared = paths[name]
        parts = Path(declared).parts
        if Path(declared).is_absolute() or ".." in parts:
            problems.append(f"{name}: path escape rejected ({declared})")
            continue
        # manifest may declare repo-relative paths (packages/mechanism-library/v1.7.0/x)
        # or package-relative paths (x); resolve both deterministically.
        resolved: Path | None = None
        for cand in (root / declared, root / Path(declared).name):
            if cand.is_file():
                resolved = cand.resolve()
                break
        if resolved is None:
            problems.append(f"{name}: artifact missing or not a regular file ({declared})")
            continue
        if not resolved.is_relative_to(root_resolved):
            problems.append(f"{name}: resolved path outside mechanism_library_root ({declared})")
            continue
        actual = hashlib.sha256(resolved.read_bytes()).hexdigest()
        expected = hashes[name]
        if actual != expected:
            problems.append(f"{name}: sha256 mismatch (expected {expected}, actual {actual})")
    return problems


def excluded_recipe_ids(manifest: dict) -> set[str]:
    excluded = set()
    for entry in manifest.get("excluded_assets") or []:
        asset_id = entry.get("asset_id")
        if asset_id:
            excluded.add(asset_id)
        for aid in entry.get("asset_ids") or []:
            excluded.add(aid)
    return excluded


def build_tag_map(pkg: dict) -> dict[str, set[str]]:
    tags: dict[str, set[str]] = {}
    for tag, ids in (pkg["slot_index"].get("retrieval_tags") or {}).items():
        for fid in ids:
            tags.setdefault(fid, set()).add(tag)
    return tags


def family_record(f: dict, pkg: dict, tags: dict[str, set[str]], matched_via: str | None) -> dict:
    links_by_pair = pkg["adjacency"]["families"].get(f["family_id"], {})
    return {
        "asset_type": FAMILY,
        "family_id": f["family_id"],
        "family_name": f.get("family_name"),
        "domain": f.get("domain"),
        "comparison_lane": f.get("comparison_lane"),
        "why": f.get("one_sentence_core"),
        "minimum_definition": f.get("minimum_definition"),
        "hard_invariants": f.get("hard_invariants"),
        "exclusion_boundary": f.get("exclusion_boundary"),
        "termination": f.get("termination_condition"),
        "tags": sorted(tags.get(f["family_id"], set())),
        "compatible_recipe_ids": sorted({
            r["recipe_id"] for r in pkg["recipes"] if f["family_id"] in r.get("source_family_ids", [])
        }),
        "outbound_link_ids": links_by_pair.get("outbound_link_ids", []),
        "inbound_link_ids": links_by_pair.get("inbound_link_ids", []),
        "matched_via": matched_via,
    }


def recipe_record(r: dict) -> dict:
    return {
        "asset_type": RECIPE,
        "recipe_id": r["recipe_id"],
        "recipe_name": r.get("recipe_name"),
        "status": r.get("status"),
        "family_sequence": r.get("family_sequence"),
        "composition_link_ids": r.get("composition_link_ids"),
        "slot_roles": r.get("slot_roles"),
        "why": r.get("creative_value"),
        "entry_condition": r.get("entry_condition"),
        "recurrence_loop": r.get("recurrence_loop"),
        "bridge_requirements": r.get("joint_bridge_conditions"),
        "failure_modes": r.get("failure_modes"),
        "limitations": list(r.get("failure_modes") or []) + list(r.get("joint_bridge_conditions") or []),
    }


def link_record(l: dict) -> dict:
    return {
        "asset_type": LINK,
        "link_id": l["link_id"],
        "source_family_id": l.get("source_family_id"),
        "target_family_id": l.get("target_family_id"),
        "composition_relation": l.get("composition_relation"),
        "source_output": l.get("source_output"),
        "target_trigger_or_input": l.get("target_trigger_or_input"),
        "bridge_condition": l.get("bridge_condition"),
    }


def search(pkg: dict, query: str, slots: list[str], limit: int, asset_types: Iterable[str]) -> dict:
    tokens = tokenize(query)
    tag_map = build_tag_map(pkg)
    excluded_recipes = excluded_recipe_ids(pkg["manifest"])
    held_ids = {h["family_id"] for h in pkg["held"]}
    active_recipe_ids = {r["recipe_id"] for r in pkg["recipes"]}

    # -- recipes: lexical score, then hard filters (dropped/held never returned)
    recipe_hits: list[dict] = []
    if RECIPE in asset_types:
        for r in pkg["recipes"]:
            if r["recipe_id"] in excluded_recipes or r["recipe_id"] not in active_recipe_ids:
                continue  # dropped recipes can never be returned
            s = score(r, RECIPE, tokens)
            if s > 0:
                recipe_hits.append((s, r))
        recipe_hits.sort(key=lambda t: (-t[0], t[1]["recipe_id"]))
        # explicit --slots longline_engine promotes recipes
        if any(SLOT_ALIASES.get(s) == "__recipes__" for s in slots):
            present = {r["recipe_id"] for _, r in recipe_hits}
            for r in pkg["recipes"]:
                if r["recipe_id"] not in present and r["recipe_id"] not in excluded_recipes:
                    recipe_hits.append((0.5, r))
        recipe_hits = recipe_hits[:limit]

    families_by_id = {f["family_id"]: f for f in pkg["families"]}
    # -- families: direct lexical hits + families pulled in via matched recipes
    family_hits: list[dict] = []
    seen_family_ids: set[str] = set()
    if FAMILY in asset_types:
        direct: list[tuple[float, dict]] = []
        for f in pkg["families"]:
            if f["family_id"] in held_ids:
                continue  # held families can never be returned
            enriched = dict(f)
            enriched["tags"] = sorted(tag_map.get(f["family_id"], set()))
            s = score(enriched, FAMILY, tokens)
            if s > 0:
                direct.append((s, f))
        direct.sort(key=lambda t: (-t[0], t[1]["family_id"]))
        for s, f in direct[:limit]:
            if f["family_id"] not in seen_family_ids:
                seen_family_ids.add(f["family_id"])
                family_hits.append(family_record(f, pkg, tag_map, None))
        for _, r in recipe_hits:
            for fid in r.get("source_family_ids") or []:
                if fid in held_ids or fid in seen_family_ids:
                    continue
                f = families_by_id.get(fid)
                if f is not None:
                    seen_family_ids.add(fid)
                    family_hits.append(family_record(f, pkg, tag_map, f"recipe:{r['recipe_id']}"))

    # -- links: lexical hits, restricted to links touched by returned recipes/families when possible
    link_hits: list[dict] = []
    if LINK in asset_types:
        touches = {lid for _, r in recipe_hits for lid in r.get("composition_link_ids") or []}
        scored: list[tuple[float, dict]] = []
        for l in pkg["links"]:
            s = score(l, LINK, tokens)
            if s > 0:
                scored.append((2.0 + s if l["link_id"] in touches else s, l))
        scored.sort(key=lambda t: (-t[0], t[1]["link_id"]))
        link_hits = [link_record(l) for _, l in scored[:limit]]

    return {
        "query": query,
        "slots": slots,
        "results": {FAMILY: family_hits, RECIPE: [recipe_record(r) for _, r in recipe_hits], LINK: link_hits},
        "excluded": {
            "held_family_ids": sorted(held_ids),
            "dropped_recipe_ids": sorted(excluded_recipes & {f"REC-{i:03d}" for i in range(1, 100)} - active_recipe_ids),
        },
    }


def render_md(result: dict) -> str:
    lines = ["# Mechanism Library Search", ""]
    if result.get("query"):
        lines += [f"- Query: {result['query']}", ""]
    for kind in ASSET_TYPES:
        rows = result["results"].get(kind) or []
        lines += [f"## {kind} ({len(rows)})", ""]
        for row in rows:
            if kind == FAMILY:
                lines += [f"- **{row['family_id']}** {row.get('family_name')} [{row.get('domain')}/{row.get('comparison_lane')}]",
                          f"  - why: {row.get('why')}",
                          f"  - recipes: {', '.join(row.get('compatible_recipe_ids') or [])}"]
            elif kind == RECIPE:
                lines += [f"- **{row['recipe_id']}** {row.get('recipe_name')} ({row.get('status')})",
                          f"  - entry: {row.get('entry_condition')}",
                          f"  - why: {row.get('why')}",
                          f"  - failure_modes: {'; '.join(row.get('failure_modes') or [])}"]
            else:
                lines += [f"- **{row['link_id']}** {row.get('source_family_id')} -> {row.get('target_family_id')}",
                          f"  - bridge: {row.get('bridge_condition')}"]
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Search the versioned RMF mechanism library (read-only).")
    parser.add_argument("--library", required=True, help="mechanism_library_root (package directory)")
    parser.add_argument("--query", default="", help="functional query text")
    parser.add_argument("--slots", default="", help="comma-separated mechanism slots (optional)")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--format", choices=("json", "jsonl", "md"), default="json")
    parser.add_argument("--asset-types", default=",".join(ASSET_TYPES),
                        help="comma-separated subset of family,recipe,link")
    parser.add_argument("--allow-staging", action="store_true",
                        help="explicitly allow an INSTALLATION_STAGING package (active_promotion=false); "
                             "for integration tests / installation verification only")
    args = parser.parse_args(argv)

    root = Path(args.library).expanduser()
    if not root.is_dir() or not (root / "manifest.json").is_file():
        json.dump({"gap": GAP_UNAVAILABLE, "library": str(root)}, sys.stdout, ensure_ascii=False)
        print()
        return EXIT_UNAVAILABLE

    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    active = manifest.get("active_promotion") is True

    # Manifest consistency: an active package must be both flagged active AND
    # marked ACTIVE_PROMOTED. active_promotion=true with a staging status is an
    # inconsistent manifest and must never be used (in any mode).
    if active and manifest.get("status") != STATUS_ACTIVE_PROMOTED:
        json.dump({"gap": GAP_MANIFEST_INVALID, "library": str(root),
                    "status": manifest.get("status"),
                    "active_promotion": manifest.get("active_promotion"),
                    "detail": "active_promotion=true requires status=ACTIVE_PROMOTED"},
                   sys.stdout, ensure_ascii=False)
        print()
        return EXIT_INTEGRITY

    if not active and not args.allow_staging:
        json.dump({"gap": GAP_NOT_ACTIVE, "library": str(root),
                    "status": manifest.get("status"),
                    "hint": "pass --allow-staging for integration tests / installation verification"},
                   sys.stdout, ensure_ascii=False)
        print()
        return EXIT_NOT_ACTIVE

    # Integrity gate runs in EVERY mode: --allow-staging bypasses only the
    # active-promotion gate, never integrity verification.
    problems = verify_package_integrity(root, manifest)
    if problems:
        json.dump({"gap": GAP_INTEGRITY, "library": str(root), "problems": problems},
                   sys.stdout, ensure_ascii=False, indent=2)
        print()
        return EXIT_INTEGRITY

    pkg = load_package(root)
    asset_types = tuple(t.strip() for t in args.asset_types.split(",") if t.strip() in ASSET_TYPES) or ASSET_TYPES
    slots = [s.strip() for s in args.slots.split(",") if s.strip()]
    result = search(pkg, args.query, slots, max(1, args.limit), asset_types)
    result["library_status"] = "ACTIVE" if manifest.get("active_promotion") is True else "STAGING"
    result["package_version"] = manifest.get("package_version")

    if args.format == "md":
        print(render_md(result))
    elif args.format == "jsonl":
        for kind in ASSET_TYPES:
            for row in result["results"][kind]:
                print(json.dumps(row, ensure_ascii=False))
    else:
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        print()
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
