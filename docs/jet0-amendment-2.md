# JET0-AMENDMENT-2 — traj-int argv bugfix (PRE-VERDICT)

**Date:** 2026-10-03. **Status:** frozen pre-verdict; gated re-run of
affected tasks only. **Supersedes:** runner detail only; no physics,
battery, gate, or ladder change from PREREG + AMENDMENT-1.

## 1. Cause (discovered during 496-task wave, pre-verdict, no verdict seen)

The 496-task wave (AMENDMENT-1 battery) finished 472 DONE / 24 FAIL.
`logs/tasks_err.log` shows the 2 `traj --kind int` tasks failed with
`argparse: argument --sub: expected one argument`. Root cause:
`scripts/jet0_campaign.py::task_argv` emitted
`--task traj --kind int --sub  --ftag INT-...` with an empty `--sub`
value (int kind has `sub=""` by frozen design, `traj_record` ignores
`sub` for int and keys on `ftag`). Bash word-splitting drops the empty
value, so `--sub` consumes `--ftag` as its value and argparse errors.
The other 22 FAILs (all `mergejet j2-L4`, 17:18:36--17:18:54, no stderr)
are transient start-up kills under the initial 96-way load spike
(single-task retry green in 134 s, see AMENDMENT-1 wave notes); they
need no code fix, just re-run.

No ladder input examined. The 472 DONE records are unaffected (none are
traj-int; the bug only affects argv encoding for the 2 int tasks, and
transient kills leave no partial files).

## 2. Change (runner only, outcome-blind, frozen by this amendment)

- `scripts/jet0_campaign.py::task_argv` for `traj`: omit `--sub` when
  `t[2]` is empty (int kind). `run_traj` already treats missing/empty
  as `""` (`args.sub or ""`), and `traj_record("int", "", ftag)` keys
  on `ftag` only (frozen `build_int_field` dispatch). Generated records
  are bitwise identical to what the intended argv would have produced.
- No `src/bh_graph/jet0.py`, battery, analyzer, pin, bar, ladder, or
  firewall change. `tests/test_jet0.py` unchanged (no int-traj pin;
  existing `traj_record` smoke covers the physics path).

## 3. Gated re-runs (this amendment)

- Keep: 472 DONE from the 496-task wave (old runner correct for all
  non-int tasks; verified by per-task `regression_ok`/`pred_ok` gates,
  not by trust).
- Re-run: the 24 FAILs only (22 transient j2-L4 + 2 int with fixed
  argv) on beast2 (96-way slots now free, OMP 1, nice), appended to the
  same `data/jet0/` with fresh `logs/jet0_retry.log`. Counts gate
  requires 496 files (472 + 24) before the verdict.
- Then: `scripts/jet0_analyze.py data/jet0` for the sole verdict (no
  verdict was run on partial data).
