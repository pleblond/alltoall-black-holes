"""WEAVE-0 campaign battery (runner; verdicts filed by weave0_analyze.py).

Preregistered grid (WEAVE0-PREREG, docs/weave0-prereg.md):
  construct  Stage-A verification + regime + meta per tag.
  dim        Stages B+C: BFS V(r)/d_eff + dense-eig spectral dimension.
  stations   Stage-D blind records (10 frozen cells x 3 sets, opaque).
  spread     Stages E/F: intrinsic-shell R/I impulse peaks + exponents.
  packet     G-a/G-aniso in-sheet packets (velocity, reversal, norm).
  transverse G-t cross-sheet arrival scaling (C1 vs C2 washout).
  switch     G-d source-switch front (filed physicality).
  hidden     Stage H: derived null census + HIDDEN battery + ledgers.
  vacuum     Stage I: JOINT vacuum compatibility + gap + stability.

Each task evolves under frozen H = -A ONLY. No fitting, no steering, no
selection. One JSON part per task lands in OUTDIR (default data/weave0).
"""

import argparse
import json
import math
import os
import sys
import warnings

import networkx as nx
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from bh_graph import dim3, obs0, obs0r, weave0  # noqa: E402
from bh_graph import response as R  # noqa: E402
from bh_graph.ballistic import (com, evolve_fixed, fit_velocity,  # noqa: E402
                                hamiltonian, index_of,
                                is_normalized_ok, node_order, unwrap_trace)
from bh_graph.continuum import j2_group_velocity  # noqa: E402
from bh_graph.driven import is_gap_ok  # noqa: E402
from scipy import sparse  # noqa: E402

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

N_STATIONS = 64
STATION_SEED_BASE = 9100
T_END = 16.0
DT = 0.05
SPREAD_AMP = 1e-3
SPREAD_REL_THETA = 1e-3
SPREAD_FLOORS = {"psi": 1e-12, "rho": 1e-14, "bond": 1e-14}
SPREAD_VMAX = 8.0  # banked in-sheet J2 Bloch-Manhattan bound
PACKET_SIGMA_FRAC = 6.0  # sigma = L/6 (Amd-1 A4 rule)
PACKET_T = 4.0
PACKET_K = 0.3


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, np.ndarray):
        return [jsonable(v) for v in o.tolist()]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        v = float(o)
        return v if np.isfinite(v) else None
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, float) and not np.isfinite(o):
        return None
    if isinstance(o, complex):
        return {"re": float(o.real), "im": float(o.imag)}
    return o


# ---------------------------------------------------------------------------
# Frozen task grid
# ---------------------------------------------------------------------------

def _c2_tags(sl, lams, seeds):
    S, L = sl
    return [f"c2-S{S}L{L}-lam{sh}-s{sd}" for sh in lams for sd in seeds]


LAM_SH = {"0.001": "0001", "0.005": "0005", "0.01": "001", "0.02": "002",
          "0.04": "004", "0.08": "008", "0.16": "016"}


def dim_tags():
    tags = ["c0-j2L44", "c1-S8L16", "c3-j3L16", "c4-cbL16"]
    tags += _c2_tags((8, 16), ("0001", "0005", "001", "002", "004", "008",
                               "016"), weave0.WEAVE_SEEDS)
    tags += _c2_tags((8, 24), ("002", "004"), weave0.SCALE_SEEDS)
    tags += _c2_tags((16, 16), ("002", "004"), weave0.SCALE_SEEDS)
    for sd in weave0.DISC_SEEDS:
        tags.append(f"c2dense-S8L16-lam004-s{sd}")
        tags.append(f"c2er3-S8L16-lam004-s{sd}")
        tags.append(f"c2sq-S8L16-lam004-s{sd}")
    for sd in weave0.SCALE_SEEDS:
        tags.append(f"c2nb-S8L16-lam004-s{sd}")
    for sd in weave0.WEAVE_SEEDS:
        tags.append(f"c5-S8L16-lam004-s{sd}")
    return tags


def spread_tags():
    tags = ["c0-j2L28", "c4-cbL16", "c5-S8L16-lam004-s7"]
    for sh in ("001", "002", "004"):
        for sd in (7, 37):
            tags.append(f"c2-S8L16-lam{sh}-s{sd}")
    return tags


def packet_specs():
    specs = [("c0-j2L16", 0, "x", 1)]
    for ax, sg in (("x", 1), ("x", -1), ("y", 1), ("y", -1)):
        specs.append(("c1-S8L16", 0, ax, sg))
    for ax, sg in (("x", 1), ("x", -1), ("y", 1), ("y", -1)):
        specs.append(("c2-S8L16-lam004-s7", 0, ax, sg))
    specs.append(("c2-S8L16-lam004-s7", 3, "x", 1))
    for ax, sg in (("x", 1), ("x", -1)):
        specs.append(("c2-S8L16-lam004-s37", 0, ax, sg))
    return specs


def transverse_tags():
    return ["c1-S8L16", "c2-S8L16-lam004-s7", "c2-S8L16-lam004-s37",
            "c2-S8L16-lam002-s7"]


def switch_tags():
    return ["c1-S8L16", "c2-S8L16-lam004-s7"]


def hidden_tags():
    return ["c0-j2L16", "c1-S8L16", "c2-S8L16-lam004-s7",
            "c2-S8L16-lam004-s37", "c2-S8L16-lam002-s7", "c4-cbL16"]


def vacuum_tags():
    return hidden_tags()


