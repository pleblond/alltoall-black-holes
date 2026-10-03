# FIBER-0 — Split-Fiber Measure Constraints: Preregistration

Frozen prereg for the FIBER-0 campaign. Branch:
`cursor/fiber0-split-fiber-e2ff` (based on `main` @ `51e0bd6`).
Apparatus: `src/bh_graph/fiber0.py`, tests `tests/test_fiber0.py`,
runners `scripts/fiber0_campaign.py` + `scripts/fiber0_analyze.py`.
Reference inputs (vendored read-only, exact bytes):
`data/fiber0_split0_ledger_ref.json`,
`data/fiber0_split0_verdict_ref.json` (SPLIT0-MIXED @ `c47c6cc`),
`data/fiber0_info0_verdict_ref.json` (INFO0-MATCHED @ `276b30f`).

## 1. Mission

Given SPLIT0-MIXED's exact inverse decomposition `X = F^{-1}(M, xi)`
with `xi = (cover, d)`, determine whether existing graph-field physics
uniquely constrains a normalized physical measure `mu_M(d xi)` on the
residual inverse fiber `Xi(M)`. The inverse split given `(M, xi)` is
deterministic; the only question is where `xi` comes from. This is
narrower than MEASURE-0: the stochastic postulate (if any) is localized
to the split inverse fiber.

## 2. Frozen ontology (read-only, never re-derived)

- Contraction/split op `u-v <-> [uv]` (BR-2.5): `contract_edge`
  (simple-kind, common neighbors collapse, consumed edge discarded),
  sum map `psi_k = psi_i + psi_j`, `3^d` directed covers, `R_U = 1`.
- Event ledger (BR-2.6/CONS-0): `dN = -1`, `dE = -(1+c)`,
  `dQ = +2B_ij`, `dE_psi` parts; split ledgers (`dN = +1`,
  `dE = +(1+c')`, CONS-0K equal/norm policies); no-go (no field-
  involving linear invariant closes arbitrary contractions); no
  firing mechanism from energetics (BR-2.7).
- Physical quotient `X_phys = X / (R x U1)` (SYM0-CLOSED); exact
  isomorphism where sufficiency matters (RAND-0F).
- Equal-halves reverse condition (MEASURE-0C): full physical reverse
  support only on `psi_i == psi_j` under the frozen equal-halves map.
- History-level control (TIME0-NULL): two-boundary selection does not
  resolve splits. Scheduler multiplicity `m!` exact (INFO0-MATCHED).
- Hidden-sector states physically distinct (HIDDEN0-SEPARATED + SYM-0);
  HBR0-SIGNREV: matched hidden pairs flip virtual-ledger signs.
- Vacuum family VPLUS/VPI/VMINUS (VACFIELD0-JOINT); no candidate
  selected for a nicer measure. `V_-^hidden` representatives are
  exact pure-`P_-` states (`hidden.hidden_delta/dipole/disk`).

## 3. Epistemic firewall (binding)

No Gaussian noise, uniformity by declaration, Born/Boltzmann rules,
maximum entropy, fitted variance/exponents, arbitrary cutoffs, or
preferred cover weights in the headline derivation. `xi` is
INFORMATION a stochastic law would have to provide; it is never
called random and never given a distribution by the earned apparatus.
Rival measures (section 12) are explicit mathematical exhibits for
the non-uniqueness proof, namespaced `rival_*`, never presented as
derived. The campaign may and must return DEBT if debt is what the
data show. No RNG anywhere in `fiber0.py` or the campaign path; no
fitted parameter (`fitted_param_count() == 0` for the earned
apparatus); no post-data cutoff (all probe grids frozen below).

## 4. Frozen battery

- Tiny cells (SPLIT-0 census, every node a split cell): graphs
  `single, k2, triangle, square, star4, path4` x fields `zero,
  bonding, current, antibonding` (RAND-0 banked) = 76 cells.
- J2 spot (`L = 4`, `k = order[0]`, `d = 8`): backgrounds ZERO
  (control), VPLUS, VPI, VMINUS (`vacfield.candidate_shape`), and
  `V_-^hidden` representatives HDELTA (`hidden_delta` @ `(0,0)`),
  HDIPOLE (`hidden_dipole` @ `(0,0),(1,1)`), HDISK (`hidden_disk`
  over all coarse cells). 7 legs; overlap with SPLIT-0's J2 legs:
  zero, uniform/VPLUS, VMINUS.
- Deterministic probes (frozen constants): `D_SWEEP` (relative-mode
  sweep incl. `d = 0`), `U1_GRID = (pi/4, pi/2, pi, 3pi/2)`,
  `RADIAL_GRID` / `ANGLE_GRID` (rival verification), perms
  `reversal_perm` / `shuffle_perm(seed 11)` (banked SYM-0).
- Remote-mutation convention (SPLIT-0F scope): field mutation at
  distance >= 3 from `k`, edge toggle outside closed `N[k]`.

## 5. Section designs (A-R)

