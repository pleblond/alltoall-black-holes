"""Q-DYN-0b pins (frozen pre-data; fast, deterministic, no RNG)."""

import numpy as np

from bh_graph import qdyn0 as q0
from bh_graph import qdyn0b as q1


def test_bars_frozen():
    assert q1.BAR_FP == 1e-12
    assert q1.BAR_LEDGER == 1e-9
    assert q1.BAR_PHYS == 1e-6
    assert q1.BAR_U1 == 1e-12
    assert q1.MAP == "sum"
    assert q1.T_LADDER == q0.T_LADDER == (0.0, 0.5, 1.0, 2.0, 4.0, 8.0)
    assert q1.DT_QDYN == q0.DT_QDYN == 0.05
    assert q1.T_MAX == q0.T_MAX == 8.0
    assert q1.T_CYC == 2.0
    assert q1.U1_ALPHAS == q0.U1_ALPHAS


def test_verdict_ladder_constants():
    assert q1.VERDICT_LADDER == ("QDYN0B-PERSISTENT",
                                 "QDYN0B-EVENT-LOCAL",
                                 "QDYN0B-FROZEN-RELATIONAL",
                                 "QDYN0B-RESIDUAL",
                                 "QDYN0B-INCOMPLETE")
    groups = q1.GATE_GROUPS
    assert set(groups) == {"counts", "REG", "QDYNOREG", "APPARATUS",
                           "MECHANISM", "FILED"}
    n_gates = sum(len(v) for v in groups.values())
    assert n_gates == 51


def test_battery_census():
    assert len(q1.reg_tasks()) == 349
    assert len(q1.waitb_tasks()) == 69
    assert len(q1.eigen_tasks()) == 10
    assert len(q1.splitback_tasks()) == 12
    assert len(q1.cycle_tasks()) == 6
    assert len(q1.sym_tasks()) == 12
    assert len(q1.loc_tasks()) == 10
    assert len(q1.hid_tasks()) == 8
    assert len(q1.src_tasks()) == 12
    assert len(q1.multi_tasks()) == 9
    assert len(q1.stoch_tasks()) == 6
    assert len(q1.audit_tasks()) == 1
    total = len(q1.all_tasks())
    assert total == 504
    assert q1.all_tasks() == q1.all_tasks()
    assert len(q1.battery_checksum()) == 64


def test_fitted_params_zero():
    assert q1.fitted_param_count() == 0
    assert q1.is_no_hidden_tuning_ok() is True
    assert q1.is_no_dynamics_ok() is True


def test_inventory_no_q_flow():
    inv = q1.inventory_report_b()
    assert inv["n"] == len(q0.TRANSITION_INVENTORY) + 14
    assert all(r["resolvable"] for r in inv["rows"])
    assert inv["q_flow_maps"] == []
    assert inv["earned_q_updater_without_event"] is False


def test_ref_verdict_present():
    ref = q1.qdyn0_ref_verdict()
    assert ref["present"] is True
    assert ref["verdict"] == "QDYN0-INCOMPLETE"
    assert ref["n_pass"] == 33
    assert ref["n_gates"] == 35


def _merge_bundle(subname="ring-8", ftag="uniform", ei=0):
    from bh_graph import merge0 as m0

    sub = m0.build_substrate(subname)
    edge = tuple(q0.wait_edges(sub, ftag)[ei])
    psi = np.asarray(q0.build_wait_field(sub, ftag),
                     dtype=np.complex128)
    return q1.merge_plus_store(sub, psi, edge)


def test_decompose_smoke():
    b = _merge_bundle()
    dec = q1.decompose_readout(b["g2"], b["psi2_0"], b["order2"],
                               b["k"], b["q"], b["frame"])
    assert abs(dec["closure_err"]) < q1.BAR_FP
    assert abs(dec["cos_law_err"]) < q1.BAR_FP
    rd = q0.store_readout(b["g2"], b["psi2_0"], b["order2"],
                          b["k"], b["q"], b["frame"])
    assert dec["E_Q"] == rd["E_Q"]
    assert dec["Acoef"] == rd["Acoef"]


def test_u1_law_smoke():
    b = _merge_bundle("ring-8", "random777", 0)
    u = q1.u1_law_rows(b["g2"], b["psi2_0"], b["order2"], b["k"],
                       b["q"], b["frame"])
    assert u["A_inv_max"] < q1.BAR_FP
    assert u["Re_law_max"] < q1.BAR_FP
    assert u["EQ_law_max"] < q1.BAR_FP
    assert len(u["rows"]) == len(q1.U1_ALPHAS)


def test_waitb_record_smoke():
    rec = q1.waitb_record("ring-8", "uniform", 0, "")
    assert "qdyn0" in rec and "qb" in rec
    assert len(rec["qb"]["rungs"]) == len(q1.T_LADDER)
    assert rec["qb"]["R0_match"] is True
    assert rec["qb"]["selfcheck_max"] < q1.BAR_FP
    assert all(abs(r["closure_err"]) < q1.BAR_FP
               for r in rec["qb"]["rungs"])
    assert all(abs(r["attrib_err"]) < q1.BAR_FP
               for r in rec["qb"]["rungs"])
    assert "E_aug_spread" in rec["qb"]
    assert rec["qdyn0"]["E_Q_spread"] >= 0.0


