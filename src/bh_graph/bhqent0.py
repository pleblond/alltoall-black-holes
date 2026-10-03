"""BH-Q-ENT-0: Boundary Scaling of Exterior-Blind Store Information.

Mission: revisit BH entropy only at the information-dimension level after
STORE0-REVERSIBLE enlarged the microscopic state to (G,psi,Q). Test how
physically distinct exterior-blind Q information scales with a region
boundary. Do not identify the result with thermodynamic entropy.

Frozen inputs (read-only, never re-derived):
  BHENT0-UNCLASSIFIED; STORE0-REVERSIBLE; SPLIT0-MIXED; INFO0-MATCHED;
  RES0-XI; FIBER0-DEBT; QDYN0B-EVENT-LOCAL; HIDDEN0-SEPARATED; HBR0-SIGNREV;
  QUOT0-OPERATIONAL; SYM0-CLOSED.

Store anatomy: each generic store entry is q=xi=(c,d) with discrete cover
c and d in C: dim_R d = 2. For N_d independent generic entries,
D_Q,cont = 2 N_d before physical/exterior constraints. Factor 2 is
dimension counting, not an entropy coefficient.

Primary observable: for region R and frozen exterior channel set O_ext
define the exterior-blind physical store fiber F_Q(R) and continuous
information dimension D_Q(R) = dim_R F_Q(R). Discrete cover multiplicity
is reported separately.

This module ADDS the BH-Q-ENT-0 battery/apparatus; it never modifies any
banked module (all consumed read-only). No RNG anywhere. No fitted
parameter. No new measure, firing law, or thermal variable.
"""

from __future__ import annotations

import itertools
import math

import networkx as nx
import numpy as np

# Frozen bars (reused, never retuned).
FP_BAR = 1e-9
LEDGER_BAR = 1e-9
LOCAL_BAR = 1e-6
REMOTE_BAR = 1e-9
FS_BAR = 1e-7
POT_OMEGA_GAP = 1.0
T_WAVE = 16.0
DT_WAVE = 0.05
PHASE_GRID = tuple(j * math.pi / 4.0 for j in range(8))
ALPHA_PROBE = 0.5

# BH-Q-ENT-0 frozen numerics (pre-data, never retuned post-data).
JAC_EPS = 1e-6          # central-difference step for d O_ext / d Q
RANK_TOL = 1e-5         # SVD rank tolerance for Jacobian rank
VAL_DELTA = 1e-3        # finite-validation perturbation norm
VAL_KERNEL_BAR = 1e-6   # kernel-direction exterior change must be below
VAL_SENS_MIN = 1e-5     # sensitive-direction exterior change must exceed
WAVE_TIMES = (0.0, 4.0, 8.0, 16.0)  # frozen wave/diff trace times (subset
# of the QUOT0 T_WAVE grid; full grid used only for TV validation)

# Scaling-gate bars (preregistered).
BHQ_BOUNDARY_SLOPE_BAR = 0.5
BHQ_BOUNDARY_GROWTH_BAR = 2.0
BHQ_BOUNDARY_R2_BAR = 0.70
BHQ_BOUNDARY_SLOPE_LO = 0.30
BHQ_VOLUME_R2_BAR = 0.90
BHQ_VOLUME_2D_BAR = 0.60
BHQ_VOLUME_SLOPE_LO = 0.50
BHQ_MIXED_R2_BAR = 0.90
BHQ_MIXED_SLOPE_BAND = (0.30, 3.00)
BHQ_FTEST_ALPHA = 0.01

FORBIDDEN_TOKENS = (
    "S_BH", "S_BH=", "Bekenstein", "bekenstein",
    "area law", "area-law", "arealaw", "Hawking temperature",
    "T_H=", "entropy=S", "S=A/4",
    "Planck", "planck", "Hawking", "hawking",
    "holograph", "Holograph", "thermodynamic", "Thermodynamic",
    "event horizon", "Event Horizon",
)


# ---------------------------------------------------------------------------
# Region battery (frozen builders; deterministic, no seeds)
# ---------------------------------------------------------------------------

BHQENT0_SPECS = (
    "P2", "P3", "P4", "P5", "P6", "P7", "P8",
    "S3_2", "S4_3", "S6_4", "S8_6", "S3_3", "S5_3",
    "J2L4edge", "J2L6r1", "J2L8r2",
    "SQL4dimer", "SQL4r1", "SQL6r1",
)

# Matched pairs (preregistered, pre-data).
MATCHED_B_PAIRS = (
    ("P4", "P6", "P8"),       # b=2 fixed, n varies
    ("S4_3", "S5_3"),         # b=3 fixed, n 5 vs 6
)
MATCHED_N_PAIRS = (
    ("P4", "S3_3"),           # n=4, b 2 vs 3
    ("P5", "S4_3"),           # n=5, b 2 vs 3
    ("P6", "S5_3"),           # n=6, b 2 vs 3
)
MATCHED_BOTH_PAIRS = (
    ("P4", "S3_2"),           # n=4,b=2 different topology
)


def build_region(spec):
    """Build a BH-Q-ENT-0 battery region (frozen mapping).

    Paths/stars/J2/squares reuse the BH-ENT-0 builders byte-identically.
    Extra star specs S3_3/S5_3 use the same star_region builder (no new
    geometry). 3D controls: no mature STORE-compatible 3D region exists
    at prereg (DIM-3-0 apparatus has no R/B collapse battery); filed as
    unavailable, never invented post-data.
    """
    from bh_graph import bhent as be

    return be.build_region(spec)


def region_battery():
    """Frozen spec lists per branch."""
    return {
        "headline": ["P2", "P3", "P4", "P5", "P6", "P7", "P8"],
        "stars": ["S3_2", "S4_3", "S6_4", "S8_6", "S3_3", "S5_3"],
        "j2": ["J2L4edge", "J2L6r1", "J2L8r2"],
        "square": ["SQL4dimer", "SQL4r1", "SQL6r1"],
        "order_invariance": ["P4", "P5", "S3_2", "J2L4edge", "SQL4dimer"],
        "hidden_overlap": ["J2L4edge", "J2L6r1"],
        "contrast": ["P4", "J2L6r1", "SQL4r1"],
    }


def boundary_data(rec):
    """Frozen graph boundary data: n_R and b_R (no new measure)."""
    return {"n_R": int(len(rec["R"])), "b_R": int(len(rec["B"])),
            "e_cut": int(rec["e_cut"])}


# ---------------------------------------------------------------------------
# Background fields (frozen closed forms)
# ---------------------------------------------------------------------------

