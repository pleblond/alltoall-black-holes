"""BR-2.5 verdict analyzer (FROZEN ladder pre-data; see BR25-PREREG).

Reads data/br25_contraction.json, checks derivation/conservation gates,
evaluates the verdict ladder. Exit 1 only on gate failure (a low rung is
never a failure). Filed debts (D3 field-mode loss, norm account, rate law)
are reported, never gated.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

PASS, FAIL = "PASS", "FAIL"
results = []


def gate(name, ok, detail=""):
    results.append((name, PASS if ok else FAIL, detail))
    print(f"[{PASS if ok else FAIL}] {name} {detail}", flush=True)


def main():
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "data", "br25_contraction.json")
    with open(path) as f:
        d = json.load(f)
    F, G, H, J, L, M, I = (d[k] for k in ("F", "G", "H", "J", "L", "M", "I"))

    # ---- Derivation/conservation gates ----
    census_ok = True
    for tag, cen in [("L12+" + m, F["torus_L12"][m]["census"]) for m in ("sum", "avg", "norm")]:
        census_ok &= (cen["dN"] == -1 and cen["dE"] == cen["dE_formula"]
                      and abs(cen["dnorm_direct"] - cen["dnorm_formula"]) < 1e-9
                      and cen["simple"])
    cenb = F["ball_R18"]["census"]
    census_ok &= (cenb["dN"] == -1 and cenb["dE"] == cenb["dE_formula"]
                  and abs(cenb["dnorm_direct"] - cenb["dnorm_formula"]) < 1e-9)
    gate("C-census-exact", census_ok, "dN/dE/dnorm formulas, all maps + ball")

    cone_ok = (F["torus_L12"]["sum"]["cone"]["ok"]
               and F["ball_R18"]["cone"]["ok"] and I["single"]["ok"]
               and F["torus_L12"]["sum"]["cone"]["max_changed_dist"] == 1)
    gate("I-cone-R1", cone_ok, "single-event R_U=1 (torus/ball/L28)")
    gate("I-cone-multitick", I["chain3"]["ok"] and not I["chain3_r2"]["ok"],
         "3 ticks need radius 3")

    m1 = F["m1_contrast"]
    gate("F-locality-contrast", m1["max_changed_dist"] > 1,
         f"M1 reach={m1['max_changed_dist']} chord={m1['chord_len']} vs R_U=1")

    gate("G-record-exact", G["record_exact"], "D1-with-record restores")
    gate("G-oracle-exists", G["oracle_restores"] and G["oracle_in_covers"],
         f"oracle among {G['n_covers']} covers (3^{G['degree_k']})")
    gate("G-field-formula",
         abs(G["field_staggered"]["error"] - G["field_staggered"]["formula"]) < 1e-12
         and G["field_uniform"]["error"] == 0.0,
         f"derr_s={G['field_staggered']['error']:.4f} (D3 quantified)")

    st = H["stagger"]
    nE = st["phi0"]["n_plus"] + st["phi0"]["n_zero"] + st["phi0"]["n_minus"]
    quad_ok = (st["phi0"]["n_plus"] == nE and st["phi_pi"]["n_minus"] == nE
               and st["phi_half"]["n_zero"] == nE
               and st["phi_half"]["J_maxabs"] > 0.1)
    gate("H-quadrature", quad_ok,
         f"E={nE}: +1@{0}, -1@{pi}, 0+flow@{pi/2}")
    gate("H-ortho", H["ortho"]["B_identical"] and H["ortho"]["tend_identical"]
         and H["ortho"]["J_negated"], "J-flip leaves geometry bitwise")
    gate("E-quiescent", H["zero"]["all_B_zero"] and H["zero"]["all_J_zero"]
         and H["zero"]["all_tend_zero"], "psi=0 readouts bitwise null")
    gate("B-2B-wired", abs(F["torus_L12"]["sum"]["dnorm_is_2B"]) < 1e-12,
         "sum-map Dn == 2B (campaign edge)")

    gate("J-between-events", J["ring60"]["post_norm_const"]
         and J["j2_L28"]["post_norm_const"] and J["j2_L28"]["simple"]
         and J["j2_L28"]["readers_ok"], "unitary between events + readers")
    gate("J-deterministic", J["ring60"]["deterministic"],
         f"jump={J['ring60']['jump']:.2e} across event")

    gate("L-collapsed", L["ext_is_boundary"] and L["simple"]
         and L["steps"] == L["region_size"] - 1,
         f"{L['region_size']}->1 ext={L['ext_degree']} "
         f"thru {L['thru_before']}->{L['thru_after']}")
    mg = M.get("merger", {})
    gate("M-composes", M["reps_adjacent"] and mg.get("same_primitive", False)
         and mg.get("dN") == -1 and mg.get("dE") == mg.get("dE_formula")
         and mg.get("ext_degree") == mg.get("union_boundary"),
         "bridge contraction, same primitive")

    # ---- Verdict ladder (frozen bars) ----
    print("\n--- ladder ---")
    g = {r[0]: r[1] == PASS for r in results}
    consistent = g["C-census-exact"] and g["I-cone-R1"] and g["J-between-events"]
    print(f"INCONSISTENT: {not consistent}")
    split_derivable = g["G-record-exact"] and g["G-oracle-exists"]
    irrevers = consistent and (not split_derivable or not g["J-deterministic"])
    print(f"IRREVERSIBLE: {irrevers}")
    local = (consistent and not irrevers and g["I-cone-multitick"]
             and g["F-locality-contrast"])
    print(f"LOCAL: {local}")
    quad = (local and g["H-quadrature"] and g["H-ortho"] and g["E-quiescent"]
            and g["B-2B-wired"])
    print(f"QUADRATURE: {quad}")
    onto = (quad and g["J-deterministic"] and g["L-collapsed"] and g["M-composes"])
    print(f"ONTOLOGY: {onto}")

    if not consistent:
        verdict = "BR25-INCONSISTENT"
    elif irrevers:
        verdict = "BR25-IRREVERSIBLE"
    elif not local:
        verdict = "BR25-INCONSISTENT"
    elif not quad:
        verdict = "BR25-LOCAL"
    elif not onto:
        verdict = "BR25-QUADRATURE"
    else:
        verdict = "BR25-ONTOLOGY"
    print(f"\nVERDICT: {verdict}")
    print("filed debts (not gates): D3 field-mode loss | norm account 2B | "
          "event-rate law unearned (BR-3C) | K design-open")

    fails = [r for r in results if r[1] == FAIL]
    print(f"\ngates: {len(results) - len(fails)}/{len(results)} pass")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
