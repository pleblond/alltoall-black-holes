# JET0-PREREG — Dynamical-Jet Merge/Split Equivalence (FROZEN PRE-DATA)

**Status:** apparatus + battery + gates + ladder frozen; campaign NOT YET RUN.
Commit predates ALL JET-0 campaign runs. Branch `cursor/jet-0-dynamical-jet-d0f5`,
base main tail `e98fb34`.

**Mission (JET-0.tex, OPEN / READY):** test whether deterministic merge/split
admissibility is encoded in exact equality of the local dynamical jet of the
pre- and post-event enlarged states `X = (G, psi, Q)`, rather than an
instantaneous ledger or static equivalence. JET-0 earns at most deterministic
admissibility (`jet equivalence => event fires` is never filed).

## 1. Frozen ontology + consumed apparatus (read-only, byte-identical)

`X = (G, psi, Q)`: simple connected graphs, `psi` complex per node,
`H(G) = -A(G)`, `J = 1`, `hbar = 1` (P1/EM-0 locked). Fixed-`G` law:
`psi(t) = U_G(t) psi(0)` via Krylov (`ballistic.evolve_fixed`, QDYN precedent).
`G` and `Q` are held fixed during waiting; `Q` is the STORE-0 minimal local
store (`q = xi = (c, d)`, QDYN0B-EVENT-LOCAL: frozen between events, `E_Q` an
event-local readout). Contraction map: `sum`. Physical quotient: `R x U(1)`
(SYM0-CLOSED).

Consumed (read-only, on main): `merge0` (substrates, fields, deterministic
contraction, ledgers), `split0` (predecessors, fiber, roundtrips, minimality),
`store0` (encode/recover, roundtrip, covariance, locality, capacity),
`reservoir0` (R-formula, `W`, `A`, fiber rows), `trigger0` (21-predicate
inventory, edge quantities, causal legs), `rewire0` (admissible swaps, radius,
anchors, Aut samples), `ballistic` (H, Krylov evolution, packets),
`sym0` (R/U1/Aut transforms, Theta identity, quotient precedent), `info0`
(field-loss precedent), `hidden`/`hiddenbr` (sectors, matched pairs),
`vacfield` (JOINT shapes), `vaccomp` (VSTAG/circle), `vactexture` (frozen maps),
`vacexc` (excitation deltas), `source0` (static pins, switch legs),
`response` (kernel/front precedent), `zero` (zero certificates, modal tools),
`backreaction` (bond_B, energy_full), `conservation` (exclusive neighborhoods,
energy parts), `contraction` (contracted_state), `accounting` (ledgers),
`u0` (cover enumeration), `measure0` (debt precedent), `stability` (BR-2.7
context), `phase` (quadratures, stagger states), `formation` (J2).
Banked code stays byte-identical.

Frozen verdicts honored (on main): STORE0-REVERSIBLE (46/46),
MERGE0-DETERMINISTIC + MERGE0-ACCOUNT-DEBT (38/38), SPLIT0-MIXED, RES0-XI,
REWIRE0-DEGENERATE, TRIGGER0-CONDITION (19 candidate-conditions, zero
implications), BR27-NO-MODE, INFO0-MATCHED, SYM0-CLOSED, HIDDEN0-SEPARATED +
HBR0-SIGNREV, VACFIELD0-JOINT + VACCOMP0-COMPLETE + VACTEXTURE-GRADIENT,
VACSTAB0-ROBUST, RESPONSE0-KERNEL, MEASURE0-DEBT, QDYN0-INCOMPLETE (autopsied).

Pinned siblings (not on main at prereg; byte-identical blobs under
`data/jet0/ref/`, see `SOURCES.txt` for branch + commit + hashes):
QDYN0B-EVENT-LOCAL (`qdyn0b_verdict.json`, 51/51): `Q` frozen with all readout
drift predicted by `E_Q = F_R(M,Q)`; `R` event-local; negated-`H` backward-leg
precedent. EVENT0-EQUIV (`event0_verdict.json`, 33/33 + `event0_orbits.json`):
61 nontrivial same-`N` rewire-equivalence orbits, zero firing implications,
zero failed rungs; J2-L4 graph-first negative (zero orbits on J2).
JET-0 re-derives every consumed EQUIV number from banked modules on its own
battery (F-gate reproduction check); no per-rung EVENT-0 number is trusted.

## 2. Frozen conventions

