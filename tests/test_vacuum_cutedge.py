"""Cut-edge probe: metric correctness (exact fractions, growth, pooling)."""
import networkx as nx
import numpy as np

from bh_graph.vacuum_cutedge import (
    K1_CUTFRAC_BAR,
    K1_KAPPA_BAR,
    LADDER_Q,
    MATCHED_PAIRS,
    RR_SEEDS,
    ball_counts,
    cut_edge_fraction,
    dilute_copy,
    growth_profile,
    growth_roots,
    is_valid_fraction,
    kappa_summary,
    lcc_fraction,
    lcc_subgraph,
    matched_rr,
    n_cut_edges,
    pooled_ci,
    spearman_with_ci,
)
from bh_graph.vacuum_graphs import build_cubic


def test_prereg_frozen_numbers():
    assert MATCHED_PAIRS == ((125, 6), (128, 8), (108, 12))
    assert RR_SEEDS == (0, 1, 2, 3, 4)
    assert LADDER_Q == (0.0, 0.05, 0.10, 0.15, 0.20)
    assert K1_KAPPA_BAR == -0.02 and K1_CUTFRAC_BAR == 0.05
    for n, k in MATCHED_PAIRS:
        assert (n * k) % 2 == 0


def test_cut_edge_exact():
    assert cut_edge_fraction(nx.path_graph(10)) == 1.0
    assert cut_edge_fraction(nx.cycle_graph(10)) == 0.0
    assert n_cut_edges(nx.path_graph(10)) == 9
    g, _ = build_cubic(3)
    assert cut_edge_fraction(g) == 0.0  # periodic lattice: no cut-edges
    assert np.isnan(cut_edge_fraction(nx.Graph()))
    assert n_cut_edges(nx.Graph()) == 0


def test_dilute_copy():
    g, _ = build_cubic(3)
    h, ndel = dilute_copy(g, 0.0, seed=0)
    assert ndel == 0 and h.number_of_edges() == g.number_of_edges()
    h2, ndel2 = dilute_copy(g, 1.0, seed=0)
    assert h2.number_of_edges() == 0
    a, _ = dilute_copy(g, 0.2, seed=7)
    b, _ = dilute_copy(g, 0.2, seed=7)
    assert set(a.edges()) == set(b.edges())  # frozen RNG deterministic
    assert not is_valid_fraction(1.5)


def test_lcc():
    g = nx.path_graph(6)
    assert lcc_fraction(g) == 1.0
    g.remove_edge(2, 3)
    assert abs(lcc_fraction(g) - 0.5) < 1e-12
    assert lcc_subgraph(g).number_of_nodes() == 3


def test_kappa_summary_path():
    k = kappa_summary(nx.path_graph(7))
    assert k["ok"] and k["n"] == 6
    assert abs(k["mean"]) < 1e-9  # chain flat (repo-pinned fact)


def test_growth_shapes():
    # Path: polynomial d ~= 1; tree: exponential wins.
    gp = growth_profile(nx.path_graph(40), 40)
    assert gp["ok"] and abs(gp["d_poly"] - 1.0) < 0.25
    assert gp["better"] == "poly" and not gp["fallback"]
    gt = growth_profile(nx.balanced_tree(2, 6), 127)
    assert gt["ok"] and gt["better"] == "exp"
    r = growth_roots(40, set(range(40)))
    assert r == [0, 13, 26]
    assert ball_counts(nx.path_graph(5), 2, 2) == {0: 1, 1: 3, 2: 5}


def test_matched_rr():
    g = matched_rr(20, 6, seed=0)
    assert g.number_of_nodes() == 20
    assert {d for _, d in g.degree()} == {6}


def test_pooling_and_spearman():
    p = pooled_ci([1.0, 2.0, 3.0, 4.0])
    assert p["ok"] and abs(p["mean"] - 2.5) < 1e-12
    assert not pooled_ci([])["ok"]
    s = spearman_with_ci([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    assert s["ok"] and abs(s["rho"] + 1.0) < 1e-12
    assert spearman_with_ci([1, 1, 1, 1], [1, 2, 3, 4])["ok"] is False
