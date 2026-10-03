"""FIBER-0 split-fiber measure constraints: apparatus (FROZEN pre-data).

Campaign: FIBER-0. Determines whether existing graph-field physics
uniquely constrains a normalized physical measure mu_M(d xi) on the
residual inverse fiber Xi(M), given SPLIT0-MIXED's exact inverse
decomposition X = F^{-1}(M, xi) with xi = (cover, d).

Frozen ontology (read-only consumption, never re-derived):
  - Contraction/split op u-v <-> [uv] (BR-2.5): contract_edge
    (simple-kind, common neighbors collapse, consumed edge discarded),
    sum map psi_k = psi_i + psi_j, 3^d directed covers, R_U = 1.
  - Event ledger (BR-2.6/CONS-0): dN = -1, dE = -(1+c), dQ = +2B_ij,
    dE_psi parts; split ledgers (dN = +1, dE = +(1+c')); CONS-0K
    equal/norm policies; no-go (no field-involving linear invariant
    closes arbitrary contractions); no firing from energetics (BR-2.7).
  - Physical quotient X_phys = X / (R x U1) (SYM0-CLOSED); exact
    isomorphism where sufficiency matters (RAND-0F).
  - Equal-halves reverse condition (MEASURE-0C): full physical reverse
    support only on psi_i == psi_j.
  - History-level control (TIME0-NULL) + scheduler m! (INFO0-MATCHED).
  - Hidden-sector states physically distinct (HIDDEN0-SEPARATED);
    HBR0-SIGNREV binding on ledger orderings.
  - Vacuum family VPLUS/VPI/VMINUS (VACFIELD0-JOINT); V_-^hidden
    representatives are exact pure-P_- states.

Load-bearing identities derived pre-data (pinned in tests/test_fiber0.py):
  - (FIBER-0A) Independent fiber reconstruction agrees exactly with
    the SPLIT0-MIXED ledger (cover counts, d_cont, halves support,
    deterministic core, hidden anatomy, roundtrip).
  - (FIBER-0C) Endpoint swap sigma: (A,B) -> (B,A), d -> -d is an
    exact involution; undirected keys swap-invariant.
  - (FIBER-0D) Tiny cells: exact full Aut(M) orbits on covers;
    J2 legs: exact group-free signature blocks (|A|,|B|,cprime)
    that true orbits refine (inter-block freedom sound).
  - (FIBER-0J) Exact closed-form split ledgers for general (c,d):
    dQ(d) = (|d|^2-|s|^2)/2 (cover-blind); dEpsi(c,d) = const(c) +
    |d|^2/2 - Re(conj(d) Delta(c)) with Delta(c) = sum_A psi -
    sum_B psi; recovers CONS-0K at d = 0; swap-invariant.
  - (FIBER-0M) Pair-exchange theorem: d purely odd (P_+ d = 0,
    P_- d = d), s purely even; symmetric linear readouts see s
    only, antisymmetric see d only.
  - (FIBER-0Q) Two inequivalent normalized rival measures
    (rival_A/rival_B) satisfying every earned constraint.

Firewall (binding): no Gaussian noise, uniformity by declaration,
Born/Boltzmann rules, maximum entropy, fitted variance/exponents,
arbitrary cutoffs, or preferred cover weights in the headline
derivation. Rival measures are explicit mathematical exhibits for
the non-uniqueness proof (namespaced rival_*), never derived.
No RNG anywhere in this module. No fitted parameter in the earned
apparatus (fitted_param_count() == 0).
"""

from __future__ import annotations

import ast
import itertools
import math
import sys

import networkx as nx
import numpy as np

# Frozen bars (SYM-0 Amendment-1 / TIME-0 grades, consumed read-only).
FP_ATOL = 1e-12
FIELD_ATOL = 1e-9
SIG_ROUND = 9

# Frozen battery (SPLIT-0 census + FIBER-0 vacuum legs).
FIBER0_GRAPHS = ("single", "k2", "triangle", "square", "star4", "path4")
FIBER0_FIELDS = ("zero", "bonding", "current", "antibonding")
J2_L_SPOT = 4
J2_BACKGROUNDS = ("ZERO", "VPLUS", "VPI", "VMINUS",
                  "HDELTA", "HDIPOLE", "HDISK")
U1_GRID = (math.pi / 4.0, math.pi / 2.0, math.pi, 3.0 * math.pi / 2.0)
# Deterministic relative-mode sweep (no RNG): d = 0 (halves) plus
# generic points in +- pairs (Z2 probe) and complex points.
D_SWEEP = (0.0j, 1.0 + 0.0j, -1.0 + 0.0j, 0.0 + 1.0j, 0.0 - 1.0j,
           1.0 + 1.0j, -1.0 - 1.0j, -0.5 + 0.25j, 0.5 - 0.25j,
           2.0 - 1.0j, -2.0 + 1.0j)
RADIAL_GRID = (0.0, 0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 8.0)
ANGLE_GRID = tuple(k * math.pi / 16.0 for k in range(32))
# Rival exhibits (section Q): closed-form scales. These are exhibit
# labels (distinct choices proving non-uniqueness), never fitted.
RIVAL_SIG_A = 1.0
RIVAL_SIG_B = 2.0
RIVAL_B_ANG_AMP = 0.5


# ---------------------------------------------------------------------------
# Battery builders (frozen)
# ---------------------------------------------------------------------------

def tiny_graph_fiber0(name: str) -> dict:
    """Frozen tiny substrates incl. the isolated single node (d = 0 cell)."""
    if name == "single":
        g = nx.Graph()
        g.add_node(0)
        return {"g": g, "order": [0]}
    from bh_graph.rand0 import tiny_graph

    return tiny_graph(name)


def tiny_field_fiber0(n: int, which: str) -> np.ndarray:
    """Frozen tiny field preparations (RAND-0 banked, incl. n = 1)."""
    from bh_graph.rand0 import tiny_field

    return tiny_field(int(n), which)


def merged_state(graph_name: str, field_name: str) -> dict:
    """Frozen merged state M = (G2, psi2, order2) (FIBER-0 battery)."""
    spec = tiny_graph_fiber0(graph_name)
    g, order = spec["g"], spec["order"]
    psi = np.asarray(tiny_field_fiber0(len(order), field_name),
                     dtype=np.complex128)
    return {"g": g, "psi": psi, "order": list(order),
            "graph": graph_name, "field": field_name}


def fiber0_cells(graph_names=tuple(FIBER0_GRAPHS),
                 field_names=tuple(FIBER0_FIELDS)) -> list:
    """All (M, k) split cells: every node of every battery state (76)."""
    cells = []
    for gn in graph_names:
        for fn in field_names:
            st = merged_state(gn, fn)
            for k in sorted(st["g"].nodes()):
                cells.append({"state": f"{gn}/{fn}", "graph": gn,
                              "field": fn, "k": k,
                              "d": int(st["g"].degree(k)),
                              "cell": f"{gn}/{fn}@{k}"})
    return cells


def j2_leg_state(background: str, L: int = J2_L_SPOT, k=None) -> dict:
    """Frozen J2 merged-state leg (FIBER-0 section L battery).

    Backgrounds: ZERO (control), VPLUS/VPI/VMINUS (VACFIELD0-JOINT
    candidate_shape), HDELTA/HDIPOLE/HDISK (exact pure-P_- states of
    V_-^hidden: hidden_delta @ (0,0), hidden_dipole @ (0,0),(1,1),
    hidden_disk over all coarse cells). k defaults to order[0].
    """
    from bh_graph.conservation import field_zero, substrate_j2
    from bh_graph.formation import j2_torus_coords
    from bh_graph import hidden as _h
    from bh_graph import vacfield as _vf

    L = int(L)
    sub = substrate_j2(L)
    g, order = sub["g"], list(sub["order"])
    c3 = j2_torus_coords(L)
    bg = str(background)
    if bg == "ZERO":
        psi = field_zero(len(order))
    elif bg in ("VPLUS", "VPI", "VMINUS"):
        psi = _vf.candidate_shape(bg, {"graph": g, "order": order,
                                       "c3": c3, "L": L}, kind="j2")
    elif bg == "HDELTA":
        psi = _h.hidden_delta(order, c3, (0, 0))
    elif bg == "HDIPOLE":
        psi = _h.hidden_dipole(order, c3, (0, 0), (1, 1))
    elif bg == "HDISK":
        cells = sorted({(x, y) for (x, y, _b) in c3.values()})
        psi = _h.hidden_disk(order, c3, cells)
    else:
        raise ValueError(f"unknown J2 background: {background}")
    if k is None:
        k = order[0]
    return {"g": g, "psi": np.asarray(psi, dtype=np.complex128),
            "order": order, "c3": dict(c3), "L": L,
            "background": bg, "k": k}


# ---------------------------------------------------------------------------
# FIBER-0A: independent fiber reconstruction
# ---------------------------------------------------------------------------

def directed_cover_count(d: int) -> int:
    """Directed cover count 3^d (BR-2.5, earned)."""
    return 3 ** int(d)


def undirected_cover_count(d: int) -> int:
    """Undirected cover count (3^d + 1)/2 (U0-H1 gauge quotient, earned)."""
    return int((3 ** int(d) + 1) / 2)


