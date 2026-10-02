# Model scaffolding history

How the current model was constrained. A choice appears when the independent
results that support it are named. Dropped routes are omitted unless a
present debt is otherwise unreadable.

The kinematic model in `docs/model.md` (all:all interiors, leg area, conditional
weak-field gravity) stays the merged L0/L1 record. This note is the scaffold
of the relational field program built on top of that graph: two real scalars,
`H = -A`, a working fabric, and the question of how geometry is allowed to
change. A later null does not erase an earlier lock.

**Names.** P0–P2 below are the field-program postulates. They are not
`docs/model.md`'s P0′–P4.

**Marks**

| Mark | Meaning |
|---|---|
| ✓ | established on `main` |
| ◇ | established in an open or stacked pull request |
| ⚠ | adopted, not uniquely derived; ontology debt |
| → | dependency |
| + | independent results combined |

**Status words:** POSTULATE, DERIVED, EMPIRICALLY ESTABLISHED, WORKING CHOICE, OPEN / DEBT.

A campaign that has a pull request but no verdict yet is marked open, not ◇.
◇ means the result is already in that pull request.

---

# 1. Primitive postulates

## P0 — Relational ontology

```text
G = (V, E)
```

Nodes do not begin with positions in an ambient space. An edge is a relation.
Distance, area, and metric are later reconstructions.

Status: **POSTULATE** ✓ (`docs/model.md` primitives; no coordinates at L0).

```text
relational fabric
    → geometry has to be earned from graph structure and observables
```

## P1 — Two real scalars per node

Each node carries `(r_u, s_u)`, written `ψ_u = r_u + i s_u`. No vector, momentum
register, or coordinate is stored at the node.

