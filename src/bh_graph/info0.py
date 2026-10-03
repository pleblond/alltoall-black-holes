"""INFO-0 structural branching and information accounting (FROZEN pre-data).

Campaign: INFO-0. Quantifies, WITHOUT probabilities, information lost by
contraction and information required to specify reverse splits and
histories. Consumes BR-2.5, RAND-0, SYM-0, TIME-0 and MEASURE0-DEBT
read-only (never re-derived, never modified).

Frozen ontology (read-only consumption):
  - X = (G, psi), simple graphs, H = -A, J = 1, hbar = 1, dt = 0.1 (P1).
  - X_phys = X / (R x U1): node relabelings + global phase (SYM0-CLOSED).
  - Contraction (u,v) -> k, sum map psi_k = psi_i + psi_j (BR-2.5);
    record-free splits degenerate (3^d directed, (3^d+1)/2 undirected).
  - Admissible sets: edge {NONE, CONTRACT}, node {NONE} + undirected
    covers x equal-halves (RAND-0A); stabilizer/orbit/iso apparatus
    (RAND-0B/E); five-grain recount (SYM-0V).
  - Histories: TIME-0 canonical (N = 1..6, 143 classes) + labeled (N <= 4,
    44 states) exact walks, timed vs skeleton (waiting placements).
  - Physical quotient: MEASURE-0 state_signature + signature_key,
    physical_admissible_edge/node, transition-graph apparatus (DEBT:
    no unique weighting is forced; this campaign uses COUNTS only).
  - Hidden sector: HIDDEN0-SEPARATED matched pairs (P_+ equal, P_-
    differ) are physically distinct; signatures must retain them.

Branch counts (combinatorial labeling, NOT Shannon entropy):
  n(X) = |A_phys(X)|, I_branch(X) = log2 n(X).
Contraction loss:
  (psi_i, psi_j) -> s = psi_i + psi_j; lost relative mode
  d = psi_i - psi_j, psi_i = (s+d)/2, psi_j = (s-d)/2.
  Discrete partition loss (finite bits) and continuous field loss
  (fiber dims + error power) are quantified SEPARATELY.
Reverse/history multiplicity:
  P(X) physical predecessor sets, I_pred = log2 |P(X)|;
  TIME-0 exact histories N_hist, I_hist = log2 N_hist;
  waiting placements (binomial) separated from structural skeletons.
Scheduler multiplicity (waiting placements + sync-vs-sequential orders)
  is quantified SEPARATELY (never folded into structural counts).

Epistemic firewall (frozen): NO -sum p log p anywhere in this module.
MEASURE0-DEBT means probabilities are not earned; only counts and their
binary logs appear. No temperature, Boltzmann factors, Born rule, action,
entropy maximization, fitted rates, or tuned weights. Forbidden forms
appear ONLY in the firewall audit as negative patterns (never evaluated).

This module introduces NO dynamics, NO firing law, NO measure, NO rate,
NO threshold, NO fitted constant. Tolerances below are numerical
identities (exact counting / 1e-12 algebra / 1e-9 Krylov), never physics.
"""

from __future__ import annotations

import inspect
import itertools
import math

import networkx as nx
import numpy as np

# Frozen battery + grids (INFO0-PREREG, pre-data).
TINY_GRAPHS = ("k2", "triangle", "square", "star4", "path4")
TINY_FIELDS = ("zero", "bonding", "current", "antibonding")
T_GRID_CANONICAL = (2, 3, 4, 5, 6)
T_GRID_LABELED = (2, 3)
N_MIN = 1
N_MAX = 6
N_MAX_LABELED = 4
N_EXACT_MAX = 5  # N <= 5: no N7 truncation for 1-step pred/succ (filed).
FP_ATOL = 1e-12
KRYLOV_ATOL = 1e-9
HIDDEN_L = 4
HIDDEN_PHASE = math.pi / 2.0
HIDDEN_AMP = 2.0

KIND_IDENTITY = "I"


# ---------------------------------------------------------------------------
# A0: binary log of counts (no probabilities)
# ---------------------------------------------------------------------------

def log2count(n: int) -> float | None:
    """Binary log of a finite count (None for n <= 0: empty set, no log).

    n = 1 -> 0.0 bits (one label needs no bits). Never raises for ints.
    """
    try:
        n = int(n)
    except Exception:
        return None
    if n <= 0:
        return None
    if n == 1:
        return 0.0
    return float(math.log2(n))


def is_log2count_ok(n: int, expect) -> bool:
    """Boolean check: log2count(n) equals expect (None-aware, never raises)."""
    try:
        got = log2count(n)
        if expect is None:
            return got is None
        if got is None:
            return False
        return bool(abs(got - float(expect)) <= 1e-12)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# A: physical grain + branch counts
# ---------------------------------------------------------------------------

def info0_states() -> dict:
    """Frozen INFO-0 tiny battery: 5 graphs x 4 fields (20 states).

    Same objects as RAND-0 T1..T8 subset + MEASURE-0 tiny battery
    (reconstructed via the same frozen factories, read-only).
    """
    from bh_graph.measure0 import tiny_state

    out = {}
    for gn in TINY_GRAPHS:
        for fn in TINY_FIELDS:
            out[f"{gn}/{fn}"] = tiny_state(gn, fn)
    return out


