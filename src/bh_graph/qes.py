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


# --- v6: enumerative S_gen(X) subset toy (small-N, toward D1) ---
# S_gen(X) = w_int |X|(N-|X|) + w_ext (k_total - sum_X k_i) + s_bulk |X|.
# Legs round-robin to nodes (leg j -> node j mod N), matching
# build_core_boundary_flow. Defaults frozen from repo: w_ext = ln 2
# (= PATCH/4, so S(empty) = S_no), s_bulk = ln 2 (saturated).
# With large w_int the minimum sits at X = {} or X = all (two-saddle),
# crossing at k* = N s_bulk / w_ext; small w_int allows partial islands.
# Conditional coincidence with packing holds iff the saturation gate
# passes (footprint k_crit == S0/ln2); otherwise thresholds differ.
# Path-integral derivation of S_gen remains open (D1).

SGEN_N_MAX = 16


def is_sgen_feasible(n: int, n_max: int = SGEN_N_MAX) -> bool:
    """Boolean check: is brute-force 2^N enumeration affordable?"""
    return bool(int(n) <= int(n_max))


def _legs_on_subset(n: int, k_total: int, mask: int) -> int:
    """Legs assigned (round-robin) to nodes selected by bitmask."""
    return sum(1 for j in range(int(k_total)) if (int(mask) >> (j % max(int(n), 1))) & 1)


def sgen_of_subset(mask, n: int, k_total: int, w_int: float = 5.0,
                   w_ext: float | None = None, s_bulk: float | None = None) -> float:
    """S_gen for one subset (int bitmask over N nodes)."""
    if w_ext is None:
        w_ext = float(np.log(2.0))
    if s_bulk is None:
        s_bulk = float(np.log(2.0))
    m = int(mask)
    size = bin(m).count("1")
    internal_cut = size * (int(n) - size)
    legs_in = _legs_on_subset(int(n), int(k_total), m)
    return float(w_int * internal_cut + w_ext * (int(k_total) - legs_in) + s_bulk * size)


def sgen_scan(n: int, k_grid, w_int: float = 5.0,
              w_ext: float | None = None, s_bulk: float | None = None) -> dict:
    """Brute-force min over 2^N subsets per k. Returns S_min, island size, flags.

    Includes "feasible": False with empty arrays when N exceeds SGEN_N_MAX
    (boolean gate, never an exception).
    """
    ks = [int(k) for k in np.atleast_1d(np.asarray(list(k_grid), dtype=float))]
    if not is_sgen_feasible(int(n)):
        z = np.array([], dtype=float)
        return {"k": np.array(ks, dtype=float), "S_min": z, "island_size": z,
                "is_island": np.array([], dtype=bool), "S_no": z, "feasible": False}
    if w_ext is None:
        w_ext = float(np.log(2.0))
    if s_bulk is None:
        s_bulk = float(np.log(2.0))
    s_min, sizes, s_no = [], [], []
    for k in ks:
        best, bsize = float("inf"), 0
        for mask in range(2 ** int(n)):
            v = sgen_of_subset(mask, int(n), k, w_int, w_ext, s_bulk)
            if v < best - 1e-12:
                best, bsize = v, bin(mask).count("1")
        s_min.append(best)
        sizes.append(bsize)
        s_no.append(w_ext * k)
    s_min = np.array(s_min)
    sizes = np.array(sizes, dtype=float)
    return {"k": np.array(ks, dtype=float), "S_min": s_min, "island_size": sizes,
            "is_island": sizes > 0, "S_no": np.array(s_no), "feasible": True}


def saturation_gate(n: int, s_bulk: float | None = None,
                    r_point: float | None = None, lp: float = 1.0,
                    rtol: float = 1e-9) -> bool:
    """Boolean check: does the footprint saturate the bulk entropy?

    Saturated iff packing k_crit(r_point) == S0/ln2 with S0 = N s_bulk,
    i.e. pi r^2 == N s_bulk (footprint area encodes the bulk).
    Coincidence of packing and Page thresholds holds iff this passes.
    """
    from bh_graph.micro import R_POINT, critical_k

    if s_bulk is None:
        s_bulk = float(np.log(2.0))
    r = R_POINT if r_point is None else float(r_point)
    k_have = critical_k(r, lp)
    k_need = float(int(n) * float(s_bulk) / np.log(2.0))
    return bool(np.isclose(k_have, k_need, rtol=rtol))


def tuned_footprint(n: int, s_bulk: float | None = None, lp: float = 1.0) -> float:
    """r_0 = sqrt(N s_bulk / pi): footprint that forces coincidence (calibration)."""
    if s_bulk is None:
        s_bulk = float(np.log(2.0))
    return float(np.sqrt(int(n) * float(s_bulk) / np.pi) * lp)
