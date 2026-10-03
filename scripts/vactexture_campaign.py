"""VAC-TEXTURE-0 spatial-texture campaign (FROZEN protocol).

Consumes read-only: VAC-FIELD-0, VAC-COMP-0 (uniform RP1 circle), SYM-0,
MALUS/QUOT ([H,S] = 0, H P_- = 0), HIDDEN-0 (local/remote readouts),
HIDDEN-BR (ledger), BG-RESP-0 (susceptibility context), FIELD-0 (witness),
RESPONSE-0 (kernel context), ZERO-0 (protection form). No graph dynamics.
No transition measure. No vacuum selection. No continuum action imposed:
gradient scaling is derived from measured observables. Deterministic
given seeds; parallel over independent tasks (beast 96: jobs <= 90).

Stages 0A..0Q + controls C0..C4 (see VACTEXTURE0-PREREG in
docs/DEFERRED.md). Writes data/vactexture/results.json. Exit 0 always
(verdicts are data, not errors); gates applied by vactexture_analyze.py.
"""

from __future__ import annotations

import argparse
import json
import math
import multiprocessing as mp
import os
import sys

import numpy as np

from bh_graph import vactexture as vt

DELTA_GRID = (math.pi / 8.0, math.pi / 4.0, math.pi / 2.0)
ALPHA0_GRID = (0.0, math.pi / 8.0)


# ---------------------------------------------------------------------------
# Workers (top-level for pickling)
# ---------------------------------------------------------------------------

def w_uniform(spec):
    L = int(spec["L"])
    rep = vt.control_uniform_joint(L, ledger_moves=int(spec.get("moves", 2000)))
    rows = []
    for r in rep["rows"]:
        rows.append({"alpha": float(r["alpha"]), "rung": r["rung"],
                     "Bmax": float(r["Bmax"]), "failed": list(r["failed"])})
    return {"tag": spec["tag"], "L": L, "rows": rows}


def _sweep_params(L):
    L = int(L)
    out = []
    for lam in [float(L), float(L) / 2.0]:
        if lam < 2.0:
            continue
        if abs(float(L) / lam - round(float(L) / lam)) > 1e-9:
            continue
        for d in DELTA_GRID:
            for a0 in ALPHA0_GRID:
                out.append(("sine-x", {"alpha0": float(a0), "delta": float(d),
                                       "lam": float(lam)}))
    for d in DELTA_GRID:
        for a0 in ALPHA0_GRID:
            out.append(("sine-xy", {"alpha0": float(a0), "delta": float(d),
                                    "lam": float(L)}))
    for w in (1, 2):
        for a0 in ALPHA0_GRID:
            out.append(("linear", {"alpha0": float(a0), "winding": int(w)}))
    for width in (1.0, 2.0):
        for d in DELTA_GRID:
            for a0 in (0.0,):
                out.append(("wall", {"alpha0": float(a0), "delta": float(d),
                                     "width": float(width)}))
    for d in DELTA_GRID:
        for a0 in (0.0,):
            out.append(("step", {"alpha0": float(a0), "delta": float(d)}))
    out.append(("uniform", {"alpha0": 0.0}))
    out.append(("uniform", {"alpha0": math.pi / 6.0}))
    return out


def w_sweep(spec):
    L = int(spec["L"])
    a = float(spec.get("a", 1.0))
    rows = []
    for fam, params in _sweep_params(L):
        rows.append(vt.sweep_row(fam, dict(params), L, a))
    return {"tag": spec["tag"], "L": L, "a": a, "rows": rows}


def w_sweep28(spec):
    L = 28
    a = 1.0
    rows = []
    for lam in (28.0, 14.0, 7.0):
        for d in DELTA_GRID:
            rows.append(vt.sweep_row("sine-x", {"alpha0": 0.0, "delta": float(d),
                                                "lam": float(lam)}, L, a))
    for w in (1, 2):
        rows.append(vt.sweep_row("linear", {"alpha0": 0.0, "winding": int(w)}, L, a))
    for width in (1.0, 2.0):
        rows.append(vt.sweep_row("wall", {"alpha0": 0.0, "delta": math.pi / 4.0,
                                          "width": float(width)}, L, a))
    for d in DELTA_GRID:
        rows.append(vt.sweep_row("step", {"alpha0": 0.0, "delta": float(d)}, L, a))
    rows.append(vt.sweep_row("uniform", {"alpha0": 0.0}, L, a))
    rows.append(vt.sweep_row("uniform", {"alpha0": math.pi / 6.0}, L, a))
    return {"tag": spec["tag"], "L": L, "rows": rows}


