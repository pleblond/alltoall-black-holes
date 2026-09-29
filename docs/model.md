# The model, stated first (v0.6)

**Status:** draft, model-first companion to the v5 paper. No new physics, no new
numbers: every value below is quoted from `paper/v5/main.tex`,
`paper/v5/supplement.tex`, `docs/DEFERRED.md`, the cited `src/bh_graph/`
module, or committed `data/` artifacts. Where the code and the paper disagree,
the code wins and the disagreement is flagged.

**v0.2 audit release.** Every symbol → module → test citation resolved; every
load-bearing literal recomputed or test-pinned (suite: 398 collected,
396 passed, 2 torch/GPU-only skipped); kill wires aligned across paper,
protocol, and code. Fixes vs v0.1: TeV absolutes corrected to post-BS values
(v5 prose preserves pre-BS numbers with identical ratios — flagged
paper-side), Kerr leg normalization stated explicitly, `pheno` restored to the
module map, D-tag collision disambiguated. Two code-side flags (comment-only
notes added, zero behavior change): `evaporate()["radius"]` legacy convention,
`kerr_newman_k` patch-1 units. See §8 provenance layers and §9.

**v0.3 imports-hardening release.** No number changes: import surgery only.
I4 splits into equipartition (I4a) and Bekenstein displacement (I4b); I6
splits into the heat-kernel bridge (I6a, cited, load: none), the
Ollivier–Ricci limit (I6b, load-bearing, now with its measure postulated in
new L0 postulate P4), and the Raychaudhuri open bridge (I6c → new DEFERRED
item D9). I3 gains the BM reduction theorem stated exactly. Import IDs are
otherwise stable; see §9.

**v0.4 I1-matching release.** No number changes: I1 splits into the saturation
postulate (I1a, `η_vN = ln2` by definition, toy-motivated by BN) and the
thermodynamic import (I1b, `S = A/4`), with the patch `4ln2` as a stated
matching theorem (pure arithmetic, equipartition reading included with the
nat/bit units corrected). Postulate B stays retired with one clarifying
sentence; the s-leg falsifier now tests I1a directly; I6c's Jacobson
conclusion is guarded given-I1b. Import IDs otherwise stable; see §9.

**v0.5 vacuum-kinematics release.** No number changes:
L0 kinematics clarification only. Adds explicit vacuum state P0 (perfect
all:all, defined before P1), formalizes the observer reconstruction map
`M_O` of which P4 is one instance, and names the three dimensions
`d_G / d_I / d_obs` with the `d_eff(r) = d ln V / d ln r` measurement
protocol (`emergent_dim` module + tests). T1 gains the corollary that spatial
distance must be derived from information-access, not adjacency. I6a/b are
restated as given-L0-vacuum-plus-`M_O` conditionals; D3/D4/D6 gain an explicit
close-route via the `d_eff -> 3` IR test. See §1–§3, §5–§6 deltas.

**v0.6 relaxed-vacuum release.** No number changes:
vacuum postulate flip + consequences. P0 (all:all) is retired as the vacuum
definition and replaced by P0' (relaxed isostatic 2D fabric, `<z> = 4`;
`K_N` interiors re-labeled as the maximum-tension extreme, T1–T3 untouched).
Adds the tension spectrum, the `d_I = 2` vacuum prediction, the only-vacuum-
is-perfectly-3D conjecture with its GR-side fingerprint, new DEFERRED item
D10 (simulator d-dip + tension→`κ` map), the D10a tense-plug pin (bare
shortest-path inverted vs GR, rejected as `d(i,j)` for tense regions;
D10b costs gate D10a), and the companion essay
`docs/relaxed-vacuum.md` (full explanation). L0 theorems, L1 imports, L2
calibrations unchanged; import IDs stable.

**What this document is:** the definition of the model — primitives, postulates,
theorems, calibrations, open maps, and non-claims — in that order. Tests,
figures, and measurements are cited as *evidence about* the model, never as its
definition.

**What this document is not:** a tutorial (see `docs/model-explained.md`), an
observation plan (see `docs/observation-protocol.md`), or the paper (see
`paper/v5/`). It does not re-derive anything; it states what is assumed, what
follows, and what is still missing.

**How to read it:** three layers, in hardening order.

- **L0 — Graph kinematics.** The robust core. Almost everything here is a theorem
  of the wiring, not a fit.
- **L1 — Spacetime interface.** The robust core plus a small list of explicit
  imports from GR/thermodynamics. All weak-field gravity and QI results live here
  *conditionally* on those imports.
- **L2 — Compact-object phenomenology.** Calibrated, not core. Fitted numbers,
  a solved weight, one ansatz map, and one extrapolation prescription. Killing L2
  must not kill L0/L1.

Open derivations (D1–D8 in `docs/DEFERRED.md`) are fenced in §5 and referenced
from the exact postulate or theorem they would promote. Nothing in §2–§4 depends
on them silently.

Conventions: Planck units `G = c = 1` unless stated; `l_p` written explicitly at
physical interfaces. `N` = interior node count, `k` = exterior leg count,
`e_int ∈ [0,1]` = interior entanglement fraction, `e_ext ∈ [0,1]` = exterior
budget fraction. Status words follow the S1 audit: **input** (assumed),
**fit** (calibrated), **measured** (output of code), **derived** (follows from
stated premises).

---

## 1. Primitives (L0)

These are undefined terms. Everything else is built from them.

| Symbol | Meaning | Notes |
|---|---|---|
| node | indivisible Planck-scale element | lives at `~1e-35` m; no internal structure |
| edge | unit of entanglement between nodes | cut edge-count bounds entanglement entropy across the cut |
| `G` | the information graph `(V,E,I)` | no coordinates; see P0'; `G_N` and ambient graph are subgraphs of `G` |
| `G_vac` | vacuum information state | relaxed isostatic 2D fabric; defined in P0' (v0.6) |
| `z` | mean coordination (edges per node) | `4` in vacuum; tension dial (v0.6) |
| `G_N` | interior graph on `N` nodes | the object under study; boundary between interior and ambient is the cut |
| ambient graph | the rest of the network | exterior legs terminate here; one realization of `G_vac` with excitations |
| `M_O` | observer reconstruction map | restricted coarse-graining / information-access channel; P4 is one instance (v0.5) |
| `d(i,j)`, `B(r)`, `V(r)`, `d_eff` | info-transfer distance, ball, capacity, effective dimension | `d_eff = d ln V / d ln r`; see §1 dimensions box (v0.5) |
| `d_G`, `d_I`, `d_obs` | microscopic / information / observed dimension | distinct in general; `d_obs -> 3` is the IR conjecture (v0.5) |
| `k` | exterior leg count (edges crossing the cut) | the model's central quantity; `k << N²` for black holes |
| `e_int`, `e_ext` | interior / exterior entanglement fractions | normalized wiring budgets; see P3 |
| `K_max` | max exterior budget (normalization) | toy-level; physical predictions must be `K_max`-independent where claimed |
| `m_x` | neighborhood measure at node `x` | canonical form postulated in P4; the only measure any theorem uses |
| `H_graph,k`, `H_leg` | graph / leg Hilbert spaces | used only where unitarity is explicitly constructed (qubit toy, see T7); no general graph Hamiltonian is postulated |

What is **not** primitive: mass, radius, temperature, metric, area, coordinates.
Those enter in L1 as interface maps, each labeled. In particular no `(x,y,z)`
is assigned to nodes of `G` at L0 (v0.5).

### Dimensions box (v0.5). Three notions of dimension, kept separate.

- `d_G` — microscopic graph dimension: whatever dimension (if any) describes
  the raw information network. For `K_N`, trivial (diameter 1, T1).
- `d_I` — information dimension: reconstructed from information-transfer /
  entanglement scaling.
- `d_obs` — observed spatial dimension: reconstructed by macroscopic observers
  via `M_O`.

