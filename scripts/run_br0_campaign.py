"""BR-0 campaign runner: frozen protocol, deterministic, formation-free.

Builds ONLY P1.1-validated packet states (+ V0 exact control + uniform
secondary-exploratory background, explicitly NOT a vacuum claim), runs the
M1 move-energy census (sampled 200k x seeds {0,1,2} on validation-size
graphs; exhaustive on small graphs), verifies C0/C4 at campaign scale,
and writes data/br0_landscape.json. Human-readable summary to stdout.

Usage: python3 scripts/run_br0_campaign.py
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
    count_relocations,
    delta_e_batch,
    delta_e_full,
    delta_e_local,
    run_landscape,
    run_landscape_exhaustive,
    sample_relocations,
    uniform_psi,
    zero_psi,
)
from bh_graph.ballistic import (  # noqa: E402
    gaussian_packet,
    index_of,
    is_normalized_ok,
    node_order,
    ring_coords,
    torus_grid_coords,
)
from bh_graph.formation import j2_torus_coords, j2_torus_graph  # noqa: E402
from bh_graph.graphs import build_torus_grid  # noqa: E402

N_MOVES = 200_000
SEEDS = (0, 1, 2)
EPS = EPS_DEFAULT
C0_N = 2000


def j2_setup(L, r0, sigma):
    g = j2_torus_graph(L)
    order = node_order(g)
    c3 = j2_torus_coords(L)
    coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    return {"graph": g, "order": order, "coords": coords, "periods": (L, L),
            "r0": tuple(r0), "sigma": float(sigma)}


def ring_setup(n, r0, sigma):
    g = nx.cycle_graph(n)
    order = node_order(g)
    return {"graph": g, "order": order, "coords": ring_coords(n), "periods": (n,),
            "r0": tuple(r0), "sigma": float(sigma)}


def torus_setup(L, r0, sigma):
    g = build_torus_grid(L)
    order = node_order(g)
    return {"graph": g, "order": order, "coords": torus_grid_coords(L),
            "periods": (L, L), "r0": tuple(r0), "sigma": float(sigma)}


def packet(setup, k):
    psi = gaussian_packet(setup["coords"], setup["order"], setup["r0"], tuple(k),
                          setup["sigma"], periods=setup["periods"])
    assert is_normalized_ok(psi)
    return psi


def run_state(tag, setup, psi, meta):
    rec = {"tag": tag, "meta": meta, "e_psi": None, "seeds": {}}
    for s in SEEDS:
        r = run_landscape(setup["graph"], setup["order"], setup["coords"],
                          setup["periods"], psi, setup["r0"], setup["sigma"],
                          N_MOVES, s, J_BR0, EPS)
        rec["seeds"][str(s)] = r
        rec["e_psi"] = r["e_psi"]
    return rec


def run_exhaustive(tag, setup, psi, meta):
    r = run_landscape_exhaustive(setup["graph"], setup["order"], setup["coords"],
                                 setup["periods"], psi, setup["r0"],
                                 setup["sigma"], J_BR0, EPS)
    return {"tag": tag, "meta": meta, "e_psi": r["e_psi"], "record": r}


def c0_check(tag, setup, psi):
    idx = index_of(setup["order"])
    moves = sample_relocations(setup["graph"], C0_N, seed=777)
    loc = np.array([delta_e_local(psi, idx, r, a) for r, a in moves])
    full = np.array([delta_e_full(psi, setup["graph"], setup["order"], r, a)
                     for r, a in moves])
    return {"tag": tag, "n": C0_N,
            "max_abs_diff": float(np.max(np.abs(loc - full)))}


def main():
    out = {
        "meta": {
            "date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "n_moves": N_MOVES,
            "seeds": list(SEEDS),
            "eps": EPS,
            "j": J_BR0,
            "git": subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                                  capture_output=True, text=True).stdout.strip(),
        },
        "sampled": [],
        "exhaustive": [],
        "c0": [],
        "c4": {},
    }

    j28 = j2_setup(28, (7.0, 14.0), 4.0)
    n28 = len(j28["order"])
    out["sampled"].append(run_state("V0", j28, zero_psi(n28),
                                    {"substrate": "J2-L28", "kind": "zero-field control",
                                     "note": "near/far use E1 geometry as neutral "
                                             "reference (homogeneity null); primary global"}))
    out["sampled"].append(run_state("V1U", j28, uniform_psi(n28),
                                    {"substrate": "J2-L28", "kind": "uniform exploratory",
                                     "note": "SECONDARY: not a vacuum claim (BR0-E); "
                                             "near/far = geometry-reference null"}))
    e1 = packet(j28, (0.3, 0.0))
    e2 = packet(j28, (-0.3, 0.0))
    out["sampled"].append(run_state("E1", j28, e1,
                                    {"substrate": "J2-L28", "kind": "P1.1b packet",
                                     "k": [0.3, 0.0], "sigma": 4.0}))
    out["sampled"].append(run_state("E2", j28, e2,
                                    {"substrate": "J2-L28", "kind": "k->-k partner",
                                     "k": [-0.3, 0.0], "sigma": 4.0}))
    out["sampled"].append(run_state("E3b", j28, packet(j28, (0.0, 0.0)),
                                    {"substrate": "J2-L28", "kind": "localized k=0",
                                     "k": [0.0, 0.0], "sigma": 4.0}))
    out["sampled"].append(run_state("E3p", j28, packet(j28, (0.3 + float(np.pi), float(np.pi))),
                                    {"substrate": "J2-L28", "kind": "branch partner k+Q",
                                     "k": "0.3+pi,pi", "sigma": 4.0}))
    r400 = ring_setup(400, (100.0,), 15.0)
    out["sampled"].append(run_state("E3r", r400, packet(r400, (0.5,)),
                                    {"substrate": "ring-400", "kind": "P1.1a packet",
                                     "k": [0.5], "sigma": 15.0}))
    t30 = torus_setup(30, (7.0, 15.0), 4.0)
    out["sampled"].append(run_state("E3t", t30, packet(t30, (0.5, 0.0)),
                                    {"substrate": "torus-30", "kind": "P1.1a packet",
                                     "k": [0.5, 0.0], "sigma": 4.0}))

    j8 = j2_setup(8, (2.0, 4.0), 1.0)
    n8 = len(j8["order"])
    out["sampled"].append(run_state("S-J2-P", j8, packet(j8, (0.3, 0.0)),
                                    {"substrate": "J2-L8", "kind": "packet (C5b sampled twin)",
                                     "k": [0.3, 0.0], "sigma": 1.0}))
    out["exhaustive"].append(run_exhaustive("X-J2-V0", j8, zero_psi(n8),
                                            {"substrate": "J2-L8", "kind": "zero control",
                                             "moves": count_relocations(j8["graph"])}))
    out["exhaustive"].append(run_exhaustive("X-J2-U", j8, uniform_psi(n8),
                                            {"substrate": "J2-L8", "kind": "uniform",
                                             "moves": count_relocations(j8["graph"])}))
    out["exhaustive"].append(run_exhaustive("X-J2-P", j8, packet(j8, (0.3, 0.0)),
                                            {"substrate": "J2-L8", "kind": "packet",
                                             "k": [0.3, 0.0], "sigma": 1.0,
                                             "moves": count_relocations(j8["graph"]),
                                             "note": "characterization (spread-gate-valid, "
                                                     "non-P1.1-validated prep)"}))
    r60 = ring_setup(60, (15.0,), 6.0)
    n60 = len(r60["order"])
    out["sampled"].append(run_state("S-R-P", r60, packet(r60, (0.5,)),
                                    {"substrate": "ring-60", "kind": "packet (C5b sampled twin)",
                                     "k": [0.5], "sigma": 6.0}))
    out["exhaustive"].append(run_exhaustive("X-R-V0", r60, zero_psi(n60),
                                            {"substrate": "ring-60", "kind": "zero control",
                                             "moves": count_relocations(r60["graph"])}))
    out["exhaustive"].append(run_exhaustive("X-R-P", r60, packet(r60, (0.5,)),
                                            {"substrate": "ring-60", "kind": "packet",
                                             "k": [0.5], "sigma": 6.0,
                                             "moves": count_relocations(r60["graph"])}))

    out["c0"].append(c0_check("J2-L28/E1", j28, e1))
    out["c0"].append(c0_check("J2-L28/uniform", j28, uniform_psi(n28)))
    out["c0"].append(c0_check("J2-L28/zero", j28, zero_psi(n28)))
    out["c0"].append(c0_check("ring-400/E3r", r400, packet(r400, (0.5,))))
    out["c0"].append(c0_check("torus-30/E3t", t30, packet(t30, (0.5, 0.0))))

    idx28 = index_of(j28["order"])
    c4moves = sample_relocations(j28["graph"], 50_000, seed=4242)
    d1 = delta_e_batch(e1, idx28, [m[0] for m in c4moves], [m[1] for m in c4moves])
    d2 = delta_e_batch(e2, idx28, [m[0] for m in c4moves], [m[1] for m in c4moves])
    out["c4"] = {"n": len(c4moves),
                 "max_abs_diff_E1_E2": float(np.max(np.abs(d1 - d2)))}

    with open("data/br0_landscape.json", "w") as f:
        json.dump(out, f)

    print(f"{'state':8s} {'substrate':9s} {'E_psi':>10s} {'f-_glob':>8s} "
          f"{'f-_near':>8s} {'f-_far':>8s} {'f0_glob':>8s} {'med':>10s} {'conn':>6s}")
    for st in out["sampled"]:
        s0 = st["seeds"]["0"]
        print(f"{st['tag']:8s} {st['meta']['substrate']:9s} {st['e_psi']:10.4f} "
              f"{s0['global']['f_neg']:8.4f} {s0['near']['f_neg']:8.4f} "
              f"{s0['far']['f_neg']:8.4f} {s0['global']['f_zero']:8.4f} "
              f"{s0['global']['median']:10.2e} {s0['frac_connected']:6.3f}")
    print("--- exhaustive ---")
    for st in out["exhaustive"]:
        r = st["record"]
        print(f"{st['tag']:8s} {st['meta']['substrate']:9s} {st['e_psi']:10.4f} "
              f"{r['global']['f_neg']:8.4f} {r['near']['f_neg']:8.4f} "
              f"{r['far']['f_neg']:8.4f} {r['global']['f_zero']:8.4f} "
              f"{r['global']['median']:10.2e} n={r['n_moves']}")
    print("--- C0 ---")
    for c in out["c0"]:
        print(f"{c['tag']:16s} max|loc-full| = {c['max_abs_diff']:.2e}")
    print(f"C4 max|E1-E2| = {out['c4']['max_abs_diff_E1_E2']:.2e}")
    print("wrote data/br0_landscape.json")


if __name__ == "__main__":
    main()
