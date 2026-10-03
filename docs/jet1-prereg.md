# JET1-PREREG — Per-Rung Compatibility Repair and Final Jet Adjudication (FROZEN PRE-DATA)

**Status:** apparatus + battery + gates + ladder frozen; repair NOT YET EXECUTED.
Commit predates ALL JET-1 witness runs. Branch `cursor/jet-1-compat-repair-2d36`,
base main tail `8b0ffff` (Release v5.9.0).

**Mission (JET-1.tex, OPEN / READY):** resolve the single apparatus defect that forced
`JET0-INCOMPLETE` despite an autopsy showing zero genuine dynamical-jet surfaces and zero
crossings. JET-1 is not a new physics search. Its sole scientific purpose is to replace the
malformed aggregate compatibility regression with the correct per-rung bitwise comparison,
then rerun the frozen jet verdict logic without changing the physical definition of a jet
surface. If the repaired regression passes, JET-1 mechanically adjudicates the already-frozen
dynamical-jet question.

## 1. Source scope (deliberately narrow)

No survey of historical branches or unrelated PRs. JET-1 consumes only:

1. The filed JET-0 branch/artifacts needed to reproduce its apparatus, records, analyzer
   logic, and autopsy: `origin/cursor/jet-0-dynamical-jet-d0f5` tip `243aa15`
   (`src/bh_graph/jet0.py`, `scripts/jet0_campaign.py`, `scripts/jet0_analyze.py`,
   `tests/test_jet0.py`, `docs/jet0-prereg.md`, `docs/jet0-amendment-1.md`,
   `data/jet0/ref/*`), ported onto this branch as read-only baseline, plus the two
   beast-run catches present in the bank-producing workspace (`scripts/jet0_campaign.py`
   traj int-kind argv fix, `scripts/jet0_analyze.py` `main()` guard) and the 496-record
   bank + `verdict.json` copied from beast2 `~/jet0-d0f5/data/jet0/` (records carry
   `_git e98fb34cde05d3567d331f83d314bae7cb1f15af`, the JET-0 base). The frozen JET-0
   forbit autopsy diagnostic (`jet0_forbit_autopsy.py`, beast workspace) is filed under
   `scripts/` read-only; it is not imported by any gate.
2. The exact vendored EVENT-0 equivalence reference consumed by JET-0:
   `data/jet0/ref/event0_orbits.json` (sha256
   `71a3103af3d19f7dcd880c14445843e895ff8337bf1228ddfa69365205369811`, per
   `data/jet0/ref/SOURCES.txt`), used byte-identically. No broader repository archaeology.

Consumed banked modules (`merge0`, `split0`, `store0`, `reservoir0`, `trigger0`, `rewire0`,
`ballistic`, `sym0`, and siblings) are byte-identical between the JET-0 base `e98fb34` and
the main tail `8b0ffff` (the tail adds only four new files: `bhent.py`, `dim31.py`,
`qdyn0b.py`, `subclass0.py`; zero deletions/modifications), so the ported apparatus runs
unchanged physics.

## 2. Frozen scientific basis (JET-0, historical)

JET-0 established and filed: 496/496 campaign tasks banked; 31/32 frozen gates green; the
only red gate was F-orbits via the `compat_keys` conjunct on exactly two cells
(`forbit_traj_bare_ring-8_tiny_antibonding_json.json` with 8 ever-compatible of 20 searched
keys, `forbit_traj_int_handbuilt_INT-hb-twospike_json.json` with 2 of 3); `n_genuine = 0`;
no genuine jet surface crossed on 18 ordinary trajectories;
algebra/order/recurrence/decoder/regression/Theta/orientation/sectors/witness/firewall gates
green. JET-0's formal verdict remains `JET0-INCOMPLETE`. JET-1 must not rewrite or supersede
that historical verdict.

## 3. Exact description of the malformed JET-0 comparison

