# Blind vacuum-annealer survey — preregistration

**Status:** preregistered BEFORE any annealer compute on this branch.
**Branch:** `cursor/vacuum-anneal-813f` (independent leg; no coordination with
derivation-attempt branches).
**Epistemic authority:** `docs/model.md` (L0/P1–P4, L1/I1–I7, L2/F1–F6, D1–D9).
Every number in the report is labelled
derived / fitted / assumed / exploratory / conjectured.
**Ledger note:** P5/D10/A4 as described in the external proposal do not exist
in `docs/model.md` v0.4 / `docs/DEFERRED.md` (verified at prereg time: D-items
run D1–D9). This leg PROPOSES D10 (vacuum selection) as a NEW OPEN item in the
final report. Nothing here closes it.

## 0. Rule zero (load-bearing)

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
  allowed; see C3/COST-3);
- any seed-pinning that prevents the annealer from leaving the seed class
  (toggle moves always on, so z and E can drift; drift is reported).

Violation handling: any run found to violate rule zero is labelled
**DISQUALIFIED** in `results/anneal/*.json` (`"disqualified": true` + reason)
and excluded from all verdict tallies. It is reported, never silently kept.

Falsification framing: the null hypothesis is that blind graph-intrinsic
costs do NOT select a flat-sparse-3D basin. A clean negative is first-class.

## 1. Cost functional (blind only)

Total cost (all terms graph-intrinsic; all weights ≥ 0 frozen in §2):

```
C(G; w) = w_E * T_edge(G) + w_L * T_spec(G) + w_R * T_reg(G) + w_S * T_sym(G)
```

### COST-1 — edge term (sparsity pressure)

```
T_edge(G) = E / N            (mean degree / 2; intrinsic: edge count)
```

Direction: minimized → sparser. No floor, no target. Alone it drives toward
trees; the survey maps what the COMBINATION selects.

### COST-2 — spectral term (algebraic connectivity)

```
T_spec(G) = λ2(L) / z̄        (combinatorial-Laplacian λ2 over mean degree)
```

`λ2` = second-smallest eigenvalue of the combinatorial Laplacian, via sparse
`eigsh`. Normalization by mean degree keeps the term O(1) across densities.
Intrinsic: Laplacian spectrum. Direction: minimized → geometrically
large-world-like spectra (lattices have small λ2; expanders large). This is a
spectral pressure, NOT a dimension target: no growth exponent, no diameter,
no ball statistic enters. Sign flips post-hoc are FORBIDDEN (would be tuning
to taste); the weight grid (§2) includes w_L = 0 ablation instead.

### COST-3 — regularity deficit (C2 direction, NO z target)

```
T_reg(G) = Var(degree) / z̄²   (squared coefficient of variation; 0 iff regular)
```

Intrinsic: degree sequence. Minimized → k-regular (C2 conjecture direction)
with the coordination z itself LEFT FREE: there is deliberately no `(z−z*)²`
term anywhere. Reported outcome z is whatever the basin selects.

### COST-4 — symmetry deficit (Weisfeiler–Lehman color count)

```
T_sym(G) = (# WL colors after K_WL=4 iterations, stabilized) / N
```

Intrinsic: WL refinement uses only adjacency. Minimized → vertex-transitive-
like (one color). Cheap: O(K_WL · E). K_WL = 4 frozen.

### Blindness audit (each term)

| Term | Uses d? | Uses κ? | Uses z-target? | Graph-intrinsic? |
|---|---|---|---|---|
| T_edge | no | no | no | yes (E, N) |
| T_spec | no | no | no | yes (Laplacian spectrum) |
| T_reg | no | no | no (CV only) | yes (degree sequence) |
| T_sym | no | no | no | yes (WL colors) |

