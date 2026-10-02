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
    seeds = []
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
        seeds.append(int(fn.split("_s")[1].split(".")[0]))
    return {"fns": fns, "seeds": seeds, "deltas": deltas, "acc_p": acc_p,
            "acc_c": acc_c, "conn": conn, "longs": longs}


def longest_run_above(prof, theta):
    """Longest consecutive-shell run with value > theta (A2.2)."""
    best, cur = 0, 0
    for r in sorted(prof):
        cur = cur + 1 if prof[r] > theta else 0
        best = max(best, cur)
    return best


def analyze_cell(outdir, L, pert, dyn):
    cell = load_cell(outdir, L, pert, dyn)
    n = len(cell["fns"])
    assert n > 0, (L, pert, dyn)
    # A2.3: exclude disconnected runs from fronts/fits.
    valid = [i for i, c in enumerate(cell["conn"]) if all(c)]
    disc = n - len(valid)
    use = [cell["deltas"][i] for i in valid]
    mean, sem = mean_delta(use) if use else ({}, {})
    n_r = shell_sizes(L)
    rmax = L // 2
    amp = amplitude_series(mean) if use else {}
    peak = peak_radii(mean) if use else {}
    mass = mass_series(mean, n_r) if use else {}
    hm = half_mass_radii(mean, n_r) if use else {}
    fronts = {}
    runs = {}
    for th in THETAS:
        fronts[th] = {"raw": front_radii(mean, th, rmax) if use else {},
                      "gated": front_radii_gated(mean, sem, th, 3.0, rmax)
                      if use else {}}
        runs[th] = {t: longest_run_above(mean[t], th) for t in mean} \
            if use else {}
    # A2.1 split-half replication (by seed value).
    halves = {}
    for tag, lo, hi in (("H1", 0, 7), ("H2", 8, 15)):
        idx = [i for i in valid if lo <= cell["seeds"][i] <= hi]
        if len(idx) >= 4:
            mh, sh = mean_delta([cell["deltas"][i] for i in idx])
            halves[tag] = {th: front_radii_gated(mh, sh, th, 3.0, rmax)
                           for th in THETAS}
        else:
            halves[tag] = {}
    g = fronts[0.001]["gated"]
    foot = g[0.0] if use else -1
    beyond = [t for t in sorted(g) if g[t] > foot + FOOT_PAD] if use else []
    rmax_reached = max(g.values()) if use else -1
    # Replicated expansion: same-t both-halves breach (A2.1).
    repl = []
    repl_r = {}
    if halves.get("H1") and halves.get("H2"):
        for t in sorted(g):
            r1 = halves["H1"][0.001].get(t, -1)
            r2 = halves["H2"][0.001].get(t, -1)
            if r1 > foot + FOOT_PAD and r2 > foot + FOOT_PAD:
                repl.append(t)
                repl_r[t] = (r1, r2)
    # Same-(t,r) replication (within 2 shells): sustained-far check.
    repl_tr = [t for t in repl if abs(repl_r[t][0] - repl_r[t][1]) <= 2]
    rising = []
    if beyond:
        t0, t1 = beyond[0], max(t for t in beyond if g[t] == rmax_reached)
        rising = [(t, g[t]) for t in sorted(g) if t0 <= t <= t1]
    fits = fit_front([t for t, _ in rising], [r for _, r in rising])
    acc_mean = (sum(cell["acc_p"][i] for i in valid) / len(valid)
                if valid else 0.0)
    e_total = 8 * L * L  # J2 torus edges = 8N/2, N = 2L^2
    longs_frac = (sum(cell["longs"][i] for i in valid) / len(valid)
                  / e_total) if valid else 0.0
    return {"n": n, "n_valid": len(valid), "mean": mean, "sem": sem,
            "amp": amp, "peak": peak, "mass": mass, "half": hm,
            "fronts": fronts, "runs": runs, "halves": halves,
            "foot": foot, "beyond": beyond, "repl": repl,
            "repl_r": repl_r, "repl_tr": repl_tr,
            "rmax_reached": rmax_reached, "rising": rising, "fits": fits,
            "acc_mean": acc_mean, "acc_p": cell["acc_p"],
            "disconnected": disc, "longs": cell["longs"],
            "longs_frac": longs_frac}


