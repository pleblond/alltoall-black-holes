"""POT-0 apparatus pins (prereg support; NO campaign data here).

Locks: quotient edge table (axis steps), bond-current antisymmetry,
D = |J_net|/S algebra (plane wave D = 1, standing/real D = 0), k->-k
covariance, global-phase invariance, J2 automorphism covariance,
spectral-C units (uniform C = 1, single-site C = 1/L^2), scrambling /
dephasing / aperture prep rules, spearman units, trace determinism.
Headline numbers (L28, T=10) are FILED in docs/DEFERRED.md, not pinned.
"""

import math

import numpy as np

from bh_graph.ballistic import (
    evolve_fixed,
    gaussian_packet,
    hamiltonian,
    node_order,
)
from bh_graph.formation import j2_torus_coords, j2_torus_graph
from bh_graph.potential import (
    ang_diff,
    aperture_mask,
    aperture_state,
    bond_current,
    cos_between,
    d_trace,
    dephasing_family,
    directional_order,
    edge_table,
    flux_decomposition,
    gradient_family,
    is_auto_ok,
    is_d_ok,
    is_flux_decomp_ok,
    is_match_ok,
    null_ensemble,
    pushforward,
    quotient_coords,
    reflectx_perm,
    rot90_perm,
    scramble_phases,
    spectral_coherence,
    spearman,
    translate_perm,
)


def _j2_small(L=8):
    g = j2_torus_graph(L)
    order = node_order(g)
    c3 = j2_torus_coords(L)
    coords = quotient_coords(c3)
    return g, order, c3, coords


def _plane_wave(order, c3, k, axis="x"):
    idx = {v: i for i, v in enumerate(order)}
    psi = np.zeros(len(order), dtype=complex)
    for v, (x, y, _) in c3.items():
        s = x if axis == "x" else y
        psi[idx[v]] = np.exp(1.0j * k * s)
    return psi / np.linalg.norm(psi)


def test_edge_table_axis_steps():
    g, order, _, coords = _j2_small(8)
    edges = edge_table(g, order, coords, 8)
    assert len(edges) == g.number_of_edges()
    nx_e = sum(1 for _, _, dx, dy in edges if dx != 0)
    ny_e = sum(1 for _, _, dx, dy in edges if dy != 0)
    for _, _, dx, dy in edges:
        assert (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1))
    assert nx_e == ny_e  # x/y symmetric (diagonal automorphism)


def test_bond_current_units():
    assert bond_current(1.0 + 0j, 1.0 + 0j) == 0.0  # real: no current
    assert bond_current(1.0 + 0j, 1.0j) == 2.0
    assert bond_current(1.0j, 1.0 + 0j) == -2.0  # antisymmetric
    a, b = 0.3 + 0.4j, -0.1 + 0.7j
    assert bond_current(a, b) == -bond_current(b, a)
    assert bond_current(a, b, j=2.0) == 2.0 * bond_current(a, b, j=1.0)


def test_plane_wave_d_one():
    # Periodic k = 2*pi/L (seam-free: non-periodic k puts anomalous
    # current on wrap bonds; headline k=0.3 is P1.1b-gated sigma<<L/6).
    L = 8
    k = 2.0 * math.pi / L
    g, order, c3, coords = _j2_small(L)
    edges = edge_table(g, order, coords, L)
    f = flux_decomposition(_plane_wave(order, c3, k, "x"), edges)
    assert is_flux_decomp_ok(f)
    assert abs(f["D"] - 1.0) < 1e-12  # ideal single-direction mode
    assert abs(f["angle"]) < 1e-12
    assert f["J_classes"]["+y"] == 0.0 and f["J_classes"]["-y"] == 0.0
    fy = flux_decomposition(_plane_wave(order, c3, k, "y"), edges)
    assert abs(fy["D"] - 1.0) < 1e-12
    assert abs(fy["angle"] - math.pi / 2) < 1e-12


def test_standing_and_real_states_d_zero():
    g, order, c3, coords = _j2_small(8)
    edges = edge_table(g, order, coords, 8)
    pp = _plane_wave(order, c3, 0.3, "x")
    pm = _plane_wave(order, c3, -0.3, "x")
    stand = (pp + pm) / np.linalg.norm(pp + pm)
    f = flux_decomposition(stand, edges)
    assert f["S"] == 0.0 and f["D"] == 0.0  # balanced: cos(kx) real
    src = gaussian_packet(coords, order, (2.0, 4.0), (0.0, 0.0), 1.2, periods=(8, 8))
    f0 = flux_decomposition(src, edges)
    assert f0["S"] < 1e-24 and f0["D"] == 0.0  # uniform phase: no current


