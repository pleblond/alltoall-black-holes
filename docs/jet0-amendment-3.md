# JET0-AMENDMENT-3 — analyzer entrypoint (PRE-VERDICT)

**Date:** 2026-10-03. **Status:** frozen pre-verdict; gated re-run is the
first verdict run (no verdict was produced before this fix).

## 1. Cause (discovered pre-verdict, no verdict seen)

`scripts/jet0_analyze.py` (prereg commit `5f1d351`) defined `main()` but
omitted the `if __name__ == "__main__": main()` guard, so
`python scripts/jet0_analyze.py data/jet0` exited 0 with no output and no
`verdict.json`. Caught on the first analyzer invocation after the 496-task
wave + 24-task retry completed (496 files present, counts green, no
verdict yet). No ladder input was examined (the analyzer never ran).

## 2. Change (runner only, 2 lines, outcome-blind)

- Append the standard entrypoint guard to `scripts/jet0_analyze.py`.
- No physics, battery, gate, ladder, bar, firewall, or pin change.
  `tests/test_jet0.py` unchanged (analyzer is exercised by the verdict
  run itself, not by unit pins).

## 3. Gated re-run (this amendment)

- Run `scripts/jet0_analyze.py data/jet0` on beast2 (496 files + retry
  logs present) for the sole verdict. No campaign re-run needed (data
  unaffected; the bug was verdict-side only).
