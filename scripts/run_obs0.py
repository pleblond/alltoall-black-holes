"""OBS-0 campaign runner (frozen per OBS0-PREREG; runs on beast, NOT locally).

Units (one process each, parallelized via xargs):
  eigen  build graph + intrinsic D + cache lsym/H eigensystems (npz)
  origin one origin: BFS dist/targets, d_H, d_s, tau_D/tau_W (wrap-safe)
  dims   C1/extension dims-only unit (16 origins, no taus)
  c5     banked-wave regression (ring-400 + torus-30 + J2-28 branch pair)

All randomness/frozen constants come from bh_graph.obs0 (prereg values).
"""
import argparse
import json
import math
import os
import random
import sys

import networkx as nx
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from bh_graph import obs0  # noqa: E402
from bh_graph.formation import j2_torus_coords, j2_torus_graph  # noqa: E402
from bh_graph.graphs import (build_random_regular,  # noqa: E402
                             build_torus_grid)


def tag_graph(tag: str):
    """Build the campaign graph for a tag (deterministic)."""
    parts = tag.split("-")
    if parts[0] == "j2":
        return j2_torus_graph(int(parts[1][1:])), {"si": 0}
    if parts[0] == "sq":
        return build_torus_grid(int(parts[1][1:])), {"si": 1}
    if parts[0] == "exp":
        n = int(parts[1][1:])
        seed = int(parts[2][1:])
        return build_random_regular(n, 8, seed=seed), {"si": 2}
    if parts[0] == "pert":
        L = int(parts[1][1:])
        seed = int(parts[2][1:])
        g = j2_torus_graph(L)
        rng = random.Random(seed)
        edges = list(g.edges())
        g.remove_edges_from(rng.sample(edges, int(0.05 * len(edges))))
        return g, {"si": 0}
    raise ValueError(f"unknown tag {tag}")


def tag_L(tag: str) -> int:  # noqa: N802
    parts = tag.split("-")
    if parts[0] in ("j2", "sq", "pert"):
        return int(parts[1][1:])
    return int(parts[1][1:])


def jsonable(o):
    """Recursively convert numpy scalars/arrays to JSON-native types."""
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, np.ndarray):
        return [jsonable(v) for v in o.tolist()]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return o


def cmd_eigen(args):
    g, meta = tag_graph(args.tag)
    L = tag_L(args.tag)
    order = sorted(g.nodes())
    D = obs0.intrinsic_diameter(g, order[0])
    N = len(order)
    wl, Vl, _ = obs0.lsym_system(g, order)
    Ew, Vw, _ = obs0.hamiltonian_system(g, order)
    os.makedirs(args.outdir, exist_ok=True)
    obs0.save_system(os.path.join(args.outdir, f"eigen_lsym_{args.tag}.npz"),
                     wl, Vl, order)
    obs0.save_system(os.path.join(args.outdir, f"eigen_ham_{args.tag}.npz"),
                     Ew, Vw, order)
    degs = [g.degree(v) for v in order]
    info = {"tag": args.tag, "L": L, "N": N, "D": D, "si": meta["si"],
            "connected": bool(nx.is_connected(g)),
            "deg_min": min(degs), "deg_max": max(degs),
            "deg_mean": sum(degs) / len(degs),
            "heat_ds": obs0.heat_trace_ds(wl),
            "weyl": obs0.weyl_ds(np.sort(wl)[:min(obs0.WEYL_K, N - 1)])}
    with open(os.path.join(args.outdir, f"info_{args.tag}.json"), "w") as f:
        json.dump(jsonable(info), f)
    # degrees needed for exact Lrw on non-regular graphs
    np.save(os.path.join(args.outdir, f"deg_{args.tag}.npy"), np.array(degs))
    print(f"eigen {args.tag}: N={N} D={D} heat_ds={info['heat_ds']['d']:.4f} "
          f"weyl={info['weyl']['d']:.4f} conn={info['connected']}", flush=True)


