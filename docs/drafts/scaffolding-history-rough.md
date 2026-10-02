# Model Scaffolding History

This document records how the current model was progressively constrained.

It is not a history of every hypothesis tested. Failed branches are omitted unless
their failure is necessary to explain why a surviving assumption remains a debt.

Legend:

- ✓ established / merged
- ◇ established in an open or stacked PR, not yet merged
- ⚠ adopted but not uniquely derived / outstanding ontology debt
- → dependency
- + independent results combined to support a conclusion

The distinction between **postulate**, **derived result**, **empirical selection**,
and **forced working choice** should be preserved throughout.

---

# 1. Primitive postulates

## P0 — Relational ontology

The fundamental object is a graph:

    G = (V,E)

Nodes do not begin with positions in an ambient space.

Edges are relations, not distances embedded in a pre-existing geometry.

Status: ...

Evidence/dependencies:
    POSTULATE

This establishes:
    relational fabric
        ↓
    geometry must emerge from graph structure / observables

---

## P1 — Two real scalars per node

Each node carries:

    (r_u, s_u)

equivalently:

    ψ_u = r_u + i s_u

No vector direction, momentum register, or spatial coordinate is stored at a node.

Status: ...

---

## P2 — Field evolution

On fixed geometry:

    i ψdot = -A ψ

or:

    H = -A

where A is graph adjacency.

Status: ...

Consequences later established independently:

    H = -A
      ├── norm conservation
      ├── exact continuity current
      ├── interference
      ├── coherent propagation
      └── static driven response

---

# 2. Selecting the fabric

## 2.1 Required properties

Document the constraints that accumulated before/while selecting the substrate.

Examples:
- locality
- connectedness
- regularity
- ability to support coherent propagation
- appropriate effective dimensionality
- formation/closure requirements
- observer-accessible geometry

Do not list every rejected graph.

---

## 2.2 J2 selected as working fabric ⚠

J2 becomes the working microscopic substrate.

Important qualification:

    J2 was not uniquely derived.

It survived / satisfied the required tests sufficiently well and eventually became
the forced working substrate on which later experiments were built.

Therefore:

    J2 = current substrate
    ≠ proof that J2 is the unique possible substrate.

Debt:
    VACUUM / SUBSTRATE UNIQUENESS

Relevant confirmation branches:
    [campaigns/PRs]

Current follow-up:
    VAC-0 ◇
        ↓
    determine whether successful physics is:
        LAW
        CLASS
        J2-specific

---

# 3. Geometry from the fabric

Show this as a convergence of independent evidence.

    J2 microscopic structure
       │
       ├── graph-ball / Hausdorff behavior
       ├── diffusion / spectral behavior
       ├── coherent-wave ruler
       └── static-field ruler
                │
                ↓
          OBS-0 / OBS-0R
                │
                ↓
          operational metric ✓/◇

Then:

    operational metric
        +
    blind observer reconstruction
        ↓
    OBS-1-QUOTIENT ◇
        ↓
    observer reconstructs ~2D quotient geometry

Important conclusion:

    microscopic graph ≠ experienced geometry

rather:

    M_O(J2) ≈ J2 / sheet

State the measured dimensional/metric evidence.

---

# 4. Field anatomy

Starting only from:

    ψ = r + is
    H = -A

derive / establish:

## 4.1 Conserved density

    ρ_u = |ψ_u|²

    Qψ = Σ_u |ψ_u|²

    dQψ/dt = 0

---

## 4.2 Relational complex product

For an edge u-v:

    ψ_u* ψ_v

decomposes into:

    B_uv = Re(ψ_u* ψ_v)

and:

    J_u→v = 2 Im(ψ_u* ψ_v)

Then show the two independent interpretations earned experimentally/mathematically:

    J
      ↓
    exact continuity flux

    B
      ↓
    bond-energy / geometry-conjugate quadrature

with:

    ∂Eψ / ∂A_uv = -2 B_uv

This is one of the central scaffolding results.

---

# 5. Propagation and potential-like behavior

## 5.1 Coherence produces direction

    coherent extended ψ state
          ↓
       interference
          ↓
    directed propagation

POT-0:
    symmetric source → spreading without direction
    coherent packet → ballistic direction
    phase scrambling → direction disappears
    restore coherence → direction returns

Conclusion:

    direction is collective phase information,
    not a primitive node variable.

---

## 5.2 Static and propagating regimes belong to the same field

POT-1 + EM-0:

    same ψ field
       ├── stationary source-relative response
       └── propagating source-change disturbance

No second field is required.

Important qualification:

    EM-1 later falsified identification with ordinary electromagnetism.

Therefore rename conceptually:

    "EM candidate"
        ↓
    complex relational scalar field

rather than deleting the established field results.

---

# 6. EM identification tested and rejected

    POT-0/POT-1
         +
       EM-0
         ↓
    superficially EM-like unified field
         ↓
       EM-1
         ↓
    EM1-FALSIFIED ◇

Summarize structural failures:
- no admissible long-range gapless static sector
- insufficient polarization structure
- no local gauge redundancy
- wrong propagation/cone structure
- signed-source requirement unresolved

