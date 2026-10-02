"""BG-RESP-0 pins: susceptibility apparatus + exact identities (frozen pre-data).

All pins run on L=4 (N=32) except where noted; headline L=28 runs live in
the beast campaign (scripts/bgresp_campaign.py). No geometry is evolved.
"""

import math

import numpy as np
import pytest

from bh_graph import bgresp as bg
from bh_graph import vacfield as vf
from bh_graph import vacexc as vx


def _sub4():
    return bg.j2_substrate(4)


def _vacs4():
    sub = _sub4()
    eu, ev = bg.edge_arrays_of(sub)
    return sub, eu, ev, {n: bg.vacuum_shape(n, sub) for n in bg.VACUUMS}


# 0A: exact response decomposition.
def test_decomp_identity_all_vacua():
    sub, eu, ev, vacs = _vacs4()
    rng = np.random.default_rng(0)
    for name in bg.VACUUMS:
        d = rng.standard_normal(32) + 1j * rng.standard_normal(32)
        d = d / np.linalg.norm(d) * 0.01
        assert bg.is_decomp_ok(vacs[name], d, eu, ev)


def test_decomp_matches_vacexc():
    sub, eu, ev, vacs = _vacs4()
    rng = np.random.default_rng(1)
    d = rng.standard_normal(32) + 1j * rng.standard_normal(32)
    d = d / np.linalg.norm(d) * 0.01
    for name in bg.NONZERO_VACUUMS:
        a = bg.decomp_anatomy(vacs[name], d, eu, ev)
        b = vx.decomp_anatomy(vacs[name], d, eu, ev)
        for k in ("cross_rho", "dd_rho", "cross_B", "dd_B", "cross_J", "dd_J"):
            assert float(np.abs(a[k] - b[k]).max()) == 0.0


def test_second_order_bg_independent():
    sub, eu, ev, vacs = _vacs4()
    rng = np.random.default_rng(2)
    d = rng.standard_normal(32) + 1j * rng.standard_normal(32)
    d = d / np.linalg.norm(d) * 0.01
    refs = {n: bg.second_order_vector(vacs[n], d, eu, ev) for n in bg.VACUUMS}
    for n in bg.VACUUMS:
        assert float(np.abs(refs[n] - refs["VPLUS"]).max()) == 0.0


# 0B/0Z: ZERO theorem.
def test_chi_zero_exact():
    sub, eu, ev, vacs = _vacs4()
    chi = bg.chi_dense(vacs["ZERO"], eu, ev)
    assert bg.is_chi_zero_ok(chi)
    assert float(np.abs(chi).max()) == 0.0


def test_chi_nonzero():
    sub, eu, ev, vacs = _vacs4()
    for name in bg.NONZERO_VACUUMS:
        assert bg.is_chi_nonzero_ok(bg.chi_dense(vacs[name], eu, ev))


# 0C/0D: chi construction + spectra.
def test_chi_apply_matches_formula():
    sub, eu, ev, vacs = _vacs4()
    rng = np.random.default_rng(3)
    for name in bg.VACUUMS:
        d = rng.standard_normal(32) + 1j * rng.standard_normal(32)
        d = d / np.linalg.norm(d) * 0.01
        y = bg.chi_apply(bg.chi_dense(vacs[name], eu, ev), bg.complex_to_real_vector(d))
        f = bg.first_order_vector(vacs[name], d, eu, ev)
        assert float(np.abs(y - f).max()) < 1e-12


def test_chi_sparse_matches_dense():
    sub, eu, ev, vacs = _vacs4()
    rng = np.random.default_rng(4)
    v = rng.standard_normal(64)
    for name in bg.VACUUMS:
        yd = bg.chi_apply(bg.chi_dense(vacs[name], eu, ev), v)
        ys = bg.chi_apply(bg.chi_sparse(vacs[name], eu, ev), v)
        assert float(np.abs(yd - ys).max()) < 1e-12


def test_chi_fro_sqrt44():
    sub, eu, ev, vacs = _vacs4()
    for name in bg.NONZERO_VACUUMS:
        spec = bg.chi_spectrum_dense(bg.chi_dense(vacs[name], eu, ev))
        assert abs(spec["fro"] - math.sqrt(44.0)) < 1e-9


def test_chi_rank_nullity():
    sub, eu, ev, vacs = _vacs4()
    for name in bg.NONZERO_VACUUMS:
        spec = bg.chi_spectrum_dense(bg.chi_dense(vacs[name], eu, ev))
        assert spec["rank"] == 63
        assert spec["nullity"] == 1


