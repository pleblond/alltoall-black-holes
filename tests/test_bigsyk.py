import numpy as np
from bh_graph.bigsyk import (
    sparse_syk, sparse_majoranas, typicality_otoc, scaling_big,
)
from bh_graph.syk import syk_hamiltonian, otoc_curve


def test_sparse_matches_dense():
    assert np.allclose(sparse_syk(8, seed=0).toarray(), syk_hamiltonian(8, seed=0))
    chi = sparse_majoranas(8)
    d = chi[0].shape[0]
    assert (chi[0] @ chi[0]).toarray().tolist() == np.eye(d).tolist()


def test_typicality_tracks_exact():
    t = np.linspace(0, 8, 16)
    c_typ = typicality_otoc(sparse_syk(8, seed=1), 4, t, n_samples=4, seed=0)
    c_ex = otoc_curve(syk_hamiltonian(8, seed=1), 4, t)
    assert np.corrcoef(c_typ, c_ex)[0, 1] > 0.9


def test_flat_vs_linear_ordering_small():
    r = scaling_big((8, 12), t_max=8, nt=16, n_samples=2, seed=0)
    # chain grows with size; SYK stays flatter
    assert r["chain"][1] > r["chain"][0]
    assert r["syk"][1] - r["syk"][0] < r["chain"][1] - r["chain"][0]
