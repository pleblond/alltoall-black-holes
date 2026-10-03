# VAC-0 verdict — Vacuum Substrate Universality (DRAFT: F/H/I/C1 closed; D/E/G/J pending)

Campaign brief: `VAC-0.tex` (frozen field law `H = -A`, fixed geometry).
Master prereg: `docs/vac0-prereg.md`. Stage addenda: `docs/vac0-{de,fg,hi,j}-*.md`.

Classification scale: LAW (generic across the battery) / CLASS (structured
family, controls fail) / J2 (only J2 retains it) / MIXED (per-phenomenon
split) / ACCIDENTAL (fragile even on J2).

## VAC-0A — algebraic identities: LAW ✓

A1–A6 (norm, continuity, bond energy, conjugacy, quadrature, branch
accounting) hold on every hostile graph tested. Nothing about J2 enters.
Pinned by `tests/test_vac0a_identities.py`. No campaign data involved.

## VAC-0F — coherent interference: square CLASS ✓

Record: `data/vac0/f_results.json` (+ `data/vac0/mz_corrected.json` erratum).

- PASS (7): open grid, square torus, J2 (L28 banked + L40), J2 quotient,
  j2swap8 seeds 1–2.
- FAIL (6): triangular (high visibility, no phase response), hex (high
  visibility, no phase response), j2rewire ×3 (speckle: slit1 + validity
  fail), j2swap8 seed 0 (phase rung fail — 2/3 within-family).
- MZ corridor: PASS at LAW level after the Amendment-1 window erratum
  (exact Campaign-2 replication; filed, original preserved for audit).

The pass set is the square family (J2 included as its microstructure
member), not J2 uniquely and not everything: CLASS. Rewiring destroys
phase-lawful interference while preserving degree → evidence against a
degree-only vacuum characterization. Triangular/hex show that high
contrast ≠ coherent interference (phase rung decisive).

## VAC-0H — static/driven field portability: CLASS (broad) ✓ (data filed)

Record: `data/vac0/hi_summary.json` (trimmed from the 617MB beast
`hi_results.json`, sha256 `1a016a3c…`, 459 records; full file retained
on beast for audit). C1 regression: `data/vac0/pot1_regression.json`
(ladder POT1-FIELD, all 89 gates true — banked POT-1 reproduced exactly
by the unmodified runner).

Cell verdicts (18-gate H battery, PASS iff all 18):

- PASS (15/27): j2 ×2, j2quot ×2, square ×2, tri ×2, j2swap8 ×3,
  rr3 ×3, ring_N400.
- FAIL (12/27): hex ×2 (`H_ramp_shell`), j2rewire ×3 + rr4 ×3 + rr8 ×3
  + ring_N1600 (`H_TAU`).

Two-part structure (read the gates, not just the bit):

1. Static existence is GENERIC: 16 of 18 gates pass on all 27 cells —
   jump/pair match to prediction, quiet (`H_J`), range, wrap,
   linearity/quadraticity, phase covariance, switch causality, secular
   balance. Every substrate tested hosts the persistent-source static
   field with the same analytic port rule (`omega = -(z+1/2)`).
2. Turn-on dynamics is CLASS-sensitive, with two distinct mechanisms:
   - hex: near-field turn-on shell shape mismatches prediction
     (`H_ramp_inner` passes at 0.05, shell means fail 25%) on both
     sizes — a hex-specific transient, not noise (jump passes).
   - expanders (rewire/rr4/rr8): the TAU lingerer ordering reverses
     (slow ramp leaves MORE far field, `c12 > c4` at ~1e-3, far above
     floor) or goes non-monotone (rr4 middle rung) — the J2
     diabatic-vs-adiabatic ordering flips on high-expansion graphs.
   - ring_N1600 `H_TAU` FAIL is a documented numerical-floor artifact:
     both ring cells have identically zero far lingerer (range 4 <
     r_far 10; N400 values ~1e-29 dust order luckily, N1600 exact 0.0
     fails strict `>`). Filed FAIL stands (no post-data weakening);
     physics replicates exactly (xi identical to 4 decimals, ranges
     4 = 4, other 17 gates pass on both).

H verdict: CLASS — but a broader class than F (triangular and rr3 join
the pass set here while failing F). Static response needs less
substrate structure than coherent interference.

## VAC-0I — static radial-law classification ✓ (data filed)

Same record as H. Decision tree (H3 + noise-floor amendment):

- 26/27 FINITE-RANGE; j2swap8_s0 NON-RADIAL (median shell CV 0.77 —
  mild disorder breaks radial symmetry on one seed while all H gates
  still pass: H phenomenology does not require radiality).
- xi values cluster by family (j2 ~2.0, square/quot ~1.54, tri ~1.6,
  hex ~1.37, ring 1.47, rr3 ~1.06, rr4 ~1.2, rr8/rewire ~1.55–1.6,
  swap8 ~1.7–1.8); every family is xi-consistent across sizes/seeds
  (ratio < 1.5, most < 1.04).
- Note: H3 xi (fit window r = 2..8) differs in convention from POT-1
  xi (J2: 2.02 vs 0.53); both classify finite-range. The portability
  rung is the field match (`H_jump_global` 5% everywhere), not the
  xi number.

I verdict: FINITE-RANGE is near-universal (LAW-like label); the xi
scale is CLASS-structured.

## VAC-0D — ballistic propagation: PENDING (beast rerun after D7 repair)

## VAC-0E — coherence-direction: PENDING (same run as D)

## VAC-0G — tunnelling: PENDING (beast run)

## VAC-0J — B/J quadrature: PENDING (apparatus frozen; runs after D)

## Overall VAC-0 synthesis: PENDING

(Open questions for the final verdict: D/E pass pattern vs F/H;
G width-law portability; J_alg LAW confirmation + J_useful table;
per-phenomenon LAW/CLASS/J2/MIXED assignment; substrate-property
statement per phenomenon.)
