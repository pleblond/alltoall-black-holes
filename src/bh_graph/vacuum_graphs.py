"""Vacuum graphs: genuinely k-regular PBC lattice families + excursions.

Preregistered in `docs/derivation-prereg.md` §1 (families) and §2.3
(excursion protocols E1/E2). All builders use PERIODIC boundary conditions
so the unperturbed vacuum is genuinely k-regular; regularity is asserted
in code (see `is_k_regular`).

Families (coordination = standard crystallography, not a choice):
  cubic   k=6   simple cubic L^3, bonds +-x/+-y/+-z mod L
  bcc     k=8   2 atoms/cell, 8 nearest-neighbor bonds, PBC
  fcc     k=12  4 atoms/cell (doubled-coords even-sublattice), 12 NN bonds
  kelvin  k=14  BCC SITES with 14 face-adjacency bonds (8 NN + 6 NNN).
                This is NOT the k=8 BCC graph. Do not conflate.

A15 / Weaire-Phelan dual is EXCLUDED (two coordinations 12/14 contradict
C2; prereg §1.3). No code for it exists here by design.

Node ids are ints 0..N-1. Each builder returns `lift` (covering-space
integer coords per node) + `period` so `max_unwrapped_radius` can check
PBC wrap without any floating point.
"""
from __future__ import annotations

from collections import deque

import networkx as nx
import numpy as np

FAMILIES = ("cubic", "bcc", "fcc", "kelvin")
K_VAC = {"cubic": 6, "bcc": 8, "fcc": 12, "kelvin": 14}

__all__ = [
    "FAMILIES",
    "K_VAC",
    "build_vacuum",
    "is_k_regular",
    "is_valid_family",
    "is_valid_L",
    "max_unwrapped_radius",
    "apply_excursion",
    "radial_bins",
]


def is_valid_family(family: str) -> bool:
    """Boolean check: known vacuum family (A15 deliberately absent)."""
    return isinstance(family, str) and family in FAMILIES


def is_valid_L(family: str, L: int) -> bool:
    """Boolean check: size usable (wrap-safe minimum per family)."""
    if not is_valid_family(family):
        return False
    if not isinstance(L, (int, np.integer)) or not np.isfinite(L):
        return False
    L = int(L)
    minimum = {"cubic": 5, "bcc": 4, "fcc": 3, "kelvin": 4}
    return L >= minimum[family]


def is_k_regular(g: nx.Graph, k: int) -> bool:
    """Boolean check: every node has degree exactly k."""
    if g is None or g.number_of_nodes() == 0:
        return False
    return all(int(d) == int(k) for _, d in g.degree())


# ---------------------------------------------------------------------------
# Builders. Each returns dict(ok, graph, lift, period, L, N, k, family,
# center). lift: (N,3) int array of covering-space coords; period: int
# with torus identification mod period per axis (in lift units).
# ---------------------------------------------------------------------------

