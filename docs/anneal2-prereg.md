# Blind vacuum-annealer survey ROUND 2 — preregistration

**Status:** preregistered BEFORE any round-2 survey compute on this branch.
Pilot/estimator-dev measurements below were taken on PRISTINE CONTROLS and
short non-grid anneals only (controls-only development); no round-2 grid run
existed when this file was frozen (see §11 log).
**Branch:** `cursor/vacuum-anneal2-7d7b`, branched off round-1 branch
`cursor/vacuum-anneal-813f` (round-1 PR #51 is DRAFT/unmerged at freeze time;
V1 code + data + report all present on the parent; all 34 V1 anneal tests
green on this branch).
**Epistemic authority:** `docs/model.md` v0.4 (L0/P1–P4, L1/I1–I7, L2/F1–F6,
D1–D9) plus D10 (vacuum selection, proposed OPEN in round-1 §7 — stays open).
Every number in the round-2 report is labelled
derived / fitted / assumed / exploratory / conjectured.
**Round-1 inputs (read before designing):** `docs/anneal-prereg.md`,
`docs/ANNEAL_REPORT.md` (§§1–2, §6). Round 2 reuses the
`anneal_cost`/`anneal_core`/`anneal_measure` machinery by extension (V2
sections alongside frozen V1 code), fixes the two quantified blockers (M1
cached-potential cancellation; d_iso miscalibration at N ≤ 512), and
re-freezes every bar, weight, seed count, and schedule below. Nothing is
recycled as "known good": the grid, bars, estimator, and schedules are de
novo even where values coincide by re-derivation (coincidences noted).

## 0. Rule zero (load-bearing, unchanged)

The cost functional contains ONLY graph-intrinsic quantities. Dimension and
curvature are MEASURED on annealer output, never targeted, never constrained,
never smuggled in via constraint sets we do not ablate. Concretely forbidden
in the cost, the move set, the constraint set, and the seed handling:

- any `(d − d*)²` / `(d_iso − 3)²` term, or any function of an estimated
  dimension, volume-growth exponent, or spectral dimension;
- any term in Ollivier-Ricci κ, Forman-Ricci, entropy-curvature, clustering
  used as a flatness proxy, or any function of measured curvature;
- any large-world / small-world enforcement (diameter caps/floors, path-length
  targets, ball-growth targets) as a hard constraint or penalty;
- any coordination target `(z − z*)²` (regularity WITHOUT a z-target is
  allowed; T_reg is target-free);
- any seed-pinning that prevents the annealer from leaving the seed class
  (toggle moves always on, so z and E drift; drift is reported).

Violation handling: any run found to violate rule zero is labelled
**DISQUALIFIED** in `results/anneal2/*.json` (`"disqualified": true` +
reason) and excluded from all verdict tallies. Reported, never silently kept.

Static enforcement (extended to V2): `test_cost_is_blind_v2_extended` and
`test_core_is_blind_v2_extended` grep the cost/loop modules for the V1 token
set plus `target` and `flat` (cycle-term smuggling guards: no
`(n4 − target)`-style construction may exist) and fail the suite on any hit
outside the lexicon strip-markers; cost-never-imports-measurement is enforced
by the same tests. V1 audit tests stay green unchanged.

