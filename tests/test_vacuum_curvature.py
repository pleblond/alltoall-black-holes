"""Vacuum curvature: profile extraction + 3-model fit comparison."""
import numpy as np

from bh_graph.vacuum_curvature import (
    compare_fits,
    fit_linear,
    fit_log,
    fit_power,
    is_valid_profile_input,
    shell_kappa_profile_vacuum,
    sinkhorn_crosscheck_kappa,
)
from bh_graph.vacuum_graphs import add_excursion, build_cubic


def test_valid_checks():
    assert is_valid_profile_input(0, 3)
    assert not is_valid_profile_input(0, 2)


def test_log_data_selects_log():
    prof = {1: 1.0, 2: 1.0 + np.log(2), 3: 1.0 + np.log(3), 4: 1.0 + np.log(4)}
    out = compare_fits(prof)
    assert out["ok"] and out["winner"] == "log"
    assert out["fits"]["log"]["r2"] > 0.999


def test_power_data_selects_power():
    prof = {r: 2.0 * r ** -0.9 for r in (1, 2, 3, 4)}
    out = compare_fits(prof)
    assert out["ok"] and out["winner"] == "power"
    assert abs(out["fits"]["power"]["p"] - 0.9) < 1e-9


def test_linear_data_selects_linear():
    prof = {r: 3.0 - 0.5 * r for r in (1, 2, 3, 4)}
    out = compare_fits(prof)
    assert out["ok"] and out["winner"] == "linear"


def test_insufficient_data_not_raise():
    assert compare_fits({1: 0.5})["ok"] is False
    assert not fit_log({1: 1.0, 2: 2.0})["ok"]
    assert np.isnan(fit_power({})["p"])


def test_profile_structure_small():
    g, _ = build_cubic(3)
    h, _ = add_excursion(g, 13, 2)
    out = shell_kappa_profile_vacuum(h, 13, max_shell=3)
    assert set(out["profile"]) == {1, 2, 3}
    assert set(out["counts"]) == {1, 2, 3}
    assert all(v >= 0 for v in out["counts"].values())


def test_radial_profile_superset_and_shell0():
    # Amendment A1 exploratory: shells 0..4, radial+intra edges each once.
    from bh_graph.vacuum_curvature import radial_edge_kappa_profile
    g, _ = build_cubic(3)
    h, _ = add_excursion(g, 13, 2)
    out = radial_edge_kappa_profile(h, 13, max_shell=3)
    assert set(out["profile"]) == {0, 1, 2, 3}
    # shell 0 = edges incident to center = k + s = 6 + 2
    assert out["counts"][0] == 8
    # every edge counted exactly once across shells
    assert sum(out["counts"].values()) == h.number_of_edges()


def test_sinkhorn_crosscheck_direction():
    # Documented bias: kappa_sink <= kappa_exact (same edges, small graph).
    import networkx as nx
    from bh_graph.orici import ollivier_curvature
    g, _ = build_cubic(3)
    edges = list(g.edges())[:6]
    dist = nx.floyd_warshall_numpy(g)
    idx = {v: i for i, v in enumerate(g.nodes())}
    exact = np.mean([ollivier_curvature(g, u, v, _dist=dist, _idx=idx)
                     for u, v in edges])
    got = sinkhorn_crosscheck_kappa(g, edges)
    assert got["ok"] and got["n"] == len(edges)
    assert got["mean"] <= exact + 1e-6
