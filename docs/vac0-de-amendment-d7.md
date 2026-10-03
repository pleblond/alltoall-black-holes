# VAC-0D/E Amendment D7 (pre-data apparatus repair: RR intrinsic-only)

## Status

Pre-data: the first VAC-0D/E beast launch crashed in the worker pool
(`AttributeError` in `coherence_of` on RR cells) before writing any
output. No `de_results.json` exists; no D/E phenomenology has been
opened on any cell. This repair implements the already-frozen spec
(master prereg P2.1 + D6.3), changes no threshold, port rule, or
verdict, and is committed before the rerun.

## D7.1 Bug

`_cases_for` correctly restricts RR cells (`rr3/rr4/rr8`, no native
coordinates) to the single intrinsic `delta` case, but `_evolve_case`
then unconditionally evaluated coordinate readouts on it:

- `coherence_of` -> `grid_coherence_2d(psi, order, coords=None, L)`
  crashed on `coords.items()`;
- `flux_of` / `d_trace` would likewise crash on `edges=None`;
- `com` / `unwrap_trace` / `msd_exponent_rs` / `velocity_autocorr` /
  `fit_velocity` need coordinates that do not exist.

## D7.2 Repair (frozen behavior)

For cells with `coords is None` (exactly the RR cells), `_evolve_case`
records an intrinsic-only record:

- coordinate readouts (`prep_D/S/angle/J`, `prep_C/M`, `mean_D`,
  `max_D`, `mean_S`, `mean_J`, `alpha`, `cv_mean50`, `v`, `speed`,
  `r2`, `disp`) are filed as `null` (UNDEFINED readout, never 0);
- evolution, norms (`norm_dev`), branch anatomy (`w_plus/w_zero/
  w_minus`, `mixing`, `n_zero`), and the full D6.3 `delta` intrinsic
  block (`delta_vshell`, `delta_r2`, `delta_ipr*`, `delta_p0_final`,
  `delta_rmax`) are computed unchanged;
- the cell verdict is unchanged: `_verdicts` returns headline
  `UNDEFINED` for RR (D6.3 intrinsic filed, not verdict-bearing).

No other cell kind is touched: every non-RR path is byte-identical in
behavior to the D6 runner (verified by diff review; the added branch
is guarded solely on `coords is None`).

## D7.3 Firewall note

This is a crash repair, not a result-driven change: the run produced
zero records, so no outcome could have informed it. The repaired
behavior is exactly what D6.3 already promised ("headline UNDEFINED
there, intrinsic filed").
