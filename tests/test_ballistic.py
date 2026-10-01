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
    com,
    evolve_fixed,
    fit_velocity,
    gaussian_packet,
    graphs_from_saved,
    hamiltonian,
    index_of,
    ipr,
    is_hermitian_ok,
    is_normalized_ok,
    msd_exponent_rs,
    node_order,
    oneway_run,
    packet_spread_ok,
    region_weight,
    residence,
    ring_coords,
    tb_chain_velocity,
    torus_grid_coords,
    unwrap_trace,
    velocity_autocorr,
)
from bh_graph.formation import formation_run, soup_graph, state_from_nx, triangle_count
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
