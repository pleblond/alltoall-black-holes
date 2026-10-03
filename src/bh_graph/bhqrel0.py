"""BH-Q-REL-0: correlation correction to the Q boundary area law (FROZEN pre-data).

Mission (BH-Q-REL-0.tex, OPEN / READY, in hand): extend BHQAREA0-MAX from
isolated boundary Q information to the JOINT boundary information without
changing the earned one-channel formula. Determine whether correlations
preserve the leading area law (AREA-SAME), reduce its coefficient
(AREA-RENORM), break area scaling (NONAREA), or cannot yet be converted
into joint entropy for lack of an earned joint object (MEASURE-DEBT).

Spec legs: A marginal regression; B joint-object legitimacy (stop rule:
no earned joint -> MEASURE-DEBT before entropy claims); C exact small
controls of the total-correlation identity on synthetic qubit states
(non-physical machinery checks); D pair anatomy (pairwise information
status + mechanical covariance diagnostic, frozen bins; never a
pairwise sum as total correlation); E joint boundary entropy; F
scaling; G correlation-length classification (descriptive); H
state-selection controls; I leading coefficient freeze; J subleading
residual; K comparison firewall.

Supersession note: a prior run on branch `cursor/bh-q-rel-0-70d6`
(PR #150) was reconstructed while the spec sheet was out of reach; it
tested pairwise covariance only under its own ladder (filed
BHQREL0-CORRELATED) and did not adjudicate the spec ladder. This branch
is the spec-faithful campaign: legs A/D/G/H reuse its validated
covariance apparatus; legs B/C/E/F/I/J/K and the AREA/MEASURE-DEBT
ladder are new. No campaign data exists on this branch at freeze.

Frozen inputs (read-only, never re-derived, never modified):
  (1) QINFO0-IDENTICAL (qinfo0.py): the earned per-mode functional
      s_Q = h2(P_-) with P_- = |d|^2/(|s|^2+|d|^2).
  (2) BH-like/high-connectivity construction: graphs.build_complete
      (paper Sec-1 all:all interior), via the banked bhqarea0 assembly.
  (3) Mature J3/3D boundary/area source: dim3.build_j3_ball,
      dim3.shells_cuts_vols, dim3.bipartition_j3; frozen law H = -A.
  (4) BH-Q-AREA-0 apparatus + filed data (bhqarea0.py read-only,
      data/bhqarea0/*.json read-only): geometry, states, edge terms,
      and the isolated S_Q^d ladder this campaign regresses against.
  (5) One prior qubit source (haar.py, read-only): the joint
      entropy functional for leg-C synthetic controls only
      (QINFO0-SECTION-2 selected source). Never applied to boundary
      channels (no boundary joint exists).

This module introduces NO dynamics, NO firing law, NO measure on any
fiber, NO invented joint, NO max-entropy completion, NO independence
assumption as a physical claim, NO pairwise-sum total correlation, NO
fitted constant, NO threshold, NO rate. Pairwise statistics are
mechanical normalized covariances of earned per-edge quantities,
never converted to bits. Tolerances are numerical, never physics.

Firewall (binding): the words black-hole entropy, holography,
thermodynamic entropy, Planck scale appear in this module ONLY in
negative firewall statements (docstrings/comments, stripped by the
apparatus audit). No invented-joint, pairwise-information-sum, or
combined total symbol is defined anywhere (gate-audited). The
total-correlation identity is evaluated ONLY on synthetic qubit
controls (leg C) and on conditional synthetic ladders (leg-F/I
logic pins); boundary joint entropy is filed if and only if leg B
legitimates a joint object.
"""

from __future__ import annotations

import hashlib
import inspect
import io
import math
import re
import tokenize

import numpy as np

from bh_graph import bhqarea0 as _bq

# ---------------------------------------------------------------------------
# Frozen design (BHQREL0-PREREG sections 2-4; ladder mirrors BHQAREA0)
# ---------------------------------------------------------------------------

R_LADDER = _bq.R_LADDER
MARGIN = _bq.MARGIN
TOP_RUNGS = _bq.TOP_RUNGS

VARIANTS = _bq.VARIANTS
HEADLINE_STATES = _bq.HEADLINE_STATES
CONTROL_STATES = _bq.CONTROL_STATES

# Relational bars (mechanical round values, never retuned post-data).
CORR_BAR = 0.05
DECAY_FRAC = 0.5
SHORT_D = (1, 2)

REGR_ATOL = 1e-9
FP_ATOL = 1e-12
CENSUS_ATOL = 1e-9

# Row-chunk width for the O(N^2) pair accumulation (scale only; the
# accumulation order is frozen, hence deterministic).
PAIR_CHUNK = 1024

KIND_IDENTITY = "I"

# ---------------------------------------------------------------------------
# Leg-B/C frozen design (prereg sections 2-4)
# ---------------------------------------------------------------------------

# Frozen joint-candidate survey (leg B; mechanical list, pre-data).
CANDIDATE_IDS = ("product", "sdweight", "modehq", "haarjoint", "maxent")

# Frozen rejection vocabulary (leg B verdict reasons).
REJECT_INDEPENDENCE = "firewall-independence"
REJECT_SAMPLE_SPACE = "sample-space"
REJECT_WRONG_OBJECT = "wrong-object"
REJECT_MISSING_OBJECT = "missing-object"
REJECT_MAXENT = "firewall-maxent"
LEGIT = "legit"

# Frozen two-channel synthetic probe cells (leg B certificates).
# Each cell: ((psi_i, psi_j), (psi_k, psi_l)) deterministic constants.
PAIR2_CELLS = (
    ("c1", (complex(1.0, 2.0), complex(3.0, -1.0)),
     (complex(0.3, -0.7), complex(-1.2, 0.4))),
    ("c2", (complex(1.0, 1.0), complex(1.0, 1.0)),
     (complex(1.0, 0.0), complex(0.0, 1.0))),
    ("c3", (complex(3.0, 0.0), complex(1.0, 0.0)),
     (complex(2.0, 0.0), complex(-1.0, 0.0))),
    ("c4", (complex(0.5, 0.8660254037844386),
            complex(0.8660254037844386, -0.5)),
     (complex(1.0, -1.0), complex(2.0, 0.5))),
)

# Frozen gauge probes (leg B invariance certificates).
GAUGE_PHASE = math.pi / 5.0

