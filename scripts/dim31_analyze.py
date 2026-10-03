"""DIM-3-1 reveal/analysis/verdict stages (DIM31-PREREG sections 2-9).

Phases:
  controls  unblind control workup -> freeze record (bars, transfer
            tables, tolerances). No J3 data touched (J3 cells refused).
  j3        hash-gated J3 reveal -> cross-channel verdict. Refuses to
            run unless the blind artifact sha256 matches the seal.

Reveal-side: hidden joins (radius, coords, layers) live ONLY here and
run strictly after blind artifacts exist. Blind claims use frozen bars
from the freeze record (passed to dim31_blind.py --bars or applied
here for audit).
"""

import argparse
import hashlib
import json
import math
import os
import sys

import networkx as nx
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

import dim31_campaign as CMP
from dim31_campaign import tag_cells, tag_graph, tag_L

from bh_graph import dim3_reveal as R3
from bh_graph import dim31, obs0
from bh_graph import obs1_reveal as R2

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

CONTROL_CELLS = tuple(c for c in range(len(CMP.CELLS)) if c not in CMP.J3_CELLS)
J3_CELLS = CMP.J3_CELLS
LADDER_LEVELS = ("W_hi_th", "W", "W_lo_th")
CHANNELS = ("W", "D", "C")
GROUPS = {"ring": (0, 1), "sq": (2, 3), "j2": (4, 5), "cb": (6, 7, 8),
          "ex": (9, 10, 11), "bcb": (12,)}

DIM_TRUE = {"ring": 1.0, "sq": 2.0, "j2": 2.0, "cb": 3.0}


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
    return o


def spread_of(vals) -> float:
    """Max absolute deviation from the median (nan-safe)."""
    v = np.asarray([x for x in vals if x is not None and np.isfinite(x)],
                   dtype=float)
    if v.size == 0:
        return float("nan")
    return float(np.max(np.abs(v - np.median(v))))


# ---------------------------------------------------------------------------
# Reveal-side hidden joins (controls + post-seal J3 only).
# ---------------------------------------------------------------------------

_radius_cache: dict = {}


def hidden_radius(tag: str, u: int, v: int) -> float:
    """Hidden quotient radius between nodes (Manhattan min-image; BFS ex)."""
    fam = tag.split("-")[0]
    if fam == "ex":
        key = ("ex", tag)
        if key not in _radius_cache:
            g = tag_graph(tag)
            _radius_cache[key] = (g, {})
        g, cache = _radius_cache[key]
        if u not in cache:
            cache[u] = nx.single_source_shortest_path_length(g, u)
        return float(cache[u][v])
    L = tag_L(tag)
    key = ("cells", tag)
    if key not in _radius_cache:
        _radius_cache[key] = tag_cells(tag, tag_graph(tag))
    cells = _radius_cache[key]
    a, b = cells[u], cells[v]
    if fam == "rg":
        n = L
        d = abs(int(a[0]) - int(b[0])) % n
        return float(min(d, n - d))
    s = 0
    for x, y in zip(a, b):
        d = abs(int(x) - int(y))
        s += min(d, L - d)
    return float(s)


def intrinsic_D(tag: str) -> int:
    key = ("D", tag)
    if key not in _radius_cache:
        g = tag_graph(tag)
        _radius_cache[key] = obs0.intrinsic_diameter(g, 0)
    return _radius_cache[key]


def hidden_coords(tag: str) -> dict:
    key = ("cells", tag)
    if key not in _radius_cache:
        _radius_cache[key] = tag_cells(tag, tag_graph(tag))
    return _radius_cache[key]


# ---------------------------------------------------------------------------
# Per-cell-set workup (shared by both phases).
# ---------------------------------------------------------------------------

def pair_lists(meas: dict):
    """Sorted pair keys + station index pairs (deterministic order)."""
    keys = sorted(meas["pairs"])
    idx = []
    for k in keys:
        a_s, b_s = k.split("|")
        idx.append((int(a_s[1:]), int(b_s[1:])))
    return keys, idx


def gamma_fits(tag: str, meas: dict, seal: dict) -> dict:
    """Frozen-protocol gamma per level (hidden-radius join, reveal-side)."""
    D = intrinsic_D(tag)
    smap = seal["stations"]
    nodes = [int(smap[f"S{i}"]) for i in range(int(meas["n"]))]
    keys, idx = pair_lists(meas)
    radii = [hidden_radius(tag, nodes[a], nodes[b]) for a, b in idx]
    out = {}
    for level in LADDER_LEVELS:
        masses = [meas["pairs"][k].get(level) for k in keys]
        out[level] = dim31.arrival_gamma(radii, masses, D)
    masses_d = [meas["pairs"][k].get("D") for k in keys]
    out["Dch"] = dim31.arrival_gamma(radii, masses_d, D,
                                     dt=obs0.DT_DIFF)
    return out