def test_chi_matches_response_static():
    # bgresp chi columns match response.chi_rho/chi_bond at K = I (t = 0).
    from bh_graph import response as rp

    sub, eu, ev, vacs = _vacs4()
    eu_a, ev_a = np.asarray(eu), np.asarray(ev)
    vac = vacs["VPLUS"]
    chi = bg.chi_dense(vac, eu_a, ev_a)
    n = len(sub["order"])
    ne = len(eu_a)
    # rho row for node 5, sourced at node 5: chi_rho(vac_v, k=1).
    row = rp.chi_rho(complex(vac[5]), 1.0 + 0.0j)
    assert abs(float(row[0]) - chi[5, 5]) < 1e-12
    assert abs(float(row[1]) - chi[5, n + 5]) < 1e-12
    # B/J rows for edge 0, sourced at its first endpoint.
    k, a, b = 0, int(eu_a[0]), int(ev_a[0])
    cb = rp.chi_bond(complex(vac[a]), complex(vac[b]), 1.0 + 0.0j, 0.0j)
    assert abs(float(cb["chi_B"][0]) - chi[n + k, a]) < 1e-12
    assert abs(float(cb["chi_B"][1]) - chi[n + k, n + a]) < 1e-12
    assert abs(float(cb["chi_J"][0]) - chi[n + ne + k, a]) < 1e-12
    assert abs(float(cb["chi_J"][1]) - chi[n + ne + k, n + a]) < 1e-12


# 0E: vacuum comparison.
def test_chi_pairwise_diffs_equal_sqrt88():
    sub, eu, ev, vacs = _vacs4()
    chis = {n: bg.chi_dense(vacs[n], eu, ev) for n in bg.NONZERO_VACUUMS}
    for a, b in (("VPLUS", "VPI"), ("VPLUS", "VMINUS"), ("VPI", "VMINUS")):
        nn = bg.chi_difference_norms(chis[a], chis[b])
        assert abs(nn["fro"] - math.sqrt(88.0)) < 1e-9
        assert nn["op"] > 0.0


# 0F/0G/0H: null spaces, phase null, amplitude.
def test_global_phase_null():
    sub, eu, ev, vacs = _vacs4()
    for name in bg.NONZERO_VACUUMS:
        assert bg.is_global_phase_null_ok(bg.chi_dense(vacs[name], eu, ev), vacs[name])


def test_null_is_phase():
    sub, eu, ev, vacs = _vacs4()
    for name in bg.NONZERO_VACUUMS:
        nb = bg.chi_null_basis_dense(bg.chi_dense(vacs[name], eu, ev))
        assert nb.shape == (64, 1)
        assert bg.null_overlap_with(bg.global_phase_vector(vacs[name]), nb) > 1.0 - 1e-9


def test_amplitude_visible():
    sub, eu, ev, vacs = _vacs4()
    n = len(sub["order"])
    for name in bg.NONZERO_VACUUMS:
        assert bg.is_amplitude_visible_ok(bg.chi_dense(vacs[name], eu, ev), vacs[name], n)


def test_amplitude_j_vanishes_real_bg():
    # Real backgrounds + real amplitude kick -> dJ1 = 0 exactly.
    sub, eu, ev, vacs = _vacs4()
    n = len(sub["order"])
    for name in bg.NONZERO_VACUUMS:
        rep = bg.amplitude_response(bg.chi_dense(vacs[name], eu, ev), vacs[name], 0, n)
        assert rep["J_norm"] == 0.0
        assert rep["rho_norm"] > 0.0 and rep["B_norm"] > 0.0


# 0I/0J: bases.
def test_primitive_basis_columns():
    sub, eu, ev, vacs = _vacs4()
    n = len(sub["order"])
    chi = bg.chi_dense(vacs["VPLUS"], eu, ev)
    vr = bg.primitive_basis_vector(n, 3, imag=False)
    vi = bg.primitive_basis_vector(n, 3, imag=True)
    assert vr[3] == 1.0 and vi[n + 3] == 1.0
    assert bg.response_column(chi, vr, n)["norm"] > 0.0
    assert bg.response_column(chi, vi, n)["norm"] > 0.0


