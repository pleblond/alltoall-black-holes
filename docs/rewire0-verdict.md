# REWIRE0-VERDICT — REWIRE0-CLASS (vacuous) / headline REWIRE0-DEGENERATE

**Branch** `cursor/rewire-0-acfd` (base main tail `51e0bd6`).
**Beast campaign** 2026-10-03 (~02:27–03:20 UTC, 16.54.88.181):
20/20 tasks CAMPAIGN-DONE via `~/rewire0_launch.sh`
(xargs `-P 12`, nice, OMP threads 1, `PYTHONPATH` to the checkout).
Beast ran pushed-commit-`124d927`-identical content (md5-verified;
a one-line test-file patch over `ea44527` during a transient GitHub
auth outage, applied before any campaign data, byte-identical to the
pushed fix). Records `data/rewire0/<task>.json` (20 files, 108 rows)
+ `data/rewire0/verdict.json` banked. Analyzer
`scripts/rewire0_analyze.py` per PREREG (no post-data changes).
Full suite on beast (see §9).

## 1. Gates (all pass, hard_ok=True)

| Gate | Result |
|---|---|
| H-INST-complete | 20/20 tasks |
| H-ledger-exact | 108 rows, max \|dE − formula\| = 2.4e-15 |
| H-quotient | R×U1 invariant (ring6 n_phys = 12) |
| H-determinism | repeat bit-identical |
| H-hist-br1 | closed 7665989632 == banked |
| H-hist-blind | square 0 / metropolis 0 / triangle 5 accepts (L4) |
| M-head-counts | 24 states, n_phys = 9792 everywhere |
| M-head-principles | CONS/LEDG/CONS_LEDG/SPAN/HID DEGENERATE 24/24; MOTIF ABSENT 24/24 |
| M-covariance | CONS/SPAN/MOTIF/HID 0 viol; LEDG/CONS_LEDG 1389 (fp, §5) |
| M-vacuum | 9 states, UNIQUE fraction 0.000 |
| M-excitation | 15 states, UNIQUE fraction 0.000 |
| M-dist | 7/24 states descriptively distinguishing |
| M-scale-j2L8/j2L28 | 11291 / 6756 per state (anchored), same pattern |
| M-tiny | 10 classes filed |

## 2. Headline census (J2 L4 exhaustive, 24 states)

n_phys = 9792 on every headline state (psi-independent enormity at
N = 32 — blind-neutral enormity reproduced in the swap class).
Per principle (survivors of 9792):

- CONS (d_ncomp == 0): 9792 everywhere (no rewire disconnects J2-L4;
  connectivity vacuous here) → DEGENERATE 24/24.
- SPAN (span-quiescent): 8000 everywhere (graph-only, field-free) →
  DEGENERATE 24/24.
- MOTIF (motif-neutral): 0 everywhere (every swap changes touched
  motif counts on J2-L4) → ABSENT 24/24.
- LEDG (dE == 0): 9792 (VPLUS/ZERO/point_amp-on-VPLUS, vacuous-all-
  neutral) down to 70 (exc-VMINUS-packet); VPI 2560, VMINUS 7328,
  textures ~1220, packets 70–208 → DEGENERATE 24/24 (min 70 ≫ 1).
- HID (hres preserved): 9792 (VPLUS/ZERO, uniform-eigenvector
  theorem: uniform psi is E = −8 for EVERY 8-regular rewiring) down
  to 16 (exc-VMINUS-packet) → DEGENERATE 24/24.
- CONS_LEDG: conjunction, DEGENERATE 24/24.

**Zero UNIQUE on any headline state by any principle.**
Vacuum UNIQUE fraction 0.000 (9/9), excitation 0.000 (15/15):
local field information (packets, patches, phase/amplitude kicks,
hidden-sector kicks, textures) fragments neutral sets (9792 → 70)
but never isolates exactly one outcome — and at L28 the packet
excitation overshoots to ABSENT (LEDG 0/6756: generic fields erase
exact ties rather than resolving them).

## 3. Mechanical verdict: REWIRE0-CLASS (vacuous trivial class)

The frozen ladder returns REWIRE0-CLASS via CONS/SPAN/MOTIF UNIQUE
on all 7 states of `tiny-path4`. **This CLASS is vacuous:** path4
has n_phys = 1 (a single admissible rewire). A "selection" among
one candidate is automatic, not discriminating — every
non-excluding principle is trivially UNIQUE there (33/42 cells
UNIQUE, including all six principles on zero/uniform/bonding/spike
fields). No discrimination occurs; no rule is evidenced.

