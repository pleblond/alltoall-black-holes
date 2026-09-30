"""Observer-blind candidate update rules U (D1 blind-U tournament).

Reframing (ADOPTED, DEFERRED D1): locality should characterize STABLE
STATES of U, not appear in U's objective function. U must not know M_O.
Every rule here satisfies the U-admissibility criteria:

  1. coordinate-free (no positions, dimensions, or embeddings referenced);
  2. permutation-equivariant (relabeling nodes changes nothing);
  3. observer-blind (no p, N_long, M_O, or reference graph in the rule);
  4. graph-local information (acceptance from touched neighborhoods only);
  5. stochasticity allowed (proposals are seeded-random);
  6. simplicity pre-registered (one motif + strict-greater + guard; the
     only parameter is the proposal budget, fixed before the tournament).

What each rule optimizes is a sum of graph-local motif terms -- a
legitimate local Hamiltonian, not an observer-relative order parameter.
p / N_long / d_I remain EXTERNAL diagnostics: measured by the harness
outside the rule, never consulted inside it. Damage recovery under a
blind rule (healing the rule cannot recognize) is the attractor
signature this tournament hunts.
"""
from __future__ import annotations

import networkx as nx


def _squares_touching(h: nx.Graph, S: set) -> set:
    """Canonical node-sets of 4-cycles touching S (graph-local)."""
    out = set()
    for s in S:
        nbrs = list(h[s])
        for i in range(len(nbrs)):
            for j in range(i + 1, len(nbrs)):
                for z in set(h[nbrs[i]]) & set(h[nbrs[j]]):
                    if z != s:
                        out.add(frozenset((s, nbrs[i], nbrs[j], z)))
    return out


def _tris_touching(h: nx.Graph, S: set) -> set:
    """Canonical node-sets of triangles touching S (graph-local)."""
    out = set()
    for s in S:
        nbrs = list(h[s])
        for i in range(len(nbrs)):
            for j in range(i + 1, len(nbrs)):
                if h.has_edge(nbrs[i], nbrs[j]):
                    out.add(frozenset((s, nbrs[i], nbrs[j])))
    return out


def nsquares(h: nx.Graph) -> int:
    """Global 4-cycle count (external diagnostic, not consulted by rules)."""
    n = 0
    for u, v in h.edges():
        Nv = set(h[v]) - {u}
        for x in set(h[u]) - {v}:
            n += len(set(h[x]) & Nv)
    return n // 4


def ntris(h: nx.Graph) -> int:
    """Global triangle count (external diagnostic, not consulted by rules)."""
    return sum(nx.triangles(h).values()) // 3


def _motif_rule(h: nx.Graph, ctx: dict, touch) -> bool:
    """Strict greedy hill-climb on a touched-set motif count.

    Propose random degree-preserving double-edge swaps; apply the first
    that strictly increases the motif count on the touched set and keeps
    the graph connected. Greedy (not Metropolis): stalls at local optima
    by design -- finite-T variants are queued, not shipped.
    """
    E = list(h.edges())
    for _ in range(ctx.get("proposals", 50)):
        (a, b), (c, d) = ctx["rng"].sample(E, 2)
        if len({a, b, c, d}) < 4:
            continue
        if ctx["rng"].random() < 0.5:
            (u1, v1), (u2, v2) = (a, d), (c, b)
        else:
            (u1, v1), (u2, v2) = (a, c), (b, d)
        if h.has_edge(u1, v1) or h.has_edge(u2, v2):
            continue
        S = {a, b, c, d}
        before = len(touch(h, S))
        h.remove_edge(a, b)
        h.remove_edge(c, d)
        h.add_edge(u1, v1)
        h.add_edge(u2, v2)
        if len(touch(h, S)) > before and nx.is_connected(h):
            return True
        h.remove_edge(u1, v1)
        h.remove_edge(u2, v2)
        h.add_edge(a, b)
        h.add_edge(c, d)
    return False


def rule_square(h: nx.Graph, ctx: dict) -> bool:
    """Blind plaquette hill-climb: strict-greater on touched 4-cycles.

    Rewards the local motif of the square vacuum (plaquettes) without
    referencing the vacuum: no coordinates, no span calibration, no M_O.
    Plain grid is a fixed point (measured); from damage it recovers
    motifs (323 -> 341) WITHOUT healing locality (longs 30 -> 35) --
    a blind-Goodhart pin: motif count and locality decouple even when
    the objective is observer-blind. Greedy stalls below the vacuum
    count (341 < 361): hill-climb is not sampling.
    """
    return _motif_rule(h, ctx, _squares_touching)


def rule_triangle(h: nx.Graph, ctx: dict) -> bool:
    """Blind triangulation hill-climb: strict-greater on touched triangles.

    Same admissibility as rule_square with the Delaunay motif. From the
    square vacuum it LEAVES the basin (triangles 0 -> 115, squares
    361 -> 162 over 200 steps) toward a triangulated class whose landing
    point needs substrate-agnostic measurement (queued) -- square-
    calibrated longs cannot judge a triangulated morphology.
    """
    return _motif_rule(h, ctx, _tris_touching)
