#!/usr/bin/env python3
"""D7 surrogate milestone runner (NMMA-backed, exploratory/SURROGATE-NOT-RT).

Runs E0/E1/E2 x {anchor, gap50, gw190814} through the transport adapter,
evaluates the anchor gate, control, GW190814 observation operator, and
gap50 predictions, and writes machine-readable results/d7/*.json.

Requires $D7_NMMA_MODELS (see d7_public_models/fetch_models.sh).
Exit 0 on success (even if gates fail — verdicts are data), 2 if the
backend is absent. Deterministic given the pinned grids.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from bh_graph import d7models as DM
from bh_graph import d7transport as DT
from bh_graph import possis as P
from bh_graph.collapse import (
    KAPPA_BLUE,
    V_BLUE_C,
    dist_modulus,
    kilonova_peak_lum_erg_s,
    kilonova_peak_time_days,
    leg_shedding_ejecta,
    lum_to_abs_mag_bol,
)
from bh_graph.massgaps import (
    GW190814_CFHT_G_EPOCHS,
    GW190814_GROWTH_I_EPOCHS,
    gw190814_dist_sigma_mag,
)

ANCHOR_DIST = 40.0
GAP_DISTS = (100.0, 200.0)
D190814 = 241.0
ANCHOR_G_PEAK, ANCHOR_G_TOL = 18.0, 1.0
I_DECLINE_LO, I_DECLINE_HI = 3.0, 5.0


def analytic_blue_mag(m1: float, m2: float, t: float, dist: float) -> float:
    """Analytic blue-term g (same shape as gw190814_blue_mag, any event)."""
    import numpy as np

    ej = leg_shedding_ejecta(m1, m2)
    lb = kilonova_peak_lum_erg_s(ej["M_blue"], V_BLUE_C, KAPPA_BLUE)
    tb = kilonova_peak_time_days(ej["M_blue"], V_BLUE_C, KAPPA_BLUE)
    dm = dist_modulus(dist)
    shape = min(t / tb, 1.0) * np.exp(-max(t - tb, 0.0) / tb)
    return float(lum_to_abs_mag_bol(lb * shape) + dm)


def mag_grid(code, params, ts, bands, models_dir, with_err):
    """Evaluate {band: {t: (mag, err)}}. err only if with_err (speed)."""
    out = {}
    for b in bands:
        col = {}
        for t in ts:
            if with_err:
                r = DT.surrogate_mag(code, params, t, b, models_dir)
                col[t] = (
                    r.get("mag", float("nan")),
                    r.get("interp_err", float("nan")) if r.get("ok") else float("nan"),
                )
            else:
                r = DT.surrogate_mag(code, params, t, b, models_dir, with_err=False)
                col[t] = (r.get("mag", float("nan")), float("nan"))
        out[b] = col
    return out


def main() -> int:
    models_dir = os.environ.get(DT.NMMA_MODELS_ENV, "")
    if not DT.nmma_available() or not DT.models_dir_present(models_dir):
        print(f"need nmma + grids (set {DT.NMMA_MODELS_ENV}; see d7_public_models/)")
        return 2
    t0 = time.time()
    out_dir = ROOT / "results" / "d7"
    out_dir.mkdir(parents=True, exist_ok=True)

    import numpy as np

    cells, anchor_gate, control, det190814, gap50 = [], {}, {}, {}, {}
    # ---- per-cell evaluation ----
    jobs = []
    for th in DM.e0_thetas_deg():
        jobs.append(("E0", "gw170817", {"theta_deg": float(th)}))
        jobs.append(("E0", "gap50", {"theta_deg": float(th)}))
        jobs.append(("E0", "gw190814", {"theta_deg": float(th)}))
    for v in DM.e1_vej_ladder():
        for ev in ("gw170817", "gap50", "gw190814"):
            jobs.append(("E1", ev, {"vej_c": v, "xlan": DM.XLAN_E1_FIXED}))
    for x in DM.e2_xlan_ladder():
        for ev in ("gw170817", "gap50", "gw190814"):
            jobs.append(("E2", ev, {"vej_c": DM.VEL_CENTRAL_C, "xlan": x}))

    for emodel, event, kw in jobs:
        cell = DM.map_event_to_nmma(event, emodel, **kw)
        inv = DM.check_invariants(cell)
        rec = {
            "emodel": emodel,
            "event": event,
            "cell_kw": kw,
            "params": cell.get("params"),
            "rescale_max": cell.get("rescale_max"),
            "headline_eligible": cell.get("headline_eligible"),
            "invariants_ok": inv.get("ok"),
            "geometry": cell.get("geometry"),
        }
        code = DM.E_CODES[emodel]
        if event == "gw170817":
            ts_g = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
            ts_i = [0.5 + 0.5 * k for k in range(16)]
            rec["mags_g"] = {
                t: mag_grid(code, cell["params"], [t], ["g"], models_dir, True)["g"][t]
                for t in ts_g
            }
            rec["mags_i"] = {
                t: mag_grid(code, cell["params"], [t], ["i"], models_dir, False)["i"][t]
                for t in ts_i
            }
        elif event == "gap50":
            rec["mags"] = {b: None for b in ()}
            rec["mags"] = mag_grid(
                code, cell["params"], [0.5, 1.0, 2.0, 5.0], ["g", "r", "i", "z"], models_dir, True
            )
        else:
            rec["mags_g"] = {
                t: mag_grid(code, cell["params"], [t], ["g"], models_dir, True)["g"][t]
                for (t, _, _) in GW190814_CFHT_G_EPOCHS
            }
            rec["mags_i"] = {
                t: mag_grid(code, cell["params"], [t], ["i"], models_dir, True)["i"][t]
                for (t, _, _) in GW190814_GROWTH_I_EPOCHS
            }
        cells.append(rec)
        n_done = len(cells)
        if n_done % 10 == 0 or n_done == len(jobs):
            print(f"  cells {n_done}/{len(jobs)} ela={time.time() - t0:.0f}s", flush=True)

    def cell_rows(em, ev):
        return [c for c in cells if c["emodel"] == em and c["event"] == ev]

    # ---- anchor gate (per E-model; E0 uses pole-near thetas <=30deg) ----
    for em in ("E0", "E1", "E2"):
        rows = cell_rows(em, "gw170817")
        if em == "E0":
            rows = [c for c in rows if c["cell_kw"]["theta_deg"] <= 30.0]
        peaks = []
        declines = []
        for c in rows:
            g = {t: v[0] + dist_modulus(ANCHOR_DIST) for t, v in c["mags_g"].items()}
            tp = min(g, key=g.get)
            peaks.append(g[tp])
            im = {t: v[0] for t, v in c["mags_i"].items()}
            ti0 = min(im, key=im.get)
            dec = next(
                (t - ti0 for t in sorted(im) if t > ti0 and im[t] - im[ti0] >= 1.0), float("inf")
            )
            declines.append(dec)
        pass_g = all(abs(p - ANCHOR_G_PEAK) <= ANCHOR_G_TOL for p in peaks)
        pass_i = all(I_DECLINE_LO <= d <= I_DECLINE_HI for d in declines)
        anchor_gate[em] = {
            "peak_g_app": peaks,
            "pass_g": bool(pass_g),
            "i_decline_days": declines,
            "pass_i": bool(pass_i),
            "n_cells": len(rows),
        }

    # ---- control: RT g vs analytic g at anchor epochs ----
    for em in ("E0", "E1", "E2"):
        rows = cell_rows(em, "gw170817")
        ctl = []
        for t in (1.0, 2.0, 4.0):
            ana = analytic_blue_mag(1.4, 1.4, t, ANCHOR_DIST)
            for c in rows:
                th = c["cell_kw"].get("theta_deg", None)
                # nearest sampled t in mags_g
                ts = sorted(c["mags_g"])
                tn = min(ts, key=lambda x: abs(x - t))
                rt = c["mags_g"][tn][0] + dist_modulus(ANCHOR_DIST)
                ctl.append(
                    {
                        "t_req": t,
                        "t_rt": tn,
                        "theta": th,
                        "rt_g": rt,
                        "analytic_g": ana,
                        "delta": rt - ana,
                    }
                )
        control[em] = ctl

    # ---- GW190814 observation operator (per E-model/cell) ----
    sig_d = gw190814_dist_sigma_mag()
    for em in ("E0", "E1", "E2"):
        for c in cell_rows(em, "gw190814"):
            per_g, per_i = [], []
            for t, depth, cov in GW190814_CFHT_G_EPOCHS:
                m, e = c["mags_g"][t]
                e = e if np.isfinite(e) else DT.INTERP_ERR_FLOOR
                per_g.append(DT.surrogate_epoch_pdetect(depth, cov, m, D190814, e, 0.5, sig_d))
            for t, depth, cov in GW190814_GROWTH_I_EPOCHS:
                m, e = c["mags_i"][t]
                e = e if np.isfinite(e) else DT.INTERP_ERR_FLOOR
                per_i.append(DT.surrogate_epoch_pdetect(depth, cov, m, D190814, e, 0.5, sig_d))
            key = f"{em}|{c['cell_kw']}"
            det190814[key] = {
                "emodel": em,
                "cell_kw": c["cell_kw"],
                "headline_eligible": c["headline_eligible"],
                "per_epoch_g": per_g,
                "per_epoch_i": per_i,
                "P_comb_g": P.rt_combined_pdetect(per_g),
                "P_comb_gi": P.rt_combined_pdetect(per_g + per_i),
            }
    # E0 hiding bounds over thetas (sensitivity-only context at 0.43).
    e0_p = [v["P_comb_g"] for k, v in det190814.items() if v["emodel"] == "E0"]
    det190814["E0_hiding_bounds_g"] = P.hiding_bounds(e0_p)

    # ---- gap50 forward predictions ----
    for em in ("E0", "E1", "E2"):
        for c in cell_rows(em, "gap50"):
            key = f"{em}|{c['cell_kw']}"
            tab = {}
            for dist in GAP_DISTS:
                dm = dist_modulus(dist)
                for b in ("g", "r", "i", "z"):
                    for t in (0.5, 1.0, 2.0, 5.0):
                        m, e = c["mags"][b][t]
                        tab[f"{b}@{t}d@{dist}Mpc"] = {
                            "mag": m + dm if np.isfinite(m) else float("nan"),
                            "err": e if np.isfinite(e) else float("nan"),
                        }
            gap50[key] = {"emodel": em, "cell_kw": c["cell_kw"], "pred": tab}

    payloads = {
        "cells.json": cells,
        "anchor_gate.json": anchor_gate,
        "control.json": control,
        "gw190814_surrogate.json": det190814,
        "gap50_predictions.json": gap50,
        "manifest.json": {
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "nmma": "1.0.1",
            "backend": "sklearn_gp/local_only",
            "models": "Bu2019nsbh + Ka2017 ps1::griz (d7_public_models/SHA256SUMS)",
            "statistic": "possis.rt_epoch_pdetect/rt_combined_pdetect, sig_RT=0.5",
            "SURROGATE-NOT-RT": True,
            "elapsed_s": round(time.time() - t0, 1),
        },
    }
    for name, obj in payloads.items():
        tmp = out_dir / (name + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=1, sort_keys=True, default=str)
        os.replace(tmp, out_dir / name)
    print(f"wrote {out_dir} ({len(cells)} cells, ela={time.time() - t0:.0f}s)")
    print(
        "anchor_gate:",
        json.dumps(
            {
                k: {kk: vv for kk, vv in v.items() if kk.startswith("pass")}
                for k, v in anchor_gate.items()
            }
        ),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
