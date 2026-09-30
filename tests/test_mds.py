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
