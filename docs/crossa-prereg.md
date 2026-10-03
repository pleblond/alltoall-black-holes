# CROSSA-PREREG (FROZEN pre-data; this commit predates ALL CROSS-IMPL-A campaign data)

Campaign: CROSS-IMPL-A — Mechanism of the BHQAREA0 Maximum-Information Boundary.
Mission (CROSS-IMPL-A.tex, OPEN / READY): determine WHY BHQAREA0-MAX obtained
B_e/q_e ~= 0 and h_2(P_-) ~= 1 on the BH-like 3D boundary, by factorizing
2x = r c exactly and attributing the large-size limit to quadrature,
amplitude-scale separation, a mixed mechanism, or a covariance/selection
mechanism. This campaign does not revisit the BHQAREA0 area law or construct
new BH states. No mechanism verdict is preregistered as preferred.

## 1. Frozen inputs (read-only, never modified)

Exactly two sources (spec narrow-scope rule), consumed read-only:

- (1) Banked BHQAREA0 boundary records/data on main tail `1f8aa32`
  (`data/bhqarea0/`: 50 rung records + regression/audit/freeze/comparison/
  verdict; verdict BHQAREA0-MAX): the size ladder, boundary-edge sets,
  B/q summaries, h_*/kappa_*, and the deterministic builders needed to
  reconstruct the complex boundary amplitudes for the SAME frozen battery.
  No new ensemble is generated: reconstruction replays the banked
  `bhqarea0.assemble_adjacency` + `state_psi` builders on the same
  (r, variant, state) inputs under the frozen single-thread env.
- (2) BHQAREA0/QINFO formula implementation needed for regression:
  `src/bh_graph/bhqarea0.py` (edge terms, geometry, states, expansion
  control), `src/bh_graph/qinfo0.py` (QINFO0-IDENTICAL `h2_binary`,
  sha256 `b737d5e1…c5f42`), plus their banked deps `dim3`/`graphs`
  (hashes pinned in `src/bh_graph/crossa.py` and verified by CROSSA-A).

CROSS-IMPL-A adds `src/bh_graph/crossa.py` + `scripts/crossa_campaign.py`
+ `scripts/crossa_analyze.py` + `tests/test_crossa.py` + `data/crossa/`;
it modifies no banked module and no frozen data file.

## 2. Frozen construction (mechanical factorization, pre-data)

Per rung (r, variant, state) in the BHQAREA0 battery (section 3), replay
the banked builders to obtain psi on the rung graph, then factor every
boundary edge e = (i, j) with pair amplitudes (psi_i, psi_j):

- a_i = |psi_i|, a_j = |psi_j|, q = a_i^2 + a_j^2,
  B = Re(conj(psi_i) psi_j), x = B/q (None if q = 0).
- r = 2 a_i a_j/(a_i^2 + a_j^2) in [0, 1] (0 for endpoints).
- c = B/(a_i a_j) clamped to [-1, 1] (None if a_i a_j = 0; no arbitrary
  phase is ever assigned).
- lam = a_i/a_j, loglam = log(lam) (None for endpoints; filed as an
  endpoint class, never as an infinite numeric value).
- P_- = 1/2 - x, h_Q = h2(P_-) via banked `qinfo0.h2_binary`.
- x2 = r^2 c^2 (0 for endpoints), deficit = 1 - h_Q,
  deficit2 = r^2 c^2/(2 ln 2).

Central apparatus theorem (pinned to 1e-12 on frozen cells): 2x = r c
pointwise, r = 2 lam/(1 + lam^2) = sech(log lam), and
1 - h_Q = r^2 c^2/(2 ln 2) + O(r^4 c^4) (theorem/control, not fitted).

Per-rung anatomy (all recomputed by the analyzer from filed r/c/x arrays):

- Amplitude (D): mean(r), R2 = mean(r^2), median(r) over all N_bnd edges
  (endpoints contribute r = 0); quantiles of |log lam| over non-endpoint
  edges; endpoint fraction f_r0; endpoint counts (q_zero, ai_zero,
  aj_zero, ok).
- Phase (E): mean(c), mean(|c|), C2 = mean(c^2) plus frozen quantiles of
  |c|, over defined-phase edges only. The load-bearing phase statistic
  is C2; mean(c) ~= 0 is NEVER filed as quadrature.
