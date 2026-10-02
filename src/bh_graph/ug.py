"""UG-0 minimal geometry dynamics postulate: exploration apparatus.

Campaign: UG-0 (Minimal Geometry Dynamics Postulate).

Mission: design and freeze the smallest additional primitive dynamical law
required to make geometry evolve. The current ontology already contains
(G, psi) with field dynamics i dpsi/dt = -A(G) psi (H = -A, J = 1, hbar = 1
frozen conventions), plus the earned structural ontology
(local contraction <-> local splitting). BR-2.7 established BR27-NO-MODE:
nothing in the current ontology causes a structural event. UG-0 accepts this
result and does NOT attempt another derivation. Its purpose is to choose one
explicit primitive law U_G: (G_t, psi_t) -> G_{t+1} that is minimal, local,
deterministic and universal.

Status honesty (frozen): any law produced here is A NEW PRIMITIVE DYNAMICAL
POSTULATE -- not emergent, not derived from conservation/energy/instability,
not required by BR-2, not implied by quantum mechanics. Previous campaigns
constrain the possible law strongly but do not determine it.

Frozen evidence respected (re-stated, not re-derived; consumers verify
against the banked branches, see docs/DEFERRED.md BR/CONS/FIELD verdicts):
  - BR-2 quadrature: B_ij = Re(psi_i* psi_j) (geometry sector),
    J_ij = Im(psi_i* psi_j) (flow sector).
  - EM-0/FIELD: J_{i->j} = 2 Im(psi_i* psi_j) is the exact continuity flux
    for |psi_i|^2; dE_psi/dA_ij = -2 B_ij (B is the exact energetic
    conjugate of connectivity). E_psi = -2 sum_{(ij) in E} B_ij (J = 1).
  - BR-2.5: fundamental geometry change may be represented locally by
    i-j -> [ij] and its inverse split; locality radius R_U = 1 achievable;
    simple-graph kind preserved; consumed edge discarded; common neighbors
    collapse to one edge. Field sum map psi_k = psi_i + psi_j gives
    Delta Q_psi = 2 B_ij (CONS-0 load-bearing identity).
  - BR-2.6: full local ledger Delta E_psi^contract = 2 B_ij - 2 sum_cross
    B_cross (common-neighbor collapse is energy-neutral, exactly 0).
    B_ij alone is NOT the complete contraction-energy account.
  - CONS-0: no universal field-involving conserved linear combination closes
    arbitrary contractions (constrains events, does not supply firing).
  - BR-2.7: no continuous deformation mode, no instability, unitary field
    evolution; downhill contractions do not fire by themselves. The event
    law must be postulated explicitly.

Sign-convention note (filed, not hidden): the UG-0 brief states
L_ij = B_ij + sum_cross B_cross with Delta E = 2 L_ij. The frozen BR-2.6
ledger is Delta E = 2 B_ij - 2 sum_cross B_cross where the cross sum runs
over exclusive-neighborhood bonds (i-only and j-only stars, see ledger_L).
The two agree iff "sum_cross" absorbs a minus sign. This module adopts the
FROZEN BR-2.6 minus convention exactly:
L_ij := B_ij - sum_cross B_cross, Delta E = 2 L_ij.
All cross terms are defined in ledger_L; the convention is pinned in tests.

Design principles P1--P9 are enforced as code predicates where checkable
(locality radius, determinism given (G, psi), coordinate-freedom by
construction, substrate-blindness, phase/conjugation behavior, zero-field
consequence, no-target, zero-parameter sign laws).

Primitive alphabet: {CONTRACT, NONE, SPLIT} only. No M1 relocation, no
remote edges.

This module introduces NO field dynamics, NO threshold, NO rate, NO fitted
constant. The sign laws are zero-parameter; eps gating (if used) is an
explicit numerical tolerance, never a physical threshold, and defaults to
exact zero.
"""

from __future__ import annotations

import itertools
import math

import networkx as nx
import numpy as np

# ---------------------------------------------------------------------------
# Frozen identities (re-stated; each pinned in tests below)
# ---------------------------------------------------------------------------

J_DEFAULT = 1.0

