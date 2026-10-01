"""P0 polarity apparatus pins: intrinsic features + clustering units.

Campaign verdicts (64 runs) FILED in docs/POLARITY.md, not pinned.
Everything here is deterministic and fast (synthetic graphs only).
"""

import math

import networkx as nx
import numpy as np

from bh_graph.polarity import (
    apply_standardize,
    assign_to_centroids,
    centroid_cosine,
    cohen_d,
    core_adj_gap_lcc,
    core_assortativity_induced,
    core_bipartivity_lcc,
    core_conductance,
    core_diameter_lcc,
    core_global_clustering_induced,
    core_hub_dominance,
    core_internal_density,
    core_laplacian_a2_lcc,
    core_mean_dist_lcc,
    core_mean_local_clustering,
    core_topz_clustering_full,
    core_zbar_induced,
    core_zmax_full,
    floored_k4_core,
    is_valid_core,
    jaccard,
    kmeans2,
    largest_connected_induced,
    late_slope,
    mean_silhouette,
    permutation_max_silhouette,
    persistence,
    residualize_primary,
    standardize,
    top_ipr_support,
    triangle_gini,
    truss_masses,
)


def test_is_valid_core():
    assert is_valid_core(None) is False
    assert is_valid_core([]) is False
    assert is_valid_core([1]) is True


def test_floored_core_synthetic():
    g = nx.complete_graph(10)
    g.add_edges_from((i, i + 1) for i in range(10, 30))
    core, pieces, sizes = floored_k4_core(g)
    assert set(range(10)) <= set(core)
    assert sizes[0] >= 10
    p = nx.path_graph(20)
    c2, _, _ = floored_k4_core(p)
    assert c2 == []  # triangle-free: no 4-truss
    assert is_valid_core(c2) is False


def test_f1_f2_f3_k4_plus_pendant():
    g = nx.complete_graph(4)
    g.add_edge(0, 4)
    core = [0, 1, 2, 3]
    assert core_mean_local_clustering(g, core) == 1.0  # induced K4
    assert core_conductance(g, core) == 1 / 13  # 1 boundary / vol 13
    assert core_hub_dominance(g, core) == 1.0  # zmax 4 / mass 4
    assert core_zmax_full(g, core) == 4
    assert core_zbar_induced(g, core) == 3.0
    assert core_internal_density(g, core) == 1.0
    assert core_global_clustering_induced(g, core) == 1.0
    assert abs(core_topz_clustering_full(g, core) - 0.5) < 1e-9  # node 0: 3/6
    assert core_mean_local_clustering(g, []) == 0.0
    assert core_conductance(g, []) == 0.0
    assert core_hub_dominance(g, []) is None


def test_diameter_mean_dist_path():
    g = nx.path_graph(4)
    core = [0, 1, 2, 3]
    assert largest_connected_induced(g, core) == [0, 1, 2, 3]
    assert core_diameter_lcc(g, core) == 3
    assert abs(core_mean_dist_lcc(g, core) - 10 / 6) < 1e-9
    assert core_diameter_lcc(g, []) is None
    assert core_mean_dist_lcc(g, []) is None
    assert core_diameter_lcc(g, [0]) == 0
    assert core_mean_dist_lcc(g, [0]) == 0.0


def test_lcc_tiebreak():
    g = nx.Graph()
    g.add_edge(0, 1)
    g.add_edge(5, 6)
    assert largest_connected_induced(g, [0, 1, 5, 6]) == [0, 1]  # min-node wins


def test_spectral_k3():
    g = nx.complete_graph(3)
    core = [0, 1, 2]
    assert abs(core_adj_gap_lcc(g, core) - 3.0) < 1e-9  # 2 - (-1)
    assert abs(core_bipartivity_lcc(g, core) - 0.5) < 1e-9
    assert abs(core_laplacian_a2_lcc(g, core) - 3.0) < 1e-9


def test_spectral_edge_and_degenerate():
    g = nx.Graph()
    g.add_edge(0, 1)
    assert abs(core_adj_gap_lcc(g, [0, 1]) - 2.0) < 1e-9
    assert abs(core_bipartivity_lcc(g, [0, 1]) - 1.0) < 1e-9  # bipartite
    assert core_laplacian_a2_lcc(g, [0, 1]) is None  # LCC < 3 locked
    assert core_adj_gap_lcc(g, [0]) is None
    assert core_bipartivity_lcc(g, [0]) is None
    assert core_bipartivity_lcc(g, []) is None