def test_eigen_record_smoke():
    import json
    import os

    rec = q1.eigen_record("j2-L4", "uniform", 0)
    assert rec["res_pre_HG"] == 0.0
    assert rec["res_post_HG2"] > 0.09
    assert rec["d0"] is True
    assert rec["true_eigvec_max_spread"] < q1.BAR_LEDGER
    ref_path = os.path.join(q1.ref_dir(), "autopsy_eigen.json")
    with open(ref_path) as f:
        auto = json.load(f)
    cells = {(c["sub"], c["ftag"], tuple(c["edge"])): c
             for c in auto["cells"]}
    ref = cells[("j2-L4", "uniform", (rec["edge"][0],
                                      rec["edge"][1]))]
    assert abs(rec["true_eigvec_max_spread"]
               - ref["true_eigvec_max_spread"]) < q1.BAR_LEDGER
    assert abs(rec["res_post_HG2"] - ref["res_post_HG2"]) \
        < q1.BAR_LEDGER


def test_splitback_record_smoke():
    rec = q1.splitback_record("ring-8", "uniform", 0)
    assert len(rec["rungs"]) == len(q1.T_LADDER)
    assert all(r["pred_ok"] and r["roundtrip_ok"]
               for r in rec["rungs"])
    assert all(abs(r["invert_current_err"]) < q1.BAR_LEDGER
               for r in rec["rungs"])
    assert "R_merge_M0" in rec


def test_cycle_record_smoke():
    rec = q1.cycle_record("ring-8", "uniform", 0)
    assert rec["return_err"] < q1.BAR_LEDGER
    assert abs(rec["ledger_closure"]) < q1.BAR_LEDGER
    assert rec["pred_ok"] is True and rec["roundtrip_ok"] is True
    assert rec["norm_drift"] < 1e-9


def test_cov_record_smoke():
    rec = q1.cov_record("ring-8", "uniform", 0)
    assert "qdyn0_sym" in rec and "qb" in rec
    assert abs(rec["qb"]["swap_EQ_T_err"]) <= q1.BAR_FP
    assert abs(rec["qb"]["rel_EQ_T_err"]) < q1.BAR_LEDGER
    assert rec["qb"]["u1_t0"]["EQ_law_max"] < q1.BAR_FP


def test_loc_record_smoke():
    rec = q1.loc_record("ring-8", "uniform", 0)
    assert rec["applicable"] is True
    assert abs(rec["qb"]["FR_t0_err"]) < q1.BAR_LEDGER
    assert rec["qb"]["q_same_T"] is True


def test_src_record_smoke():
    rec = q1.src_record("VPLUS", "point", "near")
    assert rec["applicable"] is True
    assert abs(rec["qb"]["attrib_err"]) < q1.BAR_FP
    assert rec["qb"]["q_fixed"] is True


def test_hid_record_smoke():
    rec = q1.hid_record("j2-L4", "P:sign", 0)
    assert rec["qb"]["pair"] is True
    assert "cross" in rec["qb"]
    tex = q1.hid_record("j2-L4", "H:delta", 0)
    assert tex["qb"]["pair"] is False
    assert abs(tex["qb"]["closure"]) < q1.BAR_FP


def test_multi_stoch_smoke():
    rec = q1.multi_record_seq("handbuilt-chain", "uniform")
    assert rec["qdyn0_multi"]["keys_same"] is True
    rec = q1.multi_record_pair("ring-8", "uniform", "disjoint")
    assert "qdyn0_multi" in rec
    rec = q1.stoch_record("triangle", "bonding", 0)
    assert rec["qdyn0_stoch"]["both_valid"] is True


def test_audit_record_smoke():
    rec = q1.audit_record()
    assert rec["fitted_params"] == 0
    assert rec["no_tuning"] is True
    assert rec["no_dynamics"] is True
    assert rec["qdyn0_ref"]["verdict"] == "QDYN0-INCOMPLETE"
    assert rec["inventory_b"]["earned_q_updater_without_event"] \
        is False
    assert rec["qdyn0_audit"]["fitted_params"] == 0


def test_task_kinds():
    kinds = {t[0] for t in q1.all_tasks()}
    assert kinds == {"reg", "waitb", "eigen", "splitback", "cycle",
                     "sym", "loc", "hid", "src", "multi", "stoch",
                     "audit"}


def test_d0_dnonzero_coverage():
    from bh_graph import merge0 as m0

    d0n = 0
    tot = 0
    for sub, tag, ei, mb in q1.waitb_tasks():
        s = m0.build_substrate(sub)
        psi_in = q0.build_wait_field(s, tag)
        if isinstance(psi_in, dict):
            psi = psi_in["psi_A" if mb == "A" else "psi_B"]
        else:
            psi = psi_in
        edge = tuple(q0.wait_edges(s, tag)[ei])
        enc = q1.merge_plus_store(s, np.asarray(psi), edge)
        tot += 1
        if complex(enc["q"]["d"]) == 0j:
            d0n += 1
    assert tot == 69
    assert 0 < d0n < tot
    e0n = 0
    for sub, tag, ei in q1.eigen_tasks():
        s = m0.build_substrate(sub)
        psi = np.asarray(q0.build_wait_field(s, tag))
        edge = tuple(q0.wait_edges(s, tag)[ei])
        enc = q1.merge_plus_store(s, psi, edge)
        if complex(enc["q"]["d"]) == 0j:
            e0n += 1
    assert 0 < e0n < len(q1.eigen_tasks())
