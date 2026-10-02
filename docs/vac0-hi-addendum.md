# VAC-0H / VAC-0I addendum — static source field + radial law (FROZEN)

Replay the frozen POT-1 driven-source apparatus (`bh_graph.driven`,
unmodified) on all 27 headline battery cells. Headline question (VAC-0H):

> persistent source → static field: generic under driven adjacency
> dynamics, or J2-specific?

plus the VAC-0I radial-law classification (finite-range / power /
oscillatory / saturating / non-radial) per substrate.

## H0 — C1 regression (no reimplementation)

The POT-1 banked record is reproduced by running the vendored frozen
script **unmodified** as a separate beast job:

```bash
./venv/bin/python scripts/pot1_campaign.py --jobs 20 \
    --out data/vac0/pot1_regression.json
```

C1-H gate: `ladder == POT1-FIELD` and every verdict in
A,B,C,AP,D,E,I,J,TAU,F,G,H,C1,C5,C6,RB true. The headline H runner
(`scripts/vac0_hi_campaign.py`) does not duplicate any POT-1 verdict
logic; J2-headline cells additionally give portable-rule H verdicts.

## H1 — frozen port rules (no per-graph tuning)

H1a. Drive: `omega(G) = -(z + 1/2)` with exact integer degree `z`
(all 27 cells regular; asserted in the runner). This is the POT-1 rule
itself (`-8.5 = -(8+.5)` on J2, `-2.5` on the path), not a fit.
`is_gap_ok` filed per cell (must be true: omega below Gershgorin band).

H1b. Integrator: `DT(G) = (2*pi/|omega|)/296` (commensurate-296 port;
a numerical-accuracy choice, identical in spirit on every cell).
Windows: ring `(T_jump, T_turn) = (12, 24)` (1D precedent: POT-1A
path `T = 12/24`); every other family `(8, 16)` (POT-1B precedent).
`r_set = clamp(diam // 4, 2, 8)` from the cell's own diameter.
Ramp tau headline `8.0`, ladder `{4, 12}` (POT-1 Amendment-2 values).

