"""DIM-3-0 STAGE-REVEAL + verdict analyzer (DIM3-PREREG Stages A-J).

RUN ONLY AFTER data/dim3_blind.json + data/dim3_blind.json.sha256 are
COMMITTED. Verifies the blind hash first (STOP on mismatch), then joins
the concealed station maps, rebuilds the hidden references, re-verifies
Stages A/B exactly, and evaluates the frozen verdict ladder:

  DIM3-OPERATIONAL / DIM3-GEOMETRIC / DIM3-NOT3D / DIM3-NATURALITY-DEBT
  (or DIM3-INCOMPLETE on partial coverage).
"""

import argparse
import hashlib
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from bh_graph import dim3, dim3_reveal, obs1, obs1_reveal  # noqa: E402
from bh_graph.dim3 import SWAP_XY  # noqa: E402
import dim3_campaign as DC  # noqa: E402
import run_obs0  # noqa: E402

MAJ = 2  # majority of N_SETS=3 (same rule as OBS-1)

J3_CELLS = (0, 1, 2)
CB_CELLS = (3, 4, 5)
EX_CELLS = (6, 7, 8)
J2_CELL = 9


def _arr(x):
    return np.array([[np.nan if v is None else v for v in row] for row in x],
                    dtype=float)


def _maj(flags):
    return sum(1 for f in flags if f) >= MAJ


def _med(vals):
    v = [x for x in vals if x is not None and np.isfinite(x)]
    return float(np.median(v)) if v else float("nan")


def blind_set_flags(pr):
    """Per-set blind clause flags from the composite (C) observer."""
    C = pr["C"]
    sym = all(pr[ch]["sym"]["pass"] for ch in obs1.PROBES)
    tri = bool(C["triangle"]["pass_loose"])
    complete = bool(C["measured_frac"] >= obs1.COMPOSITE_COMPLETE_BAR)
    dim_ok = bool(C["vol"]["ok"])
    emb = bool(C["dstar_pass"] and C["replicated"]
               and C["measured_frac"] >= obs1.EMBED_COMPLETE_BAR)
    return {"sym": sym, "tri": tri, "complete": complete,
            "metric_ok": bool(sym and tri and complete),
            "dim_ok": dim_ok, "d": C["vol"]["d"], "emb": emb,
            "angle": bool(C["angle"]["pass"]),
            "window": bool(C["euclid"]["window"]),
            "dstar": C["dstar"], "replicated": bool(C["replicated"]),
            "dstar_pass": bool(C["dstar_pass"])}


