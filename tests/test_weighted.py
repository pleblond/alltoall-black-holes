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


def test_phi_surface_slice_and_tolerance_contour():
    # D14 Phi-apparatus validation on frozen campaign states: the
    # Phi(n0,k) slice with the tolerance target contour drawn. Phi =
    # P(eta>1) over longs (eta = span/L); violfrac = Phi*lambda
    # (identity pinned to 1e-12 every row/level -- float association
    # in the last ulp forbids ==). Rows (seed 0):
    # ns=20/Lw=10 washes out Phi 0.900 -> 0.657 -> 0.167 -> 0.000
    # (nV 36,23,5,0; 4/40 longs already priced at k=0); Lw=1 rows
    # have Phi IDENTICALLY 1 (nV == nL every level -- analytic);
    # Lw=3 partial (Phi k3 = 11/18, never crosses). DISTRIBUTION >
    # MEAN exhibit: ns=20/Lw=10 k=1 has mean_inv_eta 1.12 ("healed"
    # by the mean) while Phi = 0.657 (23/35 still operational) --
    # the mean lies by more than a factor of honest. NON-MONOTONE
    # washout: ns=5/Lw=10 violfrac 0.0032 -> 0.0065 -> 0.000
    # (blocking first CONCENTRATES, then washes out) while nV falls
    # monotonically 10 -> 5 -> 0 -> 0. TOLERANCE CONTOUR (TOL =
    # 2/760 per-edge from binary MDS collapse; assumes density-like
    # transfer 20x20 -> 40x40 and operational-weighted ~ binary --
    # stated assumptions, not results): first-pass level is k=3 @
    # ns=20/Lw=10, k=2 @ ns=5/Lw=10, never within 4 levels for
    # Lw=1 (both ns) and Lw=3 (ns=20). k=0 ns=5 rows sit at 0.0032,
    # boundary-adjacent but correctly FAIL (> 0.00263).
    from bh_graph.weighted import phi_stats, pricing_flow_stats

    TOL = 2 / 760

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
            p, q = phi_stats(gw, gp), pricing_flow_stats(gw, gp)
            assert abs(p["phi"] * q["lambda"] - q["violfrac"]) < 1e-12
            rows.append((p, q))
            gw, gp = block_coarsen(gw), block_coarsen(gp)
        return rows

    def first_pass(rows):
        for k, (_p, q) in enumerate(rows):
            if q["violfrac"] <= TOL:
                return k
        return None

    r = run(20, 10)
    assert [p["n_viol"] for p, _ in r] == [36, 23, 5, 0]
    assert [p["n_longs"] for p, _ in r] == [40, 35, 30, 18]
    assert abs(r[0][0]["phi"] - 0.9) < 1e-12
    assert r[-1][0]["phi"] == 0.0
    assert r[1][0]["mean_inv_eta"] > 1.0
    assert r[1][0]["phi"] > 0.6, r[1][0]
    assert first_pass(r) == 3
    r = run(5, 10)
    assert [p["n_viol"] for p, _ in r] == [10, 5, 0, 0]
    v = [q["violfrac"] for _, q in r]
    assert v[1] > v[0] > TOL, v
    assert v[2] == 0.0
    assert first_pass(r) == 2
    for ns in (5, 20):
        r = run(ns, 1)
        assert all(p["n_viol"] == p["n_longs"] for p, _ in r)
        assert all(p["phi"] == 1.0 for p, _ in r)
        assert first_pass(r) is None
    r = run(20, 3)
    assert r[-1][0]["n_viol"] == 11 and r[-1][0]["n_longs"] == 18
    assert first_pass(r) is None


