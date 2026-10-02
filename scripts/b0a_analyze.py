"""B0a analysis S4 (UNTRACKED; verdict filed in DEFERRED.md).

Locked rules (P1-AMENDMENT-4/5): headline cells (+branch, x-approach);
accounting hard gate 1e-9 (>1/3 invalid -> apparatus STOP); residence/
delay median-z>3 (delay needs >=5 non-NaN else void); mixing max>1e-6
in >=2 runs; B0-TRACK dual Spearman (rho>0.5 & p<0.05, n=27, per-state);
B1 5x + every-control; decision table. Prints verdict + b0a_results.json.
"""

import json
import math
import os
import sys

import numpy as np
from scipy.stats import mannwhitneyu, spearmanr

from bh_graph.ballistic import (
    chiral_breaking_strength,
    chiral_gamma_diag,
    graphs_from_saved,
    hamiltonian,
    j2_branch_parity,
)
from bh_graph.formation import j2_torus_coords, j2_torus_graph, state_from_nx, triangle_count

OUT = os.environ.get("B0A_PART", "/home/ubuntu/ballistic-be3e/b0a_parts")


d = json.load(open(f"{OUT}/b0a_cells.json"))
cells, states = d["cells"], d["states"]
by_si = {s["si"]: s for s in states}
OUTC = []


def ev(name, fired, detail):
    print(f"  [{'FIRE' if fired else 'null'}] {name}: {detail}", flush=True)
    OUTC.append({"name": name, "fired": bool(fired), "detail": str(detail)})
    return fired

# K covariates per state (headline B + triangle density)
for s in states:
    L = s["L"]
    if s["kind"] == "formed":
        rec = json.load(open(f"{OUT}/re_L{L}-d{s['dyn']}.json"))
        g = graphs_from_saved({s["sweep"]: rec["elists"][str(s["sweep"])]}, list(range(2 * L * L)))[s["sweep"]]
    elif s["kind"] == "d1":
        rec = json.load(open(f"{OUT}/d1_L{L}-d{s['dyn']}.json"))
        g = graphs_from_saved({s["sweep"]: rec["elists"][str(s["sweep"])]}, list(range(2 * L * L)))[s["sweep"]]
    else:
        g = j2_torus_graph(L)
    order = sorted(g.nodes())
    c3 = j2_torus_coords(L)
    gam = chiral_gamma_diag(j2_branch_parity(c3), order)
    s["B"] = chiral_breaking_strength(hamiltonian(g, order=order), gam)
    st = state_from_nx(g)
    s["T"] = triangle_count(st)
    s["tridens"] = s["T"] / g.number_of_edges()

HL = [c for c in cells if c["branch"] == "plus" and c["axis"] == "x" and not c["flip"]]
print(f"headline cells: {len(HL)}", flush=True)
bad_acc = [c for c in cells if c["acc"] > 1e-9]
print(f"accounting: max-dev-all={max(c['acc'] for c in cells):.1e} invalid={len(bad_acc)}/{len(cells)}", flush=True)
if len(bad_acc) > len(cells) / 3:
    print("APPARATUS-STOP: accounting failures > 1/3", flush=True)
    sys.exit(2)
bad_app = [c for c in HL if not c["approach_ok"]]
print(f"approach_ok headline fails: {len(bad_app)} (excluded+filed)", flush=True)
H = [c for c in HL if c["approach_ok"] and c["acc"] <= 1e-9]
POOL = os.environ.get("B0A_POOL", "headline")
if POOL == "headline":
    sel = json.load(open(f"{OUT}/b0a_selection.json"))["sitters"]
    selset = {(L, d) for L, d in sel}
    H = [c for c in H if (by_si[c["si"]]["L"], by_si[c["si"]]["dyn"]) in selset]
    print(f"pool=headline sitters={sel}", flush=True)
else:
    print("pool=all6 SENSITIVITY (unlocked appendix: filed, NO verdict role)", flush=True)
F = [c for c in H if by_si[c["si"]]["kind"] == "formed"]
C = [c for c in H if by_si[c["si"]]["kind"] != "formed"]
print(f"{POOL} valid: formed={len(F)} controls={len(C)}", flush=True)

for c in H:
    c["B"] = by_si[c["si"]]["B"]
    c["mass"] = by_si[c["si"]]["mass"]

