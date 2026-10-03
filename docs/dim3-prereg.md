# DIM3-PREREG — Three-Dimensional Operational Vacuum (FROZEN PRE-DATA)

Campaign: DIM-3-0. This document predates ALL DIM-3-0 headline measurements.
Design-only pilots (local reasoning + one beast pilot at J3 torus L=4 /
ball R<=6, construction + spectrum algebra only) were used to verify the
Stage-A derivation below. NO operational-dimension, spreading-exponent,
packet, static-response, hidden-sector, or vacuum-census measurement was
run before this freeze. All bars are inherited from banked campaigns or
derived from the locked dispersion law — none are fit to DIM-3-0 data.

Frozen law (firewall): `H = -A`, `J = 1` headline, no onsite term, no edge
weight, no retuned source strength, no observer prior. No coordinates enter
dynamics; coordinates appear only as readout labels (quotient/microscopic
geometry joins happen strictly after blind artifacts freeze + hash).

## A. Candidate derivation (pre-data): the J3 family

### A1. The J2 construction principle (read off the banked substrate)

`J2 = Z^2 ⋊ Z2` with the swap action, Cayley generators
`{±h1, ±h2} × {sheet-preserving, sheet-flipping}` (8, inverse-closed):

- P1 base `Z^d` (translation lattice), fiber `Z2` (two sheets);
- P2 nontrivial fiber action permuting base axes (for d=2 the unique
  nontrivial permutation, the transposition `x↔y`);
- P3 generators = axis steps × sheet options (all sign/fiber variants);
- P4 quotient collapsing the fiber is the `d`-dimensional hypercubic
  lattice with uniform micro-multiplicity;
- P5 sheet swap `S` is a graph automorphism with `[H,S] = 0`,
  `H·P_anti = 0`, and the symmetric sector is the quotient walk with
  hopping `2J` (MALUS-0 mechanism);
- P6 bipartite with `q = Σx_i` (every micro-move flips parity).

### A2. Minimal lift to d=3

Apply P1–P6 with `d = 3`, changing NOTHING else:

```text
J3 = Z^3 ⋊ Z2,  Z2 acts by a coordinate transposition (wlog x↔y, z fixed)
gens = {±ex, ±ey, ±ez} × {b=0, 1}   (12, inverse-closed)
```

The 3 transpositions `(x↔y), (y↔z), (x↔z)` are conjugate under cubic
rotations, so the family has ONE member up to cubic symmetry. The campaign
tests the `x↔y` representative; the other two follow by relabeling (exact
graph isomorphism, pinned in tests).

### A3. Minimality criteria (M1–M5) and rejected alternatives

- M1 smallest fiber: `|fiber| = 2` (a 1-sheet graph is the bare cubic
  lattice, not a J-lift; larger fibers are non-minimal).
- M2 smallest degree given M1: `2·d·2 = 12` (axis × sign × sheet option).
- M3 exact hypercubic quotient with uniform multiplicity.
- M4 P5 sector mechanism intact (`[H,S]=0`, dead antisymmetric sector).
- M5 bipartite (chiral-real `B`-blindness structure preserved).

Rejected (filed, not tested at campaign scale):

- R1 direct product `Z^3 × Z2` (trivial action): fails M4 — it is the
  QUOT bilayer control (two propagating layers, observer must NOT merge).
  Tested ONLY as the Stage-H control, same as QUOT-0.
- R2 fiber `Z3/C3/S3` (cyclic/full permutation action): fails M1/M2
  (degree 18/36, fiber 3/6). Non-minimal; noted as the first fallback if
  the minimal candidate fails operationally AND the failure is diagnosed
  as fiber-action asymmetry (it is not expected to be: the quotient and
  the Γ-point Hessian are exactly cubic — see B).
- R3 bare cubic lattice: fails M1 (no hidden sector, no J-structure).

If the campaign finds that no member of the transposition family satisfies
M1–M5 jointly with the operational stages, the verdict is
`DIM3-NATURALITY-DEBT` (no unique natural construction forced).

### A4. Exact Stage-A predictions (pinned in tests, no tolerance)

- Degree exactly 12; torus `N = 2L^3`, `E = 12L^3`; connected.
- Quotient `(x,y,z,b)→(x,y,z)` is the cubic torus: every quotient edge
  axis-adjacent, multiplicity exactly 4 per coarse edge.
