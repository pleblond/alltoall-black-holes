"""SCALE-0 analyzer (frozen gates per SCALE0-PREREG + Amendment-1).

Reads data/scale0/cells/*.json, checks HARD regression gates, builds the
machine-readable O(L) matrix + fits + unresolved list, and writes the
verdict. Bars come ONLY from bh_graph.scale0 (no retuning).
"""

import argparse
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))
from bh_graph import obs0, scale0  # noqa: E402
import scale0_campaign as camp  # noqa: E402

FAILS = []


def gate(name: str, ok: bool, detail: str = ""):
    print(f"{'PASS' if ok else 'FAIL'} {name} {detail}", flush=True)
    if not ok:
        FAILS.append(name)


def load_cells(d: str) -> dict:
    out = {}
    cdir = os.path.join(d, "cells")
    for fn in sorted(os.listdir(cdir)):
        if fn.endswith(".json"):
            with open(os.path.join(cdir, fn)) as f:
                rec = json.load(f)
            out[rec["task"]] = rec["payload"]
    return out


def tau_pairs_ok(pairs) -> bool:
    """Per-pair |tauK - tauS| <= max(2 wave steps, 5%) (P1 gate)."""
    for pr in pairs:
        b, k = pr["banked"], pr["krylov"]
        if b is None and k is None:
            continue
        if b is None or k is None:
            return False
        if abs(k - b) > max(2 * obs0.DT_WAVE, 0.05 * abs(b)):
            return False
    return True


