"""U0 minimal geometry dynamics: candidate laws, frozen tick, gate battery.

Campaign: U0 (Minimal Geometry Dynamics). Selects, or rejects, a minimal
primitive law governing local geometry change. Accepts BR27-NO-MODE
(the current ontology contains no mechanism causing structural events)
and CONS0-PARTIAL (no conservation-derived contraction law). Any
surviving U_G is A NEW PRIMITIVE DYNAMICAL POSTULATE -- not emergent,
not derived from conservation/energy/instability/BR-2/gravity/known
physics. Previous results constrain its form but do not imply it.

Frozen evidence consumed read-only (re-stated, never re-derived):
  - Field: H(G) = -A(G), J = 1, hbar = 1; i dpsi/dt = -A psi via
    ballistic.evolve_fixed (Krylov, exact-unitary, deterministic).
  - Quadrature (BR-2): B_uv = Re(psi_u* psi_v) geometry sector,
    J_uv = Im(psi_u* psi_v) flow sector; flux J_{u->v} = 2 Im(...).
  - Energy (EM-0): E_psi = -2 sum_E B; dE/dA = -2B (B is the exact
    energetic conjugate of connectivity).
  - Ledger (BR-2.6): contraction dE = 2B_ij - 2 sum_cross B_cross
    over exclusive stars; common-neighbor collapse energy-neutral (0).
    L_ij := B_ij - sum_cross B_cross (MINUS convention, frozen).
  - Ontology (BR-2.5): (i,j) -> k simple-graph contraction, sum map
    psi_k = psi_i + psi_j, dQ = +2B_ij, 3^d split covers, R_U = 1.
  - No-go (CONS-0): no field-involving linear invariant closes
    arbitrary contractions; splits degenerate (Q1/Q2/Q3 census).
  - Scheduler (UG-0): fire-none closes formally but UG0-banked data
    shows TOTAL STALL on all uniform-field states (30/30 one-tick
    rows fire 0 except isolated spikes). U0 therefore freezes the
    synchronous quotient tick (UG-0-AMENDMENT-1, prospective there,
    FROZEN here as U0-I) so the firing law itself is probed rather
    than scheduler stall. Cost filed openly: decision radius stays 1
    while one-tick effect reach = marked-component diameter
    (unbounded a priori).

U0-A candidate semantics (frozen pre-data, analytic):
  - UB (bond-sign): B > 0 -> CONTRACT, = 0 -> NONE, < 0 -> SPLIT.
  - UL (ledger-sign): L > 0 -> CONTRACT, = 0 -> NONE, < 0 -> SPLIT,
    with L the frozen BR-2.6 quantity. Orientation (+ contracts) is
    frozen by (i) continuity with UB as cross -> 0 (L -> B, pinned),
    (ii) UG-0 byte-continuity (same decide()), (iii) the opposite
    orientation is covered by UEc (no gap).
  - UEc (contraction-only energy selection): per-edge exact-energy
    comparison of {separate, contracted}: contract iff dE = 2L < 0,
    else NONE (strict descent; ties -> NONE = minimal action).
    THEOREM (pinned): UEc contracts exactly where flipped-UL would,
    and never proposes SPLIT (no per-edge split state exists in the
    frozen ontology). Full-UE (with splits) is NOT a complete law
    (U0-H4: generic argmin ties, derived + measured).
  - SPLIT marks are reported per edge (tendency census). Node-split
    REALIZATION is undefined for all candidates (U0-H): repeated
    dynamics are contraction-only (splits counted, never applied).
    Consequence (theorem, pinned): N(t) monotone nonincreasing;
    explosion/fragmentation structurally unreachable (filed, not
    measured).

U0-I frozen tick (full-sync quotient, zero new parameters):
  From X_t = (G_t, psi_t): marks from (G_t, psi_t) only; CONTRACT
  classes merge simultaneously (quotient graph, simple kind);
  psi^e = evolve_fixed(psi_t, H(G_t), dt = DT_DEFAULT = 0.1, 1 step);
  psi_{t+1} = sum-thread psi^e onto G_{t+1}. Both updates see X_t
  only; no within-tick ordering exists (U0-G commutation, pinned).

This module introduces NO threshold, NO rate, NO fitted constant, NO
target (J2/matter/etc.). Tolerances below are numerical identities
(bitwise / 1e-12 algebraic / 1e-9 Krylov-energy), never physics.
"""

from __future__ import annotations

import itertools
import math

import networkx as nx
import numpy as np

from bh_graph import ug
from bh_graph.ballistic import DT_DEFAULT, evolve_fixed, hamiltonian, index_of

LAWS = ("UB", "UL", "UEc")
CONTRACT = ug.CONTRACT
NONE = ug.NONE
SPLIT = ug.SPLIT

DT_FROZEN = float(DT_DEFAULT)
T_DEFAULT = 20
TIE_ATOL = 1e-12
KRYLOV_ATOL = 1e-9


