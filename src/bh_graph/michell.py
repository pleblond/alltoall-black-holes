"""BM2: Michell-Laplace radius from entropic Newton + lattice light speed.

The BM reduction shows ``k(M)`` follows iff ``R_s(M)`` is given -- and
``R_s = 2M`` stood as the single GR input. This module replaces that input
with a derivation inside the model's own weak-field sector (Michell 1784,
Laplace 1796):

1.  Entropic Newton gives ``F = G M m/r^2`` (:mod:`bh_graph.entropic`, modulo
    the labelled equipartition + Bekenstein postulates). Integrating the
    model's own force from ``r`` to infinity yields ``Phi = -GM/r``, hence
    escape velocity ``v_esc = sqrt(2GM/r)`` by energy conservation
    (``v^2/2 + Phi = 0``) -- the force-to-potential-to-velocity chain is
    tested numerically, not asserted.
2.  Lattice walks propagate at fixed speed ``c`` (low-energy group velocity,
    :mod:`bh_graph.dispersion`; ``c = 1`` in Planck units).
3.  Michell bridge assumption (LABELLED, the one new postulate here): a light
    corpuscle escapes iff the Newtonian escape velocity is below ``c``. The
    trapping surface ``v_esc = c`` then sits at ``R = 2GM/c^2``.

This is famously the right radius for the wrong reason in GR textbooks; here
its status is explicit: one scalar escape condition replaces the imported
Schwarzschild metric tensor (no coordinates, no ``g_munu``). What it does NOT
do: derive the equipartition/Bekenstein postulates behind Newton, the
corpuscular escape assumption itself, or any full metric -- only the radius.
``k(M)`` computed through the Michell radius coincides with the GR-consistent
map to machine precision (same numbers, GR-free provenance).
"""

from __future__ import annotations

import numpy as np

from bh_graph.entropic import newton_force
from bh_graph.horizon import PATCH_AREA

FOUR_PI = 4.0 * np.pi


def is_valid_michell_args(r: float, m: float) -> bool:
    """Boolean check: positive finite radius and central mass?"""
    return bool(np.isfinite(r) and np.isfinite(m) and r > 0 and m > 0)


def escape_potential(r: float, m_central: float, g_newton: float = 1.0) -> float:
    """Newtonian potential ``Phi = -GM/r`` (integral of the entropic force)."""
    if not is_valid_michell_args(r, m_central) or not np.isfinite(g_newton):
        return float("nan")
    return float(-g_newton * m_central / r)


def escape_velocity(r, m_central: float, g_newton: float = 1.0):
    """Escape velocity ``v_esc = sqrt(2GM/r)`` from energy conservation.

    Scalar in, scalar out; array ``r`` gives an array (nan where invalid).
    """
    scalar = np.ndim(r) == 0
    rr = np.atleast_1d(np.asarray(r, dtype=float))
    out = np.full_like(rr, np.nan)
    if np.isfinite(m_central) and m_central > 0 and np.isfinite(g_newton) and g_newton > 0:
        ok = np.isfinite(rr) & (rr > 0)
        out[ok] = np.sqrt(2.0 * g_newton * m_central / rr[ok])
    if scalar:
        return float(out[0])
    return out


def potential_from_force_integral(r: float, m_central: float, g_newton: float = 1.0) -> float:
    """Numerically integrate the model's force: ``-int_r^inf F dr`` (unit mass).

    Must reproduce :func:`escape_potential` -- this is the tested link showing
    the escape velocity genuinely descends from entropic Newton.
    """
    from scipy.integrate import quad

    if not is_valid_michell_args(r, m_central) or not np.isfinite(g_newton):
        return float("nan")

    def f(rr):
        return float(newton_force(m_central, 1.0, rr, g_newton=g_newton))

    val, _ = quad(f, r, np.inf, limit=200)
    return float(-val)


def is_light_trapped(r: float, m_central: float, c_light: float = 1.0) -> bool:
    """Boolean check: Michell trapping (``v_esc >= c``) at this radius?"""
    if not is_valid_michell_args(r, m_central):
        return False
    if not (np.isfinite(c_light) and c_light > 0):
        return False
    return bool(escape_velocity(r, m_central) >= c_light)


def michell_radius(m_central: float, g_newton: float = 1.0, c_light: float = 1.0) -> float:
    """Michell radius ``R = 2GM/c^2``: the ``v_esc = c`` surface. nan if invalid."""
    if not (np.isfinite(m_central) and m_central > 0):
        return float("nan")
    if not (np.isfinite(g_newton) and np.isfinite(c_light)) or g_newton <= 0 or c_light <= 0:
        return float("nan")
    return float(2.0 * g_newton * m_central / c_light**2)


def is_michell_radius(r: float, m_central: float, tol: float = 1e-9) -> bool:
    """Boolean check: is ``r`` the Michell radius of ``M`` (within ``tol``)?"""
    if not (np.isfinite(tol) and tol > 0):
        return False
    expect = michell_radius(m_central)
    if not (np.isfinite(r) and np.isfinite(expect)):
        return False
    return bool(abs(r - expect) <= tol * max(expect, 1e-300))


def k_from_michell(m_central: float, lp: float = 1.0) -> float:
    """Leg count through the Michell radius: ``k = 4 pi R^2/PATCH`` (no GR input)."""
    r = michell_radius(m_central)
    if not (np.isfinite(r) and np.isfinite(lp)) or lp <= 0:
        return float("nan")
    return float(FOUR_PI * r**2 / (PATCH_AREA * lp**2))


def michell_vs_gr_map_deviation(m_grid) -> float:
    """Max relative |k_michell - k_grmap|/k_grmap: same numbers, new provenance.

    Compares against :func:`bh_graph.horizon.k_from_mass_schwarzschild`; must
    be ~0 (machine precision). The formulas coincide -- the point is that the
    left side never imports the Schwarzschild radius.
    """
    from bh_graph.horizon import k_from_mass_schwarzschild

    m = np.atleast_1d(np.asarray(list(m_grid), dtype=float))
    if m.size == 0 or not np.all(np.isfinite(m)) or np.any(m <= 0):
        return float("nan")
    k_m = np.array([k_from_michell(v) for v in m])
    k_g = np.atleast_1d(np.asarray(k_from_mass_schwarzschild(m), dtype=float))
    if not (np.all(np.isfinite(k_m)) and np.all(np.isfinite(k_g))) or np.any(k_g <= 0):
        return float("nan")
    return float(np.max(np.abs(k_m - k_g) / k_g))
