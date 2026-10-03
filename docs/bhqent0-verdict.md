# BHQENT0-VERDICT (filed post-data; prereg frozen in `docs/bhqent0-prereg.md`)

Campaign: BH-Q-ENT-0 — Boundary Scaling of Exterior-Blind Store Information.
Verdict: **BHQENT0-UNCLASSIFIED** (34/34 gates green, controls green,
blind Q exists somewhere, no frozen scaling law passes).
Records: `data/bhqent0/` (74 task records + `verdict.json`).
Branch: `cursor/bh-q-ent-0-9465` (based on main tail `aaa7aed`).
Suite: 2424 passed / 2 skipped / 5 failed on beast2 (`-n 192`,
`tests/test_weighted.py` skipped per policy); 4 failures pre-existing
(branch modifies no pre-existing file), 1 BHQENT0 pin mis-designed
pre-data and corrected (synthetic rows only; gates/bars untouched).

## 1. Headline scaling (joint D_Q^blind, VPLUS)

| family | D_joint | law within family |
|---|---|---|
| Paths P2..P8 (b=2) | 0,0,0,0,0,0,0 | joint-visible, flat |
| Stars S3_2,S4_3,S6_4,S8_6,S3_3,S5_3 | 4,6,10,14,4,8 (=2n-4, rank 2) | volume-like |
| J2 disks J2L6r1,J2L8r2 (J2L4edge 0) | 18 (=n), 42 (=n) | volume-like |
| Squares SQL4dimer,SQL4r1,SQL6r1 | 0,0,0 | joint-visible, flat |
| Static-only (rho) everywhere | 2N_Q exact | volume, exact |

Matched pairs: matched-b (P4,P6,P8) flat 0 while (S4_3,S5_3) grows 6->8;
matched-n (P4,S3_3) 0 vs 4, (P5,S4_3) 0 vs 6, (P6,S5_3) 0 vs 8;
matched-both (P4,S3_2) 0 vs 4. Topology, not (n,b), controls joint
blindness. Factor-two OK: N_split == 0 on the joint channel for all 19
specs (per-entry d_R,d_I jointly blind/visible; no split entries).

## 2. Law gates (frozen bars, no movement)

- boundary: R^2 = 0.681 < 0.70 bar -> FAIL (near-miss; squares at b=6,8
  with D=0 vs S8_6 at b=6 with D=14 break the fit).
- volume: R^2 = 0.888 < 0.90 bar -> FAIL (near-miss; flat path/square
  families vs volume-like star/J2 families).
- mixed (b log b): R^2 = 0.721 < 0.90 -> FAIL.
- mixed_dim: no boundary correlation + fixed-b growth 0 -> FAIL.
- blind_none: false (stars/J2 blind).
- quad F-test p = 0.75 (linear not rejected); second diffs filed.

Per the frozen ladder this routes to BHQENT0-UNCLASSIFIED, exactly the
pre-data prediction (topology-dependent blind dimensions, no universal
n/b law). The two near-misses are reported as-is; no bar was moved and
no post-data law was shopped (Z-firewall green, fitted params 0).

## 3. Controls and anatomy (all green)

- A-regressions: BH-ENT collapse consistency + C3 + C1/C2 on the BHQENT0
  battery; STORE roundtrip phys-match on all 19; SPLIT fiber d_cont = 2
  (affine complex line); SYM swap gauge; HIDDEN/QUOT far-blind sample.
- D-store: N_Q = n_R - 1 everywhere; 0 exterior entries.
- H-validate: every D>0 record has kernel dO < 1e-6 with local
  D > 1e-6 (e.g. S3_2: dO 8.8e-8, D_local 3.5e-4; J2L8r2: dO 4.0e-8);
  every D=0 record has sensitive-direction dO > 1e-5; static legs exact
  (d_static 0.0, match true).
- I-audit: D = 2N_Q - rank exact; C = naive - D filed per channel.
- M-anatomy: blind weight concentrated boundary-adjacent (stars/J2L6r1
  100%; J2L8r2 86% boundary-adjacent + 10% interface + 5% shallow).
- N-ancestry: every entry tracked with members/distances/step.
- O-invariance: asc == desc joint D on all 5 specs (incl. S3_2: 4 = 4).
- P-overlap (J2): J2L6r1 overlap (D18 vs 9 hidden dirs, cos 1.0 + 0.707
  + rest ~0); J2L8r2 overlap (D42 vs 21 hidden dirs); no double counting.
- Q-vacuum: VPI == VPLUS everywhere tested (paths/stars/J2L6r1/SQL);
  VMINUS on J2L6r1 gives D = 9 vs VPLUS 18 (background dependence filed,
  no interpretation attached).
- R-contrast: BH-ENT graph-leg POT visibility reproduced on all 3 specs
  (P4 pot_maxdiff 0.0678 matches banked BHENT0; J2L6r1 0.0020; SQL4r1
  0.0076) with STORE-leg pot_J_norm = 0.0 and full POT-blindness of the
  continuous store fiber (pot_D = 2N_Q) on the same regions.
- J-cover: single-entry alt covers all static-blind where tested
  (paths/stars/squares 100% blind+distinct of tested alts); J2 entries
  capped honestly (exact counts (3^d+1)/2 up to 2.4M, 200 tested each);
  log2 filed combinatorial-only (max 12.17 on J2L8r2). POT-blind cover
  alts exist on P4 (4) and J2L6r1 (1399), filed separately.
- T-audit: FIBER0-DEBT + MEASURE0 (35 gates) + STORE0 checked;
  measure_earned false, entropy_blocked true. No entropy reading exists.

## 4. Filed amendments (no bar/ladder/statistic change)

- Amendment 1 (performance bug, pre-verdict): `blind_covers_single`
  fully enumerated (3^d+1)/2 covers before applying the prereg cap-200
  slice, hanging the 3 J2 cover tasks (exact counts up to 2.4M). Fix:
  lazy capped enumeration (`undirected_predecessors_capped`) with the
  pinned exact count by formula when over cap; identical full
  enumeration under cap (cover_P2 payload bit-identical pre/post fix);
  X0-side static/POT legs hoisted per entry (same inputs/outputs);
  honest tested-alt counting. 2 new pins, all green.
- Amendment 2 (pin design, pre-verdict): `test_law_gates_branches`
  synthetic rows mis-isolated the volume and unclassified branches
  (correlated b; boundary-passing 4-point set). Rows redesigned to
  genuinely isolate each branch; gate function and bars untouched.

## 5. Interpretation (firewall binding)

BHQENT0-UNCLASSIFIED earns: exterior-blind continuous STORE dimension
exists and is topology-dependent (volume-like within stars/J2 disks,
zero on paths/squares), with the complex-d factor two resolved and no
universal boundary/volume/b-log-b law. No measure, no bits, no entropy,
no horizon reading. The near-miss fits (boundary 0.68, volume 0.89)
constrain future batteries; they change nothing about this verdict.
