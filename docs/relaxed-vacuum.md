# The relaxed vacuum: why 3D must emerge from rested information

*Companion to `docs/model.md` v0.6–v0.6.1 (P0' postulate) and the `emergent_dim`
protocol. This document explains the reasoning; `model.md` states the
definitions. Nothing here is claimed as derived unless it names its test.*

Reading guide: §1–§2 are philosophy (why relaxation belongs to the
information side). §3–§4 are the postulate (2D, 4 edges, and what each word
costs). §5–§6 are consequences (only vacuum reconstructs as perfectly 3D;
mass is tense
vacuum). §7 is the verdict on total emergence today (bracket method, first
failure, what would flip it). §8 maps every claim to definition / measured /
open. Readers who only want the postulate can read §3–§4 and §8.

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
- Rigid ⟺ constraints balance freedom: `M = Nd − d(d+1)/2` (`2N−3` in 2D
  free; bulk `<z> → 4`).
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
stress**, not dimensionality. Dimensionality is bought in §4. The postulate
means *generic* isostatic: the square grid is the non-generic control with
the right coordination that still shears (distinguished axis); see the P0'
box in `model.md` (v0.6.1).

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

## 5. Only vacuum reconstructs as perfectly 3D (flat IR readout)

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

So "only vacuum reconstructs as perfectly 3D" is not mysticism; it is the statement that
3 is the *vacuum limit* of a tension-dependent scaling exponent, with mass
as a dimensional perturbation. Curvature and dimensional deviation are two
readings of one tension pattern. (v0.6 alias: "only vacuum is perfectly 3D" —
retitled v0.6.1 so `d_I = 2` on the fabric and `d_obs = 3` in reconstruction
do not collide; "relaxed" names `G`, "flat" names the IR readout.)

---

## 6. Mass is tense vacuum (one stuff)

There is one kind of thing — entanglement relations — and one dial —
coordination/tension. Vacuum (`z = 4`), mass, and black holes differ only in
the setting of that dial:

```text
tension →   z = 4        z > 4              z >> 4         z = N−1
            vacuum       planets, stars     neutron-star-    BH interior
            (relaxed,    (mild self-        like compact    (max tension,
            flat readout stress, d≈3)       objects         T1–T3 regime)
            d_obs=3)
```

Tension is read on two ledgers (spec box v0.6.1): combinatorial
over-coordination (`z − 4`) and metric contraction (`w < d_0`); D10/T15
address the second. The map from either or both to curvature through `M_O`
stays open (D10).

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

## 8. Status map (what is what)

| claim | status | home |
|---|---|---|
| vacuum = relaxed isostatic 2D fabric, `<z>=4` | **postulated (P0')** | `model.md` §2, this doc §2–§4 |
| observer sees `M_O(G)`; P4 is one instance | postulated (P0/P4 box) | `model.md` §1–§2 |
| `d_G / d_I / d_obs` + `d_eff` protocol | defined + implemented | `model.md` §1 box, `emergent_dim` |
| bracket on imposed lattices (below + above) | **measured** | `test_emergent_dim.py` (24 tests) |
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
| `d_I = 2` for vacuum fabric | predicted (follows from P0' + protocol) | queued for simulator (D10) |
| 2D + scale → 3D mechanism | **open** | D3/D4/D6 (+ D10) |
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
