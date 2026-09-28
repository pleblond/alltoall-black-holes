"""D2 Route B calibration: IMPOSED chiral bias -> azimuthal drift (frame-dragging channel).

STATUS — READ FIRST. This module derives NOTHING about Kerr frame dragging
from the graph. It is the Route B "first computable" from
``docs/kerr-multipoles-exploration.md`` section 4: impose a directed
azimuthal overlay on the weak-field grid+hub graph (``weakfield``), run
directed random walks, and fit the induced equatorial circulation against
the Lense-Thirring rate ``Omega_LT = 2J/r^3``
(``kerrquad.lense_thirring_omega``). The bias ``b`` is PUT IN BY HAND, so any
match is a calibration curve (required ``b`` vs ``J``), not a derivation.

Null hypothesis: a UNIFORM bias plausibly gives an r-INDEPENDENT drift per
step (radial exponent ~0, flat), not the differential ``1/r^3`` rotation of
Lense-Thirring. A radially-weighted ``b(r) ~ 1/r^3`` would be needed to mimic
the GR profile -- which reintroduces "what sets the profile" and is a fit,
not a derivation, unless the profile emerges from dynamics.
``fit_drift_exponent`` reports whatever exponent comes out; only the EXPONENT
comparison against -3 is meaningful (drift units are radians-per-walk-step,
not geometric rates, so amplitudes do not compare to ``Omega_LT`` directly).

Conventions: never raise on bad inputs (NaN/False/fallback + ``is_valid_*``
checkers, following ``kerrquad``); deterministic seeds throughout.
"""
from __future__ import annotations

import numpy as np

from bh_graph.weakfield import weak_field_graph

#: Cylindrical radius below which the azimuthal direction is undefined.
R_PERP_FLOOR = 1e-9

#: Floor for directed weights (no zeros/negatives, keeps rows normalizable).
W_MIN = 1e-9

#: Kwargs of drift_profile that bias_response forwards.
_PROFILE_KWARGS = ("L", "n_stubs", "mode", "seed", "n_steps", "n_walks", "tol")


def is_valid_bias(b) -> bool:
    """Boolean check: finite bias in the open interval (-1, 1)?

    Strict bounds keep both directed weights ``1 +- b`` positive.
    """
    try:
        f = float(np.asarray(b, dtype=float))
    except (TypeError, ValueError):
        return False
    return bool(np.isfinite(f) and -1.0 < f < 1.0)


def _as_vec(p):
    """Finite 3-vector or None (never raises)."""
    try:
        v = np.asarray(p, dtype=float)
    except (TypeError, ValueError):
        return None
    if v.shape != (3,) or not np.all(np.isfinite(v)):
        return None
    return v


def _phi_of(p):
    """Azimuthal angle atan2(y, x), or None if undefined (on-axis/missing)."""
    v = _as_vec(p)
    if v is None:
        return None
    if float(np.hypot(v[0], v[1])) < R_PERP_FLOOR:
        return None
    return float(np.arctan2(v[1], v[0]))


def chiral_weights(g, pos, bias=0.0):
    """Directed weights ``1 +- b*(phi_hat_mid . e_uv)`` for each grid edge.

    For every undirected edge (u, v): ``w(u->v) = 1 + b*s`` and
    ``w(v->u) = 1 - b*s`` with ``s = phi_hat_mid . e_uv``, where ``e_uv`` is
    the unit vector from ``pos[u]`` to ``pos[v]``, ``mid`` is the edge
    midpoint, and ``phi_hat_mid`` is the azimuthal unit around the z-axis at
    ``mid``. On-axis edges (``r_perp < 1e-9``), zero-length edges, or edges
    with an endpoint missing from ``pos`` get weight 1.0 (no bias). Invalid
    bias (see :func:`is_valid_bias`) falls back to 0.0, i.e. all-ones.
    Weights are clamped below at 1e-9 (never zero/negative).
    """
    b = bias if is_valid_bias(bias) else 0.0
    b = float(np.asarray(b, dtype=float))
    weights = {}
    try:
        edges = list(g.edges())
    except Exception:  # noqa: BLE001 - never-raise: NaN/fallback
        return {}
    pmap = pos if isinstance(pos, dict) else {}
    for u, v in edges:
        w_uv, w_vu = 1.0, 1.0
        if b != 0.0:
            pu = _as_vec(pmap.get(u))
            pv = _as_vec(pmap.get(v))
            if pu is not None and pv is not None:
                mid = 0.5 * (pu + pv)
                r_perp = float(np.hypot(mid[0], mid[1]))
                d = pv - pu
                nrm = float(np.linalg.norm(d))
                if r_perp >= R_PERP_FLOOR and nrm > 0.0 and np.isfinite(nrm):
                    phi_hat = np.array([-mid[1], mid[0], 0.0]) / r_perp
                    s = float(np.dot(phi_hat, d / nrm))
                    if np.isfinite(s):
                        w_uv = max(1.0 + b * s, W_MIN)
                        w_vu = max(1.0 - b * s, W_MIN)
        weights[(u, v)] = float(w_uv)
        weights[(v, u)] = float(w_vu)
    return weights


