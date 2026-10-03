# CROSSB0-PREREG — Dimension-Controlled Two-Stitch Binding (FROZEN PRE-DATA)

**Status:** apparatus + battery + gates + ladder frozen; campaign NOT YET RUN.
Commit predates ALL CROSSB-0 campaign records. Branch
`cursor/crossb0-two-stitch-ec06`, base main tail `f5545ba`.

**Mission (CROSS-IMPL-B.tex, OPEN / READY):** theorem-first test of the
dimensional contrast for two local stitches of real hopping `t != 0` at
nonzero separation `r` between two identical substrates: J2 zero
weak-stitch binding cut at every finite separation versus J3 nonzero
separation-uniform exclusion interval. Numerical work validates the
repository realization; it does not determine the theorem.

## 1. Frozen ontology + consumed apparatus (read-only, byte-identical)

`H(G) = -A(G)`, `J = 1`, `hbar = 1` (P1/EM-0 locked). J2 torus
(`formation.j2_torus_graph/coords`), J3 torus (`dim3.j3_torus_graph/coords`),
Bloch conventions (`continuum.j2_bloch_*`, `dim3.j3_bloch_*`), symmetric
sectors `H U = U H_Q` with `H_Q = -2A` square/cubic (`malus`, `dim3`
`symmetric_embedding`, `square/cubic_hamiltonian`, `sheet_projectors`),
dense/CSR Hamiltonian (`ballistic.hamiltonian`). Banked code stays
byte-identical. No sibling campaign data is consumed (spec narrow-scope
rule); the derivation in `docs/crossb0-derivation.md` is self-contained.

Bilayer (frozen): `H0 = Hd (+) Hd`, `V = -t(|a1><a2| + h.c. + |b1><b2| +
h.c.)` with stitch cells `a = 0`, `b = r != 0`, sheet bit 0 at both
cells. Micro Green map (frozen): `Gd = (G_Q(0) + 1/E)/2`,
`Gam_r = G_Q(r)/2` for `r != 0` (sheet-blind off-cell). J2 parity
`sigma = (-1)^(r1+r2)`.

Pre-data derivation result (see derivation note): the exact finite-rank
secular is `t^2 (G +- Gam)^2 = 1`, NOT the spec form `t^2 G (G +- Gam)
= 1`. The battery pins the true form against exact finite-control
determinants and files the spec-form residual as a sharp-debt flag.

## 2. Frozen conventions

- Bars: `BAR_FP = 1e-12` (exact algebra), `BAR_ID = 1e-9` (edges,
  k-identities), `BAR_DET = 1e-8` (determinant pins), `BAR_PAIR = 1e-9`
  (staggered pairing), `BAR_LAM_AGREE = 5e-4`, `BAR_NN = 1e-3`,
  `BAR_SLOPE_AGREE = 1e-4`, `BAR_SLOPE_TRUE = 0.15`, `BAR_C1 = 1e-3`,
  `BAR_COMBO_AGREE = 5e-4`. Distinction bars: `D2_COMBO = 0.20`,
  `D3_TOP = 0.1`. Debt bars: `SPEC_RES = 1e-3`,
  `DEBT_SLOPE_SPEC = 0.15`, `LOOSE_COMBO = 0.25`.
- Constants: edges 8/12, `LAM_LO = 1/16`, `LAM_NN = 1/8`, `C1 = 1/12`,
  `SLOPE_TRUE = 1/(8 pi)`, `SLOPE_SPEC = 1/(8 pi sqrt2)`.
- Frozen eval grids: `LAM_DELTA = 1e-3`, slope pair `(0.05, 0.2)`,
  `J3_EVAL_E = 12.05`, `J3_C1_D = 0.05`, mono ladders, identity/covariance
  points (see `crossb0.py`). Out-of-band bar `1e-9`. Y-validity:
  `Delta > 1e-8` and `L >= 4/sqrt(Delta)`.
- No RNG anywhere. No fitted parameter (`fitted_param_count() == 0`).
- No out-of-band level is called a particle; no force/cosmology claim.

## 3. Core definitions (frozen)

True channels: `1 - t^2 (G+Gam)^2 = 0`, `1 - t^2 (G-Gam)^2 = 0`
(Schur complement on the 4-site support; equivalently the two
layer-exchange sectors). Spec residual: `min_+- |t^2 G (G +- Gam) - 1|`.
J2 divergent combo `G + sig Gam -> +inf` (`E v 8`), cancelled combo
`G - sig Gam -> lam_inf(r)`; `Y1 = |t| ln(1/Delta)`,
`Y2 = t^2 ln(1/Delta)` with frozen validity flags (descriptive only:
the validity regime needs `L >= 4 exp(4 pi/t)`, infeasible for
`t <= 2`, so no ladder gate consults Y values). J3 combos
`Gd +- Gam` at `12.05`; nn `C1 = Gd + Gam_nn`.

Finite-size resolution (pre-data, derivation note sec. 11): at feasible
`L`, J2 shows one finite-size level (`Delta ~ 1/L^2`, pre-asymptotic
since `xi ~ 1/sqrt(Delta_inf) >> L`) and J3 shows one perturbative
shift (`Delta ~ 1/L^3`) for every small `t`; counts alone cannot
adjudicate the distinction. The distinction is therefore adjudicated on
infinite-volume Green data plus the frozen analytic chain, with
finite-size records as consistency (det pins, pairing, decay).

## 4. Frozen battery (deterministic, no RNG; 120 tasks)

- norm (5): j2 `L in {4,6,8}`, j3 `L in {4,6}`: edges, Bloch cross-check,
  intertwining/anti-dead/commutator, V convention (norm/rank/hermitian),
  k-sum resolvent identity, axis-swap covariance, parity table.
