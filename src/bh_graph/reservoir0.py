"""RESERVOIR-0: merge-energy deficit and lost-information correspondence.

Given MERGE0-DETERMINISTIC + MERGE0-ACCOUNT-DEBT, characterize the exact
missing local account of a deterministic contraction and test whether it
is a zero-parameter function of the information xi discarded by merge.

Frozen convention (RESERVOIR0-PREREG, exact campaign conventions):
  Delta E_known = Delta E_psi + Delta E_G with
    Delta E_psi = E_psi(after) - E_psi(before), E_psi = <psi|H(G)|psi>,
      H = -A, J = 1 (BR-2.6/CONS-0: = P1+P2+P3+P4 = 2B - 2 sum_cross);
    Delta E_G = E1 - E0 = -(1+c) (edge-count change, CONS-0C dE_G).
  R_merge = -Delta E_known = (E(X) - E(M)) + (1+c).
R_merge is a diagnostic number. It is not an existing physical energy
store. No reservoir degree of freedom is invented here.

Frozen inputs (read-only, never modified): MERGE0-DETERMINISTIC +
MERGE0-ACCOUNT-DEBT, SPLIT0-MIXED, INFO0-MATCHED, BR-2.5 ONTOLOGY,
BR-2.6 ACCOUNTED, CONS0-PARTIAL, HBR0-SIGNREV, VACFIELD0-JOINT,
VACCOMP0-COMPLETE, VACTEXTURE-GRADIENT, VACEXC0-COMPLETE,
RESPONSE0-KERNEL (excitation states only).

Firewall: no strong-force, binding-energy, mass, heat, radiation,
internal energy, or sub-particle reading; no event probabilities
(MEASURE0-DEBT binds); no firing condition (BR-2.7 NO-MODE binds).
Any explicit augmented-state simulation belongs to a future campaign
and is forbidden here (audited by symbol scans).

This module ADDS the RESERVOIR-0 battery/apparatus; it never modifies
any banked module (all consumed read-only).
"""

from __future__ import annotations

import math

import networkx as nx
import numpy as np

from bh_graph import merge0 as m0
from bh_graph.merge0 import BAR_FP, BAR_LEDGER, BAR_U1

MAP = "sum"  # frozen contraction map (BR-2.5/2.6/CONS-0 primary)

# ---------------------------------------------------------------------------
# Frozen battery constants
# ---------------------------------------------------------------------------

# Extended deterministic relative-mode grid (SPLIT-0 D_SWEEP + real axis +
# imag axis + |d| = 1 and |d| = 2 circles). No RNG anywhere.
_SQ2 = math.sqrt(2.0)
D_GRID = (
    0.0j, 1.0 + 0.0j, 0.0 + 1.0j, 1.0 + 1.0j, -0.5 + 0.25j, 2.0 - 1.0j,
    complex(-2.0, 0.0), complex(-1.5, 0.0), complex(-1.0, 0.0),
    complex(-0.5, 0.0), complex(0.5, 0.0), complex(1.5, 0.0),
    complex(2.0, 0.0),
    complex(0.0, -2.0), complex(0.0, -1.5), complex(0.0, -1.0),
    complex(0.0, -0.5), complex(0.0, 0.5), complex(0.0, 1.5),
    complex(0.0, 2.0),
    complex(_SQ2 / 2.0, _SQ2 / 2.0), complex(-_SQ2 / 2.0, _SQ2 / 2.0),
    complex(-_SQ2 / 2.0, -_SQ2 / 2.0), complex(_SQ2 / 2.0, -_SQ2 / 2.0),
    complex(_SQ2, _SQ2), complex(-_SQ2, _SQ2),
    complex(-_SQ2, -_SQ2), complex(_SQ2, -_SQ2),
)

# J2 fiber cover subset: first K covers per common-charge bucket (capped,
# deterministic enumeration order; all c' buckets spanned).
COVER_CAP_PER_C = 25
J2_FIBER_L = 4
J2_FIBER_BACKGROUNDS = ("zero", "uniform", "VMINUS")

# Frozen texture specs (family, L, params): periodic maps only.
TEXTURE_SPECS = (
    ("j2-L4", "uniform", {"alpha0": 0.0}),
    ("j2-L4", "uniform", {"alpha0": math.pi / 8.0}),
    ("j2-L4", "sine-x", {"alpha0": 0.0, "delta": math.pi / 8.0, "lam": 2}),
    ("j2-L4", "sine-xy", {"alpha0": 0.0, "delta": math.pi / 8.0, "lam": 2}),
    ("j2-L4", "linear", {"alpha0": 0.0, "winding": 1}),
    ("j2-L4", "wall", {"alpha0": 0.0, "delta": math.pi / 4.0, "width": 1.0}),
    ("j2-L4", "step", {"alpha0": 0.0, "delta": math.pi / 4.0}),
    ("j2-L8", "sine-x", {"alpha0": 0.0, "delta": math.pi / 8.0, "lam": 4}),
    ("j2-L8", "step", {"alpha0": 0.0, "delta": math.pi / 4.0}),
)

# Frozen excitation-response grid (VAC-EXC states, abs mode, a = 1).
EXCRESP_KINDS = ("point_amp", "packet", "hidden_sector", "point_phase")
EXCRESP_VACS = ("VPLUS", "VPI", "VMINUS")
EXCRESP_EPS = (1e-3, 1e-2, 0.1, 0.5)
EXCRESP_SUB = "j2-L4"

# Frozen disjoint/overlap substrates (pairs by deterministic scan rule).
PAIR_SUBS = ("path-8", "ring-8", "j2-L4", "handbuilt", "er-24")
PAIR_FIELDS_DIS = {"j2-L4": ("uniform", "random777", "VMINUS"),
                   "path-8": ("uniform", "random777"),
                   "ring-8": ("uniform", "random777"),
                   "handbuilt": ("uniform", "random777"),
                   "er-24": ("uniform", "random777")}
PAIR_FIELDS_OVL = ("random777",)

# Frozen full-collapse orders (externally supplied; RES-0 chooses none).
ORDER_SPECS = (("path8-fwd", "uniform"), ("path8-rev", "uniform"),
               ("path8-fwd", "random777"), ("path8-rev", "random777"),
               ("tri-o1", "uniform"), ("tri-o2", "uniform"),
               ("tri-o1", "random777"), ("tri-o2", "random777"),
               ("tri-o1", "zero"), ("tri-o2", "zero"))

# Frozen sequences (same content as the MERGE-0 battery seq tasks).
SEQ_TASKS = [("path8-collapse", "uniform"),
             ("j2L4-ball", "uniform"),
             ("j2L4-ball", "VMINUS"),
             ("handbuilt-chain", "uniform"),
             ("ring8-chain", "uniform")]

