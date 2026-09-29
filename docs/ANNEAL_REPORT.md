# Blind vacuum-annealer survey — report

**Branch:** `cursor/vacuum-anneal-813f` · **Prereg:** `docs/anneal-prereg.md`
(committed BEFORE any annealer compute; 2 pre-compute amendments in prereg
§11: sym-cadence, toggle-only T0 probes).
**Epistemic authority:** `docs/model.md` v0.4. Every number below is labelled
derived / fitted / assumed / exploratory / conjectured.
**Ledger:** P5/D10/A4 as described in the external proposal do not exist
(verified at prereg: D-items run D1–D9). §7 PROPOSES D10 (vacuum selection)
as a NEW OPEN item. Nothing here closes it — or anything else.
**Compute:** $0 (local VM CPU, 268 runs ≈ 20 min wall on 3 workers). No
observatory data (pure computation, as tasked). Run health: 0 failed,
0 disqualified, 0 T0-fallbacks, 0 eigsh holds, 0 seed fallbacks (all
exploratory counts from `results/anneal/*.json`).

## 0. Rule-zero compliance (blindness)

- The cost contains only graph-intrinsic terms (edge count, Laplacian
  spectrum, degree sequence, WL colors). Static token audits
  (`test_cost_is_blind`, `test_core_is_blind`) fail the suite on any leak of
  dimension/curvature/coordination-target/large-world tokens into the cost or
  loop modules, and on any measurement import there. Both pass (exploratory
  caveat: lexical coverage, not semantic — stated, not oversold).
- `disqualified: false` on all 268 runs. No run targeted or constrained
  dimension, curvature, coordination, or large-world-ness at any point.
- The circular proposal's defects (dimension target, curvature penalty,
  large-world hard constraint, phantom ledger citations) are absent by
  construction: none of those quantities is computable from inside the loop.

## 1. Method — and methodology finding #1 (cached-potential cancellation)

Cost `C = w_E·E/N + w_L·λ2/z̄ + w_R·CV(deg)² + w_S·(WL colors)/N`, grid
G0–G11, N ∈ {216, 512} + N = 1000 spot, exact-P4 κ at 3 checkpoints, d_iso
shell estimator, α = 0.9995, 15000 steps (8000 spot), connectivity hard,
bridgeless ablated. Full spec: prereg §§1–8.

**Finding M1 (procedure flaw, first-class negative):** the preregistered
cadence caching (§5 + amendment 1) silently neutralized the spectral and
symmetry terms AS DRIVERS. Mechanism (derived from the code path): cached
terms are held fixed between refreshes, so they cancel exactly in every
Metropolis ΔC; refreshes then jump the reported C with no accept/reject.
Consequence: trajectories depend only on (w_E, w_R). Verified exactly —
40/40 matched-config groups show bit-identical (E, edit-distance, accepts,
T0) within each class, and class A ≠ class B in all 20 full-grid keys:

- Class A (edge-only dynamics): G0 = G1 = G3 = G5 (exploratory, exact).
- Class B (edge + regularity): G2 = G4 = G6 = G7 = G8 = G9 = G11 (exact).
- Class C (regularity-heavy): G10 alone.

The survey therefore tested THREE distinct blind drivers, not twelve. All
weight-grid legs involving w_L/w_S are VOID as driver comparisons (their
reported C values differ only via stale potentials — visible e.g. in spot
G07 traces where reported C rises while E falls). This flaw is reported,
not repaired: a fix (exact per-proposal ΔC, or accept/reject on refresh
jumps) deviates from the frozen procedure and belongs to a re-preregistered
round 2 (§6). It is not a rule-zero violation (nothing was targeted), but it
narrows every verdict in §4. The three surviving drivers still yield three
distinct attractor classes (§3) — a real, if narrower, result.

## 2. Calibration (§7 bar) — MISCALIBRATED branch fires (frozen rule)

Source: `results/anneal/calibration.json` (all exploratory).

| control (pristine) | d_iso | err | R² | §7 bar |
|---|---|---|---|---|
| cubic-216 | 4.36 | 0.84 | 0.99 | FAIL |
| diamond-216 | 6.09 | 0.76 | 1.00 | FAIL |
| cubic-512 | 4.64 | 0.61 | 1.00 | FAIL |
| diamond-512 | 5.18 | 0.42 | 1.00 | FAIL |
| er-sparse-216/512, rr6-216/512 | nan (diso_ok=false) | — | — | (no bar; small-world, as anticipated) |
| cubic-1000 (open 10³) | 2.99 | 0.22 | 0.99 | PASS (extra-prereg reference) |

