# Vacuum/curvature derivation — preregistration

**Status:** preregistered BEFORE any new computation on branch
`cursor/vacuum-derivation-7061`. No `results/vacuum/*` artifact, no
`src/bh_graph/vacuum_*.py` measurement, and no Phase-1/Addendum number
may predate this file (check `git log`). Edits after first compute must
be appended under §8 with date + rationale, never silent.

**Scope:** Phase 0 grounding audit (§0), Phase 1 derivation attempt
(C1 log-κ emergence on genuinely k-regular vacua, §2–§5), Addendum
A15/k_vac=13.5/c₂=1.21 probe (§6), and gated Phase-2 null-checks (§7).

**Epistemic labels** (mandatory, per `docs/model.md`): every number in
the report is tagged derived / fitted / assumed / exploratory /
conjectured. Anything ABSENT from `docs/model.md` stays CONJECTURE and
out of validation scope.

---

## §0. Phase 0 — grounding audit (read-only, no new claims)

Tabled from `docs/model.md` v0.4 + `docs/DEFERRED.md` + repo HEAD.
"Status" is the model.md status, not our opinion. Verified 2026-09-28
by reading the cited file/symbol (commit `d19929b`).

### §0.1 Theoretical targets used by this prereg

| # | Target | Repo file + symbol | model.md status |
|---|---|---|---|
| G1 | Ollivier–Ricci `κ(x,y)=1−W₁(m_x,m_y)/d` | `orici.ollivier_curvature` | P4 (measure postulated) + I6b (continuum limit imported); values measured |
| G2 | Canonical neighborhood measure (uniform, `p=0`) | `orici._neighborhood_measure` | P4 postulated |
| G3 | Sinkhorn OR backend | `sinkor.sinkhorn_w1`, `ollivier_curvature_sinkhorn` | measured w/ documented bias `κ_sink ≤ κ_exact` |
| G4 | Radial exponent `p = 0.913 ± 0.049` (SEM 0.0055, stacked 0.911, R² 0.956, 80/80 ok) | `shellscale.measure_p_csr`, `data/p80_n1020_beta124.json` | L2 measurement of a FITTED construction (F1 gradient + F2 β=1.24@1020 fitted); NOT derived |
| G5 | N-ladder `p`: 0.9315@4k, 0.9382@8k, 0.9137@16k | `data/p80_n4000_beta099.json`, `data/p80_n8000_beta087.json`, `data/p80_n16000_beta074.json` | L2 measurements (same fitted construction, β refit per N) |
| G6 | `κ→c₂` map `c₂(p)=p(2p−1)`; `c₂(0.92)=0.7728` | `pulsar.c2_of_p` | F4 ANSATZ; derivation open (D3); power-law vs `k₀−c₂/r²` disagree cross-applied (`test_extraction_crosscheck_ansatz_dependent`) |
| G7 | 2PN weight `w=1.953`, `c_tot=c₁+w·c₂` | `pulsar.W_2PN`, `ctot` | F3 SOLVED from cancellation, not derived (D4) |
| G8 | Bridge exponent β(N): 1.5@300 → 0.74@16k | `orici.n_bridges_for_pair`, `sinkor.beta_fit_inv_n` | F2 FITTED per N (drift faster than 1/N; D4) |
| G9 | Horizon-pop threshold `k_crit=4π≈12.57` (packing floor 12) | `micro.critical_k`, `micro.packing_kmax` | T5 derived given I1-matching + I2 + stated `r_point`; downstream of `PATCH_AREA` |
| G10 | `PATCH_AREA = 4ln2` | `horizon.PATCH_AREA` | I1a+I1b matching theorem (arithmetic; I1b imported) |
| G11 | `k(M) ∝ M²` via `R_s=2M` | `horizon.k_from_mass_via_rs`, `schwarzschild_rs` | I3 INPUT (GR-consistency); BM reduction shrinks circle to `R_s=2M`, derivation open (D6) |
| G12 | LIV: quadratic-only, `E_QG,2=√8·E_P`, Fermi margins | `dispersion.eqg2_scale_gev`, `arrival_delay_s`, `fermi_quad_margin`, `linear_term_absent` | T13 derived (regular-lattice result; scalar sector; near-horizon running open) |
| G13 | Echo margin ≈158 orders | `gwdata.echo_margin_orders` | T14 null (dimensional estimate, NOT a leg S-matrix derivation) |
| G14 | J0737/B1913 PK params (`ω̇=16.899323(13)` etc.) | `pulsar.J0737`, `pulsar.B1913` | literature inputs pinned in code (CONSISTENCY-GATE only, never validation — circularity, §7) |
| G15 | Kerr–Newman area → `k_eff` | `kerr.kerr_newman_area` (patch-1 legacy units) | I3 INPUT (area only); quadrupole/`g_tφ`/ISCO/QNM open (D2, future wire) |

