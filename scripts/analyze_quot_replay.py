"""QUOT-0P/Q/R replay reveal (calls VENDORED OBS-1 functions only).

Reads quot blind JSONs (frozen + sha-locked, same discipline as OBS-1)
+ seal files, maps quot tags to (coords, graph, L), and scores every
(cell, set) with the UNMODIFIED vendored blind_set_flags + reveal_set.
Cell-flag aggregation (2/3 majority) mirrors analyze_obs1_reveal.py; the
QUOT verdict logic on top is this campaign's own (new comparison caller,
zero observer-code changes -- firewall compliant).

Datasets (outdir layout from quot_campaign.py stations/blind units):
  mixed    cells {0: j2-L42, 3: sq-L42, 6: exp-N3528-s0}
  p_plus   cell 0 (j2-L42, symmetric sources)
  p_minus  cell 0 (j2-L42, antisymmetric sources)
  frozen28 cell 19 (j2-L28, mixed)
  pert28   cell 19 (j2p-L28-e01, mixed sources, perturbed H)
  ctrl28   cell 21 (ctrl-L28 bilayer, mixed)
"""

import argparse
import hashlib
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

import run_obs0  # noqa: E402
from analyze_obs1_reveal import blind_set_flags, reveal_set  # noqa: E402
from bh_graph import obs1, obs1_reveal, quot  # noqa: E402
from bh_graph.formation import j2_torus_graph  # noqa: E402

MAJ = 2

DATASETS = {
    "mixed": [0, 3, 6],
    "p_plus": [0],
    "p_minus": [0],
    "frozen28": [19],
    "pert28": [19],
    "ctrl28": [21],
}
SETS = [0, 1, 2]


def quot_tag_graph(tag):
    """Reveal-side builder: (graph, L) for quot tags (frozen mapping)."""
    if tag == "j2p-L28-e01":
        return j2_torus_graph(28), 28
    if tag == "ctrl-L28":
        return quot.bilayer_square_graph(28), 28
    g, _ = run_obs0.tag_graph(tag)
    return g, run_obs0.tag_L(tag)


def quot_coords_tag(tag):
    """Reveal-side coords tag: perturbed/control share J2 labels."""
    if tag in ("j2p-L28-e01", "ctrl-L28"):
        return "j2-L28"
    return tag


def _maj(flags):
    return sum(1 for f in flags if f) >= MAJ


def reveal_set_disconnected(cell_rec, tag, nodes, g, L):
    """reveal_set body with disconnect-tolerant Hg (ctrl bilayer ONLY).

    The vendored reveal_set assumes a connected hidden graph
    (hidden_graph_matrix KeyErrors on unreachable pairs). The Q-R
    control substrate is disconnected BY DESIGN (two decoupled layers),
    so this caller replicates the vendored reveal_set body line-for-line
    -- same primitives, same order, same conditions -- with the single
    documented deviation that unreachable Hg pairs are +inf (honestly
    recording disconnectedness; cross_probe_rms masks non-finite pairs,
    so micro-RMS is computed over same-layer pairs only). The vendored
    module is never patched (firewall); this is a new comparison caller.
    """
    import networkx as nx

    C = cell_rec["probes"]["C"]
    n = len(nodes)
    D = np.asarray(C["D"], dtype=float)
    X = np.asarray(C["coords"], dtype=float) \
        if C["coords"] is not None else None
    coords = obs1_reveal.hidden_quotient_coords(tag, L)
    Hq = obs1_reveal.hidden_quotient_matrix(coords, nodes, L) \
        if coords is not None else None
    dists = [dict(nx.single_source_shortest_path_length(g, v))
             for v in nodes]
    Hg = np.full((n, n), np.inf)
    np.fill_diagonal(Hg, 0.0)
    for i in range(n):
        for j in range(i + 1, n):
            if nodes[j] in dists[i]:
                d = float(dists[i][nodes[j]])
                Hg[i, j] = Hg[j, i] = d
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
        Dp = np.asarray(cell_rec["probes"][ch]["D"], dtype=float)
        out["probe_dist"][ch] = obs1_reveal.geometry_match(
            Dp, Hq, Hg)["quot"] if Hq is not None else float("nan")
    out["probe_eps"] = {}
    for ch in obs1.PROBES:
        Dp = np.asarray(cell_rec["probes"][ch]["D"], dtype=float)
        out["probe_eps"][ch] = obs1_reveal.local_chart_report(
            Dp, coords, nodes, L)["med"] \
            if coords is not None else float("nan")
    out["Hg_disconnected"] = True
    return out


def _med(vals):
    v = [x for x in vals if x is not None and np.isfinite(x)]
    return float(np.median(v)) if v else float("nan")