def test_knot_pilot_dual_reference():
    # Planted-knot pilot (5x5 clique @center 40x40, ns=20 seed 0,
    # Lw=10; frozen weights; r_O bins near/mid/far in the RULER
    # metric, frozen super-node rule; knot mask block-imaged per
    # level; interior = both endpoints in mask, excluded from weak
    # bins). DUAL ruler: eta_0 via pure plain (PRIMARY), eta_K via
    # plain+knot (weak links in NEITHER ruler -- first spike draft
    # put swaps in d_K and trivially "healed" everything, caught
    # before pinning). Results: (i) weak Phi_0 global nV/nL =
    # 36/40, 23/35, 5/30, 0/18 -- BIT-IDENTICAL campaign
    # reproduction (reduction control: knot untouched under fixed
    # ruler); (ii) weak Phi_K nV = 35,20,5,0 -- knot heals 1,3,0,0
    # marginal nearby longs via path-shortening (small, localized,
    # correct sign); (iii) METRIC BUBBLE: k=0 interior eta_0 =
    # 260/260 violated (thick vs fabric) vs eta_K = 260/0 (clique
    # distance 1 <= L -- local vs itself); (iv) d_K/d_0 <= 1 every
    # edge/level, k=0 means near 0.87 < far 0.96 (localized dip),
    # k=3 exactly 1.000 (5x5 knot dissolved to one block -- knot
    # persistence under R is scale-dependent, filed); (v) NO
    # min-rule bundle mixing: zero weak records with L < 10 at any
    # level (weak prices survive even near dense L=1 structure);
    # (vi) k=1 near-bin fast washout (1/7 vs far 9/9) is SELECTION
    # (near spans max 11, far spans min 12 -- proximity binning
    # selects pair separation; zero knot physics on the primary, as
    # constructed). Verdict: apparatus validated, null established
    # -- the real Delta-y_w test needs w-dynamics (frozen eta_0
    # cannot vary spatially by construction).
    from bh_graph.weighted import knot_block_mask, radial_eta_profile

    BINS = {"near": (0, 2), "mid": (3, 7), "far": (8, 10**9)}
    gw = nx.grid_2d_graph(40, 40)
    nx.connected_double_edge_swap(gw, 20, seed=0)
    kn = {(x, y) for x in range(18, 23) for y in range(18, 23)}
    for a in kn:
        for b in kn:
            if a < b and not gw.has_edge(a, b):
                gw.add_edge(a, b)
    nx.set_edge_attributes(gw, 1.0, "L")
    for u, v in gw.edges():
        if abs(u[0] - v[0]) + abs(u[1] - v[1]) > 1 and not (u in kn and v in kn):
            gw[u][v]["L"] = 10.0
    gKr = nx.grid_2d_graph(40, 40)
    for a in kn:
        for b in kn:
            if a < b and not gKr.has_edge(a, b):
                gKr.add_edge(a, b)
    gp = nx.grid_2d_graph(40, 40)

    v0g, vKg, nLg, means = [], [], [], []
    for k in range(4):
        m = knot_block_mask(kn, k)
        p0 = radial_eta_profile(gw, gp, m, BINS)
        pK = radial_eta_profile(gw, gKr, m, BINS)
        v0g.append(sum(p0["bins"][b]["n_viol"] for b in BINS))
        vKg.append(sum(pK["bins"][b]["n_viol"] for b in BINS))
        nLg.append(sum(p0["bins"][b]["n_longs"] for b in BINS))
        assert sum(1 for _, _, L, _ in p0["records"] if L < 10.0) == 0
        mr = {}
        for b in BINS:
            es = [e for e, bb in p0["bin_of"].items() if bb == b]
            assert all(pK["spans"][e] <= p0["spans"][e] for e in es)
            if es:
                mr[b] = sum(pK["spans"][e] / p0["spans"][e] for e in es) / len(es)
        means.append(mr)
        if k == 0:
            assert p0["interior"] == {"n_longs": 260, "n_viol": 260, "phi": 1.0}
            assert pK["interior"] == {"n_longs": 260, "n_viol": 0, "phi": 0.0}
        if k == 1:
            nb, fb = p0["bins"]["near"], p0["bins"]["far"]
            assert (nb["n_viol"], nb["n_longs"]) == (1, 7)
            assert (fb["n_viol"], fb["n_longs"]) == (9, 9)
            nsp = [p0["spans"][e] for e, bb in p0["bin_of"].items() if bb == "near"]
            fsp = [p0["spans"][e] for e, bb in p0["bin_of"].items() if bb == "far"]
            assert max(nsp) <= 11 and min(fsp) >= 12, (nsp, fsp)
        if k >= 2:
            assert p0["bins"]["far"]["n_longs"] == 0
        gw, gKr, gp = block_coarsen(gw), block_coarsen(gKr), block_coarsen(gp)

    assert v0g == [36, 23, 5, 0] and nLg == [40, 35, 30, 18]
    assert vKg == [35, 20, 5, 0]
    assert means[0]["near"] < 0.90, means[0]
    assert means[0]["far"] > 0.95, means[0]
    assert all(v == 1.0 for v in means[3].values()), means[3]


