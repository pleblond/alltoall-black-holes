import numpy as np
from bh_graph.monogamy import (
    psi_family, concurrence_2qubit, rho_ab, interior_pairwise_c2,
    exterior_tangle, ckw_deficit, frontier,
)


def test_endpoints_baby_universe_and_product():
    assert abs(interior_pairwise_c2(0.0) - 1.0) < 1e-9  # max interior
    assert abs(exterior_tangle(0.0)) < 1e-9  # zero exterior: pinch-off
    assert abs(exterior_tangle(np.pi / 4) - 0.5) < 1e-9  # peaks mid-range
    assert abs(interior_pairwise_c2(np.pi / 2)) < 1e-9  # product at pi/2


def test_frontier_below_linear_toy():
    # strictly inside the linear frontier: x + y < 1 away from endpoints
    x, y = interior_pairwise_c2(0.3), exterior_tangle(0.3)
    assert x + y < 1.0 - 1e-6


def test_ckw_holds_everywhere():
    for t in np.linspace(0, np.pi / 2, 25):
        assert ckw_deficit(float(t)) > -1e-9


def test_state_normalized_and_frontier_shape():
    assert abs(np.linalg.norm(psi_family(0.7)) - 1.0) < 1e-12
    x, y, th = frontier(50)
    assert len(x) == len(y) == len(th) == 50
