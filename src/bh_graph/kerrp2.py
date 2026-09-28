"""D2 Route A calibration: CONTINUOUS-latitude P2 estimator (alternative readout).

STATUS — READ FIRST. This module derives NOTHING about Kerr multipoles from
the graph. It is an alternative ESTIMATOR for the SAME imposed-proxy
calibration as ``kerraniso`` (Route A from
``docs/kerr-multipoles-exploration.md``): identical graph builder
(``kerraniso.gradient_shell_graph_latitude``) with the same hand-imposed
bridge-density proxy ``epsilon_bridge`` (a spin proxy, not derived spin),
but a different readout of curvature anisotropy. Where ``kerraniso`` bins
radial edges into polar/equatorial zones and forms the binary estimator
``eps_OR = (|k_pol| - |k_eq|) / |k_all|``, this module fits a pooled,
per-shell-pair-normalized regression of ``|kappa|`` on the Legendre
``P2(cos theta)`` latitude of each radial edge and reports the OLS slope
``B`` in ``|k| ~= A (1 + B P2)``. Same sign convention as ``eps_OR``
(``B > 0`` = polar ``|k|`` excess). ``B`` uses every sampled radial edge
instead of zone-pure subsets, so it stays defined where one zone starves
(``|eps| >= ~1``). Agreement with ``eps_OR`` where both work checks
estimator robustness — it does not close D2.

CHANNEL NOTE (hemispheric vs quadrupole). The ``kerraniso``/``kerrcomplete``
index-half zones are HEMISPHERIC (north vs south, corr(zone-step, P2) ~ -0.08):
their "P2-mirroring" weights carry P2-like NUMBERS on hemispheric GEOMETRY,
so the binary ``eps_OR`` slopes (~-0.1 bridges, ~+0.19 completeness) live in
the dipole-like hemispheric channel, while ``B`` under that imposition is
correctly ~0 (orthogonal channels). The ``*_p2bridge`` / ``*_p2_response``
functions below are the TRUE quadrupole-channel calibration: P2-weighted
bridge placement (``w_i = 1 + eps P2(cos theta_i)``) read out with ``B``.
"""
from __future__ import annotations

import networkx as nx
import numpy as np

from bh_graph import kerraniso
from bh_graph.orici import (
    BRIDGE_BETA_NEW,
    BRIDGE_BETA_OLD,
    n_bridges_for_pair,
    ollivier_curvature,
    ollivier_curvature_eint,
    p_adj_of_shell,
    shell_pair_radius,
)


def p2_legendre(x):
    """Second Legendre polynomial ``(3x^2 - 1)/2``, elementwise.

    ``p2(1) = 1`` (pole), ``p2(0) = -1/2`` (equator). Non-finite entries map
    to NaN; unparseable input returns NaN (never raises).
    """
    try:
        arr = np.asarray(x, dtype=float)
    except (TypeError, ValueError):
        return float("nan")
    with np.errstate(invalid="ignore", over="ignore"):
        out = (3.0 * arr**2 - 1.0) / 2.0
    out = np.where(np.isfinite(arr), out, np.nan)
    if out.ndim == 0:
        return float(out)
    return out


def attach_latitudes(g, per_shell, n_shells, seed=0):
    """Attach stratified ``cos_theta`` latitudes to shell-graph nodes (in place).

    ``cos_theta_i = 1 - (2i + 1) / per_shell`` for node ``(shell, i)``,
    identical across shells (area-stratified bins). Nodes not of ``(s, i)``
    form are skipped. Returns the same graph object. Bad inputs leave the
    graph unchanged (never raises). ``seed``/``n_shells`` are accepted for
    call-site symmetry; latitudes are deterministic by construction.
    """
    try:
        ps = int(per_shell)
    except (TypeError, ValueError):
        return g
    if ps < 1:
        return g
    try:
        nodes = list(g.nodes())
    except (AttributeError, TypeError):
        return g
    for node in nodes:
        try:
            if not (isinstance(node, tuple) and len(node) == 2):
                continue
            i = node[1]
            if isinstance(i, bool) or not isinstance(i, (int, np.integer)):
                continue
            i = int(i)
            if not 0 <= i < ps:
                continue
            g.nodes[node]["cos_theta"] = 1.0 - (2.0 * i + 1.0) / ps
        except (KeyError, TypeError, IndexError):
            continue
    return g


