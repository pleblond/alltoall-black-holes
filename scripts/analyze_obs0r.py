"""OBS-0R verdict machine (frozen gates per OBS0R-PREREG).

Reads banked OBS-0 files from BANKED (read-only) + new OBS-0R files from
OUTDIR, applies validate -> C4 -> C3 -> C0 -> C1 -> wave-verdict -> DIM ->
METRIC -> UNIVERSAL, writes verdict JSON. Exits 0 after writing (verdicts
are data). G/D/W battery analysis reuses analyze_obs0 (frozen logic).

Historical firewall: the record retains OBS0-DISCORDANT at L<=42 (C6)
regardless of outcome; obs0.py is byte-identical (hash-pinned in tests).
"""
import argparse
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))
from bh_graph import obs0, obs0r  # noqa: E402
from bh_graph.formation import j2_torus_coords  # noqa: E402
import analyze_obs0  # noqa: E402

# Frozen OBS0R-PREREG verdict parameters.
W_GAP_INTERVAL = (0.0, 0.3595)  # gap = 1632.46/N max-resid band, floored
W_DIM_BAR = 0.15  # original OBS-0 DIM bar (CONFIRM threshold)
W_GAP64 = 0.1697  # banked L64 gap (REFUTE threshold)
C0_DH_BAND = (1.70, 2.05)
C0_DS_BAND = (1.85, 2.20)
C0_DW_BAND = (1.70, 2.45)  # Amendment-3 widened band
DIM_BAR = 0.15
FLOOR_CAP = 0.40
FLOOR_NONINF = 0.05
SANITY_CAP = 0.45
IQR_BAR = 0.10
THREE_REGIME_MIN = 4  # >= 4/6 pairs interior-maximum
P_PAIRS = ("GP", "DP", "WP")
POT_LS = (28, 42, 64, 128)
C1_POT_CELLS = [(N, s) for N in (800, 1568, 3528, 8192) for s in (0, 1, 2)]


def load(d, name):
    with open(os.path.join(d, name)) as f:
        return json.load(f)


def pot_recs(outdir, tag, n=16):
    return [load(outdir, f"pot_{tag}_o{i}.json") for i in range(n)]


def origin_recs(d, tag, n=16):
    return [load(d, f"origin_{tag}_o{i}.json") for i in range(n)]


def analyze_tag_P(pots, origins, v_banked, n_train=8):
    """P-pair battery for one tag: train maps, test deltas, P-bins, IQR."""
    per_origin = []
    for prec, orec in zip(pots, origins):
        rows = []
        for node, t in prec["targets"].items():
            tau = orec["taus"].get(node, {})
            rows.append((t["R"], t["phi"], tau.get("tD"), tau.get("tW")))
        per_origin.append(rows)
    train = [r for o in per_origin[:n_train] for r in o]
    test = [(oi, o) for oi, o in enumerate(per_origin[n_train:],
                                           start=n_train)]
    calGP = obs0r.fit_yukawa([r[0] for r in train], [r[1] for r in train])
    mono = bool(calGP["ok"]) and obs0r.yukawa_monotone_ok(calGP)
    calDP = obs0r.fit_dp_pair_map([(r[2], r[1]) for r in train])
    calWP = obs0r.fit_wp_pair_map(
        [(v_banked * r[3] if r[3] is not None else None, r[1]) for r in train])
    cals = {"GP": calGP, "DP": calDP, "WP": calWP}
    med, iqr, miss = {}, {}, {}
    for pair in P_PAIRS:
        dl, bl, per_oi = [], [], {oi: [] for oi, _ in test}
        nmiss = 0
        for oi, rows in test:
            for R, phi, tD, tW in rows:
                b = obs0r.p_bin_of(R)
                if pair == "GP":
                    rhat = obs0r.invert_yukawa(phi, calGP) if mono else None
                    d = obs0.delta_stat(rhat, R)
                elif pair == "DP":
                    rp = obs0r.invert_dphi(phi, calDP)
                    sq = math.sqrt(tD) if tD else None
                    d = obs0.delta_stat(sq, rp)
                else:
                    rw = v_banked * tW if tW is not None else None
                    rp = obs0r.invert_wphi(phi, calWP)
                    d = obs0.delta_stat(rw, rp)
                if d is None or not np.isfinite(d) or b is None:
                    nmiss += 1
                    continue
                dl.append(d)
                bl.append(b)
                per_oi[oi].append((d, b))
        prof = {bb: float(np.median([d for d, q in zip(dl, bl) if q == bb]))
                if any(q == bb for q in bl) else float("nan") for bb in (0, 1, 2)}
        med[pair] = {str(k): prof[k] for k in (0, 1, 2)}
        med[pair]["n"] = len(dl)
        vals = []
        for oi, _ in test:
            vb2 = [d for d, q in per_oi[oi] if q == 2]
            if vb2:
                vals.append(float(np.median(vb2)))
        iqr[pair] = float(np.subtract(*np.percentile(vals, [75, 25]))) \
            if len(vals) >= 4 else float("nan")
        tot = sum(len(o) for _, o in test)
        miss[pair] = float(nmiss / tot) if tot else 1.0
    return {"cals": cals, "mono": mono, "medians": med, "iqr": iqr,
            "missing": miss}


