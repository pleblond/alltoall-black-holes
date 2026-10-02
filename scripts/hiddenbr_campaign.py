"""HIDDEN-BR ledger battery (preregistered grid, frozen analysis).

Grid (HIDDEN-BR-PREREG, docs/DEFERRED.md; J2 L28 headline, T=20/dt=0.1):
  pair x10: B:sign x {packet,uniform,twocell} (3), B:phase:packet x {p2,p4}
    (2), B:shape:packet x {dipole,disk} (2), B:amp:packet {05raw,20raw} (2),
    B:amp:packet:05q (1, non-qualifying control).
  conjugate x2 (L6+L28), equalledger x2, purehidden x4, vminus x1,
  phasesweep x2, ampsweep x2, shape x1, locality x3, passwave x2,
  zero x1, sym x1, vac x1, firewall x1, ledgercheck x1, infomap x1.
Total 35 cells. No fitting, no steering, no selection. Virtual ledger
only: no graph mutation anywhere in this runner.
"""
import json
import os
import time
from multiprocessing import Pool

import numpy as np
from scipy import sparse

from bh_graph import field0, hidden, hiddenbr, malus, obs0, quot
from bh_graph.accounting import dE_contract_formula
from bh_graph.ballistic import evolve_fixed, hamiltonian, node_order
from bh_graph.contraction import contraction_census
from bh_graph.driven import edge_arrays
from bh_graph.formation import j2_torus_coords, j2_torus_graph

OUT = os.environ.get("HIDDENBR_PART", "/tmp/hiddenbr_parts")
os.makedirs(OUT, exist_ok=True)

L = int(os.environ.get("HIDDENBR_L", "28"))
T_END = float(os.environ.get("HIDDENBR_T", "20.0"))
DT = float(os.environ.get("HIDDENBR_DT", "0.1"))
N_STEPS = int(round(T_END / DT))
PC = (7, 14)  # pair prep center (HIDDEN-0 window)
RC = (14, 14)  # hidden-region center (passing wave)
CC = (14, 14)  # census center
R0PKT = (7.0, 14.0)
KPKT = (0.3, 0.0)

_WC = {}


def _j2(LL):
    if LL in _WC:
        return _WC[LL]
    g = j2_torus_graph(LL)
    order = node_order(g)
    c3 = j2_torus_coords(LL)
    h = hamiltonian(g, order=order)
    pr = malus.sheet_projectors(order, c3)
    eu, ev = edge_arrays(g, order)
    sub = field0.build_substrate("j2", LL)
    J = {"g": g, "order": order, "c3": c3, "h": h, "pr": pr,
         "eu": eu, "ev": ev, "sub": sub}
    _WC[LL] = J
    return J


def _eig(J):
    if "eig" not in J:
        Ew, Vw, _ = obs0.hamiltonian_system(J["g"], J["order"])
        wl, Vl, _ = obs0.lsym_system(J["g"], J["order"])
        J["eig"] = (Ew, Vw, wl, Vl)
    return J["eig"]


def _js(o):
    if isinstance(o, (np.floating, float)):
        return float(o)
    if isinstance(o, (np.integer, int)):
        return int(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.bool_, bool)):
        return bool(o)
    if isinstance(o, complex):
        return [float(o.real), float(o.imag)]
    raise TypeError(repr(type(o)))


def build_cells():
    """Preregistered cell list (deterministic, frozen order)."""
    cells = []
    cid = 0

    def add(kind, note, **kw):
        nonlocal cid
        cells.append({"cid": cid, "kind": kind, "note": note, **kw})
        cid += 1

    for tag in ("B:sign:packet", "B:sign:uniform", "B:sign:twocell",
                "B:phase:packet:p2", "B:phase:packet:p4",
                "B:shape:packet:dipole", "B:shape:packet:disk",
                "B:amp:packet:05raw", "B:amp:packet:20raw",
                "B:amp:packet:05q"):
        add("pair", tag, tag=tag)
    add("conjugate", "X:l6", LL=6)
    add("conjugate", "X:l28", LL=28)
    add("equalledger", "J:uniform", bg="uniform")
    add("equalledger", "J:packet0", bg="packet0")
    for hp in ("delta", "disk", "checker", "complex"):
        add("purehidden", f"K:{hp}", hp=hp)
    add("vminus", "L:vminus")
    add("phasesweep", "M:packet:delta", bg="packet", hp="delta")
    add("phasesweep", "M:uniform:disk", bg="uniform", hp="disk")
    add("ampsweep", "N:packet:delta", bg="packet", hp="delta")
    add("ampsweep", "N:uniform:disk", bg="uniform", hp="disk")
    add("shape", "O:shapes")
    add("locality", "P:graded", variant="graded")
    add("locality", "P:far", variant="far")
    add("locality", "P:support", variant="support")
    add("passwave", "R:delta", hp="delta")
    add("passwave", "R:disk", hp="disk")
    add("zero", "T:packet:delta")
    add("sym", "U:sym")
    add("vac", "V:vac")
    add("firewall", "W:headon")
    add("ledgercheck", "C4:direct")
    add("infomap", "X:r2mixed")
    return cells