# Locality mutation (SPLIT-0 frozen value, read-only reuse of convention).
MUTATION_DELTA = complex(0.5, -0.25)

# Support classes (RES-0B ladder, frozen labels).
SUPPORT_CLASSES = ("edge-local", "one-neighborhood-local", "larger-local",
                   "nonlocal")


# ---------------------------------------------------------------------------
# RES-0 core: the merge deficit (diagnostic, zero-parameter)
# ---------------------------------------------------------------------------

def merge_deficit(g: nx.Graph, psi: np.ndarray, order: list, i, j) -> dict:
    """Exact merge deficit R for one selected-edge contraction (X -> M).

    R = -(Delta E_psi + Delta E_G) with Delta E_psi direct (E1 - E0)
    and Delta E_G = -(1+c). Also files the BR-2.6 formula parts, the
    cover/fiber/mixed separation, and the (s, d) fiber coordinates.
    Pure readout: one graph op + direct before/after evaluation.
    """
    from bh_graph.accounting import event_ledger as _el
    from bh_graph.backreaction import bond_B as _bond
    from bh_graph.backreaction import energy_full as _ef
    from bh_graph.ballistic import index_of
    from bh_graph.conservation import energy_parts as _ep
    from bh_graph.conservation import exclusive_neighborhoods as _xn
    from bh_graph.contraction import contracted_state as _cs

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    idx = index_of(order)
    el = _el(g, psi, order, i, j)
    p1, p2, p3, p4 = _ep(psi, idx, g, i, j)
    xi, xj, _ = _xn(g, i, j)
    g2, psi2, order2, k, _record = _cs(g, psi, order, i, j, MAP)
    e0 = _ef(psi, g, order)
    e1 = _ef(psi2, g2, order2)
    c = len(el["common"])
    dE_G = -(1 + c)
    dE_direct = int(g2.number_of_edges() - g.number_of_edges())
    dN_direct = int(g2.number_of_nodes() - g.number_of_nodes())
    dEpsi = float(e1 - e0)
    rval = -float((e1 - e0) + dE_G)
    a = complex(psi[idx[i]])
    b = complex(psi[idx[j]])
    bij = _bond(psi, idx[i], idx[j])
    cross = (sum(_bond(psi, idx[j], idx[m]) for m in xi)
             + sum(_bond(psi, idx[i], idx[m]) for m in xj))
    return {
        "E0": float(e0), "E1": float(e1),
        "dEpsi_direct": dEpsi,
        "dEpsi_formula": float(el["dE_formula"]),
        "P1": float(p1), "P2": float(p2), "P3": float(p3),
        "P4": float(p4),
        "parts_sum": float(p1 + p2 + p3 + p4),
        "dE_G": int(dE_G), "dE_direct": dE_direct, "dN_direct": dN_direct,
        "c": int(c), "n_cross": int(el["n_cross"]),
        "B": float(bij), "cross": float(cross),
        "s": complex(a + b), "d": complex(a - b),
        "R": rval,
        "R_cover": float(1 + c),
        "R_fiber": float(-2.0 * bij),
        "R_mixed": float(rval - (1 + c) + 2.0 * bij),
        "k": k,
    }


def deficit_from_event(rec: dict) -> dict:
    """R parts from a MERGE-0 event record (analyzer-side, no recompute)."""
    rval = -float(rec["dEpsi_direct"] + rec["dE"])
    cover = float(1 + rec["common"])
    fiber = float(-2.0 * rec["B_ij"])
    return {"R": rval, "R_cover": cover, "R_fiber": fiber,
            "R_mixed": float(rval - cover - fiber)}


def is_deficit_formula_ok(rep: dict, atol: float = BAR_LEDGER) -> bool:
    """Boolean: direct R matches the BR-2.6 formula (never raises)."""
    try:
        form = rep["R_cover"] + rep["R_fiber"] + 2.0 * rep["cross"]
        return bool(abs(rep["R"] - form) <= atol
                    and rep["dE_direct"] == rep["dE_G"] == -(1 + rep["c"])
                    and rep["dN_direct"] == -1
                    and abs(rep["dEpsi_direct"] - rep["dEpsi_formula"]) <= atol
                    and abs(rep["parts_sum"] - rep["dEpsi_direct"]) <= atol)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# RES-0B: locality (support + mutation invariance + classification)
# ---------------------------------------------------------------------------

def deficit_support(g: nx.Graph, i, j) -> list:
    """Exact psi/graph support of R: {i,j} + exclusive + common neighbors."""
    sup = ({i, j} | (set(g.neighbors(i)) | set(g.neighbors(j))) - {i, j})
    return sorted(sup)


def classify_deficit_support(g: nx.Graph, i, j) -> dict:
    """Support class of R (RES-0B four-way ladder, derived not assumed)."""
    sup = set(deficit_support(g, i, j))
    closed = ({i, j} | set(g.neighbors(i)) | set(g.neighbors(j)))
    if sup <= {i, j}:
        cls = "edge-local"
    elif sup <= closed:
        cls = "one-neighborhood-local"
    else:
        di = dict(nx.single_source_shortest_path_length(g, i))
        dj = dict(nx.single_source_shortest_path_length(g, j))
        ball2 = {v for v in g.nodes()
                 if min(di.get(v, 10 ** 9), dj.get(v, 10 ** 9)) <= 2}
        cls = "larger-local" if sup <= ball2 else "nonlocal"
    return {"class": cls, "support": sorted(sup),
            "support_size": len(sup)}


