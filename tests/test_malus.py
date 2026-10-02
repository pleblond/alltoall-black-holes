"""MALUS-0 sheet-sector apparatus pins (Malus track prereg).

Locks: sheet-swap algebra (S^2 = I, symmetric), projector
completeness/rank, [H,S] = 0, H*P_anti = 0, symmetric sector =
double-amplitude square lattice (exact intertwining), flat-band
decomposition n_zero = N/2 + nodal, sector-weight accounting +
conservation, antisymmetric frozen / symmetric ballistic dynamics,
sheet-polarized 50/50 split. Campaign verdicts are FILED in
docs/DEFERRED.md, not pinned.
"""

import numpy as np

from bh_graph.ballistic import (
    branch_mixing,
    branch_projectors,
    com,
    evolve_fixed,
    fit_velocity,
    gaussian_packet,
    hamiltonian,
    is_normalized_ok,
    is_projector_ok,
    msd_exponent_rs,
    node_order,
    packet_width,
    unwrap_trace,
    velocity_autocorr,
)
from bh_graph.formation import j2_torus_coords, j2_torus_graph
from bh_graph.malus import (
    coarse_cells,
    is_involution_ok,
    is_sheet_accounting_ok,
    is_symmetric_ok,
    nodal_count_square,
    sheet_packet_family,
    sheet_projectors,
    sheet_swap_matrix,
    sheet_weights,
    square_hamiltonian,
    symmetric_embedding,
)


def _setup(L):
    g = j2_torus_graph(L)
    order = node_order(g)
    c3 = j2_torus_coords(L)
    coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    return g, order, c3, coords


def test_sheet_swap_algebra():
    _, order, c3, _ = _setup(6)
    s = sheet_swap_matrix(order, c3)
    assert is_involution_ok(s) and is_symmetric_ok(s)
    assert not is_involution_ok(2 * s) and not is_symmetric_ok(s + sparse_shift(s))


def sparse_shift(s):
    from scipy import sparse

    n = s.shape[0]
    return sparse.csr_matrix(
        (np.ones(n), (np.arange(n), (np.arange(n) + 1) % n)), shape=(n, n)
    )


def test_sheet_projector_algebra():
    _, order, c3, _ = _setup(6)
    pr = sheet_projectors(order, c3)
    n = len(order)
    assert is_projector_ok(pr["P_sym"]) and is_projector_ok(pr["P_anti"])
    assert np.abs(pr["P_sym"] @ pr["P_anti"]).max() < 1e-12  # orthogonal
    assert np.abs(pr["P_sym"] + pr["P_anti"] - np.eye(n)).max() < 1e-12  # complete
    assert abs(np.trace(pr["P_sym"]) - n / 2) < 1e-9  # rank N/2 each
    assert abs(np.trace(pr["P_anti"]) - n / 2) < 1e-9


def test_sheet_sector_commutes_and_anti_dead():
    g, order, c3, _ = _setup(6)
    h = hamiltonian(g, order=order)
    s = sheet_swap_matrix(order, c3)
    comm = (h @ s - s @ h).tocoo()
    assert comm.nnz == 0 or np.abs(comm.data).max() < 1e-12  # [H,S] = 0
    pr = sheet_projectors(order, c3)
    assert np.abs(h.toarray() @ pr["P_anti"]).max() < 1e-12  # H*P_anti = 0
    assert np.abs(h.toarray().T @ pr["P_anti"]).max() < 1e-12  # Hermitian twin


def test_symmetric_sector_is_double_square():
    g, order, c3, _ = _setup(6)
    h = hamiltonian(g, order=order).toarray()
    u, cells = symmetric_embedding(order, c3)
    assert np.abs(u.T @ u - np.eye(len(cells))).max() < 1e-12  # isometry
    hsq = square_hamiltonian(cells, (6, 6))
    assert np.abs(h @ u - u @ hsq).max() < 1e-12  # exact intertwining
    w = np.linalg.eigvalsh(hsq)  # spectrum = -4(cos kx + cos ky)
    k = 2.0 * np.pi * np.arange(6) / 6
    expect = sorted(-4.0 * (a + b) for a in np.cos(k) for b in np.cos(k))
    assert np.allclose(sorted(w), expect, atol=1e-9)


def test_flat_band_decomposition():
    assert nodal_count_square(4) == 6  # hand-counted unit
    for L in (4, 8):
        g, order, c3, _ = _setup(L)
        h = hamiltonian(g, order=order).toarray()
        br = branch_projectors(h)
        assert br["n_zero"] == len(order) // 2 + nodal_count_square(L)
        pr = sheet_projectors(order, c3)  # anti sector sits inside ker H
        assert np.abs(h @ pr["P_anti"]).max() < 1e-12


