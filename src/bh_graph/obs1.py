"""OBS-1 blind observer reconstruction core (FROZEN per OBS1-PREREG).

BLINDNESS CONTRACT (C3-audited, pinned by tests): this module may consume
ONLY operational measurement records keyed by opaque station ids. It must
NEVER import substrate-construction / coordinate / path-length machinery.
Hidden geometry joins happen ONLY in the reveal module, run strictly after
blind artifacts are frozen + hashed.

Observer protocol (LOCKED in OBS1-PREREG):
  stations S0..S63 (opaque, shuffled), 3 sets per cell, 32/32 held-out.
  native channels: W = tau_W, D = sqrt(tau_D), P = -ln(phi) (s=1 known).
  symmetrize AFTER testing: D_ab = (M_ab + M_ba)/2.
  composite: median-normalize each channel (blind-safe), mean over
    available channels (equal frozen weights -- never tuned vs hidden).
"""

from __future__ import annotations

import numpy as np

# Frozen OBS1-PREREG constants.
N_STATIONS = 64
N_SETS = 3
STATION_SEED_BASE = 9100
N_TRAIN = 32
SYM_MED_BAR = 0.05
SYM_P90_BAR = 0.25
TRI_TOL = 0.05
TRI_FRAC_BAR = 0.05
TRI_FRAC_BAR_COMP = 0.15
VOL_Q_WINDOW = (0.25, 0.65)
VOL_R2_BAR = 0.85
DIM_STABLE_BAR = 0.5
DIM_TRAIN_TEST_BAR = 0.5
STRESS_BAR = 0.10  # absolute bar for LOCAL balls only (near-planar)
LINEAR_FLOOR = 0.01  # d=1 raw stress at/under this => already linear
DISTORT_FRAC = 0.5  # majority-distortion rule (see select_dimension)
NN_TRIPLETS = 8  # local-triplet neighbor count (frozen)
MDS_DIMS = (1, 2, 3, 4)
QUOTIENT_D_TOL = 0.5
EPS_HIDDEN_BAR = 0.30
LOCAL_ALIGN_BAR = 0.30
DIST_MATCH_BAR = 0.30
LOCALITY_FRAC_BAR = 0.70
SHEET_BLIND_BAR = 0.05
ANGLE_CONS_BAR = 0.20
TOPO_PREC_BAR = 0.50
TOPO_MIN_COUNT = 3
CROSS_RMS_BAR = 0.30
CROSS_D_BAR = 0.5
COMPOSITE_COMPLETE_BAR = 0.98
EMBED_COMPLETE_BAR = 0.95
LOCAL_Q_GRID = (0.10, 0.20, 0.30, 0.40)
ADJ_Q_THRESH = 0.10
IMPUTE_FACTOR = 1.5  # missing -> 1.5x channel max (frozen, recorded)
P_PHI_LO = 1e-300
P_PHI_HI = 1.0  # bulk phi clipped (source self-response s=1)
PROBES = ("W", "D", "P")


def _station_index(sid: str, n: int) -> int:
    """Opaque station id 'S{k}' -> index (schema-audited, C3)."""
    if not sid.startswith("S"):
        raise ValueError(f"non-opaque station id: {sid!r}")
    i = int(sid[1:])
    if not 0 <= i < n:
        raise ValueError(f"station id out of range: {sid!r}")
    return i


def native_matrices(pairs: dict, n: int = N_STATIONS) -> dict:
    """FROZEN native channels from directed operational pair records.

    pairs: {"Sa|Sb": {"W": tauW|None, "D": tauD|None, "P": phi|None}}.
    Returns {"W","D","P"} directed matrices (nan = missing) + meta.
    Native transforms (LOCKED): W = tau_W; D = sqrt(tau_D);
    P = -ln(clip(phi, 1e-300, 1.0)). Each matrix reads ONLY its own
    channel key (C4-structural: other channels may be absent/garbage).
    Diagonal is nan (self-pairs unmeasured; set to 0 by symmetrize).
    """
    out = {ch: np.full((n, n), np.nan) for ch in PROBES}
    n_clamp, n_phi = 0, 0
    for key, rec in pairs.items():
        a_s, b_s = key.split("|")
        a, b = _station_index(a_s, n), _station_index(b_s, n)
        if a == b:
            continue
        w = rec.get("W", None)
        if w is not None and np.isfinite(w):
            out["W"][a, b] = float(w)
        d = rec.get("D", None)
        if d is not None and np.isfinite(d) and d >= 0:
            out["D"][a, b] = float(np.sqrt(d))
        p = rec.get("P", None)
        if p is not None and np.isfinite(p) and p > 0:
            n_phi += 1
            if p > P_PHI_HI:
                n_clamp += 1
            out["P"][a, b] = float(-np.log(min(max(p, P_PHI_LO),
                                                 P_PHI_HI)))
    return {"W": out["W"], "D": out["D"], "P": out["P"],
            "meta": {"P_clamp_frac": n_clamp / n_phi if n_phi else 0.0}}


