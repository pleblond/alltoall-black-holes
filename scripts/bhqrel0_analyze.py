"""BH-Q-REL-0 analyzer (FROZEN pre-data).

Reads data/bhqrel0/*.json + sibling data/bhqarea0/*.json (read-only),
evaluates the preregistered gates, writes verdict.json. Never crashes:
gate errors file as red. Recomputes every filed census summary from the
filed arrays with an independent code path (separate accumulation code,
never bhqrel0.relational_census).
"""

from __future__ import annotations

import json
import math
import os
import sys
from collections import defaultdict
from itertools import combinations

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np

from bh_graph import bhqrel0 as bqr


def _load(outdir: str, name: str):
    with open(os.path.join(outdir, name)) as fh:
        return json.load(fh)


def _recompute_census(xs, in_idx, ex_idx, icoords) -> dict:
    """Independent pairwise-census recomputation (analyzer code path).

    INT/EXT classes via endpoint grouping + combinations (exact);
    DISJOINT + per-d bins via a chunked row scan with numpy column
    vectors. Same math as the apparatus, separately written.
    """
    xs = np.asarray(list(xs), dtype=float)
    n = int(xs.size)
    in_arr = np.asarray(list(in_idx), dtype=np.int64)
    ex_arr = np.asarray(list(ex_idx), dtype=np.int64)
    ico = np.asarray([list(c) for c in icoords], dtype=np.int64)
    _, ck_in = np.unique(in_arr, return_counts=True) if n else ([], [])
    _, ck_ex = np.unique(ex_arr, return_counts=True) if n else ([], [])
    n_int = int(np.sum(ck_in * (ck_in - 1) // 2)) if n else 0
    n_ext = int(np.sum(ck_ex * (ck_ex - 1) // 2)) if n else 0
    n_pairs = int(n * (n - 1) // 2)
    counts = {"n": n, "n_pairs": n_pairs, "n_int": n_int,
              "n_ext": n_ext, "n_dis": int(n_pairs - n_int - n_ext)}
    if n == 0:
        empty = {"n": 0, "raw": None, "C": None}
        return {"n": 0, "mean": None, "var": None, "degenerate": True,
                "counts": counts, "int": dict(empty),
                "ext": dict(empty), "dis": dict(empty), "bins": {},
                "short": dict(empty), "long": dict(empty)}
    mean = float(np.mean(xs))
    var = float(np.var(xs))
    if var == 0.0 or n < 2:
        cell = {"raw": 0.0, "C": None}
        return {"n": n, "mean": mean, "var": var, "degenerate": True,
                "counts": counts,
                "int": {"n": n_int, **cell},
                "ext": {"n": n_ext, **cell},
                "dis": {"n": counts["n_dis"], **cell},
                "bins": {}, "short": {"n": 0, "raw": None, "C": None},
                "long": {"n": 0, "raw": None, "C": None}}
    dev = xs - mean

    def _cell(tot: float, cnt: int) -> dict:
        if cnt <= 0:
            return {"n": 0, "raw": None, "C": None}
        raw = float(tot / cnt)
        return {"n": int(cnt), "raw": raw, "C": float(raw / var)}

    grp_in: dict = defaultdict(list)
    grp_ex: dict = defaultdict(list)
    for a in range(n):
        grp_in[int(in_arr[a])].append(a)
        grp_ex[int(ex_arr[a])].append(a)
    tot_in = sum(float(dev[a] * dev[b])
                 for members in grp_in.values() for a, b in
                 combinations(members, 2))
    cnt_in = sum(len(m) * (len(m) - 1) // 2 for m in grp_in.values())
    tot_ex = sum(float(dev[a] * dev[b])
                 for members in grp_ex.values() for a, b in
                 combinations(members, 2))
    cnt_ex = sum(len(m) * (len(m) - 1) // 2 for m in grp_ex.values())
    tot_dis = 0.0
    cnt_dis = 0
    per_d: dict = {}
    for a in range(n):
        b = np.arange(a + 1, n)
        if b.size == 0:
            continue
        shared = (in_arr[b] == in_arr[a]) | (ex_arr[b] == ex_arr[a])
        cols = b[~shared]
        if cols.size == 0:
            continue
        prods = dev[a] * dev[cols]
        tot_dis += float(prods.sum())
        cnt_dis += int(cols.size)
        dd = np.abs(ico[cols] - ico[a]).sum(axis=1)
        for val in np.unique(dd):
            sel = dd == val
            key = int(val)
            prev = per_d.get(key, [0.0, 0])
            prev[0] += float(prods[sel].sum())
            prev[1] += int(sel.sum())
            per_d[key] = prev
    bins = {}
    for dd in sorted(per_d):
        tot, cnt = per_d[dd]
        bins[str(dd)] = _cell(tot, cnt)
    short_keys = [d for d in per_d if d in (1, 2)]
    stot = sum(per_d[d][0] for d in short_keys)
    scnt = sum(per_d[d][1] for d in short_keys)
    top2 = sorted(per_d)[-2:]
    ltot = sum(per_d[d][0] for d in top2)
    lcnt = sum(per_d[d][1] for d in top2)
    return {"n": n, "mean": mean, "var": var, "degenerate": False,
            "counts": counts, "int": _cell(tot_in, cnt_in),
            "ext": _cell(tot_ex, cnt_ex),
            "dis": _cell(tot_dis, cnt_dis), "bins": bins,
            "short": _cell(stot, scnt), "long": _cell(ltot, lcnt)}


def _cells_match(filed: dict, re: dict, atol: float = 1e-9) -> bool:
    if filed["n"] != re["n"]:
        return False
    for key in ("raw", "C"):
        fv, rv = filed[key], re[key]
        if (fv is None) != (rv is None):
            return False
        if fv is not None and abs(float(fv) - float(rv)) > atol:
            return False
    return True


def _census_match(filed: dict, re: dict, atol: float = 1e-9) -> bool:
    if filed.get("failed") or filed["n"] != re["n"]:
        return False
    if filed["degenerate"] != re["degenerate"]:
        return False
    if filed["n"] == 0:
        return True
    if abs(filed["mean"] - re["mean"]) > atol:
        return False
    if abs(filed["var"] - re["var"]) > atol:
        return False
    if filed["counts"] != re["counts"]:
        return False
    for key in ("int", "ext", "dis", "short", "long"):
        if not _cells_match(filed[key], re[key], atol):
            return False
    if set(filed["bins"]) != set(re["bins"]):
        return False
    for key in filed["bins"]:
        if not _cells_match(filed["bins"][key], re["bins"][key], atol):
            return False
    return True


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    outdir = args[0] if len(args) > 0 else "data/bhqrel0"
    areadir = args[1] if len(args) > 1 else "data/bhqarea0"
    gates: dict = {}
    notes: dict = {}

    def gate(name: str, ok: bool, note: str = ""):
        gates[name] = bool(ok)
        if note:
            notes[name] = note

    # ---- load ----
    rel_recs: dict = {}
    regression = audit = redundant = None
    area_recs: dict = {}
    load_err = []
    try:
        for r in bqr.R_LADDER:
            for st in bqr.HEADLINE_STATES:
                rel_recs[("headline", st, r)] = _load(
                    outdir, f"rel_headline_{st}_r{int(r):02d}.json")
        for r in bqr.R_LADDER:
            rel_recs[("control", "vacuum", r)] = _load(
                outdir, f"rel_control_vacuum_r{int(r):02d}.json")
        regression = _load(outdir, "regression.json")
        audit = _load(outdir, "audit.json")
        redundant = _load(outdir, "redundant.json")
        for r in bqr.R_LADDER:
            for st in bqr.HEADLINE_STATES:
                area_recs[("headline", st, r)] = _load(
                    areadir, f"rung_headline_{st}_r{int(r):02d}.json")
        for r in bqr.R_LADDER:
            area_recs[("control", "vacuum", r)] = _load(
                areadir, f"rung_control_vacuum_r{int(r):02d}.json")
    except Exception as exc:  # noqa: BLE001 - filed, never raised
        load_err.append(f"{type(exc).__name__}: {exc}")

    n_rel = len(rel_recs)
    gate("G-INST", not load_err and n_rel == 50
         and regression is not None and audit is not None
         and redundant is not None and len(area_recs) == 50,
         f"rel={n_rel}/50 area={len(area_recs)}/50 err={load_err}")

    hv = lambda r: rel_recs.get(("headline", "vacuum", r))  # noqa: E731

    # ---- A/B/C/D ----
    try:
        gate("G-A", bool(regression["formula_ok"]))
        gate("G-B", bool(regression["endpoints_ok"]))
        gate("G-C", bool(regression["expansion_ok"]))
        d_ok = bool(regression["core_generator_ok"]) and all(
            regression["geometry_ok"].values()) and \
            regression["margin"] == bqr.MARGIN and \
            list(regression["ladder"]) == list(bqr.R_LADDER)
        gate("G-D", d_ok)
        p_ok = all(regression["partition_ok"].values()) and \
            bool(regression["covar_math_ok"]) and \
            bool(regression["binning_ok"]) and \
            bool(regression["degenerate_ok"])
        gate("G-PART-REG", p_ok)
    except Exception as exc:  # noqa: BLE001
        for g in ("G-A", "G-B", "G-C", "G-D", "G-PART-REG"):
            gate(g, False, f"eval-error: {exc}")

    # ---- REGR: isolated-leg agreement vs filed BHQAREA0 data ----
    try:
        regr_ok = True
        regr_notes = []
        sha_match = 0
        for key in sorted(rel_recs, key=str):
            rec = rel_recs[key]
            arec = area_recs[key]
            if rec["n_bnd"] != arec["n_bnd"]:
                regr_ok = False
                regr_notes.append(f"{key}: n_bnd")
            tol = bqr.REGR_ATOL * max(1.0, abs(arec["S"]))
            if abs(rec["S"] - arec["S"]) > tol:
                regr_ok = False
                regr_notes.append(f"{key}: S")
            if abs(rec["hbar"] - arec["hbar"]) > bqr.REGR_ATOL:
                regr_ok = False
                regr_notes.append(f"{key}: hbar")
            xa = np.asarray(rec["xs"], dtype=float)
            xb = np.asarray(arec["xs"], dtype=float)
            if xa.shape != xb.shape:
                regr_ok = False
                regr_notes.append(f"{key}: xs-shape")
            elif xa.size and float(np.mean(np.abs(xa - xb))) > \
                    bqr.REGR_ATOL:
                regr_ok = False
                regr_notes.append(f"{key}: xs")
            if rec["psi_sha256"] == arec["psi_sha256"]:
                sha_match += 1
        gate("G-REGR", regr_ok, "; ".join(regr_notes[:5]) +
             f" sha_match={sha_match}/50")
    except Exception as exc:  # noqa: BLE001
        gate("G-REGR", False, f"eval-error: {exc}")

    # ---- PART: per-record partition + endpoint audit ----
    try:
        part_ok = True
        part_notes = []
        for key in sorted(rel_recs, key=str):
            rec = rel_recs[key]
            n_def = rec["n_defined"]
            if rec["n_defined"] + rec["zero_pairs"] != rec["n_bnd"]:
                part_ok = False
                part_notes.append(f"{key}: count-split")
            if rec["n_bnd"] != rec["dim3_cut"]:
                part_ok = False
                part_notes.append(f"{key}: cut-mismatch")
            if len(rec["xs"]) != n_def or len(rec["in_idx"]) != n_def \
                    or len(rec["ex_idx"]) != n_def \
                    or len(rec["icoords"]) != n_def:
                part_ok = False
                part_notes.append(f"{key}: array-len")
            cnt = rec["cen_x"]["counts"]
            if cnt["n"] != n_def or cnt["n_pairs"] != \
                    n_def * (n_def - 1) // 2:
                part_ok = False
                part_notes.append(f"{key}: count-n")
            if cnt["n_int"] + cnt["n_ext"] + cnt["n_dis"] != \
                    cnt["n_pairs"]:
                part_ok = False
                part_notes.append(f"{key}: count-sum")
            if rec["cen_s"]["counts"] != cnt:
                part_ok = False
                part_notes.append(f"{key}: xs-counts")
            uniq = len(set(zip(rec["in_idx"], rec["ex_idx"]))) == n_def
            if not uniq or not rec["pairs_unique_ok"]:
                part_ok = False
                part_notes.append(f"{key}: endpoint-uniq")
            if rec["zero_pairs"] == 0:
                struct = regression["structural_counts"][str(rec["r"])]
                for kk in ("n", "n_pairs", "n_int", "n_ext", "n_dis"):
                    if cnt[kk] != struct[kk]:
                        part_ok = False
                        part_notes.append(f"{key}: struct-{kk}")
                        break
        gate("G-PART", part_ok, "; ".join(part_notes[:5]))
    except Exception as exc:  # noqa: BLE001
        gate("G-PART", False, f"eval-error: {exc}")

    # ---- F: census re-verification from filed arrays ----
    try:
        from bh_graph import qinfo0 as _q0

        f_ok = True
        f_notes = []
        for key in sorted(rel_recs, key=str):
            rec = rel_recs[key]
            xs = rec["xs"]
            if xs:
                arr = np.asarray(xs, dtype=float)
                chk = {"mean": float(np.mean(arr)),
                       "median": float(np.median(arr)),
                       "var": float(np.var(arr)),
                       "meansq": float(np.mean(arr ** 2))}
                for kk, vv in chk.items():
                    if abs(vv - rec["stats"][kk]) > bqr.CENSUS_ATOL:
                        f_ok = False
                        f_notes.append(f"{key}: {kk}-mismatch")
                        break
                qs = np.quantile(arr, list(bqr._bq.QUANTILES))
                for got, want in zip(qs, rec["stats"]["quantiles"]):
                    if abs(float(got) - float(want)) > bqr.CENSUS_ATOL:
                        f_ok = False
                        f_notes.append(f"{key}: q-mismatch")
                        break
            re_x = _recompute_census(xs, rec["in_idx"], rec["ex_idx"],
                                     rec["icoords"])
            if not _census_match(rec["cen_x"], re_x):
                f_ok = False
                f_notes.append(f"{key}: cen_x-mismatch")
            ss = [_q0.h2_binary(min(1.0, max(0.0, 0.5 - float(x))))
                  for x in xs]
            if any(v is None for v in ss):
                f_ok = False
                f_notes.append(f"{key}: s-leg-domain")
            re_s = _recompute_census(ss, rec["in_idx"], rec["ex_idx"],
                                     rec["icoords"])
            if not _census_match(rec["cen_s"], re_s):
                f_ok = False
                f_notes.append(f"{key}: cen_s-mismatch")
        gate("G-F", f_ok, "; ".join(f_notes[:5]))
    except Exception as exc:  # noqa: BLE001
        gate("G-F", False, f"eval-error: {exc}")

    # ---- O: firewall + params ----
    try:
        gate("G-O", bool(audit["firewall_ok"])
             and audit["fitted_params"] == 0
             and bool(audit["battery_counts_ok"])
             and audit["corr_bar"] == bqr.CORR_BAR
             and audit["decay_frac"] == bqr.DECAY_FRAC
             and list(audit["short_d"]) == list(bqr.SHORT_D))
    except Exception as exc:  # noqa: BLE001
        gate("G-O", False, f"eval-error: {exc}")

    # ---- S/T presence ----
    try:
        gate("G-S", all(("headline", st, r) in rel_recs
                        for st in bqr.HEADLINE_STATES
                        for r in bqr.R_LADDER))
        gate("G-T", all(("control", "vacuum", r) in rel_recs
                        for r in bqr.R_LADDER))
    except Exception as exc:  # noqa: BLE001
        gate("G-S", False, f"eval-error: {exc}")
        gate("G-T", False, f"eval-error: {exc}")

    # ---- DET: redundant determinism ----
    try:
        import hashlib as _hl

        det_ok = True
        pairs = [(5, "headline", "vacuum"), (5, "control", "vacuum")]
        for i, (r, var, stt) in enumerate(pairs):
            rec = dict(rel_recs[(var, stt, r)])
            rec.pop("kind", None)
            rec.pop("_git", None)
            blob = json.dumps(rec, sort_keys=True, allow_nan=False)
            h = _hl.sha256(blob.encode()).hexdigest()
            if h != redundant["hashes"][i]:
                det_ok = False
        gate("G-DET", det_ok)
    except Exception as exc:  # noqa: BLE001
        gate("G-DET", False, f"eval-error: {exc}")

    # ---- measurement: headline-vacuum x-leg ladder ----
    max_c = 0.0
    n_defined_c = 0
    decay_ok = True
    decay_table = []
    class_table = []
    try:
        for r in bqr.R_LADDER:
            rec = hv(r)
            cen = rec["cen_x"]
            row = {"r": r, "degenerate": cen["degenerate"]}
            for kk in ("int", "ext", "dis"):
                cc = cen[kk]["C"]
                row[kk] = cc
                if cc is not None:
                    n_defined_c += 1
                    max_c = max(max_c, abs(float(cc)))
            for dd, cell in cen["bins"].items():
                if cell["C"] is not None:
                    n_defined_c += 1
                    max_c = max(max_c, abs(float(cell["C"])))
            sh = cen["short"]["C"]
            lo = cen["long"]["C"]
            row["short"] = sh
            row["long"] = lo
            if sh is not None and lo is not None:
                rung_ok = abs(float(lo)) < max(
                    bqr.CORR_BAR, bqr.DECAY_FRAC * abs(float(sh)))
                decay_table.append({"r": r, "short": sh, "long": lo,
                                    "ok": bool(rung_ok)})
                if not rung_ok:
                    decay_ok = False
            else:
                decay_table.append({"r": r, "short": sh, "long": lo,
                                    "ok": None})
            class_table.append(row)
        gate("G-MEAS", True, f"maxC={max_c:.4f} nC={n_defined_c} "
                             f"decay_ok={decay_ok}")
    except Exception as exc:  # noqa: BLE001
        gate("G-MEAS", False, f"eval-error: {exc}")

    # ---- s-leg + discriminant summaries (descriptive, not gated) ----
    try:
        s_max = 0.0
        for r in bqr.R_LADDER:
            cen = hv(r)["cen_s"]
            for kk in ("int", "ext", "dis"):
                if cen[kk]["C"] is not None:
                    s_max = max(s_max, abs(float(cen[kk]["C"])))
            for cell in cen["bins"].values():
                if cell["C"] is not None:
                    s_max = max(s_max, abs(float(cell["C"])))
        disc = {}
        for key in sorted(rel_recs, key=str):
            var, stt, r = key
            if (var, stt) == ("headline", "vacuum"):
                continue
            cx = rel_recs[key]["cen_x"]
            vals = [cx[kk]["C"] for kk in ("int", "ext", "dis")]
            disc[f"{var}/{stt}/r{r}"] = {
                "degenerate": cx["degenerate"], "int": vals[0],
                "ext": vals[1], "dis": vals[2],
                "short": cx["short"]["C"], "long": cx["long"]["C"]}
        notes["S-LEG"] = f"s_maxC={s_max:.4f}"
        notes["DISC"] = json.dumps(disc, sort_keys=True)
    except Exception as exc:  # noqa: BLE001
        notes["S-LEG"] = f"eval-error: {exc}"

    # ---- verdict ----
    required = ["G-INST", "G-A", "G-B", "G-C", "G-D", "G-PART-REG",
                "G-REGR", "G-PART", "G-F", "G-O", "G-DET", "G-MEAS"]
    if any(not gates.get(g) for g in required):
        verdict = "BHQREL0-INCOMPLETE"
    elif n_defined_c == 0 or max_c < bqr.CORR_BAR:
        verdict = "BHQREL0-INDEPENDENT"
    elif decay_ok:
        verdict = "BHQREL0-STRUCTURED"
    else:
        verdict = "BHQREL0-CORRELATED"

    verdict_doc = {
        "campaign": "BH-Q-REL-0",
        "verdict": verdict,
        "gates": gates,
        "notes": notes,
        "measurement": {
            "max_c_x": max_c,
            "n_defined_c": n_defined_c,
            "corr_bar": bqr.CORR_BAR,
            "decay_frac": bqr.DECAY_FRAC,
            "decay_ok": decay_ok,
            "class_table": class_table,
            "decay_table": decay_table,
        },
    }
    with open(os.path.join(outdir, "verdict.json"), "w") as fh:
        json.dump(verdict_doc, fh, allow_nan=False)
        fh.write("\n")
    print(f"VERDICT {verdict}", flush=True)
    red = [g for g, v in gates.items() if not v]
    print(f"GATES {sum(gates.values())}/{len(gates)} red={red}",
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
