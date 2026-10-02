"""SPEC apparatus pins (bound-state spectroscopy prereg).

Locks: dense-spectrum correctness/orthonormality, enrichment/shell/sheet/
dormant units, candidate ranking + nonflat rule, isolation/window-contrast
units, degree-preserving rewiring, R/T partition accounting, incoming-energy
readout, driven-run unitarity/determinism + transfer units. Campaign numbers
are FILED in docs/DEFERRED.md, not pinned.
"""

import networkx as nx
import numpy as np

from bh_graph.ballistic import (
    branch_projectors,
    branch_weights_all,
    hamiltonian,
    ipr,
    is_accounting_ok,
    is_normalized_ok,
    node_order,
    region_weight,
)
from bh_graph.formation import j2_torus_coords, j2_torus_graph
from bh_graph.spectroscopy import (
    dormant_sheet_of,
    driven_run,
    enrich,
    full_spectrum,
    incoming_energy,
    is_degree_sequence_ok,
    is_orthonormal_ok,
    isolation_ratios,
    rewired_control,
    rt_partition,
    sheet_index_sets,
    shell1_union,
    top_candidates_by_enrich,
    top_nonflat_candidate,
    transfer_trace,
    window_contrast,
)


def _small_graph():
    g = nx.cycle_graph(10)
    order = node_order(g)
    h = hamiltonian(g, order=order)
    return g, order, h


def test_full_spectrum_cycle_exact():
    g, order, h = _small_graph()
    spec = full_spectrum(h)
    w = spec["evals"]
    assert len(w) == 10 and bool(np.all(np.diff(w) >= 0))  # ascending
    assert abs(w[0] + 2.0) < 1e-12 and abs(w[-1] - 2.0) < 1e-12  # cycle band edges
    assert is_orthonormal_ok(spec["evecs"])
    assert not is_orthonormal_ok(2.0 * spec["evecs"])
    for i in range(10):  # eigen-equation per mode
        assert np.allclose(h @ spec["evecs"][:, i], w[i] * spec["evecs"][:, i], atol=1e-9)
        assert is_normalized_ok(spec["evecs"][:, i])


def test_spectrum_determinism():
    _, _, h = _small_graph()
    assert np.array_equal(full_spectrum(h)["evals"], full_spectrum(h)["evals"])


def test_enrich_shell_sheet_dormant_units():
    assert enrich(0.5, 10, 100) == 5.0  # 5x delocalized
    assert enrich(0.1, 10, 100) == 1.0  # extended baseline
    g = nx.path_graph(6)
    assert shell1_union(g, [2]) == {1, 2, 3}  # K + 1-hop in own adjacency
    c3 = {v: (v, 0, v % 2) for v in range(6)}
    s0, s1 = sheet_index_sets(c3, list(range(6)))
    assert s0 == [0, 2, 4] and s1 == [1, 3, 5]
    assert dormant_sheet_of([0, 1, 2], c3) == 1  # K-majority b=0 -> dormant 1
    assert dormant_sheet_of([1, 3], c3) == 0
    assert dormant_sheet_of([0, 1], c3) == 1  # tie -> b*=0 -> dormant 1


def test_candidate_ranking_and_nonflat():
    e = [1.0, 5.0, 3.0, 5.0]
    assert top_candidates_by_enrich(e, k=2) == [1, 3]  # desc, stable ties
    w = np.array([0.0, 2.0, -1.0, 0.0])
    assert top_nonflat_candidate(w, e) == 1  # top enriched nonflat
    assert top_nonflat_candidate(np.zeros(4), e) == 1  # all-flat fallback: top enrich


def test_isolation_and_window_contrast_units():
    w = np.array([0.0, 1.0, 1.1, 3.0])  # gaps 1.0, 0.1, 1.9
    iso = isolation_ratios(w, [2], window=5)
    assert abs(iso[2] - 0.1 / 1.0) < 1e-12  # min-gap / median-gap
    bare_w = np.array([0.9, 1.0, 1.1, 5.0])
    bare_q = np.array([0.01, 0.02, 0.03, 0.5])
    assert window_contrast(1.0, 0.2, bare_w, bare_q, 0.5) == 0.2 / 0.02
    assert np.isnan(window_contrast(9.0, 0.2, bare_w, bare_q, 0.5))  # empty window


def test_rewired_control_preserves_degrees():
    g = j2_torus_graph(4)
    h = rewired_control(g, seed=1001)
    assert is_degree_sequence_ok(g, h)
    assert h.number_of_nodes() == g.number_of_nodes()
    assert h.number_of_edges() == g.number_of_edges()
    assert is_degree_sequence_ok(g, rewired_control(g, seed=1001))  # deterministic seed
    assert not is_degree_sequence_ok(g, nx.path_graph(g.number_of_nodes()))


def test_rt_partition_accounting():
    L = 6
    g = j2_torus_graph(L)
    order = node_order(g)
    c3 = j2_torus_coords(L)
    coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    mask = [0, 1, 2, 3]
    part = rt_partition(coords, order, (0.0, 0.0), (3.0, 0.0), mask, periods=(L, L))
    n = len(order)
    assert len(part["incident"]) + len(part["transmitted"]) + len(mask) + part["zero"] == n
    psi = np.full(n, 1 / np.sqrt(n), dtype=complex)  # R+T+w+z = 1 exactly
    tot = (
        region_weight(psi, part["incident"])
        + region_weight(psi, part["transmitted"])
        + region_weight(psi, [order.index(v) for v in mask])
        + part["zero"] / n
    )
    assert abs(tot - 1.0) < 1e-12


def test_incoming_energy_unit():
    g, order, h = _small_graph()
    spec = full_spectrum(h)
    for i in (0, 5, 9):  # eigenstate energy = eigenvalue
        assert abs(incoming_energy(spec["evecs"][:, i], h) - spec["evals"][i]) < 1e-9


def test_branch_accounting_on_eigenmodes():
    g = j2_torus_graph(4)
    order = node_order(g)
    h = hamiltonian(g, order=order)
    br = branch_projectors(h)
    spec = full_spectrum(h)
    for i in (0, len(order) // 2, len(order) - 1):
        w = branch_weights_all(spec["evecs"][:, i], br)
        assert is_accounting_ok(w["w_plus"], w["w_zero"], w["w_minus"])


def test_ipr_localized_vs_uniform():
    n = 40
    loc = np.zeros(n, dtype=complex)
    loc[5] = 1.0
    assert ipr(loc) == 1.0
    assert abs(ipr(np.full(n, 1 / np.sqrt(n), dtype=complex)) - 1 / n) < 1e-12


def test_driven_run_unitary_deterministic():
    g, order, _ = _small_graph()
    a = nx.to_scipy_sparse_array(g, nodelist=order, format="csr", dtype=float)
    psi0 = np.zeros(len(order), dtype=complex)
    psi0[0] = 1.0
    r1 = driven_run(psi0, a, omega=1.0, delta_j=0.05, dt=0.1, n_steps=20)
    r2 = driven_run(psi0, a, omega=1.0, delta_j=0.05, dt=0.1, n_steps=20)
    assert r1["psi"].shape == (21, len(order))
    assert np.all(np.abs(r1["norms"] - 1.0) < 1e-8)  # piecewise-unitary
    assert np.array_equal(r1["psi"], r2["psi"])
    tr = transfer_trace(r1["psi"], psi0)
    assert tr.shape == (21,) and abs(tr[0] - 1.0) < 1e-12  # survival starts at 1
    assert bool(np.all((tr >= 0.0) & (tr <= 1.0 + 1e-9)))
