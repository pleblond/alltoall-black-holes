"""GRAV-0: local fabric-disturbance propagation on the J2 torus.

Preregistration: docs/grav0-prereg.md (frozen design; read it first).
Question: can a local structural disturbance propagate arbitrarily far
through strictly local vacuum dynamics? Substrate: periodic J2
(`formation.j2_torus_graph`). Every dynamics here is observer-blind and
strictly local: proposals use canonical-slot draws with FIXED rng
consumption (exact paired coupling for the control design) and consult
the graph only inside ball(R_PROP) of the touched nodes.

Lineage (nothing invented to make gravity travel): U0/U4 = localized
D1-null (scramble / formation-d1); U1 = D1 guillotine with global
partner sampling REPLACED by slot-walk local partners; U2/U3 = blind-U
square greedy/Metropolis with local partners. Census-gated and
target-based rules are excluded (nonlocal) — see prereg §3.
"""
from __future__ import annotations

import math
import random

R_PROP = 4        # all touched nodes within ball(R_PROP) of primary node
R_OBS = 2         # primary observable ball radius
SPAN_RADIUS = 3   # D1 span eval radius (frozen)
SPAN_SMAX = 3     # pristine J2: every edge spans exactly 3 (frozen, §1)
N_SLOTS = 8       # slot range (pristine degree; mapping uses mod deg)
WALK_LEN = 3      # slot-walk length to partner edge (<= R_PROP - 1)

PERTS = ("P1", "P2", "P3", "P4", "Pc-u5")
DYNS = ("U0", "U1", "U2", "U3", "U4")


# ---------------------------------------------------------------- states

def new_state(nbrs: dict) -> dict:
    """Dynamics state: {v: set(neighbors)} (plain dict-of-sets)."""
    return {v: set(s) for v, s in nbrs.items()}


def torus_state(L: int) -> dict:
    """Pristine J2 torus state (int labels, 8-regular, 2L^2 nodes)."""
    from bh_graph.formation import j2_torus_graph

    g = j2_torus_graph(L)
    return {v: set(g.neighbors(v)) for v in g.nodes()}


def bfs_dist(nbrs: dict, src, cutoff: int | None = None) -> dict:
    """Single-source shortest-path lengths (analysis + pristine balls)."""
    dist = {src: 0}
    frontier = [src]
    while frontier:
        nxt = []
        for x in frontier:
            if cutoff is not None and dist[x] >= cutoff:
                continue
            for y in nbrs[x]:
                if y not in dist:
                    dist[y] = dist[x] + 1
                    nxt.append(y)
        frontier = nxt
    return dist


def pristine_geometry(L: int) -> dict:
    """Frozen pristine analysis frame: dist0, shells, balls, ball edges."""
    nbrs = torus_state(L)
    dist0 = bfs_dist(nbrs, 0)
    rmax = max(dist0.values())
    shells: dict[int, list] = {}
    for v, r in dist0.items():
        shells.setdefault(r, []).append(v)
    balls, ball_edges = {}, {}
    for v in nbrs:
        d = bfs_dist(nbrs, v, cutoff=R_OBS)
        b = set(d)
        balls[v] = b
        ball_edges[v] = set()
        for u in b:
            for w in nbrs[u]:
                ball_edges[v].add((u, w) if u < w else (w, u))
    return {"nbrs": nbrs, "dist0": dist0, "rmax": rmax, "shells": shells,
            "balls": balls, "ball_edges": ball_edges}


# ------------------------------------------------------- local evals

def edge_span(nbrs: dict, u, v, radius: int = SPAN_RADIUS) -> int:
    """Shortest u-v path avoiding the direct edge (radius-ball local).

    Same semantics as update_rule.edge_span (radius+1 when unfound).
    """
    seen = {u}
    frontier = [u]
    for depth in range(1, radius + 1):
        nxt = []
        for x in frontier:
            for y in nbrs[x]:
                if (x == u and y == v) or (x == v and y == u):
                    continue
                if y == v:
                    return depth
                if y not in seen:
                    seen.add(y)
                    nxt.append(y)
        frontier = nxt
    return radius + 1


