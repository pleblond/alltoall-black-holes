# Cayley-growth probe — mini-preregistration

**Status:** preregistered BEFORE any computation on branch
`cursor/cayley-growth-736b`. All families, radii, windows, seeds, and
bars below are frozen. Results go to `results/cayley/*.json` +
`docs/CAYLEY_REPORT.md` only.

**Question:** which homogeneous (Cayley) vacua grow exactly like r³?
Bass–Guivarc'h makes this answerable: nilpotent growth degree =
Σ k·rank(γ_k/γ_{k+1}). Three frozen representatives:

| # | Group | Presentation / model | Generators S | Predicted growth |
|---|---|---|---|---|
| K | Klein-bottle group | ⟨x,y \| xyx⁻¹=y⁻¹⟩, normal form x^k y^m | {x±1, y±1} | **2** (virtually Z²) |
| Z | Z³ | (a,b,c) ∈ Z³ | {±e1, ±e2, ±e3} | **3** (calibration) |
| H | Heisenberg UT₃(Z) | (x,y,z), (x,y,z)(x′,y′,z′)=(x+x′,y+y′,z+z′+xy′) | {a±1, b±1}, a=(1,0,0), b=(0,1,0) | **4** (ranks (2,1) → 1·2+2·1) |

Neighbor rules (frozen): K: (k,m)·x=(k+1,−m), ·x⁻¹=(k−1,−m),
·y=(k,m+1), ·y⁻¹=(k,m−1). Z: coordinate ±1. H: right-multiplication
by a±1=(±1,0,0), b±1=(0,±1,∓1·0)=(0,±1,0) under the group law above.

## Procedure (frozen)

- BFS balls B(r) from identity to **R = 12** (exact normal forms, no
  sampling). Record |B(r)|, r = 0..12.
- Fit: OLS on log|B(r)| vs log r over **r ∈ [5, 11]** (avoids small-r
  transient; infinite groups → no saturation). Report degree d + R².
- Seeds: none stochastic (exact enumeration). Deterministic by
  construction; tests assert group laws + small-radius exact counts.

## Bars (frozen)

- **PASS(group)** iff |d − pred| ≤ 0.35 AND R² ≥ 0.95,
  pred ∈ {2 (K), 3 (Z), 4 (H)}.
- **Z is calibration:** Z fail → METHOD-FAIL (technique broken, no
  physics verdict on K/H). K/H fail with Z passing → recorded per
  group (theory tension, not method failure).
- Heisenberg reading 4 (not 3) despite Hirsch length 3 is the
  preregistered trichotomy instance (topologically 3D, metrically 4D).

## Exploratory (no bars)

- Exact Ollivier-κ (P4, `orici` exact) on 20 seeded interior edges
  (seed=0, boundary distance ≥ 2) of each r ≤ 8 ball induced subgraph.
  Reported mean ± SEM; cubic-lattice κ≡0 is the informal reference.
- Wall-time/memory note for scale-up (N at R=12 per group).

## Labels / non-goals

All numbers exploratory (measurements) except group-law facts
(derived). Non-goals: closing D10 (stays open); selecting THE vacuum
(this probe *lists* homogeneous candidates, it does not select);
observatory data; "confirm" without a bar.