def edge_p2(g, u, v) -> float:
    """``P2`` of an edge's midpoint latitude: ``p2(mean(cos_theta_u, cos_theta_v))``.

    NaN if either endpoint lacks a finite ``cos_theta`` (never raises).
    """
    try:
        cu = float(g.nodes[u].get("cos_theta"))
        cv = float(g.nodes[v].get("cos_theta"))
    except (KeyError, TypeError, ValueError, AttributeError):
        return float("nan")
    if not (np.isfinite(cu) and np.isfinite(cv)):
        return float("nan")
    return float(p2_legendre((cu + cv) / 2.0))


def radial_edges_with_kappa(g, n_shells, max_per_shellpair=12, e_int=None):
    """Radial edges with exact OR kappa and P2 latitude, per shell-pair.

    Iterates shell-pairs ``s|s+1``; per pair collects up to
    ``max_per_shellpair`` RADIAL edges (endpoints in adjacent shells ``s``,
    ``s+1``, any zone) in graph edge order (``g.edges()`` iteration, i.e.
    insertion order — the first radial edges of each pair encountered win)
    with exact Ollivier-Ricci kappa (Floyd-Warshall cached once) and
    :func:`edge_p2`. ``e_int = None`` uses the uniform measure, otherwise
    the e_int-weighted measure. Returns ``{"r", "kappa", "p2"}`` dicts
    (kappa NaN if its LP fails; empty list on bad inputs — never raises).
    """
    try:
        ns = int(n_shells)
        mp = int(max_per_shellpair)
    except (TypeError, ValueError):
        return []
    if ns < 2 or mp < 1:
        return []
    try:
        dist = nx.floyd_warshall_numpy(g)
        idx = {v: i for i, v in enumerate(g.nodes())}
        edges = list(g.edges())
    except Exception:  # noqa: BLE001 - never-raise: NaN/fallback
        return []
    use_eint = e_int is not None
    rows = []
    for s in range(ns - 1):
        r = float(shell_pair_radius(s, ns))
        kept = 0
        for u, v in edges:
            if kept >= mp:
                break
            try:
                if not (isinstance(u, tuple) and isinstance(v, tuple)):
                    continue
                if len(u) != 2 or len(v) != 2:
                    continue
                if sorted([u[0], v[0]]) != [s, s + 1]:
                    continue
            except TypeError:
                continue
            try:
                if use_eint:
                    kap = ollivier_curvature_eint(g, u, v, e_int, _dist=dist, _idx=idx)
                else:
                    kap = ollivier_curvature(g, u, v, _dist=dist, _idx=idx)
                kap = float(kap)
            except Exception:  # noqa: BLE001 - never-raise: NaN/fallback
                kap = float("nan")
            rows.append({"r": r, "kappa": kap, "p2": edge_p2(g, u, v)})
            kept += 1
    return rows


def p2_amplitude(edge_rows):
    """Pooled normalized OLS slope of ``|kappa|`` on ``P2`` (the ``B`` estimator).

    Keeps rows with finite ``kappa < 0`` and finite ``p2``; per shell-pair
    ``r`` normalizes ``y_e = |k_e| / mean_r(|k|)`` (pairs with fewer than 3
    kept rows or a nonpositive mean are skipped); pools survivors and fits
    ``B = Cov(y, P2) / Var(P2)``. Returns ``{"B": float, "n": int}`` with
    ``B`` NaN when ``Var(P2) == 0`` or pooled ``n < 5`` (never raises).
    """
    try:
        rows = list(edge_rows)
    except TypeError:
        return {"B": float("nan"), "n": 0}
    groups: dict[float, list[tuple[float, float]]] = {}
    for row in rows:
        try:
            r = float(row["r"])
            k = float(row["kappa"])
            p = float(row["p2"])
        except (KeyError, TypeError, ValueError, IndexError):
            continue
        if not (np.isfinite(r) and np.isfinite(k) and k < 0 and np.isfinite(p)):
            continue
        groups.setdefault(r, []).append((abs(k), p))
    ys: list[float] = []
    ps: list[float] = []
    for grp in groups.values():
        if len(grp) < 3:
            continue
        mean = float(np.mean([a for a, _ in grp]))
        if not np.isfinite(mean) or mean <= 0:
            continue
        for a, p in grp:
            ys.append(a / mean)
            ps.append(p)
    n = len(ys)
    if n < 5:
        return {"B": float("nan"), "n": int(n)}
    y = np.array(ys, dtype=float)
    p = np.array(ps, dtype=float)
    if not (np.all(np.isfinite(y)) and np.all(np.isfinite(p))):
        return {"B": float("nan"), "n": int(n)}
    denom = float(np.sum((p - p.mean()) ** 2))
    if not np.isfinite(denom) or denom == 0.0:
        return {"B": float("nan"), "n": int(n)}
    num = float(np.sum((p - p.mean()) * (y - y.mean())))
    if not np.isfinite(num):
        return {"B": float("nan"), "n": int(n)}
    return {"B": float(num / denom), "n": int(n)}


