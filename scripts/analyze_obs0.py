"""OBS-0 verdict machine (frozen gates per OBS0-PREREG).

Reads campaign JSONs from OUTDIR, applies C5 -> C0 -> C1 -> DIM -> METRIC ->
UNIVERSAL (+ sheet/pert descriptive E2/epsilon), writes verdict JSON.
Exits 0 after writing verdict regardless of outcome (verdicts are data).
"""
import argparse
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from bh_graph import obs0  # noqa: E402
from bh_graph.formation import j2_torus_coords  # noqa: E402 Validation-only use


def load(outdir, name):
    with open(os.path.join(outdir, name)) as f:
        return json.load(f)


def tag_origins(outdir, tag, n=16):
    return [load(outdir, f"origin_{tag}_o{i}.json") for i in range(n)]


def pair_deltas(test_taus, cal, pair, v_banked):
    """Test-set (delta, tercile, origin) rows for a ruler pair."""
    rows = []
    for oi, items in test_taus:
        for R, tD, tW, D in items:
            if pair == "GW":
                if tW is None:
                    continue
                rhat = cal["a"] * (v_banked * tW) + cal["b"]
            elif pair == "GD":
                rhat = obs0.invert_powerlaw(tD, cal["A"], cal["p"]) if tD else None
            else:  # WD: compare in R_W units (pure wave-vs-diffusion;
                # R_W ~= R_G scale since v_banked ~ 1; C0-relative gates).
                if tW is None or tD is None:
                    continue
                rhat = v_banked * tW
                r_true = obs0.invert_powerlaw(tD, cal["A"], cal["p"])
                rows.append((obs0.delta_stat(rhat, r_true), obs0.tercile_of(R, D), oi))
                continue
            rows.append((obs0.delta_stat(rhat, R), obs0.tercile_of(R, D), oi))
    return rows


def analyze_tag(outdir, tag, v_banked, n_origins=16, n_train=8):
    """Full E1 + dims analysis for one tag (train/test by origin)."""
    info = load(outdir, f"info_{tag}.json")
    D = info["D"]
    recs = tag_origins(outdir, tag, n_origins)
    # Sampled-target rows per origin: (R, tD, tW, D).
    per_origin = []
    for rec in recs:
        rows = []
        for node, R in rec["targets"].items():
            t = rec["taus"][node]
            rows.append((t["R"], t["t"], t["tW"], D))
        per_origin.append(rows)
    train = [r for o in per_origin[:n_train] for r in o]
    test = [(oi, o) for oi, o in enumerate(per_origin[n_train:], start=n_train)]
    Rtr = np.array([r[0] for r in train])
    tDtr = np.array([r[1] if r[1] is not None else np.nan for r in train])
    tWtr = np.array([r[2] if r[2] is not None else np.nan for r in train])
    RWtr = v_banked * tWtr
    mGW = np.isfinite(RWtr)
    mGD = np.isfinite(tDtr)
    mWD = np.isfinite(RWtr) & np.isfinite(tDtr)
    calGW = obs0.fit_affine(RWtr[mGW], Rtr[mGW])
    calGD = obs0.fit_powerlaw(Rtr[mGD], tDtr[mGD])
    calWD = obs0.fit_powerlaw(RWtr[mWD], tDtr[mWD])
    cals = {"GW": calGW, "GD": calGD, "WD": calWD}
    med = {}
    iqr = {}
    uv_ir = {}
    for pair in ("GW", "GD", "WD"):
        rows = pair_deltas(test, cals[pair], pair, v_banked)
        dl = [d for d, _, _ in rows]
        tl = [t for _, t, _ in rows]
        tm = obs0.tercile_medians(dl, tl)
        med[pair] = {str(k): tm[k] for k in (0, 1, 2)}
        med[pair]["n"] = tm["n"]
        per_oi = []
        for oi in range(n_train, n_origins):
            vals = [d for d, t, o in rows if o == oi and t == 2
                    and d is not None and np.isfinite(d)]
            if vals:
                per_oi.append(float(np.median(vals)))
        iqr[pair] = float(np.subtract(*np.percentile(per_oi, [75, 25]))) if len(per_oi) >= 4 else float("nan")
        uv_ir[pair] = bool(tm[2] < tm[0]) if np.isfinite(tm[2]) and np.isfinite(tm[0]) else False
    # d_W per origin via the train law window.
    dW = [obs0.arrival_volume_dim({k: v["tW"] for k, v in rec["taus"].items()},
                                  calGW["a"], calGW["b"], D)["d"] for rec in recs]
    dims = {"dH": [r["hausdorff"]["d"] for r in recs],
            "dH_r2": [r["hausdorff"]["r2"] for r in recs],
            "ds": [r["ds_origin"]["d"] for r in recs],
            "dW": dW}
    miss = {}
    for nm, arr in (("tD", tDtr), ("tW", tWtr)):
        allv = np.concatenate([arr] + [np.array(
            [r[1 if nm == "tD" else 2] if r[1 if nm == "tD" else 2] is not None else np.nan
             for r in o]) for _, o in test])
        miss[nm] = float(np.sum(~np.isfinite(allv)) / len(allv))
    return {"tag": tag, "D": D, "cals": cals, "medians": med, "iqr": iqr,
            "uv_ir": uv_ir, "dims": dims, "missing": miss,
            "heat_ds": info["heat_ds"], "weyl": info.get("weyl")}


