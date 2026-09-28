# Vacuum/curvature derivation — report

**Branch:** `cursor/vacuum-derivation-7061` · **Prereg:**
`docs/derivation-prereg.md` (committed `0fef495`, BEFORE any compute;
one logged amendment A1, exploratory-only) · **Date:** 2026-09-28.

**One-paragraph verdict:** C1 (log-κ emergence) is KILLED robustly —
no log scaling under degree excursions on any vacuum family under
either edge assignment (0 strong log wins in 117 conclusive cells),
and the BU exponent is not recovered (0/108 cells in band; vacuum
response is contact-localized, bulk stays at vacuum κ to LP precision).
C2 (regular flat vacuum exists) SURVIVES — cubic/BCC/FCC are exactly
flat (κ≡0 to 2e-16), and Kelvin is flat at adequate sizes (nc≥5;
the prereg'd nc=3,4 positives are a small-box artifact, honestly owned
below). The A15 proposal's numbers collapse on audit: `c₂=1.21`
UNGROUNDED (0/48 map/size/BC hits + size-drifting gap), the p-formula
NON-SELECTIVE (16/17 vacuum candidates accepted — not evidence FOR
A15), `N_crit=15` UNGROUNDED, and the D1–D6 "Closed" stamps NOT ADOPTED.
D1–D9 all remain OPEN. Phase-2 nulls held (LIV by 18.7 orders, echoes
by 159.9 orders) and the 2PN consistency gate passes — as
NULL-CHECK/CONSISTENCY-GATE labels, never validation.

