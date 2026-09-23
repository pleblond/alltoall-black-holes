from bh_graph.collapse import (
    collapse_graph, order_parameters, collapse_sweep, erasure_lcc_diameter,
    is_fast_scrambler,
)
from bh_graph.graphs import build_complete


def test_endpoints_grid_and_complete():
    g0 = collapse_graph(5, 0.0)
    op0 = order_parameters(g0)
    assert op0["diameter"] == 8.0  # 5x5 grid
    g1 = collapse_graph(5, 1.0)
    op1 = order_parameters(g1)
    assert op1["diameter"] == 1.0 and is_fast_scrambler(op1, 25)


def test_crossover_sharp_mid_range():
    s = collapse_sweep(6, gamma=6.0)
    assert s["diameter"][0] > s["diameter"][-1]
    assert s["gap"][-1] > s["gap"][0]
    # most of the diameter drop happens in a compactness window < 0.6 wide
    drop = s["diameter"][0] - s["diameter"][-1]
    mid = (s["diameter"] < s["diameter"][0] - 0.1 * drop) & (s["diameter"] > s["diameter"][-1] + 0.1 * drop)
    assert float(s["c"][mid].max() - s["c"][mid].min()) < 0.6


def test_erasure_bh_recovers_matter_fragments():
    bh = build_complete(25)
    matter = collapse_graph(5, 0.0)
    assert erasure_lcc_diameter(bh, 0.4) == 1.0  # any subset still a clique
    assert erasure_lcc_diameter(matter, 0.4) > 1.0
