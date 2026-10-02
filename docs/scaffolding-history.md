# Scaffolding history

How the model in `docs/model.md` was locked, written as the decision tree.
A node is a choice that is now part of the scaffold. The children are the
independent aspects that had to agree before that choice was locked. One
aspect is a lead. The lock is the merge.

This note keeps the confirming merges. Routes that were tried and dropped
are not listed. Definitions, numbers, and close criteria stay in
`docs/model.md`, `docs/relaxed-vacuum.md`, `docs/j2-status.md`, and
`docs/DEFERRED.md`. The changelog is the version clock; pull requests are
the lock points.

**Marks**

| Mark | Meaning |
|---|---|
| lock | on `main`; the choice is in the model |
| **forced / debt** | adopted so later work has a concrete object; the derivation that would select it is still missing |
| **†** | stated in an open pull request, not on `main` |

---

## How to read a merge

```text
choice
├── aspect A     (independent evidence or principle)
├── aspect B
└── aspect C
    └── lock     only when A, B, and C agree
```

If a required aspect is still open, the node stays a conjecture, a
calibration, or a debt. It does not get promoted by rewording.

The three layers of `docs/model.md` are the trunk. L0 is graph kinematics.
L1 is the spacetime interface, conditional on named imports. L2 is
compact-object calibration and does not feed back into L0 or L1.

---

## 1. Postulates

Primitives come first and stay undefined: a node, an edge, the information
graph `G`, and the exterior leg count `k`. Mass, radius, temperature,
metric, area, and coordinates enter later, each as a labeled interface map.

### P1 — black-hole interiors are almost-perfect all:all graphs

```text
P1  K_N interior, k ≪ N²
├── T1   diameter exactly 1 at every N
│        (chain ~ N/2, grid ~ 2√N, expander ~ log N)
└── T2   finite-speed circuits scramble in t* ~ log N
         └── lock    P1 is the wiring form of "fastest scrambler"
```

