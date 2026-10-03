"""JET-0 verdict analyzer (FROZEN pre-data; decision tree only).

Reads data/jet0/*.json (ord/mergejet/splitjet/samen/forbit/traj/lower/
hidden/source/generic/witness), evaluates every preregistered gate
(docs/jet0-prereg.md section 6), writes verdict.json. No bar/ladder/
outcome may change post-data: failures file as INCOMPLETE.

Ladder (prereg section 7, precedence):
  INCOMPLETE > DEGENERATE > SURFACE > STATIC > NULL.
"""

from __future__ import annotations

import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import jet0 as j0  # noqa: E402
from bh_graph import merge0 as m0  # noqa: E402

BAR_FP = j0.BAR_FP
BAR_LEDGER = j0.BAR_LEDGER
BAR_PHYS = j0.BAR_PHYS
BAR_U1 = j0.BAR_U1


def _load_family(outdir: str, prefix: str) -> list:
    rows = []
    for path in sorted(glob.glob(os.path.join(outdir, prefix + "_*.json"))):
        if os.path.basename(path) == "verdict.json":
            continue
        with open(path) as f:
            rec = json.load(f)
        rec["_path"] = os.path.basename(path)
        rows.append(rec)
    return rows


def load(outdir: str) -> dict:
    return {
        "ord": _load_family(outdir, "ord"),
        "mergejet": _load_family(outdir, "mergejet"),
        "splitjet": _load_family(outdir, "splitjet"),
        "samen": _load_family(outdir, "samen"),
        "forbit": _load_family(outdir, "forbit"),
        "traj": _load_family(outdir, "traj"),
        "lower": _load_family(outdir, "lower"),
        "hidden": _load_family(outdir, "hidden"),
        "source": _load_family(outdir, "source"),
        "generic": _load_family(outdir, "generic"),
        "witness": _load_family(outdir, "witness"),
    }


def _genuine_task_sets(fams: dict):
    """Collect GENUINE matches per task for the ladder.

    Returns (n_genuine_total, mult_map, merge_dir_n, split_dir_n, details).
    mult_map: task_id -> set(alt_id) for multiplicity.
    """
    mult_map: dict = {}
    details = []
    merge_dir_n = 0
    split_dir_n = 0

    def _add(task_id: str, alt_id: str, direction: str):
        s = mult_map.setdefault(task_id, set())
        s.add(alt_id)
        details.append({"task": task_id, "alt": alt_id,
                        "direction": direction})
        return direction

    # MERGE-JET / HIDDEN / GENERIC (merge-direction).
    for fam, direction in (("mergejet", "merge"),
                           ("hidden", "merge"),
                           ("generic", "merge")):
        for rec in fams[fam]:
            tid = f"{fam}:{rec['_path']}"
            for row in rec.get("match_rows", []):
                if row.get("triviality") == "GENUINE":
                    cover = str(row.get("cover"))
                    d = str(row.get("d"))
                    fa = str(row.get("fa", cover + d))
                    _add(tid, f"{fa}|{cover}|{d}", direction)
                    merge_dir_n += 1
    # SPLIT-JET (split-direction).
    for rec in fams["splitjet"]:
        tid = f"splitjet:{rec['_path']}"
        for row in rec.get("match_rows", []):
            if row.get("triviality") == "GENUINE":
                _add(tid, f"{row.get('cover')}|{row.get('d')}", "split")
                split_dir_n += 1
    # SAMEN / FORBIT (same-N; direction-neutral for J, counted for ladder).
    for rec in fams["samen"]:
        tid = f"samen:{rec['_path']}"
        for row in rec.get("full_rows", []):
            if row.get("triviality") == "GENUINE":
                _add(tid, f"{row.get('rkey')}|{row.get('edge')}", "samen")
    for rec in fams["forbit"]:
        tid = f"forbit:{rec['_path']}"
        for row in rec.get("full_rows", []):
            if row.get("triviality") == "GENUINE":
                _add(tid,
                      f"{row.get('rung')}|{row.get('rkey')}|"
                      f"{row.get('edge')}", "forbit")
    # TRAJ (direction by kind: stored -> split, else merge).
    for rec in fams["traj"]:
        tid = f"traj:{rec['_path']}"
        direction = ("split" if rec.get("kind") == "stored"
                     else "merge")
        for rung in rec.get("rungs", []):
            for row in rung.get("fiber_full", []):
                if row.get("triviality") == "GENUINE":
                    alt = (f"split:{row.get('vi')}"
                           if rec.get("kind") == "stored"
                           else f"fiber:{row.get('vi')}")
                    _add(tid, alt, direction)
                    if direction == "merge":
                        merge_dir_n += 1
                    else:
                        split_dir_n += 1
            for row in rung.get("rewire_full", []):
                if row.get("triviality") == "GENUINE":
                    _add(tid, f"rewire:{row.get('rkey')}", direction)
                    if direction == "merge":
                        merge_dir_n += 1
                    else:
                        split_dir_n += 1
    n_total = sum(len(v) for v in mult_map.values())
    # Deduplicate TRAJ across rungs already via set; others are per-row.
    return n_total, mult_map, merge_dir_n, split_dir_n, details