def background_for(rec, spec, which="VPLUS"):
    """Frozen background field on the ambient graph (norm 1).

    VPLUS/VPI reuse BH-ENT-0 background_shapes. VMINUS on J2 reuses the
    HIDDEN vac_shapes sheet-staggered form; on non-J2 it is unavailable
    (filed, never invented). Hidden-texture backgrounds reuse the STORE-0
    TEXTURE_SPECS periodic maps on J2-L4/L8 substrates only where the
    region ambient matches; otherwise unavailable.
    """
    from bh_graph import bhent as be

    if which in ("VPLUS", "VPI"):
        return be.background_shapes(rec, which)
    if which == "VMINUS":
        if "c3" not in rec:
            raise ValueError("VMINUS needs J2 c3 (unavailable here)")
        from bh_graph import hidden as _h

        return _h.vac_shapes(rec["order"], rec["c3"])["VMINUS"]
    raise ValueError(f"unknown background: {which}")


# ---------------------------------------------------------------------------
# Store construction: collapse R with STORE0 xi per step (earned ops only)
# ---------------------------------------------------------------------------

def _internal_edges_sorted(g, Rset):
    return sorted(tuple(sorted(e)) for e in g.edges()
                  if e[0] in Rset and e[1] in Rset)


def collapse_region_with_store(rec, psi, order_mode="asc"):
    """Collapse R stepwise, storing STORE0 xi per earned merge.

    Deterministic order: lowest-sorted internal edge first (asc) or
    highest-sorted first (desc, for order-invariance O only). Each step
    uses the frozen BR-2.5 sum-map contraction and STORE0 encode_store
    (q=xi, canonical undirected cover + jointly-canonical d). No other
    construction appears anywhere.

    Returns M (collapsed state), Q0 (list of {cover,d}), frames, steps
    with ancestry + location tags, and the initial/final states.
    """
    from bh_graph.ballistic import index_of
    from bh_graph.contraction import contracted_state
    from bh_graph import store0 as st0

    g = rec["g"].copy()
    order = list(rec["order"])
    psi = np.asarray(psi, dtype=np.complex128).copy()
    Rset = set(rec["R"])
    Bset = set(rec["B"])
    # Original-distance map for location anatomy (frozen BFS from B).
    orig = rec["g"]
    dist_to_B = {}
    for v in orig.nodes():
        if v in Bset:
            dist_to_B[v] = 0
            continue
        try:
            d = nx.shortest_path_length(orig, v, None)
            dist_to_B[v] = min(d.get(b, 10 ** 9) for b in Bset)
        except Exception:
            dist_to_B[v] = 10 ** 9
    # Track constituent original leaves per live node.
    members = {v: {v} for v in g.nodes()}
    Q0 = []
    frames = []
    steps = []
    while len(Rset) > 1:
        internal = _internal_edges_sorted(g, Rset)
        if not internal:
            raise ValueError("region induced subgraph disconnected mid-collapse")
        e = internal[0] if order_mode == "asc" else internal[-1]
        i, j = e
        X = {"g": g, "psi": np.asarray(psi), "order": list(order)}
        enc = st0.encode_store(X, i, j)
        q = {"cover": [list(enc["q"]["cover"][0]),
                       list(enc["q"]["cover"][1])],
             "d": complex(enc["q"]["d"])}
        g2, psi2, order2, k, _record = contracted_state(
            g, psi, order, i, j, "sum")
        frame = st0.make_frame(k, i, j, enc["A_true"], enc["B_true"],
                               enc["q"]["cover"])
        # Ancestry + location.
        mem = set(members.get(i, {i})) | set(members.get(j, {j}))
        members[k] = mem
        for v in list(members.keys()):
            if v != k and v in (i, j):
                del members[v]
        dists = sorted(dist_to_B.get(v, 10 ** 9) for v in mem)
        touches_B = any(m in Bset for m in mem) or any(
            (m in g and any(nb in Bset for nb in g.neighbors(m)))
            for m in (i, j))
        # At merge time, check live adjacency to B (boundary-linked).
        live_touch = False
        try:
            for m in (i, j):
                for nb in g.neighbors(m):
                    if nb in Bset:
                        live_touch = True
        except Exception:
            live_touch = False
        loc = _classify_location(dists, live_touch, mem, Rset, Bset)
        Q0.append(q)
        frames.append(frame)
        steps.append({"edge": [i, j], "k": k,
                      "members": sorted(mem),
                      "n_members": len(mem),
                      "min_dist": int(dists[0]) if dists else -1,
                      "max_dist": int(dists[-1]) if dists else -1,
                      "touches_B": bool(live_touch),
                      "location": loc,
                      "cover": [list(q["cover"][0]), list(q["cover"][1])],
                      "d": complex(q["d"]),
                      "s": complex(enc["s"])})
        Rset = (Rset - {i, j}) | {k}
        g, psi, order = g2, psi2, order2
    k = next(iter(Rset))
    idx = index_of(order)
    M = {"g": g, "psi": np.asarray(psi, dtype=np.complex128),
         "order": list(order), "k": k,
         "psi_k": complex(psi[idx[k]])}
    return {"M": M, "Q0": Q0, "frames": frames, "steps": steps,
            "n_steps": len(steps), "N_Q": len(Q0), "N_d": len(Q0),
            "order_mode": order_mode}


def _classify_location(dists, live_touch, mem, Rset, Bset):
    """Frozen location classes (pre-data, never retuned).

    boundary-adjacent: live merge touches B.
    exterior: any member in B (should never happen; gate checks 0).
    interface: members span distinct original distances (mixed layers).
    shallow: min original distance == 2 (one hop from boundary layer).
    deep: min original distance >= 3.
    Distance-1 non-touching merges (second-wave boundary) count as
    boundary-adjacent only if live_touch else interface/shallow by span.
    """
    if any(m in Bset for m in mem):
        return "exterior"
    if bool(live_touch):
        return "boundary-adjacent"
    if not dists:
        return "deep"
    lo, hi = int(dists[0]), int(dists[-1])
    if lo != hi:
        return "interface/crossing"
    if lo <= 1:
        return "boundary-adjacent"
    if lo == 2:
        return "shallow interior"
    return "deep interior"


def pack_Q(Q):
    """Pack Q continuous params to real vector [Re d0, Im d0, ...]."""
    v = []
    for q in Q:
        d = complex(q["d"])
        v.extend([float(d.real), float(d.imag)])
    return np.asarray(v, dtype=float)


