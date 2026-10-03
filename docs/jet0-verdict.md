# JET-0 — Verdict: JET0-INCOMPLETE (31/32, autopsy-resolved)

Campaign branch: `cursor/jet-0-dynamical-jet-d0f5`, base main tail `e98fb34`.
Prereg: `docs/jet0-prereg.md` (frozen pre-data; prediction JET0-NULL).
Amendments (all pre-verdict, dated, gated re-runs): `docs/jet0-amendment-1.md`
(L28 cost scope + er-24 fiber cap + exact-to-128; battery 590 -> 496),
`docs/jet0-amendment-2.md` (traj-int argv bugfix; runner only),
`docs/jet0-amendment-3.md` (analyzer entrypoint; first verdict run).
Ledger: `data/jet0/verdict.json` (32 gates).
Apparatus: `src/bh_graph/jet0.py`, `scripts/jet0_campaign.py`,
`scripts/jet0_analyze.py`, pins `tests/test_jet0.py` (18/18).
Autopsy computation: per-rung EQUIV recompute on beast
(`jet0_forbit_autopsy.py`, post-data diagnostic, not a gate).

Null under test: zero GENUINE full EXACT dynamical-jet matches anywhere —
merge/split admissibility is not encoded in local jet equality of the
pre- and post-event enlarged states `X = (G, psi, Q)` beyond the frozen
triviality classes T1--T5 (`H(G) = -A`, `J = 1`, Krylov-exact waiting,
`Q` the STORE-0 minimal local store frozen between events).

## 1. Campaign record

| Battery | Tasks | Content |
|---|---|---|
| ord | 17 | Krylov order + recurrence + stability per (sub, edge) |
| mergejet | 235 | true merge + STORE encode, regression, fiber-alt jet census |
| splitjet | 79 | split cells + J2 spot, reference-rule jet classes |
| samen | 24 | same-N rewire jet census (incl. 6 EVENT-0 REG-REWIRE cells) |
| forbit | 15 | vendored orbit-traj recompute + per-rung EQUIV + jets |
| traj | 28 | fixed-G evolution + rung jet census + modal crossings |
| lower | 10 | nullspace z1/z1z2-zero constructions + non-containment |
| hidden | 24 | sector anatomy + fiber-alt census + triviality |
| source | 10 | causal trajs + near/far rung jets + crossing census |
| generic | 40 | deterministic fresh-seed fields + census + codimension |
| witness | 14 | forward+backward series verification of true/T3 reps |
| **total** | **496** | 496/496 filed, 0 lost |

Wave: beast2 (`xargs -P 96`, OMP 1): 472 DONE / 24 FAIL (22 transient
load-spike kills retried green, 2 traj-int argv fixed by AMENDMENT-2),
then 24/24 on retry. All task files stamped `_git = e98fb34` (beast
checkout base); apparatus synced from branch tip incl. Amendments 1-3.
STORE regression: `E-regression` green (`pred_ok` + roundtrip +
compatibility on every cross-N record); `B-order` green after exact-to-128.
Full suite on beast (`pytest tests/ -n 96`, standing `test_weighted.py`
skip): 2308 passed, 2 skipped, incl. `test_jet0.py` 18/18; the 4 failures
(`test_emergent_dim`, `test_potential`, `test_posteriors`, `test_tunnel`)
are pre-existing on main, confirmed identical on the event0/qdyn0b/store0/
weave0 peer checkouts (see `logs/fullsuite_jet0.log` on the beast checkout).

## 2. Headline result

**JET0-INCOMPLETE, 31/32.** The only red gate is `F-orbits`, and only via
its `compat_keys` conjunct on 2 of 15 forbit cells
(`traj_bare_ring-8_tiny_antibonding`, `traj_int_handbuilt_INT-hb-twospike`).
Every other conjunct of F on those cells is green (`n_rewires`, `n_cospec`,
`n_iso`, `n_nontrivial` all bitwise), all 13 remaining forbit cells are
fully green, and the rest of the instrument is fully green:

- `A-algebra`: earned jet identities exact on all 299 merge-jet true pairs.
- `B-order`/`C-recurrence`: orders + recurrences certified, modal series agree.
- `D-decoder`/`I-theta`/`L-orientation`: `R x U(1)` covariance, Theta identity,
  jet conjugation, first-derivative orientation rule all exact.
- `E-regression`: merge/split STORE regression clean everywhere.
- `G-j2neg`: J2-L4 SAMEN complete (apparatus ran).
- `H-census`/`Q-unique`/`R-compare`: complete classes, complete enumeration
  at every full match, all six comparisons filed with witnesses.