def locality_report(g: nx.Graph, psi: np.ndarray, order: list,
                    i, j) -> dict:
    """Mutation locality of R (frozen support radius, measured invariance).

    Far = outside the closed neighborhood N[i] u N[j] (dist >= 2 from
    both endpoints). Common-neighbor field mutation is inside the graph
    support but provably outside the psi support (filed separately).
    Vacuous pass (applicable False) when no remote site exists.
    """
    from bh_graph.ballistic import index_of

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    idx = index_of(order)
    r0 = merge_deficit(g, psi, order, i, j)["R"]
    closed = ({i, j} | set(g.neighbors(i)) | set(g.neighbors(j)))
    di = dict(nx.single_source_shortest_path_length(g, i))
    dj = dict(nx.single_source_shortest_path_length(g, j))
    far = sorted(v for v in order
                 if min(di.get(v, 10 ** 9), dj.get(v, 10 ** 9)) >= 2)
    out = {"R0": float(r0), "support": deficit_support(g, i, j)}
    out["class"] = classify_deficit_support(g, i, j)["class"]
    if far:
        mut = np.array(psi, dtype=np.complex128)
        mut[idx[far[0]]] += MUTATION_DELTA
        r1 = merge_deficit(g, mut, order, i, j)["R"]
        out["far_field"] = {"applicable": True, "node": str(far[0]),
                            "dR": float(r1 - r0)}
    else:
        out["far_field"] = {"applicable": False, "dR": 0.0}
    outside = sorted(v for v in g.nodes() if v not in closed)
    toggled = None
    for a in outside:
        for b in outside:
            if a < b and not g.has_edge(a, b):
                toggled = (a, b)
                break
        if toggled is not None:
            break
    if toggled is not None:
        h = g.copy()
        h.add_edge(*toggled)
        r1 = merge_deficit(h, psi, order, i, j)["R"]
        out["far_edge"] = {"applicable": True,
                           "edge": [str(toggled[0]), str(toggled[1])],
                           "dR": float(r1 - r0)}
    else:
        out["far_edge"] = {"applicable": False, "dR": 0.0}
    common = sorted(set(g.neighbors(i)) & set(g.neighbors(j)) - {i, j})
    if common:
        mut = np.array(psi, dtype=np.complex128)
        mut[idx[common[0]]] += MUTATION_DELTA
        r1 = merge_deficit(g, mut, order, i, j)["R"]
        out["common_field"] = {"applicable": True, "node": str(common[0]),
                               "dR": float(r1 - r0)}
        h = g.copy()
        h.remove_edge(common[0], i)
        r2 = merge_deficit(h, psi, order, i, j)["R"]
        c0 = len(common)
        c1 = len(set(h.neighbors(i)) & set(h.neighbors(j)) - {i, j})
        out["common_graph"] = {"applicable": True, "dR": float(r2 - r0),
                               "dc": int(c1 - c0)}
    else:
        out["common_field"] = {"applicable": False, "dR": 0.0}
        out["common_graph"] = {"applicable": False, "dR": 0.0, "dc": 0}
    return out


def is_locality_ok(rep: dict, atol: float = BAR_LEDGER) -> bool:
    """Boolean: all applicable R mutations invariant (never raises)."""
    try:
        for key in ("far_field", "far_edge", "common_field"):
            leg = rep[key]
            if leg["applicable"] and abs(float(leg["dR"])) > atol:
                return False
        return rep["class"] in ("edge-local", "one-neighborhood-local")
    except Exception:
        return False


# ---------------------------------------------------------------------------
# RES-0C: covariance (R x U(1) invariance, sheet, endpoint swap)
# ---------------------------------------------------------------------------

def u1_deficit_report(g: nx.Graph, psi: np.ndarray, order: list,
                      i, j, alphas=None) -> dict:
    """R under global phase rotation (must be invariant: B/cross products)."""
    from bh_graph import sym0 as _s

    if alphas is None:
        alphas = _s.U1_ALPHAS
    psi = np.asarray(psi, dtype=np.complex128)
    r0 = merge_deficit(g, psi, order, i, j)["R"]
    worst = 0.0
    for a in alphas:
        q = _s.apply_u1(psi, float(a))
        r1 = merge_deficit(g, q, order, i, j)["R"]
        worst = max(worst, abs(float(r1 - r0)))
    return {"R0": float(r0), "maxdiff": float(worst),
            "n_alphas": len(list(alphas))}


def relabel_deficit_report(g: nx.Graph, psi: np.ndarray, order: list,
                           i, j, seed: int = 11) -> dict:
    """R under joint relabeling (counts + bonds travel with the state)."""
    from bh_graph import sym0 as _s

    psi = np.asarray(psi, dtype=np.complex128)
    r0 = merge_deficit(g, psi, order, i, j)["R"]
    perm = _s.shuffle_perm(list(order), seed=seed)
    rel = _s.apply_relabel(g, psi, list(order), perm)
    r1 = merge_deficit(rel["g"], rel["psi"], rel["order"],
                       perm[i], perm[j])["R"]
    return {"R0": float(r0), "R1": float(r1),
            "diff": float(r1 - r0),
            "is_auto": bool(_s.is_perm_auto_ok(g, perm))}


def swap_deficit_report(g: nx.Graph, psi: np.ndarray, order: list,
                        i, j) -> dict:
    """R(i,j) vs R(j,i) (endpoint swap is gauge: bitwise identity)."""
    r0 = merge_deficit(g, psi, order, i, j)["R"]
    r1 = merge_deficit(g, psi, order, j, i)["R"]
    return {"R0": float(r0), "R1": float(r1), "diff": float(r1 - r0)}


def sheet_deficit_report(g: nx.Graph, psi: np.ndarray, order: list,
                         c3: dict, i, j) -> dict:
    """R under J2 sheet exchange (symmetry transport, SYM-0 S)."""
    from bh_graph import sym0 as _s

    psi = np.asarray(psi, dtype=np.complex128)
    r0 = merge_deficit(g, psi, order, i, j)["R"]
    perm = _s.sheet_perm_from_c3(dict(c3))
    psi_s = _s.apply_pushforward(psi, list(order), perm)
    r1 = merge_deficit(g, psi_s, list(order), perm[i], perm[j])["R"]
    return {"R0": float(r0), "R1": float(r1), "diff": float(r1 - r0),
            "is_auto": bool(_s.is_perm_auto_ok(g, perm))}


def is_covariant_ok(maxdiff: float, atol: float = BAR_U1) -> bool:
    """Boolean: covariance residual within bar (never raises)."""
    try:
        return bool(abs(float(maxdiff)) <= atol)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# RES-0A battery records (MERGE-0 events + R + locality + covariance)
# ---------------------------------------------------------------------------

