# Cut-edge/curvature probe — preregistration (append to Phase 1)

**Status:** preregistered BEFORE any cut-edge computation on branch
`cursor/cutedge-kappa-probe-7061` (stacked on `cursor/vacuum-derivation-7061`
for builder reuse; this probe adds no Phase-1 verdict weight beyond its own
named test). No `results/vacuum_cutedge/*` measurement may predate this file.
Edits after first compute go under §6, never silent.

**Terminology:** "cut-edge" throughout. The word "bridge" appears ONLY inside
the identifier `nx.bridges` (unavoidable API name) and this paragraph —
`shellscale.py` already uses "bridges" for shell connectors.

**Hypothesis H-κB:** mean Ollivier-κ rises toward 0 as cut-edge density
falls, holding volume growth fixed.

## §1. Design (frozen)

### §1.1 Graph set (all frozen; no size/seed tuning after this)

| Class | Graphs | Role |
|---|---|---|
| Lattices | cubic L=5 (N=125, k=6), BCC nc=4 (N=128, k=8), FCC nc=3 (N=108, k=12); periodic builders from `vacuum_graphs` (deterministic, no seeds) | hypothesis-consistent points (expect cut≈0, κ≈0) |
| Random-regular controls | matched (N,k) to each lattice: (125,6), (128,8), (108,12); `nx.random_regular_graph`, frozen seeds 0..4 → 15 graphs | KILLER CONTROL 1 (expect cut≈0 yet κ<0) |
| Chain | `nx.path_graph(125)` (N-matched to cubic; degree unmatched, k≈2 — labeled honestly) | KILLER CONTROL 2 (expect cut=1 yet κ=0 — repo-pinned `test_flat_line_zero`) |
| Regular-tree anchors | `nx.balanced_tree(2,5)` (N=63), `nx.balanced_tree(3,4)` (N=121) | ANCHORS only (cut=1, κ<0; illustrative, in pooled descriptives, in no bar) |
| Dilution ladder (within-class variation) | cubic L=6 (N=216), bond-deletion q ∈ {0, 0.05, 0.10, 0.15, 0.20}, frozen seeds {0,1,2} → 15 graphs; analysis on the largest connected component (LCC) | within-lattice-class monotonicity curve |

Why the ladder: periodic lattices all have cut-fraction identically 0, so
"within lattice class" is degenerate without engineered variation. Bond
dilution spans cut-density continuously. Cost: growth is NOT held fixed
along the ladder (reported per point, §3; scope-noted, never hidden).
q ≤ 0.20 stays below cubic bond-percolation (p_c ≈ 0.249), so the LCC
stays giant; any point with LCC < 0.5N is DROPPED and flagged.

### §1.2 Per-graph metrics (frozen)

- **cut-edge fraction** = #cut-edges / #edges, EXACT via `nx.bridges`
  (cut-edges of a disconnected graph = union over components; fraction
  over all edges — deterministic, no choices).
- **edge-κ distribution**: EXACT `orici` LP on EVERY edge (uniform P4
  measure, cached distances; same backend as Phase-1 verdicts). Report
  mean, sd, n, 95% CI (mean ± 1.96·sd/√n). For diluted graphs: LCC only.
- **ball-growth check**: from 3 frozen roots (ids 0, N//3, 2N//3 ∩ LCC),
  |B(r)| for r = 1..6 (cap 6 for cost); OLS log-log slope d̂ (poly) and
  log-linear slope ĝ (exp); report d̂, R²_poly, ĝ, R²_exp, better model.
  Purpose: characterize growth class per graph (lattice: poly d̂≈3;
  rr/tree: exp). "Holding volume growth fixed" is operationalized as
  WITHIN-growth-class comparison (lattice+ladder ≈ poly; rr+tree ≈ exp).

### §1.3 2×2 logic (why this kills or scopes cleanly)

The hypothesis must survive all four corners: lattice (cut≈0, κ≈0),
random-regular (cut≈0, κ<0?), chain (cut=1, κ=0), tree (cut=1, κ<0).
rr-at-zero-cut with κ<0 breaks "cut≈0 ⇒ flat"; chain-at-full-cut with
κ=0 breaks "cut≈1 ⇒ curved". Either control alone kills the naive
bidirectional reading; together they leave at most a scope-restricted
monotone story (tested by M-within, §2).

## §2. Bars (numbers, not vibes — frozen)

- **K1 — naive-reading kill.** The naive "bridgeless ⇒ flat" reading is
  DEAD iff for EVERY matched (N,k) pair, the random-regular 5-seed pool
  satisfies BOTH: (a) pooled mean-κ 95% CI lies entirely below −0.02,
  and (b) every seed's cut-fraction < 0.05. On DEAD: record "flatness
  requires lattice order, not mere redundancy" and move on (no rescue).
- **K2 — lattice-flatness sanity (not a kill).** |mean κ| < 1e-9 on all
  3 lattices (same bar as Phase-1 Test-i). Violation = methods flag
  (would contradict Test-i), never a ledger event.
- **M-within — lattice-like monotonicity.** Spearman ρ(cut-fraction,
  mean-κ) over the 18 lattice-like graphs (3 lattices + 15 ladder
  points; dropped LCC points excluded). HOLDS iff ρ < −0.5 with
  two-sided p < 0.05. Else NOT DETECTED.
- **M-across — pooled descriptives (no bar).** Spearman ρ over all
  graphs pooled (lattices + ladder + rr + chain + trees); report
  ρ + p + 95% CI. Descriptive only — pooled classes confound growth.
- **G-growth sanity (no bar).** Expect lattices poly (d̂ ∈ [2.5,3.5],
  R²_poly > R²_exp) and rr exp (R²_exp > R²_poly). Violation = methods
  flag with per-graph table, not a verdict input.

Interpretation grid (frozen): K1-DEAD + M-within-HOLDS → scope
restriction ("monotonicity within lattice-like class only"); K1-DEAD +
M-within-NOT-DETECTED → no monotone cut↔κ story at any tested scope;
K1-ALIVE (rr flat: CI overlaps [−0.02,·)) → naive reading survives this
probe (report margins; H-κB stays live).

## §3. Scope notes (pre-committed honesty)

- Dilution changes growth along the ladder: per-point growth exponents
  are reported; any M-within claim carries "growth not held fixed".
- Chain matches N only (k≈2 vs 6): K1's killer logic does not depend on
  the chain; the chain is a second, independent control.
- Trees are anchors (unmatched degrees/sizes): pooled descriptives only.
- N ≤ 256, exact OR throughout: an afternoon of compute at most; this
  probe must not crowd out main Phase-1 tests (it doesn't — Phase 1 is
  complete on the parent branch).

## §4. Deliverables

`src/bh_graph/vacuum_cutedge.py` + `tests/test_vacuum_cutedge.py` (all
passing) + `scripts/vacuum_cutedge.py` + `results/vacuum_cutedge/*.json`
+ `docs/CUTEDGE_REPORT.md` (per-bar verdicts + CIs + interpretation-grid
cell). No D-ledger changes possible from this probe (named test only).

## §5. Provenance

Parent branch `cursor/vacuum-derivation-7061` tip `0ea0ad6` provides
`vacuum_graphs`/`vacuum_curvature`/`vacuum_spectra` + Phase-1 context.
This prereg is committed before any `vacuum_cutedge` measurement.

## §6. Amendments (post-compute edits logged here, never silent)

(None yet.)
