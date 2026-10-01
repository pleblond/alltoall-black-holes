"""C2 formation dynamics: E-conserving relocation on dense soup (D14).

Minimal formation machine (pre-registered): fixed-N graphs evolve by edge
relocation (remove a uniform random edge, add a uniform random non-edge;
E conserved exactly, degrees change). Drivers: D1 null (ungated) and D3
floppy-gated kinetics (KCM class: execute iff a loser endpoint is floppy,
local z < threshold). State is plain-Python (dict-of-sets + indexed edge
list) for a fast hot loop; nx adapters at the boundary. Deterministic
given seed (random.Random + sorted construction; see per-function notes).
"""

from __future__ import annotations

import math
import random

import networkx as nx

POISSON_TAIL = 40  # support cap for Poisson reference distributions


def triangles_on_pair(st: dict, a, b) -> int:
    """Common-neighbor count |N(a) ∩ N(b)| (Δt: triangles an (a,b) edge
    closes (non-edge) or holds (edge); 1-hop-local, H-gate-clean)."""
    return len(st["nbrs"][a] & st["nbrs"][b])


def triangle_count(st: dict) -> int:
    """Exact triangle total (Σ over edges of Δt / 3 — each counted 3×)."""
    return sum(triangles_on_pair(st, a, b) for a, b in st["elist"]) // 3


def accept_d5(net: int, kappa: float, rng: random.Random) -> bool:
    """Net-Δt Metropolis accept (D5κ gain-side; Strauss-canonical).

    Short-circuit (LOCKED rng-parity): draws rng ONLY when net < 0
    and kappa > 0 — kappa=0 never draws (⟹ κ0 ≡ D1 trajectory).
    """
    if kappa == 0 or net >= 0:
        return True
    return rng.random() < math.exp(kappa * net)


def truss_count_k(g: nx.Graph, k: int, min_frac: float) -> tuple:
    """Macro-floored component count/size at fixed-k truss (trace readout).

    Returns (count, kmax_size, sizes-desc). k=5 ⟹ K5+-nuclei tracker.
    """
    t = nx.k_truss(g, k)
    if t.number_of_nodes() == 0:
        return 0, 0, []
    sizes = sorted((len(c) for c in nx.connected_components(t)), reverse=True)
    floor = math.ceil(min_frac * g.number_of_nodes())
    big = [s for s in sizes if s >= floor]
    return len(big), big[0] if big else 0, sizes


def truss_kmax(g: nx.Graph) -> int:
    """Binary-searched max-k with nonempty k-truss (clique-core scale)."""
    lo, hi = 2, 3
    while nx.k_truss(g, hi).number_of_nodes() > 0:
        lo, hi = hi, 2 * hi - 2
        if hi > g.number_of_nodes():
            return g.number_of_nodes()
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if nx.k_truss(g, mid).number_of_nodes() > 0:
            lo = mid
        else:
            hi = mid
    return lo


def truss_profile(g: nx.Graph, min_frac: float) -> dict:
    """Log-spaced k-truss profile + top-truss macro components (finals/mids)."""
    kmax = truss_kmax(g)
    ks = sorted({k for k in [2, 3, 4, 5, 6, 8, 10, 14, 20, 28, 40, 56, 80] if k <= kmax} | {kmax})
    prof = {}
    for k in ks:
        c, m, _ = truss_count_k(g, k, min_frac)
        prof[k] = {"count": c, "kmax_size": m}
    t = nx.k_truss(g, kmax)
    sizes = (
        sorted((len(c) for c in nx.connected_components(t)), reverse=True)
        if t.number_of_nodes()
        else []
    )
    floor = math.ceil(min_frac * g.number_of_nodes())
    return {
        "kmax": kmax,
        "by_k": prof,
        "top_sizes": sizes,
        "top_macro": [s for s in sizes if s >= floor],
    }


