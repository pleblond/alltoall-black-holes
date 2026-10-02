"""POT-1 Amendment-2 calibration (pre-rerun apparatus validation).

Selects PROTOCOL parameters (ramp tau, window T, AP geometry is fixed by
solves in the amendment text) with margin under FROZEN prereg thresholds.
Thresholds are NOT fit here: inherited gates stay identical; new gates come
from analytic predictions (v_max^shell=8, delta_AP from solves).

Batch (all local, L<=28 except one L42 RB run):
  K1: ramp tau x T grid on L12/L20 -> ramp-global, |F|, eps, J/B
  K2: jump 1T/2T/3T work_ratio trend (L28, L42) -> RB settling
  K3: front-threshold stability 5/10/20% (L28 raw turn-on)
  K4: H variants: (a) legacy shell match; (b) inner-shell + far-norm accounting
"""
from __future__ import annotations

import json
import math
import sys

import numpy as np

sys.path.insert(0, "src")
sys.path.insert(0, "scripts")

from pot1_campaign import DT, OM_J2, _j2_setup, _j2_src_nodes  # noqa: E402
from bh_graph.ballistic import gaussian_packet  # noqa: E402
from bh_graph.driven import (  # noqa: E402
    bilinears,
    dist_from_set,
    edge_arrays,
    final_period_rows,
    first_crossing,
    harmonic_pins,
    is_match_ok,
    period_epsilon,
    pinning_evolve,
    reactive_balance,
    shell_means_node,
    steady_predict,
    stroboscopic_separate,
)

RAMP_TAUS = (4.0, 8.0)
TS = (12.0, 24.0)


def _ramp_fn(s_vals, omega, tau):
    s_vals = np.asarray(s_vals, dtype=np.complex128)

    def fn(step: int) -> np.ndarray:
        t = (step + 1) * DT
        f = 0.5 * (1.0 - math.cos(math.pi * t / tau)) if t < tau else 1.0
        return f * s_vals * np.exp(-1.0j * float(omega) * t)

    return fn


def k1_ramp_grid():
    out = {}
    for L in (12, 20):
        g, order, c3, h, eu, ev = _j2_setup(L)
        nodes = _j2_src_nodes(L)
        idx = {v: i for i, v in enumerate(order)}
        pins = [idx[v] for v in nodes]
        pred = steady_predict(h, pins, [1.0], OM_J2)
        dist = dist_from_set(g, nodes)
        for tau in RAMP_TAUS:
            for T in TS:
                ns = int(round(T / DT))
                rec = pinning_evolve(np.zeros(len(order), dtype=np.complex128),
                                     h, DT, ns, pins, _ramp_fn([1.0], OM_J2, tau))
                rows = rec["psi"]
                fp_rows, fp_ts = final_period_rows(rows, DT, OM_J2)
                sep = stroboscopic_separate(fp_rows, fp_ts, OM_J2)
                fin = bilinears(rows[-1], eu, ev)
                mask = np.array([dist[v] <= 6 for v in order])
                key = f"L{L}_tau{tau:g}_T{T:g}"
                out[key] = {
                    "ramp_global": float(np.linalg.norm(sep["A"] - pred)
                                         / np.linalg.norm(pred)),
                    "Fmag": float(np.linalg.norm(sep["F"])),
                    "sep_resid": sep["rel_resid"],
                    "eps": period_epsilon(rows, DT, OM_J2, mask),
                    "JB": float(np.abs(fin["J"]).max()
                                / max(float(np.abs(fin["B"]).max()), 1e-300)),
                }
                print(f"K1 {key}: " + json.dumps(out[key]), flush=True)
    return out


def k2_rb_trend():
    out = {}
    for L, T in ((28, 8.0), (42, 10.0)):
        g, order, c3, h, eu, ev = _j2_setup(L)
        nodes = _j2_src_nodes(L)
        idx = {v: i for i, v in enumerate(order)}
        pins = [idx[v] for v in nodes]
        psi0 = steady_predict(h, pins, [1.0], OM_J2)
        for mult in (1, 2, 3):
            ns = int(round(mult * T / DT))
            rec = pinning_evolve(psi0, h, DT, ns, pins,
                                 harmonic_pins([1.0], OM_J2, DT))
            rb = reactive_balance(rec["work"], DT, OM_J2)
            key = f"L{L}_{mult}T"
            out[key] = {"ratio": rb["ratio"], "net": rb["net"],
                        "gross": rb["gross"],
                        "norm_drift": float(abs(rec["norms"][-1]
                                                - rec["norms"][0]))}
            print(f"K2 {key}: " + json.dumps(out[key]), flush=True)
    return out


