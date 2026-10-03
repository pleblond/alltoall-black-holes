"""FIBER-0 campaign (frozen FIBER0-PREREG cells, pre-data).

Tasks (mp pool, module-level workers, 64-way on beast):
  - tiny: per-cell facts (76 tasks: A/B/C/D/E/F/G/H/J/K/M1/Q-covers/R).
  - j2leg: per-background legs (7 tasks: L + D-blocks + transport + Q).
  - sched: scheduler census + anatomy invariance (24 states, section O).
  - timeP: TIME-0 split-step support + rival pushforward (section P).
  - rivalsQ: class-level rival density checks + proofs (section Q).
  - factorN: disjoint-support factorization (section N).
  - volumeHI: invariant-volume exhibits + normalizability (H/I).
  - hbrK: matched-pair HBR binding leg (section K).
  - hiddenM2: J2 sheet-readout instantiation (section M2).

Deterministic (no RNG anywhere). Output: data/fiber0_ledger.json.
Gates applied by scripts/fiber0_analyze.py. NO fitting after data.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import fiber0 as F

_REF_CELLS = {}
_REF_J2 = {}


def _sanitize(x):
    if isinstance(x, dict):
        return {str(k): _sanitize(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_sanitize(v) for v in x]
    if isinstance(x, np.ndarray):
        return [_sanitize(v) for v in x.tolist()]
    if isinstance(x, (np.floating, np.integer)):
        return x.item()
    if isinstance(x, complex):
        return [float(x.real), float(x.imag)]
    if isinstance(x, float) and (np.isnan(x) or np.isinf(x)):
        return str(x)
    return x


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def _git_sha():
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True,
            cwd=os.path.join(os.path.dirname(__file__), "..")).stdout.strip()
    except Exception:
        return "unknown"


# ---------------------------------------------------------------------------
# Workers
# ---------------------------------------------------------------------------

def run_tiny_task(key):
    graph_name, field_name, k = key
    facts = F.cell_facts(graph_name, field_name, k, _REF_CELLS)
    return _sanitize(facts)


def run_j2leg_task(background):
    facts = F.j2_leg_facts(background, _REF_J2)
    return _sanitize(facts)


def run_sched_task(key):
    graph_name, field_name = key
    st = F.merged_state(graph_name, field_name)
    g, psi, order = st["g"], st["psi"], st["order"]
    cen = F.sync_scheduler_census(g, psi, order)
    edges = sorted(tuple(sorted(e)) for e in g.edges())
    inv_ok = True
    n_checked = 0
    if not cen.get("capped"):
        import itertools as _it
        for m in (2, 3, 4):
            if len(edges) < m:
                continue
            for subset in _it.combinations(edges, m):
                n_checked += 1
                if not F.is_anatomy_scheduler_invariant_ok(
                        g, psi, order, list(subset)):
                    inv_ok = False
    return _sanitize({
        "state": f"{graph_name}/{field_name}",
        "E": cen.get("E"), "capped": bool(cen.get("capped")),
        "n_subsets": cen.get("n_subsets"),
        "n_all_match": cen.get("n_all_match"),
        "all_match": bool(cen.get("n_all_match") == cen.get("n_subsets")),
        "anatomy_invariant": bool(inv_ok),
        "anatomy_checked": int(n_checked),
        "xi_schema_ok": bool(F.xi_schema_ok())})


def run_timeP_task(_key):
    out = {"cells": [], "null": F.load_time0_null()}
    for gn in ("single", "k2", "triangle"):
        for fn in ("bonding", "zero"):
            st = F.merged_state(gn, fn)
            g, psi, order = st["g"], st["psi"], st["order"]
            idx = {v: t for t, v in enumerate(order)}
            steps = F.labeled_split_steps(g)
            # Demo node: first node carrying S-steps.
            by_w = {}
            for ev in steps["steps"]:
                by_w.setdefault(ev["event"][0], []).append(ev)
            w_star = sorted(by_w)[0] if by_w else None
            s0 = complex(psi[idx[w_star]]) if w_star is not None else 0.0j
            kind = (F.fiber_class(g, psi, order, w_star)
                    if w_star is not None else "plane")
            d_probe = [complex(d) for d in F.D_SWEEP[:6]]
            tv = 0.0
            cover_tv = 0.0
            if w_star is not None:
                covs = F.undirected_cover_list(sorted(g.neighbors(w_star)))
                wA = F.rival_cover_weights_A(covs)
                wB = F.rival_cover_weights_B(covs)
                cover_tv = F.rival_tv_discrete(wA, wB)
                # Directed refinements per undirected key (even split).
                refin = {}
                for ev in by_w[w_star]:
                    ck = F.undirected_key(ev["event"][1], ev["event"][2])
                    refin[ck] = refin.get(ck, 0) + 1
                rhoA = [F.rival_d_density_A(d, s0, kind) for d in d_probe]
                rhoB = [F.rival_d_density_B(d, s0, kind) for d in d_probe]
                tabA, tabB = [], []
                for ev in by_w[w_star]:
                    ck = F.undirected_key(ev["event"][1], ev["event"][2])
                    nref = refin[ck]
                    for ra, rb in zip(rhoA, rhoB):
                        tabA.append(wA[ck] / nref * ra)
                        tabB.append(wB[ck] / nref * rb)
                zA, zB = sum(tabA), sum(tabB)
                if zA > 0.0 and zB > 0.0:
                    tv = 0.5 * sum(abs(a / zA - b / zB)
                                   for a, b in zip(tabA, tabB))
            out["cells"].append(_sanitize({
                "cell": f"{gn}/{fn}", "in_scope": steps["in_scope"],
                "n_steps": steps.get("n_steps", 0),
                "support_fixed": True,
                "alpha_bijection": (F.is_split_fraction_bijection_ok(s0)
                                    if s0 != 0.0 else None),
                "s_zero": bool(s0 == 0.0),
                "pushforward_tv": float(tv),
                "weights_differ": bool(tv > 0.0),
                "cover_tv_cell": float(cover_tv)}))
    return _sanitize(out)


def run_rivalsQ_task(_key):
    checks = {}
    for kind, s in (("plane", 1.0 + 0.5j), ("plane", 0.0j),
                    ("halfline", 0.0j)):
        checks[f"{kind}|s={s}"] = {
            "z2": bool(F.is_rival_z2_ok(kind, s)),
            "u1": bool(all(F.is_rival_density_covariant_ok(kind, s, a)
                           for a in F.U1_GRID)),
            "diff": F.rival_density_diff(kind, s),
            "proof": F.rival_normalization_proof(
                kind, bool(complex(s) == 0.0))}
    return _sanitize({
        "class_checks": checks,
        "radial_normalized": bool(F.is_rival_radial_normalized_ok()),
        "correlated_law": bool(F.is_correlated_law_valid_ok())})


def run_factorN_task(_key):
    info = F.disjoint_split_cells()
    g, psi, order = info["g"], info["psi"], info["order"]
    k1, k2 = info["k1"], info["k2"]
    covs1 = F.undirected_cover_list(sorted(g.neighbors(k1)))
    covs2 = F.undirected_cover_list(sorted(g.neighbors(k2)))
    comm_ok = True
    for _a, A1, B1 in covs1:
        for _b, A2, B2 in covs2:
            if not F.is_joint_commuting_ok(g, k1, k2, A1, B1, A2, B2):
                comm_ok = False
    rt_bad, rt_n = 0, 0
    d_pairs = [(complex(a), complex(b)) for a in F.D_SWEEP[:4]
               for b in F.D_SWEEP[:4]]
    for c1 in covs1:
        for c2 in covs2:
            for d1, d2 in d_pairs:
                rt_n += 1
                if not F.is_joint_roundtrip_ok(
                        g, psi, order, k1, k2,
                        {"cover_key": c1[0], "d": d1},
                        {"cover_key": c2[0], "d": d2}):
                    rt_bad += 1
    aut = F.state_automorphisms_bruteforce(g, psi, order)
    stab = [a for a in aut if a[k1] == k1 and a[k2] == k2]
    law = F.correlated_cover_law()["table"]
    prod_tv = 0.5 * sum(abs(v - 0.25) for row in law for v in row)
    return _sanitize({
        "cells": [k1, k2], "disjoint": True,
        "n_joint_covers": len(covs1) * len(covs2),
        "commuting": bool(comm_ok),
        "roundtrip": {"n": rt_n, "bad": rt_bad},
        "n_aut": len(aut), "n_joint_stab": len(stab),
        "correlated_valid": bool(F.is_correlated_law_valid_ok()),
        "product_tv": float(prod_tv),
        "differs_from_product": bool(prod_tv > 0.0)})


def run_volumeHI_task(_key):
    return _sanitize({
        "plane": {"exhibits": F.invariant_volume_exhibits("plane"),
                  "valid": bool(F.is_volume_pair_valid_ok("plane"))},
        "halfline": {"exhibits": F.invariant_volume_exhibits("halfline"),
                     "valid": bool(F.is_volume_pair_valid_ok("halfline"))},
        "lebesgue_divergent": bool(F.is_lebesgue_nonnormalizable_ok()),
        "radial_normalized": bool(F.is_rival_radial_normalized_ok())})


def run_hbrK_task(_key):
    from bh_graph import hidden as _h
    from bh_graph import malus
    from bh_graph.backreaction import energy_full
    pair = F.matched_hidden_pair_j2()
    g, order = pair["g"], pair["order"]
    pr = malus.sheet_projectors(order, pair["c3"])
    a_p, _ = _h.sector_split(pair["psi_A"], pr)
    b_p, _ = _h.sector_split(pair["psi_B"], pr)
    eA = energy_full(pair["psi_A"], g, order)
    eB = energy_full(pair["psi_B"], g, order)
    demo = F.ledger_sign_flip_demo()
    return _sanitize({
        "pmatch": float(np.abs(a_p - b_p).max()),
        "pmatch_ok": bool(np.abs(a_p - b_p).max() < 1e-12),
        "e_match_ok": bool(abs(eA - eB) < 1e-9),
        "n_flips": demo["n_flips"],
        "flip": demo["flip"]})


def run_hiddenM2_task(_key):
    legs = []
    for bg in F.J2_BACKGROUNDS:
        leg = F.j2_leg_state(bg)
        g, psi, order = leg["g"], leg["psi"], leg["order"]
        idx = {v: t for t, v in enumerate(order)}
        s = complex(psi[idx[leg["k"]]])
        sym_ok, anti_sees = True, False
        for d in F.D_SWEEP:
            p, q = F.fiber_point(s, complex(d))
            if not F.is_linear_readout_theorem_ok(1.0, 1.0, p, q):
                sym_ok = False
            pa, qa = F.fiber_point(s, 0.0j)
            if abs((p - q) - (pa - qa)) > 1e-12:
                anti_sees = True
        legs.append({"leg": bg, "symmetric_ok": bool(sym_ok),
                     "antisymmetric_sees_d": bool(anti_sees),
                     "convention": "daughters inherit k sheet; "
                                   "symmetric readouts see s only"})
    return _sanitize({"legs": legs})


TASKS = {
    "tiny": run_tiny_task,
    "j2leg": run_j2leg_task,
    "sched": run_sched_task,
    "timeP": run_timeP_task,
    "rivalsQ": run_rivalsQ_task,
    "factorN": run_factorN_task,
    "volumeHI": run_volumeHI_task,
    "hbrK": run_hbrK_task,
    "hiddenM2": run_hiddenM2_task,
}


def build_task_list():
    tasks = []
    for c in F.fiber0_cells():
        tasks.append(("tiny", (c["graph"], c["field"], c["k"])))
    for bg in F.J2_BACKGROUNDS:
        tasks.append(("j2leg", bg))
    for gn in F.FIBER0_GRAPHS:
        for fn in F.FIBER0_FIELDS:
            tasks.append(("sched", (gn, fn)))
    for kind in ("timeP", "rivalsQ", "factorN", "volumeHI", "hbrK",
                 "hiddenM2"):
        tasks.append((kind, None))
    return tasks


def _run_one(task):
    kind, key = task
    t0 = time.time()
    try:
        res = TASKS[kind](key)
        return {"kind": kind, "key": str(key), "ok_run": True,
                "result": res, "elapsed_s": time.time() - t0}
    except Exception as e:  # noqa: BLE001 - ledger records crashes
        return {"kind": kind, "key": str(key), "ok_run": False,
                "error": f"{type(e).__name__}: {e}"[:300],
                "elapsed_s": time.time() - t0}


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--out", default="data/fiber0_ledger.json")
    ap.add_argument("--ref-ledger",
                    default="data/fiber0_split0_ledger_ref.json")
    args = ap.parse_args()
    global _REF_CELLS, _REF_J2
    with open(args.ref_ledger) as f:
        ref = json.load(f)
    _REF_CELLS = {c["cell"]: c for c in ref.get("cells", [])}
    _REF_J2 = {j["background"]: j for j in ref.get("j2", [])}
    # SPLIT-0 filed uniform under 'uniform'; map overlap in workers.
    tasks = build_task_list()
    t0 = time.time()
    if args.jobs <= 1:
        records = [_run_one(t) for t in tasks]
    else:
        with Pool(processes=args.jobs) as pool:
            records = pool.map(_run_one, tasks)
    prov = {"git": _git_sha(), "platform": platform.platform(),
            "python": platform.python_version(),
            "workers": int(args.jobs),
            "elapsed_s": time.time() - t0,
            "n_tasks": len(records),
            "ref_ledger_sha256": _sha256(args.ref_ledger)}
    with open(args.out, "w") as f:
        json.dump(_sanitize({"provenance": prov, "records": records}), f)
    n_fail = sum(1 for r in records if not r.get("ok_run"))
    print(f"ledger: {args.out} tasks={len(records)} "
          f"failures={n_fail} elapsed={prov['elapsed_s']:.1f}s")


if __name__ == "__main__":
    main()
