"""P1 wave-sector + one-way coupling apparatus pins (D14-P1 prereg).

Locks: H(G) = -J*A hopping-only, Krylov unitarity, free-packet group
velocity v_g = 2J sin(ka), k->-k reversal, zero-k null, directed-bin
MSD, one-way purity (frozen-G consumption), region-weight/IPR units.
Campaign numbers are FILED in docs/DEFERRED.md, not pinned.
"""

import networkx as nx
import numpy as np

from bh_graph.ballistic import (
    adjacency_csr,
    branch_mixing,
    branch_projectors,
    branch_purify,
    branch_weight,
    branch_weights_all,
    chiral_breaking_strength,
    chiral_gamma_diag,
    com,
    evolve_fixed,
    first_crossing_time,
    fit_velocity,
    gaussian_packet,
    graphs_from_saved,
    hamiltonian,
    index_of,
    ipr,
    is_accounting_ok,
    is_hermitian_ok,
    is_normalized_ok,
    is_projector_ok,
    j2_branch_parity,
    msd_exponent_rs,
    node_order,
    oneway_run,
    packet_spread_ok,
    packet_width,
    post_crossing_fit,
    region_weight,
    residence,
    ring_coords,
    tb_chain_velocity,
    torus_grid_coords,
    unwrap_trace,
    velocity_autocorr,
)
from bh_graph.formation import (
    formation_run,
    j2_torus_coords,
    j2_torus_graph,
    soup_graph,
    state_from_nx,
    triangle_count,
)
from bh_graph.graphs import build_torus_grid


def _ring_run(n=200, sigma=10.0, k=0.5, dt=0.2, t_end=60.0):
    g = nx.cycle_graph(n)
    order = node_order(g)
    coords = ring_coords(n)
    psi0 = gaussian_packet(coords, order, (n / 4,), (k,), sigma, periods=(n,))
    h = hamiltonian(g, j=1.0, order=order)
    rec = evolve_fixed(psi0, h, dt, int(t_end / dt))
    ts = np.arange(rec["psi"].shape[0]) * dt
    rs = unwrap_trace(
        np.array([com(p, coords, order, periods=(n,)) for p in rec["psi"]]),
        periods=(n,),
    )
    return rec, ts, rs


def test_hamiltonian_is_hopping_only():
    g = nx.path_graph(8)
    order = node_order(g)
    h = hamiltonian(g, j=1.0, order=order).toarray()
    assert np.allclose(h, -nx.to_numpy_array(g, nodelist=order))
    assert is_hermitian_ok(hamiltonian(g, order=order))
    assert not is_hermitian_ok(adjacency_csr(g, order) + 1j * adjacency_csr(g, order))
    c = nx.cycle_graph(8)  # 2-regular: H == L - 2I exactly (phase-only shift)
    oc = node_order(c)
    assert np.allclose(
        hamiltonian(c, order=oc).toarray(),
        nx.laplacian_matrix(c, nodelist=oc).toarray() - 2 * np.eye(8),
    )


def test_unitary_norm_conservation():
    rec, _, _ = _ring_run()
    assert np.all(np.abs(rec["norms"] - 1.0) < 1e-8)
    assert is_normalized_ok(rec["psi"][-1])


def test_free_packet_group_velocity():
    _, ts, rs = _ring_run()
    v = fit_velocity(rs, ts)["speed"]
    assert abs(v - tb_chain_velocity(0.5)) / tb_chain_velocity(0.5) < 0.10
    assert abs(tb_chain_velocity(0.0)) == 0.0
    assert tb_chain_velocity(0.5) == -tb_chain_velocity(-0.5)  # odd in k


def test_k_reversal_and_zero_k_null():
    _, ts, rs_p = _ring_run(k=0.5)
    _, _, rs_m = _ring_run(k=-0.5)
    vp = fit_velocity(rs_p, ts)["v"]
    vm = fit_velocity(rs_m, ts)["v"]
    assert vp[0] * vm[0] < 0  # opposite directions
    assert abs(vp[0] + vm[0]) / abs(vp[0]) < 0.10  # equal magnitude
    _, ts0, rs0 = _ring_run(k=0.0)
    assert fit_velocity(rs0, ts0)["speed"] < 0.05 * abs(vp[0])  # null control


def test_directed_bin_and_persistent_autocorr():
    _, ts, rs = _ring_run()
    assert msd_exponent_rs(rs, ts) > 1.3  # directed bin (Stage-0 bins)
    cv = velocity_autocorr(rs, ts)
    assert np.mean(cv[:10]) > 0.5  # positive over many steps


def test_packet_conjugate_and_spread_gate():
    order = list(range(60))
    coords = ring_coords(60)
    pp = gaussian_packet(coords, order, (15.0,), (0.5,), 6.0, periods=(60,))
    pm = gaussian_packet(coords, order, (15.0,), (-0.5,), 6.0, periods=(60,))
    assert is_normalized_ok(pp) and is_normalized_ok(pm)
    assert np.allclose(pm, np.conj(pp))  # real envelope: -k is conjugate
    assert packet_spread_ok(6.0, (60,)) and not packet_spread_ok(15.0, (60,))