def test_sheet_weights_accounting():
    _, order, c3, coords = _setup(6)
    pr = sheet_projectors(order, c3)
    rng = np.random.default_rng(0)
    psi = rng.normal(size=len(order)) + 1j * rng.normal(size=len(order))
    psi /= np.linalg.norm(psi)
    w = sheet_weights(psi, pr)
    assert is_sheet_accounting_ok(w["w_sym"], w["w_anti"])
    assert not is_sheet_accounting_ok(0.5, 0.6)
    base = gaussian_packet(coords, order, (1.0, 2.0), (0.3, 0.0), 1.0, periods=(6, 6))
    fam = sheet_packet_family(base, order, c3)
    assert all(is_normalized_ok(p) for p in fam.values())
    assert sheet_weights(fam["sym"], pr)["w_anti"] < 1e-12
    assert sheet_weights(fam["anti"], pr)["w_sym"] < 1e-12
    w0 = sheet_weights(fam["sheet0"], pr)
    assert abs(w0["w_sym"] - 0.5) < 1e-12 and abs(w0["w_anti"] - 0.5) < 1e-12


def test_sector_weight_conserved_free():
    _, order, c3, coords = _setup(6)
    pr = sheet_projectors(order, c3)
    base = gaussian_packet(coords, order, (1.0, 2.0), (0.3, 0.0), 1.0, periods=(6, 6))
    psi0 = sheet_packet_family(base, order, c3)["sheet0"]
    rec = evolve_fixed(psi0, hamiltonian(j2_torus_graph(6), order=order), 0.1, 20)
    ws = [sheet_weights(p, pr)["w_sym"] for p in rec["psi"]]
    assert branch_mixing(ws) < 1e-8  # construction-zero ([H,S] = 0 corollary)


def test_antisymmetric_packet_frozen():
    L = 12
    _, order, c3, coords = _setup(L)
    base = gaussian_packet(coords, order, (3.0, 6.0), (0.3, 0.0), 2.0, periods=(L, L))
    psi0 = sheet_packet_family(base, order, c3)["anti"]
    rec = evolve_fixed(psi0, hamiltonian(j2_torus_graph(L), order=order), 0.1, 30)
    assert np.all(np.abs(rec["norms"] - 1.0) < 1e-8)
    ts = np.arange(31) * 0.1
    rs = unwrap_trace(
        np.array([com(p, coords, order, periods=(L, L)) for p in rec["psi"]]),
        periods=(L, L),
    )
    assert float(np.linalg.norm(rs - rs[0], axis=1).max()) < 1e-6  # no motion
    assert abs(packet_width(rec["psi"][-1], coords, order, periods=(L, L))
               - packet_width(psi0, coords, order, periods=(L, L))) < 1e-6  # no spread
    assert abs(abs(np.vdot(rec["psi"][-1], psi0)) - 1.0) < 1e-8  # stationary state


def test_symmetric_packet_ballistic():
    L, dt, n = 24, 0.1, 80
    _, order, c3, coords = _setup(L)
    base = gaussian_packet(coords, order, (6.0, 12.0), (0.3, 0.0), 3.0, periods=(L, L))
    psi0 = sheet_packet_family(base, order, c3)["sym"]
    rec = evolve_fixed(psi0, hamiltonian(j2_torus_graph(L), order=order), dt, n)
    ts = np.arange(n + 1) * dt
    rs = unwrap_trace(
        np.array([com(p, coords, order, periods=(L, L)) for p in rec["psi"]]),
        periods=(L, L),
    )
    assert msd_exponent_rs(rs, ts) > 1.3  # directed bin (Stage-0 bins)
    assert np.mean(velocity_autocorr(rs, ts)[:10]) > 0.5
    assert fit_velocity(rs, ts)["speed"] > 0.5


def test_sheet_polarized_splits_half_frozen():
    L = 12
    _, order, c3, coords = _setup(L)
    pr = sheet_projectors(order, c3)
    base = gaussian_packet(coords, order, (3.0, 6.0), (0.3, 0.0), 2.0, periods=(L, L))
    psi0 = sheet_packet_family(base, order, c3)["sheet0"]
    rec = evolve_fixed(psi0, hamiltonian(j2_torus_graph(L), order=order), 0.1, 30)
    for p in (rec["psi"][0], rec["psi"][-1]):
        w = sheet_weights(p, pr)
        assert abs(w["w_sym"] - 0.5) < 1e-9 and abs(w["w_anti"] - 0.5) < 1e-9
    frozen_then = pr["P_anti"] @ rec["psi"][-1]  # chi part exactly stationary
    frozen_now = pr["P_anti"] @ rec["psi"][0]
    assert np.linalg.norm(frozen_then - frozen_now) < 1e-8
    moved = pr["P_sym"] @ rec["psi"][-1]  # phi part provably moved
    assert np.linalg.norm(moved - pr["P_sym"] @ rec["psi"][0]) > 1e-3
