"""Vacuum spectra/selectivity/regularity: audit math (deterministic)."""
import numpy as np

from bh_graph.vacuum_graphs import build_a15_dual, build_cubic
from bh_graph.vacuum_spectra import (
    BU_BAND,
    CLAIMED_C2,
    candidate_gamma_maps,
    degree_stats,
    hits_claimed,
    normalized_laplacian_spectrum,
    p_hat_of_k,
    repo_c2_at_bu_p,
    selectivity_audit,
    spectral_gap_info,
    stationary_tv_from_uniform,
)


def test_frozen_numbers():
    assert CLAIMED_C2 == 1.21
    assert abs(BU_BAND[0] - 0.864) < 1e-12 and abs(BU_BAND[1] - 0.962) < 1e-12


def test_p_hat_formula():
    assert abs(p_hat_of_k(13.5) - (1 / 1.21) * (1 + 1 / 13.5)) < 1e-12
    assert abs(p_hat_of_k(13.5) - 0.888) < 0.002
    assert np.isnan(p_hat_of_k(0))
    assert np.isnan(p_hat_of_k(6, c2=0.0))


def test_selectivity_audit_deterministic():
    out = selectivity_audit()
    assert out["ok"] and out["n_total"] == 17
    assert 0.0 <= out["hit_fraction"] <= 1.0
    # spot: k=6 -> (1/1.21)(7/6) = 0.9642 (just above band), k=22 -> 0.8640 (edge)
    assert abs(out["table"][6] - 0.9642) < 1e-3
    assert abs(out["table"][22] - 0.8640) < 1e-3


def test_candidate_maps_and_hits():
    maps = candidate_gamma_maps(0.5, 12.0)
    assert set(maps) == {"M1_inv_gap", "M2_gap", "M3_inv_sqrt_gap",
                         "M4_neg_log_gap", "M5_two_over_gap", "M6_k_gap_over_2"}
    assert abs(maps["M1_inv_gap"] - 2.0) < 1e-12
    assert hits_claimed(1.21) and hits_claimed(1.15) and hits_claimed(1.27)
    assert not hits_claimed(1.14) and not hits_claimed(2.0)
    assert candidate_gamma_maps(0.0, 12.0) == {}


def test_repo_c2_collision_quant():
    assert abs(repo_c2_at_bu_p() - 0.7541) < 1e-3
    assert abs(repo_c2_at_bu_p() - CLAIMED_C2) > 0.4  # 60% off


def test_spectrum_cubic():
    g, _ = build_cubic(3)
    spec = normalized_laplacian_spectrum(g)
    assert len(spec) == 27
    assert abs(spec[0]) < 1e-9 and spec[-1] <= 2.0 + 1e-9
    info = spectral_gap_info(g)
    assert info["ok"] and info["n_zeros"] == 1 and info["lambda1"] > 0


def test_regularity_metrics():
    g, _ = build_cubic(3)
    st = degree_stats(g)
    assert st["ok"] and st["var"] == 0.0 and st["min"] == st["max"] == 6
    assert stationary_tv_from_uniform(g) == 0.0
    a, _ = build_a15_dual(2)
    sa = degree_stats(a)
    assert sa["ok"] and sa["N"] == 64
    assert stationary_tv_from_uniform(a) >= 0.0
