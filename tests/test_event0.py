"""EVENT-0 unit pins (FROZEN pre-data; instrument validation only).

Tiny states (triangle/handbuilt/ring-8 samples); no campaign data is
produced here. Campaign runs on beast via scripts/event0_campaign.py.
"""

import hashlib
import os

import numpy as np

from bh_graph import event0 as e0
from bh_graph import merge0 as m0


def _tri():
    return m0.build_substrate("triangle")


# ---------------------------------------------------------------------------
# Battery / task inventory
# ---------------------------------------------------------------------------

def test_task_counts_frozen():
    assert len(e0.all_tasks()) == 463
    assert len(e0.traj_specs()) == 71
    assert len(e0.REG_MERGE_CELLS) == 12
    assert len(e0.REG_SPLIT_CELLS) == 10
    assert len(e0.REG_REWIRE_CELLS) == 6
    assert len(e0.LOC_SPECS) == 8
    assert len(e0.CYC_SPECS) == 6
    assert len(e0.ATRIGGER_SAMPLE) == 12
    assert len(e0.TRAJ_L4_TAGS) == 31
    assert len(e0.TRAJ_STORED_SPECS) == 12


def test_bars_and_ladders_frozen():
    assert e0.BAR_FP == 1e-12
    assert e0.BAR_LEDGER == 1e-9
    assert e0.BAR_PHYS == 1e-6
    assert e0.BAR_U1 == 1e-12
    assert e0.BAR_SPEC == 1e-9
    assert e0.T_LADDER == (0.0, 0.5, 1.0, 2.0, 4.0, 8.0)
    assert e0.DT_EV0 == 0.05
    assert e0.T28 == (0.0, 1.0, 2.0)
    assert e0.DT28 == 0.1
    assert e0.R_LOCAL == 4
    assert e0.CONE_V == 8.0
    assert e0.MUTATION_DELTA == complex(0.5, -0.25)
    assert e0.fitted_param_count() == 0
    assert e0.VERDICT_LADDER == ("EVENT0-FORCED", "EVENT0-INSTABILITY",
                                 "EVENT0-EQUIV", "EVENT0-CONDITION",
                                 "EVENT0-NULL", "EVENT0-INCOMPLETE")


def test_campaign_argv_unique():
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..",
                                    "scripts"))
    import event0_campaign as camp

    argv = [camp.task_argv(t) for t in e0.all_tasks()]
    assert len(argv) == 463
    assert len(set(argv)) == 463


# ---------------------------------------------------------------------------
# Fields + eigen-certification
# ---------------------------------------------------------------------------

def test_int_fields_frozen():
    from bh_graph.ballistic import packet_spread_ok

    assert packet_spread_ok(1.0, (8,))
    ring = m0.build_substrate("ring-8")
    for tag in ("INT-ring-headon", "INT-ring-chase"):
        psi = e0.build_traj_field(ring, tag)
        assert abs(float(np.vdot(psi, psi).real) - 1.0) < 1e-12
    j2 = m0.build_substrate("j2-L4")
    a = e0.build_traj_field(j2, "INT-j2-twospike-0")
    b = e0.build_traj_field(j2, "INT-j2-twospike-pi2")
    assert abs(float(np.vdot(a, a).real) - 1.0) < 1e-12
    assert abs(abs(complex(np.vdot(a, b))) - 1.0 / np.sqrt(2.0)) < 1e-9
    hb = m0.build_substrate("handbuilt")
    c = e0.build_traj_field(hb, "INT-hb-twospike")
    assert abs(float(np.vdot(c, c).real) - 1.0) < 1e-12


def test_j2_eigen_certs():
    from bh_graph.ballistic import hamiltonian

    s = m0.build_substrate("j2-L4")
    h = hamiltonian(s["g"], j=1.0, order=list(s["order"]))
    for tag in ("VPLUS", "VPI", "VMINUS", "VSTAG", "CIRCLE_pi6",
                "stagger0", "stagger_pi"):
        psi = e0.build_traj_field(s, tag)
        cert = e0.rayleigh_residual(h, psi)
        assert cert["is_eigen"], tag
    z = e0.build_traj_field(s, "zero")
    assert e0.rayleigh_residual(h, z)["is_zero"]
    g = e0.build_traj_field(s, "random777")
    assert not e0.rayleigh_residual(h, g)["is_eigen"]


def test_uniform_aliases_noted():
    s = m0.build_substrate("j2-L4")
    u = e0.build_traj_field(s, "uniform")
    v = e0.build_traj_field(s, "VPLUS")
    assert np.allclose(u, v)