def test_chi_table_three_way_split():
    # Chi-measurement spike verdict (experiment-A fork): static-chi
    # distributions by population on the knot+swap A-state.
    # EXACTNESS (3x3 grid + diagonal (0,0)-(1,1), knot =
    # {(1,1),(1,2)}): 11 fabric / 1 weak / 1 interior; weak
    # embeddedness == 2 (common {(1,0),(0,1)}), jaccard == 1/3,
    # interior degree_sum == 8 (5+3). VERDICT (reduced A-state
    # 20x20 ns=5 3x3-knot seed 0; full A-state 40x40 medians filed
    # in DEFERRED, same shape): embeddedness weak max == fabric
    # max == 0 -- local-chi impossibility CONFIRMED empirically,
    # embeddedness-F predicts Delta-y_w EXACTLY 0 (null control
    # locked); betweenness medians ordered weak 0.0566 > fabric
    # 0.0104 > interior 0.0011 -- three-way split TYPICAL but tails
    # overlap (full-state fabric max 0.041 > weak med 0.029:
    # congestion-F prices central fabric high -- side effect to
    # monitor, Phi-verdict safe since fabric eta <= 1 always).
    import statistics as st

    from bh_graph.weighted import population_chi

    g = nx.grid_2d_graph(3, 3)
    g.add_edge((0, 0), (1, 1))
    kn = {(1, 1), (1, 2)}
    t = population_chi(g, kn, "embeddedness")
    assert {p: len(v) for p, v in t.items()} == {"fabric": 11, "weak": 1, "interior": 1}
    assert t["weak"] == [2]
    assert population_chi(g, kn, "jaccard")["weak"] == [1 / 3]
    assert population_chi(g, kn, "degree_sum")["interior"] == [8]

    g = nx.grid_2d_graph(20, 20)
    nx.connected_double_edge_swap(g, 5, seed=0)
    kn = {(x, y) for x in range(9, 12) for y in range(9, 12)}
    for a in kn:
        for b in kn:
            if a < b and not g.has_edge(a, b):
                g.add_edge(a, b)
    t = population_chi(g, kn, "embeddedness")
    assert max(t["weak"]) == 0 and max(t["fabric"]) == 0
    assert min(t["interior"]) > 0
    t = population_chi(g, kn, "betweenness")
    mw, mf, mi = (st.median(t[p]) for p in ("weak", "fabric", "interior"))
    assert mw > mf > mi, (mw, mf, mi)
    assert max(t["fabric"]) > mw  # tails overlap: central fabric priced high