A static audit test (`test_anneal_cost.py::test_cost_is_blind`) greps the cost
module source for forbidden tokens (`d_iso`, `kappa`, `ricci`, `ollivier`,
`diameter`, `ball`, `dimension`, `z_star`, `zstar`, `target_z`, `(d -`,
`(d-`) and fails if any appear outside an explicit FORBIDDEN-list comment.
(The measurement module is a separate file and is never imported by the cost
module — enforced by a second test.)

## 2. Weight grid (frozen)

Numeraire w_E = 1.0 always (sets the temperature scale). Grid over
(w_L, w_R, w_S). Values frozen (12 vectors):

| gid | w_E | w_L | w_R | w_S | leg |
|---|---|---|---|---|---|
| G0 | 1.0 | 0.0 | 0.0 | 0.0 | edge-only ablation |
| G1 | 1.0 | 2.0 | 0.0 | 0.0 | edge + spectral |
| G2 | 1.0 | 0.0 | 2.0 | 0.0 | edge + regularity |
| G3 | 1.0 | 0.0 | 0.0 | 2.0 | edge + symmetry |
| G4 | 1.0 | 2.0 | 2.0 | 0.0 | pair ablation (no sym) |
| G5 | 1.0 | 2.0 | 0.0 | 2.0 | pair ablation (no reg) |
| G6 | 1.0 | 0.0 | 2.0 | 2.0 | pair ablation (no spec) |
| G7 | 1.0 | 2.0 | 2.0 | 2.0 | full combo |
| G8 | 1.0 | 8.0 | 2.0 | 2.0 | spectral-heavy |
| G9 | 1.0 | 0.5 | 2.0 | 2.0 | spectral-light |
| G10 | 1.0 | 2.0 | 8.0 | 2.0 | regularity-heavy |
| G11 | 1.0 | 2.0 | 2.0 | 8.0 | symmetry-heavy |

No other weight vectors may enter verdict tallies. Exploratory off-grid runs
(if any) are labelled `exploratory` and excluded from PASS/FAIL counts.
Rationale for magnitudes: pilot term scales are T_edge ~ 3, T_spec ~ O(0.1),
T_reg ~ O(0.01–1), T_sym ~ O(0.1–1); weights 2.0/8.0/0.5 span sub-dominant →
dominant for the non-edge terms. Temperature (§6) is set in units of measured
|ΔC| so absolute scales do not matter.

Pareto/artifact rule: a basin claimed as "selected" must persist across ≥ 3
adjacent grid vectors (sharing ≥ 2 weight values) or it is a weight artifact.

## 3. N range and lattice seeds (frozen)

Pilot N (frozen): **N ∈ {216, 512}** full grid; **N = 1000** spot-check on
{G0, G7} only (cost control). Scale-up beyond N = 1000 requires a prereg
amendment note in the report (allowed only if per-run wall time stays < 10 min
on this VM).

Seeds (frozen IDs, `anneal_core.SEED_IDS`):

Discovery leg (random starts — must carry no geometric structure):
- `er-sparse`: Erdős–Rényi G(N, p) with p = 6/(N−1) (z̄ ≈ 6), rejection-sampled
  to connectivity (≤ 200 tries, else take LCC + attach isolates — attachment
  procedure in code, deterministic given seed).
- `rr6`: random 6-regular (networkx, rejection on failure → fallback er-sparse
  with note in JSON; degree sequence is a START, toggle moves let z drift).

Stability leg (known lattices — does the annealer preserve or wander?):
- `cubic`: 6×6×6 periodic cubic (N = 216) / 8×8×8 periodic cubic (N = 512).
  For N = 1000: 10×10×10 OPEN cubic (N = 1000 exactly).
- `diamond`: periodic diamond-cubic cell replication (N = 216: 3×3×3 cells ×
  8 atoms; N = 512: 4×4×4 × 8). For N = 1000: diamond fragment is not exactly
  1000 nodes — use `cubic` only at N = 1000 (frozen; no ad-hoc diamond-1000).