def chart_claim(tag: str, Dmat: np.ndarray, seal: dict, d: int) -> dict:
    """Local-chart eps at dimension d (reveal-side, frozen bar)."""
    smap = seal["stations"]
    nodes = [int(smap[f"S{i}"]) for i in range(Dmat.shape[0])]
    coords = hidden_coords(tag)
    L = tag_L(tag)
    fam = tag.split("-")[0]
    if fam in ("j3", "cb", "bcb"):
        return R3.local_chart_report3(np.asarray(Dmat, dtype=float),
                                     coords, nodes, L, k=8, d=d)
    if fam in ("j2", "sq"):
        if d != 2:
            return {"med": float("nan"), "n": 0, "pass": False,
                    "note": "2D chart apparatus supports d=2 only"}
        return R2.local_chart_report(np.asarray(Dmat, dtype=float),
                                    coords, nodes, float(L), k=8)
    return {"med": float("nan"), "n": 0, "pass": False,
            "note": "no chart apparatus for family"}


def static_workup(potdir: str, tag: str) -> dict:
    """Static dimension per gap-delta leg (frozen section-4 protocol)."""
    p = os.path.join(potdir, f"dim31_pot1_{tag}.json")
    if not os.path.exists(p):
        return {"error": "missing pot1 record"}
    with open(p) as f:
        rec = json.load(f)
    D = intrinsic_D(tag)
    rmax = min(10, math.floor(D / 2.0) - 1)
    out = {}
    for delta, leg in rec["legs"].items():
        prof = leg["profile_med"]
        rs, ph = [], []
        for r in range(2, rmax + 1):
            v = prof.get(str(r))
            if v is not None and v >= dim31.STATIC_PHI_FLOOR:
                rs.append(float(r))
                ph.append(float(v))
        dim = dim31.static_dimension(rs, ph)
        # P-range compression check (mechanism validation).
        pr_meas, pr_pred = float("nan"), float("nan")
        if len(ph) >= 2 and dim["ok"]:
            P = -np.log(np.maximum(ph, 1e-300))
            pr_meas = float(P[-1] - P[0])
            pr_pred = float((rs[-1] - rs[0]) / dim["xi"]
                            + dim["alpha"] * math.log(rs[-1] / rs[0]))
        out[delta] = {"dim": dim, "pr_meas": pr_meas, "pr_pred": pr_pred,
                      "omega": leg["omega"], "resid": leg["resid"]}
    return out


# ---------------------------------------------------------------------------
# Controls phase -> freeze record.
# ---------------------------------------------------------------------------

def freeze_bars(ladders: dict) -> dict:
    """Mechanical bar selection per prereg section 3 (1.3x margins).

    ladders[channel][group] = list of S_d over control sets.
    Returns {"bars": ..., "debt": [...]}.
    """
    bars, debt = {}, []
    for ch in CHANNELS:
        S = {g: ladders[ch][g] for g in ("ring", "sq", "j2", "cb", "ex")}
        trial = {}
        # bar_1: max ring S1 < bar <= min others S1.
        hi1 = max(s[1] for s in S["ring"])
        lo1 = min(min(s[1] for s in S[g]) for g in ("sq", "j2", "cb", "ex"))
        if hi1 < lo1 and lo1 / hi1 >= dim31.BAR_MARGIN:
            trial[1] = math.sqrt(hi1 * lo1)
        else:
            debt.append(f"{ch}: bar_1 unfreezable "
                        f"(ring max {hi1:.4f} vs others min {lo1:.4f})")
            continue
        # bar_2: max sq/j2 S2 < bar <= min cb/ex S2; sq/j2 S1 >= bar_1.
        if any(s[1] < trial[1] for g in ("sq", "j2") for s in S[g]):
            debt.append(f"{ch}: sq/j2 S1 undercuts bar_1")
            continue
        hi2 = max(max(s[2] for s in S[g]) for g in ("sq", "j2"))
        lo2 = min(min(s[2] for s in S[g]) for g in ("cb", "ex"))
        if hi2 < lo2 and lo2 / hi2 >= dim31.BAR_MARGIN:
            trial[2] = math.sqrt(hi2 * lo2)
        else:
            debt.append(f"{ch}: bar_2 unfreezable "
                        f"(2D max {hi2:.4f} vs 3D/ex min {lo2:.4f})")
            continue
        # bar_3: max cb S3 < bar <= min ex S3; cb S2 >= bar_2.
        if any(s[2] < trial[2] for s in S["cb"]):
            debt.append(f"{ch}: cb S2 undercuts bar_2")
            continue
        hi3 = max(s[3] for s in S["cb"])
        lo3 = min(s[3] for s in S["ex"])
        if hi3 < lo3 and lo3 / hi3 >= dim31.BAR_MARGIN:
            trial[3] = math.sqrt(hi3 * lo3)
        else:
            debt.append(f"{ch}: bar_3 unfreezable "
                        f"(cb max {hi3:.4f} vs ex min {lo3:.4f})")
            continue
        bars[ch] = {str(d): trial[d] for d in (1, 2, 3)}
    return {"bars": bars, "debt": debt}


