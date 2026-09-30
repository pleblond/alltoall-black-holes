# The relaxed vacuum: why 3D must emerge from rested information

*Companion to `docs/model.md` v0.6 (P0' postulate) and the `emergent_dim`
protocol. This document explains the reasoning; `model.md` states the
definitions. Nothing here is claimed as derived unless it names its test.*

Reading guide: §1–§2 are philosophy (why relaxation belongs to the
information side). §3–§4 are the postulate (2D, 4 edges, and what each word
costs). §5–§6 are consequences (only vacuum is perfectly 3D; mass is tense
vacuum). §7 is the verdict on total emergence today (bracket method, first
failure, what would flip it). §8 is the open road on time and causal order
(substrate target, scale-multiplicity mechanism, same-`M_O` falsifier).
§9 maps every claim to definition / measured /
open. Readers who only want the postulate can read §3–§4 and §9.

---

## 1. Relax the scene, not the photo

The model says the information graph `G` is ontological and spacetime is
observational: an observer sees `M_O(G)`, a reconstruction, never `G` itself
(`model.md` P0/P4 box). From this follows a methodological rule that the
whole program now obeys:

> **The variational principle lives on `G`. Spacetime inherits whatever the
> relaxed `G` reconstructs as. Optimizing spacetime directly cannot work.**

Why not? Two reasons, one practical and one fatal.

*Practical.* Optimizing `M_O(G)` cannot change `G`. It edits the photo while
the scene stays fixed. Any "relaxed spacetime" obtained this way is a
choice of reconstruction, not a property of reality — change `M_O` and the
relaxation evaporates.

*Fatal.* "Relaxed spacetime" is ill-posed: relaxed *toward what*? The only
available answer is "toward flat" — which smuggles flatness in as the target
and makes the derivation circular. This is exactly the circle the emergence
program exists to break: flatness must come *out*, so it cannot go *in*,
neither as a metric ansatz nor as a variational target.

The alternative is to relax the information and let spacetime follow. This
move has a distinguished precedent: Jacobson's entanglement equilibrium
(2016), where maximal vacuum entanglement entropy *implies* the Einstein
equations. The variational principle (`δS_ent = 0`) lives entirely on the
information side; spacetime curvature is its shadow. P0' below is the
graph-theoretic version of that move: relaxation = a coordination principle
on `G`; flatness and 3D-ness are properties of the reconstruction of the
relaxed state.

---

## 2. Vacuum is the most relaxed state

"Vacuum = ground state = most relaxed" is nearly tautological — in a good
way. A ground state is what remains when every excitation has been removed,
and removing excitations from an information graph means removing edges
(tension) until nothing further can be removed without losing the fabric
itself. That endpoint — *relaxed as possible, connected as necessary* — is
the vacuum candidate.

This inverts the v0.5 P0, which defined vacuum as perfect all:all
(maximally connected, minimally *distinguished*). Both P0 and P0' claim an
extremality principle; they sit at opposite ends of one tension spectrum:

| | P0, v0.5 (retired) | P0', v0.6 (adopted) |
|---|---|---|
| vacuum wiring | degree `N−1` (all:all) | degree 4 (isostatic 2D) |
| vacuum edges | maximal | minimal-for-rigidity |
| black-hole interior | *near*-vacuum (defect = `k` missing legs) | *maximally far* from vacuum (max tension) |
| curvature | non-uniformity of access | mechanical self-stress |
| why flat is natural | maximal symmetry | marginal rigidity (unique relaxed-rigid point) |

The deciding argument is about black holes. Under P0, black holes — the most
extreme objects in nature — sit *closest* to vacuum (almost-perfect `K_N`,
defect = tiny `k`). Under P0', the BH interior (degree `N−1`) is the
**maximum-tension extreme**, vacuum (degree 4) the relaxed ground state, and
everything else — stars, planets, Casimir cavities — lives on the tension
spectrum between them. "Black hole = maximally stressed fabric" reads
correctly; "black hole = almost-vacuum" read backwards. The L0 theorems
T1–T3 are untouched by the flip: they were always statements about the
tense extreme (`K_N` interiors), and now they are labeled as such.

One subtlety, kept explicit: P0's "minimally distinguished" (no special
node/relation) survives inside P0' as *homogeneity* — the relaxed fabric is
uniform, no distinguished node, direction, or location. What changed is only
the wiring density at which that homogeneity lives: sparse and rigid (4),
not dense and complete (`N−1`).