### §0.2 Landmines (brief's list — all VERIFIED, do not trust, did check)

- L1. `R_s = 2M` is D6-open: confirmed (`horizon.schwarzschild_rs`
  docstring "THE single GR input"; model.md I3 + D6).
- L2. Kerr quadrupole is D2-open (future wire): confirmed
  (`kerr.py` has area only; model.md D2; no `M₂=−Ma²` symbol anywhere).
- L3. Horizon-pop threshold is `micro.k_crit` (packing, downstream of
  `PATCH_AREA`): confirmed (`micro.critical_k`/`packing_kmax`; T5).
- L4. `p = 0.913 ± 0.049` is a FIT to 80 graph sims: confirmed
  (`data/p80_n1020_beta124.json`: mean 0.9134, std 0.0488, n_ok 80;
  fitted F1+F2 construction per model.md L2).
- L5. `κ→c₂` is ansatz F4 with D3 open: confirmed (power-law R² 0.91
  vs `1/r²` 0.81; cross-applied `c₂` 0.82 vs 3.14 per model.md F4;
  kill wire `p=0.92±0.056` held to N=16000).

### §0.3 Addendum-proposal claims — grounding verdicts (pre-compute)

The separate A15 proposal is NOT part of the repo. Grep over HEAD
(`k_vac|kvac|N_crit|A15|Weaire|Kelvin|13.5`, and `1.21` as a `c₂`)
returns no theoretical symbol (only coincidental literals). Verdicts:

| Claim | Grounding |
|---|---|
| A15 vacuum graph family | ABSENT → CONJECTURE; audit object only (§6), never a Phase-1 vacuum candidate (C2 tension unresolved — see §1.4) |
| `k_vac = 13.5` | ABSENT → CONJECTURE (audit: is it even the mean degree of an A15-dual construction? §6.3) |
| `c₂ = 1.21` "from the unit-cell spectral gap" | ABSENT → CONJECTURE; NO map stated → audit candidate maps (§6.1); if none yields 1.21, record UNGROUNDED |
| `p = (1/c₂)(1+1/k_vac) ≈ 0.888` | ABSENT → CONJECTURE; audit selectivity (§6.2) |
| `N_crit = 15` | ABSENT → CONJECTURE (repo `k_crit=12.57`/floor 12; 15 matches neither; no `N_crit` symbol exists) |
| D1–D6 "Closed" (renumbered) | NOT ADOPTED under any circumstance; repo D1–D9 keep `docs/model.md` §5 meanings; status changes only via §5 bars + merged tests |

