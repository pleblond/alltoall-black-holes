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
