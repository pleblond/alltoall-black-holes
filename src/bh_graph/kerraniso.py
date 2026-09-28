"""D2 Route A calibration: latitude-labeled shell graphs -> zonal Ollivier-Ricci.

STATUS — READ FIRST. This module derives NOTHING about Kerr multipoles from
the graph. It is the Route A calibration step from
``docs/kerr-multipoles-exploration.md``: impose an axisymmetric bridge-density
deformation on the existing gradient-shell graphs (``orici``), measure
Ollivier-Ricci curvature separately on polar vs equatorial radial edges, and
report the imposed-vs-measured anisotropy map. The imposed ``epsilon_bridge``
is a SPIN PROXY (put in by hand), not spin derived from graph dynamics — so
this calibrates the "wiring anisotropy -> curvature anisotropy" map the same
way the ``p`` measurement calibrated the radial sector. It does not close D2.

Conventions (P2-mirroring throughout, matching ``kerrquad`` shell toys):
poles carry weight ``1 + eps``, equatorial nodes ``1 - eps/2`` (cf.
``P2(pole) = 1``, ``P2(equator) = -1/2``). So ``eps > 0`` = polar excess
(prolate, Kerr-quadrupole sign WRONG), ``eps < 0`` = equatorial excess
(oblate, Kerr sign RIGHT). Valid range is the open interval (-1, 2) where
both weights stay positive. Measured ``eps_OR`` uses the same sign: ``> 0``
means polar ``|kappa|`` exceeds equatorial.
"""
from __future__ import annotations

import networkx as nx
import numpy as np

from bh_graph.orici import (
    BRIDGE_BETA_NEW,
    BRIDGE_BETA_OLD,
    fit_scaling_power,
    n_bridges_for_pair,
    ollivier_curvature,
    ollivier_curvature_eint,
    p_adj_of_shell,
    shell_pair_radius,
)

POLAR = "polar"
EQUATORIAL = "equatorial"
MIXED = "mixed"

#: Default zone split: area-equal halves (uniform sphere has P(|cos t| > 1/2)
#: = 1/2), which maximizes statistical power for the polar-equatorial
#: difference. Zones are statistical labels, not physical polar caps.
DEFAULT_POLAR_FRACTION = 0.5


def is_valid_bridge_eps(eps) -> bool:
    """Boolean check: eps in (-1, 2) and finite (both zone weights > 0)?"""
    try:
        e = float(np.asarray(eps, dtype=float))
    except (TypeError, ValueError):
        return False
    return bool(np.isfinite(e) and -1.0 < e < 2.0)


def assign_latitude_labels(per_shell: int, polar_fraction: float = DEFAULT_POLAR_FRACTION) -> dict[int, str]:
    """Deterministic zone per node index: first n_polar indices polar, rest equatorial.

    ``n_polar`` is clamped to [1, per_shell - 1] so both zones are nonempty.
    Invalid ``polar_fraction`` falls back to the default (no exceptions).
    """
    try:
        per_shell = int(per_shell)
    except (TypeError, ValueError):
        return {}
    if per_shell < 2:
        return {}
    try:
        f = float(polar_fraction)
    except (TypeError, ValueError):
        f = DEFAULT_POLAR_FRACTION
    if not np.isfinite(f) or not 0.0 < f < 1.0:
        f = DEFAULT_POLAR_FRACTION
    n_polar = int(min(max(round(per_shell * f), 1), per_shell - 1))
    return {i: (POLAR if i < n_polar else EQUATORIAL) for i in range(per_shell)}


def gradient_shell_graph_latitude(
    per_shell: int = 30,
    n_shells: int = 10,
    gradient: bool = True,
    beta: float | None = None,
    epsilon_bridge: float = 0.0,
    polar_fraction: float = DEFAULT_POLAR_FRACTION,
    seed: int = 0,
) -> nx.Graph:
    """Gradient shells with zone labels and P2-weighted bridge placement.

    Intra-shell edges are identical to ``orici.gradient_shell_graph`` (same
    RNG stream). Inter-shell bridges keep the same deterministic COUNT per
    pair (``n_bridges_for_pair``) but endpoints are sampled with zone weights
    ``w_polar = 1 + eps``, ``w_equatorial = 1 - eps/2`` (pair weight = product).
    At ``eps = 0`` the code path is exactly ``orici``'s (edge sets identical
    for the same seed). Invalid ``epsilon_bridge`` falls back to uniform
    (check with :func:`is_valid_bridge_eps`). Nodes carry a ``zone`` attr.
    """
    if beta is None:
        beta = BRIDGE_BETA_NEW if gradient else BRIDGE_BETA_OLD
    try:
        eps = float(epsilon_bridge)
    except (TypeError, ValueError):
        eps = 0.0
    if not is_valid_bridge_eps(eps):
        eps = 0.0
    labels = assign_latitude_labels(per_shell, polar_fraction)
    rng = np.random.default_rng(seed)
    g = nx.Graph()
    for s in range(n_shells):
        for i in range(per_shell):
            g.add_node((s, i), zone=labels.get(i, EQUATORIAL))
    for s in range(n_shells):
        p = p_adj_of_shell(s, gradient)
        for ii in range(per_shell):
            for jj in range(ii + 1, per_shell):
                if rng.random() < p:
                    g.add_edge((s, ii), (s, jj))
    w_pol = 1.0 + eps
    w_eq = 1.0 - eps / 2.0
    w = np.array([w_pol if labels.get(i) == POLAR else w_eq for i in range(per_shell)])
    for s in range(n_shells - 1):
        r_mid = shell_pair_radius(s, n_shells)
        n_br = n_bridges_for_pair(r_mid, per_shell, beta)
        pairs = [(i, j) for i in range(per_shell) for j in range(per_shell)]
        size = min(n_br, len(pairs))
        if eps == 0.0:
            sel = rng.choice(len(pairs), size=size, replace=False)
        else:
            pw = np.array([w[i] * w[j] for i, j in pairs], dtype=float)
            pw /= pw.sum()
            sel = rng.choice(len(pairs), size=size, replace=False, p=pw)
        for k in sel:
            i, j = pairs[int(k)]
            g.add_edge((s, i), (s + 1, j))
    return g


