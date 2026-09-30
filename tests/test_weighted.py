"""Weighted-graph audit adoption (Leblond, weighted-graph-paper).

Cross-checks our implementation against the paper's exact examples:
the 3-vertex integer blind spot (Sec 4.1: excess on [3/2, 2) missed at
every integer radius), the Prop-1 underpriced witness, and the
dominance-restoring cost increase (w_D idea: no violation, no
inflation anywhere). Conventions: counting measure, center included.
"""
import networkx as nx

from bh_graph.weighted import (
    arrival_profile,
    block_coarsen,
    excess_stats,
    long_fraction,
    underpriced_census,
    volume_comparison,
)


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


def test_self_pricing_softens_but_not_restores():
    # First weight-selection candidate (blind, graph-internal, ZERO
    # parameters): w_e = span_e, each edge costs its own detour
    # (radius 8). On 30-long damage: MDS stays blurred (GoF2 0.402
    # vs vacuum 0.769 vs binary 0.385 -- softened, not restored);
    # event sweep vs plain-hop shows FULL domination (maxR 1.0, no
    # positive intervals -- costs globally high); yet the census
    # lists 16 violations (contraction without inflation: the
    # Counterexample-A regime, now measured on damage). Triple
    # readout (MDS profile + sweep domination + census violations)
    # is the scoring protocol for all future weight rules.
    import numpy as np

    from bh_graph.update_rule import edge_span, inject_shortcuts
    from bh_graph.weighted import underpriced_census, volume_comparison

    def cmds(D):
        D2 = np.asarray(D, dtype=float) ** 2
        n = D2.shape[0]
        J = np.eye(n) - np.ones((n, n)) / n
        w, _ = np.linalg.eigh(-0.5 * J @ D2 @ J)
        return w[::-1]

    g = nx.convert_node_labels_to_integers(nx.grid_2d_graph(20, 20), ordering="sorted")
    src = 10 * 20 + 10
    dam = inject_shortcuts(g, 10, 3)
    h = dam.copy()
    nx.set_edge_attributes(h, {e: float(edge_span(h, *e, 8)) for e in h.edges()}, "w")
    ev = cmds(nx.floyd_warshall_numpy(h, weight="w"))
    pos = ev[ev > 0].sum()
    assert 0.40 < ev[:2].sum() / pos < 0.41, ev[:4]
    assert 1.7 < ev[1] / ev[2] < 1.9, ev[:4]
    d0 = dict(nx.single_source_shortest_path_length(g, src))
    dw = nx.single_source_dijkstra_path_length(h, src, weight="w")
    comp = volume_comparison({k: d0[k] for k in h.nodes()}, dw)
    assert comp["max_ratio"] == 1.0
    assert comp["positive_intervals"] == []
    d0ap = {n: dict(d) for n, d in nx.all_pairs_shortest_path_length(g)}
    assert len(underpriced_census(h, d0ap, weight="w")) == 16


def test_coarsening_pilot_freezes_min_rule():
    # Weighted-RG pilot (2x2 blocking, L40 -> 5, ns=20 seed 0, tuple
    # grid; weak links = topologically long edges at length Lw):
    # (i) uniform controls flow IDENTICALLY under min/mean and the
    # Lw=1 row reproduces the binary lambda-flow 0.013 -> 0.310
    # (reduction check on the apparatus); (ii) lambda-flow is
    # topological (bit-identical across rules AND Lw); (iii) min
    # keeps fabric fidelity 1.000 at every level while mean smears
    # to 0.900 by level 3 -- min FROZEN as the campaign rule
    # (transport-faithful: parallel paths, best wins); (iv) long-edge
    # excess frozen (9.00 at every level @Lw=10 -- pilot-scale hint
    # that strength may be marginal while count is relevant; the
    # campaign decides, not this pin).
    from itertools import pairwise
    def run(Lw, rule):
        g = nx.grid_2d_graph(40, 40)
        nx.connected_double_edge_swap(g, 20, seed=0)
        nx.set_edge_attributes(g, 1.0, "L")
        if Lw > 1:
            for u, v in g.edges():
                if abs(u[0] - v[0]) + abs(u[1] - v[1]) > 1:
                    g[u][v]["L"] = float(Lw)
        lam, st = [long_fraction(g)], [excess_stats(g)]
        for _ in range(3):
            g = block_coarsen(g, rule)
            lam.append(long_fraction(g))
            st.append(excess_stats(g))
        return lam, st

    lam_min1, _ = run(1, "min")
    lam_mean1, _ = run(1, "mean")
    assert lam_min1 == lam_mean1
    assert all(b > a for a, b in pairwise(lam_min1))
    assert 0.25 < lam_min1[-1] < 0.36, lam_min1
    lam_min10, st_min10 = run(10, "min")
    _, st_mean10 = run(10, "mean")
    assert lam_min10 == lam_min1
    assert all(s["fabfid"] == 1.0 for s in st_min10)
    assert 0.89 < st_mean10[-1]["fabfid"] < 0.91, st_mean10[-1]
    assert all(abs(s["elong"] - 9.0) < 1e-9 for s in st_min10), st_min10