In frozen `jet0.forbit_record` (`src/bh_graph/jet0.py`):

```python
compat_keys = set()                      # filled only when rep["compat"] is True
...
vend_keys = set(vend.get("compat", {}).keys())
# Vendored compat maps rkey -> per-rung bool list; our keys = rkeys
# compat at >= 1 rung. Cross-check on the key SETS.
ck["compat_keys"] = bool(compat_keys == vend_keys)
```

- `compat_keys` (ours) = searched keys compatible at **at least one rung** (filtered set
  `K_ever`, size 8 and 2 in the two failing cells).
- `vend_keys` (vendored) = **all searched candidate keys** in the vendored table
  (unfiltered, sizes 20 and 3), including rows whose per-rung compatibility vector is
  all-`False` at every rung (12 and 1 such rows respectively).

The two sets live in different spaces (filtered vs unfiltered), so set equality fails
exactly when the vendored table contains all-`False` rows. The 13 already-passing cells
contain no all-`False` vendored rows, which is why the malformed comparison does not fail
there. All other `cross_check` conjuncts (`n_rewires`, `n_cospec`, `n_iso`, `n_nontrivial`)
are green in all 15 cells, including the two failing ones.

## 4. Autopsy finding (frozen input to JET-1)

The filed JET-0 autopsy demonstrated: ours equals vendored after applying the same
firing-at-least-once filter; representative counts match exactly (8 = 8 and 2 = 2);
ours-only set is empty; every vendored-only key is an all-`False` row; per-rung
compatibility bits have zero mismatches; orbit counts match (1 vs 1, 2 vs 2); search counts
match. JET-1 re-proves every one of these claims mechanically under the gates below; the
autopsy itself is input, not a gate.

## 5. Hard firewall

JET-1 may not: redefine dynamical-jet equivalence; add a new jet observable; change Krylov
order; change any physical bar/tolerance; change trajectory cells; add a "near surface";
reinterpret lower-order matches as surfaces; change `n_genuine` logic; change crossing
logic; change time-reversal/orientation logic; add stochastic firing; search for a different
event trigger; tune the repaired comparison to obtain NULL. Only the malformed compatibility
regression may be repaired. Mechanically: `src/bh_graph/jet0.py`, `scripts/jet0_campaign.py`,
`scripts/jet0_analyze.py`, and the banked `data/jet0/` records are read-only inputs;
`src/bh_graph/jet1.py` defines no triviality, jet-equality, crossing, or orientation logic
(gated by J/K/X); the ladder measurement reuses the frozen `scripts/jet0_analyze.py`
functions by import.

## 6. Repair specification (frozen)

For each of the 15 F-orbits cross-check cells, let `c[k,t]` be the per-rung compatibility
bit of searched candidate key `k` at frozen rung `t` (6 rungs, `T_LADDER`, `DT = 0.05`).

- **JET1-B (semantics):** classify every vendored candidate row by its per-rung vector
  `c[k] = (c[k,1], ..., c[k,T])`, computed identically for ours (recomputed via the frozen
  `equiv_search` + `equiv_compat` code path on the identically rebuilt trajectory) and
  vendored data. `ever-compatible(k)` iff any rung bit is true. No row is deleted from the
  underlying tables.
- **JET1-C (correct regression):** for every searched candidate key `k` shared by the two
  implementations and every frozen rung `t`, require `c_ours[k,t] == c_vend[k,t]` bitwise;
  also require searched-key sets agree under the exact candidate-search semantics. All-`False`
  rows are valid searched candidates and compare bitwise; they are not required to appear in
  a separately filtered firing set.
- **JET1-D (filtered diagnostic):** `K_ever_ours == K_ever_vend` as a secondary check only;
  it does not replace the per-rung bitwise gate.
