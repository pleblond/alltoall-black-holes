"""Vacuum curvature: flatness, locality, fits, verdicts (prereg §2)."""
import numpy as np

from bh_graph import vacuum_curv as C
from bh_graph import vacuum_graphs as V


def test_i_cubic_flat_exact_backend():
    b = V.build_vacuum("cubic", 6)
    r = C.measure_kappa_sample(b, n_edges=50, seed=0)
    assert r["ok"] and r["n"] == 50 and r["n_fail"] == 0
    assert r["max_abs"] < 1e-6  # prereg bar


def test_i_bcc_fcc_flat():
    for fam, L in (("bcc", 5), ("fcc", 4)):
        b = V.build_vacuum(fam, L)
        r = C.measure_kappa_sample(b, n_edges=30, seed=0)
        assert r["ok"] and r["max_abs"] < 1e-6, fam


def test_e1_perturbation_localized_zero_beyond():
    # Structural: E1 affects r<=2 only; r>=3 is machine-zero (all families).
    for fam, L in (("cubic", 10), ("bcc", 6), ("fcc", 5)):
        b = V.build_vacuum(fam, L)
        e = V.apply_excursion(b, "E1", delta=2, seed=0)
        p = C.radial_kappa_profile(e, V.max_unwrapped_radius(b))
        assert p["ok"], fam
        for r, k in p["profile"].items():
            if r >= 3:
                assert abs(k) < 1e-9, (fam, r, k)
        assert p["profile"][1.0] < -0.1, fam  # hub bin strongly negative


def test_e2_reaches_r3_only():
    b = V.build_vacuum("cubic", 10)
    e = V.apply_excursion(b, "E2", seed=0)
    p = C.radial_kappa_profile(e, V.max_unwrapped_radius(b))
    assert p["ok"]
    assert abs(p["profile"][3.0]) > 1e-6  # E2 reaches r=3
    assert abs(p["profile"][4.0]) < 1e-9  # ... and dies at r=4


def test_form_comparison_selects_truth():
    rs = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    log_prof = {r: -(1.0 + 0.5 * np.log(r)) for r in rs}
    f = C.fit_form_comparison(log_prof)
    assert f["ok"] and f["winner"] == "log"
    assert all(v > 10.0 for v in f["dBIC"].values())
    pow_prof = {r: -(r ** -0.9) for r in rs}
    f = C.fit_form_comparison(pow_prof)
    assert f["ok"] and f["winner"] == "power"
    lin_prof = {r: -(1.0 + 0.2 * r) for r in rs}
    f = C.fit_form_comparison(lin_prof)
    assert f["ok"] and f["winner"] == "linear"


def test_form_comparison_needs_4_negative_bins():
    assert C.fit_form_comparison({1.0: -1.0, 2.0: -0.5})["ok"] is False
    assert C.fit_form_comparison({})["ok"] is False
    mixed = {1.0: -1.0, 2.0: -0.5, 3.0: 0.0, 4.0: 0.0, 5.0: 0.0}
    assert C.fit_form_comparison(mixed)["ok"] is False  # only 2 negative


def test_base_absorbed_slopes_overlap_logic():
    rs = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    # C1-consistent: same B across families (b_fam = B/ln k_vac).
    B = 0.7
    fits = {}
    for fam, k in (("cubic", 6), ("bcc", 8), ("fcc", 12)):
        prof = {r: -(2.0 + (B / np.log(k)) * np.log(r)) for r in rs}
        fits[fam] = C.fit_form_comparison(prof)
    o = C.base_absorbed_slopes(fits)
    assert o["ok"] and o["overlap"]
    assert all(abs(v["B"] - B) < 1e-9 for v in o["B"].values())
    # Anti-C1: same natural slope (base does NOT absorb) with tight masses.
    fits2 = {}
    for fam in ("cubic", "bcc", "fcc"):
        prof = {r: -(2.0 + 0.5 * np.log(r)) + 1e-6 * r for r in rs}
        fits2[fam] = C.fit_form_comparison(prof)
    o2 = C.base_absorbed_slopes(fits2)
    assert o2["ok"] and not o2["overlap"]


def test_verdicts_on_synthetics():
    assert C.test_i_verdict({6: 1e-16, 8: 1e-16})["verdict"] == "PASS"
    assert C.test_i_verdict({6: 1e-16, 8: 0.1})["verdict"] == "FAIL"
    # test_ii: log decisive in 2/3 + base overlap -> PASS tested via real
    # fit objects; here the INCONCLUSIVE and FAIL paths.
    assert C.test_ii_verdict({"cubic": {"ok": False}})["verdict"] == "INCONCLUSIVE"
    rs = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    powfits = {f: C.fit_form_comparison({r: -(r ** -0.9) for r in rs})
               for f in ("cubic", "bcc", "fcc")}
    v = C.test_ii_verdict(powfits)
    assert v["verdict"] == "FAIL" and v["reason"] == "log-not-decisive"
    # test_iii: same-protocol requirement.
    pf = {("cubic", "E1"): {"p": 0.92, "r2": 0.9},
          ("bcc", "E1"): {"p": 0.93, "r2": 0.9}}
    assert C.test_iii_verdict(pf)["verdict"] == "RECOVERED"
    pf2 = {("cubic", "E1"): {"p": 0.92, "r2": 0.9},
           ("bcc", "E2"): {"p": 0.93, "r2": 0.9}}
    assert C.test_iii_verdict(pf2)["verdict"] == "NOT-RECOVERED"  # mixed proto
    pf3 = {("cubic", "E1"): {"p": 1.5, "r2": 0.9},
           ("bcc", "E1"): {"p": 1.6, "r2": 0.9}}
    assert C.test_iii_verdict(pf3)["verdict"] == "NOT-RECOVERED"
    pf4 = {("cubic", "E1"): {"p": float("nan"), "r2": float("nan")}}
    assert C.test_iii_verdict(pf4)["verdict"] == "INCONCLUSIVE"


def test_sinkhorn_crosscheck_runs_and_bias_direction():
    # Small graph: Sinkhorn runs; bias kappa_sink <= kappa_exact holds
    # on average (documented entropic overshoot of W1).
    b = V.build_vacuum("cubic", 6)
    e = V.apply_excursion(b, "E1", delta=2, seed=0)
    pe = C.radial_kappa_profile(e, 2)
    ps = C.radial_kappa_profile_sinkhorn(e, 2, eps=0.05)
    assert pe["ok"] and ps["ok"]
    assert set(pe["profile"]) == set(ps["profile"])
    diffs = [ps["profile"][r] - pe["profile"][r] for r in pe["profile"]]
    assert float(np.mean(diffs)) < 0.05  # bias runs sink <= exact-ish
