"""HIDDEN-0 hidden-sector battery (preregistered grid, frozen analysis).

Grid (HIDDEN0-PREREG, docs/DEFERRED.md; J2 L28 headline, T=20/dt=0.1):
  A anatomy: l6 exact + l28 regression (2 cells).
  B pairs: sign x {packet,uniform,twocell} (3), phase x {pi/2,pi} (2),
    shape x {dipole,disk} (2), amp {05raw,20raw,05q} (3) = 10 cells.
  E hidden-only: {delta,disk,checker,complex} (4 cells).
  F remote: {sharp,packet:delta,packet:disk,uniform:delta} wave+diff (4)
    + pot (1) = 5 cells.
  G persistence: {sign,phase,shape,amp} (4 cells).
  H passing wave: {delta,disk} (2 cells). K extraction: {delta,disk} (2).
  L census: mixed/pure x R{1,2,3} (6 cells). N exchange (1).
  O sweep: {packet:delta,uniform:disk} (2; 0P reads these cells).
  Q bond-full (1). R ledger (1). S vac-classes (1). T obs-input (1).
  U staggered-eps0.1 (1).
Total 43 cells. No fitting, no steering, no selection.
"""
import json
import os
import time
from multiprocessing import Pool

import numpy as np
from scipy import sparse

from bh_graph import field0, hidden, malus, obs0, quot
from bh_graph.ballistic import evolve_fixed, hamiltonian, node_order
from bh_graph.driven import edge_arrays
from bh_graph.formation import j2_torus_coords, j2_torus_graph

OUT = os.environ.get("HIDDEN0_PART", "/tmp/hidden0_parts")
os.makedirs(OUT, exist_ok=True)

L = int(os.environ.get("HIDDEN0_L", "28"))
T_END = float(os.environ.get("HIDDEN0_T", "20.0"))
DT = float(os.environ.get("HIDDEN0_DT", "0.1"))
N_STEPS = int(round(T_END / DT))
PC = (7, 14)  # pair/packet prep center (POT-0 window)
RC = (14, 14)  # hidden-region center (passing wave)
CC = (14, 14)  # census center
R0PKT = (7.0, 14.0)
KPKT = (0.3, 0.0)


def _j2(LL):
    g = j2_torus_graph(LL)
    order = node_order(g)
    c3 = j2_torus_coords(LL)
    h = hamiltonian(g, order=order)
    pr = malus.sheet_projectors(order, c3)
    eu, ev = edge_arrays(g, order)
    coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
    return {"g": g, "order": order, "c3": c3, "h": h, "pr": pr,
            "eu": eu, "ev": ev, "coords": coords}


def build_cells():
    """Preregistered cell list (deterministic, frozen order)."""
    cells = []
    cid = 0

    def add(kind, note, **kw):
        nonlocal cid
        cells.append({"cid": cid, "kind": kind, "note": note, **kw})
        cid += 1

    add("anatomy", "A:l6", LL=6)
    add("anatomy", "A:l28", LL=28)
    for bg in ("packet", "uniform", "twocell"):
        add("pair", f"B:sign:{bg}", bg=bg, mode="sign", arg=None)
    for tag, phi in (("p2", np.pi / 2.0), ("p4", np.pi)):
        add("pair", f"B:phase:packet:{tag}", bg="packet", mode="phase",
            arg=float(phi))
    for sh in ("dipole", "disk"):
        add("pair", f"B:shape:packet:{sh}", bg="packet", mode="shape", arg=sh)
    add("pair", "B:amp:packet:05raw", bg="packet", mode="amplitude", arg=0.5,
        qmatch=False)
    add("pair", "B:amp:packet:20raw", bg="packet", mode="amplitude", arg=2.0,
        qmatch=False)
    add("pair", "B:amp:packet:05q", bg="packet", mode="amplitude", arg=0.5,
        qmatch=True)
    for hp in ("delta", "disk", "checker", "complex"):
        add("hiddenonly", f"E:{hp}", hp=hp)
    for tag in ("sharp", "packet:delta", "packet:disk", "uniform:delta"):
        add("remote", f"F:{tag}", tag=tag)
    add("remote_pot", "F:pot")
    for tag in ("sign", "phase", "shape", "amp"):
        add("persist", f"G:{tag}", tag=tag)
    for hp in ("delta", "disk"):
        add("passwave", f"H:{hp}", hp=hp)
    for hp in ("delta", "disk"):
        add("extract", f"K:{hp}", hp=hp)
    for R in hidden.CENSUS_RADII:
        add("census", f"L:mixed:R{R}", variant="mixed", R=R)
    for R in hidden.CENSUS_RADII:
        add("census", f"L:pure:R{R}", variant="pure", R=R)
    add("exchange", "N:sheet")
    add("sweep", "O:packet:delta", bg="packet", hp="delta")
    add("sweep", "O:uniform:disk", bg="uniform", hp="disk")
    add("bondfull", "Q:full")
    add("ledger", "R:packet:delta")
    add("vac", "S:classes")
    add("obsinput", "T:packet:delta")
    add("staggered", "U:eps01")
    return cells


