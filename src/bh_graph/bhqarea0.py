"""BH-Q-AREA-0: Q-information area law on a 3D BH-like boundary (FROZEN pre-data).

Mission (BH-Q-AREA-0.tex): test whether the earned isolated STORE/qubit
information on boundary channels of a BH-like highly connected interior
embedded in a mature 3D exterior obeys S_Q^d ~ A.

Frozen inputs (read-only, never re-derived, never modified):
  (1) QINFO0-IDENTICAL (qinfo0.py): the earned information functional
      s_Q = h2(P_-) with P_- = |d|^2/(|s|^2+|d|^2). This module defines
      NO new entropy: every s_Q value goes through the banked
      qinfo0.h2_binary.
  (2) BH-like/high-connectivity construction: graphs.build_complete
      (paper Sec-1 all:all interior), relabeled onto each region node
      set; evaluated as a sparse block, pinned edge-identical.
  (3) Mature J3/3D boundary/area source: dim3.build_j3_ball,
      dim3.shells_cuts_vols, dim3.bipartition_j3; frozen law H = -A.

This module introduces NO dynamics, NO firing law, NO measure on any
fiber, NO relational/correlation term, NO fitted constant, NO threshold,
NO rate. Tolerances below are numerical (exact algebra / solver
residuals), never physics.

Firewall (binding): the words black-hole entropy, area law, holography,
thermodynamic entropy, Planck scale appear in this module ONLY in
negative firewall statements (docstrings/comments, stripped by the
apparatus audit). No mutual-information, entanglement-correction, or
many-body symbol is defined anywhere (gate-audited). S_Q^d is filed
explicitly as isolated/non-relational boundary Q information.
"""

from __future__ import annotations

import hashlib
import inspect
import io
import math
import re
import tokenize

import networkx as nx
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla
import scipy.stats as st

# ---------------------------------------------------------------------------
# Frozen design (BHQAREA0-PREREG sections 2-4)
# ---------------------------------------------------------------------------

R_LADDER = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
MARGIN = 4
TOP_RUNGS = (8, 9, 10)
POW_RUNGS = (4, 5, 6, 7, 8, 9, 10)

VARIANTS = ("headline", "control")
HEADLINE_STATES = ("vacuum", "vplus", "vpi", "vminus")
CONTROL_STATES = ("vacuum",)

EIG_TOL = 1e-10
EIG_MAXITER = 30000
EIG_NCV = 20

J_DOMAIN = 0.1
QUANTILES = (0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99)

CORE_PIN_SIZES = (2, 3, 4, 5, 8, 13)

BAR_REL = 0.05
BAR_H_ABS_1 = 0.01
BAR_H_ABS_2 = 0.015
BAR_KS = 0.1
BAR_COLLAPSE_STD = 0.02
BAR_J_REL = 0.10
BAR_K_REL = 1e-9
BAR_KAPPA_ZERO = 0.1
BAR_KAPPA_ZERO_ABS = 0.02
BAR_M_ZERO = 0.05
BAR_POW = (0.7, 1.3)

FP_ATOL = 1e-12
CENSUS_ATOL = 1e-9

KIND_IDENTITY = "I"


# ---------------------------------------------------------------------------
# Frozen geometry (prereg section 2)
# ---------------------------------------------------------------------------

def rmax_of(r: int) -> int:
    """Ambient J3 ball radius Rmax(r) = r + MARGIN (frozen)."""
    return int(r) + int(MARGIN)


def area_of(r: int) -> float:
    """Frozen area convention A(r) = 4 pi r^2 (a = 1)."""
    return float(4.0 * math.pi * float(int(r)) ** 2)


def ambient_ball(r: int):
    """Ambient J3 ball of radius Rmax(r) (source (3), unchanged)."""
    from bh_graph import dim3 as _d3

    return _d3.build_j3_ball(rmax_of(r))


def region_disk(g: nx.Graph, r: int) -> set:
    """BFS disk {d <= r} from the J3 root (frozen region R_r)."""
    root = (0, 0, 0, 0)
    dist = dict(nx.single_source_shortest_path_length(g, root))
    return {n for n in dist if dist[n] <= int(r)}


