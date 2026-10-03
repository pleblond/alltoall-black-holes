"""JET-1 verdict analyzer (FROZEN pre-data; decision tree only).

Reads the read-only JET-0 bank (data/jet0/*.json + verdict.json) and the 15
JET-1 compat witnesses (data/jet1/compat_*.json), evaluates every preregistered
gate (docs/jet1-prereg.md section 7), writes data/jet1/verdict.json. No
bar/ladder/outcome may change post-data: failures file as INCOMPLETE.

Ladder (prereg section 8, precedence):
  INCOMPLETE > DEGENERATE > SURFACE > STATIC > NULL.
"""

from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from bh_graph import jet0 as j0  # noqa: E402
from bh_graph import jet1 as j1  # noqa: E402
import jet0_analyze as j0a  # noqa: E402


def _load_compat(compatdir: str) -> list:
    rows = []
    for path in sorted(glob.glob(os.path.join(compatdir, "compat_*.json"))):
        with open(path) as f:
            rec = json.load(f)
        rec["_path"] = os.path.basename(path)
        rows.append(rec)
    return rows


def _rerun_frozen_analyzer(bankdir: str) -> dict:
    """Rerun frozen scripts/jet0_analyze.py on a bank copy (originals untouched).

    Returns the regenerated verdict dict.
    """
    ana = os.path.join(os.path.dirname(__file__), "jet0_analyze.py")
    with tempfile.TemporaryDirectory(prefix="jet1_rerun_") as tmpd:
        for path in sorted(glob.glob(os.path.join(bankdir, "*.json"))):
            if os.path.basename(path) == "verdict.json":
                continue
            shutil.copy(path, os.path.join(tmpd, os.path.basename(path)))
        proc = subprocess.run(
            [sys.executable, ana, tmpd],
            capture_output=True, text=True, timeout=600)
        if proc.returncode != 0:
            raise RuntimeError(f"frozen rerun failed: {proc.stderr[-2000:]}")
        with open(os.path.join(tmpd, "verdict.json")) as f:
            return json.load(f)


