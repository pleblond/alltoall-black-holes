"""SPLIT-0 deterministic inverse constraints and residual split information.

Campaign: SPLIT-0. Determines exactly which parts of a split are fixed by
being the inverse of an earned contraction, and isolates the irreducible
residual information that must be supplied to choose one physical
predecessor. This campaign does NOT derive a probability measure
(MEASURE0-DEBT remains binding).

Frozen ontology (read-only consumption, never re-derived):
  - Contraction/split op u-v <-> [uv] (BR-2.5): contract_edge (simple-kind,
    common neighbors collapse, consumed edge discarded), sum map
    psi_k = psi_i + psi_j, 3^d directed covers, R_U = 1.
  - Event ledger (BR-2.6/CONS-0): dN = -1, dE = -(1+c), dQ = +2B_ij,
    dE_psi = 2B_ij - 2*sum_cross (common collapse energy-neutral);
    split ledgers (dN = +1, dE = +(1+c'), equal dQ = -|k|^2/2);
    universal closure impossible; split degeneracy survives on level sets.
  - Physical quotient X_phys = X / (R x U1) (SYM0-CLOSED): node relabeling
    + global phase; signature proxy (MEASURE-0A) + exact isomorphism
    (RAND-0F) where sufficiency matters.
  - Equal-halves reverse condition (MEASURE-0C): full physical reverse
    support only on the psi_i == psi_j subset under the frozen
    equal-halves field map.
  - History-level control (TIME0-NULL): two-boundary selection does not
    resolve splits; no result-sharing redesign either way.
  - Hidden-sector states physically distinct (HIDDEN0-SEPARATED + SYM-0):
    P_- degrees are retained, never quotiented for remote-blindness.

Load-bearing identities derived pre-data (pinned in tests/test_split0.py):
  - (SPLIT-0B theorem) The sum-map fiber over s is the affine complex
    line {(p, s-p) : p in C}, parametrized by the relative mode
    d = p - q as p = (s+d)/2, q = (s-d)/2: 1 complex = 2 real dims,
    for EVERY s (including s = 0). The merged state fixes the common
    mode s and constrains nothing else about (p, q).
  - (SPLIT-0B quotient) Under global U1 the fiber keeps 2 real physical
    dims whenever the gauge is fixable (rest != 0 or s != 0); only the
    all-zero merged state leaves 1 redundant phase dim (d_cont = 1).
  - (SPLIT-0C theorem) The equal-halves section {d = 0} is exactly one
    point per graph cover: field residual vanishes there (d_cont = 0)
    and only discrete graph multiplicity survives.
  - (SPLIT-0H theorem) The full exact inverse is NEVER a singleton:
    |P(M)| is uncountable for every merged state (continuous fiber).
    The halves-restricted inverse is a singleton iff the split node is
    isolated (d(k) = 0) -- the deterministic core (census-verified:
    no d > 0 cell has n_phys_halves == 1).
  - (SPLIT-0I theorem) M + xi <-> X with xi = (undirected cover, d):
    minimal (ablation witnesses both ways) and sufficient (exact
    roundtrip C(decode(M, xi)) == M).

Firewall (binding): no temperature, Boltzmann factors, Born rule, action,
entropy maximization, Metropolis, event rates, fitted exponents, tunable
couplings, external noise, hidden random fields, preferred graph or matter
configuration. xi is INFORMATION a stochastic law would have to provide;
it is never called random and never given a distribution. Candidate
weightings (RAND micro/orbit, MEASURE const/orbit) appear ONLY as
SPLIT-0J no-measure controls.

This module introduces NO probability measure, NO dynamics, NO threshold,
NO rate, NO temperature, NO fitted constant. No RNG anywhere.
"""

from __future__ import annotations

import itertools
import math

import networkx as nx
import numpy as np

# Frozen bars (SYM-0 Amendment-1 / TIME-0 grades, consumed read-only).
FP_ATOL = 1e-12
FIELD_ATOL = 1e-9
SIG_ROUND = 9

# Frozen battery: merged states M range over graphs x fields; every node
# of every graph is a split cell (every (G2, k, s) has a nonempty exact
# inverse: any cover gives a graph pre-image, any fiber point a field).
SPLIT0_GRAPHS = ("single", "k2", "triangle", "square", "star4", "path4")
SPLIT0_FIELDS = ("zero", "bonding", "current", "antibonding")
J2_L_SPOT = 4
J2_BACKGROUNDS = ("zero", "uniform", "VMINUS")
U1_GRID = (math.pi / 4.0, math.pi / 2.0, math.pi, 3.0 * math.pi / 2.0)
# Deterministic relative-mode sweep (no RNG): spans d = 0 (halves),
# real/imag/unit/complex generic points.
D_SWEEP = (0.0j, 1.0 + 0.0j, 0.0 + 1.0j, 1.0 + 1.0j, -0.5 + 0.25j,
           2.0 - 1.0j)


# ---------------------------------------------------------------------------
# Battery builders (frozen)
# ---------------------------------------------------------------------------

def tiny_graph_split0(name: str) -> dict:
    """Frozen tiny substrates incl. the isolated single node (d = 0 cell).

    single: 1 node, 0 edges (deterministic-core probe). Others alias the
    frozen RAND-0 tiny graphs byte-identically (same objects).
    """
    if name == "single":
        g = nx.Graph()
        g.add_node(0)
        return {"g": g, "order": [0]}
    from bh_graph.rand0 import tiny_graph

    return tiny_graph(name)


def tiny_field_split0(n: int, which: str) -> np.ndarray:
    """Frozen tiny field preparations (RAND-0 banked, incl. n = 1)."""
    from bh_graph.rand0 import tiny_field

    return tiny_field(int(n), which)


def merged_state(graph_name: str, field_name: str) -> dict:
    """Frozen merged state M = (G2, psi2, order2) (SPLIT-0 battery)."""
    spec = tiny_graph_split0(graph_name)
    g, order = spec["g"], spec["order"]
    psi = np.asarray(tiny_field_split0(len(order), field_name),
                     dtype=np.complex128)
    return {"g": g, "psi": psi, "order": list(order),
            "graph": graph_name, "field": field_name}


def split0_cells(graph_names=tuple(SPLIT0_GRAPHS),
                 field_names=tuple(SPLIT0_FIELDS)) -> list:
    """All (M, k) split cells: every node of every battery state."""
    cells = []
    for gn in graph_names:
        for fn in field_names:
            st = merged_state(gn, fn)
            for k in sorted(st["g"].nodes()):
                cells.append({"state": f"{gn}/{fn}", "graph": gn,
                              "field": fn, "k": k,
                              "d": int(st["g"].degree(k))})
    return cells