def complete_matrix(M: np.ndarray) -> dict:
    """Symmetrize + frozen imputation (missing -> 1.5x max).

    Returns {"D", "measured_frac", "n_imputed"}. Diagonal exactly 0.
    All blind estimators run on the completed matrix (frozen).
    """
    S = symmetrize(np.asarray(M, dtype=float))
    n = S.shape[0]
    off = ~np.eye(n, dtype=bool)
    meas = np.isfinite(S) & off
    frac = float(meas.sum() / off.sum())
    mx = float(np.max(S[meas])) if meas.sum() else float("nan")
    D = S.copy()
    if np.isfinite(mx):
        D[off & ~np.isfinite(S)] = IMPUTE_FACTOR * mx
    return {"D": D, "measured_frac": frac,
            "n_imputed": int((off & ~np.isfinite(S)).sum() // 2
                             if np.isfinite(mx) else 0)}


def symmetrize(M: np.ndarray) -> np.ndarray:
    """Symmetrized matrix (M + M.T)/2 with exact-zero diagonal (None=nan)."""
    M = np.asarray(M, dtype=float)
    S = (M + M.T) / 2.0
    np.fill_diagonal(S, 0.0)
    return S


def symmetry_report(M: np.ndarray) -> dict:
    """Relative asymmetry |M_ab-M_ba|/mean over off-diagonal measured pairs."""
    M = np.asarray(M, dtype=float)
    n = M.shape[0]
    vals = []
    for a in range(n):
        for b in range(a + 1, n):
            x, y = M[a, b], M[b, a]
            if np.isfinite(x) and np.isfinite(y) and (x + y) > 0:
                vals.append(abs(x - y) / ((x + y) / 2.0))
    vals = np.array(vals)
    if len(vals) == 0:
        return {"med": float("nan"), "p90": float("nan"), "n": 0,
                "pass": False}
    med = float(np.median(vals))
    p90 = float(np.percentile(vals, 90))
    return {"med": med, "p90": p90, "n": int(len(vals)),
            "pass": bool(med < SYM_MED_BAR and p90 < SYM_P90_BAR)}


def triangle_report(D: np.ndarray) -> dict:
    """Triangle-violation distribution over measured triplets.

    Violation ratio for the largest side c: (c-a-b)/c. TRI-OK (strict,
    single-channel bar) iff the fraction exceeding TRI_TOL is below
    TRI_FRAC_BAR. pass_loose (composite bar, filed from pilot instrument
    physics: arrival channels carry O(1) dispersion/interference
    non-metricity while the static channel is exactly metric, so the
    mixed composite is gated as near-metric) iff below TRI_FRAC_BAR_COMP.
    """
    D = np.asarray(D, dtype=float)
    n = D.shape[0]
    rats = []
    for a in range(n):
        for b in range(a + 1, n):
            for c in range(b + 1, n):
                x, y, z = D[a, b], D[b, c], D[a, c]
                if not (np.isfinite(x) and np.isfinite(y) and np.isfinite(z)):
                    continue
                if min(x, y, z) <= 0:
                    continue
                s = sorted([x, y, z])
                rats.append(max(0.0, (s[2] - s[0] - s[1]) / s[2]))
    rats = np.array(rats)
    if len(rats) == 0:
        return {"frac": float("nan"), "p99": float("nan"), "n": 0,
                "pass": False, "pass_loose": False}
    frac = float(np.mean(rats > TRI_TOL))
    return {"frac": frac, "p99": float(np.percentile(rats, 99)),
            "n": int(len(rats)), "pass": bool(frac < TRI_FRAC_BAR),
            "pass_loose": bool(frac < TRI_FRAC_BAR_COMP)}


