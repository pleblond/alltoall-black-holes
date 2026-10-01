# P-track: emergent polarity (parallel, discovery-first)

Parallel campaign forked from `cursor/formation-design-2031` / PR #62 tail
(formation D5inf + spontaneous localization, BEFORE any Weyl/complex/unitary
machinery). PR #63 / D15 is READ-ONLY apparatus until a one-way convergence
gate fires. This file is the P-track ledger (preregs + verdicts); D14 sections
in `docs/DEFERRED.md` are FROZEN (no edits except this pointer).

Charter (locked):

- Hard rule: DO NOT DEFINE POLARITY FIRST. DISCOVER DEGENERACY FIRST.
  Start from finite/localized candidate excitations under exactly the same U;
  search for reproducibly distinct dynamical classes; only then ask what
  transformation relates them.
- Order: (1) multiple long-lived states at matched size/energy? (2) pairs?
  (3) intrinsic symmetry mapping? (4) derived signed observable P? (5) P
  survives translation/collisions? (6) ++/+-/-- interactions differ?
- Strong result: K+, K- with E+ = E-, P+ = -P-, neither supplied.
- Negative control: SHAPE ORIENTATION IS NOT POLARITY. Any classifier from an
  arbitrary principal axis manufactures polarity. Candidate P must arise from
  dynamics/topology and flip under an intrinsic symmetry of the law.
- Ladder: paired states < conserved polarity < particle/antiparticle
  phenomenology (annihilation into delocalized modes, pair creation, total-P
  conservation). Do not skip rungs.
- D15 convergence gate (one-way, only if P-track independently produces it):
  derived 2D dynamics with operator J satisfying J^2 = -I, J^T G J = G,
  [U,J] = 0. A bare Z2 exchange C^2 = I is interesting polarity phenomenology
  but NOT emergent complex structure. Gate fires only on J; otherwise D15
  stays closed and P-track stands alone.
- Starting kit (earned, formation branch): real graph state machine, D5inf
  dynamics, finite kmax ~= 4 structural scale, localized spontaneously
  selected cores, exchange/churn dynamics, no global orientation, no sheet
  preference. No C, no Weyl, no chirality, no J imported.
- Inheritance (filed): D5inf-plateau-achiral (Stage-0 NULL 0/6, circulation
  was candidate #1, FAILED); single-sponge + dust (count-vs-N, steps 5-7 need
  prepared two-blob initials, flagged for non-interference review:
  states-not-rules, scattering methodology); J2-orientation (c) ISOTROPIC
  (Aut(J2) survey complete: translations broken only); SSB-1 SPONTANEOUS
  (location degeneracy shown, TYPE degeneracy open). P-track begins where
  polarity-paused left off, with a NEW degeneracy search (not circulation).

## P0 — Degeneracy survey (prereg, FROZEN-2026-10-01)

Question: do finite localized D5inf objects have multiple LONG-LIVED types at
matched size/energy (same U, same N/E, same plateau T*, same k4 mass band)?

U (locked): D5inf ONLY (E-conserving relocation, accept iff gain-Dt >= 1,
uniform loser edge + uniform gainer non-edge, blind-propose, H-gate-clean).
No kappa, no D3-gating, no geometry, no labels in law. Dynamics seed varies;
soup fixed per cell (below).

Cells (locked, 64 runs total, all to cap 2000sw, plateau 1500-2000):

- P0-A (PRIMARY): J2-torus L28 (N=1568, exact symmetry, imprinting impossible
  by construction) x dyn d0-31 (32 runs).
- P0-B (N-check): J2-torus L42 (N=3528) x dyn d0-15 (16 runs).
- P0-C (disorder-check): ER-8 N=1600 soup-seed S0 FIXED x dyn d0-15 (16 runs;
  same-soup design isolates dyn-selected variation, SSB-1 precedent).

Snapshots (locked): every-100th saved edge lists (formation_run `saved`) at
1500,1600,1700,1800,1900,2000 (6 plateau points) + final state. No new
logging (observation-pure by construction; saved-states are default).
T-match not needed (fresh trajectories, not same-trajectory reruns).

