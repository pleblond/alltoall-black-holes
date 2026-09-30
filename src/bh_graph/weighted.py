"""Weighted-graph audit: arrival-event volume comparison + edge-cost census.

Adopts the reference-based audit of Leblond, "Distance, Volume, and
Apparent Dimension in Weighted Graphs" (pleblond/weighted-graph-paper):
- Prop 1 (cost dominance -- generalizes our T15): d_w >= d_0 pointwise
  iff every edge costs >= its reference endpoint distance; each
  underpriced edge is an endpoint witness (our witness-node corollary).
- Prop 2 (critical-radius sufficiency): comparing V_w vs V_0 at the
  UNION of arrival radii certifies volume domination over every radius.
  Coarse grids (integer radii, linspace -- cf. ball_volumes_weighted)
  can miss every witness (paper Sec 4.1 + grid 7.67% excess; our T15
  fractional blips are instances of the same phenomenon).
- Slope identities (Eq 15/17): p_w - p_0 is the slope of the log volume
  ratio -- slope excess is ratio-recovery, not inflation (D11-tail
  re-analysis queued under this lens).

Conventions: counting measure, center included, closed balls (match
emergent_dim). Both distance dicts must cover the same connected vertex
set with the center at 0. Ties group by exact float equality -- no
tolerance merging (per paper Sec 4.3, merging can delete the interval
under investigation).
"""
from __future__ import annotations

import networkx as nx


def arrival_profile(d0: dict, dw: dict) -> list:
    """Algorithm 1 (event sweep): (r, V0, Vw, delta, ratio) per event radius.

    Events are the union of reference + candidate arrival radii with
    tied arrivals grouped (masses added before the record is taken, so
    each record holds until the next distinct radius).
    """
    masses: dict[float, list] = {}
    for r in d0.values():
        masses.setdefault(float(r), [0, 0])[0] += 1
    for r in dw.values():
        masses.setdefault(float(r), [0, 0])[1] += 1
    out = []
    v0 = vw = 0
    for r in sorted(masses):
        m0, mw = masses[r]
        v0 += m0
        vw += mw
        out.append((r, v0, vw, vw - v0, vw / v0))
    return out


def volume_comparison(d0: dict, dw: dict) -> dict:
    """Full audit: profile + max ratio + positive-volume intervals.

    Positive intervals are merged maximal [start, end) spans with
    delta > 0. The last record always has delta 0 (both saturated at
    N), so intervals close. Max ratio is exact on the event set.
    """
    prof = arrival_profile(d0, dw)
    maxrec = max(prof, key=lambda rec: rec[4])
    intervals = []
    start = None
    for r, _v0, _vw, d, _rt in prof:
        if d > 0 and start is None:
            start = r
        if d <= 0 and start is not None:
            intervals.append((start, r))
            start = None
    return {
        "profile": prof,
        "max_ratio": maxrec[4],
        "max_ratio_radius": maxrec[0],
        "positive_intervals": intervals,
        "n_events": len(prof),
    }


def _edge_cost(h: nx.Graph, u, v, weight) -> float:
    if weight is None:
        return 1.0
    if callable(weight):
        return float(weight(u, v, h[u][v]))
    return float(h[u][v].get(weight, 1.0))


def underpriced_census(h: nx.Graph, d0_allpairs: dict, weight=None) -> list:
    """Prop 1 census: edges with w_uv < d_0(u,v), with margins.

    Each entry (u, v, w, d0) is an endpoint witness: v arrives at u
    strictly early (d_w(u,v) <= w < d_0(u,v)), breaking ball inclusion
    at radius w. Empty census certifies pointwise metric domination
    (hence ball inclusion + volume domination everywhere). d0_allpairs
    is node -> {node: distance}, e.g. from all_pairs_shortest_path.
    """
    out = []
    for u, v in h.edges():
        w = _edge_cost(h, u, v, weight)
        r = float(d0_allpairs[u][v])
        if w < r:
            out.append((u, v, w, r))
    return out


