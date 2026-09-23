#!/usr/bin/env python3
"""Dispatch the bundled specialist validators without external Skill dependencies."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SPECIALISTS = {
    "chapter-emotion-miner": "chapter-emotion-miner/validate_outputs.py",
    "golden-finger-miner": "golden-finger-miner/validate_outputs.py",
    "worldbuilding-miner": "worldbuilding-miner/validate_outputs.py",
    "cultivation-system-miner": "cultivation-system-miner/validate_outputs.py",
    "character-function-miner": "character-function-miner/validate_outputs.py",
    "plotline-miner": "plotline-miner/validate_outputs.py",
    "opening-miner": "opening-miner/validate_outputs.py",
    "arc-structure-miner": "arc-structure-miner/validate_outputs.py",
    "plot-mechanism-miner": "plot-mechanism-miner/validate_outputs.py",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Dispatch a bundled novel DNA specialist validator.")
    parser.add_argument("--specialty", required=True, choices=sorted(SPECIALISTS))
    parser.add_argument("--kind", required=True, help="Validator record kind, for example per_book or canonical.")
    parser.add_argument("target", type=Path, help="JSONL file or directory to validate.")
    parser.add_argument("validator_args", nargs=argparse.REMAINDER, help="Additional arguments passed to the specialist validator.")
    args = parser.parse_args()
    validator = ROOT / "scripts" / "specialists" / SPECIALISTS[args.specialty]
    command = [sys.executable, str(validator), str(args.target)]
    if args.specialty != "golden-finger-miner":
        command.extend(["--kind", args.kind])
    command.extend(args.validator_args)
    # Preserve the caller's working directory so relative targets, manifests,
    # and --workspace-root keep their documented project-relative meaning.
    completed = subprocess.run(command)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