def boundary_edges(g: nx.Graph, disk: set) -> list:
    """Frozen physical cut-edge set: J3 edges with one end in disk.

    Deterministic order (sorted by endpoint repr). Identical for headline
    and control by construction.
    """
    out = []
    for u, v in g.edges():
        if (u in disk) != (v in disk):
            out.append((u, v))
    out.sort(key=lambda e: (repr(e[0]), repr(e[1])))
    return out


def geometry_record(r: int) -> dict:
    """Frozen ladder geometry: N_int, N_d, A, sigma (+ dim3 cut check)."""
    from bh_graph import dim3 as _d3

    g = ambient_ball(r)
    disk = region_disk(g, r)
    edges = boundary_edges(g, disk)
    _shells, cuts, _vols = _d3.shells_cuts_vols(g, (0, 0, 0, 0),
                                                rmax_of(r))
    n_int = len(disk)
    n_bnd = len(edges)
    area = area_of(r)
    return {"r": int(r), "rmax": rmax_of(r), "n_int": n_int,
            "n_bnd": n_bnd, "area": area,
            "sigma": float(n_bnd / area),
            "dim3_cut": int(cuts[int(r) - 1])}


def is_geometry_ok(r: int) -> bool:
    """Boolean check: rung builds, N_int >= 2, N_d >= 1, N_d == dim3 cut."""
    try:
        rec = geometry_record(int(r))
        if rec["n_int"] < 2 or rec["n_bnd"] < 1:
            return False
        if rec["n_bnd"] != rec["dim3_cut"]:
            return False
        return bool(rec["rmax"] == int(r) + int(MARGIN))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Complete-core block (source (2), sparse evaluation, pinned)
# ---------------------------------------------------------------------------

def core_block_coo(nc: int):
    """COO index arrays of K_nc on 0..nc-1 (all i != j pairs).

    Same edge set as graphs.build_complete(nc) (gate G-D pins exact
    edge-set equality on CORE_PIN_SIZES); sparse assembly is scale only.
    """
    nc = int(nc)
    idx = np.arange(nc)
    rows, cols = np.meshgrid(idx, idx, indexing="ij")
    mask = rows != cols
    return np.ascontiguousarray(rows[mask]), np.ascontiguousarray(cols[mask])


