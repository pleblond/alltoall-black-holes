"""MERGE-0 verdict analyzer (FROZEN pre-data; decision tree only).

Reads data/merge0/*.json (event/scan/seq records), evaluates every
preregistered gate, writes verdict.json. No bar/ladder/estimator may
change post-data: failures file as genuine or design-error autopsies.

Ladder (MERGE0-PREREG):
  MERGE0-DETERMINISTIC: selected-edge contraction has a unique covariant
    physical outcome across the headline battery (A), with exact
    structural/norm/energy ledger (B/C/D), quantified information loss
    (H), and verified composition (I); firewall holds (J).
  MERGE0-CLASS: deterministic outcome holds only on specified classes
    (A green, B/C/D/H red on a confined filed class).
  MERGE0-ACCOUNT-DEBT (accounting status, reported alongside): outcome
    deterministic but no existing variable closes the reservoir (E).
  MERGE0-INCOMPLETE: even selected-edge post-state is not unique on the
    physical quotient (any A gate red), or firewall/data incomplete.
"""

from __future__ import annotations

import glob
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import merge0 as m0  # noqa: E402

BAR_FP = m0.BAR_FP
BAR_LEDGER = m0.BAR_LEDGER
BAR_PHYS = m0.BAR_PHYS


def load(outdir: str):
    events, pairs, scans, seqs = [], [], [], []
    for path in sorted(glob.glob(os.path.join(outdir, "event_*.json"))):
        with open(path) as f:
            r = json.load(f)
        if "A" in r and "B" in r:
            pairs.append(r)
            events.append(r["A"])
            events.append(r["B"])
        else:
            events.append(r)
    for path in sorted(glob.glob(os.path.join(outdir, "scan_*.json"))):
        with open(path) as f:
            scans.append(json.load(f))
    for path in sorted(glob.glob(os.path.join(outdir, "seq_*.json"))):
        with open(path) as f:
            seqs.append(json.load(f))
    return events, pairs, scans, seqs


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else "data/merge0"
    events, pairs, scans, seqs = load(outdir)
    gates = []

    def gate(name, ok, detail=""):
        gates.append({"gate": name, "ok": bool(ok), "detail": str(detail)})

    n = len(events)
    gate("count-events", n > 0, f"n={n}")
    gate("count-pairs", len(pairs) > 0, f"n={len(pairs)}")
    gate("count-scans", len(scans) > 0, f"n={len(scans)}")
    gate("count-seqs", len(seqs) > 0, f"n={len(seqs)}")

    # ---- A: unique outcome ----
    bad_det = [e for e in events if not e["det_ok"]]
    bad_rcov = [e for e in events if not e["rcov_ok"]]
    bad_ucov = [e for e in events if not e["ucov_ok"]]
    gate("A-det", not bad_det, f"bad={len(bad_det)}/{n}")
    gate("A-rcov", not bad_rcov, f"bad={len(bad_rcov)}/{n}")
    gate("A-ucov", not bad_ucov, f"bad={len(bad_ucov)}/{n}")
    annih = [e for e in events if e["degen"]["annihilation"]]
    gate("A-degen", all(e["det_ok"] for e in annih),
         f"annihilation_cases={len(annih)}")

    # ---- B: structural ----
    gate("B-dN", all(e["dN"] == -1 for e in events), f"n={n}")
    gate("B-dE", all(e["dE"] == e["dE_formula"] == -(1 + e["common"])
                 for e in events), f"n={n}")
    gate("B-simple", all(e["simple"] and e["simple_direct"] for e in events),
         f"n={n}")
    gate("B-cone", all(e["cone"]["ok"]
                       and e["cone"]["max_changed_dist"] == 1
                       for e in events), f"n={n}")

    # ---- C: norm ----
    gate("C-norm2B", all(abs(e["dQ_is_2B"]) < BAR_LEDGER for e in events),
         f"max={max(abs(e['dQ_is_2B']) for e in events) if events else -1}")
    gate("C-normformula", all(abs(e["dQ_direct"] - e["dQ_formula"]) < 1e-12
                              for e in events), f"n={n}")

    # ---- D: energy ----
    gate("D-energy", all(abs(e["dEpsi_direct"] - e["dEpsi_formula"])
                         < BAR_LEDGER for e in events),
         f"max={max(abs(e['dEpsi_direct'] - e['dEpsi_formula']) for e in events) if events else -1}")
    gate("D-parts", all(abs(e["parts_sum"] - e["dEpsi_direct"]) < BAR_LEDGER
                        for e in events), f"n={n}")
    gate("D-P34", all(abs(e["P3"]) < 1e-12 and abs(e["P4"]) < 1e-12
                      for e in events), f"n={n}")
    gate("D-support", all(e["ledger_support_size"] == 2 + e["n_cross"]
                          for e in events), f"n={n}")

    # ---- H: information loss ----
    def _bits_ok(e):
        d = e["deg_k"]
        return (e["n_covers_directed"] == 3 ** d
                and abs(e["graph_bits"]
                        - math.log2((3 ** d + 1) / 2.0)) < 1e-9
                and e["field_dims_lost"] == 2)

    gate("H-bits", all(_bits_ok(e) for e in events), f"n={n}")
    gate("H-relmode", all(abs(e["rel_mode_err"] - e["rel_mode_formula"])
                          < 1e-12 for e in events), f"n={n}")
    gate("H-paircontrast", any(p["dB"] > BAR_PHYS for p in pairs),
         f"npair={len(pairs)}")
    gate("H-signflip", any(p["sign_flip"] for p in pairs),
         f"nflip={sum(1 for p in pairs if p['sign_flip'])}")

    # ---- I: sequences ----
    gate("I-compose", all(s["composition_ok"] for s in seqs),
         f"n={len(seqs)}")
    gate("I-nostop", all(all(st["status"] == "contracted"
                            for st in s["steps"]) for s in seqs),
         f"n={len(seqs)}")

    # ---- E: missing reservoir ----
    probe_all = m0.probe_closure(events)
    gate("E-all", m0.is_no_closure_ok(probe_all),
         f"closed={probe_all['n_closed']}/{probe_all['n_tuples']}")
    closing = [t for t in probe_all["tuples"] if t["closes"]]
    cvals = sorted({e["common"] for e in events})
    gate("E-cvar", 0 in cvals and max(cvals) > 0, f"c={cvals}")
    # Decoupled structural law (banked remark, not a reservoir): (1,-1,0,0)
    # closes exactly on c=0 records and fails exactly by c elsewhere.
    c0 = [e for e in events if e["common"] == 0]
    cpos = [e for e in events if e["common"] > 0]
    a, b, g_, d_ = m0.DECOUPLED_TUPLE
    dec_c0 = max(abs(m0.linear_residual(e, a, b, g_, d_)) for e in c0) \
        if c0 else float("nan")
    dec_pos = [abs(m0.linear_residual(e, a, b, g_, d_) - e["common"])
               for e in cpos]
    gate("E-decoupled", dec_c0 == 0.0
         and all(v < 1e-12 for v in dec_pos) and len(c0) > 0
         and len(cpos) > 0,
         f"c0max={dec_c0} npos={len(cpos)}")
    vac = [e for e in events if e["ftag"] in m0.VAC_FIELDS]
    hid = [e for e in events if e["ftag"].startswith("H:")
           or e["ftag"].startswith("P:")]
    exc = [e for e in events if e["ftag"].startswith("X:")]
    for tag, subset in (("E-vac", vac), ("E-hidden", hid), ("E-exc", exc)):
        if not subset:
            gate(tag, False, "empty subset")
            continue
        pr = m0.probe_closure(subset, coeffs=m0.FIELD_GRID)
        gate(tag, m0.is_no_closure_ok(pr),
             f"n={len(subset)} closed={pr['n_closed']}")
    gate("E-dxi", all(r["gil"]["dxi_direct"] == -r["gil"]["c"]
                      for r in events), f"n={n}")

    # ---- F: vacuum battery (descriptive presence) ----
    vtab = m0.vacuum_table(events)
    gate("F-vac", all(t in vtab and vtab[t]["n"] > 0
                      for t in ("VPLUS", "VPI", "VMINUS")),
         f"tags={sorted(vtab)}")

    # ---- G: excitations ----
    exc_rows = [e for e in events if e["ftag"].startswith("X:")]
    baseline = {(e["sub"], e["ftag"], tuple(e["edge"])): e
                for e in events if e["ftag"] in m0.VAC_FIELDS}
    # Overlap-edge baselines: completed analyzer-side by the frozen
    # deterministic function (filed; excited records are campaign data).
    derived = 0
    need = {(r["sub"], r["ftag"].split("@")[1], tuple(r["edge"]))
            for r in exc_rows} - set(baseline)
    subs_cache = {}
    for (sn, vac_tag, edge) in sorted(need, key=str):
        if sn not in subs_cache:
            subs_cache[sn] = m0.build_substrate(sn)
        s = subs_cache[sn]
        baseline[(sn, vac_tag, edge)] = m0.event_record(
            s, vac_tag, list(edge))
        derived += 1
    gtab = m0.excitation_table(exc_rows, baseline)
    vis = [r for r in gtab["rows"] if abs(r["dL_vs_vac"]) > BAR_PHYS]
    gate("G-exc", len(gtab["rows"]) > 0,
         f"rows={len(gtab['rows'])} derived_baselines={derived}")
    gate("G-visible", len(vis) > 0, f"visible={len(vis)}")
    gate("G-sectors", len(gtab["sectors"]) > 0,
         f"n={len(gtab['sectors'])}")

    # ---- J: firewall ----
    fw = m0.firewall_summary(scans)
    gate("J-norule", fw["firing_rule_constructed"] is False, "")
    gate("J-census", fw["n_scans"] == len(scans) and len(scans) > 0,
         f"n={len(scans)}")
    gate("J-fav", True, f"favorable={fw['n_with_favorable']} "
                        f"downhill={fw['n_with_downhill']}")

    # ---- Verdict ----
    g = {c["gate"]: c["ok"] for c in gates}
    a_green = all(g[k] for k in ("A-det", "A-rcov", "A-ucov", "A-degen"))
    bcdh_green = all(g[k] for k in ("B-dN", "B-dE", "B-simple", "B-cone",
                                    "C-norm2B", "C-normformula",
                                    "D-energy", "D-parts", "D-P34",
                                    "D-support", "H-bits", "H-relmode",
                                    "H-paircontrast", "H-signflip",
                                    "I-compose", "I-nostop"))
    e_green = all(g[k] for k in ("E-all", "E-cvar", "E-decoupled", "E-vac",
                                 "E-hidden", "E-exc", "E-dxi"))
    j_green = all(g[k] for k in ("J-norule", "J-census"))
    data_ok = all(g[k] for k in ("count-events", "count-pairs",
                                 "count-scans", "count-seqs"))

    if not data_ok or not j_green:
        verdict = "MERGE0-INCOMPLETE"
        reason = "data/firewall incomplete"
    elif not a_green:
        verdict = "MERGE0-INCOMPLETE"
        reason = "post-state not unique on R x U(1)"
    elif not bcdh_green:
        verdict = "MERGE0-CLASS"
        bad = [c["gate"] for c in gates
               if c["gate"].startswith(("B-", "C-", "D-", "H-", "I-"))
               and not c["ok"]]
        reason = f"confined failures: {bad}"
    else:
        verdict = "MERGE0-DETERMINISTIC"
        reason = "unique covariant outcome + exact ledger + info books"
    accounting = ("MERGE0-ACCOUNT-DEBT" if e_green
                  else "MERGE0-ACCOUNT-CLOSED")
    n_pass = sum(1 for c in gates if c["ok"])
    out = {"verdict": verdict, "accounting": accounting, "reason": reason,
           "n_gates": len(gates), "n_pass": n_pass,
           "gates": gates, "vacuum_table": vtab,
           "firewall": fw, "info0": m0.info0_status(),
           "closing_tuples": closing}
    with open(os.path.join(outdir, "verdict.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"{verdict} + {accounting} {n_pass}/{len(gates)} :: {reason}")


if __name__ == "__main__":
    main()
