"""Tests for kerrcomplete (completeness-route calibration, imposed proxy)."""
import networkx as nx
import numpy as np

from bh_graph import kerrcomplete as C
from bh_graph.orici import gradient_shell_graph


def _edgeset(g):
    return set(map(tuple, map(sorted, g.edges())))


def test_delta_zero_matches_orici_and_zones():
    g0 = C.gradient_shell_graph_completeness(8, 4, seed=3)
    g1 = gradient_shell_graph(8, 4, seed=3)
    assert _edgeset(g0) == _edgeset(g1)
    assert all("zone" in g0.nodes[v] for v in g0.nodes())


def test_imposition_monotone_gap():
    gaps = {}
    for d in (-0.3, 0.3):
        gs = []
        for s in range(5):
            g = C.gradient_shell_graph_completeness(8, 4, delta_complete=d, seed=s)
            dens = C.zone_intra_density(g, 4)
            assert np.isfinite(dens["polar"]) and np.isfinite(dens["equatorial"])
            gs.append(dens["polar"] - dens["equatorial"])
        gaps[d] = float(np.mean(gs))
    assert gaps[-0.3] < 0 < gaps[0.3]


def test_determinism_and_invalid_delta_fallback():
    a = C.gradient_shell_graph_completeness(8, 4, delta_complete=0.2, seed=11)
    b = C.gradient_shell_graph_completeness(8, 4, delta_complete=0.2, seed=11)
    assert _edgeset(a) == _edgeset(b)
    g_bad = C.gradient_shell_graph_completeness(8, 4, delta_complete="bad", seed=1)
    g_zero = C.gradient_shell_graph_completeness(8, 4, delta_complete=0.0, seed=1)
    assert _edgeset(g_bad) == _edgeset(g_zero)
    g_big = C.gradient_shell_graph_completeness(8, 4, delta_complete=99.0, seed=1)
    assert _edgeset(g_big) == _edgeset(g_zero)


def test_measure_runs_tiny_and_bad_inputs_no_raise():
    r = C.measure_completeness_anisotropy(
        per_shell=6, n_shells=4, n_graphs=1, seed0=0, max_per_zone=1
    )
    assert set(r) >= {
        "delta_complete", "per_graph", "mean", "std", "sem",
        "n_ok", "zone_density_gap_mean", "stacked", "stacked_fits",
    }
    assert len(r["per_graph"]) == 1
    assert set(r["stacked"]) == {"polar", "equatorial", "mixed", "all"}
    # bad inputs: missing zones / bad types must not raise
    d = C.zone_intra_density(nx.Graph(), 4)
    assert np.isnan(d["polar"]) and np.isnan(d["equatorial"])
    d2 = C.zone_intra_density("bad", 4)
    assert np.isnan(d2["polar"])
    r2 = C.measure_completeness_anisotropy(
        per_shell=6, n_shells=4, n_graphs=1, delta_complete="bad",
        seed0=0, max_per_zone=1,
    )
    assert len(r2["per_graph"]) == 1
    c = C.completeness_curve(
        [0.0], per_shell=6, n_shells=4, n_graphs=1, seed0=0, max_per_zone=1
    )
    assert "slope" in c and len(c["results"]) == 1


def test_valid_delta_boundaries():
    assert C.is_valid_complete_delta(0.0)
    assert C.is_valid_complete_delta(-0.3)
    assert C.is_valid_complete_delta(0.3)
    assert not C.is_valid_complete_delta(-0.31)
    assert not C.is_valid_complete_delta(0.31)
    assert not C.is_valid_complete_delta(float("nan"))
    assert not C.is_valid_complete_delta("x")


def test_p2complete_eps_zero_matches_orici():
    g0 = C.gradient_shell_graph_p2complete(8, 4, seed=5)
    g1 = gradient_shell_graph(8, 4, seed=5)
    assert _edgeset(g0) == _edgeset(g1)
    assert all("cos_theta" in g0.nodes[v] for v in g0.nodes())


def test_p2complete_imposition_monotone_and_fallback():
    means = []
    for d in (-0.3, 0.3):
        vals = [
            C.caps_band_degree_gap(
                C.gradient_shell_graph_p2complete(8, 4, delta_p2=d, seed=s)
            )
            for s in range(5)
        ]
        assert all(np.isfinite(vals))
        means.append(float(np.mean(vals)))
    assert means[0] < means[1]
    a = C.gradient_shell_graph_p2complete(8, 4, delta_p2="bad", seed=1)
    b = C.gradient_shell_graph_p2complete(8, 4, delta_p2=0.0, seed=1)
    assert _edgeset(a) == _edgeset(b)
    assert np.isnan(C.caps_band_degree_gap(nx.Graph()))


def test_p2complete_response_runs_tiny():
    r = C.measure_p2complete_response(per_shell=10, n_shells=5, n_graphs=2, seed0=0)
    assert len(r["per_graph"]) == 2 and np.isfinite(r["degree_gap_mean"])
    c = C.p2complete_curve([0.0], per_shell=10, n_shells=5, n_graphs=1, seed0=0)
    assert c["eps_imposed"] == [0.0] and np.isnan(c["slope"])  # 1 pt
