"""RESPONSE-0 pins: exact disturbance/response kernel (pre-data apparatus gates).

Every spec letter 0A..0Z + 0AA carries at least one pin. Dense checks run on
tiny graphs (path, J2 L<=4); Krylov cross-checks on J2 L<=6. Consumed
apparatus (ballistic/potential/driven/continuum/backreaction/malus/quot) is
cross-checked here, never imported by response.py (headline independence is
itself pinned by a source scan).
"""
import math

import networkx as nx
import numpy as np
import pytest
from scipy import sparse

from bh_graph import response as R
from bh_graph.formation import j2_torus_coords, j2_torus_graph


def _path(n):
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from((i, i + 1) for i in range(n - 1))
    return g


def _j2(L):
    return j2_torus_graph(L), list(range(2 * L * L)), j2_torus_coords(L)


# 0A ----------------------------------------------------------------------

def test_0a_kernel_zero_is_identity():
    for g, order in [(_path(7), list(range(7))), (_j2(3)[0], list(range(18)))]:
        adj = nx.to_numpy_array(g, nodelist=order)
        assert R.is_identity_ok(R.kernel_dense(adj, 0.0))
        assert R.is_identity_ok(R.kernel_dense(adj, 0.0, j=2.5))


def test_0a_semigroup_and_unitarity():
    g, order, _ = _j2(3)
    adj = nx.to_numpy_array(g, nodelist=order)
    k1 = R.kernel_dense(adj, 0.7)
    k2 = R.kernel_dense(adj, 1.3)
    k12 = R.kernel_dense(adj, 2.0)
    assert R.is_semigroup_ok(k1, k2, k12, atol=1e-12)
    assert R.is_unitary_ok(k1, atol=1e-12)
    assert R.is_unitary_ok(k12, atol=1e-12)


def test_0a_krylov_column_matches_dense():
    g, order, _ = _j2(3)
    adj = nx.to_numpy_array(g, nodelist=order)
    ts = np.arange(0.0, 2.01, 0.1)
    for u in (0, 5, 17):
        col = R.kernel_column(g, order, u, ts)
        for k, t in enumerate(ts):
            kd = R.kernel_dense(adj, t)[:, order.index(u)]
            assert np.abs(col[k] - kd).max() < 1e-9, (u, t)
    # norms preserved (unitary to tol)
    assert np.abs(np.linalg.norm(col, axis=1) - 1.0).max() < 1e-9


def test_0a_evolve_matches_ballistic():
    from bh_graph.ballistic import evolve_fixed, hamiltonian

    g, order, _ = _j2(4)
    h = hamiltonian(g, order=order)
    rng = np.random.default_rng(0)
    psi0 = rng.standard_normal(len(order)) + 1j * rng.standard_normal(len(order))
    psi0 /= np.linalg.norm(psi0)
    a = R.evolve(psi0, h, 0.05, 40)["psi"]
    b = evolve_fixed(psi0, h, 0.05, 40)["psi"]
    assert np.abs(a - b).max() < 1e-9


def test_0a_evolve_step_edge_cases():
    # n_steps = 0/1 edge cases vs dense (campaign spec cell needs n_steps=1).
    g, order, _ = _j2(3)
    adj = nx.to_numpy_array(g, nodelist=order)
    h = R.hamiltonian(g, order)
    rng = np.random.default_rng(9)
    psi0 = rng.standard_normal(len(order)) + 1j * rng.standard_normal(len(order))
    psi0 /= np.linalg.norm(psi0)
    r0 = R.evolve(psi0, h, 0.3, 0)["psi"]
    assert r0.shape == (1, len(order)) and np.abs(r0[0] - psi0).max() == 0.0
    r1 = R.evolve(psi0, h, 0.3, 1)["psi"]
    assert r1.shape == (2, len(order))
    assert np.abs(r1[1] - R.kernel_dense(adj, 0.3) @ psi0).max() < 1e-9
    c1 = R.kernel_column(g, order, order[3], np.array([0.0, 0.3]))
    assert c1.shape == (2, len(order))
    assert np.abs(c1[1] - R.kernel_dense(adj, 0.3)[:, 3]).max() < 1e-9


# 0B ----------------------------------------------------------------------

