"""VAC-0A: universal algebraic identities on ARBITRARY graphs (LAW layer).

Every test runs on a hostile battery (path, cycle, star, complete,
disconnected, random GNP, small J2 ball). If any identity fails off J2,
the LAW claim is wrong and the campaign stops here.
"""

import networkx as nx
import numpy as np
import pytest

from bh_graph.backreaction import bond_B, energy_edge_sum, energy_full
from bh_graph.ballistic import (
    adjacency_csr,
    branch_projectors,
    branch_weights_all,
    evolve_fixed,
    hamiltonian,
    is_accounting_ok,
    is_hermitian_ok,
    is_normalized_ok,
    is_projector_ok,
    node_order,
)
from bh_graph.continuum import is_continuity_ok
from bh_graph.formation import j2_torus_graph
from bh_graph.graphs import build_j2_ball
from bh_graph.phase import bond_J
from bh_graph.potential import bond_current


def hostile_graphs():
    rng = np.random.default_rng(0)
    gnp = nx.fast_gnp_random_graph(12, 0.3, seed=1)
    disc = nx.Graph()
    disc.add_edges_from([(0, 1), (1, 2), (3, 4)])
    disc.add_node(5)
    return {
        "path": nx.path_graph(9),
        "cycle_even": nx.cycle_graph(10),
        "cycle_odd": nx.cycle_graph(9),
        "star": nx.star_graph(7),
        "complete": nx.complete_graph(6),
        "disconnected": disc,
        "gnp": gnp,
        "j2_ball_r2": build_j2_ball(2),
        "j2_torus_L4": j2_torus_graph(4),
    }


def random_state(n, seed):
    rng = np.random.default_rng(seed)
    psi = rng.standard_normal(n) + 1.0j * rng.standard_normal(n)
    return psi / np.linalg.norm(psi)


@pytest.mark.parametrize("name", list(hostile_graphs()))
def test_h_hermitian_all_graphs(name):
    g = hostile_graphs()[name]
    order = node_order(g)
    assert is_hermitian_ok(hamiltonian(g, order=order))


@pytest.mark.parametrize("name", list(hostile_graphs()))
def test_norm_conserved_all_graphs(name):
    g = hostile_graphs()[name]
    order = node_order(g)
    n = len(order)
    psi0 = random_state(n, 7)
    assert is_normalized_ok(psi0)
    rec = evolve_fixed(psi0, hamiltonian(g, order=order), 0.1, 20)
    assert np.all(np.abs(rec["norms"] - 1.0) < 1e-9)


@pytest.mark.parametrize("name", list(hostile_graphs()))
def test_continuity_exact_all_graphs(name):
    g = hostile_graphs()[name]
    order = node_order(g)
    n = len(order)
    psi = random_state(n, 11)
    h = hamiltonian(g, order=order)
    adj = adjacency_csr(g, order)
    assert is_continuity_ok(psi, g, order, h, adj, atol=1e-9)


@pytest.mark.parametrize("name", list(hostile_graphs()))
def test_energy_bond_sum_all_graphs(name):
    g = hostile_graphs()[name]
    order = node_order(g)
    n = len(order)
    psi = random_state(n, 13)
    assert abs(energy_full(psi, g, order) - energy_edge_sum(psi, g, order)) < 1e-9


@pytest.mark.parametrize("name", list(hostile_graphs()))
def test_bj_symmetry_all_graphs(name):
    g = hostile_graphs()[name]
    order = node_order(g)
    n = len(order)
    if n < 2:
        return
    psi = random_state(n, 17)
    assert abs(bond_B(psi, 0, 1) - bond_B(psi, 1, 0)) < 1e-12
    assert abs(bond_J(psi, 0, 1) + bond_J(psi, 1, 0)) < 1e-12
    c = np.conj(psi[0]) * psi[1]
    assert abs(bond_B(psi, 0, 1) - c.real) < 1e-12
    # Banked convention split (pinned, see docs/vac0-law-derivations.md):
    # phase.bond_J is the BARE quadrature Im(C); the continuity current
    # potential.bond_current is 2*Jcoup*Im(C).
    assert abs(bond_J(psi, 0, 1) - c.imag) < 1e-12
    assert abs(bond_current(psi[0], psi[1]) - 2.0 * c.imag) < 1e-12


def test_energy_conjugacy_path():
    """dE/dw_uv = -2 B_uv via centered finite difference (VAC-0A/A4)."""
    g = nx.path_graph(6)
    order = node_order(g)
    psi = random_state(6, 19)
    a = adjacency_csr(g, order).toarray()
    iu, iv = 2, 3
    b = bond_B(psi, iu, iv)
    eps = 1e-6
    e_vals = []
    for s in (+1.0, -1.0):
        w = a.copy()
        w[iu, iv] += s * eps
        w[iv, iu] += s * eps
        e_vals.append(float(-np.real(np.vdot(psi, w @ psi))))
    num = (e_vals[0] - e_vals[1]) / (2.0 * eps)
    assert abs(num - (-2.0 * b)) < 1e-6


def test_energy_conjugacy_star():
    g = nx.star_graph(5)
    order = node_order(g)
    psi = random_state(6, 23)
    a = adjacency_csr(g, order).toarray()
    iu, iv = 0, 4
    b = bond_B(psi, iu, iv)
    eps = 1e-6
    e_vals = []
    for s in (+1.0, -1.0):
        w = a.copy()
        w[iu, iv] += s * eps
        w[iv, iu] += s * eps
        e_vals.append(float(-np.real(np.vdot(psi, w @ psi))))
    num = (e_vals[0] - e_vals[1]) / (2.0 * eps)
    assert abs(num - (-2.0 * b)) < 1e-6


@pytest.mark.parametrize("name", list(hostile_graphs()))
def test_branch_accounting_all_graphs(name):
    """Projector validity + W_+ + W_0 + W_- = 1 on ANY graph (VAC-0A/A6)."""
    g = hostile_graphs()[name]
    order = node_order(g)
    n = len(order)
    h = hamiltonian(g, order=order)
    br = branch_projectors(h)
    assert is_projector_ok(br["P_plus"])
    assert is_projector_ok(br["P_minus"])
    psi = random_state(n, 29)
    w = branch_weights_all(psi, br)
    assert is_accounting_ok(w["w_plus"], w["w_zero"], w["w_minus"])


def test_branch_preserved_bipartite_only():
    """Free evolution preserves branch weight exactly (bipartite path)."""
    from bh_graph.ballistic import branch_mixing, branch_weight

    g = nx.path_graph(8)
    order = node_order(g)
    h = hamiltonian(g, order=order)
    br = branch_projectors(h)
    psi0 = random_state(8, 31)
    rec = evolve_fixed(psi0, h, 0.1, 10)
    ws = [branch_weight(p, br["P_plus"]) for p in rec["psi"]]
    assert branch_mixing(ws) < 1e-9