Definitions (measurement protocol, `emergent_dim`):

```
d(i,j)   = f(information-transfer cost_ij)   # NOT shortest-path adjacency on K_N
B(r)     = {j : d(i,j) <= r}
V(r)     = information capacity of B(r)       # node count proxy; see module
d_eff(r) = d ln V(r) / d ln r
d_obs    = lim_{r -> IR} d_eff(r)  ~=  3  (conjecture)
```

The microscopic value `d_G` is not set to 3. The model must calculate
`d_eff(r)` and exhibit an IR fixed point at 3 without imposing 3. Shortest-path
distance is the documented failure mode on `K_N` (always 1); the supported
`d(i,j)` instances are effective resistance / commute-time, diffusion, and
communicability distances (see `emergent_dim.info_distance_matrix`).

**v0.6 prediction.** P0' predicts `d_I = 2` for the vacuum fabric itself
(2D wiring, measured by the same protocol); `d_obs = 3` then requires the
2D + scale → 3D reconstruction (radial × area = volume). The relaxation
principle lives on `G` (coordination → 4), never on spacetime: optimizing
`M_O(G)` cannot change `G`, and "relaxed spacetime" would smuggle flatness
in as the target. Full explanation: `docs/relaxed-vacuum.md`.

---

## 2. L0 postulates and theorems

### P0' (vacuum postulate, v0.6). The vacuum is the most relaxed state that is still a fabric: isostatic 2D, four edges per node.

`G_vac = (V,E,I)` is the homogeneous 2D entanglement fabric with mean
coordination `<z> = 4` — no coordinates, no distinguished node, direction,
location, boundary, or macroscopic excitation. "Most relaxed" is Maxwell
marginal rigidity: `N` nodes in 2D have `2N` degrees of freedom, `M` edges
impose `M` constraints, and `<z> = 2M/N = 4` is the unique rigid-with-zero-
self-stress point (floppy below, stressed above). Black-hole interiors `G_N`
(P1) are the **maximum-tension extreme** (degree `N−1`), maximally far from
vacuum; stars, planets, and Casimir cavities live on the tension spectrum
between them. Curvature is self-stress: over-coordination (`z − 4`)
reconstructed through `M_O` (quantitative map open, D10). An observer never
sees `G` directly; an observer sees `M_O(G)` where `M_O` is a restricted
coarse-graining / information-access channel (see P4 box). Objective
spacetime is defined as the part of `G`'s information structure invariant
under all admissible `M_O`.

History: v0.5 P0 defined vacuum as perfect all:all (maximally connected,
minimally distinguished). That put black holes — the most extreme objects —
*closest* to vacuum, which reads backwards; P0 is retired as the vacuum
definition (kept in git history) and replaced by P0'. Homogeneity ("no
distinguished node/relation") survives unchanged; only the wiring density of
the homogeneous state changed (sparse-rigid 4, not dense-complete `N−1`).
T1–T3 are untouched: they were always statements about the tense extreme.
Full explanation: `docs/relaxed-vacuum.md`.

### P1 (wiring postulate). Black-hole interiors are almost-perfect all:all graphs.

The interior `G_N` is the complete graph `K_N` up to a sparse exterior:
`N(N-1)/2` internal edges, `k << N²` exterior legs. "Almost" is the entire
observable content: area, temperature, and radiation live in the failure to be
perfect. (`graphs`, `scrambling`.)

### P2 (edge postulate). An edge is a unit of entanglement; cut size bounds entropy.

Entanglement across any cut is bounded above by the edge count across it.
No specific state is postulated at L0; specific families appear only as
witnesses for monogamy (see T3).

### P3 (monogamy postulate, two versions).

- **Linear toy** (used for bookkeeping): `e_int + e_ext ≤ 1`. Remaining legs
  `k = K_max(1 − e_int)`. (`horizon.monogamy_frontier`, `exterior_budget`.)
- **Exact frontier** (the real constraint): the Coffman–Kundu–Wootters inequality
  `τ_A|BE − C²_AB − C²_AE ≥ 0`, verified on a 25-point grid on the explicit
  state family `|ψ(θ)⟩ = cosθ|Φ+⟩_AB|0⟩_E + sinθ|00⟩_AB|1⟩_E`. The exact frontier
  lies strictly below the linear bound (e.g. `x + y = 0.70` at `t = 0.3`; exterior
  one-tangle peaks at `0.5`, not `1`). (`monogamy`.)

At `e_int → 1`, `k → 0`: the subgraph decouples as a closed graph — the
**baby-universe limit**. Black holes live in the almost-perfect corner
`e_int ≲ 1`, small nonzero `k`. (`horizon.is_baby_universe_limit`.)

### P4 (canonical measure postulate). Neighborhood measures are uniform with idleness zero.

Ollivier–Ricci curvature `κ(x, y) = 1 − W₁(m_x, m_y)/d(x, y)` is always computed
with `m_x` uniform over the graph neighbors of `x` and zero self-mass
(`orici._neighborhood_measure` default `p = 0.0`; used by `weakfield` and the
gradient-shell measurements). Justification, in order: (i) the continuum
theorems by which Ollivier curvature recovers Ricci assume the uniform
measure; (ii) the tested alternative — `e_int`-weighted same-shell/cross-shell
measures — degrades the L2 fit (`p`: `0.94 → 0.84` at `e_int = 0.9`, `0.78`
at `0.99`), so the canonical choice is both principled and required. What is
postulated is the *choice*; the curvature values themselves are measured.
Discharge condition: derive the measure from graph dynamics, or exhibit an
alternative measure preserving the T8 sign and the L2 `p` (related: D1, D3).

**v0.5 observer box.** P4 is one explicit instance of the observer
reconstruction map `M_O` from P0': physical distance is not adjacency, it is
`d(i,j) = f(information-transfer cost_ij)` as reconstructed through `M_O`.
The `0.94 → 0.84` degradation is evidence *about* which `M_O` the L2 fit
selects, not a definition of `M_O`. Promoting P4 to derived means exhibiting
the `M_O` (measure + distance + coarse-graining) that gives `d_eff -> 3` and
negative radial `κ` without tuning.

### T1 (no interior distance). `K_N` has diameter exactly 1 at every `N`.

Mean distance 1, spectral gap `N`. Deterministic SI/operator spread covers `K_N`
in 1 step for any `N`, versus `~N/2` for a chain `P_N`, `~2√N` for a
`√N×√N` grid, and `~log N` for a random 3-regular expander. **Derived**, zero
tuning. (`graphs`, `scrambling`.)

**v0.5 corollary.** T1 shows spatial distance must be derived from
information-access, not adjacency. The complete graph — the P0' tension
extreme — is fundamentally
non-geometric while producing a geometric exterior via `M_O` (P0'/P4 box).
Graph distance is the documented failure mode (`d = 1` everywhere on `K_N`);
physical distance is `d(i,j) = f(information-transfer cost)` reconstructed
through `M_O`. Light / information inside `K_N` is 1 step; what we call `c`
outside is egress through the `k << N²` bottleneck given monogamy and
congestion (see T8–T11 `c_eff`). (`emergent_dim` pins the failure and the
supported distances.)

### T2 (fast scrambling). Finite-speed circuits give `t_* ~ log N` on all:all.

One 2-qubit interaction per qubit per step with random perfect matching
(all:all) versus dimer covering (chain) and per-encounter success `p` gives
`t_*(N) ≈ log₂N / log₂(1+p)`, exactly `log₂N` at `p = 1`, versus ballistic
`t_* ~ N/v` on the chain. Measured over 25 trials per `N`, `N = 8…128`; the
chain is already `> 5×` slower at `N = 64`. OTOC form `C(t) ~ e^{λt}/N`,
`t* = logN/λ`. **Derived** from P1 plus the stated circuit rule.
(`circuits`, `otoc`, `krylov`, `syk`, `bigsyk`, `sparse24`.)

### T3 (decoupling). Maximal interior entanglement forces exterior decoupling.

At `t = 0` the witness family has interior concurrence 1 and exterior tangle 0
(baby-universe endpoint); at `t = π/2` it is fully product `(0,0)`. This is a
theorem of quantum mechanics applied to the wiring, not an extra postulate.

### Explicitly not in L0.

No Hamiltonian, no graph dynamics, no Lorentz invariance, no mass map, no
continuum limit. Any result needing those lives in L1 or L2 and says so.

---

## 3. L1: the spacetime interface

L1 adds a short list of imports. Everything in this section is of the form
"**given** L0 + imports I1–I7 (I1, I4 and I6 split into independently
dischargeable parts), **then** T4–T14." The imports are the price;
the theorems are what the price buys.

