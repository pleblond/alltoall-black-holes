"""DIM-3-0 campaign battery (runner; verdicts filed by dim3_analyze.py).

Preregistered grid (DIM3-PREREG, docs/dim3-prereg.md):
  stations 10 frozen cells x 3 sets (64 opaque stations, W/D/P).
  spread   point R/I impulse, BG0 (+BG+ descriptive legs), T=16/dt=0.05.
  tladder  forerunner diagnosis: fronts at rel-theta 1e-2/1e-3/1e-4 (Amd-1).
  packet   G-a ballistic packets (+reversal, norm).
  pot0     G-b collective-direction 4-rung battery.
  pot1     G-c static existence + equation-exactness (+xi filed).
  switch   G-d source-change front.
  sector   H-a..H-d exact algebra + capacity + diffusion + POT anatomy.
  bilayer  H-e bilayer-cubic control (two worlds).
  hidden   H-f/H-g local-D + remote-blind + virtual sign-reversal census.
  vacuum   I JOINT-ladder census per candidate.

Each task evolves under frozen H = -A ONLY. No fitting, no steering, no
selection. One JSON part per task lands in OUTDIR (default data/dim3).
"""

import argparse
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from bh_graph import dim3, obs0, obs0r, obs1  # noqa: E402
from bh_graph import response as R  # noqa: E402
from bh_graph.ballistic import (com, evolve_fixed, fit_velocity,  # noqa: E402
                                gaussian_packet, hamiltonian, index_of,
                                is_normalized_ok, msd_exponent_rs,
                                node_order, unwrap_trace)
from bh_graph.dim3 import SWAP_XY  # noqa: E402
from bh_graph.driven import (harmonic_pins, is_gap_ok, pinning_evolve,  # noqa: E402
                             steady_predict)
from bh_graph.formation import j2_torus_coords, j2_torus_graph  # noqa: E402
from bh_graph.graphs import build_random_regular  # noqa: E402
from bh_graph.potential import scramble_phases  # noqa: E402
from scipy import sparse  # noqa: E402

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

CELLS = ("j3-L8", "j3-L12", "j3-L16",
         "cb-L10", "cb-L15", "cb-L20",
         "ex-N1024-s0", "ex-N3456-s0", "ex-N8192-s0",
         "j2-L42")
N_STATIONS = 64
STATION_SEED_BASE = 9100

SPREAD_TAGS = ("j3-L8", "j3-L12", "j3-L16", "j3-L20", "j3-L24",
               "j3-L28", "j3-L32",
               "cb-L10", "cb-L15", "cb-L20", "j2-L28")
TLADDER_TAGS = ("j3-L16", "cb-L20", "j2-L28")
TLADDER_LEVELS = (1e-2, 1e-3, 1e-4)
T_END = 16.0
DT = 0.05
FIT_SHELLS = (2, 3, 4, 5, 6, 7, 8, 9, 10)


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
# Tags
# ---------------------------------------------------------------------------

def tag_graph(tag: str):
    """Build the campaign graph for a tag (deterministic)."""
    parts = tag.split("-")
    if parts[0] == "j3":
        return dim3.j3_torus_graph(int(parts[1][1:]), SWAP_XY)
    if parts[0] == "cb":
        return dim3.cubic_torus_graph(int(parts[1][1:]))
    if parts[0] == "bcb":
        return dim3.bilayer_cubic_graph(int(parts[1][1:]))
    if parts[0] == "ex":
        return build_random_regular(int(parts[1][1:]), 12,
                                    seed=int(parts[2][1:]))
    if parts[0] == "j2":
        return j2_torus_graph(int(parts[1][1:]))
    raise ValueError(f"unknown tag {tag}")


def tag_L(tag: str) -> int:  # noqa: N802
    parts = tag.split("-")
    if parts[0] in ("j3", "cb", "bcb", "j2"):
        return int(parts[1][1:])
    return int(parts[1][1:])


def tag_cells(tag: str, g) -> dict:
    """Node -> quotient-cell tuple (readout only, never enters dynamics)."""
    fam = tag.split("-")[0]
    L = tag_L(tag)
    if fam == "j3" or fam == "bcb":
        c4 = dim3.j3_torus_coords(L)
        return {v: (x, y, z) for v, (x, y, z, _) in c4.items()}
    if fam == "cb":
        return dim3.cubic_torus_coords(L)
    if fam == "j2":
        c3 = j2_torus_coords(L)
        return {v: (x, y) for v, (x, y, _) in c3.items()}
    raise ValueError(f"no cells for {tag}")


def tag_sheet(tag: str, v: int):
    fam = tag.split("-")[0]
    if fam in ("j3", "bcb"):
        return dim3.j3_torus_coords(tag_L(tag))[v][3]
    if fam == "j2":
        return j2_torus_coords(tag_L(tag))[v][2]
    return None


