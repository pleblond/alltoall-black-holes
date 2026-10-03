# H-κB cut-edge/curvature probe — preregistration amendment to Phase 1

**Status:** preregistered BEFORE any H-κB computation. Same rules as
`docs/derivation-prereg.md`: bars frozen here; results go to
`results/vacuum/phase1b_cutedge.json` + a `docs/VACUUM_REPORT.md` appendix.
Any deviation recorded as PROTOCOL DEVIATION; silent deviations forbidden.

**Terminology (binding):** say "cut-edge", NOT "bridge" — `shellscale.py`
already uses "bridges" for shell connectors. Code identifiers use `cut_*`
(`networkx.bridges` is only the algorithm invoked inside
`cut_edge_fraction()`).

## H-0. Hypothesis

H-κB: mean Ollivier-κ rises toward 0 as cut-edge density falls, holding
volume growth fixed. The naive reading under test: "bridgeless ⇒ flat".
Epistemic status: CONJECTURE (absent from `docs/model.md`); this probe can
at most kill the naive reading or scope-restrict a within-class regularity.

## H-1. Families (exact)

| Class | Graphs | k | N | Instances |
|---|---|---|---|---|
| Lattice (Leg 1 + G-check B) | SC PBC L∈{8,10}, BCC L∈{6,7}, FCC L∈{5,6} via `vacuum_graphs.build_vacuum` (same code as Phase 1) | 6/8/12 | 512,1000 / 432,686 / 500,864 | deterministic (1 each) |
| Expander control (Leg 1) | `random_regular_graph(k, N)` matched to EACH lattice (same N, same k) | 6/8/12 | matched (6 pairs) | seeds {0..4} primary, {5..9} ordered spares (replacement rule H-3) |
| Deletion series (Leg 2) | SC L=10 + FCC L=6, NESTED cumulative random deletion (seed=0 stream) at kept-fractions {100%, 97%, 93%, 87%, 73%} of E (rounded counts) | 6/12 | 1000/864 (pre-deletion) | 5 levels × 2 series |
| Tree anchor | `balanced_tree(2, 5)` (63 nodes) | — | 63 | 1 (descriptive anchor) |

## H-2. Per-graph measures (all on the measured = largest component)

- **cutfrac** (EXACT): |cut-edges|/|edges| via `networkx.bridges` (Tarjan).
- **mean-κ + distribution**: exact backend (transportation LP + Johnson,
  P4 uniform measure — same as Phase 1). 200 seeded edges (seed=123) per
  graph, or ALL edges if fewer (tree: all 62). Report mean, SD, frac_neg,
  per-level SE. Primary uncertainty for expanders: ACROSS-SEED t 95% CI
  (n=5); lattice/deleted/tree CIs are within-sample t 95% (descriptive).
- **growth**: BFS shell counts |S(r)| from a deterministic root (lattice:
  build center; deleted/expander: min-node-id of measured component).
  Leg-2 premise: log-log slope of |B(r)| over FIXED r=1..4. Scope demo
  (G-check B, k=6 only): ratio S(3)/S(2) on SC L=10 vs matched expander.

## H-3. Component + replacement rules (frozen)

- All measures on the LARGEST connected component; its N recorded.
- Deletion level with largest-component N < 90% of pre-deletion N:
  level INVALID → dropped with reason (no replacement; levels are fixed).
- Expander instance with largest N < 90%: instance INVALID → replaced by
  next spare seed in order ({5..9}); if spares exhaust → pair INCONCLUSIVE.
- Lattices/trees: connected by construction; any disconnect = bug, halt.

## H-4. Legs and BARS (numbers, not vibes)

**Leg 1 — killer control (cross-class).** For EACH of the 6 matched (k,N)
pairs: lattice must show cutfrac EXACTLY 0 (assert; torus has no
cut-edges — nonzero = bug, halt) and lattice edge-sample max|κ|<1e-6
(Phase-1 bar reused; else machinery drift, halt).

