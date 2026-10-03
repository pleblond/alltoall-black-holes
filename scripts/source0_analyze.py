"""SOURCE-0 analyzer: evaluate the frozen verdict ladder (read-only).

Reads data/source0/*.json, evaluates the 10 CHECKS per SOURCE0-PREREG,
writes data/source0/verdict.json, prints a summary. No re-runs, no fitting,
no bar adjustments.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from bh_graph import source0 as s0  # noqa: E402
from source0_campaign import all_tasks  # noqa: E402


def load(outdir: str, name: str) -> dict:
    with open(os.path.join(outdir, name + ".json")) as f:
        return json.load(f)


FROZEN_EDGES = {4: (32, 128), 8: (128, 512), 28: (1568, 6272)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="data/source0")
    ap.add_argument("--write", default="data/source0/verdict.json")
    args = ap.parse_args(argv)
    outdir = args.outdir
    checks: dict = {}
    detail: dict = {}
    missing = []

    records = {}
    for _name, _params, record in all_tasks():
        try:
            records[record] = load(outdir, record)["payload"]
        except (OSError, ValueError, KeyError):
            missing.append(record)
    detail["missing"] = missing
    detail["n_records"] = len(records)

    def P(name):
        return records[name]

    # kernel: gated K1 (POT/VPLUS) + K2 on all pinned evolutions.
    if not missing:
        k1_legs = []
        for rec, pr in ((r, pr) for _n, pr, r in all_tasks()):
            if rec.startswith("steady_") and P(rec)["k1"].get("gated"):
                k1_legs.append(bool(P(rec)["k1"]["ok"]))
        k2_legs = []
        for _n, _pr, rec in all_tasks():
            if rec.startswith(("steady_", "turnon_", "pair_")):
                k2_legs.append(bool(P(rec)["k2"]["ok"]))
        checks["kernel"] = bool(k1_legs and all(k1_legs)
                                and k2_legs and all(k2_legs))
        detail["kernel"] = {"k1_gated": len(k1_legs),
                            "k1_ok": sum(k1_legs), "k2_legs": len(k2_legs),
                            "k2_ok": sum(k2_legs)}
    else:
        checks["kernel"] = False

    # stationary: jump-ok on invertible legs, bounded-ok on resonant legs.
    if not missing:
        legs = []
        split = {"jump": 0, "bounded": 0}
        for _n, pr, rec in all_tasks():
            if not rec.startswith("steady_"):
                continue
            r = P(rec)
            if r["expected_stationary"]:
                legs.append(bool(r["jump"]["ok"]))
                split["jump"] += 1
            else:
                legs.append(bool(r["bounded"]["ok"]))
                split["bounded"] += 1
        checks["stationary"] = bool(legs and all(legs))
        detail["stationary"] = {"legs": len(legs), "ok": sum(legs),
                                "split": split}
    else:
        checks["stationary"] = False

    # range_law: chi-consistency everywhere + radial r2 on gapped POT legs.
    if not missing:
        chi = []
        law = []
        for _n, pr, rec in all_tasks():
            if not rec.startswith("steady_"):
                continue
            r = P(rec)
            chi.append(bool(r["profiles"]["chi_ok"]))
            if str(pr.get("fam", "")).startswith("POT"):
                law.append(bool(r["profiles"]["law_ok"]))
        checks["range_law"] = bool(chi and all(chi) and law and all(law))
        detail["range_law"] = {"chi_legs": len(chi), "chi_ok": sum(chi),
                               "law_legs": len(law), "law_ok": sum(law)}
    else:
        checks["range_law"] = False

    # allpath: AP_diff + 1D-reject on both wall-cut cases.
    if not missing:
        legs = []
        for rec in ("allpath_VPLUS_POT1.0", "allpath_VPLUS_AMP"):
            r = P(rec)
            legs.append(bool(r["ap_ok"] and r["reject_ok"]))
        checks["allpath"] = bool(all(legs))
        detail["allpath"] = {"legs": legs}
    else:
        checks["allpath"] = False

    # sign_phase: sign/rotation/flip + POT-phase + lin slopes.
    if not missing:
        legs = []
        for vac in ("VPLUS", "VMINUS"):
            r = P(f"signphase_{vac}")
            legs.append(bool(r["sign_ok"] and r["rotation_ok"]
                             and r["cross_flip_ok"] and r["dd_same_ok"]))
        legs.append(bool(P("signphase_VPLUS")["pot_phase"]["ok"]))
        for L in (28, 4):
            r = P(f"lin_L{L}")
            legs.append(bool(r["d"]["ok"] and r["cross"]["ok"]))
        checks["sign_phase"] = bool(all(legs))
        detail["sign_phase"] = {"legs": legs}
    else:
        checks["sign_phase"] = False

    # background: POT carrier sha + E=0 |sha| + banked tables (= present).
    if not missing:
        pot_groups = {}
        for _n, pr, rec in all_tasks():
            if not rec.startswith("steady_"):
                continue
            fam = str(pr.get("fam", ""))
            if fam.startswith("POT"):
                pot_groups.setdefault((fam, str(pr["L"])), []).append(
                    P(rec)["sha"])
        pot_ok = all(len(set(v)) == 1 for v in pot_groups.values())
        e0_ok = True
        for fam in ("AMP", "PHASE", "COMPLEX"):
            shas = [P(f"steady_L28_{vac}_{fam}")["sha_abs"]
                    for vac in ("VMINUS", "VSTAG", "CIRCH", "ZERO")]
            e0_ok = e0_ok and (len(set(shas)) == 1)
        checks["background"] = bool(pot_ok and e0_ok)
        detail["background"] = {
            "pot_groups": {str(k): len(set(v)) for k, v in pot_groups.items()},
            "e0_ok": e0_ok}
    else:
        checks["background"] = False

    # switch: six L28 fronts + causality.
    if not missing:
        legs = []
        for rec in ("turnon_L28_VPLUS_AMP", "turnon_L28_VPLUS_POT1.0",
                    "turnon_L28_VPI_AMP", "turnon_L28_VMINUS_AMP",
                    "release_VPLUS_POT1.0", "release_VPLUS_AMP",
                    "release_VMINUS_AMP"):
            r = P(rec)
            legs.append(bool(r["front"]["ok"]
                             and float(r["causality"]) < s0.BARS["causality"]))
        checks["switch"] = bool(all(legs))
        detail["switch"] = {"legs": legs}
    else:
        checks["switch"] = False

    # superposition: field + cross anatomy on all pair cases.
    if not missing:
        legs = []
        for rec in ("pair_L28_VPLUS_AMP", "pair_L28_VMINUS_POT",
                    "pair_L4_VPLUS_AMP"):
            r = P(rec)
            legs.append(bool(r["field_ok"] and r["cross_ok"]))
        checks["superposition"] = bool(all(legs))
        detail["superposition"] = {"legs": legs}
    else:
        checks["superposition"] = False

    # quotient: five sym legs + FS battery.
    if not missing:
        sy = P("quotient_sym")["sym"]
        fs = P("quotient_fs")["fs"]
        legs = [bool(sy["u1_ok"]), bool(sy["relabel_ok"]), bool(sy["aut_ok"]),
                bool(sy["aut_distinct"]), bool(sy["scale_ok"]),
                bool(fs["u1_zero"]), bool(fs["others_positive"])]
        checks["quotient"] = bool(all(legs))
        detail["quotient"] = {"legs": legs}
    else:
        checks["quotient"] = False

    # controls: POT-1 + kernel + witness + covariance + frozen graph/params.
    if not missing:
        legs = [bool(P("controls_pot1_path")["ok"]),
                bool(P("controls_pot1_j2")["ok"]),
                bool(P("controls_resp_kernel")["ok"]),
                bool(P("controls_field0_witness")["ok"]),
                bool(P("quotient_sym")["sym"]["u1_ok"])]
        edges_ok = True
        for _n, pr, rec in all_tasks():
            r = P(rec)
            if "edges" not in r:
                continue
            L = int(pr.get("L", 28)) if rec != "quotient_sym" else 8
            if rec.startswith("quotient"):
                L = 8
            want = FROZEN_EDGES[L]
            got = (int(r["edges"]["n"]), int(r["edges"]["edges"]))
            edges_ok = edges_ok and (got == want)
        cut = P("allpath_VPLUS_AMP")
        edges_ok = edges_ok and int(cut["cut_edges"]) > 0
        legs.append(edges_ok)
        params_ok = True
        for _n, pr, rec in all_tasks():
            r = P(rec)
            veh = r.get("vehicle")
            if veh is None:
                continue
            if veh["name"] == "jump":
                params_ok = params_ok and (
                    veh["DT"] == s0.DT_HARM and veh["T"] == s0.T_JUMP)
            elif veh["name"] == "static":
                params_ok = params_ok and (
                    veh["DT"] == s0.DT_STATIC and veh["T"] == s0.T_GROW)
        for rec in ("turnon_L28_VPLUS_AMP", "turnon_L28_VPLUS_POT1.0",
                    "turnon_L28_VPI_AMP", "turnon_L28_VMINUS_AMP"):
            r = P(rec)
            fam = rec.split("_")[-1]
            if fam.startswith("POT"):
                params_ok = params_ok and (
                    r["DT"] == s0.DT_HARM and r["T"] == s0.T_ON_POT)
            elif rec == "turnon_L28_VMINUS_AMP":
                params_ok = params_ok and (
                    r["DT"] == s0.DT_STATIC and r["T"] == s0.T_GROW)
            else:
                params_ok = params_ok and (
                    r["DT"] == s0.DT_HARM and r["T"] == s0.T_ON_MAINT)
        legs.append(params_ok)
        checks["controls"] = bool(all(legs))
        detail["controls"] = {"legs": legs}
    else:
        checks["controls"] = False

    verdict = s0.campaign_verdict({**checks, "missing": bool(missing)})
    out = {"headline": verdict["headline"], "checks": verdict["checks"],
           "detail": detail,
           "ranges": {} if missing else {
               rec: P(rec)["profiles"]["range"]
               for _n, _pr, rec in all_tasks() if rec.startswith("steady_")},
           "laws": {} if missing else {
               rec: P(rec)["profiles"]["law"]
               for _n, _pr, rec in all_tasks() if rec.startswith("steady_")}}
    with open(args.write, "w") as f:
        json.dump(out, f)
    print(verdict["headline"])
    for k in s0.CHECKS:
        print(f"  {k}: {'GREEN' if verdict['checks'][k] else 'RED'}")
    print(f"wrote {args.write}")
    return 0 if verdict["headline"] == "SOURCE0-GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
