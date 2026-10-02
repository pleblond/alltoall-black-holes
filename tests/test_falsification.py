"""EM-1 falsification apparatus pins (prereg support; NO campaign data).

Locks the spectral inventory, gapless classes + chiral mirror +
antisymmetric confinement, commutant census, sheet-pin anatomy, mode
count, local-phase visibility, compensation failure + winding, cone
absence, touching anisotropy, circulation helpers. Campaign numbers and
F1--F5 verdicts are FILED in docs/DEFERRED.md, not pinned here.
"""

import math

import numpy as np

from bh_graph.ballistic import (
    adjacency_csr,
    evolve_fixed,
    gaussian_packet,
    hamiltonian,
    node_order,
)
from bh_graph.continuum import bond_current_ij
from bh_graph.driven import edge_arrays, steady_predict
from bh_graph.falsification import (
    W_ABOVE,
    W_BELOW,
    antisym_pin_drive,
    bloch_eigvecs,
    bond_phase_law,
    branch_multiplicity,
    chiral_diag,
    chiral_matrix,
    commutant_table,
    commutator_norm,
    compensation_residual,
    critical_class_table,
    critical_point_table,
    cycle_winding,
    eigvec_overlap_loop,
    fit_linear_slope,
    flat_projector,
    gap_class,
    imprint_vortex,
    is_anticonfined_ok,
    is_chiral_ok,
    is_inventory_ok,
    is_local_phase_visible_ok,
    is_mirror_identity_ok,
    is_nocone_ok,
    is_sheet_conserved_ok,
    is_sheetpin_mirror_ok,
    is_single_mode_ok,
    is_winding_integer_ok,
    is_winding_invariant_ok,
    local_phase_apply,
    local_phase_dev,
    max_density,
    mode_count_scan,
    nodal_sample,
    operator_range,
    participation_ratio,
    plaquette_circulation,
    propagating_mode_count,
    ray_fit,
    sheet_imbalance,
    sheet_pin_mirror_dev,
    solve_norm,
    static_gap_gamma,
    touching_rose,
    translation_matrix,
    twist_response,
)
from bh_graph.formation import j2_torus_coords, j2_torus_graph
from bh_graph.malus import sheet_packet_family, sheet_swap_matrix


def _j2_h(L=4):
    g = j2_torus_graph(L)
    order = node_order(g)
    c3 = j2_torus_coords(L)
    return g, order, c3, hamiltonian(g, order=order), adjacency_csr(g, order)


def test_inventory_critical_points():
    assert is_inventory_ok()
    t = critical_point_table()
    assert t["Gamma"]["kind"] == "minimum-definite-quadratic"
    assert t["M"]["kind"] == "maximum-definite-quadratic"
    assert t["X1"]["flat_gap"] < 1e-12  # saddles sit at flat-band energy
    b = branch_multiplicity(math.pi / 2.0, math.pi / 2.0)
    assert b["degenerate"] and abs(b["E_disp"]) < 1e-12
    assert abs(np.linalg.norm(b["v_disp"]) - 4.0 * math.sqrt(2.0)) < 1e-9
    assert np.linalg.norm(b["v_flat"]) == 0.0
    # Nodal samples all touch at E = 0 with generically nonzero drift.
    node = nodal_sample(32)
    assert len(node) > 40
    assert all(abs(s["E"]) < 1e-9 for s in node)
    assert sum(s["vmag"] > 1.0 for s in node) > len(node) // 2


def test_gap_classes_frozen():
    assert abs(static_gap_gamma(W_BELOW) - 0.5) < 1e-12
    assert gap_class(W_BELOW) == "gapped-below"
    assert gap_class(W_ABOVE) == "gapped-above-mirror"
    assert gap_class(-8.0) == "edge-tuned-EXCLUDED"
    assert gap_class(8.0) == "edge-tuned-EXCLUDED"
    assert gap_class(0.0) == "in-band-resonant"
    assert gap_class(-4.0) == "in-band-resonant"