def _complex_pat(J, pc):
    cells = hidden.disk_cells(pc, 1, L)
    d = hidden.hidden_disk(J["order"], J["c3"], cells)
    ph = {(x, y): (x + 2 * y) * np.pi / 4.0 for (x, y) in cells}
    return hidden.hidden_phased(d, J["order"], J["c3"], ph)


def run_pair(cell):
    t0 = time.time()
    J = _j2(L)
    order, c3, h, pr, eu, ev = (J["order"], J["c3"], J["h"], J["pr"],
                                J["eu"], J["ev"])
    bat = {b["tag"]: b for b in hiddenbr.pair_battery(J, J["sub"], PC)}
    spec = bat[cell["tag"]]
    p = spec["pair"]
    psi_A, psi_B = p["psi_A"], p["psi_B"]
    # C1/C2.
    pm = hiddenbr.is_pair_pplus_ok(psi_A, psi_B, pr)
    pplus_max = float(np.abs(np.asarray(pr["P_sym"], dtype=float)
                             @ (np.asarray(psi_A) - np.asarray(psi_B))).max())
    erep = hiddenbr.pair_energy_report(psi_A, psi_B, p["psi_plus"],
                                       p["minus_A"], p["minus_B"], h)
    eok = hiddenbr.is_pair_energy_ok(erep)
    # C0 local.
    nb = hidden.prep_neighborhood(order, c3, PC, L)
    ne = hidden.neighborhood_edges(eu, ev, nb["nodes"])
    d = hidden.local_distance(psi_A, psi_B, eu, ev, nb["nodes"], ne["mask"])
    # C0 remote (wave + diffusion + POT).
    Ew, Vw, wl, Vl = _eig(J)
    shells = quot.coarse_shells(c3, order, PC, L, 10)
    ts = np.arange(0.0, hidden.T_WAVE + hidden.DT_WAVE / 2, hidden.DT_WAVE)
    rw = hidden.remote_tv_wave(psi_A, psi_B, Ew, Vw, shells, ts)
    rd = hidden.remote_tv_diff(np.abs(psi_A) ** 2, np.abs(psi_B) ** 2,
                               wl, Vl, shells, ts)
    pos = {v: i for i, v in enumerate(order)}
    node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
    pins = (node_of[(PC[0], PC[1], 0)], node_of[(PC[0], PC[1], 1)])
    pf = hidden.pot_pair_fields(sparse.csc_matrix(h),
                                (pos[pins[0]], pos[pins[1]]), psi_A, psi_B)
    remote = sorted({i for r in range(2, 11) for i in shells[r]})
    sodd = hidden.prob_diff_sodd_ok(psi_A, psi_B,
                                    malus.sheet_swap_matrix(order, c3))
    # HBR-0D/0G/0H/0I.
    oA = hiddenbr.bond_fields(psi_A, eu, ev)
    oB = hiddenbr.bond_fields(psi_B, eu, ev)
    db = hiddenbr.delta_b_census(oA["B"], oB["B"])
    pc_ = hiddenbr.perturbation_census(oA["B"], oB["B"])
    lc = hiddenbr.ledger_census(J["g"], order, psi_A, psi_B, eu, ev)
    hsup = set(hiddenbr.hidden_node_support(p["minus_A"]).tolist())
    hsup |= set(hiddenbr.hidden_node_support(p["minus_B"]).tolist())
    touch = 0
    for k in db["support"]:
        if int(eu[int(k)]) in hsup or int(ev[int(k)]) in hsup:
            touch += 1
    flips = []
    for k in lc["flip_idx"]:
        k = int(k)
        a, b = order[int(eu[k])], order[int(ev[k])]
        flips.append({"ca": list(c3[a]), "cb": list(c3[b]),
                      "LA": float(lc["L_A"][k]), "LB": float(lc["L_B"][k])})
    zt = hiddenbr.zero_ledger_table(psi_A, psi_B, J["g"], order, eu, ev,
                                    db["support"])
    return {
        "qmatch": spec["qmatch"], "scale_c": p.get("scale_c"),
        "pmatch": bool(pm), "pplus_max": pplus_max,
        "E_A": erep["E_A"], "E_B": erep["E_B"], "dE": erep["dE"],
        "EA": erep["A"], "EB": erep["B"], "E_ok": bool(eok),
        "d_rho": d["d_rho"], "d_B": d["d_B"], "d_J": d["d_J"], "D": d["D"],
        "wave_Dmax": {str(k): float(v) for k, v in rw["Dmax"].items()},
        "diff_Dmax": {str(k): float(v) for k, v in rd["Dmax"].items()},
        "pot_remote": float(np.abs(pf["dphi"][remote]).max()),
        "pot_local": float(np.abs(pf["dphi"]).max()),
        "pot_support": bool(quot.anti_support_ok(pf["dphi"], order, J["g"],
                                                 list(pins))),
        "sodd": bool(sodd),
        "db_n": db["n_changed"], "db_max": db["max_abs"],
        "db_mean": db["mean_abs"], "db_npos": db["n_pos"],
        "db_nneg": db["n_neg"], "db_touch": int(touch),
        "db_support": [int(k) for k in db["support"][:512]],
        "pt_sign": pc_["n_sign_differ"], "pt_frac": pc_["frac_sign_differ"],
        "pt_maxdmag": pc_["max_dmag"], "pt_meandmag": pc_["mean_dmag"],
        "lc_n": lc["n_nonzero"], "lc_frac": lc["frac_nonzero"],
        "lc_max": lc["max_abs"], "lc_mean": lc["mean_abs"],
        "lc_flips": lc["n_flips"], "lc_fliprec": flips,
        "lc_cancel": lc["n_cancel"],
        "zt_frac": zt["frac_zero_free"], "zt_gminA": zt["global_min_A"],
        "zt_gminB": zt["global_min_B"],
        "wall_s": time.time() - t0}


