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

import random

import networkx as nx


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
) -> dict:
    """Run D1 (ungated) / D3 (floppy-gated, OR) relocation to a stop rule.

    Sweep = E0 proposals (attempts incl. blocks/Nones). Stops: stillborn
    (zero executes in first w_arrest sweeps -> INVALID, checked first),
    arrest (trailing w_arrest sweeps zero), stationary (hist L1 <
    stat_tol over stat_window), cap (t_max, UNRESOLVED). Snapshots every
    10 sweeps. Deterministic given seed. Returns the full filing record.
    """
    if driver not in ("d1", "d3"):
        raise ValueError(f"unknown driver: {driver}")
    st = {
        "nodes": list(st0["nodes"]),
        "nbrs": {v: set(s) for v, s in st0["nbrs"].items()},
        "elist": list(st0["elist"]),
        "epos": dict(st0["epos"]),
    }
    e0, n = len(st["elist"]), len(st["nodes"])
    h0 = coord_hist(st)
    rng = random.Random(seed)
    nbrs = st["nbrs"]
    per_sweep, snaps, stop, sw = [], {}, None, 0
    while sw < t_max:
        sw += 1
        done = 0
        for _ in range(e0):
            prop = propose_relocation(st, rng)
            if prop is None:
                continue
            (a, b), (c, d) = prop
            if driver == "d3" and not (len(nbrs[a]) < thr or len(nbrs[b]) < thr):
                continue
            _remove_edge(st, (a, b))
            _add_edge(st, (c, d))
            nbrs[a].remove(b)
            nbrs[b].remove(a)
            nbrs[c].add(d)
            nbrs[d].add(c)
            done += 1
        per_sweep.append(done)
        if sw % 10 == 0:
            snaps[sw] = coord_hist(st)
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
    return {
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
    }