- Bipartition `q = x+y+z (mod 2)`; every edge bichromatic.
- Sheet swap `S`: involution, symmetric, `[H,S] = 0` exactly,
  `H·P_anti = 0` exactly.
- Symmetric embedding `U`: `H·U = U·H_Q` exactly with
  `H_Q = -2J·A_cubic` on cells.
- Micro shell/cut laws differ from the cubic quotient (UV structure
  invisible to the quotient), same pattern as J2 (`8r` vs `4r`).

## B. Spectrum (derived from the locked law)

Bloch (translation group `Z^3`, two-site basis): with
`f(k) = 2(cos kx + cos ky + cos kz)`,

```text
A(k) = f(k) [[1,1],[1,1]],  H(k) = -J·A(k)
eps_disp(k) = -4J(cos kx + cos ky + cos kz),  eps_flat = 0
v(k) = 4J (sin kx, sin ky, sin kz)
Hess(k) = diag(4J cos kx, 4J cos ky, 4J cos kz)
```

- Band bottom `-12J` at Γ, top `+12J` at `(π,π,π)`, flat band at 0,
  touching where `cos kx + cos ky + cos kz = 0`.
- Γ-point: `v = 0`, `Minv = 4J·I_3` exactly isotropic,
  `m* = 1/4J`, cubic term 0, quartic `-(J/6)(qx^4+qy^4+qz^4)`.
- Maxima (J=1): axial 4, euclidean `4√3 ≈ 6.928` at `(π/2,π/2,π/2)`,
  Manhattan 12 (causal front bound; operational fronts must respect it).
- Anisotropy enters at quartic order and in `v·q` drift away from Γ —
  the SAME structure as the bare cubic lattice (no EXTRA anisotropy from
  the fiber; the `z`-fixed transposition is invisible at this order).
- Static drive rule (inherited, `obs0r.omega_below_edge`): `ω = -(z+0.5)`:
  J3 `-12.5`, cubic `-6.5`, 12-regular expander `-12.5`, J2 `-8.5`
  (matches banked `OMEGA_J2`). Gap `0.5` below band edge in all cases.
- Bloch-vs-brute: sorted spectra agree to `< 1e-9` (inherited bar from
  `continuum.is_bloch_ok`), zero count `= L^3 + touching` exactly.

## C. Blind dimension (OBS port, no dimension/coordinates)

Reuse `bh_graph.obs1` blind estimators VERBATIM (same module, same frozen
bars). Instruments: same mathematical protocol as OBS-1 (threshold-crossing
`τ_W` at `THETA_WAVE=1e-6`, `τ_D` first threshold-crossing at the same
floor, static `φ` with `s=1` via the same equation), implemented with
Krylov evolution (`expm_multiply`) + CG statics instead of dense
eigensystems (identical mathematics, feasible at 3D sizes; cross-checked
against dense spectral evaluation at L≤6 in tests). Grids: wave `dt=0.05`,
`Tmax=D`; diffusion `dt=0.25`, `Tmax=3(D/2)²` (same rules as OBS-0).
Stations: 64 opaque, 3 sets, `rng(9100 + 100*cell + set)`, train S0–31 /
test S32–63 (same rule; cell ids in the frozen order below).

Frozen cells (blind stage sees ONLY integer cell id):

```text
0 j3-L8    1 j3-L12   2 j3-L16    (headlines: cubic-quotient target)
3 cb-L10   4 cb-L15   5 cb-L20    (C0: known-3D cubic control, matched N)
6 ex-N1024-s0 7 ex-N3456-s0 8 ex-N8192-s0  (C1: non-Euclidean control, 12-reg)
9 j2-L42                       (C2: known-2D control, reconstructs 2D)
```

N: j3-L8=1024, j3-L12=3456, j3-L16=8192; cb-L10=1000, cb-L15=3375,
cb-L20=8000; expanders matched to J3 N; j2-L42=3528 (≈ j3-L12).

Headline blind gates (J3 cells, composite channel):

- C-a `d_O` (volume_dimension median): `|d_O − 3| ≤ 0.25` (10% window;
  2D precedent measured 1% off; window widened once, pre-data, for 3D
  station sparsity — FROZEN here, never retuned).
