# Vacuum/curvature derivation — preregistration (Phase 0 + Phase 1/2 protocol)

**Status:** preregistered BEFORE any vacuum computation was run. No number in
§1–§4 is a result; all thresholds were fixed before seeing κ on any vacuum
graph. Results go to `docs/VACUUM_REPORT.md` + `results/vacuum/*.json` only.

**Epistemic discipline:** every symbol below carries its `docs/model.md` label
(derived / fitted / assumed / exploratory / conjectured). Anything ABSENT from
`docs/model.md` stays CONJECTURE and out of validation scope.

---

## §0. Phase 0 — grounding audit (no new claims)

Targets the derivation attempt and gated protocols will use, each with repo
file + symbol + status per `docs/model.md` v0.4 / `docs/DEFERRED.md`.

### §0.1 Theoretical targets (used by Phase 1)

| # | Target | Repo file + symbol | model.md status | Verdict for use |
|---|---|---|---|---|
| T-a | Canonical neighborhood measure `m_x` uniform, idleness 0 | `orici._neighborhood_measure` default `p=0.0` | **assumed** (L0 postulate P4) | GROUNDED — postulate, used as-is |
| T-b | Ollivier–Ricci `κ(x,y)=1−W₁/d` values | `orici.ollivier_curvature` (exact LP) | **measured** given P4 (P4 text: "curvature values themselves are measured") | GROUNDED — measurement pipeline |
| T-c | OR→Ricci continuum limit | `orici`, `weakfield` via I6b | **input** (L1 import I6b, load-bearing for T8 sign + L2 p) | GROUNDED — flagged as import wherever κ is read geometrically |
| T-d | Radial-negativity sign of κ | `weakfield.kappa_profile`, T8 | **derived** given I4a+I4b+I6b+P4 | GROUNDED — sign benchmark for excursion profiles |
| T-e | Gradient slope `p_adj(s)=0.85+0.015s` | `orici.p_adj_of_shell` | **fitted** (L2 calibration F1) | GROUNDED as FIT — comparison context only, never a derivation input |
| T-f | Bridge exponent `β(N)` per-N values | `orici`/`shellscale`, `data/betascan_*.json` | **fitted** per N (L2 calibration F2; drift faster than 1/N) | GROUNDED as FIT — N-scaling caution applies to our N-scaling leg too |
| T-g | `κ→c₂` map `c₂(p)=p(2p−1)` | `pulsar.c2_of_p` | **ansatz** (L2 calibration F4; open derivation D3) | GROUNDED as ANSATZ — never used to "derive" p; D3 stays open |
| T-h | Radial exponent `p = 0.913 ± 0.049` (SEM 0.0055, stacked 0.911, R²=0.956) | `shellscale.campaign`, `data/p80_n1020_beta124.json` (80 graphs, N=1020, exact Floyd+LP) | **fitted** (L2 measurement of a fitted-pipeline output; F1/F2 fitted upstream) | GROUNDED as FIT — the comparison target p-recovery must hit WITHOUT tuning |
| T-i | D3 kill wire `p = 0.92 ± 0.056` at N=1024 class, held to N=16000 | `data/p80_n{4000,8000,16000}_*.json` (means 0.9315/0.9382/0.9137, per-N recalibrated β) | open falsifier (D3; power-law R² 0.91 vs 1/r² 0.81 cross-applied disagreement) | GROUNDED — primary recovery band (§2.3) + N-scaling kill wire (§2.4) |
| T-j | C1 log-κ emergence (log base `k_vac` from Laplacian transport, no tuned constants) | — (absent) | **ABSENT → CONJECTURE** | UNGROUNDED — the hypothesis under test, not a premise |
| T-k | C2 regular vacuum (uniform degree `k_vac`) | — (absent; P4 is measure-uniformity, NOT degree-uniformity) | **ABSENT → CONJECTURE** | UNGROUNDED — assumed only inside the derivation attempt as the thing being tested |
| T-l | C3 graph-intrinsic vacuum selection | — (absent; Kelvin/Weaire-Phelan analogy is motivation-only, imports continuum length/volume = circular pre-geometrically) | **ABSENT → CONJECTURE** | UNGROUNDED — selection claims out of scope; at most a measured regularity ranking is reported as EXPLORATORY |
| T-m | A15 / Weaire-Phelan advocacy | — (absent) | **ABSENT → CONJECTURE, EXCLUDED** (dual coordinations 12/14 contradict C2; would need explicit 2-type generalization + P4 re-examined) | EXCLUDED from families (§1.1) |

