"""OBS-0R campaign runner (FROZEN per OBS0R-PREREG; runs on beast, NOT locally).

Units (one process each, parallelized via xargs):
  eigen    build graph + intrinsic D + cache lsym/H eigensystems (npz)
           (identical to OBS-0; reuses run_obs0.cmd_eigen)
  origin128 one L128 origin: frozen 75 G/D/W targets + POT-target union +
           J2 sheet-matched extras; taus ONLY for this set (D^6 scaling
           makes OBS-0 all-safe infeasible; values bitwise-identical on
           overlap -- validated pre-campaign by `validate`)
  validate targets-only equivalence on a banked tag (L64): recompute +
           diff vs banked taus/dims; PASS iff maxdiff < 1e-9 and
           None-patterns identical (else STOP: fall back to all-safe)
  pot      one POT origin: static solve + POT targets + sheet-node phi +
           shell profiles (no eigen needed; sparse solves)
  c3       POT regression: J2-L28 source-0 static field vs banked POT-1
  c4       L128 wave regression: J2 branch-pair + square packet velocities
           vs banked P1/POT calibration (projectors from cached eigen)
  dims     C1-extension dims-only unit (reuses run_obs0.cmd_dims)

All randomness/frozen constants come from bh_graph.obs0 / obs0r.
"""
import argparse
import json
import math
import os
import sys
from types import SimpleNamespace

import networkx as nx
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))
from bh_graph import obs0, obs0r  # noqa: E402
from bh_graph.formation import j2_torus_coords  # noqa: E402
import run_obs0  # noqa: E402

# Frozen OBS0R-PREREG run parameters.
SHEET_RADII_128 = (1, 2, 3, 8, 9, 10, 11, 12)
VALIDATE_TOL = 1e-9
C3_XI_BANKED = 1.0 / 0.5272  # POT-1 filed kappa -> true xi at L28
C3_XI_RTOL = 0.10


def cmd_eigen(args):
    run_obs0.cmd_eigen(args)


def cmd_dims(args):
    run_obs0.cmd_dims(args)


def _tau_subset(tag, outdir, oi, nodes):
    """Frozen tau computation for an explicit node set (origin128 core)."""
    wl, Vl, order = obs0.load_system(
        os.path.join(outdir, f"eigen_lsym_{tag}.npz"))
    Ew, Vw, order2 = obs0.load_system(
        os.path.join(outdir, f"eigen_ham_{tag}.npz"))
    assert order == order2
    with open(os.path.join(outdir, f"info_{tag}.json")) as f:
        info = json.load(f)
    D, L, si = info["D"], info["L"], info["si"]
    g, _ = run_obs0.tag_graph(tag)
    idx = {v: i for i, v in enumerate(order)}
    origins = obs0.sample_origins(len(order), si, L)
    origin = order[origins[int(oi)]]
    dist = dict(nx.single_source_shortest_path_length(g, origin))
    tj = [idx[v] for v in nodes]
    o_idx = idx[origin]
    tD = obs0.arrival_times_diff(wl, Vl, o_idx, tj, D)
    tW = obs0.arrival_times_wave(Ew, Vw, o_idx, tj, D)
    ball1 = [o_idx] + [idx[w] for w in g.neighbors(origin)]
    return {"g": g, "order": order, "D": D, "L": L, "si": si,
            "origin": origin, "o_idx": o_idx, "dist": dist,
            "tD": tD, "tW": tW, "idx": idx,
            "hausdorff": obs0.hausdorff_dim(g, origin),
            "ds_origin": obs0.origin_return_ds(wl, Vl, o_idx),
            "dw_return": obs0.wave_return_dw(Ew, Vw, o_idx, ball1)}


