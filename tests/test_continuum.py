"""EM-0 continuum apparatus pins (prereg support; NO campaign data).

Locks the exact discrete law, continuity, J2 Bloch, long-wave Taylor,
isotropy, static operator, Green decay constants, unification identities,
energetics, B/J quadrature, superposition/sign theorems. Campaign numbers
(L20/28/42/64 fronts, xi, delta, verdicts) are FILED in docs/DEFERRED.md,
not pinned here.
"""

import math

import networkx as nx
import numpy as np

from bh_graph.ballistic import adjacency_csr, hamiltonian, node_order
from bh_graph.continuum import (
    BJ_derivatives,
    BJ_from_polar,
    axial_kappa,
    bloch_vs_exact,
    complex_to_rs,
    continuity_residual,
    dE_dA,
    div_J,
    energy_both_ways,
    envelope_pde,
    fit_decay,
    hessian_isotropy,
    ir_kappa,
    is_BJ_identity_ok,
    is_conjugate_ok,
    is_continuity_ok,
    is_energy_match_ok,
    is_global_conservation_ok,
    is_phase_invariant_ok,
    is_real_eq_ok,
    is_sign_flip_phi_ok,
    is_static_ir_ok,
    is_superposition_ok,
    is_unification_exact_ok,
    j2_bloch_bands,
    j2_bloch_matrix,
    j2_group_velocity,
    j2_hessian,
    j2_max_velocities,
    j2_predicted_zero_count,
    j2_touching_count,
    L_dyn,
    L_static_bloch,
    quartic_anisotropy,
    real_rhs,
    rho_dot_from_rs,
    rho_dot_via_h,
    rho_from_rs,
    rs_to_complex,
    static_gap,
    static_ir_symbol,
    taylor_coeffs,
    taylor_predict,
    taylor_residual,
    transient_velocity_predict,
    unification_exact_dev,
    unification_ir_kinetic_match,
    velocity_anisotropy,
)
from bh_graph.driven import bilinears, edge_arrays, path_graph, steady_predict
from bh_graph.formation import j2_torus_graph


def _path_h(n=10):
    g = path_graph(n)
    order = node_order(g)
    return g, order, hamiltonian(g, order=order), adjacency_csr(g, order)


def _j2_h(L=4):
    g = j2_torus_graph(L)
    order = node_order(g)
    return g, order, hamiltonian(g, order=order), adjacency_csr(g, order)


def test_rs_roundtrip():
    rng = np.random.default_rng(0)
    psi = rng.normal(size=16) + 1.0j * rng.normal(size=16)
    r, s = complex_to_rs(psi)
    assert np.array_equal(rs_to_complex(r, s), psi)
    assert np.allclose(rho_from_rs(r, s), np.abs(psi) ** 2)


def test_real_rhs_matches_complex():
    g, order, h, adj = _path_h(8)
    rng = np.random.default_rng(1)
    psi = rng.normal(size=8) + 1.0j * rng.normal(size=8)
    psi = psi / np.linalg.norm(psi)
    assert is_real_eq_ok(psi, h, adj, dt=1e-5, atol=1e-3)


def test_rho_dot_legs_agree():
    for mk in (_path_h, _j2_h):
        g, order, h, adj = mk()
        rng = np.random.default_rng(2)
        psi = rng.normal(size=len(order)) + 1.0j * rng.normal(size=len(order))
        r, s = complex_to_rs(psi)
        a = rho_dot_from_rs(r, s, adj)
        b = rho_dot_via_h(psi, h)
        assert np.abs(a - b).max() < 1e-9


def test_continuity_random_states():
    for mk in (_path_h, _j2_h):
        g, order, h, adj = mk()
        rng = np.random.default_rng(3)
        for _ in range(3):
            psi = rng.normal(size=len(order)) + 1.0j * rng.normal(size=len(order))
            assert is_continuity_ok(psi, g, order, h, adj, atol=1e-9)
            # Divergence antisymmetry: global sum vanishes exactly.
            assert abs(float(div_J(psi, g, order).sum())) < 1e-9


def test_global_conservation_free_evolution():
    from bh_graph.ballistic import evolve_fixed

    g, order, h, _ = _path_h(8)
    psi0 = np.zeros(len(order), dtype=complex)
    psi0[3] = 1.0
    rec = evolve_fixed(psi0, h, 0.05, 10)
    assert is_global_conservation_ok(rec["psi"], atol=1e-9)


def test_bloch_bands_analytic():
    e, f = j2_bloch_bands(0.0, 0.0)
    assert abs(e + 8.0) < 1e-12 and f == 0.0
    e, _ = j2_bloch_bands(math.pi, math.pi)
    assert abs(e - 8.0) < 1e-12
    e, _ = j2_bloch_bands(math.pi / 2.0, math.pi / 2.0)
    assert abs(e) < 1e-12
    # Matrix form reproduces bands as eigenvalues.
    for kx, ky in ((0.3, -0.2), (1.0, 2.0), (math.pi, 0.0)):
        m = j2_bloch_matrix(kx, ky)
        w = sorted(np.linalg.eigvalsh(m))
        e, _ = j2_bloch_bands(kx, ky)
        assert abs(w[0] - min(e, 0.0)) < 1e-9
        assert abs(w[1] - max(e, 0.0)) < 1e-9
        # Hessian is the analytic second derivative.
        hess = j2_hessian(kx, ky)
        assert abs(hess[0, 0] - 4.0 * math.cos(kx)) < 1e-12
        assert abs(hess[1, 1] - 4.0 * math.cos(ky)) < 1e-12
        assert hess[0, 1] == 0.0 and hess[1, 0] == 0.0


