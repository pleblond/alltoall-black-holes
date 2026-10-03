# JET-1 Verdict — JET1-NULL (filed post-data)

**Verdict:** `JET1-NULL`, 13/13 gates green.
**Reason:** zero GENUINE full EXACT matches anywhere under unchanged JET definitions
(T1--T5 only).
**Date:** 2026-10-03. **Branch:** `cursor/jet-1-compat-repair-2d36` (base main tail `8b0ffff`).
**Prediction:** `JET1-NULL` (prereg §9) — confirmed without altering any gate or the ladder.

## 1. What was repaired

The malformed JET-0 aggregate comparison in `jet0.forbit_record`:

- ours: filtered ever-compatible keys (`K_ever`, sizes 8 and 2 in the failing cells);
- vendored: all searched candidate keys (sizes 20 and 3), including 12 + 1 all-`False` rows.

Replaced by the correct per-rung bitwise comparison (prereg §6 / JET-1.tex JET1-C):
for every shared searched key `k` and every frozen rung `t`, `c_ours[k,t] == c_vend[k,t]`,
plus searched-key set agreement. `src/bh_graph/jet0.py`, the JET-0 scripts, and the banked
`data/jet0/` records were consumed read-only; no physics definition changed.

## 2. Gate results (`scripts/jet1_analyze.py`, `data/jet1/verdict.json`)

| Gate | Result |
|------|--------|
| A-provenance | counts + 496 total + banked `JET0-INCOMPLETE` 31/32 + sole-`compat_keys`-conjunct pattern on the 2 known cells + `n_genuine = 0` + 18 ordinary / 0 hits + ref sha256 pins — all True |
| A-rerun | frozen `scripts/jet0_analyze.py` rerun on a bank copy regenerates a verdict parsed-identical to the banked verdict on every field |
| B-semantics | 15/15 witnesses file ours + vendored 6-rung vectors for every searched key; ever-classification both sides |
| C-bitwise | 0 mismatches over 1152 compared bits (192 searched keys x 6 rungs); searched sets agree on all cells |
| D-ever | ever-compatible sets agree on all 15 cells (8 = 8 and 2 = 2 in the failing cells) |
| E-orbits | identical quotient inputs + identical re-executed quotient outputs on all cells; ours `n_nontrivial` equals filed vendored values (1 vs 1, 2 vs 2) |
| F-search | exact `n_rewires` / `n_cospec` / `n_iso` on all cells |
| G-allfalse | 12 + 1 load-bearing witness rows, all-`False` on both sides, sets exactly agreeing |
| H-controls | 13/13 previously passing cells green under the repaired comparison |
| I-replay | rerun verdict: only F-orbits red (frozen JET-0 pattern); `n_genuine = 0` |
| J-surface | frozen-import `n_genuine = 0` (merge 0, split 0); `jet1` defines no triviality/jet-equality symbols |
| K-crossing | frozen-import census equals banked (18 ordinary, 0 hits); `jet1` defines no crossing/orientation symbols |
| X-firewall | `fitted_param_count() == 0`, no hidden tuning, `jet1.py` + `jet1_campaign.py` + `jet1_analyze.py` scan clean |

## 3. All-`False` witnesses (JET1-G)

- `traj_bare_ring-8_tiny_antibonding.json` (12 rows, all-`False` both sides):
  `(((0, 1), (2, 3)), ((0, 2), (1, 3)))`, `(((0, 1), (4, 5)), ((0, 4), (1, 5)))`,
  `(((0, 1), (6, 7)), ((0, 6), (1, 7)))`, `(((0, 7), (1, 2)), ((0, 2), (1, 7)))`,
  `(((0, 7), (3, 4)), ((0, 4), (3, 7)))`, `(((0, 7), (5, 6)), ((0, 6), (5, 7)))`,
  `(((1, 2), (3, 4)), ((1, 3), (2, 4)))`, `(((1, 2), (5, 6)), ((1, 5), (2, 6)))`,
  `(((2, 3), (4, 5)), ((2, 4), (3, 5)))`, `(((2, 3), (6, 7)), ((2, 6), (3, 7)))`,
  `(((3, 4), (5, 6)), ((3, 5), (4, 6)))`, `(((4, 5), (6, 7)), ((4, 6), (5, 7)))`.