def epsilon_GDW(outdir_or_banked, tag, v_banked, n_train=8):
    """Test-set epsilon(r) width-4 profiles for GW/GD/WD ({pair: {lo: med}})."""
    info = load(outdir_or_banked, f"info_{tag}.json")
    D = info["D"]
    recs = origin_recs(outdir_or_banked, tag)
    per_origin = []
    for rec in recs:
        rows = []
        for node, R in rec["targets"].items():
            t = rec["taus"][node]
            rows.append((t["R"], t["tD"], t["tW"], D))
        per_origin.append(rows)
    train = [r for o in per_origin[:n_train] for r in o]
    test = [(oi, o) for oi, o in enumerate(per_origin[n_train:],
                                           start=n_train)]
    Rtr = np.array([r[0] for r in train])
    tDtr = np.array([r[1] if r[1] is not None else np.nan for r in train])
    tWtr = np.array([r[2] if r[2] is not None else np.nan for r in train])
    RWtr = v_banked * tWtr
    cals = {"GW": obs0.fit_affine(RWtr[np.isfinite(RWtr)], Rtr[np.isfinite(RWtr)]),
            "GD": obs0.fit_powerlaw(Rtr[np.isfinite(tDtr)], tDtr[np.isfinite(tDtr)]),
            "WD": obs0.fit_powerlaw(RWtr[np.isfinite(RWtr) & np.isfinite(tDtr)],
                                    tDtr[np.isfinite(RWtr) & np.isfinite(tDtr)])}
    out = {}
    for pair in ("GW", "GD", "WD"):
        rows = analyze_obs0.pair_deltas(test, cals[pair], pair, v_banked)
        dl = [d for d, _, _ in rows]
        # Rebuild the R lookup with the same skip-rules pair_deltas uses.
        Rall = []
        for _, o in test:
            for (R, tD, tW, _) in o:
                if pair == "GW" and tW is None:
                    continue
                if pair == "GD" and tD is None:
                    continue
                if pair == "WD" and (tW is None or tD is None):
                    continue
                Rall.append(R)
        assert len(Rall) == len(dl), (tag, pair, len(Rall), len(dl))
        out[pair] = obs0r.epsilon_profile(dl, Rall, float(D) / 2.0)
    return out


def epsilon_P(pots, origins, v_banked, cals, mono, n_train=8):
    """Test-set epsilon P-bin profiles for GP/DP/WP ({pair: {b: med}})."""
    per_origin = []
    for prec, orec in zip(pots, origins):
        rows = []
        for node, t in prec["targets"].items():
            tau = orec["taus"].get(node, {})
            rows.append((t["R"], t["phi"], tau.get("tD"), tau.get("tW")))
        per_origin.append(rows)
    test = [o for o in per_origin[n_train:]]
    out = {}
    for pair in P_PAIRS:
        dl, Rl = [], []
        for rows in test:
            for R, phi, tD, tW in rows:
                if pair == "GP":
                    rhat = obs0r.invert_yukawa(phi, cals["GP"]) if mono else None
                    d = obs0.delta_stat(rhat, R)
                elif pair == "DP":
                    sq = math.sqrt(tD) if tD else None
                    d = obs0.delta_stat(sq, obs0r.invert_dphi(phi, cals["DP"]))
                else:
                    rw = v_banked * tW if tW is not None else None
                    d = obs0.delta_stat(rw, obs0r.invert_wphi(phi, cals["WP"]))
                if d is not None and np.isfinite(d):
                    dl.append(d)
                    Rl.append(R)
        out[pair] = obs0r.epsilon_profile_p(dl, Rl)
    return out