def test_0b_spectral_matches_dense():
    g, order, _ = _j2(3)
    adj = nx.to_numpy_array(g, nodelist=order)
    w, v = R.eigh_adjacency(adj)
    for t in (0.0, 0.4, 1.7):
        assert np.abs(R.kernel_matrix_spectral(w, v, t) - R.kernel_dense(adj, t)).max() < 1e-9
    for iu, iv in ((0, 0), (2, 9), (17, 4)):
        s = R.kernel_spectral(w, v, iu, iv, 0.9)
        assert abs(s - R.kernel_dense(adj, 0.9)[iv, iu]) < 1e-12


def test_0b_j2_spectrum_anatomy_and_bloch_count():
    from bh_graph.continuum import j2_predicted_zero_count

    g, order, _ = _j2(4)
    adj = nx.to_numpy_array(g, nodelist=order)
    w, _ = R.eigh_adjacency(adj)
    an = R.spectrum_anatomy(w)
    assert an["n"] == 32
    assert abs(an["lo"] + 8.0) < 1e-9 and abs(an["hi"] - 8.0) < 1e-9
    assert an["n_flat"] == 22  # L^2 flat + 6 touching (exact integer pin)
    assert an["n_flat"] == j2_predicted_zero_count(4)  # EM-0 read-only count


# 0C ----------------------------------------------------------------------

def test_0c_covariance_dense_and_pushforward():
    from bh_graph.potential import pushforward as pot_push
    from bh_graph.potential import reflectx_perm, rot90_perm, translate_perm

    L = 4
    g, order, _ = _j2(L)
    adj = nx.to_numpy_array(g, nodelist=order)
    k = R.kernel_dense(adj, 1.1)
    perms = [translate_perm(L, 1, 2), rot90_perm(L), reflectx_perm(L)]
    for p in perms:
        for u, v in ((0, 0), (3, 11), (7, 30)):
            assert R.is_covariant_ok(R.kernel_covariance_dev(k, p, order, u, v),
                                     atol=1e-9)
    rng = np.random.default_rng(1)
    psi = rng.standard_normal(len(order)) + 1j * rng.standard_normal(len(order))
    for p in perms:
        assert np.abs(R.pushforward(psi, p, order) - pot_push(psi, p, order)).max() == 0.0


def test_0c_trace_covariance_krylov():
    from bh_graph.potential import translate_perm

    L = 4
    g, order, _ = _j2(L)
    p = translate_perm(L, 2, 1)
    ts = np.arange(0.0, 3.01, 0.1)
    u, v = 5, 20
    cu = R.kernel_column(g, order, u, ts)
    cg = R.kernel_column(g, order, p[u], ts)
    assert R.is_covariant_ok(R.trace_covariance_dev(cu, cg, order, v, p), atol=1e-9)


# 0D ----------------------------------------------------------------------

def test_0d_quadrature_matrix_exact():
    g, order, _ = _j2(3)
    adj = nx.to_numpy_array(g, nodelist=order)
    k = R.kernel_dense(adj, 0.9)
    iu, iv = 2, 11
    kcal = R.quadrature_matrix(k[iv, iu])
    for dr0, ds0 in ((0.3, 0.0), (0.0, -0.5), (0.3, -0.5)):
        got = R.apply_quadrature(kcal, dr0, ds0)
        want = k[iv, iu] * complex(dr0, ds0)
        assert np.abs(got - np.array([want.real, want.imag])).max() < 1e-12


# 0E-0H -------------------------------------------------------------------

def test_0eh_decomp_identity_random():
    rng = np.random.default_rng(2)
    g, order, _ = _j2(3)
    eu, ev = R.edge_index_arrays(g, order)
    for _ in range(5):
        p0 = rng.standard_normal(len(order)) + 1j * rng.standard_normal(len(order))
        dp = 1e-3 * (rng.standard_normal(len(order)) + 1j * rng.standard_normal(len(order)))
        assert R.is_decomp_ok(R.delta_observables(p0, dp, eu, ev))


def test_0eh_bond_conventions_match_banked():
    from bh_graph.backreaction import bond_B as br_B
    from bh_graph.potential import bond_current

    rng = np.random.default_rng(3)
    g, order, _ = _j2(3)
    eu, ev = R.edge_index_arrays(g, order)
    psi = rng.standard_normal(len(order)) + 1j * rng.standard_normal(len(order))
    b = R.bond_B(psi, eu, ev)
    jj = R.bond_J(psi, eu, ev)
    for e in range(0, len(eu), 7):
        assert abs(b[e] - br_B(psi, int(eu[e]), int(ev[e]))) < 1e-12
        assert abs(jj[e] - bond_current(psi[eu[e]], psi[ev[e]])) < 1e-12


