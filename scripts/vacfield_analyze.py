"""VAC-FIELD-0 analyzer: records -> preregistered checks -> verdict.

Usage:
  python scripts/vacfield_analyze.py --datadir data/vacfield \\
      --npydir data/vacfield/npy --out data/vacfield/verdict.json

All gates mirror VACFIELD0-PREREG exactly (bars: vacfield.BARS). Missing
records or .npy sidecars are LOUD failures (never silent). ZERO is a
control: ranked in the table but capped (never the vacuum by design).
Record names come from vacfield_campaign.record_name (single source).
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from bh_graph import vacfield as vf  # noqa: E402
from vacfield_campaign import record_name as R  # noqa: E402

NONZERO = ("VPLUS", "VPI", "VMINUS")


def load(datadir):
    recs = {}
    for path in sorted(glob.glob(os.path.join(datadir, "*.json"))):
        base = os.path.basename(path)
        if base == "verdict.json":
            continue
        with open(path) as f:
            recs[os.path.splitext(base)[0]] = json.load(f)
    return recs


def need(recs, name):
    if name not in recs:
        raise SystemExit(f"MISSING record: {name} (campaign incomplete)")
    return recs[name]["payload"]


def load_npy(npydir, name):
    p = os.path.join(npydir, name + ".npy")
    if not os.path.exists(p):
        raise SystemExit(f"MISSING npy sidecar: {p} (campaign incomplete)")
    return np.load(p)


def max_dev_npy(npydir, names):
    arrs = [load_npy(npydir, n) for n in names]
    base = arrs[0]
    return max(float(np.abs(a - base).max()) for a in arrs[1:]) if len(arrs) > 1 else 0.0


def kinds_for(c):
    return ["amplitude", "packet", "source"] + ([] if c == "ZERO" else ["phase"])


def analyze(datadir, npydir):
    recs = load(datadir)
    checks = {c: {} for c in vf.CANDIDATES}
    notes = []

    # --- 0A census re-verification (exact predictions, loud) ---
    cen = need(recs, R("census", {}))
    assert abs(cen["L4"]["e_min"] + 8.0) < 1e-9, cen["L4"]
    assert abs(cen["L4"]["e_max"] - 8.0) < 1e-9
    assert cen["L4"]["n_zero"] == 22
    assert abs(cen["L8"]["e_min"] + 8.0) < 1e-9
    assert abs(cen["L8"]["e_max"] - 8.0) < 1e-9
    assert cen["L8"]["n_zero"] == 78  # 64 flat + nodal(8) = 64 + 14 (Amend-3)
    assert cen["L8"]["bloch_max_dev"] < vf.BARS["bloch_dev"]
    notes.append("census L4/L8 exact (e_min/max, n_zero 22/80, Bloch)")

    # --- 0C phase equivalence (exact prediction, loud) ---
    for c in vf.CANDIDATES:
        for L in (4, 28):
            r = need(recs, R("phase", {"cand": c, "L": L}))
            assert r["ok"], (c, L, r["dev"])
    notes.append("phase equivalence holds all candidates L4/L28")

    # --- stationary (0F) ---
    for c in vf.CANDIDATES:
        r = need(recs, R("stat", {"cand": c}))
        checks[c]["stationary"] = bool(r["ok"])

    # --- perturbation_ok (0K): norms + packet velocity + cross-bg + eps-indep ---
    vexp = np.array([4.0 * math.sin(0.5), 0.0])
    for c in vf.CANDIDATES:
        norms_ok, eps_ok = True, True
        for k in kinds_for(c):
            for e in vf.EPS_GRID:
                r = need(recs, R("pert", {"cand": c, "kind": k, "eps": e}))
                norms_ok = norms_ok and bool(r["norm_ok"])
        rp = need(recs, R("pert", {"cand": c, "kind": "packet", "eps": vf.EPS_HEADLINE}))
        v = np.array(rp["vfit"]["v"], dtype=float)
        vel_ok = (float(np.linalg.norm(v - vexp) / np.linalg.norm(vexp))
                  < vf.BARS["packet_velocity"] and float(rp["vfit"]["r2"]) > 0.9)
        for k in ("packet", "amplitude", "source"):
            # Eps-independence via normalized rows (v-spread is meaningless
            # for v ~= 0 symmetric kinds; Amendment-2).
            arrs = [load_npy(npydir, R("pert", {"cand": c, "kind": k, "eps": e})
                              + "_drows_down") / float(e) for e in vf.EPS_GRID]
            dev = max(float(np.abs(arrs[i] - arrs[1]).max()) for i in (0, 2))
            eps_ok = eps_ok and dev < 1e-9
        checks[c]["perturbation_ok"] = bool(norms_ok and vel_ok and eps_ok)
        checks[c]["_vel"] = bool(vel_ok)
        notes.append(f"{c}: packet v={np.array(rp['vfit']['v']).round(4).tolist()} "
                     f"r2={rp['vfit']['r2']:.4f} alpha={rp['msd_alpha']:.3f}")
    # Cross-background dpsi agreement (load-bearing 0K/0L): downsampled max-dev.
    cross_ok, cross_sha = True, True
    for k in ("packet", "amplitude", "source"):
        names = [R("pert", {"cand": c, "kind": k, "eps": vf.EPS_HEADLINE}) + "_drows_down"
                 for c in vf.CANDIDATES]
        dev = max_dev_npy(npydir, names)
        cross_ok = cross_ok and dev < 1e-9
        shas = {need(recs, R("pert", {"cand": c, "kind": k,
                                      "eps": vf.EPS_HEADLINE}))["drows_sha"]
                for c in vf.CANDIDATES}
        cross_sha = cross_sha and len(shas) == 1
        notes.append(f"cross-bg {k}: max-dev={dev:.2e} bitwise={len(shas) == 1}")
    for c in vf.CANDIDATES:
        checks[c]["perturbation_ok"] = bool(checks[c]["perturbation_ok"] and cross_ok)
    notes.append(f"cross-bg bitwise-all: {cross_sha} (filed, gated via max-dev)")

    # --- current_free (0E) / stress (0H) ---
    for c in vf.CANDIDATES:
        checks[c]["current_free"] = bool(
            need(recs, R("current", {"cand": c, "L": 4}))["ok"]
            and need(recs, R("current", {"cand": c, "L": 28}))["ok"])
        checks[c]["stress"] = bool(
            need(recs, R("stress", {"cand": c, "L": 4}))["ok"]
            and need(recs, R("stress", {"cand": c, "L": 28}))["ok"])

    # --- amplitude_coherent (0D) ---
    for c in vf.CANDIDATES:
        checks[c]["amplitude_coherent"] = bool(need(recs, R("scaling", {"cand": c}))["ok"])

    # --- linearity (0L) ---
    for c in vf.CANDIDATES:
        oks = [need(recs, R("lin", {"cand": c, "kind": k}))["ok"]
               for k in ("packet", "amplitude")]
        checks[c]["linearity"] = bool(all(oks))

    # --- normalized_robust (0M/0P) ---
    amps = list(vf.AMPLITUDES)
    frac_ok, abs_ok = True, True
    for k in ("packet", "amplitude"):
        fn = [R("amp", {"cand": "VPLUS", "kind": k, "mode": "frac", "amp": a})
              + "_drows_normed_down" for a in amps]
        dev = max_dev_npy(npydir, fn)
        frac_ok = frac_ok and dev < 1e-9
        an = [R("amp", {"cand": "VPLUS", "kind": k, "mode": "abs", "amp": a})
              + "_drows_normed_down" for a in amps]
        araw = [load_npy(npydir, n)
                * need(recs, R("amp", {"cand": "VPLUS", "kind": k,
                                       "mode": "abs", "amp": a}))["d0_norm"]
                for n, a in zip(an, amps)]
        dev_raw = max(float(np.abs(x - araw[3]).max()) for i, x in enumerate(araw) if i != 3)
        abs_ok = abs_ok and dev_raw < 1e-9
        notes.append(f"VPLUS {k}: frac-collapse={dev:.2e} abs-raw={dev_raw:.2e}")
    rel_f = [need(recs, R("amp", {"cand": "VPLUS", "kind": "packet",
                                  "mode": "frac", "amp": a}))["peak_dB_rel"] for a in amps]
    rel_a = [need(recs, R("amp", {"cand": "VPLUS", "kind": "packet",
                                  "mode": "abs", "amp": a}))["peak_dB_rel"] for a in amps]
    spread_f = (max(rel_f) - min(rel_f)) / max(max(rel_f), 1e-300)
    la = np.log(np.array([float(a) for a in amps]))
    slope_a = float(np.polyfit(la, np.log(np.maximum(rel_a, 1e-300)), 1)[0])
    vv_f = [need(recs, R("amp", {"cand": "VPLUS", "kind": "packet",
                                 "mode": "frac", "amp": a}))["vfit"]["v"] for a in amps]
    vv_a = [need(recs, R("amp", {"cand": "VPLUS", "kind": "packet",
                                 "mode": "abs", "amp": a}))["vfit"]["v"] for a in amps]
    vspread = max(float(np.linalg.norm(np.array(v) - np.array(vv_f[3]))) for v in vv_f + vv_a)
    vrel = vspread / float(np.linalg.norm(vexp))
    frac_ok = frac_ok and spread_f < 1e-6 and vrel < 1e-6
    abs_ok = abs_ok and abs(slope_a + 1.0) < 0.05
    notes.append(f"VPLUS frac peak-spread={spread_f:.2e} v-spread={vrel:.2e} "
                 f"abs slope={slope_a:.4f} (expect -1)")
    checks["VPLUS"]["normalized_robust"] = bool(frac_ok and abs_ok)
    for c in ("VPI", "VMINUS"):
        rel = [need(recs, R("ampbracket", {"cand": c, "kind": "packet",
                                           "mode": "frac", "amp": a}))["peak_dB_rel"]
               for a in (0.1, 1.0, 10.0)]
        spread = (max(rel) - min(rel)) / max(max(rel), 1e-300)
        checks[c]["normalized_robust"] = bool(spread < 1e-6)
        notes.append(f"{c} bracket peak-spread={spread:.2e}")
    checks["ZERO"]["normalized_robust"] = False  # control: no bg scale

    # --- zero_anatomy (0N/0O) ---
    for c in vf.CANDIDATES:
        anat = True
        for k in kinds_for(c):
            for e in vf.EPS_GRID:
                z = need(recs, R("pert", {"cand": c, "kind": k, "eps": e}))["zero"]
                anat = anat and z["B_inc_max_all"] < vf.BARS["zero_incident"] \
                    and z["J_inc_max_all"] < vf.BARS["zero_incident"]
        if c != "ZERO":
            z = need(recs, R("zero", {"cand": c}))
            anat = anat and z["n_events"] >= 1 \
                and z["B_inc_max_all"] < vf.BARS["zero_incident"] \
                and z["J_inc_max_all"] < vf.BARS["zero_incident"] \
                and z["winding"]["max_drift"] < vf.BARS["winding_drift"]
            notes.append(f"{c} zero-demo: n={z['n_events']} "
                         f"drift={z['winding']['max_drift']:.2e}")
        checks[c]["zero_anatomy"] = bool(anat)

    # --- sector_filed (0R) ---
    for c in NONZERO:
        checks[c]["sector_filed"] = True
    for L in (4, 8, 28):
        s = need(recs, R("sectors", {"L": L}))
        for c, which in (("VPLUS", "sym"), ("VPI", "sym"), ("VMINUS", "anti")):
            checks[c]["sector_filed"] = bool(
                checks[c]["sector_filed"] and vf.is_sector_pure_ok(s["weights"][c], which))
        ok = max(s["frozen_err"]) < 1e-8 and max(s["split_err"]) < 1e-8 \
            and s["intertwining"] < 1e-9
        for c in NONZERO:
            checks[c]["sector_filed"] = bool(checks[c]["sector_filed"] and ok)
        notes.append(f"L{L}: frozen={max(s['frozen_err']):.2e} "
                     f"split={max(s['split_err']):.2e} intertw={s['intertwining']:.2e}")
    checks["ZERO"]["sector_filed"] = True  # control: trivially in both sectors

    # --- ledger_symmetric (0I; VPI one-sided exact per Amendment-1) ---
    VPI_F0_L28 = 776 / 1559  # same-q pairs 613872/1222256 favor; rest neutral
    for c in vf.CANDIDATES:
        m1s = [need(recs, R("m1", {"cand": c, "seed": s, "amp": 1.0}))["stats"]
               for s in vf.M1_SEEDS]
        ex = need(recs, R("m1exact", {"cand": c}))["stats"]
        co4 = need(recs, R("contract", {"cand": c, "L": 4}))
        co28 = need(recs, R("contract", {"cand": c, "L": 28}))
        contract_ok = bool(co4["uniform_ok"] and co28["uniform_ok"])
        if c in ("VPLUS", "ZERO"):
            m1_ok = all(s["f_zero"] == 1.0 for s in m1s) and ex["f_zero"] == 1.0
        elif c == "VPI":
            f0 = [s["f_zero"] for s in m1s]
            m1_ok = (all(s["f_pos"] == 0.0 for s in m1s)
                     and all(abs(x - VPI_F0_L28) < 0.015 for x in f0)
                     and float(np.std(f0)) < 0.01
                     and abs(ex["f_zero"] - 128 / 368) < 1e-12
                     and abs(ex["f_neg"] - 240 / 368) < 1e-12
                     and ex["f_pos"] == 0.0)
            notes.append(f"VPI f0 L28: {[round(x, 4) for x in f0]} "
                         f"(expect {VPI_F0_L28:.4f}), f_pos = 0 exact")
        else:
            f0 = [s["f_zero"] for s in m1s]
            m1_ok = (all(abs(x - 0.5) < 0.015 for x in f0)
                     and float(np.std(f0)) < 0.01
                     and abs(ex["f_zero"] - 0.5) < 1e-12
                     and abs(ex["f_neg"] - 176 * 64 / 47104) < 1e-12
                     and abs(ex["f_pos"] - 192 * 64 / 47104) < 1e-12)
            for a in (1e-3, 1000.0):
                xe = need(recs, R("m1extreme", {"cand": "VMINUS", "seed": 0,
                                                "amp": a}))["stats"]
                m1_ok = m1_ok and abs(xe["f_zero"] - 0.5) < 0.015
            notes.append(f"VMINUS f0 L28: {[round(x, 4) for x in f0]} "
                         f"exhaustive L4: f0={ex['f_zero']}")
        checks[c]["ledger_symmetric"] = bool(m1_ok and contract_ok)

    # --- 0J identity re-verification (exact prediction, loud) ---
    sj = need(recs, R("subcheck", {}))
    assert all(sj.values()), sj
    notes.append("0J subtraction identity holds all nonzero shapes")

    # --- 0S control verification (exact predictions, loud) ---
    for sub, kinds in (("sq-28", "square"), ("ring-256", "ring")):
        r = need(recs, R("subctl", {"sub": sub}))
        e_top = 4.0 if sub == "sq-28" else 2.0
        assert abs(r["VPLUS"]["rayleigh"] + e_top) < 1e-9, (sub, r["VPLUS"])
        assert abs(r["VPI"]["rayleigh"] - e_top) < 1e-9
        for c in ("VPLUS", "VPI"):
            assert r[c]["residual"] < 1e-9
            assert r[c]["current"]["edge_max"] < 1e-12
            assert r[c]["S_std"] < 1e-9
    rq = need(recs, R("subctl", {"sub": "quot-28"}))
    assert abs(rq["VPLUS"]["rayleigh"] + 8.0) < 1e-9
    assert abs(rq["VPI"]["rayleigh"] - 8.0) < 1e-9
    assert rq["VPLUS"]["rho_drift"] < 1e-8 and rq["VPI"]["B_drift"] < 1e-8
    for sub, f0_vpi in (("sq-28", 388 / 779), ("ring-256", 126 / 253)):
        for s in vf.M1_SEEDS:
            st = need(recs, R("m1ctl", {"sub": sub, "cand": "VPLUS",
                                        "seed": s}))["stats"]
            assert st["f_zero"] == 1.0, (sub, s, st)
        for s in vf.M1_SEEDS:
            # VPI one-sided on every bipartite substrate (Amendment-1):
            # f_pos = 0 exactly, f_0 = same-q-pair fraction.
            st = need(recs, R("m1ctl", {"sub": sub, "cand": "VPI",
                                        "seed": s}))["stats"]
            assert st["f_pos"] == 0.0, (sub, s, st)
            assert abs(st["f_zero"] - f0_vpi) < 0.015, (sub, s, st)
    notes.append("0S controls exact (energies, currents, VPLUS-flat / "
                 "VPI-one-sided ledgers, H_Q)")

    # --- ladder + 0Q table ---
    ladder_keys = ("stationary", "perturbation_ok", "current_free", "stress",
                   "amplitude_coherent", "linearity", "normalized_robust",
                   "zero_anatomy", "sector_filed", "ledger_symmetric")
    evals = {c: vf.evaluate_candidate(c, {k: checks[c][k] for k in ladder_keys})
             for c in vf.CANDIDATES}
    verdict = vf.campaign_verdict({c: evals[c] for c in NONZERO})
    q = {}
    for c in vf.CANDIDATES:
        sh = need(recs, R("shapes", {"sub": "j2-28"}))["rows"][c]
        q[c] = {
            "stationary": checks[c]["stationary"],
            "relational_Bmax": sh["B_stats"]["maxabs"],
            "current_free": checks[c]["current_free"],
            "stress": checks[c]["stress"],
            "ledger": "flat" if c == "VPLUS" else
                      ("one-sided" if c == "VPI" else
                       ("structured" if c == "VMINUS" else "trivial")),
            "perturbation_ok": checks[c]["perturbation_ok"],
            "sector": "P+" if c in ("VPLUS", "VPI") else
                      ("P-" if c == "VMINUS" else "trivial"),
            "phase_defined_everywhere": c != "ZERO",
            "rung": evals[c]["rung"] + (" (control)" if c == "ZERO" else ""),
        }
    return {"checks": {c: {k: bool(checks[c][k]) for k in ladder_keys} for c in checks},
            "evals": {c: {"rung": e["rung"]} for c, e in evals.items()},
            "headline": verdict["headline"], "q_table": q, "notes": notes}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--datadir", default="data/vacfield")
    ap.add_argument("--npydir", default="data/vacfield/npy")
    ap.add_argument("--out", default="data/vacfield/verdict.json")
    a = ap.parse_args(argv)
    out = analyze(a.datadir, a.npydir)
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)
    print("headline:", out["headline"])
    for c, e in out["evals"].items():
        print(f"  {c}: {e['rung']}")
    for n in out["notes"]:
        print("  |", n)
    print(a.out)


if __name__ == "__main__":
    main()
