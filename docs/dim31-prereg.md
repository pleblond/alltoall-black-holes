# DIM31-PREREG — Dimension-General Operational Estimators (FROZEN PRE-J3)

Campaign: DIM-3-1. This document predates ALL DIM-3-1 J3 headline
measurements. No J3 operational-dimension, arrival-law, static-profile,
or station measurement has been run under this prereg. Control
measurements (known-dimensional families) run AFTER this freeze and set
the numeric bars recorded in `docs/dim31-freeze.md`; the J3 blind seal
(`data/dim31_seal.json` + sha256) is written after the freeze record and
before any J3 cell runs.

Mission (from `DIM-3-1.tex`): repair the operational dimension
instruments falsified by DIM3-GEOMETRIC, using only
mechanism-derived corrections validated first on
known-dimensional controls.

## 0. Frozen inputs (read-only)

- DIM3-GEOMETRIC verdict + `data/dim3_diagnosis.json` mechanism
  aggregates (gamma ~ 1.48 supralinearity, d* cap at 2, P-range
  compression) — repair TARGETS, never calibration inputs.
- `src/bh_graph/dim3.py` + `src/bh_graph/dim3_reveal.py` (J3 apparatus,
  Krylov/CG instruments) vendored verbatim from the DIM-3-0 branch.
- OBS-0R / OBS-1 / QUOT-0 estimator apparatus (`obs0.py`, `obs1.py`,
  `obs0r.py`, `analyze_obs1_blind.py`) — frozen, imported, never forked.
- RESPONSE0-KERNEL + ANATOMY (`response.py`), VAC0-MIXED verdict
  (consumed banked), banked 2D J2/square controls, known-3D cubic
  control.
- H/I ports (sector/hidden/vacuum) consumed banked from DIM-3-0 (passed
  there; unaffected by estimator repair; not re-run).

## 1. Hard firewall

All estimator formulas, bars, and calibration rules are frozen using
analytic derivation and/or known-dimensional controls before the J3
headline reveal. Forbidden: choosing a rule because J3 reads 3; moving
a bar after J3 reveal; using J3 labels in estimator fitting; discarding
a control that fails the desired result.

Quarantine (procedural breach remediation, pre-campaign exploratory
context viewed old J3 station-level records): old
`dim3_blind.json` cells 0-2 (J3 station-level data) are FORBIDDEN for
all freezing decisions in this campaign. Allowed J3 inputs before
reveal: published diagnosis aggregates only (cited values in
`data/dim3_diagnosis.json`). This quarantine is enforced by NOT
vendoring `dim3_blind.json` into this branch and by fresh blind
cells/sizes/seeds below. No window, floor, k, or bar judgment from
pre-campaign exploration is carried forward as frozen; every number in
the freeze record must cite a derivation or a control record from the
DIM-3-1 control battery.

"Fitting" vs "measuring" (auditable interpretation, frozen here):
fitting = setting a free parameter, bar, window, or formula choice
using J3 data (forbidden). Measuring = applying the frozen protocol
verbatim to J3 data to obtain a protocol-defined input (allowed, and
filed as reveal-side where hidden geometry is used). Headline verdict
legs use blind inputs only (transfer legs); reveal-side direct legs
are validation, never headline.

## 2. Estimator A — arrival-dimension correction (spec A, B)

Mechanism (banked diagnosis): fixed-threshold arrival times are
supralinear, M(r) ~ r^gamma, so the arrival-time volume scales as
V(T) ~ T^{d/gamma} = T^alpha, and the blind volume slope alpha reads
d/gamma instead of d. Corrected estimator:

```text
d_arr = alpha * gamma
```

- alpha: `obs1.volume_dimension` slope on the station arrival matrix
  (blind; per channel W/D and composite C; frozen quantile window,
  r2 >= 0.85 gate inherited).
- gamma: arrival-law exponent from median arrival per integer
  hidden-radius bin, log-log OLS (`obs0.fit_loglog`).

Gamma protocol (frozen; applied to controls pre-reveal, to J3
post-reveal for the direct leg only):

