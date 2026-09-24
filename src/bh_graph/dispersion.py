"""BD: Lattice dispersion from discrete leg spacing (quadratic, safe).

Any hopping propagation on a discrete graph has lattice dispersion. Tight
binding on a 1D chain (spacing a = lp): w = 2J|sin(ka/2)|, group velocity
v_g = Ja cos(ka/2) ~= Ja(1-(ka)^2/8). Two structural consequences:

  1. NO linear term: v_g is even in k (k <-> -k symmetry of any lattice),
     so delta-v/v = O((E/E_P)^2) — quadratic (CPT-even-like). The strong
     Fermi LINEAR bounds (E_QG,1 > 9.3e19 GeV, GRB 090510) are evaded by
     symmetry, not tuning.
  2. Effective quadratic scale E_QG,2 = sqrt(8) E_P ~ 2.8 E_Planck >>
     Fermi quadratic bound (1.3e11 GeV): safe by ~8 orders. A 10 GeV GRB
     photon over a Gpc is delayed ~1e-20 s — predicted, unobservable.

Caveats (stated): regular-lattice result; all:all regions have no k to
disperse (translation invariance required); near-horizon running of the
effective spacing is open; no polarization (scalar SI only, no
birefringence prediction).
"""
from __future__ import annotations

import numpy as np

# Published 95% bounds, Fermi-LAT GRB 090510 (Abdo et al. 2009), GeV.
FERMI_LINEAR_GEV = 9.3e19
FERMI_QUAD_GEV = 1.3e11
E_PLANCK_GEV = 1.220910e19
MPC_M = 3.085677581e22
C_SI = 299792458.0


def omega_tb(k, a: float = 1.0, j: float = 1.0):
    """Tight-binding dispersion w = 2J|sin(ka/2)| (h=1 units)."""
    return 2 * j * np.abs(np.sin(np.asarray(k, dtype=float) * a / 2))


def group_velocity(k, a: float = 1.0, j: float = 1.0):
    """v_g = d w/dk = Ja cos(ka/2) sign(sin) (magnitude)."""
    k = np.asarray(k, dtype=float)
    return np.abs(j * a * np.cos(k * a / 2))


def velocity_defect(k, a: float = 1.0) -> np.ndarray | float:
    """1 - v_g/v_0 ~= (ka)^2/8 (quadratic, no linear term)."""
    return 1.0 - group_velocity(k, a) / (1.0 * a)


def eqg2_scale_gev(lp_gev_inv: float = 1.0 / E_PLANCK_GEV) -> float:
    """Effective quadratic LIV scale: E_QG,2 = sqrt(8) E_Planck."""
    return float(np.sqrt(8.0) / lp_gev_inv)


def arrival_delay_s(energy_gev: float, dist_mpc: float, eqg2_gev: float | None = None) -> float:
    """Delta t = L (E/E_QG,2)^2 / c for quadratic subluminal dispersion."""
    if eqg2_gev is None:
        eqg2_gev = eqg2_scale_gev()
    return float(dist_mpc * MPC_M / C_SI * (energy_gev / eqg2_gev) ** 2)


def fermi_quad_margin() -> float:
    """Model scale / Fermi bound (>> 1 = safe)."""
    return float(eqg2_scale_gev() / FERMI_QUAD_GEV)


def linear_term_absent() -> bool:
    """Boolean check: v_g even in k => no O(E) term (symmetry argument)."""
    ks = np.linspace(-1.0, 1.0, 9)
    return bool(np.allclose(group_velocity(ks), group_velocity(-ks)))
