"""CROSS-IMPL-A analyzer (FROZEN pre-data).

Reads data/crossa/*.json, evaluates the preregistered gates CROSSA-A..I/X
plus determinism and MAX reproduction, classifies R2/C2/X2/Gamma via the
frozen convergence rules, writes verdict.json. Never crashes: gate errors
file as red -> CROSSA-INCOMPLETE.
"""

from __future__ import annotations

import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np

from bh_graph import crossa as cx


def _load(outdir: str, name: str):
    with open(os.path.join(outdir, name)) as fh:
        return json.load(fh)


def main(argv=None) -> int:
    outdir = sys.argv[1] if len(sys.argv) > 1 else "data/crossa"
    gates: dict = {}
    notes: dict = {}

    def gate(name: str, ok: bool, note: str = ""):
        gates[name] = bool(ok)
        if note:
            notes[name] = note

    rung_recs: dict = {}
    regression = audit = redundant = None
    load_err = []
    try:
        for r in cx.R_LADDER:
            for st in cx.HEADLINE_STATES:
                rung_recs[("headline", st, r)] = _load(
                    outdir, f"rung_headline_{st}_r{int(r):02d}.json")
        for r in cx.R_LADDER:
            rung_recs[("control", "vacuum", r)] = _load(
                outdir, f"rung_control_vacuum_r{int(r):02d}.json")
        regression = _load(outdir, "regression.json")
        audit = _load(outdir, "audit.json")
        redundant = _load(outdir, "redundant.json")
    except Exception as exc:
        load_err.append(f"{type(exc).__name__}: {exc}")

    n_rung = len(rung_recs)
    gate("CROSSA-INST", not load_err and n_rung == 50
         and regression is not None and audit is not None
         and redundant is not None,
         f"rung={n_rung}/50 err={load_err}")

    hv = lambda r: rung_recs.get(("headline", "vacuum", r))
    cv = lambda r: rung_recs.get(("control", "vacuum", r))

    # ---- A: bank provenance ----
    try:
        gate("CROSSA-A", bool(regression["provenance_ok"])
             and bool(regression["provenance"]["ok"])
             and bool(regression["convergence_rules_ok"]),
             f"provenance_ok={regression.get('provenance_ok')}")
    except Exception as exc:
        gate("CROSSA-A", False, f"eval-error: {exc}")

    # ---- B: pointwise identity + banked reproduction ----
    try:
        b_ok = bool(regression["factor_identity_ok"])
        b_notes = []
        if not b_ok:
            b_notes.append("factor_identity red")
        max_err = 0.0
        worst_xs = 0.0
        worst_s = 0.0
        for key, rec in rung_recs.items():
            err = float(rec.get("max_ident_err", 1e18))
            max_err = max(max_err, err)
            if err > cx.BAR_FP:
                b_ok = False
                b_notes.append(f"{key}: ident_err={err:.3g}")
                break
            banked = rec.get("banked", {})
            if not banked.get("present"):
                b_ok = False
                b_notes.append(f"{key}: bank missing")
                break
            if not banked.get("psi_match"):
                b_ok = False
                b_notes.append(f"{key}: psi mismatch")
                break
            if not banked.get("n_bnd_match"):
                b_ok = False
                b_notes.append(f"{key}: n_bnd mismatch")
                break
            xd = banked.get("xs_max_diff")
            if xd is None or float(xd) > cx.BAR_FP:
                b_ok = False
                b_notes.append(f"{key}: xs_diff={xd}")
                break
            worst_xs = max(worst_xs, float(xd))
            sd = float(banked.get("S_diff", 1e18))
            worst_s = max(worst_s, sd)
            if sd > cx.BAR_CENSUS * max(1.0, float(rec.get("n_bnd", 1))):
                b_ok = False
                b_notes.append(f"{key}: S_diff={sd:.3g}")
                break
        if not b_notes:
            b_notes.append(f"max_ident={max_err:.3g} "
                           f"max_xs={worst_xs:.3g} max_S={worst_s:.3g}")
        gate("CROSSA-B", b_ok, "; ".join(b_notes[:3]))
    except Exception as exc:
        gate("CROSSA-B", False, f"eval-error: {exc}")

    # ---- C: endpoint handling ----
    try:
        c_ok = True
        c_notes = []
        tot_q0 = tot_e = 0
        for key, rec in rung_recs.items():
            r_list = rec["r_list"]
            c_list = rec["c_list"]
            x_list = rec["x_list"]
            n_bnd = rec["n_bnd"]
            if not (len(r_list) == len(c_list) == len(x_list) == n_bnd):
                c_ok = False
                c_notes.append(f"{key}: array-len")
                break
            n_q0 = rec["n_q0"]
            n_ai0 = rec["n_ai0"]
            n_aj0 = rec["n_aj0"]
            n_ok = rec["n_ok"]
            if n_q0 + n_ai0 + n_aj0 + n_ok != n_bnd:
                c_ok = False
                c_notes.append(f"{key}: endpoint-split")
                break
            tot_q0 += n_q0
            tot_e += n_ai0 + n_aj0
            for rv, cvv, xv in zip(r_list, c_list, x_list):
                if cvv is None:
                    if rv != 0.0:
                        c_ok = False
                        c_notes.append(f"{key}: r!=0 with c None")
                        break
                    if xv is not None and xv != 0.0:
                        c_ok = False
                        c_notes.append(f"{key}: x!=0 with c None")
                        break
                else:
                    if not (-1.0 - 1e-9 <= cvv <= 1.0 + 1e-9):
                        c_ok = False
                        c_notes.append(f"{key}: c-range")
                        break
                    if not (0.0 <= rv <= 1.0 + 1e-9):
                        c_ok = False
                        c_notes.append(f"{key}: r-range")
                        break
            if not c_ok:
                break
            want_f = float((n_q0 + n_ai0 + n_aj0) / n_bnd) if n_bnd else 0.0
            if abs(float(rec["f_r0"]) - want_f) > cx.BAR_CENSUS:
                c_ok = False
                c_notes.append(f"{key}: f_r0")
                break
        if not c_notes:
            c_notes.append(f"q0={tot_q0} ai_aj_zero={tot_e}")
        gate("CROSSA-C", c_ok, "; ".join(c_notes[:3]))
    except Exception as exc:
        gate("CROSSA-C", False, f"eval-error: {exc}")

    # ---- D/E/F: anatomy recompute ----
    try:
        d_ok = True
        d_notes = []
        for key, rec in rung_recs.items():
            r_list = [float(v) for v in rec["r_list"]]
            c_list = rec["c_list"]
            x_list = rec["x_list"]
            n_bnd = rec["n_bnd"]
            r2_chk = float(np.mean(np.asarray(r_list) ** 2))
            if abs(r2_chk - float(rec["R2"])) > cx.BAR_CENSUS:
                d_ok = False
                d_notes.append(f"{key}: R2")
                break
            if abs(float(np.mean(r_list)) - float(rec["mean_r"])) \
                    > cx.BAR_CENSUS:
                d_ok = False
                d_notes.append(f"{key}: mean_r")
                break
            if abs(float(np.median(r_list)) - float(rec["median_r"])) \
                    > cx.BAR_CENSUS:
                d_ok = False
                d_notes.append(f"{key}: median_r")
                break
            c_vals = [float(v) for v in c_list if v is not None]
            if len(c_vals) != rec["n_phase_defined"]:
                d_ok = False
                d_notes.append(f"{key}: n_phase")
                break
            if c_vals:
                c2_chk = float(np.mean(np.asarray(c_vals) ** 2))
                if rec["C2"] is None or abs(c2_chk - float(rec["C2"])) \
                        > cx.BAR_CENSUS:
                    d_ok = False
                    d_notes.append(f"{key}: C2")
                    break
                if abs(float(np.mean(c_vals)) - float(rec["mean_c"])) \
                        > cx.BAR_CENSUS:
                    d_ok = False
                    d_notes.append(f"{key}: mean_c")
                    break
            elif rec["C2"] is not None:
                d_ok = False
                d_notes.append(f"{key}: C2-None")
                break
            x2_vals = []
            for rv, cvv in zip(r_list, c_list):
                if cvv is None:
                    x2_vals.append(0.0)
                else:
                    x2_vals.append(float(rv ** 2 * cvv ** 2))
            x2_chk = float(np.mean(x2_vals))
            if abs(x2_chk - float(rec["X2"])) > cx.BAR_CENSUS:
                d_ok = False
                d_notes.append(f"{key}: X2")
                break
            r2m = float(rec["R2"])
            c2m = rec["C2"]
            if r2m > 0.0 and c2m is not None and float(c2m) > 0.0:
                g_chk = float(x2_chk / (r2m * float(c2m)))
                if rec["Gamma"] is None or abs(g_chk - float(rec["Gamma"])) \
                        > 1e-6:
                    d_ok = False
                    d_notes.append(f"{key}: Gamma")
                    break
            elif rec["Gamma"] is not None:
                d_ok = False
                d_notes.append(f"{key}: Gamma-None")
                break
            both = sum(1 for rv, cvv in zip(r_list, c_list)
                       if rv > cx.R_HI and cvv is not None
                       and abs(cvv) > cx.C_HI)
            if both != rec["joint_both_hi"]:
                d_ok = False
                d_notes.append(f"{key}: joint")
                break
            if rec["joint_both_hi"] + rec["joint_r_hi"] \
                    + rec["joint_c_hi"] + rec["joint_neither"] != n_bnd:
                d_ok = False
                d_notes.append(f"{key}: joint-split")
                break
            _ = x_list
        gate("CROSSA-DEF", d_ok, "; ".join(d_notes[:3]) or "recompute ok")
    except Exception as exc:
        gate("CROSSA-DEF", False, f"eval-error: {exc}")

    # ---- G: deficit reconstruction ----
    try:
        g_ok = True
        g_notes = []
        if not regression.get("deficit_expansion_ok"):
            g_ok = False
            g_notes.append("expansion red")
        for r in cx.R_LADDER:
            rec = hv(r)
            dom = rec["dom_n"]
            if dom >= 10:
                dnum = float(rec["dom_delta"])
                dden = float(rec["dom_delta2"])
                rel = abs(dnum - dden) / max(dnum, 1e-9)
                if rel >= cx.BAR_J_REL:
                    g_ok = False
                    g_notes.append(f"r{r}: rel={rel:.3g}")
            else:
                g_notes.append(f"r{r}: VACUOUS(n={dom})")
        gate("CROSSA-G", g_ok, "; ".join(g_notes[:6]) or "deficit ok")
    except Exception as exc:
        gate("CROSSA-G", False, f"eval-error: {exc}")

    # ---- H: asymptotic attribution ----
    tracks = {}
    ladders = {}
    try:
        for tag, ext in (("R2", "R2"), ("C2", "C2"),
                         ("X2", "X2"), ("Gamma", "Gamma")):
            seq = []
            for r in cx.R_LADDER:
                v = hv(r)[ext]
                seq.append(None if v is None else float(v))
            ladders[tag] = seq
            tracks[tag] = cx.classify_track(
                {rr: vv for rr, vv in zip(cx.R_LADDER, seq)})
        h_ok = all(t in (cx.TRACK_ZERO, cx.TRACK_NONZERO,
                         cx.TRACK_UNRESOLVED)
                   for t in tracks.values())
        gate("CROSSA-H", h_ok, f"tracks={tracks}")
    except Exception as exc:
        gate("CROSSA-H", False, f"eval-error: {exc}")
        tracks = {"R2": "ERROR", "C2": "ERROR",
                  "X2": "ERROR", "Gamma": "ERROR"}

    # ---- I: state controls ----
    try:
        i_ok = True
        i_notes = []
        for r in cx.R_LADDER:
            if cv(r) is None:
                i_ok = False
                i_notes.append(f"r{r}: control missing")
                break
            vp = rung_recs.get(("headline", "vplus", r))
            if vp is None:
                i_ok = False
                i_notes.append(f"r{r}: vplus missing")
                break
            if abs(float(vp["S_repro"]) - 0.0) > cx.BAR_CENSUS:
                i_ok = False
                i_notes.append(f"r{r}: vplus S!=0")
                break
            if abs(float(vp["banked"].get("bank_S", 1e18)) - 0.0) \
                    > cx.BAR_CENSUS:
                i_ok = False
                i_notes.append(f"r{r}: vplus bank S!=0")
                break
        if not i_notes:
            ch = [float(cv(r)["hbar_repro"]) for r in cx.R_LADDER]
            i_notes.append(f"control_hbar10={ch[-1]:.4f}")
        gate("CROSSA-I", i_ok, "; ".join(i_notes[:3]))
    except Exception as exc:
        gate("CROSSA-I", False, f"eval-error: {exc}")

    # ---- X: firewall + params + counts ----
    try:
        import inspect as _inspect

        paths_ok = bool(cx.is_file_clean_ok(cx.__file__))
        try:
            camp_path = os.path.join(os.path.dirname(__file__),
                                     "crossa_campaign.py")
            ana_path = os.path.join(os.path.dirname(__file__),
                                    "crossa_analyze.py")
            paths_ok = bool(paths_ok
                            and cx.is_file_clean_ok(camp_path)
                            and cx.is_file_clean_ok(ana_path))
        except Exception:
            paths_ok = False
        _ = _inspect
        gate("CROSSA-X", bool(audit["firewall_ok"])
             and audit["fitted_params"] == 0
             and bool(audit["battery_counts_ok"])
             and paths_ok)
    except Exception as exc:
        gate("CROSSA-X", False, f"eval-error: {exc}")

    # ---- DET: redundant determinism ----
    try:
        import hashlib as _hl

        det_ok = True
        pairs = [(5, "headline", "vacuum"), (5, "control", "vacuum")]
        for i, (r, var, stt) in enumerate(pairs):
            rec = dict(rung_recs[(var, stt, r)])
            rec.pop("kind", None)
            rec.pop("_git", None)
            blob = json.dumps(rec, sort_keys=True, allow_nan=False)
            h = _hl.sha256(blob.encode()).hexdigest()
            if h != redundant["hashes"][i]:
                det_ok = False
        gate("CROSSA-DET", det_ok)
    except Exception as exc:
        gate("CROSSA-DET", False, f"eval-error: {exc}")

    # ---- MAX reproduction ----
    try:
        h10 = float(hv(10)["hbar_repro"])
        h9 = float(hv(9)["hbar_repro"])
        h8 = float(hv(8)["hbar_repro"])
        m_ok = h10 > 0.99 and abs(h10 - h9) < 0.01 \
            and abs(h9 - h8) < 0.015
        gate("CROSSA-MAX", m_ok, f"hbar_top3={[h8, h9, h10]}")
    except Exception as exc:
        gate("CROSSA-MAX", False, f"eval-error: {exc}")

    # ---- verdict ----
    required = ["CROSSA-INST", "CROSSA-A", "CROSSA-B", "CROSSA-C",
                "CROSSA-DEF", "CROSSA-G", "CROSSA-H", "CROSSA-I",
                "CROSSA-X", "CROSSA-DET", "CROSSA-MAX"]
    r_t = tracks.get("R2")
    c_t = tracks.get("C2")
    x_t = tracks.get("X2")
    g_t = tracks.get("Gamma")
    if any(not gates.get(g) for g in required):
        verdict = "CROSSA-INCOMPLETE"
        reason = f"instrument red: {[g for g in required if not gates.get(g)]}"
    elif c_t == cx.TRACK_ZERO and r_t == cx.TRACK_NONZERO \
            and x_t == cx.TRACK_ZERO:
        verdict = "CROSSA-QUADRATURE"
        reason = f"C2->0, R2 bounded away, X2->0 {tracks}"
    elif r_t == cx.TRACK_ZERO and c_t == cx.TRACK_NONZERO \
            and x_t == cx.TRACK_ZERO:
        verdict = "CROSSA-SCALE"
        reason = f"R2->0, C2 bounded away, X2->0 {tracks}"
    elif r_t == cx.TRACK_ZERO and c_t == cx.TRACK_ZERO \
            and x_t == cx.TRACK_ZERO:
        verdict = "CROSSA-MIXED"
        reason = f"R2->0 and C2->0, X2->0 {tracks}"
    elif r_t == cx.TRACK_NONZERO and c_t == cx.TRACK_NONZERO \
            and x_t == cx.TRACK_ZERO and g_t == cx.TRACK_ZERO:
        verdict = "CROSSA-COVARIANT"
        reason = f"marginals bounded away, X2->0, Gamma->0 {tracks}"
    else:
        verdict = "CROSSA-NONASYMPTOTIC"
        reason = (f"MAX reproduces but no frozen classification {tracks}; "
                  f"ladders filed descriptively")
    verdict_doc = {
        "campaign": "CROSS-IMPL-A",
        "verdict": verdict,
        "reason": reason,
        "gates": gates,
        "notes": notes,
        "tracks": tracks,
        "ladders": ladders,
    }
    with open(os.path.join(outdir, "verdict.json"), "w") as fh:
        json.dump(verdict_doc, fh, allow_nan=False)
        fh.write("\n")
    print(f"VERDICT {verdict}", flush=True)
    red = [g for g, v in gates.items() if not v]
    print(f"GATES {sum(gates.values())}/{len(gates)} red={red}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