```text
bins r = 4..floor(D/2)-1 (D = intrinsic diameter, obs0.hausdorff_window)
median per bin over arrived nodes; bins with median < 4*DT or < 3 nodes dropped
UNMEASURABLE if < 4 bins survive or r2 < 0.85 (VOL_R2_BAR, inherited)
```

Radius = hidden quotient metric (Manhattan on quotient cells: cubic
cells; J2 quotient; J3 quotient; ring/square graph distance). Small
cells that cannot support 4 bins are UNMEASURABLE (expected, not a
failure — Amendment-1 A5 precedent).

Theta rule (spec B): station W uses absolute THETA_WAVE = 1e-6
(frozen OBS-1 instrument, verbatim). Gamma is measured at the decade
ladder {1e-5, 1e-6, 1e-7} on controls; transfer requires gamma stable
across the ladder (spread < tol_gamma_ladder, frozen from controls).
The ladder also files the threshold/group separation: front speeds
per decade (expected theta-dependent) vs packet speed (expected
Bloch, theta-free). The dimension estimator NEVER identifies a
fixed-threshold front with the Bloch/group speed.

Transfer leg (blind headline): gamma_J3 := gamma_cubic at matched
linear size L (pooled over sizes if T1 passes) and matched ladder
level, justified by the EXACT Stage-A
intertwining (H.U = U.H_Q with H_Q = -2J.A_cubic): J3
symmetric-sector wave physics IS cubic wave physics at doubled
hopping, the antisymmetric sector is exactly dead, and gamma is a
dimensionless exponent invariant under the J rescaling. Micro/UV
differences are excluded by the r >= 4 window. Transfer validity
requires (all pre-reveal, on controls): (T1) cubic gamma stable
across the size ladder (spread < tol); (T2) ladder-stable per above;
(T3) 2D regression (below) passes with family-own gamma.

Direct leg (reveal-side validation): gamma measured on J3 with the
frozen protocol post-reveal; agreement |d_arr_direct - d_arr_transfer|
<= tol_agree (frozen from control spread) required. Disagreement is a
filed apparatus red flag (transfer invalidated), not a retune trigger.

2D regression (spec I): d_arr on J2/square with family-own frozen
gamma must read 2 within tol (frozen: |d-2| <= max(0.25, 2*spread)).

## 3. Estimator C — local-ball d* rule (spec C)

The old global majority-distortion rule is structurally capped at 2
(proven diagnosis) and is filed descriptive-only in this campaign
(never gated). Replacement: blind local-ball MDS ladder.

Protocol (frozen; input = completed station matrix, channels W/D/C;
P excluded — static range compression distorts local geometry,
diagnosis mechanism):

```text
per station a: ball = {a} + 16 nearest neighbors (frozen k = 16)
MDS into d = 1, 2, 3; stress_d(a) = normalized raw stress
S_d = median over stations of stress_d
d* = smallest d in {1, 2, 3} with S_d < bar_d; else REFUSE
```

Rationale: local balls resolve intrinsic dimension (ring balls are
linear; disk balls embed in 2D; 3-ball needs 3D) while global stress
is wrap-dominated on all families. k = 16 frozen (single value; no
ladder tuning). LINEAR_FLOOR logic is subsumed: bar_1 plays its role.

Bar freezing (from the DIM-3-1 operational control battery,
recorded in `docs/dim31-freeze.md`): bars must satisfy, with >= 1.3x
margins on both sides,

```text
ring S_1 < bar_1 <= min over {sq, J2, cb, ex} S_1
sq,J2 S_2 < bar_2 <= min over {cb, ex} S_2, and sq,J2 S_1 >= bar_1
cb S_3 < bar_3 <= ex S_3, and cb S_2 >= bar_2
```

If no such bars exist on any channel, the estimator is in
ESTIMATOR-DEBT (verdict path, section 9) — controls are never
dropped. Bars frozen per channel (W/D/C may differ); headline
channel = composite C, W/D filed as legs. Expanders must REFUSE
(all S_d above bars). Ring must claim 1 (local linearity — this is
the supported d = 1 path; global MDS cannot return 1 on periodic
data since S^1 embeds extrinsically in 2D — filed apparatus fact,
not tuned).

Headline gate: d* = 3 on J3 with train/test replication (same
32/32 split rule; both halves claim 3).

