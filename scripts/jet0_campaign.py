"""JET-0 campaign (frozen battery, pre-data).

Tasks (xargs fan-out, 96-way+ on beast):
  ord       per (sub, edge_idx): certified Krylov order + recurrence.
  mergejet  per (sub, ftag, edge_pos, member): true merge + fiber census.
  splitjet  per (graph, field, k): reference split + alt census (+ J2 spot).
  samen     per (sub, ftag): same-N rewire jet census.
  forbit    per vendored orbit-traj: EQUIV reproduction + jet tests.
  traj      per (kind, sub, ftag): fixed-G traj vs static virtuals.
  lower     per (sub, edge, construction): nullspace + insufficiency.
  hidden    per (j2-L4, ftag, edge): sector anatomy + fiber census.
  source    per spec: causal/switch leg + jets + pre-arrival diagnostic.
  generic   per (sub, seed, edge): generic-state fiber census + codim.
  witness   per spec: forward+backward series identity (frozen reps).

Deterministic (frozen battery only, no RNG). Output: data/jet0/*.json.
Gates applied by scripts/jet0_analyze.py (frozen, pre-data).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import jet0 as j0


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


def all_tasks() -> list:
    out = []
    for t in j0.ord_tasks():
        out.append(("ord", t["sub"], t["edge_idx"]))
    for t in j0.mergejet_tasks():
        out.append(("mergejet", t["sub"], t["ftag"], t["edge_pos"],
                    t["member"]))
    for t in j0.splitjet_tasks():
        out.append(("splitjet", t["graph"], t["field"], t["k"]))
    for t in j0.samen_tasks():
        out.append(("samen", t["sub"], t["ftag"]))
    for t in j0.forbit_tasks():
        out.append(("forbit", t["traj"]))
    for t in j0.traj_tasks():
        out.append(("traj", t["kind"], t["sub"], t["ftag"]))
    for t in j0.lower_tasks():
        out.append(("lower", t["sub"], t["edge_idx"], t["construction"]))
    for t in j0.hidden_tasks():
        out.append(("hidden", t["sub"], t["ftag"], t["edge_idx"]))
    for t in j0.source_tasks():
        out.append(("source", t["spec"]))
    for t in j0.generic_tasks():
        out.append(("generic", t["sub"], t["seed"], t["edge_idx"]))
    for t in j0.witness_tasks():
        out.append(("witness", t["spec"]))
    return out


def task_argv(t) -> str:
    k = t[0]
    if k == "ord":
        return f"--task ord --sub {t[1]} --edge {t[2]}"
    if k == "mergejet":
        s = f"--task mergejet --sub {t[1]} --ftag {t[2]} --edge {t[3]}"
        return s + (f" --member {t[4]}" if t[4] else "")
    if k == "splitjet":
        return f"--task splitjet --graph {t[1]} --field {t[2]} --node {t[3]}"
    if k == "samen":
        return f"--task samen --sub {t[1]} --ftag {t[2]}"
    if k == "forbit":
        return f"--task forbit --traj {t[1]}"
    if k == "traj":
        return f"--task traj --kind {t[1]} --sub {t[2]} --ftag {t[3]}"
    if k == "lower":
        return (f"--task lower --sub {t[1]} --edge {t[2]} "
                f"--construction {t[3]}")
    if k == "hidden":
        return f"--task hidden --sub {t[1]} --ftag {t[2]} --edge {t[3]}"
    if k == "source":
        return f"--task source --spec {t[1]}"
    if k == "generic":
        return f"--task generic --sub {t[1]} --seed {t[2]} --edge {t[3]}"
    if k == "witness":
        return f"--task witness --spec {t[1]}"
    raise ValueError(f"unknown task kind: {k}")


def run_ord(args, outdir: str) -> str:
    rec = j0.ord_record(args.sub, int(args.edge))
    name = f"ord_sub{safe_tag(args.sub)}_e{int(args.edge)}.json"
    return _write(outdir, name, rec)


def run_mergejet(args, outdir: str) -> str:
    rec = j0.mergejet_record(args.sub, args.ftag, int(args.edge),
                             args.member or "")
    name = (f"mergejet_sub{safe_tag(args.sub)}_"
            f"ftag{safe_tag(args.ftag)}_e{int(args.edge)}")
    if args.member:
        name += f"_{args.member}"
    return _write(outdir, name + ".json", rec)


def run_splitjet(args, outdir: str) -> str:
    node = args.node
    try:
        k = int(node)
    except Exception:
        k = node
    if args.graph == "j2-spot":
        rec = j0.splitjet_j2_record(args.field, L=4)
        name = f"splitjet_j2-spot_{safe_tag(args.field)}.json"
    else:
        rec = j0.splitjet_record(args.graph, args.field, k)
        name = (f"splitjet_{safe_tag(args.graph)}_"
                f"{safe_tag(args.field)}_{k}.json")
    return _write(outdir, name, rec)


def run_samen(args, outdir: str) -> str:
    rec = j0.samen_record(args.sub, args.ftag)
    name = f"samen_{safe_tag(args.sub)}_{safe_tag(args.ftag)}.json"
    return _write(outdir, name, rec)


def run_forbit(args, outdir: str) -> str:
    rec = j0.forbit_record(args.traj)
    name = f"forbit_{safe_tag(args.traj)}.json"
    return _write(outdir, name, rec)


def run_traj(args, outdir: str) -> str:
    sub = args.sub or ""
    rec = j0.traj_record(args.kind, sub, args.ftag)
    if args.kind == "int":
        name = f"traj_int_{safe_tag(args.ftag)}.json"
    else:
        name = (f"traj_{safe_tag(args.kind)}_{safe_tag(sub)}_"
                f"{safe_tag(args.ftag)}.json")
    return _write(outdir, name, rec)


def run_lower(args, outdir: str) -> str:
    rec = j0.lower_record(args.sub, int(args.edge), args.construction)
    name = (f"lower_{safe_tag(args.sub)}_e{int(args.edge)}_"
            f"{safe_tag(args.construction)}.json")
    return _write(outdir, name, rec)


def run_hidden(args, outdir: str) -> str:
    rec = j0.hidden_record(args.sub, args.ftag, int(args.edge))
    name = (f"hidden_{safe_tag(args.sub)}_{safe_tag(args.ftag)}_"
            f"e{int(args.edge)}.json")
    return _write(outdir, name, rec)


def run_source(args, outdir: str) -> str:
    rec = j0.source_record(args.spec)
    name = f"source_{safe_tag(args.spec)}.json"
    return _write(outdir, name, rec)


def run_generic(args, outdir: str) -> str:
    rec = j0.generic_record(args.sub, int(args.seed), int(args.edge))
    name = (f"generic_{safe_tag(args.sub)}_seed{int(args.seed)}_"
            f"e{int(args.edge)}.json")
    return _write(outdir, name, rec)


def run_witness(args, outdir: str) -> str:
    rec = j0.witness_record(args.spec)
    name = f"witness_{safe_tag(args.spec)}.json"
    return _write(outdir, name, rec)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task",
                    choices=("ord", "mergejet", "splitjet", "samen",
                             "forbit", "traj", "lower", "hidden",
                             "source", "generic", "witness"))
    ap.add_argument("--sub", default=None)
    ap.add_argument("--ftag", default=None)
    ap.add_argument("--edge", default=None)
    ap.add_argument("--member", default="")
    ap.add_argument("--graph", default=None)
    ap.add_argument("--field", default=None)
    ap.add_argument("--node", default=None)
    ap.add_argument("--traj", default=None)
    ap.add_argument("--kind", default=None)
    ap.add_argument("--construction", default=None)
    ap.add_argument("--spec", default=None)
    ap.add_argument("--seed", default=None)
    ap.add_argument("--outdir", default="data/jet0")
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
    if a.task == "ord":
        print(run_ord(a, a.outdir), flush=True)
    elif a.task == "mergejet":
        print(run_mergejet(a, a.outdir), flush=True)
    elif a.task == "splitjet":
        print(run_splitjet(a, a.outdir), flush=True)
    elif a.task == "samen":
        print(run_samen(a, a.outdir), flush=True)
    elif a.task == "forbit":
        print(run_forbit(a, a.outdir), flush=True)
    elif a.task == "traj":
        print(run_traj(a, a.outdir), flush=True)
    elif a.task == "lower":
        print(run_lower(a, a.outdir), flush=True)
    elif a.task == "hidden":
        print(run_hidden(a, a.outdir), flush=True)
    elif a.task == "source":
        print(run_source(a, a.outdir), flush=True)
    elif a.task == "generic":
        print(run_generic(a, a.outdir), flush=True)
    elif a.task == "witness":
        print(run_witness(a, a.outdir), flush=True)
    else:
        ap.error("--task required (or --print-all/--count)")


if __name__ == "__main__":
    main()