def reveal_dataset(datadir, dataset):
    """Blind-load (hash-locked) + reveal one dataset -> per-cell flags."""
    blind_path = os.path.join(datadir, f"quot_blind_{dataset}.json")
    with open(blind_path, "rb") as f:
        blob = f.read()
    with open(blind_path + ".sha256") as f:
        frozen = f.read().strip()
    if hashlib.sha256(blob).hexdigest() != frozen:
        raise SystemExit(f"BLIND HASH MISMATCH for {dataset} -- STOP.")
    blind = json.loads(blob.decode())
    sealdir = os.path.join(datadir, dataset)
    cells = {}
    for c in DATASETS[dataset]:
        seals, tags = {}, set()
        for s in SETS:
            with open(os.path.join(sealdir, f"obs1_seal_cell{c}_s{s}.json")) as f:
                sm = json.load(f)
            seals[s] = sm
            tags.add(sm["tag"])
        assert len(tags) == 1
        tag = tags.pop()
        g, L = quot_tag_graph(tag)
        rtag = quot_coords_tag(tag)
        per_set, rev = {}, {}
        for s in SETS:
            sm = seals[s]
            nodes = [sm["stations"][f"S{i}"] for i in range(obs1.N_STATIONS)]
            rec = blind["cells"][str(c)]["sets"][str(s)]
            per_set[s] = blind_set_flags(rec["probes"])
            C = rec["probes"]["C"]
            if C["coords"] is not None and C["dstar"] == 2:
                if tag == "ctrl-L28":
                    rev[s] = reveal_set_disconnected(rec, rtag, nodes, g, L)
                else:
                    rev[s] = reveal_set(rec, rtag, nodes, g, L)
            else:
                # Degenerate observer (no valid 2D embedding: d* != 2 or
                # missing coords): reveal metrics are undefined, recorded
                # as fail with reason (P- no-geometry prediction). The
                # vendored reveal_set assumes 2D coords and is never
                # patched (firewall); it is simply not called here.
                rev[s] = {"degenerate": True, "dstar": C["dstar"],
                          "local": {"pass": False, "med": float("nan")},
                          "match": {"quot_pass": False, "quot": float("nan")},
                          "locality": {"pass": False, "frac": float("nan")},
                          "sheet": {"pass": False, "contrast": float("nan")},
                          "topo": {"pass": False}}
        ds = [per_set[s]["d"] for s in SETS]
        dok = [per_set[s]["dim_ok"] for s in SETS]
        dist = [rev[s]["match"].get("quot", float("nan")) for s in SETS]
        sheet_c = [rev[s]["sheet"].get("contrast", float("nan")) for s in SETS]
        measc = [blind["cells"][str(c)]["sets"][str(s)]["probes"]["C"]["measured_frac"]
                 for s in SETS]
        cells[f"{tag}@cell{c}"] = {
            "cell": c, "tag": tag, "sets": per_set,
            "METRIC_OK": _maj(per_set[s]["metric_ok"] for s in SETS),
            "DIM": _med(ds), "DIM_STABLE": bool(
                _maj(dok) and (float(np.nanmax(ds)) - float(np.nanmin(ds))
                               <= obs1.DIM_STABLE_BAR)),
            "EMB_OK": _maj(per_set[s]["emb"] for s in SETS),
            "METRIC": bool(_maj(per_set[s]["metric_ok"] for s in SETS)
                           and _maj(dok)
                           and _maj(per_set[s]["emb"] for s in SETS)),
            "LOCAL_OK": _maj(rev[s]["local"]["pass"] for s in SETS),
            "DIST_OK": _maj(rev[s]["match"].get("quot_pass", False) for s in SETS),
            "LOC_OK": _maj(rev[s]["locality"]["pass"] for s in SETS),
            "SHEET_OK": _maj(rev[s]["sheet"]["pass"] for s in SETS),
            "dist_med": _med(dist), "sheet_med": _med(sheet_c),
            "meas_med": _med(measc),
            "reveal": rev,
        }
        key = f"{tag}@cell{c}"
        print(f"reveal {dataset}/{key}: DIM={cells[key]['DIM']:.3f} "
              f"METRIC_OK={cells[key]['METRIC_OK']} DIST_OK={cells[key]['DIST_OK']} "
              f"SHEET_OK={cells[key]['SHEET_OK']} sheet={cells[key]['sheet_med']:.4f} "
              f"meas={cells[key]['meas_med']:.3f}", flush=True)
    return {"cells": cells, "blind_sha256": frozen}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datadir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--datasets", nargs="+", default=sorted(DATASETS))
    args = ap.parse_args()
    out = {"datasets": {}}
    for ds in args.datasets:
        out["datasets"][ds] = reveal_dataset(args.datadir, ds)
    # QUOT-0P bars (frozen): P+ QUOTIENT-clauses, P- no-geometry, gate flags.
    mx = out["datasets"]["mixed"]["cells"]
    j_mixed = mx["j2-L42@cell0"]
    p_plus = out["datasets"]["p_plus"]["cells"]["j2-L42@cell0"]
    p_minus = out["datasets"]["p_minus"]["cells"]["j2-L42@cell0"]

    def qclauses(cell, j2=True):
        metric = bool(cell["METRIC_OK"] and cell["DIM_STABLE"] and cell["EMB_OK"])
        d_ok = bool(np.isfinite(cell["DIM"]) and abs(cell["DIM"] - 2.0) <= 0.5)
        base = bool(metric and d_ok and cell["DIST_OK"] and cell["LOCAL_OK"]
                    and cell["LOC_OK"])
        # J2 cells add SHEET_OK (quotient-vs-micro); sq cells mirror the
        # OBS-1 C0_PASS exactly (no sheet clause: no sheets exist).
        return bool(base and cell["SHEET_OK"]) if j2 else base

    out["qclauses_fn_note"] = "qclauses mirrors OBS-1 QUOTIENT (METRIC & |d-2|<=.5 & DIST & LOCAL & LOC & SHEET)"
    dd = abs(p_plus["DIM"] - j_mixed["DIM"]) \
        if np.isfinite(p_plus["DIM"]) and np.isfinite(j_mixed["DIM"]) \
        else float("nan")
    out["bars"] = {
        "mixed_quotient_clauses": qclauses(j_mixed),
        "p_plus_quotient_clauses": qclauses(p_plus),
        "p_plus_drift": float(dd),
        "p_plus_drift_ok": bool(np.isfinite(dd) and dd <= 0.5),
        "p_minus_metric": bool(p_minus["METRIC_OK"] and p_minus["EMB_OK"]),
        "p_minus_meas": float(p_minus["meas_med"]),
        "p_minus_nogeometry": bool(p_minus["meas_med"] < 0.5
                                   and not (p_minus["METRIC_OK"] and p_minus["EMB_OK"])),
        "c0_mixed": qclauses(mx["sq-L42@cell3"], j2=False),
    }
    e = mx["exp-N3528-s0@cell6"]
    twod = sum(1 for s in SETS
               if e["sets"][s]["dim_ok"] and abs(e["sets"][s]["d"] - 2.0) <= 0.5
               and e["sets"][s]["dstar"] == 2 and e["sets"][s]["dstar_pass"]
               and e["sets"][s]["replicated"])
    out["bars"]["c1_mixed_twod_sets"] = int(twod)
    out["bars"]["c1_mixed"] = bool(twod == 0)
    if "frozen28" in out["datasets"] and "pert28" in out["datasets"]:
        fr = out["datasets"]["frozen28"]["cells"]["j2-L28@cell19"]
        pt = out["datasets"]["pert28"]["cells"]["j2-L28@cell19"] \
            if "j2-L28@cell19" in out["datasets"]["pert28"]["cells"] \
            else out["datasets"]["pert28"]["cells"]["j2p-L28-e01@cell19"]
        out["bars"]["pert_sheet"] = float(pt["sheet_med"])
        out["bars"]["frozen_sheet"] = float(fr["sheet_med"])
        out["bars"]["pert_flip"] = bool(
            np.isfinite(pt["sheet_med"]) and pt["sheet_med"] >= 0.05
            and np.isfinite(fr["sheet_med"])
            and pt["sheet_med"] > 3.0 * max(fr["sheet_med"], 1e-9))
        out["bars"]["pert_metric"] = bool(pt["METRIC_OK"] and pt["EMB_OK"])
    if "ctrl28" in out["datasets"]:
        ct = out["datasets"]["ctrl28"]["cells"]["ctrl-L28@cell21"]
        out["bars"]["ctrl_metric"] = bool(ct["METRIC_OK"] and ct["EMB_OK"])
        out["bars"]["ctrl_meas"] = float(ct["meas_med"])
        out["bars"]["ctrl_qclauses"] = qclauses(ct)
        out["bars"]["ctrl_two_worlds"] = bool(ct["meas_med"] < 0.98
                                              and not (ct["METRIC_OK"] and ct["EMB_OK"]))
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(run_obs0.jsonable(out), f)
    print("replay bars: " + json.dumps(run_obs0.jsonable(out["bars"]), indent=1), flush=True)


if __name__ == "__main__":
    main()
