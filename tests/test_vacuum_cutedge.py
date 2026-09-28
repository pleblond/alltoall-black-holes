"""H-κB probe tests: cut-edges, expanders, deletion, verdicts (fast sizes)."""
import networkx as nx
import numpy as np

from bh_graph import vacuum_cutedge as H


def test_cut_edge_fraction_pins():
    assert H.cut_edge_fraction(nx.path_graph(6))["cutfrac"] == 1.0
    assert H.cut_edge_fraction(nx.cycle_graph(6))["cutfrac"] == 0.0
    g = nx.cycle_graph(4)
    g.add_edge(0, 4)  # pendant = the only cut-edge (1/5)
    assert abs(H.cut_edge_fraction(g)["cutfrac"] - 0.2) < 1e-12
    assert H.cut_edge_fraction(nx.Graph())["ok"] is False


def test_lattice_has_no_cut_edges():
    from bh_graph.vacuum_graphs import build_vacuum
    for fam, L in (("cubic", 5), ("bcc", 4), ("fcc", 3)):
        b = build_vacuum(fam, L)
        cf = H.cut_edge_fraction(b["graph"])
        assert cf["ok"] and cf["cutfrac"] == 0.0 and cf["n_cut"] == 0


def test_measured_component_and_validity():
    g = nx.disjoint_union(nx.cycle_graph(10), nx.cycle_graph(3))
    mc = H.measured_component(g)
    assert mc["ok"] and mc["n_lc"] == 10 and mc["n_total"] == 13
    assert not H.is_valid_component(10, 13)  # 77% < 90%
    assert H.is_valid_component(9, 10)
    assert not H.is_valid_component(0, 10)


def test_edge_kappa_sample_flat_and_tree():
    from bh_graph.vacuum_graphs import build_vacuum
    b = build_vacuum("cubic", 5)
    r = H.edge_kappa_sample(b["graph"], n_edges=30, seed=123)
    assert r["ok"] and r["max_abs"] < 1e-6 and r["n_fail"] == 0
    t = nx.balanced_tree(2, 3)
    rt = H.edge_kappa_sample(t, n_edges=50, seed=123)
    assert rt["ok"] and rt["mean"] < -0.05  # repo pin direction


def test_shell_counts_and_growth_slope():
    assert H.shell_counts(nx.path_graph(7), 3, 3) == {0: 1, 1: 2, 2: 2, 3: 2}
    assert H.shell_counts(nx.path_graph(7), 99, 3) == {}
    # Synthetic cubic ball: 4-point log-log slope is 2.09 (lower-order
    # terms dominate at small r; 3 is asymptotic — see prereg §H-7).
    shells = {0: 1, 1: 6, 2: 18, 3: 38, 4: 66}
    s = H.growth_slope(shells, 1, 4)
    assert s["ok"] and abs(s["slope"] - 2.09) < 0.05 and s["r2"] > 0.99
    assert H.growth_slope({0: 1}, 1, 4)["ok"] is False
    from bh_graph.vacuum_graphs import build_vacuum
    b = build_vacuum("cubic", 8)  # r_max=3: r=1..3 unwrapped (L=6 wraps at 3)
    sh = H.shell_counts(b["graph"], int(b["center"]), 3)
    s2 = H.growth_slope(sh, 1, 3)
    assert s2["ok"] and abs(s2["slope"] - 1.98) < 0.1


def test_build_expander_regular():
    e = H.build_expander(6, 50, seed=0)
    assert e["ok"]
    assert all(d == 6 for _, d in e["graph"].degree())
    assert H.build_expander(2, 50, seed=0)["ok"] is False
    assert H.build_expander(6, 5, seed=0)["ok"] is False  # n <= k


