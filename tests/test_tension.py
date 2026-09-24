import numpy as np
from bh_graph.tension import (
    stretch_energy, stretch_force, fission_rate_toy, sigma_lower_bound,
    hawking_temperature, tension_band,
)


def test_force_is_energy_gradient():
    d = np.linspace(1, 10, 100)
    num = -np.gradient(stretch_energy(d, 2.0, 1.5), d)
    assert np.allclose(num[5:-5], stretch_force(d, 2.0, 1.5)[5:-5], rtol=0.05)
    assert bool(np.all(stretch_force(d, 1.0, 1.0) < 0))  # restoring


def test_rate_suppressed_by_barrier():
    assert fission_rate_toy(0.1, 10.0) < fission_rate_toy(0.1, 1.0)
    assert fission_rate_toy(0.1, 0.0) == 1.0


def test_bound_inverts_rate():
    s = sigma_lower_bound(1e-10, 0.1, 5.0, 1.0)
    assert abs(fission_rate_toy(0.1, s * 5.0) - 1e-10) / 1e-10 < 1e-9


def test_fiducial_band_positive_finite():
    b = tension_band()
    assert 0 < b["p1"] < np.inf and 0 < b["p2"] < np.inf
    assert hawking_temperature(1e39) < 1e-38
