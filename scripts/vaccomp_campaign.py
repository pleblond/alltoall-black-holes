"""VAC-COMP-0 complete joint-vacuum manifold campaign (FROZEN protocol).

Consumes read-only: VAC-FIELD-0 (vacfield.py), SYM-0, MALUS/QUOT/HIDDEN,
ZERO-0, EM-0, HIDDEN-BR ledger. No graph dynamics. No transition
measure. No vacuum selection (0AD firewall). Deterministic given
seeds; parallel over independent tasks (beast 96: jobs<=90).

Stages 0A..0AC + controls C0..C3 (see VACCOMP0-PREREG in
docs/DEFERRED.md). Writes data/vaccomp/results.json. Exit 0 always
(verdicts are data, not errors); gates applied by vaccomp_analyze.py.
"""

from __future__ import annotations

import argparse
import json
import math
import multiprocessing as mp
import os
import sys

import numpy as np

from bh_graph import vaccomp as vc
from bh_graph import vacfield as vf

SHAPES = ("VPLUS", "VPI", "VMINUS", "VSTAG")


def _shape(name: str, sub: dict) -> np.ndarray:
    if name == "VSTAG":
        return vc.vstag_shape(sub)
    return vf.candidate_shape(name, sub, "j2")


def _energies() -> dict:
    return {"VPLUS": -8.0, "VPI": 8.0, "VMINUS": 0.0, "VSTAG": 0.0}


# ---------------------------------------------------------------------------
# Workers (top-level for pickling)
# ---------------------------------------------------------------------------


def w_spectral(spec):
    L = int(spec["L"])
    s = vc.spectral_decomposition(L)
    rows = vc.extremal_rows(s)
    zc = vc.zero_eigenspace_census(L)
    eu = vc.extremal_uniqueness(L)
    tab = [
        [float(r["lambda"]), int(r["multiplicity"]), int(r["anti_rank"]), int(r["sym_rank"])]
        for r in s["table"]
    ]
    cand = {}
    for k, v in s["candidates"].items():
        if v is None:  # odd L: VPI has no staggered representative
            cand[k] = None
            continue
        cand[k] = {
            "rayleigh": float(v["rayleigh"]),
            "residual": float(v["residual"]),
            "max_overlap": float(v["max_overlap"]),
            "subspace_weight": float(v["subspace_weight"]),
            "nearest_lambda": float(v["nearest_lambda"]),
        }
    return {
        "tag": spec["tag"],
        "L": L,
        "n": int(s["n"]),
        "e_min": float(s["e_min"]),
        "e_max": float(s["e_max"]),
        "n_zero": int(s["n_zero"]),
        "bloch_max_dev": float(s["bloch_max_dev"]),
        "table": tab,
        "extremal": {
            k: (
                {kk: (float(vv) if isinstance(vv, float) else vv) for kk, vv in v.items()}
                if v
                else None
            )
            for k, v in rows.items()
        },
        "candidates": cand,
        "zero_census": {
            k: (
                int(v)
                if isinstance(v, (int, np.integer))
                else (float(v) if isinstance(v, float) else v)
            )
            for k, v in zc.items()
            if k != "L"
        },
        "minus8_unique": bool(eu["minus8_unique"]),
        "plus8_unique": bool(eu["plus8_unique"]),
    }


def w_statthm(spec):
    L = int(spec.get("L", 4))
    s = vc.spectral_decomposition(L)
    sub = vf.j2_substrate(L)
    eu, ev = vf.edge_arrays_of(sub)
    h = vf.hamiltonian_of(sub)
    basis = vc.eigenspace_basis(s, 0.0)
    psi = vc.random_in_subspace(basis, 7, real=False)
    rep = vc.stationarity_theorem_check(psi, h, eu, ev, 0.0)
    vm = vf.candidate_shape("VMINUS", sub, "j2")
    rep_m = vc.stationarity_theorem_check(vm, h, eu, ev, 0.0)
    return {
        "tag": spec["tag"],
        "L": L,
        "degenerate": {k: float(v) for k, v in rep.items() if k != "ok"} | {"ok": bool(rep["ok"])},
        "vminus": {k: float(v) for k, v in rep_m.items() if k != "ok"} | {"ok": bool(rep_m["ok"])},
    }


