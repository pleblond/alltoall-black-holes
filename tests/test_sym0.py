"""SYM-0 pins: inventory, exact identities, stabilizers, recount numbers.

Fast only (tiny graphs + J2-L4 sheet algebra); the full census runs in
scripts/sym0_campaign.py on beast. All pins frozen pre-data (SYM0-PREREG).
"""

import math

import numpy as np

from bh_graph import sym0
from bh_graph.rand0 import rand0_states, tiny_field, tiny_graph


def _square():
    tg = tiny_graph("square")
    return tg["g"], list(tg["order"])


def test_inventory_registry_complete():
    inv = sym0.transform_inventory()
    assert sorted(inv) == sorted(sym0.TRANSFORM_IDS)
    assert sym0.TRANSFORM_IDS[7] == "Sign"  # documents U1(pi) alias position


def test_applicability_gating():
    subs = sym0.sym0_substrates()
    assert sym0.is_transform_applicable_ok("S", subs["j2-L6"]) is True
    assert sym0.is_transform_applicable_ok("S", subs["ring-12"]) is False
    assert sym0.is_transform_applicable_ok("T", subs["ring-12"]) is True
    assert sym0.is_transform_applicable_ok("T", subs["path-12"]) is False
    assert sym0.is_transform_applicable_ok("SectorSign", subs["j2-L4"]) is True
    assert sym0.is_transform_applicable_ok("U1", subs["k2"]) is True


def test_relabel_roundtrip_identity():
    g, order = _square()
    psi = tiny_field(len(order), "bonding")
    p = sym0.reversal_perm(order)
    once = sym0.apply_relabel(g, psi, order, p)
    inv = {b: a for a, b in p.items()}
    twice = sym0.apply_relabel(once["g"], once["psi"], once["order"], inv)
    idx = {v: i for i, v in enumerate(order)}
    idx2 = {v: i for i, v in enumerate(twice["order"])}
    back = np.array([twice["psi"][idx2[v]] for v in order])
    assert np.abs(back - psi).max() == 0.0
    assert {tuple(sorted(e)) for e in twice["g"].edges()} == {
        tuple(sorted(e)) for e in g.edges()}


def test_u1_preserves_bj_energy():
    g, order = _square()
    psi = tiny_field(len(order), "bonding")
    o1 = sym0.observe_o2(psi, g, order, sym0.sym0_substrates()["square"])
    o2 = sym0.observe_o2(sym0.apply_u1(psi, 0.7), g, order,
                         sym0.sym0_substrates()["square"])
    d = sym0.obs_distance(o1, o2, "O2")
    assert max(d.values()) < sym0.FP_ZERO


def test_conjugation_flips_j_preserves_b_rho():
    tg = tiny_graph("path4")
    g, order = tg["g"], list(tg["order"])
    psi = tiny_field(len(order), "current")
    e1 = sym0.edge_bj(psi, g, order)
    e2 = sym0.edge_bj(sym0.apply_conj(psi), g, order)
    for k in e1["B"]:
        assert abs(e1["B"][k] - e2["B"][k]) == 0.0
        assert abs(e1["J"][k] + e2["J"][k]) == 0.0
    r1 = sym0.observe_o1(psi)["rho"]
    r2 = sym0.observe_o1(sym0.apply_conj(psi))["rho"]
    assert np.abs(r1 - r2).max() == 0.0
    assert max(abs(v) for v in e1["J"].values()) > 0  # current carries J


def test_sector_sign_equals_sheet_exchange():
    subs = sym0.sym0_substrates()
    sub = subs["j2-L4"]
    fields = sym0.sym0_fields(sub)
    for name, psi in fields.items():
        a = sym0.apply_sector_sign(psi, sub["order"], sub["c3"])
        b = sym0.apply_sheet_exchange(psi, sub["order"], sub["c3"])
        assert np.abs(a - b).max() < sym0.FP_ZERO, name


