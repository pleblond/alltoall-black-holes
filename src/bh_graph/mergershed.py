"""BU2: graph-derived shedding fraction (mass-ratio shape + mass independence).

The phenomenological law (:mod:`bh_graph.collapse`) prescribes a flat shed
fraction ``frac = 0.168`` and exact ``q``-independence. This module *derives*
the shape from merger combinatorics plus two model-internal premises:

(i)   Extensivity + all:all symmetry force per-bond dilution. Interior content
      ``S_int = N s_node`` (extensive, :mod:`bh_graph.maxent`) spread over
      ``N(N-1)/2`` uniform all:all bonds gives per-bond strength
      ``s_bond = 2 s_node/(N-1)``. The ``1/N`` dilution is REQUIRED for an
      all:all interior to stay extensive -- not assumed.
(ii)  Merger adds ``N1*N2`` cross bonds at remnant-uniform strength, so the
      added interior cost is ``dS = N1*N2 * 2 s_node/(N-1)`` with ``N = N1+N2``.
(iii) Monogamy (linear toy, on-frontier): the added interior cost displaces
      ``dk = dS/s_leg`` exterior legs (``s_leg = ln 2`` saturated, measured).

With ``k_tot = e_init * lam * N`` legs pre-merger, the ``N`` cancels:

    frac = dk/k_tot = [2*N1*N2/(N*(N-1))] * eta  ->  eta * 2q/(1+q)^2,

where ``eta = s_node/(e_init*lam*s_leg)`` is the per-node interior-to-exterior
budget ratio. Consequences, all tested:

* ``q``-shape ``2q/(1+q)^2`` predicted (peaks at ``q = 1``, symmetric under
  ``q <-> 1/q``) -- zero new parameters for the shape.
* mass independence exact in the large-``N`` limit (``N`` cancels between bond
  count ``~N^2``, dilution ``1/N``, and ``k_tot ~ N``); finite-``N`` O(1/N).
* ``eta < 1`` predicted: per-node exterior capacity must exceed per-node
  interior content (the Section 9 evacuation-wins condition, per node).

Calibration honesty: ``eta`` is fixed ONCE so ``frac(q=1) = 0.168`` (the
AT2017gfo anchor), i.e. ``eta = 0.336`` -- one number replacing ``e_final``,
not added alongside it (``e_final(q=1) = 0.416`` reproduced exactly). The
hadronization efficiency ``epsilon = 0.1`` stays an astrophysics input, and a
mass-dependent shutoff (if BBH are dark while gaps flash) must still be
derived, never inserted. The O5 sample adjudicates flat-vs-derived shape.
"""

from __future__ import annotations

import numpy as np

from bh_graph.collapse import E_EXT_INIT, SHED_EFFICIENCY

# Exchange ratio: interior per-node budget / exterior per-node capacity.
# ONE calibration replacing collapse.E_EXT_FINAL: frac(q=1) = eta/2 = 0.168.
ETA_EXCHANGE = 0.336
# q = 1 anchor inherited from the AT2017gfo-calibrated phenomenological law.
FRAC_AT_Q1 = 0.168


def is_valid_nodes(n1: float, n2: float) -> bool:
    """Boolean check: positive finite node counts?"""
    return bool(np.isfinite(n1) and np.isfinite(n2) and n1 > 0 and n2 > 0)


def is_valid_q(q: float) -> bool:
    """Boolean check: positive finite mass ratio?"""
    return bool(np.isfinite(q) and q > 0)


def rewire_fraction(n1: float, n2: float) -> float:
    """Exact finite-N rewiring fraction: new cross bonds / total remnant bonds.

    ``f = 2*N1*N2/(N*(N-1))``. Pure combinatorics, no physics. nan if invalid.
    """
    if not is_valid_nodes(n1, n2):
        return float("nan")
    n = n1 + n2
    if n < 2:
        return float("nan")
    return float(2.0 * n1 * n2 / (n * (n - 1.0)))


def rewire_fraction_q(q: float) -> float:
    """Large-N rewiring shape ``2q/(1+q)^2`` (peaks 1/2 at q=1). nan if invalid."""
    if not is_valid_q(q):
        return float("nan")
    return float(2.0 * q / (1.0 + q) ** 2)


def shed_fraction_q(q: float, eta: float = ETA_EXCHANGE) -> float:
    """Derived shed fraction at mass ratio ``q``: ``eta * 2q/(1+q)^2``."""
    if not is_valid_q(q) or not np.isfinite(eta):
        return float("nan")
    return float(eta * rewire_fraction_q(q))


def shed_fraction_nodes(n1: float, n2: float, eta: float = ETA_EXCHANGE) -> float:
    """Derived shed fraction at finite node counts (exact combinatorics)."""
    if not np.isfinite(eta):
        return float("nan")
    return float(eta * rewire_fraction(n1, n2))


def e_final_of_q(q: float, e_init: float = E_EXT_INIT, eta: float = ETA_EXCHANGE) -> float:
    """Remnant exterior fraction ``e_init*(1 - frac(q))``. nan if invalid."""
    if not is_valid_q(q):
        return float("nan")
    if not (np.isfinite(e_init) and np.isfinite(eta)) or not 0 < e_init <= 1:
        return float("nan")
    return float(e_init * (1.0 - shed_fraction_q(q, eta)))