- A (fiber regression): independently reconstruct SPLIT-0 fibers
  from frozen BR-2.5/contraction primitives (own assembly, own
  quotient analysis; banked exact `split_isomorphism_classes` for
  the halves grain, as SPLIT-0 did). Require EXACT agreement with
  the vendored SPLIT0-MIXED ledger on all 76 tiny cells (physical
  cover count, continuous dimension, equal-halves support,
  deterministic core, hidden anatomy, roundtrip counts) and on the
  3 overlapping J2 legs (formula counts, `d_cont`, WL groups).
- B (physical quotient): every fiber-0 predicate checked invariant
  under `R x U1` (reversal/shuffle x U1 grid). Automorphism-related
  outcomes stay distinct, transform covariantly.
- C (endpoint swap): exact cover map `sigma: (A,B) -> (B,A)`,
  `d -> -d`. `sigma` an involution; constraint sets swap-invariant;
  rival densities exactly Z2-even.
- D (automorphism covariance): `mu_{gM}(g xi) = mu_M(xi)`.
  Tiny cells: EXACT full `Aut(M)` by brute force (N <= 5), exact
  cover orbits, exact forced-vs-free quantification. J2: full-Aut
  enumeration is infeasible (measured: `|Stab(k)| > 3000` in 0.2 s,
  uncapped infeasible), so J2 legs use exact group-free signature
  blocks `(|A|,|B|,c')` (automorphism-invariant cardinalities;
  true orbits refine blocks): inter-block weight freedom is
  witnessed soundly; block-constant rivals are full-Aut-covariant
  soundly. Transport verified per-`g` (translations, sheet swap,
  pinned VF2 decision automorphisms). Within-block across-orbit
  freedom on J2 is filed as unquantified (conservative).
- E (locality): fiber fingerprint (cover keys, `s`, fiber relation
  on `D_SWEEP`, halves point) invariant under remote mutations;
  patch-stabilizer orbit partition invariant (tiny cells only:
  J2 patches exceed the banked `STABILIZER_MAX_PATCH = 8` cap, so
  J2 legs run the fingerprint only -- same scope note as SPLIT-0;
  full-Aut/global-quotient quantities are descriptive there).
- F (deterministic collapse): full fiber never singleton (all
  cells incl. J2); halves-restricted singleton iff `d(k) = 0`
  (exactly the 4 isolated-node cells); `delta` assigned exactly
  there. F is vacuous for the full fiber (filed openly).
- G (discrete cover measure): orbit-constancy (tiny exact; J2
  block-sound). `P(c|M)` unique iff 1 cover (`d = 0`); else
  inter-orbit weights free. Never uniform-by-declaration.
- H (continuous geometry): physical `d`-fiber `C` generically
  (2 real dims), half-line `|d|/2 >= 0` all-zero (1 dim).
  Earned fiber symmetries: Z2 (`d -> -d`) generically, U1
  (rotation) all-zero. No canonical invariant volume: exhibit
  two distinct invariant volumes per class (filed theorem +
  exhibits). A volume is not a probability measure.
- I (normalizability): Lebesgue diverges (exact `pi R^2` growth);
  normalizable invariant members need a scale (two scales
  exhibited). Debt type: full radial density (no canonical
  volume exists, so I is moot as a selector).
- J (conservation/accounting): exact closed-form ledger functions
  `dQ(d) = (|d|^2-|s|^2)/2` (cover-blind) and `dEpsi(c,d) =
  const(c) + |d|^2/2 - Re(conj(d) Delta(c))` with `Delta(c) =
  sum_A psi - sum_B psi` (recovers CONS-0K at `d = 0`; verified
  vs direct on the probe grid). Census `beta = 0` covers
  (circle level sets survive even hypothetical imposition) vs
  `beta != 0` (joint-level fibers <= 2 points); cross-cover
  ledger degeneracy census. No earned principle imposes ledger
  values (CONS-0F/G no-go, BR-2.7, TIME-0 descriptive). Ledgers
  are exact, informative, and purely descriptive: full
  continuous degeneracy intact. Never an equality-to-probability
  step.
- K (energy ledger): BR-2.6 accounting on every inverse candidate
  (covers x `D_SWEEP`); orderings filed descriptive-only.
  HBR0-SIGNREV binding: matched hidden pair (same `P_+`, same E)
  with opposite-sign ledger edges on the fiber (sign-flip gate).
- L (vacuum dependence): core + D/G/H on all 7 J2 backgrounds;
  per-background debt facts filed; no leg may yield DERIVED
  (no vacuum selected for simplicity).
- M (hidden residual): M1 pair-exchange theorem (exact): `d`
  purely odd (`P_+ d = 0`, `P_- d = d`), `s` purely even.
  M2 J2 sheet-extension algebra exact under the stated
  daughter-sheet convention (daughters inherit `k`'s sheet;
  convention filed, only algebra gated). M3 retention:
  `D_merged = 0` + locally-varies reproduced (no quotient by
  remote-blindness).
- N (factorization): disjoint-support joint splits: support =
  product (exact commutation check). Measure factorization NOT
  forced: correlated rival (locality-safe marginals, exact
  normalization, Z2xZ2 invariant) valid + differs from product.
  Correlation rule filed as debt.
