"""DIM-3-0 Stages A/B: J3 construction + spectrum exact pins (DIM3-PREREG).

Stage A (pre-data derivation): J3 = Z^3 ⋊ Z2 with transposition action,
12 inverse-closed generators, degree 12, exact cubic quotient (mult 4),
bipartite, [H,S] = 0, H·P_anti = 0, H·U = U·H_Q with H_Q = -2J·A_cubic.
Stage B (derived): Bloch bands/velocities/Hessian/maxima, Bloch-vs-brute
agreement, vacuum spectral census. All exact (no tolerance except
floating-point roundoff and inherited solver tolerances).
"""
import itertools
import math

import networkx as nx
import numpy as np

from bh_graph import dim3
from bh_graph.dim3 import SWAP_XY, SWAP_XZ, SWAP_YZ


def test_j3_gens_inverse_closed():
    assert len(dim3.j3_gens()) == 12
    for swap in (SWAP_XY, SWAP_YZ, SWAP_XZ):
        assert dim3.is_gens_inverse_closed_ok(swap=swap)


def test_j3_ball_census():
    # Exact ball census (deterministic construction): N/E pinned.
    for R, N, E in ((0, 1, 0), (1, 13, 12), (2, 50, 144), (3, 126, 456),
                    (4, 258, 1056), (5, 462, 2040), (6, 754, 3504)):
        g = dim3.build_j3_ball(R)
        assert g.number_of_nodes() == N, R
        assert g.number_of_edges() == E, R
        assert nx.is_connected(g)
        assert max((d for _, d in g.degree()), default=0) <= 12
        assert g.degree((0, 0, 0, 0)) == (0 if R == 0 else 12)
    try:
        dim3.build_j3_ball(-1)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_j3_torus_regular_connected():
    for L in (3, 4, 5):
        g = dim3.j3_torus_graph(L)
        assert g.number_of_nodes() == 2 * L ** 3
        assert g.number_of_edges() == 12 * L ** 3
        assert nx.is_connected(g)
        assert sorted(set(d for _, d in g.degree())) == [12]
    g4 = dim3.j3_torus_graph(4)
    assert g4.number_of_nodes() == 128 and g4.number_of_edges() == 768


def test_j3_quotient_is_cubic():
    # Quotient (x,y,z,b)->(x,y,z) IS the cubic torus: every coarse edge
    # axis-adjacent, micro-multiplicity exactly 4 per coarse edge.
    for L in (4, 6):
        g = dim3.j3_torus_graph(L)
        c4 = dim3.j3_torus_coords(L)
        cells, q, mult = dim3.quotient_cells_edges(g, dim3.j3_cell_of(c4))
        assert q.number_of_nodes() == L ** 3
        assert q.number_of_edges() == 3 * L ** 3
        assert all(sorted(v) == [0, 1] for v in
                   ([c4[n][3] for n in m] for m in cells.values()))
        assert dim3.quotient_is_cubic_ok(q, L)
        assert sorted(set(mult.values())) == [4]
    # Torus L=4 quotient shells (wrap-included, exact).
    g = dim3.j3_torus_graph(4)
    c4 = dim3.j3_torus_coords(4)
    _, q, _ = dim3.quotient_cells_edges(g, dim3.j3_cell_of(c4))
    dq = dict(nx.single_source_shortest_path_length(q, (0, 0, 0)))
    shq = [sum(1 for n in dq if dq[n] == r) for r in range(7)]
    assert shq == [1, 6, 15, 20, 15, 6, 1]
    # Open-cubic shells (L=8 torus, r <= 3 wrap-free): 4r^2+2.
    g8 = dim3.j3_torus_graph(8)
    c8 = dim3.j3_torus_coords(8)
    _, q8, _ = dim3.quotient_cells_edges(g8, dim3.j3_cell_of(c8))
    d8 = dict(nx.single_source_shortest_path_length(q8, (0, 0, 0)))
    assert [sum(1 for n in d8 if d8[n] == r) for r in range(4)] == [1, 6, 18, 38]


def test_j3_transposition_family_isomorphic():
    # The 3 transpositions are cubic-conjugate: exact graph isomorphism
    # via the preregistered axis permutation (family = 1 member up to sym).
    L = 4
    g_xy = dim3.j3_torus_graph(L, SWAP_XY)
    for swap in (SWAP_YZ, SWAP_XZ):
        g_s = dim3.j3_torus_graph(L, swap)
        perm = dim3.cubic_transposition_perm(L, swap)
        img = {(perm[u], perm[v]) if perm[u] < perm[v] else (perm[v], perm[u])
               for u, v in g_s.edges()}
        ref = {(u, v) if u < v else (v, u) for u, v in g_xy.edges()}
        assert img == ref, swap