- Joint (F): X2 = mean(r^2 c^2) over all N_bnd (0 for endpoints),
  prod = R2*C2, Gamma = X2/(R2*C2) when R2 > 0 and C2 defined and > 0
  (else None); 2x2 contingency at the frozen midpoints R_HI = C_HI = 0.5.
- Deficit (G): on the inherited domain |x| <= 0.1, aggregate D_dom and
  D2_dom plus coverage count; the 10% bar is inherited from BHQAREA0 G-J.
- Reproduction (B): psi_sha match, max|x_repro - x_banked| (1e-12 bar),
  |S_repro - S_banked| (census bar scaled by N_bnd), hbar/kappa diffs.

Endpoint handling (C): q = 0 zero pairs, ai = 0 / aj = 0 scale-separated
endpoints, and undefined phase are filed separately with r = 0 and
c = None. They count toward amplitude separation through r = 0. For
q = 0, x/P_-/h_Q are None; for ai/aj = 0, x = 0 and h_Q = 1.

## 3. Frozen battery + tasks (deterministic, no RNG)

- `rung` x 50: headline x R_LADDER x {vacuum, vplus, vpi, vminus} (40) +
  control x R_LADDER x {vacuum} (10). R_LADDER = (1..10), MARGIN = 4,
  TOP_RUNGS = (8, 9, 10), J_DOMAIN = 0.1 are consumed from `bhqarea0`
  (never re-made). Each record carries geometry, psi-meta, r/c/x arrays,
  D/E/F/G anatomy, joint contingency, deficit aggregates, and banked
  comparison, plus a `_git` stamp.
- `regression` x 1: provenance report (CROSSA-A inputs), factor-identity
  check, deficit-expansion check, convergence-rule self-check, frozen
  ladder/domain/threshold values.
- `audit` x 1: firewall scan + fitted-param count + input hashes.
- `redundant` x 1: rerun (r=5, headline, vacuum) + (r=5, control, vacuum);
  record hashes must match (determinism; frozen single-thread env
  OMP=OPENBLAS=MKL=1 in the runner wrapper).

Total census: 53 records. Tasks fan out via xargs on beast2
(`scripts/crossa_campaign.py --task ... --outdir data/crossa`).
Analyzer: `scripts/crossa_analyze.py [outdir]` -> `verdict.json`.
Runner details: `--count`/`--print-all` frozen; `task_argv` emits
shell-safe argv with no empty-valued flags.

## 4. Frozen convergence rules + gates + verdict ladder (pre-data)

Convergence rule `classify_track` (frozen, mechanical, consumed-ladder
only; no post-data absolute threshold): for a nonnegative ladder Y(R)
on rungs 7, 8, 9, 10 with values Y7..Y10:

- ZERO (tends to zero): all four zero, or Y10 = 0 reached
  non-increasing from Y7 > 0, or strictly decreasing Y7 > Y8 > Y9 > Y10
  with Y10 < Y7/2.
- NONZERO (liminf > 0): top-3 relative-stable (successive < 5%, the
  BHQAREA0 G-E/G-L bar) or min(Y8, Y9, Y10) >= Y7/2 with Y10 > 0.
- else UNRESOLVED (ERROR on bad input: None handled as UNRESOLVED for
  Gamma, negative/non-finite as ERROR).

Applied to the headline-vacuum ladders R2(R) = <r^2>, C2(R) = <c^2>,
X2(R) = <r^2 c^2>, and Gamma(R). Gamma suppression (the frozen joint
criterion for COVARIANT) is Gamma classified ZERO (strictly decreasing
and halved over rungs 7..10); contingency tables are filed for audit.

Gates (analyzer `scripts/crossa_analyze.py`):

- CROSSA-INST: 53/53 records present, 0 run-failures.
- CROSSA-A: bank provenance passes (verdict BHQAREA0-MAX, class MAX,
  ladder 1..10, margin 4, h_* > 0.99, kappa_*/sigma_* > 0, rung files
  50/50 with count splits, regression sub-checks green, QINFO/graphs/
  dim3 hashes banked == expected == current).
- CROSSA-B: factor identity green on frozen cells; per-rung
  max|2x - r c| <= 1e-12; psi_sha match; n_bnd match;
  max|x_repro - x_banked| <= 1e-12; |S_repro - S_banked| within the
  census bar scaled by N_bnd.
