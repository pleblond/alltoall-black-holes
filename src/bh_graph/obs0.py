"""OBS-0 Operational Geometry Concordance apparatus (frozen per OBS0-PREREG).

Rulers take (graph, node-ids) ONLY -- no coordinates, quotient labels,
shell indices, generators, or pairwise fitting (C2-audited). J2 coordinates
enter ONLY via explicitly marked VALIDATION-ONLY helpers (test-set
construction / post-hoc grouping) and the C5 wave-regression section.

Conventions (LOCKED in prereg):
  D        = intrinsic diameter = BFS depth from node 0 (exact diameter on
             vertex-transitive substrates; intrinsic proxy otherwise).
  wrap-safe: graph distance R < D/2 (C4).
  d_H      = log-log OLS slope of V(r) over r in [4, floor(D/2)-1].
  walk     = continuous-time unbiased walk (jump rate 1, uniform neighbors),
             generator -Lrw, computed exactly via Lsym conjugation
             (regular graphs: Lrw == Lsym == L/z elementwise).
  d_s      = mean-return fit Pbar(t) ~ t^{-d/2} over DS_TS hops.
  tau_D    = CFD-first-peak of p_j(t) (dt=0.25, Tmax=3(D/2)^2).
  H        = -A, J=1 (P1 banked law); delta launch; tau_W = CFD-first-peak
             (dt=0.05, Tmax=D); R_W = V_BANKED[sub]*tau_W.
  CFD      = first local maximum with height >= 1/2 trace global max.
  d_W      = arrival-volume fit A(T) ~ T^d over the train-law T-window.
  delta    = |Rhat - R_G| / max(R_G, 4) with globally-fitted calibration.
"""

from __future__ import annotations

import math

import networkx as nx
import numpy as np

# Frozen prereg constants.
D_H_LO = 4
DS_TS = np.array([12.0, 14.0, 16.0, 20.0, 24.0])
WEYL_LO_FRAC = 0.08
WEYL_HI_FRAC = 0.70
WEYL_K = 400
CFD_FRAC = 0.5
DT_WAVE = 0.05
DT_DIFF = 0.25
R_FLOOR = 4.0
V_BANKED = {"j2": 1.2075, "sq": 0.9658}  # P1.1b / P1.1a means
ORIGIN_SEED_BASE = 6900
TARGET_SEED_BASE = 8100
N_ORIGINS = 16
PER_TERCILE = 25


def is_connected_ok(g: nx.Graph) -> bool:
    """Boolean check: nonempty connected graph (never raises)."""
    return len(g) > 0 and nx.is_connected(g)


def intrinsic_diameter(g: nx.Graph, src=0) -> int:
    """BFS depth from `src` (== diameter on vertex-transitive graphs).

    Unknown/empty graph gives 0 (no exceptions for control flow).
    """
    if len(g) == 0 or src not in g:
        return 0
    d = nx.single_source_shortest_path_length(g, src)
    return int(max(d.values(), default=0))


def wrap_limit(D: int) -> float:
    """Wrap-safe radius R < D/2 (C4 intrinsic bound)."""
    return float(D) / 2.0


def hausdorff_window(D: int, lo: int = D_H_LO):
    """Preregistered d_H window [lo, floor(D/2)-1], or None if empty."""
    hi = int(math.floor(float(D) / 2.0)) - 1
    if hi - lo + 1 < 3:
        return None
    return (int(lo), int(hi))


def ball_shells_vols(g: nx.Graph, src, rmax: int):
    """Shell counts s[0..rmax] and cumulative volumes V (BFS from `src`)."""
    if src not in g:
        return np.zeros(0), np.zeros(0)
    d = nx.single_source_shortest_path_length(g, src)
    shells = np.array([sum(1 for n in d if d[n] == r) for r in range(rmax + 1)],
                      dtype=float)
    return shells, np.cumsum(shells)


def fit_loglog(xs, ys) -> dict:
    """OLS fit y ~ x^p on logs: {p, intercept, r2, n} (NaN if n < 3)."""
    x = np.asarray(list(xs), dtype=float)
    y = np.asarray(list(ys), dtype=float)
    bad = {"p": float("nan"), "intercept": float("nan"), "r2": float("nan"),
           "n": 0}
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
    return {"p": float(p), "intercept": float(b), "r2": float(r2),
            "n": int(m.sum())}


