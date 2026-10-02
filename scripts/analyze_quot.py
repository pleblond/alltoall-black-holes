"""QUOT-0 stage checker + verdict merger (frozen bars from the prereg).

Subcommands:
  stage  check quot_alg.json + quot_comm_*.json + quot_anatomy_*.json
         against ALL frozen non-replay bars -> quot_stage.json.
  merge  combine quot_stage.json + quot_replay.json (from
         analyze_quot_replay.py) into data/quot_verdict.json + headline.

No thresholds are set here beyond the prereg: every bar value below is
quoted from the QUOT-0 PREREG (docs/DEFERRED.md).
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

BANKED_TD_R2 = 0.1667  # OBS-0R diffusion R=2 contrast (pattern value)
BANKED_POT_R2 = 0.1407  # OBS-0R POT R=2 contrast (pattern value)
VALUE_TOL = 0.30  # banked-value agreement (DERIVED support, descriptive-grade)


def _load(d, name):
    with open(os.path.join(d, name)) as f:
        return json.load(f)


def cmd_stage(args):
    d = args.datadir
    alg = _load(d, "quot_alg.json")
    comm = {}
    for t in ("wave-sym", "wave-anti", "wave-sheet",
              "diff-sym", "diff-anti", "diff-sheet",
              "wave-proj", "diff-proj"):
        comm[t] = _load(d, f"quot_comm_{t}.json")
    anat = {}
    for k in ("diff-pattern", "pot-pattern"):
        for oi in range(4):
            anat[f"{k}_o{oi}"] = _load(d, f"quot_anatomy_{k}_o{oi}.json")
    anat["lrw_o0"] = _load(d, "quot_anatomy_lrw_o0.json")

    checks = {}
    # Q-ALG.
    checks["alg_comm"] = alg["comm_fro"] < 1e-9
    checks["alg_dead"] = alg["anti_dead"] < 1e-9
    checks["alg_inter"] = alg["intertwining"] < 1e-9
    checks["alg_Uinter"] = alg["U_inter_max"] < 1e-9
    checks["alg_frozen"] = alg["frozen_max"] < 1e-9
    checks["alg_decomp"] = alg["decomp"] < 1e-9
    checks["alg_nzero"] = (alg["n_zero"] == 838
                           and alg["nodal"] == 54
                           and alg["n_zero"] == 784 + alg["nodal"])
    checks["Q_ALG"] = all(checks[k] for k in
                          ("alg_comm", "alg_dead", "alg_inter", "alg_Uinter",
                           "alg_frozen", "alg_decomp", "alg_nzero"))

    # Q-COMM wave + diffusion.
    for ch in ("wave", "diff"):
        sym, anti, sheet = comm[f"{ch}-sym"], comm[f"{ch}-anti"], comm[f"{ch}-sheet"]
        checks[f"{ch}_sym_arr"] = all(
            sym["cap"][str(r)]["arrival"] is not None
            and sym["cap"][str(r)]["C"] > 0.001 for r in (2, 4, 6))
        checks[f"{ch}_anti_zero"] = all(
            anti["cap"][str(r)]["C"] < 1e-9 for r in range(2, 15))
        checks[f"{ch}_ratio"] = all(
            (anti["cap"][str(r)]["C"] / sym["cap"][str(r)]["C"] < 1e-6)
            for r in (2, 4, 6))
        checks[f"{ch}_sheet_local"] = abs(sheet["cap"]["0"]["C"] - 1.0) < 1e-9
        checks[f"{ch}_sheet_remote"] = all(
            sheet["cap"][str(r)]["C"] < 1e-9 for r in range(1, 15))
    checks["Q_COMM"] = all(checks[k] for k in checks if "_sym_arr" in k or "_anti_zero" in k
                           or "_ratio" in k or "_sheet_" in k)

    # Q-SECTOR wave exactness + diffusion operator.
    checks["wave_proj_exact"] = comm["wave-proj"]["remote_max_abs"] < 1e-9
    checks["wave_ratio2"] = comm["wave-proj"]["ratio_maxdev"] < 1e-9
    checks["diff_proj_exact"] = comm["diff-proj"]["remote_max_abs"] < 1e-9
    checks["diff_ratio2"] = comm["diff-proj"]["ratio_maxdev"] < 1e-9
    checks["lrw_anti"] = anat["lrw_o0"]["anti_err"] < 1e-12
    checks["lrw_sym"] = anat["lrw_o0"]["sym_err"] < 1e-12

    # Diffusion pattern + ablation (all 4 origins must agree).
    for oi in range(4):
        m = anat[f"diff-pattern_o{oi}"]["mixed"]
        s = anat[f"diff-pattern_o{oi}"]["sym"]
        checks[f"diff_pat_o{oi}"] = (
            (m["1"] is not None and m["1"] < 0.01)
            and (m["2"] is not None and m["2"] > 0.05)
            and (m["3"] is not None and m["3"] < 0.01))
        checks[f"diff_abl_o{oi}"] = (s["2"] is not None and s["2"] < 0.01)
        v = anat[f"diff-pattern_o{oi}"]["mixed"]["2"]
        checks[f"diff_val_o{oi}"] = (v is not None
                                     and abs(v - BANKED_TD_R2) / BANKED_TD_R2 < VALUE_TOL)
    checks["Q_DIFF"] = all(checks[f"diff_pat_o{oi}"] and checks[f"diff_abl_o{oi}"]
                           for oi in range(4))
    checks["Q_DIFF_VAL"] = all(checks[f"diff_val_o{oi}"] for oi in range(4))

    # POT pattern + ablation + exact support.
    for oi in range(4):
        a = anat[f"pot-pattern_o{oi}"]
        m, s = a["mixed"], a["sym"]
        checks[f"pot_pat_o{oi}"] = (
            (m["1"] is not None and m["1"] < 0.01)
            and (m["2"] is not None and m["2"] > 0.05)
            and (m["3"] is not None and m["3"] < 0.01)
            and (a["mixed_meso"] is not None and a["mixed_meso"] < 0.01))
        checks[f"pot_abl_o{oi}"] = all(
            (s[r] is not None and s[r] < 0.01) for r in ("1", "2", "3"))
        checks[f"pot_sup_o{oi}"] = bool(a["anti_support_ok"]) and a["anti_pure"] < 1e-8
        checks[f"pot_far_o{oi}"] = a["far_rel"] < 0.05
        v = a["mixed"]["2"]
        checks[f"pot_val_o{oi}"] = (v is not None
                                    and abs(v - BANKED_POT_R2) / BANKED_POT_R2 < VALUE_TOL)
    checks["Q_POT"] = all(checks[f"pot_pat_o{oi}"] and checks[f"pot_abl_o{oi}"]
                          and checks[f"pot_sup_o{oi}"] and checks[f"pot_far_o{oi}"]
                          for oi in range(4))
    checks["Q_POT_VAL"] = all(checks[f"pot_val_o{oi}"] for oi in range(4))
    checks["Q_SECTOR"] = bool(checks["wave_proj_exact"] and checks["wave_ratio2"]
                              and checks["diff_proj_exact"] and checks["diff_ratio2"]
                              and checks["lrw_anti"] and checks["lrw_sym"]
                              and checks["Q_DIFF"] and checks["Q_POT"])
    # Raw remote maxima for the ACCIDENTAL triggers (1e-6 rung, prereg).
    acc_raw = {}
    for ch in ("wave", "diff"):
        anti, sheet = comm[f"{ch}-anti"], comm[f"{ch}-sheet"]
        acc_raw[f"{ch}_anti_remote_max"] = max(
            anti["cap"][str(r)]["C"] for r in range(2, 15))
        acc_raw[f"{ch}_sheet_remote_max"] = max(
            sheet["cap"][str(r)]["C"] for r in range(1, 15))
    out = {"checks": checks, "alg": alg, "acc_raw": acc_raw,
           "comm_tasks": sorted(comm), "anatomy_shards": sorted(anat)}
    with open(args.out, "w") as f:
        json.dump(out, f)
    n = sum(1 for v in checks.values() if v)
    print(f"stage: {n}/{len(checks)} checks pass", flush=True)
    for k in sorted(checks):
        if not checks[k]:
            print(f"  FAIL {k}", flush=True)


def cmd_merge(args):
    with open(args.stage) as f:
        stage = json.load(f)
    with open(args.replay) as f:
        replay = json.load(f)
    c = dict(stage["checks"])
    b = replay["bars"]
    c["replay_mixed"] = bool(b["mixed_quotient_clauses"])
    c["replay_p_plus"] = bool(b["p_plus_quotient_clauses"] and b["p_plus_drift_ok"])
    c["replay_p_minus"] = bool(b["p_minus_nogeometry"])
    c["replay_c0"] = bool(b["c0_mixed"])
    c["replay_c1"] = bool(b["c1_mixed"])
    c["replay_pert_flip"] = bool(b.get("pert_flip", False))
    c["replay_ctrl"] = bool(b.get("ctrl_two_worlds", False))
    c["Q_REPLAY"] = bool(c["replay_mixed"] and c["replay_p_plus"]
                         and c["replay_p_minus"] and c["replay_c0"] and c["replay_c1"])

    accidental = bool(
        (not c["replay_mixed"])
        or bool(b["p_minus_metric"])
        or bool(b.get("ctrl_qclauses", False))
        or any(v > 1e-6 for v in stage["acc_raw"].values()))
    sector = bool(c["Q_ALG"])
    operational = bool(sector and c["Q_COMM"] and c["Q_REPLAY"]
                       and c["wave_proj_exact"] and c["diff_proj_exact"])
    derived = bool(operational and c["Q_SECTOR"] and c["replay_pert_flip"]
                   and c["replay_ctrl"] and c["Q_DIFF_VAL"] and c["Q_POT_VAL"])
    if accidental:
        headline = "QUOT0-ACCIDENTAL"
    elif derived:
        headline = "QUOT0-DERIVED"
    elif operational:
        headline = "QUOT0-OPERATIONAL"
    elif sector:
        headline = "QUOT0-SECTOR"
    else:
        headline = "QUOT0-PARTIAL"
    verdict = {"headline": headline, "checks": c, "replay_bars": b,
               "rungs": {"SECTOR": sector, "OPERATIONAL": operational,
                         "DERIVED": derived, "ACCIDENTAL": accidental}}
    with open(args.out, "w") as f:
        json.dump(verdict, f)
    print(f"headline: {headline}", flush=True)
    print(f"rungs: {verdict['rungs']}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("stage")
    p.add_argument("--datadir", required=True)
    p.add_argument("--out", required=True)
    p = sub.add_parser("merge")
    p.add_argument("--stage", required=True)
    p.add_argument("--replay", required=True)
    p.add_argument("--out", required=True)
    args = ap.parse_args()
    {"stage": cmd_stage, "merge": cmd_merge}[args.cmd](args)


if __name__ == "__main__":
    main()