def core_edges_equal_complete(nc: int) -> bool:
    """Boolean check: core block edge set == build_complete edge set."""
    try:
        from bh_graph import graphs as _gr

        nc = int(nc)
        g = _gr.build_complete(nc)
        want = {frozenset(e) for e in g.edges()}
        rows, cols = core_block_coo(nc)
        got = {frozenset((int(a), int(b)))
               for a, b in zip(rows.tolist(), cols.tolist())}
        return bool(got == want and len(got) == nc * (nc - 1) // 2)
    except Exception:
        return False


def is_core_generator_ok() -> bool:
    """Boolean check: generator pinned on all CORE_PIN_SIZES."""
    try:
        return bool(all(core_edges_equal_complete(n)
                        for n in CORE_PIN_SIZES))
    except Exception:
        return False


def assemble_adjacency(r: int, variant: str):
    """Full-rung adjacency as CSR + order + disk + cut edges.

    Headline: ambient J3 edges outside the R_r induced subgraph plus the
    K_{N_int} block on R_r. Control: ambient J3 edges unchanged.
    Returns dict(order, index, adj, disk_idx, cut_pairs, n, n_int).
    """
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant: {variant}")
    g = ambient_ball(int(r))
    disk = region_disk(g, int(r))
    order = sorted(g.nodes())
    index = {v: k for k, v in enumerate(order)}
    n = len(order)
    disk_idx = np.array(sorted(index[v] for v in disk))
    in_disk = np.zeros(n, dtype=bool)
    in_disk[disk_idx] = True
    rows: list = []
    cols: list = []
    for u, v in g.edges():
        iu, iv = index[u], index[v]
        if variant == "headline" and in_disk[iu] and in_disk[iv]:
            continue
        rows += [iu, iv]
        cols += [iv, iu]
    if variant == "headline":
        nc = len(disk_idx)
        brow, bcol = core_block_coo(nc)
        rows = np.concatenate([np.asarray(rows, dtype=np.int64),
                               disk_idx[brow]])
        cols = np.concatenate([np.asarray(cols, dtype=np.int64),
                               disk_idx[bcol]])
    else:
        rows = np.asarray(rows, dtype=np.int64)
        cols = np.asarray(cols, dtype=np.int64)
    adj = sp.coo_matrix((np.ones(len(rows)), (rows, cols)),
                        shape=(n, n)).tocsr()
    adj.sort_indices()
    cut = boundary_edges(g, disk)
    cut_pairs = [(index[u], index[v]) for u, v in cut]
    return {"order": order, "index": index, "adj": adj,
            "disk_idx": disk_idx, "cut_pairs": cut_pairs, "n": n,
            "n_int": len(disk_idx), "n_bnd": len(cut_pairs)}


# ---------------------------------------------------------------------------
# Frozen states (prereg section 2)
# ---------------------------------------------------------------------------

def vacuum_psi(adj) -> dict:
    """Ground state of H = -A: top adjacency eigenvector (Perron).

    Frozen solver: eigsh LA, v0 = ones, tol/maxiter/ncv frozen.
    Deterministic under the frozen single-thread env. Returns
    dict(psi, lam, residual).
    """
    n = int(adj.shape[0])
    v0 = np.ones(n, dtype=float)
    val, vec = sla.eigsh(adj, k=1, which="LA", v0=v0, tol=float(EIG_TOL),
                         maxiter=int(EIG_MAXITER), ncv=int(EIG_NCV))
    psi = np.asarray(vec[:, 0], dtype=np.complex128)
    psi = psi / np.linalg.norm(psi)
    lam = float(val[0])
    resid = float(np.linalg.norm(adj @ psi - lam * psi))
    return {"psi": psi, "lam": lam, "residual": resid}


def pattern_psi(kind: str, order: list) -> np.ndarray:
    """Source-(3) candidate family lifted to ball coords (normalized).

    vplus: uniform +1; vpi: bipartite-staggered via bipartition_j3;
    vminus: sheet-staggered via node sheet bit.
    """
    from bh_graph import dim3 as _d3

    n = len(order)
    if kind == "vplus":
        vec = np.ones(n, dtype=np.complex128)
    elif kind == "vpi":
        c4 = {v: v for v in order}
        submap = _d3.bipartition_j3(c4)
        vec = np.array([1.0 if submap[v] == 0 else -1.0 for v in order],
                       dtype=np.complex128)
    elif kind == "vminus":
        vec = np.array([1.0 if v[3] == 0 else -1.0 for v in order],
                       dtype=np.complex128)
    else:
        raise ValueError(f"unknown pattern state: {kind}")
    return vec / np.linalg.norm(vec)


def state_psi(variant: str, state: str, asm: dict) -> dict:
    """Frozen state readout: dict(psi, lam, residual).

    Vacuum: eigensolver readout (lam/residual real). Patterns: lam and
    residual filed as None (not eigenstates; frozen alternative states).
    """
    if state == "vacuum":
        return vacuum_psi(asm["adj"])
    psi = pattern_psi(state, asm["order"])
    return {"psi": psi, "lam": None, "residual": None}


def psi_sha256(psi: np.ndarray) -> str:
    """Deterministic content hash of a state vector (reproducibility)."""
    arr = np.ascontiguousarray(np.asarray(psi, dtype=np.complex128))
    return hashlib.sha256(arr.tobytes()).hexdigest()


# ---------------------------------------------------------------------------
# Boundary information (spec A/B/C/F/H/J/K; banked qinfo0 functional)
# ---------------------------------------------------------------------------

def edge_terms(psi_i: complex, psi_j: complex) -> dict | None:
    """Earned edge terms s/d/q/B/x/P_-/s_Q via the banked functional.

    None for the q = 0 pair (filed separately as undefined normalized
    ratios; never assigned). Never raises.
    """
    try:
        from bh_graph import qinfo0 as _q0

        psi_i, psi_j = complex(psi_i), complex(psi_j)
        q = float(abs(psi_i) ** 2 + abs(psi_j) ** 2)
        if q == 0.0:
            return None
        s = _q0.sum_mode(psi_i, psi_j)
        d = _q0.diff_mode(psi_i, psi_j)
        b = float((np.conj(psi_i) * psi_j).real)
        x = float(b / q)
        w = _q0.mode_weights(s, d)
        p_minus = float(w["P_minus"])
        s_q = _q0.h2_binary(p_minus)
        return {"s": s, "d": d, "q": q, "B": b, "x": x,
                "P_minus": p_minus, "s_Q": float(s_q)}
    except Exception:
        return None


def is_formula_ok(atol: float = FP_ATOL) -> bool:
    """Boolean check (A): P_- = 1/2-B/q and s_Q = h2(P_-) vs banked.

    Frozen formula cells: qinfo0 PAIR_CELLS plus boundary-like pairs.
    """
    try:
        from bh_graph import qinfo0 as _q0

        cells = list(_q0.PAIR_CELLS) + [
            ("e1", complex(1.0, 0.0), complex(1e-3, 0.0)),
            ("e2", complex(0.02, 0.01), complex(-0.015, 0.005)),
            ("e3", complex(1.0, 1.0), complex(1e-6, -2e-6)),
        ]
        for _name, psi_i, psi_j in cells:
            psi_i, psi_j = complex(psi_i), complex(psi_j)
            q = abs(psi_i) ** 2 + abs(psi_j) ** 2
            s = _q0.sum_mode(psi_i, psi_j)
            d = _q0.diff_mode(psi_i, psi_j)
            if q == 0.0:
                if edge_terms(psi_i, psi_j) is not None:
                    return False
                if _q0.mode_weights(s, d) is not None:
                    return False
                continue
            b = float((np.conj(psi_i) * psi_j).real)
            rep = edge_terms(psi_i, psi_j)
            if rep is None:
                return False
            if abs(rep["P_minus"] - (0.5 - b / q)) > atol:
                return False
            direct = _q0.h2_of_pair(s, d)
            if abs(rep["s_Q"] - direct) > atol:
                return False
        return True
    except Exception:
        return False


def is_endpoints_ok(atol: float = FP_ATOL) -> bool:
    """Boolean check (B): B=0 -> 1; B=+/-q/2 -> 0; q=0 undefined."""
    try:
        r0 = edge_terms(complex(1.0, 0.0), complex(0.0, 1.0))
        if abs(r0["B"]) > atol or abs(r0["s_Q"] - 1.0) > atol:
            return False
        rp = edge_terms(complex(1.0, 0.0), complex(1.0, 0.0))
        if abs(rp["B"] - rp["q"] / 2.0) > atol or rp["s_Q"] != 0.0:
            return False
        rm = edge_terms(complex(1.0, 0.0), complex(-1.0, 0.0))
        if abs(rm["B"] + rm["q"] / 2.0) > atol or rm["s_Q"] != 0.0:
            return False
        return bool(edge_terms(0j, 0j) is None)
    except Exception:
        return False


def expansion_terms(x: float) -> dict:
    """Small-x information deficit terms (spec small-B theorem)."""
    from bh_graph import qinfo0 as _q0

    x = float(x)
    lhs = float(1.0 - _q0.h2_binary(0.5 - x))
    quad = float((2.0 / math.log(2.0)) * x ** 2)
    quart = float((4.0 / (3.0 * math.log(2.0))) * x ** 4)
    return {"lhs": lhs, "quad": quad, "quart": quart,
            "resid2": lhs - quad, "resid4": lhs - quad - quart}


def is_expansion_ok() -> bool:
    """Boolean check (C): analytic deficit coefficients (not fitted)."""
    try:
        t2 = expansion_terms(1e-4)
        c2 = t2["lhs"] / (1e-4 ** 2)
        if abs(c2 - 2.0 / math.log(2.0)) / (2.0 / math.log(2.0)) > 1e-6:
            return False
        t4 = expansion_terms(1e-3)
        c4 = (t4["lhs"] - t4["quad"]) / (1e-3 ** 4)
        want4 = 4.0 / (3.0 * math.log(2.0))
        return bool(abs(c4 - want4) / want4 <= 1e-3)
    except Exception:
        return False


def census_stats(xs: list) -> dict:
    """Frozen census summaries: mean, median, var, meansq, quantiles."""
    arr = np.asarray([float(v) for v in xs], dtype=float)
    qs = np.quantile(arr, list(QUANTILES))
    return {"n": int(arr.size), "mean": float(np.mean(arr)),
            "median": float(np.median(arr)),
            "var": float(np.var(arr)),
            "meansq": float(np.mean(arr ** 2)),
            "min": float(np.min(arr)), "max": float(np.max(arr)),
            "quantiles": [float(v) for v in qs]}


def is_census_stats_ok() -> bool:
    """Boolean check: census math on a frozen synthetic vector."""
    try:
        rep = census_stats([0.0, 0.25, 0.5, -0.25, 0.125])
        if rep["n"] != 5:
            return False
        if abs(rep["mean"] - 0.125) > FP_ATOL:
            return False
        if abs(rep["median"] - 0.125) > FP_ATOL:
            return False
        if abs(rep["meansq"] - 0.078125) > FP_ATOL:
            return False
        if abs(rep["quantiles"][3] - 0.125) > FP_ATOL:
            return False
        return True
    except Exception:
        return False


def run_rung(r: int, variant: str, state: str) -> dict:
    """Full per-rung record (geometry + state + census + audit).

    Deterministic (frozen solver + frozen order). The x-array is filed
    (analyzer re-verifies every summary); psi is filed by hash only.
    """
    from bh_graph import qinfo0 as _q0

    r = int(r)
    if variant not in VARIANTS:
        raise ValueError(f"unknown variant: {variant}")
    states = HEADLINE_STATES if variant == "headline" else CONTROL_STATES
    if state not in states:
        raise ValueError(f"unknown state: {state} for {variant}")
    asm = assemble_adjacency(r, variant)
    psi_rep = state_psi(variant, state, asm)
    psi = np.asarray(psi_rep["psi"], dtype=np.complex128)
    geo = geometry_record(r)
    xs: list = []
    s_list: list = []
    zero_pairs = 0
    dup_keys: list = []
    for iu, iv in asm["cut_pairs"]:
        rep = edge_terms(complex(psi[iu]), complex(psi[iv]))
        if rep is None:
            zero_pairs += 1
            continue
        xs.append(rep["x"])
        s_list.append(rep["s_Q"])
        dup_keys.append((float(abs(rep["s"]) ** 2),
                         float(abs(rep["d"]) ** 2)))
    n_bnd = len(asm["cut_pairs"])
    n_def = len(xs)
    s_sum = float(sum(s_list))
    h_bar = float(s_sum / n_bnd) if n_bnd else 0.0
    kappa = float(s_sum / geo["area"]) if geo["area"] else 0.0
    delta = float(n_bnd - s_sum)
    in_dom = [float(v) for v in xs if abs(float(v)) <= float(J_DOMAIN)]
    delta2 = float((2.0 / math.log(2.0)) * sum(v * v for v in in_dom))
    # Independence audit (N): exact (s,d)-mod-swap duplicates only.
    seen: dict = {}
    for key in dup_keys:
        seen[key] = seen.get(key, 0) + 1
    n_dup_groups = sum(1 for c in seen.values() if c > 1)
    n_dup_edges = sum(c - 1 for c in seen.values() if c > 1)
    uniq_sum = None
    if n_dup_edges:
        keyed: dict = {}
        for key, s_q in zip(dup_keys, s_list):
            if key not in keyed:
                keyed[key] = s_q
        uniq_sum = float(sum(keyed.values()))
    stats = census_stats(xs) if xs else {"n": 0}
    h2_guard = _q0.h2_binary(0.5)
    return {"r": r, "variant": variant, "state": state,
            "rmax": geo["rmax"], "n_int": geo["n_int"],
            "n_bnd": n_bnd, "n_defined": n_def,
            "zero_pairs": zero_pairs, "area": geo["area"],
            "sigma": geo["sigma"], "dim3_cut": geo["dim3_cut"],
            "lam": psi_rep["lam"], "eig_residual": psi_rep["residual"],
            "psi_sha256": psi_sha256(psi), "psi_n": int(psi.size),
            "xs": [float(v) for v in xs], "stats": stats,
            "S": s_sum, "hbar": h_bar, "kappa": kappa,
            "kappa_fact": float(geo["sigma"] * h_bar),
            "vol_ratio": float(s_sum / geo["n_int"]),
            "delta": delta, "delta2": delta2,
            "delta_dom_n": len(in_dom),
            "dup_groups": n_dup_groups, "dup_edges": n_dup_edges,
            "uniq_sum": uniq_sum, "h2_guard": h2_guard}


# ---------------------------------------------------------------------------
# Distribution / scaling helpers (spec G/L/M/POW)
# ---------------------------------------------------------------------------

def ks_distance(xs_a: list, xs_b: list) -> float:
    """Two-sample KS distance (frozen distribution comparator)."""
    return float(st.ks_2samp(np.asarray(xs_a, dtype=float),
                             np.asarray(xs_b, dtype=float)).statistic)


def power_exponent(areas: list, values: list) -> float:
    """Log-log OLS exponent of values vs areas (frozen scaling readout)."""
    la = np.log(np.asarray(areas, dtype=float))
    lv = np.log(np.asarray(values, dtype=float))
    return float(np.polyfit(la, lv, 1)[0])


def is_helpers_ok() -> bool:
    """Boolean check: KS + exponent helpers on frozen synthetic inputs."""
    try:
        if ks_distance([0.1, 0.2, 0.3], [0.1, 0.2, 0.3]) != 0.0:
            return False
        if abs(ks_distance([0.0, 0.0], [1.0, 1.0]) - 1.0) > FP_ATOL:
            return False
        p = power_exponent([1.0, 4.0, 16.0], [2.0, 8.0, 32.0])
        return bool(abs(p - 1.0) < 1e-12)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Firewall / counts / params (spec N/O)
# ---------------------------------------------------------------------------

def is_firewall_ok() -> bool:
    """Boolean check (O): apparatus source audit + no combined symbol.

    Strips triple-quoted strings + comments + string literals (QINFO-0
    precedent), then fails on forbidden code tokens. Also fails if any
    relational/total attribute is defined on this module.
    """
    try:
        import bh_graph.bhqarea0 as self_mod

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
                           "area_law", "two_qubits", "rng")
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
    return {"rungs": len(R_LADDER), "headline_rung": n_head,
            "control_rung": n_ctrl, "rung_total": n_head + n_ctrl,
            "regression": 1, "audit": 1, "redundant": 1,
            "total": n_head + n_ctrl + 3}


def is_battery_counts_ok() -> bool:
    """Boolean check: 40 headline + 10 control + 3 = 53 records."""
    try:
        c = battery_counts()
        return bool(c["headline_rung"] == 40 and c["control_rung"] == 10
                    and c["total"] == 53)
    except Exception:
        return False


def input_hashes() -> dict:
    """sha256 of the frozen source files + module versions."""
    import bh_graph.dim3 as _d3
    import bh_graph.graphs as _gr
    import bh_graph.qinfo0 as _q0

    out = {}
    for name, mod in (("qinfo0", _q0), ("graphs", _gr), ("dim3", _d3)):
        path = inspect.getsourcefile(mod)
        with open(path, "rb") as fh:
            out[name] = hashlib.sha256(fh.read()).hexdigest()
    return out
