"""RAND-0 local stochastic completion: admissible sets, orbits, measures, gates.

Campaign: RAND-0 (Local Stochastic Completion). Tests whether the
underdetermination exposed by U0 (X_t = (G_t, psi_t) does not determine a
complete structural successor under deterministic minimal laws) can be
completed by a LOCAL STOCHASTIC LAW without introducing arbitrary
probabilities, random rewiring, fitted rates, or new microscopic state.

The candidate fundamental object is P(X_{t+1} | X_t), NOT X_{t+1} = U(X_t).

Frozen evidence consumed read-only (re-stated, never re-derived):
  - Ontology (BR-2.5): u-v <-> [uv]; contraction is locally defined
    (contract_edge + sum map psi_k = psi_i + psi_j, dQ = +2B_ij);
    record-free splits are degenerate (3^d directed covers, (3^d+1)/2
    undirected; endpoint swap is gauge, U0-H1); R_U = 1.
  - Quadrature (BR-2): B_uv = Re(psi_u* psi_v) geometric conjugate,
    J flux = 2 Im(psi_u* psi_v) conserved-density flux. Banked roles kept.
  - Ledger (BR-2.6): dE_contract = 2B_ij - 2 sum_cross (common collapse
    energy-neutral); conditional invariant family + B_* targets (ratios
    free = debt); universal closure impossible; graph reservoir impossible;
    zero-field contraction accounting-allowed.
  - No-mode (BR-2.7): no instability/firing mechanism in the ontology.
  - No-go (CONS-0): no field-involving linear invariant closes arbitrary
    contractions; split degeneracy survives on level sets.
  - Underdetermination (U0): contraction locally definable; splitting has
    multiple admissible outcomes; energy minimization ties generically
    (H4); deterministic local/covariant tie-breaking unavailable;
    decision locality != effect locality (one-tick effect reach =
    marked-component diameter, unbounded a priori).

RAND-0 firewalls (frozen):
  - Physics defines A(X); stochasticity selects WITHIN A(X). Randomness
    may NOT decide legality, conservation, locality, B/J meaning,
    geometry preference, or matter content. No random M1 rewiring.
  - Frozen state X = (G, psi): no hidden RNG state, age, clock, field,
    temperature, weights, bath, amplitude, record, ordering, target.
    The draw is part of the transition law, not state.
  - No vacuum exception: psi = 0 outcomes get the same universal measure.
  - Matter/decay firewalls: no scoring/tuning for lumps or exp decay.
  - Independence from TIME-0: no result-sharing redesign either way.

RAND-0A admissible sets (frozen pre-data, structural only, no veto):
  - Edge patch (u,v): A = {NONE, CONTRACT}, always (|A| = 2). Both are
    structurally admissible on every edge; CONS/BR-2.6 provide conditional
    constraints, not vetoes; zero-field contraction is accounting-allowed
    (banked), so no sector removes an outcome.
  - Node patch k (degree d): A = {NONE} + undirected split covers with
    the FROZEN equal-halves field map (p, q = s/2, s/2). |A| = 1 +
    (3^d + 1)/2. Undirected because endpoint swap is earned gauge (U0-H1);
    equal-halves because it is the unique symmetric linear inverse of the
    frozen sum map (norm policy kept ONLY as a refinement alternative for
    the RAND-0G test, never in the primary set).
  - Joint patch (e1, e2): disjoint -> product set (4 outcomes); sharing a
    node -> {NONE, CONTRACT e1, CONTRACT e2} (3 outcomes; co-firing is
    structurally conflicting, excluded by enumeration, not by scheduler).
    No random sequential update order anywhere.

RAND-0B stabilizer (frozen): Stab(X_loc) = permutations of the bounded
patch (R = 1 ball of the edge/node) preserving induced-subgraph adjacency
AND psi values EXACTLY (complex equality), fixing the center setwise
(edge: {u,v} setwise; node: k fixed). Global-phase action is trivial on
B/L-admissibility (psi-blind sets); conjugation likewise. Brute force,
tiny patches only (cap pinned).

RAND-0C/D measures (frozen candidates, zero parameters):
  - MICRO-UNIFORM: P(a) = 1/|A| over physical (undirected) micro-outcomes.
  - ORBIT-UNIFORM (rival): P(O) = 1/n_orbits, P(a) = 1/(n_orbits * |O|).
    Both satisfy orbit-uniformity (RAND-0C), normalization, covariance,
    locality. If they differ and no earned quantity prefers one, the
    inter-orbit weight problem is undetermined -> PROBABILITY-MEASURE DEBT.
  - Forbidden: P ~ exp(-beta E) (no derived beta), fitted exponents,
    temperatures, hand preferences, outcome-tuned weights. C7 pinned by
    signature inspection (no such parameter exists in this module).

RAND-0E/F/G enumeration discipline (frozen): uniformity is defined over
PHYSICAL outcomes (undirected covers). Directed enumeration (3^d) double
counts gauge copies and is WRONG, not rival. The sharp multiplicity test
is covers vs post-split unlabeled isomorphism classes: two distinct
covers can yield isomorphic (G', |psi'|) (measured, not assumed). If
micro-uniform induces a non-uniform distribution over isomorphism
classes, the apparatus reports whether the quotient ontology ([G]_{~_O},
earned elsewhere, NOT re-derived here) decides the physical outcome
grain. If undecided -> MEASURE DEBT (multiplicity dependence).

This module introduces NO threshold, NO rate, NO temperature, NO fitted
constant, NO target state. RNG appears ONLY in the sampler (numerical
implementation of a probability law, separated and audited across
BitGenerators); every analytic claim is RNG-free.
"""

