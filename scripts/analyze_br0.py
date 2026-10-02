"""BR-0 verdict analysis: preregistered decision tree over data/br0_landscape.json.

Implements BR0-PREREG (docs/DEFERRED.md) mechanically: C0/C1 hard gates,
C4 campaign check, SELECTIVE bars (i)-(iv), C5b sampled-vs-exhaustive,
A/B/C/D/E operationalization. Prints the verdict table; exits nonzero
on any hard-gate failure. No thresholds are fitted here -- all bars are
preregistered literals.
"""

import json
import math
import sys

C0_BAR = 1e-9
C4_BAR = 1e-12
FLOOR = 1e-4
F_NEAR_BAR = 0.01
RATIO_BAR = 5.0
SEED_SPREAD_BAR = 0.20
FLAT_F0_BAR = 0.99


def fail(msg):
    print("HARD-GATE FAIL:", msg)
    sys.exit(1)


def main(path="data/br0_landscape.json"):
    with open(path) as f:
        out = json.load(f)
    sampled = {s["tag"]: s for s in out["sampled"]}
    exh = {s["tag"]: s for s in out["exhaustive"]}

    print("== C0 (campaign full-H identity, bar 1e-9) ==")
    for c in out["c0"]:
        flag = "PASS" if c["max_abs_diff"] < C0_BAR else "FAIL"
        print(f"  {c['tag']:16s} {c['max_abs_diff']:.2e} {flag}")
        if flag == "FAIL":
            fail(f"C0 {c['tag']}")
    print("== C1 (V0 exact null, all 600k moves == 0.0) ==")
    v0 = sampled["V0"]
    v0_bad = 0
    for s, r in v0["seeds"].items():
        g = r["global"]
        if not (g["f_neg"] == 0.0 and g["f_pos"] == 0.0 and g["f_zero"] == 1.0):
            v0_bad += 1
        print(f"  seed {s}: f-={g['f_neg']} f+={g['f_pos']} f0={g['f_zero']}")
    if v0_bad:
        fail("C1 V0 nonzero")
    print("== C4 (E1 vs E2 identical-move invariance, bar 1e-12) ==")
    c4 = out["c4"]["max_abs_diff_E1_E2"]
    print(f"  max|dE_E1 - dE_E2| = {c4:.2e} {'PASS' if c4 < C4_BAR else 'FAIL'}")
    if c4 >= C4_BAR:
        fail("C4 momentum-reversal difference")

    print("== C5b (sampled vs exhaustive, 3xSE + 5e-4) ==")
    for s_tag, x_tag in (("S-J2-P", "X-J2-P"), ("S-R-P", "X-R-P")):
        fe = exh[x_tag]["record"]["global"]["f_neg"]
        fs = sampled[s_tag]["seeds"]["0"]["global"]["f_neg"]
        n = sampled[s_tag]["seeds"]["0"]["n_moves"]
        se = math.sqrt(fe * (1 - fe) / n)
        ok = abs(fs - fe) < 3 * se + 5e-4
        print(f"  {s_tag}: samp={fs:.5f} exact={fe:.5f} SE={se:.2e} "
              f"{'PASS' if ok else 'FAIL'}")
        if not ok:
            fail(f"C5b {s_tag}")

    print("== SELECTIVE bars (E1 J2-L28) ==")
    e1 = sampled["E1"]
    f_near = [e1["seeds"][s]["near"]["f_neg"] for s in ("0", "1", "2")]
    f_far = [e1["seeds"][s]["far"]["f_neg"] for s in ("0", "1", "2")]
    f_g = [e1["seeds"][s]["global"]["f_neg"] for s in ("0", "1", "2")]
    mn, mx = min(f_near), max(f_near)
    spread = (mx - mn) / mx if mx else 0.0
    ratio = mx / max(min(f_far), FLOOR)
    print(f"  f-_near seeds: {[f'{x:.5f}' for x in f_near]}")
    print(f"  f-_far  seeds: {[f'{x:.5f}' for x in f_far]}")
    print(f"  f-_glob seeds: {[f'{x:.5f}' for x in f_g]}")
    b2 = mx > F_NEAR_BAR
    b3 = ratio > RATIO_BAR
    b4 = spread < SEED_SPREAD_BAR
    print(f"  (ii) f-_near > 0.01: {mx:.5f} {'PASS' if b2 else 'FAIL'}")
    print(f"  (iii) ratio > 5: {ratio:.2f} {'PASS' if b3 else 'FAIL'}")
    print(f"  (iv) seed spread < 20%: {spread:.3f} {'PASS' if b4 else 'FAIL'}")

    print("== E-side states (seed 0) ==")
    for tag in ("E1", "E2", "E3b", "E3p", "E3r", "E3t"):
        s0 = sampled[tag]["seeds"]["0"]
        print(f"  {tag:4s} E={sampled[tag]['e_psi']:9.4f} "
              f"f-_n={s0['near']['f_neg']:.4f} f-_f={s0['far']['f_neg']:.4f} "
              f"f0_g={s0['global']['f_zero']:.4f} "
              f"tail_n={s0['near']['neg_tail_mean']:.2e} "
              f"tail_f={s0['far']['neg_tail_mean']:.2e} conn={s0['frac_connected']:.4f}")
    print("== V1U secondary (seed 0) ==")
    u0 = sampled["V1U"]["seeds"]["0"]
    print(f"  E={sampled['V1U']['e_psi']:.4f} f-={u0['global']['f_neg']} "
          f"f0={u0['global']['f_zero']}")

    print("== VERDICT ==")
    all_flat = all(sampled[t]["seeds"]["0"]["global"]["f_zero"] > FLAT_F0_BAR
                   for t in ("E1", "E2", "E3b", "E3p", "E3r", "E3t"))
    if b2 and b3 and b4:
        print("BR0-D SELECTIVE (+ BR0-E vacuum-half debt, pre-filed)")
    elif all_flat:
        print("BR0-A FLAT (+ BR0-E vacuum-half debt, pre-filed)")
    else:
        print("BR0-C EXCITATION-BLIND (+ BR0-E vacuum-half debt, pre-filed)")
    print("(BR0-B structurally unreachable given V1-NONE + uniform-flat; filed)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/br0_landscape.json")