# ---------------------------------------------------------------------------
# U0-A: candidate semantics (frozen)
# ---------------------------------------------------------------------------


def decisions_ub(g: nx.Graph, psi: np.ndarray, order: list) -> dict:
    """UB marks: sign(B) per edge (read-only UG-0 law)."""
    return ug.edge_decisions(g, np.asarray(psi, dtype=np.complex128), list(order), "B")


def decisions_ul(g: nx.Graph, psi: np.ndarray, order: list) -> dict:
    """UL marks: sign(L) per edge, L frozen BR-2.6 (read-only UG-0 law)."""
    return ug.edge_decisions(g, np.asarray(psi, dtype=np.complex128), list(order), "L")


def decisions_uec(g: nx.Graph, psi: np.ndarray, order: list) -> dict:
    """UEc marks: contract iff exact contraction dE = 2L < 0 (strict).

    Frozen BR-2.6 dE formula; ties (dE == 0) -> NONE (minimal action).
    Never SPLIT: no per-edge split state exists in the frozen ontology.
    """
    from bh_graph.accounting import dE_contract_formula

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    out = {}
    for a, b in g.edges():
        key = (a, b) if a < b else (b, a)
        dE = float(dE_contract_formula(g, psi, order, a, b))
        out[key] = {"X": dE, "decision": CONTRACT if dE < 0.0 else NONE}
    return out


def u0_decisions(g: nx.Graph, psi: np.ndarray, order: list, law: str) -> dict:
    """Dispatch UB/UL/UEc (canonical edge keys, deterministic)."""
    if law == "UB":
        return decisions_ub(g, psi, order)
    if law == "UL":
        return decisions_ul(g, psi, order)
    if law == "UEc":
        return decisions_uec(g, psi, order)
    raise ValueError(f"unknown U0 law: {law}")


def is_uec_theorem_ok(g: nx.Graph, psi: np.ndarray, order: list) -> bool:
    """Boolean check (U0-A theorem): UEc contracts exactly where L < 0 and
    never SPLITs; UL-flipped agrees on the contraction side (never raises)."""
    try:
        dul = decisions_ul(g, psi, order)
        due = decisions_uec(g, psi, order)
        for e, d in due.items():
            L = float(dul[e]["X"])
            want = CONTRACT if L < 0.0 else NONE
            if d["decision"] != want:
                return False
            if d["decision"] == SPLIT:
                return False
        return True
    except Exception:
        return False


def is_ub_ul_crosscheck_ok(g: nx.Graph, psi: np.ndarray, order: list) -> bool:
    """Boolean check: UG-0 B/L inputs equal frozen BR formulas (never raises).

    B vs backreaction.bond_B; L vs accounting dE/2 (BR-2.6 ledger).
    """
    try:
        from bh_graph.accounting import dE_contract_formula
        from bh_graph.backreaction import bond_B

        psi = np.asarray(psi, dtype=np.complex128)
        order = list(order)
        idx = index_of(order)
        dub = decisions_ub(g, psi, order)
        dul = decisions_ul(g, psi, order)
        for a, b in g.edges():
            key = (a, b) if a < b else (b, a)
            if dub[key]["X"] != bond_B(psi, idx[a], idx[b]):
                return False
            # Same formula, different float association: 1e-12, not bitwise.
            if abs(dul[key]["X"] * 2.0 - dE_contract_formula(g, psi, order, a, b)) >= 1e-12:
                return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# U0-L states (frozen battery S1..S8)
# ---------------------------------------------------------------------------


def bfs_parity_map(g: nx.Graph, root=None) -> dict:
    """Deterministic parity map: BFS distance parity from root (min label).

    Intrinsic given (graph, root); root defaults to the smallest label.
    On bipartite graphs this is a proper bipartition; elsewhere the
    same-parity edges are characterized, not hidden.
    """
    if root is None:
        root = min(g.nodes())
    dist = dict(nx.single_source_shortest_path_length(g, root))
    return {v: dist[v] & 1 for v in g.nodes()}


def exact_stagger(n: int, q: np.ndarray, which: str) -> np.ndarray:
    """Bitwise-exact quadrature states (normalized).

    which: bonding (rho), current (i rho on q=1), antibonding (-rho),
    current-neg (-i rho). Cross-q edges carry exactly B/J in
    {0, +-rho^2} with zero float residue (pinned).
    """
    n = int(n)
    rho = 1.0 / math.sqrt(n)
    q = np.asarray(q, dtype=int)
    if which == "bonding":
        return np.full(n, complex(rho, 0.0), dtype=np.complex128)
    if which == "current":
        return np.where(q == 0, complex(rho, 0.0), complex(0.0, rho)).astype(np.complex128)
    if which == "antibonding":
        return np.where(q == 0, complex(rho, 0.0), complex(-rho, 0.0)).astype(np.complex128)
    if which == "current-neg":
        return np.where(q == 0, complex(rho, 0.0), complex(0.0, -rho)).astype(np.complex128)
    raise ValueError(f"unknown stagger: {which}")


