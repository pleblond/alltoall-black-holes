"""POT-1 Amendment-2 calibration round 3 (beast): tau-ladder anchors,
path turn-on, inner-profile + background-subtraction feasibility.

Parallel over cases (mp). All runs cosine ramp unless noted.
"""
from __future__ import annotations

import json
import math
import multiprocessing as mp
import sys

import numpy as np

sys.path.insert(0, "src")
sys.path.insert(0, "scripts")

from pot1_campaign import DT, OM_J2, OM_PA, OM_PB, _j2_id, _j2_setup  # noqa: E402
from bh_graph.ballistic import hamiltonian, node_order  # noqa: E402
from bh_graph.driven import (  # noqa: E402
    bilinears,
    dist_from_set,
    final_period_rows,
    path_graph,
    path_kappa,
    period_epsilon,
    pinning_evolve,
    steady_predict,
    stroboscopic_separate,
)


def _ramp_fn(s_vals, omega, tau):
    s_vals = np.asarray(s_vals, dtype=np.complex128)

    def fn(step: int) -> np.ndarray:
        t = (step + 1) * DT
        f = 0.5 * (1.0 - math.cos(math.pi * t / tau)) if t < tau else 1.0
        return f * s_vals * np.exp(-1.0j * float(omega) * t)

    return fn


def _j2_case(spec):
    L, tau, T = spec["L"], spec["tau"], spec["T"]
    g, order, c3, h, eu, ev = _j2_setup(L)
    nodes = [_j2_id(L, 0, 0)]
    idx = {v: i for i, v in enumerate(order)}
    pins = [idx[v] for v in nodes]
    pred = steady_predict(h, pins, [1.0], OM_J2)
    dist = dist_from_set(g, nodes)
    dvec = np.array([dist[v] for v in order])
    ns = int(round(T / DT))
    rec = pinning_evolve(np.zeros(len(order), dtype=np.complex128), h, DT, ns,
                         pins, _ramp_fn([1.0], OM_J2, tau))
    rows = rec["psi"]
    fp_rows, fp_ts = final_period_rows(rows, DT, OM_J2)
    sep = stroboscopic_separate(fp_rows, fp_ts, OM_J2)
    A = sep["A"]
    fin = bilinears(rows[-1], eu, ev)
    mask = np.array([dist[v] <= 6 for v in order])
    m_in = dvec <= 4
    c = float(np.median(np.abs(A[dvec >= 10]))) if (dvec >= 10).any() else 0.0
    rr = np.array([2, 3, 4, 5], dtype=float)
    vv = np.array([float(np.mean(np.abs(A[dvec == r]))) for r in (2, 3, 4, 5)])
    xi_raw = float(-np.polyfit(rr, np.log(np.maximum(vv, 1e-300)), 1)[0])
    vs = np.maximum(vv - c, 1e-300)
    xi_sub = float(-np.polyfit(rr, np.log(vs), 1)[0])
    return {"tag": spec["tag"],
            "ramp_global": float(np.linalg.norm(A - pred) / np.linalg.norm(pred)),
            "inner_global": float(np.linalg.norm(A[m_in] - pred[m_in])
                                  / np.linalg.norm(pred[m_in])),
            "Fmag": float(np.linalg.norm(sep["F"])),
            "lingerer_c": c,
            "sep_resid": sep["rel_resid"],
            "eps": period_epsilon(rows, DT, OM_J2, mask),
            "JB": float(np.abs(fin["J"]).max()
                        / max(float(np.abs(fin["B"]).max()), 1e-300)),
            "xi_raw": xi_raw, "xi_sub": xi_sub}


