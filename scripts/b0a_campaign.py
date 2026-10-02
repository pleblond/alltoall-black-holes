"""B0a frozen scattering (UNTRACKED campaign script; verdict filed in DEFERRED.md).

Stages (gates LOCKED in P1-AMENDMENT-4/5):
  S0 reruns: 6 D5inf trajectories + elist/k4 capture 1500-2000, T-match 6/6
     vs j2_parts else apparatus-invalid STOP (no wave runs).
  S1 alpha recompute per run -> sitters (alpha<0.7 AND frozen-quality);
     <1 sitter -> STOP+file.
  S2 D1 label-matched fresh controls (same L/dyn/sweeps).
  S3 frozen full factorial: states x {+,-} x {x-app,x-flip,y-app,y-flip}.
  S4 analysis: fire rules + B0-TRACK + B1 + decision table -> b0a_results.json.
"""

import json
import math
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

from bh_graph.ballistic import (
    branch_mixing,
    branch_projectors,
    branch_weights_all,
    chiral_gamma_diag,
    com,
    evolve_fixed,
    first_crossing_time,
    gaussian_packet,
    graphs_from_saved,
    hamiltonian,
    j2_branch_parity,
    min_image_disp,
    msd_exponent_rs,
    packet_width,
    post_crossing_fit,
    region_weight,
    residence,
    unwrap_trace,
)
from bh_graph.formation import (
    formation_run,
    j2_torus_coords,
    j2_torus_graph,
    state_from_nx,
)

J2PARTS = "/home/ubuntu/cursor-tests-bc5ec649/j2_parts"
OUT = os.environ.get("B0A_PART", "/home/ubuntu/ballistic-be3e/b0a_parts")
os.makedirs(OUT, exist_ok=True)

# Smoke knobs (LOCAL MECHANICS ONLY -- beast runs bare defaults = locked protocol):
#   B0A_GRID="28:0" B0A_WIN="100:120" B0A_SAVES="100,110,120" B0A_T=2 B0A_TVERIFY=1
#   B0A_SKIP_TMATCH=1 (no j2_parts locally) B0A_FORCE_SITTERS=1 (tiny-window alpha)
_grid = os.environ.get("B0A_GRID")
_win = os.environ.get("B0A_WIN")
_saves = os.environ.get("B0A_SAVES")
SKIP_TMATCH = os.environ.get("B0A_SKIP_TMATCH") == "1"
FORCE_SITTERS = os.environ.get("B0A_FORCE_SITTERS") == "1"

GRID = (
    [(int(p.split(":")[0]), int(p.split(":")[1])) for p in _grid.split(",")]
    if _grid
    else [(28, d) for d in range(4)] + [(42, d) for d in range(2)]
)
WIN = tuple(int(x) for x in _win.split(":")) if _win else (1500, 2000)
SAVES = tuple(int(x) for x in _saves.split(",")) if _saves else (1500, 1800, 2000)
SIGMA = 4.0
KABS = 0.3
DT = 0.1
T_FROZEN = float(os.environ.get("B0A_T", "200.0"))
T_VERIFY = float(os.environ.get("B0A_TVERIFY", "10.0"))
TMAX = int(os.environ.get("B0A_TMAX", "2000"))


# ---------- S0: reruns ----------
def rerun(item):
    L, d = item
    tag = f"L{L}-d{d}"
    out = f"{OUT}/re_{tag}.json"
    if os.path.exists(out):
        return f"SKIP {tag}"
    t0 = time.time()
    st = state_from_nx(j2_torus_graph(L))
    r = formation_run(st, "d5inf", 4, d, k4_window=WIN, elist_window=WIN, t_max=TMAX)
    rec = {
        "key": [L, d], "stop": r["stop"], "sweeps": r["sweeps"],
        "t_trace": r["t_trace"],
        "k4sets": {str(k): v for k, v in r["k4sets"].items()},
        "elists": {str(s): r["elists"][s] for s in SAVES},
    }
    with open(out, "w") as f:
        f.write(json.dumps(rec))
    return f"DONE {tag}: {r['stop']} sw={r['sweeps']} {time.time()-t0:.0f}s"


print("== S0 reruns ==", flush=True)
with Pool(6) as pool:
    for msg in pool.imap_unordered(rerun, GRID):
        print(msg, flush=True)
tmatch = 0
for L, d in GRID:
    if SKIP_TMATCH:
        print(f"T-match L{L}-d{d}: SKIPPED (smoke knob)", flush=True)
        tmatch += 1
        continue
    ref = json.load(open(f"{J2PARTS}/L{L}-d{d}.json"))["t_trace"]
    got = json.load(open(f"{OUT}/re_L{L}-d{d}.json"))["t_trace"]
    ok = ref == got and len(ref) == len(got)
    tmatch += ok
    print(f"T-match L{L}-d{d}: {'OK' if ok else 'MISMATCH'}", flush=True)