def cmd_controls(args):
    with open(args.blind) as f:
        blind = json.load(f)
    measdir, potdir = args.measdir, args.potdir
    ladders = {ch: {g: [] for g in GROUPS} for ch in CHANNELS}
    alphas = {ch: {g: [] for g in GROUPS} for ch in CHANNELS}
    gammas = {}  # (cell,set,level) -> fit
    static = {}
    cell_of = {c: CMP.CELLS[c] for c in CONTROL_CELLS}
    group_of = {}
    for g, cells in GROUPS.items():
        for c in cells:
            if c in CONTROL_CELLS:
                group_of[c] = g
    for c in CONTROL_CELLS:
        tag = cell_of[c]
        gname = group_of[c]
        for s in range(CMP.N_SETS):
            with open(os.path.join(
                    measdir, f"dim31_meas_cell{c}_s{s}.json")) as f:
                meas = json.load(f)
            with open(os.path.join(
                    measdir, f"dim31_seal_cell{c}_s{s}.json")) as f:
                seal = json.load(f)
            assert seal["tag"] == tag
            workup = blind["cells"][str(c)]["sets"][str(s)]
            for ch in CHANNELS:
                S = workup["ladder"][ch]["S"]
                ladders[ch][gname].append({1: S["1"], 2: S["2"], 3: S["3"]})
                vol = workup["probes"][ch]["vol"]
                if vol.get("ok"):
                    alphas[ch][gname].append(vol["d"])
            gf = gamma_fits(tag, meas, seal)
            for level, fit in gf.items():
                gammas[(c, s, level)] = fit
        static[tag] = static_workup(potdir, tag)
    freeze = {"bars": {}, "debt": [], "gamma": {}, "tolerances": {},
              "gates": {}}
    frz = freeze_bars(ladders)
    freeze["bars"] = frz["bars"]
    freeze["debt"].extend(frz["debt"])
    # Headline channel C bars are REQUIRED; W/D legs filed if present.
    if "C" not in freeze["bars"]:
        freeze["debt"].append("headline C bars unfreezable -> "
                              "ESTIMATOR-DEBT path")
    # Gamma transfer tables (cubic donor).
    cb_cells = {c: CMP.CELLS[c] for c in GROUPS["cb"]}
    for level in list(LADDER_LEVELS) + ["Dch"]:
        by_L, allv = {}, []
        for c, tag in cb_cells.items():
            L = tag_L(tag)
            vals = [gammas[(c, s, level)]["gamma"] for s in range(CMP.N_SETS)
                    if gammas[(c, s, level)]["ok"]]
            if vals:
                by_L[L] = float(np.median(vals))
                allv.extend(vals)
        pooled = float(np.median(allv)) if allv else float("nan")
        freeze["gamma"][level] = {"by_L": {str(k): v for k, v in by_L.items()},
                                  "pooled": pooled,
                                  "n": len(allv)}
    # T1 size stability + T2 ladder stability on cubic.
    w_vals = [freeze["gamma"][lv]["pooled"] for lv in LADDER_LEVELS]
    freeze["gates"]["T1_spread"] = spread_of(
        [v for lv in LADDER_LEVELS for v in
         freeze["gamma"][lv]["by_L"].values()])
    freeze["gates"]["T2_ladder_spread"] = spread_of(w_vals)
    # Tolerances (mechanical rules, frozen pre-J3 here).
    cb_d = []
    for c in GROUPS["cb"]:
        for s in range(CMP.N_SETS):
            a = blind["cells"][str(c)]["sets"][str(s)]["probes"]["C"]["vol"]
            g = gammas[(c, s, "W")]
            d = dim31.arrival_dimension(a["d"] if a.get("ok") else float("nan"),
                                        bool(a.get("ok")), g)
            if d["ok"]:
                cb_d.append(d["d"])
    sp = spread_of(cb_d)
    freeze["tolerances"]["tol_identity"] = max(0.15, 2 * sp) \
        if np.isfinite(sp) else 0.15
    freeze["tolerances"]["tol_drift"] = max(0.2, 2 * sp) \
        if np.isfinite(sp) else 0.2
    freeze["tolerances"]["tol_regress"] = max(0.25, 2 * sp) \
        if np.isfinite(sp) else 0.25
    freeze["tolerances"]["tol_agree"] = 0.2
    freeze["tolerances"]["tol_gamma_ladder"] = 0.1
    with open(args.out, "w") as f:
        json.dump(jsonable(freeze), f, indent=2, sort_keys=True)
    print(f"freeze record: {args.out} debt={freeze['debt']}")
    print(json.dumps(jsonable({k: freeze[k] for k in ("tolerances", "gates")}),
                     indent=2))


