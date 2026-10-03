# DIM31 Amendment-2 (POST-CONTROLS, pre-J3): estimator repairs

Status: apparatus-repair amendment. Written after inspecting CONTROL
data only (freeze debt = 34 on the first controls pass). NO J3 data
exists (J3 grid not run; J3 cells/tags still workflow-guarded). Every
repair below cites control evidence + a mechanism; nothing is tuned
on J3. Uniform margin discipline: all numeric margins 1.3x
(`BAR_MARGIN`, frozen).

## A2.1 Battery extension (controls only)

- cb-L24 appended as cell 16 (control): L-matched transfer donor
  and identity partner for J3-L24, removing the pooled-transfer
  fallback at the top size. J3 cells stay 13/14/15.
- pot1 gap ladder extended with delta in {0.05, 0.1, 0.2} (all
  tags): the xi(δ) = m/sqrt(δ) scaling validated on old deltas
  (joint-delta m = 1.01--1.05 cubic/square/ring, 1.40 J2); small
  gaps give xi ~ 2--4.5 for static scale separation (A2.7).

## A2.2 d* headline channel C -> D

Evidence (controls workup): D bars freeze with wide margins
(bar = 0.018/0.028/0.057) and claim 36/36 control sets
correctly (1 ring, 2 square/J2, 3 cubic incl. all sizes) with
9/9 expander refusals. C bar_1 fails (ring max 0.115 vs square
min 0.123, ratio 1.06 < 1.3); W bar_2 fails (2D max 0.069 vs
cubic min 0.054, overlap).

Mechanism: the diffusion (heat-kernel) metric smooths
lattice-scale jitter, giving regime-clean local balls; the wave
threshold metric carries lattice-scale front noise; the composite
mixes metrics of different scalings and distorts local geometry
(ring S1 20x inflated vs D).

Change: headline d* = D channel (frozen bars + set-replication
per Amendment-1). W/C ladders filed descriptive-only, never
gated.

## A2.3 d_arr pairings: W headline only

- D pairing (alpha_D x gamma_Dch) INVALID: reads ~2x true on
  every family (ring 2.1, square/J2 4.0--4.3, cubic 5.0--6.3).
  Mechanism: diffusion threshold-crossing has log corrections
  (heat kernel), breaking the pure-power identity; both fits
  absorb the correction into steeper local slopes, compounding
  in the product. Dropped (descriptive-only).
- C pairing (composite-alpha x wave-gamma) INVALID: reads
  +0.7..1.4 high everywhere. Mechanism: same-metric violation
  (alpha of a mixture x gamma of the wave). Dropped.
- Headline: W pairing = blind alpha_W x transfer gamma-bar
  (A2.4), per-L set-median; direct-leg (own gamma-bar)
  agreement as validation.

## A2.4 Gamma transfer: ladder mean, exact L

T2 constancy falsified: cubic gamma runs 1.62 -> 1.86 over the
two-decade ladder (level-pooled spread 0.149 > 0.10). This is
smooth threshold physics (leading-ramp vs peak propagation),
not noise; a constancy gate tests a property the physics does
not have.

Change: transfer value = ladder-mean gamma-bar(L) = mean over
(W_hi_th, W, W_lo_th) of set-medians, exact L
(cb-L24 removes the pooled fallback).
- T2' gate: level spread <= 0.20 (1.3x control 0.149; bounds
  the averaging error under threshold mismatch).
- T1 (L-spread) descriptive (pooled transfer unused).
- tol_agree (transfer-vs-direct gamma-bar on J3): 1.3x max
  leave-one-out transfer error over cubic L (mechanical).

## A2.5 Spread legs

- j2 gets 2D windows (psi [0.35, 0.65], rho [0.70, 1.30]):
  theory (d-1)/2, d-1; validated j2-L28 psi = 0.500, rho =
  1.000 (n = 9, r2 > 0.9). The 3D windows applied to j2 in
  error (prereg bug).
