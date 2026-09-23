"""Section 1 — All:all = no interior space (fast scrambling).

We use a deterministic SI / operator-spreading toy: at t=0 one node is
"infected" (holds the infalling qubit's operator weight); at each discrete
step every infected node infects all of its graph neighbors. The cover time
is the number of steps until all N nodes are infected.

  - Complete graph K_N: cover time = 1 for any N (0 if N == 1). Diameter 1.
  - Chain / grid: cover time grows polynomially with N (diameter-limited).
  - Random regular: cover time grows ~ log N but with a larger prefactor and
    nonzero diameter, unlike K_N whose diameter is exactly 1.

This reproduces the qualitative Sekino-Susskind hierarchy: black holes are
the fastest scramblers, consistent with an effectively all:all interaction
graph. ER=EPR reading: perfect entanglement = zero-length connectivity, so
the interior has no metric extent — it is "one dot".
"""
from __future__ import annotations

from collections import deque
import networkx as nx
import numpy as np

from bh_graph.graphs import build_complete, build_chain, build_grid_2d, build_random_regular


def infection_time(g: nx.Graph, seed: int = 0) -> int:
    """Steps for SI spread from `seed` to cover the whole graph (= eccentricity of seed)."""
    if len(g) == 0:
        return 0
    if len(g) == 1:
        return 0
    seen = {seed}
    q: deque[tuple[int, int]] = deque([(seed, 0)])
    t_max = 0
    while q:
        u, t = q.popleft()
        t_max = max(t_max, t)
        for v in g.neighbors(u):
            if v not in seen:
                seen.add(v)
                q.append((v, t + 1))
    return t_max


def graph_diameter(g: nx.Graph) -> int:
    if len(g) <= 1:
        return 0
    return nx.diameter(g)


def mean_path_length(g: nx.Graph) -> float:
    if len(g) <= 1:
        return 0.0
    return float(nx.average_shortest_path_length(g))


def spectral_gap(g: nx.Graph) -> float:
    """Algebraic connectivity (Fiedler value). K_N has gap N; local graphs ~ O(1/N)."""
    if len(g) <= 1:
        return 0.0
    lap = nx.laplacian_matrix(g).toarray()
    vals = np.linalg.eigvalsh(lap)
    vals.sort()
    return float(vals[1]) if len(vals) > 1 else 0.0


def scrambling_scaling(ns: list[int], seed: int = 0) -> dict[str, dict[int, dict[str, float]]]:
    """Compare cover time / diameter / mean distance across graph families.

    Returns {family: {N: {t_cover, diameter, mean_dist, gap}}}.
    Grid sizes are snapped to the nearest square <= N for comparability.
    """
    out: dict[str, dict[int, dict[str, float]]] = {
        "complete (all:all)": {},
        "chain (1D local)": {},
        "grid (2D local)": {},
        "random-regular d=3": {},
    }
    for n in ns:
        # complete
        g = build_complete(n)
        out["complete (all:all)"][n] = {
            "t_cover": float(infection_time(g, 0)),
            "diameter": float(graph_diameter(g)),
            "mean_dist": float(mean_path_length(g)),
            "gap": float(spectral_gap(g)) if n <= 400 else float(n),
        }
        # chain
        g = build_chain(n)
        # worst-case seed at an end would be n-1; use middle-ish seed for typicality
        out["chain (1D local)"][n] = {
            "t_cover": float(infection_time(g, n // 2)),
            "diameter": float(n - 1),
            "mean_dist": float(mean_path_length(g)) if n <= 2000 else float((n + 1) / 3),
            "gap": float(2 * (1 - np.cos(np.pi / n))) if n > 1 else 0.0,
        }
        # grid (snap to square)
        side = max(1, int(round(n**0.5)))
        n_sq = side * side
        g = build_grid_2d(side)
        out["grid (2D local)"][n_sq] = {
            "t_cover": float(infection_time(g, 0)),
            "diameter": float(graph_diameter(g)),
            "mean_dist": float(mean_path_length(g)) if n_sq <= 2500 else float(side * 2 / 3),
            "gap": float(spectral_gap(g)) if n_sq <= 900 else float(2 * (1 - np.cos(np.pi / side))),
        }
        # random regular
        g = build_random_regular(n, 3, seed=seed)
        out["random-regular d=3"][len(g)] = {
            "t_cover": float(infection_time(g, 0)),
            "diameter": float(graph_diameter(g)),
            "mean_dist": float(mean_path_length(g)) if len(g) <= 3000 else 0.0,
            "gap": float(spectral_gap(g)) if len(g) <= 900 else 0.0,
        }
    return out


def is_valid_graph(g: nx.Graph) -> bool:
    """Boolean check (no exceptions for control flow): connected and nonempty."""
    return len(g) > 0 and nx.is_connected(g)
