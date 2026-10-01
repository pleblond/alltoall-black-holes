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

import networkx as nx
import numpy as np

from bh_graph.graphs import build_chain, build_complete, build_grid_2d, build_random_regular


def infection_time(g: nx.Graph, seed: int = 0) -> int:
    """Steps for SI spread from `seed` to cover the whole graph (= eccentricity of seed).

    Single BFS via hop_arrival_times (unknown seed gives 0, not an
    exception, per the no-exceptions house rule).
    """
    return max(hop_arrival_times(g, seed).values(), default=0)


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
        side = max(1, round(n**0.5))
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


def hop_arrival_times(g: nx.Graph, seed: int = 0) -> dict[int, int]:
    """Per-node SI first-passage times from `seed` (BFS layers).

    Under trivial one-hop-per-step dynamics, first-passage time equals
    hop distance -- so this is a STATIC cover observable (D13 control),
    not a causal measurement: compatibility with a finite-speed cone is
    not observation of one. Genuine arrival times T_U need an update
    rule U (D1) plus counterfactual-influence readout (D13 stage 1).
    Empty graph gives {}.
    """
    if len(g) == 0 or seed not in g:
        return {}
    return dict(nx.single_source_shortest_path_length(g, seed))


def si_first_passage_row(g: nx.Graph, source, beta: float, rng, cap: int = 100000) -> np.ndarray:
    """One stochastic-SI run from `source`: arrival step per node.

    Chain-binomial SI: every infected node attempts each susceptible
    neighbor independently with probability `beta` per step; infected
    stay infectious (persistent attempts -- dropping failed transmitters
    empties the frontier and strands the sim, a caught-and-fixed bug).
    Nodes never reached by `cap` steps get `cap`. Seeded via `rng`.
    """
    infected = {source}
    arr = {source: 0}
    nbrs = {v: list(g[v]) for v in g.nodes()}
    n = len(g)
    t = 0
    while len(infected) < n:
        t += 1
        nxt = set()
        for v in infected:
            for w in nbrs[v]:
                if w not in infected and rng.random() < beta:
                    nxt.add(w)
        for w in nxt:
            infected.add(w)
            arr[w] = t
        if t > cap:
            break
    order = list(g.nodes())
    return np.array([arr.get(v, cap) for v in order], dtype=float)


def si_fpt_matrix(g: nx.Graph, beta: float, K: int, seed: int = 0) -> np.ndarray:
    """Mean SI first-passage distance matrix (symmetrized, seeded).

    d(i,j) = E[T_{i->j}] over K stochastic-SI runs per source: the
    first DYNAMICAL relational distance in-repo (response time as the
    interaction quantity chi). Graph-internal, operational, frozen
    rule (fixed beta); symmetrized since raw FPT is asymmetric.
    cMDS null on 10x10 grid (beta=0.5, K=100): GoF2 ~ 0.89,
    lam2/lam3 ~ 17.5 -- cleanly 2-dominant (test_mds.py).
    """
    rng = np.random.default_rng(seed)
    n = len(g)
    order = list(g.nodes())
    M = np.zeros((n, n))
    for i, s in enumerate(order):
        acc = np.zeros(n)
        for _ in range(K):
            acc += si_first_passage_row(g, s, beta, rng)
        M[i] = acc / K
    return (M + M.T) / 2
