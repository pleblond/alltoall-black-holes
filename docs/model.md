# The model, stated first (v0.11)

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

**v0.7 field-program release.** No number changes:
new F-layer, §10. States the relational field program built on top of the
graph — field postulates FP1/FP2 (`ψ = r + is`, `H = -A`), the derived
`B`/`J` anatomy, the J₂ working fabric, contraction/splitting ontology,
conditional accounting, the observer quotient, the joint vacuum family,
the hidden sector, the response kernel, and the filed dynamics debts —
with every verdict quoted from `docs/scaffolding-history.md` (§§1–19),
the named `docs/DEFERRED.md` verdict section, or committed `data/`
records. Names FP1/FP2 are field-program postulates, not model.md P1/P2;
F1–F6 stay L2 calibrations. L0/L2 untouched; L1 T7/D1 record the merged
small-N `graphvk` closure (previously-merged main, not new in this release);
no new D-numbers
(D14/D15 are taken in DEFERRED.md — field debts are filed by name in
§10 with a pointer to the §19 debt register).

**v0.8 field-completion release.** No number changes:
§10 extended with the twelve merged follow-up campaigns. VAC-0 closes
(FINAL MIXED: per-phenomenon LAW/CLASS split, nothing requires uniquely
J₂ — the "H/I open" of v0.7 is retired); the vacuum family gains domain
interfaces (RADIATIVE), hidden textures (GRADIENT), and long-time
stability (ROBUST); sources are characterized (SOURCE0-INCOMPLETE with
the release rule); split selection narrows to the covariant residual `ξ`
(SPLIT0-MIXED) with probability-free books closed (INFO0-MATCHED); the
merge update is characterized as deterministic (MERGE0) with its missing
account an exact function of `ξ` (RES0-XI); the fiber measure (FIBER0-DEBT,
520 dof, two rivals) and the trigger census (TRIGGER0-CONDITION, 19 survive,
zero imply) file the remaining debts; REWIRE-0 closes the rewire-selector
question (DEGENERATE). L0/L1/L2 untouched; no new D-numbers.

**v0.9 store-and-3D release.** No number changes:
§10 gains two campaigns. STORE-0 shows a kept-`ξ` store makes merge
reversible (STORE0-REVERSIBLE, 46/46: exact predecessor recovery and
energy closure from the same stored content, minimality earned —
discrete `c` plus `d` required — filed as kept information, not derived
selection). DIM-3-0 lifts the fabric to J₃ (DIM3-GEOMETRIC: exactly
quotient-cubic with 3D far-field laws, but the 2D-calibrated blind
rulers misread known-3D three proven ways; 3D-calibrated rulers are
DIM-3-1 work). L0/L1/L2 untouched; no new D-numbers.

**v0.10 substrate-and-store release.** No number changes:
§10 gains six campaigns. SUBSTRATE-CLASS-0 narrows the VAC-0 class
(SUBCLASS0-PARTIAL: exact minimal rules for E/H-shell/G in both
spectral and combinatorial form with impossibility proofs for F and
H_TAU in frozen space — spectral vs combinatorial ties, no unified
condition); SCALE-0 banks the large-L asymptotics (SCALE0-BANKED,
178/178: `d_H → 2` with j2 == sq to machine precision, exact forms
upheld, velocities L-independent); Q-DYN-0/0b close the store-dynamics
question (QDYN0-INCOMPLETE autopsy-resolved, QDYN0B-EVENT-LOCAL 51/51:
Q frozen on all 414 rungs, RES0-XI earned as an event-local
functional, no Q-dynamics campaign justified); BH-ENT-0 censuses
collapsed-region multiplicity (BHENT0-UNCLASSIFIED 153/153: exact
orbits 8/67/701/10047/218083, volume/boundary/mixed all rejected,
hidden-sector field multiplicity exterior-blind); DIM-3-1 repairs the
3D rulers (DIM31-GEOMETRIC: dimension 3 through six channels, transfer
validation failing at L16/L20). L0/L1/L2 untouched; no new D-numbers.

**v0.11 area-law release.** No number changes:
§10 gains six campaigns. WEAVE-0 tests the random-weave 3D alternative
(WEAVE0-INCOMPLETE ambiguous: volume 3D-side only at λ = 0.01, spectral
never jointly 3D, no B+C core); Q-INFO-0 identifies store information
with the banked qubit functional (QINFO0-IDENTICAL: h2 = S_banked to
1.1e-16, no new entropy); BH-Q-ENT-0 censuses blind-store dimension
(BHQENT0-UNCLASSIFIED 34/34: topology-dependent D, all law gates miss);
BH-Q-AREA-0 earns the first area law (BHQAREA0-MAX 22/22: S_Q^∂ = κ*A
with κ* = 4.2207 at maximum density h* → 1, doubly selected —
isolated information only, thermodynamics still open); JET-1 closes
the dynamical-jet route (JET1-NULL 13/13 with a filed stop rule);
EVENT-0 shows fixed-G flow never forces structural change
(EVENT0-EQUIV 33/33: 61 orbits, zero firing implications). L0/L1/L2
untouched; no new D-numbers.

**What this document is:** the definition of the model — primitives, postulates,
theorems, calibrations, open maps, and non-claims — in that order. Tests,
figures, and measurements are cited as *evidence about* the model, never as its
definition.

**What this document is not:** a tutorial (see `docs/model-explained.md`), an
observation plan (see `docs/observation-protocol.md`), the paper (see
`paper/v5/`), or the history of how the choices were locked (see
`docs/scaffolding-history.md`). It does not re-derive anything; it states what
is assumed, what follows, and what is still missing.

**How to read it:** three layers, in hardening order, plus the field program.

- **L0 — Graph kinematics.** The robust core. Almost everything here is a theorem
  of the wiring, not a fit.
- **L1 — Spacetime interface.** The robust core plus a small list of explicit
  imports from GR/thermodynamics. All weak-field gravity and QI results live here
  *conditionally* on those imports.
- **L2 — Compact-object phenomenology.** Calibrated, not core. Fitted numbers,
  a solved weight, one ansatz map, and one extrapolation prescription. Killing L2
  must not kill L0/L1.
- **F — Relational field program (§10).** Two scalars per node plus `H = -A`
  on a working fabric: what follows (anatomy, propagation, quotient, vacuum
  family, response) and what stays debt (firing law, history measure, matter,
  gravity carrier). Killing any F verdict must not kill L0/L1.

Open derivations (D1–D13 in `docs/DEFERRED.md`) are fenced in §5 and referenced
from the exact postulate or theorem they would promote. Nothing in §2–§4 depends
on them silently. Field-program debts are fenced separately in §10 by name
(no new D-numbers; D14/D15 are taken in DEFERRED.md) with a pointer to the
debt register in `docs/scaffolding-history.md` §19.

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
sees `G` directly; an observer sees `M_O(G) = [G]_{∼_O}`, the quotient of
microscopic states by observational equivalence under the observer's
graph-internal accessible algebra `A_O` (P4 is one candidate instance).
Admissibility requires five: graph-internal, permutation-covariant,
coarse-graining stable, operational, frozen rule (D10/D12); `V_O ~ R³`
is the output test, never an input. Objective spacetime is defined as
the part of `G`'s information structure invariant under all admissible `M_O`.

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

### T15 (cost dominance). Shortcuts priced at or above their hop-saving cannot inflate balls; any inflation pins an underpriced shortcut.

Let `G₀` be a grid graph with shortest-path distance `dist₀`, and `G` be
`G₀` plus extra (shortcut) edges. Price edges with `w_e ≥ 1` on grid edges
and `w_e ≥ dist₀(u,v)` on shortcut edges. Then `dist_w ≥ dist₀` pointwise,
hence `V_w(r) ≤ V₀(r)` for every `r` (U-side: balls shrink, rulers stretch —
the GR side). Proof: project any weighted `s–t` path to a grid walk by
replacing each shortcut `(u,v)` with a `dist₀(u,v)`-hop grid path; the
projected walk has `H ≤ cost(path)` hops and `H ≥ dist₀(s,t)`, so every
path costs at least `dist₀(s,t)`; minimizing gives `dist_w ≥ dist₀`, and
`V_w(r) ⊆ V₀(r)` follows. Contrapositive: any radius with `V_w(r) > V₀(r)`
(∩-blip) pins a shortcut edge with `w_e < dist₀(u,v)`. **Derived**, pure
graph kinematics, zero tuning. (`emergent_dim`, D10b.)

Corollary (witness node). An underpriced shortcut `(u,v)` always announces
itself from its own endpoints: `dist_w(u,v) ≤ w_e < dist₀(u,v)`, so `v`
joins the `u`-centered weighted ball strictly before the unweighted one.
The converse of T15 is false for volumes: a violation need not produce any
`V_w > V₀` blip (a 5-chain with a shortcut at `1.5 < 2` and overpriced grid
edges has `V_w ≤ V₀` at every radius — the early arrival is masked in the
counts). What the contrapositive fires on is a volume blip, not a slope
flip: a window with `p_w > p_0` can in principle be catch-up growth with
`V_w ≤ V₀` everywhere.