def w_generic(spec):
    L = int(spec["L"])
    kind = spec["kind2"]
    real = bool(spec.get("real", False))
    n = int(spec.get("n", 8))
    seed0 = int(spec.get("seed0", 0))
    if kind == "mid":
        s = vc.spectral_decomposition(L)
        cands = [
            r
            for r in s["table"]
            if abs(r["lambda"]) > 1e-9
            and abs(abs(r["lambda"]) - 8.0) > 1e-9
            and r["multiplicity"] >= 2
        ]
        lam = float(cands[0]["lambda"]) if cands else 0.0
    else:
        lam = 0.0
    rep = vc.generic_state_probe(L, lam, n, seed0, real, ledger_moves=2000)
    rungs = {}
    fails = {}
    for r in rep["rows"]:
        rungs[r["rung"]] = rungs.get(r["rung"], 0) + 1
        for k, v in r["checks"].items():
            if not v:
                fails[k] = fails.get(k, 0) + 1
    return {
        "tag": spec["tag"],
        "L": L,
        "lambda": float(lam),
        "real": real,
        "n": n,
        "rungs": rungs,
        "fails": fails,
    }


def w_hidden_real(spec):
    L = int(spec["L"])
    rep = vc.hidden_real_probe(
        L, int(spec.get("n", 8)), int(spec.get("seed0", 0)), ledger_moves=2000
    )
    rungs = {}
    for r in rep["rows"]:
        rungs[r["rung"]] = rungs.get(r["rung"], 0) + 1
    return {
        "tag": spec["tag"],
        "L": L,
        "real_dim": int(rep["real_dim"]),
        "proj_dim": int(rep["proj_dim"]),
        "rungs": rungs,
        "edge_max": [float(r["edge_max"]) for r in rep["rows"]],
        "rows": [
            {
                "seed": int(r["seed"]),
                "rung": r["rung"],
                "checks": {k: bool(v) for k, v in r["checks"].items()},
            }
            for r in rep["rows"]
        ],
    }


def w_hidden_complex(spec):
    L = int(spec["L"])
    rep = vc.hidden_complex_probe(L, int(spec.get("n", 16)), int(spec.get("seed0", 100)))
    return {
        "tag": spec["tag"],
        "L": L,
        "n_excluded": int(rep["n_excluded"]),
        "frac_excluded": float(rep["frac_excluded"]),
        "edge_max": [float(r["edge_max"]) for r in rep["rows"]],
    }


def w_circle(spec):
    L = int(spec["L"])
    rep = vc.circle_probe(L, ledger_moves=2000)
    rows = []
    for r in rep["rows"]:
        rows.append(
            {
                "alpha": float(r["alpha"]),
                "rung": r["rung"],
                "Bmax": float(r["Bmax"]),
                "failed": sorted(k for k, v in r["checks"].items() if not v),
            }
        )
    return {"tag": spec["tag"], "L": L, "rows": rows}


def w_bzero(spec):
    L = int(spec["L"])
    sub = vf.j2_substrate(L)
    eu, ev = vf.edge_arrays_of(sub)
    h = vf.hamiltonian_of(sub)
    cells = vc.even_sublattice_cells(L)
    rows = []
    for seed in (0, 1):
        psi = vc.independent_set_state(sub, cells, seed)
        lad = vc.joint_ladder(psi, sub, h, eu, ev, 0.0, None, 2000)
        bj = vf.bj_of(psi, eu, ev)
        rows.append(
            {
                "seed": seed,
                "energy": float(vf.rayleigh_energy(psi, h)),
                "Bmax": float(np.abs(bj["B"]).max()),
                "Jmax": float(np.abs(bj["J"]).max()),
                "rung": lad["rung"],
                "checks": {k: bool(v) for k, v in lad["checks"].items()},
            }
        )
    return {"tag": spec["tag"], "L": L, "rows": rows}


