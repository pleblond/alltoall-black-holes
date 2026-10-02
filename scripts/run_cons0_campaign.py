"""CONS-0 validation campaign (frozen CONS0-PREREG grid, pre-data).

Event grid: substrates x fields x 2 frozen edges; every event records
the full contraction ledger (analytic vs direct for ALL deltas) plus
linear-probe residuals and (J2) sector rows. Split census on ring-24
+ handbuilt events. Special tasks: S1/S2 separation pins, 0A/0B pins,
controls C2--C5. Output: data/cons0_ledger.json.

Deterministic (frozen seeds). Multiprocessing over (substrate, field)
tasks; module-level worker (picklable).
"""

from __future__ import annotations

import json
import math
import os
import sys
from multiprocessing import Pool

import networkx as nx
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph.backreaction import bond_B
from bh_graph.ballistic import (
    adjacency_csr,
    evolve_fixed,
    hamiltonian,
    index_of,
    node_order,
)
from bh_graph.conservation import (
    canonical_current_residual,
    chiral_gamma_diag,
    contraction_ledger,
    energy_rate,
    field_random,
    field_spike,
    field_stagger,
    field_uniform,
    field_zero,
    invariant_census,
    is_commuting_ok,
    j2_sector_weights_fast,
    j2_sheet_involution,
    linear_residual,
    quad_value,
    split_census,
    substrate_collapsed_mini,
    substrate_er,
    substrate_handbuilt,
    substrate_j2,
    substrate_path,
    substrate_ring,
    substrate_square_torus,
)
from bh_graph.continuum import continuity_residual
from bh_graph.contraction import contracted_state
from bh_graph.formation import j2_torus_coords, j2_torus_graph
from bh_graph.phase import bond_J

SEED_RANDOM = 12345

BUILDERS = {
    "j2-L6": lambda: substrate_j2(6),
    "square-torus-6": lambda: substrate_square_torus(6),
    "ring-24": lambda: substrate_ring(24),
    "path-12": lambda: substrate_path(12),
    "er-24": substrate_er,
    "handbuilt": substrate_handbuilt,
    "collapsed-mini": substrate_collapsed_mini,
}

STAGGER_PHIS = [0.0, math.pi / 2, math.pi, 3 * math.pi / 2]


def _fields_for(aux):
    n = len(aux["order"])
    out = [("zero", field_zero(n)), ("uniform", field_uniform(n))]
    if aux["bipart"] is not None:
        q = np.array([aux["bipart"][v] for v in aux["order"]])
        for phi in STAGGER_PHIS:
            out.append((f"stagger-{phi:.4f}",
                        field_stagger(np.full(n, 1.0 / math.sqrt(n)), q, phi)))
    out.append(("random", field_random(n, SEED_RANDOM)))
    return out