- C-b `d* = 3` on train AND test (`select_dimension` majority-distortion
  rule, unchanged; `MDS_DIMS` already includes 3, 4 — no prior added).
- C-c volume fit quality `r² ≥ 0.85` (inherited `VOL_R2_BAR`).
- C-d composite completeness `≥ 0.98` (inherited), symmetry med/p90
  (inherited bars), near-metric composite (inherited loose bar).

Controls: C0 cubic cells must also read 3D (same C-a/C-b gates);
C2 J2 cell must read `d_O ≈ 2`, `d* = 2` (same estimators — 2D
reconstructs 2D); C1 expanders must reject Euclidean 3D
(`d* ≠ 3` with pass=False, or locality collapse — same rule as OBS-1).

## D. Metric (reveal joins AFTER blind freeze + hash)

- D-a distance match vs hidden cubic quotient `< 0.30` (inherited
  `DIST_MATCH_BAR`), and strictly closer than vs the microscopic graph
  (factor ≥ 1.5×, same pattern as OBS-1 "twice as close").
- D-b locality fraction `> 0.70` (inherited), sheet contrast `< 0.05`
  (inherited `SHEET_BLIND_BAR`), angle consistency (inherited).
- D-c local charts: MDS-3 ball charts `< 0.30` (same numeric bar as the
  OBS-1 2D-chart bar, dimensionally completed); the frozen MDS-2 chart
  readout is KEPT as a control leg and is EXPECTED to distort on 3D
  data (2D charts fail where 3D charts pass — filed, not gated).

## E. Wave spreading (RESPONSE port)

Point R/I impulse (unit, `eps=1e-3` battery legs), BG0, `T=16/dt=0.05`
(same as RESPONSE-0), quotient-shell fits on shells 2..10 (same window),
relative threshold `1e-3` × remote peak + absolute floors (same).

- E-a field front rides at Bloch-Manhattan fraction: `v/12 ∈ [0.90, 1.00]`
  (2D precedent `v/8 = 0.993`; window from the derived bound, pre-data).
- E-b `|δψ| ~ r^−α`, `α ∈ [0.80, 1.20]`, `r² > 0.9` (theory: spherical
  `r^−1` far field; 2D precedent `r^−0.50` for cylindrical).
- E-c 2D control: J2-L28 rerun gives `α ∈ [0.40, 0.60]` (same apparatus
  reconstructs the banked 2D law).

## F. Quadratic spreading (same shots as E)

- F-a `δρ ~ r^−α`, `α ∈ [1.70, 2.30]`, `r² > 0.9` (theory `r^−2`).
- F-b `δJ ~ r^−α`, `α ∈ [1.70, 2.30]`, `r² > 0.9` (theory `r^−2`).
- F-c `δB`: bipartite-blindness structure holds (chiral-real data gives
  `B = 0` exactly where the theorem applies — same theorem, J3
  bipartition); envelope exponent filed descriptively (no bar — the
  theorem leg is the gate).
- F-d cubic control shows the same exponents (class-level check, same
  windows — filed whether J3-only or cubic-class).

## G. P1/POT port

- G-a packets: gaussian on quotient coords, `σ ≪ L`, `k` along x:
  ballistic with Bloch velocity `4 sin kx` within 10%, reverses under
  `k→−k` (same protocol as P1.1), norm conserved to `1e-9`.
- G-b POT0-COLLECTIVE: symmetric source spreads without direction,
  coherent packet directs, phase scrambling kills direction, coherence
  restore returns it (same 4-rung battery, same bars).
- G-c POT1 static: gap-matched `ω = −12.5`, single-node source: static
  regime exists (solver converges, exact equation residual `< 1e-9`),
  range `ξ` filed descriptively (no Coulomb claim — J2 precedent is
  `ξ ≈ 0.53` short-range; the gate is existence + equation-exactness,
  not a 3D `1/r` law).
- G-d source-switch front: `v/12 ∈ [0.85, 1.00]` (same protocol as EM-0
  transient / RESPONSE-0 switch; window widened once pre-data for the
  3D precursor).

## H. QUOT/HIDDEN port

- H-a `[H,S] = 0`, `H·P_anti = 0`, `H·U = U·H_Q` exact (Stage-A pins,
  re-verified at campaign L).