def test_sheet_phase_pi_makes_anti():
    from bh_graph.malus import sheet_projectors, sheet_weights
    subs = sym0.sym0_substrates()
    sub = subs["j2-L4"]
    fields = sym0.sym0_fields(sub)
    pr = sheet_projectors(sub["order"], sub["c3"])
    w0 = sheet_weights(fields["uniform"], pr)
    assert abs(w0["w_sym"] - 1.0) < sym0.FP_ZERO
    flipped = sym0.apply_sheet_phase(fields["uniform"], sub["order"],
                                     sub["c3"], math.pi)
    w1 = sheet_weights(flipped, pr)
    assert abs(w1["w_anti"] - 1.0) < sym0.FP_ZERO


def test_theta_identity_tiny():
    tg = tiny_graph("triangle")
    g, order = tg["g"], list(tg["order"])
    psi = tiny_field(len(order), "bonding")
    assert sym0.is_theta_identity_ok(psi, g, order, 0.5)


def test_u1_covariance_exact():
    g, order = _square()
    psi = tiny_field(len(order), "bonding")
    err = sym0.covariance_err(lambda p: sym0.apply_u1(p, 1.1), psi, g, order)
    assert err < sym0.KRYLOV_BAR


def test_full_aut_counts():
    tg = tiny_graph("triangle")
    assert sym0.full_aut_group(tg["g"])["ok"] is True
    assert len(sym0.full_aut_group(tg["g"])["auts"]) == 6  # S3
    g, _ = _square()
    assert len(sym0.full_aut_group(g)["auts"]) == 8  # D4
    big = sym0.sym0_substrates()["j2-L6"]["g"]
    assert sym0.full_aut_group(big) == {"ok": False, "reason": "scope-cap-N>10",
                                        "auts": []}


def test_stabilizer_uniform_vs_generic():
    g, order = _square()
    auts = sym0.full_aut_group(g)["auts"]
    uni = tiny_field(len(order), "bonding")
    st = sym0.stabilizer_of(uni, order, auts)
    assert st["size"] == 8 and st["group_size"] == 8
    assert sym0.is_orbit_identity_ok(uni, order, auts)
    gen = sym0.sym0_fields(sym0.sym0_substrates()["square"])["generic-s0"]
    stg = sym0.stabilizer_of(gen, order, auts)
    assert stg["size"] == 1  # generic breaks D4 fully (frozen seed 0)
    assert sym0.is_orbit_identity_ok(gen, order, auts)


def test_conj_u1_stabilizer_kinds():
    g, order = _square()
    real = tiny_field(len(order), "bonding")
    assert sym0.conj_stabilizer_kind(real) == "full"
    cx = tiny_field(len(order), "bonding") * np.exp(1.0j * 0.3)
    cx = cx.copy()
    cx[0] += 0.1j
    assert sym0.conj_stabilizer_kind(cx) == "trivial"
    assert sym0.u1_stabilizer_kind(np.zeros(4)) == "U1-full"
    assert sym0.u1_stabilizer_kind(real) == "trivial"


def test_fs_distance_quotient_metric():
    psi = tiny_field(4, "bonding")
    phi = sym0.apply_u1(psi, 2.0)
    assert sym0.fs_distance(psi, phi) < sym0.FP_ZERO
    chi = tiny_field(4, "current") if len(psi) == 4 else phi
    assert sym0.is_fs_triangle_ok(psi, phi, chi)
    al = sym0.phase_align(phi, psi)
    assert abs(complex(np.vdot(psi, al)).imag) < 1e-12


def test_recount_star4_numbers():
    st = rand0_states()["T7"]  # star4 bonding (center degree 4)
    g, psi, order = st["g"], st["psi"], st["order"]
    k = max(g.degree(), key=lambda t: t[1])[0]
    rec = sym0.recount_node_patch(g, psi, order, k)
    assert rec["n_directed"] == 82  # NONE + 3^4
    assert rec["n_undirected"] == 42  # NONE + (81+1)/2
    assert rec["iso_capped"] is False
    assert rec["stab_capped"] is False
    assert rec["red_trivial_action"] is True
    assert rec["n_red_quotient"] == 42


