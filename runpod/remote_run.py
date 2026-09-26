"""Remote campaign entry point (runs ON the pod, same code path as tests)."""
from __future__ import annotations

import argparse
import json
import os
import sys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-shell", type=int, default=800)
    ap.add_argument("--n-shells", type=int, default=10)
    ap.add_argument("--beta", type=float, required=True)
    ap.add_argument("--graphs", type=int, default=4)
    ap.add_argument("--seed0", type=int, default=0)
    ap.add_argument("--max-per-shell", type=int, default=8)
    ap.add_argument("--eps", type=float, default=0.01)
    ap.add_argument("--backend", default="auto")
    ap.add_argument("--out", required=True)
    ap.add_argument("--save-profiles", action="store_true")
    ap.add_argument("--workers", type=int, default=None,
                    help="process workers (default: auto; set to vCPU allocation on pods)")
    args = ap.parse_args()

    sys.path.insert(0, os.path.expanduser("~/alltoall-black-holes/src"))
    from bh_graph import shellscale as H

    r = H.campaign(args.per_shell, args.n_shells, args.graphs, True,
                   args.beta, args.seed0, args.max_per_shell, args.eps,
                   args.backend, args.workers, True, args.save_profiles)
    H.save_artifact(r, args.out)
    print(json.dumps({"mean": r["mean"], "std": r["std"], "sem": r["sem"],
                      "stacked_p": r["stacked_fit"]["p"],
                      "r2": r["stacked_fit"]["r2"],
                      "elapsed_s": r["elapsed_s"], "out": args.out}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
