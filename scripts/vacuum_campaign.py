"""Vacuum campaign: runs the full prereg'd grid -> results/vacuum/*.json.

Prereg: docs/derivation-prereg.md (commit before compute). This script adds
NO new parameters: every number comes from the prereg or the modules'
prereg'd defaults. Parallel over independent cells (multiprocessing).
"""
from __future__ import annotations

import concurrent.futures
import json
import os
import subprocess
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph.vacuum_curvature import (  # noqa: E402
    all_edge_kappa,
    compare_fits,
    shell_kappa_profile_vacuum,
    sinkhorn_crosscheck_kappa,
)
from bh_graph.vacuum_graphs import (  # noqa: E402
    VACUUM_DEGREES,
    VACUUM_SIZES,
    add_excursion,
    build_a15_dual,
    build_a15_single_cell,
    build_vacuum,
    excursion_centers,
)
from bh_graph.vacuum_spectra import (  # noqa: E402
    BU_BAND,
    candidate_gamma_maps,
    degree_stats,
    hits_claimed,
    normalized_laplacian_spectrum,
    repo_c2_at_bu_p,
    selectivity_audit,
    spectral_gap_info,
    stationary_tv_from_uniform,
)

OUT = os.path.join(os.path.dirname(__file__), "..", "results", "vacuum")
EXCURSION_SIZES = (2, 4, 8)
N_SCALING_L = (4, 5, 6, 7, 8)


def _git(cmd):
    try:
        return subprocess.check_output(["git"] + cmd, text=True,
                                       cwd=os.path.dirname(__file__)).strip()
    except (subprocess.CalledProcessError, OSError):
        return "?"


def _cell(args):
    """One (family, size, s, center) grid cell -> record (picklable)."""
    family, size, s, center = args
    t0 = time.time()
    g, meta = build_vacuum(family, size)
    h, _ = add_excursion(g, center, s)
    prof = shell_kappa_profile_vacuum(h, center)
    cmp_ = compare_fits(prof["profile"])
    rec = {"family": family, "size": size, "N": meta["N"],
           "k": meta["k"], "s": s, "center": center,
           "profile": {str(r): v for r, v in prof["profile"].items()},
           "counts": {str(r): c for r, c in prof["counts"].items()},
           "signs": {str(r): v for r, v in prof["signs"].items()},
           "ok": cmp_["ok"], "winner": cmp_["winner"], "dBIC": cmp_["dBIC"],
           "elapsed_s": time.time() - t0}
    for m, f in cmp_["fits"].items():
        rec[m] = {kk: (float(v) if isinstance(v, float) else v)
                  for kk, v in f.items() if kk != "model"}
    return rec


def run_grid(workers):
    cells = [(fam, size, s, c)
             for fam, sizes in VACUUM_SIZES.items() for size in sizes
             for s in EXCURSION_SIZES
             for c in excursion_centers(
                 {"cubic": size ** 3, "bcc": 2 * size ** 3,
                  "fcc": 4 * size ** 3, "kelvin": 2 * size ** 3}[fam])]
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as ex:
        recs = list(ex.map(_cell, cells))
    recs.sort(key=lambda r: (r["family"], r["size"], r["s"], r["center"]))
    return recs


def run_test_i():
    out = {}
    for fam, sizes in VACUUM_SIZES.items():
        for size in sizes:
            g, meta = build_vacuum(fam, size)
            kaps = np.array(list(all_edge_kappa(g).values()))
            out[f"{fam}-{size}"] = {
                "family": fam, "size": size, "N": meta["N"], "k": meta["k"],
                "n_edges": len(kaps), "max_abs": float(np.max(np.abs(kaps))),
                "mean_abs": float(np.mean(np.abs(kaps))),
                "mean": float(np.mean(kaps)), "std": float(np.std(kaps)),
                "min": float(np.min(kaps)), "max": float(np.max(kaps))}
    return out


def _edge_type_split_a15():
    g, meta = build_a15_dual(2)
    kaps = all_edge_kappa(g)
    deg = dict(g.degree())
    groups: dict[str, list[float]] = {}
    for (u, v), kk in kaps.items():
        key = f"{min(deg[u], deg[v])}-{max(deg[u], deg[v])}"
        groups.setdefault(key, []).append(kk)
    return {k: {"n": len(v), "mean": float(np.mean(v)),
                "std": float(np.std(v))} for k, v in sorted(groups.items())}


