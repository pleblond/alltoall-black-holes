"""BR-1 vacuum neutrality + rigidity audit: neutral drift, fingerprint, census.

Campaign: D14-BR1 (vacuum neutrality and rigidity). This module introduces
NO graph evolution law, NO vacuum potential, and NO new interaction. It
audits what the ALREADY-EXISTING machine does on the zero-field neutral
manifold (psi = 0 => B = J = 0 => Delta E_psi = 0 for every move):

  - BR-1B: legal-move census on pristine J2 (M1 class, frozen from BR-0).
  - BR-1D/F: neutral-drift stress test (N1: execute every legal relocation
    without energetic discrimination) + survival curves over the FROZEN
    vacuum fingerprint (banked J2 observables only).
  - BR-1C/G: existing-U audit helpers (fingerprint + drift + defect
    injection consumed by the campaign; the rules themselves are NOT
    modified, rejustified, or extended here).
  - BR-1I: small-field continuity helpers (Delta E ~ eps^2 scaling check).

Frozen ontology: G, psi = (r, i), U (existing rules only). J2 coordinates
appear ONLY as persistent node labels for quotient/bipartition READOUT
(the banked J2 methodology); no dynamics consults them.
"""

from __future__ import annotations

import bisect
import random
from collections import Counter

import networkx as nx
import numpy as np

# Preregistered BR-1 survival tolerances (BR1-PREREG, docs/DEFERRED.md):
# dp_tol = banked micro-vs-quotient agreement bound (0.15, test_j2.py);
# qfrac_min = quotient square-adjacency floor (banked value 1.0 exactly).
DP_TOL_DEFAULT = 0.15
QFRAC_MIN_DEFAULT = 0.99


def shells_cuts_vols(g: nx.Graph, src, rmax: int):
    """BFS shells + cut sizes + cumulative volumes (frozen family rule).

    Shells[r] = #{d == r}; cuts[r-1] = edges crossing the r-disk boundary
    for r = 1..rmax; vols = cumsum(shells). Same prescription as the
    banked substrate-family/J2 pins (reimplemented: no cross-test imports).
    """
    from bh_graph.scrambling import hop_arrival_times

    d = hop_arrival_times(g, src)
    shells = [sum(1 for n in d if d[n] == r) for r in range(rmax + 1)]
    cuts = []
    for r in range(1, rmax + 1):
        disk = {n for n in d if d[n] <= r}
        cuts.append(sum(1 for u in disk for v in g[u] if v not in disk))
    return shells, cuts, np.cumsum(np.array(shells, dtype=float))


def window_p(vols, lo: int, hi: int) -> float:
    """Long-scale exponent: log-log slope of vols over [lo, hi] (frozen rule)."""
    vols = np.asarray(vols, dtype=float)
    rr = np.arange(len(vols), dtype=float)
    m = (rr >= lo) & (rr <= hi)
    p, _ = np.polyfit(np.log(rr[m]), np.log(vols[m]), 1)
    return float(p)


def ball_label_maps(g: nx.Graph):
    """q bipartition + quotient cells from J2-ball node labels (x, y, b)."""
    qmap, cellmap = {}, {}
    for n in g.nodes():
        x, y, _ = n
        qmap[n] = (x + y) % 2
        cellmap[n] = (x, y)
    return qmap, cellmap


def torus_label_maps(coords: dict):
    """q bipartition + quotient cells from J2-torus coords id -> (x, y, b)."""
    qmap = {v: (c[0] + c[1]) % 2 for v, c in coords.items()}
    cellmap = {v: (c[0], c[1]) for v, c in coords.items()}
    return qmap, cellmap


def square_label_maps(coords: dict):
    """q bipartition + trivial cells from square coords id -> (x, y)."""
    qmap = {v: (c[0] + c[1]) % 2 for v, c in coords.items()}
    cellmap = {v: (c[0], c[1]) for v, c in coords.items()}
    return qmap, cellmap


