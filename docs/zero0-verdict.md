# ZERO-0 — Verdict: Zero Crossing and Phase-Singularity Census

Campaign branch: `cursor/zero-crossing-census-ee5c` (PR #98).
Prereg: `docs/zero0-prereg.md` (frozen §1–§13 + two pre-verdict
amendments noted below). Ledger: `data/zero0/verdict.json`
(4432 rows). Apparatus: `src/bh_graph/zero.py`,
`scripts/zero0_campaign.py`, `scripts/analyze_zero0.py`.

Epistemic firewall (ZERO-0Z) held throughout: no zero is called a
particle, matter, defect, source, vacuum, or singularity. "Phase
singularity" means only that `arg ψ` is undefined at `ψ = 0`.
No VAC-FIELD-0 verdict was consumed (backgrounds are preparations).

## 1. Campaign record

| Bank | Rows | Content |
|---|---|---|
| full | 4119 | generic 1820 · packet 48 · collide 320 · background 1730 · winding 105 · sector 90 · persistent 4 · twomode 2 |
| supp (protected regime) | 240 | background, absolute protocol, η-scale ∈ {0.01, 0.001} |
| supp2 (smooth winding) | 72 | winding, F3 + packet preps |
| refix | 1 | duplicate filed row (rewire-28/F4/seed 3), counted once in text |
| **total** | **4432** | 2 filed (initial-exclusion), 0 lost |

Headline: `dt = 0.02`, `T = 40`, `J = 1`, Krylov-exact steps.
`EPS_SCREEN = 1e-8`, `EPS_NEAR = 1e-3`, `EPS_CERT = 1e-10`,
`EPS_MINIT = 1e-3`, modal certification at `N ≤ 200`.

Amendments (both pre-verdict, both documented in the prereg):
A1. Level-1 = amplitude screening ∪ segment-bracket screening
(pure amplitude screening misses inter-grid crossings).
A2. Level-2 refinement capped at `REFINE_CAP = 60`/trace, overflow
filed (uncapped refinement proved infeasible: single tasks burned
>80 CPU-min on dense near-zero brackets). Level-1 screening stays
exhaustive, so candidate counts and `m(t)` statistics are
version-robust; 7 rows carry `refine_overflow > 0`.

## 2. Headline results

42,589 raw Level-1 candidates, of which 11,506 were refined
(31,083 filed as `refine_overflow` on 7 dense-bracket rows) into
**11,506 labeled events: 9,918 near-zero + 1,588 certified-modal
+ 0 symmetry-exact claimed beyond unit pins**. All 1,588 certified-modal events come from one
mechanism: matched-amplitude two-packet destructive interference at
relative phase π (ZERO-0J/K).

### Q1. Can ordinary evolution reach ψ_u = 0?

**Yes, by two exact mechanisms, both interference-nodal:**
(i) matched two-component cancellation `|ψ1| = |ψ2|`, `Δφ = π`
(1,588 modal-certified events, ZERO-0K law holds razor-sharp:
head-on/match/π cells yield 167–640 events/row while all other
phase/amplitude cells yield ~0); (ii) eigenvector nodal zeros
(ring-8: 8/8 nodes nodal; J2 L=3 flat band: 2/18 nodes nodal),
verified persistent under evolution (C3).
Generic (F1/F2/F3/F5) and single-packet states produced **zero**
certified exact zeros in 1,900+ rows: exact zero is reachable but
not generic.

### Q2. Generic, symmetry-enforced, interference-enforced, or fine-tuned?

**Interference-enforced or nodal; measure-zero otherwise.**
Near-zeros (`< 1e-3`) are common (9,918 events; trace minima
routinely 1e-4–1e-6); exact zeros require magnitude + phase matching
(codimension 2, ZERO-0A) and appear only where the preparation
enforces it. Single spreading packets yield up to ~1,000 deep
near-zeros/row (diagonal max-velocity packets) with **0 of ~2,000
modal-row events certifying** — the strongest genericity bound in
the campaign.

### Q3. Instantaneous or persistent?

**Both exist; all wild zeros are instantaneous.**
Anatomy: 75/75 certified events transverse (`ψ̇ ≠ 0`);
0 persistent-degenerate events observed outside constructed
eigenstates. Persistent zeros exist exactly (nodal eigenstates,
flat-band nodes) and are the only persistent class found (ZERO-0D).

### Q4. Can phase organization change without crossing zero?

**Yes — via bond phase-slip, a graph-specific mechanism.**
Principal-relative-phase cycle winding changes while every cycle
node stays nonzero (54,448 changes, 0 associated with support
zeros; the 26 support events all sit on undefined cycles and are
hence unassociable; min cycle amplitudes 1e-4–1e-1 vs guard 1e-7).
Slip diagnostic: every sampled change
coincides with a bond at `|Δθ| ≈ π` (2.85–3.14), i.e. the
principal-branch readout relabels as a bond phase crosses the cut.
Changes arrive as 0→±1→0 flicker pairs. The continuum intuition
("winding change needs a zero") does not transfer to this discrete
readout; verdict scoped to the tested definition per prereg §10.

### Q5. Does a nonzero coherent background suppress crossings?

**Yes, monotonically in the protected direction, with a rigorous
floor.** Full-bank absolute protocol (‖η‖ = 1): 5 near-zero events
in 1,490 rows, all on the largest graphs at small a. Supp bank
(‖η‖ ≤ 0.01): 240/240 spectrally-protected rows clean (C4), with
`m_min ≈ a/√N` as the triangle bound predicts (ZERO-0M). No
background kind (Z+/Zπ/Z−) shows excess crossings vs Z0 at matched
scale. Global-rescaling control (ZERO-0N) pinned: pure `aψ`
rescaling cannot change exact-zero verdicts.

### Q6. Is zero dynamically special or just (r, s) = (0, 0)?

**A regular point of (r, s) with three exact relational
consequences:** incident `B = J = 0` (Z3, pinned), `ρ̇ = 0` with
quadratic touch `ρ̈ = 2|ψ̇|²` (ZERO-0S, pinned), and undefined phase
(Z2, by definition). Energy is finite through all 1,212 anatomy
records (Z1/ZT: phase-coordinate singularity only). B-sign
behavior at certified events is mixed (45% reversal, 39% touch,
12% unchanged, 4% degenerate): zero is a *possible* relational
reset, not a mandatory one.

### Q7. Graph-generic vs spectral-class vs J2-specific?

- Generic: codimension-2 rarity, near-zero abundance, π-null law,
  background suppression, slip mechanism (observed on all five
  substrate classes).
- Spectral-class: low-mode/smooth states stay far from zero
  (ring F3/F4 `m_min ~ 1e-2` vs F1/F2/F5 `~1e-4`–`1e-5`).
- J2-specific: extensive flat band (N/2 modes) hosts nodal
  persistent zeros (2/18 nodes at L=3); dead (P−) sector evolves
  trivially with zero events in 30 rows.

## 3. Z1–Z4 assessment

| Claim | Verdict |
|---|---|
| Z1 (Cartesian regularity) | **Earned.** 1,212/1,212 finite-energy anatomy records; exact real equations hold through zeros. |
| Z2 (phase undefined at 0) | **Earned** (definition + one-sided limits measured; slow minima show clean π jumps, 98%). |
| Z3 (incident B = J = 0) | **Earned.** Theorem pinned in unit tests; 600/600 certified B/J traces touch zero. |
| Z4 (some phase changes may require zero) | **NOT earned in the strong form.** The tested winding readout changes without zeros via slip; no stable winding transition was observed in any regime. Filed, not claimed. |

## 4. Controls

C0 norm conservation: 4,430/4,430 traces ✓. C1 banked suites green
(foundation 1,004 passed). C2 two-mode recovery to 3.5e-15 ✓.
C3 nodal persistence 10/10 ✓. C4 protected rows clean 240/240 ✓.
C5/C6 global phase/scaling pattern invariance ✓ (unit-pinned).

## 5. Caveats (filed, not buried)

1. **k/−k window effect.** Axial ±k packet cells differ per-window
(e.g. 36 vs 0 events). H is real, so `ψ_{−k}(t) = conj(ψ_{+k}(−t))`:
the two runs sample time-mirrored windows of one orbit. No
asymmetry is claimed; the comparison requires mirrored windows.
2. **Phase-limit scale dependence.** Certified fast crossings show
small one-sided jumps (mean 0.24) vs π for slow minima — the fixed
±0.01 probe overshoots fast linear regimes. Adaptive-scale limits
are deferred apparatus work; no physics claimed from the
difference.
3. **Random-state winding is a negative control.** F1/F2/F5
windings are large random-walk integers; their thousands of
"changes" are diffusion, not transitions. P/Q conclusions rest on
smooth states + the slip diagnostic only.
4. **Row version mix.** 4 packet rows ran under the capped refiner;
cross-row count comparisons use version-robust `n_candidates` and
`m_stats`. One duplicate filed row (refix-f4) is counted once.
5. **Rewire-28/F4/seed 3** cannot meet initial exclusion (low-mode
nodal structure on the irregular substrate) — filed per prereg §6,
not forced.

## 6. Data

`data/zero0/verdict.json`: per-cell ledger (636 cells) + checks.
Beast rows: `~/zero0-data/rows-all/` (4,432 JSON rows), pilot +
full + supp + supp2 task files under `/tmp/zero0-tasks/`.
Reproduce: `scripts/zero0_tasks.py --bank full` →
`scripts/zero0_campaign.py` per line → `scripts/analyze_zero0.py`.