- Bars (frozen, reused never retuned): `BAR_FP = 1e-12` (exact algebraic
  identities, jet equality), `BAR_LEDGER = 1e-9` (ledger/flow/series
  identities), `BAR_PHYS = 1e-6` (physical-vs-noise; pre-arrival diagnostic),
  `BAR_U1 = 1e-12` (phase transport). Modal/eigh cross-checks use
  `BAR_LEDGER`. Rank decisions on `N > 32` graphs use the frozen QR bar
  `1e-9` with the two-tier protocol of section B (exact recurrence check +
  stability diagnostic).
- Ladders (frozen): `T_LADDER = (0.0, 0.5, 1.0, 2.0, 4.0, 8.0)`, `DT = 0.05`
  (QDYN/EVENT-0 verbatim; DT divides every rung); L28 `T28 = (0.0, 1.0, 2.0)`,
  `DT28 = 0.1`. Witness horizon `T_WIT = 2.0`, `DT_WIT = 0.05`, forward plus
  negated-`H` backward (QDYN0B Amendment-1 precedent). Crossing refinement:
  frozen modal algorithm (`DT_FINE = 0.01` dense scan + bracket + Brent refine
  on `||F||^2`, zeros accepted below `BAR_FP`).
- Locality: rewire admissibility `R_LOCAL = 4`; remote mutation
  `MUTATION_DELTA = 0.5 - 0.25j`; causal cone `v = 8.0` (RESPONSE Bloch-max;
  operational front, diagnostic only per TRIGGER0-AMENDMENT-2 precedent).
- No RNG anywhere (generic battery uses the frozen seed list below via a
  deterministic builder). No fitted parameter (`fitted_param_count() == 0`).
- No event fires: all alternative descriptions are virtual (constructed,
  decoded, jet-compared, never adopted), TRIGGER-0/EVENT-0 virtual precedent.

## 3. Core definitions (frozen)

For candidate edge `e = (i, j)`, `r = e_i - e_j` (node-order basis),
`d = r^dagger psi = psi_i - psi_j`. `W` is the RESERVOIR exclusive-neighborhood
variable `W = sum_{Xj} psi - sum_{Xi} psi` (`conservation.exclusive_neighborhoods`
convention; `Xi = N(i) \\ (N(j) u {j})`, symmetrically). Krylov jet
`z_n = r^dagger H^n psi` (`H = -A` dense for `N <= 64`, CSR otherwise; exact
same operator). Earned identities (descriptive, never firing rules):
`i ddot = d + W`, `i zdot_n = z_{n+1}`,
`R = A + |d|^2/2 + Re(conj(d) W) = |ddot|^2/2 + Delta/2`,
`Delta = 2A - |W|^2`, `d(t) = sum_n (-it)^n/n! z_n` (entire).

Krylov order `m_e = dim span{r, Hr, H^2 r, ...}` (psi-independent, per
`(G, e)`; `1 <= m_e <= N`). Recurrence: `H^m r = sum_{k<m} c_k H^k r`
(`c_k` real; `H`, `r` real), hence `z_n = sum_k c_k z_{n-m+k}` for `n >= m`.
Jet `K = (z_0, ..., z_{m-1})`.

STORE decoder `decode_jet(G_M, psi_M, order_M, k, Q, frame)`: `X' =
store0.split_recover(...)` (read-only), `e' = (i, j)` decoded edge,
`K' = krylov_jet(X', e')` with `m` from the DECODED `(G', e')`. Quotient leg
uses `frame=None` + canonical fresh labels; exact leg restores labels.
No STORE modification; no weighting consulted.

Jet equality (two legs, both filed): EXACT = componentwise `|z_n - z'_n| <=
BAR_FP` for all `n < min(m, m')` AND `m == m'` (order match required; order
mismatch is never full equality). QUOTIENT = exact after the frozen
`R x U(1)` alignment (joint-relabel transport where labels differ; global
phase+scale from the first-nonzero-component ratio, EVENT-0 precedent; zero
jets: exact-zero preserved). Only EXACT-full counts toward the manifold;
QUOTIENT-full is filed as degeneracy-relevant (same physical continuation).