def src_node(tag: str, g) -> int:
    """Preregistered source: (L//4, L//2[, L//2]), sheet 0."""
    fam = tag.split("-")[0]
    L = tag_L(tag)
    if fam in ("j3", "bcb"):
        return ((L // 4 * L + L // 2) * L + L // 2) * 2 + 0
    if fam == "cb":
        return (L // 4 * L + L // 2) * L + L // 2
    if fam == "j2":
        return (L // 4 * L + L // 2) * 2 + 0
    raise ValueError(f"no src for {tag}")


def euclidean_shells_of(tag: str, g, src) -> dict:
    """Rounded min-image Euclidean quotient shells (banked coarse_shells rule).

    RESPONSE-0 fronts/fits run on quot.coarse_shells (Euclidean, NOT
    quotient-BFS/Manhattan: Manhattan shells lean inward and bias the
    front fast -- validated by exact replication v=7.947/r2=0.984 on
    J2-L28 with this rule). J3/cb legs use the dimensional port
    dim3.coarse_shells_3d; J2 uses quot.coarse_shells verbatim.
    """
    from bh_graph import quot as Q

    fam = tag.split("-")[0]
    L = tag_L(tag)
    order = node_order(g)
    # rmax covers the whole torus (J2: banked 25 verbatim; bigger 3D tori
    # need more: corner at sqrt(ndim)*L/2).
    ndim = 2 if fam == "j2" else 3
    rmax = max(SPREAD_RMAX,
               int(math.ceil(math.sqrt(ndim) * L / 2.0)) + 1)
    if fam == "j2":
        c3 = j2_torus_coords(L)
        cell = (c3[src][0], c3[src][1])
        return Q.coarse_shells(c3, order, cell, L, rmax)
    if fam in ("j3", "bcb"):
        c4 = dim3.j3_torus_coords(L)
        return dim3.coarse_shells_3d(c4, order, c4[src][:3], L, rmax)
    if fam == "cb":
        cc = dim3.cubic_torus_coords(L)
        c4 = {v: (x, y, z, 0) for v, (x, y, z) in cc.items()}
        return dim3.coarse_shells_3d(c4, order, cc[src], L, rmax)
    raise ValueError(f"no shells for {tag}")


# E/F/G-d spread protocol (banked RESPONSE-0 rule, dimensionally ported).
SPREAD_RMAX = 25    # banked coarse_shells rmax
SPREAD_RCAP = 16    # banked rmax_cap for remote-peak/analysis
SPREAD_REL_THETA = 1e-3
SPREAD_FLOORS = {"psi": 1e-12, "rho": 1e-14, "bond": 1e-14}
# Bloch-Manhattan velocity bound per family (derived from the locked law,
# pre-data): j3 4/sin-axis x3 = 12; cb 2/sin-axis x3 = 6; j2 banked 8.
SPREAD_VMAX = {"j3": 12.0, "bcb": 6.0, "cb": 6.0, "j2": 8.0}


def spread_window(r: float, L: int, fam: str):
    """Causal peak window (r/1.5Vmax, (L-r)/Vmax).

    J2 values verbatim banked ((r/12, (L-r)/8)); J3/cb carry the same
    1.5x precursor-exclusion ratio with their derived Bloch-Manhattan
    bounds. None when empty (shell filed without a peak, never imputed).
    """
    v = SPREAD_VMAX[fam]
    return R.arrival_window(float(r), int(L), v_hi=1.5 * v, v=v)


# ---------------------------------------------------------------------------
# stations (Stage C measurement)
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
    tag = CELLS[cell]
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    g = tag_graph(tag)
    order = node_order(g)
    assert order == list(range(len(order)))
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
    with open(os.path.join(outdir, f"dim3_meas_cell{cell}_s{aset}.json"),
              "w") as f:
        json.dump(jsonable(meas), f)
    seal = {"cell": cell, "set": aset, "tag": tag,
            "seed": STATION_SEED_BASE + 100 * cell + aset,
            "stations": smap}
    with open(os.path.join(outdir, f"dim3_seal_cell{cell}_s{aset}.json"),
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

def _bg_state(bg: str, tag: str, g, order):
    n = len(order)
    if bg == "BG0":
        return np.zeros(n, dtype=np.complex128)
    if bg == "BG+":
        fam = tag.split("-")[0]
        if fam == "j3":
            sub = dim3.j3_substrate(tag_L(tag))
            assert sub["order"] == order
            return dim3.candidate_shape("VPLUS", sub)
        return np.full(n, 1.0 / math.sqrt(n), dtype=np.complex128)
    raise ValueError(f"unknown bg {bg}")


def cmd_spread(args):
    tag, bg, kind = args.tag, args.bg, args.kind
    amp = float(args.amp)
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    g = tag_graph(tag)
    order = node_order(g)
    pos = index_of(order)
    h = R.hamiltonian(g, order)
    eu, ev = R.edge_index_arrays(g, order)
    fam = tag.split("-")[0]
    L = tag_L(tag)
    src = src_node(tag, g)
    iu = pos[src]
    n_steps = int(round(T_END / DT))
    ts = np.arange(n_steps + 1) * DT
    bg0 = _bg_state(bg, tag, g, order)
    eps = amp if kind == "R" else amp * 1j
    d0 = R.point_source(len(order), iu, complex(eps))
    has_bg = float(np.linalg.norm(bg0)) > 0
    rows_bg = R.evolve(bg0, h, DT, n_steps)["psi"] if has_bg else None
    rec_d = R.evolve(d0, h, DT, n_steps)
    rows_d = rec_d["psi"]
    rows = rows_d if rows_bg is None else rows_bg + rows_d
    rho_bg = None if rows_bg is None else np.abs(rows_bg) ** 2
    qs = euclidean_shells_of(tag, g, src)
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
        drho = np.abs(R.node_density(rows[t])
                      - (0.0 if rho_bg is None else rho_bg[t]))
        b_full = R.bond_B(rows[t], eu, ev)
        j_full = R.bond_J(rows[t], eu, ev)
        if rows_bg is not None:
            b_full = b_full - R.bond_B(rows_bg[t], eu, ev)
            j_full = j_full - R.bond_J(rows_bg[t], eu, ev)
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
        # Banked rule: remote peak over shells 1..16 (shell 1 included).
        rcap = min(max_shell, SPREAD_RCAP)
        remote_peak = max(float(tr[:, s].max()) for s in range(1, rcap + 1))
        theta = max(SPREAD_REL_THETA * remote_peak, floor)
        arrivals = {s: R.arrival_time(tr[:, s], ts, theta)
                    for s in FIT_SHELLS if s <= max_shell}
        use = [s for s in FIT_SHELLS if arrivals.get(s) is not None]
        front = R.front_velocity({s: arrivals[s] for s in use}, use) \
            if len(use) >= 3 else {"v": None, "r2": None, "n": 0}
        peaks, tstars, windows = {}, {}, {}
        for s in FIT_SHELLS:
            if s > max_shell:
                continue
            win = spread_window(s, L, fam)
            windows[s] = list(win) if win else None
            pk = R.peak_in_window(tr[:, s], ts, *win) if win else None
            if pk is None:
                continue
            # Amendment-1 A1 (v2): interior TRUE peaks only. A windowed
            # maximum is data iff (i) grid room remains past it inside the
            # window, (ii) the trace strictly falls somewhere in the
            # remainder (local max, not a rising-edge cutoff), (iii) it
            # exceeds the detection threshold (not precursor noise).
            ts_idx = int(round(pk["tstar"] / DT))
            rem = tr[ts_idx + 1:, s][ts[ts_idx + 1:] <= win[1]]
            if (rem.size > 0 and rem.min() < pk["Rmax"]
                    and pk["Rmax"] > theta):
                peaks[s] = pk["Rmax"]
                tstars[s] = pk["tstar"]
        fit = dim3.fit_exponent(peaks, FIT_SHELLS[0], FIT_SHELLS[-1])
        return {"theta": theta, "remote_peak": remote_peak,
                "arrivals": arrivals, "front": front, "peaks": peaks,
                "tstars": tstars, "windows": windows, "fit": fit}

    a_psi = analyze(psi_tr, SPREAD_FLOORS["psi"])
    a_rho = analyze(rho_tr, SPREAD_FLOORS["rho"])
    a_j = analyze(j_tr, SPREAD_FLOORS["bond"])
    rec = {"tag": tag, "bg": bg, "kind": kind, "amp": amp, "src": src,
           "T": T_END, "dt": DT, "n": len(order),
           "theta": {k: v["theta"]
                     for k, v in (("psi", a_psi), ("rho", a_rho),
                                   ("J", a_j))},
           "peaks": {k: v["peaks"]
                     for k, v in (("psi", a_psi), ("rho", a_rho),
                                   ("J", a_j))},
           "tstars": {k: v["tstars"]
                      for k, v in (("psi", a_psi), ("rho", a_rho),
                                    ("J", a_j))},
           "windows": a_psi["windows"],
           "fits": {k: v["fit"]
                    for k, v in (("psi", a_psi), ("rho", a_rho),
                                  ("J", a_j))},
           "arrivals": a_psi["arrivals"], "front": a_psi["front"],
           "fronts": {k: v["front"]
                      for k, v in (("psi", a_psi), ("rho", a_rho),
                                    ("J", a_j))},
           "bmax": bmax,
           "norms_drift": float(np.abs(rec_d["norms"]
                                       - rec_d["norms"][0]).max())}
    fn = os.path.join(outdir, f"dim3_spread_{tag}_{bg}_{kind}_{amp:g}.json")
    with open(fn, "w") as f:
        json.dump(jsonable(rec), f)
    print(f"spread {tag} {bg} {kind} amp={amp:g}: "
          f"a_psi={rec['fits']['psi']['alpha']:.3f} "
          f"a_rho={rec['fits']['rho']['alpha']:.3f} "
          f"a_J={rec['fits']['J']['alpha']:.3f} v={rec['front'].get('v')} "
          f"bmax={bmax:.1e}", flush=True)


# ---------------------------------------------------------------------------
# tladder (Amendment-1 A3 forerunner diagnosis; characterization, no gates)
# ---------------------------------------------------------------------------

def cmd_tladder(args):
    tag = args.tag
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    g = tag_graph(tag)
    order = node_order(g)
    pos = index_of(order)
    h = R.hamiltonian(g, order)
    src = src_node(tag, g)
    iu = pos[src]
    n_steps = int(round(T_END / DT))
    ts = np.arange(n_steps + 1) * DT
    rows = R.evolve(R.point_source(len(order), iu, 1.0), h, DT,
                    n_steps)["psi"]
    qs = euclidean_shells_of(tag, g, src)
    max_shell = max(qs)
    tr = np.zeros((len(ts), max_shell + 1))
    for r, members in qs.items():
        if members:
            m = np.asarray(members, dtype=int)
            tr[:, r] = np.abs(rows[:, m]).max(axis=1)
    rcap = min(max_shell, SPREAD_RCAP)
    remote_peak = max(float(tr[:, s].max()) for s in range(1, rcap + 1))
    out = {"tag": tag, "remote_peak": remote_peak, "levels": {}}
    for rel in TLADDER_LEVELS:
        theta = max(rel * remote_peak, SPREAD_FLOORS["psi"])
        arrivals = {s: R.arrival_time(tr[:, s], ts, theta)
                    for s in FIT_SHELLS if s <= max_shell}
        use = [s for s in FIT_SHELLS if arrivals.get(s) is not None]
        front = R.front_velocity({s: arrivals[s] for s in use}, use) \
            if len(use) >= 3 else {"v": None, "r2": None, "n": 0}
        out["levels"][rel] = {"theta": theta, "arrivals": arrivals,
                              "front": front}
    with open(os.path.join(outdir, f"dim3_tladder_{tag}.json"), "w") as f:
        json.dump(jsonable(out), f)
    print(f"tladder {tag}: " + " ".join(
        f"{rel:g}(v={out['levels'][rel]['front'].get('v')})"
        for rel in TLADDER_LEVELS), flush=True)


# ---------------------------------------------------------------------------
# packet (G-a)
# ---------------------------------------------------------------------------

def _quotient_coords_3d(tag, g, order):
    cell_of = tag_cells(tag, g)
    ndim = len(next(iter(cell_of.values())))
    return {v: tuple(float(x) for x in cell_of[v]) for v in order}, ndim


def cmd_packet(args):
    tag = args.tag
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    L = tag_L(tag)
    g = tag_graph(tag)
    order = node_order(g)
    coords, ndim = _quotient_coords_3d(tag, g, order)
    periods = (float(L),) * ndim
    fam = tag.split("-")[0]
    # Apparatus validity (pre-data transverse-spread formula
    # s(T) = s*sqrt(1 + (T/2m*s^2)^2), m* = 1/4 J3, 1/2 cubic):
    # s(T) <= L/4 keeps the circular-mean COM readout clean (no
    # wrap-teleport). J3's light mass needs wider-slower packets than
    # the cubic control (whose s=L/8, T=8 config passes validation).
    if fam == "j3":
        sigma, dt, n_steps = L / 6.0, 0.1, 40
    else:
        sigma, dt, n_steps = L / 8.0, 0.1, 80
    r0 = (L / 4.0, L / 2.0, L / 2.0)[:ndim]
    v_bloch = 4.0 * math.sin(0.3) if fam == "j3" else 2.0 * math.sin(0.3)
    h = hamiltonian(g, order=order)
    out = {"tag": tag, "sigma": sigma, "dt": dt, "n_steps": n_steps,
           "v_bloch": v_bloch}
    for tagk, kval in (("plus", 0.3), ("minus", -0.3)):
        k = (kval,) + (0.0,) * (ndim - 1)
        psi0 = gaussian_packet(coords, order, r0, k, sigma, periods=periods)
        rec = evolve_fixed(psi0, h, dt, n_steps)
        rs = np.array([com(p, coords, order, periods=periods)
                       for p in rec["psi"]])
        ts = np.arange(n_steps + 1) * dt
        ru = unwrap_trace(rs, periods)
        fit = fit_velocity(ru, ts)
        alpha = msd_exponent_rs(ru, ts)
        out[tagk] = {"v": fit["v"], "speed": fit["speed"], "r2": fit["r2"],
                     "alpha": alpha,
                     "norm_ok": is_normalized_ok(rec["psi"][-1]),
                     "norm_drift": float(np.abs(rec["norms"] - 1.0).max())}
    vp = np.asarray(out["plus"]["v"], dtype=float)
    vm = np.asarray(out["minus"]["v"], dtype=float)
    cos_pm = float(vp @ vm / (np.linalg.norm(vp) * np.linalg.norm(vm)))
    out["cos_pm"] = cos_pm
    with open(os.path.join(outdir, f"dim3_packet_{tag}.json"), "w") as f:
        json.dump(jsonable(out), f)
    print(f"packet {tag}: v+={out['plus']['speed']:.4f} "
          f"vBloch={v_bloch:.4f} cos={cos_pm:.4f}", flush=True)


# ---------------------------------------------------------------------------
# pot0 (G-b collective battery)
# ---------------------------------------------------------------------------

def _edges_3d(tag, g, order):
    cell_of = tag_cells(tag, g)
    L = float(tag_L(tag))
    pos = index_of(order)
    edges = []
    for u, v in g.edges():
        a = np.array(cell_of[u], dtype=float)
        b = np.array(cell_of[v], dtype=float)
        d = b - a
        d -= np.round(d / L) * L
        if len(d) == 2:
            d = np.array([d[0], d[1], 0.0])
        edges.append((pos[u], pos[v], float(d[0]), float(d[1]), float(d[2])))
    return edges


POT0_KX = 0.3  # banked POT-0 KX
POT0_T = 10.0  # banked POT-0 T
POT0_DT = 0.1  # banked POT-0 DT
POT0_N = int(round(POT0_T / POT0_DT))
POT0_C_GRID = tuple(round(c * 0.1, 10) for c in range(11))  # banked


def _evolve_case_3d(g, order, coords, periods, edges, cfield, L, psi0,
                    dt=POT0_DT, n_steps=POT0_N):
    """Banked POT-0 _evolve_case readout, dimensionally ported (3-vector J).

    Same instruments (gaussian prep outside; evolve_fixed; com/unwrap;
    msd exponent; velocity autocorr; fit_velocity; D/J flux traces;
    spectral coherence at prep). Returns the banked per-case keys.
    """
    from bh_graph.ballistic import velocity_autocorr

    h = hamiltonian(g, order=order)
    spec = dim3.spectral_coherence_3d(psi0, order, cfield, L)
    rec = evolve_fixed(psi0, h, dt, n_steps)
    ts = np.arange(rec["psi"].shape[0]) * dt
    rs = unwrap_trace(
        np.array([com(p, coords, order, periods=periods)
                  for p in rec["psi"]]), periods=periods)
    alpha = msd_exponent_rs(rs, ts)
    cv = velocity_autocorr(rs, ts)
    fit = fit_velocity(rs, ts)
    tr = dim3.d_trace_3d(rec["psi"], edges)
    jnet = np.asarray(tr["J_net"], dtype=float)
    return {"prep_C": spec["C"], "prep_M": spec["M_eff"],
            "mean_D": float(tr["D"].mean()),
            "max_D": float(tr["D"].max()),
            "mean_J": [float(jnet[:, i].mean()) for i in range(3)],
            "alpha": float(alpha),
            "cv_mean50": float(np.mean(cv[:50])),
            "v": [float(x) for x in fit["v"]],
            "speed": float(fit["speed"]), "r2": float(fit["r2"]),
            "norm_dev": float(np.abs(rec["norms"] - 1.0).max())}


def cmd_pot0(args):
    tag = args.tag
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    from bh_graph.potential import dephasing_family

    L = tag_L(tag)
    g = tag_graph(tag)
    order = node_order(g)
    coords, ndim = _quotient_coords_3d(tag, g, order)
    periods = (float(L),) * ndim
    edges = _edges_3d(tag, g, order)
    # Banked POT-0 sigma verbatim (4.0); sizes chosen so s(10) <= L/4
    # (j3-L24, cb-L20) per the transverse-spread formula (see cmd_packet).
    sigma = 4.0
    r0 = (L / 4.0, L / 2.0, L / 2.0)[:ndim]
    cfield = tag_cells(tag, g)
    out = {"tag": tag, "KX": POT0_KX, "T": POT0_T, "dt": POT0_DT,
           "C_GRID": list(POT0_C_GRID)}
    case = lambda psi0: _evolve_case_3d(g, order, coords, periods, edges,
                                        cfield, L, psi0)
    # A: symmetric source (k=0).
    out["A"] = case(gaussian_packet(coords, order, r0, (0.0,) * ndim,
                                    sigma, periods=periods))
    # B: coherent packet + reversal (banked KX).
    pkt0 = gaussian_packet(coords, order, r0,
                           (POT0_KX,) + (0.0,) * (ndim - 1),
                           sigma, periods=periods)
    pktm0 = gaussian_packet(coords, order, r0,
                            (-POT0_KX,) + (0.0,) * (ndim - 1),
                            sigma, periods=periods)
    out["B"] = case(pkt0)
    out["Bm"] = case(pktm0)
    # C: gradient rung (k = c*KX multipliers, banked) + dephase leg.
    grad = [case(gaussian_packet(
        coords, order, r0, (c * POT0_KX,) + (0.0,) * (ndim - 1),
        sigma, periods=periods)) for c in POT0_C_GRID]
    fam = dephasing_family(pkt0, tuple(POT0_C_GRID), seed=0)
    noise = [case(fam[float(c)]) for c in POT0_C_GRID]
    out["C"] = {"gd": [r["mean_D"] for r in grad],
                "gv": [r["speed"] for r in grad],
                "gc": [r["prep_C"] for r in grad],
                "nd": [r["mean_D"] for r in noise],
                "nc": [r["prep_C"] for r in noise]}
    # D: scramble kill + restore + dephase correlation pool (banked).
    out["D_scr"] = case(scramble_phases(pkt0, seed=0))
    out["D_rest"] = case(gaussian_packet(
        coords, order, r0, (POT0_KX,) + (0.0,) * (ndim - 1),
        sigma, periods=periods))
    out["pool"] = {
        "C": [r["prep_C"] for r in noise]
             + [out["B"]["prep_C"], out["D_scr"]["prep_C"],
                out["D_rest"]["prep_C"]],
        "D": [r["mean_D"] for r in noise]
             + [out["B"]["mean_D"], out["D_scr"]["mean_D"],
                out["D_rest"]["mean_D"]]}
    with open(os.path.join(outdir, f"dim3_pot0_{tag}.json"), "w") as f:
        json.dump(jsonable(out), f)
    print(f"pot0 {tag}: A_D={out['A']['mean_D']:.4f} "
          f"B_D={out['B']['mean_D']:.4f}", flush=True)


# ---------------------------------------------------------------------------
# pot1 (G-c static)
# ---------------------------------------------------------------------------

def cmd_pot1(args):
    tag = args.tag
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    g = tag_graph(tag)
    order = node_order(g)
    pos = index_of(order)
    h = hamiltonian(g, order=order)
    z = max(dict(g.degree()).values())
    omega = obs0r.omega_below_edge(z)
    assert is_gap_ok(h, omega)
    src = src_node(tag, g)
    phi = steady_predict(h, [pos[src]], np.array([1.0]), omega)
    # Equation residual (exactness gate).
    n = len(order)
    a = (h - omega * sparse.eye(n)).tocsc()
    bulk = np.ones(n, dtype=bool)
    bulk[pos[src]] = False
    res = a @ phi
    den = float(np.linalg.norm((h[bulk, :][:, [pos[src]]]).toarray()))
    resid = float(np.linalg.norm(res[bulk])) / den if den > 0 else float("nan")
    # Radial profile on Euclidean quotient shells (xi filed descriptively).
    shells = euclidean_shells_of(tag, g, src)
    prof = {}
    for r, members in shells.items():
        m = np.asarray(members, dtype=int)
        prof[r] = float(np.abs(phi[m]).max())
    rs = sorted(r for r in prof if 1 <= r <= 8 and prof[r] > 0)
    if len(rs) >= 3:
        slope = float(np.polyfit(rs, np.log([prof[r] for r in rs]), 1)[0])
        xi = float(-1.0 / slope) if slope < 0 else float("nan")
    else:
        xi, slope = float("nan"), float("nan")
    rec = {"tag": tag, "omega": omega, "z": z, "resid": resid,
           "xi": xi, "slope": slope, "profile": prof}
    with open(os.path.join(outdir, f"dim3_pot1_{tag}.json"), "w") as f:
        json.dump(jsonable(rec), f)
    print(f"pot1 {tag}: omega={omega} resid={resid:.1e} xi={xi}", flush=True)


# ---------------------------------------------------------------------------
# switch (G-d source-change front)
# ---------------------------------------------------------------------------

def cmd_switch(args):
    tag = args.tag
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    g = tag_graph(tag)
    order = node_order(g)
    pos = index_of(order)
    h = hamiltonian(g, order=order)
    z = max(dict(g.degree()).values())
    omega = obs0r.omega_below_edge(z)
    src = src_node(tag, g)
    iu = pos[src]
    phi = steady_predict(h, [iu], np.array([1.0]), omega)
    n_steps = int(round(T_END / DT))
    ts = np.arange(n_steps + 1) * DT
    free = R.evolve(phi, h, DT, n_steps)["psi"]
    drv = pinning_evolve(phi, h, DT, n_steps, [iu],
                         harmonic_pins(np.array([1.0]), omega, DT))["psi"]
    dev = np.abs(free - drv)
    shells = euclidean_shells_of(tag, g, src)
    max_shell = max(shells)
    tr = np.zeros((len(ts), max_shell + 1))
    for r, members in shells.items():
        if not members:
            continue
        m = np.asarray(members, dtype=int)
        tr[:, r] = dev[:, m].max(axis=1)
    # Threshold: relative 1e-3 x remote peak over shells 1..16 + floor
    # (banked RESPONSE-0 switch rule verbatim).
    rcap = min(max_shell, SPREAD_RCAP)
    remote = max(float(tr[:, s].max()) for s in range(1, rcap + 1))
    theta = max(1e-3 * remote, 1e-12)
    arrivals = {}
    for r in FIT_SHELLS:
        if r <= max_shell:
            arrivals[r] = R.arrival_time(tr[:, r], ts, theta)
    ok = [r for r in FIT_SHELLS if arrivals.get(r) is not None]
    front = R.front_velocity({r: arrivals[r] for r in ok}, ok) \
        if len(ok) >= 3 else {"v": None, "r2": None, "n": 0}
    rec = {"tag": tag, "omega": omega, "theta": theta, "arrivals": arrivals,
           "front": front}
    with open(os.path.join(outdir, f"dim3_switch_{tag}.json"), "w") as f:
        json.dump(jsonable(rec), f)
    print(f"switch {tag}: v={front.get('v')} r2={front.get('r2')}",
          flush=True)


# ---------------------------------------------------------------------------
# sector (H-a..H-d)
# ---------------------------------------------------------------------------

def cmd_sector(args):
    tag = args.tag
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    from bh_graph import quot as Q

    L = tag_L(tag)
    g = tag_graph(tag)
    order = node_order(g)
    c4 = dim3.j3_torus_coords(L)
    h = R.hamiltonian(g, order)
    s = dim3.sheet_swap_matrix(order, c4)
    pr = dim3.sheet_projectors(order, c4)
    u, cells = dim3.symmetric_embedding(order, c4)
    hq = dim3.cubic_hamiltonian(cells, (L, L, L))
    rec = {"tag": tag,
           "comm": dim3.commutator_norm(h, s),
           "dead": dim3.anti_dead_norm(h, pr["P_anti"]),
           "inter": dim3.intertwining_norm(h, u, hq)}
    # H-b wave capacity (Krylov full-node traces).
    x0 = (L // 4, L // 2, L // 2)
    x1 = ((L // 4 + 1) % L, L // 2, L // 2)
    preps = dim3.sector_preparations_3d(order, c4, x0, x1)
    dt, n_steps = 0.05, 200
    ts = np.arange(n_steps + 1) * dt
    shells = dim3.coarse_shells_3d(c4, order, x0, L, 3 * L // 2)
    traces = {}
    for name, psi0 in preps.items():
        rows = R.evolve(psi0, h, dt, n_steps)["psi"]
        traces[name] = (np.abs(rows) ** 2)
    cap_pos = Q.capacity_curve(traces["sym0"], traces["sym1"], shells, ts)
    cap_neg = Q.capacity_curve(traces["anti0"], traces["anti1"], shells, ts)
    cap_sheet = Q.capacity_curve(traces["sheet0"], traces["sheet1"], shells,
                                 ts)
    rec["cap_pos"] = {r: v["C"] for r, v in cap_pos.items()}
    rec["cap_neg"] = {r: v["C"] for r, v in cap_neg.items()}
    rec["cap_sheet"] = {r: v["C"] for r, v in cap_sheet.items()}
    # H-c diffusion sector separation.
    lrw = dim3.lrw_matrix(g, order)
    sd = s.toarray()
    ld = lrw.toarray()
    rec["lrw_comm"] = float(np.abs(ld @ sd - sd @ ld).max())
    p0 = (np.abs(preps["sym0"]) ** 2)
    tall = np.arange(0, 20.01, 0.25)
    pall = dim3.krylov_diff_traces(lrw, 0, list(range(len(order))), tall) * 0.0
    # Evolve the symmetric distribution directly (full-node, chunked).
    from scipy.sparse.linalg import expm_multiply as _expm

    gen = -sparse.csr_matrix(lrw, dtype=float)
    p = p0.copy()
    sym_w, anti_w = [1.0], [0.0]
    cur = [p.copy()]
    dt_d = 0.25
    for _ in range(len(tall) - 1):
        p = np.asarray(_expm(gen * dt_d, p), dtype=float).ravel()
        cur.append(p.copy())
        w = dim3.sheet_weights(p.astype(np.complex128),
                               {"P_sym": pr["P_sym"], "P_anti": pr["P_anti"]})
        sym_w.append(w["w_sym"] / p.sum())
        anti_w.append(w["w_anti"] / p.sum())
    rec["diff_sym_w_min"] = float(min(sym_w))
    rec["diff_anti_w_max"] = float(max(np.abs(anti_w)))
    rec["diff_mass_drift"] = float(
        max(abs(float(c.sum()) - 1.0) for c in cur))
    # H-d POT sector anatomy.
    pos = index_of(order)
    node_of = {(x, y, z, b): v for v, (x, y, z, b) in c4.items()}
    ia = pos[node_of[(x0[0], x0[1], x0[2], 0)]]
    ib = pos[node_of[(x0[0], x0[1], x0[2], 1)]]
    cfgs = Q.sector_pin_configs(ia, ib)
    z = max(dict(g.degree()).values())
    omega = obs0r.omega_below_edge(z)
    h_csc = sparse.csc_matrix(hamiltonian(g, order=order))
    phis = {k: Q.static_phi_multi(h_csc, v["pin_idx"], v["s_vec"], omega)
            for k, v in cfgs.items()}
    decomp = {k: Q.decompose_solution(p, pr) for k, p in phis.items()}
    rec["pot_anti_support"] = Q.anti_support_ok(decomp["anti"]["anti"],
                                                order, g, [ia, ib])
    rec["pot_anti_support_mixed"] = Q.anti_support_ok(
        decomp["mixed"]["anti"], order, g, [ia, ib])
    # Far-field agreement mixed vs sym/sqrt2 (POT_REL_BAR rule).
    far = []
    for v, (x, y, zz, _) in c4.items():
        dd = min(abs(x - x0[0]), L - abs(x - x0[0])) + \
            min(abs(y - x0[1]), L - abs(y - x0[1])) + \
            min(abs(zz - x0[2]), L - abs(zz - x0[2]))
        if dd >= 3:
            far.append(pos[v])
    far = np.asarray(far, dtype=int)
    num = np.abs(phis["mixed"][far] - phis["sym"][far] / math.sqrt(2.0)).max()
    den = np.abs(phis["mixed"][far]).max()
    rec["pot_far_rel"] = float(num / den) if den > 0 else float("nan")
    # Banked-verbatim far-field (QUOT-0 rule: L2 over coarse shells r>=4,
    # ||mixed/sqrt2 - sym||/||sym||). DESCRIPTIVE, not gated: banked J2
    # measured 0.38 (FAIL on the naive sqrt2 bar -- defect-induced
    # monopole shift; mechanism confirmed in stronger form). Filed here
    # for direct J2/J3 comparison.
    far4 = sorted(i for r in shells for i in shells[r] if r >= Q.POT_FAR_R)
    num2 = float(np.linalg.norm(
        phis["mixed"][far4] / math.sqrt(2.0) - phis["sym"][far4]))
    den2 = float(np.linalg.norm(phis["sym"][far4]))
    rec["pot_far_rel_L2"] = float(num2 / den2) if den2 > 0 else float("nan")
    # Banked "stronger form" readout (DESCRIPTIVE): mixed-drive anti part
    # far from the source cell (J2: exactly 0 at coarse r>=1).
    far1 = sorted(i for r in shells for i in shells[r] if r >= 1)
    rec["pot_mixed_anti_r1_max"] = float(
        np.abs(decomp["mixed"]["anti"][far1]).max())
    with open(os.path.join(outdir, f"dim3_sector_{tag}.json"), "w") as f:
        json.dump(jsonable(rec), f)
    print(f"sector {tag}: comm={rec['comm']:.1e} dead={rec['dead']:.1e} "
          f"inter={rec['inter']:.1e} lrw_comm={rec['lrw_comm']:.1e} "
          f"pot_far={rec['pot_far_rel']:.2e}", flush=True)


# ---------------------------------------------------------------------------
# bilayer (H-e control)
# ---------------------------------------------------------------------------

def cmd_bilayer(args):
    tag = args.tag
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    from bh_graph import obs1_reveal as OR

    L = tag_L(tag)
    g = tag_graph(tag)
    order = node_order(g)
    assert order == list(range(len(order)))
    D = obs0.intrinsic_diameter(g, order[0])
    h = sparse.csc_matrix(hamiltonian(g, order=order))
    lrw = dim3.lrw_matrix(g, order)
    z = max(dict(g.degree()).values())
    omega = obs0r.omega_below_edge(z)
    ts_w = obs0.wave_grid(D)
    ts_d = obs0.diffusion_grid(D)
    _, snodes = sample_stations(len(order), 100, 0)
    sidx = [int(v) for v in snodes]
    pairs = {}
    for a in range(N_STATIONS):
        tj = [sidx[b] for b in range(N_STATIONS) if b != a]
        pw = dim3.krylov_wave_traces(h, sidx[a], tj, ts_w)
        pd = dim3.krylov_diff_traces(lrw, sidx[a], tj, ts_d)
        phi = dim3.static_phi_cg(h, sidx[a], omega)
        for k, b in enumerate([x for x in range(N_STATIONS) if x != a]):
            v = float(phi[sidx[b]])
            pairs[f"S{a}|S{b}"] = {
                "W": obs0.threshold_crossing(pw[:, k], ts_w, obs0.THETA_WAVE),
                "D": obs0.threshold_crossing(pd[:, k], ts_d, obs0.THETA_WAVE),
                "P": v if np.isfinite(v) else None}
    sys.path.insert(0, os.path.dirname(__file__))
    from analyze_obs1_blind import analyze_cell_set
    rec = analyze_cell_set({"n": N_STATIONS, "pairs": pairs})
    Dmat = rec["probes"]["C"]["D"]
    c4 = dim3.bilayer_cubic_coords(L)
    sheets = [c4[v][3] for v in snodes]
    rep = OR.sheet_report(np.asarray(Dmat, dtype=float), sheets)
    out = {"tag": tag, "contrast": rep["contrast"],
           "n_same": rep["n_same"], "n_cross": rep["n_cross"],
           "vol_d": rec["probes"]["C"]["vol"]["d"],
           "dstar": rec["probes"]["C"]["dstar"]}
    with open(os.path.join(outdir, f"dim3_bilayer_{tag}.json"), "w") as f:
        json.dump(jsonable(out), f)
    print(f"bilayer {tag}: contrast={rep['contrast']} d={out['vol_d']}",
          flush=True)


# ---------------------------------------------------------------------------
# hidden (H-f/H-g)
# ---------------------------------------------------------------------------

def cmd_hidden(args):
    tag = args.tag
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    from bh_graph import hidden as H
    from bh_graph import hiddenbr as HBR
    from bh_graph import quot as Q

    L = tag_L(tag)
    g = tag_graph(tag)
    order = node_order(g)
    pos = index_of(order)
    c4 = dim3.j3_torus_coords(L)
    h = R.hamiltonian(g, order)
    h_csc = sparse.csc_matrix(hamiltonian(g, order=order))
    eu, ev = R.edge_index_arrays(g, order)
    n = len(order)
    plus = np.full(n, 1.0 / math.sqrt(n), dtype=np.complex128)
    cell_r = (L // 2, L // 2, L // 2)
    cell_q = ((L // 2 + 1) % L, L // 2, L // 2)
    d_r = dim3.hidden_delta_3d(order, c4, cell_r)
    d_q = dim3.hidden_delta_3d(order, c4, cell_q)
    dip = dim3.hidden_dipole_3d(order, c4, cell_r, cell_q)
    pr = dim3.sheet_projectors(order, c4)
    pairs = {
        "sign": (plus + d_r, plus - d_r),
        "phase": (plus + d_r, plus + 1j * d_r),
        "shape": (plus + d_r, plus + dip),
        "amplitude": (plus + d_r, plus + 2.0 * d_r),
    }
    # Normalize pairs to matched Q (HIDDEN-0 qmatch rule), P+ matched by
    # construction (identical plus component).
    npairs = {}
    for name, (a, b) in pairs.items():
        qa = float(np.vdot(a, a).real)
        qb = float(np.vdot(b, b).real)
        qm = math.sqrt(qa * qb)
        npairs[name] = (a * math.sqrt(qm / qa), b * math.sqrt(qm / qb))
    # Neighborhood R (quotient r <= 1) + internal edges.
    nodes_r = []
    for v, (x, y, zz, _) in c4.items():
        if (min(abs(x - cell_r[0]), L - abs(x - cell_r[0]))
                + min(abs(y - cell_r[1]), L - abs(y - cell_r[1]))
                + min(abs(zz - cell_r[2]), L - abs(zz - cell_r[2])) <= 1):
            nodes_r.append(pos[v])
    nodes_r = np.asarray(nodes_r, dtype=int)
    in_r = np.zeros(n, dtype=bool)
    in_r[nodes_r] = True
    emask = in_r[np.asarray(eu, dtype=int)] & in_r[np.asarray(ev, dtype=int)]
    # Dense systems for exact remote readouts (L=8: N=1024).
    Ew, Vw, _ = obs0.hamiltonian_system(g, order)
    wl, Vl, _ = obs0.lsym_system(g, order)
    D = obs0.intrinsic_diameter(g, order[0])
    ts_w = obs0.wave_grid(D)
    ts_d = obs0.diffusion_grid(D)
    shells = dim3.coarse_shells_3d(c4, order, cell_r, L, 3 * L // 2)
    remote = [r for r in shells if r >= 2]
    z = max(dict(g.degree()).values())
    omega = obs0r.omega_below_edge(z)
    node_of = {(x, y, zz, b): v for v, (x, y, zz, b) in c4.items()}
    ia = pos[node_of[(cell_r[0], cell_r[1], cell_r[2], 0)]]
    ib = pos[node_of[(cell_r[0], cell_r[1], cell_r[2], 1)]]
    out = {"tag": tag, "legs": {}}
    for name, (a, b) in npairs.items():
        loc = H.local_distance(a, b, np.asarray(eu), np.asarray(ev),
                               nodes_r, emask)
        rw = H.remote_tv_wave(a, b, Ew, Vw, shells, ts_w)
        pa, pb = (np.abs(a) ** 2), (np.abs(b) ** 2)
        rd = H.remote_tv_diff(pa / pa.sum(), pb / pb.sum(), wl, Vl,
                              shells, ts_d)
        pf = H.pot_pair_fields(h_csc, (ia, ib), a, b, omega)
        dphi = np.asarray(pf["dphi"], dtype=float)
        rem_idx = np.concatenate([np.asarray(shells[r], dtype=int)
                                  for r in remote])
        out["legs"][name] = {
            "local": loc,
            "local_ok": H.is_locally_distinguishable_ok(loc["D"]),
            "wave_Dmax": {r: rw["Dmax"][r] for r in remote},
            "wave_ok": H.is_remote_blind_ok(rw["Dmax"], remote),
            "diff_Dmax": {r: rd["Dmax"][r] for r in remote},
            "diff_ok": H.is_remote_blind_ok(rd["Dmax"], remote),
            "pot_remote_max": float(np.abs(dphi[rem_idx]).max()),
            "pot_exact_zero": bool(float(np.abs(dphi[rem_idx]).max()) == 0.0)}
    # H-g virtual sign-reversal census on the sign pair (no graph mutation).
    a, b = npairs["sign"]
    ea = float(np.vdot(a, h @ a).real / np.vdot(a, a).real)
    eb = float(np.vdot(b, h @ b).real / np.vdot(b, b).real)
    la = HBR.ledger_array(g, a, order)
    lb = HBR.ledger_array(g, b, order)
    nflip = 0
    for i in range(len(la)):
        if HBR.is_sign_flip(float(la[i]), float(lb[i])):
            nflip += 1
    out["hg"] = {"e_a": ea, "e_b": eb, "de": abs(ea - eb),
                 "n_edges": len(la), "n_flip": nflip}
    with open(os.path.join(outdir, f"dim3_hidden_{tag}.json"), "w") as f:
        json.dump(jsonable(out), f)
    print(f"hidden {tag}: " + " ".join(
        f"{k}(loc={v['local']['D']:.1e} w={v['wave_ok']} d={v['diff_ok']} "
        f"pot={v['pot_remote_max']:.1e})" for k, v in out["legs"].items())
        + f" flips={nflip}/{len(la)}", flush=True)


# ---------------------------------------------------------------------------
# vacuum (Stage I)
# ---------------------------------------------------------------------------

def cmd_vacuum(args):
    L = int(args.L)
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    from bh_graph import vacfield as V
    from bh_graph.continuum import div_J

    sub = dim3.j3_substrate(L)
    g, order = sub["graph"], sub["order"]
    h = hamiltonian(g, j=1.0, order=order)
    eu, ev = R.edge_index_arrays(g, order)
    eu = np.asarray(eu, dtype=int)
    ev = np.asarray(ev, dtype=int)
    c4 = sub["c4"]
    pos = index_of(order)
    node_of = {(x, y, z, b): v for v, (x, y, z, b) in c4.items()}
    plaquettes = [[pos[node_of[(x, y, z, 0)]] for (x, y, z) in loop]
                  for loop in
                  [[dim3.cubic_torus_coords(L)[i] for i in face]
                   for face in dim3.cubic_face_plaquettes(L)]]
    eclass = dim3.edge_classes_j3(sub)
    out = {"L": L, "cands": {}}
    for name in ("VPLUS", "VPI", "VMINUS", "ZERO"):
        psi = dim3.candidate_shape(name, sub)
        rec = {}
        if name == "ZERO":
            bj = V.bj_of(psi, eu, ev)
            rec["bmax"] = float(np.abs(bj["B"]).max())
            rec["rho_zero"] = bool(float(np.abs(psi).max()) == 0.0)
            out["cands"][name] = rec
            continue
        e_ref = {"VPLUS": -12.0, "VPI": 12.0, "VMINUS": 0.0}[name]
        e = dim3.rayleigh_energy(psi, h)
        rec["energy"] = e
        rec["eigen_res"] = dim3.eigen_residual(psi, h, e_ref)
        # Stationarity.
        st = V.stationarity_run(psi, h, eu, ev)
        rec["stationary"] = {"rho_drift": st["rho_drift"],
                             "B_drift": st["B_drift"],
                             "J_drift": st["J_drift"],
                             "phase_rate": st.get("phase_rate"),
                             "ok": V.is_stationary_ok(st, e_ref)}
        # Current census (3D-native).
        bj = V.bj_of(psi, eu, ev)
        div = div_J(psi, g, order, 1.0)
        circ = V.plaquette_circulations(psi, order, eu, ev, plaquettes)
        disp = dim3.j3_edge_displacements(sub, eu, ev)
        jj = bj["J"]
        fvec = (jj[:, None] * disp).sum(axis=0)
        cur = {"edge_max": float(np.abs(jj).max()) if len(jj) else 0.0,
               "div_max": float(np.abs(div).max()),
               "circ_max": float(np.abs(circ).max()) if len(circ) else 0.0,
               "flux": {"maxabs": float(np.abs(fvec).max())}}
        rec["current"] = cur
        rec["current_ok"] = V.is_current_free_ok(cur)
        # Phase invariance + amplitude scaling (generic).
        ph = V.phase_invariance(psi, g, order, eu, ev)
        rec["phase_ok"] = V.is_phase_invariant_ok(ph)
        sc = V.amplitude_scaling(psi, g, order, eu, ev)
        rec["scaling_ok"] = V.is_scaling_ok(sc)
        rec["scaling"] = {k: sc[k] for k in ("Q", "Bmax", "Jmax", "Eabs")}
        rec["scaling"]["normed_spread"] = sc["normed_spread"]
        rec["scaling"]["normed_trivial"] = sc["normed_trivial"]
        if name == "VMINUS":
            # Banked E-vacuous rule (VAC-FIELD Amendment-4): E(a) == 0 at
            # all amplitudes replaces the slope-2 Eabs leg for E=0 states.
            from bh_graph.vacfield import AMPLITUDES
            e_allzero = all(V.energy_of(a * psi, g, order) == 0.0
                            for a in AMPLITUDES)
            rec["scaling_e_vacuous"] = e_allzero
        # Stress (3D-native per-class).
        inc = V.incident_stats(bj["B"], eu, ev, len(order))
        per = {}
        for cls in ("SX", "SY", "SZ", "FX", "FY", "FZ"):
            vals = []
            for k in range(len(eu)):
                akey, bkey = order[int(eu[k])], order[int(ev[k])]
                kk = (akey, bkey) if akey < bkey else (bkey, akey)
                if eclass.get(kk) == cls:
                    vals.append(bj["B"][k])
            per[cls] = V.uniformity_stats(np.array(vals))
        stress = {"S_stats": V.uniformity_stats(inc["S"]),
                  "V_stats": V.uniformity_stats(inc["V"]),
                  "B_stats": V.uniformity_stats(bj["B"]),
                  "per_class_B": per}
        rec["stress"] = {k: (v if k == "per_class_B" else v)
                         for k, v in stress.items()}
        rec["stress_ok"] = V.is_stress_balanced_ok(stress)
        # Sector weights.
        pr = dim3.sheet_projectors(order, c4)
        w = dim3.sheet_weights(psi, pr)
        rec["sector"] = w
        # Virtual M1 ledger (sampled; patterns gated, values filed).
        led = V.m1_ledger(psi, g, order)
        rec["ledger"] = led["stats"]
        out["cands"][name] = rec
    with open(os.path.join(outdir, f"dim3_vacuum_L{L}.json"), "w") as f:
        json.dump(jsonable(out), f)
    print(f"vacuum L={L}: " + " ".join(
        f"{k}(st={v.get('stationary', {}).get('ok')} "
        f"cur={v.get('current_ok')} ph={v.get('phase_ok')} "
        f"sc={v.get('scaling_ok')} str={v.get('stress_ok')})"
        for k, v in out["cands"].items() if k != "ZERO"), flush=True)


# ---------------------------------------------------------------------------
# print-all (xargs driver source)
# ---------------------------------------------------------------------------

def cmd_print_all(_args):
    lines = []
    for c in range(len(CELLS)):
        for s in range(3):
            lines.append(f"stations --cell {c} --set {s}")
    for tag in SPREAD_TAGS:
        for kind in ("R", "I"):
            lines.append(f"spread --tag {tag} --bg BG0 --kind {kind} --amp 1.0")
    for tag in ("j3-L8", "j3-L12", "j3-L16"):
        lines.append(f"spread --tag {tag} --bg BG+ --kind R --amp 1.0")
    for tag in TLADDER_TAGS:
        lines.append(f"tladder --tag {tag}")
    for tag in ("j3-L16", "j3-L20", "cb-L15"):
        lines.append(f"packet --tag {tag}")
    for tag in ("j3-L24", "cb-L20"):
        lines.append(f"pot0 --tag {tag}")
    for tag in ("j3-L12", "j3-L16", "cb-L15"):
        lines.append(f"pot1 --tag {tag}")
    for tag in ("j3-L16", "cb-L20"):
        lines.append(f"switch --tag {tag}")
    for tag in ("j3-L8", "j3-L12", "j3-L16"):
        lines.append(f"sector --tag {tag}")
    lines.append("bilayer --tag bcb-L8")
    lines.append("hidden --tag j3-L8")
    for L in (4, 8, 12):
        lines.append(f"vacuum --L {L}")
    for ln in lines:
        print(ln)
    print(f"# {len(lines)} tasks", flush=True)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="unit", required=True)
    p = sub.add_parser("stations")
    p.add_argument("--cell", type=int, required=True)
    p.add_argument("--set", type=int, required=True)
    p.add_argument("--outdir", default="data/dim3")
    p = sub.add_parser("spread")
    p.add_argument("--tag", required=True)
    p.add_argument("--bg", required=True)
    p.add_argument("--kind", required=True)
    p.add_argument("--amp", default="1.0")
    p.add_argument("--outdir", default="data/dim3")
    p = sub.add_parser("packet")
    p.add_argument("--tag", required=True)
    p.add_argument("--outdir", default="data/dim3")
    p = sub.add_parser("pot0")
    p.add_argument("--tag", required=True)
    p.add_argument("--outdir", default="data/dim3")
    p = sub.add_parser("pot1")
    p.add_argument("--tag", required=True)
    p.add_argument("--outdir", default="data/dim3")
    p = sub.add_parser("switch")
    p.add_argument("--tag", required=True)
    p.add_argument("--outdir", default="data/dim3")
    p = sub.add_parser("sector")
    p.add_argument("--tag", required=True)
    p.add_argument("--outdir", default="data/dim3")
    p = sub.add_parser("bilayer")
    p.add_argument("--tag", required=True)
    p.add_argument("--outdir", default="data/dim3")
    p = sub.add_parser("hidden")
    p.add_argument("--tag", required=True)
    p.add_argument("--outdir", default="data/dim3")
    p = sub.add_parser("vacuum")
    p.add_argument("--L", type=int, required=True)
    p.add_argument("--outdir", default="data/dim3")
    p = sub.add_parser("tladder")
    p.add_argument("--tag", required=True)
    p.add_argument("--outdir", default="data/dim3")
    sub.add_parser("print-all")
    args = ap.parse_args()
    {"stations": cmd_stations, "spread": cmd_spread, "packet": cmd_packet,
     "pot0": cmd_pot0, "pot1": cmd_pot1, "switch": cmd_switch,
     "sector": cmd_sector, "bilayer": cmd_bilayer, "hidden": cmd_hidden,
     "vacuum": cmd_vacuum, "tladder": cmd_tladder,
     "print-all": cmd_print_all}[args.unit](args)


if __name__ == "__main__":
    main()
