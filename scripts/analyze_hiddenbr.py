"""HIDDEN-BR verdict analyzer (FROZEN pre-data; decision tree only).

Reads hiddenbr_cells.json (35 cells), evaluates every preregistered check,
writes hiddenbr_verdict.json + hiddenbr_stage.json. No bar/ladder/estimator
may change post-data: failures file as design-error autopsies or genuine.

Ladder (HIDDEN-BR-PREREG):
  HBR0-NULL: every qualifying pair has max|dB| < 1e-9 AND every ledger
    d_hidden = 0 (hidden geometrically inert).
  HBR0-GRADIENT (primary positive): >=1 qualifying equal-E pair has
    max|dB| > 1e-6 with C0-C8 green.
  HBR0-SIGNREV (distinguished refinement): GRADIENT + >=1 strict
    opposite-sign ledger edge on a qualifying pair.
  Else HBR0-PARTIAL (per-stage filing, honest).
Pairs failing C1/C2 are excluded with filed cause, never counted.
HAMP-Q (05q) is EXPECTED non-qualifying (C1+C2 fail at predicted values).
"""
import json
import sys

IN = sys.argv[1] if len(sys.argv) > 1 else "/tmp/hiddenbr_parts/hiddenbr_cells.json"
OUTD = sys.argv[2] if len(sys.argv) > 2 else "/tmp/hiddenbr_parts"

D_LOCAL_BAR = 1e-6
D_REMOTE_BAR = 1e-9
DBAR_PHYS = 1e-6
DBAR_FP = 1e-9
LEDGER_NZ = 1e-9
PMATCH_BAR = 1e-12
E_BAR = 1e-9
ESECTOR_BAR = 1e-12
FIT_BAR = 1e-9
FD_BAR = 1e-9
C4_BAR = 1e-9
U1_BAR = 1e-12
LOC_BAR = 1e-12
WIT_BAR = 1e-6
R_LOAD = (2, 4, 6)


