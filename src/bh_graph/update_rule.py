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
) -> tuple[list[float], nx.Graph, int]:
    """Run rule for steps; return (p-trajectory, final graph, accepted)."""
    if src is None:
        src = next(iter(g0.nodes()))
    h = g0.copy()
    ctx = {"rng": random.Random(seed), "src": src, "target": target,
           "proposals": proposals, "swaps_per_step": swaps_per_step}
    traj, acc = [], 0
    for _ in range(steps):
        acc += rule(h, ctx)
        traj.append(locality_p(h, src))
    return traj, h, acc