def test_chiral_algebra_and_mirror():
    g, order, c3, h, _ = _j2_h(4)
    gam = chiral_matrix(order, c3)
    assert is_chiral_ok(h, gam)
    assert np.array_equal(chiral_diag(order, c3) ** 2, np.ones(len(order)))
    idx = {v: i for i, v in enumerate(order)}
    pins = [idx[0]]
    assert is_mirror_identity_ok(h, pins, [1.0], chiral_diag(order, c3))
    # Mirror preserves range: norms identical (Gamma is unitary diagonal).
    nlo = solve_norm(h, pins, [1.0], W_BELOW)
    nhi = solve_norm(h, pins, [1.0], W_ABOVE)
    assert abs(nlo - nhi) / nlo < 1e-9


def test_antisym_drive_confined():
    g, order, c3, h, _ = _j2_h(4)
    idx = {v: i for i, v in enumerate(order)}
    d = antisym_pin_drive(4, 1, 2)
    pins = [idx[v] for v in d["nodes"]]
    assert is_anticonfined_ok(h, pins, d["s"], W_BELOW)
    assert is_anticonfined_ok(h, pins, d["s"], W_ABOVE)
    # Symmetric drive on the same pins is NOT confined (contrast leg).
    phi = steady_predict(h, pins, np.array([1.0, 1.0]), W_BELOW)
    mask = np.ones(len(order), dtype=bool)
    mask[pins] = False
    assert np.abs(phi[mask]).max() > 1e-3


def test_linear_slope_helper():
    ts = np.linspace(0.0, 5.0, 51)
    r = fit_linear_slope(ts, 2.0 * ts + 1.0)
    assert abs(r["slope"] - 2.0) < 1e-12 and r["r2"] > 1 - 1e-12
    tp = np.linspace(0.0, 4.0 * math.pi, 101)
    r = fit_linear_slope(tp, np.sin(tp))
    # Bounded oscillation shows only finite-window slope (< 0.1), >20x
    # below a genuine secular slope: the helper distinguishes them.
    assert abs(r["slope"]) < 0.1


def test_commutant_census_L4():
    t = commutant_table(4)
    # Exact commutation: I, S, Tx, Ty, H commute; Gamma anticommutes.
    for name in ("I", "S", "Tx", "Ty", "H", "P_flat"):
        assert t[name]["comm"] < 1e-9, name
    assert t["Gamma"]["comm"] > 1.0  # does NOT commute ...
    assert t["Gamma"]["anticomm"] < 1e-9  # ... it anticommutes
    # Locality filing: Gamma on-site, H/T range 1, S cell-local (range 2:
    # sheet partners share neighbours but no direct edge), P_flat global.
    assert t["Gamma"]["oprange"] == 0
    assert t["H"]["oprange"] == 1
    assert t["Tx"]["oprange"] == 1 and t["Ty"]["oprange"] == 1
    assert t["S"]["oprange"] == 2
    assert t["P_flat"]["oprange"] > 2
    # Signed-quantity filing: only S/T/H/Gamma signed; none intrinsic-conj.
    assert t["S"]["signedQ"] and not t["I"]["signedQ"]
    assert not t["P_flat"]["signedQ"]
    assert all(not t[n]["intrinsic_conj"] for n in t)


def test_translation_unitarity():
    _, order, c3, _, _ = _j2_h(4)
    for ax in (0, 1):
        m = translation_matrix(order, c3, 4, ax).toarray()
        assert np.allclose(m @ m.T, np.eye(len(order)))
    # Tx^L = I on the torus.
    m = translation_matrix(order, c3, 4, 0).toarray()
    assert np.allclose(np.linalg.matrix_power(m, 4), np.eye(len(order)))


def test_flat_projector_algebra():
    _, _, _, h, _ = _j2_h(4)
    p = flat_projector(h)
    assert np.allclose(p @ p, p, atol=1e-9)
    assert abs(np.trace(p) - 22.0) < 1e-6  # 16 flat + 6 touching at L4
    assert commutator_norm(h, p) < 1e-9


