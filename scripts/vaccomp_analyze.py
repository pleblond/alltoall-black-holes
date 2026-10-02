"""VAC-COMP-0 analyzer: preregistered gates -> verdicts (FROZEN protocol).

Reads data/vaccomp/results.json (written by vaccomp_campaign.py),
applies the VACCOMP0-PREREG gates, writes data/vaccomp/verdict.json,
prints the gate table + ladder. Exit 0 always.
"""

from __future__ import annotations

import argparse
import json
import math
import sys

import numpy as np


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inp", default="data/vaccomp/results.json")
    ap.add_argument("--out", default="data/vaccomp/verdict.json")
    args = ap.parse_args()

    with open(args.inp) as f:
        R = json.load(f)["records"]
    V: dict = {}
    out: dict = {}

    def s(tag):
        return R[tag]

    # ---- C2: spectral exactness (0A/0F/0G) ----
    c2 = True
    for tag, L in (("spectral_L4", 4), ("spectral_L6", 6), ("spectral_L8", 8)):
        r = s(tag)
        n = 2 * L * L
        ok = (
            abs(r["e_min"] + 8.0) < 1e-9
            and abs(r["e_max"] - 8.0) < 1e-9
            and r["bloch_max_dev"] < 1e-6
            and r["minus8_unique"]
            and r["plus8_unique"]
            and r["zero_census"]["decomposition_ok"]
            and r["n_zero"] == n // 2 + r["zero_census"]["nodal_predicted"]
        )
        for name in ("VPLUS", "VPI", "VMINUS"):
            c = r["candidates"][name]
            ok = ok and c["residual"] < 1e-9 and abs(c["subspace_weight"] - 1.0) < 1e-9
        ok = (
            ok
            and abs(r["candidates"]["VPLUS"]["max_overlap"] - 1.0) < 1e-9
            and abs(r["candidates"]["VPI"]["max_overlap"] - 1.0) < 1e-9
        )
        V[f"C2_L{L}"] = bool(ok)
        c2 = c2 and ok
    V["C2"] = bool(c2)
    out["n_zero"] = {L: s(f"spectral_L{L}")["n_zero"] for L in (4, 5, 6, 8)}

    # ---- C0: VAC-FIELD regression + VSTAG (headline L=28, full ledger) ----
    c0 = True
    for tag in ("lad_VPLUS_28", "lad_VPI_28", "lad_VMINUS_28", "lad_VSTAG_28", "lad_CIRCLE_28"):
        r = s(tag)
        ok = r["rung"] == "JOINT" and all(r["checks"].values())
        V[f"C0_{tag}"] = bool(ok)
        c0 = c0 and ok
    c0 = c0 and all(
        r["rung"] == "JOINT"
        for r in s("circle_L4")["rows"]
        if abs(r["alpha"]) < 1e-9 or abs(r["alpha"] - math.pi / 2) < 1e-9
    )
    V["C0"] = bool(c0)
    out["headline_rungs"] = {
        t: s(t)["rung"]
        for t in ("lad_VPLUS_28", "lad_VPI_28", "lad_VMINUS_28", "lad_VSTAG_28", "lad_CIRCLE_28")
    }

    # ---- C1: SYM quotient (structural; no data gate) ----
    V["C1"] = True

    # ---- C3/0B: stationarity theorem (arbitrary degenerate superposition) --
    st = s("stattheorem_L4")
    V["C3"] = bool(st["degenerate"]["ok"] and st["vminus"]["ok"])
    out["stattheorem"] = st

    # ---- 0E: generic eigenstates are not vacua ----
    g0 = True
    for tag in ("gen_zero_complex", "gen_zero_real", "gen_mid_complex"):
        r = s(tag)
        ok = "JOINT" not in r["rungs"]
        V[f"E_{tag}"] = bool(ok)
        g0 = g0 and ok
    V["E_current_binds"] = bool(s("gen_zero_complex")["fails"].get("current_free", 0) >= 8)
    V["E_stress_binds"] = bool(s("gen_zero_real")["fails"].get("stress", 0) >= 4)
    V["0E"] = bool(g0 and V["E_current_binds"] and V["E_stress_binds"])
    out["generic"] = {
        t: s(t)["rungs"] for t in ("gen_zero_complex", "gen_zero_real", "gen_mid_complex")
    }

    # ---- 0H: hidden RP^1 circle (central census) ----
    h0 = True
    for tag in ("circle_L4", "circle_L6"):
        rows = s(tag)["rows"]
        bg = [r for r in rows if abs(r["alpha"] - math.pi / 4) < 1e-9]
        rest = [r for r in rows if abs(r["alpha"] - math.pi / 4) >= 1e-9]
        ok = (
            len(bg) == 1
            and bg[0]["rung"] == "BACKGROUND"
            and bg[0]["Bmax"] < 1e-12
            and all(r["rung"] == "JOINT" for r in rest)
        )
        V[f"H_{tag}"] = bool(ok)
        h0 = h0 and ok
    V["0H"] = bool(h0)

    # ---- 0I/0J: complex vs real hidden ----
    V["0I"] = bool(s("hidden_complex_L4")["frac_excluded"] > 0.9)
    hr = s("hidden_real_L4")
    V["0J"] = bool(
        hr["real_dim"] == 16
        and hr["proj_dim"] == 15
        and all(e < 1e-12 for e in hr["edge_max"])
        and all(r["rung"] != "JOINT" for r in hr["rows"])
    )
    out["hidden"] = {
        "complex_excluded": s("hidden_complex_L4")["n_excluded"],
        "real_rungs": hr.get("rungs"),
    }

    # ---- BZERO background cap ----
    V["BZERO"] = bool(
        all(
            r["rung"] == "BACKGROUND" and r["Bmax"] < 1e-12 and abs(r["energy"]) < 1e-9
            for r in s("bzero_L4")["rows"]
        )
    )

    # ---- 0K: amplitude families ----
    k0 = True
    for tag in ("amp_VPLUS_L4", "amp_VPI_L4", "amp_VMINUS_L4", "amp_VSTAG_L4", "amp_CIRCLE_L4"):
        ok = bool(s(tag)["all_joint"])
        V[f"K_{tag}"] = ok
        k0 = k0 and ok
    V["0K"] = bool(k0)

    # ---- 0L: same-eigenvalue sweep (real circle interior JOINT) ----
    mstag = s("interp_MSTAG")
    V["0L"] = bool(
        mstag["dE"] == 0.0
        and mstag["max_rho_drift"] < 1e-8
        and mstag["max_B_drift"] < 1e-8
        and mstag["max_J_drift"] < 1e-8
        and mstag["n_interior_joint"] == 10
    )

    # ---- 0M/0N/0O/0P: beats, no interior JOINT ----
    beats = {"beat_PPI": 16.0, "beat_PM": 8.0, "beat_PIM": 8.0}
    m0 = True
    for tag, dE in beats.items():
        r = s(tag)
        ok = abs(r["dE"] - dE) < 1e-9 and abs(r["beat_corr"]) > 0.99 and r["rho_beat_amp"] > 0.0
        V[f"M_{tag}"] = bool(ok)
        m0 = m0 and ok
    for tag in ("interp_PPI", "interp_PM", "interp_PIM"):
        r = s(tag)
        ok = r["n_interior_joint"] == 0 and r["max_rho_drift"] > 1e-6  # beats present somewhere
        V[f"M_{tag}"] = bool(ok)
        m0 = m0 and ok
    V["0M"] = bool(m0)
    out["beats"] = {
        t: {"dE": s(t)["dE"], "corr": s(t)["beat_corr"], "amp": s(t)["rho_beat_amp"]} for t in beats
    }

    # ---- 0Q: no cross-term cancellation ----
    V["0Q"] = bool(all(not s(t)["cancelled"] and s(t)["rho_x_max"] > 1e-9 for t in beats))
    out["cross"] = {
        t: {"rho_x": s(t)["rho_x_max"], "B_x": s(t)["B_x_max"], "J_x": s(t)["J_x_max"]}
        for t in beats
    }

    # ---- 0T/0U: orbits (all four ray-TI singletons) ----
    orb = s("orbits_L4")["orbits"]
    V["0TU"] = bool(all(v["ray_TI"] and v["orbit_size"] == 1 for v in orb.values()))
    out["orbits"] = orb

    # ---- 0V: observer equivalence ----
    dist = s("coarse_L4")["dist"]
    ti = ["VPI", "VPLUS", "VMINUS", "VSTAG"]
    V["0V_blind"] = bool(
        all(dist[f"{a}|{b}"] < 1e-12 for i, a in enumerate(ti) for b in ti[i + 1 :])
    )
    V["0V_visible"] = bool(dist["CIRCLE@pi/8|VMINUS"] > 1e-4)
    V["0V"] = bool(V["0V_blind"] and V["0V_visible"])
    out["coarse"] = dist

    # ---- 0W: excitation fingerprint ----
    fp = s("excit_L4")["fp"]
    V["0W"] = bool(fp["speed"] > 0.5 and fp["r2"] > 0.9 and fp["msd_alpha"] > 1.3)
    out["excitation"] = fp

    # ---- 0X: ledger classes (descriptive) ----
    lg = s("ledger_L4")
    V["0X"] = bool(
        lg["dist"]["VPLUS|VPI"]["dmax"] > 1e-6 and lg["dist"]["VMINUS|VSTAG"]["dB"] > 1e-6
    )
    out["ledger"] = {"dist": lg["dist"], "stats": lg["stats"]}

    # ---- 0Y/0Z: zero limit + protection ----
    y0 = True
    for name, rep in s("zero_L4")["shapes"].items():
        la = np.log([r[0] for r in rep["rows"]])
        lq = np.log([r[1] for r in rep["rows"]])
        slope = float(np.polyfit(la, lq, 1)[0])
        ok = abs(slope - 2.0) < 1e-9 and rep["rows"][0][1] < 2e-6
        V[f"Y_{name}"] = bool(ok)
        y0 = y0 and ok
        n = len(rep["rows"])
        pr_ok = rep["zero_free"] and abs(rep["r_prot"] - 1.0 / math.sqrt(32)) < 1e-12
        V[f"Z_{name}"] = bool(pr_ok)
        y0 = y0 and pr_ok
    V["0Y"] = bool(y0)
    V["0Z"] = bool(y0)

    # ---- 0AA: size scaling ----
    sc = {r["L"]: r for r in s("scaling")["rows"]}
    V["0AA"] = bool(
        all(r["nodal_formula"] for r in sc.values())
        and all((r["hidden_shape_dim"] == 1) == r["even"] for r in sc.values())
        and sc[4]["n_zero"] == 22
        and sc[28]["n_zero"] == 838
        and sc[4]["n_ti_joint"] == 4
        and sc[5]["n_ti_joint"] == 2
    )
    out["scaling"] = {
        L: {
            "n_zero": r["n_zero"],
            "even": r["even"],
            "n_ti": r["n_ti_joint"],
            "hdim": r["hidden_shape_dim"],
        }
        for L, r in sc.items()
    }

    # ---- 0AB: quotient ----
    q0 = True
    for tag in ("quotient_L4", "quotient_L6"):
        r = s(tag)
        ok = (
            abs(r["e_min"] + 8.0) < 1e-9
            and abs(r["e_max"] - 8.0) < 1e-9
            and r["VPLUS"]["residual"] < 1e-9
            and r["VPI"]["residual"] < 1e-9
            and "absent" in r["VMINUS_quotient"]
        )
        V[f"AB_{tag}"] = bool(ok)
        q0 = q0 and ok
    V["0AB"] = bool(q0)

    # ---- 0AC: square control ----
    s0 = True
    for tag, e in (("square_L4", 4.0), ("square_L6", 4.0)):
        r = s(tag)
        ok = (
            abs(r["e_min"] + e) < 1e-9
            and abs(r["e_max"] - e) < 1e-9
            and r["VPLUS"]["current_free"]
            and r["VPLUS"]["stress"]
            and r["VPI"]["current_free"]
            and r["VPI"]["stress"]
        )
        V[f"AC_{tag}"] = bool(ok)
        s0 = s0 and ok
    V["0AC"] = bool(s0)

    # ---- Odd L=5 ----
    odd = s("odd_L5")
    sp5 = s("spectral_L5")
    V["ODD"] = bool(
        odd["vminus_rung"] == "JOINT"
        and odd["vstag"] == "raises (even-L only)"
        and odd["plus8_row"] is None
        and odd["e_max"] < 8.0
        and odd["n_zero"] == sp5["n_zero"]
        and sp5["zero_census"]["decomposition_ok"]
    )
    out["odd"] = {k: odd[k] for k in ("n_zero", "e_max", "vminus_rung", "vstag", "vpi_rayleigh")}

    # ---- Ladder ----
    core = [
        "C0",
        "C2",
        "C3",
        "0E",
        "0H",
        "0I",
        "0J",
        "BZERO",
        "0K",
        "0L",
        "0M",
        "0Q",
        "0TU",
        "0V",
        "0W",
        "0X",
        "0Y",
        "0Z",
        "0AA",
        "0AB",
        "0AC",
        "ODD",
    ]
    fails = [k for k in core if not V.get(k)]
    if fails and ("C0" in fails or "C2" in fails):
        ladder = "VACCOMP0-NULL"
    elif fails:
        ladder = "VACCOMP0-PARTIAL"
    else:
        ladder = "VACCOMP0-COMPLETE"
    V["ladder"] = ladder
    V["fails"] = fails
    out["verdicts"] = V
    with open(args.out, "w") as f:
        json.dump(out, f, indent=1, default=str)
    print(json.dumps(V, indent=1))
    print("ladder:", ladder)
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