def reveal_set(cell_rec, tag, nodes, g, L):
    """Hidden-join scoring of one (cell, set) composite observer (3D)."""
    C = cell_rec["probes"]["C"]
    n = len(nodes)
    D = _arr(C["D"])
    X = _arr(C["coords"]) if C["coords"] is not None else None
    fam = tag.split("-")[0]
    out = {}
    if fam in ("j3", "cb"):
        coords = dim3_reveal.hidden_quotient_coords3(tag, L)
        Hq = dim3_reveal.hidden_quotient_matrix3(coords, nodes, L)
        Hg = obs1_reveal.hidden_graph_matrix(g, nodes)
        A = np.zeros((n, n), dtype=bool)
        for a, b in C["edges"]:
            A[a, b] = A[b, a] = True
        out["align"] = dim3_reveal_topology_align(X, coords, nodes)
        out["local3"] = dim3_reveal.local_chart_report3(D, coords, nodes, L,
                                                        d=3)
        out["local2"] = dim3_reveal.local_chart_report3(D, coords, nodes, L,
                                                        d=2)
        out["locality"] = obs1_reveal.locality_report(A, Hq)
        sheets = dim3_reveal.hidden_sheets3(tag, L)
        out["sheet"] = obs1_reveal.sheet_report(
            D, [sheets[v] for v in nodes]) if sheets is not None \
            else {"contrast": float("nan"), "pass": False}
        out["topo"] = dim3_reveal.topology_report3(C["wrap"]["pairs"], coords,
                                                   nodes, L, Hq)
        out["match"] = obs1_reveal.geometry_match(D, Hq, Hg)
        q = out["match"].get("quot")
        m = out["match"].get("micro")
        out["match"]["factor"] = float(m / q) \
            if q and np.isfinite(q) and np.isfinite(m) and q > 0 \
            else float("nan")
        out["probe_dist"] = {}
        for ch in obs1.PROBES:
            Dp = _arr(cell_rec["probes"][ch]["D"])
            out["probe_dist"][ch] = obs1_reveal.geometry_match(
                Dp, Hq, Hg)["quot"]
    elif fam == "j2":
        coords = obs1_reveal.hidden_quotient_coords(tag, L)
        Hq = obs1_reveal.hidden_quotient_matrix(coords, nodes, L)
        Hg = obs1_reveal.hidden_graph_matrix(g, nodes)
        A = np.zeros((n, n), dtype=bool)
        for a, b in C["edges"]:
            A[a, b] = A[b, a] = True
        out["local2"] = obs1_reveal.local_chart_report(D, coords, nodes, L)
        out["local3"] = dim3_reveal.local_chart_report3(
            _lift2(D), {v: (p[0], p[1], 0.0) for v, p in coords.items()},
            nodes, L, d=3)
        out["locality"] = obs1_reveal.locality_report(A, Hq)
        sheets = obs1_reveal.hidden_sheets(tag, L)
        out["sheet"] = obs1_reveal.sheet_report(
            D, [sheets[v] for v in nodes])
        out["topo"] = obs1_reveal.topology_report(C["wrap"]["pairs"], coords,
                                                  nodes, L, Hq)
        out["match"] = obs1_reveal.geometry_match(D, Hq, Hg)
        out["probe_dist"] = {}
        for ch in obs1.PROBES:
            Dp = _arr(cell_rec["probes"][ch]["D"])
            out["probe_dist"][ch] = obs1_reveal.geometry_match(
                Dp, Hq, Hg)["quot"]
    else:
        out["match"] = {"quot": None, "micro": None, "closer": None}
        out["locality"] = {"frac": float("nan"), "pass": False}
        out["sheet"] = {"contrast": float("nan"), "pass": False}
        out["local3"] = {"med": float("nan"), "n": 0, "pass": False}
        out["local2"] = {"med": float("nan"), "n": 0, "pass": False}
        out["topo"] = {"precision": float("nan"), "n": 0, "pass": False}
        out["probe_dist"] = {}
    return out


def _lift2(D):
    return np.asarray(D, dtype=float)


def dim3_reveal_topology_align(X, coords, nodes):
    if X is None or coords is None:
        return {"eps": float("nan")}
    Y = np.array([coords[v] for v in nodes], dtype=float)
    r = obs1.procrustes_align(np.asarray(X, dtype=float), Y)
    return {"eps": float(r["eps"]), "scale": float(r["scale"]),
            "reflection": bool(r["reflection"])}


def stage_ab():
    """Re-verify Stages A/B exactly (read-only, L=8 torus + ball R=6)."""
    out = {}
    # A: quotient / multiplicity / bipartition / sectors at L=8.
    L = 8
    g = dim3.j3_torus_graph(L, SWAP_XY)
    c4 = dim3.j3_torus_coords(L)
    cells, q, mult = dim3.quotient_cells_edges(g, dim3.j3_cell_of(c4))
    out["A_degree12"] = sorted(set(d for _, d in g.degree())) == [12]
    out["A_quot_edges"] = q.number_of_edges() == 3 * L ** 3
    out["A_quot_cubic"] = dim3.quotient_is_cubic_ok(q, L)
    out["A_mult4"] = sorted(set(mult.values())) == [4]
    out["A_bipartite"] = dim3.is_bipartition_ok(g, dim3.bipartition_j3(c4))
    order = sorted(g.nodes())
    n = len(order)
    A = np.zeros((n, n))
    pos = {v: i for i, v in enumerate(order)}
    for u, v in g.edges():
        A[pos[u], pos[v]] = A[pos[v], pos[u]] = 1.0
    h = -A
    s = dim3.sheet_swap_matrix(order, c4).toarray()
    pr = {"P_anti": (np.eye(n) - s) / 2.0}
    u, _ = dim3.symmetric_embedding(order, c4)
    hq = dim3.cubic_hamiltonian(sorted({(x, y, z) for (x, y, z, _) in
                                        c4.values()}), (L, L, L))
    out["A_comm"] = float(np.abs(h @ s - s @ h).max())
    out["A_dead"] = float(np.abs(h @ pr["P_anti"]).max())
    out["A_inter"] = float(np.abs(h @ u - u @ hq).max())
    out["A_exact"] = bool(out["A_degree12"] and out["A_quot_edges"]
                          and out["A_quot_cubic"] and out["A_mult4"]
                          and out["A_bipartite"] and out["A_comm"] == 0.0
                          and out["A_dead"] == 0.0 and out["A_inter"] == 0.0)
    # B: Bloch-vs-brute at L=4, 6, 8.
    out["B"] = {}
    for Lb in (4, 6, 8):
        r = dim3.bloch_vs_exact(Lb)
        out["B"][str(Lb)] = {"max_dev": r["max_dev"],
                             "n_zero_exact": r["n_zero_exact"],
                             "n_zero_predicted": r["n_zero_predicted"],
                             "ok": bool(r["max_dev"] < 1e-9 and
                                        r["n_zero_exact"]
                                        == r["n_zero_predicted"])}
    out["B_ok"] = bool(all(v["ok"] for v in out["B"].values()))
    return out