def sheet_L128(outdir, tag, L):
    """OBS-0R-H sheet analysis at L128 from matched extras + taus."""
    c3 = j2_torus_coords(L)
    recs = origin_recs(outdir, tag)
    uv = {r: {"tD": {"same": [], "cross": []}, "tW": {"same": [], "cross": []}}
          for r in (1, 2, 3)}
    ir = {"tD": {"same": [], "cross": []}, "tW": {"same": [], "cross": []}}
    for rec in recs:
        for node, slot in rec["sheet_extra"].items():
            t = rec["taus"][node]
            R, s = slot["R"], slot["slot"]
            if R in (1, 2, 3):
                uv[R]["tD"][s].append(t["tD"])
                uv[R]["tW"][s].append(t["tW"])
            if 8 <= R <= 12:
                ir["tD"][s].append(t["tD"])
                ir["tW"][s].append(t["tW"])
    out = {"uv": {}, "ir": {}}
    for r in (1, 2, 3):
        out["uv"][str(r)] = {
            k: obs0.sheet_contrast(uv[r][k]["same"], uv[r][k]["cross"])
            for k in ("tD", "tW")}
    out["ir"] = {k: obs0.sheet_contrast(ir[k]["same"], ir[k]["cross"])
                 for k in ("tD", "tW")}
    out["tD_uv_sens"] = bool(any(out["uv"][str(r)]["tD"] is not None
                                 and out["uv"][str(r)]["tD"] > 0.10
                                 for r in (1, 2, 3)))
    out["blind"] = {k: out["ir"][k] is not None and out["ir"][k] < 0.05
                    for k in ("tD", "tW")}
    out["pass"] = bool(out["tD_uv_sens"] and all(out["blind"].values()))
    return out


def sheet_POT(pots, L):
    """POT sheet contrasts on phi (descriptive; J2 only)."""
    c3 = j2_torus_coords(L)
    uv = {r: {"same": [], "cross": []} for r in (1, 2, 3)}
    meso = {"same": [], "cross": []}
    for prec in pots:
        b0 = int(c3[prec["origin"]][2])
        for node, t in prec["sheet_phi"].items():
            s = "same" if int(c3[int(node)][2]) == b0 else "cross"
            if t["R"] in (1, 2, 3):
                uv[t["R"]][s].append(t["phi"])
            if t["R"] in obs0r.P_SHEET_MESO:
                meso[s].append(t["phi"])
    out = {"uv": {str(r): obs0.sheet_contrast(uv[r]["same"], uv[r]["cross"])
                  for r in (1, 2, 3)}}
    out["meso_pooled"] = obs0.sheet_contrast(meso["same"], meso["cross"])
    return out