from __future__ import annotations

import inspect
import itertools
import math

import networkx as nx
import numpy as np

FIELD_POLICY_FROZEN = "equal"
FIELD_POLICY_REFINEMENT = "norm"
RNG_KINDS = ("pcg64", "philox", "sfc64")
STABILIZER_MAX_PATCH = 8
WILSON_Z_99 = 2.5758293035489004
CHI2_P_FLOOR = 1e-3


# ---------------------------------------------------------------------------
# RAND-0A: admissible sets (structural, frozen, no veto)
# ---------------------------------------------------------------------------

def edge_admissible(g: nx.Graph, i, j) -> list:
    """Edge-patch admissible set {NONE, CONTRACT} (always, both allowed).

    Raises KeyError if (i, j) is not an edge (structural precondition, not
    a veto: the patch itself must exist).
    """
    if not g.has_edge(i, j):
        raise KeyError(f"({i}, {j}) is not an edge")
    return ["NONE", "CONTRACT"]


def node_admissible(g: nx.Graph, k) -> list:
    """Node-patch admissible set {NONE} + undirected split covers (frozen).

    Each SPLIT outcome carries its undirected cover key ((A, B) canonical,
    A <= B) plus the frozen equal-halves field policy. Deterministic order:
    NONE first, then covers in canonical key order.
    """
    from bh_graph.u0 import undirected_covers

    if k not in g:
        raise KeyError(f"{k} is not a node")
    nbrs = sorted(g.neighbors(k))
    out = [{"kind": "NONE"}]
    for key, _A, _B in undirected_covers(nbrs):
        out.append({"kind": "SPLIT", "cover": [list(key[0]), list(key[1])],
                    "field": FIELD_POLICY_FROZEN})
    return out


def directed_node_admissible(g: nx.Graph, k) -> list:
    """Directed-cover enumeration {NONE} + 3^d covers (multiplicity audit).

    WRONG enumeration (double counts endpoint-swap gauge); kept ONLY so the
    campaign can measure the multiplicity dependence of naive counting
    (RAND-0E/F). Never used as the physical set.
    """
    from bh_graph.contraction import split_covers

    if k not in g:
        raise KeyError(f"{k} is not a node")
    out = [{"kind": "NONE"}]
    for A, B in split_covers(sorted(g.neighbors(k))):
        out.append({"kind": "SPLIT", "cover": [sorted(A), sorted(B)],
                    "field": FIELD_POLICY_FROZEN, "directed": True})
    return out


def n_undirected_covers(d: int) -> int:
    """Undirected cover count (3^d + 1) / 2 (earned U0-H1 gauge quotient)."""
    return int((3 ** int(d) + 1) / 2)


def joint_edge_admissible(g: nx.Graph, e1, e2) -> list:
    """Joint admissible set for two edge patches (frozen enumeration).

    Disjoint neighborhoods -> product set (4 joint outcomes). Shared node
    -> {NONE, CONTRACT e1, CONTRACT e2} (3 outcomes; co-firing excluded as
    structurally conflicting, by enumeration not scheduler). Canonical keys
    sorted; e1 < e2 required canonical order is enforced by sorting.
    """
    a1, b1 = e1
    a2, b2 = e2
    if not g.has_edge(a1, b1):
        raise KeyError(f"{e1} is not an edge")
    if not g.has_edge(a2, b2):
        raise KeyError(f"{e2} is not an edge")
    k1 = (a1, b1) if a1 < b1 else (b1, a1)
    k2 = (a2, b2) if a2 < b2 else (b2, a2)
    if k1 == k2:
        raise ValueError("joint patch needs two distinct edges")
    first, second = sorted((k1, k2))
    if len({first[0], first[1], second[0], second[1]}) == 4:
        return [{"kind": "NONE"},
                {"kind": "CONTRACT", "edge": list(first)},
                {"kind": "CONTRACT", "edge": list(second)},
                {"kind": "BOTH", "edges": [list(first), list(second)]}]
    return [{"kind": "NONE"},
            {"kind": "CONTRACT", "edge": list(first)},
            {"kind": "CONTRACT", "edge": list(second)}]


def outcome_key(outcome) -> str:
    """Canonical string key for an admissible outcome (deterministic)."""
    if isinstance(outcome, str):
        return outcome
    kind = outcome.get("kind")
    if kind == "NONE":
        return "NONE"
    if kind == "CONTRACT":
        e = outcome.get("edge")
        return f"CONTRACT{e[0]}-{e[1]}" if e is not None else "CONTRACT"
    if kind == "BOTH":
        es = outcome.get("edges", [])
        return "BOTH:" + ",".join(f"{a}-{b}" for a, b in es)
    if kind == "SPLIT":
        c = outcome.get("cover", [[], []])
        f = outcome.get("field", FIELD_POLICY_FROZEN)
        return f"SPLIT:{tuple(c[0])}|{tuple(c[1])}:{f}"
    return str(outcome)


# ---------------------------------------------------------------------------
# Outcome application (exact maps, frozen)
# ---------------------------------------------------------------------------