def hausdorff_dim(g: nx.Graph, src, lo: int = D_H_LO) -> dict:
    """Topological ruler dimension over the preregistered window."""
    D = intrinsic_diameter(g, src)
    win = hausdorff_window(D, lo)
    if win is None:
        return {"d": float("nan"), "r2": float("nan"), "n": 0, "D": D,
                "window": None, "ok": False}
    _, vols = ball_shells_vols(g, src, win[1])
    rr = np.arange(len(vols), dtype=float)
    m = (rr >= win[0]) & (rr <= win[1])
    fit = fit_loglog(rr[m], vols[m])
    return {"d": fit["p"], "r2": fit["r2"], "n": fit["n"], "D": D,
            "window": win, "ok": bool(fit["n"] >= 3)}


def lsym_system(g: nx.Graph, order=None):
    """Dense Lsym eigensystem (ascending evals, column evecs, deterministic)."""
    if order is None:
        order = sorted(g.nodes())
    L = nx.normalized_laplacian_matrix(g, nodelist=order).toarray().astype(float)
    w, v = np.linalg.eigh(L)
    return np.clip(w, 0.0, None), v, list(order)


def hamiltonian_system(g: nx.Graph, order=None):
    """Dense H=-A eigensystem (P1 banked law, J=1)."""
    if order is None:
        order = sorted(g.nodes())
    H = -nx.to_numpy_array(g, nodelist=order, dtype=float)
    w, v = np.linalg.eigh(H)
    return w, v, list(order)


def save_system(path: str, evals: np.ndarray, evecs: np.ndarray, order) -> None:
    """Cache an eigensystem to npz (beast-side artifact, never committed)."""
    np.savez_compressed(path, evals=np.asarray(evals), evecs=np.asarray(evecs),
                        order=np.asarray(order))


def load_system(path: str):
    """Load a cached eigensystem (evals, evecs, order)."""
    z = np.load(path, allow_pickle=True)
    return np.asarray(z["evals"]), np.asarray(z["evecs"]), list(z["order"])


def heat_trace_ds(evals, ts=DS_TS) -> dict:
    """Spectral dimension from mean return Pbar(t) ~ t^{-d/2}."""
    w = np.clip(np.asarray(evals, dtype=float), 0.0, None)
    ts = np.asarray(list(ts), dtype=float)
    P = np.array([float(np.mean(np.exp(-w * t))) for t in ts])
    fit = fit_loglog(ts, P)
    return {"d": -2.0 * fit["p"] if fit["n"] >= 3 else float("nan"),
            "r2": fit["r2"], "n": fit["n"], "ok": bool(fit["n"] >= 3)}


def origin_return_ds(evals, evecs, origin_idx: int, ts=DS_TS) -> dict:
    """Per-origin spectral dimension from P_ii(t) (same frozen window)."""
    w = np.clip(np.asarray(evals, dtype=float), 0.0, None)
    Phi = np.asarray(evecs, dtype=float)
    ts = np.asarray(list(ts), dtype=float)
    phi2 = Phi[int(origin_idx), :] ** 2
    P = np.array([float(np.sum(phi2 * np.exp(-w * t))) for t in ts])
    fit = fit_loglog(ts, P)
    return {"d": -2.0 * fit["p"] if fit["n"] >= 3 else float("nan"),
            "r2": fit["r2"], "n": fit["n"], "ok": bool(fit["n"] >= 3)}


def weyl_ds(evals_ascending, lo_frac=WEYL_LO_FRAC, hi_frac=WEYL_HI_FRAC) -> dict:
    """Weyl counting-fit d_s (SECONDARY, frozen rule; banked spectral leg)."""
    w = np.asarray(evals_ascending, dtype=float)[1:]
    n = len(w)
    lo, hi = int(n * lo_frac), int(n * hi_frac)
    bad = {"d": float("nan"), "n": 0, "ok": False}
    if not 0 < lo < hi <= n:
        return bad
    if np.any(w[lo:hi] <= 0):
        return bad
    x = np.log(w[lo:hi])
    y = np.log(np.arange(lo + 1, hi + 1, dtype=float))
    slope, _ = np.polyfit(x, y, 1)
    return {"d": 2.0 * float(slope), "n": int(hi - lo), "ok": True}


