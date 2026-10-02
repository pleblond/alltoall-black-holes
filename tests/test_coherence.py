"""COH apparatus pins (COH-PREREG): reflections, pairs, visibility, spread.

Locks: R_x/R_y in Aut(J2) + H-covariance, pair algebra (N(phi), S),
phi-periodicity, evolution linearity, I_int identity, sinusoid/fringe
fit units, spectral-spread units, conjugation law, boolean checks.
Campaign numbers are FILED in docs/COHERENCE.md, not pinned.
"""

import math

import networkx as nx
import numpy as np

from bh_graph.ballistic import (
    evolve_fixed,
    gaussian_packet,
    hamiltonian,
    node_order,
    ring_coords,
)
from bh_graph.coherence import (
    PHI_SET_4,
    PHI_SET_8,
    axis_region,
    energy_expect,
    fringe_scan_1d,
    gaussian_overlap_pred,
    interference_breakdown,
    is_linearity_ok,
    is_norm_drift_ok,
    is_r2_ok,
    is_swap_ok,
    overlap,
    pair_norm_sq,
    pair_state,
    pushforward,
    reflect_j2_x,
    reflect_j2_y,
    spectral_spread,
    visibility_phi_fit,
)
from bh_graph.formation import j2_torus_coords, j2_torus_graph


def _j2_small(L=4):
    g = j2_torus_graph(L)
    order = node_order(g)
    c3 = j2_torus_coords(L)
    coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    return g, order, coords


def test_reflections_in_aut_j2():
    for L in (4, 6):
        g = j2_torus_graph(L)
        base = {tuple(sorted(e)) for e in g.edges()}
        for perm in (reflect_j2_x(L, 1), reflect_j2_y(L, 2), reflect_j2_x(L), reflect_j2_y(L)):
            assert {v: 1 for v in perm} == {v: 1 for v in g.nodes()}  # permutation
            for v, w in perm.items():
                assert perm[w] == v  # involution
            assert {tuple(sorted((perm[u], perm[v]))) for u, v in g.edges()} == base


def test_h_covariance_under_reflection():
    L = 4
    g = j2_torus_graph(L)
    order = node_order(g)
    h = hamiltonian(g, order=order).toarray()
    idx = {v: i for i, v in enumerate(order)}
    for perm in (reflect_j2_x(L, 1), reflect_j2_y(L, 3)):
        for u in order:
            for v in order:
                assert h[idx[perm[u]], idx[perm[v]]] == h[idx[u], idx[v]]


def test_pair_algebra_and_phi_periodicity():
    rng = np.random.default_rng(0)
    a = rng.standard_normal(32) + 1j * rng.standard_normal(32)
    b = rng.standard_normal(32) + 1j * rng.standard_normal(32)
    s = overlap(a, b)
    assert overlap(a, b) == np.conj(overlap(b, a))
    for phi in PHI_SET_8:
        n = float(np.vdot(a, a).real + np.vdot(b, b).real)
        expect = n + 2.0 * (np.exp(1j * phi) * s).real
        assert (
            abs(float(np.vdot(pair_state(a, b, phi), pair_state(a, b, phi)).real) - expect) < 1e-9
        )
        assert np.allclose(pair_state(a, b, phi + 2 * math.pi), pair_state(a, b, phi))
    an = a / np.linalg.norm(a)
    bn = b / np.linalg.norm(b)
    sn = overlap(an, bn)
    for phi in PHI_SET_8:
        assert abs(np.linalg.norm(pair_state(an, bn, phi)) ** 2 - pair_norm_sq(sn, phi)) < 1e-12
    assert set(PHI_SET_4) <= set(PHI_SET_8)  # 4-set embedded in 8-set


def test_evolution_linearity_ringlet():
    n = 60
    g = nx.cycle_graph(n)
    order = node_order(g)
    coords = ring_coords(n)
    h = hamiltonian(g, order=order)
    a = gaussian_packet(coords, order, (15.0,), (0.5,), 5.0, periods=(n,))
    b = gaussian_packet(coords, order, (20.0,), (0.5,), 5.0, periods=(n,))
    ra = evolve_fixed(a, h, 0.1, 30)
    rb = evolve_fixed(b, h, 0.1, 30)
    for phi in PHI_SET_8:
        rj = evolve_fixed(pair_state(a, b, phi), h, 0.1, 30)
        assert is_linearity_ok(rj["psi"][-1], ra["psi"][-1], rb["psi"][-1], phi)
        assert not is_linearity_ok(rj["psi"][-1], ra["psi"][-1], rb["psi"][-1], phi + 0.5)
        assert is_norm_drift_ok(rj["psi"][0], rj["psi"][-1])
        assert not is_norm_drift_ok(rj["psi"][0], 2.0 * rj["psi"][-1])