def transition_probs(g, weights):
    """Row-normalized directed transition probabilities from weights.

    Returns ``{u: (neighbors_list, prob_array)}`` with
    ``neighbors = list(g.neighbors(u))`` and probabilities proportional to
    ``weights[(u, v)]``. Missing keys default to 1.0; non-finite or
    non-positive weights are sanitized to 1.0. Empty/isolated nodes get
    ``([], [])``.
    """
    out = {}
    try:
        nodes = list(g.nodes())
    except Exception:  # noqa: BLE001 - never-raise: NaN/fallback
        return {}
    wmap = weights if isinstance(weights, dict) else {}
    for u in nodes:
        try:
            nbrs = list(g.neighbors(u))
        except Exception:  # noqa: BLE001 - never-raise: NaN/fallback
            out[u] = ([], [])
            continue
        if not nbrs:
            out[u] = ([], [])
            continue
        ws = []
        for v in nbrs:
            try:
                wv = float(wmap.get((u, v), 1.0))
            except (TypeError, ValueError):
                wv = 1.0
            if not np.isfinite(wv) or wv <= 0.0:
                wv = 1.0
            ws.append(wv)
        tot = float(sum(ws))
        if not np.isfinite(tot) or tot <= 0.0:
            out[u] = (nbrs, np.full(len(nbrs), 1.0 / len(nbrs)))
        else:
            out[u] = (nbrs, np.asarray(ws, dtype=float) / tot)
    return out


def equatorial_ring(g, pos, r_target, tol=0.6, z_tol=0.6):
    """Grid nodes (3-tuples only) on the equatorial ring at ``r_target``.

    Keeps nodes with ``| |pos| - r_target | < tol`` and ``|z| < z_tol``.
    Hub/stub string nodes are excluded. Returns [] if none (never raises).
    """
    try:
        rt = float(np.asarray(r_target, dtype=float))
        t = float(np.asarray(tol, dtype=float))
        zt = float(np.asarray(z_tol, dtype=float))
    except (TypeError, ValueError):
        return []
    if not (np.isfinite(rt) and np.isfinite(t) and np.isfinite(zt)):
        return []
    try:
        nodes = list(g.nodes())
    except Exception:  # noqa: BLE001 - never-raise: NaN/fallback
        return []
    pmap = pos if isinstance(pos, dict) else {}
    out = []
    for v in nodes:
        if not (isinstance(v, tuple) and len(v) == 3):
            continue
        p = _as_vec(pmap.get(v))
        if p is None:
            continue
        if abs(float(np.linalg.norm(p)) - rt) < t and abs(float(p[2])) < zt:
            out.append(v)
    return out


