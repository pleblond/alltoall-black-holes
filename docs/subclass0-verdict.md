# SUBSTRATE-CLASS-0 verdict — Structural Characterization of the VAC-0 Class

Campaign brief: `SUBSTRATE-CLASS-0.tex`. Prereg:
`docs/subclass0-prereg.md` (frozen pre-data, commit `2759fd4`).
Apparatus: `src/bh_graph/subclass0.py`. Records:
`data/subclass0/desc_*.json` (31 cells, beast) + `data/subclass0/report.json`.
Analyzer: `scripts/subclass0_analyze.py` (pure join, re-runnable).

## Headline: SUBCLASS0-PARTIAL

Three of six CLASS components admit exact minimal structural rules —
each in BOTH a spectral and a simple-combinatorial form, so multiple
inequivalent class descriptions remain. The other three components
provably admit NO exact rule in the frozen feature space: each has a
PASS/FAIL pair with identical frozen feature vectors (F: the two
J2-swap seeds; H_TAU and J_useful: the two ring sizes, a documented
floor artifact). Necessary structure is narrowed everywhere; a single
exact class condition does not exist on this battery.

| component | n | exact rules (kind) | minimal | status |
|---|---|---|---|---|
| F interference | 13 | none | — | sufficient-but-not-necessary only (FN: swap8_s1/s2) |
| E ordered-dim | 13 | E_spectral (S), E_ball (C) | both | EXACT ×2, inequivalent |
| H_shell turn-on | 27 | Hshell_spectral (S), Hshell_local (C) | both | EXACT ×2, inequivalent |
| H_TAU turn-on | 27 | none | — | best: diameter (4 errors) |
| G TUN square-grade | 10 | G_spectral (S), G_plaquette (C) | S only | EXACT ×2; plaquette non-minimal |
| J_useful quadrature | 27 | none | — | inherits H_TAU + gap-scale misses |

S = spectral, C = combinatorial. No holdout was manufactured (prereg
§8), so SUBCLASS0-EXACT was unreachable by construction; the verdict
was decided between PARTIAL / SPECTRAL / DEBT on the frozen ladder.

## A — Descriptor exactness: apparatus validates

- All 31 battery cells match their preregistered spectrum
  expectation: every pristine cell (J2/square/quotient/tri/hex/ring/
  open at every size) matches its Bloch certificate at residual
  ≤ 1e-5, and every perturbed/random cell (swap8/rewire/rr) matches
  none. `family_bad = []`, `apparatus_ok = True`.
- 36 pre-data pins green: Bloch-vs-brute identity on tiny graphs;
  exact motif counts (K4: 4 triangles + 3 four-cycles; diamond 2/1;
  K2,3: 3 four-cycles; Petersen girth 5; 6-torus 36 four-cycles;
  tri-6 torus 72 triangles; J2-L4 zero-mode dimension 22 = 16 flat
  band + 6 extra); certificate match on tiny banked builders;
  feature/score/verdict ladder units; loader shape.
- No descriptor was added, removed, or redefined post-data. No
  rule, feature, threshold, or verdict clause changed after the
  battery run.

## B — LAW controls: green

- J_alg PASS 27/27 across spectral families (j2/square/tri/hex/
  ring/none): the B/J algebra ignores every CLASS separator. ✓
- H_existence (16 non-turn-on gates) PASS 27/27. ✓
- D (ballistic propagation, LAW) passes on 6 non-square-class
  cells (tri ×2, hex ×2, ring ×2): square-class structure does not
  control D. ✓
- I_class: 26 FINITE-RANGE + 1 NON-RADIAL, filed (no LAW violation).
No CLASS separator collapses onto a LAW bit: the classification is
not rediscovered field identities.

## C — Necessary-property census (P ⇒ C on the battery)

| component | features shared by every PASS cell |
|---|---|
| F (7/13) | c4_positive, diam_not_small, not_hex, not_hex_local, superlinear_ball |
| E (11/13) | diam_not_small, disp_dim_2, ordered_dim, regular, shell_orbit_one, superlinear_ball |
| H_shell (25/27) | not_hex, not_hex_local, regular |
| H_TAU (17/27) | regular (vacuous: all cells regular) |
| G_square_grade (2/10) | 14 features (small-n effect: only j2 + square pass) |
| J_useful (12/27) | not_hex, not_hex_local, regular |