Formalized with the rest of L0 in model-docs v0.1 (PR #30). "Almost" is
the observable content: area, temperature, and radiation live in the
failure to be perfect.

### P2 — an edge is a unit of entanglement

Cut size bounds entropy across the cut. No specific quantum state is
postulated. Particular states appear only as witnesses.

### P3 — monogamy

```text
P3
├── linear toy          e_int + e_ext ≤ 1     (bookkeeping)
└── CKW frontier        verified on a 25-point grid
                        (exact frontier strictly below the linear bound;
                         exterior one-tangle peaks at 1/2)
    └── lock            black holes sit at e_int ≲ 1 with small k
                        e_int → 1 is the baby-universe limit (T3)
```

### P4 — neighborhood measure is uniform, idleness zero

```text
P4   m_x uniform on neighbors, self-mass 0
├── continuum    Ollivier curvature recovers Ricci for this measure
└── L2 fit       an e_int-weighted alternative lowers p
                 0.94 → 0.84 at e_int = 0.9, and to 0.78 at 0.99
    └── lock     the choice is postulated (v0.3, PR #36);
                 the curvature numbers are measured
```

P4 is one instance of the observer map `M_O` (below). Promoting it to a
derivation means exhibiting the map that gives `d_eff → 3` and negative
radial curvature without tuning.

### The leg–area matching (I1)

```text
patch A = 4 ln2 · k · l_p²
├── I1a   a saturated exterior leg carries η_vN = ln2 nats
│         (definition of saturation; BN toy: S/k constant to < 0.8%,
│          mean ln2)
└── I1b   S = A/4 imported
    └── lock    4 ln2 is arithmetic (v0.4, PR #40)
```

The locked leg is a saturated `ln2` bit. The factor `1/4` is the area
coefficient that comes out of I1b. The s-leg falsifier tests I1a directly.

### Vacuum — P0′

The vacuum postulate is the merge that turns the wiring postulates into
a fabric. It landed as model-docs v0.6 (PR #53, released in #54), with
the full argument in `docs/relaxed-vacuum.md`.

```text
P0′   vacuum = relaxed isostatic 2D fabric, <z> = 4
├── A  relaxation sits on G
│      spacetime is the reconstruction M_O(G), never G itself
│      (Jacobson entanglement equilibrium is the precedent)
├── B  the black-hole reading
│      K_N (degree N−1) is the maximum-tension end of one spectrum
│      stars and planets sit between vacuum and that end
│      T1–T3 stay, as statements about the tense extreme
│      homogeneity stays; the wiring density of the homogeneous state
│      is the sparse rigid point
├── C  why 2D — the area factor
│      volume factorizes as radial × area
│      leg screens already supply the radial piece
│      radial-only shells do not bracket 3
│      (shortest-path p ~ 1.4, diffusion p ~ 0.6)
│      so the missing factor is an r² of 2D information geometry
├── D  why 4 — Maxwell, given 2D
│      N nodes in d dimensions, M = N d constraints
│      <z> = 2M/N = 2d
│      in 2D the unique rigid, zero-self-stress point is <z> = 4
│      floppy below, stressed above
└── E  coordination and dimension come apart
       degree-3 honeycomb, degree-4 square, and degree-6 triangular
       lattices all scale as 2D (p ≈ 1.6–1.9, every r² > 0.997)
       └── lock    2D is the area factor; 4 is marginal rigidity
```

Curvature, in this language, is self-stress: over-coordination `z − 4`
read through `M_O`. The quantitative map is open (D10).

**† PR #58** (docs v0.6.1, open) writes the same lock in sharper words:
2D is the choice, 4 is what Maxwell then forces; the bulk count is the
free-body form `M = 2N − 3` with `<z> → 4`; the vacuum is generic
isostatic and the square grid is the shear control; combinatorial tension
`(z − 4)` and metric tension `w < d_0` are two ledgers; `<z> = 4` is
unrelated to `S = A/4`, to `4 ln2`, and to spacetime being 3+1. No new
postulate. Not merged.

**† PR #47** (open) proposes a further L0 postulate, P5, that the ambient
graph is connected, bridgeless, and large-world, plus graph theorems
A1–A5. That postulate is not in `docs/model.md`. It is not part of the
lock above.

---

## 2. The fabric is a class

P0′ names a connectivity class. The next lock is what object that class
is. Static geometry was allowed to vote; it voted for a class.

```text
vacuum object = [G]_{∼_O}     (an equivalence class, possibly an ensemble)
├── A  one frozen measurement, many constructions, one reading
│      triangular, hexagonal, square, noisy grid,
│      Poisson–Delaunay, Lloyd-relaxed Delaunay, Gabriel, k-NN,
│      and the 4-regular Delaunay medial quadrangulation
│      all give d_G → 2
│      the medial quad shows that 4-regular vs triangular does not
│      select the dimension
├── B  a second leg, spectral dimension
│      heat-trace d_s on the 60×60 torus holds (1.95, 2.05)
│      over a full decade
│      Weyl fits put every Tier-1 member in (1.90, 2.15)
├── C  the boundary of the class, measured with the same rule
│      gated walls keep ~r² balls and collapse the cuts,
│      so the vacuum also requires the channel scaling
│      long-span rewires take the graph out of d_G → 2
│      span-limited rewires (≤ 2 grid steps) keep it
│      a few O(1) shortcuts are enough (N*_med = 20, 10, 10
│      on L = 40, 60, 80)
│      2×2 blocking drives rewired long-edge density 0.013 → 0.31
└── D  what may be put into the vacuum
       observation does not ask for crystalline long-range order
       Poisson–Delaunay is frozen as a reference member,
       the way a gauge is frozen, for reproducibility
       └── lock    v5.2, PR #59 and PR #60
                   Tier-2 extra tessellations add no axis
```

Substrate ball growth confirms the same 2D count from the other side.
Unclipped Manhattan balls are exactly `V(r) = 1 + 2r(r+1)`, and the
disk-boundary cut is exactly `8r + 4`. That is the substrate prediction
of P0′. The 3D reading is reserved for after `M_O`.

**† PR #52** (open) runs the same volume-growth ruler on three Cayley
graphs. Klein, `Z^3`, and the Heisenberg group read 2, 3, and 4, all
three inside the pre-registered tolerance. The ruler can tell those
dimensions apart. The Heisenberg group, Hirsch length 3 and metrically
4-dimensional, is outside a 3D homogeneous vacuum. The probe does not
select a substrate. D10 stays open.

---

## 3. Distance and the observer

Physical distance is information-access through `M_O`. On the tense
extreme, T1 says every pair is one hop, which is why the distance has to
be reconstructed rather than read off adjacency.

```text
M_O(G) = [G]_{∼_O}
├── graph-internal, permutation-covariant, coarse-graining stable,
│   operational, and a frozen rule
│   (P4 passes (1)(2)(3)(5); (4) is partial — D12)
├── V_O ~ R³ is the output test, never an input
└── three dimensions stay distinct
    d_G microscopic, d_I information, d_obs observed
    d_obs → 3 is the infrared conjecture, not an input
```

Tension needs a cost, not a hop count. The merge that fixed the ruler:

```text
tense-region distance
├── T15   a shortcut priced at or above its hop-saving
│         cannot inflate balls (L0 theorem, v5.1, PR #56)
│         a volume blip locates an underpriced shortcut
├── shape the zero-fit c_eff rule on a 9×9 mild plug
│         reproduces the GR fingerprint
│         dip −0.18 → overshoot +0.79 → asymptote +0.09
├── window the flip sits in z_vac ~ [2, 5],
│         which contains the P0′ value 4
└── κ     boundary-negative, core-positive
          confirmed on a corner-free disk
          (internal +0.90, boundary −0.86, fabric 0)
    └── conditional lock
            the shape is a graph result
            the two bridges (χ-analogy, x-map) are still assumed
            so this is the tension-imprint conjecture, not a postulate
            promotion to a P5 cost rule needs a second geometry
            and one bridge derived or removed
```

The far-field tail (`1/r` versus `1/r²`) is a separate open item (D11).
It is not required for the shape lock above.

**† PR #85 and #90** (open, stacked) carry the observer one step further
on the working sheet. At linear size 128 the operational rulers of J₂ and
the square-torus control agree (verdict OBS0R-METRIC; the earlier wave
gap closes as a finite-size effect). A blind observer, given operational
measurements and no graph, coordinates, or dimension target, reconstructs
a stable 2D metric that matches the coarse J₂ quotient (`d_O = 2.02`
unprompted). That confirms the quotient form of `M_O` on this sheet. It
does not derive which sheet the vacuum is.

---

## 4. Interface locks that sit on the trunk

Each of these is "given L0 plus the named imports." None of them redefines
the fabric.

```text
Newton (T8)
├── I4a   equipartition on the leg screen, T(r) = M₁ / 2π r²
└── I4b   Bekenstein displacement, dS = 2π M₂ dr
    └── lock    F = M₁ M₂ / r² by exact multiplication
                log-log slope to 1e−9; orbits close; T² ∝ r³
```

```text
sign of attraction (T8)
├── I6b   Ollivier–Ricci → Ricci, continuum limit
└── P4    the uniform measure
    └── lock    radial κ negative in every tested configuration,
                attachment, and seed
```

The heat-kernel bridge (I6a) is cited and carries no load. The
Raychaudhuri step (I6c) is the open bridge D9. Einstein's equations are
conditional on it; T8–T11 do not use it.

```text
mass map (I3)
├── I1 matching
└── sphere geometry A = 4π R²
    └── shrink    k(M) ⟺ R_s(M)          (BM reduction, v3.5)
                  the remaining statement is R_s = 2M
                  that derivation is open (D6)
```

```text
spatial sector, γ = 1 (T11)
├── the coefficient 1/2, fitted to enforce γ = 1
│   (unique coefficient; the fit is kept in the history)
└── BV   c ≈ 0.44–0.60 from ln2 line-defect scattering,
         zero extra tuning (PR #4; target 0.456)
    └── lock    the micro-derivation is adopted
                p = 2c and γ = 2c are the comparison targets
```

```text
2PN cancellation (L2, not promoted)
├── measured radial exponent
│   p = 0.913 ± 0.049 at N = 1020 (80 graphs)
│   and 0.91–0.94 through N = 16 000
│   the cancellation point is p = 0.92
└── κ → c₂ map
    c₂(p) = p(2p−1) is an ansatz (F4)
    a power-law reading and a 1/r² reading disagree when crossed
    └── incomplete    the exponent meets the target
                      the map is not derived (D3)
                      F4 stays a calibration
```

Light to first order (full `4M/b`, Shapiro, achromatic lensing) and the
quadratic-only ultraviolet dispersion sit on the same interface. They
confirm the congestion and lattice-symmetry consequences. They do not
add a postulate.

---

## 5. J₂ — forced working substrate (debt)

The class lock in §2 withholds a unique graph on purpose. Formation,
waves, and the isotropy program still need one concrete member to build
on. J₂ is that member. The claim is a working member, and the derivation
that would select it stays debt.

J₂ is the degree-8 walk graph `Z² ⋊ Z₂` of D'Ariano–Erba–Perinotti
(2019): two sheets over the square lattice, quotient a 4-regular square
grid. It was admitted as a probe because that built-in coarse-graining
is a new axis, then kept because the probes that were required of a
working member came back inside the family.

```text
canonical working vacuum substrate          v5.4, PR #62
├── A  the class does not name a graph
│      §2 degeneracy is the result, not a missing discriminator
├── B  a concrete sheet is required
│      formation and wave campaigns build on one substrate
└── C  J₂ survived the probes that were asked of it
       ├── exact square quotient
       │   1861 cells, 1741 strict-interior cells of square degree 4,
       │   micro-multiplicity 4, quotient shells exactly 4r
       ├── long scale agrees with the quotient
       │   Δp = 0 (bound was 0.15); both are bipartite
       ├── ultraviolet structure is real and extra
       │   micro shells 8r, cuts 32r+16,
       │   C₄ census ~20× the square equivalent
       ├── perturbations are family-typical
       │   deletion leaves the long-scale exponent;
       │   swaps track the family, no protected tier
       ├── D5∞ formation transfers
       │   cores form on the triangle-free J₂ torus
       └── orientation is absent
           32 runs, (c)-ISOTROPIC:
           radial selection preserved, no persistent h₁/h₂ axis,
           sheet symmetry preserved
    └── missing child
            a dynamics that outputs J₂ from an arbitrary primordial graph
            └── FORCED
                evidence-based working choice
                uniqueness not claimed
                DEBT: non-derivation
                (docs/j2-status.md)
```

The debt is narrow and explicit. J₂ may be replaced by a later substrate
that out-survives it. Phenomenology already banked on it is what the
replacement has to keep. Until that happens, formation and wave work
use J₂.

The achiral Stage-0 result on this sheet (0/6 directed, 0/6 persistently
handed) closed the debt-free pure-D5∞ polarity route. Individuals on the
sheet are trackable. That dynamics does not hand the vacuum a direction.
The program therefore continues on the forced sheet, with the derivation
still owed. Record: PR #62, `docs/j2-status.md`.

### † Confirmations on the forced sheet

These are open pull requests. Each one agrees with keeping J₂ as the
working member. None of them supplies the missing derivation, so none of
them discharges the debt.

| † | PR | What agreed |
|---|---|---|
| phase coherence | #70 | bare J₂ carries coherent two-path phase, `C = 1`, with `τ` scaling as `1/ΔE`. Establishes coherent transport on the sheet. |
| interference | #69 | two-path calibration, phase, which-path, and graph corridors pass, including a J₂ secondary. Born-rule detection is deferred. |
| one field, two jobs | #76, #78 | the same `H = −A` field on J₂ supports an undirected potential-like response and a coherent directed wave (POT0-COLLECTIVE), then a static/dynamic unification (POT1-FIELD). |
| excitation ledger | #63 | the J₂ excitation constraint map is closed (null, Weyl control, compass, the no-go steps, and the time horn). SSB design stays deferred. |
| law versus sheet | #93 | partial, campaign still running. Identities A1–A6 of `H = −A` hold on hostile graphs, so those identities are law. Interference passes on J₂, the open square, and the square quotient, and fails on the triangular and hexagonal lattices. That is a square-class split, not a proof that the sheet must be J₂. |

---

## 6. The trunk in one picture

```text
primitives (node, edge, G, k)
└── L0 postulates
    ├── P1  all:all interior ──────── T1 ∧ T2
    ├── P2  cut bound
    ├── P3  monogamy ──────────────── linear toy ∧ CKW frontier
    ├── P4  uniform measure ───────── continuum ∧ fit
    └── P0′ vacuum fabric
        ├── relaxation on G
        ├── K_N = maximum tension
        ├── 2D = area factor ──────── shells miss r²
        ├── <z> = 4 ───────────────── Maxwell, given 2D
        └── 4 ≠ dimension ─────────── z = 3, 4, 6 all read 2D
            └── vacuum = class [G]_{∼_O}
                ├── family d_G → 2
                ├── spectral band
                └── span bounds the class
                    └── J₂ working member
                        ├── quotient, Δp = 0, UV extra
                        ├── perturbation family-typical
                        ├── formation transfers, no orientation
                        └── FORCED — derivation is debt
                            └── † coherence, interference, field,
                                excitation ledger, VAC-0 (partial)

L1, conditional on imports
├── I1a ∧ I1b ──────────── patch 4 ln2
├── I4a ∧ I4b ──────────── Newton
├── I6b ∧ P4 ───────────── attraction sign
├── fit 1/2 ∧ BV bracket ─ γ = 1
└── I1 ∧ sphere ────────── k ⟺ R_s ; R_s = 2M still open

still open on the trunk
├── cost bridges ───────── shape confirmed, not yet a postulate
├── 2D + scale → 3D ────── D3, D4, D6, D10
├── update rule U ──────── D1
├── same M_O for space and time, universally ── D12, D13
└── a dynamics that selects the substrate ── the J₂ debt
```

L2 (one `k ∝ M²` family, the measured exponent `p`, leg-shedding) sits
beside this trunk. It is the most testable layer and the least derived.
Killing it leaves L0 and L1 in place.

---

## 7. Where the scaffold stops

The forward pipeline, copied from the top of `docs/DEFERRED.md`, is the
same tree read onward:

vacuum class → admissible `M_O` → 2D plus scale reconstructs as 3 →
an explicit update rule `U` → influence and causal order → the same
frozen `M_O` reads the causal geometry → `M_O` and `U` commute into an
autonomous macroscopic dynamics.

P0′ has identified the connectivity class. D10 asks why observers
reconstruct 3D from it. D1 asks what dynamics preserves the class. D13
asks whether that dynamics is time. D12 asks whether every admissible
observer agrees. The J₂ debt asks which member of the class the dynamics
actually selects. Each of those closes only by its own criterion.
