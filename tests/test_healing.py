import numpy as np
from bh_graph.healing import (
    tau_heal_sec, relax_area, merger_step_response, scrambling_time_s,
    timescale_ladder, healing_energy_fraction, is_adiabatic,
)


def test_qnm_timescale_gw150914_ms():
    assert 2e-3 < tau_heal_sec(63.1) < 6e-3  # measured ringdown damping scale


def test_step_response_matches_integrator():
    t = np.linspace(0, 20, 200)
    k = lambda tt: 100.0 if tt < 5e-3 else 160.0  # noqa: E731 (t in seconds)
    num = relax_area(t * 1e-3, k, 63.1)
    ana = merger_step_response(t - 5, 100.0, 160.0, 63.1)
    ana = np.where(t < 5, 100.0, ana)
    assert np.allclose(num, ana, rtol=0.05)


def test_slow_evaporation_adiabatic_fast_plunge_not():
    assert is_adiabatic(1e60, 63.1)  # astrophysical evaporation
    assert not is_adiabatic(1e-3, 63.1)  # merger-timescale driving


def test_ladder_ordering_and_silent_sigh():
    lad = timescale_ladder(63.1)
    assert lad["healing_ringdown"] < lad["scrambling"] < lad["page"] < lad["evaporation"]
    assert 10 < lad["scrambling"] / lad["healing_ringdown"] < 200
    assert healing_energy_fraction(63.1) < 1e-60
