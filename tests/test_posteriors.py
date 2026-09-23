import numpy as np
import pytest
from bh_graph.posteriors import (
    z_from_dl, kerr_legs_msun, median_analysis, load_overall_posterior,
    source_masses_and_spins, delta_legs_posterior, GW150914_FILE,
)


def test_redshift_inversion_gw150914():
    z = float(z_from_dl(410.0))
    assert 0.07 < z < 0.11


def test_kerr_schwarzschild_limit_and_spin_reduction():
    k0 = kerr_legs_msun(30.0, 0.0)
    assert k0 == kerr_legs_msun(30.0, 0.0)
    assert kerr_legs_msun(30.0, 0.68) < k0
    assert kerr_legs_msun(30.0, 1.0) == 0.5 * k0  # extremal = half


def test_median_analysis_creates_legs():
    r = median_analysis()
    assert r["dk"] > 0 and r["frac"] > 0.3


@pytest.mark.skipif(not GW150914_FILE.exists(), reason="posterior HDF5 not cached")
def test_posterior_leg_creation_near_certain():
    post = load_overall_posterior()
    src = source_masses_and_spins(post)
    assert 0.05 < float(np.median(src["z"])) < 0.15
    r = delta_legs_posterior(src)
    assert r["p_positive"] > 0.99
    assert 0.3 < r["median_frac"] < 1.5
