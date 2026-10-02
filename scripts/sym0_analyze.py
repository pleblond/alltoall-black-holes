"""SYM-0 gate analyzer (frozen SYM0-PREREG gates, no tuning).

Reads data/sym0_ledger.json, applies HARD + MEASURED gates, writes
data/sym0_verdict.json {gates, classifications, verdict, interpretation}.
Verdict ladder: SYM0-CLOSED / SYM0-PARTIAL / SYM0-OPEN (see prereg).
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph.sym0 import FP_ZERO, KRYLOV_BAR

CORE_FAMS = ("O1", "O2", "O3", "O4")


def _fam_max(rec, fams=CORE_FAMS):
    return max(float(rec["witness"][f]) for f in fams)


def main():
    base = os.path.join(os.path.dirname(__file__), "..", "data")
    ledger = json.load(open(os.path.join(base, "sym0_ledger.json")))
    gates = []

    def gate(gid, ok, detail=""):
        gates.append({"gate": gid, "ok": bool(ok), "detail": str(detail)[:300]})

    pairs = ledger["pair"]
    by_tid = {}
    for rec in pairs:
        by_tid.setdefault(rec["cell"][2], []).append(rec)

    # HARD H-E: relabeling redundancy over O1..O4 (all states x perms).
    r_cells = by_tid.get("R", [])
    r_max = max([_fam_max(r) for r in r_cells]) if r_cells else float("inf")
    gate("H-E-relabel", r_cells and r_max < FP_ZERO,
         f"n={len(r_cells)} max={r_max:.3e}")
    r5_max = max([float(r["witness"]["O5"]) for r in r_cells]) if r_cells else -1
    gate("M-E-O5-filed", True, f"O5 max={r5_max:.3e} (filed, not hard)")

    # HARD H-D: global phase redundancy over O1..O4 (all alpha x states).
    u_cells = by_tid.get("U1", []) + by_tid.get("Sign", [])
    u_max = max([_fam_max(r) for r in u_cells]) if u_cells else float("inf")
    gate("H-D-phase", u_cells and u_max < FP_ZERO,
         f"n={len(u_cells)} max={u_max:.3e}")

    # Covariance battery (SYM-0B): U1/Scale exact, Shift defect measured.
    for tid, bar, gid in (("CovB-U1", KRYLOV_BAR, "M-B-cov-U1"),
                          ("CovB-Scale", KRYLOV_BAR, "M-B-cov-Scale")):
        cells = by_tid.get(tid, [])
        mx = max([float(c["extras"]["covariance_err"]) for c in cells]) \
            if cells else float("inf")
        gate(gid, cells and mx < bar, f"n={len(cells)} max={mx:.3e}")
    sh_cells = by_tid.get("CovB-Shift", [])
    sh_min = min([float(c["extras"]["covariance_err"]) for c in sh_cells]) \
        if sh_cells else 0.0
    gate("M-L-shift-noncovariance", sh_cells and sh_min > 0.0,
         f"n={len(sh_cells)} min-defect={sh_min:.3e} (filed: not a symmetry)")

    # HARD H-T: redundant-pair dynamics preservation (R + U1 dyn cells).
    dyn = ledger["dyn"]
    dyn_r = [d for d in dyn if d["cell"][2] == "R"]
    dyn_u = [d for d in dyn if d["cell"][2] == "U1"]
    for cells, gid in ((dyn_r, "H-T-red-R"), (dyn_u, "H-T-red-U1")):
        tj = max([float(d["traj_defect"]) for d in cells]) if cells else -1
        ep = max([max(float(v) for k, v in d["endpoint"].items()
                      if k in CORE_FAMS) for d in cells]) if cells else -1
        gate(gid, cells and tj < KRYLOV_BAR and ep < FP_ZERO,
             f"n={len(cells)} traj={tj:.3e} end={ep:.3e}")
    dyn_s = [d for d in dyn if d["cell"][2] == "S"]
    if dyn_s:
        tj = max(float(d["traj_defect"]) for d in dyn_s)
        gate("M-T-S-intertwine", tj < KRYLOV_BAR,
             f"n={len(dyn_s)} S-dyn-intertwine={tj:.3e} (filed)")

    # HARD H-Theta.
    th = ledger["theta"]
    th_max = max([float(t["theta_err"]) for t in th]) if th else float("inf")
    gate("H-Theta-identity", th and th_max < KRYLOV_BAR,
         f"n={len(th)} max={th_max:.3e}")

    # HARD H-SectorSign (= S identity on J2 battery).
    ss = by_tid.get("SectorSign", [])
    ss_max = max([float(c["extras"]["sect_eq_S"]) for c in ss]) if ss else -1
    gate("H-SectorSign-eq-S", ss and ss_max < FP_ZERO,
         f"n={len(ss)} max={ss_max:.3e}")

    # HARD H-Orbit: integer identity on all stab cells with perms.
    stab = [s for s in ledger["stab"] if "identity_ok" in s]
    stab_bad = [s for s in stab if not s["identity_ok"]]
    gate("H-Orbit-identity", stab and not stab_bad,
         f"n={len(stab)} bad={len(stab_bad)}")

    # HARD H-U: R/Aut/U1 marks covariance (UB/UL/UEc).
    ucells = ledger["ucell"]
    hard_u = [c for c in ucells if c["cell"][3] in ("R-rev", "R-shuf", "Aut0", "U1")]
    hard_u = [c for c in hard_u if c["rec"].get("ok") is not None]
    u_bad = [c["cell"] for c in hard_u if not c["rec"]["ok"]]
    gate("H-U-marks-covariance", hard_u and not u_bad,
         f"n={len(hard_u)} bad={len(u_bad)}")
    s_cells = [c for c in ucells if c["cell"][3] == "S"]
    s_bad = [c["cell"] for c in s_cells if not c["rec"].get("ok")]
    gate("M-U-S-covariance", not s_bad,
         f"n={len(s_cells)} bad={len(s_bad)} (filed)")
    c_cells = [c for c in ucells if c["cell"][3] == "C"]
    c_inv = all(c["rec"]["invariant"] for c in c_cells) if c_cells else False
    gate("M-U-C-invariance", True,
         f"UB/UL/UEc conjugation-invariant={c_inv} n={len(c_cells)} (filed)")
    for tid in ("Scale", "Shift"):
        t_cells = [c for c in ucells if c["cell"][3] == tid]
        n_inv = sum(1 for c in t_cells if c["rec"]["invariant"])
        gate(f"M-U-{tid}-marks", True,
             f"invariant {n_inv}/{len(t_cells)} (filed, not gated)")

    # MEASURED M-C: conjugation visibility conditional on J content.
    c_pairs = by_tid.get("C", [])
    vis = [(c["cell"][0], c["cell"][1],
            float(c["per_readout"]["O2"].get("edge_J", 0.0)),
            _fam_max(c)) for c in c_pairs]
    j_vis = [v for v in vis if v[2] > 0.0]
    j_zero = [v for v in vis if v[2] == 0.0]
    gate("M-C-conditional", True,
         f"J-visible {len(j_vis)} all-D>0="
         f"{all(v[3] > 0.0 for v in j_vis)}; J-absent {len(j_zero)} "
         f"all-D==0={all(v[3] < FP_ZERO for v in j_zero)} (filed)")

    # MEASURED M-F/G: Aut/T shape-invariant + location-moved.
    lm = ledger["landmark"][0]
    gate("M-G-landmark", True,
         f"rel_AO={lm['rel_AO']} rel_BO={lm['rel_BO']} "
         f"rel_TAO={lm['rel_TAO']} TA_eq_B={lm['TA_eq_B']:.3e} (filed)")
    aut_p = [c for c in by_tid.get("Aut", []) + by_tid.get("T", [])
             if c["cell"][1] == "packet" and "com_x" in c["extras"]]
    moved = sum(1 for c in aut_p
                if float(np_maxdiff(c["extras"]["com_x"],
                                    c["extras"]["com_y"])) > 1e-12)
    gate("M-FG-aut-moves-packets", True,
         f"{moved}/{len(aut_p)} packet cells COM-moved (filed)")

    # MEASURED M-H: sheet exchange pattern.
    s_pairs = by_tid.get("S", [])
    gate("M-H-sheet", True,
         f"n={len(s_pairs)} maxD={max([_fam_max(c) for c in s_pairs]) if s_pairs else -1:.3e} "
         f"(filed: coarse-same/sheet-moved in ledger)")

    # MEASURED M-K: scale exact laws.
    sc = by_tid.get("Scale", [])
    sc_max = max([float(c["extras"]["rho_ratio"]) for c in sc]) if sc else -1
    gate("M-K-scale-laws", sc and sc_max < FP_ZERO,
         f"n={len(sc)} rho-ratio-defect={sc_max:.3e} (filed: physical)")

    # MEASURED M-M: sheet-phase visibility.
    sp = by_tid.get("SheetPhase", [])
    sp_vis = [c for c in sp if _fam_max(c) > 0.0]
    gate("M-M-sheetphase", True,
         f"visible {len(sp_vis)}/{len(sp)} (filed)")

    # MEASURED M-QR: hierarchy counts.
    hier = ledger["hierarchy"][0]["counts"]
    gate("M-QR-hierarchy", True,
         f"counts={hier['counts']} monotone={hier['monotone_nondecreasing']} (filed)")

    # MEASURED M-V/W: recount + gaps.
    rec = ledger["recount"]
    debt_cells = []
    for r in rec:
        for gname, g in r["gaps"].items():
            if g.get("uniform_differs"):
                debt_cells.append((r["key"], gname))
    gate("M-V-recount", True,
         f"states={len(rec)} differing-grains={len(debt_cells)} (filed)")
    gate("M-W-indifference", True,
         f"debt_survives={bool(debt_cells)} (filed, no probabilities)")

    # MEASURED M-X: phase quotient.
    fs = ledger["fs"]
    fz = [c for c in fs if c["cell"][0] == "zero"]
    fz_max = max([float(c["d_fs"]) for c in fz]) if fz else -1
    gate("M-X-fs-zero", fz and fz_max < FP_ZERO,
         f"n={len(fz)} max={fz_max:.3e}")
    fd = [c for c in fs if c["cell"][0] == "dyn"]
    fd_max = max([float(c["drift"]) for c in fd]) if fd else -1
    gate("M-X-fs-dyn", fd and fd_max < KRYLOV_BAR,
         f"n={len(fd)} max-drift={fd_max:.3e}")
    ft = [c for c in fs if c["cell"][0] == "tri"]
    gate("M-X-fs-triangle", ft and all(c["ok"] for c in ft),
         f"n={len(ft)}")

    # MEASURED M-O5: replay manifest.
    rep = ledger["replay"][0]
    n_hit = sum(1 for v in rep.values()
                if isinstance(v, dict) and v.get("exists"))
    gate("M-O5-replay", True,
         f"banked-files-hit={n_hit} zero0={rep.get('zero0_apparatus')} (filed)")

    hard_ids = ("H-E-relabel", "H-D-phase", "H-T-red-R", "H-T-red-U1",
                "H-Theta-identity", "H-SectorSign-eq-S", "H-Orbit-identity",
                "H-U-marks-covariance")
    hard = {g["gate"]: g["ok"] for g in gates if g["gate"] in hard_ids}
    measured_inconclusive = [g["gate"] for g in gates
                             if g["gate"].startswith("M-") and not g["ok"]]
    if all(hard.values()) and not measured_inconclusive:
        verdict = "SYM0-CLOSED"
    elif all(hard.values()):
        verdict = "SYM0-PARTIAL"
    else:
        verdict = "SYM0-OPEN"
    classifications = {
        "R": "redundancy" if hard["H-E-relabel"] else "OPEN",
        "U1": "redundancy" if hard["H-D-phase"] else "OPEN",
        "Sign": "U1(pi)-alias",
        "Aut": "symmetry(filed M-FG)",
        "T": "symmetry(filed M-G)",
        "S": "symmetry+operational(filed M-H/M-O5)",
        "C": "distinguishable-conditional(filed M-C)",
        "Theta": "time-reversal" if hard["H-Theta-identity"] else "OPEN",
        "Scale": "physical-not-redundant(filed M-K)",
        "Shift": "not-symmetry(filed M-L)",
        "SheetPhase": "physical(filed M-M)",
        "SectorSign": "=S" if hard["H-SectorSign-eq-S"] else "OPEN",
    }
    out = {"gates": gates, "classifications": classifications,
           "verdict": verdict,
           "interpretation": "See docs/DEFERRED.md SYM0-VERDICT (post-data)."}
    with open(os.path.join(base, "sym0_verdict.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"verdict={verdict} hard={sum(hard.values())}/{len(hard)} "
          f"measured-open={measured_inconclusive}")


def np_maxdiff(a, b):
    import numpy as np
    return float(np.abs(np.asarray(a, dtype=float)
                        - np.asarray(b, dtype=float)).max())


if __name__ == "__main__":
    main()