Seed RNG (frozen): seeds {0, 1, 2} per (gid, seed-id, N) for the discovery
leg; seeds {0, 1} per (gid, seed-id, N) for the stability leg (cost control).
Total run cap: discovery 12 gid × 2 starts × 2 N × 3 seeds = 144 runs;
stability 12 × 2 × 2 × 2 = 96 runs; N=1000 spot 2 × 3 starts × 1 = ~10 runs.
If wall time exceeds budget, drop in this frozen order: N=1000 spot first,
then stability seeds {1}, then discovery seeds {2} — and SAY SO in the report.

## 4. Constraint ablation (frozen)

- Connectivity HARD in all runs (one space; allowed by protocol).
- Bridgelessness: ablation flag `bridgeless ∈ {off, on}`.
  - `off`: only connectivity enforced (reject disconnecting moves).
  - `on`: additionally reject any move creating a bridge (BFS/chain check;
    exact, allowed to be slow — cadence §5).
- Ablation scope (frozen, cost control): full `off` grid (all runs above);
  `on` reruns on subset {G0, G1, G7, G8} × {er-sparse, cubic} × N = 216 ×
  seeds {0, 1} = 16 runs. Constraint-drive verdict compares matched pairs.

Large-world is MEASURED (diameter, mean distance, growth), NEVER enforced.
No diameter/path/growth term or filter exists in code paths reachable by the
annealer (audit test covers the core module too).

## 5. κ backend + operating point (frozen)

κ is an OUTCOME (P4 uniform measure, zero self-mass), evaluated at
checkpoints only (initial, final, + mid-run), NEVER inside the cost loop.

- Backend: EXACT Ollivier-Ricci (`orici.ollivier_curvature`, P4 defaults)
  with sparse-Johnson cached distances (`sinkor.all_pairs_johnson`).
- Sample: ≤ 150 edges/run-checkpoint, uniform without replacement, RNG split
  from run seed (deterministic). Report mean ± SEM over sampled edges.
- N = 216/512: fine. N = 1000: Johnson on ~3000 edges ≈ seconds; allowed.
- Fallback: if Johnson fails (disconnected — should not happen), record
  `kappa_ok: false` and EXCLUDE the run from κ tallies (do not impute).
- Sinkhorn is NOT used in this leg (exact-only keeps the κ-outcome
  unconfounded by entropic bias; documented tradeoff: fewer κ checkpoints).

Cost-vs-reliability tradeoff (frozen justification): full edge-κ per step
would cost O(steps × E × LP) ≈ 10^4 × 10^3 LPs/run — infeasible and
FORBIDDEN (κ in the loop). d_iso needs only BFS (cheap) so it is measured
at the same checkpoints; its reliability at N ≤ 1000 is limited (few shells
— see §7 error bars) and we report noise honestly rather than scaling N
beyond budget.

Spectral-term operating point: T_spec via `scipy.sparse.linalg.eigsh`
(k = 2, which="SM") on the combinatorial Laplacian, evaluated on CADENCE
(every K_SPEC = 25 accepted moves, cached between), NOT every proposed move.
Edge/reg/sym terms are O(1)–O(E) incremental/full per proposal (cheap).
Per-step cost is therefore O(1) amortized + O(eigsh)/25. If eigsh fails to
converge, fall back to dense `eigvalsh` for N ≤ 512, else hold last value
(hold events counted in JSON; > 5% holds → run flagged INCONCLUSIVE-fragile).

## 6. Annealing schedule (frozen)

- Moves (proposal mix, frozen): with prob 0.5 double-edge swap
  (degree/E-preserving); with prob 0.5 single-edge toggle (add uniform random
  non-edge / remove uniform random edge, 50/50). Self-loops and multi-edges
  rejected. Disconnecting moves rejected (hard). Bridgeless-on runs
  additionally reject bridge-creating moves.