- det (28): j2 `L in {4,6}` x 4 `r` x `t in {1,4}` (16); j3 `L in {4,6}`
  x 3 `r` x `t in {10,16}` (12): out-of-band levels with true-det and
  spec-form pins from the exact finite-substrate resolvent.
- green (20): j2 6 `r` x `N in {128,256}` (12): `lam_inf`, two-point
  log-difference slope, divergent-ladder growth, sheet-blindness; j3
  4 `r` x `N in {32,64}` (8): edge combos, `C1`, combo/product
  monotonic ladders, sheet-blindness.
- cert2 (27): j2 3 `r` x `t in {0.5,1,2}` x `L in {6,8,10}`: counts,
  levels, `Y1/Y2` + validity flags, pairing.
- cert3 (36): j3 4 `r` x `t in {0.5,1,2,3}` x `L in {4,6}` (32) plus nn
  `t in {4,10}` x `L in {4,6}` (4): counts, shifts, pairing.
- ctrl (4): square `L=6` nn/diag `t=1`; cubic `L=4` nn `t in {1,10}`:
  descriptive dimensional controls.

Runner `scripts/crossb0_campaign.py` (`--count` = 120, `--print-all`,
per-`--task`, `_git` stamp). Unit pins `tests/test_crossb0.py` (9/9 on
beast pre-data). Wave on beast2, 96-way xargs, `OMP=1`, detached nohup.

## 5. Stages -> gates (scripts/crossb0_analyze.py, frozen; 17 gates)

Instrument (any red => CROSSB-INCOMPLETE): counts (exact 120 + det/green
key coverage); A-self (intertwining/anti-dead/commutator `<= 1e-12`,
k-identity `<= 1e-9`, swap covariance `<= 1e-12`, V hermitian/norm/rank);
B-det (true residual `<= 1e-8` at every filed level, `>= 1` level per
det task above and below); C-green (two-N agreement, nn `1/8`,
`C1 = 1/12`, monotonic ladders, sheet equality, reality); H-inst
(pairing `<= 1e-9`, fields filed, Y-validity logic recomputed);
X-firewall (scans clean + `fitted == 0`); S-report (one rung filed).

Spec constants (red with green instrument => NORMALIZATION-DEBT):
A-spec (edges `+-8/+-12` within `1e-9`, Bloch cross-check).

Distinction (any red => CROSSB-NONDIMENSIONAL): D1 J2 slope within 15%
of `1/(8 pi)` and `lam_inf - 5e-4 > 1/16` for all 6 `r`; D2 all J3 edge
combos `< 0.20`; D3 J3 small-t shifts decay (`top6 < top4`, `top6 < 0.1`);
D4 every J2 cert has `>= 1` level above and below; D5 J3 nn `t=10`
binds (finite cut).

Sharp debt (any true with green distinction => CROSSB-PARTIAL): F-spec
(spec residual `>= 1e-3` at every det level); F-slope (slope `>= 15%`
from `1/(8 pi sqrt2)` for all `r`); F-two (nn `t=2` has exactly 1 level
above at all `L`); F-loose (nn minus-combo `< 0.25`, i.e. true nn cut
above 4, looser than `sqrt(128/11)`).

## 6. Verdict ladder (frozen logic, mirrored in code)

- CROSSB-DIMENSIONAL: distinction holds and zero debt flags fire.
- CROSSB-PARTIAL: distinction holds and `>= 1` debt flag fires.
- CROSSB-NONDIMENSIONAL: distinction red (zero-vs-finite false).
- CROSSB-NORMALIZATION-DEBT: A-spec red with green instrument.
- CROSSB-INCOMPLETE: any instrument gate red.

Precedence INCOMPLETE > NORMALIZATION-DEBT > NONDIMENSIONAL > PARTIAL >
DIMENSIONAL. A secular-form mismatch with matching edges/Greens routes
to PARTIAL (sharp debt), not DEBT, by this frozen precedence.

Prediction (pre-data, not a gate): CROSSB-PARTIAL. The derivation proves
pre-data that the spec secular form is false (true: `t^2 (G+-Gam)^2 =
1`), which forces F-spec; the J2 divergent channel still binds for all
`t != 0` with true coefficient `8 pi`, and J3 keeps a uniform exclusion
interval, so the qualitative distinction is expected green while the
sharp spec constants (`8 pi sqrt2`, cancelled log, two-channel binding,
`sqrt(128/11)` sharpness) fail as debts.

## 7. Firewall (binding)

No theorem-from-numerics (analytic chain frozen in the derivation note;
Green data validate the realization only); no tuned asymptotic
constants (two-point slope is frozen linear algebra, not a tune);
no post-data weakening of `lam_inf > 1/16` or the J3 uniform bound;
no empirical cut replacing the proven bound; no single-stitch mixing;
no particle/force/cosmology interpretation; no post-data separation or
`t` choice. Symbol-scan audited; `fitted_param_count() == 0`.
Amendments, if any, as CROSSB0-AMENDMENT-n with gated re-runs.

## 8. Pre-data validation disclosure

Before freezing, smoke probes on beast (derivation scratch, never filed
as campaign records) checked: bilayer ED counts on the cert/det grids,
true-det residuals (`~1e-13`), spec residuals (`0.06--0.5`), staggered
pairing (`~1e-14`), k-sum N-convergence and identity exactness, slope
values per `r`, shift-decay ratios, control behavior, and task timing.
Smoke informed battery scope (det `t` values that bind, cert `t <= 3`,
green `N`, round bars with margins) but no gate, bar, or ladder item was
adjusted to force a rung: every bar is a round mechanical value the
frozen apparatus satisfies with margin, and the debt flags follow the
pre-data analytic derivation. No campaign record exists at this commit.