def median_normalize(D: np.ndarray) -> np.ndarray:
    """Scale by the off-diagonal median (blind-safe; nan-safe)."""
    D = np.asarray(D, dtype=float)
    m = D[~np.eye(D.shape[0], dtype=bool)]
    med = float(np.median(m[np.isfinite(m)]))
    if not med > 0:
        return np.full_like(D, np.nan)
    return D / med


def composite_matrix(channels: dict) -> np.ndarray:
    """Equal-weight mean of median-normalized channels over available data."""
    mats = [median_normalize(np.asarray(M, dtype=float))
            for M in channels.values()]
    stack = np.stack(mats, axis=0)
    with np.errstate(invalid="ignore"):
        out = np.nanmean(stack, axis=0)
    np.fill_diagonal(out, 0.0)
    return out


def completeness(D: np.ndarray) -> float:
    """Fraction of off-diagonal pairs measured (finite)."""
    D = np.asarray(D, dtype=float)
    m = D[~np.eye(D.shape[0], dtype=bool)]
    return float(np.mean(np.isfinite(m))) if m.size else 0.0


def volume_dimension(D: np.ndarray, origins=None) -> dict:
    """Operational volume growth V(R) ~ R^d over the frozen quantile window.

    Window = [q25, q65] of the pooled pairwise distribution (blind-safe,
    data-adaptive). Per-origin log-log OLS; median over origins.
    """
    D = np.asarray(D, dtype=float)
    n = D.shape[0]
    pool = D[~np.eye(n, dtype=bool)]
    pool = pool[np.isfinite(pool) & (pool > 0)]
    if len(pool) < 20:
        return {"d": float("nan"), "r2": float("nan"), "n": 0, "ok": False}
    lo, hi = np.quantile(pool, list(VOL_Q_WINDOW))
    grid = np.linspace(lo, hi, 12)
    ds, r2s = [], []
    for a in origins if origins is not None else range(n):
        row = D[a]
        row = row[np.isfinite(row)]
        if len(row) < 10:
            continue
        V = np.array([float(np.sum(row <= R)) for R in grid])
        m = V >= 2
        if int(m.sum()) < 3:
            continue
        lx, ly = np.log(grid[m]), np.log(V[m])
        p, _ = np.polyfit(lx, ly, 1)
        pred = p * lx + np.mean(ly - p * lx)
        denom = float(np.sum((ly - ly.mean()) ** 2))
        r2 = 1.0 - float(np.sum((ly - pred) ** 2)) / denom if denom > 0 else \
            float("nan")
        ds.append(float(p))
        r2s.append(float(r2))
    if not ds:
        return {"d": float("nan"), "r2": float("nan"), "n": 0, "ok": False}
    r2m = float(np.median(np.array(r2s)[np.isfinite(r2s)]))
    return {"d": float(np.median(ds)), "r2": r2m, "n": len(ds),
            "ok": bool(np.isfinite(r2m) and r2m >= VOL_R2_BAR)}


def classical_mds(D: np.ndarray, d: int) -> dict:
    """Deterministic classical (Torgerson) MDS into R^d.

    Returns coords (n,d), spectrum (desc), neg-mass fraction.
    """
    D = np.asarray(D, dtype=float)
    n = D.shape[0]
    if not np.all(np.isfinite(D)):
        return {"coords": None, "evals": None, "negmass": float("nan"),
                "ok": False}
    D2 = D ** 2
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ D2 @ J
    w, V = np.linalg.eigh(B)
    order = np.argsort(w)[::-1]
    w, V = w[order], V[:, order]
    pos = np.clip(w[:d], 0.0, None)
    coords = V[:, :d] * np.sqrt(pos)[None, :]
    tot = float(np.sum(np.abs(w)))
    neg = float(np.sum(np.abs(w[w < 0]))) / tot if tot > 0 else 0.0
    return {"coords": coords, "evals": w, "negmass": neg, "ok": True}