Triviality classes (frozen, checked in order; first hit wins):
T1 identity (`X'` bitwise `== X_U`: same nodes/edges/field within `BAR_FP`);
T2 quotient (`X' == X_U` mod `R x U(1)`: relabel + phase + positive scale);
T3 symmetry-transported (same-`N` only: an iso `sigma: G' -> G` with
`sigma(psi') = lambda psi` within `BAR_FP` and edge correspondence
`e = sigma(e')` (+- orientation), with the frozen transport law
`z'_n(e') = +- conj-free lambda^{-1} z_n(sigma(e'))` residual within `BAR_FP`;
i.e. the match is explained by the transport theorem);
T4 static-zero (both jets static: `z_n = 0` for all `n >= 1` within `BAR_FP`
on both sides, including the all-zero-field case);
T5 sector/vacuum (both states certified vacuum/sector-trivial: uniform
`H`-eigen, VACFIELD-JOINT/VACCOMP/texture/H-hidden with `HP_-` residual below
`BAR_FP`, or matched-pair symmetric sector; match explained by sector
membership, filed via N-records).
GENUINE = full EXACT match with none of T1--T5. Only GENUINE matches drive
the SURFACE/STATIC/DEGENERATE/NULL rungs.

## 4. Local observability theorem (C, frozen statement)

Let `(G, e)` have Krylov order `m` and real recurrence coefficients `c_k`.
Then every `z_n (n >= m)` is the fixed real-linear combination
`z_n = sum_k c_k z_{n-m+k}` of the finite jet, and `d(t)` is the everywhere-
convergent power series in the jet components. Consequently: (a) if
`K_U = K_M` EXACT-full AND the two recurrences agree coefficient-wise (same
`(G, e)` Krylov structure; automatic when STORE regression is exact), then
`d(t) == d'(t)` for all `t` (forward and backward); (b) if recurrences differ
(different graphs, e.g. rewire pairs), finite-jet match implies Taylor
agreement of `d, d'` to order `min(m, m') - 1` only. The apparatus certifies
recurrences in integer arithmetic (`N <= 32`) or float+exact-check (`N > 32`);
section S witnesses verify (a)/(b) numerically. The merged+STORE decoded
observable is `d'(t) = p(t) - q(t)` from `split_recover(M(t), Q)` with `Q`
frozen (QDYN0B mechanics).

## 5. Frozen battery (deterministic, no RNG; counts recomputed from frozen code)

- ORD (B): every `(sub, edge)` with `sub` in the 8 merge0 substrates and
  `edge` in `merge0.frozen_edges(sub)`: `m_e` + recurrence + stability.
  (~24 tasks.)
- MERGE-JET (H-merge/E/A): every `(sub, ftag, edge)` with `ftag` in
  `merge0.field_tags(sub)` (pair tags run both members) and `edge` in
  `merge0.task_edges(sub, ftag)`: true merge + STORE encode, regression,
  fiber alternatives (tiny/exhaustive: all undirected covers x full `D_GRID`
  (27); J2-L4: 25-per-`c` cover subset x `D_GRID`; J2-L8/L28: 8-per-`c` cover
  subset (frozen L28 cost cap, EVENT-0 anchor precedent) x `D_SHORT =
  D_GRID[:5]`), jet classes + triviality per alternative. (~300 tasks.)
- SPLIT-JET (H-split/E): every `split0.split0_cells()` entry (exhaustive
  covers x `D_GRID`; reference = first canonical cover + cell `d`, frozen
  outcome-blind rule) + J2 spot x `{uniform, VMINUS, zero}` (subset x
  `D_GRID`). (~13 tasks.)
- SAMEN (same-N rewire jet census; subsumes G): tiny-path4/tiny-triangle/
  tiny-diamond x `{uniform, current, antibonding}` (9) + ring-8/path-8/
  triangle/handbuilt/er-24 x `{uniform, random777}` (10) + j2-L4 x `{VPLUS,
  VPI, VMINUS, random777, zero}` (5): exhaustive admissible rewires
  (`R <= 4`, both re-pairings), triangle+spectral screens, exact iso,
  per-compat jet comparison, Aut-quotient orbits (EVENT-0 algorithm
  reimplemented from banked `rewire0`/`sym0`; `event0.py` is not on main and
  is never imported). Includes EVENT-0's 6 REG-REWIRE cells verbatim for the
  `n_phys` cross-check. (24 tasks.)
- FORBIT (F): the 15 vendored orbit-trajs: recompute traj (Krylov, same ladder/
  `DT`) + per-rung EQUIV search + jet comparison per compat triple +
  cross-check (`n_nontrivial`, compat keys) bitwise vs `event0_orbits.json`.
  (15 tasks.)