- **K1 (naive reading DEAD)** iff for EVERY pair: expander cutfrac < 0.01
  ("near-zero") AND expander across-seed mean-κ 95% CI lies ENTIRELY below
  −0.01 (upper edge < −0.01). Then record: "flatness requires lattice
  order, not mere redundancy." If ANY pair fails either condition → naive
  reading SURVIVES this probe (no kill claimed, report honestly).

**Leg 2 — monotonicity within the lattice-like class.**

- **G-check A (growth-fixed premise)** iff slope(0)∈[1.5,3.0] AND
  |slope(m)−slope(0)|<0.75 for every deletion level m, per series. Else that
  series is INCONCLUSIVE (premise fails) and excluded from K2. (Band
  calibrated pre-run, see §H-7 — NOT 3±0.5.)
- **K2 (monotonicity HOLDS)** iff Spearman ρ(cutfrac, mean-κ) over a
  series' valid levels satisfies ρ<−0.5 AND the 95% MC interval excludes 0
  (MC: 2000 draws, seed=7, per-level mean-κ ~ Normal(mean, SE); cutfrac
  exact). Both series hold → "monotonicity within lattice-like class";
  one holds → "partial, scope-restricted"; neither → "no evidence".
- Across-class rank correlation (all graphs pooled) is DESCRIPTIVE ONLY
  (no bar) — expanders are expected to break it (that is K1's point).

**Scope demo — G-check B (descriptive, k=6 pair only):** lattice
S(3)/S(2)∈[1.5,3.0] AND expander S(3)/S(2)>3.5 → "growth classes differ"
recorded as the scope restriction behind K1. Else report numbers with the
scope claim weakened. No verdict attached; K1 does not depend on it.

**Tree anchor (validity, not verdict):** cutfrac==1.0 (assert) and all-edge
mean-κ<−0.05 (repo pin from `test_tree_negative_complete_positive`); else
halt-and-investigate (machinery suspect), no verdicts from this probe.

## H-5. Confounds + non-goals (stated upfront)

- Deletion adds cut-edges AND degree defects jointly — Leg 2 measures
  their joint effect (unavoidable: a torus gains cut-edges only by
  cutting). Leg 1 isolates order-vs-redundancy at matched ≈0 cutfrac.
- Trees/expanders grow exponentially: the "growth fixed" premise holds
  ONLY within Leg 2 (checked by G-check A), never across classes.
- No new selection claims (C3 untouched); no κ→c₂ use (F4/D3 untouched).

## H-6. Budget + deliverables

- Budget: <2 CPU-hours total (expected ~10 min: ~50 graphs × 200 LPs);
  abort-and-report-partial beyond (will not happen; main Phase 1 tests
  are already complete so no crowding is possible regardless).
- Deliverables: `src/bh_graph/vacuum_cutedge.py` +
  `tests/test_vacuum_cutedge.py` + `results/vacuum/phase1b_cutedge.json` +
  report appendix. Same branch (append to Phase 1); PR #46 updated.

## H-7. Pre-run calibration fix (G-check A band; no probe data seen)

As first written, G-check A required slope(0)∈3±0.5. Unit-test arithmetic
showed this band is miscalibrated: the 4-point log-log fit over r=1..4 of
EXACT cubic balls gives slope 2.09 (SC shells 6,18,38,66 → B=7,25,63,129)
and 2.28 (FCC shells 12,42,92,162 → B=13,55,147,309) — lower-order terms
dominate at small r; 3 is the ASYMPTOTIC exponent, unreachable on 4
points. The original band would fail deterministically on intact lattices.
Correction (pure combinatorics; zero HKB probe measurements involved):
slope(0)∈[1.5,3.0], which contains both exact values with margin and still
excludes exponential-type growth (k=6 tree-like balls give ≈3.4 over the
same range). The comparative clause (|Δ|<0.75, the actual premise test) is
unchanged. Fix committed before the probe ran; recorded here, not silent.