def squares_touching(nbrs: dict, S: set) -> set:
    """Canonical node-sets of 4-cycles touching S (graph-local).

    Same semantics as blind_u._squares_touching.
    """
    out = set()
    for s in S:
        ns = sorted(nbrs[s])
        for i in range(len(ns)):
            for j in range(i + 1, len(ns)):
                for z in set(nbrs[ns[i]]) & set(nbrs[ns[j]]):
                    if z != s:
                        out.add(frozenset((s, ns[i], ns[j], z)))
    return out


def total_longs(nbrs: dict) -> int:
    """Global long census (external diagnostic, never consulted by U)."""
    n = 0
    for u, vs in nbrs.items():
        for v in vs:
            if u < v and edge_span(nbrs, u, v) > SPAN_SMAX:
                n += 1
    return n


def is_connected_state(nbrs: dict) -> bool:
    """Connectivity (external diagnostic only; dynamics never check)."""
    seen = {next(iter(nbrs))}
    stack = list(seen)
    while stack:
        for w in nbrs[stack.pop()]:
            if w not in seen:
                seen.add(w)
                stack.append(w)
    return len(seen) == len(nbrs)


# ------------------------------------------------- canonical proposals

def _sorted_nbrs(nbrs: dict, u) -> list:
    return sorted(nbrs[u])


def _walk(nbrs: dict, u, slots: list[int]) -> int | None:
    """Fixed-length slot-walk; None if a step lands on degree 0."""
    x = u
    for s in slots:
        ns = _sorted_nbrs(nbrs, x)
        if not ns:
            return None
        x = ns[s % len(ns)]
    return x


def draw_swap_proposal(rng: random.Random, n: int) -> tuple:
    """FIXED-consumption draws: (u, sv, sx1..3, sy, f_pair, f_temp).

    rng consumption is graph-independent (exact paired coupling); the
    graph enters only in slot-mapping and validity below.
    """
    u = rng.randrange(n)
    sv = rng.randrange(N_SLOTS)
    sx = [rng.randrange(N_SLOTS) for _ in range(WALK_LEN)]
    sy = rng.randrange(N_SLOTS)
    return (u, sv, sx, sy, rng.random(), rng.random())


def map_swap(nbrs: dict, prop: tuple) -> tuple | None:
    """Map slot draws to edge pair ((u,v),(x,y)); None if invalid.

    Both edges exist by construction; x is a <=3-walk from u so every
    touched node is within ball(4, u) — strictly local.
    """
    u, sv, sx, sy, f_pair, _ = prop
    nu = _sorted_nbrs(nbrs, u)
    if not nu:
        return None
    v = nu[sv % len(nu)]
    x = _walk(nbrs, u, sx)
    if x is None:
        return None
    nx_ = _sorted_nbrs(nbrs, x)
    if not nx_:
        return None
    y = nx_[sy % len(nx_)]
    if len({u, v, x, y}) < 4:
        return None
    if f_pair < 0.5:
        (u1, v1), (u2, v2) = (u, y), (x, v)
    else:
        (u1, v1), (u2, v2) = (u, x), (v, y)
    if v1 in nbrs[u1] or v2 in nbrs[u2]:
        return None
    return ((u, v), (x, y), (u1, v1), (u2, v2))


def _apply_swap(nbrs: dict, m: tuple) -> None:
    (a, b), (c, d), (u1, v1), (u2, v2) = m
    nbrs[a].remove(b)
    nbrs[b].remove(a)
    nbrs[c].remove(d)
    nbrs[d].remove(c)
    nbrs[u1].add(v1)
    nbrs[v1].add(u1)
    nbrs[u2].add(v2)
    nbrs[v2].add(u2)