- H-b sym/anti wave capacity: antisymmetric remote correlator `< 1e-9`
  (same bar as QUOT-0), symmetric arrives.
- H-c diffusion sector norms: same pattern as QUOT-0 (symmetric carries
  the banked cubic pattern, antisymmetric localizes — descriptive `R²`
  filed, gate is the sector separation, not a value).
- H-d POT sector anatomy: antisymmetric support exactly one hop (same),
  symmetric reproduces the static pattern.
- H-e bilayer-cubic control: two worlds, layer contrast `> 0.30`
  (QUOT-0 measured 0.61 on square; window lowered once pre-data for 3D
  dilution — FROZEN here).
- H-f HIDDEN-0 port: matched hidden transformations locally
  distinguishable (same readout, `≥ 5` orders above bar) while remote
  wave/diffusion shells stay blind (same `5.2e-15`-scale bar, inherited)
  and POT remote is exactly `0.0`.
- H-g HIDDEN-BR port (virtual ledgers only, no graph mutation):
  opposite-sign virtual contraction ledgers exist (count filed;
  gate is existence on `> 100` edges — QUOT precedent 1346).

## I. VAC-FIELD port (frozen `(J3, H = −A)`)

Candidates: VPLUS (uniform, `E = −12`), VPI (bipartite-staggered,
`E = +12`, even L), VMINUS (sheet-antisymmetric uniform, `E = 0`,
`P_−` sector), ZERO (no-information control). JOINT ladder gates
(inherited numeric bars from `vacfield.py`):

- I-a stationary (`is_stationary_ok`), eigen-residual `< 1e-9`,
  Rayleigh energies exact.
- I-b current-free, uniform stress, phase-invariant, amplitude-scaling.
- I-c ledger: VPLUS perfectly flat, VPI one-sided, VMINUS symmetric
  (same patterns as J2; values scale with degree — patterns gated,
  values filed).
- I-d census across L ∈ {4, 8} (+12 if cheap): same membership.

## J. Size scaling

- J-a E/F exponents consistent across L ∈ {8, 12, 16} (spread `< 0.20`).
- J-b blind `d_O` consistent across J3 cells (spread `< 0.30`).
- J-c no post-data substrate redesign: the tested graph is the
  preregistered `x↔y` representative at all sizes.

## Verdicts

- `DIM3-OPERATIONAL`: A (M1–M5 exact) + B (Bloch exact) + C (C-a…C-d on
  all J3 cells) + D (D-a…D-c) + E (E-a, E-b) + F (F-a…F-c) pass, with
  controls C0/C1/C2 behaving as preregistered. Blind geometry AND
  spreading independently support 3D.
- `DIM3-GEOMETRIC`: A + B pass (graph quotient is exactly 3D) but the
  operational probes (C–F) do not jointly recover it.
- `DIM3-NOT3D`: operational probes positively recover non-3D
  (e.g. `d* = 2` stable, or 2D-like exponents with 3D excluded by the
  preregistered windows).
- `DIM3-NATURALITY-DEBT`: no unique natural J2→J3 construction is
  forced (Stage-A failure: M1–M5 cannot be jointly satisfied, or
  inequivalent minimal lifts split the family). Decided before headline
  data; if Stage A passes exactly, this verdict is off the table.

## Controls (summary)

Unchanged `H = −A` (same module-level law, no new terms); blind observer
(same `obs1` estimators, opaque stations, hash-frozen reveal); 2D controls
reconstruct 2D (C2 + E-c); cubic controls (C0 + F-d: 3D-class checks);
expander rejects Euclidean 3D (C1); Bloch-vs-brute spectrum (B);
graph-intrinsic dynamics (no coordinates in any evolution); multiple sizes
(J); no post-data substrate redesign (frozen representative).

## Sizes and compute

Exact/dense (tests + analysis): ball R≤10, torus L ∈ {4, 6, 8}.
Campaign (beast, xargs-parallel, `nice`, JOBS≤24): blind cells as in C;
spreading L ∈ {8, 12, 16} (+L=20 far-shell leg if cheap); G/H/I as sized
above. Full suite on beast, `skip tests/test_weighted.py` (slow, per
campaign instructions).