def branch_patch_edge(g: nx.Graph, psi: np.ndarray, order: list, i, j) -> dict:
    """Edge-patch branch counts: raw 2 vs physical classes (quotiented).

    n_raw = 2 ({NONE, CONTRACT}); n_phys = #signature classes (N differs,
    so 2; recorded explicitly, never assumed). I = log2 n.
    """
    from bh_graph.measure0 import physical_admissible_edge

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    a = physical_admissible_edge(g, psi, order, i, j)
    n_raw = len(a["outcomes"])
    n_phys = int(a["n_phys"])
    return {
        "patch": ["edge", i, j],
        "n_raw": int(n_raw),
        "n_phys": n_phys,
        "I_raw": log2count(n_raw),
        "I_phys": log2count(n_phys),
        "class_sizes": sorted(len(v) for v in a["classes"].values()),
    }


def branch_patch_node(g: nx.Graph, psi: np.ndarray, order: list, k) -> dict:
    """Node-patch branch counts: raw/directed/phys/iso/orbit grains.

    n_raw = 1 + (3^d+1)/2 (undirected + NONE); n_directed = 1 + 3^d;
    n_phys = #signature classes (MEASURE-0 quotient); n_iso = #unlabeled
    (G,|psi|) classes (RAND-0F, capped for N > 12); n_orbits = #stabilizer
    orbits (RAND-0B, capped for patch > 8). I = log2 n per grain.
    Red-quotient = undirected (phase+relabel act trivially on the frozen
    structural set: verified by SYM-0V, recorded here as n_red).
    """
    from bh_graph.measure0 import physical_admissible_node
    from bh_graph.rand0 import (directed_node_admissible, local_stabilizer,
                                node_admissible, orbits_of,
                                split_isomorphism_classes)

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    d = int(g.degree(k))
    adm = node_admissible(g, k)
    dadm = directed_node_admissible(g, k)
    phys = physical_admissible_node(g, psi, order, k)
    n_raw = len(adm)
    n_directed = len(dadm)
    n_phys = int(phys["n_phys"])
    rec: dict = {
        "patch": ["node", k],
        "d": d,
        "n_raw": int(n_raw),
        "n_directed": int(n_directed),
        "n_phys": n_phys,
        "n_red": int(n_raw),
        "I_raw": log2count(n_raw),
        "I_directed": log2count(n_directed),
        "I_phys": log2count(n_phys),
        "I_red": log2count(n_raw),
    }
    if g.number_of_nodes() <= 12:
        try:
            classes = split_isomorphism_classes(g, psi, order, k, adm)
            rec["iso_capped"] = False
            rec["n_iso"] = len(classes)
            rec["I_iso"] = log2count(len(classes))
            rec["iso_sizes"] = sorted(len(c) for c in classes)
        except Exception:
            rec["iso_capped"] = True
            rec["n_iso"] = None
            rec["I_iso"] = None
    else:
        rec["iso_capped"] = True
        rec["n_iso"] = None
        rec["I_iso"] = None
    try:
        stab = local_stabilizer(g, psi, order, k)
        orbs = orbits_of(adm, stab, "node")
        rec["stab_capped"] = False
        rec["n_orbits"] = len(orbs)
        rec["I_orbits"] = log2count(len(orbs))
        rec["orbit_sizes"] = sorted(len(o) for o in orbs)
        rec["stab_order"] = len(stab)
    except ValueError:
        rec["stab_capped"] = True
        rec["n_orbits"] = None
        rec["I_orbits"] = None
        rec["stab_order"] = None
    except Exception:
        rec["stab_capped"] = True
        rec["n_orbits"] = None
        rec["I_orbits"] = None
        rec["stab_order"] = None
    return rec


def is_branch_rep_independent_ok(g: nx.Graph, psi: np.ndarray, order: list,
                                 patch) -> bool:
    """Boolean check: A_phys identical under R x U1 (MEASURE-0 gate, reused).

    patch is ("edge", i, j) or ("node", k). Never raises.
    """
    try:
        from bh_graph.measure0 import is_representation_independent_ok

        return bool(is_representation_independent_ok(g, psi, order, patch))
    except Exception:
        return False


def global_single_step(g: nx.Graph, psi: np.ndarray, order: list) -> dict:
    """Global one-event successors: one C/S anywhere + NONE (sequential).

    Enumerates every single-edge contraction outcome + every single-node
    split outcome (all undirected covers x equal-halves) + the stay.
    Groups by physical signature: n_raw_single vs n_phys_single.
    Structural-only + frozen field maps (no evolution: branching isolated
    from the deterministic U step, filed openly).
    """
    from bh_graph.measure0 import signature_key, state_signature
    from bh_graph.rand0 import (apply_edge_outcome, apply_node_outcome,
                                node_admissible)

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    sigs: list = []
    sigs.append(signature_key(state_signature(g, psi, order)))
    n_raw = 1
    for (i, j) in sorted(tuple(sorted(e)) for e in g.edges()):
        g2, psi2, order2 = apply_edge_outcome(g, psi, order, i, j, "CONTRACT")
        sigs.append(signature_key(state_signature(g2, psi2, order2)))
        n_raw += 1
    for k in sorted(g.nodes()):
        for o in node_admissible(g, k):
            if o.get("kind") == "NONE":
                continue
            h, psi_h, order_h = apply_node_outcome(g, psi, order, k, o)
            sigs.append(signature_key(state_signature(h, psi_h, order_h)))
            n_raw += 1
    n_phys = len(set(sigs))
    return {
        "n_raw_single": int(n_raw),
        "n_phys_single": int(n_phys),
        "I_raw_single": log2count(n_raw),
        "I_phys_single": log2count(n_phys),
    }


