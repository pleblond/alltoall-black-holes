"""H: Kerr/Newman extension — rotation and charge as wiring budgets.

Question: does spin break A(k) = k lp^2, or just change k at fixed M?
Answer (this module): the area law survives; rotation/charge consume part of
the exterior budget by correlating legs, so k_eff(M, a, Q) < k(M, 0, 0).

Kerr-Newman (G=c=1): r+ = M + sqrt(M^2 - a^2 - Q^2), A = 4 pi (r+^2 + a^2).
  - Schwarzschild (a=Q=0): A = 16 pi M^2 (maximal legs at fixed M).
  - Extremal Kerr (a=M): A = 8 pi M^2 (exactly half the legs).
  - Extremal RN (Q=M): A = 4 pi M^2.

Graph reading: spin orders legs (reduces independent count); charge soaks
legs into flux. The model's distinctive claim remains: A always counts
*effective independent* exterior legs, never N.
"""
from __future__ import annotations

import numpy as np

FOUR_PI = 4.0 * np.pi


def _r_plus(m, a=0.0, q=0.0):
    m = np.asarray(m, dtype=float)
    disc = m**2 - np.asarray(a, dtype=float) ** 2 - np.asarray(q, dtype=float) ** 2
    return m + np.sqrt(np.maximum(disc, 0.0))


def kerr_newman_area(m, a=0.0, q=0.0):
    """Horizon area A = 4 pi (r+^2 + a^2)."""
    r = _r_plus(m, a, q)
    return FOUR_PI * (r**2 + np.asarray(a, dtype=float) ** 2)


def kerr_newman_k(m, a=0.0, q=0.0, lp: float = 1.0):
    """Effective independent exterior legs k_eff = A/lp^2."""
    return np.asarray(kerr_newman_area(m, a, q), dtype=float) / lp**2


def spin_budget_fraction(a, m):
    """Fraction of Schwarzschild legs 'spent' on rotation: 1 - A(M,a)/A(M,0)."""
    a = np.asarray(a, dtype=float)
    m = np.asarray(m, dtype=float)
    ratio = np.asarray(kerr_newman_area(m, a, 0.0)) / np.asarray(kerr_newman_area(m, 0.0, 0.0))
    return 1.0 - ratio


def is_subextremal(m, a=0.0, q=0.0) -> np.ndarray | bool:
    """Boolean check: does (M,a,Q) satisfy the extremality bound a^2+Q^2 <= M^2?"""
    return np.asarray(a) ** 2 + np.asarray(q) ** 2 <= np.asarray(m) ** 2


def is_extremal(m, a=0.0, q=0.0, tol: float = 1e-9) -> bool:
    m = float(np.asarray(m))
    return bool(abs(float(np.asarray(a)) ** 2 + float(np.asarray(q)) ** 2 - m**2) <= tol)
