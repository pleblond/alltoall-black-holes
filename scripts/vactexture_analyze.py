"""VAC-TEXTURE-0 analyzer: preregistered gates -> verdicts (FROZEN protocol).

Reads data/vactexture/results.json (written by vactexture_campaign.py),
applies the VACTEXTURE0-PREREG gates, writes data/vactexture/verdict.json,
prints the gate table + ladder. Exit 0 always.
"""

from __future__ import annotations

import argparse
import json
import math
import sys

import numpy as np


def _sweep_ok(rows, w_bar=1e-12, h_bar=1e-9, e_bar=1e-9):
    return all(float(r["w_sym"]) < w_bar and float(r["h_residual"]) < h_bar
               and abs(float(r["energy"])) < e_bar and float(r["Jmax"]) < 1e-12
               for r in rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inp", default="data/vactexture/results.json")
    ap.add_argument("--out", default="data/vactexture/verdict.json")
    args = ap.parse_args()

    with open(args.inp) as f:
        R = json.load(f)["records"]
    V: dict = {}
    out: dict = {}

    def s(tag):
        return R[tag]

    # ---- 0A/C0: uniform-circle reproduction ----
    c0 = True
    for tag in ("uniform_L4", "uniform_L6", "uniform_L28"):
        rows = s(tag)["rows"]
        bg = [r for r in rows if abs(r["alpha"] - math.pi / 4) < 1e-9]
        rest = [r for r in rows if abs(r["alpha"] - math.pi / 4) >= 1e-9]
        ok = (len(bg) == 1 and bg[0]["rung"] == "BACKGROUND"
              and bg[0]["Bmax"] < 1e-12
              and all(r["rung"] == "JOINT" for r in rest))
        V[f"C0_{tag}"] = bool(ok)
        c0 = c0 and ok
    V["uniform_circle"] = bool(c0)
    out["uniform"] = {t: [(r["alpha"], r["rung"]) for r in s(t)["rows"]]
                      for t in ("uniform_L4", "uniform_L28")}

    # ---- 0C/0D: P_- E_0 + no emission ----
    p0 = True
    for tag in ("sweep_L4", "sweep_L8", "sweep_L28", "amp_sine_L4",
                "amp_sine_L28", "scaling"):
        rows = s(tag)["rows"] if tag != "scaling" else s(tag)["rows"]
        ok = _sweep_ok(rows)
        V[f"P_{tag}"] = bool(ok)
        p0 = p0 and ok
    for tag in ("stationary_L4", "stationary_L28"):
        rows = s(tag)["rows"]
        ok = all(float(r["w_sym_max"]) < 1e-12 and float(r["w_sym_end"]) < 1e-12
                 for r in rows)
        V[f"E_{tag}"] = bool(ok)
        p0 = p0 and ok
    V["pminus_e0"] = bool(p0)
    out["pminus_max"] = {
        t: max(float(r["w_sym"]) for r in s(t)["rows"])
        for t in ("sweep_L4", "sweep_L28")}
    out["hres_max"] = {
        t: max(float(r["h_residual"]) for r in s(t)["rows"])
        for t in ("sweep_L4", "sweep_L28")}

    # ---- 0E/0I-local: local gradient leg ----
    obs28 = {r["family"]: r for r in s("observer_L28")["rows"]}
    lgrad = bool(obs28["sine-x"]["D"] > 1e-6 and obs28["step"]["D"] > 1e-6
                 and obs28["sine-x"]["d_B"] > 1e-6)
    V["local_gradient"] = lgrad
    sw28 = s("sweep_L28")["rows"]
    nonuni = [r for r in sw28 if r["family"] != "uniform"]
    V["local_B_std"] = bool(max(float(r["B_pcmax"]) for r in nonuni) > 1e-6)
    out["observer_L28"] = {r["family"]: {"D": r["D"], "d_B": r["d_B"],
                                         "d_coarse": r["d_coarse"]}
                           for r in s("observer_L28")["rows"]}

    # ---- 0F: scaling leg (derived slopes + ordering) ----
    lam_rows = [r for r in sw28 if r["family"] == "sine-x"
                and abs(float(r["params"].get("delta", 0.0)) - math.pi / 4.0) < 1e-9]
    lam_rows = sorted(lam_rows, key=lambda r: float(r["analytic_grad"]))
    if len(lam_rows) >= 2:
        xs = np.array([float(r["analytic_grad"]) for r in lam_rows])
        ys = np.array([float(r["B_pcmax"]) for r in lam_rows])
        m = (xs > 0) & (ys >= 0)
        slope = float(np.polyfit(np.log(xs[m]),
                                 np.log(np.maximum(ys[m], 1e-300)), 1)[0]) \
            if m.sum() >= 2 and not np.all(ys[m] == 0.0) else float("nan")
        ordered = bool(ys[0] < ys[-1]) if ys.size >= 2 else False
    else:
        slope, ordered = float("nan"), False
    V["scaling"] = bool(np.isfinite(slope) and slope > 0.0 and ordered)
    out["scaling"] = {"slope_Bpcmax_vs_grad": slope, "ordered": ordered,
                      "lam_grid": [(float(r["params"]["lam"]), float(r["B_pcmax"]))
                                   for r in lam_rows]}
    amp4 = s("amp_sine_L4")["rows"]
    la = np.log([float(r["a"]) for r in amp4])
    lq = np.log([max(float(r["Q"]), 1e-300) for r in amp4])
    aslope = float(np.polyfit(la, lq, 1)[0])
    V["amp_scaling"] = bool(abs(aslope - 2.0) < 1e-9)
    out["amp_slope"] = aslope

    # ---- 0G: smooth vs sharp ----
    ss28 = s("smooth_sharp_L28")["rows"]
    g0 = True
    for key, r in ss28.items():
        ok = (float(r["D"]) > 1e-6
              and float(r["grad_step_max"]) >= float(r["grad_sine_max"]) - 1e-9)
        V[f"G_{key}"] = bool(ok)
        g0 = g0 and ok
    V["smooth_sharp"] = bool(g0)
    out["smooth_sharp_L28"] = ss28

    # ---- 0H: stationary + carrier ----
    st0 = True
    for tag in ("stationary_L4", "stationary_L28"):
        ok = all(bool(r["ok"]) and float(r["rho_drift"]) < 1e-8
               and float(r["B_drift"]) < 1e-8 and float(r["J_drift"]) < 1e-8
               for r in s(tag)["rows"])
        V[f"S_{tag}"] = bool(ok)
        st0 = st0 and ok
    V["stationary"] = bool(st0)
    car = s("carrier_L28")["rows"]
    V["carrier"] = bool(all(bool(r["ok"]) for r in car))
    out["carrier_L28"] = car

    # ---- 0I: observer static visible + dynamically blind ----
    V["observer_static"] = bool(obs28["sine-x"]["d_coarse"] > 1e-4
                                or obs28["step"]["d_coarse"] > 1e-4)
    V["observer_blind"] = bool(all(float(r["sym_tex"]) < 1e-9
                                   and float(r["sym_diff"]) < 1e-9
                                   for r in s("observer_L28")["rows"])
                               and all(float(r["sym_tex"]) < 1e-9
                                       for r in s("observer_L4")["rows"]))
    V["quotient"] = bool(s("quotient_L4")["sym_norm"] < 1e-9
                         and s("quotient_L28")["sym_norm"] < 1e-9)
    out["quotient"] = {"L4": s("quotient_L4")["sym_norm"],
                       "L28": s("quotient_L28")["sym_norm"]}

    # ---- 0J: ledger leg ----
    lg4 = s("ledger_L4")
    lg28 = s("ledger_L28")
    def _key_has(dist, frag):
        return [v for k, v in dist.items() if frag in k]
    dmax4 = max(float(v["dmax"]) for v in lg4["dist"].values())
    dmax28 = max(float(v["dmax"]) for v in lg28["dist"].values())
    cu28 = lg28["contraction"]
    tex_nonuni = any((not v["uniform"]) for k, v in cu28.items()
                     if "sine" in k or "step" in k)
    uni0 = [v for k, v in cu28.items() if "uniform" in k and "0.0" in k]
    uni_flat = all(bool(v["uniform"]) for v in uni0) if uni0 else True
    V["ledger"] = bool(dmax28 > 1e-6 and dmax4 > 1e-6 and tex_nonuni and uni_flat)
    out["ledger"] = {"dmax_L4": dmax4, "dmax_L28": dmax28,
                     "contraction_L28": {k: v["uniform"] for k, v in cu28.items()},
                     "m1_L28": {k: (v["f_zero"], v["f_neg"], v["f_pos"])
                                for k, v in lg28["m1"].items()}}

    # ---- 0K: size scaling ----
    sc = s("scaling")["rows"]
    V["size_scaling"] = bool(all(float(r["w_sym"]) < 1e-12
                                 and float(r["h_residual"]) < 1e-9
                                 and abs(float(r["energy"])) < 1e-9
                                 for r in sc)
                             and sc[0]["L"] == 4 and sc[-1]["L"] == 28)
    out["scaling_rows"] = [(r["L"], r["B_std"], r["rms_grad"]) for r in sc]

    # ---- C1-C4: controls ----
    V["phase"] = bool(s("phase_L4")["ok"] and s("phase_L28")["ok"])
    V["projective"] = bool(s("projective_L4")["ok"] and s("projective_L28")["ok"])
    V["covariance"] = bool(s("covariance_L4")["ok"] and s("covariance_L28")["ok"])
    V["witness"] = bool(s("witness_L4")["ok"])
    V["odd"] = bool(all(float(r["w_sym"]) < 1e-12
                         and float(r["h_residual"]) < 1e-9 for r in s("odd_L5")["rows"]))
    out["controls"] = {"phase": [s("phase_L4")["ok"], s("phase_L28")["ok"]],
                       "projective": [s("projective_L4")["ok"], s("projective_L28")["ok"]],
                       "covariance": [s("covariance_L4")["ok"], s("covariance_L28")["ok"]],
                       "witness": s("witness_L4")["witness"]}

    # ---- Ladder (frozen logic mirrors vactexture.campaign_verdict) ----
    checks = {k: bool(V.get(k, False)) for k in
              ("pminus_e0", "uniform_circle", "local_gradient", "scaling",
               "smooth_sharp", "stationary", "carrier", "observer_static",
               "observer_blind", "ledger", "phase", "projective",
               "covariance", "witness")}
    radiative = bool((not checks["stationary"]) or (not checks["carrier"])
                       or (not checks["pminus_e0"]) or (not checks["observer_blind"]))
    apparatus = bool(checks["uniform_circle"] and checks["phase"]
                     and checks["projective"] and checks["covariance"]
                     and checks["witness"])
    if radiative:
        ladder = "VACTEXTURE-RADIATIVE"
    elif checks["pminus_e0"] and (not checks["local_gradient"]) \
            and (not checks["ledger"]) and (not checks["scaling"]) and apparatus:
        ladder = "VACTEXTURE-NOLOCAL"
    elif checks["pminus_e0"] and (not checks["local_gradient"]) \
            and (not checks["ledger"]):
        ladder = "VACTEXTURE-FLAT"
    elif bool(checks["pminus_e0"] and checks["local_gradient"] and checks["stationary"]
              and checks["carrier"] and checks["observer_blind"] and checks["ledger"]
              and checks["scaling"] and checks["smooth_sharp"] and apparatus):
        ladder = "VACTEXTURE-GRADIENT"
    else:
        ladder = "VACTEXTURE-PARTIAL"
    V["ladder"] = ladder
    core = ["pminus_e0", "uniform_circle", "local_gradient", "scaling",
            "smooth_sharp", "stationary", "carrier", "observer_static",
            "observer_blind", "ledger", "phase", "projective",
            "covariance", "witness", "size_scaling", "quotient", "odd"]
    V["fails"] = [k for k in core if not V.get(k)]
    out["verdicts"] = V
    with open(args.out, "w") as f:
        json.dump(out, f, indent=1, default=str)
    print(json.dumps(V, indent=1))
    print("ladder:", ladder)
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
