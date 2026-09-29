"""Tests for the round-2 cost extension (prereg docs/anneal2-prereg.md §1/§2)."""
import pathlib

import networkx as nx
import numpy as np

from bh_graph.anneal_cost import (
    WEIGHT_GRID_V2,
    combine_v2,
    count_squares,
    count_triangles,
    grid_weights_v2,
    is_valid_weights_v2,
    square_term,
    squares_through_edge,
    total_cost_v2,
    triangle_term,
    triangles_through_edge,
)

COST_SRC = pathlib.Path(__file__).resolve().parent.parent / "src" / "bh_graph" / "anneal_cost.py"


def test_count_triangles_known():
    assert count_triangles(nx.complete_graph(4)) == 4
    assert count_triangles(nx.path_graph(10)) == 0
    assert count_triangles(nx.complete_bipartite_graph(3, 3)) == 0
    assert count_triangles(nx.Graph()) == 0
    g = nx.cycle_graph(5)
    g.add_edge(0, 2)
    assert count_triangles(g) == 1


def test_count_squares_known():
    assert count_squares(nx.cycle_graph(4)) == 1
    assert count_squares(nx.complete_graph(4)) == 3  # (4-1)!/2 orderings
    assert count_squares(nx.complete_bipartite_graph(2, 3)) == 3
    assert count_squares(nx.path_graph(10)) == 0
    assert count_squares(nx.complete_graph(5)) == 15  # C(5,4)*3
    assert count_squares(nx.Graph()) == 0
    # Open 2x2x2 cube: 6 faces.
    assert count_squares(nx.grid_graph(dim=[2, 2, 2], periodic=False)) == 6


def test_through_edge_telescoping_exact():
    """n(before) - n(after removal) == through_edge(before), every edge."""
    for trial in range(5):
        g = nx.erdos_renyi_graph(14, 0.35, seed=trial)
        for u, v in list(g.edges()):
            t3, s4 = triangles_through_edge(g, u, v), squares_through_edge(g, u, v)
            n3_before, n4_before = count_triangles(g), count_squares(g)
            g.remove_edge(u, v)
            assert n3_before - count_triangles(g) == t3
            assert n4_before - count_squares(g) == s4
            g.add_edge(u, v)
            assert count_triangles(g) == n3_before
            assert count_squares(g) == n4_before
    assert triangles_through_edge(g, 0, 1) >= 0  # smoke on non-edge path
    g2 = nx.path_graph(6)
    assert triangles_through_edge(g2, 0, 5) == 0
    assert squares_through_edge(g2, 0, 5) == 0


def test_square_triangle_terms_sign_and_nan():
    assert square_term(nx.cycle_graph(4)) == -1 / 4
    assert triangle_term(nx.complete_graph(4)) == 4 / 4
    assert square_term(nx.path_graph(6)) == 0.0
    assert triangle_term(nx.path_graph(6)) == 0.0
    assert np.isnan(square_term(nx.Graph()))
    assert np.isnan(triangle_term(nx.Graph()))


def test_grid_v2_frozen_12_vectors_signed():
    assert len(WEIGHT_GRID_V2) == 12
    assert all(abs(w["w_E"] - 1.0) < 1e-12 for w in WEIGHT_GRID_V2)
    assert grid_weights_v2(0)["w_L"] == grid_weights_v2(0)["w_T"] == 0.0
    assert grid_weights_v2(1)["w_L"] == 2.0
    assert grid_weights_v2(2)["w_L"] == -2.0  # spectral-hi arm (frozen sign)
    assert grid_weights_v2(5)["w_Q"] == 2.0
    assert grid_weights_v2(6)["w_T"] == -2.0  # trimax arm (frozen sign)
    assert grid_weights_v2(7)["w_T"] == 2.0
    assert grid_weights_v2(8)["w_R"] == 8.0
    assert grid_weights_v2(9)["w_Q"] == 8.0
    assert grid_weights_v2(12) == {} and grid_weights_v2(-1) == {}
    # 6/12 arms press away from trees (H2, H5, H6, H9, H10, H11).
    away = [h for h in range(12)
            if grid_weights_v2(h)["w_L"] < 0 or grid_weights_v2(h)["w_Q"] > 0
            or grid_weights_v2(h)["w_T"] < 0]
    assert away == [2, 5, 6, 9, 10, 11]


def test_is_valid_weights_v2_signed_rule():
    good = {"w_E": 1.0, "w_L": -2.0, "w_R": 0.0, "w_S": 0.0,
            "w_Q": 0.0, "w_T": -2.0}
    assert is_valid_weights_v2(good)
    bad_q = dict(good, w_Q=-1.0)
    assert not is_valid_weights_v2(bad_q)
    bad_e = dict(good, w_E=-0.5)
    assert not is_valid_weights_v2(bad_e)
    assert not is_valid_weights_v2({"w_E": 1.0})
    assert not is_valid_weights_v2(dict(good, w_L=float("nan")))


def test_combine_v2_signed_and_skip():
    w = {"w_E": 1.0, "w_L": -2.0, "w_R": 0.0, "w_S": 0.0,
         "w_Q": 0.0, "w_T": 0.0}
    assert abs(combine_v2(w, 2.0, 0.5, 0.0, 0.0, 0.0, 0.0) - 1.0) < 1e-12
    # Zero weights skip nan terms (signed-term ablation safe).
    assert abs(combine_v2(grid_weights_v2(0), 2.5, float("nan"),
                          float("nan"), float("nan"), float("nan"),
                          float("nan")) - 2.5) < 1e-12
    assert np.isnan(combine_v2(grid_weights_v2(5), 2.0, 0.0, 0.0, 0.0,
                               float("nan"), 0.0))


def test_total_cost_v2_finite_with_counts():
    g = nx.erdos_renyi_graph(30, 0.2, seed=1)
    r = total_cost_v2(g, grid_weights_v2(10))
    assert np.isfinite(r["total"])
    assert r["n3"] == count_triangles(g) and r["n4"] == count_squares(g)
    assert abs(r["t_sq"] + r["n4"] / 30) < 1e-12
    r0 = total_cost_v2(g, grid_weights_v2(0))
    assert abs(r0["total"] - r0["t_edge"]) < 1e-12


def test_spectral_no_skip_zero_regression():
    """k=2 'SM' once read λ3=0.0979 on the open 20×10×20 grid (skipped λ1).

    V2 (k=6 + zero detection) must return λ2 = 2−2cos(π/20) ≈ 0.0246.
    """
    import math

    from bh_graph.anneal_core import _build_cubic_dims
    from bh_graph.anneal_cost import spectral_term

    s = spectral_term(_build_cubic_dims(20, 10, 20, False))
    assert s["ok"] and s["method"] == "eigsh"
    assert abs(s["lambda2"] - (2 - 2 * math.cos(math.pi / 20))) < 1e-6


def _stripped_source() -> str:
    text = COST_SRC.read_text()
    begin = text.index("FORBIDDEN-LEXICON-BEGIN")
    end = text.index("FORBIDDEN-LEXICON-END") + len("FORBIDDEN-LEXICON-END")
    return (text[:text.rindex('"""', 0, begin)] + text[end:]).lower()


def test_cost_is_blind_v2_extended():
    """Rule zero, V2: extended lexicon over cost module incl. new terms."""
    src = _stripped_source()
    for tok in ("d_iso", "kappa", "ricci", "ollivier", "diameter", "ball",
                "dimension", "z_star", "zstar", "target_z", "(d -", "(d-",
                "target", "flat"):
        assert tok not in src, f"forbidden token in cost module: {tok}"
    assert "anneal_measure" not in src