def run_spectral():
    out = {}
    jobs = [("a15-nc2", build_a15_dual(2)),
            ("a15-nc3", build_a15_dual(3)),
            ("a15-cell", build_a15_single_cell()),
            ("cubic-L4", build_vacuum("cubic", 4)),
            ("cubic-L6", build_vacuum("cubic", 6)),
            ("bcc-nc3", build_vacuum("bcc", 3)),
            ("fcc-nc3", build_vacuum("fcc", 3)),
            ("kelvin-nc3", build_vacuum("kelvin", 3))]
    for name, (g, meta) in jobs:
        spec = normalized_laplacian_spectrum(g)
        info = spectral_gap_info(g)
        k_avg = 2.0 * g.number_of_edges() / g.number_of_nodes()
        maps = candidate_gamma_maps(info["lambda1"], k_avg) if info["ok"] else {}
        out[name] = {
            "N": meta["N"], "k_or_mean": meta["k"], "k_avg": k_avg,
            "lambda1": info["lambda1"], "n_zeros": info["n_zeros"],
            "lambda_max": info["lambda_max"],
            "spectrum": [float(v) for v in spec],
            "maps": maps,
            "hits": {m: bool(hits_claimed(v)) for m, v in maps.items()}}
    return out


def run_regularity(test_i):
    out = {}
    for fam, sizes in VACUUM_SIZES.items():
        for size in sizes:
            g, meta = build_vacuum(fam, size)
            out[f"{fam}-{size}"] = {
                "degree": degree_stats(g),
                "stationary_tv": stationary_tv_from_uniform(g),
                "kappa_unperturbed": test_i[f"{fam}-{size}"]}
    for nc in (2, 3):
        g, meta = build_a15_dual(nc)
        kaps = np.array(list(all_edge_kappa(g).values()))
        out[f"a15-nc{nc}"] = {
            "degree": degree_stats(g),
            "stationary_tv": stationary_tv_from_uniform(g),
            "kappa_unperturbed": {
                "N": meta["N"], "n_edges": len(kaps),
                "max_abs": float(np.max(np.abs(kaps))),
                "mean_abs": float(np.mean(np.abs(kaps))),
                "mean": float(np.mean(kaps)), "std": float(np.std(kaps)),
                "min": float(np.min(kaps)), "max": float(np.max(kaps))}}
    out["a15-edge-type-split-nc2"] = _edge_type_split_a15()
    return out


def run_phase2():
    from bh_graph.dispersion import (
        arrival_delay_s,
        eqg2_scale_gev,
        fermi_quad_margin,
    )
    from bh_graph.gwdata import echo_margin_orders
    from bh_graph.pulsar import (
        C1_GR,
        C1_MODEL,
        C2_GR,
        J0737,
        B1913,
        c2_of_p,
        dot_omega_dir_2pn_degyr,
        dot_omega_model_degyr,
        invert_mass_msun,
        kepler_a_m,
        model_factor,
        sin_i_from_x,
    )
    # A. LIV null: mock (10 GeV, 3 Gpc) then real (31 GeV GRB 090510, z=0.903).
    mock = arrival_delay_s(10.0, 3000.0)
    # Light-travel distance for z=0.903 ~ 7.3 Gyr ~ 2.24 Gpc (Planck 2018
    # cosmology, quoted; repo takes Mpc). Fermi Abdo+2009 bound < 0.859 s.
    real = arrival_delay_s(31.0, 2240.0)
    fermi_bound_s = 0.859
    # C. Echo null.
    margin = echo_margin_orders(100.0)
    # B. 2PN consistency gate (repo-pinned PK; Kramer+2021 per code comment).
    c2 = c2_of_p(0.92)
    m_gr = invert_mass_msun(J0737["Pb_s"], J0737["e"], J0737["dot_obs"],
                            C1_GR, C2_GR)
    m_mo = invert_mass_msun(J0737["Pb_s"], J0737["e"], J0737["dot_obs"],
                            C1_MODEL, c2)
    got = dot_omega_model_degyr(m_mo, J0737["Pb_s"], J0737["e"], C1_MODEL, c2)
    dd = dot_omega_dir_2pn_degyr(m_gr, J0737["Pb_s"], J0737["e"])
    resid_fixed = (model_factor(C1_MODEL, c2) - 1.0) * dd
    a_mo = kepler_a_m(m_mo, J0737["Pb_s"])
    s_mo = sin_i_from_x(J0737["xA_s"], J0737["xB_s"], a_mo)
    return {
        "A_liv": {"eqg2_gev": eqg2_scale_gev(),
                  "fermi_quad_margin": fermi_quad_margin(),
                  "mock_10gev_3gpc_s": mock,
                  "real_31gev_grb090510_s": real,
                  "fermi_bound_s": fermi_bound_s,
                  "null_margin_orders": float(np.log10(fermi_bound_s / real))},
        "C_echo": {"margin_orders_100hz": margin},
        "B_2pn_gate": {
            "label": "CONSISTENCY-GATE (never VALIDATION)",
            "m_gr": m_gr, "m_model": m_mo,
            "dot_resid_sigma": abs(got - J0737["dot_obs"]) / J0737["dot_err_new"],
            "dot_fixedM_resid_sigma": abs(resid_fixed) / J0737["dot_err_new"],
            "sin_i": s_mo, "sin_i_obs": J0737["s_obs"],
            "b1913_pb_s": B1913["Pb_s"]},
    }