def test_0g_bipartite_B_blindness_point_impulse():
    # Bipartite B-blindness: real/single-phase impulses keep B == 0 exactly
    # (all bonds, all t) while J carries the response. J2 L=4 (even torus
    # is bipartite; odd-L wraps break it) + path-9.
    for g, order, u in [(_j2(4)[0], list(range(32)), 9),
                        (_path(9), list(range(9)), 4)]:
        h = R.hamiltonian(g, order)
        eu, ev = R.edge_index_arrays(g, order)
        for eps in (1.0, 0.01, 1.0j, np.exp(0.7j)):
            rec = R.evolve(R.point_source(len(order), u, eps), h, 0.05, 60)["psi"]
            bmax = max(float(np.abs(R.bond_B(row, eu, ev)).max()) for row in rec)
            jmax = max(float(np.abs(R.bond_J(row, eu, ev)).max()) for row in rec)
            assert bmax < 1e-12, (eps, bmax)
            assert jmax > 1e-6, (eps, jmax)
    # ...but a phase-STRUCTURED source (relative phase across nodes) has B != 0.
    g, order, _ = _j2(4)
    h = R.hamiltonian(g, order)
    eu, ev = R.edge_index_arrays(g, order)
    d0 = R.point_source(len(order), 0, 1.0) + R.point_source(len(order), 1, 1.0j)
    rec = R.evolve(d0, h, 0.05, 60)["psi"]
    assert max(float(np.abs(R.bond_B(row, eu, ev)).max()) for row in rec) > 1e-6
    # Sharp edge: adjacent-node 0/pi/2 dipole (opposite sublattices) is STILL
    # chiral-real hence B-blind; same-sublattice relative phase breaks it.
    # Nodes 0=(0,0,0) and 8=(1,0,0) are adjacent (opposite parity).
    d0 = R.point_source(len(order), 0, 1.0) + R.point_source(len(order), 8, 1.0j)
    rec = R.evolve(d0, h, 0.05, 60)["psi"]
    assert max(float(np.abs(R.bond_B(row, eu, ev)).max()) for row in rec) < 1e-12
    assert max(float(np.abs(R.bond_J(row, eu, ev)).max()) for row in rec) > 1e-6
    # Sheet dipole: B is LOCALIZED (frozen anti part lives on the source cell;
    # the propagating symmetric part is single-phase hence chiral-blind).
    d0 = R.point_source(len(order), 0, 1.0) + R.point_source(len(order), 1, 1.0j)
    rec = R.evolve(d0, h, 0.05, 60)["psi"]
    src_pair = {0, 1}
    far = [e for e in range(len(eu)) if int(eu[e]) not in src_pair
           and int(ev[e]) not in src_pair]
    near = [e for e in range(len(eu)) if e not in far]
    assert max(float(np.abs(R.bond_B(row, eu, ev)[far]).max()) for row in rec) < 1e-12
    assert max(float(np.abs(R.bond_B(row, eu, ev)[near]).max()) for row in rec) > 1e-6
    # Sharp split (Amendment-3): single-sublattice real regions are blind,
    # two-sublattice real regions are not. Cell {(0,0,0),(0,0,1)} is one
    # sublattice; edge {0, 8} spans both.
    g4, order4, c34 = _j2(4)
    h4 = R.hamiltonian(g4, order4)
    eu4, ev4 = R.edge_index_arrays(g4, order4)
    m_cell = R.region_mask("cell", g4, order4, 0, c34, 4)
    rec_cell = R.evolve(R.region_source(m_cell, 1.0), h4, 0.05, 60)["psi"]
    assert max(float(np.abs(R.bond_B(row, eu4, ev4)).max()) for row in rec_cell) < 1e-12
    e_edge = (0, 8)
    assert g4.has_edge(*e_edge)
    m_edge = R.region_mask("edge", g4, order4, e_edge, c34, 4)
    rec_edge = R.evolve(R.region_source(m_edge, 1.0), h4, 0.05, 60)["psi"]
    assert max(float(np.abs(R.bond_B(row, eu4, ev4)).max()) for row in rec_edge) > 1e-6


# 0I ----------------------------------------------------------------------