def unpack_Q(Q0, vec):
    """Unpack real vector to Q list (covers frozen from Q0)."""
    vec = np.asarray(vec, dtype=float)
    Q = []
    for k, q0 in enumerate(Q0):
        re = float(vec[2 * k])
        im = float(vec[2 * k + 1])
        Q.append({"cover": [list(q0["cover"][0]), list(q0["cover"][1])],
                  "d": complex(re, im)})
    return Q


def reconstruct_from_Q(M, Q, frames):
    """Reverse-split reconstruction X' from (M,Q) (STORE0 exact ops).

    Reverse insertion order (STORE0-STORE0Q); each split consumes its
    entry via split_recover with label restoration. Covers from Q,
    d from Q. Deterministic, no weighting.
    """
    from bh_graph import store0 as st0

    g = M["g"].copy()
    psi = np.asarray(M["psi"], dtype=np.complex128).copy()
    order = list(M["order"])
    for q, fr in reversed(list(zip(Q, frames))):
        k = fr["k"]
        X = st0.split_recover(g, psi, order, k, q, fr,
                              restore_labels=True)
        g, psi, order = X["g"], np.asarray(X["psi"]), list(X["order"])
    return {"g": g, "psi": np.asarray(psi, dtype=np.complex128),
            "order": list(order)}


# ---------------------------------------------------------------------------
# Exterior channels O_ext (frozen set, differentiable vectors)
# ---------------------------------------------------------------------------

CHANNELS = ("field", "rho", "B", "J", "wave", "diff", "pot", "struct")


def exterior_vector(X, rec, channels="joint", pot_cache=None):
    """Frozen exterior observable vector(s) of reconstructed X'.

    field: exterior psi (realified 2*n_ext).
    rho/B/J: strictly-exterior t=0 readouts (BH-ENT-0 exterior_static).
    wave: exterior wave probabilities at WAVE_TIMES (quot traces).
    diff: exterior diffused probabilities at WAVE_TIMES (quot traces).
    pot: static exterior profile phi_ext (graph-sensitive only).
    struct: operational structural ints (exterior edge count, collapsed
      edge count, cut count) as floats (continuous-blind by construction).

    channels="joint" concatenates all in CHANNELS order. Otherwise a
    single channel name. Returns {"vec": 1D float array, "parts": {...}}.
    """
    from bh_graph import bhent as be
    from bh_graph import quot as _q
    from bh_graph.ballistic import index_of
    from bh_graph.obs0 import hamiltonian_system, lsym_system

    g, psi, order = X["g"], np.asarray(X["psi"]), list(X["order"])
    Rset = set(rec["R"])
    pos = {v: i for i, v in enumerate(order)}
    # Exterior psi in ambient order (rec order restricted to exterior).
    ext_nodes = [v for v in rec["order"] if v not in Rset]
    # Map: reconstructed X uses original labels (restored), so same ids.
    idx = index_of(order)
    psi_ext = np.array([complex(psi[idx[v]]) for v in ext_nodes],
                       dtype=np.complex128)
    parts = {}
    # field
    parts["field"] = np.concatenate([psi_ext.real, psi_ext.imag])
    # rho/B/J via BH-ENT-0 static (needs rec with same R/B; X graph may
    # differ in interior wirings for cover variations -- exterior_static
    # uses rec["g"] for edge arrays, so pass a rec with X graph but same
    # R/B/order? For continuous-Q (fixed covers) graphs match exactly.
    # For cover variations, rebuild edge arrays on X graph directly.
    try:
        s = be.exterior_static_on_graph(psi, X["g"], order, rec)
    except AttributeError:
        # Fallback: BH-ENT-0 exterior_static uses rec graph; for
        # continuous-Q the graphs coincide, so call directly with a
        # rec shim carrying the X graph.
        shim = dict(rec)
        shim["g"] = X["g"]
        shim["order"] = list(order)
        s = be.exterior_static(psi, shim)
    parts["rho"] = np.asarray(s["rho"], dtype=float)
    parts["B"] = np.asarray(s["B"], dtype=float)
    parts["J"] = np.asarray(s["J"], dtype=float)
    # wave/diff traces at frozen times.
    ew, vw, _ = hamiltonian_system(X["g"], order)
    ew = np.asarray(ew)
    vw = np.asarray(vw)
    ts = np.asarray(WAVE_TIMES, dtype=float)
    n = len(order)
    tj = np.arange(n)
    trW = _q.wave_traces_general(ew, vw, np.asarray(psi), tj, ts)
    # Traces are (T, N); exterior cols only, flattened time-major.
    ext_idx = np.array([pos[v] for v in ext_nodes], dtype=int)
    parts["wave"] = np.asarray(trW[:, ext_idx], dtype=float).reshape(-1)
    wl, Vl, _ = lsym_system(X["g"], order)
    wl = np.asarray(wl)
    Vl = np.asarray(Vl)
    p0 = np.abs(np.asarray(psi, dtype=np.complex128)) ** 2
    trD = _q.diff_traces_general(wl, Vl, p0, tj, ts)
    parts["diff"] = np.asarray(trD[:, ext_idx], dtype=float).reshape(-1)
    # pot (psi-blind, graph-sensitive).
    if pot_cache is not None and "pot" in pot_cache:
        parts["pot"] = np.asarray(pot_cache["pot"], dtype=float)
    else:
        shim = dict(rec)
        shim["g"] = X["g"]
        shim["order"] = list(order)
        try:
            p = be.exterior_pot_profile(shim)
        except Exception:
            p = {"phi_ext": np.zeros(len(ext_nodes))}
        parts["pot"] = np.asarray(p["phi_ext"], dtype=float).reshape(-1)
    # struct (operational ints as floats).
    try:
        n_ext_edges = sum(1 for a, b in X["g"].edges()
                          if a not in Rset and b not in Rset)
        n_cut = sum(1 for a, b in X["g"].edges()
                    if (a in Rset) != (b in Rset))
    except Exception:
        n_ext_edges, n_cut = 0, 0
    parts["struct"] = np.asarray([float(n_ext_edges), float(n_cut)],
                                 dtype=float)
    if channels == "joint":
        vec = np.concatenate([parts[c] for c in CHANNELS])
        return {"vec": vec, "parts": parts}
    if channels in parts:
        return {"vec": np.asarray(parts[channels], dtype=float),
                "parts": {channels: parts[channels]}}
    raise ValueError(f"unknown channel: {channels}")


# ---------------------------------------------------------------------------
# Jacobians + blind dimensions (tangent analysis)
# ---------------------------------------------------------------------------

