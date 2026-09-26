"""BV scaling prototype: Sinkhorn OR + Johnson CPU reference for the GPU run.

Validates the two approximations the N=4096 GPU run will use: Sinkhorn W1
matches the exact transportation LP (gap >= 0, tiny), sparse Johnson matches
Floyd exactly, and Sinkhorn-OR reproduces the exact radial slope p = 0.940
on the weak-field graph. Plus the beta(4096) starting guess and op counts.
"""
import networkx as nx
import numpy as np
from scipy.optimize import linprog

from bh_graph import sinkor as S
from bh_graph.orici import ollivier_curvature
from bh_graph.weakfield import kappa_profile, scaling_power, weak_field_graph


def _exact_w1(C, a, b):
    n, m = C.shape
    A = np.zeros((n + m, n * m))
    for i in range(n):
        A[i, i * m:(i + 1) * m] = 1
    for j in range(m):
        A[n + j, j::m] = 1
    return float(linprog(C.ravel(), A_eq=A, b_eq=np.concatenate([a, b]),
                         bounds=(0, None), method="highs").fun)


def test_sinkhorn_matches_lp():
    rng = np.random.default_rng(0)
    for trial in range(3):
        n, m = 6, 7
        C = rng.uniform(0, 4, (n, m))
        a = rng.dirichlet(np.ones(n))
        b = rng.dirichlet(np.ones(m))
        exact = _exact_w1(C, a, b)
        s = S.sinkhorn_w1(C, a, b, eps=0.02)
        assert s["ok"] and s["converged"]
        assert s["distance"] - exact > -1e-9  # entropic overshoot only
        assert s["distance"] - exact < 0.01
        assert s["marginal_error"] < 1e-8


def test_sinkhorn_bad_inputs_no_raise():
    assert S.sinkhorn_w1([[1]], [1.0], [1.0], eps=-0.1)["ok"] is False
    assert S.sinkhorn_w1([[1, 2]], [0.4, 0.6], [1.0])["ok"] is False
    assert S.sinkhorn_w1([[0.0]], [0.0], [1.0])["ok"] is False
    assert S.ollivier_curvature_sinkhorn(nx.path_graph(3), 0, 99)["ok"] is False


def test_johnson_matches_floyd():
    for g in [nx.path_graph(7), nx.balanced_tree(2, 3),
              nx.grid_graph([4, 4, 4]), nx.complete_graph(6)]:
        dj, _idx = S.all_pairs_johnson(g)
        assert _idx is not None
        nodes = list(g.nodes())
        df = nx.floyd_warshall_numpy(g)
        remap = np.array([[df[nodes.index(u), nodes.index(v)] for v in nodes]
                          for u in nodes])
        assert np.allclose(dj, remap)
    assert S.all_pairs_johnson(nx.Graph()) == (None, None)


def test_johnson_sparse_spot():
    g = nx.grid_graph([12, 12, 12])
    d, _idx = S.all_pairs_johnson(g)
    assert np.isfinite(d).all()
    a, b = (0, 0, 0), (11, 11, 11)
    assert d[_idx[a], _idx[b]] == 33  # Manhattan on the grid


def test_sinkhorn_signs_match_exact():
    t = nx.balanced_tree(2, 3)
    k = nx.complete_graph(6)
    p = nx.path_graph(9)
    for g in (t, k, p):
        edges = list(g.edges())[:8]
        sk = S.kappa_mean_sinkhorn(g, edges, eps=0.02)
        assert sk["ok"] and sk["n"] == len(edges)
        ex = float(np.mean([ollivier_curvature(g, u, v) for u, v in edges]))
        assert abs(sk["mean"] - ex) < 0.02
    assert S.kappa_mean_sinkhorn(t, [(0, 1)], eps=0.02)["mean"] < 0
    assert S.kappa_mean_sinkhorn(k, [(0, 1)], eps=0.02)["mean"] > 0
    assert abs(S.kappa_mean_sinkhorn(p, [(3, 4)], eps=0.02)["mean"]) < 1e-6


def test_sinkhorn_preserves_radial_slope():
    g, pos = weak_field_graph(L=7, n_stubs=40, mode="direct", seed=0)
    p_exact = scaling_power(kappa_profile(g, pos))
    dist, idx = S.all_pairs_johnson(g)
    prof = {}
    for r in (1.5, 2.5, 3.5):
        ks = []
        for u, v in g.edges():
            if not (isinstance(u, tuple) and isinstance(v, tuple)):
                continue
            if len(u) != 3 or len(v) != 3:
                continue
            ru, rv = np.linalg.norm(pos[u]), np.linalg.norm(pos[v])
            if abs(0.5 * (ru + rv) - r) > 0.6 or abs(ru - rv) < 0.5:
                continue
            rr = S.ollivier_curvature_sinkhorn(g, u, v, eps=0.02,
                                               dist=dist, idx=idx)
            if rr["ok"]:
                ks.append(rr["kappa"])
        prof[r] = float(np.mean(ks))
    p_sk = scaling_power(prof)
    assert abs(p_sk - p_exact) < 0.05  # slope physics survives Sinkhorn
    exact_prof = kappa_profile(g, pos)
    for r, v in prof.items():
        assert abs(v - exact_prof[r]) < 0.005


def test_beta_predictor():
    f = S.beta_fit_inv_n()
    assert abs(f["beta_inf"] - 1.112) < 0.005
    assert abs(S.beta_predict(1020) - 1.24) < 0.03
    b = S.beta_predict_4096()
    assert abs(b["point"] - 1.140) < 0.005
    assert b["lo"] < 1.15 < b["hi"] or (abs(b["lo"] - 1.095) < 0.01)
    assert b["lo"] < S.BETA_GPU_GUESS <= b["hi"] + 1e-9
    assert np.isnan(S.beta_predict(-3))


def test_scaling_table_pins_costs():
    t = S.scaling_table()
    assert abs(t["floyd_1020"] - 1.06e9) / 1.06e9 < 0.01
    assert abs(t["floyd_4096"] - 68.7e9) / 68.7e9 < 0.01
    assert abs(t["graphs80_floyd_4096"] - 5.5e12) / 5.5e12 < 0.01
    assert t["lp_4096_grid"] == 12288
    assert t["johnson_4096_grid"] < t["floyd_4096"] / 50.0
    assert np.isnan(S.floyd_cost(-1)) and S.or_lp_count(0) == 0