def event_record(sub: dict, ftag: str, edge, psi=None) -> dict:
    """Full RESERVOIR-0 event record: MERGE-0 ledger + R + probes.

    The MERGE-0 record is consumed read-only (frozen function); this
    wrapper only ADDS the deficit, locality, and covariance readouts.
    """
    if psi is None:
        psi = m0.build_field(sub, ftag)
    rec = m0.event_record(sub, ftag, edge, psi=psi)
    g, order = sub["g"], sub["order"]
    i, j = edge
    df = merge_deficit(g, np.asarray(psi, dtype=np.complex128),
                       order, i, j)
    rec["R"] = df["R"]
    rec["R_cover"] = df["R_cover"]
    rec["R_fiber"] = df["R_fiber"]
    rec["R_mixed"] = df["R_mixed"]
    rec["R_formula_ok"] = bool(is_deficit_formula_ok(df))
    rec["loc"] = locality_report(g, psi, order, i, j)
    rec["loc_ok"] = bool(is_locality_ok(rec["loc"]))
    u1 = u1_deficit_report(g, psi, order, i, j)
    rel = relabel_deficit_report(g, psi, order, i, j)
    swp = swap_deficit_report(g, psi, order, i, j)
    rec["cov_u1"] = u1
    rec["cov_rel"] = {k: v for k, v in rel.items() if k != "is_auto"}
    rec["cov_rel_auto"] = bool(rel["is_auto"])
    rec["cov_swap"] = swp
    rec["cov_u1_ok"] = bool(is_covariant_ok(u1["maxdiff"]))
    rec["cov_rel_ok"] = bool(is_covariant_ok(rel["diff"]))
    rec["cov_swap_ok"] = bool(swp["diff"] == 0.0)
    if sub.get("c3") is not None:
        sh = sheet_deficit_report(g, psi, order, sub["c3"], i, j)
        rec["cov_sheet"] = {k: v for k, v in sh.items() if k != "is_auto"}
        rec["cov_sheet_ok"] = bool(is_covariant_ok(sh["diff"]))
    else:
        rec["cov_sheet"] = None
        rec["cov_sheet_ok"] = True
    return rec


def pair_event_record(sub: dict, ftag: str, edge) -> dict:
    """Both matched-pair members + R contrast (HBR anatomy in R view)."""
    prec = m0.pair_event_record(sub, ftag, edge)
    for side in ("A", "B"):
        r = prec[side]
        parts = deficit_from_event(r)
        r["R"] = parts["R"]
        r["R_cover"] = parts["R_cover"]
        r["R_fiber"] = parts["R_fiber"]
        r["R_mixed"] = parts["R_mixed"]
    ea = float(prec["A"]["E0"])
    eb = float(prec["B"]["E0"])
    prec["E_A"] = float(ea)
    prec["E_B"] = float(eb)
    prec["dE_before"] = float(ea - eb)
    prec["R_A"] = prec["A"]["R"]
    prec["R_B"] = prec["B"]["R"]
    prec["dR"] = float(prec["A"]["R"] - prec["B"]["R"])
    return prec


# ---------------------------------------------------------------------------
# RES-0E/F/G/H/K/L/M: fiber sweeps over the SPLIT-0 inverse
# ---------------------------------------------------------------------------

def fiber_cells() -> list:
    """Frozen tiny fiber battery: every node of every SPLIT-0 state."""
    from bh_graph import split0 as s0

    cells = []
    for cell in s0.split0_cells():
        st = s0.merged_state(cell["graph"], cell["field"])
        cells.append({"cell": cell["state"], "graph": cell["graph"],
                      "field": cell["field"], "k": cell["k"],
                      "d": cell["d"], "M": st})
    return cells


def cover_subset_j2(g2: nx.Graph, k, cap: int = COVER_CAP_PER_C) -> list:
    """Frozen J2 cover subset: first `cap` covers per c' bucket (ordered).

    Deterministic enumeration order, outcome-blind. Every c' bucket
    0..d(k) is spanned (counts C(d,c') 2^(d-c') > 0); buckets smaller
    than the cap are taken exhaustively.
    """
    from bh_graph.u0 import undirected_covers

    buckets: dict = {}
    for key, A, B in undirected_covers(sorted(g2.neighbors(k))):
        cp = len(set(A) & set(B))
        slot = buckets.setdefault(cp, [])
        if len(slot) < int(cap):
            slot.append((key, set(A), set(B)))
    out = []
    for cp in sorted(buckets):
        out.extend(buckets[cp])
    return out


def _align_to(psi, order_from: list, order_to: list) -> np.ndarray:
    """Align a field vector across node orders (exact permutation)."""
    from bh_graph.ballistic import index_of

    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(list(order_from))
    return np.array([psi[idx[v]] for v in order_to], dtype=np.complex128)


def fiber_row(g2: nx.Graph, psi2: np.ndarray, order2: list, k,
              key, A, B, d: complex) -> dict:
    """One fiber row: decode X from (M, cover, d), file R + anatomy.

    Files the deficit, the exact R(d) = A + |d|^2/2 + Re(conj(d) W)
    decomposition (zero-parameter: A, W from the frozen ledger), the
    cover/fiber/mixed separation, the exact-xi split counterpart, the
    equal-halves-policy residual, the forward roundtrip check, the
    INFO-0 (s, d) cross-check, and the endpoint-swap-xi invariance.
    """
    from bh_graph import split0 as s0
    from bh_graph.backreaction import energy_full as _ef
    from bh_graph.ballistic import index_of

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    d = complex(d)
    idx2 = index_of(order2)
    s = complex(psi2[idx2[k]])
    i, j = s0.fresh_labels(g2)
    p, q = s0.fiber_point(s, d)
    X = s0.predecessor_state(g2, psi2, order2, k, set(A), set(B),
                             p, q, i, j)
    df = merge_deficit(X["g"], X["psi"], X["order"], i, j)
    a, b = set(A), set(B)
    c = len(a & b)
    xi_only = sorted(a - b)
    xj_only = sorted(b - a)
    vals = {v: complex(psi2[idx2[v]]) for v in order2 if v != k}
    wsum = (sum(vals[v] for v in xj_only)
            - sum(vals[v] for v in xi_only))
    usum = (sum(vals[v] for v in xj_only)
            + sum(vals[v] for v in xi_only))
    externe = complex(np.conj(s) * usum)
    acoef = (1 + c) - abs(s) ** 2 / 2.0 + float(np.real(externe))
    rform = (acoef + abs(d) ** 2 / 2.0
             + float(np.real(np.conj(d) * wsum)))
    e_x, e_m = df["E0"], df["E1"]
    r_split = -float((e_x - e_m) + (1 + c))
    ph, qh = s0.halves_point(s)
    xh = s0.predecessor_state(g2, psi2, order2, k, set(A), set(B),
                              ph, qh, i, j)
    e_xh = _ef(xh["psi"], xh["g"], xh["order"])
    r_split_equal = -float((float(e_xh) - e_m) + (1 + c))
    pok = s0.is_predecessor_ok(g2, psi2, order2, k, X, i, j)
    try:
        from bh_graph import info0 as i0

        fl = i0.field_loss(p, q)
        xok = bool(abs(complex(fl["s"]) - s) <= BAR_FP
                   and abs(complex(fl["d"]) - d) <= BAR_FP)
        i0avail = True
    except Exception:
        xok = False
        i0avail = False
    psw, qsw = s0.fiber_point(s, -d)
    xsw = s0.predecessor_state(g2, psi2, order2, k, set(B), set(A),
                               psw, qsw, i, j)
    rsw = merge_deficit(xsw["g"], xsw["psi"], xsw["order"], i, j)["R"]
    sup = classify_deficit_support(X["g"], i, j)
    return {
        "cover": [sorted(a), sorted(b)], "c": int(c),
        "n_xi": len(xi_only), "n_xj": len(xj_only),
        "d": [float(d.real), float(d.imag)],
        "s": [float(s.real), float(s.imag)],
        "B": df["B"], "cross": df["cross"],
        "R": df["R"], "R_cover": df["R_cover"],
        "R_fiber": df["R_fiber"], "R_mixed": df["R_mixed"],
        "Acoef": float(acoef),
        "W": [float(complex(wsum).real), float(complex(wsum).imag)],
        "Rformula": float(rform),
        "form_err": float(df["R"] - rform),
        "R_split": float(r_split),
        "invert_err": float(df["R"] + r_split),
        "R_split_equal": float(r_split_equal),
        "eq_resid": float(df["R"] + r_split_equal),
        "pred_ok": bool(pok),
        "dN": df["dN_direct"], "dE": df["dE_direct"],
        "info0_ok": bool(xok), "info0_avail": bool(i0avail),
        "swap_err": float(df["R"] - rsw),
        "support_class": sup["class"],
        "support_size": sup["support_size"],
    }