def test_violation_washout_campaign():
    # Weighted-RG (lambda, eps) campaign under FROZEN min-rule (L40 ->
    # 5, tuple grid, co-blocked plain as reference; weak links priced
    # Lw on exactly the long edges). Verdict: pricing sector
    # IRRELEVANT above span scale (washout, reviewer's y_w < 0 case),
    # topological sector RELEVANT (lambda grows regardless of Lw).
    # Rows pinned (ns=20 seed 0): lambda-flow identical across Lw
    # (topological, third confirmation); Lw=1 never heals (violfrac
    # == lambda every level -- ANALYTIC: min long-span 2 > 1, so
    # every long is underpriced at every level); Lw=10 washes out
    # (violfrac 0.012 -> 0.000 by level 3, margin ratio 0.51 -> 2.86
    # crossing 1 -- fixed weights outlive shrinking spans, defects
    # become overpriced/geometrically invisible); Lw=3 partial
    # (0.310 -> 0.190, margin 0.86 -- near the separatrix, one more
    # level would cross). Washout level k* ~= log2(span0/Lw). Control
    # ns=0: lambda = viol = 0 at every level (stays 2D). Vacuum is
    # RG-protected in the pricing direction: no pumping needed for
    # correctly-priced weak links. Caveat: frozen weights, no U --
    # washed-out defects persist as overpriced dead weight (margin
    # ~2.9), a real U might prune them (weight-rule design note).
    from bh_graph.weighted import pricing_flow_stats

    def run(ns, Lw):
        gw = nx.grid_2d_graph(40, 40)
        gp = nx.grid_2d_graph(40, 40)
        if ns:
            nx.connected_double_edge_swap(gw, ns, seed=0)
        nx.set_edge_attributes(gw, 1.0, "L")
        if ns and Lw > 1:
            for u, v in gw.edges():
                if abs(u[0] - v[0]) + abs(u[1] - v[1]) > 1:
                    gw[u][v]["L"] = float(Lw)
        rows = []
        for _ in range(4):
            rows.append(pricing_flow_stats(gw, gp))
            gw, gp = block_coarsen(gw), block_coarsen(gp)
        return rows

    ctl = run(0, 1)
    assert all(r["lambda"] == 0.0 and r["violfrac"] == 0.0 for r in ctl)
    r1, r3, r10 = run(20, 1), run(20, 3), run(20, 10)
    lam1 = [r["lambda"] for r in r1]
    assert [r["lambda"] for r in r3] == lam1
    assert [r["lambda"] for r in r10] == lam1
    assert all(r["violfrac"] == r["lambda"] for r in r1), r1
    assert 0.30 < lam1[-1] < 0.32, lam1
    assert r10[-1]["violfrac"] == 0.0, r10
    assert r10[0]["marginratio"] < 1.0 < r10[-1]["marginratio"], r10
    assert 2.8 < r10[-1]["marginratio"] < 2.9, r10[-1]
    assert r3[-1]["violfrac"] < r3[-1]["lambda"], r3[-1]
    assert 0.18 < r3[-1]["violfrac"] < 0.20, r3[-1]
    assert r3[-1]["marginratio"] < 1.0, r3[-1]
