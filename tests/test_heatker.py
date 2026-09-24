import networkx as nx
import numpy as np
from bh_graph.heatker import (
    torus_graph, weighted_torus, laplacian_eigvals, heat_trace,
    spectral_dimension, heat_coefficients,
)


def test_spectral_dimension_two():
    ev = laplacian_eigvals(torus_graph(12))
    assert abs(spectral_dimension(ev) - 2.0) < 0.2


def test_a0_volume_and_a1_curvature_response():
    flat = heat_coefficients(laplacian_eigvals(torus_graph(12)))
    curv = heat_coefficients(laplacian_eigvals(weighted_torus(12, 1.5)))
    assert abs(flat["a0"] - 144 / (4 * np.pi)) < 0.1 * 144 / (4 * np.pi)
    # lattice artifact: flat a_1 != 0; curvature signal is the RELATIVE shift
    assert abs(curv["a1"] - flat["a1"]) > abs(flat["a1"])