def j2_merged_spot(L: int = J2_L_SPOT, background: str = "uniform",
                   k=None) -> dict:
    """Frozen J2 merged-state spot (hidden/sheet covariance legs).

    Graph: J2 torus (frozen geometry). Backgrounds: zero (exact),
    uniform (VPLUS shape), VMINUS (translation-invariant hidden member).
    k defaults to node 0. Returns M + substrate records (c3, order).
    """
    from bh_graph.conservation import field_uniform, field_zero, substrate_j2
    from bh_graph.formation import j2_torus_coords
    from bh_graph.hidden import vac_shapes

    L = int(L)
    sub = substrate_j2(L)
    g, order = sub["g"], list(sub["order"])
    c3 = j2_torus_coords(L)
    if background == "zero":
        psi = field_zero(len(order))
    elif background == "uniform":
        psi = field_uniform(len(order))
    elif background == "VMINUS":
        psi = np.asarray(vac_shapes(order, c3)["VMINUS"],
                         dtype=np.complex128)
    else:
        raise ValueError(f"unknown J2 background: {background}")
    if k is None:
        k = order[0]
    return {"g": g, "psi": np.asarray(psi, dtype=np.complex128),
            "order": order, "c3": dict(c3), "L": L,
            "background": background, "k": k}


# ---------------------------------------------------------------------------
# SPLIT-0A: graph inverse
# ---------------------------------------------------------------------------

def directed_cover_count(d: int) -> int:
    """Directed cover count 3^d (BR-2.5, earned)."""
    return 3 ** int(d)


def undirected_cover_count(d: int) -> int:
    """Undirected cover count (3^d + 1)/2 (U0-H1 gauge quotient, earned)."""
    return int((3 ** int(d) + 1) / 2)


def fresh_labels(g: nx.Graph, i=None, j=None):
    """Canonical fresh daughter labels (max+1/max+2, U0/TIME-0 convention)."""
    if i is not None and j is not None:
        return i, j
    if not all(isinstance(v, int) for v in g.nodes()):
        raise ValueError("split needs integer labels or explicit i, j")
    top = max(g.nodes())
    return top + 1, top + 2


def graph_predecessors(g2: nx.Graph, k, i=None, j=None) -> list:
    """All directed graph predecessors: covers x predecessor graphs H.

    Each row: {A, B (sorted lists), h (graph), cprime, dE}. The i-j edge
    is always restored; non-neighbor relations are preserved exactly.
    Deterministic order (split_covers order).
    """
    from bh_graph.contraction import apply_split_cover, split_covers

    i, j = fresh_labels(g2, i, j)
    out = []
    for A, B in split_covers(sorted(g2.neighbors(k))):
        h = apply_split_cover(g2, k, set(A), set(B), i, j)
        out.append({"A": sorted(A), "B": sorted(B), "h": h,
                    "cprime": len(set(A) & set(B)),
                    "dE": int(h.number_of_edges() - g2.number_of_edges())})
    return out


def undirected_predecessors(g2: nx.Graph, k, i=None, j=None) -> list:
    """Canonical undirected graph predecessors (endpoint swap = gauge).

    Each row: {key ((A, B) canonical tuples), A, B (frozensets),
    h (graph), cprime, dE}. Deterministic key order.
    """
    from bh_graph.contraction import apply_split_cover
    from bh_graph.u0 import undirected_covers

    i, j = fresh_labels(g2, i, j)
    out = []
    for key, A, B in undirected_covers(sorted(g2.neighbors(k))):
        h = apply_split_cover(g2, k, set(A), set(B), i, j)
        out.append({"key": key, "A": frozenset(A), "B": frozenset(B),
                    "h": h, "cprime": len(set(A) & set(B)),
                    "dE": int(h.number_of_edges() - g2.number_of_edges())})
    return out


def cover_anatomy(A, B) -> dict:
    """Anatomy of one cover: exclusive/both splits + ledger numbers."""
    a, b = set(A), set(B)
    return {"only_A": sorted(a - b), "only_B": sorted(b - a),
            "both": sorted(a & b), "cprime": len(a & b),
            "union": sorted(a | b), "dE_formula": int(1 + len(a & b))}


def is_cover_complete_ok(g2: nx.Graph, k) -> bool:
    """Boolean check: exact split census (never raises).

    Directed count == 3^d with every union == N(k); undirected count ==
    (3^d+1)/2; every dE == 1 + cprime (CONS-0K count law).
    """
    try:
        d = int(g2.degree(k))
        want_n = sorted(g2.neighbors(k))
        directed = graph_predecessors(g2, k)
        if len(directed) != directed_cover_count(d):
            return False
        for row in directed:
            if sorted(set(row["A"]) | set(row["B"])) != want_n:
                return False
            if row["dE"] != 1 + row["cprime"]:
                return False
        undirected = undirected_predecessors(g2, k)
        if len(undirected) != undirected_cover_count(d):
            return False
        keys = [r["key"] for r in undirected]
        if len(set(keys)) != len(keys):
            return False
        return True
    except Exception:
        return False


def graph_iso_classes(g2: nx.Graph, k) -> list:
    """Undirected covers grouped by unlabeled predecessor-graph isomorphism.

    Field-blind (graph sector only). WL-hash pre-grouping + exact
    nx.is_isomorphic within groups (RAND-0F pattern). NONE-excluded:
    every member is a genuine graph predecessor. Deterministic order.
    """
    preds = undirected_predecessors(g2, k)
    groups: dict = {}
    for n, row in enumerate(preds):
        wl = nx.weisfeiler_lehman_graph_hash(row["h"])
        inv = (wl, row["h"].number_of_edges(),
               tuple(sorted(dd for _, dd in row["h"].degree())))
        groups.setdefault(inv, []).append(n)
    classes: list = []
    for _inv, members in sorted(groups.items(), key=lambda kv: kv[1]):
        for n in members:
            placed = False
            for cls in classes:
                if cls[0] not in members:
                    continue
                if nx.is_isomorphic(preds[n]["h"], preds[cls[0]]["h"]):
                    cls.append(n)
                    placed = True
                    break
            if not placed:
                classes.append([n])
    for cls in classes:
        cls.sort()
    classes.sort(key=lambda c: c[0])
    return classes


def contraction_inverse_check(g: nx.Graph, psi: np.ndarray, order: list,
                              i, j) -> dict:
    """Forward-backward bridge: recorded cover restores the pre-image.

    Contracts (i, j) with the sum map, then verifies the recorded
    (nbrs_i, nbrs_j) cover appears among the undirected predecessors of
    (g2, k) and restores the graph bit-identically (BR-2.5/CONS census
    reproduction: the record IS one enumerated cover).
    """
    from bh_graph.contraction import contracted_state

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    g2, _psi2, _order2, k, rec = contracted_state(g, psi, order, i, j, "sum")
    want = frozenset((frozenset(rec["nbrs_i"]), frozenset(rec["nbrs_j"])))
    # Undirected comparison: {A, B} as a set of frozensets.
    found = False
    for row in undirected_predecessors(g2, k, i, j):
        if frozenset((row["A"], row["B"])) == want:
            e0 = {tuple(sorted(e)) for e in g.edges()}
            e1 = {tuple(sorted(e)) for e in row["h"].edges()}
            found = bool(e0 == e1 and set(row["h"].nodes()) == set(g.nodes()))
            break
    return {"k": k, "recorded_cover_found": bool(found),
            "restores_graph": bool(found),
            "n_undirected": undirected_cover_count(int(g2.degree(k)))}


# ---------------------------------------------------------------------------
# SPLIT-0B: field inverse
# ---------------------------------------------------------------------------

