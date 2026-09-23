from bh_graph.litcompare import LITERATURE, head_to_head, hierarchy_holds, grid_diameter_prediction


def test_literature_anchors_present():
    assert set(LITERATURE) == {"Garttner2017", "Mi2021", "Blok2021"}
    assert LITERATURE["Garttner2017"]["wiring"] == "all:all Ising"
    assert LITERATURE["Mi2021"]["qubits"] == 53


def test_head_to_head_hierarchy_at_53():
    pred = head_to_head(53, trials=15, seed=0)
    assert hierarchy_holds(pred)
    assert pred["ratio_grid_over_all"] > 1.5  # decisive separation predicted
    assert abs(pred["alltoall_theory"] - 5.73) < 0.01  # log2(53)


def test_grid_proxy_scales_as_sqrt():
    assert grid_diameter_prediction(100) == 20.0