def w_amplitude(spec):
    L = int(spec["L"])
    name = spec["name"]
    sub = vf.j2_substrate(L)
    eu, ev = vf.edge_arrays_of(sub)
    h = vf.hamiltonian_of(sub)
    if name.startswith("CIRCLE@"):
        a = float(name.split("@")[1])
        psi = vc.two_value_family(sub, (a,))[a]
        energy = 0.0
    else:
        psi = _shape(name, sub)
        energy = _energies()[name]
    rep = vc.amplitude_family_ladder(psi, sub, h, eu, ev, energy, ledger_moves=2000)
    return {
        "tag": spec["tag"],
        "L": L,
        "name": name,
        "all_joint": bool(rep["all_joint"]),
        "rungs": [(float(r["a"]), r["rung"]) for r in rep["rows"]],
    }


def w_headline(spec):
    L = int(spec["L"])
    name = spec["name"]
    sub = vf.j2_substrate(L)
    eu, ev = vf.edge_arrays_of(sub)
    h = vf.hamiltonian_of(sub)
    plaq = vf.square_plaquettes_j2(L)
    if name.startswith("CIRCLE@"):
        a = float(name.split("@")[1])
        psi = vc.two_value_family(sub, (a,))[a]
        energy = 0.0
    else:
        psi = _shape(name, sub)
        energy = _energies()[name]
    lad = vc.joint_ladder(psi, sub, h, eu, ev, energy, plaq, 20000)
    return {
        "tag": spec["tag"],
        "L": L,
        "name": name,
        "rung": lad["rung"],
        "checks": {k: bool(v) for k, v in lad["checks"].items()},
        "energy": float(vf.rayleigh_energy(psi, h)),
        "Bmax_shape": float(lad["amplitude"]["Bmax_shape"]),
        "Q_slope": float(lad["amplitude"]["Q_slope"]),
        "Bmax_slope": float(lad["amplitude"]["Bmax_slope"]),
        "f0": float(lad["ledger"]["f0_mean"]),
        "fneg": float(lad["ledger"]["fneg_mean"]),
        "fpos": float(lad["ledger"]["fpos_mean"]),
        "contract_std": {k: float(v) for k, v in lad["ledger"]["contract_per_class_std"].items()},
        "drifts": {k: float(v) for k, v in lad["stationarity"].items()},
    }


def w_interp(spec):
    L = int(spec["L"])
    a, b = spec["pair"]
    sub = vf.j2_substrate(L)
    eu, ev = vf.edge_arrays_of(sub)
    h = vf.hamiltonian_of(sub)
    E = _energies()
    rep = vc.interpolation_sweep(
        _shape(a, sub), _shape(b, sub), sub, h, eu, ev, E[a], E[b], ledger_moves=1000
    )
    return {
        "tag": spec["tag"],
        "L": L,
        "pair": [a, b],
        "dE": float(rep["dE"]),
        "max_rho_drift": float(max(r["rho_drift"] for r in rep["rows"])),
        "max_B_drift": float(max(r["B_drift"] for r in rep["rows"])),
        "max_J_drift": float(max(r["J_drift"] for r in rep["rows"])),
        "cut": [(float(c["alpha"]), bool(c["stationary"]), c["rung"]) for c in rep["cut"]],
        "n_interior_joint": int(rep["n_interior_joint"]),
    }


def w_beat(spec):
    L = int(spec["L"])
    a, b = spec["pair"]
    sub = vf.j2_substrate(L)
    eu, ev = vf.edge_arrays_of(sub)
    h = vf.hamiltonian_of(sub)
    E = _energies()
    pa, pb = _shape(a, sub), _shape(b, sub)
    ba = vc.beat_anatomy(pa, pb, E[a], E[b], sub, h, eu, ev)
    cc = vc.cross_cancellation_check(pa, pb, eu, ev)
    return {
        "tag": spec["tag"],
        "L": L,
        "pair": [a, b],
        "dE": float(ba["dE"]),
        "rho_beat_amp": float(ba["rho_beat_amp"]),
        "beat_corr": float(ba["beat_corr"]),
        "cross_max": float(ba["cross_max"]),
        "cross_rms": float(ba["cross_rms"]),
        "rho_x_max": float(cc["rho_x_max"]),
        "B_x_max": float(cc["B_x_max"]),
        "J_x_max": float(cc["J_x_max"]),
        "cancelled": bool(cc["cancelled"]),
    }


