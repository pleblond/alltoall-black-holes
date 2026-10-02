#!/usr/bin/env python3
"""ZERO-0 campaign runner: one task -> one JSON row (docs/zero0-prereg.md).

Task kinds: generic | packet | collide | background | winding | sector
          | persistent | twomode

Every task is deterministic given its CLI args. Heavy kinds run on beast
via task files + xargs -P. Schemas are documented in --help and pinned
by tests/test_zero0_campaign.py (fast subset only).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time

import networkx as nx
import numpy as np

from bh_graph import zero
from bh_graph.ballistic import (
    evolve_fixed,
    gaussian_packet,
    hamiltonian,
    node_order,
    ring_coords,
    torus_grid_coords,
)
from bh_graph.conservation import field_random
from bh_graph.formation import j2_torus_coords, j2_torus_graph
from bh_graph.graphs import build_short_rewired_grid, build_torus_grid

MODAL_N_CAP = 200
ANATOMY_EVENT_CAP = 25
STORE_EVENT_CAP = 200


# ---------------------------------------------------------------- substrates

def build_substrate(tag: str, size: int) -> dict:
    """Frozen ZERO-0V battery (read-only builders)."""
    tag, size = str(tag), int(size)
    if tag == "j2":
        g = j2_torus_graph(size)
        order = node_order(g)
        c3 = j2_torus_coords(size)
        coords = {v: (float(x), float(y)) for v, (x, y, _) in c3.items()}
        return {"tag": tag, "size": size, "g": g, "order": order,
                "coords": coords, "c3": c3, "periods": (size, size),
                "bipart": {v: (x + y) & 1 for v, (x, y, _) in c3.items()},
                "sheet": np.array([c3[v][2] for v in order], dtype=float),
                "N": len(order)}
    if tag == "storus":
        g = build_torus_grid(size)
        order = node_order(g)
        return {"tag": tag, "size": size, "g": g, "order": order,
                "coords": torus_grid_coords(size), "c3": None,
                "periods": (size, size),
                "bipart": {v: ((v // size) + (v % size)) & 1 for v in order},
                "sheet": None, "N": len(order)}
    if tag == "ring":
        g = nx.cycle_graph(size)
        order = node_order(g)
        return {"tag": tag, "size": size, "g": g, "order": order,
                "coords": ring_coords(size), "c3": None,
                "periods": (size,),
                "bipart": {v: v & 1 for v in order},
                "sheet": None, "N": len(order)}
    if tag == "j2quot":
        from bh_graph.vac0 import quotient_j2

        g = quotient_j2(size)
        order = node_order(g)
        return {"tag": tag, "size": size, "g": g, "order": order,
                "coords": torus_grid_coords(size), "c3": None,
                "periods": (size, size),
                "bipart": {v: ((v // size) + (v % size)) & 1 for v in order},
                "sheet": None, "N": len(order)}
    if tag == "rewire":
        g = build_short_rewired_grid(n_side=size, n_swaps=80, span=2, seed=0)
        g = nx.convert_node_labels_to_integers(g)
        order = node_order(g)
        return {"tag": tag, "size": size, "g": g, "order": order,
                "coords": None, "c3": None, "periods": None,
                "bipart": None, "sheet": None, "N": len(order)}
    raise ValueError(f"unknown substrate: {tag}")


def substrate_h(sub: dict):
    return hamiltonian(sub["g"], 1.0, sub["order"])


# ------------------------------------------------------------------- states

def build_family_state(family: str, sub: dict, seed: int, h_dense=None,
                       n_modes: int = 3) -> dict:
    prep = zero.prepare_family(family, sub["N"], seed, h=h_dense,
                               coords=sub["coords"], order=sub["order"],
                               n_modes=n_modes)
    if not prep["exclusion_ok"]:
        raise RuntimeError(f"exclusion failed: {family} seed {seed}")
    return prep


def modal_for(h, n: int):
    if n > MODAL_N_CAP:
        return None
    hd = np.asarray(h.toarray() if hasattr(h, "toarray") else h, dtype=float)
    return {"dense": hd, "sys": zero.modal_system(hd)}


# -------------------------------------------------------------------- trace

def run_trace(psi0: np.ndarray, h, dt: float, horizon: float) -> dict:
    n_steps = int(round(horizon / dt))
    rep = evolve_fixed(np.asarray(psi0, dtype=np.complex128), h, dt, n_steps)
    ts = np.arange(n_steps + 1) * dt
    return {"psi": rep["psi"], "ts": ts, "norms": rep["norms"],
            "norm_ok": zero.is_norm_conserved_ok(rep["norms"])}


# ------------------------------------------------------------------ anatomy

def event_anatomy(psi0, h, sub: dict, ev: dict, adj) -> dict:
    """ZERO-0O/R/S/T enrichment of one Level-2+ event (fine window)."""
    from bh_graph.ballistic import evolve_fixed as _ev

    u, t_star = int(ev["node"]), float(ev["t_star"])
    half, fdt = 0.5, 0.002
    lo = max(0.0, t_star - half)
    hi = t_star + half
    n = max(8, int(round((hi - lo) / fdt)))
    base = _ev(psi0, h, lo / 2.0, 2)["psi"][2] if lo > 0 else psi0
    rows = _ev(base, h, (hi - lo) / n, n)["psi"]
    fts = lo + (hi - lo) / n * np.arange(n + 1)
    k_star = int(np.argmin(np.abs(fts - t_star)))
    tr_u = rows[:, u]
    ph = zero.one_sided_phases(tr_u, k_star)
    bj = zero.incident_BJ_trace(rows, sub["g"], sub["order"], sub["order"][u])
    pats = []
    for j in range(bj["B"].shape[1]):
        kb = max(0, k_star - 5)
        ka = min(len(fts) - 1, k_star + 5)
        pats.append({"B": zero.sign_pattern(bj["B"][kb, j], bj["B"][ka, j]),
                     "J": zero.sign_pattern(bj["J"][kb, j], bj["J"][ka, j])})
    psi_s = _ev(psi0, h, t_star / 2.0, 2)["psi"][2] if t_star > 0 else psi0
    d1 = zero.psi_dot(psi_s, adj)
    d2 = zero.psi_ddot(psi_s, adj)
    clas = zero.classify_zero(psi_s[u], d1[u])
    quad = zero.is_quadratic_touch_ok(psi_s[u], d1[u], d2[u])
    en = zero.is_energy_finite_ok(psi_s, sub["g"], sub["order"])
    return {"node": u, "t_star": t_star, "label": ev.get("label"),
            "theta_minus": ph["theta_minus"], "theta_plus": ph["theta_plus"],
            "phase_jump": ph["jump"], "class": clas,
            "quadratic_touch": quad, "energy_ok": en,
            "BJ_patterns": pats}


# -------------------------------------------------------------------- kinds

def kind_generic(a) -> dict:
    sub = build_substrate(a.substrate, a.size)
    h = substrate_h(sub)
    mo = modal_for(h, sub["N"])
    prep = build_family_state(a.family, sub, a.seed,
                              h_dense=mo["dense"] if mo else None,
                              n_modes=a.n_modes)
    tr = run_trace(prep["psi"], h, a.dt, a.horizon)
    scan = zero.trace_zero_scan(prep["psi"], h, tr["ts"], tr["psi"],
                                modal=mo["sys"] if mo else None)
    return _finish(a, sub, prep["psi"], h, tr, scan, {
        "family": a.family, "seed_used": prep["seed_used"],
        "modal": mo is not None})


def kind_packet(a) -> dict:
    sub = build_substrate(a.substrate, a.size)
    if sub["coords"] is None:
        raise ValueError("packet needs a coordinate substrate")
    h = substrate_h(sub)
    mo = modal_for(h, sub["N"])
    k = tuple(float(x) for x in a.k.split(","))
    r0 = tuple(float(x) for x in a.r0.split(","))
    psi0 = gaussian_packet(sub["coords"], sub["order"], r0, k, a.sigma,
                           periods=sub["periods"])
    tr = run_trace(psi0, h, a.dt, a.horizon)
    scan = zero.trace_zero_scan(psi0, h, tr["ts"], tr["psi"],
                                modal=mo["sys"] if mo else None)
    return _finish(a, sub, psi0, h, tr, scan, {
        "sigma": a.sigma, "k": list(k), "r0": list(r0),
        "modal": mo is not None})


def _collision_pair(sub, geom: str, sigma: float):
    L = sub["size"]
    cx = {"headon": [((L / 4, L / 2), (math.pi / 2, 0.0)),
                      ((3 * L / 4, L / 2), (-math.pi / 2, 0.0))],
          "co": [((L / 4, L / 2), (math.pi / 2, 0.0)),
                 ((L / 4 + 2 * sigma, L / 2), (math.pi / 2, 0.0))],
          "ortho": [((L / 4, L / 2), (math.pi / 2, 0.0)),
                    ((L / 2, L / 4), (0.0, math.pi / 2))],
          "oblique": [((L / 4, L / 2), (math.pi / 2, 0.0)),
                      ((L / 2, 3 * L / 4), (math.pi / 4, -math.pi / 4))],
          "near": [((L / 4, L / 2 - 3 * sigma), (math.pi / 2, 0.0)),
                   ((L / 4, L / 2 + 3 * sigma), (math.pi / 2, 0.0))]}[geom]
    return cx


def kind_collide(a) -> dict:
    if a.substrate not in ("j2", "storus", "j2quot"):
        raise ValueError("collide needs a 2D substrate")
    sub = build_substrate(a.substrate, a.size)
    h = substrate_h(sub)
    mo = modal_for(h, sub["N"])
    (r1, k1), (r2, k2) = _collision_pair(sub, a.geom, a.sigma)
    p1 = gaussian_packet(sub["coords"], sub["order"], r1, k1, a.sigma,
                         periods=sub["periods"])
    p2 = gaussian_packet(sub["coords"], sub["order"], r2, k2, a.sigma,
                         periods=sub["periods"]) * np.exp(1j * a.dphi)
    if a.amp == "mismatch":
        p2 = 0.5 * p2
    psi0 = p1 + p2
    psi0 = psi0 / np.linalg.norm(psi0)
    tr = run_trace(psi0, h, a.dt, a.horizon)
    scan = zero.trace_zero_scan(psi0, h, tr["ts"], tr["psi"],
                                modal=mo["sys"] if mo else None)
    # Overlap anatomy: separately evolved parts at each event time.
    t1 = run_trace(p1 / np.linalg.norm(p1), h, a.dt, a.horizon)["psi"]
    t2 = run_trace(p2 / np.linalg.norm(p2), h, a.dt, a.horizon)["psi"]
    for ev in scan["events"][:STORE_EVENT_CAP]:
        kk = int(round(ev["t_star"] / a.dt))
        kk = min(max(kk, 0), len(tr["ts"]) - 1)
        u = ev["node"]
        m1, m2 = abs(t1[kk, u]), abs(t2[kk, u])
        ev["overlap_minmax"] = float(min(m1, m2) / max(m1, m2, 1e-300))
        ev["null_law"] = zero.two_component_null(t1[kk, u], t2[kk, u])
    return _finish(a, sub, psi0, h, tr, scan, {
        "geom": a.geom, "dphi": a.dphi, "amp": a.amp,
        "sigma": a.sigma, "modal": mo is not None})


def kind_background(a) -> dict:
    sub = build_substrate(a.substrate, a.size)
    h = substrate_h(sub)
    mo = modal_for(h, sub["N"])
    n = sub["N"]
    bipart = np.array([sub["bipart"][v] for v in sub["order"]]) \
        if sub["bipart"] else None
    bg = zero.background_shape(a.bg, n, bipart=bipart, sheet=sub["sheet"])
    eta = field_random(n, a.seed) * a.eta_scale
    if a.bg == "Z0":
        psi0 = eta.copy()
    else:
        psi0 = zero.assemble_state(a.a, bg, eta, a.protocol)
    tr = run_trace(psi0, h, a.dt, a.horizon)
    scan = zero.trace_zero_scan(psi0, h, tr["ts"], tr["psi"],
                                modal=mo["sys"] if mo else None)
    bound = {"spectral": None, "trace": None}
    if a.bg != "Z0" and a.protocol == "absolute":
        bound["spectral"] = zero.is_spectrally_protected_ok(a.a, bg, eta)
        tb = run_trace(a.a * bg, h, a.dt, a.horizon)["psi"]
        te = run_trace(eta, h, a.dt, a.horizon)["psi"]
        bound["trace"] = zero.is_trace_bound_ok(tb, te)
    return _finish(a, sub, psi0, h, tr, scan, {
        "bg": a.bg, "a": a.a, "protocol": a.protocol,
        "eta_scale": a.eta_scale, "seed": a.seed, "bound": bound,
        "modal": mo is not None})


def test_cycles(sub: dict) -> list:
    """Frozen ZERO-0P cycle sets (verified edges, deterministic)."""
    g, L = sub["g"], sub["size"]
    out = []
    if sub["tag"] == "ring":
        return [list(range(L))]
    if sub["tag"] in ("storus", "j2quot"):
        for x0, y0 in ((1, 1), (L // 3, L // 2)):
            cyc = [x0 * L + y0, ((x0 + 1) % L) * L + y0,
                   ((x0 + 1) % L) * L + (y0 + 1) % L, x0 * L + (y0 + 1) % L]
            if all(g.has_edge(cyc[i], cyc[(i + 1) % 4]) for i in range(4)):
                out.append(cyc)
        return out or [sorted(nx.cycle_basis(g, 0), key=len)[0]]
    if sub["tag"] == "j2":
        def _id(x, y, b):
            return (x * L + y) * 2 + b
        x0, y0 = 1, 1
        sheet0 = [_id(x0, y0, 0), _id(x0 + 1, y0, 0),
                  _id(x0 + 1, y0 + 1, 0), _id(x0, y0 + 1, 0)]
        sheet1 = [_id(x0, y0, 1), _id(x0, y0 + 1, 1),
                  _id(x0 + 1, y0 + 1, 1), _id(x0 + 1, y0, 1)]
        bilayer = [_id(x0, y0, 0), _id(x0 + 1, y0, 0), _id(x0 + 2, y0, 1),
                   _id(x0 + 2, y0 + 1, 1), _id(x0 + 1, y0 + 1, 1),
                   _id(x0, y0 + 1, 0)]
        for cyc in (sheet0, sheet1, bilayer):
            if all(g.has_edge(cyc[i], cyc[(i + 1) % len(cyc)])
                   for i in range(len(cyc))):
                idx = {v: i for i, v in enumerate(sub["order"])}
                out.append([idx[v] for v in cyc])
        return out
    return [sorted(nx.cycle_basis(g, 0), key=len)[0]]


def kind_winding(a) -> dict:
    sub = build_substrate(a.substrate, a.size)
    h = substrate_h(sub)
    mo = modal_for(h, sub["N"])
    prep = build_family_state(a.family, sub, a.seed,
                              h_dense=mo["dense"] if mo else None,
                              n_modes=a.n_modes)
    tr = run_trace(prep["psi"], h, a.dt, a.horizon)
    scan = zero.trace_zero_scan(prep["psi"], h, tr["ts"], tr["psi"],
                                modal=mo["sys"] if mo else None)
    idx = {v: i for i, v in enumerate(sub["order"])}
    cycs = test_cycles(sub)
    if sub["tag"] in ("storus", "j2quot", "ring"):
        cycs = [[idx[v] for v in c] for c in cycs]
    wind = []
    for cyc in cycs:
        wt = zero.winding_trace(tr["psi"], cyc)
        ch = zero.winding_changes(wt)
        on_support = sorted({ev["t_star"] for ev in scan["events"]
                             if ev["node"] in set(cyc)})
        wind.append({
            "len": len(cyc),
            "frac_defined": float(np.mean(wt["defined"])),
            "max_resid": float(np.nanmax(np.abs(wt["residual"][wt["defined"]]))
                               if np.any(wt["defined"]) else float("nan")),
            "n_changes": len(ch),
            "assoc": zero.associate_changes(ch, tr["ts"], on_support),
            "n_support_events": len(on_support)})
    return _finish(a, sub, prep["psi"], h, tr, scan, {
        "family": a.family, "seed_used": prep["seed_used"],
        "cycles": wind, "modal": mo is not None})


def kind_sector(a) -> dict:
    from bh_graph.conservation import j2_sheet_swap

    sub = build_substrate("j2", a.size)
    h = substrate_h(sub)
    mo = modal_for(h, sub["N"])
    pr = zero.sheet_projectors(j2_sheet_swap(a.size))
    base = field_random(sub["N"], a.seed)
    if a.prep == "plus":
        psi0 = np.asarray(pr["P_plus"]) @ base
    elif a.prep == "minus":
        psi0 = np.asarray(pr["P_minus"]) @ base
    else:
        psi0 = base
    psi0 = (psi0 / np.linalg.norm(psi0)).astype(np.complex128)
    w = zero.sector_weights(psi0, pr)
    tr = run_trace(psi0, h, a.dt, a.horizon)
    scan = zero.trace_zero_scan(psi0, h, tr["ts"], tr["psi"],
                                modal=mo["sys"] if mo else None)
    return _finish(a, sub, psi0, h, tr, scan, {
        "prep": a.prep, "seed": a.seed, "w_plus": w["w_plus"],
        "w_minus": w["w_minus"], "modal": mo is not None})


def kind_persistent(a) -> dict:
    sub = build_substrate(a.substrate, a.size)
    h = substrate_h(sub)
    hd = np.asarray(h.toarray(), dtype=float)
    cen = zero.eig_nodal_census(hd)
    nodes = sorted(cen["nodal"])
    checks = []
    for u in nodes[:8]:
        k = cen["nodal"][u][0]
        checks.append({"node": u, "k": k,
                       "ok": zero.is_nodal_persistent_ok(hd, k, u)})
    return {"task": "persistent", "substrate": a.substrate, "size": a.size,
            "N": sub["N"], "n_flat": cen["n_flat"],
            "n_nodal_nodes": len(nodes), "checks": checks}


def kind_twomode(a) -> dict:
    g = nx.complete_graph(2)
    order = node_order(g)
    h = zero.dense_hamiltonian(g, order)
    ms = zero.modal_system(h)
    psi0 = np.array([1 + 0j, 0j])
    ts = np.arange(0.0, a.horizon, a.dt)
    scan = zero.trace_zero_scan(psi0, h, ts, modal=ms)
    ana = zero.two_mode_zero_times(0.5 + 0j, 0.5 + 0j, -1.0, 1.0, a.horizon)
    ev0 = sorted(e["t_star"] for e in scan["events"] if e["node"] == 0)
    dev = max(abs(f - t) for f, t in zip(ev0, ana["times"])) if ev0 else None
    ok = bool(ev0 and len(ev0) == len(ana["times"])
              and dev is not None and dev < 1e-6)
    return {"task": "twomode", "n_events": len(scan["events"]),
            "n_analytic": len(ana["times"]), "max_dev": dev,
            "recovered": ok}


def _jsonable(x):
    if isinstance(x, complex):
        return {"re": float(x.real), "im": float(x.imag)}
    if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
        return repr(x)
    if isinstance(x, dict):
        return {k: _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, np.ndarray):
        return [_jsonable(v) for v in x.tolist()]
    if isinstance(x, (np.bool_, bool)):
        return bool(x)
    if isinstance(x, (np.integer, np.floating)):
        return float(x)
    return x


def _finish(a, sub, psi0, h, tr, scan, extra: dict) -> dict:
    adj = -h
    labels: dict[str, int] = {}
    for ev in scan["events"]:
        labels[ev.get("label", "?")] = labels.get(ev.get("label", "?"), 0) + 1
    ana = []
    if a.anatomy:
        for ev in scan["events"][:ANATOMY_EVENT_CAP]:
            ana.append(event_anatomy(psi0, h, sub, ev, adj))
    row = {"task": a.task, "substrate": sub["tag"], "size": sub["size"],
           "N": sub["N"], "dt": a.dt, "horizon": a.horizon,
           "norm_ok": bool(tr["norm_ok"]), "m_stats": scan["m_stats"],
           "n_candidates": len(scan["candidates"]),
           "n_events": len(scan["events"]), "labels": labels,
           "events": scan["events"][:STORE_EVENT_CAP],
           "events_stored": min(len(scan["events"]), STORE_EVENT_CAP),
           "anatomy": ana,
           "anatomy_overflow": max(0, len(scan["events"]) - ANATOMY_EVENT_CAP)
           if a.anatomy else None}
    row.update(extra)
    return _jsonable(row)


# ---------------------------------------------------------------------- main

def parse(argv=None):
    p = argparse.ArgumentParser(description="ZERO-0 single-task runner")
    p.add_argument("--task", required=True,
                   choices=["generic", "packet", "collide", "background",
                            "winding", "sector", "persistent", "twomode"])
    p.add_argument("--substrate", default="ring",
                   choices=["j2", "storus", "ring", "j2quot", "rewire"])
    p.add_argument("--size", type=int, default=64)
    p.add_argument("--family", default="F1",
                   choices=["F1", "F2", "F3", "F4", "F5"])
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--n-modes", type=int, default=3)
    p.add_argument("--dt", type=float, default=zero.DT_HEAD)
    p.add_argument("--horizon", type=float, default=zero.T_HEAD)
    p.add_argument("--sigma", type=float, default=4.0)
    p.add_argument("--k", default="1.5708,0.0")
    p.add_argument("--r0", default=None)
    p.add_argument("--geom", default="headon",
                   choices=["headon", "co", "ortho", "oblique", "near"])
    p.add_argument("--dphi", type=float, default=math.pi)
    p.add_argument("--amp", default="match", choices=["match", "mismatch"])
    p.add_argument("--bg", default="Z+",
                   choices=["Z0", "Z+", "ZPI", "Z-"])
    p.add_argument("--a", type=float, default=1.0)
    p.add_argument("--protocol", default="absolute",
                   choices=["absolute", "fractional"])
    p.add_argument("--eta-scale", type=float, default=1.0)
    p.add_argument("--prep", default="mixed",
                   choices=["plus", "minus", "mixed"])
    p.add_argument("--anatomy", action="store_true")
    p.add_argument("--out", required=True)
    return p.parse_args(argv)


def main(argv=None):
    t0 = time.time()
    a = parse(argv)
    if a.r0 is None:
        a.r0 = ("32.0" if a.substrate == "ring"
                else f"{a.size / 4},{a.size / 2}")
    fn = {"generic": kind_generic, "packet": kind_packet,
          "collide": kind_collide, "background": kind_background,
          "winding": kind_winding, "sector": kind_sector,
          "persistent": kind_persistent, "twomode": kind_twomode}[a.task]
    row = fn(a)
    row["cpu_s"] = time.time() - t0
    with open(a.out, "w") as f:
        json.dump(row, f)
    print(json.dumps({k: row.get(k) for k in
                      ("task", "substrate", "size", "n_events", "labels",
                       "norm_ok", "cpu_s")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