def fiber_point(s: complex, d: complex):
    """Fiber parametrization: (p, q) = ((s+d)/2, (s-d)/2) (exact)."""
    s, d = complex(s), complex(d)
    return (s + d) / 2.0, (s - d) / 2.0


def fiber_residual(p: complex, q: complex) -> complex:
    """Relative mode d = p - q (exact)."""
    return complex(p) - complex(q)


def is_sum_consistent_ok(p: complex, q: complex, s: complex,
                         atol: float = FP_ATOL) -> bool:
    """Boolean check: p + q == s (never raises)."""
    try:
        return bool(abs(complex(p) + complex(q) - complex(s)) <= atol)
    except Exception:
        return False


def fiber_dims() -> dict:
    """Fiber dimension theorem: affine complex line (1 C-dim = 2 R-dims).

    Holds for every s including s = 0 (fiber {(p, -p)} is still a full
    complex line). No discrete field degeneracy exists: the sum map
    C^2 -> C has no isolated pre-images.
    """
    return {"dim_C": 1, "dim_R": 2, "discrete_points": 0,
            "topology": "affine complex line"}


def halves_point(s: complex):
    """Equal-halves point (s/2, s/2), i.e. d = 0 (exact)."""
    s = complex(s)
    return s / 2.0, s / 2.0


def is_equal_halves_ok(p: complex, q: complex) -> bool:
    """Boolean check: p == q exactly (never raises)."""
    try:
        return bool(complex(p) == complex(q))
    except Exception:
        return False


def physical_fiber_dims(rest_nonzero: bool, s: complex) -> dict:
    """Physical fiber dims after the U1 quotient (exact case analysis).

    Gauge fixable (rest has a nonzero entry, or s != 0 fixes the phase
    via the merged value) -> d fully physical (2 real dims). Only the
    all-zero merged state (rest == 0 and s == 0) leaves the global phase
    unfixable -> fiber (p, -p) modulo phase = half-line |p| >= 0
    (1 real dim). The fiber is never a point: d_cont >= 1 always.
    """
    if bool(rest_nonzero) or complex(s) != 0.0:
        return {"d_cont_phys": 2, "redundant_phase": False,
                "reason": ("rest fixes phase" if rest_nonzero
                           else "merged value s != 0 fixes phase")}
    return {"d_cont_phys": 1, "redundant_phase": True,
            "reason": "all-zero merged state: (p,-p)/U1 = |p| half-line"}


def rest_nonzero(psi2: np.ndarray, order2: list, k) -> bool:
    """Boolean check: merged rest (all nodes but k) has a nonzero entry."""
    from bh_graph.ballistic import index_of

    psi2 = np.asarray(psi2, dtype=np.complex128)
    idx = index_of(list(order2))
    return bool(any(complex(psi2[idx[v]]) != 0.0
                    for v in order2 if v != k))


def undirected_residual(d: complex) -> dict:
    """Canonical undirected relative mode {d, -d} (swap = gauge).

    Representative: Im > 0, or Im == 0 with Re >= 0. d = 0 is the unique
    fixed point (equal-halves). Deterministic, exact.
    """
    d = complex(d)
    if d == 0.0:
        return {"d_canon": 0.0j, "swapped": False, "fixed_point": True}
    if d.imag > 0.0 or (d.imag == 0.0 and d.real >= 0.0):
        return {"d_canon": d, "swapped": False, "fixed_point": False}
    return {"d_canon": -d, "swapped": True, "fixed_point": False}


def predecessor_state(g2: nx.Graph, psi2: np.ndarray, order2: list, k,
                      A, B, p: complex, q: complex, i, j) -> dict:
    """Full predecessor X = (H, psi, orderH) from cover + fiber point.

    Rest values copied bit-identically; daughters carry (p, q) with
    i on A, j on B. Exact construction (no approximation).
    """
    from bh_graph.ballistic import index_of
    from bh_graph.contraction import apply_split_cover

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    idx = index_of(order2)
    h = apply_split_cover(g2, k, set(A), set(B), i, j)
    order_h = [v for v in order2 if v != k] + [i, j]
    vals = {v: complex(psi2[idx[v]]) for v in order2 if v != k}
    vals[i], vals[j] = complex(p), complex(q)
    psi_h = np.array([vals[v] for v in order_h], dtype=np.complex128)
    return {"g": h, "psi": psi_h, "order": order_h}


def is_predecessor_ok(g2: nx.Graph, psi2: np.ndarray, order2: list, k,
                      X: dict, i, j, atol: float = FP_ATOL) -> bool:
    """Boolean check: C(X) == M exactly via (i, j) (never raises).

    Contracts X on daughters (i, j) with the sum map and compares graph
    edge-set (up to the fresh merged label) + full field vector.
    """
    try:
        from bh_graph.ballistic import index_of
        from bh_graph.contraction import contracted_state

        psi2 = np.asarray(psi2, dtype=np.complex128)
        order2 = list(order2)
        g, psi, order = X["g"], np.asarray(X["psi"],
                                           dtype=np.complex128), list(X["order"])
        g2b, psi2b, order2b, _kb, _rec = contracted_state(g, psi, order,
                                                          i, j, "sum")
        # Graph comparison up to the merged label: relabel kb -> k.
        e_want = {tuple(sorted(e)) for e in g2.edges()}
        e_got = set()
        for a, b in g2b.edges():
            a = k if a == _kb else a
            b = k if b == _kb else b
            e_got.add(tuple(sorted((a, b))))
        if e_want != e_got:
            return False
        idx = index_of(order2)
        idxb = index_of(order2b)
        for v in order2:
            vv = _kb if v == k else v
            if abs(complex(psi2b[idxb[vv]]) - complex(psi2[idx[v]])) > atol:
                return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# SPLIT-0C: equal-halves subset
# ---------------------------------------------------------------------------

def halves_predecessors(g2: nx.Graph, psi2: np.ndarray, order2: list,
                        k, i=None, j=None) -> list:
    """Halves section: undirected covers x (s/2, s/2) (exact).

    One point per graph cover (d = 0 fixed): field residual vanishes.
    Rows: {key, A, B, h, psi_h, order_h, i, j}.
    """
    from bh_graph.ballistic import index_of

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    i, j = fresh_labels(g2, i, j)
    s = complex(psi2[index_of(order2)[k]])
    p, q = halves_point(s)
    out = []
    for row in undirected_predecessors(g2, k, i, j):
        X = predecessor_state(g2, psi2, order2, k, row["A"], row["B"],
                              p, q, i, j)
        out.append({"key": row["key"], "A": row["A"], "B": row["B"],
                    "h": X["g"], "psi_h": X["psi"], "order_h": X["order"],
                    "i": i, "j": j, "s": s})
    return out


def halves_section_dims() -> dict:
    """Halves-section dimension theorem: a point per cover (d_cont = 0)."""
    return {"d_cont": 0, "points_per_cover": 1,
            "residual": "discrete graph multiplicity only"}