def test_0i_chi_predicts_first_order():
    L = 3
    g, order, _ = _j2(L)
    eu, ev = R.edge_index_arrays(g, order)
    adj = nx.to_numpy_array(g, nodelist=order)
    rng = np.random.default_rng(4)
    p00 = rng.standard_normal(len(order)) + 1j * rng.standard_normal(len(order))
    p00 /= np.linalg.norm(p00)
    t, u = 0.7, 4
    k = R.kernel_dense(adj, t)
    p0t = k @ p00
    for eps in (1e-3, 1e-3j):
        dp0 = R.point_source(len(order), u, eps)
        dpt = k @ dp0
        resp = R.delta_observables(p0t, dpt, eu, ev)
        dr0, ds0 = complex(eps).real, complex(eps).imag
        for v in (0, 9, 17):
            chi = R.chi_rho(p0t[v], k[v, u])
            assert abs(R.apply_chi(chi, dr0, ds0) - resp["d_rho1"][v]) < 1e-12
        for e in (0, 25, 60):
            vv, ww = int(eu[e]), int(ev[e])
            ch = R.chi_bond(p0t[vv], p0t[ww], k[vv, u], k[ww, u])
            assert abs(R.apply_chi(ch["chi_B"], dr0, ds0) - resp["d_B1"][e]) < 1e-12
            assert abs(R.apply_chi(ch["chi_J"], dr0, ds0) - resp["d_J1"][e]) < 1e-12


# 0J ----------------------------------------------------------------------

def test_0j_zero_background_chi_vanishes_quadratic_leads():
    g, order, _ = _j2(3)
    eu, ev = R.edge_index_arrays(g, order)
    adj = nx.to_numpy_array(g, nodelist=order)
    k = R.kernel_dense(adj, 0.6)
    u = 3
    assert R.is_chi_zero_ok(R.chi_rho(0.0j, k[5, u]))
    ch = R.chi_bond(0.0j, 0.0j, k[1, u], k[2, u])
    assert R.is_chi_zero_ok(ch["chi_B"]) and R.is_chi_zero_ok(ch["chi_J"])
    p0 = np.zeros(len(order), dtype=np.complex128)
    eps_grid = np.array([3e-5, 1e-4, 3e-4, 1e-3, 3e-3])
    norms = []
    for e in eps_grid:
        dpt = k @ R.point_source(len(order), u, e)
        resp = R.delta_observables(p0, dpt, eu, ev)
        assert np.abs(resp["d_rho1"]).max() == 0.0
        norms.append(float(np.linalg.norm(resp["d_rho"])))
    slope, _ = np.polyfit(np.log(eps_grid), np.log(norms), 1)
    assert abs(slope - 2.0) < 0.01, slope


# 0F ----------------------------------------------------------------------

def test_0f_nonzero_background_linear_scaling():
    g, order, c3 = _j2(4)
    eu, ev = R.edge_index_arrays(g, order)
    adj = nx.to_numpy_array(g, nodelist=order)
    k = R.kernel_dense(adj, 1.0)
    p00 = R.background_state("BG+", g, order, c3)
    p0t = k @ p00
    u = 9
    eps_grid = np.array([3e-5, 1e-4, 3e-4, 1e-3, 3e-3])
    norms = []
    for e in eps_grid:
        dpt = k @ R.point_source(len(order), u, e)
        norms.append(float(np.linalg.norm(R.delta_observables(p0t, dpt, eu, ev)["d_rho"])))
    slope, _ = np.polyfit(np.log(eps_grid), np.log(norms), 1)
    assert abs(slope - 1.0) < 0.05, slope


# 0K ----------------------------------------------------------------------

def test_0k_battery_eigenvalues_and_stationarity():
    L = 4
    g, order, c3 = _j2(L)
    h = R.hamiltonian(g, order).toarray()
    pars = {v: (x + y) & 1 for v, (x, y, _) in c3.items()}
    bgs = {"BG+": (R.background_state("BG+", g, order, c3), -8.0),
           "BGpi": (R.background_state("BGpi", g, order, c3), 8.0),
           "BG-": (R.background_state("BG-", g, order, c3), 0.0),
           "BGM": (R.background_state("BGM", g, order, c3, L), 0.0)}
    for name, (bg, e) in bgs.items():
        assert R.is_normalized_ok(bg), name
        assert np.linalg.norm(h @ bg - e * bg) < 1e-9, (name, e)
    bg0 = R.background_state("BG0", g, order, c3)
    assert float(np.linalg.norm(bg0)) == 0.0
    assert pars is not None
    # stationarity up to global phase under Krylov evolution
    hs = R.hamiltonian(g, order)
    for name, (bg, _) in bgs.items():
        rows = R.evolve(bg, hs, 0.05, 20)["psi"]
        assert R.is_stationary_ok(rows, atol=1e-9), name
    # BGM is mixed-sector
    partner = R.sheet_partner(order, c3)
    wts = R.sector_weights(bgs["BGM"][0], partner)
    assert abs(wts["w_plus"] - 0.5) < 1e-12
    assert abs(wts["w_minus"] - 0.5) < 1e-12