def test_sheet_imbalance_signed_conserved():
    g, order, c3, h, _ = _j2_h(6)
    s = sheet_swap_matrix(order, c3)
    coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    base = gaussian_packet(coords, order, (1.5, 3.0), (0.3, 0.0), 1.5,
                           periods=(6, 6))
    fam = sheet_packet_family(base, order, c3)
    assert abs(sheet_imbalance(fam["sym"], s) - 1.0) < 1e-9
    assert abs(sheet_imbalance(fam["anti"], s) + 1.0) < 1e-9
    assert abs(sheet_imbalance(fam["sheet0"], s)) < 1e-9
    # Conserved under free evolution (sym sector packet).
    rec = evolve_fixed(fam["sym"], h, 0.1, 20)["psi"]
    assert is_sheet_conserved_ok(rec, s)
    rec = evolve_fixed(fam["sheet0"], h, 0.1, 20)["psi"]
    assert is_sheet_conserved_ok(rec, s)


def test_participation_and_peak():
    psi = np.zeros(16, dtype=complex)
    psi[0] = 1.0
    assert abs(participation_ratio(psi) - 1.0) < 1e-12
    assert abs(max_density(psi) - 1.0) < 1e-12
    psi = np.ones(16, dtype=complex) / 4.0
    assert abs(participation_ratio(psi) - 16.0) < 1e-9


def test_sheetpin_mirror_not_negation():
    g, order, c3, h, _ = _j2_h(6)
    s = sheet_swap_matrix(order, c3)
    idx = {v: i for i, v in enumerate(order)}
    p0 = steady_predict(h, [idx[0]], np.array([1.0]), W_BELOW)
    p1 = steady_predict(h, [idx[1]], np.array([1.0]), W_BELOW)
    assert is_sheetpin_mirror_ok(p0, p1, s)
    d = sheet_pin_mirror_dev(p0, p1, s)
    assert d["mirror"] < 1e-9 and d["negation"] > 0.5


def test_mode_count_single_everywhere():
    assert is_single_mode_ok(24)
    r = mode_count_scan(24)
    assert r["max_count"] == 1 and r["n_two"] == 0
    # Band edges carry drift 0 (filed: stationary, not propagating).
    assert propagating_mode_count(0.0, 0.0) == 0
    # Generic + nodal points carry exactly one.
    assert propagating_mode_count(0.3, 0.1) == 1
    assert propagating_mode_count(math.pi / 2.0, math.pi / 2.0) == 1


def test_local_phase_visibility():
    g, order, _, h, _ = _j2_h(4)
    eu, ev = edge_arrays(g, order)
    rng = np.random.default_rng(0)
    psi = rng.normal(size=len(order)) + 1.0j * rng.normal(size=len(order))
    # Unnormalized (entries O(1)): B/J/E shifts read at O(1), not 1/N.
    alphas = rng.normal(size=len(order))
    assert is_local_phase_visible_ok(psi, alphas, g, order, eu, ev)
    d = local_phase_dev(psi, alphas, g, order, eu, ev)
    assert d["dB_loc"] > 0.05 and d["dJ_loc"] > 0.05 and d["dE_loc"] > 0.05
    assert d["dB_glo"] < 1e-9 and d["dJ_glo"] < 1e-9 and d["dE_glo"] < 1e-9
    # Bond rotation law spot: delta = pi/2 swaps B -> -Jq.
    bp, jp = bond_phase_law(0.5, 0.2, math.pi / 2.0)
    assert abs(bp + 0.2) < 1e-12 and abs(jp - 0.5) < 1e-12


def test_compensation_T1T2T3_fail():
    g, order, c3, h, _ = _j2_h(4)
    eu, ev = edge_arrays(g, order)
    rng = np.random.default_rng(1)
    psi = rng.normal(size=len(order)) + 1.0j * rng.normal(size=len(order))
    # Unnormalized (entries O(1)): residuals read at O(1), not 1/N.
    alphas = rng.normal(size=len(order))
    s = sheet_swap_matrix(order, c3)
    t = translation_matrix(order, c3, 4, 0)
    for kind, kw in (("translate", {"t_mat": t}),
                     ("sheet", {"s_mat": s}),
                     ("conjugate", {})):
        r = compensation_residual(psi, alphas, kind, g, order, eu, ev, **kw)
        assert r["dB"] > 0.05, kind  # O(1) residual: no redundancy


