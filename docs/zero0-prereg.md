# ZERO-0 — Zero Crossing and Phase-Singularity Census: Preregistration

Frozen prereg for the ZERO-0 campaign. Branch: `cursor/zero-crossing-census-ee5c`.
Apparatus: `src/bh_graph/zero.py`, tests `tests/test_zero.py`,
runners `scripts/zero0_campaign.py` + `scripts/analyze_zero0.py`.

## 1. Frozen ontology

- Geometry frozen: every run evolves under one fixed graph G.
- Field law (headline J = 1, hbar = 1): `i ψ̇ = -A ψ`, i.e. `H(G) = -A(G)`
  (P1/EM-0 locked convention, `ballistic.hamiltonian`).
- Cartesian variables `ψ = r + i s` are the regular variables.
  `θ = arg ψ` undefined at `ψ = 0` by definition (phase-coordinate
  singularity only).
- `ρ_u = |ψ_u|^2`, `B_uv = Re(ψ_u* ψ_v)`, `J_{u→v} = 2 Im(ψ_u* ψ_v)`.
- Energy `E_ψ = <ψ|H|ψ> = -2 Σ_edges B` (`continuum.energy_both_ways`).

## 2. Epistemic firewall (ZERO-0Z)

ZERO-0 may claim at most Z1–Z4 (if earned):

- Z1: `ψ = 0` is regular in Cartesian variables.
- Z2: phase is undefined at `ψ = 0`.
- Z3: incident `B = J = 0` at an exact zero.
- Z4: some phase-organizational changes may require zero crossing.

Forbidden words for a zero event: particle, matter, defect, black hole,
source, geometry change, vacuum, physical singularity.

## 3. Independence from VAC-FIELD-0

Headline analysis consumes NO VAC-FIELD-0 verdict. Background families
are experimental preparations, not vacuum declarations:

- Z0: no background (bare excitations on the all-zero reference).
- Z+: uniform nonzero coherent background `a·1/sqrt(N)`.
- Zπ: staggered background `a·(-1)^q/sqrt(N)` (bipartite substrates).
- Z−: sheet-antisymmetric background (J2 only: `+1` on b=0, `−1` on b=1,
  normalized).

## 4. Frozen numerical thresholds

| Symbol | Value | Role |
|---|---|---|
| `EPS_SCREEN` | 1e-8 (absolute, normalized states) | Level-1 zero candidate |
| `EPS_CERT` | 1e-10 | Level-3 modal-certification residual |
| `EPS_MINIT` | 1e-3 (absolute) | ZERO-0G initial exclusion: no node starts below |
| `EIG_TOL` | 1e-12 | eigenvector nodal-zero tolerance (ZERO-0D) |
| `DT_HEAD` | 0.02 | headline trace step (Krylov-exact steps) |
| `T_HEAD` | 40.0 | headline horizon (2000 steps) |
| `DT_FINE` | 0.002 | refinement step around candidates |
| `NORM_TOL` | 1e-9 | C0 norm conservation |

All thresholds live as module constants in `zero.py` and are pinned by tests.

## 5. Certification hierarchy (ZERO-0H, frozen)

- Level 1 (candidate): union of amplitude screening
  (`|ψ_u(t_k)| < EPS_SCREEN`) and segment-bracket screening (origin
  distance to the complex segment `[ψ(t_k), ψ(t_{k+1})] < EPS_SCREEN`),
  deduped per node (amendment: segment screening added before any
  campaign run because pure amplitude screening misses crossings
  between grid points; both legs are deterministic functions of the
  trace).
- Level 2 (refined): two-round zoom re-evolution (windows ±0.2 then
  ±0.01, steps `DT_FINE` then `DT_FINE`/20), parabolic `t*`, and
  `amp_min` evaluated by exact evolution AT `t*` (never the parabolic
  value, since `|ψ|` has a V-cusp at transverse zeros). Non-modal
  label: `near-zero` iff `amp_min < EPS_NEAR = 1e-3` (frozen
  grid-scale floor: a true zero and a sub-1e-3 ordinary minimum are
  indistinguishable without a Level-3 leg — this is WHY Level 3
  exists), else `ordinary`.
  Amendment (before verdict, after pilot): Level-2 refinement is
  capped at `REFINE_CAP = 60` candidates per trace in deterministic
  (node, t) order; the remainder is filed as `refine_overflow`.
  Level-1 screening stays exhaustive, so candidate counts and `m(t)`
  statistics are unaffected; only per-event L2/L3 labels are capped.
  (Uncapped refinement proved infeasible on large-graph cells with
  dense near-zero brackets: >80 CPU-min single tasks.)
- Level 3 (certified): small graphs only (N ≤ 200), dense modal
  reconstruction `ψ_u(t) = Σ_n z_n e^{-iE_n t}` with a simultaneous
  `(r_u, s_u)` root solve; certified iff residual `< EPS_CERT`.
  Labels: `exact` (analytic: two-mode match / eigenvector node /
  symmetry identity), `symmetry-exact`, `certified-modal`,
  `near-zero` (Level-2 minimum, uncertified), `ordinary` otherwise.