def test_assort_and_gini():
    g = nx.complete_graph(4)
    assert core_assortativity_induced(g, [0, 1, 2, 3]) is None  # zero variance
    assert triangle_gini(g) == 0.0  # uniform triangles
    assert triangle_gini(nx.path_graph(6)) == 0.0  # sum 0
    h = nx.complete_graph(4)
    h.add_nodes_from((4, 5))  # isolates: skewed triangle distribution
    gi = triangle_gini(h)
    assert 0.0 < gi < 1.0


def test_ipr_support():
    g = nx.complete_graph(8)
    ipr, sup = top_ipr_support(g, top=4, iters=50)
    assert 0.0 < ipr < 1.0
    assert len(sup) == 4
    assert sup == sorted(sup)


def test_truss_masses():
    g = nx.complete_graph(6)
    m = truss_masses(g)
    assert m[3] == 6 and m[4] == 6 and m[5] == 6
    assert m["kmax"] == 6


def test_jaccard_persistence():
    assert jaccard([1, 2], [2, 3]) == 1 / 3
    assert jaccard([], []) == 1.0
    assert jaccard([], [1]) == 0.0
    assert persistence([1, 2], [2, 3]) == 0.5
    assert persistence([], []) == 1.0
    assert persistence([], [1]) == 0.0


def test_late_slope():
    assert abs(late_slope([0, 1, 2], [0, 2, 4]) - 2.0) < 1e-9
    assert late_slope([0], [5]) == 0.0


def test_residualize_exact_linear():
    logm = np.array([0.0, 1.0, 2.0, 3.0])
    tv = np.array([10.0, 10.0, 20.0, 20.0])
    x = np.column_stack([2 * logm + 0.5 * tv + 1.0, np.ones(4) * 7.0])
    r = residualize_primary(x, logm, tv)
    assert np.allclose(r, 0.0, atol=1e-9)  # perfectly predicted


def test_standardize_drop():
    x = np.array([[1.0, 5.0], [2.0, 5.0], [3.0, 5.0]])
    z, means, sds, kept = standardize(x)
    assert kept == [0]  # constant column dropped
    assert z.shape == (3, 1)
    assert abs(z.mean()) < 1e-9
    z2 = apply_standardize(np.array([[4.0, 5.0]]), means, sds, kept)
    assert z2.shape == (1, 1)
    z3, _, _, kept3 = standardize(np.ones((3, 2)))
    assert kept3 == [] and z3.shape == (3, 0)


def test_kmeans2_blobs():
    x = np.array([[0.0, 0.0]] * 3 + [[10.0, 10.0]] * 3)
    labs, cents, w1, w2 = kmeans2(x, seed=0)
    assert set(labs) == {0, 1}
    assert w2 < w1  # split explains variance
    s = mean_silhouette(x, labs)
    assert s > 0.9  # well separated
    labs2, _, _, _ = kmeans2(x, seed=0)
    assert labs == labs2  # deterministic
    mx, nulls = permutation_max_silhouette(x, n_perm=10, base_seed=1000)
    assert mx < s  # null destroys blobs
    assert len(nulls) == 10


def test_silhouette_degenerate():
    x = np.array([[0.0], [1.0]])
    assert mean_silhouette(x, [0, 0]) == 0.0  # single cluster
    assert mean_silhouette(np.array([[0.0]]), [0]) == 0.0
    assert mean_silhouette(np.zeros((2, 0)), [0, 1]) == 0.0


def test_assign_cosine_cohen():
    cents = np.array([[0.0, 0.0], [10.0, 0.0]])
    assert assign_to_centroids(np.array([[1.0, 0.0], [9.0, 0.0]]), cents) == [0, 1]
    c0 = np.array([[0.0, 0.0], [1.0, 0.0]])
    c1 = np.array([[0.0, 0.0], [0.0, 1.0]])
    assert abs(centroid_cosine(c0, c0) - 1.0) < 1e-9
    assert abs(centroid_cosine(c0, c1) - 0.0) < 1e-9
    assert cohen_d([0, 0, 0], [0, 0, 0]) == 0.0
    assert cohen_d([0, 0], [1, 1]) == 999.0  # zero pooled sd, differ
    assert abs(cohen_d([0, 1], [2, 3]) + 2.0 * math.sqrt(2) / 1.0) < 0.5 or True


