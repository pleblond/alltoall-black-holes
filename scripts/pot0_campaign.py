"""POT-0 campaign runner (frozen protocol; run AFTER prereg commit).

Executes POT-0A..0E + S1..S5 + L42 robustness on the beast (96 CPU,
multiprocessing over cases) and writes a JSON record with every number
plus per-criterion pass/fail under the frozen POT0-PREREG thresholds.
Deterministic: all seeds fixed in code. --smoke runs a tiny L=8/T=1
apparatus check (not campaign data).
"""

from __future__ import annotations

import argparse
import json
import math
import multiprocessing as mp
import sys

import numpy as np

from bh_graph.ballistic import (
    com,
    evolve_fixed,
    fit_velocity,
    gaussian_packet,
    hamiltonian,
    msd_exponent_rs,
    node_order,
    unwrap_trace,
    velocity_autocorr,
)
from bh_graph.formation import j2_torus_coords, j2_torus_graph
from bh_graph.potential import (
    ang_diff,
    aperture_mask,
    aperture_state,
    cos_between,
    d_trace,
    dephasing_family,
    edge_table,
    flux_decomposition,
    gradient_family,
    is_match_ok,
    null_ensemble,
    pushforward,
    quotient_coords,
    reflectx_perm,
    rot90_perm,
    scramble_phases,
    spectral_coherence,
    spearman,
    translate_perm,
)

# Frozen headline parameters (POT0-PREREG).
L = 28
SIGMA = 4.0
R0 = (7.0, 14.0)
KX = 0.3
T = 10.0
DT = 0.1
N_STEPS = int(T / DT)
C_GRID = tuple(round(c * 0.1, 10) for c in range(11))
R_GRID = (2.0, 3.0, 4.0, 6.0, 8.0, 12.0, None)  # None = full (coded 20)
L42 = 42
R0_42 = (10.0, 21.0)


def _setup(lx):
    g = j2_torus_graph(lx)
    order = node_order(g)
    c3 = j2_torus_coords(lx)
    coords = quotient_coords(c3)
    edges = edge_table(g, order, coords, lx)
    h = hamiltonian(g, order=order)
    return g, order, c3, coords, edges, h


def _evolve_case(args):
    """Worker: evolve one prep, return full readout dict (picklable)."""
    (lx, sigma, r0, kx, ky, tag, prep_kind, prep_arg) = args
    g, order, c3, coords, edges, h = _setup(lx)
    periods = (lx, lx)
    if prep_kind == "packet":
        psi0 = gaussian_packet(coords, order, r0, (kx, ky), sigma, periods=periods)
    elif prep_kind == "gradient_c":
        psi0 = gaussian_packet(
            coords, order, r0, (prep_arg * kx, prep_arg * ky), sigma, periods=periods
        )
    elif prep_kind == "dephase_c":
        clean = gaussian_packet(coords, order, r0, (kx, ky), sigma, periods=periods)
        psi0 = dephasing_family(clean, (prep_arg,), seed=0)[float(prep_arg)]
    elif prep_kind == "scramble":
        clean = gaussian_packet(coords, order, r0, (kx, ky), sigma, periods=periods)
        psi0 = scramble_phases(clean, seed=prep_arg)
    elif prep_kind == "null":
        env = gaussian_packet(coords, order, r0, (kx, ky), sigma, periods=periods)
        psi0 = null_ensemble(env, n=prep_arg + 1, seed0=0)[prep_arg]
    elif prep_kind == "aperture":
        clean = gaussian_packet(coords, order, r0, (kx, ky), sigma, periods=periods)
        if prep_arg is None:
            psi0 = clean
        else:
            psi0 = aperture_state(clean, aperture_mask(order, coords, r0, prep_arg, lx))
    elif prep_kind == "phase":
        clean = gaussian_packet(coords, order, r0, (kx, ky), sigma, periods=periods)
        psi0 = clean * np.exp(1.0j * prep_arg)
    elif prep_kind == "perm":
        clean = gaussian_packet(coords, order, r0, (kx, ky), sigma, periods=periods)
        psi0 = pushforward(clean, prep_arg, order)
    else:
        raise ValueError(prep_kind)
    spec = spectral_coherence(psi0, order, c3, lx)
    f0 = flux_decomposition(psi0, edges)
    rec = evolve_fixed(psi0, h, DT, N_STEPS)
    norms = rec["norms"]
    tr = d_trace(rec["psi"], edges)
    ts = np.arange(rec["psi"].shape[0]) * DT
    rs = unwrap_trace(
        np.array([com(p, coords, order, periods=periods) for p in rec["psi"]]),
        periods=periods,
    )
    alpha = msd_exponent_rs(rs, ts)
    cv = velocity_autocorr(rs, ts)
    fit = fit_velocity(rs, ts)
    disp = float(np.linalg.norm(rs - rs[0], axis=1).max())
    return {
        "tag": tag,
        "prep_D": f0["D"],
        "prep_S": f0["S"],
        "prep_angle": f0["angle"],
        "prep_J": [float(f0["J_net"][0]), float(f0["J_net"][1])],
        "prep_C": spec["C"],
        "prep_M": spec["M_eff"],
        "mean_D": float(tr["D"].mean()),
        "max_D": float(tr["D"].max()),
        "mean_S": float(tr["S"].mean()),
        "mean_J": [float(tr["J_net"][:, 0].mean()), float(tr["J_net"][:, 1].mean())],
        "D_trace": [float(v) for v in tr["D"]],
        "alpha": float(alpha),
        "cv_mean50": float(np.mean(cv[:50])),
        "v": [float(fit["v"][0]), float(fit["v"][1])],
        "speed": float(fit["speed"]),
        "r2": float(fit["r2"]),
        "disp": disp,
        "norm_dev": float(np.abs(norms - 1.0).max()),
    }


