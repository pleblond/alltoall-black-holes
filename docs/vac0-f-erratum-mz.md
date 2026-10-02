# VAC-0F erratum: MZ window (filed 2026-10-02, post-run correction)

## What happened

`scripts/vac0_f_campaign.py::_run_mz` ran the MZ corridor with the
SUPERSEDED SLIT-Campaign-1 window (`T = 80`, 800 steps, interior gate
`t* < 75`) instead of the banked SLIT-Amendment-1 window (`T = 160`,
1600 steps, gate `t* < 150`).

Banked reference (`origin/cursor/slit-interference-6bce`,
`docs/DEFERRED.md`):

- Campaign-1: MZ-phi VOID — `t* = 77.2` at window edge 80
  (peak not captured); ratios exact anyway.
- Amendment-1 (pre-rerun): MZ window `T = 80 -> 160`, gate
  `t* < 75 -> t* < 150`.
- Campaign-2: SLIT-3-PASS — `half = 0.5000`, `pi = 4e-33`,
  `t* = 77.2` interior-160, single-arm exact, `arm_ratio = 3.66`.

## Effect on the filed F record

`data/vac0/f_results.json` (`mz`, `mz_verdict`) reproduces the
Campaign-1 numbers to the digit (`t* = 77.2`, `half = 0.5`,
`pi = 3.75e-33`, `arm_ratio = 4.31`, single-arm `0.0`) and hence
`mz_verdict = false` ONLY via the voided `t* < 75` bound. Apparatus
fidelity is exact in both generations; no physics gate is affected
(the 0a/0b/slit1 verdicts use independent banked rules, and the J2
+ open regressions reproduce `V = 0.853/0.678` exactly).

## Correction (same frozen lib, banked window)

Re-ran `_run_mz` verbatim with 800 -> 1600 steps (7 s, local;
30-node graph, no campaign data involved):

`data/vac0/mz_corrected.json`:

- `t* = 77.2`, `w0 = 0.4437`, `half = 0.5000`, `pi = 3.75e-33`,
  `single_arm_maxdiff = 0.0`, `arm_ratio = 3.657`.

All six banked SLIT-3 gates pass (`t* < 150` interior). Corrected
verdict: **MZ = PASS** (exact Campaign-2 replication).

This corrects a documented transcription error against an
unambiguous banked reference. It changes no threshold, no port rule,
and no cell verdict. The original `f_results.json` is preserved
unchanged for audit.