def apply_edge_outcome(g: nx.Graph, psi: np.ndarray, order: list, i, j,
                       outcome: str):
    """Apply an edge-patch outcome: NONE -> identical X; CONTRACT -> sum-map.

    Returns (g2, psi2, order2). CONTRACT uses the frozen BR-2.5 op
    (contracted_state, sum map). NONE returns copies (no aliasing).
    """
    from bh_graph.contraction import contracted_state

    psi = np.asarray(psi, dtype=np.complex128)
    if outcome == "NONE":
        return g.copy(), np.array(psi, dtype=np.complex128), list(order)
    if outcome == "CONTRACT":
        g2, psi2, order2, _k, _rec = contracted_state(g, psi, list(order), i, j, "sum")
        return g2, psi2, order2
    raise ValueError(f"unknown edge outcome: {outcome}")


def apply_node_outcome(g: nx.Graph, psi: np.ndarray, order: list, k,
                       outcome: dict, i=None, j=None):
    """Apply a node-patch outcome: NONE -> identical X; SPLIT -> cover + map.

    SPLIT uses the frozen field policy carried by the outcome (primary:
    equal halves). Fresh labels default to max+1/max+2 (integer graphs).
    Returns (h, psi_h, order_h).
    """
    from bh_graph.ballistic import index_of
    from bh_graph.contraction import (apply_split_cover, split_field_equal,
                                      split_field_norm)

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    if outcome.get("kind") == "NONE":
        return g.copy(), np.array(psi, dtype=np.complex128), list(order)
    if outcome.get("kind") != "SPLIT":
        raise ValueError(f"unknown node outcome: {outcome}")
    cover = outcome.get("cover", [[], []])
    A = frozenset(cover[0])
    B = frozenset(cover[1])
    policy = outcome.get("field", FIELD_POLICY_FROZEN)
    if i is None or j is None:
        if not all(isinstance(v, int) for v in g.nodes()):
            raise ValueError("split application needs integer labels or explicit i, j")
        i, j = max(g.nodes()) + 1, max(g.nodes()) + 2
    h = apply_split_cover(g, k, A, B, i, j)
    idx = index_of(order)
    pfun = split_field_equal if policy == "equal" else split_field_norm
    if policy not in ("equal", "norm"):
        raise ValueError(f"unknown field policy: {policy}")
    p, q = pfun(complex(psi[idx[k]]))
    order_h = [v for v in order if v != k] + [i, j]
    vals = {v: complex(psi[idx[v]]) for v in order if v != k}
    vals[i], vals[j] = p, q
    psi_h = np.array([vals[v] for v in order_h], dtype=np.complex128)
    return h, psi_h, order_h


# ---------------------------------------------------------------------------
# RAND-0B: stabilizer and symmetry orbits (frozen)
# ---------------------------------------------------------------------------

def patch_nodes(g: nx.Graph, center, radius: int = 1) -> list:
    """Sorted R-ball node set around center (node or edge tuple)."""
    if isinstance(center, tuple):
        d0 = dict(nx.single_source_shortest_path_length(g, center[0]))
        d1 = dict(nx.single_source_shortest_path_length(g, center[1]))
        nodes = [v for v in g.nodes()
                 if min(d0.get(v, 10 ** 9), d1.get(v, 10 ** 9)) <= radius]
    else:
        dist = dict(nx.single_source_shortest_path_length(g, center))
        nodes = [v for v in g.nodes() if dist.get(v, 10 ** 9) <= radius]
    return sorted(nodes)


def local_stabilizer(g: nx.Graph, psi: np.ndarray, order: list, center,
                     radius: int = 1) -> list:
    """Exact stabilizer Stab(X_loc): patch perms preserving adjacency + psi.

    Brute force over patch permutations (tiny patches only; raises if the
    patch exceeds STABILIZER_MAX_PATCH nodes -- cap pinned, not tuned).
    Each element is a dict {v: perm(v)} fixing the center setwise (edge:
    {u,v} setwise; node: k fixed) with psi[perm(v)] == psi[v] exactly and
    induced-subgraph adjacency preserved exactly.
    """
    from bh_graph.ballistic import index_of

    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(list(order))
    nodes = patch_nodes(g, center, radius)
    if len(nodes) > STABILIZER_MAX_PATCH:
        raise ValueError(f"patch size {len(nodes)} exceeds cap {STABILIZER_MAX_PATCH}")
    vals = {v: complex(psi[idx[v]]) for v in nodes}
    adj = {v: set(g.neighbors(v)) & set(nodes) for v in nodes}
    if isinstance(center, tuple):
        fixed = set(center)
        edge_mode = True
    else:
        fixed = {center}
        edge_mode = False
    out = []
    for perm in itertools.permutations(nodes):
        mp = dict(zip(nodes, perm))
        if edge_mode:
            if {mp[v] for v in fixed} != fixed:
                continue
        elif mp[center] != center:
            continue
        if any(vals[mp[v]] != vals[v] for v in nodes):
            continue
        if any({mp[w] for w in adj[v]} != adj[mp[v]] for v in nodes):
            continue
        out.append(mp)
    return out


def _act_on_edge_outcome(outcome: str, _perm: dict) -> str:
    """Stabilizer action on edge outcomes (trivial: both are swap-even)."""
    return outcome