def test_experiment_A_relaxation():
    # EXPERIMENT A (Form-1 relaxation, planted knot, E frozen, w0=1):
    # control (embeddedness, beta=1) + betweenness beta-grid
    # {3.5,35,350,3500} (alpha=0.2, 64 ticks). VERDICT vs locked
    # predictions: (i) CONTROL EXACT: weak w(n)==1.0 bit-identical
    # all 65 ticks (maxdev 0.0), all Phi rows frozen at the Lw1
    # slice (40/40,35/35,30/30,18/18), Delta=0 -- analytic null
    # holds end-to-end, no leak. (ii) TICK-0 of ALL 5 runs ==
    # Lw1 slice (uniform init = binary reduction, 5-way identity).
    # (iii) w* CONVERGENCE edgewise (maxdev < 2e-4, theory
    # excess*0.8^64). (iv) R_fw = 1/9.15 SWEEP-WIDE (0.10929 all
    # four beta -- linearity confirmed end-to-end). (v) MEDIANS hit
    # the locked table (beta=350: weak 11.004 / fabric 2.093).
    # (vi) BETA=3.5 frozen (w*~1.1 moves nothing, never cross);
    # BETA=35 partial (34/35,29/30,17/18 -- marginal healing, no
    # cross); BETA=350 CROSSES k=3 with (36,23,7,0) vs banked
    # Lw10 (36,23,5,0) -- k=0,1,3 EXACT, k=2 +2 = heterogeneity
    # cost (dynamical w* spread vs uniform planted Lw; direction
    # filed); BETA=3500 crosses k=0 (saturated, ceiling -- no
    # Delta resolution, as filed). (vii) GRADUALISM beta=350 tick8
    # (36,25,9,2) strictly between tick0 and final k=1,2,3
    # (relaxation, not imprinting). (viii) DELTA-y_w SPLIT-LEVEL
    # VERDICT (prediction FLIP filed honestly): w*-level
    # substitution CONFIRMED (near/far weak medians 8.934/11.242,
    # excess ratio 0.7746 ~= 0.775); Phi-level runs the WRONG way
    # (final k=1: near 1/7 vs far 9/9 -- SELECTION dominates:
    # near pairs are short pairs, spans <=11 vs >=12, disjoint
    # support kills matching) -- substitution invisible beneath
    # selection at Phi level. So: global basin reach YES (beta>=350
    # dynamically enters banked basin -- mechanism demonstrated,
    # beta-SCALE origin still owed to C2); knot-differential
    # washout NO at Phi level (needs matched-span apparatus or
    # dynamical chi). (ix) GATEWAY SHELL: W_fabric medians flat
    # (all ~2.0, no halo) with q90 near 4.79 > far 3.99 DESPITE
    # n=113<<2551 (tail signal = shell, as banked). (x) GUARD:
    # beta=350 fabric-med 2.09 < 3; beta=3500 trips to 11.9 WITH
    # ratio intact (predicted trip = linearity confirmation).
    import statistics as st

    from bh_graph.weighted import (
        edge_chi,
        fabric_price_profile,
        form1_trajectory,
        knot_block_mask,
        planted_knot_state,
        radial_eta_profile,
    )

    TOL = 2 / 760
    BINS = {"near": (0, 2), "mid": (3, 7), "far": (8, 10**9)}
    gw0, kn, gp0, _ = planted_knot_state()
    key_of = {tuple(sorted(e)): e for e in gw0.edges()}
    chi_emb = edge_chi(gw0, "embeddedness")
    chi_bet = edge_chi(gw0, "betweenness")
    weak_keys = [
        tuple(sorted(e))
        for e in gw0.edges()
        if abs(e[0][0] - e[1][0]) + abs(e[0][1] - e[1][1]) > 1 and not (e[0] in kn and e[1] in kn)
    ]
    fabric_keys = [
        tuple(sorted(e))
        for e in gw0.edges()
        if abs(e[0][0] - e[1][0]) + abs(e[0][1] - e[1][1]) == 1 and not (e[0] in kn and e[1] in kn)
    ]
    LW1 = [(40, 40), (35, 35), (30, 30), (18, 18)]

    def rows(traj, t):
        gw = gw0.copy()
        nx.set_edge_attributes(gw, {key_of[e]: w for e, w in traj[t].items()}, "L")
        gp = gp0.copy()
        out, nfs, cross = [], [], None
        for k in range(4):
            pr = radial_eta_profile(gw, gp, knot_block_mask(kn, k), BINS)
            nV = sum(pr["bins"][b]["n_viol"] for b in BINS)
            nL = sum(pr["bins"][b]["n_longs"] for b in BINS)
            out.append((nV, nL))
            nfs.append(
                (pr["bins"]["near"]["n_viol"], pr["bins"]["near"]["n_longs"],
                 pr["bins"]["far"]["n_viol"], pr["bins"]["far"]["n_longs"])
            )
            if nV / gw.number_of_edges() <= TOL and cross is None:
                cross = k
            gw, gp = block_coarsen(gw), block_coarsen(gp)
        return out, nfs, cross

    # control: bit-exact freeze
    traj_c, _ = form1_trajectory(chi_emb, alpha=0.2, beta=1.0, n_ticks=64)
    assert max(abs(traj_c[t][e] - 1.0) for t in range(65) for e in weak_keys) == 0.0
    for t in (0, 8, 64):
        r, _, c = rows(traj_c, t)
        assert r == LW1 and c is None

    MEDS = {3.5: (1.100, 1.0109), 35: (2.000, 1.1093), 350: (11.004, 2.0933), 3500: (101.04, 11.933)}
    for beta, (ew, ef) in MEDS.items():
        traj, ws = form1_trajectory(chi_bet, alpha=0.2, beta=beta, n_ticks=64)
        assert max(abs(traj[-1][e] - ws[e]) for e in chi_bet) < 2e-4
        mw, mf = st.median(traj[-1][e] for e in weak_keys), st.median(traj[-1][e] for e in fabric_keys)
        assert abs(mw - ew) < 0.02 and abs(mf - ef) < 0.02, (beta, mw, mf)
        assert abs((mf - 1) / (mw - 1) - 1 / 9.15) < 1e-3, (beta, mf, mw)
        r0, _, _ = rows(traj, 0)
        assert r0 == LW1
        rf, nfs, cross = rows(traj, 64)
        if beta == 3.5:
            assert rf == LW1 and cross is None
        elif beta == 35:
            assert rf == [(40, 40), (34, 35), (29, 30), (17, 18)] and cross is None
        elif beta == 350:
            assert rf == [(36, 40), (23, 35), (7, 30), (0, 18)] and cross == 3
            assert (rf[0][0], rf[1][0], rf[3][0]) == (36, 23, 0)  # banked Lw10 k=0,1,3
            r8, _, _ = rows(traj, 8)
            assert r8 == [(36, 40), (25, 35), (9, 30), (2, 18)]
            for k in (1, 2, 3):
                assert LW1[k][0] > r8[k][0] > rf[k][0], (k, r8, rf)
            assert nfs[0][:2] == (5, 6) and nfs[0][2:] == (23, 26)
            assert nfs[1][:2] == (1, 7) and nfs[1][2:] == (9, 9)
            gw = gw0.copy()
            nx.set_edge_attributes(gw, {key_of[e]: w for e, w in traj[-1].items()}, "L")
            wf = fabric_price_profile(gw, gp0, kn, BINS)
            assert all(1.8 < wf[b][0] < 2.2 for b in BINS), wf
            assert wf["near"][1] > wf["far"][1], wf
            assert mf < 3
        else:
            assert rf == [(0, 40), (0, 35), (0, 30), (0, 18)] and cross == 0
            assert mf > 3

    # w*-level substitution (beta=350): near/far weak medians + ratio
    traj, _ = form1_trajectory(chi_bet, alpha=0.2, beta=350.0, n_ticks=64)
    h = gp0.copy()
    h.add_node("SUPER")
    for z in kn:
        h.add_edge("SUPER", z)
    dh = dict(nx.single_source_shortest_path_length(h, "SUPER"))
    rr = {n: dh[n] - 1 for n in gp0.nodes()}
    wfin = traj[-1]
    near_w = sorted(wfin[e] for e in weak_keys if min(rr[e[0]], rr[e[1]]) <= 2)
    far_w = sorted(wfin[e] for e in weak_keys if min(rr[e[0]], rr[e[1]]) >= 8)
    assert abs(st.median(near_w) - 8.934) < 0.01 and abs(st.median(far_w) - 11.242) < 0.01
    assert abs((st.median(near_w) - 1) / (st.median(far_w) - 1) - 0.7746) < 0.002