def measure_p2_anisotropy(
    per_shell=15,
    n_shells=6,
    n_graphs=8,
    gradient=True,
    beta=None,
    epsilon_bridge=0.0,
    polar_fraction=0.5,
    seed0=0,
    max_per_shellpair=12,
    e_int=None,
):
    """Measured P2 amplitude ``B`` over ``n_graphs`` at one imposed ``epsilon_bridge``.

    Mirrors :func:`kerraniso.measure_anisotropy` (per-graph ``B`` list,
    mean/std/sem, ``n_ok`` of finite ``B``, bridge polar fractions) but builds
    graphs via ``kerraniso.gradient_shell_graph_latitude``, attaches
    stratified latitudes, and estimates ``B`` per graph with
    :func:`p2_amplitude`. Empty/NaN-tolerant throughout (no exceptions).
    """
    try:
        eps_out = float(epsilon_bridge)
    except (TypeError, ValueError):
        eps_out = 0.0
    if not np.isfinite(eps_out):
        eps_out = 0.0
    try:
        ng = int(n_graphs)
        s0 = int(seed0)
    except (TypeError, ValueError):
        ng, s0 = 0, 0
    per_graph: list[float] = []
    per_graph_n: list[int] = []
    bridge_fracs: list[float] = []
    for t in range(max(ng, 0)):
        try:
            g = kerraniso.gradient_shell_graph_latitude(
                per_shell, n_shells, gradient, beta,
                epsilon_bridge, polar_fraction, s0 + t,
            )
            bridge_fracs.append(kerraniso.bridge_polar_fraction(g, n_shells))
            attach_latitudes(g, per_shell, n_shells)
            rows = radial_edges_with_kappa(g, n_shells, max_per_shellpair, e_int)
            amp = p2_amplitude(rows)
            per_graph.append(float(amp["B"]))
            per_graph_n.append(int(amp["n"]))
        except Exception:  # noqa: BLE001 - never-raise: NaN/fallback
            per_graph.append(float("nan"))
            per_graph_n.append(0)
            bridge_fracs.append(float("nan"))
    per_graph_arr = np.array(per_graph, dtype=float)
    ok = per_graph_arr[np.isfinite(per_graph_arr)]
    return {
        "epsilon_bridge": eps_out,
        "per_graph": per_graph_arr,
        "per_graph_n": np.array(per_graph_n, dtype=int),
        "mean": float(np.mean(ok)) if len(ok) else float("nan"),
        "std": float(np.std(ok)) if len(ok) else float("nan"),
        "sem": float(np.std(ok) / np.sqrt(len(ok))) if len(ok) else float("nan"),
        "n_ok": len(ok),
        "bridge_polar_frac_mean": (
            float(np.nanmean(bridge_fracs)) if len(bridge_fracs) else float("nan")
        ),
    }


def _ols_slope(xs, ys) -> float:
    """OLS slope over finite pairs (NaN if fewer than 2 — never raises)."""
    try:
        x = np.asarray(xs, dtype=float)
        y = np.asarray(ys, dtype=float)
        mask = np.isfinite(x) & np.isfinite(y)
        if int(mask.sum()) < 2:
            return float("nan")
        return float(np.polyfit(x[mask], y[mask], 1)[0])
    except Exception:  # noqa: BLE001 - never-raise: NaN/fallback
        return float("nan")