CONTRACT = "CONTRACT"
NONE = "NONE"
SPLIT = "SPLIT"


def is_valid_graph(g: nx.Graph) -> bool:
    """Boolean check: simple connected graph (never raises)."""
    try:
        return (not g.is_directed()
                and sum(1 for _ in nx.selfloop_edges(g)) == 0
                and nx.is_connected(g))
    except Exception:
        return False


def bond_B(psi_u: complex, psi_v: complex) -> float:
    """Bond quadrature B_ij = Re(conj(u) v). Symmetric, phase invariant."""
    return float(np.real(np.conj(complex(psi_u)) * complex(psi_v)))


def bond_J(psi_u: complex, psi_v: complex) -> float:
    """Bond current J_ij = Im(conj(u) v). Antisymmetric."""
    return float(np.imag(np.conj(complex(psi_u)) * complex(psi_v)))


def bond_flux(psi_u: complex, psi_v: complex) -> float:
    """Exact continuity flux J_{i->j} = 2 Im(conj(u) v)."""
    return 2.0 * bond_J(psi_u, psi_v)


def is_conjugation_even_ok(a: complex, b: complex) -> bool:
    """Boolean check: B invariant under psi -> psi* (never raises)."""
    try:
        return bool(bond_B(a, b) == bond_B(np.conj(a), np.conj(b)))
    except Exception:
        return False


def field_energy(psi: np.ndarray, g: nx.Graph, order: list) -> float:
    """Wave energy E_psi = -2 sum over edges of B_ij (J = 1).

    Matches the frozen E_psi = <psi|H(G)|psi>, H = -A convention; psi = 0
    gives exactly 0.0 (explicit branch, same universal rule).
    """
    psi = np.asarray(psi, dtype=np.complex128)
    if not np.any(psi):
        return 0.0
    idx = {v: k for k, v in enumerate(order)}
    tot = 0.0
    for a, b in g.edges():
        tot += bond_B(psi[idx[a]], psi[idx[b]])
    return float(-2.0 * tot)


def ledger_L(g: nx.Graph, psi: np.ndarray, order: list, i, j) -> dict:
    """Full local ledger L_ij = B_ij - sum_cross B_cross (frozen BR-2.6).

    Cross sum runs over exclusive stars only:
      sum_{m in N(i)\\N(j)\\{j}} B_{j m} + sum_{m in N(j)\\N(i)\\{i}} B_{i m}.
    Common neighbors contribute exactly 0 (collapse is energy-neutral).
    Returns dict with B_ij, cross, L, dE_formula = 2L, common, n_cross.
    """
    psi = np.asarray(psi, dtype=np.complex128)
    idx = {v: k for k, v in enumerate(order)}
    if not g.has_edge(i, j):
        raise KeyError(f"({i}, {j}) is not an edge")
    ni = set(g.neighbors(i)) - {j}
    nj = set(g.neighbors(j)) - {i}
    common = ni & nj
    only_i = ni - nj
    only_j = nj - ni
    bij = bond_B(psi[idx[i]], psi[idx[j]])
    cross = 0.0
    for m in only_i:
        cross += bond_B(psi[idx[j]], psi[idx[m]])
    for m in only_j:
        cross += bond_B(psi[idx[i]], psi[idx[m]])
    L = bij - cross
    return {
        "B_ij": float(bij),
        "cross": float(cross),
        "L": float(L),
        "dE_formula": float(2.0 * L),
        "common": sorted(common),
        "n_cross": int(len(only_i) + len(only_j)),
    }


# ---------------------------------------------------------------------------
# UG-0B: minimal sign-law family (zero-parameter, design hypothesis)
# ---------------------------------------------------------------------------

def sign_of(x: float) -> int:
    """Exact sign: +1 / 0 / -1 (exact zero, no threshold)."""
    if x > 0.0:
        return 1
    if x < 0.0:
        return -1
    return 0


def decide(X: float) -> str:
    """Deterministic sign law: X > 0 -> CONTRACT, X = 0 -> NONE, X < 0 -> SPLIT.

    The orientation (positive contracts) is the most economical hypothesis
    suggested by BR-2, stated explicitly as DESIGN HYPOTHESIS, not derived.
    Zero-parameter; global-phase invariant and conjugation-even whenever X
    is (both B and L are).
    """
    s = sign_of(float(X))
    if s > 0:
        return CONTRACT
    if s < 0:
        return SPLIT
    return NONE