def fiber_sweep(cell: dict, d_values=tuple(D_GRID)) -> dict:
    """Exhaustive fiber sweep for one tiny cell: all covers x d grid."""
    from bh_graph.u0 import undirected_covers

    M = cell["M"]
    g2, psi2, order2 = M["g"], M["psi"], M["order"]
    k = cell["k"]
    rows = []
    covers = list(undirected_covers(sorted(g2.neighbors(k))))
    for key, A, B in covers:
        for d in d_values:
            rows.append(fiber_row(g2, psi2, order2, k, key, set(A),
                                  set(B), complex(d)))
    return {"cell": cell["cell"], "graph": cell["graph"],
            "field": cell["field"], "k": cell["k"], "d": cell["d"],
            "n_covers": len(covers), "n_d": len(d_values),
            "rows": rows}


def fiber_sweep_j2(background: str, L: int = J2_FIBER_L,
                   d_values=tuple(D_GRID)) -> dict:
    """J2 fiber sweep: frozen cover subset x d grid (one background)."""
    from bh_graph import split0 as s0

    spot = s0.j2_merged_spot(int(L), background)
    g2, psi2, order2 = spot["g"], spot["psi"], spot["order"]
    k = spot["k"]
    covers = cover_subset_j2(g2, k)
    rows = []
    for _key, A, B in covers:
        for d in d_values:
            rows.append(fiber_row(g2, psi2, order2, k, None, set(A),
                                  set(B), complex(d)))
    buckets: dict = {}
    for _key, A, B in covers:
        cp = len(set(A) & set(B))
        buckets[cp] = buckets.get(cp, 0) + 1
    return {"cell": f"j2-L{L}/{background}", "background": background,
            "L": int(L), "k": k, "d": int(g2.degree(k)),
            "n_covers": len(covers), "n_d": len(d_values),
            "buckets": {str(cp): n for cp, n in sorted(buckets.items())},
            "rows": rows}


# ---------------------------------------------------------------------------
# RES-0I: disjoint additivity + cross-term support
# ---------------------------------------------------------------------------

def _closed_nbrs(g: nx.Graph, e) -> set:
    a, b = e
    return ({a, b} | set(g.neighbors(a)) | set(g.neighbors(b)))


def pair_rule(subname: str, relation: str):
    """Frozen edge-pair rule (deterministic elist scan, outcome-blind).

    disjoint: first node-disjoint pair with disjoint closed
    neighborhoods. overlap: first node-disjoint pair with overlapping
    closed neighborhoods. Node-sharing pairs belong to RES-0J
    (sequences), never here.
    """
    sub = m0.build_substrate(subname)
    elist = sorted(tuple(sorted(e)) for e in sub["g"].edges())
    for x in range(len(elist)):
        for y in range(x + 1, len(elist)):
            ea, eb = elist[x], elist[y]
            if set(ea) & set(eb):
                continue
            dis = bool(_closed_nbrs(sub["g"], ea)
                       & _closed_nbrs(sub["g"], eb))
            if relation == "disjoint" and not dis:
                return ea, eb
            if relation == "overlap" and dis:
                return ea, eb
    raise ValueError(f"no {relation} pair on {subname}")


def _finals_equal_swap(g1, psi1, o1, n1a, n1b,
                       g2, psi2, o2, n2a, n2b, atol=BAR_FP) -> bool:
    """Swap-aware finals comparison for disjoint ab/ba orders.

    Order ab takes fresh labels (n, n+1) = (a-merged, b-merged); order
    ba takes (n, n+1) = (b-merged, a-merged). Map a<->a, b<->b across.
    """
    from bh_graph.ballistic import index_of

    mp = {n1a: n2b, n1b: n2a}
    e1 = {tuple(sorted((mp.get(a, a), mp.get(b, b))))
          for a, b in g1.edges()}
    e2 = {tuple(sorted(e)) for e in g2.edges()}
    if e1 != e2 or set(o1) != set(mp.get(v, v) for v in o1):
        pass
    if e1 != e2:
        return False
    idx1 = index_of(list(o1))
    idx2 = index_of(list(o2))
    for v in o1:
        w = mp.get(v, v)
        if abs(complex(psi1[idx1[v]]) - complex(psi2[idx2[w]])) > atol:
            return False
    return True