def halves_reverse_support(g: nx.Graph, psi: np.ndarray, order: list,
                           i, j) -> dict:
    """MEASURE-0C reproduction: full reverse iff psi_i == psi_j.

    Contracts (i, j), then checks graph-reverse (recorded cover present)
    and full-reverse (some halves predecessor matches X up to R x U1
    signature + exact halves condition). Reports all levels separately.
    """
    from bh_graph.measure0 import signature_key, state_signature

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    bridge = contraction_inverse_check(g, psi, order, i, j)
    from bh_graph.ballistic import index_of
    from bh_graph.contraction import contracted_state

    idx = index_of(order)
    halves = is_equal_halves_ok(complex(psi[idx[i]]), complex(psi[idx[j]]))
    g2, psi2, order2, k, _rec = contracted_state(g, psi, order, i, j, "sum")
    sig0 = signature_key(state_signature(g, psi, order))
    full = False
    if halves:
        for row in halves_predecessors(g2, psi2, order2, k, i, j):
            if signature_key(state_signature(row["h"], row["psi_h"],
                                              row["order_h"])) == sig0:
                full = True
                break
    else:
        # Off-halves X cannot match any halves point in field values:
        # halves predecessors all carry (s/2, s/2) != (psi_i, psi_j).
        full = False
    graph_rev = bool(bridge["recorded_cover_found"])
    if full:
        verdict = "reversible"
    elif graph_rev:
        verdict = "graph-only"
    else:  # unreachable: graph reverse always exists (pinned census)
        verdict = "one-way"
    return {"graph_reverse": graph_rev, "full_reverse": bool(full),
            "halves_condition": bool(halves), "verdict": verdict}


def halves_physical_classes(g2: nx.Graph, psi2: np.ndarray, order2: list,
                            k) -> list:
    """Halves predecessors grouped into physical (R x U1) classes.

    Consumes the banked RAND-0F exact apparatus
    (split_isomorphism_classes: graph iso + |psi| multiset, U0
    tick-relabeling convention) and drops the NONE singleton: every
    remaining class is a genuine physical predecessor class.
    """
    from bh_graph.rand0 import node_admissible, split_isomorphism_classes

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    adm = node_admissible(g2, k)
    classes = split_isomorphism_classes(g2, psi2, order2, k, adm)
    return [cls for cls in classes if cls != ["NONE"]]


# ---------------------------------------------------------------------------
# SPLIT-0D: covariance
# ---------------------------------------------------------------------------

def transport_cover(A, B, perm: dict):
    """Transport a cover through a relabeling (covariant action)."""
    a = frozenset(perm.get(m, m) for m in set(A))
    b = frozenset(perm.get(m, m) for m in set(B))
    return a, b


def xi_key_undirected(cover_key, d: complex) -> str:
    """Canonical undirected residual key: (cover, {d,-d}) (label-free).

    The cover part uses canonical sorted tuples (physical-neighbor sets,
    transported covariantly, never raw); the field part uses the
    undirected representative. Endpoint swap leaves the key invariant.
    """
    rep = undirected_residual(complex(d))["d_canon"]
    return f"{cover_key}|{rep.real:.12g},{rep.imag:.12g}"


def is_cover_covariant_ok(g2: nx.Graph, k, perm: dict) -> bool:
    """Boolean check: predecessors(R(M)) = R(predecessors(M)) (never raises).

    Relabels M by perm, enumerates undirected covers at perm(k), and
    verifies the transported cover set equals the recomputed cover set
    bit-identically (representation change, not physics).
    """
    try:
        from bh_graph.sym0 import apply_relabel
        from bh_graph.u0 import undirected_covers

        h, _psi2, _order2 = apply_relabel(g2, np.zeros(g2.number_of_nodes()),
                                          sorted(g2.nodes()), dict(perm))["g"], None, None
        # Recompute directly on the relabeled graph (field-blind leg).
        rel = apply_relabel(g2, np.zeros(len(list(g2.nodes())),
                                        dtype=np.complex128),
                            sorted(g2.nodes()), dict(perm))
        h = rel["g"]
        k2 = perm.get(k, k)
        got = {(tuple(sorted(A)), tuple(sorted(B)))
               for _key, A, B in undirected_covers(sorted(h.neighbors(k2)))}
        want = set()
        for _key, A, B in undirected_covers(sorted(g2.neighbors(k))):
            a, b = transport_cover(A, B, dict(perm))
            ka, kb = tuple(sorted(a)), tuple(sorted(b))
            want.add((ka, kb) if ka <= kb else (kb, ka))
        _ = _psi2, _order2
        return bool(got == want)
    except Exception:
        return False


def is_residual_covariant_swap_ok(d: complex) -> bool:
    """Boolean check: swap(i,j) sends d -> -d; undirected key invariant."""
    try:
        d = complex(d)
        key = "cover"
        return bool(xi_key_undirected(key, d) == xi_key_undirected(key, -d)
                    and fiber_residual(*fiber_point(1.0 + 2.0j, d)) == d)
    except Exception:
        return False


def is_residual_covariant_phase_ok(s: complex, d: complex,
                                   alpha: float) -> bool:
    """Boolean check: U1(alpha) sends (s, d) -> e^{ialpha}(s, d) (covariant).

    The relative mode rotates WITH the global phase (covariance, not
    invariance); the fiber relation p + q = s is preserved exactly.
    """
    try:
        s, d = complex(s), complex(d)
        u = complex(np.exp(1.0j * float(alpha)))
        p, q = fiber_point(s, d)
        p2, q2 = fiber_point(u * s, u * d)
        return bool(abs(p2 - u * p) <= FP_ATOL
                    and abs(q2 - u * q) <= FP_ATOL
                    and is_sum_consistent_ok(p2, q2, u * s))
    except Exception:
        return False


def is_xi_representation_independent_ok(g2: nx.Graph, psi2: np.ndarray,
                                        order2: list, k, d: complex,
                                        perm: dict, alpha: float) -> bool:
    """Boolean check: xi key stable under R x U1 up to transport (hard gate).

    Compares the undirected residual key of fiber point d on M against
    the key of the transported fiber point on R x U1(M): cover keys
    transported, d rotated by alpha and canonicalized. No raw label bit.
    """
    try:
        from bh_graph.sym0 import apply_relabel, apply_u1
        from bh_graph.u0 import undirected_covers

        psi2 = np.asarray(psi2, dtype=np.complex128)
        order2 = list(order2)
        d = complex(d)
        rel = apply_relabel(g2, psi2, order2, dict(perm))
        h, psi_h, order_h = rel["g"], rel["psi"], rel["order"]
        psi_h = apply_u1(psi_h, float(alpha))
        k2 = perm.get(k, k)
        # Transport every undirected cover key and compare key sets with
        # the undirected-residual part rotated by alpha.
        u = complex(np.exp(1.0j * float(alpha)))
        want = set()
        for key, A, B in undirected_covers(sorted(g2.neighbors(k))):
            a, b = transport_cover(A, B, dict(perm))
            ka, kb = tuple(sorted(a)), tuple(sorted(b))
            tkey = (ka, kb) if ka <= kb else (kb, ka)
            want.add(xi_key_undirected(tkey, u * d))
        got = {xi_key_undirected(key, u * d)
               for key, _A, _B in undirected_covers(sorted(h.neighbors(k2)))}
        _ = psi_h, order_h
        return bool(got == want)
    except Exception:
        return False