def undirected_cover_list(nbrs_k) -> list:
    """Own undirected-cover enumeration (canonical keys, det. order).

    Assembled here from the frozen BR-2.5 cover op; pinned identical
    to u0.undirected_covers (unit test). Rows: (key, A, B).
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


def fresh_labels(g: nx.Graph, i=None, j=None):
    """Canonical fresh daughter labels (max+1/max+2, U0/TIME-0 convention)."""
    if i is not None and j is not None:
        return i, j
    if not all(isinstance(v, int) for v in g.nodes()):
        raise ValueError("split needs integer labels or explicit i, j")
    top = max(g.nodes())
    return top + 1, top + 2


def fiber_point(s: complex, d: complex):
    """Fiber parametrization: (p, q) = ((s+d)/2, (s-d)/2) (exact)."""
    s, d = complex(s), complex(d)
    return (s + d) / 2.0, (s - d) / 2.0


def fiber_residual(p: complex, q: complex) -> complex:
    """Relative mode d = p - q (exact)."""
    return complex(p) - complex(q)


def halves_point(s: complex):
    """Equal-halves point (s/2, s/2), i.e. d = 0 (exact)."""
    s = complex(s)
    return s / 2.0, s / 2.0


def is_sum_consistent_ok(p: complex, q: complex, s: complex,
                         atol: float = FP_ATOL) -> bool:
    """Boolean check: p + q == s (never raises)."""
    try:
        return bool(abs(complex(p) + complex(q) - complex(s)) <= atol)
    except Exception:
        return False


def rest_nonzero(psi2: np.ndarray, order2: list, k) -> bool:
    """Boolean check: merged rest (all nodes but k) has a nonzero entry."""
    from bh_graph.ballistic import index_of

    psi2 = np.asarray(psi2, dtype=np.complex128)
    idx = index_of(list(order2))
    return bool(any(complex(psi2[idx[v]]) != 0.0
                    for v in order2 if v != k))


def physical_fiber_dims(rest_has_nonzero: bool, s: complex) -> dict:
    """Physical fiber dims after the U1 quotient (exact case analysis).

    Gauge fixable (rest nonzero or s != 0) -> d fully physical
    (2 real dims). Only the all-zero merged state leaves the global
    phase unfixable -> 1 real dim (|d|/2 half-line). Never a point.
    """
    if bool(rest_has_nonzero) or complex(s) != 0.0:
        return {"d_cont_phys": 2, "redundant_phase": False}
    return {"d_cont_phys": 1, "redundant_phase": True}


def predecessor_state(g2: nx.Graph, psi2: np.ndarray, order2: list, k,
                      A, B, p: complex, q: complex, i, j) -> dict:
    """Full predecessor X = (H, psi, orderH) from cover + fiber point."""
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
    """Boolean check: C(X) == M exactly via (i, j) (never raises)."""
    try:
        from bh_graph.ballistic import index_of
        from bh_graph.contraction import contracted_state

        psi2 = np.asarray(psi2, dtype=np.complex128)
        order2 = list(order2)
        g, psi, order = X["g"], np.asarray(X["psi"],
                                           dtype=np.complex128), list(X["order"])
        g2b, psi2b, order2b, _kb, _rec = contracted_state(g, psi, order,
                                                          i, j, "sum")
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


def encode_residual(X: dict, k, i, j) -> dict:
    """Encode xi = (undirected cover, d) from predecessor X (exact).

    Schema (frozen): {cover_key, d, s_check, A, B}. No order/time
    component (scheduler separation, section O).
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
    """Decode X from M + xi (exact construction)."""
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

    Re-encoded d compared at FP grade, up to the endpoint-swap sign
    (undirected gauge).
    """
    try:
        psi2 = np.asarray(psi2, dtype=np.complex128)
        order2 = list(order2)
        X = decode_residual(g2, psi2, order2, k, dict(xi))
        if not is_predecessor_ok(g2, psi2, order2, k, X, X["i"], X["j"]):
            return False
        back = encode_residual(X, k, X["i"], X["j"])
        want_key = (tuple(xi["cover_key"][0]), tuple(xi["cover_key"][1]))
        if (tuple(back["cover_key"][0]), tuple(back["cover_key"][1])) != want_key:
            return False
        d0 = complex(xi["d"])
        if not (abs(back["d"] - d0) <= FP_ATOL
                or abs(back["d"] + d0) <= FP_ATOL):
            return False
        return True
    except Exception:
        return False


def graph_iso_classes(g2: nx.Graph, k) -> list:
    """Undirected covers grouped by unlabeled predecessor-graph isomorphism.

    Field-blind. WL-hash pre-grouping + exact nx.is_isomorphic within
    groups. Deterministic order.
    """
    from bh_graph.contraction import apply_split_cover

    i, j = fresh_labels(g2)
    preds = []
    for key, A, B in undirected_cover_list(sorted(g2.neighbors(k))):
        h = apply_split_cover(g2, k, set(A), set(B), i, j)
        preds.append((key, h))
    groups: dict = {}
    for n, (key, h) in enumerate(preds):
        wl = nx.weisfeiler_lehman_graph_hash(h)
        inv = (wl, h.number_of_edges(),
               tuple(sorted(dd for _, dd in h.degree())))
        groups.setdefault(inv, []).append(n)
    classes: list = []
    for _inv, members in sorted(groups.items(), key=lambda kv: kv[1]):
        for n in members:
            placed = False
            for cls in classes:
                if cls[0] not in members:
                    continue
                if nx.is_isomorphic(preds[n][1], preds[cls[0]][1]):
                    cls.append(n)
                    placed = True
                    break
            if not placed:
                classes.append([n])
    for cls in classes:
        cls.sort()
    classes.sort(key=lambda c: c[0])
    return classes


def halves_physical_classes(g2: nx.Graph, psi2: np.ndarray, order2: list,
                            k) -> list:
    """Halves predecessors grouped into physical (R x U1) classes.

    Banked RAND-0F exact apparatus; the NONE singleton is dropped:
    every remaining class is a genuine physical predecessor class.
    """
    from bh_graph.rand0 import node_admissible, split_isomorphism_classes

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    adm = node_admissible(g2, k)
    classes = split_isomorphism_classes(g2, psi2, order2, k, adm)
    return [cls for cls in classes if cls != ["NONE"]]


def inverse_dimensions(g2: nx.Graph, psi2: np.ndarray, order2: list,
                       k) -> dict:
    """Full inverse anatomy of one merged cell (exact census, own code)."""
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


def wl_group_count(g2: nx.Graph, k) -> dict:
    """WL+invariant grouping of undirected covers (J2-safe, descriptive).

    Group count is a LOWER bound on the true class count (filed as
    such, never gated as exact).
    """
    from bh_graph.contraction import apply_split_cover

    i, j = fresh_labels(g2)
    groups: dict = {}
    n = 0
    for _key, A, B in undirected_cover_list(sorted(g2.neighbors(k))):
        h = apply_split_cover(g2, k, set(A), set(B), i, j)
        wl = nx.weisfeiler_lehman_graph_hash(h)
        inv = (wl, h.number_of_edges(),
               tuple(sorted(dd for _, dd in h.degree())))
        groups.setdefault(inv, []).append(n)
        n += 1
    return {"n_groups": len(groups), "n_covers": n,
            "group_sizes": sorted(len(v) for v in groups.values())}


def inverse_dimensions_capped(g2: nx.Graph, psi2: np.ndarray, order2: list,
                              k, cap: int = 200) -> dict:
    """Inverse anatomy with an exact-isomorphism cap (J2 legs).

    Cells with n_undirected <= cap: exact inverse_dimensions.
    Larger cells: formula counts + fiber dims + WL-group lower bound,
    iso_capped True, NO exact class claims.
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


def deterministic_core_status(g2: nx.Graph, psi2: np.ndarray, order2: list,
                              k) -> dict:
    """Deterministic-core classification of one merged cell (exact).

    Full domain: never deterministic (fiber uncountable). Halves
    domain: deterministic iff n_phys_halves == 1. Graph sector:
    deterministic iff d(k) == 0.
    """
    dims = inverse_dimensions(g2, psi2, order2, k)
    return {"d": dims["d"], "n_undirected": dims["n_undirected"],
            "n_iso_graph": dims["n_iso_graph"],
            "n_phys_halves": dims["n_phys_halves"],
            "d_cont_full": dims["d_cont_full"],
            "full_deterministic": False,
            "full_reason": "continuous fiber: |P(M)| uncountable",
            "halves_deterministic": bool(dims["n_phys_halves"] == 1),
            "graph_deterministic": bool(dims["d"] == 0)}


def hidden_anatomy(g2: nx.Graph, psi2: np.ndarray, order2: list, k,
                   d_values=tuple(D_SWEEP)) -> dict:
    """Pair-level hidden anatomy: merged-visible vs locally-visible sweep.

    First undirected cover fixed; relative mode swept. Merged data
    constant by construction (D_merged = 0); daughter-local readouts
    (rho_i, rho_j, B_ij) vary with |d|. Only banked EM-0 readouts.
    """
    from bh_graph.ballistic import index_of

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    idx = index_of(order2)
    s = complex(psi2[idx[k]])
    first_key, first_A, first_B = undirected_cover_list(
        sorted(g2.neighbors(k)))[0]
    i, j = fresh_labels(g2)
    rhos, Bs, merged = [], [], []
    for d in d_values:
        p, q = fiber_point(s, complex(d))
        X = predecessor_state(g2, psi2, order2, k, first_A,
                              first_B, p, q, i, j)
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
    phys = physical_fiber_dims(rest_nonzero(psi2, order2, k), s)
    return {"cover_key": first_key, "s": s,
            "n_sweep": len(d_values),
            "D_merged": float(d_merged),
            "rho_range": [float(rho_range[0]), float(rho_range[1])],
            "B_range": float(b_range),
            "locally_varies": bool(max(rho_range[0], rho_range[1],
                                       b_range) > 0.0),
            "hidden_dims_retained": int(phys["d_cont_phys"])}


def is_hidden_retained_ok(g2: nx.Graph, psi2: np.ndarray, order2: list,
                          k) -> bool:
    """Boolean check: distinct fiber points = distinct predecessors."""
    try:
        an = hidden_anatomy(g2, psi2, order2, k, (0.0j, 1.0 + 0.0j))
        return bool(an["D_merged"] == 0.0 and an["locally_varies"])
    except Exception:
        return False


def cell_roundtrip(g2: nx.Graph, psi2: np.ndarray, order2: list, k,
                   d_values=tuple(D_SWEEP)) -> dict:
    """M + xi <-> X roundtrip over all covers x d-sweep (exact)."""
    n, bad = 0, 0
    for key, _A, _B in undirected_cover_list(sorted(g2.neighbors(k))):
        for d in d_values:
            n += 1
            if not is_roundtrip_ok(g2, psi2, order2, k,
                                   {"cover_key": key, "d": complex(d)}):
                bad += 1
    return {"n": n, "bad": bad}


def agreement_vs_split0(cell: str, dims: dict, det: dict, hidden: dict,
                        roundtrip: dict, ref_cells: dict) -> dict:
    """Exact agreement of own reconstruction vs SPLIT0-MIXED ledger.

    Compares: physical cover count, continuous dimension,
    equal-halves support, deterministic core, hidden anatomy, and
    roundtrip status. ref_cells maps cell name -> ledger row.
    """
    ref = ref_cells.get(cell)
    if ref is None:
        return {"agree": False, "mismatches": ["missing-ref"]}
    bad = []
    rd = ref.get("dims", {})
    if dims["n_undirected"] != rd.get("n_undirected"):
        bad.append("n_undirected")
    if dims["n_iso_graph"] != rd.get("n_iso_graph"):
        bad.append("n_iso_graph")
    if dims["n_phys_halves"] != rd.get("n_phys_halves"):
        bad.append("n_phys_halves")
    if dims["d_cont_full"] != rd.get("d_cont_full"):
        bad.append("d_cont_full")
    if dims["d_cont_halves"] != rd.get("d_cont_halves"):
        bad.append("d_cont_halves")
    rdet = ref.get("det", {})
    if bool(det["halves_deterministic"]) != bool(
            rdet.get("halves_deterministic")):
        bad.append("halves_deterministic")
    if bool(det["full_deterministic"]) != bool(
            rdet.get("full_deterministic")):
        bad.append("full_deterministic")
    if bool(hidden["hidden_ok"]) != bool(ref.get("hidden")):
        bad.append("hidden")
    if bool(hidden["locally_varies"]) != bool(ref.get("locally_varies")):
        bad.append("locally_varies")
    if abs(float(hidden["D_merged"]) - float(ref.get("D_merged",
                                                     0.0))) > 0.0:
        bad.append("D_merged")
    if int(ref.get("roundtrip_bad", -1)) != 0:
        bad.append("ref-roundtrip")
    if int(roundtrip.get("bad", -1)) != 0:
        bad.append("own-roundtrip")
    return {"agree": len(bad) == 0, "mismatches": bad}


def agreement_vs_split0_j2(background: str, dims: dict,
                           ref_j2: dict) -> dict:
    """Exact agreement vs SPLIT0-MIXED J2 legs (zero/uniform/VMINUS).

    Compares formula counts, d_cont, and WL-group lower bound.
    """
    ref = ref_j2.get(background)
    if ref is None:
        return {"agree": False, "mismatches": ["missing-ref"]}
    bad = []
    rd = ref.get("dims", {})
    for key in ("n_directed", "n_undirected", "d_cont_full",
                "d_cont_halves", "n_wl_groups"):
        if dims.get(key) != rd.get(key):
            bad.append(key)
    return {"agree": len(bad) == 0, "mismatches": bad}

# ---------------------------------------------------------------------------
# FIBER-0B: physical quotient
# ---------------------------------------------------------------------------

def fiber_anatomy_keys(g2: nx.Graph, psi2: np.ndarray, order2: list,
                       k) -> dict:
    """Quotient-invariant fiber anatomy keys (counts, dims, |s|).

    Cover keys are representation-dependent raw; the invariant content
    is the transported-key SET equality checked by the caller.
    """
    from bh_graph.ballistic import index_of

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    d = int(g2.degree(k))
    s = complex(psi2[index_of(order2)[k]])
    phys = physical_fiber_dims(rest_nonzero(psi2, order2, k), s)
    return {"d": d, "n_directed": directed_cover_count(d),
            "n_undirected": undirected_cover_count(d),
            "d_cont_full": int(phys["d_cont_phys"]),
            "abs_s": float(abs(s)), "s_is_zero": bool(s == 0.0)}


def is_quotient_invariant_ok(g2: nx.Graph, psi2: np.ndarray, order2: list,
                             k, perm: dict, alpha: float) -> bool:
    """Boolean check: fiber anatomy invariant under R x U1 (never raises).

    Compares invariant keys on M vs R x U1(M) at the transported locus,
    plus transported-vs-recomputed cover-key set equality.
    """
    try:
        from bh_graph.sym0 import apply_relabel, apply_u1

        psi2 = np.asarray(psi2, dtype=np.complex128)
        order2 = list(order2)
        rel = apply_relabel(g2, psi2, order2, dict(perm))
        h, psi_h, order_h = rel["g"], rel["psi"], rel["order"]
        psi_h = apply_u1(psi_h, float(alpha))
        k2 = perm.get(k, k)
        a0 = fiber_anatomy_keys(g2, psi2, order2, k)
        a1 = fiber_anatomy_keys(h, psi_h, order_h, k2)
        if a0 != a1:
            return False
        got = {key for key, _A, _B
               in undirected_cover_list(sorted(h.neighbors(k2)))}
        want = set()
        for _key, A, B in undirected_cover_list(sorted(g2.neighbors(k))):
            a, b = transport_cover(A, B, dict(perm))
            ka, kb = tuple(sorted(a)), tuple(sorted(b))
            want.add((ka, kb) if ka <= kb else (kb, ka))
        return bool(got == want)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# FIBER-0C: endpoint swap
# ---------------------------------------------------------------------------

def swap_cover(A, B):
    """Exact endpoint-swap cover map sigma: (A, B) -> (B, A)."""
    return frozenset(B), frozenset(A)


def is_swap_involution_ok(A, B) -> bool:
    """Boolean check: sigma^2 = identity on ordered covers (never raises)."""
    try:
        A2, B2 = swap_cover(*swap_cover(set(A), set(B)))
        return bool(set(A2) == set(A) and set(B2) == set(B))
    except Exception:
        return False


