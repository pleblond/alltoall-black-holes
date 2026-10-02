"""OBS-0R apparatus unit tests (fast; NO campaign sizes / NO campaign data).

Design-validation pilots live here in miniature: every numeric assertion
uses synthetic data or toy graphs (L<=16 torus, tiny expanders). Campaign
sizes (L>=28 / N>=800) NEVER appear in this file.
"""
import math

import networkx as nx
import numpy as np
import pytest

from bh_graph import obs0, obs0r
from bh_graph.formation import j2_torus_coords, j2_torus_graph
from bh_graph.graphs import build_random_regular, build_torus_grid


def test_omega_gap_matched():
    assert obs0r.omega_below_edge(8) == pytest.approx(-8.5)
    assert obs0r.omega_below_edge(4) == pytest.approx(-4.5)


def test_static_field_toy_square():
    g = build_torus_grid(4)
    order = sorted(g.nodes())
    F = obs0r.static_field_phi(g, order, order[0], -4.5)
    assert F["gap_ok"]
    assert F["max_imag"] < 1e-9
    assert bool((F["phi"] > 0).all())
    assert F["residual"] < 1e-9
    # Source pinned to s = 1.
    assert F["phi"][0] == pytest.approx(1.0)


def test_shell_profile_path():
    g = nx.path_graph(6)
    order = sorted(g.nodes())
    dist = dict(nx.single_source_shortest_path_length(g, 0))
    prof = obs0r.shell_profile(np.arange(6.0), order, dist, 5)
    assert prof[0] == {"v": 0.0, "n": 1}
    assert prof[3] == {"v": 3.0, "n": 1}
    profm = obs0r.shell_profile(np.arange(6.0), order, dist, 5, stat="mean")
    assert profm[2]["v"] == pytest.approx(2.0)


def test_fit_yukawa_recovers_truth():
    rng = np.random.default_rng(0)
    r = rng.uniform(1.0, 10.0, size=60)
    p = 2.5 * r ** -0.4 * np.exp(-r / 1.9)
    fit = obs0r.fit_yukawa(r, p)
    assert fit["ok"]
    assert fit["A"] == pytest.approx(2.5, rel=1e-9)
    assert fit["alpha"] == pytest.approx(0.4, rel=1e-9)
    assert fit["xi"] == pytest.approx(1.9, rel=1e-9)
    assert fit["r2"] == pytest.approx(1.0, abs=1e-12)


def test_fit_yukawa_rejects_growth():
    r = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    fit = obs0r.fit_yukawa(r, np.exp(r))  # unambiguous exponential growth
    assert not fit["ok"]
    fit2 = obs0r.fit_yukawa([1.0, 2.0], [1.0, 0.5])
    assert not fit2["ok"]


def test_fit_pure_exp_recovers_kappa():
    r = np.array([2.0, 3.0, 4.0, 5.0])
    p = 3.0 * np.exp(-r / 1.9)
    fit = obs0r.fit_pure_exp(r, p)
    assert fit["ok"]
    assert fit["xi"] == pytest.approx(1.9, rel=1e-9)


def test_yukawa_monotone_and_invert_roundtrip():
    cal = {"A": 2.5, "alpha": 0.4, "xi": 1.9}
    assert obs0r.yukawa_monotone_ok(cal)
    for r in (1.0, 2.5, 5.0, 9.9):
        assert obs0r.invert_yukawa(obs0r.yukawa_F(r, **cal), cal) == pytest.approx(r, abs=1e-9)
    assert obs0r.invert_yukawa(1e9, cal) is None
    assert obs0r.invert_yukawa(1e-30, cal) is None
    assert obs0r.invert_yukawa(-1.0, cal) is None
    assert obs0r.invert_yukawa(0.5, {"A": 1.0}) is None
    bad = {"A": 1.0, "alpha": -5.0, "xi": 1.0}
    assert not obs0r.yukawa_monotone_ok(bad)


