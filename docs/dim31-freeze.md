# DIM31 controls freeze (FROZEN pre-J3)

Status: frozen 2026-10-03. Full control battery (cells 0--12, 16;
sets 0/1/2; pot1 incl. small-gap deltas; spread + packet legs).
Freeze record `data/dim31_freeze.json`: **debt = 0**, dropped = 2
(W/C d* legs: bars unfreezable, filed descriptive-only per A2.2).
No J3 data exists (J3 grid not run). All tolerances mechanical
1.3x rules (A2.6); values below are the frozen record.

Seal binding: blind
`65f5f26c12a04f86e1619ff26b8805fab4c72acdeb4224e4f13ca3189b18ec4d`
(`data/dim31_blind_controls.json`, cells 0--12+16, ladder only),
freeze `01455475...` (`data/dim31_freeze.json`), code at
`023a1f0`.

## Frozen tolerances (mechanical)

- tol_regress 0.873 = 1.3 x max control |bias| 0.672 (cb-L12)
- tol_identity 0.416 = 1.3 x max cubic transfer scatter 0.320
  (cb-L20); J3 identity + mismatch gates only (A2.6c)
- tol_agree 0.115 = 1.3 x LOO transfer error 0.088
- tol_stat 0.176 = 1.3 x max static |bias| 0.135 (cb-L24 3.135)
- tol_prange 0.15 (frozen constant); drift descriptive (A2.6)

## d* (headline D; bars frozen)

Bars: bar_1 0.0183, bar_2 0.0284, bar_3 0.0569.
Claims: 33/33 non-expander control sets correct
(ring 1, square/J2 2, cubic + bcb 3, all sizes incl. cb-L24),
9/9 expander refusals. W bar_2 unfreezable (2D max 0.0694 vs
3D/ex min 0.0544); C bar_1 unfreezable (ring max 0.1154 vs
others min 0.1226) -- both legs filed, never gated.

## d_arr (W headline; transfer instrument)

Transfer gamma-bar (ladder mean, exact L): L12 1.666, L16
1.743, L20 1.757, L24 1.669 (n = 12). T2' level spread 0.162
<= 0.20 PASS; T1 L-spread 0.180 descriptive (pooled unused).

Cubic transfer medians (J3 identity partners): L12 2.271 +-
0.080, L16 3.079 +- 0.202, L20 3.392 +- 0.320, L24 3.456 +-
0.305. 2D mismatch refs: j2-L42 2.405, sq-L48 2.294.

Control absolute gate (|med - dim| <= 0.873): medians ring
1.206/1.173, sq 2.288/2.294, j2 2.316/2.405, cb
2.328/3.127/3.392/3.463 -- all PASS. Direct scatter filed
(0.010--0.501), never gated (A2.6c).

## Charts (reveal-side, frozen bars)

2D: 12/12 pass (sq + j2, all sets). 3D: 14/15 pass (cb all
12; bcb-L12 s0/s1 pass, s2 eps 0.31 UNMEAS filed -- bcb is
an ungated refusal control). Ring/ex: no apparatus (filed).

## Static (A3 regime apparatus, xi* = 2.0)

| tag | window | d | |bias| |
|---|---|---|---|
| rg-N256 | 2..62 | 0.999 | 0.001 |
| rg-N512 | 2..126 | 0.999 | 0.001 |
| sq-L32 | 4..14 | 2.041 | 0.041 |
| sq-L48 | 4..22 | 1.905 | 0.095 |
| j2-L28 | 4..12 | 2.011 | 0.011 |
| j2-L42 | 4..19 | 1.947 | 0.053 |
| cb-L20 | 4..8 | 2.932 | 0.068 |
| cb-L24 | 4..11 | 3.135 | 0.135 |

Rule-derived UNM (empty regime window): cb-L12, cb-L16,
bcb-L12. Expander no-geometry refusals: ex-N1024-s0,
ex-N3456-s0 (s1 tag unmeasured -- no pot1 leg, filed).
Gate |d - dim| <= 0.176: all measured PASS.

## Spread / packet (descriptive + gated legs)

cb-L20: psi 0.989 (PASS, theory 1), rho 1.978 (PASS, theory
2), J 1.654 descriptive (no J-law, A2.5). Packet: v 0.584 vs
Bloch 0.591 PASS (cos_pm -1.0).

## J3 verdict criteria (frozen; see prereg + A2.6 + A3)

OPERATIONAL iff identity (3 L) + absolute + mismatch + d*
D set-replication + tol_agree + spread psi/rho + packet +
chart + static all pass; else GEOMETRIC with failures
listed. J3 static predictions (A3): L16 UNM; L20 (4..8) and
L24 (4..11) read |d - 3| <= tol_stat 0.176 (xi-gate 0.20
inside dim.ok).
