"""POT-1 Amendment-2 calibration round 2: Planck-taper ramp + RB accounting."""
from __future__ import annotations

import json
import math
import sys

import numpy as np

sys.path.insert(0, "src")
sys.path.insert(0, "scripts")

from pot1_campaign import DT, OM_J2, _j2_setup, _j2_src_nodes  # noqa: E402
from bh_graph.driven import (  # noqa: E402
    bilinears,
    dist_from_set,
    final_period_rows,
    harmonic_pins,
    period_epsilon,
    pinning_evolve,
    steady_predict,
    stroboscopic_separate,
)


def planck_fn(s_vals, omega, rise):
    s_vals = np.asarray(s_vals, dtype=np.complex128)

    def fn(step: int) -> np.ndarray:
        t = (step + 1) * DT
        if t <= 0:
            f = 0.0
        elif t >= rise:
            f = 1.0
        else:
            e = rise / t - rise / (rise - t)
            f = 0.0 if e > 700 else (1.0 if e < -700 else
                                     1.0 / (1.0 + math.exp(e)))
        return f * s_vals * np.exp(-1.0j * float(omega) * t)

    return fn


def k5_planck():
    out = {}
    for L in (12, 20):
        g, order, c3, h, eu, ev = _j2_setup(L)
        nodes = _j2_src_nodes(L)
        idx = {v: i for i, v in enumerate(order)}
        pins = [idx[v] for v in nodes]
        pred = steady_predict(h, pins, [1.0], OM_J2)
        dist = dist_from_set(g, nodes)
        for rise in (4.0, 8.0):
            for T in (12.0, 24.0):
                ns = int(round(T / DT))
                rec = pinning_evolve(np.zeros(len(order), dtype=np.complex128),
                                     h, DT, ns, pins,
                                     planck_fn([1.0], OM_J2, rise))
                rows = rec["psi"]
                fp_rows, fp_ts = final_period_rows(rows, DT, OM_J2)
                sep = stroboscopic_separate(fp_rows, fp_ts, OM_J2)
                fin = bilinears(rows[-1], eu, ev)
                mask = np.array([dist[v] <= 6 for v in order])
                key = f"L{L}_rise{rise:g}_T{T:g}"
                out[key] = {
                    "ramp_global": float(np.linalg.norm(sep["A"] - pred)
                                         / np.linalg.norm(pred)),
                    "Fmag": float(np.linalg.norm(sep["F"])),
                    "sep_resid": sep["rel_resid"],
                    "eps": period_epsilon(rows, DT, OM_J2, mask),
                    "JB": float(np.abs(fin["J"]).max()
                                / max(float(np.abs(fin["B"]).max()), 1e-300)),
                }
                print(f"K5 {key}: " + json.dumps(out[key]), flush=True)
    return out


def k2b_long_jump():
    out = {}
    for L in (28, 42):
        g, order, c3, h, eu, ev = _j2_setup(L)
        nodes = _j2_src_nodes(L)
        idx = {v: i for i, v in enumerate(order)}
        pins = [idx[v] for v in nodes]
        psi0 = steady_predict(h, pins, [1.0], OM_J2)
        T = 40.0
        ns = int(round(T / DT))
        rec = pinning_evolve(psi0, h, DT, ns, pins,
                             harmonic_pins([1.0], OM_J2, DT))
        n12 = int(round(12.0 / DT))
        seg = rec["work"][-n12:]
        nrm = rec["norms"]
        out[f"L{L}"] = {
            "net12": float(seg.sum()),
            "gross12": float(np.abs(seg).sum()),
            "ratio12": float(abs(seg.sum()) / max(np.abs(seg).sum(), 1e-300)),
            "normdrift12": float(abs(nrm[-1] - nrm[-n12]) / max(nrm[-1], 1e-300)),
            "norm": float(nrm[-1]),
        }
        print(f"K2b L{L}: " + json.dumps(out[f"L{L}"]), flush=True)
    return out


def main() -> int:
    res = {"K5": k5_planck(), "K2b": k2b_long_jump()}
    json.dump(res, open("/tmp/pot1_calib2.json", "w"), indent=1)
    print("wrote /tmp/pot1_calib2.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
