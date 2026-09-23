"""PS: Press-Schechter abundance check for hidden giants (kill-capable).

If delocalized giants trace collapsed halos, their number density cannot
exceed the halo supply: n_giants <= n_halos(>M_host, z). Required density
from LRD abundances: n_req ~ 1e-5 Mpc^-3 (fiducial, decade band either way).
Halo supply from Press-Schechter with exact flat-LCDM growth D(z) and
sigma(M,z) = D(z) sigma8 (M/M8)^-gamma, fiducial gamma = 0.16 anchored to
M* today (sigma(M*)=delta_c), sensitivity gamma in [0.12, 0.22].

Two readings, both stated: (i) giants-trace-halos -> the check can KILL the
scenario if required >> supply across the band; (ii) primordial-independent
giants -> this check is inapplicable and CMB/lensing bounds (not computed
here) are the live constraint instead.
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import quad
from scipy.special import erfc

OM_M = 0.307
OM_L = 1.0 - OM_M
SIGMA8 = 0.81
DELTA_C = 1.686
RHO_CRIT_MSUN_MPC3 = 2.775e11 * 0.677**2
RHO_M = OM_M * RHO_CRIT_MSUN_MPC3
M8_MSUN = 4.0 / 3.0 * np.pi * (8.0 / 0.677) ** 3 * RHO_M
N_REQ_FIDUCIAL = 1e-5  # Mpc^-3, LRD-order abundance


def growth_factor(z: float) -> float:
    """Exact linear growth D(z), normalized D(0) = 1 (flat LCDM integral)."""
    def e(a):
        return np.sqrt(OM_M * a**-3 + OM_L)
    a = 1.0 / (1.0 + z)
    num, _ = quad(lambda ap: 1.0 / (ap * e(ap)) ** 3, 0, a, limit=200)
    den, _ = quad(lambda ap: 1.0 / (ap * e(ap)) ** 3, 0, 1.0, limit=200)
    return float(e(a) * num / den)


def sigma_mz(m_msun: float, z: float, gamma: float = 0.16) -> float:
    return float(growth_factor(z) * SIGMA8 * (m_msun / M8_MSUN) ** -gamma)


def ps_cumulative(m_min_msun: float, z: float, gamma: float = 0.16) -> float:
    """n(>M) [Mpc^-3] Press-Schechter: rho/M * erfc(nu/sqrt2) integrated... approx.

    Uses the cumulative form n(>M) = (rho_m/M) * sqrt(2/pi) * I where
    I = integral_M^inf (nu/M') e^{-nu^2/2} |dlnsigma/dlnM| dM'; with
    power-law sigma this is analytic: |dlnsigma/dlnM| = gamma, and
    n(>M) = rho_m/M * gamma * sqrt(2/pi) * integral over nu.
    We evaluate numerically over log M for robustness.
    """
    ms = np.logspace(np.log10(m_min_msun), np.log10(m_min_msun) + 4, 400)
    sig = np.array([sigma_mz(m, z, gamma) for m in ms])
    nu = DELTA_C / np.maximum(sig, 1e-300)
    f = np.sqrt(2 / np.pi) * nu * np.exp(-0.5 * nu**2)
    dndm = RHO_M / ms**2 * f * gamma
    return float(np.trapezoid(dndm, ms))


def supply_vs_demand(m_host_msun: float = 1e11, z: float = 8.0,
                     n_req: float = N_REQ_FIDUCIAL) -> dict:
    """Halo supply across the gamma band vs required giant density."""
    out = {}
    for g in [0.12, 0.16, 0.22]:
        out[g] = ps_cumulative(m_host_msun, z, g)
    return {"supply": out, "demand": n_req,
            "ratio_fid": n_req / max(out[0.16], 1e-300)}


def structure_kills(m_host_msun: float = 1e11, z: float = 8.0,
                    n_req: float = N_REQ_FIDUCIAL, margin: float = 10.0) -> bool:
    """Boolean check: demand exceeds supply across the WHOLE band (robust kill)?"""
    r = supply_vs_demand(m_host_msun, z, n_req)
    return bool(all(n_req > margin * s for s in r["supply"].values()))


def occupation_fraction(m_host_msun: float = 1e11, z: float = 8.0,
                        n_req: float = N_REQ_FIDUCIAL) -> float:
    """Required fraction of halos hosting giants (fiducial gamma)."""
    return float(n_req / max(ps_cumulative(m_host_msun, z, 0.16), 1e-300))