def edge_decisions(g: nx.Graph, psi: np.ndarray, order: list, law: str) -> dict:
    """Per-edge candidate decisions under UG-B (X = B) or UG-L (X = L).

    law in {"B", "L"}. Returns {(a,b): {"X": float, "decision": str}} with
    canonical (min, max) edge keys. Deterministic; uses only bounded local
    neighborhoods (R = 1 star for B; R = 1 exclusive stars for L).
    """
    if law not in ("B", "L"):
        raise ValueError(f"unknown law: {law}")
    psi = np.asarray(psi, dtype=np.complex128)
    idx = {v: k for k, v in enumerate(order)}
    out = {}
    for a, b in g.edges():
        key = (a, b) if a < b else (b, a)
        if law == "B":
            X = bond_B(psi[idx[a]], psi[idx[b]])
        else:
            X = ledger_L(g, psi, order, a, b)["L"]
        out[key] = {"X": float(X), "decision": decide(X)}
    return out


# ---------------------------------------------------------------------------
# UG-0F/H: contraction op (canonical) and split degeneracy
# ---------------------------------------------------------------------------

def fresh_node_label(g: nx.Graph, i, j):
    """Canonical fresh node label (history-free: no record of i, j kept)."""
    if all(isinstance(v, int) for v in g.nodes()):
        return max(g.nodes()) + 1
    return ("contracted", i, j)


def contract_edge(g: nx.Graph, i, j):
    """Exact local contraction (i,j) -> k (BR-2.5 conventions).

    Simple-graph kind: N(k) = (N(i) u N(j)) \\ {i,j}; consumed edge
    discarded; common neighbors collapse to one edge. dN = -1,
    dE_graph = -(1 + c). Only N(i), N(j) consumed (R_U = 1).
    Returns (g2, k, record); record is the nonlocal memory for exact
    reversal (UG-0H); the forward map keeps no history (memoryless default).
    """
    if not g.has_edge(i, j):
        raise KeyError(f"({i}, {j}) is not an edge")
    nbrs_i = sorted(set(g.neighbors(i)) - {j})
    nbrs_j = sorted(set(g.neighbors(j)) - {i})
    common = sorted(set(nbrs_i) & set(nbrs_j))
    k = fresh_node_label(g, i, j)
    assert k not in g
    g2 = g.copy()
    g2.remove_nodes_from((i, j))
    g2.add_node(k)
    for m in dict.fromkeys(nbrs_i + nbrs_j):
        g2.add_edge(k, m)
    record = {"i": i, "j": j, "k": k, "nbrs_i": nbrs_i, "nbrs_j": nbrs_j,
              "common": common}
    return g2, k, record


def contract_field_sum(psi_i: complex, psi_j: complex) -> complex:
    """Primary contracted-field map: sum (interference kept, dQ = +2B_ij)."""
    return complex(psi_i) + complex(psi_j)


def split_covers(nbrs_k):
    """All record-free local split covers (A, B), A u B = N(k).

    Each neighbor independently A-only / B-only / both: 3^d policies.
    Yields (frozenset A, frozenset B) deterministically ordered.
    Count (undirected, i<->j symmetry): (3^d + 1) / 2.
    """
    nbrs = sorted(nbrs_k)
    for code in itertools.product((0, 1, 2), repeat=len(nbrs)):
        A = frozenset(n for n, c in zip(nbrs, code) if c in (0, 2))
        B = frozenset(n for n, c in zip(nbrs, code) if c in (1, 2))
        yield A, B


def n_split_covers_undirected(d: int) -> float:
    """Undirected cover count (3^d + 1) / 2 (UG-0F degeneracy measure)."""
    return (3 ** int(d) + 1) / 2.0


