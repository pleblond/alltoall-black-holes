"""Q-DYN-0 pins (frozen pre-data; fast, deterministic, no RNG)."""

import math

import numpy as np

from bh_graph import qdyn0 as q0


def test_bars_frozen():
    assert q0.BAR_FP == 1e-12
    assert q0.BAR_LEDGER == 1e-9
    assert q0.BAR_PHYS == 1e-6
    assert q0.BAR_U1 == 1e-12
    assert q0.MAP == "sum"


def test_ladder_frozen():
    assert q0.T_LADDER == (0.0, 0.5, 1.0, 2.0, 4.0, 8.0)
    assert q0.DT_QDYN == 0.05
    assert q0.T_MAX == 8.0
    for T in q0.T_LADDER:
        assert abs(T / q0.DT_QDYN - round(T / q0.DT_QDYN)) < 1e-9


def test_verdict_ladder_constants():
    assert q0.VERDICT_LADDER == ("QDYN0-FROZEN", "QDYN0-COEVOLVING",
                                 "QDYN0-HISTORY", "QDYN0-DEBT",
                                 "QDYN0-INCOMPLETE")
    groups = q0.GATE_GROUPS
    assert "counts" in groups and "REG" in groups
    assert "WAIT" in groups and "COEV" in groups
    n_gates = sum(len(v) for k, v in groups.items() if k != "counts")
    n_counts = len(groups["counts"])
    assert n_gates + n_counts == 35


def test_battery_census():
    reg = q0.reg_tasks()
    assert len(reg) == 349
    wt = q0.wait_tasks()
    assert len(wt) > 40
    assert len(q0.sym_tasks()) == 12
    assert len(q0.loc_tasks()) == 10
    assert len(q0.hid_tasks()) == 8
    assert len(q0.src_tasks()) == 12
    assert len(q0.multi_tasks()) == 9
    assert len(q0.stoch_tasks()) == 6
    assert len(q0.audit_tasks()) == 1
    total = len(q0.all_tasks())
    assert total == (len(reg) + len(wt) + 12 + 10 + 8 + 12 + 9 + 6 + 1)
    # Deterministic census (no RNG): repeated enumeration identical.
    assert q0.all_tasks() == q0.all_tasks()
    assert len(q0.battery_checksum()) == 64


def test_fitted_params_zero():
    assert q0.fitted_param_count() == 0
    assert q0.is_no_hidden_tuning_ok() is True
    assert q0.is_no_dynamics_ok() is True


def test_inventory_no_q_flow():
    inv = q0.inventory_report()
    assert inv["n"] == len(q0.TRANSITION_INVENTORY)
    assert all(r["resolvable"] for r in inv["rows"])
    assert inv["q_flow_maps"] == []
    assert inv["earned_q_updater_without_event"] is False


def test_frozen_theorem_paths():
    thm = q0.frozen_theorem_report()
    assert thm["all_clean"] is True
    assert thm["runtime_q_same"] is True
    assert "Q_{t+dt} = Q_t" in thm["theorem"]


def test_trigger_audit_condition():
    trg = q0.trigger_audit_report()
    assert trg["trigger0_verdict"] == "TRIGGER0-CONDITION"
    assert trg["condition_holds"] is True
    assert trg["implications"] == 0
    assert trg["qdyn_constructs_firing"] is False


def test_evolve_fixed_G_unitary():
    import networkx as nx

    g = nx.path_graph(4)
    order = sorted(g.nodes())
    psi0 = np.full(4, 1.0 / math.sqrt(4), dtype=np.complex128)
    traj = q0.evolve_fixed_G(psi0, g, order, 1.0)
    assert traj["psi"].shape == (21, 4)
    assert float(np.abs(traj["norms"] - 1.0).max()) < 1e-9
    rows = q0.ladder_rows(q0.evolve_fixed_G(psi0, g, order, q0.T_MAX))
    assert set(rows.keys()) == set(float(T) for T in q0.T_LADDER)


def test_wait_record_smoke():
    rec = q0.wait_record("ring-8", "uniform", 0, "")
    assert rec["eligible"] is True
    assert len(rec["rungs"]) == len(q0.T_LADDER)
    assert all(r["q_same"] for r in rec["rungs"])
    assert all(r["pred_ok"] and r["roundtrip_ok"] for r in rec["rungs"])
    assert all(r["cover_ok"] for r in rec["rungs"])
    assert rec["norm_drift"] < 1e-9
    assert rec["semi_err"] < 1e-9
    # Rival exhibit inequivalent for T > 0 by construction.
    for r in rec["rungs"]:
        if r["T"] > 0:
            assert r["rival_differs"] is True


def test_sym_record_smoke():
    rec = q0.sym_record("ring-8", "uniform", 0)
    assert rec["rel_exact"] is True
    assert rec["swap_equiv"] is True
    assert rec["orbit_not_dynamics"] is True


def test_loc_record_smoke():
    rec = q0.loc_record("ring-8", "uniform", 0)
    assert q0.is_locality_qdyn_ok(rec) is True


def test_hid_record_smoke():
    rec = q0.hid_record("j2-L4", "P:sign", 0)
    assert len(rec["branches"]) == 2
    assert all(b["q_fixed"] for b in rec["branches"])


def test_src_record_smoke():
    rec = q0.src_record("VPLUS", "point", "near")
    assert rec["applicable"] is True
    assert rec["q_fixed"] is True


def test_multi_seq_smoke():
    rec = q0.multi_record_seq("handbuilt-chain", "uniform")
    assert rec["n_entries"] > 0
    assert rec["keys_same"] is True


def test_stoch_record_smoke():
    rec = q0.stoch_record("triangle", "bonding", 0)
    assert rec["both_valid"] is True
    assert rec["distribution_assumed"] is False


def test_audit_record_smoke():
    rec = q0.audit_record()
    assert rec["fitted_params"] == 0
    assert rec["no_tuning"] is True
    assert rec["no_dynamics"] is True
    assert rec["inventory"]["earned_q_updater_without_event"] is False


def test_q_equal_boolean():
    qa = {"cover": [[0], [1]], "d": complex(1.0, 2.0)}
    qb = {"cover": [[0], [1]], "d": complex(1.0, 2.0)}
    qc = {"cover": [[0], [1]], "d": complex(1.0, 2.5)}
    assert q0.is_q_equal(qa, qb) is True
    assert q0.is_q_equal(qa, qc) is False
    assert q0.is_q_equal({}, qa) is False


def test_task_kinds():
    kinds = {t[0] for t in q0.all_tasks()}
    assert kinds == {"reg", "wait", "sym", "loc", "hid", "src",
                     "multi", "stoch", "audit"}