def u0_states() -> dict:
    """Frozen U0-L battery S1..S8 (deterministic, no seeds except ER7).

    S1 zero-field J2; S2 bonding J2; S3 pure-current J2 (exact B = 0);
    S4 antibonding J2; S5 square control (bonding); S6 ring control
    (bonding); S7 irregular ER + BFS-parity current (mixed B);
    S8 collapsed-mini (bonding). All psi normalized except S1 (zero).
    """
    from bh_graph.conservation import (
        field_uniform,
        field_zero,
        substrate_collapsed_mini,
        substrate_er,
        substrate_j2,
        substrate_ring,
        substrate_square_torus,
    )

    out = {}
    j2 = substrate_j2(6)
    order = j2["order"]
    n = len(order)
    q = np.array([j2["bipart"][v] for v in order])
    out["S1"] = {
        "g": j2["g"],
        "psi": field_zero(n),
        "order": list(order),
        "substrate": "j2-L6",
        "field": "zero",
    }
    out["S2"] = {
        "g": j2["g"].copy(),
        "psi": field_uniform(n),
        "order": list(order),
        "substrate": "j2-L6",
        "field": "bonding",
    }
    out["S3"] = {
        "g": j2["g"].copy(),
        "psi": exact_stagger(n, q, "current"),
        "order": list(order),
        "substrate": "j2-L6",
        "field": "current",
    }
    out["S4"] = {
        "g": j2["g"].copy(),
        "psi": exact_stagger(n, q, "antibonding"),
        "order": list(order),
        "substrate": "j2-L6",
        "field": "antibonding",
    }
    sq = substrate_square_torus(6)
    out["S5"] = {
        "g": sq["g"],
        "psi": field_uniform(len(sq["order"])),
        "order": list(sq["order"]),
        "substrate": "square-torus-6",
        "field": "bonding",
    }
    rg = substrate_ring(24)
    out["S6"] = {
        "g": rg["g"],
        "psi": field_uniform(len(rg["order"])),
        "order": list(rg["order"]),
        "substrate": "ring-24",
        "field": "bonding",
    }
    er = substrate_er()
    er_q = np.array([bfs_parity_map(er["g"])[v] for v in er["order"]])
    out["S7"] = {
        "g": er["g"],
        "psi": exact_stagger(len(er["order"]), er_q, "current"),
        "order": list(er["order"]),
        "substrate": "er-24",
        "field": "bfs-current",
    }
    cm = substrate_collapsed_mini()
    out["S8"] = {
        "g": cm["g"],
        "psi": field_uniform(len(cm["order"])),
        "order": list(cm["order"]),
        "substrate": "collapsed-mini",
        "field": "bonding",
    }
    return out


# ---------------------------------------------------------------------------
# U0-I: frozen full-sync quotient tick
# ---------------------------------------------------------------------------


def quotient_from_marks(g: nx.Graph, contract_edges: set) -> dict:
    """Quotient graph from CONTRACT marks (naming: singletons keep labels,
    merged classes take fresh ints in min-member order; convention only).

    Simple kind: inter-class edges kept once, intra-class edges absorbed.
    Returns {h, order2, classes, membership, intra_absorbed}.
    """
    ce = sorted(tuple(sorted(e)) for e in contract_edges)
    h = nx.Graph()
    h.add_nodes_from(g.nodes())
    h.add_edges_from(ce)
    comps = [sorted(c) for c in nx.connected_components(h)]
    comps.sort(key=lambda c: c[0])
    if not all(isinstance(v, int) for v in g.nodes()):
        raise ValueError("u0 tick requires integer node labels")
    nxt = max(g.nodes()) + 1
    node_of = {}
    for c in comps:
        if len(c) == 1:
            node_of[c[0]] = c[0]
        else:
            for v in c:
                node_of[v] = nxt
            nxt += 1
    q = nx.Graph()
    for v in g.nodes():
        q.add_node(node_of[v])
    for a, b in g.edges():
        na, nb = node_of[a], node_of[b]
        if na != nb:
            q.add_edge(na, nb)
    cls = {}
    for ci, c in enumerate(comps):
        for v in c:
            cls[v] = ci
    intra = sum(1 for a, b in g.edges() if cls[a] == cls[b])
    return {
        "h": q,
        "order2": sorted(q.nodes()),
        "classes": comps,
        "node_of": node_of,
        "merged": [c for c in comps if len(c) > 1],
        "intra_absorbed": int(intra),
    }


def thread_field_sum(
    classes: list, node_of: dict, order2: list, psi_e: np.ndarray, order: list
) -> np.ndarray:
    """U_G bookkeeping: supernode value = sum of evolved member values."""
    psi_e = np.asarray(psi_e, dtype=np.complex128)
    idx = index_of(list(order))
    pos = {v: k for k, v in enumerate(order2)}
    acc: dict = {}
    for v in order:
        nv = node_of[v]
        acc[nv] = acc.get(nv, 0.0j) + complex(psi_e[idx[v]])
    out = np.zeros(len(order2), dtype=np.complex128)
    for nv, val in acc.items():
        out[pos[nv]] = val
    return out


