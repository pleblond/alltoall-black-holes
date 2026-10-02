"""FIELD-0 collision battery (UNTRACKED runner; verdicts filed in DEFERRED.md).

Preregistered grid (FIELD0-PREREG, docs/DEFERRED.md):
  Geometry (D): 7 names x headline params (J2 L28, sigma4, k0.3, T20/dt0.1).
  Phase (E): headon x 8 dphi. Amplitude (F): headon x 7 ratios.
  Width (G): headon x 5 sigma. Impact (H): nearmiss x 6 b.
  Substrate (S): headon/coprop/overlap x j2/square/ring/quotient.
  Sector (P): sym/sym, sym/anti, anti/anti (J2 headon).
  Static (Q): phi_static+packet pass-through + far control (J2).
  Standing (N): overlap + overlap-pi (J2). Coherence (O): scramble1/2/both.
  Binding (M): overlap-slow + headon-slow (k=0.1).
Total 56 cells (1 overlap deduped in analysis, not in runs).

Each cell evolves psi1_iso, psi2_iso, psi12_joint under frozen H=-JA and
files eps_psi, rho/B/J/E decomps, PRE/OVERLAP/POST windows, outgoing
COM/v/width/coherence/momentum, naive peak/false accel, residence/beat,
witness I, and atlas candidates. No fitting, no steering, no selection.
"""

import json
import math
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

from bh_graph import field0
from bh_graph.ballistic import min_image_disp
from bh_graph.driven import bilinears, edge_arrays
from bh_graph.potential import scramble_phases

OUT = os.environ.get("FIELD0_PART", "/tmp/field0_parts")
os.makedirs(OUT, exist_ok=True)

L_J2 = int(os.environ.get("FIELD0_L", "28"))
T_END = float(os.environ.get("FIELD0_T", "20.0"))
DT = float(os.environ.get("FIELD0_DT", "0.1"))
N_STEPS = int(round(T_END / DT))
SIGMA0 = 4.0
K0 = 0.3


def ring_geom_1d(name, n, kabs=K0, sigma=SIGMA0):
    """1D ring geometries (headon/coprop/overlap/overtaking only)."""
    if name == "headon":
        return {"name": name, "r1": (n / 4.0,), "k1": (kabs,),
                "r2": (3.0 * n / 4.0,), "k2": (-kabs,), "sigma": sigma}
    if name == "coprop":
        return {"name": name, "r1": (n / 4.0,), "k1": (kabs,),
                "r2": (3.0 * n / 4.0,), "k2": (kabs,), "sigma": sigma}
    if name == "overlap":
        return {"name": name, "r1": (n / 2.0,), "k1": (kabs,),
                "r2": (n / 2.0,), "k2": (-kabs,), "sigma": sigma}
    if name == "overtaking":
        return {"name": name, "r1": (n / 4.0,), "k1": (kabs,),
                "r2": (n / 4.0 - 8.0,), "k2": (2.0 * kabs,), "sigma": sigma}
    raise ValueError(f"ring has no geometry {name}")