def test_k_reversal_covariance():
    _, order, _, coords = _j2_small(8)
    g, _, _, _ = _j2_small(8)
    edges = edge_table(g, order, coords, 8)
    pp = gaussian_packet(coords, order, (2.0, 4.0), (0.3, 0.0), 1.2, periods=(8, 8))
    pm = gaussian_packet(coords, order, (2.0, 4.0), (-0.3, 0.0), 1.2, periods=(8, 8))
    fp = flux_decomposition(pp, edges)
    fm = flux_decomposition(pm, edges)
    assert is_match_ok(fp["D"], fm["D"], 1e-9)  # |D| matched
    assert cos_between(fp["J_net"], fm["J_net"]) < -1 + 1e-9  # reversed
    assert abs(ang_diff(fp["angle"], fm["angle"]) - math.pi) < 1e-9


def test_global_phase_invariance():
    g, order, c3, coords = _j2_small(8)
    edges = edge_table(g, order, coords, 8)
    psi = gaussian_packet(coords, order, (2.0, 4.0), (0.3, 0.0), 1.2, periods=(8, 8))
    f0 = flux_decomposition(psi, edges)
    c0 = spectral_coherence(psi, order, c3, 8)
    for phi in (0.7, 2.1, 4.0):
        rot = psi * np.exp(1.0j * phi)
        f1 = flux_decomposition(rot, edges)
        assert abs(f1["D"] - f0["D"]) < 1e-12
        assert np.abs(f1["J_net"] - f0["J_net"]).max() < 1e-12
        assert abs(f1["S"] - f0["S"]) < 1e-12
        c1 = spectral_coherence(rot, order, c3, 8)
        assert abs(c1["C"] - c0["C"]) < 1e-12


def test_automorphisms_and_covariance():
    L = 6
    g, order, c3, coords = _j2_small(L)
    perms = {
        "rot90": rot90_perm(L),
        "reflectx": reflectx_perm(L),
        "translate": translate_perm(L, 2, 4),
    }
    for name, p in perms.items():
        assert is_auto_ok(g, p), name
    assert not is_auto_ok(g, {v: v for v in order} | {order[0]: order[1]})
    edges = edge_table(g, order, coords, L)
    # Rotation covariance: +x plane wave -> +y plane wave.
    px = _plane_wave(order, c3, 0.3, "x")
    fx = flux_decomposition(px, edges)
    pr = pushforward(px, perms["rot90"], order)
    fr = flux_decomposition(pr, edges)
    assert is_match_ok(fx["D"], fr["D"], 1e-9)
    assert abs(ang_diff(fr["angle"], fx["angle"]) - math.pi / 2) < 1e-9
    # Translation: lab-frame flux vector identical (same multiset).
    pkt = gaussian_packet(coords, order, (1.0, 2.0), (0.3, 0.0), 1.0, periods=(L, L))
    fp = flux_decomposition(pkt, edges)
    ft = flux_decomposition(pushforward(pkt, perms["translate"], order), edges)
    assert np.abs(ft["J_net"] - fp["J_net"]).max() < 1e-9
    assert abs(ft["D"] - fp["D"]) < 1e-9


def test_flux_algebra_random():
    g, order, _, coords = _j2_small(6)
    edges = edge_table(g, order, coords, 6)
    rng = np.random.default_rng(11)
    for _ in range(5):
        psi = rng.normal(size=len(order)) + 1.0j * rng.normal(size=len(order))
        psi = psi / np.linalg.norm(psi)
        f = flux_decomposition(psi, edges)
        assert is_flux_decomp_ok(f)
        assert is_d_ok(f["D"]) and not is_d_ok(1.5) and not is_d_ok(-0.1)


def test_directional_order_matches_flux():
    L = 8
    k = 2.0 * math.pi / L  # seam-free periodic gradient
    g, order, _, coords = _j2_small(L)
    psi = gaussian_packet(coords, order, (2.0, 4.0), (k, 0.0), 1.2, periods=(L, L))
    f = directional_order(psi, g, order, coords, L)
    assert is_flux_decomp_ok(f) and abs(f["D"] - 1.0) < 1e-9  # aligned


def test_spectral_coherence_units():
    _, order, c3, _ = _j2_small(8)
    uni = np.full(len(order), 1.0 / math.sqrt(len(order)), dtype=complex)
    cu = spectral_coherence(uni, order, c3, 8)
    assert abs(cu["C"] - 1.0) < 1e-12 and abs(cu["M_eff"] - 1.0) < 1e-9
    loc = np.zeros(len(order), dtype=complex)
    loc[0] = 1.0
    cl = spectral_coherence(loc, order, c3, 8)
    assert abs(cl["C"] - 1.0 / 64) < 1e-12  # flat spectrum
    assert abs(cl["M_eff"] - 64.0) < 1e-9


