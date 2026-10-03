"""STORE-0 campaign (frozen battery, pre-data).

Tasks (xargs fan-out, 96-way+ on beast):
  ev      per (sub, ftag, edge_index, member): single-event store record
          + pinned-RES0 R cross-check (bitwise).
  fib     per fiber cell (tiny or j2): full fiber sweep record.
  seq     per frozen sequence: forward store + exact reverse.
  pair    per frozen edge pair: composition + order record.
  detcore per d(k)==0 tiny cell: halves control record.
  tex     per frozen texture spec: texture store record.
  fw      single firewall record.

Deterministic (frozen battery only, no RNG). Output: data/store0/*.json.
Gates applied by scripts/store0_analyze.py (frozen, pre-data).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import merge0 as m0
from bh_graph import store0 as t0


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


def safe_tag(ftag: str) -> str:
    return "".join(c if c.isalnum() or c in ("-", "_") else "_"
                   for c in ftag)


def _write(outdir: str, name: str, rec: dict) -> str:
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, name)
    rec = dict(rec)
    rec["_git"] = _git_rev()
    with open(path, "w") as f:
        json.dump(jsonify(rec), f, indent=1)
    return path


def all_tasks() -> list:
    return t0.all_tasks()


def task_argv(t) -> str:
    k = t[0]
    if k == "ev":
        _, sub, ftag, ei, mb = t
        s = f"--task ev --sub {sub} --ftag {ftag} --edge {ei}"
        return s + (f" --member {mb}" if mb else "")
    if k == "fib":
        if t[1] == "tiny":
            _, _, gn, fn, kk = t
            return f"--task fib --cell tiny --graph {gn} --field {fn} --node {kk}"
        return f"--task fib --cell j2 --bg {t[2]}"
    if k == "seq":
        return f"--task seq --name {t[1]} --ftag {t[2]}"
    if k == "pair":
        return f"--task pair --sub {t[1]} --ftag {t[2]} --relation {t[3]}"
    if k == "detcore":
        return (f"--task detcore --graph {t[1]} --field {t[2]} "
                f"--node {t[3]}")
    if k == "tex":
        sub, fam, p = t[1], t[2], t[3]
        idx = [i for i, sp in enumerate(t0.TEXTURE_SPECS)
               if sp[0] == sub and sp[1] == fam and dict(sp[2]) == dict(p)]
        assert len(idx) == 1, f"tex task not unique: {t}"
        return f"--task tex --texidx {idx[0]}"
    return "--task fw"


def run_ev(sub: str, ftag: str, ei: int, member: str, outdir: str) -> str:
    s = m0.build_substrate(sub)
    edges = m0.task_edges(s, ftag)
    edge = edges[ei]
    psi = m0.build_field(s, ftag)
    if isinstance(psi, dict):
        psi = psi["psi_A" if member == "A" else "psi_B"]
        tag = f"{ftag}:{member}"
    else:
        tag = ftag
    rec = t0.event_record_store({"name": s["name"], "g": s["g"],
                                 "order": s["order"]}, tag, edge, psi=psi)
    # Pinned-RES0 R cross-check (bitwise; A-Rpin gate input).
    pin = t0.load_pinned_reservoir0()
    arr = np.asarray(psi, dtype=np.complex128)
    r_pin = pin.merge_deficit(s["g"], arr, s["order"], *edge)["R"]
    rec["R_pin"] = float(r_pin)
    rec["R_pin_match"] = bool(r_pin == rec["R"])
    name = f"ev_sub{sub}_ftag{safe_tag(tag)}_e{ei}.json"
    return _write(outdir, name, rec)


def run_fib(cell: str, graph: str, field: str, node: int,
            bg: str, outdir: str) -> str:
    if cell == "tiny":
        rec = t0.fiber_record_tiny(graph, field, node)
        name = f"fib_tiny_{graph}_{field}_{node}.json"
    else:
        rec = t0.fiber_record_j2(bg)
        name = f"fib_j2_{bg}.json"
    return _write(outdir, name, rec)


def run_seq(name: str, ftag: str, outdir: str) -> str:
    rec = t0.sequence_store_record(name, ftag)
    return _write(outdir, f"seq_{name}_{safe_tag(ftag)}.json", rec)


def run_pair(sub: str, ftag: str, relation: str, outdir: str) -> str:
    rec = t0.pair_store_record(sub, ftag, relation)
    return _write(outdir,
                  f"pair_{sub}_{safe_tag(ftag)}_{relation}.json", rec)


def run_detcore(graph: str, field: str, node: int, outdir: str) -> str:
    rec = t0.detcore_record(graph, field, node)
    return _write(outdir, f"detcore_{graph}_{field}_{node}.json", rec)


def run_tex(texidx: int, outdir: str) -> str:
    sub, fam, p = t0.TEXTURE_SPECS[texidx]
    rec = t0.texture_store_record(sub, fam, dict(p))
    return _write(outdir, f"tex_{sub}_{fam}_{texidx}.json", rec)


def run_fw(outdir: str) -> str:
    return _write(outdir, "fw_store0.json", t0.firewall_record())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", choices=("ev", "fib", "seq", "pair",
                                       "detcore", "tex", "fw"))
    ap.add_argument("--sub", default=None)
    ap.add_argument("--ftag", default=None)
    ap.add_argument("--edge", type=int, default=0)
    ap.add_argument("--member", default="")
    ap.add_argument("--cell", default="tiny")
    ap.add_argument("--graph", default=None)
    ap.add_argument("--field", default=None)
    ap.add_argument("--node", type=int, default=0)
    ap.add_argument("--bg", default=None)
    ap.add_argument("--name", default=None)
    ap.add_argument("--relation", default=None)
    ap.add_argument("--texidx", type=int, default=0)
    ap.add_argument("--outdir", default="data/store0")
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
    if a.task == "ev":
        print(run_ev(a.sub, a.ftag, a.edge, a.member, a.outdir))
    elif a.task == "fib":
        print(run_fib(a.cell, a.graph, a.field, a.node, a.bg, a.outdir))
    elif a.task == "seq":
        print(run_seq(a.name, a.ftag, a.outdir))
    elif a.task == "pair":
        print(run_pair(a.sub, a.ftag, a.relation, a.outdir))
    elif a.task == "detcore":
        print(run_detcore(a.graph, a.field, a.node, a.outdir))
    elif a.task == "tex":
        print(run_tex(a.texidx, a.outdir))
    elif a.task == "fw":
        print(run_fw(a.outdir))
    else:
        raise SystemExit("no task given (see --print-all)")


if __name__ == "__main__":
    main()
