"""VAC-STAB-0 analyzer: records -> preregistered checks -> verdict.

Usage:
  python scripts/vacstab_analyze.py --datadir data/vacstab \\
      --out data/vacstab/verdict.json

All gates mirror VACSTAB0-PREREG exactly (bars: vacstab.BARS). Missing
records are LOUD failures (never silent). FRAGILE physics lives in F1
(concentration ratio) and F2 (late near-maximal refocusing); the sup_K
gate is theorem-backed apparatus (triangle bound).
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import vacstab as vs  # noqa: E402

SAFE_BG = {"VPLUS": "VPLUS", "VPI": "VPI", "CIRCLE@0": "CIRCLE0",
           "CIRCLE@pi/2": "CIRCLE1", "CIRCLE@pi/6": "CIRCLE2",
           "CIRCLE@pi/3": "CIRCLE3"}

AMP_ANCHORS = (("VPLUS", "packet"), ("VPLUS", "point_amp"),
               ("CIRCLE@pi/6", "packet"))
LSCAN_CELLS = (("VPLUS", "packet"), ("VPLUS", "point_amp"),
               ("CIRCLE@pi/6", "packet"), ("CIRCLE@pi/6", "point_amp"))
XL_KINDS = ("packet", "point_amp")


def load(datadir):
    recs = {}
    for path in sorted(glob.glob(os.path.join(datadir, "*.json"))):
        base = os.path.basename(path)
        if base == "verdict.json":
            continue
        with open(path) as f:
            recs[os.path.splitext(base)[0]] = json.load(f)
    return recs


def need(recs, name):
    if name not in recs:
        raise SystemExit(f"MISSING record: {name} (campaign incomplete)")
    return recs[name]["payload"]


def stab_names():
    out = []
    for bg in vs.BACKGROUNDS:
        for kind in vs.KINDS:
            for eps in vs.eps_grid_for(bg):
                out.append(f"stab_bg{SAFE_BG[bg]}_kind{kind}_eps{eps}")
    return out


def amp_names():
    out = []
    for (bg, kind) in AMP_ANCHORS:
        for amp in vs.AMPLITUDES:
            out.append(f"amp_bg{SAFE_BG[bg]}_kind{kind}_amp{amp}")
    return out


def lscan_names():
    out = []
    for (bg, kind) in LSCAN_CELLS:
        for L in vs.L_SCAN:
            out.append(f"lscan_bg{SAFE_BG[bg]}_kind{kind}_L{L}")
    return out


def xl_names():
    out = []
    for bg in vs.BACKGROUNDS:
        for kind in XL_KINDS:
            out.append(f"xl_bg{SAFE_BG[bg]}_kind{kind}")
    return out


def run_names():
    return stab_names() + amp_names() + lscan_names() + xl_names()


def analyze(datadir):
    from bh_graph.ballistic import unwrap_trace
    from bh_graph import vacexc as vx

    recs = load(datadir)
    notes = []
    checks = {}

    # --- battery (0A apparatus, loud) ---
    assert need(recs, "battery")["ok"], "battery failed"
    notes.append("battery green (norms, weights, mixed 50/50, design)")

    # --- bgcheck (0A background regression) ---
    bg_ok = True
    for bg in vs.BACKGROUNDS:
        r = need(recs, f"bgcheck_{SAFE_BG[bg]}")
        leg = (abs(r["rayleigh"] - r["energy"]) < 1e-9
               and r["residual"] < 1e-9
               and r["current_free"] and r["stationary"])
        want = vs.background_sector(bg)
        w = r["sector"]
        if want == "sym":
            leg = leg and abs(w["w_sym"] - 1.0) < 1e-12
        else:
            leg = leg and abs(w["w_anti"] - 1.0) < 1e-12
            leg = leg and r["frozen_err"] < 1e-8
        bg_ok = bg_ok and leg
        notes.append(f"{bg}: E={r['energy']} res={r['residual']:.1e} "
                     f"u_min={r['extrema']['u_min']:.4f} "
                     f"u_max={r['extrema']['u_max']:.4f} ok={leg}")
    checks["backgrounds"] = bool(bg_ok)

    # --- unitarity: norms + split on every run (0A) ---
    # All run gates are recomputed here from rep data (records carry the
    # same flags from campaign time; the analyzer is the gate authority,
    # so AMENDMENT-2 needs no re-runs).
    unit_ok = True
    for name in run_names():
        r = need(recs, name)
        rep = r["rep"]
        leg = bool(vs.is_norm_conserved_ok(rep)) and bool(vs.is_split_ok(rep))
        unit_ok = unit_ok and leg
        if not leg:
            notes.append(f"{name}: UNITARITY FAIL n_d_drift="
                         f"{rep['n_d_drift']:.2e} "
                         f"split_max={rep['split_max']:.2e}")
    checks["unitarity"] = bool(unit_ok)
    notes.append(f"unitarity (norms + split) all runs: {unit_ok}")

    # --- sup_bounds: triangle apparatus (0B) ---
    sup_ok = True
    for name in run_names():
        r = need(recs, name)
        leg = bool(vs.is_sup_ok(r["rep"]["sup"], r["scales"]))
        sup_ok = sup_ok and leg
        if not leg:
            notes.append(f"{name}: SUP FAIL {r['rep']['sup']}")
    checks["sup_bounds"] = bool(sup_ok)
    notes.append(f"sup triangle apparatus all runs: {sup_ok}")

    # --- concentration F1 (0C, headline L28 only gated) ---
    conc_ok = True
    frag_cells = []
    for name in stab_names() + amp_names() + xl_names():
        r = need(recs, name)
        leg = bool(vs.is_concentration_ok(r["rep"]["C_ratio"]))
        conc_ok = conc_ok and leg
        if not leg:
            frag_cells.append(name + ":F1")
            notes.append(f"{name}: F1 C_ratio={r['rep']['C_ratio']:.1f} "
                         f"C_sup={r['rep']['C_sup']:.1f}")
    # L-scan concentration filed (finite-size revivals expected).
    for name in lscan_names():
        r = need(recs, name)
        notes.append(f"{name}: C_ratio={r['rep']['C_ratio']:.2f} (filed)")
    checks["concentration"] = bool(conc_ok)

    # --- late focus F2 (0B, propagating seeds on headline L28 gated) ---
    # AMENDMENT-2 scope: P-mixed/frozen seeds carry a frozen P_- half
    # whose persistent response is filed with mechanism (frozen floor +
    # revival-to-initial, verified: C_ratio = 1.00, late ~= initial
    # scale, max late-F < 1), not gated as refocusing.
    late_ok = True
    for name in stab_names() + amp_names() + xl_names():
        r = need(recs, name)
        kind = r["kind"]
        if kind not in vs.PROPAGATING_KINDS:
            tr = r["rep"]["traces"]
            init_B = float(tr["dB"][0]) / max(r["scales"]["S_B"], 1e-300)
            notes.append(f"{name}: late_ratio={r['late_ratio']:.3f} "
                         f"init_ratio={init_B:.3f} "
                         f"C_ratio={r['rep']['C_ratio']:.2f} "
                         f"F_min={r['rep']['F_min']:.4f} (filed, P-mixed)")
            continue
        leg = bool(vs.is_late_focus_ok(r["rep"], r["scales"]))
        late_ok = late_ok and leg
        if not leg:
            frag_cells.append(name + ":F2")
            notes.append(f"{name}: F2 late_ratio={r['late_ratio']:.3f} "
                         f"F_min={r['rep']['F_min']:.4f}")
    for name in lscan_names():
        r = need(recs, name)
        notes.append(f"{name}: late_ratio={r['late_ratio']:.3f} (filed)")
    checks["late_focus"] = bool(late_ok)

    # --- protection (0D, every run) ---
    prot_ok = True
    for name in run_names():
        r = need(recs, name)
        leg = bool(vs.is_protection_ok(r["rep"]))
        prot_ok = prot_ok and leg
        if not leg:
            notes.append(f"{name}: PROTECTION FAIL "
                         f"m_min={r['rep']['m_min']:.3e} "
                         f"n_zero={r['rep']['n_zero_steps']}")
    checks["protection"] = bool(prot_ok)
    notes.append(f"protection (margin + zero-free) all runs: {prot_ok}")

    # --- sector (0G, every run; scale-covariant, AMENDMENT-2) ---
    sector_ok = True
    for name in run_names():
        r = need(recs, name)
        leg = bool(vs.is_sector_conserved_ok(r["rep"]))
        sector_ok = sector_ok and leg
        if not leg:
            notes.append(f"{name}: SECTOR FAIL {r['rep']['w0_d']} "
                         f"{r['rep']['wT_d']}")
    checks["sector"] = bool(sector_ok)
    notes.append(f"d-sector conservation all runs: {sector_ok}")

    # --- identity (0I) ---
    ident_ok = True
    for kind in vs.XBG_KINDS:
        r = need(recs, f"xbg_kind{kind}")
        leg = bool(r["cross"]["ok"]) and bool(r["seed_uniform"])
        ident_ok = ident_ok and leg
        notes.append(f"xbg {kind}: max-dev={r['cross']['max_dev']:.2e} "
                     f"bitwise={r['cross']['bitwise']} ok={leg}")
    checks["identity"] = bool(ident_ok)

    # --- blind pins (0F theorems: hidden d on sym vacua) ---
    blind_ok = True
    for bg in ("VPLUS", "VPI"):
        for eps in vs.eps_grid_for(bg):
            r = need(recs, f"stab_bg{SAFE_BG[bg]}_kindhidden_sector_eps{eps}")
            leg = vs.is_blind_ok(r["rep"]["coarse_sup"], r["rep"]["d0_norm"])
            blind_ok = blind_ok and leg
            notes.append(f"blind {bg}/{eps}: coarse_sup="
                         f"{r['rep']['coarse_sup']:.2e} d0n2="
                         f"{r['rep']['d0_norm'] ** 2:.2e} ok={leg}")
    checks["blind"] = bool(blind_ok)

    # --- CLASS (0J): late-response spread by pi_0 component ---
    # Per kind: member bgs at eps_hi; normalized late_B/S_B clamped at
    # floor; kind abstains if max < class_min; fires if spread > 5.
    kinds_firing = []
    kinds_abstain = []
    kinds_quiet = []
    argmax_count: dict = {}
    for kind in vs.KINDS:
        comp_val = {}
        for comp in ("PLUS", "PI", "HIDDEN"):
            vals = []
            for bg in vs.BACKGROUNDS:
                if vs.background_component(bg) != comp:
                    continue
                eps = vs.eps_grid_for(bg)[-1]
                r = need(recs, f"stab_bg{SAFE_BG[bg]}_kind{kind}_eps{eps}")
                ratio = (r["rep"]["late"]["B"]
                         / max(r["scales"]["S_B"], 1e-300))
                vals.append(max(float(ratio), vs.BARS["class_floor"]))
            comp_val[comp] = max(vals)
        mx = max(comp_val.values())
        if mx < vs.BARS["class_min"]:
            kinds_abstain.append(kind)
            continue
        mn = min(comp_val.values())
        spread = mx / mn
        amax = max(comp_val, key=lambda c: comp_val[c])
        if spread > vs.BARS["class_spread"]:
            kinds_firing.append((kind, spread, amax))
            argmax_count[amax] = argmax_count.get(amax, 0) + 1
            notes.append(f"CLASS-fire {kind}: spread={spread:.2f} "
                         f"argmax={amax} {comp_val}")
        else:
            kinds_quiet.append((kind, spread))
            notes.append(f"CLASS-quiet {kind}: spread={spread:.2f}")
    class_fires = (len(kinds_firing) >= vs.BARS["class_kinds"]
                   and max(argmax_count.values()) >= vs.BARS["class_kinds"])
    class_detail = {"fires": bool(class_fires),
                    "firing": [(k, round(s, 3), a)
                               for (k, s, a) in kinds_firing],
                    "quiet": [(k, round(s, 3)) for (k, s) in kinds_quiet],
                    "abstain": kinds_abstain,
                    "argmax_count": argmax_count}

    # --- recurrence tables (0E, filed) ---
    rec_table = {}
    for name in xl_names() + lscan_names():
        r = need(recs, name)
        rep = r["rep"]
        tr = rep["traces"]
        com_tr = np.array([tr["comx"], tr["comy"]]).T
        L = r["L"]
        unw = unwrap_trace(np.asarray(com_tr, dtype=float),
                           (float(L), float(L)))
        wraps = vx.wrap_count(np.asarray(unw, dtype=float),
                              (float(L), float(L)))
        rec_table[name] = {"F_best": rep["F_best"], "t_best": rep["t_best"],
                           "t_first": rep["t_first"], "F_min": rep["F_min"],
                           "wraps": wraps}
    for name, row in rec_table.items():
        notes.append(f"{name}: F_best={row['F_best']:.4f} "
                     f"t_best={row['t_best']:.1f} t_first={row['t_first']} "
                     f"wraps={row['wraps']}")

    # --- amplitude slopes (0H, filed) ---
    for (bg, kind) in AMP_ANCHORS:
        la = np.log(np.array([float(a) for a in vs.AMPLITUDES]))
        sB = [need(recs, f"amp_bg{SAFE_BG[bg]}_kind{kind}_amp{a}")
              ["rep"]["sup"]["B"] for a in vs.AMPLITUDES]
        slope = float(np.polyfit(la, np.log(np.maximum(sB, 1e-300)), 1)[0])
        notes.append(f"amp {bg}/{kind}: sup_B slope={slope:.4f} (filed)")

    # --- visibility table (0F, filed) ---
    for bg in vs.BACKGROUNDS:
        row = {}
        for kind in vs.KINDS:
            eps = vs.eps_grid_for(bg)[-1]
            r = need(recs, f"stab_bg{SAFE_BG[bg]}_kind{kind}_eps{eps}")
            row[kind] = round(float(r["rep"]["coarse_sup"]), 6)
        notes.append(f"coarse {bg}: {row}")

    verdict = vs.campaign_verdict(checks, frag_cells, class_detail)
    return {"checks": {k: bool(v) for k, v in checks.items()},
            "headline": verdict["headline"],
            "frag_cells": verdict["frag_cells"],
            "class_detail": verdict["class_detail"],
            "recurrence": rec_table, "notes": notes}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--datadir", default="data/vacstab")
    ap.add_argument("--out", default="data/vacstab/verdict.json")
    a = ap.parse_args(argv)
    out = analyze(a.datadir)
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)
    print("headline:", out["headline"])
    for k, v in out["checks"].items():
        print(f"  {k}: {v}")
    for n in out["notes"]:
        print("  |", n)
    print(a.out)


if __name__ == "__main__":
    main()