def test_0k_touching_momentum_selection():
    assert R.touching_momentum(28) is not None
    assert R.touching_momentum(4) is not None
    kx, ky = R.touching_momentum(28)
    assert abs(math.cos(kx) + math.cos(ky)) < 1e-9


# 0L ----------------------------------------------------------------------

def test_0l_chi_proportional_to_background_amplitude():
    g, order, c3 = _j2(3)
    adj = nx.to_numpy_array(g, nodelist=order)
    k = R.kernel_dense(adj, 0.5)
    hat = R.background_state("BG+", g, order, c3)
    p0t_hat = k @ hat
    u, v = 1, 8
    ref_r = R.chi_rho(p0t_hat[v], k[v, u])
    ref_b = R.chi_bond(p0t_hat[2], p0t_hat[6], k[2, u], k[6, u])["chi_B"]
    for a in (0.01, 3.7, 100.0):
        p0t = k @ R.scaled_background(hat, a)
        assert np.abs(R.chi_rho(p0t[v], k[v, u]) - a * ref_r).max() < 1e-9
        got = R.chi_bond(p0t[2], p0t[6], k[2, u], k[6, u])["chi_B"]
        assert np.abs(got - a * ref_b).max() < 1e-9


# 0N-0O -------------------------------------------------------------------

def test_0no_phase_amplitude_kicks():
    g, order, c3 = _j2(3)
    p0 = R.background_state("BG+", g, order, c3)
    iu = 7
    # phase kick: linear matches exact to O(eps^2)
    for eps in (1e-2, 1e-3):
        pk = R.phase_kick(p0, iu, eps)
        assert np.linalg.norm(pk["dpsi_exact"] - pk["dpsi_linear"]) < eps * eps
    # amplitude kick: exact == linear (single-node scaling)
    ak = R.amplitude_kick(p0, iu, 0.05)
    assert np.abs(ak["dpsi_exact"] - ak["dpsi_linear"]).max() == 0.0
    assert abs(ak["dpsi_exact"][iu] - 0.05 * p0[iu]) < 1e-12


# 0P ----------------------------------------------------------------------

def test_0p_region_mask_sizes():
    L = 6
    g, order, c3 = _j2(L)
    center = (2 * L + 3) * 2 + 0
    assert int(R.region_mask("node", g, order, center, c3, L).sum()) == 1
    e = next(iter(g.edges(center)))
    assert int(R.region_mask("edge", g, order, e, c3, L).sum()) == 2
    assert int(R.region_mask("cell", g, order, center, c3, L).sum()) == 2
    assert int(R.region_mask("ball1", g, order, center, c3, L).sum()) == 9
    assert int(R.region_mask("patch", g, order, center, c3, L).sum()) == 18
    d = R.region_source(R.region_mask("cell", g, order, center, c3, L), 0.5)
    assert abs(float(np.linalg.norm(d)) - 0.5 * math.sqrt(2.0)) < 1e-12
    dn = R.region_source(R.region_mask("cell", g, order, center, c3, L), 0.5,
                         normalize=True)
    assert R.is_normalized_ok(dn)


# 0Q-0R -------------------------------------------------------------------