Core definition (frozen, SSB/J2 precedent): floored k4-truss node set
(nx.k_truss(g,4), floor = max(2, N//100), union of components >= floor).
If empty (not expected for D5inf plateau): run EXCLUDED from clustering,
filed as empty-core (not imputed). If multi-piece: union for mass/count/
conductance/clustering; LARGEST connected component of induced subgraph for
diameter/mean-distance/spectral (pre-registered split, no shopping).

Features (locked, ALL Aut-invariant graph-intrinsic, NO background coords,
NO principal-axis, NO centroid, NO orientation):

- Matching (A, NOT degeneracy axes): A1 k4mass (floored core nodes),
  A2 T (triangle total, formation_run t_trace final), A3 E0 (conserved,
  constant per cell, filed for E-exactness check).
- PRIMARY triad (B/C, degeneracy axes): F1 core-mean-local-clustering
  (induced-subgraph mean C over core nodes with induced-degree >= 2; 0 if
  none qualify), F2 core-conductance (boundary-edges / core-volume where
  volume = sum of full-graph degrees over core; 0 if volume 0; lower =
  compact), F3 hub-dominance (full-graph zmax over core / k4mass; higher =
  hub-like).
- SECONDARIES (descriptive ONLY, no verdict weight, filed full): kmax,
  k3mass (raw nodes in 3-truss), k4raw (nodes in 4-truss, no floor),
  k5present (bool) + k5raw, triangle-Gini (global, SSB def), core-global-C
  (induced triangles*3 / wedges; 0 if no wedges), topz-C (local C of
  max-degree core node in FULL graph; hub-vs-clique), core-zbar-induced,
  core-zmax-full, core-internal-density, core-assort-induced (None if
  zero-variance), core-diameter-LCC, core-mean-dist-LCC, core-laplacian-a2
  (algebraic connectivity of LCC, None if LCC < 3), core-adj-gap (l1-l2 of
  induced-LCC adjacency, None if LCC < 2), core-bipartivity
  (-lmin/lmax of induced-LCC adjacency, None if LCC < 2 or lmax 0),
  global-IPR + support50-core-fraction (SSB defs), k4mass-CV (6 snaps),
  Jaccard-1500-2000 + persistence-1500-2000 (anatomy defs), T-slope-late
  (linear fit 1500-2000 per 100sw), accept-rate-plateau (NOT logged here;
  DEFERRED to reruns if needed — filed gap, not measured in P0).

Matching control (locked): residualize PRIMARY triad vs log(A1) + A2 via
ordinary least squares per cell (design matrix [1, logmass, T], 3 separate
regressions, deterministic numpy lstsq). Cluster on STANDARDIZED residuals
(z-score per feature within cell, ddof=1; if sd 0, feature DROPPED and filed,
clustering proceeds in reduced dim; if all sd 0, cell NULL by degeneracy).
This guarantees clusters are NOT size/energy differences. Report Cohen's d
for A1/A2 between clusters as check (expect |d| < 0.8 if matching worked;
filed, not gated).

Clustering (locked): deterministic 2-means (k-means++ init with seed 0,
100 Lloyd iters, tie-break by lowest index; implemented in polarity.py, no
sklearn) on standardized residuals. k=1 baseline = total variance. Metrics:
WCSS ratio (1 - WCSS2/WCSS1 = variance explained), mean silhouette s_obs
(Euclidean, pre-registered formula; singleton cluster => s_obs = 0, no
positive on singletons). Null: 100 independent-feature permutations (each
column permuted with seed 1000+i, same 2-means, record s_null); POSITIVE
needs s_obs > max(s_null) (100/100, p < 0.01 permutation) AND s_obs > 0.30
(moderate separation, pre-registered floor, not tuned).

Replication (locked): PRIMARY cell P0-A must be positive alone. Then need
>= 1 of P0-B/P0-C independently positive (same pipeline per cell) AND
centroid-separation cosine > 0.5 between P0-A and that cell (same direction
in (F1,F2,F3)-residual space, sign-insensitive |cos|). Else REPLICA-FAIL.

Persistence (locked, long-lived check): assign each run's 6 snapshots to
P0-A centroids (nearest, standardized with FINAL-snapshot mean/sd). Run
STABLE if >= 5/6 snapshots same label. Need >= 80% stable runs in P0-A for
positive (long-lived types, not flicker). Else FLICKER-FAIL. (Secondaries:
report per-feature 1500-vs-2000 Pearson r, descriptive.)

Negative controls (locked, REJECT positive if any fires):

- NC-shape: if 2-means on quadrupole-axis-angle alone (J2 readout, filed
  justification) gives adjusted-Rand-index > 0.6 vs primary labels, REJECT
  as manufactured-orientation (shape is not polarity).
- NC-size: if |Cohen's d| for A1 or A2 between clusters > 1.5, REJECT as
  size/energy split (matching failed).
- NC-location: J2 centroid distances between clusters vs within (permutation
  p); if clusters are spatially segregated (p < 0.01 AND between-mean >
  within-mean + 1 torus-sigma), FLAG as location artifact (translations
  already known-broken; type must survive translation). Filed; REJECT if
  severe (pre-registered: between/within ratio > 1.5).
- NC-singleton: any cluster with < 10% of cell runs => no positive on that
  cell (outlier, not type).

Decision (locked):

- P0-POSITIVE ⟺ P0-A positive (silhouette + null + floor) AND replication
  (>=1 secondary, cosine gate) AND persistence (>=80% stable) AND no NC
  fires. Then file cluster profiles (centroid means in ORIGINAL units,
  sizes, T, secondaries by cluster) + proceed to P1 prereg (pairing/symmetry
  design, gated).
- Else P0-NULL: file "D5inf-single-type in primary space" (no degeneracy
  found at this resolution; secondaries descriptive; polarity stays paused
  OR P0b prereg with new axes gated on review, no silent re-shopping).
  Single-cell positives without replication = HINT (filed, not discovery).

Non-interference (locked): fresh trajectories (no prepared initials, no
rule changes, no logging beyond default saves); frozen core + frozen
features; plateau window anatomy-consistent; J2 primary (exact symmetry);
ER secondary (disorder robustness). No D15 imports (no complex, no Weyl,
no J, no chirality labels). Analysis code deterministic (seeded), pinned
(tests/test_polarity.py), observation-pure (feature extraction never
mutates graph).

Cost (filed): 64 runs x (50-150s) / 64 workers ~= 2-4 min wall on beast
+ feature post (~10s/run, truss + spectral on LCC <= ~400 nodes) ~= 10 min
total. Resume-safe part files (beast-only scripts, grid above reproduces).

Next (gated): P0 verdict here; P1 (pairing/symmetry) prereg only if
P0-POSITIVE; P0b (new axes) only via review (no silent iteration).

## P0 VERDICT — NULL (D5inf-single-type, 64/64 runs, beast)

64/64 cap-2000 (P0-A L28x32 + P0-B L42x16 + P0-C ER1600-S0x16, D5inf,
~4min wall/64 workers + post). 0 empty cores (excluded 0/64). E-exact
64/64 (filed). Masses 109-280 (means 203/211/191), T* 3487-7038
(means 3570/6892/3564, ER-like for J2 (triangle-free-bootstrap
replicated!)). Jaccard-1500-2000 0.09-0.23 (EXCHANGE churn replicated!).

PRIMARY (residualized (logmass,T) + standardized, 2-means, 100-perm null):

- P0-A: s_obs 0.252 < max_null 0.405 AND < 0.30 floor (varexp 0.279,
  n0/n1 13/19, d_mass -0.20, d_T -0.40 (matching worked!),
  orig-centroids F1 0.1375/0.1350 (diff 0.0025!), F2 0.518/0.495,
  F3 0.226/0.231) => NULL.
- P0-B: s_obs 0.304 (> floor) BUT < max_null 0.451 (varexp 0.389,
  n 7/9, d_mass 0.17, d_T -0.16) => NULL (fails null).
- P0-C: s_obs 0.350 (> floor) BUT < max_null 0.456 (varexp 0.419,
  n 6/10, d_mass -0.05, d_T -0.10) => NULL (fails null).
- Cosines cosAB 0.799 / cosAC 0.623 (moot, no positives to replicate).
- Persistence P0-A: 11/32 stable (frac 0.344, need >= 0.80)
  => FLICKER-FAIL (even the null-split flickers; snapshot-clarification
  filed pre-analysis: FINAL-fit OLS coeffs applied to snapshot's own
  (logmass_s,T_s), then FINAL mean/sd (feature-blind at amendment time:
  only mass/T logs opened, F1/F2/F3 unopened)).
- NCs moot (no positive to reject; singleton gate passed anyway
  (min-cluster 6/16 = 37%)).

0/3 cells positive (not even HINT: single-cell positives need null-pass,
none passed). => P0-NULL per decision rule.

SECONDARIES (descriptive, filed full, no verdict weight — all TIGHT,
single-type-consistent, several replications):

- kmax 4-5 (means 4.06-4.16, mostly 4 (LOCKED replicated!));
  k3mass 528/1053/535 (sd 4-7, tight!); k4raw 223-339 (sd 17-22);
  k5present 5/32 + 1/16 + 1/16 (rare flicker (anatomy raw-flicker
  replicated!)); Gini 0.76/0.79/0.76 (sd 0.002-0.003, TIGHT! (SSB
  0.76/0.79 replicated!)); IPR 0.0026/0.0014/0.0025 (SSB replicated!);
  topz-C 0.04-0.06 (hubs (C<<1 replicated!)); core-density
  0.05-0.07 (sd 0.003-0.006); assort ~0 +/-0.03 (mixed);
  diam 4 (A/C constant!) / 4-5 (B); meandist 2.34/2.60/2.35
  (sd 0.03-0.05); bip 0.46/0.51/0.47 (sd 0.02); a2 2.3-3.8;
  gap 4.5-7.0; sup50-core-frac 0.53-0.75 (widest secondary
  (sd 0.08-0.14, range 0.24-0.96) but unimodal-range, NOT tested
  for bimodality (would need new prereg, no shopping here));
  massCV 0.12/0.26/0.12 (Stage-0 O3 0.13-0.27 REPLICATED!);
  Tslope-per100 +18/+24/+43 (sub-%-drift (anatomy +0.5%/100sw
  REPLICATED!) + aging-consistent (positive-but-small (approach
  disclosed!))).

FILED: "D5inf-single-type in primary space" (no degeneracy in
(clustering, conductance, hub-dominance) residuals at matched
size/energy; 19 secondaries tight/unimodal-range; 7 replications
of formation-branch numbers (bootstrap, churn, kmax-lock, Gini/IPR,
hub-C, massCV, Tslope)). Location degeneracy (SSB-1) stands;
TYPE degeneracy ABSENT here. Circulation (Stage-0) + intrinsic
structure (P0) BOTH null => polarity stays paused for pure-D5inf
spontaneous single-blob.

NEXT (gated on review, no silent iteration):

- P0b-mobility (STRONGEST hint: Stage-0 sitters (3 confined, alpha~0)
  vs wanderers (3 diffusive, alpha~0.75-1.05) + 1 slither anecdote
  (N=6, heterogeneity-mechanism-OPEN!)): confirmatory MSD-alpha
  bimodality at matched mass/T + persistence + N-replication.
  Unsigned (alpha is not signed) => paired-states rung ONLY (not
  polarity yet); needs J2-readout justification (displacements are
  translation-invariant (survives translation by construction!) but
  background-dependent (filed gap)).
- P0b-sheet (J2 sheet-composition bimodality? verdict says 0.49-0.50
  preserved, no hint filed — LOW priority unless mobility positive).
- P0b-dynamics (exchange-current invariants beyond circulation?
  Jaccard tight (no churn-rate types); other currents unmeasured —
  needs new logging prereg (endpoint-moves available!)).
- D3xinf-formation (NEW U, D14-side: hard-gain MAY nucleate (25k
  closes predicted); needs formation campaign FIRST (scale? SSB?),
  then P-track IF it forms finite-scale localized objects).
- Two-blob scattering (COUNT-VS-N flagged: prepared initials needed
  for steps 5-7; states-not-rules review REQUIRED before any
  two-blob work (non-interference!)).

D15 gate: NOT fired (no J, no C, no P; D15 stays closed (read-only)).
P-track stands alone as degeneracy-null result (discovery/characterization
mandate honored: searched, found single-type, filed).

## P0b-mobility — Dynamical-degeneracy confirmatory (prereg, FROZEN-2026-10-01)

Question: do D5inf plateau cores split into multiple LONG-LIVED mobility
classes at matched mass/T/shape/age/churn (same U, same N, same plateau)?
Pilot hint (Stage-0 N=6, preregged bins, opened): 3 confined (alpha~0,
rms 2-4, sit+jiggle) + 3 diffusive (alpha~0.75-1.05, wander torus-scale,
uncorrelated-steps (NOT flicker!)) + 1 slither anecdote (L42-d0 x-rod
sliding, N=1). P0b is confirmatory (N=48, 42 blind + 6 pilot-overlap filed
below), NOT exploratory. Unsigned (alpha) => paired dynamical states rung
ONLY (not polarity); polarity transformation/conservation gated on a
preregisterable signed split (not here).

U (locked): D5inf ONLY (same as P0, no changes).

Cells (locked, 48 runs, plateau 1500-2000, k4_window logging):

- P0b-A (PRIMARY): J2 L28 (N=1568) x dyn d0-31 (32 runs, SAME soup+dyn as
  P0-A (trajectories bit-identical by determinism; T-match 32/32 vs P0-A
  REQUIRED (apparatus-validity gate, Stage-0 6/6 precedent))).
- P0b-B (N-check): J2 L42 (N=3528) x dyn d0-15 (16 runs, SAME as P0-B,
  T-match 16/16 vs P0-B REQUIRED).
- NO ER cell (mobility needs J2 readout basis; ER has no coords;
  filed limitation (background-dependent readout, displacements
  translation-invariant by construction (survives translation!))).
- Pilot overlap (filed, NOT hidden): L28 d0-3 + L42 d0-1 (6/48) alpha
  OPENED in Stage-0 (bins pre-specified there, reused here); 42/48 blind
  to alpha. P0b gates (bootstrap null, persistence 80%, bin-alignment,
  NCs) are NEW (unopened, P0-precedent). Mass/T/structure for all 48
  opened in P0 (controls may be known; degeneracy axis (alpha) blind
  except pilot 6).

Logging (locked, pinned apparatus): k4_window=(1500,2000) per-sweep floored
k4 node sets (frozen SSB/J2/Stage-0 definition: union, floor max(2,N//100)),
NO endpoint moves (mobility only, minimal logging). Observation-pure
(pinned: T-match with/without logging). Empty sweeps: carry-forward centroid
(if first sweep empty (not expected), use (0,0); file empty fraction;
Stage-0 empties <=0.4% precedent).

Observables (locked, J2-readout justification filed: circular-mean centroid
+ minimal-torus displacements, translation-invariant (survive translation!)
but background-dependent (limitation, not intrinsic)):

- PRIMARY: MSD exponent alpha over 1500-2000 (501 per-sweep union-centroids,
  circular mean (background coords), MSD(tau) for tau=1..100 via minimal
  torus disp, log-log OLS (log MSD vs log tau); if all MSD=0, alpha=0
  (static, locked); zeros excluded from log fit (filed)). Bins (Stage-0
  reuse, prespecified): alpha<0.7 CONFINED / 0.7-1.3 DIFFUSIVE / >1.3
  DIRECTED. rms = sqrt(MSD(100)) (displacement scale at max lag, filed).
- CONTROLS (matching, NOT axes): log(mass_final), T_final (P0 values reused,
  T-matched), anisotropy_final (quadrupole ani, J2 def, 0..1), Tslope-late
  (per-100sw, P0 def), Jaccard-1500-2000 (P0 def, from k4sets endpoints),
  massCV-per-sweep (501-point CV, new precision (P0 6-point CV replicated
  as check!)).
- FLICKER (artifact controls): jump_frac (fraction of 500 steps with
  torus-step >10 (unphysical for diffusion (filed threshold, ~2x sitter-rms
  + core-spread))); step_autocorr (lag-1 Pearson mean of x/y step series;
  0 if sd 0 (filed); true diffusion ~0, back-and-forth flicker <<0);
  ncomp_6pt (P0 6-point ncomp reused (same trajectories!); multi-piece proxy).
- SECONDARIES (descriptive): per-half alphas (1500-1750, 1750-2000, same fit),
  axis-angle-final (quadrupole ang, for slither check (axis-aligned mobility?
  N=1 anecdote replication? filed, not gated)), empty_frac.

Matching (locked): OLS residualize alpha vs [1, logmass, T, aniso, Tslope,
Jaccard] per cell (6-coeff, numpy lstsq, deterministic). Cluster/test on
residuals (NOT raw alpha) to guarantee classes are NOT mass/shape/age/churn.
Report Cohen's d for all 5 controls between clusters (expect |d|<0.8; filed).

Bimodality (locked, 1D): deterministic 2-means (polarity.py kmeans2, seed 0,
100 iters) on residualized alpha (standardized? NO — 1D residuals already
comparable; use RAW residuals (filed, no z-scoring in 1D (scale = alpha units,
interpretable!))). Metrics: s_obs (mean silhouette, Euclidean 1D; singleton
=> 0), varexp. Null: Gaussian parametric bootstrap (100 sims, N(mean_resid,
sd_resid) with same n, seed 2000+i, same 2-means, record s_null; POSITIVE
needs s_obs > max(s_null) (100/100, p<0.01) AND s_obs > 0.30 (P0 floor reuse,
not tuned)). Singleton gate: min-cluster >=10% else no positive. NOTE: P0
permutation null is VACUOUS in 1D (filed!); bootstrap replaces it (1D-only
deviation, pre-registered here).

Replication (locked): P0b-A positive alone REQUIRED. Then P0b-B independently
positive (same pipeline) AND bin-alignment: low-cluster mean RAW alpha <0.7
AND high-cluster mean RAW alpha in 0.7-1.3 (label-invariant) in BOTH cells
(split aligns with Stage-0 confined/diffusive bins, not arbitrary cut).
Else REPLICA-FAIL (single-cell = HINT, filed not discovery).

Persistence (locked, long-lived): per-half alphas (1500-1750 vs 1750-2000,
same fit, residualized with FINAL-fit coeffs? NO — halves use own mass/T?
Halves have own (mass_mid? T_mid?) — SIMPLER: persistence on RAW alpha bins
(not residuals): run STABLE if both halves same Stage-0 bin (confined/
diffusive/directed). Need >=80% stable in P0b-A (P0 threshold reuse).
Else FLICKER-FAIL. (Raw-bin stability tests whether mobility type persists,
independent of matching; residualization is for discovery, bins for
persistence (filed split).)

NCs (locked, REJECT positive if any fires):

- NC-control: |Cohen's d| >1.5 for ANY of 5 controls => size/shape/age/churn
  split (matching failed).
- NC-shape-coupled: |d_aniso| >1.5 SPECIFICALLY (even if others pass) =>
  shape-coupled mobility (elongated rods vs round blobs (slither-generalized?),
  not pure mobility type; needs review, no positive).
- NC-flicker: wanderer-cluster jump_frac mean >0.05 (>5% unphysical jumps)
  OR step_autocorr mean <-0.3 (back-and-forth) OR ncomp_6pt multi-fraction
  Cohen's d >1.0 (wanderers = multi-piece flicker) => FLICKER artifact.
- NC-singleton: min-cluster <10% => outlier, not type.
- NC-location: N/A for mobility (displacements translation-invariant by
  construction; filed, not tested).

Decision (locked):

- P0b-POSITIVE ⟺ P0b-A positive (silhouette + bootstrap + floor + singleton)
  AND P0b-B positive + bin-alignment (both cells) AND persistence >=80%
  AND no NC fires. Then file cluster profiles (raw alpha means, rms,
  controls by cluster, per-half stability) + proceed to temporal-mode
  characterization prereg (gated: what distinguishes the classes beyond
  alpha? churn? shape dynamics? currents?).
- Else P0b-NULL: file "mobility-continuum" (no dynamical degeneracy at
  matched controls; sitter/wanderer = continuum sampling (N=6 small-n) or
  control-correlated (age/shape/churn), NOT types) => PAUSE pure-D5inf
  polarity entirely, wait for coupled K+psi system (per review).

Non-interference (locked): same trajectories as P0-A/B (T-matched 48/48,
k4 logging observation-pure, pinned); frozen core + frozen bins (Stage-0
reuse); plateau window anatomy-consistent; J2 readout justification filed
(displacements survive translation; background-dependence disclosed); no D15
imports. Analysis deterministic (seeded), pinned (polarity.py extensions +
  tests), observation-pure.

Cost (filed): 48 runs x (70-250s with k4 logging) / 64 workers ~= 3-5min wall
+ post (~5s/run MSD + spectral already in P0 (reused!)) ~= 8min total.
Resume-safe part files (beast-only scripts, grid above reproduces).

Next (gated): P0b verdict here; temporal-mode characterization prereg ONLY if
P0b-POSITIVE; else PAUSE (K+psi wait).

## P0b VERDICT — NULL (mobility-continuum after controls + intermittent, PAUSE)

48/48 cap-2000 (L28x32 + L42x16, k4sets 501/501, T-match 48/48 vs P0-A/B
(observation-pure PINNED!)). Amendment-1 unwrap fix applied (per-pair folding
REJECTED, pilot-anchored: S0-vs-P0b k4sets 0/501 differ (L28-d1), unwrapped
recovers Stage-0 diffusive range).

FIXED alpha (unwrapped, tau 1..100): A mean 0.568 sd 0.422 range 0.057-1.156
(16 confined + 16 diffusive); B mean 0.657 sd 0.420 range 0.068-1.144
(5 confined + 11 diffusive). Pilot 6/6 REPLICATED (counts 3C+3D EXACT +
ranges: diffusive 0.86-1.02 (Stage-0 0.75-1.05) + confined 0.06-0.08 (~0)).

GATED TESTS (residualized vs 5 controls, 1D 2-means, Gaussian bootstrap):

- P0b-A: s_obs 0.650 (> 0.30 floor) BUT < max_null 0.755 (null mean 0.583;
  gated-null (singleton-excluded) max 0.719, STILL fail) => NULL.
- P0b-B: s_obs 0.653 < max_null 0.771 (gated same) => NULL.
- Persistence (raw-bin halves): A 25/32 (0.781, miss by 1), B 10/16 (0.625,
  miss by 3) => FLICKER-FAIL (both <0.80; flips DRASTIC (1.03->0.07,
  0.15->0.93, across gap, NOT threshold jitter)).
- Bin-alignment TRUE both (lo 0.25/0.40 confined, hi 0.93/0.91 diffusive)
  but MOOT (no positive). NC-controls pass (all |d|<0.85); B-flicker FLAG
  (diffusive-cluster jump 0.113 (d12 0.33 + d15 0.15, multi-piece), A clean
  (0.012/0.032)); NC-shape-coupled pass (aniso d 0.20/0.16 residual-clusters).

0/2 positive => P0b-NULL per decision rule.

POST-HOC (filed, NOT discovery, needs new prereg to adjudicate):

- RAW gaps STRIKING (A 0.41 (0.15->0.57, 4x next), B 0.635 (0.09->0.72, 6x
  next); 13/19 + 5/11 splits; rms 3-4 (low) vs 21-48 (high), d -2.5/-1.8).
  BUT residuals FILL gaps (A max-gap 0.116, B 0.145, no dominant; continuum;
  silhouette Gaussian-consistent) => "collapses to continuum after controls"
  (mentor pause-condition MET (multivariate; univariate aniso d~0.95 BUT
  SIGN-FLIPS N (A +0.98 sitters-elongated vs B -0.95 sitters-round) => no
  robust single driver; joint-controls fill (R^2 0.20/0.46, adj 0.05/0.19;
  B 6-params-on-16 OVERFIT-flagged (filed methods concern, not verdict))).
- INTERMITTENCY (NEW phenomenology): A flips 7/7 CLEAN (efrac 0, mf 0 (6/7),
  jf<0.05, mcv stable; REAL start/stop (sit-then-wander (d9) + wander-then-sit
  (d1/d6/d20))); mobility is BURSTY, not steady-state. Full-window alpha =
  burst duty-cycle proxy? Non-bursters (<=0.15) vs bursters (>=0.57)? Trait
  (ever-burst) vs waiting-time CONTINUUM needs LONGER horizon (T×2? new
  prereg, NOT here). Halves (251pt) too short for bursty persistence (filed).
- B CONTAMINATION flag (d12: jf 0.33, mf 0.50, rms 87; d15: jf 0.15, rms 70;
  jumps+multi inflate B-diffusive (A clean, B mixed; N-replication WEAKENED)).

FILED: "mobility-continuum after controls + intermittent (not long-lived
types)". Sitter/wanderer (Stage-0 N=6) = BURST-SAMPLING + control-correlated
gap (NOT stable types at matched controls; halves flip cleanly). P0 (static)
+ P0b (mobility) BOTH null => PAUSE pure-D5inf polarity ENTIRELY, wait for
coupled K+psi system (per review). No P0b-dynamics (exchange currents) w/o
preregisterable split (none found); no two-blob polarity (no K± to collide).

D15 gate: NOT fired (no J/C/P; stays closed). P-track closes pure-D5inf leg
as double-null (static single-type + mobility continuum/intermittent);
ledger stands for K+psi re-entry.


## P0b AMENDMENT-1 (analysis-bug fix, PRE-VERDICT, pilot-anchored, not shopping)

BUG: P0b analysis as coded used per-PAIR minimal torus disp for MSD
(|c_{t+tau}-c_t| folded to [-L/2,L/2] per pair). On wrapping paths
(centroid circles the torus: x-range 0-28 observed!), folded MSD saturates
at (L/2)^2 and log-log slope -> 0 ARTIFACTUALLY (all 48 confined 0.03-0.15,
rms capped <=9.2). The Stage-0 diffusive bin (0.7-1.3, wander torus-scale)
is UNREACHABLE under per-pair folding (any torus-scale sad path wraps and
scores ~0). PROOF: identical k4sets (S0 vs P0b L28-d1, 0/501 differ,
T-match) score diffusive in Stage-0 (0.75-1.05 range) but confined (0.10)
in our buggy code.

FIX (locked): UNWRAP trajectory (accumulate minimal PER-STEP disp from t0,
standard for diffusion on periodic domains), then Euclidean MSD on unwrapped
path (no torus cap). Check on same data: L28-d1 unwrapped alpha 0.86
(diffusive, Stage-0 range!) rms 13.2 (torus-scale); max-rms run unwrapped
0.96 / 45.8 (multi-wrap diffusive). Prereg "minimal torus disp" clarified as
per-STEP minimal + accumulate (unwrapped); per-PAIR folding REJECTED as
inconsistent with bins (filed reasoning: bins presuppose unwrapping).
All other gates unchanged (bootstrap, floor, replication, persistence, NCs).
Pilot replication REQUIRED: fixed code must recover >=1 diffusive among
Stage-0-overlap 6 (else still buggy). Verdict follows fixed analysis.



