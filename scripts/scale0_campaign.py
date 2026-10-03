"""SCALE-0 scaling-bank campaign runner (frozen per SCALE0-PREREG; beast only).

Units (one process each, parallelized via xargs):
  obs_replay     banked L<=128 read-only replay + Krylov validation subset
  obs_hausdorff  BFS Hausdorff dimension (16 frozen origins)
  obs_krylov     Krylov d_s + wave/diffusion taus at one origin
  obs_dim        operational dimension (banked replay L<=128; rebuild L>=256)
  resp           RESPONSE scaling cell (windowed pre/post analysis)
  resp_regress   L=28 headline replay (banked parity)
  p1             packet scaling cell (velocity/dispersion/directional order)
  p1_regress     C5 replication (banked parity)
  pot            static range/floor/all-path cell (CG)
  pot_regress    L=28 CG-vs-spsolve + banked range/xi
  quot           QUOT scaling cell (wave pre+post, diffusion pre, POT)
  quot_regress   L=28 algebra + wave replay (banked parity)
  zero           ZERO scaling cell (streamed screening + refinement)
  zero_regress   banked headon replay + refine determinism
  vacexc         VAC-EXC scaling cell (cross-bg / frac-ladder)
  vacexc_regress L=4 bitwise + L=28 frac/packet replay
  vaccomp        VAC-COMP scaling cell (formula + ladder + circle + amps)
  vaccomp_regress L=4 census + L=8 extremal rows

All randomness/seeds come from the frozen banked modules. Rows are NEVER
stored at L >= 64 (P7); arrivals/Rmax/fits run full-rate internally and
only decimated traces are kept (P4).
"""

import argparse
import json
import math
import os
import socket
import subprocess
import sys
import time

import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from bh_graph import obs0, obs1, scale0  # noqa: E402

BANKED_OBS0 = os.environ.get("SCALE0_BANKED_OBS0", os.path.expanduser("~/obs0-data"))
BANKED_OBS0R = os.environ.get("SCALE0_BANKED_OBS0R", os.path.expanduser("~/obs0r-data"))
BANKED_OBS1 = os.environ.get("SCALE0_BANKED_OBS1", os.path.expanduser("~/obs1-data"))

REPLAY_TAGS = ("j2-L28", "sq-L28", "j2-L64", "sq-L64", "j2-L128", "sq-L128")
OBS1_CELLS = {"j2-L64": 1, "j2-L128": 2, "sq-L64": 4, "sq-L128": 5}
DIM_NEW_CELLS = {("j2", 256): 100, ("sq", 256): 101,
                 ("j2", 512): 102, ("sq", 512): 103}
P1_KS = {"k03": (0.3, 0.0), "k05": (0.5, 0.0)}
RESP_BG = {"BG0": 1.0, "BG+": 1e-3}
FIT_SHELLS = (2, 3, 4, 5, 6, 7, 8, 9, 10)
CHUNK = 128
CHUNK_BIG = 64


def _git_rev() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, cwd=os.path.dirname(__file__)).stdout.strip()
    except Exception:
        return "unknown"


def jsonable(o):
    if isinstance(o, np.ndarray):
        return [jsonable(v) for v in o.tolist()]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        v = float(o)
        return v if np.isfinite(v) else None
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, float) and not np.isfinite(o):
        return None
    return o


def _banked_dir_for(tag: str) -> str:
    fam, rest = tag.split("-")
    L = int(rest[1:])
    if L <= 64:
        return BANKED_OBS0
    return BANKED_OBS0R


def _tag_sub(tag: str) -> str:
    return "j2" if tag.startswith("j2") else "sq"


def _tag_L(tag: str) -> int:
    return int(tag.split("-")[1][1:])


# ---------------------------------------------------------------------------
# obs_replay
# ---------------------------------------------------------------------------

def run_obs_replay(tag: str) -> dict:
    import networkx as nx

    t0 = time.time()
    sub, L = _tag_sub(tag), _tag_L(tag)
    bdir = _banked_dir_for(tag)
    with open(os.path.join(bdir, f"info_{tag}.json")) as f:
        info = json.load(f)
    g = scale0.build_graph(sub, L)
    order = scale0.node_order(g)
    si = 0 if sub == "j2" else 1
    degs = [g.degree(v) for v in order]
    topo = {"N_ok": len(order) == info["N"], "D_ok": True,
            "conn": bool(nx.is_connected(g)),
            "deg_min": min(degs), "deg_max": max(degs)}
    D = obs0.intrinsic_diameter(g, order[0])
    topo["D"] = D
    topo["D_ok"] = bool(D == info["D"])
    origins = obs0.sample_origins(len(order), si, L)
    # Fresh BFS d_H vs banked origin records (independent recomputation).
    dh_fresh, dh_banked, ds_banked = [], [], []
    for o_pos in range(len(origins)):
        fn = os.path.join(bdir, f"origin_{tag}_o{o_pos}.json")
        with open(fn) as f:
            rec = json.load(f)
        dh_banked.append(rec["hausdorff"]["d"])
        ds_banked.append(rec["ds_origin"]["d"])
        dh_fresh.append(obs0.hausdorff_dim(g, order[origins[o_pos]])["d"])
    dh_dev = float(np.nanmax(np.abs(np.asarray(dh_fresh) - np.asarray(dh_banked))))
    # Krylov validation subset: 4 origins (d_s + wave taus on 5 targets).
    h = scale0.hamiltonian(g, order)
    lrw = scale0.lrw_operator(g, order)
    ts_w = obs0.wave_grid(D)
    ds_dev, tau_pairs = [], []
    idx = {v: i for i, v in enumerate(order)}
    for o_pos in range(4):
        origin = order[origins[o_pos]]
        fn = os.path.join(bdir, f"origin_{tag}_o{o_pos}.json")
        with open(fn) as f:
            rec = json.load(f)
        ts = np.asarray(list(obs0.DS_TS), dtype=float)
        Pk = scale0.krylov_diffusion_return(lrw, idx[origin], ts)
        fit = obs0.fit_loglog(ts, Pk)
        ds_dev.append(abs(-2.0 * fit["p"] - rec["ds_origin"]["d"]))
        taus = rec["taus"]
        tgt_nodes = [int(v) for v in list(taus)[:5]]
        tj = [idx[v] for v in tgt_nodes]
        Pk = scale0.krylov_wave_traces_chunked(h, idx[origin], tj, ts_w,
                                               chunk_steps=256)
        for k, v in enumerate(tgt_nodes):
            t_banked = taus[str(v)]["tW"]
            t_k = obs0.threshold_crossing(Pk[:, k], ts_w, obs0.THETA_WAVE)
            tau_pairs.append({"banked": t_banked, "krylov": t_k})
    return {"tag": tag, "topo": topo, "info_heat": info["heat_ds"],
            "info_weyl": info["weyl"], "dh_dev": dh_dev,
            "dh_fresh_median": float(np.nanmedian(dh_fresh)),
            "ds_banked_median": float(np.nanmedian(ds_banked)),
            "krylov_ds_maxdev": float(max(ds_dev)) if ds_dev else None,
            "krylov_tau_pairs": tau_pairs,
            "elapsed": time.time() - t0}


# ---------------------------------------------------------------------------
# obs_hausdorff
# ---------------------------------------------------------------------------

def run_obs_hausdorff(sub: str, L: int) -> dict:
    t0 = time.time()
    g = scale0.build_graph(sub, L)
    order = scale0.node_order(g)
    si = 0 if sub == "j2" else 1
    origins = obs0.sample_origins(len(order), si, L)
    ds, r2s = [], []
    D = None
    win = None
    for o_pos in origins:
        rec = obs0.hausdorff_dim(g, order[o_pos])
        ds.append(rec["d"])
        r2s.append(rec["r2"])
        D = rec["D"]
        win = rec["window"]
    return {"sub": sub, "L": L, "D": D, "window": win,
            "d_median": float(np.nanmedian(ds)), "d_spread": float(np.nanmax(ds) - np.nanmin(ds)),
            "r2_min": float(np.nanmin(r2s)), "n": len(ds), "ds": [float(v) for v in ds],
            "elapsed": time.time() - t0}


# ---------------------------------------------------------------------------
# obs_krylov (one origin)
# ---------------------------------------------------------------------------