### §0.2 Landmine verification (verify, don't trust — all checked against repo)

| Claim | Check performed | Result |
|---|---|---|
| `R_s = 2M` is D6-open | `docs/model.md` §5 D6 + BM reduction theorem (§3, `k(M)` ⟺ `R_s(M)`); `horizon.schwarzschild_rs` docstring "THE single GR input" | CONFIRMED — D6 open; `R_s=2M` never used in Phase 1 |
| Kerr quadrupole is D2/S3-open (future wire) | `docs/DEFERRED.md` D2; `paper/v5/supplement.tex` S1/S3 ("quadrupole/QNM open; GW250114 QNM + GW241011 δ_Q future wires"); `paper/v5/main.tex` kill table "target (S1/S3)" | CONFIRMED — no Kerr claims; no overtone claims in Phase 2C |
| Horizon-pop threshold is `micro.k_crit` (packing, downstream of PATCH_AREA) | `micro.critical_k()` = `4πr²/4ln2` (float 12.566… at default), `micro.packing_kmax()` = 12 (int floor); both downstream of `horizon.PATCH_AREA = 4ln2` (I1a+I1b matching) | CONFIRMED with naming correction: the symbol is `micro.critical_k` / `micro.packing_kmax` — no `k_crit` symbol exists. Not used in Phase 1 (no horizon physics in vacuum κ) |
| `p = 0.913 ± 0.049` is a FIT to 80 graph sims (`shellscale.py`, `data/p80_n1020_beta124.json`) | File read: mean 0.91335263, std 0.04879002, sem 0.00545489, n_ok 80; `model.md` §4 labels the pipeline fitted (F1/F2 upstream) | CONFIRMED — labelled FIT everywhere; recovery must not tune to it |
| `κ→c₂` map is ansatz F4 with D3 open (power-law vs 1/r² + N-scaling kill wire) | `model.md` F4 row + §5 D3; `tests/test_orici.py::test_extraction_crosscheck_ansatz_dependent` (power-law R²>0.7 beats 1/r²; c₂ disagreement >1.0); N=4k/8k/16k artifacts with recalibrated β | CONFIRMED — F4 never used as derivation input; D3 N-scaling wire extended in §2.4 |

### §0.3 Phase-2 targets (gated protocols)

| # | Target | Repo file + symbol | model.md status | Protocol role |
|---|---|---|---|---|
| T-n | Quadratic-only LIV, `E_QG,2 = √8·E_P ≈ 3.45e19 GeV`, Fermi quad margin ~2.7e8 | `dispersion.eqg2_scale_gev`, `fermi_quad_margin`, `arrival_delay_s` | **derived** given regular-lattice tight-binding (T13; caveats: regular lattice, scalar only, near-horizon running open) | NULL-CHECK A (pre-grounded; mock-first, frozen statistic, then published bounds) |
| T-o | Echo null, `echo_margin_orders ≈ 160` (code value 159.88 at 100 Hz / E_det 0.01; "≈158" in task brief is stale by ~2 orders — code wins per model.md convention) | `gwdata.echo_margin_orders` | dimensional estimate, NOT a leg S-matrix derivation (T14) | NULL-CHECK C (pre-grounded; mock-first; LVK published nulls; no Bilby; no overtones) |
| T-p | 2PN lock (`c₁=3.36` vs GR 1.94, `w=1.953` solved, `c₂(0.92)=0.7728`, `c_tot=4.8695`) | `pulsar.*`, J0737/B1913 dicts (published PK params) | **solved/fitted** (F3/F4; circularity: graph-fit → GR-matching ansatz) | CONSISTENCY-GATE B only — NEVER labelled validation; no TOA re-timing (out of scope) |

**Scope consequence:** C1/C2/C3 are CONJECTURE. Phase 1 can at most PROMOTE
C1-form to "measured on these families" (still not derived — a measured
regularity is not a derivation) or KILL it. Nothing in Phase 1 can promote C2
to derived (regularity is assumed in the construction) or C3 (no selection
principle is tested). D2/D3/D6 stay open unless genuinely derived (they won't
be here — no derivation of `R_s=2M`, Kerr multipoles, or the `κ→c₂` map is
attempted).