### Imports (inputs, all labeled)

| ID | Import | Status | Source |
|---|---|---|---|
| I1a | Saturation postulate: exterior legs are saturated cut edges, hence `η_vN = ln2` nats/leg by definition of saturation; `S = k·ln2` | **postulated** (toy-motivated: BN `S/k` constancy `< 0.8%`, mean `ln2`) | `jacobson`, `qes`, S1 |
| I1b | Thermodynamic import `S = A/4` (`G = ℏ = c = 1`); matching gives `A(k) = 4ln2·k·l_p²`, `R(k) = √(A/4π)` | **input** (imported); the `4ln2` itself is arithmetic (matching theorem below) | `horizon`, S1 |
| I2 | Embedding rule: `k` legs need `k` Planck patches of ambient surface; interior size `N` buys no area | postulate (Bekenstein–Hawking / LQG-puncture picture in graph language) | `horizon`, `micro` |
| I3 | Mass map `k(M) = A/4ln2·l_p² = (4π/ln2)M²/l_p² ∝ M²` (Schwarzschild units), i.e. `k = 1.51e77(M/M☉)²` | **input** (GR-consistency, not derived). BM reduction: given the I1 matching (patch) + sphere geometry, `k(M)` is fixed iff `R_s(M)` is given; the circle is shrunk to the single statement `R_s = 2M`, whose derivation from wiring is open (D6) | `horizon.k_from_mass_via_rs`, `data.k_schwarzschild_sun`, S1 |
| I4a | Equipartition over Planck bits: `E = M₁ = NT/2`, `N = k·PATCH` → `T(r) = M₁/2πr²` | **input** (postulated) | `entropic.screen_temperature`, S1 |
| I4b | Bekenstein displacement: moving `M₂` by `dr` changes entropy by `dS = 2πM₂dr`; force `F = T·dS/dr` | **input** (postulated) | `entropic.entropy_gradient`, S1 |
| I5 | Equivalence principle (Newtonian potential → `g_00`, redshifts) | **input** (postulated) | `redshift`, S1 |
| I6a | Heat-kernel bridge: graph `a₁` → `∫R` identification | cited, not proved (curvature read relatively, weighted-minus-flat); load: none — AU supporting evidence only | `heatker`, S1 |
| I6b | Ollivier–Ricci → Ricci continuum limit, with the P4 uniform measure | **input** (postulated); load-bearing for the T8 sign and the L2 `p` | `orici`, `weakfield`, S1 |
| I6c | Raychaudhuri (focusing) for leg bundles + Jacobson-chain inputs (`T = κ/2π`, Clausius `dQ = T·dS`, `dS = ln2·dk` saturated) | open bridge (D9); load: only the "Einstein equations follow" conditional, stated given I1b (no double-counting of `η = 1/4`) — T8–T11 do not depend on it | `jacobson`, S1 |
| I7 | Gap coefficient, crossover scales (`r_point`, `α = 1` congestion calibration, `A_min`) | heuristic / calibrated (see T6, T9) | `micro`, `redshift`, S1 |

**v0.5 restatement.** Given L0 vacuum P0' + `M_O` = P4 uniform measure, then
Ollivier–Ricci sign = attraction T8. Promoting I6 to derived = exhibiting an
`M_O` (measure + info-transfer distance + coarse-graining) that gives
`d_eff -> 3` in the IR and negative radial `κ` without tuning. I6a stays
cited/load-none; I6b stays the load-bearing input; I6c stays the D9 open
bridge. Curvature in this language is failure of information neighborhoods
`V(r)` to scale uniformly; matter changes info structure, `M_O` reads it as
`R_μνρσ`.

### The I1 matching theorem (patch from saturation + thermodynamics).

**I1a (saturation postulate).** An exterior leg is a single edge crossing the
cut between `G_N` and the ambient graph. By P2, cut entropy is bounded above by
the crossing-edge count; the legs are postulated saturated, so each contributes
exactly one independent bit: `η_vN = ln2` nats/leg *by definition of
saturation*. Motivation (not proof): BN measured `S/k` constancy (`< 0.8%`)
with mean `ln2` in random-star tensor networks
(`jacobson.eta_constancy_deviation`, `eta_measured`). A horizon of `k`
independent saturated legs then carries `S = k·ln2`.

**I1b (thermodynamic import).** `S = A/4` (`G = ℏ = c = 1`), the
Bekenstein–Hawking relation by which the Einstein equation emerges from
thermodynamics.

**Matching (theorem, pure arithmetic).** Equating the two expressions for `S`:
`k·ln2 = A/4`, hence `A = 4ln2·k`, i.e. `A(k) = 4ln2·k·l_p²`. Each saturated
leg is assigned a surface element of `4ln2·l_p²`. Equipartition reading (same
result): `S = A/4` counts nats, so the area per nat is `4l_p²`; a leg carries
`ln2` nats, hence `4ln2·l_p²` per leg. (Note: I4a's "Planck bits" are
energy-sharing degrees of freedom, a distinct counting from I1a's entanglement
nats — compatible, not identical.)

**Status.** `ln2` follows from the definition of a saturated edge (postulated
in I1a, toy-motivated by BN); `S = A/4` is imported (I1b); `4ln2` is the
arithmetic consequence. Nothing here comes from pure graph kinematics: the
matching is part of the model's definition of how legs interface with continuum
geometry. Postulate B stays retired: its ¼-nat legs are replaced by saturated
`ln2` legs, and the ¼ now appears only as the *area* coefficient, as output —
which is also why I6c's Jacobson conclusion is stated given I1b. The s-leg
falsifier (`s_leg ≤ l_p²/4` in any physical state class) tests I1a directly.

### The BM reduction theorem (I3, stated exactly).

Given the I1 matching (patch) + sphere geometry (`A = 4πR²`), the mass map factors
entirely through the radius map:

`k(M) = 4π·R_s(M)² / PATCH_AREA·l_p²` — i.e. `k(M)` ⟺ `R_s(M)`.

So `k(M) ∝ M²` holds iff `R_s(M)` is supplied; the circle is exactly the
single statement `R_s = 2M` (derivation open, D6). Pinned in code:
`k_from_mass_via_rs(1.0) = 4π/ln2`; a wrong radius law gives the wrong legs
(`R_s = 3M` → `36π/PATCH`); the Schwarzschild entry point is backward-compatible
(`test_reduction_theorem`). (`horizon.k_from_mass_via_rs`.)

Consequences of I1–I3 worth stating plainly:

- Adding interior nodes without exterior legs changes nothing observable from
  outside. The horizon is an *empty routing buffer*.
- Mass enters only indirectly, through I3. "Massive ⇒ large" is a derived
  statement about wiring budgets, not bulk volume.
