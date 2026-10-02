"""BR-2.6 campaign runner (FROZEN pre-data; see BR26-PREREG in docs/DEFERRED.md).

Sections: V (conditional-closure tripwire: constructed B_* states must
balance), P (event-admissibility census over state families with LABELED
reference overlays, nothing selected). Deterministic; seeds frozen.
Output: data/br26_accounting.json.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import networkx as nx
import numpy as np

from bh_graph.accounting import b_star, qtot_delta  # noqa: E402
from bh_graph.backreaction import bond_B  # noqa: E402
from bh_graph.ballistic import index_of, node_order  # noqa: E402
from bh_graph.contraction import contraction_census  # noqa: E402
from bh_graph.formation import j2_torus_coords, j2_torus_graph  # noqa: E402
from bh_graph.phase import bond_J, stagger_state, sublattice_j2  # noqa: E402

# Frozen P-grid (BR26-PREREG).
RATIOS = {"R0": (0.0, 0.0, 1.0), "R1": (1.0, 0.0, 2.0), "R2": (0.0, 1.0, 1.0)}
EPS_GRID = (1e-3, 1e-2, 0.1)
V_RATIOS = ((1.0, 0.0, 2.0), (0.0, 1.0, 1.0), (-1.0, 1.0, 0.5))


def log(msg):
    print(f"[br26] {msg}", flush=True)


def run_V():
    log("V: constructed B_* balance verification (ACCOUNTED tripwire)")
    out = []
    graphs = [("j2-L6", j2_torus_graph(6)), ("path-8", nx.path_graph(8))]
    for gtag, g in graphs:
        order = node_order(g)
        idx = index_of(order)
        elist = sorted(tuple(sorted(e)) for e in g.edges())
        for (a, b), ratios in ((elist[2], V_RATIOS[0]), (elist[4], V_RATIOS[1]),
                               (elist[6], V_RATIOS[2])):
            alpha, beta, gamma = ratios
            c = len(set(g.neighbors(a)) & set(g.neighbors(b)) - {a, b})
            kind, target = b_star(c, alpha, beta, gamma)
            assert kind == "B"
            rng = np.random.default_rng(9000 + len(out))
            psi = rng.standard_normal(len(order)) + 1j * rng.standard_normal(len(order))
            psi[idx[a]] = complex(target, 0.0)
            psi[idx[b]] = complex(1.0, 0.0)
            cen = contraction_census(g, psi, order, a, b, "sum")
            dq = qtot_delta(alpha, beta, gamma, c, cen["dnorm_direct"] / 2.0)
            out.append({"graph": gtag, "edge": [a, b], "c": c,
                        "ratios": list(ratios), "B_star": target,
                        "B_built": float(bond_B(psi, idx[a], idx[b])),
                        "DeltaQ": float(dq)})
            log(f"  {gtag} {a}-{b} c={c} B*={target:.4f} DQ={dq:.2e}")
    return out


def family_edge_stats(g, psi, order):
    idx = index_of(order)
    bs, js, cs = [], [], []
    for a, b in g.edges():
        bs.append(bond_B(psi, idx[a], idx[b]))
        js.append(bond_J(psi, idx[a], idx[b]))
        cs.append(len(set(g.neighbors(a)) & set(g.neighbors(b)) - {a, b}))
    bs = np.array(bs)
    hist = {}
    for c in cs:
        hist[str(c)] = hist.get(str(c), 0) + 1
    return {"n_edges": len(bs), "B_min": float(bs.min()), "B_max": float(bs.max()),
            "B_mean": float(bs.mean()),
            "frac_pos": float(np.mean(bs > 1e-12)),
            "frac_zero": float(np.mean(np.abs(bs) <= 1e-12)),
            "frac_neg": float(np.mean(bs < -1e-12)),
            "J_maxabs": float(np.max(np.abs(js))),
            "c_hist": hist, "_B": [float(x) for x in bs], "_c": [int(x) for x in cs]}


def overlay_sensitivity(stats):
    # LABELED reference overlays (BR-1H style): stated ratios + stated
    # epsilon grid; sensitivity table, NOT a selected threshold.
    bs = np.array(stats["_B"])
    cs = np.array(stats["_c"])
    out = {}
    for tag, (alpha, beta, gamma) in RATIOS.items():
        targets = np.array([b_star(int(c), alpha, beta, gamma)[1] for c in cs])
        row = {}
        for eps in EPS_GRID:
            row[str(eps)] = float(np.mean(np.abs(bs - targets) < eps))
        out[tag] = {"ratios": [alpha, beta, gamma], "within_eps": row}
    return out


def run_P():
    log("P: admissibility census over state families")
    out = {}
    L = 12
    g = j2_torus_graph(L)
    order = node_order(g)
    n = len(order)
    c3 = j2_torus_coords(L)
    q = np.array([sublattice_j2(c3)[v] for v in order])
    rho = np.full(n, 1.0 / np.sqrt(n))
    fams = {
        "zero": np.zeros(n, dtype=np.complex128),
        "bonding": stagger_state(rho, q, 0.0),
        "current": stagger_state(rho, q, float(np.pi) / 2),
        "antibonding": stagger_state(rho, q, float(np.pi)),
    }
    rng = np.random.default_rng(777)
    psi_r = rng.standard_normal(n) + 1j * rng.standard_normal(n)
    fams["random"] = psi_r / np.linalg.norm(psi_r)
    for tag, psi in fams.items():
        st = family_edge_stats(g, psi, order)
        st["overlays"] = overlay_sensitivity(st)
        del st["_B"]
        del st["_c"]
        out[f"j2-L12-{tag}"] = st
        log(f"  {tag}: B[{st['B_min']:.4f},{st['B_max']:.4f}] "
            f"+{st['frac_pos']:.2f}/0{st['frac_zero']:.2f}/-{st['frac_neg']:.2f} "
            f"c={st['c_hist']}")
    # Irregular control: connected ER + random field (seeded).
    ge = None
    for s in range(40, 60):
        h = nx.erdos_renyi_graph(72, 0.11, seed=s)
        if nx.is_connected(h):
            ge = h
            break
    assert ge is not None
    oe = node_order(ge)
    rng = np.random.default_rng(778)
    psie = rng.standard_normal(len(oe)) + 1j * rng.standard_normal(len(oe))
    psie /= np.linalg.norm(psie)
    st = family_edge_stats(ge, psie, oe)
    st["overlays"] = overlay_sensitivity(st)
    del st["_B"]
    del st["_c"]
    out["er72-random"] = st
    log(f"  irregular: E={st['n_edges']} B[{st['B_min']:.4f},{st['B_max']:.4f}] "
        f"c={st['c_hist']}")
    return out


def main():
    t0 = time.time()
    out = {"meta": {
        "campaign": "BR-2.6 joint accounting + event-law derivation",
        "prereg": "BR26-PREREG (docs/DEFERRED.md, frozen pre-data)",
        "ratios_reference": RATIOS,
        "eps_grid": list(EPS_GRID),
    }}
    out["V"] = run_V()
    out["P"] = run_P()
    out["meta"]["seconds"] = round(time.time() - t0, 1)
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "data", "br26_accounting.json")
    with open(path, "w") as f:
        json.dump(out, f)
    log(f"wrote {path} ({out['meta']['seconds']}s total)")


if __name__ == "__main__":
    main()
