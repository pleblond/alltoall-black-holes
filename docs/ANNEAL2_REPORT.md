# Blind vacuum-annealer survey ROUND 2 — report

**Branch:** `cursor/vacuum-anneal2-7d7b` (off round-1 `cursor/vacuum-anneal-813f`,
PR #51 DRAFT/unmerged) · **Prereg:** `docs/anneal2-prereg.md` (committed BEFORE
any round-2 survey compute; zero post-freeze amendments).
**Epistemic authority:** `docs/model.md` v0.4 + D10 (vacuum selection, proposed
OPEN in round-1 §7 — stays open, §7). Every number below is labelled
derived / fitted / assumed / exploratory / conjectured.
**Compute:** $0 (local VM CPU, 316 runs ≈ 2.08 h wall on 3 workers, inside the
~6 h cap; no drop-order trigger). No observatory data (pure computation).
Run health: 0 failed, 0 disqualified, 0 T0-fallbacks, 86 seed fallbacks
(ER LCC+attach at survey N, recorded per run), 56 fragile-eigsh (all H1/H2 —
the frozen spec-phase-limited qualifier, §1). All counts exploratory from
`results/anneal2/*.json`.

## 0. Rule-zero compliance (blindness)

- The V2 cost contains only graph-intrinsic terms (edge count, Laplacian
  spectrum, degree sequence, WL colors, 4-cycle and triangle counts). Static
  token audits (V1 set + `target`/`flat` cycle-smuggling guards) pass over
  the cost and loop modules including all V2 code; cost-never-imports-
  measurement enforced by test (70/70 anneal tests green, 34 V1 + 36 V2).
- `disqualified: false` on all 316 runs. No run targeted or constrained
  dimension, curvature, coordination, or large-world-ness at any point.
- The circular proposal's defects (dimension target, curvature penalty,
  large-world hard constraint, phantom ledger citations) remain absent by
  construction: none of those quantities is computable from inside the loop.

## 1. Method — M1 fixed and verified (delayed acceptance + kill-switch)

Cost `C2 = w_E·E/N + w_L·λ2/z̄ + w_R·CV(deg)² + w_S·WL/N − w_Q·n4/N +
w_T·n3/N`, grid H0–H11 (6/12 arms press away from trees: H2/H5/H6/H9/H10/H11,
frozen signs), survey N ∈ {1000, 2000} + N = 4000 spot, exact-P4 κ at 3
checkpoints, d_iso V2 shell estimator (r_min = 2, f_up = 0.5), α = 0.9995,
STEPS = {60k, 120k, 240k} (2× collapse-settling rule, §3.4), connectivity
hard, bridgeless ablated. Full spec: prereg §§1–8.