All four frozen bars fail: with r_min = 1 the shell estimator is
transient-dominated at N ≤ 512 (reads HIGH with R² ≈ 0.99 — systematic bias,
not noise). Per the frozen §7 rule the estimator is declared
**MISCALIBRATED** and **all d_iso verdicts in §4 are INCONCLUSIVE**
(estimator failure, not physics). d_iso values are still tabulated with
error bars as descriptives, compared relatively against same-N pristine
references, carrying no verdict weight. Two notes that sharpen (not soften)
this: (i) bushy ANNEALED TREES read d ≈ 2.3–3.6 in-bar (§3.1) while pristine
cubic reads 4.4 — the estimator cannot discriminate trees from lattices at
pilot N; (ii) small-world graphs read d ≈ 6–12 with R² ≈ 1.00 (G10 finals,
N=1000 spot) — explosive shells mimic high dimension.

Ground-truth reachability of the §9 B1–B4 bars on pristine lattices:

| control | B1 | B2 (κ) | B3 (z) | B4 (diam vs 2·log2 N) | member |
|---|---|---|---|---|---|
| cubic-216 (κ=0.000, diam 9 vs 15.5) | ✗ | ✓ | ✓ (6.0) | ✗ | NO |
| diamond-216 (κ=−1.000, diam 8 vs 15.5) | ✗ | ✗ | ✓ (4.0) | ✗ | NO |
| cubic-512 (κ=0.000, diam 12 vs 18) | ✗ | ✓ | ✓ (6.0) | ✗ | NO |
| diamond-512 (κ=−1.000, diam 12 vs 18) | ✗ | ✗ | ✓ (4.0) | ✗ | NO |
| cubic-1000 open (d=2.99, κ=0, z=5.4, diam 27 vs 19.9) | ✓ | ✓ | ✓ | ✓ | YES |

κ = 0.000 on cubic (derived lattice property) and κ = −1.000 exactly on
diamond (exploratory; girth-6 tree-like local structure) frame the B2 scale.
B4 is unreachable by periodic ground truth at N = 216/512 (diameters 8–12
vs bars 15.5–18 — derived) but PASSES on open-1000. So at N = 1000 the
estimator AND all bars validate on the control — the spot leg (§3.3) is
interpretable where the pilot grid is not.

## 3. Survey data (exploratory descriptives)

### 3.1 Discovery leg — three attractor classes, zero members (0/144)

Raw bar counts: B1 10/144, B2 39/144, B3 144/144, B4 133/144, member 0/144.
Per-class final medians (classes from §1; members of a class are
trajectory-identical, so medians are exact duplicates within class):

| class | drivers | n | κ_med | z_med | diam_med | attractor |
|---|---|---|---|---|---|---|
| A | edge-only | 48 | −0.28 | 2.0 | 52 | bushy trees |
| B | edge + reg (w_R=2) | 84 | −0.07 | 2.0 | 121 | path-like trees |
| C | reg-heavy (w_R=8) | 12 | −0.61 | 2.9 | 12 | near-3-regular small-world expanders |

Details: class A ends E = N−1 exactly (trees), T_reg ≈ 0.02–0.05, κ ≈
−0.22…−0.28 (B2: 0/48). Class B ends E = N−1 (trees), lower T_reg
(path-like; regularity pressure selects degree-2 chains), κ ≈ −0.03…−0.12
(B2: 38/84 — the flat class, flat because path-like, not because 3D).
Class C: 11/12 end z ≈ 2.9 (T_reg ≈ 0.002–0.013), κ ≈ −0.58…−0.64,
diam 10–13, d_iso ≈ 6–8 (R² = 1.00, small-world misread); 1/12
(`disc-G10-rr6-N216-s02`) fell into the
tree basin (z = 1.99, κ = −0.040, diam 92) — G10 is BISTABLE across seeds
at fixed weights (basin coexistence, 11:1 in this sample).
The 10 discovery B1 passes are ALL class-A bushy trees (z ≈ 2, κ ≈ −0.25,
diam 29–73) — and B1 ∩ B2 = ∅ across all 268 runs: flat outputs are
path-like (low-d), in-bar-d outputs are bushy (curved). Anti-correlation,
not a basin.
No z-target existed anywhere; the costs selected z ∈ {2.0, 2.9} (reported,
not claimed as vacuum z).