Conclusion:

    ψ field survives
    EM interpretation does not.

This is an important distinction.

---

# 7. Field ↔ geometry coupling

Show the independent convergence on B.

    field energy
        ↓
    ∂E/∂A = -2B

    BR-0
        ↓
    structural preference follows bond energy

    BR-2
        ↓
    phase controls structural response
    B ~ cos Δθ
    J ~ sin Δθ

    BR-2.5
        ↓
    local contraction ontology
    ψ_[uv] = ψ_u + ψ_v
        ↓
    Δ||ψ||² = 2B_uv

Therefore:

                   B
          ┌────────┼────────┐
          ↓        ↓        ↓
      field energy  phase   contraction
      conjugate     response accounting

Conclusion:

    B is the established field quantity most directly coupled to geometry.

---

# 8. Geometry-change ontology

## 8.1 Arbitrary relocation demoted

Do not narrate all failed rewiring campaigns.

State only the surviving conclusion:

    arbitrary remote edge relocation
        ↓
    unsuitable as fundamental geometry dynamics

M1 remains a formation/diagnostic operation where appropriate.

---

## 8.2 Local contraction/splitting admitted

BR-2.5:

    u-v ↔ [uv]

Properties:
- local
- simple graph preserved
- collapse/merger possible
- field map/accounting quantified

Status: ...

But:

    contraction = many-to-one

so record-free splitting is degenerate.

Debt:
    information / split selection.

---

# 9. Conservation and event-law boundary

Combine CONS-0 + BR-2.6.

    CONS-0
       +
    BR-2.6
       ↓
    exact event accounting

But:

    conservation
        ↓
    admissibility/equality constraints
        ✗
    firing law

Record important exact ledger(s).

Conclusion:

    accounting is partially/conditionally understood,
    but conservation does not tell geometry when to change.

---

# 10. No derived structural kinetics

BR-2.7:

    energy ordering
        ✗ instability

    unitary ψ evolution
        ✗ growing structural mode

    discrete graph ontology
        ✗ continuous deformation coordinate

Therefore:

    BR27-NO-MODE

Conclusion:

    energetics ≠ kinetics.

No firing mechanism is derived from the existing instantaneous ontology.

---

# 11. Attempts to complete structural dynamics

This section should be concise and conceptual.

## 11.1 Deterministic forward completion

U0:

    (G_t, ψ_t) → ?

Minimal candidate laws tested.

Result:

    U0-INCOMPLETE

Primary obstruction:
    split selection remains non-unique;
    simultaneous local decisions can have extensive one-tick effects.

---

## 11.2 Two-boundary uniqueness

TIME-0:

    (X_initial, X_final)
          ↓
      history Γ ?

Exact enumeration shows many histories remain.

Result:

    TIME0-NULL
    for UNIQUE two-boundary history selection.

Important qualification:

    this does NOT falsify microscopic time-reversal symmetry.

It falsifies only:
    endpoints + current local constraints → unique history.

---

## 11.3 Stochastic completion

RAND-0:

    X
     ↓
    admissible set A(X)
     ↓
    probability measure ?

What succeeded:
- exact admissible-set construction
- symmetry orbits
- normalization
- covariance
- locality of decisions
- factorization controls

What did not:
- symmetry does not uniquely determine probabilities between inequivalent orbits.

Result:

    RAND0-MEASURE-DEBT ◇

Therefore:

    stochasticity is mathematically coherent,
    but the measure is not yet derived.

---

# 12. Current history-level picture

This should be a synthesis, not a new claim.

We now know how to define much of:

    admissible states
        +
    admissible local transitions
        ↓
    admissible histories H

But we do not yet know:

    μ(Γ)

the physical measure/weight over histories.

Thus current fundamental debt:

    HISTORY-MEASURE DEBT

TIME and RAND may eventually become two descriptions of the same object:

                 μ(Γ)
                /    \
               /      \
      whole-history    conditional/local
        description      stochastic view

provided a reversible measure can eventually be earned.

---

# 13. Vacuum concept

Historical assumption:

    ψ_vac = 0

was convenient but not derived.

Current evidence motivates reconsideration.

Possible joint vacuum:

    X_vac = (G_vac, ψ_vac)

with:

    ψ_vac ≠ 0

potentially evolving by global phase while relational observables remain stationary.

Current open campaigns:

    VAC-0 ◇
       ↓
    which graph/substrate class?

    VAC-FIELD-0 ◇
       ↓
    which stationary field background?

    ZERO-0 ◇
       ↓
    what is special about ψ=0?

Do NOT document the nonzero vacuum as established until these close.

---

# 14. Operational geometry / hidden microstructure

Combine:

    MALUS / sector structure
        +
    OBS-1 quotient reconstruction
        ↓
    QUOT-0 ◇

Current hypothesis:

    symmetric sector → transports quotient information
    antisymmetric sector → microscopic but transport-dead

Possible conclusion if QUOT-0 passes:

    experienced geometry is dynamically selected by
    information-carrying sectors.