def test_scramble_dephasing_null_rules():
    _, order, _, coords = _j2_small(8)
    psi = gaussian_packet(coords, order, (2.0, 4.0), (0.3, 0.0), 1.2, periods=(8, 8))
    scr = scramble_phases(psi, seed=3)
    assert np.allclose(np.abs(scr), np.abs(psi))  # envelope-exact
    assert abs(np.linalg.norm(scr) - 1.0) < 1e-12  # norm-exact
    assert not np.allclose(np.angle(scr), np.angle(psi))  # phases destroyed
    assert np.array_equal(scr, scramble_phases(psi, seed=3))  # deterministic
    fam = dephasing_family(psi, (0.0, 0.5, 1.0), seed=5)
    assert np.array_equal(fam[1.0], psi)  # c=1 is clean
    for c, q in fam.items():
        assert np.allclose(np.abs(q), np.abs(psi)), c
        assert abs(np.linalg.norm(q) - 1.0) < 1e-12, c
    assert np.array_equal(fam[0.5], dephasing_family(psi, (0.5,), seed=5)[0.5])
    nulls = null_ensemble(psi, n=4, seed0=7)
    assert len(nulls) == 4
    for q in nulls:
        assert np.allclose(np.abs(q), np.abs(psi))
    assert np.array_equal(nulls[0], null_ensemble(psi, n=4, seed0=7)[0])


def test_gradient_family_endpoints():
    _, order, _, coords = _j2_small(8)
    fam = gradient_family(coords, order, (2.0, 4.0), (0.3, 0.0), 1.2, (0.0, 0.5, 1.0), 8)
    direct0 = gaussian_packet(coords, order, (2.0, 4.0), (0.0, 0.0), 1.2, periods=(8, 8))
    direct1 = gaussian_packet(coords, order, (2.0, 4.0), (0.3, 0.0), 1.2, periods=(8, 8))
    assert np.array_equal(fam[0.0], direct0)  # c=0 is the uniform source
    assert np.array_equal(fam[1.0], direct1)  # c=1 is the validated packet
    for q in fam.values():  # envelope-exact across c
        assert np.allclose(np.abs(q), np.abs(direct0))


def test_aperture_keeps_gradient():
    _, order, _, coords = _j2_small(8)
    psi = gaussian_packet(coords, order, (2.0, 4.0), (0.3, 0.0), 1.2, periods=(8, 8))
    mask = aperture_mask(order, coords, (2.0, 4.0), 2.0, 8)
    assert 0 < mask.sum() < len(order)
    ap = aperture_state(psi, mask)
    assert abs(np.linalg.norm(ap) - 1.0) < 1e-12
    assert np.all(ap[~mask] == 0.0)
    ratio = ap[mask] / psi[mask]
    assert np.allclose(ratio, ratio[0])  # positive-real global rescale
    assert abs(ratio[0].imag) < 1e-12 and ratio[0].real > 0
    full = aperture_mask(order, coords, (2.0, 4.0), 100.0, 8)
    assert full.all() and np.array_equal(aperture_state(psi, full), psi)


def test_spearman_units():
    assert spearman((1, 2, 3, 4), (1, 2, 3, 4)) == 1.0
    assert spearman((1, 2, 3, 4), (4, 3, 2, 1)) == -1.0
    assert spearman((1, 1, 1, 1), (1, 2, 3, 4)) == 0.0  # degenerate
    assert spearman((0.0, 0.5, 1.0), (0.1, 0.2, 0.9)) > 0.99


def test_quotient_coords_sheets_share():
    _, order, c3, _ = _j2_small(6)
    q = quotient_coords(c3)
    assert set(q) == set(order)
    seen = {}
    for v, (x, y, b) in c3.items():
        seen.setdefault((x, y), {})[b] = q[v]
    for (x, y), d in seen.items():
        assert d[0] == (float(x), float(y)) and d[1] == (float(x), float(y))


def test_trace_shapes_and_determinism():
    g, order, _, coords = _j2_small(4)
    edges = edge_table(g, order, coords, 4)
    psi = gaussian_packet(coords, order, (1.0, 2.0), (0.3, 0.0), 0.6, periods=(4, 4))
    h = hamiltonian(g, order=order)
    rec1 = evolve_fixed(psi, h, 0.1, 5)
    rec2 = evolve_fixed(psi, h, 0.1, 5)
    assert np.array_equal(rec1["psi"], rec2["psi"])
    tr = d_trace(rec1["psi"], edges)
    assert tr["D"].shape == (6,) and tr["J_net"].shape == (6, 2)
    assert all(is_d_ok(d) for d in tr["D"])
    tr2 = d_trace(rec2["psi"], edges)
    assert np.array_equal(tr["D"], tr2["D"])  # readout deterministic


def test_match_and_angle_helpers():
    assert is_match_ok(1.0, 1.05, 0.1) and not is_match_ok(1.0, 1.5, 0.1)
    assert cos_between(np.array([1.0, 0.0]), np.array([-1.0, 0.0])) == -1.0
    assert cos_between(np.array([0.0, 0.0]), np.array([1.0, 0.0])) == 0.0
    assert abs(ang_diff(0.0, math.pi) - math.pi) < 1e-12
    assert abs(ang_diff(0.1, 0.1 + 2 * math.pi)) < 1e-12
