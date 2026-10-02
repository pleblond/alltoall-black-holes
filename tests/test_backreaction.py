"""BR-0 bond-energy landscape apparatus pins + control gates (pre-data, analytic only).

Locks: local Delta-E reduction vs full-H (C0), V0 exact null (C1), global
phase invariance (C2), endpoint symmetry (C3), k->-k exact invariance (C4),
sampling reproducibility + formation-distribution mirror (C5), M1 N/E/
simplicity preservation, amplitude quadratic scaling (no-amplitude-scan
justification), uniform-flat theorem on regular graphs. Campaign verdicts
are FILED in docs/DEFERRED.md, never pinned here.
"""

import math
import random

import networkx as nx
import numpy as np

from bh_graph.backreaction import (
    EPS_DEFAULT,
    all_relocations,
    bond_B,
    bond_field_on_edges,
    count_relocations,
    delta_e_batch,
    delta_e_full,
    delta_e_local,
    edge_midpoint,
    energy_edge_sum,
    energy_full,
    is_bond_symmetric_ok,
    is_near,
    landscape_stats,
    midpoint_radius,
    move_stays_connected,
    radial_anatomy,
    run_landscape,
    run_landscape_exhaustive,
    sample_relocations,
    uniform_psi,
    zero_psi,
)
from bh_graph.ballistic import (
    gaussian_packet,
    hamiltonian,
    index_of,
    is_normalized_ok,
    node_order,
    ring_coords,
)
from bh_graph.formation import (
    j2_torus_coords,
    j2_torus_graph,
    propose_relocation,
    state_from_nx,
)


def _rand_psi(n, seed):
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(n) + 1j * rng.standard_normal(n)
    return v / np.linalg.norm(v)


def test_bond_B_known_values_and_symmetry():
    assert abs(bond_B(np.array([1, 1]) / math.sqrt(2), 0, 1) - 0.5) < 1e-12
    assert bond_B(np.array([1, 1j]) / math.sqrt(2), 0, 1) == 0.0
    psi = _rand_psi(9, 0)
    for i in range(9):
        for j in range(9):
            assert is_bond_symmetric_ok(psi, i, j)
            assert bond_B(psi, i, j) == bond_B(psi, j, i)  # bitwise (C3 root)


def test_energy_matches_ballistic_hamiltonian():
    g = nx.cycle_graph(12)
    order = node_order(g)
    psi = _rand_psi(12, 1)
    h = hamiltonian(g, j=1.0, order=order)
    expect = float(np.real(np.vdot(psi, h @ psi)))
    assert abs(energy_full(psi, g, order) - expect) < 1e-12
    assert abs(energy_edge_sum(psi, g, order) - expect) < 1e-12


def test_local_energy_identity_C0():
    # C0: local reduction == full-H evaluation to 1e-9 on every substrate
    # class (path/cycle/J2-torus/ER) x (random/uniform/zero states).
    graphs = [nx.path_graph(10), nx.cycle_graph(14), j2_torus_graph(4),
              nx.fast_gnp_random_graph(24, 0.2, seed=3)]
    for gi, g in enumerate(graphs):
        order = node_order(g)
        idx = index_of(order)
        n = len(order)
        states = [_rand_psi(n, 100 + gi), uniform_psi(n), zero_psi(n)]
        moves = sample_relocations(g, 300, seed=gi)
        assert len(moves) == 300
        for psi in states:
            loc = np.array([delta_e_local(psi, idx, r, a) for r, a in moves])
            full = np.array([delta_e_full(psi, g, order, r, a) for r, a in moves])
            assert np.max(np.abs(loc - full)) < 1e-9, gi
            bat = delta_e_batch(psi, idx, [m[0] for m in moves], [m[1] for m in moves])
            assert np.max(np.abs(np.asarray(bat) - loc)) < 1e-12  # batch == scalar
            assert abs(energy_full(psi, g, order)
                       - energy_edge_sum(psi, g, order)) < 1e-9


