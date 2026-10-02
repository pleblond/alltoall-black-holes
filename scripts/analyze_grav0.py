#!/usr/bin/env python3
"""GRAV-0 campaign analysis (prereg + A1/A1.5 estimators).

Loads paired-run JSONs, builds per-cell ΔD̄/SEM surfaces, raw + gated
fronts, shape series, fits, and verdicts (θ ∈ {0.0005, 0.001, 0.002}).
Writes summary JSON + verdict table + figures.
"""
import collections
import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bh_graph.grav0 import (
    amplitude_series,
    delta_profiles,
    fit_front,
    front_radii,
    front_radii_gated,
    half_mass_radii,
    mass_series,
    mean_delta,
    peak_radii,
    shell_sizes,
)

THETAS = (0.0005, 0.001, 0.002)
FOOT_PAD = 2


def load_cell(outdir, L, pert, dyn):
    """Paired deltas + accept/conn diagnostics for one cell."""
    fns = sorted(glob.glob(os.path.join(
        outdir, f"grav0_L{L}_{pert}_{dyn}_s*.json")))
    deltas, acc_p, acc_c, conn, longs = [], [], [], [], []
    for fn in fns:
        with open(fn) as f:
            d = json.load(f)["legs"]
        ps = {float(t): {int(r): v for r, v in prof.items()}
              for t, prof in d["pert"]["snapshots"].items()}
        cs = {float(t): {int(r): v for r, v in prof.items()}
              for t, prof in d["ctrl"]["snapshots"].items()}
        deltas.append(delta_profiles(ps, cs))
        acc_p.append(sum(d["pert"]["accepts"]))
        acc_c.append(sum(d["ctrl"]["accepts"]))
        conn.append((d["pert"]["connected"], d["ctrl"]["connected"]))
        longs.append(d["pert"]["longs_final"])
    return {"fns": fns, "deltas": deltas, "acc_p": acc_p, "acc_c": acc_c,
            "conn": conn, "longs": longs}


def analyze_cell(outdir, L, pert, dyn):
    cell = load_cell(outdir, L, pert, dyn)
    n = len(cell["fns"])
    assert n > 0, (L, pert, dyn)
    mean, sem = mean_delta(cell["deltas"])
    n_r = shell_sizes(L)
    rmax = L // 2
    amp = amplitude_series(mean)
    peak = peak_radii(mean)
    mass = mass_series(mean, n_r)
    hm = half_mass_radii(mean, n_r)
    fronts = {}
    for th in THETAS:
        fronts[th] = {"raw": front_radii(mean, th, rmax),
                      "gated": front_radii_gated(mean, sem, th, 3.0, rmax)}
    g = fronts[0.001]["gated"]
    foot = g[0.0]
    beyond = [t for t in sorted(g) if g[t] > foot + FOOT_PAD]
    rmax_reached = max(g.values())
    # Rising-window fits (first expansion -> first rmax), gated front.
    rising = []
    if beyond:
        t0, t1 = beyond[0], max(t for t in beyond if g[t] == rmax_reached)
        rising = [(t, g[t]) for t in sorted(g) if t0 <= t <= t1]
    fits = fit_front([t for t, _ in rising], [r for _, r in rising])
    acc_mean = sum(cell["acc_p"]) / n
    disc = sum(1 for c in cell["conn"] if not all(c))
    return {"n": n, "mean": mean, "sem": sem, "amp": amp, "peak": peak,
            "mass": mass, "half": hm, "fronts": fronts, "foot": foot,
            "beyond": beyond, "rmax_reached": rmax_reached,
            "rising": rising, "fits": fits, "acc_mean": acc_mean,
            "acc_p": cell["acc_p"], "disconnected": disc,
            "longs": cell["longs"]}


def verdict(a, theta=0.001):
    """Prereg §7 + A1.4/A1.5 verdict from analyzed cell."""
    g = a["fronts"][theta]["gated"]
    foot = a["foot"]
    rmax_reached = max(v for t, v in g.items())
    expands = rmax_reached > foot + FOOT_PAD
    if a["acc_mean"] < 20 and not expands:
        return "FROZEN"
    if not expands:
        return "DEAD"
    f = a["fits"]
    rb2 = f["ballistic"]["r2"]
    rd2 = f["diffusive"]["r2"]
    v = f["ballistic"]["v"]
    amp = a["amp"]
    fades = all(vv < theta for t, vv in amp.items() if t > 30)
    if rd2 > 0.9 and rd2 >= rb2:
        return "DIFFUSIVE" + ("-transient" if fades else "")
    if rb2 > 0.9 and v < 10.0:
        return "BALLISTIC" + ("-transient" if fades else "")
    if rb2 > 0.9 and v >= 10.0:
        return "INVALID-superluminal"
    if fades:
        return "TRANSIENT-DISSIPATIVE"
    return "MIXED-expanding"