def test_walk_spike_kill_shape():
    # Walk-spike verdict (exact finite-horizon propagation PRIMARY):
    # MECHANICS (3x3 grid): T=1 equals closed form (1/N)(1/di+1/dj)
    # to 1e-12; fractions sum to 1.0; deterministic (bit-identical
    # reruns); keys cover all edges. KILL SHAPE (reduced A-state
    # 20x20 ns=5 3x3-knot; full-spec 40x40 T-scan {1..320} filed in
    # DEFERRED: strict interior>fabric>weak at 0/8 horizons):
    # strict ordering False at T=10,40,80 (reduced reproduces the
    # kill); interior medians LOWEST everywhere (trapping intuition
    # dead per-edge: region-time spread over clique edges);
    # fabric~weak TIED within 5% (no weak/fabric lever in walk-chi,
    # order unstable across scales -- full-state fab barely above,
    # reduced weak barely above); deviation-from-uniform shrinks
    # monotonically T=40 -> T=320 (stationary flattening, graceful).
    # SUSCEPTIBILITY (reduced, T=40): A_weak(10) within 0.02 of the
    # analytic stationary null 1/(10(1-f)+f) (avoidance =
    # conductance normalization, structural contribution ~0);
    # A_fab(10) > 0.7 retained. MC-CHECK (W=20000 seed 0):
    # Monte Carlo agrees with exact on ordering + fabric median
    # within 10% (implementation verified; exact has no seeds/W).
    import statistics as st

    from bh_graph.weighted import (
        edge_populations,
        planted_knot_state,
        walk_traffic,
        walk_traffic_exact,
    )

    g = nx.grid_2d_graph(3, 3)
    e1 = walk_traffic_exact(g, 1)
    N = g.number_of_nodes()
    d = dict(g.degree())
    assert max(abs(e1[e] - (1 / N) * sum(1 / d[n] for n in e)) for e in e1) < 1e-12
    assert abs(sum(e1.values()) - 1.0) < 1e-9
    assert e1 == walk_traffic_exact(g, 1)
    assert set(e1) == {tuple(sorted(e)) for e in g.edges()}

    g, kn, _, _ = planted_knot_state(size=20, ns=5, seed=0, knot_center=(10, 10), knot_rad=1)
    pops = edge_populations(g, kn)
    M = g.number_of_edges()

    def meds(T, weight=None):
        tab = walk_traffic_exact(g, T, weight=weight)
        return {p: st.median([tab[e] for e in es]) for p, es in pops.items()}

    for T in (10, 40, 80):
        m = meds(T)
        assert not (m["interior"] > m["fabric"] > m["weak"]), (T, m)
    m = meds(40)
    assert m["interior"] < m["fabric"] and m["interior"] < m["weak"], m
    assert abs(m["fabric"] - m["weak"]) / m["fabric"] < 0.05, m

    def dev(T):
        m = meds(T)
        return max(abs(m[p] - 1 / M) / (1 / M) for p in m)

    assert dev(320) < dev(40), (dev(320), dev(40))

    w = {e: 1.0 for p in pops.values() for e in p}
    for e in pops["weak"]:
        w[e] = 10.0
    m10 = meds(40, weight=w)
    f = len(pops["weak"]) / M
    assert abs(m10["weak"] / m["weak"] - 1 / (10 * (1 - f) + f)) < 0.02
    assert m10["fabric"] / m["fabric"] > 0.7

    mc = walk_traffic(g, 40, 20000, 0)
    mm = {p: st.median([mc[e] for e in es]) for p, es in pops.items()}
    assert (mm["interior"] > mm["fabric"] > mm["weak"]) == (m["interior"] > m["fabric"] > m["weak"])
    assert abs(mm["fabric"] / m["fabric"] - 1) < 0.10


