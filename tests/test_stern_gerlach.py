"""SG splitter + detector apparatus pins (SG-PREREG, docs/STERN_GERLACH.md).

Locks: g=0 reduces to -J*A exactly; Hermitian + hopping-only for all g;
[H_SG, S] = 0 (sheet-blind); exact transverse nulls (Dy(0) = 0,
Dy(-g) = -Dy(+g)); frozen SPLIT detector calibration (synthetic
double fires, single/flat/free do not); profile/seam/persistence units.
Campaign numbers are FILED in docs/STERN_GERLACH.md, not pinned.
"""

import numpy as np
from scipy import sparse

from bh_graph.ballistic import (
    com,
    evolve_fixed,
    gaussian_packet,
    hamiltonian,
    is_hermitian_ok,
    is_normalized_ok,
    node_order,
)
from bh_graph.formation import j2_torus_coords, j2_torus_graph
from bh_graph.graphs import build_torus_grid
from bh_graph.stern_gerlach import (
    commutes_ok,
    gaussian_ring_profile,
    is_involution_ok,
    is_zero_diagonal_ok,
    min_image_delta,
    seam_weight,
    sheet_packet_family,
    sheet_swap_csr,
    smooth_ring_profile,
    split_fires,
    split_persists,
    split_statistic,
    splitter_hamiltonian,
    transverse_profile,
    transverse_width,
)

G0 = 0.02  # frozen weak-gradient scale (prereg section 3)


def _j2_setup(L=6):
    g = j2_torus_graph(L)
    order = node_order(g)
    c3 = j2_torus_coords(L)
    xy = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    return g, order, c3, xy