def test_j3_micro_vs_quotient_uv():
    # Micro shell law differs from the quotient (UV structure invisible
    # to the quotient), same pattern as J2 (8r vs 4r).
    g = dim3.build_j3_ball(6)
    shells, _, _ = dim3.shells_cuts_vols(g, (0, 0, 0, 0), 6)
    assert shells == [1, 12, 37, 76, 132, 204, 292]


def test_j3_bipartite():
    # Even-L tori are bipartite (odd L wraps odd cycles, same as J2/square).
    for L in (4, 6):
        g = dim3.j3_torus_graph(L)
        c4 = dim3.j3_torus_coords(L)
        assert dim3.is_bipartition_ok(g, dim3.bipartition_j3(c4))
        assert nx.is_bipartite(g)


def test_j3_sheet_sector_mechanism():
    # [H,S] = 0, H·P_anti = 0, H·U = U·H_Q exactly (Stage-A M4 pins).
    from bh_graph.ballistic import hamiltonian, node_order

    L = 4
    g = dim3.j3_torus_graph(L)
    order = node_order(g)
    c4 = dim3.j3_torus_coords(L)
    h = hamiltonian(g, j=1.0, order=order)
    s = dim3.sheet_swap_matrix(order, c4)
    assert dim3.is_involution_ok(s)
    assert dim3.commutator_norm(h, s) == 0.0
    pr = dim3.sheet_projectors(order, c4)
    assert dim3.anti_dead_norm(h, pr["P_anti"]) == 0.0
    u, cells = dim3.symmetric_embedding(order, c4)
    hq = dim3.cubic_hamiltonian(cells, (L, L, L))
    assert dim3.intertwining_norm(h, u, hq) == 0.0
    assert dim3.time_evolution_intertwining_err(h, u, hq) < 1e-12
    # Weights account exactly on a random state.
    rng = np.random.default_rng(0)
    psi = rng.standard_normal(len(order)) + 1j * rng.standard_normal(len(order))
    psi = psi / np.linalg.norm(psi)
    w = dim3.sheet_weights(psi, pr)
    assert dim3.is_sheet_accounting_ok(w["w_sym"], w["w_anti"])


def test_j3_bloch_values():
    # Locked dispersion values (derived, pinned).
    e, f = dim3.j3_bloch_bands(0.0, 0.0, 0.0)
    assert (e, f) == (-12.0, 0.0)
    e, f = dim3.j3_bloch_bands(math.pi, math.pi, math.pi)
    assert (abs(e - 12.0) < 1e-12) and f == 0.0
    v = dim3.j3_group_velocity(math.pi / 2, math.pi / 2, math.pi / 2)
    assert np.allclose(v, [4.0, 4.0, 4.0])
    m = dim3.j3_hessian(0.0, 0.0, 0.0)
    assert np.allclose(m, 4.0 * np.eye(3))
    mx = dim3.j3_max_velocities()
    assert mx["axial"] == 4.0
    assert abs(mx["euclidean"] - 4.0 * math.sqrt(3.0)) < 1e-12
    assert mx["manhattan"] == 12.0
    # Γ-point isotropy exact; touching counts exact.
    iso = dim3.hessian_isotropy(m)
    assert iso["anisotropy"] == 0.0
    assert dim3.j3_touching_count(4) == 20
    assert dim3.j3_predicted_zero_count(4) == 84
    # Taylor: E0=-12, v=0, Minv=4I, cubic 0, quartic -(1/6).
    c = dim3.taylor_coeffs((0.0, 0.0, 0.0))
    assert c["E0"] == -12.0
    assert np.allclose(c["v"], 0.0)
    assert np.allclose(c["Minv"], 4.0 * np.eye(3))
    assert np.allclose(c["cubic"], 0.0)
    assert np.allclose(c["quartic"], [-1.0 / 6.0] * 3)


def test_j3_bloch_vs_brute():
    # Inherited bar (continuum.is_bloch_ok): dev < 1e-9 + exact zero count.
    for L in (4, 6):
        assert dim3.is_bloch_ok(L), L
    r = dim3.bloch_vs_exact(4)
    assert r["n_zero_exact"] == 84 == r["n_zero_predicted"]


def test_j3_vacuum_spectral_census():
    # VPLUS E=-12, VPI E=+12 (even L), VMINUS E=0; residuals exact.
    cen = dim3.spectral_census_j3(4)
    assert abs(cen["VPLUS"]["energy"] + 12.0) < 1e-9
    assert abs(cen["VPI"]["energy"] - 12.0) < 1e-9
    assert abs(cen["VMINUS"]["energy"]) < 1e-9
    for name in ("VPLUS", "VPI", "VMINUS"):
        assert cen[name]["residual"] < 1e-9, name