def global_sync_outcomes(g: nx.Graph, psi: np.ndarray, order: list,
                         dt: float = 0.0) -> dict:
    """Global synchronous successors: all 2^E marked subsets (U0 quotient).

    Each subset merges simultaneously (quotient graph + sum-threaded field;
    dt = 0 headline: psi_e = psi, structural branching isolated from the
    deterministic evolution step). Groups by physical signature:
    n_sync_raw = 2^E, n_sync_phys = #distinct signatures,
    I_sync_raw = E bits exactly, I_sync_phys = log2 n_phys.
    Returns per-subset signatures + class grouping (deterministic order).
    """
    from bh_graph.ballistic import evolve_fixed, hamiltonian
    from bh_graph.measure0 import signature_key, state_signature
    from bh_graph.u0 import quotient_from_marks, thread_field_sum

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    edges = sorted(tuple(sorted(e)) for e in g.edges())
    E = len(edges)
    if dt == 0.0:
        psi_e = np.array(psi, dtype=np.complex128)
    else:
        psi_e = np.asarray(
            evolve_fixed(psi, hamiltonian(g, order=order), float(dt), 2)["psi"][1],
            dtype=np.complex128)
    subsets: list = []
    for mask in range(1 << E):
        ce = {edges[t] for t in range(E) if mask & (1 << t)}
        q = quotient_from_marks(g, ce)
        h, order2 = q["h"], q["order2"]
        psi2 = thread_field_sum(q["classes"], q["node_of"], order2, psi_e, order)
        key = signature_key(state_signature(h, psi2, order2))
        subsets.append({"mask": int(mask),
                        "edges": sorted([list(e) for e in ce]),
                        "sig": key,
                        "N2": int(h.number_of_nodes()),
                        "E2": int(h.number_of_edges())})
    classes: dict = {}
    for s in subsets:
        classes.setdefault(s["sig"], []).append(s["mask"])
    n_raw = 1 << E
    n_phys = len(classes)
    return {
        "E": int(E),
        "n_sync_raw": int(n_raw),
        "n_sync_phys": int(n_phys),
        "I_sync_raw": log2count(n_raw),
        "I_sync_phys": log2count(n_phys),
        "subsets": subsets,
        "class_sizes": sorted(len(v) for v in classes.values()),
    }


# ---------------------------------------------------------------------------
# B: contraction loss (discrete partition + continuous field, separately)
# ---------------------------------------------------------------------------

def discrete_loss_bits(d: int) -> dict:
    """Discrete partition loss for a contracted node of degree d.

    n_covers_undirected = (3^d + 1)/2 (U0-H1 gauge quotient);
    I_graph_lost = log2 n. Exact counting (no probabilities).
    """
    from bh_graph.accounting import info_loss_bits

    info = info_loss_bits(int(d))
    n = int(round(info["n_covers_undirected"]))
    return {
        "d": int(d),
        "n_covers_directed": int(info["n_covers_directed"]),
        "n_covers_undirected": n,
        "I_graph_lost": log2count(n),
        "field_real_dims_lost": int(info["field_real_dims_lost"]),
    }


def field_loss(a: complex, b: complex) -> dict:
    """Continuous field fiber of one contraction: s kept, d lost.

    s = a + b (retained sum), d = a - b (lost relative mode);
    inversion a = (s+d)/2, b = (s-d)/2; equal-split error |d|^2/2;
    B = (|s|^2 - |d|^2)/4 (needs |d|: not recoverable from s alone);
    dQ = +2B (sum-map norm change); fiber 1 complex = 2 real dims.
    """
    a = complex(a)
    b = complex(b)
    s = a + b
    d = a - b
    bb = float(np.real(np.conj(a) * b))
    return {
        "s": complex(s),
        "d": complex(d),
        "a_rec": complex((s + d) / 2.0),
        "b_rec": complex((s - d) / 2.0),
        "error_equal": float(abs(d) ** 2 / 2.0),
        "B": float(bb),
        "B_from_sd": float((abs(s) ** 2 - abs(d) ** 2) / 4.0),
        "dQ": float(2.0 * bb),
        "fiber_dim_C": 1,
        "fiber_dim_R": 2,
    }


def field_split(s: complex, d: complex) -> tuple:
    """Exact inversion: (s, d) -> (a, b) = ((s+d)/2, (s-d)/2)."""
    s = complex(s)
    d = complex(d)
    return ((s + d) / 2.0, (s - d) / 2.0)


def is_contraction_inversion_ok(a: complex, b: complex,
                                atol: float = FP_ATOL) -> bool:
    """Boolean check: field_split(field_loss(a,b)) recovers (a,b)."""
    try:
        rec = field_loss(a, b)
        p, q = field_split(rec["s"], rec["d"])
        return bool(abs(p - complex(a)) <= atol and abs(q - complex(b)) <= atol)
    except Exception:
        return False


def is_error_formula_ok(a: complex, b: complex,
                        atol: float = FP_ATOL) -> bool:
    """Boolean check: equal-split roundtrip error equals |a-b|^2/2."""
    try:
        from bh_graph.contraction import roundtrip_field_error

        got = float(roundtrip_field_error(a, b, "sum", "equal")["error"])
        want = float(abs(complex(a) - complex(b)) ** 2 / 2.0)
        formula = roundtrip_field_error(a, b, "sum", "equal")["formula"]
        return bool(abs(got - want) <= atol and abs(float(formula) - want) <= atol)
    except Exception:
        return False


def is_b_from_sd_ok(a: complex, b: complex, atol: float = FP_ATOL) -> bool:
    """Boolean check: B = (|s|^2 - |d|^2)/4 exactly."""
    try:
        rec = field_loss(a, b)
        return bool(abs(rec["B"] - rec["B_from_sd"]) <= atol)
    except Exception:
        return False


