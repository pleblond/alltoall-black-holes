# GRAV-0 — Results: no far carrier on J₂

**Campaign:** 2026-10-02, beast EC2 (96 CPU, ~65 min wall).
**Design:** `docs/grav0-prereg.md` (+ amendments A1/A1.5/A2, all
pre-data except A2 estimator hardening, which is labeled post-hoc).
**Headline:** no tested strictly-local dynamics both preserves J₂
and carries a local disturbance beyond its near field. Global
verdict: **NO FAR CARRIER** (one θ-robust micro-transport cell at
r ≤ 8, fully disclosed below; no sustained or far propagation in
60 main cells + 4 L=64 + 3 nonlocal-pert calibration cells).

## 1. Verdicts by dynamics (θ = 0.001, A2 replicated)

| U | class (12 main cells) | viability | accepts / 200 sweeps |
|---|---|---|---|
| U1 guillotine-local | 12× FROZEN | VIABLE (longs 0) | 0–1 |
| U2 square-greedy-local | 12× FROZEN | VIABLE (longs 0–2) | 0–1; P2: 6–29 local repairs, support pinned |
| U0 swap-drift | 2 DEAD, 7 WEAK-unreplicated, 3 MIXED-replicated* | MELTS (longs 50–71% by t=200, t₉₀≈7) | ~1.3–5.9×10⁵ |
| U3 square-Metropolis T=20 | 1 DEAD, 6 WEAK, 5 MIXED-replicated* | MELTS (t₉₀≈10–11) | ~1.3–5.7×10⁵ |
| U4 reloc-drift | 12× FRAGMENTS (+2 L64) | FRAGMENTS (16/16 runs disconnect) | ~6–31×10³ |

\* All MIXED-replicated cases diagnosed individually (§4); none is
far propagation. Pc-u5 × U1 (nonlocal damage, labeled calibration):
FROZEN + VIABLE at all L (1–3 accepts; local partners cannot even
repair visible damage, let alone carry).

## 2. Channel findings

- **Span channel (U1): DEAD.** Pristine J₂ has every edge at span
  exactly 3; local damage (1–40 swaps, hole4, single deletions,
  star8) creates 0–2 longs — the span observable is blind to any
  local disturbance. U1 accepts ~0 in 200 sweeps; support ≡
  footprint (R=1 incident field bit-identical at t=0 vs t=200).
  Even with VISIBLE (nonlocal) damage it manages 1–3 local repairs.
  Locality costs the banked guillotine all its power.
- **Motif-greedy channel (U2): DEAD.** Pristine J₂ is a strict local
  C4 maximum (every probed local swap destroys 22–42 touched
  squares); control legs accept EXACTLY 0 across all seeds and L.
  On burst (P2) damage it finds 6–29 strictly-local C4-up repairs
  (boundary FROZEN by the preregistered <20-mean rule, disclosed)
  with support pinned at r ≤ 5.
- **Drift channel (U0): fades in place, then melts.**
  Strongest cell (P2×L42): bump 0.23 → θ by t≈30, peak PINNED at
  r ≤ 1, half-mass 2 → 4 by t=2 then noise; no traveling peak, no
  expanding ring at any (P, L). Far max-r crossings are
  unreplicated single-shell flukes (split halves disagree on r by
  4–12 and on pattern). Meanwhile the vacuum melts (background
  D 0 → 2.43, t₅₀≈2.3, t₉₀≈7; span background avalanches 0.09 →
  0.55 over t=2–5): U0 is not a viable vacuum law regardless.
- **Thermal-motif channel (U3): ≈ U0.** T=20 accepts ~81%
  (≈ ungated); verdicts, melt (t₉₀≈10–11, slightly slower), and
  bump physics match drift. The C4 bias buys nothing for carrying.
- **Relocation channel (U4): destroys the substrate in ~5 sweeps.**
  Diagnostic probe (L=42): degree-std 0 → 1.9 (t=1) → 6 (t=5) →
  36 (t=200); isolated nodes 0 → 244 (t=5) → 1516/3528 (t=200);
  hubs to d≈720 (slot-walk proposals rectify into preferential
  attachment). Excluded from fronts per prereg (16/16 disconnect);
  not a vacuum dynamics.

## 3. Secondary findings (all replicated)

