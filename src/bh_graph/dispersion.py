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

GW note (hypothetical extrapolation only, NOT derived): the functions
below assume the same quadratic law applied to GWs purely to show why
GW propagation cannot constrain it. The paper claims no GW-sector
derivation and no GW-based bound.
"""
from __future__ import annotations

import numpy as np

# Published 95% bounds, Fermi-LAT GRB 090510 (Abdo et al. 2009), GeV.
FERMI_LINEAR_GEV = 9.3e19
FERMI_QUAD_GEV = 1.3e11
E_PLANCK_GEV = 1.220910e19
MPC_M = 3.085677581e22
C_SI = 299792458.0
# Planck constant in GeV s (for GW graviton energy E = h f).
H_GEV_S = 4.135667696e-24
# Order-of-magnitude LVK MDR bound on |A_4| (GWTC-3 combined, peV^-2;
# GWTC-4.0 tightens by factors of a few — irrelevant at 60 orders).
# A_4 has dimension energy^-2; alpha = 2 is excluded by LVK (no dispersion).
LVK_A4_BOUND_PEV_INV2 = 1.0e-21
# GW170817/GRB 170817A fractional-speed difference bound (order of magnitude).
GW170817_FRAC_SPEED_BOUND = 1.0e-15
# GeV -> peV conversion: 1 GeV = 1e21 peV.
GEV_PER_PEV = 1.0e-21


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


def gw_energy_gev(frequency_hz: float) -> float:
    """Graviton energy E = h f in GeV (classical frequency component)."""
    return float(H_GEV_S * frequency_hz)


def gw_fractional_shift(frequency_hz: float, eqg2_gev: float | None = None) -> float:
    """Hypothetical GW (E/E_QG,2)^2 shift under universal extrapolation."""
    if eqg2_gev is None:
        eqg2_gev = eqg2_scale_gev()
    return float((gw_energy_gev(frequency_hz) / eqg2_gev) ** 2)


def gw_arrival_delay_s(frequency_hz: float, dist_mpc: float) -> float:
    """Hypothetical absolute GW delay over dist (differential across band ~ same order)."""
    return float(arrival_delay_s(gw_energy_gev(frequency_hz), dist_mpc))


def lvk_a4_gev_inv2(eqg2_gev: float | None = None) -> float:
    """LVK MDR amplitude: v ~= 1 + 3/2 A_4 E^2 => A_4 = -2/(3 E_QG,2^2)."""
    if eqg2_gev is None:
        eqg2_gev = eqg2_scale_gev()
    return float(-2.0 / (3.0 * eqg2_gev**2))


def lvk_a4_pev_inv2(eqg2_gev: float | None = None) -> float:
    """A_4 in peV^-2 (1 GeV^-2 = 1e-42 peV^-2)."""
    return float(lvk_a4_gev_inv2(eqg2_gev) * 1.0e-42)


def lvk_a4_margin() -> float:
    """LVK bound / |model A_4| (>> 1 = safe; ~1e60)."""
    return float(LVK_A4_BOUND_PEV_INV2 / abs(lvk_a4_pev_inv2()))


def multimessenger_margin(grb_energy_gev: float = 1.0e-4) -> float:
    """GW170817 bound / photon-side shift (photon dominates over GW by ~35 orders)."""
    photon_shift = (grb_energy_gev / eqg2_scale_gev()) ** 2
    return float(GW170817_FRAC_SPEED_BOUND / photon_shift)


def is_gw_propagation_safe() -> bool:
    """Boolean check: both MDR and multimessenger margins comfortably safe."""
    return bool(lvk_a4_margin() > 1e50 and multimessenger_margin() > 1e20)