def w_orbits(spec):
    L = int(spec["L"])
    sub = vf.j2_substrate(L)
    out = {}
    for name in SHAPES:
        rep = vc.orbit_census(_shape(name, sub), sub["order"], L)
        out[name] = {
            "stabilizer_size": int(rep["stabilizer_size"]),
            "orbit_size": int(rep["orbit_size"]),
            "ray_TI": bool(rep["ray_TI"]),
            "sheet_ray_invariant": bool(rep["sheet_ray_invariant"]),
            "max_orbit_fs": float(rep["max_orbit_fs"]),
        }
    return {"tag": spec["tag"], "L": L, "orbits": out}


def w_coarse(spec):
    L = int(spec["L"])
    sub = vf.j2_substrate(L)
    order, c3 = sub["order"], sub["c3"]
    shapes = {n: _shape(n, sub) for n in SHAPES}
    shapes["CIRCLE@pi/8"] = vc.two_value_family(sub, (math.pi / 8,))[math.pi / 8]
    keys = sorted(shapes)
    dist = {}
    for i, a in enumerate(keys):
        for b in keys[i + 1 :]:
            d = vc.coarse_distance(shapes[a], shapes[b], order, c3)
            dist[f"{a}|{b}"] = float(d["d_coarse_rho"])
    return {"tag": spec["tag"], "L": L, "dist": dist}


def w_excit(spec):
    L = int(spec["L"])
    sub = vf.j2_substrate(L)
    h = vf.hamiltonian_of(sub)
    rep = vc.excitation_fingerprint(sub, h)
    return {"tag": spec["tag"], "L": L, "fp": rep}


def w_ledger(spec):
    L = int(spec["L"])
    sub = vf.j2_substrate(L)
    eu, ev = vf.edge_arrays_of(sub)
    sigs = {}
    for name in SHAPES:
        s = vc.ledger_signature(_shape(name, sub), sub["graph"], sub["order"], eu, ev)
        sigs[name] = s
    dist = {}
    for i, a in enumerate(SHAPES):
        for b in SHAPES[i + 1 :]:
            d = vc.ledger_distance(sigs[a], sigs[b])
            dist[f"{a}|{b}"] = {k: float(v) for k, v in d.items()}
    stats = {
        n: {
            "B_mean": float(s["B_mean"]),
            "B_std": float(s["B_std"]),
            "L_mean": float(s["L_mean"]),
            "L_std": float(s["L_std"]),
        }
        for n, s in sigs.items()
    }
    return {"tag": spec["tag"], "L": L, "dist": dist, "stats": stats}


def w_zero(spec):
    L = int(spec["L"])
    sub = vf.j2_substrate(L)
    eu, ev = vf.edge_arrays_of(sub)
    out = {}
    for name in SHAPES:
        psi = _shape(name, sub)
        rows = vc.zero_limit_rows(psi, sub, eu, ev)["rows"]
        pr = vc.protection_radius(psi)
        out[name] = {
            "rows": [
                [float(r["a"]), float(r["Q"]), float(r["Bmax"]), float(r["Jmax"]), float(r["E"])]
                for r in rows
            ],
            "min_abs": float(pr["min_abs"]),
            "r_prot": float(pr["r_prot"]),
            "zero_free": bool(pr["zero_free"]),
        }
    return {"tag": spec["tag"], "L": L, "shapes": out}


def w_scaling(spec):
    rows = []
    for L in spec["Ls"]:
        r = vc.size_scaling_row(int(L))
        rows.append({k: (int(v) if isinstance(v, (int, np.integer)) else v) for k, v in r.items()})
    return {"tag": spec["tag"], "rows": rows}


