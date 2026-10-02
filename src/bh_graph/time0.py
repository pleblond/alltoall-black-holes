"""TIME-0 two-boundary history selection: exact tiny-domain census.

Campaign: TIME-0. Tests whether globally constrained histories resolve the
forward-state underdetermination banked by U0 (U0-INCOMPLETE: splits
unrealized) under the frozen ontology X = (G, psi). The candidate object is
a complete history Gamma = (X_0, ..., X_T) satisfying LOCAL pairwise
compatibility plus two microscopic boundary conditions X_0 = X_-, X_T = X_+.

Frozen inputs (read-only; never re-derived, never modified):
  - Graph maps (BR-2.5): contract_edge / split_covers / apply_split_cover,
    simple-graph kind, sum map psi_k = psi_i + psi_j, R_U = 1.
  - Ledger (BR-2.6/CONS-0): event_ledger (dE = 2B - 2 sum_cross, MINUS
    convention), dQ = +2B_ij, cycle-rank law dxi = -c, no-go (no
    field-involving linear invariant closes arbitrary contractions).
  - No-mode (BR-2.7): no instability/firing mechanism in the frozen
    ontology; contraction/split is treated as an admissible RELATION
    between neighboring temporal states, never as an event selected by X_t.
  - Field law: H(G) = -A(G), J = 1, hbar = 1, i dpsi/dt = -A psi via
    ballistic.evolve_fixed (Krylov, exact-unitary, deterministic).
  - Split census (U0-H4): undirected_covers ((3^d + 1)/2), no earned
    quantity selects a cover (J-guided vs B-guided differ on banked
    states); dt = DT_DEFAULT = 0.1 (P1-frozen, not a new parameter).

Frozen TIME-0 conventions (TIME0-PREREG, pre-data):
  - Headline = graph sector (V0 zero-field psi = 0 exactly): field
    compatibility is then closed trivially (0 -> 0 under sum map,
    sum-relation, and unitary steps), so canonical-class enumeration is
    finite and EXACT. Field sectors enter only through labeled spot
    cases (R-control, constructed I/J cases) with exact propagation.
  - Canonical universe: connected non-isomorphic simple graphs, N in
    1..6, representatives from nx.graph_atlas_g (deterministic order,
    contiguous int labels). cid = (N, k), k = same-N atlas position.
    N = 7 splits are dropped + counted (bounded-universe boundary,
    filed openly); robustness reruns on N <= 5 and an N <= 7 spot.
  - Pairwise compatibility (R_time = 1): a step is exactly one of
    IDENTITY (same class; psi' = U(G) psi), CONTRACTION (one-edge
    BR-2.5 quotient; psi'_k = psi_i + psi_j), SPLIT (one-node
    record-free cover, children adjacent; psi'_i + psi'_j = psi_k,
    the exact reverse of the sum map -- the unique relation making
    contraction steps reversible as relations). Evolution rides
    identity steps only. Hard constraints = structural adjacency +
    these field relations. Ledger quantities (dN, dE_G, dQ, dE_psi,
    dxi, triangles, B/L) are DESCRIPTIVE, never gating (CONS-0 no-go).
  - Labeled mode (N <= 4, descriptive/cross-check): contiguous labels
    0..N-1 with the TIME-0 downshift rule (contraction keeps i, drops
    j, shifts > j down; split w -> (w, N_new)); bridged to BR-2.5 ops
    by isomorphism + field-multiset pins on every transition.
  - Counting is exact DP over walks (bigints), never sampled; explicit
    walk materialization only for capped audit cases.
  - Time reversal Theta: reverse slice order + conjugate fields.
    V0-exact; 1e-9 field tolerance (Krylov grade) in field sectors.

This module introduces NO firing rule, NO threshold, NO rate, NO
objective/scoring over histories, NO new ontology (no records, clocks,
weights, hidden labels). Tolerances below are numerical identities.
"""

from __future__ import annotations

import networkx as nx
import numpy as np

from bh_graph.ballistic import (
    DT_DEFAULT,
    evolve_fixed,
    hamiltonian,
    index_of,
    node_order,
)

DT_FROZEN = float(DT_DEFAULT)
N_MIN = 1
N_MAX = 6
T_GRID = (2, 3, 4, 5, 6)
ATOL_FIELD = 1e-9
ATOL_REVERSIBLE = 1e-12

KIND_IDENTITY = "I"
KINDS = (KIND_IDENTITY, "C", "S")

# Verdict thresholds (frozen pre-data; see TIME0-PREREG).
F_UNIQUE_NULL_BELOW = 0.2
F_UNIQUE_UNIQUE_ABOVE = 0.8
F_UNIQUE_WORST_T_MIN = 0.6
F_COMPAT_UNIQUE_MIN = 0.1
SPLIT_RESOLVE_UNIQUE_MIN = 0.8


# ---------------------------------------------------------------------------
# Section 1: canonical tiny universe
# ---------------------------------------------------------------------------


def is_connected_small_ok(g: nx.Graph, n_min: int = N_MIN, n_max: int = N_MAX) -> bool:
    """Boolean check: connected simple graph with n_min <= N <= n_max."""
    try:
        n = g.number_of_nodes()
        if not (n_min <= n <= n_max):
            return False
        if sum(1 for _ in nx.selfloop_edges(g)) != 0:
            return False
        return bool(nx.is_connected(g)) if n > 0 else False
    except Exception:
        return False


def tiny_universe(n_min: int = N_MIN, n_max: int = N_MAX) -> list:
    """Canonical universe: one connected rep per isomorphism class.

    Source: nx.graph_atlas_g (deterministic; contiguous int labels).
    Returns rows {cid: (N, k), g: graph copy}; k = same-N position.
    """
    rows: list = []
    counters: dict = {}
    for g in nx.graph_atlas_g():
        n = g.number_of_nodes()
        if n == 0 or not (n_min <= n <= n_max):
            continue
        if not nx.is_connected(g):
            continue
        k = counters.get(n, 0)
        counters[n] = k + 1
        h = nx.Graph()
        h.add_nodes_from(sorted(g.nodes()))
        h.add_edges_from(tuple(sorted(e)) for e in g.edges())
        rows.append({"cid": (int(n), int(k)), "g": h})
    rows.sort(key=lambda r: (r["cid"][0], r["cid"][1]))
    return rows