def test_evolution_determinism():
    rec1, _, _ = _ring_run()
    rec2, _, _ = _ring_run()
    assert np.array_equal(rec1["psi"], rec2["psi"])


def test_com_and_unwrap_units():
    coords = ring_coords(100)
    order = list(range(100))
    psi = gaussian_packet(coords, order, (25.0,), (0.0,), 5.0, periods=(100,))
    assert abs(com(psi, coords, order, periods=(100,))[0] - 25.0) < 1.0
    ts = np.arange(0.0, 50.0, 0.5)
    rs = unwrap_trace(np.array([[(80.0 + 0.9 * t) % 100.0] for t in ts]), periods=(100,))
    assert fit_velocity(rs, ts)["speed"] == abs(fit_velocity(rs, ts)["v"][0])
    assert abs(fit_velocity(rs, ts)["v"][0] - 0.9) < 1e-9


def test_region_weight_ipr_residence_units():
    n = 50
    loc = np.zeros(n, dtype=complex)
    loc[7] = 1.0
    assert region_weight(loc, [7]) == 1.0 and ipr(loc) == 1.0
    uni = np.full(n, 1 / np.sqrt(n), dtype=complex)
    assert abs(ipr(uni) - 1 / n) < 1e-12
    assert abs(region_weight(uni, range(10)) - 0.2) < 1e-12
    assert abs(residence([0.0, 1.0, 0.0], [0.0, 1.0, 2.0]) - 1.0) < 1e-12


def test_oneway_consumes_frozen_graphs():
    st = state_from_nx(soup_graph("er", 60, 6, 0))
    r = formation_run(st, "d1", 4, 0, t_max=6, elist_window=(1, 6))
    nodes = sorted(st["nodes"])
    graphs = graphs_from_saved(r["elists"], nodes)
    assert sorted(graphs) == [1, 2, 3, 4, 5, 6]
    assert all(g.number_of_edges() == r["e0"] for g in graphs.values())
    assert triangle_count(state_from_nx(graphs[6])) == r["t_trace"][5]
    order = node_order(graphs[1])
    psi0 = np.zeros(60, dtype=complex)
    psi0[index_of(order)[0]] = 1.0
    before = [sorted(g.edges()) for g in graphs.values()]
    out = oneway_run(list(graphs.values()), psi0, order, dt=0.1, steps_per_state=4)
    assert out["psi"].shape == (1 + 6 * 4, 60)
    assert np.all(np.abs(out["norms"] - 1.0) < 1e-8)
    assert [sorted(g.edges()) for g in graphs.values()] == before  # never steers G
    out2 = oneway_run(list(graphs.values()), psi0, order, dt=0.1, steps_per_state=4)
    assert np.array_equal(out["psi"], out2["psi"])  # deterministic


def test_disconnected_graph_norm():
    g = nx.disjoint_union(nx.cycle_graph(30), nx.cycle_graph(30))
    order = node_order(g)
    coords = {v: (float(v),) for v in order}
    psi0 = gaussian_packet(coords, order, (5.0,), (0.5,), 4.0)  # no periods: plain
    rec = evolve_fixed(psi0, hamiltonian(g, order=order), 0.2, 100)
    assert np.all(np.abs(rec["norms"] - 1.0) < 1e-8)  # dust-safe (block-diagonal)


def test_torus_grid_packet_moves():
    L = 24
    g = build_torus_grid(L)
    order = node_order(g)
    coords = torus_grid_coords(L)
    assert set(coords) == set(order)
    psi0 = gaussian_packet(coords, order, (6.0, 12.0), (0.5, 0.0), 3.0, periods=(L, L))
    assert packet_spread_ok(3.0, (L, L))
    rec = evolve_fixed(psi0, hamiltonian(g, order=order), 0.2, 100)
    assert np.all(np.abs(rec["norms"] - 1.0) < 1e-8)
    ts = np.arange(101) * 0.2
    rs = unwrap_trace(
        np.array([com(p, coords, order, periods=(L, L)) for p in rec["psi"]]),
        periods=(L, L),
    )
    v = fit_velocity(rs, ts)["v"]
    assert v[0] > 0.5 and abs(v[1]) < 0.1 * v[0]  # along +x, no transverse drift


def _j2_branch_setup(L=8):
    g = j2_torus_graph(L)
    order = node_order(g)
    c3 = j2_torus_coords(L)
    coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    h = hamiltonian(g, order=order).toarray()
    return g, order, coords, c3, h, branch_projectors(h)


def test_branch_projector_algebra():
    _, order, _, c3, h, br = _j2_branch_setup()
    n = len(order)
    assert is_projector_ok(br["P_plus"]) and is_projector_ok(br["P_minus"])
    assert not is_projector_ok(2 * br["P_plus"])  # 2P not idempotent
    assert np.abs(br["P_plus"] @ br["P_minus"]).max() < 1e-12  # orthogonal
    assert br["n_zero"] >= n // 2  # extensive flat zero band (N/2 + nodal)
    gam = np.diag(chiral_gamma_diag(j2_branch_parity(c3), order))
    assert np.abs(gam @ h @ gam + h).max() < 1e-12  # {Gamma, H} = 0
    assert np.abs(gam @ br["P_plus"] @ gam - br["P_minus"]).max() < 1e-12