def disjoint_record(subname: str, ftag: str, relation: str) -> dict:
    """Joint-vs-sum ledger for a frozen edge pair (additivity / cross).

    Contracts ea then eb (both survive: node-disjoint pairs only) and
    eb then ea; files step ledgers, joint totals, the signed cross
    term X = R_joint - R_a - R_b, and the ab/ba finals comparison.
    """
    from bh_graph.backreaction import energy_full as _ef
    from bh_graph.contraction import contracted_state as _cs

    sub = m0.build_substrate(subname)
    g0, order0 = sub["g"], sub["order"]
    ea, eb = pair_rule(subname, relation)
    psi0 = np.asarray(m0.build_field(sub, ftag), dtype=np.complex128)
    e_init = _ef(psi0, g0, order0)
    eg_init = g0.number_of_edges()
    ra = merge_deficit(g0, psi0, order0, *ea)["R"]
    rb = merge_deficit(g0, psi0, order0, *eb)["R"]
    gm, psim, om, ka, _ = _cs(g0, psi0, list(order0), *ea, MAP)
    rb_after = merge_deficit(gm, psim, om, *eb)["R"]
    r_joint_ab = float(ra + rb_after)
    gfin_ab, psifin_ab, ofin_ab, kb_ab, _ = _cs(
        gm, psim, list(om), *eb, MAP)
    efin_ab = _ef(psifin_ab, gfin_ab, ofin_ab)
    r_direct_ab = -float((efin_ab - e_init)
                         + (gfin_ab.number_of_edges() - eg_init))
    gm2, psim2, om2, kb, _ = _cs(g0, psi0, list(order0), *eb, MAP)
    ra_after = merge_deficit(gm2, psim2, om2, *ea)["R"]
    r_joint_ba = float(rb + ra_after)
    gfin_ba, psifin_ba, ofin_ba, ka_ba, _ = _cs(
        gm2, psim2, list(om2), *ea, MAP)
    efin_ba = _ef(psifin_ba, gfin_ba, ofin_ba)
    r_direct_ba = -float((efin_ba - e_init)
                         + (gfin_ba.number_of_edges() - eg_init))
    finals_eq = _finals_equal_swap(gfin_ab, psifin_ab, ofin_ab, ka, kb_ab,
                                   gfin_ba, psifin_ba, ofin_ba, kb, ka_ba)
    overlap = sorted(_closed_nbrs(g0, ea) & _closed_nbrs(g0, eb),
                     key=str)
    return {
        "sub": subname, "ftag": ftag, "relation": relation,
        "ea": list(ea), "eb": list(eb),
        "disjoint_ok": bool(len(overlap) == 0),
        "overlap_size": len(overlap),
        "R_a": float(ra), "R_b": float(rb),
        "R_b_after_a": float(rb_after), "R_a_after_b": float(ra_after),
        "R_joint_ab": r_joint_ab, "R_joint_ba": r_joint_ba,
        "R_direct_ab": r_direct_ab, "R_direct_ba": r_direct_ba,
        "add_err": float(r_joint_ab - (ra + rb)),
        "step_err": float(rb_after - rb),
        "step_err_ba": float(ra_after - ra),
        "tele_err_ab": float(r_joint_ab - r_direct_ab),
        "tele_err_ba": float(r_joint_ba - r_direct_ba),
        "finals_equal": bool(finals_eq),
    }


# ---------------------------------------------------------------------------
# RES-0J: sequential composition + confluent collapse orders
# ---------------------------------------------------------------------------

def sequence_r_record(name: str, ftag: str = "uniform") -> dict:
    """Frozen MERGE-0 sequence + per-step R books (telescoping check)."""
    srec = m0.sequence_record(name, ftag)
    r_steps = []
    for st in srec["steps"]:
        if st["status"] != "contracted":
            r_steps.append(None)
            continue
        r_steps.append(float(-(st["dEpsi"] + st["dE"])))
    done = [r for r in r_steps if r is not None]
    r_total = float(sum(done))
    direct = -float((srec["W1"] - srec["W0"]) + (srec["E1"] - srec["E0"]))
    srec["R_steps"] = r_steps
    srec["R_total"] = r_total
    srec["R_direct"] = direct
    srec["tele_err"] = float(r_total - direct)
    return srec


def contraction_order(spec: str) -> dict:
    """Frozen full-collapse orders (externally supplied graph orders).

    path8-fwd: lowest-elist greedy (MERGE-0 path8-collapse). path8-rev:
    highest-elist greedy. tri-o1/o2: the two triangle collapse orders.
    Every order fully collapses to one node (checked, not assumed).
    """
    from bh_graph.contraction import contract_edge

    if spec in ("path8-fwd", "path8-rev"):
        sub = m0.build_substrate("path-8")
        g = sub["g"].copy()
        seq = []
        while g.number_of_nodes() > 1:
            elist = sorted(tuple(sorted(x)) for x in g.edges())
            e = elist[0] if spec == "path8-fwd" else elist[-1]
            seq.append([e[0], e[1]])
            g, _, _ = contract_edge(g, *e)
        return {"sub": sub, "edges": seq}
    if spec in ("tri-o1", "tri-o2"):
        sub = m0.build_substrate("triangle")
        first = (0, 1) if spec == "tri-o1" else (1, 2)
        other = 2 if spec == "tri-o1" else 0
        g = sub["g"].copy()
        g, k, _ = contract_edge(g, *first)
        seq = [[first[0], first[1]], [k, other]]
        return {"sub": sub, "edges": seq}
    raise ValueError(f"unknown order spec: {spec}")


def order_record(spec: str, ftag: str) -> dict:
    """Execute one frozen collapse order stepwise; file R books + final."""
    from bh_graph.backreaction import energy_full as _ef

    osp = contraction_order(spec)
    sub = osp["sub"]
    g = sub["g"].copy()
    order = list(sub["order"])
    psi = np.asarray(m0.build_field(sub, ftag), dtype=np.complex128)
    sum0 = complex(np.sum(psi))
    n0, e0count = g.number_of_nodes(), g.number_of_edges()
    q0 = float(np.sum(np.abs(psi) ** 2))
    w0 = float(_ef(psi, g, order))
    steps = []
    for step, (i, j) in enumerate(osp["edges"]):
        if not g.has_edge(i, j):
            steps.append({"step": step, "edge": [i, j],
                          "status": "label-retired"})
            break
        df = merge_deficit(g, psi, order, i, j)
        post = m0.contract_deterministic(g, psi, order, i, j)
        g, psi, order = post["g"], post["psi"], post["order"]
        steps.append({"step": step, "edge": [i, j],
                      "status": "contracted", "R": df["R"],
                      "dE_G": df["dE_G"],
                      "dEpsi": df["dEpsi_direct"]})
    done = [s for s in steps if s["status"] == "contracted"]
    r_total = float(sum(s["R"] for s in done))
    w1 = float(_ef(psi, g, order))
    direct = -float((w1 - w0) + (g.number_of_edges() - e0count))
    return {"spec": spec, "ftag": ftag, "steps": steps,
            "R_total": r_total, "R_direct": direct,
            "tele_err": float(r_total - direct),
            "N0": n0, "E0": e0count, "Q0": q0, "W0": w0,
            "N1": g.number_of_nodes(), "E1": g.number_of_edges(),
            "Q1": float(np.sum(np.abs(psi) ** 2)), "W1": w1,
            "sum0": [float(sum0.real), float(sum0.imag)],
            "final_field": [[float(v.real), float(v.imag)] for v in psi],
            "final_edges": sorted(tuple(sorted(e)) for e in g.edges()),
            "final_order": list(order)}


# ---------------------------------------------------------------------------
# RES-0N/O: texture states (VAC-TEXTURE gradients, E = 0 backgrounds)
# ---------------------------------------------------------------------------