Symbol collision (pre-compute fact): repo `c₂(0.913) = 0.754`
(`pulsar.c2_of_p`, F4 ansatz). Claimed `1.21` differs by 60%.
Same-quantity reading = CONTRADICTION (quantified in §6.1);
different-quantity reading = MUST RENAME the claimed object
(prereg'd rename: `γ_gap`, never `c₂`).

---

## §1. Graph families (exact builders, no tuning)

### §1.1 Phase-1 vacuum candidates (genuinely k-regular, periodic)

All builders live in `src/bh_graph/vacuum_graphs.py`, all tests in
`tests/test_vacuum_graphs.py`. Node ids are dense ints; positions and
periodic images are builder-internal. Every builder returns
`(graph, meta)` with `meta = {family, k, N, L/nc, periodic: True,
seed}`. Regularity (`deg ≡ k` on ALL nodes) is asserted in tests.

| Family | Symbol | Degree | Sizes (N) | Construction (parameter-free) |
|---|---|---|---|---|
| cubic | `C-L` | k=6 | L=4,5,6 → N=64,125,216 | `nx.grid_graph([L]*3)` + periodic wrap edges on all 3 axes |
| BCC | `B-nc` | k=8 | nc=3,4 → N=54,128 | corner + body-center sublattices on `nc³` conventional cells, periodic; edges corner↔8 nearest body-centers (`(±½,±½,±½)`) |
| FCC | `F-nc` | k=12 | nc=3,4 → N=108,256 | corner + 3 face-center sublattices, periodic; edges to 12 nearest (`(±½,±½,0)` permutations) |
| Kelvin dual (STRETCH) | `K-nc` | k=14 | nc=3,4 → N=54,128 | BCC positions + 8 nearest AND 6 second-nearest (`(±1,0,0)` permutations) edges, periodic. Rationale: Kelvin truncated-octahedron tiling has 14 faces/cell; cell centers sit on BCC sites. This is `BCC-8 PLUS cube edges`, explicitly NOT the k=8 BCC graph — the brief's non-conflation rule is enforced by separate builders + a test asserting edge-set difference |

Excluded: 2D/1D lattices (wrong dimension), random-regular (no
translation invariance → no LIV-symmetry reading), A15 (see §1.4).

### §1.2 Degree excursions (the ONLY perturbation; prereg'd, no tuning)

`vacuum_graphs.add_excursion(g, center, s)`: attach `s` NEW pendant
nodes to `center` (each pendant has degree 1; `center` degree rises
`k→k+s`; all other degrees unchanged). Prereg'd strengths:
`s ∈ {2, 4, 8}`. Centers: graph center (lexicographically middle node;
deterministic, no search) + 2 fixed-offset nodes for a within-graph
error bar (offsets +1, +7 mod N — arbitrary but FROZEN here).

Rationale: localized, exactly-quantified degree excursion; preserves
the vacuum everywhere else; pendant attachment is the minimal
topological defect (no rewiring choices to tune).

### §1.3 D3 N-scaling ladder (beyond N=1020 per kill wire)

Vacuum sizes above are N≤256 (exact-OR affordable). The D3 wire
(`p=0.92±0.056` held to N=16000) applies to SHELL graphs, not vacua —
vacuum N-scaling is reported ALONGSIDE it, not required to match it.
Scaling probe (exact OR on cubic L=4..8 → N=64..512, ≥8× span):
report `p_vac(N)` slope; bar in §5. No RunPod/GPU spend (local only).

### §1.4 A15 — excluded from Phase 1, audit object in §6 (C2 tension)

C2 (regular vacuum) requires uniform degree. The A15 dual is biregular
(12/14) by construction,の平均 13.5 is a MEAN, not a degree. Adopting
A15 as "the vacuum" would require a 2-type generalization of C2 with
P4 re-examined (site-dependent measures?) — that derivation is not
attempted here. THEREFORE: A15 appears ONLY as the object under audit
in §6 (spectral/selectivity/regularity checks), built by
`vacuum_graphs.build_a15_dual` (periodic-images Delaunay, §6.3). No
Phase-1 verdict conditions on A15. No A15 advocacy without resolving
this paragraph first — this paragraph IS the resolution (exclusion).

---

## §2. κ-computation backends

- PRIMARY: `orici.ollivier_curvature` (exact transportation LP via
  `scipy linprog`, uniform P4 measure `p=0.0`, cached Floyd–Warshall
  distances). Used for ALL verdicts. Deterministic; tolerance 1e-9.
- CROSS-CHECK (one family/size only, §5): `sinkor` Sinkhorn
  (`eps=0.05`, annealed, `max_iter=2000`) to confirm the documented
  bias direction (`κ_sink ≤ κ_exact`) holds on vacua; numbers recorded
  but NEVER used for verdicts.
- FORBIDDEN for verdicts: `e_int`-weighted measures (P4 deviation),
  subsampled neighborhoods, any backend with a tunable accuracy knob
  set after seeing results.

---

## §3. Radial profiles + fit comparison (Test ii)

### §3.1 Profile extraction (frozen)

`sell_kappa_profile_vacuum(g, center, max_shell=4)`: graph-distance
shells `r = 1..4` from `center` (BFS depth); per shell, mean exact-OR
`κ` over edges with BOTH endpoints in shell `r` (intra-shell edges;
frozen choice — radial edges cross shells and double-count). Shells
with <3 edges → NaN (excluded from fits; counts reported). Dependent
variable: `y(r) = |κ̄(r)|` (magnitude; sign reported separately —
attraction-relevant sign is negative per T8, but C1 as stated concerns
the SCALING, so magnitude is the prereg'd observable; sign flip in any
shell is reported as an exploratory flag, not a verdict input).

Minimum-data rule: fits need ≥3 finite shells; fewer → INCONCLUSIVE
for that (family, s, center) cell (reported, not imputed).

### §3.2 Three models, identical footing (2 params each)

- M-log (C1): `y = a + b·ln r` (OLS on `(ln r, y)`).
- M-pow: `y = A·r^(−p)` (OLS on `(ln r, ln y)`; `p` = Test-iii
  observable; requires `y>0` in all used shells).
- M-lin: `y = a + b·r` (OLS on `(r, y)`).

Metrics per model: R² (OLS `1−SS_res/SS_tot`), RSS, AIC, BIC with
`BIC = n·ln(RSS/n) + k·ln n`, `k=3` (2 regression + σ̂; identical
across models so ΔBIC = Δ[n·ln(RSS/n)] — reported both ways).
n = number of shells used (≤4 — small-n flagged; BIC penalty matters).

Base-specificity (exploratory, no verdict): C1 names base `k_vac`;
since `log_{k}(r) = ln r / ln k`, base only rescales `b`. Report
`b·ln(k)` (= base-`k` slope) per family: "no tuned constants" would
predict order-unity, but C1 states no slope value → NO BAR (record
only). A verdict on the base would require a slope prediction the
conjecture does not make — noted as a C1 specification gap.

### §3.3 Bar for "log emerges" (Test ii verdict)

Aggregate over the full prereg'd grid: 4 families × 3 sizes... (cubic
3 + BCC 2 + FCC 2 + Kelvin 2 = 9 graphs) × 3 strengths × 3 centers
= 81 cells (minus INCONCLUSIVE-by-data cells).

