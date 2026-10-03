# QINFO0 Amendment-1 (pre-data apparatus corrections; no campaign data exists)

Two apparatus corrections found during pin validation on beast, before any
campaign data was produced. Neither changes the prereg bar values, battery
cells, gates, or verdict mapping.

## A1-1. Scale-aware exact-algebra comparison

`is_hadamard_ok` failed on cell `g5` (|psi|^2 ~ 1e4) with deviation
2.7e-12 against the absolute `FP_ATOL = 1e-12`: pure floating-point
rounding from `/sqrt(2)` (relative error ~1e-16). Fix: comparisons of
unbounded algebraic quantities use `_close(a, b)`, i.e.
`|a - b| <= FP_ATOL * max(1, |a|, |b|)` — absolute 1e-12 at O(1) scale,
relative 1e-12 above it. The bar value is unchanged; entropy-weight
comparisons (O(1) quantities, gates Q-B/C/F/J) keep absolute form.

## A1-2. Label-mapped roundtrip field comparison

`roundtrip_cell` compared recovered vs predecessor fields positionally,
but `split_recover` returns order `[rest..., i, j]`, not the predecessor
order — cell `r3` (path-3, nonempty rest) mismatched while weights and
covers matched. Fix: compare fields mapped by node label. The checked
claim (exact recovery) is unchanged.