# ---------------------------------------------------------------------------
# Trajectory apparatus (tiny)
# ---------------------------------------------------------------------------

def test_traj_triangle_valid_and_deterministic():
    r1 = e0.traj_record("bare", "triangle", "uniform")
    r2 = e0.traj_record("bare", "triangle", "uniform")
    assert r1["all_valid"] and r1["t_star"] is None
    assert r1["crossings"]["n_cross"] == 0
    assert r1["cert"]["is_eigen"]
    assert r1 == r2


def test_traj_handbuilt_generic_runs():
    r = e0.traj_record("bare", "handbuilt", "random777")
    assert r["all_valid"]
    assert len(r["rungs"]) == 6
    assert r["equiv"]["n_rewires"] >= 0
    assert r["neighbors"]["n_split_nbrs"] == 0


def test_traj_stored_tiny_runs():
    r = e0.traj_record("stored", "handbuilt", "uniform")
    assert r["all_valid"]
    assert r["q_same_all"]
    assert all(rr["pred_ok"] and rr["roundtrip_ok"] for rr in r["rungs"])
    assert all(abs(rr["closure_err"]) < 1e-12 for rr in r["rungs"])
    assert all(abs(rr["invert_err"]) < 1e-9 for rr in r["rungs"])
    assert r["neighbors"]["n_split_nbrs"] == 1


# ---------------------------------------------------------------------------
# REG mechanics (tiny samples)
# ---------------------------------------------------------------------------

def test_reg_merge_triangle():
    r = e0.reg_merge_record("triangle", "uniform", 0, "")
    assert r["det_ok"] and r["rcov_ok"] and r["ucov_ok"] and r["ledger_ok"]


def test_reg_split_cells():
    for cell in e0.REG_SPLIT_CELLS:
        r = e0.reg_split_record(*cell)
        assert r["roundtrip_ok"] and r["minimal_ok"], cell


def test_reg_rewire_tiny():
    r = e0.reg_rewire_record("tiny-path4", "uniform")
    assert r["ledger_ok"] and r["n_phys"] == 1
    r2 = e0.reg_rewire_record("tiny-triangle", "current")
    assert r2["ledger_ok"] and r2["n_phys"] == 0


# ---------------------------------------------------------------------------
# EQUIV search (tiny)
# ---------------------------------------------------------------------------

def test_spectral_screen_selfcheck():
    s = _tri()
    ev = e0.spectrum_of(s["g"], list(s["order"]))
    assert e0.is_cospectral_ok(ev, ev)
    assert not e0.is_cospectral_ok(ev, ev + 1.0)


def test_equiv_triangle_none():
    s = _tri()
    order = list(s["order"])
    psi = np.full(len(order), 1.0 / np.sqrt(len(order)))
    out = e0.equiv_search(s["g"], [psi], order, None, False)
    assert out["n_rewires"] == 0
    assert out["n_nontrivial"] == 0


def test_equiv_path4_completes():
    from bh_graph import rewire0 as r0

    g = r0.tiny_graph("path4")
    order = sorted(g.nodes())
    psi = r0.tiny_field("uniform", order)
    out = e0.equiv_search(g, [psi], order, None, False)
    # The single path4 rewire preserves the path class (parallel
    # re-pairing); uniform psi is compatible with every sigma, so the
    # search must file exactly one verified nontrivial orbit (exact).
    assert out["n_rewires"] == 1
    assert out["n_cospec"] == 1 and out["n_iso"] == 1
    assert out["n_nontrivial"] == 1
    assert out["orbits"]["exact"] is True
    assert out["orbits"]["n_orbits"] == 1


def test_psi_compat_exact():
    order = [0, 1, 2]
    u = np.full(3, 1.0 / np.sqrt(3), dtype=np.complex128)
    assert e0.is_psi_compat_ok(u, order, {0: 1, 1: 0, 2: 2})
    z = np.zeros(3, dtype=np.complex128)
    assert e0.is_psi_compat_ok(z, order, {0: 1, 1: 0, 2: 2})
    s = np.array([1.0, 0.0, 0.0], dtype=np.complex128)
    assert not e0.is_psi_compat_ok(s, order, {0: 1, 1: 0, 2: 2})
    assert e0.is_psi_compat_ok(s, order, {0: 0, 1: 1, 2: 2})


def test_orbit_quotient_empty():
    s = _tri()
    out = e0.orbit_quotient([], s["g"], list(s["order"]), None)
    assert out["n_orbits"] == 0 and out["exact"] is True


