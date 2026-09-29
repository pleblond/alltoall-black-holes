"""Outcome measurements for the blind annealer survey (prereg §7/§8/§9).

OUTCOMES ONLY: d_iso (shell-growth), mean edge-κ (P4), coordination z,
large-world stats, and the frozen §9 basin-membership bars. Nothing in this
module may be called from inside the anneal loop (cost/core audit tests
enforce the separation). Every number produced here carries label
"exploratory" downstream in results JSON.
"""
from __future__ import annotations

import networkx as nx
import numpy as np

N_DSEEDS = 20  # frozen BFS seeds per d_iso estimate (prereg §7)
KAPPA_MAX_EDGES = 150  # frozen κ edge sample per checkpoint (prereg §5)
N_DIST_SAMPLES = 2000  # frozen mean-distance pairs (prereg §8)

# Frozen basin-membership bars (prereg §9 B1–B4).
DISO_TARGET = 3.0
DISO_TOL = 0.75
DISO_R2_MIN = 0.75
KAPPA_ABS_MAX = 0.06
Z_MEAN_MAX = 8.0


def is_valid_measure_params(n_dseeds: int, max_edges: int) -> bool:
    """Boolean check: sane measurement params (no exceptions)."""
    return bool(
        isinstance(n_dseeds, (int, np.integer)) and n_dseeds >= 1
        and isinstance(max_edges, (int, np.integer)) and max_edges >= 1
    )


def _bfs_shell_profile(g: nx.Graph, source) -> tuple[np.ndarray, np.ndarray]:
    """(V(r), S(r)) for r = 1..ecc while V(r) <= N/2 (prereg §7)."""
    n = g.number_of_nodes()
    dist = nx.single_source_shortest_path_length(g, source)
    if len(dist) < 5:
        return np.array([]), np.array([])
    maxr = max(dist.values())
    shells = np.zeros(maxr + 1, dtype=float)
    for v, r in dist.items():
        shells[r] += 1.0
    vols: list[float] = []
    area: list[float] = []
    cum = shells[0]
    for r in range(1, maxr + 1):
        cum += shells[r]
        if cum > n / 2:
            break
        vols.append(cum)
        area.append(shells[r])
    return np.array(vols), np.array(area)


def _ols_loglog(x: np.ndarray, y: np.ndarray) -> dict:
    """OLS y = a x + b with slope SE and R² (nan-guarded, no raise)."""
    bad = {"a": float("nan"), "se_a": float("nan"), "r2": float("nan")}
    if len(x) < 4 or np.any(x <= 0) or np.any(y <= 0):
        return bad
    lx, ly = np.log(x), np.log(y)
    if not (np.all(np.isfinite(lx)) and np.all(np.isfinite(ly))):
        return bad
    try:
        coef, cov = np.polyfit(lx, ly, 1, cov=True)
    except Exception:
        return bad
    pred = coef[0] * lx + coef[1]
    denom = float(np.sum((ly - ly.mean()) ** 2))
    r2 = 1.0 - float(np.sum((ly - pred) ** 2)) / denom if denom > 0 else float("nan")
    return {"a": float(coef[0]),
            "se_a": float(np.sqrt(max(cov[0, 0], 0.0))),
            "r2": float(r2)}


def diso_estimate(g: nx.Graph, n_dseeds: int = N_DSEEDS,
                  seed: int = 0) -> dict:
    """d_iso via shell-growth S ~ V^((d-1)/d), median over BFS seeds.

    {d, err, r2, n_kept, n_tried, ok}. ok=False unless ≥ 8 kept seeds
    (prereg §7). Slope window a ∈ (−0.2, 0.95); d = 1/(1−a).
    """
    bad = {"d": float("nan"), "err": float("nan"), "r2": float("nan"),
           "n_kept": 0, "n_tried": int(n_dseeds), "ok": False}
    nodes = list(g.nodes())
    if len(nodes) < 8 or not is_valid_measure_params(n_dseeds, 1):
        return bad
    rng = np.random.default_rng(seed)
    picks = [nodes[int(rng.integers(len(nodes)))] for _ in range(n_dseeds)]
    ds: list[float] = []
    ses: list[float] = []
    r2s: list[float] = []
    for s in picks:
        vols, area = _bfs_shell_profile(g, s)
        if len(vols) < 4:
            continue
        fit = _ols_loglog(vols, area)
        a = fit["a"]
        if not np.isfinite(a) or not (-0.2 < a < 0.95):
            continue
        d = 1.0 / (1.0 - a)
        if not np.isfinite(d) or d <= 0:
            continue
        ds.append(d)
        # Propagate slope SE: dd/da = 1/(1−a)².
        se = fit["se_a"] / (1.0 - a) ** 2 if np.isfinite(fit["se_a"]) else np.nan
        ses.append(se)
        r2s.append(fit["r2"])
    if len(ds) < 8:
        out = dict(bad)
        out["n_kept"] = len(ds)
        return out
    arr = np.array(ds)
    sem = float(arr.std(ddof=1) / np.sqrt(len(arr))) if len(arr) > 1 else float("nan")
    med_se = float(np.nanmedian(ses)) if np.any(np.isfinite(ses)) else float("nan")
    err = float(np.nanmax([sem, med_se])) if np.any(np.isfinite([sem, med_se])) else float("nan")
    return {"d": float(np.median(arr)), "err": err,
            "r2": float(np.nanmedian(r2s)), "n_kept": len(ds),
            "n_tried": int(n_dseeds), "ok": True}


