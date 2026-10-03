"""SCALE-0: fixed-geometry asymptotic scaling bank apparatus.

Banks already-earned fixed-geometry observables at large L (64/128/256/512)
BEFORE dynamic geometry makes them expensive. Read-only consumption of the
frozen banked apparatus (obs0/obs0r/obs1/response/ballistic/potential/quot/
zero/vacexc/vaccomp/vacfield/driven/formation/malus); this module ADDS only
sparse large-L estimators, regime bookkeeping, scaling fits, and the O(L)
matrix schema. It never modifies banked code and never retunes a bar.

Frozen law: H = -A, J = 1, hbar = 1 (P1/EM-0 locked).

Regime firewall: t_wrap(r; L) = (L - r)/8 (RESPONSE V_MAX bound). PRE fits
use t < t_wrap strictly; POST fits use t > t_wrap strictly; any fit pooling
both is VOID. Static solves are regime STATIC.

Precision scaling (SCALE0-PREREG P1..P8, the ONLY deviations from banked
dense protocols): dense->Krylov traces (P1), spsolve->CG statics (P2),
full-target->75-subset OBS taus at L >= 256 (P3), stored-trace decimation
(P4), no ZERO post at L >= 256 (P5), no Weyl at L >= 256 (P6), no stored
rows at L >= 64 (P7), banked eigen/tau/dim read-only (P8).
"""

from __future__ import annotations

import math

import networkx as nx
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import cg as _sp_cg
from scipy.sparse.linalg import expm_multiply

# ---------------------------------------------------------------------------
# Frozen ladder / substrates / constants (SCALE0-PREREG)
# ---------------------------------------------------------------------------

LADDER = (64, 128, 256, 512)
REGRESS_L = (4, 8, 28)
SUBSTRATES = ("j2", "sq")

V_MAX = 8.0          # RESPONSE bound (frozen)
VEST_PACKET = 1.21   # J2 packet speed for T rules (banked V_BANKED j2 ~1.2075)
OM_J2 = -8.5         # POT-1 frozen static pin frequency
CG_RTOL = 1e-11      # OBS1-precedent CG tolerance
TRACE_DECIM = 20     # P4 max stored-trace stride
N_TARGETS_SUBSET = 75  # P3 frozen 75-target subset (25/tercile)

# Regression bars (HARD gates, SCALE0-PREREG R-*).
BAR_RESP_V_FIELD = (0.5, 12.0)
BAR_RESP_V_RTOL = 0.05
BAR_RESP_V_QUAD_RTOL = 0.10
BAR_RESP_DECOMP = 1e-10
BAR_P1_J2_RTOL = 0.01
BAR_P1_SQ_RTOL = 0.05
BAR_CG_SPSOLVE = 1e-8
BAR_POT_XI_RTOL = 0.20
BAR_QUOT_ALG = 1e-12
BAR_QUOT_ANTI = 1e-9
BAR_VACEXC_FRAC = 1e-9
BAR_VACEXC_V_RTOL = 0.10
BAR_KRYLOV_DS = 0.05
BAR_KRYLOV_TAU_RTOL = 0.05
BAR_REPLAY = 1e-9

BANKED = {
    "resp_v_field": 7.947,
    "resp_v_quad": 5.94,
    "p1_j2": 1.2075,
    "p1_sq": 0.9658,
}

PRECISION = {
    "P1": "dense->Krylov wave/diffusion traces",
    "P2": "spsolve->CG static (rtol 1e-11)",
    "P3": "full-target->75-subset OBS taus at L>=256",
    "P4": "stored traces decimated (fits full-rate)",
    "P5": "no ZERO post at L>=256 (cost)",
    "P6": "no Weyl at L>=256 (needs full spectrum)",
    "P7": "no stored rows at L>=64",
    "P8": "banked eigen/tau/dim read-only",
}


# ---------------------------------------------------------------------------
# Substrate builders (thin read-only assembly over frozen constructors)
# ---------------------------------------------------------------------------

def j2_size(L: int) -> int:
    """J2 torus node count N = 2L^2."""
    return 2 * int(L) * int(L)


def sq_size(L: int) -> int:
    """Square torus node count N = L^2."""
    return int(L) * int(L)