def stress_normalized(D: np.ndarray, X: np.ndarray, pairs=None) -> float:
    """Normalized raw stress over given pairs (default: all off-diagonal)."""
    D = np.asarray(D, dtype=float)
    X = np.asarray(X, dtype=float)
    n = D.shape[0]
    if pairs is None:
        pairs = [(a, b) for a in range(n) for b in range(a + 1, n)]
    num, den = 0.0, 0.0
    for a, b in pairs:
        if not np.isfinite(D[a, b]):
            continue
        dhat = float(np.linalg.norm(X[a] - X[b]))
        num += (D[a, b] - dhat) ** 2
        den += D[a, b] ** 2
    return float(num / den) if den > 0 else float("nan")


def select_dimension(stress_by_d: dict) -> dict:
    """Frozen complexity-vs-error rule (majority-distortion).

    d*=1 if the d=1 stress is at/under LINEAR_FLOOR (already linear);
    else the smallest d with stress_d <= DISTORT_FRAC * stress_1 (the
    first dimension removing a majority of the linear distortion);
    else argmin with pass=False (no good low-d embedding). Absolute
    raw-stress bars are NOT used globally: periodic wrap distortion keeps
    even ideal 2D periodic data above any conventional cutoff (synthetic
    calibration, filed pre-data).
    """
    ds = sorted(stress_by_d)
    s1 = stress_by_d[ds[0]]
    if np.isfinite(s1) and s1 <= LINEAR_FLOOR:
        return {"dstar": int(ds[0]), "stress": float(s1), "pass": True}
    if np.isfinite(s1) and s1 > 0:
        for d in ds[1:]:
            s = stress_by_d[d]
            if np.isfinite(s) and s <= DISTORT_FRAC * s1:
                return {"dstar": int(d), "stress": float(s), "pass": True}
    best = min(ds, key=lambda d: (not np.isfinite(stress_by_d[d]),
                                  stress_by_d[d]))
    return {"dstar": int(best), "stress": float(stress_by_d[best]),
            "pass": False}


def train_test_pairs(n: int, n_train: int = N_TRAIN):
    """Frozen held-out split: stations [0,n_train) train, rest test."""
    train = [(a, b) for a in range(n_train) for b in range(a + 1, n_train)]
    test = [(a, b) for a in range(n) for b in range(a + 1, n)
            if a >= n_train or b >= n_train]
    return train, test


def adjacency_operational(D: np.ndarray) -> np.ndarray:
    """Observer adjacency: pairs below the bottom-decile threshold (frozen)."""
    D = np.asarray(D, dtype=float)
    n = D.shape[0]
    pool = D[~np.eye(n, dtype=bool)]
    pool = pool[np.isfinite(pool)]
    if len(pool) == 0:
        return np.zeros((n, n), dtype=bool)
    thr = float(np.quantile(pool, ADJ_Q_THRESH))
    A = (D <= thr) & np.isfinite(D)
    np.fill_diagonal(A, False)
    return A


def law_of_cosines_angles(D: np.ndarray, triplets) -> list:
    """Angle at a for triplets (a,b,c) via the cosine rule (nan-safe)."""
    D = np.asarray(D, dtype=float)
    out = []
    for a, b, c in triplets:
        x, y, z = D[a, b], D[a, c], D[b, c]
        if not all(np.isfinite(v) and v > 0 for v in (x, y, z)):
            out.append(float("nan"))
            continue
        cosang = (x * x + y * y - z * z) / (2.0 * x * y)
        out.append(float(np.arccos(np.clip(cosang, -1.0, 1.0))))
    return out


def coord_angles(X: np.ndarray, triplets) -> list:
    """Euclidean angle at a for triplets from embedding coords (nan-safe)."""
    X = np.asarray(X, dtype=float)
    out = []
    for a, b, c in triplets:
        u, v = X[b] - X[a], X[c] - X[a]
        nu, nv = float(np.linalg.norm(u)), float(np.linalg.norm(v))
        if not (nu > 0 and nv > 0):
            out.append(float("nan"))
            continue
        out.append(float(np.arccos(np.clip(u @ v / (nu * nv), -1.0, 1.0))))
    return out


