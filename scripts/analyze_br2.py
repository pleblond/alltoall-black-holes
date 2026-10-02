"""BR-2 verdict analysis: preregistered bars over data/br2_phase.json.

Implements BR2-PREREG mechanically: BR-2A replication (bitwise vs
data/br0_landscape.json), sweep bars P1-P6, quadrature Q1-Q2, even/odd
EO1-EO4, G-theorem G1-G3, controls C0/C1/C4 spots. Prints the ladder
verdict; exits nonzero on any hard-gate failure. All bars are
preregistered literals; nothing is fitted here.
"""

import json
import math
import sys

import numpy as np


def fail(msg):
    print("HARD-GATE FAIL:", msg)
    sys.exit(1)


def RB(cells):
    return cells["fn"]["f_neg"] - cells["nf"]["f_neg"]


def pearson(xs, ys):
    xs = np.array(xs, dtype=float)
    ys = np.array(ys, dtype=float)
    return float(np.corrcoef(xs, ys)[0, 1])


def main(path="data/br2_phase.json", br0_path="data/br0_landscape.json"):
    out = json.load(open(path))
    br0 = json.load(open(br0_path))
    br0s = {s["tag"]: s for s in br0["sampled"]}
    reps = {r["tag"]: r for r in out["reps"]}
    PHI = out["meta"]["phi_grid"]

    print("== BR-2A replication (bitwise vs BR-0) ==")
    for rep_tag, br0_tag in (("E1-rep", "E1"), ("E3p-rep", "E3p")):
        ok = True
        for s in ("0", "1", "2"):
            if reps[rep_tag]["seeds"][s] != br0s[br0_tag]["seeds"][s]:
                ok = False
        print(f"  {rep_tag}: {'BITWISE-IDENTICAL' if ok else 'MISMATCH'}")
        if not ok:
            fail(f"BR-2A {rep_tag}")
    e2b0 = reps["E2-rep"]["seeds"]["0"] == br0s["E2"]["seeds"]["0"]
    print(f"  E2-rep seed0: {'BITWISE-IDENTICAL' if e2b0 else 'MISMATCH'}")
    if not e2b0:
        fail("BR-2A E2-rep")
    a3 = RB(reps["E1-rep"]["seeds"]["0"]["cells"]) > 0.2
    a4 = RB(reps["E3p-rep"]["seeds"]["0"]["cells"]) < -0.1
    print(f"  (A3) bonding fn-nf>0.2: {'PASS' if a3 else 'FAIL'}; "
          f"(A4) antibonding R<-0.1: {'PASS' if a4 else 'FAIL'}")
    if not (a3 and a4):
        fail("BR-2A anatomy")

    print("== sweep bars (J2-L28 sampled, all 3 seeds) ==")
    sw = out["sweeps_sampled"][0]["cells"]
    Tall = True
    for s in ("0", "1", "2"):
        R = [RB(sw[str(p)]["seeds"][s]["cells"]) for p in PHI]
        cosv = [math.cos(p) for p in PHI]
        p1 = R[0] > 0 and R[4] < 0
        p2 = (abs(R[2]) < 0.25 * max(abs(R[0]), abs(R[4]))
              and abs(R[6]) < 0.25 * max(abs(R[0]), abs(R[4])))
        p3 = (all(R[i] >= R[i + 1] for i in range(4))
              and all(R[i] <= R[i + 1] for i in range(4, 7)) and R[7] <= R[0])
        p4 = (abs(R[1] - R[7]) < 1e-4 and abs(R[3] - R[5]) < 1e-4)
        p5 = pearson(R, cosv) > 0.9
        fnf0 = sw[str(PHI[0])]["seeds"][s]["cells"]["nf"]["f_neg"]
        fnf2 = sw[str(PHI[2])]["seeds"][s]["cells"]["nf"]["f_neg"]
        p6 = fnf0 < 5e-4 and fnf2 > 0.2
        ok = p1 and p5
        Tall = Tall and ok
        print(f"  seed {s}: R={[f'{x:.3f}' for x in R]}")
        print(f"    P1:{'P' if p1 else 'F'} P2:{'P' if p2 else 'F'} "
              f"P3:{'P' if p3 else 'F'} P4:{'P' if p4 else 'F'} "
              f"P5:r={pearson(R, cosv):.4f}{'P' if p5 else 'F'} "
              f"P6:{'P' if p6 else 'F'} -> {'BOND' if ok else 'NO'}")
    print("== sweep bars (exhaustive, confirmatory) ==")
    for swx in out["sweeps_exhaustive"]:
        cells = swx["cells"]
        R = [RB(cells[str(p)]["record"]["cells"]) for p in PHI]
        cosv = [math.cos(p) for p in PHI]
        p1 = R[0] > 0 and R[4] < 0
        p5 = pearson(R, cosv) > 0.9
        fnf0 = cells[str(PHI[0])]["record"]["cells"]["nf"]["n_neg"]
        fnf2 = cells[str(PHI[2])]["record"]["cells"]["nf"]["f_neg"]
        p6 = fnf0 == 0 and fnf2 > 0.2
        print(f"  {swx['tag']}: R={[f'{x:.3f}' for x in R]} "
              f"P1:{'P' if p1 else 'F'} P5:r={pearson(R, cosv):.4f}{'P' if p5 else 'F'} "
              f"P6:{'P' if p6 else 'F'}")

    print("== quadrature ==")
    js = [sw[str(p)]["currents"]["J_stag"] for p in PHI]
    sinv = [math.sin(p) for p in PHI]
    q1 = pearson(js, sinv) > 0.99
    je1 = abs(reps["E1-rep"]["currents"]["J_net_ax0"])
    q2 = True
    for p in PHI:
        c = sw[str(p)]["currents"]
        if not (abs(c["J_net_ax0"]) < 0.10 * je1 and abs(c["J_net_ax1"]) < 0.10 * je1):
            q2 = False
    print(f"  (Q1) J_stag~sin r={pearson(js, sinv):.5f} {'PASS' if q1 else 'FAIL'}")
    print(f"  (Q2) stagger net-null (<10% E1): {'PASS' if q2 else 'FAIL'}")

    print("== even/odd ==")
    b1 = reps["E1-rep"]["seeds"]["0"]["bond_B_edges"]
    b2 = reps["E2-rep"]["seeds"]["0"]["bond_B_edges"]
    eo1 = max(abs(u - v) for u, v in zip(b1, b2)) < 1e-12
    c1, c2 = reps["E1-rep"]["currents"], reps["E2-rep"]["currents"]
    eo2 = (abs(c2["J_net_ax0"] + c1["J_net_ax0"]) < 1e-12
           and abs(c2["J_net_ax1"] + c1["J_net_ax1"]) < 1e-12)
    eo3 = (c1["J_net_ax0"] > 0 and abs(c1["J_net_ax1"]) < 0.05 * abs(c1["J_net_ax0"])
           and c2["J_net_ax0"] < 0 and abs(c2["J_net_ax1"]) < 0.05 * abs(c2["J_net_ax0"]))
    eo4 = abs(c2["J_stag"] + c1["J_stag"]) < 1e-12
    print(f"  EO1 B-matched: {'P' if eo1 else 'F'} EO2 J-odd: {'P' if eo2 else 'F'} "
          f"EO3 v_g-sign: {'P' if eo3 else 'F'} EO4 stag-odd: {'P' if eo4 else 'F'}")
    eo = eo1 and eo2 and eo3 and eo4

    print("== G-theorem ==")
    for p in out["premise"]:
        r = p["result"]
        print(f"  {p['tag']}: holds={r['holds']} margin={r['margin']:.3f}")
    g1 = out["premise"][0]["result"]["holds"]
    g2 = all(out["strict"][0]["cells"][s]["cells"]["nf"]["n_neg"] == 0
             for s in ("0", "1", "2"))
    g3 = all(reps["E1-rep"]["seeds"][s]["cells"]["nf"]["n_neg"] == 0
             for s in ("0", "1", "2"))
    print(f"  G1 premise: {'P' if g1 else 'F'} G2 strict-zero: {'P' if g2 else 'F'} "
          f"G3 rep-zero: {'P' if g3 else 'F'}")

    print("== controls ==")
    c0 = all(c["max_abs_diff"] < 1e-9 for c in out["c0"])
    print(f"  C0: {'PASS' if c0 else 'FAIL'}")
    if not c0:
        fail("C0")
    rot = out["controls"]["global_phase"]["cells"]
    ref = sw[str(float(np.pi) / 4)]["seeds"]["0"]["cells"]
    c1ok = all(abs(rot[t]["f_neg"] - ref[t]["f_neg"]) <= 1e-5
               and abs(rot[t]["f_zero"] - ref[t]["f_zero"]) <= 1e-5
               for t in ("nn", "nf", "fn", "ff"))
    print(f"  C1-spot global-phase R-identical: {'PASS' if c1ok else 'FAIL'}")
    if not c1ok:
        fail("C1-spot")
    rs = out["controls"]["rescale_x2"]["cells"]
    rf = sw[str(0.0)]["seeds"]["0"]["cells"]
    c4ok = all(rs[t]["f_neg"] == rf[t]["f_neg"] for t in ("nn", "nf", "fn", "ff"))
    print(f"  C4 rescale R-identical: {'PASS' if c4ok else 'FAIL'}")
    if not c4ok:
        fail("C4-rescale")

    print("== LADDER ==")
    if not Tall:
        print("BR2-NULL (+EO)" if eo else "BR2-NULL")
    elif q1 and q2:
        print("BR2-QUADRATURE (+EO)" if eo else "BR2-QUADRATURE")
    else:
        print("BR2-BOND (+EO)" if eo else "BR2-BOND")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/br2_phase.json",
         sys.argv[2] if len(sys.argv) > 2 else "data/br0_landscape.json")
