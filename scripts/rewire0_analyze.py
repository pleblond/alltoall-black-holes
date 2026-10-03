"""REWIRE-0 analyzer: frozen gates -> verdict (pre-data logic).

Reads per-task records from data/rewire0/*.json (campaign output),
applies the frozen gate battery, and writes data/rewire0/verdict.json.
Headline class: j2L4-joint + j2L4-circle + j2L4-texture + j2L4-exc-*
(exhaustive, N=32). Specified classes: tiny-<graph> groups +
j2L8/j2L28 anchors (filed scale controls). Exit 0 always.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import rewire0 as r0

HEADLINE_TASKS = ("j2L4-joint", "j2L4-circle", "j2L4-texture",
                  "j2L4-exc-VPLUS", "j2L4-exc-VPI", "j2L4-exc-VMINUS")


def load_records(indir: str) -> dict:
    out = {}
    for p in sorted(glob.glob(os.path.join(indir, "*.json"))):
        base = os.path.basename(p)
        if base == "verdict.json":
            continue
        with open(p) as f:
            d = json.load(f)
        out[d.get("task", base[:-5])] = d
    return out


def analyze(indir: str) -> dict:
    recs = load_records(indir)
    gates = []

    def _gate(name, ok, detail):
        gates.append({"gate": name, "ok": bool(ok), "detail": str(detail)})

    # H-INST: all 20 tasks present.
    TASKS = ([f"tiny-{g}" for g in r0.TINY_GRAPHS]
             + ["j2L4-joint", "j2L4-circle", "j2L4-texture",
                "j2L4-exc-VPLUS", "j2L4-exc-VPI", "j2L4-exc-VMINUS",
                "j2L8-anchor", "j2L28-anchor", "historical", "controls"])

    missing = [t for t in TASKS if t not in recs]
    _gate("H-INST-complete", not missing,
          f"tasks={len(recs)}/{len(TASKS)} missing={missing}")

    # H-LEDGER: BR-2.6-style dE identity exact everywhere.
    max_err = 0.0
    n_rows = 0
    for t, d in recs.items():
        for row in d.get("rows", []):
            n_rows += 1
            max_err = max(max_err, float(row.get("max_ledger_err", 0.0)))
    _gate("H-ledger-exact", max_err < 1e-9,
          f"rows={n_rows} max_err={max_err:.3e}")

    # H-QUOT: controls quotient invariance + determinism.
    ctrl = recs.get("controls", {})
    _gate("H-quotient", bool(ctrl.get("quotient_invariant", False)),
          f"n_phys_ring6={ctrl.get('n_phys_ring6', '?')}")
    _gate("H-determinism", bool(ctrl.get("deterministic", False)), "repeat")

    # H-HIST: BR-1 closed form matches banked; blind probes filed.
    hist = recs.get("historical", {})
    br1 = hist.get("br1", {})
    _gate("H-hist-br1", bool(br1.get("match", False)),
          f"closed={br1.get('L28_closed', '?')} banked={br1.get('banked', '?')}")
    blind = {k: hist.get(k, {}) for k in ("blind_L4", "blind_L8")}
    _gate("H-hist-blind", True, f"filed sq4={blind['blind_L4'].get('square', {})} "
                                f"tri4={blind['blind_L4'].get('triangle', {})}")

    # M-HEAD: headline census table.
    head_rows = []
    for t in HEADLINE_TASKS:
        head_rows.extend(recs.get(t, {}).get("rows", []))
    nphys = [r["n_phys"] for r in head_rows]
    _gate("M-head-counts", bool(head_rows),
          f"states={len(head_rows)} n_phys_min={min(nphys) if nphys else '?'} "
          f"max={max(nphys) if nphys else '?'}")
    # Per-principle headline status histogram.
    histo = {}
    for p in r0.PRINCIPLES:
        counts = {}
        for r in head_rows:
            s = r["principles"][p]["status"]
            counts[s] = counts.get(s, 0) + 1
        histo[p] = counts
    _gate("M-head-principles", True, json.dumps(histo, sort_keys=True))

    # M-COV: covariance violations on headline (filed, ladder uses them).
    viol = {}
    for p in r0.PRINCIPLES:
        viol[p] = sum(int(r["covariance"][p].get("closure_violations", 0))
                      for r in head_rows)
    _gate("M-covariance", True, json.dumps(viol, sort_keys=True))

    # M-VAC / M-EXC: vacuum vs excitation UNIQUE fractions (descriptive).
    vac_rows = []
    for t in ("j2L4-joint", "j2L4-circle", "j2L4-texture"):
        vac_rows.extend(recs.get(t, {}).get("rows", []))
    exc_rows = []
    for t in ("j2L4-exc-VPLUS", "j2L4-exc-VPI", "j2L4-exc-VMINUS"):
        exc_rows.extend(recs.get(t, {}).get("rows", []))

    def _uniq_frac(rows):
        if not rows:
            return 0.0
        n = sum(1 for r in rows
                if any(r["principles"][p]["status"] == "UNIQUE"
                       for p in r0.PRINCIPLES))
        return n / len(rows)

    _gate("M-vacuum", True,
          f"vac_states={len(vac_rows)} uniq_frac={_uniq_frac(vac_rows):.3f}")
    _gate("M-excitation", True,
          f"exc_states={len(exc_rows)} uniq_frac={_uniq_frac(exc_rows):.3f}")

    # M-DIST: fraction of headline states with any distinguishing quantity.
    nd = sum(1 for r in head_rows
             if r.get("dist", {}).get("any_quantity_distinguishes", False))
    _gate("M-dist", True,
          f"distinguishing={nd}/{len(head_rows)}")

    # M-SCALE: anchors filed (L8/L28 n_phys per primary-subset).
    for t in ("j2L8-anchor", "j2L28-anchor"):
        rows = recs.get(t, {}).get("rows", [])
        ns = [r["n_phys"] for r in rows]
        _gate(f"M-scale-{t}", bool(rows),
              f"states={len(rows)} n_phys_range="
              f"{min(ns) if ns else '?'}..{max(ns) if ns else '?'}")

    # M-TINY: specified tiny classes filed.
    tiny_summary = {}
    for t, d in recs.items():
        if t.startswith("tiny-"):
            rows = d.get("rows", [])
            tiny_summary[t] = {
                "states": len(rows),
                "n_phys": [r["n_phys"] for r in rows],
            }
    _gate("M-tiny", True, f"classes={len(tiny_summary)}")

    # Verdict.
    specified = {}
    for t, d in recs.items():
        if t.startswith("tiny-") or t in ("j2L8-anchor", "j2L28-anchor"):
            specified[t] = d.get("rows", [])
    verdict = r0.campaign_verdict({"headline": head_rows,
                                   "specified": specified})
    hard_ok = all(g["ok"] for g in gates if g["gate"].startswith("H-"))
    return {"gates": gates, "hard_ok": bool(hard_ok),
            "verdict": verdict["verdict"], "principle": verdict.get("principle"),
            "class": verdict.get("class"),
            "interpretation": verdict.get("detail", ""),
            "headline_histo": histo, "cov_viol": viol}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--indir", default="data/rewire0")
    ap.add_argument("--out", default="data/rewire0/verdict.json")
    args = ap.parse_args()
    rep = analyze(args.indir)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(rep, f, indent=1)
    print(f"REWIRE0-VERDICT {rep['verdict']} hard_ok={rep['hard_ok']}")
    for g in rep["gates"]:
        print(f"  {'PASS' if g['ok'] else 'FAIL'} {g['gate']}: {g['detail']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