def triangle_angle_sums(D: np.ndarray, triplets) -> list:
    """Sum of the three cosine-rule angles per triplet (nan-safe).

    Pure distance geometry (no embedding): flat-local triangles sum to pi.
    """
    D = np.asarray(D, dtype=float)
    out = []
    for a, b, c in triplets:
        x, y, z = D[b, c], D[a, c], D[a, b]
        if not all(np.isfinite(v) and v > 0 for v in (x, y, z)):
            out.append(float("nan"))
            continue
        angs = []
        for opp, s1, s2 in ((x, y, z), (y, x, z), (z, x, y)):
            cosang = (s1 * s1 + s2 * s2 - opp * opp) / (2.0 * s1 * s2)
            angs.append(float(np.arccos(np.clip(cosang, -1.0, 1.0))))
        out.append(float(sum(angs)))
    return out


def local_triplets(D: np.ndarray, k: int = NN_TRIPLETS):
    """Genuinely local triplets: pairs among each station's k nearest.

    Scale-adaptive and blind-safe (fixed k, no tuned radius). Quartile
    cutoffs are NOT local on broad periodic distributions (synthetic
    calibration, filed pre-data). Deduped by sorted index tuple.
    """
    D = np.asarray(D, dtype=float)
    n = D.shape[0]
    seen, out = set(), []
    for a in range(n):
        row = D[a]
        order = [b for b in np.argsort(np.where(np.isfinite(row), row,
                                                np.inf))
                 if b != a and np.isfinite(row[b])][:k]
        for i in range(len(order)):
            for j in range(i + 1, len(order)):
                key = tuple(sorted((a, order[i], order[j])))
                if key not in seen:
                    seen.add(key)
                    out.append(key)
    return out


def ball_angles(D: np.ndarray, a: int, nbrs: list) -> list:
    """|cosine-rule angle - local-MDS angle| at apex a over nbr pairs.

    The ball {a}+nbrs is MDS-embedded in 2D on its own (cut-free: only
    the ball's pairwise distances are seen). Purely local, blind-safe.
    """
    D = np.asarray(D, dtype=float)
    ball = [a] + [b for b in nbrs if b != a]
    r = classical_mds(D[np.ix_(ball, ball)], 2)
    if not r["ok"]:
        return []
    X = r["coords"]
    pos = {v: i for i, v in enumerate(ball)}
    out = []
    for i in range(len(nbrs)):
        for j in range(i + 1, len(nbrs)):
            b, c = nbrs[i], nbrs[j]
            x, y = D[a, b], D[a, c]
            z = D[b, c]
            if not all(np.isfinite(v) and v > 0 for v in (x, y, z)):
                continue
            t1 = float(np.arccos(np.clip(
                (x * x + y * y - z * z) / (2.0 * x * y), -1.0, 1.0)))
            u, v = X[pos[b]] - X[pos[a]], X[pos[c]] - X[pos[a]]
            nu, nv = float(np.linalg.norm(u)), float(np.linalg.norm(v))
            if not (nu > 0 and nv > 0):
                continue
            t2 = float(np.arccos(np.clip(u @ v / (nu * nv), -1.0, 1.0)))
            out.append(abs(t1 - t2))
    return out


def angle_consistency(D: np.ndarray, X=None) -> dict:
    """Median local |cosine-rule angle - local-embedding angle| (OBS-1F).

    Per station: pairs among its NN_TRIPLETS nearest neighbors, angles at
    the station from distances vs from the ball's own 2D MDS embedding.
    Tests whether locally inferred angles compose into Euclidean balls.
    X accepted-but-ignored (kept for call compatibility).
    """
    _ = X
    D = np.asarray(D, dtype=float)
    n = D.shape[0]
    diffs = []
    for a in range(n):
        row = D[a]
        nbrs = [b for b in np.argsort(np.where(np.isfinite(row), row,
                                               np.inf))
                if b != a and np.isfinite(row[b])][:NN_TRIPLETS]
        if len(nbrs) < 2:
            continue
        diffs.extend(ball_angles(D, a, nbrs))
    if not diffs:
        return {"med": float("nan"), "n": 0, "pass": False}
    med = float(np.median(diffs))
    return {"med": med, "n": len(diffs),
            "pass": bool(med < ANGLE_CONS_BAR)}