def charikar_core(st: dict) -> set:
    """Greedy-peeling dense subgraph (Charikar 2-approx; cross-check)."""
    nbrs = {v: set(s) for v, s in st["nbrs"].items()}
    alive, best, best_d = set(nbrs), set(nbrs), -1.0
    import heapq

    heap = [(len(nbrs[v]), v) for v in alive]
    heapq.heapify(heap)
    edges = sum(len(s) for s in nbrs.values()) // 2
    while alive:
        d = edges / len(alive) if alive else 0
        if d > best_d:
            best_d, best = d, set(alive)
        while heap:
            _, v = heapq.heappop(heap)
            if v in alive:
                break
        alive.discard(v)
        for w in nbrs[v]:
            if w in alive:
                nbrs[w].discard(v)
                heapq.heappush(heap, (len(nbrs[w]), w))
                edges -= 1
    return best


def poisson_l1(hist: dict, lam: float, n: int) -> float:
    """L1 departure of a histogram from Poisson(lam) (formation metric)."""
    out, tot = 0.0, 0
    for z in range(POISSON_TAIL):
        p = math.exp(-lam) * lam**z / math.factorial(z)
        out += abs(hist.get(z, 0) / n - p)
        tot += hist.get(z, 0)
    return out + max(0, (n - tot)) / n


def soup_graph(kind: str, n: int, zbar, seed: int) -> nx.Graph:
    """Primordial soup: homogeneous dense initial graph (int labels).

    kind "er": G(n, p=zbar/(n-1)); kind "rr": random zbar-regular
    (zbar int, n*zbar even). d_* measured-never-tuned: report
    soup_signature alongside every result using this.
    """
    if kind == "er":
        return nx.fast_gnp_random_graph(n, zbar / (n - 1), seed=seed)
    if kind == "rr":
        return nx.random_regular_graph(int(zbar), n, seed=seed)
    raise ValueError(f"unknown soup kind: {kind}")


def j2_torus_graph(L: int) -> nx.Graph:
    """J2 torus ((Z_L)^2 ⋊ Z2) Cayley graph (vertex-transitive soup).

    Nodes (x, y, b) with x, y in Z_L, b in {0, 1}; int labels
    id = (x * L + y) * 2 + b (see j2_torus_coords). Edges from the
    8 inverse-closed generators (spatial (±1,0)/(0,±1), sheet-flip
    half of them); swap action on the sheet bit. 8-regular,
    2L^2 nodes, exactly symmetric (no quenched disorder: the
    orientation-SSB test substrate). Deterministic (no seed).
    """
    gens = (
        (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0),
        (1, 0, 1), (-1, 0, 1), (0, 1, 1), (0, -1, 1),
    )
    n = 2 * L * L
    g = nx.Graph()
    g.add_nodes_from(range(n))
    for x in range(L):
        for y in range(L):
            for b in (0, 1):
                p = (x * L + y) * 2 + b
                for u, v, d in gens:
                    a1, a2 = (u, v) if b == 0 else (v, u)
                    q = (((x + a1) % L) * L + ((y + a2) % L)) * 2 + ((b + d) % 2)
                    if q != p:
                        g.add_edge(p, q)
    return g


def j2_torus_coords(L: int) -> dict:
    """Inverse labels: id -> (x, y, b) (readout basis for orientation)."""
    return {(x * L + y) * 2 + b: (x, y, b) for x in range(L) for y in range(L) for b in (0, 1)}


def soup_signature(g: nx.Graph, src=0) -> dict:
    """Measured d_* proxies: size/budget/degrees + BFS depth from src."""
    d = dict(nx.single_source_shortest_path_length(g, src))
    degs = [dd for _, dd in g.degree()]
    return {
        "n": g.number_of_nodes(),
        "e": g.number_of_edges(),
        "zbar": sum(degs) / len(degs),
        "zmin": min(degs),
        "zmax": max(degs),
        "mean_depth": sum(d.values()) / len(d),
        "max_depth": max(d.values()),
        "n_reached": len(d),
    }


def state_from_nx(g: nx.Graph) -> dict:
    """Dynamics state: sorted nodelist + indexed edge list (deterministic)."""
    nodes = sorted(g.nodes())
    elist = sorted(tuple(sorted(e)) for e in g.edges())
    return {
        "nodes": nodes,
        "nbrs": {v: set(g.neighbors(v)) for v in nodes},
        "elist": elist,
        "epos": {e: i for i, e in enumerate(elist)},
    }


def state_to_nx(st: dict) -> nx.Graph:
    """Back to nx (interop/tests; dynamics never needs this)."""
    g = nx.Graph()
    g.add_nodes_from(st["nodes"])
    g.add_edges_from(st["elist"])
    return g