## 4. Estimator D — xi-aware static readout (spec D)

The old P-volume readout is falsified (reads 4-8 via range
compression) and is filed descriptive-only (never gated). Replacement:
direct Yukawa dimension from the joint (amplitude, decay, range) fit,
which IS xi-aware (fits xi simultaneously rather than ignoring range):

```text
phi(r) shell medians -> obs0r.fit_yukawa -> (A, alpha, xi)
d_stat = 2*alpha + 1
```

Protocol (frozen): Euclidean quotient shells r = 2..min(10, Rsafe),
median of positive phi per shell, `fit_yukawa` (log-linear OLS
ln phi = c - alpha ln r - r/xi); UNMEASURABLE if fit ok = False or
r2 < 0.9 or n < 4; solver-floor rule: shells with median phi < 1e-10
dropped (unreliable far field). Mechanism map alpha = (d-1)/2 is the
far-field Yukawa radial law (continuum; lattice corrections filed
per-control).

This channel is reveal-side by nature (shells need coords) and
J3-untuned by freeze: no blind static estimator is claimed
(P-range compression destroys blind radius information — diagnosis
mechanism). Range-compression validation (pre-reveal, on controls):
gap ladder omega = -(z+delta), delta in {0.25, 0.5, 1.0} on cubic:
(xi) xi(delta) scaling filed; (P) predicted P-range
delta_r/xi + alpha ln(ratio) must reproduce measured P-range within
tol_Prange (frozen from controls). Expanders: fit must refuse
(ok = False or r2 < 0.9 or alpha outside [0, 2]) — no dimensional
claim on non-geometric graphs.

## 5. Metric / spreading legs (spec G support)

- Local-chart dimension (reveal-side): smallest d with median k = 8
  ball chart eps <= LOCAL_ALIGN_BAR = 0.30 (inherited bar, never
  retuned; `dim3_reveal.local_chart_report3` for 3D cells,
  2D analog for J2/square). Expected: 3 on cubic/J3, 2 on J2/square.
- Spreading (reveal-side, banked apparatus): far-shell interior-peak
  fits (Amendment-1 A1 rule verbatim) on J3-L20+ and cubic controls;
  filed exponent windows inherited (psi [0.80, 1.20], rho/J
  [1.70, 2.30]) as the 3D-law check; near-field-only (n < 4) legs
  UNMEASURABLE, never gated.
- Packets (G-a verbatim protocol): Bloch-speed + reversal check on
  J3/cubic/J2 (spec B control).
- Threshold ladder on stations (blind-safe, no coords): W at three
  decade levels; files front-speed ladder + gamma ladder.

## 6. Control battery (unblind calibration; known-dimensional)

| family | sizes | N | role |
|---|---|---|---|
| ring (1D) | n = 256, 512 | 256, 512 | d = 1 leg; refusal-shape control |
| square torus (2D) | L = 32, 48 | 1024, 2304 | 2D regression |
| J2 (2D J-structure) | L = 28, 42 | 1568, 3528 | 2D regression with fiber (L42 banked bridge) |
| cubic torus (3D) | L = 12, 16, 20 | 1728, 4096, 8000 | known-3D; transfer donor; identity partner |
| expander 12-reg | N = 1024 (s0, s1), 3456 (s0) | matched | refusal (two seeds at one N) |
| bilayer-cubic | L = 12 | 3456 | observer must NOT merge layers |

Station protocol (frozen, all cells): 64 stations x 3 sets, seed base
13100 + 100*cell + set (never 9100); frozen OBS-1 instruments
(Krylov wave dt = 0.05 Tmax = D; Krylov diffusion dt = 0.25 Tmax =
3(D/2)^2; CG statics rtol = 1e-11, loud convergence; thresholds
THETA_WAVE = 1e-6 both channels). D = intrinsic diameter per cell.

## 7. Blind protocol + size ladder (spec E, F)

Freeze order: (1) this prereg; (2) estimator code `src/bh_graph/dim31.py`
+ tests; (3) control battery runs; (4) `docs/dim31-freeze.md`
(numeric bars + transfer tables + tolerances, each citing a
derivation or control record); (5) seal `data/dim31_seal.json` +
sha256 (J3 cells/sizes/seeds, code hash); (6) J3 blind run; (7)
reveal + verdict. Steps 1-5 precede ANY J3 cell run.