def main():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--datadir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--figdir", default="figures")
    a = ap.parse_args()
    cells = {}
    Ls = sorted({int(fn.split("_L")[1].split("_")[0])
                 for fn in glob.glob(os.path.join(a.datadir, "*.json"))})
    print("L:", Ls)
    rows = []
    for fn in sorted(glob.glob(os.path.join(a.datadir, "*.json"))):
        base = os.path.basename(fn)
        parts = base.replace(".json", "").split("_")
        L, pert, dyn = int(parts[1][1:]), parts[2], parts[3]
        key = (L, pert, dyn)
        if key in cells:
            continue
        cells[key] = analyze_cell(a.datadir, L, pert, dyn)
        v = {th: verdict(cells[key], th) for th in THETAS}
        c = cells[key]
        rows.append((L, pert, dyn, c["n"], c["foot"], c["rmax_reached"],
                     round(c["acc_mean"], 1), v[0.0005], v[0.001], v[0.002],
                     c["disconnected"]))
        print(f"L={L} {pert}x{dyn} n={c['n']} foot={c['foot']} "
              f"rmax={c['rmax_reached']} acc~{c['acc_mean']:.0f} "
              f"verdicts={v[0.0005]}/{v[0.001]}/{v[0.002]} "
              f"disc={c['disconnected']}")
    # L-scaling per (P,U): rmax Reached vs L.
    scal = collections.defaultdict(list)
    for (L, pert, dyn), c in sorted(cells.items()):
        scal[(pert, dyn)].append((L, c["rmax_reached"], c["foot"]))
    print("\nL-scaling (L, rmax, foot):")
    for k in sorted(scal):
        print(f"  {k}: {scal[k]}")
    out = {"rows": rows, "scaling": {f"{p}x{u}": v for (p, u), v in scal.items()}}
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)
    print("wrote", a.out)
    make_figs(cells, a.figdir)


def make_figs(cells, figdir):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    os.makedirs(figdir, exist_ok=True)
    # Fig 1: U0xP2 L=42 surface + gated front.
    key = (42, "P2", "U0")
    if key in cells:
        c = cells[key]
        ts = sorted(t for t in c["mean"] if t <= 30)
        rs = sorted(r for r in c["mean"][0.0] if r <= 21)
        Z = np.array([[c["mean"][t][r] for r in rs] for t in ts])
        _, ax = plt.subplots(figsize=(9, 5))
        im = ax.imshow(Z, aspect="auto", origin="lower",
                       extent=[rs[0] - 0.5, rs[-1] + 0.5, ts[0], ts[-1]],
                       vmin=-0.02, vmax=0.1, cmap="RdBu_r")
        plt.colorbar(im, ax=ax, label="dDbar(r,t)")
        gf = [c["fronts"][0.001]["gated"][t] for t in ts]
        ax.plot(gf, ts, "k-", lw=1, label="gated front")
        ax.set_xlabel("r (pristine shells)")
        ax.set_ylabel("t (sweeps)")
        ax.set_title("GRAV-0 U0xP2 L=42: paired ripple surface")
        ax.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(figdir, "figGRAV0_surface_U0P2L42.png"), dpi=120)
        plt.close()
    # Fig 2: gated fronts grid at L=42.
    _, axes = plt.subplots(4, 5, figsize=(14, 10), sharex=True, sharey=True)
    for i, p in enumerate(("P1", "P2", "P3", "P4")):
        for j, u in enumerate(("U0", "U1", "U2", "U3", "U4")):
            ax = axes[i][j]
            c = cells.get((42, p, u))
            if c is None:
                ax.set_title(f"{p}x{u} (missing)")
                continue
            ts = sorted(t for t in c["mean"] if t <= 30)
            for th, st in ((0.0005, ":"), (0.001, "-"), (0.002, "--")):
                ax.plot(ts, [c["fronts"][th]["gated"][t] for t in ts],
                        st, lw=1, label=f"th={th}")
            ax.set_title(f"{p}x{u}")
            ax.set_ylim(-1, 22)
    axes[0][0].legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(os.path.join(figdir, "figGRAV0_fronts_L42.png"), dpi=120)
    plt.close()
    print("figs ->", figdir)


if __name__ == "__main__":
    main()