def cmd_origin(args):
    wl, Vl, order = obs0.load_system(
        os.path.join(args.outdir, f"eigen_lsym_{args.tag}.npz"))
    Ew, Vw, order2 = obs0.load_system(
        os.path.join(args.outdir, f"eigen_ham_{args.tag}.npz"))
    assert order == order2
    with open(os.path.join(args.outdir, f"info_{args.tag}.json")) as f:
        info = json.load(f)
    D, L, si = info["D"], info["L"], info["si"]
    deg = None
    if args.tag.startswith("pert"):
        deg = np.load(os.path.join(args.outdir, f"deg_{args.tag}.npy"))
    origins = obs0.sample_origins(len(order), si, L)
    o_pos = int(args.oi)
    origin = order[origins[o_pos]]
    idx = {v: i for i, v in enumerate(order)}
    # BFS distances need the graph: rebuild (cheap) or from edges? rebuild.
    g, _ = tag_graph(args.tag)
    dist = dict(nx.single_source_shortest_path_length(g, origin))
    half = obs0.wrap_limit(D)
    safe = [v for v, r in dist.items() if 1 <= r < half]
    tj = [idx[v] for v in safe]
    o_idx = idx[origin]
    tD = obs0.arrival_times_diff(wl, Vl, o_idx, tj, D, deg=deg)
    tW = obs0.arrival_times_wave(Ew, Vw, o_idx, tj, D)
    taus = {str(v): {"R": dist[v],
                     "tD": tD[idx[v]],
                     "tW": tW[idx[v]]} for v in safe}
    rec = {"tag": args.tag, "oi": o_pos, "origin": origin, "D": D,
           "n_safe": len(safe),
           "hausdorff": obs0.hausdorff_dim(g, origin),
           "ds_origin": obs0.origin_return_ds(wl, Vl, o_idx),
           "targets": {str(k): v for k, v in
                       obs0.sample_targets(dist, D,
                                           seed=obs0.TARGET_SEED_BASE + o_pos).items()},
           "taus": taus}
    fn = os.path.join(args.outdir, f"origin_{args.tag}_o{o_pos}.json")
    with open(fn, "w") as f:
        json.dump(jsonable(rec), f)
    missD = sum(1 for v in safe if tD[idx[v]] is None)
    missW = sum(1 for v in safe if tW[idx[v]] is None)
    print(f"origin {args.tag} o{o_pos}: safe={len(safe)} "
          f"dH={rec['hausdorff']['d']:.4f} ds={rec['ds_origin']['d']:.4f} "
          f"missD={missD} missW={missW}", flush=True)


def cmd_dims(args):
    # C1 / extension dims-only unit (no taus): 16 origins d_H + d_s + Weyl.
    wl, Vl, order = obs0.load_system(
        os.path.join(args.outdir, f"eigen_lsym_{args.tag}.npz"))
    with open(os.path.join(args.outdir, f"info_{args.tag}.json")) as f:
        info = json.load(f)
    D, L, si = info["D"], info["L"], info["si"]
    g, _ = tag_graph(args.tag)
    idx = {v: i for i, v in enumerate(order)}
    origins = obs0.sample_origins(len(order), si, L)
    out = []
    for o_pos, o_samp in enumerate(origins):
        origin = order[o_samp]
        out.append({"oi": o_pos, "origin": origin,
                    "hausdorff": obs0.hausdorff_dim(g, origin),
                    "ds_origin": obs0.origin_return_ds(wl, Vl, idx[origin])})
    rec = {"tag": args.tag, "D": D, "heat_ds": obs0.heat_trace_ds(wl),
           "weyl": info["weyl"], "origins": out}
    with open(os.path.join(args.outdir, f"dims_{args.tag}.json"), "w") as f:
        json.dump(jsonable(rec), f)
    print(f"dims {args.tag}: D={D} heat_ds={rec['heat_ds']['d']:.4f}", flush=True)