- Kerr–Newman enters only as `A(M,a,Q) = 4π(r+²+a²)` with
  `r+ = M+√(M²−a²−Q²)` setting `k_eff = A/4ln2` (**input**). Spin orders legs
  smoothly: extremal Kerr carries exactly half, extremal Reissner–Nordström
  exactly one quarter, the Schwarzschild budget at fixed `M` (patch-independent
  ratios). Normalization (audit v0.2): `kerr.kerr_newman_k` returns `A/lp²`
  (patch-`1` units, exactly `PATCH_AREA`× the matched I1a+I1b leg count) and is consumed only
  by a monotonicity test; absolute leg counts use `data.k_schwarzschild_sun`.
  `kerr_newman_k` is a legacy patch-1 area convention, not the normalized leg
  count — it must not be used as an absolute `k` without dividing by
  `PATCH_AREA` (rename queued as future housekeeping, no behavior change here).
  Nothing else about Kerr is assumed here — and nothing else about Kerr
  is claimed (see §5/D2).

### T4 (area law). Horizon area counts exterior legs, independent of `N`.

`A(k) = 4ln2·k·l_p²` by the I1 matching; `R(k)` follows. Evaporation shrinks the horizon even
if `N` stays fixed: wiring-only (`N` const) and standard (`N` shrinks with `k`)
give identical `A(t)`. **Derived** given the I1 matching + I2. (`horizon`, `evaporation`.)

### T5 (micro-hole pop). Pointlike below `k_crit`, horizon above — discontinuously.

A point region of radius `r_point` embeds `k` legs without a surface while
Planck-density packing succeeds:

```
R_obs(k) = r_point                          k ≤ k_crit
         = √(4ln2·k·l_p²/4π)                k > k_crit
k_crit   = 4π·r_point² / 4ln2·l_p²
```

Default `r_point = √(4ln2)` (one leg cell, Planck units). Packing theorem (BK):
given the I1 matching, no embedding exists for `k > ⌊4πr_foot²/4ln2·l_p²⌋` — the pop is
forced. With an LQG-style minimal-area gap, area is `0` below threshold and
`≥ A_min` above: no 0.2-Planck-area hole. **Derived** given the I1 matching + I2 plus the
stated `r_point`. (`micro`: `critical_k`, `is_pointlike`, `packing_kmax`,
`pop_forced`, `embedding_radius`, `quantized_area`.)

### T6 (island-like turnover). Two-saddle competition crosses iff legs are rich enough.

`S_no = k·s_leg` versus `S_isl = k·ln2·l_p² + max(S₀ − k·s_leg, 0)` cross at
`k_page = S₀/(2·s_leg − ln2·l_p²)`, which exists iff `s_leg > ln2·l_p²/2`
(BS form: `> PATCH/8`). Saturated vacuum legs (`s_leg = ln2`) give
`k_page = S₀/ln2`. A discrete min-cut analogue (all:all core + `k` leg
capacities) mirrors the jump. **This is a two-saddle competition plus a min-cut
analogue — not** `S_gen = A/4G + S_matter` extremized from a gravitational path
integral. Genuine QES extremization and the graph-dynamics evaporation isometry
are open (D1). (`qes`, `micro`.)

### T7 (Page curve, scoped). Leg surgery reproduces Page with Haar-typical fluctuations.

Imposed surgery `k → k−1` per step gives `S_rad = min(t, N_eff − t)` with the
exact Page dip `0.72` bits and Haar-typical spread, identically in wiring-only
and `N`-shrinking modes. Scope, stated exactly:

- **Imposed**: the `min()` curve in `evaporation` (honest toy).
- **Done**: the qubit-toy unitary completion `evaporation_unitary` — per-step
  `V_t` with `V_t†V_t = I` verified (including a composed-map inner-product
  test), `S_rad` computed from `ρ_rad` (tracks Haar/Page to `0.002` bits at
  `N = 8`), finite-depth all:all circuits converging to Page by depth `~5`/step
  without assuming Haar.
- **Open**: the graph instance `V_k: H_graph,k → H_graph,k−1 ⊗ H_leg` derived
  from graph dynamics (D1). "Page curve is a theorem of graph dynamics" is the
  close criterion, not the current claim.

QEC mirror: recovery error `err(k) = min(1/2, 2^{N/2+1−k})` reaches 99% at
`k ≥ N/2+1+log₂100`, sealing at `k → 0` (Hayden–Preskill primitive).
(`evaporation`, `evaporation_unitary`, `haar`, `qec`, `kerrpage`.)

### T8 (Newton + Kepler + sign). `F = M₁M₂/r²` by exact algebra given I4a+I4b, orbits close, attraction signed.

Leg screens + I4a+I4b give `F = M₁M₂/r²` by exact multiplication of the chain
(`T·dS/dr`, pinned with `==` in `test_chain_multiplies_to_newton`); the fitted
log-log slope verifies to `1e−9` numerically, with
closed leapfrog orbits and `T² ∝ r³`. Raw link-flux scales as channels
(`∝ 1/r²`) and would give `1/r³` as energy; the temperature factor over the
`r`-dependent screen corrects it to `1/r²` — both implemented so the
distinction is checkable. Ollivier–Ricci curvature is radially negative in
every tested configuration, attachment mode, and seed: the sign of attraction,
zero tuning (I6b with the P4 measure). Micro-walks alone do **not** give Newton (persistent walks yield
drift `∝ 1/r³`, slope `≈ −3`; every smooth weight rule stays cubic, no-go
`−2.99`; `μ(χ)` fluctuation escape to `−1.95 ≈ −2` is modulo the labeled `√χ`
assumption). Conclusion: temperature (AS), not bare graph diffusion, carries
Newton. **Derived** given I4a+I4b. (`entropic`, `weakfield`, `perwalk`.)

### T9 (redshifts + freezing). GPS and Pound–Rebka with no new parameters.

I3's potential plus I5 give `z = M(1/r₁ − 1/r₂)`: GPS `+5.29e−10`,
Pound–Rebka `2.55e−15` over 22.5 m. Congestion fronts give tortoise-like
freezing (`c_eff → 0`); `α = 1` matches Schwarzschild coordinate light speed
`dr/dt = 1 − R_s/r` **exactly** (calibration); `α = 2` is qualitative only.
Redshift itself is robust to the profile; the exact exponent is open
microphysics. (`redshift`.)

### T10 (light: bending + Shapiro + chroma). Full `4M/b`, Cassini-grade delay, achromatic.

Fermat ray-tracing with `c_eff = 1 − x` (`x = R_s/r`) gives full first-order
bending `4M/b` (the naive `2M/b` bet was lost on the record). Chromatic
extension uses *phase* velocity `1/24`, not group `1/8`: the `r`-independent
factor drops out of the Born integral, leaving fractional chromaticity
`~1e−56` (optical) to `~1e−32` (10 TeV). Shapiro delay reproduces
`R_s·ln(4r₁r₂/b²)` to 5%, passing Cassini with `γ = 1` under the calibrated
spatial-sector coefficient. An isotropic
reading would give `b_crit = 8M`, 54% above GR's `3√3M` and excluded by EHT at
`~3.6σ`: the isotropic reading dies, not the core — transverse propagation must
be essentially unimpeded, as an all:all interior demands. (`lensing`, `chroma`,
`shapiro`, `bcrit`.)

### T11 (spatial sector + Mercury). Fitted `γ = 1` (independent BV micro-derivation consistent), `42.99″`/cy by direct integration.

Purely temporal models give closed Newtonian ellipses (`0` vs `43″`/cy): light
never needed `g_rr`, orbits do. Tortuosity `dl = (1+√χ/2)dr` gives
`h = (1+x/2)² ≈ 1+x`, `γ = 1`, `c_eff = √(f/h) = 1−x` matching the light sector
to first order, and `b_crit` back to `3√3M`. Direct geodesic integration
(`φ`-domain, complex-step) yields GR `42.99″`/cy and model `42.99″`/cy; a
flat-`h` hybrid gives `28.7″`/cy (PPN `2/3`). Second-order peel-off
`(ours−GR)/GR = −0.75·M/a` runs from 4.1% at `20M` to `2e−8` at Mercury.
Coefficient history, preserved: `1/2` was **fitted** to enforce `γ = 1` (BH,
unique coefficient, labeled fit); BV then **derived** `c ≈ 0.44–0.60` from
`ln2` line-defect scattering with zero tuning (target `0.456`, geometric
`1/√π = 0.564`), predicting `p = 2c` and `γ = 2c` (comparison target `p`
measured under I6b). Both determinations agree;
the micro-derivation is adopted with the fit preserved in history.
(`strain`, `uvscatter`; PPN: `γ = 1` claimed, `β` unresolved and not quoted,
`α₁,₂/ξ`/Nordtvedt untouched.)