- TRAJ (K/L): j2-L4 x 12 fields (VPLUS, VPI, VMINUS, zero, random777, spike0,
  H:dipole, P:sign:A, X:packet@VPLUS, X:patch@VPLUS, TEX:sine-x, S:VPLUS:AMP)
  + ring-8 x 3 (uniform, random777, tiny:current) + path-8 x 2 (uniform,
  random777) + triangle x 1 (uniform) + handbuilt x 2 (uniform, random777) +
  j2-L28 x 2 (VPLUS, X:packet@VPLUS; T28) + INT x 2 (ring-headon,
  j2-twospike-0; EVENT-0 frozen specs): fixed-`G` evolution + per-rung jet
  census vs frozen static virtuals (true-merge fiber subset + all/anchored
  rewire alts) + modal crossing refinement + orientation. (24 tasks.)
  Merge edge per traj = first task edge (EVENT-0 TRAJ-STORED precedent).
- LOWER (M): `{j2-L4, ring-8, path-8, triangle, handbuilt}` x first edge x
  `{z1-zero, z1z2-zero}` nullspace constructions (SVD nullspace, verified
  within `BAR_FP`; feasibility = rank condition, filed) + `d = 0` / `R = 0` /
  `Delta = 0` non-containment witnesses both ways. (~10 tasks.)
- HIDDEN (N): j2-L4 x 12 tags (VPLUS, VPI, VMINUS, VSTAG, CIRCLE_pi6, H:delta,
  H:dipole, H:disk, H:checker, H:complex, TEX:sine-x, TEX:step) x 2 edges:
  sector anatomy (`P_+-` weights, `HP_-` residual, `E` certs) + fiber-alt jet
  census + triviality classification. (24 tasks.)
- SOURCE (O): `trigger0.CAUSAL_CELLS` (6) + 4 source0 switch legs (AMP/VPLUS
  release, AMP/VMINUS release, switch-ON VPLUS, switch-ON VMINUS; SOURCE0
  constructions): causal trajectories (`T = 2.0`, `DT = 0.1`) + per-rung jets
  at frozen near/far edges + pre-arrival diagnostic (`BAR_PHYS`, not gated:
  RESPONSE fronts are operational, Schrodinger flow has no exact cone) +
  crossing census. (10 tasks.)
- GENERIC (P): `{j2-L4, ring-8, handbuilt, er-24}` x `GENERIC_SEEDS =
  (777, 1234, 9999, 31337, 7)` x `frozen_edges[:2]`: deterministic
  `random_field(sub, seed)` builder (fresh seeds, `merge0` convention) +
  fiber-alt census + exact codimension (constraint-matrix rank; linear
  subspace: jets are linear in `psi`). (40 tasks.)
- WITNESS (S): 8 true-pair reps (first merge task per sub; uniform, VPLUS on
  J2) + 6 T3 reps (first compat orbit, canonical order, of 6 frozen trajs:
  ring-8-uniform, path-8-uniform, handbuilt-uniform, ring-8-spike0,
  path-8-zero, stored-ring8-uniform): forward+backward evolution
  (`T_WIT = 2.0`) of both descriptions + modal series verification. Any
  additional GENUINE matches are verified analyzer-side by the same frozen
  algorithm (nominated by frozen canonical rule, not selected post-data).
  (14 tasks.)

Estimated total ~500 tasks (`scripts/jet0_campaign.py`, beast-parallel via
xargs, nice, OMP threads 1, jobs <= 96). Records `data/jet0/*.json`
(committed): compact digests + witness lists + full rows for matches only
(match rows only: file-size cap rationale; audit rows = first 4 rows/task).
Unit pins `tests/test_jet0.py`. Full suite on beast (`pytest -n 192`,
standing `tests/test_weighted.py` skip).

## 6. Stages -> gates (scripts/jet0_analyze.py, frozen)