def _remove_edge(st: dict, e):
    i, last = st["epos"].pop(e), st["elist"][-1]
    if e != last:
        st["elist"][i] = last
        st["epos"][last] = i
    st["elist"].pop()


def _add_edge(st: dict, e):
    st["epos"][e] = len(st["elist"])
    st["elist"].append(e)


def propose_relocation(st: dict, rng: random.Random, max_tries: int = 100):
    """Uniform loser edge + uniform gainer non-edge ((a,b),(c,d)) or None.

    None after max_tries rejections (near-complete graphs only; soups
    never hit this — counts as a non-executing proposal, never an error).
    """
    elist, nodes, nbrs = st["elist"], st["nodes"], st["nbrs"]
    a, b = elist[rng.randrange(len(elist))]
    for _ in range(max_tries):
        c, d = nodes[rng.randrange(len(nodes))], nodes[rng.randrange(len(nodes))]
        if c == d:
            continue
        e = (c, d) if c < d else (d, c)
        if e != (a, b) and d not in nbrs[c]:
            return (a, b), e
    return None


def coord_hist(st: dict) -> dict:
    """Degree histogram {z: count} (includes z=0 dust bin)."""
    h: dict = {}
    for v in st["nodes"]:
        z = len(st["nbrs"][v])
        h[z] = h.get(z, 0) + 1
    return h


def _local_maxima(h: dict, min_mass: int = 2) -> list:
    """Local maxima with count >= min_mass (guarded: a phase is never
    one node; min_mass=1 recovers the letter statistic)."""
    out = []
    for z in sorted(h):
        if h.get(z, 0) < min_mass:
            continue
        if h.get(z, 0) > h.get(z - 1, 0) and h.get(z, 0) >= h.get(z + 1, 0):
            out.append(z)
    return out


def valley_ratio(h: dict, min_mass: int = 2, connected: bool = True) -> float:
    """Bimodality gate: valley-min / lower-peak over the two highest maxima.

    Maxima ranked by (-height, z); valley = min over the closed interval.
    Fewer than two maxima -> 1.0 (unimodal). Bimodal iff ratio < 0.5
    (labeled threshold). min_mass=2 default (guarded); 1 = letter.
    connected=True (default): intervals with interior empty bins are
    disconnected islands (not saddles) -> 1.0 (textbook bimodality needs
    a saddle, not a gap; D3-dust gaps reclassify as dusty-unimodal and
    still fail WEAK via lower-mode; caveat: may under-call complete
    separation in future drivers — revisit if gapped non-dust support
    ever appears). Deterministic.
    """
    ms = sorted(_local_maxima(h, min_mass), key=lambda z: (-h[z], z))[:2]
    if len(ms) < 2:
        return 1.0
    lo, hi = min(ms), max(ms)
    if connected and any(h.get(z, 0) == 0 for z in range(lo + 1, hi)):
        return 1.0
    return min(h.get(z, 0) for z in range(lo, hi + 1)) / min(h[lo], h[hi])


def mode_locations(h: dict, min_mass: int = 2) -> list:
    """The (up to two) ranked maxima [(z, count)] (measured, no targets)."""
    ms = sorted(_local_maxima(h, min_mass), key=lambda z: (-h[z], z))[:2]
    return [(z, h[z]) for z in ms]


def l1_hist(h1: dict, h2: dict, n: int) -> float:
    """L1 distance over probability vectors (union support)."""
    return sum(abs(h1.get(z, 0) - h2.get(z, 0)) for z in set(h1) | set(h2)) / n


def giant_fraction(st: dict) -> float:
    """Largest-component node fraction (BFS; health readout)."""
    nbrs, seen, best = st["nbrs"], set(), 0
    for s in st["nodes"]:
        if s in seen:
            continue
        stack, comp = [s], 0
        seen.add(s)
        while stack:
            comp += 1
            for w in nbrs[stack.pop()]:
                if w not in seen:
                    seen.add(w)
                    stack.append(w)
        best = max(best, comp)
    return best / len(st["nodes"])


