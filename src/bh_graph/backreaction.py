"""BR-0 bond-energy landscape: offline Delta-E_psi measurement over legal graph moves.

Campaign: D14-BR0 (bond-energy landscape). This module introduces NO graph
evolution and NO new interaction law. It measures, for frozen (G, psi),
the wave-energy ordering over candidate one-edge relocations:

    E_psi(G, psi) = <psi|H(G)|psi>,  H(G) = -J * A(G)   (P1-LOCKED)

    Delta E_psi(G -> G') = <psi|H(G') - H(G)|psi>   (psi held fixed)

For a single relocation (a,b) -> (c,d) the local reduction (pinned by C0
against full-Hamiltonian evaluation before any campaign use) is

    Delta E_psi = -2*J * (B_cd - B_ab),  B_ij = Re(psi*_i psi_j).

Frozen ontology (BR0-PREREG, docs/DEFERRED.md):
  - Edges binary (A_ij in {0,1}); no edge weights.
  - H(G) = -J*A(G), J = 1 (P1 convention, J_DEFAULT).
  - psi normalized (<psi|psi> = 1) except the V0 zero-field control (psi = 0).
  - Real part B_ij ONLY. The antisymmetric Im(psi*_i psi_j) is reserved
    for later current/momentum work and has NO reader, driver, or readout
    in this module (BR-0 forbids current-driven rewiring tests).
  - Wave apparatus (gaussian_packet, node_order, hamiltonian, ...) is the
    P1-frozen sector vendored verbatim from P1 tip ac6a1409
    (origin/cursor/ballistic-motion-p1-be3e); packet families below reuse
    ONLY P1.1-validated (r0, k, sigma, substrate) settings.

Primary move class M1 (frozen pre-data): remove one uniform-random existing
edge + add one uniform-random non-edge (formation.propose_relocation
distribution, mirrored exactly). Preserves N, E, simplicity. Does NOT
preserve degree sequence. Does NOT require connectivity (post-move
connectivity filed as a covariate via bridge precompute + rare-path BFS).
"""

from __future__ import annotations

import math
import random

import networkx as nx
import numpy as np

EPS_DEFAULT = 1e-10  # primary sign epsilon (absolute, J=1 units; pre-data:
# ~1e3x above fp64 summation noise on E~O(1-10), ~1e7x below peak-bond
# scale ~1e-3; separates numerical noise from every physical tail)
J_BR0 = 1.0  # frozen P1 coupling convention
R_NEAR_DEFAULT = None  # near radius is ALWAYS 2*sigma of the packet (never a literal)


def bond_B(psi: np.ndarray, i: int, j: int) -> float:
    """Symmetric bond-energy quantity B_ij = Re(psi*_i psi_j) (BR-0 real part only)."""
    psi = np.asarray(psi, dtype=np.complex128)
    return float(np.real(np.conj(psi[i]) * psi[j]))


def is_bond_symmetric_ok(psi: np.ndarray, i: int, j: int) -> bool:
    """Boolean check: B_ij == B_ji bitwise (never raises)."""
    return bool(bond_B(psi, i, j) == bond_B(psi, j, i))


def energy_full(psi: np.ndarray, g: nx.Graph, order: list | None = None,
                j: float = J_BR0) -> float:
    """Wave energy E_psi = <psi|H(G)|psi> with H = -J*A (psi = 0 -> 0.0 exactly)."""
    from bh_graph.ballistic import adjacency_csr, node_order

    psi = np.asarray(psi, dtype=np.complex128)
    if order is None:
        order = node_order(g)
    if not np.any(psi):
        return 0.0
    a = adjacency_csr(g, order)
    return float(-float(j) * np.real(np.vdot(psi, a @ psi)))


def energy_edge_sum(psi: np.ndarray, g: nx.Graph, order: list | None = None,
                    j: float = J_BR0) -> float:
    """Cross-check form E_psi = -2*J * sum over edges of B_ij (same convention)."""
    from bh_graph.ballistic import index_of, node_order

    psi = np.asarray(psi, dtype=np.complex128)
    if order is None:
        order = node_order(g)
    if not np.any(psi):
        return 0.0
    idx = index_of(order)
    tot = 0.0
    for a, b in g.edges():
        tot += bond_B(psi, idx[a], idx[b])
    return float(-2.0 * float(j) * tot)


def delta_e_local(psi: np.ndarray, idx: dict, remove_edge, add_edge,
                  j: float = J_BR0) -> float:
    """Local move energy Delta E = -2J (B_add - B_remove) (psi held fixed)."""
    psi = np.asarray(psi, dtype=np.complex128)
    a, b = remove_edge
    c, d = add_edge
    b_rem = bond_B(psi, idx[a], idx[b])
    b_add = bond_B(psi, idx[c], idx[d])
    return float(-2.0 * float(j) * (b_add - b_rem))


