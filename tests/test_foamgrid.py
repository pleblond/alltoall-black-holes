import numpy as np
from bh_graph.foamgrid import (
    run_case, deficit_vs_omega, exclusion_epsilon,
)


def test_centroid_unbiased_with_defects():
    cs = [run_case(100, 16.0, 0.2, n_steps=350, seed=s)["centroids"][-1]
          for s in range(4)]
    assert abs(float(np.mean(cs))) < 2.0  # jitters, averages straight


def test_deficit_grows_with_frequency():
    r = deficit_vs_omega([8.0, 16.0, 32.0], eps=0.25, n=130, trials=3, seed=1)
    d = r["deficit"]
    assert d[0] > d[1] > d[2]  # spinning multiplies edge use
    assert d[0] > 0.05  # sizable at short wavelength


def test_deficit_grows_with_defects():
    a = deficit_vs_omega([8.0], eps=0.0, n=110, trials=3, seed=2)["deficit"][0]
    b = deficit_vs_omega([8.0], eps=0.25, n=110, trials=3, seed=2)["deficit"][0]
    assert abs(a) < 1e-9 and b > 0.05


def test_deficit_scales_quadratic():
    r = deficit_vs_omega([8.0, 16.0], eps=0.25, n=130, trials=3, seed=1)
    ratio = r["deficit"][0] / max(r["deficit"][1], 1e-9)
    assert 2.0 < ratio < 8.0  # ~4x per octave (phase variance ~ k^2)


def test_exclusion_ladder():
    assert exclusion_epsilon(2.0, 3000.0) < 1e-2  # optical: per-mille fabric
    assert exclusion_epsilon(1e12, 3000.0) < 1e-13  # TeV: 1e-14 fabric
    assert exclusion_epsilon(1e12, 3000.0) < exclusion_epsilon(2.0, 3000.0)
