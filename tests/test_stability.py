"""BR-2.7 pins: A3 derivation, unitary no-growth, H-blindness, null exhibits."""
import networkx as nx
import numpy as np

from bh_graph import stability
from bh_graph.accounting import dE_contract_formula, event_ledger
from bh_graph.ballistic import hamiltonian, index_of, node_order
from bh_graph.contraction import apply_split_cover, contract_edge, edge_tendency_table
from bh_graph.formation import j2_torus_graph
from bh_graph.phase import stagger_state
from bh_graph.stability import (
    VERDICT_A,
    all_single_event_ordering,
    edge_block_frozen,
    field_path_keeps_graph,
    h_has_no_psi_input,
    hamiltonian_is_binary_kind,
    perturbation_growth,
    propagator_opnorm_is_one,
    record_split_reversal,
    stability_row,
    unitary_spectral_radius,
    weighted_path_leaves_kind,
)


def _rand_psi(n, seed):
    rng = np.random.default_rng(seed)
    psi = rng.standard_normal(n) + 1j * rng.standard_normal(n)
    return psi / np.linalg.norm(psi)


def _uniform(n):
    return np.full(n, 1.0 / np.sqrt(n), dtype=np.complex128)


# ---- A: deformation-coordinate audit -> A3 ----

def test_a3_weighted_path_leaves_kind():
    # Interpolated H exits the frozen binary kind mid-path (no internal x).
    w = weighted_path_leaves_kind()
    assert w["0.0"] and w["1.0"] and not w["0.5"] and not w["0.25"]


def test_a3_field_path_keeps_graph():
    # Any psi-path at fixed G keeps (N, E): sectors disconnected.
    g = j2_torus_graph(6)
    assert field_path_keeps_graph(g) == {"n": 72, "e": 288}


def test_a3_discrete_jumps():
    # Contraction dN = -1 / split dN = +1 exactly: no intermediate state.
    g = nx.path_graph(6)
    g2, k, _ = contract_edge(g, 2, 3)
    assert g2.number_of_nodes() - g.number_of_nodes() == -1
    h = apply_split_cover(g2, k, frozenset({1}), frozenset({4}), 2, 3)
    assert h.number_of_nodes() - g2.number_of_nodes() == 1


def test_c7_no_interpolation_object():
    # C7 tripwire: no deformation path/interpolation API exists (frozen).
    assert VERDICT_A == "A3"
    assert not hasattr(stability, "deformation_path")
    assert not hasattr(stability, "interpolate")


# ---- C: the only dynamics is unitary -> no growth ----

def test_unitary_no_growth():
    # Perturbation norm conserved; Schrodinger linear (no fixed point).
    g = nx.cycle_graph(8)
    order = node_order(g)
    h = hamiltonian(g, order=order)
    r = perturbation_growth(_rand_psi(8, 1), _rand_psi(8, 2) * 0.01, h, 0.1, 6)
    assert r["max_growth"] < 1e-12 and r["linearity_defect"] < 1e-12


def test_unitary_spectral_radius_one():
    # |lambda| = 1 for every propagator eigenvalue (no Re > 0 possible).
    g = nx.cycle_graph(6)
    assert abs(unitary_spectral_radius(hamiltonian(g, order=node_order(g)), 0.1) - 1.0) < 1e-12


# ---- E: H is psi-blind -> no spectral trigger ----

def test_h_psi_blind_signature():
    # Structural proof: H's constructor takes no field state.
    assert h_has_no_psi_input()


def test_edge_block_frozen():
    # Every edge block is [[0,-1],[-1,0]]: eigenvalues +-1, no state data.
    b = edge_block_frozen()
    assert np.array_equal(b, np.array([[0.0, -1.0], [-1.0, 0.0]]))
    assert np.allclose(sorted(np.linalg.eigvals(b)), [-1.0, 1.0])


def test_propagator_bounded():
    # Unitary opnorm 1: no divergent local response exists.
    g = nx.cycle_graph(6)
    assert abs(propagator_opnorm_is_one(hamiltonian(g, order=node_order(g)), 0.1) - 1.0) < 1e-12


# ---- D: ordering without kinetics ----

def test_all_downhill_exhibit():
    # J2-L6 uniform: EVERY contraction lowers E, yet nothing fires (no mode).
    g = j2_torus_graph(6)
    order = node_order(g)
    r = all_single_event_ordering(g, _uniform(len(order)), order)
    assert r["n"] == 288 and r["frac_down"] == 1.0


def test_record_split_reversal():
    # Oracle split negates contraction dE exactly (E is a state function).
    g = nx.path_graph(6)
    order = node_order(g)
    r = record_split_reversal(g, _rand_psi(6, 4), order, 2, 3)
    assert abs(r["residual"]) < 1e-9
    assert abs(r["dE_contract"] - (r["E_contract"] - r["E0"])) < 1e-12


def test_ledger_regression_c0():
    # C0: BR-2.6 ledger reproduced (formula == ledger on 2 graphs).
    for g, e in ((nx.cycle_graph(8), (2, 3)),
                 (nx.grid_2d_graph(4, 4), ((1, 1), (1, 2)))):
        order = node_order(g)
        psi = _rand_psi(len(order), 6)
        assert abs(dE_contract_formula(g, psi, order, *e)
                   - event_ledger(g, psi, order, *e)["dE_formula"]) == 0.0