def w_amplitude(spec):
    L = int(spec["L"])
    fam = spec.get("family", "sine-x")
    params = dict(spec.get("params", {"alpha0": 0.0, "delta": math.pi / 4.0,
                                       "lam": float(L)}))
    rows = []
    for a in vt.AMPS:
        rows.append(vt.sweep_row(str(fam), dict(params), L, float(a)))
    return {"tag": spec["tag"], "L": L, "family": str(fam),
            "params": params, "rows": rows}


def w_smooth_sharp(spec):
    L = int(spec["L"])
    out = {}
    for d in DELTA_GRID:
        rep = vt.smooth_sharp_pair(L, 0.0, float(d), float(L), 2.0, 1.0)
        out[str(float(d))] = {k: (float(v) if isinstance(v, float) else v)
                              for k, v in rep.items()
                              if k in ("D", "d_rho", "d_B", "d_J")}
        out[str(float(d))]["sine_B_std"] = float(rep["sine"]["B_std"])
        out[str(float(d))]["step_B_std"] = float(rep["step"]["B_std"])
        out[str(float(d))]["sine_B_range"] = float(rep["sine"]["B_range"])
        out[str(float(d))]["step_B_range"] = float(rep["step"]["B_range"])
        out[str(float(d))]["grad_sine_max"] = float(rep["grad_sine_max"])
        out[str(float(d))]["grad_step_max"] = float(rep["grad_step_max"])
    return {"tag": spec["tag"], "L": L, "rows": out}


def w_stationarity(spec):
    L = int(spec["L"])
    sub = vt.j2_substrate(L)
    eu, ev = vt.edge_arrays_of(sub)
    h = vt.hamiltonian_of(sub)
    fams = [("uniform", {"alpha0": 0.0}),
            ("sine-x", {"alpha0": 0.0, "delta": math.pi / 4.0, "lam": float(L)}),
            ("linear", {"alpha0": 0.0, "winding": 1}),
            ("wall", {"alpha0": 0.0, "delta": math.pi / 4.0, "width": 2.0}),
            ("step", {"alpha0": 0.0, "delta": math.pi / 4.0})]
    rows = []
    for fam, params in fams:
        amap = vt.alpha_map(fam, L, dict(params))
        psi = vt.texture_state(amap, sub, 1.0)
        rep = vt.stationarity_report(psi, sub, h, eu, ev)
        em = vt.emitted_pplus_along_flow(psi, sub, h)
        rows.append({"family": fam, "params": params,
                     "rho_drift": float(rep["rho_drift"]),
                     "B_drift": float(rep["B_drift"]),
                     "J_drift": float(rep["J_drift"]),
                     "phase_rate": float(rep["phase_rate"]),
                     "frozen_err": float(rep["frozen_err"]),
                     "ok": bool(rep["ok"]),
                     "w_sym_max": float(em["w_sym_max"]),
                     "w_sym_end": float(em["w_sym_end"])})
    return {"tag": spec["tag"], "L": L, "rows": rows}


def w_carrier(spec):
    L = int(spec["L"])
    sub = vt.j2_substrate(L)
    eu, ev = vt.edge_arrays_of(sub)
    h = vt.hamiltonian_of(sub)
    rows = []
    for fam, params in [("sine-x", {"alpha0": 0.0, "delta": math.pi / 4.0,
                                    "lam": float(L)}),
                        ("step", {"alpha0": 0.0, "delta": math.pi / 4.0})]:
        amap = vt.alpha_map(fam, L, dict(params))
        psi = vt.texture_state(amap, sub, 1.0)
        rep = vt.packet_on_texture(psi, sub, h, eu, ev, eps=0.01)
        rows.append({"family": fam, "split_err": float(rep["split_err"]),
                     "frozen": float(rep["texture_frozen_err"]),
                     "speed": float(rep["speed"]), "r2": float(rep["r2"]),
                     "msd_alpha": float(rep["msd_alpha"]),
                     "ok": bool(vt.is_carrier_universal_ok(rep))})
    return {"tag": spec["tag"], "L": L, "rows": rows}


def w_observer(spec):
    L = int(spec["L"])
    sub = vt.j2_substrate(L)
    eu, ev = vt.edge_arrays_of(sub)
    rows = []
    cases = [("sine-x", {"alpha0": 0.0, "delta": math.pi / 4.0, "lam": float(L)}, 0.0),
             ("sine-x", {"alpha0": 0.0, "delta": math.pi / 8.0, "lam": float(L)}, 0.0),
             ("step", {"alpha0": 0.0, "delta": math.pi / 4.0}, 0.0),
             ("uniform", {"alpha0": math.pi / 6.0}, 0.0)]
    for fam, params, a0 in cases:
        amap = vt.alpha_map(fam, L, dict(params))
        rep = vt.texture_vs_uniform_readouts(amap, sub, eu, ev, float(a0), 1.0)
        rows.append({"family": fam, "params": params,
                     "D": float(rep["D"]), "d_rho": float(rep["d_rho"]),
                     "d_B": float(rep["d_B"]), "d_J": float(rep["d_J"]),
                     "d_coarse": float(rep["d_coarse"]),
                     "sym_tex": float(rep["sym_tex"]),
                     "sym_diff": float(rep["sym_diff"])})
    return {"tag": spec["tag"], "L": L, "rows": rows}