def universe_by_n(universe: list) -> dict:
    """Index universe rows by node count (deterministic lists)."""
    out: dict = {}
    for row in universe:
        out.setdefault(row["cid"][0], []).append(row)
    for n in out:
        out[n].sort(key=lambda r: r["cid"][1])
    return out


def _invariants(g: nx.Graph) -> tuple:
    """Cheap isomorphism prefilter: (E, degree-seq, triangles)."""
    degs = tuple(sorted(d for _, d in g.degree()))
    tri = sum(nx.triangles(g).values()) // 3 if g.number_of_nodes() else 0
    return (int(g.number_of_edges()), degs, int(tri))


def canonical_id(g: nx.Graph, universe: list, by_n: dict | None = None):
    """Canonical id (N, k) of g, or None if outside the universe.

    Boolean-friendly: disconnected / out-of-range graphs yield None
    (never raise); isomorphism search prefiltered by invariants.
    """
    try:
        n = g.number_of_nodes()
    except Exception:
        return None
    if by_n is None:
        by_n = universe_by_n(universe)
    cands = by_n.get(n, [])
    if not cands:
        return None
    try:
        if sum(1 for _ in nx.selfloop_edges(g)) != 0:
            return None
        if n > 0 and not nx.is_connected(g):
            return None
    except Exception:
        return None
    inv = _invariants(g)
    for row in cands:
        if _invariants(row["g"]) != inv:
            continue
        if nx.is_isomorphic(g, row["g"]):
            return row["cid"]
    return None


# ---------------------------------------------------------------------------
# Section 2: structural transitions
# ---------------------------------------------------------------------------


def contraction_targets(g: nx.Graph) -> list:
    """All one-edge contraction outcomes (BR-2.5 contract_edge).

    Returns rows {edge: (i, j), g2: graph}. The contraction record is
    discarded at once (C5: no record is stored anywhere downstream).
    Deterministic edge order.
    """
    from bh_graph.contraction import contract_edge

    out = []
    for i, j in sorted(tuple(sorted(e)) for e in g.edges()):
        g2, _, _ = contract_edge(g, i, j)
        out.append({"edge": (i, j), "g2": g2})
    return out


def split_targets(g: nx.Graph) -> list:
    """All record-free one-node split outcomes (U0 undirected covers).

    Fresh labels max+1/max+2 (U0-H4 convention); labels are arbitrary
    since outcomes are canonicalized. Deterministic order.
    Returns rows {node, cover: ([A], [B]), A, B, h}.
    """
    from bh_graph.contraction import apply_split_cover
    from bh_graph.u0 import undirected_covers

    out = []
    if g.number_of_nodes() == 0:
        return out
    top = max(g.nodes())
    for k in sorted(g.nodes()):
        nbrs = sorted(g.neighbors(k))
        for key, A, B in undirected_covers(nbrs):
            i, j = top + 1, top + 2
            h = apply_split_cover(g, k, A, B, i, j)
            out.append({"node": k, "cover": (list(key[0]), list(key[1])),
                        "A": frozenset(A), "B": frozenset(B), "h": h})
    return out


def canonical_transitions(universe: list) -> dict:
    """History-graph adjacency over canonical classes (exact sets).

    adj[cid] = sorted list of (cid2, kind); kinds disjoint by dN
    (C: -1, S: +1, I: same class). Meta records labeled-event
    multiplicities, dropped N7 splits (boundary), and the R=1
    locality audit over every contraction edge used.
    """
    from bh_graph.contraction import influence_check

    by_n = universe_by_n(universe)
    n_max = max(by_n) if by_n else N_MAX
    adj: dict = {}
    events: dict = {}
    dropped_n7 = 0
    loc_audit = {"checked": 0, "ok": 0, "max_dist": 0}
    for row in universe:
        cid = row["cid"]
        g = row["g"]
        succ: dict = {}
        for t in contraction_targets(g):
            c2 = canonical_id(t["g2"], universe, by_n)
            if c2 is None:  # below N_MIN: impossible for N>=1 (N=1 has no edges)
                continue
            loc = influence_check(g, t["g2"], t["edge"][0], t["edge"][1], radius=1)
            loc_audit["checked"] += 1
            loc_audit["ok"] += 1 if loc["ok"] else 0
            loc_audit["max_dist"] = max(loc_audit["max_dist"], loc["max_changed_dist"])
            key = (c2, "C")
            succ.setdefault(key, {"n_labeled": 0, "examples": []})
            succ[key]["n_labeled"] += 1
            if len(succ[key]["examples"]) < 2:
                succ[key]["examples"].append({"edge": list(t["edge"])})
        for t in split_targets(g):
            n_h = t["h"].number_of_nodes()
            if n_h > n_max:
                dropped_n7 += 1
                continue
            c2 = canonical_id(t["h"], universe, by_n)
            if c2 is None:
                continue
            key = (c2, "S")
            succ.setdefault(key, {"n_labeled": 0, "examples": []})
            succ[key]["n_labeled"] += 1
            if len(succ[key]["examples"]) < 2:
                succ[key]["examples"].append({"node": t["node"], "cover": t["cover"]})
        succ[((cid[0], cid[1]), KIND_IDENTITY)] = {"n_labeled": 1, "examples": ["identity"]}
        adj[cid] = sorted(succ)
        for key, meta in succ.items():
            events[(cid, key[0], key[1])] = meta
    return {"adj": adj, "events": events, "dropped_n7": int(dropped_n7),
            "locality": loc_audit,
            "cids": sorted(adj)}