def apply_split_cover(g: nx.Graph, k, A, B, i, j):
    """Apply one cover policy: k -> i-j with i on A, j on B."""
    h = g.copy()
    h.remove_node(k)
    h.add_node(i)
    h.add_node(j)
    h.add_edge(i, j)
    for m in A:
        h.add_edge(i, m)
    for m in B:
        h.add_edge(j, m)
    return h


def split_policy_current_guided(g: nx.Graph, psi: np.ndarray, order: list, k,
                                i, j) -> tuple:
    """One constrained split-selection pass (UG-0G candidate, debt-filed).

    Policy: assign each neighbor m of k by the sign of the local flow
    discriminator D_m = J_{k->m} (flux from k to m under the sum-field
    convention psi_k placed at k): D_m > 0 -> A-only; D_m < 0 -> B-only;
    D_m == 0 -> both (shared). Then i takes A, j takes B. Satisfies:
    coordinate-free, deterministic, local (1-ball of k), relabeling
    invariant (up to the (i,j) endpoint naming, which is itself arbitrary).

    This is the single permitted design pass. It does NOT close split
    selection: (a) the (i,j) endpoint assignment is itself a binary
    arbitrary choice (swap A<->B is an equally valid twin); (b) exact-zero
    ties ("both") still lump distinct covers; (c) choosing flow (J) over
    bond (B) as the discriminator is a NEW postulate, not an earned rule.
    Filed as SPLIT-SELECTION DEBT. Returns (A, B) frozensets.
    """
    psi = np.asarray(psi, dtype=np.complex128)
    idx = {v: t for t, v in enumerate(order)}
    pk = complex(psi[idx[k]])
    A, B = set(), set()
    for m in sorted(g.neighbors(k)):
        d = bond_flux(pk, complex(psi[idx[m]]))
        if d > 0.0:
            A.add(m)
        elif d < 0.0:
            B.add(m)
        else:
            A.add(m)
            B.add(m)
    return frozenset(A), frozenset(B)


def info_loss_bits(degree_k: int) -> dict:
    """Per-event information books (memoryless default, UG-0H).

    Graph: (3^d+1)/2 undirected covers -> log2 bits. Field: relative
    complex mode lost = 2 real dims under the sum map (exact inversion
    needs infinite precision). Memoryless ontology is the minimality
    default: contraction is many-to-one, exact reversal impossible,
    microscopic irreversibility stated openly.
    """
    n = (3 ** int(degree_k) + 1) / 2.0
    return {"n_covers_undirected": n,
            "graph_bits": float(math.log2(n)) if n > 0 else 0.0,
            "field_real_dims_lost": 2}


# ---------------------------------------------------------------------------
# UG-0I/J: tick conflict semantics and scheduler no-go
# ---------------------------------------------------------------------------

def conflict_pairs(firing: set) -> set:
    """Edge pairs in `firing` sharing a node (naive-tick conflicts)."""
    firing = sorted(firing)
    out = set()
    for a in range(len(firing)):
        for b in range(a + 1, len(firing)):
            e1, e2 = firing[a], firing[b]
            if len({e1[0], e1[1], e2[0], e2[1]}) < 4:
                out.add((e1, e2))
    return out


def scheduler_fire_none(decisions: dict, g: nx.Graph) -> set:
    """Conservative tick: fire an edge iff it says CONTRACT/SPLIT and no
    conflicting edge says CONTRACT/SPLIT (SPLIT included: any structural
    event conflicts on shared nodes).

    Deterministic, local (1-ball conflict detection), relabeling invariant,
    coordinate-free, zero-parameter. Fires nothing under exact symmetry
    (star with all-positive bonds -> all conflict -> none fire) rather than
    breaking symmetry arbitrarily. This COMPLETES scheduler semantics
    without new state, at the price of symmetric stalls (filed openly).
    Returns the fired edge set (canonical keys).
    """
    firing = {e for e, d in decisions.items() if d["decision"] != NONE}
    blocked = set()
    for e1, e2 in conflict_pairs(firing):
        blocked.add(e1)
        blocked.add(e2)
    return set(sorted(firing - blocked))


