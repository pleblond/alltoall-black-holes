"""POT-1 Amendment-3 verification (pre-freeze, beast): path tau=12 trial
(per-shell breakdown of the v3 A_a_ramp_shell miss) + jump-vehicle wrap
drift (J_wrap redesign check). All cheap.
"""
from __future__ import annotations

import json
import math
import sys

import numpy as np

sys.path.insert(0, "src")
sys.path.insert(0, "scripts")

from pot1_campaign import DT, OM_J2, OM_PA, OM_PB, _j2_id, _j2_setup  # noqa: E402
from bh_graph.ballistic import hamiltonian, node_order  # noqa: E402
from bh_graph.driven import (  # noqa: E402
    dist_from_set,
    final_period_rows,
    harmonic_pins,
    path_graph,
    pinning_evolve,
    shell_means_node,
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


def path_trial(om, tau, T=12.0, n=60):
    g = path_graph(n)
    order = node_order(g)
    h = hamiltonian(g, order=order)
    pred = steady_predict(h, [0, n - 1], [1.0, -1.0], om)
    ns = int(round(T / DT))
    rec = pinning_evolve(np.zeros(n, dtype=np.complex128), h, DT, ns,
                         [0, n - 1], _ramp_fn([1.0, -1.0], om, tau))
    fp_rows, fp_ts = final_period_rows(rec["psi"], DT, om)
    A = stroboscopic_separate(fp_rows, fp_ts, om)["A"]
    dist = dist_from_set(g, [0, n - 1])
    pm = shell_means_node(np.abs(pred), order, dist, 4)
    am = shell_means_node(np.abs(A), order, dist, 4)
    per = {r: {"pred": pm[r], "meas": am[r],
               "rel": abs(am[r] - pm[r]) / max(pm[r], 1e-300)}
           for r in range(5)}
    m = np.array([dist[v] <= 4 for v in order])
    ig = float(np.linalg.norm(A[m] - pred[m]) / np.linalg.norm(pred[m]))
    return {"per_shell": per, "inner_global": ig,
            "pass_025": all(v["rel"] < 0.25 or v["pred"] < 0.01
                            for v in per.values())}


def jump_wrap():
    L, om = 28, OM_J2
    g, order, c3, h, eu, ev = _j2_setup(L)
    nodes = [_j2_id(L, 0, 0)]
    idx = {v: i for i, v in enumerate(order)}
    pins = [idx[v] for v in nodes]
    pred = steady_predict(h, pins, [1.0], om)
    dist = dist_from_set(g, nodes)
    out = {}
    for T in (8.0, 16.0):
        ns = int(round(T / DT))
        rec = pinning_evolve(pred, h, DT, ns, pins,
                             harmonic_pins([1.0], om, DT))
        t_end = (rec["psi"].shape[0] - 1) * DT
        out[T] = rec["psi"][-1] * np.exp(1.0j * om * t_end)
    m8 = shell_means_node(np.abs(out[8.0]), order, dist, 4)
    m16 = shell_means_node(np.abs(out[16.0]), order, dist, 4)
    per = {r: abs(m16[r] - m8[r]) / max(m8[r], 1e-300) for r in range(5)}
    return {"per_shell_drift": per,
            "pass_005": bool(all(per[r] < 0.05 for r in range(5)
                                 if m8[r] > 0.01))}


def main() -> int:
    res = {}
    for om, nm in ((OM_PA, "a"), (OM_PB, "b")):
        for tau in (8.0, 12.0):
            key = f"path_{nm}_tau{tau:g}"
            res[key] = path_trial(om, tau)
            print(key, json.dumps(res[key]), flush=True)
    res["jump_wrap"] = jump_wrap()
    print("jump_wrap", json.dumps(res["jump_wrap"]), flush=True)
    json.dump(res, open("/tmp/pot1_calib4.json", "w"), indent=1)
    print("wrote /tmp/pot1_calib4.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
