"""SPLIT-0 analyzer (frozen gates, pre-data).

Reads data/split0_ledger.json, applies the frozen gate battery, writes
data/split0_verdict.json. NO fitting after data: counts in, rung out.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import split0 as s0


def _load():
    path = os.path.join(os.path.dirname(__file__), "..",
                        "data", "split0_ledger.json")
    with open(path) as fh:
        return json.load(fh)


def main():
    led = _load()
    cells = led["cells"]
    forwards = led["forwards"]
    j2rows = led["j2"]
    gates = []

    def _gate(name, ok, detail):
        gates.append({"gate": name, "ok": bool(ok), "detail": str(detail)})

    # H-A: exact graph census + dimension formulas on every cell.
    bad_a = [c["cell"] for c in cells
             if not (c["cover_ok"] and c["dim_ok"])]
    _gate("H-A-graph", not bad_a,
          f"n={len(cells)} bad={len(bad_a)}")

    # H-B: fiber roundtrip M + xi <-> X (all covers x probe d).
    rt_n = sum(c["roundtrip_n"] for c in cells)
    rt_bad = sum(c["roundtrip_bad"] for c in cells)
    _gate("H-B-roundtrip", rt_bad == 0,
          f"n={rt_n} bad={rt_bad}")

    # H-C: minimality (both ablation legs where applicable).
    bad_c = [c["cell"] for c in cells if not c["minimal"]]
    n_dc = sum(1 for c in cells if c["drop_cover_applicable"])
    _gate("H-C-minimal", not bad_c,
          f"n={len(cells)} bad={len(bad_c)} drop_cover_cells={n_dc}")

    # H-D: covariance (cover/xi/swap/phase + J2 sheet).
    bad_d = [c["cell"] for c in cells
             if not (c["cov_cover"] and c["cov_xi"] and c["cov_swap"]
                     and c["cov_phase"])]
    bad_sheet = [r["background"] for r in j2rows
                 if not r["sheet_covariant"]]
    _gate("H-D-covariance", not bad_d and not bad_sheet,
          f"cells={len(cells)} bad={len(bad_d)} sheet_bad={bad_sheet}")

    # M-E: dimension census (d_cont in {1,2}; iso bounds hold by H-A).
    dmax = max(c["dims"]["d_cont_full"] for c in cells)
    dvals = sorted({c["dims"]["d_cont_full"] for c in cells})
    _gate("M-E-dims", set(dvals) <= {1, 2},
          f"d_cont_values={dvals} max={dmax}")

    # M-F: locality everywhere; applicability filed.
    bad_f = [c["cell"] for c in cells if not c["local"]]
    bad_fj = [r["background"] for r in j2rows if not r["local"]]
    n_far = sum(1 for c in cells
                if c["applicability"]["far_field"]
                or c["applicability"]["far_edge"])
    n_far_j2 = sum(1 for r in j2rows
                   if r["applicability"]["far_field"])
    _gate("M-F-local", not bad_f and not bad_fj,
          f"cells={len(cells)} bad={len(bad_f)} "
          f"nontrivial_tiny={n_far} nontrivial_j2={n_far_j2}/3")

    # M-G: hidden retained (D_merged = 0, local varies) everywhere.
    bad_g = [c["cell"] for c in cells
             if not (c["hidden"] and c["D_merged"] == 0.0
                     and c["locally_varies"])]
    bad_gj = [r["background"] for r in j2rows
              if not (r["hidden"] and r["D_merged"] == 0.0
                      and r["locally_varies"])]
    _gate("M-G-hidden", not bad_g and not bad_gj,
          f"cells={len(cells)} bad={len(bad_g)} j2_bad={bad_gj}")

    # M-H: deterministic core census (load-bearing: halves-det iff d = 0).
    det_cells = [c["cell"] for c in cells
                 if c["det"]["halves_deterministic"]]
    det_nonzero = [c["cell"] for c in cells
                   if c["det"]["halves_deterministic"] and c["d"] != 0]
    full_det = [c["cell"] for c in cells
                if c["det"]["full_deterministic"]]
    n_need = sum(1 for c in cells
                 if c["det"]["n_phys_halves"] > 1
                 or c["dims"]["d_cont_full"] > 0)
    _gate("M-H-detcore", not det_nonzero and not full_det,
          f"halves_det={len(det_cells)} (d0_only={not det_nonzero}) "
          f"full_det={len(full_det)} need_residual={n_need}")

    # M-C: forward bridge + halves reverse support.
    bad_bridge = [r["cell"] for r in forwards
                  if not (r["recorded_cover_found"]
                          and r["restores_graph"]
                          and r["graph_reverse"])]
    bad_equiv = [r["cell"] for r in forwards
                 if not r["full_iff_halves"]]
    n_rev = sum(1 for r in forwards if r["verdict"] == "reversible")
    n_go = sum(1 for r in forwards if r["verdict"] == "graph-only")
    n_ow = sum(1 for r in forwards if r["verdict"] == "one-way")
    _gate("M-C-reverse", not bad_bridge and not bad_equiv,
          f"n={len(forwards)} rev={n_rev} graph_only={n_go} one_way={n_ow}")

    # M-J: no-measure control + firewall.
    bad_j = [c["cell"] for c in cells if not c["nomeasure"]]
    fw = bool(led["firewall"] and led["firewall"][0]["no_hidden_tuning"])
    _gate("M-J-nomeasure", not bad_j and fw,
          f"cells={len(cells)} bad={len(bad_j)} firewall={fw}")

    hard_ok = all(g["ok"] for g in gates)
    census = {"gates": {"graph_census": gates[0]["ok"],
                        "fiber_relation": gates[1]["ok"] and gates[8]["ok"],
                        "roundtrip": gates[1]["ok"],
                        "minimality": gates[2]["ok"],
                        "covariance": gates[3]["ok"],
                        "locality": gates[5]["ok"],
                        "nomeasure": gates[9]["ok"]},
              "n_cells": len(cells),
              "n_halves_deterministic": len(det_cells),
              "n_need_residual": n_need,
              "d_cont_max": dmax}
    verdict = s0.verdict_from_census(census)
    out = {"gates": gates, "hard_ok": bool(hard_ok),
           "census": {k: v for k, v in census.items() if k != "gates"},
           "verdict": verdict["verdict"],
           "interpretation": verdict["reason"],
           "provenance": led.get("provenance", {})}
    path = os.path.join(os.path.dirname(__file__), "..",
                        "data", "split0_verdict.json")
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"SPLIT0-ANALYZE hard_ok={hard_ok} "
          f"verdict={verdict['verdict']} -> {path}")
    for g in gates:
        print(f"  {g['gate']}: {'PASS' if g['ok'] else 'FAIL'} {g['detail']}")


if __name__ == "__main__":
    main()