def step_swap(nbrs: dict, rng: random.Random, mode: str, T: float = 1.0) -> bool:
    """One canonical local-swap proposal; True iff accepted.

    mode: drift (U0), guillotine (U1), square (U2), metropolis (U3).
    Takes only (state, rng, mode, T): no pristine/distance arguments
    exist by construction (anti-smuggling; pinned by test).
    """
    n = len(nbrs)
    prop = draw_swap_proposal(rng, n)
    m = map_swap(nbrs, prop)
    if m is None:
        return False
    (a, b), _, (u1, v1), (u2, v2) = m
    if mode == "drift":
        _apply_swap(nbrs, m)
        return True
    if mode == "guillotine":
        if edge_span(nbrs, a, b) <= SPAN_SMAX:
            return False
        _apply_swap(nbrs, m)
        ok = (edge_span(nbrs, u1, v1) <= SPAN_SMAX
              and edge_span(nbrs, u2, v2) <= SPAN_SMAX)
        if ok:
            return True
        _apply_swap(nbrs, ((u1, v1), (u2, v2), (a, b), m[1]))
        return False
    S = {a, b, m[1][0], m[1][1]}
    before = len(squares_touching(nbrs, S))
    _apply_swap(nbrs, m)
    after = len(squares_touching(nbrs, S))
    if mode == "square":
        if after > before:
            return True
    elif mode == "metropolis":
        d = after - before
        if d > 0 or (T > 0 and (d == 0 or prop[5] < math.exp(d / T))):
            return True
    else:
        raise ValueError(f"unknown swap mode: {mode}")
    _apply_swap(nbrs, ((u1, v1), (u2, v2), (a, b), m[1]))
    return False


def draw_reloc_proposal(rng: random.Random, n: int) -> tuple:
    """FIXED-consumption draws for local relocation (U4/P3-compatible)."""
    u = rng.randrange(n)
    sv = rng.randrange(N_SLOTS)
    sc = [rng.randrange(N_SLOTS) for _ in range(WALK_LEN)]
    sd = [rng.randrange(N_SLOTS) for _ in range(WALK_LEN)]
    return (u, sv, sc, sd, rng.random())


def map_reloc(nbrs: dict, prop: tuple) -> tuple | None:
    """Map slot draws to ((a,b),(c,d)); None if invalid.

    Loser (a,b) is an edge; gainer (c,d) a non-edge; all four nodes
    within ball(3, u) — strictly local.
    """
    u, sv, sc, sd, _ = prop
    nu = _sorted_nbrs(nbrs, u)
    if not nu:
        return None
    a, b = u, nu[sv % len(nu)]
    c = _walk(nbrs, u, sc)
    d = _walk(nbrs, u, sd)
    if c is None or d is None or c == d:
        return None
    if (a, b) == (c, d) or (a, b) == (d, c):
        return None
    if d in nbrs[c]:
        return None
    return ((a, b), (c, d))


def step_reloc(nbrs: dict, rng: random.Random) -> bool:
    """One canonical local-relocation proposal (U4 drift); True iff applied."""
    m = map_reloc(nbrs, draw_reloc_proposal(rng, len(nbrs)))
    if m is None:
        return False
    (a, b), (c, d) = m
    nbrs[a].remove(b)
    nbrs[b].remove(a)
    nbrs[c].add(d)
    nbrs[d].add(c)
    return True


# ------------------------------------------------------- perturbations

def _ball2_set(geo: dict) -> set:
    return {v for v, r in geo["dist0"].items() if r <= 2}