def test_neighbor_census_triangle():
    s = _tri()
    order = list(s["order"])
    psi = np.full(len(order), 1.0 / np.sqrt(len(order)))
    nb = e0.neighbor_census(s["g"], psi, order, False, False)
    assert nb["n_merge_nbrs"] == 3
    assert nb["n_split_nbrs"] == 0
    assert nb["n_rewire_nbrs"] == 0


def test_virtual_continuations_passing_state():
    s = _tri()
    order = list(s["order"])
    psi = np.full(len(order), 1.0 / np.sqrt(len(order)))
    out = e0.virtual_continuations(s["g"], psi, order, None, None,
                                   None, None, False)
    assert out["merge_tot"] == 3
    assert out["total_in"] == out["merge_in"] + out["split_in"] \
        + out["rewire_in"]
    assert out["unique"] is False


# ---------------------------------------------------------------------------
# Crossings + validity + Q (pure)
# ---------------------------------------------------------------------------

def test_crossing_census_pure():
    assert e0.crossing_census([[0, 0], [0, 0]], 7, (0.0, 1.0))[
        "n_cross"] == 0
    out = e0.crossing_census([[0, 0], [1, 0]], 7, (0.0, 1.0))
    assert out["n_cross"] == 1
    assert out["witness"]["edge"] == 0
    assert out["witness"]["rung"] == 1


def test_validity_bare_bounds():
    ok = e0.validity_bare(1.0, 1.0, -2.0, -2.0, True, False)
    assert ok["valid"]
    bad = e0.validity_bare(1.0 + 1e-6, 1.0, -2.0, -2.0, True, False)
    assert not bad["valid"] and not bad["V1"]
    zero = e0.validity_bare(0.0, 0.0, 0.0, 0.0, True, True)
    assert zero["valid"]


def test_q_equal_exact():
    q1 = {"cover": [[1], [2]], "d": complex(0.5, -0.25)}
    q2 = {"cover": [[1], [2]], "d": complex(0.5, -0.25)}
    q3 = {"cover": [[1], [2]], "d": complex(0.5, -0.24)}
    assert e0.is_q_equal(q1, q2)
    assert not e0.is_q_equal(q1, q3)
    assert not e0.is_q_equal(q1, {})


# ---------------------------------------------------------------------------
# LOC + CYC (tiny)
# ---------------------------------------------------------------------------

def test_loc_static_tiny():
    r = e0.loc_record("bare", "triangle", "uniform")
    assert r["static_ok"] and r["far_flips"] == 0
    assert r["causal"] is None


def test_cyc_tiny():
    r = e0.cyc_record("bare", "triangle", "uniform")
    assert r["return_ok"] and r["inverse_ok"]


# ---------------------------------------------------------------------------
# Firewall + audit + pins
# ---------------------------------------------------------------------------

def test_implication_scan_clean_and_live():
    assert e0.implication_scan()["n_hits"] == 0
    assert e0._scan_text("y = argmax(z)")["n_hits"] >= 1
    assert e0._scan_text("clean line")["n_hits"] == 0


def test_no_rng_in_source():
    import inspect

    src = inspect.getsource(e0)
    lines = src.splitlines()
    in_list = False
    body = []
    for line in lines:
        if "FORBIDDEN_TOKENS" in line and "=" in line:
            in_list = True
        if in_list:
            if line.strip().endswith(")"):
                in_list = False
            continue
        body.append(line)
    text = "\n".join(body)
    assert "default_rng" not in text
    assert "np.random" not in text


def test_audit_citations_hold():
    aud = e0.audit_record()
    assert aud["BR27_NO_MODE"] is True
    assert aud["MERGE0_J_NORULE"] is True
    assert aud["MEASURE0"] == "MEASURE0-DEBT"
    assert aud["TRIGGER0_implications"] == []
    assert aud["QDYN0B"] == "QDYN0B-EVENT-LOCAL"
    assert aud["n_implications"] == 0
    assert aud["n_pred"] == 21


def test_pinned_qdyn0b_hash():
    import json

    path = os.path.join(os.path.dirname(__file__), "..", "data",
                        "event0", "ref", "qdyn0b_verdict.json")
    with open(path) as f:
        blob = f.read()
    assert json.loads(blob)["verdict"] == "QDYN0B-EVENT-LOCAL"
    assert hashlib.sha256(blob.encode()).hexdigest() == \
        "e1462c86ad8deba7c1209d24f6f9420948ee5f95d920581edf4bbf7d1f558b85"