Headline J3 ladder (spec F, larger than DIM-3-0 where feasible):
J3-L16 (N = 8192, bridge) -> J3-L20 (N = 16000) -> J3-L24
(N = 27648). Estimator drift L16 -> L20 -> L24 reported per
channel, not just the largest point. Pre-wrap rules
(r < D/2 everywhere) and solver-floor rules (section 4) hold at
all sizes. If L24 wall-time exceeds the frozen compute budget
(6 h single-cell cap on 4 CPUs), L16/L20 are the headlines and
L24 is filed partial (never gated) — apparatus scope, not
verdict, is reduced.

J3 cells see integer ids only through the blind analyzer; reveal
joins run strictly after the blind artifact hash matches the seal.

## 8. Agreement / identity / regression / negative gates

- Cross-channel (spec G): blind d_arr(transfer), blind local-d*,
  reveal d_stat, reveal chart, reveal spreading. No single channel
  defines the verdict; OPERATIONAL requires joint agreement (section 9).
- Cubic identity (spec H): per corrected channel,
  |d_J3 - d_cb| <= tol_identity (frozen from control spread in the
  freeze record). A J3/cubic split with controls passing is an
  apparatus red flag, not a discovery, unless the preregistered
  intertwining mechanism predicts it (it predicts identity at
  matched relative theta — a split contradicts it).
- 2D regression (spec I): J2/square read 2 on every corrected
  channel that claims dimension (d_arr with own gamma, local-d*,
  d_stat, chart). A correction turning 2D controls into 3D is
  invalid (kills OPERATIONAL).
- Negative (spec J): expanders refuse on all claiming channels
  (UNMEASURABLE/refuse, never a number); bilayer observer-separation
  check inherited (layer contrast bar from QUOT-0 precedent, filed).

## 9. Verdict ladder

- DIM31-OPERATIONAL: corrected independent channels recover
  known-dimensional controls (ring 1 / J2-square 2 / cubic 3 /
  expander refuse) AND blind J3 as 3D, with size-stable agreement
  (drift < tol_drift frozen from controls) and cubic identity held.
- DIM31-GEOMETRIC: direct geometry remains 3D but at least one
  operational channel still lacks a dimension-general estimator
  (control-first corrections fail on J3 while passing controls, or
  a channel stays UNMEASURABLE on J3).
- DIM31-ESTIMATOR-DEBT: control-first corrections fail to produce a
  consistent dimension estimator even on known-dimensional controls
  (bars unfreezable, regression fails, or transfer invalidated).
- DIM31-INCOMPLETE: apparatus/blind protocol fails before
  interpretation (seal broken, solver non-convergence, compute
  budget exhausted pre-headline).

## 10. Interpretation firewall

A 3D operational verdict establishes emergent/observer dimension
within the frozen graph-field apparatus. It does not establish
Lorentz invariance, 3+1 spacetime, GR, or physical space uniquely.

## 11. Derivation log (analytic entries; control entries go to the freeze record)

- D1 (d = alpha*gamma): V(T) = #{tau <= T}; tau(r) = M(r) ~ r^gamma
  => R(T) ~ T^{1/gamma} => V(T) ~ R(T)^d ~ T^{d/gamma}; log-log
  slope alpha = d/gamma. Requires both fits sample the same regime
  (frozen shared window section 2).
- D2 (transfer invariance): J3 sym-sector intertwining exact
  (Stage-A pin); dimensionless exponent invariant under J -> 2J.
- D3 (local-ball resolution): kNN-ball MDS stress probes intrinsic
  tangent dimension; global stress wrap-dominated (OBS-1 Amd notes).
- D4 (d = 2alpha+1): Yukawa far field phi ~ r^{-(d-1)/2} e^{-r/xi}
  (continuum radial law); lattice corrections filed per control.
- D5 (fixpoint NOT used): P-volume rescale-by-xi leaves
  d ln r / d ln P distortion (log term); rejected in favor of D4.
- D6 (ring d = 1 path): local balls linear (s_1 ~ 0); global S^1
  extrinsically 2D — local rule is the supported 1D path.