def _edges_for(name, aux):
    if name == "handbuilt":
        return [tuple(aux["c1_edge"]), tuple(aux["c2_edge"])]
    g = aux["g"]
    elist = sorted(tuple(sorted(e)) for e in g.edges())
    return [elist[len(elist) // 3], elist[2 * len(elist) // 3]]


def run_event_task(task):
    """Module-level mp worker: all events for (substrate, field)."""
    name, field = task
    aux = BUILDERS[name]()
    g, order = aux["g"], aux["order"]
    idx = index_of(order)
    fields = dict(_fields_for(aux))
    if field == "spike":
        e0 = _edges_for(name, aux)[0]
        psi = field_spike(len(order), idx[e0[0]])
    else:
        psi = fields[field]
    jm = None
    if name == "j2-L6":
        jm = j2_sheet_involution(6)
    events = []
    for ei, (i, j) in enumerate(_edges_for(name, aux)):
        leg = contraction_ledger(g, psi, order, i, j)
        rec = {
            "substrate": name, "field": field, "edge": [i, j],
            "dN": leg["dN"], "dE": leg["dE"], "dE_formula": leg["dE_formula"],
            "c": leg["c"], "dnorm_direct": leg["dnorm_direct"],
            "dnorm_formula": leg["dnorm_formula"],
            "P1": leg["P1"], "P2": leg["P2"], "P3": leg["P3"], "P4": leg["P4"],
            "dEpsi_direct": leg["dEpsi_direct"],
            "dE_parts_sum": leg["dE_parts_sum"],
            "ncomp0": leg["ncomp0"], "ncomp1": leg["ncomp1"],
            "B": bond_B(psi, idx[i], idx[j]),
            "J": bond_J(psi, idx[i], idx[j]),
            "inv": leg["inv"], "graph": leg["graph"],
            "lin_0010": linear_residual(g, psi, order, i, j, 0, 0, 1, 0),
            "lin_0001": linear_residual(g, psi, order, i, j, 0, 0, 0, 1),
            "lin_m110": linear_residual(g, psi, order, i, j, -1, 1, 0, 0),
        }
        if jm is not None:
            w0 = j2_sector_weights_fast(psi, 6)
            rec["J2_QJ_before"] = quad_value(psi, jm)
            # J2 broken by contraction: no after-sector claim (filed).
            rec["J2_W_before"] = [float(v) for v in np.ravel(w0)]
        events.append(rec)
    out = {"events": events, "splits": []}
    if name in ("ring-24", "handbuilt"):
        for ei, (i, j) in enumerate(_edges_for(name, aux)):
            g2, psi2, order2, k, rec0 = contracted_state(
                g, psi, order, i, j, "sum")
            rows = split_census(g, psi, order, rec0, g2, psi2, order2)
            for r in rows:
                r["A"] = sorted(r["A"])
                r["B"] = sorted(r["B"])
                r["event"] = ei
                r["substrate"] = name
                r["field"] = field
            out["splits"].extend(rows)
    return out


def run_separation_task(_):
    """S1 phase sweep + S2 neighbor variation (frozen graphs)."""
    g = nx.cycle_graph(8)
    order = node_order(g)
    idx = index_of(order)
    i, j = 2, 3
    rho = 0.5
    s1 = []
    for k in range(8):
        dth = k * math.pi / 4
        psi = np.zeros(8, dtype=np.complex128)
        psi[idx[i]] = rho
        psi[idx[j]] = rho * np.exp(1.0j * dth)
        leg = contraction_ledger(g, psi, order, i, j)
        s1.append({"dth": dth, "dnorm": leg["dnorm_direct"],
                   "dE": leg["dEpsi_direct"],
                   "expect": 2.0 * rho * rho * math.cos(dth)})
    g2 = nx.path_graph(5)
    o2 = node_order(g2)
    base = np.zeros(5, dtype=np.complex128)
    base[1] = 0.5 + 0.1j
    base[2] = 0.3 - 0.2j
    s2 = []
    for t in (0.0, 0.25, 0.5):
        psi = base.copy()
        psi[3] = t
        leg = contraction_ledger(g2, psi, o2, 1, 2)
        s2.append({"t": t, "dnorm": leg["dnorm_direct"],
                   "dE": leg["dEpsi_direct"]})
    return {"S1": s1, "S2": s2}


def run_pins_task(_):
    """0A/0B pins on frozen small graphs."""
    out = {}
    g = nx.cycle_graph(8)
    order = node_order(g)
    h = hamiltonian(g, order=order)
    rng = np.random.default_rng(777)
    v = rng.standard_normal(8) + 1.0j * rng.standard_normal(8)
    psi = v / np.linalg.norm(v)
    rows = evolve_fixed(psi, h, 0.1, 4)["psi"]
    out["ring8_norm_const"] = float(
        np.abs([np.sum(np.abs(r) ** 2) for r in rows] - 1.0).max())
    gj = j2_torus_graph(4)
    oj = node_order(gj)
    c3 = j2_torus_coords(4)
    bipart = {v_: (x + y) & 1 for v_, (x, y, _) in c3.items()}
    cen = invariant_census(gj, oj, j2_L=4, bipart=bipart)
    out["j2_census"] = {r["name"]: bool(r["commutes"]) for r in cen}
    hj = hamiltonian(gj, order=oj)
    adj = adjacency_csr(gj, order)
    psij = np.zeros(len(oj), dtype=np.complex128)
    psij += (rng.standard_normal(len(oj)) + 1.0j * rng.standard_normal(len(oj)))
    psij = psij / np.linalg.norm(psij)
    out["j2_continuity"] = float(
        np.abs(continuity_residual(psij, gj, oj, hj, adj)).max())
    worst = 0.0
    aring = adjacency_csr(g, order)
    for seed in range(10):
        p = np.zeros(8, dtype=np.complex128)
        r2 = np.random.default_rng(1000 + seed)
        p += r2.standard_normal(8) + 1.0j * r2.standard_normal(8)
        p = p / np.linalg.norm(p)
        res = canonical_current_residual(p, g, order, aring)
        worst = max(worst, float(np.abs(res).max()))
    out["energy_obstruction_max10"] = worst
    out["energy_dEdt_zero"] = float(abs(np.sum(energy_rate(psi, aring))))
    gam = np.diag(chiral_gamma_diag(order, {vv: vv & 1 for vv in order}))
    out["gamma_commutes"] = bool(is_commuting_ok(h, gam))
    return out


def run_controls_task(_):
    """C2--C5 on frozen events."""
    out = {}
    aux = substrate_j2(6)
    g, order = aux["g"], aux["order"]
    psi = field_random(len(order), SEED_RANDOM)
    elist = sorted(tuple(sorted(e)) for e in g.edges())
    i, j = elist[len(elist) // 3]
    l0 = contraction_ledger(g, psi, order, i, j)
    l1 = contraction_ledger(g, psi * np.exp(1.0j * 0.7), order, i, j)
    out["C2_max"] = max(abs(l0[k] - l1[k]) for k in
                        ("dnorm_direct", "P1", "P2", "P3", "P4", "dEpsi_direct"))
    lx = contraction_ledger(g, psi, order, j, i)
    out["C3_max"] = max(abs(l0[k] - lx[k]) for k in
                        ("dnorm_direct", "P1", "P2", "P3", "P4", "dEpsi_direct"))
    lc = contraction_ledger(g, np.conj(psi), order, i, j)
    out["C4_max"] = max(abs(l0[k] - lc[k]) for k in
                        ("dnorm_direct", "P1", "P2", "dEpsi_direct"))
    idx = index_of(order)
    out["C4_B_same"] = bool(
        bond_B(np.conj(psi), idx[i], idx[j]) == bond_B(psi, idx[i], idx[j]))
    out["C4_J_flip"] = bool(
        bond_J(np.conj(psi), idx[i], idx[j]) == -bond_J(psi, idx[i], idx[j]))
    gr = nx.cycle_graph(24)
    ordr = node_order(gr)
    pr = field_random(24, SEED_RANDOM)
    m0 = contraction_ledger(gr, pr, ordr, 4, 5)
    mut = pr.copy()
    mut[15] *= 2.0 * np.exp(1.0j * 0.7)
    mut[20] = 0.0
    m1 = contraction_ledger(gr, mut, ordr, 4, 5)
    out["C5_max"] = max(abs(m0[k] - m1[k]) for k in
                        ("dnorm_direct", "P1", "P2", "dEpsi_direct"))
    return out


def main():
    tasks = []
    for name, build in BUILDERS.items():
        aux = build()
        fields = [f for f, _ in _fields_for(aux)] + ["spike"]
        for f in fields:
            tasks.append((name, f))
    procs = min(48, os.cpu_count() or 8)
    with Pool(processes=procs) as pool:
        results = pool.map(run_event_task, tasks)
    events, splits = [], []
    for r in results:
        events.extend(r["events"])
        splits.extend(r["splits"])
    sep = run_separation_task(None)
    pins = run_pins_task(None)
    controls = run_controls_task(None)
    data = {"meta": {"seeds": {"random": SEED_RANDOM}, "n_events": len(events),
                     "n_splits": len(splits), "tasks": tasks},
            "events": events, "splits": splits, "separation": sep,
            "pins": pins, "controls": controls}
    outp = os.path.join(os.path.dirname(__file__), "..", "data",
                        "cons0_ledger.json")

    def _default(o):
        if isinstance(o, (np.floating, float)):
            return float(o)
        if isinstance(o, (np.integer, int)):
            return int(o)
        if isinstance(o, (np.bool_, bool)):
            return bool(o)
        raise TypeError(repr(o))

    with open(outp, "w") as f:
        json.dump(data, f, default=_default)
    print(f"wrote {outp}: {len(events)} events, {len(splits)} split rows")


if __name__ == "__main__":
    main()
