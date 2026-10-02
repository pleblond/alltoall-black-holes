# GRAV-0 — Local Fabric-Disturbance Propagation: Preregistration

**Status:** FROZEN 2026-10-02 (design). Calibration values (§8) filled
2026-10-__ post-calibration, pre-campaign. Main campaign after.
**Branch:** `cursor/grav0-fabric-propagation-31cf`. **Module:**
`src/bh_graph/grav0.py`. **Tests:** `tests/test_grav0.py`.
**Runner:** `scripts/run_grav0.py`. **Results:** `docs/grav0-results.md`.
**Calibration:** 2026-10-02 (T=20 per rule below; θ=0.001 leakage check
pending on beast pre-campaign).

## Amendment A1 (2026-10-02, pre-campaign, calibration-driven)

U0×P2 calibration (L=42, 4 seeds, T=50) shows the ripple transient
lives at t < 5 sweeps (footprint erased by t=5, all shells ≈0±SEM
after; mass pure noise): the prereg snapshot grid (every 5 ticks)
cannot resolve it. Cause: dense sweeps (N proposals/tick, ball(4)
touch) give a fast (lightcone-limited) divergence front; front shape
vs proposal-count is dynamics-intrinsic, so the fix is FINER SAMPLING,
not relabeling. Changes (dynamics/perts/θ/observables untouched):

- **A1.1 snapshot schedule** (replaces every-5-ticks): every N/20
  proposals over the first 4 sweeps (80 snaps), every sweep to t=30,
  every 5 to t=200. Keys in sweeps (float). Rationale: resolve the
  sub-5-sweep transient with ~100 points.
- **A1.2 L=64 extension**: U0/U4 × P2/P4 × 16 seeds (front headroom,
  r ≤ 32); main grid unchanged (L ∈ {20,28,42} all cells).
- **A1.3 θ rule**: θ=0.001 KEPT as a significance floor. The
  leakage-raises-θ rule is DROPPED (invalid under exact coupling:
  far-field signal is genuine causal arrival, and the null is
  exact-zero, not statistical). Null check instead: U1/U2 far-field
  must be ≡0 (frozen ⇒ no divergence; violation ⇒ coupling bug,
  stop and investigate). θ-band robustness {0.0005, 0.002} kept.
- **A1.4 verdict inputs**: (r_front(t), peak amplitude A(t),
  r_peak(t), width²(t), mass M(t)) + fits. Added class:
  TRANSIENT-DISSIPATIVE (support expands then amplitude < θ
  everywhere; report r_max, t_rise, t_fade; L-scaling decides
  bounded vs unbounded). FROZEN restated: total accepts < 20 over
  200 ticks AND r_front pinned (a handful of local repairs ≠
  carrier; U1×P2 cal showed 1 accept/50 ticks, support still r≤4).

## 0. Question

Can information about a local structural disturbance propagate
arbitrarily far through local vacuum dynamics on J₂? GRAV-0 does NOT
test Newtonian attraction or GR. Verdicts: DEAD / DIFFUSIVE /
BALLISTIC / NO CARRIER (§7), per (perturbation, dynamics) cell.

## 1. Substrate

Periodic J₂ torus `formation.j2_torus_graph(L)` (8-regular, 2L² nodes,
vertex-transitive). L ∈ {20, 28, 42} (N = 800/1568/3528).
Pristine span signature (measured, frozen): every edge spans exactly 3
at radius 3 → `smax = 3`, same calibration as the square grid (no new
knob). Torus shells are exactly 8r for r ≤ L/2 (measured L = 28/42);
analysis range r ≤ L/2 (pre-wrap). Source at node 0 (any node
equivalent by vertex-transitivity). Distances d(i,S) are BFS on the
FROZEN pristine graph (analysis-only, never consulted by dynamics).

## 2. Perturbations (each applied ONCE at t=0, then no intervention)

All within ball(2) of node 0 (local by construction):

- **P1 swap1**: one degree-preserving double-edge swap, both edges
  inside ball(2). Minimal impulse; E- and degree-conserving.
- **P2 burst10**: ten such local swaps (sequential, seeded). One
  detectable-scale motif-deformation event; E-/degree-conserving.
- **P3 reloc1**: one local relocation: remove edge (0, v) (v = seeded
  neighbor slot), add seeded non-edge with both endpoints in ball(2).
  Coordination defect (±1); E-conserving.
- **P4 hole4**: delete the 4 edges of one local C4 through node 0
  (seeded choice among C4s). Cavity; E−4, coordination defect.

Calibration cell (NONLOCAL label, not main): **Pc-u5**, five
degree-preserving swaps with uniform (global) partners — the only
perturbation the span channel can see. Tests carry-given-vision for
U1; never counted toward the locality verdict.

