"""Tests for kerraniso (D2 Route A calibration — imposed proxy, no derivation)."""
import networkx as nx
import numpy as np

from bh_graph import kerraniso as K
from bh_graph.orici import gradient_shell_graph


def test_labels_split_and_fallback():
    lab = K.assign_latitude_labels(10)
    assert sum(1 for z in lab.values() if z == K.POLAR) == 5
    assert sum(1 for z in lab.values() if z == K.EQUATORIAL) == 5
    assert K.assign_latitude_labels(10, polar_fraction=0.0) == lab  # fallback
    assert K.assign_latitude_labels(1) == {}


def test_valid_eps_range():
    assert K.is_valid_bridge_eps(0.0)
    assert K.is_valid_bridge_eps(1.9)
    assert K.is_valid_bridge_eps(-0.99)
    assert not K.is_valid_bridge_eps(-1.0)  # open interval: weight hits 0
    assert not K.is_valid_bridge_eps(2.0)
    assert not K.is_valid_bridge_eps(float("nan"))
    assert not K.is_valid_bridge_eps("x")


def test_eps_zero_recovers_orici_edges():
    g0 = K.gradient_shell_graph_latitude(8, 4, seed=3)
    g1 = gradient_shell_graph(8, 4, seed=3)
    assert set(map(tuple, map(sorted, g0.edges()))) == set(map(tuple, map(sorted, g1.edges())))
    assert all("zone" in g0.nodes[v] for v in g0.nodes())


def test_imposition_shifts_bridge_composition_monotonically():
    fracs = []
    for eps in (-0.9, 0.0, 1.5):
        fs = [
            K.bridge_polar_fraction(K.gradient_shell_graph_latitude(10, 4, epsilon_bridge=eps, seed=s), 4)
            for s in range(5)
        ]
        assert all(np.isfinite(fs))
        fracs.append(float(np.mean(fs)))
    assert fracs[0] < fracs[1] < fracs[2]


def test_zonal_profile_structure_and_hand_anisotropy():
    g = K.gradient_shell_graph_latitude(6, 4, seed=0)
    prof = K.shell_kappa_profile_by_zone(g, 4, max_per_zone=2)
    assert len(prof) == 3  # one per shell-pair
    for zm in prof.values():
        assert set(zm) == {"polar", "equatorial", "mixed", "all"}
    hand = {1.0: {"polar": -2.0, "equatorial": -1.0, "mixed": -1.5, "all": -1.5}}
    a = K.zonal_anisotropy(hand)
    assert abs(a["stacked"] - (2.0 - 1.0) / 1.5) < 1e-12 and a["n_ok"] == 1
    bad = {1.0: {"polar": 0.1, "equatorial": -1.0, "mixed": -1.0, "all": -1.0}}
    assert np.isnan(K.zonal_anisotropy(bad)["stacked"])


def test_measure_anisotropy_runs_tiny():
    r = K.measure_anisotropy(per_shell=6, n_shells=4, n_graphs=2, seed0=0, max_per_zone=2)
    assert r["n_ok"] >= 0 and len(r["per_graph"]) == 2
    assert np.isfinite(r["bridge_polar_frac_mean"])
    assert set(r["stacked"]) == {"polar", "equatorial", "mixed", "all"}


def test_calibration_curve_structure_and_imposition():
    c = K.calibration_curve(
        [-0.5, 0.5], per_shell=6, n_shells=4, n_graphs=2, seed0=1, max_per_zone=2
    )
    assert c["eps_imposed"] == [-0.5, 0.5] and len(c["results"]) == 2
    f0 = c["results"][0]["bridge_polar_frac_mean"]
    f1 = c["results"][1]["bridge_polar_frac_mean"]
    assert f0 < f1  # imposition holds even where OR is noisy


def test_is_anisotropy_detected():
    assert K.is_anisotropy_detected({"mean": 0.5, "sem": 0.1, "n_ok": 5})
    assert not K.is_anisotropy_detected({"mean": 0.1, "sem": 0.1, "n_ok": 5})
    assert not K.is_anisotropy_detected({"mean": 0.5, "sem": 0.0, "n_ok": 5})
    assert not K.is_anisotropy_detected({})


def test_determinism_and_bad_inputs():
    a = K.gradient_shell_graph_latitude(8, 4, epsilon_bridge=0.7, seed=11)
    b = K.gradient_shell_graph_latitude(8, 4, epsilon_bridge=0.7, seed=11)
    assert set(map(tuple, map(sorted, a.edges()))) == set(map(tuple, map(sorted, b.edges())))
    assert K.edge_zone(a, ("nope",), ("nope",)) == K.MIXED
    assert np.isnan(K.bridge_polar_fraction(nx.Graph(), 4))
    r = K.measure_anisotropy(per_shell=6, n_shells=4, n_graphs=1,
                             epsilon_bridge="bad", seed0=0, max_per_zone=1)
    assert len(r["per_graph"]) == 1  # fallback, no raise