- **JET1-E (orbits):** using the identical per-rung compatibility data, reproduce the frozen
  EVENT/JET orbit quotient (`jet0.equiv_orbits` over the ever-compatible set, the frozen
  JET-0 semantics). Require exact orbit membership/count agreement. Because `equiv_orbits`
  is a deterministic pure function of `(G, cands)`, agreement is verified by feeding it
  identical canonical inputs derived from each side's per-rung data and requiring identical
  re-executed outputs plus match to the filed vendored `n_nontrivial`. Orbit equivalence
  definitions are unaltered.
- **JET1-F (search counts):** exact `n_rewires` / `n_cospec` / `n_iso` agreement before
  compatibility filtering on all cells.
- **JET1-G (all-False witnesses):** retain the two JET-0 failure cells; for each all-`False`
  row prove `c_ours[k,t] == c_vend[k,t] == False` for all `t`. These are the load-bearing
  repair witnesses.
- **JET1-H (controls):** the 13 previously passing cells must remain green under the repaired
  comparison.
- **JET1-I (frozen replay):** rerun the frozen `scripts/jet0_analyze.py` end-to-end on a copy
  of the bank (originals read-only) and recompute `n_genuine`, surface classification,
  trajectory crossings, time-reversal/orientation checks, sector controls, and firing
  firewall under unchanged code paths. Expected JET-0 values are recomputed, never tuned.
- **JET1-J/K (criteria retained):** the exact JET-0 genuine-surface and crossing definitions
  are reused by import; no surface is promoted by the repair. If `n_genuine = 0`, that remains
  a physical NULL result; with no genuine surface the genuine-surface crossing count is
  necessarily zero.
- **JET1-L (minimal rerun):** read-only bank use; rerun only the 15 compatibility/orbit/search
  witnesses + analyzer/adjudication + JET-1 pins + full suite on beast (standing
  `test_weighted.py` skip). No 496-task physics rerun.
- **JET1-M (no-new-data):** newly generated records exist only to validate the repaired
  apparatus; no new jet hypothesis, no ladder amendment.

## 7. Frozen gates (mechanical, `scripts/jet1_analyze.py`)

| Gate | Requirement |
|------|-------------|
| A-provenance | Per-family bank counts equal the frozen battery census (17/235/79/24/15/28/10/24/10/40/14 = 496); banked `verdict.json` is `JET0-INCOMPLETE` 31/32 with F-orbits the sole red gate; banked forbit records show exactly the two known cells with `cross_check_ok == False` and `compat_keys` the sole False conjunct; banked `n_genuine == 0`, merge/split genuine 0, `k_crossed == {ordinary_n: 18, crossed: False, hits: [], n_hits: 0}`; vendored ref sha256 match the SOURCES pins. |
| A-rerun | Frozen `scripts/jet0_analyze.py` rerun on a bank copy regenerates a verdict parsed-equal to the banked verdict on every field. |
| B-semantics | All 15 compat witnesses file ours + vendored per-rung vectors for every searched key (6 rungs each); ever-classification present on both sides. |
| C-bitwise | Zero per-rung mismatches on all shared searched keys across all 15 cells; searched-key sets agree on all cells. |
| D-ever | Ever-compatible sets agree on all 15 cells. |
| E-orbits | Identical quotient inputs (ever sets) and identical re-executed quotient outputs on all cells; ours `n_nontrivial` equals filed vendored `n_nontrivial` on all cells. |
| F-search | Exact search counts on all cells. |
| G-allfalse | Each of the two known cells carries at least one all-`False` witness row, all-`False` on both sides, with ours/vendored all-`False` sets exactly agreeing. |
| H-controls | All 13 previously passing cells green under the repaired comparison. |
| I-replay | Rerun verdict: all gates except F-orbits green; `n_genuine == 0`; 18 ordinary trajs, 0 crossings. |
| J-surface | Frozen-import `n_genuine == 0`; `jet1` module defines no triviality/jet-equality symbols. |
| K-crossing | Frozen-import crossing census equals banked (0 on 18 ordinary); `jet1` module defines no crossing/orientation symbols. |
| X-firewall | `fitted_param_count() == 0`, no hidden tuning, `jet1.py` + `jet1_campaign.py` + `jet1_analyze.py` scan clean. |