def mean(xs):
    return analyze_obs0.mean(xs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--banked", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--stage", choices=["c0", "full"], default="full")
    args = ap.parse_args()
    banked, outdir = args.banked, args.outdir
    verdict = {"prereg_commit": args.commit, "gates": {}, "stage": args.stage,
               "historical": "OBS0-DISCORDANT at L<=42 (preserved per C6)"}

    # Validate + C4 + C3.
    val = {}
    for tag in ("j2-L64", "sq-L64"):
        try:
            val[tag] = load(outdir, f"validation_{tag}.json")
        except FileNotFoundError:
            val[tag] = {"pass": False, "missing": True}
    verdict["validate"] = {t: bool(v.get("pass")) for t, v in val.items()}
    c4 = load(outdir, "c4.json")
    verdict["c4"] = c4
    c3 = load(outdir, "c3.json")
    verdict["c3"] = c3

    # C0-L128 G/D/W + POT.
    sq128 = analyze_obs0.analyze_tag(outdir, "sq-L128", obs0.V_BANKED["sq"])
    sq64 = analyze_obs0.analyze_tag(banked, "sq-L64", obs0.V_BANKED["sq"])
    sqP = {}
    for L in POT_LS:
        sqP[L] = analyze_tag_P(
            pot_recs(outdir, f"sq-L{L}"),
            origin_recs(outdir if L == 128 else banked, f"sq-L{L}"),
            obs0.V_BANKED["sq"])
    dH = mean(sq128["dims"]["dH"])
    r2ok = all(r is not None and r > 0.99 for r in sq128["dims"]["dH_r2"])
    ds = mean(sq128["dims"]["ds"])
    dW = mean(sq128["dims"]["dW"])
    floors = {p: sq128["medians"][p]["2"] for p in ("GW", "GD", "WD")}
    floors.update({p: sqP[128]["medians"][p]["2"] for p in P_PAIRS})
    rise = bool(dH > mean(sq64["dims"]["dH"]))
    c0 = bool(C0_DH_BAND[0] <= dH <= C0_DH_BAND[1] and r2ok
              and C0_DS_BAND[0] <= ds <= C0_DS_BAND[1]
              and C0_DW_BAND[0] <= dW <= C0_DW_BAND[1]
              and all(np.isfinite(v) and v <= SANITY_CAP
                      for v in floors.values()) and rise)
    verdict["C0_L128"] = {"pass": c0, "dH": dH, "ds": ds, "dW": dW,
                          "rise": rise, "floors": floors}
    c0pot = bool(all(sqP[L]["mono"]
                     and np.isfinite(sqP[L]["medians"][p]["2"])
                     for L in POT_LS for p in P_PAIRS))
    verdict["C0_POT"] = {"valid": c0pot,
                         "mono": {str(L): sqP[L]["mono"] for L in POT_LS}}

    # C1: POT cells (GP-only: expanders have no tau runs by design) +
    # N=8192 dims extension.
    c1pot = {}
    for N, s in C1_POT_CELLS:
        tag = f"exp-N{N}-s{s}"
        pots = pot_recs(outdir, tag)
        per_origin = [[(t["R"], t["phi"]) for t in prec["targets"].values()]
                      for prec in pots]
        train = [r for o in per_origin[:8] for r in o]
        test = [o for o in per_origin[8:]]
        cal = obs0r.fit_yukawa([r[0] for r in train], [r[1] for r in train])
        mono = bool(cal["ok"]) and obs0r.yukawa_monotone_ok(cal)
        dl, bl = [], []
        for rows in test:
            for R, phi in rows:
                b = obs0r.p_bin_of(R)
                rhat = obs0r.invert_yukawa(phi, cal) if mono else None
                d = obs0.delta_stat(rhat, R)
                if d is not None and np.isfinite(d) and b is not None:
                    dl.append(d)
                    bl.append(b)
        b2 = [d for d, q in zip(dl, bl) if q == 2]
        b2undef = len(b2) == 0
        rej = bool((not mono) or b2undef)
        c1pot[tag] = {"reject": rej, "mono": mono, "bin2undef": b2undef,
                      "n_bin2": len(b2)}
    nrej = sum(1 for v in c1pot.values() if v["reject"])
    verdict["C1_POT"] = {"pass": bool(nrej >= 7), "nreject": nrej,
                         "cells": c1pot}
    # C1 dims extension at N=8192 (drift joins banked {800,1568,3528}).
    rec8192 = [load(outdir, f"dims_exp-N8192-s{s}.json") for s in (0, 1, 2)]
    g8192 = [analyze_obs0.gate_c1(r) for r in rec8192]
    h_ok = bool(sum(1 for g in g8192 if g["h_clause"]) >= 2)
    ds8192 = float(np.mean([g["ds_mean"] for g in g8192]))
    ds_banked = []
    for N in (800, 1568, 3528):
        ds_banked.append(float(np.mean([
            analyze_obs0.gate_c1(
                load(banked, f"dims_exp-N{N}-s{s}.json"))["ds_mean"]
            for s in (0, 1, 2)])))
    drift = float(max(ds_banked + [ds8192]) - min(ds_banked + [ds8192]))
    c1ext = bool(h_ok and drift > 0.5)
    verdict["C1_EXT"] = {"pass": c1ext, "h_ok": h_ok, "ds8192": ds8192,
                         "drift4": drift}

    # Missing-data accounting (G/D/W L128 + P all cells).
    miss = [sq128["missing"][k] for k in ("tD", "tW")]
    miss += [sqP[L]["missing"][p] for L in POT_LS for p in P_PAIRS]
    miss_max = float(np.nanmax(miss))
    verdict["missing_max_c0"] = miss_max

    j2_open = bool(all(verdict["validate"].values()) and c4["pass"]
                   and c3["pass"] and c0 and c0pot
                   and verdict["C1_POT"]["pass"] and c1ext
                   and miss_max <= 0.25)
    verdict["gates"]["J2_open"] = j2_open
    if args.stage == "c0":
        verdict["ladder"] = "OBS0R-STAGED-C0"
        with open(os.path.join(outdir, "verdict_c0.json"), "w") as f:
            json.dump(verdict, f, indent=1)
        print("=== OBS-0R C0 STAGE ===")
        print(f"validate={verdict['validate']} C4={c4['pass']} "
              f"C3={c3['pass']} C0={c0} C0POT={c0pot} "
              f"C1POT={verdict['C1_POT']['pass']} C1EXT={c1ext}")
        print(f"sq-L128: dH={dH:.4f} ds={ds:.4f} dW={dW:.4f} floors={floors}")
        print(f"J2_open={j2_open}")
        return

    # ---- FULL: J2-L128 wave adjudication + battery ----
    j128 = analyze_obs0.analyze_tag(outdir, "j2-L128", obs0.V_BANKED["j2"])
    jP = {}
    for L in POT_LS:
        jP[L] = analyze_tag_P(
            pot_recs(outdir, f"j2-L{L}"),
            origin_recs(outdir if L == 128 else banked, f"j2-L{L}"),
            obs0.V_BANKED["j2"])
    for L in POT_LS:
        miss += [jP[L]["missing"][p] for p in P_PAIRS]
    miss += [j128["missing"][k] for k in ("tD", "tW")]
    miss_max = float(np.nanmax(miss))
    verdict["gates"]["missing_flag"] = bool(miss_max >= 0.10)
    verdict["gates"]["missing_stop"] = bool(miss_max > 0.25)
    verdict["missing_max"] = miss_max

    # Wave verdict.
    gap128 = abs(mean(j128["dims"]["dW"]) - dW)
    verdict["wave"] = {"gap128": gap128,
                       "j2_dW": mean(j128["dims"]["dW"]), "c0_dW": dW,
                       "interval": list(W_GAP_INTERVAL)}
    if gap128 <= W_DIM_BAR and W_GAP_INTERVAL[0] <= gap128 <= W_GAP_INTERVAL[1]:
        wv = "W-FINITE-SIZE-CONFIRMED"
    elif gap128 < W_GAP64:
        wv = "W-AMBIGUOUS"
    else:
        wv = "W-REFUTED"
    verdict["wave"]["verdict"] = wv

    # DIM128 (H, s, W -- no d_P by prereg design).
    gaps = {k: abs(mean(j128["dims"][k]) - mean(sq128["dims"][k]))
            for k in ("dH", "ds", "dW")}
    dim128 = bool(all(np.isfinite(v) and v <= DIM_BAR for v in gaps.values()))
    verdict["DIM128"] = {"gaps": gaps, "pass": dim128}

    # P-branch status (incompatibility is PHYSICS only if C3+C0 validate;
    # otherwise the apparatus is broken and P is void).
    p_void = bool(not (c3["pass"] and c0pot))
    p_incompat = bool(not p_void and not jP[64]["mono"] and not jP[128]["mono"])
    verdict["P_branch"] = {"void": p_void, "incompatible": p_incompat,
                           "mono": {str(L): jP[L]["mono"] for L in POT_LS}}

    # METRIC: DIM128 + six pairs @128 + sanity @64.
    pairs = {}
    for p in ("GW", "GD", "WD"):
        j = j128["medians"][p]["2"]
        c = sq128["medians"][p]["2"]
        pairs[p] = bool(np.isfinite(j) and np.isfinite(c)
                        and j <= c + FLOOR_NONINF and j <= FLOOR_CAP)
    for p in P_PAIRS:
        j = jP[128]["medians"][p]["2"]
        c = sqP[128]["medians"][p]["2"]
        pairs[p] = bool(np.isfinite(j) and np.isfinite(c)
                        and j <= c + FLOOR_NONINF and j <= FLOOR_CAP
                        and not p_void)
    j64 = analyze_obs0.analyze_tag(banked, "j2-L64", obs0.V_BANKED["j2"])
    san = all(j64["medians"][p]["2"] <= SANITY_CAP for p in ("GW", "GD", "WD"))
    san = bool(san and all(jP[64]["medians"][p]["2"] <= SANITY_CAP
                           for p in P_PAIRS))
    metric = bool(dim128 and all(pairs.values()) and san and not p_void)
    verdict["pairs128"] = pairs
    verdict["sanity64"] = san
    verdict["gates"]["METRIC"] = metric

    # Epsilon profiles + three-regime (L128 J2).
    eps = epsilon_GDW(outdir, "j2-L128", obs0.V_BANKED["j2"])
    epsP = epsilon_P(pot_recs(outdir, "j2-L128"),
                     origin_recs(outdir, "j2-L128"), obs0.V_BANKED["j2"],
                     jP[128]["cals"], jP[128]["mono"])
    tri = {}
    for p in ("GW", "GD", "WD"):
        tri[p] = obs0r.interior_maximum([eps[p][k] for k in sorted(eps[p])])
    for p in P_PAIRS:
        tri[p] = obs0r.interior_maximum([epsP[p][b] for b in (0, 1, 2)])
    verdict["epsilon128"] = {"GDW": eps, "P": epsP}
    verdict["three_regime"] = {"pairs": tri,
                               "n": sum(1 for v in tri.values() if v),
                               "pass": bool(sum(1 for v in tri.values() if v)
                                            >= THREE_REGIME_MIN)}
    # Epsilon scaling filed (L64/L42/L28 J2, GDW + P).
    for L in (28, 42, 64):
        e = epsilon_GDW(banked, f"j2-L{L}", obs0.V_BANKED["j2"])
        eP = epsilon_P(pot_recs(outdir, f"j2-L{L}"),
                       origin_recs(banked, f"j2-L{L}"), obs0.V_BANKED["j2"],
                       jP[L]["cals"], jP[L]["mono"])
        verdict[f"epsilon_L{L}"] = {"GDW": e, "P": eP}

    # Origin IQR (ii').
    iqr_ok = all(np.isfinite(j128["iqr"][p]) and j128["iqr"][p] <= IQR_BAR
                 for p in ("GW", "GD", "WD"))
    iqr_ok = bool(iqr_ok and all(np.isfinite(jP[128]["iqr"][p])
                                 and jP[128]["iqr"][p] <= IQR_BAR
                                 for p in P_PAIRS))
    verdict["iqr128"] = {"pass": iqr_ok,
                         "GDW": j128["iqr"], "P": jP[128]["iqr"]}

    # Sheet (iii').
    sh128 = sheet_L128(outdir, "j2-L128", 128)
    verdict["sheet128"] = sh128
    verdict["sheetPOT"] = {str(L): sheet_POT(pot_recs(outdir, f"j2-L{L}"), L)
                           for L in POT_LS}

    # Scaling (v').
    gstab = {p: abs(j128["medians"][p]["2"] - j64["medians"][p]["2"])
             for p in ("GW", "GD")}
    wd_down = bool(j128["medians"]["WD"]["2"] <= j64["medians"]["WD"]["2"])
    pstab = {p: abs(jP[128]["medians"][p]["2"] - jP[64]["medians"][p]["2"])
             for p in P_PAIRS}
    vpass = bool(all(np.isfinite(v) and v <= FLOOR_NONINF
                     for v in list(gstab.values()))
                 and wd_down
                 and all(np.isfinite(v) and v <= FLOOR_NONINF
                         for v in pstab.values()))
    verdict["scaling"] = {"pass": vpass, "gstab": gstab, "wd_down": wd_down,
                          "pstab": pstab}

    universal = bool(metric and verdict["three_regime"]["pass"] and iqr_ok
                     and sh128["pass"] and vpass and c0
                     and verdict["C1_POT"]["pass"] and c1ext)
    verdict["gates"]["UNIVERSAL"] = universal

    # Ladder.
    if not j2_open:
        ladder = "OBS0R-BLOCKED"
    elif p_incompat:
        ladder = "OBS0R-DISCORDANT"
    elif wv != "W-FINITE-SIZE-CONFIRMED":
        ladder = "OBS0R-DISCORDANT"
    elif universal:
        ladder = "OBS0R-UNIVERSAL"
    elif metric:
        ladder = "OBS0R-METRIC"
    elif dim128:
        ladder = "OBS0R-DIMENSION"
    else:
        ladder = "OBS0R-DISCORDANT"
    verdict["ladder"] = ladder
    with open(os.path.join(outdir, "verdict.json"), "w") as f:
        json.dump(verdict, f, indent=1)

    print("=== OBS-0R VERDICT ===")
    print(f"wave={wv} gap128={gap128:.4f} DIM128={dim128} gaps={gaps}")
    print(f"P_branch void={p_void} incompat={p_incompat} pairs={pairs}")
    print(f"METRIC={metric} three={verdict['three_regime']} iqr={iqr_ok} "
          f"sheet={sh128['pass']} scaling={vpass} UNIVERSAL={universal}")
    print(f"LADDER: {ladder}")


if __name__ == "__main__":
    main()