def _target_traces_diff(evals, evecs, origin_idx, target_idx, ts, deg=None,
                      chunk=512):
    """Occupation-probability traces p_j(t) for the unbiased walk.

    Exact e^{-t Lrw} via Lsym conjugation: p(t) = D^{-1/2} Phi e^{-Lt}
    Phi^T D^{1/2} delta_i (regular graphs, deg=None: == Lsym evolution).
    Returns (T, Nt) array, T = len(ts).
    """
    w = np.clip(np.asarray(evals, dtype=float), 0.0, None)
    Phi = np.asarray(evecs, dtype=float)
    o = int(origin_idx)
    tj = np.asarray(list(target_idx), dtype=int)
    ts = np.asarray(list(ts), dtype=float)
    c = Phi[o, :]
    if deg is not None:
        deg = np.asarray(list(deg), dtype=float)
        c = c * math.sqrt(max(float(deg[o]), 1e-300))
    out = np.zeros((len(ts), len(tj)))
    Phit = Phi[np.ix_(tj, np.arange(Phi.shape[1]))]
    for a in range(0, len(ts), chunk):
        seg = ts[a:a + chunk]
        W = c[:, None] * np.exp(-w[:, None] * seg[None, :])
        P = Phit @ W
        if deg is not None:
            P = P / np.sqrt(np.maximum(deg[tj], 1e-300))[:, None]
        out[a:a + chunk, :] = P.T
    return out


def _target_traces_wave(evals, evecs, origin_idx, target_idx, ts, chunk=512):
    """Onsite-probability traces |psi_j(t)|^2 for H=-A delta launch."""
    E = np.asarray(evals, dtype=float)
    Phi = np.asarray(evecs, dtype=float)
    o = int(origin_idx)
    tj = np.asarray(list(target_idx), dtype=int)
    ts = np.asarray(list(ts), dtype=float)
    c = Phi[o, :]
    Phit = Phi[np.ix_(tj, np.arange(Phi.shape[1]))]
    out = np.zeros((len(ts), len(tj)))
    for a in range(0, len(ts), chunk):
        seg = ts[a:a + chunk]
        W = c[:, None] * np.exp(-1j * E[:, None] * seg[None, :])
        Psi = Phit @ W
        out[a:a + chunk, :] = (np.abs(Psi) ** 2).T
    return out


def diffusion_grid(D: int):
    """Frozen diffusion time grid (dt=0.25, Tmax=3(D/2)^2)."""
    tmax = 3.0 * (float(D) / 2.0) ** 2
    n = int(round(tmax / DT_DIFF))
    return np.arange(n + 1, dtype=float) * DT_DIFF


def wave_grid(D: int):
    """Frozen wave time grid (dt=0.05, Tmax=D)."""
    n = int(round(float(D) / DT_WAVE))
    return np.arange(n + 1, dtype=float) * DT_WAVE


def cfd_first_peak(trace, ts, frac=CFD_FRAC):
    """CFD arrival: first local max with height >= frac * global max.

    Returns float time, or None if no qualifying peak (missing tau).
    """
    p = np.asarray(list(trace), dtype=float)
    ts = np.asarray(list(ts), dtype=float)
    if len(p) < 3 or len(p) != len(ts):
        return None
    gmax = float(np.max(p[1:]))
    if not np.isfinite(gmax) or gmax <= 0:
        return None
    thr = frac * gmax
    for m in range(1, len(p) - 1):
        if p[m] >= p[m - 1] and p[m] > p[m + 1] and p[m] >= thr:
            return float(ts[m])
    # No interior qualifying peak: endpoint maxima are NOT peaks (a
    # monotonic rise means the peak lies beyond Tmax -> missing tau).
    return None


def arrival_times_diff(evals, evecs, origin_idx, target_idx, D: int,
                     deg=None) -> dict:
    """tau_D per target index (None = missing)."""
    ts = diffusion_grid(D)
    P = _target_traces_diff(evals, evecs, origin_idx, target_idx, ts, deg=deg)
    return {int(j): cfd_first_peak(P[:, k], ts)
            for k, j in enumerate(target_idx)}


