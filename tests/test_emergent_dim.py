"""v0.5: emergent-dimension protocol controls + K_N failure pins."""

import networkx as nx
import numpy as np

from bh_graph import emergent_dim as ed
from bh_graph.graphs import build_chain, build_complete, build_grid_2d


def test_shortest_controls_chain_grid2_grid3():
    # chain P_60 -> d ~ 1
    g = build_chain(60)
    m = ed.measure_emergent_dimension(g, source=30, kind="shortest", n_radii=30)
    assert m["fit"]["n_points"] >= 5
    assert abs(m["fit"]["p"] - 1.0) < 0.15, m["fit"]
    assert m["fit"]["r2"] > 0.95
    # grid 2d 20x20 -> d ~ 2 (interior source, Manhattan balls; interior
    # window avoids small-r discreteness and open-boundary slowdown)
    g2 = build_grid_2d(20)
    src = 10 * 20 + 10
    m2 = ed.measure_emergent_dimension(
        g2, source=src, kind="shortest", n_radii=40, v_min=5, v_max_frac=0.5
    )
    assert m2["fit"]["n_points"] >= 5
    assert abs(m2["fit"]["p"] - 2.0) < 0.3, m2["fit"]
    assert m2["fit"]["r2"] > 0.95
    # grid 3d 9x9x9 -> d ~ 3 (controls the V ~ r^3 ruler itself)
    g3 = nx.grid_graph([9, 9, 9])
    g3 = nx.convert_node_labels_to_integers(g3)
    n_side = 9
    src3 = 4 * (n_side * n_side) + 4 * n_side + 4
    m3 = ed.measure_emergent_dimension(
        g3, source=src3, kind="shortest", n_radii=40, v_min=8, v_max_frac=0.5
    )
    assert m3["fit"]["n_points"] >= 5
    assert abs(m3["fit"]["p"] - 3.0) < 0.4, m3["fit"]
    assert m3["fit"]["r2"] > 0.95


def test_complete_shortest_trivial_no_scaling_window():
    for n in (8, 32):
        g = build_complete(n)
        assert ed.is_shortest_path_trivial(g)
        m = ed.measure_emergent_dimension(g, kind="shortest", n_radii=12)
        assert m["trivial_shortest"]
        # V jumps 1 -> N: no scaling window, fit NaN by construction
        assert not ed.scaling_window_exists(m["volumes"])
        assert not np.isfinite(m["fit"]["p"])
        # resistance on K_N is uniform 2/N: also no geometry
        dist, _, _ = ed.info_distance_matrix(g, kind="resistance")
        off = dist[~np.eye(n, dtype=bool)]
        assert np.allclose(off, 2.0 / n, atol=1e-8)
        mr = ed.measure_emergent_dimension(g, kind="resistance", n_radii=12)
        assert not ed.scaling_window_exists(mr["volumes"])


def test_chain_not_trivial_resistance_monotone():
    g = build_chain(20)
    assert not ed.is_shortest_path_trivial(g)
    dist, _, _ = ed.info_distance_matrix(g, kind="resistance")
    # resistance grows with separation along chain
    assert dist[0, 19] > dist[0, 10] > dist[0, 1] > 0
    # diffusion + communicability are symmetric, positive off-diagonal,
    # and correlate positively with shortest path (diffusion closely,
    # communicability more weakly: it measures walk-profile similarity,
    # so symmetric endpoints look similar and long-range monotonicity
    # is NOT expected -- documented non-spatial behavior)
    ds, _, _ = ed.info_distance_matrix(g, kind="shortest")
    dd, _, _ = ed.info_distance_matrix(g, kind="diffusion", t=1.0)
    dc, _, _ = ed.info_distance_matrix(g, kind="communicability")
    for alt, thresh in ((dd, 0.6), (dc, 0.5)):
        assert np.allclose(alt, alt.T, atol=1e-8)
        off = alt[~np.eye(len(g), dtype=bool)]
        assert np.all(off > 0)
        a = ds[np.triu_indices(len(g), k=1)]
        b = alt[np.triu_indices(len(g), k=1)]
        corr = float(np.corrcoef(a, b)[0, 1])
        assert corr > thresh, corr