Instances pinned (L=40 mild 5×5 king plug, center source, mid window
(8,20), control `p = 1.920`): `c_eff` costs at `z_vac = 1` satisfy the
premise (min shortcut `6.00 ≥ 2`, min grid `2.50 ≥ 1`) → max `V_w/V₀ =
0.2000`, mid `p = 1.838` (`r² = 0.74`), no flip, zero pointwise
`dist_w ≥ dist₀` violations. Slope verdicts are window diagnostics, not
theorem content: in (10,20) the z=1 comparison reverses (`2.517 > 1.928`,
catch-up growth) while the window-free facts (ratio ≤ 0.2, zero
violations) stand; the tort flip holds in all 11 scanned windows.
Tortuosity-import costs at `z_vac = 4` violate
it (all 32 diagonals `w ≤ 1.50 < 2`) → fractional blip `V_w(1.9) = 9 >
V₀ = 5` invisible to integer sampling (no excess at any BFS radius),
mid-window flips to `p = 2.020` (`r² = 1.0000`). Use: T15 is the
admissibility diagnostic for D10b cost rules — a rule must satisfy the
premise on shortcut edges or own its ∩-blips. Applied to the `c_eff` rule
at vacuum `z_vac = 4`: 24 boundary diagonals violate (`w < 2`, min 1.50;
8 interior diagonals marginal at `w = 2`), all 24 arrive early from
endpoint-centered balls, and the center-source profile carries a genuine
fractional volume blip (peak `V_w/V₀ = 1.077` at `r = 13.75`; excess over
33 of 58 critical radii spanning 7.75–39.75) that integer sampling cannot
see (zero excess at any BFS radius). The contrapositive fires on the blip
(a violation must exist); the violator census locates it at the plug
boundary. The mid-window slope flip (2.020) is the blip's window-averaged
shadow.

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
  from graph dynamics at scale (D1 remainder). "Page curve is a theorem of
  graph dynamics" in the thermodynamic limit is the close criterion, not the
  current claim.
- **Done (small-N ED)**: `graphvk` derives per-step `V_k = exp(−iH_graph·dt)`
  from the hole adjacency (disordered Heisenberg, one random XYZ term per
  edge), proves `V†V = I` (including a composed-map inner-product test),
  computes `S_rad` from `ρ_rad`: all:all tracks exact Page (mean dev `< 0.25`
  bits at `N = 8`, typically `~0.01`) while the same `dt` on a chain sags
  below Page (mean dev `> 0.4`); changing the graph changes `V`
  (`‖U_complete − U_chain‖ > 1`). What remains: large-`N` limit,
  `k`-backreaction on the interior spectrum, emission energy/mass spectrum.

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
Tag convention: D1–D13 here always mean DEFERRED items; the appendix-letter tag
(D2) (= module `evaporation_unitary`) is always written as the module name —
supplement.tex S1/S3 uses bare (D2) for both meanings (flagged paper-side).

| ID | Missing | Close criterion | Gates / kill relevance |
|---|---|---|---|
| D1 | Graph evaporation isometry `V_k: H_graph,k → H_graph,k−1 ⊗ H_leg` from graph dynamics (small-N ED instance closed: `graphvk` derives `V_k = exp(−iH_graph·dt)` from hole adjacency, `V†V = I`, all:all tracks Page `< 0.25` bits at `N = 8` vs chain sag `> 0.4`); genuine QES extremization; `C_vac` preservation (`U(G_vac) ∈ C_vac`, self-healing vs amplify) | derive (not choose) a scrambling `V_k` from the graph Hamiltonian/adjacency at scale (large-`N` limit, `k`-backreaction, emission spectrum still open); reduced radiation spectrum follows Page under all:all dynamics; extremize `S_gen` from a path integral; trajectory stays in `C_vac` (`⟨Λ⟩_U` in-basin; injection test) | promotes T6/T7 from scoped to full; no current falsifier (no observed BH Page curve) — referee-honesty issue |
| D2 | Kerr multipoles from the graph: `M₂ = −Ma²`, `g_tφ`, `r_ISCO(M,J)`, Kerr QNM spectrum | derive `Q = −Ma²(1+δ_Q)` without assuming Kerr; exterior perturbation `δω_nlm` vs Kerr | future wires: graph `|δ_Q| ≳ 0.17` ruled out by GW241011; QNM benchmark from GW250114 (`δf_220~2%`, `δτ_220~10%`, `δf_221~30%`, `δf_440~tens%`); GW250114/GW241011 currently consistent *by construction*, not passed predictions |
| D3 | Quantitative Ollivier–Ricci `κ → c₂` map | derive the map; resolve power-law vs `1/r²` disagreement | promotes F4 to derived; kill wire `p = 0.92 ± 0.056` at `N = 1024` class held to N=16000; v0.5 route: curvature as failure of `V(r)` to scale uniformly via `d_eff(r)` (`emergent_dim`) |
| D4 | `β(N)` and `w` from geometry | derive `β(N)` from `N(r)` geometry, `w` from the graph Laplacian (Damour–Schäfer from wiring) | promotes F2/F3 to derived; v0.5 route: `β(N)` from `N(r)` implied by `V(r)` scaling (`emergent_dim`) |
| D5 | NICER `M-R-Λ` + tidal deformability from routing stiffness | derive `R_1.4`, `M-R`, `Λ` | sharpest near-term test after kilonova rate (2–3 yr): `R_1.4` at 11–13 km, 5%, unreproducible by routing stiffness kills L2 compactness |
| D6 | Mass–radius from wiring | derive `R_s = 2M` from wiring alone | promotes I3 to derived (long-term); v0.5 route: `R_s` as radius where embedding `k` legs into `M_O(G_vac)` forces a surface (T5 pop + `d_eff -> 3` fixed point) |
| D7 | Kilonova radiative transfer | validated multidimensional RT on public ejecta models/transformations compatible with the F5/F6 bulk prescription (morphology, velocity structure per VEL-1, Ye-dependent opacities/reprocessing, viewing-angle dependence, direct `i`-band); pipeline must pass the AT2017gfo anchor/control gate before its GW190814 result promotes the analytic verdict (POSSIS primary implementation) | decides whether the GW190814 non-detection is compatible with universal shedding or falsifies it; `g`-band verdicts already robust |
| D8 | Shedding efficiency `ε(M,a,q)` + shutoff location | derive mass/spin/ratio dependence from `K_max(N)` combinatorics, spin-ordered reabsorption, or remnant-trap physics, with any shutoff location as *output* | highest-value attack surface on universal shedding; a derived shutoff between gap and BBH masses must land where it lands (same no-insertion rule as the 44 M☉ null) |
| D9 | Raychaudhuri (focusing) for leg bundles | derive focusing for SI fronts on leg networks (seed: AT congestion slowdown); closes the Jacobson chain to Einstein's equations with `η = 1/4` from I1b, `G = 1` | promotes I6c from open bridge to derived; gates nothing else — T8–T11 stand without it |
| D10 | Tension spectrum: simulator d-dip around mass + tension→`κ` map (v0.6) | (a) an over-coordinated (tense) region in the graph shows the GR fingerprint shape (near dip, overshoot, →3⁺) under info-side `d_eff`; relaxed `z≈4` regions show `d=2` fabric / `d=3` reconstruction as applicable; (b) Ollivier–Ricci `κ` tracks over-coordination (`z−4`) quantitatively | P0' first quantitative wire; failure of (a) shape-match after the mapping is fixed refutes P0'. v0.6 probe: bare shortest-path rejected for tense regions (inverted far side: shortcuts shrink balls, GR needs stretched rulers); D10b: tortuosity-import costs partially recover (no flip), `c_eff`-import costs give full dip → overshoot → asymptote on 9×9 mild plug (conditional on bridge); amplitude scales loosely with χ; κ is an interface pattern (criterion (b) reformulated); tension-imprint conjecture stated in §5; T15 cost-dominance is the cost-rule diagnostic; `M_O` = quotient + five criteria; substrate family measured (tri/hex/noisy +, gated-wall/rewired −); rewire sweep N*~O(10) flat in L (measured medians 20/10/10; α≈0 over range; asymptotic f*→0 hypothesis); RG blocking λ 0.013→0.31 (y≈1.5 rough) |
| D11 | Far-field tail exponent of the tension fingerprint (D10b) | measured `E(r)` tail on `L ≥ 200` with clean windows to `10Rc`: `1/r` (wedge shadow, delayed nodes `~ Rc·r`) vs `1/r²` (fixed shadow, deficit `~ Rc²`) | feeds the tension-imprint conjecture amplitude clause; no direct kill wire (shape detail, not shape itself) |
| D12 | Reconstruction universality: why admissible `M_O` converge (essay §8) | quotient `M_O(G)=[G]_{∼_O}` + five admissibility criteria (D10); ≥2 admissible `M_O` converging to the same IR geometry | meta-criterion over D3/D4/D6/D10; P4 audit: (1)(2)(3)(5) pass, (4) partial; a second admissible `M_O` with robustly non-3D IR refutes the P0' program |
| D13 | Emergent causal order: control + 4 stages (essay §8) | D13.0 static control measured (analytic `V_G`, `8r+4` law, substrate family ±, sign pattern); stage-1 spec filed (`V_U`/`Ṽ_U`, do-intervention, 3 controls); open: (1) `U→T_U,≺_U`; (2) cone under same `M_O`; (3) clocks unimported; (4) Malament interval → T8–T11 | extends D1 (D1 provides `U`); same-`M_O` + C1–C5 falsifier with D12 |

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