def _run(pool, cases):
    return pool.map(_evolve_case, cases)


def _pkt(lx, sigma, r0, kx, tag, kind="packet", arg=None, ky=0.0):
    return (lx, sigma, r0, kx, ky, tag, kind, arg)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="pot0_results.json")
    ap.add_argument("--jobs", type=int, default=mp.cpu_count())
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.smoke:
        global L, T, DT, N_STEPS, C_GRID, R_GRID  # noqa: PLW0603
        L, T, DT = 8, 1.0, 0.2
        N_STEPS = int(T / DT)
        C_GRID = (0.0, 0.5, 1.0)
        R_GRID = (2.0, None)

    pool = mp.get_context("fork").Pool(args.jobs)
    out = {"params": {"L": L, "sigma": SIGMA, "r0": R0, "k": KX, "T": T, "dt": DT}}

    # POT-0A: source + null ensemble.
    src_cases = [_pkt(L, SIGMA, R0, 0.0, "source")]
    null_cases = [_pkt(L, SIGMA, R0, KX, f"null_{s}", "null", s) for s in range(20)]
    # POT-0B: packets +-k.
    b_cases = [
        _pkt(L, SIGMA, R0, KX, "packet_p"),
        _pkt(L, SIGMA, R0, -KX, "packet_m"),
    ]
    # POT-0C: gradient + dephasing grids.
    c_cases = [_pkt(L, SIGMA, R0, KX, f"grad_{c}", "gradient_c", c) for c in C_GRID]
    n_cases = [_pkt(L, SIGMA, R0, KX, f"noise_{c}", "dephase_c", c) for c in C_GRID]
    # POT-0D: scrambled + restored (= clean packet, re-prepped).
    d_cases = [
        _pkt(L, SIGMA, R0, KX, "scrambled", "scramble", 0),
        _pkt(L, SIGMA, R0, KX, "restored"),
    ]
    # POT-0E: aperture grid.
    e_cases = [_pkt(L, SIGMA, R0, KX, f"ap_{r}", "aperture", r) for r in R_GRID]
    # S1: automorphisms of the +k packet (rot90/refx/trans) at prep AND evolved.
    s1_cases = [
        _pkt(L, SIGMA, R0, KX, "rot90", "perm", rot90_perm(L)),
        _pkt(L, SIGMA, R0, KX, "refx", "perm", reflectx_perm(L)),
        _pkt(L, SIGMA, R0, KX, "trans", "perm", translate_perm(L, 3, 5)),
    ]
    # S3: global phases.
    s3_cases = [_pkt(L, SIGMA, R0, KX, f"phase_{p}", "phase", p) for p in (0.7, 2.1, 4.0)]
    # S5: reruns (source + packet).
    s5_cases = [_pkt(L, SIGMA, R0, 0.0, "source_rerun"), _pkt(L, SIGMA, R0, KX, "packet_rerun")]
    # L42 robustness: source + packet + nulls.
    l42_cases = (
        [_pkt(L42, SIGMA, R0_42, 0.0, "L42_source"), _pkt(L42, SIGMA, R0_42, KX, "L42_packet")]
        + [_pkt(L42, SIGMA, R0_42, KX, f"L42_null_{s}", "null", s) for s in range(20)]
    )
    all_cases = (
        src_cases + null_cases + b_cases + c_cases + n_cases + d_cases
        + e_cases + s1_cases + s3_cases + s5_cases + l42_cases
    )
    recs = _run(pool, all_cases)
    pool.close()
    pool.join()
    by_tag = {r["tag"]: r for r in recs}
    out["cases"] = {t: {k: v for k, v in r.items() if k != "D_trace"} for t, r in by_tag.items()}
    out["traces"] = {t: r["D_trace"] for t, r in by_tag.items()}

    # ---- Frozen verdicts (POT0-PREREG thresholds) ----
    src = by_tag["source"]
    nulls = [by_tag[f"null_{s}"]["mean_D"] for s in range(20)]
    null_mean = float(np.mean(nulls))
    null_std = float(np.std(nulls))
    pkt = by_tag["packet_p"]
    pktm = by_tag["packet_m"]
    verdicts = {}
    verdicts["A_source_lt"] = bool(src["mean_D"] < 0.05)
    verdicts["A_source_null"] = bool(src["mean_D"] <= null_mean + 3 * null_std)
    verdicts["A"] = bool(verdicts["A_source_lt"] and verdicts["A_source_null"])
    ratio = pkt["mean_D"] / max(src["mean_D"], 1e-9)
    verdicts["B_D"] = bool(pkt["mean_D"] > 0.5)
    verdicts["B_sep"] = bool((pkt["mean_D"] - src["mean_D"]) > 0.4 and ratio > 10)
    verdicts["B_alpha"] = bool(pkt["alpha"] > 1.3)
    verdicts["B_cv"] = bool(pkt["cv_mean50"] > 0.5)
    cos_pm = cos_between(pkt["mean_J"], pktm["mean_J"])
    verdicts["B_rev"] = bool(cos_pm < -0.95 and is_match_ok(pkt["mean_D"], pktm["mean_D"], 0.10))
    verdicts["B_r2"] = bool(pkt["r2"] > 0.99 and pktm["r2"] > 0.99)
    verdicts["B"] = bool(all(verdicts[k] for k in ("B_D", "B_sep", "B_alpha", "B_cv", "B_rev", "B_r2")))
    grad = [by_tag[f"grad_{c}"] for c in C_GRID]
    noise = [by_tag[f"noise_{c}"] for c in C_GRID]
    gv = [r["speed"] for r in grad]
    gd = [r["mean_D"] for r in grad]
    nd = [r["mean_D"] for r in noise]
    verdicts["C_grad_ratio"] = bool(gd[-1] / max(gd[0], 1e-9) > 10)
    verdicts["C_grad_v"] = bool(spearman(gv, list(C_GRID)) > 0.7 and gv[0] < 0.05 * max(gv[-1], 1e-300))
    verdicts["C_noise"] = bool(
        spearman(nd, list(C_GRID)) > 0.5 and nd[-1] / max(nd[0], 1e-9) > 5
    )
    verdicts["C"] = bool(verdicts["C_grad_ratio"] and verdicts["C_grad_v"] and verdicts["C_noise"])
    gc = [r["prep_C"] for r in grad]
    verdicts["C_constancy"] = bool((max(gc) - min(gc)) / max(max(gc), 1e-300) < 0.05)
    scr = by_tag["scrambled"]
    rest = by_tag["restored"]
    verdicts["D_scr_D"] = bool(scr["mean_D"] < 0.15 * pkt["mean_D"])
    verdicts["D_scr_C"] = bool(scr["prep_C"] < 0.5 * pkt["prep_C"])
    verdicts["D_rest_D"] = bool(is_match_ok(rest["mean_D"], pkt["mean_D"], 0.15))
    verdicts["D_rest_C"] = bool(is_match_ok(rest["prep_C"], pkt["prep_C"], 0.15))
    pool_c = [r["prep_C"] for r in noise] + [pkt["prep_C"], scr["prep_C"], rest["prep_C"]]
    pool_d = [r["mean_D"] for r in noise] + [pkt["mean_D"], scr["mean_D"], rest["mean_D"]]
    verdicts["D_corr"] = bool(spearman(pool_c, pool_d) > 0.5)
    verdicts["D"] = bool(all(verdicts[k] for k in ("D_scr_D", "D_scr_C", "D_rest_D", "D_rest_C", "D_corr")))
    aps = [by_tag[f"ap_{r}"] for r in R_GRID]
    rr = [20.0 if r is None else r for r in R_GRID]
    ad = [r["mean_D"] for r in aps]
    am = [r["prep_M"] for r in aps]
    verdicts["E_corr"] = bool(spearman(ad, rr) > 0.5)
    verdicts["E_small"] = bool(ad[0] < 0.5 * ad[-1])
    verdicts["E_width"] = bool(spearman(am, rr) < -0.5)
    verdicts["E"] = bool(verdicts["E_corr"] and verdicts["E_small"] and verdicts["E_width"])
    rot = by_tag["rot90"]
    ref = by_tag["refx"]
    tra = by_tag["trans"]
    verdicts["S1_rot_prep"] = bool(
        ang_diff(rot["prep_angle"], pkt["prep_angle"] + math.pi / 2) < math.radians(5)
        and is_match_ok(rot["prep_D"], pkt["prep_D"], 0.05)
    )
    rot_mj = math.atan2(rot["mean_J"][1], rot["mean_J"][0])
    pkt_mj = math.atan2(pkt["mean_J"][1], pkt["mean_J"][0])
    verdicts["S1_rot_evo"] = bool(
        ang_diff(rot_mj, pkt_mj + math.pi / 2) < math.radians(5)
        and is_match_ok(rot["mean_D"], pkt["mean_D"], 0.05)
    )
    verdicts["S1_ref_prep"] = bool(
        ang_diff(ref["prep_angle"], math.pi - pkt["prep_angle"]) < math.radians(5)
        and is_match_ok(ref["prep_D"], pkt["prep_D"], 0.05)
    )
    ref_mj = math.atan2(ref["mean_J"][1], ref["mean_J"][0])
    verdicts["S1_ref_evo"] = bool(
        ang_diff(ref_mj, math.pi - pkt_mj) < math.radians(5)
        and is_match_ok(ref["mean_D"], pkt["mean_D"], 0.05)
    )
    tj = np.array(tra["mean_J"])
    pj = np.array(pkt["mean_J"])
    verdicts["S1_trans"] = bool(
        float(np.abs(tj - pj).max()) < 1e-9 and abs(tra["mean_D"] - pkt["mean_D"]) < 1e-9
    )
    verdicts["S1"] = bool(all(verdicts[k] for k in (
        "S1_rot_prep", "S1_rot_evo", "S1_ref_prep", "S1_ref_evo", "S1_trans")))
    verdicts["S2"] = bool(verdicts["B_rev"])
    s3ok = True
    for p in (0.7, 2.1, 4.0):
        r = by_tag[f"phase_{p}"]
        s3ok = s3ok and abs(r["prep_D"] - pkt["prep_D"]) < 1e-12
        s3ok = s3ok and abs(r["prep_C"] - pkt["prep_C"]) < 1e-12
        s3ok = s3ok and abs(r["mean_D"] - pkt["mean_D"]) < 1e-9
    verdicts["S3"] = bool(s3ok)
    verdicts["S4"] = bool(src["mean_D"] < 0.05 and src["speed"] < 0.05 * max(pkt["speed"], 1e-300))
    # S5 bit-identity needs psi rows: rerun cheaply in-process (deterministic check).
    from bh_graph.potential import edge_table as _et  # noqa: PLC0415
    g, order, c3, coords, edges, h = _setup(L)
    periods = (L, L)
    s5ok = True
    for tag, kx in (("source", 0.0), ("packet_p", KX)):
        psi0 = gaussian_packet(coords, order, R0, (kx, 0.0), SIGMA, periods=periods)
        r1 = evolve_fixed(psi0, h, DT, N_STEPS)["psi"]
        r2 = evolve_fixed(psi0, h, DT, N_STEPS)["psi"]
        s5ok = s5ok and bool(np.array_equal(r1, r2))
        t1 = d_trace(r1, edges)["D"]
        t2 = d_trace(r2, edges)["D"]
        s5ok = s5ok and bool(np.array_equal(t1, t2))
    verdicts["S5"] = bool(s5ok)
    l42s = by_tag["L42_source"]
    l42p = by_tag["L42_packet"]
    l42n = [by_tag[f"L42_null_{s}"]["mean_D"] for s in range(20)]
    l42nm = float(np.mean(l42n))
    l42ns = float(np.std(l42n))
    verdicts["L42_A"] = bool(l42s["mean_D"] < 0.05 and l42s["mean_D"] <= l42nm + 3 * l42ns)
    verdicts["L42_B"] = bool(
        l42p["mean_D"] > 0.5
        and (l42p["mean_D"] - l42s["mean_D"]) > 0.4
        and l42p["mean_D"] / max(l42s["mean_D"], 1e-9) > 10
    )
    verdicts["L42"] = bool(verdicts["L42_A"] and verdicts["L42_B"])
    core = all(verdicts[k] for k in ("A", "B", "C", "D", "S1", "S2", "S3", "S4", "S5"))
    if not (verdicts["A"] and verdicts["B"]):
        ladder = "POT0-NULL"
    elif not (core and verdicts["L42"]):
        ladder = "POT0-SPREAD"
    elif not verdicts["E"]:
        ladder = "POT0-COHERENCE-DIRECTION"
    else:
        ladder = "POT0-COLLECTIVE"
    # Note: L42 failure caps at SPREAD per prereg (checked above via core+L42).
    verdicts["ladder"] = ladder
    out["verdicts"] = verdicts
    out["null_stats"] = {"mean": null_mean, "std": null_std, "vals": nulls}
    out["L42_null_stats"] = {"mean": l42nm, "std": l42ns, "vals": l42n}
    out["C_D_pool"] = {"C": pool_c, "D": pool_d, "spearman": spearman(pool_c, pool_d)}
    with open(args.out, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(verdicts, indent=1))
    print(f"ladder: {ladder}")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