Mark as open until verdict.

---

# 15. Interaction null

FIELD-0 ◇ establishes the baseline:

    ψ1 + ψ2 evolves linearly

while:

    ρ, B, J

contain interference cross terms.

Purpose:

    dramatic observable interference
        ≠
    genuine dynamical interaction

Future forces/matter interactions must exceed this null.

---

# 16. Response carrier

RESPONSE-0 ◇:

    local δψ
        ↓
    remote δψ
        ↓
    δρ, δB, δJ

This characterizes the carrier half of any future long-range interaction without
claiming a force.

---

# 17. Physical-state equivalence

SYM-0 ◇ asks:

    what counts as one physical microstate?

Distinguish:
- node-label redundancy
- global-phase redundancy
- physical symmetry
- time reversal
- observer equivalence
- genuinely distinct state

This feeds directly into RAND's measure debt because:

    uniform over representations
    ≠
    uniform over physical states.

---

# 18. Current model scaffolding tree

The document should culminate in something approximately like:

POSTULATES
│
├── relational graph G
│
├── two real scalars (r,s) → ψ
│
└── H = -A
     │
     ├─────────────── FIELD ─────────────────┐
     │                                        │
     │   |ψ|² → conserved density             │
     │   Im(ψ*u ψv) → current J               │
     │   Re(ψ*u ψv) → bond quantity B         │
     │                                        │
     │   coherence → directed waves           │
     │   sources → static response             │
     │   source changes → propagating response │
     │                                        │
     └────────────────────────────────────────┘
                         │
                         │ B couples energetically to connectivity
                         ↓
                    BACKREACTION
                         │
                 local contraction/split
                         │
                accounting understood
                         │
                 firing/measure missing
                         ↓
                 HISTORY-MEASURE DEBT


FABRIC SELECTION
│
└── J2 ⚠ forced working choice
      │
      ├── transport / spectral tests
      ├── operational rulers
      └── OBS reconstruction
              ↓
         2D quotient geometry
              │
              └── QUOT-0 ◇ mechanism pending


CURRENT OPEN FOUNDATIONS
│
├── VAC-0 ◇          substrate class
├── VAC-FIELD-0 ◇    vacuum ψ background
├── QUOT-0 ◇         quotient mechanism
├── ZERO-0 ◇         ψ=0 anatomy
├── FIELD-0 ◇        interaction null
├── RESPONSE-0 ◇     disturbance kernel
└── SYM-0 ◇          physical state equivalence


BLOCKED DOWNSTREAM PHYSICS
│
├── complete graph dynamics
├── formation under mature dynamics
├── matter identification
├── gravity
├── decay
└── force phenomenology

---

# 19. Debt register

Finish with a compact debt table.

| Debt | Origin | Meaning | What can close it |
|---|---|---|---|
| Substrate uniqueness | J2 selection | J2 is working fabric, not uniquely derived | VAC-0 |
| Vacuum-field state | BR0/current vacuum assumption | ψ=0 not justified as physical vacuum | VAC-FIELD-0 |
| History measure | U0/TIME0/RAND0 | admissible histories known better than their weights | future measure principle |
| Physical state counting | RAND0 | measure depends on what counts as distinct | SYM-0 |
| Structural kinetics | BR27 | no derived firing mechanism | potentially history measure/completion |
| Split information | BR25/CONS | contraction many-to-one | stochastic/history treatment or new ontology |
| Matter | formation track | no mature dynamically stable matter yet | formation after dynamics |
| Gravity | GRAV0 | old graph-only carrier failed | mature coupled dynamics |
| EM | EM1 | current ψ field is not ordinary EM | closed unless ontology changes |

---

# Writing principles

1. Prefer dependency trees over chronology.

2. Clearly label:
   - POSTULATE
   - DERIVED
   - EMPIRICALLY ESTABLISHED
   - WORKING CHOICE
   - OPEN / DEBT

3. Add the requested unmerged marker directly to every result whose supporting PR is still open.

4. A later null must not erase an earlier valid result.

   Example:

       EM0 established field structure.
       EM1 falsified the EM interpretation.

   Do not write:
       "EM0 was wrong."

5. Preserve historical amendments where they materially changed what was established, but do not turn the document into an amendment log.

6. Failed exploratory routes should normally be omitted.

7. Include a result only when it became part of the surviving model scaffolding or explains an explicit present debt.

8. Whenever a conclusion required independent branches, show the merge explicitly:

       result A
          +
       result B
          ↓
       model conclusion

9. Distinguish the microscopic model from interpretations:

       ψ field ✓
       "ψ is electromagnetism" ✗

       operational quotient ✓
       "this is spacetime" not yet established

       B geometry conjugacy ✓
       "B causes gravity" not established

10. End with the current minimal model, not with the chronology.

The reader should be able to answer:

    What are we assuming?
    What did we derive?
    What did experiments establish?
    Why J2?
    Why ψ?
    Why B and J?
    Why the quotient?
    What remains arbitrary?
    Which results are still in open PRs?
    What physics is currently blocked?