**Tension-imprint conjecture (fingerprint universality; D10b).** Under
information-transfer costs set by local congestion via the *fixed* ceff rule
(`w = 1+χ`, `χ_v = max(0,deg−4)/4`, saturating `x = χ/(1+χ)` bridge), *every*
localized tension region in relaxed fabric imprints the GR fingerprint shape
on info-side `d_eff` — dip, then overshoot, then asymptote to fabric — with
dip depth, overshoot height, and far-field coefficient scaling monotonically
in χ, plus the κ interface profile (boundary-negative, core-positive).
Evidence (not proof): 9×9 χ~1 full shape (dip −0.18 → peak +0.79 → +0.09);
amplitude trio (dip-min 0.20/0.077/0.016, peak 0.79/0.94/2.91, far-field `A`
growing with χ); κ first measurement (clique −0.93/+0.89, mild −0.31/~0);
flip window `z_vac ~ [2,5]` containing P0' 4. Falsifiers: (i) a localized
tension geometry with no U-shape under the fixed rule (no re-tuning); (ii)
κ-profile absent on independent geometries; (iii) amplitude anti-scaling
with χ. Promotion: confirmation on ≥2 new plug geometries plus reducing the
two bridges (χ-analogy, x-map) to one — or deriving either — promotes the
cost rule to a P5/import and closes D10a (shape+amplitude). The rule stays
conjecture-grade until then: single-family confirmation, two bridges, and
mild selection (the rule that flips among two tried). Not a postulate yet.
T15 (cost dominance, §2) is the admissibility diagnostic for any D10b
candidate: shortcuts priced below their hop-saving are located, not
averaged away.

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
- Simulator d-dip: DEMONSTRATED conditional on the ceff cost bridge (9×9
  mild-plug dip → overshoot → asymptote + amplitude scaling, D10b) — shape
  is a graph result, but the bridges (χ-analogy, x-map) are assumed, not
  derived. No 2D + scale → 3D mechanism (open D3/D4/D6);
  tension→`κ` is a measured interface profile awaiting independent-geometry
  confirmation (D10b, criterion reformulated); no isostatic-stability
  derivation under graph dynamics (needs D1).
- No P5 cost postulate yet: the tension-imprint conjecture (§5) is
  conjecture-grade (single-family confirmation, two bridges, mild
  selection) with stated falsifiers and promotion criteria.
- No far-field tail exponent: `1/r` vs `1/r²` unresolved on `L = 120`
  (χ~1 looks `1/r²`-like to `6Rc`, χ~2 looks `1/r`-like to `5Rc`, then
  bursty/clipped); needs `L ≥ 200` asymptotics (open D11).
- No emergent-time derivation: `n`/`≺_U`/`τ` distinguished and the D13.0
  control measured (`t²` + plug sign pattern), but no update rule, no
  `T_U`/`≺_U` measurement, no clock model (D13 stages 1–4 open; D1
  provides `U`).
- No electromagnetic identification of `ψ`: EM1-FALSIFIED on four
  structural wires (static range saturates `ξ ≈ 0.53`; one propagating
  scalar mode; local phase moves `B`/`J`/`E` by order one; nodal drift
  tracks `v · q`, not `v |q|`); the signed charge is sheet-tied with a
  frozen conjugate (§10).
- No firing law for geometry change: BR27-NO-MODE derives the absence
  (downhill scans don't fire, spectral radius exactly 1, binary graph
  has no deformation coordinate); no rate may be shopped on top (§10).
- No history measure: TIME0-NULL + RAND0-MEASURE-DEBT + MEASURE0-DEBT
  (4/4 debt reasons) leave `μ(Γ)` absent; SYM-0 settles only the
  counting list (§10).
- No matter, no gravitational carrier from the coupled `(G, ψ)`
  dynamics, no vacuum-member selection (VACSEL0-NOMEASURE refuses
  without the missing measure); `ψ = 0` is the no-information limit,
  not the vacuum (§10).
- No J₂ uniqueness: the working fabric is forced, not derived; VAC-0
  Final MIXED dissolves the question into per-phenomenon classes
  (nothing needs J₂ only); the F mechanism and VAC-0Q stay open (§10).
- No rewire selector, no trigger: REWIRE0-DEGENERATE (no earned rule
  selects a rewire) and TRIGGER0-CONDITION (19 conditions, zero firing
  implications) leave kinetics absent; no TRIGGER-1 shopping (§10).
- No fiber measure: FIBER0-DEBT exhibits two inequivalent normalized
  rivals with 520 residual dof; no weighting without a new primitive (§10).
- No reservoir: RES0-XI determines what a reservoir would store
  (`R_merge` as an exact function of `ξ`) without inventing one;
  energy debt and information debt are distinct (§10).
- No derived observer quotient yet: QUOT0-OPERATIONAL is the mechanism
  (transporting symmetric sector); the DERIVED rung stays open (§10).
- No inter-event store dynamics: Q-DYN-0b holds Q frozen on all 414
  waiting rungs with the RES0-XI functional earned as event-local;
  event timing stays a separate primitive debt (§10).
- No black-hole entropy identification: BH-ENT-0 censuses exact joint
  orbits (8/67/701/10047/218083) and rejects volume/boundary/mixed —
  no tested asymptotic law, no S_BH claim (§10).
- No exact substrate class rule: SUBCLASS0-PARTIAL ties spectral vs
  combinatorial on E/H-shell/G and proves F/H_TAU exact rules
  impossible in frozen space; no unified condition (§10).
- No thermodynamic entropy from the area law: BHQAREA0-MAX earns
  S_Q = κ*A for isolated boundary information only — no temperature,
  no first law, no Hawking flux, no horizon claim (§10).
- No dynamical jet, no event forcing: JET1-NULL closes the jet route
  (stop rule, no JET-2) and EVENT0-EQUIV shows fixed-G flow never
  forces structural change — timing stays a separate debt (§10).
- No 3D core on random weaves: WEAVE0-INCOMPLETE finds volume and
  spectral never jointly 3D (no B+C cell); randomness alone does not
  make 3D (§10).

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
| `ψ_u`, `r_u`, `s_u` | node field `ψ_u = r_u + i s_u` (two real scalars) | FP1 (§10), `ballistic` |
| `H` | field law `H = -A` (frozen `J = 1`) | FP2 (§10), `ballistic` |
| `ρ_u`, `Q_ψ`, `E_ψ` | `|ψ_u|²`, conserved norm, `⟨ψ|H|ψ⟩ = -2ΣB` | §10 anatomy, `continuum` |
| `B_uv`, `J_{u→v}` | `Re(ψ*_u ψ_v)`, `2Im(ψ*_u ψ_v)` (continuity current) | §10 anatomy, `continuum` |
| `χ_+`, `χ_π`, `χ_-` | vacuum susceptibility operators (math response only) | §10, `bgresp` (distinct from congestion `χ`) |
| `[G]` | vacuum connectivity class (J₂ = working member) | §10, `docs/j2-status.md` |
| `d_O` | blind-observer reconstructed dimension (`2.02`) | §10, `obs1` |
| `X_red`, `d_FS` | `X/(relabel × U(1))`, projective metric | §10, `sym0` |
| `μ(Γ)` | history weight (absent: the measure debt) | §10, `measure0` |
| `ξ = (cover, d)` | covariant split residual (what the inverse needs) | §10, `split0` |
| `d_cont` | continuous fiber dimension (1–2; never 0) | §10, `split0` |
| `R_merge` | `−(ΔE_ψ + ΔE_G)` = exact `f(ξ)` (no reservoir invented) | §10, `reservoir0` |
| `Q`, `E_Q` | kept event record `(cover, d)`; event-local readout (frozen store, Q-DYN-0b) | §10, `store0`/`qdyn0b` |
| `h2(P_−)`, `H_Q` | isolated STORE information = banked qubit functional (QINFO0-IDENTICAL, 1.1e-16) | §10, `qinfo0` |
| `S_Q^∂`, `κ*`, `h*` | boundary Q-information area law `κ* = 4.2207`, `h* → 1` (BHQAREA0-MAX) | §10, `bhqarea0` |

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
  `massgaps` (lower-gap continuity + upper-gap null + GW190814 audit),
  `mergershed` (BU2: `q`-shape + mass independence derived,
  `frac(q) = η·2q/(1+q)²`; flat law kept as the O5 falsifier, sample
  adjudicates; `ε(M,a)` shutoff still open).