def test_zero_field_exact_null_C1():
    # C1 hard gate: psi = 0 -> Delta E == 0.0 bitwise for every move.
    g = j2_torus_graph(4)
    order = node_order(g)
    idx = index_of(order)
    psi = zero_psi(len(order))
    assert energy_full(psi, g, order) == 0.0
    for r, a in sample_relocations(g, 2000, seed=0):
        assert delta_e_local(psi, idx, r, a) == 0.0
        assert delta_e_full(psi, g, order, r, a) == 0.0
    st = landscape_stats(delta_e_batch(psi, idx,
                                        [m[0] for m in sample_relocations(g, 2000, seed=1)],
                                        [m[1] for m in sample_relocations(g, 2000, seed=1)]))
    assert st["f_neg"] == 0.0 and st["f_pos"] == 0.0 and st["f_zero"] == 1.0


def test_global_phase_invariance_C2():
    # C2 hard gate: psi -> e^{itheta} psi leaves every Delta E unchanged.
    g = nx.cycle_graph(20)
    order = node_order(g)
    idx = index_of(order)
    psi = _rand_psi(20, 2)
    moves = sample_relocations(g, 1000, seed=0)
    base = delta_e_batch(psi, idx, [m[0] for m in moves], [m[1] for m in moves])
    for th in (0.7, 2.1, math.pi):
        rot = delta_e_batch(psi * np.exp(1j * th), idx,
                            [m[0] for m in moves], [m[1] for m in moves])
        assert np.max(np.abs(rot - base)) < 1e-12, th


def test_endpoint_symmetry_C3():
    # C3: reversing endpoint order changes nothing (bitwise, B symmetric).
    g = nx.path_graph(16)
    order = node_order(g)
    idx = index_of(order)
    psi = _rand_psi(16, 3)
    for r, a in sample_relocations(g, 500, seed=0):
        fwd = delta_e_local(psi, idx, r, a)
        assert delta_e_local(psi, idx, (r[1], r[0]), a) == fwd
        assert delta_e_local(psi, idx, r, (a[1], a[0])) == fwd
        assert delta_e_local(psi, idx, (r[1], r[0]), (a[1], a[0])) == fwd


def test_momentum_reversal_exact_C4():
    # C4: literal k -> -k (complex conjugate) preserves every B_ij hence
    # every Delta E; the symmetric potential cannot manufacture direction.
    n = 60
    order = list(range(n))
    coords = ring_coords(n)
    pp = gaussian_packet(coords, order, (15.0,), (0.5,), 6.0, periods=(n,))
    pm = gaussian_packet(coords, order, (15.0,), (-0.5,), 6.0, periods=(n,))
    assert np.allclose(pm, np.conj(pp))
    g = nx.cycle_graph(n)
    idx = index_of(order)
    moves = sample_relocations(g, 2000, seed=0)
    dp = delta_e_batch(pp, idx, [m[0] for m in moves], [m[1] for m in moves])
    dm = delta_e_batch(pm, idx, [m[0] for m in moves], [m[1] for m in moves])
    assert np.max(np.abs(dp - dm)) < 1e-12
    assert np.max(np.abs(dp - dm)) == 0.0  # bitwise (conjugation theorem)


def test_amplitude_quadratic_scaling():
    # dE(lam*psi) = lam^2 dE(psi): linear scaling makes amplitude scans redundant.
    g = nx.cycle_graph(18)
    order = node_order(g)
    idx = index_of(order)
    psi = _rand_psi(18, 4)
    moves = sample_relocations(g, 300, seed=0)
    base = delta_e_batch(psi, idx, [m[0] for m in moves], [m[1] for m in moves])
    for lam in (0.0, 0.5, 2.0, -1.5):
        got = delta_e_batch(lam * psi, idx, [m[0] for m in moves], [m[1] for m in moves])
        assert np.allclose(got, lam * lam * base, atol=1e-12), lam