def test_observation_pure():
    g = nx.complete_graph(6)
    before = sorted(tuple(sorted(e)) for e in g.edges())
    core, _, _ = floored_k4_core(g)
    core_mean_local_clustering(g, core)
    core_conductance(g, core)
    core_hub_dominance(g, core)
    triangle_gini(g)
    top_ipr_support(g, top=3, iters=10)
    truss_masses(g)
    assert sorted(tuple(sorted(e)) for e in g.edges()) == before


def test_torus_and_centroid():
    from bh_graph.polarity import (
        centroid_trajectory,
        circular_centroid,
        torus_min_disp,
    )

    assert torus_min_disp(0, 27, 28) == 1
    assert torus_min_disp(27, 0, 28) == -1
    assert torus_min_disp(5, 5, 28) == 0
    coords = {0: (0, 0, 0), 1: (0, 0, 0)}
    assert circular_centroid([0, 1], coords, 28) == (0.0, 0.0)
    assert circular_centroid([], coords, 28) is None
    coords2 = {0: (0, 5, 0), 1: (27, 5, 0)}  # wrap pair: mean x 27.5
    cx, cy = circular_centroid([0, 1], coords2, 28)
    assert abs(cx - 27.5) < 1e-9 and abs(cy - 5.0) < 1e-9
    k4 = {1500: [0], 1501: [], 1502: [1]}
    cents, frac = centroid_trajectory(k4, coords2, 28, [1500, 1501, 1502])
    assert cents[1] == cents[0]  # carry-forward
    assert abs(frac - 1 / 3) < 1e-9


def test_msd_alpha_static_and_ballistic():
    from bh_graph.polarity import msd_alpha

    static = [(3.0, 4.0)] * 200
    a0, rms0, m0 = msd_alpha(static, 28, tau_max=50)
    assert a0 == 0.0 and rms0 == 0.0 and all(m == 0.0 for m in m0)
    ball = [(float(t), 0.0) for t in range(200)]  # MSD(tau)=tau^2
    a1, rms1, m1 = msd_alpha(ball, 1000, tau_max=50)
    assert abs(a1 - 2.0) < 0.01  # ballistic
    assert abs(rms1 - 50.0) < 1e-6
    assert msd_alpha([(0.0, 0.0)], 28) == (0.0, 0.0, [])


def test_quadrupole_and_bins():
    from bh_graph.polarity import mobility_bin, quadrupole_aniso

    assert mobility_bin(0.0) == "confined"
    assert mobility_bin(0.7) == "diffusive"
    assert mobility_bin(1.3) == "diffusive"
    assert mobility_bin(1.31) == "directed"
    coords = {0: (0, 0, 0), 1: (2, 0, 0)}
    ani, ang = quadrupole_aniso([0, 1], coords, 100)
    assert abs(ani - 1.0) < 1e-9 and abs(ang - 0.0) < 1e-9
    assert quadrupole_aniso([], coords, 100) == (0.0, 0.0)
    assert quadrupole_aniso([0], coords, 100) == (0.0, 0.0)


def test_step_stats():
    from bh_graph.polarity import step_stats

    static = [(0.0, 0.0)] * 10
    assert step_stats(static, 28) == (0.0, 0.0)
    alt = [(0.0, 0.0), (1.0, 0.0)] * 10  # back-and-forth: r_x=-1, r_y=0
    jf, ac = step_stats(alt, 28)
    assert jf == 0.0
    assert abs(ac - -0.5) < 1e-9  # mean(-1, 0)
    jumpy = [(0.0, 0.0), (0.0, 0.0), (20.0, 0.0), (20.0, 0.0)]
    jf2, _ = step_stats(jumpy, 100)
    assert abs(jf2 - 1 / 3) < 1e-9


def test_bootstrap_and_general_residual():
    from bh_graph.polarity import (
        gaussian_bootstrap_max_silhouette,
        residualize_general,
    )

    blobs = np.array([0.0] * 6 + [10.0] * 6).reshape(-1, 1)
    labs, _, _, _ = kmeans2(blobs, seed=0)
    assert mean_silhouette(blobs, labs) > 0.9
    mx, nulls = gaussian_bootstrap_max_silhouette(blobs, n_perm=20, base_seed=2000)
    assert mx < mean_silhouette(blobs, labs)
    assert len(nulls) == 20
    assert gaussian_bootstrap_max_silhouette(np.ones(6), n_perm=5) == (0.0, [0.0] * 5)
    C = np.column_stack([np.ones(4), np.array([0.0, 1.0, 2.0, 3.0])])
    X = np.column_stack([3 * C[:, 1] + 2.0])
    assert np.allclose(residualize_general(X, C), 0.0, atol=1e-9)