- **F** (§10): `ballistic` (P1 waves), `coherence` + `slit` + `tunnel`
  (interference), `potential` (POT-0) + `driven` (POT-1), `continuum`
  (EM-0) + `falsification` (EM-1), `malus` (sheet sectors), `obs0` +
  `obs0r` + `obs1` + `obs1_reveal` + `quot` (rulers, blind observer,
  quotient), `backreaction` (BR-0) + `phase` (BR-2) + `rigidity` (BR-1),
  `contraction` (BR-2.5) + `conservation` + `accounting` (CONS-0/BR-2.6)
  + `stability` (BR-2.7), `u0` + `time0` + `rand0` + `measure0` + `sym0`
  (dynamics completion + state census), `field0` (linearity null),
  `response` + `bgresp` (kernel + vacuum susceptibility), `vac0` +
  `vacfield` + `vacexc` + `vaccomp` + `vacselect` (LAW/class split +
  vacuum family), `hidden` + `hiddenbr` (dead-sector info + response),
  `zero` (nodal census), `grav0` (graph-only null), `vacdomain` +
  `vactexture` + `vacstab` (domain interfaces, hidden textures,
  long-time stability), `source0` (persistent sources), `split0` +
  `info0` + `merge0` + `fiber0` + `reservoir0` + `trigger0` + `rewire0`
  (inverse fiber, books, deterministic update, fiber debt, missing
  account, trigger census, rewire null), `store0` (kept-`ξ` reversible
  store), `dim3` + `dim3_reveal` (J₃ lift + blind reveal), `subclass0`
  + `scale0` (substrate class + large-L bank), `qdyn0` + `qdyn0b`
  (store-dynamics null + event-local readout), `bhent` (collapsed
  census), `dim31` (3D repaired rulers), `weave0` (random-weave core
  search), `qinfo0` (store/qubit identity), `bhqent0` (blind-store
  dimension), `bhqarea0` (boundary Q area law), `jet0` + `jet1`
  (jet search + NULL repair), `event0` (event necessity). Side apparatus:
  `spectroscopy` (SPEC0 null: no localized modes beyond controls),
  `stern_gerlach` (SG gate fails), `fep` (FEP0 null), `graphvk` (D1 graph
  instance closed at small-N ED: all:all `< 0.25` bits vs chain sag `> 0.4`
  at `N = 8`; large-N open).
- **Falsifiers**: AF quench ratio, `α ∈ [9.0,12.4]`, `A ∝ N` TN wire, LHC
  thermality below `k_crit`, `s_leg ≤ l_p²/4` wire, linear LIV, `p` wire, gap/BBH
  kilonova wires, NICER wire, Kerr-quadrupole future wire, field-program wires
  (second-`M_O` quotient refuter, `I > 0` linearity breaker — §10) — see the v5 kill
  table (`paper/v5/main.tex` §6) and `docs/observation-protocol.md`.
- **Reproduce**: `pip install -e ".[dev]"`, `pytest tests/ -q` (2545 tests),
  `python scripts/generate_figures.py` + `python scripts/generate_v5_figs.py`
  (86 figure files, Figs 1–75), `streamlit run app.py`.

Counts above are v5.10 (`main.pdf` 13pp + `supplement.pdf` 22pp, S1–S12, 49
references cited). The v4.1 sources were removed after v5.7 (recoverable
from git history); v5 is canonical.

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
2 torch/GPU-only skipped. Suite at v0.7: 1789 collected (field-program
campaigns banked; L0/L1/L2 pins unchanged). Suite at v0.8: 2194
collected, 2192 passed, 2 torch/GPU-only skipped (twelve follow-up
campaigns banked: VAC-0 completion, SPLIT-0, REWIRE-0, MERGE-0,
RESERVOIR-0, TRIGGER-0, FIBER-0, INFO-0, VAC-DOMAIN-0, VAC-TEXTURE-0,
VAC-STAB-0, SOURCE-0; L0/L1/L2 pins unchanged). Suite at v0.9: 2253
collected, 2251 passed, 2 torch/GPU-only skipped (STORE-0, DIM-3-0
banked; consistency tests repointed to the v5 paper; L0/L1/L2 pins
unchanged). Suite at v0.10: 2409 collected, 2407 passed, 2
torch/GPU-only skipped (SUBSTRATE-CLASS-0, SCALE-0, Q-DYN-0/0b,
BH-ENT-0, DIM-3-1 banked; L0/L1/L2 pins unchanged). Suite at v0.11: 2545
collected, 2543 passed, 2 torch/GPU-only skipped (WEAVE-0, Q-INFO-0,
BH-Q-ENT-0, BH-Q-AREA-0, JET-0/1, EVENT-0 banked; L0/L1/L2 pins
unchanged).

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
  v0.7 adds the F-layer (§10: field postulates FP1/FP2, derived anatomy,
  J₂ working fabric, backreaction ontology + accounting, observer
  quotient, vacuum family, hidden sector, response kernel, filed dynamics
  debts) with no number changes, no new D-numbers, and stable L0/L2;
  L1 T7/D1 record the merged small-N `graphvk` closure.
  v0.8 extends the F-layer (§10: VAC-0 completion FINAL MIXED with the
  LAW/CLASS per-phenomenon split, vacuum domain/texture/stability trio,
  SOURCE-0 INCOMPLETE, MERGE-0 deterministic consolidation, RESERVOIR-0
  ξ-accounting, TRIGGER-0 conditional coupling, FIBER-0 fiber debt,
  INFO-0 matched conservation, SPLIT-0/REWIRE-0 fabric operations) with
  no number changes, no new D-numbers, and stable L0/L1/L2.
  v0.9 extends the F-layer (§10: STORE-0 reversible kept-`ξ` store,
  DIM-3-0 J₃ quotient-cubic lift with 2D-capped rulers, 3D-blind-rulers
  debt) with no number changes, no new D-numbers, and stable L0/L1/L2.
  v0.10 extends the F-layer (§10: SUBSTRATE-CLASS-0 PARTIAL substrate
  rules, SCALE-0 large-L bank, Q-DYN-0/0b frozen store + event-local
  readout, BH-ENT-0 UNCLASSIFIED collapsed census, DIM-3-1 GEOMETRIC
  repaired 3D rulers with transfer-validation debt) with no number
  changes, no new D-numbers, and stable L0/L1/L2.
  v0.11 extends the F-layer (§10: WEAVE-0 INCOMPLETE random-weave core
  search, Q-INFO-0 IDENTICAL store/qubit identity, BH-Q-ENT-0
  UNCLASSIFIED blind-store dimension, BH-Q-AREA-0 MAX boundary
  Q-information area law with BH-entropy debt, JET-1 NULL jet-route
  closure, EVENT-0 EQUIV flow-never-forces) with no number changes,
  no new D-numbers, and stable L0/L1/L2.
  Any number changed here must change in the same PR in the S1 audit table or
  be flagged as a deliberate divergence. One deliberate divergence stands:
  T14 TeV absolutes follow the code (post-BS), not v5 prose (pre-BS).

---

## 10. The relational field program (F-layer)

Built on top of the L0 graph: two real scalars per node evolving under
`H = -A` on a working fabric, asking how geometry may change and what an
observer reconstructs. Authority for every verdict below is
`docs/scaffolding-history.md` (§§1–19), the named `docs/DEFERRED.md`
verdict section, or committed `data/` records; this section states, never
re-derives. **Names:** FP1/FP2 are field-program postulates — not model.md
P1 (wiring) / P2 (edge), and F1–F6 stay L2 calibrations. Status words follow
the scaffold: POSTULATE, DERIVED, EMPIRICALLY ESTABLISHED, WORKING CHOICE,
OPEN / DEBT.

### FP1 (field postulate). Two real scalars per node.

Each node carries `(r_u, s_u)`, written `ψ_u = r_u + i s_u`. No vector,
momentum register, or coordinate is stored at the node. Status: **POSTULATE**
of the field program; the frozen node field of every campaign below.
(`ballistic`.)

### FP2 (field law). `i ∂_t ψ = H ψ` with `H = -A`.

`A` is the adjacency (`J = 1` in the frozen convention; hopping only).
Status: **WORKING LAW** — the one-way map from a fixed graph to `ψ`,
not derived from a deeper dynamical principle. Once granted, the anatomy
below follows and VAC-0A shows it holds on every simple graph.
(`ballistic`.)

### Field anatomy (DERIVED for every simple undirected graph).

`H = -A` is real symmetric, so evolution is unitary: `ρ_u = |ψ_u|²`,
`Q_ψ = Σ_u |ψ_u|²`, `dQ_ψ/dt = 0`. The bond correlator splits into a
symmetric part and an antisymmetric part:

```
B_uv     = Re(ψ*_u ψ_v)            bond energy
J_{u→v}  = 2 Im(ψ*_u ψ_v)          continuity current
dρ_u/dt + Σ_v A_uv J_{u→v} = 0
E_ψ = ⟨ψ|H|ψ⟩ = -2 Σ_{(uv) ∈ E} B_uv
∂E_ψ/∂A_uv = -2 B_uv               conjugacy (central scaffolding identity)
```

Quadrature, algebraic: `B ~ cos Δθ`, `J/2 ~ sin Δθ`. Some backreaction
readouts store the bare imaginary part — exactly half of this continuity
current; the factor is a convention, not a second current. Nothing about
J₂ enters: VAC-0A (A1–A6 identities on hostile graphs) promotes the
anatomy to **LAW**. First pinned on the J₂ stack inside EM-0.
(`continuum`, `vac0`.)