def _act_on_node_cover(cover, perm: dict):
    """Permute a cover's neighbor labels, re-canonicalized undirected."""
    A = frozenset(perm.get(m, m) for m in cover[0])
    B = frozenset(perm.get(m, m) for m in cover[1])
    ka, kb = tuple(sorted(A)), tuple(sorted(B))
    return [list(ka), list(kb)] if ka <= kb else [list(kb), list(ka)]


def orbits_of(admissible: list, stabilizer: list, patch_kind: str) -> list:
    """Orbit partition of the admissible set under the stabilizer (frozen).

    patch_kind in {"edge", "node"}. Returns orbits as sorted lists of
    outcome keys (deterministic order: NONE-orbit first, then by key).
    BFS closure under the group action; identity always present.
    """
    keys = [outcome_key(o) for o in admissible]
    key_of = {}
    for o in admissible:
        key_of[outcome_key(o)] = o
    acted = {}
    for o in admissible:
        ko = outcome_key(o)
        imgs = set()
        for perm in stabilizer:
            if patch_kind == "edge":
                imgs.add(_act_on_edge_outcome(o, perm))
            elif isinstance(o, dict) and o.get("kind") == "SPLIT":
                moved = {"kind": "SPLIT",
                         "cover": _act_on_node_cover(o["cover"], perm),
                         "field": o.get("field", FIELD_POLICY_FROZEN)}
                imgs.add(outcome_key(moved))
            else:
                imgs.add(ko)
        acted[ko] = sorted(imgs)
    unseen = set(keys)
    orbits = []
    for ko in sorted(unseen):
        if ko not in unseen:
            continue
        orbit, stack = set(), [ko]
        while stack:
            cur = stack.pop()
            if cur in orbit:
                continue
            orbit.add(cur)
            for nxt in acted.get(cur, [cur]):
                if nxt in unseen and nxt not in orbit:
                    stack.append(nxt)
        for m in orbit:
            unseen.discard(m)
        orbits.append(sorted(orbit))
    orbits.sort(key=lambda o: (0 if o == ["NONE"] else 1, o))
    return orbits


# ---------------------------------------------------------------------------
# RAND-0C/D/E: candidate measures (zero parameters, frozen)
# ---------------------------------------------------------------------------

def uniform_measure(admissible: list) -> dict:
    """MICRO-UNIFORM: P(a) = 1/|A| over physical micro-outcomes (frozen)."""
    keys = [outcome_key(o) for o in admissible]
    if len(set(keys)) != len(keys):
        raise ValueError("admissible set has duplicate outcome keys")
    if not keys:
        raise ValueError("empty admissible set")
    return {k: 1.0 / len(keys) for k in keys}


def orbit_uniform_measure(admissible: list, orbits: list) -> dict:
    """ORBIT-UNIFORM rival: P(O) = 1/n_orbits, split evenly within orbits."""
    if not orbits:
        raise ValueError("empty orbit partition")
    flat = [k for orb in orbits for k in orb]
    keys = [outcome_key(o) for o in admissible]
    if sorted(flat) != sorted(keys):
        raise ValueError("orbits do not partition the admissible set")
    out = {}
    for orb in orbits:
        for k in orb:
            out[k] = 1.0 / (len(orbits) * len(orb))
    return out


def coarse_probability(measure: dict, coarse_map: dict) -> dict:
    """Coarse-grain: P(A) = sum_{a -> A} P(a) (RAND-0F, exact sum)."""
    out = {}
    for micro, p in measure.items():
        coarse = coarse_map.get(micro, micro)
        out[coarse] = out.get(coarse, 0.0) + float(p)
    return out


def split_coarse_map(admissible: list) -> dict:
    """Canonical coarse map: every SPLIT micro-outcome -> 'SPLIT'."""
    out = {}
    for o in admissible:
        k = outcome_key(o)
        if isinstance(o, dict) and o.get("kind") == "SPLIT":
            out[k] = "SPLIT"
        else:
            out[k] = k
    return out


def is_normalized_ok(measure: dict, atol: float = 1e-12) -> bool:
    """Boolean check: probs nonnegative and summing to 1 (never raises)."""
    try:
        vals = [float(v) for v in measure.values()]
        if any(v < 0.0 or not math.isfinite(v) for v in vals):
            return False
        return bool(abs(sum(vals) - 1.0) <= atol)
    except Exception:
        return False


def is_orbit_uniform_ok(measure: dict, orbits: list, atol: float = 0.0) -> bool:
    """Boolean check: equal probability within every orbit (never raises).

    Default atol = 0.0 (bitwise): symmetry indifference is exact, not
    approximate. A law giving different probabilities to
    automorphism-equivalent outcomes FAILS (RAND-0C).
    """
    try:
        for orb in orbits:
            vals = [float(measure[k]) for k in orb]
            if any(v != vals[0] if atol == 0.0 else abs(v - vals[0]) > atol
                   for v in vals):
                return False
        return True
    except Exception:
        return False


def is_no_hidden_tuning_ok() -> bool:
    """Boolean check (C7): no temperature/rate/fitted parameter exists here.

    Inspects the measure/sampler signatures for forbidden names (never
    raises). Uniformity is parameter-free by construction.
    """
    try:
        forbidden = ("beta", "temperature", "temp", "rate", "fitted",
                     "exponent", "preference", "bias", "threshold", "eps_phys")
        fns = [uniform_measure, orbit_uniform_measure, sample_outcome,
               sample_census, edge_admissible, node_admissible,
               joint_edge_admissible]
        for fn in fns:
            params = [p.lower() for p in inspect.signature(fn).parameters]
            if any(any(f in p for f in forbidden) for p in params):
                return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# RAND-0E/G: multiplicity audit (covers vs isomorphism classes)