def scheduler_label_greedy(decisions: dict) -> set:
    """NEGATIVE CONTROL: label-ordered greedy maximal set (breaks relabeling
    invariance by construction; demonstrates what UG-0J forbids)."""
    ordered = sorted(e for e in decisions if decisions[e]["decision"] != NONE)
    taken, out = set(), []
    for a, b in ordered:
        if a not in taken and b not in taken:
            taken.add(a)
            taken.add(b)
            out.append((a, b))
    return set(out)


def intrinsic_discriminator_tie(g: nx.Graph, psi: np.ndarray, order: list,
                                law: str) -> dict:
    """Exact-symmetry tie exhibit (UG-0J): star with uniform bonding field.

    All leaves carry identical psi, so every edge has identical X under
    either law; any intrinsic discriminator built only from earned local
    quantities (|X|, degree, B sums) ties exactly. Breaking the tie needs
    labels (forbidden), randomness (forbidden), scheduler state (new
    primitive), or firing none / a composite event. Returns the tie table.
    """
    dec = edge_decisions(g, psi, order, law)
    xs = sorted(d["X"] for d in dec.values())
    tied = len(xs) > 1 and (max(xs) - min(xs) == 0.0)
    return {"n_edges": len(dec), "X_values": xs, "all_tied": bool(tied),
            "fired_fire_none": sorted(scheduler_fire_none(dec, g))}


# ---------------------------------------------------------------------------
# UG-0K: symmetry predicates
# ---------------------------------------------------------------------------

def permute_state(g: nx.Graph, psi: np.ndarray, order: list, perm: dict):
    """Relabeled state (P G P^-1, P psi): Wikipedia-grade covariance check."""
    nodes = list(order)
    mapping = {v: perm.get(v, v) for v in nodes}
    h = nx.relabel_nodes(g, mapping)
    idx = {v: k for k, v in enumerate(order)}
    order2 = [mapping[v] for v in order]
    psi2 = np.array([psi[idx[v]] for v in order], dtype=np.complex128)
    # reorder psi2 to match order2 positions: psi2[pos of mapping[v]] = psi[v]
    pos = {v: k for k, v in enumerate(order2)}
    out = np.zeros_like(psi2)
    for v in order:
        out[pos[mapping[v]]] = psi[idx[v]]
    return h, out, order2


def is_relabeling_covariant_ok(g: nx.Graph, psi: np.ndarray, order: list,
                               law: str, perm: dict) -> bool:
    """Boolean check: decisions commute with relabeling (never raises)."""
    try:
        dec = edge_decisions(g, psi, order, law)
        h, psi2, order2 = permute_state(g, psi, order, perm)
        dec2 = edge_decisions(h, psi2, order2, law)
        # map dec keys through perm
        mapped = {}
        for (a, b), d in dec.items():
            pa, pb = perm.get(a, a), perm.get(b, b)
            key = (pa, pb) if pa < pb else (pb, pa)
            mapped[key] = d["decision"]
        got = {e: d["decision"] for e, d in dec2.items()}
        return bool(mapped == got)
    except Exception:
        return False


def is_phase_invariant_ok(g: nx.Graph, psi: np.ndarray, order: list,
                          law: str, alpha: float = 0.7) -> bool:
    """Boolean check: U_G(G, e^{i alpha} psi) == U_G(G, psi) (never raises)."""
    try:
        d1 = edge_decisions(g, psi, order, law)
        d2 = edge_decisions(g, np.asarray(psi) * np.exp(1.0j * alpha),
                            order, law)
        return bool(all(d1[e]["decision"] == d2[e]["decision"] for e in d1))
    except Exception:
        return False


def is_conjugation_covariant_ok(g: nx.Graph, psi: np.ndarray, order: list,
                                law: str) -> bool:
    """Boolean check: geometry depends only on conjugation-even inputs, so
    U_G(G, psi*) == U_G(G, psi) under UG-B/UG-L (never raises)."""
    try:
        d1 = edge_decisions(g, psi, order, law)
        d2 = edge_decisions(g, np.conj(np.asarray(psi)), order, law)
        return bool(all(d1[e]["decision"] == d2[e]["decision"] for e in d1))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# UG-0L: locality theorem (coded predicate + documented proof)
# ---------------------------------------------------------------------------

