# Vacuum/curvature derivation attempt — report (Phases 0–2)

**Preregistration:** `docs/derivation-prereg.md` (committed BEFORE any vacuum
computation; all bars below are quoted from it, not fitted to results).
**Artifacts:** `results/vacuum/*.json` (exact backend unless labelled).
**Code:** `src/bh_graph/vacuum_*.py`; **tests:** `tests/test_vacuum_*.py`
(21 tests, all passing) + full suite green (see §7).
**Compute spend:** $0 (CPU-only; campaign wall time 977 s single-threaded).

**Epistemic labels** (mandatory per `docs/model.md`): every number below is
tagged derived / fitted / assumed / measured / exploratory / conjectured.
C1/C2/C3 entered as CONJECTURE and remain so (see §5 for exactly what moved).

---

## Verdicts at a glance

| Test | Bar (prereg) | Result | Verdict |
|---|---|---|---|
| (i) κ=0 on unperturbed vacuum, all families | max\|κ\|<1e-6 at 2 sizes | all 4 fams ≤3.4e-16 at all sizes | **PASS** (measured) |
| (ii) C1 log-form emergence | log ΔBIC>10 vs power+linear on ≥2/3 fams + base absorption | 0/9 stacked fits yieldable (<4 neg bins) | **INCONCLUSIVE** (structural: exact zeros beyond r≤3) |
| (iii) p recovered without tuning | \|p−0.92\|≤0.056 AND R²>0.7, same protocol, ≥2/3 fams | best clean fits p≈1.5–1.7, R²≈0.6; E1 nan | **NOT-RECOVERED — kill** (successful kill, not failure) |
| D3 N-scaling (vacuum graphs) | exploratory: p(N) to N>1020 | E2 p≈1.5–1.7 flat N=250→1728, never near band | N-robust kill (not BU-wire pressure — different graph class) |
| A. LIV null | FAIL iff predicted 31-GeV delay exceeds bounds | 5.8e-19 s vs ~1 s window (18.2 orders) | **PASS — null held** |
| C. Echo null | margin + LVK nulls consistent | 159.9 orders; LVK nulls stand; real-strain leg descriptive | **PASS — null held** |
| B. 2PN gate | gate-only, <3σ = not-inconsistent | fitted p: 0.10σ/0.06σ; phase-1 leg omitted (no invented p) | **CONSISTENCY-GATE held** (never validation) |

**Protocol deviations:** NONE. No third excursion protocol, no masking
change, no bar change, no reweighting (see §6 for the full deviation audit
including cases where deviation was tempting and refused).

---

## §0. Phase 0 — grounding audit (summary; full table in prereg §0)

All theoretical targets were tabled with repo file + symbol + `docs/model.md`
v0.4 status BEFORE use. Landmine verification outcomes:

- `R_s = 2M` is D6-open (BM reduction; `horizon.schwarzschild_rs` is THE
  single GR input) — CONFIRMED, never used in Phase 1.
- Kerr quadrupole D2/S3-open, future wire (`supplement.tex` S1/S3, GW241011
  δ_Q + GW250114 QNM) — CONFIRMED; no Kerr/overtone claims anywhere here.
- Horizon-pop threshold: CONFIRMED with naming correction — the symbols are
  `micro.critical_k` (=12.566… float) / `micro.packing_kmax` (=12 int),
  downstream of `horizon.PATCH_AREA = 4ln2`; no `k_crit` symbol exists.
- `p = 0.913 ± 0.049` (SEM 0.0055, n_ok 80) re-read from
  `data/p80_n1020_beta124.json` — CONFIRMED FIT (F1/F2 fitted upstream);
  N=4k/8k/16k means 0.9315/0.9382/0.9137 with per-N recalibrated β.
- `κ→c₂` map `c₂(p)=p(2p−1)` is ansatz F4, D3 open (power-law R² 0.91 vs 1/r²
  0.81, cross-applied c₂ disagreement) — CONFIRMED; never used as input.
- T-o correction: code gives `echo_margin_orders = 159.88`, not "≈158"
  (task brief stale by ~2 orders — code wins per model.md convention).

C1 (log-κ), C2 (regular vacuum), C3 (vacuum selection): ABSENT from
`docs/model.md` → CONJECTURE, out of validation scope. P4 is
measure-uniformity, NOT degree-uniformity (no support for C2). The
Kelvin/Weaire-Phelan analogy stays motivation-only (circular
pre-geometrically); BCC(k=8) ≠ Kelvin-dual(k=14) enforced in code
(`test_builders_k_regular_and_counts`); A15 EXCLUDED (no code written).

---

## §1. Phase 1 — derivation attempt

### §1.1 Families built (prereg §1, exact)

Genuinely k-regular PBC graphs, regularity ASSERTED in code:

