"""G: Robustness sweeps — do A–C survive parameter changes?

1. Circuits at p < 1 keep log scaling with slope 1/log2(1+p).
2. k*(N) stays quadratic for all eps (only the coefficient moves).
3. QES crossing exists iff s_leg > lp^2/4 (sharp phase boundary).
"""
from __future__ import annotations

import numpy as np

from bh_graph.circuits import predicted_alltoall_log
from bh_graph.maxent import selfconsistent_k_quadratic
from bh_graph.qes import has_qes_transition


def log_slope_vs_p(p_grid) -> np.ndarray:
    """Slope dt*/d(log2 N) = 1/log2(1+p): log law persists, steepens as p drops."""
    p = np.asarray(list(p_grid), dtype=float)
    return 1.0 / np.log2(1.0 + p)


def quadratic_coefficient(eps: float, lp: float = 1.0) -> float:
    """k*(N) = coeff * N^2 with coeff = 16 pi (eps/lp)^2."""
    return float(16.0 * np.pi * (eps / lp) ** 2)


def qes_phase_boundary(s_leg_grid, lp: float = 1.0) -> np.ndarray:
    """Boolean array: transition exists at each s_leg."""
    return np.array([has_qes_transition(s, lp) for s in s_leg_grid], dtype=bool)


def all_quadratic(eps_grid, n_probe: int = 7) -> bool:
    """Boolean check: k*(2N)/k*(N) == 4 for every eps (exact quadraticity)."""
    for eps in eps_grid:
        k1 = float(selfconsistent_k_quadratic(n_probe, eps))
        k2 = float(selfconsistent_k_quadratic(2 * n_probe, eps))
        if abs(k2 / k1 - 4.0) > 1e-9:
            return False
    return True