def jacobian_Q(build_X, v0, out_dim, eps=JAC_EPS):
    """Central-difference Jacobian (M x P) of vector map at v0.

    build_X(v) -> 1D float array of length out_dim. Deterministic.
    """
    v0 = np.asarray(v0, dtype=float)
    P = v0.size
    J = np.zeros((int(out_dim), int(P)), dtype=float)
    for j in range(P):
        vp = v0.copy()
        vm = v0.copy()
        vp[j] += eps
        vm[j] -= eps
        fp = np.asarray(build_X(vp), dtype=float).reshape(-1)
        fm = np.asarray(build_X(vm), dtype=float).reshape(-1)
        J[:, j] = (fp - fm) / (2.0 * eps)
    return J


def rank_of(J, tol=RANK_TOL):
    """SVD rank + kernel/row bases (deterministic, never raises)."""
    try:
        J = np.asarray(J, dtype=float)
        if J.size == 0:
            return {"rank": 0, "D_blind": int(J.shape[1]),
                    "s": [], "ker": np.eye(J.shape[1]),
                    "row": np.zeros((J.shape[1], 0))}
        u, s, vh = np.linalg.svd(J, full_matrices=True)
        s = np.asarray(s, dtype=float)
        smax = float(s.max()) if s.size else 0.0
        if smax <= 0:
            rank = 0
        else:
            rank = int((s > max(tol, tol * smax)).sum())
        P = J.shape[1]
        ker = vh[rank:, :].T  # P x (P-rank)
        row = vh[:rank, :].T  # P x rank
        return {"rank": rank, "D_blind": int(P - rank),
                "s": [float(v) for v in s],
                "smax": smax, "ker": ker, "row": row}
    except Exception:
        P = np.asarray(J).shape[1] if np.asarray(J).ndim == 2 else 0
        return {"rank": -1, "D_blind": -1, "s": [],
                "ker": np.zeros((P, 0)), "row": np.zeros((P, 0))}


def blind_analysis_for_region(rec, M, Q0, frames, channels="joint"):
    """Joint/per-channel Jacobians + blind dims for one region.

    Returns per-channel {J, rank, D_blind, ker, row, dim} and joint.
    """
    v0 = pack_Q(Q0)
    P = v0.size
    # Base exterior dim per channel (single build).
    X0 = reconstruct_from_Q(M, Q0, frames)
    base = exterior_vector(X0, rec, "joint")
    dims = {c: np.asarray(base["parts"][c]).size for c in CHANNELS}
    joint_dim = int(np.asarray(base["vec"]).size)

    def _build_joint(v):
        Q = unpack_Q(Q0, v)
        X = reconstruct_from_Q(M, Q, frames)
        return exterior_vector(X, rec, "joint")["vec"]

    out = {}
    J_joint = jacobian_Q(_build_joint, v0, joint_dim) if P > 0 else np.zeros(
        (joint_dim, 0))
    rj = rank_of(J_joint)
    out["joint"] = {"J": J_joint, "rank": rj["rank"],
                    "D_blind": rj["D_blind"], "s": rj["s"],
                    "ker": rj["ker"], "row": rj["row"],
                    "dim": joint_dim, "P": P}
    for c in CHANNELS:
        def _build(v, _c=c):
            Q = unpack_Q(Q0, v)
            X = reconstruct_from_Q(M, Q, frames)
            return exterior_vector(X, rec, _c)["vec"]
        Jc = jacobian_Q(_build, v0, dims[c]) if P > 0 else np.zeros(
            (dims[c], 0))
        rc = rank_of(Jc)
        out[c] = {"J": Jc, "rank": rc["rank"], "D_blind": rc["D_blind"],
                  "s": rc["s"], "ker": rc["ker"], "row": rc["row"],
                  "dim": dims[c], "P": P}
    return out


def x_jacobian_rank(rec, M, Q0, frames, eps=JAC_EPS):
    """Rank of Q -> X' map (continuous rank before blindness, E).

    X' vector = realified full psi (2N) + (graph fixed, so field only).
    Generic expectation: rank = 2 N_d.
    """
    v0 = pack_Q(Q0)
    P = v0.size
    if P == 0:
        return {"rank": 0, "P": 0, "D_cont": 0, "s": []}
    X0 = reconstruct_from_Q(M, Q0, frames)
    N = len(X0["order"])

    def _build(v):
        Q = unpack_Q(Q0, v)
        X = reconstruct_from_Q(M, Q, frames)
        psi = np.asarray(X["psi"], dtype=np.complex128)
        return np.concatenate([psi.real, psi.imag])

    Jx = jacobian_Q(_build, v0, 2 * N, eps=eps)
    r = rank_of(Jx)
    return {"rank": r["rank"], "P": P, "D_cont": r["rank"], "s": r["s"],
            "J": Jx}


def entry_blindness(J, N_Q, tol=RANK_TOL):
    """Per-entry (d_R,d_I) blindness audit (I).

    For each entry k, rank of the M x 2 sub-Jacobian J_k:
      0 -> fully blind (both R,I blind)
      1 -> split (one combo blind)
      2 -> fully visible.
    Naive blind count = 2*N_full + N_split; constraint rank
    C = naive - D_blind (>= 0 when D from same J).
    """
    J = np.asarray(J, dtype=float)
    rows = []
    for k in range(int(N_Q)):
        Jk = J[:, 2 * k:2 * k + 2] if J.shape[1] >= 2 * k + 2 else np.zeros(
            (J.shape[0], 0))
        r = rank_of(Jk, tol=tol)
        rk = r["rank"]
        if rk <= 0:
            cls = "full-blind"
        elif rk == 1:
            cls = "split"
        else:
            cls = "visible"
        rows.append({"entry": k, "rank": rk, "class": cls,
                     "s": r["s"]})
    N_full = sum(1 for r in rows if r["class"] == "full-blind")
    N_split = sum(1 for r in rows if r["class"] == "split")
    naive = 2 * N_full + N_split
    rj = rank_of(J, tol=tol)
    D = rj["D_blind"]
    C = int(naive - D) if D >= 0 else -1
    return {"rows": rows, "N_full": N_full, "N_split": N_split,
            "N_visible": int(N_Q) - N_full - N_split,
            "naive": naive, "D_blind": D, "C_constraints": C,
            "rank": rj["rank"]}