def delta_e_full(psi: np.ndarray, g: nx.Graph, order: list, remove_edge, add_edge,
                 j: float = J_BR0) -> float:
    """Direct move energy E(G') - E(G) via full-Hamiltonian evaluation (C0 reference)."""
    a, b = remove_edge
    c, d = add_edge
    if (a, b) == (c, d) or (a, b) == (d, c):
        return 0.0
    e0 = energy_full(psi, g, order, j)
    g2 = g.copy()
    g2.remove_edge(a, b)
    g2.add_edge(c, d)
    return float(energy_full(psi, g2, order, j) - e0)


def delta_e_batch(psi: np.ndarray, idx: dict, removals, additions,
                  j: float = J_BR0) -> np.ndarray:
    """Vectorized local Delta E over parallel move lists (same formula as delta_e_local)."""
    psi = np.asarray(psi, dtype=np.complex128)
    r1 = np.array([idx[a] for a, _ in removals], dtype=int)
    r2 = np.array([idx[b] for _, b in removals], dtype=int)
    a1 = np.array([idx[c] for c, _ in additions], dtype=int)
    a2 = np.array([idx[d] for _, d in additions], dtype=int)
    b_rem = np.real(np.conj(psi[r1]) * psi[r2])
    b_add = np.real(np.conj(psi[a1]) * psi[a2])
    return -2.0 * float(j) * (b_add - b_rem)


