"""OBS-1 STAGE-REVEAL analyzer (FROZEN per OBS1-PREREG).

RUN ONLY AFTER data/obs1_blind.json + data/obs1_blind.json.sha256 are
COMMITTED. Verifies the blind hash first (STOP on mismatch: the blind
stage must be re-frozen, never silently edited), then joins the concealed
station maps, rebuilds the hidden references, and evaluates the frozen
verdict ladder -> data/obs1_verdict.json.

Verdict ladder (cumulative headline; independent clause flags recorded):
  OBS1-NO-GEOMETRY   no stable metric/dimension at J2-L128
  OBS1-METRIC        stable metric + dimension + replicated embedding
  OBS1-QUOTIENT      METRIC + quotient match (d~2, eps, locality, sheets)
  OBS1-CROSS-PROBE   QUOTIENT + W/D/P mutual agreement
  OBS1-RECONSTRUCTED CROSS-PROBE + angles + window + topology + C0/C1/scale
Headline rungs above METRIC additionally require C0-PASS (pipeline
validation on the known-2D control); else capped with PIPELINE-FAIL.
"""

import argparse
import hashlib
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))
from bh_graph import obs1, obs1_reveal  # noqa: E402
import run_obs0  # noqa: E402

MAJ = 2  # majority of N_SETS=3 (frozen)


def _arr(x):
    return np.array([[np.nan if v is None else v for v in row] for row in x],
                    dtype=float)


def _maj(flags):
    return sum(1 for f in flags if f) >= MAJ


def _med(vals):
    v = [x for x in vals if x is not None and np.isfinite(x)]
    return float(np.median(v)) if v else float("nan")


def blind_set_flags(pr):
    """Per-set blind clause flags from the composite (C) observer."""
    C = pr["C"]
    sym = all(pr[ch]["sym"]["pass"] for ch in obs1.PROBES)
    tri = bool(C["triangle"]["pass_loose"])  # composite near-metric bar
    complete = bool(C["measured_frac"] >= obs1.COMPOSITE_COMPLETE_BAR)
    dim_ok = bool(C["vol"]["ok"])
    emb = bool(C["dstar_pass"] and C["replicated"]
               and C["measured_frac"] >= obs1.EMBED_COMPLETE_BAR)
    return {"sym": sym, "tri": tri, "complete": complete,
            "metric_ok": bool(sym and tri and complete),
            "dim_ok": dim_ok, "d": C["vol"]["d"], "emb": emb,
            "angle": bool(C["angle"]["pass"]),
            "window": bool(C["euclid"]["window"]),
            "dstar": C["dstar"], "replicated": bool(C["replicated"]),
            "dstar_pass": bool(C["dstar_pass"])}