# residence / delay contrasts
Rc = np.array([c["R"] for c in C])
mc, sc = float(Rc.mean()), float(Rc.std())
zR = [(c["R"] - mc) / sc if sc > 0 else 0.0 for c in F]
print(f"residence: controls mean={mc:.3f} std={sc:.3f} | formed={[f'{c['R']:.3f}' for c in F]}", flush=True)
print(f"  z = {[f'{z:+.2f}' for z in zR]} median={float(np.median(zR)):+.2f}", flush=True)
res_fire = float(np.median(zR)) > 3 if len(F) else False

def matched_bare_delay(c):
    sib = next(s["si"] for s in states if s["kind"] == "bare" and s["L"] == by_si[c["si"]]["L"]
               and s["dyn"] == by_si[c["si"]]["dyn"] and s["sweep"] == by_si[c["si"]]["sweep"])
    b = next(x for x in H if x["si"] == sib)
    if c["tcross"] is not None and b["tcross"] is not None:
        return c["tcross"] - b["tcross"]
    return None


dts = [x for x in (matched_bare_delay(c) for c in F) if x is not None]
dts_d1 = [x for x in (matched_bare_delay(c) for c in H if by_si[c["si"]]["kind"] == "d1") if x is not None]
print(f"delay formed: n={len(dts)} dts={[f'{x:+.1f}' for x in dts]}", flush=True)
print(f"delay D1-null: n={len(dts_d1)} dts={[f'{x:+.1f}' for x in dts_d1]}", flush=True)
delay_void = len(dts) < 5 or len(dts_d1) < 2
delay_fire = False
if not delay_void:
    m0, s0 = float(np.median(dts_d1)), float(np.std(dts_d1))
    z = [(x - m0) / s0 if s0 > 0 else (1.0 if x != m0 else 0.0) for x in dts]
    delay_fire = abs(float(np.median(z))) > 3 if s0 > 0 else abs(float(np.median(dts)) - m0) > 1.0
    print(f"  delay z = {[f'{x:+.2f}' for x in z]} (null: D1-vs-bare; bare-vs-bare === 0)", flush=True)
print(f"  delay_void={delay_void} delay_fire={delay_fire}", flush=True)

# mixing (DOMINANCE, Amendment-6: Mann-Whitney formed > D1 one-sided)
mixf = [c["mix"] for c in F]
mixd = [c["mix"] for c in H if by_si[c["si"]]["kind"] == "d1"]
mixb = [c["mix"] for c in H if by_si[c["si"]]["kind"] == "bare"]
print(f"mixing formed max={[f'{m:.1e}' for m in mixf]}", flush=True)
print(f"mixing D1 max={[f'{m:.1e}' for m in mixd]}", flush=True)
print(f"mixing bare floor={[f'{m:.1e}' for m in mixb]}", flush=True)
u_p = float(mannwhitneyu(mixf, mixd, alternative="greater").pvalue) if mixf and mixd else 1.0
mix_absent = not (len(mixf) and float(np.median(mixf)) > 1e-6)
mix_fire = ev("B0-mixing-dominance (MWU p<0.05)", (u_p < 0.05) and not mix_absent,
              f"p={u_p:.3g} absent={mix_absent}")
res_fire_full = res_fire or (delay_fire and not delay_void)
ev("B0-residence/delay (med-z>3)", res_fire_full, f"res={res_fire} delay={delay_fire} void={delay_void}")

# TRACK
mall = np.array([c["mix"] for c in H])
rall = np.array([c["R"] for c in H])
ball = np.array([c["B"] for c in H])
rho_m, p_m = spearmanr(mall, ball)
rho_r, p_r = spearmanr(rall, ball)
print(f"TRACK mixing-vs-B: rho={rho_m:+.3f} p={p_m:.3g} (n={len(H)})", flush=True)
print(f"TRACK residence-vs-B: rho={rho_r:+.3f} p={p_r:.3g} (n={len(H)})", flush=True)
track = rho_m > 0.5 and p_m < 0.05 and rho_r > 0.5 and p_r < 0.05
ev("B0-TRACK (dual rho>0.5 p<0.05)", track, "bridge" if track else "no-bridge")

