"""D2 Route A2 calibration: latitude-dependent intra-shell completeness.

STATUS — READ FIRST. This module derives NOTHING about Kerr multipoles from
the graph. It is a calibration step parallel to ``kerraniso`` (Route A
bridge anisotropy): impose a latitude-dependent intra-shell completeness
deformation on gradient-shell graphs, measure zonal Ollivier-Ricci
curvature on polar vs equatorial radial edges, and report the
imposed-vs-measured anisotropy map. The imposed ``delta_complete`` is a
SPIN PROXY (put in by hand), not spin derived from graph dynamics — spin
from dynamics remains OPEN. Like ``kerraniso``, this calibrates the
"wiring anisotropy -> curvature anisotropy" map; it does not close D2.

Conventions (P2-mirroring, matching ``kerraniso``/``kerrquad``): intra-shell
pair probability is ``p = base + delta*(w_i + w_j)/2`` with ``w = +1`` for
polar nodes and ``w = -1/2`` for equatorial nodes. So ``delta > 0`` gives
polar completeness excess, ``delta < 0`` equatorial excess. Valid range is
[-0.3, 0.3]; probabilities are clamped to [0.02, 0.995] and bridges stay
uniform to isolate the completeness effect.
"""
from __future__ import annotations

import networkx as nx
import numpy as np

from bh_graph.kerraniso import (
    DEFAULT_POLAR_FRACTION,
    EQUATORIAL,
    MIXED,
    POLAR,
    assign_latitude_labels,
    shell_kappa_profile_by_zone,
    zonal_anisotropy,
)
from bh_graph.kerrp2 import (
    attach_latitudes,
    p2_amplitude,
    p2_legendre,
    radial_edges_with_kappa,
)
from bh_graph.orici import (
    BRIDGE_BETA_NEW,
    BRIDGE_BETA_OLD,
    fit_scaling_power,
    n_bridges_for_pair,
    p_adj_of_shell,
    shell_pair_radius,
)

#: Clamp range for zone-dependent intra-shell probabilities.
P_MIN = 0.02
P_MAX = 0.995

#: Valid imposed-completeness range (keeps deformations perturbative).
DELTA_MIN = -0.3
DELTA_MAX = 0.3


def is_valid_complete_delta(d) -> bool:
    """Boolean check: d finite and in [-0.3, 0.3]?"""
    try:
        v = float(np.asarray(d, dtype=float))
    except (TypeError, ValueError):
        return False
    return bool(np.isfinite(v) and DELTA_MIN <= v <= DELTA_MAX)


def gradient_shell_graph_completeness(
    per_shell: int = 30,
    n_shells: int = 10,
    gradient: bool = True,
    beta: float | None = None,
    delta_complete: float = 0.0,
    polar_fraction: float = DEFAULT_POLAR_FRACTION,
    seed: int = 0,
) -> nx.Graph:
    """Gradient shells with zone-dependent intra-shell completeness.

    Intra-shell pair (ii, jj) in shell s uses ``p = base + delta*(w_i+w_j)/2``
    with ``base = p_adj_of_shell(s, gradient)``, ``w = +1`` polar, ``-1/2``
    equatorial (zones from ``assign_latitude_labels``), clamped to
    [0.02, 0.995]. At ``delta = 0`` the RNG stream is identical to
    ``orici.gradient_shell_graph`` (same call order), so edge sets match
    exactly for the same seed. Bridges are uniform (same unweighted code as
    ``orici``) to isolate the completeness effect. Nodes carry ``zone`` attrs.
    Invalid ``delta_complete`` falls back to 0.0 (no exceptions).
    """
    try:
        per_shell = int(per_shell)
    except (TypeError, ValueError):
        return nx.Graph()
    try:
        n_shells = int(n_shells)
    except (TypeError, ValueError):
        return nx.Graph()
    if per_shell < 1 or n_shells < 1:
        return nx.Graph()
    if beta is None:
        beta = BRIDGE_BETA_NEW if gradient else BRIDGE_BETA_OLD
    try:
        beta = float(beta)
    except (TypeError, ValueError):
        beta = BRIDGE_BETA_NEW if gradient else BRIDGE_BETA_OLD
    if not np.isfinite(beta):
        beta = BRIDGE_BETA_NEW if gradient else BRIDGE_BETA_OLD
    try:
        delta = float(delta_complete)
    except (TypeError, ValueError):
        delta = 0.0
    if not is_valid_complete_delta(delta):
        delta = 0.0
    try:
        rng = np.random.default_rng(seed)
    except (TypeError, ValueError):
        rng = np.random.default_rng(0)
    labels = assign_latitude_labels(per_shell, polar_fraction)
    w = np.array(
        [1.0 if labels.get(i) == POLAR else -0.5 for i in range(per_shell)]
    )
    g = nx.Graph()
    for s in range(n_shells):
        for i in range(per_shell):
            g.add_node((s, i), zone=labels.get(i, EQUATORIAL))
    for s in range(n_shells):
        base = p_adj_of_shell(s, gradient)
        for ii in range(per_shell):
            for jj in range(ii + 1, per_shell):
                if delta == 0.0:
                    p = base
                else:
                    p = base + delta * (w[ii] + w[jj]) / 2.0
                    p = min(max(p, P_MIN), P_MAX)
                if rng.random() < p:
                    g.add_edge((s, ii), (s, jj))
    for s in range(n_shells - 1):
        r_mid = shell_pair_radius(s, n_shells)
        n_br = n_bridges_for_pair(r_mid, per_shell, beta)
        pairs = [(i, j) for i in range(per_shell) for j in range(per_shell)]
        sel = rng.choice(len(pairs), size=min(n_br, len(pairs)), replace=False)
        for k in sel:
            i, j = pairs[int(k)]
            g.add_edge((s, i), (s + 1, j))
    return g