Notable necessities and non-necessities:

- F does NOT require square_class, bipartiteness, separability, or
  any spectrum: swap8_s1/s2 pass with `disp_family = none`.
  F-necessary conditions are all combinatorial / local-growth.
- E requires 2D-ness in both forms (disp_dim_2, superlinear_ball)
  plus full shell symmetry; rings violate all three.
- H_shell requires only non-hex-ness (both forms); everything else
  about the 25 passers varies freely (degree 2–8, expanders and
  lattices alike).
- H_TAU has NO nontrivial necessary frozen feature: passers span
  every spectral family, both gap sides, and diameters 9–800.
- Sheet structure (`sheet2`) is necessary for NOTHING: every
  component has passers without sheets (§I).

## D — Sufficiency census (frozen rules only)

Confusion matrices (measured cells):

| rule | tp | fp | tn | fn | exact |
|---|---|---|---|---|---|
| F_spectral | 5 | 0 | 6 | 2 (swap8_s1/s2) | no |
| F_plaquette | 5 | 0 | 6 | 2 (swap8_s1/s2) | no |
| E_spectral | 11 | 0 | 2 | 0 | YES |
| E_ball | 11 | 0 | 2 | 0 | YES |
| Hshell_spectral | 25 | 0 | 2 | 0 | YES |
| Hshell_local | 25 | 0 | 2 | 0 | YES |
| HTAU_gap | 7 | 1 (ring_N1600) | 9 | 10 | no |
| HTAU_diameter | 14 | 1 (ring_N1600) | 9 | 3 (rr3 ×3) | no |
| G_spectral | 2 | 0 | 8 | 0 | YES |
| G_plaquette | 2 | 0 | 8 | 0 | YES (non-minimal) |
| J_inherited | 5 | 1 (ring_N1600) | 14 | 7 | no |

- F rules are SUFFICIENT (fp = 0: square-class/plaquette structure
  never passes spuriously) but not necessary (the two swap seeds).
- HTAU_gap fails badly (10 FN): the frozen absolute cut 1/12 does
  not scale with coordination — J2_L20/L28 (λ2 = 0.196/0.100),
  j2quot_L20 (0.098), tri_L28 (0.100) all exceed it yet pass. The
  normalized gaps λ2/z are theory-identical across same-size tori
  (j2_L28 and square_n28 both 0.01254); the frozen rule compares
  unnormalized values across bandwidths. Honest scale miss, filed
  as a mechanism hypothesis for a future campaign — NOT rescored
  here (no post-data rule changes).
- HTAU_diameter (4 errors) is the closest H_TAU rule; its
  residuals are the rr3 puzzle and the ring artifact (§G).
- J_inherited misses via the gap conjunct (7 FN: the same
  small-L ordered cells + rr3 ×3) plus the ring FP.

## E — Degree-only negative control

All 6 perturbed cells preserve degree exactly (8-regular, N = 1568)
yet change 19–25 frozen descriptors each:

- 8 swaps already break: bipartiteness, the J2 spectrum
  (`j2` → `none`), separability, all three shell/orbit statistics,
  quotient-squareness, the flat-band count (838 → 822), and 11
  further descriptors. swap8_s2 additionally gains triangles
  (girth 4 → 3).
- 20000 swaps further collapse: diameter 28 → 6, zero modes
  822 → 0, shell orbits to ~1200, superlinear ball lost,
  diam_not_small lost.
- cross_sheet_fraction stays ≈ 0.5 throughout (labels, not
  geometry — correctly uninformative).

Degree/multiset preservation constrains essentially nothing tested:
phenomenology needs spectral/geometric organization. Evidence
against degree-only vacuum, exactly as VAC-0 filed — with the
quantified descriptor ledger above.

## F — J2 non-uniqueness

Every component has non-J2 passers; nothing tested is J2-only:

- F: quot, square, open + swap8_s1/s2 (5 non-J2).
- E: quot/square/tri/hex/ring-fail-excluded (9 non-J2).
- H_shell: 23 non-J2 (everything except hex).
- H_TAU: 15 non-J2 (incl. hex, swap8, rr3, ring_N400).
- G: square.
- J_useful: 10 non-J2 (quot/square/tri/ring_N400/rr3).