def build_graph(sub: str, L: int) -> nx.Graph:
    """Frozen substrate graph (J2 or square torus)."""
    from bh_graph.formation import j2_torus_graph
    from bh_graph.graphs import build_torus_grid

    if sub == "j2":
        return j2_torus_graph(int(L))
    if sub == "sq":
        return build_torus_grid(int(L))
    raise ValueError(f"unknown substrate {sub!r}")


def substrate_coords(sub: str, L: int) -> dict:
    """Readout coords: J2 id -> (x, y, b); sq id -> (x, y)."""
    from bh_graph.formation import j2_torus_coords

    L = int(L)
    if sub == "j2":
        return j2_torus_coords(L)
    if sub == "sq":
        return {x * L + y: (float(x), float(y)) for x in range(L) for y in range(L)}
    raise ValueError(f"unknown substrate {sub!r}")


def quotient_coords_j2(c3: dict) -> dict:
    """Collapse J2 (x, y, b) labels to quotient (x, y) readout."""
    return {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}


def node_order(g: nx.Graph) -> list:
    """Deterministic Hilbert index map: sorted node labels."""
    return sorted(g.nodes())


def hamiltonian(g: nx.Graph, order: list):
    """Frozen law H(G) = -A(G) as CSR (J = 1)."""
    return -nx.to_scipy_sparse_array(g, nodelist=list(order), format="csr", dtype=float)


def lrw_operator(g: nx.Graph, order: list):
    """Unbiased-walk generator Lrw = I - D^-1 A as CSR (exact, any degree)."""
    n = len(order)
    idx = {v: i for i, v in enumerate(order)}
    deg = np.array([float(g.degree(v)) for v in order], dtype=float)
    deg[deg <= 0.0] = 1.0
    rows, cols, data = [], [], []
    for v in order:
        i = idx[v]
        rows.append(i)
        cols.append(i)
        data.append(1.0)
        for w in g.neighbors(v):
            rows.append(i)
            cols.append(idx[w])
            data.append(-1.0 / deg[i])
    return sparse.csr_matrix((np.array(data), (np.array(rows), np.array(cols))),
                             shape=(n, n))


# ---------------------------------------------------------------------------
# Frozen time rules (SCALE0-PREREG)
# ---------------------------------------------------------------------------

def response_T(L: int) -> float:
    """RESPONSE T(L) = max(16, 2*(L-10)/8 + 4)."""
    L = int(L)
    return max(16.0, 2.0 * (L - 10) / 8.0 + 4.0)


def packet_T_pre(L: int) -> float:
    """Packet pre-wrap horizon 0.30*L/1.21."""
    return 0.30 * int(L) / VEST_PACKET


def packet_T_post(L: int) -> float:
    """Packet recurrence horizon 1.20*L/1.21."""
    return 1.20 * int(L) / VEST_PACKET


def zero_T_post(L: int) -> float:
    """ZERO post horizon 1.5*(L/2)/1.21 (L <= 128 only per P5)."""
    return 1.5 * (int(L) / 2.0) / VEST_PACKET


def t_wrap(r: float, L: int, v: float = V_MAX) -> float:
    """Earliest torus return (L - r)/v (RESPONSE bound, frozen)."""
    return (int(L) - float(r)) / float(v)


def is_pre_ok(t: float, r: float, L: int) -> bool:
    """Boolean check: t strictly before t_wrap (never raises)."""
    try:
        return bool(float(t) < t_wrap(float(r), int(L)))
    except (TypeError, ValueError):
        return False


def is_post_ok(t: float, r: float, L: int) -> bool:
    """Boolean check: t strictly after t_wrap (never raises)."""
    try:
        return bool(float(t) > t_wrap(float(r), int(L)))
    except (TypeError, ValueError):
        return False


def split_pre_post(ts: np.ndarray, r: float, L: int) -> dict:
    """Index masks for PRE / POST samples at shell radius r (strict)."""
    ts = np.asarray(ts, dtype=float)
    tw = t_wrap(float(r), int(L))
    pre = ts < tw
    post = ts > tw
    return {"t_wrap": float(tw), "pre": pre, "post": post,
            "n_pre": int(pre.sum()), "n_post": int(post.sum())}


