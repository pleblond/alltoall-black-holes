"""GEOM-ATTRACTOR-0 campaign battery (runner; gates in geomattr0_analyze.py).

Preregistered grid (GEOMATTR0-PREREG, docs/geomattr0-prereg.md):
  dim     per graph tag: Stage-A verification + regime + meta (section B) and
          Stages C/D: BFS V(r)/d_eff + dense-eig spectral dimension.
  aniso   per headline tag: frozen directional packet transport (section G).

Each task evolves under frozen H = -A ONLY (aniso) or measures intrinsic
graph geometry (dim). No fitting, no steering, no selection. One JSON part
per task lands in OUTDIR (default data/geomattr0). Every record carries a
_git stamp from the checkout that wrote it.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import warnings

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import geomattr0 as g0
from bh_graph import obs0
from bh_graph import weave0 as W
from bh_graph.ballistic import (com, evolve_fixed, fit_velocity,
                                hamiltonian, is_normalized_ok, unwrap_trace)

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")


def _git_rev() -> str:
    try:
        here = os.path.join(os.path.dirname(__file__), "..")
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=here,
            stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def jsonify(x):
    if isinstance(x, dict):
        return {str(k): jsonify(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonify(v) for v in x]
    if isinstance(x, np.ndarray):
        return [jsonify(v) for v in x.tolist()]
    if isinstance(x, (np.floating, np.integer)):
        return x.item()
    if isinstance(x, complex):
        return [float(x.real), float(x.imag)]
    if isinstance(x, float) and (np.isnan(x) or np.isinf(x)):
        return str(x)
    if isinstance(x, frozenset):
        return sorted(jsonify(v) for v in x)
    return x


def safe_tag(tag: str) -> str:
    return "".join(c if c.isalnum() or c in ("-", "_") else "_"
                   for c in tag)


def _write(outdir: str, name: str, rec: dict) -> str:
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, name)
    rec = dict(rec)
    rec["_git"] = _git_rev()
    with open(path, "w") as f:
        json.dump(jsonify(rec), f)
    return path


def task_argv(t) -> str:
    k = t[0]
    if k == "dim":
        return f"--task dim --tag {t[1]}"
    if k == "aniso":
        return f"--task aniso --tag {t[1]}"
    raise ValueError(f"unknown task: {k}")


def run_dim(tag: str, outdir: str) -> str:
    asm = g0.build_tag(tag)
    g = asm["graph"]
    order = asm["order"]
    olam = g0.origin_lam(asm)
    a = g0.verify_stage_a(asm)
    reg = g0.regime_of(asm)
    degs = [d for _, d in g.degree()]
    meta = {"tag": tag, "family": asm.get("family", ""),
            "n": g.number_of_nodes(), "e": g.number_of_edges(),
            "K": asm.get("K", 0), "K_target": asm.get("K_target", 0),
            "S": asm.get("S", 0), "L": asm.get("L", 0),
            "lam": asm.get("lam", -1.0), "seed": asm.get("seed", 0),
            "substrate": asm.get("substrate", ""),
            "meeting": asm.get("meeting", ""),
            "deg_min": int(min(degs)) if degs else 0,
            "deg_max": int(max(degs)) if degs else 0,
            "deg_mean": float(sum(degs) / len(degs)) if degs else 0.0,
            "stage_a": a, "regime": reg, "origin_lam": olam}
    if "defect" in asm:
        dd = asm["defect"]
        meta["defect"] = {"frac": dd["frac"], "seed": dd["seed"],
                          "n_inc": dd["n_inc"], "k_drop": dd["k_drop"]}
    if asm.get("family") == "ph" and "lines" in asm:
        meta["lines_summary"] = {
            str(i): {"K_e": rec["K_e"], "n1": len(rec["lines1"]),
                     "n2": len(rec["lines2"]), "rot": rec["rot"]}
            for i, rec in asm["lines"].items()}
    WIN = g0.GEOM_WINDOWS
    D = obs0.intrinsic_diameter(g, order[0])
    wrap_hi = max(3, D // 2 - 1)
    loc = (WIN["local"][0], min(WIN["local"][1], wrap_hi))
    glo = (WIN["glob"][0], min(WIN["glob"][1], wrap_hi))
    xglo = (WIN["xglob"][0], min(WIN["xglob"][1], wrap_hi))
    oasm = dict(asm)
    oasm["lam"] = olam
    org = W.stage_b_origins(oasm)
    b_orig = {}
    deffs = {"far": [], "all": []}
    for grp in ("far", "near", "uni"):
        for v in org[grp]:
            prof = W.volume_profile(g, v)
            de = W.deff_curve(prof["vols"], prof["radii"])
            b_orig[str(v)] = {
                "grp": grp, "dmax": prof["dmax"],
                "local": W.window_fit(prof["radii"], prof["vols"],
                                      loc[0], loc[1], g0.R2_BAR),
                "glob": W.window_fit(prof["radii"], prof["vols"],
                                     glo[0], glo[1], g0.R2_BAR),
                "xglob": W.window_fit(prof["radii"], prof["vols"],
                                      xglo[0], xglo[1], g0.R2_BAR),
                "deff": [None if not np.isfinite(x) else float(x)
                         for x in de],
                "radii": [float(x) for x in prof["radii"]],
                "vols": [float(x) for x in prof["vols"]]}
            if grp == "far":
                deffs["far"].append(de)
            deffs["all"].append(de)
    rmax = max(len(d) for d in deffs["all"])
    rr = np.arange(rmax, dtype=float)

    def _pad(arr):
        out = []
        for dd in arr:
            dd = np.asarray(dd, dtype=float)
            if len(dd) == rmax:
                out.append(dd)
            else:
                out.append(np.pad(dd, (0, rmax - len(dd)),
                                  constant_values=np.nan))
        return np.array(out, dtype=float)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        with np.errstate(all="ignore"):
            deff_far_med = np.nanmedian(_pad(deffs["far"]), axis=0)
            deff_all_med = np.nanmedian(_pad(deffs["all"]), axis=0)
    rc = W.crossover_radius(rr, deff_far_med)
    w, V = W.eigh_lrw(g, order)
    heat_local = W.heat_ds_window(w, W.T_GRID, *WIN["tlocal"])
    heat_glob = W.heat_ds_window(w, W.T_GRID, *WIN["tglob"])
    heat_xglob = W.heat_ds_window(w, W.T_GRID, *WIN["xtglob"])
    slide = W.sliding_ds_heat(w)
    pos = {v: i for i, v in enumerate(order)}
    ori_ds = {}
    for v in org["all"]:
        ori_ds[str(v)] = {
            "local": W.origin_ds_window(w, V, pos[v], W.T_GRID,
                                        *WIN["tlocal"]),
            "glob": W.origin_ds_window(w, V, pos[v], W.T_GRID,
                                       *WIN["tglob"]),
            "xglob": W.origin_ds_window(w, V, pos[v], W.T_GRID,
                                        *WIN["xtglob"])}
    tc = W.crossover_radius(np.array(slide["t"]), np.array(slide["d"]))
    rec = dict(meta)
    rec.update({"D": D, "wrap_hi": wrap_hi,
                "windows": {"local": list(loc), "glob": list(glo),
                            "xglob": list(xglo),
                            "tlocal": list(WIN["tlocal"]),
                            "tglob": list(WIN["tglob"]),
                            "xtglob": list(WIN["xtglob"])},
                "origins": org, "B_origins": b_orig,
                "deff_far_med": [None if not np.isfinite(x) else float(x)
                                 for x in deff_far_med],
                "deff_all_med": [None if not np.isfinite(x) else float(x)
                                 for x in deff_all_med],
                "r_c": rc,
                "heat_local": heat_local, "heat_glob": heat_glob,
                "heat_xglob": heat_xglob, "origin_ds": ori_ds,
                "sliding_ds": slide, "t_c": tc,
                "lrw_evals": [float(x) for x in w[:64]]})
    name = f"geomattr0_dim_{safe_tag(tag)}.json"
    return _write(outdir, name, rec)


def run_aniso(tag: str, outdir: str) -> str:
    asm = g0.build_tag(tag)
    assert g0.is_stage_a_ok(asm), f"Stage-A fail {tag}"
    spec = g0.aniso_spec(tag)
    g = asm["graph"]
    order = sorted(g.nodes())
    h = hamiltonian(g, order=order)
    full_coords = g0.aniso_coords(asm, spec)
    if spec["kind"] == "sheet":
        sheet = spec["sheet"]
        sub_nodes = [v for v in order if asm["coords"][v][0] == sheet]
        coords = {v: full_coords[v] for v in sub_nodes}
        order_use = sub_nodes
    else:
        coords = {v: full_coords[v] for v in order}
        order_use = order
    from bh_graph.ballistic import gaussian_packet

    periods = spec["periods"]
    dim = len(periods)
    legs = {}
    for (ax, sg) in spec["dirs"]:
        k = [0.0] * dim
        k[{"x": 0, "y": 1, "z": 2}[ax]] = sg * spec["kabs"]
        psi0 = gaussian_packet(coords, order_use, spec["r0"], k,
                               spec["sigma"], periods=periods)
        assert is_normalized_ok(psi0), "packet norm"
        full = np.zeros(len(order), dtype=np.complex128)
        pos = {v: i for i, v in enumerate(order)}
        for v, amp in zip(order_use, psi0):
            full[pos[v]] = complex(amp)
        n_steps = int(round(spec["T"] / spec["dt"]))
        ts = np.arange(n_steps + 1) * spec["dt"]
        rows = evolve_fixed(full, h, spec["dt"], n_steps)["psi"]
        idx = [pos[v] for v in order_use]
        sub_rows = rows[:, idx]
        rs = np.array([com(row, coords, order_use, periods=periods)
                       for row in sub_rows])
        rs_u = unwrap_trace(rs, periods=periods)
        wfit = fit_velocity(rs_u, ts)
        legs[f"{ax}{sg:+d}"] = {
            "k": list(k), "v_fit": [float(x) for x in wfit["v"]],
            "speed": float(wfit["speed"]), "r2": float(wfit["r2"]),
            "norm_drift": float(np.abs(
                np.linalg.norm(rows, axis=1) - 1.0).max()),
            "com_0": [float(x) for x in rs_u[0]],
            "com_T": [float(x) for x in rs_u[-1]]}
    speeds = [r["speed"] for r in legs.values() if r["r2"] > 0.9]
    ratio = (max(speeds) / min(speeds) if len(speeds) >= 2
             and min(speeds) > 0 else None)
    rec = {"tag": tag, "spec": spec, "legs": legs,
           "n_good": len(speeds), "ratio": ratio,
           "pref": (ratio is not None and ratio <= g0.ANISO_PREF)}
    name = f"geomattr0_aniso_{safe_tag(tag)}.json"
    return _write(outdir, name, rec)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=False, default="",
                    choices=["", "dim", "aniso"])
    ap.add_argument("--tag", default="")
    ap.add_argument("--outdir", default="data/geomattr0")
    ap.add_argument("--count", action="store_true")
    ap.add_argument("--print-all", action="store_true")
    args = ap.parse_args()
    if args.count:
        print(len(g0.all_tasks()))
        return
    if args.print_all:
        for t in g0.all_tasks():
            print(task_argv(t))
        return
    if args.task == "dim":
        print(run_dim(args.tag, args.outdir))
    elif args.task == "aniso":
        print(run_aniso(args.tag, args.outdir))
    else:
        raise SystemExit("need --task dim|aniso or --count/--print-all")


if __name__ == "__main__":
    main()
