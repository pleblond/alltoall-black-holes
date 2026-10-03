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
GROUPS = {"ring": (0, 1), "sq": (2, 3), "j2": (4, 5), "cb": (6, 7, 8, 16),
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


def chart_claim_3d(tag: str, Dmat: np.ndarray, seal: dict) -> dict:
    """Smallest d in {1, 2, 3} with chart eps <= 0.30 (reveal-side)."""
    for d in (1, 2, 3):
        rep = chart_claim(tag, Dmat, seal, d)
        if rep.get("pass"):
            return {"d": d, "pass": True, "eps": rep["med"]}
    last = chart_claim(tag, Dmat, seal, 3)
    return {"d": None, "pass": False, "eps": last.get("med")}


def chart_claim_2d(tag: str, Dmat: np.ndarray, seal: dict) -> dict:
    """2D chart leg: claim 2 iff eps2 <= 0.30 (banked apparatus)."""
    rep = chart_claim(tag, Dmat, seal, 2)
    if rep.get("pass"):
        return {"d": 2, "pass": True, "eps": rep["med"]}
    return {"d": None, "pass": False, "eps": rep.get("med")}


def spread_check(potdir: str, tag: str) -> dict:
    """Far-shell exponent windows (banked E/F bars, descriptive + gate)."""
    out = {}
    for kind in ("R", "I"):
        p = os.path.join(potdir, f"dim31_spread_{tag}_BG0_{kind}_1.json")
        if not os.path.exists(p):
            out[kind] = {"error": "missing spread record"}
            continue
        with open(p) as f:
            rec = json.load(f)
        fits = rec.get("fits", {})
        legs = {}
        for ch, window in (("psi", (0.80, 1.20)), ("rho", (1.70, 2.30)),
                            ("J", (1.70, 2.30))):
            fit = fits.get(ch, {})
            n = fit.get("n", 0) or 0
            r2 = fit.get("r2")
            a = fit.get("alpha")
            meas = n >= 4 and r2 is not None and r2 > 0.9
            ok = bool(meas and a is not None
                      and window[0] <= a <= window[1])
            legs[ch] = {"alpha": a, "r2": r2, "n": n,
                        "measurable": meas, "pass": ok}
        out[kind] = {"legs": legs,
                     "front_v": rec.get("front", {}).get("v")}
    return out


def packet_check(potdir: str, tag: str) -> dict:
    """G-a packet leg: Bloch speed within 10% + reversal (frozen)."""
    p = os.path.join(potdir, f"dim31_packet_{tag}.json")
    if not os.path.exists(p):
        return {"error": "missing packet record"}
    with open(p) as f:
        rec = json.load(f)
    vb = rec["v_bloch"]
    sp = rec["plus"]["speed"]
    ok_v = abs(sp - vb) / abs(vb) <= 0.10
    ok_r = abs(rec["cos_pm"] + 1.0) <= 0.05
    ok_n = bool(rec["plus"]["norm_ok"]) and bool(rec["minus"]["norm_ok"])
    return {"v": sp, "v_bloch": vb, "cos_pm": rec["cos_pm"],
            "pass": bool(ok_v and ok_r and ok_n)}


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


def halfsplit_claims(D: np.ndarray, bars) -> dict:
    """Descriptive 32/32 half-split d* (Amendment-1 A1; never gated)."""
    D = np.asarray(D, dtype=float)
    n = D.shape[0] // 2
    out = {}
    for name, sub in (("train", D[:n, :][:, :n]),
                      ("test", D[n:, :][:, n:])):
        cl = dim31.local_dstar(sub, bars)
        out[name] = {"dstar": cl["dstar"], "pass": cl["pass"]}
    return out


def own_darr(blind_cell_set: dict, gf: dict) -> dict:
    """d_arr pairings with own (same cell/set) gamma (controls)."""
    out = {}
    pairings = {"W": ("W", "W"), "D": ("D", "Dch"), "C": ("C", "W")}
    for ch, (a_ch, g_lv) in pairings.items():
        vol = blind_cell_set["probes"][a_ch]["vol"]
        out[ch] = dim31.arrival_dimension(
            vol["d"] if vol.get("ok") else float("nan"),
            bool(vol.get("ok")), gf[g_lv])
    out["C"]["approximate"] = True  # mixture channel, gamma_W hybrid
    return out


def cmd_controls(args):
    with open(args.blind) as f:
        blind = json.load(f)
    measdir, potdir = args.measdir, args.potdir
    ladders = {ch: {g: [] for g in GROUPS} for ch in CHANNELS}
    gammas = {}  # (cell,set,level) -> fit
    static = {}
    charts = {}  # (cell,set) -> claim
    darr = {}  # (cell,set,ch) -> d_arr record
    claims = {}  # (cell,set,ch) -> d* claim (applied after bar freeze)
    group_of = {}
    for g, cells in GROUPS.items():
        for c in cells:
            if c in CONTROL_CELLS:
                group_of[c] = g
    for c in CONTROL_CELLS:
        tag = CMP.CELLS[c]
        gname = group_of[c]
        fam = tag.split("-")[0]
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
            gf = gamma_fits(tag, meas, seal)
            for level, fit in gf.items():
                gammas[(c, s, level)] = fit
            for ch, rec in own_darr(workup, gf).items():
                darr[(c, s, ch)] = rec
            Dc = np.asarray(workup["probes"]["C"]["D"], dtype=float)
            if fam in ("j3", "cb", "bcb"):
                charts[(c, s)] = chart_claim_3d(tag, Dc, seal)
            elif fam in ("j2", "sq"):
                charts[(c, s)] = chart_claim_2d(tag, Dc, seal)
            else:
                charts[(c, s)] = {"d": None, "pass": False, "eps": None,
                                  "note": "no chart apparatus"}
        static[tag] = static_workup(potdir, tag)
    spread = {tag: spread_check(potdir, tag)
              for tag in ("cb-L20", "j2-L28")}
    packet = {"cb-L20": packet_check(potdir, "cb-L20")}
    # --- freeze bars (mechanical) ---
    freeze = {"bars": {}, "debt": [], "gamma": {}, "tolerances": {},
              "gates": {}, "dropped_legs": []}
    frz = freeze_bars(ladders)
    freeze["bars"] = frz["bars"]
    for ch in CHANNELS:
        if ch not in freeze["bars"]:
            if ch == "C":
                freeze["debt"].append(
                    "headline C d* bars unfreezable -> ESTIMATOR-DEBT")
            else:
                freeze["dropped_legs"].append(
                    f"d* {ch}: bars unfreezable (filed, never gated)")
    # Apply frozen bars -> claims (mechanical; blind matrices only).
    halfsplit = {}
    for c in CONTROL_CELLS:
        for s in range(CMP.N_SETS):
            workup = blind["cells"][str(c)]["sets"][str(s)]
            for ch in CHANNELS:
                if ch not in freeze["bars"]:
                    claims[(c, s, ch)] = {"dstar": None, "pass": False,
                                          "reason": "leg dropped"}
                    continue
                D = np.asarray(workup["probes"][ch]["D"], dtype=float)
                bars = {int(k): v
                        for k, v in freeze["bars"][ch].items()}
                cl = dim31.local_dstar(D, bars)
                claims[(c, s, ch)] = {"dstar": cl["dstar"],
                                      "pass": cl["pass"]}
                halfsplit[f"{c}/{s}/{ch}"] = halfsplit_claims(D, bars)
    # --- gamma transfer tables (cubic donor) ---
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
                                  "pooled": pooled, "n": len(allv)}
    if not np.isfinite(freeze["gamma"]["W"]["pooled"]):
        freeze["debt"].append("cubic gamma_W unmeasurable -> ESTIMATOR-DEBT")
    freeze["gates"]["T1_spread"] = spread_of(
        [v for lv in LADDER_LEVELS for v in
         freeze["gamma"][lv]["by_L"].values()])
    freeze["gates"]["T2_ladder_spread"] = spread_of(
        [freeze["gamma"][lv]["pooled"] for lv in LADDER_LEVELS])
    freeze["gates"]["T1_pass"] = bool(
        np.isfinite(freeze["gates"]["T1_spread"])
        and freeze["gates"]["T1_spread"] <= 0.15)
    freeze["gates"]["T2_pass"] = bool(
        np.isfinite(freeze["gates"]["T2_ladder_spread"])
        and freeze["gates"]["T2_ladder_spread"] <= 0.1)
    if not freeze["gates"]["T1_pass"]:
        freeze["dropped_legs"].append(
            "pooled gamma transfer invalid (T1); L-matched only; "
            "J3-L24 descriptive (no cb-L24 donor)")
    if not freeze["gates"]["T2_pass"]:
        freeze["debt"].append("gamma ladder-unstable (T2) -> transfer "
                              "invalid -> ESTIMATOR-DEBT")
    # --- tolerances (mechanical rules, frozen pre-J3 here) ---
    cb_d = [darr[(c, s, "W")]["d"] for c in GROUPS["cb"]
            for s in range(CMP.N_SETS) if darr[(c, s, "W")]["ok"]]
    sp = spread_of(cb_d)
    sp = sp if np.isfinite(sp) else 0.0
    freeze["tolerances"]["tol_identity"] = max(0.15, 2 * sp)
    freeze["tolerances"]["tol_drift"] = max(0.2, 2 * sp)
    freeze["tolerances"]["tol_regress"] = max(0.25, 2 * sp)
    freeze["tolerances"]["tol_agree"] = 0.2
    freeze["tolerances"]["tol_prange"] = 0.15
    tol_r = freeze["tolerances"]["tol_regress"]
    # --- control gates (headline failures -> debt) ---
    for gname, dim in DIM_TRUE.items():
        for c in GROUPS[gname]:
            for s in range(CMP.N_SETS):
                d = darr[(c, s, "W")]
                if not d["ok"] or abs(d["d"] - dim) > tol_r:
                    freeze["debt"].append(
                        f"d_arr W {CMP.CELLS[c]} s{s}: "
                        f"{d['d'] if d['ok'] else 'UNMEAS'} vs {dim}")
                cl = claims[(c, s, "C")]
                if not cl["pass"] or cl["dstar"] != int(dim):
                    freeze["debt"].append(
                        f"d* C {CMP.CELLS[c]} s{s}: {cl['dstar']} "
                        f"vs {int(dim)}")
                if charts[(c, s)].get("note") is None \
                        and charts[(c, s)]["d"] != int(dim):
                    freeze["debt"].append(
                        f"chart {CMP.CELLS[c]} s{s}: "
                        f"{charts[(c, s)]['d']} vs {int(dim)}")
    for tag, dim in [("rg-N256", 1.0), ("rg-N512", 1.0), ("sq-L32", 2.0),
                     ("sq-L48", 2.0), ("j2-L28", 2.0), ("j2-L42", 2.0),
                     ("cb-L12", 3.0), ("cb-L16", 3.0), ("cb-L20", 3.0)]:
        leg = static.get(tag, {}).get("0.5", {})
        dimrec = leg.get("dim", {})
        if not dimrec.get("ok") or abs(dimrec["d"] - dim) > tol_r:
            freeze["debt"].append(
                f"d_stat {tag}: "
                f"{dimrec.get('d') if dimrec.get('ok') else 'UNMEAS'} "
                f"vs {dim}")
        pr_m, pr_p = leg.get("pr_meas"), leg.get("pr_pred")
        if pr_m is None or not np.isfinite(pr_m) or not np.isfinite(pr_p) \
                or abs(pr_m - pr_p) / abs(pr_m) > 0.15:
            freeze["debt"].append(f"P-range {tag}: meas {pr_m} pred {pr_p}")
    # Expander refusal on every claiming channel.
    for c in GROUPS["ex"]:
        for s in range(CMP.N_SETS):
            if darr[(c, s, "W")]["ok"]:
                freeze["debt"].append(
                    f"expander d_arr claimed {CMP.CELLS[c]} s{s}")
            if claims[(c, s, "C")]["pass"]:
                freeze["debt"].append(
                    f"expander d* claimed {CMP.CELLS[c]} s{s}")
    for tag in ("ex-N1024-s0", "ex-N3456-s0"):
        leg = static.get(tag, {}).get("0.5", {})
        if leg.get("dim", {}).get("ok"):
            freeze["debt"].append(f"expander d_stat claimed {tag}")
    # Spreading + packet legs.
    for tag in ("cb-L20", "j2-L28"):
        legs = spread.get(tag, {}).get("R", {}).get("legs", {})
        for ch in ("psi", "rho", "J"):
            if not legs.get(ch, {}).get("pass"):
                freeze["debt"].append(f"spread {tag} R/{ch} fails")
    if not packet.get("cb-L20", {}).get("pass"):
        freeze["debt"].append("packet cb-L20 fails")
    # --- records ---
    with open(args.out, "w") as f:
        json.dump(jsonable(freeze), f, indent=2, sort_keys=True)
    workup = {
        "ladders": {ch: {g: [{str(k): v for k, v in s.items()}
                               for s in lst]
                         for g, lst in ladders[ch].items()}
                    for ch in CHANNELS},
        "darr": {f"{c}/{s}/{ch}": darr[(c, s, ch)]
                 for c in CONTROL_CELLS for s in range(CMP.N_SETS)
                 for ch in CHANNELS},
        "claims": {f"{c}/{s}/{ch}": claims[(c, s, ch)]
                   for c in CONTROL_CELLS for s in range(CMP.N_SETS)
                   for ch in CHANNELS},
        "charts": {f"{c}/{s}": charts[(c, s)]
                   for c in CONTROL_CELLS for s in range(CMP.N_SETS)},
        "static": static, "spread": spread, "packet": packet,
        "gamma_ok": {f"{c}/{s}/{lv}": gammas[(c, s, lv)]["ok"]
                     for c in CONTROL_CELLS for s in range(CMP.N_SETS)
                     for lv in list(LADDER_LEVELS) + ["Dch"]},
        "halfsplit": halfsplit,
    }
    with open(args.out + ".workup.json", "w") as f:
        json.dump(jsonable(workup), f, indent=2, sort_keys=True)
    print(f"freeze record: {args.out} debt={len(freeze['debt'])} "
          f"dropped={len(freeze['dropped_legs'])}")
    for cause in freeze["debt"][:20]:
        print(f"  DEBT: {cause}")
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