def apply_pert(L: int, pert: str, seed: int, geo: dict | None = None) -> dict:
    """Perturbed J2 torus (fresh state). Deterministic in (pert, seed).

    Uses its own rng stream — never the trajectory stream (coupling).
    """
    import networkx as nx

    from bh_graph.formation import j2_torus_graph

    if pert not in PERTS:
        raise ValueError(f"unknown pert: {pert}")
    geo = geo or pristine_geometry(L)
    rng = random.Random(f"grav0-pert-{pert}-{seed}")
    g = j2_torus_graph(L)
    ball = _ball2_set(geo)
    if pert in ("P1", "P2"):
        want = 1 if pert == "P1" else 10
        ap = 0
        for _ in range(50000):
            if ap >= want:
                break
            E = [e for e in g.edges() if e[0] in ball and e[1] in ball]
            (a, b), (c, d) = rng.sample(E, 2)
            if len({a, b, c, d}) < 4:
                continue
            if g.has_edge(a, d) or g.has_edge(c, b):
                continue
            g.remove_edge(a, b)
            g.remove_edge(c, d)
            g.add_edge(a, d)
            g.add_edge(c, b)
            ap += 1
        assert ap == want, (pert, ap, want)
    elif pert == "P3":
        nbrs0 = sorted(g.neighbors(0))
        v = nbrs0[rng.randrange(len(nbrs0))]
        g.remove_edge(0, v)
        nonedges = []
        bl = sorted(ball)
        for i, x in enumerate(bl):
            for y in bl[i + 1:]:
                if not g.has_edge(x, y):
                    nonedges.append((x, y))
        c, d = rng.choice(nonedges)
        g.add_edge(c, d)
    elif pert == "P4":
        nbrs0 = sorted(g.neighbors(0))
        c4s = []
        for i in range(len(nbrs0)):
            for j in range(i + 1, len(nbrs0)):
                for z in sorted(set(g[nbrs0[i]]) & set(g[nbrs0[j]])):
                    if z != 0:
                        c4s.append([(0, nbrs0[i]), (nbrs0[i], z),
                                    (z, nbrs0[j]), (nbrs0[j], 0)])
        c4 = rng.choice(sorted(map(tuple, c4s)))
        g.remove_edges_from(c4)
        assert nx.is_connected(g)
    elif pert == "Pc-u5":
        nx.connected_double_edge_swap(g, 5, seed=rng.randrange(2**31))
    return {v: set(g.neighbors(v)) for v in g.nodes()}


# ------------------------------------------------------- observables

def disturbance_field(nbrs: dict, geo: dict) -> dict:
    """Primary δg_i: ball(R_OBS) edge-symmetric-difference vs pristine."""
    out = {}
    for v in nbrs:
        cur = set()
        for u in geo["balls"][v]:
            for w in nbrs[u]:
                cur.add((u, w) if u < w else (w, u))
        base = geo["ball_edges"][v]
        out[v] = len(cur ^ base) / max(len(base), 1)
    return out


def radial_profile(field: dict, geo: dict, rmax: int | None = None) -> dict:
    """Shell means D(r) at pristine distance r from node 0."""
    if rmax is None:
        rmax = geo["rmax"]
    acc: dict[int, list] = {}
    for v, val in field.items():
        r = geo["dist0"][v]
        if r <= rmax:
            acc.setdefault(r, []).append(val)
    return {r: sum(v) / len(v) for r, v in sorted(acc.items())}


def secondary_fields(nbrs: dict, geo: dict) -> dict:
    """Secondaries: incident-adj, span-excess, |deg-8|, C4-touch-dev."""
    f_adj, f_span, f_deg = {}, {}, {}
    for v, vs in nbrs.items():
        cur = set(vs)
        base = set(geo["nbrs"][v])
        f_adj[v] = len(cur ^ base) / max(len(base), 1)
        inc = [w for w in vs]
        f_span[v] = (sum(1 for w in inc if edge_span(nbrs, v, w) > SPAN_SMAX)
                     / max(len(inc), 1))
        f_deg[v] = abs(len(vs) - 8)
    return {"adj1": f_adj, "span": f_span, "deg": f_deg}


# ------------------------------------------------------- trajectories

_STEP = {"U0": ("swap", "drift"), "U1": ("swap", "guillotine"),
         "U2": ("swap", "square"), "U3": ("swap", "metropolis"),
         "U4": ("reloc", None)}


