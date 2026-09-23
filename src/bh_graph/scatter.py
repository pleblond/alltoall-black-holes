"""SC: Overmassive-tail scatter toy vs wiring-collapse fraction.

High-z baseline: log M_BH = log M_* - 3 + N(0, 0.3) (local-like ratio with
scatter). Wiring channel (fraction f_w): M_BH drawn log-uniform 1e6-1e9
(independent of host — wiring collapse needs no stars), host M_* log-uniform
1e7-1e9. Observable: overmassive fraction P(M_BH/M_* > 0.1) vs f_w.

Prediction: overmassive tail grows monotonically with f_w from ~0 (baseline
rarely exceeds 0.1 at 3-sigma... baseline mean ratio 1e-3, sigma 0.3 dex ->
P(>0.1) ~ tiny) to O(1) at f_w -> 1. Falsifier: a COMPLETE high-z sample with
zero overmassive outliers drives f_w -> 0 (kills the channel's relevance,
not the core model). Current JWST impression (few-10% UHZ1-like among tens
of AGN) maps to f_w ~ 0.05-0.3 —Illustrative until selection-corrected data.
"""
from __future__ import annotations

import numpy as np


def mock_catalog(n: int = 5000, f_w: float = 0.1, seed: int = 0) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    log_mstar = rng.uniform(7, 9.5, n)
    wiring = rng.random(n) < f_w
    log_mbh = np.empty(n)
    base = ~wiring
    log_mbh[base] = log_mstar[base] - 3.0 + rng.normal(0, 0.3, base.sum())
    log_mbh[wiring] = rng.uniform(6, 9, wiring.sum())
    return {"log_mstar": log_mstar, "log_mbh": log_mbh, "wiring": wiring,
            "ratio": 10.0 ** (log_mbh - log_mstar)}


def overmassive_fraction(cat: dict, threshold: float = 0.1) -> float:
    return float(np.mean(np.asarray(cat["ratio"]) > threshold))


def tail_vs_fw(f_grid, n: int = 5000, seed: int = 0) -> dict[str, np.ndarray]:
    f = np.asarray(list(f_grid), dtype=float)
    tails = [overmassive_fraction(mock_catalog(n, float(fw), seed), 0.1) for fw in f]
    return {"f_w": f, "tail": np.array(tails)}


def fw_required_for_tail(target: float = 0.1, seed: int = 0) -> float:
    """Wiring fraction giving an overmassive tail >= target (scan)."""
    for fw in np.linspace(0, 1, 51):
        if overmassive_fraction(mock_catalog(4000, float(fw), seed)) >= target:
            return float(fw)
    return float("nan")


def tail_slope(seed: int = 0) -> float:
    """Overmassive probability per unit f_w (measured at f_w = 1)."""
    return overmassive_fraction(mock_catalog(6000, 1.0, seed))


def channel_killed_by_null(n_clean: int, relevance: float = 0.05, seed: int = 0) -> bool:
    """Rule-of-three: 0 outliers in n_clean bounds tail < 3/n (95%).

    Kills the channel's relevance if that forces f_w < `relevance`.
    """
    c = tail_slope(seed)
    f_upper = (3.0 / max(n_clean, 1)) / max(c, 1e-9)
    return bool(f_upper < relevance)
