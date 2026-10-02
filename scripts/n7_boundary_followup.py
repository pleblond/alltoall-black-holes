"""TIME-0 SUPPLEMENTARY (post-data): N<=7 boundary-effect quantification.

NOT part of the frozen campaign (does not affect the ladder verdict).
Motivation: headline N<=6 drops all N=6->7 splits, visibly inflating
T=2 uniqueness for N=6 starts (0.644 vs 0.028 at N=5). This reruns the
headline-grid census (all N<=6 starts x all N<=6 ends, T in {2,3,4})
inside the N<=7 universe (996 classes), where N=6 splits are restored,
plus the full 996x996 census. Compares subset-matched f_unique.

Beast-side: PYTHONPATH=src python3 scripts/n7_boundary_followup.py
"""

from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import time0  # noqa: E402


def main():
    t0 = time.time()
    print("[n7] building N<=7 universe + transitions ...", flush=True)
    uni7 = time0.tiny_universe(1, 7)
    tra7 = time0.canonical_transitions(uni7)
    adj7, cids7 = tra7["adj"], tra7["cids"]
    print(f"[n7] classes={len(uni7)} edges={sum(len(v) for v in adj7.values())} "
          f"dropped_n8={tra7['dropped_n7']} ({round(time.time()-t0,1)}s)", flush=True)
    starts6 = [c for c in cids7 if c[0] <= 6]
    out = {"n_classes_7": len(uni7), "dropped_n8": tra7["dropped_n7"],
           "subset6": {}, "full7": {}}
    for T in (2, 3, 4):
        c6 = time0.boundary_census(adj7, starts6, T)
        c6["matrix"] = []
        out["subset6"][str(T)] = c6
        print(f"[n7] subset(N<=6 ends) T={T} f_unique={c6['f_unique']:.4f} "
              f"compat={c6['f_compatible']:.4f} max={c6['max_nhist']}", flush=True)
    for T in (2, 3):
        c7 = time0.boundary_census(adj7, cids7, T)
        c7["matrix"] = []
        out["full7"][str(T)] = c7
        print(f"[n7] full(996x996) T={T} f_unique={c7['f_unique']:.4f} "
              f"compat={c7['f_compatible']:.4f} max={c7['max_nhist']}", flush=True)
    # F0-style: initial-boundary totals from the HEADLINE ledger.
    led = json.load(open("data/time0_ledger.json"))
    f0 = {}
    for T, pack in sorted(led["headline"].items()):
        tots = sorted(pack["census"]["per_start_total"].values())
        f0[T] = {"median_nhist_xminus": float(tots[len(tots) // 2]),
                 "max_nhist_xminus": int(max(tots)),
                 "min_nhist_xminus": int(min(tots))}
    out["headline_initial_boundary"] = f0
    print("[n7] headline N_hist(X_-) medians:", {k: v["median_nhist_xminus"] for k, v in f0.items()})
    json.dump(out, open("data/time0_n7_followup.json", "w"), indent=1)
    print(f"[n7] wrote data/time0_n7_followup.json "
          f"({round(time.time()-t0,1)}s) FOLLOWUP_EXIT:0", flush=True)


if __name__ == "__main__":
    main()