def _build_cubic(L: int) -> dict:
    n = L ** 3

    def nid(x, y, z):
        return (x % L) * L * L + (y % L) * L + (z % L)

    g = nx.Graph()
    g.add_nodes_from(range(n))
    for x in range(L):
        for y in range(L):
            for z in range(L):
                u = nid(x, y, z)
                g.add_edge(u, nid(x + 1, y, z))
                g.add_edge(u, nid(x, y + 1, z))
                g.add_edge(u, nid(x, y, z + 1))
    lift = np.zeros((n, 3), dtype=int)
    for x in range(L):
        for y in range(L):
            for z in range(L):
                lift[nid(x, y, z)] = (x, y, z)
    return {"graph": g, "lift": lift, "period": L, "L": L, "N": n, "k": 6,
            "family": "cubic", "center": nid(L // 2, L // 2, L // 2)}


def _build_bcc(L: int, nnn: bool = False) -> dict:
    # Doubled coords: corner (2cx,2cy,2cz), body (2cx+1,2cy+1,2cz+1),
    # all arithmetic mod 2L. NN offsets (+-1,+-1,+-1).
    P = 2 * L
    corner = np.zeros((L, L, L), dtype=int)
    body = np.zeros((L, L, L), dtype=int)
    for cx in range(L):
        for cy in range(L):
            for cz in range(L):
                corner[cx, cy, cz] = (cx * L * L + cy * L + cz) * 2
                body[cx, cy, cz] = (cx * L * L + cy * L + cz) * 2 + 1
    n = 2 * L ** 3
    g = nx.Graph()
    g.add_nodes_from(range(n))
    for cx in range(L):
        for cy in range(L):
            for cz in range(L):
                u = body[cx, cy, cz]
                for dx in (0, 1):
                    for dy in (0, 1):
                        for dz in (0, 1):
                            g.add_edge(u, corner[(cx + dx) % L, (cy + dy) % L,
                                                 (cz + dz) % L])
    if nnn:
        # Same-sublattice bonds through square faces: (+-2,0,0) + perms.
        for cx in range(L):
            for cy in range(L):
                for cz in range(L):
                    g.add_edge(corner[cx, cy, cz], corner[(cx + 1) % L, cy, cz])
                    g.add_edge(corner[cx, cy, cz], corner[cx, (cy + 1) % L, cz])
                    g.add_edge(corner[cx, cy, cz], corner[cx, cy, (cz + 1) % L])
                    g.add_edge(body[cx, cy, cz], body[(cx + 1) % L, cy, cz])
                    g.add_edge(body[cx, cy, cz], body[cx, (cy + 1) % L, cz])
                    g.add_edge(body[cx, cy, cz], body[cx, cy, (cz + 1) % L])
    lift = np.zeros((n, 3), dtype=int)
    for cx in range(L):
        for cy in range(L):
            for cz in range(L):
                lift[corner[cx, cy, cz]] = (2 * cx, 2 * cy, 2 * cz)
                lift[body[cx, cy, cz]] = (2 * cx + 1, 2 * cy + 1, 2 * cz + 1)
    fam = "kelvin" if nnn else "bcc"
    return {"graph": g, "lift": lift, "period": P, "L": L, "N": n,
            "k": 14 if nnn else 8, "family": fam,
            "center": int(corner[L // 2, L // 2, L // 2])}


def _build_fcc(L: int) -> dict:
    # Doubled coords: even-sublattice of Z_{2L}^3, N = 4L^3.
    # NN offsets: (+-1,+-1,0), (+-1,0,+-1), (0,+-1,+-1).
    P = 2 * L
    idx = {}
    nodes = []
    for X in range(P):
        for Y in range(P):
            for Z in range(P):
                if (X + Y + Z) % 2 == 0:
                    idx[(X, Y, Z)] = len(nodes)
                    nodes.append((X, Y, Z))
    n = len(nodes)
    g = nx.Graph()
    g.add_nodes_from(range(n))
    offs = [(1, 1, 0), (1, -1, 0), (1, 0, 1), (1, 0, -1),
            (0, 1, 1), (0, 1, -1)]
    for (X, Y, Z), u in idx.items():
        for dx, dy, dz in offs:
            v = idx.get(((X + dx) % P, (Y + dy) % P, (Z + dz) % P))
            if v is not None:
                g.add_edge(u, v)
    lift = np.asarray(nodes, dtype=int)
    c = (L, L, L) if (3 * L) % 2 == 0 else (L + 1, L, L)
    c = (c[0] % P, c[1] % P, c[2] % P)
    return {"graph": g, "lift": lift, "period": P, "L": L, "N": n, "k": 12,
            "family": "fcc", "center": int(idx[c])}


def build_vacuum(family: str, L: int) -> dict:
    """Build an unperturbed k-regular vacuum graph. {ok, ...} (no raise)."""
    bad = {"ok": False}
    if not is_valid_L(family, L):
        return bad
    L = int(L)
    if family == "cubic":
        out = _build_cubic(L)
    elif family == "bcc":
        out = _build_bcc(L, nnn=False)
    elif family == "fcc":
        out = _build_fcc(L)
    elif family == "kelvin":
        out = _build_bcc(L, nnn=True)
    else:
        return bad
    if not is_k_regular(out["graph"], out["k"]):
        return bad
    out["ok"] = True
    return out


# ---------------------------------------------------------------------------
# PBC-wrap control: the torus r-ball is unwrapped iff its shell counts match
# the INFINITE lattice (BFS on Z^3 with the family step set, no mod) at every
# radius <= r. Count equality at all s<=r implies isometric balls (covering
# argument: a wrapped identification would shrink some shell count).
# ---------------------------------------------------------------------------

STEP_SETS = {
    "cubic": [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1),
              (0, 0, -1)],
    "bcc": [(dx, dy, dz) for dx in (1, -1) for dy in (1, -1)
            for dz in (1, -1)],
    "fcc": [(1, 1, 0), (1, -1, 0), (-1, 1, 0), (-1, -1, 0),
            (1, 0, 1), (1, 0, -1), (-1, 0, 1), (-1, 0, -1),
            (0, 1, 1), (0, 1, -1), (0, -1, 1), (0, -1, -1)],
    "kelvin": [(dx, dy, dz) for dx in (1, -1) for dy in (1, -1)
               for dz in (1, -1)]
    + [(2, 0, 0), (-2, 0, 0), (0, 2, 0), (0, -2, 0), (0, 0, 2), (0, 0, -2)],
}


def _infinite_shell_counts(family: str, r_cap: int) -> list:
    """Cumulative ball counts on the infinite lattice (Z^3 BFS, no mod)."""
    steps = STEP_SETS[family]
    dist = {(0, 0, 0): 0}
    q = deque([(0, 0, 0)])
    while q:
        u = q.popleft()
        if dist[u] >= r_cap:
            continue
        for s in steps:
            v = (u[0] + s[0], u[1] + s[1], u[2] + s[2])
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    shells = [0] * (r_cap + 1)
    for d in dist.values():
        shells[d] += 1
    cum = []
    tot = 0
    for c in shells:
        tot += c
        cum.append(tot)
    return cum


def max_unwrapped_radius(built: dict, center: int | None = None,
                         r_cap: int = 12) -> int:
    """Largest r with an unwrapped r-ball (shell-count isometry check).

    Returns 0 if the build is bad. Prereg: r_max rule for §2.3 (REQUIRE
    >= 4 else grow L). Runs on the UNPERTURBED lattice (excursion edges
    carry no lattice step); see vacuum_curv for the documented choice.
    """
    if not built.get("ok", False):
        return 0
    g = built["graph"]
    family = built["family"]
    if family not in STEP_SETS:
        return 0
    if center is None:
        center = int(built["center"])
    if center not in g:
        return 0
    torus = nx.single_source_shortest_path_length(g, center)
    t_shells = [0] * (r_cap + 1)
    for d in torus.values():
        if d <= r_cap:
            t_shells[d] += 1
    inf_cum = _infinite_shell_counts(family, r_cap)
    r_max, t_tot = 0, 0
    for r in range(r_cap + 1):
        t_tot += t_shells[r]
        if t_tot != inf_cum[r]:
            return r_max
        r_max = r
    return r_max


# ---------------------------------------------------------------------------
# Excursion protocols E1/E2 (prereg §2.3). Targets at UNPERTURBED distance
# >= 3 from center (seeded). Returns {ok, graph, center, protocol, added}.
# ---------------------------------------------------------------------------

def _dist_ge3_nodes(g: nx.Graph, center: int) -> list:
    dist = nx.single_source_shortest_path_length(g, center, cutoff=2)
    close = set(dist)
    return [v for v in g.nodes() if v not in close]


def apply_excursion(built: dict, protocol: str = "E1", delta: int = 2,
                    seed: int = 0) -> dict:
    """Apply E1 (hub-plus) or E2 (shell-plus) excursion. {ok, ...}."""
    bad = {"ok": False}
    if not built.get("ok", False):
        return bad
    if protocol not in ("E1", "E2"):
        return bad
    if not isinstance(delta, (int, np.integer)) or int(delta) < 1:
        return bad
    delta = int(delta)
    g0 = built["graph"]
    center = int(built["center"])
    rng = np.random.default_rng(seed)
    cand = _dist_ge3_nodes(g0, center)
    if len(cand) < 1:
        return bad
    g = g0.copy()
    added = []
    if protocol == "E1":
        if len(cand) < delta:
            return bad
        picks = rng.choice(len(cand), size=delta, replace=False)
        for i in picks:
            v = int(cand[int(i)])
            g.add_edge(center, v)
            added.append((center, v))
    else:
        ball = [center] + sorted(g0.neighbors(center), key=int)
        for u in ball:
            v = int(cand[int(rng.integers(len(cand)))])
            if not g.has_edge(u, v):
                g.add_edge(u, v)
                added.append((int(u), v))
    return {"ok": True, "graph": g, "center": center, "protocol": protocol,
            "delta": delta if protocol == "E1" else None, "seed": seed,
            "added": added, "family": built["family"], "k_vac": built["k"],
            "L": built["L"]}


def radial_bins(g: nx.Graph, center: int, r_max: int) -> dict:
    """Bin RADIAL edges by outer-endpoint hop distance from center.

    {r: [(u, v)]} for r = 1..r_max; radial = endpoints differ in r by 1,
    binned at max(r(u), r(v)). Empty bins omitted. {} on bad input.
    """
    if g is None or center not in g:
        return {}
    if not isinstance(r_max, (int, np.integer)) or int(r_max) < 1:
        return {}
    r_max = int(r_max)
    dist = nx.single_source_shortest_path_length(g, center, cutoff=r_max)
    bins: dict = {}
    for u, v in g.edges():
        ru, rv = dist.get(u), dist.get(v)
        if ru is None or rv is None or abs(ru - rv) != 1:
            continue
        r = max(ru, rv)
        if 1 <= r <= r_max:
            bins.setdefault(int(r), []).append((u, v))
    return bins
