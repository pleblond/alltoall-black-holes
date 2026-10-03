"""VAC-STAB-0 campaign runner: one task per invocation (beast-parallel).

Usage:
  python scripts/vacstab_campaign.py --task stab --bg VPLUS --kind packet \\
      --eps 0.01 --outdir data/vacstab
  python scripts/vacstab_campaign.py --print-all   # emit every task argv line
  python scripts/vacstab_campaign.py --list        # task names + params

Each invocation writes one JSON record and prints the record path.
Deterministic given (task, params). No geometry is ever evolved; all
delta variables are readout-only (VACSTAB0 firewall).

Run on beast (96 CPU), never locally beyond --list:
  python scripts/vacstab_campaign.py --print-all | sed 's/.* :: //' > /tmp/x
  cat /tmp/x | xargs -P 80 -I{} bash -c 'run_one "{}"'
(see vacstab_launch.sh; OMP single-thread per task).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import socket
import subprocess
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import vacstab as vs  # noqa: E402
from bh_graph import vacfield as vf  # noqa: E402

SAFE_BG = {"VPLUS": "VPLUS", "VPI": "VPI", "CIRCLE@0": "CIRCLE0",
           "CIRCLE@pi/2": "CIRCLE1", "CIRCLE@pi/6": "CIRCLE2",
           "CIRCLE@pi/3": "CIRCLE3"}
UNSAFE_BG = {v: k for k, v in SAFE_BG.items()}

AMP_ANCHORS = (("VPLUS", "packet"), ("VPLUS", "point_amp"),
               ("CIRCLE@pi/6", "packet"))
LSCAN_CELLS = (("VPLUS", "packet"), ("VPLUS", "point_amp"),
               ("CIRCLE@pi/6", "packet"), ("CIRCLE@pi/6", "point_amp"))
XL_KINDS = ("packet", "point_amp")
T_XBG = 100.0


def _git_rev() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, timeout=10).stdout.strip()
    except Exception:
        return "unknown"


def jsonify(x):
    """Numpy-safe JSON conversion."""
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, (np.floating, np.integer)):
        return float(x)
    if isinstance(x, complex):
        return [float(x.real), float(x.imag)]
    if isinstance(x, dict):
        return {str(k): jsonify(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonify(v) for v in x]
    if isinstance(x, float) and (np.isnan(x) or np.isinf(x)):
        return str(x)
    return x


def sha_of(arr: np.ndarray) -> str:
    """Checksum of raw bytes (bitwise agreement evidence)."""
    a = np.ascontiguousarray(np.asarray(arr))
    return hashlib.sha256(a.view(np.uint8)).hexdigest()


def write_record(outdir: str, name: str, params: dict, payload: dict) -> str:
    os.makedirs(outdir, exist_ok=True)
    rec = {"task": name, "params": jsonify(params), "payload": jsonify(payload),
           "provenance": {"git_rev": _git_rev(),
                          "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                time.gmtime()),
                          "host": socket.gethostname()}}
    path = os.path.join(outdir, name + ".json")
    with open(path, "w") as f:
        json.dump(rec, f)
    print(path, flush=True)
    return path


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

def t_battery(p, outdir, record):
    sub = vf.j2_substrate(vs.L_HEAD)
    design = {}
    for bg in vs.BACKGROUNDS:
        for eps in vs.eps_grid_for(bg):
            design[f"{bg}/{eps}"] = vs.is_protected_design_ok(
                bg, sub, eps, 1.0, "abs")
        design[f"{bg}/frac"] = vs.is_protected_design_ok(
            bg, sub, vs.eps_frac_for(bg), 1.0, "frac")
    ok = vs.is_battery_ok(sub) and all(design.values())
    return {"ok": bool(ok), "design": design}


def t_bgcheck(p, outdir, record):
    from bh_graph.ballistic import evolve_fixed

    bg = p["bg"]
    sub = vf.j2_substrate(vs.L_HEAD)
    eu, ev = vf.edge_arrays_of(sub)
    h = vf.hamiltonian_of(sub)
    shape = vs.background_shape(bg, sub)
    energy = vs.background_energy(bg)
    res = vf.eigen_residual(shape, h, energy)
    ray = vf.rayleigh_energy(shape, h)
    cur = vf.current_census(shape, sub, np.asarray(eu), np.asarray(ev))
    stat = vf.stationarity_run(shape, h, np.asarray(eu), np.asarray(ev),
                               dt=0.1, t_end=8.0)
    w = vf.sector_weights(shape, sub["order"], sub["c3"])
    ext = vs.shape_abs_extrema(bg, sub)
    # Frozen dynamics pin for P_- backgrounds (QUOT banked U psi = psi).
    frozen_err = None
    if vs.background_sector(bg) == "anti":
        rows = evolve_fixed(shape, h, 0.1, 80)["psi"]
        frozen_err = float(np.abs(rows - rows[0][None, :]).max())
    return {"energy": energy, "rayleigh": float(ray),
            "residual": float(res),
            "current_free": bool(vf.is_current_free_ok(cur)),
            "stationary": bool(vf.is_stationary_ok(stat, energy)),
            "sector": w, "extrema": ext,
            "r_prot": float(ext["u_min"]),
            "frozen_err": frozen_err}


def _stab_payload(bg, kind, L, eps, a, mode, t_end):
    sub = vf.j2_substrate(int(L))
    eu, ev = vf.edge_arrays_of(sub)
    h = vf.hamiltonian_of(sub)
    shape = vs.background_shape(bg, sub)
    ext = vs.shape_abs_extrema(bg, sub)
    vac = float(a) * shape
    rep = vs.stab_run(vac, kind, sub, h, np.asarray(eu), np.asarray(ev),
                      eps=float(eps), a=float(a), mode=mode, dt=vs.DT,
                      t_end=float(t_end))
    scales = vs.cross_scales(ext["u_max"], float(a), rep["d0_norm"])
    return {"L": int(L), "bg": bg, "kind": kind, "eps": float(eps),
            "a": float(a), "mode": mode, "t_end": float(t_end),
            "u_max": ext["u_max"], "u_min": ext["u_min"],
            "scales": scales,
            "sup_ok": vs.is_sup_ok(rep["sup"], scales),
            "conc_ok": vs.is_concentration_ok(rep["C_ratio"]),
            "late_ok": vs.is_late_focus_ok(rep, scales),
            "late_ratio": vs.late_focus_ratio(rep["late"], scales),
            "norm_ok": vs.is_norm_conserved_ok(rep),
            "split_ok": vs.is_split_ok(rep),
            "sector_ok": vs.is_sector_conserved_ok(rep),
            "prot_ok": vs.is_protection_ok(rep),
            "rep": rep}


def t_stab(p, outdir, record):
    return _stab_payload(p["bg"], p["kind"], vs.L_HEAD, p["eps"], 1.0,
                         "abs", vs.T_HEAD)


def t_amp(p, outdir, record):
    return _stab_payload(p["bg"], p["kind"], vs.L_HEAD,
                         vs.eps_frac_for(p["bg"]), p["amp"], "frac",
                         vs.T_HEAD)


def t_lscan(p, outdir, record):
    bg = p["bg"]
    eps = vs.eps_grid_for(bg)[-1]
    return _stab_payload(bg, p["kind"], p["L"], eps, 1.0, "abs", vs.T_HEAD)


def t_xl(p, outdir, record):
    bg = p["bg"]
    eps = vs.eps_grid_for(bg)[-1]
    return _stab_payload(bg, p["kind"], vs.L_HEAD, eps, 1.0, "abs", vs.T_XL)


def t_xbg(p, outdir, record):
    from bh_graph.ballistic import evolve_fixed

    kind = p["kind"]
    eps = 0.01
    sub = vf.j2_substrate(vs.L_HEAD)
    h = vf.hamiltonian_of(sub)
    d0 = vs.stab_seed(kind, sub) * eps
    n_steps = int(round(T_XBG / vs.DT))
    # Same d0 evolved once per background label: guards against
    # background-dependent battery bugs (VAC-EXC 0B regression form).
    rows_by_bg = {}
    seed_dev = 0.0
    for bg in vs.BACKGROUNDS:
        vac = vs.background_shape(bg, sub)
        dd = vs.stab_delta(kind, vac, sub, eps, 1.0, "abs")
        seed_dev = max(seed_dev, float(np.linalg.norm(dd - d0)))
        rows_by_bg[bg] = evolve_fixed(dd, h, vs.DT, n_steps)["psi"]
    dev = vs.cross_background_dev(rows_by_bg)
    dev["ok"] = vs.is_identity_ok(dev)
    return {"cross": dev, "seed_dev": seed_dev,
            "seed_uniform": bool(seed_dev == 0.0)}


# ---------------------------------------------------------------------------
# Task registry
# ---------------------------------------------------------------------------

def all_tasks():
    """Yield (record_name, task_fn, params) for the full campaign."""
    yield ("battery", t_battery, {})
    for bg in vs.BACKGROUNDS:
        yield (f"bgcheck_{SAFE_BG[bg]}", t_bgcheck, {"bg": bg})
    for bg in vs.BACKGROUNDS:
        for kind in vs.KINDS:
            for eps in vs.eps_grid_for(bg):
                yield (f"stab_bg{SAFE_BG[bg]}_kind{kind}_eps{eps}",
                       t_stab, {"bg": bg, "kind": kind, "eps": eps})
    for (bg, kind) in AMP_ANCHORS:
        for amp in vs.AMPLITUDES:
            yield (f"amp_bg{SAFE_BG[bg]}_kind{kind}_amp{amp}", t_amp,
                   {"bg": bg, "kind": kind, "amp": amp})
    for (bg, kind) in LSCAN_CELLS:
        for L in vs.L_SCAN:
            yield (f"lscan_bg{SAFE_BG[bg]}_kind{kind}_L{L}", t_lscan,
                   {"bg": bg, "kind": kind, "L": L})
    for bg in vs.BACKGROUNDS:
        for kind in XL_KINDS:
            yield (f"xl_bg{SAFE_BG[bg]}_kind{kind}", t_xl,
                   {"bg": bg, "kind": kind})
    for kind in vs.XBG_KINDS:
        yield (f"xbg_kind{kind}", t_xbg, {"kind": kind})


TASK_FNS = {
    "battery": t_battery, "bgcheck": t_bgcheck, "stab": t_stab,
    "amp": t_amp, "lscan": t_lscan, "xl": t_xl, "xbg": t_xbg,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default=None)
    ap.add_argument("--bg", default=None)
    ap.add_argument("--kind", default=None)
    ap.add_argument("--eps", default=None)
    ap.add_argument("--amp", default=None)
    ap.add_argument("--L", default=None)
    ap.add_argument("--outdir", default="data/vacstab")
    ap.add_argument("--print-all", action="store_true")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    if args.print_all:
        for name, _, params in all_tasks():
            argv = " ".join(f"--{k} {v}" for k, v in params.items())
            print(f"{name} :: --task {task_of(name)} {argv}".strip())
        return
    if args.list:
        for name, _, params in all_tasks():
            print(name, params)
        return
    if not args.task:
        raise SystemExit("need --task (or --print-all / --list)")
    fn = TASK_FNS[args.task]
    params = {k: v for k, v in
              (("bg", args.bg), ("kind", args.kind), ("eps", args.eps),
               ("amp", args.amp), ("L", args.L)) if v is not None}
    record = None
    for name, f, prm in all_tasks():
        if f is fn and all(str(prm.get(k)) == str(v)
                           for k, v in params.items()):
            if len(prm) == len(params):
                record = name
                break
    if record is None:
        raise SystemExit(f"no registered record for task={args.task} "
                         f"params={params}")
    for k in ("eps", "amp"):
        if k in params:
            params[k] = float(params[k])
    if "L" in params:
        params["L"] = int(params["L"])
    # Resolve safe-bg tokens back to registry names.
    if "bg" in params and params["bg"] in UNSAFE_BG:
        params["bg"] = UNSAFE_BG[params["bg"]]
    payload = fn(params, args.outdir, record)
    write_record(args.outdir, record, params, payload)


def task_of(record_name: str) -> str:
    """Task keyword for a record name (prefix before _ or full name)."""
    for tname in TASK_FNS:
        if record_name == tname or record_name.startswith(tname + "_"):
            return tname
    raise ValueError(record_name)


if __name__ == "__main__":
    main()