def test_j3_krylov_matches_dense():
    # Campaign instruments == dense spectral mathematics (L=4 cross-check).
    from bh_graph import obs0
    from bh_graph.ballistic import hamiltonian, node_order

    L = 4
    g = dim3.j3_torus_graph(L)
    order = node_order(g)
    h = hamiltonian(g, j=1.0, order=order)
    lrw = dim3.lrw_matrix(g, order)
    Ew, Vw, _ = obs0.hamiltonian_system(g, order)
    wl, Vl, _ = obs0.lsym_system(g, order)
    o, tj = 0, [1, 2, 3, 40, 100]
    ts_w = np.arange(0, 2.01, 0.05)
    ts_d = np.arange(0, 6.01, 0.25)
    pw_ref = obs0._target_traces_wave(Ew, Vw, o, tj, ts_w)
    pd_ref = obs0._target_traces_diff(wl, Vl, o, tj, ts_d)
    pw = dim3.krylov_wave_traces(h, o, tj, ts_w)
    pd = dim3.krylov_diff_traces(lrw, o, tj, ts_d)
    assert np.abs(pw - pw_ref).max() < 1e-6
    assert np.abs(pd - pd_ref).max() < 1e-6


def test_j3_cg_matches_direct():
    # CG statics == direct solve (same equation; 1e-8 bar as run_obs1).
    from bh_graph.ballistic import hamiltonian, node_order
    from bh_graph.driven import steady_predict
    from bh_graph.obs0r import omega_below_edge

    assert omega_below_edge(12) == -12.5
    L = 4
    g = dim3.j3_torus_graph(L)
    order = node_order(g)
    h = hamiltonian(g, j=1.0, order=order)
    om = omega_below_edge(12)
    phi_cg = dim3.static_phi_cg(h.tocsc(), 0, om)
    phi_di = steady_predict(h, [0], np.array([1.0]), om)
    assert np.abs(phi_cg - phi_di).max() < 1e-8


def test_j3_cubic_and_bilayer_controls():
    # C0 cubic torus: L^3 nodes, 6-regular, 3L^3 edges.
    g = dim3.cubic_torus_graph(4)
    assert g.number_of_nodes() == 64 and g.number_of_edges() == 192
    assert sorted(set(d for _, d in g.degree())) == [6]
    assert nx.is_connected(g)
    # R1 bilayer: decoupled sheets, BOTH sectors propagate (H_- != 0).
    from bh_graph.ballistic import hamiltonian, node_order

    b = dim3.bilayer_cubic_graph(4)
    c4 = dim3.bilayer_cubic_coords(4)
    assert dim3.is_decoupled_ok(b, c4)
    order = node_order(b)
    h = hamiltonian(b, j=1.0, order=order)
    pr = dim3.sheet_projectors(order, c4)
    assert dim3.commutator_norm(h, dim3.sheet_swap_matrix(order, c4)) == 0.0
    assert dim3.anti_dead_norm(h, pr["P_anti"]) == 0.5  # H_- = -A_cubic != 0


def test_j3_fit_exponent_synthetic():
    # fit_exponent recovers r^-1 and r^-2 laws on synthetic shells.
    p1 = {r: float(r) ** -1.0 for r in range(2, 11)}
    f = dim3.fit_exponent(p1, 2, 10)
    assert abs(f["alpha"] - 1.0) < 1e-9 and f["r2"] > 0.999 and f["n"] == 9
    p2 = {r: float(r) ** -2.0 for r in range(2, 11)}
    f = dim3.fit_exponent(p2, 2, 10)
    assert abs(f["alpha"] - 2.0) < 1e-9 and f["r2"] > 0.999
    assert dim3.fit_exponent({2: 1.0}, 2, 10)["n"] == 0


def test_j3_window_p_cubic_control():
    # window_p reads d=3 on the open cubic ball (control of the ruler).
    g = nx.Graph()
    rng = range(-18, 19)
    for x, y, z in itertools.product(rng, rng, rng):
        g.add_node((x, y, z))
    for x, y, z in g.nodes():
        for nb in ((x + 1, y, z), (x, y + 1, z), (x, y, z + 1)):
            if nb in g:
                g.add_edge((x, y, z), nb)
    _, _, vols = dim3.shells_cuts_vols(g, (0, 0, 0), 17)
    assert 2.85 < dim3.window_p(vols, 9, 16) < 3.05