def test_branch_momentum_locking_and_purify():
    _, order, coords, _, _, br = _j2_branch_setup()
    lo = gaussian_packet(coords, order, (2.0, 4.0), (0.3, 0.0), 1.2, periods=(8, 8))
    assert packet_spread_ok(1.2, (8, 8))
    assert branch_weight(lo, br["P_minus"]) > 0.95  # k locks to minus branch
    hi = gaussian_packet(coords, order, (2.0, 4.0), (0.3 + np.pi, np.pi), 1.2, periods=(8, 8))
    assert branch_weight(hi, br["P_plus"]) > 0.95  # k+Q locks to plus branch
    pure, retained = branch_purify(lo, br["P_minus"])
    assert is_normalized_ok(pure) and abs(retained - branch_weight(lo, br["P_minus"])) < 1e-12
    assert branch_weight(pure, br["P_minus"]) > 1 - 1e-12  # exact purity


def test_free_branch_mixing_exact_zero():
    _, order, coords, _, h, br = _j2_branch_setup()
    psi = gaussian_packet(coords, order, (2.0, 4.0), (0.3, 0.0), 1.2, periods=(8, 8))
    rec = evolve_fixed(psi, h, 0.2, 20)
    assert branch_mixing([branch_weight(p, br["P_minus"]) for p in rec["psi"]]) < 1e-8
    assert branch_mixing([0.5, 0.5, 0.5]) == 0.0  # unit: flat trace


def test_fit_velocity_r2_unit():
    ts = np.arange(0.0, 10.0, 0.5)
    assert fit_velocity(np.array([[0.9 * t] for t in ts]), ts)["r2"] > 0.999  # linear
    assert fit_velocity(np.zeros((len(ts), 1)), ts)["r2"] == 1.0  # stationary


def test_branch_accounting_identity():
    _, order, coords, _, _, br = _j2_branch_setup()
    psi = gaussian_packet(coords, order, (2.0, 4.0), (0.3, 0.0), 1.2, periods=(8, 8))
    w = branch_weights_all(psi, br)
    assert is_accounting_ok(w["w_plus"], w["w_zero"], w["w_minus"])
    assert abs(w["w_plus"] + w["w_zero"] + w["w_minus"] - 1.0) < 1e-12
    assert not is_accounting_ok(0.5, 0.5, 0.5)
    assert w["w_zero"] >= 0.0 and w["w_plus"] >= 0.0 and w["w_minus"] >= 0.0


def test_chiral_breaking_zero_vs_triangle():
    g, order, _, c3, h, _ = _j2_branch_setup(L=4)
    gam = chiral_gamma_diag(j2_branch_parity(c3), order)
    assert chiral_breaking_strength(h, gam) == 0.0  # bare J2 bipartite-exact
    par = j2_branch_parity(c3)
    a, b = next(
        (u, v) for u in order for v in order if u < v and par[u] == par[v] and not g.has_edge(u, v)
    )
    g2 = g.copy()
    g2.add_edge(a, b)  # intra-partition edge: odd cycles guaranteed
    assert chiral_breaking_strength(hamiltonian(g2, order=order), gam) > 0.0


def test_first_crossing_time_unit():
    ts = np.arange(0.0, 10.0, 0.5)
    rs = np.array([[t, 0.0] for t in ts])  # unit-speed approach along x
    assert first_crossing_time(rs, ts, (5.0, 0.0), 1.0) == 4.5
    assert first_crossing_time(rs, ts, (50.0, 0.0), 1.0) is None  # miss, not error
    assert first_crossing_time(rs, ts, (0.0, 0.0), 1.0) == 0.0  # starts inside


def test_post_crossing_fit_unit():
    ts = np.arange(0.0, 10.0, 0.5)
    rs = np.array([[2.0 * t, -t] for t in ts])
    f = post_crossing_fit(rs, ts, 3.0, window=4.0)
    assert np.allclose(f["v"], [2.0, -1.0]) and f["r2"] > 0.999 and not f["truncated"]
    f2 = post_crossing_fit(rs, ts, 8.0, window=10.0)
    assert f2["truncated"] and f2["r2"] > 0.999  # flagged, still exact


def test_packet_width_unit():
    coords = ring_coords(100)
    order = list(range(100))
    loc = np.zeros(100, dtype=complex)
    loc[30] = 1.0
    assert packet_width(loc, coords, order, periods=(100,)) == 0.0  # single-site
    uni = np.full(100, 0.1, dtype=complex)
    assert packet_width(uni, coords, order, periods=(100,)) > 20.0  # delocalized
    psi = gaussian_packet(coords, order, (50.0,), (0.0,), 5.0, periods=(100,))
    assert 3.0 < packet_width(psi, coords, order, periods=(100,)) < 7.0  # ~sigma
