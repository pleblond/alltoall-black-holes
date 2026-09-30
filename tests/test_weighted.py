"""Weighted-graph audit adoption (Leblond, weighted-graph-paper).

Cross-checks our implementation against the paper's exact examples:
the 3-vertex integer blind spot (Sec 4.1: excess on [3/2, 2) missed at
every integer radius), the Prop-1 underpriced witness, and the
dominance-restoring cost increase (w_D idea: no violation, no
inflation anywhere). Conventions: counting measure, center included.
"""
import networkx as nx

from bh_graph.weighted import arrival_profile, underpriced_census, volume_comparison


def _three_vertex(cost):
    g0 = nx.path_graph(3)
    h = nx.path_graph(3)
    h.add_edge(0, 2, cost=cost)
    d0 = dict(nx.single_source_shortest_path_length(g0, 0))
    dw = nx.single_source_dijkstra_path_length(h, 0, weight="cost")
    d0ap = {n: dict(d) for n, d in nx.all_pairs_shortest_path_length(g0)}
    return h, d0, dw, d0ap


def test_event_sweep_finds_integer_blind_spot():
    # Paper Sec 4.1: path 0-1-2 + (0,2) at cost 3/2. Volumes agree at
    # every integer radius {0,1,2} but V_w = 3 > 2 = V_0 on [3/2, 2).
    # The sweep certifies max ratio 3/2 at r = 3/2; integer sampling
    # certifies nothing.
    _, d0, dw, _ = _three_vertex(1.5)
    for r in (0, 1, 2):
        v0 = sum(1 for d in d0.values() if d <= r)
        vw = sum(1 for d in dw.values() if d <= r)
        assert v0 == vw, r
    comp = volume_comparison(d0, dw)
    assert comp["max_ratio"] == 1.5
    assert comp["max_ratio_radius"] == 1.5
    assert comp["positive_intervals"] == [(1.5, 2.0)]


def test_underpriced_census_witnesses():
    # Prop 1: (0,2) at 3/2 < d_0 = 2 is the unique violation; original
    # edges (cost 1, unset attr defaults to 1.0) are fine.
    h, _, _, d0ap = _three_vertex(1.5)
    cens = underpriced_census(h, d0ap, weight="cost")
    assert cens == [(0, 2, 1.5, 2.0)]


def test_dominance_restoring_cost_removes_inflation():
    # w_D idea: raising (0,2) to exactly d_0 = 2 empties the census and
    # removes ALL inflation (max ratio 1.0, no positive intervals) --
    # Prop 1 + Corollary 1, executable. Costs equal to reference
    # distance are dominating (strict < is the violation).
    h, d0, dw, d0ap = _three_vertex(2.0)
    assert underpriced_census(h, d0ap, weight="cost") == []
    comp = volume_comparison(d0, dw)
    assert comp["max_ratio"] == 1.0
    assert comp["positive_intervals"] == []
    prof = arrival_profile(d0, dw)
    assert all(d <= 0 for _, _, _, d, _ in prof)


def test_weight_tolerance_recovers_geometry():
    # Well-posed tolerance (square L=20, same 30 damage longs, now with
    # length Lw on exactly the long edges): Lw=1 reproduces the binary
    # collapse (GoF2 0.385, lam2/lam3 1.92); Lw=20 recovers
    # near-vacuum (GoF2 0.684, lam2/lam3 5.49, past the 2-dominance
    # bar of 3). Continuity in weight is the knob binary lacks:
    # long-enough weak links are geometrically invisible. lam2/lam3
    # dips mid-transition (1.36 at Lw=5) before recovering (filed
    # as-is); lam3/lam4 never gaps (no 3D from weak wiring either).
    import numpy as np

    from bh_graph.update_rule import edge_span, inject_shortcuts

    def cmds(D):
        D2 = np.asarray(D, dtype=float) ** 2
        n = D2.shape[0]
        J = np.eye(n) - np.ones((n, n)) / n
        w, _ = np.linalg.eigh(-0.5 * J @ D2 @ J)
        return w[::-1]

    g = nx.convert_node_labels_to_integers(nx.grid_2d_graph(20, 20), ordering="sorted")
    dam = inject_shortcuts(g, 10, 3)
    longs = [(u, v) for u, v in dam.edges() if edge_span(dam, u, v) > 3]
    assert len(longs) == 30
    rows = {}
    for Lw in (1, 2, 5, 20):
        h = dam.copy()
        nx.set_edge_attributes(h, 1.0, "length")
        for u, v in longs:
            h[u][v]["length"] = float(Lw)
        ev = cmds(nx.floyd_warshall_numpy(h, weight="length"))
        pos = ev[ev > 0].sum()
        rows[Lw] = (ev[:2].sum() / pos, ev[1] / ev[2], ev[2] / ev[3])
    assert 0.38 < rows[1][0] < 0.39, rows[1]
    assert 1.9 < rows[1][1] < 2.0, rows[1]
    assert 1.3 < rows[5][1] < 1.5, rows[5]
    assert 0.68 < rows[20][0] < 0.69, rows[20]
    assert 5.4 < rows[20][1] < 5.6, rows[20]
    assert all(r[2] < 2.0 for r in rows.values()), rows
