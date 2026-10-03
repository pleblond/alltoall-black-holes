"""DIM-3-1 STAGE-BLIND analyzer (frozen per DIM31-PREREG).

Reads ONLY opaque measurement files (integer cell id, integer set id,
S-id pair records) plus an optional frozen bars file. It NEVER loads
concealed maps, tags, graphs, or coordinates (firewall-audited: import
scan + token scan of THIS file in tests/test_dim31.py).

Per (cell, set) the analyzer runs the FROZEN OBS-1 estimators
(analyze_obs1_blind, imported verbatim) and the DIM-3-1 blind local
ladder (dim31.local_ball_stress per channel W/D/C). With --bars, it
also emits local-d* claims; without, claims are null (ladder only).
The reveal stage refuses to run unless the recorded hash matches.
"""

import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
from analyze_obs1_blind import _jsonable, analyze_cell_set

from bh_graph import dim31

LADDER_CHANNELS = ("W", "D", "C")


def analyze_ladder(cell_set: dict, bars=None) -> dict:
    """Blind local ladder + optional d* claims (opaque matrices only)."""
    out = {}
    for ch in LADDER_CHANNELS:
        D = np.asarray(cell_set["probes"][ch]["D"], dtype=float)
        lad = dim31.local_ball_stress(D)
        rec = {"S": lad["S"], "n_balls": lad["n_balls"], "k": lad["k"],
               "ladder_ok": lad["ok"], "dstar": None, "dstar_pass": False}
        if bars is not None and ch in bars:
            claim = dim31.local_dstar(D, bars[ch])
            rec["dstar"] = claim["dstar"]
            rec["dstar_pass"] = claim["pass"]
            rec["dstar_reason"] = claim["reason"]
        out[ch] = rec
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--measdir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cells", type=int, nargs="+", required=True)
    ap.add_argument("--sets", type=int, nargs="+", required=True)
    ap.add_argument("--bars", default=None)
    args = ap.parse_args()
    bars = None
    if args.bars:
        with open(args.bars) as f:
            bars = json.load(f)
    out = {"cells": {}, "meta": {"cells": args.cells, "sets": args.sets,
                                 "bars": bars is not None}}
    for c in args.cells:
        out["cells"][str(c)] = {"sets": {}}
        for s in args.sets:
            with open(os.path.join(
                    args.measdir,
                    f"dim31_meas_cell{c}_s{s}.json")) as f:
                meas = json.load(f)
            assert int(meas["cell"]) == c and int(meas["set"]) == s
            assert int(meas["n"]) == 64
            workup = analyze_cell_set(meas)
            workup["ladder"] = analyze_ladder(workup, bars)
            out["cells"][str(c)]["sets"][str(s)] = workup
            print(f"blind cell={c} set={s} done", flush=True)
    blob = json.dumps(_jsonable(out), sort_keys=True).encode()
    with open(args.out, "w") as f:
        f.write(blob.decode())
    digest = hashlib.sha256(blob).hexdigest()
    with open(args.out + ".sha256", "w") as f:
        f.write(digest + "\n")
    print(f"blind artifact: {args.out} sha256={digest}")


if __name__ == "__main__":
    main()