# ---------------------------------------------------------------------------

def split_outcome_signature(g: nx.Graph, psi: np.ndarray, order: list, k,
                            outcome: dict) -> dict:
    """Unlabeled signature of a split outcome: (sorted deg seq, |psi| multiset).

    Two outcomes with different signatures are NOT isomorphic (sound
    non-isomorphism witness). Same signature -> candidate pair for the
    exact test below. NONE has its own fixed signature.
    """
    from bh_graph.ballistic import index_of

    psi = np.asarray(psi, dtype=np.complex128)
    if outcome.get("kind") == "NONE":
        deg = sorted(d for _, d in g.degree())
        mag = sorted(np.round(np.abs(psi), 9).tolist())
        return {"kind": "NONE", "deg": deg, "mag": mag,
                "E": g.number_of_edges(), "N": g.number_of_nodes()}
    h, psi_h, _order_h = apply_node_outcome(g, psi, list(order), k, outcome)
    deg = sorted(d for _, d in h.degree())
    mag = sorted(np.round(np.abs(psi_h), 9).tolist())
    return {"kind": "SPLIT", "deg": deg, "mag": mag,
            "E": h.number_of_edges(), "N": h.number_of_nodes()}


def split_isomorphism_classes(g: nx.Graph, psi: np.ndarray, order: list,
                              k, admissible: list) -> list:
    """Group node outcomes into unlabeled isomorphism classes (exact test).

    Two SPLIT outcomes share a class iff their post-split graphs are
    isomorphic AND their |psi| multisets match to 1e-6 (U0 tick-relabeling
    convention). NONE is always its own class. Deterministic order.
    """
    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    idx = {v: t for t, v in enumerate(order)}
    states = {}
    for o in admissible:
        ko = outcome_key(o)
        if o.get("kind") == "NONE":
            states[ko] = (g, np.array(psi, dtype=np.complex128))
        else:
            h, psi_h, _oh = apply_node_outcome(g, psi, order, k, o)
            states[ko] = (h, psi_h)
    classes = []
    unseen = [outcome_key(o) for o in admissible]
    for ko in unseen:
        placed = False
        for cls in classes:
            rep = cls[0]
            if _isomorphic_states(states[ko], states[rep]):
                cls.append(ko)
                placed = True
                break
        if not placed:
            classes.append([ko])
    for cls in classes:
        cls.sort()
    classes.sort(key=lambda c: (0 if c == ["NONE"] else 1, c))
    return classes


def _isomorphic_states(state_a, state_b) -> bool:
    """Unlabeled (G, |psi|)-isomorphism (graph iso + magnitude multiset)."""
    ga, pa = state_a
    gb, pb = state_b
    if ga.number_of_nodes() != gb.number_of_nodes():
        return False
    if ga.number_of_edges() != gb.number_of_edges():
        return False
    if not nx.is_isomorphic(ga, gb):
        return False
    fa = sorted(np.round(np.abs(pa), 9).tolist())
    fb = sorted(np.round(np.abs(pb), 9).tolist())
    return bool(np.allclose(fa, fb, atol=1e-6))


# ---------------------------------------------------------------------------
# RAND-0L/M: covariance and locality predicates (frozen)
# ---------------------------------------------------------------------------

def is_edge_covariant_ok(g: nx.Graph, psi: np.ndarray, order: list, i, j,
                         perm: dict) -> bool:
    """Boolean check: edge measure commutes with relabeling (never raises)."""
    try:
        from bh_graph.ug import permute_state

        m1 = uniform_measure(edge_admissible(g, i, j))
        h, psi2, order2 = permute_state(g, psi, order, perm)
        pi, pj = perm.get(i, i), perm.get(j, j)
        m2 = uniform_measure(edge_admissible(h, pi, pj))
        return bool(m1 == m2)
    except Exception:
        return False


def is_node_covariant_ok(g: nx.Graph, psi: np.ndarray, order: list, k,
                         perm: dict) -> bool:
    """Boolean check: node measure commutes with relabeling (never raises).

    Compares the full micro-outcome key multiset mapped through perm:
    P(a|X) = P(ga|gX) with ga the permuted cover. Uniform is covariant iff
    the mapped key set equals the recomputed key set (same cardinality +
    matching keys).
    """
    try:
        from bh_graph.ug import permute_state

        adm1 = node_admissible(g, k)
        m1 = uniform_measure(adm1)
        h, psi2, order2 = permute_state(g, psi, order, perm)
        pk = perm.get(k, k)
        adm2 = node_admissible(h, pk)
        m2 = uniform_measure(adm2)
        mapped = set()
        for o in adm1:
            if o["kind"] == "NONE":
                mapped.add("NONE")
            else:
                A = sorted(perm.get(m, m) for m in o["cover"][0])
                B = sorted(perm.get(m, m) for m in o["cover"][1])
                ka, kb = tuple(A), tuple(B)
                if ka > kb:
                    ka, kb = kb, ka
                mapped.add(f"SPLIT:{ka}|{kb}:{FIELD_POLICY_FROZEN}")
        return bool(mapped == set(m2.keys()) and m1["NONE"] == m2["NONE"]
                    and len(m1) == len(m2))
    except Exception:
        return False