def zone_intra_density(g: nx.Graph, n_shells: int) -> dict[str, float]:
    """Intra-shell edge density split by pair zone (imposition check).

    Counts realized over possible intra-shell pairs for both-polar pairs vs
    both-equatorial pairs; cross-zone pairs are ignored. NaN where a zone
    has no possible pairs. Never raises (NaN on bad inputs).
    """
    bad = {"polar": float("nan"), "equatorial": float("nan")}
    try:
        n_shells = int(n_shells)
    except (TypeError, ValueError):
        return bad
    try:
        nodes = list(g.nodes())
        edges = list(g.edges())
    except (AttributeError, TypeError):
        return bad
    try:
        n_pol = np.zeros(n_shells, dtype=float)
        n_eq = np.zeros(n_shells, dtype=float)
        for v in nodes:
            if not (isinstance(v, tuple) and len(v) == 2):
                continue
            s = v[0]
            if not isinstance(s, (int, np.integer)) or not 0 <= s < n_shells:
                continue
            if g.nodes[v].get("zone") == POLAR:
                n_pol[s] += 1
            else:
                n_eq[s] += 1
        r_pol = 0
        r_eq = 0
        for u, v in edges:
            if not (isinstance(u, tuple) and isinstance(v, tuple)):
                continue
            if len(u) != 2 or len(v) != 2 or u[0] != v[0]:
                continue
            zu = g.nodes[u].get("zone")
            zv = g.nodes[v].get("zone")
            if zu == POLAR and zv == POLAR:
                r_pol += 1
            elif zu == EQUATORIAL and zv == EQUATORIAL:
                r_eq += 1
        poss_pol = float(np.sum(n_pol * (n_pol - 1) / 2.0))
        poss_eq = float(np.sum(n_eq * (n_eq - 1) / 2.0))
        return {
            "polar": float(r_pol / poss_pol) if poss_pol > 0 else float("nan"),
            "equatorial": float(r_eq / poss_eq) if poss_eq > 0 else float("nan"),
        }
    except (TypeError, ValueError, KeyError, AttributeError):
        return bad


def _stacked_zone_profile(
    profiles: list[dict[float, dict[str, float]]], zone: str
) -> dict[float, float]:
    rs = sorted(profiles[0]) if profiles and isinstance(profiles[0], dict) else []
    stacked: dict[float, float] = {}
    for r in rs:
        try:
            vals = np.array([p[r][zone] for p in profiles if zone in p.get(r, {})])
        except (TypeError, KeyError, AttributeError):
            stacked[r] = float("nan")
            continue
        vals = vals[np.isfinite(vals)]
        stacked[r] = float(np.mean(vals)) if len(vals) else float("nan")
    return stacked