### Propagation and response (EMPIRICALLY ESTABLISHED).

Direction is collective phase, not a node-level arrow (POT0-COLLECTIVE:
symmetric source spreads without direction; coherent packet goes
ballistic; phase scrambling kills direction; coherence restores it).
One field has a static regime and a propagating regime (POT1-FIELD +
EM0-BACKREACTIVE): stationary source-relative response plus a front when
the source changes — no second field required. EM-0 adds the continuum
reading later tests use (J₂ Bloch bands, long-wave Schrödinger sector,
continuity to numerical zero, same `B`/`J` quadrature) with no Maxwell,
charge, or photon claim. (`potential`, `driven`, `continuum`.)

### EM1-FALSIFIED. `ψ` is a complex relational scalar, not ordinary electromagnetism.

| Test | Result |
|---|---|
| Long-range gapless static sector | fail; static range saturates (`ξ ≈ 0.53`, range 3) |
| Polarization | fail; one propagating scalar mode (the MALUS sector) |
| Local gauge redundancy | fail; a local phase moves `B`, `J`, `E` by order one |
| Propagation / cone | fail; nodal drift tracks `v · q`, not `v |q|` |
| Signed source | unresolved; conserved signed charge exists, tied to the sheet automorphism with frozen conjugate |

The field results above survive; the EM program is closed unless the
ontology changes (new degrees of freedom, or a different substrate).
(`falsification`.)

### Fabric: J₂ working choice plus operational geometry.

J₂ is the canonical working vacuum substrate: **WORKING CHOICE**, forced —
adopted because later work needs one concrete sheet and J₂ survives the
required probes (exact square quotient with shells `4r`, UV structure
kept, family-typical perturbations, formation transfer, no persistent
orientation). Forced is not derived: **substrate uniqueness stays debt**.
VAC-0 is complete (FINAL MIXED): per phenomenon, generic law or class
member — **nothing requires uniquely J₂**. LAW: A-identities, D-ballistic
propagation (10/10 cells, any coordination/bipartiteness), H-core (16/18
gates on 27/27), I finite-range label (26/27), J-algebra (27/27 exact),
MZ at LAW level. CLASS: F-interference (square: open/square/J₂/quotient
pass, tri/hex/rewires fail phase), E (2D-ordered; rings fail aperture
gates), H turn-on (broad, 15/27; hex shells + expander TAU reversal),
G tunnelling (square-grade at TUN level; the frozen all-FAIL battery is
a gate artifact — J₂ matches transfer-matrix prediction to <3%),
J-usefulness (13/27). Degree-preserving rewiring destroys F/H/G/DE
validity (degree-only vacuum excluded) while alternatives survive
everywhere (not J₂-selected). The substrate-uniqueness debt dissolves
into per-phenomenon classes; open threads: the F mechanism, unified
H-turnon, the LB = 8 floor, held-out VAC-0Q. (`vac0`,
`docs/vac0-verdict.md`, `docs/j2-status.md`.)

Independent rulers on J₂ meet (OBS0R-METRIC): graph balls/Hausdorff match
the square control (gap 0 at L = 128), diffusion/spectral agree to 4
decimals (gap 0.0005), the coherent-wave ruler disagrees at small L and
converges as a finite-size residue (gap 0.134 at L = 128), and the
all-path static POT ruler joins the same geometry — six pairwise ruler
gaps pass. The blind observer (no graph, coordinates, or dimension
target) reconstructs the quotient, not the microscopic graph
(OBS1-QUOTIENT): `d_O = 2.02` unprompted, `d* = 2` on train and test,
distance match 8% against the quotient (twice as close as microscopic),
local charts 6%, locality above 95%, sheet contrast below 0.03;
expanders come out non-2D (`d* = 3`). `M_O(J₂) ≈ J₂ / sheet`. A
static-channel floor blocks a full three-way cross-probe at L = 128;
calling the quotient metric spacetime is not established. (`obs0`,
`obs0r`, `obs1`.)

The quotient has an operational mechanism (QUOT0-OPERATIONAL): the
symmetric sheet sector transports while the antisymmetric sector is
exactly dead under `H = -A` (MALUS-0 M0-NULL) — only
quotient-compatible modes carry information, and that is the geometry
the observer reconstructs (symmetric projector returns the quotient
with `d` drift 0.022; antisymmetric measures no geometry; a bilayer
control stays two worlds at layer contrast 0.61; a staggered onsite
perturbation induces only order-`ε²` remote sheet signal). The DERIVED
rung stays open: four pre-registered sub-bars were design errors in the
ratio tests, filed with autopsies, never retuned. (`malus`, `quot`.)

DIM-3-0 lifts the fabric to J₃ (`J₃ = Z³ ⋊ Z2`, 12 gens) and finds the
quotient survives but the 2D-calibrated rulers do not (DIM3-GEOMETRIC):
the lift is exactly quotient-cubic (mult 4, `[H,S] = 0`, dead
antisymmetric sector, Bloch bands with isotropic Γ Hessian), the metric
reveal confirms 3D quotient geometry (distance match 4–7%, 2.1–2.6×
closer than microscopic at L12+, MDS-3 charts pass where MDS-2 fail
exactly as pre-registered, sheet contrast 0.0), and far-field spreading
reads `r⁻¹`/`r⁻²` at L20+ with J₃ identical to the cubic control on
every readout — but blind dimension reads `d* = 2` on known-3D data
three proven ways (`d*` structurally capped at 2 by the
majority-distortion rule; arrival supralinearity `M ~ r^1.48` from
threshold-plus-decay, predicting the `R²` volume growth to 1%;
static-range compression `∝ 1/ξ`), fronts ride at 2/3 of bound on J₃
and cubic alike (forerunner artifact; packets at Bloch speed), and the
current exponent chirps (1.53–1.66). No post-data bar moved; the
3D-geometry result stands where the apparatus validates, and
3D-calibrated rulers are DIM-3-1 work. (`dim3`, `dim3_reveal`.)

DIM-3-1 repairs the estimators and measures J₃ blind
(DIM31-GEOMETRIC): dimension reads 3 through six independent channels
(arrival-time transfer + direct medians 3.458/3.552/3.757 at
L16/20/24, `d*` 9/9, charts 9/9, static L20 2.932 / L24 3.135 with
J₃/cubic static identity to six decimals, 3D spread laws, packets at
Bloch speed) — but the cubic-gamma transfer the arrival channel
relies on disagrees with J₃'s own gamma beyond the calibrated bar at
L16 (by 0.007) and L20 (by 0.042), passing barely at L24. By the
frozen all-gates rule the verdict is GEOMETRIC, not OPERATIONAL: every
dimension-reading channel is unanimous at 3; what failed is a transfer
validation leg, decaying with L, consistent with finite-size
fiber-antisymmetric contamination (a follow-up hypothesis, not a
correction). (`dim31`.)

The substrate question is narrowed structurally and banked at scale.
SUBSTRATE-CLASS-0 characterizes the VAC-0 class on a 31-cell frozen
battery (SUBCLASS0-PARTIAL): E, H-shell, and G admit exact minimal
rules each in BOTH spectral and simple-combinatorial form
(E = {disp_dim_2} or {superlinear_ball}, H-shell = {not_hex} or
{not_hex_local}, G = {square_class} with the frozen plaquette form
non-minimal), while F, H_TAU, and J_useful provably admit no exact
rule in frozen space (F: the two J2-swap seeds share identical
feature vectors with split labels — defect location, not global
structure; H_TAU: the ring floor artifact plus the rr3 puzzle; best
rule diameter with 4 errors). Spectral vs combinatorial ties on every
exact component, so SUBCLASS0-SPECTRAL is refused; no unified
cross-component condition exists; sheets are necessary for nothing
tested. One data-quality flag stands: VAC-0 prose says J-useful
13/27, the JSON record counts 12 — JSON authoritative, prose flagged
for erratum. (`subclass0`.) SCALE-0 banks the large-L asymptotics
(SCALE0-BANKED, 178/178, L64–512): `d_H` 1.9098 → 1.9725 monotone
toward 2 with j2 == sq to machine precision (substrate universality
of the volume-growth exponent), `d_s` L-independent, exact forms
upheld (QUOT anti/sheet remote exactly 0.0 to L512, VACEXC
cross-deviations exactly 0.0), velocities exactly L-independent
(local pre-horizon physics), POT `ξ`/range exact at all L, packet
speed vacuum-independent (1.9028 in all 4 vacua). (`scale0`.)

The random alternative to the regular J₃ fabric shows no 3D core.
WEAVE-0 tests Poisson-sheet weaves over a coupling ladder
(WEAVE0-INCOMPLETE, ambiguous: no core, not stably 2D/nongeometric;
270/270 grid cells): the apparatus validates (B/C controls read C0
as 2D and C4/C3 as 3D; C5 never matches, 0/8), but volume reads
3D-side only at `λ = 0.01` (B-head 5/8; 2/8 at 0.005, 0/8 above with
overshoot past 3.5) while spectral never reads 3D jointly (0/8 at
every rung, 2.05 → 2.77; 3D only at `λ = 0.16` where volume
explodes) — no B+C joint cell, so `core_lams` is empty. E/F and H
legs are filed apparatus-invalid (controls fail), not repaired.
Randomness alone, as woven here, does not make 3D; the J₃/WEAVE
universality question stays open with a first negative data point.
(`weave0`.)