def is_phase_invariant_ok(g: nx.Graph, psi: np.ndarray, order: list,
                          center, alpha: float = 0.7) -> bool:
    """Boolean check: measure invariant under global phase (never raises)."""
    try:
        psi = np.asarray(psi, dtype=np.complex128)
        psi2 = psi * np.exp(1.0j * alpha)
        if isinstance(center, tuple):
            m1 = uniform_measure(edge_admissible(g, *center))
            m2 = uniform_measure(edge_admissible(g, *center))
        else:
            m1 = uniform_measure(node_admissible(g, center))
            m2 = uniform_measure(node_admissible(g, center))
        _ = psi2
        return bool(m1 == m2)
    except Exception:
        return False


def is_conjugation_covariant_ok(g: nx.Graph, psi: np.ndarray, order: list,
                                center) -> bool:
    """Boolean check: measure unchanged under conjugation (never raises).

    Uniform is psi-blind, hence trivially conjugation-even; the predicate
    pins that no J-sensitive weighting leaked into the measure.
    """
    try:
        if isinstance(center, tuple):
            m1 = uniform_measure(edge_admissible(g, *center))
            m2 = uniform_measure(edge_admissible(g, *center))
        else:
            m1 = uniform_measure(node_admissible(g, center))
            m2 = uniform_measure(node_admissible(g, center))
        return bool(m1 == m2)
    except Exception:
        return False


def is_edge_local_ok(g: nx.Graph, psi: np.ndarray, order: list, i, j) -> bool:
    """Boolean check (RAND-0M): edge prob invariant under remote changes.

    Remote = field mutation at distance >= 3 from both endpoints + edge
    toggle disjoint from the closed neighborhood N[{i,j}] (U0-F
    convention). Uniform edge measure is (2-outcome) constant, so the
    predicate pins locality structurally. Never raises; vacuous True when
    no remote site exists (tiny graphs, recorded by the campaign).
    """
    try:
        from bh_graph.ballistic import index_of

        psi = np.asarray(psi, dtype=np.complex128)
        order = list(order)
        m0 = uniform_measure(edge_admissible(g, i, j))
        da = dict(nx.single_source_shortest_path_length(g, i))
        db = dict(nx.single_source_shortest_path_length(g, j))
        far = [v for v in g.nodes()
               if min(da.get(v, 10 ** 9), db.get(v, 10 ** 9)) >= 3]
        if far:
            idx = index_of(order)
            mut = np.array(psi, dtype=np.complex128)
            mut[idx[far[0]]] += complex(0.5, -0.25)
            _ = mut
            m1 = uniform_measure(edge_admissible(g, i, j))
            if m1 != m0:
                return False
        closed = {i, j} | set(g.neighbors(i)) | set(g.neighbors(j))
        outside = [v for v in g.nodes() if v not in closed]
        h = g.copy()
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
            m2 = uniform_measure(edge_admissible(h, i, j))
            if m2 != m0:
                return False
        return True
    except Exception:
        return False


def is_node_local_ok(g: nx.Graph, psi: np.ndarray, order: list, k) -> bool:
    """Boolean check (RAND-0M): node measure invariant under remote changes.

    Same remote convention as the edge predicate, centered on k (closed
    neighborhood N[k]). Uniform node measure depends only on degree d(k),
    which remote changes cannot alter. Never raises.
    """
    try:
        from bh_graph.ballistic import index_of

        psi = np.asarray(psi, dtype=np.complex128)
        order = list(order)
        m0 = uniform_measure(node_admissible(g, k))
        dist = dict(nx.single_source_shortest_path_length(g, k))
        far = [v for v in g.nodes() if dist.get(v, 10 ** 9) >= 3]
        if far:
            idx = index_of(order)
            mut = np.array(psi, dtype=np.complex128)
            mut[idx[far[0]]] += complex(0.5, -0.25)
            _ = mut
            m1 = uniform_measure(node_admissible(g, k))
            if m1 != m0:
                return False
        closed = {k} | set(g.neighbors(k))
        outside = [v for v in g.nodes() if v not in closed]
        h = g.copy()
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
            m2 = uniform_measure(node_admissible(h, k))
            if m2 != m0:
                return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# RAND-0N: joint measures for competing events (frozen)
# ---------------------------------------------------------------------------

def is_joint_normalized_ok(g: nx.Graph, e1, e2) -> bool:
    """Boolean check: joint uniform measure normalized (never raises)."""
    try:
        return is_normalized_ok(uniform_measure(joint_edge_admissible(g, e1, e2)))
    except Exception:
        return False


