"""RESPONSE-0 campaign battery (runner; verdicts filed in DEFERRED.md).

Preregistered grid (RESPONSE0-PREREG, docs/DEFERRED.md):
  spec:    L=8 Krylov-vs-spectral agreement (G1).
  headline:H-R/H-I (L=28, BG0, unit R/I impulse at (7,14,0), T=16/dt=0.05).
  battery: BG+/BGpi/BG-/BGM x R/I impulses, eps=1e-3 (G4/G5/G13/G14).
  ladder:  BG0 eps ladder / BG+ amplitude ladder / fractional ladder (G5).
  kick:    BG+ phase/amplitude kicks, eps=1e-2.
  region:  BG0 x {edge,cell,ball1,patch} + BG+ x cell.
  sector:  BG0 sym/anti/sheet0/sheet1 matched preparations (G8).
  dipole:  BG0 two-node 0/pi/2 phase-structured B-carrier (B-blindness control).
  quot:    quotient delta + lift comparison + bond lift (G9).
  green:   path-61 + J2-L8 retarded-Green static identity (G10).
  switch:  path-61 + J2-L28 source-switch protocol (G11).
  linear:  BG0 + BG+ two-source linearity + cross terms (G12).
  cov:     translate/rot90/reflectx/sheet-swap covariance (G6).

Thresholds: relative 1e-3 x remote peak per (task, observable) + absolute
floors (psi 1e-12, rho/bond 1e-14); headline absolute thresholds additionally
reported. Front fits on quotient shells 2..10 (r2 > 0.9 gate).

Each cell evolves under frozen H = -A ONLY (response.evolve, independently
implemented; ballistic cross-check is a G2 cell-level comparison). No fitting,
no steering, no selection. Parts + aggregate JSON land in RESPONSE0_PART
(default /tmp/response0_parts); headline rows are saved as npy sidecars.
"""

import json
import math
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

from bh_graph import response as R
from bh_graph.driven import steady_predict
from bh_graph.formation import j2_torus_coords, j2_torus_graph
from bh_graph.quot import coarse_shells

OUT = os.environ.get("RESPONSE0_PART", "/tmp/response0_parts")
os.makedirs(OUT, exist_ok=True)

L_J2 = int(os.environ.get("RESPONSE0_L", "28"))
T_END = float(os.environ.get("RESPONSE0_T", "16.0"))
DT = float(os.environ.get("RESPONSE0_DT", "0.05"))
N_STEPS = int(round(T_END / DT))
SRC_CELL = (7, 14)
FIT_SHELLS = (2, 3, 4, 5, 6, 7, 8, 9, 10)
REL_THETA = 1e-3
FLOORS = {"psi": 1e-12, "rho": 1e-14, "bond": 1e-14}


def _ts():
    return np.arange(N_STEPS + 1) * DT


def _graph_shells(g, src):
    dist = dict(nx_single_source(g, src))
    shells = {}
    for v, d in dist.items():
        shells.setdefault(d, []).append(v)
    return shells


def nx_single_source(g, src):
    import networkx as nx

    return nx.single_source_shortest_path_length(g, src)


def _bond_shells(eu, ev, node_shell_of):
    out = {}
    for e in range(len(eu)):
        s = min(node_shell_of[int(eu[e])], node_shell_of[int(ev[e])])
        out.setdefault(s, []).append(e)
    return out


def _shell_max_traces(node_rows, node_shells_idx):
    """Per-shell max|.| traces for node-valued rows."""
    return {s: np.abs(np.asarray(node_rows)[:, ii]).max(axis=1)
            for s, ii in node_shells_idx.items()}


