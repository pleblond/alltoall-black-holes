"""Run the Cayley-growth probe (frozen prereg: docs/cayley-prereg.md)."""
import json
import os
import time

from bh_graph.cayley_growth import (GROUPS, PREDICTED, ball_volumes,
                                    fit_growth_degree, kappa_interior_sample)

R_FIT, R_KAPPA = 12, 8
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "results", "cayley")


def main():
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    verdicts = {}
    for group in GROUPS:
        vols = ball_volumes(group, R_FIT)
        fit = fit_growth_degree(vols)
        pred = PREDICTED[group]
        passed = abs(fit["d"] - pred) <= 0.35 and fit["r2"] >= 0.95
        kap = kappa_interior_sample(group, R_KAPPA)
        verdicts[group] = {
            "predicted": pred, "d": fit["d"], "r2": fit["r2"],
            "pass": bool(passed), "N_R12": vols[R_FIT],
            "kappa_interior": kap,
        }
        with open(os.path.join(OUT, f"{group}.json"), "w") as f:
            json.dump({"volumes": vols, "fit": fit,
                       "kappa_interior": kap}, f, indent=1)
    verdicts["elapsed_s"] = time.time() - t0
    verdicts["calibration_z3"] = ("METHOD-OK" if verdicts["z3"]["pass"]
                                  else "METHOD-FAIL")
    with open(os.path.join(OUT, "verdicts.json"), "w") as f:
        json.dump(verdicts, f, indent=1)
    for group in GROUPS:
        v = verdicts[group]
        print(f"{group}: d={v['d']:.3f} R2={v['r2']:.4f} "
              f"pred={v['predicted']} -> {'PASS' if v['pass'] else 'FAIL'} "
              f"(N={v['N_R12']}, kap={v['kappa_interior']['mean']:.3f}+-"
              f"{v['kappa_interior']['sem']:.3f})")
    print("calibration:", verdicts["calibration_z3"],
          f"elapsed={verdicts['elapsed_s']:.1f}s")


if __name__ == "__main__":
    main()
