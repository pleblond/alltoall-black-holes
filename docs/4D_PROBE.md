# 4D vacuum candidates — curiosity probe (EXPLORATORY, no verdicts)

**Branch:** `cursor/4d-vacuum-probe-7061` · **Date:** 2026-09-28.
**Status:** curiosity only. No prereg (nothing here can promote, kill, or
move any ledger item), no verdicts, no follow-up claims. Methods frozen in
`scripts/vacuum4d_probe.py`; results in `results/vacuum4d/probe.json`.

## Objects

| Candidate | Builder | N | Degree | Regularity (measured) |
|---|---|---|---|---|
| tesseract dual (4D cubic) | `vacuum4d.build_tesseract(3/4)` | 81 / 256 | k=8 | exact, test-asserted |
| 24-cell dual (D4 + 24 bonds) | `vacuum4d.build_d4_24cell_dual(4/6)` | 128 / 648 | k=24 | exact, test-asserted |
| 16-cell dual (= 24-cell 1-skeleton, 16-regular) | NONE — multi-orbit vertex set (D4 holes, not a lattice); out of scope | — | — | stated, not stretched |

## Findings (measured, exploratory)

1. **Both candidates are flat at adequate sizes.** Tesseract L=4: κ≡0
   exactly (256 nodes, 1024 edges). D4 nc=6: κ≡0 to 4.4e-16 (648 nodes,
   7776 edges). So a regular flat vacuum exists in 4D under both the
   boring (k=8) and symmetric (k=24) candidates.
2. **Same small-box wraparound artifact as 3D Kelvin.**
   Tesseract L=3: uniform κ=+0.125. D4 nc=4: uniform κ=+0.333. Both
   vanish at the next size up. Lesson (3rd instance): periodic boxes
   need diameter comfortably above the W₁ coupling range; small-box
   positives are artifacts until proven otherwise.
3. **3D rigidity pattern reproduces in 4D** (single s=4 excursion,
   radial/min-depth profile): tesseract-L4 gives shell-0 κ̄=−0.28,
   shells 1–4 exactly 0 — contact-localized, no propagation. D4-nc4:
   shell-0 drops +0.33→+0.11, bulk stays at vacuum value. No scaling
   of any kind (all R² NaN/negative on flats). Consistent with the
   3D C1 kill; not an independent kill (n=1 excursion, exploratory).
4. **Spectra sane:** tesseract-L4 λ₁=0.25, λ_max=2.0 (bipartite ✓);
   D4 λ₁=0.5, λ_max=1.333 (non-bipartite ✓). Stationary TV=0 (regular).

## Cute pattern (not a result)

Packing-optimal dual degrees track the kissing numbers: 2D hex k=6 =
kissing 6; 3D FCC k=12 = kissing 12; 4D 24-cell dual k=24 = kissing 24
(Musin 2003). Least-area optima do not track it (3D: WP 12/14). Another
face of the functional-dependence point in the 4D discussion.

## Reproduce

`pytest tests/test_vacuum4d.py -q` (4 passed) →
`python3 scripts/vacuum4d_probe.py` (~15 s). Full suite unaffected
(new tests only). Compute: local, <$1.
