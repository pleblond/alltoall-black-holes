"""BV: UV tortuosity-as-scattering — derivation tests, not fits.

Headline: soft Gaussian cost alpha = s_leg = ln2 gives c ~ 0.44-0.64
(target 0.456 from BU p = 0.913, geometric 1/sqrt(pi) = 0.564) with zero
tuning; hard walls overshoot or pop; mixed mode rises then disconnects at
k ~ k_crit = 4 pi r^2/sigma; OR stays negative in the UV.
"""
import numpy as np

from bh_graph import uvscatter as U
from bh_graph.horizon import PATCH_AREA


def test_patch_identities():
    assert abs(U.sigma_lat2() - PATCH_AREA / 1.56**2) < 1e-12
    assert abs(U.r_excl_lat() - 0.6022) < 1e-3
    assert abs(U.chi_of(20, 5.0, U.sigma_lat2()) - U.x_of_chi(U.chi_of(20, 5.0, U.sigma_lat2()))**2) < 1e-12
    # Rs inverts kcrit: pop radius of k legs holds exactly k legs
    sig = U.sigma_lat2()
    assert abs(U.kcrit_of(U.rs_of(40, sig), sig) - 40.0) < 1e-9
    # lattice kcrit matches the micro packing theorem in Planck units
    from bh_graph.micro import packing_kmax
    assert abs(U.kcrit_of(1.6, U.SIGMA_LP2) - 11.6) < 0.1
    assert packing_kmax(1.6) == 11


def test_tortuosity_maps():
    assert U.p_of_c(0.5) == 1.0
    assert U.gamma_of_c(0.5) == 1.0
    assert abs(U.c_of_p(0.913) - 0.4565) < 1e-12
    assert abs(U.c2_of_p(0.913) - 0.754) < 0.002
    assert abs(U.ctot_of_p(0.913) - 4.833) < 0.003  # Delta -0.037 vs GR
    assert abs(U.ctot_of_p(0.5) - 3.36) < 1e-12     # flat case dead
    assert abs(U.ctot_of_p(1.0) - 5.313) < 0.002    # pure scattering 1.8sigma
    assert abs(U.h_of_x(0.1, 0.5) - 1.1025) < 1e-12
    assert abs(U.dl_dr_of(0.1, 0.5) - 1.05) < 1e-12


def test_bridge_ladder_and_sigmas():
    lad = U.bridge_exponent_ladder()
    assert lad["point_like"] == 0.0 and lad["line_like"] == 1.0 and lad["area_like"] == 2.0
    assert lad["bu_1020"] == 1.24  # between line-like and area-like
    assert U.sigma_vs_bu(0.913) == 0.0
    assert abs(U.sigma_vs_bu(1.0) - 1.78) < 0.05
    assert abs(U.p_precision_j0737() - 0.028) < 0.003


def test_validity_no_exceptions():
    assert not U.is_valid_k(-1) and not U.is_valid_radius(0) and not U.is_valid_lattice(3)
    assert U.is_valid_k(0) and U.is_valid_lattice(5)
    assert np.isnan(U.chi_of(-1, 1.0, 1.0)) and np.isnan(U.rs_of(1, -2.0))
    assert np.isnan(U.kcrit_of(0.0, 1.0)) and np.isnan(U.p_of_c(np.inf))
    assert U.build_lattice_csr(3) is None
    assert U.measure_c(3, 5)["ok"] is False
    assert U.mc_ray_tortuosity(5, -1.0)["ok"] is False


def test_detour_identity():
    assert abs(U.C_GEOM - 1.0 / np.sqrt(np.pi)) < 1e-15
    assert abs(U.detour_fraction_of(40, 5.0) - np.sqrt(U.chi_of(40, 5.0, U.sigma_lat2()) / np.pi)) < 1e-12
    assert U.detour_fraction_of(0, 5.0) == 0.0
    assert U.spacing_of(0, 5.0) == float("inf")


def test_fibonacci_and_line_distance():
    d = U.fibonacci_directions(20)
    assert d.shape == (20, 3)
    assert np.allclose(np.linalg.norm(d, axis=1), 1.0)
    assert U.fibonacci_directions(0).shape == (0, 3)
    # single +z ray: node (0.5, 0, 3) sits 0.5 off the ray
    pos = np.array([[0.5, 0.0, 3.0], [0.0, 0.0, 0.5]])
    dist = U.min_line_distance(pos, np.array([[0.0, 0.0, 1.0]]), core_radius=1.0)
    assert abs(dist[0] - 0.5) < 1e-12
    assert dist[1] == np.inf  # core exempt
    assert np.all(U.min_line_distance(pos, np.zeros((0, 3))) == np.inf)


def test_lattice_and_soft_cost():
    csr = U.build_lattice_csr(5)
    assert csr.shape == (125, 125)
    assert (csr != csr.T).nnz == 0  # symmetric
    deg = np.asarray(csr.sum(axis=1)).ravel()
    assert deg.max() == 6  # interior nodes 6-connected
    w0 = U.node_cost_soft(np.array([0.0, 1.0, np.inf]), alpha=0.0)
    assert np.allclose(w0, 1.0)
    w = U.node_cost_soft(np.array([0.0, np.inf]))
    assert abs(w[0] - (1.0 + np.log(2.0))) < 1e-12 and w[1] == 1.0