def test_local_kick_phase_rho_b_vanish_real_bg():
    # Real backgrounds: local phase kick -> drho1 = dB1 = 0, dJ1 != 0.
    sub, eu, ev, vacs = _vacs4()
    n = len(sub["order"])
    order = sub["order"]
    pos = {v: i for i, v in enumerate(order)}
    i0 = pos[bg.u0_node(sub)]
    for name in bg.NONZERO_VACUUMS:
        chi = bg.chi_dense(vacs[name], eu, ev)
        kv = bg.local_kick_vectors(vacs[name], i0)
        rp = bg.response_column(chi, kv["phase"], n)
        assert float(np.abs(rp["rho"]).max()) == 0.0
        assert float(np.abs(rp["B"]).max()) == 0.0
        assert float(np.abs(rp["J"]).max()) > 0.0


# 0K: bipartite B-null.
def test_bipartite_bnull():
    sub = _sub4()
    eu, ev = bg.edge_arrays_of(sub)
    h = bg.hamiltonian_of(sub)
    rep = bg.bipartite_bnull_report(sub, h, eu, ev, t_end=8.0)
    assert bg.is_bipartite_bnull_ok(rep)


# 0L/0M: scalings.
def test_amplitude_scaling():
    sub, eu, ev, vacs = _vacs4()
    for name in bg.NONZERO_VACUUMS:
        chi1 = bg.chi_dense(vacs[name], eu, ev)
        for a in (0.1, 1.0, 10.0):
            assert bg.is_amplitude_scaling_ok(bg.chi_dense(a * vacs[name], eu, ev), chi1, a)


def test_frac_collapse():
    sub, eu, ev, vacs = _vacs4()
    eta = vx.excitation_seed("packet", sub)
    rep = bg.fractional_scaling_report(vacs["VPLUS"], eta, eu, ev)
    assert bg.is_frac_collapse_ok(rep)


# 0N: sector-resolved.
def test_sector_projectors():
    sub = _sub4()
    pr = bg.sheet_projectors_real(sub["order"], sub["c3"])
    n = len(sub["order"])
    assert pr["P_plus"].shape == (2 * n, 2 * n)
    assert float(np.abs(pr["P_plus"] @ pr["P_plus"] - pr["P_plus"]).max()) < 1e-12
    assert float(np.abs(pr["P_minus"] @ pr["P_minus"] - pr["P_minus"]).max()) < 1e-12
    assert float(np.abs(pr["P_plus"] + pr["P_minus"] - np.eye(2 * n)).max()) < 1e-12


def test_sector_norms_vminus_swapped():
    sub, eu, ev, vacs = _vacs4()
    pr = bg.sheet_projectors_real(sub["order"], sub["c3"])
    nrm = {name: bg.sector_restricted_norms(bg.chi_dense(vacs[name], eu, ev), pr)
           for name in bg.NONZERO_VACUUMS}
    # VPLUS/VPI: op(P_+) > op(P_-); VMINUS: swapped.
    assert nrm["VPLUS"]["P_plus"]["op"] > nrm["VPLUS"]["P_minus"]["op"]
    assert nrm["VPI"]["P_plus"]["op"] > nrm["VPI"]["P_minus"]["op"]
    assert nrm["VMINUS"]["P_minus"]["op"] > nrm["VMINUS"]["P_plus"]["op"]


# 0O/0P/0Q: anatomy.
def test_covariance_translations():
    sub, eu, ev, vacs = _vacs4()
    for name in bg.NONZERO_VACUUMS:
        perm = bg.translation_perm_j2(sub["order"], sub["c3"], 4, 1, 2)
        dev = bg.covariance_dev_chi(bg.chi_dense(vacs[name], eu, ev), vacs[name],
                                    eu, ev, sub["order"], perm)
        assert dev < 1e-9


def test_per_class_uniformity():
    sub, eu, ev, vacs = _vacs4()
    for name in bg.NONZERO_VACUUMS:
        stats = bg.per_class_chi_stats(bg.chi_dense(vacs[name], eu, ev), sub, eu, ev)
        for cls in ("SX", "SY", "F1", "F2"):
            assert stats[cls]["B_std"] == 0.0
            assert stats[cls]["J_std"] == 0.0


# 0R: same carrier.
def test_same_carrier_exact():
    sub, eu, ev, vacs = _vacs4()
    chis = {n: bg.chi_dense(vacs[n], eu, ev) for n in bg.NONZERO_VACUUMS}
    rng = np.random.default_rng(5)
    d = rng.standard_normal(32) + 1j * rng.standard_normal(32)
    d = d / np.linalg.norm(d) * 0.01
    for a, b in (("VPLUS", "VPI"), ("VPLUS", "VMINUS"), ("VPI", "VMINUS")):
        rep = bg.same_carrier_residual(chis[a], chis[b], vacs[a], vacs[b], d, eu, ev)
        assert bg.is_same_carrier_ok(rep)