def local_euclideanity(D: np.ndarray, d: int = 2) -> dict:
    """2D-MDS stress on D-balls over the frozen quantile radius grid.

    Per origin and radius: stress of the induced submatrix. WINDOW-EXISTS
    iff >= 2 consecutive grid radii have median stress < STRESS_BAR.
    """
    D = np.asarray(D, dtype=float)
    n = D.shape[0]
    pool = D[~np.eye(n, dtype=bool)]
    pool = pool[np.isfinite(pool) & (pool > 0)]
    if len(pool) < 20:
        return {"profile": {}, "window": False}
    prof = {}
    for q in LOCAL_Q_GRID:
        R = float(np.quantile(pool, q))
        ss = []
        for a in range(n):
            sub = [a] + [b for b in range(n)
                         if b != a and np.isfinite(D[a, b]) and D[a, b] <= R]
            if len(sub) < d + 2:
                continue
            Dm = D[np.ix_(sub, sub)]
            r = classical_mds(Dm, d)
            if r["ok"]:
                ss.append(stress_normalized(Dm, r["coords"]))
        prof[q] = float(np.median(ss)) if ss else float("nan")
    qs = sorted(prof)
    win = any(np.isfinite(prof[qs[i]]) and prof[qs[i]] < STRESS_BAR
              and np.isfinite(prof[qs[i + 1]]) and prof[qs[i + 1]] < STRESS_BAR
              for i in range(len(qs) - 1))
    return {"profile": prof, "window": bool(win)}


def wrap_candidates(D: np.ndarray, X: np.ndarray) -> dict:
    """Pairs operationally near but embedding-far (blind topology flag).

    Near = bottom-10% D; far = top-25% embedding distance. Descriptive.
    """
    D = np.asarray(D, dtype=float)
    X = np.asarray(X, dtype=float)
    n = D.shape[0]
    pairs = [(a, b) for a in range(n) for b in range(a + 1, n)
             if np.isfinite(D[a, b])]
    if not pairs:
        return {"pairs": [], "n": 0}
    ds = np.array([D[a, b] for a, b in pairs])
    es = np.array([float(np.linalg.norm(X[a] - X[b])) for a, b in pairs])
    near = np.quantile(ds, 0.10)
    far = np.quantile(es, 0.75)
    out = [[a, b] for (a, b), dd, ee in zip(pairs, ds, es)
           if dd <= near and ee >= far]
    return {"pairs": out, "n": len(out)}


def procrustes_align(X: np.ndarray, Y: np.ndarray) -> dict:
    """Optimal translate/rotate/reflect/scale X -> Y (Procrustes, no warp).

    Returns aligned X, normalized RMS residual, scale, reflection flag.
    """
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    Xc = X - X.mean(axis=0)
    Yc = Y - Y.mean(axis=0)
    # Pad X with zero columns if fewer embedding dims than target.
    if Xc.shape[1] < Yc.shape[1]:
        Xc = np.pad(Xc, ((0, 0), (0, Yc.shape[1] - Xc.shape[1])))
    U, svals, Vt = np.linalg.svd(Xc.T @ Yc)
    R = U @ Vt
    num = float(np.sum(svals))
    den = float(np.sum(Xc ** 2))
    scale = num / den if den > 0 else 0.0
    Xa = (Xc @ R) * scale + Y.mean(axis=0)
    resid = float(np.sqrt(np.mean(np.sum((Xa - Y) ** 2, axis=1))))
    spread = float(np.sqrt(np.mean(np.sum(Yc ** 2, axis=1))))
    return {"aligned": Xa, "eps": resid / spread if spread > 0 else resid,
            "scale": float(scale),
            "reflection": bool(np.linalg.det(R) < 0)}


def cross_probe_rms(Da: np.ndarray, Db: np.ndarray) -> dict:
    """Scale-aligned relative RMS between two geometries (global scalar).

    Least-squares scale s minimizing ||s*Da - Db|| over common pairs.
    No nonlinear or pair-specific correction.
    """
    Da = np.asarray(Da, dtype=float)
    Db = np.asarray(Db, dtype=float)
    m = np.isfinite(Da) & np.isfinite(Db)
    np.fill_diagonal(m, False)
    x, y = Da[m], Db[m]
    if len(x) < 3 or float(x @ x) <= 0:
        return {"rms": float("nan"), "scale": float("nan"), "n": 0,
                "pass": False}
    s = float((x @ y) / (x @ x))
    rms = float(np.sqrt(np.mean((s * x - y) ** 2)) / np.sqrt(np.mean(y ** 2)))
    return {"rms": rms, "scale": s, "n": int(len(x)),
            "pass": bool(rms < CROSS_RMS_BAR)}