- Acceptance: Metropolis `P = min(1, exp(−ΔC/T))`, ΔC from §1.
- Temperature: geometric `T_k = T0 * alpha^k`, k = step index.
  T0 selection (frozen procedure, not a tuned value): at run start, propose
  200 random moves, measure median |ΔC| over non-rejected proposals = m;
  T0 = m / ln(2) (median move accepted with p = 0.5 at k = 0). If m == 0
  (degenerate), T0 = 1.0 fallback, flagged in JSON. This is a SCALE, not a
  target: it contains no d/κ information.
- alpha frozen: `alpha = 0.9995`; STEPS frozen: discovery 15000, stability
  15000, N=1000 spot 8000 (cost control). Final T ≈ T0 × 5.5e-4 (discovery).
- Checkpoints: k ∈ {0, mid, end} for (d_iso, κ, z, E, WL colors, λ2, LW stats);
  full cost trace thinned to ≤ 300 points stored per run.

## 7. d_iso estimator spec (frozen)

Ball-boundary profile: for seed node s, BFS gives V(r) = |B(s,r)|,
S(r) = |∂B(s,r)| = shell size. Model: S ~ V^((d−1)/d).

- Seeds: n_dseeds = 20 uniform nodes (RNG split, deterministic).
- Per seed: collect (V(r), S(r)) for r = 1..r_max(s) where r_max(s) is the
  largest r with V(r) ≤ N/2 (avoids saturation). REQUIRE ≥ 4 points else seed
  dropped.
- Fit: OLS on log S = a·log V + b over the seed's points; slope a →
  d = 1/(1−a). Valid slope range a ∈ (−0.2, 0.95) else seed dropped
  (a ≥ 1 → d ≤ 0 unphysical; a ≤ 0 → d ≤ 1 Lipshitz-pathological at this N).
- Aggregate: d_iso = median over kept seeds; err = max(SEM over kept seeds,
  median |per-seed fit-SE|); R² = median per-seed R². REQUIRE ≥ 8 kept seeds
  else `diso_ok: false` (INCONCLUSIVE-noisy, excluded from tallies).
- Calibration (frozen, run once, reported): estimator applied to pristine
  `cubic` and `diamond` seeds at N = 216/512 must return d_iso ∈ [2.0, 4.0]
  with R² ≥ 0.8, else the estimator is declared MISCALIBRATED and ALL d_iso
  verdicts become INCONCLUSIVE (estimator failure, not physics). Also applied
  to `er-sparse` starts (expected: noisy/small-world, recorded, no bar).
- Small-N honesty: at N = 216 the fit uses ~3–6 shells; error bars will be
  O(0.5). That is REPORTED, not hidden. No N beyond budget to shrink them.

## 8. Outcomes per run (frozen JSON schema keys)

Each `results/anneal/<run_id>.json`: run_id, gid, weights, N, seed_id, seed,
bridgeless, disqualified(+reason), steps, alpha, T0, T0_fallback, schedule
traces (thinned), checkpoints[initial/mid/final] each with
{E, z_mean, z_std, T_edge, T_spec, T_reg, T_sym, C_total, diso{d, err, r2,
n_kept, ok}, kappa{mean, sem, n, ok}, LW{diameter, mean_dist_sampled,
n_dist_samples}}, holds_eigsh, n_rejected_disconnect, wall_s, bh_graph_git_sha,
label ("exploratory" on every measured number — see §10).

## 9. Kill criteria / verdict bars (FROZEN — not vibes)

Basin-membership bar (ALL FOUR must hold on the FINAL checkpoint):

- B1 dimension: `diso.ok AND |d_iso − 3| ≤ 0.75 AND R² ≥ 0.75`
- B2 flatness: `kappa.ok AND |mean κ| ≤ 0.06`
- B3 sparsity: `z_mean ≤ 8.0` (no lower bound except connectivity; trees
  allowed — if trees pass B1/B2/B4 they pass, say so)
- B4 large-world: `diameter ≥ 2·log2(N)` (N=216: ≥ 15.5 → 16; N=512: ≥ 18)

Leg verdicts:

- V-DISCOVERY (blind runs find a flat-3D-sparse basin): PASS iff ≥ 2
  discovery-leg runs with DIFFERENT gid (persistence, cf. §2 Pareto rule ≥ 3
  adjacent vectors for a "selected" claim; 2 = basin EXISTS, 3+ adjacent =
  basin SELECTED) meet B1–B4, with at least one at each of N = 216 AND N = 512
  (no single-N mirage). Else FAIL (record: "no flat-3D-sparse basin").
- V-ARTIFACT (attractor moves with weights): PASS(no-artifact) iff every
  pair of adjacent grid vectors (differing in one weight by one grid step)
  agrees on basin-membership majority (≥ 2/3 of matched runs agree) for ≥ 80%
  of adjacent pairs. Else FAIL → outcome is a weight artifact (record which
  weights drive it).
- V-STABILITY (seeded lattices preserved): per (lattice, gid): PRESERVED iff
  final checkpoint meets B1+B2 (B3/B4 not required — preservation, not
  discovery) AND graph-edit distance from seed (added+removed edges)/E_seed
  ≤ 0.5. Leg verdict: STABILITY-ONLY iff ≥ 50% of stability runs PRESERVED
  while V-DISCOVERY FAILs. If V-DISCOVERY PASSes, stability is supporting.
- V-CONSTRAINT (constraint set drives outcome): report matched-pair
  (bridgeless on/off) Δd_iso, Δκ, Δz with paired error bars; verdict
  DESCRIPTIVE (no PASS/FAIL): "constraint drives X" iff |Δ| > 2σ_paired on
  ≥ 50% of pairs. Constraints never select alone (both arms use identical
  blind costs — the comparison is clean).

Kill mapping: V-DISCOVERY FAIL + V-STABILITY STABILITY-ONLY → "discovery
dead, stability-only result". V-DISCOVERY FAIL + stability also fails →
"flat sparse 3D is a needle, not a basin" (clean negative, first-class).
Any PASS without §2 persistence (≥ 3 adjacent) is downgraded to
INCONCLUSIVE-lonely (single-point mirage watch).

## 10. Labels and non-goals (frozen)

- Every measured number: `exploratory`. No fitted numbers (no tuning to
  targets — weights are GRIDDED, not fit). Assumed: P4 measure for κ
  outcomes, connectivity-hard. Conjectured: C2/C3 motivation only.
- Non-goals: closing D10 (stays open); any "Closed" stamp; weight-tuning;
  observatory data (no Fermi/LVK); deriving d = 3 (report, don't claim).
- Compute cap: $0 (local VM CPU only). No external spend. Ask before > $25
  (not expected to trigger).

## 11. Amendments

Any deviation from §§1–10 is recorded here with date + reason BEFORE the
affected compute runs. Post-hoc amendments disqualify affected runs.

| # | Date | Section | Change | Reason |
|---|---|---|---|---|
| 1 | 2026-09-28 | §5–§6 | T_sym evaluated on cadence K_SYM = 25 accepted moves (cached between proposals), same mechanism as T_spec; when w_S = 0 (resp. w_L = 0) no WL (resp. eigsh) evaluation inside the loop at all — checkpoint values (§8) are always freshly computed, never cached. | Per-step cost stays O(1) amortized as §5 intends: full WL per proposal is O(K_WL·E) Python and would dominate wall time without changing the landscape (single-edge moves rarely change WL colors; cadence-25 refresh captures drift). Filed BEFORE any annealer compute; no run affected retroactively. |
| 2 | 2026-09-28 | §6 | T0 calibration uses toggle-only probes (200 toggle proposals; median \|ΔC\| over constraint-passing probes; T0 = median/ln2; fallback T0 = 1.0 flagged). | Swaps carry ΔC ≡ 0 under the preregistered cadence caching, so the frozen 50/50 mix would measure the proposal mix rather than the cost scale. Still a pure scale (no outcome statistic enters). Filed BEFORE any annealer compute. |