def changed_within_radius(g0: nx.Graph, g1: nx.Graph, i, j,
                          radius: int = 1) -> dict:
    """Light-cone predicate: every changed node within `radius` of {i,j}.

    Changed = present in both graphs with a different neighbor set.
    Single contraction satisfies radius = 1 (R_U = 1); t sequential ticks
    satisfy radius <= t before field-mediated effects (induction: each tick
    touches only the 1-ball of its edge; union bound over t ticks).
    """
    d0 = dict(nx.single_source_shortest_path_length(g0, i))
    d1 = dict(nx.single_source_shortest_path_length(g0, j))
    changed = []
    for v in g0.nodes():
        if v == i or v == j or v not in g1:
            continue
        if set(g0.neighbors(v)) != set(g1.neighbors(v)):
            changed.append(min(d0.get(v, 10 ** 9), d1.get(v, 10 ** 9)))
    mx = max(changed) if changed else 0
    return {"ok": bool(mx <= radius), "max_changed_dist": int(mx),
            "n_changed": int(len(changed))}


# ---------------------------------------------------------------------------
# UG-0C/D/E + UG-0M: analytic comparison states and one-tick census
# ---------------------------------------------------------------------------

def matched_state(n: int, rho: float, dtheta: float) -> np.ndarray:
    """Matched-amplitude banked state: psi_0 = rho, all others rho e^{i dtheta}.

    dtheta = 0 bonding; pi antibonding; pi/2 pure current (B = 0 on every
    cross edge from node 0, |J| maximal). Phase-sweep ready.
    """
    dtheta = float(dtheta)
    c, s = math.cos(dtheta), math.sin(dtheta)
    # Snap trig zeros to exact 0.0 so pure-current (pi/2) banked states carry
    # exactly B = 0 rather than 1e-17 float residue (exact-zero pin).
    if abs(c) < 1e-12:
        c = 0.0
    if abs(s) < 1e-12:
        s = 0.0
    psi = np.full(n, complex(rho * c, rho * s), dtype=np.complex128)
    psi[0] = complex(rho, 0.0)
    return psi


def compare_laws_table(g: nx.Graph, psi: np.ndarray, order: list) -> dict:
    """UG-0C analytic comparison: per-edge (B-decision, L-decision, agree?).

    Purpose is to understand what each postulate MEANS on frozen banked
    states, not to select by outcome. Returns counts + disagreement list.
    """
    db = edge_decisions(g, psi, order, "B")
    dl = edge_decisions(g, psi, order, "L")
    agree = sum(1 for e in db if db[e]["decision"] == dl[e]["decision"])
    disagree = sorted(e for e in db if db[e]["decision"] != dl[e]["decision"])
    return {"n": len(db),
            "B_contract": sum(1 for e in db if db[e]["decision"] == CONTRACT),
            "B_split": sum(1 for e in db if db[e]["decision"] == SPLIT),
            "B_none": sum(1 for e in db if db[e]["decision"] == NONE),
            "L_contract": sum(1 for e in dl if dl[e]["decision"] == CONTRACT),
            "L_split": sum(1 for e in dl if dl[e]["decision"] == SPLIT),
            "L_none": sum(1 for e in dl if dl[e]["decision"] == NONE),
            "agree": int(agree), "disagree": disagree}


