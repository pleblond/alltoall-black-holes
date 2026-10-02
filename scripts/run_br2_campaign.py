"""BR-2 campaign runner: frozen protocol, deterministic, formation-free.

Fixed-envelope sublattice-stagger sweep psi(phi) = rho e^{i phi q} over the
frozen 8-point full-cycle grid, on J2-L28 (sampled, paired moves across phi),
J2-L8 + ring-60 (exhaustive); BR-2A replication cells (E1/E2/E3p reps);
rescale + global-phase control cells; endpoint-strict G-census + premise;
current readouts (net directional + staggered flux) per state.
Writes data/br2_phase.json. Usage: python3 scripts/run_br2_campaign.py
"""

import datetime
import json
import subprocess
import sys

import networkx as nx
import numpy as np

sys.path.insert(0, "src")

from bh_graph.backreaction import (  # noqa: E402
    EPS_DEFAULT,
    J_BR0,
    delta_e_full,
    delta_e_local,
    run_landscape,
    run_landscape_exhaustive,
    sample_relocations,
)
from bh_graph.ballistic import (  # noqa: E402
    gaussian_packet,
    index_of,
    is_normalized_ok,
    node_order,
    ring_coords,
)
from bh_graph.formation import j2_torus_coords, j2_torus_graph  # noqa: E402
from bh_graph.phase import (  # noqa: E402
    PHI_GRID,
    directional_current,
    premise_strict,
    run_strict_census,
    stagger_state,
    staggered_current,
    sublattice_j2,
    sublattice_ring,
)

N_MOVES = 200_000
SEEDS = (0, 1, 2)
EPS = EPS_DEFAULT
C0_N = 2000
R_IN, R_OUT = 7.0, 8.0


def j2_setup(L, r0, sigma, k):
    g = j2_torus_graph(L)
    order = node_order(g)
    c3 = j2_torus_coords(L)
    coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    psi = gaussian_packet(coords, order, tuple(r0), tuple(k), sigma, (L, L))
    assert is_normalized_ok(psi)
    sub = sublattice_j2(c3)
    return {"graph": g, "order": order, "coords": coords, "periods": (L, L),
            "r0": tuple(r0), "sigma": float(sigma), "seed_psi": psi, "sub": sub,
            "ndim": 2}


def ring_setup(n, r0, sigma, k):
    g = nx.cycle_graph(n)
    order = node_order(g)
    psi = gaussian_packet(ring_coords(n), order, tuple(r0), tuple(k), sigma, (n,))
    assert is_normalized_ok(psi)
    return {"graph": g, "order": order, "coords": ring_coords(n), "periods": (n,),
            "r0": tuple(r0), "sigma": float(sigma), "seed_psi": psi,
            "sub": sublattice_ring(n), "ndim": 1}


def rho_q(setup):
    rho = np.abs(setup["seed_psi"])
    q = np.array([setup["sub"][v] for v in setup["order"]], dtype=int)
    return rho, q


def currents(setup, psi):
    out = {}
    for ax in range(setup["ndim"]):
        out[f"J_net_ax{ax}"] = directional_current(
            psi, setup["graph"], setup["order"], setup["coords"],
            setup["periods"], ax, J_BR0)
    out["J_stag"] = staggered_current(psi, setup["graph"], setup["order"],
                                      setup["sub"], J_BR0)
    return out


def run_sweep_sampled(tag, setup, meta):
    rho, q = rho_q(setup)
    cells = {}
    for phi in PHI_GRID:
        psi = stagger_state(rho, q, phi)
        assert is_normalized_ok(psi)
        per_seed = {}
        for s in SEEDS:
            per_seed[str(s)] = run_landscape(
                setup["graph"], setup["order"], setup["coords"], setup["periods"],
                psi, setup["r0"], setup["sigma"], N_MOVES, s, J_BR0, EPS)
        cells[str(phi)] = {"seeds": per_seed, "currents": currents(setup, psi),
                           "e_psi": per_seed["0"]["e_psi"]}
    return {"tag": tag, "meta": meta, "cells": cells}


