# CROSSB-0 — Verdict: CROSSB-PARTIAL (17/17, autopsy-resolved)

Campaign branch: `cursor/crossb0-two-stitch-ec06`.
Prereg: `docs/crossb0-prereg.md` (frozen pre-data; prediction CROSSB-PARTIAL).
Derivation: `docs/crossb0-derivation.md` (frozen pre-data; true secular proof).
Ledger: `data/crossb0/verdict.json` (17 gates).
Apparatus: `src/bh_graph/crossb0.py`, `scripts/crossb0_campaign.py`,
`scripts/crossb0_analyze.py`, pins `tests/test_crossb0.py` (9/9).

Claim under test: J2 zero weak-stitch binding cut at every finite
separation vs J3 separation-uniform exclusion interval, with the spec
secular `t^2 G (G +- Gam) = 1`, `|t| ln(1/Delta) -> 8 pi sqrt2`,
cancelled `t^2` log law, and J3 `24/sqrt(55)` / `sqrt(128/11)` bounds.

## 1. Campaign record

| Battery | Tasks | Content |
|---|---|---|
| norm | 5 | edges, Bloch cross-check, intertwining, V convention, identities |
| det | 28 | finite-rank determinant pins (true vs spec secular) |
| green | 20 | k-sum Greens (`lam_inf`, slopes, combos, `C1`, ladders) |
| cert2 | 27 | J2 finite-size certification (counts, Y pair + validity) |
| cert3 | 36 | J3 finite-size certification (counts, shifts, pairing) |
| ctrl | 4 | square/cubic descriptive controls |
| **total** | **120** | 120/120 filed, 0 lost |

Wave: beast2 (`xargs -P 96`), 120/120 DONE, 0 FAIL, 0 stderr bytes
(`logs/crossb0_wave.log` on the beast checkout); all task files stamped
`_git = 4695239` (prereg commit; zero checkout skew).
Full suite on beast: see section 6.

## 2. Headline result

**CROSSB-PARTIAL, 17/17.** Every instrument gate is green, every
distinction conjunct is green, and all four sharp-debt flags fire:

- Instrument: counts 120/120 exact; A-spec edges `+-8/+-12` within
  `1e-9` with Bloch cross-check; A-self intertwining/anti-dead/
  commutator `<= 1e-12`, k-identities exact, V norm/rank exact; B-det
  true residual `<= 6.5e-13` (bar `1e-8`) at every filed level;
  C-green two-N agreement, nn `lam = 0.12496` (vs `1/8`), `C1 =
  0.082911` (vs `1/12`), monotonic ladders; H-inst pairing `<= 1e-9`,
  Y-validity logic exact; X-firewall clean, fitted `0`.
- Distinction: D1 J2 slopes `0.0358--0.0403` within 10% of `1/(8 pi)`
  with `lam_inf` in `0.125--0.172` (`>> 1/16`); D2 all J3 edge combos
  `<= 0.1201` (`< 0.20`); D3 J3 small-t shifts decay `~1/L^3`
  (e.g. `0.0666 -> 0.0205`); D4 every J2 cert binds `1/1`; D5 J3 nn
  `t = 10` binds (finite cut).
- Debt: F-spec (spec residual `0.0078--0.44`, bar `1e-3`, at every det
  level); F-slope (`>= 27%` from `1/(8 pi sqrt2)` for all `r`);
  F-two (nn `t = 2` has exactly 1 level above at all `L`, not 2);
  F-loose (nn minus-combo `0.120`, true nn cut `~7.94`, looser than
  `sqrt(128/11) ~ 3.41`).

Per the frozen ladder, distinction-held plus debt-fired files PARTIAL.
The earned theorem: J2 first-binding cut `0` for every `r != 0` (one
channel, true `8 pi` law) while J3 keeps a uniform non-binding interval
(`|t| <= 24/sqrt(55)` via the derivation chain) — a genuine
dimension/substrate-dependent binding distinction with the sharp spec
extras as located debt.

