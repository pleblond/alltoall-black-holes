"""BG-RESP-0 analyzer: evaluate the frozen verdict ladder (read-only).

Reads data/bgresp/*.json, evaluates the 10 CHECKS per BGRESP0-PREREG,
writes data/bgresp/verdict.json, prints a summary. No re-runs, no fitting,
no bar adjustments.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import bgresp as bg  # noqa: E402


def load(outdir: str, name: str) -> dict:
    with open(os.path.join(outdir, name + ".json")) as f:
        return json.load(f)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="data/bgresp")
    ap.add_argument("--write", default="data/bgresp/verdict.json")
    args = ap.parse_args(argv)
    outdir = args.outdir
    checks = {}
    detail = {}

    # decomp: L4 exact split on all vacua x kinds.
    r = load(outdir, "decomp_L4")["payload"]
    checks["decomp"] = bool(r["ok"])
    detail["decomp"] = {"n_rows": len(r["rows"])}

    # zero_theorem: chi_ZERO = 0, chi_nonzero != 0 (all L) + lin slopes.
    zt = []
    for L in (4, 8, 28):
        zt.append(bool(load(outdir, f"chi_L{L}_ZERO")["payload"]["chi_zero_ok"]))
        for vac in bg.NONZERO_VACUUMS:
            zt.append(bool(load(outdir, f"chi_L{L}_{vac}")["payload"]["chi_nonzero_ok"]))
    for vac in bg.VACUUMS:
        zt.append(bool(load(outdir, f"energy_{vac}")["payload"]["ok"] is not None))
    for vac in bg.VACUUMS:
        zt.append(bool(load(outdir, f"lin_{vac}")["payload"]["ok"]))
    checks["zero_theorem"] = bool(all(zt))
    detail["zero_theorem"] = {"n_legs": len(zt)}

    # phase_null: global-phase null on all nonzero vacua x L.
    pn = [bool(load(outdir, f"chi_L{L}_{vac}")["payload"]["phase_null_ok"])
          for L in (4, 8, 28) for vac in bg.NONZERO_VACUUMS]
    checks["phase_null"] = bool(all(pn))
    detail["phase_null"] = {"n_legs": len(pn)}

    # amplitude: amplitude direction visible on all nonzero vacua x L.
    am = [bool(load(outdir, f"chi_L{L}_{vac}")["payload"]["amp_visible_ok"])
          for L in (4, 8, 28) for vac in bg.NONZERO_VACUUMS]
    checks["amplitude"] = bool(all(am))
    detail["amplitude"] = {"n_legs": len(am)}

    # scaling: amplitude scaling + fractional collapse (L4 + L28).
    sc = []
    for L in (4, 28):
        for vac in bg.NONZERO_VACUUMS:
            rr = load(outdir, f"scaling_L{L}_{vac}")["payload"]
            sc.append(bool(rr["rows_ok"] and rr["frac_ok"]))
    checks["scaling"] = bool(all(sc))
    detail["scaling"] = {"n_legs": len(sc)}

    # same_carrier: L4 static + L28 time-domain + kernel legs.
    mc = [bool(load(outdir, "samecarrier_L4")["payload"]["ok"])]
    for kind in bg.CENSUS_KINDS:
        mc.append(bool(load(outdir, f"evol_{kind}")["payload"]["same_carrier_ok"]))
    for vac in bg.NONZERO_VACUUMS:
        rr = load(outdir, f"kernel_{vac}")["payload"]
        mc.append(bool(rr["crosscheck_ok"] and rr["krylov_ok"]))
    checks["same_carrier"] = bool(all(mc))
    detail["same_carrier"] = {"n_legs": len(mc)}

    # bipartite_bnull: L4 + L28.
    bb = [bool(load(outdir, "bnull_L4")["payload"]["ok"]),
          bool(load(outdir, "bnull_L28")["payload"]["ok"])]
    checks["bipartite_bnull"] = bool(all(bb))

    # energy: anatomy (all vacua) + hidden null (L4 + L28).
    en = [bool(load(outdir, f"energy_{vac}")["payload"]["ok"]) for vac in bg.VACUUMS]
    en.append(bool(load(outdir, "hiddennull_L4")["payload"]["ok"]))
    en.append(bool(load(outdir, "hiddennull_L28")["payload"]["ok"]))
    checks["energy"] = bool(all(en))
    detail["energy"] = {"n_legs": len(en)}

    # witness: FIELD-0 I = 0 on all vacua.
    wi = [bool(load(outdir, f"witness_{vac}")["payload"]["ok"]) for vac in bg.VACUUMS]
    checks["witness"] = bool(all(wi))

    # fingerprint: distances separate on all L + minimal size filed.
    fp = [bool(load(outdir, f"fingerprint_L{L}")["payload"]["dist_ok"]) for L in (4, 8, 28)]
    checks["fingerprint"] = bool(all(fp))
    detail["fingerprint"] = {
        L: load(outdir, f"fingerprint_L{L}")["payload"]["minimal"] for L in (4, 8, 28)}

    verdict = bg.campaign_verdict(checks)
    out = {"headline": verdict["headline"], "checks": verdict["checks"], "detail": detail,
           "descriptive": {
               "pairdiff": {f"L{L}": {f"{a}-{b}":
                   load(outdir, f"pairdiff_L{L}_{a}_{b}")["payload"]
                   for a, b in (("VPLUS", "VPI"), ("VPLUS", "VMINUS"), ("VPI", "VMINUS"))}
                   for L in (4, 8, 28)},
               "anatomy_cov": {f"L{L}_{v}":
                   load(outdir, f"anatomy_L{L}_{v}")["payload"]["cov_ok"]
                   for L in (4, 28) for v in bg.NONZERO_VACUUMS},
               "size": {f"L{L}": load(outdir, f"size_L{L}")["payload"]["norms"]
                        for L in (6, 12)},
           }}
    with open(args.write, "w") as f:
        json.dump(out, f)
    print(verdict["headline"])
    for k in bg.CHECKS:
        print(f"  {k}: {'GREEN' if verdict['checks'][k] else 'RED'}")
    print(f"wrote {args.write}")
    return 0 if verdict["headline"] == "BGRESP0-COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