def w_quotient(spec):
    L = int(spec["L"])
    rep = vc.quotient_comparison(L)
    return {
        "tag": spec["tag"],
        "L": L,
        "m": int(rep["m"]),
        "e_min": float(rep["e_min"]),
        "e_max": float(rep["e_max"]),
        "n_zero": int(rep["n_zero"]),
        "nodal": int(rep["nodal"]),
        "VPLUS": {k: float(v) for k, v in rep["VPLUS"].items()},
        "VPI": {k: float(v) for k, v in rep["VPI"].items()},
        "VMINUS_quotient": rep["VMINUS_quotient"],
    }


def w_square(spec):
    L = int(spec["L"])
    rep = vc.square_control(L)
    return {
        "tag": spec["tag"],
        "L": L,
        "n": int(rep["n"]),
        "e_min": float(rep["e_min"]),
        "e_max": float(rep["e_max"]),
        "n_zero": int(rep["n_zero"]),
        "VPLUS": {
            "rayleigh": float(rep["VPLUS"]["rayleigh"]),
            "residual": float(rep["VPLUS"]["residual"]),
            "current_free": bool(rep["VPLUS"]["current_free"]),
            "stress": bool(rep["VPLUS"]["stress"]),
        },
        "VPI": {
            "rayleigh": float(rep["VPI"]["rayleigh"]),
            "residual": float(rep["VPI"]["residual"]),
            "current_free": bool(rep["VPI"]["current_free"]),
            "stress": bool(rep["VPI"]["stress"]),
        },
    }


def w_odd(spec):
    L = int(spec["L"])
    s = vc.spectral_decomposition(L)
    rows = vc.extremal_rows(s)
    sub = vf.j2_substrate(L)
    eu, ev = vf.edge_arrays_of(sub)
    h = vf.hamiltonian_of(sub)
    vm = vf.candidate_shape("VMINUS", sub, "j2")
    lad = vc.joint_ladder(vm, sub, h, eu, ev, 0.0, None, 2000)
    try:
        vc.vstag_shape(sub)
        vstg = "constructed (unexpected)"
    except ValueError:
        vstg = "raises (even-L only)"
    try:
        vpi = vf.candidate_shape("VPI", sub, "j2")
        vpi_ray = float(vf.rayleigh_energy(vpi, h))
    except ValueError:
        vpi_ray = None  # odd L: frustrated top, no staggered representative
    return {
        "tag": spec["tag"],
        "L": L,
        "n": int(s["n"]),
        "e_min": float(s["e_min"]),
        "e_max": float(s["e_max"]),
        "n_zero": int(s["n_zero"]),
        "plus8_row": rows["plus8"],
        "vpi_rayleigh": vpi_ray,
        "vminus_rung": lad["rung"],
        "vminus_checks": {k: bool(v) for k, v in lad["checks"].items()},
        "vstag": vstg,
    }


DISPATCH = {
    "spectral": w_spectral,
    "statthm": w_statthm,
    "generic": w_generic,
    "hidden_real": w_hidden_real,
    "hidden_complex": w_hidden_complex,
    "circle": w_circle,
    "bzero": w_bzero,
    "amplitude": w_amplitude,
    "headline": w_headline,
    "interp": w_interp,
    "beat": w_beat,
    "orbits": w_orbits,
    "coarse": w_coarse,
    "excit": w_excit,
    "ledger": w_ledger,
    "zero": w_zero,
    "scaling": w_scaling,
    "quotient": w_quotient,
    "square": w_square,
    "odd": w_odd,
}