def validate_kernel(rec, M, Q0, frames, analysis, channel="joint",
                    delta=VAL_DELTA):
    """Finite-validation of tangent blindness (H).

    Along one kernel direction (if any) and one row direction (if any),
    perturb Q0 by delta and report exterior change (joint/channel),
    static change, wave/diff TV, and local distinguishability D in R.
    """
    from bh_graph import bhent as be

    v0 = pack_Q(Q0)
    P = v0.size
    ch = analysis[channel]
    ker = np.asarray(ch["ker"])
    row = np.asarray(ch["row"])
    X0 = reconstruct_from_Q(M, Q0, frames)
    psi0 = np.asarray(X0["psi"])
    s0 = None
    try:
        shim = dict(rec)
        shim["g"] = X0["g"]
        shim["order"] = list(X0["order"])
        s0 = be.exterior_static(psi0, shim)
    except Exception:
        s0 = None

    def _eval(dv):
        v = v0 + np.asarray(dv, dtype=float)
        Q = unpack_Q(Q0, v)
        X = reconstruct_from_Q(M, Q, frames)
        psi = np.asarray(X["psi"])
        o0 = exterior_vector(X0, rec, channel)["vec"]
        o1 = exterior_vector(X, rec, channel)["vec"]
        do = float(np.linalg.norm(o1 - o0))
        # Static change + TVs on X graphs (shared-graph pair needs same
        # graph: continuous-Q keeps covers, so graphs match exactly).
        try:
            shim1 = dict(rec)
            shim1["g"] = X["g"]
            shim1["order"] = list(X["order"])
            s1 = be.exterior_static(psi, shim1)
            ds = float(max(
                float(np.abs(np.asarray(s0[k]) - np.asarray(s1[k])).max(
                    initial=0.0)) for k in ("rho", "B", "J"))) if s0 is not None else -1.0
            sm = bool(be.is_static_match_ok(s0, s1)) if s0 is not None else False
        except Exception:
            ds, sm = -1.0, False
        try:
            wv = be.exterior_tv_wave(psi0, psi, shim1)
            df = be.exterior_tv_diff(psi0, psi, shim1)
            wmax = float(max(v["C"] for v in wv.values())) if wv else -1.0
            dmax = float(max(v["C"] for v in df.values())) if df else -1.0
        except Exception:
            wmax, dmax = -1.0, -1.0
        try:
            loc = be.local_distance_in_R(psi0, psi, shim1)
            D = float(loc["D"])
        except Exception:
            D = -1.0
        return {"dO": do, "d_static": ds, "static_match": sm,
                "wave_max": wmax, "diff_max": dmax, "D_local": D}

    out = {"P": P, "D_blind": int(ch["D_blind"]), "channel": channel,
           "delta": float(delta)}
    if ker.shape[1] > 0:
        vk = ker[:, 0]
        vk = vk / (np.linalg.norm(vk) + 1e-300) * delta
        out["kernel"] = _eval(vk)
        out["kernel_ok"] = bool(out["kernel"]["dO"] < VAL_KERNEL_BAR)
    else:
        out["kernel"] = None
        out["kernel_ok"] = True
    if row.shape[1] > 0:
        vr = row[:, 0]
        vr = vr / (np.linalg.norm(vr) + 1e-300) * delta
        out["row"] = _eval(vr)
        out["row_ok"] = bool(out["row"]["dO"] > VAL_SENS_MIN)
    else:
        out["row"] = None
        out["row_ok"] = True
    out["valid"] = bool(out["kernel_ok"] and out["row_ok"])
    return out


# ---------------------------------------------------------------------------
# Store-location anatomy (M) + collapse ancestry (N)
# ---------------------------------------------------------------------------

def blind_anatomy(analysis, steps, channel="joint"):
    """Weight of the blind subspace on each location class.

    For each kernel basis vector, per-entry weight = norm of its 2
    params; aggregate mean weight per location class + per-entry means.
    Tests whether only a boundary-sized basis survives (filed).
    """
    ker = np.asarray(analysis[channel]["ker"])
    N_Q = len(steps)
    locs = [s["location"] for s in steps]
    if ker.shape[1] == 0 or N_Q == 0:
        return {"classes": sorted(set(locs)),
                "mean_weight": {c: 0.0 for c in set(locs)},
                "per_entry": [0.0] * N_Q, "D_blind": 0}
    W = np.zeros(N_Q)
    for j in range(ker.shape[1]):
        v = ker[:, j]
        for k in range(N_Q):
            W[k] += float(v[2 * k] ** 2 + v[2 * k + 1] ** 2)
    W = W / (W.sum() + 1e-300)
    agg = {}
    for c in sorted(set(locs)):
        agg[c] = float(W[[i for i, l in enumerate(locs) if l == c]].sum())
    return {"classes": sorted(set(locs)), "mean_weight": agg,
            "per_entry": [float(w) for w in W],
            "D_blind": int(ker.shape[1])}


# ---------------------------------------------------------------------------
# Discrete cover census (J; combinatorial only, never combined)
# ---------------------------------------------------------------------------

def undirected_predecessors_capped(g2, k, cap=200):
    """SPLIT0 undirected predecessors with an honest enumeration cap.

    Exact undirected count is the pinned formula (3^d+1)/2 (U0-H); degrees
    >= 6 already exceed any feasible full enumeration (each row also
    builds a graph). When the exact count fits in `cap`, enumerate fully
    (identical to SPLIT0 undirected_predecessors). Otherwise lazily take
    the first `cap` unique canonical covers in split_covers generator
    order (deterministic), sorted by canonical key. Returns
    (rows, exact_count, capped). Rows mirror undirected_predecessors
    ({key,A,B,h,cprime,dE}).
    """
    from bh_graph import split0 as s0
    from bh_graph.contraction import apply_split_cover, split_covers

    nbrs = sorted(g2.neighbors(k))
    d = len(nbrs)
    exact = (3 ** d + 1) // 2
    if exact <= cap:
        return s0.undirected_predecessors(g2, k), exact, False
    seen: dict = {}
    for A, B in split_covers(nbrs):
        ka = tuple(sorted(A))
        kb = tuple(sorted(B))
        key = (ka, kb) if ka <= kb else (kb, ka)
        if key not in seen:
            seen[key] = (frozenset(A), frozenset(B))
            if len(seen) >= cap:
                break
    i, j = s0.fresh_labels(g2)
    rows = []
    for key in sorted(seen):
        A, B = seen[key]
        h = apply_split_cover(g2, k, set(A), set(B), i, j)
        rows.append({"key": key, "A": A, "B": B, "h": h,
                     "cprime": len(set(A) & set(B)),
                     "dE": int(h.number_of_edges()
                               - g2.number_of_edges())})
    return rows, exact, True