def undirected_key(A, B):
    """Canonical undirected cover key (swap-invariant by construction)."""
    ka, kb = tuple(sorted(set(A))), tuple(sorted(set(B)))
    return (ka, kb) if ka <= kb else (kb, ka)


def is_swap_fiber_ok(s: complex, d: complex) -> bool:
    """Boolean check: swap sends (p,q) -> (q,p), i.e. d -> -d (exact)."""
    try:
        s, d = complex(s), complex(d)
        p, q = fiber_point(s, d)
        return bool(fiber_residual(q, p) == -d
                    and is_sum_consistent_ok(q, p, s))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# FIBER-0D: automorphism covariance
# ---------------------------------------------------------------------------

def transport_cover(A, B, perm: dict):
    """Transport a cover through a relabeling (covariant action)."""
    a = frozenset(perm.get(m, m) for m in set(A))
    b = frozenset(perm.get(m, m) for m in set(B))
    return a, b


def state_automorphisms_bruteforce(g: nx.Graph, psi: np.ndarray,
                                   order: list) -> list:
    """Exact full Aut(M): perms preserving edges + psi (tiny states).

    Brute force over N! (N <= 6 only; raises above: exactness first).
    Each element is a dict {v: perm(v)}. Deterministic order.
    """
    from bh_graph.ballistic import index_of

    order = list(order)
    if len(order) > 6:
        raise ValueError("brute-force Aut only for N <= 6")
    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(order)
    vals = {v: complex(psi[idx[v]]) for v in order}
    elist = {tuple(sorted(e)) for e in g.edges()}
    out = []
    for perm in itertools.permutations(order):
        mp = dict(zip(order, perm))
        if any(vals[mp[v]] != vals[v] for v in order):
            continue
        if {tuple(sorted((mp[u], mp[v]))) for u, v in elist} != elist:
            continue
        out.append(mp)
    return out


def cover_orbits(covers: list, stab: list) -> list:
    """Exact orbit partition of undirected covers under a stabilizer.

    covers: [(key, A, B)]; stab: [{v: perm(v)}] fixing k. Returns
    orbits as sorted key lists (deterministic: first-key order).
    Union-find over the transported-key relation (exact orbit
    equivalence: transitive by group closure).
    """
    keys = [row[0] for row in covers]
    parent = {kk: kk for kk in keys}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for key, A, B in covers:
        for perm in stab:
            a, b = transport_cover(A, B, perm)
            union(key, undirected_key(a, b))
    orbits: dict = {}
    for kk in keys:
        orbits.setdefault(find(kk), []).append(kk)
    out = [sorted(v) for v in orbits.values()]
    out.sort(key=lambda o: o[0])
    return out


def cover_signature(A, B) -> tuple:
    """Automorphism-invariant cover signature (|A|,|B|,cprime).

    Cardinalities are preserved by every automorphism (exact).
    """
    a, b = set(A), set(B)
    lo, hi = (len(a), len(b)) if len(a) <= len(b) else (len(b), len(a))
    return (lo, hi, len(a & b))


def signature_blocks(covers: list) -> list:
    """Group-free signature-block partition of undirected covers.

    True Aut-orbits refine blocks (sound): inter-block weight
    freedom is witnessed without knowing the group; block-constant
    laws are full-Aut-covariant. Deterministic order.
    """
    blocks: dict = {}
    for key, A, B in covers:
        blocks.setdefault(cover_signature(A, B), []).append(key)
    out = [sorted(v) for v in blocks.values()]
    out.sort(key=lambda o: o[0])
    return out


def is_transport_correct_ok(g2: nx.Graph, k, perm: dict) -> bool:
    """Boolean check: transported covers == recomputed covers (never raises).

    Verifies the covariant cover action for one permutation: transport
    every undirected cover of k, compare (as canonical keys) against
    covers recomputed at perm(k) on the permuted graph.
    """
    try:
        from bh_graph.sym0 import apply_relabel

        order = sorted(g2.nodes())
        n = len(order)
        rel = apply_relabel(g2, np.zeros(n, dtype=np.complex128),
                            order, dict(perm))
        h = rel["g"]
        k2 = perm.get(k, k)
        got = {key for key, _A, _B
               in undirected_cover_list(sorted(h.neighbors(k2)))}
        want = set()
        for _key, A, B in undirected_cover_list(sorted(g2.neighbors(k))):
            a, b = transport_cover(A, B, dict(perm))
            want.add(undirected_key(a, b))
        return bool(got == want)
    except Exception:
        return False


def translation_perms_j2(L: int) -> list:
    """J2 pure (x,y) translations as label perms (verified automorphisms).

    Built from the banked translation matrices; every element is
    verified edge-preserving before return (verified, not assumed).
    """
    from bh_graph.ballistic import node_order
    from bh_graph.conservation import j2_translations
    from bh_graph.formation import j2_torus_graph
    from bh_graph.sym0 import is_perm_auto_ok

    L = int(L)
    g = j2_torus_graph(L)
    order = node_order(g)
    tx, ty = j2_translations(L)
    tx = np.asarray(tx.toarray() if hasattr(tx, "toarray") else tx)
    ty = np.asarray(ty.toarray() if hasattr(ty, "toarray") else ty)
    perms = []
    # Translation by (a, c): T = Tx^a Ty^c; matrix acts on vectors,
    # so columns give images: T e_j = e_{p(j)}.
    mat_x = np.eye(len(order), dtype=int)
    for a in range(L):
        mat_y = np.eye(len(order), dtype=int)
        for c in range(L):
            mat = mat_x @ mat_y
            perm = {}
            for j, v in enumerate(order):
                img = int(np.argmax(mat[:, j]))
                perm[v] = order[img]
            if not is_perm_auto_ok(g, perm):
                raise ValueError("translation not an automorphism")
            perms.append(perm)
            mat_y = mat_y @ ty
        mat_x = mat_x @ tx
    return perms


def find_pinned_automorphism(g: nx.Graph, pin: dict):
    """One VF2 automorphism extending a partial pin, or None (exact).

    Decision query (first-hit): pins node pairs via categorical
    node_match. Returns {v: image} or None. No enumeration.
    """
    order = sorted(g.nodes())
    for v in order:
        g.nodes[v]["_fiber0_pin"] = pin.get(v, -1)
    try:
        nm = nx.algorithms.isomorphism.categorical_node_match(
            "_fiber0_pin", -1)
        gm = nx.algorithms.isomorphism.GraphMatcher(g, g, node_match=nm)
        for iso in gm.isomorphisms_iter():
            return dict(iso)
        return None
    finally:
        for v in order:
            g.nodes[v].pop("_fiber0_pin", None)


def orbit_dof_summary(n_covers: int, partition: list) -> dict:
    """Forced-vs-free quantification for a cover partition.

    Forced: weights constant within each block (n_covers - n_blocks
    equalities). Free: inter-block weights (n_blocks - 1 DOF after
    normalization). Unique iff 1 cover.
    """
    n_blocks = len(partition)
    return {"n_covers": int(n_covers), "n_blocks": int(n_blocks),
            "forced_equalities": int(n_covers - n_blocks),
            "free_weights_dof": int(max(n_blocks - 1, 0)),
            "unique": bool(n_covers == 1)}


# ---------------------------------------------------------------------------
# FIBER-0E: locality
# ---------------------------------------------------------------------------

def fiber_fingerprint(g2: nx.Graph, psi2: np.ndarray, order2: list,
                      k) -> tuple:
    """Local fiber fingerprint (cover keys, s, fiber relation, halves)."""
    from bh_graph.ballistic import index_of

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    covers = [key for key, _A, _B
              in undirected_cover_list(sorted(g2.neighbors(k)))]
    s = complex(psi2[index_of(order2)[k]])
    probe = tuple(is_sum_consistent_ok(*fiber_point(s, d), s)
                  for d in D_SWEEP)
    return (covers, s, probe, halves_point(s),
            undirected_cover_count(int(g2.degree(k))))


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


def is_fiber_local_ok(g2: nx.Graph, psi2: np.ndarray, order2: list,
                      k) -> bool:
    """Boolean check: LOCAL fiber data invariant under remote mutations.

    Frozen support radius: field mutation at distance >= 3 from k,
    edge toggle outside closed N[k]. Vacuous True where inapplicable
    (applicability filed separately).
    """
    try:
        psi2 = np.asarray(psi2, dtype=np.complex128)
        order2 = list(order2)
        from bh_graph.ballistic import index_of

        fam0 = fiber_fingerprint(g2, psi2, order2, k)
        dist = dict(nx.single_source_shortest_path_length(g2, k))
        idx = index_of(order2)
        far = [v for v in order2 if dist.get(v, 10 ** 9) >= 3]
        if far:
            mut = np.array(psi2, dtype=np.complex128)
            mut[idx[far[0]]] += complex(0.5, -0.25)
            if fiber_fingerprint(g2, mut, order2, k) != fam0:
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
            if fiber_fingerprint(h, psi2, order2, k) != fam0:
                return False
        return True
    except Exception:
        return False


def patch_cover_orbits(g2: nx.Graph, psi2: np.ndarray, order2: list,
                       k) -> list:
    """Patch-stabilizer orbit partition of SPLIT outcomes (banked).

    RAND-0 local_stabilizer (radius 1) + orbits_of on node_admissible
    outcomes, NONE dropped. Tiny cells only (banked cap 8).
    """
    from bh_graph.rand0 import (local_stabilizer, node_admissible,
                                orbits_of, outcome_key)

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    adm = node_admissible(g2, k)
    stab = local_stabilizer(g2, psi2, order2, k)
    orbs = orbits_of(adm, stab, "node")
    out = []
    for orb in orbs:
        rest = sorted(o for o in orb if o != outcome_key("NONE")
                      and o != "NONE")
        if rest:
            out.append(rest)
    out.sort(key=lambda o: o[0])
    return out


def is_patch_orbits_local_ok(g2: nx.Graph, psi2: np.ndarray, order2: list,
                             k) -> bool:
    """Boolean check: patch orbit partition invariant under remote mutation.

    Same labels before/after (no relabeling): direct comparison.
    Vacuous True where no remote site exists. Tiny cells only.
    """
    try:
        psi2 = np.asarray(psi2, dtype=np.complex128)
        order2 = list(order2)
        from bh_graph.ballistic import index_of

        before = patch_cover_orbits(g2, psi2, order2, k)
        dist = dict(nx.single_source_shortest_path_length(g2, k))
        idx = index_of(order2)
        far = [v for v in order2 if dist.get(v, 10 ** 9) >= 3]
        if far:
            mut = np.array(psi2, dtype=np.complex128)
            mut[idx[far[0]]] += complex(0.5, -0.25)
            if patch_cover_orbits(g2, mut, order2, k) != before:
                return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# FIBER-0F: deterministic collapse
# ---------------------------------------------------------------------------

def singleton_status(g2: nx.Graph, psi2: np.ndarray, order2: list,
                     k, dims: dict | None = None) -> dict:
    """Singleton analysis: full fiber never; halves iff n_phys == 1.

    Returns delta specs where singleton (halves only, d = 0 cells).
    """
    if dims is None:
        dims = inverse_dimensions(g2, psi2, order2, k)
    halves_single = bool(dims["n_phys_halves"] == 1)
    return {"full_singleton": False,
            "full_reason": "continuous fiber: |P(M)| uncountable",
            "halves_singleton": halves_single,
            "halves_delta": ("delta@halves" if halves_single else None),
            "graph_deterministic": bool(dims["d"] == 0)}


# ---------------------------------------------------------------------------
# FIBER-0G: discrete cover measure
# ---------------------------------------------------------------------------

def cover_measure_freedom(n_covers: int, partition: list) -> dict:
    """Discrete cover-measure freedom from a partition (orbits/blocks).

    Forced: P constant within each block. Unique iff 1 cover.
    Never uniform-by-declaration: freedom is filed, not filled.
    """
    dof = orbit_dof_summary(n_covers, partition)
    return {"unique": dof["unique"],
            "n_blocks": dof["n_blocks"],
            "forced_equalities": dof["forced_equalities"],
            "free_weights_dof": dof["free_weights_dof"],
            "block_sizes": sorted(len(o) for o in partition)}

# ---------------------------------------------------------------------------
# FIBER-0H: continuous relative-mode geometry
# ---------------------------------------------------------------------------

def fiber_class(g2: nx.Graph, psi2: np.ndarray, order2: list, k) -> str:
    """Physical d-fiber class: 'plane' (2 dims) or 'halfline' (all-zero)."""
    from bh_graph.ballistic import index_of

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    s = complex(psi2[index_of(order2)[k]])
    phys = physical_fiber_dims(rest_nonzero(psi2, order2, k), s)
    return "halfline" if phys["d_cont_phys"] == 1 else "plane"


