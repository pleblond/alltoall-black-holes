"""VAC-DOMAIN-0 analyzer: preregistered gates -> verdicts (FROZEN protocol).

Reads data/vacdomain/*.json (written by vacdomain_campaign.py), applies
the VACDOMAIN0-PREREG gates, writes data/vacdomain/verdict.json, prints
the gate table + ladder. Exit 0 always.
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys

BARS = {
    "stationarity": 1e-8,
    "sector_weight": 1e-12,
    "spectral_match": 1e-8,
    "witness": 1e-10,
    "support_drift": 1e-9,
    "front_r2": 0.8,
    "front_reach": 3,
    "step_ratio": 0.5,
    "plateau_frac": 0.2,
    "bulk_frac": 0.1,
    "orient_cov": 1e-9,
    "phase_inv": 1e-9,
    "pminus_frozen": 1e-9,
    "sector_conserve": 1e-9,
}
V_QUAD = 5.94  # banked RESPONSE-0 quadratic-front speed (filed comparison)

BULKS = ("VPLUS", "VPI", "H0", "H1", "H2", "H3")
DISC = (
    ("VPLUS", "VPI"),
    ("VPLUS", "H0"),
    ("VPLUS", "H1"),
    ("VPLUS", "H2"),
    ("VPLUS", "H3"),
    ("VPI", "H0"),
    ("VPI", "H1"),
    ("VPI", "H2"),
    ("VPI", "H3"),
)
HIDHID = (("H0", "H3"), ("H1", "H2"))
SAME = (("VPLUS", "VPLUS"), ("VPI", "VPI"), ("H0", "H0"))
L_LIST = (4, 8, 28)


def pn(a, b):
    return f"{a}_{b}"


def load(outdir):
    recs = {}
    for path in glob.glob(os.path.join(outdir, "*.json")):
        base = os.path.basename(path)
        if base == "verdict.json":
            continue
        with open(path) as f:
            recs[base[:-5]] = json.load(f)
    return recs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inp", default="data/vacdomain")
    ap.add_argument("--out", default="data/vacdomain/verdict.json")
    args = ap.parse_args()
    R = load(args.inp)
    V: dict = {}
    out: dict = {}

    def pay(rec):
        return rec["payload"]

    def ev(L, a, b, ori):
        return pay(R[f"evolve_L{L}_ori{ori}_pair{pn(a, b)}"])

    # ---- G0: bulk JOINT regression ----
    g0 = True
    for L in L_LIST:
        for name in BULKS:
            r = pay(R[f"bulk_L{L}_name{name}"])
            ok = r["rung"] == "JOINT" and all(r["checks"].values())
            V[f"G0_L{L}_{name}"] = bool(ok)
            g0 = g0 and ok
    V["G0"] = bool(g0)

    # ---- G1: no-go analytic + numeric ----
    g1 = True
    for L in L_LIST:
        for ori in ("x", "y"):
            for a, b in DISC:
                r = pay(R[f"nogo_L{L}_ori{ori}_pair{pn(a, b)}"])
                ana_ok = bool(r["analytic"]["no_go"]) and r["analytic"]["dE"] in (8.0, 16.0)
                num = r["numeric"]
                if L >= 8:
                    num_ok = (
                        num["interiorA"]["n"] > 0
                        and num["interiorB"]["n"] > 0
                        and num["interiorA"]["lam_maxdev"] < 1e-9
                        and num["interiorB"]["lam_maxdev"] < 1e-9
                        and num["best_residual"] > 1e-6
                    )
                    eA = {"VPLUS": -8.0, "VPI": 8.0}.get(a, 0.0)
                    eB = {"VPLUS": -8.0, "VPI": 8.0}.get(b, 0.0)
                    num_ok = num_ok and abs(num["interiorA"]["lam_median"] - eA) < 1e-9
                    num_ok = num_ok and abs(num["interiorB"]["lam_median"] - eB) < 1e-9
                else:
                    num_ok = (
                        num["interiorA"]["n"] == 0
                        and num["interiorB"]["n"] == 0
                        and num["best_residual"] > 1e-6
                    )
                ok = ana_ok and num_ok
                V[f"G1_L{L}_{ori}_{pn(a, b)}"] = bool(ok)
                g1 = g1 and ok
            for a, b in HIDHID:
                r = pay(R[f"nogo_L{L}_ori{ori}_pair{pn(a, b)}"])
                ok = (not r["analytic"]["no_go"]) and r["numeric"]["best_residual"] < 1e-9
                V[f"G1_L{L}_{ori}_{pn(a, b)}"] = bool(ok)
                g1 = g1 and ok
    V["G1"] = bool(g1)

    # ---- G2: hidden-hidden exactly stationary ----
    g2 = True
    for L in L_LIST:
        for ori in ("x", "y"):
            for a, b in HIDHID:
                r = ev(L, a, b, ori)
                ok = (
                    r["interface_stationary"]
                    and abs(r["sector"]["w_anti_0"] - 1.0) < 1e-12
                    and r["pminus"]["frozen_err"] < BARS["pminus_frozen"]
                )
                V[f"G2_L{L}_{ori}_{pn(a, b)}"] = bool(ok)
                g2 = g2 and ok
    V["G2"] = bool(g2)

    # ---- G3: disconnected nonstationary (STATIONARY verdict iff fails) ----
    g3 = True
    nonstat = {}
    for L in L_LIST:
        for ori in ("x", "y"):
            for a, b in DISC:
                r = ev(L, a, b, ori)
                ok = not r["interface_stationary"]
                nonstat[f"{L}/{ori}/{pn(a, b)}"] = bool(ok)
                g3 = g3 and ok
    V["G3"] = bool(g3)
    out["nonstationary"] = nonstat

    # ---- G4: spectral superposition + witness + conservation ----
    g4 = True
    for L in (4, 8):
        for a, b in DISC:
            r = pay(R[f"spectral_L{L}_pair{pn(a, b)}"])
            ok = (
                r["spectral"]["max_err"] < BARS["spectral_match"]
                and r["witness"]["I_linearity"] < BARS["witness"]
                and r["support"]["support_drift"] < BARS["support_drift"]
            )
            V[f"G4_L{L}_{pn(a, b)}"] = bool(ok)
            g4 = g4 and ok
    for L in L_LIST:
        for ori in ("x", "y"):
            for a, b in DISC:
                r = ev(L, a, b, ori)
                ok = (
                    r["sector"]["w_sym_drift"] < BARS["sector_conserve"]
                    and r["sector"]["w_anti_drift"] < BARS["sector_conserve"]
                    and r["pminus"]["frozen_err"] < BARS["pminus_frozen"]
                    and r["energy_drift"] < 1e-9
                )
                # Mixed-sector joins carry exact-half P_- residue.
                if b in ("H0", "H1", "H2", "H3"):
                    ok = ok and abs(r["pminus"]["weight"] - 0.5) < 1e-9
                V[f"G4cons_L{L}_{ori}_{pn(a, b)}"] = bool(ok)
                g4 = g4 and ok
    V["G4"] = bool(g4)

    # ---- G5: RADIATIVE vs MIXING at L=28 headline ----
    # RADIATIVE = ballistic emitted fronts (reach + linearity) + the S
    # step and both bulk plateaus persist (bulk vacua survive while the
    # disturbance propagates away). Width growth is broadening anatomy
    # (a radiating sharp step widens the disturbed zone ~ 2 v t), never
    # a gate. Front speed is filed against V_QUAD = 5.94 (banked
    # RESPONSE-0 quadratic front), not gated.
    g5 = True
    rad = {}
    for ori in ("x", "y"):
        for a, b in DISC:
            r = ev(28, a, b, ori)
            fr = r["front"]
            front_ok = (
                fr["moving"]
                and fr["reach"] >= BARS["front_reach"]
                and fr["r2"] > BARS["front_r2"]
            )
            wS = r["width_S"]
            step_ok = wS["step_ratio"] > BARS["step_ratio"]
            plat_ok = (
                wS["plateauA_drift"] < BARS["plateau_frac"] * wS["step_0"]
                and wS["plateauB_drift"] < BARS["plateau_frac"] * wS["step_0"]
            )
            ok = bool(front_ok and step_ok and plat_ok)
            rad[f"{ori}/{pn(a, b)}"] = {
                "radiative": ok,
                "v": fr["v"],
                "v_over_quad": fr["v"] / V_QUAD if fr["moving"] else 0.0,
                "r2": fr["r2"],
                "reach": fr["reach"],
                "step_ratio": wS["step_ratio"],
                "wS_growth": wS["t10_90_growth"],
            }
            V[f"G5_{ori}_{pn(a, b)}"] = ok
            g5 = g5 and ok
    V["G5"] = bool(g5)
    out["radiative"] = rad

    # ---- Controls ----
    cc = True
    for L in L_LIST:
        for ori in ("x", "y"):
            for a, b in SAME:
                r = ev(L, a, b, ori)
                ok = r["interface_stationary"] and r["width_S"]["t10_90_0"] == 0
                V[f"Csame_L{L}_{ori}_{pn(a, b)}"] = bool(ok)
                cc = cc and ok
    for L in (4, 28):
        for a, b in DISC:
            r = pay(R[f"phase_L{L}_pair{pn(a, b)}"])
            ok = all(v < BARS["phase_inv"] for v in r["dev"].values())
            V[f"Cphase_L{L}_{pn(a, b)}"] = bool(ok)
            cc = cc and ok
    for L in L_LIST:
        for a, b in DISC + HIDHID:
            rx, ry = ev(L, a, b, "x"), ev(L, a, b, "y")
            ok = True
            for k in ("rho_drift", "B_drift", "J_drift"):
                ok = ok and abs(rx["interface_drifts"][k] - ry["interface_drifts"][k]) < 1e-9
            ok = ok and rx["width_S"]["t10_90_0"] == ry["width_S"]["t10_90_0"]
            V[f"Cori_L{L}_{pn(a, b)}"] = bool(ok)
            cc = cc and ok
    # Wrap-free control at L=28 only (headline): bulk centers see <
    # 10% of the interface disturbance (relative, scale free), or both
    # below the absolute bar for stationary joins. L=4/8 tori have no
    # tail-free bulk (slab half-widths 1-2 cells vs Lieb-Robinson tails
    # + threshold reach); their bulk drifts are filed as scaling anatomy.
    for L in (28,):
        for ori in ("x", "y"):
            for a, b in DISC + HIDHID + SAME:
                r = ev(L, a, b, ori)
                c = r["bulk_clean_drifts"]
                ic = r["interface_drifts_clean"]
                cmax = max(c["rho_drift"], c["B_drift"], c["J_drift"])
                imax = max(ic["rho_drift"], ic["B_drift"], ic["J_drift"])
                if imax < BARS["stationarity"]:
                    ok = cmax < BARS["stationarity"]
                else:
                    ok = cmax < BARS["bulk_frac"] * imax
                V[f"Cclean_L{L}_{ori}_{pn(a, b)}"] = bool(ok)
                cc = cc and ok
    for L in L_LIST:
        for ori in ("x", "y"):
            for a, b in DISC:
                lg = ev(L, a, b, ori)["ledger"]
                ok = all(math.isfinite(lg[k]) for k in ("B_mean", "B_std", "L_mean", "L_std"))
                V[f"Cledger_L{L}_{ori}_{pn(a, b)}"] = bool(ok)
                cc = cc and ok
    V["C"] = bool(cc)

    # ---- Ladder ----
    if not (V["G0"] and V["G4"] and V["C"]):
        ladder = "VACDOMAIN-NOJOIN"
    elif not V["G3"]:
        ladder = "VACDOMAIN-STATIONARY"
    elif V["G2"] and V["G5"]:
        ladder = "VACDOMAIN-RADIATIVE"
    else:
        ladder = "VACDOMAIN-MIXING"
    V["ladder"] = ladder
    V["fails"] = [k for k in ("G0", "G1", "G2", "G3", "G4", "G5", "C") if not V.get(k)]
    out["verdicts"] = V
    with open(args.out, "w") as f:
        json.dump(out, f, indent=1, default=str)
    core = {k: V[k] for k in ("G0", "G1", "G2", "G3", "G4", "G5", "C", "ladder")}
    print(json.dumps(core, indent=1))
    print("ladder:", ladder)
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
