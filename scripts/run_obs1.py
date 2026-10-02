"""OBS-1 station measurement runner (FROZEN per OBS1-PREREG; beast only).

Units (one process each, parallelized via xargs):
  eigen    build graph + cache eigensystems for a NEW tag (reuses the
           OBS-0 unit verbatim): needed ONLY for exp-N32768-s{0,1,2}
           (all other cells reuse banked obs0/obs0r eigen -- the runner
           never rebuilds banked systems).
  stations one (cell, set): 64 opaque stations, all-pairs directed
           operational measurements (tau_D, tau_W, static phi).

CELLS (FROZEN order; the blind stage sees ONLY the integer cell id):
  0 j2-L42    1 j2-L64    2 j2-L128     (headlines: quotient target)
  3 sq-L42    4 sq-L64    5 sq-L128     (C0: known-2D control)
  6 exp-N3528-s0  7 exp-N8192-s0  8 exp-N32768-s0  (C1: non-2D control)

Station sampling (FROZEN): rng(9100 + 100*cell + set).choice(N, 64)
with S-ids assigned in rng-permuted order (train S0-31 / test S32-63
is therefore a random held-out split).

Outputs per (cell, set):
  obs1_meas_cell{c}_s{set}.json  OPAQUE (S-ids + values only; the ONLY
                                 blind-stage input -- schema-audited)
  obs1_seal_cell{c}_s{set}.json  SEALED (cell->tag + S-id->node map;
                                 reveal stage ONLY, after blind freeze)
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))
from bh_graph import obs0, obs0r  # noqa: E402
from bh_graph.ballistic import hamiltonian  # noqa: E402
from bh_graph.driven import is_gap_ok  # noqa: E402
from scipy import sparse  # noqa: E402
from scipy.sparse.linalg import cg as _sp_cg  # noqa: E402
import run_obs0  # noqa: E402

CELLS = ("j2-L42", "j2-L64", "j2-L128",
         "sq-L42", "sq-L64", "sq-L128",
         "exp-N3528-s0", "exp-N8192-s0", "exp-N32768-s0")
N_STATIONS = 64
STATION_SEED_BASE = 9100
CG_RTOL = 1e-11  # solver tolerance (pinned vs spsolve by unit test)


def static_phi_cg(h_csc, src_idx: int, omega: float,
                  rtol: float = CG_RTOL) -> np.ndarray:
    """POT-1 static field via CG (same equation as driven.steady_predict).

    Solves (H_BB-w)*phi_B = -H_BS*s, phi_S = s = 1.0 with spsolve replaced
    by conjugate gradients: H-wI is SPD (spectrum in [0.5, z+0.5]), so CG
    converges in O(sqrt(kappa)) iterations with ZERO fill-in. Direct
    SuperLU is infeasible here (expander treewidth -> dense fill: 64
    factorizations/set would take weeks at N32768; identical equation,
    verified bit-compatible to 1e-8 by tests/test_run_obs1.py). Raises on
    non-convergence (loud, never silent).
    """
    n = h_csc.shape[0]
    o = int(src_idx)
    bulk = np.ones(n, dtype=bool)
    bulk[o] = False
    a = (h_csc - float(omega) * sparse.eye(n)).tocsc()
    abb = a[bulk, :][:, bulk]
    rhs = -a[bulk, :][:, [o]].toarray().ravel()
    phi_b, info = _sp_cg(abb, rhs, rtol=float(rtol), atol=0.0,
                         maxiter=10 * n)
    if int(info) != 0:
        raise RuntimeError(f"CG failed to converge (info={info})")
    phi = np.zeros(n)
    phi[bulk] = phi_b
    phi[o] = 1.0
    return phi


def diff_readouts(wl, Vl, o_idx, tj, D):
    """OBS-1 diffusion observer readout (FROZEN instrument).

    tau_D = FIRST THRESHOLD-CROSSING at the shared instrument floor
    THETA_WAVE (same floor as the wave channel): the observer's
    "when did you first notice" detection time. The OBS-0 CFD peak time
    is structurally missing in the far field (monotonic rise: 52%
    missing on spanning station sets -- pre-prereg smoke, no geometry
    consulted) and is recorded as the Dcfd bridge column only (never
    consumed by blind estimators). sqrt(tau_D) correlates 0.98 with R
    and 0.96 with CFD on common pairs (sq-L42 smoke).
    Returns ({idx: tau_thresh}, {idx: tau_cfd}).
    """
    ts = obs0.diffusion_grid(D)
    P = obs0._target_traces_diff(wl, Vl, o_idx, tj, ts)
    th = obs0.THETA_WAVE
    t_thr = {int(j): obs0.threshold_crossing(P[:, k], ts, th)
             for k, j in enumerate(tj)}
    t_cfd = {int(j): obs0.cfd_first_peak(P[:, k], ts)
             for k, j in enumerate(tj)}
    return t_thr, t_cfd


def audit_meas_schema(meas):
    """C3 defense-in-depth: opaque files carry ONLY S-ids + values.

    Raises on any hidden-geometry key (tag/node/coords/...). Called by
    cmd_stations before writing; the blind loader re-enforces S-id keys.
    """
    if set(meas) != {"cell", "set", "n", "pairs"}:
        raise ValueError(f"meas top-level keys: {sorted(meas)}")
    for key, rec in meas["pairs"].items():
        a, b = key.split("|")
        for s in (a, b):
            if not s.startswith("S") or not s[1:].isdigit():
                raise ValueError(f"non-opaque pair key: {key!r}")
        bad = set(rec) - {"W", "D", "P", "Dcfd"}
        if bad:
            raise ValueError(f"hidden channel keys: {bad}")
    return True


def cmd_eigen(args):
    run_obs0.cmd_eigen(args)


def _find(tag_name, datadirs):
    for d in datadirs:
        p = os.path.join(d, tag_name)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f"{tag_name} not in {datadirs}")


def sample_stations(n_nodes, cell, aset):
    """FROZEN station draw: {S-id: node} + node list in S-order."""
    rng = np.random.default_rng(STATION_SEED_BASE + 100 * cell + aset)
    nodes = rng.choice(n_nodes, size=N_STATIONS, replace=False)
    order = rng.permutation(N_STATIONS)
    smap = {f"S{i}": int(nodes[order[i]]) for i in range(N_STATIONS)}
    return smap, [smap[f"S{i}"] for i in range(N_STATIONS)]


def cmd_stations(args):
    cell, aset = int(args.cell), int(args.set)
    tag = CELLS[cell]
    datadirs = args.datadir
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    wl, Vl, order = obs0.load_system(_find(f"eigen_lsym_{tag}.npz", datadirs))
    Ew, Vw, order2 = obs0.load_system(_find(f"eigen_ham_{tag}.npz", datadirs))
    assert order == order2
    with open(_find(f"info_{tag}.json", datadirs)) as f:
        info = json.load(f)
    D = info["D"]
    g, _ = run_obs0.tag_graph(tag)
    assert sorted(g.nodes()) == order
    idx = {v: i for i, v in enumerate(order)}
    smap, snodes = sample_stations(len(order), cell, aset)
    sidx = [idx[v] for v in snodes]

    pairs = {}
    for a in range(N_STATIONS):
        tj = [sidx[b] for b in range(N_STATIONS) if b != a]
        tD, tCFD = diff_readouts(wl, Vl, sidx[a], tj, D)
        tW = obs0.arrival_times_wave(Ew, Vw, sidx[a], tj, D)
        for b in range(N_STATIONS):
            if b == a:
                continue
            pairs[f"S{a}|S{b}"] = {
                "W": tW[sidx[b]], "D": tD[sidx[b]], "P": None,
                "Dcfd": tCFD[sidx[b]]}

    # Static channel: one sparse prebuilt H, one CG solve per station source.
    h = sparse.csc_matrix(hamiltonian(g, order=order))
    z = max(dict(g.degree()).values())
    omega = obs0r.omega_below_edge(z)
    assert is_gap_ok(h, omega), f"gap fail {tag} omega={omega}"
    n = h.shape[0]
    a_full = (h - omega * sparse.eye(n)).tocsc()
    worst_res = 0.0
    for a in range(N_STATIONS):
        phi = static_phi_cg(h, sidx[a], omega)
        res = a_full @ phi
        bulk = np.ones(n, dtype=bool)
        bulk[sidx[a]] = False
        den = float(np.linalg.norm((h[bulk, :][:, [sidx[a]]]).toarray()))
        worst_res = max(worst_res, float(np.linalg.norm(res[bulk])) / den
                        if den > 0 else float("nan"))
        for b in range(N_STATIONS):
            if b == a:
                continue
            v = float(phi[sidx[b]])
            pairs[f"S{a}|S{b}"]["P"] = v if np.isfinite(v) else None

    meas = {"cell": cell, "set": aset, "n": N_STATIONS, "pairs": pairs}
    audit_meas_schema(meas)
    with open(os.path.join(outdir,
                           f"obs1_meas_cell{cell}_s{aset}.json"), "w") as f:
        json.dump(run_obs0.jsonable(meas), f)
    seal = {"cell": cell, "set": aset, "tag": tag,
            "seed": STATION_SEED_BASE + 100 * cell + aset,
            "stations": smap}
    with open(os.path.join(outdir,
                           f"obs1_seal_cell{cell}_s{aset}.json"), "w") as f:
        json.dump(seal, f)
    cw = sum(1 for r in pairs.values() if r["W"] is not None) / len(pairs)
    cd = sum(1 for r in pairs.values() if r["D"] is not None) / len(pairs)
    cp = sum(1 for r in pairs.values() if r["P"] is not None) / len(pairs)
    cc = sum(1 for r in pairs.values() if r["Dcfd"] is not None) / len(pairs)
    print(f"stations cell={cell} ({tag}) set={aset}: "
          f"W={cw:.4f} D={cd:.4f} P={cp:.4f} Dcfd={cc:.4f} "
          f"resid={worst_res:.1e}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="unit", required=True)
    p = sub.add_parser("eigen")
    p.add_argument("--tag", required=True)
    p.add_argument("--outdir", required=True)
    p = sub.add_parser("stations")
    p.add_argument("--cell", type=int, required=True)
    p.add_argument("--set", type=int, required=True)
    p.add_argument("--datadir", action="append", required=True)
    p.add_argument("--outdir", required=True)
    args = ap.parse_args()
    {"eigen": cmd_eigen, "stations": cmd_stations}[args.unit](args)


if __name__ == "__main__":
    main()