- **Fiber memory hierarchy** (late uniform ΔD̄, L42×U0, t=200):
  P4 (E−4): −0.0069 ± 0.0003; P3 (degree defect): −0.0013 ±
  0.0004; P1/P2 (same fiber): 0.0007/−0.0002 ± 0.0003 (≈ 0).
  Different-fiber defects leave permanent k=0 offsets (not
  propagation — no r-structure); same-fiber ripples are transient.
- **Cavity signal** (P4×U0): late NEGATIVE bump at r ≤ 2 (−0.056,
  L-independent, stable t=60–200): the hole region melts LESS than
  background (constrained local kinetics). Sign flip: early +0.03
  (damage vs pristine) → late −0.056 (order vs melt).
- **Micro-transport** (strongest cells only): bump flank reaches
  r ≈ 7–8 at t ≈ 1–2 (L28 P2×U3: r=7, 4 snaps, θ-robust to 0.002,
  half-pattern corr 1.00). Within single-hop observability reach
  (~R_prop + R_obs + re-pairing ≈ 10, cf. coupling-test bound);
  peak pinned; fades with the bump. Real diffusive edge transport,
  too weak/slow to matter (mixing wins immediately).
- **L-scaling**: r_max "growth" with L is a max-r artifact (more
  cells → farther flukes); replicated reach does not grow with L
  (L=64 confirms: same pinned bumps, wandering far noise).

## 4. Diagnosed MIXED-replicated cells (all non-propagation)

- L20 P3×U0 (t=22, r=10=wrap, full-range run): fiber-offset onset.
- L28 P1×U0 (t=125, r=8) / L42 P1×U0 (t=85, r=7–8): slow-k0
  fluctuations (single snapshots, small run).
- L28 P2×U3 (t≈1, r=7×4): micro-transport (§3).
- L28 P4×U3 (t=2.25, r=8): bump + fiber onset (corr 0.997).
- L42 P1×U3 (t=6, r=14/12): REJECTED — halves opposite patterns
  (corr 0.35), no single-seed driver, inverse dose (P2 silent).
- L64 P4×U0 (t=60/85, r=21–32): REJECTED — corr 0.993 is
  center-dominated (cavity −0.056); far maxima wander r=15–32
  across snapshots (noise); positive mass scales with area (noise
  floor × area) while negative mass is L-independent.
- L42 P2/P4×U0/U3 (t=155 etc.): single-snapshot halves-r
  disagreement ≥ 4 → flukes.

## 5. Estimator lessons (A2 post-hoc, uniformly applied)

Raw max-r front over ~3000 (t,r) cells has multiple-comparisons
bias (3σ-per-cell insufficient): inverse dose-response (P1
out-reaches P2) and wrap-hitting flukes. Hardening: split-half
same-t replication + same-(t,r) ± 2 + pattern correlation +
θ-band {0.0005, 0.002}. Prereg max-r + gated fronts kept in
output for the record (`scripts/analyze_grav0.py` prints both).
Coupling validated throughout: U1/U2 far-field ≡ 0 (exact null);
per-seed σ ~ 0.01–0.06 (vs O(1) uncoupled).

## 6. GRAV-1 implications

- The viability–carrying tension is the result: viable laws
  (U1/U2) are frozen; carrying laws (U0/U3) melt; U4 fragments.
  A viable carrying law needs damage-gating that SEES local J₂
  damage (span/C4-greedy do not) — a D1 target, not a GRAV-0
  invention.
- Deliverable for GRAV-1: the propagator kernel is effectively
  LOCAL + TRANSIENT (pinned bump, ~30-sweep life, no far field);
  any K_A → δG → K_B mechanism must work with (or fix) that.
- Filed, not attempted: source→detector coupling (no
  matter-response law exists); gated-but-seeing U design.

## 7. Campaign record

1152 paired runs (2304 trajectories, ~10⁹ local updates): main
3L × 4P × 5U × 16 seeds (T=200, A1.1 dense-early grid); Pc-u5 ×
U1 × 3L × 16; secondaries (L42 × 20 cells × 4 seeds);
L64 × U0/U4 × P2/P4 × 16. Data: beast `~/grav0-data/`
(main/cal-pcu5/sec/L64); analysis `scripts/analyze_grav0.py`.
Figures: `figGRAV0_surface_U0P2L42`, `figGRAV0_fronts_L42`,
`figGRAV0_bumpdecay_L42`. Module `src/bh_graph/grav0.py`, tests
`tests/test_grav0.py` (11 pins), runner `scripts/run_grav0.py`.
