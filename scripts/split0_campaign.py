"""SPLIT-0 campaign (frozen cells, pre-data).

Tasks (mp pool, module-level workers, 96-way on beast):
  - cell: per (M, k) merged cell: graph census, inverse dimensions,
    deterministic core, roundtrip (all covers x 2 d-values), minimality,
    locality + applicability, hidden anatomy, no-measure control,
    relabel/phase/swap/xi covariance.
  - forward: per (X, edge) forward cell: contraction-inverse bridge +
    halves reverse support (MEASURE-0C reproduction).
  - j2: per J2 background: sheet covariance, hidden anatomy, locality.
  - firewall: no-tuning inspection (single task).

Deterministic (frozen battery only, no RNG). Output:
data/split0_ledger.json. Gates applied by scripts/split0_analyze.py.
"""

from __future__ import annotations

import json
import math
import os
import platform
import subprocess
import sys
import time
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import split0 as s0

D_PROBE = (0.0j, 0.5 - 0.25j)


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
    if isinstance(x, frozenset):
        return sorted(_sanitize(v) for v in x)
    return x


def _git_hash():
    try:
        here = os.path.join(os.path.dirname(__file__), "..")
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=here,
            stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


# ---------------------------------------------------------------------------
# Workers
# ---------------------------------------------------------------------------

def run_cell_task(key):
    from bh_graph.sym0 import reversal_perm, shuffle_perm

    gn, fn, k = key
    st = s0.merged_state(gn, fn)
    g, psi, order = st["g"], st["psi"], st["order"]
    cover_ok = s0.is_cover_complete_ok(g, k)
    dim_ok = s0.is_dimension_formula_ok(g, psi, order, k)
    dims = s0.inverse_dimensions(g, psi, order, k)
    det = s0.deterministic_core_status(g, psi, order, k)
    # Roundtrip over all covers x probe d-values.
    rt_bad = 0
    rt_n = 0
    for row in s0.undirected_predecessors(g, k):
        for d in D_PROBE:
            rt_n += 1
            if not s0.is_roundtrip_ok(g, psi, order, k,
                                      {"cover_key": row["key"],
                                       "d": complex(d)}):
                rt_bad += 1
    minimal = s0.is_minimal_ok(g, psi, order, k)
    wit = s0.minimality_witnesses(g, psi, order, k)
    local = s0.is_inverse_local_ok(g, psi, order, k)
    appl = s0.locality_applicability(g, order, k)
    hidden = s0.is_hidden_retained_ok(g, psi, order, k)
    han = s0.hidden_anatomy(g, psi, order, k)
    nomeas = s0.is_measure_independent_ok(g, psi, order, k)
    perms = [reversal_perm(order), shuffle_perm(order, 11)]
    cov_cover = all(s0.is_cover_covariant_ok(g, k, p) for p in perms)
    cov_xi = all(s0.is_xi_representation_independent_ok(
        g, psi, order, k, 0.5 + 0.5j, p, a)
        for p in perms for a in s0.U1_GRID)
    cov_swap = all(s0.is_residual_covariant_swap_ok(d)
                   for d in s0.D_SWEEP)
    cov_phase = all(s0.is_residual_covariant_phase_ok(1.0 + 1.0j, d, a)
                    for d in s0.D_SWEEP for a in s0.U1_GRID)
    return _sanitize({"cell": f"{gn}/{fn}@{k}", "d": dims["d"],
                      "cover_ok": bool(cover_ok), "dim_ok": bool(dim_ok),
                      "dims": dims, "det": det,
                      "roundtrip_bad": rt_bad, "roundtrip_n": rt_n,
                      "minimal": bool(minimal),
                      "drop_cover_applicable": bool(
                          wit["drop_cover"].get("applicable", False)),
                      "local": bool(local), "applicability": appl,
                      "hidden": bool(hidden),
                      "D_merged": han["D_merged"],
                      "locally_varies": bool(han["locally_varies"]),
                      "nomeasure": bool(nomeas),
                      "cov_cover": bool(cov_cover),
                      "cov_xi": bool(cov_xi), "cov_swap": bool(cov_swap),
                      "cov_phase": bool(cov_phase)})


