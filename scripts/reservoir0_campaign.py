"""RESERVOIR-0 campaign runner: one task per invocation (beast-parallel).

Usage:
  python scripts/reservoir0_campaign.py --task event --sub j2-L4 \\
      --ftag VPLUS --edge 0 --outdir data/reservoir0
  python scripts/reservoir0_campaign.py --task fiber --graph triangle \\
      --field bonding --k 0 --outdir data/reservoir0
  python scripts/reservoir0_campaign.py --task fiberj2 --background VMINUS \\
      --outdir data/reservoir0
  python scripts/reservoir0_campaign.py --task texture --spec 0 --edge 0 \\
      --outdir data/reservoir0
  python scripts/reservoir0_campaign.py --task excresp --kind packet \\
      --vac VPLUS --epsidx 2 --outdir data/reservoir0
  python scripts/reservoir0_campaign.py --task disjoint --sub path-8 \\
      --relation disjoint --ftag uniform --outdir data/reservoir0
  python scripts/reservoir0_campaign.py --task order --name tri-o1 \\
      --ftag uniform --outdir data/reservoir0
  python scripts/reservoir0_campaign.py --task seq --name handbuilt-chain \\
      --ftag uniform --outdir data/reservoir0
  python scripts/reservoir0_campaign.py --print-all   # emit every task argv line
  python scripts/reservoir0_campaign.py --count       # number of tasks

Each invocation writes one JSON record and prints the record path.
Deterministic given (task, params): all battery content frozen in
reservoir0.py. No firing law, scheduler, probability, or reservoir
store is constructed anywhere in this runner.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import merge0 as m0  # noqa: E402
from bh_graph import reservoir0 as r0  # noqa: E402


def _git_rev() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, timeout=10).stdout.strip()
    except Exception:
        return "unknown"


def jsonify(x):
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, (np.floating, np.integer)):
        return float(x)
    if isinstance(x, (np.bool_, bool)):
        return bool(x)
    if isinstance(x, complex):
        return [float(x.real), float(x.imag)]
    if isinstance(x, dict):
        return {str(k): jsonify(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonify(v) for v in x]
    if isinstance(x, float) and (np.isnan(x) or np.isinf(x)):
        return str(x)
    return x


def all_tasks() -> list:
    """Frozen task list (deterministic order, pre-data)."""
    tasks = []
    for sub in m0.SUBSTRATES:
        s = m0.build_substrate(sub)
        for ftag in m0.field_tags(s):
            for ei in range(len(m0.task_edges(s, ftag))):
                tasks.append(("event", sub, ftag, ei))
    for cell in r0.fiber_cells():
        tasks.append(("fiber", cell["graph"], cell["field"], cell["k"]))
    for bg in r0.J2_FIBER_BACKGROUNDS:
        tasks.append(("fiberj2", bg))
    for ti in range(len(r0.TEXTURE_SPECS)):
        subname = r0.TEXTURE_SPECS[ti][0]
        s = m0.build_substrate(subname)
        for ei in range(len(m0.frozen_edges(s))):
            tasks.append(("texture", ti, ei))
    for kind in r0.EXCRESP_KINDS:
        for vac in r0.EXCRESP_VACS:
            for pi in range(len(r0.EXCRESP_EPS)):
                tasks.append(("excresp", kind, vac, pi))
    for sub in r0.PAIR_SUBS:
        for ftag in r0.PAIR_FIELDS_DIS[sub]:
            tasks.append(("disjoint", sub, "disjoint", ftag))
        for ftag in r0.PAIR_FIELDS_OVL:
            tasks.append(("disjoint", sub, "overlap", ftag))
    for name, ftag in r0.ORDER_SPECS:
        tasks.append(("order", name, ftag))
    for name, ftag in r0.SEQ_TASKS:
        tasks.append(("seq", name, ftag))
    return tasks


def task_argv(t) -> str:
    kind = t[0]
    if kind == "event":
        _, sub, ftag, ei = t
        return f"--task event --sub {sub} --ftag {ftag} --edge {ei}"
    if kind == "fiber":
        _, graph, field, k = t
        return f"--task fiber --graph {graph} --field {field} --k {k}"
    if kind == "fiberj2":
        return f"--task fiberj2 --background {t[1]}"
    if kind == "texture":
        return f"--task texture --spec {t[1]} --edge {t[2]}"
    if kind == "excresp":
        _, kind_, vac, pi = t
        return f"--task excresp --kind {kind_} --vac {vac} --epsidx {pi}"
    if kind == "disjoint":
        _, sub, relation, ftag = t
        return (f"--task disjoint --sub {sub} --relation {relation} "
                f"--ftag {ftag}")
    if kind == "order":
        return f"--task order --name {t[1]} --ftag {t[2]}"
    return f"--task seq --name {t[1]} --ftag {t[2]}"


def safe_tag(ftag: str) -> str:
    return ftag.replace(":", "-").replace("@", "-").replace("/", "-")


def _write(rec: dict, kind: str, fn: str, outdir: str, t0: float) -> str:
    rec = jsonify(rec)
    rec["meta"] = {"kind": kind, "rev": _git_rev(),
                   "wall_s": time.time() - t0}
    path = os.path.join(outdir, fn)
    with open(path, "w") as f:
        json.dump(rec, f)
    return path


def run_event(sub: str, ftag: str, ei: int, outdir: str) -> str:
    t0 = time.time()
    s = m0.build_substrate(sub)
    edge = m0.task_edges(s, ftag)[ei]
    if ftag in m0.PAIR_FIELDS:
        rec = r0.pair_event_record(s, ftag, edge)
    else:
        rec = r0.event_record(s, ftag, edge)
    return _write(rec, "event",
                  f"event_sub{sub}_ftag{safe_tag(ftag)}_e{ei}.json",
                  outdir, t0)


def run_fiber(graph: str, field: str, k: int, outdir: str) -> str:
    t0 = time.time()
    cell = None
    for c in r0.fiber_cells():
        if c["graph"] == graph and c["field"] == field and c["k"] == k:
            cell = c
            break
    if cell is None:
        raise ValueError(f"unknown fiber cell: {graph}/{field}#{k}")
    rec = r0.fiber_sweep(cell)
    return _write(rec, "fiber", f"fiber_{graph}-{field}-k{k}.json",
                  outdir, t0)


def run_fiberj2(background: str, outdir: str) -> str:
    t0 = time.time()
    rec = r0.fiber_sweep_j2(background)
    return _write(rec, "fiberj2", f"fiberj2_{background}.json",
                  outdir, t0)


def run_texture(spec: int, ei: int, outdir: str) -> str:
    t0 = time.time()
    subname, family, params = r0.TEXTURE_SPECS[spec]
    rec = r0.texture_record(subname, family, params, ei)
    return _write(rec, "texture",
                  f"tex_{subname}-{family}-t{spec}_e{ei}.json",
                  outdir, t0)


def run_excresp(kind: str, vac: str, pi: int, outdir: str) -> str:
    t0 = time.time()
    rec = r0.excresp_record(kind, vac, r0.EXCRESP_EPS[pi])
    return _write(rec, "excresp", f"exc_{kind}-{vac}-p{pi}.json",
                  outdir, t0)


def run_disjoint(sub: str, relation: str, ftag: str, outdir: str) -> str:
    t0 = time.time()
    rec = r0.disjoint_record(sub, ftag, relation)
    return _write(rec, "disjoint",
                  f"dis_{sub}-{relation}-{safe_tag(ftag)}.json",
                  outdir, t0)


def run_order(name: str, ftag: str, outdir: str) -> str:
    t0 = time.time()
    rec = r0.order_record(name, ftag)
    return _write(rec, "order", f"ord_{name}_{safe_tag(ftag)}.json",
                  outdir, t0)


def run_seq(name: str, ftag: str, outdir: str) -> str:
    t0 = time.time()
    rec = r0.sequence_r_record(name, ftag)
    return _write(rec, "seq", f"seq_{name}_{safe_tag(ftag)}.json",
                  outdir, t0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", choices=("event", "fiber", "fiberj2",
                                       "texture", "excresp", "disjoint",
                                       "order", "seq"))
    ap.add_argument("--sub", default=None)
    ap.add_argument("--ftag", default=None)
    ap.add_argument("--edge", type=int, default=0)
    ap.add_argument("--graph", default=None)
    ap.add_argument("--field", default=None)
    ap.add_argument("--k", type=int, default=0)
    ap.add_argument("--background", default=None)
    ap.add_argument("--spec", type=int, default=0)
    ap.add_argument("--kind", default=None)
    ap.add_argument("--vac", default=None)
    ap.add_argument("--epsidx", type=int, default=0)
    ap.add_argument("--relation", default=None)
    ap.add_argument("--name", default=None)
    ap.add_argument("--outdir", default="data/reservoir0")
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
    if a.task == "event":
        print(run_event(a.sub, a.ftag, a.edge, a.outdir), flush=True)
    elif a.task == "fiber":
        print(run_fiber(a.graph, a.field, a.k, a.outdir), flush=True)
    elif a.task == "fiberj2":
        print(run_fiberj2(a.background, a.outdir), flush=True)
    elif a.task == "texture":
        print(run_texture(a.spec, a.edge, a.outdir), flush=True)
    elif a.task == "excresp":
        print(run_excresp(a.kind, a.vac, a.epsidx, a.outdir), flush=True)
    elif a.task == "disjoint":
        print(run_disjoint(a.sub, a.relation, a.ftag, a.outdir),
              flush=True)
    elif a.task == "order":
        print(run_order(a.name, a.ftag, a.outdir), flush=True)
    elif a.task == "seq":
        print(run_seq(a.name, a.ftag, a.outdir), flush=True)
    else:
        ap.error("--task required (or --print-all/--count)")


if __name__ == "__main__":
    main()
