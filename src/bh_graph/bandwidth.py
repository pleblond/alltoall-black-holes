"""BC: Last-leg bandwidth — the baby must be born empty.

No-cloning constraint on pinch-off: if radiation holds the interior's S0 bits
(post-Page) AND a k=0 baby also held them, quantum information would clone.
Consistent story: legs carry info out as they're cut (s_leg bits per cut, the
Appendix C bulk entropy per leg); evacuation completes before pinch-off iff
total capacity covers S0:

    remaining(k) = S0 - (k0 - k) s_leg;   clean iff remaining(0) <= 0.

Info per remaining leg I(k) = remaining/k peaks mid-evaporation and drains to
0 in clean cases; it diverges as k -> 0 if and only if evacuation FAILS
(remaining(0) > 0 with nowhere to go) — divergence is the diagnostic of
cloning risk, not a generic feature. With k* ~ N^2 (Appendix B) and
S0 ~ N, capacity exceeds content by ~N: evacuation is easy, and the baby
pinches off in vacuum. Adversarial case (tiny s_leg): remaining(0) > 0 flags
'cloning risk' — pinch-off forbidden until more info flows (the dynamical
stall behind 'why would the last leg cut?').
"""
from __future__ import annotations

import numpy as np


def remaining_info(k, s0: float, s_leg: float, k0: float) -> np.ndarray | float:
    k = np.asarray(k, dtype=float)
    return np.maximum(s0 - (k0 - k) * s_leg, 0.0)


def info_per_leg(k, s0: float, s_leg: float, k0: float) -> np.ndarray | float:
    k = np.asarray(k, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.where(k > 0, remaining_info(k, s0, s_leg, k0) / np.maximum(k, 1e-300), np.inf)
    if out.ndim == 0:
        return float(out)
    return out


def evacuates_cleanly(s0: float, s_leg: float, k0: float) -> bool:
    """Boolean check: all S0 bits out by the time k hits 0?"""
    return bool(k0 * s_leg >= s0)


def baby_inventory(s0: float, s_leg: float, k0: float) -> str:
    """'empty' (consistent pinch-off) or 'cloning risk' (stall required)."""
    return "empty" if evacuates_cleanly(s0, s_leg, k0) else "cloning risk"


def evacuation_trajectory(s0: float, s_leg: float, k0: float, n: int = 200) -> dict[str, np.ndarray]:
    k = np.linspace(k0, 0, n)
    return {"k": k, "remaining": np.asarray(remaining_info(k, s0, s_leg, k0), dtype=float),
            "per_leg": np.asarray(info_per_leg(np.maximum(k, 1e-9), s0, s_leg, k0), dtype=float)}
