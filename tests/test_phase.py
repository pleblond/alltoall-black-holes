"""BR-2 phase-quadrature theorem pins (pre-data, analytic only).

Locks: phi grid, canonical bipartitions, stagger construction, bond
quadrature formulas (B = rho rho cos, J = +-rho rho sin), J
antisymmetry, conjugation (B-even/J-odd, bitwise), global-phase
invariance, zero null, amplitude scaling (real + complex), current
units (traveling sign/oddness, real-zero, stagger theorems),
response-helper arithmetic, strict-census partition, premise units.
Campaign verdicts are FILED in docs/DEFERRED.md, never pinned here.
"""

import math

import networkx as nx
import numpy as np
import pytest

from bh_graph.backreaction import (
    bond_B,
    delta_e_batch,
    landscape_stats,
    sample_relocations,
)
from bh_graph.ballistic import (
    gaussian_packet,
    index_of,
    is_normalized_ok,
    node_order,
    ring_coords,
)
from bh_graph.formation import j2_torus_coords, j2_torus_graph
from bh_graph.phase import (
    PHI_GRID,
    bond_C,
    bond_J,
    directional_current,
    is_bipartition_ok,
    is_J_antisymmetric_ok,
    node_radii,
    premise_strict,
    response_RB,
    response_RB_from_cells,
    response_Rmag_from_cells,
    run_strict_census,
    stagger_state,
    staggered_current,
    sublattice_j2,
    sublattice_ring,
    sublattice_torus_grid,
)


def _rand_psi(n, seed):
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(n) + 1j * rng.standard_normal(n)
    return v / np.linalg.norm(v)


def test_phi_grid_frozen():
    assert len(PHI_GRID) == 8
    for k, phi in enumerate(PHI_GRID):
        assert phi == k * math.pi / 4.0
    assert PHI_GRID[0] == 0.0 and PHI_GRID[4] == math.pi


def test_sublattices_proper():
    g = j2_torus_graph(4)
    assert is_bipartition_ok(g, sublattice_j2(j2_torus_coords(4)))
    assert is_bipartition_ok(nx.cycle_graph(60), sublattice_ring(60))
    assert not is_bipartition_ok(nx.cycle_graph(9), {v: v & 1 for v in range(9)})
    assert not is_bipartition_ok(nx.complete_graph(3), {0: 0, 1: 1, 2: 0})
    assert not is_bipartition_ok(g, {})
    with pytest.raises(ValueError):
        sublattice_ring(9)
    from bh_graph.graphs import build_torus_grid

    assert is_bipartition_ok(build_torus_grid(10), sublattice_torus_grid(10))


def test_stagger_construction():
    rho = np.array([0.5, 0.25, 0.125, 0.125])
    q = np.array([0, 1, 0, 1])
    psi0 = stagger_state(rho, q, 0.0)
    assert np.all(np.imag(psi0) == 0.0)  # real-positive
    assert np.allclose(np.abs(psi0), rho)
    for phi in PHI_GRID:
        psi = stagger_state(rho, q, phi)
        assert np.allclose(np.abs(psi), rho, atol=1e-12)  # envelope fixed
        assert np.allclose(psi, rho * np.exp(1j * phi * q), atol=0.0)
    assert np.allclose(stagger_state(rho, q, math.pi), rho * np.array([1, -1, 1, -1]),
                       atol=1e-12)


def test_bond_quadrature_theorems():
    # Stagger: EVERY edge has |Delta theta| = phi exactly.
    g = nx.cycle_graph(20)
    order = node_order(g)
    sub = sublattice_ring(20)
    rho = np.abs(_rand_psi(20, 0))
    q = np.array([sub[v] for v in order])
    idx = index_of(order)
    for phi in PHI_GRID:
        psi = stagger_state(rho, q, phi)
        for a, b in g.edges():
            i, k = idx[a], idx[b]
            assert abs(bond_B(psi, i, k) - rho[i] * rho[k] * math.cos(phi)) < 1e-12
            u, v = (i, k) if q[i] == 0 else (k, i)  # 0 -> 1 order
            assert abs(bond_J(psi, u, v) - rho[u] * rho[v] * math.sin(phi)) < 1e-12
            assert bond_C(psi, i, k) == complex(bond_B(psi, i, k), bond_J(psi, i, k))


def test_J_antisymmetry_bitwise():
    psi = _rand_psi(12, 1)
    for i in range(12):
        for k in range(12):
            assert is_J_antisymmetric_ok(psi, i, k)
            assert bond_J(psi, i, k) == -bond_J(psi, k, i)