| Family | k_vac | Construction | Sizes run (L→N) |
|---|---|---|---|
| Cubic (SC) | 6 | L³, ±x/±y/±z bonds mod L | 6→216, 8→512, 10→1000, 12→1728 |
| BCC (NN) | 8 | 2 atoms/cell, 8 (±1,±1,±1) bonds | 5→250 … 9→1458 |
| FCC (NN) | 12 | even sublattice of Z³_{2L}, 12 NN bonds | 4→256 … 7→1372 |
| Kelvin dual (stretch) | 14 | BCC sites + 8 NN + 6 NNN bonds | 5→250, 6→432, 10→2000 |

Wrap control: shell-count isometry vs the infinite lattice (a first,
lifted-coordinate check was found VACUOUS in smoke testing and replaced
BEFORE the campaign — the fix is in committed code, the rule is the
preregistered one). Measured r_max: cubic L/2−1 (5 at L=12); BCC L−1
(7 at L=8); FCC ≈L−1 (6 at L=7); Kelvin wraps early (r_max=2–3 at L≤8 →
grew to L=10/N=2000, r_max=4, per the preregistered grow-L rule).

### §1.2 Test (i): κ = 0 on the unperturbed vacuum — PASS (all families)

Exact backend (transportation LP + sparse Johnson, P4 uniform measure),
50 seeded edges per family×size:

| Family | max\|κ\| (all sizes) | Verdict |
|---|---|---|
| Cubic (L=6,8,10) | 1.1e-16 | PASS (3/3 sizes) |
| BCC (L=5,6,7) | 0.0 exactly | PASS (3/3) |
| FCC (L=4,5,6) | 2.2e-16 | PASS (3/3) |
| Kelvin (L=5,6) | 3.3e-16 | PASS (2/2) |

All four vacuum families are Ollivier-flat to machine precision —
MEASURED (given P4+I6b), including triangle-containing FCC and k=14
Kelvin. This is a measured regularity, NOT a C3 derivation (no selection
principle was tested). It does remove a conceivable C2 objection (vacuum
candidates need not be non-flat to be interesting — all are flat).

### §1.3 Test (ii): excursion profiles + form comparison — INCONCLUSIVE

Excursions E1 (hub-plus, Δ∈{2,4}) / E2 (shell-plus) applied exactly as
preregistered; stacked profiles over seeds {0,1,2} (means, exact backend):

| Setting | r=1 | r=2 | r=3 | r≥4 | Neg bins |
|---|---|---|---|---|---|
| SC E1 (Δ=2,4) | −0.63/−0.97 | −0.07/−0.10 | 0 (exact) | 0 (exact) | 2 |
| SC E2 | −0.39 | −0.40 | −0.061 | 0 (exact) | 3 |
| BCC E1 | −0.60/−0.90 | −0.04/−0.07 | 0 (exact) | 0 (exact) | 2 |
| BCC E2 | −0.36 | −0.33 | −0.045 | 0 (exact) | 3 |
| FCC E1 | −0.42/−0.69 | −0.03/−0.04 | ~0 (2e-16 noise) | ~0 | 2 |
| FCC E2 | −0.27 | −0.28 | −0.036 | ~0 | 3 |
| Kelvin E1/E2 (L=10) | −0.37/−0.23 | −0.02/−0.26 | +2e-16/−0.032 | ~0 | 2/3 |

Form comparison needs ≥4 negative bins (prereg §2.3): **0 of 9 core
settings yieldable → INCONCLUSIVE on the preregistered bars** (all three
settings `E1/d2`, `E1/d4`, `E2/d2` return `only-0-ok-fits`).

The CAUSE is measured and structural, not a power issue: the κ
perturbation is confined to r≤2 (E1) / r≤3 (E2) with EXACT zeros beyond
(cubic/BCC: literally +0.0 on every far edge; FCC: ±2.2e-16 LP noise).
Ollivier curvature is local (1-neighborhoods + their pairwise distances),
so a degree excursion of radius R_exc perturbs κ only to ≈R_exc+2 —
measured exactly. **C1's presupposition (multi-bin κ scaling under
localized degree excursions) FAILS on E1/E2** — recorded as wire pressure
against C1's domain, NOT as a preregistered form kill (the verdict stays
INCONCLUSIVE per the bars; upgrading it without a bar would be the same
sin as rescuing without one).

Sign-mixture honesty (supplementary `spreads`, fits use means per prereg):
E1 r=1 bins are uniformly negative (frac_neg=1.0); E1 r=2 is sign-MIXED
(frac_neg≈0.39–0.40); E2 r=1,2 uniformly negative; E2 r=3 mixed
(frac_neg≈0.22–0.33, max\|κ\| 0.12–0.24). The BU pipeline also fits means,
so comparability stands — but the r=2/3 means average over mixed signs.

