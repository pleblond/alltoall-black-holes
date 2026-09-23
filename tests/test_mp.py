import numpy as np
from bh_graph.mp import (
    mp_edges, mp_density, star_spectrum, spectrum_moments, mp_predicted_var,
)


def test_mp_edges_known_cases():
    lo, hi = mp_edges(4, 2)  # c = 4/16
    assert abs(lo - 0.25) < 1e-9 and abs(hi - 2.25) < 1e-9


def test_spectrum_matches_mp_moments():
    lam = np.concatenate([star_spectrum(5, 3, seed=i) for i in range(6)])
    m = spectrum_moments(lam)
    assert abs(m["mean"] - 1.0) < 1e-9
    # variance within 30% of MP prediction at these small dims
    assert abs(m["var"] - mp_predicted_var(5, 3)) < 0.3 * mp_predicted_var(5, 3)
    lo, hi = mp_edges(5, 3)
    assert m["min"] > 0.3 * lo and m["max"] < hi * 2.0  # support roughly right


def test_density_normalized_shape():
    xs = np.linspace(0.01, 4, 2000)
    d = mp_density(xs, 5, 3)
    assert abs(np.trapezoid(d, xs) - 1.0) < 0.05