def one_tick_census(g: nx.Graph, psi: np.ndarray, order: list,
                    law: str) -> dict:
    """UG-0M one-tick apparatus validation (NO long evolution).

    Candidate decisions -> fire-none scheduler -> sequential local
    application of fired CONTRACTIONS only (splits are counted, never
    applied: SPLIT realization is debt, UG-0F). Reports candidate/fired/
    conflict counts, contractions/splits, Delta N, Delta E_graph,
    Delta E_psi (sum-map ledger), Delta Q_psi, symmetry residuals
    (phase/conjugation booleans on the pre-tick state).
    """
    psi = np.asarray(psi, dtype=np.complex128)
    dec = edge_decisions(g, psi, order, law)
    firing = {e for e, d in dec.items() if d["decision"] != NONE}
    n_conflict_pairs = len(conflict_pairs(firing))
    fired = scheduler_fire_none(dec, g)
    contracts = sorted(e for e in fired if dec[e]["decision"] == CONTRACT)
    splits = sorted(e for e in fired if dec[e]["decision"] == SPLIT)
    # Apply contractions sequentially (skip those consumed by earlier ticks;
    # each applied tick is R_U = 1 local; count skipped as conflicts).
    h = g.copy()
    hpsi = np.array(psi, dtype=np.complex128)
    horder = list(order)
    hidx = {v: k for k, v in enumerate(horder)}
    applied, skipped = [], []
    dE_psi, dQ_psi = 0.0, 0.0
    for a, b in contracts:
        if not h.has_edge(a, b):
            skipped.append((a, b))
            continue
        led = ledger_L(h, hpsi, horder, a, b)
        dE_psi += led["dE_formula"]
        dQ_psi += 2.0 * led["B_ij"]
        h2, k, _ = contract_edge(h, a, b)
        # thread sum-map field through the contraction
        vals = {v: complex(hpsi[hidx[v]]) for v in horder}
        kval = vals[a] + vals[b]
        horder2 = [v for v in horder if v != a and v != b] + [k]
        hpsi = np.array([vals[v] for v in horder2[:-1]] + [kval],
                        dtype=np.complex128)
        hidx = {v: t for t, v in enumerate(horder2)}
        h, horder = h2, horder2
        applied.append((a, b))
    return {
        "law": law,
        "n_edges": int(g.number_of_edges()),
        "n_candidates": int(len(firing)),
        "n_conflict_pairs": int(n_conflict_pairs),
        "n_fired": int(len(fired)),
        "n_contract": int(len(contracts)),
        "n_split": int(len(splits)),
        "n_applied": int(len(applied)),
        "n_skipped": int(len(skipped)),
        "dN": int(h.number_of_nodes() - g.number_of_nodes()),
        "dE_graph": int(h.number_of_edges() - g.number_of_edges()),
        "dE_psi": float(dE_psi),
        "dQ_psi": float(dQ_psi),
        "phase_ok": bool(is_phase_invariant_ok(g, psi, order, law)),
        "conj_ok": bool(is_conjugation_covariant_ok(g, psi, order, law)),
    }


def verdict() -> dict:
    """UG-0 primary verdict logic (principle-based, UG-0N compliant).

    Scoring is a strict dominance hierarchy (no numerical weights):
    1. complete law? 2. local? 3. deterministic? 4. relabeling invariant?
    5. no hidden state? 6. zero free parameters? 7. fewer primitive inputs?

    Findings banked by this module:
    - Scheduler closes via fire-none (deterministic, local, invariant,
      stateless, zero-parameter) for BOTH candidates.
    - Split selection does NOT close: 3^d degeneracy with no unique
      zero-parameter local policy surviving UG-0G conditions (the single
      current-guided pass introduces an endpoint-naming choice plus a new
      J-over-B discriminator postulate).
    Hence neither UG-B nor UG-L is a complete law: the additional primitive
    debts are SPLIT-SELECTION (both) with symmetric-stall openly filed for
    the scheduler. Selection by phenomenological outcome is FORBIDDEN
    (UG-0N): no candidate is preferred here for destroying/preserving J2.
    On inputs (criterion 7) UG-B uses strictly fewer primitives (single
    bond vs full exclusive-star ledger), while on banked-identity
    consistency UG-L tracks the full contraction energy (BR-2.6) that UG-B
    provably misses -- neither dominates. With incompleteness prevailing,
    the verdict is UG0-NO-COMPLETE-LAW (BR-3C remains blocked).
    """
    return {
        "verdict": "UG0-NO-COMPLETE-LAW",
        "interpretation": ("one geometry-firing postulate is insufficient; "
                           "the ontology still lacks structural update "
                           "semantics (split realization + symmetric-stall "
                           "costs filed as primitive debts)"),
        "ug_b_complete": False,
        "ug_l_complete": False,
        "scheduler_closed": True,
        "scheduler_mechanism": "fire-none (symmetric stalls filed)",
        "split_closed": False,
        "split_debt": "SPLIT-SELECTION DEBT (both candidates)",
        "br3c": "BLOCKED",
    }
