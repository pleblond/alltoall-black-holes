"""GEOM-ATTRACTOR-0 verdict analyzer (GEOMATTR0-PREREG gates + ladder).

Reads data/geomattr0/*.json (dim + aniso records), evaluates the frozen
instrument gates and the verdict ladder:

  GEOMATTR0-ROBUST3D / GEOMATTR0-3D / GEOMATTR0-DECOUPLED /
  GEOMATTR0-INTRINSIC2D / GEOMATTR0-NONGEOMETRIC / GEOMATTR0-INCOMPLETE

Writes verdict.json + diagnosis.json. Run on beast over the filed data.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from bh_graph import geomattr0 as g0


def _load(path):
    with open(path) as f:
        return json.load(f)


def _ok_num(x) -> bool:
    try:
        return x is not None and np.isfinite(float(x))
    except Exception:
        return False


def _med(vals):
    v = [float(x) for x in vals if _ok_num(x)]
    return float(np.median(v)) if v else float("nan")


def _num(x):
    return float(x) if _ok_num(x) else float("nan")


def b_part_medians(rec):
    """All-origin medians per r-window (needs >= 4 ok origins; A0-10 rule)."""
    out = {}
    for win in ("local", "glob", "xglob"):
        vals = [o[win]["d"] for o in rec["B_origins"].values()
                if o[win]["ok"]]
        out[win] = _med(vals) if len(vals) >= 4 else float("nan")
        out["n_" + win] = len(vals)
    return out


def c_part_vals(rec):
    """Heat-trace window readouts (NaN when UNMEASURABLE)."""
    out = {}
    for k in ("heat_local", "heat_glob", "heat_xglob"):
        r = rec[k]
        out[k] = float(r["d"]) if r["ok"] else float("nan")
    return out


def e_pass(b_glob, c_glob) -> bool:
    """Joint-lock gate E (headline windows, frozen D3WIN + DLOCK)."""
    lo, hi = g0.D3WIN
    return bool(_ok_num(b_glob) and _ok_num(c_glob)
                and lo <= b_glob <= hi and lo <= c_glob <= hi
                and abs(b_glob - c_glob) <= g0.DLOCK)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--measdir", default="data/geomattr0")
    ap.add_argument("--out", default="data/geomattr0_verdict.json")
    ap.add_argument("--diag", default="data/geomattr0_diagnosis.json")
    args = ap.parse_args()
    measdir = args.measdir

    verdict: dict = {}
    diag: dict = {}

    def _dim_path(tag):
        safe = "".join(c if c.isalnum() or c in ("-", "_") else "_"
                       for c in tag)
        return os.path.join(measdir, f"geomattr0_dim_{safe}.json")

    def _aniso_path(tag):
        safe = "".join(c if c.isalnum() or c in ("-", "_") else "_"
                       for c in tag)
        return os.path.join(measdir, f"geomattr0_aniso_{safe}.json")

    # ---- coverage ----
    missing = []
    for t in g0.dim_tags():
        if not os.path.exists(_dim_path(t)):
            missing.append(_dim_path(t))
    for t in g0.aniso_tags():
        if not os.path.exists(_aniso_path(t)):
            missing.append(_aniso_path(t))
    verdict["coverage_missing"] = missing
    verdict["coverage_ok"] = len(missing) == 0

    # ---- Stage A ----
    dims = {}
    for t in g0.dim_tags():
        p = _dim_path(t)
        dims[t] = _load(p) if os.path.exists(p) else None
    a_flags = {t: bool(r and r["stage_a"]["A_PASS"]) for t, r in dims.items()}
    verdict["A_PASS"] = bool(all(a_flags.values())) and verdict["coverage_ok"]
    verdict["A_fail"] = [t for t, v in a_flags.items() if not v]

    # ---- B/C readers ----
    b_med = {t: (b_part_medians(r) if r else
                 {"local": float("nan"), "glob": float("nan"),
                  "xglob": float("nan")}) for t, r in dims.items()}
    c_vals = {t: (c_part_vals(r) if r else
                  {"heat_local": float("nan"), "heat_glob": float("nan"),
                   "heat_xglob": float("nan")}) for t, r in dims.items()}

    # ---- control validation (WEAVE B-val/C-val, verbatim bars) ----
    d_c0l = b_med["c0-j2L44"]["local"]
    d_c0g = b_med["c0-j2L44"]["glob"]
    d_c4g = b_med["c4-cbL26"]["glob"]
    d_c3g = b_med["c3-j3L26"]["glob"]
    h_c0l = c_vals["c0-j2L44"]["heat_local"]
    h_c0g = c_vals["c0-j2L44"]["heat_glob"]
    h_c4g = c_vals["c4-cbL26"]["heat_glob"]
    h_c3g = c_vals["c3-j3L26"]["heat_glob"]
    lo2, hi2 = g0.D2WIN
    b_val2 = all(_ok_num(x) and lo2 <= x <= hi2 for x in (d_c0l, d_c0g))
    b_val3 = (_ok_num(d_c4g) and 2.20 <= d_c4g <= 3.30
              and _ok_num(d_c3g) and d_c3g > 2.20)
    c_val2 = all(_ok_num(x) and lo2 <= x <= hi2 for x in (h_c0l, h_c0g))
    c_val3 = (_ok_num(h_c4g) and 2.20 <= h_c4g <= 3.30
              and _ok_num(h_c3g) and h_c3g > 2.20)
    verdict["B_val"] = {"d_c0": [_num(d_c0l), _num(d_c0g)],
                        "d_c4g": _num(d_c4g), "d_c3g": _num(d_c3g),
                        "val2D": bool(b_val2), "val3D": bool(b_val3)}
    verdict["C_val"] = {"h_c0": [_num(h_c0l), _num(h_c0g)],
                        "h_c4g": _num(h_c4g), "h_c3g": _num(h_c3g),
                        "val2D": bool(c_val2), "val3D": bool(c_val3)}
    bc_valid = bool(b_val2 and b_val3 and c_val2 and c_val3)
    verdict["BC_valid"] = bc_valid

    # ---- A-repro (banked WEAVE values within REPRO_TOL; no WEAVE E) ----
    repro_rows = {}
    repro_ok = True
    for tag, bank in g0.WEAVE_BANKED.items():
        got = {"B_local": b_med[tag]["local"], "B_glob": b_med[tag]["glob"],
               "C_local": c_vals[tag]["heat_local"],
               "C_glob": c_vals[tag]["heat_glob"]}
        devs = {k: (abs(got[k] - bank[k]) if _ok_num(got[k]) else None)
                for k in bank}
        ok = all(v is not None and v <= g0.REPRO_TOL for v in devs.values())
        repro_rows[tag] = {"got": {k: _num(v) for k, v in got.items()},
                           "dev": devs, "ok": bool(ok)}
        repro_ok = repro_ok and ok
    weave_e = {t: e_pass(b_med[t]["glob"], c_vals[t]["heat_glob"])
               for t in ("c2-S16L24-lam001-s7", "c2-S16L24-lam002-s7",
                         "c2-S16L24-lam004-s7")}
    repro_ok = bool(repro_ok and not any(weave_e.values()))
    verdict["A_repro"] = {"rows": repro_rows, "weave_e": weave_e,
                          "pass": bool(repro_ok)}

    # ---- E per graph ----
    e_map = {t: e_pass(b_med[t]["glob"], c_vals[t]["heat_glob"])
             for t in g0.dim_tags()}

    def _nr(small, large) -> bool:
        b0, c0v = b_med[small]["glob"], c_vals[small]["heat_glob"]
        b1, c1v = b_med[large]["glob"], c_vals[large]["heat_glob"]
        if not all(_ok_num(x) for x in (b0, c0v, b1, c1v)):
            return False
        return bool(b1 >= b0 - g0.NORETREAT and c1 >= c0v - g0.NORETREAT)

    # ---- PH family ----
    S, L = g0.PH_SL_HEAD
    S2, L2 = g0.PH_SL_SCALE
    ph_head = [f"ph-S{S}L{L}-lam{g0.PH_LAM_HEAD}-s{sd}"
               for sd in g0.GEOM_SEEDS]
    ph_scale = [f"ph-S{S2}L{L2}-lam{g0.PH_LAM_HEAD}-s{sd}"
                for sd in g0.GEOM_SEEDS]
    ph_graphs = ph_head + ph_scale
    ph_e = [e_map[t] for t in ph_graphs]
    ph_nr = all(_nr(h, s) for h, s in zip(ph_head, ph_scale))
    ph_woven = all((dims[t] or {}).get("regime", {}).get("regime") == "WOVEN"
                   for t in ph_graphs)
    ph_core = bool(sum(ph_e) >= 3 and ph_nr and ph_woven)
    ph_def = f"ph-S{S}L{L}-lam{g0.PH_LAM_HEAD}-s{g0.GEOM_SEEDS[0]}-d5"
    ph_robust = bool(ph_core and e_map[ph_def])
    verdict["PH"] = {"e": {t: e_map[t] for t in ph_graphs},
                     "nr": bool(ph_nr), "woven": bool(ph_woven),
                     "core": bool(ph_core),
                     "defect_e": bool(e_map[ph_def]),
                     "robust": bool(ph_robust)}

    # ---- TPMS families ----
    tpm_out = {}
    for kind in g0.TPM_KINDS:
        bare_h = f"tpm-{kind}-L{g0.TPM_L_HEAD}"
        bare_s = f"tpm-{kind}-L{g0.TPM_L_SCALE}"
        inc_h = f"tpm-{kind}-inc-L{g0.TPM_L_HEAD}"
        inc_s = f"tpm-{kind}-inc-L{g0.TPM_L_SCALE}"
        inc_def = inc_h + "-d5"

        def _is2d(t):
            b, c = b_med[t]["glob"], c_vals[t]["heat_glob"]
            return bool(_ok_num(b) and _ok_num(c)
                        and lo2 <= b <= hi2 and lo2 <= c <= hi2)

        bare_2d = bool(_is2d(bare_h) and _is2d(bare_s))
        inc_e = bool(e_map[inc_h] and e_map[inc_s])
        nr = _nr(inc_h, inc_s)
        core = bool(bare_2d and inc_e and nr)
        robust = bool(core and e_map[inc_def])
        tpm_out[kind] = {"bare_2d": bare_2d,
                         "e": {inc_h: bool(e_map[inc_h]),
                               inc_s: bool(e_map[inc_s])},
                         "nr": bool(nr), "core": core,
                         "defect_e": bool(e_map[inc_def]),
                         "robust": robust,
                         "confounded": bool(not bare_2d)}
    verdict["TPM"] = tpm_out

    # ---- FOL family ----
    fol_h = f"fol-3ply-L{g0.FOL_L_HEAD}"
    fol_s = f"fol-3ply-L{g0.FOL_L_SCALE}"
    fol_def = fol_h + "-d5"
    fol_e = bool(e_map[fol_h] and e_map[fol_s])
    fol_nr = _nr(fol_h, fol_s)
    fol_core = bool(fol_e and fol_nr)
    fol_robust = bool(fol_core and e_map[fol_def])
    verdict["FOL"] = {"e": {fol_h: bool(e_map[fol_h]),
                            fol_s: bool(e_map[fol_s])},
                      "nr": bool(fol_nr), "core": bool(fol_core),
                      "defect_e": bool(e_map[fol_def]),
                      "robust": bool(fol_robust)}

    # ---- refusal (expanders must not lock) ----
    exp_e = {t: e_map[t] for t in ("c5-S16L24-lam004-s7",
                                   f"exp-N{g0.EXP_N}-s{g0.EXP_SEED}")}
    verdict["refusal"] = {"e": exp_e, "pass": bool(not any(exp_e.values()))}

    # ---- X-firewall ----
    here = os.path.dirname(__file__)
    fw_files = [os.path.join(here, "..", "src", "bh_graph", "geomattr0.py"),
                os.path.join(here, "geomattr0_campaign.py"),
                os.path.join(here, "geomattr0_analyze.py"),
                os.path.join(here, "..", "tests", "test_geomattr0.py")]
    fw_clean = {os.path.basename(p): g0.is_file_clean_ok(p) for p in fw_files}
    fw_ok = bool(all(fw_clean.values())
                 and g0.fitted_param_count() == 0
                 and g0.is_no_hidden_tuning_ok())
    verdict["X_firewall"] = {"clean": fw_clean,
                             "fitted": int(g0.fitted_param_count()),
                             "pass": bool(fw_ok)}

    # ---- aniso summary (G, secondary: filed, never verdict-gated) ----
    aniso = {}
    for t in g0.aniso_tags():
        p = _aniso_path(t)
        r = _load(p) if os.path.exists(p) else None
        aniso[t] = {"ratio": (r or {}).get("ratio"),
                    "n_good": (r or {}).get("n_good"),
                    "pref": (r or {}).get("pref"),
                    "e": bool(e_map.get(t, False))}
    verdict["aniso"] = aniso

    # ---- verdict ladder ----
    core_fams = []
    if ph_core:
        core_fams.append("PH")
    for kind in g0.TPM_KINDS:
        if tpm_out[kind]["core"]:
            core_fams.append(f"TPM-{kind}")
    if fol_core:
        core_fams.append("FOL")
    robust_fams = []
    if ph_robust:
        robust_fams.append("PH")
    for kind in g0.TPM_KINDS:
        if tpm_out[kind]["robust"]:
            robust_fams.append(f"TPM-{kind}")
    if fol_robust:
        robust_fams.append("FOL")
    verdict["core_fams"] = core_fams
    verdict["robust_fams"] = robust_fams

    reps = [f"ph-S{S}L{L}-lam{g0.PH_LAM_HEAD}-s{g0.GEOM_SEEDS[0]}",
            f"tpm-gyro-inc-L{g0.TPM_L_HEAD}",
            f"tpm-schwP-inc-L{g0.TPM_L_HEAD}",
            f"fol-3ply-L{g0.FOL_L_HEAD}"]

    def _decoupled(t):
        b, c = b_med[t]["glob"], c_vals[t]["heat_glob"]
        return bool(_ok_num(b) and _ok_num(c) and b >= 2.70 and c <= 2.60
                    and abs(b - c) > g0.DLOCK)

    def _intrinsic2d(t):
        b, c = b_med[t]["glob"], c_vals[t]["heat_glob"]
        return bool(_ok_num(b) and _ok_num(c)
                    and lo2 <= b <= hi2 and lo2 <= c <= hi2)

    def _nongeom(t):
        b, c = b_med[t]["glob"], c_vals[t]["heat_glob"]
        if not _ok_num(b) or not _ok_num(c):
            return True
        return bool(b > g0.NONGEOM_HI or c > g0.NONGEOM_HI)

    buckets = {"decoupled": [t for t in reps if _decoupled(t)],
               "intrinsic2d": [t for t in reps if _intrinsic2d(t)],
               "nongeom": [t for t in reps if _nongeom(t)]}
    verdict["buckets"] = buckets

    if (not verdict["A_PASS"]) or (not verdict["coverage_ok"]):
        headline, why = "GEOMATTR0-INCOMPLETE", "stage-A or coverage"
    elif not bc_valid:
        headline, why = "GEOMATTR0-INCOMPLETE", "B/C control validation"
    elif not repro_ok:
        headline, why = "GEOMATTR0-INCOMPLETE", "WEAVE repro failed"
    elif not verdict["refusal"]["pass"]:
        headline, why = "GEOMATTR0-INCOMPLETE", "expander refusal failed"
    elif not fw_ok:
        headline, why = "GEOMATTR0-INCOMPLETE", "firewall"
    elif robust_fams:
        headline = "GEOMATTR0-ROBUST3D"
        why = f"joint 3D + defect-robust: {robust_fams}"
    elif core_fams:
        headline = "GEOMATTR0-3D"
        why = f"joint 3D, robustness not earned: {core_fams}"
    elif len(buckets["decoupled"]) >= 3:
        headline, why = "GEOMATTR0-DECOUPLED", "WEAVE-like split, no lock"
    elif len(buckets["intrinsic2d"]) >= 3:
        headline, why = "GEOMATTR0-INTRINSIC2D", "stably 2D"
    elif len(buckets["nongeom"]) >= 3:
        headline, why = "GEOMATTR0-NONGEOMETRIC", "refuse/super-3D"
    else:
        headline, why = "GEOMATTR0-INCOMPLETE", "mixed/ambiguous, autopsy"
    verdict["headline"] = headline
    verdict["why"] = why

    diag.update({k: v for k, v in verdict.items()})
    diag["B_med"] = {t: {k: _num(v) if k in ("local", "glob", "xglob")
                         else v for k, v in m.items()}
                     for t, m in b_med.items()}
    diag["C_vals"] = {t: {k: _num(v) for k, v in m.items()}
                      for t, m in c_vals.items()}
    diag["E_map"] = {t: bool(v) for t, v in e_map.items()}
    diag["r_c"] = {t: (r or {}).get("r_c") for t, r in dims.items()}
    diag["t_c"] = {t: (r or {}).get("t_c") for t, r in dims.items()}
    with open(args.out, "w") as f:
        json.dump(_jsonable(verdict), f, indent=1, sort_keys=True)
    with open(args.diag, "w") as f:
        json.dump(_jsonable(diag), f, indent=1, sort_keys=True)
    print(f"headline: {headline} ({why})")


def _jsonable(o):
    if isinstance(o, dict):
        return {str(k): _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, np.ndarray):
        return [_jsonable(v) for v in o.tolist()]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        v = float(o)
        return v if np.isfinite(v) else None
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, float) and not np.isfinite(o):
        return None
    if isinstance(o, float) and (math.isnan(o) or math.isinf(o)):
        return None
    return o


if __name__ == "__main__":
    main()