- PASS ("log emerges"): M-log wins by ΔBIC > 6 (strong evidence,
  Kass–Raftery) in ≥80% of conclusive cells AND median R²_log > 0.9.
- FAIL ("log does not emerge" — SUCCESSFUL KILL): M-log wins by
  ΔBIC > 6 in <20% of conclusive cells, OR median R²_log < 0.5.
- Else INCONCLUSIVE.
- KILL CONFIRMATION: if FAIL, the leading alternative (M-pow/M-lin by
  win fraction) is named with margins; NO rescue parameters (no fourth
  model, no per-family model switching — the bar is fixed).

---

## §4. Test (i) — κ = 0 on unperturbed vacua

Per family/size: exact-OR `κ` on every edge (N≤256 → ≤1792 edges;
affordable). Statistic: `max|κ|` and `mean|κ|`.

- PASS: `max|κ| < 1e-9` (LP tolerance) on ALL 9 Phase-1 graphs.
- INCONCLUSIVE: any graph `1e-9 ≤ max|κ| ≤ 1e-3`.
- FAIL: any graph `max|κ| > 1e-3` (report per-family values).
- A15 (§6.3) is CHARACTERIZATION ONLY (biregular → no zero prediction;
  report histogram + edge-type split, no pass/fail).

---

## §5. Test (iii) — radial exponent WITHOUT tuning + N-scaling

### §5.1 p extraction (frozen, zero free constants)

`p` comes ONLY from the M-pow OLS slope in §3.2 on the prereg'd grid.
No alternative extraction (no `k₀−c₂/r²` cross-fit for verdicts — the
F4 ansatz-dependence is the REASON cross-fits are forbidden here).
Comparison target (frozen): BU `p = 0.913 ± 0.049` (G4; band
`[0.864, 0.962]`), with the N-ladder (G5) as context.

- STRONG-PASS ("p recovered"): ≥80% of conclusive cells land in band.
- PASS: ≥1 family has ≥50% of its conclusive cells in band.
- FAIL ("p not recovered" — SUCCESSFUL KILL): ZERO families pass.
- Else INCONCLUSIVE.
- "Without tuning" audit: the ONLY numbers set by us are prereg'd
  above (s ∈ {2,4,8}, shells 1..4, intra-shell edges, exact OR) —
  none chosen to match 0.913 (no BU-profile peeking in builder code;
  builders take no exponent input — enforced by code review + test
  asserting builder signatures contain no `p`/`beta`/`c2`).

### §5.2 N-scaling (D3 context)

Cubic L=4..8 (N=64..512): per-N median `p_vac` over the 9
(s, center) cells. Report slope `d p / d ln N` + 95% CI (OLS).
NO BAR (vacuum class ≠ shell class; the D3 kill wire binds shell
graphs). Purpose: detect drift that would disqualify any future
"vacuum explains BU-p" claim (a drifting `p_vac` cannot be THE
explanation of a stable BU `p`).

---

