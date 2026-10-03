"""STORE-0: minimal reversible internal store for merge/split.

Campaign: STORE-0. Tests whether the information discarded by deterministic
merge can be retained in a minimal local hidden internal store q such that
merge becomes information-preserving on the enlarged state (M, q), split
becomes a deterministic recovery operation, the same stored information
closes the exact merge/split energy account, and no stochastic split-fiber
weighting is required when the complete microscopic state is known.

Frozen ontology (read-only consumption, never re-derived):
  - MERGE0-DETERMINISTIC + MERGE0-ACCOUNT-DEBT: unique selected-edge update
    (sum map), exact structural/norm/energy ledger, quantified loss books.
  - SPLIT0-MIXED: M + xi <-> X with xi = (undirected cover, d), minimality
    witnesses, deterministic core, endpoint-swap gauge.
  - INFO0-MATCHED: predecessor/successor information matching.
  - RES0-XI (pinned blob, sibling branch): R_merge = F_R(M, xi),
    R(d) = A + |d|^2/2 + Re(conj(d) W), R_split = -R_merge, disjoint
    additivity, one-neighborhood-local support.
  - FIBER0-DEBT (pinned verdict, sibling branch): rival_A/rival_B normalized
    weightings satisfy every earned constraint (non-uniqueness exhibits).
  - Physical quotient X_phys = X / (R x U1) (SYM0-CLOSED).
  - Hidden-sector states physically distinct (HIDDEN0-SEPARATED + HBR0).
  - Vacuum family VPLUS/VPI/VMINUS (VACFIELD0-JOINT), textures
    (VACTEXTURE-GRADIENT), excitations (VAC-EXC/MERGE-0G).

Preregistered store (STORE0-PREREG, frozen pre-data):
  - Physical content q_xi = xi = (canonical undirected cover, d).
  - Energy readout E_store = R_merge(M, xi), derived from the frozen RES0
    formula, never an independent stored field.
  - Operational frame (k; i, j; swap): event locator filed alongside q,
    fully determined by the merge operation (no freedom). Minimality
    ablation applies to (c, d) only.
  - Multi-event store Q: node-keyed map {merged node: (frame, q)}.
  - Candidates: qR (scalar R), qd (d only), qc (cover only), qxi (full xi).
    No other candidate may be added post-data.

Load-bearing identities derived pre-data (pinned in tests/test_store0.py):
  - (STORE-0D) R(d) = A - |W|^2/2 + |d + W|^2/2 (completing the square):
    same-cover R-level sets are circles in the d-plane (analytic witness
    pairs); cross-cover pairs always exist on multi-cover cells
    (pigeonhole on r^2 = 2(A2 - A1) + |W1|^2 over both orders).
  - (STORE-0D corollary) qR is sufficient iff the cell has a single cover
    and an all-zero merged state (R = 1 + c + |d|^2/2 strictly monotone
    in |d|); insufficient with constructive witness everywhere else.
  - (STORE-0Q) Reverse-insertion-order node-keyed reversal restores the
    forward trajectory exactly (label restoration reinstates consumed
    merged nodes before their stores are consumed).

Firewall (binding): no new force, firing rule, event weight, probability
law, thermal variable, entropy, fitted storage energy/coupling, arbitrary
capacity or decay, particle interpretation. No RNG anywhere. The store is
bookkeeping candidate state, not assumed physical.

This module ADDS the STORE-0 battery/apparatus; it never modifies any
banked module (all consumed read-only). Functions marked FROZEN-REF are
verbatim transcriptions of frozen sibling-branch code (see
data/store0/ref/SOURCES.txt); tests cross-check them against the pinned
blobs (numeric equality + sha256).
"""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
import math
import os

import networkx as nx
import numpy as np

from bh_graph import merge0 as m0
from bh_graph.merge0 import BAR_FP, BAR_LEDGER, BAR_PHYS, BAR_U1

MAP = "sum"  # frozen contraction map (BR-2.5/2.6/CONS-0 primary)

# ---------------------------------------------------------------------------
# Frozen battery constants
# ---------------------------------------------------------------------------

# Single-event substrates (MERGE-0 battery minus j2-L28: filed cost
# decision, pre-data; L4/L8 + textures cover the vacuum leg).
STORE0_SUBS = ("j2-L4", "j2-L8", "ring-8", "path-8", "triangle",
               "handbuilt", "er-24")

# Deterministic witness probes (no RNG).
D_QD = complex(1.0, 0.0)  # qd-class probe d (fixed for every cell)
D_QC = (0.0j, complex(1.0, 0.0))  # qc-witness pair (SPLIT-0 pinned)
R_CIRCLE_R = 1.0  # same-cover R-level circle radius
R_THETAS = (math.pi / 2.0, math.pi, math.pi / 4.0, 3.0 * math.pi / 4.0,
            math.pi / 3.0)  # deterministic angle fallbacks
MUTATION_DELTA = complex(0.5, -0.25)  # locality mutation (RES0 frozen)

# J2 fiber subset (FROZEN-REF: RES0 cover_subset_j2 rule + constants).
J2_FIBER_L = 4
J2_FIBER_BACKGROUNDS = ("zero", "uniform", "VMINUS")
COVER_CAP_PER_C = 25

# Frozen texture specs (FROZEN-REF: RES0 TEXTURE_SPECS verbatim).
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

# Frozen sequences (FROZEN-REF: RES0 SEQ_TASKS verbatim content).
SEQ_TASKS = [("path8-collapse", "uniform"),
             ("j2L4-ball", "uniform"),
             ("j2L4-ball", "VMINUS"),
             ("handbuilt-chain", "uniform"),
             ("ring8-chain", "uniform")]

# Frozen disjoint/overlap substrates (FROZEN-REF: RES0 pair constants).
PAIR_SUBS = ("path-8", "ring-8", "j2-L4", "handbuilt", "er-24")
PAIR_FIELDS_DIS = {"j2-L4": ("uniform", "random777", "VMINUS"),
                   "path-8": ("uniform", "random777"),
                   "ring-8": ("uniform", "random777"),
                   "handbuilt": ("uniform", "random777"),
                   "er-24": ("uniform", "random777")}
PAIR_FIELDS_OVL = ("random777",)

# Isomorphism-enumeration cap for field-aware class analysis (filed;
# capped pairs are reported honestly, never silently dropped).
ISO_CAP = 2000

# Preregistered candidates (STORE-0B; frozen tuple, no additions).
CANDIDATES = ("qR", "qd", "qc", "qxi")

# Verdict ladder + gate groups (frozen; analyzer consumes, never edits).
VERDICT_LADDER = ("STORE0-REVERSIBLE", "STORE0-INFO", "STORE0-ENERGY",
                  "STORE0-STACK", "STORE0-NULL", "STORE0-INCOMPLETE")
GATE_GROUPS = {
    "counts": ("count-ev", "count-fib", "count-seq", "count-pair",
               "count-detcore", "count-tex"),
    "REG": ("A-det", "A-split", "A-info", "A-R", "A-Rsplit", "A-Rpin"),
    "SINGLE": ("C-qxi", "C-qc", "C-qd", "C-qR", "D-Rcollision",
               "E-covermulti", "F-dvary", "I-rel", "I-u1", "I-Rinv",
               "J-swap", "K-remote", "K-class", "L-merge", "M-split",
               "N-roundtrip", "N-exact", "X-nosample", "X-firewall",
               "Y-pairs"),
    "COMP": ("O-disjoint", "P-adjacent", "Q-reverse", "R-commute",
             "R-overlap", "S-capacity"),
    "BATT": ("T-closed", "T-nonzero", "U-hidden", "V-vac", "V-nofire",
             "W-exc", "B-candidates", "Z-report"),
}


# ---------------------------------------------------------------------------
# Pinned-blob loader (read-only consumption of sibling branches)
# ---------------------------------------------------------------------------

def _ref_dir() -> str:
    """Absolute path of data/store0/ref (pinned frozen blobs)."""
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(os.path.dirname(here))
    return os.path.join(root, "data", "store0", "ref")