### 3.2 Stability leg — lattices are not fixed points (0/96 preserved)

Preservation by (class, lattice): edit-distance medians 1.32–1.73, MINIMUM
1.32 across all 96 runs vs the ≤ 0.5 bar — complete rewiring everywhere
(A/B → trees, C → expanders). B2 retention in class B (26/56) is
coincidental path-tree flatness, not preservation. Seeded lattices do not
survive any blind driver tested: the stability leg is a stability NEGATIVE
(descriptive; membership verdict INCONCLUSIVE per §4 because the B1 leg of
the preservation rule is unmeasurable — the edit-distance fact stands on
its own as an exact graph property).

### 3.3 N = 1000 spot — controls validate, runs under-cool (0/12 members)

At N = 1000 the bars work on the control (§2, cubic-1000 full member) and
0/12 spot runs are members: κ ≈ −0.37…−0.75 (bar: 0.06 — missed by 5–12×
SEM-corrected margins), d_iso ≈ 6–13 (small-world misread), z ≈ 2.2–3.1,
E still falling steeply at step 8000 (mid→final E drops ~40%; cf. N = 216
runs frozen by mid). Frozen 8000 steps under-cool N = 1000 (operating-point
finding: annealing time grows with N). Reading: consistent with
needle-not-basin at the only N where the ruler works — QUALIFIED by
under-cooling ("no basin found within 8000 steps" ≠ "no basin exists").
Not a FAIL verdict (spot is extra-rule); carried to round 2 with longer
schedules (§6).

### 3.4 Constraint ablation — 8 unique pairs (G1/G8 exact duplicates of G0/G7)

On-arm trajectory identity verified exact (G0 = G1, G7 = G8 in (E, edit,
accepts) on all 8 matched configs — corollary of §1). Unique-pair Δs
(on − off), κ/d_iso with 2σ_paired assessment (frozen rule):

- κ: fires 4/8 = 50% → meets the frozen "≥ 50%" threshold EXACTLY, driven
  entirely by class A (Δκ ≈ +0.17…+0.25 at 6–9σ — bridgeless steering raises
  κ toward zero there); class B silent (Δκ ≈ 0.00–0.03, 0/4 fire).
  Verdict (descriptive, as preregistered): "constraint drives κ" IN CLASS A
  ONLY — class-dependent, stated with the boundary.
- d_iso: fires 3/8 = 37.5% → does not meet threshold (and d_iso is
  miscalibrated regardless).
- z (exact, no sampling noise): Δz = +0.04…+0.11, ALL 8 positive (sign
  p = 0.004) — bridgelessness systematically resists full tree-collapse by
  4–12 edges.
- diameter (exact): sign-FLIPS by class: +11…+47 in class A (bridgeless →
  longer), −13…−45 in class B (bridgeless → shorter). The constraint
  steers structure in opposite directions depending on the cost — pure
  constraint-drive evidence, mechanism open.

## 4. Verdicts (frozen §9 rules — no PASS, no FAIL)

| verdict | result | basis (frozen rule, margins) |
|---|---|---|
| V-DISCOVERY | INCONCLUSIVE | Rule requires B1–B4 at N = 216 AND 512; B1 unmeasurable there (§2 branch) and B4 unreachable by ground truth there (diam 8–12 vs bars 15.5–18). Cannot pass even in principle → INCONCLUSIVE, not FAIL (FAIL would assert "no basin exists" — unwarranted on the d-leg). Supporting: 0/144 members; B1∩B2 = ∅ over 268 runs; N=1000 control-validated spot 0/12 (qualified, §3.3). |
| V-ARTIFACT | INCONCLUSIVE (membership) + descriptive | Membership-majority needs B1. Descriptively: attractors are EXACTLY stable across w_L/w_S (void legs, §1) and DISTINCT across w_R (trees at w_R ≤ 2 → expanders at w_R = 8 + 11:1 bistability) — the outcome moves with the surviving weight, mapped not hidden. |
| V-STABILITY | INCONCLUSIVE (membership) + descriptive | B1+B2 preservation rule needs B1. Descriptive fact (exact): min edit 1.32 > 0.5 bar — zero preservation; lattices not fixed points of any tested driver. |
| V-CONSTRAINT | DESCRIPTIVE: FIRES on κ in class A only | Frozen 2σ/50% rule: κ 4/8 = 50% (all class A, 6–9σ each); d_iso 3/8 no-fire; Δz 8/8 positive; Δdiam class-sign-flipped (§3.4). |