def pair_dq_formula(classes: list, psi_e: np.ndarray, order: list) -> float:
    """Multi-merger norm theorem: dQ = 2 sum_classes sum_{pairs} B_pair.

    Exact algebra (|sum|^2 - sum||^2) on the threaded (evolved) values,
    including non-edge pairs. Gated vs direct in every tick.
    """
    psi_e = np.asarray(psi_e, dtype=np.complex128)
    idx = index_of(list(order))
    tot = 0.0
    for c in classes:
        if len(c) < 2:
            continue
        vals = [complex(psi_e[idx[v]]) for v in c]
        for a in range(len(vals)):
            for b in range(a + 1, len(vals)):
                tot += float(np.real(np.conj(vals[a]) * vals[b]))
    return float(2.0 * tot)


def u0_tick(g: nx.Graph, psi: np.ndarray, order: list, law: str, dt: float = DT_FROZEN) -> dict:
    """One frozen full-sync tick from X = (G, psi) under law (U0-I).

    Marks from X only; CONTRACT classes merge simultaneously; psi^e =
    evolve_fixed(psi, H(G), dt, 1 step); psi' = sum-thread psi^e.
    SPLIT marks are counted, never applied (U0-H). Deterministic.
    """
    from bh_graph.backreaction import energy_full

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    dec = u0_decisions(g, psi, order, law)
    ce = {e for e, d in dec.items() if d["decision"] == CONTRACT}
    se = sorted(e for e, d in dec.items() if d["decision"] == SPLIT)
    q = quotient_from_marks(g, ce)
    h, order2 = q["h"], q["order2"]
    n0 = float(np.sum(np.abs(psi) ** 2))
    e0 = energy_full(psi, g, order)
    psi_e = evolve_fixed(psi, hamiltonian(g, order=order), float(dt), 2)["psi"][1]
    psi2 = thread_field_sum(q["classes"], q["node_of"], order2, psi_e, order)
    n1 = float(np.sum(np.abs(psi2) ** 2))
    e1 = energy_full(psi2, h, order2)
    dq_form = pair_dq_formula(q["classes"], psi_e, order)
    return {
        "law": law,
        "g2": h,
        "psi2": psi2,
        "order2": order2,
        "decisions": dec,
        "n_contract_marks": len(ce),
        "n_split_marks": len(se),
        "split_marks": se,
        "classes": q["classes"],
        "n_merged_classes": len(q["merged"]),
        "max_class_size": int(max((len(c) for c in q["classes"]), default=0)),
        "dN": int(h.number_of_nodes() - g.number_of_nodes()),
        "dE_graph": int(h.number_of_edges() - g.number_of_edges()),
        "dQ_direct": float(n1 - n0),
        "dQ_formula": float(dq_form),
        "dE_psi": float(e1 - e0),
        "intra_absorbed": q["intra_absorbed"],
    }


# ---------------------------------------------------------------------------
# U0-K: one-tick / one-event books
# ---------------------------------------------------------------------------


def cycle_rank(g: nx.Graph) -> int:
    """xi = E - N + ncomp (CONS-0H graph invariant)."""
    return int(g.number_of_edges() - g.number_of_nodes() + nx.number_connected_components(g))