Substance: **no genuine (discriminating) unique selection exists on
any state with more than one admissible rewire** (24/24 headline +
all 7-state L8/L28 anchors + every tiny state with n_phys > 1:
zero UNIQUE by any principle except two sporadic single cells,
§6). The campaign's headline question — n_constrained == 1 on a
nontrivial class — answers NO. Headline rung: REWIRE0-DEGENERATE
(multiple physical rewires survive every earned exact constraint;
earned constraints beyond quotient are vacuous identities for
rewire: dQ = dD2 = 0, dS = 0).

## 4. Scale controls (filed, same pattern)

- J2 L8 anchored (16 primaries, 7 states): n_phys = 11291/state;
  all principles DEGENERATE except MOTIF ABSENT; zero UNIQUE.
- J2 L28 anchored (8 primaries, 7 states): n_phys = 6756/state;
  same pattern; exc-VPLUS-packet LEDG/HID ABSENT (exact ties
  erased at scale); texture LEDG 385, HID 63 (still DEGENERATE).
Degeneracy persists from N = 32 to N = 1568.

## 5. Covariance (filed; ladder-remote)

Integer-exact principles (CONS/SPAN/MOTIF) are orbit-closed with
zero violations (data label-free by construction). HID likewise
clean (matches on exactly-representable residuals). LEDG and
CONS_LEDG show 1389 closure violations on the headline: exact
`dE == 0.0` compares fp sums whose summation order differs across
Aut-images (irrational 1/√N bond values; cancellation-prone
differences). **Exact-equality energy selection is fp-summation-
order fragile at ulp** — filed as a representation-robustness
null for ledger-exact selection (no tolerance introduced:
that would be a post-data threshold; firewall held).
Covariance is moot for the verdict (no UNIQUE on headline to
qualify); the orbit theorem stands (symmetric states forbid
covariant uniqueness; max orbit 7 on the 6-sample).

## 6. Tiny classes + sporadic cells (filed)

- Empty (n_phys = 0): triangle, star4, diamond, k4minus (4
  distinct-endpoint pairs impossible) → all ABSENT.
- path4 (n_phys = 1): vacuous UNIQUEs (§3).
- ring6/square/path6/tree7/er8s3 (n_phys 2–32): all
  DEGENERATE/ABSENT except two isolated HID UNIQUE cells
  (er8s3/current 1-of-32, path6/current 1-of-9; both covariant,
  trivial stabilizer) — 2/420 tiny cells (0.5%), non-systematic,
  no class triggered. Filed as chance tie-breaking curiosities.

## 7. DIST census (descriptive, not selective)

7/24 headline states have an earned quantity taking a unique value
(circle@π/3, both textures, 4 excitations) — symmetry-breaking
fields create descriptive distinguishability. No frozen principle
converts it to selection (all DEGENERATE/ABSENT there). Per the
firewall, no post-hoc score/threshold was constructed from these;
they are reported, not promoted.

## 8. Historical nulls (reproduced)

- BR-1 M1 enormity: closed form E·(N(N−1)/2 − E) == banked
  7665989632 exactly (gate).
- Blind-U on J2: square/metropolis(T0.25) FROZEN (0 accepts),
  triangle DESTRUCTIVE (5 accepts/5 steps L4) — banked C4-optimum
  mechanism cited.
- REWIRE-0 analog: local-swap enormity (9792 at N = 32;
  6756 per 8-edge anchor at N = 1568) with survivor counts in the
  thousands (CONS/SPAN) or exactly-zero (MOTIF) — blind-neutral
  moves are enormous and either vacuous or absent, never uniquely
  selective. SPAN/MOTIF controls confirm no coincidence with
  falsified repair/hill-climb forms yields uniqueness (exact-
  equality vs strict-greater distinction filed; neither selects).

## 9. Full suite + pins (beast)

- `tests/test_rewire0.py`: 32/32 pins green on beast.
- Full suite on beast (`pytest -n 60`, pyproject addopts skips
  `tests/test_weighted.py`): **1876 passed, 2 skipped, 0 failed**
  in 65 s (`~/rewire0-suite.log`).

## 10. Bottom line (boxed)

No already-earned local, covariant, zero-parameter rule uniquely
selects a degree-preserving rewire on any nontrivial state:
24/24 headline states DEGENERATE-or-ABSENT under all six exact
principles (vacuum and excited alike), scale-persistent to L28,
with descriptive distinguishability (7/24) never converting to
selection and energy-exact selection fp-fragile at ulp. The
mechanical ladder reads REWIRE0-CLASS on a vacuous single-outcome
toy class; substantively the campaign is a null — rewiring admits
no deterministic exact-physics selector. MEASURE0-DEBT, EVENT-RATE
debt, and BR27-NO-MODE stand unreduced. No scores, thresholds,
rates, or measures were introduced; no weak-interaction
identification was made.
