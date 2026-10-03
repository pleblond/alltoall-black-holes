# EVENT0-VERDICT — EVENT0-EQUIV (DATA)

Beast campaign 2026-10-03 (463 tasks, 96-way, xargs/nice/OMP=1) +
frozen analyzer: **EVENT0-EQUIV 33/33 :: 61 nontrivial same-$N$ orbits;
zero firing implications**. Records `data/event0/*.json` (463) +
`verdict.json`. No amendments: the frozen apparatus ran first-try green
(one beast-local arm-script quoting fault, fixed before any data; no
campaign file touched).

## Headline

Fixed-$G$ unitary flow never breaks the earned representation: all 426
rungs of all 71 trajectories stay inside $\mathcal A_G$
($t_*=+\infty$ everywhere; zero C-failures), $Q$ is bitwise frozen on
every stored rung, and current-$M$ reversal stays exact. But structural
uniqueness fails on small symmetric graphs: 61 exact nontrivial
rewire-equivalence orbits exist (symmetric-$\psi$ loci where a different
labeled edge set describes the same physical state mod $R\times U(1)$),
while the J2 headline is ruled out graph-first (zero cospectral rewire
neighbors out of 9792 per state, $\psi$-independently). The stability
audit is clean (zero implications), and 2493 exact time-crossing edges
are filed as TRIGGER-0-consistent conditions. Nothing forces change:
EQUIV, not FORCED.

## Gates (33/33 green)

- counts: 349/12/10/6/71/8/6/1 exact, no drops.
- A-store/A-merge/A-split/A-rewire/A-trigger: all green. 349 STORE-0
  digests reproduce (det/info/R-formula/roundtrip/closure/cov/loc;
  fiber rows exact); 12 MERGE cells (det+ledger+cov); 10 SPLIT cells
  (roundtrip+minimality); 6 REWIRE states (ledger-exact, max err 0.0 on
  tiny); $t{=}0$ census bitwise recomputed on 12 sample trajs.
- Q-frozen/Q-reversal/Q-attrib/Q-current: QDYN mechanics re-derived on
  all 12 STORED trajs (Q bitwise frozen; V5/V6/V7 every rung;
  attribution closure $<10^{-12}$; current inversion $<10^{-9}$).
- C-valid: 426/426 rungs valid, $t_*=+\infty$ everywhere.
  D-neighbors filed-complete; D-search vacuous (no failures).
- E-equiv/F-perclass/F-orbits: search complete on all 71 trajs
  (screen + exact iso on survivors + exact per-rung compat; tiny
  enumeration recomputed); Aut redundancy removed (exact on tiny,
  6-perm sample on J2, filed).
- G-audit: BR27-NO-MODE + MERGE-0J no-rule + MEASURE0-DEBT +
  TRIGGER0 zero implications + pinned QDYN0B-EVENT-LOCAL all hold;
  implication count 0.
- H-cross: census complete (2493 crossing edges, 7830 pred-edge flips;
  graph preds BRIDGE/C0/C_POS never flip, as G is fixed).
- I-static: zero far flips at $t{=}0$ on all 8 LOC legs (exact
  support-disjoint theorem). I-causal filed: L28 packet 0 beyond-cone
  flips (5872/4976/1936 beyond edges at T=0.5/1/2); L4 packet vacuous
  (cone covers the graph).
- J-hidden: 3 matched pairs filed (near flips 16/12/21, far flips 0;
  crossing sets 72/72, 72/72, 72/76; EQUIV 0/0 everywhere).
- K-vacuum: 8+ JOINT legs valid every rung, never forced-active.
  K-zerocert: all 28 certified (eigen $+$ zero) legs crossing-free.
- L-cycle: forth-back return $\le 2.2\times10^{-13}$ + inverse exactness
  on all 6 legs. X-firewall: scan clean (0 hits) + live positive
  control + zero fitted params. S-report: exactly one verdict.