def measure_completeness_anisotropy(
    per_shell: int = 15,
    n_shells: int = 6,
    n_graphs: int = 8,
    gradient: bool = True,
    beta: float | None = None,
    delta_complete: float = 0.0,
    polar_fraction: float = DEFAULT_POLAR_FRACTION,
    seed0: int = 0,
    max_per_zone: int = 4,
    e_int: float | None = None,
) -> dict:
    """Measured eps_OR over n_graphs at one imposed delta_complete.

    Builds graphs with :func:`gradient_shell_graph_completeness` and measures
    with ``shell_kappa_profile_by_zone`` + ``zonal_anisotropy``. Returns
    per-graph stacked eps list, mean/std/sem, zone density gap mean
    (imposition check), stacked per-zone profiles, and per-zone ``|k| ~ r^-p``
    fits (NaN-tolerant). Empty/NaN-tolerant throughout (no exceptions).
    """
    try:
        d_out = float(delta_complete)
    except (TypeError, ValueError):
        d_out = 0.0
    if not np.isfinite(d_out):
        d_out = 0.0
    try:
        n_graphs = int(n_graphs)
    except (TypeError, ValueError):
        n_graphs = 0
    try:
        seed0 = int(seed0)
    except (TypeError, ValueError):
        seed0 = 0
    try:
        max_per_zone = int(max_per_zone)
    except (TypeError, ValueError):
        max_per_zone = 4
    per_graph: list[float] = []
    gaps: list[float] = []
    profiles = []
    for t in range(max(n_graphs, 0)):
        try:
            g = gradient_shell_graph_completeness(
                per_shell, n_shells, gradient, beta,
                delta_complete, polar_fraction, seed0 + t,
            )
            dens = zone_intra_density(g, n_shells)
            dp = float(dens["polar"])
            de = float(dens["equatorial"])
            gaps.append(dp - de if np.isfinite(dp) and np.isfinite(de) else np.nan)
            prof = shell_kappa_profile_by_zone(g, n_shells, max_per_zone, e_int)
            profiles.append(prof)
            per_graph.append(zonal_anisotropy(prof)["stacked"])
        except (TypeError, ValueError, KeyError, AttributeError, RuntimeError,
                ArithmeticError, nx.NetworkXException):
            per_graph.append(float("nan"))
            gaps.append(float("nan"))
            profiles.append({})
    per_graph_arr = np.array(per_graph, dtype=float)
    ok = per_graph_arr[np.isfinite(per_graph_arr)]
    stacked = {
        z: _stacked_zone_profile(profiles, z)
        for z in (POLAR, EQUATORIAL, MIXED, "all")
    }
    fits = {}
    for z, prof in stacked.items():
        try:
            fits[z] = fit_scaling_power(prof)
        except (TypeError, ValueError, ArithmeticError):
            fits[z] = {"p": float("nan"), "p_err": float("nan"), "r2": float("nan")}
    gaps_arr = np.array(gaps, dtype=float) if gaps else np.array([])
    gaps_ok = gaps_arr[np.isfinite(gaps_arr)] if len(gaps_arr) else np.array([])
    return {
        "delta_complete": d_out,
        "per_graph": per_graph_arr,
        "mean": float(np.mean(ok)) if len(ok) else float("nan"),
        "std": float(np.std(ok)) if len(ok) else float("nan"),
        "sem": float(np.std(ok) / np.sqrt(len(ok))) if len(ok) else float("nan"),
        "n_ok": len(ok),
        "zone_density_gap_mean": float(np.mean(gaps_ok)) if len(gaps_ok) else float("nan"),
        "stacked": stacked,
        "stacked_fits": fits,
    }


def completeness_curve(delta_grid, **kwargs) -> dict:
    """Measured eps_OR vs imposed delta_complete over a grid + linear slope.

    ``kwargs`` pass through to :func:`measure_completeness_anisotropy`. Slope
    is the ordinary least-squares ``d(measured)/d(imposed)`` over finite
    points (NaN if fewer than 2 finite). Never raises on bad inputs.
    """
    try:
        raw = list(delta_grid)
    except TypeError:
        raw = []
    grid = []
    for e in raw:
        try:
            grid.append(float(e))
        except (TypeError, ValueError):
            grid.append(float("nan"))
    results = []
    for e in grid:
        try:
            results.append(measure_completeness_anisotropy(delta_complete=e, **kwargs))
        except (TypeError, ValueError, KeyError, AttributeError, RuntimeError,
                ArithmeticError):
            results.append(
                measure_completeness_anisotropy(delta_complete=0.0, **kwargs)
            )
    means = np.array([r["mean"] for r in results], dtype=float) if results else np.array([])
    sems = np.array([r["sem"] for r in results], dtype=float) if results else np.array([])
    mask = np.isfinite(means) & np.isfinite(np.array(grid, dtype=float))
    if int(mask.sum()) >= 2:
        try:
            slope = float(np.polyfit(np.array(grid)[mask], means[mask], 1)[0])
        except (TypeError, ValueError, ArithmeticError):
            slope = float("nan")
    else:
        slope = float("nan")
    return {
        "eps_imposed": grid,
        "eps_measured": means,
        "eps_sem": sems,
        "slope": slope,
        "results": results,
    }