- O (scheduler separation): INFO-0 scheduler `m!` reproduced
  with own implementation on the battery (all `2^E` subsets
  valid+matching); vendored INFO0-MATCHED scheduler gate consumed
  as filed; `xi` schema carries no order component; fiber anatomy
  invariant across scheduler orders (multiplicity never enters
  `xi`).
- P (TIME consistency): banked TIME-0 split-step set fixed (no
  `mu` input); split-fraction map `alpha = 1/2 + d/(2s)`
  (`s != 0`) exact; rivals push forward to different weights on
  the SAME enumerated support (finite-probe demonstration, exact
  closed-form weights); TIME0-NULL non-uniqueness survives both
  rivals; no selection by uniqueness.
- Q (rival-measure proof): `rival_A` / `rival_B`, normalized
  closed forms: covers A uniform / B `(cprime + 1) / Z`
  full-support (transport-invariant, hence orbit-constant and
  R-covariant; orbit-index ranking is label-dependent, not covariant); `d`-law radial non-Gaussian
  (A exponential `e^{-r/sig}`, B Cauchy-square `(1+r^2/sig^2)^{-2}`,
  `sig_A = 1`, `sig_B = 2`); angular uniform (A) vs
  `(1+cos(2 phi_rel)/2)/2pi` (B, `s != 0`; uniform both at
  `s = 0`); half-line radial-only all-zero. Verified:
  normalization exact (symbolic + quadrature), Z2, orbit
  covariance (tiny exact; J2 block-sound), R x U1 covariance,
  locality, exact support, full support. Differ on every
  non-degenerate fiber (TV > 0).
- R (minimal new primitive): exact type per cell: inter-orbit
  weights (`n_orbits - 1` numbers; J2: `>= n_blocks - 1`),
  radial density on `|d|`, angular density (gauge-fixed
  `s != 0`), cross-cell correlation rule. DOF census filed.
  Not chosen.

## 6. Gates

HARD (apparatus; any red -> FIBER0-INCOMPLETE): H-A-fiber,
H-A-roundtrip, H-B-quotient, H-C-swap, H-D-transport,
H-E-local, H-F-collapse, H-O-sched, H-FW-firewall.
MEASURED (findings -> ladder): M-G-cover, M-H-volume,
M-I-norm, M-J-ledger, M-K-energy, M-L-vacuum, M-M-hidden,
M-N-factor, M-P-time, M-Q-rivals (validity + difference),
M-R-primitive.

## 7. Verdict ladder (frozen)

- Any HARD red -> FIBER0-INCOMPLETE.
- Else M-Q rivals valid + differ -> FIBER0-DEBT.
- Else M-H unique volume + M-I divergent + discrete unique ->
  FIBER0-NONNORMALIZABLE.
- Else M-R empty on all cells -> FIBER0-DERIVED.
- Else -> FIBER0-PARTIAL.
All rungs are data-reachable. Prediction (theorem-backed, not
assumed): FIBER0-DEBT.

## 8. Campaign layout (beast)

- Run dir `~/fiber0-e2ff` (repo checkout of this branch), venv
  `~/vactexture-1b52/venv` (shared read-only convention).
- `scripts/fiber0_campaign.py`: mp pool (`--jobs 64`),
  deterministic cells, one JSON record per cell/leg; output
  `data/fiber0_ledger.json`.
- `scripts/fiber0_analyze.py`: frozen gates -> `data/fiber0_verdict.json`.
- Full suite on beast: `pytest tests/ -n 64 --ignore=tests/test_weighted.py`.
- Reference-data provenance: `fiber0_split0_*_ref.json` exact bytes
  from `origin/cursor/split0-inverse-49b3 @ c47c6cc`;
  `fiber0_info0_verdict_ref.json` exact bytes from
  `origin/cursor/info0-structural-2034 @ 276b30f`. SHA256 recorded
  in the ledger provenance.

## 9. Required controls (mapped)

SPLIT roundtrip exact (H-A); INFO matching reproduced (H-O);
R x U1 exact (H-B); endpoint/automorphism/sheet covariance
(H-C/H-D + J2 sheet legs); locality (H-E); deterministic fibers
give delta measures (H-F); no RNG, fitted parameter, or post-data
cutoff in the headline derivation (H-FW).

## 10. Apparatus-fix log (post-data, comparisons only)

- 2026-10-03, run 1 -> run 2: first campaign returned
  FIBER0-INCOMPLETE on H-B (HDIPOLE leg), H-C (10 tiny cells),
  M-M (24 tiny cells via `pair_exchange_ok`). Diagnosis: exact
  `==` on computed floats in three boolean checks
  (`is_quotient_invariant_ok` |s| key after U1 rotation,
  `is_swap_fiber_ok` residual, `is_pair_exchange_theorem_ok`
  reconstruction), failing at 1 ulp (5.6e-17). Fix: compare
  within the frozen `FP_ATOL = 1e-12` (same tolerance already
  used by `is_sum_consistent_ok` / `is_linear_readout_theorem_ok`);
  no physics, gate, cell, or threshold changed. Pins extended
  with the failing values (`s = 0.7071067811865476`, HDIPOLE leg).
  Campaign re-run in full (run 2); run-1 ledger discarded.
