"""SYM-0 census campaign (frozen SYM0-PREREG cells, pre-data).

Tasks (mp pool, module-level workers, 96-way on beast):
  - inventory: per-substrate transform applicability + Aut evidence.
  - pair: per (substrate, field, transform, param) witness distances.
  - theta: per (substrate, field, t) Theta-identity errors.
  - landmark: J2-L6 relational two-packet protocol (SYM-0G).
  - stab: per (group, substrate, field) stabilizer/order/identity.
  - dyn: redundant-pair evolution preservation + S-pair measurement.
  - ucell: per (law, substrate, field, transform) marks covariance.
  - recount: RAND battery edge/node patch five-scheme recount (SYM-0V).
  - fs: phase-quotient metric battery (SYM-0X).
  - hierarchy: probe-pair O1..O5 class counts (SYM-0Q/R).
  - replay: banked QUOT/OBS read-only replay manifest (SYM-0 O5).

Deterministic (frozen seeds only). Output: data/sym0_ledger.json. Gates
applied by scripts/sym0_analyze.py. NO fitting after opening data.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import sym0
from bh_graph.sym0 import (FP_ZERO, OB_FAMILIES, SCALE_GRID, SHIFT_GRID,
                           SHEET_PHASE_GRID, THETA_T_GRID, U1_ALPHAS)

FIELDS_U = ("uniform", "current", "packet", "generic-s0")
FIELDS_THETA = ("uniform", "current", "packet", "generic-s0")
FIELDS_DYN = ("uniform", "packet")


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
    return x


def _get_state(sub_name, field):
    bat = sym0.sym0_states()
    sub = bat["substrates"][sub_name]
    return sub, bat["fields"][sub_name][field]


def _aut_perms(sub_name, sub):
    from bh_graph.potential import rot90_perm, translate_perm
    kind = sub["kind"]
    if kind == "j2":
        L = sub["L"]
        return [("T10", translate_perm(L, 1, 0)),
                ("T01", translate_perm(L, 0, 1)),
                ("rot90", rot90_perm(L))]
    if kind == "ring":
        return [("rot1", sym0.ring_rotation(len(sub["order"]), 1))]
    if kind == "path":
        return [("reversal", sym0.path_reversal(len(sub["order"])))]
    if kind == "square":
        return [("T10", sym0.square_translation(4, 1, 0))]
    res = sym0.full_aut_group(sub["g"])
    if not res["ok"]:
        return []
    ident = {v: v for v in sub["order"]}
    nontriv = [p for p in res["auts"] if p != ident]
    return [(f"aut{k}", p) for k, p in enumerate(nontriv[:3])]


def _t_perm(sub_name, sub):
    from bh_graph.potential import translate_perm
    if sub["kind"] == "j2":
        return ("T10", translate_perm(sub["L"], 1, 0))
    if sub["kind"] == "square":
        return ("T10", sym0.square_translation(4, 1, 0))
    if sub["kind"] == "ring":
        return ("rot1", sym0.ring_rotation(len(sub["order"]), 1))
    return (None, None)


# ---------------------------------------------------------------------------
# Workers
# ---------------------------------------------------------------------------

def run_inventory_task(sub_name):
    bat = sym0.sym0_states()
    sub = bat["substrates"][sub_name]
    out = {"substrate": sub_name, "n": len(sub["order"]),
           "fields": sorted(bat["fields"][sub_name]),
           "applicability": {},
           "aut_evidence": {}}
    for tid in sym0.TRANSFORM_IDS:
        out["applicability"][tid] = bool(
            sym0.is_transform_applicable_ok(tid, sub))
    for name, perm in _aut_perms(sub_name, sub):
        out["aut_evidence"][name] = bool(sym0.is_perm_auto_ok(sub["g"], perm))
    if sub["kind"] == "j2":
        out["sheet_auto"] = bool(sym0.is_perm_auto_ok(
            sub["g"], sym0.sheet_perm_from_c3(sub["c3"])))
    return _sanitize(out)


def run_pair_task(cell):
    sub_name, field, tid, param = cell
    bat = sym0.sym0_states()
    sub = bat["substrates"][sub_name]
    g, order = sub["g"], list(sub["order"])
    psi = np.asarray(bat["fields"][sub_name][field], dtype=np.complex128)
    obs_x = sym0.observe_all(psi, g, order, sub)
    extras = {}
    if tid == "R":
        perm = sym0.reversal_perm(order) if param == "reversal" \
            else sym0.shuffle_perm(order)
        r = sym0.apply_relabel(g, psi, order, perm)
        sub2 = dict(sym0.transport_sub(sub, perm))
        sub2["g"] = r["g"]
        obs_y = sym0.observe_all(r["psi"], r["g"], r["order"], sub2)
        obs_y = sym0.transport_obs_back(obs_y, order, r["order"], perm)
    elif tid in ("Aut", "T"):
        perms = dict(_aut_perms(sub_name, sub))
        if tid == "T":
            tname, tperm = _t_perm(sub_name, sub)
            perms = {tname: tperm}
        perm = perms[param]
        extras["auto_verified"] = bool(sym0.is_perm_auto_ok(g, perm))
        psi_y = sym0.apply_pushforward(psi, order, perm)
        obs_y = sym0.observe_all(psi_y, g, order, sub)
        if field == "packet" and sub.get("coords") is not None:
            from bh_graph.ballistic import com
            cx = np.asarray(com(psi, sub["coords"], order,
                               periods=sub["periods"]), dtype=float)
            cy = np.asarray(com(psi_y, sub["coords"], order,
                               periods=sub["periods"]), dtype=float)
            extras["com_x"] = cx
            extras["com_y"] = cy
    elif tid == "S":
        psi_y = sym0.apply_sheet_exchange(psi, order, sub["c3"])
        obs_y = sym0.observe_all(psi_y, g, order, sub)
    elif tid == "U1":
        psi_y = sym0.apply_u1(psi, float(param))
        obs_y = sym0.observe_all(psi_y, g, order, sub)
    elif tid == "C":
        psi_y = sym0.apply_conj(psi)
        obs_y = sym0.observe_all(psi_y, g, order, sub)
    elif tid == "Sign":
        # Sign has no independent code path: alias of U1(pi) by
        # construction (single implementation, pinned in test_sym0).
        extras["alias_by_construction"] = True
        obs_y = sym0.observe_all(sym0.apply_u1(psi, float(np.pi)), g, order,
                                 sub)
    elif tid == "Scale":
        psi_y = sym0.apply_scale(psi, float(param))
        obs_y = sym0.observe_all(psi_y, g, order, sub)
        a = float(param)
        extras["rho_ratio"] = float(
            np.abs(obs_y["O1"]["rho"] - a * a * obs_x["O1"]["rho"]).max())
    elif tid == "Shift":
        psi_y = sym0.apply_shift(psi, complex(param))
        obs_y = sym0.observe_all(psi_y, g, order, sub)
    elif tid == "SheetPhase":
        psi_y = sym0.apply_sheet_phase(psi, order, sub["c3"], float(param))
        obs_y = sym0.observe_all(psi_y, g, order, sub)
    elif tid == "SectorSign":
        psi_y = sym0.apply_sector_sign(psi, order, sub["c3"])
        ref = sym0.apply_sheet_exchange(psi, order, sub["c3"])
        extras["sect_eq_S"] = float(np.abs(psi_y - ref).max())
        obs_y = sym0.observe_all(psi_y, g, order, sub)
    elif tid == "CovB-U1":
        extras["covariance_err"] = float(sym0.covariance_err(
            lambda p: sym0.apply_u1(p, 1.1), psi, g, order))
        obs_y = obs_x
    elif tid == "CovB-Scale":
        extras["covariance_err"] = float(sym0.covariance_err(
            lambda p: sym0.apply_scale(p, 2.0), psi, g, order))
        obs_y = obs_x
    elif tid == "CovB-Shift":
        c = complex(0.1)
        extras["covariance_err"] = float(sym0.covariance_err(
            lambda p: sym0.apply_shift(p, c), psi, g, order))
        extras["shift_defect"] = extras["covariance_err"]
        obs_y = obs_x
    else:
        raise ValueError(f"unknown pair tid: {tid}")
    wit = sym0.witness_d(obs_x, obs_y, OB_FAMILIES)
    per = {fam: sym0.obs_distance(obs_x[fam], obs_y[fam], fam)
           for fam in OB_FAMILIES}
    extras["cond"] = sym0.o3_conditioning(obs_x["O3"], obs_y["O3"])
    return _sanitize({"cell": list(cell), "witness": wit, "per_readout": per,
                      "extras": extras})


def run_theta_task(cell):
    sub_name, field, t = cell
    sub, psi = _get_state(sub_name, field)
    err = sym0.theta_identity_err(np.asarray(psi), sub["g"],
                                  list(sub["order"]), float(t))
    return _sanitize({"cell": list(cell), "theta_err": err,
                      "ok": bool(err < sym0.KRYLOV_BAR)})


def run_landmark_task(_arg):
    from bh_graph.ballistic import com, gaussian_packet
    sub = sym0.sym0_states()["substrates"]["j2-L6"]
    order = list(sub["order"])
    A = gaussian_packet(sub["coords"], order, (1.0, 1.0), (0.8, 0.0), 1.0,
                        periods=sub["periods"])
    B = gaussian_packet(sub["coords"], order, (2.0, 1.0), (0.8, 0.0), 1.0,
                        periods=sub["periods"])
    O = gaussian_packet(sub["coords"], order, (4.0, 4.0), (0.0, 0.0), 1.0,
                        periods=sub["periods"])
    from bh_graph.potential import translate_perm
    perm = translate_perm(6, 1, 0)
    tA = sym0.apply_pushforward(A, order, perm)
    cA = np.asarray(com(A, sub["coords"], order, periods=sub["periods"]))
    cB = np.asarray(com(B, sub["coords"], order, periods=sub["periods"]))
    cO = np.asarray(com(O, sub["coords"], order, periods=sub["periods"]))
    ctA = np.asarray(com(tA, sub["coords"], order, periods=sub["periods"]))
    rel = lambda c, o: [float((c[0] - o[0]) % 6.0), float((c[1] - o[1]) % 6.0)]
    return _sanitize({"com_A": cA, "com_B": cB, "com_O": cO, "com_TA": ctA,
                      "rel_AO": rel(cA, cO), "rel_BO": rel(cB, cO),
                      "rel_TAO": rel(ctA, cO),
                      "TA_eq_B": float(np.abs(tA - B).max())})


def run_stab_task(cell):
    group_id, sub_name, field = cell
    sub, psi = _get_state(sub_name, field)
    order = list(sub["order"])
    psi = np.asarray(psi)
    if group_id == "j2T":
        perms = sym0.group_j2_translations(sub["L"])
    elif group_id == "ringC":
        perms = sym0.group_ring_rotations(len(order))
    elif group_id == "pathZ2":
        perms = sym0.group_path_flip(len(order))
    elif group_id == "sheetZ2":
        perms = sym0.group_sheet(sub["c3"])
    elif group_id == "tinyAut":
        perms = sym0.full_aut_group(sub["g"])["auts"]
    elif group_id == "conjZ2":
        return _sanitize({"cell": list(cell),
                          "kind": sym0.conj_stabilizer_kind(psi)})
    elif group_id == "u1":
        return _sanitize({"cell": list(cell),
                          "kind": sym0.u1_stabilizer_kind(psi)})
    else:
        raise ValueError(group_id)
    st = sym0.stabilizer_of(psi, order, perms)
    dc = sym0.distinct_orbit_count(psi, order, perms)
    ok = sym0.is_orbit_identity_ok(psi, order, perms)
    return _sanitize({"cell": list(cell), "stab_size": st["size"],
                      "group_size": st["group_size"], "n_distinct": dc["n_distinct"],
                      "orbit_size": st["group_size"] // max(st["size"], 1),
                      "identity_ok": bool(ok)})


def run_dyn_task(cell):
    sub_name, field, kind = cell
    sub, psi = _get_state(sub_name, field)
    order = list(sub["order"])
    g = sub["g"]
    psi = np.asarray(psi)
    n_steps = int(round(sym0.HORIZON_T / sym0.DT_FROZEN))
    if kind == "R":
        perm = sym0.shuffle_perm(order)
        r = sym0.apply_relabel(g, psi, order, perm)
        rows1 = sym0.evolve_rows(psi, g, order, sym0.DT_FROZEN, n_steps)
        rows2 = sym0.evolve_rows(r["psi"], r["g"], r["order"],
                                  sym0.DT_FROZEN, n_steps)
        pos2 = {v: i for i, v in enumerate(r["order"])}
        back = np.array([[row[pos2[perm[v]]] for v in order] for row in rows2])
        traj = float(np.abs(rows1 - back).max())
        sub2 = dict(sym0.transport_sub(sub, perm))
        sub2["g"] = r["g"]
        o1 = sym0.observe_all(rows1[-1], g, order, sub)
        o2 = sym0.observe_all(rows2[-1], r["g"], r["order"], sub2)
        o2 = sym0.transport_obs_back(o2, order, r["order"], perm)
        wit = sym0.witness_d(o1, o2, ("O1", "O2", "O3", "O4"))
    elif kind == "U1":
        psi2 = sym0.apply_u1(psi, float(np.pi) / 2.0)
        rows1 = sym0.evolve_rows(psi, g, order, sym0.DT_FROZEN, n_steps)
        rows2 = sym0.evolve_rows(psi2, g, order, sym0.DT_FROZEN, n_steps)
        align = np.array([sym0.phase_align(row, rows1[k])
                          for k, row in enumerate(rows2)])
        traj = float(np.abs(rows1 - align).max())
        o1 = sym0.observe_all(rows1[-1], g, order, sub)
        o2 = sym0.observe_all(rows2[-1], g, order, sub)
        wit = sym0.witness_d(o1, o2, ("O1", "O2", "O3", "O4"))
    elif kind == "S":
        psi2 = sym0.apply_sheet_exchange(psi, order, sub["c3"])
        rows1 = sym0.evolve_rows(psi, g, order, sym0.DT_FROZEN, n_steps)
        rows2 = sym0.evolve_rows(psi2, g, order, sym0.DT_FROZEN, n_steps)
        s_perm = sym0.sheet_perm_from_c3(sub["c3"])
        back = np.array([sym0.apply_pushforward(row, order, s_perm)
                         for row in rows2])
        # S intertwines dynamics: S U(t) psi = U(t) S psi (symmetry).
        traj = float(np.abs(rows1 - back).max())
        o1 = sym0.observe_all(rows1[-1], g, order, sub)
        o2 = sym0.observe_all(rows2[-1], g, order, sub)
        wit = sym0.witness_d(o1, o2, ("O1", "O2", "O3", "O4"))
    else:
        raise ValueError(kind)
    cond = sym0.o3_conditioning(o1["O3"], o2["O3"])
    return _sanitize({"cell": list(cell), "traj_defect": traj,
                      "endpoint": wit, "cond": cond})


def run_u_task(cell):
    law, sub_name, field, tid = cell
    sub, psi = _get_state(sub_name, field)
    order = list(sub["order"])
    g = sub["g"]
    if tid == "R-rev":
        ok = sym0.marks_covariance_R(g, psi, order, law,
                                     sym0.reversal_perm(order))
        rec = {"ok": bool(ok)}
    elif tid == "R-shuf":
        ok = sym0.marks_covariance_R(g, psi, order, law,
                                     sym0.shuffle_perm(order))
        rec = {"ok": bool(ok)}
    elif tid == "Aut0":
        perms = _aut_perms(sub_name, sub)
        perm = perms[0][1] if perms else None
        rec = {"ok": bool(sym0.marks_covariance_auto(g, psi, order, law, perm))
               if perm is not None else None,
               "perm_name": perms[0][0] if perms else None}
    elif tid == "U1":
        rec = {"ok": bool(sym0.marks_phase_invariance(g, psi, order, law,
                                                      float(np.pi) / 4.0))}
    elif tid == "C":
        rec = sym0.marks_conjugation_table(g, psi, order, law)
    elif tid == "S":
        perm = sym0.sheet_perm_from_c3(sub["c3"])
        rec = {"ok": bool(sym0.marks_covariance_auto(g, psi, order, law, perm))}
    elif tid == "Scale":
        from bh_graph.u0 import u0_decisions
        d1 = u0_decisions(g, np.asarray(psi), order, law)
        d2 = u0_decisions(g, sym0.apply_scale(psi, 2.0), order, law)
        rec = {"invariant": bool(all(d1[e]["decision"] == d2[e]["decision"]
                                     for e in d1))}
    elif tid == "Shift":
        from bh_graph.u0 import u0_decisions
        d1 = u0_decisions(g, np.asarray(psi), order, law)
        d2 = u0_decisions(g, sym0.apply_shift(psi, 0.1), order, law)
        rec = {"invariant": bool(all(d1[e]["decision"] == d2[e]["decision"]
                                     for e in d1))}
    else:
        raise ValueError(tid)
    return _sanitize({"cell": list(cell), "rec": rec})


def run_recount_task(key):
    from bh_graph.rand0 import rand0_states
    st = rand0_states()[key]
    g, psi, order = st["g"], st["psi"], list(st["order"])
    elist = sorted(tuple(sorted(e)) for e in g.edges())
    ei, ej = elist[len(elist) // 3]
    k = order[len(order) // 2]
    node = sym0.recount_node_patch(g, np.asarray(psi), order, k)
    gaps = {}
    if node["n_undirected"]:
        gaps["directed_vs_undirected"] = sym0.indifference_gap(
            node["n_directed"], node["n_undirected"])
        if not node["iso_capped"]:
            gaps["undirected_vs_iso"] = sym0.indifference_gap(
                node["n_undirected"], node["n_iso_classes"])
        if not node["stab_capped"]:
            gaps["undirected_vs_orbits"] = sym0.indifference_gap(
                node["n_undirected"], node["n_orbits"])
        gaps["undirected_vs_red"] = sym0.indifference_gap(
            node["n_undirected"], node["n_red_quotient"])
    return _sanitize({"key": key, "edge": [ei, ej], "node": k,
                      "degree": int(g.degree(k)), "node_recount": node,
                      "gaps": gaps})


def run_fs_task(cell):
    kind = cell[0]
    bat = sym0.sym0_states()
    if kind == "zero":
        _, sub_name, field, alpha = cell
        sub = bat["substrates"][sub_name]
        psi = np.asarray(bat["fields"][sub_name][field])
        d = sym0.fs_distance(psi, sym0.apply_u1(psi, float(alpha)))
        return _sanitize({"cell": list(cell), "d_fs": d})
    if kind == "dyn":
        _, sub_name, field_a, field_b = cell
        sub = bat["substrates"][sub_name]
        a = np.asarray(bat["fields"][sub_name][field_a])
        b = np.asarray(bat["fields"][sub_name][field_b])
        d0 = sym0.fs_distance(a, b)
        n = int(round(sym0.HORIZON_T / sym0.DT_FROZEN))
        ra = sym0.evolve_rows(a, sub["g"], list(sub["order"]),
                               sym0.DT_FROZEN, n)
        rb = sym0.evolve_rows(b, sub["g"], list(sub["order"]),
                               sym0.DT_FROZEN, n)
        d1 = sym0.fs_distance(ra[-1], rb[-1])
        return _sanitize({"cell": list(cell), "d0": d0, "d1": d1,
                          "drift": abs(d1 - d0)})
    if kind == "tri":
        _, sub_name, fa, fb, fc = cell
        sub = bat["substrates"][sub_name]
        f = bat["fields"][sub_name]
        ok = sym0.is_fs_triangle_ok(np.asarray(f[fa]), np.asarray(f[fb]),
                                    np.asarray(f[fc]))
        return _sanitize({"cell": list(cell), "ok": bool(ok)})
    raise ValueError(kind)


def run_hierarchy_task(_arg):
    sub = sym0.sym0_states()["substrates"]["j2-L6"]
    order = list(sub["order"])
    g = sub["g"]
    F = sym0.sym0_states()["fields"]["j2-L6"]
    from bh_graph.ballistic import gaussian_packet
    pkt_m = gaussian_packet(sub["coords"], order, (1.0, 1.0), (-0.8, 0.0),
                            1.0, periods=sub["periods"])
    members = {
        "uniform": F["uniform"],
        "uniform-U1": sym0.apply_u1(F["uniform"], 1.0),
        "packet": F["packet"],
        "packet-C": sym0.apply_conj(F["packet"]),
        "packet+k": F["packet"],
        "packet-k": pkt_m,
        "standing": F["standing"],
        "generic": F["generic-s0"],
        "generic-C": sym0.apply_conj(F["generic-s0"]),
        "current": F["current"],
        "current-C": sym0.apply_conj(F["current"]),
        "sheet-anti": F["sheet-anti"],
        "uniform-x2": sym0.apply_scale(F["uniform"], 2.0),
        "uniform+sh": sym0.apply_shift(F["uniform"], 0.1),
    }
    obs = {m: sym0.observe_all(np.asarray(p), g, order, sub)
           for m, p in members.items()}
    names = sorted(members)
    flags = {}
    for fam in OB_FAMILIES:
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                d = sym0.family_max(sym0.obs_distance(obs[a][fam], obs[b][fam], fam))
                # Scale pairs: O1/O2 absolute readouts move by construction;
                # hierarchy uses the frozen FP bar uniformly (filed).
                flags[(fam, a, b)] = bool(d < FP_ZERO)
    classes = {}
    for fam in OB_FAMILIES:
        pf = {(a, b): flags[(fam, a, b)] for i, a in enumerate(names)
              for j, b in enumerate(names) if j > i}
        classes[fam] = sym0.equivalence_classes(pf, names)
    counts = sym0.hierarchy_counts({fam: len(classes[fam]) for fam in OB_FAMILIES})
    return _sanitize({"members": names, "classes": classes, "counts": counts,
                      "n_flags": len(flags)})


def run_replay_task(_arg):
    home = os.path.expanduser("~")
    paths = [
        "quot-ea4c-data/quot_alg.json",
        "quot-ea4c-data/info_j2p-L28-e01.json",
        "quot-ea4c-data/quot_anatomy_lrw_o0.json",
        "quot-bank/obs1_blind.json.sha256",
        "rand0-1621/data/rand0_verdict.json",
        "u0-7069/data/u0_verdict.json",
        "cons0-4129/data/cons0_ledger.json",
    ]
    rec = {}
    for rel in paths:
        p = os.path.join(home, rel)
        if not os.path.exists(p):
            rec[rel] = {"exists": False}
            continue
        try:
            with open(p, "rb") as f:
                blob = f.read()
            h = hashlib.sha256(blob).hexdigest()
            entry = {"exists": True, "sha256": h, "bytes": len(blob)}
            if rel.endswith(".json"):
                try:
                    obj = json.loads(blob.decode("utf-8"))
                    if isinstance(obj, dict):
                        entry["top_keys"] = sorted(obj)[:20]
                        if "verdict" in obj:
                            entry["verdict"] = str(obj["verdict"])[:200]
                    else:
                        entry["json_type"] = type(obj).__name__
                except Exception as exc:
                    entry["json_error"] = str(exc)[:120]
            rec[rel] = entry
        except Exception as exc:
            rec[rel] = {"exists": True, "read_error": str(exc)[:120]}
    try:
        import bh_graph.zero0  # noqa: F401
        rec["zero0_apparatus"] = {"available": True}
    except Exception:
        rec["zero0_apparatus"] = {"available": False}
    return _sanitize(rec)


# ---------------------------------------------------------------------------
# Cell enumeration (frozen)
# ---------------------------------------------------------------------------

def build_cells():
    bat = sym0.sym0_states()
    pair_cells, theta_cells, stab_cells = [], [], []
    dyn_cells, u_cells, fs_cells = [], [], []
    for sub_name, sub in bat["substrates"].items():
        fields = sorted(bat["fields"][sub_name])
        for field in fields:
            pair_cells.append((sub_name, field, "R", "reversal"))
            pair_cells.append((sub_name, field, "R", "shuffle"))
            for name, _ in _aut_perms(sub_name, sub):
                pair_cells.append((sub_name, field, "Aut", name))
            tname, _ = _t_perm(sub_name, sub)
            if tname is not None:
                pair_cells.append((sub_name, field, "T", tname))
            for a in U1_ALPHAS:
                pair_cells.append((sub_name, field, "U1", a))
            pair_cells.append((sub_name, field, "C", ""))
            pair_cells.append((sub_name, field, "Sign", float(np.pi)))
            for a in SCALE_GRID:
                pair_cells.append((sub_name, field, "Scale", a))
            for c in SHIFT_GRID:
                pair_cells.append((sub_name, field, "Shift", str(complex(c))))
            if sub["kind"] == "j2":
                pair_cells.append((sub_name, field, "S", ""))
                for beta in SHEET_PHASE_GRID:
                    pair_cells.append((sub_name, field, "SheetPhase", beta))
                pair_cells.append((sub_name, field, "SectorSign", ""))
            if field in ("uniform", "generic-s0"):
                pair_cells.append((sub_name, field, "CovB-U1", ""))
                pair_cells.append((sub_name, field, "CovB-Scale", ""))
                pair_cells.append((sub_name, field, "CovB-Shift", ""))
        for field in fields:
            if field in FIELDS_THETA:
                for t in THETA_T_GRID:
                    theta_cells.append((sub_name, field, t))
        if sub["kind"] == "j2":
            for field in fields:
                stab_cells.append(("j2T", sub_name, field))
                stab_cells.append(("sheetZ2", sub_name, field))
        if sub["kind"] == "ring":
            for field in fields:
                stab_cells.append(("ringC", sub_name, field))
        if sub["kind"] == "path":
            for field in fields:
                stab_cells.append(("pathZ2", sub_name, field))
        if sub["kind"] == "tiny":
            for field in fields:
                stab_cells.append(("tinyAut", sub_name, field))
        for field in fields:
            stab_cells.append(("conjZ2", sub_name, field))
            stab_cells.append(("u1", sub_name, field))
        for field in fields:
            if field in FIELDS_DYN:
                dyn_cells.append((sub_name, field, "R"))
                dyn_cells.append((sub_name, field, "U1"))
                if sub["kind"] == "j2":
                    dyn_cells.append((sub_name, field, "S"))
        for field in fields:
            if field in FIELDS_U:
                for law in ("UB", "UL", "UEc"):
                    for tid in ("R-rev", "R-shuf", "Aut0", "U1", "C",
                                "Scale", "Shift"):
                        u_cells.append((law, sub_name, field, tid))
                    if sub["kind"] == "j2":
                        u_cells.append((law, sub_name, field, "S"))
    for sub_name, fset in (("square-torus-4",
                             ("uniform", "current", "generic-s0", "generic-s1")),
                            ("j2-L4",
                             ("uniform", "packet", "generic-s0", "current"))):
        for field in fset:
            for a in (0.7, 2.1):
                fs_cells.append(("zero", sub_name, field, a))
    for sub_name, fa, fb in (("square-torus-4", "uniform", "generic-s0"),
                             ("j2-L4", "packet", "generic-s0"),
                             ("j2-L4", "uniform", "sheet-anti"),
                             ("ring-12", "packet", "standing")):
        fs_cells.append(("dyn", sub_name, fa, fb))
    for sub_name, fa, fb, fc in (
            ("square-torus-4", "uniform", "generic-s0", "generic-s1"),
            ("square-torus-4", "uniform", "current", "antibonding"),
            ("j2-L4", "packet", "standing", "generic-s0"),
            ("j2-L4", "uniform", "sheet-anti", "generic-s0"),
            ("ring-12", "packet", "standing", "uniform")):
        fs_cells.append(("tri", sub_name, fa, fb, fc))
    return {"pair": pair_cells, "theta": theta_cells, "stab": stab_cells,
            "dyn": dyn_cells, "ucell": u_cells, "fs": fs_cells}


def main():
    t0 = time.time()
    workers = min(96, os.cpu_count() or 1)
    try:
        rev = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                             text=True, cwd=os.path.join(
                                 os.path.dirname(__file__), "..")).stdout.strip()
    except Exception:
        rev = "unknown"
    import networkx, scipy  # noqa: E402
    manifest = {"git_rev": rev, "host": platform.node(),
                "workers": workers, "t_start": time.time(),
                "versions": {"numpy": np.__version__,
                             "scipy": scipy.__version__,
                             "networkx": networkx.__version__}}
    cells = build_cells()
    out = {"manifest": manifest}
    with Pool(workers) as pool:
        bat = sym0.sym0_states()
        out["inventory"] = pool.map(run_inventory_task,
                                    sorted(bat["substrates"]))
        out["pair"] = pool.map(run_pair_task, cells["pair"], chunksize=4)
        out["theta"] = pool.map(run_theta_task, cells["theta"], chunksize=8)
        out["landmark"] = pool.map(run_landmark_task, [0])
        out["stab"] = pool.map(run_stab_task, cells["stab"], chunksize=8)
        out["dyn"] = pool.map(run_dyn_task, cells["dyn"], chunksize=2)
        out["ucell"] = pool.map(run_u_task, cells["ucell"], chunksize=16)
        from bh_graph.rand0 import rand0_states
        out["recount"] = pool.map(run_recount_task, sorted(rand0_states()))
        out["fs"] = pool.map(run_fs_task, cells["fs"], chunksize=4)
        out["hierarchy"] = pool.map(run_hierarchy_task, [0])
        out["replay"] = pool.map(run_replay_task, [0])
    out["manifest"]["t_end"] = time.time()
    out["manifest"]["wall_s"] = time.time() - t0
    ledger = os.path.join(os.path.dirname(__file__), "..", "data",
                          "sym0_ledger.json")
    with open(ledger, "w") as f:
        json.dump(_sanitize(out), f)
    print(f"cells: {sum(len(v) for v in cells.values())} "
          f"wall={out['manifest']['wall_s']:.1f}s -> {ledger}")


if __name__ == "__main__":
    main()
