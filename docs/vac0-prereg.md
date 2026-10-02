# VAC-0 Master Preregistration — Vacuum Universality and Substrate Necessity

Frozen before any VAC-0 headline phenomenology runs. Amendments allowed only
pre-data per stage (short addenda `docs/vac0-{stage}.md` committed before the
corresponding beast campaign launches).

## 1. Frozen field law (all substrates, no exceptions)

- `H(G) = -A(G)`, `J = 1`, `hbar = 1`. No onsite terms, no edge weights, no
  degree terms, no graph-dependent source strength, no fitted time rescaling.
- Every node carries `psi_u = r_u + i s_u`. No extra internal state.
- Apparatus vendored byte-identical from sibling branches (see PR description
  for provenance). VAC-0 does not modify vendored files; all VAC-0-native code
  lives in `src/bh_graph/vac0*.py`, `scripts/vac0_*.py`, `tests/test_vac0*.py`.

## 2. Port rules (how frozen apparatus moves across substrates)

LAW (dynamics + identities) is frozen. READOUT geometry is ported by these
canonical rules; anything outside them is UNDEFINED, never FAIL-by-stretch:

- **P2.1 Coordinates.** Coordinate readouts (COM, MSD-alpha, velocity fits,
  flux D, spectral coherence C) use each family's NATIVE lattice coordinates
  (frozen in `vac0.py`, §4). Families without coordinates (random regular)
  get UNDEFINED for coordinate-only cells and use intrinsic readouts
  (graph-distance shells, IPR, arrival times) where the stage addendum defines
  them.
- **P2.2 Momenta.** Gaussian packets use the same numerical `k` in native
  lattice units per stage addendum (headline: `k = 0.5` along x/a1 for
  ballistic/coherence stages). No per-substrate k tuning.
- **P2.3 Drive frequency (POT-1 port).** `omega(G) = -(rho(A) + 0.5)` where
  `rho` is the measured adjacency spectral radius (gap 1/2 below band edge,
  matching the J2 banked gap; `is_gap_ok` must pass or the cell is UNDEFINED).
  Drive amplitude `s = 1.0`, `dt = 0.02` frozen.
- **P2.4 Barriers/walls/slits.** Geometry-only bond/node cuts defined per
  family in the stage addendum, spectrally analyzed before dynamics. If no
  canonical construction exists, the cell is UNDEFINED (never FAIL).
- **P2.5 Observer.** Headline dimension from velocity-free estimators
  (Hausdorff, spectral, Weyl). Wavefront-radius readouts use the VAC-0D
  measured group velocity of the SAME substrate (operational, frozen before
  OBS runs open). No J2 velocity prior on non-J2 substrates.

## 3. Classification scale (primary output)

Every matrix cell: PASS / FAIL / UNDEFINED + quantitative readout.
Phenomenon-level labels: LAW (generic) / CLASS (substrate class) /
J2 (J2-only among tested) / ACCIDENTAL (fragile on J2 itself).

## 4. Frozen substrate battery (VAC-0B)

Headline families (2 sizes each unless noted; all builders deterministic):

| id | builder | sizes (N) | coords |
|----|---------|-----------|--------|
| j2 | `formation.j2_torus_graph(L)` | L=20 (800), L=28 (1568) | quotient (x,y), periods (L,L) |
| j2quot | `vac0.quotient_j2(L)` | L=20 (400), L=28 (784) | (x,y), periods (L,L) |
| square | `graphs.build_torus_grid(n)` | n=28 (784), n=40 (1600) | (x,y), periods (n,n) |
| ring | `nx.cycle_graph(N)` | N=400, N=1600 | 1D, period N |
| tri | `vac0.build_triangular_torus(L)` | L=28 (784), L=40 (1600) | axial 2D, periods (L,L) |
| hex | `vac0.build_hex_torus(L)` | L=28 (784), L=40 (1600) | brick-wall 2D, periods (L,L) |
| rr3 | `graphs.build_random_regular(N,3,seed)` | N=1600, seeds {0,1,2} | none (intrinsic only) |
| rr4 | `graphs.build_random_regular(N,4,seed)` | N=1600, seeds {0,1,2} | none (intrinsic only) |
| rr8 | `graphs.build_random_regular(N,8,seed)` | N=1568, seeds {0,1,2} | none (intrinsic only) |
| j2swap8 | degree-preserved 8-swap J2(L=28) | seeds {0,1,2} | J2 labels kept |
| j2rewire | degree-preserved 20000-swap J2(L=28) | seeds {0,1,2} | J2 labels kept |
| path | `driven.path_graph(N)` (calibration only) | N=200 | 1D open |

Held-out families (VAC-0Q/C7; frozen now, opened only for validation):
poisson_delaunay, gabriel, knn(k=6), medial_quad, noisy_grid(q=0.1),
gated_wall — N≈1600, seeds {0,1} — plus short_rewired_grid as the
span-control. No held-out graph may inform `V(G)` formulation.

VAC-0M note: the sheet-breaking family is `j2swap8` (few-swap,
symmetry-breaking but geometry-preserving). If QUOT-0 freezes a different
perturbation family, it is added as a SECONDARY VAC-0M arm (pre-data
amendment), never replacing `j2swap8`.

## 5. VAC-0C census (recorded pre-phenomenology per substrate)

N, degree histogram, mean degree, spectral radius rho(A), second-moment gap
(rho - |lambda_2|), bipartiteness, triangle count, ball-growth exponent,
heat-trace ds plateau, Weyl ds, vertex-transitivity-by-construction flag,
quotient/layer structure. Census code in `vac0.py`; data filed in
`data/vac0/census.json`. No outcome labels are opened during the census.

## 6. Stage addenda + verdict ladder

Each phenomenon stage (D through K) gets a frozen addendum with exact ports,
(T, dt), seeds, and PASS/FAIL thresholds ported from the banked campaign
criteria (P1.1/POT-0/POT-1/SLIT/TUN/BR/OBS), committed before its beast run.
Final synthesis (O/P/Q/R/S) follows the campaign brief's verdict ladder
(VAC0-GENERIC / CLASS / J2 / FRAGILE / NO-VACUUM). No-selection firewall:
VAC-0 never modifies the substrate program or feeds features back into
formation dynamics.