---

## 3. Why 4 edges: the isostatic point

"Most relaxed yet still a fabric" has a unique quantitative meaning in
network physics: **marginal rigidity (isostaticity)**. The counting is
Maxwell's, and it fits on an index card:

- `N` nodes in `d` dimensions have `Nd` degrees of freedom.
- `M` edges impose `M` constraints (one fixed distance each).
- Rigid ⟺ constraints balance freedom: `M = Nd`.
- Mean coordination `<z> = 2M/N` (each edge touches two nodes).

Hence the isostatic point is `<z> = 2d` — **in 2D: `<z> = 4`**.

| regime | `<z>` | character |
|---|---|---|
| floppy | `< 4` | zero modes; fabric collapses; no stable geometry |
| **marginal (vacuum)** | **`= 4`** | rigid with zero self-stress; unique relaxed-rigid point |
| stressed | `> 4` | self-stress; stored tension; curved reconstruction |

So "each node with 4 edges" is not numerology: 4 is the only coordination at
which a 2D network is rigid without carrying stress. Below it there is no
fabric to reconstruct spacetime from; above it the fabric carries tension,
which the observer reconstructs as curvature (§6). Isostatic networks are a
studied universality class (jamming, marginal solids) with soft modes and
diverging length scales — the postulate plugs the model into known physics
rather than inventing a principle.

A control the model already ran pins down what 4 does *not* do: degree-3
honeycomb, degree-4 square, and degree-6 triangular lattices *all* scale as
2D (`p ≈ 1.6–1.9`, every `r2 > 0.997`). Dimension comes from 2D-ness, not
from the coordination number. The 4 therefore buys **stability without
stress**, not dimensionality. Dimensionality is bought in §4.

---

## 4. Why 2D: vacuum is the area factor

Three-dimensional volume factorizes as radial × area (`r³ = r × r²`). The
model's radial structure (leg screens `k(r)`, shells, tension depth) already
supplies the `r`. What was missing — diagnosed exactly by the shell-graph
failure (`emergent_dim`: radial-only shells give shortest `p ~ 1.4`,
diffusion `p ~ 0.6`, no bracket, pinned) — is the **`r²` factor**: shells
with 2D-like internal information geometry. P0' supplies it as the vacuum
itself:

> **The 2D isostatic fabric is the area factor. Radial scale (tension / RG
> depth) × area = emergent 3D volume.**

This is holographic structure, and it matches the known examples: MERA and
HaPPY turn 2D boundary entanglement + scale into a 3D bulk. The proposal in
one line is **2D vacuum entanglement + scale = 3D space**, with total
emergence meaning: neither the 2D (a coordination principle, not a metric
ansatz) nor the scale (tension depth / RG steps) may contain 3D.

Status, honestly: the *arithmetic* (radial × area = volume) is trivial; the
*mechanism* (which tension rule over a 2D isostatic fabric reconstructs as
the third dimension) is the open D3/D4/D6 route. The grid-shells probe
(shells as imposed-2D patches, scaffolding only) is queued to validate the
arithmetic inside the protocol; growth-rule graphs with no dimensional input
are the real prize.

---

## 5. Only vacuum is perfectly 3D

If dimension is the infrared scaling exponent of accessible information
volume (`d_obs = lim_IR d ln V / d ln r`), and tension perturbs information
geometry, then exact 3D-ness can hold only where tension vanishes:

> **`d_obs ≡ 3` exactly ⟺ zero tension (vacuum). Mass imprints a dimensional
> fingerprint `d_eff(l) ≠ 3` with computable profile.**

The GR side of this fingerprint is already computed (weak-field uniform
star, proper balls of proper radius `l`; flat ball = `4πl³/3`):

```text
   l        V/V_flat   d_eff
   30       0.921      2.990   near-field dip (deficit accumulating)
  100       0.941      3.030   overshoot
 1000       0.987      3.010
10000       0.998      3.0017  → 3 from above, ~1/l
```

Structure: a dip below 3 near the mass, an overshoot above 3 outside,
asymptote `→ 3⁺`. The far-field overshoot is robust, not an artifact: a
localized mass leaves `V(l) = flat − deficit`, so `V/V_flat` rises toward
1 — and a rising ratio *is* `d_eff > 3` by definition. Amplitude is `O(M/l)`:
`~10⁻⁹` at Earth's surface (directly unmeasurable), large near horizons and
in strongly tensed simulator graphs (measurable — this is D10).