def p2_curve(eps_grid, **kwargs):
    """Measured P2 amplitude ``B`` vs imposed ``epsilon_bridge`` + linear slope.

    Mirrors :func:`kerraniso.calibration_curve`: ``kwargs`` pass through to
    :func:`measure_p2_anisotropy`; slope is OLS ``dB/d(eps)`` over finite
    points (NaN if fewer than 2 finite). Empty/bad grids yield NaN (no raise).
    """
    try:
        grid = [float(e) for e in list(eps_grid)]
    except (TypeError, ValueError):
        grid = []
    results = []
    for e in grid:
        try:
            results.append(measure_p2_anisotropy(epsilon_bridge=e, **kwargs))
        except Exception:  # noqa: BLE001 - never-raise: NaN/fallback
            fb = dict(kwargs)
            fb["epsilon_bridge"] = e
            fb["n_graphs"] = 0
            try:
                results.append(measure_p2_anisotropy(**fb))
            except Exception:  # noqa: BLE001 - never-raise: NaN/fallback
                results.append({"mean": float("nan"), "sem": float("nan")})
    try:
        means = np.array([float(r["mean"]) for r in results], dtype=float)
        sems = np.array([float(r["sem"]) for r in results], dtype=float)
    except (KeyError, TypeError, ValueError):
        means = np.full(len(results), np.nan)
        sems = np.full(len(results), np.nan)
    return {
        "eps_imposed": grid,
        "b_measured": means,
        "b_sem": sems,
        "eps_measured": means,
        "eps_sem": sems,
        "slope": _ols_slope(grid, means),
        "results": results,
    }


def compare_estimators(eps_grid, **kwargs):
    """Head-to-head: binary ``eps_OR`` vs P2 ``B`` on the SAME graphs per eps.

    Runs ``kerraniso.measure_anisotropy`` (``max_per_zone = 4``) and
    :func:`measure_p2_anisotropy` (``max_per_shellpair = 12``) with matching
    ``seed0``/``per_shell``/``n_shells``/``n_graphs`` so both estimators see
    identical graph draws. ``kwargs`` may override shared params plus
    ``gradient``, ``beta``, ``polar_fraction``, ``e_int``, ``max_per_zone``,
    ``max_per_shellpair``. Slopes are OLS over finite points (NaN if < 2).
    """
    try:
        grid = [float(e) for e in list(eps_grid)]
    except (TypeError, ValueError):
        grid = []
    per_shell = kwargs.get("per_shell", 15)
    n_shells = kwargs.get("n_shells", 6)
    n_graphs = kwargs.get("n_graphs", 8)
    gradient = kwargs.get("gradient", True)
    beta = kwargs.get("beta", None)
    polar_fraction = kwargs.get("polar_fraction", kerraniso.DEFAULT_POLAR_FRACTION)
    seed0 = kwargs.get("seed0", 0)
    e_int = kwargs.get("e_int", None)
    try:
        mpz = int(kwargs.get("max_per_zone", 4))
    except (TypeError, ValueError):
        mpz = 4
    try:
        mpp = int(kwargs.get("max_per_shellpair", 12))
    except (TypeError, ValueError):
        mpp = 12
    b_mean: list[float] = []
    b_sem: list[float] = []
    b_nok: list[int] = []
    p_mean: list[float] = []
    p_sem: list[float] = []
    p_nok: list[int] = []
    for e in grid:
        try:
            rb = kerraniso.measure_anisotropy(
                per_shell=per_shell, n_shells=n_shells, n_graphs=n_graphs,
                gradient=gradient, beta=beta, epsilon_bridge=e,
                polar_fraction=polar_fraction, seed0=seed0,
                max_per_zone=mpz, e_int=e_int,
            )
            b_mean.append(float(rb["mean"]))
            b_sem.append(float(rb["sem"]))
            b_nok.append(int(rb["n_ok"]))
        except Exception:  # noqa: BLE001 - never-raise: NaN/fallback
            b_mean.append(float("nan"))
            b_sem.append(float("nan"))
            b_nok.append(0)
        try:
            rp = measure_p2_anisotropy(
                per_shell=per_shell, n_shells=n_shells, n_graphs=n_graphs,
                gradient=gradient, beta=beta, epsilon_bridge=e,
                polar_fraction=polar_fraction, seed0=seed0,
                max_per_shellpair=mpp, e_int=e_int,
            )
            p_mean.append(float(rp["mean"]))
            p_sem.append(float(rp["sem"]))
            p_nok.append(int(rp["n_ok"]))
        except Exception:  # noqa: BLE001 - never-raise: NaN/fallback
            p_mean.append(float("nan"))
            p_sem.append(float("nan"))
            p_nok.append(0)
    return {
        "eps_imposed": grid,
        "binary_mean": np.array(b_mean, dtype=float),
        "binary_sem": np.array(b_sem, dtype=float),
        "binary_n_ok": [int(v) for v in b_nok],
        "p2_mean": np.array(p_mean, dtype=float),
        "p2_sem": np.array(p_sem, dtype=float),
        "p2_n_ok": [int(v) for v in p_nok],
        "binary_slope": _ols_slope(grid, b_mean),
        "p2_slope": _ols_slope(grid, p_mean),
    }