def test_iint_identity_on_random_states():
    rng = np.random.default_rng(1)
    for _ in range(4):
        a = rng.standard_normal(48) + 1j * rng.standard_normal(48)
        b = rng.standard_normal(48) + 1j * rng.standard_normal(48)
        for phi in (0.0, 0.7, math.pi):
            br = interference_breakdown(a, b, phi)
            assert np.abs(br["I_int"] - br["cross_pred"]).max() < 1e-12
            assert abs(br["sum_AB"] - br["sum_A"] - br["sum_B"] - br["cross_pred"].sum()) < 1e-9
            sub = interference_breakdown(a, b, phi, region=[0, 1, 2])
            assert len(sub["I_AB"]) == 3


def test_visibility_fit_unit():
    ph = np.array(PHI_SET_8)
    y = 3.0 + 1.5 * np.cos(ph + 0.4)
    f = visibility_phi_fit(ph, y)
    assert abs(f["V"] - 0.5) < 1e-12
    assert abs((f["delta"] - 0.4 + math.pi) % (2 * math.pi) - math.pi) < 1e-12
    assert f["r2"] > 1 - 1e-12 and is_r2_ok(f["r2"]) and not is_r2_ok(0.5)
    flat = visibility_phi_fit(ph, np.full_like(ph, 2.0))
    assert flat["V"] < 1e-12 and flat["r2"] == 1.0


def test_overlap_prediction_equals_measured_v():
    rng = np.random.default_rng(2)
    a = rng.standard_normal(64) + 1j * rng.standard_normal(64)
    b = rng.standard_normal(64) + 1j * rng.standard_normal(64)
    a, b = a / np.linalg.norm(a), b / np.linalg.norm(b)
    sums = [interference_breakdown(a, b, phi)["sum_AB"] for phi in PHI_SET_8]
    f = visibility_phi_fit(PHI_SET_8, sums)
    assert abs(f["V"] - abs(overlap(a, b))) < 1e-12  # V_meas == |S| exactly
    assert abs(gaussian_overlap_pred(0.0, 4.0) - 1.0) < 1e-15
    assert abs(gaussian_overlap_pred(8.0, 4.0) - math.exp(-0.5)) < 1e-15


def test_spectral_spread_units():
    h = np.diag([1.0, 3.0, 3.0, 5.0])
    assert spectral_spread(np.array([1, 0, 0, 0], dtype=complex), h) == 0.0  # eigenstate
    sup = np.array([1, 0, 0, 1], dtype=complex) / math.sqrt(2.0)
    assert abs(spectral_spread(sup, h) - 2.0) < 1e-12  # gap/2
    assert abs(energy_expect(sup, h) - 3.0) < 1e-12
    sparse = nx.to_scipy_sparse_array(nx.path_graph(4), format="csr", dtype=float)
    v = np.array([0.5, 0.5, 0.5, 0.5], dtype=complex)
    assert spectral_spread(v, sparse) >= 0.0  # sparse-safe


def test_fringe_scan_unit():
    x = np.linspace(0.0, 40.0, 401)
    env = np.exp(-((x - 20.0) ** 2) / 72.0) + 1e-6
    inten = env * (1.0 + 0.9 * np.cos(2 * 0.3 * x + 1.1))
    f = fringe_scan_1d(x, inten, env)
    assert abs(f["k_fit"] - 0.3) / 0.3 < 0.02
    assert abs(f["V"] - 0.9) < 0.02
    assert f["r2"] > 0.999


def test_conjugation_and_swap_symmetry():
    _g, order, coords = _j2_small()
    L = 4
    perm = reflect_j2_y(L, 1)
    a = gaussian_packet(coords, order, (1.0, 2.0), (0.3, 0.0), 0.6, periods=(L, L))
    b = pushforward(a, perm, order)  # mirrored arm
    assert is_swap_ok(abs(overlap(a, b)), abs(overlap(b, a)))
    assert not is_swap_ok(0.5, 0.6)
    for phi in PHI_SET_4:
        left = np.abs(pair_state(a, b, phi)) ** 2
        right = np.abs(pushforward(pair_state(a, b, -phi), perm, order)) ** 2
        assert np.abs(left - right).max() < 1e-9  # I(phi) = R_* I(-phi)


def test_axis_region_fixed_rule():
    _g, order, coords = _j2_small()
    sel = axis_region(order, coords, 1.0, 1.0, 4, radius=1.0)
    assert len(sel) > 0 and max(sel) < len(order) and len(set(sel)) == len(sel)
    assert axis_region(order, coords, 1.0, 1.0, 4, radius=1.0) == sel  # deterministic