No descriptor is "the J2 property": `is_j2_spectrum` is lacked by
every non-J2 passer trivially, while every other J2-shared feature
(bipartite, girth_4, c4_positive, triangle_free, separable_band,
square_class, disp_dim_2, …) is held by some non-J2 passer and
lacked by another. In particular the F-passing swap seeds share
with J2 only: c4_positive, diam_not_small, superlinear_ball,
triangle_free (s1), and the not_hex pair — while lacking spectrum,
bipartiteness, separability, shell symmetry, and quotient-squareness.

## G — Failure anatomy

1. **F swap split (mechanism: defect location, not global
   structure).** j2swap8_s0 (FAIL) and j2swap8_s1 (PASS) have
   IDENTICAL frozen boolean feature vectors (verified in
   `report.json` inputs): no exact F rule exists in the frozen
   feature space — a proof, not a shortfall. Their numeric
   descriptors differ (orbits 34 vs 72, diameters 25 vs 23,
   projector ratios 2.2 vs 1.6) but not along the F label (s2 ≈ s0
   numerically, yet s2 passes). The filed F failure is the slit1
   phase rung — a defect sitting on a slit path. Association class:
   mechanism-supported (global invariants provably insufficient;
   slit-relative defect position is the remaining degree of
   freedom). Mere correlation: none claimed.
2. **F tri/hex fail (mechanism: band/plaquette).** Both fail all
   four plaquette conjuncts jointly (tri: non-bipartite, girth 3;
   hex: girth 6, c4 = 0) and lack separable bands. Consistent with
   the SLIT rectangular-phase mechanism; the swap counterexample
   shows these conditions are sufficient, not necessary.
3. **F rewire fail (mechanism: total organization loss).** 25
   descriptors move; speckle failure (slit1 + validity) follows
   from destroyed transverse coherence. Overdetermined; no single
   descriptor isolable.
4. **H_TAU ring_N1600 (artifact, documented).** N400 (PASS) and
   N1600 (FAIL) have identical frozen feature vectors, so no exact
   H_TAU rule exists in this space either — but here the cause is
   the filed floor artifact (exact-0.0 far field fails strict >;
   physics identical: ξ to 4 decimals). Any gap/diameter/order rule
   FP on N1600 inherits this artifact. Exclude-on-repair (not
   excluded here: labels frozen).
5. **H_TAU rr3 puzzle (open).** rr3 (λ2 ≈ 0.17, diam 14) pass while
   rr4/rr8 (λ2 0.55/2.75, diam 9/5) fail; the diameter rule's only
   non-artifact residuals. Hypothesis: lower-degree expanders mix
   slowly enough for ramp ordering to survive. Correlation only —
   no frozen feature separates rr3 from rr4/rr8 on the passing
   side (all share disp none, small diameter, large gap).
6. **H_TAU gap-scale miss (frozen-rule defect, §D).** Absolute
   1/12 cut splits same-size tori by coordination (J2 vs square).
   Filed as future-campaign hypothesis (normalized gap), with the
   caveat that no gap rule of any normalization can fix rr3
   (λ2/z = 0.059 sits between ordered ≤ 0.025 and failing
   expanders ≥ 0.139 yet passes) or the ring artifact.
7. **J_useful residuals** are inherited: gap-scale FN (small-L
   ordered) + rr3 FN + ring artifact FP. No independent J anatomy;
   J_useful = DE∧HI behaves exactly as its frozen conjunction.
8. **H_shell hex fail.** Only hex fails (both sizes); hex is the
   unique 3-regular girth-6 bipartite triangle-free cell and the
   unique hex-spectrum cell. Near-field shell-shape mechanism per
   VAC-0H; association class: exact on the battery, mechanism
   cited from VAC-0 (transient shell shape), not re-derived here.

## H — Spectral versus combinatorial: tie, not a win

- E, H_shell, G: BOTH kinds exact. Spectral certificates and
  simple local combinatorics tie on this battery; neither is
  "better". Matched pairs cut both ways: swap8 preserves degree
  but breaks spectrum while keeping F (spectrum not necessary
  for F); tri/hex preserve 2D order but change the band while
  losing F/G (band/plaquette jointly sufficient).
- F has an anti-spectral necessity result (§C): PASS without any
  pristine spectrum.
- F, H_TAU, J_useful have NEITHER kind exact (impossibility
  proofs for F and H_TAU in frozen space).