def test_bloch_vs_exact_small_tori():
    r4 = bloch_vs_exact(4)
    assert r4["max_dev"] < 1e-9
    assert r4["n_zero_exact"] == r4["n_zero_predicted"]
    assert r4["n_zero_predicted"] == j2_predicted_zero_count(4)
    r6 = bloch_vs_exact(6)
    assert r6["max_dev"] < 1e-9
    # Banked POT-1 calibration: 46 = 36 flat + 10 touching on L6.
    assert r6["n_zero_exact"] == 46
    assert j2_touching_count(6) == 10
    # Banked P1.1b: 838 on L28 (784 flat + 54 touching).
    assert j2_predicted_zero_count(28) == 838
    assert j2_touching_count(28) == 54


def test_group_velocity_maxima():
    m = j2_max_velocities()
    assert abs(m["axial"] - 4.0) < 1e-12
    assert abs(m["euclidean"] - 4.0 * math.sqrt(2.0)) < 1e-12
    assert abs(m["manhattan"] - 8.0) < 1e-12
    v = j2_group_velocity(math.pi / 2.0, math.pi / 2.0)
    assert abs(np.linalg.norm(v) - m["euclidean"]) < 1e-12
    assert abs(abs(v[0]) + abs(v[1]) - 8.0) < 1e-12
    # Headline packet momentum: v(0.3,0) = 4 sin 0.3.
    v = j2_group_velocity(0.3, 0.0)
    assert abs(v[0] - 4.0 * math.sin(0.3)) < 1e-12
    assert abs(v[1]) < 1e-12
    assert abs(v[0] - 1.182080827) < 1e-9


def test_taylor_gamma():
    c = taylor_coeffs((0.0, 0.0))
    assert abs(c["E0"] + 8.0) < 1e-12
    assert np.linalg.norm(c["v"]) < 1e-12
    assert np.allclose(c["Minv"], 4.0 * np.eye(2))
    assert np.linalg.norm(c["cubic"]) < 1e-12
    assert abs(c["quartic"][0] + 1.0 / 6.0) < 1e-12
    assert abs(c["quartic"][1] + 1.0 / 6.0) < 1e-12
    # Order-2 residual at |q|=0.05 is quartic-scale (~1e-6).
    assert abs(taylor_residual((0.0, 0.0), (0.05, 0.0), 2)) < 5e-6
    assert abs(taylor_residual((0.0, 0.0), (0.03, 0.04), 2)) < 5e-6
    # Order-4 residual is 6th-order (tiny).
    assert abs(taylor_residual((0.0, 0.0), (0.05, 0.0), 4)) < 1e-9
    # Predict helper matches manual evaluation.
    assert abs(taylor_predict((0.0, 0.0), (0.1, 0.0), 2) + 8.0 - 2 * 0.01) < 1e-9


def test_envelope_gamma_schrodinger():
    pde = envelope_pde((0.0, 0.0))
    assert pde["kind"] == "schrodinger-like"
    assert pde["isotropic"] and not pde["drift"]
    assert abs(pde["m_star"] - 0.25) < 1e-12
    assert abs(pde["E0"] + 8.0) < 1e-12


def test_hessian_isotropy_gamma():
    c = taylor_coeffs((0.0, 0.0))
    iso = hessian_isotropy(c["Minv"])
    assert iso["isotropic"] and abs(iso["ratio"] - 1.0) < 1e-12
    # Away from Gamma the Hessian is anisotropic (filed, not gated).
    c2 = taylor_coeffs((1.0, 0.2))
    iso2 = hessian_isotropy(c2["Minv"])
    assert not iso2["isotropic"]


def test_velocity_anisotropy_small():
    a = velocity_anisotropy(0.1, n_angles=36)
    assert a["rel_spread"] < 1e-3
    assert abs(a["mean"] - 0.4) < 1e-2  # |v| ~= 4|q| at small q


def test_quartic_anisotropy():
    q = quartic_anisotropy(0.1)
    assert abs(q["ratio"] - 0.5) < 1e-12  # diagonal half of isotropic


def test_static_gap_and_ir():
    assert abs(static_gap(-8.0, -8.5) - 0.5) < 1e-12
    assert is_static_ir_ok()
    # IR symbol spot values: gap + 2|q|^2 at Gamma.
    c = taylor_coeffs((0.0, 0.0))
    assert abs(static_ir_symbol((0.1, 0.0), 0.5, c["Minv"]) - (0.5 + 0.02)) < 1e-9
    assert abs(L_static_bloch(0.0, 0.0, -8.5) - 0.5) < 1e-12