So "only vacuum is perfectly 3D" is not mysticism; it is the statement that
3 is the *vacuum limit* of a tension-dependent scaling exponent, with mass
as a dimensional perturbation. Curvature and dimensional deviation are two
readings of one tension pattern.

---

## 6. Mass is tense vacuum (one stuff)

There is one kind of thing — entanglement relations — and one dial —
coordination/tension. Vacuum (`z = 4`), mass, and black holes differ only in
the setting of that dial:

```text
tension →   z = 4        z > 4              z >> 4         z = N−1
            vacuum       planets, stars     neutron-star-    BH interior
            (relaxed,    (mild self-        like compact    (max tension,
            exactly 3D)  stress, d≈3)       objects         T1–T3 regime)
```

"Mass is not looking different" because at the information level there is
nothing else it could be made of: mass *looks like* vacuum plus a tension
pattern (curvature outside, dimensional fingerprint inside the scaling).
This also re-reads Casimir correctly: plates constrain the relaxed fabric
(`M_O` reconstructs less 3D between them); the force measures frustrated
relaxation, and a true void (no `G`) would give exactly zero.

---

## 7. Total emergence: the verdict today

Total emergence means: nothing dimensional in — no 3D lattice, no 2D metric
ansatz smuggled as "scaffolding," no target exponent — and `d_eff → 3` out,
read identically by independent distances. The protocol enforces this with
the **two-distance bracket**: shortest-path balls (adjacency scaling) and
diffusion balls (information-spreading scaling) must agree at 3 on the same
graph. The scoreboard:

| graph | 3D imposed? | shortest | diffusion | bracket? |
|---|---|---|---|---|
| 3D lattices | **yes** (construction) | → 3 from below | → 3 from above | ✓ (ruler validation, circular for emergence) |
| radial shells | no | ~1.4 | ~0.6 | ✗ FAIL (pinned; no 2-sphere factor) |
| `K_N` | no | trivial (1) | uniform | ✗ by design (T1: no interior geometry) |
| tense 2D plug (D10a) | no | dips below fabric, recovers from below (**inverted** vs GR far side) | collapses (heat trap, no power law) | ✗ unweighted; excess-degree costs flip toward GR side (mechanism check, α ad hoc) |
| tense plug + imported costs (D10b) | no | tortuosity-import: partial recovery (1.60→1.86, no flip); c_eff-import: flips (clique 3.43, mild 2.02 vs 1.92) | open (weighted diffusion untested) | overshoot-side only; dip-phase open; cost-saturation past threshold |
| 9×9 mild plug + c_eff (D10a) | no | FULL fingerprint: dip −0.18 → overshoot +0.79 → asymptote +0.09 (all clean) | partial (r² 0.54→0.78, no clean window) | ✓ shape conditional on bridge; amplitude scales (min↓, H↑, A(χ)); κ = interface pattern |
| 2D isostatic + scale | no | open | open | **the prize (D3/D4/D6 + D10)** |

The tense-plug row refines D10 rather than closing it: shortcuts shrink
distances (balls overfull near tension ⇒ `d < d_vac` outside), while GR mass
stretches rulers (balls underfull ⇒ `d > 3` outside) — so bare shortest-path
is *rejected* as `d(i,j)` for tense regions, and the costs must be
congestion-weighted (D10b gates D10a). This matches the model's own light
sector, which never counts hops: T9–T11 use `c_eff → 0` and tortuosity
`dl = (1+√χ/2)dr`, i.e. stretched rulers from congestion. The far-field
companion result is clean: near balls around a far source are bit-identical
to control — relaxed fabric next to tension measures exactly relaxed.

Two zero-fit cost candidates import the ruler from independent sectors.
Tortuosity-import (`w = 1 + c√χ`, `c = 1/2` from T11, BV-bracketed) recovers
the clique plug partway (1.60 → 1.86 vs control 1.92) but does not flip;
the flip needs `c* ≈ 0.58` (diagnostic bracket, not a fit — the import
falls short by ~15–20%, which quantifies the gap rather than closing it).
`c_eff`-import (`w = 1 + χ`, AT light sector with the saturating
`x = χ/(1+χ)` bridge) flips both plugs: clique mid-window 3.43 (clean
power law, big overshoot — amplitude unclaimed) and mild plug
1.73 → 2.02 vs control 1.92 (modest +5% overshoot, the fingerprint
regime). Past threshold the plug routes around and `V(r)` goes insensitive
to cost height (cost-saturation). Static local costs give the
overshoot-side only; the dip-phase (U-shape) mechanism stays open, as does
weighted diffusion (heat-trap remedy untested).

