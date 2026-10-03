"""VAC-0D/E D7 pin: coord-less (RR) cells record intrinsic-only data.

Regression test for the D7 crash repair: RR delta cases must not touch
coordinate readouts (null fields) while keeping the D6.3 intrinsic
block. Uses a tiny RR cell (fast); the campaign still uses N=1600/1568.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import vac0_de_campaign as vde


def test_rr_delta_intrinsic_only():
    vde.CELLS["rr3_tiny"] = ("rr", (3, 60, 0), 1.0)
    try:
        assert vde._cases_for("rr3_tiny") == [("rr3_tiny", "delta", "delta", None)]
        rec = vde._evolve_case(("rr3_tiny", "delta", "delta", None))
    finally:
        del vde.CELLS["rr3_tiny"]
    for k in ("prep_D", "prep_S", "prep_angle", "prep_C", "prep_M",
              "mean_D", "max_D", "mean_S", "alpha", "cv_mean50",
              "speed", "r2", "disp"):
        assert rec[k] is None, k
    assert rec["prep_J"] == [None, None]
    assert rec["mean_J"] == [None, None]
    assert rec["v"] == [None, None]
    for k in ("delta_vshell", "delta_r2", "delta_ipr_final",
              "delta_ipr0", "delta_p0_final", "delta_rmax"):
        assert rec[k] is not None, k
    assert rec["norm_dev"] < 1e-9
    assert abs(rec["w_plus"] + rec["w_zero"] + rec["w_minus"] - 1.0) < 1e-9


def test_rr_verdict_undefined():
    vde.CELLS["rr3_tiny"] = ("rr", (3, 60, 0), 1.0)
    try:
        v = vde._verdicts("rr3_tiny", {})
    finally:
        del vde.CELLS["rr3_tiny"]
    assert v == {"headline": "UNDEFINED"}


def test_trans_perm_j2_bijective_sheet_preserving():
    """D8.1: J2 translation is a sheet-preserving permutation (S1 premise)."""
    import math

    from bh_graph.ballistic import node_order
    from bh_graph.formation import j2_torus_coords, j2_torus_graph
    from bh_graph.potential import quotient_coords

    L = 4
    c3 = j2_torus_coords(L)
    order = node_order(j2_torus_graph(L))
    setup = {"kind": "j2", "L": L, "c3": c3,
             "coords": quotient_coords(c3), "order": order}
    perm = vde._trans_perm(setup, 3, 5)
    assert set(perm) == set(order)
    assert set(perm.values()) == set(order)  # bijective (old code: 784->1568 collapse)
    for v, (x, y, b) in c3.items():
        assert c3[perm[v]] == ((x + 3) % L, (y + 5) % L, b)
    # swap/rewire share the J2-label path
    setup["kind"] = "sw8"
    perm = vde._trans_perm(setup, 3, 5)
    assert set(perm.values()) == set(order)


def test_trans_perm_unique_coord_and_ring():
    """D8.1: D6 behavior unchanged off J2 labels."""
    from bh_graph.vac0 import torus_coords_2d

    L = 6
    coords = torus_coords_2d(L)
    order = sorted(coords)
    setup = {"kind": "sq", "L": L, "c3": None, "coords": coords,
             "order": order}
    perm = vde._trans_perm(setup, 3, 5)
    assert set(perm.values()) == set(order)
    for v, (x, y) in coords.items():
        assert coords[perm[v]] == (float((int(x) + 3) % L), float((int(y) + 5) % L))
    rsetup = {"kind": "ring", "L": 20, "c3": None, "coords": None,
              "order": list(range(20))}
    perm = vde._trans_perm(rsetup, 2, 0)
    assert perm == {v: (v + 2) % 20 for v in range(20)}


def test_sq30_wrap_budget():
    """D8.2: sq30 T satisfies the frozen wrap rule with margin."""
    import math

    kind, L, T = vde.CELLS["square_n30"]
    assert (kind, L) == ("sq30", 30)
    assert 2.0 * math.sin(0.5) * T < L / 2