# Frozen Schmidt-sweep angles (leg C T-identity controls).
SWEEP_ANGLES = (0.0, math.pi / 12.0, math.pi / 6.0, math.pi / 4.0,
                math.pi / 3.0, 5.0 * math.pi / 12.0, math.pi / 2.0)

# Leg-C expected total correlations (exact mathematical values).
T_PRODUCT2 = 0.0
T_BELL = 2.0
T_PRODUCT3 = 0.0
T_GHZ3 = 3.0

# Tolerances (repo precedent: 1e-12 exact algebra, 1e-9 banked SVD).
BANKED_ATOL = 1e-9

# Conditional-path bars (legs F/I/J; frozen mechanical values for the
# joint-exists path and its logic pins; N/A-gated without a joint).
TAU_FRAC = 0.01
KAPPA_REL = 0.05


# ---------------------------------------------------------------------------
# Frozen pair geometry (prereg section 2; structural, no psi)
# ---------------------------------------------------------------------------

def manhattan4(u, v) -> int:
    """J3 word-coordinate distance |dx|+|dy|+|dz|+|db| (frozen bins)."""
    return int(abs(int(u[0]) - int(v[0])) + abs(int(u[1]) - int(v[1]))
               + abs(int(u[2]) - int(v[2])) + abs(int(u[3]) - int(v[3])))


def edge_anatomy(r: int) -> dict:
    """Per-cut-edge endpoint anatomy (structural; no psi, no eigensolver).

    Frozen cut order (bhqarea0.boundary_edges). Per edge: interior index,
    exterior index (ambient-order indices), interior J3 coords. Class
    counts via bincount (O(N), no pair matrix). A pair shares both
    endpoints only for parallel edges, impossible on a simple graph, so
    INT/EXT classes are exclusive by construction (pinned + audited).
    """
    r = int(r)
    if r < 1:
        raise ValueError("rung r must be >= 1")
    g = _bq.ambient_ball(r)
    disk = _bq.region_disk(g, r)
    edges = _bq.boundary_edges(g, disk)
    order = sorted(g.nodes())
    index = {v: k for k, v in enumerate(order)}
    in_idx: list = []
    ex_idx: list = []
    icoords: list = []
    for u, v in edges:
        u_in = u in disk
        v_in = v in disk
        if u_in == v_in:
            raise ValueError("cut edge with both/neither end in disk")
        i_node = u if u_in else v
        e_node = v if u_in else u
        in_idx.append(int(index[i_node]))
        ex_idx.append(int(index[e_node]))
        icoords.append([int(i_node[0]), int(i_node[1]),
                        int(i_node[2]), int(i_node[3])])
    counts = class_counts_from_endpoints(in_idx, ex_idx)
    return {"r": r, "n_bnd": len(edges), "in_idx": in_idx,
            "ex_idx": ex_idx, "icoords": icoords, "counts": counts}