def k3_front_thresh():
    L, T = 28, 8.0
    g, order, c3, h, eu, ev = _j2_setup(L)
    nodes = _j2_src_nodes(L)
    idx = {v: i for i, v in enumerate(order)}
    dist = dist_from_set(g, nodes)
    dvec = np.array([dist[v] for v in order])
    ns = int(round(T / DT))
    rec = pinning_evolve(np.zeros(len(order), dtype=np.complex128), h, DT, ns,
                         [idx[v] for v in nodes],
                         harmonic_pins([1.0], OM_J2, DT))
    rows = rec["psi"]
    ts = np.arange(rows.shape[0]) * DT
    sab = np.array([[float(np.mean(np.abs(rk[dvec == r]))) for r in range(15)]
                    for rk in rows[::5]])
    ts5 = ts[::5]
    out = {}
    for frac in (0.05, 0.10, 0.20):
        arr = {}
        for sh in range(6, 13):
            col = sab[:, sh]
            t = first_crossing(col, ts5, frac * float(col.max()))
            if t is not None:
                arr[sh] = t
        rr = np.array(sorted(arr), dtype=float)
        tt = np.array([arr[s] for s in sorted(arr)], dtype=float)
        slope, _ = np.polyfit(rr, tt, 1)
        pred = slope * rr + np.polyfit(rr, tt, 1)[1]
        r2 = 1 - float(np.sum((tt - pred) ** 2)) / float(np.sum((tt - tt.mean()) ** 2))
        out[f"thr{frac:g}"] = {"v": float(1 / slope), "r2": r2, "n": len(arr)}
        print(f"K3 thr={frac:g}: " + json.dumps(out[f"thr{frac:g}"]), flush=True)
    return out


def k4_h_variants():
    L, T = 28, 20.0
    g, order, c3, h, eu, ev = _j2_setup(L)
    nodes = _j2_src_nodes(L)
    idx = {v: i for i, v in enumerate(order)}
    pins = [idx[v] for v in nodes]
    pred = steady_predict(h, pins, [1.0], OM_J2)
    coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    pkt = gaussian_packet(coords, order, (20.0, 0.0), (0.3, 0.0), 4.0,
                          periods=(L, L))
    ns = int(round(T / DT))
    rec = pinning_evolve(pred + pkt, h, DT, ns, pins,
                         harmonic_pins([1.0], OM_J2, DT))
    rows = rec["psi"]
    fp_rows, fp_ts = final_period_rows(rows, DT, OM_J2)
    A = stroboscopic_separate(fp_rows, fp_ts, OM_J2)["A"]
    dist = dist_from_set(g, nodes)
    pm = shell_means_node(np.abs(pred), order, dist, 6)
    am = shell_means_node(np.abs(A), order, dist, 6)
    per_shell = {r: abs(am[r] - pm[r]) / max(pm[r], 0.01) for r in range(7)}
    # accounting variant: residual after subtracting rotating steady state
    t_end = (rows.shape[0] - 1) * DT
    steady_t = pred * np.exp(-1.0j * OM_J2 * t_end)
    resid = rows[-1] - steady_t
    mloc = np.array([dist[v] <= 4 for v in order])
    out = {
        "legacy_per_shell": per_shell,
        "legacy_ok": bool(all(v < 0.10 for v in per_shell.values())),
        "inner_max": max(per_shell[r] for r in range(5)),
        "resid_local": float(np.linalg.norm(resid[mloc])),
        "resid_far": float(np.linalg.norm(resid[~mloc])),
        "pkt_norm": float(np.linalg.norm(pkt)),
        "steady_norm": float(np.linalg.norm(pred)),
    }
    print("K4: " + json.dumps(out, default=str), flush=True)
    return out


def main() -> int:
    res = {"K1": k1_ramp_grid(), "K2": k2_rb_trend(), "K3": k3_front_thresh(),
           "K4": k4_h_variants()}
    json.dump(res, open("/tmp/pot1_calib.json", "w"), indent=1)
    print("wrote /tmp/pot1_calib.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