def test_effective_dimension_local_matches_fit_on_chain():
    g = build_chain(80)
    m = ed.measure_emergent_dimension(g, source=40, kind="shortest", n_radii=40)
    # median local d_eff over scaling window should sit near the fitted p ~ 1
    v = m["volumes"]
    vmax = float(np.max(v))
    mask = (v >= 2) & (v <= 0.9 * vmax)
    loc = m["d_eff"][mask]
    loc = loc[np.isfinite(loc)]
    assert len(loc) >= 3
    assert abs(float(np.median(loc)) - 1.0) < 0.35, (np.median(loc), m["fit"])
    assert abs(m["fit"]["p"] - 1.0) < 0.15


def test_shell_graph_has_nontrivial_profile():
    from bh_graph.orici import gradient_shell_graph

    g = gradient_shell_graph(per_shell=12, n_shells=6, gradient=True, seed=0)
    assert not ed.is_shortest_path_trivial(g)
    for kind in ("shortest", "resistance"):
        m = ed.measure_emergent_dimension(g, kind=kind, n_radii=20)
        # nontrivial: scaling window exists (exponent measured, not asserted to 3)
        assert ed.scaling_window_exists(m["volumes"]), kind
        assert m["fit"]["n_points"] >= 3, kind


def test_validity_helpers_no_exceptions():
    assert ed.is_valid_graph_for_dim(build_chain(5))
    assert not ed.is_valid_graph_for_dim(nx.Graph())
    assert ed.is_connected_for_resistance(build_chain(5))
    assert not ed.is_connected_for_resistance(nx.Graph())
    # unknown kind -> NaN matrix, not raise
    dist, _, _ = ed.info_distance_matrix(build_chain(5), kind="nope")
    assert bool(np.all(~np.isfinite(dist)))
    # degenerate ball/eff inputs -> empty/nan, not raise
    r, _v = ed.ball_volumes(np.zeros((0, 0)), 0)
    assert len(r) == 0
    assert len(ed.effective_dimension(np.array([1.0]), np.array([1.0]))) == 1


def test_diffusion_recovers_dimension_at_large_t():
    # t is the coarse-graining scale: small t sees grain, large t sees IR.
    g = build_chain(30)
    m = ed.measure_emergent_dimension(g, source=15, kind="diffusion", t=20.0, n_radii=30)
    assert m["fit"]["r2"] > 0.95
    assert abs(m["fit"]["p"] - 1.0) < 0.25, m["fit"]
    g2 = build_grid_2d(12)
    m2 = ed.measure_emergent_dimension(g2, source=6 * 12 + 6, kind="diffusion", t=5.0, n_radii=30)
    assert m2["fit"]["r2"] > 0.95
    assert abs(m2["fit"]["p"] - 2.0) < 0.4, m2["fit"]


def test_rejected_distances_pinned():
    # Resistance fails in 2D (log-growth -> spurious large p), communicability
    # fails on chain (similarity, not separation). Pinned qualitatively so a
    # future "fix" that silently re-adopts them must confront this test.
    g2 = build_grid_2d(12)
    mr = ed.measure_emergent_dimension(g2, source=6 * 12 + 6, kind="resistance", n_radii=25)
    assert np.isfinite(mr["fit"]["p"])
    assert abs(mr["fit"]["p"] - 2.0) > 1.0, mr["fit"]
    mc = ed.measure_emergent_dimension(
        build_chain(30), source=15, kind="communicability", n_radii=25
    )
    assert np.isfinite(mc["fit"]["p"])
    assert abs(mc["fit"]["p"] - 1.0) > 0.5, mc["fit"]