- `traj_int_handbuilt_INT-hb-twospike.json` (1 row): `(((0, 3), (4, 5)), ((0, 4), (3, 5)))`.

Full per-rung vectors for all 192 searched keys are filed in `data/jet1/compat_*.json`.

## 4. Unchanged physics (JET1-I/J/K)

`n_genuine = 0`, merge-direction 0, split-direction 0, no degeneracy tasks, 18 ordinary
trajectories with 0 genuine-surface crossings — recomputed via the frozen JET-0 analyzer
and frozen ladder functions, identical to the banked JET-0 values. No surface was promoted
by the repair; the NULL is the physical result of the unchanged definitions.

## 5. Execution provenance

- Witness wave: beast2 `~/jet1-2d36`, 15/15 DONE in ~2 s (xargs `-P 15`, OMP 1);
  records carry `_git 4cb3cf4` (prereg commit).
- Analyzer: `scripts/jet1_analyze.py` at `0635332` (prereg analyzer + cosmetic J/K detail
  label fix only; gate booleans and ladder untouched); verdict regenerated post-fix.
- Pins: `tests/test_jet1.py` 8/8 green, `tests/test_jet0.py` 18/18 green on beast.
- Full suite on beast (`pytest -n 192`, standing `tests/test_weighted.py` skip via
  `pyproject.toml`): **4 failed, 2429 passed, 2 skipped** in 130 s. The 4 failures
  (`test_emergent_dim.py::test_weighted_diffusion_partially_untraps`,
  `test_potential.py::test_aperture_keeps_gradient`,
  `test_posteriors.py::test_posterior_leg_creation_near_certain`,
  `test_tunnel.py::test_transfer_matrix_unitarity_and_limits`) reproduce identically on
  clean main tail `8b0ffff` (verified in a detached worktree): pre-existing, unrelated to
  JET-1. This branch adds files only (zero modifications to main-tail tracked files).

## 6. Required filing checklist (JET-1.tex)

- [x] frozen JET-1 prereg before repair execution (`docs/jet1-prereg.md`, commit `4cb3cf4`)
- [x] exact description of the malformed JET-0 comparison (prereg §3, verdict §1)
- [x] per-rung mismatch count: 0 over 1152 compared bits
- [x] searched-key equality: True on all 15 cells
- [x] filtered ever-compatible equality: True on all 15 cells
- [x] orbit equality: True on all 15 cells (membership via identical quotient inputs +
      identical re-executed outputs; counts 1v1, 2v2)
- [x] all-`False` witnesses: 12 + 1 rows (§3, `data/jet1/`)
- [x] unchanged `n_genuine` (0) and crossing results (0 on 18 ordinary)
- [x] final verdict: `JET1-NULL`
- [x] full-suite result: 4 pre-existing failures / 2429 passed / 2 skipped (§5)

JET-0 remains historically filed as INCOMPLETE.

## 7. Stop rule consequence

`JET1-NULL` is earned: do not open JET-2. The dynamical-jet route is closed unless a
genuinely new theorem/state variable is independently earned elsewhere. The remaining
event-occurrence question passes to TIME-Q-0 and, if that also leaves timing
underdetermined, to an explicitly new event-occurrence law.

## 8. Interpretation firewall

`JET1-NULL` establishes only that the tested existing ontology contains no nontrivial
dynamical-jet merge/split admissibility surface. It does not establish stochastic decay,
a hazard law, nuclear interactions, measurement, gravity, or cosmological topology change.
