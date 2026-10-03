"""CROSSB-0 campaign runner (frozen battery, pre-data).

Tasks (xargs fan-out, 96-way on beast):
  norm    per (sub, L): Hamiltonian normalization pins.
  det     per (sub, L, r, t): finite-rank determinant pins.
  green   per (sub, r, N): quotient k-sum Green pins.
  cert2   per (r, t, L): J2 finite-size certification.
  cert3   per (r, t, L): J3 finite-size certification.
  ctrl    per (kind, r, t): square/cubic descriptive controls.

Deterministic (frozen battery only, no RNG). Output: data/crossb0/*.json.
Gates applied by scripts/crossb0_analyze.py (frozen, pre-data).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import crossb0 as c0


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


def safe_tag(s: str) -> str:
    return "".join(c if c.isalnum() or c in ("-", "_") else "_"
                   for c in str(s))


def _write(outdir: str, name: str, rec: dict) -> str:
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, name)
    rec = dict(rec)
    rec["_git"] = _git_rev()
    with open(path, "w") as f:
        json.dump(jsonify(rec), f, indent=1)
    return path


def _parse_r(s: str) -> tuple:
    return tuple(int(x) for x in str(s).split(","))


def all_tasks() -> list:
    out = []
    for t in c0.norm_tasks():
        out.append(("norm", t["sub"], t["L"]))
    for t in c0.det_tasks():
        out.append(("det", t["sub"], t["L"], t["r"], t["t"]))
    for t in c0.green_tasks():
        out.append(("green", t["sub"], t["r"], t["n"]))
    for t in c0.cert2_tasks():
        out.append(("cert2", t["r"], t["t"], t["L"]))
    for t in c0.cert3_tasks():
        out.append(("cert3", t["r"], t["t"], t["L"]))
    for t in c0.ctrl_tasks():
        out.append(("ctrl", t["kind"], t["r"], t["t"]))
    return out


def task_argv(t) -> str:
    k = t[0]
    if k == "norm":
        return f"--task norm --sub {t[1]} --L {t[2]}"
    if k == "det":
        r = ",".join(str(x) for x in t[3])
        return f"--task det --sub {t[1]} --L {t[2]} --r {r} --t {t[4]}"
    if k == "green":
        r = ",".join(str(x) for x in t[2])
        return f"--task green --sub {t[1]} --r {r} --N {t[3]}"
    if k == "cert2":
        r = ",".join(str(x) for x in t[1])
        return f"--task cert2 --r {r} --t {t[2]} --L {t[3]}"
    if k == "cert3":
        r = ",".join(str(x) for x in t[1])
        return f"--task cert3 --r {r} --t {t[2]} --L {t[3]}"
    if k == "ctrl":
        r = ",".join(str(x) for x in t[2])
        return f"--task ctrl --kind {t[1]} --r {r} --t {t[3]}"
    raise ValueError(f"unknown task kind: {k}")


def run_norm(args, outdir: str) -> str:
    rec = c0.norm_record(args.sub, int(args.L))
    return _write(outdir, f"norm_{safe_tag(args.sub)}_L{int(args.L)}.json",
                  rec)


def run_det(args, outdir: str) -> str:
    r = _parse_r(args.r)
    rec = c0.det_record(args.sub, int(args.L), r, float(args.t))
    rt = "_".join(str(x) for x in r)
    return _write(outdir, f"det_{safe_tag(args.sub)}_L{int(args.L)}_"
                           f"r{rt}_t{safe_tag(args.t)}.json", rec)


def run_green(args, outdir: str) -> str:
    r = _parse_r(args.r)
    rec = c0.green_record(args.sub, r, int(args.N))
    rt = "_".join(str(x) for x in r)
    return _write(outdir, f"green_{safe_tag(args.sub)}_r{rt}_"
                           f"N{int(args.N)}.json", rec)


def run_cert2(args, outdir: str) -> str:
    r = _parse_r(args.r)
    rec = c0.cert2_record(r, float(args.t), int(args.L))
    rt = "_".join(str(x) for x in r)
    return _write(outdir, f"cert2_r{rt}_t{safe_tag(args.t)}_"
                           f"L{int(args.L)}.json", rec)


def run_cert3(args, outdir: str) -> str:
    r = _parse_r(args.r)
    rec = c0.cert3_record(r, float(args.t), int(args.L))
    rt = "_".join(str(x) for x in r)
    return _write(outdir, f"cert3_r{rt}_t{safe_tag(args.t)}_"
                           f"L{int(args.L)}.json", rec)


def run_ctrl(args, outdir: str) -> str:
    r = _parse_r(args.r)
    rec = c0.ctrl_record(args.kind, r, float(args.t))
    rt = "_".join(str(x) for x in r)
    return _write(outdir, f"ctrl_{safe_tag(args.kind)}_r{rt}_"
                           f"t{safe_tag(args.t)}.json", rec)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task",
                    choices=("norm", "det", "green", "cert2", "cert3",
                             "ctrl"))
    ap.add_argument("--sub", default=None)
    ap.add_argument("--L", default=None)
    ap.add_argument("--r", default=None)
    ap.add_argument("--t", default=None)
    ap.add_argument("--N", default=None)
    ap.add_argument("--kind", default=None)
    ap.add_argument("--outdir", default="data/crossb0")
    ap.add_argument("--print-all", action="store_true")
    ap.add_argument("--count", action="store_true")
    a = ap.parse_args()
    if a.print_all:
        for t in all_tasks():
            print(task_argv(t))
        return
    if a.count:
        print(len(all_tasks()))
        return
    os.makedirs(a.outdir, exist_ok=True)
    if a.task == "norm":
        print(run_norm(a, a.outdir), flush=True)
    elif a.task == "det":
        print(run_det(a, a.outdir), flush=True)
    elif a.task == "green":
        print(run_green(a, a.outdir), flush=True)
    elif a.task == "cert2":
        print(run_cert2(a, a.outdir), flush=True)
    elif a.task == "cert3":
        print(run_cert3(a, a.outdir), flush=True)
    elif a.task == "ctrl":
        print(run_ctrl(a, a.outdir), flush=True)
    else:
        ap.error("--task required (or --print-all/--count)")


if __name__ == "__main__":
    main()