- J leg descriptive-only everywhere (no derived J-law; banked
  cubic J is L-unstable, 2.01 at n = 3 vs 1.65 at n = 4).
- 3D psi/rho windows unchanged (theory + exact banked
  reproduction on cb-L20: 0.989/1.978).

## A2.6 Tolerances and verdict logic (1.3x discipline)

The W absolute scale carries O(0.9) finite-size bias at small L
(max control |bias| 0.90, cb-L12); the 64-station sampling
precision is ~0.46 (max cubic set-scatter). Honest labeling:
regression = smoke (apparatus sanity), identity/mismatch =
precision (discrimination).

- d_arr(L) = set-median, transfer-based (same instrument J3
  and cubic). Scatter filed.
- tol_identity = 1.3x max cubic set-scatter (~0.60,
  mechanical): |med_J3(L) - med_cb(L)| <= tol, L = 16/20/24.
- tol_regress = 1.3x max control |bias| (~1.17, mechanical):
  |med(L) - dim| <= tol on controls; |med_J3 - 3| <= tol.
- NEW mismatch gate (discriminative): J3 medians must differ
  from 2D medians (J2-L42, sq-L48) by > tol_identity at every
  L (excludes 2D-J3, which the loose absolute gate cannot).
- Drift gate -> descriptive (per-L identity at three sizes
  implies trend match); drift figure filed.
- OPERATIONAL iff: identity (3 L) + absolute + mismatch +
  d* D set-replication + tol_agree + spread psi/rho +
  packet + chart + static (A2.7/A3) all pass. Else GEOMETRIC
  with failures listed; freeze debt -> ESTIMATOR-DEBT.

## A2.6c Correction (2026-10-03, post-controls, pre-J3)

Two deviations between the A2.6 text/implementation and the
frozen mechanical record, corrected here (no J3 data exists;
J3 verdict criteria unchanged):

1. Code gated control DIRECT (own-gamma) set-scatter against
   tol_identity. The amendment specifies "Scatter filed": the
   headline instrument is transfer-based (same instrument J3
   and cubic), and tol_identity calibrates TRANSFER precision
   for the J3 identity/mismatch gates. Holding the direct
   calibration leg (alpha x own-gamma sampling noise, control
   scatter 0.49--0.50 on j2-L42/cb-L20) to headline precision
   is a category error. Gate removed; own_scat now filed in
   the freeze record alongside own_med. The specified control
   absolute gate (|med - dim| <= tol_regress) passes on all
   ten control cells.
2. Informal "~" values in A2.6 (0.46 scatter, 0.90 bias) were
   diagnosis-phase notebook figures, superseded by the
   mechanical record: max cubic transfer scatter 0.320 ->
   tol_identity 0.416; max control |bias| 0.672 (cb-L12) ->
   tol_regress 0.873. The 1.3x rules, not the informal
   figures, bind the J3 verdict.

## A2.7 Static channel: deferred to Amendment-3

Single-delta joint (alpha, xi) fits FALSIFIED on controls:
alpha(R) rises monotonically with window top on every family
(sq -0.27 -> +0.47, cb-L20 +0.83 -> +2.20), no plateau; at
delta = 0.5 (xi ~ 1.5) the Yukawa regime does not exist
(no scale separation anywhere except the trivial ring).
Joint-delta OLS constrains xi (m ~ 1.0) but alpha still
window-dependent. No static bar/window from old-delta data is
carried forward.

Repair path: small-gap data (A2.1, running) for xi ~ 2--4.5
scale separation. Estimator form + windows + regime rule +
expected-UNM table frozen from that data in Amendment-3
(pre-J3 calibration). J3 static xi prior from band theory:
xi_J3(d) = sqrt(2)/sqrt(d) (acoustic m* = 1/4 from the
12-generator edge curvature; fiber-antisymmetric branch
decays in < 1 site) -- a frozen prediction, tested not tuned.