def test_conjugation_B_even_J_odd():
    # k -> -k for Gaussian packets is conjugation: B matched bitwise,
    # J negated bitwise, both currents odd bitwise.
    n = 40
    order = list(range(n))
    coords = ring_coords(n)
    pp = gaussian_packet(coords, order, (10.0,), (0.5,), 5.0, periods=(n,))
    pm = np.conj(pp)
    g = nx.cycle_graph(n)
    idx = index_of(order)
    for a, b in g.edges():
        i, k = idx[a], idx[b]
        assert bond_B(pm, i, k) == bond_B(pp, i, k)
        assert bond_J(pm, i, k) == -bond_J(pp, i, k)
    assert directional_current(pm, g, order, coords, (n,), 0) == -directional_current(
        pp, g, order, coords, (n,), 0)
    sub = sublattice_ring(n)
    assert staggered_current(pm, g, order, sub) == -staggered_current(pp, g, order, sub)


def test_global_phase_invariance():
    # psi -> e^{i theta} psi: B/J/dE unchanged (<1e-12); R identical.
    g = nx.cycle_graph(16)
    order = node_order(g)
    idx = index_of(order)
    psi = _rand_psi(16, 2)
    rot = psi * np.exp(1j * 0.7)
    for a, b in g.edges():
        i, k = idx[a], idx[b]
        assert abs(bond_B(rot, i, k) - bond_B(psi, i, k)) < 1e-12
        assert abs(bond_J(rot, i, k) - bond_J(psi, i, k)) < 1e-12
    moves = sample_relocations(g, 500, seed=0)
    d0 = delta_e_batch(psi, idx, [m[0] for m in moves], [m[1] for m in moves])
    d1 = delta_e_batch(rot, idx, [m[0] for m in moves], [m[1] for m in moves])
    assert np.max(np.abs(d0 - d1)) < 1e-12


def test_zero_null():
    z = np.zeros(10, dtype=complex)
    assert bond_J(z, 0, 1) == 0.0 and bond_C(z, 0, 1) == 0.0j
    g = nx.cycle_graph(10)
    order = node_order(g)
    coords = ring_coords(10)
    assert directional_current(z, g, order, coords, (10,), 0) == 0.0
    assert staggered_current(z, g, order, sublattice_ring(10)) == 0.0
    p = premise_strict(z, g, order, coords, (10,), (0.0,), 2.0, 4.0)
    assert p["min_near_B"] == 0.0 and p["max_far_B"] == 0.0 and not p["holds"]


def test_amplitude_scaling():
    # Real c: B/J/dE scale by c^2; complex c: by |c|^2; signs/rates invariant.
    g = nx.cycle_graph(14)
    order = node_order(g)
    idx = index_of(order)
    psi = _rand_psi(14, 3)
    moves = sample_relocations(g, 300, seed=0)
    base = delta_e_batch(psi, idx, [m[0] for m in moves], [m[1] for m in moves])
    for c in (2.5, -1.5, 1 + 1j, 0.5 - 0.5j):
        got = delta_e_batch(c * psi, idx, [m[0] for m in moves], [m[1] for m in moves])
        assert np.allclose(got, abs(c) ** 2 * base, atol=1e-12)
        i, k = 2, 5
        assert abs(bond_B(c * psi, i, k) - abs(c) ** 2 * bond_B(psi, i, k)) < 1e-12
        assert abs(bond_J(c * psi, i, k) - abs(c) ** 2 * bond_J(psi, i, k)) < 1e-12
    s0 = landscape_stats(base)
    s4 = landscape_stats(4.0 * base)
    assert (s0["f_neg"], s0["f_zero"], s0["f_pos"]) == (s4["f_neg"], s4["f_zero"], s4["f_pos"])


def test_directional_current_units():
    n = 60
    order = list(range(n))
    coords = ring_coords(n)
    g = nx.cycle_graph(n)
    pp = gaussian_packet(coords, order, (15.0,), (0.5,), 6.0, periods=(n,))
    jp = directional_current(pp, g, order, coords, (n,), 0)
    assert jp > 0  # +k packet flows +x (P1 v_g sign)
    pm = gaussian_packet(coords, order, (15.0,), (-0.5,), 6.0, periods=(n,))
    assert directional_current(pm, g, order, coords, (n,), 0) == -jp  # odd, bitwise
    z0 = gaussian_packet(coords, order, (15.0,), (0.0,), 6.0, periods=(n,))
    assert directional_current(z0, g, order, coords, (n,), 0) == 0.0  # real: exact
    uni = np.full(n, 1 / math.sqrt(n))
    assert directional_current(uni, g, order, coords, (n,), 0) == 0.0
    rho = np.full(n, 1 / math.sqrt(n))  # uniform-envelope stagger: pairwise cancel
    q = np.array([v & 1 for v in order])
    assert abs(directional_current(stagger_state(rho, q, math.pi / 2), g, order,
                                   coords, (n,), 0)) < 1e-12


