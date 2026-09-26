"""BV scale-up: CSR shell graphs + Sinkhorn OR campaigns.

Spec fidelity to BU (same bridge counts, radii, p_adj), CSR-direct builder
(no NetworkX on the hot path), streaming == dense backends, and campaign
reproduction of BU bands (N=300 ~0.92, N=1020 ~0.913).
"""
import numpy as np

from bh_graph import shellscale as H


def test_spec_fidelity():
    assert abs(H.p_adj_of_shell(0, True) - 0.85) < 1e-12
    assert abs(H.p_adj_of_shell(9, True) - (0.85 + 0.015 * 9)) < 1e-12
    assert abs(H.p_adj_of_shell(5, False) - 0.85) < 1e-12
    assert abs(H.shell_pair_radius(0, 10) - 1.7222222222222223) < 1e-12
    assert abs(H.shell_pair_radius(8, 10) - 5.277777777777778) < 1e-9
    # bridge law anchored: n = 8 at per_shell = 30, r = 2 by construction
    assert H.n_bridges_for_pair(2.0, 30, 1.5) == 8
    assert H.n_bridges_for_pair(4.0, 30, 1.5) == 23  # 8 * 2^1.5
    assert H.is_valid_shell_params(12, 6, 3)
    assert not H.is_valid_shell_params(2, 6, 3)


def test_packing_spacing_pins():
    a300 = H.packing_implied_spacing(30, 1.5)
    a600 = H.packing_implied_spacing(60, 1.28)
    a1020 = H.packing_implied_spacing(102, 1.24)
    assert a300 < a600 < a1020
    assert 1.2 < a1020 < 2.0
    assert np.isnan(H.packing_implied_spacing(-5, 1.5))


def test_csr_builder_counts():
    b = H.build_shell_csr(12, 6, True, 1.5, 0)
    assert b["ok"] and b["n_nodes"] == 72
    assert (b["csr"] != b["csr"].T).nnz == 0  # symmetric
    assert list(b["shell_of"][:12]) == [0] * 12
    for s, blist in enumerate(b["bridges"]):
        r = H.shell_pair_radius(s, 6)
        assert len(blist) == H.n_bridges_for_pair(r, 12, 1.5)
    assert H.build_shell_csr(2, 6)["ok"] is False
    assert H.build_shell_csr(12, 6, beta=-1.0)["ok"] is False


def test_nx_port_valid():
    g = H.gradient_shell_graph_nx(per_shell=12, n_shells=6, gradient=True, seed=0)
    assert g.number_of_nodes() == 72
    for s in range(5):
        assert any(sorted([u[0], v[0]]) == [s, s + 1] for u, v in g.edges())


def test_streaming_matches_dense():
    b = H.build_shell_csr(12, 6, True, 1.5, 1)
    d = H.shell_kappa_profile_csr(b["csr"], b["bridges"], 6, 4, 0.05, "dense", 1)
    s = H.shell_kappa_profile_csr(b["csr"], b["bridges"], 6, 4, 0.05, "stream", 1)
    assert set(d) == set(s)
    for r in d:
        assert abs(d[r] - s[r]) < 1e-9


def test_fit_and_local_slopes():
    prof = {r: -(r ** -0.9) for r in (1.5, 2.5, 3.5, 4.5, 5.5)}
    f = H.fit_scaling_power(prof)
    assert abs(f["p"] - 0.9) < 1e-9 and f["r2"] > 0.999
    loc = H.local_slopes(prof, 3)
    assert len(loc) == 3 and all(abs(v - 0.9) < 1e-9 for v in loc.values())
    assert np.isnan(H.fit_scaling_power({1.0: -1.0})["p"])
    assert H.local_slopes(prof, 2) == {}


def test_old_vs_new_split_csr():
    old = H.campaign(12, 6, 3, False, 1.0, 0, 4, 0.05, "dense", 2, verbose=False)
    new = H.campaign(12, 6, 3, True, 1.5, 0, 4, 0.05, "dense", 2, verbose=False)
    assert 0.3 < old["mean"] < 0.9
    assert 0.7 < new["mean"] < 1.4
    assert new["mean"] - old["mean"] > 0.2


def test_csr_reproduces_bu_n300():
    r = H.campaign(30, 10, 4, True, 1.5, 0, 8, 0.02, "dense", 2, verbose=False)
    assert r["n_ok"] == 4
    assert 0.80 < r["mean"] < 1.05
    assert all(v < 0 for v in r["stacked"].values())


def test_csr_reproduces_bu_n1020():
    r = H.campaign(102, 10, 4, True, 1.24, 0, 8, 0.01, "dense", 2, verbose=False)
    assert r["n_ok"] == 4
    assert 0.85 < r["mean"] < 0.98  # BU: 0.9134
    assert r["stacked_fit"]["r2"] > 0.9


def test_bu_reference_transcription():
    f = H.fit_scaling_power(H.BU_N1020_STACKED)
    assert abs(f["p"] - 0.9105) < 0.001  # main stacked fit 0.91054
    assert abs(f["r2"] - 0.9559) < 0.002
    assert abs(H.BU_N1020_P - 0.9134) < 0.001


def test_campaign_artifact_roundtrip(tmp_path):
    r = H.campaign(12, 6, 2, True, 1.5, 0, 4, 0.05, "dense", 1, verbose=False)
    p = str(tmp_path / "mini.json")
    assert H.save_artifact(r, p) == p
    back = H.load_artifact(p)
    assert back["config"]["beta"] == 1.5 and back["n_ok"] == 2
    assert back["stacked_fit"]["p"] == r["stacked_fit"]["p"]
    assert H.load_artifact(str(tmp_path / "nope.json")) == {}