def texture_record(subname: str, family: str, params: dict,
                   edge_idx: int) -> dict:
    """R books for one frozen hidden texture at one frozen edge."""
    from bh_graph import vactexture as _tx

    sub = m0.build_substrate(subname)
    edge = m0.frozen_edges(sub)[edge_idx]
    L = int(subname.split("-L")[1])
    vsub = _tx.j2_substrate(L)
    amap = _tx.alpha_map(family, L, dict(params))
    psi_v = _tx.texture_state(amap, vsub, _tx.A_HEADLINE)
    psi = _align_to(psi_v, vsub["order"], sub["order"])
    df = merge_deficit(sub["g"], psi, sub["order"], *edge)
    grad = _tx.gradient_strength(amap, L)
    q_direct = float(np.sum(np.abs(psi) ** 2))
    q_formula = float(_tx.texture_norm2(amap, _tx.A_HEADLINE, L))
    loc = locality_report(sub["g"], psi, sub["order"], *edge)
    return {"sub": subname, "family": family, "params": dict(params),
            "edge": list(edge), "R": df["R"],
            "R_cover": df["R_cover"], "R_fiber": df["R_fiber"],
            "R_mixed": df["R_mixed"], "c": df["c"], "B": df["B"],
            "E": df["E0"], "Q_direct": q_direct, "Q_formula": q_formula,
            "grad": {k: float(v) for k, v in grad.items()
                     if isinstance(v, (int, float, np.floating))},
            "loc_ok": bool(is_locality_ok(loc)),
            "support_class": loc["class"]}


# ---------------------------------------------------------------------------
# RES-0P: excitation response (exact linear + quadratic split)
# ---------------------------------------------------------------------------

def excresp_record(kind: str, vac: str, eps: float) -> dict:
    """R response to a VAC-EXC disturbance (polarization-identity split).

    R is exactly quadratic in psi (plus the graph constant), so with
    R0 = R(vac), Rp = R(vac+delta), Rm = R(vac-delta):
    linear part L = (Rp - Rm)/2, quadratic part Q = (Rp + Rm)/2 - R0,
    and deltaR = Rp - R0 = L + Q exactly (no fitting anywhere).
    """
    from bh_graph import vacexc as _x

    sub = m0.build_substrate(EXCRESP_SUB)
    ftag = f"X:{kind}@{vac}"
    edge = m0.support_edge(sub, ftag)
    if edge is None:
        edge = m0.task_edges(sub, ftag)[0]
    vsub = _x.j2_substrate(sub["L"])
    carrier = np.asarray(_x.vacuum_shape(vac, vsub), dtype=np.complex128)
    delta = np.asarray(_x.excitation_delta(kind, carrier, vsub,
                                           float(eps), 1.0, "abs"),
                       dtype=np.complex128)
    psi0 = _align_to(carrier, vsub["order"], sub["order"])
    dpsi = _align_to(delta, vsub["order"], sub["order"])
    r0 = merge_deficit(sub["g"], psi0, sub["order"], *edge)["R"]
    rp = merge_deficit(sub["g"], psi0 + dpsi, sub["order"], *edge)["R"]
    rm = merge_deficit(sub["g"], psi0 - dpsi, sub["order"], *edge)["R"]
    lin = float((rp - rm) / 2.0)
    quad = float((rp + rm) / 2.0 - r0)
    delta_r = float(rp - r0)
    ratio = (float(abs(quad) / abs(lin)) if abs(lin) > 1e-12 else None)
    return {"sub": EXCRESP_SUB, "kind": kind, "vac": vac,
            "eps": float(eps), "edge": list(edge),
            "R0": float(r0), "Rp": float(rp), "Rm": float(rm),
            "deltaR": delta_r, "L": lin, "Q": quad,
            "decomp_err": float(delta_r - lin - quad),
            "ratio": ratio}


# ---------------------------------------------------------------------------
# Verdict ladder (frozen, pre-data)
# ---------------------------------------------------------------------------

APPARATUS_GATES = (
    "count-events", "count-fiber", "count-fiberj2", "count-texture",
    "count-excresp", "count-disjoint", "count-order", "count-seq",
    "A-det", "A-rcov", "A-ucov", "A-dQ2B", "A-energy", "A-P34",
    "A-support", "A-signflip", "B-formula", "B-farfield", "B-faredge",
    "B-commonfield", "B-class", "C-u1", "C-rel", "C-swap", "C-sheet",
    "C-xi", "J-nostop", "O-nofire", "R-nosim", "R-verdict",
)
FORMULA_GATES = ("E-formula", "F-sep", "G-forward", "K-invert")


def verdict_from_gates(gates: dict, r_allzero: bool) -> dict:
    """Frozen ladder mapping (gates in, rung out; books only, no q).

    INCOMPLETE if any apparatus/locality/covariance/firewall gate is
    red. CLOSED if R vanishes identically (contradicts the banked
    no-go: genuine surprise). XI if R is an exact nontrivial
    zero-parameter function of xi on both legs. PARTIAL if exactly one
    leg carries R variation (blind leg filed). SEPARATE if R is blind
    to the whole fiber. Mixed correspondence reds -> INCOMPLETE.
    """
    g = dict(gates)
    bad_app = [k for k in APPARATUS_GATES if not g.get(k, False)]
    if bad_app:
        return {"verdict": "RES0-INCOMPLETE",
                "reason": f"apparatus red: {bad_app}"}
    if bool(r_allzero):
        return {"verdict": "RES0-CLOSED",
                "reason": "R vanishes identically: known ledger closes"}
    formula_ok = all(g.get(k, False) for k in FORMULA_GATES)
    if not formula_ok:
        bad = [k for k in FORMULA_GATES if not g.get(k, False)]
        return {"verdict": "RES0-INCOMPLETE",
                "reason": f"correspondence formula red: {bad}"}
    d_leg = bool(g.get("E-dvar", False) and g.get("H-dropd", False))
    c_leg = bool(g.get("F-cvar", False) and g.get("H-dropc", False))
    if d_leg and c_leg:
        return {"verdict": "RES0-XI",
                "reason": "R is an exact nontrivial function of xi"}
    if d_leg and not c_leg:
        return {"verdict": "RES0-PARTIAL",
                "reason": "d leg carries R; cover leg blind (filed)"}
    if c_leg and not d_leg:
        return {"verdict": "RES0-PARTIAL",
                "reason": "cover leg carries R; d leg blind (filed)"}
    if not d_leg and not c_leg:
        return {"verdict": "RES0-SEPARATE",
                "reason": "R blind to the whole xi fiber"}
    return {"verdict": "RES0-INCOMPLETE",
            "reason": "unreachable ladder fallthrough"}