def mean(xs):
    vals = [x for x in xs if x is not None and np.isfinite(x)]
    return float(np.mean(vals)) if vals else float("nan")


def gate_c0(ana):
    dH, ds, dW = mean(ana["dims"]["dH"]), mean(ana["dims"]["ds"]), mean(ana["dims"]["dW"])
    r2ok = all(r is not None and r > 0.99 for r in ana["dims"]["dH_r2"])
    floors = {p: ana["medians"][p]["2"] for p in ("GW", "GD", "WD")}
    ok = (1.70 <= dH <= 2.05 and r2ok and 1.85 <= ds <= 2.20
          and 1.70 <= dW <= 2.30
          and all(np.isfinite(v) and v <= 0.45 for v in floors.values()))
    return {"pass": bool(ok), "dH": dH, "dH_r2_all": bool(r2ok), "ds": ds,
            "dW": dW, "floors": floors}


def gate_c1(dims_rec):
    hits_h, ds_vals = 0, []
    for o in dims_rec["origins"]:
        h = o["hausdorff"]
        if (not h["ok"] or abs(h["d"] - 2.0) > 0.5 or h["r2"] < 0.9):
            hits_h += 1
        ds_vals.append(o["ds_origin"]["d"])
    ds_mean = mean(ds_vals)
    h_pass = hits_h >= 12
    ds_pass = bool(np.isfinite(ds_mean) and (ds_mean < 1.5 or ds_mean > 2.5))
    return {"pass": bool(h_pass and ds_pass), "h_clause": bool(h_pass),
            "ds_clause": bool(ds_pass), "ds_mean": ds_mean,
            "heat_ds": dims_rec["heat_ds"]["d"]}