def cmd_origin128(args):
    tag, oi, outdir = args.tag, int(args.oi), args.outdir
    g, _ = run_obs0.tag_graph(tag)
    with open(os.path.join(outdir, f"info_{tag}.json")) as f:
        info = json.load(f)
    D, L, si = info["D"], info["L"], info["si"]
    order = sorted(g.nodes())
    origins = obs0.sample_origins(len(order), si, L)
    origin = order[origins[oi]]
    dist = dict(nx.single_source_shortest_path_length(g, origin))
    gdwt = obs0.sample_targets(dist, D, seed=obs0.TARGET_SEED_BASE + oi)
    pott = obs0r.pot_targets_by_shell(dist, seed=obs0r.P_TARGET_SEED_BASE + oi)
    nodes = sorted(set(gdwt) | set(pott))
    sheet_extra = {}
    if tag.startswith("j2"):
        c3 = j2_torus_coords(L)
        sm = obs0r.sheet_matched(dist, c3, origin, SHEET_RADII_128,
                                 per_slot=obs0r.P_SHEET_N)
        for r, slots in sm.items():
            for slot in ("same", "cross"):
                for v in slots[slot]:
                    sheet_extra[v] = {"R": r, "slot": slot}
        nodes = sorted(set(nodes) | set(sheet_extra))
    r = _tau_subset(tag, outdir, oi, nodes)
    taus = {str(v): {"R": r["dist"][v], "tD": r["tD"][r["idx"][v]],
                     "tW": r["tW"][r["idx"][v]]} for v in nodes}
    rec = {"tag": tag, "oi": oi, "origin": origin, "D": D,
           "mode": "targets-only-union", "n_nodes": len(nodes),
           "hausdorff": r["hausdorff"], "ds_origin": r["ds_origin"],
           "dw_return": r["dw_return"],
           "targets": {str(k): v for k, v in gdwt.items()},
           "taus": taus,
           "sheet_extra": {str(k): v for k, v in sheet_extra.items()}}
    with open(os.path.join(outdir, f"origin_{tag}_o{oi}.json"), "w") as f:
        json.dump(run_obs0.jsonable(rec), f)
    missD = sum(1 for v in nodes if r["tD"][r["idx"][v]] is None)
    missW = sum(1 for v in nodes if r["tW"][r["idx"][v]] is None)
    print(f"origin128 {tag} o{oi}: nodes={len(nodes)} "
          f"dH={r['hausdorff']['d']:.4f} ds={r['ds_origin']['d']:.4f} "
          f"dW={r['dw_return']['d']:.4f} missD={missD} missW={missW}",
          flush=True)


def cmd_validate(args):
    tag, datadir = args.tag, args.datadir
    outdir = getattr(args, "outdir", None) or datadir
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(datadir, f"info_{tag}.json")) as f:
        info = json.load(f)
    D = info["D"]
    worst = 0.0
    pat_bad = 0
    rep = {"tag": tag, "tol": VALIDATE_TOL, "origins": []}
    for oi in range(16):
        with open(os.path.join(datadir, f"origin_{tag}_o{oi}.json")) as f:
            banked = json.load(f)
        nodes = [int(k) for k in banked["targets"]]
        r = _tau_subset(tag, datadir, oi, nodes)
        md = 0.0
        for v in nodes:
            for nm, new in (("tD", r["tD"][r["idx"][v]]),
                            ("tW", r["tW"][r["idx"][v]])):
                old = banked["taus"][str(v)][nm]
                if (old is None) != (new is None):
                    pat_bad += 1
                elif old is not None:
                    md = max(md, abs(float(new) - float(old)))
        for k in ("hausdorff", "ds_origin", "dw_return"):
            md = max(md, abs(float(r[k]["d"]) - float(banked[k]["d"])))
        rep["origins"].append({"oi": oi, "maxdiff": md})
        worst = max(worst, md)
    rep["worst"] = worst
    rep["none_pattern_mismatches"] = pat_bad
    rep["pass"] = bool(worst < VALIDATE_TOL and pat_bad == 0)
    with open(os.path.join(outdir, f"validation_{tag}.json"), "w") as f:
        json.dump(rep, f)
    print(f"validate {tag}: worst={worst:.3e} pat_bad={pat_bad} "
          f"PASS={rep['pass']}", flush=True)
    if not rep["pass"]:
        raise SystemExit("VALIDATION FAILED: fall back to all-safe (prereg)")


