"""BH-Q-AREA-0 pins (frozen apparatus checks, pre-data).

Pins cover formulas (synthetic inputs), core-generator equivalence,
ladder geometry structure (counts only), assembly structure (no psi),
firewall, and counts. No pin computes psi-dependent campaign
observables (no eigensolver, no x/S/hbar/kappa on ladder graphs).
"""

import math

import numpy as np

from bh_graph import bhqarea0 as bq


def test_bhqarea0_design_frozen():
    assert bq.R_LADDER == (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    assert bq.MARGIN == 4
    assert bq.TOP_RUNGS == (8, 9, 10)
    assert bq.rmax_of(10) == 14
    assert abs(bq.area_of(2) - 16.0 * math.pi) < 1e-12
    assert bq.EIG_TOL == 1e-10
    assert bq.EIG_MAXITER == 30000
    assert bq.EIG_NCV == 20


def test_bhqarea0_formula_regression():
    assert bq.is_formula_ok()


def test_bhqarea0_endpoints():
    assert bq.is_endpoints_ok()


def test_bhqarea0_expansion():
    assert bq.is_expansion_ok()
    t = bq.expansion_terms(0.05)
    assert abs(t["quad"] - (2.0 / math.log(2.0)) * 0.05 ** 2) < 1e-15
    assert abs(t["lhs"] - t["quad"] - t["quart"]) < 10.0 * 0.05 ** 6


def test_bhqarea0_edge_terms_values():
    rep = bq.edge_terms(complex(3.0, 0.0), complex(1.0, 0.0))
    assert abs(rep["q"] - 10.0) < 1e-12
    assert abs(rep["B"] - 3.0) < 1e-12
    assert abs(rep["x"] - 0.3) < 1e-12
    assert abs(rep["P_minus"] - 0.2) < 1e-12
    assert abs(rep["s_Q"] - 0.7219280948873623) < 1e-12
    assert bq.edge_terms(0j, 0j) is None


def test_bhqarea0_census_math():
    assert bq.is_census_stats_ok()


def test_bhqarea0_helpers():
    assert bq.is_helpers_ok()


def test_bhqarea0_core_generator():
    assert bq.is_core_generator_ok()
    rows, cols = bq.core_block_coo(4)
    assert len(rows) == 12 and len(cols) == 12
    assert bq.core_edges_equal_complete(6)


def test_bhqarea0_geometry_structure():
    for r in (1, 2, 10):
        assert bq.is_geometry_ok(r)
    rec = bq.geometry_record(2)
    assert rec["n_int"] == 50
    assert rec["n_bnd"] == 312
    assert rec["n_bnd"] == rec["dim3_cut"]
    assert abs(rec["sigma"] - 312.0 / (16.0 * math.pi)) < 1e-12


def test_bhqarea0_assembly_structure():
    for variant in ("headline", "control"):
        asm = bq.assemble_adjacency(1, variant)
        assert asm["n"] == len(asm["order"])
        assert asm["n_int"] == 13
        assert asm["n_bnd"] == 132
        diff = (asm["adj"] - asm["adj"].T).nnz
        assert diff == 0
        assert asm["adj"].diagonal().sum() == 0
    head = bq.assemble_adjacency(2, "headline")
    ctrl = bq.assemble_adjacency(2, "control")
    assert head["cut_pairs"] == ctrl["cut_pairs"]
    # Headline core block: each core node links the other Nc-1 core nodes.
    deg = np.asarray(head["adj"].sum(axis=1)).ravel()
    core_deg = deg[head["disk_idx"]]
    assert bool((core_deg >= 49).all())
    # Control keeps ambient edges only (r=2 ambient is ball(6), E=3504).
    assert ctrl["adj"].nnz == 2 * 3504


def test_bhqarea0_patterns_synthetic():
    order = [(0, 0, 0, 0), (1, 0, 0, 0), (0, 0, 0, 1)]
    vp = bq.pattern_psi("vplus", order)
    assert abs(float(np.vdot(vp, vp).real) - 1.0) < 1e-12
    vi = bq.pattern_psi("vpi", order)
    assert abs(float(np.vdot(vi, vi).real) - 1.0) < 1e-12
    assert vi[0] == -vi[1]
    vm = bq.pattern_psi("vminus", order)
    assert vm[0] == vm[1] and vm[0] == -vm[2]


def test_bhqarea0_firewall_and_params():
    assert bq.is_firewall_ok()
    assert bq.fitted_param_count() == 0
    for attr in ("H_total", "Htotal", "total_entropy", "mutual_info",
                 "S_BH", "area_law"):
        assert not hasattr(bq, attr)


def test_bhqarea0_counts_and_hashes():
    assert bq.is_battery_counts_ok()
    c = bq.battery_counts()
    assert c["total"] == 53
    h = bq.input_hashes()
    assert set(h) == {"qinfo0", "graphs", "dim3"}
    assert all(len(v) == 64 for v in h.values())