def main():
    """CLI entry point (see module docstring)."""
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", default="data/jet0")
    ap.add_argument("--compat", default="data/jet1")
    ap.add_argument("--out", default="data/jet1/verdict.json")
    a = ap.parse_args()
    bankdir, compatdir, outpath = a.bank, a.compat, a.out

    fams = j0a.load(bankdir)
    compat = _load_compat(compatdir)
    by_traj = {r.get("traj"): r for r in compat}
    with open(os.path.join(bankdir, "verdict.json")) as f:
        banked = json.load(f)
    gates = []

    def gate(name, ok, detail=""):
        gates.append({"gate": name, "ok": bool(ok),
                      "detail": str(detail)})

    # ---- A-provenance ----
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
    counts_ok = all(len(fams[f]) == want[f] for f in want)
    total_ok = sum(len(fams[f]) for f in want) == 496
    red = [g["gate"] for g in banked.get("gates", []) if not g.get("ok")]
    verdict_ok = (banked.get("verdict") == "JET0-INCOMPLETE"
                  and banked.get("n_gates") == 32
                  and banked.get("n_pass") == 31
                  and red == ["F-orbits"])
    bad_forbit = sorted(r["_path"] for r in fams["forbit"]
                        if not r.get("cross_check_ok"))
    conjunct_ok = (bad_forbit == sorted(j1.KNOWN_BAD_FORBIT))
    for r in fams["forbit"]:
        ck = r.get("cross_check", {})
        if not r.get("cross_check_ok"):
            if not (ck.get("n_rewires") and ck.get("n_cospec")
                    and ck.get("n_iso") and ck.get("n_nontrivial")
                    and ck.get("compat_keys") is False):
                conjunct_ok = False
    phys_ok = (banked.get("n_genuine") == 0
               and banked.get("merge_dir_genuine") == 0
               and banked.get("split_dir_genuine") == 0
               and banked.get("k_crossed", {}).get("ordinary_n") == 18
               and banked.get("k_crossed", {}).get("crossed") is False
               and banked.get("k_crossed", {}).get("hits") == []
               and banked.get("k_crossed", {}).get("n_hits") == 0)
    refs_ok = all(j1.is_ref_ok(n) for n in j1.REF_SHA256)
    a_ok = bool(counts_ok and total_ok and verdict_ok and conjunct_ok
                and phys_ok and refs_ok)
    gate("A-provenance", a_ok,
         f"counts={counts_ok} total={total_ok} verdict={verdict_ok} "
         f"conjunct={conjunct_ok} phys={phys_ok} refs={refs_ok}")

    # ---- A-rerun (frozen analyzer end-to-end on a bank copy) ----
    rerun: dict = {}
    rerun_ok = False
    rerun_detail = ""
    try:
        rerun = _rerun_frozen_analyzer(bankdir)
        rerun_ok = bool(rerun == banked)
        if not rerun_ok:
            keys = sorted(set(rerun) | set(banked))
            diff = [k for k in keys if rerun.get(k) != banked.get(k)]
            rerun_detail = f"diff={diff[:5]}"
    except Exception as exc:  # noqa: BLE001
        rerun_detail = f"{type(exc).__name__}: {exc}"
    gate("A-rerun", rerun_ok, rerun_detail or "regenerated verdict identical")

    # ---- B-semantics ----
    b_ok = (len(compat) == 15 and len(by_traj) == 15
            and set(by_traj) == set(j0.FORBIT_KEYS))
    for r in compat:
        ladder = r.get("ladder", [])
        if len(ladder) != 6:
            b_ok = False
        for rk in r.get("searched_ours", []):
            if len(r.get("ours_vec", {}).get(rk, [])) != 6:
                b_ok = False
        for rk in r.get("searched_vend", []):
            if len(r.get("vend_vec", {}).get(rk, [])) != 6:
                b_ok = False
        if "ever_ours" not in r or "ever_vend" not in r:
            b_ok = False
    gate("B-semantics", b_ok, f"n={len(compat)}")

    # ---- C-bitwise ----
    c_bad = [r["_path"] for r in compat
             if not (j1.is_per_rung_ok(r) and j1.is_searched_ok(r))]
    n_mismatch = sum(int(r.get("n_mismatch", -1)) for r in compat)
    n_compared = sum(int(r.get("n_compared", 0)) for r in compat)
    gate("C-bitwise", not c_bad and n_mismatch == 0,
         f"bad={c_bad[:3]} mismatch={n_mismatch} compared={n_compared}")

    # ---- D-ever ----
    d_bad = [r["_path"] for r in compat if not j1.is_ever_ok(r)]
    gate("D-ever", not d_bad, f"bad={d_bad[:3]}")

    # ---- E-orbits ----
    e_bad = [r["_path"] for r in compat if not j1.is_orbit_ok(r)]
    gate("E-orbits", not e_bad, f"bad={e_bad[:3]}")

    # ---- F-search ----
    f_bad = [r["_path"] for r in compat if not j1.is_search_counts_ok(r)]
    gate("F-search", not f_bad, f"bad={f_bad[:3]}")

    # ---- G-allfalse ----
    g_ok = True
    g_wit: dict = {}
    for traj in j1.KNOWN_BAD_TRAJ:
        r = by_traj.get(traj)
        if r is None:
            g_ok = False
            continue
        both = r.get("allfalse_both", [])
        ours = r.get("allfalse_ours", [])
        vend = r.get("allfalse_vend", [])
        g_wit[traj] = both
        if not both or ours != vend or sorted(both) != sorted(ours):
            g_ok = False
            continue
        for rk in both:
            if any(r.get("ours_vec", {}).get(rk, [True])) or \
                    any(r.get("vend_vec", {}).get(rk, [True])):
                g_ok = False
    gate("G-allfalse", g_ok,
         f"witness_n={ {k: len(v) for k, v in g_wit.items()} }")

    # ---- H-controls ----
    h_bad = [r["_path"] for r in compat
             if r.get("traj") not in j1.KNOWN_BAD_TRAJ
             and not j1.is_cell_ok(r)]
    h_n = sum(1 for r in compat if r.get("traj") not in j1.KNOWN_BAD_TRAJ)
    gate("H-controls", h_n == 13 and not h_bad,
         f"n={h_n} bad={h_bad[:3]}")

    # ---- I-replay ----
    i_ok = False
    i_detail = ""
    if rerun:
        i_red = [g["gate"] for g in rerun.get("gates", [])
                 if not g.get("ok")]
        i_ok = bool(
            i_red == ["F-orbits"] and rerun.get("n_genuine") == 0
            and rerun.get("k_crossed", {}).get("ordinary_n") == 18
            and rerun.get("k_crossed", {}).get("n_hits") == 0)
        i_detail = f"red={i_red} n_genuine={rerun.get('n_genuine')}"
    gate("I-replay", i_ok, i_detail or "no rerun")

    # ---- J-surface + K-crossing (frozen-import measurement) ----
    n_genuine, mult_map, merge_n, split_n, _det = \
        j0a._genuine_task_sets(fams)
    krep = j0a._k_crossed(fams, mult_map)
    j1_syms = ("triviality_class", "classify_pair", "jet_equality_class",
               "jet_equal_exact", "jet_equal_quotient", "GENUINE")
    j_clean = not any(hasattr(j1, s) for s in j1_syms)
    j_ok = bool(n_genuine == 0 and j_clean)
    gate("J-surface", j_ok,
         f"n_genuine={n_genuine} merge={merge_n} split={split_n} "
         f"clean={j_clean}")
    k1_syms = ("crossing_refine", "crossing_classify", "orientation_of",
               "mismatch_eval", "crossing_class")
    k_clean = not any(hasattr(j1, s) for s in k1_syms)
    k_ok = bool(krep == banked.get("k_crossed") and k_clean)
    gate("K-crossing", k_ok,
         f"ordinary={krep.get('ordinary_n')} hits={krep.get('n_hits')} "
         f"clean={k_clean}")

    # ---- X-firewall ----
    here = os.path.dirname(__file__)
    x_ok = bool(j1.fitted_param_count() == 0
                and j1.is_no_hidden_tuning_ok()
                and j0.is_file_clean_ok(j1.__file__)
                and j0.is_file_clean_ok(os.path.join(here, "jet1_campaign.py"))
                and j0.is_file_clean_ok(os.path.join(here, "jet1_analyze.py")))
    gate("X-firewall", x_ok, "clean" if x_ok else "symbols/tuning found")

    # ---- verdict ----
    degen_tasks = [t for t, s in mult_map.items() if len(s) >= 2]
    incomplete = [g["gate"] for g in gates if not g["ok"]]
    if incomplete:
        verdict = "JET1-INCOMPLETE"
        reason = f"instrument red: {incomplete}"
    elif n_genuine == 0:
        verdict = "JET1-NULL"
        reason = ("zero GENUINE full EXACT matches anywhere under "
                  "unchanged JET definitions (T1--T5 only)")
    elif degen_tasks:
        verdict = "JET1-DEGENERATE"
        reason = (f"{n_genuine} GENUINE matches; "
                  f"{len(degen_tasks)} tasks with >=2 inequivalent "
                  f"continuations (e.g. {degen_tasks[0]})")
    elif krep["crossed"]:
        verdict = "JET1-SURFACE"
        reason = (f"{n_genuine} GENUINE unique; "
                  f"{krep['n_hits']} crossed by ordinary trajs "
                  f"(ordinary_n={krep['ordinary_n']})")
    else:
        verdict = "JET1-STATIC"
        reason = (f"{n_genuine} GENUINE unique; none crossed by "
                  f"ordinary trajs (ordinary_n={krep['ordinary_n']})")
    n_pass = sum(1 for c in gates if c["ok"])
    out = {"verdict": verdict, "reason": reason,
           "n_gates": len(gates), "n_pass": n_pass,
           "gates": gates,
           "classification": verdict.replace("JET1-", ""),
           "malformed": ("ours filtered ever-compatible keys vs vendored "
                         "all searched keys (incl. all-False rows)"),
           "per_rung_mismatch": n_mismatch,
           "per_rung_compared": n_compared,
           "searched_equal": not c_bad,
           "ever_equal": not d_bad,
           "orbit_equal": not e_bad,
           "allfalse_witness": {k: v for k, v in g_wit.items()},
           "n_genuine": n_genuine,
           "merge_dir_genuine": merge_n,
           "split_dir_genuine": split_n,
           "degen_tasks": degen_tasks[:8],
           "k_crossed": krep,
           "policy": ("read-only bank; 15 compat witnesses + analyzer "
                      "rerun + pins + full suite; no 496-task rerun")}
    os.makedirs(os.path.dirname(outpath) or ".", exist_ok=True)
    with open(outpath, "w") as f:
        json.dump(out, f, indent=1)
    print(f"{verdict} {n_pass}/{len(gates)} :: {reason}")


if __name__ == "__main__":
    main()