Falsification framing: the null hypothesis is that blind graph-intrinsic
costs do NOT select a flat-sparse-3D basin. A clean negative ("needle, not
basin") is first-class. No PASS without calibration + reachability +
persistence ALL holding (§9).

## 1. Cost functional V2 (blind only) + M1 fix (frozen)

Total V2 cost (all terms graph-intrinsic; signs frozen per-arm in §2):

```
C2(G; w) = w_E·T_edge + w_L·T_spec + w_R·T_reg + w_S·T_sym + w_Q·T_sq + w_T·T_tri
```

V1 terms (unchanged semantics): T_edge = E/N; T_spec = λ2(L)/z̄ (sparse
eigsh, §1.2 robustness fixes); T_reg = Var(deg)/z̄²; T_sym = WL-colors/N
(K_WL = 4 frozen). New V2 terms (exact-incremental, adjacency-only):

- T_sq = −(4-cycle count)/N. Minimized → square-rich (away-from-trees arm;
  trees have 0 squares; cubic lattices have ≈ 3/N squares per node —
  lattice-compatible loopiness with no dimension/curvature content).
- T_tri = (triangle count)/N. Minimized → triangle-free (bipartite-friendly);
  frozen w_T < 0 arms reward triangles (clustered direction, away from trees).

Blindness audit (new terms): both use only adjacency (common-neighbor /
4-cycle-through-edge counts). No d/κ/z-target/large-world quantity enters.
The cyclomatic count E−N+1 is deliberately NOT added: under connectivity-hard
it is affine in T_edge (redundant — documented, not smuggled). Girth was
considered and not implemented: per-proposal exact girth is O(E) with mostly
zero deltas (weak driver); squares/triangles are the frozen equivalents
(task allows "cycle-space dimension, girth, or equivalents").

Signed weights (frozen): w_L and w_T may be negative (spec-hi / trimax arms,
§2). Nonneg keys: w_E, w_R, w_S, w_Q. Sign flips post-hoc are FORBIDDEN.
`is_valid_weights_v2` enforces exactly this split.

### 1.1 M1 fix: delayed acceptance with refresh-gated block verdicts (frozen)

Round-1's cadence cache let T_spec/T_sym cancel in Metropolis ΔC (12 vectors
→ 3 drivers, verified bit-identical). Round 2 splits the cost:

- CHEAP-EXACT (per proposal, O(1) incremental): T_edge, T_reg, T_sq, T_tri
  via `_StateV2` (E, Σdeg, Σdeg², n3, n4 maintained exactly; telescoping
  verified against full recount in `test_state_v2_incremental_matches_recount`
  and end-to-end in `test_anneal_v2_final_counts_match_recount`).
- EXPENSIVE (exact at block ends): T_spec (eigsh, §1.2), T_sym (full WL).
  Every K_REFRESH = 100 accepted moves (frozen, §1.3 audit), the exact
  expensive residual Δ_exp = C_exp(new) − C_exp(old-boundary) of the whole
  block faces a Metropolis verdict at current T; reject → revert to the
  block-start snapshot (exact restore, tested). This is delayed acceptance
  (surrogate = cheap-exact, correction = expensive residual); at fixed T it
  targets the full Boltzmann distribution up to the inherited symmetric-
  proposal approximation (V1 also ignores proposal asymmetry — documented,
  no worse). When w_L = w_S = 0 the machinery reduces to exact per-proposal
  cheap annealing (block counters stay zero, tested).

Hold rule (frozen, V1 semantics): if the exact expensive evaluation fails at
a block end (eigsh non-convergence — expected in tree phases, §1.2), the
boundary is kept (block extends to the next verdict), `holds_eigsh` += 1, and
`fragile_eigsh` flags when holds/(verdicts+1) > 5%. Holds are tallied per arm
(median hold fraction in `manifest.json`); arms with median > 50% carry a
"spec-phase-limited" qualifier (descriptive). Initial-eval failure holds 0.0
(V1 would freeze on NaN — documented deviation).

KILL-SWITCH (frozen, load-bearing): after the survey, runs are grouped by
(phase, seed-id, N, seed, bridgeless) across hid; if any two hid with
DIFFERENT weight vectors show bit-identical (E, edit-distance, accepts, T0),
collapse has recurred → the affected legs are VOID exactly as round 1 voided
them (§9 verdicts restricted to surviving legs). Unit tripwire (must pass
before any survey launch): `test_kill_switch_distinct_weights_distinct_trajectories`
(H0/H1/H2/H4 pairwise-distinct at fixed config/seed; pilot: block A/R =
18/28, 5/41, 45/1 — vetoes fire). If the tripwire ever fails, the survey
does not launch.

### 1.2 Spectral backend robustness (frozen, pilot-found)

