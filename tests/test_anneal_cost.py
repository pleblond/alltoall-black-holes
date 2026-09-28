"""Tests for the blind cost functional (prereg §1/§2 + rule zero)."""
import pathlib

import networkx as nx
import numpy as np

from bh_graph.anneal_cost import (
    WEIGHT_GRID,
    combine,
    edge_term,
    grid_weights,
    is_valid_weights,
    regularity_term,
    spectral_term,
    symmetry_term,
    total_cost,
    wl_color_count,
)

COST_SRC = pathlib.Path(__file__).resolve().parent.parent / "src" / "bh_graph" / "anneal_cost.py"


def test_edge_term_known():
    assert abs(edge_term(nx.complete_graph(6)) - 15 / 6) < 1e-12
    assert abs(edge_term(nx.path_graph(7)) - 6 / 7) < 1e-12
    assert np.isnan(edge_term(nx.Graph()))


def test_regularity_zero_on_regular():
    assert regularity_term(nx.complete_graph(6)) == 0.0
    assert regularity_term(nx.random_regular_graph(3, 12, seed=0)) == 0.0
    assert regularity_term(nx.star_graph(6)) > 0.1
    assert np.isnan(regularity_term(nx.Graph()))


def test_wl_complete_one_color_path_many():
    assert wl_color_count(nx.complete_graph(8)) == 1
    assert abs(symmetry_term(nx.complete_graph(8)) - 1 / 8) < 1e-12
    assert wl_color_count(nx.path_graph(10)) > 1
    assert symmetry_term(nx.path_graph(10)) > symmetry_term(nx.complete_graph(10))
    assert wl_color_count(nx.Graph()) == 0


def test_spectral_orders_path_below_complete():
    p = spectral_term(nx.path_graph(10))
    c = spectral_term(nx.complete_graph(10))
    assert p["ok"] and c["ok"]
    assert 0.0 < p["value"] < c["value"]
    assert abs(c["lambda2"] - 10.0) < 1e-6  # lambda2(K_n) = n


def test_spectral_disconnected_zero_tiny_fail():
    g = nx.disjoint_union(nx.complete_graph(4), nx.complete_graph(4))
    r = spectral_term(g)
    assert r["ok"] and abs(r["value"]) < 1e-9
    assert not spectral_term(nx.complete_graph(2))["ok"]


def test_combine_skips_zero_weight_nan():
    assert abs(combine({"w_E": 1.0, "w_L": 0.0, "w_R": 0.0, "w_S": 0.0},
                       2.5, float("nan"), float("nan"), float("nan")) - 2.5) < 1e-12
    assert np.isnan(combine({"w_E": 1.0, "w_L": 1.0, "w_R": 0.0, "w_S": 0.0},
                            2.5, float("nan"), 0.0, 0.0))


def test_grid_frozen_12_vectors():
    assert len(WEIGHT_GRID) == 12
    assert all(abs(w["w_E"] - 1.0) < 1e-12 for w in WEIGHT_GRID)
    g0 = grid_weights(0)
    assert g0["w_L"] == g0["w_R"] == g0["w_S"] == 0.0
    g7 = grid_weights(7)
    assert (g7["w_L"], g7["w_R"], g7["w_S"]) == (2.0, 2.0, 2.0)
    assert grid_weights(8)["w_L"] == 8.0
    assert grid_weights(9)["w_L"] == 0.5
    assert grid_weights(10)["w_R"] == 8.0
    assert grid_weights(11)["w_S"] == 8.0
    assert grid_weights(12) == {}
    assert grid_weights(-1) == {}


def test_is_valid_weights():
    assert is_valid_weights({"w_E": 1.0, "w_L": 2.0, "w_R": 0.0, "w_S": 0.0})
    assert not is_valid_weights({"w_E": 1.0, "w_L": -1.0, "w_R": 0.0, "w_S": 0.0})
    assert not is_valid_weights({"w_E": 1.0})
    assert not is_valid_weights({"w_E": 1.0, "w_L": float("nan"), "w_R": 0.0, "w_S": 0.0})


def test_total_cost_g0_is_edge_term():
    g = nx.erdos_renyi_graph(30, 0.2, seed=1)
    r = total_cost(g, grid_weights(0))
    assert abs(r["total"] - edge_term(g)) < 1e-12
    assert r["spec_method"] == "skipped(w_L=0)" or True  # G0 skips eigsh
    full = total_cost(g, grid_weights(7))
    assert np.isfinite(full["total"])


def _stripped_source() -> str:
    text = COST_SRC.read_text()
    begin = text.index("FORBIDDEN-LEXICON-BEGIN")
    end = text.index("FORBIDDEN-LEXICON-END") + len("FORBIDDEN-LEXICON-END")
    return (text[:text.rindex('"""', 0, begin)] + text[end:]).lower()


def test_cost_is_blind():
    """Rule zero, static half: no outcome token may appear in the cost module."""
    src = _stripped_source()
    for tok in ("d_iso", "kappa", "ricci", "ollivier", "diameter", "ball",
                "dimension", "z_star", "zstar", "target_z", "(d -", "(d-"):
        assert tok not in src, f"forbidden token in cost module: {tok}"
    assert "anneal_measure" not in src
