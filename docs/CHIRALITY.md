# P3: emergent handedness/chirality (parallel, K+psi)

Parallel campaign forked from `cursor/formation-design-2031` / PR #62 tail
(formation D5inf + spontaneous localization, BEFORE any wave-sector
machinery). D14 sections in `docs/DEFERRED.md` are FROZEN (no edits except
this pointer). PR #63 / D15 is READ-ONLY apparatus until the one-way
convergence gate fires (below). This file is the P3 ledger (preregs +
verdicts). Sibling tracks P1 (ballisticity) and P2 (polarity, PR #64) share
the base only; no cross-branch imports (duplication-with-pointer precedent
if apparatus must be shared before merge).

Charter (locked):

- Arena: the CONVERGED OBJECT K+psi (formation blob K coupled to a wave
  sector psi), NOT formation alone. Stage-0 NULL (D5inf-plateau-achiral,
  0/6 persistent circulation) closed the debt-free pure-formation route;
  P3 does not rerun it. P-track P0 NULL (no intrinsic type degeneracy)
  further motivates the wave sector: psi must provide the rest.
- Hard rule: NO HANDEDNESS IN THE LAW. The coupled law (D5inf + psi
  sector + coupling) must satisfy R U R^-1 = U for an explicit reflection
  R, with H real-symmetric (time-reversal symmetric) and blind proposals.
  Any L/R asymmetry must be spontaneous: <H> ~= 0, <|H|> > 0 across runs,
  H(t) ~= +-H0 within a run. P3.0 pins the symmetry before any search.
- Order: (0) symmetry/null apparatus R + psi + W; (1) stable winding
  sectors on frozen blobs (P3-A); (2) spontaneity from unprepared psi
  (P3-B, queued); (3) persistence under churn (P3-C, queued); (4) mirror
  experiment K_R = R K_L with matched scalars (P3.3-full, queued);
  (5) L+L/R+R/L+R interactions (P3.4, queued). Do not skip rungs.
- Strong result: K_L, K_R with E_L = E_R, m_L = m_R, tau_L ~= tau_R,
  W_R = -W_L, neither handedness supplied. Polarity (P2) and ballisticity
  (P1) are SEPARATE claims (P1 != P2 != P3); P3 needs no head-tail arrow
  and no directed motion.
- Negative control: CIRCULATION-SIGN-ON-FORMATION IS NOT P3. Stage-0
  killed it (0/6). P3's signed quantity comes from the wave sector's
  independently existing phase (winding W), not graph-edge churn.
- Ladder: winding sectors exist < persist under churn < survive
  perturbations/constituent-change < back-react self-consistently
  (psi->K, queued P3-D) < interactions depend on relative handedness.
  P3-A/B/C are ONE-WAY coupled (K->psi, test wave); back-reaction is a
  filed debt, not smuggled in.
- D15 convergence gate (one-way, only if P3 independently produces it):
  derived localized dynamics with operator J satisfying J^2 = -I,
  J^T G J = G, [U,J] = 0 (same bar as P-track charter). A bare L/R pair
  W = +-1 is chirality phenomenology but NOT emergent complex structure.
  Gate fires only on J; otherwise D15 stays closed and P3 stands alone.
  If persistent K_L/K_R with momentum-dependent internal travel emerge,
  a followup (P3-D15, queued, own prereg) runs the FROZEN D15 detector
  (two unit-modulus bands? k-dependent eigenvectors? spin-momentum
  locking?) on coarse-grained K_L/K_R psi-dynamics. Neither track is
  modified to force convergence.
- Starting kit (earned, formation branch): real graph state machine,
  D5inf dynamics, finite kmax ~= 4 structural scale, localized
  spontaneously selected cores (mobile/trackable: sitters + diffusive
  wanderers), exchange/churn dynamics, no global orientation, no sheet
  preference. No C, no Weyl, no chirality imported in the law.
- Inheritance (filed): D5inf-plateau-achiral (Stage-0 NULL 0/6);
  single-sponge + dust (count-vs-N: steps 4-5 need prepared initials,
  flagged states-not-rules); J2-orientation (c) ISOTROPIC (Aut(J2)
  survey: translations broken only); SSB-1 SPONTANEOUS (location
  degeneracy shown). J2-torus readout-basis justification stands
  (coords for preparation/readout basis only, observable intrinsic).

## Wave sector psi (C0-merge, minimal, locked for P3-A)

State: complex psi : V -> C, normalized sum|psi|^2 = 1, numpy complex128
aligned to sorted nodelist (deterministic). Hamiltonian: H(G) = -A
(negated adjacency, real symmetric, parameter-free given G, hopping-only,
no on-site terms). Units J = 1. Evolution: psi(t+dt) = exp(-iH dt) psi(t)
via scipy expm_multiply (unitary, deterministic given (G, psi0, t-grid)).

- H-gate: H real symmetric ==> [H,K] = 0 (K = complex conjugation,
  time-reversal-symmetric law); no complex phases in the law; proposals
  blind (D5inf unchanged). R-covariance pinned (P3.0).
- Coupling (one-way, P3-A): K->psi. psi evolves under H(G(t)) with G(t)
  the formation trajectory. Frozen-frame stepping for churn runs:
  piecewise-constant H per sweep-frame (exact unitary per frame,
  first-order in frame time; norm pinned to 1e-10). Static-graph runs
  (P3-A primary) use H(G_frozen).
- Back-reaction psi->K: ABSENT in P3-A/B/C (queued P3-D). Filed openly:
  rung-1 chirality belongs to (blob geometry + linear test wave), not yet
  a self-consistent particle.
- Time-unit assumption (labeled, filed): formation sweeps and
  Schrodinger-t have no derived relation; churn stepping uses dt = 1 per
  sweep. P1 may derive it; P3 does not tune it.

## Reflection R (locked)

J2-torus R_x: (x,y,b) -> (L-x mod L, y, b) as a node permutation
(`chirality.reflect_j2_x`). Claim: R_x in Aut(j2_torus_graph) (edge-set
invariant), involution, H-covariant (H[R(u)R(v)] = H[uv]). Pinned on L=4
(P3.0). Pushforward (R_*psi)(Rv) = psi(v). Observable flip:
W(R_*psi) = -W(psi) for ANY psi (pure covariance, pinned with seed-fixed
random psi). Conjugation C: psi -> psi* flips W exactly (time-reversal
mirror, needs no coords; used for E/H matching checks). Law symmetry:
exp(-iH(RG)t) R_* = R_* exp(-iH(G)t) (pinned exactly); i.e. the mirror
experiment (K_R = R K_L run under the identical law) is well-defined with
both runs on the same substrate. D5inf proposal equivariance holds in
distribution (blind uniform edge/non-edge + seeded rng); P3.3-full tests
it via tau_L ~= tau_R (the mirror experiment itself), not bit-identical
trajectories.

## Chirality observable W (primary, locked)

Discrete vorticity (intrinsic, Aut-covariant, no coords). Bond phase
(directed u->v): phi_uv = arg(psi_v conj(psi_u)) in (-pi, pi]
(antisymmetric). Face circulation for triangle (a,b,c) with canonical
orientation a<b<c: c_D = (phi_ab + phi_bc + phi_ca)/2pi. Region
vorticity: W(S) = sum over triangles fully inside S of c_D (Stokes:
equals boundary-loop winding; integer-valued when all bonds healthy, up
to fp error -- pinned |W-round(W)| < 1e-9 on synthetics).

- Region S (intrinsic): S_r = {v : dist_G(v, core) <= r}, r = 2 PRIMARY
  (W2), r = 1/3 robustness (W1/W3, filed). Core = floored k4-truss node
  set (SSB-1/J2 precedent: floor = max(2, N//100); re-implemented here,
  duplication-with-pointer, no cross-branch import).
- Amplitude floor: bonds with min(|psi_u|,|psi_v|) < eps*max|psi| are
  EXCLUDED (phase meaningless near zeros); triangles with any excluded
  bond excluded. eps = 1e-6 (relative, pre-registered). Exclusion breaks
  exact quantization (open paths) ==> always report exclusion fraction
  alongside W.
- Health (pre-registered exclusion rule, not shopping): a run is HEALTHY
  iff exclusion < 5% of triangles in S AND |W - round(W)| < 0.1 at t=0.
  UNHEALTHY runs are excluded and replaced (P3-A replacement rule below);
  if >2 blobs unhealthy ==> STOP, file apparatus failure (P3.0
  invalidated ==> amend, never shop).
- Why face-sum, not boundary loop: loop-finding around a core needs
  coords or fragile cycle search; face-sum gets Stokes for free and stays
  intrinsic. Preparation may use the J2 readout basis (filed
  justification); the observable never does.

## Planted initials (locked for P3-A)

psi_m(v) = rho(v) exp(i m theta(v)) / norm, m in {-1, 0, +1}:

- Envelope rho(v) = exp(-d(v,core)^2/2sigma^2), d = graph distance (BFS
  from core set, deterministic), sigma = 6 hops (pre-registered constant,
  ~ blob scale; labeled choice).
- Angle theta(v) = atan2(dy, dx) of the minimal-torus-displacement of v
  from the core circular-mean centroid in J2 readout coords (Stage-0
  centroid precedent; J2 readout-basis justification filed). Antipodal-cut
  caveat filed: the cut sits far from the core (amplitude-suppressed);
  primary S2 never touches it.
- Controls share the SAME rho (isolate phase pattern): m=0 (uniform
  phase) + 2 random-phase draws (iid uniform phases, seed = 5100 +
  10*blob + rep, rep in {0,1}).
- Mirror relation: psi_{-m} = conj(psi_{+m}) ==> E matched exactly for
  real H (pinned); W matched-opposite (pinned on synthetics, verified on
  campaign graphs at t=0 in P3.0).
- Lattice-vortex note (filed, not assumed): planted twists have no
  amplitude zero (rho > 0 on support); W = m is the U(1)-winding of the
  loop map, well-defined since |psi| > 0 on loops; it can unwind only via
  phase-slips (amplitude zeros). W persistence = absence of phase-slips.
  Whether linear tight-binding holds twists is MEASURED (P3-A), and NULL
  (transient winding) is an informative verdict pointing at nonlinearity.

## P3.0 — symmetry/null apparatus (prereg, FROZEN-2026-10-01 ~18:35 UTC)

Claim: the apparatus (R, H, evolution, W, planting) is correct and
handedness-free BEFORE any search. Positive = apparatus valid (not
discovery). Pins in tests/test_chirality.py (all fast synthetics):

1. R involution + automorphism of j2_torus_graph(4) (edge-set invariant).
2. H build: real symmetric, H=-A exact on K4 + path graph.
3. H R-covariance on J2 L4 (H[R(u)R(v)] = H[uv]).
4. Evolution: norm + energy conserved (wheel-12, T=20); expm_multiply vs
   dense expm agreement to 1e-12; determinism (same seed bit-identical).
5. Bond-phase antisymmetry; triangle-circulation telescoping.
6. Wheel-12 planted m=+1/-1/0 read W=+1/-1/0 within 1e-9, exclusion 0.
7. Conjugation flips W exactly (W(psi*) = -W(psi) to 1e-9).
8. R pushforward flips W for seed-fixed random psi on J2-L4 (exact).
9. E(psi*) = E(psi) exactly (real H).
10. Triangle enumeration deterministic + counts (K5: 10).
11. Region S BFS deterministic; envelope/planting deterministic.
12. tau_W unit test on synthetic traces (first-sustained-drop logic).
13. is_valid_* boolean checks (no-raise discipline for routine flow).
14. Planted mirror pair on synthetic: E equal, W opposite, same exclusion.
15. Law symmetry: exp(-iH(RG)t)R_* = R_*exp(-iH(G)t) on J2-L4 (to 1e-12).

Campaign-graph checks (2 pilot blobs = P3-A blobs 0-1, FORMATION ONLY +
t=0 planting, NO evolution -- conservation is pinned on synthetics (pin 4),
keeping all P3-A evolution traces fully blind until P3-A analysis):

- 2/2 planted m=+-1 read W=+-1 within 0.25 with exclusion < 5% (healthy).
- m=0 reads |W| < 0.25. Conjugation/mirror flips hold at t=0 on both.
- Random-phase t=0 W2 values filed (baseline for P3-A tau rule).

P3.0-POSITIVE <==> all pins pass + all campaign-graph checks pass.
Else file apparatus failure and AMEND (P3-A gated on P3.0-positive).

## P3-A — winding persistence on frozen blobs (prereg, FROZEN-2026-10-01 ~18:35 UTC)

Question: do planted phase twists (m = +-1) persist as integer winding
sectors on frozen D5inf plateau blobs under linear tight-binding, with
stable sign -- vs random-phase/m=0 controls?

Formation (locked): soup = j2_torus_graph(28) (N=1568, deterministic),
driver d5inf, thr=4 (unused by d5inf, precedent value), dyn seeds d0-d7
(8 blobs), t_max=2000, return_state. Freeze = FINAL state, REQUIRE
sweeps >= 1500 (plateau/in-plateau; file stop+sweeps per run). Violation
==> run EXCLUDED, replaced by next dyn seed (d8, d9, ...) in order
(pre-registered replacement; replacements filed, capped: >2 replacements
==> STOP + file formation anomaly, do not shop).

Per blob (locked): core (floored k4, floor=max(2,1568//100)=15); if core
empty ==> run EXCLUDED + replaced (same rule; not expected for D5inf
plateau). 5 initials (shared rho): m in {-1,0,+1} + 2 random-phase.
Planting-health gate per blob (all 5 initials must be healthy at t=0 per
P3.0 rule; unhealthy ==> exclude blob + replace seed; >2 unhealthy blobs
==> STOP + file apparatus failure).

Evolution (locked): H = -A(G_frozen); T = 200, samples every dt = 2 (101
samples, expm_multiply per step); record W2 (+W1/W3), exclusion fraction,
E = <psi|H|psi>, IPR = sum|psi|^4, psi snapshots at t = 0/100/200 (filed,
not verdict-weighted).

tau_W (locked): first t_k with |W2| < 0.5 for 5 CONSECUTIVE samples; never
==> tau = >200 (censored, filed as >200). Sign-stability (locked): for
planted m=+-1, sign(W2_k) = m at every sample with |W2_k| >= 0.5 before
tau (any large-opposite-sign sample ==> stability FAIL, file flip time).
For random controls the same tau rule with any-sign persistence.

PRIMARY verdict (locked): P3-A-POSITIVE <==> (a) >= 6/16 planted-|m|=1
runs show tau_W > 50 with stable sign, AND (b) <= 2/16 random-phase runs
show tau_W > 50 (contrast: rules out everything-persists triviality).
Else NULL (file "linear-test-wave winding transient on frozen blobs";
implication: rung-1 linear chirality excluded ==> nonlinearity (P3-D
coupling and/or self-consistent psi->K) becomes the live followup, NOT
assumed into existence).

Mirror-lite (locked, descriptive + one exact check): per blob, tau_{+1}
vs tau_{-1} (filed pair table; P3.3-full does the statistical tau_L~tau_R
test); E_{+1} = E_{-1} exactly (pinned apparatus + verified per blob);
W_{+1}(0) = -W_{-1}(0) within 0.05 (verified per blob).

Secondaries (descriptive ONLY, filed full): W(t) traces; exclusion(t);
E per run (confound check: tau vs E); IPR(t) (wave localization vs blob);
W1/W3 robustness; m=0 max|W| excursion (spontaneous-pair watch, P3-B
input, no verdict weight).

S-churn pilot (locked scope, descriptive, NO verdict weight): 2 blobs
(P3-A blobs 0-1) x m=+1, co-evolved live formation 1500 -> 1700 sweeps
from the frozen frame (continue formation_run trajectory? NO -- fresh
formation_run from frozen state with new preregistered seeds 9100/9101,
dt = 1/sweep labeled choice, per-sweep H rebuild + psi step, triangle
re-enumeration per sweep). Report W2(t) + exclusion(t) + E(t). Purpose:
scope P3-C design (churn-timescale vs winding-timescale), not evidence.

Campaign discipline: prereg commit predates runs; pins commit predates
analysis; verdict filed here whatever the outcome; full traces + seeds in
ledger appendix for audit. Formation trajectories are FRESH (P0 precedent:
no T-match needed). Suite stays green (parallel xdist on beast).

## Queued (sketches, NOT frozen, gated on P3-A verdict)

- P3-B (spontaneity): random-phase psi ensembles per blob (many draws);
  P(W>0) ~= P(W<0)? <W> ~= 0, <|W|> > 0 at late t? Requires P3-A-positive
  (sectors must exist before asking if they self-populate). If P3-A NULL,
  P3-B is redesigned around nonlinear psi (P3-D first).
- P3-C (churn persistence): full co-evolution campaign (winding under
  live K churn; nodes/edges change but W remains?); time-unit assumption
  revisited with S-churn pilot data; own prereg.
- P3.3-full (mirror experiment): K_R = R K_L reflected-blob runs under
  identical law; matched scalars E/m/tau + flipped W; tau_L ~= tau_R
  statistical test (law-symmetry check: systematic tau_L != tau_R would
  indict the law itself). Gated on persistent sectors (P3-A/C).
- P3.4 (interactions): prepared two-blob L+L/R+R/L+R initials (needs the
  non-interference review flagged in count-vs-N: states-not-rules,
  scattering methodology); sigma_LL = sigma_RR by mirror symmetry?;
  sigma_LR != sigma_LL? Gated on P3.3-full.
- P3-D (back-reaction): psi->K coupling designs (psi-weighted relocation
  proposals? |psi|^2-modulated acceptance?); self-consistency rung;
  separate prereg with its own H-gate proof (coupling must preserve
  R-symmetry: pinned R-covariance of the coupled update).
- P3-D15 (gate run): if K_L/K_R persist with momentum-dependent internal
  travel, run the frozen D15 detector on coarse-grained psi-dynamics;
  fires only on J (J^2=-I, J^T G J=G, [U,J]=0). Own prereg. D15 untouched
  until then.

## Verdicts (append below; nothing above this line changes post-freeze
except via numbered amendments, pre-data, same discipline as D14)

## Amendment-1 (orientation correction, committed PRE-data, pre-implementation)

Seed: while specifying `winding()` I found by analytic check (wheel-graph
counterexample: canonical a<b<c face orientation reads W = -10/11 for a
genuine m=1 lattice vortex) that canonical label orientation does NOT
telescope: interior bonds fail to cancel, Stokes fails, the sum is
orientation noise, not winding. Face-sum REQUIRES consistently oriented
faces. Fix (locked):

- Faces are oriented by signed area in the J2 readout coords: for triangle
  (a,b,c), e1 = mindisp(a->b), e2 = mindisp(a->c) (minimal torus
  displacement in (x,y)); sign = sign(e1_x e2_y - e1_y e2_x); cyclic order
  flipped to make orientation positive. Deterministic given coords.
- DEGENERATE triangles (zero signed area: collinear or same-(x,y) sheet
  pairs) are EXCLUDED from W (like amplitude exclusions); degenerate
  fraction filed per run; >5% ==> flag (systematic, hits all initials
  equally). Exclusion keeps the R-flip EXACT (R permutes non-degenerate
  triangles, flipping each orientation; pinned).
- Charter softened (owned over-promise): the observable is LOOP-FREE
  (Stokes face-sum: no loop-finding, no principal axis, no centroid loop)
  with face orientation from the J2 readout basis (filed justification,
  same standing as Stage-0 kinematics). Fully intrinsic (ER-ready)
  orientation is QUEUED, not claimed.
- Added pin 5b: Stokes consistency -- K4 (tetrahedron) outward-oriented
  faces sum to 0 for seed-fixed random psi (each bond twice, opposite).
- Wheel-graph pins gain synthetic circle coords (rim on circle, hub at
  center: signed area orients correctly). J2 flip tests verify exactness
  INCLUDING degenerate handling. Health gate unchanged (amplitude
  exclusion < 5% AND |W-round(W)| < 0.1); degenerate fraction filed
  alongside. Bar, tau rule, cells, replacements, blinding: all stand.
- Lattice-vortex note confirmed by the same analysis: the planted twist's
  +-1 charge sits on the CENTRAL (centroid) triangles where the lattice
  angle field is singular (XY-model logic, rho > 0 everywhere is fine);
  all other triangles read ~0. W(S) = net vortex charge in S.

Original text preserved in git history (dcab8b2).

## Amendment-2 (torus-ball region + envelope, committed PRE-evolution-data)

Seed: P3.0-original t=0 readouts (filed below, NO verdict weight) showed
planted m=+-1 reading W2 = +56/-56 (blob 0), +18/-18 (blob 1) and random
controls reading +13/-67/+18/-3 -- all large integers, not +-1/0.
Diagnosis (structural, no evolution data seen): (1) graph-ball S2 (530
nodes, nearly ALL 3500 triangles) is torus-scattered by rewired long
edges, so the antipodal cut of the torus-angle field passes THROUGH S2;
cut-straddling triangles each contribute +-1 and dominate W (the true
core-vortex +-1 is buried). The graph-distance envelope (sigma=6) cannot
suppress the cut because graph-near != torus-near on rewired graphs.
(2) The k4 core itself SPANS the torus (median dist-to-centroid ~10 of
max 19.8; torus-ball r=3 around core set = 1554/1568 nodes): the blob is
a graph-localized SPONGE, not a torus lump. BUT a broad triangle lump
exists: 20-30% of triangles within torus r4 of the core-centroid (3-4x
uniform 6.4%), 44-56% within r6 (vs 14.4%), all 8 blobs; top-degree hubs
scattered (x-range 23-27); k5 ~= 0. The centroid tracks the lump
(Stage-0 continuity preserved). Fix (locked):

- Region: S^T_r = {v : d_T(v, centroid) <= r} (torus-ball around the CORE
  circular-mean centroid, Stage-0 definition UNCHANGED). Primary r=4
  (W^T_4), robustness r in {3, 6} (filed). Replaces graph-ball S_r.
  Cut (dist ~14) never enters the region.
- Envelope: rho(v) = exp(-d_T(v,centroid)^2/2sigma^2), sigma=6 TORUS units
  (same number, torus metric). Replaces graph-distance envelope.
  Controls (m=0, random-phase) share it (control logic unchanged).
- theta(v): UNCHANGED (torus angle about centroid). Orientation:
  UNCHANGED (amendment-1). Health gate / tau rule / bar / cells /
  blinding: UNCHANGED. Region floor (new insurance): S^T_4 must contain
  >= 100 kept triangles (far below observed ~700-1000; violation ==>
  exclude+replace like unhealthy).
- Charter: observable = loop-free Stokes face-sum with orientation AND
  region from the J2 readout basis (filed justification); ER-intrinsic
  queued. Framing: "phase-winding persistence around the triangle lump
  (the D5inf blob's torus manifestation)".
- Mirror P3.0 check CLARIFIED (prereg text was ambiguous, script wrong):
  the exact t=0 check is the (G,RG) comparison W^{RG}_{R(S)}(R_*psi) =
  -W^G_S(psi) (reflected GRAPH's triangles, not G's triangles in R(S);
  R is not in Aut(G) for rewired G). Script bug owned; prereg law-symmetry
  claim (pin 15) stands.
- Superseded graph-region t=0 readouts (blobs 0-1, filed, no weight):
  W2(m=+1) = +56/+18; W2(m=-1) = -56/-18; W2(m=0) = 0/0;
  W2(rand) = +13/-67 (blob0), +18/-3 (blob1); exclusion 0 everywhere
  (envelope failed open); E(+1)=E(-1) exact both blobs (kept result:
  conjugation-E equality is region-independent).
- P3.0-ORIGINAL verdict: APPARATUS-FAILED (2/2 blobs unhealthy under the
  graph-region observable; P3.0 gate correctly stopped P3-A evolutions;
  blinding preserved -- zero psi-evolution steps run). P3.0-REDO (new
  region/envelope, same bar: 2/2 healthy + flips + m=0 + random filed)
  gates P3-A. New pins: torus distance/region + synthetic torus-planted
  winding (sign/magnitude with empirical margin; exact quantization stays
  pinned on the wheel).

## Amendment-3 (coverage normalization, committed PRE-evolution-data)

Seed: the synthetic torus-planted pin reads W = +2.0 EXACTLY for m=+1
(not +1): two sheet-doubled triangles enclosing the centroid each
contribute +1 (per-triangle telescoping is exact; the sum multi-covers).
General law: W(0) = m x E, E = coverage number (count of
centroid-enclosing triangles, a graph-geometric per-blob constant).
Stokes-equals-boundary (= m) holds only for single-cover disks; the blob
lump multi-covers. Fix (locked): all verdict quantities use NORMALIZED
winding Ŵ(t) = W(t)/W_planted(0) (fraction of initial winding retained):

- Planted m=+-1 runs divide by their OWN W(0) (Ŵ(0) = 1 by construction).
- Random-phase controls divide by the SAME-BLOB |W^{+1}(0)| (planted
  scale; filed per blob). m=0 stays RAW (W(0) = 0 exactly); its max|W|
  excursion is reported vs the planted scale (filed, descriptive).
- tau rule / sign-stability / PRIMARY bar (>= 6/16 planted tau > 50 +
  stable sign AND <= 2/16 random tau > 50): UNCHANGED, operating on Ŵ
  (same numbers 0.5/5/50, rescaled meaning: half the initial winding
  lost). Sign-stability for planted: sign(Ŵ) = m while |Ŵ| >= 0.5.
- Health RESTATED (vacuous |W-m|<0.25 replaced): exclusion < 5% AND
  |W(0)| >= 1 (imprint present) AND |W-round(W)| < 0.1 at t=0
  (quantization = leakage check; exact absent exclusions) AND region
  floor >= 100 kept triangles (amendment-2, stands).
- Mirror-imprint: |W^{+1}(0) + W^{-1}(0)| < 0.1 (was 0.05; uniform tol).
- E_blob = W^{+1}(0) filed per blob (coverage; lump triangle-density
  readout). Synthetic pin documents E=2 (sheet doubling) exactly.
- P3.0-REDO bar (same gate, restated quantities): 2/2 blobs healthy +
  flips exact + m=0 ~0 + random t=0 filed + E_blob filed. P3-A gated on
  P3.0-REDO-positive. Zero evolution steps run to date (blinding holds).

## Amendment-4 (region radius r10, committed PRE-evolution-data)

Seed: P3.0-REDO t=0 readouts (filed below, NO verdict weight): apparatus
CORRECT (quantization fp-exact, mirror-imprint exact, conjugation exact,
(G,RG) mirror exact to 1e-16, m=0 exact 0, exclusion 0) but REGION-STARVED:
S^T_4 holds 1 (blob 0) / 8 (blob 1) fully-inside kept triangles -- floor
>= 100 FAILS 2/2. Diagnosis (structural): blob triangles are
TORUS-SPANNING (rewired long edges): ~700 touch the lump (min-dist) but
~0 fit fully inside a small ball (max-dist). Seam analysis (filed): the
P3.0-original +-56 poison was the mindisp-SEAM domain wall (psi sign flip
at dist 14), NOT the theta branch cut (e^{itheta} is continuous across
2pi jumps -- invisible to psi-based W); Stokes handles wraps; regions
avoiding the seam read TRUE core charge (REDO +-1/+-2 correct). Fix
(rule-based on structural counts, no W/tau seen): smallest torus-ball
meeting floor >= 100 on 8/8 with seam margin. Measured kept-tris curve
(blobs 0-7): r4: 0-8; r6: 12-48; r8: 81-186 (fails 2/8: 81, 94); r10:
258-525 (passes 8/8); r12: 787-1215. LOCKED: primary r=10 (W^T_10,
seam margin 4), robustness {8, 12} (filed; r12 margin 2, caveat filed).
sigma=6 STANDS (boundary rho(10)=0.25 healthy; deterministic evolution
has no weak-amplitude noise; exclusion(t) tracked). Floor >= 100 STANDS
(now met: min 258). Health/tau/bar/blinding: STAND. Random-control note
(filed expectation): W_raw_rand(0) ~ O(sqrt(B)) vs E ~ O(10-100) ==>
normalized random starts mostly < 0.5 (contrast half likely vacuous;
planted-persistence half remains a real discovery bar; traces filed).
- P3.0-REDO verdict: APPARATUS-CORRECT BUT REGION-STARVED (2/2 below
  floor; gate correctly holds P3-A; blinding preserved -- zero evolution
  steps run). P3.0-REREDO (r10, same bar) gates P3-A.
- Superseded S^T_4 t=0 readouts (filed, no weight): blob0: W(+1)=+1.00
  (1 tri!), W(-1)=-1.00, W(0)=0, W(rand)=+1/0; blob1: W(+1)=+2.00 (8
  tris), W(-1)=-2.00, W(0)=0, W(rand)=+3/+1; all quant_resid 0, excl 0;
  (G,RG) diff ~1e-16 both; E(+1)=E(-1) exact both.

## Amendment-5 (seam-critical exclusion, committed PRE-evolution-data)

Seed: P3.0-REREDO t=0 (r10) reads E = 72/99 (healthy!), quantization
exact, imprint/conjugation/m=0/exclusion all perfect -- BUT (G,RG) mirror
diff = +4/+12 (was exact at r4). Diagnosis (analytic): signed-area
orientation via mindisp is R-ODD except at the wrap boundary: for even L,
wrap(-L/2) = wrap(+L/2) = -L/2 (R and wrap do not commute there), so any
triangle with a bond of torus-length EXACTLY L/2 (= 14, antipodal,
possible since node coords are integral) has ARBITRARY orientation sign
(R-image keeps, not flips, the sign) and pollutes W by arbitrary +-1.
Spanning-triangle blobs hit these; small regions missed them by luck.
Fix (locked): SEAM-CRITICAL triangles (any bond with |dx| == L/2 or |dy|
== L/2 exactly, integer-exact comparison) are EXCLUDED from W alongside
degenerate ones (orientation-ill-defined by construction, not by luck);
seam fraction filed per run (expect ~1-2%). R-flip then EXACT by the
covariance proof (R permutes kept triangles, flipping each orientation).
L=None synthetics have no seam (plain displacement). Charity check: this
also REMOVES arbitrary +-1s from W itself (cleaner observable).
Completeness note: for integral coords + even L this is the ONLY
R/wrap non-commutation (wrap odd elsewhere) -- pinned + verified.
- P3.0-REREDO verdict: APPARATUS-CORRECT except MIRROR-INEXACT (+4/+12);
  gate holds P3-A; blinding preserved (zero evolution steps run).
  P3.0-REREREDO (seam exclusion, same bar + seam fraction filed + exact
  (G,RG) required) gates P3-A.
- Superseded r10 t=0 readouts (filed, no weight): blob0: E=72,
  W(rand)=+9/+2 (normalized 0.125/0.028, < 0.5 as predicted), quant 0;
  blob1: E=99, W(rand)=+10/-2 (0.101/0.020), quant ~1e-14; mirror
  diff +4/+12; E(+1)=E(-1) exact (region-independent values unchanged
  across redos: +0.0606/-0.0236 -- sanity held).

## Amendment-6 (wrapped-triangle exclusion, committed PRE-evolution-data)

Seed: P3.0-REREREDO t=0: seam exclusion helped (+4/+12 -> +2/+4) but
mirror still inexact. Per-triangle forensics (blob 0, t=0, filed
method): set correspondence R(T^G)==T^RG EXACT (235/235), regions match
(symdiff 0), but 5/235 triangles read SAME sign both sides (net
2x(+1-1+1-1+1)=+2 = the diff exactly). Diagnosis (analytic, verified on
the 5): WRAP-FOLDED triangles -- spanning > L/2 so mindisp folds them
(e.g. y-bonds +17 read as -11); signed area becomes START-DEPENDENT
(+53 from vertex a, -91 from vertex b for BAD #1) and R-inconsistent.
Complete theory (locked): orientation is R-odd EXACTLY for triangles
that are (i) UNWRAPPED (mindisp closure e_ab+e_bc-e_ac == 0 exactly;
wrapped == +-L) and (ii) NON-SEAM (no bond |d| == L/2, amendment-5);
start-independence <==> closure; R-image negates unwrapped vectors
bitwise ==> s' = -s bitwise ==> flip exact. Wrapped triangles (closure
+-L) are EXCLUDED (orientation start-arbitrary); seam kept (R/wrap
non-commute even when closed); degenerate kept (s == 0). orient_faces
returns (kept, oriented, seam_mask, wrap_mask); all fractions filed.
Regression pin: forensics BAD #1 coords pinned wrapped+excluded.
- P3.0-REREREDO verdict: MIRROR-STILL-INEXACT (+2/+4, wrapped triangles);
  gate holds P3-A; blinding preserved (zero evolution steps run).
  P3.0-REREREREDO (wrapped exclusion, same bar + wrap fraction filed +
  exact (G,RG) required) gates P3-A.
- Superseded rererredo t=0 (filed, no weight): blob0: E=66 (235 kept,
  24 seam in region), W(rand)=+3/+2; blob1: E=87 (479 kept, 46 seam),
  W(rand)=+11/+1; mirror diff +2/+4; all else (quant/imprint/conj/m=0/
  E-match) exact as before.

## Verdicts

### P3.0-POSITIVE (apparatus valid; P3-A gate OPENS; filed 2026-10-01)

20 pins pass (suite green on beast, parallel xdist) + campaign-graph
checks on blobs 0-1 (t=0, ZERO evolution steps run before this verdict):

- blob 0 (k4mass 140, centroid (3.96,15.78)): S^T_10 = 624 nodes,
  207 kept tris (>= 100 floor PASS), seam 24 + wrap 28 in region
  (~22% geometric exclusion, psi-independent, filed); E = W(+1)(0) =
  +59.00 (imprint PASS); W(-1)(0) = -59.00 (mirror-imprint sum 0.00
  PASS); W(conj) = -59.00 (PASS); W(m=0) = 0.00 (PASS); quant_resid 0
  (PASS); excl 0 (PASS); (G,RG) mirror diff +0.00e+00 EXACT (PASS);
  E(+1) = E(-1) = +0.060551 exact, E^RG = E^G (PASS).
- blob 1 (k4mass 199, centroid (27.02,20.21)): S^T_10 = 622 nodes,
  428 kept (>= 100 PASS), seam 46 + wrap 51; E = +80.00; W(-1) =
  -80.00 (sum 0.00); conj -80.00; m=0 0.00; quant ~0; excl 0; mirror
  diff +0.00e+00 EXACT; E(+1) = E(-1) = -0.023606 exact, E^RG = E^G.
- Random-phase t=0 (filed baseline): blob0 W = +2/-2 (normalized
  0.034/0.028); blob1 W = +8/-2 (0.100/0.025); all < 0.5 as predicted
  (amendment-4 note holds); quant exact; excl 0.
- Law symmetry R U R^-1 = U verified: pin 15 ([evol,R_*] = 0 to
  1e-12) + campaign (G,RG) exactness + E^RG = E^G. H-gate holds: H
  real-symmetric (K-symmetric), blind proposals, R-covariant law; any
  L/R asymmetry in P3-A is spontaneous by construction.
- Path to green (filed): P3.0-original (graph region, cut-dominated)
  -> amendment-2 (torus region) -> amendment-3 (coverage norm) ->
  amendment-4 (r10; region-starved at r4) -> amendment-5 (seam) ->
  amendment-6 (wrapped; forensics complete theory) -> POSITIVE. All
  amendments pre-evolution-data; blinding held throughout.

P3-A runs authorized (8 blobs x 5 initials, T=200, dt=2, locked bar).

### P3-A verdict: NULL (linear test-wave winding transient; filed 2026-10-01)

40 evolutions (8 frozen blobs x {m=-1,0,+1,r0,r1}, H=-A static, T=200,
dt=2, 101 samples; all formation inputs valid: stop=cap, sweeps=2000,
cores nonempty, no replacements). PRIMARY (locked): planted 0/16 with
tau > 50 + stable sign (need >= 6) AND random 0/16 (need <= 2) ==> NULL.
Result is UNANIMOUS, not marginal:

- Planted 16/16: tau = 2.0 (FIRST sample; |Ŵ| below 0.5 immediately).
  max|Ŵ| = 1.000 for all 16 (never exceeds initial; no revivals).
  Ŵ_end ~ -0.21..+0.23 (noise floor). Coverage E = 52-90 per blob
  (filed per blob below). maxexcl = 0.000 all runs (no zeros ever form).
  Edrift ~ 1e-15..1e-13 (unitary, apparatus healthy). IPR 0.0022 ->
  0.0019-0.0020 (amplitudes stay lump-localized; uniform = 0.00064).
- v1/v2 analysis agreement (filed correction): v1 used signed W(0)
  scale per amendment-3 letter, which forces Ŵ(0)=+1 and fails m=-1
  sign==-1 at t=0 BY CONSTRUCTION (prereg text jointly inconsistent
  for m=-1; v1: 0/16 NULL). v2 uses |W(0)| scale (sign-preserving;
  equivalent to signed-scale + test sign==+1): 0/16 NULL. Verdict
  INVARIANT (tau = 2.0 decides; stability moot). Both versions reported;
  v2 is the corrected record (m=-1 stable=True 7/8 (vacuous single
  t=0 sample), blob6 m=-1 stable=False (one wrong-sign >= 0.5 sample,
  descriptive anomaly, tau fails regardless)).
- Random 16/16: tau = 0.0 (start below 0.5; Ŵ(0) = -0.16..+0.33) --
  contrast holds as predicted (amendment-4 note). m=0: max|W| = 9-13
  raw (frac 0.11-0.24 of planted scale): zero-winding initial GAINS
  pair-fluctuations while planted LOSES winding -- winding
  EQUILIBRATES to a common floor ~0.15 from above and below.
- Robustness W8/W12 (descriptive): tau = 2.0 in 30/32 cells (rest:
  4/6/8/22, all << 50) -- NULL consistent across regions.
- Mirror-lite: tau_{+1} = tau_{-1} = 2.0 on ALL 8 blobs (matched
  trivially; no tau_L != tau_R anomaly -- law-symmetry consistent).
  E_{+1} = E_{-1} exact (t=0, kept). Per-blob (E+, E-, tau+, tau-):
  b0 (59,59,2,2); b1 (80,80,2,2); b2 (78,78,2,2); b3 (60,60,2,2);
  b4 (83,83,2,2); b5 (55,55,2,2); b6 (52,52,2,2); b7 (90,90,2,2).
- Mechanism (post-verdict resolved probe, blob0 m=+1, dt=0.2,
  descriptive): Ŵ = +1.00 -> +0.46 (t=0.2) -> -0.05 (t=0.4) -> noise
  (+-0.25); half-life ~0.2-0.3 ~= 1/spread (spread 2.95, E0=+0.06
  mid-band) ==> DEPHASING (multimode beating). Amplitudes stay (IPR
  flat), phases scramble, no zeros (excl 0): charge exits through the
  region boundary as incoherent phase noise. Linear twists are not
  topologically trapped -- they radiate/dephase away.
- S-churn pilot (descriptive, 2 blobs x m=+1, 200 sweeps, dt=1/sweep
  labeled, seed schedule 9100+k/9300+k filed deviation from 9100/9101
  (rng has no checkpoint; avoids range overlap)): half-life 1 SWEEP
  both regions both blobs; traces fluctuate +-0.3 (noise); maxexcl 0;
  IPR flat; E drifts (time-dependent H, expected); blob0 drifts 4.9
  (lump stays in r10 ball), blob1 sitter (drift 0.2). Drifting-region
  W agrees with fixed-region (true unwinding, not drift-out).
  Full decimated traces: b0 What_fix = +1.00,+0.02,-0.17,-0.03,-0.02,
  +0.02,-0.08,+0.08,-0.12,-0.02,-0.07,+0.05,+0.08,+0.08,+0.15,+0.08,
  -0.14,+0.39,+0.05,-0.05,-0.03 (every 10 sw); What_drift similar
  (+-0.24); b1 similar (+-0.30). Live formation churn destroys winding
  within ~1 sweep.

Implication (filed): rung-1 LINEAR test-wave chirality EXCLUDED on
D5inf blobs (frozen AND churned). The coupled K+psi object at one-way
linear order has NO protected winding sectors; winding equilibrates.
P3-B/P3-C AS DESIGNED are MOOT (no sectors to populate/persist) --
REDESIGN around NONLINEAR psi (self-trapping/DNLS vortices, P3-D debt
now REQUIRED not optional) or gapped/topological H (debts filed openly
if pursued). P3.3/P3.4/D15-gate: no sectors ==> gate never fires; D15
stays closed (correct one-way behavior). The apparatus (R, psi, W,
mirror) stands VALIDATED (P3.0-POSITIVE) for reuse on nonlinear psi.
Data: /tmp/p3_traces on beast (evol_*.pkl x40, churn2_*.pkl x2,
formation pickles /tmp/p3_blobs); suite green (beast, parallel xdist).
NEXT: P3-D prereg (nonlinear psi designs + H-gate proof) or PI redirect
(gated on go).