### §1.4 Test (iii): p-recovery — NOT-RECOVERED (kill)

SAME `orici.fit_scaling_power` metric as BU (no constant adjusted to match
p — protocols contain no κ-dependent parameter):

| Setting | p ± p_err | R² | Hit? (\|p−0.92\|≤0.056 AND R²>0.7) |
|---|---|---|---|
| E1 (all fams, Δ=2,4) | nan (2 bins) | nan | NO |
| SC E2 | 1.513 ± 1.224 | 0.604 | NO (misses by 10× tolerance; R²<0.7) |
| BCC E2 | 1.714 ± 1.267 | 0.647 | NO |
| FCC E2 | 1.630 ± 1.351 | 0.593 | NO |
| Kelvin E2 | 1.568 ± 1.414 | 0.552 | NO (stretch, same pattern) |

**Verdict: NOT-RECOVERED** — "p not recovered" is a SUCCESSFUL kill, not a
failure. Notes: (a) the ±1.2–1.4 errors are 3-point-fit widths — the bar
requires a HIT, and an unconstraining error bar is failure-to-hit, not a
hit; (b) the E2 profile shape is flat-then-cliff (r=1≈r=2, cliff at r=3),
so power-law is descriptively poor (R²≈0.6) before any band comparison;
(c) no setting is within 0.5 of the band (nearest miss: 1.513 vs 0.976
band top).

**Masking-noise artifact (diagnosed, NOT patched):** 4 scaling fits
(fcc/L5/E1, fcc/L5/E2, fcc/L6/E1, fcc/L6/E2) plus fcc/L7/E1/d4 return
spurious p≈22–33 (R² 0.47–0.89): the κ<0 mask admits a machine-noise bin
(stacked mean −7.7e-19 at fcc/L7/E1/d4/r=6; edge max\|κ\|=2.2e-16 = eps).
Patching the mask (e.g. κ<−1e-12) post-hoc is FORBIDDEN by the prereg
("no post-hoc masking changes") and was refused — the artifact changes no
verdict (p≈22–33 is not a hit with or without the noise bin). It is
reported here so no reader mistakes it for signal.

**D3 N-scaling (beyond N=1020):** E2 p(N) is flat-and-outside:
cubic 1.520→1.513 (N=1000→1728); BCC 1.713→1.590→1.652→1.714→1.740
(N=250→1458); FCC clean point 1.630 (N=1372). No N approaches the band —
the kill is N-robust to N=1728. (This is kill-robustness, NOT D3-wire
pressure on BU: different graph class, stated explicitly.)

**Sinkhorn cross-check (labelled, bcc/L6/E2):** VALUES agree (bias
−2.8e-4 at eps=0.05, ~1e-9 at eps=0.01; direction κ_sink≤κ_exact
confirmed) but DERIVED p is garbage under Sinkhorn (p=6.08 at eps=0.05
via systematic −4.6e-05 fake-negative bins; p=22.2 at eps=0.01 via
−1e-15 bins). This validates the prereg choice of exact backend for
verdicts and independently confirms the masking-noise diagnosis.

---

## §2. Phase 2 — gated protocols

### §2.1 Protocol A — LIV null (Fermi) — PASS (null held)

Mock-first: frozen statistic (E²-slope + analytic delay31) is QUIET at
model scale (slope 4.7e-06 vs jitter floor 4.4e-04) and FIRES at the
excluded scale 1e10 GeV (slope 7.2e-03 > 5×floor) — the statistic has
power where it must. Real leg (published bounds, Abdo+2009 — no raw
HEASARC download needed): predicted 31-GeV delay over 7 Gpc = **5.81e-19
s** vs the ~1 s arrival window → **margin 18.2 orders**; Fermi quad-scale
margin 2.7e8; linear term absent by symmetry. Falsification bar
(predicted delay exceeds bounds): not triggered → **PASS**.

### §2.2 Protocol C — Echo null (GWOSC) — PASS (null held)

Mock-first: frozen excess-power statistic FIRES on detectable injected
echo (13.1 > 5.0) and stays QUIET at model level (0.02) — power
demonstrated. Analytic verdict: **margin 159.9 orders** (echo energy
~1e-160 vs 0.01 detectability); LVK O3 BayesWave + template nulls stand
(Abbott PRD 112 084080; Uchikata PRD 108 104040) → **PASS**.
Real-strain leg (GWOSC reachable; 4×32 s 4 kHz snippets downloaded):
frozen statistic at frozen delay +0.3 s gives 0.93 (150914/H1),
364 (150914/L1), 23.6 (190521/H1), 23.1 (190521/L1) — the three FIREs
are a DEMONSTRATED artifact (unwhitened DC ~1e-19–1e-18 + asymmetric
demeaning: signal mean-square keeps DC², background variance removes it;
post-hoc symmetric var/var: −0.89, 3.22, 3.40, 3.87 — all QUIET <5.0).
Rule fixed BEFORE download: data-leg numbers are descriptive-only, the
toy statistic (white-noise-mock-validated) has no veto over LVK
pipelines, verdict stays margin-driven. No Bilby. No overtones (D2-open).
Numbers + provenance in `results/vacuum/phase2_echo_real.json`;
limitation noted comment-only in `vacuum_echo.py` (zero behavior change).