### T12 (Kerr thermodynamics, conditional). `T_H`, `Ω_H`, first law — given `A(M,J)`.

With `S = k·ln2` (saturated legs) and the I1 matching, `S = A/4`; importing `A(M,J)` gives
`S(M,J) = 2π[M²+√(M⁴−J²)]`, whose derivatives return the textbook `T_H` and
`Ω_H = a/(r+²+a²)`, i.e. `dM = T·dS + Ω_H·dJ` (identities `< 1e−6`, independent
finite-step `ΔM = TΔS + Ω_HΔJ` to `O(d²)`; super-extremal `|J| > M²` returns NaN,
never clamped). Per-leg reading `T_H = (dM/dk)/ln2`; finite-step shift `−1/4k`
(`~1e−77` stellar-mass). Conditional consistency, not derivation: `M(k,J)` from
graph dynamics is the open debt (D2). (`thermo`, `kerr`.)

### T13 (UV dispersion). Quadratic-only by symmetry; `E_QG,1 = ∞`.

Tight-binding hopping `ω = 2J|sin ka/2|` has group velocity even in `k`: no
linear term, so Fermi's linear bound (`E_QG,1 > 9.3e19` GeV; GRB 090510
`> 1.2·E_P`) is evaded by symmetry. Leading correction
`v(E) = c(1 − E²/E_QG,2²)` with `E_QG,2 = √8·E_P ≈ 3.4e19` GeV, safe by `~1e8`
against Fermi's quadratic bound (`1.3e11` GeV): a 10 GeV GRB photon over 3 Gpc
delays by `~1e−20` s. Foamgrid FDTD confirms unbiased centroids with
transmission deficit `∝ ω²` (`16% → 4% → 0.2%` for `λ = 8 → 32` cells at
`ε = 0.25`), bounding per-Planck-edge defect density to `ε ≲ 1e−3`
(optical/Gpc) and `1e−14` (TeV/Gpc) for independent edges. Caveats:
regular-lattice result, near-horizon running open, scalar sector only (no
birefringence claimed); the universal-GW extrapolation (`~1e−82` at 100 Hz,
LVK `α = 4` safe by `~1e60`) is a recorded null, not a falsifier — no GW sector
derived. (`dispersion`, `foamgrid`.)

### T14 (merger battery + nulls held). Area theorem in wiring language; nulls, not anomalies.

All 32 confident GWTC-3 BBH medians (live GWOSC fetch; 8-event bundled fallback
offline) satisfy `k_f > k₁+k₂` (median fractional
creation `0.77` at `0.04` radiated; spin neglected but `a_f ~ 0.7` costs `~13%`
against a `77%` margin). GW150914 posteriors (8350 samples, spin-aware both
ends) give `P(Δk > 0) = 100%`, median `0.57`. Healing `dA/dt` with
`τ = 11.24M` (3.5 ms at GW150914 mass); ladder healing/scrambling/Page/
evaporation separated by `~66×` to `1e80` s; MSS `λ/2πT = 0.50–0.68`
(`α ∈ [9.0,12.4]`, `11.24` inside). Nulls held: no LHC thermal black holes
(`k ≈ 4.0–6.1` at 3–13 TeV vs `k_crit ≈ 18.1` at `r = 2l_D`, `M_D = 1` TeV,
`n = 6`, ratios `0.22–0.33`, onset `~550` TeV; recomputed from `tev.k_add` /
`k_crit_tev` — v5 prose preserves the pre-BS absolutes `11–17` vs `50` with
identical ratios, flagged paper-side), no lattice echoes
(amplitude `R ~ (ω/ω_P)² ~ 1e−80`, energy `~1e−160` at 100 Hz — dimensional
estimate, not a leg S-matrix derivation), no EHT shadow shift (`1e−48`, 47
orders below sensitivity). Remnant dark matter excluded on the record except a
narrow `~0.4`-dex window at `~4e5` g. (`data`, `gwdata`, `posteriors`,
`healing`, `mss`, `tev`, `lhc`, `echoes`, `bounds`, `remnant`, `emd`.)

---

## 4. L2: compact-object phenomenology (calibrated)

L2 is one mass–leg law plus six explicitly labelled phenomenological
calibrations/prescriptions (F1–F6). F1–F4 concern the spatial/PN phenomenology;
F5–F6 concern ejecta shedding. The shedding sector is calibrated **once** on
AT2017gfo; the remaining quantities are fitted, solved, or prescribed as
labelled below. It is the most testable layer and the least derived.
Its claims must be defeasible without touching L0/L1.

### The one law

`k = 1.51e77·(M/M☉)²` with no matter phases (I3 evaluated in solar masses).
Pulsars (`1.1–2.3 M☉`, `k ~ 1e77`), gap objects (`2.5–5 M☉`,
`k = 1.0–2.0e78`), and black holes are the same low-`k` all:all graphs at
different sizes. Consequences, stated bluntly: stable nuclear matter ends at
`~1e15` g/cc with no hyperon/quark branch realized in nature; `r`-process
yields through AT2017gfo neutron ejecta are reinterpreted as shed-leg
hadronisation. The gap is *described* (not derived) as the regime
`e_int ~ e_ext`; that interpretation inherits its calibration from AT2017gfo
and its mass-independence has not been derived from graph dynamics (D8).

### L2 calibrations (fits, all labeled)

| ID | Calibration | Value | Status |
|---|---|---|---|
| F1 | gradient slope | `p_adj(s) = 0.85 + 0.015·s`, 8–10 shells, exact EMD on full neighborhoods | **fitted**, labeled |
| F2 | bridge exponent | `β ≈ 1.5@300; 1.28@600; 1.24@1020; 0.99@4k; 0.87@8k; 0.74@16k`, deterministic `n ∝ r^β(N)`; log-linear over 6 points; recalibrated per `N` (drift faster than `1/N`; pre-run `1/N` extrapolation predicted `β(16000) ≈ 1.18`, measured `0.74`) | **fitted** per `N`; derivation from `N(r)` geometry queued (D4) |
| F3 | 2PN weight | `w = 1.953`, `c_tot = c₁ + w·c₂` | **solved** from the cancellation condition, not tuned — but not derived from the graph Laplacian either (D4) |
| F4 | `κ → c₂` map | `c₂(p) = p(2p−1)` | **ansatz** (open derivation D3): power-law fits better on these profiles (`R² 0.91` vs `0.81`) but the two maps disagree cross-applied (`c₂ 0.82` vs `3.14`); the uniform
measure is postulated in P4, so the open part is the map alone |
| F5 | shedding | `e: 0.5 → 0.416` (fraction `0.168`) + `10%` efficiency + `blue_frac 0.2` (`v_blue 0.3c κ 0.5`, `v_red 0.1c κ 10`) | **calibrated once** on AT2017gfo; `M_ej` exactly `k`-normalization-independent (`M_ej = frac·M_tot·ε`) |
| F6 | `q`-independence | `M_ej = 0.0168·M_tot` exactly flat in mass ratio (machine precision) | **prescription**, not derived from `V_k` (D1/D8): `q ~ 0.11` (GW190814) flashing at the same fraction as `q = 1` (GW170817) is the model's biggest theory bet |

### L2 measurements (outputs, not inputs)