def test_betweenness_cross_sign_indefinite():
    # Filed analytic correction, verified (not cited): 5-node graph
    # (sa=1, at=1, sb=2, bt=3, xs=1), all-pairs demand; raising ONLY
    # w_sa 1->5: own-edge sa 5->2 (nonpositive, kept); cross-edge at
    # 3->2 DECREASES (abandoned route sheds with repriced edge --
    # sign-indefinite proven, unique shortest paths both ends, no
    # tie artifact) while sb 3->4 and bt 1->4 increase. So:
    # own-effect <=0 (fixed demand/normalization); cross-effects
    # unrestricted. "Fabric absorbs" / "higher beta needed" are
    # hypotheses, never corollaries.
    h = nx.Graph()
    h.add_edge("s", "a", w=1)
    h.add_edge("a", "t", w=1)
    h.add_edge("s", "b", w=2)
    h.add_edge("b", "t", w=3)
    h.add_edge("x", "s", w=1)

    def bet():
        return {tuple(sorted(e)): v for e, v in nx.edge_betweenness_centrality(h, weight="w", normalized=False).items()}

    b1 = bet()
    h["s"]["a"]["w"] = 5
    b5 = bet()
    assert (b1[("a", "s")], b5[("a", "s")]) == (5.0, 2.0)
    assert (b1[("a", "t")], b5[("a", "t")]) == (3.0, 2.0)
    assert (b1[("b", "s")], b5[("b", "s")]) == (3.0, 4.0)
    assert (b1[("b", "t")], b5[("b", "t")]) == (1.0, 4.0)