def kappa_sample_mean(g: nx.Graph, max_edges: int = KAPPA_MAX_EDGES,
                      seed: int = 0) -> dict:
    """Mean exact edge-κ (P4) over a uniform edge sample {mean, sem, n, ok}.

    Sparse-Johnson cached distances + exact LP per edge. ok=False (never
    imputed) when Johnson fails or the graph is disconnected (prereg §5).
    """
    bad = {"mean": float("nan"), "sem": float("nan"), "n": 0, "ok": False}
    if not is_valid_measure_params(1, max_edges):
        return bad
    try:
        if not nx.is_connected(g):
            return bad
        from bh_graph.orici import ollivier_curvature
        from bh_graph.sinkor import all_pairs_johnson

        dist, idx = all_pairs_johnson(g)
        if dist is None or idx is None or not np.all(np.isfinite(dist)):
            return bad
        edges = list(g.edges())
        if not edges:
            return bad
        rng = np.random.default_rng(seed)
        take = min(max_edges, len(edges))
        sel = [edges[int(i)] for i in
               rng.choice(len(edges), size=take, replace=False)]
        kaps = [float(ollivier_curvature(g, u, v, _dist=dist, _idx=idx))
                for u, v in sel]
        kaps = [k for k in kaps if np.isfinite(k)]
        if not kaps:
            return bad
        arr = np.array(kaps)
        sem = float(arr.std(ddof=1) / np.sqrt(len(arr))) if len(arr) > 1 else 0.0
        return {"mean": float(arr.mean()), "sem": sem, "n": len(arr),
                "ok": True}
    except Exception:
        return bad


def coordination(g: nx.Graph) -> dict[str, float]:
    """Mean/std coordination z (outcome; no target anywhere)."""
    deg = np.array([d for _, d in g.degree()], dtype=float)
    if len(deg) == 0:
        return {"z_mean": float("nan"), "z_std": float("nan")}
    return {"z_mean": float(deg.mean()), "z_std": float(deg.std())}


def large_world_stats(g: nx.Graph,
                      n_dist_samples: int = N_DIST_SAMPLES,
                      seed: int = 0) -> dict:
    """Large-world outcomes {diameter, mean_dist_sampled, n, ok}.

    Exact diameter + sampled mean pairwise distance. ok=False on
    disconnected graphs (diameter undefined there).
    """
    bad = {"diameter": -1, "mean_dist_sampled": float("nan"),
           "n_dist_samples": 0, "ok": False}
    try:
        if not nx.is_connected(g):
            return bad
        diam = int(nx.diameter(g))
        nodes = list(g.nodes())
        rng = np.random.default_rng(seed)
        dists: list[float] = []
        for _ in range(max(int(n_dist_samples), 1)):
            u = nodes[int(rng.integers(len(nodes)))]
            v = nodes[int(rng.integers(len(nodes)))]
            if u == v:
                continue
            dists.append(float(nx.shortest_path_length(g, u, v)))
        if not dists:
            return {"diameter": diam, "mean_dist_sampled": float("nan"),
                    "n_dist_samples": 0, "ok": True}
        return {"diameter": diam,
                "mean_dist_sampled": float(np.mean(dists)),
                "n_dist_samples": len(dists), "ok": True}
    except Exception:
        return bad


def lw_diameter_bar(n: int) -> float:
    """Frozen B4 bar: diameter ≥ 2·log2(N) (prereg §9)."""
    return float(2.0 * np.log2(max(int(n), 2)))


