"""BH-Q-REL-0 analyzer (FROZEN pre-data).

Reads data/bhqrel0/*.json + sibling data/bhqarea0/*.json (read-only),
evaluates the spec legs A--K as preregistered gates, writes
verdict.json. Never crashes: gate errors file as red. Recomputes every
filed certificate number with independent code paths (never the
apparatus audit/census functions).

Verdict ladder (frozen order): INCOMPLETE (apparatus/regression red,
or unexpected joint without an E/F battery) > MEASURE-DEBT (complete,
no earned joint) > AREA-SAME / AREA-RENORM / NONAREA (conditional on
a joint; criteria frozen, adjudicated-as-gated without joint data).
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
    DISJOINT + per-d bins via a row scan with numpy column vectors.
    Same math as the apparatus, separately written.
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


def _marginals_msb_first(psi, n_qubits: int) -> list:
    """Single-qubit marginal entropies, MSB-first reshape convention.

    Independent convention from the apparatus (LSB-first); leg-C
    states are qubit-symmetric, so all marginals agree across
    conventions (symmetry asserted by the caller).
    """
    psi = np.asarray(psi, dtype=np.complex128).ravel()
    n = int(n_qubits)
    out = []
    for k in range(n):
        rest = list(range(n))
        rest.remove(k)
        order = [k] + rest
        ten = psi.reshape((2,) * n)
        moved = np.transpose(ten, order).reshape(2, 2 ** (n - 1))
        rho = moved @ moved.conj().T
        vals = np.linalg.eigvalsh((rho + rho.conj().T) / 2.0)
        vals = np.clip(vals.real, 0.0, None)
        out.append(float(-sum(v * math.log2(v) for v in vals if v > 0)))
    return out


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
    audits: dict = {}
    smallctrl = regression = audit = redundant = None
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
        for cid in bqr.CANDIDATE_IDS:
            audits[cid] = _load(outdir, f"jointaudit_{cid}.json")
        smallctrl = _load(outdir, "smallctrl.json")
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
    gate("G-INST", not load_err and n_rel == 50 and len(audits) == 5
         and smallctrl is not None and regression is not None
         and audit is not None and redundant is not None
         and len(area_recs) == 50,
         f"rel={n_rel}/50 audits={len(audits)}/5 "
         f"area={len(area_recs)}/50 err={load_err}")

    # ---- A/B/C/D (apparatus booleans) ----
    try:
        gate("G-A0", bool(regression["formula_ok"])
             and bool(regression["endpoints_ok"])
             and bool(regression["expansion_ok"]))
        d_ok = bool(regression["core_generator_ok"]) and all(
            regression["geometry_ok"].values()) and \
            regression["margin"] == bqr.MARGIN and \
            list(regression["ladder"]) == list(bqr.R_LADDER)
        gate("G-D0", d_ok)
        m_ok = all(regression["partition_ok"].values()) and \
            bool(regression["covar_math_ok"]) and \
            bool(regression["binning_ok"]) and \
            bool(regression["degenerate_ok"]) and \
            bool(regression["t_identity_ok"]) and \
            bool(regression["partial_trace_ok"]) and \
            bool(regression["jointaudit_ok"]) and \
            bool(regression["conditional_logic_ok"])
        gate("G-MACH", m_ok)
    except Exception as exc:  # noqa: BLE001
        for g in ("G-A0", "G-D0", "G-MACH"):
            gate(g, False, f"eval-error: {exc}")

    # ---- A: marginal regression vs filed BHQAREA0 data ----
    try:
        from bh_graph import qinfo0 as _q0

        a_ok = True
        a_notes = []
        sha_match = 0
        for key in sorted(rel_recs, key=str):
            rec = rel_recs[key]
            arec = area_recs[key]
            if rec["n_bnd"] != arec["n_bnd"]:
                a_ok = False
                a_notes.append(f"{key}: n_bnd")
            tol = bqr.REGR_ATOL * max(1.0, abs(arec["S"]))
            if abs(rec["S"] - arec["S"]) > tol:
                a_ok = False
                a_notes.append(f"{key}: S")
            if abs(rec["hbar"] - arec["hbar"]) > bqr.REGR_ATOL:
                a_ok = False
                a_notes.append(f"{key}: hbar")
            xa = np.asarray(rec["xs"], dtype=float)
            xb = np.asarray(arec["xs"], dtype=float)
            if xa.shape != xb.shape:
                a_ok = False
                a_notes.append(f"{key}: xs-shape")
            elif xa.size and float(np.mean(np.abs(xa - xb))) > \
                    bqr.REGR_ATOL:
                a_ok = False
                a_notes.append(f"{key}: xs")
            probs = [min(1.0, max(0.0, 0.5 - float(x)))
                     for x in rec["xs"]]
            s_re = sum(_q0.h2_binary(p) for p in probs)
            if abs(s_re - rec["S"]) > tol:
                a_ok = False
                a_notes.append(f"{key}: h2-sum")
            if rec["psi_sha256"] == arec["psi_sha256"]:
                sha_match += 1
        gate("G-A", a_ok, "; ".join(a_notes[:5]) +
             f" sha_match={sha_match}/50")
    except Exception as exc:  # noqa: BLE001
        gate("G-A", False, f"eval-error: {exc}")

    # ---- B: joint-object legitimacy audit re-verification ----
    joint_exists = False
    try:
        from bh_graph import qinfo0 as _q0

        b_ok = True
        b_notes = []
        want = {"product": bqr.REJECT_INDEPENDENCE,
                "sdweight": bqr.REJECT_SAMPLE_SPACE,
                "modehq": bqr.REJECT_WRONG_OBJECT,
                "haarjoint": bqr.REJECT_MISSING_OBJECT,
                "maxent": bqr.REJECT_MAXENT}
        for cid in bqr.CANDIDATE_IDS:
            rep = audits[cid]
            if rep.get("failed"):
                b_ok = False
                b_notes.append(f"{cid}: failed-flag")
                continue
            if rep.get("verdict") == "LEGIT":
                joint_exists = True
            elif rep.get("verdict") != "REJECTED" or \
                    rep.get("reason") != want[cid]:
                b_ok = False
                b_notes.append(f"{cid}: verdict-reason")
        prod = audits["product"]
        if not prod.get("failed"):
            if not prod.get("formal_ok"):
                b_ok = False
                b_notes.append("product: formal_ok")
            if len(prod.get("certs", [])) != len(bqr.PAIR2_CELLS):
                b_ok = False
                b_notes.append("product: cell-count")
            for cell, cert in zip(bqr.PAIR2_CELLS,
                                  prod.get("certs", [])):
                (_n, (pi, pj), (pk, pl)) = cell
                w1 = _q0.mode_weights(_q0.sum_mode(pi, pj),
                                      _q0.diff_mode(pi, pj))
                w2 = _q0.mode_weights(_q0.sum_mode(pk, pl),
                                      _q0.diff_mode(pk, pl))
                p1 = (w1["P_plus"], w1["P_minus"])
                p2 = (w2["P_plus"], w2["P_minus"])
                probs = [p1[0] * p2[0], p1[0] * p2[1],
                         p1[1] * p2[0], p1[1] * p2[1]]
                if abs(cert["norm_dev"] - abs(sum(probs) - 1.0)) > 1e-12:
                    b_ok = False
                    b_notes.append(f"product/{cell[0]}: norm")
                if abs(cert["min_prob"] - min(probs)) > 1e-12:
                    b_ok = False
                    b_notes.append(f"product/{cell[0]}: pos")
                mdev = max(abs(probs[0] + probs[1] - p1[0]),
                           abs(probs[2] + probs[3] - p1[1]),
                           abs(probs[0] + probs[2] - p2[0]),
                           abs(probs[1] + probs[3] - p2[1]))
                if abs(cert["marg_dev"] - mdev) > 1e-12:
                    b_ok = False
                    b_notes.append(f"product/{cell[0]}: marg")
        sdw = audits["sdweight"]
        if not sdw.get("failed"):
            if not sdw.get("formal_weights_ok"):
                b_ok = False
                b_notes.append("sdweight: formal")
            for row in sdw.get("counts", []):
                if row["n_weights"] != 2 * row["N"] or \
                        row["n_joint_outcomes"] != 2 ** row["N"]:
                    b_ok = False
                    b_notes.append("sdweight: counts")
            if [c["match"] for c in sdw.get("counts", [])] != \
                    [True, True, False, False, False]:
                b_ok = False
                b_notes.append("sdweight: match-col")
            if any(c.get("mapping_earned") for c in
                   sdw.get("certs", [])):
                b_ok = False
                b_notes.append("sdweight: mapping")
        mhq = audits["modehq"]
        if not mhq.get("failed"):
            if not mhq.get("sanity_ok"):
                b_ok = False
                b_notes.append("modehq: sanity")
            if mhq.get("marginals_defined"):
                b_ok = False
                b_notes.append("modehq: marginals-flag")
            want_h = {"m1": 2.0, "m2": 0.0, "m3": 1.0,
                      "m4": _q0.h2_binary(0.1)}
            for kk, vv in want_h.items():
                if abs(mhq["sanity"][kk] - vv) > 1e-12:
                    b_ok = False
                    b_notes.append(f"modehq: {kk}")
        haj = audits["haarjoint"]
        if not haj.get("failed"):
            if not haj.get("banked_callable"):
                b_ok = False
                b_notes.append("haarjoint: banked")
            if not haj.get("per_channel_only"):
                b_ok = False
                b_notes.append("haarjoint: per-channel")
            if haj.get("boundary_state_found"):
                b_ok = False
                b_notes.append("haarjoint: found-flag")
            if set(haj.get("survey", {})) != \
                    {"qinfo0", "haar", "store0_split0"}:
                b_ok = False
                b_notes.append("haarjoint: survey")
        mxe = audits["maxent"]
        if not mxe.get("failed") and mxe.get("constructed"):
            b_ok = False
            b_notes.append("maxent: constructed-flag")
        gate("G-B", b_ok, "; ".join(b_notes[:6]) +
             f" joint_exists={joint_exists}")
    except Exception as exc:  # noqa: BLE001
        gate("G-B", False, f"eval-error: {exc}")

    # ---- C: small-control functional re-verification ----
    try:
        from bh_graph import haar as banked
        from bh_graph import qinfo0 as _q0

        c_ok = True
        c_notes = []
        if smallctrl.get("failed") or not smallctrl.get("all_ok"):
            c_ok = False
            c_notes.append("all_ok-flag")
        vecs = {
            "product2": (np.array([1.0, 0.0, 0.0, 0.0],
                                  dtype=np.complex128), 2, 0.0),
            "bell": (np.array([1.0, 0.0, 0.0, 1.0],
                              dtype=np.complex128) / math.sqrt(2.0),
                     2, 2.0),
            "product3": (np.array([1.0] + [0.0] * 7,
                                  dtype=np.complex128), 3, 0.0),
            "ghz3": (np.array([1.0 / math.sqrt(2.0)] + [0.0] * 6
                              + [1.0 / math.sqrt(2.0)],
                              dtype=np.complex128), 3, 3.0),
        }
        filed = {r["cell"]: r for r in smallctrl.get("cells", [])}
        for name, (vec, n, want) in vecs.items():
            row = filed.get(name)
            if row is None or row.get("failed"):
                c_ok = False
                c_notes.append(f"{name}: missing")
                continue
            hs = _marginals_msb_first(vec, n)
            if max(abs(a - b) for a in hs for b in hs) > 1e-9:
                c_ok = False
                c_notes.append(f"{name}: symmetry")
            tre = float(sum(hs))
            if abs(tre - want) > 1e-9 or abs(row["T"] - tre) > 1e-9:
                c_ok = False
                c_notes.append(f"{name}: T")
            bh = float(banked.subsystem_entropy_bits(vec, 1, n))
            if abs(bh - hs[0]) > 1e-9:
                c_ok = False
                c_notes.append(f"{name}: banked")
        fsweep = {s["theta"]: s for s in smallctrl.get("sweep", [])}
        for theta in bqr.SWEEP_ANGLES:
            row = fsweep.get(float(theta))
            if row is None or row.get("failed"):
                c_ok = False
                c_notes.append(f"sweep@{theta:.3f}: missing")
                continue
            want = 2.0 * _q0.h2_binary(math.cos(float(theta)) ** 2)
            if abs(row["T"] - want) > 1e-9 or row["T"] < 0.0:
                c_ok = False
                c_notes.append(f"sweep@{theta:.3f}: T")
        gate("G-C", c_ok, "; ".join(c_notes[:6]))
    except Exception as exc:  # noqa: BLE001
        gate("G-C", False, f"eval-error: {exc}")

    # ---- D: pair-anatomy status (pairwise-I unearned + census filed) ----
    try:
        d_ok = True
        d_notes = []
        if "pairwise_note" not in audits["product"] or \
                "pairwise_note" not in audits["sdweight"]:
            d_ok = False
            d_notes.append("pairwise-notes-missing")
        for key in sorted(rel_recs, key=str):
            rec = rel_recs[key]
            if "cen_x" not in rec or "cen_s" not in rec:
                d_ok = False
                d_notes.append(f"{key}: census-missing")
                break
        gate("G-D", d_ok, "; ".join(d_notes[:3]) +
             " pairwise-I: UNEARNED (B-product/B-sdweight)")
    except Exception as exc:  # noqa: BLE001
        gate("G-D", False, f"eval-error: {exc}")

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
             and list(audit["short_d"]) == list(bqr.SHORT_D)
             and audit["tau_frac"] == bqr.TAU_FRAC
             and audit["kappa_rel"] == bqr.KAPPA_REL
             and list(audit["candidates"]) == list(bqr.CANDIDATE_IDS))
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

    # ---- MEAS: leg-B outcome + conditional-path status ----
    try:
        reasons = {cid: audits[cid].get("reason")
                   for cid in bqr.CANDIDATE_IDS}
        gate("G-MEAS", True,
             f"joint_exists={joint_exists} reasons={reasons} "
             "conditional AREA-SAME/RENORM/NONAREA: N/A-gated "
             "(no joint data; criteria frozen prereg-4)")
    except Exception as exc:  # noqa: BLE001
        gate("G-MEAS", False, f"eval-error: {exc}")

    # ---- descriptive anatomy (legs D/G/H flavor; not gated) ----
    try:
        desc = {}
        for r in bqr.R_LADDER:
            rec = rel_recs[("headline", "vacuum", r)]
            cx = rec["cen_x"]
            desc[str(r)] = {
                "degenerate": cx["degenerate"],
                "int": cx["int"]["C"], "ext": cx["ext"]["C"],
                "dis": cx["dis"]["C"], "short": cx["short"]["C"],
                "long": cx["long"]["C"]}
        notes["ANATOMY"] = json.dumps(desc, sort_keys=True)
    except Exception as exc:  # noqa: BLE001
        notes["ANATOMY"] = f"eval-error: {exc}"

    # ---- verdict ----
    required = ["G-INST", "G-A0", "G-D0", "G-MACH", "G-A", "G-B", "G-C",
                "G-D", "G-PART", "G-F", "G-O", "G-S", "G-T", "G-DET",
                "G-MEAS"]
    if any(not gates.get(g) for g in required):
        verdict = "BHQREL0-INCOMPLETE"
    elif joint_exists:
        verdict = "BHQREL0-INCOMPLETE"
        notes["JOINT-EXISTS"] = ("unexpected LEGIT joint without an "
                                 "E/F battery: follow-up wave required")
    else:
        verdict = "BHQREL0-MEASURE-DEBT"

    verdict_doc = {
        "campaign": "BH-Q-REL-0",
        "verdict": verdict,
        "gates": gates,
        "notes": notes,
        "measurement": {
            "joint_exists": joint_exists,
            "reasons": {cid: audits[cid].get("reason")
                        for cid in bqr.CANDIDATE_IDS}
            if audits else {},
            "conditional": "AREA-SAME/RENORM/NONAREA criteria frozen "
                           "(prereg-4); evaluation N/A-gated on leg B",
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