def test_betw_cong_closure():
    # Betw-cong closure (feedback w'=(1-a)w+a(1+b*chi(w)), chi =
    # weighted edge-betweenness recomputed every m ticks; alpha=0.2
    # beta=350). FULL-STATE verdict (40x40, 64 ticks, filed in
    # DEFERRED): feedback ATTENUATES toward the basin, both cadences
    # (m=1 weak_med 7.842 att 0.684; m=4 weak_med 6.913 att 0.591;
    # static 11.004) with fabric median UP (2.547/2.09 -- rerouted
    # load lands on fabric). m=1 (physical branch) IN basin:
    # endpoint (39,27,13,0) cross=3, basin-fraction 1.0 over 7 late
    # snaps; weak chi_med 0.0286->~0.019 by t=8 then flat, no
    # ringing; concave-D -5.00. m=4 OUT of basin ((39,26,13,1)/None,
    # basin-frac 0.0, residual 18.7 vs m=1's 9.3, ~150x noisier
    # weak-var) with overshoot+ring flapping = CADENCE ARTIFACT
    # (m/tau~1 ringing with stale chi; m=1 kills it). Rerouting map
    # (m=1): weak sheds (dchi_med -0.00634), fabric median flat
    # (-0.0002) with q90 tails gaining in ALL r_O bins (no gateway
    # pile-up), top gainers scattered far corridors (r_O 21-27).
    # STATIC-CHI CLOSED: no scale-separation mechanism in static chi
    # (2x2 collapse). REDUCED-STATE pins (12x12 ns=6 3x3-knot, 8
    # ticks): determinism bit-exact; embeddedness-control freezes
    # weak bit-exact; cadence checkpoint structure (m=1: 9, m=4:
    # 0/4/8); attenuation direction BOTH cadences (weak below,
    # fabric above the same-tick static run); R1 weak sheds both,
    # fabric median non-gaining both; concave-D <0 both; endpoint
    # Phi rows identical across cadences (m-agreement: cadence never
    # flips the qualitative answer at tame scale).
    import statistics as st

    from bh_graph.weighted import (
        edge_populations,
        feedback_trajectory,
        form1_trajectory,
        knot_block_mask,
        planted_knot_state,
        radial_eta_profile,
        weighted_edge_betweenness,
    )

    BINS = {"near": (0, 2), "mid": (3, 7), "far": (8, 10**9)}
    gw0, kn, gp0, _ = planted_knot_state(size=12, ns=6, seed=0, knot_center=(6, 6), knot_rad=1)
    pops = edge_populations(gw0, kn)
    key_of = {tuple(sorted(e)): e for e in gw0.edges()}
    w1 = dict.fromkeys([tuple(sorted(e)) for e in gw0.edges()], 1.0)

    def rows(wdict):
        gw = gw0.copy()
        nx.set_edge_attributes(gw, {key_of[e]: w for e, w in wdict.items()}, "L")
        gp = gp0.copy()
        out = []
        for k in range(4):
            pr = radial_eta_profile(gw, gp, knot_block_mask(kn, k), BINS)
            nV = sum(pr["bins"][b]["n_viol"] for b in BINS)
            nL = sum(pr["bins"][b]["n_longs"] for b in BINS)
            out.append((nV, nL))
            gw, gp = block_coarsen(gw), block_coarsen(gp)
        return out

    # mechanics: determinism + control freeze + cadence structure
    traj_a, _ = feedback_trajectory(gw0, kind="betweenness", beta=350.0, n_ticks=8, m=1)
    traj_b, _ = feedback_trajectory(gw0, kind="betweenness", beta=350.0, n_ticks=8, m=1)
    assert max(abs(traj_a[t][e] - traj_b[t][e]) for t in range(9) for e in traj_a[0]) == 0.0
    traj_c, _ = feedback_trajectory(gw0, kind="embeddedness", beta=1.0, n_ticks=8)
    assert max(abs(traj_c[t][e] - 1.0) for t in range(9) for e in pops["weak"]) == 0.0
    _, chist1 = feedback_trajectory(gw0, kind="betweenness", beta=350.0, n_ticks=8, m=1)
    _, chist4 = feedback_trajectory(gw0, kind="betweenness", beta=350.0, n_ticks=8, m=4)
    assert [t for t, _ in chist1] == list(range(9))
    assert [t for t, _ in chist4] == [0, 4, 8]

    # qualitative: attenuation direction vs same-tick static run
    chi0 = weighted_edge_betweenness(gw0, w1)
    traj_s, _ = form1_trajectory(chi0, alpha=0.2, beta=350.0, n_ticks=8)
    sw = st.median(traj_s[-1][e] for e in pops["weak"])
    sf = st.median(traj_s[-1][e] for e in pops["fabric"])
    assert abs(sw - 16.32) < 0.05 and abs(sf - 6.32) < 0.05, (sw, sf)
    for m, (ew, ef) in ((1, (13.03, 7.82)), (4, (8.69, 6.55))):
        traj, chist = feedback_trajectory(gw0, kind="betweenness", beta=350.0, n_ticks=8, m=m)
        wfin = traj[-1]
        _, chiF = chist[-1]
        mw = st.median(wfin[e] for e in pops["weak"])
        mf = st.median(wfin[e] for e in pops["fabric"])
        assert abs(mw - ew) < 0.05 and abs(mf - ef) < 0.05, (m, mw, mf)
        assert mw < sw and mf > sf, (m, mw, sw, mf, sf)
        dw = st.median([chiF[e] - chi0[e] for e in pops["weak"]])
        df = st.median([chiF[e] - chi0[e] for e in pops["fabric"]])
        assert dw < -1e-3 and df < 1e-3, (m, dw, df)
        dot = sum((chiF[e] - chi0[e]) * (wfin[e] - 1.0) for e in wfin)
        assert dot < -1.0, (m, dot)

    # basin outcome identical across cadences at tame scale
    assert rows(traj_a[0]) == [(8, 8), (5, 5), (1, 1), (1, 1)]
    healed = [(0, 8), (0, 5), (0, 1), (0, 1)]
    assert rows(traj_s[-1]) == healed
    assert rows(traj_a[-1]) == healed
    traj4, _ = feedback_trajectory(gw0, kind="betweenness", beta=350.0, n_ticks=8, m=4)
    assert rows(traj4[-1]) == healed