def basin_membership(diso: dict, kappa: dict, z_mean: float,
                     lw: dict, n: int) -> dict:
    """Frozen §9 B1–B4 bars on a final checkpoint. {B1..B4, member, margins}.

    Margins: signed distance past each bar in natural units (positive =
    passing with room). All inputs treated as exploratory.
    """
    try:
        b1 = bool(diso.get("ok") and abs(float(diso["d"]) - DISO_TARGET) <= DISO_TOL
                  and float(diso["r2"]) >= DISO_R2_MIN)
        m1 = float(DISO_TOL - abs(float(diso.get("d", np.nan)) - DISO_TARGET))
    except (TypeError, ValueError):
        b1, m1 = False, float("nan")
    try:
        b2 = bool(kappa.get("ok") and abs(float(kappa["mean"])) <= KAPPA_ABS_MAX)
        m2 = float(KAPPA_ABS_MAX - abs(float(kappa.get("mean", np.nan))))
    except (TypeError, ValueError):
        b2, m2 = False, float("nan")
    try:
        b3 = bool(np.isfinite(z_mean) and float(z_mean) <= Z_MEAN_MAX)
        m3 = float(Z_MEAN_MAX - float(z_mean))
    except (TypeError, ValueError):
        b3, m3 = False, float("nan")
    try:
        bar = lw_diameter_bar(n)
        b4 = bool(lw.get("ok") and float(lw["diameter"]) >= bar)
        m4 = float(float(lw.get("diameter", np.nan)) - bar)
    except (TypeError, ValueError):
        b4, m4 = False, float("nan")
    return {"B1_diso": b1, "B2_kappa": b2, "B3_sparse": b3, "B4_lw": b4,
            "member": bool(b1 and b2 and b3 and b4),
            "margins": {"B1": m1, "B2": m2, "B3": m3, "B4": m4}}


def measure_graph(g: nx.Graph, seed: int = 0,
                  n_dseeds: int = N_DSEEDS,
                  max_edges: int = KAPPA_MAX_EDGES,
                  n_dist_samples: int = N_DIST_SAMPLES) -> dict:
    """Full outcome bundle for one graph (runner checkpoints call this)."""
    n = g.number_of_nodes()
    diso = diso_estimate(g, n_dseeds=n_dseeds, seed=seed)
    kappa = kappa_sample_mean(g, max_edges=max_edges, seed=seed + 1)
    z = coordination(g)
    lw = large_world_stats(g, n_dist_samples=n_dist_samples, seed=seed + 2)
    return {"diso": diso, "kappa": kappa, "z": z, "lw": lw,
            "basin": basin_membership(diso, kappa, z["z_mean"], lw, n),
            "label": "exploratory"}


# ---------------------------------------------------------------------------
# Round-2 (V2): shell estimator with r_min + upper-V window, N-aware B4.
# ---------------------------------------------------------------------------

# Frozen V2 estimator geometry (round-2 prereg §7; selected on pristine
# controls only — see docs/ANNEAL2_REPORT.md estimator-dev appendix).
R_MIN_V2 = 2
F_UP_V2 = 0.5

# Re-frozen V2 basin bars (round-2 prereg §9; values re-derived, margins new).
DISO_TARGET_V2 = 3.0
DISO_TOL_V2 = 0.75
DISO_R2_MIN_V2 = 0.75
KAPPA_ABS_MAX_V2 = 0.06
Z_MEAN_MAX_V2 = 8.0
F_B4_V2 = 0.5  # B4: diameter >= F_B4 * (pristine open-cubic control diam at N)


def _bfs_shell_profile_v2(g: nx.Graph, source, r_min: int = R_MIN_V2,
                          f_up: float = F_UP_V2) -> tuple[np.ndarray, np.ndarray]:
    """(V(r), S(r)) for r_min <= r while V(r) <= f_up * N (V2 window)."""
    n = g.number_of_nodes()
    dist = nx.single_source_shortest_path_length(g, source)
    if len(dist) < 8:
        return np.array([]), np.array([])
    maxr = max(dist.values())
    shells = np.zeros(maxr + 1, dtype=float)
    for r in dist.values():
        shells[r] += 1.0
    vols: list[float] = []
    area: list[float] = []
    cum = float(shells[: max(int(r_min), 0)].sum())
    for r in range(max(int(r_min), 0), maxr + 1):
        cum += shells[r]
        if cum > float(f_up) * n:
            break
        vols.append(cum)
        area.append(shells[r])
    return np.array(vols), np.array(area)