Status: **POSTULATE** of the field program ✓. It is the frozen node field of
every later campaign (P1 ballistic #65, EM-0 #81, VAC-0A #93), all on `main`.

## P2 — Field evolution on a fixed graph

```text
i ∂_t ψ = H ψ,    H = -A
```

with `A` the adjacency (`J = 1` in the frozen convention; P1.2 writes the same
law as `H = -J A`, hopping only).

Status: **POSTULATE / WORKING LAW** ✓. P1.2 (#65) locks this as the one-way
map from a fixed graph to `ψ`. It is not derived from a deeper dynamical
principle. Once it is granted, the consequences in §4–§5 follow, and VAC-0A
shows they hold on every simple graph.

```text
H = -A
  ├── norm conservation          DERIVED ✓
  ├── exact continuity current   DERIVED ✓
  ├── interference               EMPIRICALLY ESTABLISHED ✓
  ├── coherent propagation       EMPIRICALLY ESTABLISHED ✓
  └── static driven response     EMPIRICALLY ESTABLISHED ✓
```

---

# 2. Selecting the fabric

## 2.1 What the substrate had to be

These constraints accumulated. They select a class, then a working member.
Rejected graphs are not listed.

| Constraint | Status | Where it was locked |
|---|---|---|
| Locality: the vacuum is a protected low-dimensional connectivity class, not a complete graph | ✓ | P0′ and the substrate family (`docs/model.md`, `docs/relaxed-vacuum.md`; v5.2, PR #59–#60) |
| Connectedness with channel access: ball growth `~ r²` is not enough; cuts have to scale too | ✓ | gated-wall control, same family |
| Effective dimension 2 at substrate level; 3 is an observer reading, not an input | ✓ | P0′, `d_G / d_I / d_obs` |
| Marginal rigidity `<z> = 4` once the fabric is 2D | ✓ | Maxwell count inside P0′ |
| The object is a class `[G]`, not one crystal | ✓ | Tier-1 degeneracy; Delaunay is a reference gauge |
| Formation can nucleate on the member, without selecting a compass | ✓ ⚠ | D5∞ on the J₂ torus, orientation absent (PR #62) |
| Coherent `H = -A` transport | ✓ | P1.1 ballistic pass (#65); bare-J₂ coherence `C = 1` (#70); two-path interference (#69) |
| Observer-accessible geometry | ✓ | §3 |

## 2.2 J₂ as the working fabric ⚠

Status: **WORKING CHOICE**, forced. ✓ on `main` as the canonical working
vacuum substrate (v5.4, PR #62, `docs/j2-status.md`). ⚠ because it was not
uniquely derived.

```text
class [G] does not name one graph
    +
later work needs one concrete sheet
    +
J₂ survives the probes that were required
        ├── exact square quotient, quotient shells 4r, micro/coarse Δp = 0
        ├── ultraviolet structure kept (shells 8r, cuts 32r+16, ~20× C₄)
        ├── perturbations family-typical
        ├── formation transfers onto the triangle-free torus
        └── no persistent h₁/h₂ orientation (32 runs, isotropic)
    → J₂ = current substrate
```

```text
J₂ = current substrate
```

is not a proof that J₂ is the only substrate. The missing derivation is the
debt: **substrate uniqueness**.

Confirmations that the forced sheet can carry the field program, all ✓, none
of which pay the debt: coherence #70, interference #69, POT-0/POT-1 #76/#78,
OBS-1 #90.

Follow-up, partly open: **VAC-0** (#93). Completed pieces already split the physics:

```text
VAC-0A  A1–A6 identities hold on hostile graphs     → LAW        ✓
VAC-0F  interference passes on J₂, open square,
        and the square quotient; fails on tri/hex   → square CLASS,
                                                      not yet J₂-only  ✓
VAC-0H/I  substrate-wide verdicts                   → apparatus banked,
                                                      verdicts OPEN
```

Filed (VAC-0F): two-path PASS on the open grid, square torus, J₂, and the J₂
quotient; FAIL on triangular and hex; rewires fail the phase rung; the MZ
corridor passes at LAW level after a window erratum. The finished question is
which banked phenomena are LAW, which need a class, which need J₂, and which
are accidental. Until H/I close, uniqueness stays debt.

---

# 3. Geometry from the fabric

Independent rulers on J₂, compared with a square-torus control. All of this
is ✓.

```text
J₂ microscopic structure
    ├── graph balls / Hausdorff     dH matches the square control
    │                               (exact at the scales tested; gap 0 at L = 128)
    ├── diffusion / spectral        ds agrees to 4 decimals;
    │                               gap 0.0005 at L = 128
    ├── coherent-wave ruler         disagrees at L ≤ 42 (OBS-0 #82);
    │                               the gap is a finite-size residue
    │                               (OBS-0R #85: gap 0.134 at L = 128)
    └── static-field ruler          all-path POT ruler joins the same geometry
            +
            → OBS0R-METRIC ✓
              six pairwise ruler gaps pass against the square control
```

The wave disagreement at small L is kept only because the later agreement is
otherwise easy to over-read. What remains at L = 128 is a substrate systematic
(purification removes much more of J₂ than of the square), and the campaign
itself records that the match is not a far-infrared universal reconvergence.

```text
operational metric (OBS0R-METRIC)
    +
blind observer (no graph, coordinates, or dimension target)
    → OBS1-QUOTIENT ✓   (#90)
```

Measured: `d_O = 2.02` unprompted, `d* = 2` on train and test, distance match
8% against the quotient (twice as close as the microscopic graph), local charts
6%, locality above 95%, sheet contrast below 0.03. Expanders come out
non-2-dimensional (`d* = 3`).

```text
M_O(J₂) ≈ J₂ / sheet
```

The microscopic graph and the reconstructed geometry are different objects.
The quotient is an operational 2D metric ✓. Calling that metric spacetime is
not established. A static-channel floor still blocks a full three-way
cross-probe at L = 128; that limit stays on the record. Why the observer
inhabits that quotient is §14.

---

# 4. Field anatomy

Granted only `ψ = r + i s` and `H = -A`. The identities are **DERIVED** for
every simple undirected graph (VAC-0A ✓, #93; first pinned on the J₂ stack
inside EM-0 #81). Nothing about J₂ enters A1–A5.

## 4.1 Conserved density

```text
ρ_u = |ψ_u|²
Q_ψ = Σ_u |ψ_u|²
dQ_ψ / dt = 0
```

`H = -A` is real symmetric, so the evolution is unitary. Status: **DERIVED** ✓.

## 4.2 Bond quantity B and current J

The bond correlator `ψ*_u ψ_v` splits into a symmetric part and an
antisymmetric part:

```text
B_uv     = Re(ψ*_u ψ_v)
J_{u→v}  = 2 Im(ψ*_u ψ_v)
```

`J` is the continuity current:

```text
dρ_u / dt + Σ_v A_uv J_{u→v} = 0
```

`B` is the bond energy. With `E_ψ = ⟨ψ|H|ψ⟩`,

```text
E_ψ = -2 Σ_{(uv) ∈ E} B_uv
∂E_ψ / ∂A_uv = -2 B_uv
```

Status: **DERIVED** ✓. This conjugacy is the central scaffolding identity
between the field and the edges.

Quadrature, algebraic: `B ~ cos Δθ` and `J/2 ~ sin Δθ`. Some backreaction
readouts store the bare imaginary part, exactly half of this continuity
current. The factor is a convention, not a second current.

---

# 5. Propagation, and a response that looks like a potential

## 5.1 Direction is collective phase

```text
coherent extended ψ
    → interference
    → directed propagation
```

P1.1 (#65) validates the ballistic detector: packets on a ring and on bare J₂
propagate, reverse under `k → -k`, and keep their norm. POT-0 (#76) then
separates direction from any node-level arrow. Verdict **POT0-COLLECTIVE** ✓:

```text
symmetric source     → spreads, no direction
coherent packet      → ballistic direction
phase scrambling     → direction disappears
coherence restored   → direction returns
```

Direction is collective phase information. It is not a primitive variable on
the node. Status: **EMPIRICALLY ESTABLISHED** ✓.

## 5.2 One field has a static regime and a propagating regime

```text
POT-1  (#78)  POT1-FIELD ✓
    +
EM-0   (#81)  EM0-BACKREACTIVE ✓
    → the same ψ
         ├── stationary source-relative response
         └── a front when the source changes
```

No second field is required for those two regimes. EM-0 adds the continuum
reading that later interpretation tests use: J₂ Bloch bands, a long-wave
Schrödinger sector, continuity to numerical zero, and the same `B`/`J`
quadrature. It does not claim Maxwell, charge, or photons.

EM-1 (§6) rejects the electromagnetic reading. The field results above stay.

---

# 6. Electromagnetic identification rejected

```text
POT-0 + POT-1 + EM-0
    → one complex scalar with static and propagating regimes
    → EM-1 (#87)
    → EM1-FALSIFIED ✓
```

Structural failures, from the frozen tests:

| Test | Result |
|---|---|
| Long-range gapless static sector | fail; the static range saturates (`ξ ≈ 0.53`, range 3) |
| Polarization | fail; one propagating scalar mode, the same sector MALUS already isolated |
| Local gauge redundancy | fail; a local phase moves `B`, `J`, and `E` by order one |
| Propagation / cone | fail; nodal drift tracks `v · q`, not `v |q|` |
| Signed source | unresolved; a conserved signed charge exists, but it is tied to the sheet automorphism and the conjugate is frozen |

```text
ψ field                         survives   ✓
"ψ is ordinary electromagnetism"  rejected   ✓
```

The electromagnetic program is closed unless the ontology changes (new degrees
of freedom, or a different substrate). That closure does not touch §4 or §5.

---

# 7. How the field couples to geometry

Three independent uses of `B` meet.

```text
∂E_ψ / ∂A = -2B                         DERIVED ✓          §4
    +
BR-0 (#75)  BR0-D-SELECTIVE* ✓
    the zero field is exactly flat under the sampled moves
    (§13: that state is the no-information limit, not the vacuum)
    an excitation opens energetically favorable channels
    +
BR-2 (#77)  BR2-QUADRATURE ✓
    structural response tracks cos Δθ through B
    staggered flux tracks sin Δθ through J
    +
BR-2.5 (#83)  sum map
    ψ_[uv] = ψ_u + ψ_v
    Δ‖ψ‖² = +2 B_uv
    →
              B
     ┌────────┼─────────┐
     ↓        ↓         ↓
  energy    phase     contraction
  conjugate response  norm change
```

Status: **DERIVED** for the conjugacy; **EMPIRICALLY ESTABLISHED** ✓ for the
phase response and the energetic selectivity. Conclusion that belongs in the
scaffold: `B` is the field quantity coupled directly to connectivity.

`B` causes gravity is not established. GRAV-0 (§19) is why that sentence stays
out.

---

# 8. What a geometry change is allowed to be

## 8.1 Remote relocation is not the fundamental move

Surviving conclusion, from the contraction campaign rather than from a tour
of rewiring rules:

```text
arbitrary remote edge relocation
    → unsuitable as the fundamental geometry update
```

BR-2.5 demotes the relocation move M1 to a formation and diagnostic tool.
BR-1 (#79, **BR1-FLAT** ✓) is the related debt, stated once: on pristine J₂
the neutral drift that the legal moves allow destroys the vacuum class in a
handful of moves, at every size tested. Quiescence is not explained by the
move set. That is the neutral-move debt later campaigns inherit.

## 8.2 Local contraction and splitting are admitted

BR-2.5 verdict **BR25-ONTOLOGY** ✓. The primitive is the local exchange
`u—v ↔ [uv]`.

- The move is local.
- The result stays a simple graph.
- Repeated contraction can collapse a region, and mergers use the same primitive.
- Field maps and their ledgers are quantified. The sum map ties the norm change to `B` (§7).

Contraction is many-to-one. A record-free split therefore has many preimages.
CONS-0 counts them: the split multiplicities are powers of two (and a further
degeneracy when amplitudes match). The information lost on the sum map is
exact, `|a − b|² / 2`.

Debt: **split selection**. Which preimage, or which record, comes back is not
determined by the instantaneous ontology.

---

# 9. Accounting is not a firing law

```text
CONS-0 (#88)  CONS0-PARTIAL ✓
    +
BR-2.6 (#84)  BR26-ACCOUNTED ✓
    → event accounting, conditional and exact where it closes
```

What is exact:

- Cycle rank on triangle-free domains changes by the local contraction count.
- A conditional ledger closes end to end when the bond quantity sits on the
  admissibility surface `B = B_*(c)` (six constructed families, residuals at
  `1e−13`).
- The energy change of a contraction has an exact formula, and `B` alone does
  not balance it.

What is proved absent:

- No linear combination of node count, graph energy, `Q_ψ`, and `E_ψ` is
  conserved for arbitrary states.
- There is no graph reservoir that closes the books.
- Split conservation constrains the candidates and never selects one.

```text
conservation
    → admissibility and equalities
    ✗ a law that says when the graph fires
```

Status: accounting **EMPIRICALLY ESTABLISHED** where the condition holds ✓;
the event rate is **OPEN / DEBT**. Zero-field contraction remains allowed, so
conservation also does not explain why an empty field would sit still.

---

# 10. No structural kinetics from the present ontology

BR-2.7 (#86), verdict **BR27-NO-MODE** ✓. Each expected trigger is absent
for a structural reason:

```text
energy ordering of contractions     ✗ an instability that fires
    (every uniform scan is downhill; discrete maxima do not fire)
unitary evolution of ψ             ✗ a growing structural mode
    (spectral radius exactly 1; H does not see ψ)
binary graph                       ✗ a continuous deformation coordinate
    (a weighted path leaves the frozen kind of H)
    → BR27-NO-MODE
```

Energetics and kinetics are different questions. No firing mechanism is
derived from the instantaneous ontology. The campaign's own statement stands:
one further primitive dynamical postulate is required before geometry changes.
The strong stop holds: no rate shopping on top of this null.

---

# 11. Completing the dynamics

## 11.1 Forward deterministic laws

U0 (#91) asks for a map `(G_t, ψ_t) → (G_{t+1}, ψ_{t+1})` using only the
admitted local moves.

Three contraction-only laws (bond sign, ledger sign, energy selection) pass
the structural gates: deterministic, decision-local, automorphism-covariant,
zero parameters, quotient-synchronous, accounted.

Verdict **U0-INCOMPLETE** ✓. Splits are unrealized. Energy minimization ties
on every tested bond-sign case and on 11 of 27 ledger-sign cases; at zero
field the tie is a theorem. Simultaneous local decisions also have effects
that are not bounded by the decision radius (quantified again in RAND-0).

Primary obstruction: split selection, plus one-tick effects that a purely
local rule does not contain.

## 11.2 Two boundaries do not pick one history

TIME-0 (#92) asks whether `(X_initial, X_final)` selects a unique history
under the current local constraints.

Exact census: 143 canonical graph classes, `N = 1…6`, durations `T = 2…6`,
102245 boundary pairs. Verdict **TIME0-NULL** ✓.

- Unique-history fraction `0.051` on 74977 compatible pairs, below the
  pre-registered bar `0.2`.
- A truncation-free follow-up drops the apparent `T = 2` uniqueness from
  `0.554` to `0.073`. The headline scarcity of histories was a boundary artifact.
- From the initial state alone, the median number of histories runs from 74
  to about `8×10⁵`.
- Single-step tails resolve; pooled split resolution stays below its bar.
- The symmetry control is exact (`K`-symmetry on the tested pairs; spatial
  and temporal reversal pins hold).

```text
TIME0-NULL  =  endpoints plus these local constraints do not select one history
```

That null leaves microscopic reversibility in place. The symmetry control
passed. What fails is uniqueness.

## 11.3 A stochastic completion has no derived measure

RAND-0 (#94), independent of TIME-0. Verdict **RAND0-MEASURE-DEBT** ✓.

What is in place:

- The admissible set is constructed exactly (contract or not; no scheduler and no veto smuggled in).
- Symmetry orbits, normalization, relabeling, global-phase and conjugation covariance.
- Decision locality and bitwise factorization on disjoint regions.
- Three independent generators agree.

What is not determined: probabilities on inequivalent orbits. A uniform draw
over micro-moves and a uniform draw over orbits disagree wherever a nontrivial
stabilizer exists. Directed and undirected coarse-grainings disagree on every
tested state. At one-half per edge the vacuum is not quiescent, and the effect
of one synchronous tick is not bounded by the decision.

Stochasticity is coherent. The measure is not derived.

## 11.4 No unique transition measure is forced

MEASURE-0 (#105) formalizes the debt as a campaign: 544 cells, six HARD
gates, representation-independent apparatus (physical outcome sets,
covariant, time-reversal compatible). Verdict **MEASURE0-DEBT** ✓. All
four frozen debt-reasons trigger, so no unique inter-outcome weighting is
forced. A CLOSED verdict was data-reachable and did not occur. Downstream
may consume the apparatus and the disagreement battery, never a tuned
weight.

---

# 12. Histories, without a weight

Synthesis of §9–§11, not a new result.

```text
admissible states
    +
admissible local transitions
    → admissible histories
```

The weight `μ(Γ)` on those histories is missing. That is the
**history-measure debt**.

TIME-0 and RAND-0 can become two readings of one object if a reversible
measure is ever earned:

```text
              μ(Γ)
             /    \
whole history      conditional local draw
```

Until then they are two precise ways of saying the weight is absent.

---

# 13. The vacuum field is a family

`ψ = 0` was the convenient background. BR-0 finds that background exactly
flat under the moves it samples. VAC-FIELD-0 (#100) now says what that
flatness is. Verdict **VACFIELD0-JOINT** ✓, on frozen `(J₂, H = -A)`, with
no geometry-update rule and with the candidates fixed by spectrum and
symmetry before their consequences were read.

JOINT means the full ladder: stationary, stable under perturbation,
current-free, uniform stress, coherent across amplitudes, linear,
normalized-robust, zeros in the right place, sector recorded, and a ledger
that matches an exact symmetry prediction. Three nonzero states reach it.
`ψ = 0` stops at BACKGROUND.

```text
VPLUS    ground state, E = -8, perfectly flat ledger, sector P+
         propagating and quotient-visible
VPI      variational maximum, one-sided ledger
         (every favorable relocation adds a bipartition-frustrating edge),
         sector P+
VMINUS   frozen dead-sector state, E = 0, no phase motion,
         symmetric ledger, sector P-
         joint as a state, operationally decoupled (§14)
ψ = 0    no relational information (Bmax = 0), phase undefined
         at every node, ledger with no distinguishing power
         → the no-information limit, not the vacuum
```

Perturbations propagate identically on all four backgrounds, including zero
(packet speed `1.9204`, bitwise-identical `δψ`). What the nonzero states add
is a uniform, phase-defined, stationary relational background with a
predictive ledger.

The campaign does not choose among the three. Tie-breaking by later
structural consequences is refused. Joint vacuum is a characterized family.
The propagating, quotient-visible members are VPLUS and VPI. VMINUS stays
on the record as a joint state in the transport-dead sector.

| Campaign | State |
|---|---|
| VAC-FIELD-0 (#100) | ✓ VACFIELD0-JOINT: three-member family; `ψ = 0` is the no-information limit |
| VAC-0 (#93) | ✓ for the LAW identities and the interference class split; H/I verdicts still open |
| ZERO-0 (#98) | ✓ nodal-zero census: exact zeros are interference-nodal or eigen-nodal; winding changes need no zero (§13.4) |
| VAC-EXC-0 (#103) | ✓ VACEXC0-COMPLETE: excitation physics around the family (§13.1) |
| VAC-COMP-0 (#108) | ✓ VACCOMP0-COMPLETE: the full joint manifold (§13.2) |
| VAC-SELECT-0 (#106) | ✓ VACSEL0-NOMEASURE: selection refuses without a measure (§13.3) |

Which member of the family is the physical background remains open. That is
a narrower debt than "the vacuum field might be zero."

## 13.1 Excitations see every vacuum the same way

VAC-EXC-0 (#103), verdict **VACEXC0-COMPLETE** ✓ (10/10, 241 tasks). The
excitation `δψ = ψ − ψ_vac` evolves as `δψ(t) = U(t)δ0` in the co-evolving
vacuum frame, exactly (split error `≤ 1.2e-13`). The cross-vacuum identity
is bitwise: the same excitation trajectory on VPLUS, VPI, VMINUS, and ZERO
(max deviation `0.00e+00`). The carrier is background-independent. What
differs per vacuum is the relational response, and that is §16.1.

## 13.2 The joint manifold is fully censused

VAC-COMP-0 (#108), verdict **VACCOMP0-COMPLETE** ✓. Modulo `R × U(1)`, on
even L the nonzero JOINT manifold is two isolated extremal rays (VPLUS at
`E = −8`, VPI at `E = +8`, both nondegenerate) plus one hidden real `RP¹`
JOINT circle (the VMINUS–VSTAG span in the `P₋` zero-energy sector, JOINT
except at `B = 0` BACKGROUND points), each times a full amplitude ray
(`10⁻³…10³` all JOINT). VMINUS is one translation-invariant point of a
continuous hidden-vacuum circle, not an isolated class. On odd L only the
VPLUS and VMINUS rays survive (VPI frustrated). The filed state space —
even `{VPLUS-ray, VPI-ray, CIRCLE × R₊}` plus the `B = 0` BACKGROUND sector,
odd `{VPLUS-ray, VMINUS-ray}` — is what VAC-SELECT receives, with no
preference attached.

## 13.3 Selection refuses without a measure

VAC-SELECT-0 (#106), verdict **VACSEL0-NOMEASURE** ✓. This is the
pre-registered predicted outcome, not a failure: the MEASURE gate,
re-evaluated from code, is not ready (all four MEASURE-0 debt-reasons
hold), so none of the 23 headline selection stages ran — all refusal
records. No transition weight was chosen, no vacuum ranked. The
vacuum-member debt deepens by one rung: selection needs a dynamics that is
still incomplete (§11–§12).

## 13.4 Zeros are nodal, and winding slips without them

ZERO-0 (#98), 4432 ledger rows, verdict filed in `docs/zero0-verdict.md` ✓.
Exact zeros are reachable but not generic: 1588 certified-modal events,
all from matched-amplitude two-packet destructive interference at relative
phase `π`, plus nodal eigenstates (the only persistent class). Generic and
single-packet states yield zero certified exact zeros in 1900+ rows, while
near-zeros are common. A zero is a regular point of `(r, s)` with three
exact relational consequences (incident `B = J = 0`, `ρ̇ = 0` with quadratic
touch, undefined phase). Cycle winding changes without any zero, via bond
phase-slip at `|Δθ| ≈ π` — the continuum intuition does not transfer. The
epistemic firewall held: no zero is called a particle, defect, or source.

---

# 14. Quotient mechanism

```text
MALUS-0 (#67)  M0-NULL ✓
    one propagating combination: the symmetric sheet sector
    the antisymmetric sector is exactly dead under H = -A
    +
OBS1-QUOTIENT ✓
    → QUOT-0 (#95)
    → QUOT0-OPERATIONAL ✓
```

The blind-observer quotient follows from the sheet-sector split at the
operational rung. Only quotient-compatible modes transport information, and
that is the geometry the observer reconstructs. The merger is
SECTOR pass, OPERATIONAL pass, DERIVED fail. The derived rung is blocked by
four pre-registered sub-bars that were design errors in the ratio tests,
filed with autopsies, not retuned into a pass.

What the stages show:

- The symmetric sector arrives at a distance. The antisymmetric remote
  correlator stays below `1e−9`. A sheet bit is local and does not travel.
- Diffusion and the static potential reproduce the banked square patterns
  (`R² = 0.1667` and `0.1407`) from the symmetric sector alone. The
  antisymmetric support of the potential is exactly one hop.
- A station-matched replay of the blind observer: the symmetric projector
  returns the quotient (`d` drift `0.022`); the antisymmetric projector
  measures no geometry.
- A bilayer control stays two worlds (layer contrast `0.61`). The observer
  does not merge two propagating layers. The quotient follows the dynamics.
- A staggered onsite perturbation couples the sectors locally and still
  gives the antisymmetric block no kinetic term. The induced remote sheet
  signal is order `ε²`, below the observer's resolution.

Status: **EMPIRICALLY ESTABLISHED** ✓ as an operational mechanism.
**DERIVED** is still open. Experienced geometry is the part carried by the
transporting sector. That sentence is the operational result, not yet a
derivation from the algebra alone.

## 14.1 The dead sector stores local information

HIDDEN-0 (#101), verdict **HIDDEN0-SEPARATED** ✓ (279/279). Every hidden
transformation tested — sign, phase, shape, amplitude — locally
distinguishes on at least one of `ρ/B/J` (5–6 orders above bar) while the
remote shells stay at `≤ 5.2e-15` (wave and diffusion) and the POT remote
is exactly `0.0`. The antisymmetric sector is transport-dead and
informationally live: local physics sees more than the quotient observer.

## 14.2 Hidden information reverses geometric response

HIDDEN-BR (#104), verdict **HBR0-SIGNREV** ✓ (214/214). Matched states with
equal energy and wave+POT remote blindness nevertheless carry different `B`
landscapes, hence different `dE/dA = −2B`: equal field energy does not imply
equal geometric response. Stronger: 1346 edges carry strictly opposite-sign
virtual contraction ledgers — changing only transport-hidden information
reverses the energetic ordering of structural alternatives. All virtual; no
graph operation is executed anywhere. A zero-energy pure-hidden state can
carry a nontrivial ledger: a vanishing bond field with a non-vanishing
gradient.

---

# 15. Interference is not interaction

FIELD-0 (#96), verdict **FIELD0-LINEAR** and **FIELD0-APPARENT** ✓. Fifty-seven
collision cells, frozen `H = -A`.

```text
ψ₁ + ψ₂  evolves exactly as the linear theory   (interaction witness I = 0)
ρ, B, J  still show cross terms
```

False accelerations in the atlas are large (order 50–80 in the overlap and
head-on cells) while `I` stays at numerical zero, including a static
arrangement that looks forceful and is not. Apparent drama is not a dynamical
interaction.

Any later force or matter coupling has to beat this null: `I > 0`, not a
picture of fringes.

---

# 16. Response carrier

The carrier half of a future long-range effect is the map

```text
local δψ → remote δψ → δρ, δB, δJ
```

with no force claimed. Under the frozen law the field disturbance itself is
exact, `δψ(t) = U(t) δψ(0)`. RESPONSE-0 (#99) measures how `ρ`, `B`, and `J`
answer. Verdict **RESPONSE0-KERNEL-BANKED** ✓ (G0–G14 all green, 45 cells)
plus a measured **ANATOMY**:

- The field front rides at Bloch-max speed (`v = 7.95`, `v/8 = 0.993`);
  quadratic fronts (`ρ`, `J`) ride slower (`v ≈ 5.94`); first-order `B`/`J`
  fronts on nonzero backgrounds ride at field speed.
- Measured distance laws: `|δψ| ~ r^−0.50`, `δρ ~ r^−1.00`, `δJ ~ r^−0.95`.
- The bipartite `B`-blindness theorem is pinned (chiral-real data gives
  `B = 0` exactly), with the sharpening that two-sublattice real regions
  are not blind — the prereg overgeneralization was falsified and corrected.

GRAV-0 (§19) remains the separate statement that a graph-only local update
does not carry a far disturbance. The field kernel is banked; a force
reading of it is not.

## 16.1 The same carrier gets different responses per vacuum

BG-RESP-0 (#107), verdict **BGRESP0-COMPLETE** ✓ (10/10, 77 tasks). The
carrier `δψ(t)` is background-independent (VAC-EXC-0 identity), but the
susceptibility operators differ per vacuum as operators: `χ₊ ≠ χ_π ≠ χ₋`
(pairwise Frobenius distance `√88` at every size), each of rank `2N − 1`
with the sole null direction exactly global phase, while `χ_ZERO = 0`.
Same carrier plus different vacuum gives provably different relational
response, pinned to floating-point precision. "Susceptibility" means only
this mathematical response of established relational observables — no
force, charge, or curvature is claimed.

---

# 17. What counts as one microstate

RAND-0 already shows that a uniform measure on representations and a uniform
measure on orbits are different measures. SYM-0 (#102) settles the list.
Verdict **SYM0-CLOSED** ✓ (1973 cells, 8/8 hard gates):

- Representation redundancy is exactly node relabelings and global phase.
  The microscopic state space is `X_red = X / (relabeling × U(1))`; at fixed
  nonzero norm the field sector is the projective quotient with metric
  `d_FS`. No Born rule is attached.
- Everything else tested is not redundancy: graph symmetries are distinct
  states with corresponding observables; time reversal relates histories;
  observer equivalence is channel-relative; accidental degeneracies do not
  survive the full census.

The counting list now exists. The history-measure debt cannot be closed by
declaring a uniform distribution — but at least the objects being counted
are earned.

---

# 18. The scaffold as it stands

```text
POSTULATES
├── relational graph G                         ✓
├── two real scalars (r, s) → ψ                ✓  POSTULATE
└── H = -A                                     ✓  WORKING LAW
     │
     ├── FIELD
     │     |ψ|² → conserved density            ✓  DERIVED
     │     J = 2 Im(ψ*_u ψ_v) → continuity     ✓  DERIVED
     │     B = Re(ψ*_u ψ_v)                    ✓  DERIVED
     │     ∂E/∂A = -2B                         ✓  DERIVED
     │     coherence → directed waves          ✓  EMPIRICAL
     │     sources → static response           ✓  EMPIRICAL
     │     source changes → propagating response ✓ EMPIRICAL
     │     "this is electromagnetism"          rejected ✓
     │     disturbance kernel + anatomy        ✓  EMPIRICAL
     │     vacuum-dependent susceptibility     ✓  EMPIRICAL
     │
     └── B couples to connectivity
           → local contraction / split         ✓  ontology
           → conditional accounting            ✓
           → firing law absent                 ✓  BR27-NO-MODE
           → history weight μ(Γ) absent        ⚠  DEBT

FABRIC
└── J₂  ⚠ forced working choice                ✓ adopted, not derived
      ├── transport and spectral tests         ✓ quotient; ✓ waves
      ├── operational rulers                   ✓ OBS0R-METRIC
      └── blind reconstruction                 ✓ OBS1-QUOTIENT
            → 2D quotient geometry
            → QUOT0-OPERATIONAL ✓
              transporting sector only
              DERIVED rung still open

VACUUM
├── VAC-FIELD-0      joint vacuum family        ✓ VACFIELD0-JOINT
│                    which member               still open (VAC-SELECT refuses)
├── VAC-EXC-0        background-free carrier    ✓ excitations identical on all vacua
├── VAC-COMP-0       complete manifold          ✓ two rays + hidden circle (even L)
└── VAC-SELECT-0     member selection           ✓ NOMEASURE (needs the missing measure)

HIDDEN SECTOR
├── HIDDEN-0         dead sector stores local info ✓ SEPARATED
└── HIDDEN-BR        hidden info steers response  ✓ SIGNREV (virtual ledgers)

FOUNDATIONS, CLOSED OR OPEN
├── VAC-0            substrate class            partial ✓ (LAW + square class; H/I open)
├── ZERO-0           anatomy of nodal zeros     ✓ established
├── FIELD-0          interaction null           ✓ established
├── RESPONSE-0       disturbance kernel         ✓ established
├── SYM-0            physical-state equivalence ✓ list settled
├── RAND-0           stochastic completion      ✓ coherent apparatus, measure debt
├── MEASURE-0        transition measure         ✓ debt formalized (4/4 reasons)
└── QUOT-0           quotient mechanism         ✓ operational, not derived

BLOCKED UNTIL THE DEBTS MOVE
├── a complete graph dynamics
├── formation under that dynamics
├── matter
├── a gravitational carrier from the coupled system
├── decay
└── force phenomenology beyond the FIELD-0 null
```

---

# 19. Debt register

| Debt | Origin | Meaning | What can close it |
|---|---|---|---|
| Substrate uniqueness | J₂ adoption, PR #62 | Working fabric, not a derived unique substrate | VAC-0 H/I, when the LAW / CLASS / J₂ split is finished |
| Vacuum-field member | VAC-FIELD-0 (#100) ✓ | Three nonzero states are joint vacua; `ψ = 0` is the no-information limit; VAC-SELECT refuses to rank them without a measure | A principle that selects inside the VAC-COMP manifold without using later consequences; needs the history measure first |
| History measure | U0, TIME-0, RAND-0, MEASURE-0 (#105) ✓ | Admissible histories are known more sharply than their weights; MEASURE-0 shows no unique weighting is forced | A measure principle that is reversible and matches both readings |
| Physical-state counting | RAND-0 orbit mismatch | Settled by SYM-0 (#102) ✓: `X/(R × U(1))` with `d_FS`. The measure on it is still missing | The same completion as history measure |
| Structural kinetics | BR-2.7 | Ordering and unitarity do not fire an event | The same completion, as a new primitive if that is what it is |
| Split information | BR-2.5, CONS-0 | Contraction is many-to-one | A history or stochastic treatment that carries the lost record, or a new ontology |
| Neutral quiescence | BR-1 | Legal neutral moves destroy the vacuum class | Whatever dynamics makes the vacuum an attractor |
| Matter | formation track, FIELD-0 | No dynamically stable matter, and linear overlap is not a force | Formation after a real dynamics, beating the interaction null |
| Gravity | GRAV-0 (#80) ✓ | No tested strictly local graph update both preserves J₂ and carries a disturbance past the near field | A carrier inside the coupled `(G, ψ)` dynamics, not a retry of graph-only relocation |
| Electromagnetism | EM-1 ✓ | The present `ψ` is a complex relational scalar, not ordinary electromagnetism | Closed unless the ontology changes |

The merged weak-field interface in `docs/model.md` (Newton through Mercury, conditional on its imports) is a separate lock. GRAV-0 does not retract it. GRAV-0 says that interface has not been re-derived as a far signal of local fabric updates.