The pilot's kill bars worked as designed: they intercepted unmeasurable
claims (B1/B4 at pilot N, void spec/sym legs) before any could be made,
and converted the run into quantified blockers + a narrower real result
(three blind drivers → three non-vacuum attractors; constraint-drive map).

## 5. What the pilot established (exploratory, with provenance)

1. Three blind drivers → three attractor classes, none flat-3D-sparse:
   bushy trees (A), path-trees (B), 3-regular-ish expanders (C) — §3.1,
   `results/anneal/*.json` (exact trajectories, 40/40 collapse groups).
2. Coordination selected without any z-target: z = 2.0 (trees) / ≈ 2.9
   (expanders) — reported, not claimed.
3. Flatness is path-likeness here: the only flat class (B, 38/84 B2) reads
   d ≈ 1.1–2.1; everything in-bar-d is curved (κ ≈ −0.25). B1∩B2 = ∅/268.
4. Lattices are not fixed points: min edit 1.32 over 96 seeded runs (§3.2).
5. Constraint-set drive quantified with its class boundary (§3.4).
6. Two blocking quantifications for round 2: shell-estimator small-N bias
   (§2: trees read 3D, small-world reads d ≈ 6–12, periodic ground truth
   fails B4) and the cached-potential cancellation (§1: refresh-without-
   accept voids cached terms as drivers).
7. Positive control at scale: open-1000 cubic passes estimator + all bars
   (d = 2.99 ± 0.22) — the ruler works at N = 1000; the pilot grid sat
   below its range.

## 6. Round-2 re-preregistration proposal (NOT implemented — post-hoc here)

1. Fix M1: exact per-proposal ΔC (incremental spectral/symmetry updates) or
   accept/reject on cache refreshes — frozen before compute; verify with a
   trajectory-identity test that DISTINCT weights give DISTINCT trajectories.
2. d_iso estimator v2: r_min ≥ 2 + upper-V window, validated on pristine
   lattices at the survey N with a re-frozen §7-style bar BEFORE any anneal.
3. N-aware B4: bar as a fraction of pristine-lattice diameter at survey N
   and boundary condition (periodic vs open), frozen before compute.
4. N range 1000–4000 with N-scaled schedules (pilot: 8000 steps under-cool
   N = 1000; freeze steps(N) from a cooling pilot, not from targets).
5. Cost-grid v2 (de novo): anti-collapse blind terms (cycle-space, girth —
   still intrinsic, still blind) in a FRESH grid with FRESH bars; no
   recycling of this grid's weights as "known good".
6. Rule zero, ablation/seed/label/disqualification discipline carry over
   unchanged. D10 (§7) stays open until its close criterion is met.

## 7. D10 proposal (NEW OPEN ledger item — stays open)

**D10 — Vacuum selection from a graph-intrinsic principle.** Missing: a
derivation (not a construction) of the vacuum graph family — regularity
(C2), dimension, flatness — from a graph-intrinsic variational principle
(spectral / entropic / symmetry-based, C3) whose cost contains no
dimension, curvature, or large-world quantity. Close criterion: exhibit the
principle + derive (not fit) that its minima are sparse, flat,
3D-large-world graphs at large N, with dimension and curvature as MEASURED
outputs under preregistered estimators that pass pristine-lattice
calibration; survive weight-grid Pareto + seed + constraint ablation with
distinct-weights-distinct-trajectories verified (§1 lesson). Gated by: a
calibrated d_iso estimator at survey N (§2 blocker) and unvoided driver
legs (§1 blocker). Kill relevance: none yet (no vacuum-observation
falsifier) — framework-honesty issue: without D10, "the vacuum is a flat
3D lattice" is an assumed background, not a result. This pilot contributes
the machinery (`anneal_cost`/`anneal_core`/`anneal_measure`, runner, JSON
schema), the three-attractor map, and two quantified blockers; it does not
advance D10 toward closure.

## 8. Reproduce

`pip install -e ".[dev]"`, `pytest tests/test_anneal_*.py -q` (34 tests),
`python3 scripts/run_anneal_survey.py --jobs 3` (≈20 min, 268 runs + tally),
outputs `results/anneal/{calibration.json,manifest.json,<run_id>.json}`.
Prereg: `docs/anneal-prereg.md` (commit predates all survey compute).
