# VAC-0J addendum — B/J quadrature portability (FROZEN pre-data)

No J campaign has run; no J phenomenology is opened. This addendum freezes
the J apparatus before its beast launch. The J algebra gates below are
exact identities whose thresholds come from machine precision, not from
any banked outcome; the J_useful synthesis rule is a frozen scoping
decision (which verdicts count as "useful phenomenology"), not a fit.

## J0. Question split (campaign brief)

- J_alg: is the `B/J` quadrature algebra generic? (direct test, this stage)
- J_useful: does the substrate support the large-scale phenomenology
  needed for useful propagation/static response? (read-only consumption
  of the banked DE + HI cell verdicts, §J4; never inferred from J_alg)

## J1. Cells + states (frozen construction, no fitting)

All 27 headline battery cells (`battery_headline()`), RR included
(algebra needs no coordinates). Four frozen arms per cell:

- `random`: complex Gaussian state, seed 0, normalized.
- `stagger`: uniform-amplitude phase-structured state. Geometric cells
  (native coords): `psi_v = exp(i*q*x_v)`, `q = 0.3` (DE headline k).
  Coord-less cells (RR): `psi_v = exp(i*2*pi*3*rank(v)/N)` with rank by
  node label (deterministic, coord-free, full Δθ coverage).
- `packet_mid`: DE-port Gaussian packet (`k/sigma/r0` exactly as in
  `vac0_de_campaign._prep_sigma_k_r0`) unitarily evolved to `T_DE/2`
  with the DE `dt = 0.1`, where `T_DE` is the frozen D1 window per
  cell (table §J2). RR cells: single-node `delta` at `order[0]`
  evolved to `T = 5.0` (half the DE RR window).
- `driven`: HI-port analytic steady state
  `steady_predict(h, pins=[order[0]], s=[1.0], omega=-(z+1/2))`
  with exact integer degree `z` (H1a rule, no evolution).

## J2. Frozen T_DE/2 table (half-windows from DE addendum D1)

`j2_L20: 3.0, j2_L28: 5.0, j2quot_L20: 5.0, j2quot_L28: 5.0,
square_n28: 8.0, square_n40: 12.0, ring_N400: 60.0, ring_N1600: 240.0,
tri_L28: 5.0, tri_L40: 7.0, hex_L28: 5.0, hex_L40: 8.0,
j2swap8_*: 5.0, j2rewire_*: 5.0, rr_*_*: 5.0 (delta).`

## J3. J_alg gates (LAW rung; exact algebra, machine-precision bars)

Convention (A5): `bilinears` returns the BARE quadrature
`J_bare = Im(C)`; the brief's continuity current is `J_tex = 2*J_bare`.
With `C_uv = psi*_u psi_v` per bond, `B_uv = Re(C)`,
`Dth = arg(C)`:

- `J_decomp`: `max|C - (B + i*J_tex/2)| < 1e-9` on every arm.
- `J_cos`: on `stagger`, `max|B/|C| - cos(Dth)| < 1e-9`
  (bonds with `|C| <= 1e-300` excluded; none for uniform states).
- `J_sin`: on `stagger`, `max|J_tex/2|C| - sin(Dth)| < 1e-9`.
- `J_dynnodrift`: `J_decomp` also holds on `packet_mid` and `driven`
  (same 1e-9 bar): unitary evolution and the steady solve introduce
  no quadrature drift.

`J_alg = PASS` iff all four pass. These gates have teeth only against
convention/implementation errors (notably the bare-vs-continuity
factor of 2); any physics failure here would be a code bug, and the
cell would be INVALID (apparatus repair), never FAIL. Expected
outcome under VAC-0A A5: PASS on all 27 cells (LAW).

Filed secondaries per arm: max residual, cos/sin fit R² over bonds,
`max|C|` (relational amplitude scale), bond count.

## J4. J_useful rule (phenomenology rung; frozen conjunction)

`J_useful(cell) = PASS` iff every phenomenology verdict DEFINED on
that cell passes:

- geometric cells (j2/j2quot/square/ring/tri/hex/j2swap8/j2rewire):
  `DE D_cell == PASS` AND `HI H_pass == true`;
- RR cells (DE headline UNDEFINED by P2.1): `HI H_pass == true` alone.

F/G verdicts are not per-headline-cell (own geometries) and enter the
written synthesis only, not the J cell gate. The DE/HI verdict files
are consumed read-only; J never recomputes them.

## J5. Record + verdict

Per cell: `{J_alg, J_useful, arms{...}, pheno_row{DE, HI}}`.
No UNDEFINED at J_alg level (defined on all 27 cells). Verdict files:
`data/vac0/j_results.json` (full records, small: no wavefunctions),
consuming `data/vac0/de_results.json` + `data/vac0/hi_summary.json`.

## J6. Firewall note

J_alg thresholds (1e-9) are set by float64 arithmetic, not by data.
J_useful is fixed as the DE∧HI conjunction before DE verdicts exist
(DE rerun pending at freeze time), so it cannot have been tuned to
the DE outcome pattern. No J gate was moved, added, or dropped
post-data because no J data exists.
