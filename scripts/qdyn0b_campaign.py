"""Q-DYN-0b campaign (frozen battery, pre-data).

Tasks (xargs fan-out, 96-way on beast):
  reg       STORE regression (full store0 battery wrapped as reg_*).
  waitb     per (sub, ftag, edge, member): waiting + relational readout.
  eigen     per (sub, ftag, edge): autopsy-reproduction eigen anatomy.
  splitback per (sub, ftag, edge): wait-then-inverse-split ledgers.
  cycle     per (sub, ftag, edge): forth-back closed-cycle accounting.
  sym       per (sub, ftag, edge): readout covariance.
  loc       per (sub, ftag, edge): locality + readout attribution.
  hid       per (sub, ftag, edge): hidden sensitivity, fixed Q.
  src       per (vac, kind, placement): source-response readout.
  multi     per sequence/pair: multi-store stability + waiting.
  stoch     per fiber cell: apparent-stochasticity pairs.
  audit     single static-audit record.

Deterministic (frozen battery only, no RNG). Output: data/qdyn0b/*.json.
Gates applied by scripts/qdyn0b_analyze.py (frozen, pre-data).
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
from bh_graph import qdyn0b as qb
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
    return qb.all_tasks()


def task_argv(t) -> str:
    k = t[0]
    if k == "reg":
        st = t[1:]
        sk = st[0]
        if sk == "ev":
            _, sub, ftag, ei, mb = st
            s = f"--task reg --reg ev --sub {sub} --ftag {ftag} --edge {ei}"
            return s + (f" --member {mb}" if mb else "")
        if sk == "fib":
            if st[1] == "tiny":
                _, _, gn, fn, kk = st
                return (f"--task reg --reg fib --cell tiny --graph {gn} "
                        f"--field {fn} --node {kk}")
            return f"--task reg --reg fib --cell j2 --bg {st[2]}"
        if sk == "seq":
            return f"--task reg --reg seq --name {st[1]} --ftag {st[2]}"
        if sk == "pair":
            return (f"--task reg --reg pair --sub {st[1]} --ftag {st[2]} "
                    f"--relation {st[3]}")
        if sk == "detcore":
            return (f"--task reg --reg detcore --graph {st[1]} "
                    f"--field {st[2]} --node {st[3]}")
        if sk == "tex":
            sub, fam, p = st[1], st[2], st[3]
            idx = [i for i, sp in enumerate(t0.TEXTURE_SPECS)
                   if sp[0] == sub and sp[1] == fam
                   and dict(sp[2]) == dict(p)]
            assert len(idx) == 1, f"tex task not unique: {t}"
            return f"--task reg --reg tex --texidx {idx[0]}"
        return "--task reg --reg fw"
    if k == "waitb":
        _, sub, ftag, ei, mb = t
        s = f"--task waitb --sub {sub} --ftag {ftag} --edge {ei}"
        return s + (f" --member {mb}" if mb else "")
    if k == "eigen":
        return f"--task eigen --sub {t[1]} --ftag {t[2]} --edge {t[3]}"
    if k == "splitback":
        return f"--task splitback --sub {t[1]} --ftag {t[2]} --edge {t[3]}"
    if k == "cycle":
        return f"--task cycle --sub {t[1]} --ftag {t[2]} --edge {t[3]}"
    if k == "sym":
        return f"--task sym --sub {t[1]} --ftag {t[2]} --edge {t[3]}"
    if k == "loc":
        return f"--task loc --sub {t[1]} --ftag {t[2]} --edge {t[3]}"
    if k == "hid":
        return f"--task hid --sub {t[1]} --ftag {t[2]} --edge {t[3]}"
    if k == "src":
        return f"--task src --vac {t[1]} --kind {t[2]} --placement {t[3]}"
    if k == "multi":
        if t[1] == "seq":
            return f"--task multi --mkind seq --name {t[2]} --ftag {t[3]}"
        return (f"--task multi --mkind pair --sub {t[2]} --ftag {t[3]} "
                f"--relation {t[4]}")
    if k == "stoch":
        return (f"--task stoch --graph {t[1]} --field {t[2]} "
                f"--node {t[3]}")
    return "--task audit"


def run_reg(args, outdir: str) -> str:
    rk = args.reg
    if rk == "ev":
        s = m0.build_substrate(args.sub)
        edges = m0.task_edges(s, args.ftag)
        edge = edges[int(args.edge)]
        psi = m0.build_field(s, args.ftag)
        if isinstance(psi, dict):
            psi = psi["psi_A" if args.member == "A" else "psi_B"]
            tag = f"{args.ftag}:{args.member}"
        else:
            tag = args.ftag
        rec = t0.event_record_store(
            {"name": s["name"], "g": s["g"], "order": s["order"]},
            tag, edge, psi=psi)
        pin = t0.load_pinned_reservoir0()
        rec["R_pin_match"] = bool(
            abs(pin.merge_deficit(
                s["g"], np.asarray(psi), list(s["order"]),
                *edge)["R"] - rec["R"]) == 0.0)
        name = (f"reg_ev_sub{safe_tag(args.sub)}_"
                f"ftag{safe_tag(args.ftag)}")
        if args.member:
            name += f"_{args.member}"
        name += f"_e{args.edge}.json"
        return _write(outdir, name, rec)
    if rk == "fib":
        if args.cell == "tiny":
            try:
                kk = int(args.node)
            except Exception:
                kk = args.node
            rec = t0.fiber_record_tiny(args.graph, args.field, kk)
            name = (f"reg_fib_tiny_{safe_tag(args.graph)}_"
                    f"{safe_tag(args.field)}_{kk}.json")
        else:
            rec = t0.fiber_record_j2(args.bg)
            name = f"reg_fib_j2_{safe_tag(args.bg)}.json"
        return _write(outdir, name, rec)
    if rk == "seq":
        rec = t0.sequence_store_record(args.name, args.ftag)
        name = (f"reg_seq_{safe_tag(args.name)}_"
                f"{safe_tag(args.ftag)}.json")
        return _write(outdir, name, rec)
    if rk == "pair":
        rec = t0.pair_store_record(args.sub, args.ftag, args.relation)
        name = (f"reg_pair_{safe_tag(args.sub)}_"
                f"{safe_tag(args.ftag)}_{args.relation}.json")
        return _write(outdir, name, rec)
    if rk == "detcore":
        try:
            kk = int(args.node)
        except Exception:
            kk = args.node
        rec = t0.detcore_record(args.graph, args.field, kk)
        name = (f"reg_detcore_{safe_tag(args.graph)}_"
                f"{safe_tag(args.field)}_{kk}.json")
        return _write(outdir, name, rec)
    if rk == "tex":
        sub, fam, p = t0.TEXTURE_SPECS[int(args.texidx)]
        rec = t0.texture_store_record(sub, fam, dict(p))
        name = (f"reg_tex_{safe_tag(sub)}_{safe_tag(fam)}_"
                f"{int(args.texidx)}.json")
        return _write(outdir, name, rec)
    rec = t0.firewall_record()
    return _write(outdir, "reg_fw_store0.json", rec)


def run_waitb(args, outdir: str) -> str:
    rec = qb.waitb_record(args.sub, args.ftag, int(args.edge),
                          args.member or "")
    name = f"waitb_sub{safe_tag(args.sub)}_ftag{safe_tag(args.ftag)}"
    if args.member:
        name += f"_{args.member}"
    name += f"_e{int(args.edge)}.json"
    return _write(outdir, name, rec)


def run_eigen(args, outdir: str) -> str:
    rec = qb.eigen_record(args.sub, args.ftag, int(args.edge))
    name = (f"eigen_sub{safe_tag(args.sub)}_ftag{safe_tag(args.ftag)}_"
            f"e{int(args.edge)}.json")
    return _write(outdir, name, rec)


def run_splitback(args, outdir: str) -> str:
    rec = qb.splitback_record(args.sub, args.ftag, int(args.edge))
    name = (f"splitback_sub{safe_tag(args.sub)}_ftag{safe_tag(args.ftag)}_"
            f"e{int(args.edge)}.json")
    return _write(outdir, name, rec)


def run_cycle(args, outdir: str) -> str:
    rec = qb.cycle_record(args.sub, args.ftag, int(args.edge))
    name = (f"cycle_sub{safe_tag(args.sub)}_ftag{safe_tag(args.ftag)}_"
            f"e{int(args.edge)}.json")
    return _write(outdir, name, rec)


def run_sym(args, outdir: str) -> str:
    rec = qb.cov_record(args.sub, args.ftag, int(args.edge))
    name = (f"sym_sub{safe_tag(args.sub)}_ftag{safe_tag(args.ftag)}_"
            f"e{int(args.edge)}.json")
    return _write(outdir, name, rec)


def run_loc(args, outdir: str) -> str:
    rec = qb.loc_record(args.sub, args.ftag, int(args.edge))
    name = (f"loc_sub{safe_tag(args.sub)}_ftag{safe_tag(args.ftag)}_"
            f"e{int(args.edge)}.json")
    return _write(outdir, name, rec)


def run_hid(args, outdir: str) -> str:
    rec = qb.hid_record(args.sub, args.ftag, int(args.edge))
    name = (f"hid_sub{safe_tag(args.sub)}_ftag{safe_tag(args.ftag)}_"
            f"e{int(args.edge)}.json")
    return _write(outdir, name, rec)


def run_src(args, outdir: str) -> str:
    rec = qb.src_record(args.vac, args.kind, args.placement)
    name = (f"src_vac{safe_tag(args.vac)}_kind{safe_tag(args.kind)}_"
            f"{safe_tag(args.placement)}.json")
    return _write(outdir, name, rec)


def run_multi(args, outdir: str) -> str:
    if args.mkind == "seq":
        rec = qb.multi_record_seq(args.name, args.ftag)
        name = (f"multi_seq_{safe_tag(args.name)}_"
                f"{safe_tag(args.ftag)}.json")
    else:
        rec = qb.multi_record_pair(args.sub, args.ftag, args.relation)
        name = (f"multi_pair_{safe_tag(args.sub)}_"
                f"{safe_tag(args.ftag)}_{args.relation}.json")
    return _write(outdir, name, rec)


def run_stoch(args, outdir: str) -> str:
    try:
        kk = int(args.node)
    except Exception:
        kk = args.node
    rec = qb.stoch_record(args.graph, args.field, kk)
    name = (f"stoch_{safe_tag(args.graph)}_{safe_tag(args.field)}_"
            f"{kk}.json")
    return _write(outdir, name, rec)


def run_audit(outdir: str) -> str:
    rec = qb.audit_record()
    return _write(outdir, "audit_qdyn0b.json", rec)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", choices=("reg", "waitb", "eigen",
                                       "splitback", "cycle", "sym",
                                       "loc", "hid", "src", "multi",
                                       "stoch", "audit"))
    ap.add_argument("--reg", default=None,
                    choices=("ev", "fib", "seq", "pair", "detcore",
                             "tex", "fw"))
    ap.add_argument("--sub", default=None)
    ap.add_argument("--ftag", default=None)
    ap.add_argument("--edge", default=None)
    ap.add_argument("--member", default="")
    ap.add_argument("--cell", default=None)
    ap.add_argument("--graph", default=None)
    ap.add_argument("--field", default=None)
    ap.add_argument("--node", default=None)
    ap.add_argument("--bg", default=None)
    ap.add_argument("--name", default=None)
    ap.add_argument("--relation", default=None)
    ap.add_argument("--texidx", default=None)
    ap.add_argument("--vac", default=None)
    ap.add_argument("--kind", default=None)
    ap.add_argument("--placement", default=None)
    ap.add_argument("--mkind", default=None)
    ap.add_argument("--outdir", default="data/qdyn0b")
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
    if a.task == "reg":
        print(run_reg(a, a.outdir), flush=True)
    elif a.task == "waitb":
        print(run_waitb(a, a.outdir), flush=True)
    elif a.task == "eigen":
        print(run_eigen(a, a.outdir), flush=True)
    elif a.task == "splitback":
        print(run_splitback(a, a.outdir), flush=True)
    elif a.task == "cycle":
        print(run_cycle(a, a.outdir), flush=True)
    elif a.task == "sym":
        print(run_sym(a, a.outdir), flush=True)
    elif a.task == "loc":
        print(run_loc(a, a.outdir), flush=True)
    elif a.task == "hid":
        print(run_hid(a, a.outdir), flush=True)
    elif a.task == "src":
        print(run_src(a, a.outdir), flush=True)
    elif a.task == "multi":
        print(run_multi(a, a.outdir), flush=True)
    elif a.task == "stoch":
        print(run_stoch(a, a.outdir), flush=True)
    elif a.task == "audit":
        print(run_audit(a.outdir), flush=True)
    else:
        ap.error("--task required (or --print-all/--count)")


if __name__ == "__main__":
    main()
