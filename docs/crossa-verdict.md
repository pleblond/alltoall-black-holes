# CROSS-IMPL-A — Verdict: CROSSA-SCALE (11/11)

Campaign branch: `cursor/crossa-438c`.
Prereg: `docs/crossa-prereg.md` (FROZEN pre-data; commit `0fb530f` predates
ALL CROSS-IMPL-A campaign data; no amendments).
Ledger: `data/crossa/` (50 rung records + regression/audit/redundant +
`verdict.json`). Apparatus: `src/bh_graph/crossa.py`,
`scripts/crossa_campaign.py`, `scripts/crossa_analyze.py`, pins
`tests/test_crossa.py` (9/9, pre-data).
Frozen inputs (read-only, unmodified): banked BHQAREA0 records on main
tail `1f8aa32` (verdict BHQAREA0-MAX) + `qinfo0.py` @ `b737d5e1`
(QINFO0-IDENTICAL) + `bhqarea0.py`/`dim3`/`graphs` (hashes in
`data/crossa/audit.json`; provenance gate CROSSA-A).

Question under test: WHY did BHQAREA0-MAX obtain B_e/q_e ~= 0 and
h_2(P_-) ~= 1 on the BH-like 3D boundary — phase quadrature,
amplitude-scale separation, a mixed mechanism, or a covariance/selection
mechanism — via the exact factorization 2x = r c?

## 1. Campaign record

| Battery | Records | Content |
|---|---|---|
| headline rung | 40 | r = 1..10 x {vacuum, vplus, vpi, vminus} |
| control rung | 10 | r = 1..10 x {vacuum}, plain J3 (no core) |
| regression/audit/redundant | 3 | provenance + identity + firewall + determinism |
| **total** | **53/53** | 0 run-failures (beast2 xargs wave, 96-way, ~35 s) |

Determinism: redundant rerun hashes match exactly (frozen builders +
frozen single-thread env). Analyzer recomputation: every filed anatomy
summary re-verified from filed r/c/x arrays to the census bar (CROSSA-DEF).

## 2. Headline result

**CROSSA-SCALE.** BHQAREA0 MAX is asymptotically amplitude-scale-driven:

- R2 = <r^2>: 0.347 -> 0.0348 -> 0.00642 -> 0.00166 -> 0.000544 ->
  0.000211 -> 9.32e-05 -> 4.53e-05 -> 2.37e-05 -> 1.32e-05
  (strictly decreasing over rungs 7..10, halved: ZERO track).
- C2 = <c^2>: 1.0 at every rung (the banked vacuum is the real-positive
  Perron vector, so c = 1 on all 5304 boundary edges at r = 10):
  NONZERO track (stable).
- X2 = <r^2 c^2> = R2 identically (since c = 1): ZERO track.
- Gamma = X2/(R2 C2) = 1.0 at every rung (NONZERO: no joint suppression;
  the product vanishes because the amplitude marginal does).

Pointwise identity: max|2x - r c| = 0.0 over all 50 rungs (exact).
Banked reproduction: psi_sha match on all 50 rungs, max|x_repro - x_bank|
= 0.0, max|S_repro - S_bank| = 9.1e-13 (h2 summation FP only).
Endpoints: q0 = 0 and ai/aj-zero = 0 on all 50 rungs (f_r0 = 0
everywhere; every boundary edge is class `ok`).
Deficit: r^2 c^2/(2 ln 2) form validated on the inherited |x| <= 0.1
domain at every headline-vacuum rung with coverage (r10: rel 2.3e-06 vs
the 10% bar; r1 filed VACUOUS with 0 in-domain edges, same as BHQAREA0).
MAX reproduction: hbar ladder 0.719 -> ... -> 0.999990, identical to the
banked values (CROSSA-MAX green).

Amplitude anatomy (headline vacuum): mean(r) 0.0036 and median(r) 0.0038
at r = 10; median |log lam| grows 1.15 (r = 1, ratio ~3:1) -> 6.25
(r = 10, ratio ~518:1): the core/exterior amplitude hierarchy steepens
with size. Phase anatomy: |c| = 1 identically (all quantiles 1.0);
mean(c) = 1.0 is NOT filed as quadrature (C2 = 1 is the load-bearing
statistic, and it is bounded away from zero). Joint: at r = 10 all 5304
edges are c-hi-only (r <= 0.5, |c| = 1), both-hi = 0.

## 3. Discriminants (I): the mechanism is state- AND geometry-selected

- Zero-information pattern controls (S): vplus/vpi/vminus give
  R2 = C2 = X2 = 1 constantly with S = 0 EXACTLY (x = +/-0.5 ->
  P_- = 0/1 -> h = 0) at every rung — the opposite extreme from MAX.
  MAX's r -> 0 collapse is a property of the VACUUM on BH-like geometry,
  not of any state.
- Topology control (T): plain-J3 vacuum gives R2 = 0.969 -> 0.942
  (NONZERO, stable: local 3D coupling keeps amplitude balance r ~= 1),
  C2 = 1, X2 ~= 0.94, hbar(10) = 0.1021 (NONMAX, matching the banked
  control). The complete core selects SCALE (r -> 0) where local 3D
  coupling keeps r ~= 1.
- Structural observation (not a gate): C2 = 1 on ALL 50 rung records
  (every banked state is real: Perron-positive vacuum, +/-1 patterns),
  so quadrature, mixed, and covariant mechanisms are structurally
  unreachable in this battery — the only available asymptotic channel
  for x -> 0 is r -> 0. The SCALE verdict is the frozen rules' readout
  of that structural fact, not a post-data threshold choice.

## 4. Firewalls (hold)

No new BH ensemble was generated (reconstruction replays the same frozen
builders on the same battery; psi_sha match on all 50 rungs proves it);
no state, boundary, or edge set was changed or selected by B/q; no
causal claim about BH formation is made (spec section J: SCALE
establishes only the mathematical mechanism by which the already-banked
state obtains B/q -> 0 and h_Q -> 1). Apparatus scans clean on all new
files; fitted params == 0. No entropy reinterpretation, event-trigger
claim, or Planck/BH coefficient fitting appears anywhere.

## 5. Handoff

Per the spec handoff for CROSSA-SCALE: future BH interpretation should
treat MAX primarily as a core/exterior amplitude-hierarchy effect rather
than a phase-quadrature boundary condition. Both the hierarchy growth
(median |log lam| 1.15 -> 6.25) and the control contrast (headline
R2 -> 0 vs control R2 -> 0.94) are filed above. No follow-up campaign is
opened to force any interpretation.

## 6. Reproduce

On beast2 (`ubuntu@99.79.192.152`, workspace `~/crossa-438c`, branch
`cursor/crossa-438c`):

- Pins: `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
  PYTHONPATH=src venv/bin/python -m pytest tests/test_crossa.py -q`
  (9/9 pre-data).
- Enumeration: `scripts/crossa_campaign.py --count` (= 53).
- Wave: `scripts/crossa_campaign.py --print-all | xargs -P 96 -I{} sh -c
  '... --outdir data/crossa'` (see `logs/crossa_wave.log`; 53/53 filed).
- Verdict: `PYTHONPATH=src venv/bin/python scripts/crossa_analyze.py
  data/crossa` (-> `data/crossa/verdict.json`: CROSSA-SCALE, 11/11).
- Suite: `OMP_NUM_THREADS=1 ... PYTHONPATH=src venv/bin/python -m pytest
  tests/ -n 96 -q` (weighted skip automatic; see `logs/crossa_suite.log`).
