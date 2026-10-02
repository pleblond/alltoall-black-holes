"""HIDDEN-0 verdict analyzer (FROZEN pre-data; decision tree only).

Reads hidden0_cells.json (43 cells), evaluates every preregistered check,
writes hidden0_verdict.json + hidden0_stage.json. No bar/ladder/estimator
may change post-data: failures file as design-error autopsies or genuine.

Ladder (HIDDEN0-PREREG + AMENDMENT-1):
  HIDDEN0-LEAK: any frozen-H remote Dmax > 1e-6 at r >= 2 (F/T cells).
  HIDDEN0-INTERACT: any passing-wave witness I > 1e-6 (H cells).
  HIDDEN0-ABSENT: no local distinguishability anywhere (all B/H/K D <= 1e-6).
  HIDDEN0-SEPARATED (primary positive): every SEPARATED-clause green
    (A1-A7 applied: amp-raw dQ values, HAMP-Q collinearity, sodd scope,
    E:delta structural B, G descriptive decay/residual, deduped census,
    U OR-logic non-flip).
  Else HIDDEN0-PARTIAL (per-stage filing, honest).
"""
import json
import os
import sys

IN = sys.argv[1] if len(sys.argv) > 1 else "/tmp/hidden0_parts/hidden0_cells.json"
OUTD = sys.argv[2] if len(sys.argv) > 2 else "/tmp/hidden0_parts"

D_LOCAL_BAR = 1e-6
D_REMOTE_BAR = 1e-9
RATIO_BAR = 1e-6
LEAK_BAR = 1e-6
WITNESS_ATOL = 1e-6
R_LOAD = (2, 4, 6)


