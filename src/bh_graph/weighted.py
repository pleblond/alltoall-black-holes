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