# B1 (>=2 runs satisfying BOTH 5x AND exceeds-every-control)
wbars_f = [(c["wbar"], c["wbar"] / c["wdeloc"] if c["wdeloc"] > 0 else 0.0) for c in F]
wbars_c = [c["wbar"] for c in C]
print(f"B1 formed wbar/ratios={[f'{w:.4f}/{r:.1f}x' for w, r in wbars_f]}", flush=True)
print(f"B1 controls max wbar={max(wbars_c):.4f}", flush=True)
n_both = sum(1 for w, r in wbars_f if r > 5 and w > max(wbars_c))
b1 = ev("B1 (5x AND >every-control in >=2)", n_both >= 2, f"{n_both}/{len(wbars_f)}")

# descriptive (filed, no fire role): v_out, dispersion, incident-half, dW
def desc(label, vals):
    v = [x for x in vals if x is not None and (not isinstance(x, float) or math.isfinite(x))]
    print(f"  desc {label}: n={len(v)} " + (f"mean={float(np.mean(v)):.4f} min={min(v):.4f} max={max(v):.4f}" if v else "(empty)"), flush=True)
    return v

def vout_speed(c):
    v = c["vout"]
    return math.sqrt(v[0] ** 2 + v[1] ** 2) if v else None


print("descriptive formed vs controls:", flush=True)
for lab, key in (("vout_speed", None), ("width_growth", "width_growth"), ("incident", "inc")):
    if key is None:
        vf = [vout_speed(c) for c in F]
        vc = [vout_speed(c) for c in C]
    else:
        vf = [c[key] for c in F]
        vc = [c[key] for c in C]
    desc(f"formed-{lab}", vf)
    desc(f"controls-{lab}", vc)
desc("formed-vout_r2", [c["vout_r2"] for c in F])
desc("controls-vout_r2", [c["vout_r2"] for c in C])
desc("formed-vout_speed-r2gated", [vout_speed(c) for c in F if (c["vout_r2"] or 0) > 0.9])
desc("controls-vout_speed-r2gated", [vout_speed(c) for c in C if (c["vout_r2"] or 0) > 0.9])
for b in ("plus", "zero", "minus"):
    desc(f"formed-dW_{b}", [c["dW"][b] for c in F])
    desc(f"controls-dW_{b}", [c["dW"][b] for c in C])
print(f"K covariates: " + "; ".join(
    f"{s['kind']}@{s['L']}-d{s['dyn']}-sw{s['sweep']}: mass={s['mass']} B={s['B']:.4f} tridens={s['tridens']:.4f}"
    for s in states if s["kind"] == "formed"), flush=True)

# decision table (Amendment-6: BRIDGE = conjunction)
fire = res_fire_full or mix_fire
bridge = mix_fire and res_fire_full and track
if fire and bridge:
    verdict = "B0-FIRE+BRIDGE"
elif fire:
    verdict = "B0-FIRE-bridgeless"
else:
    verdict = "B0-NULL"
print(f"2x2: mix_fire={mix_fire} res_fire={res_fire_full}", flush=True)
tag = "VERDICT" if POOL == "headline" else "SENSITIVITY-unlocked"
print(f"{tag}: {verdict} | B1: {'FIRE' if b1 else 'NULL'}", flush=True)
# appendix snapshot (filed, no fire role)
app = [c for c in cells if not (c["branch"] == "plus" and c["axis"] == "x" and not c["flip"])]
print(f"appendix cells filed: {len(app)} "
      f"(minus/x-flip/y); approach_ok={sum(c['approach_ok'] for c in app)}/{len(app)}", flush=True)
out = {"pool": POOL, "verdict": verdict, "b1": bool(b1), "fire": bool(fire), "track": bool(track),
       "mix_fire": bool(mix_fire), "res_fire": bool(res_fire_full),
       "rho_m": float(rho_m), "p_m": float(p_m), "rho_r": float(rho_r), "p_r": float(p_r),
       "zR": [float(z) for z in zR], "dts": [float(x) for x in dts],
       "outcomes": OUTC, "n_headline": len(H), "n_formed": len(F), "n_controls": len(C)}
fn = f"{OUT}/b0a_results.json" if POOL == "headline" else f"{OUT}/b0a_results_all6.json"
json.dump(out, open(fn, "w"), indent=1)
