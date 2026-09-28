# Cut-edge/curvature probe — report (append to Phase 1)

**Branch:** `cursor/cutedge-kappa-probe-7061` (stacked on
`cursor/vacuum-derivation-7061`) · **Prereg:** `docs/cutedge-prereg.md`
(committed `580d7d0` BEFORE compute; one PRE-compute clarification C1) ·
**Date:** 2026-09-28. **Compute:** 36 graphs in 7 s (local, <$1).

**One-paragraph verdict:** the naive "bridgeless ⇒ flat" reading is DEAD
(K1 triggers on all three matched pairs with huge margins: random-regular
graphs carry ZERO cut-edges yet κ = −0.67/−0.48/−0.19 at k = 6/8/12).
Recorded: **flatness requires lattice order, not mere redundancy.** The
chain (cut = 1, κ = 0 exactly) independently breaks the converse. The
within-lattice-class monotonicity question is UNTESTED, not answered —
the dilution ladder produced zero cut-edges at all q ≤ 0.2 (probe-design
miss, owned below), so M-within is degenerate; the ladder still killed
through a second door (κ falls 0 → −0.43 at constant cut = 0). The
ball-growth diagnostic is flagged UNINFORMATIVE at N ≤ 256 (no-bar
sanity; saturation + short prefixes). No D-ledger changes (named test).

## 1. Verdict table (prereg'd bars)

| Bar | Frozen criterion | Measured | Verdict |
|---|---|---|---|
| K1 naive-kill (×3 pairs) | pooled rr κ-CI entirely < −0.02 AND every cut < 0.05 | (125,6): CI (−0.677,−0.654), cut 0.0000 · (128,8): (−0.489,−0.475), 0.0000 · (108,12): (−0.190,−0.181), 0.0000 | **DEAD on all pairs** (margins 9–30× on κ, exact 0 on cut) |
| K2 lattice sanity | \|mean κ\| < 1e-9, all 3 lattices | 0, 1.1e-16, −1.1e-17; cut 0 | **HOLDS** (consistent with Test-i) |
| M-within | Spearman < −0.5, p < 0.05 over 18 lattice-like | degenerate (all 18 cut-fractions ≡ 0; ok=False) | **NOT DETECTED (untestable — ladder miss)** |
| M-across (descriptive) | report ρ + p + CI | ρ = +0.11, p = 0.54, CI (−0.23, +0.42), n = 36 | no pooled trend |
| G-growth sanity (no bar) | lattices poly d̂∈[2.5,3.5]; rr exp | lattices poly ✓ but d̂ ≈ 1.8–2.1; rr/tree unreliable (saturation) | **METHODS FLAG (§4)** |

Interpretation-grid cell (frozen): K1-DEAD + M-within-NOT-DETECTED →
**no monotone cut↔κ story at any tested scope.**

## 2. The 2×2 that kills (measured)

|  | cut ≈ 0 | cut = 1 |
|---|---|---|
| **κ ≈ 0** | lattices (0.0, κ≡0) | **chain (1.0, κ≡0)** — breaks "cut⇒curved" |
| **κ < 0** | **random-regular (0.0, −0.67..−0.19)** — breaks "bridgeless⇒flat" | trees (1.0, −0.31/−0.32) |

No monotone function cut→κ fits all four corners. Both killer controls
fired: rr CIs exclude −0.02 by 9–30× with literally zero cut-edges
(n = 1875–3240 pooled edge-κ values per pair); chain κ = 0.0000000000
at cut = 1.0. Recorded per prereg: **flatness requires lattice order,
not mere redundancy.**

Characterization (exploratory): rr mean-κ rises with degree (−0.67 @
k=6 → −0.48 @ k=8 → −0.19 @ k=12) — denser random graphs are flatter
(more short cycles); all still decisively negative.

## 3. Ladder: designed door jammed, second door killed

All 15 ladder points (q ∈ {0,…,0.20} × 3 seeds, cubic-6, LCC = 100%):
cut-fraction **0.0000 everywhere** — deleting ≤20% of bonds on a
6-regular periodic lattice never strands a cut-edge. M-within is
therefore degenerate (Spearman undefined on constant x), NOT a measured
null. Owned as a probe-design miss: spanning cut-density needs q
through percolation (p_c ≈ 0.249 bond, higher for cut-production) —
recommended for a follow-up prereg, not run here (no rescue compute).

But the ladder killed anyway, un-prereg'd (exploratory observation, no
verdict weight beyond supporting K1's sentence): mean-κ falls
monotonically with q — 0.000 → −0.134 → −0.246 → −0.344 → −0.422 —
**at constant cut = 0**. κ responds to cycle degradation, not to
cut-edges. Three seed-replicates per q agree to ±0.01.

## 4. Growth diagnostic: methods flag (UNINFORMATIVE at N ≤ 256)

Per-graph table in `results/vacuum_cutedge/summary.json` (`growth` key);
honest accounting:

- Lattices select poly correctly (R²_poly 0.994–1.000 > R²_exp) but
  d̂ ≈ 1.8–2.1, missing the [2.5, 3.5] expectation: small periodic
  boxes saturate by r ≈ 3–4 (n_used = 3–6), and r = 1–3 balls are not
  asymptotic. True d = 3 needs r ≫ 1 AND r ≪ diameter — impossible on
  N ≤ 256 (diameter ~6–10).
- rr/tree model selection is saturation noise (3-point R² ≈ 0.99 ties;
  tree-3-4 "poly" from center+leaf root mixing; chain poly-correct
  with endpoint-biased d̂ = 0.79).
- Consequence: the prereg'd "within growth class" operationalization
  is unsupported BY MEASUREMENT at these sizes. Interpretation is
  downgraded to construction-labeled classes (lattice-like vs
  expander-like by build, not by fitted growth). A growth-based scope
  claim needs N ≳ 10³ boxes — queued as a methods note, not run
  (budget + no verdict depends on it).

## 5. Deliverables / reproduce

`src/bh_graph/vacuum_cutedge.py` + `tests/test_vacuum_cutedge.py`
(8 passed) + `scripts/vacuum_cutedge.py` +
`results/vacuum_cutedge/{graphs,summary}.json` + this report. Reproduce:
`pytest tests/test_vacuum_cutedge.py -q` → `python3
scripts/vacuum_cutedge.py` (~10 s). Full vacuum set: 37 passed.
Ledger: no changes possible or made (D1–D9 still OPEN per parent).