---

## §1. Preregistered graph families (exact constructions)

All families are built with PERIODIC boundary conditions (PBC) so the
unperturbed vacuum is GENUINELY k-regular (no boundary degree deficit).
Regularity is ASSERTED in code (every node degree == k_vac) and tested.

### §1.1 Core families (must all run)

| Family | Symbol `k_vac` | Construction (exact) | Sizes (L → N) |
|---|---|---|---|
| Cubic (simple cubic, SC) | 6 | `L³` sites, bonds ±x/±y/±z, PBC per axis | L=6→216, L=8→512, L=10→1000 (test i); L=12→1728 (test ii/iii lever arm) |
| BCC (nearest-neighbor) | 8 | Conventional `L³` cells × 2 sites (corner + body center), 8 NN bonds each, PBC | L=5→250, L=6→432, L=7→686 (test i); L=8→1024 (test ii/iii) |
| FCC (nearest-neighbor) | 12 | Conventional `L³` cells × 4 sites, 12 NN bonds each, PBC | L=4→256, L=5→500, L=6→864 (test i); L=7→1372 (test ii/iii) |

Crystallography pins (no freedom): SC k=6, BCC NN k=8, FCC NN k=12 — these
are the standard coordination numbers, not choices.

### §1.2 Stretch family (run if core pipeline works; reported separately)

| Family | Symbol `k_vac` | Construction (exact) |
|---|---|---|
| Kelvin dual (k=14) | 14 | BCC SITES with 14 face-adjacency bonds (8 NN through hex faces + 6 NNN through square faces of the truncated-octahedron tiling). This is NOT the k=8 BCC NN graph — BCC(k=8) ≠ Kelvin-dual(k=14). Do not conflate. |

Sizes: L=5→250, L=6→432.

### §1.3 EXCLUDED

A15 / Weaire-Phelan dual: two coordinations (12/14) contradict C2
regularity. Excluded unless the C2 tension is resolved in writing first (it
is not — out of scope) or an explicit 2-type generalization with P4
re-examined is formalized (not attempted). No A15 code will be written.

---

## §2. Preregistered tests

### §2.1 Backend

- PRIMARY: `orici` EXACT backend — transportation LP (`scipy.linprog`,
  HiGHS) for W₁ with the P4 uniform measure (`p=0.0`), distances from sparse
  Johnson (`sinkor.all_pairs_johnson`, validated against Floyd in
  `tests/test_sinkor.py`), called via `orici.ollivier_curvature(g,x,y,
  _dist=..., _idx=...)`.
- SCALE CROSS-CHECK ONLY: `sinkor` Sinkhorn (`eps=0.05` and `0.01`,
  annealed). Rationale: entropic plans OVERSHOOT true W₁, so
  `κ_sink ≤ κ_exact` (documented bias, `sinkor` docstring) — verdicts must
  not depend on it. Reported as cross-check with the bias direction stated.
- All verdicts (PASS/FAIL/INCONCLUSIVE) rest on the EXACT backend unless a
  size is explicitly marked Sinkhorn-only (N-scaling leg, §2.4), in which
  case the verdict is labelled accordingly and Sinkhorn-vs-exact agreement
  at small N is shown first.

### §2.2 Test (i): κ = 0 on the unperturbed vacuum

- Procedure: per family × size, sample ≥50 edges (seeded, seed=0), exact κ
  each (shared Johnson cache).
- Bar (fixed before compute): PASS(family) iff max|κ| < 1e-6 over sampled
  edges at TWO sizes (size-independence = PBC-wrap control); else FAIL.
  Tolerance matches `test_eh_functional_flat_zero` (1e-6) scale; per-edge LP
  tolerance ~1e-9.
- Note: vertex-transitive does NOT imply κ=0 (trees are regular with κ<0),
  so this is a real measurement, not a formality. If only SC is flat, that
  is reported as a MEASURED regularity ranking (exploratory), not a C3
  derivation.

### §2.3 Test (ii): degree excursions → radial κ-profiles → form comparison

**Excursion protocols (fixed before seeing κ):**

- E1 (hub-plus): center node c gains +Δ edges to uniformly random nodes at
  unperturbed-hop-distance ≥3 from c (seeded). Δ ∈ {2, 4}. Degrees after:
  c has k+Δ, Δ partners have k+1, all else k.