def run_sweep_exhaustive(tag, setup, meta):
    rho, q = rho_q(setup)
    cells = {}
    for phi in PHI_GRID:
        psi = stagger_state(rho, q, phi)
        assert is_normalized_ok(psi)
        r = run_landscape_exhaustive(setup["graph"], setup["order"], setup["coords"],
                                     setup["periods"], psi, setup["r0"],
                                     setup["sigma"], J_BR0, EPS)
        cells[str(phi)] = {"record": r, "currents": currents(setup, psi),
                           "e_psi": r["e_psi"]}
    return {"tag": tag, "meta": meta, "cells": cells}


def run_rep(tag, setup, psi, meta, seeds=SEEDS):
    per_seed = {}
    for s in seeds:
        per_seed[str(s)] = run_landscape(
            setup["graph"], setup["order"], setup["coords"], setup["periods"],
            psi, setup["r0"], setup["sigma"], N_MOVES, s, J_BR0, EPS)
    return {"tag": tag, "meta": meta, "seeds": per_seed,
            "currents": currents(setup, psi), "e_psi": per_seed["0"]["e_psi"]}


def main():
    out = {
        "meta": {
            "date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "n_moves": N_MOVES,
            "seeds": list(SEEDS),
            "eps": EPS,
            "j": J_BR0,
            "phi_grid": list(PHI_GRID),
            "r_in": R_IN,
            "r_out": R_OUT,
            "git": subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                                  capture_output=True, text=True).stdout.strip(),
        },
        "reps": [],
        "sweeps_sampled": [],
        "sweeps_exhaustive": [],
        "controls": {},
        "strict": [],
        "premise": [],
        "c0": [],
    }

    j28 = j2_setup(28, (7.0, 14.0), 4.0, (0.3, 0.0))
    e1 = j28["seed_psi"]
    e2 = gaussian_packet(j28["coords"], j28["order"], (7.0, 14.0), (-0.3, 0.0),
                         4.0, (28, 28))
    e3p = gaussian_packet(j28["coords"], j28["order"], (7.0, 14.0),
                          (0.3 + float(np.pi), float(np.pi)), 4.0, (28, 28))
    out["reps"].append(run_rep("E1-rep", j28, e1, {"kind": "BR-2A bonding rep"}))
    out["reps"].append(run_rep("E3p-rep", j28, e3p, {"kind": "BR-2A antibonding rep"}))
    out["reps"].append(run_rep("E2-rep", j28, e2, {"kind": "EO traveling partner"},
                               seeds=(0,)))

    out["sweeps_sampled"].append(run_sweep_sampled("SW-J28", j28, {
        "substrate": "J2-L28", "rho": "|E1| envelope",
        "note": "paired moves across phi (same seeds)"}))

    j8 = j2_setup(8, (2.0, 4.0), 1.0, (0.3, 0.0))
    out["sweeps_exhaustive"].append(run_sweep_exhaustive("SWX-J8", j8, {
        "substrate": "J2-L8", "rho": "|packet k=(0.3,0)|"}))
    r60 = ring_setup(60, (15.0,), 6.0, (0.5,))
    out["sweeps_exhaustive"].append(run_sweep_exhaustive("SWX-R60", r60, {
        "substrate": "ring-60", "rho": "|packet k=0.5|"}))

    rho28, q28 = rho_q(j28)
    phi0 = stagger_state(rho28, q28, 0.0)
    r_rescale = run_landscape(j28["graph"], j28["order"], j28["coords"], (28, 28),
                              2.0 * phi0, (7.0, 14.0), 4.0, N_MOVES, 0, J_BR0, EPS)
    out["controls"]["rescale_x2"] = r_rescale
    r_rot = run_landscape(j28["graph"], j28["order"], j28["coords"], (28, 28),
                          stagger_state(rho28, q28, float(np.pi) / 4) * np.exp(1j * 0.7),
                          (7.0, 14.0), 4.0, N_MOVES, 0, J_BR0, EPS)
    out["controls"]["global_phase"] = r_rot

    strict_cells = {}
    for s in SEEDS:
        strict_cells[str(s)] = run_strict_census(
            j28["graph"], j28["order"], j28["coords"], (28, 28), e1,
            (7.0, 14.0), R_IN, R_OUT, N_MOVES, s, J_BR0, EPS)
    out["strict"].append({"tag": "STRICT-E1", "cells": strict_cells})
    out["premise"].append({"tag": "E1", "result": premise_strict(
        e1, j28["graph"], j28["order"], j28["coords"], (28, 28),
        (7.0, 14.0), R_IN, R_OUT)})
    out["premise"].append({"tag": "phi0", "result": premise_strict(
        phi0, j28["graph"], j28["order"], j28["coords"], (28, 28),
        (7.0, 14.0), R_IN, R_OUT)})

    idx28 = index_of(j28["order"])
    for phi in (0.0, float(np.pi) / 2, float(np.pi)):
        psi = stagger_state(rho28, q28, phi)
        moves = sample_relocations(j28["graph"], C0_N, seed=777)
        loc = np.array([delta_e_local(psi, idx28, r, a) for r, a in moves])
        full = np.array([delta_e_full(psi, j28["graph"], j28["order"], r, a)
                         for r, a in moves])
        out["c0"].append({"tag": f"stagger phi={phi:.4f}", "n": C0_N,
                         "max_abs_diff": float(np.max(np.abs(loc - full)))})

    with open("data/br2_phase.json", "w") as f:
        json.dump(out, f)

    print(f"{'cell':10s} {'phi':>7s} {'E_psi':>9s} {'R_B':>8s} "
          f"{'f_fn':>7s} {'f_nf':>7s} {'J_stag':>10s} {'Jx':>10s}")
    sw = out["sweeps_sampled"][0]["cells"]
    for phi in PHI_GRID:
        r = sw[str(phi)]["seeds"]["0"]
        c = sw[str(phi)]["currents"]
        rb = r["cells"]["fn"]["f_neg"] - r["cells"]["nf"]["f_neg"]
        print(f"{'SW-J28':10s} {phi:7.4f} {sw[str(phi)]['e_psi']:9.4f} {rb:8.4f} "
              f"{r['cells']['fn']['f_neg']:7.4f} {r['cells']['nf']['f_neg']:7.4f} "
              f"{c['J_stag']:10.3e} {c['J_net_ax0']:10.3e}")
    for rep in out["reps"]:
        r = rep["seeds"]["0"]
        rb = r["cells"]["fn"]["f_neg"] - r["cells"]["nf"]["f_neg"]
        print(f"{rep['tag']:10s} {'---':>7s} {rep['e_psi']:9.4f} {rb:8.4f} "
              f"{r['cells']['fn']['f_neg']:7.4f} {r['cells']['nf']['f_neg']:7.4f}")
    print("--- exhaustive R_B(phi) ---")
    for swx in out["sweeps_exhaustive"]:
        row = []
        for phi in PHI_GRID:
            r = swx["cells"][str(phi)]["record"]
            row.append("%.3f" % (r["cells"]["fn"]["f_neg"] - r["cells"]["nf"]["f_neg"]))
        print(f"{swx['tag']:10s} {' '.join(row)}")
    print("--- premise/strict ---")
    for p in out["premise"]:
        r = p["result"]
        print(f"{p['tag']:4s} holds={r['holds']} margin={r['margin']:.3f} "
              f"min_near={r['min_near_B']:.2e} max_far={r['max_far_B']:.2e}")
    for s, r in strict_cells.items():
        print(f"strict seed {s}: R={r['R_strict']:.4f} "
              f"nf_n_neg={r['cells']['nf']['n_neg']} n_strict={r['n_strict']}")
    print("--- C0 ---")
    for c in out["c0"]:
        print(f"{c['tag']:18s} max|loc-full| = {c['max_abs_diff']:.2e}")
    print("wrote data/br2_phase.json")


if __name__ == "__main__":
    main()