def load_json(path):
    with open(path) as f:
        return json.load(f)


def eval_ports(datadir):
    """Evaluate the G/H/I characterization ports (filed, not gating)."""
    ports = {}
    # G-a packets.
    for t in ("j3-L12", "j3-L16", "cb-L15"):
        p = os.path.join(datadir, f"dim3_packet_{t}.json")
        if not os.path.exists(p):
            ports[f"packet_{t}"] = {"pass": False, "missing": True}
            continue
        d = load_json(p)
        vb = d["v_bloch"]
        vp = d["plus"]["speed"]
        vm = d["minus"]["speed"]
        ok = bool(abs(vp - vb) / vb < 0.10 and d["plus"]["r2"] > 0.99
                  and d["plus"]["norm_ok"] and d["minus"]["norm_ok"]
                  and d["cos_pm"] < -0.95
                  and abs(vp - vm) / max(vp, 1e-300) < 0.10)
        ports[f"packet_{t}"] = {"pass": ok, "v+": vp, "v Bloch": vb,
                                "cos": d["cos_pm"]}
    # G-b POT0 rungs (banked POT-0 bars on the 4-rung core).
    for t in ("j3-L12", "cb-L15"):
        p = os.path.join(datadir, f"dim3_pot0_{t}.json")
        if not os.path.exists(p):
            ports[f"pot0_{t}"] = {"pass": False, "missing": True}
            continue
        from bh_graph.potential import (cos_between, is_match_ok,  # noqa: E402
                                        spearman)
        d = load_json(p)
        src = d["A"]
        pkt = d["B"]
        pktm = d["Bm"]
        A = bool(src["mean_D"] < 0.05)
        ratio = pkt["mean_D"] / max(src["mean_D"], 1e-9)
        cos_pm = cos_between(np.asarray(pkt["mean_J"], dtype=float),
                             np.asarray(pktm["mean_J"], dtype=float))
        B = bool(pkt["mean_D"] > 0.5
                 and (pkt["mean_D"] - src["mean_D"]) > 0.4 and ratio > 10
                 and pkt["alpha"] > 1.3 and pkt["cv_mean50"] > 0.5
                 and cos_pm < -0.95
                 and is_match_ok(pkt["mean_D"], pktm["mean_D"], 0.10)
                 and pkt["r2"] > 0.99 and pktm["r2"] > 0.99)
        grid = list(d["C_GRID"])
        gv, gd = d["C"]["gv"], d["C"]["gd"]
        nd = d["C"]["nd"]
        C = bool(gd[-1] / max(gd[0], 1e-9) > 10
                 and spearman(gv, grid) > 0.7
                 and gv[0] < 0.05 * max(gv[-1], 1e-300)
                 and spearman(nd, grid) > 0.5
                 and nd[-1] / max(nd[0], 1e-9) > 5)
        scr = d["D_scr"]
        rest = d["D_rest"]
        D = bool(scr["mean_D"] < 0.15 * pkt["mean_D"]
                 and scr["prep_C"] < 0.5 * pkt["prep_C"]
                 and is_match_ok(rest["mean_D"], pkt["mean_D"], 0.15)
                 and is_match_ok(rest["prep_C"], pkt["prep_C"], 0.15)
                 and spearman(d["pool"]["C"], d["pool"]["D"]) > 0.5)
        ports[f"pot0_{t}"] = {"pass": bool(A and B and C and D),
                              "A": A, "B": B, "C": C, "D": D,
                              "cos_pm": cos_pm}
    # G-c POT1 existence + exactness.
    for t in ("j3-L12", "j3-L16", "cb-L15"):
        p = os.path.join(datadir, f"dim3_pot1_{t}.json")
        if not os.path.exists(p):
            ports[f"pot1_{t}"] = {"pass": False, "missing": True}
            continue
        d = load_json(p)
        ports[f"pot1_{t}"] = {"pass": bool(d["resid"] < 1e-9),
                              "resid": d["resid"], "xi": d["xi"]}
    # G-d switch fronts (family Bloch-Manhattan normalization; J3 /12
    # prereg-verbatim, cubic /6 dimensional analog).
    for t in ("j3-L16", "cb-L20"):
        p = os.path.join(datadir, f"dim3_switch_{t}.json")
        if not os.path.exists(p):
            ports[f"switch_{t}"] = {"pass": False, "missing": True}
            continue
        d = load_json(p)
        v = (d.get("front") or {}).get("v")
        vmax = 12.0 if t.startswith("j3") else 6.0
        ports[f"switch_{t}"] = {
            "pass": bool(v is not None and np.isfinite(v)
                         and 0.85 <= v / vmax <= 1.00
                         and (d["front"].get("r2") or 0) > 0.9),
            "v": v, "vmax": vmax}
    # H-a..H-d sectors.
    for t in ("j3-L8", "j3-L12", "j3-L16"):
        p = os.path.join(datadir, f"dim3_sector_{t}.json")
        if not os.path.exists(p):
            ports[f"sector_{t}"] = {"pass": False, "missing": True}
            continue
        d = load_json(p)
        a_ok = bool(d["comm"] == 0.0 and d["dead"] == 0.0
                    and d["inter"] == 0.0)
        remote = [r for r in d["cap_neg"] if int(r) >= 2]
        b_ok = bool(all(d["cap_neg"][r] < 1e-9 for r in remote)
                    and max(d["cap_pos"][r] for r in remote) > 1e-3)
        c_ok = bool(d["lrw_comm"] < 1e-12 and d["diff_anti_w_max"] < 1e-9)
        # H-d gate = exact support legs only. The naive sqrt2 far-field bar
        # is DESCRIPTIVE per banked QUOT-0 precedent (J2 measured 0.38:
        # prereg-design error, defect-induced monopole shift; mechanism
        # confirmed in stronger form via exact support + remote blindness).
        dd_ok = bool(d["pot_anti_support"]
                     and d["pot_anti_support_mixed"])
        ports[f"sector_{t}"] = {"pass": bool(a_ok and b_ok and c_ok and dd_ok),
                                "a": a_ok, "b": b_ok, "c": c_ok, "d": dd_ok,
                                "pot_far_rel": d["pot_far_rel"],
                                "pot_far_rel_L2": d.get("pot_far_rel_L2"),
                                "pot_mixed_anti_r1_max": d.get(
                                    "pot_mixed_anti_r1_max")}
    # H-e bilayer.
    p = os.path.join(datadir, "dim3_bilayer_bcb-L8.json")
    if os.path.exists(p):
        d = load_json(p)
        ports["bilayer"] = {"pass": bool(d["contrast"] > 0.30),
                            "contrast": d["contrast"]}
    else:
        ports["bilayer"] = {"pass": False, "missing": True}
    # H-f/H-g hidden.
    p = os.path.join(datadir, "dim3_hidden_j3-L8.json")
    if os.path.exists(p):
        d = load_json(p)
        legs = {k: bool(v["local_ok"] and v["wave_ok"] and v["diff_ok"]
                        and v["pot_remote_max"] < 1e-9)
                for k, v in d["legs"].items()}
        hg = bool(d["hg"]["n_flip"] > 100)
        ports["hidden"] = {"pass": bool(all(legs.values()) and hg),
                           "legs": legs, "hg": hg,
                           "n_flip": d["hg"]["n_flip"]}
    else:
        ports["hidden"] = {"pass": False, "missing": True}
    # I vacuum census.
    for L in (4, 8, 12):
        p = os.path.join(datadir, f"dim3_vacuum_L{L}.json")
        if not os.path.exists(p):
            ports[f"vacuum_L{L}"] = {"pass": False, "missing": True}
            continue
        d = load_json(p)
        cands = {}
        for name in ("VPLUS", "VPI", "VMINUS"):
            v = d["cands"][name]
            if name == "VMINUS":
                # Banked E-vacuous rule (VAC-FIELD Amendment-4).
                sc = v["scaling"]
                st = 0.01  # vacfield.BARS["scaling_slope"]
                sb = 1e-9  # vacfield.BARS["scaling_normed"]
                sc_ok = bool(
                    not sc["Q"]["trivial"]
                    and abs(sc["Q"]["slope"] - 2.0) < st
                    and not sc["Bmax"]["trivial"]
                    and abs(sc["Bmax"]["slope"] - 2.0) < st
                    and sc["Eabs"]["trivial"] and v["scaling_e_vacuous"]
                    and sc["normed_spread"] < sb)
            else:
                sc_ok = bool(v["scaling_ok"])
            led = v["ledger"]
            if name == "VPLUS":
                pat = bool(led["f_zero"] == 1.0)
            elif name == "VPI":
                pat = bool(led["f_neg"] == 0.0 and led["f_zero"] < 1.0)
            else:
                pat = bool(led["f_neg"] > 0.0 and led["f_pos"] > 0.0
                           and abs(led["mean"]) < 1e-12)
            cands[name] = bool(v["eigen_res"] < 1e-9
                               and v["stationary"]["ok"] and v["current_ok"]
                               and v["phase_ok"] and sc_ok
                               and v["stress_ok"] and pat)
        cands["ZERO_bg"] = bool(d["cands"]["ZERO"]["bmax"] == 0.0)
        ports[f"vacuum_L{L}"] = {"pass": bool(all(cands.values())),
                                 "cands": cands}
    return ports


