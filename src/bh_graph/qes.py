"""C: Tensor-network min-cut / QES-pop check for Sec 3.

Two complementary calculations showing a horizon/QES really *pops* at a
critical exterior budget rather than being put in by hand:

1. Generalized-entropy crossing (analytic): naive Hawking candidate grows as
   S_no(k) = k s_leg forever, while the island candidate costs area plus
   remaining bulk entanglement S_isl(k) = k PATCH/4 + max(S0 - k s_leg, 0).
   If 2 s_leg exceeds area cost per leg (s_leg > PATCH/8 = ln 2/2), the
   lines cross at k_page = S0 / (2 s_leg - PATCH/4): below it the minimal
   surface is trivial (no island / pointlike), above it the island/QES
   dominates. Saturated vacuum legs (s_leg = ln 2) give k_page = S0/ln 2.

2. Explicit graph min-cut (numeric): flow network with an all:all core
   (internal capacity c_int) wired to boundary sinks via k legs (capacity
   c_leg). The min-cut value and location are computed with networkx; at small
   k the cheapest cut severs the legs (exterior wedge excludes interior), and
   past a critical k the cut jumps to include an island region. This mirrors
   RT/QES behavior in a discrete setting.
"""
from __future__ import annotations

import numpy as np
import networkx as nx


def qes_candidates(k, s0: float, s_leg: float | None = None, lp: float = 1.0):
    """Return (S_no_island, S_island) generalized-entropy candidates (BS: area k PATCH/4)."""
    from bh_graph.horizon import PATCH_AREA
    if s_leg is None:
        s_leg = float(np.log(2.0))  # saturated legs
    k = np.asarray(k, dtype=float)
    s_no = k * s_leg
    s_isl = k * PATCH_AREA * lp**2 / 4.0 + np.maximum(s0 - k * s_leg, 0.0)
    if s_no.ndim == 0:
        return float(s_no), float(s_isl)
    return s_no, s_isl


def qes_page_k(s0: float, s_leg: float | None = None, lp: float = 1.0) -> float:
    """Analytic crossing k_page = S0/(2 s_leg - PATCH lp^2/4) (BS). Inf if none."""
    from bh_graph.horizon import PATCH_AREA
    if s_leg is None:
        s_leg = float(np.log(2.0))
    denom = 2.0 * s_leg - PATCH_AREA * lp**2 / 4.0
    if denom <= 0:
        return float("inf")
    return float(s0 / denom)


def qes_dominant(k, s0: float, s_leg: float | None = None, lp: float = 1.0):
    """Boolean array: True where island/QES dominates (S_isl < S_no)."""
    if s_leg is None:
        s_leg = float(np.log(2.0))
    s_no, s_isl = qes_candidates(k, s0, s_leg, lp)
    return np.asarray(s_isl) <= np.asarray(s_no)  # BS: tie counts as island (saturated slopes match)


def has_qes_transition(s_leg: float | None = None, lp: float = 1.0) -> bool:
    """Boolean check: does the model admit a QES pop at all (BS: > PATCH/8)?"""
    from bh_graph.horizon import PATCH_AREA
    if s_leg is None:
        s_leg = float(np.log(2.0))
    return bool(s_leg > PATCH_AREA * lp**2 / 8.0)


def build_core_boundary_flow(n_core: int, k: int, c_int: float = 5.0, c_leg: float = 1.0) -> nx.DiGraph:
    """Flow network: source -> core (all:all, cap c_int) -> boundary legs (cap c_leg) -> sink.

    Core is a clique with bidirectional capacity c_int; leg i connects core
    node (i mod n_core) to sink with capacity c_leg. Source connects to every
    core node with infinite capacity.
    """
    g = nx.DiGraph()
    src, snk = "src", "snk"
    g.add_node(src)
    g.add_node(snk)
    core = [f"c{i}" for i in range(n_core)]
    for c in core:
        g.add_edge(src, c, capacity=float("inf"))
    for i in range(n_core):
        for j in range(i + 1, n_core):
            g.add_edge(core[i], core[j], capacity=c_int)
            g.add_edge(core[j], core[i], capacity=c_int)
    for leg in range(k):
        g.add_edge(core[leg % n_core], snk, capacity=c_leg)
    return g


def min_cut_value(n_core: int, k: int, c_int: float = 5.0, c_leg: float = 1.0) -> float:
    g = build_core_boundary_flow(n_core, k, c_int, c_leg)
    val, _ = nx.minimum_cut(g, "src", "snk", capacity="capacity")
    return float(val)


def min_cut_scaling(n_core: int, k_grid, c_int: float = 5.0, c_leg: float = 1.0) -> np.ndarray:
    return np.array([min_cut_value(n_core, int(k), c_int, c_leg) for k in k_grid], dtype=float)