def test_deletion_series_nested_and_counts():
    s = H.build_deletion_series("cubic", 5, keep_fracs=(1.0, 0.9, 0.8), seed=0)
    assert s["ok"] and len(s["levels"]) == 3
    e0 = s["n_edges0"]
    d1, d2 = s["levels"][1]["n_deleted"], s["levels"][2]["n_deleted"]
    assert s["levels"][0]["n_deleted"] == 0
    assert abs(d1 - 0.1 * e0) <= 1 and abs(d2 - 0.2 * e0) <= 1  # float-robust
    # Nested: level-2 edge set ⊆ level-1 ⊆ intact.
    e1 = set(s["levels"][1]["graph"].edges())
    e2 = set(s["levels"][2]["graph"].edges())
    assert e2 <= e1 and len(e1) == e0 - d1 and len(e2) == e0 - d2


def test_spearman_mc_paths():
    cf = [0.0, 0.05, 0.1, 0.2, 0.3]
    perfect = H.spearman_mc(cf, [0.0, -0.1, -0.2, -0.3, -0.4],
                            [0.01] * 5, n_draws=500, seed=7)
    assert perfect["ok"] and abs(perfect["rho"] + 1.0) < 1e-9 and perfect["hi"] < 0
    null = H.spearman_mc(cf, [0.0, 0.01, -0.01, 0.005, -0.005],
                         [0.1] * 5, n_draws=500, seed=7)
    assert null["ok"] and null["lo"] <= 0 <= null["hi"]
    const = H.spearman_mc(cf, [0.0] * 5, [0.1] * 5, n_draws=100, seed=7)
    assert const["ok"] is False  # constant input: rho undefined
    assert H.spearman_mc([0.1], [0.0], [0.01])["ok"] is False  # <3 points


def test_k1_verdict_paths():
    good = {"a": {"cutfracs": [0.0, 0.001], "kappa_means": [-0.15, -0.17]},
            "b": {"cutfracs": [0.0, 0.0], "kappa_means": [-0.2, -0.22]}}
    assert H.k1_verdict(good)["verdict"] == "NAIVE-DEAD"
    bad_cf = {"a": {"cutfracs": [0.05, 0.0], "kappa_means": [-0.15, -0.17]}}
    assert H.k1_verdict(bad_cf)["verdict"] == "NAIVE-SURVIVES"
    bad_k = {"a": {"cutfracs": [0.0, 0.0], "kappa_means": [-0.001, 0.002]}}
    assert H.k1_verdict(bad_k)["verdict"] == "NAIVE-SURVIVES"
    assert H.k1_verdict({})["verdict"] == "INCONCLUSIVE"


def test_k2_verdict_paths():
    hold = {"s": {"ok": True, "rho": -1.0, "lo": -1.0, "hi": -0.9}}
    assert H.k2_verdict(hold)["verdict"] == "PARTIAL-SCOPE-RESTRICTED"
    hold2 = {"s1": {"ok": True, "rho": -1.0, "lo": -1.0, "hi": -0.9},
             "s2": {"ok": True, "rho": -0.9, "lo": -1.0, "hi": -0.5}}
    assert H.k2_verdict(hold2)["verdict"] == "MONOTONIC-WITHIN-CLASS"
    no = {"s": {"ok": True, "rho": -0.2, "lo": -0.8, "hi": 0.5}}
    assert H.k2_verdict(no)["verdict"] == "NO-EVIDENCE"


def test_leg1_pair_tiny():
    r = H.leg1_pair("cubic", 5, seeds=(0, 1))
    assert r["ok"] and r["k"] == 6 and r["n"] == 125
    assert r["lattice"]["cutfrac"] == 0.0
    assert len(r["expanders"]) == 2
    assert all(np.isfinite(e["kappa"]["mean"]) for e in r["expanders"])


def test_measure_graph_and_mean_ci():
    from bh_graph.vacuum_graphs import build_vacuum
    b = build_vacuum("cubic", 5)
    m = H.measure_graph(b["graph"], root=int(b["center"]), n_edges=20)
    assert m["ok"] and m["cutfrac"] == 0.0 and abs(m["kappa"]["mean"]) < 1e-6
    ci = H.mean_ci([-0.15, -0.17, -0.16, -0.14, -0.18])
    assert ci["ok"] and ci["hi"] < -0.01
    assert H.mean_ci([1.0])["ok"] is False
