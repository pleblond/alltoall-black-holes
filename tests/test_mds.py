"""D12 MDS readout: Tier-1 hop-distance calibration + Delaunay bowl control.

cMDS (B = -1/2 J D^2 J) is the embedding-dimension readout for the
holographic+relational program: a future attractive-dynamics distance
claims 3D only by beating its substrate's null profile with an
N-stable lam3/lam4 gap AND a non-radial v3. Calibration (pinned):
lattice/gabriel/knn hop shows lam1,lam2 dominance (lam2/lam3 > 3);
Delaunay hop shows a radial tortuosity bowl (v3 <-> r^2 > 0.85,
lam3/lam4 ~ 5-6) -- the null INCLUDES a third axis here, so any
del-based rank-3 claim must clear that bar with v3 decorrelated
from radial/tortuosity fields.
"""
import networkx as nx
import numpy as np

from bh_graph import graphs as G


def _cmds(D):
    """Classical MDS: eigenvalues (desc) and vectors of -1/2 J D^2 J."""
    D2 = np.asarray(D, dtype=float) ** 2
    n = D2.shape[0]
    J = np.eye(n) - np.ones((n, n)) / n
    w, V = np.linalg.eigh(-0.5 * J @ D2 @ J)
    return w[::-1], V[:, ::-1]


def _ev_profile(g):
    D = nx.floyd_warshall_numpy(g)
    return _cmds(D)


def test_mds_two_dominant_on_lattice_like():
    # Grid/tri/hex/gabriel/knn hop: lam1,lam2 dominant (GoF2 > 0.7,
    # lam2/lam3 > 3), no lam3/lam4 gap (all < 2.5). The 2D-fabric
    # null profile an attractive-dynamics distance must beat.
    subs = {
        "grid": G.build_grid_2d(20),
        "tri": G.build_triangular_lattice(25),
        "hex": G.build_hex_lattice(25),
        "gab": G.build_gabriel(n_points=625, seed=0),
        "knn": G.build_knn(n_points=625, seed=0),
    }
    for name, g in subs.items():
        ev, _ = _ev_profile(g)
        pos = ev[ev > 0].sum()
        assert ev[:2].sum() / pos > 0.7, (name, ev[:4])
        assert ev[1] / ev[2] > 3.0, (name, ev[:4])
        assert ev[2] / ev[3] < 2.5, (name, ev[:4])


def test_mds_delaunay_bowl_control():
    # Delaunay-hop null INCLUDES a third axis (lam3/lam4 ~ 5-6, all
    # seeds, strengthening with N) -- diagnosed as a radial tortuosity
    # bowl: v3 correlates > 0.85 with centered r^2 AND per-node
    # tortuosity (hop/Euclidean MGM). Regression guard: any del-based
    # rank-3 claim must beat THIS bar with v3 decorrelated from r^2.
    from scipy.spatial.distance import cdist

    n, seed = 625, 0
    g = G.build_poisson_delaunay(n_points=n, seed=seed)
    pts = G.poisson_points(n, 40.0, seed)
    D = nx.floyd_warshall_numpy(g)
    ev, V = _cmds(D)
    assert 4.5 < ev[2] / ev[3] < 7.0, ev[:4]
    x, y = pts[:, 0] - 20, pts[:, 1] - 20
    r2 = x**2 + y**2
    assert abs(np.corrcoef(V[:, 2], r2)[0, 1]) > 0.85
    De = cdist(pts, pts)
    with np.errstate(divide="ignore", invalid="ignore"):
        tort = np.nanmean(np.where(De > 0, D / np.maximum(De, 1e-9), np.nan), axis=1)
    assert abs(np.corrcoef(V[:, 2], tort)[0, 1]) > 0.8