def cmd_pot(args):
    tag, oi, outdir = args.tag, int(args.oi), args.outdir
    os.makedirs(outdir, exist_ok=True)
    g, meta = run_obs0.tag_graph(tag)
    L = run_obs0.tag_L(tag)
    si = meta["si"]
    order = sorted(g.nodes())
    origins = obs0.sample_origins(len(order), si, L)
    origin = order[origins[oi]]
    dist = dict(nx.single_source_shortest_path_length(g, origin))
    D = max(dist.values())
    z = max(dict(g.degree()).values())
    omega = obs0r.omega_below_edge(z)
    F = obs0r.static_field_phi(g, order, origin, omega)
    idx = {v: i for i, v in enumerate(order)}
    phi = F["phi"]
    tg = obs0r.pot_targets_by_shell(dist, seed=obs0r.P_TARGET_SEED_BASE + oi)
    sheet_nodes = sorted(v for v, d in dist.items()
                         if d in (1, 2, 3) + tuple(obs0r.P_SHEET_MESO))
    prof_mean = obs0r.shell_profile(phi, order, dist, min(D, 12), stat="mean")
    prof_med = obs0r.shell_profile(phi, order, dist, min(D, 12), stat="median")
    rec = {"tag": tag, "oi": oi, "origin": origin, "D": int(D), "L": L,
           "si": si, "z": int(z), "omega": omega,
           "max_imag": F["max_imag"], "residual": F["residual"],
           "gap_ok": F["gap_ok"], "positive": bool((phi > 0).all()),
           "targets": {str(v): {"R": r, "phi": float(phi[idx[v]])}
                       for v, r in tg.items()},
           "sheet_phi": {str(v): {"R": dist[v], "phi": float(phi[idx[v]])}
                         for v in sheet_nodes},
           "shells_mean": {str(r): v for r, v in prof_mean.items()},
           "shells_median": {str(r): v for r, v in prof_med.items()}}
    with open(os.path.join(outdir, f"pot_{tag}_o{oi}.json"), "w") as f:
        json.dump(run_obs0.jsonable(rec), f)
    print(f"pot {tag} o{oi}: ntarg={len(tg)} resid={F['residual']:.1e} "
          f"pos={rec['positive']}", flush=True)


def cmd_c3(args):
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    tag = "j2-L28"
    g, _ = run_obs0.tag_graph(tag)
    order = sorted(g.nodes())
    omega = obs0r.omega_below_edge(8)
    F = obs0r.static_field_phi(g, order, 0, omega)
    dist = dict(nx.single_source_shortest_path_length(g, 0))
    prof = obs0r.shell_profile(F["phi"], order, dist, 8, stat="mean")
    fit = obs0r.fit_pure_exp([2, 3, 4, 5],
                             [prof[r]["v"] for r in (2, 3, 4, 5)])
    rng = max([r for r in range(9) if prof[r]["v"] > 0.05])
    checks = {
        "real": bool(F["max_imag"] < 1e-9),
        "positive": bool((F["phi"] > 0).all()),
        "xi": bool(fit["ok"] and abs(fit["xi"] - C3_XI_BANKED) / C3_XI_BANKED
                   < C3_XI_RTOL),
        "range": bool(abs(rng - 3) <= 1),
        "residual": bool(F["residual"] < 1e-9),
        "gap": bool(F["gap_ok"]),
    }
    rec = {"pass": bool(all(checks.values())), "checks": checks,
           "xi": fit["xi"], "xi_banked": C3_XI_BANKED, "range": rng,
           "residual": F["residual"], "max_imag": F["max_imag"],
           "omega": omega}
    with open(os.path.join(outdir, "c3.json"), "w") as f:
        json.dump(run_obs0.jsonable(rec), f)
    print(f"c3: xi={fit['xi']:.4f} (banked {C3_XI_BANKED:.4f}) range={rng} "
          f"PASS={rec['pass']}", flush=True)