def class_counts_from_endpoints(in_idx, ex_idx) -> dict:
    """INT/EXT/DIS pair counts from endpoint index arrays (O(N))."""
    in_arr = np.asarray(list(in_idx), dtype=np.int64)
    ex_arr = np.asarray(list(ex_idx), dtype=np.int64)
    n = int(in_arr.size)
    if n == 0:
        return {"n": 0, "n_pairs": 0, "n_int": 0, "n_ext": 0,
                "n_dis": 0}
    _, ck_in = np.unique(in_arr, return_counts=True)
    _, ck_ex = np.unique(ex_arr, return_counts=True)
    n_int = int(np.sum(ck_in * (ck_in - 1) // 2))
    n_ext = int(np.sum(ck_ex * (ck_ex - 1) // 2))
    n_pairs = int(n * (n - 1) // 2)
    return {"n": n, "n_pairs": n_pairs, "n_int": n_int,
            "n_ext": n_ext, "n_dis": int(n_pairs - n_int - n_ext)}


def is_partition_ok(r: int) -> bool:
    """Boolean check: bincount counts + matrix exclusivity on rung r.

    Builds the full pair masks (pins call this on small rungs only).
    Never raises.
    """
    try:
        ana = edge_anatomy(int(r))
        return bool(is_anatomy_partition_ok(
            ana["in_idx"], ana["ex_idx"], ana["counts"]))
    except Exception:
        return False


def is_anatomy_partition_ok(in_idx, ex_idx, counts) -> bool:
    """Boolean check: masks exclusive + counts match bincounts.

    Never raises. Full-matrix check (small inputs only).
    """
    try:
        in_arr = np.asarray(list(in_idx), dtype=np.int64)
        ex_arr = np.asarray(list(ex_idx), dtype=np.int64)
        n = int(in_arr.size)
        want = class_counts_from_endpoints(in_arr, ex_arr)
        for k in ("n", "n_pairs", "n_int", "n_ext", "n_dis"):
            if want[k] != counts[k]:
                return False
        if n < 2:
            return bool(want["n_pairs"] == 0)
        stm = np.ones((n, n), dtype=bool)
        triu = np.triu(stm, k=1)
        intm = (in_arr[:, None] == in_arr[None, :]) & triu
        extm = (ex_arr[:, None] == ex_arr[None, :]) & triu
        if bool((intm & extm).any()):
            return False
        if int(intm.sum()) != want["n_int"]:
            return False
        if int(extm.sum()) != want["n_ext"]:
            return False
        dism = ~(intm | extm) & triu
        return bool(int(dism.sum()) == want["n_dis"])
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Pairwise normalized covariance (prereg section 2; pure math, no psi)
# ---------------------------------------------------------------------------

def _class_cell(n_pairs: int, total: float, var: float) -> dict:
    """One filed class/bin cell: count + raw mean + normalized C."""
    if int(n_pairs) <= 0:
        return {"n": 0, "raw": None, "C": None}
    raw = float(total / float(n_pairs))
    if var == 0.0:
        return {"n": int(n_pairs), "raw": raw, "C": None}
    return {"n": int(n_pairs), "raw": raw, "C": float(raw / float(var))}


def relational_census(xs, in_idx, ex_idx, icoords) -> dict:
    """Full pairwise census of one per-edge quantity (deterministic).

    Inputs: per-defined-edge values xs, interior/exterior endpoint
    indices, interior J3 coords. Normalized covariance
    C(P) = mean_{(a<b) in P}[(x_a-xbar)(x_b-xbar)] / Var(x) per pair
    class (INT/EXT/DIS) and per exact Manhattan4 distance d over
    disjoint pairs. SHORT pools d in {1,2}; LONG pools the top-2 d
    values present. Degenerate (Var == 0): raw filed, C None.
    Never raises (failures filed as {"failed": True}).
    """
    try:
        xs = np.asarray([float(v) for v in xs], dtype=float)
        in_arr = np.asarray(list(in_idx), dtype=np.int64)
        ex_arr = np.asarray(list(ex_idx), dtype=np.int64)
        ico = np.asarray([list(c) for c in icoords], dtype=np.int64)
        n = int(xs.size)
        counts = class_counts_from_endpoints(in_arr, ex_arr)
        if n == 0:
            empty = {"n": 0, "raw": None, "C": None}
            return {"n": 0, "mean": None, "var": None,
                    "degenerate": True, "counts": counts,
                    "int": dict(empty), "ext": dict(empty),
                    "dis": dict(empty), "bins": {}, "short": dict(empty),
                    "long": dict(empty)}
        xbar = float(np.mean(xs))
        var = float(np.var(xs))
        degen = bool(var == 0.0)
        if n < 2 or degen:
            raw0 = 0.0
            cell = {"raw": raw0, "C": None}
            out = {"n": n, "mean": xbar, "var": var,
                   "degenerate": bool(degen), "counts": counts,
                   "int": {"n": counts["n_int"], **cell},
                   "ext": {"n": counts["n_ext"], **cell},
                   "dis": {"n": counts["n_dis"], **cell},
                   "bins": {}, "short": {"n": 0, "raw": None,
                                         "C": None},
                   "long": {"n": 0, "raw": None, "C": None}}
            if n < 2:
                out["degenerate"] = True
            return out
        dev = xs - xbar
        cols = np.arange(n)
        acc_int = [0.0, 0]
        acc_ext = [0.0, 0]
        acc_dis = [0.0, 0]
        per_d: dict = {}
        for start in range(0, n, int(PAIR_CHUNK)):
            stop = min(n, start + int(PAIR_CHUNK))
            rows = np.arange(start, stop)
            prod = dev[rows][:, None] * dev[None, :]
            triu = cols[None, :] > rows[:, None]
            intm = (in_arr[rows][:, None] == in_arr[None, :]) & triu
            extm = (ex_arr[rows][:, None] == ex_arr[None, :]) & triu
            dism = ~(intm | extm) & triu
            acc_int[0] += float((prod * intm).sum())
            acc_int[1] += int(intm.sum())
            acc_ext[0] += float((prod * extm).sum())
            acc_ext[1] += int(extm.sum())
            acc_dis[0] += float((prod * dism).sum())
            acc_dis[1] += int(dism.sum())
            hit_r, hit_c = np.where(dism)
            if hit_r.size:
                gra = rows[hit_r]
                dvals = np.abs(ico[gra] - ico[hit_c]).sum(axis=1)
                pvals = prod[hit_r, hit_c]
                for dd in np.unique(dvals):
                    sel = dvals == dd
                    key = int(dd)
                    prev = per_d.get(key, [0.0, 0])
                    prev[0] += float(pvals[sel].sum())
                    prev[1] += int(sel.sum())
                    per_d[key] = prev
        bins = {}
        for dd in sorted(per_d):
            tot, cnt = per_d[dd]
            bins[str(dd)] = _class_cell(cnt, tot, var)
        short_keys = [d for d in per_d if int(d) in SHORT_D]
        stot = sum(per_d[d][0] for d in short_keys)
        scnt = sum(per_d[d][1] for d in short_keys)
        top2 = sorted(per_d)[-2:]
        ltot = sum(per_d[d][0] for d in top2)
        lcnt = sum(per_d[d][1] for d in top2)
        return {"n": n, "mean": xbar, "var": var, "degenerate": False,
                "counts": counts,
                "int": _class_cell(acc_int[1], acc_int[0], var),
                "ext": _class_cell(acc_ext[1], acc_ext[0], var),
                "dis": _class_cell(acc_dis[1], acc_dis[0], var),
                "bins": bins,
                "short": _class_cell(scnt, stot, var),
                "long": _class_cell(lcnt, ltot, var)}
    except Exception:
        return {"failed": True}


def is_covar_math_ok(atol: float = FP_ATOL) -> bool:
    """Boolean check: hand-verified C on a frozen synthetic vector.

    xs = [1,2,3,4] (mean 2.5, var 1.25); in = [0,0,1,1] (INT pairs
    (0,1):0.75 and (2,3):0.75); ex distinct; icoords pair the INT
    blocks at distance 0/1. INT raw 0.75 C 0.6; EXT empty; DIS raw
    -1.0 C -0.8; bins d=1 raw -1.0 C -0.8; SHORT == LONG == d=1 cell.
    Never raises.
    """
    try:
        xs = [1.0, 2.0, 3.0, 4.0]
        rep = relational_census(xs, [0, 0, 1, 1], [0, 1, 2, 3],
                                [[0, 0, 0, 0], [0, 0, 0, 0],
                                 [1, 0, 0, 0], [1, 0, 0, 0]])
        if rep.get("failed") or rep["degenerate"]:
            return False
        if abs(rep["mean"] - 2.5) > atol or abs(rep["var"] - 1.25) > atol:
            return False
        cell = rep["int"]
        if cell["n"] != 2 or abs(cell["raw"] - 0.75) > atol:
            return False
        if abs(cell["C"] - 0.6) > atol:
            return False
        if rep["ext"]["n"] != 0 or rep["ext"]["C"] is not None:
            return False
        cell = rep["dis"]
        if cell["n"] != 4 or abs(cell["raw"] + 1.0) > atol:
            return False
        if abs(cell["C"] + 0.8) > atol:
            return False
        only = rep["bins"].get("1")
        if only is None or only["n"] != 4:
            return False
        if abs(only["C"] + 0.8) > atol:
            return False
        if abs(rep["short"]["C"] + 0.8) > atol:
            return False
        return bool(abs(rep["long"]["C"] + 0.8) <= atol)
    except Exception:
        return False


def is_binning_ok(atol: float = FP_ATOL) -> bool:
    """Boolean check: per-d bins + SHORT/LONG pools on frozen input.

    xs = [1,2,3,4]; all endpoints distinct (all pairs disjoint);
    icoords [[0..],[1..],[3..],[6..]] give d = 1,3,6,2,5,3 over the
    six pairs with products 0.75,-0.75,-2.25,-0.25,-0.75,0.75.
    SHORT (d in {1,2}): raw 0.25, C 0.2. LONG (top-2 d {5,6}):
    raw -1.5, C -1.2. Never raises.
    """
    try:
        rep = relational_census([1.0, 2.0, 3.0, 4.0], [0, 1, 2, 3],
                                [0, 1, 2, 3],
                                [[0, 0, 0, 0], [1, 0, 0, 0],
                                 [3, 0, 0, 0], [6, 0, 0, 0]])
        if rep.get("failed") or rep["degenerate"]:
            return False
        bins = rep["bins"]
        if abs(bins["1"]["raw"] - 0.75) > atol:
            return False
        if abs(bins["2"]["raw"] + 0.25) > atol:
            return False
        if bins["3"]["n"] != 2 or abs(bins["3"]["raw"]) > atol:
            return False
        if abs(bins["5"]["raw"] + 0.75) > atol:
            return False
        if abs(bins["6"]["raw"] + 2.25) > atol:
            return False
        if abs(rep["short"]["raw"] - 0.25) > atol:
            return False
        if abs(rep["short"]["C"] - 0.2) > atol:
            return False
        if abs(rep["long"]["raw"] + 1.5) > atol:
            return False
        return bool(abs(rep["long"]["C"] + 1.2) <= atol)
    except Exception:
        return False


def is_degenerate_ok(atol: float = FP_ATOL) -> bool:
    """Boolean check: constant vector files degenerate (raw 0, C None).

    Never raises.
    """
    try:
        rep = relational_census([0.5, 0.5, 0.5, 0.5], [0, 0, 1, 2],
                                [0, 1, 2, 3],
                                [[0, 0, 0, 0], [0, 0, 0, 0],
                                 [1, 0, 0, 0], [2, 0, 0, 0]])
        if rep.get("failed") or not rep["degenerate"]:
            return False
        if rep["var"] != 0.0:
            return False
        for key in ("int", "ext", "dis"):
            if rep[key]["C"] is not None:
                return False
            if abs(rep[key]["raw"]) > atol:
                return False
        if rep["int"]["n"] != 1 or rep["dis"]["n"] != 5:
            return False
        if rep["bins"] != {}:
            return False
        if rep["short"]["C"] is not None or rep["long"]["C"] is not None:
            return False
        solo = relational_census([0.25], [0], [1], [[0, 0, 0, 0]])
        if solo.get("failed") or not solo["degenerate"]:
            return False
        void = relational_census([], [], [], [])
        return bool(void.get("degenerate") and void["counts"]["n"] == 0)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Full per-rung record (prereg section 3)
# ---------------------------------------------------------------------------

def run_rel(r: int, variant: str, state: str) -> dict:
    """Full relational record: isolated leg + x/s pairwise census.

    Geometry, states, and edge terms via banked bhqarea0 primitives
    (read-only); the edge loop is mechanical composition. Pairwise
    census over defined (q > 0) edges only. Deterministic under the
    frozen single-thread env.
    """
    from bh_graph import bhqarea0 as bq

    r = int(r)
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant: {variant}")
    states = HEADLINE_STATES if variant == "headline" else CONTROL_STATES
    if state not in states:
        raise ValueError(f"unknown state: {state} for {variant}")
    asm = bq.assemble_adjacency(r, variant)
    psi_rep = bq.state_psi(variant, state, asm)
    psi = np.asarray(psi_rep["psi"], dtype=np.complex128)
    geo = bq.geometry_record(r)
    diskset = set(np.asarray(asm["disk_idx"]).tolist())
    order = asm["order"]
    xs: list = []
    ss: list = []
    in_idx: list = []
    ex_idx: list = []
    icoords: list = []
    zero_pairs = 0
    for iu, iv in asm["cut_pairs"]:
        rep = bq.edge_terms(complex(psi[iu]), complex(psi[iv]))
        if rep is None:
            zero_pairs += 1
            continue
        xs.append(float(rep["x"]))
        ss.append(float(rep["s_Q"]))
        ii = int(iu) if int(iu) in diskset else int(iv)
        ei = int(iv) if int(iu) in diskset else int(iu)
        in_idx.append(ii)
        ex_idx.append(ei)
        node = order[ii]
        icoords.append([int(node[0]), int(node[1]),
                        int(node[2]), int(node[3])])
    n_bnd = len(asm["cut_pairs"])
    n_def = len(xs)
    s_sum = float(sum(ss))
    h_bar = float(s_sum / n_bnd) if n_bnd else 0.0
    kappa = float(s_sum / geo["area"]) if geo["area"] else 0.0
    cen_x = relational_census(xs, in_idx, ex_idx, icoords)
    cen_s = relational_census(ss, in_idx, ex_idx, icoords)
    stats = bq.census_stats(xs) if xs else {"n": 0}
    pairs_unique_ok = bool(
        len(set(zip(in_idx, ex_idx))) == n_def)
    return {"r": r, "variant": variant, "state": state,
            "rmax": geo["rmax"], "n_int": geo["n_int"],
            "n_bnd": n_bnd, "n_defined": n_def,
            "zero_pairs": zero_pairs, "area": geo["area"],
            "sigma": geo["sigma"], "dim3_cut": geo["dim3_cut"],
            "lam": psi_rep["lam"], "eig_residual": psi_rep["residual"],
            "psi_sha256": bq.psi_sha256(psi), "psi_n": int(psi.size),
            "xs": [float(v) for v in xs], "stats": stats,
            "S": s_sum, "hbar": h_bar, "kappa": kappa,
            "kappa_fact": float(geo["sigma"] * h_bar),
            "vol_ratio": float(s_sum / geo["n_int"]),
            "in_idx": [int(v) for v in in_idx],
            "ex_idx": [int(v) for v in ex_idx],
            "icoords": icoords, "pairs_unique_ok": pairs_unique_ok,
            "cen_x": cen_x, "cen_s": cen_s}


# ---------------------------------------------------------------------------
# Leg C: total-correlation identity on synthetic qubit states
# (non-physical machinery checks; never applied to boundary channels)
# ---------------------------------------------------------------------------

def partial_trace_1q(psi, n_qubits: int, target: int) -> np.ndarray:
    """Exact single-qubit reduced density matrix of a pure state.

    Qubit k is bit k of the basis index (k = 0 least significant).
    Exact double loop over spectator configs (n <= 3 here).
    """
    psi = np.asarray(psi, dtype=np.complex128).ravel()
    n = int(n_qubits)
    t = int(target)
    dim = 2 ** n
    if psi.size != dim or not (0 <= t < n):
        raise ValueError("shape/target mismatch")
    rho = np.zeros((2, 2), dtype=np.complex128)
    for rest in range(2 ** (n - 1)):
        idx = [0, 0]
        for a in (0, 1):
            full = 0
            bit = 0
            for k in range(n):
                if k == t:
                    b = a
                else:
                    b = (rest >> bit) & 1
                    bit += 1
                full |= (b << k)
            idx[a] = full
        for a in (0, 1):
            for b in (0, 1):
                rho[a, b] += psi[idx[a]] * np.conj(psi[idx[b]])
    return rho


def vne_1q(rho) -> float:
    """Von Neumann entropy (bits) of a 2x2 density matrix (0 log 0 = 0)."""
    rho = np.asarray(rho, dtype=np.complex128)
    herm = (rho + rho.conj().T) / 2.0
    vals = np.linalg.eigvalsh(herm)
    vals = np.clip(vals.real, 0.0, None)
    return float(-sum(v * math.log2(v) for v in vals if v > 0.0))


def total_corr_pure(psi, n_qubits: int) -> dict:
    """Total correlation T = sum_e H(Q_e) - H(joint), pure n-qubit state.

    Joint pure so H(joint) = 0 exactly (filed, not estimated).
    Single-qubit marginals via exact partial trace.
    """
    n = int(n_qubits)
    hs = [vne_1q(partial_trace_1q(psi, n, k)) for k in range(n)]
    return {"marginals": [float(v) for v in hs], "joint": 0.0,
            "T": float(sum(hs))}


def bell_state() -> np.ndarray:
    """Frozen (|00> + |11>)/sqrt(2) (expected T = 2)."""
    return np.array([1.0, 0.0, 0.0, 1.0],
                    dtype=np.complex128) / math.sqrt(2.0)


def ghz3_state() -> np.ndarray:
    """Frozen (|000> + |111>)/sqrt(2) (expected T = 3)."""
    vec = np.zeros(8, dtype=np.complex128)
    vec[0] = 1.0 / math.sqrt(2.0)
    vec[7] = 1.0 / math.sqrt(2.0)
    return vec


def product_state(n_qubits: int) -> np.ndarray:
    """Frozen |0...0> (expected T = 0)."""
    vec = np.zeros(2 ** int(n_qubits), dtype=np.complex128)
    vec[0] = 1.0
    return vec


def schmidt_pair_state(theta: float) -> np.ndarray:
    """Frozen cos(theta)|00> + sin(theta)|11> (T = 2 h2(cos^2))."""
    return np.array([math.cos(float(theta)), 0.0, 0.0,
                     math.sin(float(theta))], dtype=np.complex128)


def run_smallctrl() -> dict:
    """Leg-C battery: T-identity functional checks (synthetic only).

    Product T = 0 (2- and 3-qubit), Bell T = 2, GHZ T = 3, sweep
    T >= 0 with exact-formula agreement, banked haar cross-checks.
    Never raises (failures filed as None/False).
    """
    try:
        from bh_graph import haar as banked
        from bh_graph import qinfo0 as _q0

        rows = []
        for name, psi, n, want in (
                ("product2", product_state(2), 2, T_PRODUCT2),
                ("bell", bell_state(), 2, T_BELL),
                ("product3", product_state(3), 3, T_PRODUCT3),
                ("ghz3", ghz3_state(), 3, T_GHZ3)):
            try:
                rep = total_corr_pure(psi, n)
                banked_h = float(banked.subsystem_entropy_bits(psi, 1, n))
                rows.append({"cell": name, "n": n, "T": rep["T"],
                             "marginals": rep["marginals"],
                             "want_T": want,
                             "banked_h_first": banked_h,
                             "match": bool(abs(rep["T"] - want)
                                           <= BANKED_ATOL),
                             "banked_match": bool(
                                 abs(rep["marginals"][0] - banked_h)
                                 <= BANKED_ATOL)})
            except Exception:
                rows.append({"cell": name, "failed": True})
        sweep = []
        for theta in SWEEP_ANGLES:
            try:
                psi = schmidt_pair_state(theta)
                rep = total_corr_pure(psi, 2)
                want = 2.0 * _q0.h2_binary(math.cos(theta) ** 2)
                sweep.append({"theta": float(theta), "T": rep["T"],
                              "want": float(want),
                              "nonneg": bool(rep["T"] >= 0.0),
                              "match": bool(abs(rep["T"] - want)
                                            <= BANKED_ATOL)})
            except Exception:
                sweep.append({"theta": float(theta), "failed": True})
        ok = all(r.get("match") and r.get("banked_match") for r in rows) \
            and all(s.get("match") and s.get("nonneg") for s in sweep)
        return {"cells": rows, "sweep": sweep, "all_ok": bool(ok)}
    except Exception:
        return {"failed": True}


def is_t_identity_ok(atol: float = BANKED_ATOL) -> bool:
    """Boolean check: leg-C T values + banked agreement. Never raises."""
    try:
        rep = run_smallctrl()
        if rep.get("failed") or not rep["all_ok"]:
            return False
        for row in rep["cells"]:
            if abs(row["T"] - row["want_T"]) > atol:
                return False
        return True
    except Exception:
        return False


def is_partial_trace_ok(atol: float = FP_ATOL) -> bool:
    """Boolean check: exact reduced states (Bell I/2, product pure).

    Never raises.
    """
    try:
        rho = partial_trace_1q(bell_state(), 2, 0)
        if float(np.max(np.abs(rho - 0.5 * np.eye(2)))) > atol:
            return False
        rho1 = partial_trace_1q(bell_state(), 2, 1)
        if float(np.max(np.abs(rho1 - 0.5 * np.eye(2)))) > atol:
            return False
        rp = partial_trace_1q(product_state(2), 2, 0)
        if abs(float(rp[0, 0]) - 1.0) > atol:
            return False
        if abs(vne_1q(rp)) > atol or abs(vne_1q(rho) - 1.0) > atol:
            return False
        try:
            partial_trace_1q([1.0, 0.0], 2, 5)
            return False
        except ValueError:
            return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Leg B: joint-object legitimacy audit (frozen candidate survey)
# ---------------------------------------------------------------------------

def _pair_marginals(cell) -> tuple:
    """Earned one-channel (P_+, P_-) for both channels of a pair cell."""
    from bh_graph import qinfo0 as _q0

    (_name, (pi, pj), (pk, pl)) = cell
    out = []
    for a, b in ((pi, pj), (pk, pl)):
        w = _q0.mode_weights(_q0.sum_mode(a, b), _q0.diff_mode(a, b))
        out.append((float(w["P_plus"]), float(w["P_minus"])))
    return out[0], out[1]


def _phase_shifted(cell, phi: float):
    """Pair cell with global phase e^{i phi} on all four amplitudes."""
    name, (pi, pj), (pk, pl) = cell
    fac = complex(math.cos(phi), math.sin(phi))
    return (name, (pi * fac, pj * fac), (pk * fac, pl * fac))


def _swap_within(cell):
    """Pair cell with endpoint swap inside each channel."""
    name, (pi, pj), (pk, pl) = cell
    return (name, (pj, pi), (pl, pk))


def audit_product() -> dict:
    """Candidate 1: product of earned one-channel marginals.

    Formal certificates (normalization, positivity, marginals, gauge)
    computed on the frozen pair cells; physical verdict REJECTED: the
    product asserts independence, which the hard firewall forbids as a
    claim about the boundary (control use only, legs C/G precedent).
    """
    try:
        certs = []
        for cell in PAIR2_CELLS:
            (p1p, p1m), (p2p, p2m) = _pair_marginals(cell)
            probs = [p1p * p2p, p1p * p2m, p1m * p2p, p1m * p2m]
            norm = sum(probs)
            pos = min(probs)
            marg1 = (probs[0] + probs[1], probs[2] + probs[3])
            marg2 = (probs[0] + probs[2], probs[1] + probs[3])
            (q1p, q1m), (q2p, q2m) = _pair_marginals(
                _phase_shifted(cell, GAUGE_PHASE))
            phase_dev = max(abs(q1p - p1p), abs(q1m - p1m),
                            abs(q2p - p2p), abs(q2m - p2m))
            (r1p, r1m), (r2p, r2m) = _pair_marginals(_swap_within(cell))
            swap_dev = max(abs(r1p - p1p), abs(r1m - p1m),
                           abs(r2p - p2p), abs(r2m - p2m))
            certs.append({"cell": cell[0], "norm_dev": abs(norm - 1.0),
                          "min_prob": min(probs),
                          "marg_dev": max(abs(marg1[0] - p1p),
                                          abs(marg1[1] - p1m),
                                          abs(marg2[0] - p2p),
                                          abs(marg2[1] - p2m)),
                          "phase_dev": phase_dev, "swap_dev": swap_dev,
                          "pos_ok": bool(pos >= 0.0)})
        formal = all(c["norm_dev"] <= FP_ATOL and c["pos_ok"]
                     and c["marg_dev"] <= FP_ATOL
                     and c["phase_dev"] <= FP_ATOL
                     and c["swap_dev"] <= FP_ATOL for c in certs)
        return {"candidate": "product", "certs": certs,
                "formal_ok": bool(formal),
                "verdict": "REJECTED", "reason": REJECT_INDEPENDENCE,
                "pairwise_note": "pairwise product is the independence "
                                 "assumption: rejected as a physical "
                                 "pair joint (control use only)",
                "full_n_note": "N-channel product inherits formal "
                               "properties by induction (structural; no "
                               "2^N enumeration)"}
    except Exception:
        return {"candidate": "product", "failed": True}


def audit_sdweight() -> dict:
    """Candidate 2: normalized pair/all (s,d)-weight distribution.

    Formal weight certificates computed; verdict REJECTED: the labels
    are mode weights, not joint channel outcomes -- no earned bijection
    to {(+,+),(+,-),(-,+),(--)} at N = 2, and 2N weights vs 2^N joint
    outcomes mismatch for N >= 3 (4 = 4 at N = 2 is coincidence only).
    """
    try:
        from bh_graph import qinfo0 as _q0

        certs = []
        for cell in PAIR2_CELLS:
            _name, (pi, pj), (pk, pl) = cell
            ws = []
            for a, b in ((pi, pj), (pk, pl)):
                s = _q0.sum_mode(a, b)
                d = _q0.diff_mode(a, b)
                ws += [abs(s) ** 2, abs(d) ** 2]
            tot = sum(ws)
            probs = [w / tot for w in ws]
            certs.append({"cell": cell[0],
                          "norm_dev": abs(sum(probs) - 1.0),
                          "min_prob": min(probs),
                          "n_weights": 4, "n_joint_outcomes": 4,
                          "mapping_earned": False})
        counts = [{"N": n, "n_weights": 2 * n,
                   "n_joint_outcomes": 2 ** n,
                   "match": bool(2 * n == 2 ** n)}
                  for n in (1, 2, 3, 4, 10)]
        formal = all(c["norm_dev"] <= FP_ATOL and c["min_prob"] >= 0.0
                     for c in certs)
        return {"candidate": "sdweight", "certs": certs,
                "formal_weights_ok": bool(formal), "counts": counts,
                "verdict": "REJECTED", "reason": REJECT_SAMPLE_SPACE,
                "pairwise_note": "pairwise 4-weight has no earned "
                                 "identification with joint channel "
                                 "outcomes: pairwise information unearned"}
    except Exception:
        return {"candidate": "sdweight", "failed": True}


def audit_mode_hq() -> dict:
    """Candidate 3: QINFO0-J mode-distribution H_Q over d-modes.

    Sanity recomputation of the banked multi-set values; verdict
    REJECTED: the object is a distribution over mode index, not over
    channel outcomes -- per-channel binary marginals are undefined.
    """
    try:
        from bh_graph import qinfo0 as _q0

        sets = {n: ds for n, ds in _q0.MULTI_SETS}
        sanity = {
            "m1": _q0.multi_entropy_hq(list(sets["m1"])),
            "m2": _q0.multi_entropy_hq(list(sets["m2"])),
            "m3": _q0.multi_entropy_hq(list(sets["m3"])),
            "m4": _q0.multi_entropy_hq(list(sets["m4"])),
        }
        ok = abs(sanity["m1"] - 2.0) <= FP_ATOL \
            and sanity["m2"] == 0.0 \
            and abs(sanity["m3"] - 1.0) <= FP_ATOL \
            and abs(sanity["m4"] - _q0.h2_binary(0.1)) <= FP_ATOL
        return {"candidate": "modehq", "sanity": sanity,
                "sanity_ok": bool(ok),
                "marginals_defined": False,
                "verdict": "REJECTED", "reason": REJECT_WRONG_OBJECT}
    except Exception:
        return {"candidate": "modehq", "failed": True}


def audit_haar_joint() -> dict:
    """Candidate 4: banked haar joint on an earned boundary state.

    Mechanical survey (QINFO0-SECTION-2 precedent): the banked
    -sum p log p functional (haar) needs a state; the only earned
    boundary-state construction (QINFO0-F Schmidt) is per-channel
    1-qubit, and tensoring it is the product (candidate 1). No other
    banked module constructs an N-variable boundary state. Verdict
    REJECTED: missing object.
    """
    try:
        from bh_graph import haar as banked
        from bh_graph import qinfo0 as _q0

        survey = {
            "qinfo0": "per-channel Schmidt states only "
                      "(schmidt_state_for_weights, dim 4)",
            "haar": "functional needs a state "
                    "(subsystem_entropy_bits state-arg)",
            "store0_split0": "no probabilities "
                             "(fiber conventions only)",
        }
        banked_ok = callable(banked.subsystem_entropy_bits)
        per_channel_only = _q0.schmidt_state_for_weights(0.5, 0.5).size \
            == 4
        return {"candidate": "haarjoint", "survey": survey,
                "banked_callable": bool(banked_ok),
                "per_channel_only": bool(per_channel_only),
                "boundary_state_found": False,
                "verdict": "REJECTED",
                "reason": REJECT_MISSING_OBJECT}
    except Exception:
        return {"candidate": "haarjoint", "failed": True}


def audit_maxent() -> dict:
    """Candidate 5: maximum-entropy completion given marginals.

    Not constructed: the spec hard firewall forbids max-entropy
    completion a priori. Filed REJECTED without construction.
    """
    return {"candidate": "maxent", "constructed": False,
            "verdict": "REJECTED", "reason": REJECT_MAXENT}


def run_jointaudit(candidate: str) -> dict:
    """Leg-B audit record for one frozen candidate id. Never raises."""
    try:
        cid = str(candidate)
        if cid == "product":
            return audit_product()
        if cid == "sdweight":
            return audit_sdweight()
        if cid == "modehq":
            return audit_mode_hq()
        if cid == "haarjoint":
            return audit_haar_joint()
        if cid == "maxent":
            return audit_maxent()
        return {"candidate": cid, "failed": True}
    except Exception:
        return {"candidate": str(candidate), "failed": True}


def joint_exists_of(audits) -> bool:
    """Leg-B measurement: True iff any audit files LEGIT (else False)."""
    try:
        return bool(any(a.get("verdict") == "LEGIT" for a in audits))
    except Exception:
        return False


def is_jointaudit_ok() -> bool:
    """Boolean check: all 5 audits reject with frozen reasons.

    Never raises. This checks the AUDIT MACHINERY + its outcome on the
    frozen survey (the predicted MEASURE-DEBT path); the analyzer
    re-verifies every certificate number independently.
    """
    try:
        want = {"product": REJECT_INDEPENDENCE,
                "sdweight": REJECT_SAMPLE_SPACE,
                "modehq": REJECT_WRONG_OBJECT,
                "haarjoint": REJECT_MISSING_OBJECT,
                "maxent": REJECT_MAXENT}
        audits = [run_jointaudit(cid) for cid in CANDIDATE_IDS]
        for rep, cid in zip(audits, CANDIDATE_IDS):
            if rep.get("failed"):
                return False
            if rep.get("verdict") != "REJECTED":
                return False
            if rep.get("reason") != want[cid]:
                return False
        if joint_exists_of(audits):
            return False
        prod = audits[0]
        if not prod["formal_ok"]:
            return False
        if len(prod["certs"]) != len(PAIR2_CELLS):
            return False
        sdw = audits[1]
        if not sdw["formal_weights_ok"]:
            return False
        if [c["match"] for c in sdw["counts"]] != \
                [True, True, False, False, False]:
            return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Conditional-path classification (legs F/I/J logic; pure functions)
#
# Implemented + pinned on synthetic ladders. The analyzer calls this with
# real T/H ladders if and only if leg B legitimates a joint; without a
# joint it files N/A (the MEASURE-DEBT path) and these rungs are
# adjudicated-as-gated, never evaluated on invented data.
# ---------------------------------------------------------------------------

def classify_conditional(kappa_iso: float, areas: list, t_vals: list,
                         h_vals: list) -> dict:
    """AREA-SAME / AREA-RENORM / NONAREA on T/H ladders (pure logic).

    SAME: T/A < TAU_FRAC * kappa_iso at top rung and strictly
    decreasing over top-3. RENORM: tau = T/A relatively stable (<
    KAPPA_REL successive, top-3), tau* >= TAU_FRAC * kappa_iso,
    kappa_joint = kappa_iso - tau* > 0. Else NONAREA.
    """
    try:
        k = float(kappa_iso)
        areas = [float(v) for v in areas]
        tvals = [float(v) for v in t_vals]
        taus = [t / a for t, a in zip(tvals, areas)]
        top3 = taus[-3:]
        same = taus[-1] < TAU_FRAC * k and top3[2] < top3[1] < top3[0]
        rel = [abs(top3[i + 1] - top3[i]) / max(abs(top3[i + 1]),
               abs(top3[i]), 1e-300) for i in (0, 1)]
        tau_star = taus[-1]
        kappa_joint = k - tau_star
        renorm = max(rel) < KAPPA_REL and tau_star >= TAU_FRAC * k \
            and kappa_joint > 0.0
        if same:
            rung = "BHQREL0-AREA-SAME"
        elif renorm:
            rung = "BHQREL0-AREA-RENORM"
        else:
            rung = "BHQREL0-NONAREA"
        return {"rung": rung, "tau_star": tau_star,
                "kappa_joint": kappa_joint if renorm else None,
                "taus_top3": top3}
    except Exception:
        return {"failed": True}


def classify_subleading(resid_top4: list) -> str:
    """J-logic: CONSTANT / CURVATURE / LOGA / UNRESOLVED (pure logic).

    Input: residual R(A) at the top-4 rungs (ascending A).
    CONSTANT: top-2 relative within 1%. CURVATURE: |R| strictly
    decreasing over top-4. LOGA: |R|/log(A-rank) stable 5% (rank
    proxy 7,8,9,10 for top-4). Else UNRESOLVED.
    """
    try:
        vals = [float(v) for v in resid_top4]
        if len(vals) != 4:
            return "UNRESOLVED"
        denom = max(abs(vals[3]), abs(vals[2]), 1e-300)
        if abs(vals[3] - vals[2]) / denom < 0.01:
            return "CONSTANT"
        mags = [abs(v) for v in vals]
        if mags[3] < mags[2] < mags[1] < mags[0]:
            return "CURVATURE"
        ranks = [7.0, 8.0, 9.0, 10.0]
        ratios = [m / math.log(r) for m, r in zip(mags, ranks)]
        base = max(abs(v) for v in ratios + [1e-300])
        if max(abs(a - b) for a in ratios for b in ratios) / base < 0.05:
            return "LOGA"
        return "UNRESOLVED"
    except Exception:
        return "UNRESOLVED"


def is_conditional_logic_ok() -> bool:
    """Boolean check: conditional ladder logic on synthetic ladders.

    Never raises. SAME (small decaying tau), RENORM (stable tau*),
    NONAREA (tau* >= kappa_iso; non-convergent tau), subleading
    four-branch classification.
    """
    try:
        k = 4.2207
        areas = [4.0 * math.pi * r ** 2 for r in range(1, 11)]
        same_t = [0.05 * a for a in areas]
        same_t[-3:] = [0.02 * areas[-3], 0.008 * areas[-2],
                       0.005 * areas[-1]]
        rep = classify_conditional(k, areas, same_t, [0.0] * 10)
        if rep.get("rung") != "BHQREL0-AREA-SAME":
            return False
        ren_t = [0.5 * a for a in areas]
        rep = classify_conditional(k, areas, ren_t, [0.0] * 10)
        if rep.get("rung") != "BHQREL0-AREA-RENORM":
            return False
        if abs(rep["kappa_joint"] - (k - 0.5)) > 1e-9:
            return False
        big_t = [5.0 * a for a in areas]
        rep = classify_conditional(k, areas, big_t, [0.0] * 10)
        if rep.get("rung") != "BHQREL0-NONAREA":
            return False
        wild_t = [0.1 * a for a in areas]
        wild_t[-3:] = [0.1 * areas[-3], 0.9 * areas[-2],
                       0.1 * areas[-1]]
        rep = classify_conditional(k, areas, wild_t, [0.0] * 10)
        if rep.get("rung") != "BHQREL0-NONAREA":
            return False
        if classify_subleading([3.0, 3.001, 2.999, 3.0]) != "CONSTANT":
            return False
        if classify_subleading([4.0, 3.0, 2.0, 1.0]) != "CURVATURE":
            return False
        loga = [math.log(r) for r in (7.0, 8.0, 9.0, 10.0)]
        if classify_subleading(loga) != "LOGA":
            return False
        if classify_subleading([0.0, 1.0, 0.0, 1.0]) != "UNRESOLVED":
            return False
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Firewall / counts / params (prereg section 4)
# ---------------------------------------------------------------------------

def is_firewall_ok() -> bool:
    """Boolean check: apparatus source audit + no combined symbol.

    Strips triple-quoted strings + comments + string literals (QINFO-0
    precedent), then fails on forbidden code tokens. Relational
    statistics (covar/corr/bins) are the campaign subject and pass;
    joint-entropy, pairwise-information, combined-total, and
    thermodynamic tokens fail. Also fails if any combined/total
    attribute is defined on this module.
    """
    try:
        import bh_graph.bhqrel0 as self_mod

        for attr in ("H_total", "Htotal", "total_entropy", "mutual_info",
                     "S_BH", "area_law"):
            if hasattr(self_mod, attr):
                return False
        src = inspect.getsource(inspect.getmodule(is_firewall_ok))
        src_nostr = re.sub(r'""".*?"""', " ", src, flags=re.DOTALL)
        src_nostr = re.sub(r"'''.*?'''", " ", src_nostr, flags=re.DOTALL)
        toks = []
        for tok in tokenize.generate_tokens(
                io.StringIO(src_nostr).readline):
            if tok.type == tokenize.COMMENT:
                continue
            if tok.type == tokenize.STRING:
                continue
            toks.append(tok.string)
        names = {t.lower() for t in toks}
        forbidden_names = ("planck", "hawking", "bekenstein", "holograph",
                           "a_over_4", "mutual_info", "correlation_entropy",
                           "h_total", "htotal", "total_entropy", "s_bh",
                           "area_law", "two_qubits", "fiber_measure", "rng")
        if any(f in names for f in forbidden_names):
            return False
        code_ns = re.sub(r"\s+", "", " ".join(toks)).lower()
        forbidden_seq = ("np.random", "random.", "scipy.stats.entropy")
        return bool(all(f not in code_ns for f in forbidden_seq))
    except Exception:
        return False


def fitted_param_count() -> int:
    """Fitted parameters introduced by this module: always 0."""
    return 0


def battery_counts() -> dict:
    """Frozen battery counts (prereg section 3)."""
    n_head = len(R_LADDER) * len(HEADLINE_STATES)
    n_ctrl = len(R_LADDER) * len(CONTROL_STATES)
    return {"rungs": len(R_LADDER), "headline_rel": n_head,
            "control_rel": n_ctrl, "rel_total": n_head + n_ctrl,
            "jointaudit": len(CANDIDATE_IDS), "smallctrl": 1,
            "regression": 1, "audit": 1, "redundant": 1,
            "total": n_head + n_ctrl + len(CANDIDATE_IDS) + 4}


def is_battery_counts_ok() -> bool:
    """Boolean check: 50 rel + 5 audits + smallctrl + 3 = 59 records."""
    try:
        c = battery_counts()
        return bool(c["headline_rel"] == 40 and c["control_rel"] == 10
                    and c["jointaudit"] == 5 and c["total"] == 59)
    except Exception:
        return False


def input_hashes() -> dict:
    """sha256 of the frozen source files consumed read-only."""
    import bh_graph.bhqarea0 as _ba
    import bh_graph.dim3 as _d3
    import bh_graph.graphs as _gr
    import bh_graph.haar as _ha
    import bh_graph.qinfo0 as _q0

    out = {}
    for name, mod in (("qinfo0", _q0), ("graphs", _gr), ("dim3", _d3),
                      ("bhqarea0", _ba), ("haar", _ha)):
        path = inspect.getsourcefile(mod)
        with open(path, "rb") as fh:
            out[name] = hashlib.sha256(fh.read()).hexdigest()
    return out