def test_indifference_gap_logic():
    assert sym0.indifference_gap(82, 42)["uniform_differs"] is True
    assert sym0.indifference_gap(42, 42)["uniform_differs"] is False


def test_hierarchy_helpers():
    flags = {("a", "b"): True, ("b", "c"): False, ("a", "c"): False}
    cls = sym0.equivalence_classes(flags, ["a", "b", "c"])
    assert sorted(map(sorted, cls)) == [["a", "b"], ["c"]]
    assert sym0.is_hierarchy_monotone_ok([1, 1, 2, 3, 3]) is True
    assert sym0.is_hierarchy_monotone_ok([2, 1, 2, 2, 2]) is False
    h = sym0.hierarchy_counts({"O1": 1, "O2": 2, "O3": 2, "O4": 3, "O5": 3})
    assert h["monotone_nondecreasing"] is True


def test_perm_auto_check():
    from bh_graph.potential import translate_perm
    sub = sym0.sym0_substrates()["j2-L4"]
    assert sym0.is_perm_auto_ok(sub["g"], translate_perm(4, 1, 0)) is True
    tg = tiny_graph("path4")
    rot = {v: (v + 1) % 4 for v in range(4)}
    assert sym0.is_perm_auto_ok(tg["g"], rot) is False
    assert sym0.is_perm_auto_ok(tg["g"], sym0.path_reversal(4)) is True


def test_uniform_mode_energy_regular():
    sub = sym0.sym0_substrates()["ring-12"]
    assert abs(sym0.uniform_mode_energy(sub["g"], sub["order"]) + 2.0) < 1e-12


def test_energy_identity_repin():
    from bh_graph.ug import field_energy
    g, order = _square()
    psi = tiny_field(len(order), "bonding")
    e = sym0.edge_bj(psi, g, order)
    assert abs(field_energy(psi, g, order) + 2.0 * sum(e["B"].values())) < 1e-12


def test_marks_covariance_and_phase_tiny():
    g, order = _square()
    psi = tiny_field(len(order), "bonding")
    p = sym0.reversal_perm(order)
    for law in ("UB", "UL", "UEc"):
        assert sym0.marks_covariance_R(g, psi, order, law, p) is True
        assert sym0.marks_phase_invariance(g, psi, order, law, 0.7) is True
        assert sym0.marks_conjugation_table(g, psi, order, law)["invariant"] is True


def test_observe_all_smoke_k2():
    subs = sym0.sym0_substrates()
    sub = subs["k2"]
    psi = sym0.sym0_fields(sub)["uniform"]
    obs = sym0.observe_all(psi, sub["g"], sub["order"], sub)
    assert sorted(obs) == ["O1", "O2", "O3", "O4", "O5"]
    assert obs["O1"]["rho"].shape == (2,)
    assert obs["O4"]["pot_profile"].shape == (2,)


def test_observe_all_smoke_j2():
    subs = sym0.sym0_substrates()
    sub = subs["j2-L4"]
    psi = sym0.sym0_fields(sub)["packet"]
    obs = sym0.observe_all(psi, sub["g"], sub["order"], sub)
    assert "sheet" in obs["O2"] and "spec_coh" in obs["O2"]
    assert "dir_order_t0" in obs["O3"] and "d_trace" in obs["O3"]
    assert "pot_sheet_asym" in obs["O4"] and "wave_shell_trace" in obs["O4"]
    assert len(obs["O5"]["arrival_taus"]) == 4


def test_scale_shift_exact_laws():
    g, order = _square()
    psi = tiny_field(len(order), "bonding")
    o1 = sym0.observe_o1(psi)
    o2 = sym0.observe_o1(sym0.apply_scale(psi, 2.0))
    assert np.abs(o2["rho"] - 4.0 * o1["rho"]).max() == 0.0
    e1 = sym0.edge_bj(psi, g, order)
    e2 = sym0.edge_bj(sym0.apply_scale(psi, 0.5), g, order)
    assert abs(e2["B"][(0, 1)] - 0.25 * e1["B"][(0, 1)]) == 0.0