def edge_zone(g: nx.Graph, u, v) -> str:
    """Zone of a radial edge: polar / equatorial if both ends agree, else mixed."""
    try:
        zu = g.nodes[u].get("zone")
        zv = g.nodes[v].get("zone")
    except KeyError:
        return MIXED
    if zu == POLAR and zv == POLAR:
        return POLAR
    if zu == EQUATORIAL and zv == EQUATORIAL:
        return EQUATORIAL
    return MIXED


def bridge_polar_fraction(g: nx.Graph, n_shells: int) -> float:
    """Fraction of inter-shell bridge endpoints in the polar zone.

    Verifies the imposition worked: must rise monotonically with
    ``epsilon_bridge``. NaN if the graph has no bridges.
    """
    n_pol = 0
    n_tot = 0
    for u, v in g.edges():
        if not (isinstance(u, tuple) and isinstance(v, tuple)):
            continue
        if len(u) != 2 or len(v) != 2:
            continue
        if u[0] == v[0]:
            continue
        for node in (u, v):
            n_tot += 1
            if g.nodes[node].get("zone") == POLAR:
                n_pol += 1
    if n_tot == 0:
        return float("nan")
    return float(n_pol / n_tot)


def shell_kappa_profile_by_zone(
    g: nx.Graph, n_shells: int, max_per_zone: int = 4, e_int: float | None = None
) -> dict[float, dict[str, float]]:
    """Mean exact-OR kappa on radial edges per shell-pair, split by zone.

    Caps EACH zone at ``max_per_zone`` edges per shell-pair (balanced stats).
    ``e_int = None`` uses the uniform measure (default, principled); a value
    in [0, 1] uses the e_int-weighted measure. Returns
    ``{r: {"polar": ..., "equatorial": ..., "mixed": ..., "all": ...}}`` with
    NaN for empty zones.
    """
    dist = nx.floyd_warshall_numpy(g)
    idx = {v: i for i, v in enumerate(g.nodes())}
    out: dict[float, dict[str, float]] = {}
    for s in range(n_shells - 1):
        r = shell_pair_radius(s, n_shells)
        kaps: dict[str, list[float]] = {POLAR: [], EQUATORIAL: [], MIXED: []}
        for u, v in g.edges():
            if not (isinstance(u, tuple) and isinstance(v, tuple)):
                continue
            if len(u) != 2 or len(v) != 2:
                continue
            if sorted([u[0], v[0]]) != [s, s + 1]:
                continue
            z = edge_zone(g, u, v)
            if len(kaps[z]) >= max_per_zone:
                continue
            if e_int is None:
                kaps[z].append(ollivier_curvature(g, u, v, _dist=dist, _idx=idx))
            else:
                kaps[z].append(ollivier_curvature_eint(g, u, v, e_int, _dist=dist, _idx=idx))
            if all(len(kaps[z]) >= max_per_zone for z in kaps):
                break
        zone_means = {z: (float(np.mean(kaps[z])) if kaps[z] else float("nan")) for z in kaps}
        flat = [k for z in kaps for k in kaps[z]]
        zone_means["all"] = float(np.mean(flat)) if flat else float("nan")
        out[r] = zone_means
    return out


def zonal_anisotropy(profile_by_zone: dict[float, dict[str, float]]) -> dict:
    """Per-shell ``eps_OR = (|pol| - |eq|) / |all|`` with ``|.| = -kappa``.

    Positive = polar curvature magnitude exceeds equatorial (same sign
    convention as imposed ``epsilon_bridge``). A shell contributes only if
    polar, equatorial, AND all means are negative and finite; otherwise NaN.
    Returns ``{"per_shell": {r: eps}, "stacked": mean-of-finite, "n_ok": int}``.
    """
    per_shell: dict[float, float] = {}
    for r, zm in profile_by_zone.items():
        try:
            kp = float(zm[POLAR])
            ke = float(zm[EQUATORIAL])
            ka = float(zm["all"])
        except (KeyError, TypeError, ValueError):
            per_shell[r] = float("nan")
            continue
        if all(np.isfinite(v) and v < 0 for v in (kp, ke, ka)):
            per_shell[r] = float((-kp + ke) / -ka)
        else:
            per_shell[r] = float("nan")
    ok = np.array([v for v in per_shell.values() if np.isfinite(v)])
    return {
        "per_shell": per_shell,
        "stacked": float(np.mean(ok)) if len(ok) else float("nan"),
        "n_ok": len(ok),
    }