def build_cells():
    """Preregistered cell list (deterministic, frozen order)."""
    cells = []
    cid = 0

    def add(kind, sub_kind, sub_L, geom, p1_extra=None, p2_extra=None,
            prep="packet", note=""):
        nonlocal cid
        cells.append({"cid": cid, "kind": kind, "sub_kind": sub_kind,
                      "sub_L": sub_L, "geom": geom,
                      "p1_extra": p1_extra or {}, "p2_extra": p2_extra or {},
                      "prep": prep, "note": note})
        cid += 1

    # D: geometry battery (J2 headline)
    for gname in field0.GEOMETRY_NAMES:
        b = 4.0 if gname == "nearmiss" else 0.0
        g = field0.collision_geometry(gname, L=L_J2, b=b)
        add("geometry", "j2", L_J2, g, note=f"D:{gname}")
    # E: phase sweep (headon)
    gh = field0.collision_geometry("headon", L=L_J2)
    for j, phi in enumerate(field0.PHASE_GRID):
        add("phase", "j2", L_J2, dict(gh),
            p1_extra={"phase": 0.0}, p2_extra={"phase": float(phi)},
            note=f"E:phi{j}")
    # F: amplitude sweep (headon, a1=1)
    for r in field0.AMP_GRID:
        add("amplitude", "j2", L_J2, dict(gh),
            p1_extra={"amplitude": 1.0}, p2_extra={"amplitude": float(r)},
            note=f"F:a{r}")
    # G: width sweep (headon, both sigma)
    for s in field0.SIGMA_GRID:
        g = field0.collision_geometry("headon", L=L_J2, sigma=float(s))
        add("width", "j2", L_J2, g, note=f"G:sig{s}")
    # H: impact sweep (nearmiss)
    for b in field0.IMPACT_GRID:
        g = field0.collision_geometry("nearmiss", L=L_J2, b=float(b))
        add("impact", "j2", L_J2, g, note=f"H:b{b}")
    # S: substrate controls (headon/coprop/overlap)
    for sk, sl in (("j2", L_J2), ("square", 28), ("ring", 64), ("quotient", 28)):
        for gname in ("headon", "coprop", "overlap"):
            if sk == "ring":
                g = ring_geom_1d(gname, sl)
            else:
                g = field0.collision_geometry(gname, L=sl)
            add("substrate", sk, sl, g, note=f"S:{sk}:{gname}")
    # P: sector collisions (J2 headon, sym/anti)
    for combo in (("sym", "sym"), ("sym", "anti"), ("anti", "anti")):
        add("sector", "j2", L_J2, dict(gh), prep=f"sector:{combo[0]}:{combo[1]}",
            note=f"P:{combo[0]}:{combo[1]}")
    # Q: static + packet (J2)
    add("static", "j2", L_J2,
        {"name": "static-pass", "r1": None, "k1": None,
         "r2": (7.0, 14.0), "k2": (K0, 0.0), "sigma": SIGMA0},
        prep="static:pass", note="Q:pass")
    add("static", "j2", L_J2,
        {"name": "static-far", "r1": None, "k1": None,
         "r2": (7.0, 2.0), "k2": (K0, 0.0), "sigma": SIGMA0},
        prep="static:far", note="Q:far")
    # N: standing (overlap + overlap-pi)
    go = field0.collision_geometry("overlap", L=L_J2)
    add("standing", "j2", L_J2, dict(go),
        p1_extra={"phase": 0.0}, p2_extra={"phase": 0.0}, note="N:phi0")
    add("standing", "j2", L_J2, dict(go),
        p1_extra={"phase": 0.0}, p2_extra={"phase": math.pi}, note="N:phiPi")
    # O: coherence destruction (headon, scramble)
    add("coherence", "j2", L_J2, dict(gh), prep="scramble:1", note="O:scr1")
    add("coherence", "j2", L_J2, dict(gh), prep="scramble:2", note="O:scr2")
    add("coherence", "j2", L_J2, dict(gh), prep="scramble:both", note="O:scrB")
    # M: binding candidates (slow)
    gs = field0.collision_geometry("overlap", L=L_J2, kabs=0.1)
    add("binding", "j2", L_J2, gs, note="M:overlap-slow")
    hs = field0.collision_geometry("headon", L=L_J2, kabs=0.1)
    add("binding", "j2", L_J2, hs, note="M:headon-slow")
    return cells


