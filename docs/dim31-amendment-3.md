# DIM31 Amendment-3 (POST-CONTROLS, pre-J3): static regime apparatus

Status: apparatus-repair amendment. Written after inspecting CONTROL
data only (pot1 with A2.1 small-gap deltas). No J3 data exists. The
single-delta joint fits were falsified in Amendment-2 A2.7
(alpha(R) monotone, no plateau at any delta in {0.25, 0.5, 1.0});
this amendment freezes their replacement. Selection among
candidate scales is mechanical (minimax bias on the largest cell
per family class); J3 settings are transferred, never tuned.

## A3.1 Mechanism findings (controls)

- xi(delta) = m/sqrt(delta) validated over six deltas (m =
  1.01--1.05 cubic/square/ring, 1.40 J2 vs band-theory 1.414).
  Ring xi exact to 1% at every delta.
- At delta >= 0.25 (xi ~ 1--2) there is no scale separation:
  UV lattice effects (r <~ 4) overlap the deep-exp regime and
  the power prefactor is unidentifiable (window-dependent alpha
  everywhere except the trivial ring).
- At delta <= 0.1 (xi >~ 3) torus images swamp small cells
  (fitted xi 3x theory on cb-L20 at delta = 0.05).
- Wrap-boundary shells (min-image |coord| = L/2, e.g. cb-L24
  r = 12) carry dual-path enhancement and bias alpha by +0.5;
  excluded by the coord guard below (verified: 4..11 reads
  3.14 while 4..12 reads 3.73).
- Curvature (local-alpha) estimators are noise-dominated (no
  plateaus); window-averaged joint OLS is the stable core.

## A3.2 Frozen apparatus (uniform xi* = 2.0)

- delta* per family class from band masses m (theory: 1.0
  cubic/square/ring/bilayer, sqrt(2) J2/J3): delta* = (m/2)^2
  on the pot1 grid -> 0.25 (rg/sq/cb/bcb), 0.5 (j2/j3). The
  xi* = 2.0 scale reads truth on the largest cell of every
  class (minimax selection; biases <= 0.14).
- Regime window [rlo, rhi], all guards mechanical
  (`dim31.static_regime_window`): rlo = 2 (ring, exact 1D
  shells) / 4 (UV lattice scale); rhi = min over image guard
  (total contamination <= 10% at xi* = 2.0), wrap-distance
  guard (D/2 - 2), coord guard (L/2 - 1). UNM if < 4 shells
  survive (solver floor still applies).
- Fit: existing joint OLS + r2 >= 0.9 + n >= 4, PLUS the
  xi-gate |xi*sqrt(delta*)/m - 1| <= 0.20 (in-situ band-theory
  validation; refuses contaminated fits). d = 2*alpha + 1.
- Non-torus families (ex): legacy rmax fallback -> UNM
  (no-geometry refusal).

## A3.3 Frozen control outcomes (rule x controls)

Claim: ring 1.00/1.00, sq 2.04/1.90, j2 2.01/1.95, cb-L20
2.93, cb-L24 3.14 (max bias 0.14). Expected-UNM: cb-L12/L16
(empty regime window). Refuse: expanders. P-range agrees
within 1% on all claiming cells (smoke check kept).

- tol_stat = 1.3x max bias = 0.19 (mechanical).
- Gate (uniform rule, controls and J3): window empty ->
  require UNM (claiming without regime is debt); window
  nonempty -> require |d - dim| <= tol_stat.

## A3.4 Falsifiable J3 predictions (transferred, D = 24/30/36)

delta* = 0.5 (3D J class, xi_J3 = sqrt(2)/sqrt(0.5) = 2.0):
J3-L16 static UNM (empty window); J3-L20 (4..8, 5 shells)
and J3-L24 (4..11, 8 shells) must read 3 +- 0.19.