def _stacked_zone_profile(profiles: list[dict[float, dict[str, float]]], zone: str) -> dict[float, float]:
    rs = sorted(profiles[0]) if profiles else []
    stacked: dict[float, float] = {}
    for r in rs:
        vals = np.array([p[r][zone] for p in profiles if zone in p.get(r, {})])
        vals = vals[np.isfinite(vals)]
        stacked[r] = float(np.mean(vals)) if len(vals) else float("nan")
    return stacked


def measure_anisotropy(
    per_shell: int = 15,
    n_shells: int = 6,
    n_graphs: int = 8,
    gradient: bool = True,
    beta: float | None = None,
    epsilon_bridge: float = 0.0,
    polar_fraction: float = DEFAULT_POLAR_FRACTION,
    seed0: int = 0,
    max_per_zone: int = 4,
    e_int: float | None = None,
) -> dict:
    """Measured eps_OR over n_graphs at one imposed epsilon_bridge.

    Returns per-graph stacked eps list, mean/std/sem, bridge polar fractions
    (imposition check), stacked per-zone profiles, and per-zone ``|k| ~ r^-p``
    fits (NaN-tolerant). Empty/NaN-tolerant throughout (no exceptions).
    """
    per_graph: list[float] = []
    bridge_fracs: list[float] = []
    profiles = []
    try:
        eps_out = float(epsilon_bridge)
    except (TypeError, ValueError):
        eps_out = 0.0
    if not np.isfinite(eps_out):
        eps_out = 0.0
    for t in range(n_graphs):
        g = gradient_shell_graph_latitude(
            per_shell, n_shells, gradient, beta, epsilon_bridge, polar_fraction, seed0 + t
        )
        bridge_fracs.append(bridge_polar_fraction(g, n_shells))
        prof = shell_kappa_profile_by_zone(g, n_shells, max_per_zone, e_int)
        profiles.append(prof)
        per_graph.append(zonal_anisotropy(prof)["stacked"])
    per_graph = np.array(per_graph, dtype=float)
    ok = per_graph[np.isfinite(per_graph)]
    stacked = {z: _stacked_zone_profile(profiles, z) for z in (POLAR, EQUATORIAL, MIXED, "all")}
    fits = {z: fit_scaling_power(stacked[z]) for z in stacked}
    return {
        "epsilon_bridge": eps_out,
        "per_graph": per_graph,
        "mean": float(np.mean(ok)) if len(ok) else float("nan"),
        "std": float(np.std(ok)) if len(ok) else float("nan"),
        "sem": float(np.std(ok) / np.sqrt(len(ok))) if len(ok) else float("nan"),
        "n_ok": len(ok),
        "bridge_polar_frac_mean": float(np.nanmean(bridge_fracs)) if len(bridge_fracs) else float("nan"),
        "stacked": stacked,
        "stacked_fits": fits,
    }


def calibration_curve(eps_grid, **kwargs) -> dict:
    """Measured eps_OR vs imposed epsilon_bridge over a grid + linear slope.

    ``kwargs`` pass through to :func:`measure_anisotropy`. Slope is the
    ordinary least-squares ``d(measured)/d(imposed)`` over finite points
    (NaN if fewer than 2 finite). The slope SIGN is the key calibration
    result: positive means polar bridge excess -> polar |kappa| excess.
    """
    grid = [float(e) for e in list(eps_grid)]
    results = [measure_anisotropy(epsilon_bridge=e, **kwargs) for e in grid]
    means = np.array([r["mean"] for r in results], dtype=float)
    sems = np.array([r["sem"] for r in results], dtype=float)
    mask = np.isfinite(means)
    if int(mask.sum()) >= 2:
        slope = float(np.polyfit(np.array(grid)[mask], means[mask], 1)[0])
    else:
        slope = float("nan")
    return {
        "eps_imposed": grid,
        "eps_measured": means,
        "eps_sem": sems,
        "slope": slope,
        "results": results,
    }


def is_anisotropy_detected(result: dict, sigma: float = 2.0) -> bool:
    """Boolean check: |mean| > sigma * sem with >= 2 ok graphs (all finite)?"""
    try:
        mean = float(result["mean"])
        sem = float(result["sem"])
        n_ok = int(result["n_ok"])
        sig = float(sigma)
    except (KeyError, TypeError, ValueError):
        return False
    if not all(np.isfinite(v) for v in (mean, sem, sig)) or sig <= 0:
        return False
    return bool(n_ok >= 2 and sem > 0 and abs(mean) > sig * sem)