def labeled_universe(n_min: int = N_MIN, n_max: int = 4) -> list:
    """All connected LABELED graphs on contiguous 0..N-1 (exact list).

    N <= 4 only (1 + 1 + 4 + 38 = 44 states). Deterministic order.
    """
    out = []
    for n in range(n_min, n_max + 1):
        pairs = [(a, b) for a in range(n) for b in range(a + 1, n)]
        for mask in range(1 << len(pairs)):
            g = nx.Graph()
            g.add_nodes_from(range(n))
            for t, (a, b) in enumerate(pairs):
                if mask & (1 << t):
                    g.add_edge(a, b)
            if n == 0 or not nx.is_connected(g):
                continue
            out.append(g)
    out.sort(key=lambda g: (g.number_of_nodes(), sorted(tuple(sorted(e)) for e in g.edges())))
    return out


def labeled_key(g: nx.Graph) -> tuple:
    """Hashable key of a contiguous-labeled graph (N + sorted edges)."""
    return (int(g.number_of_nodes()),
            tuple(sorted(tuple(sorted(e)) for e in g.edges())))


def labeled_contract(g: nx.Graph, i: int, j: int) -> nx.Graph:
    """TIME-0 downshift contraction: keep i, drop j, shift labels > j.

    Deterministic contiguous relabeling (frozen TIME-0 label rule);
    unlabeled outcome equals BR-2.5 contract_edge (bridging pin).
    """
    nbrs = sorted((set(g.neighbors(i)) | set(g.neighbors(j))) - {i, j})
    keep = [v for v in sorted(g.nodes()) if v != j]
    remap = {v: (v if v < j else v - 1) if v != i else (i if i < j else i - 1)
             for v in keep}
    h = nx.Graph()
    h.add_nodes_from(sorted(remap.values()))
    for a, b in g.edges():
        if a == j or b == j:
            continue
        if a == i or b == i:
            continue
        h.add_edge(remap[a], remap[b])
    for m in nbrs:
        h.add_edge(remap[i], remap[m])
    return h


def labeled_split(g: nx.Graph, w: int, A: frozenset, B: frozenset) -> nx.Graph:
    """TIME-0 split: children (w on A, N_new on B), adjacent children."""
    n = g.number_of_nodes()
    new = n
    h = nx.Graph()
    h.add_nodes_from(range(n + 1))
    for a, b in g.edges():
        if a != w and b != w:
            h.add_edge(a, b)
    h.add_edge(w, new)
    for m in A:
        h.add_edge(w, m)
    for m in B:
        h.add_edge(new, m)
    return h


def labeled_transitions(states: list) -> dict:
    """History-graph adjacency over labeled states (exact sets).

    adj[key] = sorted list of (key2, kind, event). Contraction events
    are edges; split events are (w, sorted A, sorted B) over ORDERED
    covers (children distinguished by labels). Identity self-loops.
    """
    from bh_graph.contraction import split_covers

    keys = {labeled_key(g): g for g in states}
    adj: dict = {}
    for g in states:
        key = labeled_key(g)
        n = g.number_of_nodes()
        succ: dict = {}
        for i, j in sorted(tuple(sorted(e)) for e in g.edges()):
            h = labeled_contract(g, i, j)
            k2 = labeled_key(h)
            if k2 in keys:
                succ.setdefault((k2, "C"), []).append({"edge": [i, j]})
        for w in sorted(g.nodes()):
            for A, B in split_covers(sorted(g.neighbors(w))):
                h = labeled_split(g, w, A, B)
                k2 = labeled_key(h)
                if k2 in keys:
                    succ.setdefault((k2, "S"), []).append(
                        {"node": w, "A": sorted(A), "B": sorted(B)})
        succ[((key[0], key[1]), KIND_IDENTITY)] = ["identity"]
        adj[key] = sorted((k2, kind) for (k2, kind) in succ)
        for (k2, kind), evs in succ.items():
            adj.setdefault("_events", {})[(key, k2, kind)] = evs
    events = adj.pop("_events", {})
    return {"adj": adj, "events": events, "keys": sorted(adj)}


# ---------------------------------------------------------------------------
# Section 3: exact DP counting over walks
# ---------------------------------------------------------------------------


def successors(adj: dict, node) -> list:
    """Sorted (succ, kind) pairs (adj values are (succ, kind) lists)."""
    return list(adj.get(node, []))


def count_walks_from(adj: dict, start, T: int) -> dict:
    """Exact #length-T walks start -> each node (bigints, DP)."""
    cur = {start: 1}
    for _ in range(int(T)):
        nxt: dict = {}
        for node, c in cur.items():
            for s2, _ in successors(adj, node):
                nxt[s2] = nxt.get(s2, 0) + c
        cur = nxt
    return cur


def count_matrix(adj: dict, starts: list, T: int) -> dict:
    """Exact (a, b) -> #length-T walks for all start/end pairs."""
    out: dict = {}
    for a in starts:
        for b, c in count_walks_from(adj, a, int(T)).items():
            out[(a, b)] = int(c)
    return out


def forward_backward(adj: dict, start, end, T: int) -> tuple:
    """Forward/backward DP tables for participation queries.

    fwd[t][c] = #walks start ->^t c; bwd[t][c] = #walks c ->^{T-t} end.
    Exact bigints.
    """
    T = int(T)
    fwd: list = [{start: 1}]
    for _ in range(T):
        nxt: dict = {}
        for node, c in fwd[-1].items():
            for s2, _ in successors(adj, node):
                nxt[s2] = nxt.get(s2, 0) + c
        fwd.append(nxt)
    preds: dict = {}
    for node in adj:
        for s2, kind in successors(adj, node):
            preds.setdefault(s2, []).append((node, kind))
    bwd: list = [{} for _ in range(T + 1)]
    bwd[T] = {end: 1}
    for t in range(T - 1, -1, -1):
        cur: dict = {}
        for node, c in bwd[t + 1].items():
            for p, _ in preds.get(node, []):
                cur[p] = cur.get(p, 0) + c
        bwd[t] = cur
    return fwd, bwd