def _backgrounds(J):
    order, c3 = J["order"], J["c3"]
    sub = field0.build_substrate("j2", L)
    out = {
        "packet": hidden.symmetric_packet(sub, R0PKT, KPKT, 4.0),
        "uniform": hidden.symmetric_uniform(len(order)),
        "twocell": (hidden.symmetric_delta(order, c3, PC)
                    + hidden.symmetric_delta(order, c3, (PC[0] + 1, PC[1]))
                    ) / np.sqrt(2.0),
    }
    return out


def _hidden_pat(J, hp):
    order, c3 = J["order"], J["c3"]
    if hp == "delta":
        return hidden.hidden_delta(order, c3, PC)
    if hp == "disk":
        return hidden.hidden_disk(order, c3, hidden.disk_cells(PC, 1, L))
    if hp == "checker":
        return hidden.hidden_checker(order, c3, hidden.disk_cells(PC, 1, L))
    if hp == "complex":
        cells = hidden.disk_cells(PC, 1, L)
        d = hidden.hidden_disk(order, c3, cells)
        ph = {(x, y): (x + 2 * y) * np.pi / 4.0 for (x, y) in cells}
        return hidden.hidden_phased(d, order, c3, ph)
    raise ValueError(hp)


def run_anatomy(cell):
    t0 = time.time()
    J = _j2(cell["LL"])
    h, pr, order, c3 = J["h"], J["pr"], J["order"], J["c3"]
    s = malus.sheet_swap_matrix(order, c3)
    u, cells = malus.symmetric_embedding(order, c3)
    hsq = malus.square_hamiltonian(cells, (cell["LL"], cell["LL"]))
    pm = hidden.hidden_delta(order, c3, (0, 0))
    rng = np.random.default_rng(7)
    psi = rng.standard_normal(len(order)) + 1.0j * rng.standard_normal(len(order))
    psi = psi / np.linalg.norm(psi)
    w = np.linalg.eigvalsh(h.toarray())
    return {"comm": quot.commutator_norm(h, s),
            "dead": quot.anti_dead_norm(h, pr["P_anti"]),
            "inter": quot.intertwining_norm(h, u, hsq),
            "frozen": quot.frozen_err(h, pm, 0.1, 30)["max_err"],
            "decomp": quot.decomposition_err(h, pr, psi, 0.1, 10),
            "n_zero": int(np.sum(np.abs(w) < 1e-9)),
            "nodal_pred": int(len(order) // 2 + malus.nodal_count_square(cell["LL"])),
            "wall_s": time.time() - t0}


def run_pair(cell):
    t0 = time.time()
    J = _j2(L)
    order, c3, h, pr, eu, ev = (J["order"], J["c3"], J["h"], J["pr"],
                                J["eu"], J["ev"])
    bg = _backgrounds(J)[cell["bg"]]
    ma = hidden.hidden_delta(order, c3, PC)
    mode, arg = cell["mode"], cell["arg"]
    if mode == "shape":
        arg = (hidden.hidden_dipole(order, c3, PC, (PC[0] + 1, PC[1]))
               if arg == "dipole"
               else hidden.hidden_disk(order, c3, hidden.disk_cells(PC, 1, L)))
    pair = hidden.matched_pair(bg, ma, mode, arg)
    if cell.get("qmatch"):
        qm = hidden.qmatch_pair(pair)
        psi_A, psi_B = qm["psi_A"], qm["psi_B"]
        scale_c = qm["scale_c"]
    else:
        psi_A, psi_B = pair["psi_A"], pair["psi_B"]
        scale_c = None
    nb = hidden.prep_neighborhood(order, c3, PC, L)
    ne = hidden.neighborhood_edges(eu, ev, nb["nodes"])
    d = hidden.local_distance(psi_A, psi_B, eu, ev, nb["nodes"], ne["mask"])
    # NOTE: energy anatomy always on the (bg, minus_A) construction parts.
    an = hidden.energy_sector_anatomy(bg, ma, h)
    s = malus.sheet_swap_matrix(order, c3)
    return {"pmatch": hidden.is_pplus_match_ok(psi_A, psi_B, pr),
            "Q_A": hidden.total_Q(psi_A), "Q_B": hidden.total_Q(psi_B),
            "dQ": float(abs(hidden.total_Q(psi_A) - hidden.total_Q(psi_B))),
            "scale_c": scale_c, "d_rho": d["d_rho"], "d_B": d["d_B"],
            "d_J": d["d_J"], "D": d["D"],
            "E_plus": an["E_plus"], "E_minus": an["E_minus"], "E_x": an["E_x"],
            "E_total": an["E_total"],
            "E_free": hidden.is_energy_hidden_free_ok(an),
            "sodd": hidden.prob_diff_sodd_ok(psi_A, psi_B, s),
            "wall_s": time.time() - t0}


def run_hiddenonly(cell):
    t0 = time.time()
    J = _j2(L)
    h, eu, ev = J["h"], J["eu"], J["ev"]
    pm = _hidden_pat(J, cell["hp"])
    o = hidden.em_observables(pm, eu, ev)
    return {"frozen": quot.frozen_err(h, pm, 0.1, 50)["max_err"],
            "rho_max": float(np.abs(o["rho"]).max()),
            "B_max": float(np.abs(o["B"]).max()),
            "J_max": float(np.abs(o["J"]).max()),
            "E": field0.energy_of(pm, h),
            "wall_s": time.time() - t0}


def _sym_ref(J, Ew, Vw, wl, Vl, shells, ts):
    order, c3 = J["order"], J["c3"]
    prep = quot.sector_preparations(order, c3, PC, (PC[0] + 2, PC[1]))
    rw = hidden.remote_tv_wave(prep["sym0"], prep["sym1"], Ew, Vw, shells, ts)
    p0 = np.abs(prep["sym0"]) ** 2
    p1 = np.abs(prep["sym1"]) ** 2
    rd = hidden.remote_tv_diff(p0, p1, wl, Vl, shells, ts)
    return rw, rd


def run_remote(cell):
    t0 = time.time()
    J = _j2(L)
    order, c3 = J["order"], J["c3"]
    Ew, Vw, _ = obs0.hamiltonian_system(J["g"], order)
    wl, Vl, _ = obs0.lsym_system(J["g"], order)
    shells = quot.coarse_shells(c3, order, PC, L, 10)
    ts = np.arange(0.0, hidden.T_WAVE + hidden.DT_WAVE / 2, hidden.DT_WAVE)
    tag = cell["tag"]
    if tag == "sharp":
        prep = quot.sector_preparations(order, c3, PC, (PC[0] + 2, PC[1]))
        psi_A, psi_B = prep["sheet0"], prep["sheet1"]
    else:
        bg = _backgrounds(J)[tag.split(":")[0]]
        hp = tag.split(":")[1]
        ma = (hidden.hidden_delta(order, c3, PC) if hp == "delta"
              else hidden.hidden_disk(order, c3, hidden.disk_cells(PC, 1, L)))
        pair = hidden.matched_pair(bg, ma, "sign")
        psi_A, psi_B = pair["psi_A"], pair["psi_B"]
    rw = hidden.remote_tv_wave(psi_A, psi_B, Ew, Vw, shells, ts)
    pA = np.abs(psi_A) ** 2
    pB = np.abs(psi_B) ** 2
    rd = hidden.remote_tv_diff(pA, pB, wl, Vl, shells, ts)
    rw_ref, rd_ref = _sym_ref(J, Ew, Vw, wl, Vl, shells, ts)
    out = {"wall_s": time.time() - t0}
    for nm, r, rr in (("wave", rw, rw_ref), ("diff", rd, rd_ref)):
        out[f"{nm}_Dmax"] = {str(k): float(v) for k, v in r["Dmax"].items()}
        out[f"{nm}_Cplus"] = {str(k): float(v) for k, v in rr["Dmax"].items()}
        out[f"{nm}_ratio"] = {str(k): (float(r["Dmax"][k] / rr["Dmax"][k])
                                        if rr["Dmax"][k] > 0 else float("inf"))
                              for k in r["Dmax"]}
    return out


def run_remote_pot(cell):
    t0 = time.time()
    J = _j2(L)
    order, c3 = J["order"], J["c3"]
    bg = _backgrounds(J)["packet"]
    ma = hidden.hidden_delta(order, c3, PC)
    pair = hidden.matched_pair(bg, ma, "sign")
    pos = {v: i for i, v in enumerate(order)}
    node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
    pins = (node_of[(PC[0], PC[1], 0)], node_of[(PC[0], PC[1], 1)])
    ia, ib = pos[pins[0]], pos[pins[1]]
    pf = hidden.pot_pair_fields(sparse.csc_matrix(J["h"]), (ia, ib),
                                pair["psi_A"], pair["psi_B"])
    shells = quot.coarse_shells(c3, order, PC, L, 10)
    remote = sorted({i for r in range(2, 11) for i in shells[r]})
    return {"remote_max": float(np.abs(pf["dphi"][remote]).max()),
            "local_max": float(np.abs(pf["dphi"]).max()),
            "pin_norm": pf["pin_norm"],
            "support_ok": quot.anti_support_ok(pf["dphi"], order, J["g"],
                                               list(pins)),
            "wall_s": time.time() - t0}


def run_persist(cell):
    t0 = time.time()
    J = _j2(L)
    order, c3, h, eu, ev = J["order"], J["c3"], J["h"], J["eu"], J["ev"]
    bg = _backgrounds(J)["packet"]
    ma = hidden.hidden_delta(order, c3, PC)
    tag = cell["tag"]
    if tag == "sign":
        pair = hidden.matched_pair(bg, ma, "sign")
    elif tag == "phase":
        pair = hidden.matched_pair(bg, ma, "phase", np.pi / 2.0)
    elif tag == "shape":
        mb = hidden.hidden_dipole(order, c3, PC, (PC[0] + 1, PC[1]))
        pair = hidden.matched_pair(bg, ma, "shape", mb)
    else:
        pair = hidden.matched_pair(bg, ma, "amplitude", 0.5)
    rA = evolve_fixed(pair["psi_A"], h, DT, N_STEPS)["psi"]
    rB = evolve_fixed(pair["psi_B"], h, DT, N_STEPS)["psi"]
    rP = evolve_fixed(pair["psi_plus"], h, DT, N_STEPS)["psi"]
    nb = hidden.prep_neighborhood(order, c3, PC, L)
    ne = hidden.neighborhood_edges(eu, ev, nb["nodes"])
    samp = sorted(set(list(range(0, N_STEPS + 1, 5)) + [N_STEPS]))
    tr = hidden.local_distance_trace(rA[samp], rB[samp], eu, ev,
                                     nb["nodes"], ne["mask"])
    # cross-term identity worst over sampled rows (sign/phase exact form).
    worst = 0.0
    for k in samp:
        D_rho = np.abs(rA[k]) ** 2 - np.abs(rB[k]) ** 2
        if tag in ("sign", "phase"):
            mb = pair["minus_B"]
            pred = field0.rho_cross(rP[k], ma) - field0.rho_cross(rP[k], mb)
            pred = pred + (np.abs(ma) ** 2 - np.abs(mb) ** 2)
            worst = max(worst, float(np.abs(D_rho - pred).max()))
    D = tr["D"]
    # hidden-only residual reference (shape/amp persistent leg).
    dHid = hidden.local_distance(pair["minus_A"], pair["minus_B"], eu, ev,
                                 nb["nodes"], ne["mask"])
    return {"D_max": float(D.max()), "D_post": float(D[-1]),
            "D_t0": float(D[0]),
            "decay_ratio": float(D[-1] / D.max()) if D.max() > 0 else 0.0,
            "cross_worst": float(worst),
            "resid_ref": float(dHid["D"]),
            "wall_s": time.time() - t0}


def run_passwave(cell):
    t0 = time.time()
    J = _j2(L)
    order, c3, h, pr, eu, ev = (J["order"], J["c3"], J["h"], J["pr"],
                                J["eu"], J["ev"])
    sub = field0.build_substrate("j2", L)
    pkt = hidden.symmetric_packet(sub, R0PKT, KPKT, 4.0)
    mcells = hidden.disk_cells(RC, 1, L)
    mh = (hidden.hidden_delta(order, c3, RC) if cell["hp"] == "delta"
          else hidden.hidden_disk(order, c3, mcells))
    v = field0.group_speed("j2", KPKT, 1.0)
    tcross = hidden.predict_crossing(R0PKT, RC, v)
    win = hidden.pass_windows(tcross)
    nb = hidden.prep_neighborhood(order, c3, RC, L)
    ne = hidden.neighborhood_edges(eu, ev, nb["nodes"])
    out = {"t_cross": tcross, "wall_s": 0.0}
    for tag, sgn in (("A", 1.0), ("B", -1.0)):
        rec = field0.evolve_triplet(pkt, sgn * mh, h, DT, N_STEPS)
        p1pre, p1post = rec["psi1"][win["k_pre"]], rec["psi1"][win["k_post"]]
        p2pre, p2post = rec["psi2"][win["k_pre"]], rec["psi2"][win["k_post"]]
        w = field0.witness_components(float(rec["eps"].max()), p1pre, p1post,
                                      p2pre, p2post, h, sub)
        # sector preservation: P_+ joint == isolated packet rows (fp).
        samp = list(range(0, N_STEPS + 1, 5)) + [N_STEPS]
        sp_worst = 0.0
        for k in samp:
            pp_k = np.asarray(pr["P_sym"], dtype=float) @ rec["psi12"][k]
            sp_worst = max(sp_worst, float(np.abs(pp_k - rec["psi1"][k]).max()))
        # write leg: P_- joint const + w_anti const.
        w0 = hidden.sector_weights(rec["psi12"][0], pr)["w_anti"]
        _, m0 = hidden.sector_split(rec["psi12"][0], pr)
        wr_w = 0.0
        wr_m = 0.0
        for k in samp:
            wr_w = max(wr_w, abs(hidden.sector_weights(rec["psi12"][k], pr)["w_anti"] - w0))
            _, mt = hidden.sector_split(rec["psi12"][k], pr)
            wr_m = max(wr_m, float(np.abs(mt - m0).max()))
        mpre = field0.momentum_peak(p1pre, sub)
        mpost = field0.momentum_peak(p1post, sub)
        cpre = field0.coherence_of(p1pre, sub)
        cpost = field0.coherence_of(p1post, sub)
        out[tag] = {"eps": float(rec["eps"].max()), "w_I": w["I"],
                    "w_dP1": w["dP1"], "w_dP2": w["dP2"], "w_clin": w["clin"],
                    "w_dE": w["dE"], "w_eps": w["eps"],
                    "sector_worst": float(sp_worst),
                    "write_w": float(wr_w), "write_m": float(wr_m),
                    "k_pre": list(mpre["k"]), "k_post": list(mpost["k"]),
                    "C_pre": float(mpre["C"]), "C_post": float(mpost["C"])}
    # read leg: A/B joint states at overlap (both triplets' joint rows).
    recA = field0.evolve_triplet(pkt, mh, h, DT, N_STEPS)["psi12"]
    recB = field0.evolve_triplet(pkt, -mh, h, DT, N_STEPS)["psi12"]
    d_over = hidden.local_distance(recA[win["k_over"]], recB[win["k_over"]],
                                   eu, ev, nb["nodes"], ne["mask"])
    out["read"] = {"d_rho": d_over["d_rho"], "d_B": d_over["d_B"],
                   "d_J": d_over["d_J"], "D": d_over["D"]}
    out["wall_s"] = time.time() - t0
    return out


def run_extract(cell):
    t0 = time.time()
    J = _j2(L)
    order, c3, h, eu, ev = J["order"], J["c3"], J["h"], J["eu"], J["ev"]
    sub = field0.build_substrate("j2", L)
    pkt = hidden.symmetric_packet(sub, R0PKT, KPKT, 4.0)
    mh = (hidden.hidden_delta(order, c3, RC) if cell["hp"] == "delta"
          else hidden.hidden_disk(order, c3, hidden.disk_cells(RC, 1, L)))
    v = field0.group_speed("j2", KPKT, 1.0)
    win = hidden.pass_windows(hidden.predict_crossing(R0PKT, RC, v))
    recA = field0.evolve_triplet(pkt, mh, h, DT, N_STEPS)["psi12"]
    recB = field0.evolve_triplet(pkt, -mh, h, DT, N_STEPS)["psi12"]
    # local detector: R-neighborhood at overlap.
    nb = hidden.prep_neighborhood(order, c3, RC, L)
    ne = hidden.neighborhood_edges(eu, ev, nb["nodes"])
    profA = hidden.readout_vector(recA[win["k_over"]], eu, ev, nb["nodes"], ne["mask"])
    profB = hidden.readout_vector(recB[win["k_over"]], eu, ev, nb["nodes"], ne["mask"])
    cA = hidden.classify_readout(profA, profA, profB)
    cB = hidden.classify_readout(profB, profA, profB)
    # remote detector: complement of r<=3 disk at post.
    inner = set(hidden.prep_neighborhood(order, c3, RC, L, r_prep=3)["nodes"].tolist())
    rnodes = np.array(sorted(set(range(len(order))) - inner), dtype=int)
    keep = np.zeros(len(order), dtype=bool)
    keep[rnodes] = True
    rmask = keep[eu] & keep[ev]
    rA = hidden.readout_vector(recA[win["k_post"]], eu, ev, rnodes, rmask)
    rB = hidden.readout_vector(recB[win["k_post"]], eu, ev, rnodes, rmask)
    cAr = hidden.classify_readout(rA, rA, rB)
    return {"local_decA": cA["decision"], "local_gapA": cA["gap"],
            "local_decB": cB["decision"], "local_gapB": cB["gap"],
            "remote_gap": cAr["gap"],
            "remote_maxdiff": float(np.abs(rA - rB).max()),
            "wall_s": time.time() - t0}


def run_census(cell):
    t0 = time.time()
    J = _j2(L)
    order, c3, eu, ev = J["order"], J["c3"], J["eu"], J["ev"]
    cells_R = hidden.disk_cells(CC, cell["R"], L)
    nb = hidden.prep_neighborhood(order, c3, CC, L, r_prep=cell["R"] + 1)
    ne = hidden.neighborhood_edges(eu, ev, nb["nodes"])
    if cell["variant"] == "mixed":
        bg = hidden.symmetric_uniform(len(order))
        states = hidden.census_mixed_alphabet(order, c3, cells_R, bg)
        mat = hidden.readout_matrix(states, eu, ev, nb["nodes"], ne["mask"])
        pw = hidden.pairwise_min_D(mat)
        return {"n_R": len(cells_R), "n_states": pw["n_states"],
                "min_D": pw["min_D"], "argmin": list(pw["argmin"]),
                "n_below": pw["n_below"], "wall_s": time.time() - t0}
    states = hidden.census_pure_alphabet(order, c3, cells_R)
    pos = [s for s in states if s["kind"] == "pos"]
    mat = hidden.readout_matrix(pos, eu, ev, nb["nodes"], ne["mask"])
    pw = hidden.pairwise_min_D(mat)
    quo_max = 0.0
    by_tag = {s["tag"]: s["psi"] for s in states}
    for s in states:
        if s["kind"] == "quo":
            d = hidden.local_distance(s["psi"], by_tag[s["parent"]], eu, ev,
                                      nb["nodes"], ne["mask"])
            quo_max = max(quo_max, d["D"])
    return {"n_R": len(cells_R), "n_states": pw["n_states"],
            "min_D": pw["min_D"], "n_below": pw["n_below"],
            "quo_max": float(quo_max), "wall_s": time.time() - t0}


def run_exchange(cell):
    t0 = time.time()
    J = _j2(L)
    order, c3, eu, ev = J["order"], J["c3"], J["eu"], J["ev"]
    nodes = np.arange(len(order))
    mask = np.ones(len(eu), dtype=bool)
    d = hidden.hidden_delta(order, c3, PC)
    bg = hidden.symmetric_uniform(len(order))
    pure = hidden.local_distance(d, -d, eu, ev, nodes, mask)
    mixed = hidden.local_distance(bg + d, bg - d, eu, ev, nodes, mask)
    s = malus.sheet_swap_matrix(order, c3)
    smap = float(np.abs(s @ (bg + d) - (bg - d)).max())
    return {"pure_D": pure["D"], "mixed_D": mixed["D"],
            "mixed_d_rho": mixed["d_rho"], "mixed_d_B": mixed["d_B"],
            "mixed_d_J": mixed["d_J"], "smap": smap,
            "wall_s": time.time() - t0}


def run_sweep(cell):
    t0 = time.time()
    J = _j2(L)
    order, c3, eu, ev = J["order"], J["c3"], J["eu"], J["ev"]
    bg = (_backgrounds(J)["packet"] if cell["bg"] == "packet"
          else hidden.symmetric_uniform(len(order)))
    ma = (hidden.hidden_delta(order, c3, PC) if cell["hp"] == "delta"
          else hidden.hidden_disk(order, c3, hidden.disk_cells(PC, 1, L)))
    sw = hidden.phase_sweep_readouts(bg, ma, eu, ev)
    res = hidden.phase_fit_maxres(sw)
    r = np.asarray(sw["rho"])
    b = np.asarray(sw["B"])
    jj = np.asarray(sw["J"])
    return {"res_rho": res["res_rho"], "res_B": res["res_B"],
            "res_J": res["res_J"],
            "rho_mod": float((r.max(axis=0) - r.min(axis=0)).max()),
            "B_mod": float((b.max(axis=0) - b.min(axis=0)).max()),
            "J_mod": float((jj.max(axis=0) - jj.min(axis=0)).max()),
            "min_abs": [m["min_abs"] for m in sw["mins"]],
            "nzero": sw["nzero_candidates"], "wall_s": time.time() - t0}


def run_bondfull(cell):
    t0 = time.time()
    J = _j2(L)
    order, c3, eu, ev = J["order"], J["c3"], J["eu"], J["ev"]
    bg = hidden.symmetric_uniform(len(order))
    ma = hidden.hidden_delta(order, c3, PC)
    pair = hidden.matched_pair(bg, ma, "sign")
    oA = hidden.em_observables(pair["psi_A"], eu, ev)
    oB = hidden.em_observables(pair["psi_B"], eu, ev)
    dB = np.abs(oA["B"] - oB["B"])
    dJ = np.abs(oA["J"] - oB["J"])
    return {"dB_max": float(dB.max()), "dJ_max": float(dJ.max()),
            "dB_count": int(np.sum(dB > 1e-6)),
            "dB_mean": float(dB.mean()), "wall_s": time.time() - t0}


def run_ledger(cell):
    t0 = time.time()
    J = _j2(L)
    bg = _backgrounds(J)["packet"]
    ma = hidden.hidden_delta(J["order"], J["c3"], PC)
    pair = hidden.matched_pair(bg, ma, "sign")
    lc = hidden.ledger_contrast(pair["psi_A"], pair["psi_B"], J["g"],
                                J["order"], J["coords"], (L, L), R0PKT, 4.0)
    return {"de": lc["de"], "bond_maxdiff": lc["bond_maxdiff"],
            "e_A": lc["e_A"], "e_B": lc["e_B"],
            "near_A": {k: lc["near_A"][k] for k in ("f_neg", "f_zero", "f_pos")},
            "near_B": {k: lc["near_B"][k] for k in ("f_neg", "f_zero", "f_pos")},
            "far_A": {k: lc["far_A"][k] for k in ("f_neg", "f_zero", "f_pos")},
            "far_B": {k: lc["far_B"][k] for k in ("f_neg", "f_zero", "f_pos")},
            "wall_s": time.time() - t0}


def run_vac(cell):
    t0 = time.time()
    J = _j2(L)
    order, c3, h, pr, eu, ev = (J["order"], J["c3"], J["h"], J["pr"],
                                J["eu"], J["ev"])
    vc = hidden.vac_shapes(order, c3)
    out = {}
    for name, psi in vc.items():
        w = hidden.sector_weights(psi, pr)
        o = hidden.em_observables(psi, eu, ev)
        out[name] = {"w_sym": w["w_sym"], "w_anti": w["w_anti"],
                     "E": field0.energy_of(psi, h),
                     "rho_max": float(np.abs(o["rho"]).max()),
                     "B_max": float(np.abs(o["B"]).max()),
                     "J_max": float(np.abs(o["J"]).max())}
    out["wall_s"] = time.time() - t0
    return out


def run_obsinput(cell):
    t0 = time.time()
    J = _j2(L)
    order, c3 = J["order"], J["c3"]
    bg = _backgrounds(J)["packet"]
    ma = hidden.hidden_delta(order, c3, PC)
    pair = hidden.matched_pair(bg, ma, "sign")
    Ew, Vw, _ = obs0.hamiltonian_system(J["g"], order)
    wl, Vl, _ = obs0.lsym_system(J["g"], order)
    shells = quot.coarse_shells(c3, order, PC, L, 8)
    ts = np.arange(0.0, hidden.T_WAVE + hidden.DT_WAVE / 2, hidden.DT_WAVE)
    tj = np.arange(len(order))
    trA = quot.wave_traces_general(Ew, Vw, pair["psi_A"], tj, ts)
    trB = quot.wave_traces_general(Ew, Vw, pair["psi_B"], tj, ts)
    pA = np.abs(pair["psi_A"]) ** 2
    pB = np.abs(pair["psi_B"]) ** 2
    drA = quot.diff_traces_general(wl, Vl, pA, tj, ts)
    drB = quot.diff_traces_general(wl, Vl, pB, tj, ts)
    pos = {v: i for i, v in enumerate(order)}
    node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
    ia = pos[node_of[(PC[0], PC[1], 0)]]
    ib = pos[node_of[(PC[0], PC[1], 1)]]
    pf = hidden.pot_pair_fields(sparse.csc_matrix(J["h"]), (ia, ib),
                                pair["psi_A"], pair["psi_B"])
    out = {}
    for r in hidden.R_LOAD:
        idx = shells[r]
        out[f"W_r{r}"] = float(np.abs(trA[:, idx] - trB[:, idx]).max())
        out[f"D_r{r}"] = float(np.abs(drA[:, idx] - drB[:, idx]).max())
        out[f"P_r{r}"] = float(np.abs(pf["dphi"][idx]).max())
    nb = hidden.prep_neighborhood(order, c3, PC, L)
    ne = hidden.neighborhood_edges(J["eu"], J["ev"], nb["nodes"])
    d = hidden.local_distance(pair["psi_A"], pair["psi_B"], J["eu"], J["ev"],
                              nb["nodes"], ne["mask"])
    out["D_local"] = d["D"]
    out["wall_s"] = time.time() - t0
    return out


def run_staggered(cell):
    t0 = time.time()
    J = _j2(L)
    order, c3 = J["order"], J["c3"]
    chk = hidden.staggered_checks(order, c3, J["g"])
    Hp = quot.perturbed_hamiltonian(J["g"], order, c3)
    Ep, Vp = np.linalg.eigh(Hp.toarray())
    n_zero = int(np.sum(np.abs(Ep) < 1e-9))
    prep = quot.sector_preparations(order, c3, PC, (PC[0] + 2, PC[1]))
    shells = quot.coarse_shells(c3, order, PC, L, 8)
    ts = np.arange(0.0, hidden.T_WAVE + hidden.DT_WAVE / 2, hidden.DT_WAVE)
    r = hidden.remote_tv_wave(prep["sheet0"], prep["sheet1"], Ep, Vp,
                              shells, ts)
    return {"pvp": chk["pvp_max"], "comm_relerr": chk["comm_relerr"],
            "n_zero_pert": n_zero,
            "Dmax": {str(k): float(v) for k, v in r["Dmax"].items()},
            "wall_s": time.time() - t0}


def run_cell(cell):
    """Execute one HIDDEN-0 cell (frozen analysis, no tuning)."""
    fn = {"anatomy": run_anatomy, "pair": run_pair,
          "hiddenonly": run_hiddenonly, "remote": run_remote,
          "remote_pot": run_remote_pot, "persist": run_persist,
          "passwave": run_passwave, "extract": run_extract,
          "census": run_census, "exchange": run_exchange,
          "sweep": run_sweep, "bondfull": run_bondfull,
          "ledger": run_ledger, "vac": run_vac, "obsinput": run_obsinput,
          "staggered": run_staggered}[cell["kind"]]
    rec = fn(cell)
    rec["cid"] = cell["cid"]
    rec["kind"] = cell["kind"]
    rec["note"] = cell["note"]
    return rec


def main():
    cells = build_cells()
    print(f"HIDDEN-0 cells: {len(cells)} (T={T_END}, dt={DT}, L={L})", flush=True)
    ckpt = os.path.join(OUT, "hidden0_cells.jsonl")
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
    nw = int(os.environ.get("HIDDEN0_WORKERS", "32"))
    t0 = time.time()
    fh = open(ckpt, "a")
    if todo:
        with Pool(nw) as pool:
            for i, r in enumerate(pool.imap_unordered(run_cell, todo)):
                fh.write(json.dumps(r) + "\n")
                fh.flush()
                if (i + 1) % 5 == 0:
                    print(f"  {len(done)+i+1}/{len(cells)} {time.time()-t0:.0f}s "
                          f"{r['note']}", flush=True)
    fh.close()
    allc = []
    with open(ckpt) as f:
        for line in f:
            allc.append(json.loads(line))
    with open(os.path.join(OUT, "hidden0_cells.json"), "w") as f:
        json.dump({"cells": allc, "T": T_END, "dt": DT, "L": L}, f)
    print(f"done {len(allc)} cells in {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