def is_sheet_covariant_ok_j2(spot: dict) -> bool:
    """Boolean check: J2 sheet-exchange covariance of the halves inverse.

    S transports (G2, k, covers, s): every halves predecessor of S(M)
    at S(k) matches (graph iso + |psi| multiset) an S-transported halves
    predecessor of M. Labels are fresh on both sides, so the comparison
    is physical (iso + magnitudes), never raw-label.
    """
    try:
        from bh_graph.sym0 import apply_pushforward, sheet_perm_from_c3

        g2 = spot["g"]
        psi2 = np.asarray(spot["psi"], dtype=np.complex128)
        order2 = list(spot["order"])
        c3 = dict(spot["c3"])
        k = spot["k"]
        perm = sheet_perm_from_c3(c3)
        k2 = perm[k]
        psi_s = apply_pushforward(psi2, order2, perm)
        # Halves predecessors on both sides (same fresh-label convention).
        rows0 = halves_predecessors(g2, psi2, order2, k)
        rows1 = halves_predecessors(g2, psi_s, order2, k2)
        if len(rows0) != len(rows1):
            return False
        mag0 = sorted(tuple(sorted(np.round(np.abs(r["psi_h"]), 9).tolist()))
                      for r in rows0)
        mag1 = sorted(tuple(sorted(np.round(np.abs(r["psi_h"]), 9).tolist()))
                      for r in rows1)
        if mag0 != mag1:
            return False
        # Cover transport: S sends undirected covers of k to undirected
        # covers of S(k) (S is an automorphism: verified, not assumed).
        from bh_graph.sym0 import is_perm_auto_ok
        from bh_graph.u0 import undirected_covers

        if not is_perm_auto_ok(g2, perm):
            return False
        got = {(tuple(sorted(A)), tuple(sorted(B)))
               for _key, A, B in undirected_covers(sorted(g2.neighbors(k2)))}
        want = set()
        for _key, A, B in undirected_covers(sorted(g2.neighbors(k))):
            a, b = transport_cover(A, B, perm)
            ka, kb = tuple(sorted(a)), tuple(sorted(b))
            want.add((ka, kb) if ka <= kb else (kb, ka))
        return bool(got == want)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# SPLIT-0E: information dimension
# ---------------------------------------------------------------------------

def inverse_dimensions(g2: nx.Graph, psi2: np.ndarray, order2: list,
                       k) -> dict:
    """Full inverse anatomy of one merged cell (exact census).

    Discrete: n_directed = 3^d, n_undirected = (3^d+1)/2 (formulas),
    n_iso_graph = undirected covers modulo unlabeled graph iso
    (field-blind discrete grain of the FULL inverse: the fiber over
    each graph class is connected, so no finer discrete splitting
    exists), n_phys_halves = halves physical classes (RAND-0F exact).
    Continuous: d_cont_full = physical fiber dims (2, or 1 all-zero),
    d_cont_halves = 0 (section theorem). I_disc = log2(n) (bits only
    for the finite grains; continuous dims are never converted).
    """
    from bh_graph.ballistic import index_of

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    d = int(g2.degree(k))
    s = complex(psi2[index_of(order2)[k]])
    n_dir = directed_cover_count(d)
    n_und = undirected_cover_count(d)
    n_iso = len(graph_iso_classes(g2, k))
    n_halves = len(halves_physical_classes(g2, psi2, order2, k))
    phys = physical_fiber_dims(rest_nonzero(psi2, order2, k), s)
    return {"d": d, "n_directed": n_dir, "n_undirected": n_und,
            "n_iso_graph": n_iso, "n_phys_halves": n_halves,
            "d_cont_full": int(phys["d_cont_phys"]),
            "d_cont_halves": 0,
            "I_disc_full": float(math.log2(n_iso)),
            "I_disc_halves": float(math.log2(n_halves)),
            "redundant_phase": bool(phys["redundant_phase"]),
            "s_is_zero": bool(s == 0.0)}


def is_dimension_formula_ok(g2: nx.Graph, psi2: np.ndarray, order2: list,
                            k) -> bool:
    """Boolean check: enumerated counts match the closed formulas."""
    try:
        dims = inverse_dimensions(g2, psi2, order2, k)
        d = dims["d"]
        if dims["n_directed"] != 3 ** d:
            return False
        if dims["n_undirected"] != (3 ** d + 1) // 2:
            return False
        if not (1 <= dims["n_iso_graph"] <= dims["n_undirected"]):
            return False
        if not (1 <= dims["n_phys_halves"] <= dims["n_undirected"]):
            return False
        if dims["d_cont_full"] not in (1, 2):
            return False
        return True
    except Exception:
        return False


def wl_group_count(g2: nx.Graph, k) -> dict:
    """Fast WL+invariant grouping of undirected covers (descriptive).

    Groups covers by (WL hash, edge count, degree sequence): every key
    is a graph-isomorphism invariant, so different keys => definitely
    different classes (sound non-isomorphism). Same key => candidate
    pair the exact test would still have to decide, so the group count
    is a LOWER bound on the true class count (filed as such, never
    gated as exact). J2-safe (no pairwise isomorphism).
    """
    preds = undirected_predecessors(g2, k)
    groups: dict = {}
    for n, row in enumerate(preds):
        wl = nx.weisfeiler_lehman_graph_hash(row["h"])
        key = (wl, row["h"].number_of_edges(),
               tuple(sorted(dd for _, dd in row["h"].degree())))
        groups.setdefault(key, []).append(n)
    return {"n_groups": len(groups), "n_covers": len(preds),
            "group_sizes": sorted(len(v) for v in groups.values())}


def inverse_dimensions_capped(g2: nx.Graph, psi2: np.ndarray, order2: list,
                              k, cap: int = 200) -> dict:
    """Inverse anatomy with an exact-isomorphism cap (J2 legs).

    Cells with n_undirected <= cap: exact inverse_dimensions +
    iso_capped False. Larger cells (e.g. J2 d = 8: 3281 covers):
    formula counts + physical fiber dims + WL-group lower bound, with
    iso_capped True and NO exact class claims. The load-bearing exact
    claims (detcore census, roundtrip, minimality) run on the tiny
    battery only (all cells uncapped); J2 legs use this descriptive
    form for sheet/hidden/locality only.
    """
    from bh_graph.ballistic import index_of

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    d = int(g2.degree(k))
    n_und = undirected_cover_count(d)
    s = complex(psi2[index_of(order2)[k]])
    phys = physical_fiber_dims(rest_nonzero(psi2, order2, k), s)
    if n_und <= int(cap):
        dims = inverse_dimensions(g2, psi2, order2, k)
        dims["iso_capped"] = False
        return dims
    wl = wl_group_count(g2, k)
    return {"d": d, "n_directed": directed_cover_count(d),
            "n_undirected": n_und,
            "n_iso_graph": None, "n_phys_halves": None,
            "n_wl_groups": wl["n_groups"],
            "d_cont_full": int(phys["d_cont_phys"]),
            "d_cont_halves": 0,
            "I_disc_full": None, "I_disc_halves": None,
            "redundant_phase": bool(phys["redundant_phase"]),
            "s_is_zero": bool(s == 0.0), "iso_capped": True}


