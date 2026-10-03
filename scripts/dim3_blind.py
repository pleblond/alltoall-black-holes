"""DIM-3-0 STAGE-BLIND analyzer (frozen per DIM3-PREREG).

Reads ONLY opaque measurement files (integer cell id, integer set id,
S-id pair records). It NEVER loads concealed maps, tags, graphs, or
coordinates (firewall-audited: import scan + token scan of THIS file in
tests/test_dim3.py).

Per (cell, set, probe in W/D/P/composite) the analyzer reconstructs the
observer geometry with the FROZEN OBS-1 estimators (analyze_obs1_blind,
imported verbatim) and writes the frozen blind artifact plus its sha256.
The reveal stage refuses to run unless the recorded hash matches.
"""

import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from analyze_obs1_blind import _jsonable, analyze_cell_set  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--measdir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cells", type=int, nargs="+", required=True)
    ap.add_argument("--sets", type=int, nargs="+", required=True)
    args = ap.parse_args()
    out = {"cells": {}, "meta": {"cells": args.cells, "sets": args.sets}}
    for c in args.cells:
        out["cells"][str(c)] = {"sets": {}}
        for s in args.sets:
            with open(os.path.join(
                    args.measdir,
                    f"dim3_meas_cell{c}_s{s}.json")) as f:
                meas = json.load(f)
            assert int(meas["cell"]) == c and int(meas["set"]) == s
            assert int(meas["n"]) == 64
            out["cells"][str(c)]["sets"][str(s)] = analyze_cell_set(meas)
            print(f"blind cell={c} set={s} done", flush=True)
    blob = json.dumps(_jsonable(out), sort_keys=True).encode()
    with open(args.out, "w") as f:
        f.write(blob.decode())
    digest = hashlib.sha256(blob).hexdigest()
    with open(args.out + ".sha256", "w") as f:
        f.write(digest)
    print(f"blind artifact: {args.out} sha256={digest}")


if __name__ == "__main__":
    main()