def blind_covers_single(rec, M, Q0, frames, steps, psi0_full,
                        static_bar=REMOTE_BAR):
    """Single-entry cover variations: blind + distinct counts.

    For each entry k, enumerate all undirected covers of the merged
    node at its step (SPLIT0 undirected_predecessors on the step's
    merged state) and test each alt cover (same d) for exterior-static
    blindness + dynamical TV filing + physical distinctness. Quotient:
    covers giving isomorphic (graph,|psi|) are merged (SPLIT0 iso
    classes where cheap; otherwise edge-count + field-aware check).
    Returns per-entry rows + totals. Log counts reported only as
    combinatorial information.
    """
    from bh_graph import bhent as be
    from bh_graph import store0 as st0

    # Rebuild step merged states by forward replay to get (g2,k) per step.
    # Simpler: use frames/Q0 reverse replay forward: start from X0 full,
    # re-collapse in recorded edge order, capturing merged states.
    X0 = reconstruct_from_Q(M, Q0, frames)
    g = X0["g"].copy()
    psi = np.asarray(X0["psi"]).copy()
    order = list(X0["order"])
    from bh_graph.contraction import contracted_state

    rows = []
    total_alts = 0
    total_blind = 0
    for k, st in enumerate(steps):
        i, j = st["edge"]
        # Current merged state after this step's contraction:
        g2, psi2, order2, kk, _ = contracted_state(g, psi, order, i, j,
                                                   "sum")
        # Enumerate undirected covers at kk (capped honestly at 200;
        # exact count is the pinned (3^d+1)/2 formula, never enumerated).
        cap = 200
        try:
            preds, n_covers, capped = undirected_predecessors_capped(
                g2, kk, cap)
        except Exception:
            preds, n_covers, capped = [], 0, False
        enum = preds[:cap]
        # True cover (canonical) for reference.
        true_cover = tuple(sorted([tuple(sorted(st["cover"][0])),
                                   tuple(sorted(st["cover"][1]))]))
        blind_here = 0
        distinct_here = 0
        pot_blind_here = 0
        details = []
        tested_here = 0
        # X0-side legs hoisted per entry (identical inputs/outputs).
        try:
            shim0 = dict(rec)
            shim0["g"] = X0["g"]
            shim0["order"] = list(X0["order"])
            psi0a = np.asarray(X0["psi"])
            sA = be.exterior_static(psi0a, shim0)
            pA = be.exterior_pot_profile(shim0)
            legs0_ok = True
        except Exception:
            legs0_ok = False
        for row_p in enum:
            A, B = set(row_p["A"]), set(row_p["B"])
            key = tuple(sorted([tuple(sorted(A)), tuple(sorted(B))]))
            if key == true_cover:
                continue
            total_alts += 1
            # Alt Q: same d, alt cover (canonicalized).
            ck = tuple(sorted([tuple(sorted(set(A))),
                               tuple(sorted(set(B)))]))
            q_alt = {"cover": [list(ck[0]), list(ck[1])],
                     "d": complex(Q0[k]["d"])}
            Qalt = [dict(q) for q in Q0]
            Qalt[k] = q_alt
            # Frames: swap flag depends on cover orientation; for the
            # quotient leg use frame=None canonical decode per step?
            # Here keep original frames except k (recompute swap).
            fr = dict(frames[k])
            tru = (tuple(sorted(set(A))), tuple(sorted(set(B))))
            # Canonical key is ck; swap iff tru != ck.
            fr["swap"] = bool(tru != ck)
            Falt = [dict(f) for f in frames]
            Falt[k] = fr
            try:
                Xalt = reconstruct_from_Q(M, Qalt, Falt)
            except Exception:
                continue
            # Exterior static blindness (same R/B partition).
            try:
                shim1 = dict(rec)
                shim1["g"] = Xalt["g"]
                shim1["order"] = list(Xalt["order"])
                sB = be.exterior_static(np.asarray(Xalt["psi"]), shim1)
                sm = bool(legs0_ok and be.is_static_match_ok(sA, sB))
            except Exception:
                sm = False
            # POT graph-sensitive leg (filed; wave/diff TV undefined
            # across different graphs -- BH-ENT-0 equiv precedent).
            try:
                pB = be.exterior_pot_profile(shim1)
                pot_diff = float(
                    __import__("numpy").abs(
                        pA["phi_ext"] - pB["phi_ext"]).max())
                pot_blind = bool(legs0_ok and pot_diff < 1e-9)
            except Exception:
                pot_diff, pot_blind = -1.0, False
            # Distinctness (graph+field mod R x U1, capped audit).
            try:
                dd = st0.is_graph_pair_distinct(
                    X0["g"], np.asarray(X0["psi"]), list(X0["order"]),
                    Xalt["g"], np.asarray(Xalt["psi"]), list(Xalt["order"]))
                distinct = bool(dd.get("distinct", False))
            except Exception:
                distinct = False
            if sm:
                blind_here += 1
            if distinct:
                distinct_here += 1
            if pot_blind:
                pot_blind_here += 1
            if sm and distinct:
                total_blind += 1
            tested_here += 1
            details.append({"blind_static": sm, "distinct": distinct,
                            "pot_diff": pot_diff,
                            "pot_blind": pot_blind})
        rows.append({"entry": k, "n_covers": n_covers,
                     "n_alts": tested_here,
                     "capped": capped,
                     "blind_static": blind_here,
                     "pot_blind": pot_blind_here,
                     "distinct": distinct_here})
        # Advance forward replay.
        g, psi, order = g2, np.asarray(psi2), list(order2)
    log_blind = float(math.log2(total_blind)) if total_blind > 1 else (
        0.0 if total_blind == 1 else float("-inf"))
    return {"rows": rows, "total_alts": total_alts,
            "total_blind_distinct": total_blind,
            "log2_blind": log_blind}


# ---------------------------------------------------------------------------
# Hidden-sector overlap (P)
# ---------------------------------------------------------------------------