# 0S: time-domain kernel.
def test_kernel_crosscheck():
    sub = _sub4()
    eu, ev = bg.edge_arrays_of(sub)
    h = bg.hamiltonian_of(sub)
    for name in bg.NONZERO_VACUUMS:
        vac = bg.vacuum_shape(name, sub)
        rep = bg.response_kernel_crosscheck(bg.chi_dense(vac, eu, ev), vac, h,
                                            eu, ev, 1.0, bg.vacuum_energy(name))
        assert rep["max_dev"] < 1e-9


def test_kernel_action_matches_dense():
    sub = _sub4()
    eu, ev = bg.edge_arrays_of(sub)
    h = bg.hamiltonian_of(sub)
    rng = np.random.default_rng(6)
    d0 = rng.standard_normal(32) + 1j * rng.standard_normal(32)
    d0 = d0 / np.linalg.norm(d0) * 0.01
    for name in bg.NONZERO_VACUUMS:
        vac = bg.vacuum_shape(name, sub)
        chi0 = bg.chi_dense(vac, eu, ev)
        k = bg.kernel_matrix_dense(chi0, h, 2.0, bg.vacuum_energy(name))
        y_dense = k @ bg.complex_to_real_vector(d0)
        y_kry = bg.kernel_action_with_edges(vac, d0, h, eu, ev, 2.0,
                                            bg.vacuum_energy(name))
        assert float(np.abs(y_dense - y_kry).max()) < 1e-8


# 0V: sign census.
def test_sign_census_battery():
    sub = _sub4()
    for kind in bg.CENSUS_KINDS:
        d = bg.census_delta(kind, bg.vacuum_shape("VPLUS", sub), sub)
        assert abs(float(np.linalg.norm(d)) - 0.01) < 1e-12


def test_sign_reversal_present():
    sub, eu, ev, vacs = _vacs4()
    census = bg.sign_reversal_census({k: vacs[k] for k in bg.NONZERO_VACUUMS}, eu, ev, sub)
    assert census["point_real"]["pairs"]["VPLUS-VPI"]["n_opp"] > 0


# 0X/0Y: energy.
def test_energy_anatomy():
    sub = _sub4()
    eu, ev = bg.edge_arrays_of(sub)
    h = bg.hamiltonian_of(sub)
    for name in bg.NONZERO_VACUUMS:
        vac = bg.vacuum_shape(name, sub)
        d = vx.excitation_delta("packet", vac, sub, eps=0.01, a=1.0, mode="abs")
        assert bg.is_energy_anatomy_ok(bg.energy_anatomy(vac, d, h))


def test_hidden_energy_null():
    sub = _sub4()
    eu, ev = bg.edge_arrays_of(sub)
    h = bg.hamiltonian_of(sub)
    rep = bg.hidden_energy_null_report(sub, h, eu, ev)
    assert rep["dE_total"] == 0.0
    assert rep["dB_max"] > 0.0


# 0AC/0AD: fingerprint.
def test_fingerprint_separates():
    sub = _sub4()
    eu, ev = bg.edge_arrays_of(sub)
    h = bg.hamiltonian_of(sub)
    fps = {n: bg.fingerprint_vector(bg.vacuum_shape(n, sub), sub, h, eu, ev)
           for n in bg.NONZERO_VACUUMS}
    assert bg.is_fingerprint_ok(bg.fingerprint_distances(fps))


def test_minimal_fingerprint_size1():
    sub = _sub4()
    eu, ev = bg.edge_arrays_of(sub)
    h = bg.hamiltonian_of(sub)
    fps = {n: bg.fingerprint_vector(bg.vacuum_shape(n, sub), sub, h, eu, ev)
           for n in bg.NONZERO_VACUUMS}
    rep = bg.minimal_fingerprint_search(fps)
    assert rep["size"] == 1


# Verdict ladder.
def test_verdict_ladder():
    full = {k: True for k in bg.CHECKS}
    assert bg.campaign_verdict(full)["headline"] == "BGRESP0-COMPLETE"
    part = dict(full)
    part["witness"] = False
    assert bg.campaign_verdict(part)["headline"] == "BGRESP0-PARTIAL"