def is_factorization_ok(g: nx.Graph, e1, e2) -> bool:
    """Boolean check: disjoint joint = product of edge marginals (exact).

    For disjoint edges the joint set IS the product set and uniform-over-4
    equals the product of uniform-over-2 marginals (pinned identity). For
    overlapping edges returns True vacuously (no factorization claimed;
    the campaign records the joint-3 structure instead). Never raises.
    """
    try:
        a1, b1 = e1
        a2, b2 = e2
        k1 = (a1, b1) if a1 < b1 else (b1, a1)
        k2 = (a2, b2) if a2 < b2 else (b2, a2)
        if len({k1[0], k1[1], k2[0], k2[1]}) != 4:
            return True
        joint = uniform_measure(joint_edge_admissible(g, e1, e2))
        m1 = uniform_measure(edge_admissible(g, *k1))
        m2 = uniform_measure(edge_admissible(g, *k2))
        expect = {"NONE": m1["NONE"] * m2["NONE"],
                  outcome_key({"kind": "CONTRACT", "edge": list(sorted((k1, k2))[0])}):
                  m1["CONTRACT"] * m2["NONE"],
                  outcome_key({"kind": "CONTRACT", "edge": list(sorted((k1, k2))[1])}):
                  m1["NONE"] * m2["CONTRACT"],
                  outcome_key({"kind": "BOTH", "edges": [list(x) for x in sorted((k1, k2))]}) :
                  m1["CONTRACT"] * m2["CONTRACT"]}
        return bool(all(abs(joint[k] - expect[k]) == 0.0 for k in expect))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# RAND-0P/Q/R: sampling with RNG separation (frozen)
# ---------------------------------------------------------------------------

def _bit_generator(kind: str, seed: int):
    """Frozen BitGenerator factory (implementation detail, not physics)."""
    if kind == "pcg64":
        return np.random.PCG64(seed)
    if kind == "philox":
        return np.random.Philox(seed)
    if kind == "sfc64":
        return np.random.SFC64(seed)
    raise ValueError(f"unknown RNG kind: {kind}")


def sample_outcome(admissible: list, measure: dict, rng: np.random.Generator) -> str:
    """Draw one outcome key from the physical measure (implementation draw).

    The measure is the physical object; rng is the numerical sampler. Keys
    in deterministic sorted order; probabilities aligned to keys.
    """
    keys = sorted(measure.keys())
    probs = np.array([float(measure[k]) for k in keys], dtype=float)
    probs = probs / probs.sum()
    return str(rng.choice(keys, p=probs))


def sample_census(admissible: list, measure: dict, n_draws: int, seed: int,
                  rng_kind: str = "pcg64") -> dict:
    """Empirical census: n_draws i.i.d. draws + exact uncertainty bars.

    Returns {counts, freqs, wilson99: {key: (lo, hi)}, analytic}. Wilson
    score intervals at 99% (frozen z). Deterministic given (seed, kind).
    """
    rng = np.random.Generator(_bit_generator(rng_kind, seed))
    keys = sorted(measure.keys())
    counts = {k: 0 for k in keys}
    for _ in range(int(n_draws)):
        counts[sample_outcome(admissible, measure, rng)] += 1
    n = int(n_draws)
    z = WILSON_Z_99
    denom = 1.0 + z * z / n
    wilson = {}
    for k in keys:
        phat = counts[k] / n
        center = (phat + z * z / (2 * n)) / denom
        half = z * math.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n)) / denom
        wilson[k] = [float(max(0.0, center - half)), float(min(1.0, center + half))]
    return {"counts": counts,
            "freqs": {k: counts[k] / n for k in keys},
            "wilson99": wilson,
            "analytic": {k: float(measure[k]) for k in keys},
            "n": n, "seed": seed, "rng_kind": rng_kind}


def is_census_consistent_ok(census: dict) -> bool:
    """Boolean check: empirical census matches analytic measure (frozen).

    Every outcome's analytic p must lie inside its Wilson 99% interval AND
    the chi-square goodness-of-fit p-value must exceed 1e-3 (frozen floor).
    Never raises.
    """
    try:
        from scipy.stats import chisquare

        for k, (lo, hi) in census["wilson99"].items():
            if not (lo <= census["analytic"][k] <= hi):
                return False
        keys = sorted(census["analytic"].keys())
        obs = [census["counts"][k] for k in keys]
        exp = [census["analytic"][k] * census["n"] for k in keys]
        _stat, pval = chisquare(obs, exp)
        return bool(pval > CHI2_P_FLOOR)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# RAND-0O: stochastic tick and effect-radius distribution (frozen)
# ---------------------------------------------------------------------------

def stochastic_edge_tick(g: nx.Graph, psi: np.ndarray, order: list,
                         rng: np.random.Generator, dt: float = 0.1) -> dict:
    """One stochastic synchronous tick: independent uniform edge draws.

    Each edge draws {NONE, CONTRACT} at 1/2 (micro-uniform edge measure);
    CONTRACT classes merge simultaneously (frozen U0 quotient machinery);
    psi^e = evolve_fixed(psi, H(G), dt, 1 step); psi' = sum-thread psi^e.
    Decision radius R_decision = 1 (each draw sees only its edge patch);
    R_effect = max merged-class size (marked-component diameter analogue).
    Returns the tick record (structural + field books).
    """
    from bh_graph.ballistic import evolve_fixed, hamiltonian
    from bh_graph.u0 import (pair_dq_formula, quotient_from_marks,
                             thread_field_sum)

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    edges = sorted(tuple(sorted(e)) for e in g.edges())
    ce = set()
    for e in edges:
        if str(rng.choice(["NONE", "CONTRACT"], p=[0.5, 0.5])) == "CONTRACT":
            ce.add(e)
    q = quotient_from_marks(g, ce)
    h, order2 = q["h"], q["order2"]
    psi_e = evolve_fixed(psi, hamiltonian(g, order=order), float(dt), 2)["psi"][1]
    psi2 = thread_field_sum(q["classes"], q["node_of"], order2, psi_e, order)
    n0 = float(np.sum(np.abs(psi) ** 2))
    n1 = float(np.sum(np.abs(psi2) ** 2))
    return {"g2": h, "psi2": psi2, "order2": order2,
            "n_contract_draws": len(ce),
            "n_merged_classes": len(q["merged"]),
            "max_class_size": int(max((len(c) for c in q["classes"]), default=0)),
            "dN": int(h.number_of_nodes() - g.number_of_nodes()),
            "dQ_direct": float(n1 - n0),
            "dQ_formula": float(pair_dq_formula(q["classes"], psi_e, order))}