def block_coarsen(g: nx.Graph, rule: str = "min") -> nx.Graph:
    """2x2 block coarse-graining with weighted multi-edge merger (tuple grid).

    Same blocking as the binary RG study (coords //2, self-loops drop);
    merged multi-edges combine lengths by rule: "min" (transport-
    faithful: parallel paths, best wins — FROZEN by pilot) or "mean".
    Length attr "L" (default 1.0). Rule "min" keeps fabric fidelity
    1.000 where "mean" smears to 0.900 by level 3 (pinned pilot).
    """
    h = nx.Graph()
    acc: dict = {}
    for u, v, d in g.edges(data=True):
        a = (u[0] // 2, u[1] // 2)
        b = (v[0] // 2, v[1] // 2)
        if a == b:
            continue
        e = (a, b) if a < b else (b, a)
        acc.setdefault(e, []).append(float(d.get("L", 1.0)))
    for e, ws in acc.items():
        h.add_edge(*e, L=(min(ws) if rule == "min" else sum(ws) / len(ws)))
    return h


def _manhattan(a, b) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def long_fraction(g: nx.Graph) -> float:
    """Fraction of edges spanning >1 Manhattan unit (shortcut density)."""
    edges = list(g.edges())
    return sum(1 for a, b in edges if _manhattan(a, b) > 1) / len(edges)


def excess_stats(g: nx.Graph) -> dict:
    """(lambda, ebar, elong, fabfid) flow variables for weighted RG.

    lambda = long-edge fraction; ebar = mean excess (L-1) over all
    edges; elong = mean excess over long edges (0.0 if none); fabfid
    = fraction of span-1 fabric edges with length exactly 1.0.
    """
    E = list(g.edges(data=True))
    lam = sum(1 for a, b, _d in E if _manhattan(a, b) > 1) / len(E)
    ebar = sum(d.get("L", 1.0) - 1 for _a, _b, d in E) / len(E)
    le = [d.get("L", 1.0) - 1 for a, b, d in E if _manhattan(a, b) > 1]
    fab = [(a, b, d) for a, b, d in E if _manhattan(a, b) == 1]
    fid = sum(1 for _a, _b, d in fab if d.get("L", 1.0) == 1.0) / max(len(fab), 1)
    return {"lambda": lam, "ebar": ebar, "elong": sum(le) / max(len(le), 1), "fabfid": fid}


def _long_records(gw: nx.Graph, gplain: nx.Graph):
    """(n_edges, [(u, v, L, d0-span)]) over span>1 edges; endpoint BFS."""
    E = list(gw.edges(data=True))
    longs = [(a, b, float(d.get("L", 1.0))) for a, b, d in E if _manhattan(a, b) > 1]
    if not longs:
        return len(E), []
    ends = {n for a, b, _ in longs for n in (a, b)}
    dist = {s: dict(nx.single_source_shortest_path_length(gplain, s)) for s in ends}
    return len(E), [(a, b, L, dist[a][b]) for a, b, L in longs]


def _long_prices_spans(gw: nx.Graph, gplain: nx.Graph):
    """Shared endpoint-BFS: (n_edges, [(L, d0-span)]) over long edges."""
    nE, recs = _long_records(gw, gplain)
    return nE, [(L, s) for _, _, L, s in recs]


def pricing_flow_stats(gw: nx.Graph, gplain: nx.Graph) -> dict:
    """(lambda, violfrac, marginratio) campaign flow variables.

    lambda = long-edge fraction (topological, Manhattan span > 1);
    violfrac = fraction of ALL edges underpriced (L < d_0 span on the
    co-blocked plain — Prop-1 violations per unit edge); marginratio =
    mean L/d_0 over long edges (1 = exactly priced; <1 under, >1
    over). d_0 comes from endpoint-only BFS on gplain (cheaper than
    all-pairs; longs are sparse). Length attr "L" (default 1.0).
    """
    nE, ps = _long_prices_spans(gw, gplain)
    lam = len(ps) / nE
    if not ps:
        return {"lambda": lam, "violfrac": 0.0, "marginratio": 1.0}
    viol = sum(1 for L, s in ps if L < s)
    mr = sum(L / s for L, s in ps) / len(ps)
    return {"lambda": lam, "violfrac": viol / nE, "marginratio": mr}


def phi_stats(gw: nx.Graph, gplain: nx.Graph) -> dict:
    """Phi-surface apparatus: P(eta>1) over longs + eta distribution.

    eta = d_0-span / L per long edge (shortcut relevance; >1 =
    operational shortcut). phi = fraction of LONGS violated (cf.
    violfrac = fraction of ALL edges; phi * lambda = violfrac).
    etas sorted ascending; mean_inv_eta = mean(L/d) = marginratio,
    kept alongside phi to exhibit distribution-vs-mean (mean can
    cross 1 while violations persist). Length attr "L" (default 1.0).
    """
    _nE, ps = _long_prices_spans(gw, gplain)
    if not ps:
        return {"phi": 0.0, "n_longs": 0, "n_viol": 0, "etas": [], "mean_inv_eta": 1.0}
    etas = sorted(s / L for L, s in ps)
    nviol = sum(1 for e in etas if e > 1)
    return {
        "phi": nviol / len(etas),
        "n_longs": len(etas),
        "n_viol": nviol,
        "etas": etas,
        "mean_inv_eta": sum(1 / e for e in etas) / len(etas),
    }


def knot_block_mask(knot_nodes, k: int) -> set:
    """Block-image of a planted knot mask after k 2x2 blocking levels."""
    f = 2**k
    return {(x // f, y // f) for x, y in knot_nodes}


def radial_eta_profile(gw: nx.Graph, gref: nx.Graph, knotmask, bins: dict) -> dict:
    """r_O-binned eta stats for the planted-knot pilot (frozen rule).

    r_O(x) = min d_ref(x, knotmask) via one super-node BFS on gref
    (the RULER graph -- background plain for eta_0, plain+knot for
    eta_K; weak links belong in NEITHER ruler). Longs with both
    endpoints in the mask are "interior" (excluded from weak bins);
    the rest bin by min endpoint r_O. Returns per-bin (n_longs,
    n_viol, phi), interior ditto, per-edge spans {(u,v): d_ref}
    (sorted keys; eta_K/eta_0 = d_K/d_0 per edge, L cancels),
    per-edge bin labels, and weak records [(u,v,L,span)].
    """
    h = gref.copy()
    h.add_node("SUPER")
    for z in knotmask:
        if z in h:
            h.add_edge("SUPER", z)
    dh = dict(nx.single_source_shortest_path_length(h, "SUPER"))
    r = {n: dh[n] - 1 for n in gref.nodes()}
    _, recs = _long_records(gw, gref)
    weak = [rc for rc in recs if not (rc[0] in knotmask and rc[1] in knotmask)]
    inter = [rc for rc in recs if rc[0] in knotmask and rc[1] in knotmask]
    out: dict = {"bins": {}, "interior": {}, "spans": {}, "bin_of": {}, "records": weak}
    for name, (lo, hi) in bins.items():
        sel = [(u, v, L, s) for u, v, L, s in weak if lo <= min(r[u], r[v]) <= hi]
        nv = sum(1 for _, _, L, s in sel if L < s)
        out["bins"][name] = {"n_longs": len(sel), "n_viol": nv, "phi": nv / max(len(sel), 1)}
        for u, v, _, _ in sel:
            out["bin_of"][tuple(sorted((u, v)))] = name
    nv = sum(1 for _, _, L, s in inter if L < s)
    out["interior"] = {"n_longs": len(inter), "n_viol": nv, "phi": nv / max(len(inter), 1)}
    for u, v, _, s in weak:
        out["spans"][tuple(sorted((u, v)))] = s
    return out


def edge_chi(g: nx.Graph, kind: str = "betweenness") -> dict:
    """Per-edge static chi {(u,v) sorted: value} (tuple grid).

    kinds: "embeddedness" (common-neighbor count), "jaccard",
    "degree_sum", "betweenness" (exact edge betweenness).
    """
    if kind == "betweenness":
        raw = nx.edge_betweenness_centrality(g)
        return {tuple(sorted(e)): val for e, val in raw.items()}
    if kind not in ("embeddedness", "jaccard", "degree_sum"):
        raise ValueError(f"unknown chi kind: {kind}")
    nbr = {n: set(g.neighbors(n)) for n in g.nodes()}
    out = {}
    for u, v in g.edges():
        e = tuple(sorted((u, v)))
        if kind == "embeddedness":
            out[e] = len(nbr[u] & nbr[v])
        elif kind == "jaccard":
            out[e] = len(nbr[u] & nbr[v]) / len(nbr[u] | nbr[v])
        else:
            out[e] = g.degree(u) + g.degree(v)
    return out


def population_chi(g: nx.Graph, knot_nodes, kind: str = "betweenness") -> dict:
    """Per-population static-chi table for experiment-A design (tuple grid).

    kinds: see edge_chi. Populations: "fabric" (span-1, non-interior),
    "weak" (span>1, non-interior), "interior" (both endpoints in
    knot_nodes). Returns {pop: [values]} in edge order.
    """
    knot_nodes = set(knot_nodes)
    tab = edge_chi(g, kind)
    pops: dict = {"fabric": [], "weak": [], "interior": []}
    for u, v in g.edges():
        if u in knot_nodes and v in knot_nodes:
            pop = "interior"
        elif _manhattan(u, v) > 1:
            pop = "weak"
        else:
            pop = "fabric"
        pops[pop].append(tab[tuple(sorted((u, v)))])
    return pops


def planted_knot_state(size=40, ns=20, seed=0, knot_center=(20, 20), knot_rad=2):
    """Canonical experiment-A state: grid + swaps + clique knot (topology).

    Returns (gw_topo, knot_nodes, gplain, gknot_ref): swapped grid with
    planted clique, planted node set, pure plain ruler, plain+knot
    ruler. Weights NOT set (w-dynamics runs from uniform 1).
    """
    gw = nx.grid_2d_graph(size, size)
    if ns:
        nx.connected_double_edge_swap(gw, ns, seed=seed)
    cx, cy = knot_center
    kn = {(x, y) for x in range(cx - knot_rad, cx + knot_rad + 1) for y in range(cy - knot_rad, cy + knot_rad + 1)}
    for a in kn:
        for b in kn:
            if a < b and not gw.has_edge(a, b):
                gw.add_edge(a, b)
    gk = nx.grid_2d_graph(size, size)
    for a in kn:
        for b in kn:
            if a < b and not gk.has_edge(a, b):
                gk.add_edge(a, b)
    return gw, kn, nx.grid_2d_graph(size, size), gk


def form1_trajectory(chi: dict, alpha=0.2, beta=350.0, n_ticks=64, w_init=1.0):
    """Form-1 relaxation w'=(1-a)w+a(1+b*chi) from uniform init.

    chi = {edge: value} (any hashable edge keys). Deterministic.
    Returns (trajectory [w0..wn] as list of dicts, w_star dict).
    """
    w = dict.fromkeys(chi, float(w_init))
    traj = [dict(w)]
    for _ in range(n_ticks):
        w = {e: (1 - alpha) * w[e] + alpha * (1 + beta * chi[e]) for e in chi}
        traj.append(dict(w))
    return traj, {e: 1 + beta * chi[e] for e in chi}


def fabric_price_profile(gw: nx.Graph, gref: nx.Graph, knotmask, bins: dict) -> dict:
    """Per-r_O-bin fabric-price stats {bin: (median, q90, n)} (prereg W).

    Fabric = span-1 non-interior edges; r(e) = min endpoint r_O via
    one super-node BFS on gref (same frozen rule as radial_eta).
    Length attr "L" (default 1.0). Median = halo detector, q90 =
    shell/tail detector.
    """
    import statistics as st

    h = gref.copy()
    h.add_node("SUPER")
    for z in knotmask:
        if z in h:
            h.add_edge("SUPER", z)
    dh = dict(nx.single_source_shortest_path_length(h, "SUPER"))
    r = {n: dh[n] - 1 for n in gref.nodes()}
    out = {}
    for name, (lo, hi) in bins.items():
        ws = sorted(
            float(d.get("L", 1.0))
            for u, v, d in gw.edges(data=True)
            if _manhattan(u, v) == 1
            and not (u in knotmask and v in knotmask)
            and lo <= min(r[u], r[v]) <= hi
        )
        q = st.quantiles(ws, n=10) if len(ws) >= 10 else [ws[-1]] * 9
        out[name] = (st.median(ws), q[8], len(ws)) if ws else (1.0, 1.0, 0)
    return out