def sheet_analysis(outdir, tag, L):
    """OBS-0H pooled sheet contrasts (coords = validation-only grouping)."""
    c3 = j2_torus_coords(L)
    recs = tag_origins(outdir, tag)
    D = recs[0]["D"]
    ir_hi = min(12, math.floor(D / 2.0) - 1)
    uv = {r: {"tD": {"same": [], "cross": []}, "tW": {"same": [], "cross": []}}
          for r in (1, 2, 3)}
    ir = {"tD": {"same": [], "cross": []}, "tW": {"same": [], "cross": []}}
    for rec in recs:
        b0 = int(c3[rec["origin"]][2])
        for node, t in rec["taus"].items():
            R = t["R"]
            slot = "same" if int(c3[int(node)][2]) == b0 else "cross"
            if R in (1, 2, 3):
                uv[R]["tD"][slot].append(t["tD"])
                uv[R]["tW"][slot].append(t["tW"])
            if 8 <= R <= ir_hi:
                ir["tD"][slot].append(t["t"])
                ir["tW"][slot].append(t["tW"])
    out = {"uv": {}, "ir": {}}
    for r in (1, 2, 3):
        out["uv"][str(r)] = {
            k: obs0.sheet_contrast(uv[r][k]["same"], uv[r][k]["cross"])
            for k in ("tD", "tW")}
    out["ir"] = {k: obs0.sheet_contrast(ir[k]["same"], ir[k]["cross"])
                 for k in ("tD", "tW")}
    sens = {k: any(out["uv"][str(r)][k] is not None and out["uv"][str(r)][k] > 0.10
                   for r in (1, 2, 3)) for k in ("tD", "tW")}
    blind = {k: out["ir"][k] is not None and out["ir"][k] < 0.05 for k in ("tD", "tW")}
    out["pass"] = bool(all(sens.values()) and all(blind.values()))
    out["sensitive"] = sens
    out["blind"] = blind
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--stage", choices=["c0", "full"], default="full")
    args = ap.parse_args()
    outdir = args.outdir
    verdict = {"prereg_commit": args.commit, "gates": {}, "tags": {},
               "stage": args.stage}

    # C5.
    c5 = load(outdir, "c5.json")
    verdict["gates"]["C5"] = bool(c5["pass"])
    verdict["c5"] = c5

    # Main tags.
    main = {}
    c0tags = [("sq-L20", "sq"), ("sq-L28", "sq"), ("sq-L42", "sq")]
    j2tags = [("j2-L20", "j2"), ("j2-L28", "j2"), ("j2-L42", "j2")]
    for tag, fam in c0tags + (j2tags if args.stage == "full" else []):
        main[tag] = analyze_tag(outdir, tag, obs0.V_BANKED[fam])
        verdict["tags"][tag] = {
            "D": main[tag]["D"],
            "dims_mean": {k: mean(v) for k, v in main[tag]["dims"].items()
                          if k != "dH_r2"},
            "medians": main[tag]["medians"], "iqr": main[tag]["iqr"],
            "uv_ir": main[tag]["uv_ir"], "missing": main[tag]["missing"],
            "heat_ds": main[tag]["heat_ds"], "weyl": main[tag]["weyl"]}
    # Missing-tau accounting.
    miss_max = max(main[t]["missing"][k] for t in main for k in ("tD", "tW"))
    verdict["gates"]["missing_flag"] = bool(miss_max >= 0.10)
    verdict["gates"]["missing_stop"] = bool(miss_max > 0.25)
    verdict["missing_max"] = miss_max

    # C0 per L + monotone rise.
    c0 = {L: gate_c0(main[f"sq-L{L}"]) for L in (20, 28, 42)}
    mono = (c0[20]["dH"] < c0[28]["dH"] < c0[42]["dH"])
    c0pass = all(v["pass"] for v in c0.values()) and bool(mono)
    verdict["gates"]["C0"] = bool(c0pass)
    verdict["C0"] = c0
    verdict["C0_monotone"] = bool(mono)

    # C1 majority.
    c1 = {}
    for N in (800, 1568, 3528):
        for s in (0, 1, 2):
            c1[f"exp-N{N}-s{s}"] = gate_c1(load(outdir, f"dims_exp-N{N}-s{s}.json"))
    c1pass = sum(1 for v in c1.values() if v["pass"]) >= 6  # >=2/3 of 9
    verdict["gates"]["C1"] = bool(c1pass)
    verdict["C1"] = c1

    j2_open = bool(c0pass and verdict["gates"]["C5"]
                   and not verdict["gates"]["missing_stop"])
    verdict["gates"]["J2_open"] = j2_open
    if args.stage == "c0":
        verdict["ladder"] = "OBS0-STAGED-C0"
        with open(os.path.join(outdir, "verdict_c0.json"), "w") as f:
            json.dump(verdict, f, indent=1)
        print("=== OBS-0 C0 STAGE ===")
        print(f"C5={c5['pass']} C0={c0pass} C1={c1pass} J2_open={j2_open}")
        for tag in ("sq-L20", "sq-L28", "sq-L42"):
            m = verdict["tags"][tag]
            print(f"{tag}: dH={m['dims_mean']['dH']:.4f} ds={m['dims_mean']['ds']:.4f} "
                  f"dW={m['dims_mean']['dW']:.4f} "
                  f"dT3={ {p: round(m['medians'][p]['2'], 4) for p in ('GW', 'GD', 'WD')}}")
        return

    # DIM-PASS per L (C0-relative).
    dim = {}
    for L in (20, 28, 42):
        gaps = {k: abs(mean(main[f"j2-L{L}"]["dims"][k])
                        - mean(main[f"sq-L{L}"]["dims"][k]))
                for k in ("dH", "ds", "dW")}
        dim[str(L)] = {"gaps": gaps,
                       "pass": bool(all(np.isfinite(v) and v <= 0.15
                                            for v in gaps.values()))}
    verdict["DIM"] = dim

    # METRIC (L42 pairs + L28 sanity).
    metric_pairs = {}
    for p in ("GW", "GD", "WD"):
        j = main["j2-L42"]["medians"][p]["2"]
        c = main["sq-L42"]["medians"][p]["2"]
        metric_pairs[p] = bool(np.isfinite(j) and np.isfinite(c)
                               and j <= c + 0.05 and j <= 0.40)
    sanity28 = all(main["j2-L28"]["medians"][p]["2"] <= 0.45 for p in ("GW", "GD", "WD"))
    metric = bool(dim["28"]["pass"] and dim["42"]["pass"]
                  and all(metric_pairs.values()) and sanity28)
    verdict["METRIC_pairs"] = metric_pairs
    verdict["L28_sanity"] = bool(sanity28)
    verdict["gates"]["METRIC"] = metric

    # Sheet (L28 + L42 gate, L20 filed).
    sheet = {str(L): sheet_analysis(outdir, f"j2-L{L}", L) for L in (20, 28, 42)}
    verdict["sheet"] = sheet
    verdict["gates"]["sheet"] = bool(sheet["28"]["pass"] and sheet["42"]["pass"])

    # Perturbation (reduced battery: 8 origins, train 0-3 / test 4-7).
    pert = {}
    ref = main["j2-L28"]
    for s in range(4):
        tag = f"pert-L28-s{s}"
        pa = analyze_tag(outdir, tag, obs0.V_BANKED["j2"], n_origins=8, n_train=4)
        gaps = {k: abs(mean(pa["dims"][k]) - mean(ref["dims"][k]))
                for k in ("dH", "ds", "dW")}
        wd = pa["medians"]["WD"]["2"]
        wd_ref = ref["medians"]["WD"]["2"]
        pert[tag] = {
            "gaps": gaps,
            "wd_ir": wd, "wd_ref": wd_ref,
            "pass": bool(all(np.isfinite(v) and v <= 0.2 for v in gaps.values())
                         and np.isfinite(wd) and abs(wd - wd_ref) <= 0.05)}
        verdict["tags"][tag] = {
            "dims_mean": {k: mean(v) for k, v in pa["dims"].items() if k != "dH_r2"},
            "medians": pa["medians"], "missing": pa["missing"]}
    verdict["pert"] = pert
    verdict["gates"]["pert"] = bool(all(v["pass"] for v in pert.values()))

    # UNIVERSAL clauses.
    wtrend = [main[f"j2-L{L}"]["medians"]["WD"]["2"] for L in (20, 28, 42)]
    gstab = {p: max(main[f"j2-L{L}"]["medians"][p]["2"] for L in (20, 28, 42))
             - min(main[f"j2-L{L}"]["medians"][p]["2"] for L in (20, 28, 42))
             for p in ("GW", "GD")}
    univ_v = bool(all(np.isfinite(v) for v in wtrend)
                  and wtrend[0] >= wtrend[1] >= wtrend[2]
                  and all(np.isfinite(v) and v <= 0.10 for v in gstab.values()))
    univ_i = bool(all(main["j2-L42"]["uv_ir"].values()))
    univ_ii = bool(all(np.isfinite(main["j2-L42"]["iqr"][p])
                       and main["j2-L42"]["iqr"][p] <= 0.10 for p in ("GW", "GD", "WD")))
    universal = bool(metric and univ_i and univ_ii and verdict["gates"]["sheet"]
                     and verdict["gates"]["pert"] and univ_v)
    verdict["UNIVERSAL"] = {"i_uv_ir": univ_i, "ii_iqr": univ_ii,
                            "iii_sheet": verdict["gates"]["sheet"],
                            "iv_pert": verdict["gates"]["pert"],
                            "v_scaling": univ_v,
                            "wtrend": wtrend, "gstab": gstab}
    verdict["gates"]["UNIVERSAL"] = universal

    # Ladder.
    if not j2_open:
        ladder = "OBS0-BLOCKED"
    elif universal:
        ladder = "OBS0-UNIVERSAL"
    elif metric:
        ladder = "OBS0-METRIC"
    elif dim["28"]["pass"] and dim["42"]["pass"]:
        ladder = "OBS0-DIMENSION-ONLY"
    else:
        ladder = "OBS0-DISCORDANT"
    verdict["ladder"] = ladder
    with open(os.path.join(outdir, "verdict.json"), "w") as f:
        json.dump(verdict, f, indent=1)

    print("=== OBS-0 VERDICT ===")
    print(f"C5={c5['pass']} C0={c0pass} C1={c1pass} J2_open={j2_open}")
    print(f"DIM28={dim['28']['pass']} DIM42={dim['42']['pass']} "
          f"METRIC={metric} pairs={metric_pairs}")
    print(f"sheet={verdict['gates']['sheet']} pert={verdict['gates']['pert']} "
          f"UNIVERSAL={universal}")
    print(f"LADDER: {ladder}")
    for tag in ("j2-L20", "j2-L28", "j2-L42", "sq-L20", "sq-L28", "sq-L42"):
        m = verdict["tags"][tag]
        print(f"{tag}: dH={m['dims_mean']['dH']:.4f} ds={m['dims_mean']['ds']:.4f} "
              f"dW={m['dims_mean']['dW']:.4f} "
              f"dT3={ {p: round(m['medians'][p]['2'], 4) for p in ('GW', 'GD', 'WD')}}")


if __name__ == "__main__":
    main()
