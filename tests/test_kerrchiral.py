"""Tests for kerrchiral (D2 Route B calibration — imposed bias, no derivation)."""
import numpy as np

from bh_graph import kerrchiral as C
from bh_graph.weakfield import weak_field_graph


def _tiny_graph():
    return weak_field_graph(L=5, n_stubs=10, mode="direct", seed=0)


def test_is_valid_bias():
    assert C.is_valid_bias(0.0)
    assert C.is_valid_bias(0.99)
    assert C.is_valid_bias(-0.99)
    assert not C.is_valid_bias(1.0)
    assert not C.is_valid_bias(-1.0)
    assert not C.is_valid_bias(1.5)
    assert not C.is_valid_bias(float("nan"))
    assert not C.is_valid_bias(float("inf"))
    assert not C.is_valid_bias("bad")


def test_weights_antisymmetric_and_zero_bias_ones():
    g, pos = _tiny_graph()
    w = C.chiral_weights(g, pos, bias=0.3)
    u, v = (2, 2, 2), (3, 2, 2)
    assert (u, v) in w and (v, u) in w
    assert abs(w[(u, v)] + w[(v, u)] - 2.0) < 1e-9
    assert all(vv > 0 for vv in w.values())
    w0 = C.chiral_weights(g, pos, bias=0.0)
    assert w0 and all(vv == 1.0 for vv in w0.values())


def test_weights_invalid_bias_falls_back_to_ones():
    g, pos = _tiny_graph()
    for bad in ("bad", 1.5, float("nan"), None):
        w = C.chiral_weights(g, pos, bias=bad)
        assert w and all(vv == 1.0 for vv in w.values())


def test_transition_rows_sum_to_one_and_empty_nodes():
    g, pos = _tiny_graph()
    w = C.chiral_weights(g, pos, bias=0.4)
    tp = C.transition_probs(g, w)
    assert set(tp) == set(g.nodes())
    for nbrs, probs in tp.values():
        assert len(nbrs) == len(probs)
        if nbrs:
            assert abs(float(np.sum(probs)) - 1.0) < 1e-9
    g.add_node(("lonely",))
    assert C.transition_probs(g, w)[("lonely",)] == ([], [])


def test_equatorial_ring_nodes_and_empty():
    g, pos = weak_field_graph(L=7, n_stubs=20, mode="direct", seed=1)
    ring = C.equatorial_ring(g, pos, 2.5)
    assert len(ring) > 0
    assert all(isinstance(v, tuple) and len(v) == 3 for v in ring)
    assert C.equatorial_ring(g, pos, 1e6) == []
    assert C.equatorial_ring(g, pos, "bad") == []


def test_zero_bias_drift_consistent_with_zero():
    p = C.drift_profile([2.5], bias=0.0, L=7, n_stubs=40, seed=0,
                        n_steps=60, n_walks=40)
    e = p[2.5]
    assert e["n"] > 0
    assert abs(e["drift"]) < 3.0 * max(e["sem"], 1e-6)


def test_drift_deterministic_same_seed():
    g, pos = _tiny_graph()
    w = C.chiral_weights(g, pos, bias=0.3)
    start = min(C.equatorial_ring(g, pos, 2.0))
    kw = {"n_steps": 60, "n_walks": 40, "seed": 5}
    r1 = C.azimuthal_drift(g, pos, w, start, **kw)
    r2 = C.azimuthal_drift(g, pos, w, start, **kw)
    assert r1 == r2 and r1["n"] > 0


def test_unknown_and_hub_start_nan_no_raise():
    g, pos = _tiny_graph()
    w = C.chiral_weights(g, pos, bias=0.3)
    for start in (("nope",), ("hub",), None):
        r = C.azimuthal_drift(g, pos, w, start, n_steps=10, n_walks=5, seed=0)
        assert np.isnan(r["drift"]) and r["n"] == 0


def test_linearity_smoke_ratio():
    def mean_drift(bias):
        ds = [C.drift_profile([2.5], bias=bias, L=7, n_stubs=40, seed=s,
                              n_steps=60, n_walks=40)[2.5]["drift"]
              for s in (0, 2)]
        return float(np.mean(ds))

    d2, d4 = mean_drift(0.2), mean_drift(0.4)
    assert np.isfinite(d2) and np.isfinite(d4)
    assert d2 > 0 and d4 > 0  # same sign
    assert 1.2 < d4 / d2 < 2.8


def test_drift_profile_structure_and_empty_ring():
    p = C.drift_profile([2.5, 1e6], L=5, n_stubs=10, bias=0.3, seed=0,
                        n_steps=20, n_walks=10)
    assert set(p) == {2.5, 1e6}
    assert p[2.5]["n"] > 0 and np.isfinite(p[2.5]["drift"])
    assert np.isnan(p[1e6]["drift"]) and p[1e6]["n"] == 0


def test_bias_response_smoke():
    r = C.bias_response([0.0, 0.4], r_target=2.5, L=7, n_stubs=40, seed=0,
                        n_steps=60, n_walks=40)
    assert r["biases"] == [0.0, 0.4]
    assert len(r["drifts"]) == 2 and len(r["sems"]) == 2
    assert r["slope"] > 0


def test_fit_exponent_nan_handling_and_synthetic_minus_three():
    bad = C.fit_drift_exponent({})
    assert all(np.isnan(bad[k]) for k in ("exponent", "log_amp", "r2"))
    one = C.fit_drift_exponent({2.5: {"drift": 0.05, "sem": 0.01, "n": 10}})
    assert np.isnan(one["exponent"])
    zeros = C.fit_drift_exponent({1.5: {"drift": 0.0}, 2.5: {"drift": 0.0}})
    assert np.isnan(zeros["exponent"])
    synth = {1.0: {"drift": 1.0}, 2.0: {"drift": 0.125}, 4.0: {"drift": 0.015625}}
    fit = C.fit_drift_exponent(synth)
    assert abs(fit["exponent"] + 3.0) < 1e-9
    assert abs(fit["r2"] - 1.0) < 1e-9
