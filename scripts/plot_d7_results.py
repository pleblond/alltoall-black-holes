#!/usr/bin/env python3
"""The one D7 surrogate comparison plot (anchor control).

Reads results/d7/*.json (committed) + analytic curves; writes
results/d7/fig1_anchor_control.png. Exploratory (SURROGATE-NOT-RT):
anchor g lightcurves analytic vs E0 (pole/equator) vs E1 central vs E2
bracket, with the gate band and the observed AT2017gfo peak marked.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from run_d7_surrogate import analytic_blue_mag

from bh_graph.collapse import dist_modulus

RES = ROOT / "results" / "d7"
DM40 = dist_modulus(40.0)


def main() -> int:
    cells = json.loads((RES / "cells.json").read_text())
    anchor = [c for c in cells if c["event"] == "gw170817"]

    def curve(em, match):
        c = next(x for x in anchor if x["emodel"] == em and match(x["cell_kw"]))
        ts = sorted(float(t) for t in c["mags_g"])
        ms = [c["mags_g"][str(t)][0] + DM40 for t in ts]
        return np.array(ts), np.array(ms)

    fig, ax = plt.subplots(figsize=(8, 4.6))
    t = np.linspace(0.4, 2.1, 120)
    ana = np.array([analytic_blue_mag(1.4, 1.4, v, 40.0) for v in t])
    ax.plot(t, ana, "k-", lw=2, label="analytic (F5/F6, 1.4+1.4 @40Mpc)")
    ax.axhspan(17.0, 19.0, color="grey", alpha=0.15, label="gate 18.0±1.0")
    ax.axhline(17.5, color="k", ls=":", lw=1, label="AT2017gfo obs ~17.5")
    tp, mp = curve("E0", lambda k: k["theta_deg"] == 0.0)
    ax.plot(tp, mp, "o-", ms=3, label="E0 nsbh pole (PASS)")
    te, me = curve("E0", lambda k: k["theta_deg"] == 90.0)
    ax.plot(te, me, "s--", ms=3, label="E0 nsbh equator")
    tc, mc = curve("E1", lambda k: k["vej_c"] == 0.14)
    ax.plot(tc, mc, "^-", ms=3, label="E1 Ka vej=0.14 (gate FAIL)")
    tb, mb = curve("E2", lambda k: k["xlan"] == 1e-05)
    ax.plot(tb, mb, "v-", ms=3, label="E2 Ka Xlan=1e-5 (blue end)")
    tr, mr = curve("E2", lambda k: k["xlan"] == 0.01)
    ax.plot(tr, mr, "x--", ms=4, label="E2 Ka Xlan=1e-2 (red end)")
    ax.invert_yaxis()
    ax.set_xlabel("days post-merger")
    ax.set_ylabel("apparent g @ 40 Mpc (PS1-approx)")
    ax.set_title("D7 surrogate anchor control (EXPLORATORY — SURROGATE-NOT-RT)")
    ax.legend(fontsize=7, loc="best")
    fig.tight_layout()
    fig.savefig(RES / "fig1_anchor_control.png", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {RES / 'fig1_anchor_control.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