def test_soft_lands_on_target():
    m = U.measure_c(32, 20, mode="soft")
    assert m["ok"] and m["reachable_frac"] == 1.0
    assert 0.30 < m["c_median"] < 0.65  # target 0.456, geometric 0.564
    assert 0.6 < m["p_median"] < 1.3 and 0.6 < m["gamma_median"] < 1.3
    assert U.sigma_vs_bu(m["p_median"], 2 * m["c_std"]) < 1.5


def test_alpha_scan_monotone():
    c0 = U.measure_c(12, 10, mode="soft", alpha=0.0)["c_median"]
    c1 = U.measure_c(12, 10, mode="soft", alpha=np.log(2.0))["c_median"]
    c2 = U.measure_c(12, 10, mode="soft", alpha=1.5)["c_median"]
    assert c0 == 0.0 and c1 > 0.15 and c2 > c1  # cost drives tortuosity


def test_hard_overshoots_and_pops():
    soft = U.measure_c(24, 10, mode="soft")["c_median"]
    hard = U.measure_c(24, 10, mode="hard")["c_median"]
    assert hard > soft + 0.15  # hard walls too strong
    pop = U.measure_c(16, 20, mode="hard")
    assert pop["reachable_frac"] < 0.5  # ...and brittle: pops early
    assert U.measure_c(16, 20, mode="soft")["reachable_frac"] == 1.0


def test_mixed_pop_at_kcrit():
    assert abs(U.kcrit_of(2.0, U.sigma_lat2()) - 44.1) < 0.2
    rows = U.pop_scan(24, [20, 80], mode="mixed")
    assert rows[0]["reachable_frac"] > 0.9 and rows[0]["c_median"] < 1.0
    assert rows[1]["reachable_frac"] < 0.01  # disconnected past k_crit
    assert rows[0]["chi_inner"] < 1.0 < rows[1]["chi_inner"]


def test_uv_rise_then_turnover():
    rp = U.running_profile(24, 40, mode="mixed")
    uv = U.uv_running_p(rp)
    inner = [b["p"] for b in uv if b["chi"] > 0.2]
    outer = [b["p"] for b in uv if 0.01 < b["chi"] < 0.05]
    assert np.mean(inner) > np.mean(outer) + 0.5  # UV rise emerges
    dil = U.fit_c_dilute([b for b in rp if b["chi"] < 0.05])["c_median"]
    assert 0.01 < U.turnover_chi(rp, dil) < 0.2


def test_estimators_agree():
    run = U.run_soft(16, 20)
    prof = U.tortuosity_profile(run["d_graph"], run["d_clean"], run["pos"],
                                U.rs_of(20, U.sigma_lat2()))
    s = U.fit_c_slopes(prof)
    assert s["n_shells"] >= 3
    assert abs(s["c_median"] - s["c_mean"]) < 0.1
    assert abs(s["c_median"] - s["c_regression"]) < 0.15


def test_graph_distance_agrees():
    run = U.run_soft(16, 20)
    sig = U.sigma_lat2()
    fe = U.fit_c_dilute(U.tortuosity_profile(run["d_graph"], run["d_clean"],
                                             run["pos"], U.rs_of(20, sig)))
    gd = U.graph_distance_profile(run["d_graph"], run["d_clean"], run["pos"])
    fg = U.c_with_graph_distance(gd, 20, sig, U.lattice_tort0(16))
    assert 1.1 < U.lattice_tort0(16) < 1.6
    assert abs(fe["c_median"] - fg["c_median"]) < 0.15  # no-r analysis


def test_transport_ladder():
    t = U.mc_transport_c(12, 10, temperatures=(0.5, 1.0, 2.0), n_walks=40, seed=1)
    assert t["ok"]
    cs = [row["c"] for row in t["ladder"]]
    assert all(0.05 < c < 1.5 for c in cs)  # drifted sampling ~= Dijkstra band
    d = U.measure_c(12, 10, mode="soft")["c_median"]
    assert min(cs) < 2.5 * d
    ray = U.mc_ray_tortuosity(10, 6.0)
    assert ray["ok"] and ray["c"] > max(cs)  # no-detour rays overshoot


def test_ray_monotone():
    a = U.mc_ray_tortuosity(10, 6.0, alpha=0.7)["tort_mean"]
    b = U.mc_ray_tortuosity(40, 6.0, alpha=0.7)["tort_mean"]
    c = U.mc_ray_tortuosity(10, 6.0, alpha=1.5)["tort_mean"]
    assert 1.0 < a < b and a < c


def test_or_sign_survives_uv():
    o = U.uv_or_sign()
    assert o["ok"] and o["all_negative"]  # attraction holds at chi ~ 1


def test_survey_table_smoke():
    rows = U.survey_table(16, [10, 20], modes=("soft", "mixed"), seed=0)
    assert len(rows) == 4 and all(r["ok"] for r in rows)
    assert all(r["reachable_frac"] > 0.9 for r in rows)
