import numpy as np

from bh_graph.collapse import (
    E_EXT_FINAL,
    E_EXT_INIT,
    SHED_EFFICIENCY,
    is_kilonova_capable,
    leg_shedding_ejecta,
    shed_fraction,
)
from bh_graph.mergershed import (
    ETA_EXCHANGE,
    FRAC_AT_Q1,
    derived_vs_universal_dimming_mag,
    e_final_of_q,
    ejecta_derived,
    gw190814_derived,
    is_eta_below_unity,
    is_mass_independent,
    is_peak_at_equal_mass,
    is_q_shape_symmetric,
    is_valid_nodes,
    is_valid_q,
    mass_ratio,
    rewire_fraction,
    rewire_fraction_q,
    shed_fraction_nodes,
    shed_fraction_q,
)


def test_rewire_combinatorics_exact_values():
    # (1,1): one cross bond out of one total bond -> all new
    assert rewire_fraction(1, 1) == 1.0
    # (2,2): 8 cross-bond endpoints over 4*3
    assert abs(rewire_fraction(2, 2) - 8 / 12) < 1e-12
    # equal split tends to 1/2 (half the remnant interior is rewired)
    assert abs(rewire_fraction(500, 500) - 0.5) < 0.005
    # q-form matches node form at large N
    assert abs(rewire_fraction(400, 100) - rewire_fraction_q(0.25)) < 0.005
    # q-form anchor values: peaks 1/2 at q=1, vanishes at q->0
    assert rewire_fraction_q(1.0) == 0.5
    assert rewire_fraction_q(0.01) < 0.02
    assert is_q_shape_symmetric()
    assert is_peak_at_equal_mass()


def test_mass_independence_exact_in_limit_bounded_at_finite_n():
    # N cancels in the derivation; finite-N holds O(1/N) corrections only
    assert is_mass_independent(50, 50, scale=10.0, tol=0.01)
    assert is_mass_independent(100, 25, scale=5.0, tol=0.01)
    # ... while the q-dependence itself is O(1), not a finite-N artifact
    assert shed_fraction_q(1.0) / shed_fraction_q(0.1) > 2.0
    # ejecta fraction exactly mass independent at fixed q (k_tot cancels)
    lo = ejecta_derived(1.4, 1.4)
    hi = ejecta_derived(14.0, 14.0)
    assert lo["frac"] == hi["frac"]
    assert abs(hi["M_ej"] / lo["M_ej"] - 10.0) < 1e-9  # M_ej scales with M_tot


def test_calibration_replaces_e_final_and_matches_at_q1():
    # one number for one number: eta fixed so frac(q=1) = 0.168 anchor
    assert ETA_EXCHANGE == 0.336
    assert abs(FRAC_AT_Q1 - shed_fraction()) < 1e-12  # anchor = pheno frac
    assert abs(shed_fraction_q(1.0) - FRAC_AT_Q1) < 1e-12
    # remnant exterior fraction reproduces the phenomenological e_final at q=1
    assert E_EXT_INIT == 0.5
    assert abs(e_final_of_q(1.0) - E_EXT_FINAL) < 1e-12
    # ... and sheds less at unequal mass (less rewiring)
    assert e_final_of_q(0.1) > e_final_of_q(1.0)
    assert SHED_EFFICIENCY == 0.1  # efficiency stays an external input
    # eta < 1: exterior per-node capacity exceeds interior content (S9 condition)
    assert is_eta_below_unity()
    assert not is_eta_below_unity(1.5)


def test_gw190814_still_bright_under_derived_law():
    got = gw190814_derived()
    # q = 2.59/23.2 ~ 0.11 -> frac ~ 0.061 (vs 0.168 flat)
    assert abs(got["q"] - 2.59 / 23.2) < 1e-9
    assert abs(got["frac"] - 0.0607) < 0.002
    assert abs(got["M_ej"] - 0.157) < 0.005
    assert is_kilonova_capable(got["M_ej"])  # still far above 0.01 threshold
    # dimmer than the flat prescription by ~0.4 mag -- tension eases, survives
    assert abs(got["dimming_mag"] - 0.38) < 0.05
    assert abs(derived_vs_universal_dimming_mag(1.4, 1.4)) < 1e-9  # agree at q=1
    # cross-check against the phenomenological module (no drift in either)
    uni = leg_shedding_ejecta(23.2, 2.59)
    assert abs(uni["M_ej"] - 0.433) < 0.005
    assert got["M_ej"] < uni["M_ej"]


def test_mass_ratio_and_node_form_agree():
    assert mass_ratio(23.2, 2.59) == mass_ratio(2.59, 23.2)  # order-free
    assert abs(mass_ratio(1.4, 1.4) - 1.0) < 1e-12
    # node form converges to q-form with N at fixed ratio
    for n in (50, 500):
        assert abs(shed_fraction_nodes(n, n) - shed_fraction_q(1.0)) < 0.002


def test_invalid_inputs_return_nan_or_false_without_exceptions():
    assert not is_valid_nodes(0, 5)
    assert not is_valid_nodes(-1, 5)
    assert not is_valid_nodes(5, float("nan"))
    assert not is_valid_q(0.0)
    assert not is_valid_q(-0.5)
    assert not is_valid_q(float("inf"))
    assert not np.isfinite(rewire_fraction(0, 5))
    assert not np.isfinite(rewire_fraction_q(0.0))
    assert not np.isfinite(shed_fraction_q(float("nan")))
    assert not np.isfinite(e_final_of_q(-1.0))
    assert not np.isfinite(mass_ratio(1.4, 0.0))
    bad = ejecta_derived(-1.0, 1.4)
    assert not np.isfinite(bad["M_ej"])
    assert not np.isfinite(derived_vs_universal_dimming_mag(0.0, 1.4))
    assert not is_mass_independent(0, 5)