# ---------------------------------------------------------------------------
# J3 phase (hash-gated).
# ---------------------------------------------------------------------------

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def cmd_j3(args):
    with open(args.seal) as f:
        seal = json.load(f)
    digest = sha256_file(args.blind)
    if digest != seal["blind_sha256"]:
        raise SystemExit(f"seal mismatch: blind {digest} != "
                         f"seal {seal['blind_sha256']}")
    with open(args.freeze) as f:
        freeze = json.load(f)
    with open(args.blind) as f:
        blind = json.load(f)
    verdict = {"seal": seal["blind_sha256"], "cells": {}, "verdict": None,
               "debt": list(freeze.get("debt", []))}
    # Full workup per J3 cell (transfer + direct + static + chart).
    for c in J3_CELLS:
        tag = CMP.CELLS[c]
        L = tag_L(tag)
        cell = {"tag": tag, "sets": {}}
        for s in range(CMP.N_SETS):
            with open(os.path.join(
                    args.measdir, f"dim31_meas_cell{c}_s{s}.json")) as f:
                meas = json.load(f)
            with open(os.path.join(
                    args.measdir, f"dim31_seal_cell{c}_s{s}.json")) as f:
                seal_c = json.load(f)
            workup = blind["cells"][str(c)]["sets"][str(s)]
            gf = gamma_fits(tag, meas, seal_c)
            # Transfer leg (blind headline).
            tW = dim31.transfer_lookup(
                {"by_L": {int(k): v for k, v in
                           freeze["gamma"]["W"]["by_L"].items()},
                 "pooled": freeze["gamma"]["W"]["pooled"]}, L)
            aC = workup["probes"]["C"]["vol"]
            d_tr = dim31.arrival_dimension(
                aC["d"] if aC.get("ok") else float("nan"),
                bool(aC.get("ok")),
                {"gamma": tW["value"], "ok": tW["ok"]})
            # Direct leg (reveal-side validation).
            d_di = dim31.arrival_dimension(
                aC["d"] if aC.get("ok") else float("nan"),
                bool(aC.get("ok")), gf["W"])
            lad = workup["ladder"]["C"]
            Dc = np.asarray(workup["probes"]["C"]["D"], dtype=float)
            bars = {int(k): v for k, v in freeze["bars"]["C"].items()}
            audit = dim31.local_dstar(Dc, bars)
            claim = {"dstar": audit["dstar"], "pass": audit["pass"],
                     "blind_agrees": bool(audit["dstar"] == lad.get("dstar")
                                          and audit["pass"] == lad.get(
                                              "dstar_pass"))}
            cell["sets"][str(s)] = {
                "alpha_C": aC["d"] if aC.get("ok") else None,
                "gamma_transfer": tW, "d_arr_transfer": d_tr,
                "gamma_direct": {k: v for k, v in gf["W"].items()
                                 if k in ("gamma", "r2", "n", "ok")},
                "d_arr_direct": d_di,
                "dstar": claim, "ladder_S": lad["S"]}
        cell["static"] = static_workup(args.potdir, tag)
        verdict["cells"][str(c)] = cell
    verdict["verdict"] = "DIM31-UNDECIDED (full gates in next commit)"
    with open(args.out, "w") as f:
        json.dump(jsonable(verdict), f, indent=2, sort_keys=True)
    print(f"verdict scaffold: {args.out}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("controls")
    p.add_argument("--measdir", required=True)
    p.add_argument("--potdir", required=True)
    p.add_argument("--blind", required=True)
    p.add_argument("--out", required=True)
    p = sub.add_parser("j3")
    p.add_argument("--measdir", required=True)
    p.add_argument("--potdir", required=True)
    p.add_argument("--blind", required=True)
    p.add_argument("--freeze", required=True)
    p.add_argument("--seal", required=True)
    p.add_argument("--out", required=True)
    args = ap.parse_args()
    if args.cmd == "controls":
        cmd_controls(args)
    elif args.cmd == "j3":
        cmd_j3(args)


if __name__ == "__main__":
    main()
