"""BH-Q-REL-0: relational Q-information on a 3D BH-like boundary (FROZEN pre-data).

Mission (BH-Q-REL-0): test whether boundary Q-channels on BH-like geometry
carry pairwise relational structure beyond the isolated BHQAREA0 sum, and
whether any such structure is independent, short-ranged (structured), or
long-ranged (correlated). The BH-Q-REL-0.tex spec sheet arrived out-of-band
and was not present in the workspace; this campaign is reconstructed from
the banked BH-Q-AREA-0/Q-INFO-0 debts (relations between Q modes precede
any joint-information functional) and filed as such.

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

This module introduces NO dynamics, NO firing law, NO measure on any
fiber, NO joint entropy, NO pairwise information functional, NO fitted
constant, NO threshold, NO rate. Pairwise statistics below are mechanical
normalized covariances of earned per-edge quantities (x_e, s_Q(e)),
never converted to bits. Tolerances are numerical, never physics.

Firewall (binding): the words black-hole entropy, holography,
thermodynamic entropy, Planck scale appear in this module ONLY in
negative firewall statements (docstrings/comments, stripped by the
apparatus audit). No joint-entropy, pairwise-information, or combined
total symbol is defined anywhere (gate-audited). Relational structure
is filed explicitly as correlation statistics, never as information.
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
            "regression": 1, "audit": 1, "redundant": 1,
            "total": n_head + n_ctrl + 3}


def is_battery_counts_ok() -> bool:
    """Boolean check: 40 headline + 10 control + 3 = 53 records."""
    try:
        c = battery_counts()
        return bool(c["headline_rel"] == 40 and c["control_rel"] == 10
                    and c["total"] == 53)
    except Exception:
        return False


def input_hashes() -> dict:
    """sha256 of the frozen source files consumed read-only."""
    import bh_graph.bhqarea0 as _ba
    import bh_graph.dim3 as _d3
    import bh_graph.graphs as _gr
    import bh_graph.qinfo0 as _q0

    out = {}
    for name, mod in (("qinfo0", _q0), ("graphs", _gr), ("dim3", _d3),
                      ("bhqarea0", _ba)):
        path = inspect.getsourcefile(mod)
        with open(path, "rb") as fh:
            out[name] = hashlib.sha256(fh.read()).hexdigest()
    return out