def quotient_square_frac(g: nx.Graph, cellmap: dict, periods=None) -> float:
    """Fraction of quotient edges that are square-adjacent (banked: 1.0 on J2).

    periods=(Lx, Ly) enables minimal-image adjacency for toroidal readouts
    (P1 min-image convention); None = plain adjacency (banked ball readout).
    """
    qe = set()
    for u, v in g.edges():
        cu, cv = cellmap[u], cellmap[v]
        if cu != cv:
            qe.add((cu, cv) if cu < cv else (cv, cu))
    if not qe:
        return 1.0

    def adj(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        if periods is not None:
            dx = min(dx, periods[0] - dx)
            dy = min(dy, periods[1] - dy)
        return dx + dy == 1

    sq = sum(1 for a, b in qe if adj(a, b))
    return sq / len(qe)


def bipartition_violations(g: nx.Graph, qmap: dict) -> int:
    """Edges with q(u) == q(v) (banked: 0 on pristine J2; odd-cycle witness)."""
    return sum(1 for u, v in g.edges() if qmap[u] == qmap[v])


def vacuum_fingerprint(g: nx.Graph, src, rmax: int, qmap: dict, cellmap: dict,
                       p_lo: int, p_hi: int, with_heavy: bool = True,
                       periods=None) -> dict:
    """Frozen vacuum fingerprint: banked UV + IR observables, one snapshot.

    UV/micro: n, e, degree histogram, shells, cuts, C4 census, bipartition
    violations. IR/class: connectivity, long-scale exponent p, quotient
    square-adjacency fraction. C4 via the banked blind_u census.
    with_heavy=False skips shells/cuts/C4 (light cadence for trajectories;
    survival inputs connected/p/qfrac are always present).
    """
    from bh_graph.blind_u import nsquares

    connected = bool(nx.is_connected(g)) if len(g) > 0 else False
    shells, cuts, vols = shells_cuts_vols(g, src, rmax)
    p = window_p(vols, p_lo, p_hi) if connected else None
    fp = {
        "connected": connected,
        "n": g.number_of_nodes(),
        "e": g.number_of_edges(),
        "degrees": dict(sorted(Counter(dict(g.degree()).values()).items())),
        "p": (None if p is None else float(p)),
        "bip_viol": int(bipartition_violations(g, qmap)),
        "qfrac": float(quotient_square_frac(g, cellmap, periods)),
    }
    if with_heavy:
        fp["shells"] = [int(x) for x in shells]
        fp["cuts"] = [int(x) for x in cuts]
        fp["c4"] = int(nsquares(g))
    return fp


def class_alive(fp: dict, base: dict, dp_tol: float = DP_TOL_DEFAULT,
                qfrac_min: float = QFRAC_MIN_DEFAULT) -> bool:
    """Preregistered CLASS-ALIVE predicate (BR1-PREREG survival criterion)."""
    if not fp["connected"]:
        return False
    if abs(fp["p"] - base["p"]) > dp_tol:
        return False
    if fp["qfrac"] < qfrac_min:
        return False
    return True


def death_move(traj: list, base: dict, snapshot_every: int | None = None,
               dp_tol: float = DP_TOL_DEFAULT,
               qfrac_min: float = QFRAC_MIN_DEFAULT):
    """First CLASS-DEAD move index (from snapshot t stamps), else None."""
    for k, fp in enumerate(traj):
        if not class_alive(fp, base, dp_tol, qfrac_min):
            if "t" in fp:
                return int(fp["t"])
            return k * (snapshot_every or 1)
    return None


def drift_propose(elist: list, nbrs: dict, nodes: list, rng: random.Random,
                  max_tries: int = 100):
    """One M1 proposal: uniform edge + rejection-sampled uniform non-edge.

    Same distribution + consumption order as backreaction.sample_relocations
    (pinned mirror); returns ((a,b),(c,d)) with sorted tuples, or None.
    """
    a, b = elist[rng.randrange(len(elist))]
    for _ in range(max_tries):
        c = nodes[rng.randrange(len(nodes))]
        d = nodes[rng.randrange(len(nodes))]
        if c == d:
            continue
        e = (c, d) if c < d else (d, c)
        if e != (a, b) and d not in nbrs[c]:
            return (a, b), e
    return None


def neutral_drift(g0: nx.Graph, n_moves: int, seed: int, snapshot_every: int,
                  fp_kwargs: dict, heavy_every: int = 4,
                  return_final: bool = False) -> dict:
    """N1 neutral drift: execute every legal M1 relocation, no discrimination.

    Counterfactual stress test (NOT proposed physics). Returns fingerprint
    trajectory (t=0 first, full), moves applied, and determinism metadata.
    Light snapshots every snapshot_every moves; heavy (shells/cuts/C4)
    every heavy_every-th snapshot. E is conserved exactly (C3);
    microstate changes on every applied move.
    """
    h = g0.copy()
    nodes = sorted(h.nodes())
    elist = sorted(tuple(sorted(e)) for e in h.edges())
    nbrs = {v: set(h.neighbors(v)) for v in nodes}
    rng = random.Random(seed)
    traj = [dict(vacuum_fingerprint(h, **fp_kwargs), t=0)]
    applied = 0
    for t in range(1, n_moves + 1):
        mv = drift_propose(elist, nbrs, nodes, rng)
        if mv is None:
            break
        (a, b), (c, d) = mv
        h.remove_edge(a, b)
        h.add_edge(c, d)
        nbrs[a].discard(b)
        nbrs[b].discard(a)
        nbrs[c].add(d)
        nbrs[d].add(c)
        elist.pop(bisect.bisect_left(elist, (a, b)))
        bisect.insort(elist, (c, d))
        applied += 1
        if t % snapshot_every == 0:
            k = t // snapshot_every
            fp = vacuum_fingerprint(h, with_heavy=(k % heavy_every == 0), **fp_kwargs)
            traj.append(dict(fp, t=t))
    out = {
        "traj": traj,
        "moves_applied": int(applied),
        "moves_proposed": int(n_moves),
        "snapshot_every": int(snapshot_every),
        "heavy_every": int(heavy_every),
        "seed": int(seed),
        "final_edges": None,
    }
    if return_final:
        out["final_edges"] = [[a, b] for a, b in elist]
    return out


def disconnect_frac(g: nx.Graph, n_sample: int, seed: int) -> dict:
    """Sampled M1 anatomy: fraction of relocations disconnecting the graph."""
    from bh_graph.backreaction import sample_relocations

    n_disc = 0
    moves = sample_relocations(g, n_sample, seed)
    for (a, b), (c, d) in moves:
        h = g.copy()
        h.remove_edge(a, b)
        h.add_edge(c, d)
        if not nx.is_connected(h):
            n_disc += 1
    return {"n_sample": int(len(moves)), "n_disconnect": int(n_disc),
            "frac": float(n_disc / len(moves)) if moves else 0.0}


def chord_distance_hist(g: nx.Graph, n_sample: int, seed: int) -> dict:
    """Graph-distance distribution of M1-added pairs (coordinate-free anatomy).

    Distance measured on the pristine graph: d >= 4 marks nonlocal chords
    beyond 2nd-neighbor range (genuinely new microstructure, B2).
    """
    from bh_graph.backreaction import sample_relocations

    dist = dict(nx.all_pairs_shortest_path_length(g))
    hist: dict = {}
    moves = sample_relocations(g, n_sample, seed)
    for _, (c, d) in moves:
        dd = dist[c][d]
        hist[dd] = hist.get(dd, 0) + 1
    n = len(moves)
    return {"n_sample": int(n), "hist": {int(k): int(v) for k, v in sorted(hist.items())},
            "frac_nonlocal": float(sum(v for k, v in hist.items() if k >= 4) / n) if n else 0.0}


def span_signature(h: nx.Graph, radius: int = 3) -> dict:
    """Edge-span histogram (update_rule.edge_span): fabric baseline census."""
    from bh_graph.update_rule import edge_span

    hist: dict = {}
    for u, v in h.edges():
        s = edge_span(h, u, v, radius)
        hist[s] = hist.get(s, 0) + 1
    return {"radius": int(radius), "hist": {int(k): int(v) for k, v in sorted(hist.items())}}


def defect_inject(g0: nx.Graph, seed: int):
    """One M1 move from pristine (BR-1G single-defect probe input)."""
    from bh_graph.backreaction import sample_relocations

    (a, b), (c, d) = sample_relocations(g0, 1, seed)[0]
    h = g0.copy()
    h.remove_edge(a, b)
    h.add_edge(c, d)
    return h, {"remove": [a, b], "add": [c, d]}


def max_abs_dep_over_field(psi_hat: np.ndarray, g: nx.Graph, order: list,
                           eps_grid, n_sample: int, seed: int) -> dict:
    """Small-field continuity (BR-1I): max|Delta E| over eps * psi_hat moves.

    psi_hat is a FIXED normalized pattern (preregistered); Delta E must
    scale as eps^2 bit-cleanly (bilinearity of B in psi).
    """
    from bh_graph.backreaction import delta_e_batch, sample_relocations
    from bh_graph.ballistic import index_of

    idx = index_of(order)
    moves = sample_relocations(g, n_sample, seed)
    rems = [m[0] for m in moves]
    adds = [m[1] for m in moves]
    out = {}
    for eps in eps_grid:
        psi = np.asarray(eps, dtype=float) * np.asarray(psi_hat, dtype=np.complex128)
        dE = delta_e_batch(psi, idx, rems, adds)
        out[str(float(eps))] = float(np.max(np.abs(dE))) if len(dE) else 0.0
    return {"n_sample": int(len(moves)), "max_abs_dE": out}