def _path_case(spec):
    n, om, tau, T = spec["n"], spec["om"], spec["tau"], spec["T"]
    g = path_graph(n)
    order = node_order(g)
    h = hamiltonian(g, order=order)
    pred = steady_predict(h, [0, n - 1], [1.0, -1.0], om)
    ns = int(round(T / DT))
    rec = pinning_evolve(np.zeros(n, dtype=np.complex128), h, DT, ns,
                         [0, n - 1], _ramp_fn([1.0, -1.0], om, tau))
    rows = rec["psi"]
    fp_rows, fp_ts = final_period_rows(rows, DT, om)
    A = stroboscopic_separate(fp_rows, fp_ts, om)["A"]
    dist0 = dist_from_set(g, [0])
    dvec = np.array([dist0[v] for v in order])
    c = float(np.median(np.abs(A[(dvec >= 20) & (dvec <= 40)])))
    rr = np.array([r for r in range(2, 9)], dtype=float)
    vv = np.array([float(np.mean(np.abs(A[dvec == r]))) for r in range(2, 9)])
    kap_raw = float(-np.polyfit(rr, np.log(np.maximum(vv, 1e-300)), 1)[0])
    kap_sub = float(-np.polyfit(rr, np.log(np.maximum(vv - c, 1e-300)), 1)[0])
    return {"tag": spec["tag"],
            "ramp_global": float(np.linalg.norm(A - pred) / np.linalg.norm(pred)),
            "lingerer_c": c, "kap_raw": kap_raw, "kap_sub": kap_sub,
            "kap_theory": path_kappa(om),
            "eps": period_epsilon(rows, DT, om)}


def _solve_case(spec):
    # Fast containment/delta numbers from solves (no evolution).
    tag = spec["tag"]
    if tag == "AP_delta":
        L = 28
        g, order, c3, h, eu, ev = _j2_setup(L)
        idx = {v: i for i, v in enumerate(order)}
        nodes = [_j2_id(L, 0, 0)]
        pu = steady_predict(h, [idx[v] for v in nodes], [1.0], OM_J2)
        gw = g.copy()
        for y in range(L):
            if y == 1:
                continue
            for b1 in (0, 1):
                for b2 in (0, 1):
                    u, v = _j2_id(L, 1, y, b1), _j2_id(L, 2, y, b2)
                    if gw.has_edge(u, v):
                        gw.remove_edge(u, v)
        pw = steady_predict(hamiltonian(gw, order=order),
                            [idx[v] for v in nodes], [1.0], OM_J2)
        return {"tag": tag, "delta": float(np.linalg.norm(pw - pu)
                                           / np.linalg.norm(pu))}
    L = spec["L"]
    g, order, c3, h, eu, ev = _j2_setup(L)
    idx = {v: i for i, v in enumerate(order)}
    nodes = [_j2_id(L, 0, 0)]
    pred = steady_predict(h, [idx[v] for v in nodes], [1.0], OM_J2)
    dist = dist_from_set(g, nodes)
    dvec = np.array([dist[v] for v in order])
    n2 = float(np.vdot(pred, pred).real)
    return {"tag": tag,
            "contain_r4": float(np.vdot(pred[dvec <= 4], pred[dvec <= 4]).real / n2),
            "contain_r3": float(np.vdot(pred[dvec <= 3], pred[dvec <= 3]).real / n2)}


def _run_case(spec):
    fn = {"j2": _j2_case, "path": _path_case, "solve": _solve_case}[spec["fn"]]
    r = fn(spec)
    print(json.dumps(r), flush=True)
    return r


def main() -> int:
    cases = []
    for tau in (4.0, 8.0, 12.0):
        cases.append({"fn": "j2", "tag": f"j2_L20_tau{tau:g}_T16",
                      "L": 20, "tau": tau, "T": 16.0})
    for om, nm in ((OM_PA, "a"), (OM_PB, "b")):
        cases.append({"fn": "path", "tag": f"path_{nm}_tau8_T12",
                      "n": 60, "om": om, "tau": 8.0, "T": 12.0})
    for L in (20, 28, 42):
        cases.append({"fn": "solve", "tag": f"contain_L{L}", "L": L})
    cases.append({"fn": "solve", "tag": "AP_delta"})

    with mp.get_context("fork").Pool(10) as pool:
        res = pool.map(_run_case, cases)
    json.dump({r["tag"]: r for r in res}, open("/tmp/pot1_calib3.json", "w"), indent=1)
    print("wrote /tmp/pot1_calib3.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