- Therefore SUBCLASS0-SPECTRAL is refused: the strongest exact
  characterizations are evenly split, and three components resist
  both kinds. This tie is the core of the PARTIAL verdict.

## I — Quotient/sheet role: not required for any CLASS phenomenon

- `sheet2` is necessary for no component (§C): F/E/H/G/J all have
  sheetless passers (square, quot, open, tri, hex, ring, rr3).
- `quotient_is_square` (True only on pristine J2) is likewise
  unnecessary: F passes on swap8_s1/s2 with broken quotients.
- Conclusion: sheet/quotient structure is required only for
  hidden-sector phenomena (HIDDEN0-SEPARATED, QUOT0-OPERATIONAL —
  both banked frozen on main and consumed as cited results, not
  re-derived), never for VAC-0 CLASS membership. Observer
  quotient and generic 2D geometry are not conflated: 2D
  sheetless substrates (square/tri/hex/open) pass E/F/G while
  the sheeted-but-disorganized rewire fails them.

## J — Dimensional controls

- Consumed only the frozen completed DIM-3-0 result
  (DIM3-GEOMETRIC, banked on main tail). No interim DIM-3-1
  outcome was read or used.
- No volume-fit geometric-dimension descriptor exists in the
  frozen set: `disp_dim` is an exact spectral certificate and
  `ball_vol` entries are exact counts, so the known-bad
  inherited estimator (structurally capped d*, supralinear
  arrival times) enters nowhere.

## K — Holdout: none (reported limitation)

Per prereg §8: labels public, too few independent families, VAC-0Q
builders phenotypeless. No holdout manufactured; `holdout_passed =
False` blocks SUBCLASS0-EXACT on the frozen ladder.

## L — Minimal class description (ablation)

- E_spectral, E_ball, Hshell_spectral, Hshell_local, G_spectral:
  exact AND minimal (singleton ablation to the always-PASS null
  breaks exactness with exhibited FP cells).
- G_plaquette: exact but NOT minimal — dropping girth_4,
  triangle_free, or c4_positive individually preserves exactness;
  only bipartiteness is load-bearing (its ablation FPs on
  swap8_s0/s1). The frozen 4-conjunct form over-specifies G;
  reported as-is, no reformulation (post-data rule edits are
  forbidden).
- F/H_TAU/J rules: not exact, minimality moot.

Smallest exact per-component descriptions: E = {disp_dim_2} or
{superlinear_ball}; H_shell = {not_hex} or {not_hex_local};
G = {square_class}. No unified cross-component condition exists:
their conjunction is not a single "class rule" (different
components need different properties — F needs plaquette/growth,
E needs 2D-ness, H_shell needs non-hex-ness).

## Verdict: SUBCLASS0-PARTIAL

Necessary/sufficient structure is narrowed (exact minimal rules
for E, H_shell, G; sufficient-only rules for F; impossibility
proofs for F and H_TAU in frozen space; full necessity/degree/J2
ledgers) but multiple inequivalent class descriptions remain —
both across kinds (spectral vs combinatorial ties) and across
components (no unified condition). SPECTRAL is refused (§H);
EXACT is blocked (§K); DEBT is refused (three components exact);
INCOMPLETE is refused (apparatus 31/31).

## Data-quality flag (pre-existing, not this campaign's)

`docs/vac0-verdict.md` prose states J_useful "13/27 PASS"; the
filed `data/vac0/j_results.json` record consumed here counts 12
PASS (j2 ×2, quot ×2, square ×2, tri ×2, ring_N400, rr3 ×3).
The JSON record is authoritative for this campaign; the prose
count is flagged for the VAC-0 erratum process, not adjudicated
here.

## Open threads (for future campaigns, not this one)

- Normalized-gap TAU hypothesis (λ2/z with an independently
  motivated cut) — needs its own preregistration; cannot fix
  rr3 or the ring artifact in any normalization.
- F defect-location probe: slit-relative swap position as the
  F-predicting variable (requires new experiment graphs, hence
  a new campaign with a pre-data family extension).
- rr3-vs-rr4/rr8 TAU mechanism (mixing-rate ladder).
- Unified multi-component condition, if any exists beyond the
  per-component rules.

## Firewall

Output = substrate conditions supporting the tested VAC-0
phenomenology on the tested battery. No claim of a uniquely
physical substrate; no "J2 property" named (§F); no
generalization beyond the battery without theorem.
