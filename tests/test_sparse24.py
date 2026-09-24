import numpy as np
from bh_graph.sparse24 import triplet_syk, thermal_typicality_otoc
from bh_graph.bigsyk import sparse_syk
from bh_graph.syk import syk_hamiltonian
from bh_graph.mss import thermal_otoc


def test_triplet_matches_sparse_and_dense():
    assert np.allclose(triplet_syk(8, seed=0).toarray(), sparse_syk(8, seed=0).toarray())
    assert np.allclose(triplet_syk(8, seed=2).toarray(), syk_hamiltonian(8, seed=2))


def test_triplet_hermitian_at_20():
    h = triplet_syk(20, seed=0)
    assert h.shape == (1024, 1024)
    diff = (h - h.conj().T).nnz
    assert diff == 0


def test_thermal_typicality_tracks_exact():
    t = np.linspace(0, 8, 16)
    c_typ = thermal_typicality_otoc(triplet_syk(8, seed=1), 4, 1.0, t, 4, 0)
    c_ex = thermal_otoc(syk_hamiltonian(8, seed=1), 4, 1.0, t)
    assert np.corrcoef(c_typ, c_ex)[0, 1] > 0.85