def test_winding_integer_invariant():
    _, order, c3, _, _ = _j2_h(8)
    psi = imprint_vortex(order, c3, (4.0, 4.0), 1, 2.0, 8)
    ring = [i for i, v in enumerate(order) if c3[v][2] == 0
            and abs(c3[v][0] - 4) + abs(c3[v][1] - 4) == 3]
    # Order the diamond ring by polar angle for a proper cycle.
    xs = np.array([c3[order[i]][0] for i in ring], dtype=float)
    ys = np.array([c3[order[i]][1] for i in ring], dtype=float)
    ang = np.arctan2(ys - 4.0, xs - 4.0)
    cyc = [ring[i] for i in np.argsort(ang)]
    assert abs(cycle_winding(psi, cyc) - 1.0) < 1e-9  # imprint m = 1
    assert is_winding_integer_ok(psi, cyc)
    rng = np.random.default_rng(2)
    small = 0.1 * rng.normal(size=len(order))  # no branch-cut crossing
    assert is_winding_invariant_ok(psi, small, cyc)
    # Large phases keep integrality but may re-wrap the value (filed).
    big = local_phase_apply(psi, rng.normal(size=len(order)))
    assert is_winding_integer_ok(big, cyc)


def test_ray_fits_and_classes():
    assert is_nocone_ok()
    t = critical_class_table()
    assert t["Gamma"]["kind"] == "minimum-definite-quadratic"
    assert t["nodal"]["kind"] == "touching-drift-linear"
    assert t["conical_candidates"] == []
    # Gamma ray is quadratic; nodal ray is drift-linear.
    rq = ray_fit((0.0, 0.0), (1.0, 0.0))
    assert rq["kind"] == "quadratic"
    # Joint-fit c1 absorbs O(rmax^3) quartic contamination (~0.005 at
    # rmax=0.3); the Taylor-linear coefficient itself is v.qhat = 0.
    assert abs(rq["a1"]) < 0.05 and abs(rq["a2"] - 2.0) < 0.1
    rd = ray_fit((math.pi / 2.0, math.pi / 2.0), (1.0, 1.0))
    assert rd["kind"] == "drift-linear" and abs(rd["a1"]) > 1.0
    # Bloch eigenvectors k-independent: loop overlap exactly 1.
    assert abs(eigvec_overlap_loop() - 1.0) < 1e-12
    u = bloch_eigvecs(0.3, -0.2)
    assert abs(np.vdot(u["u_disp"], u["u_flat"])) < 1e-12


def test_touching_rose_anisotropic():
    rose = touching_rose()
    assert rose["min"] < 0.6  # tangent direction: near-zero drift
    assert rose["max"] > 5.0  # normal direction: full drift
    assert rose["rel_spread"] > 1.0  # leading-order anisotropy (fails IR)


def test_vortex_and_circulation():
    _, order, c3, _, _ = _j2_h(8)
    psi = imprint_vortex(order, c3, (4.0, 4.0), 1, 2.0, 8)
    assert abs(float(np.linalg.norm(psi)) - 1.0) < 1e-12
    idx = {v: i for i, v in enumerate(order)}
    by_cell = {(x, y, b): v for v, (x, y, b) in c3.items()}
    # Intrinsic 4-cycle around cell (4,4), sheet 0 (J2 edges are axial).
    cyc = [by_cell[(4, 4, 0)], by_cell[(5, 4, 0)],
           by_cell[(5, 5, 0)], by_cell[(4, 5, 0)]]
    gam = plaquette_circulation(psi, idx, cyc)
    assert abs(gam) > 1e-6  # imprinted vortex carries circulation
    # Twist law spot: J = 2 rho^2 sin g, continuous in g.
    assert abs(twist_response(0.0) - 0.0) < 1e-12
    assert abs(twist_response(math.pi / 2.0) - 2.0) < 1e-12
    assert abs(twist_response(0.1) - 2.0 * math.sin(0.1)) < 1e-12
    # Bond-current antisymmetry underlies circulation accounting.
    a, b = 0.3 + 0.1j, 0.2 - 0.4j
    assert abs(bond_current_ij(a, b) + bond_current_ij(b, a)) < 1e-12
