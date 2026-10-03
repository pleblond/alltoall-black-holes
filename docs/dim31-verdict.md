# DIM31 verdict: DIM31-GEOMETRIC (FROZEN record)

Verdict run 2026-10-03, code `ac91305`, seal
`data/dim31_seal.json` (blind `6defe9ed...`, freeze
`01455475...`, rev `ac91305`). Ordering per A4.3: freeze
committed (debt = 0) -> preseal anchor
(`data/dim31_preseal.json`, untracked) -> J3 grid mechanical
(18 tasks, GRID_DONE rc = 0) -> blind over all cells 0--16
(frozen D bars) -> seal -> `cmd_j3` (hash-verified, control
ladders match frozen workup to 1e-9). This file is the
sanctioned read; no post-verdict tuning is permitted (any
follow-up is a new campaign).

**Verdict: DIM31-GEOMETRIC, failures = 2**, both on the same
transfer-validation leg (tol_agree) at two of three sizes:

- `j3 transfer/direct gamma disagree j3-L16: 1.621 vs 1.743`
  (diff 0.122 > tol_agree 0.115, fails by 0.007)
- `j3 transfer/direct gamma disagree j3-L20: 1.600 vs 1.757`
  (diff 0.157 > tol_agree 0.115, fails by 0.042)

Per the frozen OPERATIONAL definition (A2.6: all gates pass),
the verdict is GEOMETRIC. It is not close to flipping: L20
fails by 0.042, beyond any margin discipline.

## What passed (everything else)

d_arr transfer medians (J3): L16 3.458, L20 3.552, L24 3.757
(n = 3 each). Absolute |med - 3| <= 0.873: PASS (margins
0.42/0.32/0.12). Identity vs cubic exact-L (3.079/3.392/
3.456) <= 0.416: PASS (margins 0.037/0.256/0.115 -- L16
close). Mismatch vs 2D refs (j2-L42 2.405, sq-L48 2.294) >
0.416 at every L: PASS (min margin 0.64). Direct-leg
validation medians (own gamma, ungated): 3.25/3.28/3.40 --
read 3 on both legs. Drift spread 0.206 (descriptive).

d*: 9/9 J3 sets read 3 (D headline, frozen bars); blind
claims agree with reveal audit 9/9; halfsplit test halves
read 3 on all 9. Charts: 9/9 read 3 (frozen eps bar
0.30).

Static (A3 banked predictions, all confirmed): L16 UNM
(empty regime window, unclaimed -- expected); L20 window
4..8 d = 2.932 (|bias| 0.068 <= 0.176); L24 window 4..11 d
= 3.135 (|bias| 0.135 <= 0.176); xi 2.117/2.156 inside the
0.20 xi-gate (dev 0.06/0.08). J3/cubic static identity to
SIX decimals (d, xi, alpha bitwise-equal at matched L):
the fiber-antisymmetric sector is invisible to the
shell-median profile at r >= 4, exactly the A3 mechanism.

Spread (L20+): L20 psi 1.007 / rho 2.015 PASS; L24 psi
0.904 / rho 1.809 PASS (3D windows); J descriptive (1.66/
1.58). Packet: L20 v 1.146 vs Bloch 1.182 PASS; L24 v
1.193 vs 1.182 PASS; reversal cos_pm -1.0 both. L16 has no
spread/packet legs (A4 scope) -- absent, as expected.

Gamma agreement at L24: 1.564 vs 1.669, diff 0.106 <= 0.115
PASS (margin 0.009 -- close).

## Reading of the failure (post-verdict discussion; filed)

tol_agree validates the TRANSFER assumption
(gamma_J3(L) = gamma_cb(L)), calibrated by cubic
leave-one-out self-consistency (max 0.088 -> tol 0.115).
J3's own wavefront gamma runs below cubic's: diffs 0.122 /
0.157 / 0.106 at L16/20/24 -- a violation beyond cubic
self-variation at the two smaller sizes, passing (barely)
at L24. The signature decays with L, consistent with a
finite-size contamination (e.g. fiber-antisymmetric
branches excited by point sources biasing arrival-mass
slopes at short radius, washing out as the symmetric
sector dominates) -- but that is a hypothesis for a
follow-up campaign, not a correction to this verdict.

Key separation: every DIMENSION-reading channel is
unanimous at 3 (transfer + direct d_arr, d*, chart,
static, spread-law, packet). What failed is a transfer
VALIDATION leg (gamma equality), not a dimension
measurement. The frozen definition nevertheless binds:
OPERATIONAL requires all gates. GEOMETRIC with the two
causes above is the recorded outcome.

## Bottom line

DIM-3-1 set out to repair DIM-3-0's falsified estimators
and test J3's operational dimension blind. The repaired
apparatus froze clean (debt = 0), called every banked
control and J3 static prediction correctly, and measured
dimension 3 on J3 through six independent channels -- but
the cubic gamma transfer it relies on disagrees with J3's
own gamma beyond the calibrated bar at L16/L20. By the
frozen all-gates rule: DIM31-GEOMETRIC (transfer-validation
failure, dimension channels unanimous at 3).