# ---------------------------------------------------------------------------
# True quadrupole-channel calibration: P2-weighted bridge imposition + B readout.
#
# Unlike the hemispheric index-half zones, node weights w_i = 1 + eps*P2_i are
# EVEN under north/south reflection (caps excess, band deficit for eps > 0),
# i.e. a genuine axisymmetric quadrupole deformation. Validity interval is the
# same open (-1, 2) as kerraniso (P2 in [-1/2, 1] gives identical positivity
# constraints), so kerraniso.is_valid_bridge_eps is reused as the checker.
# ---------------------------------------------------------------------------


def p2_node_weights(per_shell, epsilon):
    """Per-node weights ``w_i = 1 + eps*P2(cos theta_i)`` (stratified latitudes).

    ``eps > 0`` = polar-caps excess, equatorial-band deficit (even parity).
    Returns an empty array for unparseable ``per_shell``; NaN-filled for
    unparseable ``epsilon`` (never raises). Positivity is the caller's
    responsibility (see ``kerraniso.is_valid_bridge_eps``).
    """
    try:
        ps = int(per_shell)
    except (TypeError, ValueError):
        return np.array([])
    if ps < 1:
        return np.array([])
    try:
        e = float(epsilon)
    except (TypeError, ValueError):
        return np.full(ps, np.nan)
    if not np.isfinite(e):
        return np.full(ps, np.nan)
    cos = np.array([1.0 - (2.0 * i + 1.0) / ps for i in range(ps)])
    return 1.0 + e * np.asarray(p2_legendre(cos), dtype=float)


def gradient_shell_graph_p2bridge(
    per_shell: int = 30,
    n_shells: int = 10,
    gradient: bool = True,
    beta: float | None = None,
    epsilon_p2: float = 0.0,
    seed: int = 0,
) -> nx.Graph:
    """Gradient shells with P2-weighted bridge placement (quadrupole channel).

    Intra-shell edges are identical to ``orici.gradient_shell_graph`` (same
    RNG stream). Inter-shell bridges keep the deterministic COUNT per pair
    but endpoints are sampled with pair weights ``w_i*w_j`` from
    :func:`p2_node_weights`. At ``eps = 0`` the code path is exactly
    ``orici``'s (edge sets identical for the same seed). Invalid
    ``epsilon_p2`` falls back to 0.0 (check with
    ``kerraniso.is_valid_bridge_eps``). Nodes carry ``zone`` (index-half,
    for binary-estimator comparison) and ``cos_theta`` attrs.
    """
    if beta is None:
        beta = BRIDGE_BETA_NEW if gradient else BRIDGE_BETA_OLD
    try:
        eps = float(epsilon_p2)
    except (TypeError, ValueError):
        eps = 0.0
    if not kerraniso.is_valid_bridge_eps(eps):
        eps = 0.0
    labels = kerraniso.assign_latitude_labels(per_shell, kerraniso.DEFAULT_POLAR_FRACTION)
    rng = np.random.default_rng(seed)
    g = nx.Graph()
    for s in range(n_shells):
        for i in range(per_shell):
            g.add_node((s, i), zone=labels.get(i, kerraniso.EQUATORIAL))
    attach_latitudes(g, per_shell, n_shells)
    for s in range(n_shells):
        p = p_adj_of_shell(s, gradient)
        for ii in range(per_shell):
            for jj in range(ii + 1, per_shell):
                if rng.random() < p:
                    g.add_edge((s, ii), (s, jj))
    w = p2_node_weights(per_shell, eps)
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