def transition_participation(adj: dict, start, end, T: int) -> dict:
    """Exact per-step transition usage over all start -> end walks.

    part[(a, b, kind, t)] = #walks using a -> b at step t (0-based).
    """
    T = int(T)
    fwd, bwd = forward_backward(adj, start, end, T)
    part: dict = {}
    for t in range(T):
        for a, ca in fwd[t].items():
            if ca == 0:
                continue
            for b, kind in successors(adj, a):
                cb = bwd[t + 1].get(b, 0)
                if cb:
                    part[(a, b, kind, t)] = int(ca * cb)
    return part


def explicit_walks(adj: dict, start, end, T: int, cap: int = 100000) -> tuple:
    """Materialize all start -> end length-T walks (capped audit).

    Returns (walks, complete): walks = node sequences; complete False
    iff cap was hit (flagged, never silently sampled).
    """
    T = int(T)
    walks: list = []
    complete = True
    stack = [(start, [start])]
    while stack:
        node, path = stack.pop()
        if len(path) - 1 == T:
            if node == end:
                walks.append(path)
                if len(walks) >= cap:
                    complete = False
                    break
            continue
        if len(path) - 1 > T:
            continue
        for s2, _ in successors(adj, node):
            stack.append((s2, path + [s2]))
            if len(stack) > cap * max(T, 1) * 4:
                complete = False
                stack = []
                break
    walks.sort(key=lambda w: [str(v) for v in w])
    return walks, complete


def toy_chain_adj() -> dict:
    """TIME-0T synthetic unique control: 0 -> 1 -> 2 plus identities."""
    return {0: [(0, KIND_IDENTITY), (1, "C")],
            1: [(1, KIND_IDENTITY), (2, "C")],
            2: [(2, KIND_IDENTITY)]}


def toy_diamond_adj() -> dict:
    """TIME-0S synthetic degenerate control: 0 -> {1a, 1b} -> 2 (+ids)."""
    return {0: [(0, KIND_IDENTITY), ("1a", "C"), ("1b", "C")],
            "1a": [("1a", KIND_IDENTITY), (2, "C")],
            "1b": [("1b", KIND_IDENTITY), (2, "C")],
            2: [(2, KIND_IDENTITY)]}


# ---------------------------------------------------------------------------
# Section 4: field compatibility (labeled microstates)
# ---------------------------------------------------------------------------


def make_state(g: nx.Graph, psi: np.ndarray, order: list | None = None) -> dict:
    """Labeled microstate X = (G, psi, order); order defaults to sorted."""
    if order is None:
        order = node_order(g)
    return {"g": g.copy(), "psi": np.asarray(psi, dtype=np.complex128),
            "order": list(order)}


def zero_state(g: nx.Graph) -> dict:
    """V0 microstate (psi = 0 exactly)."""
    order = node_order(g)
    return make_state(g, np.zeros(len(order), dtype=np.complex128), order)


def propagate_forward(psi: np.ndarray, g: nx.Graph, order: list,
                      dt: float = DT_FROZEN) -> np.ndarray:
    """One frozen identity-step evolution psi -> U(G) psi (banked Krylov)."""
    h = hamiltonian(g, order=list(order))
    return np.asarray(evolve_fixed(np.asarray(psi, dtype=np.complex128), h,
                                   float(dt), 2)["psi"][1])


def propagate_backward(psi: np.ndarray, g: nx.Graph, order: list,
                       dt: float = DT_FROZEN) -> np.ndarray:
    """Reverse evolution via the exact time-reversal identity (C0).

    H(G) = -A is real symmetric, so U(dt)* = U(-dt) = U(dt)^{-1}:
    U^{-1} phi = conj(U conj(phi)) using only the banked forward
    propagator plus exact conjugation (no new numerics).
    """
    inner = propagate_forward(np.conj(np.asarray(psi, dtype=np.complex128)),
                              g, order, dt)
    return np.conj(np.asarray(inner, dtype=np.complex128))


def is_identity_step_ok(X: dict, X2: dict, dt: float = DT_FROZEN,
                        atol: float = ATOL_FIELD) -> bool:
    """Boolean check: labeled identity step (same edges + psi' = U psi)."""
    try:
        if sorted(X["g"].nodes()) != sorted(X2["g"].nodes()):
            return False
        e1 = sorted(tuple(sorted(e)) for e in X["g"].edges())
        e2 = sorted(tuple(sorted(e)) for e in X2["g"].edges())
        if e1 != e2:
            return False
        if list(X["order"]) != list(X2["order"]):
            return False
        want = propagate_forward(X["psi"], X["g"], X["order"], dt)
        return bool(np.allclose(X2["psi"], want, atol=atol, rtol=0.0))
    except Exception:
        return False


def is_contraction_step_ok(X: dict, X2: dict, i: int, j: int,
                           atol: float = ATOL_FIELD) -> bool:
    """Boolean check: labeled contraction on (i, j) + sum map (TIME-0 rule)."""
    try:
        g, order = X["g"], list(X["order"])
        if not g.has_edge(i, j):
            return False
        h = labeled_contract(g, i, j)
        if labeled_key(h) != labeled_key(X2["g"]):
            return False
        idx = index_of(order)
        psi = np.asarray(X["psi"], dtype=np.complex128)
        order2 = node_order(X2["g"])
        if list(X2["order"]) != order2:
            return False
        idx2 = index_of(order2)
        psi2 = np.asarray(X2["psi"], dtype=np.complex128)
        kval = complex(psi[idx[i]]) + complex(psi[idx[j]])
        knew = i if i < j else i - 1
        if abs(complex(psi2[idx2[knew]]) - kval) > atol:
            return False
        for v in order:
            if v == i or v == j:
                continue
            vnew = v if v < j else v - 1
            if abs(complex(psi2[idx2[vnew]]) - complex(psi[idx[v]])) > atol:
                return False
        return True
    except Exception:
        return False