if tmatch != len(GRID):
    print("APPARATUS-INVALID-STOP: T-match != 6/6", flush=True)
    sys.exit(2)

# ---------- S1: alpha + sitter selection ----------
print("== S1 sitter selection ==", flush=True)
coords_cache = {}
c3_cache = {}


def bg(L):
    if L not in coords_cache:
        c3 = j2_torus_coords(L)
        c3_cache[L] = c3
        coords_cache[L] = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    return coords_cache[L]


def centroid_trace(L, k4sets):
    coords = bg(L)
    pos = np.array([coords[v] for v in sorted(coords)], dtype=float)
    idx = {v: i for i, v in enumerate(sorted(coords))}
    out, skipped = [], 0
    for sw in range(WIN[0], WIN[1] + 1):
        m = k4sets.get(str(sw), [])
        if not m:
            skipped += 1
            continue
        ang = 2 * math.pi * pos[[idx[v] for v in m]] / L
        z = np.exp(1.0j * ang).mean(axis=0)
        out.append([(np.angle(z[a]) / (2 * math.pi) * L) % L for a in (0, 1)])
    return np.array(out), skipped


def lag_alpha(rs):
    n = len(rs)
    taus = np.unique(np.linspace(5, n // 2, 12).astype(int))
    msd = [float(np.mean(np.sum((rs[t:] - rs[:-t]) ** 2, axis=1))) for t in taus]
    slope, _ = np.polyfit(np.log(taus), np.log(np.maximum(msd, 1e-300)), 1)
    return float(slope)


def jacc(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 0.0


sitters = []
alphas = {}
for L, d in GRID:
    rec = json.load(open(f"{OUT}/re_L{L}-d{d}.json"))
    assert rec["sweeps"] >= TMAX, f"sweeps short L{L}-d{d}"
    rs_w, skipped = centroid_trace(L, rec["k4sets"])
    rs = unwrap_trace(rs_w, periods=(L, L))  # Amendment-7: unwrap before alpha
    a1 = msd_exponent_rs(rs, np.arange(len(rs), dtype=float))
    a2 = lag_alpha(rs)
    masks = [rec["k4sets"][str(s)] for s in SAVES]
    jm = min(jacc(masks[i], masks[j]) for i in range(3) for j in range(i + 1, 3))
    present = all(len(m) > 0 for m in masks)
    alphas[f"L{L}-d{d}"] = {"single": a1, "lag": a2, "skipped": skipped, "jacmin_filed": jm,
                            "masses": [len(m) for m in masks]}
    sit = (a1 < 0.7 and present and skipped / (WIN[1] - WIN[0] + 1) <= 0.05) or FORCE_SITTERS
    print(f"L{L}-d{d}: alpha_single={a1:+.2f} alpha_lag={a2:+.2f} skipped={skipped} "
          f"present={present} masses={alphas[f'L{L}-d{d}']['masses']} "
          f"-> {'SITTER' if sit else 'wanderer'}", flush=True)
    if sit:
        sitters.append((L, d))
print(f"sitters: {sitters}", flush=True)
json.dump({"sitters": sitters, "alphas": alphas, "method": "amendment-7"},
          open(f"{OUT}/b0a_selection.json", "w"), indent=1)
if len(sitters) < 1:
    print("STOP+file: no sitters", flush=True)
    sys.exit(3)

# ---------- S2: D1 controls ----------
def d1run(item):
    L, d = item
    tag = f"L{L}-d{d}"
    out = f"{OUT}/d1_{tag}.json"
    if os.path.exists(out):
        return f"SKIP D1-{tag}"
    t0 = time.time()
    st = state_from_nx(j2_torus_graph(L))
    r = formation_run(st, "d1", 4, d, elist_window=WIN, t_max=TMAX)
    rec = {"key": [L, d], "stop": r["stop"], "sweeps": r["sweeps"],
           "elists": {str(s): [list(e) for e in r["elists"][s]] for s in SAVES}}
    with open(out, "w") as f:
        f.write(json.dumps(rec))
    return f"DONE D1-{tag}: {r['stop']} {time.time()-t0:.0f}s"


print("== S2 D1 controls ==", flush=True)
with Pool(4) as pool:
    for msg in pool.imap_unordered(d1run, GRID):  # all 6 (headline-matched + appendix)
        print(msg, flush=True)

# ---------- S3: frozen runs ----------
print("== S3 frozen factorial ==", flush=True)
Q = math.pi


def mom_candidates(branch, axis):
    s = KABS
    if branch == "minus":
        return [(s, 0.0), (-s, 0.0)] if axis == "x" else [(0.0, s), (0.0, -s)]
    return [(s + Q, Q), (-s + Q, Q)] if axis == "x" else [(Q, s + Q), (Q, -s + Q)]


def circ_center(mask, coords, L, order):
    idx = {v: i for i, v in enumerate(order)}
    pos = np.array([coords[v] for v in order])
    ang = 2 * math.pi * pos[[idx[v] for v in mask]] / L
    z = np.exp(1.0j * ang).mean(axis=0)
    return np.array([(np.angle(z[a]) / (2 * math.pi) * L) % L for a in (0, 1)])


STATES = []  # (kind, L, dyn, sweep, graph, mask); ALL 6 runs (S4 filters headline)
for L, d in GRID:
    rec = json.load(open(f"{OUT}/re_L{L}-d{d}.json"))
    nodes = list(range(2 * L * L))
    graphs = graphs_from_saved({int(k): v for k, v in rec["elists"].items()}, nodes)
    for s in SAVES:
        STATES.append(("formed", L, d, s, graphs[s], rec["k4sets"][str(s)]))
for L, d in GRID:
    rec = json.load(open(f"{OUT}/d1_L{L}-d{d}.json"))
    nodes = list(range(2 * L * L))
    graphs = graphs_from_saved({int(k): v for k, v in rec["elists"].items()}, nodes)
    fref = json.load(open(f"{OUT}/re_L{L}-d{d}.json"))
    for s in SAVES:
        STATES.append(("d1", L, d, s, graphs[s], fref["k4sets"][str(s)]))
for L, d in GRID:
    g0 = j2_torus_graph(L)
    fref = json.load(open(f"{OUT}/re_L{L}-d{d}.json"))
    for s in SAVES:
        STATES.append(("bare", L, d, s, g0, fref["k4sets"][str(s)]))
print(f"states: {len(STATES)} (formed/d1/bare x 6 runs x 3 saves; S4 filters headline)", flush=True)

BR = {}  # L -> bare projectors
GAM = {}
for L in {s[1] for s in STATES}:
    g0 = j2_torus_graph(L)
    order = sorted(g0.nodes())
    H0 = hamiltonian(g0, order=order)
    BR[L] = branch_projectors(H0.toarray())
    c3 = j2_torus_coords(L)
    GAM[L] = chiral_gamma_diag(j2_branch_parity(c3), order)
    print(f"bare L{L}: n_zero={BR[L]['n_zero']} Emax={BR[L]['evals'].max():.2f}", flush=True)


def prep_for(state_idx):
    kind, L, d, s, g, mask = STATES[state_idx]
    coords = bg(L)
    order = sorted(g.nodes())
    cc = circ_center(mask, coords, L, order)
    pos = np.array([coords[v] for v in order])
    dist = np.linalg.norm(min_image_disp(pos, cc, (L, L)), axis=1)
    return order[int(np.argmax(dist))], cc


def run_cell(args):
    si, branch, axis, flip = args
    kind, L, d, s, g, mask = STATES[si]
    coords = bg(L)
    order = sorted(g.nodes())
    n = len(order)
    idx = {v: i for i, v in enumerate(order)}
    cc = circ_center(mask, coords, L, order)
    pos = np.array([coords[v] for v in order])
    dist = np.linalg.norm(min_image_disp(pos, cc, (L, L)), axis=1)
    prep = order[int(np.argmax(dist))]
    r0 = coords[prep]
    H = hamiltonian(g, order=order)
    br = BR[L]
    P = br["P_plus"] if branch == "plus" else br["P_minus"]
    # approach-sign verify on THIS graph (10 units, both signs)
    cands = mom_candidates(branch, axis)
    dists = []
    for k in cands:
        q0 = gaussian_packet(coords, order, r0, k, SIGMA, periods=(L, L))
        rec = evolve_fixed(q0, H, DT, int(round(T_VERIFY / DT)))
        rend = com(rec["psi"][-1], coords, order, periods=(L, L))
        dists.append(float(np.linalg.norm(min_image_disp(rend, cc, (L, L)))))
    init_dist = float(dist[idx[prep]])
    approach_ok = min(dists) < init_dist
    k = cands[int(np.argmin(dists))] if not flip else cands[int(np.argmax(dists))]
    psi0 = gaussian_packet(coords, order, r0, k, SIGMA, periods=(L, L))
    w_init = branch_weights_all(psi0, br)
    rec = evolve_fixed(psi0, H, DT, int(round(T_FROZEN / DT)))
    psi = rec["psi"]
    ts = np.arange(psi.shape[0]) * DT
    rs_w = np.array([com(p, coords, order, periods=(L, L)) for p in psi])
    rs = unwrap_trace(rs_w, periods=(L, L))
    core_idx = [idx[v] for v in mask]
    cw = np.array([region_weight(p, core_idx) for p in psi])
    wall = [branch_weights_all(p, br) for p in psi]
    wb = np.array([[w["w_plus"], w["w_zero"], w["w_minus"]] for w in wall])
    acc = float(np.abs(wb.sum(axis=1) - 1.0).max())
    R = residence(cw, ts)
    rcore = math.sqrt(len(mask))
    tcross = first_crossing_time(rs_w, ts, cc, rcore, periods=(L, L))
    wkey = {"plus": 0, "minus": 2}[branch]
    mix = branch_mixing(wb[:, wkey])
    dW = {b: float(wb[-1, j] - wb[0, j]) for b, j in (("plus", 0), ("zero", 1), ("minus", 2))}
    maxdev = {b: float(np.abs(wb[:, j] - wb[0, j]).max()) for b, j in (("plus", 0), ("zero", 1), ("minus", 2))}
    wbar = float(cw[int(len(cw) * 0.8):].mean())
    # incident half at T (prep side of core bisector)
    side = np.sign(min_image_disp(pos, cc, (L, L)) @ min_image_disp(np.array(r0), cc, (L, L)))
    inc = region_weight(psi[-1], np.where(side > 0)[0]) if np.any(side > 0) else float("nan")
    out = {"w_init": w_init, "R": R, "tcross": tcross, "mix": mix, "dW": dW, "maxdev": maxdev,
           "wbar": wbar, "wdeloc": len(mask) / n, "inc": inc, "acc": acc,
           "normdev": float(np.abs(rec["norms"] - 1.0).max()),
           "k": list(k), "prep": prep, "verify_dists": dists, "approach_ok": bool(approach_ok)}
    if tcross is not None and int(np.searchsorted(ts, min(tcross + 10.0, ts[-1]))) - int(
        np.searchsorted(ts, tcross)
    ) >= 3:
        f = post_crossing_fit(rs, ts, tcross, window=10.0)
        out.update({"vout": [float(x) for x in f["v"]], "vout_r2": f["r2"], "vout_trunc": f["truncated"]})
        i0 = int(np.searchsorted(ts, tcross))
        i1 = int(np.searchsorted(ts, min(tcross + 10.0, ts[-1])))
        out["width_growth"] = packet_width(psi[i1], coords, order, periods=(L, L)) - packet_width(
            psi[i0], coords, order, periods=(L, L))
    else:
        out.update({"vout": None, "vout_r2": None, "vout_trunc": None, "width_growth": None})
    return (si, branch, axis, flip, out)


CELLS = [(si, b, a, f) for si in range(len(STATES)) for b in ("plus", "minus")
         for a in ("x", "y") for f in (False, True)]
NW = int(os.environ.get("B0A_WORKERS", "16"))
CKPT = f"{OUT}/b0a_cells.jsonl"
SIG = [(s[0], s[1], s[2], s[3]) for s in STATES]
done = set()
if os.path.exists(CKPT):
    with open(CKPT) as f:
        first = f.readline()
        meta = json.loads(first) if first else {}
        if meta.get("states_sig") != [list(x) for x in SIG]:
            print("CHECKPOINT-STATE-MISMATCH: refusing to mix pools; remove jsonl to restart", flush=True)
            sys.exit(4)
        for line in f:
            r = json.loads(line)
            done.add((r["si"], r["branch"], r["axis"], r["flip"]))
TODO = [c for c in CELLS if c not in done]
print(f"cells: {len(CELLS)} ({len(done)} resumed) workers={NW}", flush=True)
t0 = time.time()
fh = open(CKPT, "a" if done else "w")
if not done:
    fh.write(json.dumps({"states_sig": SIG}) + "\n")
    fh.flush()
with Pool(NW) as pool:
    for i, r in enumerate(pool.imap_unordered(run_cell, TODO)):
        rec = {"si": r[0], "branch": r[1], "axis": r[2], "flip": r[3], **r[4]}
        fh.write(json.dumps(rec) + "\n")
        fh.flush()
        if (i + 1) % 10 == 0:
            print(f"  {len(done)+i+1}/{len(CELLS)} {time.time()-t0:.0f}s", flush=True)
fh.close()
print(f"frozen done {time.time()-t0:.0f}s", flush=True)

allcells = []
with open(CKPT) as f:
    f.readline()
    for line in f:
        allcells.append(json.loads(line))
with open(f"{OUT}/b0a_cells.json", "w") as f:
    json.dump({"cells": allcells,
               "states": [{"si": i, "kind": s[0], "L": s[1], "dyn": s[2], "sweep": s[3],
                           "mass": len(s[5])} for i, s in enumerate(STATES)],
               "alphas": alphas}, f)
print(f"cells persisted ({len(allcells)})", flush=True)