def task_list():
    lines = []
    for t in dim_tags():
        lines.append(f"construct --tag {t}")
        lines.append(f"dim --tag {t}")
    for c in range(10):
        for s in range(3):
            lines.append(f"stations --cell {c} --set {s}")
    for t in spread_tags():
        for k in ("R", "I"):
            lines.append(f"spread --tag {t} --kind {k}")
    for (t, sh, ax, sg) in packet_specs():
        lines.append(f"packet --tag {t} --sheet {sh} --axis {ax} "
                     f"--sign {sg}")
    for t in transverse_tags():
        lines.append(f"transverse --tag {t}")
    for t in switch_tags():
        lines.append(f"switch --tag {t}")
    for t in hidden_tags():
        lines.append(f"hidden --tag {t}")
    for t in vacuum_tags():
        lines.append(f"vacuum --tag {t}")
    return lines


# ---------------------------------------------------------------------------
# construct
# ---------------------------------------------------------------------------

def cmd_construct(args):
    tag = args.tag
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    asm = weave0.build_tag(tag)
    g = asm["graph"]
    a = weave0.verify_stage_a(asm)
    reg = weave0.regime_of(asm)
    degs = [d for _, d in g.degree()]
    rec = {"tag": tag, "fam": asm["fam"], "n": g.number_of_nodes(),
           "e": g.number_of_edges(), "K": asm["K"],
           "K_target": asm["K_target"], "S": asm["S"], "L": asm["L"],
           "lam": asm["lam"], "seed": asm["seed"],
           "substrate": asm["substrate"], "meeting": asm["meeting"],
           "deg_min": int(min(degs)), "deg_max": int(max(degs)),
           "deg_mean": float(sum(degs) / len(degs)),
           "stage_a": a, "regime": reg}
    fn = os.path.join(outdir, f"weave0_construct_{tag}.json")
    with open(fn, "w") as f:
        json.dump(jsonable(rec), f)
    print(f"construct {tag}: A_PASS={a['A_PASS']} regime={reg['regime']} "
          f"K={asm['K']}/{asm['K_target']}", flush=True)


# ---------------------------------------------------------------------------
# dim (Stages B+C)
# ---------------------------------------------------------------------------

def _windows_for(asm):
    key = (asm["S"], asm["L"])
    if key in weave0.WINDOWS:
        return dict(weave0.WINDOWS[key])
    return dict(weave0.WINDOWS_C0)