def is_split_step_ok(X: dict, X2: dict, w: int, A: frozenset, B: frozenset,
                     atol: float = ATOL_FIELD) -> bool:
    """Boolean check: labeled split + sum-relation psi_i + psi_j = psi_k."""
    try:
        g, order = X["g"], list(X["order"])
        if w not in g.nodes():
            return False
        h = labeled_split(g, w, frozenset(A), frozenset(B))
        if labeled_key(h) != labeled_key(X2["g"]):
            return False
        idx = index_of(order)
        psi = np.asarray(X["psi"], dtype=np.complex128)
        order2 = node_order(X2["g"])
        if list(X2["order"]) != order2:
            return False
        idx2 = index_of(order2)
        psi2 = np.asarray(X2["psi"], dtype=np.complex128)
        new = g.number_of_nodes()
        sk = complex(psi[idx[w]])
        if abs(complex(psi2[idx2[w]]) + complex(psi2[idx2[new]]) - sk) > atol:
            return False
        for v in order:
            if v == w:
                continue
            if abs(complex(psi2[idx2[v]]) - complex(psi[idx[v]])) > atol:
                return False
        return True
    except Exception:
        return False


def matching_contraction_events(X: dict, X2: dict,
                                atol: float = ATOL_FIELD) -> list:
    """All edges (i, j) making (X, X2) an admissible contraction step."""
    out = []
    for i, j in sorted(tuple(sorted(e)) for e in X["g"].edges()):
        if is_contraction_step_ok(X, X2, i, j, atol):
            out.append((i, j))
    return out


def matching_split_events(X: dict, X2: dict, atol: float = ATOL_FIELD) -> list:
    """All (w, A, B) making (X, X2) an admissible split step (ordered)."""
    from bh_graph.contraction import split_covers

    out = []
    if X2["g"].number_of_nodes() != X["g"].number_of_nodes() + 1:
        return out
    for w in sorted(X["g"].nodes()):
        for A, B in split_covers(sorted(X["g"].neighbors(w))):
            if is_split_step_ok(X, X2, w, A, B, atol):
                out.append((w, frozenset(A), frozenset(B)))
    return out


def step_kinds(X: dict, X2: dict, dt: float = DT_FROZEN,
               atol: float = ATOL_FIELD) -> list:
    """Admissible kinds for the labeled pair (disjoint by dN)."""
    try:
        dn = X2["g"].number_of_nodes() - X["g"].number_of_nodes()
        if dn == 0:
            return [KIND_IDENTITY] if is_identity_step_ok(X, X2, dt, atol) else []
        if dn == -1:
            return ["C"] if matching_contraction_events(X, X2, atol) else []
        if dn == 1:
            return ["S"] if matching_split_events(X, X2, atol) else []
        return []
    except Exception:
        return []


def is_history_admissible_ok(hist: list, dt: float = DT_FROZEN,
                             atol: float = ATOL_FIELD) -> bool:
    """Boolean check: every consecutive pair is an admissible step."""
    try:
        if len(hist) < 2:
            return bool(len(hist) == 1)
        return bool(all(step_kinds(hist[t], hist[t + 1], dt, atol)
                        for t in range(len(hist) - 1)))
    except Exception:
        return False


def time_reverse_history(hist: list) -> list:
    """Theta: reverse slice order + conjugate fields (frozen reversal)."""
    out = []
    for X in reversed(hist):
        out.append(make_state(X["g"], np.conj(np.asarray(X["psi"])), X["order"]))
    return out


def field_along_labeled_walk(g_walk: list, events: list, psi0: np.ndarray,
                             dt: float = DT_FROZEN) -> list:
    """Deterministic field propagation along an event-annotated walk.

    g_walk: labeled graphs; events[t] = ("I",) | ("C", i, j) |
    ("S", w, A, B, alpha) with alpha = psi_w-child fraction
    (psi_w_child = alpha * psi_k, other = (1 - alpha) * psi_k).
    Identity steps evolve by U; contraction threads the sum map;
    split threads the (alpha) sum-relation. Returns psi per slice.
    """
    psis = [np.asarray(psi0, dtype=np.complex128)]
    for t, ev in enumerate(events):
        g, g2 = g_walk[t], g_walk[t + 1]
        order, order2 = node_order(g), node_order(g2)
        idx = index_of(order)
        psi = psis[-1]
        if ev[0] == KIND_IDENTITY:
            psis.append(propagate_forward(psi, g, order, dt))
        elif ev[0] == "C":
            _, i, j = ev
            knew = i if i < j else i - 1
            vals = {}
            for v in order:
                if v == i or v == j:
                    continue
                vnew = v if v < j else v - 1
                vals[vnew] = complex(psi[idx[v]])
            vals[knew] = complex(psi[idx[i]]) + complex(psi[idx[j]])
            psis.append(np.array([vals[v] for v in order2], dtype=np.complex128))
        elif ev[0] == "S":
            _, w, A, B, alpha = ev
            new = g.number_of_nodes()
            sk = complex(psi[idx[w]])
            vals = {v: complex(psi[idx[v]]) for v in order if v != w}
            vals[w] = complex(alpha) * sk
            vals[new] = (1.0 - complex(alpha)) * sk
            psis.append(np.array([vals[v] for v in order2], dtype=np.complex128))
        else:
            raise ValueError(f"unknown event kind: {ev[0]}")
    return psis


# ---------------------------------------------------------------------------
# Section 5: descriptive step ledger (TIME-0E; never gating)
# ---------------------------------------------------------------------------