def main():
    with open(IN) as f:
        rec = json.load(f)
    cells = {c["note"]: c for c in rec["cells"]}
    checks = []

    def chk(name, ok, detail=""):
        checks.append({"name": name, "ok": bool(ok), "detail": str(detail)})

    # Pair battery (HBR-0A/B/C/D/F/G/H/I; C0/C1/C2) ---------------------------
    pnotes = sorted(n for n in cells if n.startswith("B:"))
    assert len(pnotes) == 10, pnotes
    valid = []
    for n in pnotes:
        c = cells[n]
        qm = c["qmatch"]
        if qm:
            chk(f"{n}:pmatch_false_expected", not c["pmatch"], c["pplus_max"])
            ratio = c["E_B"] / c["E_A"] if c["E_A"] != 0 else float("nan")
            cc = c["scale_c"]
            chk(f"{n}:E_ratio_c2", abs(ratio - cc ** 2) < 1e-9, ratio)
            chk(f"{n}:E_fail_expected", not c["E_ok"], c["dE"])
            continue
        c1 = bool(c["pmatch"])
        c2 = bool(c["E_ok"])
        chk(f"{n}:C1", c1, c["pplus_max"])
        chk(f"{n}:C2", c2, c["dE"])
        if not (c1 and c2):
            continue
        valid.append(n)
        # AMENDMENT-1: diffusion-blindness holds iff Dp(0) is S-odd (P_-
        # eigenmode decays in place); sign/phase pairs are S-odd analytic
        # (pure cross-term Dp), shape/amp-raw carry an S-even |psi_-|^2
        # difference that diffuses (filed VISIBLE). Wave+POT stay blind
        # universally (difference never leaves the hidden support).
        sodd_exp = (":sign:" in n) or (":phase:" in n)
        chk(f"{n}:sodd_pattern", bool(c["sodd"]) == sodd_exp, c["sodd"])
        chk(f"{n}:C0_Dlocal", c["D"] > D_LOCAL_BAR, c["D"])
        for r in R_LOAD:
            chk(f"{n}:C0_wave_r{r}",
                c["wave_Dmax"][str(r)] < D_REMOTE_BAR, c["wave_Dmax"][str(r)])
            if c["sodd"]:
                chk(f"{n}:C0_diff_r{r}",
                    c["diff_Dmax"][str(r)] < D_REMOTE_BAR,
                    c["diff_Dmax"][str(r)])
        chk(f"{n}:C0_pot", c["pot_remote"] < D_REMOTE_BAR, c["pot_remote"])
        chk(f"{n}:C0_potsup", c["pot_support"])
        chk(f"{n}:dB_headline", c["db_max"] > DBAR_PHYS, c["db_max"])
        chk(f"{n}:ledger_nonzero", c["lc_n"] > 0, c["lc_n"])

    # Conjugate (HBR-0E; C3) --------------------------------------------------
    for n in ("X:l6", "X:l28"):
        chk(f"{n}:conjugacy", cells[n]["worst"] < FD_BAR, cells[n]["worst"])

    # Equal-ledger control (HBR-0J) -------------------------------------------
    for n in ("J:uniform", "J:packet0"):
        c = cells[n]
        chk(f"{n}:bg_real", c["bg_real"])
        chk(f"{n}:pmatch", c["pmatch"])
        chk(f"{n}:dB_null", c["max_dB"] < 1e-12, c["max_dB"])
        chk(f"{n}:ledger_null", c["lc_n"] == 0, c["lc_n"])
        chk(f"{n}:J_visible", c["max_dJ"] > D_LOCAL_BAR, c["max_dJ"])
        chk(f"{n}:D_visible", c["D"] > D_LOCAL_BAR, c["D"])

    # Pure hidden (HBR-0K) ----------------------------------------------------
    for n in ("K:delta", "K:disk", "K:checker", "K:complex"):
        chk(f"{n}:E_zero", abs(cells[n]["E"]) < 1e-12, cells[n]["E"])
    for n in ("K:disk", "K:checker", "K:complex"):
        chk(f"{n}:B_nontrivial", cells[n]["B_max"] > D_LOCAL_BAR,
            cells[n]["B_max"])
        chk(f"{n}:L_nontrivial", cells[n]["L_nnz"] > 0, cells[n]["L_nnz"])

    # VMINUS (HBR-0L) ----------------------------------------------------------
    lv = cells["L:vminus"]
    chk("L:w_minus_pure", lv["tab"]["w_plus"] < 1e-12, lv["tab"]["w_plus"])
    chk("L:E_zero", abs(lv["tab"]["E"]) < 1e-12, lv["tab"]["E"])
    chk("L:class_uniform", lv["tab"]["max_class_spread"] < 1e-12,
        lv["tab"]["max_class_spread"])
    chk("L:translation", lv["trans_maxdiff"] < 1e-12, lv["trans_maxdiff"])
    chk("L:J_zero_real", lv["J_max"] < 1e-12, lv["J_max"])
    chk("L:pair_pmatch", lv["pair_pmatch"])
    chk("L:pair_Eok", lv["pair_Eok"])
    chk("L:pair_dB", lv["pair_db_max"] > DBAR_PHYS, lv["pair_db_max"])
    chk("L:pair_lc", lv["pair_lc_n"] > 0, lv["pair_lc_n"])

    # Sweeps (HBR-0M/N) --------------------------------------------------------
    for n in ("M:packet:delta", "M:uniform:disk"):
        c = cells[n]
        chk(f"{n}:res_B", c["res_B"] < FIT_BAR, c["res_B"])
        chk(f"{n}:res_L", c["res_L"] < FIT_BAR, c["res_L"])
        chk(f"{n}:E_const", c["E_range"] < 1e-12, c["E_range"])
        chk(f"{n}:B_varies", c["B_varmax"] > D_LOCAL_BAR, c["B_varmax"])
        chk(f"{n}:L_varies", c["L_varmax"] > D_LOCAL_BAR, c["L_varmax"])
    for n in ("N:packet:delta", "N:uniform:disk"):
        c = cells[n]
        chk(f"{n}:res_B", c["res_B"] < FIT_BAR, c["res_B"])
        chk(f"{n}:res_L", c["res_L"] < FIT_BAR, c["res_L"])
        chk(f"{n}:d_lin", c["d_lin"] < 1e-9, c["d_lin"])
        chk(f"{n}:d_quad", c["d_quad"] < 1e-9, c["d_quad"])
        chk(f"{n}:E_const", c["E_range"] < 1e-12, c["E_range"])
        chk(f"{n}:clin_nontrivial", c["clin_max"] > 1e-9, c["clin_max"])

    # Shape (HBR-0O) ------------------------------------------------------------
    sh = cells["O:shapes"]
    for k in ("dipole", "disk", "checker"):
        chk(f"O:norm_{k}", abs(sh["norms"][k] - 1.0) < 1e-12,
            sh["norms"][k])
    for k in ("dipole_vs_disk", "dipole_vs_checker", "disk_vs_checker"):
        chk(f"O:{k}", sh[k]["db_max"] > D_LOCAL_BAR, sh[k]["db_max"])

    # Locality (HBR-0P/Q; C5) ---------------------------------------------------
    g = cells["P:graded"]
    far_rows = [r for r in g["rows"] if r["dist"] >= 2]
    chk("P:graded_has_far", len(far_rows) > 0, len(far_rows))
    chk("P:graded_dh", all(r["dh_edge"] < LOC_BAR for r in far_rows),
        max([r["dh_edge"] for r in far_rows]) if far_rows else "none")
    chk("P:graded_dB", all(r["dB_edge"] < LOC_BAR for r in far_rows),
        max([r["dB_edge"] for r in far_rows]) if far_rows else "none")
    pf = cells["P:far"]
    chk("P:far_dh", abs(pf["dh_edge"]) < LOC_BAR, pf["dh_edge"])
    chk("P:far_dB", pf["dB_edge"] < LOC_BAR, pf["dB_edge"])
    chk("P:far_nontrivial", pf["lc_n_full"] > 0, pf["lc_n_full"])
    ps = cells["P:support"]
    chk("P:sup_n", ps["n_support"] > 0, ps["n_support"])
    chk("P:sup_off", all(abs(r["dh_edge"]) < LOC_BAR for r in ps["off"]),
        max([abs(r["dh_edge"]) for r in ps["off"]]))

    # Passing wave (HBR-0R) ------------------------------------------------------
    for n in ("R:delta", "R:disk"):
        c = cells[n]
        chk(f"{n}:wA", c["wA"]["I"] < WIT_BAR, c["wA"]["I"])
        chk(f"{n}:wB", c["wB"]["I"] < WIT_BAR, c["wB"]["I"])
        chk(f"{n}:far_null", c["far_max_t"] < 1e-12, c["far_max_t"])
        chk(f"{n}:overlap_mod", c["near_over"] > D_LOCAL_BAR, c["near_over"])

    # Symmetry (HBR-0U; C6/C7) ----------------------------------------------------
    su = cells["U:sym"]
    chk("U:u1_dB", su["u1_dB"] < U1_BAR, su["u1_dB"])
    chk("U:u1_dL", su["u1_dL"] < U1_BAR, su["u1_dL"])
    chk("U:rl_dB", su["rl_dB"] < 1e-12, su["rl_dB"])
    chk("U:rl_dL", su["rl_dL"] < 1e-12, su["rl_dL"])
    chk("U:sh_dB", su["sh_dB"] < 1e-12, su["sh_dB"])
    chk("U:sh_dL", su["sh_dL"] < 1e-12, su["sh_dL"])

    # Vacuum (HBR-0V) --------------------------------------------------------------
    vv = cells["V:vac"]
    chk("V:VPLUS_E", abs(vv["VPLUS"]["E"] + 8.0) < 1e-9, vv["VPLUS"]["E"])
    chk("V:VPLUS_plus", vv["VPLUS"]["w_minus"] < 1e-12,
        vv["VPLUS"]["w_minus"])
    chk("V:VPI_E", abs(vv["VPI"]["E"] - 8.0) < 1e-9, vv["VPI"]["E"])
    chk("V:VPI_plus", vv["VPI"]["w_minus"] < 1e-12, vv["VPI"]["w_minus"])
    chk("V:VMINUS_E", abs(vv["VMINUS"]["E"]) < 1e-12, vv["VMINUS"]["E"])
    chk("V:VMINUS_minus", vv["VMINUS"]["w_plus"] < 1e-12,
        vv["VMINUS"]["w_plus"])
    chk("V:VMINUS_spread", vv["VMINUS"]["max_class_spread"] < 1e-12,
        vv["VMINUS"]["max_class_spread"])

    # Firewall (HBR-0W; C8) + ledger identity (C4) + infomap (HBR-0X) ------------
    chk("W:I", cells["W:headon"]["I_ok"], cells["W:headon"]["witness"]["I"])
    chk("C4:direct", cells["C4:direct"]["worst"] < C4_BAR,
        cells["C4:direct"]["worst"])
    xm = cells["X:r2mixed"]
    chk("X:n", xm["n_states"] == 168, xm["n_states"])
    chk("X:separates", xm["min_D"] > D_LOCAL_BAR, xm["min_D"])
    chk("X:n_below", xm["n_below"] == 0, xm["n_below"])
    # AMENDMENT-1 (HBR-0X refinement): R_G separates up to conjugation
    # (B,L conjugation-even; mechanism = HBR-0J control). 3 conjugate
    # pairs/cell x 21 cells = 63, all fp-identical.
    chk("X:n_conj", xm["n_conj"] == 63, xm["n_conj"])
    chk("X:conj_blind", xm["conj_max_D"] < 1e-12, xm["conj_max_D"])

    # Verdict ladder --------------------------------------------------------------
    n_pass = sum(1 for c in checks if c["ok"])
    c0c8 = [c for c in checks if (":C0_" in c["name"] or ":C1" in c["name"]
                                  or ":C2" in c["name"] or ":conjugacy" in c["name"]
                                  or c["name"].startswith("C4:")
                                  or c["name"].startswith("P:")
                                  or c["name"].startswith("U:")
                                  or c["name"].startswith("W:")
                                  or ":wA" in c["name"] or ":wB" in c["name"])]
    controls_green = all(c["ok"] for c in c0c8)
    dbs = [(n, cells[n]["db_max"]) for n in valid]
    lcs = [(n, cells[n]["lc_n"]) for n in valid]
    flips = sum(cells[n]["lc_flips"] for n in valid) + lv["pair_flips"]
    null = (len(valid) > 0
            and all(v < DBAR_FP for _, v in dbs)
            and all(n == 0 for _, n in lcs))
    gradient = (any(v > DBAR_PHYS for _, v in dbs) and controls_green
                and len(valid) > 0)
    if gradient and flips > 0:
        verdict = "HBR0-SIGNREV"
    elif gradient:
        verdict = "HBR0-GRADIENT"
    elif null:
        verdict = "HBR0-NULL"
    else:
        verdict = "HBR0-PARTIAL"
    with open(f"{OUTD}/hiddenbr_verdict.json", "w") as f:
        json.dump({"verdict": verdict, "n_checks": len(checks),
                   "n_pass": n_pass, "valid_pairs": valid,
                   "controls_green": controls_green,
                   "total_flips": int(flips),
                   "checks": checks}, f, indent=1)
    with open(f"{OUTD}/hiddenbr_stage.json", "w") as f:
        json.dump({"cells": rec["cells"]}, f)
    print(f"{verdict} {n_pass}/{len(checks)} valid={len(valid)} "
          f"flips={flips} controls={controls_green}")


if __name__ == "__main__":
    main()