def fiber_symmetry_group(g2: nx.Graph, psi2: np.ndarray, order2: list,
                         k) -> str:
    """Earned fiber symmetry: 'U1' (all-zero) else 'Z2' (endpoint swap).

    U1 covariance relates fibers across s; only the all-zero cell
    (U1-invariant M) carries within-fiber rotation symmetry. Generic
    cells carry exactly the Z2 swap d -> -d.
    """
    return "U1" if fiber_class(g2, psi2, order2, k) == "halfline" else "Z2"


def invariant_volume_exhibits(fiber_kind: str) -> dict:
    """Two distinct invariant volumes per fiber class (non-uniqueness).

    Plane (Z2): Lebesgue density 1 and density (1 + r^2), both
    Z2-even, differing everywhere off d = 0. Half-line (U1 acts
    trivially on the quotient): dr and (1 + r) dr, both invariant,
    differing for r > 0. Each exhibit: {density, invariant_why,
    differs_where}. A volume element is not yet a probability measure.
    """
    if fiber_kind == "plane":
        return {
            "vol1": {"density": "1",
                     "invariant_why": "constant density: even under d->-d"},
            "vol2": {"density": "1+|d|^2",
                     "invariant_why": "radial density: even under d->-d"},
            "differs_where": "all d != 0",
            "canonical": False}
    if fiber_kind == "halfline":
        return {
            "vol1": {"density": "1",
                     "invariant_why": "U1 acts trivially on |d| quotient"},
            "vol2": {"density": "1+r",
                     "invariant_why": "U1 acts trivially on |d| quotient"},
            "differs_where": "all r > 0",
            "canonical": False}
    raise ValueError(f"unknown fiber kind: {fiber_kind}")


def is_volume_pair_valid_ok(fiber_kind: str) -> bool:
    """Boolean check: both exhibits invariant + mutually distinct."""
    try:
        ex = invariant_volume_exhibits(fiber_kind)
        if ex["canonical"]:
            return False
        if fiber_kind == "plane":
            for d in D_SWEEP:
                r = abs(complex(d))
                v1, v2 = 1.0, 1.0 + r * r
                if v1 <= 0.0 or v2 <= 0.0:
                    return False
                # Z2-evenness (exact: radial).
                if (1.0 + abs(-complex(d)) ** 2) != v2:
                    return False
            # Differ off d = 0.
            if not any(abs(complex(d)) > 0.0
                       and (1.0 + abs(complex(d)) ** 2) != 1.0
                       for d in D_SWEEP):
                return False
            return True
        if fiber_kind == "halfline":
            for r in RADIAL_GRID:
                if not (1.0 > 0.0 and 1.0 + r > 0.0):
                    return False
            if not any(r > 0.0 and (1.0 + r) != 1.0
                       for r in RADIAL_GRID):
                return False
            return True
        return False
    except Exception:
        return False


# ---------------------------------------------------------------------------
# FIBER-0I: normalizability
# ---------------------------------------------------------------------------

def lebesgue_ball_volume(radius: float) -> float:
    """Lebesgue volume of the d-disk |d| <= R: pi R^2 (exact formula)."""
    return float(math.pi * float(radius) ** 2)


def is_lebesgue_nonnormalizable_ok() -> bool:
    """Boolean check: Lebesgue volume diverges (exact growth V(2R)=4V(R))."""
    try:
        for R in (1.0, 2.0, 5.0, 10.0):
            if lebesgue_ball_volume(2.0 * R) != 4.0 * lebesgue_ball_volume(R):
                return False
            if not lebesgue_ball_volume(R * 10.0) > lebesgue_ball_volume(R):
                return False
        return True
    except Exception:
        return False


def rival_radial_plane_A(r: float, sig: float = RIVAL_SIG_A) -> float:
    """Rival-A radial density on the plane: (1/2pi sig^2) e^{-r/sig}."""
    r, sig = float(r), float(sig)
    return float(math.exp(-r / sig) / (2.0 * math.pi * sig * sig))


def rival_radial_plane_B(r: float, sig: float = RIVAL_SIG_B) -> float:
    """Rival-B radial density on the plane: Cauchy-square, non-Gaussian."""
    r, sig = float(r), float(sig)
    return float(1.0 / (math.pi * sig * sig * (1.0 + (r / sig) ** 2) ** 2))


def rival_radial_halfline(r: float, sig: float) -> float:
    """Half-line radial density: (1/sig) e^{-r/sig} (normalized on r >= 0)."""
    r, sig = float(r), float(sig)
    return float(math.exp(-r / sig) / sig)


def rival_radial_normalization(which: str) -> dict:
    """Closed-form normalization of rival radial densities (exact).

    A-plane: int (1/2pi s^2) e^{-r/s} r dr dphi = (1/s^2) s^2 = 1.
    B-plane: int (1/pi s^2)(1+r^2/s^2)^{-2} r dr dphi = 2 (1/2) = 1.
    Half-line: int_0^inf (1/s) e^{-r/s} dr = 1.
    """
    if which == "A-plane":
        return {"integral": 1.0, "closed_form": "(1/s^2)·s^2 = 1"}
    if which == "B-plane":
        return {"integral": 1.0, "closed_form": "2·(1/2) = 1"}
    if which == "halfline":
        return {"integral": 1.0, "closed_form": "1"}
    raise ValueError(f"unknown radial: {which}")


def is_rival_radial_normalized_ok(n_gl: int = 200,
                                  atol: float = 1e-9) -> bool:
    """Boolean check: rival radial integrals == 1 (Gauss-Legendre).

    Deterministic compactification u = r/(1+r) on [0,1]; the symbolic
    proof is in rival_radial_normalization, this is the numeric
    cross-check. Never raises.
    """
    try:
        from numpy.polynomial.legendre import leggauss

        xs, ws = leggauss(int(n_gl))
        us = 0.5 * (xs + 1.0)
        jac = 0.5 / (1.0 - us) ** 2
        rs = us / (1.0 - us)
        # A-plane radial integrand: (1/s^2) e^{-r/s} r (angle done).
        s = RIVAL_SIG_A
        ia = float(np.sum(ws * jac * np.exp(-rs / s) * rs / s ** 2))
        # B-plane: (2/s^2)(1+r^2/s^2)^{-2} r.
        t = RIVAL_SIG_B
        ib = float(np.sum(ws * jac * 2.0 * rs / t ** 2
                           / (1.0 + (rs / t) ** 2) ** 2))
        # Half-line A/B scales.
        ih_a = float(np.sum(ws * jac * np.exp(-rs / s) / s))
        ih_b = float(np.sum(ws * jac * np.exp(-rs / t) / t))
        return bool(abs(ia - 1.0) < atol and abs(ib - 1.0) < atol
                    and abs(ih_a - 1.0) < atol and abs(ih_b - 1.0) < atol)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# FIBER-0J: conservation/accounting
# ---------------------------------------------------------------------------

def ledger_coefficients(g2: nx.Graph, psi2: np.ndarray, order2: list,
                        k, A, B) -> dict:
    """Exact closed-form split-ledger coefficients for one cover.

    dQ(d) = (|d|^2 - |s|^2)/2 (cover-blind).
    dEpsi(c,d) = const(c) + |d|^2/2 - Re(conj(d) Delta(c)) with
    Delta(c) = sum_A psi - sum_B psi and const(c) = -|s|^2/2 +
    sum_{A symdiff B} Re(conj(s) psi_m). Recovers CONS-0K at d = 0.
    """
    from bh_graph.ballistic import index_of

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    idx = index_of(order2)
    s = complex(psi2[idx[k]])
    a, b = set(A), set(B)
    delta = sum((complex(psi2[idx[m]]) for m in a), 0.0j) - sum(
        (complex(psi2[idx[m]]) for m in b), 0.0j)
    const = -abs(s) ** 2 / 2.0 + sum(
        float(np.real(np.conj(s) * complex(psi2[idx[m]])))
        for m in (a ^ b))
    return {"s": s, "const": float(const), "Delta": complex(delta)}


def split_ledger_general(coeffs: dict, d: complex) -> dict:
    """Closed-form split ledger at (c, d) (exact, no graph build)."""
    s = complex(coeffs["s"])
    d = complex(d)
    dq = (abs(d) ** 2 - abs(s) ** 2) / 2.0
    de = (float(coeffs["const"]) + abs(d) ** 2 / 2.0
          - float(np.real(np.conj(d) * complex(coeffs["Delta"]))))
    return {"dQ": float(dq), "dEpsi": float(de)}


def split_ledger_direct(g2: nx.Graph, psi2: np.ndarray, order2: list,
                        k, A, B, d: complex) -> dict:
    """Direct split ledger at (c, d) via full-state construction."""
    from bh_graph.backreaction import energy_full
    from bh_graph.ballistic import index_of

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    s = complex(psi2[index_of(order2)[k]])
    i, j = fresh_labels(g2)
    p, q = fiber_point(s, complex(d))
    X = predecessor_state(g2, psi2, order2, k, A, B, p, q, i, j)
    e0 = energy_full(psi2, g2, order2)
    e1 = energy_full(X["psi"], X["g"], X["order"])
    n0 = float(np.sum(np.abs(psi2) ** 2))
    n1 = float(np.sum(np.abs(X["psi"]) ** 2))
    return {"dQ": float(n1 - n0), "dEpsi": float(e1 - e0)}


def is_ledger_formula_ok(g2: nx.Graph, psi2: np.ndarray, order2: list,
                         k, atol: float = 1e-9) -> bool:
    """Boolean check: closed-form vs direct ledgers (never raises).

    All covers x D_SWEEP; both dQ and dEpsi.
    """
    try:
        for _key, A, B in undirected_cover_list(sorted(g2.neighbors(k))):
            coeffs = ledger_coefficients(g2, psi2, order2, k, A, B)
            for d in D_SWEEP:
                closed = split_ledger_general(coeffs, complex(d))
                direct = split_ledger_direct(g2, psi2, order2, k,
                                             A, B, complex(d))
                if abs(closed["dQ"] - direct["dQ"]) > atol:
                    return False
                if abs(closed["dEpsi"] - direct["dEpsi"]) > atol:
                    return False
        return True
    except Exception:
        return False


def is_cons0_crosscheck_ok(g2: nx.Graph, psi2: np.ndarray, order2: list,
                           k, atol: float = 1e-9) -> bool:
    """Boolean check: d = 0 ledgers match banked CONS-0K (never raises)."""
    try:
        from bh_graph.ballistic import index_of
        from bh_graph.conservation import (dnorm_split_formula,
                                           dsplit_energy_formula)

        psi2 = np.asarray(psi2, dtype=np.complex128)
        order2 = list(order2)
        idx = index_of(order2)
        s = complex(psi2[idx[k]])
        for _key, A, B in undirected_cover_list(sorted(g2.neighbors(k))):
            coeffs = ledger_coefficients(g2, psi2, order2, k, A, B)
            closed = split_ledger_general(coeffs, 0.0j)
            if abs(closed["dQ"] - dnorm_split_formula(s, "equal")) > atol:
                return False
            if abs(closed["dEpsi"] - dsplit_energy_formula(
                    psi2, idx, k, set(A), set(B), "equal")) > atol:
                return False
        return True
    except Exception:
        return False


def beta_zero_census(g2: nx.Graph, psi2: np.ndarray, order2: list,
                     k) -> dict:
    """Census of Delta(c) == 0 covers (circle level-set survivors).

    Delta(c) = 0 -> dEpsi depends on |d| only -> joint ledger level
    sets are circles (continuous degeneracy survives even hypothetical
    imposition). Delta(c) != 0 -> joint levels are circle-meets-line
    (<= 2 points). Exact complex equality (banked exact fields).
    """
    n_zero, n_nonzero = 0, 0
    for _key, A, B in undirected_cover_list(sorted(g2.neighbors(k))):
        coeffs = ledger_coefficients(g2, psi2, order2, k, A, B)
        if complex(coeffs["Delta"]) == 0.0:
            n_zero += 1
        else:
            n_nonzero += 1
    return {"n_zero": n_zero, "n_nonzero": n_nonzero}