def w_ledger(spec):
    L = int(spec["L"])
    sub = vt.j2_substrate(L)
    eu, ev = vt.edge_arrays_of(sub)
    eu = np.asarray(eu)
    ev = np.asarray(ev)
    moves = 20000 if len(sub["order"]) > 64 else 20000
    fams = [("uniform", {"alpha0": 0.0}),
            ("uniform", {"alpha0": math.pi / 6.0}),
            ("sine-x", {"alpha0": 0.0, "delta": math.pi / 4.0, "lam": float(L)}),
            ("step", {"alpha0": 0.0, "delta": math.pi / 4.0})]
    sigs = {}
    m1 = {}
    cu = {}
    for fam, params in fams:
        key = f"{fam}@{sorted(params.items())}"
        amap = vt.alpha_map(fam, L, dict(params))
        psi = vt.texture_state(amap, sub, 1.0)
        s = vt.ledger_signature(psi, sub["graph"], sub["order"], eu, ev)
        sigs[key] = s
        m1[key] = vt.m1_stats(psi, sub["graph"], sub["order"], moves, 0)
        cu[key] = vt.contraction_uniformity(psi, sub)
    keys = sorted(sigs)
    dist = {}
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            d = vt.ledger_distance(sigs[a], sigs[b])
            dist[f"{a}||{b}"] = {k: float(v) for k, v in d.items()}
    stats = {k: {"B_mean": float(s["B_mean"]), "B_std": float(s["B_std"]),
                 "L_mean": float(s["L_mean"]), "L_std": float(s["L_std"])}
             for k, s in sigs.items()}
    cu_out = {k: {"per_class_std": {kk: float(vv) for kk, vv in v["per_class_std"].items()},
                  "uniform": bool(v["uniform"])} for k, v in cu.items()}
    return {"tag": spec["tag"], "L": L, "dist": dist, "stats": stats,
            "m1": m1, "contraction": cu_out}


def w_scaling(spec):
    rows = []
    for L in spec["Ls"]:
        rows.append(vt.size_scaling_row(int(L)))
    return {"tag": spec["tag"], "rows": rows}


def w_quotient(spec):
    L = int(spec["L"])
    rep = vt.quotient_control(L)
    return {"tag": spec["tag"], "L": L, "sym_norm": float(rep["sym_norm"]),
            "image": rep["quotient_image"]}


def w_phase(spec):
    L = int(spec["L"])
    sub = vt.j2_substrate(L)
    eu, ev = vt.edge_arrays_of(sub)
    amap = vt.alpha_map_sine_x(L, 0.0, math.pi / 4.0, float(L))
    psi = vt.texture_state(amap, sub, 1.0)
    rep = vt.control_global_phase(psi, sub, eu, ev)
    return {"tag": spec["tag"], "L": L, "dev": rep["dev"], "ok": bool(rep["ok"])}


def w_projective(spec):
    L = int(spec["L"])
    sub = vt.j2_substrate(L)
    rep = vt.control_projective_periodicity(sub, 1.0)
    return {"tag": spec["tag"], "L": L, "ok": bool(rep["ok"]),
            "uniform": rep["uniform"], "texture": rep["texture"]}


def w_covariance(spec):
    L = int(spec["L"])
    rep = vt.control_origin_covariance("sine-x",
                                       {"alpha0": 0.0, "delta": math.pi / 4.0,
                                        "lam": float(L)},
                                       L, 1, 2, 1.0)
    return {"tag": spec["tag"], "L": L, "state_dev": float(rep["state_dev"]),
            "rho_dev": float(rep["rho_dev"]), "B_dev": float(rep["B_dev"]),
            "ok": bool(rep["ok"])}


def w_witness(spec):
    L = int(spec["L"])
    from bh_graph import field0 as f0

    sub = vt.j2_substrate(L)
    h = vt.hamiltonian_of(sub)
    sub_f0 = f0.build_substrate("j2", L)
    m1 = vt.alpha_map_sine_x(L, 0.0, math.pi / 4.0, float(L))
    m2 = vt.alpha_map_step(L, 0.0, math.pi / 4.0)
    p1 = vt.texture_state(m1, sub, 1.0)
    p2 = vt.texture_state(m2, sub, 1.0)
    rep = vt.control_witness_null(p1, p2, sub_f0, h)
    return {"tag": spec["tag"], "L": L, "witness": rep["witness"],
            "ok": bool(rep["ok"])}