def test_splitter_reduces_to_bare_at_zero_gradient():
    g, order, _, xy = _j2_setup()
    h0 = splitter_hamiltonian(g, order, xy, 3.0, 0.0, 6).toarray()
    assert np.array_equal(h0, hamiltonian(g, order=order).toarray())  # exact, not close
    tg = build_torus_grid(8)
    torder = node_order(tg)
    txy = {v: (float(v // 8), float(v % 8)) for v in torder}
    assert np.array_equal(
        splitter_hamiltonian(tg, torder, txy, 4.0, 0.0, 8).toarray(),
        hamiltonian(tg, order=torder).toarray(),
    )


def test_splitter_hermitian_and_hopping_only():
    g, order, _, xy = _j2_setup()
    for grad in (G0 / 2, G0, 2 * G0, -G0):
        h = splitter_hamiltonian(g, order, xy, 3.0, grad, 6)
        assert is_hermitian_ok(h)
        assert is_zero_diagonal_ok(h)
        assert not is_zero_diagonal_ok(h + np.eye(len(order)) * 0.5)


def test_y_bonds_only_modulated():
    g, order, _, xy = _j2_setup(L=4)
    h = splitter_hamiltonian(g, order, xy, 2.0, G0, 4).toarray()
    pos = {v: i for i, v in enumerate(order)}
    for u, v in g.edges():
        w = h[pos[u], pos[v]]
        if min_image_delta(xy[v][1], xy[u][1], 4) == 0.0:
            assert w == -1.0  # x/sheet-flip bonds untouched
        else:
            assert w != -1.0 and abs(w + 1.0) < G0 * 2.0 + 1e-12  # weak modulation


def test_splitter_sheet_blind_commutes_with_swap():
    g, order, c3, xy = _j2_setup(L=4)
    s = sheet_swap_csr(order, c3)
    assert is_involution_ok(s)
    assert (s != s.T).nnz == 0  # symmetric permutation
    for grad in (0.0, G0, -G0):
        assert commutes_ok(splitter_hamiltonian(g, order, xy, 2.0, grad, 4), s)
    n = len(order)
    assert not commutes_ok(s, sparse.diags(np.arange(n, dtype=float)))  # generic D breaks [S,D]


def _dy(g, order, xy, c3, L, grad, k=(0.3, 0.0), sigma=3.0, t_end=2.0, shape="linear"):
    # Pin regime L=24/sigma=3/T=2 (localized, NOT a campaign cell: the
    # campaign runs L28/T=10 and TG30/T=25). Self-policing width assert
    # keeps COM branch-meaningful (wrap interference voids COM).
    x0, y0 = L / 4.0, L / 2.0
    psi0 = gaussian_packet(xy, order, (x0, y0), k, sigma, periods=(L, L))
    h = splitter_hamiltonian(g, order, xy, y0, grad, L, shape=shape)
    rec = evolve_fixed(psi0, h, 0.1, int(t_end / 0.1))
    assert np.all(np.abs(rec["norms"] - 1.0) < 1e-8)
    _, prof = transverse_profile(rec["psi"][-1], order, xy, L)
    assert transverse_width(prof, L) < L / 4.0  # self-policing: compact, COM meaningful
    c0 = com(rec["psi"][0], xy, order, periods=(L, L))
    c1 = com(rec["psi"][-1], xy, order, periods=(L, L))
    return min_image_delta(c1[1], c0[1], L), rec


def test_reversal_and_zero_exact_nulls():
    g, order, c3, xy = _j2_setup(L=24)
    dy0, _ = _dy(g, order, xy, c3, 24, 0.0)
    assert abs(dy0) < 1e-8  # R-symmetry theorem: exact null
    dyp, _ = _dy(g, order, xy, c3, 24, G0)
    dym, _ = _dy(g, order, xy, c3, 24, -G0)
    assert abs(dyp + dym) < 1e-6  # R*H(g)*R = H(-g): exact antisymmetry


def test_zero_k_transverse_null():
    # Zero-k null holds for FREE flight (no forces at g=0); under a
    # gradient the spreading packet may drift transversely (unconstrained).
    g, order, c3, xy = _j2_setup(L=24)
    dy, _ = _dy(g, order, xy, c3, 24, 0.0, k=(0.0, 0.0))
    assert abs(dy) < 1e-8


def test_detector_calibration_synthetic():
    two = gaussian_ring_profile(64, [16.0, 40.0], 4.0)  # separation 24 = 6*sigma0
    st = split_statistic(two, 4.0)
    assert st["fires"] and split_fires(two, 4.0)
    assert st["depth"] > 0.9 and st["separation"] == 24.0 and st["minority_weight"] > 0.4
    one = gaussian_ring_profile(64, [16.0], 4.0)
    assert not split_fires(one, 4.0)
    assert not split_fires(np.full(28, 1.0 / 28), 4.0)  # flat never fires
    assert not split_fires(gaussian_ring_profile(28, [7.0, 14.0], 4.0), 4.0)  # 7 < 3*4


def test_detector_free_flight_no_split():
    g, order, c3, xy = _j2_setup(L=24)
    _, rec = _dy(g, order, xy, c3, 24, 0.0)
    ys, prof = transverse_profile(rec["psi"][-1], order, xy, 24)
    assert len(ys) == 24 and abs(prof.sum() - 1.0) < 1e-12
    assert not split_fires(prof, 3.0)


def test_transverse_profile_and_smoothing_units():
    _, order, _, xy = _j2_setup(L=4)
    loc = np.zeros(len(order), dtype=complex)
    loc[0] = 1.0
    _, prof = transverse_profile(loc, order, xy, 4)
    assert abs(prof.sum() - 1.0) < 1e-12 and (prof == 1.0).sum() == 1
    sm = smooth_ring_profile(np.array([1.0, 0.0, 0.0, 0.0]), 1.0)
    assert abs(sm.sum() - 1.0) < 1e-12 and sm[0] == sm.max()  # peak preserved


def test_seam_weight_and_persistence_units():
    p = np.zeros(28)
    p[14] = 1.0  # launch y0 = 14 -> seam at 0/28
    assert seam_weight(p, 14.0, 28) == 0.0
    p2 = np.zeros(28)
    p2[0] = 1.0
    assert seam_weight(p2, 14.0, 28) == 1.0
    assert split_persists([True] * 10) and not split_persists([True] * 9 + [False] * 1)
    assert not split_persists([])


def test_sheet_family_port_matches_malus_algebra():
    _g, order, c3, xy = _j2_setup(L=4)
    psi0 = gaussian_packet(xy, order, (1.0, 2.0), (0.3, 0.0), 0.6, periods=(4, 4))
    fam = sheet_packet_family(psi0, order, c3)
    assert all(is_normalized_ok(fam[k]) for k in ("sym", "anti", "sheet0"))
    assert np.array_equal(fam["sym"], psi0)  # coarse packet IS the symmetric one
    s = sheet_swap_csr(order, c3).toarray()
    assert np.allclose(s @ fam["sym"], fam["sym"])  # even
    assert np.allclose(s @ fam["anti"], -fam["anti"])  # odd
    assert abs(np.vdot(fam["sym"], fam["anti"])) < 1e-12  # orthogonal sectors


def test_splitter_determinism():
    g, order, _, xy = _j2_setup()
    h1 = splitter_hamiltonian(g, order, xy, 3.0, G0, 6)
    h2 = splitter_hamiltonian(g, order, xy, 3.0, G0, 6)
    assert (h1 != h2).nnz == 0
    g24, order24, _, xy24 = _j2_setup(L=24)
    d1, _ = _dy(g24, order24, xy24, None, 24, G0)
    d2, _ = _dy(g24, order24, xy24, None, 24, G0)
    assert d1 == d2


def test_splitter_keeps_packet_compact_no_wrap():
    g, order, c3, xy = _j2_setup(L=24)
    _, rec = _dy(g, order, xy, c3, 24, G0)
    _, prof = transverse_profile(rec["psi"][-1], order, xy, 24)
    assert transverse_width(prof, 24) < 24.0 / 4.0  # campaign width-gate class
    assert seam_weight(prof, 12.0, 24) < 0.01  # campaign seam-gate class


def test_transverse_width_unit():
    p = gaussian_ring_profile(64, [32.0], 4.0)
    assert abs(transverse_width(p, 64) - 4.0) < 0.4  # recovers launch sigma


def test_sine_reduces_to_bare_and_hopping_only():
    g, order, _, xy = _j2_setup()
    h0 = splitter_hamiltonian(g, order, xy, 3.0, 0.0, 6, shape="sine").toarray()
    assert np.array_equal(h0, hamiltonian(g, order=order).toarray())  # exact
    for grad in (G0 / 8, G0 / 4, G0):
        h = splitter_hamiltonian(g, order, xy, 3.0, grad, 6, shape="sine")
        assert is_hermitian_ok(h) and is_zero_diagonal_ok(h)


def test_sine_sheet_blind_commutes_with_swap():
    g, order, c3, xy = _j2_setup(L=4)
    s = sheet_swap_csr(order, c3)
    assert commutes_ok(splitter_hamiltonian(g, order, xy, 2.0, G0 / 4, 4, shape="sine"), s)


def test_sine_bounded_no_seam_jump():
    g, order, _, xy = _j2_setup(L=8)
    hs = splitter_hamiltonian(g, order, xy, 4.0, G0, 8, shape="sine").toarray()
    hl = splitter_hamiltonian(g, order, xy, 4.0, G0, 8, shape="linear").toarray()
    dev_s = np.abs(hs[np.nonzero(hs)] + 1.0).max()
    dev_l = np.abs(hl[np.nonzero(hl)] + 1.0).max()
    assert dev_s <= G0 * 8 / (2.0 * np.pi) * (1 + 1e-9)  # smooth periodic bound
    assert dev_s < dev_l  # linear seam jump exceeds the sine bound
    assert dev_l > G0 * 3.0  # linear reaches ~L/2 at the seam


def test_sine_reversal_and_zero_exact_nulls():
    g, order, c3, xy = _j2_setup(L=24)
    dy0, _ = _dy(g, order, xy, c3, 24, 0.0, shape="sine")
    assert abs(dy0) < 1e-8  # R-theorem survives (sin is odd)
    dyp, _ = _dy(g, order, xy, c3, 24, G0 / 4, shape="sine")
    dym, _ = _dy(g, order, xy, c3, 24, -G0 / 4, shape="sine")
    assert abs(dyp + dym) < 1e-6
