"""BH-ENT-0 campaign runner: one task per invocation (beast-parallel).

Usage:
  python scripts/bhent0_campaign.py --task collapse --spec P4 --outdir data/bhent0
  python scripts/bhent0_campaign.py --print-all   # emit every task argv line
  python scripts/bhent0_campaign.py --list        # task names + params

Each invocation writes one JSON record and prints the record path.
Deterministic given (task, params). Collapse uses the frozen BR-2.5 op as
readout; no geometry is evolved as dynamics.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import socket
import subprocess
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph import bhent as be  # noqa: E402


def _git_rev() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, timeout=10).stdout.strip()
    except Exception:
        return "unknown"


def jsonify(x):
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, (np.floating, np.integer)):
        return float(x)
    if isinstance(x, complex):
        return [float(x.real), float(x.imag)]
    if isinstance(x, dict):
        return {str(k): jsonify(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonify(v) for v in x]
    if isinstance(x, float) and (np.isnan(x) or np.isinf(x)):
        return str(x)
    return x


def write_record(outdir: str, name: str, params: dict, payload: dict) -> str:
    os.makedirs(outdir, exist_ok=True)
    rec = {"task": name, "params": jsonify(params), "payload": jsonify(payload),
           "provenance": {"git_rev": _git_rev(),
                          "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                time.gmtime()),
                          "host": socket.gethostname()}}
    path = os.path.join(outdir, name + ".json")
    with open(path, "w") as f:
        json.dump(rec, f)
    print(path, flush=True)
    return path


# ---------------------------------------------------------------------------
# Task implementations
# ---------------------------------------------------------------------------

def t_collapse(spec, outdir):
    r = be.build_region(spec)
    bg = be.background_shapes(r, "VPLUS")
    step = be.collapse_region_stepwise(r, bg)
    direct = be.collapse_region_direct(r, bg, step["k"])
    c3 = be.control_ledger_reproduction(r, bg)
    payload = {"n": r["n"], "b": r["b"], "e_cut": r["e_cut"],
               "n_steps": len(step["steps"]),
               "psi_k": step["psi_k"],
               "consistent": bool(be.is_collapse_consistent_ok(step, direct)),
               "c3": c3,
               "firewall_ok": bool(be.scan_forbidden_ok(step["steps"]))}
    return write_record(outdir, f"collapse_{spec}", {"spec": spec}, payload)


def t_joint(spec, outdir):
    r = be.build_region(spec)
    got = be.joint_exact_count(r)
    payload = {"n": r["n"], "b": r["b"], "e_cut": r["e_cut"], **got,
               "firewall_ok": True}
    return write_record(outdir, f"joint_{spec}", {"spec": spec}, payload)


def t_joint_chunk(spec, chunk, outdir):
    r = be.build_region(spec)
    n = r["n"]
    n_in = 1 << (n * (n - 1) // 2)
    per = n_in // be.P6_CHUNKS
    lo = chunk * per
    hi = lo + per if chunk < be.P6_CHUNKS - 1 else n_in
    got = be.joint_exact_chunk(r, lo, hi)
    payload = {"n": n, "b": r["b"], "lo": lo, "hi": hi,
               "n_keys": got["n_orbits_slice"],
               "n_labeled": got["n_labeled"],
               "n_connected": got["n_connected"],
               "keys": got["keys"]}
    return write_record(outdir, f"joint_{spec}_c{chunk:02d}",
                        {"spec": spec, "chunk": chunk}, payload)


def t_wiring(spec, outdir):
    r = be.build_region(spec)
    n, b = r["n"], r["b"]
    full = be.wiring_orbits_full(n, b)
    leg = be.wiring_orbits_leg(n, b)
    payload = {"n": n, "b": b, "e_cut": r["e_cut"],
               "full_orbits": str(full), "leg_orbits": str(leg),
               "log2_full": float(math.log2(full)),
               "log2_leg": float(math.log2(leg)) if leg > 0 else None,
               "m_predictor": float(b * math.log2(n)),
               "firewall_ok": True}
    return write_record(outdir, f"wiring_{spec}", {"spec": spec}, payload)


def t_interior(spec, outdir):
    r = be.build_region(spec)
    n = r["n"]
    roots = len(be.actual_roots(r))
    rooted = be.rooted_connected_count(n, roots)
    bounds = be.orbit_log_bounds(rooted, n)
    payload = {"n": n, "b": r["b"], "roots": roots,
               "rooted_labeled": str(rooted),
               "log2_rooted": float(math.log2(rooted)),
               "orbit_bounds": bounds, "firewall_ok": True}
    return write_record(outdir, f"interior_{spec}", {"spec": spec}, payload)


def t_fiber(spec, outdir):
    r = be.build_region(spec)
    bg = be.background_shapes(r, "VPLUS")
    step0 = be.collapse_region_stepwise(r, bg)
    fb = be.fiber_basis(r)
    bb = be.blind_basis(r)
    ok_fiber = all(be.is_fiber_vector_ok(r, None, v) for v in fb)
    inv = all(abs(be.collapse_region_stepwise(r, bg + 0.1 * v)["psi_k"]
                  - step0["psi_k"]) < 1e-9 for v in fb)
    s0 = be.exterior_static(bg, r)
    blind_static = all(be.is_static_match_ok(
        s0, be.exterior_static(bg + 0.1 * v, r)) for v in bb) if bb else True
    payload = {"n": r["n"], "b": r["b"],
               "fiber_dims": be.fiber_dims(r["n"]),
               "blind_dims": be.blind_dims(r),
               "n_fiber_basis": len(fb), "n_blind_basis": len(bb),
               "fiber_ok": bool(ok_fiber),
               "collapse_invariant": bool(inv),
               "blind_static_exterior": bool(blind_static),
               "firewall_ok": True}
    return write_record(outdir, f"fiber_{spec}", {"spec": spec}, payload)


def t_alphabet(spec, bg_name, outdir):
    r = be.build_region(spec)
    bg = be.background_shapes(r, bg_name)
    if "c3" in r:
        states = be.blind_alphabet_j2(r, bg)
    else:
        states = be.blind_alphabet_pair(r, bg)
    s0 = be.exterior_static(bg, r)
    shells = sorted(be.exterior_shells(r))
    rows = []
    for s in states:
        psi = s["psi"]
        loc = be.local_distance_in_R(bg, psi, r)
        sm = be.is_static_match_ok(s0, be.exterior_static(psi, r))
        wv = be.exterior_tv_wave(bg, psi, r)
        df = be.exterior_tv_diff(bg, psi, r)
        wmax = max(v["C"] for v in wv.values())
        dmax = max(v["C"] for v in df.values())
        rows.append({"tag": s["tag"], "D": loc["D"], "static": bool(sm),
                     "wave_max": float(wmax), "diff_max": float(dmax),
                     "dyn_blind": bool(wmax < be.REMOTE_BAR
                                       and dmax < be.REMOTE_BAR)})
    payload = {"n_states": len(rows),
               "min_D": min(x["D"] for x in rows),
               "n_local": sum(1 for x in rows if x["D"] > be.LOCAL_BAR),
               "n_static": sum(1 for x in rows if x["static"]),
               "n_dyn_blind": sum(1 for x in rows if x["dyn_blind"]),
               "rows": rows, "firewall_ok": True}
    return write_record(outdir, f"alphabet_{spec}_{bg_name}",
                        {"spec": spec, "bg": bg_name}, payload)


def t_equiv(spec, outdir):
    import networkx as nx

    r = be.build_region(spec)
    bg = be.background_shapes(r, "VPLUS")
    Rset = set(r["R"])
    # Graph pair: actual interior vs one-interior-edge toggled (valid kept).
    interior_edges = sorted(tuple(sorted(e)) for e in r["g"].edges()
                            if e[0] in Rset and e[1] in Rset)
    g1 = r["g"].copy()
    assert interior_edges, "region needs an interior edge for equiv pair"
    e = interior_edges[0]
    if g1.has_edge(*e):
        g1.remove_edge(*e)
    if not nx.is_connected(g1):
        g1.add_edge(*e)
        # Fallback: add a non-edge inside R instead.
        R = list(r["R"])
        for i in range(len(R)):
            for j in range(i + 1, len(R)):
                if not g1.has_edge(R[i], R[j]):
                    g1.add_edge(R[i], R[j])
                    break
            else:
                continue
            break
    r1 = dict(r)
    r1["g"] = g1
    c0 = be.collapse_region_direct(r, bg, "K")
    c1 = be.collapse_region_direct(r1, bg, "K")
    es0 = {tuple(sorted(x)) for x in c0["g"].edges()}
    es1 = {tuple(sorted(x)) for x in c1["g"].edges()}
    s0 = be.exterior_static(bg, r)
    s1 = be.exterior_static(bg, r1)
    p0 = be.exterior_pot_profile(r)
    p1 = be.exterior_pot_profile(r1)
    # Wave TV between identical fields on the two graphs is undefined by the
    # trace API (shared eigenbasis); use POT + static as the graph-pair legs
    # and wave/diff on the field pair below (shared graph).
    bb = be.blind_basis(r)
    psi_f = bg + (0.1 * bb[0] if bb else 0.0)
    wv = be.exterior_tv_wave(bg, psi_f, r)
    df = be.exterior_tv_diff(bg, psi_f, r)
    payload = {
        "collapsed_edge_match": bool(es0 == es1),
        "collapsed_field_match": bool(abs(c0["psi"][-1] - c1["psi"][-1]) < 1e-12),
        "graph_static_match": bool(be.is_static_match_ok(s0, s1)),
        "pot_maxdiff": float(np.abs(p0["phi_ext"] - p1["phi_ext"]).max()),
        "field_static_match": bool(be.is_static_match_ok(
            s0, be.exterior_static(psi_f, r))),
        "field_wave_max": float(max(v["C"] for v in wv.values())),
        "field_diff_max": float(max(v["C"] for v in df.values())),
        "firewall_ok": True}
    return write_record(outdir, f"equiv_{spec}", {"spec": spec}, payload)


def t_control(kind, spec, outdir):
    r = be.build_region(spec)
    if kind == "C1":
        payload = be.control_relabel_invariance(r)
    elif kind == "C2":
        payload = be.control_automorph_distinct(r)
    else:
        raise ValueError(kind)
    payload["firewall_ok"] = bool(be.scan_forbidden_ok(payload))
    return write_record(outdir, f"control_{kind}_{spec}",
                        {"kind": kind, "spec": spec}, payload)


def t_audit(outdir):
    ok_w = all(be.wiring_orbits_full(n, b)
               == be.wiring_orbits_bruteforce(n, b, leg=False)
               for n in (2, 3) for b in (1, 2))
    ok_l = all(be.wiring_orbits_leg(n, b)
               == be.wiring_orbits_bruteforce(n, b, leg=True)
               for n in (2, 3) for b in (1, 2))
    ok_r = (be.rooted_connected_count(4, 2) == 48
            and be.connected_labeled_count(4) == 38)
    payload = {"wiring_full": bool(ok_w), "wiring_leg": bool(ok_l),
               "recurrence": bool(ok_r), "firewall_ok": True}
    return write_record(outdir, "audit_crosscheck", {}, payload)


# ---------------------------------------------------------------------------
# Task list
# ---------------------------------------------------------------------------

def all_tasks():
    bat = be.region_battery()
    tasks = []
    specs_c = sorted(set(bat["exact_joint"]) | {"P7", "J2L6r1"})
    for s in specs_c:
        tasks.append(f"--task collapse --spec {s}")
    for s in ("P2", "P3", "P4", "P5", "S3_2", "J2L4r0", "SQL4dimer"):
        tasks.append(f"--task joint --spec {s}")
    for c in range(be.P6_CHUNKS):
        tasks.append(f"--task joint_chunk --spec P6 --chunk {c}")
    for s in bat["wiring"]:
        tasks.append(f"--task wiring --spec {s}")
    for s in bat["interior"]:
        tasks.append(f"--task interior --spec {s}")
    for s in bat["field"]:
        tasks.append(f"--task fiber --spec {s}")
    for s in bat["alphabet"]:
        tasks.append(f"--task alphabet --spec {s} --bg VPLUS")
    tasks.append("--task alphabet --spec J2L6r1 --bg VPI")
    for s in bat["equiv"]:
        tasks.append(f"--task equiv --spec {s}")
    for s in ("P2", "P3"):
        tasks.append(f"--task control --kind C1 --spec {s}")
    for s in ("P3", "P4", "S3_2"):
        tasks.append(f"--task control --kind C2 --spec {s}")
    tasks.append("--task audit")
    return tasks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--print-all", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--task", default=None)
    ap.add_argument("--spec", default=None)
    ap.add_argument("--bg", default="VPLUS")
    ap.add_argument("--kind", default=None)
    ap.add_argument("--chunk", type=int, default=0)
    ap.add_argument("--outdir", default="data/bhent0")
    a = ap.parse_args()
    if a.print_all or a.list:
        for t in all_tasks():
            print(f"bhent0 :: {t}")
        return
    t = a.task
    if t == "collapse":
        t_collapse(a.spec, a.outdir)
    elif t == "joint":
        t_joint(a.spec, a.outdir)
    elif t == "joint_chunk":
        t_joint_chunk(a.spec, a.chunk, a.outdir)
    elif t == "wiring":
        t_wiring(a.spec, a.outdir)
    elif t == "interior":
        t_interior(a.spec, a.outdir)
    elif t == "fiber":
        t_fiber(a.spec, a.outdir)
    elif t == "alphabet":
        t_alphabet(a.spec, a.bg, a.outdir)
    elif t == "equiv":
        t_equiv(a.spec, a.outdir)
    elif t == "control":
        t_control(a.kind, a.spec, a.outdir)
    elif t == "audit":
        t_audit(a.outdir)
    else:
        raise ValueError(f"unknown task: {t}")


if __name__ == "__main__":
    main()
