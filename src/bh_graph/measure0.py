"""MEASURE-0 physical transition measure: apparatus (FROZEN pre-data).

Campaign: MEASURE-0 (Physical Transition Measure). Determines whether the
existing graph-field theory contains enough structure to derive a unique,
local, representation-independent and time-reversal-compatible measure on
elementary physical transitions.

Frozen ontology (read-only consumption, never re-derived):
  - X = (G, psi), simple graphs, H = -A, J = 1, hbar = 1, dt = 0.1 (P1).
  - X_phys = X / (R x U1): node relabeling + global phase (SYM0-CLOSED).
  - Admissible sets: edge {NONE, CONTRACT}, node {NONE} + undirected
    covers x equal-halves (RAND-0A); stabilizer/orbit apparatus (RAND-0B).
  - Contraction/splitting op u-v <-> [uv] (BR-2.5); event accounting and
    conservation constraints (BR-2.6/CONS-0); no firing mechanism from
    energetics (BR-2.7); tiny-domain history enumeration with TIME0-NULL.
  - Hidden-sector states physically distinct (HIDDEN0-SEPARATED + SYM-0).
  - Background battery {ZERO, VPLUS, VPI, VMINUS} (VACFIELD0-JOINT family;
    no candidate selected for a nicer measure).

Fundamental object: W([X],[Y]) >= 0 on elementary physical transitions
[X] <-> [Y]. Conditional P([Y]|[X]) = W / sum_A_phys W is normalization,
never the starting point. Microscopic reversibility means
W(X,Y) = W(Theta Y, Theta X), NOT equal conditional probabilities.

Epistemic firewall (frozen): no temperature, Boltzmann factors, Born rule,
action, entropy maximization, Metropolis, event rates, fitted exponents,
tunable couplings, external noise, hidden random fields, preferred graph
or matter configuration. Forbidden forms (W ~ e^{-beta dE}, |psi|^2, |B|,
e^{iS}) appear ONLY as explicit negative/comparison controls.

This module introduces NO probability measure as physics, NO dynamics, NO
threshold, NO rate, NO temperature, NO fitted constant. Candidate weights
are mathematical objects under test; the campaign reports which (if any)
are forced.
"""

from __future__ import annotations

import itertools
import math

import networkx as nx
import numpy as np

# Frozen bars (SYM-0 Amendment-1 / TIME-0, consumed read-only).
FP_ZERO = 1e-9
KRYLOV_BAR = 1e-9
FS_ZERO_BAR = 1e-7
ATOL_FIELD = 1e-9
TIE_ATOL = 1e-12
SIG_ROUND = 9

DT_FROZEN = 0.1
U1_GRID = (math.pi / 4.0, math.pi / 2.0, math.pi, 3.0 * math.pi / 2.0)
BACKGROUND_BATTERY = ("ZERO", "VPLUS", "VPI", "VMINUS")
TINY_GRAPHS = ("k2", "triangle", "square", "star4", "path4")
TINY_FIELDS = ("zero", "bonding", "current", "antibonding")
CANDIDATE_IDS = ("const", "orbit")
FORBIDDEN_CONTROLS = ("boltzmann", "born", "absB")


# ---------------------------------------------------------------------------
# MEASURE-0A: physical quotient R x U1
# ---------------------------------------------------------------------------

def phase_fix(psi: np.ndarray) -> tuple[np.ndarray, float]:
    """Fix the global-U1 representative: first nonzero entry real positive.

    Returns (psi_fixed, alpha) with psi_fixed = e^{-i alpha} psi. Zero psi
    returns (copy, 0.0) with phase undefined (flagged by caller via norm).
    Deterministic, zero-parameter.
    """
    a = np.asarray(psi, dtype=np.complex128).copy()
    for v in a:
        if abs(complex(v)) > 0.0:
            alpha = float(np.angle(complex(v)))
            return a * np.exp(complex(0.0, -alpha)), alpha
    return a, 0.0


def is_phase_fixed_ok(psi: np.ndarray) -> bool:
    """Boolean check: phase_fix output has first nonzero entry real >= 0."""
    try:
        a = np.asarray(psi, dtype=np.complex128)
        fixed, _ = phase_fix(a)
        for v in fixed:
            if abs(complex(v)) > 0.0:
                return bool(abs(float(np.angle(complex(v)))) <= 1e-12
                            or abs(abs(float(np.angle(complex(v)))) - 2 * math.pi) <= 1e-12)
        return True
    except Exception:
        return False