The dip-phase resolved on a wider plug: a 9×9 χ~1 plug under the same
zero-fit `c_eff` rule shows the FULL fingerprint — dip (E = −0.18,
r² = 0.89) → overshoot (peak +0.79, r² = 1.0) → asymptote (+0.09) — the
D10a shape-match conditional on the bridge. (The 5×5 dip lives at r ≤ 3,
below window resolution; the clique dip is a violent transient.) Amplitude
scales with tension in the loose sense: dip-min ratio deepens
(0.20/0.077/0.016), overshoot peak grows (0.79/0.94/2.91), peak sits at
~1 tension-radius, far-field `E ~ A(χ)Rc/r` with non-universal `A`
(deficit ∝ tension). Fixed windows do NOT scale — the fingerprint scale
itself grows with tension, as GR features sit at fixed l/M. The κ half
redirected: κ is an interface pattern (boundary-negative — the T8
attraction signature — core-positive, nonlinear in χ), not monotone
tracking; criterion (b) reformulated to profile-with-confirmation-pending.
The flip lives in `z_vac ~ [2,5]`, containing the independently-fixed P0'
value 4. Conductance-weighted diffusion improves the heat trap (r²
0.54 → 0.78) without cleaning it.

The shell failure is doing its job: it localizes the gap (radial-only ⇒
~1D; area factor missing) instead of allowing a false success. What would
flip the verdict, in increasing strength:

1. **Grid-shells** (scaffolding): imposed-2D shells × radial bridges bracket
   3 — validates radial × area arithmetic inside the protocol.
2. **Entanglement-weighted `V(r)`**: cut entropy / mutual information as
   capacity on existing graphs — tests whether `d_I` differs from bare
   connectivity scaling at all.
3. **Growth-rule graphs**: attachment dynamics with no dimensional input
   whose bracket hits 3 — genuine total emergence; closes D3/D4/D6.

Until then: protocol ✓, ruler ✓, mechanism open, first honest candidate
failed informatively.

---

## 8. Time and causal order (open road)

Everything so far is space: `d(i,j) → V(r) → d_eff → 3`. Time is untouched —
L0 has no dynamics (D1), and "why spacetime?" is strictly bigger than "why
space?". This section records the open road as a notebook, not a claim: the
corrected substrate target (measured), one candidate mechanism (unmeasured),
and the falsifier that would make the program real.

**The corrected target.** An early version of this road asked for causal
growth `V(t) ~ t³` at the graph level. That contradicts P0': on a 2D fabric
with finite-speed local propagation, raw causal balls must grow as `t²` —
`t³` at substrate level would smuggle back a 3D substrate. The honest target
splits by level:

> **`V_G ~ t²` at substrate (L0), `V_O ~ R³` after `M_O` reconstruction.**
> The physics is the map `(fabric neighborhood, scale) → R` that changes
> the effective dimensionality — the same map whose spatial half is D10.