def run_forward_task(key):
    gn, fn, i, j = key
    st = s0.merged_state(gn, fn)
    g, psi, order = st["g"], st["psi"], st["order"]
    bridge = s0.contraction_inverse_check(g, psi, order, i, j)
    rev = s0.halves_reverse_support(g, psi, order, i, j)
    equiv = bool(rev["full_reverse"] == rev["halves_condition"])
    return _sanitize({"cell": f"{gn}/{fn}#{i}-{j}",
                      "recorded_cover_found": bridge["recorded_cover_found"],
                      "restores_graph": bridge["restores_graph"],
                      "graph_reverse": rev["graph_reverse"],
                      "halves_condition": rev["halves_condition"],
                      "full_reverse": rev["full_reverse"],
                      "verdict": rev["verdict"],
                      "full_iff_halves": equiv})


def run_j2_task(bg):
    spot = s0.j2_merged_spot(s0.J2_L_SPOT, bg)
    g, psi, order = spot["g"], spot["psi"], spot["order"]
    k = spot["k"]
    sheet = s0.is_sheet_covariant_ok_j2(spot)
    hidden = s0.is_hidden_retained_ok(g, psi, order, k)
    han = s0.hidden_anatomy(g, psi, order, k)
    local = s0.is_inverse_local_ok(g, psi, order, k)
    appl = s0.locality_applicability(g, order, k)
    dims = s0.inverse_dimensions(g, psi, order, k)
    return _sanitize({"background": bg, "k": k, "d": dims["d"],
                      "sheet_covariant": bool(sheet),
                      "hidden": bool(hidden),
                      "D_merged": han["D_merged"],
                      "locally_varies": bool(han["locally_varies"]),
                      "local": bool(local), "applicability": appl,
                      "dims": dims})


def run_firewall_task(_key):
    return _sanitize({"no_hidden_tuning": bool(s0.is_no_hidden_tuning_ok())})


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def main():
    t0 = time.time()
    t0 = time.time()
    cells = [(c["graph"], c["field"], c["k"])
             for c in s0.split0_cells()]
    forwards = []
    for gn in s0.SPLIT0_GRAPHS:
        for fn in s0.SPLIT0_FIELDS:
            st = s0.merged_state(gn, fn)
            for (i, j) in sorted(tuple(sorted(e))
                                 for e in st["g"].edges()):
                forwards.append((gn, fn, i, j))
    j2keys = list(s0.J2_BACKGROUNDS)
    workers = int(os.environ.get("SPLIT0_WORKERS", "32"))
    with Pool(workers) as pool:
        cell_rows = pool.map(run_cell_task, cells)
        forward_rows = pool.map(run_forward_task, forwards)
        j2_rows = pool.map(run_j2_task, j2keys)
        firewall_rows = pool.map(run_firewall_task, ["firewall"])
    out = {"provenance": {"git": _git_hash(),
                          "platform": platform.platform(),
                          "python": platform.python_version(),
                          "workers": workers,
                          "elapsed_s": round(time.time() - t0, 1)},
           "cells": cell_rows, "forwards": forward_rows,
           "j2": j2_rows, "firewall": firewall_rows}
    path = os.path.join(os.path.dirname(__file__), "..",
                        "data", "split0_ledger.json")
    with open(path, "w") as fh:
        json.dump(out, fh)
    n_cells = len(cell_rows)
    n_fwd = len(forward_rows)
    print(f"SPLIT0-CAMPAIGN cells={n_cells} forwards={n_fwd} "
          f"j2={len(j2_rows)} elapsed={time.time() - t0:.1f}s -> {path}")


if __name__ == "__main__":
    main()