def step_ledger(X: dict, X2: dict, kind: str, event: dict) -> dict:
    """Descriptive books for one labeled step (measured, not conserved).

    dN, dE_G, dQ, dE_psi (direct), dxi, dtri + contraction cross-checks
    (B_ij, dE formula vs direct). No value here gates admissibility.
    """
    from bh_graph.accounting import event_ledger
    from bh_graph.backreaction import energy_full
    from bh_graph.conservation import cycle_rank, triangle_count

    g, g2 = X["g"], X2["g"]
    psi = np.asarray(X["psi"], dtype=np.complex128)
    psi2 = np.asarray(X2["psi"], dtype=np.complex128)
    out = {
        "kind": kind,
        "dN": int(g2.number_of_nodes() - g.number_of_nodes()),
        "dE_graph": int(g2.number_of_edges() - g.number_of_edges()),
        "dQ": float(np.sum(np.abs(psi2) ** 2) - np.sum(np.abs(psi) ** 2)),
        "dE_psi": float(energy_full(psi2, g2, node_order(g2))
                        - energy_full(psi, g, node_order(g))),
        "dxi": int(cycle_rank(g2) - cycle_rank(g)),
        "dtri": int(triangle_count(g2) - triangle_count(g)),
    }
    if kind == "C":
        i, j = event["edge"]
        led = event_ledger(g, psi, node_order(g), i, j)
        out["B_ij"] = float(led["B_ij"])
        out["dQ_formula"] = float(led["dQ_formula"])
        out["dE_formula"] = float(led["dE_formula"])
    return out


# ---------------------------------------------------------------------------
# Section 6: census drivers
# ---------------------------------------------------------------------------