def _analyze_shell_traces(tr, ts, floor, kind, cell, obs, ledger, rmax_cap=16):
    """Arrivals + front fit + Rmax/integrated + ledger rows for shell traces."""
    ts = np.asarray(ts)
    remote_peak = 0.0
    for s, t in tr.items():
        if s >= 1 and s <= rmax_cap:
            remote_peak = max(remote_peak, float(t.max()))
    theta = max(REL_THETA * remote_peak, floor)
    arrivals = {}
    for s in sorted(tr):
        if s > rmax_cap:
            continue
        arrivals[s] = R.arrival_time(tr[s], ts, theta)
    fit = None
    use = [s for s in FIT_SHELLS if arrivals.get(s) is not None]
    if len(use) >= 3:
        fv = R.front_velocity({s: arrivals[s] for s in use}, use)
        fit = {"v": fv["v"], "r2": fv["r2"], "shells": use}
    for s in sorted(tr):
        if s > rmax_cap:
            continue
        win = R.arrival_window(float(s), L_J2)
        pk = R.peak_in_window(tr[s], ts, *win) if win else None
        ig = R.integrated_in_window(tr[s], ts, *win) if win else None
        tw = R.time_windows(L_J2, float(s))
        wrap = bool(win is not None and win[1] >= tw["t_wrap"] - 1e-12)
        ledger.append(R.ledger_event(cell["support"], cell["kind"], cell["bg"],
                                     cell["eps"], obs, kind, float(s),
                                     arrivals[s],
                                     pk["Rmax"] if pk else None,
                                     pk["tstar"] if pk else None,
                                     ig["abs"] if ig else None,
                                     ig["signed"] if ig else None,
                                     theta, win[0] if win else None,
                                     win[1] if win else None, wrap))
    return {"theta": theta, "remote_peak": remote_peak, "arrivals": arrivals, "fit": fit}


def _j2_ctx(L):
    g = j2_torus_graph(L)
    order = list(range(2 * L * L))
    c3 = j2_torus_coords(L)
    h = R.hamiltonian(g, order)
    eu, ev = R.edge_index_arrays(g, order)
    return {"g": g, "order": order, "c3": c3, "h": h, "eu": eu, "ev": ev}