def reveal_set(cell_rec, tag, nodes, g, L):
    """Hidden-join scoring of one (cell, set) composite observer."""
    C = cell_rec["probes"]["C"]
    n = len(nodes)
    D = _arr(C["D"])
    X = _arr(C["coords"]) if C["coords"] is not None else None
    coords = obs1_reveal.hidden_quotient_coords(tag, L)
    Hq = obs1_reveal.hidden_quotient_matrix(coords, nodes, L) \
        if coords is not None else None
    Hg = obs1_reveal.hidden_graph_matrix(g, nodes)
    A = np.zeros((n, n), dtype=bool)
    for a, b in C["edges"]:
        A[a, b] = A[b, a] = True
    out = {}
    out["align"] = obs1_reveal.hidden_alignment(X, coords, nodes) \
        if X is not None and coords is not None \
        else {"eps": float("nan")}
    out["local"] = obs1_reveal.local_chart_report(D, coords, nodes, L) \
        if coords is not None \
        else {"med": float("nan"), "n": 0, "pass": False}
    out["locality"] = obs1_reveal.locality_report(A, Hq) \
        if Hq is not None else {"frac": float("nan"), "pass": False}
    sheets = obs1_reveal.hidden_sheets(tag, L)
    out["sheet"] = obs1_reveal.sheet_report(
        D, [sheets[v] for v in nodes]) if sheets is not None \
        else {"contrast": float("nan"), "pass": False}
    out["topo"] = obs1_reveal.topology_report(C["wrap"]["pairs"], coords,
                                              nodes, L, Hq) \
        if coords is not None else {"precision": float("nan"),
                                    "n": 0, "pass": False}
    out["match"] = obs1_reveal.geometry_match(D, Hq, Hg)
    out["probe_dist"] = {}
    for ch in obs1.PROBES:
        Dp = _arr(cell_rec["probes"][ch]["D"])
        out["probe_dist"][ch] = obs1_reveal.geometry_match(
            Dp, Hq, Hg)["quot"] if Hq is not None else float("nan")
    out["probe_eps"] = {}
    for ch in obs1.PROBES:
        Dp = _arr(cell_rec["probes"][ch]["D"])
        out["probe_eps"][ch] = obs1_reveal.local_chart_report(
            Dp, coords, nodes, L)["med"] \
            if coords is not None else float("nan")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--blind", required=True)
    ap.add_argument("--sealdir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cells", type=int, nargs="+", required=True)
    ap.add_argument("--sets", type=int, nargs="+", required=True)
    args = ap.parse_args()

    with open(args.blind, "rb") as f:
        blob = f.read()
    with open(args.blind + ".sha256") as f:
        frozen = f.read().strip()
    digest = hashlib.sha256(blob).hexdigest()
    if digest != frozen:
        raise SystemExit(
            f"BLIND HASH MISMATCH: {digest} != frozen {frozen} -- STOP. "
            "Re-freeze the blind stage; never edit it post-hoc.")
    blind = json.loads(blob.decode())

    cells = {}
    for c in args.cells:
        seals, tags = {}, set()
        for s in args.sets:
            with open(os.path.join(
                    args.sealdir, f"obs1_seal_cell{c}_s{s}.json")) as f:
                sm = json.load(f)
            seals[s] = sm
            tags.add(sm["tag"])
        assert len(tags) == 1
        tag = tags.pop()
        L = run_obs0.tag_L(tag)
        g, _ = run_obs0.tag_graph(tag)
        per_set, rev = {}, {}
        for s in args.sets:
            sm = seals[s]
            nodes = [sm["stations"][f"S{i}"] for i in range(obs1.N_STATIONS)]
            rec = blind["cells"][str(c)]["sets"][str(s)]
            per_set[s] = blind_set_flags(rec["probes"])
            cross = rec["cross"]
            per_set[s]["cross"] = bool(all(
                cross[k]["rms_pass"] and cross[k]["d_pass"]
                for k in ("WD", "WP", "DP")))
            rev[s] = reveal_set(rec, tag, nodes, g, L)
        ds = [per_set[s]["d"] for s in args.sets]
        dok = [per_set[s]["dim_ok"] for s in args.sets]
        cells[tag] = {
            "cell": c, "sets": per_set, "reveal": rev,
            "METRIC_OK": _maj(per_set[s]["metric_ok"] for s in args.sets),
            "DIM": _med(ds), "DIM_STABLE": bool(
                _maj(dok) and (float(np.nanmax(ds)) - float(np.nanmin(ds))
                <= obs1.DIM_STABLE_BAR)),
            "EMB_OK": _maj(per_set[s]["emb"] for s in args.sets),
            "LOCAL_OK": _maj(rev[s]["local"]["pass"] for s in args.sets),
            "DIST_OK": _maj(rev[s]["match"].get("quot_pass", False)
                             for s in args.sets),
            "LOC_OK": _maj(rev[s]["locality"]["pass"] for s in args.sets),
            "SHEET_OK": _maj(rev[s]["sheet"]["pass"] for s in args.sets),
            "TOPO_OK": _maj(rev[s]["topo"]["pass"] for s in args.sets),
            "CROSS_OK": _maj(per_set[s]["cross"] for s in args.sets),
            "ANGLE_OK": _maj(per_set[s]["angle"] for s in args.sets),
            "WINDOW_OK": _maj(per_set[s]["window"] for s in args.sets),
        }
        print(f"reveal {tag}: DIM={cells[tag]['DIM']:.3f} "
              f"METRIC_OK={cells[tag]['METRIC_OK']} "
              f"LOCAL_OK={cells[tag]['LOCAL_OK']} "
              f"DIST_OK={cells[tag]['DIST_OK']}", flush=True)

    # Full coverage required for a headline (partial runs: INCOMPLETE).
    have_tags = set(cells)
    need_tags = {"j2-L42", "j2-L64", "j2-L128", "sq-L42", "sq-L64",
                 "sq-L128", "exp-N3528-s0", "exp-N8192-s0",
                 "exp-N32768-s0"}
    full = have_tags >= need_tags and len(args.sets) >= 3

    def _cell(tag):
        return cells.get(tag, {"DIM": float("nan"), "METRIC_OK": False,
                              "DIM_STABLE": False, "EMB_OK": False,
                              "LOCAL_OK": False, "DIST_OK": False,
                              "LOC_OK": False, "SHEET_OK": False,
                              "TOPO_OK": False, "CROSS_OK": False,
                              "ANGLE_OK": False, "WINDOW_OK": False,
                              "sets": {}, "cell": -1})
    J = _cell("j2-L128")
    METRIC = bool(J["METRIC_OK"] and J["DIM_STABLE"] and J["EMB_OK"])
    d_ok = bool(np.isfinite(J["DIM"]) and abs(J["DIM"] - 2.0) <= 0.5)
    QUOTIENT = bool(METRIC and d_ok and J["DIST_OK"] and J["LOCAL_OK"]
                    and J["LOC_OK"] and J["SHEET_OK"])
    CROSS = bool(QUOTIENT and J["CROSS_OK"])
    C0 = _cell("sq-L128")
    C0_PASS = bool(C0["DIM_STABLE"] and np.isfinite(C0["DIM"])
                   and abs(C0["DIM"] - 2.0) <= 0.5 and C0["DIST_OK"]
                   and C0["LOCAL_OK"] and C0["LOC_OK"])
    C1, c1_detail = True, {}
    for t in ("exp-N3528-s0", "exp-N8192-s0", "exp-N32768-s0"):
        E = _cell(t)
        if E["cell"] < 0:
            c1_detail[t] = {"twod_sets": -1, "data_sets": -1,
                            "pass": False}
            C1 = False
            continue
        twod_sets = sum(
            1 for s in args.sets
            if E["sets"][s]["dim_ok"]
            and abs(E["sets"][s]["d"] - 2.0) <= 0.5
            and E["sets"][s]["dstar"] == 2
            and E["sets"][s]["dstar_pass"]
            and E["sets"][s]["replicated"])
        data_sets = sum(
            1 for s in args.sets
            if blind["cells"][str(E["cell"])]["sets"][str(s)]
            ["probes"]["C"]["measured_frac"] >= 0.5)
        ok = bool(twod_sets == 0 and data_sets >= MAJ)
        c1_detail[t] = {"twod_sets": twod_sets, "data_sets": data_sets,
                        "pass": ok}
        C1 = C1 and ok
    dj = [_cell(t)["DIM"] for t in ("j2-L42", "j2-L64", "j2-L128")]
    SCALING = bool(full
                   and all(np.isfinite(d) and abs(d - 2.0) <= 0.5
                           for d in dj)
                   and _cell("j2-L64")["DIST_OK"] and J["DIST_OK"]
                   and (max(dj) - min(dj) <= obs1.DIM_STABLE_BAR))
    RECON = bool(CROSS and J["ANGLE_OK"] and J["WINDOW_OK"] and J["TOPO_OK"]
                 and C0_PASS and C1 and SCALING)
    pipeline_fail = (QUOTIENT or CROSS or RECON) and not C0_PASS
    if not full:
        headline = "OBS1-INCOMPLETE"
    elif RECON and C0_PASS:
        headline = "OBS1-RECONSTRUCTED"
    elif CROSS and C0_PASS:
        headline = "OBS1-CROSS-PROBE"
    elif QUOTIENT and C0_PASS:
        headline = "OBS1-QUOTIENT"
    elif METRIC:
        headline = "OBS1-METRIC"
    else:
        headline = "OBS1-NO-GEOMETRY"
    verdict = {
        "rungs": {"METRIC": METRIC, "QUOTIENT": QUOTIENT, "CROSS": CROSS,
                  "RECONSTRUCTED": RECON},
        "clauses": {"d_128": J["DIM"], "C0_PASS": C0_PASS, "C1": C1,
                    "c1_detail": c1_detail, "SCALING": SCALING,
                    "dj_scaling": dj, "PIPELINE_FAIL": bool(pipeline_fail),
                    "cross_without_quotient": bool(J["CROSS_OK"]
                                                   and not QUOTIENT)},
        "cells": cells, "headline": headline, "blind_sha256": frozen,
    }
    with open(args.out, "w") as f:
        json.dump(run_obs0.jsonable(verdict), f)
    print(f"verdict: {headline} (C0={C0_PASS} C1={C1} scaling={SCALING})")


if __name__ == "__main__":
    main()