def viability(a):
    """A2.4 viability axis: VIABLE / MELTS / FRAGMENTS."""
    if a["n_valid"] == 0:
        return "FRAGMENTS"
    if a["longs_frac"] > 0.10:
        return "MELTS"
    if a["disconnected"] > 0:
        return f"VIABLE?({a['disconnected']}disc)"
    return "VIABLE"


def verdict(a, theta=0.001):
    """Prereg §7 + A1.4/A1.5 verdict from analyzed cell (max-r based)."""
    if a["n_valid"] == 0:
        return "FRAGMENTS"
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


def verdict_rep(a, theta=0.001):
    """A2.1 replicated verdict: expansion must replicate across halves."""
    if a["n_valid"] == 0:
        return "FRAGMENTS"
    expands = len(a["repl"]) > 0
    if a["acc_mean"] < 20 and not expands:
        return "FROZEN"
    if not expands:
        # Distinguish unreplicated-max-r claims (WEAK) from pinned (DEAD).
        g = a["fronts"][theta]["gated"]
        if max(g.values()) > a["foot"] + FOOT_PAD:
            return "WEAK-unreplicated"
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
    if fades:
        return "TRANSIENT-DISSIPATIVE"
    return "MIXED-replicated"


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
        vr = {th: verdict_rep(cells[key], th) for th in THETAS}
        c = cells[key]
        rows.append((L, pert, dyn, c["n"], c["n_valid"], c["foot"],
                     c["rmax_reached"], round(c["acc_mean"], 1),
                     v[0.001], vr[0.001], viability(c),
                     len(c["repl"]), c["disconnected"],
                     round(c["longs_frac"], 3)))
        rmax_tr = max((max(c["repl_r"][t]) for t in c["repl_tr"]),
                      default=-1)
        print(f"L={L} {pert}x{dyn} n={c['n']}/{c['n_valid']} foot={c['foot']} "
              f"rmax={c['rmax_reached']} acc~{c['acc_mean']:.0f} "
              f"maxr={v[0.001]} repl={vr[0.001]} via={viability(c)} "
              f"nrepl={len(c['repl'])}/tr={len(c['repl_tr'])}@{rmax_tr} "
              f"disc={c['disconnected']} longs={c['longs_frac']:.2f}")
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
    make_figs(cells, a.figdir, a.datadir)


def make_figs(cells, figdir, datadir):
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
    # Fig 3: bump decay + background melt (P2xU0 L=42).
    key = (42, "P2", "U0")
    if key in cells:
        import json as _json

        c = cells[key]
        ts = sorted(c["mean"])
        amp = [max(c["mean"][t].values()) for t in ts]
        bg = {}
        for fn in sorted(glob.glob(os.path.join(datadir, "*.json"))):
            if "L42_P2_U0" not in fn:
                continue
            with open(fn) as f:
                d = _json.load(f)["legs"]
            for t, prof in d["ctrl"]["snapshots"].items():
                bg.setdefault(float(t), []).append(
                    sum(v for r, v in prof.items() if int(r) <= 2) / 3)
        bt = sorted(bg)
        bv = [sum(bg[t]) / len(bg[t]) for t in bt]
        _, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        ax1.semilogx([max(t, 0.03) for t in ts], amp, "k-", lw=1.5)
        ax1.axhline(0.001, color="r", ls="--", lw=1, label="theta")
        ax1.set_xlabel("t (sweeps, log)")
        ax1.set_ylabel("bump amplitude A(t)")
        ax1.set_title("P2xU0 L=42: ripple amplitude (peak pinned r<=1)")
        ax1.legend()
        ax2.plot(bt, bv, "b-", lw=1.5, label="U0 ctrl background")
        ax2.set_xlabel("t (sweeps)")
        ax2.set_ylabel("D_ctrl (r<=2)")
        ax2.set_title("vacuum melts by t~10 (same runs)")
        ax2.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(figdir, "figGRAV0_bumpdecay_L42.png"), dpi=120)
        plt.close()
    print("figs ->", figdir)


if __name__ == "__main__":
    main()
