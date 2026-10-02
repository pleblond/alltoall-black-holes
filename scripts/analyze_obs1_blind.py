"""OBS-1 STAGE-BLIND analyzer (FROZEN per OBS1-PREREG).

Reads ONLY opaque measurement files (integer cell id, integer set id,
S-id pair records). It NEVER loads concealed maps, tags, graphs, or
coordinates (pinned by tests/test_obs1.py C3 audit: import scan + token
scan of THIS file).

Per (cell, set, probe in W/D/P/composite) the analyzer reconstructs the
observer geometry with the frozen estimators and writes the frozen blind
artifact data/obs1_blind.json plus its sha256. The reveal stage refuses
to run unless the recorded hash matches.
"""

import argparse
import hashlib
import json
import os

import numpy as np

from bh_graph import obs1


def _jsonable(o):
    if isinstance(o, np.ndarray):
        return [_jsonable(v) for v in o.tolist()]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        v = float(o)
        return v if np.isfinite(v) else None
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, dict):
        return {str(k): _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, float) and not np.isfinite(o):
        return None
    return o


def _probe_geometry(D, n_train=obs1.N_TRAIN):
    """Frozen blind reconstruction of ONE completed distance matrix."""
    n = D.shape[0]
    tri = obs1.triangle_report(D)
    vol = obs1.volume_dimension(D)
    d_range = list(obs1.MDS_DIMS)
    tr = list(range(n_train))
    te = list(range(n_train, n))
    Dtr = D[np.ix_(tr, tr)]
    Dte = D[np.ix_(te, te)]
    stresses = {}
    for d in d_range:
        r = obs1.classical_mds(Dtr, d)
        stresses[d] = obs1.stress_normalized(Dtr, r["coords"]) if r["ok"] \
            else float("nan")
    sel = obs1.select_dimension({d: stresses[d] for d in d_range})
    rt_all = {}
    for d in d_range:
        r = obs1.classical_mds(Dte, d)
        rt_all[d] = obs1.stress_normalized(Dte, r["coords"]) if r["ok"] \
            else float("nan")
    sel_te = obs1.select_dimension(rt_all)
    test_stress = rt_all[sel["dstar"]]
    replicated = bool(sel_te["pass"] and sel_te["dstar"] == sel["dstar"])
    rf = obs1.classical_mds(D, sel["dstar"])
    coords = rf["coords"] if rf["ok"] else None
    A = obs1.adjacency_operational(D)
    iu = np.triu_indices(n, 1)
    edges = [[int(a), int(b)] for a, b in zip(iu[0][A[iu]],
                                              iu[1][A[iu]])]
    ang = obs1.angle_consistency(D, coords) if coords is not None \
        else {"med": float("nan"), "n": 0, "pass": False}
    eu = obs1.local_euclideanity(D, d=2)
    wrap = obs1.wrap_candidates(D, coords) if coords is not None \
        else {"pairs": [], "n": 0}
    return {
        "triangle": tri, "vol": vol,
        "train_stress": {str(d): stresses[d] for d in d_range},
        "dstar": sel["dstar"], "dstar_pass": sel["pass"],
        "test_stress": {str(d): rt_all[d] for d in d_range},
        "test_dstar": sel_te["dstar"], "test_dstar_pass": sel_te["pass"],
        "replicated": replicated,
        "coords": coords, "negmass": rf["negmass"] if rf["ok"] else None,
        "edges": edges, "angle": ang, "euclid": eu, "wrap": wrap,
    }


def analyze_cell_set(meas):
    """Full blind workup of one measurement file (opaque dict)."""
    n = int(meas["n"])
    nat = obs1.native_matrices(meas["pairs"], n=n)
    comp = {}
    per_probe = {}
    for ch in obs1.PROBES:
        raw = nat[ch]
        done = obs1.complete_matrix(raw)
        comp[ch] = obs1.symmetrize(raw)  # UN-imputed (Amendment-1)
        geo = _probe_geometry(done["D"])
        geo["sym"] = obs1.symmetry_report(raw)
        geo["measured_frac"] = done["measured_frac"]
        geo["n_imputed"] = done["n_imputed"]
        geo["D"] = done["D"]
        per_probe[ch] = geo
    C_raw = obs1.composite_matrix(comp)
    C_done = obs1.complete_matrix(C_raw)  # complete AFTER mixing
    C = C_done["D"]
    geo = _probe_geometry(C)
    geo["sym"] = None
    geo["measured_frac"] = C_done["measured_frac"]
    geo["n_imputed"] = C_done["n_imputed"]
    geo["D"] = C
    per_probe["C"] = geo
    cross = {}
    for x, y in (("W", "D"), ("W", "P"), ("D", "P")):
        r = obs1.cross_probe_rms(per_probe[x]["D"], per_probe[y]["D"])
        dx = per_probe[x]["vol"]["d"]
        dy = per_probe[y]["vol"]["d"]
        dd = abs(dx - dy) if np.isfinite(dx) and np.isfinite(dy) \
            else float("nan")
        cross[x + y] = {"rms": r["rms"], "scale": r["scale"],
                        "rms_pass": r["pass"], "d_diff": dd,
                        "d_pass": bool(np.isfinite(dd)
                                       and dd <= obs1.CROSS_D_BAR)}
    return {"probes": per_probe, "cross": cross,
            "P_clamp_frac": nat["meta"]["P_clamp_frac"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--measdir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cells", type=int, nargs="+", required=True)
    ap.add_argument("--sets", type=int, nargs="+", required=True)
    args = ap.parse_args()
    out = {"cells": {}, "meta": {"cells": args.cells, "sets": args.sets}}
    for c in args.cells:
        out["cells"][str(c)] = {"sets": {}}
        for s in args.sets:
            with open(os.path.join(
                    args.measdir,
                    f"obs1_meas_cell{c}_s{s}.json")) as f:
                meas = json.load(f)
            assert int(meas["cell"]) == c and int(meas["set"]) == s
            assert int(meas["n"]) == obs1.N_STATIONS
            out["cells"][str(c)]["sets"][str(s)] = analyze_cell_set(meas)
            print(f"blind cell={c} set={s} done", flush=True)
    blob = json.dumps(_jsonable(out), sort_keys=True).encode()
    with open(args.out, "w") as f:
        f.write(blob.decode())
    digest = hashlib.sha256(blob).hexdigest()
    with open(args.out + ".sha256", "w") as f:
        f.write(digest + "\n")
    print(f"blind artifact: {args.out} sha256={digest}")


if __name__ == "__main__":
    main()