Instrument (any red => JET0-INCOMPLETE):
counts (11 families, exact task census vs frozen battery code); A-algebra
(`i ddot = d + W`, `i zdot_n = z_{n+1}`, `R = |ddot|^2/2 + Delta/2` residuals
below `BAR_FP` on all MERGE-JET true pairs + TRAJ rungs); B-order (exact
integer certs `N <= 32`; QR + exact recurrence check + stability `N > 32`);
C-recurrence (recurrence residuals exact + modal series agreement on 12 frozen
samples, EVENT-0 A-trigger precedent); D-decoder (`R x U(1)` representation
independence + endpoint-swap covariance, pins + campaign sample recompute);
E-regression (`pred_ok` + roundtrip + compatibility on every cross-N record);
F-orbits (orbit reproduction bitwise + transport-theorem residuals +
exact-vs-quotient filing); G-j2neg (apparatus ran: J2-L4 SAMEN complete);
H-census (complete classes); I-theta (Theta identity + jet conjugation +
history covariance); J-setsurface (see below); K-crossing (refinement
converged on all trajs); L-orientation (first-derivative rule + Theta
reversal); M-lower (constructions verify + insufficiency both ways);
N-hidden (sector certs complete); O-source (diagnostic filed + census);
P-generic (counts + codim filed); Q-unique (enumeration complete at every
full match); R-compare (all six comparisons filed with witnesses);
S-witness (series identity within `BAR_LEDGER` forward+backward for
recurrence-compatible reps; Taylor+divergence filed for incompatible);
X-firewall (symbol scan clean + `fitted_param_count() == 0`); S-report
(exactly one ladder verdict filed).

Measurement (verdict input):
- GENUINE-set: every full EXACT match of class GENUINE (across H/F/TRAJ/
  GENERIC/HIDDEN/SOURCE batteries).
- Q-multiplicity: per GENUINE point, the count of mutually-inequivalent (mod
  T1--T5) matching continuations (T1 identity excluded: it is the status quo,
  not a continuation). > 1 anywhere => DEGENERATE-track.
- J-setsurface: `Sigma_split = Theta Sigma_merge` as sets on the battery
  (merge-direction = unmerged-vs-virtual-merged; split-direction =
  decoded-evolving-vs-virtual-splits; Theta = conjugation applied on the fly
  by frozen protocol), plus the stronger `Sigma_split = Sigma_merge` on the
  TR-even (real-jet) subset. Mismatch => INCOMPLETE (apparatus: Theta
  covariance failed), not a data rung.
- K-crossed: >= 1 GENUINE alternative CROSSED (transversal modal zero, odd
  first-nonzero-derivative order... precisely: zero of `F(t)` with first
  nonzero time derivative of odd order `2k+1` in the frozen orientation rule)
  by an ordinary trajectory (TRAJ battery minus `zero` legs minus
  `H`-eigen-certified legs, EVENT-0 cert precedent). TOUCHED-only or never =>
  STATIC-track (given GENUINE exists).

## 7. Verdict ladder (frozen logic, mirrored in code)

- JET0-DEGENERATE: GENUINE exists and >= 1 GENUINE point has >= 2 inequivalent
  continuations (no deterministic admissibility).
- JET0-SURFACE: GENUINE exists, all GENUINE points unique, >= 1 GENUINE
  alternative CROSSED by an ordinary trajectory (TR-compatible by J-gate).
- JET0-STATIC: GENUINE exists, all unique, none CROSSED by ordinary trajs
  (touched-only or never; static/symmetry crossings excluded by definition).
- JET0-NULL: zero GENUINE full EXACT matches anywhere (T1--T5 only).
- JET0-INCOMPLETE: any instrument gate red (decoder/order/regression/apparatus
  failure; genuine-or-autopsy filed).

Precedence INCOMPLETE > DEGENERATE > SURFACE > STATIC > NULL.

Prediction (pre-data, not a gate): JET0-NULL. True pairs match by T1,
orbit pairs match mod quotient by the T3 transport theorem, vacuum/hidden
legs are T4/T5 static/sector; generic alternatives miss at some finite order
(jets probe cover-dependent local Krylov data; non-Aut-related covers differ
generically). Tiny-cell collisions (small `m_e`, few constraints) are the
honestly-uncertain locus: filed descriptively, ladder decides. DEGENERATE
stays reachable on symmetric cells; SURFACE/STATIC require a GENUINE match.

## 8. Firewall (binding)

No fitted jet weights, post-data truncation, near-surface scoring, fitted
equality tolerance, `R = 0`, `Delta = 0`, `d = 0`, `ddot = 0`, energy
minimization, stochastic firing, rates, or STORE modification (tex hard
firewall; symbol-scan audited). Numerical tolerance only reflects pre-frozen
floating-point error backed by exact controls (integer-arithmetic certs where
stated, modal cross-checks elsewhere). No identification with decay, nuclear
interactions, probability, measurement, gravity, or cosmology (interpretation
firewall). Even an exact crossed surface earns at most deterministic
admissibility: no EVENT-1 formula shopping follows any result.
Amendments, if any, as JET0-AMENDMENT-n with gated re-runs.