def main():
    os.makedirs(OUT, exist_ok=True)
    workers = max(1, min(4, os.cpu_count() or 2))
    t0 = time.time()
    meta = {"prereg": "docs/derivation-prereg.md",
            "branch": _git(["rev-parse", "--abbrev-ref", "HEAD"]),
            "commit": _git(["rev-parse", "HEAD"]),
            "prereg_commit": "0fef495",
            "workers": workers}
    print("test_i ...", flush=True)
    test_i = run_test_i()
    json.dump(test_i, open(f"{OUT}/test_i.json", "w"), indent=1)
    print("grid (81 cells) ...", flush=True)
    grid = run_grid(workers)
    json.dump(grid, open(f"{OUT}/grid.json", "w"), indent=1)
    print("nscaling (cubic L=4..8 medians from grid+runs) ...", flush=True)
    nscal = {}
    for L in N_SCALING_L:
        recs = [r for r in grid if r["family"] == "cubic" and r["size"] == L]
        if not recs:  # L=7,8 not in prereg grid: run 9 cells each
            cells = [("cubic", L, s, c) for s in EXCURSION_SIZES
                     for c in excursion_centers(L ** 3)]
            with concurrent.futures.ProcessPoolExecutor(
                    max_workers=workers) as ex:
                recs = list(ex.map(_cell, cells))
            grid.extend(recs)
            json.dump(grid, open(f"{OUT}/grid.json", "w"), indent=1)
        ps = [r["power"]["p"] for r in recs
              if r["ok"] and np.isfinite(r["power"].get("p", np.nan))]
        nscal[str(L)] = {"N": L ** 3, "n_cells": len(recs),
                         "n_p_ok": len(ps),
                         "median_p": float(np.median(ps)) if ps else None,
                         "mean_p": float(np.mean(ps)) if ps else None,
                         "std_p": float(np.std(ps)) if ps else None}
    json.dump(nscal, open(f"{OUT}/nscaling.json", "w"), indent=1)
    print("spectral ...", flush=True)
    json.dump(run_spectral(), open(f"{OUT}/spectral.json", "w"), indent=1)
    print("selectivity ...", flush=True)
    sel = selectivity_audit()
    sel["band"] = list(BU_BAND)
    sel["repo_c2_at_bu_p"] = repo_c2_at_bu_p()
    from bh_graph.vacuum_spectra import p_hat_of_k
    sel["p_hat_13p5"] = float(p_hat_of_k(13.5))
    sel["p_hat_repo_c2_k13p5"] = float(p_hat_of_k(13.5, c2=repo_c2_at_bu_p()))
    json.dump(sel, open(f"{OUT}/selectivity.json", "w"), indent=1)
    print("regularity ...", flush=True)
    json.dump(run_regularity(test_i),
              open(f"{OUT}/regularity.json", "w"), indent=1)
    print("sinkhorn cross-check (cubic L=4, 8 edges) ...", flush=True)
    g, _ = build_vacuum("cubic", 4)
    import networkx as nx
    from bh_graph.orici import ollivier_curvature
    edges = list(g.edges())[:8]
    dist = nx.floyd_warshall_numpy(g)
    idx = {v: i for i, v in enumerate(g.nodes())}
    exact = float(np.mean([ollivier_curvature(g, u, v, _dist=dist, _idx=idx)
                           for u, v in edges]))
    sk = sinkhorn_crosscheck_kappa(g, edges)
    json.dump({"family": "cubic", "size": 4, "n_edges": len(edges),
               "exact_mean": exact, "sinkhorn_mean": sk.get("mean"),
               "bias_ok": bool(sk.get("mean", 1) <= exact + 1e-6)},
              open(f"{OUT}/sinkhorn_xcheck.json", "w"), indent=1)
    print("phase2 ...", flush=True)
    json.dump(run_phase2(), open(f"{OUT}/phase2.json", "w"), indent=1)
    meta["elapsed_s"] = time.time() - t0
    json.dump(meta, open(f"{OUT}/meta.json", "w"), indent=1)
    print(f"done in {meta['elapsed_s']:.0f}s -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