def azimuthal_drift(g, pos, weights, start, n_steps=200, n_walks=100, seed=0):
    """Mean azimuthal drift (rad per step) of directed walks from ``start``.

    Each walk follows :func:`transition_probs`, accumulating wrapped dphi in
    [-pi, pi] from consecutive ``arctan2(y, x)`` angles. Stepping onto an
    on-axis node (hub at origin: angle undefined) ENDS that walk, keeping its
    partial phi trace with its own step count. Walks with < 2 angled samples
    are skipped. ``drift`` is the mean over used walks of
    ``total_dphi / n_dphi_steps``; ``sem = std / sqrt(n)``. Returns NaN drift
    with ``n == 0`` if ``start`` is unknown, has no defined angle, or no
    walk yields >= 2 angled samples (never raises).
    """
    nan_out = {"drift": float("nan"), "sem": float("nan"), "n": 0}
    try:
        n_steps = int(n_steps)
        n_walks = int(n_walks)
    except (TypeError, ValueError):
        return dict(nan_out)
    if n_steps <= 0 or n_walks <= 0:
        return dict(nan_out)
    try:
        in_graph = start in g.nodes()
    except Exception:  # noqa: BLE001 - never-raise: NaN/fallback
        return dict(nan_out)
    if not in_graph:
        return dict(nan_out)
    pmap = pos if isinstance(pos, dict) else {}
    phi0 = _phi_of(pmap.get(start))
    if phi0 is None:
        return dict(nan_out)
    trans = transition_probs(g, weights)
    try:
        rng = np.random.default_rng(seed)
    except Exception:  # noqa: BLE001 - never-raise: NaN/fallback
        rng = np.random.default_rng(0)
    rates = []
    for _ in range(n_walks):
        cur = start
        phis = [phi0]
        for _ in range(n_steps):
            entry = trans.get(cur)
            if entry is None:
                break
            nbrs, probs = entry
            if len(nbrs) == 0:
                break
            try:
                pick = np.asarray(probs, dtype=float)
                nxt = nbrs[int(rng.choice(len(nbrs), p=pick))]
            except Exception:  # noqa: BLE001 - never-raise: NaN/fallback
                break
            ph = _phi_of(pmap.get(nxt))
            if ph is None:
                break
            cur = nxt
            phis.append(ph)
        if len(phis) < 2:
            continue
        dphi = np.diff(np.asarray(phis, dtype=float))
        dphi = (dphi + np.pi) % (2.0 * np.pi) - np.pi
        rates.append(float(np.sum(dphi)) / len(dphi))
    if not rates:
        return dict(nan_out)
    arr = np.asarray(rates, dtype=float)
    sem = float(np.std(arr) / np.sqrt(len(arr)))
    return {"drift": float(np.mean(arr)), "sem": sem, "n": len(arr)}


def drift_profile(r_targets, L=9, n_stubs=40, mode="direct", bias=0.3, seed=0,
                  n_steps=200, n_walks=100, tol=0.6):
    """Per-radius drift entries from ONE graph with weights computed once.

    Builds ``weak_field_graph(L, n_stubs, mode, seed)``, computes
    :func:`chiral_weights` once, then for each ``r_target`` averages
    :func:`azimuthal_drift` over up to 4 :func:`equatorial_ring` starts
    (seeded ``seed + start_index``). Combined ``sem`` propagates the
    per-start SEMs (mean-of-means variance). Empty rings give NaN entries
    (never raises).
    """
    nan_entry = {"drift": float("nan"), "sem": float("nan"), "n": 0}
    try:
        rts = list(r_targets)
    except TypeError:
        return {}
    try:
        g, pos = weak_field_graph(L, n_stubs, mode, seed)
    except Exception:  # noqa: BLE001 - never-raise: NaN/fallback
        out = {}
        for r in rts:
            try:
                out[r] = dict(nan_entry)
            except TypeError:
                continue
        return out
    try:
        w = chiral_weights(g, pos, bias=bias)
    except Exception:  # noqa: BLE001 - never-raise: NaN/fallback
        w = {}
    try:
        s0 = int(seed)
    except (TypeError, ValueError):
        s0 = 0
    out = {}
    for r in rts:
        try:
            hash(r)
        except TypeError:
            continue
        try:
            starts = sorted(equatorial_ring(g, pos, r, tol=tol))[:4]
        except Exception:  # noqa: BLE001 - never-raise: NaN/fallback
            starts = []
        if not starts:
            out[r] = dict(nan_entry)
            continue
        drifts, sems, ns = [], [], []
        for i, st in enumerate(starts):
            try:
                res = azimuthal_drift(g, pos, w, st, n_steps=n_steps,
                                      n_walks=n_walks, seed=s0 + i)
            except Exception:  # noqa: BLE001 - never-raise: NaN/fallback
                res = None
            if res is None:
                continue
            try:
                d = float(np.asarray(res.get("drift", np.nan), dtype=float))
                s = float(np.asarray(res.get("sem", np.nan), dtype=float))
                n = int(res.get("n", 0))
            except (TypeError, ValueError):
                continue
            if np.isfinite(d) and n > 0:
                drifts.append(d)
                sems.append(s)
                ns.append(n)
        if not drifts:
            out[r] = dict(nan_entry)
            continue
        k = len(drifts)
        fin = [s for s in sems if np.isfinite(s)]
        if fin:
            sem = float(np.sqrt(sum(s * s for s in fin)) / len(fin))
        elif k > 1:
            sem = float(np.std(drifts) / np.sqrt(k))
        else:
            sem = float("nan")
        out[r] = {"drift": float(np.mean(drifts)), "sem": sem,
                  "n": int(sum(ns))}
    return out


