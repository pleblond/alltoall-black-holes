"""Candidate graph-update rules U: G_n -> G_{n+1} + falsifier harness (D1).

D1 provides U; everything downstream (stability tournament, healing
battery, D13 stages) consumes it. This module hosts the harness
(locality functional, damage injection, evolve loop) plus the first
three rules: null (harness validation), scramble (negative control:
locality death), and twin-targeted greedy (existence probe: is there
ANY local-move path back to the vacuum basin? -- uses a global target
and is NOT a local rule, honest label).
"""
from __future__ import annotations

import random

import networkx as nx
import numpy as np


def locality_p(g: nx.Graph, src: int, lo: int = 4, hi: int = 10) -> float:
    """Locality functional: window-p of ball growth from src (frozen rule)."""
    d = dict(nx.single_source_shortest_path_length(g, src))
    sh = np.array([sum(1 for x in d if d[x] == r) for r in range(hi + 1)], dtype=float)
    vo = np.cumsum(sh)
    rr = np.arange(hi + 1, dtype=float)
    m = rr >= lo
    p, _ = np.polyfit(np.log(rr[m]), np.log(vo[m]), 1)
    return float(p)


def inject_shortcuts(g: nx.Graph, n_swaps: int, seed: int = 0) -> nx.Graph:
    """Damage: n_swaps random degree-preserving double-edge swaps (seeded)."""
    rng = random.Random(seed)
    h = g.copy()
    E = list(h.edges())
    m = len(E)
    for _ in range(n_swaps):
        i, j = rng.sample(range(m), 2)
        (a, b), (c, dd) = E[i], E[j]
        if len({a, b, c, dd}) < 4:
            continue
        if h.has_edge(a, dd) or h.has_edge(c, b):
            continue
        h.remove_edge(a, b)
        h.remove_edge(c, dd)
        h.add_edge(a, dd)
        h.add_edge(c, b)
        E[i], E[j] = (a, dd), (c, b)
    return h


def _try_swap(h: nx.Graph, E: list, m: int, rng: random.Random):
    i, j = rng.sample(range(m), 2)
    (a, b), (c, dd) = E[i], E[j]
    if len({a, b, c, dd}) < 4:
        return None
    if h.has_edge(a, dd) or h.has_edge(c, b):
        return None
    return (i, j, a, b, c, dd)


def rule_null(h: nx.Graph, ctx: dict) -> bool:
    """Identity: damage persists bit-identically (harness validation)."""
    return False


def rule_scramble(h: nx.Graph, ctx: dict) -> bool:
    """Random rewiring: expect locality death (negative control)."""
    E = list(h.edges())
    m = len(E)
    for _ in range(ctx["swaps_per_step"]):
        s = _try_swap(h, E, m, ctx["rng"])
        if s is None:
            continue
        i, j, a, b, c, dd = s
        h.remove_edge(a, b)
        h.remove_edge(c, dd)
        h.add_edge(a, dd)
        h.add_edge(c, b)
        E[i], E[j] = (a, dd), (c, b)
    return True


def rule_greedy_heal(h: nx.Graph, ctx: dict) -> bool:
    """Twin-targeted greedy: accept first swap reducing |p - target|.

    Existence probe, NOT a local rule (global target + global evals).
    Answers: does a local-move descent path back to the basin exist?
    """
    cur = locality_p(h, ctx["src"])
    E = list(h.edges())
    m = len(E)
    for _ in range(ctx["proposals"]):
        s = _try_swap(h, E, m, ctx["rng"])
        if s is None:
            continue
        _, _, a, b, c, dd = s
        h.remove_edge(a, b)
        h.remove_edge(c, dd)
        h.add_edge(a, dd)
        h.add_edge(c, b)
        if abs(locality_p(h, ctx["src"]) - ctx["target"]) < abs(cur - ctx["target"]):
            return True
        h.remove_edge(a, dd)
        h.remove_edge(c, b)
        h.add_edge(a, b)
        h.add_edge(c, dd)
    return False