- **Radial exponent**: `p = 0.913 ± 0.049` (80 graphs, `N = 1020`, exact
  Floyd+LP `~545` s; SEM `0.0055`, stacked `0.911` with `R² = 0.956`, 80/80 fits
  ok, range `0.79–1.05`). Distance to the GR-cancellation point `0.92` is
  `0.007` (`0.24σ` in `p`, `~0.09σ` in `ω̇`), with `5×` precision margin
  (`0.0055` vs `0.028`). N-scale: `0.9315 ± 0.0032` (4k), `0.9382 ± 0.0030`
  (8k), `0.9137 ± 0.0022` (16k); CSR-direct cross-check `0.9107` vs `0.9134`;
  local-`p` turnover `0.63–0.69 → 1.26–1.46` measured. Flat control `p = 0.49`
  is `−10σ` dead. (`orici`, `sinkor`, `shellscale`.)
- **2PN lock**: model `c₁ = 3.36` vs GR `1.94` (73% excess) is cancelled at
  `p = 0.92` (`c₂ = 0.7728`, `c_tot = 4.8693` vs GR `4.8695` → `0.00σ`
  fixed-`M`). Self-consistent `R+ω̇ → M`: `ΔM = −11.2` ppm naive (`−4.5` ppm
  with GR `g_rr`), `Δsin i = 3.7e−6`; J0737 `ω̇ = 16.899323(13)` deg/yr at
  `0.1σ`, `sin i` at `0.36σ`; B1913 at `0.01σ`. Bending/Mercury 2PN pieces hide
  below VLBI/astrometry. (`pulsar`.)
- **AT2017gfo anchor**: `1.4+1.4` gives `0.047 M☉` (blue `0.009` + red `0.038`),
  `m_g ~ 18.0` at 40 Mpc vs observed `17.5` (inside the `±1` analytic
  tolerance). Gap events are *brighter* at fixed distance. Band mags assume
  `BC = 0` and per-component peaks; `g`-band verdicts robust, `i`-band NOT
  claimed (one-zone `κ = 10` over-traps: `t_red ~ 10` d vs observed `~4` d
  decline, `m_i` faint by `~2–3` mag — conservative for gap-`g`
  detectability). (`collapse`.)
- **Gap prediction**: `M_tot → M_ej`: `2.8 → 0.047`, `5.0 → 0.084`,
  `7.2 → 0.121` (all `M☉`); `m_g ~ 21.2` at 200 Mpc (Rubin single-visit
  `r = 24.5`, DECam KN depth `23.5`); O5 yield `~1.05`/yr (ours, 1.5 gap/yr ×
  70% DECam-like) vs `≤ 0.3`/yr standard (literature `2–28%` mgNSBH input, not
  derived). Kill rule: 10 qualifying gap mergers (`< 200` Mpc, `< 100` deg²
  90%, multi-detector) with zero kilonovae to `m < 24` kills L2. One bright gap
  kilonova kills neutron-star EOS models instead. (`collapse`,
  `docs/observation-protocol.md`.)
- **Universal (BBH) shedding**: Eq. `M_ej = 0.0168·M_tot`, locked by the
  AT2017gfo calibration before anyone asked what it implies at `30+30 M☉`:
  nearby BBH must flash at `m_g ~ 22` (O5-testable). Kill accounting kept
  **separate** from the gap sample. (`massgaps`.)
- **GW190814 stress test**: `23.2+2.6 M☉` at `241^{+41}_{−45}` Mpc predicts
  `M_ej = 0.43 M☉` (blue `0.087`), `m_g ≈ 21.0` at `t ≈ 1.9` d. Epoch audit
  (CFHT MegaCam `g` + GROWTH DECam `i` detection limits) gives combined
  `P(detect) ≈ 0.68` (`g`-only, robust, no color term) to `0.88` (with
  `g−i = 0.7` systematic): non-detection at `p_miss ~ 0.32` down to `~0.12` —
  genuine pressure about one sigma from a kill, not exclusion. Analytic
  systematics (POSSIS-inspired viewing `0–1.25` mag + opacity `L ∝ κ^{−0.65}`,
  Fig. 75b) bound the hiding window: equatorial + lanthanide-mixed
  (`κ_blue = 2`) drops `P` to `~0.18`. Full 3D POSSIS queued (D7). Erratum on
  record: the first audit used a nominal ZTF depth, but ZTF ran no targeted
  GW190814 follow-up; superseded by CFHT/GROWTH epoch tables. (`massgaps`,
  Fig. 75/75b.)

### L2 positive null (upper gap)

No graph-scale feature at the `~44 M☉` pair-instability edge (GWTC-4:
`44.3^{+5.9}_{−3.5} M☉`, hierarchical transition at `46.2^{+12.6}_{−7.2} M☉` —
labeled literature inputs): `k(M) ∝ M²` has zero log-log curvature (`< 1e−9`
over `0.7–150 M☉`); spin orders legs smoothly (`1 → 0.857 → 0.5` at
`a = 0 → 0.7 → 1`); Love `k₂` runs slope `−2` with no break; the leg-quantum
line crossing 10 Hz at `~32 M☉` is energetically invisible (`dM/M ~ 1e−81`).
Congestion ladder seals the assignment: `χ ~ 1e−8` in He cores, `~1e−14` in
envelopes — graph corrections where pair-instability happens are negligible in
the model's own terms. The boundary belongs to stellar/nuclear physics, not the
graph; inserting `44 M☉` as a graph parameter is refused. (`massgaps`.)

---

## 5. Open maps (explicitly open)

Each item: what is missing, what would close it, what it gates. Tracked in
`docs/DEFERRED.md`; the paper's kill table wires the falsifiable ones.
Tag convention: D1–D10 here always mean DEFERRED items; the appendix-letter tag
(D2) (= module `evaporation_unitary`) is always written as the module name —
supplement.tex S1/S3 uses bare (D2) for both meanings (flagged paper-side).