def run_obs_krylov(sub: str, L: int, oi: int) -> dict:
    t0 = time.time()
    g = scale0.build_graph(sub, L)
    order = scale0.node_order(g)
    idx = {v: i for i, v in enumerate(order)}
    si = 0 if sub == "j2" else 1
    origins = obs0.sample_origins(len(order), si, L)
    origin = order[origins[oi]]
    o_idx = idx[origin]
    import networkx as nx

    dist = dict(nx.single_source_shortest_path_length(g, origin))
    D = max(dist.values())
    # d_s via Krylov return.
    lrw = scale0.lrw_operator(g, order)
    ts = np.asarray(list(obs0.DS_TS), dtype=float)
    Pk = scale0.krylov_diffusion_return(lrw, o_idx, ts)
    fit = obs0.fit_loglog(ts, Pk)
    ds = -2.0 * fit["p"] if fit["n"] >= 3 else float("nan")
    # Wave taus on the frozen 75-target subset.
    h = scale0.hamiltonian(g, order)
    targets = obs0.sample_targets(dist, D, seed=obs0.TARGET_SEED_BASE + oi)
    tgt_nodes = list(targets.keys())
    tj = [idx[v] for v in tgt_nodes]
    ts_w = obs0.wave_grid(D)
    Pk = scale0.krylov_wave_traces_chunked(h, o_idx, tj, ts_w,
                                           chunk_steps=CHUNK_BIG if L >= 256 else CHUNK)
    taus = {}
    n_missing = 0
    for k, v in enumerate(tgt_nodes):
        t = obs0.threshold_crossing(Pk[:, k], ts_w, obs0.THETA_WAVE)
        taus[str(v)] = {"R": dist[v], "tW": t}
        if t is None:
            n_missing += 1
    out = {"sub": sub, "L": L, "oi": oi, "D": D, "ds": float(ds),
           "ds_r2": fit["r2"], "n_targets": len(tgt_nodes),
           "n_missing_wave": n_missing, "taus": taus}
    # Validation vs banked spectral at L <= 128.
    if L <= 128:
        tag = f"{sub}-L{L}"
        bdir = _banked_dir_for(tag)
        with open(os.path.join(bdir, f"origin_{tag}_o{oi}.json")) as f:
            rec = json.load(f)
        pairs = []
        for v in tgt_nodes:
            tb = rec["taus"][str(v)]["tW"]
            tk = taus[str(v)]["tW"]
            pairs.append({"banked": tb, "krylov": tk})
        out["banked_ds"] = rec["ds_origin"]["d"]
        out["val_tau_pairs"] = pairs
    # Restricted diffusion taus (r <= 16) at L >= 256.
    if L >= 256:
        near = [v for v in tgt_nodes if dist[v] <= 16]
        tj2 = [idx[v] for v in near]
        tmax = 3.0 * 16.0 ** 2
        n_steps = int(round(tmax / obs0.DT_DIFF))
        Pd = scale0.krylov_diffusion_stepped(lrw, o_idx, tj2, obs0.DT_DIFF, n_steps)
        ts_d = np.arange(n_steps + 1, dtype=float) * obs0.DT_DIFF
        tD = {}
        for k, v in enumerate(near):
            tD[str(v)] = {"R": dist[v],
                          "tD": obs0.cfd_first_peak(Pd[:, k], ts_d, obs0.CFD_FRAC)}
        out["tD_restricted"] = tD
        out["tD_rmax"] = 16
    out["elapsed"] = time.time() - t0
    return out


# ---------------------------------------------------------------------------
# obs_dim (blind-chain estimators on operational matrices)
# ---------------------------------------------------------------------------

def _blind_geometry(D: np.ndarray) -> dict:
    n = D.shape[0]
    vol = obs1.volume_dimension(D)
    stresses = {}
    tr = list(range(obs1.N_TRAIN))
    for d in obs1.MDS_DIMS:
        r = obs1.classical_mds(D[np.ix_(tr, tr)], d)
        stresses[d] = obs1.stress_normalized(D[np.ix_(tr, tr)], r["coords"]) if r["ok"] else None
    sel = obs1.select_dimension({d: s for d, s in stresses.items() if s is not None})
    return {"vol_d": vol["d"], "vol_r2": vol["r2"], "vol_n": vol["n"],
            "stress": {str(k): v for k, v in stresses.items()},
            "dstar": sel["dstar"], "pass": sel["pass"]}


def run_obs_dim(sub: str, L: int) -> dict:
    t0 = time.time()
    if L <= 128:
        tag = f"{sub}-L{L}"
        cell = OBS1_CELLS[tag]
        with open(os.path.join(BANKED_OBS1, f"obs1_meas_cell{cell}_s0.json")) as f:
            meas = json.load(f)
        nat = obs1.native_matrices(meas["pairs"], n=meas["n"])
        probes = {}
        for ch in ("W", "D", "P"):
            done = obs1.complete_matrix(nat[ch])
            probes[ch] = {"completeness": obs1.completeness(nat[ch]),
                          "geo": _blind_geometry(done["D"])}
        comp = obs1.composite_matrix({ch: obs1.complete_matrix(nat[ch])["D"]
                                      for ch in ("W", "D", "P")})
        comp_d = obs1.complete_matrix(comp)["D"]
        probes["composite"] = {"geo": _blind_geometry(comp_d)}
        # Wave+static-only validation chain (method for L >= 256).
        comp_wp = obs1.composite_matrix({ch: obs1.complete_matrix(nat[ch])["D"]
                                         for ch in ("W", "P")})
        probes["composite_WP"] = {"geo": _blind_geometry(obs1.complete_matrix(comp_wp)["D"])}
        return {"sub": sub, "L": L, "mode": "replay", "cell": cell,
                "probes": probes, "elapsed": time.time() - t0}
    # Rebuild at L >= 256: Krylov wave + CG static, 64 stations, set s0.
    return _obs_dim_rebuild(sub, L, t0)


def _obs_dim_rebuild(sub: str, L: int, t0: float) -> dict:
    import networkx as nx

    cell = DIM_NEW_CELLS[(sub, L)]
    g = scale0.build_graph(sub, L)
    order = scale0.node_order(g)
    idx = {v: i for i, v in enumerate(order)}
    N = len(order)
    rng = np.random.default_rng(9100 + 100 * cell + 0)
    stations = [order[i] for i in rng.choice(N, 64, replace=False)]
    sidx = [idx[v] for v in stations]
    D = obs0.intrinsic_diameter(g, order[0])
    h = scale0.hamiltonian(g, order)
    ts_w = obs0.wave_grid(D)
    pairs = {}
    for a in range(64):
        Pk = scale0.krylov_wave_traces_chunked(h, sidx[a], sidx, ts_w,
                                               chunk_steps=CHUNK_BIG)
        for b in range(64):
            if a == b:
                continue
            t = obs0.threshold_crossing(Pk[:, b], ts_w, obs0.THETA_WAVE)
            pairs[f"S{a}|S{b}"] = {"W": t, "D": None, "P": None, "Dcfd": None}
    hcsc = h.tocsc()
    for a in range(64):
        phi = scale0.cg_static_phi(hcsc, sidx[a], scale0.OM_J2)
        for b in range(64):
            if a == b:
                continue
            pairs[f"S{a}|S{b}"]["P"] = float(abs(phi[sidx[b]]))
    nat = obs1.native_matrices(pairs, n=64)
    probes = {}
    for ch in ("W", "P"):
        done = obs1.complete_matrix(nat[ch])
        probes[ch] = {"completeness": obs1.completeness(nat[ch]),
                      "geo": _blind_geometry(done["D"])}
    comp = obs1.composite_matrix({ch: obs1.complete_matrix(nat[ch])["D"]
                                  for ch in ("W", "P")})
    probes["composite_WP"] = {"geo": _blind_geometry(obs1.complete_matrix(comp)["D"])}
    return {"sub": sub, "L": L, "mode": "rebuild", "cell": cell,
            "probes": probes, "elapsed": time.time() - t0}


# ---------------------------------------------------------------------------
# resp (RESPONSE scaling cell, streaming)
# ---------------------------------------------------------------------------