## §6. Addendum prereg (A15/k_vac=13.5/c₂=1.21 probe)

### §6.1 SPECTRAL CHECK

**Construction.** `build_a15_dual(nc)`: 8-site A15 basis at
conventional fractional coords — A: (0,0,0), (½,½,½); B: (¼,½,0),
(¾,½,0), (0,¼,½), (0,¾,½), (½,0,¼), (½,0,¾) — tiled `nc³` cells
(`nc ∈ {2,3}` → N=64,216), periodic-images Delaunay
(`scipy.spatial.Delaunay` on 27-replica cloud, central-block edges
kept, image endpoints mapped to central representatives;
PARAMETER-FREE — no distance cutoff). Controls: cubic/BCC/FCC/Kelvin
builders from §1.1 at matched N where possible.

**Spectrum.** Normalized Laplacian `L_sym = I − D^(−1/2) A D^(−1/2)`
(dense `eigvalsh`; N≤256 affordable). Record full spectrum +
`λ₁` (smallest nonzero) + `λ_max` + gap ratio. BC note (prereg'd):
finite periodic graphs have `λ₁ > 0` with `λ₁ → 0` as N→∞ (infinite
lattice: `λ₁ = 0`); single-cell "gaps" are BC artifacts. THEREFORE any
gap→constant map needs a thermodynamic-limit prescription the proposal
does not give — size-dependence of `λ₁` across `nc` is itself a
falsifier of "gap yields universal 1.21".

**Candidate maps** (exhaustive audit of standard readings; the proposal
states NONE, so we test the plausible family — if the proposal meant an
unstated seventh map, it must state it; absence = UNGROUNDED):

- M1: `γ = 1/λ₁` · M2: `γ = λ₁` · M3: `γ = 1/√λ₁` ·
  M4: `γ = −ln λ₁` · M5: `γ = 2/λ₁` · M6: `γ = ⟨k⟩·λ₁/2`

(each evaluated on A15 `nc=2,3` + single open cell N=8; "yields 1.21"
= within ±5% i.e. `[1.15, 1.27]`).

- VERDICT: if NO (map, size, BC) yields 1.21 → `c₂ = 1.21`
  recorded UNGROUNDED (and the infinite-lattice `λ₁=0` argument makes
  ANY gap-map size-dependent → cannot be universal without a stated
  limit prescription). If some (map, size) hits — report it as
  POST-HOC (map chosen after seeing the answer) + demand the proposal
  preregister that map and re-hit at a HELD-OUT size.

**Symbol collision** (decided pre-compute, quantified in report):
repo `c₂ = c₂(p) = p(2p−1)` (F4 ansatz; 0.754 at BU p). `|1.21 −
0.754| = 0.456` ≈ 9× the BU-`p`-propagated `σ(c₂) ≈ 0.05`
(`dc₂/dp = 4p−1 ≈ 2.65` at 0.913; `σ = 2.65×0.049/√80`? — report
computes both per-graph and SEM-propagated). Same-quantity reading:
CONTRADICTION at >>5σ. Different-quantity reading: proposal's object
is RENAMED `γ_gap` everywhere in our report, never `c₂`.

### §6.2 SELECTIVITY AUDIT

Formula (proposal's): `p̂(k) = (1/1.21)·(1 + 1/k)`. Frozen band:
BU `[0.864, 0.962]` (G4 ±0.049; per-graph σ, the proposal's own
comparison). Compute `p̂(k)` for integer `k ∈ [6,22]` + `k=13.5`;
report hit fraction + implied k-range (solve band edges).

- BAR: if >50% of integer `k ∈ [6,22]` land in band → formula is
  NON-SELECTIVE → "not evidence FOR A15" (explicit report sentence).
- COROLLARY (pre-compute): with repo `c₂=0.7728`, `p̂(k) =
  1.294·(1+1/k) ∈ [1.35, 1.51]` — entirely OUTSIDE the band →
  formula+repo-`c₂` inconsistent (symbol-collision consequence).
- No fitting, no error bars on `p̂` (deterministic formula); band edges
  frozen.

### §6.3 REGULARITY CHECK

On A15-dual (`nc=2,3`) vs regular controls (§1.1):

- R1 degree histogram: exact counts; regulars must show `Var(deg)=0`
  (test-asserted); A15 expectation (proposal's own numbers): masses at
  12/14, mean 13.5 — VERIFY (tolerance: mean ±0.5, modes ∈ {11..13} /
  {13..15} allowing Delaunay degeneracy; else report actual).
- R2 P4-transport uniformity: random-walk stationary `π_x = deg(x)/2E`;
  TV distance `‖π − uniform‖₁/2` (=0 iff regular). Report per graph.
- R3 unperturbed-κ uniformity: exact-OR histogram; regulars → §4 bar;
  A15 → report edge-type-split means (12–12, 12–14, 14–14 edges) +
  spread.
- R4 LIV relevance: the T13 linear-term absence rests on `k↔−k`
  symmetry (translation invariance). A15-dual is CELL-periodic →
  symmetry survives at cell level (analytic point, no computation
  needed); biregularity affects ISOTROPY/higher-order only. Report:
  (a) translation-invariance status per family (yes/yes/yes/yes/A15-cell);
  (b) degree-anisotropy proxy = `max−min` hopping-coordination seen by
  a wavepacket = `max deg − min deg` (0 vs 2). NO claim that A15
  violates Fermi bounds (it doesn't, by the same symmetry) — the
  regularity failure is about C2/P4 justification, not LIV exclusion.
  Verdict labels: CHARACTERIZATION (no pass/fail; the C2 verdict is
  §1.4's exclusion, already decided in writing).

### §6.4 LEDGER INTEGRITY (non-negotiable, no bar needed)

Repo D1–D9 keep `docs/model.md` §5 meanings. The proposal's renumbered
D1–D6 "Closed" stamps are NOT adopted under ANY circumstance —
including a hypothetical full PASS (a PASS would open a NEW derivation
claim with its own review, never a bulk status flip). NOTHING moves
status without meeting its prereg'd bar + merged tests. The report
carries a one-line-per-D-item ledger table (all OPEN unless a §3–§5
STRONG-PASS + review says otherwise — and even then, only the
specifically-derived item).

---

## §7. Phase 2 — gated protocols (run ONLY as specified)

GATE RULE: B runs only as CONSISTENCY-GATE (label mandatory); A and C
are pre-grounded null-checks and may run regardless (mock-first,
frozen statistic, then literature-data comparison). NO new data fetches
beyond repo-pinned constants + published numbers quoted with sources;
no TOA re-timing; no Bilby PE; no overtone claims; the word "confirm"
is FORBIDDEN without a prereg'd bar (use NULL-HELD / CONSISTENT /
INCONCLUSIVE).

- **A. LIV null** (frozen statistic: `arrival_delay_s(31 GeV,
  D_GRB090510)` vs Fermi published bounds). Mock: toy `(10 GeV,
  3 Gpc)` → expect `~1e−20 s` (T13). Real: 31-GeV photon
  (GRB 090510 highest-energy; Abdo+2009) at `z=0.903` (`D≈2.8 Gpc`
  comoving → light-travel `≈9.1e25 m`; repo uses Mpc input —
  convert explicitly). FALSIFICATION BAR (prereg'd): model FAILS iff
  predicted 31-GeV delay EXCEEDS the published Fermi upper bound
  (Abdo+2009: `Δt < 0.859 s` conservative / spectral-lag analyses;
  quote exact bound used). Expectation (T13): delay `~1e−19 s` →
  NULL-HELD by ~18 orders. Label: NULL-CHECK, never VALIDATION.
- **C. Echo null** (frozen statistic: `echo_margin_orders(100 Hz)`
  ≈ 158). BAR: NULL-HELD iff margin > 10 orders (LVK O3 nulls
  consistent); FAIL iff margin < 2. Quote LVK sources (O3 BayesWave +
  template searches per `gwdata` docstring). No PE. Label: NULL-CHECK.
- **B. 2PN gate** (Double Pulsar PUBLISHED PK only): `invert_mass_msun`
  + `sin_i_from_x` on repo-pinned J0737 (values match Kramer+2021 to
  quoted precision — VERIFY first decimal places against the paper's
  published numbers as available offline; if offline, label "repo-pinned
  PK, source Kramer+2021 per code comment"). BAR: GATE-PASS iff
  `ω̇` residual < 1σ AND `sin i` residual < 1σ at `p=0.92`
  (`test_resuscitated_passes_dot_and_s` already pins this — the gate
  RE-RUNS it on the branch). Label: CONSISTENCY-GATE, never VALIDATION
  (circularity: graph-fit → GR-matching ansatz → pulsars-confirm-GR).

---

## §8. Amendments (post-compute edits logged here, never silent)

(None yet.)