Pilot finding E1 (procedure flaw in V1's eigsh use, caught before survey):
k=2 'SM' can SKIP λ1 = 0 and return {λ2, λ3} (observed: open 20×10×20 grid
read 0.0979 = λ3 instead of 0.0246 — silently wrong, ok=True). V1 data are
unaffected (spec leg void; no verdict rested on λ2 values) but all V1 λ2
values are suspect — recorded, not used. V2 fix (frozen): k=6 with zero
detection (smallest < 1e-8 → λ2 is next; else smallest IS λ2), dense for
n ≤ 64, one deterministic retry on connected-graph double-zero, fixed start
vectors (determinism: `test_anneal_v2_deterministic_with_expensive_terms`
pins bit-identical C_total/traces/counters). Validated: ≤ 2e-13 relative vs
dense across 9 families (path/cycle/star/ER/regular/tree/cubic/diamond/fcc)
+ exact grid-theory match at N = 1000/2000/4000.

Pilot finding E2 (tree-phase non-convergence): ARPACK 'SM' cannot resolve
near-zero-clustered tree spectra at survey N (path/tree fail at
N = 1000/2000/4000 even at maxiter = 2000, ~1–2 s burned per failure).
Frozen response: maxiter = 300 (all loopy families still converge with
identical values — re-validated ≤ 2e-13; trees fail fast ~0.1 s into the
hold path). Consequence: the spectral leg holds (rather than steers) once a
run collapses to trees — phase-limited legs, flagged per run, reported per
arm. Early-phase verdicts still differentiate H1/H2/H0 (kill-switch).

### 1.3 M1-fix cost audit (measured, pilot — the preregistered choice)

Per-proposal exact eigsh is infeasible as the SOLE mechanism: 240k steps ×
≈ 0.02 s ≈ 80 min/run at N = 4000 (measured eigsh 0.01–0.05 s loopy,
0.1–0.24 s tree-fail at survey N). The frozen variant is delayed acceptance
(§1.1). Measured block-verdict cost: eigsh (0.01–0.05 s) + WL (0.004–0.028 s)
+ snapshot (4.6/9.0/22.5 ms at N = 1000/2000/4000) ≈ 0.02–0.08 s;
amortized over K_REFRESH = 100 → 0.2–0.8 ms/step, comparable to the cheap
proposal step itself (≈ 0.1–0.5 ms, swap-connectivity dominated). K_REFRESH =
100 is frozen (larger K weakens the legs; smaller K wastes verdicts; 100
balances at measured parity).

## 2. Weight grid V2 (frozen, de novo)

Numeraire w_E = 1.0 always. Grid over (w_L, w_R, w_S, w_Q, w_T). 12 vectors
H0–H11 (fresh — no round-1 weight is treated as "known good"):

| hid | w_E | w_L | w_R | w_S | w_Q | w_T | arm |
|---|---|---|---|---|---|---|---|
| H0 | 1.0 | 0 | 0 | 0 | 0 | 0 | edge-only ablation |
| H1 | 1.0 | +2 | 0 | 0 | 0 | 0 | edge + spectral-lo |
| H2 | 1.0 | −2 | 0 | 0 | 0 | 0 | edge + spectral-hi (AWAY) |
| H3 | 1.0 | 0 | +2 | 0 | 0 | 0 | edge + regularity |
| H4 | 1.0 | 0 | 0 | +2 | 0 | 0 | edge + symmetry |
| H5 | 1.0 | 0 | 0 | 0 | +2 | 0 | edge + squaremax (AWAY) |
| H6 | 1.0 | 0 | 0 | 0 | 0 | −2 | edge + trimax (AWAY) |
| H7 | 1.0 | 0 | 0 | 0 | 0 | +2 | edge + trifree |
| H8 | 1.0 | 0 | +8 | 0 | 0 | 0 | regularity-heavy |
| H9 | 1.0 | 0 | 0 | 0 | +8 | 0 | square-heavy (AWAY) |
| H10 | 1.0 | 0 | +2 | 0 | +2 | 0 | reg + squaremax (AWAY) |
| H11 | 1.0 | 0 | +2 | +2 | +2 | 0 | reg + sym + squaremax (AWAY) |

6/12 arms press away from trees (H2, H5, H6, H9, H10, H11 — pinned by test);
6/12 are treelike-compatible. Round-1's deck leaned treelike (min-λ2);
this grid spans driver space honestly in both directions (frozen signs).

No other weight vectors may enter verdict tallies. Exploratory off-grid runs
(if any) are labelled `exploratory` and excluded from PASS/FAIL counts.

Adjacency (differ in one weight by one grid step; steps: w_L −2→0→+2;
w_R 0→2→8; w_S 0→2; w_Q 0→2→8; w_T −2→0→+2). 12 adjacent pairs (frozen):
(H2,H0), (H0,H1), (H6,H0), (H0,H7), (H0,H3), (H3,H8), (H0,H5), (H5,H9),
(H0,H4), (H5,H10), (H3,H10), (H10,H11).
Pareto/artifact rule (carries over): a basin claimed as "selected" must
persist across ≥ 3 adjacent grid vectors (chains exist: H2–H0–H1, H6–H0–H7,
H0–H3–H8, H0–H5–H9, H3–H10–H11) or it is a weight artifact.

## 3. N range, lattice seeds, schedules (frozen)

Survey N: {1000, 2000} full grid. Spot N: {4000} (§3, scope below).
N ≥ 1000 hard floor (below that the ruler doesn't work — round-1 §2).

Seeds (frozen IDs, `SEED_IDS_V2` = er-sparse, rr6, cubic, diamond, fcc):

Discovery leg (random starts — carry no geometric structure):
- `er-sparse`: G(N, 6/(N−1)), ≤ 25 tries to connected (V2 cap; ER(2000+) never
  connects — 200 tries burned 20–77 s/build in pilot — then LCC + attach
  fallback, deterministic given seed; V1 default 200 preserved in code).
- `rr6`: random 6-regular, ≤ 50 offsets, else er-sparse fallback (25-try cap).

Stability leg (pristine lattices — ALL PERIODIC at survey N):
- `cubic`: periodic 10³ (N=1000) / 10×10×20 (N=2000) / 20×10×20 (N=4000).
- `diamond`: periodic 5³ (N=1000) / 5×5×10 (N=2000) / 5×10×10 (N=4000) cells.
- `fcc`: periodic 5×5×10 (N=1000) / 5×10×10 (N=2000) / 10³ (N=4000) cells.
All N exact (8 atoms/diamond-cell, 4 atoms/FCC-cell); 6/4/12-regular
(respectively) pinned by tests. PERIODICITY IS A PILOT-FORCED DEVIATION from
round-1's open-1000: the V2 estimator on OPEN survey-N fragments is seed-
flaky (open-2000: 9/10 gate passes, median 2.49, min 2.17 — boundary noise),
while periodic tilings read 3.06–3.42 with ZERO seed variance, 10/10
(controls-only evidence, §7). Bulk property → bulk boundary conditions.

Schedules (frozen from the cooling pilot, §3.1): STEPS = {1000: 60000,
2000: 120000}, SPOT_STEPS_4000 = 240000 (2× steps(2000), linear-N rule).
Alpha = 0.9995 (V1 value, carried over).

Seed counts (frozen): discovery seeds {0,1,2} per (hid, start, N);
stability seeds {0,1} per (hid, lattice, N); spot {H0,H2,H10} ×
{er-sparse, cubic} × {0,1} at N=4000 (12 runs: baseline + both
away-directions at scale); ablation §4 (16 runs).
Total: discovery 144 + stability 144 + spot 12 + ablation 16 = 316 runs.
Frozen drop order if the 6 h cap binds: spot first, then stability seeds {1},
then discovery seeds {2} — and SAY SO in the report.

### 3.1 Cooling pilot (frozen operating-point rule + measurement)

Rule (frozen): STEPS(N) = 2× the smallest pilot steps at which the collapse
arm H0 (er-sparse, seed 0, K_REFRESH = 100) shows mid→final |ΔE|/E < 5%.
Measured: H0-1000 settles at 30000 (999→999, 0%) → STEPS = 60000; H0-2000
settles at 60000 (1999→1999, 0%) → STEPS = 120000. The tension arm H10 does
NOT settle by this rule (N=1000@60k: 2828→4128, +46% late densification;
N=2000@120k: 2962→2754, −7.0%) — tension-arm cooling state is REPORTED per
arm (mid→final ΔE table in the report) and QUALIFIES negatives (round-1
§3.3 precedent), not a gate. Cause (exploratory): square/edge tension
evolves on longer timescales than collapse; freezing longer was judged
diminishing-returns vs grid breadth at fixed cap.

### 3.2 Reachability table (frozen, measured pre-freeze at CAL_SEED = 4242)

d_ctrl (periodic-cubic control diameter): {1000: 15, 2000: 20, 4000: 25}.
B4 bar = 0.5 × d_ctrl = {7.5, 10.0, 12.5} (frozen §9).

| control | d_iso | R² | κ | z | diam | B1 | B2 | B3 | B4 | member |
|---|---|---|---|---|---|---|---|---|---|---|
| cubic-1000 | 3.42 | 0.99 | 0.000 | 6.00 | 15 | ✓ | ✓ | ✓ | ✓ | YES |
| cubic-2000 | 3.06 | 0.99 | 0.000 | 6.00 | 20 | ✓ | ✓ | ✓ | ✓ | YES |
| cubic-4000 | 3.09 | 0.99 | 0.000 | 6.00 | 25 | ✓ | ✓ | ✓ | ✓ | YES |
| diamond-1000 | 4.24 | 1.00 | −1.000 | 4.00 | 14 | ✗ | ✗ | ✓ | ✓ | NO |
| diamond-2000 | 3.56 | 0.99 | −1.000 | 4.00 | 20 | ✓ | ✗ | ✓ | ✓ | NO |
| diamond-4000 | 2.98 | 0.98 | −1.000 | 4.00 | 24 | ✓ | ✗ | ✓ | ✓ | NO |
| fcc-1000 | 3.26 | 0.98 | −0.000 | 12.00 | 10 | ✓ | ✓ | ✗ | ✓ | NO |
| fcc-2000 | 3.12 | 0.98 | −0.000 | 12.00 | 12 | ✓ | ✓ | ✗ | ✓ | NO |
| fcc-4000 | 4.11 | 1.00 | −0.000 | 12.00 | 15 | ✗ | ✓ | ✗ | ✓ | NO |

Every bar is passable-in-principle at every survey N (B1: cubic/fcc/diamond;
B2: cubic/fcc with κ = 0.000 exactly; B3: cubic/diamond; B4: ALL lattices at
all N). Full membership is reachable (cubic, all N). Round-1's unreachable-B4
failure cannot recur: B4 is a fraction of control diameter by construction.
Diamond κ = −1.000 exactly (girth-6 tree-like locale, as round-1) anchors the
curved end of the B2 scale; fcc z = 12 fails B3 (dense control — expected).

## 4. Constraint ablation (frozen)

- Connectivity HARD in all runs (one space; allowed by protocol).
- Bridgelessness: ablation flag `bridgeless ∈ {off, on}` (exact `nx.bridges`
  scan per proposal — slow, frozen exactness-over-speed for the constraint leg).
- Ablation scope (frozen): {H0, H1, H2, H10} × {er-sparse, cubic} × N = 1000
  × seeds {0, 1} = 16 runs (edge-only / spec-lo / spec-hi / square-tension —
  spans the driver space). Matched off-runs exist in the main grids.
  Verdict V-CONSTRAINT is descriptive with the frozen paired rule (§9).

## 5. κ backend + operating point (frozen)

κ is an OUTCOME (P4 uniform measure, zero self-mass), evaluated at
checkpoints only (initial, mid, final), NEVER inside the cost loop.

- Backend: EXACT Ollivier-Ricci (`orici.ollivier_curvature`, P4 defaults)
  with sparse-Johnson cached distances (`sinkor.all_pairs_johnson`).
- Sample: ≤ 150 edges/run-checkpoint, uniform without replacement, RNG split
  from run seed (deterministic). Report mean ± SEM over sampled edges.
- Fallback: if Johnson fails, record `kappa_ok: false` and EXCLUDE the run
  from κ tallies (do not impute).
- Sinkhorn is NOT used (exact-only verdicts; GPU rule is vacuous — see below).

κ-cost vs N tradeoff (measured, pilot — full outcome bundle per checkpoint):
≈ 0.5 s (N=1000), ≈ 1.2 s (N=2000), ≈ 3.9 s (N=4000, worst control). Verdicts
stay exact-backend-only at all N; NO GPU is used in round 2 (no GPU on the
VM; exact CPU fits the cap — the GPU rule's condition never triggers).
Large-world stats use the Johnson-backed exact implementation
(`large_world_stats_v2`, proven equal to V1 BFS quantities in
`test_lw_v2_matches_v1_exact` — V1's O(N) Python-BFS diameter is infeasible
at survey N × 3 checkpoints).

## 6. Annealing schedule (frozen)

- Moves (proposal mix, frozen): with prob 0.5 double-edge swap
  (degree/E-preserving; n3/n4 change exactly); with prob 0.5 single-edge
  toggle (add uniform random non-edge / remove uniform random edge, 50/50).
  Self-loops and multi-edges rejected. Disconnecting moves rejected (hard).
  Bridgeless-on runs additionally reject bridge-creating moves (exact scan).
- Acceptance: per-proposal Metropolis on the EXACT cheap cost
  `P = min(1, exp(−ΔC_cheap/T))` (V1's proposal-asymmetry approximation
  inherited and documented); block verdicts per §1.1.
- Temperature: geometric `T_k = T0 · alpha^k`, alpha = 0.9995 (frozen V1).
  T0 selection (frozen procedure, not a tuned value): 200 toggle-only probes
  on the seed graph (cheap-exact deltas incl. square/triangle terms; swaps
  excluded by the V1-amendment-2 argument — they carry ΔC_cheap ≡ 0 when
  w_Q = w_T = 0), median |ΔC| over constraint-passing probes = m;
  T0 = m / ln(2); if m == 0, T0 = 1.0 fallback flagged in JSON. Pure scale.
- STEPS: §3 (60000/120000/240000). Checkpoints k ∈ {0, mid, end} with FRESH
  full V2 costs + V2 outcomes; cost trace thinned to ≤ 300 points/run
  (carries C_cheap, C_exp, E, accepts, block rejects).

## 7. d_iso estimator V2 spec (frozen) + calibration gate

Ball-boundary profile with r_min + upper-V window: for seed node s, BFS gives
V(r) = |B(s,r)|, S(r) = shell size. Model: S ~ V^((d−1)/d).

- Window (frozen): shells r_min = 2 .. r_max(s), largest r with
  V(r) ≤ f_up·N, f_up = 0.5. (Minimal change from V1: only r_min added;
  selected on pristine controls only — §7.1.)
- Seeds: n_dseeds = 20 uniform nodes (RNG split, deterministic).
- Per seed: REQUIRE ≥ 4 points else dropped. Fit OLS log S = a·log V + b;
  slope window a ∈ (−0.2, 0.95) else dropped; d = 1/(1−a).
- Aggregate: d_iso = median over kept seeds; err = max(SEM, median fit-SE);
  R² = median per-seed R². REQUIRE ≥ 8 kept seeds else `diso_ok: false`.
- Calibration GATE (frozen, must pass BEFORE any anneal run counts — applied
  at verdict time; fail-safe as round 1): d ∈ [2.0, 4.0] + R² ≥ 0.8 +
  n_kept ≥ 8 on ALL of {cubic-1000, cubic-2000, fcc-1000, fcc-2000,
  diamond-2000} at CAL_SEED = 4242. If ANY fails → estimator MISCALIBRATED →
  ALL d_iso verdicts INCONCLUSIVE (B1 unmeasurable; V-DISCOVERY,
  V-ARTIFACT-membership, V-STABILITY downgraded; constraint d-part dropped).
  All five pass deterministically (zero seed variance on periodic lattices):
  margins 0.33/0.69/0.49/0.63/0.19 (thinnest: diamond-2000 at 3.56 vs 3.75).
- Spot gate (N=4000): {cubic-4000, diamond-4000} must pass the same bar
  before spot-4000 d-counts (spot is extra-rule regardless).
- Documented below-range REFERENCES (reported, no gate weight): diamond-1000
  (d = 4.24 — 5-cell tiling too small for the window at any tried variant)
  and fcc-4000 (d = 4.11 — few-shell transient at z = 12). Exclusions decided
  on controls only, structural reasons, pre-freeze.
- Negatives (recorded, no bar): er-sparse/rr6 at survey N read ok=False
  under V2 (specificity IMPROVED vs V1: nan instead of confident-wrong
  d ≈ 6–12); path-1000 reads d ≈ 1.00 out-of-bar; balanced trees read
  d ≈ 9–15 out-of-bar. Residual risk (honest): round-1's bushy-annealed-tree
  shape is not reproducible from controls alone, so V2 misread risk on
  annealed outputs is UNKNOWN — mitigated by the gate + B1∩B2 conjunction +
  per-seed R²/n_kept reporting, stated not hidden.

### 7.1 Estimator-dev log (controls only, pre-freeze — not tuning on outcomes)

Variants tried on pristine lattices at survey N (seed 11): (r_min, f_up) ∈
{(1,0.5), (2,0.5), (2,0.7), (3,0.5)}. (2,0.5) chosen: passes cubic-1000/2000/
4000 + fcc-1000/2000 + diamond-2000/4000 (7 controls), minimal change from V1
(only r_min added), no variant passes diamond-1000 or fcc-4000 (documented
above). Open→periodic seed switch forced by seed-flakiness evidence (§3).
No anneal output was consulted at any point (none existed).

## 8. Outcomes per run (frozen JSON schema keys)

Each `results/anneal2/<run_id>.json`: run_id, phase, hid, weights (6 keys),
N, seed_id, seed, bridgeless, disqualified(+reason), steps, alpha, T0,
T0_fallback, k_refresh, block counters (accept/reject/hold), holds_eigsh,
fragile_eigsh, checkpoints[initial/mid/final] each with {E, z_mean, z_std,
T_edge, T_spec, T_reg, T_sym, T_sq, T_tri, n3, n4, C_total, spec info,
outcomes{V2 bundle: diso, kappa, z, lw, basin}}, schedule traces (thinned,
≤ 300 pts), edit_distance_from_seed, wall_s, total_wall_s, git_sha,
label ("exploratory" on every measured number).

## 9. Kill criteria / verdict bars (FROZEN — not vibes)

Basin-membership bar (ALL FOUR must hold on the FINAL checkpoint):

- B1 dimension: `diso.ok AND |d_iso − 3| ≤ 0.75 AND R² ≥ 0.75`
- B2 flatness: `kappa.ok AND |mean κ| ≤ 0.06`
- B3 sparsity: `z_mean ≤ 8.0` (no lower bound except connectivity; trees
  allowed — if trees pass B1/B2/B4 they pass, say so)
- B4 large-world: `diameter ≥ 0.5 · d_ctrl(N)` (N-aware; d_ctrl = {15, 20, 25}
  → bars {7.5, 10.0, 12.5}). Reachability proven in §3.2 (all lattices pass
  B4 at all N; cubic is a full member at all N).

(B1/B2/B3 values coincide with round-1 by RE-DERIVATION (same principled
widths: 0.75 = quarter-dimension tolerance; 0.06 = cubic-exact 0.000 with
10× SEM headroom; 8.0 = cubic-6 with headroom); margins will differ. B4 is
new (N-aware fraction replacing 2·log2 N). All re-frozen here, not recycled.)

Leg verdicts:

- V-DISCOVERY (blind runs find a flat-3D-sparse basin): PASS iff ≥ 2
  discovery-leg runs with DIFFERENT hid meet B1–B4, with at least one at
  each of N = 1000 AND N = 2000 (no single-N mirage); "SELECTED" additionally
  requires ≥ 3 ADJACENT hid (§2 chains). FAIL ("needle, not basin",
  first-class clean negative) iff 0 discovery members across the full grid
  AND gate passes AND reachability holds AND kill-switch holds (legs
  genuine) AND the H0 cooling rule met (§3.1; tension-arm drift carried as
  a stated qualifier). Else INCONCLUSIVE (gate fail → INCONCLUSIVE, never
  FAIL; lonely passes → INCONCLUSIVE-lonely downgrade, §9.1).
- V-ARTIFACT (attractor moves with weights): PASS(no-artifact) iff every
  adjacent hid pair (§2, 12 pairs) agrees on basin-membership majority
  (≥ 2/3 of matched runs agree) for ≥ 80% of adjacent pairs. Else FAIL →
  outcome is a weight artifact (record which weights drive it). Needs B1;
  gate fail → INCONCLUSIVE-membership (+ descriptive attractor map).
- V-STABILITY (seeded lattices preserved): per (lattice, hid): PRESERVED iff
  final meets B1+B2 AND edit-distance/E_seed ≤ 0.5. Leg verdict:
  STABILITY-ONLY iff ≥ 50% of stability runs PRESERVED while V-DISCOVERY
  FAILs. If V-DISCOVERY PASSes, stability is supporting. Gate fail →
  INCONCLUSIVE-membership (+ exact edit-distance descriptives).
- V-CONSTRAINT (constraint set drives outcome): DESCRIPTIVE (no PASS/FAIL):
  matched-pair Δd_iso, Δκ, Δz with paired error bars; "constraint drives X"
  iff |Δ| > 2σ_paired on ≥ 50% of pairs. Gate fail → d-part dropped.

Kill mapping: V-DISCOVERY FAIL + V-STABILITY STABILITY-ONLY → "discovery
dead, stability-only result". V-DISCOVERY FAIL + stability also fails →
"flat sparse 3D is a needle, not a basin" (clean negative, first-class).

### 9.1 Lonely-pass rule

Any PASS-pattern without §2 persistence (≥ 3 adjacent) is downgraded to
INCONCLUSIVE-lonely (single-point mirage watch). A "SELECTED" claim additionally
requires the both-N condition AND the kill-switch AND the gate — no PASS
without calibration + reachability + persistence ALL holding.

## 10. Labels, non-goals, compute (frozen)

- Every measured number: `exploratory`. No fitted numbers (weights GRIDDED,
  not fit; T0/schedules are procedures/scales, not targets). Assumed: P4
  measure for κ outcomes, connectivity-hard. Conjectured: C2/C3 motivation.
- Non-goals: closing D10 (stays open — §7 close criterion unmet by design);
  weight-tuning to taste; recycling round-1 grids/bars without re-freezing
  (done: all re-frozen); observatory data (pure computation); deriving d = 3
  (report, don't claim); "confirm" without a bar.
- Compute cap: ~6 h wall baseline on 3 workers (local VM CPU, $0 marginal).
  Measured grid estimate ≈ 2 h (survey-N runs 25–90 s; spot ≈ 350 s pre-fix
  timing, faster post-fix; ablation ≈ 150 s). Frozen drop order if exceeded
  (§3). No GPU used (exact CPU fits; Sinkhorn never enters verdicts or
  exploration — GPU rule vacuous, stated). Memory peak < 2 GB/worker
  (Johnson 4000² float64 = 128 MB largest object).

## 11. Amendments + pre-freeze pilot log

Amendments (deviations from §§1–10 AFTER freeze — recorded here BEFORE the
affected compute; post-hoc amendments disqualify affected runs):

| # | Date | Section | Change | Reason |
|---|---|---|---|---|
| — | — | — | (none at freeze) | — |

Pre-freeze pilot log (development BEFORE this prereg was frozen — informs
frozen parameters, not amendments; pilot runs in `results/anneal2/pilot/`
are excluded from all tallies by runner glob):
- P1 (cost audit): eigsh/WL/snapshot micro-costs → K_REFRESH = 100 (§1.3).
- P2 (estimator-dev): 4 window variants on controls only → (2, 0.5) (§7.1);
  open→periodic seed switch (9/10 vs 10/10 evidence, §3).
- P3 (cooling): H0/H10 curves at 1000/2000 → STEPS rule + values (§3.1).
- P4 (max-N): one full H1-4000 run 1082 s < 1800 s → spot leg allowed (§10).
- P5 (eigsh robustness): skip-zero miss → k=6 + zero detection (E1);
  tree-phase non-convergence → maxiter 300 + hold rule (E2) (§1.2).
- P6 (seeds): ER 200-try cap burn → V2 25-try cap (same distribution family,
  fast fallback); diamond/FCC builders verified 4/12-regular at all N.
- P7 (reachability): 9-control table + d_ctrl + gate verification (§3.2, §7).
