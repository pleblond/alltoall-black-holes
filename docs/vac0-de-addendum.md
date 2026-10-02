# VAC-0D/E Addendum — Ballistic propagation + coherence-direction (FROZEN)

Committed before the VAC-0D/E beast campaign. Ports the frozen P1.1/POT-0
apparatus by master-prereg port rules P2.1/P2.2.

## D1. Cells + prep (all frozen)

2D tori: `k = (0.3, 0)` (POT-0 headline value), `sigma = 4`, `r0 = (L/4, L/2)`,
`dt = 0.1`. Ring: `k = ±0.5` (P1.1a value), `sigma = 4`, `r0 = N/4`, `dt = 0.1`.

| cell | T | wrap budget: v_pred*T vs L/2 (or N/2) |
|------|---|----------------------------------------|
| j2_L28 | 10 | 1.18*10 = 11.8 < 14 ✓ |
| j2_L20 | 6 | 1.18*6 = 7.1 < 10 ✓ |
| j2quot_L28 / square_n28 | 10 / 16 | 0.59*10 = 5.9 < 14 ✓ / 0.59*16 = 9.4 < 14 ✓ |
| j2quot_L20 | 10 | 5.9 < 10 ✓ |
| square_n40 | 24 | 0.59*24 = 14.2 < 20 ✓ |
| tri_L28 / tri_L40 | 10 / 14 | 1.18*10 = 11.8 < 14 ✓ / 1.18*14 = 16.5 < 20 ✓ |
| hex_L28 / hex_L40 | 10 / 16 | ~0.59 (brick-wall Bloch, §D4) |
| ring_N400 / ring_N1600 | 120 / 480 | 0.96*120 = 115 < 200 ✓ / 0.96*480 = 460 < 800 ✓ |
| j2swap8 / j2rewire (all seeds) | 10 | J2 budget (labels kept) |

v_pred: square/ring `2 sin k` (exact); J2 `tunnel.j2_group_velocity`
(banked); tri `4 sin k` (axial Bloch, `E = -2[cos kx + cos ky +
cos(kx+ky)]`, `vx = 2[sin kx + sin(kx+ky)]`, at ky=0); hex §D4.

## D2. Arms per cell (raw = headline, POT-0 faithful)

- `pkt±`: raw Gaussian `±k`, full trace readouts (D, alpha, Cv, R2, v).
- `pur±`: branch-purified onto P_+ (file retained weight; splitting diagnosis).
- `grad`: c-grid 0..1 step 0.1, `k_eff = c*k` (envelope-exact family).
- `deph`: dephasing family c-grid, seed 0 (literal coherence strength).
- `scr`: phase scramble seeds {0,1,2}; `rest`: fresh clean re-prep.
- `null`: 20 random-phase states (prep-only D_null calibration).
- `ap`: aperture R-grid (2,3,4,6,8,12,None) (POT-0E).
- Branch anatomy: `w0`, `w±`, mixing for every ±k prep (P1.1b regression).

Ring ports: 1D flux D (`J_net = Σ J_e dx`, `S = Σ|J_e|`, `D = |J_net|/S`),
1D FFT coherence, interval aperture. 2D ports: native `edge_table`,
`flux_decomposition`, grid-FFT coherence (same peak-fraction formula as
`spectral_coherence` WITHOUT the sheet sum — canonical port, frozen here).

RR cells: headline UNDEFINED (no momentum sector / coordinates); intrinsic
secondary filed (shell peak-time linear fit + IPR trace + return prob).

## D3. Verdicts (ported POT0-PREREG thresholds, same numbers)

VAC-0D cell (from `pkt±` + `grad c=0` as source):
B_D `mean_D > 0.5`; B_sep `(pkt-src) > 0.4 and ratio > 10`;
B_alpha `alpha > 1.3`; B_cv `cv > 0.5`; B_rev `cos < -0.95, D-match 10%`;
B_r2 `R2 > 0.99 both`. PASS iff all six.
VAC-0E cell: C_grad_ratio `> 10`; C_grad_v `spearman > 0.7, c0 < 5% max`;
C_noise (deph family monotone, same test as POT-0);
D_scr_D `< 0.15 pkt`; D_scr_C `< 0.5 pkt`; D_rest match 15%;
D_corr `spearman(pool) > 0.5`; E_corr/E_small/E_width (aperture, POT-0E).
PASS iff all C + all D + all E.

## D4. Hex band note (pre-data theory, why `pur±` exists)

Brick-wall Bravais lattice `t1 = (1,1)`, `t2 = (1,-1)`, two-site basis:
`f(k) = 1 + e^{-i(k1+k2)} + e^{-ik2}`, bands `E = ∓|f|`. At axial
`k = (0.3, 0)`: `|f| ≈ 2.91`, `vx ≈ +0.59` (lower band). A raw packet
projects on BOTH bands (`±v`), so the raw arm may split (R2 gate
catches it honestly); the purified arm tests single-band flight.
Same logic covers any bipartite cell; non-bipartite cells (tri,
rewires) have no chiral symmetry — purification there is spectral-half,
filed with the same code path.

## D5. Regression arm (C1)

- `j2_L28 pkt±` must reproduce POT-0 `pkt`/`pktm` (`mean_D`, `alpha`,
  `v`, prep `C`) within 15% (same code path, same params — should be
  near-exact; 15% allows the record's T-window edge conventions).
- `ring_N400` must reproduce P1.1a (`v = ±0.9583`, `alpha = 2.00`) within 2%.
- Extra non-battery cell `square_n30` with P1.1a params replicates
  `v ≈ 0.966`, `alpha ≈ 2.05` within 5%.
- `j2_L28` branch anatomy must reproduce P1.1b (`w0 = 0`, mixing `< 1e-6`).