### Backreaction: `B` couples to connectivity; accounting is not a firing law.

Three independent uses of `B` meet: the conjugacy `∂E_ψ/∂A = -2B`
(**DERIVED**), the energetic selectivity of excitations (BR-0:
BR0-D-SELECTIVE* — the zero field is exactly flat under the sampled
moves while an excitation opens energetically favorable channels; §13
below re-reads that flat state as the no-information limit, not the
vacuum), the phase response (BR-2: BR2-QUADRATURE — structural response
tracks `cos Δθ` through `B`, staggered flux tracks `sin Δθ` through
`J`), and the contraction sum map (BR-2.5: `ψ_[uv] = ψ_u + ψ_v`,
`Δ‖ψ‖² = +2 B_uv`). Conclusion: `B` is the field quantity coupled
directly to connectivity. `B` causes gravity is not established (see
GRAV-0 below). (`backreaction`, `phase`, `contraction`.)

The admitted primitive is the local exchange `u—v ↔ [uv]`
(BR25-ONTOLOGY): local, simple-graph-preserving, repeatable into
collapse; remote relocation is demoted to a formation/diagnostic tool.
Contraction is many-to-one, so a record-free split has many preimages
(CONS-0: powers of two, plus amplitude-match degeneracy; the sum-map
information loss is exact, `|a − b|²/2`). SPLIT-0 narrows **split
selection** to a measured residual (SPLIT0-MIXED): every tested inverse
decomposes into forced-plus-residual (`M + ξ ↔ X`, 824/824 roundtrips,
minimality 76/76), where the covariant residual `ξ = (cover, d)` is
exactly what must be supplied beyond the merged state; the full inverse
is never a singleton (continuous fiber, `d_cont` 1–2); halves-restricted
determinism holds exactly on the 4 isolated-node cells; reverse support
is exact on the halves subset (36/24/0), correcting 3 MEASURE-0A cells
(J-multiset orientation artifact). No measure derived. What remains is
the fiber measure over `ξ` (FIBER-0 files it: two rivals, 520 dof).
STORE-0 shows what a kept record buys (STORE0-REVERSIBLE, 46/46): with
the full `ξ` stored, split recovery is exact (5784/5784 fiber rows over
235 events on 79 cells; 5 sequences reversed exactly; disjoint
factorization with additive `R`) and the merge/split energy account
closes from the same stored content (`< 3e-14`); minimality is earned
(cover-only fails everywhere, `d`-only fails on all multi-class cells,
scalar-`R` fails on all 78 non-injective cells) — ontology: discrete
`c` plus `d` required. No sampling is needed given the complete
microscopic state; the store is kept information, not derived selection.
Q-DYN-0/0b close the store-dynamics question (QDYN0-INCOMPLETE
autopsy-resolved, then QDYN0B-EVENT-LOCAL, 51/51): Q stays bitwise
identical on all 414 waiting rungs with current-M reversal and the
semigroup exact, and the Q-DYN-0 red legs are premise errors — merged
states are not eigenstates of the post-merge H(G₂) (residuals
0.094–0.458), and the `Re(d̄W)` readout provably rotates under phase
flow for `d ≠ 0` cells (true-eigenvector spread 1.76 vs 3e-13 at
`d = 0`). The RES0-XI functional R is earned as an event-local
accounting functional, not a persistent stored-energy term
(`E_aug` drifts to 2.05 while `E_ψ + E_G` holds to 2.4e-12;
inverse-split account equals the negative of the CURRENT account to
3.1e-15; closed cycles return to 5.4e-15): it is evaluated when the
structural map executes, while between events only the field energy
is conserved. Zero evidence for Q dynamics; no further Q-dynamics
campaign is justified; event timing stays a separate primitive debt.
(`qdyn0`, `qdyn0b`).
Q-INFO-0 identifies the isolated STORE information measure with the
banked qubit functional (QINFO0-IDENTICAL, 16/17 — the red gate is the
equiv-rule, red by design when IDENTICAL holds): `h2(P_−)` with
`P_− = |d|²/(|s|² + |d|²)` matches `S_banked` to `1.1e-16` (machine
precision vs a 1e-9 bar) under the exact Hadamard map (`H′H = I`,
Schmidt values `== √(P_±)`), with the same log base 2 and the same
`0 log 0 = 0` convention; multi-entry `H_Q` is filed separately from
local `h2` per the no-relations firewall, and the factor-two audit
reads `(d_R, d_I)` as one complex amplitude (no two-bit inference).
Handoff: later work reuses the earned qubit measure for isolated Q
modes instead of inventing an entropy; relations between entries and
any thermodynamic reading stay out of scope. (`qinfo0`.)
On pristine J₂ the neutral drift the legal moves allow destroys
the vacuum class in a handful of moves at every tested size (BR1-FLAT):
**neutral quiescence stays debt.** The remaining local degree-preserving move admits no
deterministic exact-physics selector either (REWIRE-0:
REWIRE0-DEGENERATE — 24/24 J₂-L4 states DEGENERATE-or-ABSENT under all
six exact principles, scale-persistent to L28; exact-energy selection
fp-fragile at ulp). (`contraction`, `conservation`, `rigidity`,
`split0`, `rewire0`, `store0`).

Event accounting closes conditionally and exactly where it closes
(CONS0-PARTIAL + BR26-ACCOUNTED): cycle rank on triangle-free domains
changes by the local contraction count; the ledger closes end to end
when `B` sits on the admissibility surface `B = B_*(c)` (six constructed
families, residuals at `1e−13`); the contraction energy change has an
exact formula that `B` alone does not balance. Proved absent: no linear
combination of node count, graph energy, `Q_ψ`, `E_ψ` is conserved for
arbitrary states; no graph reservoir closes the books; split
conservation constrains but never selects. Zero-field contraction stays
allowed. Conservation yields admissibility and equalities — never a law
that says when the graph fires. MERGE-0 characterizes the update side
(MERGE0-DETERMINISTIC + MERGE0-ACCOUNT-DEBT, 38/38): selected-edge
contraction is a unique covariant deterministic primitive (`R × U(1)`
exact on all 325 events, incl. 87 annihilations) with exact ledger
(`dQ = 2B`, `dE = P1 + P2`, `P3 = P4 = 0`, support `2 + n_cross`);
HIDDEN-BR SIGNREV survives execution (2/24 on-support); no existing
variable closes the reservoir (0/80 tuples); favorable orderings on
19/30 scans, still no firing rule. RESERVOIR-0 determines what the
reservoir would have to store (RES0-XI, 68/68): `R_merge = −(ΔE_ψ +
ΔE_G) = A + |d|²/2 + Re(d̄W)` exact to `≤ 1e−9` on 26,992 fiber rows
— an exact zero-parameter function of the lost `ξ`, swap-bitwise,
`R_split = −R_merge`, one-neighborhood-local, disjoint-additive; and
`R` never vanishes on the halves subset (min 0.167), so energy debt
and information debt are distinct. TRIGGER-0 censuses the trigger
side (TRIGGER0-CONDITION, 75/77): 19 of 21 earned exact local
predicates survive as CANDIDATE-CONDITION on 257,668 edges with zero
firing implications — merge is an unknown trigger plus an earned
deterministic update. (`conservation`, `accounting`, `merge0`,
`reservoir0`, `trigger0`).

No firing mechanism derives from the instantaneous ontology
(BR27-NO-MODE): every uniform scan is downhill yet discrete maxima do
not fire; unitary `ψ` evolution has spectral radius exactly 1 (`H` does
not see `ψ`); the binary graph admits no continuous deformation
coordinate (a weighted path leaves the frozen kind of `H`). One further
primitive dynamical postulate is required before geometry changes; the
strong stop holds (no rate shopping on this null). (`stability`.)

### Dynamics completion: four debt-filing verdicts.

U0 asks for `(G_t, ψ_t) → (G_{t+1}, ψ_{t+1})` from admitted local moves
only: three contraction-only laws (bond sign, ledger sign, energy
selection) pass the structural gates, but splits are unrealized, energy
minimization ties (a theorem at zero field), and one-tick effects escape
the decision radius — U0-INCOMPLETE. TIME-0 asks whether two boundaries
pick one history: exact census (143 canonical classes, 102245 pairs)
gives unique-history fraction 0.051 below the 0.2 bar, the `T = 2`
uniqueness dissolves under truncation-free follow-up (0.554 → 0.073),
and the median history count from the initial state alone runs 74 to
`8×10⁵` — TIME0-NULL (microscopic reversibility intact, uniqueness
failed). RAND-0 builds the stochastic completion coherently (exact
admissible set, symmetry orbits, bitwise factorization, three agreeing
generators) but the measure is underived: micro-move-uniform and
orbit-uniform disagree at every nontrivial stabilizer, directed and
undirected coarse-grainings disagree everywhere tested, and the vacuum
is not quiescent at one-half per edge — RAND0-MEASURE-DEBT. MEASURE-0
formalizes the debt (544 cells, six HARD gates,
representation-independent): all four frozen debt-reasons trigger, so no
unique inter-outcome weighting is forced; CLOSED was data-reachable and
did not occur — MEASURE0-DEBT. Downstream may consume the apparatus and
the disagreement battery, never a tuned weight. FIBER-0 asks whether
earned physics constrains a normalized measure on the SPLIT-0 inverse
fiber (FIBER0-DEBT, 22/22): two inequivalent normalized closed-form
rivals satisfy every earned constraint (TV > 0 on 79 cells), with 520
residual dof (206 + 168 inter-orbit + 83 radial + 63 angular) —
DERIVED was reachable and did not occur; six sub-debts filed by name;
zero fitted params. INFO-0 closes the probability-free books
(INFO0-MATCHED, 19/19): pred == succ 143/143 (mirror theorem),
timed-skeleton identity, schedulers all `m!`, hidden books green,
TIME-0 recomputed exactly — exact counts with binary logs, no
`−Σp log p` anywhere. (`u0`, `time0`, `rand0`, `measure0`, `fiber0`,
`info0`.)