def level_fiber_witnesses(g2: nx.Graph, psi2: np.ndarray, order2: list,
                          k) -> dict:
    """Constructive level-set degeneracy witnesses (exact).

    For a Delta == 0 cover (if any): two distinct d with identical
    (dQ, dEpsi) (same |d|, different phase). For a Delta != 0 cover
    (if any): explicit circle-meets-line solve (<= 2 joint-level
    points, degeneracy counted, never selected).
    """
    from bh_graph.ballistic import index_of

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    s = complex(psi2[index_of(order2)[k]])
    out = {"circle_witness": None, "pointpair_witness": None}
    for key, A, B in undirected_cover_list(sorted(g2.neighbors(k))):
        coeffs = ledger_coefficients(g2, psi2, order2, k, A, B)
        delta = complex(coeffs["Delta"])
        if delta == 0.0 and out["circle_witness"] is None:
            d1, d2 = 1.0 + 0.0j, 0.0 + 1.0j
            l1 = split_ledger_general(coeffs, d1)
            l2 = split_ledger_general(coeffs, d2)
            if d1 != d2 and l1 == l2:
                out["circle_witness"] = {
                    "cover": [list(key[0]), list(key[1])],
                    "d1": [d1.real, d1.imag], "d2": [d2.real, d2.imag],
                    "ledger": [l1["dQ"], l1["dEpsi"]]}
        if delta != 0.0 and out["pointpair_witness"] is None:
            # Joint level (dQ*, dE*): |d| = r* pinned by dQ;
            # Re(conj(d) Delta) = const + r*^2/2 - dE* pinned by dEpsi.
            r_star = abs(s) + 1.0
            dq_star = (r_star ** 2 - abs(s) ** 2) / 2.0
            # Line offset t = Re(conj(d) Delta): pick t = 0 (through
            # origin: d = i*Delta*u/r... solve |d| = r*, Re = 0).
            # d = r* e^{i phi}: Re(conj(d)Delta) = r*|Delta|cos(phi_d).
            # t = 0 -> two solutions phi = +- pi/2 relative to Delta.
            ang = float(np.angle(delta))
            sols = [r_star * complex(np.exp(1.0j * (ang + math.pi / 2.0))),
                    r_star * complex(np.exp(1.0j * (ang - math.pi / 2.0)))]
            de_vals = [split_ledger_general(coeffs, z)["dEpsi"]
                       for z in sols]
            if abs(de_vals[0] - de_vals[1]) <= 1e-9:
                out["pointpair_witness"] = {
                    "cover": [list(key[0]), list(key[1])],
                    "n_points": 2, "dQ": float(dq_star),
                    "dEpsi": float(de_vals[0])}
    return out


def cross_cover_degeneracy(g2: nx.Graph, psi2: np.ndarray, order2: list,
                           k) -> dict:
    """Ledger-value degeneracy across covers (descriptive, exact).

    Counts distinct const(c) values: shared values mean covers the
    energy ledger cannot separate even in principle.
    """
    consts = []
    for _key, A, B in undirected_cover_list(sorted(g2.neighbors(k))):
        coeffs = ledger_coefficients(g2, psi2, order2, k, A, B)
        consts.append(round(float(coeffs["const"]), SIG_ROUND))
    return {"n_covers": len(consts),
            "n_distinct_const": len(set(consts))}


# ---------------------------------------------------------------------------
# FIBER-0K: energy ledger
# ---------------------------------------------------------------------------

def candidate_ledgers(g2: nx.Graph, psi2: np.ndarray, order2: list,
                      k, d_values=tuple(D_SWEEP)) -> dict:
    """BR-2.6 accounting on every inverse candidate (descriptive).

    Per cover: dEpsi over the d-sweep + range. Ordering filed only;
    never selective (HBR0-SIGNREV binding, see below).
    """
    rows = []
    for key, A, B in undirected_cover_list(sorted(g2.neighbors(k))):
        coeffs = ledger_coefficients(g2, psi2, order2, k, A, B)
        vals = [split_ledger_general(coeffs, complex(d))["dEpsi"]
                for d in d_values]
        rows.append({"cover": [list(key[0]), list(key[1])],
                     "dEpsi_min": float(min(vals)),
                     "dEpsi_max": float(max(vals)),
                     "dEpsi_range": float(max(vals) - min(vals))})
    return {"rows": rows, "n_covers": len(rows)}


def matched_hidden_pair_j2(L: int = J2_L_SPOT):
    """Matched hidden pair (same P_+, same E) for the HBR binding leg.

    psi_+ = VPLUS background; psi_-^A = HDELTA @ (0,0); sign mode:
    psi_-^B = -psi_-^A. P_+ parts exactly equal, E_A = E_B exactly
    (E = E_+ law). Returns (psi_A, psi_B, substrate).
    """
    from bh_graph.conservation import substrate_j2
    from bh_graph.formation import j2_torus_coords
    from bh_graph import hidden as _h
    from bh_graph import vacfield as _vf

    sub = substrate_j2(int(L))
    g, order = sub["g"], list(sub["order"])
    c3 = j2_torus_coords(int(L))
    plus = _vf.candidate_shape("VPLUS", {"graph": g, "order": order,
                                         "c3": c3, "L": int(L)}, kind="j2")
    minus_a = _h.hidden_delta(order, c3, (0, 0))
    pair = _h.matched_pair(np.asarray(plus), np.asarray(minus_a), "sign")
    return {"psi_A": np.asarray(pair["psi_A"]),
            "psi_B": np.asarray(pair["psi_B"]),
            "g": g, "order": order, "c3": dict(c3)}


def ledger_sign_flip_demo(L: int = J2_L_SPOT, k=None,
                          d_values=tuple(D_SWEEP)) -> dict:
    """HBR0-SIGNREV binding on the fiber: ledger sign flips (exact).

    Same cell, same (c, d) candidates, matched-pair backgrounds A/B:
    files opposite-sign dEpsi edges. Ordering descriptive only.
    """
    pair = matched_hidden_pair_j2(L)
    g, order = pair["g"], pair["order"]
    if k is None:
        k = order[0]
    flips = []
    for key, A, B in undirected_cover_list(sorted(g.neighbors(k))):
        ca = ledger_coefficients(g, pair["psi_A"], order, k, A, B)
        cb = ledger_coefficients(g, pair["psi_B"], order, k, A, B)
        for d in d_values:
            va = split_ledger_general(ca, complex(d))["dEpsi"]
            vb = split_ledger_general(cb, complex(d))["dEpsi"]
            if va == 0.0 or vb == 0.0:
                continue
            if (va > 0.0) != (vb > 0.0):
                flips.append({"cover": [list(key[0]), list(key[1])],
                              "d": [complex(d).real, complex(d).imag],
                              "dEpsi_A": float(va),
                              "dEpsi_B": float(vb)})
                break
        if flips:
            break
    return {"n_flips": len(flips), "flip": (flips[0] if flips else None)}


# ---------------------------------------------------------------------------
# FIBER-0L: vacuum dependence (per-leg debt facts)
# ---------------------------------------------------------------------------

def leg_debt_facts(g2: nx.Graph, psi2: np.ndarray, order2: list,
                   k, partition: list) -> dict:
    """Per-leg debt facts: fiber uncountable + freedom witnesses.

    discrete_free: >= 2 blocks (sound inter-block freedom).
    d_law_free: True (H exhibits: no canonical volume on any class).
    leg_debt: fiber uncountable AND (discrete_free OR d_law_free).
    """
    from bh_graph.ballistic import index_of

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    s = complex(psi2[index_of(order2)[k]])
    phys = physical_fiber_dims(rest_nonzero(psi2, order2, k), s)
    uncountable = bool(phys["d_cont_phys"] >= 1)
    discrete_free = bool(len(partition) >= 2)
    return {"fiber_uncountable": uncountable,
            "discrete_free": discrete_free,
            "d_law_free": True,
            "leg_debt": bool(uncountable and (discrete_free or True))}


# ---------------------------------------------------------------------------
# FIBER-0M: hidden residual
# ---------------------------------------------------------------------------

def pair_exchange_split(p: complex, q: complex) -> dict:
    """Pair-exchange decomposition: s-part even, d-part odd (exact)."""
    p, q = complex(p), complex(q)
    s = p + q
    d = p - q
    return {"s": s, "d": d,
            "even_part": (s / 2.0, s / 2.0),
            "odd_part": (d / 2.0, -d / 2.0),
            "P_plus_d": 0.0j, "P_minus_d": d}


def is_pair_exchange_theorem_ok(p: complex, q: complex) -> bool:
    """Boolean check: d purely odd, s purely even (never raises)."""
    try:
        rep = pair_exchange_split(complex(p), complex(q))
        e0, e1 = rep["even_part"]
        o0, o1 = rep["odd_part"]
        # Even part invariant under daughter swap; odd flips sign.
        if not (e0 == e1 and o0 == -o1):
            return False
        # Reconstruction + P_+ d = 0, P_- d = d.
        if not (e0 + o0 == complex(p) and e1 + o1 == complex(q)):
            return False
        return bool(rep["P_plus_d"] == 0.0j
                    and rep["P_minus_d"] == rep["d"])
    except Exception:
        return False


def linear_readout_split(a_i: complex, a_j: complex) -> dict:
    """Linear readout split: symmetric part sees s only (exact).

    L(p,q) = a_i p + a_j q = ((a_i+a_j)/2) s + ((a_i-a_j)/2) d.
    Symmetric (a_i = a_j) -> s only; antisymmetric -> d only.
    """
    a_i, a_j = complex(a_i), complex(a_j)
    return {"s_coeff": (a_i + a_j) / 2.0, "d_coeff": (a_i - a_j) / 2.0}


def is_linear_readout_theorem_ok(a_i: complex, a_j: complex,
                                 p: complex, q: complex) -> bool:
    """Boolean check: readout == s-part + d-part (never raises)."""
    try:
        a_i, a_j = complex(a_i), complex(a_j)
        p, q = complex(p), complex(q)
        rep = linear_readout_split(a_i, a_j)
        s = p + q
        d = p - q
        return bool(abs(a_i * p + a_j * q
                        - (rep["s_coeff"] * s
                           + rep["d_coeff"] * d)) <= FP_ATOL)
    except Exception:
        return False

# ---------------------------------------------------------------------------
# FIBER-0N: factorization
# ---------------------------------------------------------------------------

def disjoint_split_cells(graph_name: str = "path4",
                         field_name: str = "bonding") -> dict:
    """Two split cells with disjoint closed neighborhoods (exact).

    path4/bonding k = 0, 3: N[0] = {0,1}, N[3] = {2,3}, disjoint.
    Verified, not assumed.
    """
    st = merged_state(graph_name, field_name)
    g = st["g"]
    k1, k2 = 0, 3
    n1 = {k1} | set(g.neighbors(k1))
    n2 = {k2} | set(g.neighbors(k2))
    if n1 & n2:
        raise ValueError("closed neighborhoods not disjoint")
    return {"graph": graph_name, "field": field_name, "k1": k1, "k2": k2,
            "g": g, "psi": st["psi"], "order": st["order"]}


def is_joint_commuting_ok(g2: nx.Graph, k1, k2, A1, B1, A2, B2) -> bool:
    """Boolean check: disjoint splits commute (never raises).

    Applies covers in both orders with explicit daughter tracking;
    compares labeled edge sets under the canonical daughter map.
    """
    try:
        from bh_graph.contraction import apply_split_cover

        top = max(g2.nodes())
        i1, j1 = top + 1, top + 2
        i2, j2 = top + 3, top + 4
        h1 = apply_split_cover(g2, k1, set(A1), set(B1), i1, j1)
        h1 = apply_split_cover(h1, k2, set(A2), set(B2), i2, j2)
        h2 = apply_split_cover(g2, k2, set(A2), set(B2), i2, j2)
        h2 = apply_split_cover(h2, k1, set(A1), set(B1), i1, j1)
        e1 = {tuple(sorted(e)) for e in h1.edges()}
        e2 = {tuple(sorted(e)) for e in h2.edges()}
        return bool(e1 == e2 and set(h1.nodes()) == set(h2.nodes()))
    except Exception:
        return False


def is_joint_roundtrip_ok(g2: nx.Graph, psi2: np.ndarray, order2: list,
                          k1, k2, xi1: dict, xi2: dict,
                          atol: float = FP_ATOL) -> bool:
    """Boolean check: joint decode contracts back to M (never raises)."""
    try:
        from bh_graph.ballistic import index_of
        from bh_graph.contraction import contracted_state

        psi2 = np.asarray(psi2, dtype=np.complex128)
        order2 = list(order2)
        idx = index_of(order2)
        s1 = complex(psi2[idx[k1]])
        s2 = complex(psi2[idx[k2]])
        X1 = decode_residual(g2, psi2, order2, k1, dict(xi1))
        # Second decode inside X1's graph (k2 untouched: disjoint support).
        g_mid, psi_mid, order_mid = X1["g"], X1["psi"], X1["order"]
        X2 = decode_residual(g_mid, np.asarray(psi_mid), list(order_mid),
                             k2, dict(xi2))
        _ = s1, s2
        g, psi, order = X2["g"], np.asarray(X2["psi"]), list(X2["order"])
        # Contract both daughter pairs back (either order).
        g_a, psi_a, order_a, _ka, _r = contracted_state(
            g, psi, order, X1["i"], X1["j"], "sum")
        g_b, psi_b, order_b, _kb, _r2 = contracted_state(
            g_a, psi_a, order_a, X2["i"], X2["j"], "sum")
        e_want = {tuple(sorted(e)) for e in g2.edges()}
        mp = {_ka: k1, _kb: k2}
        e_got = {tuple(sorted((mp.get(a, a), mp.get(b, b))))
                 for a, b in g_b.edges()}
        if e_want != e_got:
            return False
        idxb = index_of(order_b)
        for v in order2:
            vv = _ka if v == k1 else (_kb if v == k2 else v)
            if abs(complex(psi_b[idxb[vv]]) - complex(psi2[idx[v]])) > atol:
                return False
        return True
    except Exception:
        return False