def mass_ratio(m1: float, m2: float) -> float:
    """Mass ratio ``q <= 1`` (``N ~ M`` by extensivity, so ``q_mass = q_N``)."""
    if not (np.isfinite(m1) and np.isfinite(m2)) or m1 <= 0 or m2 <= 0:
        return float("nan")
    return float(min(m1, m2) / max(m1, m2))


def ejecta_derived(
    m1_msun: float,
    m2_msun: float,
    efficiency: float = SHED_EFFICIENCY,
    eta: float = ETA_EXCHANGE,
) -> dict[str, float]:
    """Derived-law ejecta: ``M_ej = frac(q)*M_tot*eps`` (``k_tot`` cancels exactly).

    Same ``k_tot`` cancellation as the phenomenological law, so the fraction is
    exactly mass independent at fixed ``q``; only the SHAPE in ``q`` is new.
    """
    nan = float("nan")
    q = mass_ratio(m1_msun, m2_msun)
    if not is_valid_q(q):
        return {"q": nan, "frac": nan, "M_tot": nan, "M_ej": nan}
    if not (np.isfinite(efficiency) and np.isfinite(eta)):
        return {"q": float(q), "frac": nan, "M_tot": nan, "M_ej": nan}
    if not 0 < efficiency <= 1:
        return {"q": float(q), "frac": nan, "M_tot": nan, "M_ej": nan}
    frac = shed_fraction_q(q, eta)
    m_tot = float(m1_msun + m2_msun)
    return {
        "q": float(q),
        "frac": float(frac),
        "M_tot": m_tot,
        "M_ej": float(frac * m_tot * efficiency),
    }


def derived_vs_universal_dimming_mag(m1_msun: float, m2_msun: float) -> float:
    """How much dimmer (mag) the derived law is vs the flat prescription.

    From ``L_peak ~ M_ej^0.35`` (same Arnett scaling as
    :func:`bh_graph.collapse.kilonova_peak_lum_erg_s`): positive means the
    derived law predicts dimmer. nan if either ejecta is invalid.
    """
    from bh_graph.collapse import leg_shedding_ejecta

    got = ejecta_derived(m1_msun, m2_msun)
    uni = leg_shedding_ejecta(m1_msun, m2_msun)
    if not (np.isfinite(got["M_ej"]) and np.isfinite(uni["M_ej"])):
        return float("nan")
    if not (got["M_ej"] > 0 and uni["M_ej"] > 0):
        return float("nan")
    return float(2.5 * 0.35 * np.log10(uni["M_ej"] / got["M_ej"]))


def gw190814_derived() -> dict[str, float]:
    """Derived-law prediction for GW190814 (23.2 + 2.6, q ~ 0.11)."""
    from bh_graph.massgaps import GW190814_M1, GW190814_M2

    out = ejecta_derived(GW190814_M1, GW190814_M2)
    out["dimming_mag"] = derived_vs_universal_dimming_mag(GW190814_M1, GW190814_M2)
    return out


def is_eta_below_unity(eta: float = ETA_EXCHANGE) -> bool:
    """Boolean check: exchange ratio below 1 (evacuation-wins condition)?"""
    return bool(np.isfinite(eta) and 0 < eta < 1.0)


def is_mass_independent(
    n1: float = 50.0, n2: float = 50.0, scale: float = 10.0, tol: float = 0.01
) -> bool:
    """Boolean check: rewiring fraction unchanged under N-scaling (large N)?

    Exact mass independence holds in the thermodynamic limit; at finite ``N``
    the ``N-1`` vs ``N`` denominator leaves O(1/N) corrections, bounded here.
    """
    if not (is_valid_nodes(n1, n2) and np.isfinite(scale) and scale > 0):
        return False
    if not (np.isfinite(tol) and tol > 0):
        return False
    f0 = rewire_fraction(n1, n2)
    f1 = rewire_fraction(n1 * scale, n2 * scale)
    return bool(np.isfinite(f0) and np.isfinite(f1) and abs(f1 - f0) < tol)


def is_q_shape_symmetric(tol: float = 1e-12) -> bool:
    """Boolean check: ``f(q) == f(1/q)`` (merger symmetric in progenitors)?"""
    if not (np.isfinite(tol) and tol > 0):
        return False
    for q in (0.1, 0.25, 0.5, 0.8):
        if abs(rewire_fraction_q(q) - rewire_fraction_q(1.0 / q)) > tol:
            return False
    return True


def is_peak_at_equal_mass(n_grid: int = 101) -> bool:
    """Boolean check: shed fraction maximized at ``q = 1`` (most rewiring)?"""
    q = np.linspace(0.05, 1.0, n_grid)
    frac = np.array([shed_fraction_q(v) for v in q])
    if not np.all(np.isfinite(frac)):
        return False
    return bool(int(np.argmax(frac)) == n_grid - 1)