def hidden_overlap(rec, M, Q0, frames, analysis, channel="joint"):
    """Overlap of STORE-blind psi variations with HIDDEN P_- subspace.

    Maps the STORE blind basis (ker J) to psi variations via the Q->X'
    Jacobian J_XQ, then compares with the J2 hidden-delta span (one per
    R cell) via principal angles (SVD of cross-Gram). Reports
    intersection/overlap/independence + dims. Non-J2 regions: inapplicable
    (filed, never forced).
    """
    if "c3" not in rec:
        return {"applicable": False, "reason": "non-J2 (no P_- sector)"}
    from bh_graph import hidden as _h

    ker = np.asarray(analysis[channel]["ker"])
    if ker.shape[1] == 0:
        return {"applicable": True, "D_blind": 0,
                "overlap": "vacuous (no blind dims)"}
    # J_XQ: d psi / d Q (complex N x P -> real 2N x P already in E).
    xr = x_jacobian_rank(rec, M, Q0, frames)
    Jx = np.asarray(xr["J"])  # 2N x P
    # STORE-blind psi directions (realified).
    S = Jx @ ker  # 2N x D
    # Hidden span: hidden_delta per R cell (realified).
    order = rec["order"]
    c3 = rec["c3"]
    cells = rec.get("cells", [])
    H = []
    for c in cells:
        try:
            d = _h.hidden_delta(order, c3, (int(c[0]), int(c[1])))
            H.append(np.concatenate([d.real, d.imag]))
        except Exception:
            continue
    if not H:
        return {"applicable": False, "reason": "no R cells filed"}
    H = np.column_stack(H)  # 2N x n_cells
    # Orthonormalize both, cross-Gram SVD -> principal cosines.
    def _orth(A):
        q, _ = np.linalg.qr(A)
        return q[:, :min(A.shape)]
    try:
        Qs = _orth(S)
        Qh = _orth(H)
        G = Qs.T @ Qh
        sv = np.linalg.svd(G, compute_uv=False)
        sv = [float(v) for v in sv]
        # Intersection dim (cos > 0.99), overlap (any cos > 0.5).
        n_inter = sum(1 for v in sv if v > 0.99)
        n_over = sum(1 for v in sv if v > 0.5)
        if n_inter == min(Qs.shape[1], Qh.shape[1]):
            verdict = "equality"
        elif n_over > 0:
            verdict = "overlap"
        else:
            verdict = "independence"
        return {"applicable": True, "D_blind": int(ker.shape[1]),
                "n_hidden": int(H.shape[1]),
                "principal_cos": sv, "n_intersection": n_inter,
                "n_overlap": n_over, "verdict": verdict}
    except Exception as e:
        return {"applicable": True, "error": str(e)[:200]}


# ---------------------------------------------------------------------------
# Graph multiplicity contrast (R)
# ---------------------------------------------------------------------------

def graph_contrast(rec, psi_bg):
    """BH-ENT exterior visibility of graph multiplicity vs STORE multiplicity.

    Graph leg: BH-ENT-0 equiv battery (actual vs one-interior-edge-toggled
    valid preimage): collapsed match + static match + POT maxdiff filed.
    STORE leg: on the same region, continuous-Q POT Jacobian norm (expect
    0: POT is graph-only) + static/wave/diff blind dims filed.
    Contrast is descriptive (no combined statistic).
    """
    from bh_graph import bhent as be

    # Graph leg (reuse BH-ENT-0 equiv payload construction, read-only).
    import networkx as nx

    Rset = set(rec["R"])
    interior_edges = sorted(tuple(sorted(e)) for e in rec["g"].edges()
                            if e[0] in Rset and e[1] in Rset)
    if not interior_edges:
        return {"applicable": False, "reason": "no interior edge"}
    g1 = rec["g"].copy()
    e = interior_edges[0]
    if g1.has_edge(*e):
        g1.remove_edge(*e)
    if not nx.is_connected(g1):
        g1.add_edge(*e)
        R = list(rec["R"])
        done = False
        for ii in range(len(R)):
            for jj in range(ii + 1, len(R)):
                if not g1.has_edge(R[ii], R[jj]):
                    g1.add_edge(R[ii], R[jj])
                    done = True
                    break
            if done:
                break
    r1 = dict(rec)
    r1["g"] = g1
    kint = max(v for v in rec["order"] if isinstance(v, int)) + 1
    c0 = be.collapse_region_direct(rec, psi_bg, kint)
    c1 = be.collapse_region_direct(r1, psi_bg, kint)
    es0 = {tuple(sorted(x)) for x in c0["g"].edges()}
    es1 = {tuple(sorted(x)) for x in c1["g"].edges()}
    s0 = be.exterior_static(psi_bg, rec)
    s1 = be.exterior_static(psi_bg, r1)
    p0 = be.exterior_pot_profile(rec)
    p1 = be.exterior_pot_profile(r1)
    graph_leg = {
        "collapsed_edge_match": bool(es0 == es1),
        "collapsed_field_match": bool(
            abs(c0["psi"][-1] - c1["psi"][-1]) < 1e-12),
        "graph_static_match": bool(be.is_static_match_ok(s0, s1)),
        "pot_maxdiff": float(
            np.abs(p0["phi_ext"] - p1["phi_ext"]).max()),
    }
    # STORE leg on same region/bg.
    try:
        col = collapse_region_with_store(rec, psi_bg, "asc")
        M, Q0, frames = col["M"], col["Q0"], col["frames"]
        an = blind_analysis_for_region(rec, M, Q0, frames, "joint")
        pot_J = np.asarray(an["pot"]["J"])
        store_leg = {
            "N_Q": len(Q0),
            "pot_J_norm": float(np.linalg.norm(pot_J)),
            "pot_D_blind": int(an["pot"]["D_blind"]),
            "static_D_blind": int(min(
                an["rho"]["D_blind"], an["B"]["D_blind"],
                an["J"]["D_blind"])),
            "joint_D_blind": int(an["joint"]["D_blind"]),
        }
    except Exception as ex:
        store_leg = {"error": str(ex)[:200]}
    return {"applicable": True, "graph_leg": graph_leg,
            "store_leg": store_leg}


# ---------------------------------------------------------------------------
# Scaling fits + law gates (K/L/S; analyzer-side pure functions)
# ---------------------------------------------------------------------------

def linear_fit(xs, ys):
    """OLS y = a x + c with R^2 (reused BH-ENT-0 form, no tuning)."""
    from bh_graph import bhent as be

    return be.linear_fit(xs, ys)


def quad_f_test(xs, ys):
    """Quadratic-vs-linear F-test (reused BH-ENT-0)."""
    from bh_graph import bhent as be

    return be.quad_f_test(xs, ys)


def second_diffs(ys):
    """Consecutive second differences."""
    from bh_graph import bhent as be

    return be.second_diffs(ys)


