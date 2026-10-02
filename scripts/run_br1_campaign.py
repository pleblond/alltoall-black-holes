"""BR-1 campaign runner (FROZEN pre-data; see BR1-PREREG in docs/DEFERRED.md).

Sections: B-census, t=0 baselines, D/F neutral drift + survival, C existing-U
audit (+ C2 damaged controls), G single-defect probes, I small-field
continuity, C0 zero-field gate, C6 wave check. Deterministic; seeds frozen.
Output: data/br1_vacuum.json.
"""
import json
import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import networkx as nx
import numpy as np

from bh_graph.backreaction import (  # noqa: E402
    all_relocations,
    count_relocations,
    delta_e_batch,
    delta_e_full,
    sample_relocations,
)
from bh_graph.ballistic import (  # noqa: E402
    com,
    gaussian_packet,
    index_of,
    is_normalized_ok,
    node_order,
    oneway_run,
)
from bh_graph.blind_u import nsquares  # noqa: E402
from bh_graph.formation import (  # noqa: E402
    j2_torus_coords,
    j2_torus_graph,
)
from bh_graph.graphs import build_j2_ball, build_torus_grid  # noqa: E402
from bh_graph.rigidity import (  # noqa: E402
    ball_label_maps,
    chord_distance_hist,
    death_move,
    defect_inject,
    disconnect_frac,
    max_abs_dep_over_field,
    neutral_drift,
    quotient_square_frac,
    span_signature,
    square_label_maps,
    torus_label_maps,
    vacuum_fingerprint,
)
from bh_graph.update_rule import (  # noqa: E402
    evolve,
    inject_shortcuts,
    rule_anneal,
    rule_guillotine,
    rule_null,
    rule_scramble,
    rule_slide,
    total_longs,
    total_longs_selfcal,
)
from bh_graph.blind_u import (  # noqa: E402
    rule_kappa_flat,
    rule_square,
    rule_square_metropolis,
    rule_triangle,
)

# ---- Frozen campaign constants (BR1-PREREG) ----
DRIFT_SEEDS = (0, 1, 2)
T_DRIFT = 3000
SNAP = 25
HEAVY_EVERY = 4
BALL_R = (12, 18, 24)
BALL_WIN = {12: (11, 4, 9), 18: (17, 6, 14), 24: (22, 8, 20)}  # R -> rmax, plo, phi
TORUS_WIN = (13, 5, 11)  # rmax, plo, phi for L28 tori
ANATOMY_N = 2000
C0_N = 2000
DEFECT_SEEDS = (0, 1, 2)
PSI_HAT_SEED = 1001
EPS_GRID = (1.0, 1e-1, 1e-2, 1e-4, 1e-8)
WAVE_STEPS = 60
WAVE_DT = 0.1


def log(msg):
    print(f"[br1] {msg}", flush=True)


def ball_fp_kwargs(g):
    R = g.graph.get("radius", None)
    rmax, plo, phi = BALL_WIN[R]
    qmap, cellmap = ball_label_maps(g)
    return dict(src=(0, 0, 0), rmax=rmax, qmap=qmap, cellmap=cellmap,
                p_lo=plo, p_hi=phi)


def torus_fp_kwargs(g, L):
    rmax, plo, phi = TORUS_WIN
    qmap, cellmap = torus_label_maps(j2_torus_coords(L))
    return dict(src=0, rmax=rmax, qmap=qmap, cellmap=cellmap, p_lo=plo, p_hi=phi,
                periods=(L, L))