def load_pinned_reservoir0():
    """Load the pinned RES0 apparatus module (read-only, no import side
    effects on banked modules). Raises if the blob is absent."""
    path = os.path.join(_ref_dir(), "reservoir0_pin.py")
    spec = importlib.util.spec_from_file_location("reservoir0_pin", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def pinned_verdict(name: str) -> dict:
    """Load a pinned verdict JSON (name without extension)."""
    import json

    path = os.path.join(_ref_dir(), f"{name}_verdict.json")
    with open(path) as f:
        return json.load(f)


def ref_sha256(name: str) -> str:
    """sha256 of a pinned ref blob (audit helper)."""
    path = os.path.join(_ref_dir(), name)
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


# ---------------------------------------------------------------------------
# R core (FROZEN-REF: verbatim RES0 transcription, see SOURCES.txt)
# ---------------------------------------------------------------------------

def merge_deficit_frozen(g: nx.Graph, psi: np.ndarray, order: list,
                         i, j) -> dict:
    """Exact merge deficit R for one selected-edge contraction (X -> M).

    FROZEN-REF: verbatim transcription of RES0 merge_deficit
    (reservoir0_pin.py @ 63fcec3). R = -(Delta E_psi + Delta E_G) with
    Delta E_psi direct (E1 - E0) and Delta E_G = -(1+c). Pure readout.
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


def is_deficit_formula_ok(rep: dict, atol: float = BAR_LEDGER) -> bool:
    """Boolean: direct R matches the BR-2.6 formula (never raises).

    FROZEN-REF: verbatim transcription of RES0 is_deficit_formula_ok."""
    try:
        form = rep["R_cover"] + rep["R_fiber"] + 2.0 * rep["cross"]
        return bool(abs(rep["R"] - form) <= atol
                    and rep["dE_direct"] == rep["dE_G"] == -(1 + rep["c"])
                    and rep["dN_direct"] == -1
                    and abs(rep["dEpsi_direct"] - rep["dEpsi_formula"]) <= atol
                    and abs(rep["parts_sum"] - rep["dEpsi_direct"]) <= atol)
    except Exception:
        return False


def r_decomposition(g2: nx.Graph, psi2: np.ndarray, order2: list, k,
                    A, B, d: complex) -> dict:
    """Exact R(d) = A + |d|^2/2 + Re(conj(d) W) parts (zero-parameter).

    FROZEN-REF: verbatim transcription of the RES0 fiber_row
    decomposition block (Acoef/W/Rformula from the frozen ledger).
    A, W depend on (M, cover) only; d is the fiber coordinate.
    """
    from bh_graph.ballistic import index_of

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    d = complex(d)
    idx2 = index_of(order2)
    s = complex(psi2[idx2[k]])
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
    return {"Acoef": float(acoef),
            "W": complex(wsum),
            "c": int(c),
            "s": complex(s),
            "Rformula": float(rform)}


def split_deficit(E_X: float, E_M: float, c: int) -> float:
    """Exact-xi split counterpart R_split (FROZEN-REF RES0 convention).

    R_split = -((E_X - E_M) + (1 + c)); with exact reconstruction X the
    frozen identity R_split = -R_merge holds by the same arithmetic
    (verified numerically, never assumed)."""
    return -float((float(E_X) - float(E_M)) + (1 + int(c)))


def known_energy(g: nx.Graph, psi: np.ndarray, order: list) -> float:
    """Known energy E_known(X) = E_psi + E_G (RES0 account).

    E_psi = <psi|H(G)|psi> (H = -A, J = 1); E_G = edge count, so that
    Delta E_G = -(1+c) on contraction (MERGE-0B) and R_merge =
    E_known(X) - E_known(M) exactly (verified per record)."""
    from bh_graph.backreaction import energy_full as _ef

    psi = np.asarray(psi, dtype=np.complex128)
    return float(_ef(psi, g, list(order))) + float(g.number_of_edges())


def deficit_support(g: nx.Graph, i, j) -> list:
    """Exact psi/graph support of R: {i,j} + exclusive + common neighbors.

    FROZEN-REF: verbatim transcription of RES0 deficit_support."""
    sup = ({i, j} | (set(g.neighbors(i)) | set(g.neighbors(j))) - {i, j})
    return sorted(sup)


def classify_deficit_support(g: nx.Graph, i, j) -> dict:
    """Support class of R (RES-0B four-way ladder, derived not assumed).

    FROZEN-REF: verbatim transcription of RES0 classify_deficit_support."""
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


def cover_subset_j2(g2: nx.Graph, k, cap: int = COVER_CAP_PER_C) -> list:
    """Frozen J2 cover subset: first `cap` covers per c' bucket (ordered).

    FROZEN-REF: verbatim transcription of RES0 cover_subset_j2."""
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


def _closed_nbrs(g: nx.Graph, e) -> set:
    """Closed neighborhood of an edge (FROZEN-REF: RES0 _closed_nbrs)."""
    a, b = e
    return ({a, b} | set(g.neighbors(a)) | set(g.neighbors(b)))


def pair_rule(subname: str, relation: str):
    """Frozen edge-pair rule (deterministic elist scan, outcome-blind).

    FROZEN-REF: verbatim transcription of RES0 pair_rule. disjoint: first
    node-disjoint pair with disjoint closed neighborhoods. overlap: first
    node-disjoint pair with overlapping closed neighborhoods."""
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

    FROZEN-REF: verbatim transcription of RES0 _finals_equal_swap. Order
    ab takes fresh labels (n, n+1) = (a-merged, b-merged); order ba takes
    (n, n+1) = (b-merged, a-merged). Map a<->a, b<->b across."""
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


# ---------------------------------------------------------------------------
# Store encode / decode (preregistered STORE0-PREREG section 3)
# ---------------------------------------------------------------------------

def encode_store(X: dict, i, j) -> dict:
    """Encode the physical store content q_xi = xi from predecessor X.

    q = {cover: canonical undirected [[A],[B]], d: jointly-canonical d}
    via SPLIT0 encode_residual; the stored d is flipped when
    canonicalization flips the true daughter orientation, so that q is a
    gauge-invariant function of the physical state (both endpoint-swap
    partners map to the same pair). Oriented (A_true, B_true) returned
    alongside for the operational frame (locator, not content). Exact
    (no approximation)."""
    from bh_graph import split0 as s0

    enc = s0.encode_residual(X, None, None, i, j)
    key = (tuple(enc["cover_key"][0]), tuple(enc["cover_key"][1]))
    tru = (tuple(sorted(enc["A"])), tuple(sorted(enc["B"])))
    d = complex(enc["d"])
    if tru != key:
        d = -d
    return {"q": {"cover": [list(key[0]), list(key[1])],
                  "d": d},
            "A_true": sorted(enc["A"]), "B_true": sorted(enc["B"]),
            "s": complex(enc["s_check"])}


def make_frame(k, i, j, A_true, B_true, cover_key) -> dict:
    """Operational frame (k; i, j; swap): event locator (not content).

    swap records whether canonicalization flipped the true daughter
    orientation; decode unswaps before assigning (i, j). Fully
    determined by the merge operation (no freedom)."""
    tru = (tuple(sorted(A_true)), tuple(sorted(B_true)))
    key = (tuple(cover_key[0]), tuple(cover_key[1]))
    return {"k": k, "i": i, "j": j, "swap": bool(tru != key)}


def oriented_cover(q: dict, frame: dict | None) -> tuple:
    """Oriented (A, B) for decode: unswap the canonical cover via frame.

    frame=None (quotient leg): canonical order as-is (endpoint gauge)."""
    ca, cb = list(q["cover"][0]), list(q["cover"][1])
    if frame is not None and bool(frame.get("swap", False)):
        return cb, ca
    return ca, cb


def split_recover(g2: nx.Graph, psi2: np.ndarray, order2: list, k,
                  q: dict, frame: dict | None = None,
                  restore_labels: bool = True) -> dict:
    """Deterministic split recovery X' from (M, q) (+ frame).

    (p, q) = fiber_point(s, d); X' = SPLIT0 predecessor_state (exact
    construction). restore_labels=True reuses the frame's original
    (i, j) (free after the merge removed them); False uses canonical
    fresh labels (mod-quotient leg). No weighting is consulted."""
    from bh_graph import split0 as s0
    from bh_graph.ballistic import index_of

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    s = complex(psi2[index_of(order2)[k]])
    d = complex(q["d"])
    A, B = oriented_cover(q, frame)
    if frame is not None and bool(frame.get("swap", False)):
        d = -d
    p, qq = s0.fiber_point(s, d)
    if restore_labels and frame is not None:
        i, j = frame["i"], frame["j"]
    else:
        i, j = s0.fresh_labels(g2)
    X = s0.predecessor_state(g2, psi2, order2, k, set(A), set(B),
                             p, qq, i, j)
    X["i"], X["j"] = i, j
    return X


def candidate_store(q_full: dict, Rval: float, which: str) -> dict:
    """Preregistered candidate projections of the full store (STORE-0B).

    qR: scalar R only. qd: relative mode d only. qc: discrete cover
    only. qxi: full xi = (c, d). Anything else raises (no additions)."""
    if which == "qR":
        return {"R": float(Rval)}
    if which == "qd":
        return {"d": complex(q_full["d"])}
    if which == "qc":
        return {"cover": [list(q_full["cover"][0]),
                          list(q_full["cover"][1])]}
    if which == "qxi":
        return {"cover": [list(q_full["cover"][0]),
                          list(q_full["cover"][1])],
                "d": complex(q_full["d"])}
    raise ValueError(f"unknown candidate: {which}")


# ---------------------------------------------------------------------------
# Physical equivalence (mod R x U(1), SYM0-CLOSED)
# ---------------------------------------------------------------------------

def is_exact_equiv_ok(X1: dict, X2: dict, atol: float = BAR_FP) -> bool:
    """Boolean: label-restored exact identity (never raises).

    Same node set + same edge set + per-node field within atol
    (order-insensitive). Stronger than physical equivalence."""
    try:
        from bh_graph.ballistic import index_of

        g1, p1, o1 = X1["g"], np.asarray(X1["psi"],
                                        dtype=np.complex128), list(X1["order"])
        g2, p2, o2 = X2["g"], np.asarray(X2["psi"],
                                        dtype=np.complex128), list(X2["order"])
        if set(g1.nodes()) != set(g2.nodes()):
            return False
        e1 = {tuple(sorted(e)) for e in g1.edges()}
        e2 = {tuple(sorted(e)) for e in g2.edges()}
        if e1 != e2:
            return False
        i1, i2 = index_of(o1), index_of(o2)
        for v in o1:
            if abs(complex(p1[i1[v]]) - complex(p2[i2[v]])) > atol:
                return False
        return True
    except Exception:
        return False


def align_phase(psi: np.ndarray, ref: np.ndarray) -> np.ndarray:
    """U1 gauge fix: rotate psi to maximize Re<ref|psi> (SYM-0 section)."""
    from bh_graph.sym0 import phase_align

    return phase_align(np.asarray(psi, dtype=np.complex128),
                       np.asarray(ref, dtype=np.complex128))


def _vec_in_order(psi, order, want: list) -> np.ndarray:
    from bh_graph.ballistic import index_of

    psi = np.asarray(psi, dtype=np.complex128)
    idx = index_of(list(order))
    return np.array([complex(psi[idx[v]]) for v in want],
                    dtype=np.complex128)


def is_phys_equiv_map_ok(X1: dict, X2: dict, mapping: dict,
                         atol: float = BAR_LEDGER) -> bool:
    """Boolean: X2 transported by mapping equals X1 mod U(1) (never raises).

    mapping: X1-node -> X2-node. Edge sets compared under the map, fields
    compared up to one global phase (SYM-0 section)."""
    try:
        g1, o1 = X1["g"], list(X1["order"])
        g2, o2 = X2["g"], list(X2["order"])
        if set(mapping.keys()) != set(o1):
            return False
        if set(mapping.values()) != set(o2):
            return False
        e1 = {tuple(sorted(e)) for e in g1.edges()}
        inv = {w: v for v, w in mapping.items()}
        e2b = {tuple(sorted((inv[a], inv[b]))) for a, b in g2.edges()}
        if e1 != e2b:
            return False
        v1 = _vec_in_order(X1["psi"], o1, o1)
        v2 = _vec_in_order(X2["psi"], o2, [mapping[v] for v in o1])
        al = align_phase(v2, v1)
        return bool(float(np.abs(al - v1).max()) <= atol)
    except Exception:
        return False


def is_phys_equiv_ok(X1: dict, X2: dict, d1=None, d2=None,
                     atol: float = BAR_LEDGER) -> bool:
    """Boolean: physical equivalence mod R x U(1) (never raises).

    Same labels: direct (+ optional daughter-swap when d1/d2 given).
    Different labels: rest-identity + daughter correspondence in both
    endpoint orientations (explicit, no blind search). d1/d2 are the two
    daughter pairs ((i1, j1), (i2, j2)) when known."""
    try:
        o1, o2 = list(X1["order"]), list(X2["order"])
        if set(o1) == set(o2) and d1 is None and d2 is None:
            return is_phys_equiv_map_ok(X1, X2, {v: v for v in o1},
                                        atol=atol)
        if d1 is not None and d2 is not None:
            (i1, j1), (i2, j2) = tuple(d1), tuple(d2)
            rest1 = [v for v in o1 if v != i1 and v != j1]
            rest2 = [v for v in o2 if v != i2 and v != j2]
            if set(rest1) != set(rest2):
                return False
            for pair in (((i1, i2), (j1, j2)), ((i1, j2), (j1, i2))):
                mp = {v: v for v in rest1}
                for a, b in pair:
                    mp[a] = b
                if is_phys_equiv_map_ok(X1, X2, mp, atol=atol):
                    return True
            return False
        return False
    except Exception:
        return False


def is_graph_pair_distinct(h1, psi1, o1, h2, psi2, o2,
                           atol: float = BAR_LEDGER) -> dict:
    """Sound+complete physical-distinctness verdict for a state pair.

    Ladder: edge-count (necessary) -> plain isomorphism (necessary) ->
    field-aware isomorphism under every automorphism-map (capped
    enumeration, exact). Returns {distinct: True/False/None,
    reason}. None (capped) is filed honestly, never forced."""
    try:
        if h1.number_of_edges() != h2.number_of_edges():
            return {"distinct": True, "reason": "edge-count"}
        if h1.number_of_nodes() != h2.number_of_nodes():
            return {"distinct": True, "reason": "node-count"}
        gm = nx.isomorphism.GraphMatcher(h1, h2)
        if not gm.is_isomorphic():
            return {"distinct": True, "reason": "non-isomorphic"}
        from itertools import islice

        from bh_graph.ballistic import index_of

        maps = list(islice(gm.isomorphisms_iter(), ISO_CAP + 1))
        if len(maps) > ISO_CAP:
            return {"distinct": None, "reason": "capped"}
        p1 = np.asarray(psi1, dtype=np.complex128)
        p2 = np.asarray(psi2, dtype=np.complex128)
        idx2 = index_of(list(o2))
        for mp in maps:
            v1 = _vec_in_order(p1, o1, list(o1))
            v2 = np.array([complex(p2[idx2[mp[v]]]) for v in o1],
                           dtype=np.complex128)
            al = align_phase(v2, v1)
            if float(np.abs(al - v1).max()) <= atol:
                return {"distinct": False, "reason": "gauge-equivalent"}
        return {"distinct": True, "reason": "gauge-inequivalent-fields"}
    except Exception:
        return {"distinct": None, "reason": "error"}


# ---------------------------------------------------------------------------
# Sufficiency + falsifier witnesses (fiber-level, STORE-0C-H)
# ---------------------------------------------------------------------------

def qxi_sufficiency(g2: nx.Graph, psi2: np.ndarray, order2: list, k,
                    cover, d: complex) -> dict:
    """Full-xi sufficiency: canonical decode recovers X mod quotient.

    cover is canonical (ca, cb); d is the jointly-canonical stored value.
    Builds Xq (quotient leg: canonical decode, fresh labels, no frame)
    and Xt (the flipped oriented lift ((cb,ca),-d), same fresh locus)
    and checks validity + physical equivalence. Xt == Xq holds up to the
    endpoint-swap gauge by joint-canonical construction; any failure is
    a genuine insufficiency. The headline STORE-0G leg."""
    from bh_graph import split0 as s0

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    d = complex(d)
    ca, cb = list(cover[0]), list(cover[1])
    i0, j0 = s0.fresh_labels(g2)
    Xq = split_recover(g2, psi2, order2, k, {"cover": [ca, cb], "d": d},
                       None, restore_labels=False)
    Xt = split_recover(g2, psi2, order2, k, {"cover": [ca, cb], "d": d},
                       {"k": k, "i": i0, "j": j0, "swap": True},
                       restore_labels=True)
    ok_q = s0.is_predecessor_ok(g2, psi2, order2, k, Xq, Xq["i"], Xq["j"])
    ok_t = s0.is_predecessor_ok(g2, psi2, order2, k, Xt, i0, j0)
    equiv = is_phys_equiv_ok(Xt, Xq, (i0, j0), (Xq["i"], Xq["j"]))
    return {"sufficient": bool(ok_t and ok_q and equiv),
            "true_valid": bool(ok_t), "quot_valid": bool(ok_q),
            "equiv": bool(equiv)}


def qc_witness(g2: nx.Graph, psi2: np.ndarray, order2: list, k,
               cover) -> dict:
    """Cover-only insufficiency witness: d=0 vs d=1 on one cover.

    Both decodes valid (SPLIT0 exact) with distinct daughter pairs
    (rho_i, rho_j, B_ij jointly; SPLIT-0 pinned rule). STORE-0F leg."""
    from bh_graph import split0 as s0
    from bh_graph.ballistic import index_of

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    ca, cb = list(cover[0]), list(cover[1])
    i, j = s0.fresh_labels(g2)
    idx2 = index_of(order2)
    s = complex(psi2[idx2[k]])
    Xa = s0.predecessor_state(g2, psi2, order2, k, set(ca), set(cb),
                              *s0.fiber_point(s, D_QC[0]), i, j)
    Xb = s0.predecessor_state(g2, psi2, order2, k, set(ca), set(cb),
                              *s0.fiber_point(s, D_QC[1]), i, j)
    oka = s0.is_predecessor_ok(g2, psi2, order2, k, Xa, i, j)
    okb = s0.is_predecessor_ok(g2, psi2, order2, k, Xb, i, j)
    ia = index_of(Xa["order"])
    ib = index_of(Xb["order"])
    pa = (complex(Xa["psi"][ia[i]]), complex(Xa["psi"][ia[j]]))
    pb = (complex(Xb["psi"][ib[i]]), complex(Xb["psi"][ib[j]]))
    rho_diff = max(abs(abs(pa[0]) ** 2 - abs(pb[0]) ** 2),
                   abs(abs(pa[1]) ** 2 - abs(pb[1]) ** 2))
    b_diff = abs(float(np.real(np.conj(pa[0]) * pa[1]))
                 - float(np.real(np.conj(pb[0]) * pb[1])))
    diff = max(float(rho_diff), float(b_diff))
    necessary = bool(oka and okb and diff > 0.0)
    return {"sufficient": bool(not necessary),
            "both_valid": bool(oka and okb),
            "pair_diff": float(diff), "necessary": necessary}


def qd_classes(g2: nx.Graph, psi2: np.ndarray, order2: list, k,
               covers: list, d: complex = D_QD) -> dict:
    """d-only class analysis: all covers x fixed d (STORE-0E leg).

    Decodes every cover (same fresh daughters) and partitions into
    physical classes (union-find over pairwise distinctness). sufficient
    iff exactly one class. Capped pairs filed honestly (vacuous).

    Exact acceleration (same verdict): decodes are pre-grouped by the
    necessary conditions (edge count, sorted degree sequence); pairs
    across groups are provably distinct without isomorphism work. The
    full within-group ladder runs only on small graphs (N <= 8,
    MERGE-0 automorphism-enumeration precedent); on larger graphs the
    signature-group count is filed as a proven lower bound
    (classes_exact=False) with within-group pairs skipped honestly.
    A cross-group witness proves insufficiency exactly either way."""
    from bh_graph import split0 as s0
    from bh_graph.ballistic import index_of

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    d = complex(d)
    idx2 = index_of(order2)
    s = complex(psi2[idx2[k]])
    i, j = s0.fresh_labels(g2)
    decs = []
    for row in covers:
        _key, A, B = row[0], set(row[1]), set(row[2])
        X = s0.predecessor_state(g2, psi2, order2, k, A, B,
                                 *s0.fiber_point(s, d), i, j)
        decs.append(X)
    n = len(decs)
    parent = list(range(n))
    capped = 0

    def _find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def _union(a, b):
        ra, rb = _find(a), _find(b)
        if ra != rb:
            parent[ra] = rb

    def _sig(X):
        return (X["g"].number_of_edges(),
                tuple(sorted(v for _, v in X["g"].degree())))

    sigs = [_sig(X) for X in decs]
    groups: dict = {}
    for n_, sg in enumerate(sigs):
        groups.setdefault(sg, []).append(n_)
    witness = None
    if len(groups) > 1:
        ga = groups[sorted(groups)[0]][0]
        gb = groups[sorted(groups)[1]][0]
        why = ("edge-count" if sigs[ga][0] != sigs[gb][0]
               else "degree-sequence")
        witness = {"a": ga, "b": gb, "reason": why}
    n_max = max(X["g"].number_of_nodes() for X in decs) if decs else 0
    exact = bool(n_max <= 8)
    skipped = 0
    if exact:
        for members in groups.values():
            for xi in range(len(members)):
                for yi in range(xi + 1, len(members)):
                    x, y = members[xi], members[yi]
                    rep = is_graph_pair_distinct(
                        decs[x]["g"], decs[x]["psi"], decs[x]["order"],
                        decs[y]["g"], decs[y]["psi"], decs[y]["order"])
                    if rep["distinct"] is None:
                        capped += 1
                    elif rep["distinct"] is False:
                        _union(x, y)
                    elif witness is None:
                        witness = {"a": x, "b": y,
                                   "reason": rep["reason"]}
    else:
        for members in groups.values():
            skipped += len(members) * (len(members) - 1) // 2
    if exact:
        classes = len({_find(v) for v in range(n)}) if n else 0
    else:
        classes = len(groups)  # proven lower bound (groups distinct)
    sufficient = bool(n > 0 and exact and classes == 1 and capped == 0)
    if n > 0 and len(groups) > 1:
        sufficient = False
    return {"n_covers": n, "n_classes": int(classes),
            "classes_exact": bool(exact),
            "sufficient": sufficient,
            "capped_pairs": int(capped),
            "skipped_pairs": int(skipped), "witness": witness}


def r_circle_pair(g2: nx.Graph, psi2: np.ndarray, order2: list, k,
                  A, B) -> dict | None:
    """Analytic same-cover R-level pair (STORE-0D construction).

    R(d) = A - |W|^2/2 + |d + W|^2/2: d1 = -W + r, d2 = -W + r e^{i th}
    share R exactly; inequivalence verified numerically (phase-aligned
    daughter fields). Deterministic theta fallbacks; None if exhausted."""
    from bh_graph import split0 as s0

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    i, j = s0.fresh_labels(g2)
    base = r_decomposition(g2, psi2, order2, k, set(A), set(B), 0.0j)
    W = complex(base["W"])
    d1 = -W + complex(R_CIRCLE_R, 0.0)
    r1 = r_decomposition(g2, psi2, order2, k, set(A), set(B), d1)["Rformula"]
    X1 = split_recover(g2, psi2, order2, k,
                       {"cover": [sorted(A), sorted(B)], "d": d1},
                       {"k": k, "i": i, "j": j, "swap": False},
                       restore_labels=True)
    for th in R_THETAS:
        d2 = -W + complex(R_CIRCLE_R * math.cos(th),
                          R_CIRCLE_R * math.sin(th))
        r2 = r_decomposition(g2, psi2, order2, k, set(A),
                             set(B), d2)["Rformula"]
        if abs(r1 - r2) > BAR_LEDGER:
            continue
        X2 = split_recover(g2, psi2, order2, k,
                           {"cover": [sorted(A), sorted(B)], "d": d2},
                           {"k": k, "i": i, "j": j, "swap": False},
                           restore_labels=True)
        v1 = _vec_in_order(X1["psi"], X1["order"], list(X1["order"]))
        v2 = _vec_in_order(X2["psi"], X2["order"], list(X1["order"]))
        if X1["g"].number_of_edges() != X2["g"].number_of_edges():
            ineq = True
        else:
            al = align_phase(v2, v1)
            ineq = bool(float(np.abs(al - v1).max()) > BAR_LEDGER)
        oka = s0.is_predecessor_ok(g2, psi2, order2, k, X1, i, j)
        okb = s0.is_predecessor_ok(g2, psi2, order2, k, X2, i, j)
        if ineq and oka and okb:
            return {"kind": "circle", "theta": float(th),
                    "d1": d1, "d2": d2, "R": float(r1),
                    "R_err": float(r1 - r2)}
    return None


def r_cross_pair(g2: nx.Graph, psi2: np.ndarray, order2: list, k,
                 covers: list) -> dict | None:
    """Analytic cross-cover R-level pair (STORE-0D construction).

    d2 = 0 on cover2 (R2 = A2); d1 = -W1 + r on cover1 with
    r^2 = 2(A2 - A1) + |W1|^2. A witness always exists on multi-cover
    cells (pigeonhole over both orders: r^2_12 + r^2_21 >= 0).
    Decodes differ in edge count (c differs): physically distinct."""
    from bh_graph import split0 as s0

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    for r1 in covers:
        for r2 in covers:
            A1, B1 = set(r1[1]), set(r1[2])
            A2, B2 = set(r2[1]), set(r2[2])
            c1 = len(A1 & B1)
            c2 = len(A2 & B2)
            if c1 == c2:
                continue
            base1 = r_decomposition(g2, psi2, order2, k, A1, B1, 0.0j)
            base2 = r_decomposition(g2, psi2, order2, k, A2, B2, 0.0j)
            A1v, W1 = float(base1["Acoef"]), complex(base1["W"])
            A2v = float(base2["Acoef"])
            rsq = 2.0 * (A2v - A1v) + abs(W1) ** 2
            if rsq < -1e-12:
                continue
            r = math.sqrt(max(rsq, 0.0))
            d1 = -W1 + complex(r, 0.0)
            d2 = 0.0j
            R1 = r_decomposition(g2, psi2, order2, k, A1, B1,
                                 d1)["Rformula"]
            R2 = r_decomposition(g2, psi2, order2, k, A2, B2,
                                 d2)["Rformula"]
            if abs(R1 - R2) > BAR_LEDGER:
                continue
            i, j = s0.fresh_labels(g2)
            X1 = split_recover(g2, psi2, order2, k,
                               {"cover": [sorted(A1), sorted(B1)], "d": d1},
                               {"k": k, "i": i, "j": j, "swap": False},
                               restore_labels=True)
            X2 = split_recover(g2, psi2, order2, k,
                               {"cover": [sorted(A2), sorted(B2)], "d": d2},
                               {"k": k, "i": i, "j": j, "swap": False},
                               restore_labels=True)
            if X1["g"].number_of_edges() == X2["g"].number_of_edges():
                continue
            oka = s0.is_predecessor_ok(g2, psi2, order2, k, X1, i, j)
            okb = s0.is_predecessor_ok(g2, psi2, order2, k, X2, i, j)
            if oka and okb:
                return {"kind": "cross", "c1": int(c1), "c2": int(c2),
                        "d1": d1, "d2": d2, "R": float(R1),
                        "R_err": float(R1 - R2)}
    return None


def is_qR_injective_cell(n_covers: int, allzero: bool) -> bool:
    """Proven qR-injective cells: single cover + all-zero merged state.

    There R = 1 + c + |d|^2/2 is strictly monotone in |d| and the
    physical fiber is the half-line |d| >= 0 (SPLIT-0 quotient): the
    scalar R determines the physical predecessor uniquely."""
    return bool(int(n_covers) == 1 and bool(allzero))


def qr_witness(g2: nx.Graph, psi2: np.ndarray, order2: list, k,
               covers: list) -> dict:
    """Scalar-store verdict for one fiber cell (STORE-0D leg).

    Circle pairs first (same cover), then cross pairs (multi-cover).
    Proven-injective cells (single cover + all-zero M) return
    sufficient=True with the monotone reconstruction check."""
    from bh_graph import split0 as s0

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    allzero = bool(np.all(psi2 == 0.0))
    if is_qR_injective_cell(len(covers), allzero):
        _key, A, B = covers[0][0], set(covers[0][1]), set(covers[0][2])
        c = len(A & B)
        d_true = complex(0.75, -0.5)
        R = r_decomposition(g2, psi2, order2, k, A, B,
                            d_true)["Rformula"]
        rec_abs = math.sqrt(max(2.0 * (R - 1 - c), 0.0))
        ok = bool(abs(rec_abs - abs(d_true)) <= 1e-9)
        return {"sufficient": True, "injective": True,
                "witness": None, "reconstruct_ok": ok}
    for row in covers:
        hit = r_circle_pair(g2, psi2, order2, k, set(row[1]), set(row[2]))
        if hit is not None:
            hit["cover_idx"] = covers.index(row)
            return {"sufficient": False, "injective": False,
                    "witness": hit, "reconstruct_ok": False}
    hit = r_cross_pair(g2, psi2, order2, k, covers)
    if hit is not None:
        return {"sufficient": False, "injective": False,
                "witness": hit, "reconstruct_ok": False}
    s0_unused = s0  # namespace anchor (no-op)
    _ = s0_unused
    return {"sufficient": None, "injective": False,
            "witness": None, "reconstruct_ok": False}


# ---------------------------------------------------------------------------
# Covariance (STORE-0I/J)
# ---------------------------------------------------------------------------

def transport_store_perm(q: dict, frame: dict, perm: dict) -> tuple:
    """Transport (q, frame) through a node relabeling (exact).

    Oriented roundtrip: uncanonicalize via the frame, permute daughter
    neighborhoods, re-canonicalize jointly (d flipped iff the canonical
    order flips). The merged label k is invariant (canonical max+1 fresh
    labels are relabel-invariant on int graphs, MERGE-0A precedent)."""
    At, Bt = oriented_cover(q, frame)
    dt = complex(q["d"])
    if bool(frame.get("swap", False)):
        dt = -dt
    pA = sorted(perm[v] for v in At)
    pB = sorted(perm[v] for v in Bt)
    key = (tuple(pA), tuple(pB))
    ckey = key if key[0] <= key[1] else (key[1], key[0])
    flipped = bool(ckey != key)
    nq = {"cover": [list(ckey[0]), list(ckey[1])],
          "d": -dt if flipped else dt}
    nf = {"k": frame["k"], "i": perm[frame["i"]], "j": perm[frame["j"]],
          "swap": flipped}
    return nq, nf


def transport_store_u1(q: dict, alpha: float) -> dict:
    """Transport q through a global phase: d -> e^{i a} d (cover fixed)."""
    return {"cover": [list(q["cover"][0]), list(q["cover"][1])],
            "d": complex(q["d"]) * complex(math.cos(alpha),
                                           math.sin(alpha))}


def swap_store(q: dict, frame: dict) -> tuple:
    """Endpoint-swap gauge: oriented ((B,A),-d) re-canonicalized jointly.

    Uncanonicalize via the frame, exchange daughters (d -> -d), then
    re-canonicalize (d flipped again iff the canonical order flips).
    An exact involution on (q, frame) pairs."""
    At, Bt = oriented_cover(q, frame)
    dt = complex(q["d"])
    if bool(frame.get("swap", False)):
        dt = -dt
    sA, sB = sorted(Bt), sorted(At)
    key = (tuple(sA), tuple(sB))
    ckey = key if key[0] <= key[1] else (key[1], key[0])
    flipped = bool(ckey != key)
    nq = {"cover": [list(ckey[0]), list(ckey[1])],
          "d": dt if flipped else -dt}
    nf = {"k": frame["k"], "i": frame["j"], "j": frame["i"],
          "swap": flipped}
    return nq, nf


def relabel_covariance_store(g: nx.Graph, psi: np.ndarray, order: list,
                             i, j, seed: int = 11) -> dict:
    """R covariance: recover(R(M), R(q)) == R(X) + R invariant (exact).

    Transports the full enlarged state through a frozen relabeling and
    checks exact reconstruction of the transported predecessor."""
    from bh_graph import sym0 as _s

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    post = m0.contract_deterministic(g, psi, order, i, j)
    g2, psi2, order2, k = post["g"], post["psi"], post["order"], post["k"]
    X = {"g": g, "psi": psi, "order": order}
    enc = encode_store(X, i, j)
    frame = make_frame(k, i, j, enc["A_true"], enc["B_true"],
                       enc["q"]["cover"])
    R0 = merge_deficit_frozen(g, psi, order, i, j)["R"]
    perm = _s.shuffle_perm(list(order), seed=seed)
    R = _s.apply_relabel(g, psi, list(order), perm)
    gR, psiR, orderR = R["g"], R["psi"], R["order"]
    postR = m0.contract_deterministic(gR, psiR, orderR, perm[i], perm[j])
    nq, nf = transport_store_perm(enc["q"], frame, perm)
    XR = {"g": gR, "psi": psiR, "order": orderR}
    Xrec = split_recover(postR["g"], postR["psi"], postR["order"],
                         postR["k"], nq, nf, restore_labels=True)
    R1 = merge_deficit_frozen(gR, psiR, orderR, perm[i], perm[j])["R"]
    # Transported daughters may differ from canonical fresh merged label
    # bookkeeping only through the frame (exact by construction).
    _ = (g2, psi2, order2)
    return {"exact_ok": bool(is_exact_equiv_ok(XR, Xrec)),
            "k_equal": bool(postR["k"] == post["k"]),
            "R_err": float(R1 - R0)}


def u1_covariance_store(g: nx.Graph, psi: np.ndarray, order: list,
                        i, j, alphas=None) -> dict:
    """U(1) covariance: recover(e^{ia}M, e^{ia}q) == e^{ia}X (exact).

    d transforms with the global phase; R is invariant (verified)."""
    from bh_graph import sym0 as _s

    if alphas is None:
        alphas = _s.U1_ALPHAS
    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    post = m0.contract_deterministic(g, psi, order, i, j)
    X = {"g": g, "psi": psi, "order": order}
    enc = encode_store(X, i, j)
    frame = make_frame(post["k"], i, j, enc["A_true"], enc["B_true"],
                       enc["q"]["cover"])
    R0 = merge_deficit_frozen(g, psi, order, i, j)["R"]
    worst_rec = 0.0
    worst_R = 0.0
    for a in alphas:
        a = float(a)
        qp = _s.apply_u1(psi, a)
        postp = m0.contract_deterministic(g, qp, order, i, j)
        nq = transport_store_u1(enc["q"], a)
        Xp = {"g": g, "psi": qp, "order": order}
        Xrec = split_recover(postp["g"], postp["psi"], postp["order"],
                             postp["k"], nq, frame, restore_labels=True)
        from bh_graph.ballistic import index_of

        idx = index_of(order)
        idxr = index_of(Xrec["order"])
        diffs = [abs(complex(Xrec["psi"][idxr[v]]) - complex(qp[idx[v]]))
                 for v in order]
        worst_rec = max(worst_rec, float(max(diffs)) if diffs else 0.0)
        R1 = merge_deficit_frozen(g, qp, order, i, j)["R"]
        worst_R = max(worst_R, abs(float(R1 - R0)))
    return {"rec_maxdiff": float(worst_rec), "R_maxdiff": float(worst_R)}


def swap_covariance_store(g: nx.Graph, psi: np.ndarray, order: list,
                          i, j) -> dict:
    """Endpoint-swap gauge: swapped store recovers swapped X + same R."""
    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    post = m0.contract_deterministic(g, psi, order, i, j)
    X = {"g": g, "psi": psi, "order": order}
    enc = encode_store(X, i, j)
    frame = make_frame(post["k"], i, j, enc["A_true"], enc["B_true"],
                       enc["q"]["cover"])
    R0 = merge_deficit_frozen(g, psi, order, i, j)["R"]
    nq, nf = swap_store(enc["q"], frame)
    Xrec = split_recover(post["g"], post["psi"], post["order"],
                         post["k"], nq, nf, restore_labels=True)
    # Swapped recovery carries daughters (j, i): compare with the
    # daughter-swap orientation against X.
    equiv = is_phys_equiv_ok(X, Xrec, (i, j), (Xrec["i"], Xrec["j"]))
    # R of the swapped event (daughters exchanged): same value.
    R1 = merge_deficit_frozen(g, psi, order, j, i)["R"]
    return {"equiv_ok": bool(equiv), "R_err": float(R1 - R0)}


# ---------------------------------------------------------------------------
# Locality (STORE-0K)
# ---------------------------------------------------------------------------

def locality_report_store(g: nx.Graph, psi: np.ndarray, order: list,
                          i, j) -> dict:
    """Remote-mutation invariance of q, R, reconstruction (exact).

    Mutates one remote node (outside the RES0 support) by the frozen
    MUTATION_DELTA; the store, its energy readout, and the recovered
    predecessor (on the unmutated locus) must not change. Vacuous
    (applicable=False) when no remote node exists."""
    from bh_graph.ballistic import index_of

    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    sup = set(deficit_support(g, i, j))
    remote = [v for v in order if v not in sup]
    if not remote:
        return {"applicable": False}
    v = remote[0]
    idx = index_of(order)
    post = m0.contract_deterministic(g, psi, order, i, j)
    X = {"g": g, "psi": psi, "order": order}
    enc = encode_store(X, i, j)
    frame = make_frame(post["k"], i, j, enc["A_true"], enc["B_true"],
                       enc["q"]["cover"])
    R0 = merge_deficit_frozen(g, psi, order, i, j)["R"]
    psi_m = psi.copy()
    psi_m[idx[v]] = complex(psi_m[idx[v]]) + MUTATION_DELTA
    post_m = m0.contract_deterministic(g, psi_m, order, i, j)
    Xm = {"g": g, "psi": psi_m, "order": order}
    enc_m = encode_store(Xm, i, j)
    R1 = merge_deficit_frozen(g, psi_m, order, i, j)["R"]
    q_same = bool(enc_m["q"]["cover"] == enc["q"]["cover"]
                  and complex(enc_m["q"]["d"]) == complex(enc["q"]["d"]))
    Xr = split_recover(post_m["g"], post_m["psi"], post_m["order"],
                       post_m["k"], enc["q"], frame, restore_labels=True)
    # Recovered predecessor equals the mutated X on the support locus
    # (remote value carried through bit-identically from mutated M).
    Xr_ref = split_recover(post_m["g"], post_m["psi"], post_m["order"],
                           post_m["k"], enc_m["q"], frame,
                           restore_labels=True)
    same_rec = is_exact_equiv_ok(Xr, Xr_ref)
    return {"applicable": True, "remote": v,
            "q_same": q_same, "R_err": float(R1 - R0),
            "rec_same": bool(same_rec)}


def is_locality_store_ok(rep: dict, atol: float = BAR_LEDGER) -> bool:
    """Boolean: locality report passes (never raises)."""
    try:
        if not rep.get("applicable", False):
            return True
        return bool(rep["q_same"] and rep["rec_same"]
                    and abs(rep["R_err"]) <= atol)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Single-event record (STORE-0A/B/I/J/K/L/M/N)
# ---------------------------------------------------------------------------

def event_record_store(sub: dict, ftag: str, edge, psi=None) -> dict:
    """Full single-event store record: merge + store + split roundtrip.

    Files MERGE/SPLIT/INFO/RES regressions, candidate constructibility,
    covariance (R/U1/swap), locality, energy closure (both legs), and
    the exact + quotient roundtrip. Pure readout + exact constructions."""
    from bh_graph import info0 as i0
    from bh_graph import split0 as s0
    from bh_graph.ballistic import index_of

    g, order = sub["g"], sub["order"]
    i, j = edge
    if psi is None:
        psi = m0.build_field(sub, ftag)
    psi = np.asarray(psi, dtype=np.complex128)
    order = list(order)
    idx = index_of(order)
    a = complex(psi[idx[i]])
    b = complex(psi[idx[j]])
    X = {"g": g, "psi": psi, "order": order}

    det = m0.determinism_check(g, psi, order, i, j)
    rcov = m0.relabel_covariance(g, psi, order, i, j)
    ucov = m0.u1_covariance(psi, g, order, i, j)
    post = m0.contract_deterministic(g, psi, order, i, j)
    g2, psi2, order2, k = post["g"], post["psi"], post["order"], post["k"]
    M = {"g": g2, "psi": psi2, "order": order2}

    enc = encode_store(X, i, j)
    q = enc["q"]
    frame = make_frame(k, i, j, enc["A_true"], enc["B_true"], q["cover"])
    df = merge_deficit_frozen(g, psi, order, i, j)
    d_true = -complex(q["d"]) if frame["swap"] else complex(q["d"])
    dec = r_decomposition(g2, psi2, order2, k, set(enc["A_true"]),
                          set(enc["B_true"]), d_true)

    Xrec = split_recover(g2, psi2, order2, k, q, frame,
                         restore_labels=True)
    Xq = split_recover(g2, psi2, order2, k, q, None,
                       restore_labels=False)
    pred_ok = s0.is_predecessor_ok(g2, psi2, order2, k, Xrec, i, j)
    xi_dict = {"cover_key": (tuple(q["cover"][0]), tuple(q["cover"][1])),
               "d": complex(q["d"])}
    rt_ok = s0.is_roundtrip_ok(g2, psi2, order2, k, xi_dict)
    exact_ok = is_exact_equiv_ok(X, Xrec)
    phys_ok = is_phys_equiv_ok(X, Xq, (i, j), (Xq["i"], Xq["j"]))

    R = float(df["R"])
    E_X = known_energy(g, psi, order)
    E_M = known_energy(g2, psi2, order2)
    from bh_graph.backreaction import energy_full as _ef

    E_Xr = float(_ef(np.asarray(Xrec["psi"], dtype=np.complex128),
                     Xrec["g"], Xrec["order"]))
    E_Mf = float(_ef(psi2, g2, order2))
    R_split = split_deficit(E_Xr, E_Mf, df["c"])
    dE_known_m = float(E_M - E_X)
    close_m = float(dE_known_m + R)
    E_Xr_known = float(E_Xr) + float(Xrec["g"].number_of_edges())
    dE_known_s = float(E_Xr_known - E_M)
    close_s = float(dE_known_s - R)

    fl = i0.field_loss(a, b)
    info_ok = bool(abs(complex(fl["s"]) - complex(a + b)) <= BAR_FP
                   and abs(complex(fl["d"]) - complex(a - b)) <= BAR_FP
                   and abs(complex(fl["a_rec"]) - a) <= BAR_FP
                   and abs(complex(fl["b_rec"]) - b) <= BAR_FP)

    rc = relabel_covariance_store(g, psi, order, i, j)
    uu = u1_covariance_store(g, psi, order, i, j)
    sw = swap_covariance_store(g, psi, order, i, j)
    loc = locality_report_store(g, psi, order, i, j)
    sup = classify_deficit_support(g, i, j)

    cands = {c: candidate_store(q, R, c) for c in CANDIDATES}
    return {
        "sub": sub["name"], "ftag": ftag, "edge": [i, j], "k": k,
        "eligible": bool(m0.is_state_eligible_ok(psi, edge, sub)),
        "det_ok": bool(m0.is_deterministic_ok(det)),
        "rcov_ok": bool(m0.is_covariant_ok(rcov)),
        "ucov_ok": bool(m0.is_covariant_ok(ucov)),
        "info_ok": info_ok,
        "R": R, "R_cover": float(df["R_cover"]),
        "R_fiber": float(df["R_fiber"]), "R_mixed": float(df["R_mixed"]),
        "c": int(df["c"]), "B": float(df["B"]),
        "Acoef": float(dec["Acoef"]),
        "W": [float(complex(dec["W"]).real),
              float(complex(dec["W"]).imag)],
        "Rformula": float(dec["Rformula"]),
        "form_err": float(R - float(dec["Rformula"])),
        "formula_ok": bool(is_deficit_formula_ok(df)),
        "R_split": float(R_split),
        "invert_err": float(R + float(R_split)),
        "pred_ok": bool(pred_ok), "roundtrip_ok": bool(rt_ok),
        "exact_ok": bool(exact_ok), "phys_ok": bool(phys_ok),
        "drained": True,
        "E_X": float(E_X), "E_M": float(E_M),
        "close_merge": close_m, "close_split": close_s,
        "store_cov": {"rel_exact": bool(rc["exact_ok"]),
                      "rel_k": bool(rc["k_equal"]),
                      "rel_R": float(rc["R_err"]),
                      "u1_rec": float(uu["rec_maxdiff"]),
                      "u1_R": float(uu["R_maxdiff"]),
                      "swap_equiv": bool(sw["equiv_ok"]),
                      "swap_R": float(sw["R_err"])},
        "locality": {"applicable": bool(loc.get("applicable", False)),
                     "ok": bool(is_locality_store_ok(loc)),
                     "class": sup["class"]},
        "candidates": {c: True for c in cands},
        "E_store_derived": True,
    }


# ---------------------------------------------------------------------------
# Fiber record (STORE-0C/D/E/F/G/H/Y + A-split legs)
# ---------------------------------------------------------------------------

def _canonical_covers(covers: list) -> list:
    """Canonical orientation: (A, B) listed in canonical key order.

    undirected_covers stores the first-seen directed orientation per
    key; fiber rows need the canonical orientation for key-exact
    SPLIT0 roundtrips (same undirected cover, fixed orientation)."""
    out = []
    for key, _A, _B in covers:
        ka, kb = tuple(key[0]), tuple(key[1])
        out.append(((ka, kb), set(ka), set(kb)))
    return out


def _fiber_rows(g2: nx.Graph, psi2: np.ndarray, order2: list, k,
                covers: list, d_values) -> dict:
    """Exact-xi fiber rows: decode + merge + R books (FIB counts)."""
    from bh_graph import info0 as i0
    from bh_graph import split0 as s0

    psi2 = np.asarray(psi2, dtype=np.complex128)
    order2 = list(order2)
    n_rows = 0
    bad_pred = 0
    bad_rt = 0
    bad_form = 0
    bad_inv = 0
    bad_info = 0
    for row in covers:
        _key, A, B = row[0], set(row[1]), set(row[2])
        for d in d_values:
            d = complex(d)
            n_rows += 1
            X = split_recover(g2, psi2, order2, k,
                              {"cover": [sorted(A), sorted(B)], "d": d},
                              {"k": k, "i": "i", "j": "j", "swap": False},
                              restore_labels=False)
            if not s0.is_predecessor_ok(g2, psi2, order2, k, X,
                                        X["i"], X["j"]):
                bad_pred += 1
            xi = {"cover_key": (tuple(sorted(A)), tuple(sorted(B))),
                  "d": d}
            if not s0.is_roundtrip_ok(g2, psi2, order2, k, xi):
                bad_rt += 1
            df = merge_deficit_frozen(X["g"], X["psi"], X["order"],
                                      X["i"], X["j"])
            dec = r_decomposition(g2, psi2, order2, k, A, B, d)
            if abs(float(df["R"]) - float(dec["Rformula"])) > BAR_LEDGER:
                bad_form += 1
            from bh_graph.backreaction import energy_full as _ef

            E_X = float(_ef(np.asarray(X["psi"], dtype=np.complex128),
                            X["g"], X["order"]))
            E_M = float(_ef(psi2, g2, order2))
            Rs = split_deficit(E_X, E_M, df["c"])
            if abs(float(df["R"]) + float(Rs)) > BAR_LEDGER:
                bad_inv += 1
            p, qq = s0.fiber_point(complex(psi2[list(order2).index(k)])
                                   if k in order2 else 0.0j, d)
            _ = (p, qq)
            fl = i0.field_loss(*s0.fiber_point(
                complex(_vec_in_order(psi2, order2, [k])[0]), d))
            if abs(complex(fl["d"]) - d) > BAR_FP:
                bad_info += 1
    return {"n_rows": n_rows, "bad_pred": bad_pred, "bad_rt": bad_rt,
            "bad_form": bad_form, "bad_inv": bad_inv,
            "bad_info": bad_info}


def fiber_record_tiny(graph_name: str, field_name: str, k) -> dict:
    """Full fiber record for one SPLIT-0 tiny cell (all covers x D_SWEEP)."""
    from bh_graph import split0 as s0
    from bh_graph.u0 import undirected_covers

    st = s0.merged_state(graph_name, field_name)
    g2, psi2, order2 = st["g"], st["psi"], st["order"]
    covers = _canonical_covers(undirected_covers(sorted(g2.neighbors(k))))
    rows = _fiber_rows(g2, psi2, order2, k, covers, s0.D_SWEEP)
    first = covers[0]
    qxi_all = True
    for row in covers:
        rep = qxi_sufficiency(g2, psi2, order2, k,
                              (set(row[1]), set(row[2])),
                              s0.D_SWEEP[3])
        qxi_all = qxi_all and rep["sufficient"]
    qc = qc_witness(g2, psi2, order2, k, (set(first[1]), set(first[2])))
    qd = qd_classes(g2, psi2, order2, k, covers, D_QD)
    qr = qr_witness(g2, psi2, order2, k, covers)
    n_iso = len(s0.graph_iso_classes(g2, k))
    return {"cell": f"{graph_name}/{field_name}@{k}",
            "graph": graph_name, "field": field_name, "k": k,
            "d": int(g2.degree(k)), "n_covers": len(covers),
            "n_iso": int(n_iso), "rows": rows,
            "qxi_sufficient": bool(qxi_all),
            "qc": {"sufficient": bool(qc["sufficient"]),
                   "necessary": bool(qc["necessary"]),
                   "pair_diff": float(qc["pair_diff"])},
            "qd": {"sufficient": bool(qd["sufficient"]),
                   "n_classes": int(qd["n_classes"]),
                   "classes_exact": bool(qd["classes_exact"]),
                   "capped": int(qd["capped_pairs"]),
                   "skipped": int(qd["skipped_pairs"]),
                   "witness": bool(qd["witness"] is not None),
                   "reason": (qd["witness"] or {}).get("reason", "")},
            "qR": {"sufficient": qr["sufficient"],
                   "injective": bool(qr["injective"]),
                   "witness": bool(qr["witness"] is not None),
                   "kind": (qr["witness"] or {}).get("kind", ""),
                   "reconstruct_ok": bool(qr["reconstruct_ok"])},
            "y_pair": bool(qc["necessary"])}


def fiber_record_j2(background: str) -> dict:
    """Full fiber record for one J2-L4 spot (capped covers x D_SWEEP)."""
    from bh_graph import split0 as s0

    spot = s0.j2_merged_spot(J2_FIBER_L, background)
    g2, psi2, order2 = spot["g"], spot["psi"], spot["order"]
    k = spot["k"]
    covers = _canonical_covers(cover_subset_j2(g2, k))
    rows = _fiber_rows(g2, psi2, order2, k, covers, s0.D_SWEEP)
    first = covers[0]
    qxi_all = True
    for row in covers:
        rep = qxi_sufficiency(g2, psi2, order2, k,
                              (set(row[1]), set(row[2])),
                              s0.D_SWEEP[3])
        qxi_all = qxi_all and rep["sufficient"]
    qc = qc_witness(g2, psi2, order2, k, (set(first[1]), set(first[2])))
    qd = qd_classes(g2, psi2, order2, k, covers, D_QD)
    qr = qr_witness(g2, psi2, order2, k, covers)
    buckets: dict = {}
    for row in covers:
        cp = len(set(row[1]) & set(row[2]))
        buckets[cp] = buckets.get(cp, 0) + 1
    return {"cell": f"j2-L{J2_FIBER_L}/{background}",
            "background": background, "k": k,
            "d": int(g2.degree(k)), "n_covers": len(covers),
            "buckets": {str(cp): n for cp, n in sorted(buckets.items())},
            "rows": rows,
            "qxi_sufficient": bool(qxi_all),
            "qc": {"sufficient": bool(qc["sufficient"]),
                   "necessary": bool(qc["necessary"]),
                   "pair_diff": float(qc["pair_diff"])},
            "qd": {"sufficient": bool(qd["sufficient"]),
                   "n_classes": int(qd["n_classes"]),
                   "classes_exact": bool(qd["classes_exact"]),
                   "capped": int(qd["capped_pairs"]),
                   "skipped": int(qd["skipped_pairs"]),
                   "witness": bool(qd["witness"] is not None),
                   "reason": (qd["witness"] or {}).get("reason", "")},
            "qR": {"sufficient": qr["sufficient"],
                   "injective": bool(qr["injective"]),
                   "witness": bool(qr["witness"] is not None),
                   "kind": (qr["witness"] or {}).get("kind", ""),
                   "reconstruct_ok": bool(qr["reconstruct_ok"])},
            "y_pair": bool(qc["necessary"])}


# ---------------------------------------------------------------------------
# Sequences (STORE-0P/Q/R/S)
# ---------------------------------------------------------------------------

def sequence_store_record(name: str, ftag: str = "uniform") -> dict:
    """Forward store + exact reverse for a frozen sequence (SEQ legs).

    Forward: merge each frozen edge, storing (frame, q) keyed by the
    merged node. Reverse: split present stored nodes in reverse
    insertion order (locality-forced LIFO for overlapping events),
    consuming each entry. Files books, capacity, and final identity."""
    spec = m0.frozen_sequence(name)
    sub = spec["sub"]
    g = sub["g"].copy()
    order = list(sub["order"])
    psi = np.asarray(m0.build_field(sub, ftag), dtype=np.complex128)
    X0 = {"g": g.copy(), "psi": psi.copy(), "order": list(order)}
    Q: dict = {}
    ins: list = []
    steps = []
    E_prev = known_energy(g, psi, order)
    store_E = 0.0
    for step, (i, j) in enumerate([tuple(e) for e in spec["edges"]]):
        if not g.has_edge(i, j):
            steps.append({"step": step, "edge": [i, j],
                          "status": "label-retired"})
            break
        X = {"g": g, "psi": psi, "order": order}
        enc = encode_store(X, i, j)
        post = m0.contract_deterministic(g, psi, order, i, j)
        g2, psi2, order2, k = (post["g"], post["psi"], post["order"],
                               post["k"])
        df = merge_deficit_frozen(g, psi, order, i, j)
        R = float(df["R"])
        frame = make_frame(k, i, j, enc["A_true"], enc["B_true"],
                           enc["q"]["cover"])
        Q[k] = {"frame": dict(frame), "q": {"cover": [list(c) for c in
                                                      enc["q"]["cover"]],
                                            "d": complex(enc["q"]["d"])}}
        ins.append(k)
        E_now = known_energy(g2, psi2, order2)
        close = float((E_now - E_prev) + R)
        store_E += R
        steps.append({"step": step, "edge": [i, j],
                      "status": "contracted", "k": k,
                      "R": R, "close_merge": close,
                      "deg_k": int(g2.degree(k)),
                      "c": int(df["c"])})
        g, psi, order = g2, psi2, order2
        E_prev = E_now
    Xn = {"g": g, "psi": psi, "order": order}
    # Reverse in reverse insertion order (present-node rule).
    rev_steps = []
    Qwork = {k: {"frame": dict(v["frame"]),
                 "q": {"cover": [list(c) for c in v["q"]["cover"]],
                       "d": complex(v["q"]["d"])}}
             for k, v in Q.items()}
    E_cur = known_energy(g, psi, order)
    for k in reversed(ins):
        if k not in g.nodes():
            rev_steps.append({"k": k, "status": "absent"})
            continue
        v = Qwork.pop(k)
        Xr = split_recover(g, psi, order, k, v["q"], v["frame"],
                           restore_labels=True)
        from bh_graph.backreaction import energy_full as _ef

        E_Xr = float(_ef(np.asarray(Xr["psi"], dtype=np.complex128),
                         Xr["g"], Xr["order"]))
        E_Mf = float(_ef(np.asarray(psi, dtype=np.complex128), g, order))
        c_now = len(set(v["q"]["cover"][0]) & set(v["q"]["cover"][1]))
        Rs = split_deficit(E_Xr, E_Mf, c_now)
        E_Xr_known = E_Xr + float(Xr["g"].number_of_edges())
        R_fwd = float(merge_deficit_frozen(
            Xr["g"], Xr["psi"], Xr["order"],
            v["frame"]["i"], v["frame"]["j"])["R"])
        close = float((E_Xr_known - E_cur) - R_fwd)
        store_E -= R_fwd
        rev_steps.append({"k": k, "status": "split",
                          "R_split": float(Rs), "close_split": close,
                          "invert_err": float(R_fwd + Rs)})
        g, psi, order = Xr["g"], Xr["psi"], Xr["order"]
        E_cur = known_energy(g, psi, order)
    Xfin = {"g": g, "psi": psi, "order": order}
    return {"name": name, "ftag": ftag, "steps": steps,
            "rev_steps": rev_steps,
            "exact_ok": bool(is_exact_equiv_ok(X0, Xfin)),
            "phys_ok": bool(is_phys_equiv_ok(X0, Xfin)),
            "drained": bool(len(Qwork) == 0),
            "store_E_final": float(store_E),
            "capacity": capacity_report(steps)}


def capacity_report(steps: list) -> dict:
    """Store capacity scaling: discrete + continuous + scalar + frame.

    Discrete cover information (counts + graph bits, descriptive),
    continuous relative-mode dimension (dims only, never bits), scalar
    energy readout count, and frame locator overhead. No fitting."""
    from bh_graph.accounting import info_loss_bits as _ilb

    per = []
    for st in steps:
        if st.get("status") != "contracted":
            continue
        ilb = _ilb(int(st["deg_k"]))
        per.append({"step": st["step"], "k": str(st["k"]),
                    "n_covers_directed": int(ilb["n_covers_directed"]),
                    "n_covers_undirected": float(
                        ilb["n_covers_undirected"]),
                    "graph_bits": float(ilb["graph_bits"]),
                    "field_real_dims": 2,
                    "scalar_readouts": 1,
                    "frame_labels": 3, "frame_bits_swap": 1})
    return {"n_events": len(per),
            "total_field_real_dims": 2 * len(per),
            "total_scalar_readouts": len(per),
            "continuous_bits_claimed": False,
            "per_event": per}


# ---------------------------------------------------------------------------
# Pairs (STORE-0O/P/R)
# ---------------------------------------------------------------------------

def pair_store_record(subname: str, ftag: str, relation: str) -> dict:
    """Two-event composition: factorization, additivity, order (PAIR legs).

    Runs both merge orders with per-event stores; disjoint pairs must
    factorize (order-free entries, additive R) and reverse in both
    tie-breaks; overlap pairs file the relative second store + the
    forced reverse chain."""
    from bh_graph.backreaction import energy_full as _ef
    from bh_graph.contraction import contracted_state as _cs

    sub = m0.build_substrate(subname)
    g0, order0 = sub["g"], sub["order"]
    ea, eb = pair_rule(subname, relation)
    psi0 = np.asarray(m0.build_field(sub, ftag), dtype=np.complex128)
    e_init = _ef(psi0, g0, order0)
    eg_init = g0.number_of_edges()

    def _run(e_first, e_second):
        gg, pp, oo = g0.copy(), psi0.copy(), list(order0)
        Q = {}
        ins = []
        Rs = []
        for e in (e_first, e_second):
            X = {"g": gg, "psi": pp, "order": oo}
            enc = encode_store(X, *e)
            df = merge_deficit_frozen(gg, pp, oo, *e)
            post = m0.contract_deterministic(gg, pp, oo, *e)
            k = post["k"]
            frame = make_frame(k, *e, enc["A_true"], enc["B_true"],
                               enc["q"]["cover"])
            Q[k] = {"frame": frame, "q": enc["q"]}
            ins.append(k)
            Rs.append(float(df["R"]))
            gg, pp, oo = post["g"], post["psi"], post["order"]
        return {"g": gg, "psi": pp, "order": oo, "Q": Q, "ins": ins,
                "Rs": Rs}

    A = _run(ea, eb)
    B = _run(eb, ea)
    ra = merge_deficit_frozen(g0, psi0, order0, *ea)["R"]
    rb = merge_deficit_frozen(g0, psi0, order0, *eb)["R"]
    gm, psim, om, ka, _ = _cs(g0, psi0, list(order0), *ea, MAP)
    rb_after = merge_deficit_frozen(gm, psim, om, *eb)["R"]
    gm2, psim2, om2, kb, _ = _cs(g0, psi0, list(order0), *eb, MAP)
    ra_after = merge_deficit_frozen(gm2, psim2, om2, *ea)["R"]
    efin_ab = _ef(A["psi"], A["g"], A["order"])
    efin_ba = _ef(B["psi"], B["g"], B["order"])
    r_direct_ab = -float((efin_ab - e_init)
                         + (A["g"].number_of_edges() - eg_init))
    r_direct_ba = -float((efin_ba - e_init)
                         + (B["g"].number_of_edges() - eg_init))
    finals_eq = _finals_equal_swap(A["g"], A["psi"], A["order"],
                                   A["ins"][0], A["ins"][1],
                                   B["g"], B["psi"], B["order"],
                                   B["ins"][0], B["ins"][1])
    # Factorization: entries agree across orders (a<->a, b<->b).
    qa_ab = A["Q"][A["ins"][0]]["q"]
    qb_ab = A["Q"][A["ins"][1]]["q"]
    qb_ba = B["Q"][B["ins"][0]]["q"]
    qa_ba = B["Q"][B["ins"][1]]["q"]

    def _qeq(q1, q2):
        return bool(list(q1["cover"][0]) == list(q2["cover"][0])
                    and list(q1["cover"][1]) == list(q2["cover"][1])
                    and complex(q1["d"]) == complex(q2["d"]))

    factorize = bool(_qeq(qa_ab, qa_ba) and _qeq(qb_ab, qb_ba))

    def _reverse(state, tiebreak: str):
        gg, pp, oo = state["g"].copy(), state["psi"].copy(), \
            list(state["order"])
        Qw = {k: {"frame": dict(v["frame"]),
                  "q": {"cover": [list(c) for c in v["q"]["cover"]],
                        "d": complex(v["q"]["d"])}}
              for k, v in state["Q"].items()}
        order_keys = list(state["ins"]) if tiebreak == "forward" \
            else list(reversed(state["ins"]))
        chain = []
        for k in order_keys:
            if k not in gg.nodes():
                chain.append({"k": k, "status": "absent"})
                continue
            v = Qw.pop(k)
            Xr = split_recover(gg, pp, oo, k, v["q"], v["frame"],
                               restore_labels=True)
            chain.append({"k": k, "status": "split"})
            gg, pp, oo = Xr["g"], Xr["psi"], Xr["order"]
        Xfin = {"g": gg, "psi": pp, "order": oo}
        X0 = {"g": g0, "psi": psi0, "order": order0}
        return {"exact": bool(is_exact_equiv_ok(X0, Xfin)),
                "drained": bool(len(Qw) == 0), "chain": chain}

    rev_ab_f = _reverse(A, "forward")
    rev_ab_r = _reverse(A, "reverse")
    rev_ba_f = _reverse(B, "forward")
    rev_ba_r = _reverse(B, "reverse")
    overlap = sorted(_closed_nbrs(g0, ea) & _closed_nbrs(g0, eb),
                     key=str)
    return {
        "sub": subname, "ftag": ftag, "relation": relation,
        "ea": list(ea), "eb": list(eb),
        "disjoint_ok": bool(len(overlap) == 0),
        "R_a": float(ra), "R_b": float(rb),
        "R_b_after_a": float(rb_after), "R_a_after_b": float(ra_after),
        "R_joint_ab": float(A["Rs"][0] + A["Rs"][1]),
        "R_joint_ba": float(B["Rs"][0] + B["Rs"][1]),
        "R_direct_ab": float(r_direct_ab),
        "R_direct_ba": float(r_direct_ba),
        "add_err": float(A["Rs"][0] + A["Rs"][1] - (ra + rb)),
        "step_err": float(rb_after - rb),
        "step_err_ba": float(ra_after - ra),
        "tele_err_ab": float(A["Rs"][0] + A["Rs"][1] - r_direct_ab),
        "tele_err_ba": float(B["Rs"][0] + B["Rs"][1] - r_direct_ba),
        "finals_equal": bool(finals_eq),
        "factorize": factorize,
        "rev_ab_forward": {k: v for k, v in rev_ab_f.items()
                           if k != "chain"},
        "rev_ab_reverse": {k: v for k, v in rev_ab_r.items()
                           if k != "chain"},
        "rev_ba_forward": {k: v for k, v in rev_ba_f.items()
                           if k != "chain"},
        "rev_ba_reverse": {k: v for k, v in rev_ba_r.items()
                           if k != "chain"},
    }


# ---------------------------------------------------------------------------
# Deterministic-core control (STORE-0T) + textures (STORE-0V leg)
# ---------------------------------------------------------------------------

def detcore_record(graph_name: str, field_name: str, k) -> dict:
    """Halves-deterministic cell: halves decode + merge + R filing.

    No split-choice information is required (single cover, d = 0);
    files whether energy storage (R) is nonetheless nonzero."""
    from bh_graph import split0 as s0
    from bh_graph.backreaction import energy_full as _ef

    st = s0.merged_state(graph_name, field_name)
    g2, psi2, order2 = st["g"], st["psi"], st["order"]
    det = s0.deterministic_core_status(g2, psi2, order2, k)
    i, j = s0.fresh_labels(g2)
    s = complex(psi2[list(order2).index(k)])
    p, qq = s0.halves_point(s)
    Xh = s0.predecessor_state(g2, psi2, order2, k, set(), set(),
                              p, qq, i, j)
    df = merge_deficit_frozen(Xh["g"], Xh["psi"], Xh["order"], i, j)
    R = float(df["R"])
    E_X = known_energy(Xh["g"], Xh["psi"], Xh["order"])
    E_M = known_energy(g2, psi2, order2)
    close_m = float((E_M - E_X) + R)
    # Store roundtrip on the halves state (frame from the halves X).
    X = {"g": Xh["g"], "psi": Xh["psi"], "order": Xh["order"]}
    enc = encode_store(X, i, j)
    post = m0.contract_deterministic(Xh["g"], Xh["psi"], Xh["order"],
                                     i, j)
    frame = make_frame(post["k"], i, j, enc["A_true"], enc["B_true"],
                       enc["q"]["cover"])
    Xr = split_recover(post["g"], post["psi"], post["order"],
                       post["k"], enc["q"], frame, restore_labels=True)
    E_Xr = float(_ef(np.asarray(Xr["psi"], dtype=np.complex128),
                     Xr["g"], Xr["order"]))
    E_Mf = float(_ef(post["psi"], post["g"], post["order"]))
    Rs = split_deficit(E_Xr, E_Mf, df["c"])
    E_Xr_known = E_Xr + float(Xr["g"].number_of_edges())
    E_M_known = E_Mf + float(post["g"].number_of_edges())
    close_s = float((E_Xr_known - E_M_known) - R)
    return {"cell": f"{graph_name}/{field_name}@{k}",
            "halves_deterministic": bool(det["halves_deterministic"]),
            "graph_deterministic": bool(det["graph_deterministic"]),
            "R": R, "nonzero": bool(abs(R) > BAR_LEDGER),
            "close_merge": close_m, "close_split": close_s,
            "invert_err": float(R + Rs),
            "exact_ok": bool(is_exact_equiv_ok(X, Xr)),
            "phys_ok": bool(is_phys_equiv_ok(X, Xr))}


def texture_store_record(subname: str, family: str, params: dict,
                         edge_idx: int = 0) -> dict:
    """Store roundtrip on a frozen vacuum texture state (TEX leg).

    Texture builders consumed read-only (VACTEXTURE); edge externally
    supplied (frozen first edge); no spontaneous firing constructed."""
    from bh_graph import vactexture as _tx
    from bh_graph.ballistic import index_of

    sub = m0.build_substrate(subname)
    edge = m0.frozen_edges(sub)[edge_idx]
    L = int(subname.split("-L")[1])
    vsub = _tx.j2_substrate(L)
    amap = _tx.alpha_map(family, L, dict(params))
    psi_v = _tx.texture_state(amap, vsub, _tx.A_HEADLINE)
    idx = index_of(vsub["order"])
    psi = np.array([complex(psi_v[idx[v]]) for v in sub["order"]],
                   dtype=np.complex128)
    rec = event_record_store({"name": sub["name"], "g": sub["g"],
                              "order": sub["order"]},
                             f"TEX:{family}", edge, psi=psi)
    grad = _tx.gradient_strength(amap, L)
    rec["texture"] = {
        "family": family, "params": dict(params),
        "grad": {k: float(v) for k, v in grad.items()
                 if isinstance(v, (int, float, np.floating))}}
    return rec


# ---------------------------------------------------------------------------
# Firewall record (STORE-0X legs + FW task)
# ---------------------------------------------------------------------------

def fitted_param_count() -> int:
    """Minimality audit: STORE-0 has zero fitted continuous parameters."""
    return 0


def is_no_hidden_tuning_ok() -> bool:
    """Boolean check: no temperature/weighting/fitted parameter here."""
    try:
        forbidden = ("beta", "temperature", "temp", "weighting", "fitted",
                     "exponent", "preference", "bias", "threshold",
                     "eps_phys", "sigma", "variance", "prior",
                     "likelihood", "prob")
        fns = [merge_deficit_frozen, r_decomposition, split_deficit,
               known_energy, deficit_support, classify_deficit_support,
               cover_subset_j2, pair_rule, encode_store, make_frame,
               oriented_cover, split_recover, candidate_store,
               is_exact_equiv_ok, align_phase, is_phys_equiv_map_ok,
               is_phys_equiv_ok, is_graph_pair_distinct,
               qxi_sufficiency, qc_witness, qd_classes, r_circle_pair,
               r_cross_pair, qr_witness, transport_store_perm,
               transport_store_u1, swap_store, relabel_covariance_store,
               u1_covariance_store, swap_covariance_store,
               locality_report_store, event_record_store,
               fiber_record_tiny, fiber_record_j2, sequence_store_record,
               capacity_report, pair_store_record, detcore_record,
               texture_store_record]
        for fn in fns:
            params = [p.lower() for p in inspect.signature(fn).parameters]
            if any(any(f in p for f in forbidden) for p in params):
                return False
        return True
    except Exception:
        return False


def is_no_measure_ok() -> bool:
    """Boolean check: no weighting/sampling/thermal machinery here.

    Strips triple-quoted strings + comments + string literals, then fails
    on forbidden code tokens/patterns (INFO-0 is_no_shannon_ok pattern).
    Counting logs (math.log2 on integer counts) are allowed: they take
    cover counts, never probability vectors."""
    try:
        import io
        import re
        import tokenize

        src = inspect.getsource(inspect.getmodule(is_no_measure_ok))
        src_nostr = re.sub(r'""".*?"""', ' ', src, flags=re.DOTALL)
        src_nostr = re.sub(r"'''.*?'''", ' ', src_nostr, flags=re.DOTALL)
        toks = []
        for tok in tokenize.generate_tokens(
                io.StringIO(src_nostr).readline):
            if tok.type == tokenize.COMMENT:
                continue
            if tok.type == tokenize.STRING:
                continue
            toks.append(tok.string)
        names = {t.lower() for t in toks}
        forbidden_names = ("shannon", "entropy", "boltzmann", "born",
                           "metropolis", "temperature", "sample", "rng",
                           "gaussian", "maxent", "uniform_measure",
                           "orbit_uniform", "sample_outcome", "firing",
                           "trigger", "rate")
        if any(f in names for f in forbidden_names):
            return False
        code_ns = re.sub(r"\s+", "", " ".join(toks)).lower()
        # NOTE: no bare "-sum" pattern: the frozen R transcription
        # contains ")-sum(" ledger arithmetic (RES0 verbatim); entropy
        # forms are still caught via p-log + entropy-name patterns.
        forbidden_seq = ("scipy.stats", "stats.entropy", "born(",
                         "p*np.log", "p*log",
                         "orbit-uniform", "rng.", "np.random",
                         "random.random", "randomrandom", "choice(")
        return bool(all(f not in code_ns for f in forbidden_seq))
    except Exception:
        return False


def firewall_record() -> dict:
    """FW task record: tuning/weighting scans + pinned FIBER0 exhibits.

    Verifies zero fitted parameters, clean symbol scans, and loads the
    pinned FIBER0-DEBT verdict (rival weightings exist and differ) as
    exhibits only: store roundtrips below use no weighting."""
    from bh_graph import split0 as s0

    verdict = pinned_verdict("fiber0")
    gates = {g["gate"]: g for g in verdict.get("gates", [])}
    mq = gates.get("M-Q-rivals", {})
    # Weighting-free roundtrip exemplars (exact, no rival weights used).
    n_ok = 0
    n_tot = 0
    for gn, fn in (("triangle", "bonding"), ("square", "current")):
        st = s0.merged_state(gn, fn)
        g2, psi2, order2 = st["g"], st["psi"], st["order"]
        k = sorted(g2.nodes())[0]
        from bh_graph.u0 import undirected_covers

        covers = undirected_covers(sorted(g2.neighbors(k)))
        for row in covers[:3]:
            for d in (0.0j, 0.5 - 0.25j):
                n_tot += 1
                rep = qxi_sufficiency(g2, psi2, order2, k,
                                      (set(row[1]), set(row[2])), d)
                n_ok += int(bool(rep["sufficient"]))
    return {"fitted_params": int(fitted_param_count()),
            "no_tuning": bool(is_no_hidden_tuning_ok()),
            "no_measure": bool(is_no_measure_ok()),
            "fiber0_verdict": verdict.get("verdict", ""),
            "rivals_valid": bool(mq.get("ok", False)),
            "rivals_detail": str(mq.get("detail", "")),
            "roundtrips_exact": bool(n_ok == n_tot and n_tot > 0),
            "n_roundtrips": int(n_tot)}


# ---------------------------------------------------------------------------
# Battery enumeration (frozen; campaign + analyzer consume)
# ---------------------------------------------------------------------------

def ev_tasks() -> list:
    """All single-event tasks: (sub, ftag, edge_index, member)."""
    tasks = []
    for sub in STORE0_SUBS:
        s = m0.build_substrate(sub)
        for tag in m0.field_tags(s):
            try:
                edges = m0.task_edges(s, tag)
            except Exception:
                continue
            members = ("A", "B") if tag in m0.PAIR_FIELDS else ("",)
            for ei in range(len(edges)):
                for mb in members:
                    tasks.append((sub, tag, ei, mb))
    return tasks


def fib_tasks() -> list:
    """All fiber tasks: tiny cells + J2 spots."""
    from bh_graph import split0 as s0

    tasks = []
    for cell in s0.split0_cells():
        tasks.append(("tiny", cell["graph"], cell["field"], cell["k"]))
    for bg in J2_FIBER_BACKGROUNDS:
        tasks.append(("j2", bg))
    return tasks


def seq_tasks() -> list:
    """All sequence tasks (frozen RES0 SEQ_TASKS content)."""
    return [("seq", name, ftag) for name, ftag in SEQ_TASKS]


def pair_tasks() -> list:
    """All pair tasks (frozen RES0 pair battery content)."""
    tasks = []
    for sub in PAIR_SUBS:
        for ftag in PAIR_FIELDS_DIS[sub]:
            tasks.append(("pair", sub, ftag, "disjoint"))
        for ftag in PAIR_FIELDS_OVL:
            tasks.append(("pair", sub, ftag, "overlap"))
    return tasks


def detcore_tasks() -> list:
    """All deterministic-core tasks (d(k) == 0 tiny cells)."""
    from bh_graph import split0 as s0

    tasks = []
    for cell in s0.split0_cells():
        if int(cell["d"]) == 0:
            tasks.append(("detcore", cell["graph"], cell["field"],
                          cell["k"]))
    return tasks


def tex_tasks() -> list:
    """All texture tasks (frozen RES0 TEXTURE_SPECS content)."""
    return [("tex", sub, fam, dict(p)) for sub, fam, p in TEXTURE_SPECS]


def all_tasks() -> list:
    """Complete frozen task census (campaign fan-out + analyzer counts)."""
    out = [("ev",) + t for t in ev_tasks()]
    out += [("fib",) + t for t in fib_tasks()]
    out += list(seq_tasks())
    out += list(pair_tasks())
    out += list(detcore_tasks())
    out += list(tex_tasks())
    out.append(("fw",))
    return out
