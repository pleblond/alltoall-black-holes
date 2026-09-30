import networkx as nx
import numpy as np

from bh_graph.graphs import build_chain, build_complete, build_grid_2d
from bh_graph.scrambling import (
    arrival_times,
    graph_diameter,
    infection_time,
    mean_path_length,
)


def test_complete_has_diameter_one_and_cover_one():
    for n in [2, 5, 20]:
        g = build_complete(n)
        assert graph_diameter(g) == 1
        assert infection_time(g, 0) == 1
        assert mean_path_length(g) == 1.0


def test_single_node_is_zero():
    g = build_complete(1)
    assert graph_diameter(g) == 0
    assert infection_time(g, 0) == 0


def test_local_graphs_slower_than_complete():
    n = 25
    t_all = infection_time(build_complete(n), 0)
    t_chain = infection_time(build_chain(n), n // 2)
    t_grid = infection_time(build_grid_2d(5), 0)
    assert t_chain > t_all
    assert t_grid > t_all
    assert nx.diameter(build_chain(n)) == n - 1


def _sorted_grid_2d(L):
    return nx.convert_node_labels_to_integers(nx.grid_2d_graph(L, L), ordering="sorted")


def _clique_plug_grid(L=40, c=20):
    g0 = _sorted_grid_2d(L)
    g = g0.copy()
    plug = [x * L + y for x in range(c - 2, c + 3) for y in range(c - 2, c + 3)]
    for i in range(len(plug)):
        for j in range(i + 1, len(plug)):
            g.add_edge(plug[i], plug[j])
    return g0, g, plug


def test_static_shells_match_exact_2d_law_and_plug_shortcuts():
    # D13.0 control: P0' predicts ANALYTICALLY 2D substrate ball growth,
    # V(r) = 1+2r(r+1), so local slope p_eff(r) -> 2- (no exponent is
    # estimated; finite-window decimals are known finite-radius
    # behavior). Pins bit-exact match on all unclipped radii at L=40/80
    # (implementation check) plus finite-size approach: fractional-
    # window [0.2L, 0.5L] p rises toward 2 with L (1.9196 -> 1.9603).
    # Plug sign pattern (35<38, cover 37<40) pre-registered for
    # dynamical confirmation (D13.1).
    ps = []
    for L, plo, phi in ((40, 1.90, 1.94), (80, 1.94, 1.98)):
        g0 = _sorted_grid_2d(L)
        c = L // 2
        src = c * L + c
        d0 = arrival_times(g0, src)
        edge = min(c, L - 1 - c)
        for r in range(1, edge + 1):
            v = sum(1 for n in d0 if d0[n] <= r)
            assert v == 1 + 2 * r * (r + 1), (L, r, v)
        rr = np.arange(1, edge + 1, dtype=float)
        vv = np.array([sum(1 for n in d0 if d0[n] <= r) for r in rr])
        lo, hi = int(0.2 * L), min(int(0.5 * L), edge)
        m = (rr >= lo) & (rr <= hi)
        p, _ = np.polyfit(np.log(rr[m]), np.log(vv[m]), 1)
        assert plo < p < phi, (L, p)
        ps.append(p)
    assert ps[1] > ps[0], ps
    g0, g, _ = _clique_plug_grid(40, 20)
    src, corner = 20 * 40 + 20, 39 * 40 + 39
    d0 = arrival_times(g0, src)
    dp = arrival_times(g, src)
    assert d0[corner] == 38, d0[corner]
    assert dp[corner] == 35, dp[corner]
    assert max(dp.values()) == 37, max(dp.values())
    assert max(d0.values()) == 40, max(d0.values())


def test_weighted_first_passage_delays_at_plug():
    # Static dissociation (cf. T9): ceff-weighted distance runs strictly
    # later than hop distance -- adjacency vs candidate physical cost,
    # not yet propagation (no U). Corner delay exactly 5.0; all plug
    # nodes delayed except the source itself (0 under both readings).
    # Dynamical confirmation (T_U^plug > T_U^vac) queued on D13.1.
    from bh_graph import emergent_dim as ed

    L, c = 40, 20
    g0, g, plug = _clique_plug_grid(L, c)
    src, corner = c * L + c, 39 * L + 39
    dp = arrival_times(g, src)
    d0 = arrival_times(g0, src)
    w = ed.ceff_cost_fn(g, z_vac=4.0)
    dw = nx.single_source_dijkstra_path_length(g, src, weight=w)
    assert abs(dw[corner] - d0[corner] - 5.0) < 1e-9, dw[corner]
    delayed = [n for n in plug if dw[n] > dp[n] + 1e-9]
    assert len(delayed) == 24, len(delayed)
    assert set(plug) - set(delayed) == {src}