def eval_spread(d, tag):
    """Evaluate one spread record against the E/F gates.

    Velocity normalized by the family Bloch-Manhattan bound (j3: 12
    prereg-verbatim; cb: 6, j2: 8 dimensionally-correct analogs, filed).
    """
    fam = tag.split("-")[0]
    vmax = {"j3": 12.0, "cb": 6.0, "j2": 8.0}[fam]
    f = d["fits"]
    front = d.get("front", {})
    v = front.get("v")
    v_ok = (v is not None and np.isfinite(v)
            and 0.90 <= v / vmax <= 1.00
            and (front.get("r2") or 0) > 0.9)
    e_psi = f["psi"]
    e_rho = f["rho"]
    e_j = f["J"]
    psi_ok = (np.isfinite(e_psi["alpha"] or np.nan)
              and 0.80 <= e_psi["alpha"] <= 1.20 and e_psi["r2"] > 0.9)
    rho_ok = (np.isfinite(e_rho["alpha"] or np.nan)
              and 1.70 <= e_rho["alpha"] <= 2.30 and e_rho["r2"] > 0.9)
    j_ok = (np.isfinite(e_j["alpha"] or np.nan)
            and 1.70 <= e_j["alpha"] <= 2.30 and e_j["r2"] > 0.9)
    b_ok = (d.get("bmax") or np.inf) < 1e-9
    return {"v": v, "vmax": vmax, "v_ok": bool(v_ok),
            "psi_ok": bool(psi_ok), "rho_ok": bool(rho_ok),
            "j_ok": bool(j_ok), "b_ok": bool(b_ok)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--blind", required=True)
    ap.add_argument("--sealdir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cells", type=int, nargs="+", required=True)
    ap.add_argument("--sets", type=int, nargs="+", required=True)
    args = ap.parse_args()

    with open(args.blind, "rb") as f:
        blob = f.read()
    with open(args.blind + ".sha256") as f:
        frozen = f.read().strip()
    digest = hashlib.sha256(blob).hexdigest()
    if digest != frozen:
        raise SystemExit(
            f"BLIND HASH MISMATCH: {digest} != frozen {frozen} -- STOP.")
    blind = json.loads(blob.decode())

    cells = {}
    for c in args.cells:
        seals, tags = {}, set()
        for s in args.sets:
            sm = load_json(os.path.join(
                args.sealdir, f"dim3_seal_cell{c}_s{s}.json"))
            seals[s] = sm
            tags.add(sm["tag"])
        assert len(tags) == 1
        tag = tags.pop()
        L = DC.tag_L(tag)
        g = DC.tag_graph(tag)
        per_set, rev = {}, {}
        for s in args.sets:
            sm = seals[s]
            nodes = [sm["stations"][f"S{i}"] for i in range(64)]
            rec = blind["cells"][str(c)]["sets"][str(s)]
            per_set[s] = blind_set_flags(rec["probes"])
            cross = rec["cross"]
            per_set[s]["cross"] = bool(all(
                cross[k]["rms_pass"] and cross[k]["d_pass"]
                for k in ("WD", "WP", "DP")))
            rev[s] = reveal_set(rec, tag, nodes, g, L)
        ds = [per_set[s]["d"] for s in args.sets]
        dok = [per_set[s]["dim_ok"] for s in args.sets]
        fam = tag.split("-")[0]
        is3d = fam in ("j3", "cb")
        cells[tag] = {
            "cell": c, "sets": per_set, "reveal": rev,
            "METRIC_OK": _maj(per_set[s]["metric_ok"] for s in args.sets),
            "DIM": _med(ds), "DIM_STABLE": bool(
                _maj(dok) and (float(np.nanmax(ds)) - float(np.nanmin(ds))
                <= obs1.DIM_STABLE_BAR)),
            "EMB_OK": _maj(per_set[s]["emb"] for s in args.sets),
            "LOCAL3_OK": _maj(rev[s]["local3"]["pass"] for s in args.sets),
            "LOCAL2_OK": _maj(rev[s]["local2"]["pass"] for s in args.sets),
            "DIST_OK": _maj(rev[s]["match"].get("quot_pass", False)
                             for s in args.sets),
            "FACTOR_OK": _maj((rev[s]["match"].get("factor") or 0) >= 1.5
                               for s in args.sets),
            "LOC_OK": _maj(rev[s]["locality"]["pass"] for s in args.sets),
            "SHEET_OK": _maj(rev[s]["sheet"]["pass"] for s in args.sets),
            "CROSS_OK": _maj(per_set[s]["cross"] for s in args.sets),
            "D3": bool(np.isfinite(_med(ds)) and abs(_med(ds) - 3.0) <= 0.25),
            "DSTAR3": _maj(per_set[s]["dstar"] == 3
                            and per_set[s]["dstar_pass"]
                            and per_set[s]["replicated"] for s in args.sets),
            "D2": bool(np.isfinite(_med(ds)) and abs(_med(ds) - 2.0) <= 0.5),
            "DSTAR2": _maj(per_set[s]["dstar"] == 2
                            and per_set[s]["dstar_pass"]
                            and per_set[s]["replicated"] for s in args.sets),
            "is3d": is3d,
        }
        print(f"reveal {tag}: DIM={cells[tag]['DIM']:.3f} "
              f"DSTAR={[per_set[s]['dstar'] for s in args.sets]} "
              f"DIST_OK={cells[tag]['DIST_OK']} "
              f"LOCAL3_OK={cells[tag]['LOCAL3_OK']}", flush=True)

    def _cell(tag):
        return cells.get(tag, {"DIM": float("nan"), "METRIC_OK": False,
                              "DIM_STABLE": False, "EMB_OK": False,
                              "LOCAL3_OK": False, "LOCAL2_OK": False,
                              "DIST_OK": False, "FACTOR_OK": False,
                              "LOC_OK": False, "SHEET_OK": False,
                              "CROSS_OK": False, "D3": False,
                              "DSTAR3": False, "D2": False,
                              "DSTAR2": False, "sets": {}, "cell": -1})

    # Stage C/D per-J3-cell gates (majority-of-sets each; all 3 cells).
    j3tags = ["j3-L8", "j3-L12", "j3-L16"]
    C_cells, D_cells = {}, {}
    for t in j3tags:
        J = _cell(t)
        C_cells[t] = bool(J["D3"] and J["DSTAR3"] and J["METRIC_OK"]
                          and J["EMB_OK"])
        D_cells[t] = bool(J["DIST_OK"] and J["FACTOR_OK"] and J["LOC_OK"]
                          and J["SHEET_OK"] and J["LOCAL3_OK"])
    C_PASS = bool(all(C_cells.values()))
    D_PASS = bool(all(D_cells.values()))

    # Controls: C0 cubic reads 3D; C2 J2 reads 2D; C1 expanders reject 3D.
    C0 = {t: bool(_cell(t)["D3"] and _cell(t)["DSTAR3"]
                  and _cell(t)["DIST_OK"] and _cell(t)["LOCAL3_OK"]
                  and _cell(t)["LOC_OK"])
          for t in ("cb-L10", "cb-L15", "cb-L20")}
    C0_PASS = bool(all(C0.values()))
    J2 = _cell("j2-L42")
    C2_PASS = bool(J2["D2"] and J2["DSTAR2"])
    C1, c1_detail = True, {}
    for t in ("ex-N1024-s0", "ex-N3456-s0", "ex-N8192-s0"):
        E = _cell(t)
        if E["cell"] < 0:
            c1_detail[t] = {"threed_sets": -1, "data_sets": -1,
                            "pass": False}
            C1 = False
            continue
        threed_sets = sum(
            1 for s in args.sets
            if E["sets"][s]["dim_ok"]
            and abs(E["sets"][s]["d"] - 3.0) <= 0.25
            and E["sets"][s]["dstar"] == 3
            and E["sets"][s]["dstar_pass"]
            and E["sets"][s]["replicated"])
        data_sets = sum(
            1 for s in args.sets
            if blind["cells"][str(E["cell"])]["sets"][str(s)]
            ["probes"]["C"]["measured_frac"] >= 0.5)
        ok = bool(threed_sets == 0 and data_sets >= MAJ)
        c1_detail[t] = {"threed_sets": threed_sets, "data_sets": data_sets,
                        "pass": ok}
        C1 = C1 and ok

    # Stages E/F from spread records.
    datadir = os.path.dirname(args.blind)
    spread, E_tags, P_tags, F_tags = {}, {}, {}, {}
    for t in DC.SPREAD_TAGS:
        spread[t] = {}
        for kind in ("R", "I"):
            p = os.path.join(datadir, f"dim3_spread_{t}_BG0_{kind}_1.json")
            if os.path.exists(p):
                spread[t][kind] = eval_spread(load_json(p), t)
        if spread[t]:
            E_tags[t] = bool(all(spread[t][k]["v_ok"]
                                 and spread[t][k]["psi_ok"]
                                 for k in spread[t]))
            P_tags[t] = bool(all(spread[t][k]["psi_ok"]
                                 for k in spread[t]))
            F_tags[t] = bool(all(spread[t][k]["rho_ok"]
                                 and spread[t][k]["j_ok"]
                                 and spread[t][k]["b_ok"]
                                 for k in spread[t]))
    j3spread_tags = ["j3-L8", "j3-L12", "j3-L16"]
    E_PASS = bool(all(E_tags.get(t, False) for t in j3spread_tags))
    F_PASS = bool(all(F_tags.get(t, False) for t in j3spread_tags))
    # E-c 2D control: J2-L28 alpha in [0.40, 0.60].
    Ec = True
    for kind in ("R", "I"):
        p = os.path.join(datadir, f"dim3_spread_j2-L28_BG0_{kind}_1.json")
        if not os.path.exists(p):
            Ec = False
            continue
        a = load_json(p)["fits"]["psi"]
        Ec = Ec and bool(np.isfinite(a["alpha"] or np.nan)
                         and 0.40 <= a["alpha"] <= 0.60 and a["r2"] > 0.9)
    # F-d cubic class check: same EXPONENT windows (psi/rho/J/b), filed.
    # Cubic velocity is filed under its own /6 normalization (eval_spread),
    # not the J3 /12 bar.
    Fd = bool(all(F_tags.get(t, False) for t in ("cb-L10", "cb-L15", "cb-L20"))
              and all(P_tags.get(t, False)
                      for t in ("cb-L10", "cb-L15", "cb-L20")))

    # Stage J size consistency (filed spreads; gates).
    def _alphas(key, obs):
        vals = []
        for t in j3spread_tags:
            for kind in ("R", "I"):
                p = os.path.join(
                    datadir, f"dim3_spread_{t}_BG0_{kind}_1.json")
                if os.path.exists(p):
                    vals.append(load_json(p)["fits"][obs]["alpha"])
        return [v for v in vals if v is not None and np.isfinite(v)]

    j_psi = _alphas("psi", "psi")
    j_rho = _alphas("rho", "rho")
    J_spread = bool(j_psi and j_rho
                    and max(j_psi) - min(j_psi) < 0.20
                    and max(j_rho) - min(j_rho) < 0.20)
    dj = [_cell(t)["DIM"] for t in j3tags]
    J_dim = bool(all(np.isfinite(d) for d in dj)
                 and max(dj) - min(dj) < 0.30)
    J_PASS = bool(J_spread and J_dim)

    # Stages A/B re-verification.
    ab = stage_ab()
    A_PASS = bool(ab["A_exact"])
    B_PASS = bool(ab["B_ok"])

    # Ports G/H/I (characterization; filed, not headline-gating).
    ports = eval_ports(datadir)

    # Headline.
    full = len(args.cells) >= 10 and len(args.sets) >= 3
    not3d_dstar = _maj(_cell(t)["DSTAR2"] for t in j3tags)
    not3d_exp = False
    n2d = 0
    for t in j3spread_tags:
        for kind in ("R", "I"):
            p = os.path.join(datadir, f"dim3_spread_{t}_BG0_{kind}_1.json")
            if os.path.exists(p):
                a = load_json(p)["fits"]["psi"]
                if np.isfinite(a["alpha"] or np.nan) and a["r2"] > 0.9 \
                        and 0.35 <= a["alpha"] <= 0.65:
                    n2d += 1
    not3d_exp = n2d >= 4  # 2D-like exponents on >= 2 J3 sizes (R+I)
    if not full:
        headline = "DIM3-INCOMPLETE"
    elif not A_PASS:
        headline = "DIM3-NATURALITY-DEBT"
    elif C_PASS and D_PASS and E_PASS and F_PASS and C0_PASS and C1 \
            and C2_PASS and B_PASS:
        headline = "DIM3-OPERATIONAL"
    elif not3d_dstar or not3d_exp:
        headline = "DIM3-NOT3D"
    elif A_PASS and B_PASS:
        headline = "DIM3-GEOMETRIC"
    else:
        headline = "DIM3-GEOMETRIC"

    verdict = {
        "headline": headline, "blind_sha256": frozen,
        "A": ab, "A_PASS": A_PASS, "B_PASS": B_PASS,
        "C_cells": C_cells, "C_PASS": C_PASS,
        "D_cells": D_cells, "D_PASS": D_PASS,
        "E_tags": E_tags, "E_PASS": E_PASS,
        "F_tags": F_tags, "F_PASS": F_PASS,
        "controls": {"C0": C0, "C0_PASS": C0_PASS, "C2_PASS": C2_PASS,
                     "C1": C1, "c1_detail": c1_detail,
                     "E_c_2d": Ec, "F_d_cubic": Fd},
        "J": {"psi_spread": (max(j_psi) - min(j_psi)) if j_psi else None,
              "rho_spread": (max(j_rho) - min(j_rho)) if j_rho else None,
              "dim_spread": (max(dj) - min(dj))
              if all(np.isfinite(d) for d in dj) else None,
              "J_PASS": J_PASS},
        "ports": ports,
        "cells": cells,
    }
    with open(args.out, "w") as f:
        json.dump(run_obs0.jsonable(verdict), f)
    print(f"verdict: {headline} (A={A_PASS} B={B_PASS} C={C_PASS} "
          f"D={D_PASS} E={E_PASS} F={F_PASS} C0={C0_PASS} C1={C1} "
          f"C2={C2_PASS} J={J_PASS})")


if __name__ == "__main__":
    main()
