"""TIME-Q-0 campaign (frozen battery, pre-data).

Tasks (xargs fan-out, 96-way+ on beast):
  wait, merge1, split1, roundtrip, detcore, multicover, disjoint, seqrev,
  timing, hidden, hiddenq, sched, forward, toy, horizon, fw.

Deterministic (frozen battery only, no RNG). Output: data/timeq0/*.json.
Gates applied by scripts/timeq0_analyze.py (frozen, pre-data).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import timeq0 as q0


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
    return q0.all_tasks()


def task_argv(t) -> str:
    k = t[0]
    if k == "wait":
        _, g, wk, T = t
        return f"--task wait --graph {g} --wk {wk} --horizon {T}"
    if k in ("merge1", "split1", "roundtrip"):
        _, g, T = t
        return f"--task {k} --graph {g} --horizon {T}"
    if k == "detcore":
        _, g, f, kk, dk = t
        return f"--task detcore --graph {g} --field {f} --node {kk} --dk {dk}"
    if k == "multicover":
        if t[1] == "j2":
            return f"--task multicover --cell j2 --bg {t[2]}"
        return (f"--task multicover --cell tiny --graph {t[2]} "
                f"--field {t[3]}")
    if k == "disjoint":
        _, sub, ftag, T = t
        return f"--task disjoint --sub {sub} --ftag {ftag} --horizon {T}"
    if k == "seqrev":
        _, n, f, dk = t
        return f"--task seqrev --name {n} --ftag {f} --dk {dk}"
    if k == "timing":
        _, g, dk, T = t
        return f"--task timing --graph {g} --dk {dk} --horizon {T}"
    if k == "hidden":
        _, ftag, dk = t
        return f"--task hidden --ftag {ftag} --dk {dk}"
    if k == "hiddenq":
        _, g, v = t
        return f"--task hiddenq --graph {g} --variant {v}"
    if k == "sched":
        _, sub, T = t
        return f"--task sched --sub {sub} --horizon {T}"
    if k == "forward":
        _, g, T = t
        return f"--task forward --graph {g} --horizon {T}"
    if k == "toy":
        _, dk, idx = t
        return f"--task toy --dk {dk} --idx {idx}"
    if k == "horizon":
        _, hk, g, T = t
        return f"--task horizon --hk {hk} --graph {g} --horizon {T}"
    return "--task fw"


def _is_V0(Xm: dict, Xp) -> bool:
    try:
        n0 = float(np.sum(np.abs(np.asarray(Xm["psi"])) ** 2))
        if Xp is None:
            return bool(n0 == 0.0)
        n1 = float(np.sum(np.abs(np.asarray(Xp["psi"])) ** 2))
        return bool(n0 == 0.0 and n1 == 0.0)
    except Exception:
        return False


def _run_boundary(t: tuple) -> dict:
    b = q0.boundary_for_task(t)
    Xm, Xp, T = b["Xm"], b["Xp"], int(b["T"])
    meta = dict(b["meta"])
    cnt = q0.count_histories_Q(Xm, Xp, T)
    sk = q0.skeleton_Q(Xm, Xp, T)
    sk_ok = bool(cnt["N"] == sk["expect_timed"])
    v0 = _is_V0(Xm, Xp)
    red = None
    if v0:
        red = q0.reduced_count_canonical(Xm, Xp, T)
        if red.get("outside"):
            r2 = q0.reduced_count_V0_iso(Xm, Xp, T)
            red = {"N_red": r2["N_red"], "N_skel_red": 0,
                   "S_vec_red": [], "cm": "outside", "cp": "outside",
                   "identity_ok": True, "outside": True,
                   "method": "V0iso",
                   "complete": bool(r2.get("complete", True))}
        else:
            red["method"] = "canonical"
    else:
        r = q0.reduced_count_field(Xm, Xp, T)
        red = {"N_red": r.get("N_red", 0), "N_skel_red": 0,
               "S_vec_red": [], "cm": "field", "cp": "field",
               "identity_ok": True, "outside": False,
               "method": "field", "complete": bool(r.get("complete", True)),
               "n_graph_walks": int(r.get("n_graph_walks", 0))}
    ex = q0.explicit_histories_Q(Xm, Xp, T, cap=5000)
    rev_ok = True
    acct_ok = True
    worst_close = 0.0
    if ex.get("complete") and ex.get("N", 0) > 0 and ex["N"] <= 200:
        for hist, evs in zip(ex["walks"], ex["events"]):
            rh = q0.reverse_history(hist)
            for s in range(len(rh) - 1):
                if not q0.is_enlarged_step_ok(rh[s], rh[s + 1]):
                    rev_ok = False
                    break
            for s, ev in enumerate(evs):
                ac = q0.event_accounting(hist[s], hist[s + 1], ev)
                if ev.get("kind") == "C":
                    worst_close = max(worst_close,
                                      abs(float(ac.get("close_merge", 0.0))))
                    if abs(float(ac.get("close_merge", 0.0))) >= 1e-9:
                        acct_ok = False
                    if ac.get("support") != "one-neighborhood-local":
                        pass
                elif ev.get("kind") == "S":
                    worst_close = max(worst_close,
                                      abs(float(ac.get("close_split", 0.0))))
                    if abs(float(ac.get("close_split", 0.0))) >= 1e-9:
                        acct_ok = False
                    if abs(float(ac.get("invert_err", 0.0))) >= 1e-9:
                        acct_ok = False
                else:
                    if not ac.get("Q_same", False):
                        acct_ok = False
            if not rev_ok:
                break
    Xr_m = q0.reverse_history([Xp])[0] if Xp is not None else None
    Xr_p = q0.reverse_history([Xm])[0] if Xm is not None else None
    n_rev = None
    sym_ok = True
    if Xr_m is not None and Xr_p is not None:
        try:
            n_rev = int(q0.count_histories_Q(Xr_m, Xr_p, T)["N"])
            sym_ok = bool(n_rev == cnt["N"])
        except Exception:
            sym_ok = False
    proj = []
    if ex.get("complete") and ex.get("N", 0) <= 500:
        try:
            from bh_graph import time0 as t0

            uni, _, byn = q0._time0_universe()
            for hist in ex["walks"]:
                seq = []
                for X in hist:
                    c = t0.canonical_id(X["g"], uni, byn)
                    seq.append(str(c) if c else "out")
                proj.append(seq)
        except Exception:
            proj = []
    return {"meta": meta, "T": T, "V0": bool(v0),
            "N_Q": int(cnt["N"]), "widths_Q": cnt["widths"],
            "total_final_Q": int(cnt["total_final"]),
            "S_vec_Q": sk["S_vec"], "N_skel_Q": int(sk["N_skel"]),
            "expect_timed_Q": int(sk["expect_timed"]),
            "skel_identity_ok": bool(sk_ok),
            "red": red, "explicit_complete": bool(ex.get("complete")),
            "explicit_N": int(ex.get("N", 0)),
            "rev_ok": bool(rev_ok), "acct_ok": bool(acct_ok),
            "worst_close": float(worst_close),
            "N_rev": None if n_rev is None else int(n_rev),
            "sym_ok": bool(sym_ok), "proj": proj[:200]}


def run_wait(graph: str, wk: str, horizon: int, outdir: str) -> str:
    rec = _run_boundary(("wait", graph, wk, int(horizon)))
    return _write(outdir, f"wait_{graph}_{wk}_T{horizon}.json", rec)


def run_merge1(graph: str, horizon: int, outdir: str) -> str:
    rec = _run_boundary(("merge1", graph, int(horizon)))
    return _write(outdir, f"merge1_{graph}_T{horizon}.json", rec)


def run_split1(graph: str, horizon: int, outdir: str) -> str:
    rec = _run_boundary(("split1", graph, int(horizon)))
    return _write(outdir, f"split1_{graph}_T{horizon}.json", rec)


def run_roundtrip(graph: str, horizon: int, outdir: str) -> str:
    rec = _run_boundary(("roundtrip", graph, int(horizon)))
    return _write(outdir, f"roundtrip_{graph}_T{horizon}.json", rec)


def run_detcore(graph: str, field: str, node: int, dk: str,
                outdir: str) -> str:
    rec = _run_boundary(("detcore", graph, field, int(node), dk))
    return _write(outdir, f"detcore_{graph}_{field}_{node}_{dk}.json", rec)


def run_multicover(cell: str, graph: str, field: str, bg: str,
                   outdir: str) -> str:
    if cell == "j2":
        rec = _run_boundary(("multicover", "j2", bg))
        return _write(outdir, f"multicover_j2_{bg}.json", rec)
    rec = _run_boundary(("multicover", "tiny", graph, field))
    return _write(outdir, f"multicover_{graph}_{field}.json", rec)


def run_disjoint(sub: str, ftag: str, horizon: int, outdir: str) -> str:
    rec = _run_boundary(("disjoint", sub, ftag, int(horizon)))
    return _write(outdir,
                  f"disjoint_{sub}_{safe_tag(ftag)}_T{horizon}.json", rec)


def run_seqrev(name: str, ftag: str, dk: str, outdir: str) -> str:
    rec = _run_boundary(("seqrev", name, ftag, dk))
    return _write(outdir, f"seqrev_{name}_{safe_tag(ftag)}_{dk}.json", rec)


def run_timing(graph: str, dk: str, horizon: int, outdir: str) -> str:
    rec = _run_boundary(("timing", graph, dk, int(horizon)))
    return _write(outdir, f"timing_{graph}_{dk}_T{horizon}.json", rec)


def run_hidden(ftag: str, dk: str, outdir: str) -> str:
    rec = _run_boundary(("hidden", ftag, dk))
    return _write(outdir, f"hidden_{safe_tag(ftag)}_{dk}.json", rec)


def run_hiddenq(graph: str, variant: str, outdir: str) -> str:
    rec = _run_boundary(("hiddenq", graph, variant))
    return _write(outdir, f"hiddenq_{graph}_{variant}.json", rec)


def run_sched(sub: str, horizon: int, outdir: str) -> str:
    rec = _run_boundary(("sched", sub, int(horizon)))
    return _write(outdir, f"sched_{sub}_T{horizon}.json", rec)


def run_forward(graph: str, horizon: int, outdir: str) -> str:
    from bh_graph import time0 as t0

    b = q0.boundary_for_task(("forward", graph, int(horizon)))
    Xm, T = b["Xm"], int(b["T"])
    fc = q0.forward_census_Q(Xm, T)
    uni, tra, byn = q0._time0_universe()
    cm = t0.canonical_id(Xm["g"], uni, byn)
    tot_r = 0
    ncl_r = 0
    if cm is not None:
        d = t0.count_walks_from(tra["adj"], cm, T)
        tot_r = int(sum(d.values()))
        ncl_r = int(len(d))
    rec = {"meta": b["meta"], "T": T, "forward_Q": fc,
           "forward_red": {"total": tot_r, "n_classes": ncl_r,
                           "cm": None if cm is None else str(cm)}}
    return _write(outdir, f"forward_{graph}_T{T}.json", rec)


def run_toy(dk: str, idx: int, outdir: str) -> str:
    rec = _run_boundary(("toy", dk, int(idx)))
    return _write(outdir, f"toy_{dk}_{idx}.json", rec)


def run_horizon(hk: str, graph: str, horizon: int, outdir: str) -> str:
    rec = _run_boundary(("horizon", hk, graph, int(horizon)))
    return _write(outdir, f"horizon_{hk}_{graph}_T{horizon}.json", rec)


def run_fw(outdir: str) -> str:
    rec = {"meta": {"kind": "fw"}}
    rec.update(q0.firewall_record())
    return _write(outdir, "fw_timeq0.json", rec)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", choices=("wait", "merge1", "split1",
                                       "roundtrip", "detcore", "multicover",
                                       "disjoint", "seqrev", "timing",
                                       "hidden", "hiddenq", "sched",
                                       "forward", "toy", "horizon", "fw"))
    ap.add_argument("--graph", default=None)
    ap.add_argument("--wk", default="on")
    ap.add_argument("--horizon", type=int, default=2)
    ap.add_argument("--field", default=None)
    ap.add_argument("--node", type=int, default=0)
    ap.add_argument("--dk", default=None)
    ap.add_argument("--cell", default="tiny")
    ap.add_argument("--bg", default=None)
    ap.add_argument("--sub", default=None)
    ap.add_argument("--ftag", default=None)
    ap.add_argument("--name", default=None)
    ap.add_argument("--variant", default="empty")
    ap.add_argument("--idx", type=int, default=0)
    ap.add_argument("--hk", default="wait")
    ap.add_argument("--outdir", default="data/timeq0")
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
    if a.task == "wait":
        print(run_wait(a.graph, a.wk, a.horizon, a.outdir))
    elif a.task == "merge1":
        print(run_merge1(a.graph, a.horizon, a.outdir))
    elif a.task == "split1":
        print(run_split1(a.graph, a.horizon, a.outdir))
    elif a.task == "roundtrip":
        print(run_roundtrip(a.graph, a.horizon, a.outdir))
    elif a.task == "detcore":
        print(run_detcore(a.graph, a.field, a.node, a.dk, a.outdir))
    elif a.task == "multicover":
        print(run_multicover(a.cell, a.graph, a.field, a.bg, a.outdir))
    elif a.task == "disjoint":
        print(run_disjoint(a.sub, a.ftag, a.horizon, a.outdir))
    elif a.task == "seqrev":
        print(run_seqrev(a.name, a.ftag, a.dk, a.outdir))
    elif a.task == "timing":
        print(run_timing(a.graph, a.dk, a.horizon, a.outdir))
    elif a.task == "hidden":
        print(run_hidden(a.ftag, a.dk, a.outdir))
    elif a.task == "hiddenq":
        print(run_hiddenq(a.graph, a.variant, a.outdir))
    elif a.task == "sched":
        print(run_sched(a.sub, a.horizon, a.outdir))
    elif a.task == "forward":
        print(run_forward(a.graph, a.horizon, a.outdir))
    elif a.task == "toy":
        print(run_toy(a.dk, a.idx, a.outdir))
    elif a.task == "horizon":
        print(run_horizon(a.hk, a.graph, a.horizon, a.outdir))
    elif a.task == "fw":
        print(run_fw(a.outdir))
    else:
        raise SystemExit("no task given (see --print-all)")


if __name__ == "__main__":
    main()