def run_census():
    log("B-census: exact + closed-form + anatomy")
    out = {"exact": {}, "closed": {}, "anatomy": {}}
    for L in (4, 6):
        g = j2_torus_graph(L)
        n_enum = sum(1 for _ in all_relocations(g))
        out["exact"][str(L)] = {
            "n": g.number_of_nodes(), "e": g.number_of_edges(),
            "n_legal_enum": int(n_enum),
            "n_legal_closed": int(count_relocations(g)),
        }
    for L in (4, 6, 8, 12, 28):
        g = j2_torus_graph(L)
        out["closed"][str(L)] = {
            "n": g.number_of_nodes(), "e": g.number_of_edges(),
            "n_legal": int(count_relocations(g)),
        }
    for L in (8, 12, 28):
        g = j2_torus_graph(L)
        out["anatomy"][str(L)] = {
            "disconnect": disconnect_frac(g, ANATOMY_N, 100),
            "chords": chord_distance_hist(g, ANATOMY_N, 101),
        }
    return out


def run_baselines():
    log("t=0 baselines: J2 balls + span signature + tori + square control")
    out = {"balls": {}, "tori": {}, "span": {}}
    for R in BALL_R:
        g = build_j2_ball(R)
        g.graph["radius"] = R
        fp = vacuum_fingerprint(g, **ball_fp_kwargs(g))
        out["balls"][str(R)] = fp
        log(f"  ball R{R}: n={fp['n']} e={fp['e']} p={fp['p']:.4f} "
            f"c4={fp['c4']} bip={fp['bip_viol']} qfrac={fp['qfrac']}")
    g12 = j2_torus_graph(12)
    out["span"]["j2-L12-r3"] = span_signature(g12, 3)
    out["span"]["smax_J2"] = max(out["span"]["j2-L12-r3"]["hist"])
    out["span"]["selfcal_pristine"] = int(total_longs_selfcal(g12, 3))
    log(f"  smax_J2={out['span']['smax_J2']} "
        f"selfcal={out['span']['selfcal_pristine']}")
    for L in (12, 28):
        g = j2_torus_graph(L)
        out["tori"][f"j2-L{L}"] = vacuum_fingerprint(g, **torus_fp_kwargs(g, L))
    sq = build_torus_grid(28)
    order = node_order(sq)
    sqc = {v: (float(v[0]), float(v[1])) for v in order} if isinstance(order[0], tuple) \
        else {v: (float(v % 28), float(v // 28)) for v in order}
    qmap, cellmap = square_label_maps(sqc)
    rmax, plo, phi = TORUS_WIN
    out["tori"]["sq-L28"] = vacuum_fingerprint(
        sq, order[0], rmax, qmap, cellmap, plo, phi, periods=(28, 28))
    out["tori"]["sq-L28"]["src"] = list(order[0]) if isinstance(order[0], tuple) else order[0]
    return out, sqc


def run_drift(baselines):
    log(f"D/F drift: balls x{len(DRIFT_SEEDS)} seeds, T={T_DRIFT}")
    out = {"balls": {}, "controls": {}}
    for R in BALL_R:
        g = build_j2_ball(R)
        g.graph["radius"] = R
        kw = ball_fp_kwargs(g)
        base = baselines["balls"][str(R)]
        runs = {}
        for s in DRIFT_SEEDS:
            t0 = time.time()
            r = neutral_drift(g, T_DRIFT, s, SNAP, kw, HEAVY_EVERY)
            r["death"] = death_move(r["traj"], base)
            runs[str(s)] = r
            log(f"  R{R} seed {s}: death={r['death']} "
                f"({time.time() - t0:.1f}s)")
        out["balls"][str(R)] = runs
    # Square-torus N1 control (identical protocol, own baseline).
    sq = build_torus_grid(28)
    order = node_order(sq)
    src = order[0]
    sqc = {v: (float(v[0]), float(v[1])) for v in order} if isinstance(order[0], tuple) \
        else {v: (float(v % 28), float(v // 28)) for v in order}
    qmap, cellmap = square_label_maps(sqc)
    rmax, plo, phi = TORUS_WIN
    kw = dict(src=src, rmax=rmax, qmap=qmap, cellmap=cellmap, p_lo=plo, p_hi=phi,
              periods=(28, 28))
    base = baselines["tori"]["sq-L28"]
    runs = {}
    for s in (0, 1):
        r = neutral_drift(sq, T_DRIFT, s, SNAP, kw, HEAVY_EVERY)
        r["death"] = death_move(r["traj"], base)
        runs[str(s)] = r
        log(f"  sq-L28 seed {s}: death={r['death']}")
    out["controls"]["sq-L28"] = runs
    # J2-torus cross-check (1 seed, final graph kept for wave check).
    g = j2_torus_graph(28)
    kw = torus_fp_kwargs(g, 28)
    r = neutral_drift(g, T_DRIFT, 0, SNAP, kw, HEAVY_EVERY, return_final=True)
    r["death"] = death_move(r["traj"], baselines["tori"]["j2-L28"])
    out["controls"]["j2-L28"] = {"0": r}
    log(f"  j2-L28 seed 0: death={r['death']}")
    return out


def audit_run(g0, rule, steps, seed, kw, smax, extra_ctx=None, src=0):
    t0 = time.time()
    fp0 = vacuum_fingerprint(g0, **kw)
    longs0 = int(total_longs(g0, 3, smax))
    ctx_extra = dict(extra_ctx or {})
    traj, h, acc = evolve(g0, rule, steps, seed=seed, src=src,
                          proposals=ctx_extra.pop("proposals", 50),
                          swaps_per_step=4, T0=ctx_extra.pop("T0", 2.0),
                          Tend=0.05, radius=3, max_span=smax, **ctx_extra)
    fp1 = vacuum_fingerprint(h, **kw)
    return {
        "accepts": int(acc),
        "p_traj": [float(x) for x in traj],
        "longs_before": longs0,
        "longs_after": int(total_longs(h, 3, smax)),
        "fp_before": {k: fp0[k] for k in ("connected", "p", "c4", "bip_viol", "qfrac")},
        "fp_after": {k: fp1[k] for k in ("connected", "p", "c4", "bip_viol", "qfrac")},
        "seconds": round(time.time() - t0, 1),
    }


def run_audit(baselines, smax):
    log("C-audit: existing U on pristine J2 (+ C2 damaged controls)")
    out = {"pristine_L12": {}, "pristine_L28": {}, "damaged_L12": {}}
    g12 = j2_torus_graph(12)
    kw12 = torus_fp_kwargs(g12, 12)
    rules_L12 = [
        ("null", rule_null, 50, {}),
        ("scramble", rule_scramble, 50, {}),
        ("guillotine", rule_guillotine, 50, {}),
        ("anneal", rule_anneal, 50, {}),
        ("slide", rule_slide, 50, {}),
        ("square", rule_square, 200, {}),
        ("triangle", rule_triangle, 200, {}),
        ("metropolis_T0.25", rule_square_metropolis, 200, {"T0": 0.25}),
        ("metropolis_T1.0", rule_square_metropolis, 200, {"T0": 1.0}),
        ("kappa", rule_kappa_flat, 5, {"proposals": 12}),
    ]
    for name, rule, steps, ctx in rules_L12:
        r = audit_run(g12, rule, steps, 5000, kw12, smax, ctx)
        out["pristine_L12"][name] = r
        log(f"  L12 {name}: acc={r['accepts']} longs {r['longs_before']}->"
            f"{r['longs_after']} p {r['fp_before']['p']}->{r['fp_after']['p']} "
            f"({r['seconds']}s)")
    g28 = j2_torus_graph(28)
    kw28 = torus_fp_kwargs(g28, 28)
    for name, rule, steps, ctx in [
        ("null", rule_null, 30, {}),
        ("scramble", rule_scramble, 30, {}),
        ("guillotine", rule_guillotine, 30, {}),
        ("square", rule_square, 100, {}),
    ]:
        r = audit_run(g28, rule, steps, 6000, kw28, smax, ctx)
        out["pristine_L28"][name] = r
        log(f"  L28 {name}: acc={r['accepts']} longs {r['longs_before']}->"
            f"{r['longs_after']} ({r['seconds']}s)")
    # C2: damaged-J2 controls (rules must be active in principle on J2 fabric).
    dam = inject_shortcuts(g12, 20, seed=7000)
    for name, rule, steps, ctx in [
        ("guillotine", rule_guillotine, 50, {}),
        ("anneal", rule_anneal, 50, {}),
        ("slide", rule_slide, 50, {}),
    ]:
        r = audit_run(dam, rule, steps, 7001, kw12, smax, ctx)
        out["damaged_L12"][name] = r
        log(f"  dam12 {name}: acc={r['accepts']} longs {r['longs_before']}->"
            f"{r['longs_after']} ({r['seconds']}s)")
    return out


def run_defects(smax):
    log("G-defects: single-M1 defect + repair/blind response")
    out = {}
    g0 = j2_torus_graph(12)
    kw = torus_fp_kwargs(g0, 12)
    e0 = {tuple(sorted(e)) for e in g0.edges()}
    for s in DEFECT_SEEDS:
        gdef, mv = defect_inject(g0, 8000 + s)
        fp_def = vacuum_fingerprint(gdef, **kw)
        rec = {"move": mv, "defect_fp": {k: fp_def[k] for k in
               ("connected", "p", "c4", "bip_viol", "qfrac")},
               "defect_longs": int(total_longs(gdef, 3, smax)), "rules": {}}
        for name, rule, steps, ctx in [
            ("guillotine", rule_guillotine, 50, {}),
            ("anneal", rule_anneal, 50, {}),
            ("slide", rule_slide, 50, {}),
            ("square", rule_square, 200, {}),
        ]:
            t0 = time.time()
            _, h, acc = evolve(gdef, rule, steps, seed=8100 + s,
                               src=0, proposals=ctx.get("proposals", 50),
                               T0=ctx.get("T0", 2.0), Tend=0.05,
                               radius=3, max_span=smax)
            fp1 = vacuum_fingerprint(h, **kw)
            eh = {tuple(sorted(e)) for e in h.edges()}
            rec["rules"][name] = {
                "accepts": int(acc),
                "bit_restored": bool(eh == e0),
                "edge_overlap": int(len(eh & e0)),
                "longs_after": int(total_longs(h, 3, smax)),
                "fp_after": {k: fp1[k] for k in
                             ("connected", "p", "c4", "bip_viol", "qfrac")},
                "seconds": round(time.time() - t0, 1),
            }
            log(f"  def{s} {name}: acc={acc} restored={eh == e0} "
                f"longs->{rec['rules'][name]['longs_after']}")
        out[str(s)] = rec
    return out


def run_smallfield():
    log("I-smallfield: eps^2 continuity on J2-L8")
    g = j2_torus_graph(8)
    order = node_order(g)
    rng = np.random.default_rng(PSI_HAT_SEED)
    psi_hat = rng.standard_normal(len(order)) + 1j * rng.standard_normal(len(order))
    psi_hat /= np.linalg.norm(psi_hat)
    return max_abs_dep_over_field(psi_hat, g, order, EPS_GRID, 500, 2001)


def run_c0():
    log("C0 gate: zero-field bitwise null (exhaustive + sampled)")
    out = {}
    g = nx.cycle_graph(8)
    order = node_order(g)
    idx = index_of(order)
    psi0 = np.zeros(len(order), dtype=np.complex128)
    pairs = list(all_relocations(g))
    dE = delta_e_batch(psi0, idx, [m[0] for m in pairs], [m[1] for m in pairs])
    full = np.array([delta_e_full(psi0, g, order, r, a) for r, a in pairs])
    out["exhaustive_ring8"] = {"n": len(pairs),
                               "all_local_zero": bool(np.all(dE == 0.0)),
                               "all_full_zero": bool(np.all(full == 0.0))}
    g12 = j2_torus_graph(12)
    order12 = node_order(g12)
    idx12 = index_of(order12)
    psi12 = np.zeros(len(order12), dtype=np.complex128)
    moves = sample_relocations(g12, C0_N, seed=777)
    loc = delta_e_batch(psi12, idx12, [m[0] for m in moves], [m[1] for m in moves])
    fh = np.array([delta_e_full(psi12, g12, order12, r, a) for r, a in moves])
    out["sampled_L12"] = {"n": len(moves),
                          "all_local_zero": bool(np.all(loc == 0.0)),
                          "all_full_zero": bool(np.all(fh == 0.0)),
                          "max_abs_full": float(np.max(np.abs(fh)))}
    return out


def wave_readout(g, tag):
    L = 28
    order = node_order(g)
    c3 = j2_torus_coords(L)
    coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    periods = (float(L), float(L))
    psi0 = gaussian_packet(coords, order, (7.0, 15.0), (0.3, 0.0), 4.0,
                           periods=periods)
    assert is_normalized_ok(psi0)
    res = oneway_run([g], psi0, order, dt=WAVE_DT, steps_per_state=WAVE_STEPS)
    rows = np.asarray(res["psi"])
    coms = np.array([com(r, coords, order, periods) for r in rows])
    d = coms[-1] - coms[0]
    d -= np.round(d / L) * L
    disp = float(np.linalg.norm(d))
    ipr0 = float(np.sum(np.abs(rows[0]) ** 4))
    ipr1 = float(np.sum(np.abs(rows[-1]) ** 4))
    return {"tag": tag, "disp": disp, "pr0": float(1.0 / ipr0),
            "pr1": float(1.0 / ipr1),
            "norm_ok": bool(np.allclose(np.linalg.norm(rows, axis=1), 1.0))}


def run_wave(drift):
    log("C6 wave check: pristine vs N1-killed L28 endpoint")
    gpris = j2_torus_graph(28)
    rec = {"pristine": wave_readout(gpris, "pristine")}
    log(f"  pristine: disp={rec['pristine']['disp']:.3f} "
        f"pr {rec['pristine']['pr0']:.1f}->{rec['pristine']['pr1']:.1f}")
    edges = drift["controls"]["j2-L28"]["0"]["final_edges"]
    gkill = nx.Graph()
    gkill.add_nodes_from(range(gpris.number_of_nodes()))
    gkill.add_edges_from([(a, b) for a, b in edges])
    rec["killed"] = wave_readout(gkill, "killed")
    log(f"  killed: disp={rec['killed']['disp']:.3f} "
        f"pr {rec['killed']['pr0']:.1f}->{rec['killed']['pr1']:.1f}")
    return rec


def main():
    t0 = time.time()
    out = {"meta": {
        "campaign": "BR-1 vacuum neutrality + rigidity",
        "prereg": "BR1-PREREG (docs/DEFERRED.md, frozen pre-data)",
        "seeds": {"drift": list(DRIFT_SEEDS), "defect": list(DEFECT_SEEDS)},
        "T_drift": T_DRIFT, "snapshot_every": SNAP, "heavy_every": HEAVY_EVERY,
    }}
    out["census"] = run_census()
    out["baselines"], _ = run_baselines()
    smax = out["baselines"]["span"]["smax_J2"]
    out["drift"] = run_drift(out["baselines"])
    out["audit"] = run_audit(out["baselines"], smax)
    out["defects"] = run_defects(smax)
    out["smallfield"] = run_smallfield()
    out["c0"] = run_c0()
    out["wave"] = run_wave(out["drift"])
    out["meta"]["seconds"] = round(time.time() - t0, 1)
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "data", "br1_vacuum.json")
    with open(path, "w") as f:
        json.dump(out, f)
    log(f"wrote {path} ({out['meta']['seconds']}s total)")


if __name__ == "__main__":
    main()