EVENT-0 shows fixed-G flow never forces structural change
(EVENT0-EQUIV, 33/33): all 426 rungs of all 71 trajectories stay
valid (`t* = +∞` everywhere), Q bitwise frozen, reversal exact —
but 61 exact nontrivial same-N rewire-equivalence orbits exist on
small symmetric graphs (same state mod `R × U(1)` under a relabeled
edge set), while J₂-L4 is ruled out graph-first (0 cospectral rewire
neighbors of 9792/leg). The orbits are equivalence surfaces, not
triggers: zero firing implications, with 2493 exact time-crossing
edges filed as TRIGGER-0-consistent conditions. EQUIV, not FORCED;
no EVENT-1 shopping. (`event0`.) JET-1 closes the dynamical-jet
route (JET1-NULL, 13/13): repairing JET-0's malformed aggregate
`compat_keys` comparison with the correct per-rung bitwise check (0
mismatches over 1152 bits; JET-0 apparatus + 496-record bank consumed
read-only, banked JET0-INCOMPLETE 31/32 reproduced exactly) promotes
no surface — `n_genuine = 0`, 0 crossings on 18 ordinary
trajectories under unchanged definitions. Filed stop rule: no JET-2;
event-occurrence passes to TIME-Q-0, then to an explicitly new law.
(`jet0`, `jet1`.)

Synthesis: admissible states plus admissible local transitions give
admissible histories; the weight `μ(Γ)` on them is missing — the
**history-measure debt**. What counts as one microstate is settled
(SYM0-CLOSED, 1973 cells, 8/8 gates): representation redundancy is
exactly node relabelings and global phase, so the state space is
`X_red = X / (relabeling × U(1))` with projective metric `d_FS` at
fixed nonzero norm — graph symmetries, time reversal, observer
equivalence, and accidental degeneracies are all tested non-redundant.
No Born rule is attached. (`sym0`.)

Collapsed-region multiplicity is censused exactly
(BHENT0-UNCLASSIFIED, 153/153): exact joint graph-field-store orbits
8/67/701/10047/218083 on paths P2–P6 at fixed boundary (log₂ slope
3.67, R² = 0.9945 — yet strict VOLUME rejected by second differences
and a quadratic F-test at p = 0.0052, BOUNDARY rejected by growth at
fixed boundary, MIXED rejected by the full-wiring branch at R² =
0.928 off-band). Interior-graph multiplicity dominates and is
volume-superlinear (`~2^{n²/2}/n!` quotient-corrected); boundary
wiring is polylog/saturating (path leg wirings = 2 for all n).
Matched sign pairs are 36/36 near+far blind on J₂ (VPLUS and VPI, L6
and L28) vs 0/12 paths and 0/16 square: hidden-sector field
multiplicity is exterior-blind and extensive in |R|, while graph
multiplicity is dynamically exterior-visible (POT distinguishes graph
pairs). No asymptotic law supported, no S_BH identification anywhere
(firewall held), no finite field-fiber count derived (MEASURE0-DEBT);
blind-submanifold dims filed. (`bhent`.)

The exterior-blind continuous STORE dimension is topology-dependent
with no universal law (BHQENT0-UNCLASSIFIED, 34/34 — the pre-data
prediction): joint D is 0 on paths and squares, `2n−4` on stars, `n`
on J₂ disks, with matched-`(n, b)` pairs splitting by topology; all
law gates miss (boundary R² = 0.68 vs 0.70 bar, volume 0.89 vs 0.90,
`b log b` 0.72), near-misses reported unmoved and unshopped. Blind
weight concentrates boundary-adjacent; the complex-`d` factor two is
resolved (`N_split = 0`); VMINUS halves the J₂ blind dimension;
the STORE leg is fully POT-blind where BH-ENT graph legs are
POT-visible. No measure, no bits, no entropy (`entropy_blocked`
true). (`bhqent0`.)

Isolated boundary Q-information obeys an area law at maximum density
(BHQAREA0-MAX, 22/22) — the first earned area law in the program: a
complete-graph core in a J₃-ball ladder (`r = 1..10`) gives
`S_Q^∂ = κ* A + o(A)` with `κ* = 4.2207` bits/unit-area,
`σ* = 4.2208` channels/unit-area, `h* = 0.999990` bits/channel
(`h̄` ladder monotone 0.72 → 1; power `p(S vs A) = 0.92`;
volume-density strictly decreasing, ruling out a volume law). The law
is doubly selected: patterns give `S = 0` exactly (the MAX law is a
vacuum-on-BH-geometry property, not a property of any state), and the
plain-J₃ control gives a non-MAX law (`κ = 0.43`, `h ≈ 0.10`) with
disjoint boundary distributions (`KS = 1.0`) — the complete core
selects MAX. One disclosed amendment (domain-vs-domain G–J; v1
NONUNIVERSAL preserved, freeze byte-identical); the conditional
`a/ℓ_P = 3.42` carries NO agreement claim. Firewall holds: isolated
boundary information only — not Bekenstein–Hawking entropy, not a
horizon, not Hawking radiation. (`bhqarea0`, on frozen QINFO0 input.)

### The vacuum field is a family; `ψ = 0` is the no-information limit.

VACFIELD0-JOINT (frozen `(J₂, H = -A)`, no geometry-update rule,
candidates fixed by spectrum and symmetry before consequences were
read): three nonzero states reach the full JOINT ladder (stationary,
perturbation-stable, current-free, uniform stress, amplitude-coherent,
linear, normalized-robust, zeros in place, sector recorded, exact
symmetry-predicted ledger), while `ψ = 0` stops at BACKGROUND — no
relational information (`Bmax = 0`), phase undefined at every node, a
ledger with no distinguishing power:

```
VPLUS    ground state, E = -8, flat ledger, sector P+ (propagating, quotient-visible)
VPI      variational maximum, E = +8, one-sided ledger, sector P+ (propagating, quotient-visible)
VMINUS   E = 0, symmetric ledger, sector P- (joint as a state, operationally decoupled)
ψ = 0    no-information limit, not the vacuum
```

Perturbations propagate identically on all four backgrounds (packet
speed 1.9204, bitwise-identical `δψ`): the nonzero states add a
uniform, phase-defined, stationary relational background with a
predictive ledger. No member is chosen; tie-breaking by later
consequences is refused. (`vacfield`.)

Excitations see every vacuum the same way (VACEXC0-COMPLETE, 241
tasks): `δψ = ψ − ψ_vac` evolves as `δψ(t) = U(t)δ0` in the co-evolving
frame (split error `≤ 1.2e-13`), bitwise-identical across VPLUS, VPI,
VMINUS, and ZERO. The carrier is background-independent; per-vacuum
differences live in the relational response (see susceptibility
below). (`vacexc`.)

The joint manifold is fully censused (VACCOMP0-COMPLETE, modulo
`R × U(1)`): on even L, two isolated extremal rays (VPLUS at `E = −8`,
VPI at `E = +8`, both nondegenerate) plus one hidden real `RP¹` JOINT
circle (the VMINUS–VSTAG span in the `P₋` zero-energy sector, JOINT
except at `B = 0` BACKGROUND points), each times a full amplitude ray
(`10⁻³…10³` all JOINT) — `π_0 = 3`; on odd L only VPLUS and VMINUS
rays survive (VPI frustrated) — `π_0 = 2`. Generic eigenstates are
excluded (current binds complex 16/16, stress binds real 8/8);
mixed-eigenvalue beats sit at `dE = 16/8/8` with no interior JOINT and
no cross-term cancellation; ledger classes are distinct per member.
(`vaccomp`.)

Member selection refuses without a measure (VACSEL0-NOMEASURE, the
pre-registered predicted outcome): the MEASURE gate re-evaluated from
code is not ready (all four MEASURE-0 debt-reasons hold), so none of
the 23 headline selection stages ran — all refusal records, no vacuum
ranked, no weight chosen. (`vacselect`.)

