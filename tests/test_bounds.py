import numpy as np
from bh_graph.bounds import (
    t_form_s, t_form_temp_ev, f_to_beta, load_bound,
    bound_envelope_beta, remnant_exclusion_ratio, remnant_ruled_out_everywhere,
    EVAPORATION_BOUNDS,
)


def test_formation_time_scales_with_mass():
    assert t_form_s(2e10) == 2 * t_form_s(1e10)
    assert 1e-24 < t_form_s(1e15) < 1e-22


def test_conversion_sane_voyager_point():
    # Voyager ~4e14 g, f ~ 2e-8 -> beta ~ 1e-26 order
    b = f_to_beta(2.3e-8, 4e14)
    assert 1e-28 < b < 1e-24


def test_all_bound_files_load():
    for name in EVAPORATION_BOUNDS:
        m, f = load_bound(name)
        assert len(m) > 5 and bool(np.all(f > 0))


def test_remnant_excluded_by_orders_of_magnitude():
    # covered window 5e14-1e17 g: required exceeds bounds by 40+ orders
    m = np.logspace(np.log10(5e14), 17, 12)
    req, bound, ratio = remnant_exclusion_ratio(m)
    assert remnant_ruled_out_everywhere(m)
    assert bool(np.all(ratio[np.isfinite(ratio)] > 1e6))


def test_remnant_impossible_above_1e6g_without_any_data():
    from bh_graph.remnant import required_beta_for_dm
    for m in [1e6, 1e9, 1e12]:
        assert required_beta_for_dm(m) > 1.0  # unphysical, bounds unnecessary