def arrival_times_wave(evals, evecs, origin_idx, target_idx, D: int) -> dict:
    """tau_W per target index (None = missing)."""
    ts = wave_grid(D)
    P = _target_traces_wave(evals, evecs, origin_idx, target_idx, ts)
    return {int(j): cfd_first_peak(P[:, k], ts)
            for k, j in enumerate(target_idx)}


def sample_origins(n_nodes: int, si: int, L: int, n: int = N_ORIGINS,
                   base: int = ORIGIN_SEED_BASE) -> list:
    """Frozen origin sample: rng(base+100*si+L).integers(n_nodes)."""
    rng = np.random.default_rng(base + 100 * int(si) + int(L))
    return [int(v) for v in rng.integers(0, n_nodes, size=n)]


def tercile_bounds(D: int):
    """Equal-width R_G tercile cut points (a, b) over [1, D/2)."""
    half = float(D) / 2.0
    a = 1.0 + (half - 1.0) / 3.0
    b = 1.0 + 2.0 * (half - 1.0) / 3.0
    return (a, b)


def tercile_of(r: float, D: int) -> int:
    """Tercile index 0/1/2 for graph distance r (wrap-safe only)."""
    a, b = tercile_bounds(D)
    if r < a:
        return 0
    if r < b:
        return 1
    return 2


def sample_targets(dist: dict, D: int, per_tercile: int = PER_TERCILE,
                   seed: int = 0) -> dict:
    """Frozen target sample: per-tercile uniform over wrap-safe nodes.

    Returns {node: R_G}. Nodes at R=0 or R >= D/2 excluded.
    """
    rng = np.random.default_rng(int(seed))
    half = float(D) / 2.0
    bins = {0: [], 1: [], 2: []}
    for v, r in dist.items():
        if 1 <= r < half:
            bins[tercile_of(r, D)].append(v)
    out = {}
    for t in (0, 1, 2):
        pool = sorted(bins[t])
        if not pool:
            continue
        take = rng.choice(pool, size=min(per_tercile, len(pool)), replace=False)
        for v in take:
            out[v] = dist[v]
    return out


def fit_affine(x, y) -> dict:
    """OLS y = a*x + b ({a, b, r2, n}; NaN if n < 3)."""
    x = np.asarray(list(x), dtype=float)
    y = np.asarray(list(y), dtype=float)
    bad = {"a": float("nan"), "b": float("nan"), "r2": float("nan"), "n": 0}
    m = np.isfinite(x) & np.isfinite(y)
    if int(m.sum()) < 3:
        return bad
    a, b = np.polyfit(x[m], y[m], 1)
    pred = a * x[m] + b
    denom = float(np.sum((y[m] - y[m].mean()) ** 2))
    r2 = 1.0 - float(np.sum((y[m] - pred) ** 2)) / denom if denom > 0 else float("nan")
    return {"a": float(a), "b": float(b), "r2": float(r2), "n": int(m.sum())}


def fit_powerlaw(x, y) -> dict:
    """OLS log-log y = A*x^p ({A, p, r2, n}; NaN if n < 3)."""
    x = np.asarray(list(x), dtype=float)
    y = np.asarray(list(y), dtype=float)
    bad = {"A": float("nan"), "p": float("nan"), "r2": float("nan"), "n": 0}
    m = np.isfinite(x) & np.isfinite(y) & (x > 0) & (y > 0)
    if int(m.sum()) < 3:
        return bad
    fit = fit_loglog(x[m], y[m])
    if fit["n"] < 3:
        return bad
    return {"A": float(math.exp(fit["intercept"])), "p": fit["p"],
            "r2": fit["r2"], "n": fit["n"]}


def invert_powerlaw(tau, A: float, p: float):
    """Invert tau = A*R^p to Rhat (None-safe; None if A,p invalid)."""
    if tau is None or not np.isfinite(tau) or tau <= 0:
        return None
    if not np.isfinite(A) or not np.isfinite(p) or A <= 0 or p == 0:
        return None
    return float((float(tau) / A) ** (1.0 / p))