def _run_response_cell(cell):
    """Evolve (bg, delta) and analyze dpsi/drho/dB/dJ shells. Returns result."""
    t0 = time.time()
    L = cell["L"]
    ctx = _j2_ctx(L)
    g, order, c3, h, eu, ev = (ctx["g"], ctx["order"], ctx["c3"], ctx["h"],
                               ctx["eu"], ctx["ev"])
    idx = {v: i for i, v in enumerate(order)}
    src_node = (SRC_CELL[0] * L + SRC_CELL[1]) * 2 + cell.get("sheet", 0)
    iu = idx[src_node]
    bg = R.background_state(cell["bg"], g, order, c3, L)
    if cell.get("amp") is not None:
        bg = R.scaled_background(bg, cell["amp"])
    if cell["src"] == "point-R":
        d0 = R.point_source(len(order), iu, cell["eps"])
    elif cell["src"] == "point-I":
        d0 = R.point_source(len(order), iu, 1j * cell["eps"])
    elif cell["src"] in ("edge", "cell", "ball1", "patch"):
        center = src_node if cell["src"] != "edge" else next(iter(g.edges(src_node)))
        m = R.region_mask(cell["src"], g, order, center, c3, L)
        d0 = R.region_source(m, cell["eps"])
    elif cell["src"] == "phase":
        d0 = R.phase_kick(bg, iu, cell["eps"])["dpsi_exact"]
    elif cell["src"] == "amplitude":
        d0 = R.amplitude_kick(bg, iu, cell["eps"])["dpsi_exact"]
    elif cell["src"] in ("sym", "anti", "sheet0", "sheet1"):
        sib = (SRC_CELL[0] * L + SRC_CELL[1]) * 2 + 1
        d0 = np.zeros(len(order), dtype=np.complex128)
        if cell["src"] == "sym":
            d0[iu] = cell["eps"] / math.sqrt(2.0)
            d0[idx[sib]] = cell["eps"] / math.sqrt(2.0)
        elif cell["src"] == "anti":
            d0[iu] = cell["eps"] / math.sqrt(2.0)
            d0[idx[sib]] = -cell["eps"] / math.sqrt(2.0)
        elif cell["src"] == "sheet0":
            d0[iu] = cell["eps"]
        else:
            d0[idx[sib]] = cell["eps"]
    elif cell["src"] == "dipole":
        # Sheet dipole: eps|u> + i eps|sib(u)> (same sublattice, relative
        # phase -> breaks chiral-reality -> the BG0 B-carrier).
        sib = (SRC_CELL[0] * L + SRC_CELL[1]) * 2 + 1
        d0 = np.zeros(len(order), dtype=np.complex128)
        d0[iu] = cell["eps"]
        d0[idx[sib]] = 1j * cell["eps"]
    else:
        raise ValueError(f"unknown src {cell['src']}")
    n_steps = cell.get("n_steps", N_STEPS)
    dt = cell.get("dt", DT)
    ts = np.arange(n_steps + 1) * dt
    rec_bg = R.evolve(bg, h, dt, n_steps)["psi"] if float(np.linalg.norm(bg)) > 0 else None
    rec_d = R.evolve(d0, h, dt, n_steps)["psi"]
    # observable traces
    psi_rows = rec_d if rec_bg is None else rec_bg + rec_d
    rho = np.abs(psi_rows) ** 2
    drho = rho - (0.0 if rec_bg is None else np.abs(rec_bg) ** 2)
    b_all = (np.conj(psi_rows[:, eu]) * psi_rows[:, ev]).real
    j_all = 2.0 * (np.conj(psi_rows[:, eu]) * psi_rows[:, ev]).imag
    if rec_bg is not None:
        b_all = b_all - (np.conj(rec_bg[:, eu]) * rec_bg[:, ev]).real
        j_all = j_all - 2.0 * (np.conj(rec_bg[:, eu]) * rec_bg[:, ev]).imag
    # shells
    gs = _graph_shells(g, src_node)
    gs_idx = {s: [idx[v] for v in vv] for s, vv in gs.items()}
    qs_idx = coarse_shells(c3, order, SRC_CELL, L, 25)
    node_shell_of = {}
    for s, ii in gs_idx.items():
        for i in ii:
            node_shell_of[i] = s
    q_of = {}
    for s, ii in qs_idx.items():
        for i in ii:
            q_of[i] = s
    gb = _bond_shells(eu, ev, node_shell_of)
    qb = _bond_shells(eu, ev, q_of)
    ledger = []
    out = {"cid": cell["cid"], "kind": cell["kind"], "bg": cell["bg"],
           "src": cell["src"], "eps": cell["eps"], "L": L,
           "amp": cell.get("amp"),
           "norm_drift": float(np.abs(np.linalg.norm(rec_d, axis=1) - np.linalg.norm(d0)).max())}
    psi_tr = _shell_max_traces(rec_d, gs_idx)
    out["g_psi"] = _analyze_shell_traces(psi_tr, ts, FLOORS["psi"], "gshell",
                                         cell, "dpsi", ledger)
    qpsi_tr = _shell_max_traces(rec_d, {s: ii for s, ii in qs_idx.items() if ii})
    out["q_psi"] = _analyze_shell_traces(qpsi_tr, ts, FLOORS["psi"], "qshell",
                                         cell, "dpsi", ledger)
    rho_tr = {s: np.abs(drho[:, ii]).max(axis=1) for s, ii in qs_idx.items() if ii}
    out["q_rho"] = _analyze_shell_traces(rho_tr, ts, FLOORS["rho"], "qshell",
                                         cell, "drho", ledger)
    b_tr = {s: np.abs(b_all[:, ee]).max(axis=1) for s, ee in qb.items()}
    out["q_B"] = _analyze_shell_traces(b_tr, ts, FLOORS["bond"], "qshell",
                                       cell, "dB", ledger)
    j_tr = {s: np.abs(j_all[:, ee]).max(axis=1) for s, ee in qb.items()}
    out["q_J"] = _analyze_shell_traces(j_tr, ts, FLOORS["bond"], "qshell",
                                       cell, "dJ", ledger)
    # decomp identity + first-order fraction at sample times
    devs, fracs = [], []
    for k in range(0, n_steps + 1, max(n_steps // 8, 1)):
        p0 = np.zeros(len(order)) if rec_bg is None else rec_bg[k]
        rr = R.delta_observables(p0, rec_d[k], eu, ev)
        devs.append(max(float(np.abs(rr["d_rho"] - rr["d_rho1"] - rr["d_rho2"]).max()),
                        float(np.abs(rr["d_B"] - rr["d_B1"] - rr["d_B2"]).max()),
                        float(np.abs(rr["d_J"] - rr["d_J1"] - rr["d_J2"]).max())))
        if rec_bg is not None:
            n1 = float(np.linalg.norm(rr["d_rho1"]))
            n2 = float(np.linalg.norm(rr["d_rho2"]))
            fracs.append(n1 / max(n1 + n2, 1e-300))
    out["decomp_max"] = float(max(devs))
    out["first_order_frac"] = fracs
    # chi spot-check at t ~ T/2 for nonzero backgrounds + point sources:
    # K_vu(t) recovered exactly from the evolved single-node impulse.
    out["chi_spot"] = None
    if rec_bg is not None and cell["src"] in ("point-R", "point-I"):
        k = n_steps // 2
        p0 = rec_bg[k]
        d0u = complex(cell["eps"]) if cell["src"] == "point-R" else 1j * cell["eps"]
        rr = R.delta_observables(p0, rec_d[k], eu, ev)
        errs = []
        for vn in [order[(i * 197) % len(order)] for i in range(6)]:
            vi = idx[vn]
            kvu = rec_d[k, vi] / d0u
            chi = R.chi_rho(p0[vi], kvu)
            errs.append(abs(R.apply_chi(chi, d0u.real, d0u.imag) - rr["d_rho1"][vi]))
        out["chi_spot"] = float(max(errs))
    # sector weights (all cells; anti-frozen gate lives in sector cells)
    partner = R.sheet_partner(order, c3)
    w0 = R.sector_weights(rec_d[0] / max(float(np.linalg.norm(rec_d[0])), 1e-300),
                          partner)
    w1 = R.sector_weights(rec_d[-1] / max(float(np.linalg.norm(rec_d[-1])), 1e-300),
                          partner)
    out["sector_drift"] = float(abs(w1["w_plus"] - w0["w_plus"])
                                + abs(w1["w_minus"] - w0["w_minus"]))
    if cell.get("save_rows"):
        np.save(os.path.join(OUT, f"rows_cid{cell['cid']:03d}.npy"), rec_d)
    out["ledger"] = ledger
    out["elapsed"] = time.time() - t0
    return out


def run_spec(cell):
    t0 = time.time()
    import networkx as nx

    L = 8
    g = j2_torus_graph(L)
    order = list(range(2 * L * L))
    adj = nx.to_numpy_array(g, nodelist=order)
    w, v = R.eigh_adjacency(adj)
    an = R.spectrum_anatomy(w)
    devs = []
    for t in (0.5, 2.0, 5.0):
        ks = R.kernel_matrix_spectral(w, v, t)
        for u in (0, 40, 127):
            col = R.kernel_column(g, order, u, np.array([0.0, t]))[1]
            devs.append(float(np.abs(col - ks[:, u]).max()))
    return {"cid": cell["cid"], "kind": "spec", "anatomy": an,
            "max_dev": float(max(devs)), "elapsed": time.time() - t0}


def run_quot(cell):
    t0 = time.time()
    L = cell["L"]
    ctx = _j2_ctx(L)
    g, order, c3, h, eu, ev = (ctx["g"], ctx["order"], ctx["c3"], ctx["h"],
                               ctx["eu"], ctx["ev"])
    u, cells = R.quotient_lift_matrix(order, c3)
    cpos = {c: k for k, c in enumerate(cells)}
    hq = R.quotient_hamiltonian(cells, L)
    from scipy import sparse as _sp

    phi0 = np.zeros(len(cells), dtype=np.complex128)
    phi0[cpos[SRC_CELL]] = 1.0
    full = R.evolve(R.lift_state(phi0, u), h, DT, N_STEPS)["psi"]
    quot = R.evolve(phi0, _sp.csr_matrix(hq), DT, N_STEPS)["psi"]
    inter = float(np.abs(full - quot @ u.T).max())
    # bond lift at sample times
    idx = {v: i for i, v in enumerate(order)}
    devs = []
    for k in (40, 160, 320):
        psi = full[k]
        bm = R.bond_B(psi, eu, ev)
        worst = 0.0
        for e in range(0, len(eu), 37):
            a, b = order[int(eu[e])], order[int(ev[e])]
            ca, cb = (c3[a][0], c3[a][1]), (c3[b][0], c3[b][1])
            bq = float((np.conj(quot[k, cpos[ca]]) * quot[k, cpos[cb]]).real)
            worst = max(worst, abs(bm[e] - bq / 2.0))
        devs.append(worst)
    return {"cid": cell["cid"], "kind": "quot", "intertwining": inter,
            "bond_lift_max": float(max(devs)), "elapsed": time.time() - t0}


def run_green(cell):
    t0 = time.time()
    if cell["sub"] == "path":
        from bh_graph.driven import path_graph

        n = 61
        g = path_graph(n)
        order = list(range(n))
        pin, w = [30], -2.5
    else:
        L = 8
        g = j2_torus_graph(L)
        order = list(range(2 * L * L))
        pin = [(7 * L + 7) * 2]
        w = -8.5
    h = R.hamiltonian(g, order)
    s = np.array([1.0])
    pred = steady_predict(h.tocsc(), pin, s, w)
    got = R.green_static_approx(h, pin, s, w, dt=0.05,
                                T=cell.get("T", 300.0),
                                eta=cell.get("eta", 0.02))["phi"]
    dev = float(np.linalg.norm(got - pred) / np.linalg.norm(pred))
    return {"cid": cell["cid"], "kind": "green", "sub": cell["sub"],
            "omega": w, "dev": dev, "elapsed": time.time() - t0}


def run_switch(cell):
    t0 = time.time()
    if cell["sub"] == "path":
        from bh_graph.driven import path_graph

        n = 61
        g = path_graph(n)
        order = list(range(n))
        src, pin, w = 30, [30], -2.5
        n_steps, dt = 480, 0.05
        shells = {v: abs(v - src) for v in order}
    else:
        L = L_J2
        g = j2_torus_graph(L)
        order = list(range(2 * L * L))
        c3 = j2_torus_coords(L)
        src = (SRC_CELL[0] * L + SRC_CELL[1]) * 2
        pin, w = [src], -8.5
        n_steps, dt = N_STEPS, DT
        idx = {v: i for i, v in enumerate(order)}
        qs = coarse_shells(c3, order, SRC_CELL, L, 25)
        shells = {}
        for s, ii in qs.items():
            for i in ii:
                shells[order[i]] = s
    h = R.hamiltonian(g, order)
    phi0 = np.real_if_close(steady_predict(h.tocsc(), pin, np.array([1.0]), w))
    phi0 = np.asarray(phi0, dtype=np.complex128)
    rows = R.switch_evolution(phi0, h, dt, n_steps)["psi"]
    ts = np.arange(n_steps + 1) * dt
    dev = R.switch_deviation(rows, phi0, w, dt)
    idx = {v: i for i, v in enumerate(order)}
    by_shell = {}
    for v, s in shells.items():
        by_shell.setdefault(s, []).append(idx[v])
    tr = {s: np.abs(dev[:, ii]).max(axis=1) for s, ii in by_shell.items() if s <= 16}
    peak = max(float(t.max()) for s, t in tr.items() if s >= 1)
    theta = max(1e-3 * peak, 1e-12)
    arrivals = {s: R.arrival_time(t, ts, theta) for s, t in tr.items()}
    use = [s for s in FIT_SHELLS if arrivals.get(s) is not None]
    fit = R.front_velocity({s: arrivals[s] for s in use}, use) if len(use) >= 3 else None
    # superposition sub-check on 8 columns
    cols = [R.kernel_column(g, order, order[(i * 131) % len(order)],
                            np.arange(0, 41) * dt) for i in range(8)]
    rng = np.random.default_rng(cell["cid"])
    coeffs = rng.standard_normal(8) + 1j * rng.standard_normal(8)
    direct = R.evolve(sum(c * (R.point_source(len(order), order[(i * 131) % len(order)], 1.0))
                          for i, c in enumerate(coeffs)), h, dt, 40)["psi"]
    sup_dev = float(np.abs(R.superpose_columns(cols, coeffs) - direct).max())
    return {"cid": cell["cid"], "kind": "switch", "sub": cell["sub"],
            "theta": theta, "arrivals": arrivals,
            "fit": {"v": fit["v"], "r2": fit["r2"]} if fit else None,
            "sup_dev": sup_dev, "elapsed": time.time() - t0}


def run_linear(cell):
    t0 = time.time()
    L = L_J2
    ctx = _j2_ctx(L)
    g, order, c3, h, eu, ev = (ctx["g"], ctx["order"], ctx["c3"], ctx["h"],
                               ctx["eu"], ctx["ev"])
    idx = {v: i for i, v in enumerate(order)}
    u1 = (SRC_CELL[0] * L + SRC_CELL[1]) * 2
    u2 = ((SRC_CELL[0] + 5) % L * L + SRC_CELL[1]) * 2
    eps = 1e-3
    e1 = R.point_source(len(order), idx[u1], eps)
    e2 = R.point_source(len(order), idx[u2], eps * np.exp(1j * math.pi / 3))
    bg = R.background_state(cell["bg"], g, order, c3, L)
    has_bg = float(np.linalg.norm(bg)) > 0
    bg_rows = R.evolve(bg, h, DT, N_STEPS)["psi"] if has_bg else None
    full1 = R.evolve(bg + e1, h, DT, N_STEPS)["psi"] if has_bg else R.evolve(e1, h, DT, N_STEPS)["psi"]
    full2 = R.evolve(bg + e2, h, DT, N_STEPS)["psi"] if has_bg else R.evolve(e2, h, DT, N_STEPS)["psi"]
    full12 = R.evolve(bg + e1 + e2, h, DT, N_STEPS)["psi"] if has_bg else R.evolve(e1 + e2, h, DT, N_STEPS)["psi"]
    rec1 = full1 - bg_rows if has_bg else full1
    rec2 = full2 - bg_rows if has_bg else full2
    rec12 = full12 - bg_rows if has_bg else full12
    fdev = max(R.field_linearity_dev(rec1[k], rec2[k], rec12[k])
               for k in range(0, N_STEPS + 1, 40))
    xdev = []
    for k in (N_STEPS // 4, N_STEPS // 2, N_STEPS):
        p0 = bg_rows[k] if has_bg else np.zeros(len(order))
        full = R.delta_observables(p0, rec12[k], eu, ev)
        r1 = R.delta_observables(p0, rec1[k], eu, ev)
        r2 = R.delta_observables(p0, rec2[k], eu, ev)
        x = R.quadratic_cross_terms(rec1[k], rec2[k], eu, ev)
        xdev.append(max(float(np.abs(full["d_rho"] - r1["d_rho"] - r2["d_rho"] - x["x_rho"]).max()),
                        float(np.abs(full["d_B"] - r1["d_B"] - r2["d_B"] - x["x_B"]).max()),
                        float(np.abs(full["d_J"] - r1["d_J"] - r2["d_J"] - x["x_J"]).max())))
    return {"cid": cell["cid"], "kind": "linear", "bg": cell["bg"],
            "field_dev": float(fdev), "cross_max": float(max(xdev)),
            "elapsed": time.time() - t0}


def run_cov(cell):
    t0 = time.time()
    from bh_graph.potential import reflectx_perm, rot90_perm, translate_perm

    L = L_J2
    ctx = _j2_ctx(L)
    g, order, c3 = ctx["g"], ctx["order"], ctx["c3"]
    idx = {v: i for i, v in enumerate(order)}
    sheet = {(x * L + y) * 2 + b: (x * L + y) * 2 + (1 - b)
             for x in range(L) for y in range(L) for b in (0, 1)}
    perms = {"translate": translate_perm(L, 5, 9), "rot90": rot90_perm(L),
             "reflectx": reflectx_perm(L), "sheet": sheet}
    ts = np.arange(0, 161) * DT
    u = (SRC_CELL[0] * L + SRC_CELL[1]) * 2
    cu = R.kernel_column(g, order, u, ts)
    out = {"cid": cell["cid"], "kind": "cov", "devs": {}}
    for name, p in perms.items():
        cg = R.kernel_column(g, order, p[u], ts)
        worst = 0.0
        for v in (u, (SRC_CELL[0] + 3) * L * 2 + SRC_CELL[1] * 2,
                  ((SRC_CELL[0] + 11) % L) * L * 2 + ((SRC_CELL[1] + 7) % L) * 2):
            worst = max(worst, R.trace_covariance_dev(cu, cg, order, v, p))
        out["devs"][name] = float(worst)
    out["elapsed"] = time.time() - t0
    return out


def run_ballistic_xcheck(cell):
    from bh_graph.ballistic import evolve_fixed

    t0 = time.time()
    L = 6
    ctx = _j2_ctx(L)
    h = ctx["h"]
    rng = np.random.default_rng(11)
    psi0 = rng.standard_normal(2 * L * L) + 1j * rng.standard_normal(2 * L * L)
    psi0 /= np.linalg.norm(psi0)
    a = R.evolve(psi0, h, 0.05, 100)["psi"]
    b = evolve_fixed(psi0, h, 0.05, 100)["psi"]
    return {"cid": cell["cid"], "kind": "ballistic", "max_dev": float(np.abs(a - b).max()),
            "elapsed": time.time() - t0}


def build_cells():
    cells = []
    cid = 0

    def add(d):
        nonlocal cid
        d["cid"] = cid
        d.setdefault("L", L_J2)
        d.setdefault("eps", 1.0)
        d.setdefault("bg", "BG0")
        d.setdefault("support", "node@src")
        cells.append(d)
        cid += 1

    add({"kind": "spec", "task": "spec", "support": "spectral"})
    add({"kind": "ballistic", "task": "ballistic", "support": "random-state"})
    for src, eps in (("point-R", 1.0), ("point-I", 1.0)):
        add({"kind": "headline", "task": "response", "src": src, "eps": eps,
             "save_rows": True, "support": "node@src"})
    for bg in ("BG+", "BGpi", "BG-", "BGM"):
        for src in ("point-R", "point-I"):
            add({"kind": "battery", "task": "response", "src": src, "eps": 1e-3,
                 "bg": bg, "support": "node@src"})
    for eps in (1e-4, 1e-3, 1e-2, 1e-1, 1.0):
        add({"kind": "ladder-eps", "task": "response", "src": "point-R", "eps": eps,
             "support": "node@src"})
    for bg, eps in (("BG+", 1e-3),):
        for a in (1e-3, 1e-1, 1.0, 1e1, 1e2):
            add({"kind": "ladder-amp", "task": "response", "src": "point-R",
                 "eps": eps, "bg": bg, "amp": a, "support": "node@src"})
    for bg in ("BG+",):
        for frac in (1e-3, 1e-2, 1e-1):
            add({"kind": "ladder-frac", "task": "response", "src": "point-R",
                 "eps": frac / math.sqrt(2 * L_J2 * L_J2), "bg": bg,
                 "support": "node@src"})
    for src in ("phase", "amplitude"):
        add({"kind": "kick", "task": "response", "src": src, "eps": 1e-2,
             "bg": "BG+", "support": "node@src"})
    for src in ("edge", "cell", "ball1", "patch"):
        add({"kind": "region", "task": "response", "src": src, "eps": 1.0,
             "support": f"{src}@src"})
    add({"kind": "region", "task": "response", "src": "cell", "eps": 1e-3,
         "bg": "BG+", "support": "cell@src"})
    for src in ("sym", "anti", "sheet0", "sheet1"):
        add({"kind": "sector", "task": "response", "src": src, "eps": 1.0,
             "support": f"{src}@srccell"})
    add({"kind": "dipole", "task": "response", "src": "dipole", "eps": 1.0,
         "support": "dipole@src"})
    add({"kind": "quot", "task": "quot", "support": "quotcell@src"})
    add({"kind": "green", "task": "green", "sub": "path", "support": "pin@mid",
         "T": 300.0, "eta": 0.02})
    add({"kind": "green", "task": "green", "sub": "j2", "support": "pin@src",
         "T": 200.0, "eta": 0.03})
    add({"kind": "switch", "task": "switch", "sub": "path", "support": "pin@mid"})
    add({"kind": "switch", "task": "switch", "sub": "j2", "support": "pin@src"})
    for bg in ("BG0", "BG+"):
        add({"kind": "linear", "task": "linear", "bg": bg, "eps": 1e-3,
             "support": "2nodes"})
    add({"kind": "cov", "task": "cov", "support": "node@src"})
    return cells


def run_cell(cell):
    task = cell["task"]
    if task == "response":
        return _run_response_cell(cell)
    if task == "spec":
        return run_spec(cell)
    if task == "quot":
        return run_quot(cell)
    if task == "green":
        return run_green(cell)
    if task == "switch":
        return run_switch(cell)
    if task == "linear":
        return run_linear(cell)
    if task == "cov":
        return run_cov(cell)
    if task == "ballistic":
        return run_ballistic_xcheck(cell)
    raise ValueError(task)


def main():
    workers = int(os.environ.get("RESPONSE0_WORKERS", str(os.cpu_count() or 8)))
    cells = build_cells()
    print(f"RESPONSE-0: {len(cells)} cells, {workers} workers, L={L_J2} T={T_END} dt={DT}",
          flush=True)
    t0 = time.time()
    with Pool(workers) as pool:
        results = pool.map(run_cell, cells)
    results.sort(key=lambda r: r["cid"])
    with open(os.path.join(OUT, "response0_results.json"), "w") as f:
        json.dump({"meta": {"L": L_J2, "T": T_END, "dt": DT, "workers": workers,
                             "elapsed": time.time() - t0},
                   "results": results}, f)
    # gate table
    by_kind = {}
    for r in results:
        by_kind.setdefault(r["kind"], []).append(r)
    print("=== gate table (prereg bars in RESPONSE0-PREREG) ===")
    for r in by_kind.get("spec", []):
        print(f"G1 spec: max_dev={r['max_dev']:.2e} (bar 1e-8) an={r['anatomy']}")
    for r in by_kind.get("ballistic", []):
        print(f"G2 ballistic: max_dev={r['max_dev']:.2e} (bar 1e-9)")
    for r in by_kind.get("headline", []) + by_kind.get("battery", []) \
            + by_kind.get("dipole", []) + by_kind.get("sector", []):
        f = (r["q_psi"]["fit"] or {})
        print(f"H/B cid={r['cid']} {r['bg']}/{r['src']}: decomp={r['decomp_max']:.1e} "
              f"v={f.get('v')} r2={f.get('r2')} drift={r['sector_drift']:.1e} "
              f"chi={r['chi_spot']}")
    for kind, xkey, expect in (("ladder-eps", "eps", {"dpsi": 1.0, "drho": 2.0,
                                                      "dB": 2.0, "dJ": 2.0}),
                               ("ladder-amp", "amp", {"dpsi": 0.0, "drho": 1.0,
                                                      "dB": 1.0, "dJ": 1.0})):
        rows = sorted(by_kind.get(kind, []), key=lambda r: r[xkey])
        if not rows:
            continue
        for obs, key in (("dpsi", "q_psi"), ("drho", "q_rho"), ("dB", "q_B"),
                         ("dJ", "q_J")):
            xs = np.array([r[xkey] for r in rows], dtype=float)
            ys = np.array([r[key]["remote_peak"] for r in rows], dtype=float)
            m = ys > 0
            if kind == "ladder-amp" and obs != "dpsi":
                m = m & (xs >= 1.0)  # linear-dominated subset; low-a crossover filed
            slope, _ = np.polyfit(np.log(xs[m]), np.log(ys[m]), 1)
            print(f"G5 {kind}/{obs}: slope={slope:.3f} (expect {expect[obs]})")
    for r in by_kind.get("ladder-frac", []):
        print(f"ladder-frac eps={r['eps']:.2e}: rho_peak={r['q_rho']['remote_peak']:.2e} "
              f"B_peak={r['q_B']['remote_peak']:.2e}")
    for r in by_kind.get("quot", []):
        print(f"G9 quot: inter={r['intertwining']:.2e} (bar 1e-8) "
              f"bondlift={r['bond_lift_max']:.2e} (bar 1e-12)")
    for r in by_kind.get("green", []):
        print(f"G10 green/{r['sub']}: dev={r['dev']:.3f} (bar 0.1)")
    for r in by_kind.get("switch", []):
        print(f"G11 switch/{r['sub']}: fit={r['fit']} sup={r['sup_dev']:.1e}")
    for r in by_kind.get("linear", []):
        print(f"G12 linear/{r['bg']}: field={r['field_dev']:.1e} cross={r['cross_max']:.1e}")
    for r in by_kind.get("cov", []):
        print(f"G6 cov: {r['devs']} (bar 1e-9)")
    print(f"elapsed {time.time() - t0:.1f}s -> {OUT}/response0_results.json")


if __name__ == "__main__":
    main()