# ---------------------------------------------------------------------------
# True quadrupole-channel completeness: P2-weighted intra-shell probability.
#
# Hemispheric-channel caveat (see kerrp2.CHANNEL NOTE): the index-half zones
# above are north-vs-south, so completeness_curve's slope (+0.19) lives in the
# dipole-like channel. Here the deformation is EVEN under N/S reflection:
# p = base + delta*(P2_i + P2_j)/2, i.e. caps-vs-band completeness excess for
# delta > 0 — the quadrupole-channel analogue, read out with B.
# ---------------------------------------------------------------------------


def _stratified_cos(per_shell: int) -> np.ndarray:
    """Stratified cos_theta per node index (same convention as attach_latitudes)."""
    return np.array([1.0 - (2.0 * i + 1.0) / per_shell for i in range(per_shell)])


def gradient_shell_graph_p2complete(
    per_shell: int = 30,
    n_shells: int = 10,
    gradient: bool = True,
    beta: float | None = None,
    delta_p2: float = 0.0,
    seed: int = 0,
) -> nx.Graph:
    """Gradient shells with P2-weighted intra-shell completeness.

    Intra-shell pair (ii, jj) in shell s uses
    ``p = base + delta*(P2_i + P2_j)/2`` with ``base = p_adj_of_shell(s)``,
    clamped to [0.02, 0.995]; ``delta > 0`` = caps completeness excess.
    Bridges are uniform (same unweighted code as ``orici``). At ``delta = 0``
    the RNG stream is identical to ``orici.gradient_shell_graph``. Nodes carry
    ``zone`` (index-half) and ``cos_theta`` attrs. Invalid ``delta_p2`` falls
    back to 0.0 (check with :func:`is_valid_complete_delta`).
    """
    if beta is None:
        beta = BRIDGE_BETA_NEW if gradient else BRIDGE_BETA_OLD
    try:
        delta = float(delta_p2)
    except (TypeError, ValueError):
        delta = 0.0
    if not is_valid_complete_delta(delta):
        delta = 0.0
    labels = assign_latitude_labels(per_shell, DEFAULT_POLAR_FRACTION)
    rng = np.random.default_rng(seed)
    g = nx.Graph()
    for s in range(n_shells):
        for i in range(per_shell):
            g.add_node((s, i), zone=labels.get(i, EQUATORIAL))
    attach_latitudes(g, per_shell, n_shells)
    p2v = np.asarray(p2_legendre(_stratified_cos(per_shell)), dtype=float)
    for s in range(n_shells):
        base = p_adj_of_shell(s, gradient)
        for ii in range(per_shell):
            for jj in range(ii + 1, per_shell):
                if delta == 0.0:
                    p = base
                else:
                    p = base + delta * (p2v[ii] + p2v[jj]) / 2.0
                    p = min(max(p, P_MIN), P_MAX)
                if rng.random() < p:
                    g.add_edge((s, ii), (s, jj))
    for s in range(n_shells - 1):
        r_mid = shell_pair_radius(s, n_shells)
        n_br = n_bridges_for_pair(r_mid, per_shell, beta)
        pairs = [(i, j) for i in range(per_shell) for j in range(per_shell)]
        sel = rng.choice(len(pairs), size=min(n_br, len(pairs)), replace=False)
        for k in sel:
            i, j = pairs[int(k)]
            g.add_edge((s, i), (s + 1, j))
    return g


