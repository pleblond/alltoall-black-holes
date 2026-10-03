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


def test_dim3_blind_firewall_audit():
    # The blind analyzer must never touch hidden geometry (import + token
    # scan, same firewall pattern as OBS-1 C3).
    import pathlib

    src = pathlib.Path("scripts/dim3_blind.py").read_text()
    for tok in ("dim3_reveal", "tag_graph", "j3_torus", "cubic_torus",
                "coords", "formation", "hidden", "seal", "quotient",
                "sheet", "symmetric_embedding"):
        assert tok not in src, tok
    tree = __import__("ast").parse(src)
    imported = set()
    for node in __import__("ast").walk(tree):
        if isinstance(node, __import__("ast").ImportFrom):
            imported.add(node.module or "")
        elif isinstance(node, __import__("ast").Import):
            imported.update(a.name for a in node.names)
    assert not ({"bh_graph.dim3_reveal", "bh_graph.dim3",
                 "dim3_campaign"} & imported)


def test_dim3_reveal_helpers_synthetic():
    # 3D reveal joins on synthetic exact-cubic data (no campaign data).
    from bh_graph import dim3_reveal as DR

    assert DR.torus_distance3((0, 0, 0), (7, 0, 0), 8) == 1.0
    assert abs(DR.torus_distance3((0, 0, 0), (4, 4, 4), 8)
               - math.sqrt(48.0)) < 1e-12
    L = 6
    nodes = list(range(8))
    coords = {i: (float(i % 2), float((i // 2) % 2), float(i // 4))
              for i in nodes}
    H = DR.hidden_quotient_matrix3(coords, nodes, L)
    assert np.allclose(H, H.T) and np.allclose(np.diag(H), 0.0)
    # Exact-distance charts pass in 3D.
    rep = DR.local_chart_report3(H, coords, nodes, float(L), k=4, d=3)
    assert rep["pass"] and rep["n"] == 8
    topo = DR.topology_report3([], coords, nodes, L, H)
    assert topo["n"] == 0 and not topo["pass"]
    assert DR.hidden_quotient_coords3("ex-N10-s0", 0) is None
    assert DR.hidden_sheets3("cb-L4", 4) is None
    c3 = DR.hidden_quotient_coords3("j3-L4", 4)
    assert len(c3) == 128 and c3[0] == (0.0, 0.0, 0.0)
    sh = DR.hidden_sheets3("j3-L4", 4)
    assert sh[0] == 0 and sh[1] == 1


def test_dim3_sector_preps_and_shells():
    from bh_graph.ballistic import node_order

    L = 4
    g = dim3.j3_torus_graph(L)
    order = node_order(g)
    c4 = dim3.j3_torus_coords(L)
    pr = dim3.sheet_projectors(order, c4)
    x0, x1 = (1, 2, 2), (2, 2, 2)
    preps = dim3.sector_preparations_3d(order, c4, x0, x1)
    for name, psi in preps.items():
        assert abs(np.linalg.norm(psi) - 1.0) < 1e-12, name
    w = dim3.sheet_weights(preps["sym0"], pr)
    assert abs(w["w_sym"] - 1.0) < 1e-12
    w = dim3.sheet_weights(preps["anti0"], pr)
    assert abs(w["w_anti"] - 1.0) < 1e-12
    w = dim3.sheet_weights(preps["sheet0"], pr)
    assert abs(w["w_sym"] - 0.5) < 1e-12
    shells = dim3.coarse_shells_3d(c4, order, x0, L, 6)
    assert len(shells[0]) == 2  # both sheets of the source cell
    assert sum(len(v) for v in shells.values()) == len(order)
    assert all(len(shells[r]) > 0 for r in (1, 2))
    d = dim3.hidden_delta_3d(order, c4, x0)
    assert abs(np.linalg.norm(d) - 1.0) < 1e-12
    assert abs(dim3.sheet_weights(d, pr)["w_anti"] - 1.0) < 1e-12
    dip = dim3.hidden_dipole_3d(order, c4, x0, x1)
    assert abs(np.linalg.norm(dip) - 1.0) < 1e-12


def test_dim3_plaquettes_displacements_classes():
    L = 4
    faces = dim3.cubic_face_plaquettes(L)
    assert len(faces) == 3 * L ** 3
    assert all(len(f) == 4 for f in faces)
    sub = dim3.j3_substrate(L)
    g, order = sub["graph"], sub["order"]
    eu, ev = np.array([[u] for u, v in g.edges()]), None
    eu = np.array([order.index(u) for u, v in g.edges()])
    ev = np.array([order.index(v) for u, v in g.edges()])
    disp = dim3.j3_edge_displacements(sub, eu, ev)
    assert disp.shape == (len(eu), 3)
    # Every micro-edge moves one quotient axis by +-1 (min-image unit).
    assert np.allclose(np.abs(disp).sum(axis=1), 1.0)
    eclass = dim3.edge_classes_j3(sub)
    assert set(eclass.values()) == {"SX", "SY", "SZ", "FX", "FY", "FZ"}
    for cls in ("SX", "SY", "SZ", "FX", "FY", "FZ"):
        assert sum(1 for v in eclass.values() if v == cls) == 128, cls


def test_dim3_coherence_and_flux():
    from bh_graph.ballistic import node_order

    L = 4
    g = dim3.j3_torus_graph(L)
    order = node_order(g)
    n = len(order)
    cfield = {v: (x, y, z) for v, (x, y, z, _) in
              dim3.j3_torus_coords(L).items()}
    uni = np.full(n, 1.0 / math.sqrt(n), dtype=np.complex128)
    assert dim3.spectral_coherence_3d(uni, order, cfield, L)["C"] == 1.0
    delta = np.zeros(n, dtype=np.complex128)
    delta[0] = 1.0
    assert abs(dim3.spectral_coherence_3d(delta, order, cfield, L)["C"]
               - 1.0 / 64.0) < 1e-12
    # +x plane wave on the cubic control: D = 1, J_net along +x.
    gc = dim3.cubic_torus_graph(L)
    oc = node_order(gc)
    cc = dim3.cubic_torus_coords(L)
    k = math.pi / 2  # periodic on L=4 (wrap edges see +k, not a jump)
    psi = np.array([np.exp(1j * k * cc[v][0]) / math.sqrt(len(oc))
                       for v in oc], dtype=np.complex128)
    pos = {v: i for i, v in enumerate(oc)}
    edges = []
    for u, v in gc.edges():
        a = np.array(cc[u], dtype=float)
        b = np.array(cc[v], dtype=float)
        d = b - a
        d -= np.round(d / L) * L
        edges.append((pos[u], pos[v], d[0], d[1], d[2]))
    f = dim3.flux_decomposition_3d(psi, edges)
    assert abs(f["D"] - 1.0) < 1e-9
    assert f["J_net"][0] > 0 and abs(f["J_net"][1]) < 1e-9
    tr = dim3.d_trace_3d(np.array([psi, psi]), edges)
    assert tr["D"].shape == (2,) and tr["J_net"].shape == (2, 3)
    f0 = dim3.flux_decomposition_3d(np.zeros_like(psi), edges)
    assert f0["D"] == 0.0
    # Hand-computed two-node case (irrational phases exercise fp paths):
    # single edge, d=(1,0,0): D=1, S=|2Im(conj(a)b)|, J_net=(cur,0,0).
    a = complex(0.6, 0.8) / math.sqrt(2.0)
    b = complex(0.8, -0.6) / math.sqrt(2.0)
    tiny = np.array([a, b], dtype=np.complex128)
    te = [(0, 1, 1.0, 0.0, 0.0)]
    ft = dim3.flux_decomposition_3d(tiny, te)
    cur = 2.0 * (np.conj(a) * b).imag
    assert abs(ft["S"] - abs(cur)) < 1e-15
    assert abs(ft["D"] - 1.0) < 1e-15
    assert abs(ft["J_net"][0] - cur) < 1e-15
    assert abs(ft["J_net"][1]) + abs(ft["J_net"][2]) == 0.0
    tt = dim3.d_trace_3d(np.array([tiny, tiny]), te)
    assert np.allclose(tt["D"], [1.0, 1.0], atol=1e-15)
    assert np.allclose(tt["J_net"][:, 0], [cur, cur], atol=1e-15)


def test_dim3_measure_source_consistent():
    # measure_source == manual Krylov + threshold + CG (L=3 smoke).
    from bh_graph import obs0
    from bh_graph.ballistic import hamiltonian, node_order
    from bh_graph.obs0r import omega_below_edge

    L = 3
    g = dim3.j3_torus_graph(L)
    order = node_order(g)
    h = hamiltonian(g, order=order)
    lrw = dim3.lrw_matrix(g, order)
    ts_w = np.arange(0, 0.11, 0.05)
    ts_d = np.arange(0, 0.26, 0.25)
    phi = dim3.static_phi_cg(h.tocsc(), 0, omega_below_edge(12))
    rec = dim3.measure_source(h, lrw, 0, [1, 2], ts_w, ts_d, phi)
    pw = dim3.krylov_wave_traces(h, 0, [1, 2], ts_w)
    assert rec["W"][1] == obs0.threshold_crossing(pw[:, 0], ts_w,
                                                  obs0.THETA_WAVE)
    assert rec["P"][2] == float(phi[2])
    assert set(rec) == {"W", "D", "P"}