def component_sizes(st: dict) -> list:
    """All component sizes, descending (filed full, not gated)."""
    nbrs, seen, out = st["nbrs"], set(), []
    for s in st["nodes"]:
        if s in seen:
            continue
        stack, comp = [s], 0
        seen.add(s)
        while stack:
            comp += 1
            for w in nbrs[stack.pop()]:
                if w not in seen:
                    seen.add(w)
                    stack.append(w)
        out.append(comp)
    return sorted(out, reverse=True)


def assortativity(st: dict) -> float:
    """Degree assortativity (Pearson over edges; float-summation order
    follows elist — pin with tolerance, never exact)."""
    nbrs = st["nbrs"]
    xs = [(len(nbrs[a]), len(nbrs[b])) for a, b in st["elist"]]
    n = len(xs)
    sx = sum(x + y for x, y in xs) / (2 * n)
    sxx = sum(x * x + y * y for x, y in xs) / (2 * n)
    sxy = sum(x * y for x, y in xs) / n
    denom = sxx - sx * sx
    if denom == 0:
        return None  # undefined for zero-variance (regular) graphs (JSON-safe None, not NaN)
    return (sxy - sx * sx) / denom


def formation_run(
    st0: dict,
    driver: str,
    thr: int,
    seed: int,
    w_arrest: int = 20,
    stat_window: int = 50,
    stat_tol: float = 0.02,
    t_max: int = 2000,
    kappa: float = 0.0,
    return_state: bool = False,
    log_stride: int = 0,
    log_window: tuple | None = None,
    k5_window: tuple | None = None,
    k4_window: tuple | None = None,
    log_endpoints: bool = False,
) -> dict:
    """Run D1/D3/D5-family relocation to a stop rule.

    Drivers: d1 (ungated), d3 (floppy-gated loss, OR), d5k (D1-propose
    + net-Δt Metropolis accept (kappa)), d5inf (D1-propose + close-only
    gain (Δt_gain ≥ 1)), d35 (D3-loss × κ-gain). kappa=0 ⟹ d5k ≡ d1
    (short-circuit rng-parity (locked!)).
    Sweep = E0 proposals (attempts incl. blocks/Nones). Stops: stillborn
    (zero executes in first w_arrest sweeps -> INVALID, checked first),
    arrest (trailing w_arrest sweeps zero), stationary (hist L1 <
    stat_tol over stat_window), cap (t_max, UNRESOLVED). Snapshots every
    10 sweeps (hist + k5-truss-count); every-100th state saved (mids
    profiles offline); T (triangles) tracked incrementally every sweep.
    Anatomy (pure observation, never perturbs dynamics): log_stride>0
    logs every log_stride-th proposal as (sweep, t_loss, t_gain,
    accepted) within log_window (sweep range or None); log_endpoints
    widens rows to (sweep, a, b, c, d, t_loss, t_gain, accepted);
    k5_window logs per-sweep k5-count in range; k4_window logs
    per-sweep floored-k4-core node sets (blob tracking). Deterministic
    given seed. Returns the full filing record (+ state iff
    return_state).
    """
    if driver not in ("d1", "d3", "d5k", "d5inf", "d35"):
        raise ValueError(f"unknown driver: {driver}")
    st = {
        "nodes": list(st0["nodes"]),
        "nbrs": {v: set(s) for v, s in st0["nbrs"].items()},
        "elist": list(st0["elist"]),
        "epos": dict(st0["epos"]),
    }
    e0, n = len(st["elist"]), len(st["nodes"])
    h0 = coord_hist(st)
    t_now = triangle_count(st)
    t0 = t_now
    lam = 2 * e0 / n
    rng = random.Random(seed)
    nbrs = st["nbrs"]
    per_sweep, snaps, k5trace, saved, t_trace = [], {}, {}, {}, []
    moves, k5win, k4sets = [], {}, {}
    prop_n = 0

    def log_move(sw_, a_, b_, c_, d_, loss_, gain_, acc_):
        if log_endpoints:
            moves.append((sw_, a_, b_, c_, d_, loss_, gain_, acc_))
        else:
            moves.append((sw_, loss_, gain_, acc_))
    stop, sw = None, 0
    while sw < t_max:
        sw += 1
        done = 0
        for _ in range(e0):
            prop = propose_relocation(st, rng)
            if prop is None:
                continue
            (a, b), (c, d) = prop
            prop_n += 1
            logging = (
                log_stride > 0
                and prop_n % log_stride == 0
                and (log_window is None or log_window[0] <= sw <= log_window[1])
            )
            if driver in ("d3", "d35") and not (len(nbrs[a]) < thr or len(nbrs[b]) < thr):
                if logging:
                    log_move(sw, a, b, c, d, None, None, False)
                continue
            gain = len(nbrs[c] & nbrs[d])
            loss = len(nbrs[a] & nbrs[b])
            # Overlap correction (exact ΔT): pre-removal N includes the
            # removed endpoint — triangles using edge (a,b) are not real.
            if c == a:
                gain -= 1 if b in nbrs[d] else 0
            elif c == b:
                gain -= 1 if a in nbrs[d] else 0
            if d == a:
                gain -= 1 if b in nbrs[c] else 0
            elif d == b:
                gain -= 1 if a in nbrs[c] else 0
            if driver in ("d5k", "d35"):
                if not accept_d5(gain - loss, kappa, rng):
                    if logging:
                        log_move(sw, a, b, c, d, loss, gain, False)
                    continue
            elif driver == "d5inf" and gain < 1:
                if logging:
                    log_move(sw, a, b, c, d, loss, gain, False)
                continue
            if logging:
                log_move(sw, a, b, c, d, loss, gain, True)
            _remove_edge(st, (a, b))
            _add_edge(st, (c, d))
            nbrs[a].remove(b)
            nbrs[b].remove(a)
            nbrs[c].add(d)
            nbrs[d].add(c)
            t_now += gain - loss
            done += 1
        per_sweep.append(done)
        t_trace.append(t_now)
        if sw % 10 == 0:
            snaps[sw] = coord_hist(st)
            k5trace[sw] = truss_count_k(state_to_nx(st), 5, 0.01)
        if k5_window is not None and k5_window[0] <= sw <= k5_window[1] and sw % 10 != 0:
            k5win[sw] = truss_count_k(state_to_nx(st), 5, 0.01)
        if k4_window is not None and k4_window[0] <= sw <= k4_window[1]:
            t4 = nx.k_truss(state_to_nx(st), 4)
            fl = max(2, -(-n // 100))
            big = (
                [c for c in nx.connected_components(t4) if len(c) >= fl]
                if t4.number_of_nodes()
                else []
            )
            k4sets[sw] = sorted(set().union(*big)) if big else []
        if sw % 100 == 0:
            saved[sw] = list(st["elist"])
        if sw == w_arrest and sum(per_sweep) == 0:
            stop = "stillborn"
            break
        if sw > w_arrest and sum(per_sweep[-w_arrest:]) == 0:
            stop = "arrest"
            break
        if (
            sw >= stat_window
            and sw % 10 == 0
            and sw - stat_window in snaps
            and l1_hist(snaps[sw], snaps[sw - stat_window], n) < stat_tol
        ):
            stop = "stationary"
            break
    if stop is None:
        stop = "cap"
    hf = coord_hist(st)
    rec = {
        "stop": stop,
        "sweeps": sw,
        "executes_total": sum(per_sweep),
        "executes_trace": per_sweep,
        "e_final": len(st["elist"]),
        "e0": e0,
        "hist_initial": h0,
        "hist_final": hf,
        "snaps": {sw: dict(h) for sw, h in snaps.items()},
        "valley_initial": valley_ratio(h0),
        "valley_final": valley_ratio(hf),
        "modes_final": mode_locations(hf),
        "giant_final": giant_fraction(st),
        "comp_sizes_final": component_sizes(st),
        "assort_final": assortativity(st),
        "assort_initial": assortativity(st0),
        "t0": t0,
        "t_trace": t_trace,
        "t_final": t_now,
        "k5_trace": {sw: list(v) for sw, v in k5trace.items()},
        "saved": {sw: [list(e) for e in el] for sw, el in saved.items()},
        "dep_initial": poisson_l1(h0, lam, n),
        "dep_final": poisson_l1(hf, lam, n),
        "moves": moves,
        "k5win": {sw: list(v) for sw, v in k5win.items()},
        "k4sets": {sw: list(v) for sw, v in k4sets.items()},
    }
    if return_state:
        return rec, st
    return rec