Interfaces between disconnected JOINT components are radiative
(VACDOMAIN-RADIATIVE, 7/7): all 9 disconnected joins emit ballistic
`|δρ|` fronts (`v ≈ 5–6.1`, `R² 0.89–0.92`, reach 4–6 cells) while
S-steps persist (0.999) and bulks hold — hidden-hidden joins exactly
stationary, mixed P₋ weight frozen at 1/2, spectral superposition
exact (`I = 0`). Hidden orientation textures are visible but silent
(VACTEXTURE-GRADIENT, 14/14): obstruction zero bitwise (`E = 0`
everywhere), gradients relationally real (local `D = 6.4e-4`,
coarse `1.3e-3`, ledger `dmax` 0.15/0.003, `B` slope +0.173) yet
dynamically void (symmetric amplitude exactly 0.0, `I = 1.6e-17`,
packets ballistic at `v = 1.92` on frozen backgrounds). Joint vacua
stay operationally close to vacuum to `T = 1000/4000`
(VACSTAB0-ROBUST, 9/9): small stays small, never focuses beyond input
scale (max 3.5 vs trigger 50), no late refocusing (0.499 below own
initial 0.704), margins positive with zero zero-steps, recurrence
background-independent and growing with L. (`vacdomain`,
`vactexture`, `vacstab`.)

### The dead sector stores local information that reverses geometric response.

Every hidden transformation tested — sign, phase, shape, amplitude —
distinguishes locally on at least one of `ρ`/`B`/`J` (5–6 orders above
bar) while remote shells stay at `≤ 5.2e-15` (wave and diffusion) and
the POT remote is exactly 0.0 (HIDDEN0-SEPARATED, 279/279): the
antisymmetric sector is transport-dead and informationally live — local
physics sees more than the quotient observer. (`hidden`.)

Matched states with equal energy and wave+POT remote blindness carry
different `B` landscapes, hence different `dE/dA = −2B` (HIDDEN-BR:
HBR0-SIGNREV, 214/214): equal field energy does not imply equal
geometric response — and 1346 edges carry strictly opposite-sign
virtual contraction ledgers, so changing only transport-hidden
information reverses the energetic ordering of structural alternatives.
A zero-energy pure-hidden state carries a nontrivial ledger (vanishing
bond field, non-vanishing gradient). All virtual; no graph operation
executed anywhere. (`hiddenbr`.)

### Linearity holds; the response kernel is banked per vacuum.

Fifty-seven collision cells on frozen `H = -A` evolve exactly as the
linear theory (FIELD0-LINEAR): the interaction witness stays at
numerical zero (`I = 0`) while `ρ`/`B`/`J` still show cross terms —
including large false accelerations (order 50–80) and a static
arrangement that looks forceful and is not (FIELD0-APPARENT). Any later
force or matter coupling must beat this null with `I > 0`, not a
picture of fringes. (`field0`.)

The map local `δψ →` remote `δψ → δρ, δB, δJ` is measured with no force
claimed (RESPONSE0-KERNEL-BANKED, G0–G14, 45 cells): the field front
rides at Bloch-max speed (`v = 7.95`, `v/8 = 0.993`), quadratic fronts
(`ρ`, `J`) ride slower (`v ≈ 5.94`), first-order `B`/`J` fronts on
nonzero backgrounds ride at field speed; distance laws `|δψ| ~ r^−0.50`,
`δρ ~ r^−1.00`, `δJ ~ r^−0.95`; the bipartite `B`-blindness theorem is
pinned (chiral-real data gives `B = 0` exactly) with the sharpening
that two-sublattice real regions are not blind (the prereg
overgeneralization was falsified and corrected). (`response`.)

Same carrier, different response per vacuum (BGRESP0-COMPLETE, 77
tasks): the susceptibility operators differ as operators
(`χ_+ ≠ χ_π ≠ χ_-`, pairwise Frobenius distance `√88` at every size),
each of rank `2N − 1` with the sole null direction exactly global
phase, while `χ_ZERO = 0` — pinned to floating-point precision.
"Susceptibility" means only this mathematical response of established
relational observables: no force, charge, or curvature is claimed.
(`bgresp`.)

A persistent source is boundary data `s(t)` on `δψ` in the vacuum
frame, and POT's stationary field IS its driven RESPONSE counterpart
(SOURCE0-INCOMPLETE, 9/10 — INCOMPLETE = falsified frozen prediction
with complete data): K1 dev 0.024–0.037, K2 exact to 6.6e-12, carrier
vacuum-independent with per-vacuum response via banked `χ` (42/42).
Switch-ON always radiates (`v = 5.5–5.6`); the falsified blanket rule
was release fronts — AMP/VPLUS release is silent by theorem (steady
state equals `c·u₊` to 7.4e-15) and AMP/VMINUS release is
beating-dominated and frontless. Rule: switch-OFF radiates only on
mismatch with free evolution. `R_G → dG` stays blocked by
MEASURE0-DEBT. (`source0`.)

### Zeros are nodal; graph-only gravity is a null.

Exact zeros are reachable but not generic (ZERO-0, 4432 ledger rows):
1588 certified-modal events, all from matched-amplitude two-packet
destructive interference at relative phase `π`, plus nodal eigenstates
(the only persistent class); generic and single-packet states yield
zero certified exact zeros in 1900+ rows while near-zeros are common.
A zero is a regular point of `(r, s)` with three exact relational
consequences (incident `B = J = 0`, `ρ̇ = 0` with quadratic touch,
undefined phase). Cycle winding changes without any zero, via bond
phase-slip at `|Δθ| ≈ π` — the continuum intuition does not transfer.
No zero is called a particle, defect, or source. (`zero`.)

No tested strictly local graph update both preserves J₂ and carries a
disturbance past the near field (GRAV-0): a gravitational carrier must
come from inside the coupled `(G, ψ)` dynamics, not from a retry of
graph-only relocation. GRAV-0 does not retract the merged L1
weak-field interface (Newton through Mercury, conditional on its
imports) — it says that interface has not been re-derived as a far
signal of local fabric updates. (`grav0`.)

### F-layer debts (filed by name, not number).

No new D-numbers are minted here (D14/D15 are taken in DEFERRED.md).
The open debts, each with its closer in `docs/scaffolding-history.md`
§19: **substrate uniqueness** (dissolved by VAC-0 Final MIXED into
per-phenomenon classes — nothing needs J₂ only — and narrowed by
SUBCLASS0-PARTIAL: exact minimal E/H-shell/G rules in tied
spectral+combinatorial form, impossibility proofs for F/H_TAU in
frozen space, no unified condition; SCALE-0 banks j2 == sq to machine
precision; WEAVE-0 finds no 3D core on random weaves; closer: the F
mechanism, VAC-0Q, or a surviving derivation);
**3D transfer validation** (DIM-3-1: repaired rulers read dimension 3
through six channels, but the cubic-gamma transfer fails tol_agree at
L16/L20 — GEOMETRIC, not OPERATIONAL; closer: a follow-up on the
fiber-antisymmetric contamination hypothesis or L24+ transfer);
**vacuum-field member** (a principle selecting inside the VAC-COMP
manifold without using later consequences — needs the history measure
first); **history measure** `μ(Γ)` (a reversible measure matching both
the whole-history and conditional-local readings; FIBER-0: two rivals,
520 dof); **structural
kinetics** (the firing postulate, if that is what it is — TRIGGER-0:
19 conditions, zero implications; EVENT-0: flow never forces, 61
orbits, zero implications; JET-1 NULL closes the jet route with a
stop rule);
**split information** (narrowed by SPLIT-0 to the fiber measure over
`ξ`; RESERVOIR-0: the missing account is an exact function of `ξ`;
STORE-0: a kept-`ξ` store recovers and closes exactly — kept, not
derived; Q-DYN-0b: Q frozen on all 414 rungs, R earned as an
event-local functional — no Q dynamics, timing stays debt;
Q-INFO-0: h2(P_−) is the banked qubit functional to 1.1e-16 — the
isolated-mode measure is earned, relations between modes are not);
**BH entropy** (BHQAREA0-MAX: isolated boundary Q-information obeys
S_Q = κ*A at maximum density — thermodynamic identification stays
open: temperature, first law, Hawking flux; BHQENT0 scopes the
dimensions as topology-dependent);
**neutral quiescence** (a dynamics making
the vacuum an attractor); **matter** (formation after a real dynamics,
beating the FIELD-0 null); **gravity carrier** (inside coupled `(G, ψ)`
dynamics). Blocked until the debts move: a complete graph dynamics,
formation under it, matter, the carrier, decay, and force
phenomenology beyond the FIELD-0 null.

---

*Index-card version: L0 says what the wiring is (all:all, monogamy, no interior
distance). L1 says what spacetime costs (4ln2 per leg, one GR input, borrowed
thermodynamics) and what that buys (scrambling, Page, Newton-to-Mercury,
quadratic-only UV). L2 says what compact objects are (one `k ∝ M²` family, shed
legs, flash in O5) and what kills it (ten clean misses). F says what the field
is (`ψ = r + is`, `H = -A` on J₂: derived anatomy, collective direction,
quotient geometry, a vacuum family with `ψ = 0` demoted, hidden information
that steers response) and what stays debt (firing law, history measure,
matter, gravity carrier). §5 lists exactly what
would turn calibrations into theorems. Everything else is evidence.*
