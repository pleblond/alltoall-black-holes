# VACDOMAIN0-VERDICT — VACDOMAIN-RADIATIVE (DATA)

Beast campaign 2026-10-03 (204 tasks, 90-way) + frozen analyzer: every gate
green, fails []. Records data/vacdomain/*.json (204) + verdict.json.
Amendment-1 (headline ledger budget, measurement resolution) applied
pre-rerun; six L=28 bulk records rerun, all else first-pass.

## Headline

Fixed-geometry interfaces between disconnected JOINT components are
RADIATIVE: every disconnected join (V+|Vpi, V+|Vhidden x4, Vpi|Vhidden x4,
both orientations, L=28) emits ballistic |drho| fronts (reach 4-6 cells by
T_CLEAN, R^2 0.89-0.92) while the S-step fully persists (step ratio 0.999)
and both bulk plateaus hold (drift 0.0 to fp precision). Bulk vacua survive;
the disturbance propagates away. Same-component hidden-hidden joins are
exactly stationary (drifts 0.0); same-vacuum preparations show no interface.

## Gates

- G0 BULK: all 6 bulks x 3 L re-ladder JOINT (10/10 checks).
- G1 NOGO: analytic no-go for all 9 disconnected (dE 8/16); numeric
  interior eigenvalues exactly (-8/+8/0) at L>=8 with best residuals
  3.71 (dE 8) and 7.21 (dE 16); L=4 all-interface + residual >1e-6;
  hidden-hidden residuals 0.0 (exact E=0 eigenstates).
- G2 FLAT: hidden-hidden stationary + P_- pure + frozen (all L, ori).
- G3 NONSTAT: all disconnected nonstationary (interface dmax ~1e-3 at
  L=28 vs 1e-8 bar; hidden-hidden/same exactly 0.0).
- G4 SPECTRAL: dense match <1e-8, witness I <1e-10, support drift <1e-9;
  sector conserved, P_- frozen, energy drift <1e-9; mixed-sector P_-
  weight exactly 1/2 (persistent residue).
- G5 RADIATIVE: 18/18 pair-orientation cells radiative (table below).
- C controls: same-vacuum quiet; phase <1e-9; x/y covariance <1e-9 with
  equal initial widths; L=28 bulk <10% of interface (ratio 0.006);
  ledgers finite.

## Radiative table (L=28, per pair x orientation)

| join | v | v/V_QUAD | R^2 | reach | step | dW |
|---|---|---|---|---|---|---|
| VPLUS\|VPI (x,y) | 6.10 | 1.03 | 0.919 | 6 | 0.999 | 4 |
| VPLUS\|H0,H3 (x,y) | 4.98 | 0.84 | 0.895 | 4 | 0.999 | 6 |
| VPLUS\|H1,H2 (x,y) | 5.13 | 0.86 | 0.893 | 4 | 0.999 | 6 |
| VPI\|H0,H3 (x,y) | 4.98 | 0.84 | 0.895 | 4 | 0.999 | 6 |
| VPI\|H1,H2 (x,y) | 5.13 | 0.86 | 0.893 | 4 | 0.999 | 6 |

V_QUAD = 5.94 banked (RESPONSE-0). H1/H2 and H0/H3 pair up exactly
(alpha <-> pi/2 - alpha symmetry, filed). x/y identical to all digits
(D-SWAP exact). dW = disturbed-zone widening ~ 2 v t (anatomy, not a gate).

## Anatomy (filed, not gated)

- Energies: VPLUS|VPI E = 0.0 (excess 0.0); VPLUS|H* E = -3.8571
  (excess +1/7); VPI|H* E = +3.8571 (excess -1/7); hidden-hidden E = 0.
- Sector: mixed joins exact halves (P_- residue frozen, weight 1/2);
  VPLUS|VPI all-P_+; hidden-hidden all-P_-.
- Beats: disconnected joins carry dE = 8/16 spectral beating AND
  radiation; the beating is global phase structure, the fronts are the
  emitted disturbance (spectral superposition exact: no new content,
  witness zero, so this is linear propagation, not interaction).
- Ledgers: virtual (B, L) landscapes recorded per join (band/off split);
  no structural reading attached (firewall kept).
- Scaling: L=4/8 confirm nonstationarity + sector/no-go structure; L=8
  fronts saturate (short torus, filed); headline is L=28.

## Firewall

No domain-wall particle, cosmology, phase-transition, geometry-dynamics,
or vacuum-preference claims. Interfaces are linear field evolution under
unchanged H = -A; "radiative" means emitted propagating fronts with
persistent bulk steps, nothing more.

## Suite

Full test suite on beast (90-way, tests/test_weighted.py skipped):
1812 passed, 2 skipped.