def transfer_darr(blind_cell_set: dict, freeze: dict, L: int) -> dict:
    """d_arr pairings with transfer gamma (J3 blind headline)."""
    out = {}
    specs = {"W": ("W", "W"), "D": ("D", "Dch"), "C": ("C", "W")}
    for ch, (a_ch, g_lv) in specs.items():
        tab = freeze["gamma"][g_lv]
        t = dim31.transfer_lookup(
            {"by_L": {int(k): v for k, v in tab["by_L"].items()},
             "pooled": tab["pooled"]}, L)
        vol = blind_cell_set["probes"][a_ch]["vol"]
        d = dim31.arrival_dimension(
            vol["d"] if vol.get("ok") else float("nan"),
            bool(vol.get("ok")), {"gamma": t["value"], "ok": t["ok"]})
        d["transfer"] = t
        out[ch] = d
    out["C"]["approximate"] = True
    return out


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
    with open(args.workup) as f:
        ctrl = json.load(f)
    verdict = {"seal": seal["blind_sha256"], "cells": {}, "verdict": None,
               "failures": []}
    if freeze.get("debt"):
        verdict["verdict"] = "DIM31-ESTIMATOR-DEBT"
        verdict["failures"].append("freeze debt non-empty; J3 uninterpretted")
        with open(args.out, "w") as f:
            json.dump(jsonable(verdict), f, indent=2, sort_keys=True)
        print("verdict: DIM31-ESTIMATOR-DEBT (controls failed)")
        return
    tol = freeze["tolerances"]
    # Integrity: blind control ladders must match the frozen workup.
    for key, rec in ctrl["claims"].items():
        c, s, ch = key.split("/")
        lad = blind["cells"][c]["sets"][s]["ladder"][ch]["S"]
        wlad = ctrl["ladders"][ch][_group_of(int(c))][_set_index(int(c),
                                                                  int(s))]
        for d in ("1", "2", "3"):
            if abs(lad[d] - wlad[d]) > 1e-9:
                raise SystemExit(f"integrity fail: ladder drift {key}")
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
            assert seal_c["tag"] == tag
            workup = blind["cells"][str(c)]["sets"][str(s)]
            gf = gamma_fits(tag, meas, seal_c)
            d_tr = transfer_darr(workup, freeze, L)
            d_di = own_darr(workup, gf)
            Dc = np.asarray(workup["probes"]["C"]["D"], dtype=float)
            bars = {int(k): v for k, v in freeze["bars"]["C"].items()}
            audit = dim31.local_dstar(Dc, bars)
            lad = workup["ladder"]["C"]
            claim = {"dstar": audit["dstar"], "pass": audit["pass"],
                     "blind_agrees": bool(
                         audit["dstar"] == lad.get("dstar")
                         and audit["pass"] == lad.get("dstar_pass"))}
            chart = chart_claim_3d(tag, Dc, seal_c)
            cell["sets"][str(s)] = {
                "d_arr_transfer": d_tr, "d_arr_direct": d_di,
                "gamma_direct_W": {k: gf["W"][k] for k in
                                   ("gamma", "r2", "n", "ok")},
                "dstar": claim, "chart": chart,
                "halfsplit_C": halfsplit_claims(Dc, bars)}
        cell["static"] = static_workup(args.potdir, tag)
        cell["spread"] = spread_check(args.potdir, tag)
        cell["packet"] = packet_check(args.potdir, tag)
        verdict["cells"][str(c)] = cell
    # --- headline gates (per J3 cell; L24 descriptive if T1 failed) ---
    F = verdict["failures"]
    pooled_ok = freeze["gates"].get("T1_pass", False)
    headline_cells = [13, 14] if not pooled_ok else [13, 14, 15]
    verdict["headline_cells"] = headline_cells
    for c in headline_cells:
        cell = verdict["cells"][str(c)]
        for s in range(CMP.N_SETS):
            rec = cell["sets"][str(s)]
            d = rec["d_arr_transfer"]["W"]
            if not d["ok"] or abs(d["d"] - 3.0) > tol["tol_regress"]:
                F.append(f"j3 d_arr {c}/{s}: "
                         f"{d['d'] if d['ok'] else 'UNMEAS'}")
            dd = rec["d_arr_direct"]["W"]
            if d["ok"] and dd["ok"] and \
                    abs(d["d"] - dd["d"]) > tol["tol_agree"]:
                F.append(f"j3 transfer/direct disagree {c}/{s}")
            if rec["dstar"]["dstar"] != 3 or not rec["dstar"]["pass"]:
                F.append(f"j3 d* {c}/{s}: {rec['dstar']['dstar']}")
            if rec["chart"]["d"] != 3:
                F.append(f"j3 chart {c}/{s}: {rec['chart']['d']}")
        st = cell["static"].get("0.5", {}).get("dim", {})
        if not st.get("ok") or abs(st["d"] - 3.0) > tol["tol_regress"]:
            F.append(f"j3 d_stat {c}: "
                     f"{st.get('d') if st.get('ok') else 'UNMEAS'}")
        for ch in ("psi", "rho", "J"):
            leg = cell["spread"].get("R", {}).get("legs", {}).get(ch, {})
            if leg.get("measurable") and not leg.get("pass"):
                F.append(f"j3 spread {c}/R/{ch} fails")
            if not leg.get("measurable"):
                F.append(f"j3 spread {c}/R/{ch} unmeasurable")
        if not cell["packet"].get("pass"):
            F.append(f"j3 packet {c} fails")
    # --- identity (matched L; L24 vs nearest cb-L20) + drift ---
    for c in headline_cells:
        tag = CMP.CELLS[c]
        L = tag_L(tag)
        cb_tag = f"cb-L{L}" if f"cb-L{L}" in CMP.CELLS else "cb-L20"
        cb_cell = CMP.CELLS.index(cb_tag)
        for s in range(CMP.N_SETS):
            dj = verdict["cells"][str(c)]["sets"][str(s)][
                "d_arr_transfer"]["W"]
            dc = ctrl["darr"][f"{cb_cell}/{s}/W"]
            if dj["ok"] and dc["ok"] and \
                    abs(dj["d"] - dc["d"]) > tol["tol_identity"]:
                F.append(f"identity {tag}/W s{s} vs {cb_tag}")
    drift_vals = [verdict["cells"][str(c)]["sets"][str(s)][
        "d_arr_transfer"]["W"]["d"]
        for c in headline_cells for s in range(CMP.N_SETS)
        if verdict["cells"][str(c)]["sets"][str(s)][
            "d_arr_transfer"]["W"]["ok"]]
    if spread_of(drift_vals) > tol["tol_drift"]:
        F.append("J3 size drift exceeds tolerance")
    verdict["verdict"] = "DIM31-OPERATIONAL" if not F else "DIM31-GEOMETRIC"
    with open(args.out, "w") as f:
        json.dump(jsonable(verdict), f, indent=2, sort_keys=True)
    print(f"verdict: {verdict['verdict']} failures={len(F)}")
    for cause in F[:20]:
        print(f"  FAIL: {cause}")


def _group_of(c: int) -> str:
    for g, cells in GROUPS.items():
        if c in cells:
            return g
    raise ValueError(f"cell {c} not in any group")


def _set_index(c: int, s: int) -> int:
    g = _group_of(c)
    cells = sorted(cc for cc in GROUPS[g] if cc in CONTROL_CELLS)
    return cells.index(c) * CMP.N_SETS + s


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
    p.add_argument("--workup", required=True)
    p.add_argument("--seal", required=True)
    p.add_argument("--out", required=True)
    args = ap.parse_args()
    if args.cmd == "controls":
        cmd_controls(args)
    elif args.cmd == "j3":
        cmd_j3(args)


if __name__ == "__main__":
    main()
