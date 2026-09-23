"""N: Kerr Page curve with evolving spin budget.

Evaporation sheds spin faster than mass (Page 1976: superradiance + lopsided
emission spin holes down). Toy trajectories over lifetime T:

    M(t) = M0 (1 - t/T)^{1/3},   J(t) = J0 (1 - t/T)^p  (p > 2/3 => spins down),

a(t) = J/M clipped to M. Bekenstein-Hawking S_BH(t) = A(M,a)/4 falls; naive
Hawking radiation entropy grows as S_naive(t) = g (S0 - S_BH(t)) with greybody
factor g ~ 1.48; island candidate S_isl(t) = S_BH(t). Physical:

    S_phys(t) = min(S_naive(t), S_isl(t)).

Result: high initial spin => smaller S0 at fixed M => lower Page peak, and
spin-shedding initially *grows* area (lower a at fixed M means bigger A),
partially offsetting mass-loss shrinkage => *later* turnover. Spin is a second
exterior budget that visibly moves the curve (lower + later).
"""
from __future__ import annotations

import numpy as np

from bh_graph.kerr import kerr_newman_area


def trajectories(
    m0: float, a0_ratio: float = 0.0, steps: int = 200, p_spin: float = 1.2
) -> dict[str, np.ndarray]:
    """M(t), a(t), S_BH(t) over t in [0, 1] (fraction of lifetime)."""
    t = np.linspace(0, 1, steps + 1)
    m = m0 * np.maximum(1.0 - t, 0.0) ** (1.0 / 3.0)
    j0 = a0_ratio * m0 * m0
    j = j0 * np.maximum(1.0 - t, 0.0) ** p_spin
    a = np.divide(j, np.maximum(m, 1e-12), out=np.zeros_like(j), where=m > 1e-12)
    a = np.minimum(a, m)  # cosmic censorship clip
    s_bh = np.asarray(kerr_newman_area(m, a, 0.0), dtype=float) / 4.0
    return {"t": t, "M": m, "a": a, "S_BH": s_bh}


def kerr_page(
    m0: float, a0_ratio: float = 0.0, steps: int = 200, p_spin: float = 1.2,
    greybody: float = 1.48,
) -> dict[str, np.ndarray]:
    """Naive, island, and physical radiation entropy + turnover index."""
    tr = trajectories(m0, a0_ratio, steps, p_spin)
    s0 = float(tr["S_BH"][0])
    s_naive = greybody * (s0 - tr["S_BH"])
    s_isl = tr["S_BH"]
    s_phys = np.minimum(s_naive, s_isl)
    out = dict(tr)
    out.update({"S_naive": s_naive, "S_isl": s_isl, "S_phys": s_phys, "S0": s0})
    return out


def page_time_fraction(pg: dict) -> float:
    """t/T at peak S_phys."""
    i = int(np.argmax(pg["S_phys"]))
    return float(pg["t"][i])


def peak_entropy(pg: dict) -> float:
    return float(np.max(pg["S_phys"]))