def candidate_requirements(gates: dict, facts: dict) -> dict:
    """Derived constraints on a hypothetical added local state (RES-0Q).

    Pure derivation from gate outcomes + filed census facts. Classifies
    what an added store would have to satisfy (transformation law,
    locality, additivity, update rule, storage options); chooses none
    and simulates nothing. Every row cites the gates behind it.
    """
    g = dict(gates)
    f = dict(facts)
    rows = []
    rows.append({
        "id": "transformation",
        "constraint": ("values invariant under R x U(1) relabel/phase, "
                       "covariant under sheet exchange and endpoint swap"),
        "cited": ["C-u1", "C-rel", "C-swap", "C-sheet", "C-xi"],
        "status": ("earned" if all(g.get(k, False) for k in
                                   ("C-u1", "C-rel", "C-swap", "C-sheet",
                                    "C-xi")) else "withheld")})
    rows.append({
        "id": "locality",
        "constraint": ("update inputs live on " + str(f.get(
            "support_class", "one-neighborhood-local")) + "; far-field, "
            "far-edge, and common-neighbor-field blind"),
        "cited": ["B-formula", "B-farfield", "B-faredge",
                  "B-commonfield", "B-class"],
        "status": ("earned" if all(g.get(k, False) for k in
                                   ("B-formula", "B-farfield", "B-faredge",
                                    "B-commonfield", "B-class"))
                   else "withheld")})
    rows.append({
        "id": "additivity",
        "constraint": ("additive on disjoint merges; cross terms only on "
                       "shared neighborhoods"),
        "cited": ["I-disjoint", "I-step", "I-cross"],
        "status": ("earned" if all(g.get(k, False) for k in
                                   ("I-disjoint", "I-step", "I-cross"))
                   else "withheld")})
    rows.append({
        "id": "update",
        "constraint": ("per-event shift by R = (1+c) - 2B + 2 sum_cross, "
                       "evaluated from the pre-image (needs xi at event "
                       "time); path-independent totals on confluent orders"),
        "cited": ["E-formula", "F-sep", "J-total", "J-path", "K-invert"],
        "status": ("earned" if all(g.get(k, False) for k in
                                   ("E-formula", "F-sep", "J-total",
                                    "J-path", "K-invert")) else "withheld")})
    signs = f.get("signs", {})
    nonneg = not signs.get("has_neg", True)
    rows.append({
        "id": "storage-scalar",
        "constraint": ("signed accumulator viable only with transient xi "
                       "access at events (update needs cover + d)"),
        "cited": ["H-dropd", "H-dropc", "H-ledgerblind"],
        "status": ("earned" if all(g.get(k, False) for k in
                                   ("H-dropd", "H-dropc", "H-ledgerblind"))
                   else "withheld")})
    rows.append({
        "id": "storage-nonnegative",
        "constraint": ("allowed iff no R < 0 observed; excluded otherwise"),
        "cited": ["D-complete"],
        "status": ("excluded" if not nonneg else
                   ("open" if g.get("D-complete", False) else "withheld"))})
    rows.append({
        "id": "storage-vector",
        "constraint": ("relative-mode store alone insufficient: cover leg "
                       "carries R independently"),
        "cited": ["F-cvar", "H-dropc"],
        "status": ("earned" if all(g.get(k, False) for k in
                                   ("F-cvar", "H-dropc")) else "withheld")})
    rows.append({
        "id": "storage-discrete",
        "constraint": ("cover store alone insufficient: d leg carries R "
                       "independently"),
        "cited": ["E-dvar", "H-dropd"],
        "status": ("earned" if all(g.get(k, False) for k in
                                   ("E-dvar", "H-dropd")) else "withheld")})
    rows.append({
        "id": "storage-compound",
        "constraint": "(cover, d) compound store sufficient (XI verdict)",
        "cited": ["E-formula", "F-sep", "G-forward"],
        "status": ("earned" if all(g.get(k, False) for k in
                                   ("E-formula", "F-sep", "G-forward"))
                   else "withheld")})
    return {"rows": rows, "choice": "none (classification only)",
            "simulated": False}


# ---------------------------------------------------------------------------
# Firewall scans (no augmentation / no kinetics anywhere in this apparatus)
# ---------------------------------------------------------------------------

_SUB_FORBID = (
    "trigger", "firing", "temperature", "boltzmann", "metropolis",
    "reservoir_q", "internal_state", "internal", "augment", "shannon",
    "entropy", "binding", "radiation", "heat", "hadron", "quark", "gluon",
    "higgs", "nuclear", "fission", "fusion", "particle", "gibbs",
    "langevin", "mcmc", "thermostat", "anneal", "likelihood", "posterior",
    "random", "rng", "stochastic", "monte", "born", "free_energy",
    "partition_function",
)
_EXACT_FORBID = frozenset({
    "rate", "rates", "prob", "probs", "probability", "prior", "weight",
    "weights", "measure", "measures", "threshold", "thresholds", "fitted",
    "fit", "temp", "beta", "bias", "fire", "fires", "fired", "sample",
    "samples", "markov",
})

def _identifiers_of_source(path: str) -> list:
    """Code identifiers of a Python file (tokenize: strings/comments out).

    The tokenize module yields NAME tokens only for real code; string
    and comment contents (including this scan's own word lists and all
    docstrings) can never flag.
    """
    import io
    import tokenize

    with open(path, "rb") as f:
        toks = tokenize.tokenize(f.readline)
        return [t.string for t in toks if t.type == tokenize.NAME]


def is_file_clean_ok(path: str) -> bool:
    """Boolean: file builds no kinetics/augmentation/state (never raises)."""
    try:
        bad = []
        for tok in _identifiers_of_source(path):
            low = tok.lower()
            if low in _EXACT_FORBID or any(s in low for s in _SUB_FORBID):
                bad.append(tok)
        return not bad
    except Exception:
        return False


def filed_tokens(path: str) -> list:
    """Flagged identifiers (empty when clean; audit helper, not a gate)."""
    try:
        out = []
        for tok in _identifiers_of_source(path):
            low = tok.lower()
            if low in _EXACT_FORBID or any(s in low for s in _SUB_FORBID):
                out.append(tok)
        return sorted(set(out))
    except Exception:
        return ["<unreadable>"]


def is_no_added_store_ok() -> bool:
    """Boolean: this module adds no store and no kinetics (never raises)."""
    try:
        return bool(is_file_clean_ok(__file__))
    except Exception:
        return False


def info0_status() -> dict:
    """INFO-0 availability probe (import-only; absence filed, not fatal)."""
    try:
        import bh_graph.info0 as _i  # noqa: F401

        return {"available": True}
    except Exception as exc:
        return {"available": False, "reason": f"{type(exc).__name__}"}
