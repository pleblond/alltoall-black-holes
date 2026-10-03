# VAC-0G Amendment G6 (pre-data apparatus repair: LB=1 slope guard)

## Status

Pre-data: the second VAC-0G beast launch crashed in the G1 worker pool
(single-column `interior_slope` polyfit) before writing any output. No
`g_results.json` exists; no G phenomenology has been opened on any
cell. This repair changes no threshold, port rule, or verdict, and is
committed before the rerun.

## G6.1 Bug

`_g1_case` called `interior_slope(prof, WALL_LO, nfit)` with
`nfit = min(lb, 8)` for every `lb > 0`. At LB=1 the fit window is a
single column; degree-1 `polyfit` on one point is rank-deficient and
this LAPACK build raises `LinAlgError: SVD did not converge` (rather
than warning), killing the whole G1 `pool.map`.

## G6.2 Repair (frozen behavior)

Slope is a filed-only readout (G4.1 gates the interior on
`interior_asym` at LB ∈ {4, 5, 6, 8}; the slope value never gates).
For LB=1 the record now files `slope = NaN, n = 1` (a slope from one
column is undefined — filed honestly, not zero-filled); LB=0 keeps
`slope = 0.0, n = 0`. All LB ≥ 2 paths are behavior-identical.

## G6.3 Firewall note

Crash repair, not a result-driven change: the run produced zero
records. NaN-filing follows the census precedent (`vac0.census`
files NaN for failed estimators).