def evolve(
    g0: nx.Graph,
    rule,
    steps: int,
    seed: int = 0,
    src: int | None = None,
    target: float | None = None,
    proposals: int = 50,
    swaps_per_step: int = 4,
    T0: float = 2.0,
    Tend: float = 0.05,
    radius: int = 3,
    max_span: int = 3,
) -> tuple[list[float], nx.Graph, int]:
    """Run rule for steps; return (p-trajectory, final graph, accepted)."""
    if src is None:
        src = next(iter(g0.nodes()))
    h = g0.copy()
    ctx = {"rng": random.Random(seed), "src": src, "target": target,
           "proposals": proposals, "swaps_per_step": swaps_per_step,
           "T0": T0, "Tend": Tend, "total": steps,
           "radius": radius, "max_span": max_span}
    traj, acc = [], 0
    for s in range(steps):
        ctx["step"] = s
        acc += rule(h, ctx)
        traj.append(locality_p(h, src))
    return traj, h, acc


def edge_span(h: nx.Graph, u, v, radius: int = 3) -> int:
    """Shortest u-v path avoiding the direct edge, searched to depth radius.

    Returns radius+1 when no alternative path is found within radius
    (treated as "long"). Strictly radius-ball local.
    """
    seen = {u}
    frontier = [u]
    for depth in range(1, radius + 1):
        nxt = []
        for x in frontier:
            for y in h[x]:
                if (x == u and y == v) or (x == v and y == u):
                    continue
                if y == v:
                    return depth
                if y not in seen:
                    seen.add(y)
                    nxt.append(y)
        frontier = nxt
    return radius + 1


def rule_guillotine(h: nx.Graph, ctx: dict) -> bool:
    """Local shortcut guillotine: rewire edges with span > max_span.

    Genuinely local: detection (BFS within radius of the edge) and repair
    (swap with a sampled partner, accepted only if both new edges are
    short) use span evals that are each radius-ball local; partner
    sampling is global-uniform with long-edge preference (documented mild
    globality). Long-edge count decreases monotonically, so it terminates
    with zero long edges (inverse swaps always qualify). Plain grid is an
    automatic fixed point (every edge spans exactly 3). Threshold is
    fabric-relative (grid 3, triangular/Delaunay 2, hex 5).
    """
    radius = ctx.get("radius", 3)
    smax = ctx.get("max_span", 3)
    E = list(h.edges())
    m = len(E)
    for _ in range(ctx.get("proposals", 40)):
        i = ctx["rng"].randrange(m)
        a, b = E[i]
        if edge_span(h, a, b, radius) <= smax:
            continue
        cands = []
        for _ in range(60):
            x, y = E[ctx["rng"].randrange(m)]
            if len({a, b, x, y}) < 4:
                continue
            if (x, y) in cands or (y, x) in cands:
                continue
            cands.append((x, y))
        cands.sort(key=lambda e: edge_span(h, e[0], e[1], radius), reverse=True)
        for x, y in cands:
            for (u1, v1), (u2, v2) in (((a, x), (b, y)), ((a, y), (b, x))):
                if h.has_edge(u1, v1) or h.has_edge(u2, v2):
                    continue
                h.remove_edge(a, b)
                h.remove_edge(x, y)
                h.add_edge(u1, v1)
                h.add_edge(u2, v2)
                if edge_span(h, u1, v1, radius) <= smax and edge_span(h, u2, v2, radius) <= smax:
                    return True
                h.remove_edge(u1, v1)
                h.remove_edge(u2, v2)
                h.add_edge(a, b)
                h.add_edge(x, y)
    return False


def _first_neutral_move(h: nx.Graph, ctx: dict):
    """Scan for the first swap not growing local longs; None if none found."""
    radius = ctx.get("radius", 3)
    smax = ctx.get("max_span", 3)
    E = list(h.edges())
    m = len(E)
    for _ in range(ctx.get("proposals", 40)):
        i = ctx["rng"].randrange(m)
        a, b = E[i]
        if edge_span(h, a, b, radius) <= smax:
            continue
        cands = []
        for _ in range(60):
            x, y = E[ctx["rng"].randrange(m)]
            if len({a, b, x, y}) < 4:
                continue
            if (x, y) in cands or (y, x) in cands:
                continue
            cands.append((x, y))
        cands.sort(key=lambda e: edge_span(h, e[0], e[1], radius), reverse=True)
        for x, y in cands:
            old = (edge_span(h, a, b, radius) > smax) + (edge_span(h, x, y, radius) > smax)
            for (u1, v1), (u2, v2) in (((a, x), (b, y)), ((a, y), (b, x))):
                if h.has_edge(u1, v1) or h.has_edge(u2, v2):
                    continue
                h.remove_edge(a, b)
                h.remove_edge(x, y)
                h.add_edge(u1, v1)
                h.add_edge(u2, v2)
                new = (edge_span(h, u1, v1, radius) > smax) + (edge_span(h, u2, v2, radius) > smax)
                h.remove_edge(u1, v1)
                h.remove_edge(u2, v2)
                h.add_edge(a, b)
                h.add_edge(x, y)
                if new <= old:
                    return (a, b, x, y, u1, v1, u2, v2)
    return None