| ID | Missing | Close criterion | Gates / kill relevance |
|---|---|---|---|
| D1 | Graph evaporation isometry `V_k: H_graph,k → H_graph,k−1 ⊗ H_leg` from graph dynamics; genuine QES extremization | derive (not choose) a scrambling `V_k` from the graph Hamiltonian/adjacency; reduced radiation spectrum follows Page under all:all dynamics; extremize `S_gen` from a path integral | promotes T6/T7 from scoped to full; no current falsifier (no observed BH Page curve) — referee-honesty issue |
| D2 | Kerr multipoles from the graph: `M₂ = −Ma²`, `g_tφ`, `r_ISCO(M,J)`, Kerr QNM spectrum | derive `Q = −Ma²(1+δ_Q)` without assuming Kerr; exterior perturbation `δω_nlm` vs Kerr | future wires: graph `|δ_Q| ≳ 0.17` ruled out by GW241011; QNM benchmark from GW250114 (`δf_220~2%`, `δτ_220~10%`, `δf_221~30%`, `δf_440~tens%`); GW250114/GW241011 currently consistent *by construction*, not passed predictions |
| D3 | Quantitative Ollivier–Ricci `κ → c₂` map | derive the map; resolve power-law vs `1/r²` disagreement | promotes F4 to derived; kill wire `p = 0.92 ± 0.056` at `N = 1024` class held to N=16000; v0.5 route: curvature as failure of `V(r)` to scale uniformly via `d_eff(r)` (`emergent_dim`) |
| D4 | `β(N)` and `w` from geometry | derive `β(N)` from `N(r)` geometry, `w` from the graph Laplacian (Damour–Schäfer from wiring) | promotes F2/F3 to derived; v0.5 route: `β(N)` from `N(r)` implied by `V(r)` scaling (`emergent_dim`) |
| D5 | NICER `M-R-Λ` + tidal deformability from routing stiffness | derive `R_1.4`, `M-R`, `Λ` | sharpest near-term test after kilonova rate (2–3 yr): `R_1.4` at 11–13 km, 5%, unreproducible by routing stiffness kills L2 compactness |
| D6 | Mass–radius from wiring | derive `R_s = 2M` from wiring alone | promotes I3 to derived (long-term); v0.5 route: `R_s` as radius where embedding `k` legs into `M_O(G_vac)` forces a surface (T5 pop + `d_eff -> 3` fixed point) |
| D7 | Kilonova radiative transfer | validated multidimensional RT on public ejecta models/transformations compatible with the F5/F6 bulk prescription (morphology, velocity structure per VEL-1, Ye-dependent opacities/reprocessing, viewing-angle dependence, direct `i`-band); pipeline must pass the AT2017gfo anchor/control gate before its GW190814 result promotes the analytic verdict (POSSIS primary implementation) | decides whether the GW190814 non-detection is compatible with universal shedding or falsifies it; `g`-band verdicts already robust |
| D8 | Shedding efficiency `ε(M,a,q)` + shutoff location | derive mass/spin/ratio dependence from `K_max(N)` combinatorics, spin-ordered reabsorption, or remnant-trap physics, with any shutoff location as *output* | highest-value attack surface on universal shedding; a derived shutoff between gap and BBH masses must land where it lands (same no-insertion rule as the 44 M☉ null) |
| D9 | Raychaudhuri (focusing) for leg bundles | derive focusing for SI fronts on leg networks (seed: AT congestion slowdown); closes the Jacobson chain to Einstein's equations with `η = 1/4` from I1b, `G = 1` | promotes I6c from open bridge to derived; gates nothing else — T8–T11 stand without it |
| D10 | Tension spectrum: simulator d-dip around mass + tension→`κ` map (v0.6) | (a) an over-coordinated (tense) region in the graph shows the GR fingerprint shape (near dip, overshoot, →3⁺) under info-side `d_eff`; relaxed `z≈4` regions show `d=2` fabric / `d=3` reconstruction as applicable; (b) Ollivier–Ricci `κ` tracks over-coordination (`z−4`) quantitatively | P0' first quantitative wire; failure of (a) shape-match after the mapping is fixed refutes P0'. v0.6 probe: bare shortest-path rejected for tense regions (inverted far side: shortcuts shrink balls, GR needs stretched rulers); D10b: tortuosity-import costs partially recover (no flip), `c_eff`-import costs give full dip → overshoot → asymptote on 9×9 mild plug (conditional on bridge); amplitude scales loosely with χ; κ is an interface pattern (criterion (b) reformulated) |

Rule for all D-items: the closing derivation must output the number or location,
not take it as input. Inserting an observed scale as a graph parameter is a fit,
not a prediction, and is refused (precedent: 44 M☉).

**v0.5 measurement protocol (D3/D4/D6).** For many states in `src/bh_graph/`:
1. compute `d(i,j)` from information-transfer (resistance / diffusion /
communicability, not shortest path — see `emergent_dim`); 2. build `B(r)`;
3. measure `V(r)`; 4. compute `d_eff(r) = d ln V / d ln r`. Ask: does
`d_eff -> 3` without imposing 3? A positive result promotes the D-item
per its close criterion; a negative result localizes which part of the
information geometry needs another principle.

**v0.6 conjecture: only vacuum is perfectly 3D (D10 target).** `d_obs ≡ 3`
exactly holds only in the zero-tension limit; mass imprints a dimensional
fingerprint. GR side, computed (weak-field uniform star, proper balls of
proper radius `l`): near-field dip (`d_eff ≈ 2.99` at `l = 30M`), overshoot
(`≈ 3.03` at `100M`, `≈ 3.010` at `1000M`), asymptote `→ 3⁺` as `~1/l`.
Amplitude `O(M/l)` (`~10⁻⁹` at Earth's surface: structure, not a laboratory
signal). The simulator must reproduce this *shape* around tensed regions
(D10a); the relaxation principle itself lives on `G` (coordination → 4),
never on spacetime. Full explanation: `docs/relaxed-vacuum.md` §1, §5.

---

## 6. Non-claims (what the model does not say)

Stated so no reader misses them:

- Not a UV-complete quantum gravity: no Hamiltonian derivation of the mass map,
  no Lorentz-invariant dynamics.
- No `β` PPN parameter (coordinate-confused, not quoted); no `α₁,₂`, `ξ`,
  Nordtvedt; no linear LIV (forbidden: finite `E_QG,1` kills the discrete-leg
  picture outright).
- No Kerr `M₂`, `g_tφ`, ISCO, or QNM spectrum from the graph (overtone toy is
  Schwarzschild-like; fundamental damping `τ = 11.24M` calibrated).
- No NICER radii or tidal deformabilities yet (queued, D5).
- No `i`-band kilonova photometry claimed (one-zone red over-traps).
- No graph feature at 44 M☉ (positive null, §4).
- No explanation of FRBs, lensing oddities, or TeV transparency (examined, died
  on arithmetic, on the record). Pre-v4.0 "no standing anomaly" framing is
  superseded for exactly the five compact-object facts in §4 — nothing else.
- Ruled out on the record (kept visible): broad Planck-remnant dark matter
  (survives only in a `~0.4`-dex EMD window at `~4e5` g); isotropic
  `b_crit = 8M`; naive `γ = 2` strain; linear LIV; flat `p = 0.49`.
- No microscopic 3D lattice postulated (v0.5): `d_G ≠ d_I ≠ d_obs` in general;
  no Lorentz-invariant dynamics; no Born rule / double-slit derivation (needs
  D1); no Casimir `1/d⁴` derivation (ontology only: constrained `G_vac`, not void).
- No simulator d-dip yet (v0.6, queued D10): the GR fingerprint shape is a
  target, not a graph result. No 2D + scale → 3D mechanism (open D3/D4/D6);
  no tension→`κ` map (`z−4` to curvature, open D10b); no isostatic-stability
  derivation under graph dynamics (needs D1).

---

## 7. Symbol ledger

Single table; every symbol in §1–§4 appears here with its home.

| Symbol | Definition | Home |
|---|---|---|
| `N` | interior node count | §1, `graphs` |
| `z` | mean coordination (edges per node) | P0' (v0.6): `4` in vacuum |
| `G`, `G_vac` | information graph `(V,E,I)`; relaxed vacuum state | P0' (v0.6), `emergent_dim` |
| `M_O` | observer reconstruction map (restricted channel) | P0'/P4 box (v0.5–v0.6) |
| `d(i,j)`, `B(r)`, `V(r)`, `d_eff` | info-transfer distance, ball, capacity, `d ln V / d ln r` | §1 box (v0.5), `emergent_dim` |
| `d_G`, `d_I`, `d_obs` | microscopic / information / observed dimension | §1 box (v0.5) |
| `k` | exterior leg count | §1, `horizon` |
| `e_int`, `e_ext` | interior / exterior entanglement fractions | P3, `horizon`/`monogamy` |
| `K_max` | max exterior budget (normalization) | §1, `horizon.exterior_budget` |
| `m_x` | neighborhood measure at `x` (P4: uniform, `p = 0`) | P4, `orici` |
| `κ(x,y)` | Ollivier–Ricci curvature `1 − W₁(m_x,m_y)/d(x,y)` | T8/F4, `orici` |
| `A(k)`, `R(k)` | `4ln2·k·l_p²`, `√(A/4π)` | I1b, `horizon` |
| `PATCH_AREA` | `4ln2` Planck areas per leg | I1b (via matching), `horizon.PATCH_AREA` |
| `r_point`, `k_crit`, `R_obs` | point radius, `4πr²/4ln2`, piecewise radius | T5, `micro` |
| `s_leg`, `η_vN` | per-leg entanglement (`ln2` saturated) | I1a/T6, `qes` |
| `S₀`, `k_page` | bulk entropy, island crossing | T6, `qes` |
| `t_*`, `λ` | scrambling time, Lyapunov exponent | T2, `circuits`/`otoc` |
| `S_rad`, `N_eff` | radiation entropy, effective qubit count | T7, `evaporation` |
| `V_t`, `V_k` | qubit-toy isometry (done) / graph isometry (D1) | T7, `evaporation_unitary` |
| `a`, `Q`, `r+`, `k_eff` | Kerr spin, charge, outer horizon, effective legs | I3/T12, `kerr` |
| `T_H`, `Ω_H`, `S(M,J)` | Hawking temp, horizon velocity, entropy | T12, `thermo` |
| `k(r)`, `T(r)`, `Φ` | screen legs, equipartition temp, potential | T8, `entropic` |
| `z`, `c_eff`, `α` | redshift, front speed, congestion exponent | T9, `redshift` |
| `b_crit`, `γ` | photon capture impact parameter, PPN gamma | T10/T11, `bcrit`/`strain` |
| `h`, `χ`, `x`, `c` | radial metric factor, congestion, `R_s/r`, tortuosity | T11, `strain`/`uvscatter` |
| `σ`, `κ_blue/red` | leg cross-section `4ln2`, kilonova opacities | T11/§4, `uvscatter`/`collapse` |
| `E_QG,1`, `E_QG,2` | linear (`∞`) / quadratic (`√8·E_P`) LIV scales | T13, `dispersion` |
| `p`, `β(N)`, `c₁`, `c₂`, `w`, `c_tot` | radial exponent, bridge exponent, 2PN coefficients/weight | §4 F1–F4, `orici`/`pulsar` |
| `e_init/final`, `ε`, `M_ej` | shed fractions, efficiency, ejecta mass | §4 F5–F6, `collapse` |
| `m_g`, `m_i` | peak apparent mags (analytic, `BC = 0`) | §4, `collapse.peak_apparent_mags` |