def _c5_ring():
    n = 400
    g = nx.cycle_graph(n)
    order = sorted(g.nodes())
    coords = {v: (float(v),) for v in order}
    psi0 = obs0.c5_gaussian_packet(coords, order, (100.0,), (0.5,), 20.0,
                                   periods=(n,))
    E, V, _ = obs0.hamiltonian_system(g, order)
    rows = obs0.c5_evolve_packet(E, V, psi0, 0.2, 600)
    ts = np.arange(601) * 0.2
    rs = obs0.c5_unwrap_trace(
        np.array([obs0.c5_com(p, coords, order, periods=(n,)) for p in rows]),
        periods=(n,))
    v = obs0.c5_fit_speed(rs, ts)["speed"]
    analytic = 2 * math.sin(0.5)
    return {"v": v, "analytic": analytic, "relerr": abs(v - analytic) / analytic,
            "pass": bool(abs(v - analytic) / analytic < 0.01)}


def _c5_torus():
    L = 30
    g = build_torus_grid(L)
    order = sorted(g.nodes())
    coords = {x * L + y: (float(x), float(y))
              for x in range(L) for y in range(L)}
    psi0 = obs0.c5_gaussian_packet(coords, order, (7.0, 15.0), (0.5, 0.0), 3.0,
                                   periods=(L, L))
    E, V, _ = obs0.hamiltonian_system(g, order)
    rows = obs0.c5_evolve_packet(E, V, psi0, 0.2, 125)
    ts = np.arange(126) * 0.2
    rs = obs0.c5_unwrap_trace(
        np.array([obs0.c5_com(p, coords, order, periods=(L, L)) for p in rows]),
        periods=(L, L))
    v = obs0.c5_fit_speed(rs, ts)["speed"]
    ref = 0.9658
    return {"v": v, "ref": ref, "relerr": abs(v - ref) / ref,
            "pass": bool(abs(v - ref) / ref < 0.05)}


def _c5_j2():
    L = 28
    g = j2_torus_graph(L)
    order = sorted(g.nodes())
    c3 = j2_torus_coords(L)
    coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    H = -nx.to_numpy_array(g, nodelist=order, dtype=float)
    br = obs0.c5_branch_projectors(H)
    E, V, _ = obs0.hamiltonian_system(g, order)
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


def cmd_c5(args):
    os.makedirs(args.outdir, exist_ok=True)
    rec = {"ring": _c5_ring(), "torus": _c5_torus(), "j2": _c5_j2()}
    rec["pass"] = bool(rec["ring"]["pass"] and rec["torus"]["pass"]
                       and rec["j2"]["pass"])
    with open(os.path.join(args.outdir, "c5.json"), "w") as f:
        json.dump(jsonable(rec), f)
    print(f"c5: ring relerr={rec['ring']['relerr']:.4f} "
          f"torus relerr={rec['torus']['relerr']:.4f} "
          f"j2 relerr={[round(r, 4) for r in rec['j2']['relerr']]} "
          f"PASS={rec['pass']}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="unit", required=True)
    p = sub.add_parser("eigen")
    p.add_argument("--tag", required=True)
    p.add_argument("--outdir", required=True)
    p = sub.add_parser("origin")
    p.add_argument("--tag", required=True)
    p.add_argument("--oi", type=int, required=True)
    p.add_argument("--outdir", required=True)
    p = sub.add_parser("dims")
    p.add_argument("--tag", required=True)
    p.add_argument("--outdir", required=True)
    p = sub.add_parser("c5")
    p.add_argument("--outdir", required=True)
    args = ap.parse_args()
    {"eigen": cmd_eigen, "origin": cmd_origin, "dims": cmd_dims,
     "c5": cmd_c5}[args.unit](args)


if __name__ == "__main__":
    main()