The substrate half is measured **as a control, not a causal result**
(this was briefly filed as D13 stage 1 and demoted on review — the
correction stays on the record): SI first-passage shells fit `p = 1.920`
over `r ∈ [8,20]`, but first-passage here *is* hop distance, so this is
one measurement (static P0' geometry), not two pieces of evidence:

> **Compatibility with a finite-speed cone is not observation of one.**
> Calling BFS depth `t` declares "1 edge = 1 time step" — exactly the
> dynamical structure D1 is supposed to derive.

The plug dissociates hop distance from candidate physical cost (corner
35 < 38, yet ceff-weighted +5.0 — the static sign pattern a future
`U`-experiment must reproduce dynamically as `T_U^plug > T_U^vac).
In one line:

> **Shorter topological path ⇏ shorter physical distance.**
> The plug gives `Δd_hop < 0` (35 < 38) with `ΔT_candidate > 0` (+5.0):
> raw adjacency says "closer", candidate cost says "farther" —
> a minimal demonstration of why P0' needs `M_O` at all.

**Genuine stage 1: `U → T_U, ≺_U`.** A state `X_n` on the graph plus a
local rule `X_{n+1} = U_G(X_n)`; perturb locally, run twin systems, and
define influence counterfactually —
`I(s→v,n) = D(X_n(v), X'_n(v))`, arrival
`T_U(s,v) = min{n : I > ε}`. This is the OTOC-threshold arrival time
generalized (`otoc`, T2, already measures influence spreading under
unitary dynamics) — stage 1 needs `U` on the fabric, not a new readout
concept. `T_U` need not equal `d_hop`: that difference is where the
physics lives. Two well-definedness demands: cone speed must be
ε-robust in the IR (or "arrival" is threshold artifact), and causal
order must come from counterfactuals — `e_i ≺_U e_j` iff changing
`e_i` can change `e_j` under `U` — never from adjacency repackaged as
`d_hop ≤ n`. In short: **D1 provides `U`; D13 asks whether `U` becomes
time.**

**Events, order, cone, clocks (sketch).** The road, compressed: add one
microscopic ingredient — a local update rule `G_n → G_{n+1}` (this is D1,
now gating time itself, not just evaporation). Each elementary change is an
event; influence-dependence gives a partial order `e_i ≺ e_j` (comparable =
timelike-related, incomparable = spacelike-separated). Finite information
speed per update yields a causal cone `r_max ∝ n`, hence an effective
`c_eff` as the vacuum's maximum propagation rate — not a postulate. Clocks
are internal: a repeatable subsystem cycle counts proper time along its
trajectory, and finite update capacity shared with motion/connectivity is
the candidate microscopic source of `dτ < dt` (`congestion.py` is the
repo-native starting point for a capacity model; T9's `c_eff → 0` freezing
already tells a clock-rate story, T11's tortuosity a transfer-cost story —
the road's `g_tt ← clock rate / g_rr ← transfer cost` split independently
re-derives our light/spatial-sector factorization).

Three orderings must not be confused: `n` (microscopic update index),
`≺` (fundamental causal order), `τ` (observer clock time). Just as
`d_G ≠ d_obs`, expect `n ≠ t_obs`: time undergoes reconstruction exactly
as space does.

**Candidate mechanism: scale multiplicity.** Suppose a raw 2D shell
`dV_G ~ r dr` carries an accessible scale multiplicity `n_s(r)`, so the
reconstructed volume is `dV_O ~ n_s(r) dV_G`. Then `n_s(r) ~ r` gives
`dV_O ~ r²dr`, i.e. `V_O ~ R³` — the second `r` factor is *counted
scales*, not a third graph direction. Status: skeleton only. `s` has no
definition yet (candidates: coarse-graining depth, boundary-leg channels —
note circumference itself grows as `r`, which would ground both factors in
2D geometry — bond dimension across cuts), and the baseline to beat is the
RG expectation `n_s ~ log r`, which gives the *wrong* profile (`r log r`).
The mechanism earns its keep if and only if `s` is defined independently
of the desired output and the linear-vs-log profile is then measured.
Recorded as D10's leading 2D+scale candidate; derivation or measurement
promotes it, nothing else does. One refinement: distinguish `n_levels(r)`
(hierarchy depth, expect `~ log r`) from `n_channels(r)` (distinguishable
information channels across scales — min-cut multiplicity, transfer
modes, crossing rank, channel capacity). The mechanism needs the
*channels* linear, and the count must be purely graph-theoretic, never
defined using the target dimension (counting along the `r`-shell by
construction would put the answer in). Honesty note: on any 2D-like
graph, channel counts scale `~ r` for geometric reasons (Menger caps
modes at cut value; cut value is boundary size) — so a measured
`n_channels ∝ r` re-measures 2D-ness. Necessary, not sufficient: the
explanatory burden sits entirely in the second half, *why `M_O` reads
channels as scales*. The non-geometric probe in this cluster is
cost-weighted boundary capacity vs `r` (conductances can break the
geometric scaling — it can surprise). Measured: deficit at `r ≤ 4`
(83.7/133.8/76.5/5.9 on the clique plug — tension suppresses near-field
capacity), exact recovery from `r = 5` (first boundary clearing the
plug's edge-shadow). The count behaves geometrically; the skeleton
stands, explanatory work still in `M_O`.

**Why this could work (grounding).** Malament's theorem: causal order +
volume determine the metric. Our two measurement programs map onto it
exactly — causal relations (this section's road) + `V(r)` (`emergent_dim`)
— so metric reconstruction from graph observables has a real theorem
behind it, not just an analogy. The hard parts are inherited honestly:
order dimension is a measurement problem, not a theorem (a generic partial
order isn't 1+3 — spatial `d_eff` and causal-order dimension must agree
independently); Lorentz symmetry must be demonstrated against
preferred-frame artifacts (T13's quadratic-only LIV is the existing
asset); manifoldlikeness is the causal-set hard problem, related to, not
reinvented.

**The falsifiers.** The same `M_O` must perform *both* the `2+scale → 3`
reconstruction and the microscopic-order → Lorentzian-cone reconstruction.
If space and time end up needing different reconstruction maps, the
program is fitting, not deriving. (This is D12's universality question
made concrete.) The universality target, stated with its quantifier:

> **∀ `M_O ∈ A_macro(G)`, `M_O(G)` ∼ `M`** (up to coordinate /
> coarse-graining equivalence) — where `A_macro` is defined from
> graph-internal admissibility/access criteria alone, and neither "3D"
> nor "Lorentzian" may occur in its definition.

Snapshot emergence is cheap; the over-arching falsifier is dynamical
coherence — graph evolution must map consistently into spacetime
evolution (`M_O ∘ U ≃ U_eff ∘ M_O`), in increasing strength:

> **C1 coherence:** successive reconstructions form a well-defined evolution.
> **C2 locality:** `U_eff` is local in reconstructed spacetime.
> **C3 autonomy:** `U_eff(M_n)` needs no hidden `G_n`.
> **C4 universality:** same frozen `M_O`, `U` across admissible states.
> **C5 GR limit:** `U_eff → GR` in the IR (measured, never demanded).

Each level presupposes the previous; C4 is a quantifier upgrading C1–C3
from "on this trajectory" to "across `A_macro`". Autonomy-before-GR in
bold ink: snapshots resembling a GR solution whose next step needs
microscopic information is *not* emergent spacetime physics. The sharp
operational form is the twin-histories test: find `G_a ≠ G_b` with
`M_O(G_a) = M_O(G_b) = M`, evolve both, and demand
`M_O(U(G_a)) ≃ M_O(U(G_b))` — it tests whether the information `M_O`
discards is actually irrelevant to macroscopic evolution. The measurable
form is ε–δ in macro-profile distance (the RG-weakened version,
`ΔM → 0` in the IR, is probably the right target); it presupposes fiber
control — twins require understanding `M_O`'s preimages, which is D12
work. Note the sequencing: D10a close → freeze `M_O` → compression test;
counting phenomena before the bridges are derived would let construction
inputs masquerade as evidence.

The roof over all of it: define macroscopic states dynamically, not by
hand-chosen coarse-graining. Two graphs are macro-equivalent when they
have the same observable future under `U` over the IR horizon:

> **`G_a ~_macro G_b` ⟺ `M_O(UⁿG_a) ≃ M_O(UⁿG_b)`.**
> An emergent spacetime state is an equivalence class of microscopic
> graphs with indistinguishable macroscopic dynamics.

Given candidate `(U, M_O)`, `~_macro` is derived, and the consistency
demand is that `M_O` factor through the classes — well-definedness on
classes ⟺ autonomy (C3). The architecture becomes `(G,U) → dynamical
equivalence classes → (M,U_eff) → local autonomous 3+1 physics`, rather
than merely `G → 3D geometry`. Currently a target definition (needs `U`
and `M_O` to instantiate); recorded here so the program knows its roof.

---

## 9. Status map (what is what)

| claim | status | home |
|---|---|---|
| vacuum = relaxed isostatic 2D fabric, `<z>=4` | **postulated (P0')** | `model.md` §2, this doc §2–§4 |
| observer sees `M_O(G)`; P4 is one instance | postulated (P0/P4 box) | `model.md` §1–§2 |
| `d_G / d_I / d_obs` + `d_eff` protocol | defined + implemented | `model.md` §1 box, `emergent_dim` |
| bracket on imposed lattices (below + above) | **measured** | `test_emergent_dim.py` (25 tests) |
| convergence `p(L)` monotone, gap `~1/√L` | **measured** | BFS series test |
| resistance / communicability rejected | **measured (negative)** | rejection test |
| shell no-emergence pin (~1.4 / ~0.6) | **measured (negative)** | shell test |
| GR fingerprint (dip, overshoot, →3⁺) | **computed (GR side)** | this doc §5; graph-side: unweighted measured (**inverted** side, shortest rejected for tense regions), tortuosity-import costs partial recovery (no flip), c_eff-import costs flip overshoot-side (dip-phase open, D10b) |
| tension costs (D10b candidates) | **measured** | `tension_cost_fn` (partial recovery, c* diagnostic), `ceff_cost_fn` (clique + mild flips); fabric-identity + 3D-ruler controls |
| D10a fingerprint shape | **measured (conditional)** | 9×9 mild plug: dip → overshoot → asymptote under zero-fit ceff costs; conditional on the χ/x bridges (derivation open) |
| amplitude scaling | **measured (loose)** | min-ratio ↓, peak ↑, far-field `A(χ)` grow with χ; fixed windows don't scale (scale grows with tension, GR-like) |
| κ-profile (D10b) | **measured (first)** | interface pattern (boundary −0.93/−0.31, core +0.89/~0); monotone-tracking FAILED, criterion reformulated, confirmation pending |
| tension-imprint conjecture | **conjectured** | `model.md` §5: fingerprint universality under the fixed ceff rule; falsifiers + promotion to P5 stated; not a postulate yet |
| T15 cost dominance | **derived (theorem)** | `model.md` §2: shortcuts priced ≥ hop-saving can't inflate balls; ∩-blip pins an underpriced shortcut (z=1 U-side 0.2000, tort blip 9>5 + flip 2.020, ceff-z=4 blip 1.077 at r=13.75) |
| far-field tail exponent | **open** | D11: `1/r` (χ~2 to `5Rc`) vs `1/r²` (χ~1 to `6Rc`); `L ≥ 200` asymptotics needed |
| SI static shells `V(r)~r²` | **measured (control)** | `test_scrambling.py` (5 tests): p = 1.920; plug sign pattern (35<38 hops, +5.0 weighted) pre-registered for D13.1 |
| scale-multiplicity mechanism `n_s~r` | **conjectured (skeleton)** | this doc §8: `s` undefined; RG-log baseline gives wrong profile; linear-vs-log must be measured, not assumed |
| boundary channel capacity | **measured** | clique plug: deficit `r≤4` (83.7/133.8/76.5/5.9), exact recovery `r≥5`; count re-measures 2D-ness (skeleton intact) |
| reconstruction universality | **open** | D12: ∀ `M_O ∈ A_macro(G)` converge in the IR (access floor graph-internal; no "3D"/"Lorentzian" in the definition) |
| causal order / cone / clocks | **open** | D13: D13.0 control measured; stages 1–4 open (`U→T_U`, same-`M_O` cone, clocks, interval) |
| same-`M_O` + dynamics coherence | **open (criterion)** | this doc §8: one map yields `R³` + cone (C1–C5 ladder, twin-histories test, `~_macro` classes), or the program is fitting |
| `d_I = 2` for vacuum fabric | predicted (follows from P0' + protocol) | queued for simulator (D10) |
| 2D + scale → 3D mechanism | **open** | D3/D4/D6 (+ D10); leading candidate: scale multiplicity `n_s~r` (this doc §8, skeleton) |
| tension → `κ` map (`z−4` to curvature) | **open** | D10 |
| Born rule / double-slit dynamics | open (needs D1) | non-claim |
| Casimir `1/d⁴` from frustrated relaxation | open (ontology only) | non-claim |

Refutation wires (what would kill P0'): a relaxed (`z≈4`) fabric whose
`M_O` reconstruction is robustly non-flat at large scales with no
tension source; a tensed region whose `d_eff` profile contradicts the GR
fingerprint shape after the simulator mapping is fixed; or a derivation
showing isostaticity is unstable under the (future) graph dynamics D1.

*Index-card version: relax the information, not the spacetime — the
variational principle lives on `G`. Vacuum is the most relaxed state that
is still a fabric: isostatic 2D, four edges per node, rigid with zero
self-stress. 3D is radial scale × vacuum area, exact only at zero tension;
mass is tense vacuum wearing a dimensional fingerprint. Total emergence is
a bracket that first failed informatively and now knows what it needs.*