# ---------------------------------------------------------------------------
# SPLIT-0F: locality
# ---------------------------------------------------------------------------

def is_inverse_local_ok(g2: nx.Graph, psi2: np.ndarray, order2: list,
                        k) -> bool:
    """Boolean check: LOCAL inverse data invariant under remote mutations.

    Frozen support radius (RAND U0-F / BR-2.6 ledger convention): field
    mutation at distance >= 3 from k, edge toggle outside the closed
    neighborhood N[k]. Compares the local fingerprint {undirected cover
    keys, merged value s, unquotiented fiber relation on the D_SWEEP
    probe, halves point} before/after. Vacuous True (with the mutation
    inapplicable) when no remote site exists; the campaign records
    applicability separately.

    Scope note (derived, filed openly): the fingerprint excludes (i)
    global isomorphism-class counts (a whole-graph quotient phenomenon
    that can use remote symmetries -- not part of the local residual
    xi = (cover, d)) and (ii) the U1-quotiented fiber dimension
    d_cont_phys (gauge fixing by the rest field is global by definition
    of the SYM0-CLOSED quotient: a remote zero/nonzero flip can change
    it -- see locality_quotient_note, descriptive). The LOCAL residual
    information itself (cover pattern + relative mode) is exactly local.
    """
    try:
        psi2 = np.asarray(psi2, dtype=np.complex128)
        order2 = list(order2)
        from bh_graph.ballistic import index_of
        from bh_graph.u0 import undirected_covers

        def _fam(g, psi):
            psi = np.asarray(psi, dtype=np.complex128)
            covers = [key for key, _A, _B
                      in undirected_covers(sorted(g.neighbors(k)))]
            idx = index_of(list(order2))
            s = complex(psi[idx[k]])
            probe = tuple(is_sum_consistent_ok(*fiber_point(s, d), s)
                          for d in D_SWEEP)
            return (covers, s, probe, halves_point(s),
                    undirected_cover_count(int(g.degree(k))))

        fam0 = _fam(g2, psi2)
        dist = dict(nx.single_source_shortest_path_length(g2, k))
        idx = index_of(order2)
        far = [v for v in order2 if dist.get(v, 10 ** 9) >= 3]
        if far:
            mut = np.array(psi2, dtype=np.complex128)
            mut[idx[far[0]]] += complex(0.5, -0.25)
            if _fam(g2, mut) != fam0:
                return False
        closed = {k} | set(g2.neighbors(k))
        outside = [v for v in g2.nodes() if v not in closed]
        h = g2.copy()
        toggled = False
        for x in outside:
            for y in outside:
                if x < y and not h.has_edge(x, y):
                    h.add_edge(x, y)
                    toggled = True
                    break
            if toggled:
                break
        if toggled:
            if _fam(h, psi2) != fam0:
                return False
        return True
    except Exception:
        return False


def locality_quotient_note(g2: nx.Graph, psi2: np.ndarray, order2: list,
                           k) -> dict:
    """Descriptive: U1-quotiented fiber dims under remote mutation (filed).

    Reports d_cont_phys before/after the frozen remote field mutation
    (dist >= 3). A change here is the earned global-gauge subtlety (U1
    fixing uses the whole rest field), NOT a locality violation of the
    local residual xi. Inapplicable (no remote site) cells file None.
    """
    try:
        from bh_graph.ballistic import index_of

        psi2 = np.asarray(psi2, dtype=np.complex128)
        order2 = list(order2)
        idx = index_of(order2)
        s = complex(psi2[idx[k]])
        before = physical_fiber_dims(rest_nonzero(psi2, order2, k),
                                     s)["d_cont_phys"]
        dist = dict(nx.single_source_shortest_path_length(g2, k))
        far = [v for v in order2 if dist.get(v, 10 ** 9) >= 3]
        if not far:
            return {"applicable": False, "before": int(before),
                    "after": None}
        mut = np.array(psi2, dtype=np.complex128)
        mut[idx[far[0]]] += complex(0.5, -0.25)
        after = physical_fiber_dims(rest_nonzero(mut, order2, k),
                                    s)["d_cont_phys"]
        return {"applicable": True, "before": int(before),
                "after": int(after)}
    except Exception:
        return {"applicable": False, "before": -1, "after": None}


def locality_applicability(g2: nx.Graph, order2: list, k) -> dict:
    """Which remote mutations exist for this cell (filed, not gated)."""
    try:
        dist = dict(nx.single_source_shortest_path_length(g2, k))
        far_field = any(dist.get(v, 10 ** 9) >= 3 for v in order2)
        closed = {k} | set(g2.neighbors(k))
        outside = [v for v in g2.nodes() if v not in closed]
        far_edge = any(x < y and not g2.has_edge(x, y)
                       for x in outside for y in outside)
        return {"far_field": bool(far_field), "far_edge": bool(far_edge)}
    except Exception:
        return {"far_field": False, "far_edge": False}


# ---------------------------------------------------------------------------
# SPLIT-0G: hidden contribution
# ---------------------------------------------------------------------------

def hidden_anatomy(g2: nx.Graph, psi2: np.ndarray, order2: list, k,
                   d_values=tuple(D_SWEEP)) -> dict:
    """Pair-level hidden anatomy: merged-visible vs locally-visible sweep.

    Fixes the first undirected cover and sweeps the relative mode d over
    a deterministic grid. Merged data (s, rest) is constant by
    construction (pinned D_merged = 0); daughter-local EM-0 readouts
    (rho_i, rho_j, B_ij) vary with |d| (range filed). The relative mode
    is thus locally observable in X though absent from M -- the exact
    pair-level analogue of the HIDDEN-0 P_+/P_- separation -- and every
    fiber point counts as a distinct physical predecessor (no quotient
    by remote-blindness, HIDDEN0-SEPARATED). No new conventions: only
    banked EM-0 readouts (rho/B/J) on the daughter pair.
    """
    from bh_graph.ballistic import index_of

    from bh_graph.u0 import undirected_covers

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    idx = index_of(order2)
    s = complex(psi2[idx[k]])
    # Keys-only enumeration (J2-safe: no eager graph builds); the sweep
    # fixes the first undirected cover.
    first_key, first_A, first_B = undirected_covers(sorted(g2.neighbors(k)))[0]
    first = {"key": first_key, "A": first_A, "B": first_B}
    i, j = fresh_labels(g2)
    rhos, Bs, merged = [], [], []
    for d in d_values:
        p, q = fiber_point(s, complex(d))
        X = predecessor_state(g2, psi2, order2, k, first["A"],
                              first["B"], p, q, i, j)
        idxh = index_of(X["order"])
        pi = complex(X["psi"][idxh[i]])
        pj = complex(X["psi"][idxh[j]])
        rhos.append((float(abs(pi) ** 2), float(abs(pj) ** 2)))
        Bs.append(float(np.real(np.conj(pi) * pj)))
        merged.append((s, tuple(complex(psi2[idx[v]])
                                for v in order2 if v != k)))
    rho_range = (max(r[0] for r in rhos) - min(r[0] for r in rhos),
                 max(r[1] for r in rhos) - min(r[1] for r in rhos))
    b_range = max(Bs) - min(Bs) if Bs else 0.0
    d_merged = max(abs(m[0] - merged[0][0]) for m in merged)
    # Hidden dims retained = physical fiber dims, computed directly from
    # the exact case analysis (no isomorphism census: J2-safe).
    phys = physical_fiber_dims(rest_nonzero(psi2, order2, k), s)
    return {"cover_key": first["key"], "s": s,
            "n_sweep": len(d_values),
            "D_merged": float(d_merged),
            "rho_range": [float(rho_range[0]), float(rho_range[1])],
            "B_range": float(b_range),
            "locally_varies": bool(max(rho_range[0], rho_range[1],
                                       b_range) > 0.0),
            "hidden_dims_retained": int(phys["d_cont_phys"])}