def _k_crossed(fams: dict, mult_map: dict) -> dict:
    """K-crossed measurement: GENUINE alt CROSSED by ordinary trajectory.

    Ordinary = TRAJ battery minus zero legs minus H-eigen-certified legs.
    CROSSED = interior modal zero with odd first-nonzero-derivative order
    in the frozen orientation rule.
    """
    crossed_hits = []
    ordinary_n = 0
    for rec in fams["traj"]:
        tid = f"traj:{rec['_path']}"
        ftag = str(rec.get("ftag", ""))
        cert = rec.get("cert", {})
        is_zero_leg = (ftag == "zero") or bool(cert.get("is_zero", False))
        is_eigen = bool(cert.get("is_eigen", False))
        if is_zero_leg or is_eigen:
            continue
        ordinary_n += 1
        genuine_alts = set(mult_map.get(tid, set()))
        if not genuine_alts:
            continue
        cross_by_alt = {c.get("alt"): c for c in rec.get("crossings", [])}
        for alt in genuine_alts:
            c = cross_by_alt.get(alt)
            if c is None:
                continue
            if c.get("class") != "crossed":
                continue
            ori = c.get("orientation") or {}
            comps = ori.get("components", [])
            odd = any(isinstance(cp.get("k"), int) and cp["k"] % 2 == 1
                      for cp in comps if isinstance(cp, dict))
            if odd:
                crossed_hits.append({"traj": tid, "alt": alt,
                                     "zeros": c.get("zeros", [])[:1]})
    return {"ordinary_n": ordinary_n,
            "crossed": bool(crossed_hits),
            "hits": crossed_hits[:8],
            "n_hits": len(crossed_hits)}


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else "data/jet0"
    fams = load(outdir)
    gates = []

    def gate(name, ok, detail=""):
        gates.append({"gate": name, "ok": bool(ok),
                      "detail": str(detail)})

    # ---- counts (exact census vs frozen battery code) ----
    want = {"ord": len(j0.ord_tasks()),
            "mergejet": len(j0.mergejet_tasks()),
            "splitjet": len(j0.splitjet_tasks()),
            "samen": len(j0.samen_tasks()),
            "forbit": len(j0.forbit_tasks()),
            "traj": len(j0.traj_tasks()),
            "lower": len(j0.lower_tasks()),
            "hidden": len(j0.hidden_tasks()),
            "source": len(j0.source_tasks()),
            "generic": len(j0.generic_tasks()),
            "witness": len(j0.witness_tasks())}
    for fam in ("ord", "mergejet", "splitjet", "samen", "forbit",
                "traj", "lower", "hidden", "source", "generic",
                "witness"):
        gate(f"count-{fam}", len(fams[fam]) == want[fam],
             f"got={len(fams[fam])} want={want[fam]}")

    # ---- A-algebra ----
    def _a_ok(rec):
        return bool(rec.get("algebra_ok") and rec.get("deriv_ok")
                    and rec.get("reservoir_jet_ok"))
    a_recs = fams["mergejet"] + fams["hidden"] + fams["generic"]
    a_bad = [r["_path"] for r in a_recs if not _a_ok(r)]
    gate("A-algebra", len(a_recs) > 0 and not a_bad,
         f"n={len(a_recs)} bad={a_bad[:3]}")

    # ---- B-order ----
    def _b_ok(rec):
        oc = rec.get("order", {})
        if not j0.is_order_ok(oc):
            return False
        n = int(oc.get("n", -1))
        method = oc.get("method")
        if n <= j0.N_EXACT_MAX:
            return method == "exact"
        return method == "qr"
    b_bad = [r["_path"] for r in fams["ord"] if not _b_ok(r)]
    b_m_ok = all(int(r.get("m_u", 1)) >= 1 for r in fams["mergejet"])
    gate("B-order", len(fams["ord"]) > 0 and not b_bad and b_m_ok,
         f"n={len(fams['ord'])} bad={b_bad[:3]} m_ok={b_m_ok}")

    # ---- C-recurrence (exact + 12 frozen modal probes) ----
    c_exact_bad = [r["_path"] for r in fams["ord"]
                   if r.get("order", {}).get("method") == "exact"
                   and not r.get("order", {}).get(
                       "recurrence_exact_ok", False)]
    c_probe_ok = True
    c_probe_detail = ""
    try:
        import numpy as np  # noqa: F401
        frozen12 = j0.mergejet_tasks()[:12]
        for t in frozen12:
            sub = m0.build_substrate(t["sub"])
            edge = m0.task_edges(sub, t["ftag"])[t["edge_pos"]]
            psi = m0.build_field(sub, t["ftag"])
            if isinstance(psi, dict):
                mb = t["member"] or "A"
                psi = psi["psi_" + mb]
            import numpy as _np
            rep = j0.series_agreement_report(
                sub["g"], _np.asarray(psi, dtype=_np.complex128),
                list(sub["order"]), *edge)
            if not j0.is_series_agreement_ok(rep):
                c_probe_ok = False
                c_probe_detail = f"probe {t} dev={rep['max_dev']:.3g}"
                break
    except Exception as exc:  # noqa: BLE001
        c_probe_ok = False
        c_probe_detail = f"{type(exc).__name__}: {exc}"
    gate("C-recurrence",
         not c_exact_bad and c_probe_ok,
         f"exact_bad={c_exact_bad[:3]} probe_ok={c_probe_ok} "
         f"{c_probe_detail}")

    # ---- D-decoder (probe recompute: R x U(1) + swap) ----
    d_ok = True
    d_detail = ""
    try:
        import numpy as _np
        frozen = [("ring-8", "uniform", 0), ("j2-L4", "VPLUS", 0),
                  ("triangle", "uniform", 0)]
        for subname, ftag, ei in frozen:
            sub = m0.build_substrate(subname)
            edge = m0.task_edges(sub, ftag)[ei]
            psi = _np.asarray(m0.build_field(sub, ftag),
                              dtype=_np.complex128)
            i, j = edge
            g, order = sub["g"], list(sub["order"])
            for rep in (j0.swap_covariance_jet(g, psi, order, i, j),
                        j0.relabel_covariance_jet(g, psi, order, i, j),
                        j0.u1_covariance_jet(g, psi, order, i, j)):
                if not j0.is_decoder_covariant_ok(rep):
                    d_ok = False
                    d_detail = f"{subname}/{ftag} dev={rep['max_dev']:.3g}"
                    break
            if not d_ok:
                break
    except Exception as exc:  # noqa: BLE001
        d_ok = False
        d_detail = f"{type(exc).__name__}: {exc}"
    gate("D-decoder", d_ok, d_detail or "3 frozen probes covariant")

    # ---- E-regression ----
    e_bad = [r["_path"] for r in
             (fams["mergejet"] + fams["hidden"] + fams["generic"])
             if not r.get("regression_ok")]
    e_split_bad = [r["_path"] for r in fams["splitjet"]
                   if not r.get("pred_ok")]
    gate("E-regression", not e_bad and not e_split_bad,
         f"merge_bad={e_bad[:3]} split_bad={e_split_bad[:3]}")

    # ---- F-orbits ----
    f_bad = [r["_path"] for r in fams["forbit"]
             if not r.get("cross_check_ok")]
    f_orb_filed = all("n_orbits_repro" in r and "n_orbits_vend" in r
                      for r in fams["forbit"])
    gate("F-orbits", len(fams["forbit"]) > 0 and not f_bad and f_orb_filed,
         f"n={len(fams['forbit'])} bad={f_bad[:3]}")

    # ---- G-j2neg (J2-L4 SAMEN complete) ----
    g_want = {(s, f) for s, f in j0.SAMEN_J2 if s == "j2-L4"}
    g_got = {(r.get("sub"), r.get("ftag")) for r in fams["samen"]}
    g_filed = all("n_rewires" in r and "orbits" in r
                  for r in fams["samen"] if r.get("sub") == "j2-L4")
    gate("G-j2neg", g_want <= g_got and g_filed,
         f"want={len(g_want)} got_j2="
         f"{sum(1 for r in fams['samen'] if r.get('sub') == 'j2-L4')}")

    # ---- H-census (complete classes) ----
    def _h_ok_merge(rec):
        c = rec.get("counts", {})
        return (set(c.keys()) >= {"full", "lower-only", "no"}
                and sum(c.values()) == rec.get("n_alts")
                and "triviality_counts" in rec)
    h_bad = [r["_path"] for r in
             (fams["mergejet"] + fams["splitjet"] + fams["hidden"]
              + fams["generic"]) if not _h_ok_merge(r)]
    h_samen_ok = all("n_jet_tests" in r and "triviality_counts" in r
                     for r in fams["samen"])
    h_forbit_ok = all("n_jet_tests" in r and "triviality_counts" in r
                      for r in fams["forbit"])
    h_traj_ok = all("rungs" in r and "crossings" in r
                    for r in fams["traj"])
    gate("H-census", not h_bad and h_samen_ok and h_forbit_ok and h_traj_ok,
         f"bad={h_bad[:3]}")

    # ---- I-theta ----
    i_merge_bad = [r["_path"] for r in fams["mergejet"]
                   if not r.get("theta_counterpart_ok")]
    i_traj_bad = [r["_path"] for r in fams["traj"]
                  if not r.get("theta_history_ok")]
    i_probe_ok = True
    try:
        import numpy as _np
        sub = m0.build_substrate("ring-8")
        edge = m0.task_edges(sub, "uniform")[0]
        psi = _np.asarray(m0.build_field(sub, "uniform"),
                          dtype=_np.complex128)
        g, order = sub["g"], list(sub["order"])
        i, j = edge
        r1 = j0.jet_conjugation_report(g, psi, order, i, j)
        r2 = j0.theta_identity_report(g, psi, order, 1.0)
        i_probe_ok = bool(j0.is_theta_ok(r1) and j0.is_theta_ok(r2))
    except Exception:  # noqa: BLE001
        i_probe_ok = False
    gate("I-theta", not i_merge_bad and not i_traj_bad and i_probe_ok,
         f"merge_bad={i_merge_bad[:2]} traj_bad={i_traj_bad[:2]} "
         f"probe={i_probe_ok}")

    # ---- J-setsurface (Theta apparatus + both directions filed) ----
    n_genuine, mult_map, merge_n, split_n, _det = _genuine_task_sets(fams)
    j_ok = (not i_merge_bad and not i_traj_bad and i_probe_ok)
    gate("J-setsurface", j_ok,
         f"theta_cov={j_ok} merge_gen={merge_n} split_gen={split_n} "
         f"(empty-empty equal; non-empty filed for audit)")

    # ---- K-crossing (refinement converged on all trajs) ----
    k_bad = []
    for rec in fams["traj"]:
        for c in rec.get("crossings", []):
            if c.get("class") not in ("crossed", "touched",
                                      "occupied", "never"):
                k_bad.append(rec["_path"])
                break
            if "zeros" not in c or "orientation" not in c:
                # 'never' legs still file zeros=[] orientation=None.
                if c.get("class") != "never":
                    k_bad.append(rec["_path"])
                    break
    k_filed = all("n_crossed" in r for r in fams["traj"])
    gate("K-crossing", not k_bad and k_filed,
         f"n_traj={len(fams['traj'])} bad={k_bad[:3]}")

    # ---- L-orientation ----
    l_bad = []
    for rec in fams["traj"]:
        for c in rec.get("crossings", []):
            if c.get("zeros"):
                ori = c.get("orientation") or {}
                comps = ori.get("components", None)
                if not isinstance(comps, list) or not comps:
                    l_bad.append(rec["_path"])
                    break
                for cp in comps:
                    if not isinstance(cp, dict) or "k" not in cp:
                        l_bad.append(rec["_path"])
                        break
    gate("L-orientation", not l_bad,
         f"bad={l_bad[:3]}")

    # ---- M-lower ----
    m_bad = []
    for rec in fams["lower"]:
        ana = rec.get("anatomy", {})
        if not all(k in ana for k in ("d", "W", "z1", "R", "Delta",
                                      "full_static")):
            m_bad.append(rec["_path"])
            continue
        if "vs_static_class" not in rec or "jet_abs" not in rec:
            m_bad.append(rec["_path"])
            continue
        if rec.get("feasible"):
            jab = rec.get("jet_abs", [])
            if rec.get("construction") == "z1-zero":
                if len(jab) < 2 or jab[1] > BAR_FP:
                    m_bad.append(rec["_path"])
            elif rec.get("construction") == "z1z2-zero":
                if len(jab) < 3 or jab[1] > BAR_FP or jab[2] > BAR_FP:
                    m_bad.append(rec["_path"])
    gate("M-lower", len(fams["lower"]) > 0 and not m_bad,
         f"n={len(fams['lower'])} bad={m_bad[:3]}")

    # ---- N-hidden ----
    n_bad = [r["_path"] for r in fams["hidden"]
             if not all(k in r for k in ("sector", "cert",
                                         "vacuum_sector", "counts",
                                         "triviality_counts"))]
    gate("N-hidden", len(fams["hidden"]) > 0 and not n_bad,
         f"n={len(fams['hidden'])} bad={n_bad[:3]}")

    # ---- O-source ----
    o_bad = []
    for rec in fams["source"]:
        if "pre_arrival_diagnostic_ok" not in rec:
            o_bad.append(rec["_path"])
            continue
        rungs = rec.get("rungs", [])
        if not rungs or not all("far_dev_vs_vac" in r
                                and "beyond_cone" in r for r in rungs):
            o_bad.append(rec["_path"])
    gate("O-source", len(fams["source"]) > 0 and not o_bad,
         f"n={len(fams['source'])} bad={o_bad[:3]}")

    # ---- P-generic ----
    p_bad = [r["_path"] for r in fams["generic"]
             if not all(k in r for k in ("counts", "triviality_counts",
                                         "codim_first_alt",
                                         "codim_method", "seed"))]
    gate("P-generic", len(fams["generic"]) > 0 and not p_bad,
         f"n={len(fams['generic'])} bad={p_bad[:3]}")

    # ---- Q-unique (no truncation at any GENUINE task) ----
    q_bad = []
    for fam in ("mergejet", "splitjet", "hidden", "generic"):
        for rec in fams[fam]:
            rows = rec.get("match_rows", [])
            if any(r.get("triviality") == "GENUINE" for r in rows):
                if rec.get("n_match_rows", len(rows)) != len(rows):
                    q_bad.append(rec["_path"])
    for fam in ("samen", "forbit"):
        key = "full_rows"
        for rec in fams[fam]:
            rows = rec.get(key, [])
            if any(r.get("triviality") == "GENUINE" for r in rows):
                # Samen/forbit cap at 64/32 with filed counts; require
                # the capped list to cover all full rows when GENUINE.
                n_full = rec.get("n_full", rec.get("n_exact_full",
                                                   len(rows)))
                if n_full != len(rows):
                    q_bad.append(rec["_path"])
    gate("Q-unique", not q_bad, f"bad={q_bad[:3]}")

    # ---- R-compare (six comparison families filed) ----
    r_ok = all(len(fams[f]) > 0 for f in
               ("mergejet", "splitjet", "samen", "forbit", "traj",
                "generic"))
    r_wit = all(any("match_rows" in r or "full_rows" in r or "rungs" in r
                    for r in fams[f])
                for f in ("mergejet", "splitjet", "samen", "forbit",
                          "traj", "generic"))
    gate("R-compare", r_ok and r_wit, "six families filed")

    # ---- S-witness ----
    s_bad = []
    for rec in fams["witness"]:
        if rec.get("compatible") is False:
            # T3 legs with no compat orbit: filed, vacuous.
            continue
        if rec.get("rec_match"):
            a = rec.get("A", {})
            b = rec.get("B", {})
            if not (a.get("krylov_modal_max", 1e18) <= BAR_LEDGER
                    and b.get("krylov_modal_max", 1e18) <= BAR_LEDGER
                    and a.get("return_err", 1e18) <= BAR_LEDGER
                    and b.get("return_err", 1e18) <= BAR_LEDGER
                    and rec.get("series_max_dev", 1e18) <= BAR_LEDGER):
                s_bad.append(rec["_path"])
        else:
            if ("taylor_agree_order" not in rec
                    or "series_max_dev" not in rec):
                s_bad.append(rec["_path"])
    gate("S-witness", not s_bad, f"bad={s_bad[:3]}")

    # ---- X-firewall ----
    import inspect as _inspect
    x_ok = bool(j0.fitted_param_count() == 0
                and j0.is_no_hidden_tuning_ok()
                and j0.is_file_clean_ok(j0.__file__))
    try:
        camp_path = os.path.join(os.path.dirname(__file__),
                                 "jet0_campaign.py")
        ana_path = os.path.join(os.path.dirname(__file__),
                                "jet0_analyze.py")
        x_ok = bool(x_ok and j0.is_file_clean_ok(camp_path)
                    and j0.is_file_clean_ok(ana_path))
        _ = _inspect
    except Exception:  # noqa: BLE001
        x_ok = False
    gate("X-firewall", x_ok, "clean" if x_ok else "symbols/tuning found")

    # ---- measurement for the ladder ----
    krep = _k_crossed(fams, mult_map)
    degen_tasks = [t for t, s in mult_map.items() if len(s) >= 2]
    gate("S-report", True, "one rung filed (see verdict)")

    # ---- verdict ----
    g = {c["gate"]: c["ok"] for c in gates}
    instrument = [c["gate"] for c in gates
                  if c["gate"] != "S-report"]
    incomplete = [k for k in instrument if not g[k]]
    if incomplete:
        verdict = "JET0-INCOMPLETE"
        reason = f"instrument red: {incomplete}"
    elif n_genuine == 0:
        verdict = "JET0-NULL"
        reason = ("zero GENUINE full EXACT matches anywhere "
                  "(T1--T5 only)")
    elif degen_tasks:
        verdict = "JET0-DEGENERATE"
        reason = (f"{n_genuine} GENUINE matches; "
                  f"{len(degen_tasks)} tasks with >=2 inequivalent "
                  f"continuations (e.g. {degen_tasks[0]})")
    elif krep["crossed"]:
        verdict = "JET0-SURFACE"
        reason = (f"{n_genuine} GENUINE unique; "
                  f"{krep['n_hits']} crossed by ordinary trajs "
                  f"(ordinary_n={krep['ordinary_n']})")
    else:
        verdict = "JET0-STATIC"
        reason = (f"{n_genuine} GENUINE unique; none crossed by "
                  f"ordinary trajs (ordinary_n={krep['ordinary_n']})")
    n_pass = sum(1 for c in gates if c["ok"])
    out = {"verdict": verdict, "reason": reason,
           "n_gates": len(gates), "n_pass": n_pass,
           "gates": gates,
           "classification": verdict.replace("JET0-", ""),
           "n_genuine": n_genuine,
           "merge_dir_genuine": merge_n,
           "split_dir_genuine": split_n,
           "degen_tasks": degen_tasks[:8],
           "k_crossed": krep}
    with open(os.path.join(outdir, "verdict.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"{verdict} {n_pass}/{len(gates)} :: {reason}")