## 3. Autopsy: the spec secular is the decoupled-stitch truncation

The campaign's central analytic finding (proved pre-data in the
derivation note, pinned here on 28 finite controls): the exact secular
is `t^2 (G +- Gam)^2 = 1` (Schur: `det(I - t^2 g^2)`), while the spec
form `t^2 G (G +- Gam) = 1` drops the `t^2 Gam (Gam +- G)` terms.

The data show exactly where the truncation bites and where it hides:

(a) **It bites wherever inter-stitch coherence matters.** At band-edge
  levels (`Gam ~ G`), spec residuals are `0.06--0.44` (J2: `0.21--0.44`,
  J3 near-edge: `0.06--0.13`) — the missing `Gam^2 +- G Gam` terms are
  order-unity. Every consequence built on the spec channels (two-channel
  binding for all `t != 0`, `8 pi sqrt2`, the `t^2` log law, the
  `12/G3` / `4/(I G3)` formulas) inherits the error.
(b) **It hides where the second stitch decouples.** The smallest spec
  residual (`0.0078`, still `7.8x` above bar) sits at the deep J3 level
  `E* = +-17.0` (`t = 16`), where `G = 0.062`, `Gam = -0.0005`: far
  outside the band `Gam -> 0` and both forms collapse to `t^2 G^2 = 1`.
  The spec form is thus the `Gam -> 0` truncation of the truth — valid
  only in the decoupled far field, false in the binding regime.
(c) **Counts cannot see it.** J3 `t = 10/16` binds `1/2` channels under
  both the true cuts (`12`, `~7.94`) and the spec formulas (`~10.7`,
  `~8.7`): channel counts coincide. Only the determinant pin (exact
  finite resolvent, residual `<= 6.5e-13` vs `>= 0.0078`) discriminates
  — which is why CROSSB-B pins determinants, not counts.

No data supports NONDIMENSIONAL (all five distinction conjuncts green
with margin) or NORMALIZATION-DEBT (edges, Greens, `sigma`, `lam > 1/16`,
nn `1/8`, `C1 = 1/12` all match the spec normalization exactly).

## 4. What this establishes (firewall)

- Effective dimensionality qualitatively controls weak local-defect
  binding: zero first-binding cut in J2, finite uniform exclusion in J3.
- The repository realization matches the spec normalization (edges,
  Green map, parity, exact edge identities) — the debt is purely in the
  channel structure and sharp constants, located flag by flag.
- PARTIAL here is a proved-distinction verdict with sharp debt, not a
  failure verdict: no instrument is red, nothing is missing or untried.
- No bound state is identified with matter, a force, or an event; no
  cosmology is invoked. A future formation campaign may ask whether
  dynamically generated defects exploit this theorem (spec handoff).

## 5. Follow-up

A CROSSB-1 re-test could: interval-certify the J3 edge lemma
(`Gd(12+) <= 0.13`, currently numerical with 27% margin); pin the true
nn cuts (`12`, `~7.94`) as exact threshold equalities; and certify the
`8 pi` law by direct log-slope at singularity-subtracted grids. No gate,
bar, or ladder rung of CROSSB-0 itself was changed post-data.

Reproduce: `pytest tests/test_crossb0.py -q` (9 pins);
`python scripts/crossb0_campaign.py --count` (120);
`python scripts/crossb0_analyze.py data/crossb0` (17/17 PARTIAL).

## 6. Full suite (beast2, parallel)

`OMP=1 PYTHONPATH=src venv/bin/python -m pytest tests/ -n 96 -q`
(standing `test_weighted.py` skip): **2557 passed, 2 skipped, 4 failed**
in 132 s (`logs/fullsuite.log` on the beast checkout). The 4 failures
(`test_posteriors`, `test_potential::test_aperture_keeps_gradient`,
`test_tunnel`, `test_emergent_dim`) are byte-identical to the
`~/gate-main-fullsuite.log` failures on current main — pre-existing,
none from this branch (additive files only; all 9 `test_crossb0` pins
pass inside the suite).
