"""REWIRE-0 deterministic rewire census campaign (FROZEN protocol).

Consumes read-only: BR-1 (neutral-move enormity), GRAV-0 (locality +
blind-move nulls), U0 (candidate-law precedent), RAND-0 (quotient
apparatus), SYM-0 (R x U1 redundancy), CONS-0 (ledger identities),
VAC-0/VAC-FIELD/VAC-COMP/VAC-TEXTURE (JOINT vacua + textures),
VAC-EXC (controlled disturbances), MEASURE0-DEBT (firewall).
No new dynamics, no measure, no threshold, no fitted score.
Deterministic given frozen seeds; parallel over independent tasks
(beast 96: jobs <= 90, nice).

Tasks (20): tiny-<graph> x10 (exhaustive x 7 fields), j2L4-joint,
j2L4-circle, j2L4-texture, j2L4-exc-{VPLUS,VPI,VMINUS}, j2L8-anchor,
j2L28-anchor, historical, controls. Each invocation writes one JSON
record to --outdir. Analyzer scripts/rewire0_analyze.py merges +
verdicts. Exit 0 always (verdicts are data, not errors).
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import rewire0 as r0

TASKS = ([f"tiny-{g}" for g in r0.TINY_GRAPHS]
         + ["j2L4-joint", "j2L4-circle", "j2L4-texture",
            "j2L4-exc-VPLUS", "j2L4-exc-VPI", "j2L4-exc-VMINUS",
            "j2L8-anchor", "j2L28-anchor", "historical", "controls"])


def _smax_for(graph_name: str, g) -> int:
    if graph_name.startswith("j2"):
        return r0.SPAN_SMAX_J2
    from bh_graph.update_rule import edge_span

    try:
        return max(edge_span(g, u, v, r0.SPAN_RADIUS) for u, v in g.edges())
    except Exception:
        return r0.SPAN_SMAX_J2


def _covariance_per_principle(g, psi, order, rewires, rows, smax, perms):
    out = {}
    for p in r0.PRINCIPLES:
        mask = r0.principle_mask(rows, p, smax=smax)
        idx = [i for i, m in enumerate(mask) if m]
        if not idx:
            out[p] = {"n_surv": 0, "covariant": True, "n_stab": 0,
                      "max_orbit": 0, "closure_violations": 0,
                      "note": "vacuous (no survivors)"}
            continue
        rep = r0.covariance_audit(g, psi, list(order), rewires, idx, perms)
        rep["n_surv"] = int(len(idx))
        rep["max_orbit"] = int(max(rep["orbits"])) if rep["orbits"] else 0
        del rep["orbits"]
        out[p] = rep
    return out


def _run_states(graph_name: str, g, order, fields: dict, smax: int,
                perms, anchored: int | None = None) -> list:
    if anchored is not None:
        prim = r0.anchor_primaries(g, int(anchored))
        rewires = r0.enumerate_rewires(g, primaries=prim)
    else:
        rewires = r0.enumerate_rewires(g)
    q0 = r0.physical_quotient(g, fields[next(iter(fields))], list(order),
                              rewires)
    rows_out = []
    for fname, psi in fields.items():
        t0 = time.time()
        rep = r0.census_state(g, psi, list(order), rewires=rewires,
                              smax=smax)
        # Recompute rows for covariance (census_state is exact; rows
        # rebuilt identically here for survivor indexing).
        from bh_graph.ballistic import hamiltonian

        import numpy as np

        try:
            H0 = hamiltonian(g, order=list(order))
            H0d = H0.toarray() if hasattr(H0, "toarray") else np.asarray(H0)
            href = float(np.linalg.norm(H0d @ np.asarray(psi)))
        except Exception:
            href = float("nan")
        rows = []
        for r in rewires:
            qr = r0.rewire_quantities(g, psi, list(order), r, smax=smax)
            qr["_href"] = href
            rows.append(qr)
        cov = _covariance_per_principle(g, psi, list(order), rewires,
                                        rows, smax, perms)
        rows_out.append({"graph": graph_name, "field": fname,
                         "n_nodes": int(g.number_of_nodes()),
                         "n_edges": int(g.number_of_edges()),
                         "anchored": anchored, "smax": int(smax),
                         "n_raw": rep["n_raw"], "n_phys": rep["n_phys"],
                         "principles": rep["principles"],
                         "covariance": cov, "dist": rep["dist"],
                         "max_ledger_err": rep["max_ledger_err"],
                         "href": rep["href"],
                         "elapsed_s": round(time.time() - t0, 3)})
    return rows_out


def run_task(task: str) -> dict:
    import numpy as np

    t0 = time.time()
    if task.startswith("tiny-"):
        name = task[len("tiny-"):]
        g = r0.tiny_graph(name)
        order = list(g.nodes())
        fields = {f: r0.tiny_field(f, order) for f in r0.TINY_FIELDS}
        smax = _smax_for(task, g)
        try:
            ag = r0.full_aut_group_capped(g)
            auts = ag.get("auts", []) if isinstance(ag, dict) else []
            perms = [dict(p) for p in auts[:200] if isinstance(p, dict)]
            if not perms:
                perms = [{v: v for v in order}]
        except Exception:
            perms = [{v: v for v in order}]
        rows = _run_states(task, g, order, fields, smax, perms)
        return {"task": task, "rows": rows,
                "elapsed_s": round(time.time() - t0, 3)}
    if task in ("j2L4-joint", "j2L4-circle", "j2L4-texture",
                "j2L4-exc-VPLUS", "j2L4-exc-VPI", "j2L4-exc-VMINUS"):
        sub = r0.j2_substrate(4)
        g, order = sub["graph"], sub["order"]
        perms = r0.j2_aut_sample(4)
        smax = r0.SPAN_SMAX_J2
        if task == "j2L4-joint":
            fields = {n: r0.j2_field(n, sub) for n in r0.JOINT_FIELDS}
        elif task == "j2L4-circle":
            fields = {f"circle@{a:.3f}": r0.circle_field(a, sub)
                      for a in r0.CIRCLE_ALPHAS}
        elif task == "j2L4-texture":
            fields = {f"texture-{f}": r0.texture_field(f, sub, 4)
                      for f in r0.TEXTURE_FAMS}
        else:
            vac = task.split("-")[-1]
            fields = {f"exc-{vac}-{k}": r0.excitation_field(k, vac, sub)
                      for k in r0.EXC_KINDS}
        rows = _run_states(task, g, order, fields, smax, perms)
        return {"task": task, "rows": rows,
                "elapsed_s": round(time.time() - t0, 3)}
    if task == "j2L8-anchor":
        sub = r0.j2_substrate(8)
        g, order = sub["graph"], sub["order"]
        perms = r0.j2_aut_sample(8)
        fields = {n: r0.j2_field(n, sub) for n in r0.JOINT_FIELDS}
        fields["texture-sine-x"] = r0.texture_field("sine-x", sub, 8)
        fields["exc-VPLUS-packet"] = r0.excitation_field("packet", "VPLUS",
                                                         sub)
        fields["exc-VMINUS-point_amp"] = r0.excitation_field(
            "point_amp", "VMINUS", sub)
        rows = _run_states(task, g, order, fields, r0.SPAN_SMAX_J2,
                           perms, anchored=r0.N_ANCHOR_MID)
        return {"task": task, "rows": rows,
                "elapsed_s": round(time.time() - t0, 3)}
    if task == "j2L28-anchor":
        sub = r0.j2_substrate(28)
        g, order = sub["graph"], sub["order"]
        perms = r0.j2_aut_sample(28)
        fields = {n: r0.j2_field(n, sub) for n in r0.JOINT_FIELDS}
        fields["texture-sine-x"] = r0.texture_field("sine-x", sub, 28)
        fields["exc-VPLUS-packet"] = r0.excitation_field("packet", "VPLUS",
                                                         sub)
        fields["exc-VMINUS-point_amp"] = r0.excitation_field(
            "point_amp", "VMINUS", sub)
        rows = _run_states(task, g, order, fields, r0.SPAN_SMAX_J2,
                           perms, anchored=r0.N_ANCHOR_HEAD)
        return {"task": task, "rows": rows,
                "elapsed_s": round(time.time() - t0, 3)}
    if task == "historical":
        br1 = {"L28_closed": r0.br1_m1_legal_count_closed(28),
               "banked": r0.BR1_N_LEGAL_L28,
               "match": bool(r0.br1_m1_legal_count_closed(28)
                             == r0.BR1_N_LEGAL_L28)}
        sub4 = r0.j2_substrate(4)
        blind4 = r0.blind_frozen_probe(sub4["graph"], seed=0)
        sub8 = r0.j2_substrate(8)
        blind8 = r0.blind_frozen_probe(sub8["graph"], seed=0)
        return {"task": task, "br1": br1, "blind_L4": blind4,
                "blind_L8": blind8,
                "elapsed_s": round(time.time() - t0, 3)}
    if task == "controls":
        # Quotient invariance across relabel x phase grid (tiny).
        g = r0.tiny_graph("ring6")
        order = list(g.nodes())
        psi = r0.tiny_field("random_s7", order)
        n0 = r0.physical_quotient(
            g, psi, order, r0.enumerate_rewires(g))["n_phys"]
        ok = True
        for s in (1, 2, 5):
            perm = {v: (v + s) % 6 for v in order}
            for alpha in (0.0, math.pi / 4.0, math.pi):
                if not r0.is_quotient_invariant_ok(g, psi, order, perm,
                                                   alpha):
                    ok = False
        # Determinism: repeated census bit-identical (counts + statuses).
        r1 = r0.census_state(g, psi, order)
        r2 = r0.census_state(g, psi, order)
        det = bool(r1["n_phys"] == r2["n_phys"]
                   and all(r1["principles"][p]["status"]
                           == r2["principles"][p]["status"]
                           for p in r0.PRINCIPLES))
        return {"task": task, "quotient_invariant": bool(ok),
                "n_phys_ring6": int(n0), "deterministic": det,
                "elapsed_s": round(time.time() - t0, 3)}
    raise ValueError(f"unknown task: {task}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--print-all", action="store_true")
    ap.add_argument("--task", default=None)
    ap.add_argument("--outdir", default="data/rewire0")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--jobs", type=int, default=4)
    args = ap.parse_args()
    if args.print_all:
        for t in TASKS:
            print(f"rewire0 :: {t}")
        return 0
    if args.task is not None:
        rec = run_task(args.task)
        os.makedirs(args.outdir, exist_ok=True)
        with open(os.path.join(args.outdir, f"{args.task}.json"), "w") as f:
            json.dump(rec, f, indent=1)
        print(f"REWIRE0-DONE {args.task} "
              f"elapsed={rec.get('elapsed_s', 0)}s")
        return 0
    if args.all:
        import multiprocessing as mp

        os.makedirs(args.outdir, exist_ok=True)

        def _one(t):
            rec = run_task(t)
            with open(os.path.join(args.outdir, f"{t}.json"), "w") as f:
                json.dump(rec, f, indent=1)
            return t

        with mp.Pool(int(args.jobs)) as pool:
            done = pool.map(_one, TASKS)
        print(f"REWIRE0-ALL-DONE {len(done)}/{len(TASKS)}")
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