def boundary_census(adj: dict, starts: list, T: int) -> dict:
    """Full (a, b) pair census at depth T (exact counts + aggregates).

    Reports n_pairs, n_compatible, f_compatible, f_unique, median/max
    N_hist, histogram P(N_hist), per-start totals N_hist(X_-), and
    mean branching b_t (distinct classes at exact depth t).
    """
    T = int(T)
    mat = count_matrix(adj, list(starts), T)
    pair_counts = [mat.get((a, b), 0) for a in starts for b in starts]
    compat = [c for c in pair_counts if c > 0]
    n_pairs = len(pair_counts)
    n_compat = len(compat)
    uniq = sum(1 for c in compat if c == 1)
    hist: dict = {}
    for c in compat:
        hist[int(c)] = hist.get(int(c), 0) + 1
    med = 0
    if compat:
        s = sorted(compat)
        med = s[len(s) // 2] if len(s) % 2 else (s[len(s) // 2 - 1] + s[len(s) // 2]) / 2
    per_start = {}
    branch: dict = {}
    for a in starts:
        tot = 0
        cur = {a: 1}
        bt = {}
        for t in range(1, T + 1):
            nxt: dict = {}
            for node, c in cur.items():
                for s2, _ in successors(adj, node):
                    nxt[s2] = nxt.get(s2, 0) + c
            cur = nxt
            bt[t] = len(cur)
            if t == T:
                tot = sum(cur.values())
        per_start[a] = int(tot)
        branch[a] = bt
    mean_b = {}
    for t in range(1, T + 1):
        mean_b[t] = float(sum(branch[a][t] for a in starts) / max(len(starts), 1))
    return {
        "T": T,
        "n_pairs": int(n_pairs),
        "n_compatible": int(n_compat),
        "f_compatible": float(n_compat / n_pairs) if n_pairs else 0.0,
        "f_unique": float(uniq / n_compat) if n_compat else 0.0,
        "median_nhist": float(med),
        "max_nhist": int(max(compat)) if compat else 0,
        "histogram": {str(k): v for k, v in sorted(hist.items())},
        "per_start_total": {str(a): v for a, v in per_start.items()},
        "mean_branching": {str(t): v for t, v in mean_b.items()},
        "matrix": {(str(a), str(b)): int(mat.get((a, b), 0))
                   for a in starts for b in starts},
    }


def split_outcomes_of_node(g: nx.Graph, universe: list, by_n: dict, w) -> dict:
    """Canonical split-outcome classes of node w: outcome -> covers."""
    from bh_graph.contraction import apply_split_cover
    from bh_graph.u0 import undirected_covers

    top = max(g.nodes())
    out: dict = {}
    for key, A, B in undirected_covers(sorted(g.neighbors(w))):
        h = apply_split_cover(g, w, A, B, top + 1, top + 2)
        c2 = canonical_id(h, universe, by_n)
        if c2 is None:
            continue
        out.setdefault(c2, []).append((list(key[0]), list(key[1])))
    return out


def anchored_step_census(adj: dict, universe: list, T1: int, T2: int,
                         kind: str, cap_examples: int = 2000) -> dict:
    """Intermediate-anchored selection census (TIME-0I / TIME-0J).

    Anchor class a with a distinguished step kind at t = T1:
      kind "S": for each node w of rep(a) with >= 2 distinct canonical
        split outcomes, group compatible through-a (c_-, c_+) pairs by
        their participating-outcome set; resolved iff exactly 1 outcome.
      kind "C": for each class a with >= 2 distinct canonical
        contraction predecessors, group pairs by participating-
        predecessor set; selected iff exactly 1.
    Exact DP with precomputation (no sampling); rows aggregated into
    (local_deg, n_participating) histograms + capped example rows.
    """
    T1, T2 = int(T1), int(T2)
    by_n = universe_by_n(universe)
    reps = {row["cid"]: row["g"] for row in universe}
    cids = sorted(adj)
    heads: dict = {}
    if kind == "S":
        for c0 in cids:
            heads[c0] = count_walks_from(adj, c0, T1)
        tails: dict = {}
        agg: dict = {}
        n_rows = 0
        n_res = 0
        examples: list = []
        for a in cids:
            g = reps[a]
            out_s = [b for b, k in successors(adj, a) if k == "S"]
            if not out_s:
                continue
            for w in sorted(g.nodes()):
                outcomes = sorted(split_outcomes_of_node(g, universe, by_n, w))
                if len(outcomes) < 2:
                    continue
                for o in outcomes:
                    if (o, T2 - 1) not in tails and T2 >= 1:
                        tails[(o, T2 - 1)] = count_walks_from(adj, o, T2 - 1)
                for c0 in cids:
                    reach_a = heads[c0].get(a, 0)
                    if reach_a == 0:
                        continue
                    for cT in cids:
                        part = []
                        thru = 0
                        for o in outcomes:
                            if T2 >= 1:
                                tail = tails[(o, T2 - 1)].get(cT, 0)
                            else:
                                tail = 1 if o == cT else 0
                            if tail > 0:
                                part.append(o)
                                thru += reach_a * tail
                        if not part:
                            continue
                        n_rows += 1
                        key = (len(outcomes), len(part))
                        agg[key] = agg.get(key, 0) + 1
                        if len(part) == 1:
                            n_res += 1
                        if len(examples) < cap_examples:
                            examples.append({
                                "anchor": str(a), "node": int(w),
                                "c0": str(c0), "cT": str(cT),
                                "local_deg": int(len(outcomes)),
                                "participating": sorted(str(o) for o in part),
                                "n_participating": int(len(part)),
                                "n_through": int(thru),
                                "resolved": bool(len(part) == 1),
                            })
        return {"kind": "S", "T1": T1, "T2": T2, "n_rows": int(n_rows),
                "n_resolved": int(n_res),
                "resolution_rate": float(n_res / n_rows) if n_rows else 0.0,
                "agg": {f"{k[0]}->{k[1]}": v for k, v in sorted(agg.items())},
                "examples": examples,
                "examples_capped": bool(n_rows > len(examples))}
    if kind == "C":
        preds: dict = {}
        for node in adj:
            for s2, k in successors(adj, node):
                if k == "C":
                    preds.setdefault(s2, []).append(node)
        for c0 in cids:
            heads[c0] = count_walks_from(adj, c0, max(T1 - 1, 0))
        leaves: dict = {}
        for a in cids:
            leaves[a] = count_walks_from(adj, a, T2)
        agg = {}
        n_rows = 0
        n_res = 0
        examples = []
        for a in cids:
            ps = sorted(set(preds.get(a, [])))
            if len(ps) < 2:
                continue
            for c0 in cids:
                for cT in cids:
                    if leaves[a].get(cT, 0) == 0:
                        continue
                    part = [p for p in ps
                            if (heads[c0].get(p, 0) > 0 if T1 >= 1 else p == c0)]
                    if not part:
                        continue
                    n_rows += 1
                    key = (len(ps), len(part))
                    agg[key] = agg.get(key, 0) + 1
                    if len(part) == 1:
                        n_res += 1
                    if len(examples) < cap_examples:
                        examples.append({
                            "anchor": str(a), "c0": str(c0), "cT": str(cT),
                            "local_deg": int(len(ps)),
                            "participating": sorted(str(p) for p in part),
                            "n_participating": int(len(part)),
                            "resolved": bool(len(part) == 1),
                        })
        return {"kind": "C", "T1": T1, "T2": T2, "n_rows": int(n_rows),
                "n_resolved": int(n_res),
                "resolution_rate": float(n_res / n_rows) if n_rows else 0.0,
                "agg": {f"{k[0]}->{k[1]}": v for k, v in sorted(agg.items())},
                "examples": examples,
                "examples_capped": bool(n_rows > len(examples))}
    raise ValueError(f"unknown anchored kind: {kind}")


def final_affine_system(g_walk: list, events: list, psi0: np.ndarray,
                        dt: float = DT_FROZEN) -> tuple:
    """Affine final-field system of a graph walk over split fractions.

    psi_final(alpha) = base + M @ alpha exactly (all maps linear):
    base = all-alpha-0 propagation; column j = (alpha_j=1 rest 0)
    propagation minus base. Returns (base, M) with M shape (N, n_splits).
    """
    n_splits = sum(1 for e in events if e[0] == "S")
    ev0 = [("S", e[1], e[2], e[3], 0.0) if e[0] == "S" else e for e in events]
    base = field_along_labeled_walk(g_walk, ev0, psi0, dt)[-1]
    cols = []
    seen = 0
    for j in range(n_splits):
        evj = []
        sj = 0
        for e in events:
            if e[0] == "S":
                evj.append(("S", e[1], e[2], e[3], 1.0 if sj == j else 0.0))
                sj += 1
            else:
                evj.append(e)
        cols.append(field_along_labeled_walk(g_walk, evj, psi0, dt)[-1] - base)
        seen += 1
    assert seen == n_splits
    M = np.column_stack(cols) if cols else np.zeros((len(base), 0),
                                                    dtype=np.complex128)
    return np.asarray(base, dtype=np.complex128), np.asarray(M, dtype=np.complex128)


def is_affine_reachable_ok(base: np.ndarray, M: np.ndarray, target: np.ndarray,
                           atol: float = ATOL_FIELD) -> bool:
    """Boolean check: target in the affine set {base + M alpha} (exact)."""
    try:
        base = np.asarray(base, dtype=np.complex128)
        M = np.asarray(M, dtype=np.complex128)
        target = np.asarray(target, dtype=np.complex128)
        if M.shape[1] == 0:
            return bool(np.allclose(base, target, atol=atol, rtol=0.0))
        sol, *_ = np.linalg.lstsq(M, target - base, rcond=None)
        return bool(np.allclose(base + M @ sol, target, atol=atol, rtol=0.0))
    except Exception:
        return False


def fixed_graph_control(g: nx.Graph, psi0: np.ndarray, T: int,
                        dt: float = DT_FROZEN, seed: int = 0,
                        cap: int = 200000) -> dict:
    """TIME-0R control: on-trajectory pair compatible, off-trajectory filed.

    Enumerates labeled length-T graph walks from (g, psi0) exactly
    (identity carries U; structural steps carry sum/sum-relation maps);
    each walk's reachable final set is affine in its split fractions,
    and membership of the on-trajectory final (U^T psi0 on g) and a
    seeded off-trajectory final is decided EXACTLY (lstsq, no sampling).
    Gates: identity walk present + matching (R1), on-trajectory >= 1
    walk (R2); off-trajectory count RECORDED (R3, excursion DOFs may
    cover generic finals -- data, not apparatus fault).
    """
    from bh_graph.contraction import split_covers

    rng = np.random.default_rng(seed)
    order = node_order(g)
    n = len(order)
    psi0 = np.asarray(psi0, dtype=np.complex128)
    psi_on = np.asarray(psi0, dtype=np.complex128)
    for _ in range(int(T)):
        psi_on = propagate_forward(psi_on, g, order, dt)
    psi_off = np.asarray(rng.normal(size=n) + 1j * rng.normal(size=n),
                         dtype=np.complex128)
    psi_off = psi_off / float(np.linalg.norm(psi_off))

    states = [(g, [g], [])]  # (current g, g_walk, graph events)
    complete = True
    for _ in range(int(T)):
        nxt = []
        for gc, walk, evs in states:
            nxt.append((gc, walk + [gc], evs + [(KIND_IDENTITY,)]))
            for i, j in sorted(tuple(sorted(e)) for e in gc.edges()):
                h = labeled_contract(gc, i, j)
                nxt.append((h, walk + [h], evs + [("C", i, j)]))
            if gc.number_of_nodes() <= 4:
                for w in sorted(gc.nodes()):
                    for A, B in split_covers(sorted(gc.neighbors(w))):
                        h = labeled_split(gc, w, A, B)
                        nxt.append((h, walk + [h],
                                    evs + [("S", w, frozenset(A), frozenset(B))]))
            if len(nxt) > cap:
                complete = False
                break
        states = nxt
        if not complete:
            break
    n_on = 0
    n_off = 0
    n_identity_path = 0
    n_on_any = 0
    n_off_any = 0
    max_splits = 0
    for gc, walk, evs in states:
        if gc.number_of_nodes() != g.number_of_nodes():
            continue
        evs_full = [("S", e[1], e[2], e[3], 0.0) if e[0] == "S" else e
                    for e in evs]
        base, M = final_affine_system(walk, evs_full, psi0, dt)
        max_splits = max(max_splits, M.shape[1])
        strict = labeled_key(gc) == labeled_key(g)
        if is_affine_reachable_ok(base, M, psi_on):
            n_on_any += 1
            if strict:
                n_on += 1
                if all(e[0] == KIND_IDENTITY for e in evs):
                    n_identity_path += 1
        if is_affine_reachable_ok(base, M, psi_off):
            n_off_any += 1
            if strict:
                n_off += 1
    return {"T": int(T), "n_graph_walks": int(len(states)),
            "complete": bool(complete),
            "n_on_trajectory": int(n_on),
            "n_off_trajectory": int(n_off),
            "n_on_any_graph": int(n_on_any),
            "n_off_any_graph": int(n_off_any),
            "identity_path_present": bool(n_identity_path == 1),
            "max_splits_per_walk": int(max_splits)}


# ---------------------------------------------------------------------------
# Section 7: frozen verdict
# ---------------------------------------------------------------------------


def nowait_adjacency(adj: dict) -> dict:
    """History graph with identity self-loops removed (structural only)."""
    return {a: [(b, k) for b, k in succ if not (b == a and k == KIND_IDENTITY)]
            for a, succ in adj.items()}


def skeleton_census(adj: dict, starts: list, T: int) -> dict:
    """Exact identity-compressed (skeleton) history counts per pair.

    Skeleton count = sum_L S_L(a, b) over no-wait walks of length L<=T
    (timed total = sum_L C(T,L) S_L, pinned identity). Descriptive
    co-headline separating waiting-degeneracy from structural
    degeneracy. Compatible here = skeleton count > 0.
    """
    T = int(T)
    noloop = nowait_adjacency(adj)
    mats = [count_matrix(noloop, list(starts), L) for L in range(T + 1)]
    pair_skel = {}
    for a in starts:
        for b in starts:
            pair_skel[(a, b)] = sum(m.get((a, b), 0) for m in mats)
    compat = [c for c in pair_skel.values() if c > 0]
    uniq = sum(1 for c in compat if c == 1)
    hist: dict = {}
    for c in compat:
        hist[int(c)] = hist.get(int(c), 0) + 1
    return {
        "T": T,
        "n_pairs": int(len(pair_skel)),
        "n_compatible": int(len(compat)),
        "f_unique_skel": float(uniq / len(compat)) if compat else 0.0,
        "max_skel": int(max(compat)) if compat else 0,
        "histogram_skel": {str(k): v for k, v in sorted(hist.items())},
        "matrix_skel": {(str(a), str(b)): int(pair_skel[(a, b)])
                        for a in starts for b in starts},
    }


def verdict_from_census(census: dict) -> dict:
    """Frozen ladder mapping (counts in, rung out; no scoring of histories).

    Consumes only aggregate census tables (never individual histories).
    Gates: C-pins green (caller-provided flags) else TIME0-INCONCLUSIVE.
    """
    gates = census.get("gates", {})
    if not all(gates.get(k, False) for k in ("C0", "C1", "C2", "C3", "C4", "C5", "C6")):
        return {"verdict": "TIME0-INCONCLUSIVE", "reason": "control gate red"}
    per_t = census.get("per_T", {})
    pooled_u = census.get("pooled", {}).get("f_unique", 0.0)
    pooled_c = census.get("pooled", {}).get("f_compatible", 0.0)
    worst_t = min((v.get("f_unique", 0.0) for v in per_t.values()), default=0.0)
    split_res = census.get("split_resolution", 0.0)
    if pooled_u < F_UNIQUE_NULL_BELOW:
        rung = "TIME0-NULL"
    elif (pooled_u >= F_UNIQUE_UNIQUE_ABOVE and worst_t >= F_UNIQUE_WORST_T_MIN
          and pooled_c >= F_COMPAT_UNIQUE_MIN and split_res >= SPLIT_RESOLVE_UNIQUE_MIN):
        rung = "TIME0-UNIQUE"
        if bool(gates.get("locality_R1", False)) and bool(gates.get("no_objective", False)):
            rung = "TIME0-LOCAL"
    else:
        rung = "TIME0-CONSTRAINED"
    return {"verdict": rung,
            "pooled_f_unique": float(pooled_u),
            "pooled_f_compatible": float(pooled_c),
            "worst_T_f_unique": float(worst_t),
            "split_resolution": float(split_res)}