- E2 (shell-plus): every node in the closed 1-ball of c (c + its k
  neighbors) gains +1 edge to a uniformly random node at unperturbed
  distance ≥3 (seeded). More symmetric, shell-like.
- Radial coordinate r = hop distance from c in the PERTURBED graph
  (graph-intrinsic choice, preregistered). Profile: mean exact-κ over
  radial edges per integer-r bin (radial = endpoints differ in r).
- r_max rule (preregistered, not a number): largest r with an UNWRAPPED
  r-ball (ball contains no PBC-identified pair — checked via lattice
  coordinates); REQUIRE r_max ≥ 4 else grow L (sizes in §1.1 chosen for
  this; fallback: report INCONCLUSIVE for lever-arm, not FAIL).

**Form comparison (uniform masking, preregistered):** all three models fit
the SAME bins: bins with mean κ<0 (the T8 attraction-sign regime in which
the BU p-pipeline is defined). If fewer than 4 negative bins → form
comparison INCONCLUSIVE (insufficient lever arm). Full-|κ| fits reported as
exploratory only.

| Model | Form | Fit variables |
|---|---|---|
| (a) log (C1) | \|κ\|(r) = a + b·ln(r) | linear LS on (ln r, \|κ\|) |
| (b) power (BU) | \|κ\|(r) = A·r^(−p) | linear LS on (ln r, ln\|κ\|) — SAME as `orici.fit_scaling_power` |
| (c) linear | \|κ\|(r) = a + b·r | linear LS on (r, \|κ\|) |

Metrics (all reported): R² on native scale, R² + RSS on COMMON \|κ\| scale,
AIC/BIC (k=2 params each; ΔBIC>10 = decisive per Kass–Raftery).

**Bar for "log emerges" (ALL must hold):**

1. Log wins DECISIVELY: ΔBIC > 10 vs BOTH power-law and linear on the
   stacked profile (stacked = mean over excursion seeds {0,1,2} per
   family×protocol), in ≥2 of 3 core families.
2. C1 base test (GATED on 1): with per-family natural-log slope b_fam, the
   base-absorbed slope B_fam = b_fam·ln(k_vac) has overlapping 95% CIs
   across the winning families (i.e. the k_vac-dependence is absorbed by
   the log base, as C1 claims) — else the form is "log-like" but the
   base-k_vac content FAILS.

If (1) fails → C1-form KILLED on these families (a successful kill, reported
with equal rigor). No rescue with extra parameters (no profile reweighting,
no post-hoc masking changes, no third excursion protocol).

### §2.4 Test (iii): p-recovery WITHOUT tuning + D3 N-scaling

**p-recovery:**

- Procedure: SAME `orici.fit_scaling_power` metric as BU (power-law on
  κ<0 bins, ≥3 bins) applied to each excursion stacked profile. NO
  constant is adjusted to match p — the excursion protocols (§2.3) contain
  no κ-dependent parameter (Δ, seeds, r_max rule all fixed above).
- Bar (fixed before compute): RECOVERED iff |p − 0.92| ≤ 0.056 (the D3
  kill-wire band) AND R² > 0.7 (the `test_extraction_crosscheck` bar), on
  ≥2 of 3 core families (any protocol, but the SAME protocol must work on
  both — no mixing E1/E2 across families post-hoc).
- Secondary (descriptive, not a bar): distance of p to the fitted 0.913 in
  units of the excursion-fit error; R², residual pattern.
- If not recovered → "p not recovered" KILL (successful kill, not failure).

**D3 N-scaling (beyond N=1020 per kill wire):**

- Procedure: largest sizes per family (SC L=12/N=1728, BCC L=8/N=1024,
  FCC L=7/N=1372 — all >1020 except BCC which is ≈1020; add BCC L=9/N=1458
  if runtime allows), exact backend if Johnson+LPs complete in <30 min per
  graph else Sinkhorn-only (labelled; small-N Sinkhorn-vs-exact agreement
  shown first).
- Report: p(N) trend across the three test-(i) sizes + the large size, per
  family. No bar (exploratory extension of the D3 wire) — but a p(N) drift
  OUTSIDE 0.92±0.056 at large N is recorded as wire pressure, and drift
  WITHIN is recorded as wire-held-on-vacuum-graphs (not as BU validation —
  different graph class).

---

## §3. Preregistered Phase-2 protocols (GATED)