---

## 8. Map to code, tests, figures

- **L0**: `graphs`, `scrambling`, `circuits`, `otoc`+`pheno`, `krylov`, `syk`, `bigsyk`,
  `sparse24`, `monogamy`, `qec`, `robustness`, `fission`, `klanguage`,
  `collapse` (grid→complete part), `concentration`, `emergent_dim` (v0.5–v0.6:
  `d(i,j)` / `B(r)` / `V(r)` / `d_eff(r)` protocol, `K_N` shortest-path
  failure pinned; v0.6: BFS convergence series, diffusion overshoot-shrink,
  shell no-emergence pin, tense-plug inversion pin (shortest-path rejected
  for tense regions, far-field near-balls identical to control);
  explanation: `docs/relaxed-vacuum.md`).
- **L1**: `horizon`, `micro`, `qes`, `evaporation`, `evaporation_unitary`,
  `haar`, `maxent`, `tn`, `kerr`, `kerrpage`, `thermo`, `entropic`, `redshift`,
  `heatker`, `orici` (AU signs), `jacobson`, `lensing`, `chroma`, `shapiro`,
  `bcrit`, `strain`, `weakfield`, `perwalk`, `legham`, `dispersion`, `foamgrid`,
  `data`, `gwdata`, `posteriors`, `litcompare`, `healing`, `mss`, `mp`,
  `greybody`, `congestion`, `charge`, `bandwidth`, `gridcirc`, `monitor`,
  `selfattack`, `lhc`, `ps`, `scatter`, `emd`, `viability`, `tension`,
  `tensionvol`, `overtones`, `qnmfoot`, `qnmlegs`, `gw250114`, `echoes`, `tev`,
  `bounds`, `remnant`, `cosmic`, `ds`, `lunch`, `uvscatter` (BV derivation of
  `c`), `sinkor`, `shellscale` (N-scale backends).
- **L2**: `pulsar`, `orici` (gradient shells), `collapse` (leg-shedding),
  `massgaps` (lower-gap continuity + upper-gap null + GW190814 audit).
- **Falsifiers**: AF quench ratio, `α ∈ [9.0,12.4]`, `A ∝ N` TN wire, LHC
  thermality below `k_crit`, `s_leg ≤ l_p²/4` wire, linear LIV, `p` wire, gap/BBH
  kilonova wires, NICER wire, Kerr-quadrupole future wire — see the v5 kill
  table (`paper/v5/main.tex` §6) and `docs/observation-protocol.md`.
- **Reproduce**: `pip install -e ".[dev]"`, `pytest tests/ -q` (398 tests),
  `python scripts/generate_figures.py` + `python scripts/generate_v5_figs.py`
  (81 figure files, Figs 1–75), `streamlit run app.py`.

Counts above are v5.0 (`main.pdf` 12pp + `supplement.pdf` 11pp, S1–S10, 46/46
references cited). The v4.1 living document stays archived as the extended
record; v5 is canonical.

**Provenance layers (v0.2 audit).** Checked numbers fall in three layers with no
numerical contradictions except the TeV absolutes (fixed in T14): test-pinned
(shed `0.168`, `c₂(0.92) = 0.7728`, log-log slope `2.0`, fitted-form `γ = 1`
to `1e-6` with BV interval consistent,
`p = 0.913 ± 0.049` / SEM `0.0055` / 80-of-80 in `data/p80_n1020_beta124.json`),
test-pinned envelopes (B1913 `6.2σ` / J0737 `9.7σ` naive bands, J0737 `< 0.1σ`
resuscitated, GW190814 `P = 0.68 ± 0.02`, chromaticity `< 1e-50/1e-30`),
figure-computed (`25` trials `N = 8…128`, depth-`5` convergence scan,
deficit orderings), and paper-quoted (`0.002`-bit tracking, `42.99`,
`0.57`/`100%` posteriors, `32` live BBH, MSS `0.50–0.68`, `1e-80/1e-160`
dimensional estimate). Suite at v0.6: 425 collected, 423 passed,
2 torch/GPU-only skipped.

---

## 9. Promotion rules (how this document changes)

- An **input** becomes **derived** only by a derivation from earlier layers plus
  a merged test — never by rewording. (Precedent: tortuosity `1/2` fit → BV
  `0.44–0.60` derivation, with the fit preserved in history.)
- An **L2 calibration** moves to L1 only when its value is output by graph
  dynamics or geometry, with its old fitted value kept as the target it had to
  hit. (Candidates: F2/F3 via D4, F4 via D3, F6 via D1/D8.)
- A **D-item** closes only by its stated close criterion in §5. Partial progress
  is recorded in `docs/DEFERRED.md`, not by softening the criterion here.
- A **killed** claim stays in §6 with its killer named. (Precedents: broad
  remnant DM, isotropic `b_crit`, naive `γ = 2`, linear LIV, flat `p = 0.49`.)
- This document versions with the paper: v0.4 tracks v5.0 (I1-matching
  release; import IDs stable except the splits I1→I1a/I1b (v0.4),
  I4→I4a/I4b and I6→I6a-c (v0.3)). v0.5 adds P0/M_O/
  dimensions + `emergent_dim` with no number changes; v0.6
  flips P0→P0' (relaxed isostatic vacuum), adds the tension spectrum,
  the only-vacuum-is-3D conjecture, D10 (with the D10a tense-plug inversion
  pin: bare shortest-path rejected for tense regions), and
  `docs/relaxed-vacuum.md`, with
  no number changes and stable import IDs.
  Any number changed here must change in the same PR in the S1 audit table or
  be flagged as a deliberate divergence. One deliberate divergence stands:
  T14 TeV absolutes follow the code (post-BS), not v5 prose (pre-BS).

---

*Index-card version: L0 says what the wiring is (all:all, monogamy, no interior
distance). L1 says what spacetime costs (4ln2 per leg, one GR input, borrowed
thermodynamics) and what that buys (scrambling, Page, Newton-to-Mercury,
quadratic-only UV). L2 says what compact objects are (one `k ∝ M²` family, shed
legs, flash in O5) and what kills it (ten clean misses). §5 lists exactly what
would turn calibrations into theorems. Everything else is evidence.*