Floating-point underflow is NEVER reported as exact.

## 6. State families (ZERO-0G, frozen seeds)

- F1 broad random complex (`conservation.field_random`), seeds 0..39.
- F2 equal-amplitude random phases, seeds 0..39.
- F3 smooth phase field: uniform envelope × `exp(i φ)`, φ a low-order
  Fourier field (3×3 modes, seeded), seeds 0..19.
- F4 low-mode superposition: 2–4 lowest nonzero eigenmodes, seeded
  coefficients, seeds 0..19.
- F5 broad spectral superposition: all-mode random coefficients,
  seeds 0..19.

Every initial state is normalized and checked against `EPS_MINIT`
(resample with seed+1000 on violation, at most 10 tries, then file).

## 7. Substrate battery (ZERO-0V, frozen)

| Tag | Builder | Sizes |
|---|---|---|
| j2 | `formation.j2_torus_graph` | L ∈ {6, 10, 20} (N = 72, 200, 800) |
| storus | `graphs.build_torus_grid` | L ∈ {8, 16, 28} |
| ring | `nx.cycle_graph` | N ∈ {64, 256, 1024} |
| j2quot | `vac0.quotient_j2` (read-only) | L ∈ {8, 16} |
| rewire | `graphs.build_short_rewired_grid` (span-2, seed 0) | L ∈ {16, 28} |

ZERO-0W size scaling reuses these columns (ring to N=1024, J2 to L=20
headline; L=28 J2 only if budget allows).

## 8. Packet batteries (ZERO-0I/J/K, frozen)

- P1 packets: `ballistic.gaussian_packet`, σ ∈ {2.0, 4.0},
  k ∈ {(π/2,0), (π/2,π/2), (0,π/2)} and negatives, J2 + storus.
- POT states: `potential` null-ensemble / gradient-family controls
  where they type-check on the substrate (filed if N/A).
- Collisions (ZERO-0J): head-on, co-propagating, orthogonal, oblique,
  near-miss; relative phase sweep Δφ ∈ {kπ/4}, matched + mismatched
  amplitudes (ZERO-0K law validation).

## 9. Background sweep (ZERO-0L/M, frozen)

- `a` over {0, 1e-3, 1e-2, 0.1, 0.3, 1.0, 3.0, 10.0} × scale set by
  normalization after assembly (both fixed-absolute-η and
  fixed-fractional-εη protocols).
- η: F1/F5 draws, 10 seeds each.
- Bound (ZERO-0M): triangle-inequality certificate
  `|δψ_u(t)| < |a ψ_bg,u(t)| ∀u,t` evaluated on the trace grid;
  reported as sufficient-condition flag, never as observed claim.

## 10. Winding readout (ZERO-0P/Q, frozen)

- Cycle winding: sum of principal relative phases around an ordered
  cycle, defined ONLY if every node on the cycle is nonzero
  (`|ψ| > 10·EPS_SCREEN` at every sample); result rounded to nearest
  integer with residual filed.
- Test cycles: J2 plaquettes (sheet-resolved 4-cycles + 8-node
  bilayer rings), storus plaquettes, full rings.
- Winding-change verdict requires the cycle to be defined on both
  sides of the change window; association with a zero event requires
  a Level-2+ event on the cycle support within ±0.5 time units.

## 11. Controls (frozen)

- C0 norm conservation on every trace (`NORM_TOL`).
- C1 banked P1/POT/EM regression = copied suites stay green.
- C2 analytic two-mode zero times recovered to 1e-9.
- C3 nodal eigenstates remain zero to `EIG_TOL` under evolution.
- C4 protected cases (ZERO-0M bound active) never screen positive.
- C5 global phase `e^{iα}` invariance of zero locations/times.
- C6 global scaling `aψ` invariance of exact-zero verdicts.

## 12. Campaign layout (beast)

- Run dir `~/zero0-ee5c` (repo checkout), venv `~/zero0-venv`,
  data dir `~/zero0-data`.
- `scripts/zero0_campaign.py`: single-task CLI
  (`--task KIND --substrate ... --family ... --seed ... --out ...`),
  one JSON row per task; task files under `/tmp/zero0-tasks/`;
  execution via `xargs -P 48`.
- `scripts/analyze_zero0.py`: ledger aggregation → verdict tables
  (no re-running of physics).

## 13. Verdict criteria (frozen)

The campaign earns per-cell verdicts (substrate × family × background):
certified-zero rate, near-zero rate, transverse-vs-persistent split,
winding-change counts with/without associated zeros, background
suppression curves P(a). Cross-cell claims (graph-generic vs
spectral-class vs J2-specific) require ≥2 substrates per class.