def test_pot_targets_by_shell():
    g = build_torus_grid(6)
    dist = dict(nx.single_source_shortest_path_length(g, 0))
    t1 = obs0r.pot_targets_by_shell(dist, seed=8200)
    t2 = obs0r.pot_targets_by_shell(dist, seed=8200)
    assert t1 == t2
    Rs = sorted(t1.values())
    assert min(Rs) >= 1 and max(Rs) <= 10
    # Seed sensitivity where pools exceed per-shell takes.
    s1 = obs0r.pot_targets_by_shell(dist, per_shell=2, seed=8200)
    s2 = obs0r.pot_targets_by_shell(dist, per_shell=2, seed=8201)
    assert s1 != s2


def test_dp_wp_pair_maps_roundtrip():
    rng = np.random.default_rng(1)
    tD = rng.uniform(2.0, 60.0, size=40)
    phi = np.exp(-(0.5 * np.sqrt(tD) + 1.2))
    cal = obs0r.fit_dp_pair_map(list(zip(tD, phi)))
    assert cal["a"] == pytest.approx(0.5, rel=1e-9)
    assert cal["n"] == 40
    for t, p in zip(tD[:5], phi[:5]):
        assert obs0r.invert_dphi(p, cal) == pytest.approx(math.sqrt(t), rel=1e-9)
    assert obs0r.invert_dphi(2.0, cal) is None  # above map range
    assert obs0r.invert_dphi(0.5, {"a": -1.0, "b": 0.0}) is None
    RW = rng.uniform(0.5, 12.0, size=40)
    phiw = np.exp(-(1.1 * RW + 0.7))
    calw = obs0r.fit_wp_pair_map(list(zip(RW, phiw)))
    assert calw["a"] == pytest.approx(1.1, rel=1e-9)
    for w, p in zip(RW[:5], phiw[:5]):
        assert obs0r.invert_wphi(p, calw) == pytest.approx(w, rel=1e-9)
    assert obs0r.invert_wphi(0.0, calw) is None


def test_p_bin_edges():
    assert obs0r.p_bin_of(1.0) == 0
    assert obs0r.p_bin_of(3.99) == 0
    assert obs0r.p_bin_of(4.0) == 1
    assert obs0r.p_bin_of(7.0) == 2
    assert obs0r.p_bin_of(10.0) == 2
    assert obs0r.p_bin_of(0.5) is None
    assert obs0r.p_bin_of(10.5) is None
    assert obs0r.p_bin_of(None) is None


def test_epsilon_profiles():
    d = [0.1, 0.2, 0.3, 0.4]
    R = [2.0, 6.0, 9.0, 13.0]
    ep = obs0r.epsilon_profile(d, R, 16.0)
    assert ep[1.0] == pytest.approx(0.1)
    assert ep[5.0] == pytest.approx(0.2)
    assert ep[9.0] == pytest.approx(0.3)
    assert ep[13.0] == pytest.approx(0.4)
    epp = obs0r.epsilon_profile_p([0.5, 0.1, 0.2], [8.0, 2.0, 5.0])
    assert epp == {0: 0.1, 1: 0.2, 2: 0.5}


def test_interior_maximum():
    assert obs0r.interior_maximum([0.1, 0.3, 0.2])
    assert obs0r.interior_maximum([0.1, 0.2, 0.4, 0.3, 0.15])
    assert not obs0r.interior_maximum([0.1, 0.2, 0.3])  # monotone rise
    assert not obs0r.interior_maximum([0.3, 0.2, 0.1])  # monotone fall
    assert not obs0r.interior_maximum([0.1, 0.3])  # too short
    assert not obs0r.interior_maximum([0.1, float("nan"), 0.05])


def test_sheet_matched_structure():
    L = 4
    g = j2_torus_graph(L)
    c3 = j2_torus_coords(L)
    origin = 0
    dist = dict(nx.single_source_shortest_path_length(g, origin))
    sm = obs0r.sheet_matched(dist, c3, origin, (1, 2), per_slot=3)
    assert set(sm) == {1, 2}
    for r in (1, 2):
        assert len(sm[r]["same"]) <= 3 and len(sm[r]["cross"]) <= 3
        for v in sm[r]["same"]:
            assert dist[v] == r and c3[v][2] == c3[origin][2]
        for v in sm[r]["cross"]:
            assert dist[v] == r and c3[v][2] != c3[origin][2]


