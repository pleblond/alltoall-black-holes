# BH-Q-REL-0 — Verdict: BHQREL0-CORRELATED (14/14)

Campaign branch: `cursor/bh-q-rel-0-70d6` (PR #150).
Prereg: `docs/bhqrel0-prereg.md` (FROZEN pre-data) + `docs/bhqrel0-amendment-1.md`
(pre-data rung-validation fix, disclosed; moves no number).
Ledger: `data/bhqrel0/` (50 rel records + regression/audit/redundant +
`verdict.json`). Apparatus: `src/bh_graph/bhqrel0.py`,
`scripts/bhqrel0_campaign.py`, `scripts/bhqrel0_analyze.py`, pins
`tests/test_bhqrel0.py` (12/12). Frozen inputs (read-only, unmodified):
QINFO0-IDENTICAL, `graphs.build_complete`, `dim3` J3 apparatus,
BHQAREA0 apparatus + filed ladder (hashes in `data/bhqrel0/audit.json`).

Question under test: do boundary Q-channels on BH-like geometry carry
pairwise relational structure beyond the isolated BHQAREA0 sum — and is
it independent, short-ranged, or long-ranged?

## 1. Campaign record

| Battery | Records | Content |
|---|---|---|
| headline rel | 40 | r = 1..10 × {vacuum, vplus, vpi, vminus} |
| control rel | 10 | r = 1..10 × {vacuum}, plain J3 (no core) |
| regression/audit/redundant | 3 | A/B/C/D + partition/math, firewall, determinism |
| **total** | **53/53** | 0 run-failures (beast2 xargs wave, -P 96, ~1 min) |

Determinism: redundant rerun hashes match exactly (frozen v0 + frozen
single-thread env). Census re-verification: every filed class/bin/
SHORT/LONG cell recomputed from filed arrays with the analyzer's
independent code path to 1e-9 (G-F). Isolated-leg regression:
S/hbar/xs agree with filed BHQAREA0 data on all 50 cells to 1e-9,
psi-sha match 50/50 bitwise (G-REGR).

Provenance: beast checkout `~/bhqrel0-70d6` at commit `9036a3c`
(prereg) plus the Amendment-1 two-line validation fix scp-synced
pre-wave (file-identical to committed `05ab853`, verified by
git-hash `a38b8f1`); `_git` stamps read `9036a3c`. The fix touches
only off-ladder input validation and moves no number.

## 2. Headline result

**BHQREL0-CORRELATED.** Boundary Q-channels on headline-vacuum
geometry carry strong pairwise structure that the frozen ladder
routes to CORRELATED (max|C| = 2.10 ≥ 0.05, ladder decay fails).

Headline-vacuum x-leg ladder (C = normalized covariance; INT/EXT =
shared-interior/exterior-endpoint pairs; DIS = disjoint):

| r | N_∂ | C_INT | C_EXT | C_DIS | SHORT | LONG | decay |
|---|---|---|---|---|---|---|---|
| 1 | 132 | -0.100 | 2.104 | -0.0602 | -0.063 | -0.056 | FAIL |
| 2 | 312 | 0.285 | 0.971 | -0.0219 | -0.018 | -0.011 | ok |
| 3 | … | 0.352 | 0.879 | -0.0117 | 0.076 | -0.007 | ok |
| 4 | … | 0.391 | 0.815 | -0.0072 | 0.106 | -0.000 | ok |
| 5 | … | 0.418 | 0.774 | -0.0048 | 0.123 | 0.005 | ok |
| 6 | … | 0.440 | 0.746 | -0.0034 | 0.136 | 0.009 | ok |
| 7 | … | 0.457 | 0.726 | -0.0026 | 0.147 | 0.012 | ok |
| 8 | … | 0.470 | 0.710 | -0.0020 | 0.155 | 0.014 | ok |
| 9 | … | 0.481 | 0.698 | -0.0016 | 0.163 | 0.015 | ok |
| 10 | 5304 | 0.491 | 0.688 | -0.0013 | 0.169 | 0.016 | ok |

Shared-endpoint coherence is large and stable: C_INT grows
0.28 → 0.49, C_EXT stays 0.97 → 0.69 over rungs 2..10.
Disjoint pairs dilute to ≈ 0 (−0.0013 at r = 10). SHORT-range
C grows 0.076 → 0.169 while LONG stays ≤ 0.016 — a 10× decay
at the top of the ladder.

Rung-1 anatomy (why CORRELATED, not STRUCTURED): the ladder
decay rule requires EVERY rung to decay, and rung 1 fails:
|LONG| = 0.0564 vs the max(0.05, 0.5·|SHORT|) = 0.05 bar — a 13%
margin. Rung 1 has only 3 distance bins (dmax = 3), so the SHORT
pool (d ∈ {1,2}) and the LONG pool (top-2 d = {2,3}) OVERLAP at
d = 2; decay is nearly vacuous there by construction. Rungs 2..10
(all with disjoint SHORT/LONG pools) decay cleanly. The verdict is
filed as the frozen ladder routes it; the r=1-overlap margin is
disclosed here rather than re-ruled.

Note on scale: C is a class-conditional mean cross-product over
global variance, NOT a Pearson coefficient — it is unbounded
(C_EXT = 2.10 at r = 1 reflects few EXT pairs, n = 222, over
outlier x values). The prereg claims no bound.

## 3. Discriminants: the structure is vacuum- AND core-selected

- s-leg tracks x-leg: max|C^s| = 2.73; per-rung signs match
  (e.g. r = 10: 0.478/0.704/−0.0013 vs x-leg 0.491/0.688/−0.0013).
- Topology control (plain-J3 vacuum): C_INT ≈ −0.10 → −0.157
  (NEGATIVE, stable), C_EXT decays 0.46 → 0.026, SHORT/LONG ≈ 0
  at top rungs. The complete core selects strong positive
  shared-endpoint coherence where local 3D coupling gives weak
  negative INT and decaying EXT.
- State control: VPLUS/VPI give degenerate legs (Var = 0, all 20
  records, C None) — constant patterns carry no variation to
  correlate. VMINUS (binary x = ±0.5) gives negative structure
  (C_EXT ≈ −0.30 → −0.22, C_INT ≈ −0.09 → −0.17, LONG = 0.0
  exactly): sign-flipped vs vacuum, filed descriptively.
- The positive growing INT/EXT coherence is thus a property of
  the VACUUM on BH-like geometry, not of any state or of J3 alone.

## 4. Interpretation firewall (holds)

CORRELATED establishes ONLY pairwise correlation structure of
boundary Q-channels in this model. It is not entanglement, not a
relational entropy, not mutual information (no joint functional is
defined — the debt is preserved, not closed), and not
Bekenstein–Hawking thermodynamics, a physical event horizon,
Hawking radiation, holography, or the Planck scale. No C value is
converted to bits anywhere.

## 5. Follow-up

A follow-up campaign (not this one) could: (a) define an earned
joint-information functional over correlated channel pairs and test
whether its correction inherits area scaling; (b) adopt a
top-rung-weighted or disjoint-pool decay rule so the smallest rung
cannot drive the ladder (proposed, not applied — the frozen rule
binds this verdict); (c) test the mechanism behind negative
control/VMINUS INT vs positive headline INT.

## 6. Reproduce

Beast2 (`ubuntu@99.79.192.152`, workspace `~/bhqrel0-70d6`,
interpreter `~/store0-95bd/venv/bin/python`, `PYTHONPATH=src`,
`OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1`):

- Battery: `scripts/bhqrel0_campaign.py --print-all | xargs -P 96
  -I{} sh -c '… --outdir data/bhqrel0'` (53 tasks; `WAVE-DONE rc=0`,
  0 FAIL; `logs/bhqrel0_wave.log`, `logs/bhqrel0_err.log` empty).
- Analyzer: `scripts/bhqrel0_analyze.py data/bhqrel0 data/bhqarea0`
  → `VERDICT BHQREL0-CORRELATED`, 14/14.
- Suite: `pytest tests/ -n 96 -q` → 4 failed / 2551 passed /
  2 skipped (`logs/bhqrel0_suite.log`); the 4 failures are the
  identical pre-existing main set (`test_posteriors`,
  `test_potential`, `test_tunnel`, `test_emergent_dim`), verified
  against `~/gate-main-fullsuite.log`; this branch modifies no
  pre-existing file.