def delta_stat(rhat, r_true, floor: float = R_FLOOR):
    """Normalized concordance residual |Rhat-R|/max(R, floor) (None-safe)."""
    if rhat is None or r_true is None:
        return None
    if not np.isfinite(rhat) or not np.isfinite(r_true):
        return None
    return float(abs(float(rhat) - float(r_true)) / max(float(r_true), floor))


def tercile_medians(deltas: list, terciles: list) -> dict:
    """Median delta per tercile ({0,1,2} -> median or NaN)."""
    out = {}
    for t in (0, 1, 2):
        vals = [d for d, q in zip(deltas, terciles)
                if q == t and d is not None and np.isfinite(d)]
        out[t] = float(np.median(vals)) if vals else float("nan")
    out["n"] = int(sum(1 for d in deltas if d is not None and np.isfinite(d)))
    return out


def arrival_volume_dim(taus: dict, a: float, b: float, D: int,
                       lo_R: int = D_H_LO) -> dict:
    """Wave dimension from arrival-volume A(T) over the train-law window.

    taus maps node -> tau_W (None allowed); window T in [a*lo_R+b,
    a*(D/2-1)+b]. Returns {d, r2, n, window, ok}.
    """
    bad = {"d": float("nan"), "r2": float("nan"), "n": 0, "window": None,
           "ok": False}
    if not np.isfinite(a) or not np.isfinite(b) or a <= 0:
        return bad
    hi_R = int(math.floor(float(D) / 2.0)) - 1
    if hi_R <= lo_R:
        return bad
    t_lo, t_hi = a * lo_R + b, a * hi_R + b
    if not t_hi > t_lo > 0:
        return bad
    vals = np.array([t for t in taus.values()
                     if t is not None and np.isfinite(t)], dtype=float)
    if len(vals) < 3:
        return bad
    grid = np.linspace(t_lo, t_hi, 40)
    vols = np.array([float(np.sum(vals <= T)) for T in grid])
    m = vols >= 2
    if int(m.sum()) < 3:
        return bad
    fit = fit_loglog(grid[m], vols[m])
    if fit["n"] < 3:
        return bad
    return {"d": fit["p"], "r2": fit["r2"], "n": fit["n"],
            "window": (float(t_lo), float(t_hi)), "ok": True}


# ---------------------------------------------------------------------------
# VALIDATION-ONLY helpers (ground-truth grouping for OBS-0H test-set
# construction; NEVER called by rulers -- C2-audited).
# ---------------------------------------------------------------------------

def sheet_of(node, coords3: dict):
    """VALIDATION-ONLY: sheet bit b from background J2 (x, y, b) coords."""
    return int(coords3[node][2])


def sheet_split(origin, dist: dict, coords3: dict):
    """VALIDATION-ONLY: {R: {'same': [nodes], 'cross': [nodes]}} by sheet."""
    b0 = sheet_of(origin, coords3)
    out = {}
    for v, r in dist.items():
        if v == origin:
            continue
        slot = out.setdefault(int(r), {"same": [], "cross": []})
        slot["same" if sheet_of(v, coords3) == b0 else "cross"].append(v)
    return out


def sheet_contrast(same_vals: list, cross_vals: list):
    """VALIDATION-ONLY: |med_same - med_cross| / pooled_med (None-safe)."""
    s = np.array([v for v in same_vals if v is not None and np.isfinite(v)],
                 dtype=float)
    c = np.array([v for v in cross_vals if v is not None and np.isfinite(v)],
                 dtype=float)
    if len(s) == 0 or len(c) == 0:
        return None
    pooled = float(np.median(np.concatenate([s, c])))
    if pooled <= 0:
        return None
    return float(abs(float(np.median(s)) - float(np.median(c))) / pooled)


# ---------------------------------------------------------------------------
# C5 wave-regression helpers (apparatus check; coordinates allowed here).
# Ported conventions from P1 ballistic.py (H=-A, Gaussian packets, COM fits).
# ---------------------------------------------------------------------------

def c5_min_image_disp(r, r0, periods):
    """Minimal-image displacement (C5 readout only)."""
    d = np.asarray(r, dtype=float) - np.asarray(r0, dtype=float)
    if periods is not None:
        for ax, L in enumerate(periods):
            if L is not None:
                d[..., ax] -= np.round(d[..., ax] / L) * L
    return d