def contraction_loss_event(g: nx.Graph, psi: np.ndarray, order: list,
                           i, j) -> dict:
    """Full per-event loss books: discrete partitions + continuous fiber.

    Contracts (i, j) via the frozen BR-2.5 sum map; reports daughter
    degree d_k, discrete n_covers/I_graph_lost, field (s, d, error, B),
    dQ direct vs formula, and the graph-reverse pin (original partition
    among covers of N(k)).

    Implementation (INFO0-AMENDMENT-2): reverse checks are DIRECT (O(d),
    no enumeration), exact for every degree. Graph-reverse holds by
    BR-2.5 construction (N(k) = N(i) u N(j)); verified explicitly via
    set equality, never via 3^d enumeration (which blows up for J2
    daughters with d_k ~ 14: 3^14 covers). Full-reverse (signature
    match under frozen equal-halves) holds iff the halves condition
    a == b holds (exact complex equality) given graph-reverse: |psi|
    multisets match iff {|a|,|b|} == {|s|/2,|s|/2}, which forces a == b
    (triangle-equality rigidity); verified against MEASURE-0 enumeration
    on the tiny battery (reversible == halves, 33/60 banked). No
    enumeration anywhere here; tiny-vs-J2 identical code path.
    """
    from bh_graph.contraction import contracted_state

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    idx = {v: t for t, v in enumerate(order)}
    a = complex(psi[idx[i]])
    b = complex(psi[idx[j]])
    g2, psi2, order2, k, rec = contracted_state(g, psi, order, i, j, "sum")
    d_k = int(g2.degree(k))
    disc = discrete_loss_bits(d_k)
    fld = field_loss(a, b)
    n0 = float(np.sum(np.abs(psi) ** 2))
    n1 = float(np.sum(np.abs(psi2) ** 2))
    # Direct reverse checks (no enumeration; exact for all d).
    nbrs_i = set(g.neighbors(i)) - {j}
    nbrs_j = set(g.neighbors(j)) - {i}
    nk = set(g2.neighbors(k))
    part_found = bool((nbrs_i | nbrs_j) == nk)
    graph_reverse = bool(part_found)
    halves = bool(a == b)
    full_reverse = bool(graph_reverse and halves)
    return {
        "edge": [i, j],
        "k": k,
        "d_k": d_k,
        "n_covers_undirected": disc["n_covers_undirected"],
        "I_graph_lost": disc["I_graph_lost"],
        "s": [float(fld["s"].real), float(fld["s"].imag)],
        "d": [float(fld["d"].real), float(fld["d"].imag)],
        "error_equal": fld["error_equal"],
        "B": fld["B"],
        "B_from_sd": fld["B_from_sd"],
        "dQ_direct": float(n1 - n0),
        "dQ_formula": fld["dQ"],
        "fiber_dim_R": 2,
        "graph_reverse": bool(graph_reverse),
        "full_reverse": bool(full_reverse),
        "halves_condition": bool(halves),
        "partition_found": bool(part_found),
    }


# ---------------------------------------------------------------------------
# C: physical predecessor sets
# ---------------------------------------------------------------------------

def successors_of(adj: dict, node) -> list:
    """Sorted (succ, kind) pairs (adj values are (succ, kind) lists)."""
    return list(adj.get(node, []))


def predecessors_of(adj: dict, node) -> list:
    """All (pred, kind) with pred -> node (exact reverse lookup)."""
    out = []
    for pred, succs in adj.items():
        for s2, kind in succs:
            if s2 == node:
                out.append((pred, kind))
    out.sort(key=str)
    return out


def predecessor_record(adj: dict, node) -> dict:
    """One-step predecessor/successor books for a history-graph node.

    Structural (C/S, excludes identity waits) and total (includes waits)
    reported separately. Kinds: C = contraction step (N-1), S = split
    step (N+1), I = identity wait (same class). Field fibers filed:
    C-predecessors (larger Y) carry a 1-complex-dim field fiber (d free);
    S/I-predecessors carry determined fields (0 dims). At V0 (psi = 0)
    the fiber collapses to the single zero point (exact finite counts).
    """
    succs = successors_of(adj, node)
    preds = predecessors_of(adj, node)
    succ_struct = [(s, k) for s, k in succs if k != KIND_IDENTITY]
    pred_struct = [(p, k) for p, k in preds if k != KIND_IDENTITY]
    # Fiber dims per predecessor kind (frozen field relations, TIME-0):
    # Y -C-> X (Y larger): X_k = a+b, (a,b) fiber 1-dim (d free).
    # Y -S-> X (Y smaller): Y_k = a+b determined, 0 dims.
    # Y -I-> X (Y = X): psi_X = U psi_Y determined (unitary), 0 dims.
    n_pred_C = sum(1 for _, k in pred_struct if k == "C")
    n_pred_S = sum(1 for _, k in pred_struct if k == "S")
    out = {
        "n_succ_total": len(succs),
        "n_succ_struct": len(succ_struct),
        "n_pred_total": len(preds),
        "n_pred_struct": len(pred_struct),
        "n_pred_C": int(n_pred_C),
        "n_pred_S": int(n_pred_S),
        "I_succ_total": log2count(len(succs)),
        "I_succ_struct": log2count(len(succ_struct)),
        "I_pred_total": log2count(len(preds)),
        "I_pred_struct": log2count(len(pred_struct)),
        "succ_set": sorted(str(s) for s, _ in succs),
        "pred_set": sorted(str(p) for p, _ in preds),
        "succ_struct_set": sorted(str(s) for s, _ in succ_struct),
        "pred_struct_set": sorted(str(p) for p, _ in pred_struct),
        "sets_equal_total": bool(sorted(str(s) for s, _ in succs)
                                 == sorted(str(p) for p, _ in preds)),
        "sets_equal_struct": bool(sorted(str(s) for s, _ in succ_struct)
                                  == sorted(str(p) for p, _ in pred_struct)),
        "fiber_infinite": bool(n_pred_C > 0),
    }
    return out