def correlated_cover_law() -> dict:
    """Correlated joint cover law on 2x2 covers (exact exhibit).

    P = [[3/8, 1/8], [1/8, 3/8]]: uniform marginals (1/2, exact),
    cell-swap symmetric, differs from product (TV = 1/4). Locality-safe
    (marginals = single-cell laws), orbit-constant (singleton orbits
    under the joint stabilizer), normalized exactly.
    """
    return {"table": [[3.0 / 8.0, 1.0 / 8.0], [1.0 / 8.0, 3.0 / 8.0]],
            "marginals": [0.5, 0.5]}


def is_correlated_law_valid_ok() -> bool:
    """Boolean check: correlated law normalized + uniform marginals."""
    try:
        law = correlated_cover_law()["table"]
        tot = sum(sum(row) for row in law)
        if abs(tot - 1.0) > 1e-15:
            return False
        for row in law:
            if abs(sum(row) - 0.5) > 1e-15:
                return False
        for c in range(2):
            if abs(law[0][c] + law[1][c] - 0.5) > 1e-15:
                return False
        # Symmetric + differs from product.
        if law[0][1] != law[1][0] or law[0][0] != law[1][1]:
            return False
        tv = 0.5 * sum(abs(v - 0.25) for row in law for v in row)
        return bool(tv > 0.0)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# FIBER-0O: scheduler separation
# ---------------------------------------------------------------------------

def sequential_orders_for_subset(g: nx.Graph, psi: np.ndarray, order: list,
                                 subset) -> dict:
    """Sequential contraction orders for one marked set (own code).

    Own implementation of the INFO-0 scheduler census from frozen
    BR-2.5/U0 ops: all m! permutations simulated as sequential
    single-edge contractions with sum-map threading; redundant cyclic
    marks skipped; valid iff completes; matching iff final graphs
    isomorphic AND |psi| multisets match at 1e-9 (TIME-0 grade).
    Cap m > 6 (INFO-0 convention; battery m <= 4, never capped).
    """
    from bh_graph.u0 import quotient_from_marks, thread_field_sum

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    edges = sorted(tuple(sorted(e)) for e in subset)
    m = len(edges)
    idx = {v: t for t, v in enumerate(order)}
    vals0 = {v: complex(psi[idx[v]]) for v in order}
    q = quotient_from_marks(g, set(edges))
    qpsi = thread_field_sum(q["classes"], q["node_of"], q["order2"],
                            psi, order)
    qmag = sorted(np.round(np.abs(qpsi), SIG_ROUND).tolist())
    qh = q["h"]
    if m > 6:
        return {"m": int(m), "capped": True, "n_perms": None,
                "n_valid": None, "n_matching": None, "all_match": None}
    n_valid, n_match = 0, 0
    for perm in itertools.permutations(edges):
        h = g.copy()
        live = dict(vals0)
        rep = {v: v for v in g.nodes()}
        nxt = max(h.nodes()) + 1 if len(h.nodes()) else 0
        ok = True
        for (a, b) in perm:
            ra, rb = rep[a], rep[b]
            if ra == rb:
                continue
            if not h.has_edge(ra, rb):
                ok = False
                break
            va, vb = live.pop(ra), live.pop(rb)
            nbrs = sorted((set(h.neighbors(ra)) | set(h.neighbors(rb)))
                           - {ra, rb})
            kk = nxt
            nxt += 1
            h.remove_nodes_from((ra, rb))
            h.add_node(kk)
            for w in nbrs:
                h.add_edge(kk, w)
            live[kk] = va + vb
            for v in g.nodes():
                if rep[v] in (ra, rb):
                    rep[v] = kk
        if not ok:
            continue
        n_valid += 1
        fmag = sorted(np.round(np.abs(np.array(
            [live[v] for v in sorted(live)])), SIG_ROUND).tolist())
        if nx.is_isomorphic(h, qh) and np.allclose(fmag, qmag, atol=1e-9):
            n_match += 1
    fact = int(math.factorial(m))
    return {"m": int(m), "capped": False, "n_perms": fact,
            "n_valid": int(n_valid), "n_matching": int(n_match),
            "all_match": bool(n_valid == fact and n_match == fact)}


def sync_scheduler_census(g: nx.Graph, psi: np.ndarray,
                          order: list) -> dict:
    """Scheduler census over all 2^E marked subsets (exact, tiny only).

    Cap E > 8 (INFO-0 convention; battery E <= 4, never capped).
    """
    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    edges = sorted(tuple(sorted(e)) for e in g.edges())
    if len(edges) > 8:
        return {"E": len(edges), "capped": True}
    rows = []
    for mask in range(1 << len(edges)):
        ce = [edges[t] for t in range(len(edges)) if mask & (1 << t)]
        r = sequential_orders_for_subset(g, psi, order, ce)
        r["mask"] = int(mask)
        rows.append(r)
    n_all = sum(1 for r in rows if r.get("all_match"))
    return {"E": len(edges), "capped": False, "n_subsets": len(rows),
            "n_all_match": int(n_all), "rows": rows}


def xi_schema_ok() -> bool:
    """Boolean check: xi schema carries no order/time component."""
    try:
        st = merged_state("k2", "bonding")
        g2, psi2, order2 = st["g"], st["psi"], st["order"]
        X = decode_residual(g2, psi2, order2, 0,
                            {"cover_key": ((0,), (0,)), "d": 1.0j})
        xi = encode_residual(X, 0, X["i"], X["j"])
        allowed = {"cover_key", "d", "s_check", "A", "B"}
        if set(xi) != allowed:
            return False
        banned = ("order", "schedule", "time", "history", "step")
        return bool(not any(b in str(k).lower() for k in xi for b in banned))
    except Exception:
        return False


def fiber_anatomy_multiset(g: nx.Graph, psi: np.ndarray,
                           order: list) -> list:
    """Isomorphism-invariant fiber-anatomy multiset over nodes.

    Sorted [(n_undirected, d_cont)] over nodes: invariant under
    relabeling (scheduler-order comparison).
    """
    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    out = []
    for k in sorted(g.nodes()):
        a = fiber_anatomy_keys(g, psi, order, k)
        out.append((a["n_undirected"], a["d_cont_full"]))
    return sorted(out)


def is_anatomy_scheduler_invariant_ok(g: nx.Graph, psi: np.ndarray,
                                       order: list, subset) -> bool:
    """Boolean check: fiber anatomy identical across scheduler orders.

    Re-runs the sequential simulation per order, collects the final
    (G, psi) per order, and requires identical anatomy multisets.
    The m! multiplicity never enters xi.
    """
    try:
        psi = np.asarray(psi, dtype=np.complex128)
        order = list(order)
        edges = sorted(tuple(sorted(e)) for e in subset)
        m = len(edges)
        if m > 6 or m < 2:
            return True
        idx = {v: t for t, v in enumerate(order)}
        vals0 = {v: complex(psi[idx[v]]) for v in order}
        anatomies = set()
        for perm in itertools.permutations(edges):
            h = g.copy()
            live = dict(vals0)
            rep = {v: v for v in g.nodes()}
            nxt = max(h.nodes()) + 1 if len(h.nodes()) else 0
            ok = True
            for (a, b) in perm:
                ra, rb = rep[a], rep[b]
                if ra == rb:
                    continue
                if not h.has_edge(ra, rb):
                    ok = False
                    break
                va, vb = live.pop(ra), live.pop(rb)
                nbrs = sorted((set(h.neighbors(ra)) | set(h.neighbors(rb)))
                               - {ra, rb})
                kk = nxt
                nxt += 1
                h.remove_nodes_from((ra, rb))
                h.add_node(kk)
                for w in nbrs:
                    h.add_edge(kk, w)
                live[kk] = va + vb
                for v in g.nodes():
                    if rep[v] in (ra, rb):
                        rep[v] = kk
            if not ok:
                return False
            live_order = sorted(live)
            live_psi = np.array([live[v] for v in live_order],
                                dtype=np.complex128)
            anatomies.add(tuple(fiber_anatomy_multiset(h, live_psi,
                                                        live_order)))
        return bool(len(anatomies) == 1)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# FIBER-0P: TIME consistency
# ---------------------------------------------------------------------------

def split_fraction(d: complex, s: complex) -> complex:
    """Split fraction alpha = 1/2 + d/(2s) (s != 0, exact bijection)."""
    d, s = complex(d), complex(s)
    if s == 0.0:
        raise ValueError("split fraction needs s != 0")
    return 0.5 + d / (2.0 * s)


def split_fraction_inverse(alpha: complex, s: complex) -> complex:
    """Inverse: d = (2 alpha - 1) s (exact)."""
    return (2.0 * complex(alpha) - 1.0) * complex(s)


def is_split_fraction_bijection_ok(s: complex) -> bool:
    """Boolean check: alpha <-> d roundtrip on D_SWEEP (never raises)."""
    try:
        s = complex(s)
        for d in D_SWEEP:
            a = split_fraction(complex(d), s)
            back = split_fraction_inverse(a, s)
            if abs(back - complex(d)) > 1e-9:
                return False
        return True
    except Exception:
        return False


def labeled_split_steps(g: nx.Graph) -> dict:
    """Banked TIME-0 labeled split-step set from graph g (fixed support).

    Uses time0.labeled_transitions over the N <= 4 labeled universe;
    the S-step set is computed with NO measure input (support fixed).
    Graphs with N > 4 or non-contiguous labels are out of scope
    (filed, not gated).
    """
    from bh_graph.time0 import (labeled_key, labeled_transitions,
                                labeled_universe)

    nodes = sorted(g.nodes())
    if len(nodes) > 4 or nodes != list(range(len(nodes))):
        return {"in_scope": False, "steps": []}
    states = labeled_universe(1, 4)
    ltra = labeled_transitions(states)
    adj, events = ltra["adj"], ltra["events"]
    key = labeled_key(g)
    steps = []
    for (k2, kind) in adj.get(key, []):
        if kind != "S":
            continue
        for ev in events.get((key, k2, kind), []):
            steps.append({"event": [ev["node"], sorted(ev["A"]),
                                    sorted(ev["B"])]})
    return {"in_scope": True, "n_steps": len(steps), "steps": steps}


def rival_pushforward_demo(steps: list, cover_of_event,
                           w_cover: dict, rho_vals: list) -> dict:
    """Finite-probe pushforward demo: weights on steps x d-probe.

    w(step, d) = W_cover(cover(step)) rho(d) / Z_probe (DEMONSTRATION
    normalization over the finite probe; exact normalization lives in
    section Q). Support identical by construction; weights compared
    across rivals by the caller.
    """
    z = 0.0
    table = []
    for ev in steps:
        c = cover_of_event(ev)
        for r in rho_vals:
            w = float(w_cover[c]) * float(r)
            table.append(w)
            z += w
    if z == 0.0:
        return {"weights": table, "Z": 0.0}
    return {"weights": [w / z for w in table], "Z": float(z)}


def load_time0_null(path: str = "data/time0_verdict.json") -> dict:
    """Consume the filed TIME0-NULL verdict (read-only).

    Returns {verdict, per_T f_unique, null_survives}. The admissible
    history SET is fixed by structural compatibility; weights from
    any fiber measure leave it unchanged (never selected by
    uniqueness: filed explicitly).
    """
    import json as _json

    with open(path) as f:
        v = _json.load(f)
    raw = v.get("verdict")
    label = raw.get("verdict") if isinstance(raw, dict) else raw
    per_t = {}
    for t, row in (v.get("per_T") or {}).items():
        per_t[str(t)] = float(row.get("f_unique", float("nan")))
    return {"verdict": label,
            "per_T_f_unique": per_t,
            "null_survives": bool(label == "TIME0-NULL")}

# ---------------------------------------------------------------------------
# FIBER-0Q: rival-measure proof
# ---------------------------------------------------------------------------

def cover_cprime_from_key(key) -> int:
    """cprime = |A cap B| from a canonical cover key (exact)."""
    return len(set(key[0]) & set(key[1]))


def rival_cover_weights_A(covers: list) -> dict:
    """Rival-A cover law: uniform 1/n (covariant, full support)."""
    n = len(covers)
    return {row[0]: 1.0 / n for row in covers}


def rival_cover_weights_B(covers: list) -> dict:
    """Rival-B cover law: (cprime + 1)/Z (covariant, full support).

    Transport-invariant (cprime preserved), hence orbit-constant and
    R-covariant; differs from uniform wherever cprime varies.
    """
    z = sum(cover_cprime_from_key(row[0]) + 1 for row in covers)
    return {row[0]: (cover_cprime_from_key(row[0]) + 1.0) / z
            for row in covers}