def prep_packets(cell, sub):
    """Build (psi1_0, psi2_0) per cell prep rule (deterministic)."""
    g = cell["geom"]
    prep = cell["prep"]
    e1 = cell["p1_extra"]
    e2 = cell["p2_extra"]
    if prep == "packet":
        p1 = field0.make_packet(sub, g["r1"], g["k1"], g["sigma"],
                                phase=e1.get("phase", 0.0),
                                amplitude=e1.get("amplitude", 1.0))
        p2 = field0.make_packet(sub, g["r2"], g["k2"], g["sigma"],
                                phase=e2.get("phase", 0.0),
                                amplitude=e2.get("amplitude", 1.0))
        return p1, p2
    if prep.startswith("sector:"):
        _, s1, s2 = prep.split(":")
        b1 = field0.make_packet(sub, g["r1"], g["k1"], g["sigma"])
        b2 = field0.make_packet(sub, g["r2"], g["k2"], g["sigma"])
        f1 = field0.sector_packets(b1, sub)
        f2 = field0.sector_packets(b2, sub)
        return f1[s1], f2[s2]
    if prep.startswith("static:"):
        st = field0.static_field_j2(L=sub["L"], pin_cell=(14, 14), sheet=0)
        p1 = st["phi_norm"]
        p2 = field0.make_packet(sub, g["r2"], g["k2"], g["sigma"])
        return p1, p2
    if prep.startswith("scramble:"):
        p1 = field0.make_packet(sub, g["r1"], g["k1"], g["sigma"])
        p2 = field0.make_packet(sub, g["r2"], g["k2"], g["sigma"])
        mode = prep.split(":")[1]
        if mode in ("1", "both"):
            p1 = scramble_phases(p1, seed=1000 + cell["cid"])
        if mode in ("2", "both"):
            p2 = scramble_phases(p2, seed=2000 + cell["cid"])
        return p1, p2
    raise ValueError(f"unknown prep {prep}")


