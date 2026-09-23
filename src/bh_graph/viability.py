"""AE (corrected v1.8): remnant viability vs mass — bounds where they bite.

v1.7 erratum (stated): the overlay used the RD-only required-beta formula
(itself missing the growth factor — see bh_graph.emd) across masses where
PBHs haven't even evaporated. Corrected logic per mass M:

  - M > M* ~ 5e14 g: PBHs survive today -> no remnants exist. Dead trivially.
  - evaporated + max_omega(M) << 0.12: dead by abundance (photon-converted
    bounds pile on independently where files cover, 4e14+ g).
  - M ~ 4e5 g EMD sweet spot: max_omega ~= 0.12, currently unconstrained
    (evaporates at 1e-9 s; no photon/BBN/poltergeist-current coverage).
  - M << 1e5 g: max_omega >> 0.12 -> overclose-or-negligible, dead natural.

max_omega(M) = EMD value (RD capped below it); bounds enter as an
independent upper lid via omega(bound_beta, M) with automatic branch.
"""
from __future__ import annotations

import numpy as np

from bh_graph.bounds import bound_envelope_beta, EVAPORATION_BOUNDS  # noqa: F401 (re-export)
from bh_graph.emd import omega as omega_of_beta, omega_emd, beta_domination
from bh_graph.remnant import pbh_lifetime_s

AGE_S = 4.35e17
M_STAR_G = 5e14  # evaporating today (order-of-magnitude boundary)


def evaporated(m_g: float) -> bool:
    """Boolean check: has this mass fully evaporated by today?"""
    return bool(pbh_lifetime_s(m_g) < AGE_S)


def allowed_omega(m_grid_g) -> np.ndarray:
    """Max remnant density consistent with converted bound envelope."""
    from bh_graph.bounds import bound_envelope_beta as env
    m = np.asarray(list(m_grid_g), dtype=float)
    b = env(EVAPORATION_BOUNDS, m)
    return np.array([omega_of_beta(float(bb), float(mm)) if np.isfinite(bb) else np.inf
                     for bb, mm in zip(b, m)])


def viability(m_g: float) -> str:
    """'no remnants yet' | 'dead (underclose)' | 'sweet spot' | 'dead (overclose)' ..."""
    if not evaporated(m_g):
        return "no remnants yet"
    mx = omega_emd(m_g)
    if mx < 0.012:
        return "dead (underclose)"
    if mx > 1.2:
        return "dead (overclose)"
    return "sweet spot"


def viability_curve(m_grid_g) -> dict[str, np.ndarray]:
    m = np.asarray(list(m_grid_g), dtype=float)
    return {"M": m,
            "max_omega": np.array([omega_emd(x) for x in m]),
            "allowed": allowed_omega(m)}