def test_gain_free_discriminator():
    # Gain-free discriminator (zero-free-parameter pricing w =
    # max(1, J/Jbar), J = static betweenness, Jbar over
    # non-interior edges; full 40x40 state, ~7s). VERDICT: FAILS
    # (rows (39,30,20,4)/None — no TOL crossing) => debt
    # CONFIRMED per pre-registered interpretation (basin reach
    # needs nonlinearity/gain = named debt; YES prong stays
    # logically open but its natural structural candidate fails;
    # formation/topology inherits). Numbers: Jbar 0.004598,
    # weak_med 6.216 (= chi_med/Jbar — median weak edge priced
    # purely by traffic ratio), fab_med EXACTLY 1.0 (median
    # fabric below mean, clipped to the ontological floor),
    # max_w 11.707 (hierarchy PEAK reaches static-beta=350
    # median scale ~11 — right order at top, insufficient mass
    # at median). DOSE-RESPONSE (secondary product): rows sit
    # strictly between the locked static brackets at every k
    # (beta=35 weak_med 2.0: (40,34,29,17)/None; beta=350
    # weak_med 11.0: (36,23,7,0)/cross=3) — Phi rows monotone
    # in weak_med across three points, narrowing the indicative
    # basin-entry threshold to (6.2,11.0) (shape-transfer
    # approximate: clipped-ratio vs affine).
    import statistics as st

    from bh_graph.weighted import (
        edge_chi,
        edge_populations,
        knot_block_mask,
        planted_knot_state,
        radial_eta_profile,
    )

    TOL = 2 / 760
    BINS = {"near": (0, 2), "mid": (3, 7), "far": (8, 10**9)}
    gw0, kn, gp0, _ = planted_knot_state()
    pops = edge_populations(gw0, kn)
    key_of = {tuple(sorted(e)): e for e in gw0.edges()}
    chi = edge_chi(gw0, "betweenness")

    pool = [chi[e] for e in pops["weak"]] + [chi[e] for e in pops["fabric"]]
    jbar = sum(pool) / len(pool)
    assert abs(jbar - 0.004598) < 1e-6, jbar
    w = {e: max(1.0, chi[e] / jbar) for e in chi}
    mw = st.median(w[e] for e in pops["weak"])
    mf = st.median(w[e] for e in pops["fabric"])
    assert abs(mw - 6.2163) < 1e-3 and mf == 1.0, (mw, mf)
    assert min(w.values()) == 1.0
    assert abs(max(w.values()) - 11.7066) < 1e-3
    assert 2.00 < mw < 11.00  # locked static brackets (MEDS table)

    gw = gw0.copy()
    nx.set_edge_attributes(gw, {key_of[e]: v for e, v in w.items()}, "L")
    gp = gp0.copy()
    rows, cross = [], None
    for k in range(4):
        pr = radial_eta_profile(gw, gp, knot_block_mask(kn, k), BINS)
        nV = sum(pr["bins"][b]["n_viol"] for b in BINS)
        nL = sum(pr["bins"][b]["n_longs"] for b in BINS)
        rows.append((nV, nL))
        if nV / gw.number_of_edges() <= TOL and cross is None:
            cross = k
        gw, gp = block_coarsen(gw), block_coarsen(gp)
    assert rows == [(39, 40), (30, 35), (20, 30), (4, 18)] and cross is None
    lo = [(36, 40), (23, 35), (7, 30), (0, 18)]  # beta=350 (heals)
    hi = [(40, 40), (34, 35), (29, 30), (17, 18)]  # beta=35 (fails)
    for k in range(4):
        assert lo[k][0] < rows[k][0] < hi[k][0], (k, rows[k])