def test_c2_permutation_invariance():
    g = build_torus_grid(5)
    perm = {v: 1000 + ((v * 7) % 25) for v in g.nodes()}
    h = nx.relabel_nodes(g, perm)
    go, ho = sorted(g.nodes()), sorted(h.nodes())
    Fg = obs0r.static_field_phi(g, go, go[3], -4.5)
    Fh = obs0r.static_field_phi(h, ho, perm[go[3]], -4.5)
    pg = {v: Fg["phi"][i] for i, v in enumerate(go)}
    ph = {v: Fh["phi"][i] for i, v in enumerate(ho)}
    for v in go:
        assert pg[v] == pytest.approx(ph[perm[v]], rel=1e-9)


def test_branch_projectors_cached_vs_dense():
    # C4 equivalence: projectors from cached eigen == c5 dense path.
    g = j2_torus_graph(6)
    order = sorted(g.nodes())
    E, V, _ = obs0.hamiltonian_system(g, order)
    H = -nx.to_numpy_array(g, nodelist=order, dtype=float)
    a = obs0r.branch_projectors_from_eigen(E, V)
    b = obs0.c5_branch_projectors(H)
    assert a["n_zero"] == b["n_zero"]
    assert np.allclose(a["P_plus"], b["P_plus"], atol=1e-9)
    assert np.allclose(a["P_minus"], b["P_minus"], atol=1e-9)


def test_c3_convention_l16_design_point():
    # Non-campaign size: static TRUE-xi (shell-mean, pure-exp, shells 2..5)
    # must sit near the banked POT-1 value 1/0.5272 = 1.8968 (L-independent).
    # This pins the C3 convention pre-data; the campaign C3 runs at L28.
    L = 16
    g = j2_torus_graph(L)
    order = sorted(g.nodes())
    F = obs0r.static_field_phi(g, order, 0, -8.5)
    assert F["max_imag"] < 1e-9
    assert bool((F["phi"] > 0).all())
    dist = dict(nx.single_source_shortest_path_length(g, 0))
    prof = obs0r.shell_profile(F["phi"], order, dist, 8, stat="mean")
    fit = obs0r.fit_pure_exp([2, 3, 4, 5], [prof[r]["v"] for r in (2, 3, 4, 5)])
    assert fit["ok"]
    assert fit["xi"] == pytest.approx(1.0 / 0.5272, rel=0.10)
    assert max(r for r in range(9) if prof[r]["v"] > 0.05) == 3


def test_expander_toy_pot_contrast():
    # Toy expander: few shells exist; shell-{2..5} fits must no-fit or the
    # (G,P) map must fail monotone validity (C1 design behavior in miniature).
    g = build_random_regular(120, 8, seed=0)
    order = sorted(g.nodes())
    F = obs0r.static_field_phi(g, order, order[0], -8.5)
    dist = dict(nx.single_source_shortest_path_length(g, order[0]))
    prof = obs0r.shell_profile(F["phi"], order, dist, 5, stat="median")
    have = [r for r in (2, 3, 4, 5) if prof[r]["n"] > 0]
    if len(have) >= 3:
        fit = obs0r.fit_yukawa([float(r) for r in have],
                               [prof[r]["v"] for r in have])
        assert (not fit["ok"]) or (not obs0r.yukawa_monotone_ok(fit))


def test_no_dp_estimator_by_design():
    # Pinned honest branch: reintroducing d_P requires deleting this
    # test AND amending OBS0R-PREREG.
    assert not hasattr(obs0r, "dp_from_alpha")
    assert not hasattr(obs0r, "fit_dp_origin")
    assert "d_P" not in dir(obs0r)


def test_obs0_frozen_hash():
    # Historical firewall: obs0.py must be byte-identical to the OBS-0
    # verdict commit (hash recorded in OBS0R-PREREG).
    import hashlib
    import os

    p = os.path.join(os.path.dirname(obs0.__file__), "obs0.py")
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    assert h == "683f7620a0aa00dff886c0e2a5022539bb5cefd6490ce0daa692539c1a55abde"
