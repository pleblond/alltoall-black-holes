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

## Verdicts (append below; nothing above this line changes post-freeze)