Gate rule: a protocol runs only if its theoretical target survived Phases
0–1. Null-checks A and C are pre-grounded (T-n, T-o) and may run regardless
(mock-first, frozen statistic, then real/published data). Gate B is
CONSISTENCY-GATE only, always.

### §3.1 Protocol A — LIV null (Fermi GRB 090510/080916C)

- Prediction (T-n): quadratic-only, `E_QG,2 = √8·E_P`; 31-GeV delay over
  cosmological distances ~1e-19–1e-18 s (~1e8 below Fermi sensitivity).
- Mock-first: synthetic GRB photon lists (power-law spectrum, E²-delay
  injection at model scale AND at an excluded scale); FROZEN statistic =
  `arrival_delay_s(31.0, dist_mpc)` comparison + E²-slope sign check.
  Mock must show: statistic QUIET at model scale, FIRES at excluded scale
  (validates the statistic has power).
- Real-data leg: PUBLISHED bounds (Abdo et al. 2009: linear >9.3e19 GeV,
  quad >1.3e11 GeV; GRB 090510 31-GeV photon; 080916C limits) — no raw
  HEASARC photon download required (model delay is 19 orders below
  ~1 s-scale limits; the comparison is analytic).
- Falsification bar (preregistered): FAIL iff predicted 31-GeV delay
  exceeds published bounds. PASS = NULL HELD with margin quoted.

### §3.2 Protocol C — Echo null (GWOSC 4 kHz, GW150914 + GW190521)

- Prediction (T-o): NO detectable echoes (echo energy ~1e-160 vs O(0.01)
  detectability; margin ~160 orders).
- Mock-first: synthetic ringdown + noise with (a) injected echo at
  detectable level → frozen excess-power statistic must FIRE; (b) injected
  echo at model level → must stay QUIET.
- Real-data leg: GWOSC 4 kHz strain for GW150914 + GW190521 IF reachable
  offline-cached or via network; else PUBLISHED LVK nulls (O3 BayesWave +
  template searches, Abbott et al. PRD 112 084080; Uchikata et al. PRD 108
  104040) + analytic margin quote. Data leg SKIPPED (not failed) with
  reason if GWOSC unreachable.
- Constraints: NO Bilby PE without pre-approved budget. NO overtone claims
  (D2-open). Verify LVK nulls stay consistent; quote the margin.

### §3.3 Protocol B — 2PN gate (Double Pulsar PUBLISHED PK params, Kramer+2021)

- Procedure: published PK params only (J0737 `ω̇=16.899323(13)` deg/yr,
  `sin i`; B1913 `ω̇`; already in `pulsar.py` dicts — verify values match
  Kramer+2021 before use). NO TOA re-timing (out of scope).
- Gate: model `ω̇` at (a) fitted p=0.913 and (b) Phase-1 p IF recovered
  (else (b) omitted — no invented p), vs observed, in σ.
- Label: CONSISTENCY-GATE, NEVER validation (circularity: graph-fit →
  GR-matching ansatz → pulsars-confirm-GR). A gate PASS means "not
  inconsistent", nothing more.

---

## §4. Deliverables, branch, kill discipline

- Code: `src/bh_graph/vacuum_*.py` + `tests/test_vacuum_*.py` (all passing).
- Results: `results/vacuum/*.json` (exact-backend profiles, fits, verdicts).
- Report: `docs/VACUUM_REPORT.md` with per-test verdicts (PASS/FAIL/
  INCONCLUSIVE) + margins. FAIL of C1-form or p-recovery = SUCCESSFUL KILL.
- Branch `cursor/vacuum-derivation-0c63` off `main`; PR on completion.
- Compute: CPU-only, laptop-scale (largest graph N=1728, ~10² exact LPs per
  graph); no spend >$25 (nothing to ask for — no paid compute used).
- Non-goals (restated): no `R_s=2M`/Kerr/`κ→c₂`-by-assumption (D2/D3/D6 stay
  open); no A15; no TOA re-timing; no full PE; the word "confirm" appears
  only next to a pre-registered bar.

---

*Preregistration integrity: this file was committed BEFORE any `vacuum_*`
computation ran. Any deviation (extra protocol, changed bar, re-masking) must
be recorded in `docs/VACUUM_REPORT.md` as a PROTOCOL DEVIATION with
justification — silent deviations are forbidden.*
