# VAC-0 verdict — Vacuum Substrate Universality (FINAL)

Campaign brief: `VAC-0.tex` (frozen field law `H = -A`, fixed geometry).
Master prereg: `docs/vac0-prereg.md`. Stage addenda: `docs/vac0-{de,fg,hi,j}-*.md`
plus D7/D8, F2/F3, G4/G5/G6, H3-amendment-1, MZ erratum (all filed pre- or
per-prescribed-remedy; see firewall log below).

Classification scale: LAW (generic across the battery) / CLASS (structured
family, controls fail) / J2 (only J2 retains it) / ACCIDENTAL (fragile on
J2 itself) / MIXED (per-phenomenon split — legitimate and, here, the result).

## Headline: MIXED (no phenomenon requires uniquely J2)

| Stage | Phenomenon | Verdict | Record |
|---|---|---|---|
| A | algebraic identities | LAW | tests, `docs/vac0-law-derivations.md` |
| D | ballistic propagation | LAW (geometric scope) | `data/vac0/de_results.json` |
| E | coherence-direction battery | CLASS (2D ordered) | same |
| F | two-path interference | CLASS (square) | `data/vac0/f_results.json` |
| G | tunnelling (frozen battery) | FRAGILE/all-fail (gate artifact, §G) | `data/vac0/g_results.json` |
| G | tunnelling (TUN-level, descriptive) | CLASS (square-grade) | same |
| H | static/driven existence (16 gates) | LAW-like (27/27) | `data/vac0/hi_summary.json` |
| H | static turn-on (TAU/shells) | CLASS (broad) | same |
| I | radial-law label | LAW-like (26/27 finite-range) | same |
| I | xi scale | CLASS-structured | same |
| J | B/J algebra | LAW (27/27 exact) | `data/vac0/j_results.json` |
| J | quadrature usefulness (DE∧HI) | CLASS (13/27) | same |
| C1 | POT-0/P1.1/POT-1 regressions | PASS (digit-exact) | DE/F/HI records + `data/vac0/pot1_regression.json` |

Central question — is J2 uniquely required, one member of a viable class,
or one realization of generic laws? **Per phenomenon: generic laws (A, D,
H-core, I-label, J-alg) or class member (F, E, H-turnon, G, J-useful).
Nothing tested requires uniquely J2.** The substrate-uniqueness debt is
not paid toward J2; it dissolves into per-phenomenon substrate classes.

## VAC-0A — algebraic identities: LAW

A1–A6 hold on every hostile graph (path/cycle/star/complete/
disconnected/random/J2-ball/J2-torus). Nothing about J2 enters.
Pinned by `tests/test_vac0a_identities.py`.

## VAC-0D — ballistic propagation: LAW (geometric scope)

10/10 measurable cells PASS (j2/j2quot/square/tri/hex/ring × sizes):
D > 0.5, source separation, alpha > 1.3, Cv, exact reversal, R2 > 0.99.
Independent of coordination (3/4/6/8), bipartiteness, microstructure.
- RR: UNDEFINED by P2.1 (no momentum sector) — intrinsic delta filed.
- j2swap8/j2rewire: INVALID via S1_trans (translation symmetry broken
  by construction; D8.1) — no verdict drawable, never FAIL.