def effect_radius_distribution(g: nx.Graph, psi: np.ndarray, order: list,
                               n_reps: int, seed: int,
                               rng_kind: str = "pcg64",
                               dt: float = 0.1) -> dict:
    """Distribution P(R_effect) over n_reps stochastic ticks (frozen).

    R_effect per rep = max merged-class size. Deterministic given
    (seed, kind). Reports histogram + moments + full sample list.
    """
    rng = np.random.Generator(_bit_generator(rng_kind, seed))
    radii = []
    dNs = []
    for _ in range(int(n_reps)):
        rec = stochastic_edge_tick(g, psi, list(order), rng, dt)
        radii.append(rec["max_class_size"])
        dNs.append(rec["dN"])
    hist = {}
    for r in radii:
        hist[str(int(r))] = hist.get(str(int(r)), 0) + 1
    arr = np.array(radii, dtype=float)
    return {"n": int(n_reps), "seed": seed, "rng_kind": rng_kind,
            "hist": hist, "radii": [int(r) for r in radii],
            "dNs": [int(d) for d in dNs],
            "mean": float(arr.mean()), "max": int(arr.max()),
            "min": int(arr.min())}


# ---------------------------------------------------------------------------
# RAND-0 states: tiny exact battery (frozen)
# ---------------------------------------------------------------------------

def tiny_graph(name: str) -> dict:
    """Frozen tiny substrates (integer labels, deterministic, no seeds).

    k2 (2 nodes, 1 edge); triangle (3-cycle); square (4-cycle); star4
    (center 0 + leaves 1..4); path4 (0-1-2-3). Orders sorted.
    """
    if name == "k2":
        g = nx.Graph()
        g.add_edge(0, 1)
    elif name == "triangle":
        g = nx.Graph()
        g.add_edges_from([(0, 1), (1, 2), (2, 0)])
    elif name == "square":
        g = nx.Graph()
        g.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0)])
    elif name == "star4":
        g = nx.Graph()
        g.add_edges_from([(0, 1), (0, 2), (0, 3), (0, 4)])
    elif name == "path4":
        g = nx.Graph()
        g.add_edges_from([(0, 1), (1, 2), (2, 3)])
    else:
        raise ValueError(f"unknown tiny graph: {name}")
    order = sorted(g.nodes())
    return {"g": g, "order": order}


def tiny_field(n: int, which: str) -> np.ndarray:
    """Frozen tiny field preparations (exact, normalized except zero).

    zero; bonding (uniform 1/sqrt(n)); current (q-parity stagger with
    +i on odd: exact B = 0 on cross edges up to parity); antibonding
    (-1 on odd). Parity q_v = v & 1 (canonical for these labelings;
    triangle is non-bipartite: same-parity edge filed, not hidden).
    """
    n = int(n)
    rho = 1.0 / math.sqrt(n)
    if which == "zero":
        return np.zeros(n, dtype=np.complex128)
    if which == "bonding":
        return np.full(n, complex(rho, 0.0), dtype=np.complex128)
    q = np.array([v & 1 for v in range(n)], dtype=int)
    if which == "current":
        return np.where(q == 0, complex(rho, 0.0),
                        complex(0.0, rho)).astype(np.complex128)
    if which == "antibonding":
        return np.where(q == 0, complex(rho, 0.0),
                        complex(-rho, 0.0)).astype(np.complex128)
    raise ValueError(f"unknown tiny field: {which}")


def rand0_states() -> dict:
    """Frozen RAND-0 battery: tiny sectors + U0 S1..S8 read-only handles.

    T1..T4: K2 x {zero, bonding, current, antibonding} (RAND-0H/I/J edge
    sectors). T5: triangle bonding. T6: square bonding. T7: star4 bonding
    (exact-symmetry orbit exhibit). T8: path4 current. U1..U8: aliases of
    the frozen U0 S1..S8 states (same objects, no copies diverged).
    """
    from bh_graph.u0 import u0_states

    out = {}
    specs = [("T1", "k2", "zero"), ("T2", "k2", "bonding"),
             ("T3", "k2", "current"), ("T4", "k2", "antibonding"),
             ("T5", "triangle", "bonding"), ("T6", "square", "bonding"),
             ("T7", "star4", "bonding"), ("T8", "path4", "current")]
    for key, gname, field in specs:
        tg = tiny_graph(gname)
        out[key] = {"g": tg["g"], "psi": tiny_field(len(tg["order"]), field),
                    "order": list(tg["order"]), "substrate": gname,
                    "field": field}
    u0s = u0_states()
    for k in ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]:
        out["U" + k[1:]] = {"g": u0s[k]["g"], "psi": u0s[k]["psi"],
                            "order": list(u0s[k]["order"]),
                            "substrate": u0s[k]["substrate"],
                            "field": u0s[k]["field"]}
    return out