def _le(x, bar) -> bool:
    """Amendment-2: None-safe x <= bar (exact 0.0 passes; None/NaN fail).

    The frozen draft used `(x or default)`, which maps exact 0.0 -- the
    best possible outcome -- to the fail default. Bars are unchanged.
    """
    try:
        return x is not None and bool(x <= bar)
    except TypeError:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--indir", default="data/scale0")
    ap.add_argument("--outdir", default="data/scale0")
    args = ap.parse_args()
    cells = load_cells(args.indir)
    expected = camp.all_tasks()
    missing = [t for t in expected if t not in cells]
    gate("COMPLETE", not missing, f"({len(cells)}/{len(expected)}"
         + (f" missing={missing[:5]}" if missing else "") + ")")

    # ---- R-OBS ----
    ok = True
    for tag in camp.REPLAY_TAGS:
        p = cells.get(f"obs_replay__{tag}", {})
        if not p:
            ok = False
            continue
        ok = ok and _le(p.get("dh_dev"), scale0.BAR_REPLAY)
        ok = ok and _le(p.get("krylov_ds_maxdev"), scale0.BAR_KRYLOV_DS)
        ok = ok and tau_pairs_ok(p.get("krylov_tau_pairs", [{"banked": 0, "krylov": 1}]))
        ok = ok and bool((p.get("topo") or {}).get("N_ok")) and bool((p.get("topo") or {}).get("D_ok"))
    for L in (64, 128):
        for sub in ("j2", "sq"):
            for oi in range(4):
                p = cells.get(f"obs_krylov__{sub}-L{L}-o{oi}", {})
                if not p:
                    ok = False
                    continue
                if p.get("banked_ds") is not None:
                    ok = ok and abs(p["ds"] - p["banked_ds"]) <= scale0.BAR_KRYLOV_DS
                ok = ok and tau_pairs_ok(p.get("val_tau_pairs", [{"banked": 0, "krylov": 1}]))
    gate("R-OBS", ok)

    # ---- R-RESP ----
    ok = True
    for which in ("HR", "HI"):
        p = cells.get(f"resp_regress__L28-{which}", {})
        v = p.get("v_field")
        lo, hi = scale0.BAR_RESP_V_FIELD
        ok = ok and v is not None and bool(lo < v < hi)
        if which == "HR" and v is not None:
            ok = ok and abs(v - scale0.BANKED["resp_v_field"]) / scale0.BANKED["resp_v_field"] <= scale0.BAR_RESP_V_RTOL
            vq = p.get("v_J")
            ok = ok and vq is not None and abs(vq - scale0.BANKED["resp_v_quad"]) / scale0.BANKED["resp_v_quad"] <= scale0.BAR_RESP_V_QUAD_RTOL
        elif which == "HR":
            ok = False
        ok = ok and _le(p.get("decomp"), scale0.BAR_RESP_DECOMP)
    gate("R-RESP", ok)

    # ---- R-P1 ----
    ok = True
    p = cells.get("p1_regress__j2-L28", {})
    if p:
        ok = ok and abs(p["mean"] - scale0.BANKED["p1_j2"]) / scale0.BANKED["p1_j2"] <= scale0.BAR_P1_J2_RTOL
    else:
        ok = False
    p = cells.get("p1_regress__sq-L30", {})
    if p:
        ok = ok and abs(p["v"] - scale0.BANKED["p1_sq"]) / scale0.BANKED["p1_sq"] <= scale0.BAR_P1_SQ_RTOL
    else:
        ok = False
    gate("R-P1", ok)

    # ---- R-POT ----
    ok = True
    p = cells.get("pot_regress__L28", {})
    if p:
        ok = ok and _le(p.get("cg_spsolve_dev"), scale0.BAR_CG_SPSOLVE)
        ok = ok and abs(p.get("range", -99) - 3) <= 1
        ok = ok and abs(p.get("xi", 0.0) - 0.53) / 0.53 <= scale0.BAR_POT_XI_RTOL
    else:
        ok = False
    gate("R-POT", ok)

    # ---- R-QUOT ----
    ok = True
    p = cells.get("quot_regress__L28-alg", {})
    if p:
        ok = ok and _le(p.get("comm"), scale0.BAR_QUOT_ALG)
        ok = ok and _le(p.get("dead"), scale0.BAR_QUOT_ALG)
        ok = ok and _le(p.get("inter"), scale0.BAR_QUOT_ALG)
        ok = ok and bool(p.get("neighbor_sets"))
    else:
        ok = False
    p = cells.get("quot_regress__L28-wave", {})
    if p:
        sh = p.get("shells", {})
        for r in (2, 4, 6):
            s = sh.get(f"sym@{r}", {})
            a = sh.get(f"anti@{r}", {})
            ok = ok and s.get("arrival") is not None
            ok = ok and _le(a.get("C"), scale0.BAR_QUOT_ANTI)
    else:
        ok = False
    gate("R-QUOT", ok)

    # ---- R-ZERO ----
    # Amendment-2: the banked 508 was refined with PRE-CAP code; frozen
    # code caps Level-2 refinement at REFINE_CAP = 60 (ZERO-0 d932d57).
    # Exact-replay gate under current code: screening reproduces 508
    # candidates to the digit, cap binds at 60 events, rest overflows.
    ok = True
    p = cells.get("zero_regress__headon", {})
    ok = ok and bool(p) and p.get("n_candidates") == 508 \
        and p.get("n_events") == 60 and p.get("refine_overflow") == 448
    p = cells.get("zero_regress__refine", {})
    ok = ok and bool(p) and bool(p.get("bitwise"))
    gate("R-ZERO", ok)

    # ---- R-VACEXC ----
    ok = True
    p = cells.get("vacexc_regress__L4-crossbg", {})
    md = (p.get("maxdev", {}) or {})
    if isinstance(md, dict):
        mdv = md.get("max_dev", md.get("maxdev", 1.0))
    else:
        mdv = md
    ok = ok and bool(p) and float(mdv) == 0.0
    p = cells.get("vacexc_regress__L28-frac", {})
    ok = ok and bool(p) and _le(p.get("frac_dev"), scale0.BAR_VACEXC_FRAC)
    p = cells.get("vacexc_regress__L28-packet", {})
    if p and p.get("vels"):
        vv = np.array(list(p["vels"].values()), dtype=float)
        ok = ok and (vv.max() - vv.min()) / max(vv.mean(), 1e-300) <= scale0.BAR_VACEXC_V_RTOL
    else:
        ok = False
    gate("R-VACEXC", ok)

    # ---- R-VACCOMP ----
    ok = True
    p = cells.get("vaccomp_regress__L4-census", {})
    c = (p.get("census") or {}) if p else {}
    ok = ok and bool(c.get("decomposition_ok")) and c.get("n_zero") == 22
    p = cells.get("vaccomp_regress__L8-rows", {})
    ok = ok and bool(p) and p.get("minus8_mult") == 1 and p.get("plus8_mult") == 1
    gate("R-VACCOMP", ok)

    # ---- matrix ----
    rows = []
    unr = []

    def add(row):
        rows.append(row)
        if row["unresolved"] is not None:
            unr.append({"observable": row["observable"], "L": row["L"],
                        "channel": row["channel"], "variant": row["variant"],
                        "reason": row["unresolved"]["reason"]})

    LADDER = list(scale0.LADDER)
    # OBS rows.
    for L in LADDER:
        for sub in ("j2", "sq"):
            h = cells.get(f"obs_hausdorff__{sub}-L{L}", {})
            if h:
                add(scale0.make_row("OBS", L, sub, "STATIC", "d_H", "median",
                                    h["d_median"], {"kind": "median_spread",
                                                    "spread": h["d_spread"],
                                                    "r2_min": h["r2_min"]},
                                    "obs0.hausdorff_dim", h["n"]))
            ds_vals = []
            for key in cells:
                if key.startswith(f"obs_krylov__{sub}-L{L}-o"):
                    ds_vals.append(cells[key]["ds"])
            if ds_vals:
                a = np.array(ds_vals, dtype=float)
                add(scale0.make_row("OBS", L, sub, "PRE", "d_s", "krylov-return",
                                    float(np.nanmedian(a)),
                                    {"kind": "median_spread",
                                     "spread": float(np.nanmax(a) - np.nanmin(a))},
                                    "scale0.krylov_diffusion_return", len(a),
                                    "diffusive wrap (L/2)^2 >> 24 at all L"))
            # tauW residuals (banked-V calibration, wrap-safe subset).
            V = obs0.V_BANKED[sub]
            deltas, teens, miss, tot = [], [], 0, 0
            for key in cells:
                if key.startswith(f"obs_krylov__{sub}-L{L}-o"):
                    D = cells[key]["D"]
                    for v, rec in cells[key]["taus"].items():
                        tot += 1
                        if rec["tW"] is None:
                            miss += 1
                            continue
                        deltas.append(obs0.delta_stat(V * rec["tW"], rec["R"]))
            if deltas:
                a = np.array(deltas, dtype=float)
                add(scale0.make_row("OBS", L, sub, "PRE", "tauW_resid", "median",
                                    float(np.median(a)),
                                    {"kind": "median_spread",
                                     "spread": float(a.max() - a.min())},
                                    "obs0.delta_stat-banked-V", len(a)))
                add(scale0.make_row("OBS", L, sub, "PRE", "tauW_missing", "frac",
                                    miss / max(tot, 1), {"kind": "count"},
                                    "threshold_crossing", tot))
            dm = cells.get(f"obs_dim__{sub}-L{L}", {})
            if dm:
                for ch in ("composite", "composite_WP"):
                    if ch in dm.get("probes", {}):
                        g = dm["probes"][ch]["geo"]
                        add(scale0.make_row("OBS", L, sub, "STATIC", "d_star", ch,
                                            g["dstar"], {"kind": "fit_r2",
                                                         "pass": g["pass"],
                                                         "stress": g["stress"]},
                                            "obs1.select_dimension",
                                            64, "WP-only at L>=256" if L >= 256 else ""))
                        add(scale0.make_row("OBS", L, sub, "STATIC", "vol_d", ch,
                                            g["vol_d"], {"kind": "fit_r2",
                                                         "r2": g["vol_r2"]},
                                            "obs1.volume_dimension", 64))
    # OBS replay rows (banked heat/weyl) + P6 unresolved.
    for tag in camp.REPLAY_TAGS:
        p = cells.get(f"obs_replay__{tag}", {})
        if not p:
            continue
        sub = "j2" if tag.startswith("j2") else "sq"
        L = int(tag.split("-")[1][1:])
        add(scale0.make_row("OBS", L, sub, "STATIC", "heat_ds", "banked",
                            p["info_heat"]["d"], {"kind": "fit_r2",
                                                  "r2": p["info_heat"]["r2"]},
                            "obs0.heat_trace_ds-banked", 5, "P8 read-only"))
        add(scale0.make_row("OBS", L, sub, "STATIC", "weyl_ds", "banked",
                            p["info_weyl"]["d"], {"kind": "count",
                                                  "n": p["info_weyl"]["n"]},
                            "obs0.weyl_ds-banked", p["info_weyl"]["n"],
                            "P8 read-only"))
    for L in (256, 512):
        for sub in ("j2", "sq"):
            add(scale0.make_row("OBS", L, sub, "STATIC", "weyl_ds", "banked",
                                None, {"kind": "none"}, "none", 0,
                                "P6 needs full spectrum",
                                {"reason": "P6-no-Weyl-at-L>=256", "class": "spectrum"}))
            add(scale0.make_row("OBS", L, sub, "STATIC", "heat_ds", "banked",
                                None, {"kind": "none"}, "none", 0,
                                "P6 needs full spectrum",
                                {"reason": "P6-no-heat-trace-at-L>=256", "class": "spectrum"}))
    # OBS gaps.
    for L in LADDER:
        for ch, var in (("d_H", "median"), ("d_s", "krylov-return"),
                        ("d_star", "composite_WP")):
            vals = {}
            for r in rows:
                if r["observable"] == "OBS" and r["L"] == L and r["channel"] == ch \
                        and r["variant"] == var and r["substrate"] in ("j2", "sq"):
                    vals[r["substrate"]] = r["value"]
            if "j2" in vals and "sq" in vals and vals["j2"] is not None \
                    and vals["sq"] is not None:
                add(scale0.make_row("OBS", L, "gap", "STATIC", f"gap-{ch}", var,
                                    abs(vals["j2"] - vals["sq"]),
                                    {"kind": "exact"}, "abs-diff", 2))
    # RESPONSE rows.
    for L in LADDER:
        for bg in ("BG0", "BG+"):
            p = cells.get(f"resp__L{L}-{bg}", {})
            if not p:
                continue
            for obs_ch, var in (("q_psi", "dpsi"), ("q_rho", "drho"),
                                ("q_B", "dB"), ("q_J", "dJ")):
                a = p.get(obs_ch, {})
                for fit in ("fit10", "fitExt"):
                    f = a.get(fit) or {}
                    if f.get("v") is not None:
                        add(scale0.make_row("RESPONSE", L, bg, "PRE", f"v_{var}",
                                            fit, f["v"],
                                            {"kind": "fit_r2", "r2": f["r2"]},
                                            "response.front_velocity", f["n"]))
                for reg in ("pre", "post"):
                    for ext in ("exp10", "expExt"):
                        e = a.get(f"{ext}_{reg}") or {}
                        if e.get("n", 0) >= 3:
                            add(scale0.make_row("RESPONSE", L, bg, reg.upper(),
                                                f"exp_{var}", ext, e["p"],
                                                {"kind": "fit_r2", "r2": e["r2"]},
                                                "scale0.fit_loglog", e["n"]))
            rv = p.get("ray_vel", {})
            if (rv.get("axial") or {}).get("v") and (rv.get("diag") or {}).get("v"):
                add(scale0.make_row("RESPONSE", L, bg, "PRE", "anisotropy",
                                    "diag-over-axial",
                                    rv["diag"]["v"] / rv["axial"]["v"],
                                    {"kind": "exact",
                                     "axial": rv["axial"], "diag": rv["diag"]},
                                    "response.quotient_ray", 2))
            add(scale0.make_row("RESPONSE", L, bg, "STATIC", "decomp", "max",
                                p.get("decomp_max"), {"kind": "exact"},
                                "response.delta_observables", 8))
    # P1 rows.
    for L in LADDER:
        for kk in ("k03", "k05"):
            p = cells.get(f"p1__L{L}-{kk}", {})
            if not p:
                continue
            pre_ok = p["travel_pre_max"] < p["L_half"]
            post_ok = p["travel_post_max"] >= p["L_half"]
            for reg, ok in (("PRE", pre_ok), ("POST", post_ok)):
                v = (p["v_pre"] if reg == "PRE" else p["v_post"]) or {}
                # Amendment-2: row banks the scalar speed (fit_velocity
                # "speed"); the draft banked the 2-vector "v", which is not
                # a fittable series (vectors stay available in the cells).
                add(scale0.make_row("P1", L, kk, reg, "v", "com-fit",
                                    v.get("speed"), {"kind": "fit_r2",
                                                     "r2": v.get("r2")},
                                    "ballistic.fit_velocity", 2,
                                    "" if ok else "REGIME-VOID",
                                    None if ok else {"reason": "regime-window-void",
                                                     "class": "fit_fail"}))
                add(scale0.make_row("P1", L, kk, reg, "width_rate", "linear",
                                    p.get(f"width_rate_{reg.lower()}"),
                                    {"kind": "exact"}, "ballistic.packet_width", 2))
                add(scale0.make_row("P1", L, kk, reg, "msd_alpha", "rs",
                                    p.get(f"msd_{reg.lower()}"),
                                    {"kind": "exact"},
                                    "ballistic.msd_exponent_rs", 2))
    # POT rows.
    for L in LADDER:
        p = cells.get(f"pot__L{L}", {})
        if not p:
            continue
        for ch in ("xi", "range", "floor", "res1d"):
            add(scale0.make_row("POT", L, "j2", "STATIC", ch, "cg",
                                p.get(ch), {"kind": "exact"},
                                "scale0.cg_static_phi", 1))
    # QUOT rows.
    for L in LADDER:
        fams = ["sym", "anti"] + (["sheet0", "sheet1"] if L <= 128 else [])
        for fam in fams:
            p = cells.get(f"quot__L{L}-{fam}", {})
            if not p:
                continue
            for reg in ("pre", "post"):
                cap = p.get(f"wave_{reg}", {}) or {}
                for r in ("2", "4", "6"):
                    c = cap.get(r, {}) or cap.get(int(r), {}) or {}
                    if c:
                        add(scale0.make_row("QUOT", L, fam, reg.upper(),
                                            "arrival", f"shell-{r}",
                                            c.get("arrival"), {"kind": "exact"},
                                            "quot.capacity_curve", c.get("n", 0)))
                # Amendment-2: remote = r >= 2 per frozen R_LOAD = (2,4,6);
                # r = 1 is a contact shell (C = 0.5 by construction).
                remote = [c.get("C") for r, c in cap.items()
                          if int(r) >= 2 and c.get("C") is not None]
                if remote:
                    add(scale0.make_row("QUOT", L, fam, reg.upper(),
                                        "Cmax_remote", "max-r>=2", max(remote),
                                        {"kind": "exact"},
                                        "quot.capacity_curve", len(remote)))
            dc = p.get("diff_pre", {}) or {}
            dremote = [c.get("C") for r, c in dc.items()
                       if int(r) >= 1 and c.get("C") is not None]
            if dremote:
                add(scale0.make_row("QUOT", L, fam, "PRE", "diff_Cmax_remote",
                                    "T16", max(dremote), {"kind": "exact"},
                                    "stepped-diffusion", len(dremote),
                                    "frozen T=16 horizon; post unresolved-cost"))
            if fam == "sym" and p.get("pot_asym") is not None:
                add(scale0.make_row("QUOT", L, fam, "STATIC", "pot_asym", "cg",
                                    p["pot_asym"], {"kind": "exact"},
                                    "quot.pot_sheet_asymmetry", 1))
    # ZERO rows.
    for L in LADDER:
        for fam in ("F1", "F5", "ppinode"):
            p = cells.get(f"zero__L{L}-{fam}-pre", {})
            if not p or p.get("filed"):
                # Amendment-2: filed pre cells (e.g. F1 initial-exclusion
                # vacuous at large n) skip like POST filed cells; the cell
                # itself is the machine-readable record.
                continue
            if p.get("unresolved"):
                for ch in ("near_density", "min_amp", "n_screen", "refined_min"):
                    add(scale0.make_row("ZERO", L, fam, "PRE", ch, "stream",
                                        None, {"kind": "none"}, "none", 0, "",
                                        p["unresolved"]))
                continue
            n = scale0.j2_size(L)
            steps = int(round(p["T"] / p["dt"])) + 1
            add(scale0.make_row("ZERO", L, fam, "PRE", "near_density", "stream",
                                p["near_total"] / max(steps * n, 1),
                                {"kind": "count"}, "streamed-screen", steps))
            add(scale0.make_row("ZERO", L, fam, "PRE", "min_amp", "global",
                                p["min_amp_global"], {"kind": "exact"},
                                "streamed-min", steps))
            add(scale0.make_row("ZERO", L, fam, "PRE", "n_screen", "nodes",
                                p["n_screen_nodes"], {"kind": "count"},
                                "zero.screen_candidates", steps))
            rmin = min([r.get("amp_min") for r in p.get("refined", [])
                        if r.get("amp_min") is not None], default=None)
            add(scale0.make_row("ZERO", L, fam, "PRE", "refined_min", "top25",
                                rmin, {"kind": "exact"},
                                "zero.refine_candidate",
                                len(p.get("refined", []))))
    for L in (64, 128):
        for fam in ("F1", "F5", "ppinode"):
            p = cells.get(f"zero__L{L}-{fam}-post", {})
            if not p or p.get("unresolved") or p.get("filed"):
                continue
            n = scale0.j2_size(L)
            steps = int(round(p["T"] / p["dt"])) + 1
            add(scale0.make_row("ZERO", L, fam, "POST", "near_density", "stream",
                                p["near_total"] / max(steps * n, 1),
                                {"kind": "count"}, "streamed-screen", steps))
    # VACEXC rows.
    for L in LADDER:
        p = cells.get(f"vacexc__L{L}-crossbg", {})
        if p:
            for kind, rec in (p.get("kinds") or {}).items():
                add(scale0.make_row("VACEXC", L, kind, "STATIC", "cross_maxdev",
                                    "all-vac", rec.get("cross_maxdev"),
                                    {"kind": "exact"},
                                    "streamed-cross-dev", 4,
                                    "exact identity, all-t max"))
                for vc, vv in (rec.get("vels") or {}).items():
                    add(scale0.make_row("VACEXC", L, kind, "PRE", "packet_v", vc,
                                        (vv or {}).get("v"), {"kind": "exact"},
                                        "streamed-COM", 2))
        q = cells.get(f"vacexc__L{L}-fracladder", {})
        if q:
            add(scale0.make_row("VACEXC", L, "packet", "STATIC", "frac_dev",
                                "7dec", q.get("frac_dev"), {"kind": "exact"},
                                "streamed-frac-dev", 7))
            for vc, mm in (q.get("margins") or {}).items():
                add(scale0.make_row("VACEXC", L, "packet", "PRE", "margin", vc,
                                    mm, {"kind": "exact"},
                                    "vacexc.protection_margin", 31))
    # VACCOMP rows.
    for L in LADDER:
        p = cells.get(f"vaccomp__L{L}", {})
        if not p:
            continue
        f = p.get("formula", {})
        for ch in ("n_zero", "flat", "nodal"):
            add(scale0.make_row("VACCOMP", L, "j2", "STATIC", ch, "formula",
                                f.get(ch), {"kind": "exact"},
                                "vaccomp.zero_count_formula", 1))
        for name, rec in (p.get("rays") or {}).items():
            if rec:
                add(scale0.make_row("VACCOMP", L, "j2", "STATIC", "ray_E", name,
                                    rec.get("E"), {"kind": "exact"},
                                    "vacfield.rayleigh_energy", 1))
        for name, rec in (p.get("ladders") or {}).items():
            rec = rec or {}
            # Amendment-2: dense legs filed unresolved-cost at L >= 256.
            if "unresolved" in rec:
                add(scale0.make_row("VACCOMP", L, "j2", "STATIC", "ladder",
                                    name, None, {"kind": "none"},
                                    "none", 0, "", rec["unresolved"]))
                continue
            add(scale0.make_row("VACCOMP", L, "j2", "STATIC", "ladder", name,
                                rec.get("rung", rec.get("error")),
                                {"kind": "exact"}, "vaccomp.joint_ladder", 1))
        circ = p.get("circle", {}) or {}
        if "unresolved" in circ:
            for ch in ("n_joint", "n_background"):
                add(scale0.make_row("VACCOMP", L, "j2", "STATIC",
                                    f"circle_{ch}", "RP1", None,
                                    {"kind": "none"}, "none", 0, "",
                                    circ["unresolved"]))
        else:
            for ch in ("n_joint", "n_background"):
                if ch in circ:
                    add(scale0.make_row("VACCOMP", L, "j2", "STATIC",
                                        f"circle_{ch}",
                                        "RP1", circ[ch], {"kind": "count"},
                                        "vaccomp.circle_probe", 1))
        amps = p.get("amps", {}) or {}
        if "unresolved" in amps:
            add(scale0.make_row("VACCOMP", L, "j2", "STATIC", "amps", "VPLUS",
                                None, {"kind": "none"}, "none", 0, "",
                                amps["unresolved"]))
        elif "all_joint" in amps:
            add(scale0.make_row("VACCOMP", L, "j2", "STATIC", "amps", "VPLUS",
                                amps["all_joint"], {"kind": "exact"},
                                "vaccomp.amplitude_family_ladder", 7))

    assert scale0.is_matrix_ok(rows), "matrix schema violation"
    print(f"MATRIX rows={len(rows)} unresolved={len(unr)}", flush=True)

    # ---- fits ----
    FIT_SPECS = [
        ("OBS", "d_H", "STATIC", "const"), ("OBS", "d_s", "PRE", "const"),
        ("OBS", "d_star", "STATIC", "const"), ("OBS", "vol_d", "STATIC", "const"),
        ("OBS", "tauW_resid", "PRE", "trend-only"),
        ("OBS", "gap-d_H", "STATIC", "trend-only"),
        ("OBS", "gap-d_s", "STATIC", "trend-only"),
        ("RESPONSE", "v_dpsi", "PRE", "const"),
        ("RESPONSE", "v_drho", "PRE", "const"),
        ("RESPONSE", "v_dJ", "PRE", "const"),
        ("RESPONSE", "exp_dpsi", "PRE", "trend-only"),
        ("RESPONSE", "exp_drho", "PRE", "trend-only"),
        ("RESPONSE", "exp_dJ", "PRE", "trend-only"),
        ("RESPONSE", "anisotropy", "PRE", "trend-only"),
        ("P1", "v", "PRE", "const"), ("P1", "v", "POST", "trend-only"),
        ("P1", "width_rate", "PRE", "trend-only"),
        ("P1", "msd_alpha", "PRE", "trend-only"),
        ("POT", "xi", "STATIC", "saturate"), ("POT", "range", "STATIC", "saturate"),
        ("POT", "floor", "STATIC", "trend-only"),
        ("POT", "res1d", "STATIC", "trend-only"),
        ("QUOT", "arrival", "PRE", "trend-only"),
        ("QUOT", "Cmax_remote", "PRE", "exact-zero"),
        ("QUOT", "Cmax_remote", "POST", "trend-only"),
        ("ZERO", "near_density", "PRE", "trend-only"),
        ("ZERO", "min_amp", "PRE", "trend-only"),
        ("VACEXC", "cross_maxdev", "STATIC", "exact-zero"),
        ("VACEXC", "frac_dev", "STATIC", "exact-zero"),
        ("VACEXC", "packet_v", "PRE", "const"),
        ("VACEXC", "margin", "PRE", "trend-only"),
        ("VACCOMP", "n_zero", "STATIC", "exact-formula"),
    ]
    fits = []
    for obs, ch, reg, form in FIT_SPECS:
        if form == "exact-formula":
            ok = True
            for r in rows:
                if r["observable"] == obs and r["channel"] == ch and r["regime"] == reg:
                    f = {"n_zero": r["L"] ** 2 + __import__(
                        "bh_graph.malus", fromlist=["nodal_count_square"]
                    ).nodal_count_square(r["L"])}["n_zero"] if ch == "n_zero" else None
                    if ch == "n_zero" and r["value"] != 2 * r["L"] ** 2 // 2 + \
                            __import__("bh_graph.malus",
                                       fromlist=["nodal_count_square"]).nodal_count_square(r["L"]):
                        ok = False
            fits.append({"observable": obs, "channel": ch, "regime": reg,
                         "form": form, "upheld": ok, "n": 4,
                         "comment": "n_zero = N/2 + nodal(L) combinatorics"})
            if not ok:
                FAILS.append(f"FIT-{obs}-{ch}")
            continue
        if form == "exact-zero":
            series = [(r["L"], r["value"]) for r in rows
                      if r["observable"] == obs and r["channel"] == ch
                      and r["regime"] == reg and r["value"] is not None
                      and not (obs == "QUOT" and r["substrate"] == "sym")]
            bars = {"QUOT": scale0.BAR_QUOT_ANTI, "VACEXC": 1e-9}
            bar = bars.get(obs, 1e-9)
            worst = max([abs(v) for _, v in series], default=float("nan"))
            upheld = bool(series) and bool(worst <= bar)
            fits.append({"observable": obs, "channel": ch, "regime": reg,
                         "form": form, "bar": bar, "worst": worst,
                         "upheld": upheld, "n": len(series),
                         "comment": "exact-zero upheld at all L" if upheld
                         else "NONZERO at some L (filed, not asymptotic)"})
            if not upheld:
                FAILS.append(f"FIT-{obs}-{ch}-{reg}")
            continue
        # Grouped series over ladder L.
        groups = {}
        for r in rows:
            if r["observable"] == obs and r["channel"] == ch and r["regime"] == reg \
                    and r["value"] is not None and r["unresolved"] is None:
                key = (r["substrate"], r["variant"])
                groups.setdefault(key, []).append((r["L"], r["value"]))
        for (sub, var), pts in sorted(groups.items()):
            pts = sorted(pts)
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            est = scale0.asymptotic_estimate(xs, ys)
            entry = {"observable": obs, "channel": ch, "regime": reg,
                     "substrate": sub, "variant": var, "form": form,
                     "points": pts, "monotone": scale0.is_monotone_ok(ys),
                     "asymptotic": est, "n": len(pts)}
            if form == "const":
                entry["fit"] = scale0.fit_const(ys)
                entry["comment"] = "theory: L-independent"
            elif form == "saturate":
                entry["fit"] = scale0.fit_const(ys[-2:])
                entry["comment"] = "saturate: last-two-rung const"
            elif form == "trend-only":
                entry["fit"] = scale0.fit_loglog(xs, ys)
                entry["comment"] = "effective exponent (r2<0.9: trend only)"
            fits.append(entry)
    print(f"FITS n={len(fits)}", flush=True)

    os.makedirs(args.outdir, exist_ok=True)
    with open(os.path.join(args.outdir, "matrix.json"), "w") as f:
        json.dump(rows, f)
    with open(os.path.join(args.outdir, "fits.json"), "w") as f:
        json.dump(fits, f)
    with open(os.path.join(args.outdir, "unresolved.json"), "w") as f:
        json.dump(unr, f)
    verdict = "SCALE0-BANKED" if not FAILS else "SCALE0-PARTIAL"
    with open(os.path.join(args.outdir, "verdict.json"), "w") as f:
        json.dump({"verdict": verdict, "fails": FAILS,
                   "n_cells": len(cells), "n_expected": len(expected),
                   "n_rows": len(rows), "n_unresolved": len(unr)}, f)
    print(f"VERDICT {verdict} fails={FAILS}", flush=True)


if __name__ == "__main__":
    main()