def count_relocations(g: nx.Graph) -> int:
    """Exhaustive M1 census size: E * (N(N-1)/2 - E)."""
    n, e = g.number_of_nodes(), g.number_of_edges()
    return int(e * (n * (n - 1) // 2 - e))


def sample_relocations(g: nx.Graph, n_moves: int, seed: int,
                       max_tries: int = 100) -> list:
    """M1 sampler: uniform edge + uniform non-edge (formation.propose_relocation dist).

    Mirrors formation.propose_relocation exactly (uniform elist pick, then
    rejection-sampled uniform node pairs); deterministic given seed.
    Returns [((a,b),(c,d)), ...] with sorted tuples; may return fewer
    than n_moves only on near-complete graphs (filed, never an error).
    """
    nodes = sorted(g.nodes())
    elist = sorted(tuple(sorted(e)) for e in g.edges())
    nbrs = {v: set(g.neighbors(v)) for v in nodes}
    eset = set(elist)
    rng = random.Random(seed)
    out = []
    for _ in range(n_moves):
        a, b = elist[rng.randrange(len(elist))]
        for _ in range(max_tries):
            c = nodes[rng.randrange(len(nodes))]
            d = nodes[rng.randrange(len(nodes))]
            if c == d:
                continue
            e = (c, d) if c < d else (d, c)
            if e != (a, b) and e not in eset:
                out.append(((a, b), e))
                break
    return out


def all_relocations(g: nx.Graph):
    """Exhaustive M1 census generator over edges x non-edges (small graphs only)."""
    edges = sorted(tuple(sorted(e)) for e in g.edges())
    nonedges = sorted(tuple(sorted(e)) for e in nx.complement(g).edges())
    for e in edges:
        for f in nonedges:
            yield (e, f)


def edge_midpoint(a, b, coords: dict, periods) -> np.ndarray:
    """Minimal-image midpoint of edge (a,b) in readout coords (P1 min-image convention)."""
    from bh_graph.ballistic import min_image_disp

    ra = np.asarray(coords[a], dtype=float)
    rb = np.asarray(coords[b], dtype=float)
    return ra + min_image_disp(rb, ra, periods) / 2.0


def midpoint_radius(mid: np.ndarray, r0, periods) -> float:
    """Minimal-image distance of a midpoint from packet center r0."""
    from bh_graph.ballistic import min_image_disp

    return float(np.linalg.norm(min_image_disp(np.asarray(mid, dtype=float),
                                               np.asarray(r0, dtype=float), periods)))


def is_near(mid: np.ndarray, r0, r_near: float, periods) -> bool:
    """Boolean check: midpoint within r_near of r0 (minimal-image; never raises)."""
    return bool(midpoint_radius(mid, r0, periods) <= r_near)


def landscape_stats(dE: np.ndarray, eps: float = EPS_DEFAULT) -> dict:
    """Distribution summary: f_-/f0/f_+, median, quantiles, tails (eps-gated signs)."""
    d = np.asarray(dE, dtype=float)
    n = d.shape[0]
    neg = d < -eps
    pos = d > eps
    qs = np.quantile(d, [0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]) if n else np.zeros(9)
    out = {
        "n": int(n),
        "f_neg": float(np.mean(neg)) if n else 0.0,
        "f_zero": float(1.0 - np.mean(neg) - np.mean(pos)) if n else 0.0,
        "f_pos": float(np.mean(pos)) if n else 0.0,
        "n_neg": int(np.sum(neg)),
        "mean": float(np.mean(d)) if n else 0.0,
        "median": float(qs[3]) if n else 0.0,
        "q01": float(qs[0]) if n else 0.0,
        "q05": float(qs[1]) if n else 0.0,
        "q25": float(qs[2]) if n else 0.0,
        "q75": float(qs[4]) if n else 0.0,
        "q95": float(qs[5]) if n else 0.0,
        "q99": float(qs[6]) if n else 0.0,
        "min": float(np.min(d)) if n else 0.0,
        "max": float(np.max(d)) if n else 0.0,
    }
    if out["n_neg"]:
        out["neg_tail_mean"] = float(np.mean(d[neg]))
        out["neg_tail_min"] = float(np.min(d[neg]))
    else:
        out["neg_tail_mean"] = 0.0
        out["neg_tail_min"] = 0.0
    return out


def uniform_psi(n: int) -> np.ndarray:
    """Uniform state psi_i = 1/sqrt(N) (BR-0 SECONDARY exploratory background ONLY).

    This is NOT a vacuum claim: no nonzero psi_vac is justified by the wave
    program (BR0-PREREG V1-status: NONE). On z-regular graphs this coincides
    with the H ground state (pinned in tests); its landscape flatness is
    filed as mechanism information for BR-1, never as vacuum rigidity.
    """
    if n < 1:
        raise ValueError("n must be >= 1")
    return np.full(n, 1.0 / math.sqrt(n), dtype=np.complex128)


def zero_psi(n: int) -> np.ndarray:
    """V0 zero-field control psi = 0 (exact Delta E = 0 for every move, C1)."""
    if n < 1:
        raise ValueError("n must be >= 1")
    return np.zeros(n, dtype=np.complex128)


def move_stays_connected(g: nx.Graph, bridges: set, remove_edge, add_edge) -> bool:
    """Post-move connectivity: non-bridge removal cannot disconnect (rare-path BFS else)."""
    a, b = remove_edge
    e = (a, b) if a < b else (b, a)
    if e not in bridges:
        return True
    c, d = add_edge
    g2 = g.copy()
    g2.remove_edge(a, b)
    g2.add_edge(c, d)
    return bool(nx.is_connected(g2))


def radial_anatomy(rem_mid, add_mid, dE: np.ndarray, r0, periods,
                   n_bins: int = 30, eps: float = EPS_DEFAULT) -> dict:
    """Radial histograms of removed/added-edge midpoints (all + favorable subset).

    Bins span [0, maxR] with maxR the largest minimal-image radius from r0
    (half-diagonal of the period cell). Deterministic.
    """
    from bh_graph.ballistic import min_image_disp

    dE = np.asarray(dE, dtype=float)
    r0v = np.asarray(r0, dtype=float)
    maxR = float(np.sqrt(sum((p / 2.0) ** 2 for p in periods)))
    edges = np.linspace(0.0, maxR, n_bins + 1)
    rm = np.asarray([np.asarray(m, dtype=float) for m in rem_mid])
    am = np.asarray([np.asarray(m, dtype=float) for m in add_mid])
    rem_r = np.linalg.norm(min_image_disp(rm, r0v, periods), axis=1)
    add_r = np.linalg.norm(min_image_disp(am, r0v, periods), axis=1)
    neg = dE < -eps
    return {
        "rbins": [float(x) for x in edges],
        "rem_all": [int(x) for x in np.histogram(rem_r, bins=edges)[0]],
        "add_all": [int(x) for x in np.histogram(add_r, bins=edges)[0]],
        "rem_neg": [int(x) for x in np.histogram(rem_r[neg], bins=edges)[0]],
        "add_neg": [int(x) for x in np.histogram(add_r[neg], bins=edges)[0]],
    }


def bond_field_on_edges(psi: np.ndarray, g: nx.Graph, idx: dict) -> list:
    """B_ij over the sorted edge list (bond-energy field; order = sorted elist)."""
    psi = np.asarray(psi, dtype=np.complex128)
    return [bond_B(psi, idx[a], idx[b])
            for a, b in sorted(tuple(sorted(e)) for e in g.edges())]


def run_landscape(g: nx.Graph, order: list, coords: dict, periods, psi: np.ndarray,
                  r0, sigma: float, n_moves: int, seed: int,
                  j: float = J_BR0, eps: float = EPS_DEFAULT) -> dict:
    """Per-state BR-0 record: sampled M1 landscape + near/far + 2x2 anatomy + covariates.

    Near/far (preregistered primary): removed-edge midpoint within
    R_near = 2*sigma of packet center r0 (minimal-image). Added-edge
    midpoint gives the secondary 2x2 (remove-near/far x add-near/far).
    Also files |psi|^2, the B_ij bond field over the sorted edge list,
    and radial midpoint histograms (all + favorable). Deterministic
    given (graph, psi, n_moves, seed).
    """
    from bh_graph.ballistic import index_of

    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(order)
    moves = sample_relocations(g, n_moves, seed)
    if not moves:
        raise ValueError("empty move sample (graph too dense for M1 sampling?)")
    removals = [m[0] for m in moves]
    additions = [m[1] for m in moves]
    dE = delta_e_batch(psi, idx, removals, additions, j)
    r_near = 2.0 * float(sigma)
    r0v = np.asarray(r0, dtype=float)
    rem_mid = [edge_midpoint(a, b, coords, periods) for a, b in removals]
    add_mid = [edge_midpoint(c, d, coords, periods) for c, d in additions]
    rem_near = np.array([is_near(m, r0v, r_near, periods) for m in rem_mid])
    add_near = np.array([is_near(m, r0v, r_near, periods) for m in add_mid])
    bridges = set(tuple(sorted(e)) for e in nx.bridges(g)) if n_moves else set()
    conn = np.array([move_stays_connected(g, bridges, r, a)
                     for r, a in zip(removals, additions)])
    cells = {}
    for rn, an, tag in ((True, True, "nn"), (True, False, "nf"),
                        (False, True, "fn"), (False, False, "ff")):
        m = rem_near == rn
        m = m & (add_near == an)
        cells[tag] = landscape_stats(dE[m], eps)
    return {
        "n_moves": int(len(moves)),
        "seed": int(seed),
        "eps": float(eps),
        "j": float(j),
        "r_near": float(r_near),
        "e_psi": float(energy_full(psi, g, order, j)),
        "psi_sq": [float(x) for x in np.abs(psi) ** 2],
        "bond_B_edges": bond_field_on_edges(psi, g, idx),
        "global": landscape_stats(dE, eps),
        "near": landscape_stats(dE[rem_near], eps),
        "far": landscape_stats(dE[~rem_near], eps),
        "cells": cells,
        "anatomy": radial_anatomy(rem_mid, add_mid, dE, r0v, periods, 30, eps),
        "frac_rem_near": float(np.mean(rem_near)),
        "frac_add_near": float(np.mean(add_near)),
        "frac_connected": float(np.mean(conn)),
        "n_bridges": int(len(bridges)),
    }


def run_landscape_exhaustive(g: nx.Graph, order: list, coords: dict, periods,
                             psi: np.ndarray, r0, sigma: float,
                             j: float = J_BR0, eps: float = EPS_DEFAULT) -> dict:
    """Exact BR-0 record: exhaustive M1 census (no sampling noise; small graphs only)."""
    from bh_graph.ballistic import index_of

    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(order)
    pairs = list(all_relocations(g))
    if not pairs:
        raise ValueError("empty move census (complete graph has no M1 moves?)")
    removals = [m[0] for m in pairs]
    additions = [m[1] for m in pairs]
    dE = delta_e_batch(psi, idx, removals, additions, j)
    r_near = 2.0 * float(sigma)
    r0v = np.asarray(r0, dtype=float)
    rem_mid = [edge_midpoint(a, b, coords, periods) for a, b in removals]
    add_mid = [edge_midpoint(c, d, coords, periods) for c, d in additions]
    rem_near = np.array([is_near(m, r0v, r_near, periods) for m in rem_mid])
    add_near = np.array([is_near(m, r0v, r_near, periods) for m in add_mid])
    cells = {}
    for rn, an, tag in ((True, True, "nn"), (True, False, "nf"),
                        (False, True, "fn"), (False, False, "ff")):
        m = (rem_near == rn) & (add_near == an)
        cells[tag] = landscape_stats(dE[m], eps)
    return {
        "n_moves": int(len(pairs)),
        "exhaustive": True,
        "eps": float(eps),
        "j": float(j),
        "r_near": float(r_near),
        "e_psi": float(energy_full(psi, g, order, j)),
        "psi_sq": [float(x) for x in np.abs(psi) ** 2],
        "bond_B_edges": bond_field_on_edges(psi, g, idx),
        "global": landscape_stats(dE, eps),
        "near": landscape_stats(dE[rem_near], eps),
        "far": landscape_stats(dE[~rem_near], eps),
        "cells": cells,
        "anatomy": radial_anatomy(rem_mid, add_mid, dE, r0v, periods, 30, eps),
        "frac_rem_near": float(np.mean(rem_near)),
        "frac_add_near": float(np.mean(add_near)),
    }
