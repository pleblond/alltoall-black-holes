# VAC-0F/G Addendum — Interference + tunnelling (FROZEN)

Committed before any VAC-0F/G beast run. Ports frozen SLIT/TUN apparatus.

## F1. VAC-0F cells (SLIT-0a + SLIT-1 headline; 0b/2 secondary; MZ LAW-level)

Barrier = bond removal only (node set fixed). Ports:

| cell | graph | xb | slits | mouths (σ=2, k=(0.3,0)) | xd | window | T* range |
|------|-------|----|-------|--------------------------|----|--------|----------|
| open-70x61 (regr) | open_grid 70x61 | 30 | A(22,23) B(37,38) | (31,22.5)/(31,37.5) σ=2 k=(1,0); source (12,30) σ=3 k=(1,0) | 54 | \|y-30\|≤16 | [0,60] |
| j2_L28 | j2_barrier | 12 | (8,20) | (13,8)/(13,20) | 20 | \|y-14\|≤12 | [0,20] |
| j2quot_L28 | torus interior line | 12 | (8,20) | (13,8)/(13,20) | 20 | \|y-14\|≤12 | [0,20] |
| square_n40 | torus interior line | 16 | (12,28) | (17,12)/(17,28) | 26 | \|y-20\|≤16 | [0,30] |
| tri_L28 | torus interior line | 12 | (8,20) | (13,8)/(13,20) | 20 | \|y-14\|≤12 | [0,20] |
| hex_L28 | torus interior line | 12 | (8,20) | (13,8)/(13,20) | 20 | \|y-14\|≤12 | [0,20] |
| j2swap8_s{0,1,2} | j2_barrier by labels | 12 | (8,20) | (13,8)/(13,20) | 20 | \|y-14\|≤12 | [0,20] |
| j2rewire_s{0,1,2} | j2_barrier by labels | 12 | (8,20) | (13,8)/(13,20) | 20 | \|y-14\|≤12 | [0,20] |

`dt = 0.1` everywhere. Interior-line rule (canonical port of `j2_barrier`):
cut every bond whose endpoint x-labels are exactly `{xb, xb+1}`, except
bonds at slit rows (all sheets/sectors pass). Detector: `detector_profile`
generic 2D (sum over sheets/none); rewires use `detector_profile_j2`
(labels kept). `T*` = argmax detector-line weight from the AB run (one
clock, SLIT rule). ring/RR: UNDEFINED (no transverse direction).

SLIT-0a prep: Loewdin pair + `superpose(phi)` on ONE `G_AB`; headline
`V(W) > 0.3, nmax(W) ≥ 3, rmsR > 0.2, L2(AB,incoh) > 0.05, lin < 1e-9`;
validity `corr < 0.05, detW > 0.5%, wallW < 5%, T* interior, norm 1e-8`.
SLIT-1: `φ ∈ {0,π/2,π,2π}`, center `I(π/2)/I(0) = 0.5±0.1`,
`I(π)/I(0) < 0.05`, periodicity `< 1e-9`, `L2(0,π) > 0.05`.
SLIT-0b (secondary, filed): source-driven `G_A/G_B/G_AB`, `Rmax > 1.4`,
`Rmin < 0.6`, `L2 > 0.05` + mirror/control gates.
SLIT-3 MZ (LAW-level, run once, not per-cell): len-14 corridor,
`w(π/2)/w(0) = 0.5±0.03`, `w(π)/w(0) < 0.02`, single-arm exact,
arm-scan ratio `> 3`.

VAC-0F cell verdict: PASS iff 0a-headline + 0a-validity + SLIT-1 all pass.
Regression: open-grid `V = 0.678` (±20%), J2 `V = 0.853` (±20%),
MZ banked numbers (exact gates above).

## G1. VAC-0G cells (TUN-1 + width law + strength law headline; TUN-4 secondary)

Wall = y-bond removal in wall columns (TUN law, no onsite terms).
Geometry (all 2D families): `L = 160`, `x0 = 8`, `wall_lo = 56`,
`σ = (6,8)`, `dt = 0.1`. Packets from `E0` via per-family band
(frozen formulas §G2). `T_sep` = locked formula fed by G0-banked
free `v_in` per (family, E0) (LB=0 runs first, TUN-0 pattern).

| family | lead band | wall band | E0 width (LB∈{0..8}) | E0 strength (LB=4) | control |
|--------|-----------|-----------|----------------------|--------------------|---------|
| j2 (+regr) | [-8,8] | [-4,4] | -5.5 | {-5,-6,-6.5,-7} | -3.0 |
| j2quot/square | [-4,4] | [-2,2] | -3.0 | {-2.5,-3,-3.5} | -1.5 |
| tri | [-6,3] | [-2,2] | -4.0 | {-3,-4,-5} | -1.5 |
| hex | [-3,3] | [-2,2] | -2.5 | {-2.2,-2.5,-2.8} | -1.5 |
| j2swap8_s{0,1,2} | ≈J2 | Gershgorin filed | -5.5 | {-5,-6} | -3.0 |
| j2rewire_s{0,1,2} | ≈J2 | Gershgorin filed | -5.5 | {-5,-6} | -3.0 |

ring/RR: UNDEFINED (no canonical finite-transmission geometry-only
barrier in 1D / without columns).

## G2. Per-family band formulas (frozen, pre-data theory)

- square/j2quot: `E = -2(cos kx + cos ky)`; `kx0 = acos(-E0/2 - 1)`;
  `vx = 2 sin kx0`. Transfer-matrix port: per-ky 1D problem
  (`eps_lead = -2 cos ky`, `t = 1`, barrier `[0]*LB`) averaged over the
  packet k-Gaussian (same code pattern as `packet_T_pred`, family
  constants swapped — implemented in the VAC runner, J2 original untouched).
- tri: `E = -2(cos kx + cos ky + cos(kx+ky))`; at `ky = 0`:
  `kx0 = acos(-E0/4 - 0.5)`; `vx = 4 sin kx0`. No analytic-T port
  (complex-hopping reduction); width law uses monotonicity + κ (§G3).
- hex: brick-wall Bloch `f = 1 + e^{-i(k1+k2)} + e^{-ik2}`,
  `E = -|f|`; `kx0` solved numerically pre-run (filed); `vx` numeric.
  No analytic-T port (same reason as tri).
- j2: banked `kx_for_energy` / `packet_T_pred` (regression path).
- Wall κ (all families): wall = plain 1D chain ⇒
  `κ = arccosh(|E0| / 2)` (square/tri/hex) or `/4J` (J2, banked).

## G3. Verdicts (ported TUN thresholds)

- TUN-1 spectral: wall band edge `< |E0|` pre-dynamics (exact; J2/square/
  tri/hex analytic; rewires measured-Gershgorin — if violated, UNDEFINED).
- Evanescent interior: `interior_slope` monotone-decay + `interior_asym`
  entry>exit (TUN readouts, generic column profile) + κ fit within 20%
  of §G2 prediction.
- Finite-T: `T > 1e-6` all LB cells + `T+R+B = 1` accounting.
- Width law: J2 `T` ratios vs `T_pred` ≤ 5% (regression); square ≤ 15%;
  tri/hex monotone decrease + `T(LB=8) < T(LB=1)/2`.
- Strength law: `T(E0)` increases toward the control + control transmits
  (`T > 0.5`, propagating check).
- PASS iff all five. TUN-4 resonance (secondary): J2 + square double-wall
  only (ports clean); tri/hex skipped (box-mode theory not ported — filed).
