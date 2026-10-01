"""J2 micro/macro probe (D'Ariano-Erba-Perinotti substrate, NOT Tier-1-track).

Pre-registered as a probe per the standing no-new-statics direction: J2 is
QI to the square lattice (index-2), so long-scale d=2 is a CONTROL (failure
would indict the apparatus); the live questions are micro-vs-coarse readout
tracking, the quotient check, and perturbation response vs the family.
One pre-registered micro-prediction (aperiodic walk) was FALSIFIED cleanly:
the parity argument was fallacious (a p-preserving edge is not an odd
cycle); the correct bipartition is q=x+y (every micro-move flips it), so J2
is BIPARTITE and odd returns vanish exactly like the square. Even-return
values and 4-cycle density track the MICRO level (degree 8, dense cycles).
Perturbation: family-typical (swap-fragile majority + deletion-robust).
"""
import random

import networkx as nx
import numpy as np

from bh_graph.graphs import build_j2_ball
from bh_graph.scrambling import hop_arrival_times


# Frozen family rule, duplicated VERBATIM from test_substrate_family (the
# rule must be identical for apples-to-apples; no cross-test imports exist).
def _shells_cuts_vols(g, src, rmax):
    d = hop_arrival_times(g, src)
    shells = [sum(1 for n in d if d[n] == r) for r in range(rmax + 1)]
    cuts = []
    for r in range(1, rmax + 1):
        disk = {n for n in d if d[n] <= r}
        cuts.append(sum(1 for u in disk for v in g[u] if v not in disk))
    return shells, cuts, np.cumsum(np.array(shells, dtype=float))


def _window_p(vols, lo, hi):
    rr = np.arange(len(vols), dtype=float)
    m = (rr >= lo) & (rr <= hi)
    p, _ = np.polyfit(np.log(rr[m]), np.log(vols[m]), 1)
    return p


_J2_ALL_GENS = (
    (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0),
    (1, 0, 1), (-1, 0, 1), (0, 1, 1), (0, -1, 1),
)


def _quotient(g):
    """Two-cell quotient: (cells, quotient graph, per-coarse-edge micro counts)."""
    cells = {}
    for (x, y, b) in g.nodes():
        cells.setdefault((x, y), []).append(b)
    q = nx.Graph()
    q.add_nodes_from(cells)
    mult = {}
    for (u, v) in g.edges():
        cu, cv = (u[0], u[1]), (v[0], v[1])
        if cu != cv:
            q.add_edge(cu, cv)
            e = (cu, cv) if cu < cv else (cv, cu)
            mult[e] = mult.get(e, 0) + 1
    return cells, q, mult


def _strict_interior(g, cells):
    """Cells with both sheets + all 16 micro-neighbor slots present."""
    out = []
    for c, bs in cells.items():
        if sorted(bs) != [0, 1]:
            continue
        ok = True
        for b in (0, 1):
            for (u, v, dd) in _J2_ALL_GENS:
                a1, a2 = (u, v) if b == 0 else (v, u)
                if (c[0] + a1, c[1] + a2, (b + dd) % 2) not in g:
                    ok = False
        if ok:
            out.append(c)
    return out


def _return_probs(h, s, nmax):
    """Exact vertex return probs p_1..p_nmax at s (dict propagation, unweighted)."""
    nbrs = {n: list(h.neighbors(n)) for n in h.nodes()}
    dist = {s: 1.0}
    out = []
    for _ in range(nmax):
        nd = {}
        for n, p in dist.items():
            share = p / len(nbrs[n])
            for w in nbrs[n]:
                nd[w] = nd.get(w, 0.0) + share
        dist = nd
        out.append(dist.get(s, 0.0))
    return out