def triangle_count(g: nx.Graph) -> int:
    """Exact triangle total."""
    return int(sum(nx.triangles(g).values()) // 3)


def largest_component_diameter(g: nx.Graph) -> int:
    """Diameter of the largest component (0 for singletons)."""
    if g.number_of_nodes() == 0:
        return 0
    big = max(nx.connected_components(g), key=len)
    if len(big) < 2:
        return 0
    return int(nx.diameter(g.subgraph(big)))


def single_edge_books(g: nx.Graph, psi: np.ndarray, order: list, i, j) -> dict:
    """Frozen single-contraction books on edge (i, j) (BR-2.6/CONS-0).

    Parts (analytic) + direct before/after; the analyzer hard-gates
    parts == direct (integrity, not physics).
    """
    from bh_graph.accounting import event_ledger
    from bh_graph.backreaction import energy_full
    from bh_graph.conservation import contraction_ledger
    from bh_graph.contraction import contracted_state

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    led = event_ledger(g, psi, order, i, j)
    g2, psi2, order2, _, _ = contracted_state(g, psi, order, i, j, "sum")
    clog = contraction_ledger(g, psi, order, i, j)
    return {
        "edge": [i, j],
        "dN": led["dN"],
        "dE": led["dE"],
        "B_ij": led["B_ij"],
        "dQ_formula": led["dQ_formula"],
        "dQ_direct": float(np.sum(np.abs(psi2) ** 2) - np.sum(np.abs(psi) ** 2)),
        "dE_formula": led["dE_formula"],
        "dE_direct": float(energy_full(psi2, g2, order2) - energy_full(psi, g, order)),
        "dE_parts_sum": clog["dE_parts_sum"],
        "dEpsi_direct_cons": clog["dEpsi_direct"],
        "dxi": cycle_rank(g2) - cycle_rank(g),
        "dtri": triangle_count(g2) - triangle_count(g),
    }


# ---------------------------------------------------------------------------
# U0-L: repeated dynamics + observables
# ---------------------------------------------------------------------------


def tick_observables(g: nx.Graph, psi: np.ndarray, order: list, tick: dict | None = None) -> dict:
    """Frozen per-tick observable row (U0-L protocol)."""
    from bh_graph.backreaction import bond_B, energy_full
    from bh_graph.ballistic import ipr
    from bh_graph.blind_u import nsquares

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    idx = index_of(order)
    degs = [d for _, d in g.degree()]
    n_edges = g.number_of_edges()
    bzero = sum(1 for a, b in g.edges() if bond_B(psi, idx[a], idx[b]) == 0.0)
    return {
        "N": int(g.number_of_nodes()),
        "E": int(n_edges),
        "ncomp": int(nx.number_connected_components(g)),
        "Q": float(np.sum(np.abs(psi) ** 2)),
        "Epsi": float(energy_full(psi, g, list(order))),
        "IPR": float(ipr(psi)) if np.any(psi) else 0.0,
        "maxdeg": int(max(degs)) if degs else 0,
        "meandeg": float(sum(degs) / len(degs)) if degs else 0.0,
        "triangles": triangle_count(g),
        "squares": int(nsquares(g)),
        "diameter": largest_component_diameter(g),
        "xi": cycle_rank(g),
        "bzero_frac": float(bzero / n_edges) if n_edges else 0.0,
    }


def run_trajectory(
    g0: nx.Graph,
    psi0: np.ndarray,
    order0: list,
    law: str,
    T: int = T_DEFAULT,
    dt: float = DT_FROZEN,
) -> dict:
    """Frozen repeated dynamics: T full-sync ticks, contraction-only.

    Always runs all T ticks (N = 1 ticks are exact no-ops, pinned).
    Records per-tick observables + marks/mergers + books.
    """
    g, psi, order = g0.copy(), np.asarray(psi0, dtype=np.complex128), list(order0)
    rows = []
    for _ in range(int(T)):
        tick = u0_tick(g, psi, order, law, dt)
        obs = tick_observables(g, psi, order, tick)
        obs.update(
            {
                "n_C": tick["n_contract_marks"],
                "n_S": tick["n_split_marks"],
                "n_merged": tick["n_merged_classes"],
                "max_class": tick["max_class_size"],
                "dN": tick["dN"],
                "dE_graph": tick["dE_graph"],
                "dQ_direct": tick["dQ_direct"],
                "dQ_formula": tick["dQ_formula"],
                "dE_psi": tick["dE_psi"],
            }
        )
        rows.append(obs)
        g, psi, order = tick["g2"], tick["psi2"], tick["order2"]
    rows.append(tick_observables(g, psi, order))
    rows[-1].update(
        {
            "n_C": 0,
            "n_S": 0,
            "n_merged": 0,
            "max_class": 0,
            "dN": 0,
            "dE_graph": 0,
            "dQ_direct": 0.0,
            "dQ_formula": 0.0,
            "dE_psi": 0.0,
        }
    )
    return {
        "law": law,
        "T": int(T),
        "dt": float(dt),
        "rows": rows,
        "N0": int(g0.number_of_nodes()),
        "Nf": int(g.number_of_nodes()),
    }


# ---------------------------------------------------------------------------
# U0-M: frozen runaway classifier (contraction-only decision tree)
# ---------------------------------------------------------------------------


def classify(rows: list, n0: int) -> dict:
    """Frozen classifier on a trajectory's observable rows (T + 1 rows).

    quiescent: zero applied mergers. collapse: Nf <= max(2, ceil(.1 N0)).
    other/{settled-partial, reactivated, window-unresolved}: decided by
    the merger tail (last-3-tick quiet?) and burst count (bursts = ticks
    with mergers > 0; reactivated iff >= 2 bursts separated by >= 2
    quiet ticks). Bounded-active/oscillatory-in-N/explosion/
    fragmentation are structurally unreachable under contraction-only
    (N-monotone + connectivity theorems, pinned) -- filed, not measured.
    """
    mergers = [int(r.get("n_merged", 0)) for r in rows[:-1]]
    total = sum(mergers)
    nf = int(rows[-1]["N"])
    if total == 0:
        return {"label": "quiescent", "subreason": "none", "mergers_total": 0, "Nf": nf}
    if nf <= max(2, int(math.ceil(0.1 * int(n0)))):
        return {"label": "collapse", "subreason": "none", "mergers_total": total, "Nf": nf}
    bursts = [t for t, m in enumerate(mergers) if m > 0]
    reactivated = any(
        b2 - b1 - 1 >= 2 for b1, b2 in itertools.pairwise(bursts)
    )
    if reactivated:
        return {
            "label": "other",
            "subreason": "reactivated",
            "mergers_total": total,
            "Nf": nf,
            "n_bursts": len(bursts),
        }
    if all(m == 0 for m in mergers[-3:]):
        return {"label": "other", "subreason": "settled-partial", "mergers_total": total, "Nf": nf}
    return {"label": "other", "subreason": "window-unresolved", "mergers_total": total, "Nf": nf}


# ---------------------------------------------------------------------------
# U0-H4: energy-minimizing split census (the one forced selection attempt)
# ---------------------------------------------------------------------------


def split_delta_formulas(
    g: nx.Graph, psi: np.ndarray, order: list, k, A: frozenset, B: frozenset
) -> dict:
    """CONS-0K analytic split deltas for cover (A, B) x {equal, norm}.

    equal: dE = -|s|^2/2 - sum_{A cap B} B_km + sum_{A cup B} B_km.
    norm: dE/(-2) = |s|^2/2 + (sum_A + sum_B) B_km/sqrt2 - sum_{A cup B}.
    Re-stated from the frozen CONS0-PREREG record; gated vs direct.
    """
    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(list(order))
    s = complex(psi[idx[k]])
    nbrs = sorted(g.neighbors(k))
    bnd = {m: float(np.real(np.conj(s) * complex(psi[idx[m]]))) for m in nbrs}
    cap = sum(bnd[m] for m in (set(A) & set(B)))
    cup = sum(bnd[m] for m in (set(A) | set(B)))
    sa = sum(bnd[m] for m in A)
    sb = sum(bnd[m] for m in B)
    nsq = abs(s) ** 2
    return {
        "equal": float(-nsq / 2.0 - cap + cup),
        "norm": float(-2.0 * (nsq / 2.0 + (sa + sb) / math.sqrt(2.0) - cup)),
    }


def undirected_covers(nbrs_k) -> list:
    """Undirected split covers {{A, B}} (endpoint swap = gauge, U0-H).

    Canonical keys; count (3^d + 1) / 2 (pinned). Deterministic order.
    """
    from bh_graph.contraction import split_covers

    seen: dict = {}
    for A, B in split_covers(nbrs_k):
        ka = tuple(sorted(A))
        kb = tuple(sorted(B))
        key = (ka, kb) if ka <= kb else (kb, ka)
        if key not in seen:
            seen[key] = (frozenset(A), frozenset(B))
    return [(k, v[0], v[1]) for k, v in sorted(seen.items())]


def min_energy_split(
    g: nx.Graph, psi: np.ndarray, order: list, k, max_options: int | None = None
) -> dict:
    """Argmin-split census at node k over undirected covers x {equal,norm}.

    Direct exact dE per option + CONS-0K analytic cross-check (max
    residual recorded; analyzer hard-gates 1e-9). Tie iff >= 2 options
    within TIE_ATOL of the minimum (exact-degeneracy detection).
    """
    from bh_graph.backreaction import energy_full
    from bh_graph.contraction import (
        apply_split_cover,
        split_field_equal,
        split_field_norm,
    )

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    if not all(isinstance(v, int) for v in g.nodes()):
        raise ValueError("H4 census requires integer node labels")
    idx = index_of(order)
    nbrs = sorted(g.neighbors(k))
    d = len(nbrs)
    covers = undirected_covers(nbrs)
    e0 = energy_full(psi, g, order)
    polys = {"equal": split_field_equal, "norm": split_field_norm}
    opts = []
    worst = 0.0
    for key, A, B in covers:
        ana = split_delta_formulas(g, psi, order, k, A, B)
        for pname, pfun in polys.items():
            i, j = max(g.nodes()) + 1, max(g.nodes()) + 2
            h = apply_split_cover(g, k, A, B, i, j)
            p, q = pfun(complex(psi[idx[k]]))
            order_h = [v for v in order if v != k] + [i, j]
            vals = {v: complex(psi[idx[v]]) for v in order if v != k}
            vals[i], vals[j] = p, q
            psi_h = np.array([vals[v] for v in order_h], dtype=np.complex128)
            dE = float(energy_full(psi_h, h, order_h) - e0)
            worst = max(worst, abs(dE - ana[pname]))
            opts.append(
                {
                    "cover": [list(key[0]), list(key[1])],
                    "policy": pname,
                    "dE_direct": dE,
                    "dE_formula": float(ana[pname]),
                }
            )
            if max_options is not None and len(opts) >= max_options:
                break
        if max_options is not None and len(opts) >= max_options:
            break
    mind = min(o["dE_direct"] for o in opts)
    argmin = [o for o in opts if abs(o["dE_direct"] - mind) <= TIE_ATOL]
    return {
        "node": k,
        "degree": int(d),
        "n_covers_undirected": len(covers),
        "n_options": len(opts),
        "min_dE": float(mind),
        "min_sign": "negative" if mind < 0.0 else ("zero" if mind == 0.0 else "positive"),
        "tied": bool(len(argmin) > 1),
        "n_tied": len(argmin),
        "argmin": argmin[:10],
        "max_formula_residual": float(worst),
        "options": opts if len(opts) <= 100 else [],
    }


def b_guided_cover(g: nx.Graph, psi: np.ndarray, order: list, k):
    """B-guided cover twin of UG-0's J-guided pass (U0-H3 exhibit).

    D_m = B_km: > 0 -> A-only; < 0 -> B-only; == 0 -> both. The J-vs-B
    disagreement on banked states pins selection as unforced.
    """
    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(list(order))
    pk = complex(psi[idx[k]])
    A, B = set(), set()
    for m in sorted(g.neighbors(k)):
        d = float(np.real(np.conj(pk) * complex(psi[idx[m]])))
        if d > 0.0:
            A.add(m)
        elif d < 0.0:
            B.add(m)
        else:
            A.add(m)
            B.add(m)
    return frozenset(A), frozenset(B)


# ---------------------------------------------------------------------------
# U0-E/F/G/J gate predicates
# ---------------------------------------------------------------------------


def is_phase_invariant_ok(
    g: nx.Graph, psi: np.ndarray, order: list, law: str, alpha: float = 0.7
) -> bool:
    """Boolean check: marks invariant under global phase (never raises)."""
    try:
        d1 = u0_decisions(g, psi, order, law)
        d2 = u0_decisions(g, np.asarray(psi) * np.exp(1.0j * alpha), order, law)
        return bool(all(d1[e]["decision"] == d2[e]["decision"] for e in d1))
    except Exception:
        return False


def is_conjugation_covariant_ok(g: nx.Graph, psi: np.ndarray, order: list, law: str) -> bool:
    """Boolean check: marks identical under conjugation (J-blind, B-even)."""
    try:
        d1 = u0_decisions(g, psi, order, law)
        d2 = u0_decisions(g, np.conj(np.asarray(psi)), order, law)
        return bool(all(d1[e]["decision"] == d2[e]["decision"] for e in d1))
    except Exception:
        return False


def is_relabeling_covariant_ok(
    g: nx.Graph, psi: np.ndarray, order: list, law: str, perm: dict
) -> bool:
    """Boolean check: marks commute with relabeling (never raises)."""
    try:
        return bool(
            ug.is_relabeling_covariant_ok(g, psi, order, "B" if law == "UB" else "L", perm)
            if law in ("UB", "UL")
            else _relabel_ok_uec(g, psi, order, perm)
        )
    except Exception:
        return False


def _relabel_ok_uec(g, psi, order, perm) -> bool:
    h, psi2, order2 = ug.permute_state(g, psi, order, perm)
    d1 = decisions_uec(g, psi, order)
    d2 = decisions_uec(h, psi2, order2)
    mapped = {}
    for (a, b), d in d1.items():
        pa, pb = perm.get(a, a), perm.get(b, b)
        key = (pa, pb) if pa < pb else (pb, pa)
        mapped[key] = d["decision"]
    return bool(mapped == {e: d["decision"] for e, d in d2.items()})


def is_tick_relabeling_ok(g: nx.Graph, psi: np.ndarray, order: list, law: str, perm: dict) -> bool:
    """Boolean check: full tick commutes with relabeling up to graph
    isomorphism with mapped field (never raises)."""
    try:
        r1 = u0_tick(g, psi, order, law)
        h, psi2, order2 = ug.permute_state(g, psi, order, perm)
        r2 = u0_tick(h, psi2, order2, law)
        if r1["g2"].number_of_nodes() != r2["g2"].number_of_nodes():
            return False
        if r1["g2"].number_of_edges() != r2["g2"].number_of_edges():
            return False
        if not nx.is_isomorphic(r1["g2"], r2["g2"]):
            return False
        f1 = sorted(np.round(np.abs(r1["psi2"]), 9))
        f2 = sorted(np.round(np.abs(r2["psi2"]), 9))
        return bool(np.allclose(f1, f2, atol=1e-6))
    except Exception:
        return False


def is_mark_field_remote_ok(g: nx.Graph, psi: np.ndarray, order: list, edge, law: str) -> bool:
    """Boolean check (U0-F): mark on edge bitwise-invariant under field
    mutation at distance >= 3 from both endpoints (never raises)."""
    try:
        a, b = edge
        da = dict(nx.single_source_shortest_path_length(g, a))
        db = dict(nx.single_source_shortest_path_length(g, b))
        far = [v for v in g.nodes() if min(da.get(v, 10**9), db.get(v, 10**9)) >= 3]
        if not far:
            return True
        psi = np.asarray(psi, dtype=np.complex128)
        idx = index_of(list(order))
        mut = np.array(psi, dtype=np.complex128)
        mut[idx[far[0]]] += complex(0.5, -0.25)
        key = (a, b) if a < b else (b, a)
        d1 = u0_decisions(g, psi, order, law)[key]
        d2 = u0_decisions(g, mut, order, law)[key]
        return bool(d1["X"] == d2["X"] and d1["decision"] == d2["decision"])
    except Exception:
        return False


def is_ledger_graph_remote_ok(g: nx.Graph, psi: np.ndarray, order: list, edge, law: str) -> bool:
    """Boolean check (U0-F): L/UEc mark bitwise-invariant under an edge
    toggle disjoint from the closed neighborhood N[{i,j}] (never raises;
    UB is graph-blind, pinned separately)."""
    try:
        a, b = edge
        closed = {a, b} | set(g.neighbors(a)) | set(g.neighbors(b))
        outside = [v for v in g.nodes() if v not in closed]
        toggled = None
        h = g.copy()
        for x in outside:
            for y in outside:
                if x < y and not h.has_edge(x, y):
                    h.add_edge(x, y)
                    toggled = ("add", x, y)
                    break
            if toggled:
                break
        if toggled is None:
            for x, y in g.edges():
                if x in outside and y in outside:
                    h.remove_edge(x, y)
                    if nx.is_connected(h):
                        toggled = ("rem", x, y)
                        break
                    h.add_edge(x, y)
        if toggled is None:
            return True
        key = (a, b) if a < b else (b, a)
        d1 = u0_decisions(g, psi, order, law)[key]
        d2 = u0_decisions(h, psi, order, law)[key]
        return bool(d1["X"] == d2["X"] and d1["decision"] == d2["decision"])
    except Exception:
        return False


def is_tick_deterministic_ok(g: nx.Graph, psi: np.ndarray, order: list, law: str) -> bool:
    """Boolean check (U0-J): repeated ticks bitwise-identical G + 1e-12 psi."""
    try:
        r1 = u0_tick(g, psi, order, law)
        r2 = u0_tick(g, psi, order, law)
        e1 = sorted(tuple(sorted(e)) for e in r1["g2"].edges())
        e2 = sorted(tuple(sorted(e)) for e in r2["g2"].edges())
        if e1 != e2 or r1["order2"] != r2["order2"]:
            return False
        return bool(np.allclose(r1["psi2"], r2["psi2"], atol=TIE_ATOL))
    except Exception:
        return False


def sequential_quotient_check(
    g: nx.Graph, psi: np.ndarray, order: list, law: str, seed: int = 0
) -> dict:
    """U0-G commutation exhibit: quotient vs two sequential merger orders.

    Sequential application (BR-2.5 contract_edge + sum map, input psi
    threaded) must yield isomorphic graphs with equal field multisets
    for any merger order (synchronous sets commute). Record, not gate.
    """
    import random

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    dec = u0_decisions(g, psi, order, law)
    ce = sorted(e for e, d in dec.items() if d["decision"] == CONTRACT)
    q = quotient_from_marks(g, set(ce))
    idx = index_of(order)
    vals = {v: complex(psi[idx[v]]) for v in order}
    qvals = sorted(
        np.round(np.abs(thread_field_sum(q["classes"], q["node_of"], q["order2"], psi, order)), 9)
    )

    def run_seq(edges):
        h = g.copy()
        live = dict(vals)
        rep = {v: v for v in g.nodes()}
        nxt = max(h.nodes()) + 1
        for a, b in edges:
            ra, rb = rep[a], rep[b]
            if ra == rb or not h.has_edge(ra, rb):
                continue
            nbrs = sorted((set(h.neighbors(ra)) | set(h.neighbors(rb))) - {ra, rb})
            k = nxt
            nxt += 1
            h.remove_nodes_from((ra, rb))
            h.add_node(k)
            for m in nbrs:
                h.add_edge(k, m)
            live[k] = live.pop(ra) + live.pop(rb)
            for v in g.nodes():
                if rep[v] in (ra, rb):
                    rep[v] = k
        return h, sorted(np.round(np.abs(np.array([live[v] for v in sorted(live)])), 9))

    rng = random.Random(seed)
    e1, e2 = list(ce), list(ce)
    rng.shuffle(e2)
    h1, f1 = run_seq(e1)
    h2, f2 = run_seq(e2)
    return {
        "quotient_nodes": q["h"].number_of_nodes(),
        "quotient_edges": q["h"].number_of_edges(),
        "seq1_iso": bool(nx.is_isomorphic(q["h"], h1)),
        "seq2_iso": bool(nx.is_isomorphic(q["h"], h2)),
        "field_match_1": bool(np.allclose(qvals, f1, atol=1e-6)),
        "field_match_2": bool(np.allclose(qvals, f2, atol=1e-6)),
    }