def diso_estimate_v2(g: nx.Graph, n_dseeds: int = N_DSEEDS,
                     seed: int = 0, r_min: int = R_MIN_V2,
                     f_up: float = F_UP_V2) -> dict:
    """d_iso V2 via shell growth with r_min + upper-V window.

    Same slope window a in (-0.2, 0.95), >= 4 points/seed, >= 8 kept seeds,
    median aggregate as V1; only the shell window changes (round-2 §7).
    {d, err, r2, n_kept, n_tried, r_min, f_up, ok}.
    """
    bad = {"d": float("nan"), "err": float("nan"), "r2": float("nan"),
           "n_kept": 0, "n_tried": int(n_dseeds), "r_min": int(r_min),
           "f_up": float(f_up), "ok": False}
    nodes = list(g.nodes())
    if len(nodes) < 8 or not is_valid_measure_params(n_dseeds, 1):
        return bad
    rng = np.random.default_rng(seed)
    picks = [nodes[int(rng.integers(len(nodes)))] for _ in range(n_dseeds)]
    ds: list[float] = []
    ses: list[float] = []
    r2s: list[float] = []
    for s in picks:
        vols, area = _bfs_shell_profile_v2(g, s, r_min=r_min, f_up=f_up)
        if len(vols) < 4:
            continue
        fit = _ols_loglog(vols, area)
        a = fit["a"]
        if not np.isfinite(a) or not (-0.2 < a < 0.95):
            continue
        d = 1.0 / (1.0 - a)
        if not np.isfinite(d) or d <= 0:
            continue
        ds.append(d)
        se = fit["se_a"] / (1.0 - a) ** 2 if np.isfinite(fit["se_a"]) else np.nan
        ses.append(se)
        r2s.append(fit["r2"])
    if len(ds) < 8:
        out = dict(bad)
        out["n_kept"] = len(ds)
        return out
    arr = np.array(ds)
    sem = float(arr.std(ddof=1) / np.sqrt(len(arr))) if len(arr) > 1 else float("nan")
    med_se = float(np.nanmedian(ses)) if np.any(np.isfinite(ses)) else float("nan")
    err = float(np.nanmax([sem, med_se])) if np.any(np.isfinite([sem, med_se])) else float("nan")
    return {"d": float(np.median(arr)), "err": err,
            "r2": float(np.nanmedian(r2s)), "n_kept": len(ds),
            "n_tried": int(n_dseeds), "r_min": int(r_min),
            "f_up": float(f_up), "ok": True}


def lw_diameter_bar_v2(d_ctrl: float) -> float:
    """Frozen N-aware B4 bar: diameter >= F_B4 * control diameter (§9)."""
    return float(F_B4_V2 * float(d_ctrl))


def basin_membership_v2(diso: dict, kappa: dict, z_mean: float,
                        lw: dict, d_ctrl: float) -> dict:
    """Frozen V2 §9 B1–B4 bars (d_ctrl = pristine control diam at survey N).

    {B1..B4, member, margins, bars}. d_ctrl is explicit (prereg table value),
    never inferred from the measured graph.
    """
    try:
        b1 = bool(diso.get("ok") and abs(float(diso["d"]) - DISO_TARGET_V2) <= DISO_TOL_V2
                  and float(diso["r2"]) >= DISO_R2_MIN_V2)
        m1 = float(DISO_TOL_V2 - abs(float(diso.get("d", np.nan)) - DISO_TARGET_V2))
    except (TypeError, ValueError):
        b1, m1 = False, float("nan")
    try:
        b2 = bool(kappa.get("ok") and abs(float(kappa["mean"])) <= KAPPA_ABS_MAX_V2)
        m2 = float(KAPPA_ABS_MAX_V2 - abs(float(kappa.get("mean", np.nan))))
    except (TypeError, ValueError):
        b2, m2 = False, float("nan")
    try:
        b3 = bool(np.isfinite(z_mean) and float(z_mean) <= Z_MEAN_MAX_V2)
        m3 = float(Z_MEAN_MAX_V2 - float(z_mean))
    except (TypeError, ValueError):
        b3, m3 = False, float("nan")
    try:
        bar = lw_diameter_bar_v2(d_ctrl)
        b4 = bool(lw.get("ok") and float(lw["diameter"]) >= bar)
        m4 = float(float(lw.get("diameter", np.nan)) - bar)
    except (TypeError, ValueError):
        b4, m4 = False, float("nan")
        bar = float("nan")
    return {"B1_diso": b1, "B2_kappa": b2, "B3_sparse": b3, "B4_lw": b4,
            "member": bool(b1 and b2 and b3 and b4),
            "margins": {"B1": m1, "B2": m2, "B3": m3, "B4": m4},
            "bars": {"B4_bar": bar, "d_ctrl": float(d_ctrl)}}


def measure_graph_v2(g: nx.Graph, d_ctrl: float, seed: int = 0,
                     n_dseeds: int = N_DSEEDS,
                     max_edges: int = KAPPA_MAX_EDGES,
                     n_dist_samples: int = N_DIST_SAMPLES,
                     r_min: int = R_MIN_V2,
                     f_up: float = F_UP_V2) -> dict:
    """Full V2 outcome bundle for one graph (V2 runner checkpoints call this)."""
    diso = diso_estimate_v2(g, n_dseeds=n_dseeds, seed=seed, r_min=r_min,
                            f_up=f_up)
    kappa = kappa_sample_mean(g, max_edges=max_edges, seed=seed + 1)
    z = coordination(g)
    lw = large_world_stats(g, n_dist_samples=n_dist_samples, seed=seed + 2)
    return {"diso": diso, "kappa": kappa, "z": z, "lw": lw,
            "basin": basin_membership_v2(diso, kappa, z["z_mean"], lw, d_ctrl),
            "label": "exploratory"}