## 3. Dynamics (all STRICTLY LOCAL, observer-blind)

Proposal = canonical-slot draws with FIXED rng consumption per
proposal (exact paired coupling, §5). Graph consulted only for
slot-mapping, validity, and evaluation inside ball(R_prop) of the
touched nodes. Frozen: **R_prop = 4** (partner edge reached by
≤3-step slot-walk from the primary edge; every touched node within
ball(4)). One tick = N proposal attempts. NO connectivity guard
(a local rule cannot check a global predicate; runs that disconnect
are flagged in output and excluded from front fits — count reported).

- **U0 swap-drift**: accept every valid local swap. Lineage: D1
  `rule_scramble` made strictly local (negative-control class).
  Diffusion baseline; always acts.
- **U1 guillotine-local**: accept iff a touched edge is long
  (span > 3, radius 3) and both new edges are short. Lineage: D1
  `rule_guillotine` with global-uniform partner sampling REPLACED by
  slot-walk local partners (globality removed, never added).
  Prediction: frozen on P1–P4 (span-blind, §9).
- **U2 square-greedy-local**: accept iff touched-4-cycle count
  strictly increases. Lineage: blind-U `rule_square`, local partners.
  Prediction: frozen everywhere (pristine J₂ is a strict local
  C4 maximum — every local swap destroys 22–42 touched squares).
- **U3 square-Metropolis-local**: accept iff connected-local…
  (no connectivity check — see above) with P = min(1, e^{ΔC4/T}).
  Lineage: blind-U `rule_square_metropolis`, local partners.
  T set by calibration rule §8 (acts but does not instantly melt).
- **U4 reloc-drift**: accept every valid local relocation (loser edge
  at slot-walk ball, gainer non-edge with both endpoints in
  ball(R_prop)). Lineage: formation driver d1 (ungated null),
  localized. Diffusion baseline with mobile degree-defects.

Excluded with reason: census-gated rules (`rule_anneal`,
`rule_triple_anneal`, `rule_pair_anneal`, gated `rule_quad`) — global
census acceptance is nonlocal coordination; twin-targeted greedy —
global target; kappa rules — frozen on grids + Johnson-per-step cost;
triangle rules / d5inf — anti-vacuum direction on triangle-free J₂;
pair/triple/slide — act only on longs (span-blind ⇒ frozen, same
verdict as U1 by construction, no new information).

## 4. Observables (frozen; observation-only)

- **Primary δg_i(t)**: ball(R_obs=2) edge-symmetric-difference vs the
  frozen pristine graph:
  δg_i = |E(ball₂(i)) Δ E'(ball₂(i))| / |E_pristine(ball₂(i))|,
  balls from pristine BFS. Sees every local move by construction.
- **Secondaries** (same shells): incident (R=1) adjacency deviation;
  span-excess (fraction of incident edges with span > 3);
  |deg − 8|; touched-C4 deviation |C4(S_i) − C4_pristine|.
- **D(r,t)** = shell mean of δg at pristine distance r from node 0
  (primary object; full surface recorded, snapshots every 5 ticks +
  t=0, r ≤ L/2).
- **Paired ripple ΔD(r,t)** = D_pert − D_ctrl, same seed (§5). The
  front object (kills uniform heating background exactly in
  expectation, exactly far-field pre-arrival).
- **r_front(t)** = max r with ΔD̄(r,t) > θ (mean over seeds),
  θ = 0.001 (frozen; robustness band {0.0005, 0.002} must not change
  any cell verdict). **r_mass(t)** = ΔD-weighted median radius
  (θ-free secondary; reported alongside).

## 5. Paired design (common random numbers — variance reduction only)

Each (P, U, L, seed) runs TWICE: perturbed and control (pristine
start), identical seed and identical canonical-slot rng streams.
Marginals are ordinary local-dynamics trajectories; coupling affects
only noise (E[ΔD] unbiased). Far-field agreement is EXACT until causal
chains arrive (verified by test: ≤5 proposals ⇒ far field ≡ 0).
Seeds: 12 per cell (0..11), L ∈ {20, 28, 42} ⇒ 72 trajectories/cell.

## 6. Campaign

- **T = 200 ticks**/trajectory all cells. Snapshots every 5 ticks.
- **Adaptive extension (preregistered)**: cells with r_front(200) in
  (footprint, L/2 − 2) AND rising extend to T = 600 on L = 42 only
  (same seeds). Cells at wrap flag WRAPPED (need bigger L; verdict
  provisional).
