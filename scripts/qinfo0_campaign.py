"""Q-INFO-0 campaign (frozen QINFO0-PREREG battery, pre-data).

Runs the small deterministic battery only (spec section O): 11 pair
cells, 4 multi-entry sets, 3 graph-level STORE roundtrips, frozen
phase/scale probes, and the banked-formula comparison. No RNG, no
parameter scan, no fitting. Output: data/qinfo0/qinfo0_ledger.json.
Gates applied by scripts/qinfo0_analyze.py.
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import qinfo0 as q0

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "qinfo0",
                   "qinfo0_ledger.json")


def _sanitize(x):
    if isinstance(x, dict):
        return {str(k): _sanitize(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_sanitize(v) for v in x]
    if isinstance(x, complex):
        return {"re": float(x.real), "im": float(x.imag)}
    try:
        import numpy as np

        if isinstance(x, np.ndarray):
            return [_sanitize(v) for v in x.tolist()]
        if isinstance(x, (np.floating, np.integer)):
            return float(x)
        if isinstance(x, np.bool_):
            return bool(x)
    except Exception:
        pass
    if isinstance(x, float) and (x != x or x in (float("inf"),
                                                 float("-inf"))):
        return None
    return x


def _git_sha() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"],
                             capture_output=True, text=True,
                             cwd=os.path.dirname(__file__),
                             timeout=10)
        return out.stdout.strip()
    except Exception:
        return "unknown"


def main() -> int:
    t0 = time.time()
    battery = q0.run_battery()
    ledger = {
        "campaign": "Q-INFO-0",
        "prereg": "docs/qinfo0-prereg.md (FROZEN pre-data)",
        "provenance": {
            "git_sha": _git_sha(),
            "platform": platform.platform(),
            "python": platform.python_version(),
        },
        "elapsed_s": time.time() - t0,
        "battery": _sanitize(battery),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        json.dump(ledger, fh, indent=1, sort_keys=True)
    n_pairs = len(battery.get("pairs", []))
    print(f"wrote {OUT} pairs={n_pairs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