- CROSSA-C: array lengths equal N_bnd; endpoint split sums; c None iff
  r = 0 with x None-or-0 as specified; r in [0, 1], c in [-1, 1];
  f_r0 recompute.
- CROSSA-DEF: analyzer recomputation from filed r/c/x arrays matches
  filed mean_r/R2/median_r, mean_c/C2, X2, Gamma (1e-6), joint counts
  and split, to the census bar.
- CROSSA-G: deficit-expansion self-check green; on |x| <= 0.1,
  |D_dom - D2_dom|/max(D_dom, 1e-9) < 0.10 at every headline-vacuum rung
  with >= 10 in-domain edges, else filed VACUOUS.
- CROSSA-H: R2/C2/X2/Gamma tracks computed (each ZERO/NONZERO/
  UNRESOLVED, never ERROR).
- CROSSA-I: control vacuum x 10 present; headline vplus x 10 present
  with S_repro = 0 and banked S = 0 (the zero-information pattern
  control); control hbar ladder filed.
- CROSSA-X: firewall scans clean (`crossa.py`, runner, analyzer),
  fitted params == 0, battery counts ok.
- CROSSA-DET: redundant hashes match exactly.
- CROSSA-MAX: BHQAREA0 MAX reproduces on the reconstructed headline
  vacuum (hbar(10) > 0.99, |hbar10 - hbar9| < 0.01,
  |hbar9 - hbar8| < 0.015).

Verdict mapping (frozen order):

- CROSSA-INCOMPLETE: any instrument gate red (any of the above), or any
  crash, or bank lacks amplitude information (psi mismatch / bank files
  missing route here via A/B).
- CROSSA-QUADRATURE: C2 ZERO, R2 NONZERO, X2 ZERO.
- CROSSA-SCALE: R2 ZERO, C2 NONZERO, X2 ZERO.
- CROSSA-MIXED: R2 ZERO, C2 ZERO, X2 ZERO.
- CROSSA-COVARIANT: R2 NONZERO, C2 NONZERO, X2 ZERO, Gamma ZERO.
- CROSSA-NONASYMPTOTIC: MAX reproduces but no frozen asymptotic
  classification is supported.

Precedence: INCOMPLETE > the four asymptotic rungs (mutually exclusive
by construction) > NONASYMPTOTIC.

## 5. Firewalls (binding)

Hard firewall (spec): no new BH simulations (reconstruction replays the
same frozen builders on the same battery; a different ensemble routes to
INCOMPLETE, never generated); no changing the BHQAREA0 state, boundary
edges, or edge selection by B/q; no calling mean(c) = 0 quadrature (C2
is load-bearing); no inferring scale separation from raw amplitude
difference without normalized r; no post-data mechanism thresholds (all
bars above are frozen pre-data); no entropy reinterpretation, event-
trigger claims, or Planck/BH coefficient fitting. Even SCALE or
QUADRATURE establishes only the mathematical mechanism by which the
already-banked state obtains B/q -> 0 and h_Q -> 1; no causal claim
about BH formation is made (spec section J).

Apparatus code tokens banned (module scan): planck, hawking, bekenstein,
holograph, a_over_4, mutual_info, correlation_entropy, h_total, htotal,
total_entropy, s_bh, area_law, two_qubits, rng, sample, samples,
threshold, fit, trigger, rate, prob, weight, measure, entropy, random,
and the JET-0 kinetics/stochastic set (see `crossa.py`). The words may
appear in this prereg and in docstrings only as negative firewall
statements.

## 6. Pre-data validation disclosure

No campaign observables (no r/c/lam, R2/C2/X2/Gamma, deficit, or tracks)
were computed or seen before freezing. Pre-prereg inspection was limited
to the banked BHQAREA0 verdict/freeze values (MAX, h_* = 0.999990,
kappa_* = 4.2207, x ~ 0.002 at r = 10, zero-pair count 0) for sizing the
apparatus and to the frozen source hashes for provenance pinning. The
convergence bars above (halving over rungs 7..10, 5% stability, 10%
deficit, 1e-12/1e-9 recompute) are round mechanical values inherited from
the BHQAREA0 precedent, not fitted to mechanism data.