def main():
    with open(IN) as f:
        rec = json.load(f)
    cells = {c["note"]: c for c in rec["cells"]}
    checks = []  # (name, ok, detail)

    def chk(name, ok, detail=""):
        checks.append({"name": name, "ok": bool(ok), "detail": str(detail)})

    # A: anatomy -----------------------------------------------------------
    a6, a28 = cells["A:l6"], cells["A:l28"]
    chk("A6:comm", a6["comm"] < 1e-12, a6["comm"])
    chk("A6:dead", a6["dead"] < 1e-12, a6["dead"])
    chk("A6:inter", a6["inter"] < 1e-12, a6["inter"])
    chk("A6:frozen", a6["frozen"] < 1e-9, a6["frozen"])
    chk("A6:decomp", a6["decomp"] < 1e-8, a6["decomp"])
    chk("A6:n_zero", a6["n_zero"] == a6["nodal_pred"],
        f"{a6['n_zero']} vs {a6['nodal_pred']}")
    chk("A28:n_zero", a28["n_zero"] == 838, a28["n_zero"])
    chk("A28:dead", a28["dead"] < 1e-12, a28["dead"])
    chk("A28:comm", a28["comm"] < 1e-12, a28["comm"])

    # B: pair battery -------------------------------------------------------
    bnotes = [n for n in cells if n.startswith("B:")]
    for n in sorted(bnotes):
        c = cells[n]
        if not n.endswith("05q"):
            chk(f"{n}:pmatch", c["pmatch"])
        if ":sign:" in n or ":phase:" in n or ":shape:" in n:
            chk(f"{n}:dQ", c["dQ"] < 1e-9, c["dQ"])
        if n.endswith("05raw"):
            chk(f"{n}:dQfiled", abs(c["dQ"] - 0.75) < 1e-9, c["dQ"])
        if n.endswith("05q"):
            chk(f"{n}:dQ", c["dQ"] < 1e-9, c["dQ"])
            chk(f"{n}:scale", abs(c["scale_c"] - (1.75) ** 0.5) < 1e-9,
                c["scale_c"])
        if n.endswith("20raw"):
            chk(f"{n}:dQfiled", abs(c["dQ"] - 3.0) < 1e-9, c["dQ"])
        chk(f"{n}:Dlocal", c["D"] > D_LOCAL_BAR, c["D"])
        chk(f"{n}:Efree", c["E_free"],
            f"E-={c['E_minus']:.1e} Ex={c['E_x']:.1e}")
        if ":sign:" in n or ":phase:" in n:
            chk(f"{n}:sodd", c["sodd"])
    # A2: HAMP-Q P_+ direction-collinearity audit (deterministic rebuild).
    import numpy as _np

    from bh_graph import hidden as _hd
    from bh_graph import malus as _ma
    from bh_graph.ballistic import node_order as _no
    from bh_graph import field0 as _f0
    from bh_graph.formation import j2_torus_coords as _c3
    from bh_graph.formation import j2_torus_graph as _jg
    _g = _jg(28)
    _o = _no(_g)
    _cc = _c3(28)
    _pr = _ma.sheet_projectors(_o, _cc)
    _sub = _f0.build_substrate("j2", 28)
    _bg = _hd.symmetric_packet(_sub, (7.0, 14.0), (0.3, 0.0), 4.0)
    _ma0 = _hd.hidden_delta(_o, _cc, (7, 14))
    _qm = _hd.qmatch_pair(_hd.matched_pair(_bg, _ma0, "amplitude", 0.5))
    _pa = _np.asarray(_pr["P_sym"], dtype=float) @ _qm["psi_A"]
    _pb = _np.asarray(_pr["P_sym"], dtype=float) @ _qm["psi_B"]
    _cos = abs(complex(_np.vdot(_pa, _pb))) / (_np.linalg.norm(_pa)
                                               * _np.linalg.norm(_pb))
    chk("B:amp:packet:05q:collinear", abs(_cos - 1.0) < 1e-12, _cos)

    # E: hidden-only ----------------------------------------------------------
    for n in sorted(n for n in cells if n.startswith("E:")):
        c = cells[n]
        chk(f"{n}:frozen", c["frozen"] < 1e-9, c["frozen"])
        chk(f"{n}:rho", c["rho_max"] > D_LOCAL_BAR, c["rho_max"])
        if n == "E:delta":
            chk(f"{n}:Bstruct", c["B_max"] < 1e-12, c["B_max"])
        else:
            chk(f"{n}:B", c["B_max"] > D_LOCAL_BAR, c["B_max"])
        chk(f"{n}:E0", abs(c["E"]) < 1e-9, c["E"])

    # F: remote ---------------------------------------------------------------
    for n in sorted(n for n in cells if n.startswith("F:") and n != "F:pot"):
        c = cells[n]
        for leg in ("wave", "diff"):
            dm = {int(k): v for k, v in c[f"{leg}_Dmax"].items()}
            cp = {int(k): v for k, v in c[f"{leg}_Cplus"].items()}
            rt = {int(k): v for k, v in c[f"{leg}_ratio"].items()}
            for r in range(2, 11):
                chk(f"{n}:{leg}:r{r}", dm[r] < D_REMOTE_BAR, dm[r])
            for r in R_LOAD:
                chk(f"{n}:{leg}:arr{r}", cp[r] > 0.001, cp[r])
                chk(f"{n}:{leg}:ratio{r}", rt[r] < RATIO_BAR, rt[r])
    fp = cells["F:pot"]
    chk("F:pot:remote", fp["remote_max"] < D_REMOTE_BAR, fp["remote_max"])
    chk("F:pot:support", fp["support_ok"])

    # G: persistence ------------------------------------------------------------
    # A5: decay ratio + resid_match are DESCRIPTIVE (torus-geometry filing);
    # G physics carried by cross-identity (sign/phase) + residual-exists.
    print("G descriptive (A5):")
    for n in sorted(n for n in cells if n.startswith("G:")):
        c = cells[n]
        chk(f"{n}:Dmax", c["D_max"] > D_LOCAL_BAR, c["D_max"])
        if n in ("G:sign", "G:phase"):
            chk(f"{n}:cross", c["cross_worst"] < 1e-9, c["cross_worst"])
            print(f"  {n}: decay_ratio={c['decay_ratio']:.3f} (filed)")
        else:
            chk(f"{n}:resid", c["D_post"] > D_LOCAL_BAR, c["D_post"])
            print(f"  {n}: Dpost={c['D_post']:.3e} ref={c['resid_ref']:.3e} (filed)")

    # H/I/J: passing wave ---------------------------------------------------------
    for n in sorted(n for n in cells if n.startswith("H:")):
        c = cells[n]
        for tag in ("A", "B"):
            s = c[tag]
            chk(f"{n}:{tag}:eps", s["eps"] < 1e-8, s["eps"])
            chk(f"{n}:{tag}:I", s["w_I"] < WITNESS_ATOL, s["w_I"])
            chk(f"{n}:{tag}:sector", s["sector_worst"] < 1e-9, s["sector_worst"])
            chk(f"{n}:{tag}:write_w", s["write_w"] < 1e-9, s["write_w"])
            chk(f"{n}:{tag}:write_m", s["write_m"] < 1e-9, s["write_m"])
        chk(f"{n}:read", c["read"]["D"] > D_LOCAL_BAR, c["read"]["D"])

    # K: extraction ---------------------------------------------------------------
    for n in sorted(n for n in cells if n.startswith("K:")):
        c = cells[n]
        chk(f"{n}:decA", c["local_decA"] == "A", c["local_decA"])
        chk(f"{n}:decB", c["local_decB"] == "B", c["local_decB"])
        chk(f"{n}:gapA", c["local_gapA"] > D_LOCAL_BAR, c["local_gapA"])
        chk(f"{n}:gapB", c["local_gapB"] > D_LOCAL_BAR, c["local_gapB"])
        chk(f"{n}:remote", c["remote_gap"] < D_REMOTE_BAR, c["remote_gap"])

    # L: census ---------------------------------------------------------------------
    for n in sorted(n for n in cells if n.startswith("L:")):
        c = cells[n]
        if "mixed" in n:
            chk(f"{n}:minD", c["min_D"] > D_LOCAL_BAR,
                f"minD={c['min_D']:.2e} N={c['n_states']} R={c['n_R']}")
            chk(f"{n}:nbelow", c["n_below"] == 0, c["n_below"])
        else:
            chk(f"{n}:pos", c["min_D"] > D_LOCAL_BAR,
                f"minD={c['min_D']:.2e} N={c['n_states']} R={c['n_R']}")
            chk(f"{n}:quo", c["quo_max"] < 1e-12, c["quo_max"])

    # N: exchange ---------------------------------------------------------------------
    nx = cells["N:sheet"]
    chk("N:pure", nx["pure_D"] < 1e-12, nx["pure_D"])
    chk("N:mixed", nx["mixed_D"] > D_LOCAL_BAR, nx["mixed_D"])
    chk("N:smap", nx["smap"] < 1e-12, nx["smap"])

    # O/P: sweep ------------------------------------------------------------------------
    for n in sorted(n for n in cells if n.startswith("O:")):
        c = cells[n]
        chk(f"{n}:fitR", c["res_rho"] < 1e-9, c["res_rho"])
        chk(f"{n}:fitB", c["res_B"] < 1e-9, c["res_B"])
        chk(f"{n}:fitJ", c["res_J"] < 1e-9, c["res_J"])
        chk(f"{n}:modR", c["rho_mod"] > D_LOCAL_BAR, c["rho_mod"])

    # Q: bond ------------------------------------------------------------------------------
    q = cells["Q:full"]
    chk("Q:dB", q["dB_max"] > D_LOCAL_BAR, q["dB_max"])
    chk("Q:count", q["dB_count"] > 0, q["dB_count"])

    # R: ledger ------------------------------------------------------------------------------
    rl = cells["R:packet:delta"]
    chk("R:de", rl["de"] < 1e-9, rl["de"])
    chk("R:bond", rl["bond_maxdiff"] > D_LOCAL_BAR, rl["bond_maxdiff"])

    # S: vac classes ---------------------------------------------------------------------------
    sv = cells["S:classes"]
    chk("S:VPLUS", abs(sv["VPLUS"]["w_sym"] - 1.0) < 1e-12
        and abs(sv["VPLUS"]["E"] + 8.0) < 1e-9,
        f"w={sv['VPLUS']['w_sym']:.4f} E={sv['VPLUS']['E']:.4f}")
    chk("S:VPI", abs(sv["VPI"]["w_sym"] - 1.0) < 1e-12
        and abs(sv["VPI"]["E"] - 8.0) < 1e-9,
        f"w={sv['VPI']['w_sym']:.4f} E={sv['VPI']['E']:.4f}")
    chk("S:VMINUS", abs(sv["VMINUS"]["w_anti"] - 1.0) < 1e-12
        and abs(sv["VMINUS"]["E"]) < 1e-12,
        f"w={sv['VMINUS']['w_anti']:.4f} E={sv['VMINUS']['E']:.2e}")

    # T: obs-input -------------------------------------------------------------------------------
    t = cells["T:packet:delta"]
    for leg in ("W", "D", "P"):
        for r in R_LOAD:
            chk(f"T:{leg}{r}", t[f"{leg}_r{r}"] < D_REMOTE_BAR, t[f"{leg}_r{r}"])
    chk("T:Dlocal", t["D_local"] > D_LOCAL_BAR, t["D_local"])

    # U: staggered -----------------------------------------------------------------------------------
    u = cells["U:eps01"]
    chk("U:pvp", u["pvp"] < 1e-12, u["pvp"])
    chk("U:comm", u["comm_relerr"] < 1e-9, u["comm_relerr"])
    chk("U:lifted", u["n_zero_pert"] < 838, u["n_zero_pert"])
    fsharp = cells["F:sharp"]
    for r in R_LOAD:
        du = u["Dmax"][str(r)]
        df = fsharp["wave_Dmax"][str(r)]
        # A7: non-flip = complement of QUOT-0Q flip (>= 0.05 AND > 3x).
        chk(f"U:nonflip{r}", du < 0.05 or du <= 3 * max(df, 1e-300),
            f"pert={du:.2e} frozen={df:.2e}")

    # Ladder ----------------------------------------------------------------------------------------------
    fails = [c for c in checks if not c["ok"]]
    n_pass = len(checks) - len(fails)
    # LEAK re-evaluated on values (not bars): Dmax > 1e-6 at r >= 2.
    leak_hit = False
    for n in [nn for nn in cells if nn.startswith("F:") and nn != "F:pot"]:
        for leg in ("wave", "diff"):
            for r in range(2, 11):
                if cells[n][f"{leg}_Dmax"][str(r)] > LEAK_BAR:
                    leak_hit = True
    if cells["F:pot"]["remote_max"] > LEAK_BAR:
        leak_hit = True
    for r in R_LOAD:
        for leg in ("W", "D", "P"):
            if cells["T:packet:delta"][f"{leg}_r{r}"] > LEAK_BAR:
                leak_hit = True
    interact = any(c["name"].endswith(":I") and not c["ok"] for c in checks)
    # any B-pair D gate or H read gate green -> locally distinguishable.
    any_local = any(c["ok"] for c in checks
                    if c["name"].startswith("B:") or c["name"].endswith(":read"))
    if leak_hit:
        verdict = "HIDDEN0-LEAK"
    elif interact:
        verdict = "HIDDEN0-INTERACT"
    elif not any_local:
        verdict = "HIDDEN0-ABSENT"
    elif not fails:
        verdict = "HIDDEN0-SEPARATED"
    else:
        verdict = "HIDDEN0-PARTIAL"

    stage = {"n_checks": len(checks), "n_pass": n_pass,
             "n_fail": len(fails), "verdict": verdict,
             "leak_hit": leak_hit, "interact": interact,
             "fails": fails}
    with open(os.path.join(OUTD, "hidden0_verdict.json"), "w") as f:
        json.dump(stage, f, indent=1)
    with open(os.path.join(OUTD, "hidden0_stage.json"), "w") as f:
        json.dump({"checks": checks}, f)
    print(f"HIDDEN-0: {n_pass}/{len(checks)} pass -> {verdict}")
    for c in fails:
        print(f"  FAIL {c['name']}: {c['detail']}")
    print(f"cells: {len(cells)}/43")


if __name__ == "__main__":
    main()