def test_0qr_arrival_velocity_windows():
    ts = np.linspace(0.0, 10.0, 101)
    tr = np.concatenate([np.zeros(40), np.linspace(0.0, 1.0, 61)])
    assert R.arrival_time(tr, ts, 0.5) == pytest.approx(7.0, abs=0.11)
    assert R.arrival_time(tr, ts, 2.0) is None
    arr = {r: 1.0 + 0.25 * r for r in range(1, 7)}
    fv = R.front_velocity(arr, list(range(1, 7)))
    assert abs(fv["v"] - 4.0) < 1e-9 and abs(fv["r2"] - 1.0) < 1e-12
    w = R.time_windows(28, 6.0)
    assert abs(w["t_front"] - 0.75) < 1e-12 and abs(w["t_wrap"] - 2.75) < 1e-12
    assert R.arrival_window(2.0, 28) == (2.0 / 12.0, 26.0 / 8.0)
    assert R.arrival_window(27.0, 28) is None
    assert R.is_front_velocity_ok(7.9) and not R.is_front_velocity_ok(0.1)
    # cross-check vs POT-1 arrival fit
    from bh_graph.driven import arrival_velocity as pot_av

    assert abs(pot_av(arr, list(range(1, 7)))["v"] - 4.0) < 1e-9


# 0S-0U -------------------------------------------------------------------

def test_0stu_peak_integrated_rays():
    ts = np.linspace(0.0, 10.0, 101)
    tr = np.sin(ts) ** 2
    pk = R.peak_in_window(tr, ts, 1.0, 2.0)
    assert abs(pk["Rmax"] - 1.0) < 0.01
    assert R.peak_in_window(tr, ts, 20.0, 30.0) is None
    it = R.integrated_in_window(np.ones_like(ts), ts, 2.0, 5.0)
    assert abs(it["signed"] - 3.0) < 0.11 and abs(it["abs"] - 3.0) < 0.11
    assert R.integrated_in_window(np.ones_like(ts), ts, 20.0, 30.0) is None
    assert R.quotient_ray((7, 14), (1, 0), 3, 28) == [(7, 14), (8, 14), (9, 14), (10, 14)]
    _, order, c3 = _j2(4)
    mp = R.cells_to_indices([(0, 0), (3, 3)], c3, order)
    assert all(len(v) == 2 for v in mp.values())


# 0V ----------------------------------------------------------------------

def test_0v_sectors_vs_malus_and_frozen_anti():
    from bh_graph import malus

    L = 4
    g, order, c3 = _j2(L)
    partner = R.sheet_partner(order, c3)
    rng = np.random.default_rng(5)
    psi = rng.standard_normal(len(order)) + 1j * rng.standard_normal(len(order))
    psi /= np.linalg.norm(psi)
    pr = R.sheet_project(psi, partner)
    assert np.abs(pr["plus"] + pr["minus"] - psi).max() < 1e-12
    wts = R.sector_weights(psi, partner)
    assert R.is_sector_accounting_ok(wts["w_plus"], wts["w_minus"])
    mpr = malus.sheet_projectors(order, c3)
    mw = malus.sheet_weights(psi, mpr)
    assert abs(mw["w_sym"] - wts["w_plus"]) < 1e-12
    assert abs(mw["w_anti"] - wts["w_minus"]) < 1e-12
    # anti sector frozen under own evolver; sym of symmetric is identity
    hs = R.hamiltonian(g, order)
    rows = R.evolve(pr["minus"], hs, 0.05, 30)["psi"]
    assert float(np.abs(rows - rows[0][None, :]).max()) < 1e-9
    assert R.is_stationary_ok(R.evolve(pr["minus"], hs, 0.05, 30)["psi"], atol=1e-9)


# 0W ----------------------------------------------------------------------

def test_0w_quotient_lift_intertwining_and_bond_lift():
    from bh_graph import malus

    L = 4
    g, order, c3 = _j2(L)
    u, cells = R.quotient_lift_matrix(order, c3)
    um, _ = malus.symmetric_embedding(order, c3)
    assert np.abs(u - um).max() == 0.0
    hq = R.quotient_hamiltonian(cells, L)
    hqm = malus.square_hamiltonian(cells, (L, L))
    assert np.abs(hq - hqm).max() == 0.0
    # U(t) L = L U_Q(t) under the independent evolver
    rng = np.random.default_rng(6)
    phi0 = rng.standard_normal(len(cells)) + 1j * rng.standard_normal(len(cells))
    phi0 /= np.linalg.norm(phi0)
    hf = R.hamiltonian(g, order)
    hq_csr = sparse.csr_matrix(hq)
    full = R.evolve(R.lift_state(phi0, u), hf, 0.05, 40)["psi"]
    quot = R.evolve(phi0, hq_csr, 0.05, 40)["psi"]
    assert float(np.abs(full - quot @ u.T).max()) < 1e-8
    # symmetric bond lift: every micro-edge B = B^Q / 2
    eu, ev = R.edge_index_arrays(g, order)
    psi = R.lift_state(phi0, u)
    bm = R.bond_B(psi, eu, ev)
    cpos = {c: k for k, c in enumerate(cells)}
    for e in range(len(eu)):
        a, b = order[int(eu[e])], order[int(ev[e])]
        ca, cb = (c3[a][0], c3[a][1]), (c3[b][0], c3[b][1])
        bq = float((np.conj(phi0[cpos[ca]]) * phi0[cpos[cb]]).real)
        assert abs(bm[e] - bq / 2.0) < 1e-12, e