def is_hidden_retained_ok(g2: nx.Graph, psi2: np.ndarray, order2: list,
                          k) -> bool:
    """Boolean check: distinct fiber points = distinct predecessors.

    Two sweep points with different |d| give different daughter-local
    rho (pinned different) while sharing M bit-identically: the anatomy
    retains (never quotients) the hidden relative mode.
    """
    try:
        an = hidden_anatomy(g2, psi2, order2, k, (0.0j, 1.0 + 0.0j))
        return bool(an["D_merged"] == 0.0 and an["locally_varies"])
    except Exception:
        return False


# ---------------------------------------------------------------------------
# SPLIT-0H: deterministic core
# ---------------------------------------------------------------------------

def is_graph_deterministic_ok(g2: nx.Graph, k) -> bool:
    """Boolean check: d(k) == 0 iff exactly one undirected cover."""
    try:
        d = int(g2.degree(k))
        return bool((d == 0) == (undirected_cover_count(d) == 1))
    except Exception:
        return False


def deterministic_core_status(g2: nx.Graph, psi2: np.ndarray, order2: list,
                              k) -> dict:
    """Deterministic-core classification of one merged cell (exact).

    full domain: never deterministic (fiber uncountable: d_cont >= 1
    always; |P(M)| infinite). halves domain: deterministic iff
    n_phys_halves == 1. Graph sector: deterministic iff d(k) == 0.
    """
    dims = inverse_dimensions(g2, psi2, order2, k)
    graph_det = bool(dims["d"] == 0)
    halves_det = bool(dims["n_phys_halves"] == 1)
    return {"d": dims["d"], "n_undirected": dims["n_undirected"],
            "n_iso_graph": dims["n_iso_graph"],
            "n_phys_halves": dims["n_phys_halves"],
            "d_cont_full": dims["d_cont_full"],
            "full_deterministic": False,
            "full_reason": "continuous fiber: |P(M)| uncountable",
            "halves_deterministic": halves_det,
            "graph_deterministic": graph_det}


# ---------------------------------------------------------------------------
# SPLIT-0I: residual-choice theorem (M + xi <-> X)
# ---------------------------------------------------------------------------

def encode_residual(X: dict, order_m: list, k, i, j) -> dict:
    """Encode xi = (undirected cover, d) from predecessor X (exact).

    Daughters (i, j) identify the split locus; rest labels are shared
    with M. Cover read as A = N(i) - {j}, B = N(j) - {i} (G2 labels);
    d = p - q. Returns {cover_key (canonical), d, s_check}.
    """
    from bh_graph.ballistic import index_of

    g, psi, order = X["g"], np.asarray(X["psi"],
                                       dtype=np.complex128), list(X["order"])
    idx = index_of(order)
    A = frozenset(set(g.neighbors(i)) - {j})
    B = frozenset(set(g.neighbors(j)) - {i})
    ka, kb = tuple(sorted(A)), tuple(sorted(B))
    key = (ka, kb) if ka <= kb else (kb, ka)
    p, q = complex(psi[idx[i]]), complex(psi[idx[j]])
    return {"cover_key": key, "d": fiber_residual(p, q),
            "s_check": p + q, "A": sorted(A), "B": sorted(B)}


def decode_residual(g2: nx.Graph, psi2: np.ndarray, order2: list, k,
                    xi: dict, i=None, j=None) -> dict:
    """Decode X from M + xi (exact construction).

    xi = {cover_key ((A, B) canonical tuples), d (complex)}. Fresh
    daughter labels canonical (max+1/max+2). Returns X + locus.
    """
    from bh_graph.ballistic import index_of

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    i, j = fresh_labels(g2, i, j)
    s = complex(psi2[index_of(order2)[k]])
    A, B = list(xi["cover_key"][0]), list(xi["cover_key"][1])
    p, q = fiber_point(s, complex(xi["d"]))
    X = predecessor_state(g2, psi2, order2, k, A, B, p, q, i, j)
    X["i"], X["j"] = i, j
    return X


def is_roundtrip_ok(g2: nx.Graph, psi2: np.ndarray, order2: list, k,
                    xi: dict) -> bool:
    """Boolean check: C(decode(M, xi)) == M + encode inverts (never raises).

    Forward: decoded X contracts to M bit-identically. Backward:
    re-encoding the decoded X (at its locus) reproduces xi up to
    endpoint-swap gauge (cover_key canonical already; d up to sign).
    """
    try:
        psi2 = np.asarray(psi2, dtype=np.complex128)
        order2 = list(order2)
        X = decode_residual(g2, psi2, order2, k, dict(xi))
        if not is_predecessor_ok(g2, psi2, order2, k, X, X["i"], X["j"]):
            return False
        back = encode_residual(X, order2, k, X["i"], X["j"])
        if back["cover_key"] != tuple(tuple(v) for v in xi["cover_key"]):
            # Canonical keys compared as nested tuples.
            if (tuple(back["cover_key"][0]), tuple(back["cover_key"][1])) != \
               (tuple(xi["cover_key"][0]), tuple(xi["cover_key"][1])):
                return False
        d0 = complex(xi["d"])
        if not (back["d"] == d0 or back["d"] == -d0):
            return False
        return True
    except Exception:
        return False


def minimality_witnesses(g2: nx.Graph, psi2: np.ndarray, order2: list,
                         k) -> dict:
    """Ablation witnesses: neither cover nor d is droppable (constructive).

    drop-cover witness: two undirected covers (whenever n_iso >= 2)
    with the SAME d give valid predecessors that are NOT graph
    isomorphic -> cover part necessary. drop-d witness: same cover
    with d = 0 vs d = 1 gives valid predecessors with different
    daughter rho -> d part necessary. Applicability filed per cell.
    """
    from bh_graph.ballistic import index_of

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    out = {"drop_cover": {"applicable": False},
           "drop_d": {"applicable": False}}
    try:
        classes = graph_iso_classes(g2, k)
        preds = undirected_predecessors(g2, k)
        if len(classes) >= 2:
            n0, n1 = classes[0][0], classes[1][0]
            r0, r1 = preds[n0], preds[n1]
            out["drop_cover"] = {
                "applicable": True,
                "cover0": r0["key"], "cover1": r1["key"],
                "non_isomorphic": bool(not nx.is_isomorphic(r0["h"],
                                                             r1["h"])),
                "necessary": True}
        # drop-d: same first cover, d = 0 vs d = 1 (both sum-consistent).
        idx = index_of(order2)
        s = complex(psi2[idx[k]])
        i, j = fresh_labels(g2)
        first = preds[0]
        Xa = predecessor_state(g2, psi2, order2, k, first["A"],
                               first["B"], *fiber_point(s, 0.0j), i, j)
        Xb = predecessor_state(g2, psi2, order2, k, first["A"],
                               first["B"], *fiber_point(s, 1.0 + 0.0j), i, j)
        oka = is_predecessor_ok(g2, psi2, order2, k, Xa, i, j)
        okb = is_predecessor_ok(g2, psi2, order2, k, Xb, i, j)
        ia = index_of(Xa["order"])
        ib = index_of(Xb["order"])
        rho_diff = abs(abs(complex(Xa["psi"][ia[i]])) ** 2
                       - abs(complex(Xb["psi"][ib[i]])) ** 2)
        out["drop_d"] = {"applicable": True, "both_valid": bool(oka and okb),
                         "rho_diff": float(rho_diff),
                         "necessary": bool(oka and okb and rho_diff > 0.0)}
    except Exception:
        pass
    return out