def predecessor_census(adj: dict, nodes: list) -> dict:
    """Predecessor census over a history-graph node set (exact).

    Reports per-node records + aggregates: equality fractions
    (pred_set == succ_set, total + structural), I distributions,
    fiber flags (any C-predecessor => infinite field fiber at psi != 0,
    single zero point at V0).
    """
    recs = {}
    for v in nodes:
        recs[str(v)] = predecessor_record(adj, v)
    n = len(recs)
    n_eq_total = sum(1 for r in recs.values() if r["sets_equal_total"])
    n_eq_struct = sum(1 for r in recs.values() if r["sets_equal_struct"])
    n_fiber = sum(1 for r in recs.values() if r["fiber_infinite"])
    return {
        "n": int(n),
        "n_equal_total": int(n_eq_total),
        "n_equal_struct": int(n_eq_struct),
        "f_equal_total": float(n_eq_total / n) if n else 0.0,
        "f_equal_struct": float(n_eq_struct / n) if n else 0.0,
        "n_fiber_infinite": int(n_fiber),
        "records": recs,
    }


# ---------------------------------------------------------------------------
# D: history multiplicity (timed vs skeleton vs waiting)
# ---------------------------------------------------------------------------

def waiting_placements(T: int, L: int) -> dict:
    """Waiting placements: C(T, L) ways to place L structural steps in T.

    I_wait_place(L) = log2 C(T, L). Exact integers (no probabilities).
    """
    from math import comb

    T, L = int(T), int(L)
    if L < 0 or L > T:
        return {"T": T, "L": L, "C": 0, "I_wait_place": None}
    c = int(comb(T, L))
    return {"T": T, "L": L, "C": c, "I_wait_place": log2count(c)}


def skeleton_lengths(adj: dict, starts: list, T: int) -> list:
    """Per-length no-wait walk matrices S_L(a, b) for L = 0..T (exact).

    S_0 = identity (a == b); S_L for L >= 1 via count_matrix on the
    identity-stripped adjacency. Bigints, never sampled.
    """
    from bh_graph.time0 import count_matrix, nowait_adjacency

    T = int(T)
    noloop = nowait_adjacency(adj)
    mats = []
    for L in range(T + 1):
        if L == 0:
            mats.append({(a, b): (1 if a == b else 0)
                         for a in starts for b in starts})
        else:
            mats.append(count_matrix(noloop, list(starts), L))
    return mats


def history_pair_decomposition(adj: dict, a, b, T: int,
                               mats=None) -> dict:
    """Timed-vs-skeleton decomposition for one boundary pair (exact).

    N_timed(a, b, T) = #length-T walks (with waits);
    S_L(a, b) = #no-wait walks of length L (L = 0..T);
    identity: N_timed = sum_L C(T, L) S_L (pinned, not assumed).
    N_skel = sum_L S_L; I_hist = log2 N_timed; I_skel = log2 N_skel;
    I_wait = log2(N_timed / N_skel) when both > 0 (average waiting
    multiplicity per skeleton; None for incompatible pairs).
    """
    from math import comb

    from bh_graph.time0 import count_walks_from

    T = int(T)
    if mats is None:
        mats = skeleton_lengths(adj, [a, b], T)
    n_timed = int(count_walks_from(adj, a, T).get(b, 0))
    s_vec = [int(mats[L].get((a, b), 0)) for L in range(T + 1)]
    n_skel = int(sum(s_vec))
    expect = int(sum(int(comb(T, L)) * s_vec[L] for L in range(T + 1)))
    i_hist = log2count(n_timed)
    i_skel = log2count(n_skel)
    if n_timed > 0 and n_skel > 0:
        ratio = n_timed / n_skel
        i_wait = float(math.log2(ratio)) if ratio > 0 else None
    else:
        i_wait = None
    return {
        "T": T,
        "N_timed": n_timed,
        "N_skel": n_skel,
        "S_vec": s_vec,
        "expect_timed": expect,
        "identity_ok": bool(n_timed == expect),
        "I_hist": i_hist,
        "I_skel": i_skel,
        "I_wait": i_wait,
    }


