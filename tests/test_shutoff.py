import numpy as np

from bh_graph.shutoff import (
    escape_fraction,
    insertion_cost_fixed_radius_km,
    is_blue_red_split_in_alpha,
    is_selfsimilar_no_shutoff,
    is_valid_shutoff_args,
    kn_efficiency,
    required_alpha,
    required_alpha_smooth,
    vesc_of_alpha,
)


def test_escape_velocity_mass_free_and_values():
    # v_esc/c = sqrt((1-f)/alpha): no mass enters (self-similarity)
    assert abs(vesc_of_alpha(2.0) - np.sqrt(0.96 / 2.0)) < 1e-12
    assert abs(vesc_of_alpha(100.0) - 0.098) < 0.001
    assert not np.isfinite(vesc_of_alpha(-1.0))


def test_required_shedding_radii_split_by_component():
    assert is_blue_red_split_in_alpha()
    assert abs(required_alpha(0.3) - 10.7) < 0.1  # blue past ~11 Rs
    assert abs(required_alpha(0.1) - 96.0) < 0.5  # red past ~96 Rs
    # finite velocity widths push red further at 95% escape
    assert abs(required_alpha_smooth(0.95, 0.1) - 138.0) < 2.0
    assert abs(required_alpha_smooth(0.95, 0.3) - 374.0) < 3.0
    assert not np.isfinite(required_alpha_smooth(1.5, 0.3))


def test_no_mass_shutoff_flatness_theorem():
    assert is_selfsimilar_no_shutoff()
    # M_ej/M_tot identical at 0.7 and 150 Msun (fixed q)
    lo = kn_efficiency(0.7, 400.0)["M_ej"] / 0.7
    hi = kn_efficiency(150.0, 400.0)["M_ej"] / 150.0
    assert abs(lo - hi) < 1e-12
    # universality stands: GW190814 derived ejecta unchanged by fallback
    g = kn_efficiency(25.8, 400.0, q=2.59 / 23.2)
    assert abs(g["M_ej"] - 0.155) < 0.005
    assert g["consistent"] == 1.0  # esc > 0.95 leaves calibration intact
    assert kn_efficiency(25.8, 2.0)["consistent"] == 0.0  # deep shed would not


def test_insertion_detector_prices_hypothetical_shutoffs():
    # shutoff at 44 Msun would cost a fixed ~12,500 km shedding radius
    assert abs(insertion_cost_fixed_radius_km(44.0) - 12478.0) < 5.0
    # cost scales linearly with the shutoff mass (non-self-similar by readout)
    assert (
        abs(insertion_cost_fixed_radius_km(88.0) / insertion_cost_fixed_radius_km(44.0) - 2.0)
        < 1e-9
    )
    assert not np.isfinite(insertion_cost_fixed_radius_km(-5.0))


def test_invalid_inputs_return_nan_or_false():
    assert not is_valid_shutoff_args(0.0, 0.1)
    assert not is_valid_shutoff_args(10.0, -0.1)
    assert not np.isfinite(escape_fraction(float("nan")))
    bad = kn_efficiency(-1.0, 400.0)
    assert not np.isfinite(bad["M_ej"])
