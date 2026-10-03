"""DIM-3-1 blind seal writer (pre-J3 workflow guard).

Reads the frozen controls record (freeze.json) and the sealed blind
artifact (blind over ALL cells 0..15, ladders + no claims), and writes
the seal file consumed by dim31_analyze.py j3. Refuses to seal when
the freeze carries estimator debt (controls failed -> ESTIMATOR-DEBT
path, no J3 run).

The seal binds blind_sha256 + freeze_sha256 + git rev so the J3 phase
can verify it is scoring the exact frozen apparatus on the exact
sealed data. Deterministic; no measurements are read or written.
"""

import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dim31_analyze import CONTROL_CELLS, J3_CELLS


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def git_rev() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True,
            check=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--blind", required=True,
                    help="sealed blind artifact (cells 0..15)")
    ap.add_argument("--freeze", required=True,
                    help="frozen controls record")
    ap.add_argument("--out", required=True, help="seal output path")
    args = ap.parse_args()

    with open(args.freeze) as f:
        freeze = json.load(f)
    if freeze.get("debt"):
        raise SystemExit(
            f"refusing seal: freeze debt non-empty ({len(freeze['debt'])} "
            "items) -> ESTIMATOR-DEBT path, no J3 run")
    with open(args.blind) as f:
        blind = json.load(f)
    want = {str(c) for c in CONTROL_CELLS} | {str(c) for c in J3_CELLS}
    have = set(blind.get("cells", {}))
    if want - have:
        raise SystemExit(
            f"refusing seal: blind missing cells {sorted(want - have)} "
            "(sealed blind must cover all cells for ladder integrity)")
    seal = {
        "blind_sha256": sha256_file(args.blind),
        "freeze_sha256": sha256_file(args.freeze),
        "git_rev": git_rev(),
        "created_utc": datetime.datetime.now(
            datetime.timezone.utc).isoformat(),
        "cells": sorted(want, key=int),
        "note": "DIM-3-1 blind seal: j3 phase verifies blind_sha256",
    }
    with open(args.out, "w") as f:
        json.dump(seal, f, indent=2, sort_keys=True)
    print(f"seal written: {args.out} blind={seal['blind_sha256'][:12]}...")


if __name__ == "__main__":
    main()