def c5_gaussian_packet(coords: dict, order: list, r0, k, sigma: float,
                       periods=None) -> np.ndarray:
    """Momentum Gaussian env*phase(k.d), normalized (C5 prep only)."""
    d = len(next(iter(coords.values())))
    r0v = np.asarray(r0, dtype=float).reshape(-1)
    kv = np.asarray(k, dtype=float).reshape(-1)
    pos = np.array([coords[v] for v in order], dtype=float)
    disp = c5_min_image_disp(pos, r0v, periods)
    env = np.exp(-np.sum(disp * disp, axis=1) / (4.0 * sigma * sigma))
    psi = env * np.exp(1.0j * (disp @ kv))
    return psi / np.linalg.norm(psi)


def c5_com(psi: np.ndarray, coords: dict, order: list, periods=None) -> np.ndarray:
    """Probability COM, circular mean on periodic axes (C5 readout only)."""
    d = len(next(iter(coords.values())))
    pos = np.array([coords[v] for v in order], dtype=float)
    w = np.abs(np.asarray(psi, dtype=np.complex128)) ** 2
    w = w / w.sum()
    out = np.zeros(d)
    for ax in range(d):
        L = periods[ax] if periods is not None else None
        if L is None:
            out[ax] = float(w @ pos[:, ax])
        else:
            ang = 2.0 * math.pi * pos[:, ax] / L
            z = np.sum(w * np.exp(1.0j * ang))
            out[ax] = (float(np.angle(z)) / (2.0 * math.pi) * L) % L
    return out


def c5_unwrap_trace(rs: np.ndarray, periods) -> np.ndarray:
    """Unwrap circular-mean COM trace (C5 readout only)."""
    rs = np.asarray(rs, dtype=float)
    if periods is None:
        return rs.copy()
    out = rs.copy()
    for ax, L in enumerate(periods):
        if L is not None:
            out[:, ax] = (np.unwrap(rs[:, ax] * 2.0 * math.pi / L)
                          / (2.0 * math.pi) * L)
    return out


def c5_fit_speed(rs: np.ndarray, ts: np.ndarray) -> dict:
    """Least-squares COM velocity + displacement-norm r2 (C5 readout only)."""
    rs = np.asarray(rs, dtype=float)
    ts = np.asarray(ts, dtype=float)
    v = np.array([np.polyfit(ts, rs[:, ax], 1)[0] for ax in range(rs.shape[1])])
    dd = np.linalg.norm(rs - rs[0], axis=1)
    slope, icept = np.polyfit(ts, dd, 1)
    ss_res = float(np.sum((dd - (slope * ts + icept)) ** 2))
    ss_tot = float(np.sum((dd - dd.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return {"v": v, "speed": float(np.linalg.norm(v)), "r2": float(r2)}


def c5_evolve_packet(evals, evecs, psi0: np.ndarray, dt: float,
                     n_steps: int) -> np.ndarray:
    """Eigen-exact packet evolution rows (n_steps+1, N) incl. psi0 (C5)."""
    E = np.asarray(evals, dtype=float)
    Phi = np.asarray(evecs, dtype=float)
    c = Phi.T @ np.asarray(psi0, dtype=np.complex128)
    rows = [np.asarray(psi0, dtype=np.complex128)]
    for s in range(1, n_steps + 1):
        rows.append(Phi @ (c * np.exp(-1j * E * (s * dt))))
    return np.array(rows)


def c5_branch_projectors(h_dense: np.ndarray, tol: float = 1e-9) -> dict:
    """Spectral E-sign branch projectors (C5 J2 prep; P1 convention)."""
    hd = np.asarray(h_dense, dtype=float)
    w, v = np.linalg.eigh(hd)
    vp, vm = v[:, w > tol], v[:, w < -tol]
    return {"P_plus": vp @ vp.T, "P_minus": vm @ vm.T,
            "n_zero": int(np.sum(np.abs(w) <= tol)), "evals": w}


def c5_branch_purify(psi: np.ndarray, p: np.ndarray):
    """Project psi onto branch (renormalized) + retained weight (C5 prep)."""
    psi = np.asarray(psi, dtype=np.complex128)
    q = np.asarray(p, dtype=float) @ psi
    retained = float(np.vdot(q, q).real)
    return q / np.linalg.norm(q), retained