def history_decomposition(adj: dict, starts: list, T: int) -> dict:
    """Full (a, b) timed-vs-skeleton census at depth T (exact).

    Aggregates: compatibility, uniqueness (timed + skeleton), median/max
    N/I, waiting-factor distribution, identity verification on every
    pair (all must hold: combinatorial theorem, apparatus gate).
    """
    from bh_graph.time0 import count_matrix

    T = int(T)
    mats = skeleton_lengths(adj, list(starts), T)
    timed = count_matrix(adj, list(starts), T)
    n_pairs = len(starts) * len(starts)
    n_compat = 0
    n_uniq = 0
    n_skel_compat = 0
    n_skel_uniq = 0
    n_identity_fail = 0
    comp_timed: list = []
    comp_skel: list = []
    wait_ratios: list = []
    max_timed = 0
    max_skel = 0
    for a in starts:
        for b in starts:
            s_vec = [int(mats[L].get((a, b), 0)) for L in range(T + 1)]
            n_skel = int(sum(s_vec))
            n_timed = int(timed.get((a, b), 0))
            from math import comb

            expect = int(sum(int(comb(T, L)) * s_vec[L] for L in range(T + 1)))
            if n_timed != expect:
                n_identity_fail += 1
            if n_timed > 0:
                n_compat += 1
                comp_timed.append(n_timed)
                max_timed = max(max_timed, n_timed)
                if n_timed == 1:
                    n_uniq += 1
            if n_skel > 0:
                n_skel_compat += 1
                comp_skel.append(n_skel)
                max_skel = max(max_skel, n_skel)
                if n_skel == 1:
                    n_skel_uniq += 1
            if n_timed > 0 and n_skel > 0:
                wait_ratios.append(n_timed / n_skel)

    def _med(xs):
        if not xs:
            return 0.0
        s = sorted(xs)
        m = len(s)
        return float(s[m // 2] if m % 2 else (s[m // 2 - 1] + s[m // 2]) / 2)

    med_t = _med(comp_timed)
    med_s = _med(comp_skel)
    med_w = _med(wait_ratios)
    return {
        "T": T,
        "n_pairs": int(n_pairs),
        "n_compatible": int(n_compat),
        "f_compatible": float(n_compat / n_pairs) if n_pairs else 0.0,
        "f_unique": float(n_uniq / n_compat) if n_compat else 0.0,
        "median_nhist": float(med_t),
        "max_nhist": int(max_timed),
        "I_hist_median": (float(math.log2(med_t)) if med_t > 0 else None),
        "I_hist_max": log2count(max_timed),
        "n_skel_compatible": int(n_skel_compat),
        "f_unique_skel": float(n_skel_uniq / n_skel_compat) if n_skel_compat else 0.0,
        "median_nskel": float(med_s),
        "max_nskel": int(max_skel),
        "I_skel_median": (float(math.log2(med_s)) if med_s > 0 else None),
        "I_skel_max": log2count(max_skel),
        "median_wait_ratio": float(med_w),
        "I_wait_median": (float(math.log2(med_w)) if med_w > 0 else None),
        "n_identity_fail": int(n_identity_fail),
        "identity_ok": bool(n_identity_fail == 0),
    }


# ---------------------------------------------------------------------------
# E: scheduler multiplicity (waiting placements + sync-vs-sequential)
# ---------------------------------------------------------------------------

def sequential_orders_for_subset(g: nx.Graph, psi: np.ndarray, order: list,
                                 subset) -> dict:
    """Sequential contraction orders realizing one synchronous marked set.

    subset: iterable of sorted edges (marked for contraction). Enumerates
    all m! permutations (m = |subset|); each order is simulated as m
    sequential single-edge BR-2.5 contractions with sum-map threading
    (fresh labels max+1..., rep tracking like U0-G). Redundant marks in
    cyclic subsets become no-ops (ra == rb after prior merges within the
    same marked component: skipped, not failures; the quotient absorbs
    intra-class edges). An order is valid iff it completes without a
    missing-edge failure (ra != rb but no edge: genuine failure, filed);
    matching iff the final (G, |psi|)-multiset matches the synchronous
    quotient outcome (isomorphic graphs + 1e-6 magnitude multisets).
    I_sched = log2(#valid) (m = 0 has exactly 1 valid order (empty),
    I = 0). Predicted: all m! valid and matching (sets commute).
    """
    from bh_graph.contraction import contract_edge

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    edges = sorted(tuple(sorted(e)) for e in subset)
    m = len(edges)
    idx = {v: t for t, v in enumerate(order)}
    vals0 = {v: complex(psi[idx[v]]) for v in order}
    # Synchronous quotient reference (dt = 0: psi_e = psi).
    from bh_graph.u0 import quotient_from_marks, thread_field_sum

    q = quotient_from_marks(g, set(edges))
    qpsi = thread_field_sum(q["classes"], q["node_of"], q["order2"], psi, order)
    qmag = sorted(np.round(np.abs(qpsi), 9).tolist())
    qh = q["h"]
    n_perms = int(math.factorial(m)) if m <= 8 else None
    if m > 6:
        return {"m": int(m), "capped": True, "n_perms": n_perms,
                "n_valid": None, "n_matching": None, "I_sched": None}
    n_valid = 0
    n_match = 0
    for perm in itertools.permutations(edges):
        h = g.copy()
        live = dict(vals0)
        rep = {v: v for v in g.nodes()}
        nxt = max(h.nodes()) + 1 if len(h.nodes()) else 0
        ok = True
        for (a, b) in perm:
            ra, rb = rep[a], rep[b]
            if ra == rb:
                continue  # redundant cyclic mark: intra-class, absorbed.
            if not h.has_edge(ra, rb):
                ok = False
                break
            va, vb = live.pop(ra), live.pop(rb)
            nbrs = sorted((set(h.neighbors(ra)) | set(h.neighbors(rb))) - {ra, rb})
            k = nxt
            nxt += 1
            h.remove_nodes_from((ra, rb))
            h.add_node(k)
            for w in nbrs:
                h.add_edge(k, w)
            live[k] = va + vb
            for v in g.nodes():
                if rep[v] in (ra, rb):
                    rep[v] = k
        if not ok:
            continue
        n_valid += 1
        fmag = sorted(np.round(np.abs(np.array([live[v] for v in sorted(live)])), 9).tolist())
        if nx.is_isomorphic(h, qh) and np.allclose(fmag, qmag, atol=1e-6):
            n_match += 1
    _ = contract_edge
    return {
        "m": int(m),
        "capped": False,
        "n_perms": int(math.factorial(m)),
        "n_valid": int(n_valid),
        "n_matching": int(n_match),
        "I_sched": log2count(n_valid) if n_valid > 0 else None,
        "all_match": bool(n_valid == math.factorial(m) and n_match == math.factorial(m)),
    }


def sync_scheduler_census(g: nx.Graph, psi: np.ndarray, order: list) -> dict:
    """Scheduler census over all 2^E marked subsets (exact, tiny only).

    Per-subset sequential-order counts + matching vs quotient; aggregates:
    all_match fraction, I_sched distribution, max m. Caps at E > 8
    (returns capped True; tiny battery has E <= 4, never capped).
    """
    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    edges = sorted(tuple(sorted(e)) for e in g.edges())
    E = len(edges)
    if E > 8:
        return {"E": int(E), "capped": True}
    rows = []
    for mask in range(1 << E):
        ce = [edges[t] for t in range(E) if mask & (1 << t)]
        r = sequential_orders_for_subset(g, psi, order, ce)
        r["mask"] = int(mask)
        rows.append(r)
    n_all = sum(1 for r in rows if r.get("all_match"))
    return {
        "E": int(E),
        "capped": False,
        "n_subsets": len(rows),
        "n_all_match": int(n_all),
        "f_all_match": float(n_all / len(rows)) if rows else 0.0,
        "rows": rows,
    }


# ---------------------------------------------------------------------------
# F: comparisons (equalities, bounds, separation)
# ---------------------------------------------------------------------------

def compare_branch_loss(n_covers: int, n_branch_raw: int) -> dict:
    """Branch-vs-loss relation: n_branch == 1 + n_covers (exact function).

    I_lost = log2 n_covers; I_branch = log2(1 + n_covers);
    bound: I_lost < I_branch < I_lost + 1 for n_covers >= 1
    (gap = log2(1 + 1/n) in (0, 1]). Never raises.
    """
    try:
        n_covers = int(n_covers)
        n_branch_raw = int(n_branch_raw)
        exact = bool(n_branch_raw == 1 + n_covers)
        i_lost = log2count(n_covers)
        i_branch = log2count(n_branch_raw)
        if i_lost is None or i_branch is None:
            return {"exact": exact, "bound_ok": False, "gap": None}
        gap = float(i_branch - i_lost)
        bound_ok = bool(i_branch > i_lost and gap <= 1.0 + 1e-12 and gap > 0.0)
        return {"exact": exact, "bound_ok": bound_ok, "gap": gap,
                "I_lost": i_lost, "I_branch": i_branch}
    except Exception:
        return {"exact": False, "bound_ok": False, "gap": None}


def compare_pred_branch(pred_set, succ_set) -> dict:
    """Predecessor-vs-successor sets: equality + gap (log counts)."""
    try:
        ps = sorted(str(s) for s in pred_set)
        ss = sorted(str(s) for s in succ_set)
        equal = bool(ps == ss)
        i_pred = log2count(len(ps))
        i_succ = log2count(len(ss))
        if i_pred is None or i_succ is None:
            gap = None
        else:
            gap = float(abs(i_pred - i_succ))
        return {"equal": equal, "gap": gap, "n_pred": len(ps),
                "n_succ": len(ss), "I_pred": i_pred, "I_succ": i_succ}
    except Exception:
        return {"equal": False, "gap": None}


def compare_hist_bound(n_hist: int, T: int, max_out_degree: int) -> dict:
    """History bound: N_hist(a,b,T) <= D_max^T (combinatorial theorem).

    I_hist <= T * log2 D_max when N_hist >= 1 (None for incompatible).
    Never raises.
    """
    try:
        n_hist = int(n_hist)
        T = int(T)
        D = int(max_out_degree)
        if n_hist <= 0:
            return {"bound_ok": True, "vacuous": True, "I_hist": None,
                    "I_cap": (float(T * math.log2(D)) if D >= 1 else None)}
        if D < 1:
            return {"bound_ok": False, "vacuous": False}
        cap = float(T * math.log2(D)) if D > 1 else 0.0
        i_hist = float(math.log2(n_hist))
        return {"bound_ok": bool(n_hist <= D ** T), "vacuous": False,
                "I_hist": i_hist, "I_cap": cap, "gap": float(cap - i_hist)}
    except Exception:
        return {"bound_ok": False, "vacuous": False}


def compare_phys_raw(n_phys: int, n_raw: int) -> dict:
    """Quotient bound: n_phys <= n_raw (grouping cannot increase counts)."""
    try:
        n_phys = int(n_phys)
        n_raw = int(n_raw)
        ok = bool(n_phys <= n_raw and n_phys >= 1 and n_raw >= 1)
        i_phys = log2count(n_phys)
        i_raw = log2count(n_raw)
        if i_phys is None or i_raw is None:
            gap = None
        else:
            gap = float(i_raw - i_phys)
        return {"bound_ok": ok, "gap": gap, "I_phys": i_phys, "I_raw": i_raw}
    except Exception:
        return {"bound_ok": False, "gap": None}


# ---------------------------------------------------------------------------
# G: hidden physical states (HIDDEN0-SEPARATED + SYM-0)
# ---------------------------------------------------------------------------

def hidden_pair_states(L: int = HIDDEN_L) -> dict:
    """Frozen hidden battery on J2-L: matched pairs + vacuum backgrounds.

    Pairs (same P_+, different P_-): sign (B = -A), phase (e^{i pi/2} A),
    shape (delta vs dipole, fixed norm), amplitude (B = 2A, RAW dQ filed).
    P_+ = uniform (VPLUS shape, norm 1); P_- = single-cell delta (norm 1).
    Backgrounds {ZERO, VPLUS, VPI, VMINUS} via MEASURE-0 battery.
    All psi unnormalized sums for pairs (HIDDEN-0 precedent); backgrounds
    normalized (VACFIELD0 shapes).
    """
    from bh_graph.hidden import (hidden_delta, hidden_dipole, matched_pair,
                                 symmetric_uniform)
    from bh_graph.measure0 import background_battery

    L = int(L)
    bat = background_battery(L)
    sub = bat["substrate"]
    order = list(sub["order"])
    c3 = dict(sub["c3"])
    n = len(order)
    pp = symmetric_uniform(n)
    cell0 = (0, 0)
    cell1 = (1, 0)
    ma = hidden_delta(order, c3, cell0)
    mb_shape = hidden_dipole(order, c3, cell0, cell1)
    pairs = {
        "sign": matched_pair(pp, ma, "sign"),
        "phase": matched_pair(pp, ma, "phase", HIDDEN_PHASE),
        "shape": matched_pair(pp, ma, "shape", mb_shape),
        "amplitude": matched_pair(pp, ma, "amplitude", HIDDEN_AMP),
    }
    return {"substrate": sub, "order": order, "pairs": pairs,
            "backgrounds": bat["states"], "L": L}


def hidden_cell_branch(pair_name: str, side: str, patch: str,
                       L: int = HIDDEN_L) -> dict:
    """Branch + loss books for one hidden/vacuum state on a frozen patch.

    pair_name in {sign, phase, shape, amplitude} with side in {A, B}, or
    a vacuum name {ZERO, VPLUS, VPI, VMINUS} (side ignored). patch in
    {"edge0", "node0"} (first edge / first node, deterministic).
    Reports n_raw/n_phys/I (edge or node), contraction error (edge only),
    and the state signature key (U1/R-invariant, hidden-sensitive).
    """
    from bh_graph.measure0 import signature_key, state_signature

    info = hidden_pair_states(int(L))
    sub = info["substrate"]
    g = sub["graph"]
    order = list(info["order"])
    if pair_name in info["pairs"]:
        psi = np.asarray(info["pairs"][pair_name][f"psi_{side}"],
                         dtype=np.complex128)
    elif pair_name in info["backgrounds"]:
        psi = np.asarray(info["backgrounds"][pair_name]["psi"],
                         dtype=np.complex128)
    else:
        raise ValueError(f"unknown hidden state: {pair_name}")
    e0 = sorted(tuple(sorted(e)) for e in g.edges())[0]
    k0 = sorted(g.nodes())[0]
    sig = signature_key(state_signature(g, psi, order))
    out: dict = {"state": pair_name, "side": side, "patch": patch,
                 "sig": str(sig)[:120]}
    if patch == "edge0":
        i, j = e0
        br = branch_patch_edge(g, psi, order, i, j)
        loss = contraction_loss_event(g, psi, order, i, j)
        out["branch"] = br
        out["error_equal"] = loss["error_equal"]
        out["B"] = loss["B"]
        out["I_graph_lost"] = loss["I_graph_lost"]
    elif patch == "node0":
        br = branch_patch_node(g, psi, order, k0)
        out["branch"] = {k: v for k, v in br.items()
                         if k not in ("iso_sizes", "orbit_sizes")}
    else:
        raise ValueError(f"unknown patch: {patch}")
    return out


# ---------------------------------------------------------------------------
# H: firewall audit (no Shannon, no tuning, zero params)
# ---------------------------------------------------------------------------

def fitted_param_count() -> int:
    """Minimality audit: INFO-0 has zero fitted continuous parameters."""
    return 0


def is_no_hidden_tuning_ok() -> bool:
    """Boolean check: no temperature/rate/fitted parameter in signatures."""
    try:
        forbidden = ("beta", "temperature", "temp", "rate", "fitted",
                     "exponent", "preference", "bias", "threshold", "eps_phys")
        fns = [log2count, branch_patch_edge, branch_patch_node,
               global_single_step, global_sync_outcomes, discrete_loss_bits,
               field_loss, contraction_loss_event, predecessor_record,
               history_pair_decomposition, sequential_orders_for_subset,
               compare_branch_loss, compare_pred_branch, compare_hist_bound,
               compare_phys_raw]
        for fn in fns:
            params = [p.lower() for p in inspect.signature(fn).parameters]
            if any(any(f in p for f in forbidden) for p in params):
                return False
        return True
    except Exception:
        return False


def is_no_shannon_ok() -> bool:
    """Boolean check: no Shannon/probability machinery in this module.

    Strips triple-quoted strings + comments, then fails on forbidden
    code patterns (shannon/entropy calls, p log p forms, Boltzmann/Born
    weights, uniform/orbit measures). Counting logs (log2count/math.log2)
    are allowed: they take integer counts, never probability vectors.
    """
    try:
        import re
        import tokenize
        import io

        src = inspect.getsource(inspect.getmodule(is_no_shannon_ok))
        # Remove triple-quoted strings (docstrings mention Shannon negatively).
        src_nostr = re.sub(r'""".*?"""', ' ', src, flags=re.DOTALL)
        src_nostr = re.sub(r"'''.*?'''", ' ', src_nostr, flags=re.DOTALL)
        # Remove comments + string literals via tokenize (keep code only).
        toks = []
        for tok in tokenize.generate_tokens(io.StringIO(src_nostr).readline):
            if tok.type == tokenize.COMMENT:
                continue
            if tok.type == tokenize.STRING:
                continue
            toks.append(tok.string)
        # Single-word forbiddens: exact token match (own audit name
        # is_no_shannon_ok must not self-trigger on substring).
        names = {t.lower() for t in toks}
        forbidden_names = ("shannon", "boltzmann", "uniform_measure",
                           "orbit_uniform", "sample_outcome", "sample_census",
                           "entropy")
        if any(f in names for f in forbidden_names):
            return False
        # Multi-token patterns: whitespace-insensitive substring.
        code_ns = re.sub(r"\s+", "", " ".join(toks)).lower()
        forbidden_seq = ("scipy.stats.entropy", "stats.entropy", "born(",
                         "|psi|**2", "p*np.log", "p*log", "-np.sum", "-sum",
                         "orbit-uniform", "rng.choice", "np.random",
                         "random.random")
        return bool(all(f not in code_ns for f in forbidden_seq))
    except Exception:
        return False