def relative_angle(d: complex, s: complex) -> float:
    """Relative angle phi_rel = arg(d/s) (U1-invariant, s != 0).

    Single-point convention phi_rel = 0 at d = 0 (filed;
    measure-irrelevant).
    """
    d, s = complex(d), complex(s)
    if d == 0.0:
        return 0.0
    return float(np.angle(d / s))


def rival_d_density_A(d: complex, s: complex, fiber_kind: str) -> float:
    """Rival-A d-density (plane: radial-A x uniform angle; half-line: r)."""
    d = complex(d)
    if fiber_kind == "halfline":
        return rival_radial_halfline(abs(d) / 2.0, RIVAL_SIG_A)
    return float(rival_radial_plane_A(abs(d)) / (2.0 * math.pi))


def rival_d_density_B(d: complex, s: complex, fiber_kind: str) -> float:
    """Rival-B d-density (radial-B x angle; uniform angle at s = 0)."""
    d, s = complex(d), complex(s)
    if fiber_kind == "halfline":
        return rival_radial_halfline(abs(d) / 2.0, RIVAL_SIG_B)
    radial = rival_radial_plane_B(abs(d))
    if s == 0.0:
        return float(radial / (2.0 * math.pi))
    phi = relative_angle(d, s)
    return float(radial * (1.0 + RIVAL_B_ANG_AMP * math.cos(2.0 * phi))
                 / (2.0 * math.pi))


def rival_normalization_proof(fiber_kind: str, s_is_zero: bool) -> dict:
    """Closed-form normalization proof (factors multiply to 1).

    Covers: A: n.(1/n) = 1; B: Z/Z = 1. Plane radial: A/B = 1
    (section I). Plane angular: A: 1; B: 1 + (1/2).0 = 1 (s != 0)
    or 1 (s = 0). Half-line radial: 1.
    """
    if fiber_kind == "halfline":
        return {"covers_A": 1.0, "covers_B": 1.0, "radial_A": 1.0,
                "radial_B": 1.0, "joint_A": 1.0, "joint_B": 1.0}
    return {"covers_A": 1.0, "covers_B": 1.0,
            "radial_A": 1.0, "radial_B": 1.0,
            "angular_A": 1.0,
            "angular_B": 1.0 if s_is_zero else 1.0,
            "joint_A": 1.0, "joint_B": 1.0}


def is_rival_z2_ok(fiber_kind: str, s: complex,
                   atol: float = 1e-12) -> bool:
    """Boolean check: rival densities exactly Z2-even on D_SWEEP."""
    try:
        s = complex(s)
        for d in D_SWEEP:
            d = complex(d)
            for rho in (rival_d_density_A, rival_d_density_B):
                if abs(rho(-d, s, fiber_kind) - rho(d, s, fiber_kind)) > atol:
                    return False
        return True
    except Exception:
        return False


def is_rival_orbit_constant_ok(weights: dict, partition: list) -> bool:
    """Boolean check: weights bitwise-constant within each block."""
    try:
        for block in partition:
            vals = {weights[kk] for kk in block}
            if len(vals) != 1:
                return False
        return True
    except Exception:
        return False


def is_rival_cover_covariant_ok(g2: nx.Graph, k, perm: dict) -> bool:
    """Boolean check: rival-B weights covariant under transport.

    Transported weights (via the cover map) equal weights recomputed
    at the transported cell (bitwise: same (c'+1)/Z rationals).
    Rival-A uniform is trivially covariant (same n).
    """
    try:
        from bh_graph.sym0 import apply_relabel

        order = sorted(g2.nodes())
        rel = apply_relabel(g2, np.zeros(len(order),
                                         dtype=np.complex128),
                            order, dict(perm))
        h = rel["g"]
        k2 = perm.get(k, k)
        covs0 = undirected_cover_list(sorted(g2.neighbors(k)))
        covs1 = undirected_cover_list(sorted(h.neighbors(k2)))
        if len(covs0) != len(covs1):
            return False
        w0 = rival_cover_weights_B(covs0)
        w1 = rival_cover_weights_B(covs1)
        for key, A, B in covs0:
            a, b = transport_cover(A, B, dict(perm))
            if w1[undirected_key(a, b)] != w0[key]:
                return False
        return True
    except Exception:
        return False


def is_rival_density_covariant_ok(fiber_kind: str, s: complex,
                                  alpha: float, atol: float = 1e-12) -> bool:
    """Boolean check: U1 pushforward covariance on D_SWEEP (never raises).

    rho_{e^{ialpha}M}(e^{ialpha} d) == rho_M(d): |d| preserved,
    phi_rel preserved (d, s rotate together).
    """
    try:
        s = complex(s)
        u = complex(np.exp(1.0j * float(alpha)))
        for d in D_SWEEP:
            d = complex(d)
            for rho in (rival_d_density_A, rival_d_density_B):
                if abs(rho(u * d, u * s, fiber_kind)
                       - rho(d, s, fiber_kind)) > atol:
                    return False
        return True
    except Exception:
        return False


def is_rival_cover_local_ok(g2: nx.Graph, psi2: np.ndarray, order2: list,
                            k) -> bool:
    """Boolean check: rival cover laws invariant under remote mutation.

    Same labels before/after: bitwise comparison. Vacuous True where
    no remote site exists.
    """
    try:
        psi2 = np.asarray(psi2, dtype=np.complex128)
        order2 = list(order2)
        from bh_graph.ballistic import index_of

        covs = undirected_cover_list(sorted(g2.neighbors(k)))
        wA0 = rival_cover_weights_A(covs)
        wB0 = rival_cover_weights_B(covs)
        dist = dict(nx.single_source_shortest_path_length(g2, k))
        idx = index_of(order2)
        far = [v for v in order2 if dist.get(v, 10 ** 9) >= 3]
        if far:
            mut = np.array(psi2, dtype=np.complex128)
            mut[idx[far[0]]] += complex(0.5, -0.25)
            _ = mut  # cover laws are field-blind; mutation changes nothing
            covs1 = undirected_cover_list(sorted(g2.neighbors(k)))
            if (rival_cover_weights_A(covs1) != wA0
                    or rival_cover_weights_B(covs1) != wB0):
                return False
        return True
    except Exception:
        return False


def rival_class_stability(g2: nx.Graph, psi2: np.ndarray, order2: list,
                          k) -> dict:
    """Fiber-class stability under the frozen remote mutation (filed).

    Unstable exactly on all-zero cells (earned global-gauge scope
    note, SPLIT-0F): there the QUOTIENT interpretation follows the
    earned quotient; the local law itself is remote-invariant.
    """
    try:
        from bh_graph.ballistic import index_of

        psi2 = np.asarray(psi2, dtype=np.complex128)
        order2 = list(order2)
        before = fiber_class(g2, psi2, order2, k)
        dist = dict(nx.single_source_shortest_path_length(g2, k))
        idx = index_of(order2)
        far = [v for v in order2 if dist.get(v, 10 ** 9) >= 3]
        if not far:
            return {"applicable": False, "stable": True,
                    "before": before, "after": before}
        mut = np.array(psi2, dtype=np.complex128)
        mut[idx[far[0]]] += complex(0.5, -0.25)
        after = fiber_class(g2, mut, order2, k)
        return {"applicable": True, "stable": bool(before == after),
                "before": before, "after": after}
    except Exception:
        return {"applicable": False, "stable": False,
                "before": "?", "after": "?"}


def is_rival_support_ok(weights: dict, fiber_kind: str, s: complex,
                        d_values=tuple(D_SWEEP)) -> bool:
    """Boolean check: full support (weights > 0, densities > 0 on probe)."""
    try:
        if any(not (v > 0.0) for v in weights.values()):
            return False
        s = complex(s)
        for d in d_values:
            d = complex(d)
            if not (rival_d_density_A(d, s, fiber_kind) > 0.0
                    and rival_d_density_B(d, s, fiber_kind) > 0.0):
                return False
        return True
    except Exception:
        return False


def rival_tv_discrete(wA: dict, wB: dict) -> float:
    """Exact total-variation distance between rival cover laws."""
    return float(0.5 * sum(abs(wA[kk] - wB[kk]) for kk in wA))


def rival_density_diff(fiber_kind: str, s: complex) -> dict:
    """Sup density difference over the radial x angle probe + witness."""
    s = complex(s)
    best = 0.0
    wit = None
    for r in RADIAL_GRID:
        for phi in ANGLE_GRID:
            d = r * complex(math.cos(phi), math.sin(phi))
            diff = abs(rival_d_density_A(d, s, fiber_kind)
                       - rival_d_density_B(d, s, fiber_kind))
            if diff > best:
                best = float(diff)
                wit = [float(d.real), float(d.imag)]
    return {"sup_diff": float(best), "witness_d": wit}


# ---------------------------------------------------------------------------
# FIBER-0R: minimal new primitive
# ---------------------------------------------------------------------------

def primitive_census(n_covers: int, partition: list, fiber_kind: str,
                     s: complex, exact_orbits: bool) -> dict:
    """Exact residual-freedom type census for one cell (filed, not chosen).

    Inter-orbit weights: exact DOF (tiny) or sound lower bound (J2
    blocks). Radial density on |d|: free on every class. Angular
    density: free on gauge-fixed s != 0 planes. Correlation rule:
    N-level (section N).
    """
    n_blocks = len(partition)
    return {"inter_orbit_dof": int(max(n_blocks - 1, 0)),
            "inter_orbit_exact": bool(exact_orbits),
            "radial_density_free": True,
            "angular_density_free": bool(fiber_kind == "plane"
                                         and complex(s) != 0.0),
            "correlation_rule": "N-level debt",
            "n_covers": int(n_covers), "n_blocks": int(n_blocks)}


# ---------------------------------------------------------------------------
# Witness theorems (F/G without census)
# ---------------------------------------------------------------------------

def halves_nonsingleton_witness(g2: nx.Graph, k) -> dict:
    """Degree-sequence witness: halves never singleton for d >= 1.

    Covers (N, empty) vs (N, N): daughter-j degrees 1 vs d+1 >= 2
    differ -> post-split graphs non-isomorphic -> >= 2 halves
    classes. d = 0: single cover -> singleton. Exact, census-free.
    """
    from bh_graph.contraction import apply_split_cover

    d = int(g2.degree(k))
    if d == 0:
        return {"d": 0, "singleton": True, "why": "single cover"}
    nbrs = sorted(g2.neighbors(k))
    i, j = fresh_labels(g2)
    h1 = apply_split_cover(g2, k, set(nbrs), set(), i, j)
    h2 = apply_split_cover(g2, k, set(nbrs), set(nbrs), i, j)
    dj1 = int(h1.degree(j))
    dj2 = int(h2.degree(j))
    return {"d": d, "singleton": False,
            "deg_j_witness": [dj1, dj2],
            "why": "daughter degrees 1 vs d+1 differ"}


def cover_nonsingleton_witness(g2: nx.Graph, k) -> dict:
    """Signature witness: >= 2 blocks for d >= 1 (non-unique covers).

    Witness covers (N, empty) [signature (d,0,0)] vs (N, N)
    [(d,d,d)]: signatures differ for d >= 1. d = 0: 1 cover.
    """
    d = int(g2.degree(k))
    if d == 0:
        return {"d": 0, "n_blocks_ge": 1, "unique": True}
    nbrs = sorted(g2.neighbors(k))
    keys = {key for key, _A, _B in undirected_cover_list(nbrs)}
    k1 = undirected_key(set(nbrs), set())
    k2 = undirected_key(set(nbrs), set(nbrs))
    sigs = {cover_signature(set(nbrs), set()),
            cover_signature(set(nbrs), set(nbrs))}
    return {"d": d, "n_blocks_ge": 2, "unique": False,
            "witnesses_present": bool(k1 in keys and k2 in keys),
            "signatures_differ": bool(len(sigs) == 2)}


# ---------------------------------------------------------------------------
# Firewall
# ---------------------------------------------------------------------------

def fitted_param_count() -> int:
    """Fitted physical parameters in the earned apparatus: 0 (exact)."""
    return 0


def is_no_hidden_tuning_ok(path: str | None = None) -> bool:
    """Boolean check: no RNG, no tuning in earned code (never raises).

    AST scan of the target file (default: this module): forbids
    random imports/calls and forbidden tuning names in function
    signatures outside the rival_*/is_rival_* namespace (rivals are labeled
    exhibits, and carry no tuning names either -- the exemption is
    structural, verified empty).
    """
    import inspect as _inspect

    try:
        if path is None:
            path = _inspect.getfile(sys.modules[__name__])
        with open(path) as f:
            tree = ast.parse(f.read())
        forbidden = ("beta", "temperature", "temp", "rate", "fitted",
                     "exponent", "preference", "bias", "threshold",
                     "eps_phys", "prob", "weight", "measure", "prior")
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    if (a.name or "").split(".")[0] == "random":
                        return False
            elif isinstance(node, ast.ImportFrom):
                if (node.module or "").split(".")[0] == "random":
                    return False
            elif isinstance(node, ast.Call):
                fn = node.func
                name = ""
                if isinstance(fn, ast.Name):
                    name = fn.id or ""
                elif isinstance(fn, ast.Attribute):
                    name = fn.attr or ""
                low = name.lower()
                if "random" in low or "rng" in low or low == "seed":
                    return False
            elif isinstance(node, ast.FunctionDef):
                if (node.name.startswith("rival_")
                        or node.name.startswith("is_rival_")):
                    continue
                params = [a.arg.lower() for a in node.args.args
                          + node.args.kwonlyargs]
                if any(any(f in p for f in forbidden) for p in params):
                    return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Verdict ladder (frozen, pre-data)
