"""QUOT-0 campaign runner (beast only; frozen per QUOT-0 prereg).

Units (one process each, parallelized via xargs -P):
  eigen    fresh eigensystems for NEW tags only (j2p-L28-e01 ham,
           ctrl-L28 lsym+ham); banked eigen consumed READ-ONLY.
  alg      Q-ALG L28 exact-algebra numerics -> quot_alg.json.
  comm     Q-COMM channel task (one --task of wave/diff x pair) -> shard.
  anatomy  Q-SECTOR task (diffusion/POT pattern+ablation per origin,
           wave exactness) -> shard.
  stations replay measurement file (one --dataset/--cell/--set) -> meas+seal.
  blind    vendored blind workup of one dataset dir (shells to the
           UNMODIFIED analyze_obs1_blind.py; sha logged for C6).
  gate     Mixed-reproduction gate (mixed vs banked composite D < 1e-6).

Replay cells reuse OBS-1 cell ids (station-matched) in separate outdirs:
  L42: cells {0: j2-L42, 3: sq-L42, 6: exp-N3528-s0} x sets {0,1,2};
       datasets mixed (all cells), p_plus/p_minus (cell 0 only).
  L28: cell 19 frozen j2-L28 (mixed) + perturbed j2p-L28-e01 (mixed).
  CTRL: cell 21 ctrl-L28 bilayer (mixed).
Seal tags: coord/graph tags (j2-L42, sq-L42, exp-N3528-s0, j2-L28,
j2p-L28-e01, ctrl-L28); the quot replay analyzer maps tags to builders.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

import run_obs0  # noqa: E402
import run_obs1  # noqa: E402
from bh_graph import malus, obs0, obs0r, quot  # noqa: E402
from bh_graph.ballistic import hamiltonian, node_order  # noqa: E402
from bh_graph.formation import j2_torus_coords, j2_torus_graph  # noqa: E402
from scipy import sparse  # noqa: E402

L_HEADLINE = 28
X0 = (7, 14)
X1 = (8, 14)
N_ORIGIN_ANATOMY = 4
REPLAY_L42 = {0: "j2-L42", 3: "sq-L42", 6: "exp-N3528-s0"}
REPLAY_L28_TAG = "j2-L28"
REPLAY_PERT_TAG = "j2p-L28-e01"
REPLAY_CTRL_TAG = "ctrl-L28"


def sha_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def find(name, datadirs):
    for d in datadirs:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f"{name} not in {datadirs}")


def tag_graph(tag):
    """Campaign graph builder (frozen tags + quot control tags)."""
    if tag == REPLAY_PERT_TAG:
        return j2_torus_graph(L_HEADLINE), {"si": 0}
    if tag == REPLAY_CTRL_TAG:
        return quot.bilayer_square_graph(L_HEADLINE), {"si": 0}
    return run_obs0.tag_graph(tag)


def tag_L(tag):  # noqa: N802
    if tag in (REPLAY_PERT_TAG, REPLAY_CTRL_TAG):
        return L_HEADLINE
    return run_obs0.tag_L(tag)


def tag_c3(tag, L):
    """Node -> (x, y, b) map, or None for sheet-less tags."""
    if tag in (REPLAY_CTRL_TAG,):
        return quot.bilayer_square_coords(L)
    if tag.startswith("j2") or tag == REPLAY_PERT_TAG:
        return j2_torus_coords(L)
    return None


# ---------------------------------------------------------------------------
# eigen unit
# ---------------------------------------------------------------------------

def cmd_eigen(args):
    os.makedirs(args.outdir, exist_ok=True)
    if args.tag == REPLAY_PERT_TAG:
        g, _ = tag_graph(args.tag)
        order = sorted(g.nodes())
        c3 = j2_torus_coords(L_HEADLINE)
        h = quot.perturbed_hamiltonian(g, order, c3, eps=quot.EPS_PERT)
        Ew, Vw = np.linalg.eigh(h.toarray())
        obs0.save_system(os.path.join(args.outdir, f"eigen_ham_{args.tag}.npz"),
                         Ew, Vw, order)
        D = obs0.intrinsic_diameter(g, order[0])
        info = {"tag": args.tag, "L": L_HEADLINE, "N": len(order), "D": D,
                "eps": quot.EPS_PERT, "note": "H=-A+V(staggered); lsym/graph=D-identical-to-j2-L28"}
        with open(os.path.join(args.outdir, f"info_{args.tag}.json"), "w") as f:
            json.dump(run_obs0.jsonable(info), f)
        print(f"eigen {args.tag}: N={len(order)} D={D} (ham-only; lsym=reused-banked-j2-L28)", flush=True)
    elif args.tag == REPLAY_CTRL_TAG:
        g, _ = tag_graph(args.tag)
        order = sorted(g.nodes())
        D = obs0.intrinsic_diameter(g, order[0])
        wl, Vl, _ = obs0.lsym_system(g, order)
        Ew, Vw, _ = obs0.hamiltonian_system(g, order)
        obs0.save_system(os.path.join(args.outdir, f"eigen_lsym_{args.tag}.npz"), wl, Vl, order)
        obs0.save_system(os.path.join(args.outdir, f"eigen_ham_{args.tag}.npz"), Ew, Vw, order)
        degs = [g.degree(v) for v in order]
        info = {"tag": args.tag, "L": L_HEADLINE, "N": len(order), "D": D,
                "deg_min": min(degs), "deg_max": max(degs)}
        with open(os.path.join(args.outdir, f"info_{args.tag}.json"), "w") as f:
            json.dump(run_obs0.jsonable(info), f)
        np.save(os.path.join(args.outdir, f"deg_{args.tag}.npy"), np.array(degs))
        print(f"eigen {args.tag}: N={len(order)} D={D}", flush=True)
    else:
        raise ValueError(f"eigen unit only builds new tags, got {args.tag}")


# ---------------------------------------------------------------------------
# alg unit (Q-ALG L28)
# ---------------------------------------------------------------------------

def cmd_alg(args):
    g = j2_torus_graph(L_HEADLINE)
    order = node_order(g)
    c3 = j2_torus_coords(L_HEADLINE)
    h = hamiltonian(g, order=order)
    s = malus.sheet_swap_matrix(order, c3)
    pr = malus.sheet_projectors(order, c3)
    u, cells = malus.symmetric_embedding(order, c3)
    hsq = malus.square_hamiltonian(cells, (L_HEADLINE, L_HEADLINE))
    rng = np.random.default_rng(28)
    inter = [quot.time_evolution_intertwining_err(
        h, u, hsq, (v := rng.normal(size=len(cells)) + 1j * rng.normal(size=len(cells))) / np.linalg.norm(v),
        0.1, 10)["max_err"] for _ in range(5)]
    frozen = []
    for _ in range(3):
        psi = rng.normal(size=len(order)) + 1j * rng.normal(size=len(order))
        psi /= np.linalg.norm(psi)
        pm = pr["P_anti"] @ psi
        pm /= np.linalg.norm(pm)
        frozen.append(quot.frozen_err(h, pm, 0.1, 10)["max_err"])
    psi = rng.normal(size=len(order)) + 1j * rng.normal(size=len(order))
    psi /= np.linalg.norm(psi)
    Ew = np.linalg.eigvalsh(h.toarray())
    n_zero = int(np.sum(np.abs(Ew) <= 1e-9))
    out = {
        "L": L_HEADLINE, "N": len(order),
        "comm_fro": quot.commutator_norm(h, s),
        "anti_dead": quot.anti_dead_norm(h, pr["P_anti"]),
        "intertwining": quot.intertwining_norm(h, u, hsq),
        "U_inter_max": float(max(inter)),
        "frozen_max": float(max(frozen)),
        "decomp": quot.decomposition_err(h, pr, psi, 0.1, 10),
        "n_zero": n_zero,
        "nodal": malus.nodal_count_square(L_HEADLINE),
        "neighbor_sets_identical": quot.is_coarse_neighbor_sets_identical_ok(g, c3),
    }
    os.makedirs(args.outdir, exist_ok=True)
    with open(os.path.join(args.outdir, "quot_alg.json"), "w") as f:
        json.dump(run_obs0.jsonable(out), f)
    print(f"alg L{L_HEADLINE}: " + json.dumps(run_obs0.jsonable(out)), flush=True)


# ---------------------------------------------------------------------------
# comm unit (Q-COMM shards)
# ---------------------------------------------------------------------------

COMM_TASKS = ("wave-sym", "wave-anti", "wave-sheet",
              "diff-sym", "diff-anti", "diff-sheet",
              "wave-proj", "diff-proj")


def cmd_comm(args):
    from bh_graph.formation import j2_torus_coords as _c3

    task = args.task
    datadirs = args.datadir
    wl, Vl, order = obs0.load_system(find("eigen_lsym_j2-L28.npz", datadirs))
    Ew, Vw, order2 = obs0.load_system(find("eigen_ham_j2-L28.npz", datadirs))
    assert order == order2
    with open(find("info_j2-L28.json", datadirs)) as f:
        D = json.load(f)["D"]
    c3 = _c3(L_HEADLINE)
    fam = quot.sector_preparations(order, c3, X0, X1)
    shells = quot.coarse_shells(c3, order, X0, L_HEADLINE, 14)
    tj = list(range(len(order)))
    out = {"task": task, "L": L_HEADLINE, "D": D}
    if task.startswith("wave"):
        ts = np.arange(0.0, quot.T_WAVE + 1e-9, quot.DT_WAVE)
        out["ts"] = {"dt": quot.DT_WAVE, "T": quot.T_WAVE, "n": len(ts)}
        if task == "wave-proj":
            pr = malus.sheet_projectors(order, c3)
            tr_m = quot.wave_traces_general(Ew, Vw, fam["sheet0"], tj, ts)
            tr_p = quot.wave_traces_general(Ew, Vw, pr["P_sym"] @ fam["sheet0"], tj, ts)
            remote = sorted(i for r in shells for i in shells[r] if r >= 1)
            out["remote_max_abs"] = float(np.abs(tr_m[:, remote] - tr_p[:, remote]).max())
            tr_plus = quot.wave_traces_general(Ew, Vw, fam["sym0"], tj, ts)
            with np.errstate(divide="ignore", invalid="ignore"):
                ratio = np.where(tr_m[:, remote] > 1e-300,
                                 tr_plus[:, remote] / tr_m[:, remote], np.nan)
            ok = ratio[np.isfinite(ratio) & (tr_m[:, remote] > 1e-12)]
            out["ratio_med"] = float(np.median(ok)) if ok.size else float("nan")
            out["ratio_maxdev"] = float(np.abs(ok - 2.0).max()) if ok.size else float("nan")
        else:
            pair = {"wave-sym": ("sym0", "sym1"), "wave-anti": ("anti0", "anti1"),
                    "wave-sheet": ("sheet0", "sheet1")}[task]
            tr0 = quot.wave_traces_general(Ew, Vw, fam[pair[0]], tj, ts)
            tr1 = quot.wave_traces_general(Ew, Vw, fam[pair[1]], tj, ts)
            out["cap"] = quot.capacity_curve(tr0, tr1, shells, ts)
    else:
        ts = obs0.diffusion_grid(D)
        out["ts"] = {"n": len(ts), "tmax": float(ts[-1])}
        pos = {v: i for i, v in enumerate(order)}
        node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}

        def as_prob(name):
            if name.startswith("anti"):
                cell = X0 if name == "anti0" else X1
                d0 = np.zeros(len(order))
                d0[pos[node_of[(cell[0], cell[1], 0)]]] = 0.5
                d0[pos[node_of[(cell[0], cell[1], 1)]]] = -0.5
                return d0
            return np.abs(fam[name]) ** 2

        if task == "diff-proj":
            pr = malus.sheet_projectors(order, c3)
            d_m = np.zeros(len(order))
            d_m[pos[node_of[(X0[0], X0[1], 0)]]] = 1.0
            tr_m = quot.diff_traces_general(wl, Vl, d_m, tj, ts)
            tr_p = quot.diff_traces_general(wl, Vl, pr["P_sym"] @ d_m, tj, ts)
            remote = sorted(i for r in shells for i in shells[r] if r >= 1)
            out["remote_max_abs"] = float(np.abs(tr_m[:, remote] - tr_p[:, remote]).max())
            tr_plus = quot.diff_traces_general(wl, Vl, as_prob("sym0"), tj, ts)
            with np.errstate(divide="ignore", invalid="ignore"):
                ratio = np.where(tr_m[:, remote] > 1e-300,
                                 tr_plus[:, remote] / tr_m[:, remote], np.nan)
            ok = ratio[np.isfinite(ratio) & (tr_m[:, remote] > 1e-12)]
            out["ratio_med"] = float(np.median(ok)) if ok.size else float("nan")
            out["ratio_maxdev"] = float(np.abs(ok - 2.0).max()) if ok.size else float("nan")
        else:
            pair = {"diff-sym": ("sym0", "sym1"), "diff-anti": ("anti0", "anti1"),
                    "diff-sheet": ("sheet0", "sheet1")}[task]
            tr0 = quot.diff_traces_general(wl, Vl, as_prob(pair[0]), tj, ts)
            tr1 = quot.diff_traces_general(wl, Vl, as_prob(pair[1]), tj, ts)
            out["cap"] = quot.capacity_curve(tr0, tr1, shells, ts)
    os.makedirs(args.outdir, exist_ok=True)
    with open(os.path.join(args.outdir, f"quot_comm_{task}.json"), "w") as f:
        json.dump(run_obs0.jsonable(out), f)
    print(f"comm {task} done", flush=True)


# ---------------------------------------------------------------------------
# anatomy unit (Q-SECTOR shards)
# ---------------------------------------------------------------------------

def _sheet_slots(g, origin, c3_origin_b, dist):
    """Same/cross sheet slot per node (validation-only grouping)."""
    return {v: ("same" if (c3[v][2] == c3_origin_b) else "cross") for v in dist}


import networkx as nx  # noqa: E402


def cmd_anatomy(args):
    kind, oi = args.kind, int(args.oi)
    datadirs = args.datadir
    g = j2_torus_graph(L_HEADLINE)
    order = node_order(g)
    c3 = j2_torus_coords(L_HEADLINE)
    origins = obs0.sample_origins(len(order), 0, L_HEADLINE)
    origin = order[origins[oi]]
    dist = dict(nx.single_source_shortest_path_length(g, origin))
    idx = {v: i for i, v in enumerate(order)}
    out = {"kind": kind, "oi": oi, "origin": int(origin),
           "origin_cell": [int(v) for v in c3[origin]]}
    if kind == "diff-pattern":
        wl, Vl, _ = obs0.load_system(find("eigen_lsym_j2-L28.npz", datadirs))
        with open(find("info_j2-L28.json", datadirs)) as f:
            D = json.load(f)["D"]
        o_idx = idx[origin]
        tj = [idx[v] for v in dist if 1 <= dist[v] < obs0.wrap_limit(D)]
        tD = obs0.arrival_times_diff(wl, Vl, o_idx, tj, D)
        # Ablation: sym-projected launch (same linear propagator).
        pr = malus.sheet_projectors(order, c3)
        d = np.zeros(len(order))
        d[o_idx] = 1.0
        ts = obs0.diffusion_grid(D)
        tr_sym = quot.diff_traces_general(wl, Vl, pr["P_sym"] @ d, tj, ts)
        tD_sym = {int(j): obs0.cfd_first_peak(tr_sym[:, k], ts)
                  for k, j in enumerate(tj)}
        for tag, taus in (("mixed", tD), ("sym", tD_sym)):
            by_r = {}
            for v in dist:
                if 1 <= dist[v] < obs0.wrap_limit(D) and idx[v] in taus:
                    by_r.setdefault(dist[v], {"same": [], "cross": []})
                    slot = "same" if c3[v][2] == c3[origin][2] else "cross"
                    by_r[dist[v]][slot].append(taus[idx[v]])
            out[tag] = {str(r): obs0.sheet_contrast(by_r[r]["same"], by_r[r]["cross"])
                        for r in sorted(by_r) if r in (1, 2, 3)}
            meso = {"same": [], "cross": []}
            for v in dist:
                if 4 <= dist[v] < obs0.wrap_limit(D) and idx[v] in taus:
                    slot = "same" if c3[v][2] == c3[origin][2] else "cross"
                    meso[slot].append(taus[idx[v]])
            out[tag + "_meso"] = obs0.sheet_contrast(meso["same"], meso["cross"])
    elif kind == "pot-pattern":
        from bh_graph.ballistic import hamiltonian as ham

        z = max(dict(g.degree()).values())
        omega = obs0r.omega_below_edge(z)
        F = obs0r.static_field_phi(g, order, origin, omega)
        out["omega"] = omega
        out["gap_ok"] = F["gap_ok"]
        out["residual"] = F["residual"]
        out["max_imag"] = F["max_imag"]
        # Ablation: sym-drive response (two-pin, matched norm).
        h = sparse.csc_matrix(ham(g, order=order))
        x0y = (c3[origin][0], c3[origin][1])
        node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
        ia = idx[node_of[(x0y[0], x0y[1], 0)]]
        ib = idx[node_of[(x0y[0], x0y[1], 1)]]
        cfgs = quot.sector_pin_configs(ia, ib)
        phi_sym = quot.static_phi_multi(h, cfgs["sym"]["pin_idx"], cfgs["sym"]["s_vec"], omega)
        phi_anti = quot.static_phi_multi(h, cfgs["anti"]["pin_idx"], cfgs["anti"]["s_vec"], omega)
        pr = malus.sheet_projectors(order, c3)
        pa = quot.decompose_solution(phi_anti, pr)
        out["anti_pure"] = float(np.abs(pa["sym"]).max())
        out["anti_support_ok"] = bool(quot.anti_support_ok(
            pa["anti"], order, g, [order[ia], order[ib]], atol=1e-8))
        for tag, phi in (("mixed", F["phi"]), ("sym", phi_sym)):
            by_r = {}
            for v in dist:
                if dist[v] in (1, 2, 3):
                    by_r.setdefault(dist[v], {"same": [], "cross": []})
                    slot = "same" if c3[v][2] == c3[origin][2] else "cross"
                    by_r[dist[v]][slot].append(float(phi[idx[v]]))
            out[tag] = {str(r): obs0.sheet_contrast(by_r[r]["same"], by_r[r]["cross"])
                        for r in sorted(by_r)}
            meso = {"same": [], "cross": []}
            for v in dist:
                if 4 <= dist[v] <= 8:
                    slot = "same" if c3[v][2] == c3[origin][2] else "cross"
                    meso[slot].append(float(phi[idx[v]]))
            out[tag + "_meso"] = obs0.sheet_contrast(meso["same"], meso["cross"])
        # Mixed-vs-sym far-field agreement (coarse r >= 4).
        src = (c3[origin][0], c3[origin][1])
        shells = quot.coarse_shells(c3, order, src, L_HEADLINE, 14)
        far = sorted(i for r in shells for i in shells[r] if r >= quot.POT_FAR_R)
        num = float(np.linalg.norm(F["phi"][far] / np.sqrt(2.0) - phi_sym[far]))
        den = float(np.linalg.norm(phi_sym[far]))
        out["far_rel"] = float(num / den) if den > 0 else float("nan")
        pm = quot.decompose_solution(F["phi"], pr)
        per_r = {}
        for r in sorted(shells):
            ii = shells[r]
            per_r[str(r)] = float(np.linalg.norm(pm["anti"][ii])
                                  / max(float(np.linalg.norm(pm["sym"][ii])), 1e-300))
        out["anti_over_sym_by_r"] = per_r
    elif kind == "lrw":
        norms = quot.diffusion_sector_norms(g, order, c3)
        out.update(norms)
    else:
        raise ValueError(f"unknown anatomy kind {kind}")
    os.makedirs(args.outdir, exist_ok=True)
    with open(os.path.join(args.outdir, f"quot_anatomy_{kind}_o{oi}.json"), "w") as f:
        json.dump(run_obs0.jsonable(out), f)
    print(f"anatomy {kind} o{oi} done", flush=True)


# ---------------------------------------------------------------------------
# stations unit (replay measurement files)
# ---------------------------------------------------------------------------

def _sector_wave_taus(Ew, Vw, o_idx, tj, D, psi0):
    ts = obs0.wave_grid(D)
    P = quot.wave_traces_general(Ew, Vw, psi0, tj, ts)
    return {int(j): obs0.threshold_crossing(P[:, k], ts, obs0.THETA_WAVE)
            for k, j in enumerate(tj)}


def _sector_diff_taus(wl, Vl, o_idx, tj, D, p0, signed):
    ts = obs0.diffusion_grid(D)
    P = quot.diff_traces_general(wl, Vl, p0, tj, ts)
    if signed:
        P = np.abs(P)
    th = {int(j): obs0.threshold_crossing(P[:, k], ts, obs0.THETA_WAVE)
          for k, j in enumerate(tj)}
    cfd = {int(j): obs0.cfd_first_peak(P[:, k], ts) for k, j in enumerate(tj)}
    return th, cfd


def cmd_stations(args):
    cell, aset, dataset = int(args.cell), int(args.set), args.dataset
    tag = args.tag
    datadirs = args.datadir
    outdir = os.path.join(args.outdir, dataset)
    os.makedirs(outdir, exist_ok=True)
    lsym_name = ("eigen_lsym_j2-L28.npz" if tag == REPLAY_PERT_TAG
                 else f"eigen_lsym_{tag}.npz")
    wl, Vl, order = obs0.load_system(find(lsym_name, datadirs))
    Ew, Vw, order2 = obs0.load_system(find(f"eigen_ham_{tag}.npz", datadirs))
    assert order == order2
    info_name = f"info_{tag}.json"
    try:
        with open(find(info_name, datadirs)) as f:
            D = json.load(f)["D"]
    except FileNotFoundError:
        with open(find(f"info_{REPLAY_L28_TAG}.json", datadirs)) as f:
            D = json.load(f)["D"]
    g, _ = tag_graph(tag)
    assert sorted(g.nodes()) == order
    L = tag_L(tag)
    c3 = tag_c3(tag, L)
    idx = {v: i for i, v in enumerate(order)}
    smap, snodes = run_obs1.sample_stations(len(order), cell, aset)
    sidx = [idx[v] for v in snodes]
    if dataset in ("p_plus", "p_minus") and c3 is None:
        raise ValueError(f"dataset {dataset} needs sheets (tag {tag} has none)")

    node_of = None
    if c3 is not None:
        node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}

    def source_vecs(a):
        """Per-station (wave psi0, diff p0, diff_signed, pins, s) by dataset."""
        if dataset == "mixed" or c3 is None:
            d = np.zeros(len(order))
            d[sidx[a]] = 1.0
            return d.astype(complex), d, False, [sidx[a]], [1.0]
        v = snodes[a]
        x, y, _ = c3[v]
        ia = idx[node_of[(x, y, 0)]]
        ib = idx[node_of[(x, y, 1)]]
        s = 1.0 / np.sqrt(2.0)
        if dataset == "p_plus":
            w = np.zeros(len(order), dtype=complex)
            w[ia] = s
            w[ib] = s
            p = np.zeros(len(order))
            p[ia] = 0.5
            p[ib] = 0.5
            return w, p, False, [ia, ib], [s, s]
        w = np.zeros(len(order), dtype=complex)
        w[ia] = s
        w[ib] = -s
        p = np.zeros(len(order))
        p[ia] = 0.5
        p[ib] = -0.5
        return w, p, True, [ia, ib], [s, -s]

    pairs = {}
    for a in range(run_obs1.N_STATIONS):
        tj = [sidx[b] for b in range(run_obs1.N_STATIONS) if b != a]
        w0, p0, signed, pins, svec = source_vecs(a)
        if dataset == "mixed":
            tD, tCFD = run_obs1.diff_readouts(wl, Vl, sidx[a], tj, D)
            tW = obs0.arrival_times_wave(Ew, Vw, sidx[a], tj, D)
        else:
            tW = _sector_wave_taus(Ew, Vw, sidx[a], tj, D, w0)
            tD, tCFD = _sector_diff_taus(wl, Vl, sidx[a], tj, D, p0, signed)
        for b in range(run_obs1.N_STATIONS):
            if b == a:
                continue
            pairs[f"S{a}|S{b}"] = {
                "W": tW[sidx[b]], "D": tD[sidx[b]], "P": None,
                "Dcfd": tCFD[sidx[b]]}

    h = sparse.csc_matrix(hamiltonian(g, order=order))
    if tag == REPLAY_PERT_TAG:
        h = sparse.csc_matrix(
            quot.perturbed_hamiltonian(g, order, c3, eps=quot.EPS_PERT))
    z = max(dict(g.degree()).values())
    omega = obs0r.omega_below_edge(z)
    from bh_graph.driven import is_gap_ok
    assert is_gap_ok(h, omega), f"gap fail {tag} omega={omega}"
    for a in range(run_obs1.N_STATIONS):
        _, _, _, pins, svec = source_vecs(a)
        if len(pins) == 1:
            phi = run_obs1.static_phi_cg(h, pins[0], omega)
        else:
            phi = quot.static_phi_multi(h, pins, svec, omega)
        for b in range(run_obs1.N_STATIONS):
            if b == a:
                continue
            v = float(phi[sidx[b]])
            pairs[f"S{a}|S{b}"]["P"] = v if np.isfinite(v) else None

    meas = {"cell": cell, "set": aset, "n": run_obs1.N_STATIONS, "pairs": pairs}
    run_obs1.audit_meas_schema(meas)
    with open(os.path.join(outdir, f"obs1_meas_cell{cell}_s{aset}.json"), "w") as f:
        json.dump(run_obs0.jsonable(meas), f)
    seal = {"cell": cell, "set": aset, "tag": tag,
            "seed": run_obs1.STATION_SEED_BASE + 100 * cell + aset,
            "stations": smap}
    with open(os.path.join(outdir, f"obs1_seal_cell{cell}_s{aset}.json"), "w") as f:
        json.dump(seal, f)
    cw = sum(1 for r in pairs.values() if r["W"] is not None) / len(pairs)
    cd = sum(1 for r in pairs.values() if r["D"] is not None) / len(pairs)
    cp = sum(1 for r in pairs.values() if r["P"] is not None) / len(pairs)
    print(f"stations dataset={dataset} cell={cell} ({tag}) set={aset}: "
          f"W={cw:.4f} D={cd:.4f} P={cp:.4f}", flush=True)


# ---------------------------------------------------------------------------
# blind + gate units
# ---------------------------------------------------------------------------

def cmd_blind(args):
    repo = os.path.join(os.path.dirname(__file__), "..")
    for rel in ("src/bh_graph/obs1.py", "scripts/analyze_obs1_blind.py"):
        print(f"C6 {rel} sha256={sha_of(os.path.join(repo, rel))}", flush=True)
    measdir = os.path.join(args.datadir, args.dataset)
    cmd = [sys.executable, os.path.join(os.path.dirname(__file__), "analyze_obs1_blind.py"),
           "--measdir", measdir, "--out", os.path.join(args.outdir, f"quot_blind_{args.dataset}.json"),
           "--cells"] + [str(c) for c in args.cells] + ["--sets", "0", "1", "2"]
    os.makedirs(args.outdir, exist_ok=True)
    print("blind: " + " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)
    blob = os.path.join(args.outdir, f"quot_blind_{args.dataset}.json")
    with open(blob + ".sha256", "w") as f:
        f.write(sha_of(blob))


def cmd_gate(args):
    """Mixed-reproduction gate: mixed composite D vs banked OBS-1 D (<1e-6)."""
    import glob

    banked = None
    for d in args.bankdir:
        cand = os.path.join(d, "obs1_blind.json")
        if os.path.exists(cand):
            banked = cand
    if banked is None:
        cands = []
        for d in args.bankdir:
            cands += glob.glob(os.path.join(d, "obs1_blind*.json"))
        raise FileNotFoundError(f"obs1_blind.json not in {args.bankdir} (saw {cands})")
    with open(banked) as f:
        ref = json.load(f)
    with open(os.path.join(args.datadir, "quot_blind_mixed.json")) as f:
        got = json.load(f)
    worst = 0.0
    for c in ("0", "3", "6"):
        for s in ("0", "1", "2"):
            a = np.asarray(ref["cells"][c]["sets"][s]["probes"]["C"]["D"], dtype=float)
            b = np.asarray(got["cells"][c]["sets"][s]["probes"]["C"]["D"], dtype=float)
            worst = max(worst, float(np.abs(a - b).max()))
    print(f"gate: mixed-vs-banked composite max|dD| = {worst:.3e} (bar 1e-6)", flush=True)
    if worst >= 1e-6:
        raise SystemExit(f"GATE FAILED: {worst:.3e} >= 1e-6 -- campaign PAUSES (runner fault)")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="unit", required=True)
    p = sub.add_parser("eigen")
    p.add_argument("--tag", required=True)
    p.add_argument("--outdir", required=True)
    p = sub.add_parser("alg")
    p.add_argument("--outdir", required=True)
    p = sub.add_parser("comm")
    p.add_argument("--task", required=True, choices=COMM_TASKS)
    p.add_argument("--datadir", action="append", required=True)
    p.add_argument("--outdir", required=True)
    p = sub.add_parser("anatomy")
    p.add_argument("--kind", required=True, choices=("diff-pattern", "pot-pattern", "lrw"))
    p.add_argument("--oi", required=True)
    p.add_argument("--datadir", action="append", required=True)
    p.add_argument("--outdir", required=True)
    p = sub.add_parser("stations")
    p.add_argument("--dataset", required=True)
    p.add_argument("--cell", required=True)
    p.add_argument("--set", required=True)
    p.add_argument("--tag", required=True)
    p.add_argument("--datadir", action="append", required=True)
    p.add_argument("--outdir", required=True)
    p = sub.add_parser("blind")
    p.add_argument("--dataset", required=True)
    p.add_argument("--cells", type=int, nargs="+", required=True)
    p.add_argument("--datadir", required=True)
    p.add_argument("--outdir", required=True)
    p = sub.add_parser("gate")
    p.add_argument("--datadir", required=True)
    p.add_argument("--bankdir", action="append", required=True)
    args = ap.parse_args()
    {"eigen": cmd_eigen, "alg": cmd_alg, "comm": cmd_comm,
     "anatomy": cmd_anatomy, "stations": cmd_stations,
     "blind": cmd_blind, "gate": cmd_gate}[args.unit](args)


if __name__ == "__main__":
    main()