- **Calibration (pre-campaign)**: (a) U3 temperature by rule §8;
  (b) coupling/leakage check: U1×P2 far-field |ΔD| ≡ 0 (frozen ⇒
  exact null); U0 far-field leakage histogram ≪ θ at all t;
  (c) disconnect count (expect 0; U4 relocation monitored).
- **Compute**: beast EC2 (96 CPU), one process per trajectory.

## 7. Verdicts (per cell; θ-robustness required)

- **FROZEN**: 0 accepts in ≥11/12 seeds (dynamics never acts) ⇒
  **NO CARRIER** for that channel at that scale.
- **DEAD**: acts, but r_front(t) ≤ footprint + 2 for all t (heals or
  pins in place).
- **DIFFUSIVE**: r²_front(t) linear in t (fit r² = 2D_eff·t + c on the
  rising window; R² > 0.9 required) with r_max growing under
  finite-size scaling (L = 20/28/42: r_max(L) increasing ⇒ consistent
  with unbounded propagation in the thermodynamic limit; saturating ⇒
  bounded).
- **BALLISTIC**: r_front(t) linear in t (R² > 0.9) with v < R_prop +
  R_eval per tick (causality bound respected; violation ⇒ nonlocality
  leak ⇒ INVALID, investigate).
- **MIXED/TRANSIENT**: rising then receding below θ (mixing erases
  memory): report r_max, t_rise, t_fall; L-scaling decides bounded vs
  unbounded.
- **NO CARRIER (global)**: no (P, U) main cell shows r_front beyond
  footprint + 2 at any t. (Does NOT license inventing a carrier.)

## 8. Calibration rules (procedure frozen; values filled pre-campaign)

- **U3 temperature**: smallest T ∈ {5, 10, 20, 40, 80} with pristine
  per-proposal accept rate in [0.05, 0.5], measured L = 28, 2000
  proposals, seeds 0–3 pooled. Pilot (uncoupled scan): T=10 → 0.025,
  T=20 → 0.15 ⇒ expect T = 20. FILLED: T = 20 (formal calibration
  L=28, 2000 proposals × seeds 0–3: T=5 → 0.0006, T=10 → 0.0238,
  T=20 → 0.1371, T=40 → 0.3509, T=80 → 0.4989; smallest in
  [0.05, 0.5] is T=20).
- **θ leakage check**: U0×P2, L = 42, seeds 0–3: max far-field
  (r > 12, t ≤ 50) |ΔD| must be < θ/3 = 0.00033, else raise θ per
  rule θ = 3 × measured leakage (rounded up to {0.001, 0.002,
  0.005}) and re-freeze before campaign. FILLED: θ = ___.

## 9. Pre-filed pilot facts (motivate, do not replace, the campaign)

- Pristine J₂ torus: all edges span exactly 3 (radius 3); 0 longs.
  J₂ is a fixed point of the (unmodified) guillotine.
- Span-blindness: 1 uniform swap → 0–2 longs (lottery); 5–40 LOCAL
  swaps → 0–2 longs; hole4/star8/1-del → 0 longs. Only nonlocal
  (long-range) edges read as long. ⇒ U1 predicted frozen on P1–P4.
- C4-maximality: all 400/400 probed local swaps on pristine AND
  damaged J₂ strictly decrease touched C4 (δ ∈ [−42, −22]).
  ⇒ U2 predicted frozen everywhere.
- Footprints (R=2 adjacency, L=16): P1 ≤ 0.028 (r ≤ 4), P2 ≤ 0.25
  (r ≤ 4), P4 ≤ 0.028 (r ≤ 3) — all ≫ θ = 0.001 at every footprint
  shell (t=0 front is θ-band-stable).
- Uncoupled pilot (U0×P2, L=16): background heating saturates to
  O(1); uncoupled differencing noise O(0.03) everywhere ⇒ coupling
  load-bearing (§5).

## 10. Anti-smuggling ledger

- Dynamics never see: pristine graph, distance-to-source, shells,
  D(r,t), θ, or any global scalar. (Tests assert: proposal functions
  take only (state, slots, T); no pristine/distance arguments.)
- Distance/shells/θ used ONLY in analysis (§4).
- U1/U2/U3 are existing rules with globality REMOVED (local partners
  replace global sampling) — locality strictly increased, which can
  only hurt propagation. No rule was given a propagation-favoring
  term.
- Perturbations are single local events (§2); Pc-u5 is labeled
  NONLOCAL and excluded from verdicts.
- GRAV-1 (source→detector coupling K_A → δG → K_B) is OUT OF SCOPE:
  no matter-response law exists in the model; GRAV-0 delivers the
  propagator kernel ΔD(r,t) it would need. Filed, not attempted.