def run_trajectory(L: int, pert: str | None, dyn: str, seed: int,
                   ticks: int, snapshot_every: int = 5,
                   T: float = 20.0, secondaries: bool = False) -> dict:
    """One (pert, dyn, L, seed) trajectory; pert=None is the control leg.

    Trajectory rng = Random(seed): pert/control legs consume identical
    streams (exact coupling). Returns snapshots {t: {r: D}}, accepts,
    connectivity flag, long census.
    """
    if dyn not in DYNS:
        raise ValueError(f"unknown dyn: {dyn}")
    geo = pristine_geometry(L)
    nbrs = apply_pert(L, pert, seed, geo) if pert else new_state(geo["nbrs"])
    n = len(nbrs)
    rng = random.Random(seed)
    kind, mode = _STEP[dyn]
    snaps = {0: radial_profile(disturbance_field(nbrs, geo), geo)}
    secs = {0: {k: radial_profile(f, geo)
                for k, f in secondary_fields(nbrs, geo).items()}} if secondaries else {}
    accepts = []
    for t in range(1, ticks + 1):
        acc = 0
        for _ in range(n):
            if kind == "swap":
                acc += step_swap(nbrs, rng, mode, T)
            else:
                acc += step_reloc(nbrs, rng)
        accepts.append(acc)
        if t % snapshot_every == 0 or t == ticks:
            snaps[t] = radial_profile(disturbance_field(nbrs, geo), geo)
            if secondaries:
                secs[t] = {k: radial_profile(f, geo)
                           for k, f in secondary_fields(nbrs, geo).items()}
    return {"L": L, "pert": pert, "dyn": dyn, "seed": seed, "ticks": ticks,
            "snapshots": snaps, "accepts": accepts,
            "connected": is_connected_state(nbrs),
            "longs_final": total_longs(nbrs),
            "secondaries": secs}


# ------------------------------------------------------- front analysis

def delta_profiles(pert_snaps: dict, ctrl_snaps: dict) -> dict:
    """Paired ripple ΔD(r,t) = D_pert − D_ctrl (same ticks)."""
    return {t: {r: pert_snaps[t][r] - ctrl_snaps[t].get(r, 0.0)
                for r in pert_snaps[t]}
            for t in pert_snaps}


def mean_delta(deltas: list[dict]) -> tuple[dict, dict]:
    """Seed-mean ΔD̄(r,t) and SEM(r,t) over paired deltas."""
    ts = sorted(deltas[0])
    mean, sem = {}, {}
    import statistics as st

    for t in ts:
        rs = sorted(deltas[0][t])
        mean[t], sem[t] = {}, {}
        for r in rs:
            xs = [d[t][r] for d in deltas]
            mean[t][r] = sum(xs) / len(xs)
            sem[t][r] = (st.pstdev(xs) / math.sqrt(len(xs))) if len(xs) > 1 else 0.0
    return mean, sem


def front_radii(mean_delta_: dict, theta: float) -> dict:
    """r_front(t) = max r with ΔD̄(r,t) > θ (−1 if none)."""
    out = {}
    for t in sorted(mean_delta_):
        rs = [r for r, v in mean_delta_[t].items() if v > theta]
        out[t] = max(rs) if rs else -1
    return out


def fit_front(times: list, radii: list) -> dict:
    """Linear (ballistic) vs sqrt (diffusive) fits with R² (numpy)."""
    import numpy as np

    t = np.array(times, dtype=float)
    r = np.array(radii, dtype=float)
    out = {}
    if len(t) >= 3 and np.ptp(r) > 0:
        b1, a1 = np.polyfit(t, r, 1)
        p1 = a1 + b1 * t
        ss = float(np.sum((r - p1) ** 2))
        st_ = float(np.sum((r - r.mean()) ** 2))
        out["ballistic"] = {"v": float(b1), "r0": float(a1),
                            "r2": 1 - ss / st_}
        b2, a2 = np.polyfit(t, r ** 2, 1)
        p2 = a2 + b2 * t
        ss2 = float(np.sum((r ** 2 - p2) ** 2))
        st2 = float(np.sum((r ** 2 - (r ** 2).mean()) ** 2))
        out["diffusive"] = {"D": float(b2 / 2), "c": float(a2),
                            "r2": 1 - ss2 / st2 if st2 > 0 else 0.0}
    else:
        out["ballistic"] = {"v": 0.0, "r0": float(r[0]) if len(r) else 0.0,
                            "r2": 0.0}
        out["diffusive"] = {"D": 0.0, "c": 0.0, "r2": 0.0}
    return out