def _c4count(h):
    """4-cycle census via tr(A^4): C4 = (tr - sum d(2d-1))/8 (exact ints)."""
    nodes = list(h.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    A = np.zeros((len(nodes), len(nodes)), dtype=np.int64)
    for u, v in h.edges():
        A[idx[u], idx[v]] = 1
        A[idx[v], idx[u]] = 1
    t4 = int(np.trace(A @ A @ A @ A))
    deg = np.array([dd for _, dd in h.degree()], dtype=np.int64)
    return (t4 - int(np.sum(deg * (2 * deg - 1)))) // 8


def test_j2_construction_and_quotient():
    # Constructor: R30 ball N=3722/E=14400 (exact, deterministic),
    # connected, max degree 8, root degree 8; R0 = singleton.
    # Quotient: 1861 cells/3600 edges; EVERY quotient edge is
    # square-adjacent (global structural pin — no diagonal coarse
    # edges anywhere); 1741 strict-interior cells each with exactly
    # the 4 square neighbors and micro-multiplicity exactly 4 per
    # coarse edge (hand-verification reproduced computationally);
    # quotient shells exactly 4r (r=1..20) — the quotient IS square.
    g = build_j2_ball(30)
    assert g.number_of_nodes() == 3722
    assert g.number_of_edges() == 14400
    assert nx.is_connected(g)
    assert max(d for _, d in g.degree()) == 8
    assert g.degree((0, 0, 0)) == 8
    g0 = build_j2_ball(0)
    assert g0.number_of_nodes() == 1 and g0.number_of_edges() == 0
    try:
        build_j2_ball(-1)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass

    cells, q, mult = _quotient(g)
    assert q.number_of_nodes() == 1861 and q.number_of_edges() == 3600
    for a, b in q.edges():
        assert abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1, (a, b)
    interior = _strict_interior(g, cells)
    assert len(interior) == 1741
    for c in interior:
        exp = {(c[0] + 1, c[1]), (c[0] - 1, c[1]), (c[0], c[1] + 1), (c[0], c[1] - 1)}
        assert set(q.neighbors(c)) == exp, c
        for e in exp:
            k = (c, e) if c < e else (e, c)
            assert mult[k] == 4, (c, e, mult[k])
    dq = hop_arrival_times(q, (0, 0))
    shq = [sum(1 for n in dq if dq[n] == r) for r in range(21)]
    for r in range(1, 21):
        assert shq[r] == 4 * r, (r, shq[r])


def test_j2_volume_control():
    # QI control (must read d=2 — failure would indict the apparatus):
    # shells exactly 8/17/8r (r=1/2/3..22), p[8,20] = 1.9205 in band,
    # fractional-window approach 1.84 -> 1.89 -> 1.92 (tri/hex pattern),
    # quotient p agrees to 0.0000 (Δp bound 0.15, huge margin), cuts
    # exactly 32r+16 (r=2..22; r=1 is 56) — J2's cut law, the analog
    # of square 8r+4 / tri 12r+6 (prefactor non-universal, filed).
    g = build_j2_ball(30)
    src = (0, 0, 0)
    shells, cuts, vols = _shells_cuts_vols(g, src, 22)
    assert shells[1] == 8 and shells[2] == 17
    for r in range(3, 23):
        assert shells[r] == 8 * r, (r, shells[r])
    assert vols[22] == 2026
    p = _window_p(vols, 8, 20)
    assert 1.90 < p < 1.94, p
    ps = []
    for R, lo, hi, plo, phi in (
        (20, 4, 10, 1.82, 1.86), (30, 6, 15, 1.88, 1.91), (40, 8, 20, 1.91, 1.94),
    ):
        gR = build_j2_ball(R)
        _, _, volsR = _shells_cuts_vols(gR, src, hi)
        pr = _window_p(volsR, lo, hi)
        assert plo < pr < phi, (R, pr)
        ps.append(pr)
    assert ps[0] < ps[1] < ps[2], ps
    _, q, _ = _quotient(g)
    dq = hop_arrival_times(q, (0, 0))
    shq = [sum(1 for n in dq if dq[n] == r) for r in range(19)]
    pq = _window_p(np.cumsum(np.array(shq, dtype=float)), 8, 18)
    assert 1.90 < pq < 1.94, pq
    assert abs(_window_p(vols, 8, 18) - pq) < 0.15
    assert cuts[0] == 56
    for r in range(2, 23):
        assert cuts[r - 1] == 32 * r + 16, (r, cuts[r - 1])


def test_j2_walk_parity_and_degree():
    # FALSIFIED-then-reframed leg: the pre-registered aperiodic-walk
    # prediction was WRONG (logic erratum: a p-preserving edge is not
    # an odd cycle; correct bipartition q=x+y — every micro-move flips
    # it — so J2 IS bipartite). Odd returns vanish EXACTLY like the
    # square (parity pattern = coarse-matching); even VALUES track the
    # micro degree (p2 = 1/8 vs square 1/4 exactly; p4+ pinned tight).
    g = build_j2_ball(30)
    pj = _return_probs(g, (0, 0, 0), 12)
    for n in (1, 3, 5, 7, 9, 11):
        assert pj[n - 1] == 0.0, (n, pj[n - 1])
    assert pj[1] == 0.125
    for got, exp in zip((pj[3], pj[5], pj[7], pj[9], pj[11]),
                        (0.070312, 0.048828, 0.037384, 0.030281, 0.025445)):
        assert abs(got - exp) < 1e-6, (got, exp)
    sq = nx.grid_2d_graph(41, 41)
    ps = _return_probs(sq, (20, 20), 12)
    for n in (1, 3, 5, 7, 9, 11):
        assert ps[n - 1] == 0.0, (n, ps[n - 1])
    assert ps[1] == 0.25


def test_j2_four_cycle_census():
    # Census apparatus validated exactly (square LxL -> (L-1)^2);
    # J2 R18 (N=1370): C4 = 26072 (exact regression) — ~20x the
    # square-equivalent density at same N (~1300): 4-cycle density
    # tracks MICRO (sheet-mixing cycles), characterization pinned.
    assert _c4count(nx.grid_2d_graph(5, 5)) == 16
    assert _c4count(nx.grid_2d_graph(10, 10)) == 81
    g18 = build_j2_ball(18)
    assert g18.number_of_nodes() == 1370
    assert _c4count(g18) == 26072


def test_j2_perturbation_matches_family():
    # THE discriminator: swap-fragility (ns=20, 3 seeds) kills 2/3
    # (2.49/2.60/2.16 — seed2 = documented lottery miss, Delaunay
    # stream-1 precedent) with all streams in loose (2.0,2.9) and
    # mean rise > +0.2; q=0.05 deletion keeps p in (1.90,1.94)
    # both seeds (deletion-robust). Family-typical both legs:
    # perturbation response tracks the FAMILY envelope (no surprise
    # => no discovery-route tier claim; probe verdict stands).
    g = build_j2_ball(30)
    src = (0, 0, 0)
    _, _, vols0 = _shells_cuts_vols(g, src, 22)
    p0 = _window_p(vols0, 8, 20)
    ps = []
    for seed in (0, 1, 2):
        h = g.copy()
        nx.connected_double_edge_swap(h, 20, seed=seed)
        assert nx.is_connected(h)
        _, _, vols = _shells_cuts_vols(h, src, 22)
        ph = _window_p(vols, 8, 20)
        assert 2.0 < ph < 2.9, (seed, ph)
        ps.append(ph)
    assert sum(1 for ph in ps if ph > 2.2) >= 2, ps
    assert sum(ps) / 3 > p0 + 0.2, (ps, p0)
    for seed in (0, 1):
        rng = random.Random(seed)
        h = g.copy()
        h.remove_edges_from(rng.sample(list(h.edges()), int(0.05 * h.number_of_edges())))
        assert nx.is_connected(h)
        _, _, vols = _shells_cuts_vols(h, src, 22)
        pq = _window_p(vols, 8, 20)
        assert 1.90 < pq < 1.94, (seed, pq)