def w_odd(spec):
    L = int(spec["L"])
    sub = vt.j2_substrate(L)
    eu, ev = vt.edge_arrays_of(sub)
    h = vt.hamiltonian_of(sub)
    rows = []
    for fam, params in [("uniform", {"alpha0": 0.0}),
                        ("sine-x", {"alpha0": 0.0, "delta": math.pi / 4.0,
                                     "lam": float(L)})]:
        amap = vt.alpha_map(fam, L, dict(params))
        psi = vt.texture_state(amap, sub, 1.0)
        obs = vt.obstruction_report(psi, sub, h)
        ana = vt.relational_anatomy(psi, sub, eu, ev)
        rows.append({"family": fam, "w_sym": float(obs["w_sym"]),
                     "h_residual": float(obs["h_residual"]),
                     "energy": float(obs["energy"]),
                     "B_std": float(ana["B_std"]),
                     "Jmax": float(ana["Jmax"])})
    return {"tag": spec["tag"], "L": L, "rows": rows}


DISPATCH = {
    "uniform": w_uniform,
    "sweep": w_sweep,
    "sweep28": w_sweep28,
    "amplitude": w_amplitude,
    "smooth_sharp": w_smooth_sharp,
    "stationarity": w_stationarity,
    "carrier": w_carrier,
    "observer": w_observer,
    "ledger": w_ledger,
    "scaling": w_scaling,
    "quotient": w_quotient,
    "phase": w_phase,
    "projective": w_projective,
    "covariance": w_covariance,
    "witness": w_witness,
    "odd": w_odd,
}


def _run_worker(spec):
    return DISPATCH[spec["kind"]](spec)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/vactexture/results.json")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 6))
    args = ap.parse_args()

    specs = [
        {"kind": "uniform", "tag": "uniform_L4", "L": 4, "moves": 2000},
        {"kind": "uniform", "tag": "uniform_L6", "L": 6, "moves": 20000},
        {"kind": "uniform", "tag": "uniform_L28", "L": 28, "moves": 20000},
        {"kind": "sweep", "tag": "sweep_L4", "L": 4},
        {"kind": "sweep", "tag": "sweep_L8", "L": 8},
        {"kind": "sweep28", "tag": "sweep_L28"},
        {"kind": "amplitude", "tag": "amp_sine_L4", "L": 4},
        {"kind": "amplitude", "tag": "amp_sine_L28", "L": 28},
        {"kind": "smooth_sharp", "tag": "smooth_sharp_L4", "L": 4},
        {"kind": "smooth_sharp", "tag": "smooth_sharp_L28", "L": 28},
        {"kind": "stationarity", "tag": "stationary_L4", "L": 4},
        {"kind": "stationarity", "tag": "stationary_L28", "L": 28},
        {"kind": "carrier", "tag": "carrier_L28", "L": 28},
        {"kind": "observer", "tag": "observer_L4", "L": 4},
        {"kind": "observer", "tag": "observer_L28", "L": 28},
        {"kind": "ledger", "tag": "ledger_L4", "L": 4},
        {"kind": "ledger", "tag": "ledger_L28", "L": 28},
        {"kind": "scaling", "tag": "scaling", "Ls": [4, 6, 8, 12, 16, 20, 28]},
        {"kind": "quotient", "tag": "quotient_L4", "L": 4},
        {"kind": "quotient", "tag": "quotient_L28", "L": 28},
        {"kind": "phase", "tag": "phase_L4", "L": 4},
        {"kind": "phase", "tag": "phase_L28", "L": 28},
        {"kind": "projective", "tag": "projective_L4", "L": 4},
        {"kind": "projective", "tag": "projective_L28", "L": 28},
        {"kind": "covariance", "tag": "covariance_L4", "L": 4},
        {"kind": "covariance", "tag": "covariance_L28", "L": 28},
        {"kind": "witness", "tag": "witness_L4", "L": 4},
        {"kind": "odd", "tag": "odd_L5", "L": 5},
    ]
    jobs = max(1, min(int(args.jobs), len(specs)))
    if jobs == 1:
        recs = [_run_worker(s) for s in specs]
    else:
        with mp.Pool(jobs) as pool:
            recs = pool.map(_run_worker, specs)
    out = {"records": {r["tag"]: r for r in recs}}
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(out, f, indent=1, default=str)
    print(f"wrote {args.out} ({len(recs)} records)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