def bridge_p2_mean(g: nx.Graph) -> float:
    """Mean P2 over inter-shell bridge endpoints (imposition check).

    Must rise monotonically with ``epsilon_p2``. NaN if no bridge endpoints
    carry finite latitudes (never raises).
    """
    try:
        edges = list(g.edges())
    except (AttributeError, TypeError):
        return float("nan")
    vals = []
    for u, v in edges:
        try:
            if not (isinstance(u, tuple) and isinstance(v, tuple)):
                continue
            if len(u) != 2 or len(v) != 2 or u[0] == v[0]:
                continue
            for node in (u, v):
                cu = float(g.nodes[node].get("cos_theta"))
                if np.isfinite(cu):
                    vals.append(float(p2_legendre(cu)))
        except (KeyError, TypeError, ValueError, AttributeError):
            continue
    if not vals:
        return float("nan")
    return float(np.mean(vals))


def measure_p2_response(
    per_shell=15,
    n_shells=6,
    n_graphs=8,
    gradient=True,
    beta=None,
    epsilon_p2=0.0,
    seed0=0,
    max_per_shellpair=12,
    e_int=None,
):
    """P2 amplitude ``B`` over ``n_graphs`` at one imposed P2 ``epsilon_p2``.

    Mirrors :func:`measure_p2_anisotropy` keys (per-graph ``B``, mean/std/sem,
    ``n_ok``) but builds graphs with :func:`gradient_shell_graph_p2bridge`
    (true quadrupole-channel imposition). Includes ``bridge_p2_mean`` averaged
    over graphs (imposition check). NaN-tolerant throughout (no exceptions).
    """
    try:
        eps_out = float(epsilon_p2)
    except (TypeError, ValueError):
        eps_out = 0.0
    if not np.isfinite(eps_out):
        eps_out = 0.0
    try:
        ng = int(n_graphs)
        s0 = int(seed0)
    except (TypeError, ValueError):
        ng, s0 = 0, 0
    per_graph: list[float] = []
    impos: list[float] = []
    for t in range(max(ng, 0)):
        try:
            g = gradient_shell_graph_p2bridge(
                per_shell, n_shells, gradient, beta, epsilon_p2, s0 + t
            )
            impos.append(bridge_p2_mean(g))
            rows = radial_edges_with_kappa(g, n_shells, max_per_shellpair, e_int)
            per_graph.append(float(p2_amplitude(rows)["B"]))
        except Exception:  # noqa: BLE001 - never-raise: NaN/fallback
            per_graph.append(float("nan"))
            impos.append(float("nan"))
    arr = np.array(per_graph, dtype=float)
    ok = arr[np.isfinite(arr)]
    return {
        "epsilon_p2": eps_out,
        "per_graph": arr,
        "mean": float(np.mean(ok)) if len(ok) else float("nan"),
        "std": float(np.std(ok)) if len(ok) else float("nan"),
        "sem": float(np.std(ok) / np.sqrt(len(ok))) if len(ok) else float("nan"),
        "n_ok": len(ok),
        "bridge_p2_mean": float(np.nanmean(impos)) if len(impos) else float("nan"),
    }


def p2_response_curve(eps_grid, **kwargs):
    """P2 amplitude ``B`` vs imposed P2 ``epsilon_p2`` + OLS slope.

    Quadrupole-channel analogue of :func:`p2_curve` (kwargs pass through to
    :func:`measure_p2_response`). The slope SIGN here is the key number: under
    the dilution picture (caps bridge excess -> caps |k| deficit) it should be
    NEGATIVE like the hemispheric bridge slope.
    """
    try:
        grid = [float(e) for e in list(eps_grid)]
    except (TypeError, ValueError):
        grid = []
    results = []
    for e in grid:
        try:
            results.append(measure_p2_response(epsilon_p2=e, **kwargs))
        except Exception:  # noqa: BLE001 - never-raise: NaN/fallback
            results.append({"mean": float("nan"), "sem": float("nan")})
    try:
        means = np.array([float(r["mean"]) for r in results], dtype=float)
        sems = np.array([float(r["sem"]) for r in results], dtype=float)
    except (KeyError, TypeError, ValueError):
        means = np.full(len(results), np.nan)
        sems = np.full(len(results), np.nan)
    return {
        "eps_imposed": grid,
        "b_measured": means,
        "b_sem": sems,
        "slope": _ols_slope(grid, means),
        "results": results,
    }
