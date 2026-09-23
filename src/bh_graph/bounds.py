"""AE: Remnant-required-beta vs published evaporation bounds (public data).

Vendored PBHbounds curves (Bradley Kavanagh, BSD; see data/pbhbounds/) give
f_PBH upper limits vs mass. We convert to initial-fraction beta(M) from first
principles (monochromatic, horizon-mass formation M = gamma M_H with
gamma = 0.2, radiation domination, Planck15: Omega_DM h^2 = 0.12,
Omega_rad h^2 = 4.15e-5):

    beta = f_PBH (Omega_DM/Omega_rad) (T0/T_form),
    T_form from t_form = G M/(gamma c^3), T(t) = 1 MeV (t/1s)^-1/2.

Overlay: remnant-DM required beta (bh_graph.remnant) vs the min-envelope of
converted bounds across 1e9-1e17 g. Verdict metric: required/bound ratio;
>> conceivable O(1-1e3) systematics (gamma, g*, convention) means exclusion
is robust, not marginal.
"""
from __future__ import annotations

from pathlib import Path
import numpy as np

BOUNDS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "pbhbounds"
M_SUN_G = 1.98847e33
GAMMA = 0.2
OM_DM_H2 = 0.12
OM_RAD_H2 = 4.15e-5
T0_EV = 2.35e-4  # CMB temperature today
G_CGS = 6.67430e-8
C_CGS = 2.99792458e10


def t_form_s(m_g: float) -> float:
    """Horizon-mass formation time t = G M/(gamma c^3)."""
    return float(G_CGS * m_g / (GAMMA * C_CGS**3))


def t_form_temp_ev(m_g: float) -> float:
    return float(1e6 * (t_form_s(m_g) / 1.0) ** -0.5)


def f_to_beta(f_pbh, m_g) -> np.ndarray | float:
    """beta(M) = f_PBH (Omega_DM/Omega_rad) (T0/T_form)."""
    f = np.asarray(f_pbh, dtype=float)
    m = np.asarray(m_g, dtype=float)
    tf = np.array([t_form_temp_ev(float(x)) for x in np.atleast_1d(m)])
    out = f * (OM_DM_H2 / OM_RAD_H2) * (T0_EV / tf)
    if out.ndim == 0:
        return float(out)
    return out


def load_bound(name: str) -> tuple[np.ndarray, np.ndarray]:
    """(M [g], f_PBH upper) from a vendored file (comments skipped)."""
    m_sun, f = np.loadtxt(BOUNDS_DIR / f"{name}.txt", unpack=True)
    return np.asarray(m_sun) * M_SUN_G, np.asarray(f)


def bound_envelope_beta(names, m_grid_g) -> np.ndarray:
    """Min over bounds of converted beta_upper, interpolated on m_grid."""
    m_grid = np.asarray(list(m_grid_g), dtype=float)
    env = np.full_like(m_grid, np.inf)
    for name in names:
        m, f = load_bound(name)
        beta = f_to_beta(f, m)
        ok = np.isfinite(beta) & (beta > 0)
        env = np.minimum(env, np.interp(m_grid, m[ok], beta[ok], left=np.inf, right=np.inf))
    return env


EVAPORATION_BOUNDS = ["EGRB", "Voyager", "INTEGRAL", "SuperK", "CMBevap", "511keV", "Comptel"]


def remnant_exclusion_ratio(m_grid_g) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(required_beta, bound_beta, ratio) across masses."""
    from bh_graph.remnant import required_beta_for_dm

    m = np.asarray(list(m_grid_g), dtype=float)
    req = np.array([required_beta_for_dm(float(x)) for x in m])
    bound = bound_envelope_beta(EVAPORATION_BOUNDS, m)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = req / bound
    return req, bound, ratio


def remnant_ruled_out_everywhere(m_grid_g, margin: float = 1e3) -> bool:
    """Boolean check: required exceeds bound by > margin at every covered mass?"""
    _, _, ratio = remnant_exclusion_ratio(m_grid_g)
    finite = ratio[np.isfinite(ratio)]
    return bool(len(finite) > 0 and np.all(finite > margin))
