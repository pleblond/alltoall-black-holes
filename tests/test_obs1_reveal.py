"""OBS-1 reveal-join tests (tiny substrates; hidden geometry allowed HERE).

These tests pin obs1_reveal.py on J2-L4 / sq-L4 toy graphs. They NEVER run
in the blind stage (C3: analyze_obs1_blind.py cannot import this module).
"""

import numpy as np

from bh_graph import obs1, obs1_reveal
from bh_graph.formation import j2_torus_graph
from bh_graph.graphs import build_torus_grid


def test_hidden_coords_and_wrap_distance():
    c = obs1_reveal.hidden_quotient_coords("j2-L4", 4)
    assert len(c) == 32
    assert c[0] == (0.0, 0.0)
    # Wrap pair: x=0 vs x=3 adjacent across the boundary.
    assert obs1_reveal.torus_distance((0.0, 1.0), (3.0, 1.0), 4) == 1.0
    s = obs1_reveal.hidden_sheets("j2-L4", 4)
    assert s[0] == 0 and s[1] == 1
    assert obs1_reveal.hidden_quotient_coords("exp-N32-s0", 32) is None
    assert obs1_reveal.hidden_sheets("sq-L4", 4) is None
    q = obs1_reveal.hidden_quotient_coords("sq-L4", 4)
    assert q[0] == (0.0, 0.0) and q[15] == (3.0, 3.0)


def test_locality_perfect_and_random():
    g = j2_torus_graph(4)
    nodes = sorted(g.nodes())[:16]
    coords = obs1_reveal.hidden_quotient_coords("j2-L4", 4)
    H = obs1_reveal.hidden_quotient_matrix(coords, nodes, 4)
    thr = obs1_reveal.hidden_near_threshold(H)
    A = (H <= thr)
    np.fill_diagonal(A, False)
    rep = obs1_reveal.locality_report(A, H)
    assert rep["pass"] and rep["frac"] == 1.0
    # Random decile-scale adjacency scores far below the bar.
    rng = np.random.default_rng(0)
    Ar = rng.random((16, 16)) < 0.10
    Ar = np.triu(Ar, 1)
    Ar = Ar | Ar.T
    assert obs1_reveal.locality_report(Ar, H)["frac"] < 0.70


def test_sheet_contrast_quotient_blind():
    g = j2_torus_graph(6)
    nodes = sorted(g.nodes())
    coords = obs1_reveal.hidden_quotient_coords("j2-L6", 6)
    sheets = obs1_reveal.hidden_sheets("j2-L6", 6)
    H = obs1_reveal.hidden_quotient_matrix(coords, nodes, 6)
    # The quotient metric identifies sheets -> zero contrast.
    rep = obs1_reveal.sheet_report(H + 1e-6,
                                   [sheets[v] for v in nodes])
    assert rep["pass"] and rep["contrast"] < 0.05


def test_topology_true_wrap_detection():
    L = 8
    coords = obs1_reveal.hidden_quotient_coords("sq-L8", 8)
    nodes = [0 * L + 0, 0 * L + 7, 3 * L + 3, 7 * L + 0]
    H = obs1_reveal.hidden_quotient_matrix(coords, nodes, L)
    # Pair (0,1): minimal-image 1.0 via the wrap (raw gap 7 > L/2).
    assert H[0, 1] == 1.0
    rep = obs1_reveal.topology_report([[0, 1], [0, 2], [1, 3]],
                                      coords, nodes, L, H)
    assert rep["n"] == 3
    assert rep["n_true"] >= 1


def test_geometry_match_prefers_quotient():
    g = j2_torus_graph(4)
    nodes = sorted(g.nodes())
    coords = obs1_reveal.hidden_quotient_coords("j2-L4", 4)
    Hq = obs1_reveal.hidden_quotient_matrix(coords, nodes, 4)
    Hg = obs1_reveal.hidden_graph_matrix(g, nodes)
    m = obs1_reveal.geometry_match(Hq + 0.01, Hq, Hg)
    assert m["closer"] == "quotient"
    m2 = obs1_reveal.geometry_match(Hg, Hq, Hg)
    assert m2["closer"] == "microscopic"


def test_hidden_alignment_exact():
    coords = obs1_reveal.hidden_quotient_coords("sq-L4", 4)
    nodes = sorted(coords)[:16]
    Y = np.array([coords[v] for v in nodes])
    th = 1.1
    R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    X = (Y @ R) * 0.4 + np.array([5.0, 2.0])
    rep = obs1_reveal.hidden_alignment(X, coords, nodes)
    assert rep["eps"] < 1e-9


def test_local_alignment_recovers_periodic():
    # Blind-like MDS reconstruction of periodic stations: strict global
    # alignment fails (cut+bend ~ 0.9) while local charts and the global
    # dist-match recover the quotient (filed gates).
    rng = np.random.default_rng(7)
    L = 128.0
    pts = rng.random((64, 2)) * L
    d = np.abs(pts[:, None, :] - pts[None, :, :])
    d = np.minimum(d, L - d)
    D = np.sqrt((d ** 2).sum(-1))
    E = rng.normal(0.0, 0.02, D.shape)
    E = (E + E.T) / 2.0
    Dn = D * (1.0 + E)
    np.fill_diagonal(Dn, 0.0)
    X = obs1.classical_mds(Dn, 2)["coords"]
    coords = {i: (float(pts[i, 0]), float(pts[i, 1])) for i in range(64)}
    nodes = list(range(64))
    strict = obs1_reveal.hidden_alignment(X, coords, nodes)
    assert strict["eps"] > 0.3
    loc = obs1_reveal.local_chart_report(Dn, coords, nodes, L)
    assert loc["pass"] and loc["med"] <= 0.30
    H = np.zeros((64, 64))
    for i in range(64):
        for j in range(64):
            H[i, j] = obs1_reveal.torus_distance(coords[i], coords[j], L)
    assert obs1_reveal.dist_match(Dn, H)["pass"]


def test_dist_match_rejects_star():
    H = np.arange(64, dtype=float)
    H = np.abs(H[:, None] - H[None, :])
    S = np.full((64, 64), 2.0)
    S[0, 1:] = S[1:, 0] = 1.0
    np.fill_diagonal(S, 0.0)
    assert not obs1_reveal.dist_match(S, H)["pass"]


def test_graph_matrix_matches_bfs():
    g = build_torus_grid(4)
    nodes = [0, 1, 5, 10]
    H = obs1_reveal.hidden_graph_matrix(g, nodes)
    assert H[0, 1] == 1.0 and H[0, 0] == 0.0
    assert (H == H.T).all()