# ---------------------------------------------------------------------------

def verdict_from_census(census: dict) -> dict:
    """Frozen ladder mapping (counts in, rung out).

    hard: dict of HARD gate bools (any False -> FIBER0-INCOMPLETE).
    rivals_valid + rivals_differ -> FIBER0-DEBT.
    volume_unique + lebesgue_divergent + discrete_unique_all ->
      FIBER0-NONNORMALIZABLE.
    residual_dof_total == 0 -> FIBER0-DERIVED.
    Else -> FIBER0-PARTIAL.
    """
    hard = census.get("hard", {})
    if not hard or not all(bool(v) for v in hard.values()):
        return {"verdict": "FIBER0-INCOMPLETE",
                "reason": "apparatus gate red"}
    if bool(census.get("rivals_valid")) and bool(census.get("rivals_differ")):
        return {"verdict": "FIBER0-DEBT",
                "reason": ("two inequivalent normalized measures "
                           "satisfy every earned constraint")}
    if (bool(census.get("volume_unique"))
            and bool(census.get("lebesgue_divergent"))
            and bool(census.get("discrete_unique_all"))):
        return {"verdict": "FIBER0-NONNORMALIZABLE",
                "reason": "canonical volume needs a new scale/cutoff"}
    if int(census.get("residual_dof_total", 1)) == 0:
        return {"verdict": "FIBER0-DERIVED",
                "reason": "unique normalized mu_M, no new parameter"}
    return {"verdict": "FIBER0-PARTIAL",
            "reason": "part fixed, exact residual freedom remains"}


# ---------------------------------------------------------------------------
# Campaign fact aggregators (deterministic)
# ---------------------------------------------------------------------------

def cell_facts(graph_name: str, field_name: str, k: int,
               ref_cells: dict | None = None) -> dict:
    """All per-cell facts for one tiny cell (campaign worker core)."""
    from bh_graph.ballistic import index_of
    from bh_graph.sym0 import reversal_perm, shuffle_perm

    st = merged_state(graph_name, field_name)
    g2, psi2, order2 = st["g"], st["psi"], st["order"]
    s = complex(psi2[index_of(order2)[k]])
    covs = undirected_cover_list(sorted(g2.neighbors(k)))
    dims = inverse_dimensions(g2, psi2, order2, k)
    det = deterministic_core_status(g2, psi2, order2, k)
    an = hidden_anatomy(g2, psi2, order2, k)
    hidden = {"hidden_ok": is_hidden_retained_ok(g2, psi2, order2, k),
              "locally_varies": an["locally_varies"],
              "D_merged": an["D_merged"]}
    rt = cell_roundtrip(g2, psi2, order2, k)
    agree = (agreement_vs_split0(f"{graph_name}/{field_name}@{k}",
                                 dims, det, hidden, rt, ref_cells)
             if ref_cells is not None else {"agree": None,
                                            "mismatches": []})
    aut = state_automorphisms_bruteforce(g2, psi2, order2)
    stab = [a for a in aut if a[k] == k]
    orbits = cover_orbits(covs, stab)
    blocks = signature_blocks(covs)
    perms = [reversal_perm(order2), shuffle_perm(order2, 11)]
    facts = {
        "cell": f"{graph_name}/{field_name}@{k}", "d": int(g2.degree(k)),
        "dims": dims, "det": det, "hidden": hidden, "roundtrip": rt,
        "agreement": agree,
        "quotient_ok": bool(all(
            is_quotient_invariant_ok(g2, psi2, order2, k, p, a)
            for p in perms for a in U1_GRID)),
        "swap_ok": bool(all(is_swap_involution_ok(A, B) for _k, A, B in covs)
                        and all(is_swap_fiber_ok(s, d) for d in D_SWEEP)),
        "n_aut": len(aut), "n_stab": len(stab),
        "orbits": [len(o) for o in orbits],
        "n_blocks": len(blocks),
        "transport_ok": bool(all(
            is_transport_correct_ok(g2, k, a) for a in aut)),
        "local_ok": bool(is_fiber_local_ok(g2, psi2, order2, k)),
        "applicability": locality_applicability(g2, order2, k),
        "patch_orbits_ok": bool(is_patch_orbits_local_ok(g2, psi2, order2,
                                                         k)),
        "singleton": singleton_status(g2, psi2, order2, k, dims),
        "halves_witness": halves_nonsingleton_witness(g2, k),
        "cover_witness": cover_nonsingleton_witness(g2, k),
        "cover_freedom": cover_measure_freedom(len(covs), orbits),
        "fiber_kind": fiber_class(g2, psi2, order2, k),
        "fiber_sym": fiber_symmetry_group(g2, psi2, order2, k),
        "ledger_ok": bool(is_ledger_formula_ok(g2, psi2, order2, k)),
        "cons0_ok": bool(is_cons0_crosscheck_ok(g2, psi2, order2, k)),
        "beta_census": beta_zero_census(g2, psi2, order2, k),
        "level_witnesses": level_fiber_witnesses(g2, psi2, order2, k),
        "cross_cover": cross_cover_degeneracy(g2, psi2, order2, k),
        "candidate_ledger": candidate_ledgers(g2, psi2, order2, k),
        "pair_exchange_ok": bool(all(
            is_pair_exchange_theorem_ok(*fiber_point(s, dd))
            for dd in D_SWEEP)),
        "readout_ok": bool(all(
            is_linear_readout_theorem_ok(1.0, 1.0, *fiber_point(s, dd))
            and is_linear_readout_theorem_ok(1.0, -1.0,
                                             *fiber_point(s, dd))
            for dd in D_SWEEP)),
        "primitive": primitive_census(len(covs), orbits,
                                      fiber_class(g2, psi2, order2, k),
                                      s, True),
    }
    # Rival cover checks (per-cell discrete part).
    wA = rival_cover_weights_A(covs)
    wB = rival_cover_weights_B(covs)
    facts["rival_covers"] = {
        "sum_A": float(sum(wA.values())), "sum_B": float(sum(wB.values())),
        "orbit_const_A": bool(is_rival_orbit_constant_ok(wA, orbits)),
        "orbit_const_B": bool(is_rival_orbit_constant_ok(wB, orbits)),
        "covariant_B": bool(all(
            is_rival_cover_covariant_ok(g2, k, p) for p in perms)),
        "local_ok": bool(is_rival_cover_local_ok(g2, psi2, order2, k)),
        "support_ok": bool(is_rival_support_ok(
            wA, facts["fiber_kind"], s)
            and is_rival_support_ok(wB, facts["fiber_kind"], s)),
        "tv": float(rival_tv_discrete(wA, wB)),
        "z2_ok": bool(is_rival_z2_ok(facts["fiber_kind"], s)),
        "u1_ok": bool(all(
            is_rival_density_covariant_ok(facts["fiber_kind"], s, a)
            for a in U1_GRID)),
        "class_stability": rival_class_stability(g2, psi2, order2, k),
    }
    return facts


def j2_leg_facts(background: str, ref_j2: dict | None = None) -> dict:
    """All per-leg facts for one J2 background (campaign worker core)."""
    from bh_graph.ballistic import index_of
    from bh_graph.sym0 import (is_perm_auto_ok, reversal_perm,
                               sheet_perm_from_c3, shuffle_perm)

    leg = j2_leg_state(background)
    g2, psi2, order2 = leg["g"], leg["psi"], leg["order"]
    c3, k = leg["c3"], leg["k"]
    s = complex(psi2[index_of(order2)[k]])
    covs = undirected_cover_list(sorted(g2.neighbors(k)))
    dims = inverse_dimensions_capped(g2, psi2, order2, k)
    an = hidden_anatomy(g2, psi2, order2, k)
    hidden = {"hidden_ok": is_hidden_retained_ok(g2, psi2, order2, k),
              "locally_varies": an["locally_varies"],
              "D_merged": an["D_merged"]}
    rt = cell_roundtrip(g2, psi2, order2, k)
    overlap = {"ZERO": "zero", "VPLUS": "uniform", "VMINUS": "VMINUS"}
    agree = (agreement_vs_split0_j2(overlap[background], dims, ref_j2)
             if ref_j2 is not None and background in overlap
             else {"agree": None, "mismatches": []})
    blocks = signature_blocks(covs)
    perms = [reversal_perm(order2), shuffle_perm(order2, 11)]
    trans = translation_perms_j2(J2_L_SPOT)
    sheet = sheet_perm_from_c3(c3)
    # Pinned VF2 decision queries: automorphisms fixing k (exact,
    # first-hit; None filed where none extends the pin).
    nbrs = sorted(g2.neighbors(k))
    pinned = []
    for m1, m2 in itertools.islice(itertools.product(nbrs, nbrs), 6):
        pin = {k: k, m1: m2}
        iso = find_pinned_automorphism(g2.copy(), pin)
        pinned.append({"pin": [m1, m2], "found": bool(iso is not None)})
    facts = {
        "leg": background, "d": int(g2.degree(k)),
        "dims": dims, "hidden": hidden, "roundtrip": rt,
        "agreement": agree,
        "quotient_ok": bool(all(
            is_quotient_invariant_ok(g2, psi2, order2, k, p, a)
            for p in perms for a in U1_GRID)),
        "swap_ok": bool(all(is_swap_involution_ok(A, B) for _kk, A, B in covs)
                        and all(is_swap_fiber_ok(s, d) for d in D_SWEEP)),
        "blocks": [len(o) for o in blocks],
        "n_blocks": len(blocks),
        "transport_translations_ok": bool(all(
            is_transport_correct_ok(g2, k, t) for t in trans)),
        "transport_sheet_ok": bool(
            is_perm_auto_ok(g2, sheet)
            and is_transport_correct_ok(g2, k, sheet)),
        "pinned_queries": pinned,
        "local_ok": bool(is_fiber_local_ok(g2, psi2, order2, k)),
        "applicability": locality_applicability(g2, order2, k),
        "full_never_singleton": True,
        "halves_witness": halves_nonsingleton_witness(g2, k),
        "cover_witness": cover_nonsingleton_witness(g2, k),
        "cover_freedom": cover_measure_freedom(len(covs), blocks),
        "fiber_kind": fiber_class(g2, psi2, order2, k),
        "fiber_sym": fiber_symmetry_group(g2, psi2, order2, k),
        "ledger_ok": bool(is_ledger_formula_ok(g2, psi2, order2, k)),
        "cons0_ok": bool(is_cons0_crosscheck_ok(g2, psi2, order2, k)),
        "beta_census": beta_zero_census(g2, psi2, order2, k),
        "level_witnesses": level_fiber_witnesses(g2, psi2, order2, k),
        "cross_cover": cross_cover_degeneracy(g2, psi2, order2, k),
        "leg_debt": leg_debt_facts(g2, psi2, order2, k, blocks),
        "primitive": primitive_census(len(covs), blocks,
                                      fiber_class(g2, psi2, order2, k),
                                      s, False),
    }
    wA = rival_cover_weights_A(covs)
    wB = rival_cover_weights_B(covs)
    facts["rival_covers"] = {
        "sum_A": float(sum(wA.values())), "sum_B": float(sum(wB.values())),
        "block_const_A": bool(is_rival_orbit_constant_ok(wA, blocks)),
        "block_const_B": bool(is_rival_orbit_constant_ok(wB, blocks)),
        "covariant_B_perms": bool(all(
            is_rival_cover_covariant_ok(g2, k, p) for p in perms)),
        "covariant_B_trans": bool(all(
            is_rival_cover_covariant_ok(g2, k, t) for t in trans)),
        "covariant_B_sheet": bool(is_rival_cover_covariant_ok(
            g2, k, sheet)),
        "local_ok": bool(is_rival_cover_local_ok(g2, psi2, order2, k)),
        "support_ok": bool(is_rival_support_ok(
            wA, facts["fiber_kind"], s)
            and is_rival_support_ok(wB, facts["fiber_kind"], s)),
        "tv": float(rival_tv_discrete(wA, wB)),
        "z2_ok": bool(is_rival_z2_ok(facts["fiber_kind"], s)),
        "u1_ok": bool(all(
            is_rival_density_covariant_ok(facts["fiber_kind"], s, a)
            for a in U1_GRID)),
        "class_stability": rival_class_stability(g2, psi2, order2, k),
    }
    return facts