## EQUIV anatomy (61 orbits, 15 legs)

| legs | orbits | mechanism |
|---|---|---|
| ring-8 uniform/stagger0/zero/spike0 | 3/3/3/3 (cospec 20/32) | parallel re-pairings preserve the $C_8$ class; symmetric $\psi$ compatible |
| ring-8 antibonding | 1 (cospec 20) | alternating pattern compatible with half-turn-class swaps |
| path-8 uniform/zero/stagger0/spike0 | 8 each (cospec 14/23) | path-class-preserving swaps; spike via node-0-fixing isos |
| handbuilt uniform/zero | 2 each (cospec 3/18) | iso-preserving swaps on the irregular graph |
| handbuilt INT-twospike | 2 | two-spike pattern compatible at $\ge 1$ rung |
| stored ring-8/path-8/handbuilt uniform | 2/6/2 | post-merge graphs inherit iso-preserving swaps |
| J2-L4 all 39 legs (bare+stored) | 0 (cospec 0/9792) | spectral screen rules out every rewire neighbor |
| J2-L28 (anchored 64) | 0 | no cospectral anchored neighbor |
| triangle all legs | 0 (0 rewires) | no admissible swap exists on $N{=}3$ |

Cross-$N$ legs: dimension obstruction filed ($N\ne N'$ forbids direct
mod-quotient identity); the earned cross-$N$ equivalence is the STORE
roundtrip itself, exact on every stored rung (coexistence without
forcing, never a surface).

## Crossing census (conditions, not triggers)

2493 edges flip $\ge 1$ predicate along flow (witness: handbuilt
random777 edge 0 B_POS at T=0.5). Per-predicate edge counts: J_ZERO
2074, UNIFORM_EDGE 991, L_NEG 646, ANNIHIL 562, CROSS_ZERO 431,
LEDG_ZERO 430, CELL_ANTI 424, BJ_ZERO/ZERO_MIN 404, FAVORABLE 358,
B_POS 342, B_NEG 310, L_POS 388, B_ZERO 62, BAL_R1 3, BAL_R2 1,
BRIDGE/C0/C_POS/CELL_SYM/HID_ACTIVE 0. Filed mechanism: the J2 spike
front is exactly $P_+$-symmetric (flat-band localization of the
antisymmetric sector), so CELL_SYM never flips while CELL_ANTI does
(verified by independent rung recompute, masks bitwise identical).

## Vacuum control (28 certified zero-event legs)

All JOINT vacua (VPLUS/VPI/VMINUS/VSTAG/CIRCLE_pi6), both textures, all
five hidden textures, staggers, and zero states on J2-L4/L28, plus ring
uniform/stagger/current/antibonding/zero, triangle uniform/current/zero,
handbuilt zero, and stored-L4-H:dipole/zero, are $H$-eigenstates (or
exact-zero) with phase-only flow and zero crossings. Eigenstate legs
with EQUIV orbits (ring-8 uniform/stagger0/antibonding) carry their
equivalences on every rung (compat is phase-invariant).

## Firewall

No bar was tuned, no predicate invented, no score, rate, clock, or state
variable added; no virtual description was adopted (nothing fired). The
61 orbits are equivalence surfaces, not triggers: each is exactly
evaluable, and none implies firing. No EVENT-1 shopping follows.

## Suite

Full test suite on beast (192-way, tests/test_weighted.py skipped):
2319 passed, 2 skipped, 3 failed in 71s. The 3 failures
(test_emergent_dim::test_weighted_diffusion_partially_untraps,
test_potential::test_aperture_keeps_gradient,
test_tunnel::test_transfer_matrix_unitarity_and_limits) reproduce
identically on unmodified main in the same beast environment
(numpy 2.5.3/scipy 1.18.1/nx 3.7) and pass locally: pre-existing
environment-sensitive failures, unrelated to EVENT-0 (which modifies
no banked module). All 28 EVENT-0 pins pass on beast.