def test_staggered_current_units():
    g = nx.cycle_graph(20)
    order = node_order(g)
    sub = sublattice_ring(20)
    q = np.array([sub[v] for v in order])
    rho = np.abs(_rand_psi(20, 4))
    idx = index_of(order)
    const = sum(2.0 * rho[idx[a]] * rho[idx[b]]
                for a, b in g.edges())  # phi-free factor (all edges 0->1-able)
    for phi in PHI_GRID:
        js = staggered_current(stagger_state(rho, q, phi), g, order, sub)
        assert abs(js - const * math.sin(phi)) < 1e-12  # exact sine law
    assert staggered_current(stagger_state(rho, q, 0.0), g, order, sub) == 0.0
    with pytest.raises(ValueError):
        staggered_current(rho, nx.complete_graph(3), [0, 1, 2], {0: 0, 1: 1, 2: 0})


def test_response_helpers():
    assert response_RB(0.34, 0.0) == 0.34
    assert response_RB(0.5, 0.9) == -0.4
    cells = {"fn": {"f_neg": 0.5, "neg_tail_mean": -2.0},
             "nf": {"f_neg": 0.1, "neg_tail_mean": -1.0}}
    assert response_RB_from_cells(cells) == 0.4
    assert response_Rmag_from_cells(cells) == (-0.1) - (-1.0)  # mass_nf - mass_fn


def test_strict_census_partition():
    g = nx.cycle_graph(24)
    order = node_order(g)
    coords = ring_coords(24)
    psi = gaussian_packet(coords, order, (6.0,), (0.5,), 2.5, periods=(24,))
    assert is_normalized_ok(psi)
    r1 = run_strict_census(g, order, coords, (24,), psi, (6.0,), 3.0, 6.0, 3000, seed=0)
    r2 = run_strict_census(g, order, coords, (24,), psi, (6.0,), 3.0, 6.0, 3000, seed=0)
    assert r1 == r2
    assert r1["n_strict"] + r1["n_buf"] == 3000
    assert sum(r1["cells"][t]["n"] for t in ("nn", "nf", "fn", "ff")) == r1["n_strict"]
    assert r1["R_strict"] == response_RB_from_cells(r1["cells"])
    assert r1["n_strict"] > 500  # geometry-dependent fraction, filed not barred


def test_premise_units():
    g = nx.cycle_graph(12)
    order = node_order(g)
    coords = ring_coords(12)
    rho = np.array([0.7, 0.5, 0.3, 0.1, 0.05, 0.02, 0.01, 0.02, 0.05, 0.1, 0.3, 0.5])
    rho = rho / np.linalg.norm(rho)
    psi = stagger_state(rho, np.array([v & 1 for v in order]), 0.0)
    p = premise_strict(psi, g, order, coords, (12,), (0.0,), 1.5, 4.0)
    assert p["holds"] and p["margin"] > 1.0
    assert p["n_near_edges"] >= 1 and p["n_far_nonedges"] >= 1
    # Brute-force cross-check of the extrema over the same populations.
    idx = index_of(order)
    rad = node_radii(coords, order, (0.0,), (12,))
    assert rad[0] == 0.0 and abs(rad[6] - 6.0) < 1e-9
    near_e = [bond_B(psi, idx[a], idx[b]) for a, b in g.edges()
              if rad[idx[a]] <= 1.5 and rad[idx[b]] <= 1.5]
    assert min(near_e) == p["min_near_B"]
    with pytest.raises(ValueError):
        premise_strict(psi, g, order, coords, (12,), (0.0,), 0.0, 4.0)  # no near edges


def test_E1_E2_current_oddness_J2():
    # Small-J2 traveling pair: B matched bitwise, both currents odd bitwise.
    L = 4
    g = j2_torus_graph(L)
    order = node_order(g)
    c3 = j2_torus_coords(L)
    coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    pp = gaussian_packet(coords, order, (1.0, 2.0), (0.3, 0.0), 0.5, periods=(L, L))
    pm = gaussian_packet(coords, order, (1.0, 2.0), (-0.3, 0.0), 0.5, periods=(L, L))
    idx = index_of(order)
    for a, b in g.edges():
        assert bond_B(pm, idx[a], idx[b]) == bond_B(pp, idx[a], idx[b])
    for ax in (0, 1):
        assert directional_current(pm, g, order, coords, (L, L), ax) == -directional_current(
            pp, g, order, coords, (L, L), ax)
    sub = sublattice_j2(c3)
    assert staggered_current(pm, g, order, sub) == -staggered_current(pp, g, order, sub)
    assert directional_current(pp, g, order, coords, (L, L), 0) > 0  # +k flows +x
