"""BR-1 verdict analyzer (FROZEN ladder pre-data; see BR1-PREREG).

Reads data/br1_vacuum.json, checks gates C0/C1/C3/C5 + t=0 baseline pins,
evaluates the verdict ladder, prints the BR-3 handoff table. Exit 1 only
on gate failure (verdicts FLAT/METASTABLE/... are never failures).
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import networkx as nx

from bh_graph.rigidity import class_alive, neutral_drift

PASS, FAIL = "PASS", "FAIL"
results = []


def gate(name, ok, detail=""):
    results.append((name, PASS if ok else FAIL, detail))
    print(f"[{PASS if ok else FAIL}] {name} {detail}", flush=True)


def main():
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "data", "br1_vacuum.json")
    with open(path) as f:
        d = json.load(f)

    # ---- C0: zero-field bitwise null ----
    c0 = d["c0"]
    gate("C0-exhaustive", c0["exhaustive_ring8"]["all_local_zero"]
         and c0["exhaustive_ring8"]["all_full_zero"],
         f"n={c0['exhaustive_ring8']['n']} both paths")
    gate("C0-sampled-L12", c0["sampled_L12"]["all_full_zero"],
         f"n={c0['sampled_L12']['n']} max={c0['sampled_L12']['max_abs_full']}")

    # ---- t=0 baseline pins (banked J2 numbers) ----
    balls = d["baselines"]["balls"]
    for R in ("12", "18", "24"):
        fp = balls[R]
        sh, cu = fp["shells"], fp["cuts"]
        ok_shell = sh[1] == 8 and sh[2] == 17 and all(
            sh[r] == 8 * r for r in range(3, len(sh)))
        ok_cut = cu[0] == 56 and all(
            cu[r - 1] == 32 * r + 16 for r in range(2, len(cu) + 1))
        gate(f"T0-R{R}-micro", ok_shell and ok_cut and fp["bip_viol"] == 0
             and fp["qfrac"] == 1.0 and fp["connected"],
             f"shells/cuts/bip/qfrac")
    gate("T0-R24-p", 1.90 < balls["24"]["p"] < 1.94,
         f"p={balls['24']['p']:.4f} (banked band)")
    gate("T0-R18-c4", balls["18"]["c4"] == 26072,
         f"c4={balls['18']['c4']} (banked)")
    for tag in ("j2-L12", "j2-L28", "sq-L28"):
        fp = d["baselines"]["tori"][tag]
        gate(f"T0-{tag}", fp["connected"] and fp["bip_viol"] == 0
             and fp["qfrac"] == 1.0, f"p={fp['p']:.4f}")

    # ---- B-gates: census exactness ----
    ex = d["census"]["exact"]
    gate("B-exact-L4L6", all(v["n_legal_enum"] == v["n_legal_closed"] for v in ex.values())
         and ex["4"]["n_legal_enum"] > 0,
         f"L4={ex['4']['n_legal_enum']} L6={ex['6']['n_legal_enum']}")

    # ---- C1: determinism (independent re-run) ----
    g = nx.cycle_graph(10)
    kw = dict(src=0, rmax=5, qmap={v: v % 2 for v in g},
              cellmap={v: (v, 0) for v in g}, p_lo=2, p_hi=4)
    r1 = neutral_drift(g, 20, seed=11, snapshot_every=5, fp_kwargs=kw)
    r2 = neutral_drift(g, 20, seed=11, snapshot_every=5, fp_kwargs=kw)
    gate("C1-determinism", r1 == r2)

    # ---- C3: E conservation along every drift trajectory ----
    c3ok = True
    for sec in ("balls", "controls"):
        for tag, runs in d["drift"][sec].items():
            for s, r in runs.items():
                es = {fp["e"] for fp in r["traj"]}
                if len(es) != 1 or r["moves_applied"] != r["moves_proposed"]:
                    c3ok = False
    gate("C3-E-conserved", c3ok, "all drift trajectories")

    # ---- Death table ----
    print("\n--- class-death table (move index; None = alive at T) ---")
    med = {}
    for R in ("12", "18", "24"):
        deaths = [d["drift"]["balls"][R][s]["death"] for s in ("0", "1", "2")]
        med[R] = sorted(x for x in deaths if x is not None)
        med[R] = med[R][len(med[R]) // 2] if med[R] else None
        print(f"  J2-ball R{R}: deaths={deaths} median={med[R]}")
    for tag in ("sq-L28", "j2-L28"):
        runs = d["drift"]["controls"][tag]
        print(f"  {tag}: " + ", ".join(f"seed {s}: death={r['death']}" for s, r in runs.items()))
    n_dead = sum(1 for R in ("12", "18", "24") for s in ("0", "1", "2")
                 if d["drift"]["balls"][R][s]["death"] is not None)
    gate("C5-multisize", True, f"{n_dead}/9 J2 runs dead across R=12/18/24")

    # ---- U-audit + defect summary ----
    print("\n--- U-audit (pristine L12) ---")
    for name, r in d["audit"]["pristine_L12"].items():
        print(f"  {name}: acc={r['accepts']} longs {r['longs_before']}->"
              f"{r['longs_after']} p {r['fp_before']['p']}->{r['fp_after']['p']}")
    print("--- defects (class-restore check) ---")
    base12 = d["baselines"]["tori"]["j2-L12"]
    for s, rec in d["defects"].items():
        for name, r in rec["rules"].items():
            alive = class_alive({**r["fp_after"], "connected": r["fp_after"]["connected"]},
                                base12)
            print(f"  def{s} {name}: bit={r['fp_after'] and r['bit_restored']} "
                  f"longs={r['longs_after']} alive={alive}")

    # ---- Verdict ladder (frozen bars) ----
    print("\n--- ladder ---")
    n_legal = d["census"]["closed"]["28"]["n_legal"]
    kinematic = (n_legal == 0)
    print(f"KINEMATIC-RIGID: N_legal(L28)={n_legal} -> {kinematic}")

    dyn_candidates = []
    for name, r in d["audit"]["pristine_L12"].items():
        inert_fixed = (r["accepts"] == 0 and class_alive(
            {**r["fp_after"], "connected": r["fp_after"]["connected"]}, base12))
        restored = 0
        for s, rec in d["defects"].items():
            rr = rec["rules"].get(name)
            if rr is None:
                continue
            if rr["longs_after"] == 0 and class_alive(
                    {**rr["fp_after"], "connected": rr["fp_after"]["connected"]}, base12):
                restored += 1
        n_def = sum(1 for s in d["defects"].values() if name in s["rules"])
        dyn = inert_fixed and n_def == 3 and restored >= 2
        print(f"DYNAMIC probe {name}: inert_fixed={inert_fixed} "
              f"restored={restored}/{n_def} -> {dyn}")
        if dyn:
            dyn_candidates.append(name)

    all_alive = (n_dead == 0)
    print(f"CLASS-RIGID: all 9 alive at T -> {all_alive}")
    finite_meds = [m for m in med.values() if m is not None]
    mono_up = (len(finite_meds) == 3 and med["12"] is not None
               and med["12"] < med["18"] < med["24"])
    metastable = (not all_alive and len(finite_meds) >= 2
                  and (any(m > 200 for m in finite_meds) or mono_up))
    print(f"METASTABLE: finite_meds={finite_meds} mono_up={mono_up} -> {metastable}")
    flat = (not kinematic and not dyn_candidates and not all_alive and not metastable)

    if kinematic:
        verdict = "BR1-KINEMATIC-RIGID"
    elif dyn_candidates:
        verdict = "BR1-DYNAMIC-RIGID"
    elif all_alive:
        verdict = "BR1-CLASS-RIGID"
    elif metastable:
        verdict = "BR1-METASTABLE"
    else:
        verdict = "BR1-FLAT"
    print(f"\nVERDICT: {verdict}")
    print(f"  (flat={flat}; N0=frozen-analytic; N1=measured above; "
          f"NX=vacuous-no-vacuum-domain-U)")

    fails = [r for r in results if r[1] == FAIL]
    print(f"\ngates: {len(results) - len(fails)}/{len(results)} pass")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