def test_decay_constants():
    k = axial_kappa(-8.5)
    assert abs(k - math.acosh(1.125)) < 1e-12
    assert abs(k - 0.494932923) < 1e-9
    assert abs(ir_kappa(0.5, 2.0) - 0.5) < 1e-12
    try:
        axial_kappa(-7.0)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
    # POT-1 xi protocol recovers an imposed exponential rate.
    means = {r: math.exp(-0.5 * r) for r in range(6)}
    assert abs(fit_decay(means, (2, 3, 4, 5)) - 0.5) < 1e-9


def test_unification_exact():
    assert is_unification_exact_ok()
    assert unification_exact_dev(-8.5, 0.3, -0.2) < 1e-12
    assert abs(L_dyn(-8.5, 0.0, 0.0) + L_static_bloch(0.0, 0.0, -8.5)) < 1e-12


def test_unification_ir_kinetic():
    u = unification_ir_kinetic_match()
    assert np.allclose(u["Minv"], 4.0 * np.eye(2))
    assert abs(u["gap"] - 0.5) < 1e-12
    assert abs(u["offset_mean"] - 0.5) < 1e-9
    assert u["offset_spread"] < 1e-9  # k-independent (exact cancellation)


def test_transient_predict():
    assert abs(transient_velocity_predict() - 8.0) < 1e-12


def test_energy_match_and_conjugate():
    for mk in (_path_h, _j2_h):
        g, order, _, _ = mk()
        rng = np.random.default_rng(5)
        psi = rng.normal(size=len(order)) + 1.0j * rng.normal(size=len(order))
        psi = psi / np.linalg.norm(psi)
        assert is_energy_match_ok(psi, g, order, atol=1e-9)
        eb = energy_both_ways(psi, g, order)
        assert eb["dev"] < 1e-9
        # Conjugate factor spot: dE/dA = -2B.
        assert abs(dE_dA(0.3) + 0.6) < 1e-12
        # Relocation identity on two sample moves.
        idx = {v: i for i, v in enumerate(order)}
        edges = sorted(tuple(sorted(e)) for e in g.edges())
        nonedges = sorted(tuple(sorted(e)) for e in nx.complement(g).edges())
        if edges and nonedges:
            assert is_conjugate_ok(psi, idx, edges[0], nonedges[0])
            assert is_conjugate_ok(psi, idx, edges[-1], nonedges[-1])


def test_BJ_identities_and_derivatives():
    q = BJ_from_polar(0.5, 0.4, 0.7)
    assert abs(q["B"] - 0.5 * 0.4 * math.cos(0.7)) < 1e-12
    assert abs(q["J"] - 0.5 * 0.4 * math.sin(0.7)) < 1e-12
    d = BJ_derivatives(0.5, 0.4, 0.7)
    assert abs(d["dB"] + q["J"]) < 1e-12
    assert abs(d["dJ"] - q["B"]) < 1e-12
    rng = np.random.default_rng(6)
    psi = rng.normal(size=10) + 1.0j * rng.normal(size=10)
    for i, j_ in ((0, 1), (3, 7), (9, 2)):
        assert is_BJ_identity_ok(psi, i, j_)


def test_superposition_and_sign():
    g, order, h, _ = _path_h(10)
    idx = {v: i for i, v in enumerate(order)}
    pins = [idx[2], idx[7]]
    s1 = np.array([1.0, 0.0], dtype=complex)
    s2 = np.array([0.0, -1.0], dtype=complex)
    assert is_superposition_ok(h, pins, s1, s2, -2.5, rtol=1e-9)
    assert is_sign_flip_phi_ok(h, pins, s1 + s2, -2.5, rtol=1e-9)
    gj, oj, hj, _ = _j2_h(4)
    idxj = {v: i for i, v in enumerate(oj)}
    src = [idxj[(0 * 4 + 0) * 2 + 0]]
    assert is_sign_flip_phi_ok(hj, src, np.array([1.0]), -8.5, rtol=1e-9)
    # B/J/E invariance under S -> -S on the J2 single source.
    from bh_graph.continuum import sign_flip_dev

    dev = sign_flip_dev(hj, src, np.array([1.0]), -8.5, gj, oj)
    assert dev["dphi"] < 1e-9
    assert dev["dB"] < 1e-9 and dev["dJ"] < 1e-9
    assert dev["dE"] < 1e-9


def test_phase_invariance_bilinears():
    g, order, _, _ = _path_h(8)
    eu, ev = edge_arrays(g, order)
    rng = np.random.default_rng(7)
    psi = rng.normal(size=8) + 1.0j * rng.normal(size=8)
    b0 = bilinears(psi, eu, ev)
    for alpha in (0.7, 2.1, 4.0):
        b1 = bilinears(psi * np.exp(1.0j * alpha), eu, ev)
        assert is_phase_invariant_ok(b1["B"], b0["B"], atol=1e-12)
        assert is_phase_invariant_ok(b1["J"], b0["J"], atol=1e-12)
