"""Tests for kerrp2 (continuous-latitude P2 estimator — readout only, no derivation)."""
import networkx as nx
import numpy as np

from bh_graph import kerraniso as K
from bh_graph import kerrp2 as P


def test_p2_values_and_edge_p2():
    assert P.p2_legendre(1.0) == 1.0  # pole
    assert P.p2_legendre(0.0) == -0.5  # equator
    assert P.p2_legendre(-1.0) == 1.0
    arr = P.p2_legendre([1.0, 0.0, -1.0])
    assert np.allclose(arr, [1.0, -0.5, 1.0])
    assert np.isnan(P.p2_legendre(float("nan")))
    assert np.isnan(P.p2_legendre(float("inf")))
    assert np.isnan(P.p2_legendre("x"))  # bad input -> NaN, no raise
    g = K.gradient_shell_graph_latitude(8, 4, seed=0)
    assert np.isnan(P.edge_p2(g, (0, 0), (1, 0)))  # missing attrs
    assert np.isnan(P.edge_p2(g, ("nope",), ("nope",)))  # missing nodes
    P.attach_latitudes(g, 8, 4)
    cts = [g.nodes[v]["cos_theta"] for v in g.nodes()]
    assert all(-1.0 <= c <= 1.0 for c in cts)
    assert g.nodes[(2, 3)]["cos_theta"] == 1.0 - (2 * 3 + 1) / 8.0
    assert g.nodes[(0, 5)]["cos_theta"] == g.nodes[(3, 5)]["cos_theta"]
    assert np.isfinite(P.edge_p2(g, (0, 0), (1, 0)))


def test_p2_amplitude_hand_check():
    p2s = [-0.5, -0.3, -0.1, 0.1, 0.3, 0.5]  # mean 0 -> exact recovery
    rows = [{"r": 2.0, "kappa": -2.0 * (1.0 + 0.5 * p), "p2": p} for p in p2s]
    amp = P.p2_amplitude(rows)
    assert amp["n"] == 6 and abs(amp["B"] - 0.5) < 1e-9
    flat = [{"r": 2.0, "kappa": -2.0, "p2": 0.25} for _ in range(6)]
    a_flat = P.p2_amplitude(flat)
    assert a_flat["n"] == 6 and np.isnan(a_flat["B"])  # Var(P2) == 0
    few = [{"r": 2.0, "kappa": -2.0 * (1.0 + 0.5 * p), "p2": p} for p in p2s[:4]]
    a_few = P.p2_amplitude(few)
    assert a_few["n"] == 4 and np.isnan(a_few["B"])  # n < 5
    assert np.isnan(P.p2_amplitude(None)["B"]) and P.p2_amplitude([])["n"] == 0


def test_eps_zero_tiny_finite():
    r = P.measure_p2_anisotropy(per_shell=8, n_shells=4, n_graphs=2, seed0=0)
    assert r["n_ok"] >= 1 and np.isfinite(r["mean"])  # finite only; tiny = noisy
    assert len(r["per_graph"]) == 2 and np.isfinite(r["bridge_polar_frac_mean"])


def test_starvation_contrast():
    # n_shells=5: per_shell=6/n_shells=4 pools only 4 rows (structural NaN floor
    # n>=5), so one extra shell-pair keeps it tiny while letting B exist.
    n_b_ok = 0
    n_bin_nan = 0
    for s in range(5):
        g = K.gradient_shell_graph_latitude(6, 5, epsilon_bridge=1.5, seed=s)
        P.attach_latitudes(g, 6, 5)
        amp = P.p2_amplitude(P.radial_edges_with_kappa(g, 5))
        if np.isfinite(amp["B"]):
            n_b_ok += 1
        prof = K.shell_kappa_profile_by_zone(g, 5, 4)
        if not np.isfinite(K.zonal_anisotropy(prof)["stacked"]):
            n_bin_nan += 1
    assert n_b_ok >= 1  # B usable where ...
    assert n_bin_nan >= 1  # ... the binary estimator starves


def test_determinism_and_bad_inputs():
    kw = {"per_shell": 8, "n_shells": 4, "n_graphs": 1, "seed0": 3}
    a = P.measure_p2_anisotropy(**kw)
    b = P.measure_p2_anisotropy(**kw)
    assert np.array_equal(a["per_graph"], b["per_graph"], equal_nan=True)
    c = P.p2_curve([], **kw)
    assert c["eps_imposed"] == [] and np.isnan(c["slope"])  # empty grid ok
    c2 = P.p2_curve([-0.5, 0.5], **kw)
    assert c2["eps_imposed"] == [-0.5, 0.5] and len(c2["results"]) == 2
    r = P.measure_p2_anisotropy(epsilon_bridge="bad", **kw)
    assert len(r["per_graph"]) == 1  # fallback, no raise
    h = P.compare_estimators([], **kw)
    assert h["eps_imposed"] == [] and np.isnan(h["binary_slope"])
    assert np.isnan(h["p2_slope"])
    assert P.radial_edges_with_kappa(nx.Graph(), 4) == []


def test_compare_estimators_smoke():
    h = P.compare_estimators(
        [0.0], per_shell=8, n_shells=4, n_graphs=1, seed0=0
    )
    assert h["eps_imposed"] == [0.0]
    for k in ("binary_mean", "binary_sem", "p2_mean", "p2_sem"):
        assert len(h[k]) == 1
    assert h["binary_n_ok"] == [int(v) for v in h["binary_n_ok"]]
    assert np.isnan(h["binary_slope"]) and np.isnan(h["p2_slope"])  # 1 pt


def test_p2bridge_eps_zero_matches_orici():
    from bh_graph.orici import gradient_shell_graph

    g0 = P.gradient_shell_graph_p2bridge(8, 4, seed=5)
    g1 = gradient_shell_graph(8, 4, seed=5)
    e0 = set(map(tuple, map(sorted, g0.edges())))
    e1 = set(map(tuple, map(sorted, g1.edges())))
    assert e0 == e1
    assert all("cos_theta" in g0.nodes[v] for v in g0.nodes())
    w = P.p2_node_weights(8, 0.5)
    assert w[0] > w[4]  # caps weight exceeds band weight at eps > 0


def test_p2bridge_imposition_monotone_and_fallback():
    means = []
    for e in (-0.9, 0.9):
        vals = [
            P.bridge_p2_mean(P.gradient_shell_graph_p2bridge(10, 4, epsilon_p2=e, seed=s))
            for s in range(5)
        ]
        assert all(np.isfinite(vals))
        means.append(float(np.mean(vals)))
    assert means[0] < means[1]
    a = P.gradient_shell_graph_p2bridge(8, 4, epsilon_p2="bad", seed=1)
    b = P.gradient_shell_graph_p2bridge(8, 4, epsilon_p2=0.0, seed=1)
    assert set(map(tuple, map(sorted, a.edges()))) == set(map(tuple, map(sorted, b.edges())))
    assert np.isnan(P.bridge_p2_mean(nx.Graph()))


def test_p2_response_runs_tiny():
    r = P.measure_p2_response(per_shell=10, n_shells=5, n_graphs=2, seed0=0)
    assert len(r["per_graph"]) == 2 and np.isfinite(r["bridge_p2_mean"])
    c = P.p2_response_curve([0.0], per_shell=10, n_shells=5, n_graphs=1, seed0=0)
    assert c["eps_imposed"] == [0.0] and np.isnan(c["slope"])  # 1 pt