def _run_worker(spec):
    return DISPATCH[spec["kind"]](spec)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/vaccomp/results.json")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 6))
    args = ap.parse_args()

    specs = [
        {"kind": "spectral", "tag": "spectral_L4", "L": 4},
        {"kind": "spectral", "tag": "spectral_L5", "L": 5},
        {"kind": "spectral", "tag": "spectral_L6", "L": 6},
        {"kind": "spectral", "tag": "spectral_L8", "L": 8},
        {"kind": "statthm", "tag": "stattheorem_L4", "L": 4},
        {
            "kind": "generic",
            "tag": "gen_zero_complex",
            "L": 4,
            "kind2": "zero",
            "real": False,
            "n": 16,
            "seed0": 0,
        },
        {
            "kind": "generic",
            "tag": "gen_zero_real",
            "L": 4,
            "kind2": "zero",
            "real": True,
            "n": 8,
            "seed0": 0,
        },
        {
            "kind": "generic",
            "tag": "gen_mid_complex",
            "L": 4,
            "kind2": "mid",
            "real": False,
            "n": 8,
            "seed0": 0,
        },
        {"kind": "hidden_real", "tag": "hidden_real_L4", "L": 4, "n": 8, "seed0": 0},
        {"kind": "hidden_complex", "tag": "hidden_complex_L4", "L": 4, "n": 16, "seed0": 100},
        {"kind": "circle", "tag": "circle_L4", "L": 4},
        {"kind": "circle", "tag": "circle_L6", "L": 6},
        {"kind": "bzero", "tag": "bzero_L4", "L": 4},
        {"kind": "amplitude", "tag": "amp_VPLUS_L4", "L": 4, "name": "VPLUS"},
        {"kind": "amplitude", "tag": "amp_VPI_L4", "L": 4, "name": "VPI"},
        {"kind": "amplitude", "tag": "amp_VMINUS_L4", "L": 4, "name": "VMINUS"},
        {"kind": "amplitude", "tag": "amp_VSTAG_L4", "L": 4, "name": "VSTAG"},
        {"kind": "amplitude", "tag": "amp_CIRCLE_L4", "L": 4, "name": "CIRCLE@0.5235987755982988"},
        {"kind": "headline", "tag": "lad_VPLUS_28", "L": 28, "name": "VPLUS"},
        {"kind": "headline", "tag": "lad_VPI_28", "L": 28, "name": "VPI"},
        {"kind": "headline", "tag": "lad_VMINUS_28", "L": 28, "name": "VMINUS"},
        {"kind": "headline", "tag": "lad_VSTAG_28", "L": 28, "name": "VSTAG"},
        {"kind": "headline", "tag": "lad_CIRCLE_28", "L": 28, "name": "CIRCLE@0.5235987755982988"},
        {"kind": "interp", "tag": "interp_PM", "L": 4, "pair": ["VPLUS", "VMINUS"]},
        {"kind": "interp", "tag": "interp_PPI", "L": 4, "pair": ["VPLUS", "VPI"]},
        {"kind": "interp", "tag": "interp_PIM", "L": 4, "pair": ["VPI", "VMINUS"]},
        {"kind": "interp", "tag": "interp_MSTAG", "L": 4, "pair": ["VMINUS", "VSTAG"]},
        {"kind": "beat", "tag": "beat_PPI", "L": 4, "pair": ["VPLUS", "VPI"]},
        {"kind": "beat", "tag": "beat_PM", "L": 4, "pair": ["VPLUS", "VMINUS"]},
        {"kind": "beat", "tag": "beat_PIM", "L": 4, "pair": ["VPI", "VMINUS"]},
        {"kind": "orbits", "tag": "orbits_L4", "L": 4},
        {"kind": "coarse", "tag": "coarse_L4", "L": 4},
        {"kind": "excit", "tag": "excit_L4", "L": 4},
        {"kind": "ledger", "tag": "ledger_L4", "L": 4},
        {"kind": "zero", "tag": "zero_L4", "L": 4},
        {"kind": "scaling", "tag": "scaling", "Ls": [4, 5, 6, 8, 12, 16, 20, 28]},
        {"kind": "quotient", "tag": "quotient_L4", "L": 4},
        {"kind": "quotient", "tag": "quotient_L6", "L": 6},
        {"kind": "square", "tag": "square_L4", "L": 4},
        {"kind": "square", "tag": "square_L6", "L": 6},
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