# ---- C1: phase anatomy regression ----

def test_phase_anatomy_regression():
    # C1: BR-2 stagger sign pattern reproduced (ring-8).
    from bh_graph.phase import stagger_state as _ss

    g = nx.cycle_graph(8)
    order = node_order(g)
    rho = np.full(8, 1.0 / np.sqrt(8))
    q = np.array([v % 2 for v in order])
    for phi, want in ((0.0, 1), (float(np.pi), -1)):
        tab = edge_tendency_table(_ss(rho, q, phi), index_of(order), g)
        assert {v["tend"] for v in tab.values()} == {want}
    tab = edge_tendency_table(_ss(rho, q, float(np.pi) / 2), index_of(order), g)
    assert {v["tend"] for v in tab.values()} == {0}


# ---- C2/C3/C4/C5: input locality + symmetries ----

def test_row_locality_far_change():
    # C2: remote edits leave the stability row identical (bounded inputs).
    g = nx.path_graph(30)
    order = node_order(g)
    psi = _rand_psi(len(order), 12)
    ref = {"R0": (0.0, 0.0, 1.0)}
    r0 = stability_row(g, psi, order, 14, 15, ref)
    psi2 = psi.copy()
    idx = index_of(order)
    psi2[idx[0]] *= -3.0
    g2 = g.copy()
    g2.remove_edge(0, 1)
    g2.add_edge(0, 2)
    r1 = stability_row(g2, psi2, order, 14, 15, ref)
    assert r0["B"] == r1["B"] and r0["dE"] == r1["dE"] and r0["ordering"] == r1["ordering"]


def test_ordering_symmetries():
    # C3/C4/C5: dE invariant under global phase, conjugation, swap.
    g = nx.cycle_graph(8)
    order = node_order(g)
    idx = index_of(order)
    psi = _rand_psi(8, 20)
    d0 = dE_contract_formula(g, psi, order, 2, 3)
    ph = np.exp(0.7j)
    assert abs(dE_contract_formula(g, psi * ph, order, 2, 3) - d0) < 1e-12
    assert abs(dE_contract_formula(g, np.conj(psi), order, 2, 3) - d0) < 1e-12
    assert abs(dE_contract_formula(g, psi, order, 3, 2) - d0) < 1e-12
    assert idx[2] != idx[3]


def test_label_invariance_c6():
    # C6: random relabeling leaves verdict inputs identical (no coords).
    import random as _r

    g = j2_torus_graph(6)
    order = node_order(g)
    psi = _rand_psi(len(order), 21)
    r0 = all_single_event_ordering(g, psi, order)
    rng = _r.Random(0)
    perm = list(g.nodes())
    rng.shuffle(perm)
    mp = dict(zip(sorted(g.nodes()), perm))
    h = nx.relabel_nodes(g, mp)
    orderh = node_order(h)
    psih = np.array([psi[order.index(next(k for k in mp if mp[k] == v))] for v in orderh])
    r1 = all_single_event_ordering(h, psih, orderh)
    assert (r0["n"], r0["frac_down"]) == (r1["n"], r1["frac_down"])
    assert abs(r0["min"] - r1["min"]) < 1e-12 and abs(r0["max"] - r1["max"]) < 1e-12


# ---- G: quadrature preserved in the null ----

def test_current_ordering_no_mechanism():
    # Pure current: B = 0, ordering whatever-it-is, stability NONE either way.
    g = nx.cycle_graph(10)
    order = node_order(g)
    rho = np.full(10, 1.0 / np.sqrt(10))
    q = np.array([v % 2 for v in order])
    psi = stagger_state(rho, q, float(np.pi) / 2)
    r = stability_row(g, psi, order, 4, 5, {"R0": (0.0, 0.0, 1.0)})
    assert abs(r["B"]) < 1e-12
    assert r["stability"] == "NONE (A3: no mode)"
    assert r["direction"] == "NONE (no mechanism)"


# ---- M: substrate controls ----

def test_a3_all_substrates():
    # Binary-kind H + psi-blindness on J2/square/ring/ER/collapsed-star.
    from bh_graph.contraction import contracted_state

    ge = nx.erdos_renyi_graph(20, 0.25, seed=8)
    gj = j2_torus_graph(6)
    oj = node_order(gj)
    e = sorted(tuple(sorted(x)) for x in gj.edges())[3]
    gc, _, _, _, _ = contracted_state(gj, _uniform(len(oj)), oj, *e, "sum")
    for g in (gj, nx.grid_2d_graph(6, 6), nx.cycle_graph(10), ge, gc):
        assert hamiltonian_is_binary_kind(hamiltonian(g, order=node_order(g)))
    assert h_has_no_psi_input()


def test_ordering_signs_substrates():
    # Uniform field: all-downhill on regular fabrics (c = 0, n_cross >= 2).
    for g in (j2_torus_graph(6), nx.grid_2d_graph(6, 6), nx.cycle_graph(10)):
        order = node_order(g)
        r = all_single_event_ordering(g, _uniform(len(order)), order)
        assert r["frac_down"] == 1.0, g