**M1 fix verified (round-1's procedure flaw does not recur):** per-proposal
Metropolis on the exact cheap cost (edge/reg/square/triangle, O(1)
incremental, telescoping-tested) + exact block verdicts on the expensive
residual every K_REFRESH = 100 accepted moves (reject → revert to the
block-start snapshot — INTENDED; see M1b below for the implementation flaw).
Kill-switch tripwire passes (H0/H1/H2/H4 pairwise-distinct, block A/R 18/28,
5/41, 45/1); survey-wide scan finds NO driver collapse in the discovery or
stability grids (0 bit-identical hid pairs over 288 runs). The spectral and
symmetry legs differentiate trajectories (median block-reject fractions
0.81/0.83/1.00 for H1/H2/H4 over runs with verdicts) — genuine drivers,
weakened by M1b, not void.

**Finding M1b (round-2 procedure flaw, first-class negative — reported, not
repaired, per round-1 precedent):** `_StateV2.restore` assigns snapshot
references instead of copies, so the first block rejection per accepted
boundary reverts correctly but subsequent mutations corrupt the anchor and
all FOLLOWING rejects-until-next-accept are silent no-ops (single-restore
unit test passed; the bug needs restore→mutate→restore to manifest — test
gap recorded for round 3). Quantified: median real-reject fraction 0.25
(H1) / 0.22 (H2) / 0.01 (H4/H11). The expensive legs steered at reduced
strength (symmetry legs barely vetoed — H4 ≈ H0 in outcomes, consistent);
accepts and cheap-exact dynamics are unaffected (snapshot() copies; cheap
terms never use verdicts). Scoping (frozen-rule compliant): kill-switch still
holds (steering proven nonzero — divergence + real vetoes); NO leg is void
(voiding requires bit-identical = zero steering, as round-1 M1). Verdict
impact: the 8 cheap-driven arms (H0/H3/H5/H6/H7/H8/H9/H10 — including every
square/triangle away-arm) ran at FULL strength (no verdicts involved);
H1/H2/H4/H11 outcomes carry an M1b qualifier (weakened legs). V-DISCOVERY
FAIL stands for the as-run dynamics with this stated scoping; V-CONSTRAINT
is unaffected (matched weakened-vs-weakened comparisons). Round 3 must fix
restore (copy-on-restore + double-restore regression test), re-freeze, and
re-run the expensive arms at full strength (§6).

**Phase limitation (frozen qualifier FIRES for H1/H2, descriptive):**
ARPACK 'SM' cannot resolve near-zero-clustered tree spectra at survey N
(pilot finding E2), so the spectral leg holds (rather than steers) once a
run collapses to trees: median hold fraction 0.59 (H1) / 0.64 (H2),
fragile-flagged 26/28 + 30/32 runs (> 50% → "spec-phase-limited" qualifier
per the frozen rule). H4/H11 hold fraction 0.00 (WL always exact). Early-
phase verdicts still differentiate all trajectories (kill-switch holds).

**Pilot finding E1 (V1 eigsh flaw, fixed pre-freeze):** k=2 'SM' can skip
λ1 = 0 and return {λ2, λ3} (open 20×10×20 grid read λ3 = 0.0979 instead of
λ2 = 0.0246 — silently wrong). V2 uses k=6 + zero detection + deterministic
starts, validated ≤ 2e-13 vs dense (9 families) and theory-exact on grids.
V1 λ2 values are suspect (recorded, unused); no V1 verdict rested on them.

**Frozen-config note (2 kill-switch groups, mechanism identified, no void):**
8/8 er-sparse ablation runs froze at 0 accepts (bridgeless × bridge-rich ER
start: every proposal preserves a bridge → all rejected; E/edit/T0 frozen).
H0/H1/H2 share bit-identical signatures in 2 configs (same cheap cost + zero
moves = trivially identical; H10's T0 differs → excluded). This is a
constraint × seed interaction, NOT cost-term cancellation: it carries no
driver information and is excluded from hid-driver comparisons (which never
used ablation configs); V-CONSTRAINT on/off pairs remain valid (freezing IS
the measured constraint effect on ER starts). No leg is voided: 314/316
configs diverge + unit tripwire + veto fractions prove genuine drivers.

## 2. Calibration (gate PASSES — d_iso verdicts are live)

Source: `results/anneal2/calibration.json` (all exploratory). The frozen
5-bar gate passes deterministically (zero seed variance on periodic
lattices) + the 4000 spot gate passes:

| gate control | d_iso | R² | bar [2,4] | margin |
|---|---|---|---|---|
| cubic-1000 | 3.42 | 0.99 | PASS | 0.33 |
| cubic-2000 | 3.06 | 0.99 | PASS | 0.69 |
| fcc-1000 | 3.26 | 0.98 | PASS | 0.49 |
| fcc-2000 | 3.12 | 0.98 | PASS | 0.63 |
| diamond-2000 | 3.56 | 0.99 | PASS | 0.19 |
| cubic-4000 (spot) | 3.09 | 0.99 | PASS | 0.66 |
| diamond-4000 (spot) | 2.98 | 0.98 | PASS | 0.73 |

References (below-range, pre-declared): diamond-1000 (4.24, 5-cell tiling),
fcc-4000 (4.11, few-shell transient at z = 12). Negatives: er-sparse/rr6
read ok=False at survey N (V2 specificity: nan, not V1's confident-wrong
d ≈ 6–12); path/balanced-tree controls out-of-bar (report §7 honest residual
risk stands: annealed-tree misread risk UNKNOWN from controls alone).

Reachability (§3.2 table re-verified in calibration): every bar passable at
every survey N (B1: cubic/fcc/diamond; B2: cubic/fcc κ = 0.000; B3:
cubic/diamond; B4: ALL lattices, bars {7.5, 10.0, 12.5}); cubic is a full
member at all N. Round-1's unreachable-B4 failure cannot recur.

## 3. Survey data (exploratory descriptives + frozen counts)

### 3.1 Discovery leg — 0/144 members, five attractor classes

Raw bar counts: B1 29/144, B2 10/144, B3 140/144, B4 144/144, member 0/144.
B1∩B2 = ∅ over all 144 discovery runs (round-1's anti-correlation
REPLICATED at survey N with a calibrated estimator and live gate).

Per-hid final medians (12 runs each: 2 starts × 2 N × 3 seeds):

| hid | κ_med | z_med | diam_med | d_med | attractor class |
|---|---|---|---|---|---|
| H0 | −0.28 | 2.00 | 120 | 2.08 | T bushy trees (E = N−1) |
| H1 | −0.28 | 2.00 | 106 | 1.87 | T bushy trees (spec-lo; phase-limited) |
| H2 | −0.29 | 2.00 | 110 | 2.18 | T bushy trees (spec-hi COLLAPSES anyway) |
| H3 | −0.05 | 2.00 | 339 | 1.51 | P path-trees (10/12 B2 — all discovery B2 passes live here) |
| H4 | −0.28 | 2.00 | 120 | 2.07 | T bushy trees (symmetry) |
| H5 | −0.43 | 3.37 | 23 | 7.60 | L loopy square-rich |
| H6 | −0.17 | 2.28 | 95 | 2.32 | NT near-trees (triangle-rewarded) |
| H7 | −0.28 | 2.00 | 99 | 2.12 | T bushy trees (trifree) |
| H8 | −0.64 | 2.96 | 14 | 14.17 | X near-3-regular expanders (V1 class-C analog) |
| H9 | −0.44 | 3.44 | 22 | 7.10 | L loopy square-rich |
| H10 | −0.21 | 3.10 | 42 | 5.51 | L loopy (reg+square tension) |
| H11 | −0.40 | 3.48 | 23 | 7.62 | L loopy (reg+sym+square) |

Twelve blind drivers → five attractor classes (T/P/NT/L/X), none
flat-3D-large-world: flat outputs are path-trees (H3: d_med = 1.51, all B2
passes live here); in-bar-d outputs are curved trees (κ ≈ −0.28) or
small-world transients (d_med 5.5–14.2, B1 passes are tail lottery). The
away-arms fail to escape: H2 (max-λ2) collapses to E = N−1 trees exactly
like H0; H5/H9/H10/H11 leave trees but land loopy-small-world (diam 22–42,
κ ≈ −0.2…−0.4), not flat-3D. B3 fails only 4/144 (H9/H10 densifiers past
z = 8 from ER starts). No z-target existed; selected z spans 2.0 (trees) →
2.1–2.7 (near-trees) → 2.9–3.0 (expanders) → 3.1–3.8 (loopy) (reported).

### 3.2 Stability leg — lattices are not fixed points (0/144 preserved)

Preservation (B1+B2+edit ≤ 0.5): 0/144. Edit-distance median 1.49, min 0.12.
The min-edit runs (H06-fcc, edit 0.12–0.13 — trimax preserves 88% of FCC
edges) read d = nan (small-world, ok=False), κ = −0.18, z = 12.7: the
closest approaches to preservation are dense-small-world, failing B1/B2/B3.
The single B1+B2 stability run (stab2-H03-diamond-N2000-s01, §3.5) has edit
1.50 (complete rewiring to a path-tree). Seeded lattices do not survive any
blind driver tested: the stability leg is a stability NEGATIVE with live
bars (not INCONCLUSIVE — the gate passes, so 0/144 is a measured zero).

### 3.3 N = 4000 spot — control-validated negative (0/12 members)

Spot gate passes (cubic/diamond-4000 full members, §2), runs use 240k steps:
H0/H2 → exact trees (E = 3999, z = 2.00, d = 1.4–2.2, κ ≈ −0.24…−0.33,
diam ~200) — the H2 away-pressure provably cannot prevent collapse at scale.
H10 is bistable by start (V1-G10 analog): from cubic → dense loopy
(E ≈ 12600, z ≈ 6.3, d ≈ 9.5, diam 13); from er-sparse → near-trees
(E ≈ 4475, z = 2.24, diam 323–447). 0/12 members at the only N above survey
range with a validated ruler. Cooling: H0-container settled; H10 drift
carried (§3.4).

### 3.4 Cooling state per arm (operating point demonstrated + qualified)

Mid→final |ΔE|/E medians (discovery): H0/H1/H2/H4/H7: 0.0%; H3: 0.1%;
H6: 1.9%; H8: 2.0%; H11: 1.4%; H5: 2.6% (max 46%); H9: 2.5% (max 66%);
H10: 4.8% (max 46%). Collapse arms (8/12, incl. both spec arms and reg)
are frozen solid — the operating point is DEMONSTRATED there. Tension arms
(H5/H9/H10/H11) carry the pre-registered under-cooling qualifier on their
negatives (a few runs still evolving at final). The 2×-settling rule (§3.1)
held for collapse dynamics; square/edge tension evolves slower (measured).

### 3.5 Members: five path-trees in stability/ablation legs (reported, no verdict weight)

| run | leg | d_iso | R² | κ | z | diam | E | edit |
|---|---|---|---|---|---|---|---|---|
| stab2-H03-diamond-N2000-s01 | stab | 2.53 | 0.77 | −0.042 | 2.00 | 342 | 1999 | 1.50 |
| abl2-H00-cubic-N1000-s01-bl | abl | 2.27 | 0.87 | −0.017 | 2.03 | 148 | 1013 | 1.34 |
| abl2-H01-cubic-N1000-s00-bl | abl | 2.34 | 0.91 | −0.036 | 2.04 | 142 | 1018 | 1.34 |
| abl2-H02-cubic-N1000-s00-bl | abl | 2.29 | 0.87 | −0.021 | 2.03 | 203 | 1015 | 1.34 |
| abl2-H02-cubic-N1000-s01-bl | abl | 2.42 | 0.90 | −0.040 | 2.04 | 134 | 1018 | 1.34 |

All five pass the FROZEN bars (reported, never hidden) and all five are
path-trees by exact graph properties (z ≈ 2, E ≈ N−1 + bridgeless extra,
diam 134–342 ≈ 7–17× control). None is a discovery member → zero verdict
weight under the frozen rules (V-DISCOVERY counts discovery-leg only). The
four ablation members form an H2–H0–H1 adjacent chain — under the discovery
grid that pattern would merit a "selected" claim; under the bridgeless
constraint it is a constraint-drive result (§3.6), and it flags B1-bar
permissiveness for path-trees (d ≈ 2.3–2.5 transients on elongated branched
trees) as a round-3 re-preregistration question. Bars are NOT tightened
post-hoc (that would be tuning to taste — forbidden).

### 3.6 Constraint ablation — FIRES on κ (15/16), freezing mapped

Matched-pair Δs (on − off), frozen 2σ_paired rule:

- κ: 15/16 fire → FIRES (descriptive). By start: cubic Δκ ≈ +0.21…+0.30
  (H0/H1/H2 — bridgeless steering raises κ toward flat; replicates round-1's
  class-A +0.17…+0.25 with the calibrated ruler); er-sparse Δκ ≈
  −0.84…−0.90 (on-arm FROZEN at seed κ ≈ −1.1 vs evolved off-arm — freezing,
  not steering); H10 cubic ≈ +0.01…+0.03 (silent, 1/2 fires).
- d_iso: 2/16 fire → no-fire (er-sparse pairs unmeasurable: frozen seeds read
  ok=False — specificity working as designed).
- z: median Δz = +0.038, mixed signs (round-1's all-positive does not
  replicate — the frozen ER arms dominate the sign pattern).
- Membership: the constraint flips 4/4 cubic pairs (non-member trees,
  κ ≈ −0.26 → path-tree members, §3.5); matched off-arms verified
  non-members. Bridgelessness + cubic start + H0/H1/H2 selects elongated
  flat path-trees — pure constraint-drive evidence, mechanism open.

## 4. Verdicts (frozen §9 rules — one FAIL, one PASS, two descriptive)

| verdict | result | basis (frozen rule, margins) |
|---|---|---|
| V-DISCOVERY | FAIL ("needle, not basin") | 0/144 discovery members with gate PASS (§2) + reachability proven (§2) + kill-switch holding (§1, no driver collapse in grids) + H0 cooling demonstrated (0.0% drift, §3.4). All FAIL preconditions met → first-class clean negative for the as-run dynamics. Qualifiers (pre-registered + M1b): tension arms H5/H9/H10/H11 show late drift (med 1.4–4.8%, max 29–66%) — their negatives qualified by under-cooling; expensive arms H1/H2/H4/H11 steered at M1b-reduced strength (§1) — their negatives qualified by weakened legs. Full-strength negatives: 8/12 arms (H0/H3/H5/H6/H7/H8/H9/H10, incl. every square/triangle away-arm), frozen solid (≤2.6% drift except noted tension maxima). |
| V-ARTIFACT | PASS (no-artifact) | 12/12 adjacent hid pairs agree on membership majority (bar ≥ 80% = 9.6). Agreement is vacuous-unanimous (all agree "not a member") — stated, not oversold; M1b note: H4 ≈ H0 partly reflects weak sym vetoes (descriptive). Membership-level stability coexists with attractor-level drive (T→P→NT→L→X across hid, §3.1). |
| V-STABILITY | 0/144 preserved (stability NEGATIVE) | No run within edit 0.5 of its lattice while meeting B1+B2 (min edit 0.12 fails 3 bars as dense small-world). With V-DISCOVERY FAIL → "needle, not basin" on both legs (kill mapping). Lattices are not fixed points of any tested driver (live bars — a measured zero, not INCONCLUSIVE). |
| V-CONSTRAINT | DESCRIPTIVE: FIRES on κ | 15/16 pairs fire (§3.6); d_iso 2/16 no-fire; Δz mixed. Constraint flips 4/4 cubic membership pairs. |

The five path-tree members (§3.5) pass frozen bars in non-discovery legs and
are reported with exact-property characterization; they carry no verdict
weight and motivate a round-3 bar-tightening question (not a round-2 edit).

## 5. What round 2 established (exploratory, with provenance)

1. The M1 procedure flaw is fixed in design and verified by kill-switch
   (no voided legs), with a new implementation flaw M1b quantified honestly:
   restore-aliasing weakened expensive-leg vetoes (median real-reject
   fraction 0.22–0.25 spectral, 0.01 symmetry) — full strength for the 8
   cheap-driven arms, qualified steering for H1/H2/H4/H11 (§1). No legs voided.
2. The d_iso estimator validates at survey N: 5/5 gate bars + 2/2 spot bars
   pass deterministically; specificity improved (small-world → nan, not
   confident-wrong); reachability proven for every bar at every survey N (§2).
3. Twelve blind drivers → five attractor classes, none flat-3D-large-world:
   bushy trees (H0/H1/H2/H4/H7), path-trees (H3), near-trees (H6), loopy
   square-rich (H5/H9/H10/H11), 3-regular expanders (H8) — §3.1,
   `results/anneal2/*.json`. Away-from-trees pressures fail honestly: max-λ2
   collapses to trees exactly; square-max lands loopy-small-world.
4. B1∩B2 = ∅ over the 144-run discovery grid (round-1 anti-correlation
   replicated with live bars); the only members anywhere (5/316) are
   path-trees in stability/ablation legs (§3.5) — reported, characterized,
   unweighted.
5. Lattices are not fixed points (0/144 preserved, min edit 0.12 fails bars
   as dense small-world); H10 bistable by start at N = 4000 (dense-loopy vs
   near-tree); cooling demonstrated on collapse arms, qualified on tension
   arms (§§3.2–3.4).
6. Constraint drive quantified with mechanism split: cubic steering
   (Δκ ≈ +0.25, replicates round-1) vs ER-start freezing (8/8 runs at 0
   accepts, Δκ ≈ −0.87); membership flips 4/4 cubic pairs (§3.6).
7. Two pilot-caught methodology fixes with independent value: silent
   λ3-as-λ2 eigsh miss (E1, fixed + validated ≤ 2e-13) and tree-phase
   ARPACK non-convergence (E2, fail-fast maxiter + hold rule); periodic-BC
   requirement for shell-estimator stability (9/10 vs 10/10 evidence).
8. Positive controls at scale: cubic passes estimator + all bars at
   1000/2000/4000 (d = 3.42/3.06/3.09) — the ruler works where the survey ran.

## 6. Round-3 re-preregistration proposal (NOT implemented — post-hoc here)

0. Fix M1b FIRST: copy-on-restore + double-restore (restore→mutate→restore→
   verify) regression test; re-freeze; re-run at minimum the expensive arms
   (H1/H2/H4/H11 analogs) at full veto strength — H2-full-strength is the
   sharpest untested away-pressure. The kill-switch must additionally assert
   a minimum real-reject fraction on a pinned config (vetoes must bite, not
   just fire).
1. B1-bar tightening question: path-trees (diam 7–17× control) pass
   d ∈ [2.25, 3.75] via growth transients (§3.5). Round 3 should re-freeze
   B1 with an estimator that separates elongated trees from 3D bulk
   (candidates: volume-growth fit alongside shell fit, diameter-normalized
   window, or r_min scaling with N) — validated on PRISTINE controls +
   synthetic tree negatives BEFORE any anneal, same fail-safe.
2. Tension-arm schedules: square/edge tension evolves slower than collapse
   (§3.4). Round 3 should freeze STEPS from the slowest arm's settling (or
   N-scaled alpha holding final-T fixed), costed from a pilot.
3. Spectral-leg hardening: tree-phase holds (E2) phase-limit H1/H2. Options:
   shift-invert λ2 (validated vs dense), or a cheap spectral proxy as the
   frozen driver with exact λ2 as the checkpoint — frozen before compute.
4. Grid v3: the H2-collapse and H10-bistability results motivate arms that
   oppose densification AND collapse simultaneously (e.g., edge-window
   terms are FORBIDDEN as z-targets — stay with cycle/spectral combinations);
   keep the 6/6 away/compatible balance and the adjacency-Pareto structure.
5. Rule zero, ablation/seed/label/disqualification discipline carry over
   unchanged. D10 (§7) stays open until its close criterion is met.

## 7. D10 status (OPEN — criterion unmet, narrowed honestly)

D10 (vacuum selection from a graph-intrinsic principle) stays OPEN. Its close
criterion (round-1 §7: exhibit the principle + derive sparse/flat/3D minima
at large N + survive weight/seed/constraint ablation) is unmet: this round
exhibits no principle and derives no minima — it maps twelve blind drivers
(8 at full strength, 4 M1b-weakened) to five non-vacuum attractors with two legs' negatives measured (not
inconclusive). Contribution toward D10: (a) verified M1-free driver
machinery with kill-switch discipline reusable by any future principle;
(b) a calibrated dimension ruler + reachability method at survey N;
(c) the quantified elimination of 8 blind directions at full strength
(edge/regularity/square/triangle pressures and combos) plus 4 at M1b-reduced
strength (spectral±/symmetry) as vacuum selectors — the "needle, not basin" result constrains where a future
principle may live (not in these 12 directions). "The vacuum is a flat 3D
lattice" remains an assumed background, not a result.

