# BHQREL0 Amendment-1 (pre-verdict apparatus correction; analyzer not yet run)

One apparatus correction found during wave triage (a `ComplexWarning` in
`logs/bhqrel0_err.log` from the regression task), before the analyzer ran
on this branch. No prereg bar, battery cell, gate, or verdict mapping
changes; no campaign number moves.

## A1-1. Explicit real/imag check in `is_partial_trace_ok`

`float(rp[0, 0])` on a complex reduced-state element discards the
imaginary part with a `ComplexWarning` (numerically harmless here:
imag ~1e-17 — but sloppy enough to hide a real bug). Fix: assert the
real part is 1 and the imaginary part is 0 separately, same `FP_ATOL`
bar. Gated re-run: `regression` task only (the sole task calling this
helper) + full pin file; `regression.json` content verified identical
apart from the `_git` stamp.