If any gate is red, the verdict is `JET1-INCOMPLETE`.

## 8. Verdict ladder (precedence: INCOMPLETE first, then ladder)

- **JET1-SURFACE:** repaired regression exact and the unchanged JET logic finds at least one
  nontrivial genuine dynamical-equivalence surface satisfying the frozen surface criteria
  (allowed only if the unchanged JET-0 definitions themselves produce the surface).
- **JET1-STATIC:** repaired regression exact and nontrivial full dynamical-jet equivalence
  exists only in static/symmetry-protected cases, with no ordinary trajectory crossing under
  the frozen criteria.
- **JET1-DEGENERATE:** repaired regression exact and jet equivalence exists, but multiple
  inequivalent structural continuations remain under the frozen uniqueness criterion.
- **JET1-NULL:** repaired regression exact and `n_genuine = 0` under the unchanged JET
  definitions, with no genuine surface crossed by the frozen ordinary trajectories. Formally
  closes the dynamical-jet admissibility route on the tested ontology.
- **JET1-INCOMPLETE:** repaired regression cannot be certified, JET-0 provenance fails, or
  another apparatus failure prevents mechanical adjudication.

Ladder measurement reuses frozen `jet0_analyze._genuine_task_sets` / `_k_crossed` by import
on the live bank (J/K-gated unchanged definitions).

## 9. Prediction

Based on the filed JET-0 autopsy, the pre-data prediction is `JET1-NULL`. This prediction
does not alter the ladder or any gate.

## 10. Battery and execution

15 compat witnesses (`compat_tasks()` = `forbit_tasks()` keys), each recomputing the frozen
trajectory + `equiv_search` + per-rung `equiv_compat` + frozen `equiv_orbits` quotient and
comparing against the vendored table. Records: `data/jet1/compat_<cell>.json` + analyzer
verdict `data/jet1/verdict.json`. Execution on beast2 (xargs fan-out); pins
(`tests/test_jet1.py`) green before the witness wave; full suite on beast (`pytest -n 192`,
standing `test_weighted.py` skip via `pyproject.toml` addopts) after the verdict.

## 11. Required filing

Frozen prereg (this file, pre-data); exact malformed-comparison description (section 3);
per-rung mismatch count; searched-key equality; filtered ever-compatible equality; orbit
equality; all-`False` witnesses; unchanged `n_genuine` and crossing results; final verdict;
full-suite result. JET-0 remains historically filed as INCOMPLETE.

## 12. Stop rule and interpretation firewall

If `JET1-NULL` is earned: do not open JET-2. The dynamical-jet route is closed unless a
genuinely new theorem/state variable is independently earned elsewhere. The remaining
event-occurrence question passes to TIME-Q-0 and, if that also leaves timing underdetermined,
to an explicitly new event-occurrence law. `JET1-NULL` establishes only that the tested
existing ontology contains no nontrivial dynamical-jet merge/split admissibility surface; it
does not establish stochastic decay, a hazard law, nuclear interactions, measurement,
gravity, or cosmological topology change.

## Appendix: frozen file manifest

- `src/bh_graph/jet1.py` (repair apparatus; imports frozen `jet0` helpers only)
- `scripts/jet1_campaign.py` (15-task witness runner; reuses frozen `jet0_campaign` IO helpers)
- `scripts/jet1_analyze.py` (gates + ladder; reuses frozen `jet0_analyze` by import/subprocess)
- `tests/test_jet1.py` (pins)
- `scripts/jet0_forbit_autopsy.py` (filed frozen JET-0 diagnostic, read-only, not a gate input)
- `data/jet1/compat_*.json` (15 witnesses) + `data/jet1/verdict.json` (post-data)
