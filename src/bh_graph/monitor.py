"""KB: Alpha universality monitor — per-event scaffold awaiting O4/O5.

The AG identification predicts a UNIVERSAL healing coefficient: every merger
remnant rings with alpha = tau/M = 11.24 (Schwarzschild; spin corrections via
Kerr QNM tables in a future version). Two kill conditions, pre-registered:

  1. Combined bound kill: hierarchical delta_tau220 excluding 0 at 90%
     (currently [-0.2, +0.1]: alive).
  2. Universality kill: per-event alpha_i scattering beyond measurement noise
     (chi2/dof >> 1 against a common alpha) or trending with mass/spin —
     healing would be environment-dependent, not a wiring constant.

This module implements the verdict machinery on pinned GWTC-3 numbers plus a
registry where future per-event (Mf, tau, sigma_tau) rows drop in; the
chi2 test runs the moment O4/O5 ringdown posteriors land. No data invented:
with zero per-event rows the monitor reports 'awaiting data', never a pass.
"""
from __future__ import annotations

import numpy as np

from bh_graph.healing import QNM_DAMPING_M, alpha_heal_bounds

# Pinned GWTC-3 hierarchical 90% (Abbott et al. 2021, via 2603.16026 compilation).
DTAU_PINNED = (-0.2, 0.1)


def combined_alive(dtau_lo: float = DTAU_PINNED[0], dtau_hi: float = DTAU_PINNED[1]) -> bool:
    """Boolean check: does the combined 90% interval still include GR (0)?"""
    return bool(dtau_lo <= 0.0 <= dtau_hi)


def alpha_from_dtau(dtau: float) -> float:
    return float(QNM_DAMPING_M * (1.0 + dtau))


def universality_chi2(events: list[dict]) -> dict:
    """Inverse-variance chi2 of per-event alpha_i vs common mean.

    events: [{name, mf_msun, tau_s, sigma_s}]. Returns chi2, dof, p-ish
    (survival fraction via chi2 sf), weighted mean alpha. Empty -> awaiting.
    """
    from scipy.stats import chi2 as chi2_dist

    if not events:
        return {"status": "awaiting data", "chi2": None, "dof": 0}
    alphas, sigmas = [], []
    for ev in events:
        m_sec = ev["mf_msun"] * 4.92549095e-6
        alphas.append(ev["tau_s"] / m_sec)
        sigmas.append(ev["sigma_s"] / m_sec)
    a = np.array(alphas)
    w = 1.0 / np.maximum(np.array(sigmas), 1e-300) ** 2
    mean = float(np.sum(w * a) / np.sum(w))
    c2 = float(np.sum(w * (a - mean) ** 2))
    dof = max(len(a) - 1, 1)
    return {"status": "evaluated", "chi2": c2, "dof": dof,
            "p_value": float(chi2_dist.sf(c2, dof)), "mean_alpha": mean,
            "kill": bool(float(chi2_dist.sf(c2, dof)) < 0.01)}


def universality_verdict(events: list[dict]) -> str:
    r = universality_chi2(events)
    if r["status"] == "awaiting data":
        return "awaiting O4/O5 per-event ringdown rows"
    if r["kill"]:
        return "KILL universality (scatter beyond noise)"
    lo, hi = alpha_heal_bounds()
    if not (lo <= r["mean_alpha"] <= hi):
        return "KILL alpha value (mean outside LVK window)"
    return "alive (universal alpha within window)"
