"""BH-Q-AREA-0 analyzer (FROZEN pre-data).

Reads data/bhqarea0/*.json, evaluates the preregistered gates, writes
freeze.json (P) FIRST, then comparison.json (Q), then verdict.json.
Order is enforced in code (freeze -> comparison -> verdict) and
re-verified by gates G-P/G-Q. Never crashes: gate errors file as red.
"""

from __future__ import annotations

import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np

from bh_graph import bhqarea0 as bq


def _load(outdir: str, name: str):
    with open(os.path.join(outdir, name)) as fh:
        return json.load(fh)


def _rel(a: float, b: float) -> float:
    return abs(a - b) / max(abs(a), abs(b), 1e-300)


def main(argv=None) -> int:
    outdir = sys.argv[1] if len(sys.argv) > 1 else "data/bhqarea0"
    gates: dict = {}
    notes: dict = {}

    def gate(name: str, ok: bool, note: str = ""):
        gates[name] = bool(ok)
        if note:
            notes[name] = note

    # ---- load ----
    rung_recs: dict = {}
    regression = audit = redundant = None
    load_err = []
    try:
        for r in bq.R_LADDER:
            for st in bq.HEADLINE_STATES:
                rung_recs[("headline", st, r)] = _load(
                    outdir, f"rung_headline_{st}_r{int(r):02d}.json")
        for r in bq.R_LADDER:
            rung_recs[("control", "vacuum", r)] = _load(
                outdir, f"rung_control_vacuum_r{int(r):02d}.json")
        regression = _load(outdir, "regression.json")
        audit = _load(outdir, "audit.json")
        redundant = _load(outdir, "redundant.json")
    except Exception as exc:  # noqa: BLE001 - filed, never raised
        load_err.append(f"{type(exc).__name__}: {exc}")

    n_rung = len(rung_recs)
    gate("G-INST", not load_err and n_rung == 50
         and regression is not None and audit is not None
         and redundant is not None,
         f"rung={n_rung}/50 err={load_err}")

    hv = lambda r: rung_recs.get(("headline", "vacuum", r))  # noqa: E731
    cv = lambda r: rung_recs.get(("control", "vacuum", r))  # noqa: E731

    # ---- A/B/C/D ----
    try:
        gate("G-A", bool(regression["formula_ok"]))
        gate("G-B", bool(regression["endpoints_ok"]))
        gate("G-C", bool(regression["expansion_ok"]))
        d_ok = bool(regression["core_generator_ok"]) and all(
            regression["geometry_ok"].values()) and \
            regression["margin"] == bq.MARGIN and \
            list(regression["ladder"]) == list(bq.R_LADDER)
        gate("G-D", d_ok)
    except Exception as exc:  # noqa: BLE001
        for g in ("G-A", "G-B", "G-C", "G-D"):
            gate(g, False, f"eval-error: {exc}")

    # ---- E: sigma stability (headline vacuum geometry) ----
    try:
        sig = [hv(r)["sigma"] for r in bq.TOP_RUNGS]
        e_ok = _rel(sig[2], sig[1]) < bq.BAR_REL and \
            _rel(sig[1], sig[0]) < bq.BAR_REL
        gate("G-E", e_ok, f"sigma_top3={sig}")
        sigma_star = float(hv(10)["sigma"])
    except Exception as exc:  # noqa: BLE001
        gate("G-E", False, f"eval-error: {exc}")
        sigma_star = None

    # ---- F: census completeness + summary re-verification ----
    try:
        f_ok = True
        f_notes = []
        for key, rec in sorted(rung_recs.items(), key=str):
            xs = rec["xs"]
            if rec["n_defined"] + rec["zero_pairs"] != rec["n_bnd"]:
                f_ok = False
                f_notes.append(f"{key}: count-split")
            if rec["n_bnd"] != rec["dim3_cut"]:
                f_ok = False
                f_notes.append(f"{key}: cut-mismatch")
            if len(xs) != rec["n_defined"]:
                f_ok = False
                f_notes.append(f"{key}: xs-len")
            if xs:
                arr = np.asarray(xs, dtype=float)
                chk = {"mean": float(np.mean(arr)),
                       "median": float(np.median(arr)),
                       "var": float(np.var(arr)),
                       "meansq": float(np.mean(arr ** 2))}
                for k, v in chk.items():
                    if abs(v - rec["stats"][k]) > bq.CENSUS_ATOL:
                        f_ok = False
                        f_notes.append(f"{key}: {k}-mismatch")
                qs = np.quantile(arr, list(bq.QUANTILES))
                for got, want in zip(qs, rec["stats"]["quantiles"]):
                    if abs(float(got) - float(want)) > bq.CENSUS_ATOL:
                        f_ok = False
                        f_notes.append(f"{key}: q-mismatch")
                        break
        gate("G-F", f_ok, "; ".join(f_notes[:5]))
    except Exception as exc:  # noqa: BLE001
        gate("G-F", False, f"eval-error: {exc}")

    # ---- G: distribution limit (headline vacuum) ----
    g_branch = "UNRESOLVED"
    try:
        x8, x9, x10 = hv(8)["xs"], hv(9)["xs"], hv(10)["xs"]
        ks89 = bq.ks_distance(x8, x9)
        ks910 = bq.ks_distance(x9, x10)
        means = [float(np.mean(np.abs(hv(r)["xs"]))) for r in (7, 8, 9, 10)]
        stds = [float(np.std(np.asarray(hv(r)["xs"]))) for r in (7, 8, 9, 10)]
        if ks89 < bq.BAR_KS and ks910 < bq.BAR_KS:
            g_branch = "CONVERGED"
        elif (means[3] < means[2] < means[1] < means[0]
              and stds[3] < stds[2] < stds[1] < stds[0]
              and stds[3] < bq.BAR_COLLAPSE_STD):
            g_branch = "COLLAPSED"
        gate("G-G", True, f"branch={g_branch} ks89={ks89:.4f} "
                          f"ks910={ks910:.4f} std10={stds[3]:.2e}")
    except Exception as exc:  # noqa: BLE001
        gate("G-G", False, f"eval-error: {exc}")

    # ---- H/I: hbar stability + classification ----
    h_class = "UNRESOLVED"
    h_star = None
    try:
        h8, h9, h10 = hv(8)["hbar"], hv(9)["hbar"], hv(10)["hbar"]
        h_ok = abs(h10 - h9) < bq.BAR_H_ABS_1 and \
            abs(h9 - h8) < bq.BAR_H_ABS_2
        gate("G-H", h_ok, f"hbar_top3={[h8, h9, h10]}")
        h_star = float(h10)
        if h_ok:
            if h10 > 0.99:
                h_class = "MAX"
            elif h10 >= 0.01:
                h_class = "NONMAX"
            else:
                h_class = "ZERO"
        gate("G-I", True, f"class={h_class}")
    except Exception as exc:  # noqa: BLE001
        gate("G-H", False, f"eval-error: {exc}")
        gate("G-I", False, f"eval-error: {exc}")

    # ---- J: deficit agreement ----
    try:
        j_ok = True
        j_notes = []
        for r in bq.R_LADDER:
            rec = hv(r)
            if rec["delta_dom_n"] >= 10:
                denom = max(rec["delta"], 1e-9)
                rel = abs(rec["delta"] - rec["delta2"]) / denom
                if rel >= bq.BAR_J_REL:
                    j_ok = False
                    j_notes.append(f"r{r}: rel={rel:.3g}")
            else:
                j_notes.append(f"r{r}: VACUOUS(n={rec['delta_dom_n']})")
        gate("G-J", j_ok, "; ".join(j_notes[:6]))
    except Exception as exc:  # noqa: BLE001
        gate("G-J", False, f"eval-error: {exc}")

    # ---- K: direct vs factorized ----
    try:
        k_ok = True
        for key, rec in rung_recs.items():
            if abs(rec["kappa"] - rec["kappa_fact"]) > \
                    bq.BAR_K_REL * max(1.0, abs(rec["kappa"])):
                k_ok = False
                notes["G-K"] = f"mismatch at {key}"
                break
        gate("G-K", k_ok)
    except Exception as exc:  # noqa: BLE001
        gate("G-K", False, f"eval-error: {exc}")

    # ---- L: kappa stability ----
    kappa_star = None
    try:
        k8, k9, k10 = hv(8)["kappa"], hv(9)["kappa"], hv(10)["kappa"]
        l_ok = (_rel(k10, k9) < bq.BAR_REL
                and _rel(k9, k8) < bq.BAR_REL) or \
            (k10 < bq.BAR_KAPPA_ZERO
             and abs(k10 - k9) < bq.BAR_KAPPA_ZERO_ABS
             and abs(k9 - k8) < bq.BAR_KAPPA_ZERO_ABS)
        gate("G-L", l_ok, f"kappa_top3={[k8, k9, k10]}")
        kappa_star = float(k10)
    except Exception as exc:  # noqa: BLE001
        gate("G-L", False, f"eval-error: {exc}")

    # ---- M: volume control ----
    try:
        v8, v9, v10 = (hv(8)["vol_ratio"], hv(9)["vol_ratio"],
                       hv(10)["vol_ratio"])
        v1 = hv(1)["vol_ratio"]
        allv = [hv(r)["vol_ratio"] for r in bq.R_LADDER]
        m_ok = (v10 < v9 < v8 and v10 < v1 / 2.0) or \
            all(v < bq.BAR_M_ZERO for v in allv)
        gate("G-M", m_ok, f"vol_top3={[v8, v9, v10]} v1={v1}")
    except Exception as exc:  # noqa: BLE001
        gate("G-M", False, f"eval-error: {exc}")

    # ---- N: audit completeness ----
    try:
        n_ok = all("dup_groups" in rec and "dup_edges" in rec
                   and "uniq_sum" in rec for rec in rung_recs.values())
        tot_dup = sum(rec["dup_edges"] for rec in rung_recs.values())
        gate("G-N", n_ok, f"total_dup_edges={tot_dup}")
    except Exception as exc:  # noqa: BLE001
        gate("G-N", False, f"eval-error: {exc}")

    # ---- O: firewall + params ----
    try:
        gate("G-O", bool(audit["firewall_ok"])
             and audit["fitted_params"] == 0
             and bool(audit["battery_counts_ok"]))
    except Exception as exc:  # noqa: BLE001
        gate("G-O", False, f"eval-error: {exc}")

    # ---- S/T presence ----
    try:
        gate("G-S", all(("headline", st, r) in rung_recs
                        for st in bq.HEADLINE_STATES for r in bq.R_LADDER))
        gate("G-T", all(("control", "vacuum", r) in rung_recs
                        for r in bq.R_LADDER))
    except Exception as exc:  # noqa: BLE001
        gate("G-S", False, f"eval-error: {exc}")
        gate("G-T", False, f"eval-error: {exc}")

    # ---- DET: redundant determinism ----
    try:
        import hashlib as _hl

        det_ok = True
        pairs = [(5, "headline", "vacuum"), (5, "control", "vacuum")]
        for i, (r, var, stt) in enumerate(pairs):
            rec = dict(rung_recs[(var, stt, r)])
            rec.pop("kind", None)
            blob = json.dumps(rec, sort_keys=True, allow_nan=False)
            h = _hl.sha256(blob.encode()).hexdigest()
            if h != redundant["hashes"][i]:
                det_ok = False
        gate("G-DET", det_ok)
    except Exception as exc:  # noqa: BLE001
        gate("G-DET", False, f"eval-error: {exc}")

    # ---- POW: exponent ----
    pow_p = None
    try:
        areas = [hv(r)["area"] for r in bq.POW_RUNGS]
        svals = [hv(r)["S"] for r in bq.POW_RUNGS]
        if all(v > 0 for v in svals):
            pow_p = bq.power_exponent(areas, svals)
            gate("G-POW", True, f"p={pow_p:.4f}")
        else:
            gate("G-POW", True, "non-positive S; exponent undefined")
    except Exception as exc:  # noqa: BLE001
        gate("G-POW", False, f"eval-error: {exc}")

    # ================= FREEZE (P) FIRST =================
    freeze = {
        "campaign": "BH-Q-AREA-0",
        "frozen_at": time.time(),
        "kappa_star": kappa_star,
        "sigma_star": sigma_star,
        "h_star": h_star,
        "class": h_class,
        "g_branch": g_branch,
        "ladder": list(bq.R_LADDER),
        "margin": bq.MARGIN,
        "input_hashes": (audit["input_hashes"] if audit else None),
    }
    with open(os.path.join(outdir, "freeze.json"), "w") as fh:
        json.dump(freeze, fh, allow_nan=False)
        fh.write("\n")

    # ================= COMPARISON (Q) AFTER FREEZE =================
    g_val = sigma_star  # sigma* = g/a^2 in a = 1 units
    if g_val is not None and h_star is not None and h_star > 0:
        a_over_lp = 2.0 * math.sqrt(g_val * h_star * math.log(2.0))
    else:
        a_over_lp = None
    if h_class == "MAX" and g_val is not None:
        a_over_lp_max = 2.0 * math.sqrt(g_val * math.log(2.0))
        a_over_lp_g1 = 2.0 * math.sqrt(math.log(2.0))
    else:
        a_over_lp_max = None
        a_over_lp_g1 = None
    comparison = {
        "campaign": "BH-Q-AREA-0",
        "post_freeze": True,
        "kappa_BH_formula": "1/(4 lp^2 ln2) bits per unit area",
        "conditional": "a = 2 lp sqrt(g h_* ln2); sigma* = g/a^2",
        "g_a1": g_val,
        "a_over_lp": a_over_lp,
        "max_case": {"a_over_lp": a_over_lp_max,
                     "a_over_lp_g1": a_over_lp_g1},
        "claim": False,
        "claim_note": ("graph length a is not independently known; "
                       "no coefficient-agreement claim is made"),
    }
    with open(os.path.join(outdir, "comparison.json"), "w") as fh:
        json.dump(comparison, fh, allow_nan=False)
        fh.write("\n")

    # ---- G-P / G-Q order + hash checks ----
    try:
        fr = _load(outdir, "freeze.json")
        cp = _load(outdir, "comparison.json")
        mt_f = os.path.getmtime(os.path.join(outdir, "freeze.json"))
        mt_c = os.path.getmtime(os.path.join(outdir, "comparison.json"))
        p_ok = mt_f <= mt_c and \
            fr["input_hashes"] == audit["input_hashes"] and \
            all(k in fr for k in ("kappa_star", "sigma_star", "h_star",
                                  "class", "ladder"))
        gate("G-P", p_ok)
        gate("G-Q", bool(cp.get("post_freeze")) and cp.get("claim") is False)
    except Exception as exc:  # noqa: BLE001
        gate("G-P", False, f"eval-error: {exc}")
        gate("G-Q", False, f"eval-error: {exc}")

    # ---- verdict ----
    required = ["G-INST", "G-A", "G-B", "G-C", "G-D", "G-F", "G-K", "G-O",
                "G-P", "G-DET"]
    pow_outside = pow_p is not None and not (
        bq.BAR_POW[0] <= pow_p <= bq.BAR_POW[1])
    if any(not gates.get(g) for g in required):
        verdict = "BHQAREA0-INCOMPLETE"
    elif not gates.get("G-E") or pow_outside:
        verdict = "BHQAREA0-NOTAREA"
    elif g_branch == "UNRESOLVED" or not gates.get("G-H") or \
            not gates.get("G-L"):
        verdict = "BHQAREA0-NONUNIVERSAL"
    elif not gates.get("G-M") or not gates.get("G-J") or \
            not gates.get("G-S") or not gates.get("G-T"):
        verdict = "BHQAREA0-NONUNIVERSAL"
    elif h_class == "MAX":
        verdict = "BHQAREA0-MAX"
    elif h_class == "NONMAX":
        verdict = "BHQAREA0-AREA"
    elif h_class == "ZERO":
        verdict = "BHQAREA0-ZERO"
    else:
        verdict = "BHQAREA0-NONUNIVERSAL"

    verdict_doc = {
        "campaign": "BH-Q-AREA-0",
        "verdict": verdict,
        "gates": gates,
        "notes": notes,
        "freeze": freeze,
        "comparison": comparison,
        "power_p": pow_p,
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