- C1: j2_L28 reproduces POT-0B to the digit (0.8551/2.087/1.2110/
  0.4116); ring_N400 P1.1a within 0.6%; sq30 P1.1a within 2% (D8.2
  T = 12; VAC-0D wrap is 2× stricter than P1.1a's own gate);
  j2 branch anatomy w0 = 9e-6 (0.0000 at P1.1b precision), mixing exact.

Statement: ballistic propagation requires lattice translation order;
among ordered lattices it is generic.

## VAC-0E — coherence-direction: CLASS (2D ordered)

PASS on all 2D ordered lattices (j2/j2quot/square/tri/hex); FAIL on
ring ×2 (E aperture gates: 1D narrow packets stay ballistic, so the
aperture–directionality relation differs; N400 also D_scr_D).
Statement: the frozen coherence-direction battery is 2D-specific;
1D propagates (D PASS) but scales differently under apertures.

## VAC-0F — two-path interference: CLASS (square)

PASS: open grid, square torus, J2 (L28 + L40), J2 quotient, swap8 2/3.
FAIL: tri/hex (high visibility, no phase response), rewire ×3
(speckle: slit1 + validity fail), swap8 1/3 (phase rung).
MZ corridor PASS at LAW level (Amendment-1 window erratum filed).
Statement: phase-lawful interference needs square-class structure;
degree-preserving rewiring destroys it (evidence against degree-only
vacuum). Precise property (rectangular separability? band-structure
at operating k?) left open.

## VAC-0G — tunnelling: frozen FRAGILE, TUN-level CLASS (square-grade)

Frozen battery: ALL FAIL (j2/square/tri/hex/swap8) or UNDEFINED
(rewire: wall_dmax 7–8 ≥ |E0|, no barrier per spec). Verdicts stand —
no post-data weakening — but the J2 regression localizes the failure
to a gate-tightness artifact, not physics:

- J2 matches k-averaged transfer-matrix T_pred to <3% at LB = 0..6
  (LB = 6: 2.6%); only LB = 8 deviates (T = 2.9e-5 vs pred 1.1e-5,
  non-monotone interior) — a ~2e-5 floor TUN-2 deliberately did not
  fire on (TUN gates: ratios ∈ [1/3, 3] for LB ∈ {1..6} only;
  LB = 8 gated solely T < 1e-4, which VAC-0G passes; LB8-ratio filed
  non-firing; interior gated at LB = 6 only). VAC-0G ported 5%-per-LB
  including LB = 8 plus interior at {4,5,6,8} — tighter than TUN.
- Against TUN-2/TUN-3 banked gates the VAC-0G J2 record passes
  everything (ratios ≤ 1.03 vs 3× bar; slope within 10% vs 30% bar;
  strength strictly ordered; control 0.695 vs 0.710 pred).

TUN-level descriptive comparison (filed numbers, not verdict bits):
square ≈ J2 (LB ≤ 6 within 1%, same LB = 8 floor); tri textbook
evanescent staircase + κ-slope ✓ with control T = 0.36 (trapped
B = 0.21 — frozen wall-band model wrong for tri, not physics
absent); hex soft decay (chain-κ over-predicts suppression) +
LB = 8 non-monotone; swap8 J2-grade at LB ≤ 3 (0.462/0.105 match
pred) with defect floor ~2e-3; rewire no barrier (UNDEFINED, honest).

Statement: TUN-grade evanescent transmission with predicted width
dependence is square-class; the frozen VAC-0G battery cannot rank
substrates (fails its own J2 regression at LB = 8 by gate design).

## VAC-0H — static/driven: existence LAW-like, turn-on CLASS (broad)

15/27 PASS (j2/quot/square/tri ×2, swap8 ×3, rr3 ×3, ring_N400).
FAIL: hex ×2 (H_ramp_shell), rewire/rr4/rr8 ×3 each + ring_N1600
(H_TAU). Structure:

1. Existence GENERIC: 16/18 gates pass on all 27 cells (jump/pair
   match, quiet, range, wrap, linearity, phase, switch, secular).
   Every substrate hosts the analytic static field
   (omega = -(z+1/2) port, zero tuning).
2. Turn-on CLASS-sensitive: hex near-field shell shape (both sizes);
   expander TAU reversal (slow ramp leaves MORE far field, ~1e-3,
   above floor) / non-monotonicity (rr4); ring_N1600 TAU FAIL is a
   documented floor artifact (both rings exactly-zero far field;
   N400 dust orders luckily, N1600 exact 0.0 fails strict >;
   physics identical: xi to 4 decimals, ranges 4 = 4).

Statement: static response needs less structure than interference
(tri/rr3 pass H, fail F); turn-on dynamics discriminates
(non-expander ordering + non-hex transients, two mechanisms).

## VAC-0I — radial law: label LAW-like, scale CLASS

26/27 FINITE-RANGE (swap8_s0 NON-RADIAL at CV 0.77 — H passes
anyway: radiality not required). xi family-clustered (j2 ~2.0,
square/quot ~1.54, tri ~1.6, hex ~1.37, ring 1.47, rr3 ~1.06,
rr4 ~1.2, rr8/rewire ~1.55, swap8 ~1.7–1.8), every family
size-consistent (ratio < 1.5, mostly < 1.04). H3 xi convention
differs from POT-1 xi (fit window); both finite-range.

## VAC-0J — quadrature: algebra LAW, usefulness CLASS

J_alg PASS 27/27, decomposition residual exactly 0.00e+00 on all
four arms (random/stagger/packet-mid/driven): the B/J algebra is
generic, as VAC-0A says. J_useful (frozen DE∧HI conjunction):
13/27 PASS — usefulness needs ordered-substrate phenomenology.
The brief's firewall held in the data: rewire/hex carry exact
algebra with no useful phenomenology. (swap8 J_useful FAIL rides
on DE-INVALID/unmeasured + HI-PASS; rewire on DE-INVALID + HI-FAIL —
pheno_rows filed per cell.)

## Degree-only vacuum: excluded (not J2-selected)

Degree-preserving rewiring destroys: F phase-lawfulness (speckle),
H-TAU ordering (reversed), G barrier (wall band too wide),
DE validity (S1 symmetry broken). Phenomenology needs long-range
spectral/geometric organization, not degree/motifs. But alternatives
survive everywhere (square/quot for F; +tri/rr3 for H; +hex/ring for
D), so this is evidence against degree-only characterization, not
for unique J2 — exactly the brief's required distinction.

## Firewall log (amendments and remedies)

- D7 (pre-data): RR intrinsic-only records (first DE launch crashed,
  zero records). Non-RR paths untouched.
- D8 (D6.1-prescribed INVALID remedy): trans permutation fix for
  J2-label cells (provable non-permutation: 784 images for 1568
  nodes) + sq30 T 25 → 12 (frozen wrap arithmetic). Valid cells
  reproduce; no threshold moved; swap/rewire stay INVALID as filed.
- G5/G6 (pre-data): LB = 0 dmax guard; LB = 1 NaN-slope guard (two
  G launches crashed, zero records each).
- H3-amendment-1 (pre-data): 1% noise floor for sign/CV shells.
- F2/F3, G4, MZ erratum: banked on main (prior agent).
- J addendum frozen pre-data (J_alg bars from float arithmetic;
  J_useful conjunction fixed before DE verdicts existed).
- G frozen FAILs stand (no post-data gate weakening); TUN-level
  evaluation is descriptive synthesis, not a verdict change.
- Full suite on beast (parallel, test_weighted skipped per config):
  1794 passed / 2 skipped, 0 failed (final code).

## Open threads (not VAC-0's to close)

- Exact substrate property for F (square-class mechanism).
- Unified property for H turn-on (two mechanisms: hex shells,
  expander TAU).
- LB = 8 tunnelling floor mechanism (~2e-5, unassigned).
- Held-out validation battery (VAC-0Q, frozen unopened).