Epistemic labels follow `docs/model.md`: every number below is tagged
**derived / fitted / assumed / exploratory / conjectured** (or
**measured** = output of code on this branch, the model's word for it).

---

## 1. Verdict table (prereg'd bars, no silent edits)

| Test | Bar (prereg) | Result (measured) | Verdict |
|---|---|---|---|
| (i) κ=0 unperturbed (§4) | PASS iff max\|κ\|<1e-9 ALL 9 graphs | cubic/BCC/FCC: ≤2.2e-16 PASS (7 orders margin); kelvin-3: 0.357, kelvin-4: 0.071 → FAIL trigger | **FAIL\*** — \*small-box artifact: supplementary kelvin-5/6 κ≡0 (3.3e-16). Substantive: flat vacua exist in all 4 families; C2 NOT killed |
| (ii) log emerges (§3.3) | PASS iff log wins ΔBIC>6 in ≥80% + median R²>0.9; FAIL iff <20% or R²<0.5 | 45/81 conclusive; log strong-wins **0/45 (0%)**; winners linear 30 / log 15 (9 tie artifacts) / power 0; median R²_log=0.635 | **FAIL = SUCCESSFUL KILL** (observable-robust: A1 exploratory 0/72 strong, linear 57 / log 15 / power 0) |
| (iii) p recovered (§5.1) | PASS iff ≥1 family ≥50% in BU band | **0/45** in band (cubic p≡0; kelvin −0.67..−0.24; fcc −1.46..2.88); exploratory 0/63 | **FAIL = SUCCESSFUL KILL** |
| A1 spectral (§6.1) | UNGROUNDED iff no (map,size,BC) yields 1.21±5% | **0/48 hits** (closest 9% off); λ₁ drifts 2× over 2 sizes | **c₂=1.21 UNGROUNDED**; symbol collision = CONTRADICTION (same-q) else rename γ_gap |
| A2 selectivity (§6.2) | NON-SELECTIVE iff >50% of k∈[6,22] hit band | **16/17 hit (94%)**; implied k∈[6.1,22.0] | **NON-SELECTIVE — not evidence FOR A15** |
| A3 regularity (§6.3) | characterization | A15 exactly biregular 12/14, mean 13.5 ✓ (as MEAN); TV=0.028; κ̄≈−0.15 edge-split vs regulars κ≡0 | **P4-uniformity measurably fails at transport level; LIV symmetry survives (no LIV exclusion)** |
| 2A LIV null (§7) | FAIL iff 31-GeV delay > Fermi bound | 1.86e-19 s vs 0.859 s | **NULL-HELD by 18.7 orders** |
| 2C echo null (§7) | NULL-HELD iff margin > 10 orders | 159.9 orders | **NULL-HELD** |
| 2B 2PN gate (§7) | GATE-PASS iff ω̇,sin i < 1σ | 5e-10σ (refit), 6e-4σ fixed-M; sin i +0.15e-3 (<1σ) | **GATE-PASS (CONSISTENCY-GATE, never VALIDATION)** |

Ledger: **D1–D9 all remain OPEN** (§7). No status moved (nothing met a
promotion bar; Test-i's FAIL is artifact-qualified, not a derivation).

---

## 2. What was built (deliverables)

- `src/bh_graph/vacuum_graphs.py` — periodic cubic (k=6), BCC (k=8),
  FCC (k=12), Kelvin dual (k=14 = BCC-8 + cube edges, separate builder,
  edge-superset test), A15-dual audit object (parameter-free
  periodic-images Delaunay), pendant-excursion perturbation (frozen
  s∈{2,4,8}, frozen centers). Builders take no exponent input
  (no-tuning audit test).
- `src/bh_graph/vacuum_curvature.py` — exact-OR profiles (prereg
  intra-shell + A1 radial/min-depth), 3-model OLS comparison
  (R²/RSS/AIC/BIC), Sinkhorn cross-check wrapper.
- `src/bh_graph/vacuum_spectra.py` — normalized-Laplacian spectra,
  gap info, candidate maps M1–M6, selectivity audit, degree/TV metrics.
- `tests/test_vacuum_{graphs,curvature,spectra}.py` — 25 tests, all
  passing; full suite **436 passed, 2 skipped** (pre-existing
  torch/GPU-only skips).
- `scripts/vacuum_campaign.py`, `scripts/vacuum_radial.py`,
  `scripts/vacuum_supplementary.py` — reproducible runners.
- `results/vacuum/*.json` — `test_i`, `grid` (99 cells: 81 prereg +
  18 cubic L=7,8 scaling), `grid_radial` (81 A1 cells), `nscaling`,
  `spectral`, `selectivity`, `regularity`, `phase2`,
  `sinkhorn_xcheck`, `supplementary_sizes`, `meta`.

---

## 3. Phase 1 — derivation attempt

### 3.1 Test (i): κ = 0 on unperturbed vacua — FAIL\* (artifact-qualified)

Measured exact-OR κ on every edge of all 9 prereg'd graphs
(`results/vacuum/test_i.json`):

| Graph | N | edges | max\|κ\| | mean κ | Per-graph |
|---|---|---|---|---|---|
| cubic-4/5/6 | 64/125/216 | 192/375/648 | 1.1e-16 | 0 | PASS (margin ~1e7×) |
| bcc-3/4 | 54/128 | 216/512 | 0 | 0 | PASS (exact) |
| fcc-3/4 | 108/256 | 648/1536 | 2.2e-16 | −0.0 | PASS (margin ~1e7×) |
| kelvin-3/4 | 54/128 | 378/896 | 0.357/0.071 | +0.276/+0.031 | **FAIL trigger** |

Per the prereg'd §4 bar (any graph >1e-3 → FAIL), Test (i) is a FAIL.
The honest follow-up (supplementary, `supplementary_sizes.json`):
kelvin-5 (N=250) and kelvin-6 (N=432) give κ≡0 to 3.3e-16 on all
1750/3024 edges. The nc=3,4 positives are finite-size wraparound
(short periodic wraps shrink W₁ couplings), vanishing with size —
while cubic/BCC/FCC are flat at every tested size. Substantive
conclusion: **flat regular vacua exist in all four families; C2 is not
killed; the prereg FAIL kills "nc=3,4 boxes are adequate", i.e. a
prereg-design miss, owned here.** A size-adequate follow-up prereg
(nc≥5) is expected to PASS (exploratory prediction, not a verdict).

### 3.2 Test (ii): log vs power-law vs linear — FAIL = KILL (robust)

Primary (prereg §3 intra-shell observable, `results/vacuum/grid.json`):
45/81 cells conclusive (36 inconclusive: cubic-even/BCC have ZERO
intra-shell edges — bipartite graphs admit no odd cycles — plus
noise-floor shells; reported, never imputed). Of 45 conclusive:

- Strong wins (ΔBIC>6, Kass–Raftery): **NONE for any model (0/45)** —
  log strong-win fraction 0% < 20% → FAIL bar triggers.
- Weak wins: linear 30, log 15, power 0. Of the 15 log wins, 9 are
  cubic-L5 tie artifacts (flat noise-floor profiles, R²=NaN,
  ΔBIC≡0, winner by dict order) — only 6 FCC cells genuinely prefer
  log, all weakly (best ΔBIC_log-vs-next < 4).
- Median R²: log 0.635, power 0.640, linear 0.673 — all below the 0.9
  PASS conjunction.
- Leading alternative: LINEAR, weakly (no strong wins anywhere — the
  sharpest statement is "none of the three models is strongly
  supported; the response is too small to discriminate").

Amendment-A1 exploratory (radial/min-depth assignment, shells 1–4,
`results/vacuum/grid_radial.json`): 72/81 conclusive, strong wins
0/72, weak wins linear 57 / log 15 (9 BCC ties on exact-zero flats) /
power 0, median R²_log = 0.40. **Kill is OBSERVABLE-ROBUST** per A1's
frozen interpretation rule. No rescue parameters were or will be added.

Physical picture (measured, exploratory): the excursion response is
CONTACT-LOCALIZED — shell-0 (defect-incident) κ̄ = −0.28..−0.44
(sign-mixed: 43–75% of contact edges negative), shells ≥1 at vacuum κ
to LP precision (cubic-6 s=8: shells 1–4 all 1.1e-16). Curvature does
not propagate into the lattice bulk under pendant defects. Contact
response grows monotonically with s but saturates (−0.31→−0.40→−0.41
cubic), not log-linear. Base-k slopes b·ln(k): cubic/BCC/FCC ≈ 0
(≤4e-17), Kelvin ≈ 0.11 (not order-unity; log not winning there
anyway) — no "no-tuned-constants" slope recovery (exploratory, no bar).

### 3.3 Test (iii): radial exponent — FAIL = KILL

p from the frozen M-pow OLS slope, zero free constants
(`results/vacuum/grid.json` + `grid_radial.json`):

- Primary: 0/45 conclusive cells in BU band [0.864, 0.962]
  (cubic p≡0 — flat; kelvin −0.67..−0.24; fcc −1.46..2.88, fitting
  LP noise at ~1e-17). No family passes → FAIL.
- Exploratory: 0/63. N-scaling (cubic L=4..8, N=64..512, ≥8× span):
  p_vac ≡ 0 at every N — trivially stable, consistently zero, never
  near 0.913. Scaling slope degenerate (nothing to fit).
- The profiles are additionally s-INSENSITIVE (identical p across
  s=2,4,8 at fixed center in the primary observable) — the defect
  strength leaves no radial trace.

Negative result reported with full rigor: **C1 does not emerge from
graph transport under the prereg'd operationalization, and p is not
recovered without tuning.** The BU shell-graph power law (fitted F1+F2
construction) is specific to that construction, not a generic vacuum
response — power-law NEVER wins on vacua (0/45 primary, 0/72 A1).

Backend note: primary = `orici` exact LP throughout; Sinkhorn
cross-check (cubic-4, 8 edges) confirms the documented bias direction
(κ_sink=5.6e-16 ≤ κ_exact+1e-6; both at noise floor) —
`results/vacuum/sinkhorn_xcheck.json`. Verdicts never use Sinkhorn.

---

## 4. Addendum — A15/k_vac=13.5/c₂=1.21 probe

### 4.1 SPECTRAL CHECK — c₂ = 1.21 UNGROUNDED + symbol CONTRADICTION

Construction validated: periodic-images Delaunay (parameter-free — no
cutoff) reproduces EXACTLY biregular 12/14, mean 13.5, 1:3 ratio at
nc=2 (16:48) and nc=3 (54:162), connected
(`results/vacuum/regularity.json`). Single open cell N=8 also built
(BC diagnostic).

Map audit (`results/vacuum/spectral.json`): all 6 prereg'd candidate
maps (1/λ₁, λ₁, 1/√λ₁, −lnλ₁, 2/λ₁, ⟨k⟩λ₁/2) × 8 graphs (A15 nc=2,3 +
open cell + 5 regular controls) = 48 combos. **Zero hits** of 1.21±5%
[1.15,1.27]; closest is 1.099 (cubic-L4 M4, 9% off). The proposal
states NO map, so there is no seventh reading to test — absence of a
stated map = UNGROUNDED, and the audit shows the plausible family
fails wholesale. Independently fatal: λ₁ drifts ~2× across sizes
(A15: 0.460@64 → 0.225@216; cubic: 0.333@64 → 0.167@216) toward the
infinite-lattice λ₁=0 — ANY gap-derived "constant" is size-dependent
without a thermodynamic-limit prescription the proposal does not give.
Controls behave (bipartite cubic/BCC λ_max=2.000 exactly).

Symbol collision — decided: repo c₂ = c₂(p)=p(2p−1) (F4 ansatz,
measured 0.754 at BU p=0.913). |1.21−0.754| = 0.456 = 3.5σ (per-graph
σ=0.049-propagated) = 31σ (SEM-propagated). **Same-quantity reading:
CONTRADICTION. Different-quantity reading: the claimed object is
renamed γ_gap and shares no symbol with repo c₂.** This report uses
γ_gap=1.21 (conjectured/ungrounded) vs c₂=0.754 (F4 ansatz).

### 4.2 SELECTIVITY AUDIT — NON-SELECTIVE, not evidence FOR A15

p̂(k)=(1/1.21)(1+1/k) over integer k∈[6,22] vs frozen BU band
(`results/vacuum/selectivity.json`): **16/17 hit (94%)** — every k
except k=6, which misses by 0.002 (p̂(6)=0.9642 vs band top 0.962).
Implied k-range solving the band: **[6.1, 22.0]** — the entire
plausible vacuum range. Bar (>50% → non-selective) triggers
overwhelmingly. **A formula that accepts cubic (6), BCC (8), FCC (12),
Kelvin (14), and everything else cannot discriminate vacuum candidates
and is not evidence FOR A15** (explicit prereg'd sentence). Corollary:
with repo c₂=0.7728 the formula gives p̂∈[1.35,1.51], entirely outside
the band — formula+repo-c₂ inconsistent (symbol-collision consequence).
p̂(13.5)=0.888 (conjectured formula) vs BU 0.913±0.049 (fitted): close
is meaningless without selectivity.

### 4.3 REGULARITY CHECK — P4-uniformity fails at transport level

- R1 degrees: regulars Var=0 test-asserted; A15 exactly {12:×1/4,
  14:×3/4} (proposal's 12/14/13.5 grounded AS A MEAN — a mean is not
  a degree, and C2 requires uniform degree; §1.4 exclusion stands).
- R2 stationary TV from uniform: 0.0000 (all regulars) vs **0.0278**
  (A15, both sizes) — random-walk transport provably non-uniform.
- R3 unperturbed-κ uniformity: regulars κ≡0, std ~1e-16; A15 κ̄≈−0.15
  (stable nc=3,4; nc=2 +0.08 is small-box), std 0.067, edge-type-split
  (12–14: +0.083 vs 14–14: +0.071 at nc=2; no 12–12 edges exist —
  A-sites bond exclusively to B-sites). Transport heterogeneity is
  measurable at every level.
- R4 LIV relevance: A15-dual is cell-periodic → k↔−k symmetry survives
  at cell level → T13's linear-term absence is unaffected; biregularity
  touches isotropy/higher-order only (degree span 0 vs 2). **No claim
  that A15 violates Fermi bounds — the regularity failure constrains
  C2/P4 justification, not LIV exclusion.**

### 4.4 LEDGER INTEGRITY + N_crit=15

- `N_crit=15`: UNGROUNDED — no `N_crit` symbol exists in the repo;
  the actual pop threshold is k_crit=12.57/floor 12 (T5, measured).
- The proposal's renumbered D1–D6 "Closed" stamps are NOT ADOPTED
  under any circumstance (§6.4). D-items keep `docs/model.md` §5
  meanings; nothing moved (see §7).

---

## 5. Phase 2 — gated protocols (labels mandatory)

- **A. LIV null** (NULL-CHECK): mock (10 GeV, 3 Gpc) → 2.6e-20 s
  (matches T13 ~1e-20 s expectation ✓); real 31-GeV GRB 090510 photon
  (Abdo+2009, z=0.903, D≈2240 Mpc light-travel) → 1.86e-19 s vs
  published bound Δt<0.859 s → **NULL-HELD by 18.7 orders**.
  E_QG,2=√8·E_P=3.45e19 GeV (derived T13); Fermi quad margin 2.66e8 ✓.
- **C. Echo null** (NULL-CHECK): echo_margin_orders(100 Hz) = **159.9**
  (≈158 ✓) → LVK O3 nulls (BayesWave + template searches, per `gwdata`
  docstring) consistent → **NULL-HELD**. No PE, no overtone claims.
- **B. 2PN gate** (CONSISTENCY-GATE, repo-pinned PK per code comment
  citing Kramer+2021; no TOA re-timing): p=0.92 model refits
  J0737 ω̇ to 5e-10σ, fixed-M residual 6e-4σ, sin i 0.99989 vs
  0.99974±~0.0003 (<1σ) → **GATE-PASS** — circularity acknowledged
  (graph-fit → GR-matching ansatz → pulsars-confirm-GR), never called
  validation. B1913 Pb pinned for reference.

---

## 6. Kill/keep accounting (honesty ledger additions)

KILLED (this branch, prereg'd bars): C1 log-κ emergence (robust);
"p recovered from vacuum transport"; γ_gap=1.21 as grounded (UNGROUNDED);
p-formula as A15 evidence (NON-SELECTIVE); "nc=3,4 Kelvin boxes are
Ricci-flat" (artifact); power-law as generic vacuum response (0 wins).

KEPT: C2 regular vacuum (4 flat families at adequate sizes); T13 LIV
null; T14 echo null; 2PN gate; P4 canonical measure (used throughout,
unchallenged); BU p=0.913±0.049 as the fitted L2 target (its
explanation is NOT vacuum transport — D3/D4 remain the live leads).

SPECIFICATION GAPS FOUND (for follow-ups): C1 states a log base but no
slope → base untestable beyond rescaling (§3.2); §3.1 intra-shell
observable blind on bipartite lattices (A1 fix validated, needs a
fresh prereg + held-out sizes for verdict weight); Kelvin needs nc≥5.

---

## 7. D-ledger (all OPEN — no bulk flips, no renumbering)

| ID | model.md meaning | This branch | Status |
|---|---|---|---|
| D1 | graph evaporation isometry V_k | untouched | OPEN |
| D2 | Kerr multipoles from graph | untouched (no quadrupole work) | OPEN |
| D3 | quantitative κ→c₂ map | C1 vacuum route KILLED; shell-route wire untouched | OPEN |
| D4 | β(N), w from geometry | untouched | OPEN |
| D5 | NICER M-R-Λ from routing | untouched | OPEN |
| D6 | R_s=2M from wiring | untouched (I3 still the one GR input) | OPEN |
| D7 | kilonova RT | untouched | OPEN |
| D8 | shedding ε(M,a,q) | untouched | OPEN |
| D9 | Raychaudhuri for leg bundles | untouched | OPEN |

Proposal's "D1–D6 Closed" (renumbered): NOT ADOPTED. Promotion requires
a prereg'd bar + merged tests + review — none met.

---

## 8. Reproduce

`pip install -e ".[dev]"` →
`pytest tests/test_vacuum_graphs.py tests/test_vacuum_curvature.py tests/test_vacuum_spectra.py -q`
(25 passed) →
`python3 scripts/vacuum_campaign.py` (~25 s) →
`python3 scripts/vacuum_radial.py` (~25 s) →
`python3 scripts/vacuum_supplementary.py` (~20 s).
Full suite: 436 passed, 2 skipped (torch/GPU-only, pre-existing).
Compute spend: local only, <$1. The word "confirm" is never used for a
physics claim (all verdicts use PASS / FAIL / NULL-HELD / GATE-PASS /
UNGROUNDED / NON-SELECTIVE per prereg'd bars; remaining "confirm*"
strings are audit-trail verbs, e.g. "confirmed the symbol exists").