def is_regime_pure_ok(ts, r: float, L: int, regime: str) -> bool:
    """Boolean check: all sample times lie in the claimed regime."""
    try:
        ts = np.asarray(list(ts), dtype=float)
        if regime == "PRE":
            return bool(np.all(ts < t_wrap(float(r), int(L))))
        if regime == "POST":
            return bool(np.all(ts > t_wrap(float(r), int(L))))
        return False
    except (TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# Sparse estimators (P1/P2): Krylov traces + CG statics
# ---------------------------------------------------------------------------

def krylov_wave_traces(h, origin_idx: int, target_idx, ts: np.ndarray) -> np.ndarray:
    """Onsite-probability traces |psi_j(t)|^2 for H delta launch (Krylov).

    Mirrors obs0._target_traces_wave mathematics with sparse evolution:
    psi(t) = exp(-iHt) delta_o. Returns (T, Nt) array. ts must be a
    uniform grid starting at 0 (frozen OBS grids are).
    """
    from bh_graph.ballistic import evolve_fixed

    ts = np.asarray(list(ts), dtype=float)
    n = h.shape[0]
    psi0 = np.zeros(n, dtype=np.complex128)
    psi0[int(origin_idx)] = 1.0
    dt = float(ts[1] - ts[0]) if len(ts) > 1 else 0.05
    rows = evolve_fixed(psi0, h, dt, len(ts) - 1)["psi"]
    tj = np.asarray(list(target_idx), dtype=int)
    return (np.abs(rows[:, tj]) ** 2).astype(float)


def krylov_diffusion_return(lrw, origin_idx: int, ts: np.ndarray) -> np.ndarray:
    """Unbiased-walk return P_oo(t) = [exp(-Lrw t)]_oo via Krylov.

    Exact e^{-t Lrw} on the delta vector (regular graphs: identical to
    the banked Lsym-conjugation evolution; non-regular: exact Lrw).
    """
    ts = np.asarray(list(ts), dtype=float)
    n = lrw.shape[0]
    p0 = np.zeros(n, dtype=float)
    p0[int(origin_idx)] = 1.0
    gen = -lrw.tocsr()
    out = np.zeros(len(ts), dtype=float)
    for k, t in enumerate(ts):
        if float(t) == 0.0:
            out[k] = 1.0
        else:
            row = np.asarray(expm_multiply(gen * float(t), p0), dtype=float).ravel()
            out[k] = float(row[int(origin_idx)])
    return out


def krylov_diffusion_traces(lrw, origin_idx: int, target_idx, ts: np.ndarray,
                            chunk: int = 512) -> np.ndarray:
    """Occupation traces p_j(t) for the unbiased walk (Krylov, chunked).

    Mirrors obs0._target_traces_diff mathematics (exact Lrw). Returns
    (T, Nt). Chunked over time to bound memory at large N.
    """
    ts = np.asarray(list(ts), dtype=float)
    tj = np.asarray(list(target_idx), dtype=int)
    n = lrw.shape[0]
    p0 = np.zeros(n, dtype=float)
    p0[int(origin_idx)] = 1.0
    out = np.zeros((len(ts), len(tj)), dtype=float)
    gen = -lrw.tocsr()
    blocks = [list(range(a, min(a + chunk, len(ts)))) for a in range(0, len(ts), chunk)]
    for blk in blocks:
        seg = ts[blk]
        if len(seg) == 1 and seg[0] == 0.0:
            mat = p0[None, :]
        else:
            mat = np.asarray(expm_multiply(gen, p0, start=float(seg[0]),
                                           stop=float(seg[-1]), num=len(seg)),
                             dtype=float)
            if mat.ndim == 1:
                mat = mat[None, :]
        out[blk, :] = mat[:, tj]
    return out


def cg_static_phi(h_csc, src_idx: int, omega: float,
                  rtol: float = CG_RTOL) -> np.ndarray:
    """POT-1 static field via CG (OBS1 equation, P2 precision scaling).

    Solves (H_BB - w) phi_B = -H_BS s, phi_S = s = 1.0. H - wI is SPD
    (spectrum in [0.5, z+0.5]), so CG converges with zero fill-in.
    Pinned bit-compatible to spsolve at 1e-8 (tests/test_run_obs1.py
    precedent; re-pinned here at L = 28 by R-POT).
    """
    n = h_csc.shape[0]
    src = int(src_idx)
    mask = np.ones(n, dtype=bool)
    mask[src] = False
    bulk = np.nonzero(mask)[0]
    a = (h_csc - float(omega) * sparse.eye(n)).tocsc()
    abb = a[bulk, :][:, bulk]
    rhs = -np.asarray(a[bulk, src].todense()).ravel().astype(np.complex128)
    sol, info = _sp_cg(abb, rhs, rtol=float(rtol))
    if int(info) != 0:
        raise RuntimeError(f"CG static solve failed to converge (info={info})")
    phi = np.zeros(n, dtype=np.complex128)
    phi[bulk] = np.asarray(sol, dtype=np.complex128)
    phi[src] = 1.0
    return phi


def evolve_segments(h, psi0: np.ndarray, dt: float, n_steps: int,
                    chunk_steps: int = 128):
    """Yield (k_offset, rows) Krylov segments (memory-bounded evolution).

    Each segment restarts Krylov from the current state (differences vs
    one-shot evolution are fp-noise only, pinned). rows covers steps
    k_offset..k_offset+len(rows)-1. Never materializes full (T, N).
    """
    from bh_graph.ballistic import evolve_fixed

    psi = np.asarray(psi0, dtype=np.complex128)
    k = 0  # next unfilled step
    m0 = min(int(chunk_steps), n_steps - k)
    rec = evolve_fixed(psi, h, float(dt), m0)["psi"]  # steps k..k+m0
    yield k, rec
    psi = rec[-1]
    k = k + m0 + 1
    while k <= n_steps:
        m = min(int(chunk_steps), n_steps - k + 1)
        rec = evolve_fixed(psi, h, float(dt), m)["psi"]  # steps k-1..k-1+m
        yield k, rec[1:]  # new steps k..k-1+m
        psi = rec[-1]
        k = k + m


def krylov_wave_traces_chunked(h, origin_idx: int, target_idx, ts: np.ndarray,
                               chunk_steps: int = 128) -> np.ndarray:
    """Chunked |psi_j(t)|^2 traces (== krylov_wave_traces, bounded memory)."""
    ts = np.asarray(list(ts), dtype=float)
    tj = np.asarray(list(target_idx), dtype=int)
    n = h.shape[0]
    psi0 = np.zeros(n, dtype=np.complex128)
    psi0[int(origin_idx)] = 1.0
    dt = float(ts[1] - ts[0]) if len(ts) > 1 else 0.05
    out = np.zeros((len(ts), len(tj)), dtype=float)
    for k_off, rows in evolve_segments(h, psi0, dt, len(ts) - 1, chunk_steps):
        out[k_off:k_off + rows.shape[0], :] = (np.abs(rows[:, tj]) ** 2)
    return out


def krylov_diffusion_stepped(lrw, origin_idx: int, target_idx, dt: float,
                             n_steps: int) -> np.ndarray:
    """Per-step unbiased-walk traces p_j(t) (bounded memory, exact Lrw)."""
    tj = np.asarray(list(target_idx), dtype=int)
    n = lrw.shape[0]
    p = np.zeros(n, dtype=float)
    p[int(origin_idx)] = 1.0
    gen = (-lrw.tocsr() * float(dt)).tocsr()
    out = np.zeros((n_steps + 1, len(tj)), dtype=float)
    out[0, :] = p[tj]
    for k in range(1, n_steps + 1):
        p = np.asarray(expm_multiply(gen, p), dtype=float).ravel()
        out[k, :] = p[tj]
    return out


def decimate_trace(tr: np.ndarray, ts: np.ndarray, stride: int = TRACE_DECIM) -> dict:
    """P4 stored-trace decimation (fits always run full-rate first)."""
    tr = np.asarray(tr, dtype=float)
    ts = np.asarray(ts, dtype=float)
    s = max(int(stride), 1)
    return {"trace": tr[::s].tolist(), "ts": ts[::s].tolist(), "stride": s,
            "n_full": int(len(tr))}


# ---------------------------------------------------------------------------
# Scaling fits (theory-first; effective exponents + monotone trends otherwise)
# ---------------------------------------------------------------------------

def fit_const(ys) -> dict:
    """Constant fit: {value, spread, n} (theory-first for L-independent)."""
    y = np.asarray(list(ys), dtype=float)
    y = y[np.isfinite(y)]
    if len(y) == 0:
        return {"value": float("nan"), "spread": float("nan"), "n": 0}
    return {"value": float(np.median(y)), "spread": float(y.max() - y.min()),
            "n": int(len(y))}


def fit_loglog(xs, ys) -> dict:
    """OLS power fit y ~ x^p on logs: {p, intercept, r2, n}."""
    x = np.asarray(list(xs), dtype=float)
    y = np.asarray(list(ys), dtype=float)
    bad = {"p": float("nan"), "intercept": float("nan"), "r2": float("nan"), "n": 0}
    if x.shape != y.shape or len(x) < 3:
        return bad
    m = np.isfinite(x) & np.isfinite(y) & (x > 0) & (y > 0)
    if int(m.sum()) < 3:
        return bad
    lx, ly = np.log(x[m]), np.log(y[m])
    p, b = np.polyfit(lx, ly, 1)
    pred = p * lx + b
    denom = float(np.sum((ly - ly.mean()) ** 2))
    r2 = 1.0 - float(np.sum((ly - pred) ** 2)) / denom if denom > 0 else float("nan")
    return {"p": float(p), "intercept": float(b), "r2": float(r2), "n": int(m.sum())}


def is_monotone_ok(ys) -> bool:
    """Boolean check: finite values monotone (non-decreasing or not)."""
    try:
        y = np.asarray(list(ys), dtype=float)
        y = y[np.isfinite(y)]
        if len(y) < 2:
            return False
        d = np.diff(y)
        return bool(np.all(d >= 0) or np.all(d <= 0))
    except (TypeError, ValueError):
        return False


def asymptotic_estimate(xs, ys, err=None) -> dict:
    """Justified asymptotic estimate or explicit unresolved entry.

    JUSTIFIED only if the last two rungs agree within error AND the
    sequence is monotone; otherwise unresolved-asymptotic (no eyeball
    extrapolation). err defaults to rung spread of the last two.
    """
    x = np.asarray(list(xs), dtype=float)
    y = np.asarray(list(ys), dtype=float)
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    if len(y) < 3:
        return {"status": "unresolved-asymptotic", "reason": "fewer-than-3-rungs",
                "n": int(len(y))}
    e = float(err) if err is not None else float(abs(y[-1] - y[-2]))
    agree = bool(abs(y[-1] - y[-2]) <= max(e, 1e-300))
    mono = is_monotone_ok(y)
    if agree and mono:
        return {"status": "estimated", "value": float(y[-1]),
                "err": float(abs(y[-1] - y[-2])), "n": int(len(y))}
    why = []
    if not agree:
        why.append("last-two-rungs-disagree")
    if not mono:
        why.append("non-monotone")
    return {"status": "unresolved-asymptotic", "reason": "+".join(why),
            "n": int(len(y)), "last_two": [float(y[-2]), float(y[-1])]}


# ---------------------------------------------------------------------------
# O(L) matrix schema (frozen)
# ---------------------------------------------------------------------------

MATRIX_FIELDS = ("observable", "L", "substrate", "regime", "channel",
                 "variant", "value", "stat", "method", "n",
                 "precision_note", "unresolved")

REGIMES = ("PRE", "POST", "STATIC", "REGRESS")


def make_row(observable: str, L: int, substrate: str, regime: str,
             channel: str, variant: str, value, stat: dict,
             method: str, n: int, precision_note: str = "",
             unresolved=None) -> dict:
    """One O(L) matrix row (frozen schema; unresolved null or {reason})."""
    if regime not in REGIMES:
        raise ValueError(f"regime must be one of {REGIMES}")
    if unresolved is not None and "reason" not in dict(unresolved):
        raise ValueError("unresolved entries need a reason")
    return {"observable": str(observable), "L": int(L),
            "substrate": str(substrate), "regime": str(regime),
            "channel": str(channel), "variant": str(variant),
            "value": value, "stat": dict(stat), "method": str(method),
            "n": int(n), "precision_note": str(precision_note),
            "unresolved": (None if unresolved is None else dict(unresolved))}


def is_matrix_ok(rows) -> bool:
    """Boolean check: every row matches the frozen schema (never raises)."""
    try:
        for r in list(rows):
            if tuple(sorted(r.keys())) != tuple(sorted(MATRIX_FIELDS)):
                return False
            if r["regime"] not in REGIMES:
                return False
            u = r["unresolved"]
            if u is not None and "reason" not in dict(u):
                return False
        return True
    except (TypeError, ValueError, AttributeError):
        return False


def is_theory_form_ok(form: str) -> bool:
    """Boolean check: fit form is a registered theory/effective form."""
    return str(form) in {"const", "power", "exact-zero", "exact-formula",
                         "saturate", "trend-only", "unresolved"}