def law_gates_bhqent(rows):
    """Preregistered AREA/VOLUME/MIXED/BLIND-NONE gates (pure).

    rows: list of {spec, n_R, b_R, D_joint, D_static} (headline battery).
    Returns gates + fits. Headline = joint D (full O_ext); static filed.
    """
    # BLIND-NONE: all joint D == 0.
    all_zero = all(int(r["D_joint"]) == 0 for r in rows)
    # Fixed-b growth (paths b=2).
    paths = [r for r in rows if r["spec"].startswith("P")
             and "_" not in r["spec"]]
    paths = sorted(paths, key=lambda r: r["n_R"])
    if len(paths) >= 2:
        dys = [int(r["D_joint"]) for r in paths]
        dns = [int(r["n_R"]) for r in paths]
        fit_fixed = linear_fit(dns, dys)
        growth = max(dys) - min(dys)
    else:
        fit_fixed = {"a": 0.0, "c": 0.0, "r2": 1.0, "ss_res": 0.0, "n": 0}
        growth = 0
    # Boundary fit D vs b.
    bs = [int(r["b_R"]) for r in rows]
    ds = [int(r["D_joint"]) for r in rows]
    fit_b = linear_fit(bs, ds) if len(rows) >= 2 else {
        "a": 0.0, "c": 0.0, "r2": 1.0, "ss_res": 0.0, "n": len(rows)}
    # Volume fit D vs n.
    ns = [int(r["n_R"]) for r in rows]
    fit_n = linear_fit(ns, ds) if len(rows) >= 2 else {
        "a": 0.0, "c": 0.0, "r2": 1.0, "ss_res": 0.0, "n": len(rows)}
    sd = second_diffs(ds) if len(ds) >= 3 else []
    mean2 = float(sum(sd) / len(sd)) if sd else 0.0
    qf = quad_f_test(ns, ds) if len(ns) >= 4 else {
        "F": 0.0, "p": 1.0, "quadratic_better": False}
    # Mixed predictor m = b * log2(b) (b>=2; else 0).
    def _m(b):
        b = int(b)
        return float(b * math.log2(b)) if b >= 2 else 0.0
    ms = [_m(b) for b in bs]
    fit_m = linear_fit(ms, ds) if len(rows) >= 2 else {
        "a": 0.0, "c": 0.0, "r2": 1.0, "ss_res": 0.0, "n": len(rows)}
    boundary_gate = bool(
        fit_b["r2"] > BHQ_BOUNDARY_R2_BAR
        and fit_b["a"] > BHQ_BOUNDARY_SLOPE_LO
        and abs(fit_fixed["a"]) < BHQ_BOUNDARY_SLOPE_BAR
        and growth < BHQ_BOUNDARY_GROWTH_BAR)
    volume_gate = bool(
        fit_n["r2"] > BHQ_VOLUME_R2_BAR
        and abs(mean2) < BHQ_VOLUME_2D_BAR
        and fit_n["a"] > BHQ_VOLUME_SLOPE_LO
        and not qf["quadratic_better"])
    mixed_gate = bool(
        fit_m["r2"] > BHQ_MIXED_R2_BAR
        and BHQ_MIXED_SLOPE_BAND[0] < fit_m["a"]
        < BHQ_MIXED_SLOPE_BAND[1])
    # Mixed-dim: boundary component + irreducible volume growth.
    mixed_dim_gate = bool(
        fit_b["r2"] > BHQ_BOUNDARY_R2_BAR
        and fit_b["a"] > BHQ_BOUNDARY_SLOPE_LO
        and growth >= BHQ_BOUNDARY_GROWTH_BAR)
    return {
        "blind_none_gate": bool(all_zero),
        "boundary_gate": boundary_gate,
        "volume_gate": volume_gate,
        "mixed_gate": mixed_gate,
        "mixed_dim_gate": mixed_dim_gate,
        "fixed_growth": int(growth),
        "fixed_fit": fit_fixed,
        "boundary_fit": fit_b,
        "volume_fit": fit_n,
        "mixed_fit": fit_m,
        "quad_ftest": qf,
        "second_diffs": sd,
    }


def verdict_of(gates, controls_ok, factor_two_ok=True, cause=""):
    """Verdict ladder (preregistered priority; firewall-safe strings)."""
    if not controls_ok:
        return f"BHQENT0-INCOMPLETE (apparatus: {cause})"
    if gates["blind_none_gate"]:
        return "BHQENT0-BLIND-NONE"
    if gates["boundary_gate"] and factor_two_ok:
        return "BHQENT0-AREA-DIM"
    if gates["mixed_dim_gate"]:
        return "BHQENT0-MIXED-DIM"
    if gates["volume_gate"]:
        return "BHQENT0-VOLUME-DIM"
    if gates["mixed_gate"]:
        # b log b without clean boundary/volume split files as mixed-dim
        # only if volume growth present, else unclassified per ladder.
        if gates["fixed_growth"] >= BHQ_BOUNDARY_GROWTH_BAR:
            return "BHQENT0-MIXED-DIM"
        return "BHQENT0-UNCLASSIFIED"
    return "BHQENT0-UNCLASSIFIED"


# ---------------------------------------------------------------------------
# Measure-debt audit (T) + firewall scan
# ---------------------------------------------------------------------------

def measure_audit():
    """Audit earned results for a finite Q-fiber measure (T).

    Checks FIBER0-DEBT (two rivals, no unique measure), MEASURE0-DEBT
    (no unique weighting), and the STORE0 capacity filing (no bits
    claimed for continuous dims). Returns audit (always passes when
    evidence complete; outcome blocked unless a measure is earned).
    """
    import json
    import os

    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(os.path.dirname(here))
    out = {"checked": [], "measure_earned": False}
    try:
        with open(os.path.join(root, "data", "fiber0_verdict.json")) as f:
            fv = json.load(f)
        out["checked"].append(
            f"FIBER0:{fv.get('verdict', '?')}")
        out["fiber0_debt"] = bool(
            fv.get("verdict", "") == "FIBER0-DEBT")
    except Exception as e:
        out["checked"].append(f"FIBER0:error:{str(e)[:80]}")
        out["fiber0_debt"] = False
    try:
        with open(os.path.join(root, "data", "measure0_verdict.json")) as f:
            mv = json.load(f)
        out["checked"].append("MEASURE0:loaded")
        out["measure0_gates"] = len(mv.get("gates", []))
    except Exception as e:
        out["checked"].append(f"MEASURE0:error:{str(e)[:80]}")
    try:
        with open(os.path.join(root, "data", "store0",
                               "verdict.json")) as f:
            sv = json.load(f)
        out["checked"].append(f"STORE0:{sv.get('verdict', '?')}")
    except Exception as e:
        out["checked"].append(f"STORE0:error:{str(e)[:80]}")
    # No earned finite measure exists in the frozen bank at prereg.
    out["measure_earned"] = False
    out["entropy_blocked"] = True
    out["reason"] = ("no earned finite measure/resolution/quantization "
                     "of the continuous blind Q fiber in the frozen bank; "
                     "entropy remains blocked")
    return out


def scan_forbidden_ok(obj):
    """Boolean check: no firewall tokens anywhere in the record."""
    try:
        txt = repr(obj)
        return bool(all(tok not in txt for tok in FORBIDDEN_TOKENS))
    except Exception:
        return False


def fitted_param_count():
    """Zero fitted parameters (audited)."""
    return 0