def _resp_analyze(tr: dict, ts: np.ndarray, floor: float, L: int, rmax_cap: int = 64):
    from bh_graph import response as R

    ts = np.asarray(ts, dtype=float)
    remote_peak = 0.0
    for s, t in tr.items():
        if 1 <= s <= rmax_cap:
            remote_peak = max(remote_peak, float(np.asarray(t).max()))
    theta = max(1e-3 * remote_peak, floor)
    arrivals = {}
    for s in sorted(tr):
        if s > rmax_cap:
            continue
        arrivals[s] = R.arrival_time(np.asarray(tr[s]), ts, theta)
    out = {"theta": theta, "remote_peak": remote_peak, "arrivals": arrivals}
    for name, shells in (("fit10", FIT_SHELLS),
                         ("fitExt", [s for s in range(2, min(L // 4, 64) + 1)])):
        use = [s for s in shells if arrivals.get(s) is not None]
        if len(use) >= 3:
            fv = R.front_velocity({s: arrivals[s] for s in use}, use)
            out[name] = {"v": fv["v"], "r2": fv["r2"], "n": len(use)}
        else:
            out[name] = None
    # Pre/post Rmax + distance exponents (regime firewall enforced).
    rmax_pre, rmax_post = {}, {}
    for s in sorted(tr):
        if s > rmax_cap or s < 1:
            continue
        sp = scale0.split_pre_post(ts, float(s), L)
        t = np.asarray(tr[s])
        rmax_pre[s] = float(t[sp["pre"]].max()) if sp["n_pre"] else None
        rmax_post[s] = float(t[sp["post"]].max()) if sp["n_post"] else None
    out["rmax_pre"] = rmax_pre
    out["rmax_post"] = rmax_post
    for reg, tab in (("pre", rmax_pre), ("post", rmax_post)):
        xs = np.array([s for s in sorted(tab) if tab[s] and tab[s] > 0], dtype=float)
        ys = np.array([tab[s] for s in sorted(tab) if tab[s] and tab[s] > 0], dtype=float)
        m = (xs >= 2) & (xs <= 10)
        out[f"exp10_{reg}"] = scale0.fit_loglog(xs[m], ys[m]) if m.sum() >= 3 else None
        m2 = (xs >= 2) & (xs <= min(L // 4, 64))
        out[f"expExt_{reg}"] = scale0.fit_loglog(xs[m2], ys[m2]) if m2.sum() >= 3 else None
    return out


def run_resp(L: int, bg: str) -> dict:
    from bh_graph import response as R
    from bh_graph.formation import j2_torus_coords, j2_torus_graph
    from bh_graph.quot import coarse_shells

    t0 = time.time()
    g = j2_torus_graph(L)
    order = list(range(2 * L * L))
    c3 = j2_torus_coords(L)
    h = R.hamiltonian(g, order)
    eu, ev = R.edge_index_arrays(g, order)
    idx = {v: i for i, v in enumerate(order)}
    sx, sy = L // 4, L // 2
    src_node = (sx * L + sy) * 2
    iu = idx[src_node]
    eps = RESP_BG[bg]
    vac = R.background_state(bg, g, order, c3, L)
    has_bg = float(np.linalg.norm(vac)) > 0
    d0 = R.point_source(len(order), iu, eps)
    T = scale0.response_T(L)
    dt = 0.05
    n_steps = int(round(T / dt))
    ts = np.arange(n_steps + 1) * dt
    qs = coarse_shells(c3, order, (sx, sy), L, min(L // 2, 70))
    qs_idx = {s: ii for s, ii in qs.items() if ii}
    chunk = CHUNK_BIG if L >= 256 else CHUNK
    psi_tr = {s: np.zeros(n_steps + 1) for s in qs_idx}
    rho_tr = {s: np.zeros(n_steps + 1) for s in qs_idx}
    q_of = {}
    for s, ii in qs_idx.items():
        for i in ii:
            q_of[i] = s
    qb = {}
    for e in range(len(eu)):
        s = min(q_of.get(int(eu[e]), 10 ** 9), q_of.get(int(ev[e]), 10 ** 9))
        if s < 10 ** 9:
            qb.setdefault(s, []).append(e)
    b_tr = {s: np.zeros(n_steps + 1) for s in qb}
    j_tr = {s: np.zeros(n_steps + 1) for s in qb}
    # Ray traces (axial/diagonal quotient rays).
    rays = {"axial": R.quotient_ray((sx, sy), (1, 0), min(L // 2, 64), L),
            "diag": R.quotient_ray((sx, sy), (1, 1), min(L // 2, 64), L)}
    ray_idx = {}
    for name, cells in rays.items():
        mp = R.cells_to_indices(cells, c3, order)
        ray_idx[name] = [(k, mp[c]) for k, c in enumerate(cells) if c in mp]
    ray_tr = {name: np.zeros((n_steps + 1, len(ray_idx[name]))) for name in rays}
    psi_d = d0.copy()
    psi_b = vac.copy() if has_bg else None
    k = 0
    seg_gen_d = scale0.evolve_segments(h, psi_d, dt, n_steps, chunk)
    seg_gen_b = scale0.evolve_segments(h, psi_b, dt, n_steps, chunk) if has_bg else None
    for k_off, rows_d in seg_gen_d:
        rows_b = None
        if has_bg:
            _, rows_b = next(seg_gen_b)
            full = rows_b + rows_d
            rho = np.abs(full) ** 2 - np.abs(rows_b) ** 2
            b_all = (np.conj(full[:, eu]) * full[:, ev]).real - \
                (np.conj(rows_b[:, eu]) * rows_b[:, ev]).real
            j_all = 2.0 * (np.conj(full[:, eu]) * full[:, ev]).imag - \
                2.0 * (np.conj(rows_b[:, eu]) * rows_b[:, ev]).imag
        else:
            rho = np.abs(rows_d) ** 2
            b_all = (np.conj(rows_d[:, eu]) * rows_d[:, ev]).real
            j_all = 2.0 * (np.conj(rows_d[:, eu]) * rows_d[:, ev]).imag
        sl = slice(k_off, k_off + rows_d.shape[0])
        ad = np.abs(rows_d)
        for s, ii in qs_idx.items():
            psi_tr[s][sl] = ad[:, ii].max(axis=1)
            rho_tr[s][sl] = np.abs(rho[:, ii]).max(axis=1)
        ab = np.abs(b_all)
        aj = np.abs(j_all)
        for s, ee in qb.items():
            b_tr[s][sl] = ab[:, ee].max(axis=1)
            j_tr[s][sl] = aj[:, ee].max(axis=1)
        for name in rays:
            for j, ii in ray_idx[name]:
                ray_tr[name][sl, j] = ad[:, ii].max(axis=1)
    # Decomp identity at 8 sample times (re-evolved exactly at samples).
    from scipy.sparse.linalg import expm_multiply as _expm

    devs = []
    for kk in range(0, n_steps + 1, max(n_steps // 8, 1)):
        t = kk * dt
        dk = np.asarray(_expm(-1.0j * h * t, d0), dtype=np.complex128).ravel() \
            if t > 0 else d0.copy()
        bk = np.asarray(_expm(-1.0j * h * t, vac), dtype=np.complex128).ravel() \
            if (t > 0 and has_bg) else (vac.copy() if has_bg else np.zeros(len(order)))
        rr = R.delta_observables(bk, dk, eu, ev)
        devs.append(max(float(np.abs(rr["d_rho"] - rr["d_rho1"] - rr["d_rho2"]).max()),
                        float(np.abs(rr["d_B"] - rr["d_B1"] - rr["d_B2"]).max()),
                        float(np.abs(rr["d_J"] - rr["d_J1"] - rr["d_J2"]).max())))
    # Sector drift.
    partner = R.sheet_partner(order, c3)
    dend = np.asarray(_expm(-1.0j * h * (n_steps * dt), d0),
                      dtype=np.complex128).ravel()
    w0 = R.sector_weights(d0 / max(float(np.linalg.norm(d0)), 1e-300), partner)
    w1 = R.sector_weights(dend / max(float(np.linalg.norm(dend)), 1e-300), partner)
    drift = float(abs(w1["w_plus"] - w0["w_plus"]) + abs(w1["w_minus"] - w0["w_minus"]))
    # Ray velocities (arrival per ray cell, theta from ray peak).
    ray_vel = {}
    for name in rays:
        peak = float(ray_tr[name][:, 1:].max()) if ray_tr[name].shape[1] > 1 else 0.0
        th = max(1e-3 * peak, 1e-12)
        arr = {}
        for j, _ in ray_idx[name]:
            a = R.arrival_time(ray_tr[name][:, j], ts, th)
            if a is not None:
                arr[j] = a
        use = [j for j in range(2, 11) if j in arr]
        if len(use) >= 3:
            fv = R.front_velocity({j: arr[j] for j in use}, use)
            ray_vel[name] = {"v": fv["v"], "r2": fv["r2"]}
        else:
            ray_vel[name] = None
    return {"L": L, "bg": bg, "eps": eps, "T": T, "dt": dt,
            "q_psi": _resp_analyze(psi_tr, ts, 1e-12, L),
            "q_rho": _resp_analyze(rho_tr, ts, 1e-14, L),
            "q_B": _resp_analyze(b_tr, ts, 1e-14, L),
            "q_J": _resp_analyze(j_tr, ts, 1e-14, L),
            "ray_vel": ray_vel, "decomp_max": float(max(devs)),
            "sector_drift": drift, "elapsed": time.time() - t0}


def run_resp_regress(which: str) -> dict:
    from bh_graph import response as R
    from bh_graph.formation import j2_torus_coords, j2_torus_graph
    from bh_graph.quot import coarse_shells

    t0 = time.time()
    L = 28
    g = j2_torus_graph(L)
    order = list(range(2 * L * L))
    c3 = j2_torus_coords(L)
    h = R.hamiltonian(g, order)
    eu, ev = R.edge_index_arrays(g, order)
    idx = {v: i for i, v in enumerate(order)}
    iu = idx[(7 * L + 14) * 2]
    eps = 1.0 if which == "HR" else 1.0j
    d0 = R.point_source(len(order), iu, eps)
    dt, n_steps = 0.05, 320
    ts = np.arange(n_steps + 1) * dt
    rows = R.evolve(d0, h, dt, n_steps)["psi"]
    qs = coarse_shells(c3, order, (7, 14), L, 25)
    qs_idx = {s: ii for s, ii in qs.items() if ii}
    psi_tr = {s: np.abs(rows[:, ii]).max(axis=1) for s, ii in qs_idx.items()}
    rho = np.abs(rows) ** 2
    rho_tr = {s: rho[:, ii].max(axis=1) for s, ii in qs_idx.items()}
    q_of = {}
    for s, ii in qs_idx.items():
        for i in ii:
            q_of[i] = s
    qb = {}
    for e in range(len(eu)):
        s = min(q_of.get(int(eu[e]), 10 ** 9), q_of.get(int(ev[e]), 10 ** 9))
        if s < 10 ** 9:
            qb.setdefault(s, []).append(e)
    j_all = 2.0 * (np.conj(rows[:, eu]) * rows[:, ev]).imag
    j_tr = {s: np.abs(j_all[:, ee]).max(axis=1) for s, ee in qb.items()}
    a_psi = _resp_analyze(psi_tr, ts, 1e-12, L)
    a_rho = _resp_analyze(rho_tr, ts, 1e-14, L)
    a_j = _resp_analyze(j_tr, ts, 1e-14, L)
    rr = R.delta_observables(np.zeros(len(order)), rows[n_steps // 2], eu, ev)
    dev = max(float(np.abs(rr["d_rho"] - rr["d_rho1"] - rr["d_rho2"]).max()),
              float(np.abs(rr["d_B"] - rr["d_B1"] - rr["d_B2"]).max()),
              float(np.abs(rr["d_J"] - rr["d_J1"] - rr["d_J2"]).max()))
    return {"which": which, "v_field": (a_psi["fit10"] or {}).get("v"),
            "v_field_r2": (a_psi["fit10"] or {}).get("r2"),
            "v_rho": (a_rho["fit10"] or {}).get("v"),
            "v_J": (a_j["fit10"] or {}).get("v"),
            "decomp": dev, "elapsed": time.time() - t0}


# ---------------------------------------------------------------------------
# p1 (packet scaling cell, streaming)
# ---------------------------------------------------------------------------

def run_p1(L: int, kkey: str) -> dict:
    from bh_graph.ballistic import (com, fit_velocity, gaussian_packet,
                                    msd_exponent_rs, packet_width,
                                    unwrap_trace)
    from bh_graph.formation import j2_torus_coords, j2_torus_graph
    from bh_graph.potential import edge_table, flux_decomposition

    t0 = time.time()
    k = P1_KS[kkey]
    g = j2_torus_graph(L)
    order = sorted(g.nodes())
    c3 = j2_torus_coords(L)
    coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    periods = (L, L)
    h = scale0.hamiltonian(g, order)
    r0 = (L / 4.0, L / 2.0)
    psi0 = gaussian_packet(coords, order, r0, k, 4.0, periods=periods)
    T_pre = scale0.packet_T_pre(L)
    T_post = scale0.packet_T_post(L)
    dt = 0.1
    n_steps = int(round(T_post / dt))
    ts = np.arange(n_steps + 1) * dt
    edges = edge_table(g, order, coords, L)
    chunk = CHUNK_BIG if L >= 256 else CHUNK
    rs = np.zeros((n_steps + 1, 2))
    width = np.zeros(n_steps + 1)
    stride = max(n_steps // 60, 1)
    d_trace = {}
    for k_off, rows in scale0.evolve_segments(h, psi0, dt, n_steps, chunk):
        for j in range(rows.shape[0]):
            kk = k_off + j
            rs[kk] = com(rows[j], coords, order, periods=periods)
            width[kk] = packet_width(rows[j], coords, order, periods=periods)
            if kk % stride == 0:
                f = flux_decomposition(rows[j], edges)
                d_trace[kk] = f["D"]
    unr = unwrap_trace(rs, periods)
    trav = np.linalg.norm(unr - unr[0], axis=1)
    pre = ts <= T_pre
    post = ts >= 0.7 * T_post
    v_pre = fit_velocity(unr[pre], ts[pre])
    v_post = fit_velocity(unr[post], ts[post])
    w_pre = np.polyfit(ts[pre], width[pre], 1)[0] if pre.sum() >= 3 else float("nan")
    w_post = np.polyfit(ts[post], width[post], 1)[0] if post.sum() >= 3 else float("nan")
    return {"L": L, "k": list(k), "T_pre": T_pre, "T_post": T_post,
            "v_pre": v_pre, "v_post": v_post,
            "msd_pre": float(msd_exponent_rs(unr[pre], ts[pre])),
            "msd_post": float(msd_exponent_rs(unr[post], ts[post])),
            "width_rate_pre": float(w_pre), "width_rate_post": float(w_post),
            "width_growth": float(width[-1] - width[0]),
            "travel_pre_max": float(trav[pre].max()),
            "travel_post_max": float(trav[post].max()),
            "L_half": L / 2.0, "D_trace": {str(k): v for k, v in d_trace.items()},
            "elapsed": time.time() - t0}


def run_p1_regress(which: str) -> dict:
    import math

    import networkx as nx
    from bh_graph import obs0
    from bh_graph.ballistic import (branch_projectors, branch_purify, com,
                                    gaussian_packet, unwrap_trace)
    from bh_graph.formation import j2_torus_coords, j2_torus_graph
    from bh_graph.graphs import build_torus_grid

    t0 = time.time()
    if which == "sq-L30":
        L = 30
        g = build_torus_grid(L)
        order = sorted(g.nodes())
        coords = {x * L + y: (float(x), float(y)) for x in range(L) for y in range(L)}
        psi0 = obs0.c5_gaussian_packet(coords, order, (7.0, 15.0), (0.5, 0.0), 3.0,
                                       periods=(L, L))
        E, V, _ = obs0.hamiltonian_system(g, order)
        rows = obs0.c5_evolve_packet(E, V, psi0, 0.2, 125)
        ts = np.arange(126) * 0.2
        rs = obs0.c5_unwrap_trace(
            np.array([obs0.c5_com(p, coords, order, periods=(L, L)) for p in rows]),
            periods=(L, L))
        v = obs0.c5_fit_speed(rs, ts)["speed"]
        return {"which": which, "v": float(v), "ref": 0.9658,
                "elapsed": time.time() - t0}
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
    for kk, branch in specs:
        psi = obs0.c5_gaussian_packet(coords, order, (7.0, 14.0), kk, 4.0,
                                      periods=(L, L))
        pure, retained = obs0.c5_branch_purify(psi, br[branch])
        rows = obs0.c5_evolve_packet(E, V, pure, 0.1, 100)
        ts = np.arange(101) * 0.1
        rs = obs0.c5_unwrap_trace(
            np.array([obs0.c5_com(p, coords, order, periods=(L, L)) for p in rows]),
            periods=(L, L))
        speeds.append(float(obs0.c5_fit_speed(rs, ts)["speed"]))
    return {"which": which, "speeds": speeds,
            "mean": float(np.mean(speeds)), "ref": 1.2075,
            "elapsed": time.time() - t0}


# ---------------------------------------------------------------------------
# pot (static range/floor/all-path cell, CG)
# ---------------------------------------------------------------------------

def run_pot(L: int) -> dict:
    import networkx as nx
    from bh_graph.driven import dist_from_set, shell_means_node
    from bh_graph.formation import j2_torus_coords, j2_torus_graph
    from bh_graph.quot import coarse_shells

    t0 = time.time()
    g = j2_torus_graph(L)
    order = sorted(g.nodes())
    idx = {v: i for i, v in enumerate(order)}
    c3 = j2_torus_coords(L)
    h = scale0.hamiltonian(g, order).tocsc()
    sx, sy = L // 4, L // 2
    src = (sx * L + sy) * 2
    phi = scale0.cg_static_phi(h, idx[src], scale0.OM_J2)
    amp = np.abs(phi)
    dist = dist_from_set(g, [src])
    rmax = min(max(dist.values()), 70)
    means = shell_means_node(amp, order, dist, rmax)
    # POT-1 parity: xi = -log-slope over shells r = 2..5 (banked 0.53).
    rr = np.array([2, 3, 4, 5], dtype=float)
    vv = np.array([means[r] for r in (2, 3, 4, 5)], dtype=float)
    okm = vv > 1e-300
    xi = float(-np.polyfit(rr[okm], np.log(vv[okm]), 1)[0]) if okm.sum() >= 3 else None
    pin = float(amp[idx[src]])
    rng = max([r for r in range(rmax + 1) if means[r] > 0.05 * pin], default=0)
    far = [means[r] for r in range(rmax // 2, rmax + 1)]
    floor = float(np.median(far)) if far else None
    # All-path diagnostic: single-exp misfit over r = 0..12 (1D model reject).
    rr1 = np.array([r for r in range(0, 13)], dtype=float)
    vv1 = np.array([means[r] for r in range(0, 13)], dtype=float)
    ok1 = vv1 > 1e-6
    if ok1.sum() >= 3:
        slope, icept = np.polyfit(rr1[ok1], np.log(vv1[ok1]), 1)
        fit1d = {r: float(math.exp(icept + slope * r)) for r in range(0, 13)}
        res1d = max(abs(fit1d[r] - means[r]) for r in range(0, 13))
    else:
        res1d = None
    # Quotient-shell profile (coarse readout).
    qs = coarse_shells(c3, order, (sx, sy), L, min(L // 2, 70))
    qmeans = {}
    for s, ii in qs.items():
        if ii:
            qmeans[s] = float(np.median(amp[np.asarray(ii)]))
    return {"L": L, "omega": scale0.OM_J2, "xi": xi, "range": int(rng),
            "floor": floor, "pin": pin, "res1d": res1d,
            "shell_means": {str(k): float(v) for k, v in means.items()},
            "qmeans": {str(k): float(v) for k, v in qmeans.items()},
            "elapsed": time.time() - t0}


def run_pot_regress() -> dict:
    from bh_graph.driven import dist_from_set, shell_means_node, steady_predict
    from bh_graph.formation import j2_torus_graph

    t0 = time.time()
    L = 28
    g = j2_torus_graph(L)
    order = sorted(g.nodes())
    idx = {v: i for i, v in enumerate(order)}
    h = scale0.hamiltonian(g, order).tocsc()
    src = (7 * L + 14) * 2
    phi_cg = scale0.cg_static_phi(h, idx[src], scale0.OM_J2)
    phi_sp = steady_predict(h, [idx[src]], [1.0], scale0.OM_J2)
    dev = float(np.abs(phi_cg - phi_sp).max())
    amp = np.abs(phi_cg)
    dist = dist_from_set(g, [src])
    means = shell_means_node(amp, order, dist, 12)
    rr = np.array([2, 3, 4, 5], dtype=float)
    vv = np.array([means[r] for r in (2, 3, 4, 5)], dtype=float)
    xi = float(-np.polyfit(rr, np.log(np.maximum(vv, 1e-300)), 1)[0])
    pin = float(amp[idx[src]])
    rng = max([r for r in range(13) if means[r] > 0.05 * pin], default=0)
    return {"cg_spsolve_dev": dev, "xi": xi, "range": int(rng),
            "elapsed": time.time() - t0}


# ---------------------------------------------------------------------------
# quot (QUOT scaling cell)
# ---------------------------------------------------------------------------

def run_quot(L: int, family: str) -> dict:
    from bh_graph import quot
    from bh_graph.formation import j2_torus_coords, j2_torus_graph

    t0 = time.time()
    g = j2_torus_graph(L)
    order = sorted(g.nodes())
    c3 = j2_torus_coords(L)
    h = scale0.hamiltonian(g, order)
    X0 = (L // 4, L // 2)
    X1 = (L // 4 + 1, L // 2)
    fam = quot.sector_preparations(order, c3, X0, X1)
    pair = {"sym": ("sym0", "sym1"), "anti": ("anti0", "anti1"),
            "sheet0": ("sheet0", "sheet1"), "sheet1": ("sheet0", "sheet1")}[family]
    rmax = min(L // 2, 70)
    shells = quot.coarse_shells(c3, order, X0, L, rmax)
    shells_idx = {r: ii for r, ii in shells.items() if ii}
    n = len(order)

    def wave_caps(T: float):
        dt = quot.DT_WAVE
        n_steps = int(round(T / dt))
        ts = np.arange(n_steps + 1) * dt
        chunk = CHUNK_BIG if L >= 256 else CHUNK
        Dtr = {r: np.zeros(n_steps + 1) for r in shells_idx}
        g0 = scale0.evolve_segments(h, fam[pair[0]], dt, n_steps, chunk)
        g1 = scale0.evolve_segments(h, fam[pair[1]], dt, n_steps, chunk)
        for (k0, r0), (k1, r1) in zip(g0, g1):
            assert k0 == k1
            p0 = np.abs(r0) ** 2
            p1 = np.abs(r1) ** 2
            sl = slice(k0, k0 + r0.shape[0])
            for r, ii in shells_idx.items():
                ii = np.asarray(ii)
                Dtr[r][sl] = 0.5 * np.abs(p0[:, ii] - p1[:, ii]).sum(axis=1)
        cap = {}
        for r, d in Dtr.items():
            k = int(np.argmax(d))
            arr = None
            for t, v in zip(ts, d):
                if v > quot.THETA_ARR:
                    arr = float(t)
                    break
            cap[r] = {"C": float(d[k]), "tstar": float(ts[k]), "arrival": arr,
                      "n": len(shells_idx[r])}
        return cap, ts

    cap_pre, _ = wave_caps(quot.T_WAVE)
    cap_post, _ = wave_caps(scale0.packet_T_post(L))
    # Diffusion (T = 16 frozen pre-horizon, stepped Krylov).
    lrw = scale0.lrw_operator(g, order)
    dt_d, T_d = 0.05, 16.0
    n_d = int(round(T_d / dt_d))

    def as_prob(name):
        if name.startswith("anti"):
            d0 = np.zeros(n)
            pos = {v: i for i, v in enumerate(order)}
            node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
            cell = X0 if name == "anti0" else X1
            d0[pos[node_of[(cell[0], cell[1], 0)]]] = 0.5
            d0[pos[node_of[(cell[0], cell[1], 1)]]] = -0.5
            return d0
        return (np.abs(fam[name]) ** 2).astype(float)

    p0, p1 = as_prob(pair[0]), as_prob(pair[1])
    gen = (-lrw.tocsr() * dt_d).tocsr()
    Dtr = {r: np.zeros(n_d + 1) for r in shells_idx}
    for kk in range(n_d + 1):
        if kk > 0:
            from scipy.sparse.linalg import expm_multiply as _expm

            p0 = np.asarray(_expm(gen, p0), dtype=float).ravel()
            p1 = np.asarray(_expm(gen, p1), dtype=float).ravel()
        for r, ii in shells_idx.items():
            ii = np.asarray(ii)
            Dtr[r][kk] = 0.5 * np.abs(p0[ii] - p1[ii]).sum()
    ts_d = np.arange(n_d + 1) * dt_d
    cap_diff = {}
    for r, d in Dtr.items():
        k = int(np.argmax(d))
        arr = None
        for t, v in zip(ts_d, d):
            if v > quot.THETA_ARR:
                arr = float(t)
                break
        cap_diff[r] = {"C": float(d[k]), "tstar": float(ts_d[k]), "arrival": arr}
    # POT channel (sparse CG multi).
    from bh_graph import response as _R

    pos = {v: i for i, v in enumerate(order)}
    node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
    pin = [pos[node_of[(X0[0], X0[1], 0)]]]
    phi = quot.static_phi_multi(h.tocsc(), pin, np.array([1.0]), scale0.OM_J2)
    from bh_graph import malus

    pr = malus.sheet_projectors(order, c3)
    decomp = quot.decompose_solution(np.real(phi), pr)
    anti_frac = float(np.linalg.norm(decomp["anti"]) / max(np.linalg.norm(phi), 1e-300))
    near8 = [(x, y) for x in range(L) for y in range(L)
             if min((x - X0[0]) % L, (X0[0] - x) % L) ** 2
             + min((y - X0[1]) % L, (X0[1] - y) % L) ** 2 <= 64]
    asym_d = quot.pot_sheet_asymmetry(phi, order, c3, near8)
    asym_vals = [v for v in asym_d.values() if v is not None]
    asym = {"max": float(max(asym_vals)) if asym_vals else None,
            "median": float(np.median(asym_vals)) if asym_vals else None,
            "n": len(asym_vals)}
    return {"L": L, "family": family, "wave_pre": cap_pre, "wave_post": cap_post,
            "diff_pre": cap_diff, "pot_anti_frac": anti_frac,
            "pot_asym": asym, "elapsed": time.time() - t0}


def run_quot_regress(which: str) -> dict:
    from bh_graph import malus, quot
    from bh_graph.formation import j2_torus_coords, j2_torus_graph

    t0 = time.time()
    L = 28
    g = j2_torus_graph(L)
    order = sorted(g.nodes())
    c3 = j2_torus_coords(L)
    h = scale0.hamiltonian(g, order)
    if which == "alg":
        pr = malus.sheet_projectors(order, c3)
        n = len(order)
        pos = {v: i for i, v in enumerate(order)}
        node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
        S = np.zeros((n, n))
        for v in order:
            x, y, b = c3[v]
            w = node_of[(x, y, 1 - b)]
            S[pos[w], pos[v]] = 1.0
        u, cells_sq = malus.symmetric_embedding(order, c3)
        hsq = malus.square_hamiltonian(cells_sq, (L, L))
        return {"comm": quot.commutator_norm(h, S),
                "dead": quot.anti_dead_norm(h, pr["P_anti"]),
                "inter": quot.intertwining_norm(h, u, hsq),
                "neighbor_sets": quot.is_coarse_neighbor_sets_identical_ok(g, c3),
                "elapsed": time.time() - t0}
    # Wave replay at load shells (banked parity: sym arrives, anti silent).
    X0, X1 = (7, 14), (8, 14)
    fam = quot.sector_preparations(order, c3, X0, X1)
    shells = quot.coarse_shells(c3, order, X0, L, 14)
    shells_idx = {r: ii for r, ii in shells.items() if ii}
    out = {"shells": {}}
    for name, pair in (("sym", ("sym0", "sym1")), ("anti", ("anti0", "anti1"))):
        dt = quot.DT_WAVE
        n_steps = int(round(quot.T_WAVE / dt))
        ts = np.arange(n_steps + 1) * dt
        g0 = scale0.evolve_segments(h, fam[pair[0]], dt, n_steps, CHUNK)
        g1 = scale0.evolve_segments(h, fam[pair[1]], dt, n_steps, CHUNK)
        Dtr = {r: np.zeros(n_steps + 1) for r in shells_idx}
        for (k0, r0), (k1, r1) in zip(g0, g1):
            p0 = np.abs(r0) ** 2
            p1 = np.abs(r1) ** 2
            sl = slice(k0, k0 + r0.shape[0])
            for r, ii in shells_idx.items():
                ii = np.asarray(ii)
                Dtr[r][sl] = 0.5 * np.abs(p0[:, ii] - p1[:, ii]).sum(axis=1)
        for r in quot.R_LOAD:
            d = Dtr[r]
            arr = None
            for t, v in zip(ts, d):
                if v > quot.THETA_ARR:
                    arr = float(t)
                    break
            out["shells"][f"{name}@{r}"] = {"C": float(d.max()), "arrival": arr}
    out["elapsed"] = time.time() - t0
    return out


# ---------------------------------------------------------------------------
# zero (ZERO scaling cell, streaming)
# ---------------------------------------------------------------------------

def _ppinode_state(L: int, sigma: float = 3.0, dphi: float = math.pi):
    from bh_graph.ballistic import gaussian_packet
    from bh_graph.formation import j2_torus_coords, j2_torus_graph

    g = j2_torus_graph(L)
    order = sorted(g.nodes())
    c3 = j2_torus_coords(L)
    coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    p1 = gaussian_packet(coords, order, (L / 4.0, L / 2.0), (math.pi / 2, 0.0),
                         sigma, periods=(L, L))
    p2 = gaussian_packet(coords, order, (3 * L / 4.0, L / 2.0), (-math.pi / 2, 0.0),
                         sigma, periods=(L, L)) * np.exp(1j * dphi)
    psi0 = p1 + p2
    return g, order, coords, (psi0 / np.linalg.norm(psi0)).astype(np.complex128)


def run_zero(L: int, fam: str, regime: str) -> dict:
    from bh_graph import zero

    t0 = time.time()
    if fam == "F5" and L >= 128:
        return {"L": L, "fam": fam, "regime": regime,
                "unresolved": {"reason": "F5-prep-needs-dense-eig",
                               "class": "cost"},
                "elapsed": time.time() - t0}
    if regime == "post" and L >= 256:
        return {"L": L, "fam": fam, "regime": regime,
                "unresolved": {"reason": "P5-no-ZERO-post-at-L>=256",
                               "class": "cost"},
                "elapsed": time.time() - t0}
    dt = zero.DT_HEAD
    T = zero.T_HEAD if regime == "pre" else scale0.zero_T_post(L)
    n_steps = int(round(T / dt))
    ts = np.arange(n_steps + 1) * dt
    if fam == "ppinode":
        g, order, coords, psi0 = _ppinode_state(L)
    else:
        from bh_graph.formation import j2_torus_coords, j2_torus_graph

        g = j2_torus_graph(L)
        order = sorted(g.nodes())
        c3 = j2_torus_coords(L)
        coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    h = scale0.hamiltonian(g, order)
    n = len(order)
    if fam in ("F1", "F5"):
        hd = None
        if fam == "F5":
            hd = np.asarray(h.toarray(), dtype=float)
        prep = zero.prepare_family(fam, n, 0, h=hd, coords=coords, order=order)
        if not prep["exclusion_ok"]:
            return {"L": L, "fam": fam, "regime": regime,
                    "filed": "initial-exclusion", "elapsed": time.time() - t0}
        psi0 = prep["psi"]
        seed_used = prep["seed_used"]
    else:
        seed_used = 0
    chunk = CHUNK_BIG if L >= 256 else CHUNK
    min_trace = np.full(n_steps + 1, np.inf)
    near_counts = np.zeros(n_steps + 1, dtype=int)
    best = {}  # node -> [amp, t]
    cand_nodes = set()
    for k_off, rows in scale0.evolve_segments(h, psi0, dt, n_steps, chunk):
        amp = np.abs(rows)
        sl = slice(k_off, k_off + rows.shape[0])
        min_trace[sl] = amp.min(axis=1)
        near_counts[sl] = (amp < zero.EPS_NEAR).sum(axis=1)
        loc = amp.argmin(axis=1)
        for j in range(rows.shape[0]):
            u = int(loc[j])
            a = float(amp[j, u])
            if u not in best or a < best[u][0]:
                best[u] = [a, float(ts[k_off + j])]
        for hit in zero.screen_candidates(rows, ts[sl], zero.EPS_SCREEN):
            cand_nodes.add(int(hit["node"]) if isinstance(hit, dict)
                           else int(hit[0]))
    # Refine top candidates by amplitude (cap 25, ZERO-0 precedent).
    ranked = sorted(best.items(), key=lambda kv: kv[1][0])[:25]
    refined = []
    for u, (a, t_seed) in ranked:
        try:
            lv2 = zero.refine_candidate(psi0, h, int(u), float(t_seed))
            refined.append({"node": int(u), "t_star": lv2.get("t_star"),
                            "amp_min": lv2.get("amp_min")})
        except Exception as e:  # noqa: BLE001 -- filed, never silent
            refined.append({"node": int(u), "error": str(e)[:200]})
    return {"L": L, "fam": fam, "regime": regime, "seed_used": seed_used,
            "T": T, "dt": dt, "min_amp_global": float(min_trace.min()),
            "near_total": int(near_counts.sum()),
            "near_per_step_max": int(near_counts.max()),
            "n_screen_nodes": len(cand_nodes),
            "min_trace_decim": scale0.decimate_trace(min_trace, ts),
            "refined": refined, "elapsed": time.time() - t0}


def run_zero_regress(which: str) -> dict:
    from bh_graph import zero

    t0 = time.time()
    if which == "refine":
        from bh_graph.formation import j2_torus_graph

        L = 28
        g = j2_torus_graph(L)
        order = sorted(g.nodes())
        h = scale0.hamiltonian(g, order)
        prep = zero.prepare_family("F1", len(order), 0, coords=None, order=order)
        psi0 = prep["psi"]
        a = zero.refine_candidate(psi0, h, 7, 1.0)
        b = zero.refine_candidate(psi0, h, 7, 1.0)
        return {"t_star": a.get("t_star"), "amp_min": a.get("amp_min"),
                "bitwise": bool(a.get("t_star") == b.get("t_star")
                                and a.get("amp_min") == b.get("amp_min")),
                "elapsed": time.time() - t0}
    # Exact-parity replay of the banked collide row (same frozen code).
    sys.path.insert(0, os.path.dirname(__file__))
    import zero0_campaign as zc

    class A:
        task = "collide"
        substrate = "j2"
        size = 20
        geom = "headon"
        dphi = math.pi
        amp = "match"
        sigma = 3.0
        dt = zero.DT_HEAD
        horizon = zero.T_HEAD
        anatomy = False
        n_modes = 3
        seed = 0

    row = zc.kind_collide(A())
    return {"n_events": row["n_events"], "n_candidates": row["n_candidates"],
            "labels": row["labels"], "banked_events": 508,
            "elapsed": time.time() - t0}


# ---------------------------------------------------------------------------
# vacexc (VAC-EXC scaling cell)
# ---------------------------------------------------------------------------

def run_vacexc(L: int, group: str) -> dict:
    from bh_graph import vacexc as vx
    from bh_graph.ballistic import com

    t0 = time.time()
    sub = vx.j2_substrate(L)
    h = vx.hamiltonian_of(sub)
    order, coords, periods = sub["order"], sub["coarse"], sub["periods"]
    dt = vx.DT_K
    n_steps = int(round(vx.T_K / dt))
    ts = np.arange(n_steps + 1) * dt
    chunk = CHUNK_BIG if L >= 256 else CHUNK
    if group == "crossbg":
        kinds = ("point_amp", "packet", "hidden_sector")
        vacs = ("VPLUS", "VPI", "VMINUS", "ZERO")
        out = {"kinds": {}}
        for kind in kinds:
            d0_by = {}
            for vc in vacs:
                vac = vx.vacuum_shape(vc, sub)
                d0_by[vc] = vx.excitation_delta(kind, vac, sub, eps=vx.EPS_HEADLINE,
                                                a=1.0, mode="abs")
            gens = {vc: scale0.evolve_segments(h, d0_by[vc], dt, n_steps, chunk)
                    for vc in vacs}
            maxdev = 0.0
            coms = {vc: np.zeros((n_steps + 1, 2)) for vc in vacs}
            while True:
                try:
                    segs = {vc: next(gens[vc]) for vc in vacs}
                except StopIteration:
                    break
                k_off = segs[vacs[0]][0]
                rows = {vc: segs[vc][1] for vc in vacs}
                arrs = [rows[vc] for vc in vacs]
                for i in range(len(arrs)):
                    for j in range(i + 1, len(arrs)):
                        maxdev = max(maxdev, float(np.abs(arrs[i] - arrs[j]).max()))
                for vc in vacs:
                    for jj in range(rows[vc].shape[0]):
                        r = rows[vc][jj]
                        s = float(np.linalg.norm(r))
                        coms[vc][k_off + jj] = com(r / s if s > 0 else r, coords,
                                                  order, periods=periods)
            norms = {vc: float(np.linalg.norm(d0_by[vc])) for vc in vacs}
            vels = {}
            for vc in vacs:
                m = ts <= vx.T_FIT
                vels[vc] = {"v": float(np.linalg.norm(coms[vc][m][-1] - coms[vc][m][0])
                                          / max(ts[m][-1] - ts[m][0], 1e-300))}
            out["kinds"][kind] = {"cross_maxdev": maxdev, "norms": norms,
                                  "vels": vels}
        out["elapsed"] = time.time() - t0
        out["L"] = L
        return out
    # fracladder: packet kind x AMPLITUDES, normalized-trajectory dev.
    kind = "packet"
    amps = sorted(vx.AMPLITUDES)
    d0_by = {}
    for a in amps:
        eta = vx.excitation_seed(kind, sub)
        d0_by[a] = (vx.EPS_HEADLINE * eta).astype(np.complex128)
    ref = {}
    fracdev = 0.0
    vels = {}
    for a in amps:
        gen = scale0.evolve_segments(h, d0_by[a], dt, n_steps, chunk)
        com_tr = np.zeros((n_steps + 1, 2))
        for k_off, rows in gen:
            s = float(np.linalg.norm(d0_by[a]))
            nr = rows / s if s > 0 else rows
            for jj in range(rows.shape[0]):
                r = rows[jj]
                sn = float(np.linalg.norm(r))
                com_tr[k_off + jj] = com(r / sn if sn > 0 else r, coords, order,
                                        periods=periods)
            if a == amps[0]:
                ref[k_off] = nr.copy()
            else:
                fracdev = max(fracdev, float(np.abs(nr - ref[k_off]).max()))
        m = ts <= vx.T_FIT
        vels[str(a)] = float(np.linalg.norm(com_tr[m][-1] - com_tr[m][0])
                             / max(ts[m][-1] - ts[m][0], 1e-300))
    # Protection margins on VPLUS/VPI/VMINUS (packet d, sampled steps).
    from scipy.sparse.linalg import expm_multiply as _expm

    margins = {}
    for vc in ("VPLUS", "VPI", "VMINUS"):
        vac = vx.vacuum_shape(vc, sub)
        d0 = vx.excitation_delta(kind, vac, sub, eps=vx.EPS_HEADLINE, a=1.0,
                                 mode="abs")
        E = vx.vacuum_energy(vc)
        mm = float("inf")
        for kk in range(0, n_steps + 1, max(n_steps // 30, 1)):
            t = kk * dt
            dk = np.asarray(_expm(-1.0j * h * t, d0),
                            dtype=np.complex128).ravel() if t > 0 else d0.copy()
            vk = vac * np.exp(-1.0j * E * t)
            mm = min(mm, float(np.min(np.abs(vk) - np.abs(dk))))
        margins[vc] = mm
    return {"L": L, "group": group, "amps": amps, "frac_dev": fracdev,
            "vels": vels, "margins": margins, "elapsed": time.time() - t0}


def run_vacexc_regress(which: str) -> dict:
    from bh_graph import vacexc as vx
    from bh_graph.ballistic import evolve_fixed

    t0 = time.time()
    if which == "L4-crossbg":
        sub = vx.j2_substrate(4)
        h = vx.hamiltonian_of(sub)
        drows_by = {}
        for vc in ("VPLUS", "VPI", "VMINUS", "ZERO"):
            vac = vx.vacuum_shape(vc, sub)
            d0 = vx.excitation_delta("packet", vac, sub, eps=vx.EPS_HEADLINE,
                                     a=1.0, mode="abs")
            n_steps = int(round(vx.T_K / vx.DT_K))
            drows_by[vc] = evolve_fixed(d0, h, vx.DT_K, n_steps)["psi"]
        dev = vx.cross_background_dev(drows_by)
        return {"maxdev": dev.get("maxdev", dev), "ok": vx.is_cross_bg_ok(dev),
                "elapsed": time.time() - t0}
    sub = vx.j2_substrate(28)
    h = vx.hamiltonian_of(sub)
    if which == "L28-frac":
        rows_by_a = {}
        for a in sorted(vx.AMPLITUDES):
            eta = vx.excitation_seed("packet", sub)
            d0 = (vx.EPS_HEADLINE * eta).astype(np.complex128)
            n_steps = int(round(vx.T_K / vx.DT_K))
            rows_by_a[a] = evolve_fixed(d0, h, vx.DT_K, n_steps)["psi"]
        return {"frac_dev": vx.frac_collapse_dev(rows_by_a),
                "elapsed": time.time() - t0}
    # L28-packet: velocity identical across vacua.
    from bh_graph.ballistic import com

    order, coords, periods = sub["order"], sub["coarse"], sub["periods"]
    ts = np.arange(int(round(vx.T_K / vx.DT_K)) + 1) * vx.DT_K
    vels = {}
    for vc in ("VPLUS", "VPI", "VMINUS", "ZERO"):
        vac = vx.vacuum_shape(vc, sub)
        d0 = vx.excitation_delta("packet", vac, sub, eps=vx.EPS_HEADLINE,
                                 a=1.0, mode="abs")
        rows = evolve_fixed(d0, h, vx.DT_K, int(round(vx.T_K / vx.DT_K)))["psi"]
        m = ts <= vx.T_FIT
        rs = np.array([com(r / float(np.linalg.norm(r)), coords, order,
                           periods=periods) for r in rows[m]])
        vels[vc] = float(np.linalg.norm(rs[-1] - rs[0]) / max(ts[m][-1] - ts[m][0], 1e-300))
    vv = np.array(list(vels.values()))
    return {"vels": vels, "spread": float(vv.max() - vv.min()),
            "elapsed": time.time() - t0}


# ---------------------------------------------------------------------------
# vaccomp (VAC-COMP scaling cell)
# ---------------------------------------------------------------------------

def run_vaccomp(L: int) -> dict:
    from bh_graph import vaccomp as vc
    from bh_graph import vacfield as vf

    t0 = time.time()
    formula = vc.zero_count_formula(L)
    sub = vf.j2_substrate(L)
    eu, ev = vf.edge_arrays_of(sub)
    h = vf.hamiltonian_of(sub)

    def sparse_rayleigh(psi):
        psi = np.asarray(psi, dtype=np.complex128)
        return float((np.vdot(psi, h @ psi) / np.vdot(psi, psi)).real)

    rays = {}
    for name in ("VPLUS", "VMINUS"):
        psi = vf.candidate_shape(name, sub, "j2")
        rays[name] = {"E": sparse_rayleigh(psi)}
    try:
        psi_pi = vf.candidate_shape("VPI", sub, "j2")
        rays["VPI"] = {"E": sparse_rayleigh(psi_pi)}
    except ValueError:
        rays["VPI"] = None
    # JOINT ladder on rays (ledger_moves frozen 20000).
    ladders = {}
    for name in ("VPLUS", "VMINUS"):
        psi = vf.candidate_shape(name, sub, "j2")
        E = rays[name]["E"]
        try:
            lad = vc.joint_ladder(psi, sub, h, eu, ev, E, ledger_moves=20000)
            ladders[name] = {"rung": lad.get("rung"), "checks": lad.get("checks")}
        except Exception as e:  # noqa: BLE001 -- filed, never silent
            ladders[name] = {"error": str(e)[:300]}
    if rays["VPI"] is not None:
        psi = vf.candidate_shape("VPI", sub, "j2")
        try:
            lad = vc.joint_ladder(psi, sub, h, eu, ev, rays["VPI"]["E"],
                                  ledger_moves=20000)
            ladders["VPI"] = {"rung": lad.get("rung"), "checks": lad.get("checks")}
        except Exception as e:  # noqa: BLE001
            ladders["VPI"] = {"error": str(e)[:300]}
    # Hidden circle census.
    try:
        circ = vc.circle_probe(L, ledger_moves=20000)
        rungs = [r["rung"] for r in circ["rows"]]
        circle = {"n_joint": sum(1 for r in rungs if r == "JOINT"),
                  "n_background": sum(1 for r in rungs if r == "BACKGROUND"),
                  "n": len(rungs),
                  "rungs": rungs,
                  "alphas": [r["alpha"] for r in circ["rows"]]}
    except Exception as e:  # noqa: BLE001
        circle = {"error": str(e)[:300]}
    # Amplitude ladder on VPLUS.
    try:
        amp = vc.amplitude_family_ladder(vf.candidate_shape("VPLUS", sub, "j2"),
                                         sub, h, eu, ev, -8.0,
                                         ledger_moves=20000)
        amps = {"all_joint": amp.get("all_joint"),
                "rungs": [r["rung"] for r in amp["rows"]]}
    except Exception as e:  # noqa: BLE001
        amps = {"error": str(e)[:300]}
    return {"L": L, "formula": formula, "rays": rays, "ladders": ladders,
            "circle": circle, "amps": amps, "elapsed": time.time() - t0}


def run_vaccomp_regress(which: str) -> dict:
    from bh_graph import vaccomp as vc

    t0 = time.time()
    if which == "L4-census":
        return {"census": vc.zero_eigenspace_census(4),
                "elapsed": time.time() - t0}
    spec = vc.spectral_decomposition(8)
    rows = vc.extremal_rows(spec)
    return {"e_min": spec["e_min"], "e_max": spec["e_max"],
            "n_zero": spec["n_zero"],
            "minus8_mult": (rows["minus8"] or {}).get("multiplicity"),
            "plus8_mult": (rows["plus8"] or {}).get("multiplicity"),
            "elapsed": time.time() - t0}


# ---------------------------------------------------------------------------
# task registry + main
# ---------------------------------------------------------------------------

def all_tasks() -> list:
    tasks = []
    for tag in REPLAY_TAGS:
        tasks.append(f"obs_replay__{tag}")
    for L in scale0.LADDER:
        for sub in ("j2", "sq"):
            tasks.append(f"obs_hausdorff__{sub}-L{L}")
    for L in (64, 128):
        for sub in ("j2", "sq"):
            for oi in range(4):
                tasks.append(f"obs_krylov__{sub}-L{L}-o{oi}")
    for L in (256, 512):
        for sub in ("j2", "sq"):
            for oi in range(16):
                tasks.append(f"obs_krylov__{sub}-L{L}-o{oi}")
    for L in scale0.LADDER:
        for sub in ("j2", "sq"):
            tasks.append(f"obs_dim__{sub}-L{L}")
    for L in scale0.LADDER:
        for bg in ("BG0", "BG+"):
            tasks.append(f"resp__L{L}-{bg}")
    tasks += ["resp_regress__L28-HR", "resp_regress__L28-HI"]
    for L in scale0.LADDER:
        for kk in ("k03", "k05"):
            tasks.append(f"p1__L{L}-{kk}")
    tasks += ["p1_regress__j2-L28", "p1_regress__sq-L30"]
    for L in scale0.LADDER:
        tasks.append(f"pot__L{L}")
    tasks.append("pot_regress__L28")
    for L in scale0.LADDER:
        for fam in ("sym", "anti"):
            tasks.append(f"quot__L{L}-{fam}")
    for L in (64, 128):
        for fam in ("sheet0", "sheet1"):
            tasks.append(f"quot__L{L}-{fam}")
    tasks += ["quot_regress__L28-alg", "quot_regress__L28-wave"]
    for L in scale0.LADDER:
        for fam in ("F1", "F5", "ppinode"):
            tasks.append(f"zero__L{L}-{fam}-pre")
    for L in (64, 128):
        for fam in ("F1", "F5", "ppinode"):
            tasks.append(f"zero__L{L}-{fam}-post")
    tasks += ["zero_regress__headon", "zero_regress__refine"]
    for L in scale0.LADDER:
        for grp in ("crossbg", "fracladder"):
            tasks.append(f"vacexc__L{L}-{grp}")
    tasks += ["vacexc_regress__L4-crossbg", "vacexc_regress__L28-frac",
              "vacexc_regress__L28-packet"]
    for L in scale0.LADDER:
        tasks.append(f"vaccomp__L{L}")
    tasks += ["vaccomp_regress__L4-census", "vaccomp_regress__L8-rows"]
    return tasks


def run_task(key: str) -> dict:
    if key.startswith("obs_replay__"):
        return run_obs_replay(key.split("__")[1])
    if key.startswith("obs_hausdorff__"):
        sub, Ls = key.split("__")[1].split("-L")
        return run_obs_hausdorff(sub, int(Ls))
    if key.startswith("obs_krylov__"):
        rest = key.split("__")[1]
        (subLs, o) = rest.rsplit("-o", 1)
        sub, Ls = subLs.split("-L")
        return run_obs_krylov(sub, int(Ls), int(o))
    if key.startswith("obs_dim__"):
        sub, Ls = key.split("__")[1].split("-L")
        return run_obs_dim(sub, int(Ls))
    if key.startswith("resp_regress__"):
        return run_resp_regress(key.split("__")[1].split("-")[1])
    if key.startswith("resp__L"):
        rest = key.split("__")[1][1:]
        Ls, bg = rest.split("-", 1)
        return run_resp(int(Ls), bg)
    if key.startswith("p1_regress__"):
        return run_p1_regress(key.split("__")[1])
    if key.startswith("p1__L"):
        rest = key.split("__")[1][1:]
        Ls, kk = rest.split("-", 1)
        return run_p1(int(Ls), kk)
    if key == "pot_regress__L28":
        return run_pot_regress()
    if key.startswith("pot__L"):
        return run_pot(int(key.split("__")[1][1:]))
    if key.startswith("quot_regress__"):
        return run_quot_regress(key.split("__")[1].split("-", 1)[1])
    if key.startswith("quot__L"):
        rest = key.split("__")[1][1:]
        Ls, fam = rest.split("-", 1)
        return run_quot(int(Ls), fam)
    if key.startswith("zero_regress__"):
        return run_zero_regress(key.split("__")[1])
    if key.startswith("zero__L"):
        rest = key.split("__")[1][1:]
        Ls, fam, regime = rest.split("-", 2)
        return run_zero(int(Ls), fam, regime)
    if key.startswith("vacexc_regress__"):
        return run_vacexc_regress(key.split("__")[1])
    if key.startswith("vacexc__L"):
        rest = key.split("__")[1][1:]
        Ls, grp = rest.split("-", 1)
        return run_vacexc(int(Ls), grp)
    if key.startswith("vaccomp_regress__"):
        return run_vaccomp_regress(key.split("__")[1])
    if key.startswith("vaccomp__L"):
        return run_vaccomp(int(key.split("__")[1][1:]))
    raise ValueError(f"unknown task {key}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--print-all", action="store_true")
    ap.add_argument("--task", default=None)
    ap.add_argument("--outdir", default="data/scale0")
    args = ap.parse_args()
    if args.print_all:
        for t in all_tasks():
            print(f"{t} :: --task {t}")
        return
    if not args.task:
        raise SystemExit("need --task (or --print-all)")
    t0 = time.time()
    payload = run_task(args.task)
    celldir = os.path.join(args.outdir, "cells")
    os.makedirs(celldir, exist_ok=True)
    rec = {"task": args.task, "meta": {"git_rev": _git_rev(),
                                       "host": socket.gethostname(),
                                       "elapsed": time.time() - t0},
           "payload": payload}
    with open(os.path.join(celldir, f"{args.task}.json"), "w") as f:
        json.dump(jsonable(rec), f)
    print(f"SCALE0 {args.task}: done in {time.time() - t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