## 8. Reproduce

`pip install -e ".[dev]"`, `pytest tests/test_anneal*_*.py -q` (70 tests),
`python3 scripts/run_anneal2_survey.py --jobs 3` (≈ 2.1 h, 316 runs + tally;
resume-safe, pilot files never tallied), outputs
`results/anneal2/{calibration.json,manifest.json,<run_id>.json}`.
Prereg: `docs/anneal2-prereg.md` (commit predates all survey compute; zero
amendments). Pilot/estimator-dev: `results/anneal2/pilot/` + §7.1/§11 logs.

## Appendix A. Estimator-dev + pilot provenance (controls-only, pre-freeze)

- Window variants tried (seed 11, pristine lattices only): (1,0.5) [V1],
  (2,0.5) [FROZEN — passes 7 lattice controls, minimal change], (2,0.7),
  (3,0.5). No variant passes diamond-1000 or fcc-4000 (pre-declared
  below-range references with structural reasons).
- Open→periodic forcing evidence: open-2000 cubic 9/10 gate passes
  (median 2.49, min 2.17, boundary noise) vs periodic-2000 10/10 at
  d = 3.06 exactly (zero variance). All survey lattice seeds periodic.
- Negatives: er-sparse/rr6 ok=False (all windows); path-1000 d ≈ 1.00;
  uniform trees d ≈ 1.6; balanced trees d ≈ 9–15 — all out-of-bar.
- Cooling: H0 settles 30k/60k (0% drift) → STEPS = 2× = 60k/120k/240k;
  H10 drifts (+46%/-7% — pre-registered qualifier).
- Spectral: k=6+zero-detection ≤ 2e-13 vs dense (9 families); maxiter 300
  (loopy converge identically, trees fail fast 0.1 s); per-proposal eigsh
  infeasible (80 min/run at 4000) → delayed acceptance (0.2–0.8 ms/step
  amortized, measured parity with cheap proposals).
- Max-N gate: one full H1-4000 run 1082 s < 1800 s (pre-fix timing) → spot
  leg allowed. Seed-build fix: ER 25-try cap (200-try burn 20–77 s at
  survey N). Builders verified 6/4/12-regular at all N.