def test_shell_mds_rank_is_order_one():
    # Dilemma-lemma leg (D12): within-shell hop MDS on the L=40 grid is
    # a scale-invariant ring profile -- lam1 == lam2 dominant pair,
    # GoF2 = 0.772 at EVERY radius 5..14, rank O(1). Shells carry no
    # growing independent relational content: honest per-shell counts
    # (nodes ~r, cut 8r+4, MDS rank O(1)) never reach r^2, while the
    # only r^2 count (cumulative ball) violates shell-independence by
    # construction. d_H = 2 XOR independence on 2D fabric.
    L = 40
    g = nx.convert_node_labels_to_integers(nx.grid_2d_graph(L, L), ordering="sorted")
    src = (L // 2) * L + L // 2
    d = dict(nx.single_source_shortest_path_length(g, src))
    Dfull = nx.floyd_warshall_numpy(g)
    nodes = list(g.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    for r in (5, 8, 11, 14):
        sh = [v for v in nodes if d[v] == r]
        ii = [idx[v] for v in sh]
        ev, _ = _cmds(Dfull[np.ix_(ii, ii)])
        pos = ev[ev > 0].sum()
        assert ev[0] / ev[1] < 1.01, (r, ev[:4])
        assert 0.76 < ev[:2].sum() / pos < 0.78, (r, ev[:4])


def test_fpt_mds_two_dominant():
    # First DYNAMICAL distance null (D12): mean SI first-passage time
    # (beta=0.5, K=100, 10x10 grid) reads cleanly 2-dominant under MDS
    # (GoF2 ~ 0.89, lam2/lam3 ~ 17.5 -- MORE Euclidean than hop's 6.8:
    # stochastic averaging smooths lattice anisotropy). Dynamical
    # generation alone does not select 3D -- rank-3 remains a nontrivial
    # dynamical property to hunt (biased/attractive variants queued).
    from bh_graph.scrambling import si_fpt_matrix

    g = nx.convert_node_labels_to_integers(nx.grid_2d_graph(10, 10), ordering="sorted")
    ev, _ = _cmds(si_fpt_matrix(g, 0.5, 100, seed=0))
    pos = ev[ev > 0].sum()
    assert ev[:2].sum() / pos > 0.85, ev[:4]
    assert ev[1] / ev[2] > 12.0, ev[:4]
    assert (-ev[ev < 0]).sum() / pos < 0.1, ev[:4]


def test_observer_geometry_fragile_to_binary_longs():
    # Tolerance curve, unweighted baseline (square L=20, damage seed 3):
    # binary "weak" wiring is an oxymoron -- 2 longs collapse MDS
    # 2-dominance (lam2/lam3 6.82 -> 1.93, GoF2 0.769 -> 0.632); by 30
    # longs GoF2 0.385, participation ratio 3.3 -> 10.3, kappa^2
    # 0.0645. lam3/lam4 never gaps (~1.1-1.7): weak binary wiring
    # blurs 2D, never builds 3D. The measurement that forces weights:
    # no binary knob is weak (a binary long edge is maximally strong).
    from bh_graph.blind_u import kappa2_census
    from bh_graph.update_rule import inject_shortcuts, locality_p, total_longs

    g = nx.convert_node_labels_to_integers(nx.grid_2d_graph(20, 20), ordering="sorted")
    src = 10 * 20 + 10
    rows = {
        # ns: (longs, p-band, l23-band, gof2-band, k2-band-or-None)
        0: (0, (1.83, 1.84), (6.5, 7.0), (0.76, 0.78), 0.0),
        1: (2, (1.91, 1.92), (1.8, 2.1), (0.62, 0.65), None),
        10: (30, (2.36, 2.37), (1.8, 2.1), (0.37, 0.40), 0.0645),
    }
    for ns, (longs_exp, pb, l23b, g2b, k2) in rows.items():
        h = inject_shortcuts(g, ns, 3)
        assert total_longs(h) == longs_exp
        assert pb[0] < locality_p(h, src) < pb[1], ns
        ev, _ = _ev_profile(h)
        pos = ev[ev > 0].sum()
        assert l23b[0] < ev[1] / ev[2] < l23b[1], (ns, ev[:4])
        assert g2b[0] < ev[:2].sum() / pos < g2b[1], (ns, ev[:4])
        assert ev[2] / ev[3] < 2.0, (ns, ev[:4])
        if k2 is not None:
            got = kappa2_census(h)["mean_k2"]
            assert abs(got - k2) < (1e-9 if k2 == 0.0 else 0.005), (ns, got)
