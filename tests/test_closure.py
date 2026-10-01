"""D5 closure-driver apparatus pins (C2-PILOT-2): accept/units/theorems.

Locked test-list (review-response): propose-mechanism (pilot-1) +
cap-determinism + acceptance-exact + κ0≡D1 + Δt-accounting + truss +
Charikar. Campaign (66 union-runs) FILED in docs/DEFERRED.md.
"""

import math
import random

import networkx as nx

from bh_graph.formation import (
    accept_d5,
    charikar_core,
    formation_run,
    poisson_l1,
    soup_graph,
    state_from_nx,
    triangle_count,
    triangles_on_pair,
    truss_count_k,
    truss_kmax,
)


def test_accept_exact_and_parity():
    rng = random.Random(0)
    s0 = rng.getstate()
    assert accept_d5(2, 1.0, rng) is True
    assert rng.getstate() == s0  # net>=0: no draw
    assert accept_d5(-5, 0.0, rng) is True
    assert rng.getstate() == s0  # kappa=0 short-circuit: no draw
    assert accept_d5(0, 2.0, rng) is True
    assert rng.getstate() == s0
    r1, r2 = random.Random(3), random.Random(3)
    assert accept_d5(-1, 1.0, r1) == (r2.random() < math.exp(-1))  # single draw
    assert r1.getstate() == r2.getstate()


def test_k0_is_d1():
    st = state_from_nx(soup_graph("er", 200, 8, 0))
    rk = formation_run(st, "d5k", 4, 7, t_max=30, kappa=0.0)
    rd = formation_run(st, "d1", 4, 7, t_max=30)
    assert rk["hist_final"] == rd["hist_final"]
    assert rk["executes_trace"] == rd["executes_trace"]


def test_deltaT_accounting():
    g = nx.complete_graph(4)
    g.add_edge(0, 4)  # pendant (no new triangles)
    g.add_node(5)
    st = state_from_nx(g)
    assert triangles_on_pair(st, 0, 1) == 2  # K4 edge holds 2
    assert triangles_on_pair(st, 4, 1) == 1  # pendant closes 1 via node 0
    assert triangles_on_pair(st, 4, 5) == 0
    assert triangle_count(st) == 4  # K4 only


def test_T_incremental_exact():
    st = state_from_nx(soup_graph("er", 100, 8, 0))
    assert triangle_count(st) >= 0
    r, fs = formation_run(st, "d5k", 4, 0, t_max=10, kappa=1.0, return_state=True)
    assert r["t_final"] == triangle_count(fs)  # incremental == exact recount
    assert r["t_trace"][-1] == r["t_final"]
    assert len(r["t_trace"]) == r["sweeps"]


def test_truss_synthetic():
    g = nx.complete_graph(10)
    g.add_edges_from(
        (i, j) for i in range(10, 60) for j in range(i + 1, 60) if (i * 7 + j) % 13 == 0
    )
    assert truss_kmax(g) == 10  # K10 dominates scraps
    c, m, _ = truss_count_k(g, 5, 0.01)
    assert (c, m) == (1, 10)  # K10 is 10-truss (edges in 8 tris)
    c3, _, _ = truss_count_k(g, 3, 0.01)
    assert c3 >= 1


def test_charikar_synthetic():
    g = nx.complete_graph(10)
    g.add_edges_from((i, i + 1) for i in range(10, 30))  # sparse path aside
    core = charikar_core(state_from_nx(g))
    assert set(range(10)) <= core  # K10 survives peeling
    assert len(core) <= 12


def test_cap_determinism_dense():
    g = nx.complete_graph(30)
    g.remove_edges_from([(0, 1), (2, 3), (4, 5), (6, 7), (8, 9)])  # 5 non-edges
    st = state_from_nx(g)
    r1 = formation_run(st, "d1", 4, 0, t_max=5)
    r2 = formation_run(st, "d1", 4, 0, t_max=5)
    assert r1["executes_trace"] == r2["executes_trace"]  # deterministic Nones
    assert r1["executes_total"] <= 5 * r1["e0"]
    assert r1["executes_total"] < 5 * r1["e0"]  # cap-hits occurred


def test_d5inf_mirror_micro():
    g = nx.path_graph(8)  # wedges, zero triangles
    st = state_from_nx(g)
    r, fs = formation_run(st, "d5inf", 4, 0, t_max=5, return_state=True)
    assert r["executes_total"] > 0  # closures available
    assert r["e_final"] == r["e0"]
    assert r["t_final"] == triangle_count(fs)


def test_d35_rr_stillborn():
    st = state_from_nx(soup_graph("rr", 60, 6, 0))
    r = formation_run(st, "d35", 4, 0, kappa=1.0)
    assert r["stop"] == "stillborn"  # D3-loser inheritance (theorem)


def test_soup_triangle_baselines():
    g8 = soup_graph("er", 1600, 8, 0)
    t8 = triangle_count(state_from_nx(g8))
    assert 40 < t8 < 130  # zbar^3/6 ≈ 85 (loose: any sane draw)
    assert truss_kmax(g8) <= 4
    assert truss_count_k(g8, 5, 0.01)[0] == 0  # clean nucleation baseline
    assert 20 < triangle_count(state_from_nx(soup_graph("rr", 1600, 8, 0))) < 100
    assert 500 < triangle_count(state_from_nx(soup_graph("er", 1600, 16, 0))) < 900


def test_poisson_l1_unit():
    p8 = math.exp(-8) * 8**8 / math.factorial(8)
    assert abs(poisson_l1({8: 100}, 8.0, 100) - 2 * (1 - p8)) < 1e-9


def test_E_conservation_D5():
    st = state_from_nx(soup_graph("er", 200, 8, 0))
    for drv, kw in (
        ("d5k", {"kappa": 0.25}),
        ("d5k", {"kappa": 2.0}),
        ("d5inf", {}),
        ("d35", {"kappa": 1.0}),
    ):
        r = formation_run(st, drv, 4, 0, t_max=20, **kw)
        assert r["e_final"] == r["e0"]


def test_log_moves_shape_and_purity():
    st = state_from_nx(soup_graph("er", 100, 8, 0))
    r = formation_run(st, "d5k", 4, 0, t_max=15, kappa=1.0, log_stride=10)
    assert len(r["moves"]) > 100
    assert all(len(m) == 4 and isinstance(m[0], int) for m in r["moves"])
    assert any(m[3] for m in r["moves"]) and any(not m[3] for m in r["moves"])
    r2 = formation_run(st, "d5k", 4, 0, t_max=15, kappa=1.0, log_stride=10)
    assert r["moves"] == r2["moves"]  # deterministic log
    r0 = formation_run(st, "d5k", 4, 0, t_max=15, kappa=1.0)
    assert r["hist_final"] == r0["hist_final"]  # observation-pure
    assert r["executes_trace"] == r0["executes_trace"]
    assert r["t_trace"] == r0["t_trace"]


def test_k5_window():
    st = state_from_nx(soup_graph("er", 100, 8, 0))
    r = formation_run(st, "d5k", 4, 0, t_max=30, kappa=1.0, k5_window=(11, 29))
    assert sorted(r["k5win"]) == [x for x in range(11, 30) if x % 10 != 0]
    assert all(v[0] >= 0 for v in r["k5win"].values())