def fit_drift_exponent(profile):
    """OLS fit ``log|drift| = log_amp + exponent*log(r)`` over valid entries.

    Uses r entries with finite nonzero drift (need >= 2, else NaNs).
    Compare ``exponent`` to -3 (Lense-Thirring); a uniform bias is expected
    to give ~0 (flat). Reports honestly whatever comes out (never raises).
    """
    nan_out = {"exponent": float("nan"), "log_amp": float("nan"),
               "r2": float("nan")}
    try:
        items = list(profile.items())
    except (AttributeError, TypeError):
        return dict(nan_out)
    xs, ys = [], []
    for r, entry in items:
        try:
            lr = float(np.asarray(r, dtype=float))
            raw = entry.get("drift", np.nan) if isinstance(entry, dict) else entry
            dv = float(np.asarray(raw, dtype=float))
        except (TypeError, ValueError):
            continue
        if np.isfinite(lr) and lr > 0 and np.isfinite(dv) and dv != 0.0:
            xs.append(np.log(lr))
            ys.append(np.log(abs(dv)))
    if len(xs) < 2:
        return dict(nan_out)
    try:
        x = np.asarray(xs, dtype=float)
        y = np.asarray(ys, dtype=float)
        slope, intercept = np.polyfit(x, y, 1)
        yhat = slope * x + intercept
        ss_res = float(np.sum((y - yhat) ** 2))
        ss_tot = float(np.sum((y - np.mean(y)) ** 2))
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
        return {"exponent": float(slope), "log_amp": float(intercept),
                "r2": float(r2)}
    except Exception:  # noqa: BLE001 - never-raise: NaN/fallback
        return dict(nan_out)


def bias_response(bias_grid, r_target=2.5, **kwargs):
    """Linearity check: drift vs bias at fixed radius (one graph per bias).

    Returns ``{"biases", "drifts", "sems", "slope"}`` where ``slope`` is the
    OLS drift-vs-bias slope over finite points (NaN if < 2 usable, or if the
    biases have zero spread). Extra kwargs (L, n_stubs, mode, seed, n_steps,
    n_walks, tol) pass to :func:`drift_profile`; unknown kwargs are ignored.
    Non-floatable or non-finite grid entries are skipped (never raises).
    """
    try:
        grid = list(bias_grid)
    except TypeError:
        return {"biases": [], "drifts": [], "sems": [],
                "slope": float("nan")}
    try:
        hash(r_target)
        hashable_rt = True
    except TypeError:
        hashable_rt = False
    kw = {k: v for k, v in kwargs.items() if k in _PROFILE_KWARGS}
    biases, drifts, sems = [], [], []
    for b in grid:
        try:
            bf = float(np.asarray(b, dtype=float))
        except (TypeError, ValueError):
            continue
        if not np.isfinite(bf):
            continue
        try:
            prof = drift_profile([r_target], bias=bf, **kw)
            entry = prof.get(r_target, {}) if hashable_rt else {}
            d = float(np.asarray(entry.get("drift", np.nan), dtype=float))
            s = float(np.asarray(entry.get("sem", np.nan), dtype=float))
        except Exception:  # noqa: BLE001 - never-raise: NaN/fallback
            d, s = float("nan"), float("nan")
        biases.append(bf)
        drifts.append(d)
        sems.append(s)
    slope = float("nan")
    pts = [(b, d) for b, d in zip(biases, drifts)
           if np.isfinite(b) and np.isfinite(d)]
    if len(pts) >= 2:
        try:
            bx = np.array([p[0] for p in pts], dtype=float)
            dy = np.array([p[1] for p in pts], dtype=float)
            if np.std(bx) > 0:
                slope = float(np.polyfit(bx, dy, 1)[0])
        except Exception:  # noqa: BLE001 - never-raise: NaN/fallback
            slope = float("nan")
    return {"biases": biases, "drifts": drifts, "sems": sems, "slope": slope}