def test_uniform_flat_on_regular_graphs():
    # Uniform psi has constant B = 1/N: every M1 move is exactly neutral
    # (filed as mechanism information; NOT a vacuum claim, BR0-PREREG V1-status).
    for g in (nx.cycle_graph(30), j2_torus_graph(4)):
        order = node_order(g)
        idx = index_of(order)
        n = len(order)
        psi = uniform_psi(n)
        assert is_normalized_ok(psi)
        z = {d for _, d in g.degree()}
        assert len(z) == 1  # regular
        deg = z.pop()
        h = hamiltonian(g, j=1.0, order=order)
        assert np.allclose((h @ psi), -deg * psi, atol=1e-12)  # H ground state
        for r, a in sample_relocations(g, 1000, seed=0):
            assert delta_e_local(psi, idx, r, a) == 0.0
        assert abs(energy_full(psi, g, order) + deg) < 1e-9  # E = -J*z


def test_sampler_mirrors_formation_stream_C5():
    # C5 root: our M1 stream is bitwise-identical to formation.propose_relocation.
    g = nx.fast_gnp_random_graph(40, 0.15, seed=7)
    st = state_from_nx(g)
    rng = random.Random(11)
    expect = [propose_relocation(st, rng) for _ in range(200)]
    got = sample_relocations(g, 200, seed=11)
    assert got == expect
    again = sample_relocations(g, 200, seed=11)
    assert again == got  # seed determinism
    other = sample_relocations(g, 200, seed=12)
    assert other != got  # independent streams


def test_exhaustive_count_and_agreement_C5():
    # Census size identity + sampled-vs-exhaustive agreement within 3x binomial SE.
    assert count_relocations(nx.path_graph(4)) == 9
    assert len(list(all_relocations(nx.path_graph(4)))) == 9
    g = nx.cycle_graph(10)
    assert count_relocations(g) == len(list(all_relocations(g)))
    order = node_order(g)
    idx = index_of(order)
    psi = _rand_psi(10, 5)
    exact = np.array([delta_e_local(psi, idx, r, a) for r, a in all_relocations(g)])
    f_exact = float(np.mean(exact < -EPS_DEFAULT))
    moves = sample_relocations(g, 5000, seed=0)
    samp = delta_e_batch(psi, idx, [m[0] for m in moves], [m[1] for m in moves])
    f_samp = float(np.mean(samp < -EPS_DEFAULT))
    se = math.sqrt(f_exact * (1 - f_exact) / len(moves))
    assert abs(f_samp - f_exact) < 3 * se + 1e-3


def test_move_class_preserves_N_E_simplicity():
    # M1 primary: N, E, simplicity preserved; degrees/connectivity NOT required.
    g = j2_torus_graph(4)
    n0, e0 = g.number_of_nodes(), g.number_of_edges()
    for r, a in sample_relocations(g, 500, seed=0):
        g2 = g.copy()
        g2.remove_edge(*r)
        g2.add_edge(*a)
        assert g2.number_of_nodes() == n0 and g2.number_of_edges() == e0
        assert nx.number_of_selfloops(g2) == 0
        assert not isinstance(g2, nx.MultiGraph)


def test_disconnect_covariate_units():
    # Bridge removal without reconnection disconnects (rare path); bare J2 is bridgeless.
    g = nx.Graph()
    g.add_nodes_from([0, 1, 2, 4, 5, 6])
    g.add_edges_from([(0, 1), (1, 2), (2, 0), (2, 4), (4, 5), (5, 6)])
    bridges = set(tuple(sorted(e)) for e in nx.bridges(g))
    assert (2, 4) in bridges and (0, 1) not in bridges
    assert not move_stays_connected(g, bridges, (2, 4), (4, 6))  # within-side add
    assert move_stays_connected(g, bridges, (0, 1), (4, 6))  # non-bridge removal
    assert move_stays_connected(g, bridges, (2, 4), (0, 5))  # bridge + reconnect
    j2 = j2_torus_graph(4)
    assert len(list(nx.bridges(j2))) == 0  # relocation cannot disconnect bare J2