def run_cell(cell):
    """Execute one collision cell (frozen analysis, no tuning)."""
    t0 = time.time()
    sub = field0.build_substrate(cell["sub_kind"], cell["sub_L"])
    p1_0, p2_0 = prep_packets(cell, sub)
    rec = field0.evolve_triplet(p1_0, p2_0, sub["h"], DT, N_STEPS)
    ts = np.arange(N_STEPS + 1) * DT
    # windows from predicted tcoll (packet geoms only; static/scramble use headon rule)
    try:
        if cell["prep"].startswith("static:"):
            gh = field0.collision_geometry("headon", L=sub["L"])
            pr = field0.predict_tcoll(sub, gh)
            sig = SIGMA0
        elif sub["kind"] == "ring":
            v1 = field0.group_speed("ring", cell["geom"]["k1"])
            v2 = field0.group_speed("ring", cell["geom"]["k2"])
            vr = float(np.linalg.norm(v2 - v1))
            d0 = float(min_image_disp(np.asarray(cell["geom"]["r2"]),
                                      np.asarray(cell["geom"]["r1"]),
                                      sub["periods"])[0])
            tc = -d0 * float(v2[0] - v1[0]) / (vr * vr) if vr > 0 else float("inf")
            tc = max(float(tc), 0.0) if math.isfinite(tc) else float("inf")
            pr = {"tcoll": tc, "vrel": v2 - v1}
            sig = float(cell["geom"]["sigma"])
        else:
            pr = field0.predict_tcoll(sub, cell["geom"])
            sig = float(cell["geom"]["sigma"])
    except Exception:
        pr = {"tcoll": float("inf"), "vrel": np.zeros(len(sub["periods"]))}
        sig = SIGMA0
    vr = float(np.linalg.norm(pr["vrel"])) if "vrel" in pr else 0.0
    win = field0.define_windows(pr["tcoll"], sig, vr, T_END, DT)
    # per-row observables (sampled every 5 steps + endpoints for cost)
    samp = sorted(set(list(range(0, N_STEPS + 1, 5)) + [N_STEPS]))
    eu, ev = edge_arrays(sub["g"], sub["order"])
    eps_max = float(rec["eps"].max())
    # Hilbert overlap S(t) (unitary preserves |S| exactly: constancy is a null
    # leg, Amendment-2) + spatial overlap via COM distance (min = collision).
    from bh_graph.ballistic import com as _com
    S = np.array([abs(complex(field0.overlap_S(a, b)))
                  for a, b in zip(rec["psi1"][samp], rec["psi2"][samp])])
    S_const_dev = float(S.max() - S.min()) if len(S) else 0.0
    com1 = np.array([_com(p, sub["coords"], sub["order"], periods=sub["periods"])
                     for p in rec["psi1"][samp]])
    com2 = np.array([_com(p, sub["coords"], sub["order"], periods=sub["periods"])
                     for p in rec["psi2"][samp]])
    d_com = np.array([float(np.linalg.norm(min_image_disp(a, b, sub["periods"])))
                      for a, b in zip(com1, com2)])
    k_max = samp[int(np.argmin(d_com))] if len(d_com) else N_STEPS // 2
    a1m, a2m = rec["psi1"][k_max], rec["psi2"][k_max]
    rho_ok = bool(field0.is_rho_decomp_ok(a1m, a2m))
    bj_ok = bool(field0.is_BJ_decomp_ok(a1m, a2m, eu, ev, sub["j"]))
    e_ok = bool(field0.is_energy_decomp_ok(a1m, a2m, sub["h"]))
    # cross-term magnitudes
    rx = field0.rho_cross(a1m, a2m)
    cx = field0.BJ_cross_arrays(a1m, a2m, eu, ev, sub["j"])
    ex = float(field0.energy_cross(a1m, a2m, sub["h"]))
    # outgoing (POST mean where available else last quarter)
    post_idx = np.where(win["post"])[0] if np.any(win["post"]) else np.arange(3 * N_STEPS // 4, N_STEPS + 1)
    pre_idx = np.where(win["pre"])[0] if np.any(win["pre"]) else np.arange(0, N_STEPS // 4)
    # COM/velocity/width/coherence/momentum at PRE-mean and POST-mean reps
    def rep(idx_list, rows):
        k = idx_list[len(idx_list) // 2] if len(idx_list) else N_STEPS // 2
        return rows[k], k
    p1pre, k1p = rep(pre_idx, rec["psi1"])
    p1post, k1q = rep(post_idx, rec["psi1"])
    p2pre, k2p = rep(pre_idx, rec["psi2"])
    p2post, k2q = rep(post_idx, rec["psi2"])
    m1pre = field0.momentum_peak(p1pre, sub)
    m1post = field0.momentum_peak(p1post, sub)
    m2pre = field0.momentum_peak(p2pre, sub)
    m2post = field0.momentum_peak(p2post, sub)
    c1post = field0.coherence_of(p1post, sub)
    c2post = field0.coherence_of(p2post, sub)
    # naive peak trace (sampled) + false accel
    peak_coords = []
    for k in samp:
        nk = field0.naive_peak(rec["psi12"][k], sub)
        peak_coords.append(list(nk["com"]))
    peak_coords = np.array(peak_coords)
    uw = field0.unwrap_coords(peak_coords, sub["periods"])
    fa = field0.false_acceleration(uw, ts[samp])
    # residence/beat on joint (center disk radius 2*sigma)
    cx0 = sub["L"] / 2.0
    center = (cx0,) if sub["kind"] == "ring" else (cx0, cx0)
    res = field0.residence_on_disk(rec["psi12"][samp], sub, center, 2.0 * sig)
    beat = float(field0.beat_lifetime(ts[samp], res))
    # witness (isolated PRE vs POST momentum + spectral + energy at POST rep)
    w = field0.witness_components(eps_max, p1pre, p1post, p2pre, p2post,
                                  sub["h"], sub)
    out = {"cid": cell["cid"], "kind": cell["kind"], "note": cell["note"],
           "sub_kind": cell["sub_kind"], "sub_L": cell["sub_L"],
           "tcoll_pred": float(pr["tcoll"]), "vrel": vr,
           "eps_max": eps_max, "rho_ok": rho_ok, "bj_ok": bj_ok, "e_ok": e_ok,
           "rhox_max": float(np.abs(rx).max()), "rhox_sum": float(np.abs(rx).sum()),
           "Bx_max": float(np.abs(cx["B"]).max()), "Jx_max": float(np.abs(cx["J"]).max()),
           "Ex": ex, "S_max": float(S.max()), "S_pre": float(S[0]),
           "S_post": float(S[-1]), "S_const_dev": S_const_dev,
           "d_com_min": float(d_com.min()) if len(d_com) else 0.0,
           "k_max": int(k_max),
           "m1pre_k": list(m1pre["k"]), "m1post_k": list(m1post["k"]),
           "m2pre_k": list(m2pre["k"]), "m2post_k": list(m2post["k"]),
           "m1pre_C": float(m1pre["C"]), "m1post_C": float(m1post["C"]),
           "m2pre_C": float(m2pre["C"]), "m2post_C": float(m2post["C"]),
           "c1post_D": float(c1post["D"]) if np.isfinite(c1post["D"]) else None,
           "c2post_D": float(c2post["D"]) if np.isfinite(c2post["D"]) else None,
           "fa_amax": fa["amax"], "fa_amean": fa["amean"], "fa_vmax": fa["vmax"],
           "res_max": float(res.max()), "beat": beat,
           "w_eps": w["eps"], "w_dP1": w["dP1"], "w_dP2": w["dP2"],
           "w_snew": w["snew"], "w_clin": w["clin"], "w_dE": w["dE"], "w_I": w["I"],
           "norm1_dev": float(np.abs(rec["norms1"] - rec["norms1"][0]).max()),
           "norm12_dev": float(np.abs(rec["norms12"] - rec["norms12"][0]).max()),
           "wall_s": float(time.time() - t0)}
    return out


def main():
    cells = build_cells()
    print(f"FIELD-0 cells: {len(cells)} (T={T_END}, dt={DT}, L_J2={L_J2})", flush=True)
    ckpt = os.path.join(OUT, "field0_cells.jsonl")
    done = set()
    if os.path.exists(ckpt):
        with open(ckpt) as f:
            for line in f:
                try:
                    r = json.loads(line)
                    done.add(r["cid"])
                except Exception:
                    pass
    todo = [c for c in cells if c["cid"] not in done]
    print(f"resumed {len(done)}, todo {len(todo)}", flush=True)
    nw = int(os.environ.get("FIELD0_WORKERS", "32"))
    t0 = time.time()
    fh = open(ckpt, "a")
    if todo:
        with Pool(nw) as pool:
            for i, r in enumerate(pool.imap_unordered(run_cell, todo)):
                fh.write(json.dumps(r) + "\n")
                fh.flush()
                if (i + 1) % 5 == 0:
                    print(f"  {len(done)+i+1}/{len(cells)} {time.time()-t0:.0f}s "
                          f"eps={r['eps_max']:.1e} I={r['w_I']:.1e}", flush=True)
    fh.close()
    allc = []
    with open(ckpt) as f:
        for line in f:
            allc.append(json.loads(line))
    with open(os.path.join(OUT, "field0_cells.json"), "w") as f:
        json.dump({"cells": allc, "T": T_END, "dt": DT, "L_J2": L_J2}, f)
    # headline rollup
    eps = [c["eps_max"] for c in allc]
    Is = [c["w_I"] for c in allc]
    print(f"done {len(allc)} cells in {time.time()-t0:.0f}s", flush=True)
    print(f"eps_max: max={max(eps):.2e} median={sorted(eps)[len(eps)//2]:.2e}", flush=True)
    print(f"I: max={max(Is):.2e} median={sorted(Is)[len(Is)//2]:.2e}", flush=True)
    print(f"rho_ok: {sum(c['rho_ok'] for c in allc)}/{len(allc)} "
          f"bj_ok: {sum(c['bj_ok'] for c in allc)}/{len(allc)} "
          f"e_ok: {sum(c['e_ok'] for c in allc)}/{len(allc)}", flush=True)


if __name__ == "__main__":
    main()