# 0X ----------------------------------------------------------------------

def test_0x_green_static_matches_driven_solve():
    from bh_graph.driven import path_graph, steady_predict

    n = 15
    g = path_graph(n)
    order = list(range(n))
    h = R.hamiltonian(g, order)
    pin, s, w = [0], np.array([1.0]), -2.5
    pred = steady_predict(h.tocsc(), pin, s, w)
    got = R.green_static_approx(h, pin, s, w, dt=0.05, T=120.0, eta=0.05)["phi"]
    den = float(np.linalg.norm(pred))
    assert float(np.linalg.norm(got - pred)) / den < 0.15


# 0Y ----------------------------------------------------------------------

def test_0y_switch_deviation_and_superposition():
    g = _path(7)
    order = list(range(7))
    h = R.hamiltonian(g, order)
    rng = np.random.default_rng(7)
    phi0 = rng.standard_normal(7) + 1j * rng.standard_normal(7)
    phi0 /= np.linalg.norm(phi0)
    rec = R.switch_evolution(phi0, h, 0.05, 20)
    dev = R.switch_deviation(rec["psi"], phi0, -2.5, 0.05)
    assert float(np.abs(dev[0]).max()) == 0.0
    # kernel completeness: direct == column superposition
    ts = np.arange(21) * 0.05
    cols = [R.kernel_column(g, order, u, ts) for u in order]
    assert float(np.abs(R.superpose_columns(cols, phi0) - rec["psi"]).max()) < 1e-9


# 0Z ----------------------------------------------------------------------

def test_0z_linearity_and_cross_terms():
    rng = np.random.default_rng(8)
    g, order, _ = _j2(3)
    eu, ev = R.edge_index_arrays(g, order)
    n = len(order)
    p0 = rng.standard_normal(n) + 1j * rng.standard_normal(n)
    d1 = 1e-3 * (rng.standard_normal(n) + 1j * rng.standard_normal(n))
    d2 = 1e-3 * (rng.standard_normal(n) + 1j * rng.standard_normal(n))
    assert R.field_linearity_dev(d1, d2, d1 + d2) < 1e-12
    x = R.quadratic_cross_terms(d1, d2, eu, ev)
    full = R.delta_observables(p0, d1 + d2, eu, ev)
    r1 = R.delta_observables(p0, d1, eu, ev)
    r2 = R.delta_observables(p0, d2, eu, ev)
    assert np.abs(full["d_rho"] - r1["d_rho"] - r2["d_rho"] - x["x_rho"]).max() < 1e-12
    assert np.abs(full["d_B"] - r1["d_B"] - r2["d_B"] - x["x_B"]).max() < 1e-12
    assert np.abs(full["d_J"] - r1["d_J"] - r2["d_J"] - x["x_J"]).max() < 1e-12


# 0AA ---------------------------------------------------------------------

def test_0aa_ledger_record():
    ev = R.ledger_event("node@u", "point-R", "BG0", 1.0, "dB", "qshell", 4.0,
                        0.55, 1e-4, 0.6, 2e-5, 1e-6, 1e-6, 0.33, 3.0, False)
    assert ev["arrival"] == 0.55 and ev["wrap_flag"] is False
    ev2 = R.ledger_event("cell", "point-I", "BG+", 1e-3, "dJ", "qray", 9.0,
                         None, None, None, None, None, 1e-6, None, None, True)
    assert ev2["arrival"] is None and ev2["t_lo"] is None and ev2["wrap_flag"] is True


# independence --------------------------------------------------------------

def test_headline_independence_no_bh_graph_imports():
    import pathlib
    import re

    src = pathlib.Path(R.__file__).read_text()
    assert re.search(r"^\s*(from|import)\s+bh_graph", src, re.MULTILINE) is None