- `J-setsurface`: `Sigma_split = Theta Sigma_merge` as sets (empty-empty
  equal; non-empty filed for audit).
- `K-crossing`: modal refinement converged on all 28 trajs.
- `M-lower`/`N-hidden`/`O-source`/`P-generic`/`S-witness`: constructions
  verify, sector certs complete, census + codim filed, forward+backward
  series identities hold for recurrence-compatible reps.
- `X-firewall`: symbol scan clean, `fitted_param_count() == 0`.

Ladder input filed in `verdict.json`: `n_genuine = 0`
(`merge_dir = 0`, `split_dir = 0`; descriptive triviality totals over the
census: 1,796,198 not-a-match, 5275 T2 quotient, 949 T4 static-zero),
`K-crossed = false` over 18 ordinary trajectories — i.e. the
would-have-been rung is NULL, exactly the prereg prediction. But per the
frozen ladder (prereg section 7: INCOMPLETE > DEGENERATE > SURFACE >
STATIC > NULL; no bar/ladder change post-data), NULL is unreached and
**INCOMPLETE is the filed verdict**, with the failure autopsied below
(genuine-or-autopsy per prereg: this one is autopsy).

## 3. Autopsy: the F cross-check compared a filtered set against an unfiltered one

`forbit_record` builds our compat key set as the rkeys firing at >= 1 rung
(`compat_keys.add(...)` only under `rep["compat"]`), but cross-checks it
against the raw vendored table `set(vend["compat"].keys())`, which lists
*every* searched candidate — including candidates that never fire at any
rung (all-`False` per-rung rows). The gate therefore demands equality
between a filtered set and an unfiltered one, which fails exactly when the
vendored table contains never-firing rows.

The census + recompute exhibit show the EQUIV reproduction itself fully
succeeds, on both failing cells:

- Ours == vendored-filtered (keys with any `True` rung) exactly: 8 == 8
  on ring-8 antibonding, 2 == 2 on INT-hb-twospike; ours-only is empty
  both sides.
- Every vendored-only key is an all-`False` row (12 on ring-8, 1 on
  INT-hb-twospike): both sides agree these candidates never fire.
- Per-rung compat agrees bitwise on all shared keys (0 mismatches over
  8 and 2 keys x 6 rungs).
- Orbit reproduction matches (`n_nontrivial` 1v1 and 2v2), and
  `n_rewires`/`n_cospec`/`n_iso` match bitwise (32/20/20 and 18/3/3).

The 13 passing cells confirm the diagnosis by contrast: their vendored
tables contain zero all-`False` rows, so filtered-vs-unfiltered coincide
and the check passes. The bug fires if and only if the vendored table
lists never-firing candidates — a property of the frozen apparatus encoding
(predating all JET-0 data), not of the physics: the two failing cells are
simply the only ones whose fields leave some searched rewires incompatible
on every rung. Zero residual points at jet dynamics: no GENUINE match is
implicated, and the underlying per-rung EQUIV + orbit + jet numbers all
reproduce EVENT-0 bitwise.

## 4. What this establishes (firewall)

- The earned apparatus reproduces the EVENT-0 EQUIV inventory bitwise
  (search counts, per-rung compat, orbits) on all 15 orbit-trajs; the red
  conjunct is a set-encoding mismatch in one cross-check line, not a
  reproduction failure and not missing data.
- The NULL-consistent ladder input (`n_genuine = 0`, uncrossed, Theta-set
  equality vacuous) is filed descriptively; INCOMPLETE here is an
  apparatus-leg verdict, and no NULL claim is earned by this campaign.
- No fitted jet weights, tolerances, truncations, or STORE modifications
  were introduced at any stage (X green; Amendments 1-3 are scope/runner/
  entrypoint only, all pre-verdict with gated re-runs).

## 5. Follow-up

A JET-1 (or JET-0b) re-test with the corrected F cross-check: filter the
vendored key set to rungs-firing (`any(bools)`) before set comparison, or —
better — replace the key-set check with the strictly stronger per-rung
bitwise compat comparison (already demonstrated 0-mismatch on the full
battery in the autopsy exhibit). No gate, bar, or ladder rung of JET-0
itself was changed post-data.

Reproduce: `pytest tests/test_jet0.py -q` (18 pins);
`python scripts/jet0_campaign.py --count` (496);
`python scripts/jet0_analyze.py data/jet0` (31/32 INCOMPLETE).