def run_conjugate(cell):
    t0 = time.time()
    LL = cell["LL"]
    J = _j2(LL)
    order, c3, h, eu, ev = J["order"], J["c3"], J["h"], J["eu"], J["ev"]
    pc = (1, 3) if LL == 6 else PC
    r0 = (1.5, 3.0) if LL == 6 else R0PKT
    sig = 1.5 if LL == 6 else 4.0
    pkt = hidden.symmetric_packet(J["sub"], r0, KPKT, sig)
    pm = hidden.hidden_delta(order, c3, pc)
    shapes = hidden.vac_shapes(order, c3)
    states = [pkt + pm, pkt - pm, shapes["VMINUS"]]
    E = eu.shape[0]
    idx = list(range(E)) if LL == 6 else list(range(0, E, max(E // 24, 1)))
    worst = 0.0
    for psi in states:
        for k in idx:
            r = hiddenbr.conjugacy_fd(psi, h, int(eu[k]), int(ev[k]))
            worst = max(worst, r["err"])
    return {"n_edges": len(idx), "n_states": len(states),
            "worst": float(worst), "wall_s": time.time() - t0}


def run_equalledger(cell):
    t0 = time.time()
    J = _j2(L)
    order, c3, eu, ev = J["order"], J["c3"], J["eu"], J["ev"]
    if cell["bg"] == "uniform":
        bg = hidden.symmetric_uniform(len(order))
    else:
        bg = hidden.symmetric_packet(J["sub"], (7.0, 14.0), (0.0, 0.0), 4.0)
        bg = np.real(bg).astype(np.complex128)  # k=0 prep is real-valued
    pm = hidden.hidden_phased(hidden.hidden_delta(order, c3, PC),
                              order, c3, {PC: 1.0})
    psi_A, psi_B = bg + pm, bg + np.conj(pm)
    oA = hiddenbr.bond_fields(psi_A, eu, ev)
    oB = hiddenbr.bond_fields(psi_B, eu, ev)
    lc = hiddenbr.ledger_census(J["g"], order, psi_A, psi_B, eu, ev)
    nb = hidden.prep_neighborhood(order, c3, PC, L)
    ne = hidden.neighborhood_edges(eu, ev, nb["nodes"])
    d = hidden.local_distance(psi_A, psi_B, eu, ev, nb["nodes"], ne["mask"])
    return {"bg_real": bool(np.all(np.isreal(bg))),
            "pmatch": bool(hiddenbr.is_pair_pplus_ok(psi_A, psi_B, J["pr"])),
            "max_dB": float(np.abs(oA["B"] - oB["B"]).max()),
            "max_drho": float(np.abs(oA["rho"] - oB["rho"]).max()),
            "max_dJ": float(np.abs(oA["J"] - oB["J"]).max()),
            "lc_n": lc["n_nonzero"], "lc_max": lc["max_abs"],
            "D": d["D"], "wall_s": time.time() - t0}


def run_purehidden(cell):
    t0 = time.time()
    J = _j2(L)
    order, c3, h, eu, ev = J["order"], J["c3"], J["h"], J["eu"], J["ev"]
    hp = cell["hp"]
    if hp == "delta":
        pm = hidden.hidden_delta(order, c3, PC)
    elif hp == "disk":
        pm = hidden.hidden_disk(order, c3, hidden.disk_cells(PC, 1, L))
    elif hp == "checker":
        pm = hidden.hidden_checker(order, c3, hidden.disk_cells(PC, 1, L))
    else:
        pm = _complex_pat(J, PC)
    o = hiddenbr.bond_fields(pm, eu, ev)
    Lv = hiddenbr.ledger_array(J["g"], pm, order, eu, ev)
    return {"E": float(field0.energy_of(pm, h)),
            "B_max": float(np.abs(o["B"]).max()),
            "B_meanabs": float(np.abs(o["B"]).mean()),
            "J_max": float(np.abs(o["J"]).max()),
            "rho_max": float(np.abs(o["rho"]).max()),
            "L_min": float(Lv.min()), "L_max": float(Lv.max()),
            "L_mean": float(Lv.mean()),
            "L_nnz": int(np.sum(np.abs(Lv) > hiddenbr.LEDGER_NONZERO)),
            "L_fracpos": float(np.mean(Lv > hiddenbr.LEDGER_NONZERO)),
            "L_fracneg": float(np.mean(Lv < -hiddenbr.LEDGER_NONZERO)),
            "wall_s": time.time() - t0}


def run_vminus(cell):
    t0 = time.time()
    J = _j2(L)
    order, c3, h, eu, ev = J["order"], J["c3"], J["h"], J["eu"], J["ev"]
    tab = hiddenbr.vac_ledger_table(order, c3, J["g"], h, eu, ev)
    shapes = hidden.vac_shapes(order, c3)
    vm = shapes["VMINUS"]
    # Translation covariance: VMINUS is translation-invariant exactly.
    LL = L
    perm = {}
    node_of = {(x, y, b): v for v, (x, y, b) in c3.items()}
    for v, (x, y, b) in c3.items():
        perm[v] = node_of[((x + 3) % LL, (y + 5) % LL, b)]
    from bh_graph.potential import pushforward
    vm_t = pushforward(np.asarray(vm), perm, list(order))
    o = hiddenbr.bond_fields(vm, eu, ev)
    Lv = hiddenbr.ledger_array(J["g"], vm, order, eu, ev)
    # VMINUS-based sign pair (HBR-0A battery member).
    pkt = hidden.symmetric_packet(J["sub"], R0PKT, KPKT, 4.0)
    pair = hidden.matched_pair(pkt, vm, "sign")
    oA = hiddenbr.bond_fields(pair["psi_A"], eu, ev)
    oB = hiddenbr.bond_fields(pair["psi_B"], eu, ev)
    db = hiddenbr.delta_b_census(oA["B"], oB["B"])
    lc = hiddenbr.ledger_census(J["g"], order, pair["psi_A"],
                                pair["psi_B"], eu, ev)
    erep = hiddenbr.pair_energy_report(pair["psi_A"], pair["psi_B"],
                                       pair["psi_plus"], pair["minus_A"],
                                       pair["minus_B"], h)
    return {"tab": tab["VMINUS"],
            "trans_maxdiff": float(np.abs(vm_t - vm).max()),
            "J_max": float(np.abs(o["J"]).max()),
            "J_meanabs": float(np.abs(o["J"]).mean()),
            "L_nnz": int(np.sum(np.abs(Lv) > hiddenbr.LEDGER_NONZERO)),
            "pair_pmatch": bool(hiddenbr.is_pair_pplus_ok(pair["psi_A"],
                                                          pair["psi_B"],
                                                          J["pr"])),
            "pair_Eok": bool(hiddenbr.is_pair_energy_ok(erep)),
            "pair_db_n": db["n_changed"], "pair_db_max": db["max_abs"],
            "pair_lc_n": lc["n_nonzero"], "pair_lc_max": lc["max_abs"],
            "pair_flips": lc["n_flips"],
            "wall_s": time.time() - t0}


def run_phasesweep(cell):
    t0 = time.time()
    J = _j2(L)
    order, c3, h, eu, ev = J["order"], J["c3"], J["h"], J["eu"], J["ev"]
    bg = (hidden.symmetric_packet(J["sub"], R0PKT, KPKT, 4.0)
          if cell["bg"] == "packet" else hidden.symmetric_uniform(len(order)))
    ma = (hidden.hidden_delta(order, c3, PC) if cell["hp"] == "delta"
          else hidden.hidden_disk(order, c3, hidden.disk_cells(PC, 1, L)))
    sw = hiddenbr.phase_sweep_ledger(bg, ma, J["g"], order, eu, ev, h)
    Bvar = (sw["B"].max(axis=0) - sw["B"].min(axis=0))
    Lvar = (sw["L"].max(axis=0) - sw["L"].min(axis=0))
    return {"res_B": sw["res_B"], "res_L": sw["res_L"],
            "E_range": sw["E_range"], "E0": float(sw["E"][0]),
            "B_varmax": float(Bvar.max()), "L_varmax": float(Lvar.max()),
            "B_nvar": int(np.sum(Bvar > hiddenbr.DBAR_FP)),
            "L_nvar": int(np.sum(Lvar > hiddenbr.LEDGER_NONZERO)),
            "wall_s": time.time() - t0}


def run_ampsweep(cell):
    t0 = time.time()
    J = _j2(L)
    order, c3, h, eu, ev = J["order"], J["c3"], J["h"], J["eu"], J["ev"]
    bg = (hidden.symmetric_packet(J["sub"], R0PKT, KPKT, 4.0)
          if cell["bg"] == "packet" else hidden.symmetric_uniform(len(order)))
    ma = (hidden.hidden_delta(order, c3, PC) if cell["hp"] == "delta"
          else hidden.hidden_disk(order, c3, hidden.disk_cells(PC, 1, L)))
    sw = hiddenbr.amp_sweep_ledger(bg, ma, J["g"], order, eu, ev, h)
    Es = sw["E"]
    return {"res_B": sw["res_B"], "res_L": sw["res_L"],
            "d_lin": sw["d_lin"], "d_quad": sw["d_quad"],
            "E_range": float(Es.max() - Es.min()),
            "E_list": [float(v) for v in Es],
            "clin_max": float(np.abs(sw["coef_L"][1]).max()),
            "cquad_max": float(np.abs(sw["coef_L"][2]).max()),
            "wall_s": time.time() - t0}


def run_shape(cell):
    t0 = time.time()
    J = _j2(L)
    order, c3, eu, ev = J["order"], J["c3"], J["eu"], J["ev"]
    bg = hidden.symmetric_packet(J["sub"], R0PKT, KPKT, 4.0)
    pats = {
        "dipole": hidden.hidden_dipole(order, c3, PC, (PC[0] + 1, PC[1])),
        "disk": hidden.hidden_disk(order, c3, hidden.disk_cells(PC, 1, L)),
        "checker": hidden.hidden_checker(order, c3,
                                         hidden.disk_cells(PC, 1, L)),
    }
    norms = {k: float(np.linalg.norm(v)) for k, v in pats.items()}
    states = {k: bg + v for k, v in pats.items()}
    out = {"norms": norms, "wall_s": 0.0}
    for a, b in (("dipole", "disk"), ("dipole", "checker"),
                 ("disk", "checker")):
        oA = hiddenbr.bond_fields(states[a], eu, ev)
        oB = hiddenbr.bond_fields(states[b], eu, ev)
        db = hiddenbr.delta_b_census(oA["B"], oB["B"])
        lc = hiddenbr.ledger_census(J["g"], order, states[a], states[b],
                                    eu, ev)
        out[f"{a}_vs_{b}"] = {"db_max": db["max_abs"],
                              "db_n": db["n_changed"],
                              "lc_max": lc["max_abs"],
                              "lc_n": lc["n_nonzero"],
                              "flips": lc["n_flips"]}
    out["wall_s"] = time.time() - t0
    return out


def _test_edge(J):
    node_of = {(x, y, b): v for v, (x, y, b) in J["c3"].items()}
    v0 = node_of[(PC[0], PC[1], 0)]
    return (v0, next(iter(J["g"].neighbors(v0))))


def run_locality(cell):
    t0 = time.time()
    J = _j2(L)
    order, c3, h, eu, ev = J["order"], J["c3"], J["h"], J["eu"], J["ev"]
    bg = hidden.symmetric_packet(J["sub"], R0PKT, KPKT, 4.0)
    a, b = _test_edge(J)
    var = cell["variant"]
    if var == "graded":
        rows = []
        for dd in list(range(0, 7)) + ["anti"]:
            center = ((PC[0] + dd) % L, PC[1]) if dd != "anti" else (21, 0)
            disk = hidden.hidden_disk(order, c3,
                                      hidden.disk_cells(center, 1, L))
            sup = hiddenbr.hidden_node_support(disk)
            dist = hiddenbr.edge_support_distance(J["g"], a, b, sup, order)
            la = dE_contract_formula(J["g"], bg + disk, order, a, b)
            lb = dE_contract_formula(J["g"], bg - disk, order, a, b)
            ia = order.index(a)
            ib = order.index(b)
            ba = float(np.real(np.conj((bg + disk)[ia]) * (bg + disk)[ib]))
            bb = float(np.real(np.conj((bg - disk)[ia]) * (bg - disk)[ib]))
            rows.append({"d": dd, "center": list(center), "dist": dist,
                         "dh_edge": float(la - lb),
                         "dB_edge": float(abs(ba - bb))})
        return {"edge": [list(c3[a]), list(c3[b])], "rows": rows,
                "wall_s": time.time() - t0}
    if var == "far":
        disk = hidden.hidden_disk(order, c3, hidden.disk_cells((21, 0), 1, L))
        oA = hiddenbr.bond_fields(bg + disk, eu, ev)
        oB = hiddenbr.bond_fields(bg - disk, eu, ev)
        db = hiddenbr.delta_b_census(oA["B"], oB["B"])
        lc = hiddenbr.ledger_census(J["g"], order, bg + disk, bg - disk,
                                    eu, ev)
        ia = order.index(a)
        ib = order.index(b)
        k = int(np.nonzero(((eu == ia) & (ev == ib))
                            | ((eu == ib) & (ev == ia)))[0][0])
        return {"edge_k": k,
                "dB_edge": float(abs(oA["B"][k] - oB["B"][k])),
                "dh_edge": float(lc["d_hidden"][k]),
                "db_max_full": db["max_abs"], "db_n_full": db["n_changed"],
                "lc_max_full": lc["max_abs"], "lc_n_full": lc["n_nonzero"],
                "wall_s": time.time() - t0}
    # support variant: deltas on exact-support cells (filed) vs outside (gated).
    sup = hiddenbr.ledger_support_nodes(J["g"], order, a, b)
    sup_cells = sorted({(c3[v][0], c3[v][1]) for v in sup})
    ex, ey = (c3[a][0] + c3[b][0]) / 2.0, (c3[a][1] + c3[b][1]) / 2.0
    outside = []
    for x in range(L):
        for y in range(L):
            dx = min(abs(x - ex), L - abs(x - ex))
            dy = min(abs(y - ey), L - abs(y - ey))
            if (dx ** 2 + dy ** 2) ** 0.5 >= 4 and (x, y) not in sup_cells:
                outside.append((x, y))
    outside = outside[:8]
    on_rows, off_rows = [], []
    for (x, y) in sup_cells:
        d = hidden.hidden_delta(order, c3, (x, y))
        la = dE_contract_formula(J["g"], bg + d, order, a, b)
        lb = dE_contract_formula(J["g"], bg - d, order, a, b)
        on_rows.append({"cell": [x, y], "dh_edge": float(la - lb)})
    for (x, y) in outside:
        d = hidden.hidden_delta(order, c3, (x, y))
        la = dE_contract_formula(J["g"], bg + d, order, a, b)
        lb = dE_contract_formula(J["g"], bg - d, order, a, b)
        off_rows.append({"cell": [x, y], "dh_edge": float(la - lb)})
    return {"edge": [list(c3[a]), list(c3[b])],
            "n_support": len(sup), "on": on_rows, "off": off_rows,
            "wall_s": time.time() - t0}


def run_passwave(cell):
    t0 = time.time()
    J = _j2(L)
    order, c3, h, eu, ev = J["order"], J["c3"], J["h"], J["eu"], J["ev"]
    sub = J["sub"]
    pkt = hidden.symmetric_packet(sub, R0PKT, KPKT, 4.0)
    mh = (hidden.hidden_delta(order, c3, RC) if cell["hp"] == "delta"
          else hidden.hidden_disk(order, c3, hidden.disk_cells(RC, 1, L)))
    v = field0.group_speed("j2", KPKT, 1.0)
    win = hidden.pass_windows(hidden.predict_crossing(R0PKT, RC, v))
    wit = {}
    for tag, sgn in (("A", 1.0), ("B", -1.0)):
        rec = field0.evolve_triplet(pkt, sgn * mh, h, DT, N_STEPS)
        w = field0.witness_components(
            float(rec["eps"].max()), rec["psi1"][win["k_pre"]],
            rec["psi1"][win["k_post"]], rec["psi2"][win["k_pre"]],
            rec["psi2"][win["k_post"]], h, sub)
        wit[tag] = {k: (float(vv) if not isinstance(vv, bool) else vv)
                    for k, vv in w.items()}
    rA = evolve_fixed(pkt + mh, h, DT, N_STEPS)["psi"]
    rB = evolve_fixed(pkt - mh, h, DT, N_STEPS)["psi"]
    sub_e = hiddenbr.ledger_subset(eu, ev, order, c3, RC, L)
    LA = hiddenbr.ledger_trace(rA, J["g"], order, eu, ev, sub_e["near"])
    LB = hiddenbr.ledger_trace(rB, J["g"], order, eu, ev, sub_e["near"])
    FA = hiddenbr.ledger_trace(rA, J["g"], order, eu, ev, sub_e["far"])
    FB = hiddenbr.ledger_trace(rB, J["g"], order, eu, ev, sub_e["far"])
    dN = np.abs(LA - LB).max(axis=1)
    dF = np.abs(FA - FB).max(axis=1)
    kp, ko, kq = win["k_pre"], win["k_over"], win["k_post"]
    return {"t_cross": win["t_cross"], "wA": wit["A"], "wB": wit["B"],
            "near_pre": float(dN[kp]), "near_over": float(dN[ko]),
            "near_post": float(dN[kq]),
            "near_max_t": float(dN.max()),
            "far_max_t": float(dF.max()),
            "mod_over_pre": float(dN[ko] / dN[kp]) if dN[kp] > 0 else -1.0,
            "post_pre": float(dN[kq] / dN[kp]) if dN[kp] > 0 else -1.0,
            "n_near": int(sub_e["near"].size),
            "n_far": int(sub_e["far"].size),
            "wall_s": time.time() - t0}


def run_zero(cell):
    t0 = time.time()
    J = _j2(L)
    order, c3, eu, ev = J["order"], J["c3"], J["eu"], J["ev"]
    bg = hidden.symmetric_packet(J["sub"], R0PKT, KPKT, 4.0)
    pair = hidden.matched_pair(bg, hidden.hidden_delta(order, c3, PC), "sign")
    oA = hiddenbr.bond_fields(pair["psi_A"], eu, ev)
    oB = hiddenbr.bond_fields(pair["psi_B"], eu, ev)
    db = hiddenbr.delta_b_census(oA["B"], oB["B"])
    lc = hiddenbr.ledger_census(J["g"], order, pair["psi_A"],
                                pair["psi_B"], eu, ev)
    nz = np.nonzero(np.abs(lc["d_hidden"]) > hiddenbr.LEDGER_NONZERO)[0]
    zt = hiddenbr.zero_ledger_table(pair["psi_A"], pair["psi_B"], J["g"],
                                    order, eu, ev, nz)
    return {"n_nz": int(nz.size), "frac_zero_free": zt["frac_zero_free"],
            "min_nz": float(zt["min_amp"].min()) if nz.size else -1.0,
            "gminA": zt["global_min_A"], "gminB": zt["global_min_B"],
            "wall_s": time.time() - t0}


def run_sym(cell):
    t0 = time.time()
    J = _j2(L)
    order, c3, eu, ev = J["order"], J["c3"], J["eu"], J["ev"]
    psi = (hidden.symmetric_packet(J["sub"], R0PKT, KPKT, 4.0)
           + hidden.hidden_delta(order, c3, PC))
    u1 = hiddenbr.u1_invariance(psi, J["g"], order, eu, ev)
    rl = hiddenbr.relabel_covariance(psi, J["g"], order, eu, ev)
    sh = hiddenbr.sheet_covariance(psi, J["g"], order, c3, eu, ev)
    return {"u1_dB": u1["max_dB"], "u1_dL": u1["max_dL"],
            "rl_dB": rl["max_dB"], "rl_dL": rl["max_dL"],
            "rl_auto": rl["is_auto"],
            "sh_dB": sh["max_dB"], "sh_dL": sh["max_dL"],
            "wall_s": time.time() - t0}


def run_vac(cell):
    t0 = time.time()
    J = _j2(L)
    tab = hiddenbr.vac_ledger_table(J["order"], J["c3"], J["g"], J["h"],
                                    J["eu"], J["ev"])
    tab["wall_s"] = time.time() - t0
    return tab


def run_firewall(cell):
    t0 = time.time()
    J = _j2(L)
    rep = hiddenbr.headon_witness(J["sub"], J["h"])
    rep["wall_s"] = time.time() - t0
    return rep


def run_ledgercheck(cell):
    t0 = time.time()
    J = _j2(L)
    order, eu, ev = J["order"], J["eu"], J["ev"]
    bg = hidden.symmetric_packet(J["sub"], R0PKT, KPKT, 4.0)
    pm = hidden.hidden_delta(order, J["c3"], PC)
    vm = hidden.vac_shapes(order, J["c3"])["VMINUS"]
    states = [bg + pm, bg - pm, vm]
    E = eu.shape[0]
    idx = list(range(0, E, max(E // 20, 1)))
    worst = 0.0
    for psi in states:
        for k in idx:
            a, b = order[int(eu[k])], order[int(ev[k])]
            f = dE_contract_formula(J["g"], psi, order, a, b)
            dd = contraction_census(J["g"], psi, order, a, b, "sum")["dEpsi"]
            worst = max(worst, abs(f - dd))
    return {"n_edges": len(idx), "worst": float(worst),
            "wall_s": time.time() - t0}


def run_infomap(cell):
    t0 = time.time()
    J = _j2(L)
    order, c3, eu, ev = J["order"], J["c3"], J["eu"], J["ev"]
    cells_R = hidden.disk_cells(CC, 2, L)
    nb = hidden.prep_neighborhood(order, c3, CC, L, r_prep=3)
    ne = hidden.neighborhood_edges(eu, ev, nb["nodes"])
    patch = np.nonzero(np.asarray(ne["mask"], dtype=bool))[0]
    bg = hidden.symmetric_uniform(len(order))
    states = hidden.census_mixed_alphabet(order, c3, cells_R, bg)
    tags = [s["tag"] for s in states]
    conj = hiddenbr.census_conj_pairs(tags)
    mat = np.array([hiddenbr.rg_signature(s["psi"], J["g"], order, eu, ev,
                                          patch) for s in states])
    pw = hiddenbr.pairwise_min_excluding(mat, conj)
    cmax = 0.0
    for pr in conj:
        i, k = sorted(pr)
        cmax = max(cmax, float(np.abs(mat[i] - mat[k]).max()))
    return {"n_R": len(cells_R), "n_states": len(states),
            "n_patch": int(patch.size),
            "min_D": pw["min_D"], "argmin": list(pw["argmin"]),
            "n_below": pw["n_below"], "n_pairs": pw["n_pairs"],
            "n_conj": len(conj), "conj_max_D": float(cmax),
            "wall_s": time.time() - t0}


def run_cell(cell):
    fn = {"pair": run_pair, "conjugate": run_conjugate,
          "equalledger": run_equalledger, "purehidden": run_purehidden,
          "vminus": run_vminus, "phasesweep": run_phasesweep,
          "ampsweep": run_ampsweep, "shape": run_shape,
          "locality": run_locality, "passwave": run_passwave,
          "zero": run_zero, "sym": run_sym, "vac": run_vac,
          "firewall": run_firewall, "ledgercheck": run_ledgercheck,
          "infomap": run_infomap}[cell["kind"]]
    rec = fn(cell)
    rec["cid"] = cell["cid"]
    rec["kind"] = cell["kind"]
    rec["note"] = cell["note"]
    return json.loads(json.dumps(rec, default=_js))


def main():
    cells = build_cells()
    print(f"HIDDEN-BR cells: {len(cells)} (T={T_END}, dt={DT}, L={L})",
          flush=True)
    ckpt = os.path.join(OUT, "hiddenbr_cells.jsonl")
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
    nw = int(os.environ.get("HIDDENBR_WORKERS", "32"))
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
    with open(os.path.join(OUT, "hiddenbr_cells.json"), "w") as f:
        json.dump({"cells": allc, "T": T_END, "dt": DT, "L": L}, f)
    print(f"done {len(allc)} cells in {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