def caps_band_degree_gap(g: nx.Graph) -> float:
    """Mean intra-shell degree of caps nodes minus band nodes (imposition check).

    Caps = |cos_theta| > 1/2, band = the rest. Must rise monotonically with
    ``delta_p2``. NaN if either group is empty or latitudes are missing
    (never raises).
    """
    try:
        nodes = list(g.nodes())
    except (AttributeError, TypeError):
        return float("nan")
    caps: list[float] = []
    band: list[float] = []
    for v in nodes:
        try:
            if not (isinstance(v, tuple) and len(v) == 2):
                continue
            cu = float(g.nodes[v].get("cos_theta"))
            if not np.isfinite(cu):
                continue
            deg = 0
            for x in g.neighbors(v):
                if isinstance(x, tuple) and len(x) == 2 and x[0] == v[0]:
                    deg += 1
            (caps if abs(cu) > 0.5 else band).append(float(deg))
        except (KeyError, TypeError, ValueError, AttributeError):
            continue
    if not caps or not band:
        return float("nan")
    return float(np.mean(caps) - np.mean(band))


def measure_p2complete_response(
    per_shell: int = 15,
    n_shells: int = 6,
    n_graphs: int = 8,
    gradient: bool = True,
    beta: float | None = None,
    delta_p2: float = 0.0,
    seed0: int = 0,
    max_per_shellpair: int = 12,
    e_int: float | None = None,
) -> dict:
    """P2 amplitude ``B`` over ``n_graphs`` at one imposed P2 ``delta_p2``.

    Builds graphs with :func:`gradient_shell_graph_p2complete` and estimates
    ``B`` per graph via ``kerrp2`` helpers. Includes ``degree_gap_mean``
    (imposition check). NaN-tolerant throughout (no exceptions).
    """
    try:
        d_out = float(delta_p2)
    except (TypeError, ValueError):
        d_out = 0.0
    if not np.isfinite(d_out):
        d_out = 0.0
    try:
        n_graphs = int(n_graphs)
        seed0 = int(seed0)
    except (TypeError, ValueError):
        n_graphs, seed0 = 0, 0
    per_graph: list[float] = []
    gaps: list[float] = []
    for t in range(max(n_graphs, 0)):
        try:
            g = gradient_shell_graph_p2complete(
                per_shell, n_shells, gradient, beta, delta_p2, seed0 + t
            )
            gaps.append(caps_band_degree_gap(g))
            rows = radial_edges_with_kappa(g, n_shells, max_per_shellpair, e_int)
            per_graph.append(float(p2_amplitude(rows)["B"]))
        except Exception:  # noqa: BLE001 - never-raise: NaN/fallback
            per_graph.append(float("nan"))
            gaps.append(float("nan"))
    arr = np.array(per_graph, dtype=float)
    ok = arr[np.isfinite(arr)]
    return {
        "delta_p2": d_out,
        "per_graph": arr,
        "mean": float(np.mean(ok)) if len(ok) else float("nan"),
        "std": float(np.std(ok)) if len(ok) else float("nan"),
        "sem": float(np.std(ok) / np.sqrt(len(ok))) if len(ok) else float("nan"),
        "n_ok": len(ok),
        "degree_gap_mean": float(np.nanmean(gaps)) if len(gaps) else float("nan"),
    }


def p2complete_curve(delta_grid, **kwargs) -> dict:
    """P2 amplitude ``B`` vs imposed P2 ``delta_p2`` + OLS slope.

    Quadrupole-channel analogue of :func:`completeness_curve`. Under the
    "completeness deepens |k|" picture from the hemispheric channel, the slope
    here should be POSITIVE (caps completeness excess -> caps |k| excess) —
    opposite to the P2-bridge slope if the bridge/completeness opposition is
    structural rather than channel-specific.
    """
    try:
        grid = [float(e) for e in list(delta_grid)]
    except (TypeError, ValueError):
        grid = []
    results = []
    for e in grid:
        try:
            results.append(measure_p2complete_response(delta_p2=e, **kwargs))
        except Exception:  # noqa: BLE001 - never-raise: NaN/fallback
            results.append({"mean": float("nan"), "sem": float("nan")})
    try:
        means = np.array([float(r["mean"]) for r in results], dtype=float)
        sems = np.array([float(r["sem"]) for r in results], dtype=float)
    except (KeyError, TypeError, ValueError):
        means = np.full(len(results), np.nan)
        sems = np.full(len(results), np.nan)
    mask = np.isfinite(means)
    if int(mask.sum()) >= 2:
        slope = float(np.polyfit(np.array(grid)[mask], means[mask], 1)[0])
    else:
        slope = float("nan")
    return {
        "eps_imposed": grid,
        "b_measured": means,
        "b_sem": sems,
        "slope": slope,
        "results": results,
    }
