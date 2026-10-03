# JET0-AMENDMENT-1 — L28 cost scope + er-24 fiber cap + exact-to-128 (PRE-VERDICT)

**Date:** 2026-10-03. **Status:** frozen pre-verdict; full gated re-run.
**Supersedes:** battery + apparatus details of `docs/jet0-prereg.md` (prereg
commit `5f1d351` remains the frozen pre-data record; this amendment is the
dated change log with gated re-runs, per prereg section 8).

## 1. Cause (discovered during initial wave, pre-verdict, no verdict seen)

The initial 590-task wave (beast2, 96-way, OMP 1) stalled with 224 DONE /
18 transient FAILs (all retried green) and 96 heavy tasks still running
after 30+ min. Profiling (pre-verdict, instrument only, no ladder input):

- **j2-L28 (N = 1568):** `krylov_order_qr` takes ~22 s per call with
  `m = 334--336`, `recurrence_resid ~ 1e289`, `stable = False`
  (`m = 129` at `1e-6` vs `336` at `1e-9`/`1e-12`). MERGE-JET L28 tasks
  carry ~280 fiber alts each (`8-per-c x D_SHORT`, prereg cost cap), so
  ~280 x 22 s ~= 1.7 h per task. 90 L28 MERGE-JET tasks ~= 153 h CPU.
  TRAJ L28 (2 tasks) similar fiber cost. Exact certification is infeasible
  at N = 1568 (`m = 336`, 200-digit big ints, Bareiss + Fraction blowup).
  B-order (`is_order_ok`: resid <= `BAR_LEDGER` + stable) is red on L28.
- **er-24 (N = 24):** merged node has 9 neighbors, 9,842 undirected covers
  x `D_GRID` (27) = 265,734 alts per task (prereg "tiny/exhaustive" rule
  assumed low degree like ring-8 with 140 alts). Each alt runs exact order
  + T1--T5 (GraphMatcher + eigvalsh on N = 24). Measured >38 min per task
  and still running; projected ~7 h per task. 12 er-24 MERGE-JET tasks
  ~= 84 h CPU.
- **j2-L8 (N = 128):** `krylov_order_qr` gives `m = 12`, `resid ~= 0.05`,
  `stable = False` (16 at `1e-12` vs 12 at `1e-9`/`1e-6`). B-order red.
  Exact path (`krylov_order_exact`) on the same edge gives `m = 12`,
  `recurrence_exact_ok = True` in 0.06 s (Bareiss on 128 x 13, 32-bit
  magnitudes). QR ill-conditioning is apparatus, not physics (unscaled
  Krylov columns, spectral radius ~4--6, `6^12 ~= 2e9` dynamic range).

No ladder input was examined (no GENUINE counts, no verdict). The 224
partial records are **discarded** (old battery, incomplete counts); the
gated re-run below is the sole verdict input.

Precedents: STORE-0 excluded j2-L28 for cost pre-data ("L4/L8 + textures
cover the vacuum leg"); STORE-0/RES-0 use the frozen 25-per-c J2 fiber
subset rule; EVENT-0 anchors L28 rewires (8 primaries, 64 cap).

## 2. Changes (frozen by this amendment)

- **(a) L28 scope (cost + QR apparatus):** j2-L28 is excluded from ORD,
  MERGE-JET, and TRAJ (94 tasks: ord 2, mergejet 90, traj 2). j2-L28 is
  retained for WITNESS (`true:j2-L28`, 1 task, no fiber census, modal
  series identity on N = 1568) and SOURCE (6 causal legs on j2-L28,
  2 orders + 21-step Krylov each, no fiber census, pre-arrival
  diagnostic). Rationale: fiber censuses on N = 1568 are infeasible
  (1.7 h/task) and QR order is uncertifiable (resid 1e289, unstable);
  retained L28 legs are light (seconds--minutes) and diagnostic-only
  (B-gate does not consult them; S-witness/O-source file raw numbers).
- **(b) er-24 fiber cap (cost):** er-24 MERGE-JET (12 tasks) uses the
  frozen 25-per-c cover subset rule (J2-L4 precedent,
  `COVER_CAP_PER_C = 25`) x `D_GRID` (27), instead of exhaustive
  (9,842 covers). New alts per task <= 250 x 27 = 6,750 (vs 265,734,
  39x reduction, ~11 min/task projected). Rule is outcome-blind
  (first-25-per-`c`-bucket in canonical cover order, fixed pre-data).
  Other non-J2 subs (ring-8, path-8, triangle, handbuilt) keep
  exhaustive (low degree, 100--500 alts, seconds).
- **(c) Exact-to-128 (apparatus fix):** `N_EXACT_MAX` 32 -> 128.
  `krylov_order` uses exact integer certification (QR-guess + Bareiss
  rank + Fraction recurrence + exact verify, filed `fallback`) for
  N <= 128, QR above. j2-L8 (N = 128, m = 12) moves from QR
  (resid 0.05, unstable, B-red) to exact (0.06 s, B-green). No other
  sub changes method (j2-L4 N = 32 exact unchanged; L28 N = 1568 QR
  unchanged but now out of B-gated families). Bars unchanged
  (`BAR_FP`/`BAR_LEDGER`/`BAR_PHYS`/`BAR_U1`/`QR_BAR` frozen).
  Prereg section 2 "N > 32" now reads "N > 128"; section 6 B-order
  "exact N <= 32" now reads "exact N <= 128". All other gates, ladder,
  firewall, prediction (JET0-NULL) unchanged.

## 3. New frozen battery (recomputed from amended code)

- ord 17 (was 19, minus 2 L28), mergejet 235 (was 325, minus 90 L28),
  splitjet 79, samen 24, forbit 15, traj 28 (was 30, minus 2 L28),
  lower 10, hidden 24, source 10, generic 40, witness 14.
- **Total 496** (was 590). Checksum recomputed from `jet0.all_tasks()`
  (see `tests/test_jet0.py` pins). Campaign (`scripts/jet0_campaign.py`)
  and analyzer (`scripts/jet0_analyze.py`) unchanged (they enumerate
  from `jet0` code; B-gate uses `N_EXACT_MAX` constant).

## 4. Gated re-runs (this amendment)

- Discard: `data/jet0/*.json` from the initial 590-task wave (224 DONE,
  partial counts, old battery). `data/jet0/ref/` retained (byte-identical
  QDYN0B + EVENT-0 refs, amendment-independent).
- Re-run: full 496-task battery on beast2 (96-way, OMP 1, nice), fresh
  `logs/jet0_wave.log` + `logs/tasks_err.log`, then
  `scripts/jet0_analyze.py data/jet0` for the sole verdict.
- Pins: `tests/test_jet0.py` updated (exact-128 bar, 496 census) and green
  on beast before the re-run wave.
- Full suite on beast (`pytest -n 192`, standing `test_weighted.py` skip
  via `pyproject.toml` addopts) after the verdict, before merge.

## 5. What this amendment does NOT change

No bar/ladder/firewall/prediction change. No per-task physics change
(except the outcome-blind er-24 cover subset and the exact-vs-QR method
for N in (32, 128], both filed per record via `order.method` /
`order_method` / `n_alts`). No EVENT-0/QDYN0B ref change. No firing
implication (jet equivalence never fires, all virtuals).