def _c4_j2(datadir):
    L = 128
    tag = "j2-L128"
    E, V, order = obs0.load_system(
        os.path.join(datadir, f"eigen_ham_{tag}.npz"))
    g, _ = run_obs0.tag_graph(tag)
    assert sorted(g.nodes()) == order
    c3 = j2_torus_coords(L)
    coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    br = obs0r.branch_projectors_from_eigen(E, V)
    specs = [((0.3, 0.0), "P_minus"), ((0.3 + math.pi, math.pi), "P_plus"),
             ((-0.3, 0.0), "P_minus"), ((-0.3 - math.pi, -math.pi), "P_plus")]
    speeds = []
    for k, branch in specs:
        psi = obs0.c5_gaussian_packet(coords, order, (7.0, 14.0), k, 4.0,
                                      periods=(L, L))
        pure, retained = obs0.c5_branch_purify(psi, br[branch])
        rows = obs0.c5_evolve_packet(E, V, pure, 0.1, 100)
        ts = np.arange(101) * 0.1
        rs = obs0.c5_unwrap_trace(
            np.array([obs0.c5_com(p, coords, order, periods=(L, L))
                      for p in rows]), periods=(L, L))
        speeds.append({"k": k, "branch": branch, "retained": retained,
                       "speed": obs0.c5_fit_speed(rs, ts)["speed"]})
    got = sorted(s["speed"] for s in speeds)
    ref = sorted([1.2039, 1.2110, 1.2039, 1.2110])
    rel = [abs(a - b) / b for a, b in zip(got, ref)]
    return {"speeds": speeds, "relerr": rel,
            "pass": bool(all(r < 0.10 for r in rel))}


def _c4_sq(datadir):
    L = 128
    tag = "sq-L128"
    E, V, order = obs0.load_system(
        os.path.join(datadir, f"eigen_ham_{tag}.npz"))
    coords = {x * L + y: (float(x), float(y))
              for x in range(L) for y in range(L)}
    assert sorted(coords) == order
    psi0 = obs0.c5_gaussian_packet(coords, order, (7.0, 15.0), (0.5, 0.0),
                                   3.0, periods=(L, L))
    rows = obs0.c5_evolve_packet(E, V, psi0, 0.2, 125)
    ts = np.arange(126) * 0.2
    rs = obs0.c5_unwrap_trace(
        np.array([obs0.c5_com(p, coords, order, periods=(L, L)) for p in rows]),
        periods=(L, L))
    v = obs0.c5_fit_speed(rs, ts)["speed"]
    ref = 0.9658
    return {"v": v, "ref": ref, "relerr": abs(v - ref) / ref,
            "pass": bool(abs(v - ref) / ref < 0.05)}


def cmd_c4(args):
    os.makedirs(args.outdir, exist_ok=True)
    rec = {"j2": _c4_j2(args.datadir), "sq": _c4_sq(args.datadir)}
    rec["pass"] = bool(rec["j2"]["pass"] and rec["sq"]["pass"])
    with open(os.path.join(args.outdir, "c4.json"), "w") as f:
        json.dump(run_obs0.jsonable(rec), f)
    print(f"c4: j2 relerr={[round(r, 4) for r in rec['j2']['relerr']]} "
          f"sq relerr={rec['sq']['relerr']:.4f} PASS={rec['pass']}",
          flush=True)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="unit", required=True)
    p = sub.add_parser("eigen")
    p.add_argument("--tag", required=True)
    p.add_argument("--outdir", required=True)
    p = sub.add_parser("dims")
    p.add_argument("--tag", required=True)
    p.add_argument("--outdir", required=True)
    p = sub.add_parser("origin128")
    p.add_argument("--tag", required=True)
    p.add_argument("--oi", type=int, required=True)
    p.add_argument("--outdir", required=True)
    p = sub.add_parser("validate")
    p.add_argument("--tag", required=True)
    p.add_argument("--datadir", required=True)
    p.add_argument("--outdir", default=None)
    p = sub.add_parser("pot")
    p.add_argument("--tag", required=True)
    p.add_argument("--oi", type=int, required=True)
    p.add_argument("--outdir", required=True)
    p = sub.add_parser("c3")
    p.add_argument("--outdir", required=True)
    p = sub.add_parser("c4")
    p.add_argument("--datadir", required=True)
    p.add_argument("--outdir", required=True)
    args = ap.parse_args()
    {"eigen": cmd_eigen, "dims": cmd_dims, "origin128": cmd_origin128,
     "validate": cmd_validate, "pot": cmd_pot, "c3": cmd_c3,
     "c4": cmd_c4}[args.unit](args)


if __name__ == "__main__":
    main()