def cmd_dim(args):
    tag = args.tag
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    asm = weave0.build_tag(tag)
    g = asm["graph"]
    order = asm["order"]
    assert weave0.is_stage_a_ok(asm), f"Stage-A fail {tag}"
    W = _windows_for(asm)
    D = obs0.intrinsic_diameter(g, order[0])
    wrap_hi = max(3, D // 2 - 1)
    glo = (W["glob"][0], min(W["glob"][1], wrap_hi))
    loc = (W["local"][0], min(W["local"][1], wrap_hi))
    # Stage B: BFS volumes from 8 frozen origins.
    org = weave0.stage_b_origins(asm)
    b_orig = {}
    deffs = {"far": [], "all": []}
    for grp in ("far", "near", "uni"):
        for v in org[grp]:
            prof = weave0.volume_profile(g, v)
            de = weave0.deff_curve(prof["vols"], prof["radii"])
            b_orig[str(v)] = {
                "grp": grp, "dmax": prof["dmax"],
                "local": weave0.window_fit(prof["radii"], prof["vols"],
                                           loc[0], loc[1]),
                "glob": weave0.window_fit(prof["radii"], prof["vols"],
                                          glo[0], glo[1]),
                "deff": [None if not np.isfinite(x) else float(x)
                         for x in de],
                "radii": [float(x) for x in prof["radii"]],
                "vols": [float(x) for x in prof["vols"]]}
            if grp == "far":
                deffs["far"].append(de)
            deffs["all"].append(de)
    rmax = max(len(d) for d in deffs["all"])
    rr = np.arange(rmax, dtype=float)
    seal = lambda arr: np.array([a if len(a) == rmax
                                 else np.pad(a.astype(float), (0, rmax - len(a)),
                                             constant_values=np.nan)
                                 for a in arr], dtype=float)
    with np.errstate(all="ignore"):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            deff_far_med = np.nanmedian(seal(deffs["far"]), axis=0)
            deff_all_med = np.nanmedian(seal(deffs["all"]), axis=0)
    lam = asm["lam"] if asm["lam"] > 0 else 0.01
    rc = weave0.crossover_radius(rr, deff_far_med)
    # Stage C: dense Lrw eigensystem + heat/origin ds.
    w, V = weave0.eigh_lrw(g, order)
    heat_local = weave0.heat_ds_window(w, weave0.T_GRID, *W["tlocal"])
    heat_glob = weave0.heat_ds_window(w, weave0.T_GRID, *W["tglob"])
    slide = weave0.sliding_ds_heat(w)
    pos = index_of(order)
    ori_ds = {}
    for v in org["all"]:
        ori_ds[str(v)] = {
            "local": weave0.origin_ds_window(w, V, pos[v], weave0.T_GRID,
                                             *W["tlocal"]),
            "glob": weave0.origin_ds_window(w, V, pos[v], weave0.T_GRID,
                                            *W["tglob"])}
    tc = weave0.crossover_radius(np.array(slide["t"]), np.array(slide["d"]))
    # Null census needs H eig (headline + controls only to bound cost).
    null = None
    if tag in ("c0-j2L44", "c1-S8L16", "c3-j3L16", "c4-cbL16") \
            or tag.startswith("c2-S8L16-lam004-s") or tag.startswith("c5-"):
        wh, Vh = weave0.eigh_ham(g, order)
        null = weave0.null_census(wh, Vh, asm)
    rec = {"tag": tag, "D": D, "wrap_hi": wrap_hi,
           "windows": {"local": list(loc), "glob": list(glo),
                       "tlocal": list(W["tlocal"]), "tglob": list(W["tglob"])},
           "origins": org, "B_origins": b_orig,
           "deff_far_med": [None if not np.isfinite(x) else float(x)
                            for x in deff_far_med],
           "deff_all_med": [None if not np.isfinite(x) else float(x)
                            for x in deff_all_med],
           "r_c": rc, "lw_pred": weave0.lw_pred(lam),
           "heat_local": heat_local, "heat_glob": heat_glob,
           "origin_ds": ori_ds, "sliding_ds": slide, "t_c": tc,
           "tw_pred": weave0.tw_pred(lam), "null": null,
           "lrw_evals": [float(x) for x in w[:64]]}
    fn = os.path.join(outdir, f"weave0_dim_{tag}.json")
    with open(fn, "w") as f:
        json.dump(jsonable(rec), f)
    print(f"dim {tag}: D={D} rc={rc} tc={tc} "
          f"heat=({heat_local['d']:.2f},{heat_glob['d']:.2f})", flush=True)


# ---------------------------------------------------------------------------
# stations (Stage D measurement)
# ---------------------------------------------------------------------------

def sample_stations(n_nodes, cell, aset):
    """FROZEN station draw: {S-id: node} + node list in S-order."""
    rng = np.random.default_rng(STATION_SEED_BASE + 100 * cell + aset)
    nodes = rng.choice(n_nodes, size=N_STATIONS, replace=False)
    order = rng.permutation(N_STATIONS)
    smap = {f"S{i}": int(nodes[order[i]]) for i in range(N_STATIONS)}
    return smap, [smap[f"S{i}"] for i in range(N_STATIONS)]


def audit_meas_schema(meas):
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


def cmd_stations(args):
    cell, aset = int(args.cell), int(args.set)
    tag = weave0.blind_cell_tag(cell)
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    asm = weave0.build_tag(tag)
    g = asm["graph"]
    order = node_order(g)
    assert order == list(range(len(order)))
    assert weave0.is_stage_a_ok(asm), f"Stage-A fail {tag}"
    D = obs0.intrinsic_diameter(g, order[0])
    h = sparse.csc_matrix(hamiltonian(g, order=order))
    lrw = dim3.lrw_matrix(g, order)
    z = max(dict(g.degree()).values())
    omega = obs0r.omega_below_edge(z)
    assert is_gap_ok(h, omega), f"gap fail {tag} omega={omega}"
    ts_w = obs0.wave_grid(D)
    ts_d = obs0.diffusion_grid(D)
    smap, snodes = sample_stations(len(order), cell, aset)
    sidx = [int(v) for v in snodes]
    a_full = (h - omega * sparse.eye(len(order))).tocsc()
    pairs = {}
    worst_res = 0.0
    for a in range(N_STATIONS):
        tj = [sidx[b] for b in range(N_STATIONS) if b != a]
        pw = dim3.krylov_wave_traces(h, sidx[a], tj, ts_w)
        pd = dim3.krylov_diff_traces(lrw, sidx[a], tj, ts_d)
        phi = dim3.static_phi_cg(h, sidx[a], omega)
        res = a_full @ phi
        bulk = np.ones(len(order), dtype=bool)
        bulk[sidx[a]] = False
        den = float(np.linalg.norm((h[bulk, :][:, [sidx[a]]]).toarray()))
        if den > 0:
            worst_res = max(worst_res, float(np.linalg.norm(res[bulk])) / den)
        for k, b in enumerate([x for x in range(N_STATIONS) if x != a]):
            v = float(phi[sidx[b]])
            pairs[f"S{a}|S{b}"] = {
                "W": obs0.threshold_crossing(pw[:, k], ts_w, obs0.THETA_WAVE),
                "D": obs0.threshold_crossing(pd[:, k], ts_d, obs0.THETA_WAVE),
                "P": v if np.isfinite(v) else None,
                "Dcfd": obs0.cfd_first_peak(pd[:, k], ts_d)}
    meas = {"cell": cell, "set": aset, "n": N_STATIONS, "pairs": pairs}
    audit_meas_schema(meas)
    with open(os.path.join(outdir, f"weave0_meas_cell{cell}_s{aset}.json"),
              "w") as f:
        json.dump(jsonable(meas), f)
    seal = {"cell": cell, "set": aset, "tag": tag,
            "seed": STATION_SEED_BASE + 100 * cell + aset,
            "stations": smap}
    with open(os.path.join(outdir, f"weave0_seal_cell{cell}_s{aset}.json"),
              "w") as f:
        json.dump(seal, f)
    cw = sum(1 for r in pairs.values() if r["W"] is not None) / len(pairs)
    cd = sum(1 for r in pairs.values() if r["D"] is not None) / len(pairs)
    cp = sum(1 for r in pairs.values() if r["P"] is not None) / len(pairs)
    print(f"stations cell={cell} ({tag}) set={aset}: D={D} "
          f"W={cw:.4f} D={cd:.4f} P={cp:.4f} resid={worst_res:.1e}",
          flush=True)


# ---------------------------------------------------------------------------
# spread (Stages E/F)
# ---------------------------------------------------------------------------

def spread_src(tag, asm):
    """Preregistered spread source: sheet 0, far-from-stitch preferred."""
    order = asm["order"]
    dts = weave0.dist_to_stub(asm)
    best = max(order, key=lambda v: (dts.get(v, -1), -v))
    return int(best)


def cmd_spread(args):
    tag, kind = args.tag, args.kind
    amp = SPREAD_AMP
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    asm = weave0.build_tag(tag)
    assert weave0.is_stage_a_ok(asm), f"Stage-A fail {tag}"
    g = asm["graph"]
    order = node_order(g)
    pos = index_of(order)
    h = R.hamiltonian(g, order)
    eu, ev = R.edge_index_arrays(g, order)
    src = spread_src(tag, asm)
    iu = pos[src]
    D = obs0.intrinsic_diameter(g, src)
    n_steps = int(round(T_END / DT))
    ts = np.arange(n_steps + 1) * DT
    eps = amp if kind == "R" else amp * 1j
    d0 = R.point_source(len(order), iu, complex(eps))
    rec_d = R.evolve(d0, h, DT, n_steps)
    rows_d = rec_d["psi"]
    rows = rows_d  # BG0 (no background)
    qs = weave0.intrinsic_shells(g, src)
    max_shell = max(qs)
    psi_tr = np.zeros((len(ts), max_shell + 1))
    rho_tr = np.zeros((len(ts), max_shell + 1))
    j_tr = np.zeros((len(ts), max_shell + 1))
    node_shell_of = {}
    for r, members in qs.items():
        for m in members:
            node_shell_of[m] = r
    bond_shells: dict = {}
    for e in range(len(eu)):
        s = min(node_shell_of[int(eu[e])], node_shell_of[int(ev[e])])
        bond_shells.setdefault(s, []).append(e)
    bmax = 0.0
    for t in range(len(ts)):
        a_d = np.abs(rows_d[t])
        drho = np.abs(R.node_density(rows[t]))
        b_full = R.bond_B(rows[t], eu, ev)
        j_full = R.bond_J(rows[t], eu, ev)
        bmax = max(bmax, float(np.abs(b_full).max()))
        dj = np.abs(j_full)
        for r, members in qs.items():
            if not members:
                continue
            m = np.asarray(members, dtype=int)
            psi_tr[t, r] = float(a_d[m].max())
            rho_tr[t, r] = float(drho[m].max())
        for r, members in bond_shells.items():
            m = np.asarray(members, dtype=int)
            j_tr[t, r] = float(dj[m].max())

    def analyze(tr, floor):
        rcap = min(max_shell, 16)
        remote_peak = max(float(tr[:, s].max()) for s in range(1, rcap + 1))
        theta = max(SPREAD_REL_THETA * remote_peak, floor)
        peaks, tstars, windows = {}, {}, {}
        for s in range(2, 11):
            if s > max_shell:
                continue
            win = weave0.weave_spread_window(s, D, SPREAD_VMAX)
            windows[s] = list(win) if win else None
            pk = R.peak_in_window(tr[:, s], ts, *win) if win else None
            if pk is None:
                continue
            if weave0.interior_peak_ok(tr[:, s], ts, pk["tstar"],
                                       pk["Rmax"], win[1], theta):
                peaks[s] = pk["Rmax"]
                tstars[s] = pk["tstar"]
        return {"theta": theta, "remote_peak": remote_peak, "peaks": peaks,
                "tstars": tstars, "windows": windows}

    a_psi = analyze(psi_tr, SPREAD_FLOORS["psi"])
    a_rho = analyze(rho_tr, SPREAD_FLOORS["rho"])
    a_j = analyze(j_tr, SPREAD_FLOORS["bond"])
    rec = {"tag": tag, "bg": "BG0", "kind": kind, "amp": amp, "src": src,
           "D": D, "T": T_END, "dt": DT, "n": len(order),
           "theta": {"psi": a_psi["theta"], "rho": a_rho["theta"],
                     "J": a_j["theta"]},
           "peaks": {"psi": a_psi["peaks"], "rho": a_rho["peaks"],
                     "J": a_j["peaks"]},
           "tstars": {"psi": a_psi["tstars"], "rho": a_rho["tstars"],
                      "J": a_j["tstars"]},
           "windows": a_psi["windows"], "bmax": bmax,
           "norms_drift": float(np.abs(rec_d["norms"]
                                       - rec_d["norms"][0]).max())}
    fn = os.path.join(outdir, f"weave0_spread_{tag}_BG0_{kind}.json")
    with open(fn, "w") as f:
        json.dump(jsonable(rec), f)
    print(f"spread {tag} {kind}: n_psi={len(a_psi['peaks'])} "
          f"n_rho={len(a_rho['peaks'])} n_J={len(a_j['peaks'])}", flush=True)


# ---------------------------------------------------------------------------
# packet (G-a/G-aniso)
# ---------------------------------------------------------------------------

def cmd_packet(args):
    tag, sheet, axis, sign = (args.tag, int(args.sheet), args.axis,
                              int(args.sign))
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    asm = weave0.build_tag(tag)
    assert weave0.is_stage_a_ok(asm), f"Stage-A fail {tag}"
    g = asm["graph"]
    order = node_order(g)
    h = hamiltonian(g, order=order)
    L = asm["L"]
    sigma = L / PACKET_SIGMA_FRAC
    r0 = (L / 4.0, L / 2.0)
    k = (sign * PACKET_K, 0.0) if axis == "x" else (0.0, sign * PACKET_K)
    psi0 = weave0.sheet_packet(asm, sheet, r0, k, sigma)
    assert is_normalized_ok(psi0), "packet norm"
    n_steps = int(round(PACKET_T / DT))
    ts = np.arange(n_steps + 1) * DT
    rec = evolve_fixed(psi0, h, DT, n_steps)
    rows = rec["psi"]
    coords2 = {v: (float(asm["coords"][v][1]), float(asm["coords"][v][2]))
               for v in order}
    rs = np.array([com(row, coords2, order, periods=(L, L)) for row in rows])
    rs_u = unwrap_trace(rs, periods=(L, L))
    fit = fit_velocity(rs_u, ts)
    v_bloch = j2_group_velocity(k[0], k[1])
    rec_out = {"tag": tag, "sheet": sheet, "axis": axis, "sign": sign,
               "k": list(k), "sigma": sigma, "T": PACKET_T,
               "v_fit": [float(x) for x in fit["v"]],
               "speed": float(np.linalg.norm(fit["v"])),
               "r2": float(fit["r2"]),
               "v_bloch": [float(x) for x in v_bloch],
               "bloch_speed": float(np.linalg.norm(v_bloch)),
               "norm_drift": float(np.abs(rec["norms"] - 1.0).max()),
               "com_0": [float(x) for x in rs_u[0]],
               "com_T": [float(x) for x in rs_u[-1]]}
    fn = os.path.join(outdir, f"weave0_packet_{tag}_sh{sheet}_{axis}{sign:+d}.json")
    with open(fn, "w") as f:
        json.dump(jsonable(rec_out), f)
    print(f"packet {tag} sh{sheet} {axis}{sign:+d}: v={rec_out['speed']:.3f} "
          f"bloch={rec_out['bloch_speed']:.3f} r2={rec_out['r2']:.3f}",
          flush=True)


# ---------------------------------------------------------------------------
# transverse (G-t)
# ---------------------------------------------------------------------------

def cmd_transverse(args):
    tag = args.tag
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    asm = weave0.build_tag(tag)
    assert weave0.is_stage_a_ok(asm), f"Stage-A fail {tag}"
    g = asm["graph"]
    order = node_order(g)
    pos = index_of(order)
    h = hamiltonian(g, order=order)
    M = asm["M"]
    L = asm["L"]
    src = 0 * M + ((L // 4) * L + L // 2) * 2 + 0
    fam = asm["fam"]
    if fam == "c1":
        ring = list(range(asm["S"]))
    else:
        ring = list(asm["ring"])
        i0 = ring.index(0)
        ring = ring[i0:] + ring[:i0]
    T = 64.0
    ts = np.arange(int(round(T / DT)) + 1) * DT
    # Peak-arrival instrument (threshold-free; Amd-0 rule): per-sheet-k max
    # trace, first local-max peak time via interior-peak logic on the full
    # horizon; threshold-crossing (1e-3 rel) filed as secondary.
    from scipy.sparse.linalg import expm_multiply

    n = h.shape[0]
    psi0 = np.zeros(n, dtype=np.complex128)
    psi0[pos[src]] = 1.0
    sheets_idx = [weave0.sheet_nodes_of(asm, s) for s in ring]
    traces = {k: np.zeros(len(ts)) for k in range(1, min(5, len(ring)))}
    psi = psi0.copy()
    for k in traces:
        traces[k][0] = float(np.abs(psi[sheets_idx[k]]).max())
    row = 1
    while row < len(ts):
        seg = min(256, len(ts) - row)
        if seg == 1:
            tail = np.asarray(expm_multiply(-1.0j * h * DT, psi),
                              dtype=np.complex128).reshape(1, -1)
        else:
            tail = expm_multiply(-1.0j * h, psi, start=DT, stop=seg * DT,
                                 num=seg)
            tail = np.asarray(tail, dtype=np.complex128)
        for k in traces:
            traces[k][row:row + seg] = np.abs(
                tail[:, sheets_idx[k]]).max(axis=1)
        psi = tail[-1, :]
        row += seg
    peak_t, cross_t = {}, {}
    for k, tr in traces.items():
        t_cfd = obs0.cfd_first_peak(tr, ts)  # banked CFD (frac 1/2)
        peak_t[k] = None
        if t_cfd is not None:
            kidx = int(np.argmin(np.abs(ts - t_cfd)))
            if weave0.interior_peak_ok(tr, ts, ts[kidx], tr[kidx], T, 1e-12):
                peak_t[k] = float(ts[kidx])
        rp = float(tr.max())
        cross_t[k] = R.arrival_time(tr, ts, max(1e-3 * rp, 1e-12))
    rec = {"tag": tag, "src": src, "ring": ring, "T": T,
           "peak_t": peak_t, "cross_t": cross_t,
           "remote_peak": {k: float(traces[k].max()) for k in traces}}
    fn = os.path.join(outdir, f"weave0_transverse_{tag}.json")
    with open(fn, "w") as f:
        json.dump(jsonable(rec), f)
    print(f"transverse {tag}: peak={peak_t} cross={cross_t}", flush=True)


# ---------------------------------------------------------------------------
# switch (G-d, filed physicality)
# ---------------------------------------------------------------------------

def cmd_switch(args):
    tag = args.tag
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    asm = weave0.build_tag(tag)
    assert weave0.is_stage_a_ok(asm), f"Stage-A fail {tag}"
    g = asm["graph"]
    order = node_order(g)
    pos = index_of(order)
    h = hamiltonian(g, order=order)
    src = spread_src(tag, asm)
    qs = weave0.intrinsic_shells(g, src)
    T = 16.0
    ts = np.arange(int(round(T / DT)) + 1) * DT
    # Source-switch: steady drive then release; front = first 1e-3 crossing
    # per shell of the release transient (physicality: v < Vmax filed).
    psi0 = np.zeros(len(order), dtype=np.complex128)
    psi0[pos[src]] = 1.0
    rec = R.evolve(psi0, h, DT, int(round(T / DT)))
    rows = rec["psi"]
    max_shell = min(max(qs), 10)
    tr = np.zeros((len(ts), max_shell + 1))
    for r in range(max_shell + 1):
        m = np.asarray(qs.get(r, []), dtype=int)
        if len(m):
            tr[:, r] = np.abs(rows[:, m]).max(axis=1)
    rp = max(float(tr[:, s].max()) for s in range(1, max_shell + 1))
    theta = max(1e-3 * rp, 1e-12)
    arrivals = {s: R.arrival_time(tr[:, s], ts, theta)
                for s in range(2, max_shell + 1)}
    use = [s for s in arrivals if arrivals[s] is not None]
    front = R.front_velocity({s: arrivals[s] for s in use}, use) \
        if len(use) >= 3 else {"v": None, "r2": None, "n": 0}
    rec_out = {"tag": tag, "src": src, "arrivals": arrivals, "front": front,
               "vmax_bound": SPREAD_VMAX,
               "physical": (front["v"] is not None
                            and front["v"] < SPREAD_VMAX)}
    fn = os.path.join(outdir, f"weave0_switch_{tag}.json")
    with open(fn, "w") as f:
        json.dump(jsonable(rec_out), f)
    print(f"switch {tag}: v={front['v']} physical={rec_out['physical']}",
          flush=True)


# ---------------------------------------------------------------------------
# hidden (Stage H)
# ---------------------------------------------------------------------------

def _krylov_diff_tv(lrw, pA, pB, shells_idx, ts):
    """Exact per-shell TV Dmax between diffused distributions (TRUE Lrw).

    Krylov evolution of both distributions under generator -Lrw (exact on
    irregular graphs, where eigen-Lrw is non-orthogonal; coincides with the
    banked eigen method on regular graphs, pinned in tests on C0).
    Returns {r: Dmax(r)} over nonempty shells.
    """
    from scipy.sparse.linalg import expm_multiply

    gen = -sparse.csr_matrix(np.asarray(lrw.todense()
                                        if sparse.issparse(lrw) else lrw),
                             dtype=float)
    ts = np.asarray(ts, dtype=float)
    dt = float(ts[1] - ts[0])
    pA = np.asarray(pA, dtype=float)
    pB = np.asarray(pB, dtype=float)
    acc = {int(r): 0.0 for r, m in shells_idx.items() if len(m)}

    def tv_at(a, b):
        for r, m in shells_idx.items():
            m = np.asarray(m, dtype=int)
            if not len(m):
                continue
            tv = 0.5 * float(np.abs(a[m] - b[m]).sum())
            if tv > acc[int(r)]:
                acc[int(r)] = tv

    tv_at(pA, pB)
    a, b = pA.copy(), pB.copy()
    row = 1
    while row < len(ts):
        seg = min(256, len(ts) - row)
        if seg == 1:
            a = np.asarray(expm_multiply(gen * dt, a), dtype=float).ravel()
            b = np.asarray(expm_multiply(gen * dt, b), dtype=float).ravel()
            tv_at(a, b)
        else:
            ta = np.asarray(expm_multiply(gen, a, start=dt, stop=seg * dt,
                                          num=seg), dtype=float)
            tb = np.asarray(expm_multiply(gen, b, start=dt, stop=seg * dt,
                                          num=seg), dtype=float)
            for k in range(seg):
                tv_at(ta[k], tb[k])
            a, b = ta[-1], tb[-1]
        row += seg
    return acc


def cmd_hidden(args):
    tag = args.tag
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    asm = weave0.build_tag(tag)
    assert weave0.is_stage_a_ok(asm), f"Stage-A fail {tag}"
    from bh_graph import hidden as H
    from bh_graph import hiddenbr as HBR

    g = asm["graph"]
    order = node_order(g)
    pos = index_of(order)
    n = len(order)
    h = hamiltonian(g, order=order)
    h_csc = sparse.csc_matrix(h)
    eu, ev = R.edge_index_arrays(g, order)
    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    fam = asm["fam"]
    out: dict = {"tag": tag}
    # H-der: null census (H eig) + sector mixing.
    wh, Vh = weave0.eigh_ham(g, order)
    out["null"] = weave0.null_census(wh, Vh, asm)
    out["mix"] = weave0.sheet_sector_mixing(asm)
    if fam not in ("c0", "c1", "c2"):
        fn = os.path.join(outdir, f"weave0_hidden_{tag}.json")
        with open(fn, "w") as f:
            json.dump(jsonable(out), f)
        print(f"hidden {tag}: der-only", flush=True)
        return
    # H-bat: banked-verbatim sign leg (Amendment-1 A6 rules): uniform
    # background + pure-hidden delta on sheet 0 far from stitches, RAW
    # (no rescaling). Remote readouts split in-sheet vs cross-sheet
    # (Amd-0: inter-sheet coupling breaks exact P_- death by design, so
    # intrinsic-mixed shells cannot be gated; the split measures leakage).
    L = asm["L"]
    dts = weave0.dist_to_stub(asm)
    coords = asm["coords"]
    # Prep cell: sheet-0 cell maximizing min endpoint-distance over BOTH bits
    # (Amd-0 rule: neither bit may be a stitch endpoint, so the hidden delta
    # is an exact E=0 eigenstate and Dp an exact Lrw eigenmode).
    node_of = {(c[0], c[1], c[2], c[3]): v for v, c in coords.items()}
    cands = [v for v in order if coords[v][0] == 0 and coords[v][3] == 0]
    L_sheet = asm["L"]

    def _cell_key(v):
        c = coords[v]
        mate = node_of[(0, c[1], c[2], 1)]
        return (min(dts.get(v, -1), dts.get(mate, -1)), -v)

    src_cell_node = max(cands, key=_cell_key)
    mate = node_of[(0, coords[src_cell_node][1], coords[src_cell_node][2], 1)]
    prep_dts = [dts.get(src_cell_node, -1), dts.get(mate, -1)]
    cx, cy = coords[src_cell_node][1], coords[src_cell_node][2]
    plus = H.symmetric_uniform(n)
    minus = weave0.sheet_hidden_delta(asm, 0, (cx, cy))
    pr = weave0.sheet_sector_projectors(asm, 0)
    p = H.matched_pair(plus, minus, "sign")
    A, B = p["psi_A"], p["psi_B"]
    pm = HBR.is_pair_pplus_ok(A, B, pr)
    pplus_max = float(np.abs(
        np.asarray(pr["P_sym"], dtype=float) @ (A - B)).max())
    erep = HBR.pair_energy_report(A, B, p["psi_plus"], p["minus_A"],
                                  p["minus_B"], h)
    eok = HBR.is_pair_energy_ok(erep)
    d_full = dict(nx.single_source_shortest_path_length(g, src_cell_node))
    nodes_r = np.asarray(sorted(pos[v] for v in order
                                if d_full.get(v, 99) <= 2), dtype=int)
    in_r = np.zeros(n, dtype=bool)
    in_r[nodes_r] = True
    emask = in_r[eu] & in_r[ev]
    loc = H.local_distance(A, B, eu, ev, nodes_r, emask)
    Ew, Vw, _ = obs0.hamiltonian_system(g, order)
    D = obs0.intrinsic_diameter(g, order[0])
    ts_w = obs0.wave_grid(D)
    ts_d = obs0.diffusion_grid(D)
    shells = weave0.intrinsic_shells(g, src_cell_node)
    on_sheet0 = np.array([coords[v][0] == 0 for v in order])
    sh_in = {r: [i for i in m if on_sheet0[i]] for r, m in shells.items()}
    sh_x = {r: [i for i in m if not on_sheet0[i]] for r, m in shells.items()}
    rem_in = [r for r in sh_in if r >= 2 and len(sh_in[r])]
    rem_x = [r for r in sh_x if r >= 2 and len(sh_x[r])]
    rw_in = H.remote_tv_wave(A, B, Ew, Vw, sh_in, ts_w) if rem_in else {"Dmax": {}}
    rw_x = H.remote_tv_wave(A, B, Ew, Vw, sh_x, ts_w) if rem_x else {"Dmax": {}}
    lrw = dim3.lrw_matrix(g, order)
    rd_in = _krylov_diff_tv(lrw, np.abs(A) ** 2, np.abs(B) ** 2, sh_in, ts_d)
    rd_x = _krylov_diff_tv(lrw, np.abs(A) ** 2, np.abs(B) ** 2, sh_x, ts_d)
    z = max(dict(g.degree()).values())
    omega = obs0r.omega_below_edge(z)
    mate = [v for v in order if coords[v][:3] == (0, cx, cy)
            and coords[v][3] == 1][0]
    assert mate == node_of[(0, cx, cy, 1)]
    pf = H.pot_pair_fields(h_csc, (pos[src_cell_node], pos[mate]), A, B,
                           omega)
    dphi = np.asarray(pf["dphi"], dtype=float)
    rem_in_idx = np.concatenate([np.asarray(sh_in[r], dtype=int)
                                 for r in rem_in]) if rem_in else np.zeros(0, dtype=int)
    rem_x_idx = np.concatenate([np.asarray(sh_x[r], dtype=int)
                                for r in rem_x]) if rem_x else np.zeros(0, dtype=int)
    oA = HBR.bond_fields(A, eu, ev)
    oB = HBR.bond_fields(B, eu, ev)
    db = HBR.delta_b_census(oA["B"], oB["B"])
    lc = HBR.ledger_census(g, order, A, B, eu, ev)
    out["bat"] = {
        "cell": [cx, cy], "prep_dts": [float(x) for x in prep_dts],
        "prep_clean": bool(min(prep_dts) >= 1),
        "pmatch": bool(pm), "pplus_max": pplus_max,
        "dQ": float(abs(H.total_Q(A) - H.total_Q(B))),
        "E_A": erep["E_A"], "E_B": erep["E_B"], "dE": erep["dE"],
        "E_ok": bool(eok),
        "local": loc,
        "local_ok": bool(H.is_locally_distinguishable_ok(loc["D"])),
        "wave_in": {str(r): rw_in["Dmax"].get(r) for r in rem_in},
        "wave_x": {str(r): rw_x["Dmax"].get(r) for r in rem_x},
        "wave_in_ok": bool(H.is_remote_blind_ok(rw_in["Dmax"], rem_in))
        if rem_in else True,
        "wave_x_ok": bool(H.is_remote_blind_ok(rw_x["Dmax"], rem_x))
        if rem_x else True,
        "diff_in": {str(r): rd_in.get(r) for r in rem_in},
        "diff_x": {str(r): rd_x.get(r) for r in rem_x},
        "diff_in_ok": bool(H.is_remote_blind_ok(rd_in, rem_in))
        if rem_in else True,
        "diff_x_ok": bool(H.is_remote_blind_ok(rd_x, rem_x))
        if rem_x else True,
        "pot_in_max": float(np.abs(dphi[rem_in_idx]).max())
        if len(rem_in_idx) else 0.0,
        "pot_x_max": float(np.abs(dphi[rem_x_idx]).max())
        if len(rem_x_idx) else 0.0,
        "db_max": db["max_abs"], "db_n": db["n_changed"],
        "lc_n": lc["n_nonzero"], "lc_max": lc["max_abs"],
        "n_flip": lc["n_flips"],
    }
    # H-g: VMINUS-analog global pair (banked L:vminus precedent) on the G-a
    # packet background + staggered global pair (filed). Gate: texture pair
    # flips > 100 (inherited H-g bar).
    bg = weave0.sheet_packet(asm, 0, (L / 4.0, L / 2.0), (PACKET_K, 0.0),
                             L / PACKET_SIGMA_FRAC)
    tex = weave0.sheet_vminus_texture(asm)
    pv = H.matched_pair(bg, tex, "sign")
    lc_g = HBR.ledger_census(g, order, pv["psi_A"], pv["psi_B"], eu, ev)
    n_flip = int(lc_g["n_flips"])
    stag = weave0.stag_state(asm)
    ps = H.matched_pair(bg, stag, "sign")
    lc_s = HBR.ledger_census(g, order, ps["psi_A"], ps["psi_B"], eu, ev)
    out["hg"] = {"n_flip": n_flip, "gate100": bool(n_flip > 100),
                 "lc_n": int(lc_g["n_nonzero"]),
                 "stag_n_flip": int(lc_s["n_flips"]),
                 "stag_lc_n": int(lc_s["n_nonzero"])}
    fn = os.path.join(outdir, f"weave0_hidden_{tag}.json")
    with open(fn, "w") as f:
        json.dump(jsonable(out), f)
    print(f"hidden {tag}: local={out['bat']['local']['D']:.1e} "
          f"hg_flips={n_flip}", flush=True)


# ---------------------------------------------------------------------------
# vacuum (Stage I)
# ---------------------------------------------------------------------------

def cmd_vacuum(args):
    tag = args.tag
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    asm = weave0.build_tag(tag)
    assert weave0.is_stage_a_ok(asm), f"Stage-A fail {tag}"
    from bh_graph import vacfield as vf

    g = asm["graph"]
    order = node_order(g)
    pos = index_of(order)
    n = len(order)
    h = hamiltonian(g, order=order)
    eu, ev = R.edge_index_arrays(g, order)
    eu_np = np.asarray(eu, dtype=int)
    ev_np = np.asarray(ev, dtype=int)
    perron = weave0.perron_state(h)
    e_per = vf.rayleigh_energy(perron, h)
    res_per = vf.eigen_residual(perron, h, e_per)
    # I-a stationarity drift (Krylov, inherited bar).
    stat = vf.stationarity_run(perron, h, eu_np, ev_np)
    # I-b JOINT rungs.
    sub = {"graph": g, "order": order}
    cur = vf.current_census(perron, sub, eu_np, ev_np, plaquettes=[])
    ph = vf.phase_invariance(perron, g, order, eu_np, ev_np)
    sc = vf.amplitude_scaling(perron / np.linalg.norm(perron), g, order,
                              eu_np, ev_np)
    # Stress uniformity filed (expected non-uniform: irregular graph).
    from bh_graph.vacfield import incident_stats, rho_of

    rho = rho_of(perron)
    # I-c ledgers.
    from bh_graph import hiddenbr as HBR

    led_p = HBR.ledger_array(g, perron, order, eu_np, ev_np)
    stag = weave0.stag_state(asm) if asm.get("bipart") else None
    led_s = HBR.ledger_array(g, stag, order, eu_np, ev_np) \
        if stag is not None else None

    def led_frac(led):
        if led is None:
            return None
        a = np.asarray(led, dtype=float)
        tot = a.size
        return {"fneg": float(np.sum(a < 0)) / tot,
                "fpos": float(np.sum(a > 0)) / tot,
                "fzero": float(np.sum(a == 0)) / tot, "n": int(tot)}

    # I-d gap + excitation stability.
    wh, _ = weave0.eigh_ham(g, order)
    wsort = np.sort(np.asarray(wh, dtype=float))
    gap = float(wsort[1] - wsort[0]) if len(wsort) > 1 else float("nan")
    iu = pos[spread_src(tag, asm)]
    stab = weave0.excitation_stability(h, perron, iu)
    # I-e texture drift (filed).
    tex = None
    if asm.get("substrate") == "j2":
        tex_state = weave0.sheet_vminus_texture(asm)
        tex = vf.stationarity_run(tex_state, h, eu_np, ev_np)
    out = {"tag": tag, "E_perron": float(e_per), "res_perron": float(res_per),
           "stationarity": stat,
           "current": cur, "phase": ph, "scaling": sc,
           "rho_std": float(np.std(rho)), "rho_mean": float(np.mean(rho)),
           "ledger_perron": led_frac(led_p), "ledger_stag": led_frac(led_s),
           "gap": gap, "stability": stab, "texture": tex}
    fn = os.path.join(outdir, f"weave0_vacuum_{tag}.json")
    with open(fn, "w") as f:
        json.dump(jsonable(out), f)
    print(f"vacuum {tag}: E={e_per:.4f} res={res_per:.1e} gap={gap:.2e}",
          flush=True)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="task", required=True)
    p = sub.add_parser("construct")
    p.add_argument("--tag", required=True)
    p.add_argument("--outdir", default="data/weave0")
    p = sub.add_parser("dim")
    p.add_argument("--tag", required=True)
    p.add_argument("--outdir", default="data/weave0")
    p = sub.add_parser("stations")
    p.add_argument("--cell", required=True)
    p.add_argument("--set", required=True)
    p.add_argument("--outdir", default="data/weave0")
    p = sub.add_parser("spread")
    p.add_argument("--tag", required=True)
    p.add_argument("--kind", required=True, choices=("R", "I"))
    p.add_argument("--outdir", default="data/weave0")
    p = sub.add_parser("packet")
    p.add_argument("--tag", required=True)
    p.add_argument("--sheet", required=True)
    p.add_argument("--axis", required=True, choices=("x", "y"))
    p.add_argument("--sign", required=True)
    p.add_argument("--outdir", default="data/weave0")
    p = sub.add_parser("transverse")
    p.add_argument("--tag", required=True)
    p.add_argument("--outdir", default="data/weave0")
    p = sub.add_parser("switch")
    p.add_argument("--tag", required=True)
    p.add_argument("--outdir", default="data/weave0")
    p = sub.add_parser("hidden")
    p.add_argument("--tag", required=True)
    p.add_argument("--outdir", default="data/weave0")
    p = sub.add_parser("vacuum")
    p.add_argument("--tag", required=True)
    p.add_argument("--outdir", default="data/weave0")
    sub.add_parser("print-all")
    args = ap.parse_args()
    if args.task == "print-all":
        for line in task_list():
            print(line)
        return
    fn = {"construct": cmd_construct, "dim": cmd_dim,
          "stations": cmd_stations, "spread": cmd_spread,
          "packet": cmd_packet, "transverse": cmd_transverse,
          "switch": cmd_switch, "hidden": cmd_hidden,
          "vacuum": cmd_vacuum}[args.task]
    fn(args)


if __name__ == "__main__":
    main()