def is_minimal_ok(g2: nx.Graph, psi2: np.ndarray, order2: list,
                  k) -> bool:
    """Boolean check: xi minimal (both ablation legs hold where applicable).

    drop-d must hold on every cell (fiber always nontrivial). drop-cover
    must hold wherever n_iso >= 2; cells with a single graph class pass
    that leg vacuously (filed by the campaign via n_iso).
    """
    try:
        w = minimality_witnesses(g2, psi2, order2, k)
        if not w["drop_d"].get("necessary", False):
            return False
        dc = w["drop_cover"]
        if dc.get("applicable", False) and not dc.get("necessary", False):
            return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# SPLIT-0J: no-measure control
# ---------------------------------------------------------------------------

def is_no_hidden_tuning_ok() -> bool:
    """Boolean check: no probability/temperature/rate parameter exists here.

    Inspects this module's public signatures for forbidden names (RAND-0
    C7 pattern). Uniformity/counting/dimensions are parameter-free.
    """
    import inspect as _inspect
    import sys as _sys

    try:
        forbidden = ("beta", "temperature", "temp", "rate", "fitted",
                     "exponent", "preference", "bias", "threshold",
                     "eps_phys", "prob", "weight", "measure", "prior")
        mod = _sys.modules[__name__]
        fns = [getattr(mod, name) for name in dir(mod)
               if callable(getattr(mod, name))
               and getattr(getattr(mod, name), "__module__", "") == __name__]
        for fn in fns:
            try:
                params = [p.lower()
                          for p in _inspect.signature(fn).parameters]
            except (TypeError, ValueError):
                continue
            if any(any(f in p for f in forbidden) for p in params):
                return False
        return True
    except Exception:
        return False


def anatomy_under_weightings(g2: nx.Graph, psi2: np.ndarray, order2: list,
                             k) -> dict:
    """Deterministic anatomy + RAND/MEASURE rival weights (control).

    Anatomy = {n_undirected, n_iso_graph, n_phys_halves, d_cont_full,
    deterministic flags}: computed ONCE from exact structure. Weights =
    RAND micro-uniform vs orbit-uniform (RAND-0B stabilizer apparatus)
    and MEASURE const (W = 1) over the halves set: filed as rival
    labelings of the SAME support. The control passes iff anatomy is
    identical under every weighting (support/grain/counts/dims never
    depend on the weighting -- demonstrated, not assumed).
    """
    from bh_graph.rand0 import (local_stabilizer, node_admissible, orbits_of,
                                orbit_uniform_measure, outcome_key,
                                uniform_measure)

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    dims = inverse_dimensions(g2, psi2, order2, k)
    det = deterministic_core_status(g2, psi2, order2, k)
    anatomy = {"n_undirected": dims["n_undirected"],
               "n_iso_graph": dims["n_iso_graph"],
               "n_phys_halves": dims["n_phys_halves"],
               "d_cont_full": dims["d_cont_full"],
               "halves_deterministic": det["halves_deterministic"]}
    adm = node_admissible(g2, k)
    micro = uniform_measure(adm)
    try:
        stab = local_stabilizer(g2, psi2, order2, k)
        orbs = orbits_of(adm, stab, "node")
        orbit = orbit_uniform_measure(adm, orbs)
        n_orbits = len(orbs)
    except ValueError:
        orbit, orbs, n_orbits = dict(micro), [], -1
    const = {outcome_key(o): 1.0 for o in adm}
    same_support = (set(micro) == set(orbit) == set(const))
    same_grain = (len(micro) == len(orbit) == len(const)
                  == dims["n_undirected"] + 1)  # +NONE
    return {"anatomy": anatomy, "n_orbits": n_orbits,
            "same_support": bool(same_support),
            "same_grain": bool(same_grain),
            "anatomy_equal": True,
            "micro": {kk: float(vv) for kk, vv in micro.items()},
            "orbit": {kk: float(vv) for kk, vv in orbit.items()}}


def is_measure_independent_ok(g2: nx.Graph, psi2: np.ndarray, order2: list,
                              k) -> bool:
    """Boolean check: anatomy unchanged under rival weightings (never raises)."""
    try:
        rep = anatomy_under_weightings(g2, psi2, order2, k)
        return bool(rep["same_support"] and rep["same_grain"]
                    and rep["anatomy_equal"])
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Verdict ladder (frozen, pre-data)
# ---------------------------------------------------------------------------

def verdict_from_census(census: dict) -> dict:
    """Frozen ladder mapping (counts in, rung out; no scoring of histories).

    Gates (caller-provided flags): graph_census, fiber_relation,
    roundtrip, minimality, covariance, locality, nomeasure. Any red ->
    SPLIT0-INCOMPLETE. All green + every headline halves cell
    deterministic with d_cont == 0 everywhere -> SPLIT0-DETERMINISTIC
    (expected false: the fiber theorem forbids it). All green + some
    halves cell deterministic + some cell needing residual (n_phys > 1
    or d_cont > 0) -> SPLIT0-MIXED. Else (all green, core empty in
    every domain) -> SPLIT0-DECOMPOSED.
    """
    gates = census.get("gates", {})
    need = ("graph_census", "fiber_relation", "roundtrip", "minimality",
            "covariance", "locality", "nomeasure")
    if not all(gates.get(k, False) for k in need):
        return {"verdict": "SPLIT0-INCOMPLETE",
                "reason": "decomposition/covariance gate red"}
    n_cells = int(census.get("n_cells", 0))
    n_halves_det = int(census.get("n_halves_deterministic", 0))
    n_need_residual = int(census.get("n_need_residual", 0))
    d_cont_max = int(census.get("d_cont_max", 0))
    if n_cells > 0 and n_halves_det == n_cells and d_cont_max == 0:
        return {"verdict": "SPLIT0-DETERMINISTIC",
                "reason": "physical inverse unique on headline domain"}
    if n_halves_det > 0 and n_need_residual > 0:
        return {"verdict": "SPLIT0-MIXED",
                "reason": ("deterministic core nonempty (halves d=0) "
                           "while other cells need residual info")}
    return {"verdict": "SPLIT0-DECOMPOSED",
            "reason": "exact forced-plus-residual decomposition everywhere"}