def _apply(h, mv):
    a, b, x, y, u1, v1, u2, v2 = mv
    h.remove_edge(a, b)
    h.remove_edge(x, y)
    h.add_edge(u1, v1)
    h.add_edge(u2, v2)


def _revert(h, mv):
    a, b, x, y, u1, v1, u2, v2 = mv
    h.remove_edge(u1, v1)
    h.remove_edge(u2, v2)
    h.add_edge(a, b)
    h.add_edge(x, y)


def total_longs(h: nx.Graph, radius: int = 3, smax: int = 3) -> int:
    """Global census: edges with span > smax (the honest health stat)."""
    return sum(1 for u, v in h.edges() if edge_span(h, u, v, radius) > smax)


def rule_drift(h: nx.Graph, ctx: dict) -> bool:
    """Neutral-tolerant long-count descent: apply first non-growing move.

    Strict guillotine stalls on locked configs; allowing neutral moves
    was meant to cross plateaus -- measured WORSE (longs leak globally
    through detour rerouting). Kept as the documented failure: local
    delta does not bound global longs. See rule_anneal for the census
    gate that fixes the leak.
    """
    mv = _first_neutral_move(h, ctx)
    if mv is None:
        return False
    _apply(h, mv)
    return True


def rule_anneal(h: nx.Graph, ctx: dict) -> bool:
    """Census-gated annealing on global long-count (stochastic U).

    TARGETED proposals (long-first scan) + global-census acceptance:
    keep iff census doesn't grow, or uphill with prob exp(-dT/T) on a
    geometric schedule. Targeting is load-bearing -- blind (uniform
    random) proposals stall greedy at 29 longs and explode to 101 under
    T0=5 (measured, not shipped): proposals matter more than acceptance.
    """
    import math

    mv = _first_neutral_move(h, ctx)
    if mv is None:
        return False
    radius = ctx.get("radius", 3)
    smax = ctx.get("max_span", 3)
    before = total_longs(h, radius, smax)
    _apply(h, mv)
    after = total_longs(h, radius, smax)
    d = after - before
    if d <= 0:
        return True
    frac = ctx.get("step", 0) / max(ctx.get("total", 1), 1)
    T0 = ctx.get("T0", 2.0)
    T = T0 * (ctx.get("Tend", 0.05) / T0) ** frac if T0 > 0 else 0.0
    if T > 0 and ctx["rng"].random() < math.exp(-d / T):
        return True
    _revert(h, mv)
    return False


def rule_slide(h: nx.Graph, ctx: dict) -> bool:
    """Edge-slide reel-in: slide a long edge's endpoint toward shorter span.

    New move class beyond swaps: pick (a,b) with span > smax, try sliding
    each endpoint along its neighbors ((a,b) -> (a,w), w in N(b)), accept
    the first strictly span-reducing slide that keeps degrees >= 2 and
    the graph connected. Total edges fixed; degrees drift (documented:
    weaker conservation than swaps). Reel-in can reach what swaps can't.
    """
    radius = ctx.get("radius", 3)
    smax = ctx.get("max_span", 3)
    E = list(h.edges())
    m = len(E)
    for _ in range(ctx.get("proposals", 40)):
        a, b = E[ctx["rng"].randrange(m)]
        sab = edge_span(h, a, b, radius)
        if sab <= smax:
            continue
        for (u, v) in ((a, b), (b, a)):
            nbrs = list(h[v])
            ctx["rng"].shuffle(nbrs)
            for w in nbrs:
                if w == u or h.has_edge(u, w):
                    continue
                if h.degree(v) - 1 < 2 or h.degree(u) < 2:
                    continue
                h.remove_edge(u, v)
                h.add_edge(u, w)
                if edge_span(h, u, w, radius) < sab and nx.is_connected(h):
                    return True
                h.remove_edge(u, w)
                h.add_edge(u, v)
    return False