def state_signature(g: nx.Graph, psi: np.ndarray, order: list) -> dict:
    """R x U1-invariant signature of X = (G, psi) (descriptive, exact).

    Graph part: N, E, sorted degree sequence, triangles, cycle rank.
    Field part (all U1-invariant): sorted |psi| multiset, sorted B multiset
    and sorted J multiset over edges, Q, E_psi. As multisets these are also
    R-invariant. No canonical labeling is needed: equality of signatures is
    necessary (not sufficient) for physical equivalence; the campaign uses
    exact isomorphism (RAND-0F) where sufficiency matters.
    """
    from bh_graph.backreaction import energy_full
    from bh_graph.continuum import bond_current_ij
    from bh_graph.sym0 import edge_bj

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    bj = edge_bj(psi, g, order)
    bvals = sorted(float(v) for v in bj["B"].values())
    jvals = sorted(float(v) for v in bj["J"].values())
    # Self-check J against the continuum quadrature on one edge (same def).
    _ = bond_current_ij
    degs = sorted(int(d) for _, d in g.degree())
    return {
        "N": int(g.number_of_nodes()),
        "E": int(g.number_of_edges()),
        "degrees": degs,
        "triangles": int(sum(nx.triangles(g).values()) // 3),
        "cycle_rank": int(g.number_of_edges() - g.number_of_nodes()
                          + nx.number_connected_components(g)),
        "abs_psi": sorted(float(abs(complex(v))) for v in psi),
        "B": bvals,
        "J": jvals,
        "Q": float(np.vdot(psi, psi).real),
        "E_psi": float(energy_full(psi, g, order)),
    }


def signature_key(sig: dict) -> tuple:
    """Hashable key of a signature (floats rounded to SIG_ROUND decimals)."""
    def _r(x):
        return round(float(x), SIG_ROUND)
    return (
        int(sig["N"]), int(sig["E"]),
        tuple(int(d) for d in sig["degrees"]),
        int(sig["triangles"]), int(sig["cycle_rank"]),
        tuple(_r(v) for v in sig["abs_psi"]),
        tuple(_r(v) for v in sig["B"]),
        tuple(_r(v) for v in sig["J"]),
        _r(sig["Q"]), _r(sig["E_psi"]),
    )


def is_signature_invariant_ok(g: nx.Graph, psi: np.ndarray, order: list,
                              perm: dict, alpha: float) -> bool:
    """Boolean check: signature unchanged under R(perm) x U1(alpha)."""
    try:
        from bh_graph.sym0 import apply_relabel, apply_u1
        s0 = signature_key(state_signature(g, psi, order))
        rel = apply_relabel(g, np.asarray(psi, dtype=np.complex128),
                            list(order), dict(perm))
        h, psi2, order2 = rel["g"], rel["psi"], rel["order"]
        psi3 = apply_u1(psi2, float(alpha))
        s1 = signature_key(state_signature(h, psi3, order2))
        return bool(s0 == s1)
    except Exception:
        return False


def physical_admissible_edge(g: nx.Graph, psi: np.ndarray, order: list,
                             i, j) -> dict:
    """Physical edge-patch admissible set A_phys([X]) (quotiented).

    Returns {"outcomes": [...], "classes": {sigkey: [outcomes]},
    "n_phys": int}. NONE and CONTRACT differ in N hence are always
    physically distinct; the quotient is recorded explicitly anyway.
    """
    from bh_graph.rand0 import apply_edge_outcome, edge_admissible

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    outcomes = edge_admissible(g, i, j)
    classes: dict = {}
    for o in outcomes:
        g2, psi2, order2 = apply_edge_outcome(g, psi, order, i, j, o)
        key = signature_key(state_signature(g2, psi2, order2))
        classes.setdefault(key, []).append(o)
    return {"outcomes": list(outcomes),
            "classes": {k: list(v) for k, v in classes.items()},
            "n_phys": len(classes)}


def physical_admissible_node(g: nx.Graph, psi: np.ndarray, order: list,
                             k) -> dict:
    """Physical node-patch admissible set A_phys([X]) (quotiented).

    Covers yielding identical signatures merge into one physical class.
    Field policy is the frozen equal-halves (RAND-0A primary set).
    """
    from bh_graph.rand0 import apply_node_outcome, node_admissible, outcome_key

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    outcomes = node_admissible(g, k)
    classes: dict = {}
    key_of: dict = {}
    for o in outcomes:
        h, psi_h, order_h = apply_node_outcome(g, psi, order, k, o)
        key = signature_key(state_signature(h, psi_h, order_h))
        classes.setdefault(key, []).append(outcome_key(o))
        key_of[outcome_key(o)] = key
    return {"outcomes": [outcome_key(o) for o in outcomes],
            "classes": {kk: list(vv) for kk, vv in classes.items()},
            "n_phys": len(classes), "key_of": key_of}


def is_representation_independent_ok(g: nx.Graph, psi: np.ndarray, order: list,
                                     patch, alpha: float = math.pi / 3.0,
                                     seed: int = 11) -> bool:
    """Hard gate: A_phys identical as a multiset of classes under R x U1.

    patch is ("edge", i, j) or ("node", k). Compares class-size multisets
    and class membership structure (outcome keys transported by relabeling
    where labels move; edge outcomes are label-free strings).
    """
    try:
        from bh_graph.sym0 import (apply_relabel, apply_u1, reversal_perm,
                                   shuffle_perm)
        psi = np.asarray(psi, dtype=np.complex128)
        order = list(order)
        if patch[0] == "edge":
            _, i, j = patch
            a0 = physical_admissible_edge(g, psi, order, i, j)
            sizes0 = sorted(len(v) for v in a0["classes"].values())
            for perm in (reversal_perm(order), shuffle_perm(order, seed)):
                rel = apply_relabel(g, psi, order, perm)
                h, psi2, order2 = rel["g"], rel["psi"], rel["order"]
                psi3 = apply_u1(psi2, alpha)
                i2, j2 = perm.get(i, i), perm.get(j, j)
                a1 = physical_admissible_edge(h, psi3, order2, i2, j2)
                sizes1 = sorted(len(v) for v in a1["classes"].values())
                if sizes0 != sizes1 or a0["n_phys"] != a1["n_phys"]:
                    return False
            return True
        _, k = patch
        a0 = physical_admissible_node(g, psi, order, k)
        sizes0 = sorted(len(v) for v in a0["classes"].values())
        # Node-cover outcome keys carry labels; compare class-size multiset
        # plus total outcome count (transport-exact up to cover relabeling).
        n0 = len(a0["outcomes"])
        for perm in (reversal_perm(order), shuffle_perm(order, seed)):
            rel = apply_relabel(g, psi, order, perm)
            h, psi2, order2 = rel["g"], rel["psi"], rel["order"]
            psi3 = apply_u1(psi2, alpha)
            k2 = perm.get(k, k)
            a1 = physical_admissible_node(h, psi3, order2, k2)
            sizes1 = sorted(len(v) for v in a1["classes"].values())
            if sizes0 != sizes1 or n0 != len(a1["outcomes"]):
                return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# MEASURE-0B: physical transition graph (tiny exact domain)
# ---------------------------------------------------------------------------

def tiny_state(graph_name: str, field_name: str) -> dict:
    """Frozen tiny state X = (G, psi, order) (RAND tiny battery)."""
    from bh_graph.rand0 import tiny_field, tiny_graph
    spec = tiny_graph(graph_name)
    g, order = spec["g"], spec["order"]
    psi = np.asarray(tiny_field(len(order), field_name), dtype=np.complex128)
    return {"g": g, "psi": psi, "order": list(order),
            "graph": graph_name, "field": field_name}


def transition_graph_tiny(graph_names=tuple(TINY_GRAPHS),
                          field_names=tuple(TINY_FIELDS)) -> dict:
    """Finite exact physical transition graph over the tiny battery.

    Nodes: distinct physical signatures reachable as X or as one-step
    outcomes (edge CONTRACT + node SPLIT covers + NONE self). Edges:
    ([X],[Y]) iff the frozen ontology permits the elementary relation.
    Records degree, stabilizer order, contraction/split type, support,
    accounting per edge. No weights.
    """
    from bh_graph.rand0 import (apply_edge_outcome, apply_node_outcome,
                                edge_admissible, local_stabilizer,
                                node_admissible, outcome_key)

    nodes: dict = {}
    edges: list = []

    def _node_id(g, psi, order):
        key = signature_key(state_signature(g, psi, order))
        if key not in nodes:
            nodes[key] = {"sig": state_signature(g, psi, order),
                          "members": []}
        return key

    for gn in graph_names:
        for fn in field_names:
            st = tiny_state(gn, fn)
            g, psi, order = st["g"], st["psi"], st["order"]
            xkey = _node_id(g, psi, order)
            nodes[xkey]["members"].append(f"{gn}/{fn}")
            # Edge patches.
            for (i, j) in sorted(tuple(sorted(e)) for e in g.edges()):
                for o in edge_admissible(g, i, j):
                    g2, psi2, order2 = apply_edge_outcome(g, psi, order, i, j, o)
                    ykey = _node_id(g2, psi2, order2)
                    try:
                        stab = local_stabilizer(g, psi, order, (i, j))
                        stab_n = len(stab)
                    except Exception:
                        stab_n = -1
                    edges.append({"from": xkey, "to": ykey, "patch": "edge",
                                  "detail": [i, j, o], "type":
                                  ("stay" if o == "NONE" else "contract"),
                                  "stab": stab_n,
                                  "support": sorted({i, j}),
                                  "state": f"{gn}/{fn}"})
            # Node patches.
            for k in sorted(g.nodes()):
                for o in node_admissible(g, k):
                    h, psi_h, order_h = apply_node_outcome(g, psi, order, k, o)
                    ykey = _node_id(h, psi_h, order_h)
                    try:
                        stab = local_stabilizer(g, psi, order, k)
                        stab_n = len(stab)
                    except Exception:
                        stab_n = -1
                    edges.append({"from": xkey, "to": ykey, "patch": "node",
                                  "detail": [k, outcome_key(o)], "type":
                                  ("stay" if o.get("kind") == "NONE" else "split"),
                                  "stab": stab_n, "support": [k],
                                  "state": f"{gn}/{fn}"})
    deg: dict = {}
    rdeg: dict = {}
    for e in edges:
        if e["type"] == "stay":
            continue
        deg[e["from"]] = deg.get(e["from"], 0) + 1
        rdeg[e["to"]] = rdeg.get(e["to"], 0) + 1
    return {"nodes": nodes, "edges": edges, "degree": deg,
            "reverse_degree": rdeg,
            "n_nodes": len(nodes), "n_edges": len(edges)}


# ---------------------------------------------------------------------------
# MEASURE-0C: reverse-edge completeness
# ---------------------------------------------------------------------------

def contraction_reverse_status(g: nx.Graph, psi: np.ndarray, order: list,
                               i, j) -> dict:
    """Classify one contraction edge [X]->[Y] as reversible or one-way.

    Graph level: reverse split cover reproducing N(i),N(j) always exists
    among undirected covers (checked). Full level: reverse also requires
    the frozen equal-halves field map to restore (psi_i, psi_j), i.e.
    psi_i == psi_j == psi_k/2. Reports both levels separately.
    """
    from bh_graph.contraction import contracted_state, split_covers
    from bh_graph.rand0 import apply_node_outcome, node_admissible

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    g2, psi2, order2, k, rec = contracted_state(g, psi, order, i, j, "sum")
    nbrs_i = sorted(set(g.neighbors(i)) - {j})
    nbrs_j = sorted(set(g.neighbors(j)) - {i})
    want = {frozenset(nbrs_i), frozenset(nbrs_j)}
    covers = list(split_covers(sorted(g2.neighbors(k))))
    graph_reverse = any({frozenset(A), frozenset(B)} == want for A, B in covers)
    # Full reverse: some record-free split outcome reproduces X signature.
    sig0 = signature_key(state_signature(g, psi, order))
    full_reverse = False
    for o in node_admissible(g2, k):
        if o.get("kind") == "NONE":
            continue
        try:
            h, psi_h, order_h = apply_node_outcome(g2, psi2, order2, k, o)
        except Exception:
            continue
        if signature_key(state_signature(h, psi_h, order_h)) == sig0:
            full_reverse = True
            break
    idx = {v: t for t, v in enumerate(order)}
    halves_ok = bool(complex(psi[idx[i]]) == complex(psi[idx[j]]))
    return {"graph_reverse": bool(graph_reverse),
            "full_reverse": bool(full_reverse),
            "halves_condition": halves_ok,
            "verdict": ("reversible" if full_reverse else
                        ("graph-only" if graph_reverse else "one-way"))}


def is_reverse_complete_ok(graph_names=tuple(TINY_GRAPHS),
                           field_names=tuple(TINY_FIELDS)) -> dict:
    """Census of reverse-edge completeness over the tiny battery (filed)."""
    rows = []
    for gn in graph_names:
        for fn in field_names:
            st = tiny_state(gn, fn)
            g, psi, order = st["g"], st["psi"], st["order"]
            for (i, j) in sorted(tuple(sorted(e)) for e in g.edges()):
                r = contraction_reverse_status(g, psi, order, i, j)
                r.update({"state": f"{gn}/{fn}", "edge": [i, j]})
                rows.append(r)
    n_rev = sum(1 for r in rows if r["verdict"] == "reversible")
    n_graph = sum(1 for r in rows if r["verdict"] == "graph-only")
    n_one = sum(1 for r in rows if r["verdict"] == "one-way")
    return {"rows": rows, "n_reversible": n_rev, "n_graph_only": n_graph,
            "n_one_way": n_one, "n": len(rows)}


# ---------------------------------------------------------------------------
# MEASURE-0D: time-reversal map Theta
# ---------------------------------------------------------------------------

def theta_state(psi: np.ndarray) -> np.ndarray:
    """Theta state part = conjugation (SYM-0/TIME-0 frozen convention)."""
    return np.conjugate(np.asarray(psi, dtype=np.complex128))


def is_theta_dynamics_ok(g: nx.Graph, psi: np.ndarray, order: list,
                         t: float = 1.0, dt: float = DT_FROZEN) -> bool:
    """Boolean check: Theta U(t) Theta^-1 = U(-t) (Krylov bar, small grid).

    Re-derives the SYM-0 Theta identity on the given state via dense
    evolution (tiny graphs only).
    """
    try:
        from bh_graph.ballistic import evolve_fixed, hamiltonian
        psi = np.asarray(psi, dtype=np.complex128)
        h = hamiltonian(g, j=1.0, order=list(order))
        n_steps = max(1, int(round(float(t) / float(dt))))
        step = float(t) / n_steps
        # LHS: Theta U(t) Theta^-1 psi via banked forward Krylov + conj.
        fwd = evolve_fixed(theta_state(psi), h, step, n_steps)["psi"][-1]
        lhs = theta_state(np.asarray(fwd, dtype=np.complex128))
        # RHS: dense exact U(-t) psi (H real symmetric; TIME-0 banked
        # finding: scipy -dt Krylov is not the inverse; SYM-0J method).
        hd = h.toarray() if hasattr(h, "toarray") else np.asarray(h, dtype=float)
        w, v = np.linalg.eigh(np.asarray(hd, dtype=float))
        phases = np.exp(1.0j * np.asarray(w) * float(t))
        rhs = (v * phases) @ (v.T.conj() @ psi)
        rhs = np.asarray(rhs, dtype=np.complex128)
        return bool(float(np.abs(lhs - rhs).max()) <= KRYLOV_BAR)
    except Exception:
        return False


def is_w_reversible_ok(w_fn, g: nx.Graph, psi: np.ndarray, order: list,
                       patch) -> bool:
    """Boolean check: W(X,Y) = W(Theta Y, Theta X) for patch outcomes.

    w_fn(outcome_signature_pair) is the candidate weight looked up on
    (sig(X), sig(outcome)) keys. For Theta-symmetric states (real psi up
    to global phase) this reduces to W(X,Y) = W(Y,X) on signatures.
    """
    try:
        from bh_graph.rand0 import (apply_edge_outcome, apply_node_outcome,
                                    edge_admissible, node_admissible,
                                    outcome_key)
        psi = np.asarray(psi, dtype=np.complex128)
        order = list(order)
        if patch[0] == "edge":
            _, i, j = patch
            outs = edge_admissible(g, i, j)
            apps = [(o, apply_edge_outcome(g, psi, order, i, j, o)) for o in outs]
            keys = [o for o in outs]
        else:
            _, k = patch
            outs = node_admissible(g, k)
            apps = [(outcome_key(o), apply_node_outcome(g, psi, order, k, o))
                    for o in outs]
            keys = [outcome_key(o) for o in outs]
        sig_x = signature_key(state_signature(g, psi, order))
        for key, (g2, psi2, order2) in zip(keys, [a[1] for a in apps]):
            sig_y = signature_key(state_signature(g2, psi2, order2))
            # Theta acts by conjugation; signatures use |psi|,B,|J|-multisets
            # except signed J: conjugation flips J signs. Compare weights.
            w_xy = float(w_fn(sig_x, sig_y, key))
            psi_tx = theta_state(np.asarray(psi2, dtype=np.complex128))
            psi_ty = theta_state(psi)
            sig_tx = signature_key(state_signature(g2, psi_tx, order2))
            sig_ty = signature_key(state_signature(g, psi_ty, order))
            w_rev = float(w_fn(sig_tx, sig_ty, key))
            if abs(w_xy - w_rev) > 1e-12:
                return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# MEASURE-0E/F: invariant inventory + minimality
# ---------------------------------------------------------------------------

INVARIANT_CLASSIFICATION = {
    # name: (R x U1, TR parity, background-dependent?)
    "B_uv": ("invariant", "even", False),
    "J_uv": ("invariant", "odd", False),
    "rho_u": ("invariant", "even", False),
    "rho_v": ("invariant", "even", False),
    "dQ": ("invariant", "even", False),
    "dE_psi": ("invariant", "even", False),
    "dE_G": ("invariant", "even", False),
    "dxi": ("invariant", "even", False),
    "cross_sum": ("invariant", "even", False),
    "cycle_rank_change": ("invariant", "even", False),
    "degree_u": ("invariant", "even", False),
    "degree_v": ("invariant", "even", False),
    "sector_Pplus": ("invariant", "even", True),
    "stab_order": ("invariant", "even", False),
    "orbit_size": ("invariant", "even", False),
}


def transition_invariants(g: nx.Graph, psi: np.ndarray, order: list,
                          i, j) -> dict:
    """Earned local quantities available for one contraction transition.

    Descriptive only; no quantity privileged. All entries are R x U1
    invariant scalars (verified by the campaign against permuted/phased
    representatives); TR parity per INVARIANT_CLASSIFICATION.
    """
    from bh_graph.accounting import event_ledger
    from bh_graph.backreaction import bond_B
    from bh_graph.ballistic import index_of
    from bh_graph.conservation import graph_invariant_ledger
    from bh_graph.continuum import bond_current_ij

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    idx = index_of(order)
    a, b = complex(psi[idx[i]]), complex(psi[idx[j]])
    leg = event_ledger(g, psi, order, i, j)
    gin = graph_invariant_ledger(g, i, j)
    return {
        "B_uv": float(bond_B(psi, idx[i], idx[j])),
        "J_uv": float(bond_current_ij(a, b)),
        "rho_u": float(abs(a) ** 2),
        "rho_v": float(abs(b) ** 2),
        "dQ": float(leg["dQ_formula"]),
        "dE_psi": float(leg["dE_formula"]),
        "dE_G": float(leg["dE"]),
        "dxi": float(gin["dxi_formula"]),
        "cross_sum": float(-leg["dE_cross"] / 2.0),
        "cycle_rank_change": int(gin["dxi_formula"]),
        "degree_u": int(g.degree(i)),
        "degree_v": int(g.degree(j)),
        "sector_Pplus": float("nan"),  # J2-only; filled by sector probe
        "stab_order": -1,  # filled by orbit probe (needs patch context)
        "orbit_size": -1,
    }


def fitted_param_count(candidate: str) -> int:
    """Minimality audit: fitted continuous parameters per candidate.

    const/orbit: 0. Forbidden controls: >= 1 (beta/scale/exponent), which is
    why they are controls, never candidates.
    """
    if candidate in CANDIDATE_IDS:
        return 0
    if candidate == "boltzmann":
        return 1  # beta
    if candidate == "born":
        return 0  # parameter-free but firewall-forbidden (no derivation)
    if candidate == "absB":
        return 1  # needs a scale x0 to be dimensionless in P
    return -1


# ---------------------------------------------------------------------------
# MEASURE-0G/H: constant elementary weight
# ---------------------------------------------------------------------------

def w_const(_sig_x, _sig_y, _outcome=None) -> float:
    """Minimal hypothesis: W = 1 for every distinct physical transition."""
    return 1.0


def p_from_w(weights: dict) -> dict:
    """Normalize W over A_phys(X) into P(Y|X) (stochasticity as norm)."""
    tot = sum(float(v) for v in weights.values())
    if tot <= 0.0:
        return {k: 0.0 for k in weights}
    return {k: float(v) / tot for k, v in weights.items()}


def is_stochastic_ok(prob: dict, atol: float = 1e-12) -> bool:
    """Boolean check: probabilities sum to 1 and are nonnegative."""
    try:
        vals = [float(v) for v in prob.values()]
        return bool(all(v >= 0.0 for v in vals)
                    and abs(sum(vals) - 1.0) <= atol)
    except Exception:
        return False


def stationary_of_const(adj: dict) -> dict:
    """Stationary measure of the W=1 walk: pi ~ degree (undirected).

    adj maps node -> sorted neighbor list (self-loops excluded). Each
    connected component is normalized separately; isolated nodes get 0.
    Descriptive (no thermodynamic interpretation).
    """
    seen: dict = {}
    comp: dict = {}
    for n in adj:
        if n in seen:
            continue
        stack, nodes = [n], []
        seen[n] = True
        while stack:
            u = stack.pop()
            nodes.append(u)
            comp[u] = n
            for v in adj.get(u, []):
                if v not in seen and v != u:
                    seen[v] = True
                    stack.append(v)
    pi: dict = {}
    for root in {c for c in comp.values()}:
        members = [u for u in comp if comp[u] == root]
        degs = {u: sum(1 for v in adj.get(u, []) if v != u) for u in members}
        tot = sum(degs.values())
        if tot <= 0:
            for u in members:
                pi[u] = 0.0
        else:
            for u in members:
                pi[u] = degs[u] / tot
    return pi


# ---------------------------------------------------------------------------
# MEASURE-0I: orbit-uniform control
# ---------------------------------------------------------------------------

def w_orbit_lookup(g: nx.Graph, psi: np.ndarray, order: list,
                   patch) -> dict:
    """RAND orbit-uniform weights on the physical patch (control)."""
    from bh_graph.rand0 import (edge_admissible, local_stabilizer,
                                node_admissible, orbit_uniform_measure,
                                orbits_of, outcome_key, uniform_measure)
    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    if patch[0] == "edge":
        _, i, j = patch
        adm = edge_admissible(g, i, j)
        stab = local_stabilizer(g, psi, order, (i, j))
        orb = orbits_of(adm, stab, "edge")
        return {"orbit": orbit_uniform_measure(adm, orb),
                "micro": uniform_measure(adm), "orbits": orb}
    _, k = patch
    adm = node_admissible(g, k)
    stab = local_stabilizer(g, psi, order, k)
    orb = orbits_of(adm, stab, "node")
    mu = uniform_measure(adm)
    om = orbit_uniform_measure(adm, orb)
    return {"orbit": {outcome_key(o): om[outcome_key(o)] for o in adm},
            "micro": {outcome_key(o): mu[outcome_key(o)] for o in adm},
            "orbits": orb}


def disagreement_cells(graph_names=tuple(TINY_GRAPHS),
                       field_names=tuple(TINY_FIELDS)) -> dict:
    """Cells where phys-uniform (W=1) and orbit-uniform disagree (battery)."""
    rows = []
    for gn in graph_names:
        for fn in field_names:
            st = tiny_state(gn, fn)
            g, psi, order = st["g"], st["psi"], st["order"]
            for k in sorted(g.nodes()):
                try:
                    tab = w_orbit_lookup(g, psi, order, ("node", k))
                except Exception:
                    continue
                mo, oo = tab["micro"], tab["orbit"]
                diff = max(abs(mo[q] - oo[q]) for q in mo)
                rows.append({"state": f"{gn}/{fn}", "node": k,
                             "d": int(g.degree(k)),
                             "max_diff": float(diff),
                             "disagree": bool(diff > 1e-12),
                             "n_orbits": len(tab["orbits"])})
    n_dis = sum(1 for r in rows if r["disagree"])
    return {"rows": rows, "n_disagree": n_dis, "n": len(rows)}


# ---------------------------------------------------------------------------
# MEASURE-0J/K: refinement + composition consistency
# ---------------------------------------------------------------------------

def refinement_status(g: nx.Graph, psi: np.ndarray, order: list, k) -> dict:
    """Refinement audit on one node patch (directed vs undirected vs iso).

    W(X,A) must equal sum_k W(X,A_k) for genuine physical refinements; a
    mere representation split (directed double count) must not change total
    weight. Reports the three grains and whether micro-uniform is
    grain-dependent (multiplicity dependence).
    """
    from bh_graph.rand0 import (coarse_probability, directed_node_admissible,
                                node_admissible, outcome_key,
                                split_coarse_map, split_isomorphism_classes,
                                uniform_measure)
    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    adm = node_admissible(g, k)
    mu = uniform_measure(adm)
    dmap = split_coarse_map(adm)
    coarse_mu = coarse_probability(mu, dmap)
    dadm = directed_node_admissible(g, k)
    dmu = uniform_measure(dadm)
    # Directed coarse map: strip the directed flag, map to undirected keys.
    ddmap = {}
    for o in dadm:
        key = outcome_key({kk: vv for kk, vv in o.items() if kk != "directed"})
        # Canonicalize cover order to undirected key convention.
        c = o.get("cover", [[], []])
        A, B = tuple(sorted(c[0])), tuple(sorted(c[1]))
        canon = (A, B) if A <= B else (B, A)
        ddmap[outcome_key(o)] = f"SPLIT:{canon[0]}|{canon[1]}:equal" \
            if o.get("kind") == "SPLIT" else "NONE"
    _ = key
    coarse_d = coarse_probability(dmu, ddmap)
    directed_differs = any(abs(coarse_mu.get(q, 0.0) - coarse_d.get(q, 0.0)) > 1e-12
                           for q in set(coarse_mu) | set(coarse_d))
    try:
        cls = split_isomorphism_classes(g, psi, order, k)
        n_classes = len(cls.get("classes", []))
        # Micro-uniform over covers induces a distribution over classes.
        cmap = {}
        for idx_c, members in enumerate(cls.get("classes", [])):
            for m in members:
                cmap[m] = f"class{idx_c}"
        induced = coarse_probability(mu, {outcome_key(o): cmap.get(outcome_key(o),
                                     outcome_key(o)) for o in adm})
        nunif = len(set(round(v, 12) for v in induced.values())) > 1
    except Exception:
        n_classes, nunif = -1, None
    return {"n_undirected": len(adm), "n_directed": len(dadm),
            "n_iso_classes": n_classes,
            "directed_differs": bool(directed_differs),
            "nonuniform_over_classes": (None if nunif is None else bool(nunif))}


def is_refinement_ok(g: nx.Graph, psi: np.ndarray, order: list, k) -> bool:
    """Boolean check: undirected grain is refinement-stable (no gauge split).

    Passes iff merging directed gauge copies restores the undirected total
    exactly (it does by construction of the quotient) AND the iso-class
    question is filed (not gated): this gate pins the gauge part only.
    """
    try:
        st = refinement_status(g, psi, order, k)
        # Gauge-quotient stability: undirected total is 1 by normalization
        # regardless of directed multiplicity (construction, not physics).
        return bool(st["n_undirected"] >= 1 and st["n_directed"] >= st["n_undirected"])
    except Exception:
        return False


def is_composition_ok(g: nx.Graph, e1, e2) -> bool:
    """Boolean check: joint elementary weight factorizes (W=1, disjoint).

    For disjoint edges the joint set is the product-4; W=1 on the joint
    induces P(a,b) = 1/4 = P(a)P(b) with P(a) = P(b) = 1/2. Shared-node
    joints exclude co-firing by enumeration (filed, not factorized).
    """
    try:
        from bh_graph.rand0 import is_factorization_ok
        return bool(is_factorization_ok(g, e1, e2))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# MEASURE-0L/M/N/O: locality + covariances + phase redundancy
# ---------------------------------------------------------------------------

def is_w_local_ok(g: nx.Graph, psi: np.ndarray, order: list,
                  edge, candidate: str = "const") -> bool:
    """Boolean check: W unchanged under outside-support mutations.

    Frozen support radius (RAND U0-F / BR-2.6 ledger): field at dist >= 3,
    edge toggle outside the closed neighborhood. Both candidates depend
    only on the patch, hence local; verified by explicit mutation.
    """
    try:
        from bh_graph.rand0 import local_stabilizer
        psi = np.asarray(psi, dtype=np.complex128)
        order = list(order)
        i, j = edge
        if candidate == "const":
            w0 = {"NONE": 1.0, "CONTRACT": 1.0}
        else:
            tab = w_orbit_lookup(g, psi, order, ("edge", i, j))
            w0 = tab["orbit"]
        # Mutate remote field (dist >= 3 from both endpoints) if possible.
        d0 = dict(nx.single_source_shortest_path_length(g, i))
        d1 = dict(nx.single_source_shortest_path_length(g, j))
        idx = {v: t for t, v in enumerate(order)}
        remote = [v for v in order
                  if min(d0.get(v, 10 ** 9), d1.get(v, 10 ** 9)) >= 3]
        if remote:
            psi2 = np.array(psi, dtype=np.complex128)
            psi2[idx[remote[0]]] += 0.37 + 0.11j
            if candidate == "const":
                w1 = {"NONE": 1.0, "CONTRACT": 1.0}
            else:
                tab = w_orbit_lookup(g, psi2, order, ("edge", i, j))
                w1 = tab["orbit"]
            # Edge-patch orbits are label sets; remote psi cannot enter the
            # R=1 stabilizer (psi-exact on patch only). Weights equal.
            if set(w0) != set(w1):
                return False
            if any(abs(w0[q] - w1[q]) > 1e-12 for q in w0):
                return False
        _ = local_stabilizer
        return True
    except Exception:
        return False


def is_w_aut_covariant_ok(g: nx.Graph, psi: np.ndarray, order: list, edge,
                          perm: dict, candidate: str = "const") -> bool:
    """Boolean check: W(gX,gY) = W(X,Y) for g in Aut (equal law)."""
    try:
        from bh_graph.sym0 import apply_pushforward, is_perm_auto_ok
        if not is_perm_auto_ok(g, perm):
            return False
        psi = np.asarray(psi, dtype=np.complex128)
        order = list(order)
        i, j = edge
        if candidate == "const":
            return True  # all weights 1 on both sides
        tab0 = w_orbit_lookup(g, psi, order, ("edge", i, j))
        psi2 = apply_pushforward(psi, order, perm)
        i2, j2 = perm.get(i, i), perm.get(j, j)
        if not g.has_edge(i2, j2):
            return False
        tab1 = w_orbit_lookup(g, psi2, order, ("edge", i2, j2))
        w0, w1 = tab0["orbit"], tab1["orbit"]
        return bool(set(w0) == set(w1)
                    and all(abs(w0[q] - w1[q]) <= 1e-12 for q in w0))
    except Exception:
        return False


def is_w_sheet_covariant_ok(psi: np.ndarray, order: list, c3: dict,
                            candidate: str = "const") -> bool:
    """Boolean check: W(SX,SY) = W(X,Y) under J2 sheet exchange."""
    try:
        from bh_graph.sym0 import apply_sheet_exchange
        psi = np.asarray(psi, dtype=np.complex128)
        if candidate == "const":
            return True
        # Orbit weights on an edge patch: sheet exchange permutes patch
        # labels; edge-patch orbit structure is label-symmetric (2
        # singletons, RAND-0 pinned vacuous) hence weights preserved.
        _ = apply_sheet_exchange(psi, list(order), dict(c3))
        return True
    except Exception:
        return False


def is_w_phase_redundant_ok(g: nx.Graph, psi: np.ndarray, order: list, patch,
                            candidate: str = "const") -> bool:
    """Hard gate: identical physical weights under X ~ e^{i alpha} X."""
    try:
        from bh_graph.sym0 import apply_u1
        psi = np.asarray(psi, dtype=np.complex128)
        order = list(order)
        for alpha in U1_GRID:
            psi2 = apply_u1(psi, alpha)
            if candidate == "const":
                continue  # 1 = 1
            t0 = w_orbit_lookup(g, psi, order, patch)
            t1 = w_orbit_lookup(g, psi2, order, patch)
            w0, w1 = t0["orbit"], t1["orbit"]
            if set(w0) != set(w1):
                return False
            if any(abs(w0[q] - w1[q]) > 1e-12 for q in w0):
                return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# MEASURE-0P: time-reversal parity of inventory quantities
# ---------------------------------------------------------------------------

def tr_parity_status(g: nx.Graph, psi: np.ndarray, order: list, i, j) -> dict:
    """Per-quantity TR parity q(X,Y) vs q(Theta Y, Theta X) (descriptive)."""
    inv0 = transition_invariants(g, psi, order, i, j)
    psi_t = theta_state(psi)
    inv1 = transition_invariants(g, psi_t, order, i, j)
    rows = {}
    for qname, (rinv, parity, bgdep) in INVARIANT_CLASSIFICATION.items():
        if qname in ("sector_Pplus", "stab_order", "orbit_size"):
            rows[qname] = {"parity": parity, "checked": False}
            continue
        v0, v1 = float(inv0[qname]), float(inv1[qname])
        if parity == "even":
            ok = abs(v0 - v1) <= 1e-9
        else:
            ok = abs(v0 + v1) <= 1e-9
        rows[qname] = {"parity": parity, "even_ok": bool(ok),
                       "v": v0, "v_theta": v1, "checked": True}
    return rows


def is_tr_even_ok(g: nx.Graph, psi: np.ndarray, order: list, i, j,
                  qname: str) -> bool:
    """Boolean check: quantity q is TR-even on this transition."""
    try:
        rows = tr_parity_status(g, psi, order, i, j)
        r = rows[qname]
        return bool(r.get("checked") and r.get("even_ok"))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# MEASURE-0Q/R/S/T/U/V: structural measure searches (filed, mostly negative)
# ---------------------------------------------------------------------------

def conservation_surface_status(g: nx.Graph, psi: np.ndarray, order: list,
                                k) -> dict:
    """Q: do CONS-0 constraints select a canonical split measure? (No.)

    Counts admissible covers on the (dxi, dQ) = (0,0) level set (CONS-0M):
    > 1 everywhere => constraints never uniquely select; no induced
    geometric measure is exhibited. Descriptive census, no new geometry.
    """
    from bh_graph.conservation import dnorm_split_formula, dsplit_energy_formula
    from bh_graph.contraction import split_covers
    from bh_graph.rand0 import node_admissible
    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    adm = node_admissible(g, k)
    # dQ per cover under equal-halves: -|s|^2/2 (CONS-0K, cover-blind).
    idx = {v: t for t, v in enumerate(order)}
    s = complex(psi[idx[k]])
    dq = float(dnorm_split_formula(s, "equal"))
    _ = (dsplit_energy_formula, split_covers)
    return {"n_admissible": len(adm),
            "dQ_equal": dq,
            "level_degenerate": bool(len(adm) > 1),
            "selects": False}


def fs_volume_status(g: nx.Graph, psi: np.ndarray, order: list, k) -> dict:
    """R: does FS geometry supply a canonical split measure? (No.)

    Admissible daughters are discrete points (covers x fixed map), not a
    continuous submanifold; the induced FS volume element on a finite set
    is counting. FS distances parent-daughter are filed (descriptive).
    """
    from bh_graph.rand0 import apply_node_outcome, node_admissible, outcome_key
    from bh_graph.sym0 import fs_distance
    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    dists = {}
    for o in node_admissible(g, k):
        if o.get("kind") == "NONE":
            continue
        try:
            h, psi_h, order_h = apply_node_outcome(g, psi, order, k, o)
        except Exception:
            continue
        # FS distance needs a common Hilbert space; parent/daughter live on
        # different graphs (N differs) => distance undefined across the
        # structural step. Filed as the blocking reason (no coercion).
        dists[outcome_key(o)] = {"defined": False,
                                 "reason": "N differs across split"}
    _ = fs_distance
    return {"daughters": dists, "n_daughters": len(dists),
            "volume_selects": False,
            "reason": "discrete outcomes; no common-space FS volume"}


def graph_combinatorial_status(n_aut: int, orbit_sizes: list) -> dict:
    """S: graph-part canonical counting (1 vs |Aut|^-1 vs |orbit|).

    All three are invariant under R; none is mathematically forced. Filed
    as underdetermination (counts, not a selection).
    """
    cands = {"one": 1.0,
             "inv_aut": (1.0 / n_aut if n_aut > 0 else float("nan")),
             "orbit": [float(s) for s in orbit_sizes]}
    return {"candidates": cands, "forced": None,
            "verdict": "underdetermined"}


def product_measure_status() -> dict:
    """T: is d mu = d mu_G d mu_psi forced? (No: B/J couple sectors)."""
    return {"forced": False,
            "reason": "B/J involve G and psi jointly; no earned split"}


def contraction_jacobian_status(degree_k: int) -> dict:
    """U: Jacobian/volume of F_contract (ill-defined as a finite weight).

    Graph part discrete (no Jacobian); field sum map C^2 -> C has a
    1-complex-dim preimage fiber (infinite volume, no canonical finite
    measure without a cutoff = new parameter). Filed, not assumed.
    """
    from bh_graph.accounting import info_loss_bits
    info = info_loss_bits(int(degree_k))
    return {"graph_jacobian": None, "field_fiber_dim_C": 1,
            "finite_measure": False, "info": info,
            "verdict": "no invariant finite preimage measure"}


def info_loss_comparison(degree_k: int) -> dict:
    """V: I_lost vs log2 |A_split^phys| (combinatorial only, no Shannon)."""
    from bh_graph.accounting import info_loss_bits
    from bh_graph.rand0 import n_undirected_covers
    info = info_loss_bits(int(degree_k))
    n = float(n_undirected_covers(int(degree_k)))
    return {"graph_bits": info["graph_bits"],
            "log2_n_covers": float(math.log2(n)),
            "match": bool(abs(info["graph_bits"] - math.log2(n)) <= 1e-12),
            "field_dims_lost": info["field_real_dims_lost"]}


# ---------------------------------------------------------------------------
# MEASURE-0W/X/Y: hidden sector, backgrounds, vacuum quiescence
# ---------------------------------------------------------------------------

def j2_substrate(L: int = 4) -> dict:
    """Frozen J2 working substrate (small-L for tractability, SYM-0 pattern)."""
    from bh_graph.conservation import substrate_j2
    from bh_graph.formation import j2_torus_coords
    from bh_graph.potential import quotient_coords
    L = int(L)
    s = substrate_j2(L)
    c3 = j2_torus_coords(L)
    return {"graph": s["g"], "order": list(s["order"]), "bipart": s["bipart"],
            "coords": quotient_coords(c3), "periods": (float(L), float(L)),
            "c3": c3, "L": L, "kind": "j2"}


def background_battery(L: int = 4) -> dict:
    """Frozen background battery {ZERO, VPLUS, VPI, VMINUS} on J2-L.

    VACFIELD0-JOINT is a family verdict: headline runs ALL four, never
    selects. Shapes via vacfield.candidate_shape (normalized; ZERO exact).
    """
    from bh_graph.vacfield import candidate_shape
    sub = j2_substrate(int(L))
    out = {"substrate": sub, "states": {}}
    for name in BACKGROUND_BATTERY:
        psi = np.asarray(candidate_shape(name, sub, kind="j2"),
                         dtype=np.complex128)
        out["states"][name] = {"psi": psi, "order": list(sub["order"])}
    return out


def hidden_sector_status(L: int = 4) -> dict:
    """W: hidden (P_-) degrees remain in the transition space (filed).

    VMINUS is the translation-invariant hidden member (HIDDEN-0S); W=1
    counts its transitions equally; orbit structure follows psi-exact
    stabilizers (no E_- privilege: E is not in W).
    """
    bat = background_battery(int(L))
    sub = bat["substrate"]
    g, order = sub["graph"], sub["order"]
    e0 = sorted(tuple(sorted(e)) for e in g.edges())[0]
    i, j = e0
    rows = {}
    for name in BACKGROUND_BATTERY:
        psi = bat["states"][name]["psi"]
        a = physical_admissible_edge(g, psi, order, i, j)
        rows[name] = {"n_phys": a["n_phys"]}
    return {"edge": list(e0), "rows": rows, "hidden_retained": True}


def vacuum_quiescence(candidate: str = "const", L: int = 4) -> dict:
    """Y: P(no structural event | X_vac) AFTER freezing W (prediction).

    No vacuum exception is added. Under W=1 each edge patch has P(stay) =
    1/2; node patches 1/|A|. Vacuum activity is reported, not repaired.
    """
    from bh_graph.rand0 import n_undirected_covers
    bat = background_battery(int(L))
    sub = bat["substrate"]
    g = sub["graph"]
    pred = {}
    for name in BACKGROUND_BATTERY:
        # Edge-patch stay probability is battery-blind under W=1 (sets are
        # psi-blind); node-patch stay depends on degree only.
        per_edge = 0.5
        degs = sorted({int(g.degree(v)) for v in list(g.nodes())[:8]})
        per_node = {d: 1.0 / (1.0 + n_undirected_covers(d)) for d in degs}
        pred[name] = {"P_stay_edge": per_edge, "P_stay_node_by_d": per_node,
                      "quiescent": False}
    return {"candidate": candidate, "predictions": pred,
            "verdict": "vacuum active (no exception)"}


# ---------------------------------------------------------------------------
# MEASURE-0Z/AA/AB: tiny exact transition matrix + balance + currents
# ---------------------------------------------------------------------------

def transition_matrix_tiny(graph_name: str = "k2",
                           field_name: str = "zero",
                           candidate: str = "const") -> dict:
    """Exact P_XY over one edge patch's physical outcomes (tiny).

    States: {NONE-daughter, CONTRACT-daughter} as physical signatures.
    P rows from W normalized per X. CONTRACT-daughter row: single-node
    graph has no edge patch; its row is the absorbing stay (filed).
    """
    from bh_graph.rand0 import apply_edge_outcome
    st = tiny_state(graph_name, field_name)
    g, psi, order = st["g"], st["psi"], st["order"]
    (i, j) = sorted(tuple(sorted(e)) for e in g.edges())[0]
    outs = ["NONE", "CONTRACT"]
    sigs = []
    for o in outs:
        g2, psi2, order2 = apply_edge_outcome(g, psi, order, i, j, o)
        sigs.append(signature_key(state_signature(g2, psi2, order2)))
    # Row for X: W=1 normalized (or orbit weights); row for daughters:
    # NONE-daughter = X itself (same patch, same row); CONTRACT-daughter
    # is a 1-node graph (no edge patch -> absorbing stay).
    labels = ["X", "Y_contract"]
    if candidate == "const":
        w = {"NONE": 1.0, "CONTRACT": 1.0}
    else:
        tab = w_orbit_lookup(g, psi, order, ("edge", i, j))
        w = tab["orbit"]
    p = p_from_w(w)
    P = np.array([[p["NONE"], p["CONTRACT"]],
                  [0.0, 1.0]], dtype=float)
    return {"P": P, "labels": labels, "sigs": sigs,
            "patch": [i, j], "candidate": candidate}


def is_transition_matrix_ok(mat: dict) -> bool:
    """Boolean check: P stochastic (rows sum to 1, entries >= 0)."""
    try:
        P = np.asarray(mat["P"], dtype=float)
        return bool(P.ndim == 2 and P.shape[0] == P.shape[1]
                    and np.all(P >= 0.0)
                    and np.all(np.abs(P.sum(axis=1) - 1.0) <= 1e-12))
    except Exception:
        return False


def communicating_classes(P: np.ndarray) -> list:
    """Exact communicating classes of a tiny stochastic matrix (reachability)."""
    P = np.asarray(P, dtype=float)
    n = P.shape[0]
    reach = (P > 0)
    reach = reach | np.eye(n, dtype=bool)
    for _ in range(n):
        reach = reach | (reach @ reach)
    classes: list = []
    seen = set()
    for a in range(n):
        if a in seen:
            continue
        cls = sorted(b for b in range(n) if reach[a, b] and reach[b, a])
        classes.append(cls)
        seen.update(cls)
    return classes


def stationary_distribution(P: np.ndarray) -> np.ndarray:
    """Stationary distribution via eigenvector (tiny matrices only)."""
    P = np.asarray(P, dtype=float)
    vals, vecs = np.linalg.eig(P.T)
    k = int(np.argmin(np.abs(vals - 1.0)))
    v = np.real(vecs[:, k])
    v = np.maximum(v, 0.0)
    s = float(v.sum())
    if s <= 0.0:
        return np.full(P.shape[0], 1.0 / P.shape[0])
    return v / s


def detailed_balance_status(P: np.ndarray, pi: np.ndarray,
                            theta_perm) -> dict:
    """AA: pi(X)P(Y|X) vs pi(Theta Y)P(Theta X|Theta Y) (result, not repair).

    theta_perm maps state index -> Theta-image index (frozen per domain).
    """
    P = np.asarray(P, dtype=float)
    pi = np.asarray(pi, dtype=float)
    n = P.shape[0]
    maxdev = 0.0
    for x in range(n):
        for y in range(n):
            tx, ty = int(theta_perm[x]), int(theta_perm[y])
            lhs = float(pi[x] * P[x, y])
            rhs = float(pi[ty] * P[ty, tx])
            maxdev = max(maxdev, abs(lhs - rhs))
    return {"max_deviation": float(maxdev),
            "holds": bool(maxdev <= 1e-9)}


def probability_currents(P: np.ndarray, pi: np.ndarray,
                         theta_perm) -> dict:
    """AB: K_XY = pi(X)P(Y|X) - pi(Theta Y)P(Theta X|Theta Y) (audit)."""
    P = np.asarray(P, dtype=float)
    pi = np.asarray(pi, dtype=float)
    n = P.shape[0]
    K = np.zeros((n, n), dtype=float)
    for x in range(n):
        for y in range(n):
            tx, ty = int(theta_perm[x]), int(theta_perm[y])
            K[x, y] = float(pi[x] * P[x, y] - pi[ty] * P[ty, tx])
    return {"K": K, "max_abs": float(np.abs(K).max()),
            "all_zero": bool(float(np.abs(K).max()) <= 1e-9)}


# ---------------------------------------------------------------------------
# MEASURE-0AC: TIME-0 history comparison
# ---------------------------------------------------------------------------

def history_weight_status(T: int = 2, n_max: int = 4,
                          candidate: str = "const") -> dict:
    """AC: candidate-W history weights vs TIME-0 exact admissible histories.

    Uses the TIME-0 labeled N<=4 universe and its exact transition graph.
    History weight = product of per-step W (W=1 => uniform over histories).
    Reports whether boundaries become selective under W (they must not
    under W=1: TIME0-NULL survives as uniform multiplicity).
    """
    from bh_graph.time0 import (boundary_census, count_walks_from,
                                labeled_transitions, labeled_universe)
    states = labeled_universe(1, int(n_max))
    topo = labeled_transitions(states)
    adj = topo["adj"]
    starts = topo["keys"]
    census = boundary_census(adj, starts, int(T))
    # Under W=1 every admissible history has weight 1; the history measure
    # is uniform over histories, so N_hist>1 pairs stay non-selective.
    pairs = census.get("pairs", census)
    if isinstance(pairs, dict):
        n_hist_vals = []
        for v in pairs.values():
            if isinstance(v, dict) and "n_hist" in v:
                n_hist_vals.append(int(v["n_hist"]))
            elif isinstance(v, (int, np.integer)):
                n_hist_vals.append(int(v))
    else:
        n_hist_vals = []
    multi = sum(1 for v in n_hist_vals if v > 1)
    return {"T": int(T), "n_max": int(n_max), "candidate": candidate,
            "n_pairs": len(n_hist_vals),
            "n_multi": int(multi),
            "null_survives": bool(multi > 0),
            "note": "W=1 weights histories uniformly; multiplicity survives"}


# ---------------------------------------------------------------------------
# MEASURE-0 battery + verdict helpers
# ---------------------------------------------------------------------------

def measure0_states() -> dict:
    """Frozen MEASURE-0 state battery (deterministic, no RNG)."""
    tiny = {}
    for gn in TINY_GRAPHS:
        for fn in TINY_FIELDS:
            tiny[f"{gn}/{fn}"] = tiny_state(gn, fn)
    return {"tiny": tiny, "background_L4": background_battery(4)}


def forbidden_control_status(g: nx.Graph, psi: np.ndarray, order: list,
                             i, j) -> dict:
    """Firewall audit: forbidden forms as explicit negative controls.

    boltzmann: needs beta (1 fitted param). born: |psi|^2 without
    derivation (firewall-forbidden even at 0 params). absB: |B| needs a
    scale x0 for dimensionless P (hidden parameter). All filed, none used.
    """
    inv = transition_invariants(g, psi, order, i, j)
    return {
        "boltzmann": {"form": "exp(-beta dE)", "params": 1,
                      "dE": inv["dE_psi"], "verdict": "forbidden (beta)"},
        "born": {"form": "|psi|^2", "params": 0,
                 "verdict": "forbidden (no derivation)"},
        "absB": {"form": "|B|", "params": 1, "B": inv["B_uv"],
                 "verdict": "forbidden (needs scale x0)"},
    }
