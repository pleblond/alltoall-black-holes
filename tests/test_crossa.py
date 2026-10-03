"""CROSS-IMPL-A pins (frozen apparatus checks, pre-data).

Pins cover factorization (synthetic inputs), amplitude-ratio form,
endpoint handling, deficit expansion, convergence rules, firewall, and
counts. No pin reconstructs ladder psi or computes campaign observables
(no eigensolver, no R2/C2/X2 on ladder graphs).
"""

import math

import numpy as np

from bh_graph import crossa as cx


def test_crossa_design_frozen():
    assert cx.R_LADDER == (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    assert cx.MARGIN == 4
    assert cx.TOP_RUNGS == (8, 9, 10)
    assert cx.J_DOMAIN == 0.1
    assert cx.BAR_FP == 1e-12
    assert cx.BAR_CENSUS == 1e-9
    assert cx.BAR_J_REL == 0.10
    assert cx.BAR_REL == 0.05
    assert cx.R_HI == 0.5
    assert cx.C_HI == 0.5
    assert cx.QINFO_EXPECTED.startswith("b737d5e1")
    assert len(cx.QINFO_EXPECTED) == 64


def test_crossa_factor_identity():
    assert cx.is_factor_identity_ok()


def test_crossa_factor_values():
    rep = cx.factor_edge(complex(3.0, 0.0), complex(1.0, 0.0))
    assert rep["endpoint"] == "ok"
    assert abs(rep["q"] - 10.0) < 1e-12
    assert abs(rep["B"] - 3.0) < 1e-12
    assert abs(rep["x"] - 0.3) < 1e-12
    assert abs(rep["r"] - 0.6) < 1e-12
    assert abs(rep["c"] - 1.0) < 1e-12
    assert abs(2.0 * rep["x"] - rep["r"] * rep["c"]) < 1e-12
    assert abs(rep["lam"] - 3.0) < 1e-12
    assert abs(rep["r"] - 1.0 / math.cosh(rep["loglam"])) < 1e-12
    quad = complex(1.0, 0.0)
    quad_j = complex(0.0, 1.0)
    rq = cx.factor_edge(quad, quad_j)
    assert abs(rq["r"] - 1.0) < 1e-12
    assert abs(rq["c"] - 0.0) < 1e-12
    assert abs(rq["x"] - 0.0) < 1e-12
    assert abs(rq["h_Q"] - 1.0) < 1e-12


def test_crossa_endpoints():
    z = cx.factor_edge(0j, 0j)
    assert z["endpoint"] == "q_zero"
    assert z["r"] == 0.0 and z["c"] is None
    assert z["x"] is None and z["h_Q"] is None
    assert z["lam"] is None and z["loglam"] is None
    a = cx.factor_edge(0j, complex(1.0, 2.0))
    assert a["endpoint"] == "ai_zero"
    assert a["r"] == 0.0 and a["c"] is None
    assert abs(a["x"] - 0.0) < 1e-12
    assert abs(a["h_Q"] - 1.0) < 1e-12
    b = cx.factor_edge(complex(3.0, -1.0), 0j)
    assert b["endpoint"] == "aj_zero"
    assert b["r"] == 0.0 and b["c"] is None
    assert abs(b["x"] - 0.0) < 1e-12


def test_crossa_deficit_expansion():
    assert cx.is_deficit_expansion_ok()
    rep = cx.factor_edge(complex(1.0, 0.0), complex(1e-3, 0.0))
    x = rep["x"]
    assert abs(x) < 0.1
    lhs = float(1.0 - rep["h_Q"])
    quad = float(rep["r"] ** 2 * rep["c"] ** 2 / (2.0 * math.log(2.0)))
    assert abs(lhs - quad) / max(lhs, 1e-12) < 0.01


def test_crossa_convergence_rules():
    assert cx.is_convergence_rules_ok()
    assert cx.classify_track([9.0, 8.0, 7.0, 6.0, 5.0, 4.0,
                              4.0, 3.0, 2.0, 1.0]) == "ZERO"
    assert cx.classify_track([1.0] * 10) == "NONZERO"
    assert cx.classify_track([0.0] * 10) == "ZERO"
    assert cx.classify_track([5.0, 5.0, 5.0, 5.0, 5.0, 5.0,
                              1.0, 0.3, 0.9, 0.4]) == "UNRESOLVED"
    assert cx.classify_track([1.0, 2.0]) == "ERROR"


def test_crossa_gamma_math():
    r = np.array([0.1, 0.5, 1.0, 0.0])
    c = np.array([1.0, 0.5, 0.0, 0.0])
    r2 = float(np.mean(r ** 2))
    c2 = float(np.mean(c[:3] ** 2))
    x2 = float(np.mean([0.01, 0.0625, 0.0, 0.0]))
    g = float(x2 / (r2 * c2))
    assert abs(r2 - 0.315) < 1e-12
    assert g > 0.0 and g < 2.0


def test_crossa_firewall_and_params():
    assert cx.is_firewall_ok()
    assert cx.fitted_param_count() == 0
    for attr in ("H_total", "Htotal", "total_entropy", "mutual_info",
                 "S_BH", "area_law"):
        assert not hasattr(cx, attr)
    assert cx.filed_tokens(cx.__file__) == []


def test_crossa_counts_and_hashes():
    assert cx.is_battery_counts_ok()
    c = cx.battery_counts()
    assert c["total"] == 53
    h = cx.input_hashes()
    assert set(h) == {"qinfo0", "bhqarea0", "graphs", "dim3"}
    assert all(len(v) == 64 for v in h.values())
    assert h["qinfo0"] == cx.QINFO_EXPECTED