H1c. Sources: single source = `order[0]` (smallest label; on J2 this
is exactly POT-1's `(0,0)` node). Pair separation
`d* = min(8, max(2, diam // 2))`; pair node = `(d*, 0)` in native
coords on j2/j2quot/square/tri/hex/ring/j2swap8, else (rr\*, j2rewire)
the smallest label at graph distance exactly `d*` from the source
(BFS rule). Exchange mirror `x -> d* - x` (sheet-preserving on J2)
on j2/j2quot/square/tri/hex/ring only; UNDEFINED on rr\*/j2swap8
(broken isometry)/j2rewire.

H1d. Inject secondary (pred_plus_packet, `T = 2.5*T_jump`) on native-
coord cells (j2/j2quot/square/tri/hex/ring/j2swap8) with
`r0 = ((L-8) % L, 0)` (ring: `(N-8,)`), `k = (0.3, 0)` (`(0.3,)`),
`sigma = 4.0` (POT-1H values); UNDEFINED on rr\*/j2rewire (no
meaningful packet coords). D-trace secondary on
j2/j2quot/square/tri/hex/j2swap8 (native 2D orientation); UNDEFINED
on ring (1D), rr\*, j2rewire.

## H2 — headline H verdict: 18 generic core gates (all cells)

Every gate below needs only the graph + battery order + census
diameter, hence is DEFINED on all 27 cells. All tolerances are the
POT-1 values verbatim.

- H2.1 existence/quiet/range: `H_jump_global` 5%; `H_jump_shell` 15%
  (shells `0..r_set`); `H_ramp_inner` 10% (`r = min(4, r_set)`);
  `H_ramp_shell` 25% (shells `0..min(4, rmax)`); `H_eps` (jump
  `eps < 0.02`, mask `dist <= r_set`); `H_J` (`jmax/bmax < 0.05`);
  `H_range` (turn-on 0.05-range within ±1 of prediction range);
  `H_wrap` (2T jump inner drift 5%, shells `0..min(4, rmax)`).
- H2.2 pair: `H_pair_jump` 5%; `H_pair_ramp_inner` 10%
  (`r = min(4, max(2, diam // 6))`); `H_pair_nodal` (>95% sign
  agreement, POT-1C rule incl. `|pred| >= 0.05` floor).
- H2.3 linearity: `H_lin` 5% (λ = 0.5, 2.0); `H_quad` 5% (B scales
  λ²).
- H2.4 phase: `H_phase` (B/J covariance `atol = 1e-9` over the 3
  frozen source phases 0.7/2.1/4.0).
- H2.5 switch causality: `H_switch_instant` (far response `< 1e-9`
  one step after the flip; far = `dist >= min(8, max(4, rmax//2))`);
  `H_switch_cone` (pre-cone B `< 1e-6`, cone velocity
  `v_cone = 2*z`, shells `r_lo..rmax` with
  `r_lo = min(max(6, diam//3), rmax - 1)`).
- H2.6 secular: `H_RB` (`norm_range_24 < 0.01` on the `T = 40` jump).
- H2.7 adiabatic: `H_TAU` (far lingerer medians satisfy
  `c(4) > c(12)` with `c(8)` between; far =
  `dist >= min(10, max(3, rmax//2))`; ends-strict form of the POT-1
  trend, robust to numerical-floor ties).
- H2.8 extension (frozen, one step): if `H_ramp_inner` fails while
  `H_jump_global` passes (same for pair), run the harmonic turn-on
  at `T = 2*T_turn` once and re-evaluate that gate; a pass sets
  `H_slow_settle = 1` (filed; synthesis must discuss timescales).
- H2.9 secondaries (filed, never gating the matrix cell): front
  velocity + 5%/20% threshold stability (shells
  `lo = min(6, max(1, rmax//4))` to `hi = min(rmax-1, lo+7)`;
  UNDEFINED if fewer than 4 arriving shells); D means; inject
  return/acct; exchange match; `sep_resid`; flat-band `|F|`.

The matrix cell is PASS iff all 18 core gates pass (after the frozen
extension). There is no UNDEFINED at cell level.

## H3 — VAC-0I radial-law tree (classification only)

Input: jump-vehicle shell profile `m(r) = mean |A|` + within-shell
dispersion + `Re(A)` shell signs. Order is frozen:

1. `NON-RADIAL` if median within-shell CV over the fit range > 0.75.
2. `SATURATING` (expander-like) if last-two-shell mean > 1/2 the
   bulk max.
3. `OSCILLATORY` if `Re(A)` shell means change sign ≥ 3 times.
4. `FINITE-RANGE` if the log-linear fit (`r = 2..min(8, rmax-1)`,
   ≥3 points) has `r² > 0.9` and `ξ < rmax/2`.
5. `POWER(a)` if the log-log fit has `r² > 0.9`.
6. else `UNCLASSIFIED` (profile filed; no forced label).

`ξ_jump`, `r²`, shell CV, and the full profile are filed per cell.
Family ξ-consistency (`max/min < 1.5` across headline sizes/seeds)
is a C6 secondary, reported at family level, never flipping cells.

H3-AMENDMENT-1 (pre-data apparatus repair, before any beast run):
sign-change counting (rule 3) and CV shells (rule 1) are restricted
to shells with `m(r) > 0.01 * max(m)`. Without this floor, far
shells carrying only integrator contamination flip `Re(A)` signs at
random and force OSCILLATORY on clean exponentials (hex smoke:
`r² = 0.9998` exponential misclassified; zero flips above the
floor). The floor mirrors the filed shell-match floor convention
and leaves the J2 reference verdict unchanged.

## H4 — record trimming (auditability, no physics impact)

Shell series are stored for shells `0..min(rmax, ceil(v_cone*T)+8)`
and time-strided to ≤ 600 rows; fronts/D/switch analyses use only
stored rows. Full-row data never leaves the worker. JSON stays
auditable on ring cells (rmax ≤ 800).

## H5 — firewall notes

- No graph receives graph-specific field parameters: ω/DT/T follow
  the closed rules above (C4).
- Coordinates enter only the frozen secondaries (inject/exch/D),
  never the 18 core gates (C5).
- J2-specific anatomy (branch projectors, AP wall-cut) stays in the
  C1 subprocess; it is not ported and not gated cross-substrate.
- Size replication (C6) is evaluated at family level in synthesis.
