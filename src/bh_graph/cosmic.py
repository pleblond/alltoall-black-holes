"""AB: Cosmic leg history k(t) + de Sitter scrambling time.

Flat LCDM has a future event horizon r_eh(t) = a(t) int_t^inf dt'/a(t') whose
legs k(t) = 4 pi r_eh^2/lp^2 grow from ~1e122 (t = 1 Gyr) to the de Sitter
value k_dS ~ 1e123 (the late-dS future guarantees convergence from any t, so
a cosmic event horizon exists even in the matter era). Cosmic history in
wiring language: the exterior budget *opens up* from a sliver to its full
1e123 legs as Lambda takes over; the early universe is a nearly-closed
(baby-like) patch that gains its exterior with time. Scale factor analytic:
a(t) = (Om/Ol)^{1/3} sinh^{2/3}(3/2 sqrt(Ol) H0 t).

Second consequence (Susskind's dS scrambling conjecture in our language):
t* = H0^-1 log S_dS ~ 280 Hubble times ~ 4000 Gyr >> 13.8 Gyr. The observable
universe has not had time to scramble — we live inside a young, unscrambled
patch. A falsifiable-flavored corollary: any cosmological observable requiring
a scrambled dS patch is off-limits, and super-horizon correlations must be
primordial (inflationary), never dynamically generated.
"""
from __future__ import annotations

import numpy as np

H0_S = 2.195e-18  # 67.7 km/s/Mpc in s^-1
OM_M = 0.307
OM_L = 1.0 - OM_M
C_M_S = 299792458.0
LP_M = 1.616255e-35
GYR_S = 3600 * 24 * 365.25 * 1e9


def scale_factor(t_s) -> np.ndarray | float:
    t = np.asarray(t_s, dtype=float)
    x = 1.5 * np.sqrt(OM_L) * H0_S * np.maximum(t, 1e-30)
    with np.errstate(over="ignore"):
        out = (OM_M / OM_L) ** (1.0 / 3.0) * np.sinh(np.minimum(x, 700.0)) ** (2.0 / 3.0)
    return out


def event_horizon_meters(t_s, t_max_s: float = 1e13 * GYR_S, n: int = 20000) -> np.ndarray | float:
    """r_eh(t) by trapezoid integration of dt/a from t to t_max (converged if late dS)."""
    t = np.atleast_1d(np.asarray(t_s, dtype=float))
    grid = np.concatenate([np.sort(t), [t_max_s]])
    grid = np.unique(grid[grid <= t_max_s])
    # fine log grid for the tail integral
    fine = np.exp(np.linspace(np.log(max(grid.min(), 1e8)), np.log(t_max_s), n))
    inv_a = 1.0 / scale_factor(fine)
    # cumulative integral from each t: int_t^tmax dt/a
    from scipy.integrate import cumulative_trapezoid

    cum = cumulative_trapezoid(inv_a, fine, initial=0.0)
    total = cum[-1]
    out = []
    for tt in t:
        idx = np.searchsorted(fine, tt)
        val = total - (cum[idx] if idx < len(cum) else total)
        out.append(float(scale_factor(tt) * C_M_S * val))
    out = np.array(out)
    return float(out[0]) if out.size == 1 else out


def cosmic_legs(t_s, **kw) -> np.ndarray | float:
    r = np.asarray(event_horizon_meters(t_s, **kw), dtype=float)
    return 4.0 * np.pi * (r / LP_M) ** 2


def ds_scrambling_gyr(h0_s: float = H0_S) -> float:
    """t* = H^-1 log S_dS in Gyr (S_dS from bh_graph.ds)."""
    from bh_graph.ds import ds_entropy

    s = ds_entropy(h0_s * 5.391247e-44)
    return float(np.log(s) / h0_s / GYR_S)


def universe_scrambled(age_gyr: float = 13.8) -> bool:
    """Boolean check: has the patch had time to scramble? (No.)"""
    return bool(age_gyr >= ds_scrambling_gyr())