def test_midpoint_and_near_far_units():
    coords = ring_coords(100)
    assert midpoint_radius(edge_midpoint(10, 12, coords, (100,)), (11.0,), (100,)) < 1e-9
    assert is_near(np.array([11.0]), (11.0,), 3.0, (100,))
    assert not is_near(np.array([50.0]), (11.0,), 3.0, (100,))
    assert is_near(np.array([99.0]), (1.0,), 3.0, (100,))  # minimal-image wrap


def test_run_landscape_partition_and_determinism():
    g = nx.cycle_graph(30)
    order = node_order(g)
    coords = ring_coords(30)
    psi = gaussian_packet(coords, order, (7.0,), (0.5,), 3.0, periods=(30,))
    assert is_normalized_ok(psi)
    r1 = run_landscape(g, order, coords, (30,), psi, (7.0,), 3.0, 5000, seed=0)
    r2 = run_landscape(g, order, coords, (30,), psi, (7.0,), 3.0, 5000, seed=0)
    assert r1 == r2  # deterministic
    assert r1["near"]["n"] + r1["far"]["n"] == r1["n_moves"] == 5000
    assert sum(r1["cells"][t]["n"] for t in ("nn", "nf", "fn", "ff")) == 5000
    assert r1["frac_connected"] == 1.0  # cycle is bridgeless
    assert r1["n_bridges"] == 0
    re_ = run_landscape_exhaustive(g, order, coords, (30,), psi, (7.0,), 3.0)
    assert re_["exhaustive"] and re_["n_moves"] == count_relocations(g) == 30 * 405
    assert re_["near"]["n"] + re_["far"]["n"] == re_["n_moves"]


def test_anatomy_partition_and_fields():
    g = nx.cycle_graph(24)
    order = node_order(g)
    coords = ring_coords(24)
    psi = gaussian_packet(coords, order, (6.0,), (0.5,), 2.5, periods=(24,))
    r = run_landscape(g, order, coords, (24,), psi, (6.0,), 2.5, 3000, seed=0)
    a = r["anatomy"]
    assert len(a["rbins"]) == 31 and a["rbins"][0] == 0.0
    assert sum(a["rem_all"]) == sum(a["add_all"]) == 3000
    assert sum(a["rem_neg"]) == sum(a["add_neg"]) == r["global"]["n_neg"]
    assert abs(sum(r["psi_sq"]) - 1.0) < 1e-12
    assert len(r["psi_sq"]) == 24 and len(r["bond_B_edges"]) == 24
    idx = index_of(order)
    elist = sorted(tuple(sorted(e)) for e in g.edges())
    assert r["bond_B_edges"][0] == bond_B(psi, idx[elist[0][0]], idx[elist[0][1]])
    assert abs(-2.0 * sum(r["bond_B_edges"]) - r["e_psi"]) < 1e-9
    z = run_landscape(g, order, coords, (24,), zero_psi(24), (6.0,), 2.5, 1000, seed=0)
    assert sum(z["psi_sq"]) == 0.0 and all(b == 0.0 for b in z["bond_B_edges"])
    assert sum(z["anatomy"]["rem_neg"]) == 0


def test_j2_torus_packet_prep_convention():
    # J2 campaign prep convention: (x, y) readout coords + periods (L, L),
    # sigma < L/6 spread gate, P1.1b-validated (L28, sigma 4, k (0.3, 0)).
    from bh_graph.ballistic import packet_spread_ok

    L = 28
    g = j2_torus_graph(L)
    order = node_order(g)
    c3 = j2_torus_coords(L)
    coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    assert set(coords) == set(order)
    assert packet_spread_ok(4.0, (L, L))
    psi = gaussian_packet(coords, order, (7.0, 14.0), (0.3, 0.0), 4.0, periods=(L, L))
    assert is_normalized_ok(psi)
    assert energy_full(psi, g, order) < 0.0  # bound packet: negative hopping energy