### §2.3 Protocol B — 2PN gate (Double Pulsar) — HELD (gate-only)

Published anchors verified against `pulsar.py` (J0737 ω̇=16.899323(13),
sin i=0.99974; B1913 ω̇=4.226598). No TOA re-timing. Fixed-M gate at
FITTED p=0.913: J0737 0.10σ, B1913 0.06σ — not-inconsistent (reproduces
the model.md <0.1σ resuscitated number). Phase-1 leg OMITTED (p not
recovered → no invented p; `phase1: null` in JSON). Label:
**CONSISTENCY-GATE, never validation** (circularity acknowledged: the
gate checks the graph-fit→GR-matching chain for self-consistency, and a
fitted-p gate passing is expected of a self-consistency check, not
evidence for the model).

---

## §3. Theory status updates (what moved, what didn't)

- **C1 (log-κ emergence): remains CONJECTURE.** Form verdict INCONCLUSIVE
  (no yieldable comparison); presupposition (multi-bin scaling) fails on
  E1/E2 (exact zeros). C1 is neither derived nor killed on bars — but its
  domain now has a measured hole: NO localized degree excursion of radius
  ≤1 produces the multi-bin profile C1 presupposes. A future C1 revival
  would need preregistered R_exc≥2 excursions (explicitly NOT run here —
  "no third excursion protocol" refused as rescue).
- **C2 (regular vacuum): remains CONJECTURE** (regularity was assumed in
  construction; test (i) measures flatness conditional on it, nothing more).
- **C3 (vacuum selection): remains CONJECTURE.** All four candidates are
  OR-flat, so flatness does NOT select among them (exploratory observation).
- **D2/D3/D6: stay OPEN.** No derivation of Kerr multipoles, the κ→c₂ map,
  or R_s=2M was attempted or smuggled.
- **BU pipeline untouched:** the fitted p=0.913 ± 0.049, F1–F4, and all L2
  claims stand exactly as fitted — this attempt neither promotes nor
  disturbs them (a failed derivation leaves the fit a fit).

---

## §4. Files

- `src/bh_graph/vacuum_graphs.py` — PBC builders (SC/BCC/FCC/Kelvin),
  shell-count wrap control, E1/E2 excursions, radial bins.
- `src/bh_graph/vacuum_curv.py` — exact-κ profiles, log/power/linear
  comparison (R²/AIC/BIC), base-absorption, verdicts, stacking.
- `src/bh_graph/vacuum_liv.py`, `vacuum_echo.py`, `vacuum_pulsar.py` —
  gated Phase-2 protocols (mock-first, frozen statistics, gate labels).
- `src/bh_graph/vacuum_run.py` — campaign runner (`--outdir`).
- `tests/test_vacuum_{graphs,curv,phase2}.py` — 21 tests.
- `results/vacuum/{phase1_test_i,phase1_profiles,phase1_scaling,phase1_kelvin,phase1_sinkhorn_xcheck,phase2,phase2_echo_real,verdicts}.json`.

---

## §5. Deviation audit (prereg integrity)

| Temptation | Action taken |
|---|---|
| Add E3 (2-ball) excursion to gain lever arm | REFUSED (prereg: "no third excursion protocol") |
| Patch κ<0 mask to kill fcc p≈22–33 artifacts | REFUSED (prereg: "no post-hoc masking changes"); diagnosed instead |
| Upgrade C1 INCONCLUSIVE→FAIL on zeros | REFUSED (no bar); presupposition failure recorded separately |
| Downgrade p kill on 3-point-fit widths | REFUSED (bar is on point+R²; widths reported honestly) |
| Change frozen echo statistic post-data | REFUSED (behavior frozen); symmetric variant post-hoc only |
| Kelvin L≤8 r_max<4 | GREW to L=10 — preregistered rule, not a deviation |
| "≈158" vs 159.88 echo margin | Code wins (159.88), divergence flagged (model.md convention) |
| Standalone "X proves/validates Y" physics claims | None made; gate labelled gate-only, nulls labelled nulls-held |

---

*One-line record: vacuum OR-flatness measured on 4/4 families; C1-form
untestable on localized excursions (exact zeros — presupposition fails);
p-recovery killed (1.5–1.7 vs 0.92 band, N-robust); LIV + echo nulls held
with 18/160-order margins; 2PN gate held as gate-only. Zero deviations,
zero dollars.*
