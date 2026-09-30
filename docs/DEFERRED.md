# Deferred derivations (v5+)

Single tracker for open derivations deliberately **not** claimed in v5.
Each item: what is missing, why it matters, what would close it.
Honesty ledger in `paper/v5/supplement.tex` S1 points here.

**Tag note (audit v0.2):** `Dn` below means DEFERRED item n. The appendix-letter
tag (D2) (= module `evaporation_unitary`, the closed qubit-toy instance under
D1) is unrelated to DEFERRED-D2 (Kerr multipoles); `docs/model.md` always
writes the module name. `supplement.tex` S1/S3 still uses bare (D2) for both —
flagged for the paper flow (needs PDF rebuild).

## Program pipeline (P0'/D10/D1/D13/D12 + commutation)

Vacuum graph family → graph-internal admissible `M_O` → 2+scale → 3
reconstruction → explicit `U` → `δ_U(s,v;n)` → `V_U(n)`, `≺_U` →
same frozen `M_O` → observed causal geometry → `M_O U ≃ U_eff M_O`.
Division of labor: P0' identifies the vacuum connectivity class; D10
asks why observers reconstruct 3D from it; D1 asks what dynamics
preserves/evolves it; D13 asks whether that dynamics generates causal
time; D12 asks whether the reconstruction is universal;
`M_O U ≃ U_eff M_O` asks whether the whole construction becomes
autonomous spacetime physics.

## D1 — Evaporation isometry V_k (Page/QES) — P0 next cycle

**Missing:** unitary/isometric evaporation map from graph dynamics:
`V_k: H_graph,k -> H_graph,k-1 ⊗ H_leg`.
Current status: `k -> k-1` surgery is imposed; `S_rad = min(t, Neff-t)`
with 0.72-bit dip is imposed/sampled (`evaporation`, `haar`); QES crossing
is a two-saddle competition + discrete min-cut analogue (`qes`), not
`S_gen = A/4G + S_matter` extremized from a gravitational path integral.
Update (PR #10): the qubit-toy instance is closed — `evaporation_unitary`
(appendix tag D2 — not DEFERRED-D2) constructs per-step `V_t`, proves `V†V=I` (incl. a composed-map
inner-product test), and computes `S_rad` from `rho_rad` (tracks Haar/Page
to 0.002 bits; all:all circuits converge by depth ~5). What remains is the
graph instance: derive `V_k` from graph dynamics, not merely choose one.
Scope note (D13): D1's dynamics now also gates emergent time itself
(update rule → causal order → cone → clocks), not just evaporation/QES.
D13-input desideratum (not a close criterion): candidate `U` should be
local and fabric-compatible so D13 stage 1 can run on it. Stabilizer
question (rewire sweep): what dynamics keeps the `d_G ≃ 2` phase
stable against shortcut proliferation (`N* ∼ O(10)` flat in L)?
Preservation target: `U(G_vac) ∈ C_vac` — microscopic evolution may
fluctuate (`G_n ≠ G_{n+1}`) while the IR class stays invariant
(`[G_n]_IR = [G_{n+1}]_IR ∈ C_vac`): vacuum as invariant dynamical
universality class. Then `M_O` quotienting irrelevant fluctuations
gives `M_O(G_n) ≃ M_O(G_{n+1})` — stable vacuum atop a changing
graph (the commutation link). Falsifier protocol (gated on U):
evolve `G_0 → G_1 → …` from `G_vac` and require `G_n ∈ C_vac ∀n`
in equilibrium, up to fluctuations — operationally `⟨Λ⟩_U` in the
vacuum basin for a locality functional Λ (candidates: window-p;
N* itself; distance-to-C_vac; Λ undefined — open). Then inject
shortcuts (`G → G + δG_shortcut`) and watch: persist/amplify kills
the candidate; `δG_shortcut → G_vac` (self-healing) means locality
is an attractor — no perfectly local vacuum graph need be
postulated. Statistical form (stochastic/quantum U): ensemble
concentration `P_U(G ∉ C_vac) → 0` in the IR limit — vacuum as
dynamical phase (this licenses "phase"; no rewiring phase
transition is claimed). Acquired constraint: find a simple U for
which locality, unitarity/information conservation, and the vacuum
structure are simultaneously natural. Stability tournament
(QUEUED behind U, protocol fixed on review): initialize EVERY
Tier-1 candidate (triangular, hex, square, Delaunay, Gabriel, …)
and evolve under EXACTLY the same U; measure escape
P(U^t G ∈ C_vac) per candidate — vacuum selection as attractor /
stationary ensemble (P_U(G) = P_U(U(G))), not static p. Healing
battery: apply the same normalized damage to each candidate
(shortcut injection, edge deletion, degree defect, bottleneck,
plug insertion) and measure relaxation τ_heal(G, δG) under U —
candidates identical in equilibrium may differ sharply in
locality restoration. Selection rule (conceptual):
G_vac = argmax stability of the M_O-equivalence class. First rules
(MEASURED, test_update_rule.py, L=20): harness (locality-p, shortcut
injection, evolve) validated — null persists damage bit-identically,
scramble kills (2.51 → 1.79 collapse). Twin-targeted greedy heals
p = 2.36 → p_plain to 1e-6 into a DIFFERENT microstate (699/760
overlap) — class healing, existence probe only (global target, not a
local rule); plain is its fixed point. Genuinely-local guillotine
(radius-3 edge-span evals, no twin): plain-grid span signature is
exactly 3 on all 760 edges; rule heals longs 30 → 6, p 2.36 → 2.13,
then STALLS — exhaustive check proves 4 of 6 residual longs admit
zero both-short single-swap repairs (locked, incl. short-range edges
whose plaquette detours were destroyed). Mechanism lessons: repair
needs long×long straddling (re-pairing a long with a local edge
always leaves one long); total-span descent splits longs instead of
killing them (count 30 → 39 while p falls — span-sum is a poor
proxy); no local potential tracks p well (corr ≤ 0.58 — p is
source-relative/lottery-noisy, span-census is the more honest global
health stat). Queued escape: neutral moves / annealing on long-count
(stochastic U is filed-legal) / coordinated multi-swaps. Escape
results (MEASURED): neutral drift is WORSE than strict (longs 30 →
22 — local delta doesn't bound global longs, detour rerouting
leaks); blind-proposal annealing stalls (greedy) or explodes
(longs → 101 at T0=5 — proposals matter more than acceptance, not
shipped); census-gated targeted annealing reaches longs 11 (T0=0,
p 1.97) / longs 9 (T0=2, p 2.26) — temperature trades p for longs;
strict→anneal chains and drift⇄strict ratchets don't clear the
locked core. Tournament table from damage (p 2.362, longs 30):
null (2.362, 30); greedy-twin (1.835, 88 — games p, triples
longs!); guillotine (2.132, 6); drift (2.129, 22); anneal (1.97,
11)/(2.26, 9); scramble (1.786, 297). HEADLINE: p-healing ≠
healing — the D1 falsifier must judge (p, longs) jointly, and no
single-swap rule clears both. Next: coordinated multi-swap moves
or new move classes (degree-changing repair? edge-slide?), then
the cross-candidate tournament this harness was built for. New
move class (MEASURED): edge-slide reel-in (radius-6 span gradient;
radius 3 blinds it — 1 accept) reaches longs 5 (best yet) but p
stuck at 2.32 — 5 levered longs hold the window while greedy's 88
hide from it: the (p, longs) plane is genuinely 2D. Slide ⇄
guillotine hybrid FROZEN bit-identically (joint fixed point).
VERDICT: single-move local dynamics (strict/neutral/annealed
swaps, slides, hybrids) cannot restore locality from swap damage
— all stall with residual longs. Locality protection needs
coordinated moves, global search, or new physics (a publishable
constraint on U). D1 first-pass CLOSED; tournament harness stands
ready for future entrants.

**Close criterion (graph instance):** derive (not choose) a scrambling `V_k`
from the graph Hamiltonian/adjacency; show the reduced radiation spectrum
follows the claimed Page curve under all:all dynamics. Then "Page curve is
a theorem of graph dynamics".
Update (this branch): graph instance closed at small-`N` ED level —
`graphvk` derives per-step `V_k = exp(-i H_graph dt)` from the hole adjacency
(disordered Heisenberg, one random XYZ term per edge), proves `V†V=I` (incl.
a composed-map inner-product test), computes `S_rad` from `rho_rad`, and shows
all:all tracks exact Page (mean dev < 0.25 bits at `N = 8`, typically ~0.01)
while the same `dt` on a chain sags below Page (mean dev > 0.4); changing the
graph changes `V` (`||U_complete - U_chain|| > 1`, `is_adjacency_sensitive`).
Fig 74b. What remains: large-`N`/thermodynamic limit, `k`-backreaction on the
interior spectrum, emission energy/mass spectrum, and `S_gen` extremization
from a gravitational path integral (QES still two-saddle + min-cut analogue).

**Kill relevance:** none currently (no observed BH Page curve); referee
honesty issue, not a falsifier.

## D2 — Kerr multipoles from the graph — P1 next cycle

**Missing:** derivation of spin-induced quadrupole `M2 = -M a^2`,
frame dragging `g_tφ`, `r_ISCO(M,J)`, Kerr QNM spectrum from graph dynamics.
Current status: only Kerr-Newman area `A(M,a,Q)` is assumed to set
`k_eff = A/4ln2` (`kerr`, `kerrpage`); overtone toy is Schwarzschild-like.

**Close criterion:** derive `Q = -M a^2 (1 + δ_Q)` without assuming Kerr;
compare `δ_Q` to GW241011 (`|δ_Q| ≳ 0.17` ruled out at symmetric-combination
level; factor ~2 resp. ~10% by parametrization, LIGO-P2500402).

**Kill relevance:** future wire (see v5 kill table "Kerr quadrupole").
GW250114 (LIGO-P2500421, SNR 80 area law + Kerr ringdown) and GW241011 are
currently consistent by construction, not passed predictions.

## D3 — κ -> c2 map (2PN) — ongoing

**Missing:** quantitative Ollivier-Ricci `κ` to 2PN coefficient `c2` map.
`c2 = p(2p-1)` is ansatz; power-law vs `1/r^2` disagree cross-applied.
See supplement S4 / BU. Kill wire `p = 0.92 ± 0.056` held to N=16000.
**v0.5 route:** curvature as failure of `V(r)` to scale uniformly via
`d_eff(r) = d ln V / d ln r` (`emergent_dim` protocol + controls; diffusion
viable at large t, resistance/communicability rejected on record).

## D4 — β(N), w from geometry — ongoing

**Missing:** bridge exponent `β(N)` (log-linear over 6 points, recalibrated
per N) and 2PN weight `w = 1.953` (solved from cancellation) derived from
graph Laplacian / Damour-Schafer from wiring.
**v0.5 route:** `β(N)` from `N(r)` implied by `V(r)` scaling (`emergent_dim`).

## D5 — NICER M-R-Λ + tidal deformability — P1

**Missing:** `R_1.4`, `M-R`, tidal `Λ` from routing stiffness.
Sharpest near-term test after kilonova rate (2-3 yr timeline).

## D6 — Mass-radius from wiring — long-term

**Missing:** `R_s = 2M` (BM reduction: `k(M)` iff `R_s(M)` given).
Single GR input; derivation from wiring alone open.
**v0.5 route:** `R_s` as radius where embedding `k` legs into `M_O(G_vac)`
forces a surface (T5 pop + `d_eff -> 3` IR fixed point, still open).

## D7 — Kilonova radiative transfer — analytic systematics done, full RT queued

**Update (round 4):** analytic viewing/opacity/dust systematics shipped
(`massgaps.gw190814_*_sys`, `gw190814_systematics_table`, Fig 75b, 9 tests):
POSSIS-inspired viewing (equatorial +1.25 g/+0.5 i) + Arnett opacity
rescaling bound the hiding window (equatorial + κ_blue=2 → P~0.18).
**Still missing:** validated multidimensional RT per the D7 v2 work package
(public-data ejecta compatible with F5/F6 bulk parameters, morphology +
velocity structure + Ye-dependent opacities/reprocessing, viewing-angle
dependence, direct i-band after the AT2017gfo anchor gate passes; POSSIS
primary). i-band direct not claimed until then (one-zone κ=10 over-traps).
g-band verdicts robust; gap-KN ~1/yr O5 prediction stands.

## D8 — Shedding efficiency ε(M,a) + upper-gap assignment — P1

**Missing:** derivation of the shedding efficiency's mass, spin, and
mass-ratio dependence from graph dynamics. Current status: `M_ej =
0.0168 M_tot` exactly universal (shed fraction 0.168 × 10% efficiency,
both fixed once on AT2017gfo; `collapse`, `massgaps`). Mass and
q-independence are extrapolated, not derived — the highest-value attack
surface on the universal (BBH) transient prediction.

**Close criterion:** derive `ε(M,a,q)` from `K_max(N)` combinatorics,
spin-ordered reabsorption, or remnant-trap physics with the shutoff
location (if any) as output, not input. A derived shutoff between gap
and BBH masses must land where it lands; inserting it at any observed
scale is refused (same rule as the 44 M☉ graph null).
Update (this branch): mass-ratio SHAPE + mass independence derived —
`mergershed` gets `frac(q) = η·2q/(1+q)²` from cross-bond counting with
`1/N` dilution forced by extensivity + all:all symmetry (monogamy
displaces `dS/s_leg` legs; `N` cancels). One calibration `η = 0.336`
replaces `e_final` (anchor `frac(1) = 0.168`); `η < 1` predicted and held;
`ε = 0.1` stays an astrophysics input. GW190814 dims ~0.4 mag vs the flat
prescription but stays kilonova-bright (`M_ej ≈ 0.157 M☉`); the flat
`collapse` law is kept as the O5 falsifier and the sample adjudicates
flat-vs-shaped (Fig 68b). Still open: `ε(M,a)` shutoff derivation.

**Related (not deferred — answered):** no graph feature at the
pair-instability edge. `k(M)` zero curvature, smooth spin/Love running,
He-core χ ~ 1e-8 (`massgaps`): the ~44 M☉ boundary belongs to
stellar/nuclear physics. Negative prediction, main text.

## D9 — Raychaudhuri for leg bundles (Jacobson-chain closure)

**Missing:** focusing theorem for SI fronts on leg networks. Current status:
the Jacobson chain is complete *except* this bridge — heat `dQ = eps·dk`,
Unruh `T = kappa/2pi` (input), saturated `dS = ln2·dk`, Clausius-demanded
`eps = kappa·ln2/2pi`, and measured `eta = ln2/PATCH = 1/4` giving `G = 1`
(`jacobson`: `clausius_leg_energy`, `measured_eta_closure`, all tested).

**Close criterion:** derive (not cite) Raychaudhuri-style focusing for fronts
propagating on leg networks; AT congestion slowdown is the documented seed.
Closes I6c in `docs/model.md` and promotes "Einstein equations follow" from
conditional to derived.

**Kill relevance:** none (gates no theorem in T8–T11); mathematical completion
of the AU triptych's third route.

## D10 — Tension spectrum: simulator d-dip around mass + tension→κ map (v0.6)

**Missing:** (a) the graph-side reproduction of the GR dimensional
fingerprint: an over-coordinated (tense, `z > 4`) region must show near dip +
overshoot + `→3⁺` under info-side `d_eff`, while relaxed `z ≈ 4` regions
show fabric `d = 2` / reconstructed `d = 3` as applicable; (b) a quantitative
tension→curvature map: Ollivier–Ricci `κ` tracking over-coordination (`z−4`).
Current status: GR side computed (`docs/relaxed-vacuum.md` §5: dip 2.990 at
`30M`, overshoot 3.030 at `100M`, `→3⁺` as `~1/l`); graph side: v0.6 probe
(L=100) shows unweighted tense plugs dip below fabric dimension and recover
from below (**inverted** vs GR far side — bare shortest-path rejected as
`d(i,j)` for tense regions, pinned), ad-hoc excess-degree costs flip toward
the GR side (mechanism check, `α` not derived), diffusion collapses on the
clique plug (heat trap, no power law); far-source near balls bit-identical
to control (relaxed-near-tension pin). D10b cost candidates (15 tests): tortuosity-import `w = 1 + c√χ` (`c = 1/2` from T11, zero-fit)
partially recovers the clique plug (1.60 → 1.86 vs control 1.92, no flip;
flip needs `c* ≈ 0.58`, diagnostic); `c_eff`-import `w = 1 + χ` (AT light
sector, saturating `x = χ/(1+χ)` bridge) flips clique (3.43, big overshoot)
and mild plug (1.73 → 2.02 vs 1.92, modest +5% overshoot) — overshoot-side
only, dip-phase (U-shape) open, amplitude unclaimed. Fingerprint + amplitude
(25 tests): 9×9 χ~1 plug shows full dip (−0.18) → overshoot (+0.79 peak) →
asymptote (+0.09) shape-match conditional on the ceff bridge; dip-min ratio
deepens (0.20/0.077/0.016), overshoot peak grows (0.79/0.94/2.91), far-field
`E ~ A(χ)Rc/r` with non-universal `A` (deficit ∝ tension; tail exponent
filed as D11); κ-profile is an
interface pattern (boundary-negative, core-positive), not monotone tracking
(criterion (b) refined to profile); flip lives in `z_vac ~ [2,5]` containing
P0' 4; conductance-weighted diffusion improves the heat trap (r² 0.54 →
0.78) without cleaning it. T15 cost-dominance theorem (`model.md` §2):
shortcuts priced ≥ hop-saving cannot inflate balls — c_eff at `z_vac=1`
satisfies it (max `V_w/V_0 = 0.2000`, no flip), tortuosity-import at
`z_vac=4` violates it on all 32 diagonals (fractional blip `V_w(1.9)=9>5`,
hidden from integer sampling, mid-window flips 2.020); c_eff at vacuum
`z_vac=4` violates on exactly the 24 boundary diagonals (witness: all 24
arrive early from endpoint balls; center-source volume blip peaks 1.077
at r=13.75, likewise hidden at integers).
Leading 2D+scale candidate mechanism: scale multiplicity `n_s(r) ∝ r`
(`dV_O ~ n_s·dV_G → R³`); `s` undefined, RG-log baseline gives the wrong
profile — linear-vs-log must be measured, not assumed (essay §8).
`emergent_dim` protocol +
two-distance bracket ready; shell no-emergence pin shows what failure looks like.
`M_O` formal upgrade (adopted): observer `O` is defined by a
graph-internal accessible observable algebra `A_O(G)`; observational
equivalence `G_1 ~_O G_2 ⟺ A(G_1) = A(G_2) ∀A ∈ A_O`, and
`M_O(G) = [G]_{~_O}` — an operational quotient, not a free
graph-to-manifold embedding (a clever-enough free map could make
anything look 3D). Admissibility requires all five: (1) graph-internal
(no target dimension, coordinates, metric, GR quantity, or desired
phenomenology in the definition); (2) permutation-covariant
(relabeling cannot change reconstructed physics); (3) coarse-graining
stable (`A_O`-invisible perturbations don't move the macroscopic
reconstruction); (4) operational (every quantity obtainable by
interactions available to `O`); (5) frozen rule (state-independent
prescription). `V_O(R) ~ R³` is an output test, never an input:
admissible-from-graph-internal-criteria ⟹ measure `d_obs`, not the
reverse. Substrate family (D13.0, MEASURED): triangular/hexagonal
positive controls reproduce `d_G → 2` with lattice-dependent
prefactors under one frozen measurement rule; gated-wall negative
control keeps bit-identical `~r²` balls with collapsed cut capacity —
`d_G ≃ 2` is not sufficient for channel scaling. Killer result queued:
same frozen `M_O` → `d_obs → 3` on every positive family member
(per-`M_O` tuning proves nothing). Vacuum-class sketch (from the
rewire sweep): degree sequence fixed does NOT imply 2D information
geometry — ~20 swaps in 3120 edges take V(14) 421 → ~909 with p ~ 2.6.
Candidate mesoscopic characterization: `G_vac ∈ C_2 ⟺ V_G(r) ~ r²`
over an expanding pre-boundary regime — but this risks circularity
(P0' says "vacuum is 2D"; defining vacuum graphs as "graphs whose
balls are 2D" defines the result). The primitive property sought is
absence of sufficiently long-range shortcuts, to be formulated via
graph-internal hierarchy, not coordinates (shortcut-absence
hypothesis, open). Sweep results (L=30/40/60, 5 seeds): few swaps
inflate (p > 2, placement lottery — typically 4/5 seeds rise by
ns=20), many swaps saturate (p → 0); N* (first ns with p > 2.2) has
median ≤ 40 at every L — O(10) shortcuts regardless of size (α ≈ 0
on L=30..60, fixed window). Scaled windows LANDED (L=40/60/80, [0.15L,0.35L]). Bookkeeping:
MEASURED — N*_med = (20,10,10); INFERENCE supported — N* = O(1)
consistent (α ≈ 0 over the tested range; rejects N* ∝ |E| there);
HYPOTHESIS — asymptotic f* = N*/|E| → 0. Headline: low-dimensional
locality is not generic; it must be protected. Working gloss (not a
new postulate): vacuum is a dynamically protected low-dimensional
information-locality class — something P0' + D1 must eventually
explain. Shortcut density is a candidate RG-relevant perturbation
(y_λ > 0? — investigation, not established). First RG-blocking
measurement SUPPORTS relevance: 2×2 blocking (L40 → 5) keeps
plain-grid long-edge fraction exactly 0.0 at every level while
ns=20 rewired flows 0.013 → 0.044 → 0.14 → 0.31 (>1.8× per step,
every seed; rough y_λ ≈ 1.5 from 24× over 3 steps). Long COUNT
falls (40 → ~18, some merge into short edges) while the DENSITY
rises 24× — the density is the relevant quantity. y_λ ≈ 1.5 is a
first estimate, not a quoted exponent (one blocking scheme, one f). Within-L caveat: at fixed
absolute ns the departure peaks mid-window and dilutes outward —
the relevance statement is f* → 0, not within-L growth. Small
systems saturate while large still inflate (ns=320: L=30 p < 1 <
2.5 < L=60 p). No sharp jump seen: smooth crossover with extreme
small-f sensitivity. Two emergence problems, kept separate (essay
§8): L0 locality (P0' + D1 — why U maintains a low-dimensional
connectivity class) vs observer dimensionality (D10 + D12 — why M_O
reconstructs 2+scale as 3D). Tier-1 substrate filing (universality
class, not lattice luck): Poisson-Delaunay (PINNED,
test_substrate_family.py) — planar, mean degree 5.97, shells ≈ 8n, linear cuts
(R² > 0.996), p ≈ 1.92..2.06, survives q = 0.10 deletion, dies on
20 swaps (p ≈ 2.50..2.67); Delaunay-medial quadrangulation (PINNED)
— 4-regular interior reproduces d_G → 2, so quad vs
triangulation does not select the dimension. Schaeffer-exact-UIPQ:
ATTEMPTED, FAILED with diagnosis — free-walk-plus-shift labels are
not conditioned well-labeled trees (post-hoc shift ≠ Doob
conditioning; root label free instead of 1; min->1 labelings only),
so the sampler never was uniform over well-labeled trees; the
observable symptom is parallel-edge concentration collapsing the
map origin to a degree-1 leaf (shells[1] = 1 all seeds) with
seed-unstable bulk p (1.69..3.24 at n=2000). Exact-Brownian
benchmark stays QUEUED behind the conditioned-labels sampler
(mobiles/BDFG route); the medial quad carries quadrangulation
evidence meanwhile. Lloyd-relaxed Delaunay (PINNED, iters=20 converged:
p = 1.91/2.08; Lloyd5 seed-0 p ≈ 2.3 was under-relaxation
artifact) and Gabriel/k-NN graphs (PINNED: connected, p ≈
1.92..2.02, linear cuts; Gabriel strictly sparser at ~2/3
Delaunay edges) plus short-only rewire (PINNED: span ≤ 2 swaps
keep p ≈ 1.77..1.96 at ns=20/80 — the rewire kill comes from
span, not rewiring as such). Ensemble ontology (ADOPTED on
review): Tier-1 degeneracy across topology/degree/order is the
EXPECTED signature, not a missing discriminator —
G_△ ∼_O G_hex ∼_O G_□ ∼_O G_Del ∼_O G_Gabriel is positive
universality evidence. The physical object is the class [G]_{~_O}
(prospectively the dynamical class [G]_{U,O}), possibly an
ensemble E_vac = {G : P_vac(G)} rather than one graph;
Poisson-Delaunay is frozen as REFERENCE MEMBER (gauge choice for
reproducibility), never "the" vacuum. Companion principle to the
five admissibility criteria: don't put information into the
vacuum that observation doesn't require — crystalline candidates
smuggle unrequested long-range order; the max-entropy program
(P(G|C_vac) ∝ e^{-λI(G)}, derive the typical graph from the
constraints) is QUEUED behind formulating the C_vac constraint
set without circularity (shortcut-absence still open). Spectral
leg (MEASURED, test_spectral.py): heat-trace d_s(t) on the
boundary-free 60×60 torus holds (1.95, 2.05) over t ∈ [10,100]
(method anchor — finite-size falloff only past t ~ 150); Weyl
counting fits land every Tier-1 member in one band (1.90, 2.15):
torus 2.049, open 1.947, tri 2.018, hex 1.983, Delaunay 2.103,
Gabriel 2.021, k-NN 1.926, medial 1.931. k-NN's 1.514 at N=1600
is a slow diffusive-crossover transient (clustering traps), not
a split — converges up with N as Delaunay converges down
(2.223 → 2.103). Lloyd EXCLUDED from spectral comparison: the
unclipped relaxation coalesces points above N≈1600 (mean degree
1.52 at N=6400/iters=20, 0.04 at iters=80 — degenerate input,
not physics); boundary-clipped Lloyd queued. d_s is now the
second universality leg beside d_H;
diffusion-anisotropy precursor (second-moment tensor of K(t))
SUPERSEDED by measurement: covariance is blind to 4-fold
(square-lattice heat is x↔y symmetric → A ≡ 0 exactly while
diamonds persist); angular-4-fold-power F4 replacement shows
lattice F4 already < 0.01 by t=10 (fast CLT isotropization)
while Poisson-fabric F4 sits at fluctuation level 0.01..0.11
with square-box boundary imprint at large r — no clean IR
discriminator at these scales. Fair lattice-vs-fabric IR
comparison (F4-decay exponents at matched radius) queued behind
toroidal point-set builds + the D13.5 propagation law; NOT
pinned. It pre-registers the minimize-preferred-frame criterion
for D13 as a questioned precursor, not evidence.

**Close criterion:** (a) measured `d_eff(l)` profile around a tensed region
matches the GR fingerprint *shape* (dip, overshoot, asymptote) after the
simulator mapping is fixed, with amplitude scaling in the tension; relaxed
control regions show `d = 2` fabric scaling. (a) is SATISFIED conditional on
the ceff cost bridge (mild-plug shape + amplitude scaling pinned); full close
needs the bridge derived or replaced by derivation. (b) κ-PROFILE (REFORMULATED
after monotone-tracking failed): boundary-negative / core-positive pattern
with stated values, first measurement recorded (clique −0.93/+0.89, mild
−0.31/~0, fabric 0) — confirmation on independent plug geometries pending
before (b) closes. Both (a) and (b) must output their
curves from graph construction + dynamics, not take GR as input.

**Kill relevance:** P0' first quantitative wire. Failure of the (a)
shape-match after the mapping is fixed refutes the relaxed-vacuum postulate;
success promotes curvature-as-self-stress from ontology to measurement and
feeds D3 (κ→c₂ via tension) and D6 (R_s from the tension profile).
Generalization stated as the tension-imprint conjecture (`model.md` §5):
fingerprint universality under the fixed ceff rule, with falsifiers and
P5-promotion criteria; the cost rule stays conjecture-grade until they are met.
D10a bridge-derivation attempts (MEASURED NEGATIVES, not pinned):
(i) random-walk first-passage across the plug ladder DECREASES with
χ (416 → 304 → 263 → 232 steps, plain → mild → x2 → x3; clique 237)
— tense regions conduct faster, so √χ-as-traversal-delay has no
walk derivation (anti-tortuosity); (ii) plug residence (center exit
time) scales as exitT/exitT0 ~ (1+χ)^0.78 with a mild→clique jump
(10.4 → 12.0 → 14.2 → 14.8 → 32.9) — sublinear but neither √χ nor
linear, deriving neither candidate's form. Remaining honest paths:
tighten the BV ln2 bracket to c = 1/2 analytically (pen-and-paper),
or the congestion route via D1 update-capacity (gated on U). The
imports stay labeled.

## D11 — Far-field tail exponent of the tension fingerprint (D10b)

**Missing:** the asymptotic law of the excess-slope tail `E(r) = p_w − p_0`
far from a tensed region. Two shadow accountings compete: a *wedge* shadow
(delayed nodes `~ Rc·r` in 2D) gives deficit `D = 1 − V_w/V_0 ~ Rc/r` hence
`E ~ 1/r`; a *fixed* shadow (constant delayed interior `~ Rc²`) gives
`E ~ 1/r²`. L=120 probe (strength trio, `Rc`-relative windows): χ~1 tail is
`1/r²`-like to `6Rc` (`E·r²` flat: `A = E·r/Rc` falls 0.30 → 0.16 as `1/r`);
χ~2 is `1/r`-like to `5Rc` (`A` flat 0.64 → 0.63) then bursty; χ~5 bursty
throughout. Windows past `~6Rc` are boundary-contaminated on L=120
(half-width 60; χ~1 `k=10` window fully clipped, `E = 0.0000`), so neither
law is established — the exponent may be tension-dependent or one law may
be a transient of the other.

**Close criterion:** measured `E(r)` tail on `L ≥ 200` with clean
(`Rc`-relative, unclipped) windows to `10Rc`, deciding `1/r` vs `1/r²` vs
tension-dependent crossover, with the winning accounting derived from the
cost rule rather than fitted.

**Kill relevance:** none directly — a shape detail, not the shape itself.
Feeds the tension-imprint conjecture amplitude clause (`model.md` §5).

## D12 — Reconstruction universality: why admissible M_O converge

**Missing:** the reason independently-admissible observer reconstruction
maps recover the same macroscopic geometry. `model.md` defines objective
spacetime as the part of `G`'s information structure invariant under all
admissible `M_O` — but names no independent admissibility criterion, so
"admissible" risks meaning "gives 3D" (circular). The critic's question
stands: why resistance / diffusion / communicability distance, and why
couldn't another reasonable reconstruction give 4D, 7D, or no smooth
geometry at all?

**Close criterion:** `A_macro(G)` = {`M_O(G) = [G]_{~_O}` : `A_O`
satisfies the five admissibility criteria (graph-internal,
permutation-covariant, coarse-graining stable, operational, frozen
rule — D10)}. The access floor is part of the definition (a
single-node "observer" recovers nothing); `V_O ~ R³` is the output
test, never an input. Target: ∀ `M_O ∈ A_macro(G)`,
`M_O(G) ∼ M` up to coordinate/coarse-graining equivalence. P4 audit
(uniform Ollivier, `orici`, p=0): (1) graph-internal PASS (uniform
neighborhood measures + hop metric; no coordinates or target
dimension); (2) permutation-covariant PASS + TEST (relabeling leaves
the κ multiset unchanged); (3) coarse-graining stable PASS on flat and plug backgrounds
(single-edge flip moves κ only within 3 hops, far drift < 1e-9 —
measured modulus); (4) operational
PARTIAL (EMD computable from neighborhood data in principle, but
global-EMD + full-neighborhood readout exceeds local-observer access —
needs access-cost accounting); (5) frozen rule PASS (p=0 uniform
prescription is state-independent).
Partial-credit ladder:
(i) criterion stated + non-circularity argued; (ii) two instances agree on
vacuum fabric; (iii) agreement extends to tensed regions (fingerprint
shape under both). Prerequisite (fiber control): verify `M_O`
preimages exist at the reconstruction resolution — distinct
`G_a ≠ G_b` sharing a macro-state — else C3's twin-histories test is
untestable. Dynamical extension (on review): once D1 exists the
universality object upgrades from `[G]_{~_O}` to the dynamical
class `[G]_{U,O}` — microscopic graphs may fluctuate
(`G_1 → G_2 → …`) while `M_O(G_1) ≃ M_O(G_2)`; Tier-1
indistinguishability is then exactly what emergence predicts, and
the vacuum measure over graphs (or its dynamical universality
class) replaces the winning tessellation as the derivation target.

**Kill relevance:** none directly — a meta-criterion over D3/D4/D6/D10.
But a second admissible `M_O` giving robustly non-3D IR on relaxed fabric
refutes the P0' reconstruction program (same-`M_O` falsifier, essay §8).

## D13 — Emergent causal order: update rule → cone → clocks → interval (staged)

**Missing:** the temporal half of "why spacetime?". L0 has no dynamics
(D1); D1's scope now includes time itself, not just evaporation/QES
(D1 provides `U`; D13 asks whether `U` becomes time — the items share
their object). Target, split by level (corrected): `V_G ~ t²` at
substrate, `V_O ~ R³` after `M_O`; microscopic index `n`, causal order
`≺_U`, and clock time `τ` are three distinct orderings (`n ≠ t_obs` as
`d_G ≠ d_obs`).

**Control (D13.0, MEASURED):** static P0' substrate geometry: analytic
`V_G(r) = 1+2r(r+1)`, bit-pinned at L=40/80, finite-window fits rising
toward 2 with radius (1.9196 → 1.9603 fractional); plus the plug sign
pattern (35<38 hops vs +5.0 weighted) as pre-registration for stage 1.
Briefly filed as stage 1, demoted on review: first-passage here *is*
hop distance — compatibility with a cone is not observation of one.
Substrate family MEASURED (de-brittling landed): triangular (shells
6n, cuts 12r+6) and hexagonal (shells 3n, alternating cut law)
positive controls reproduce `d_G → 2` with lattice-dependent
prefactors under one frozen rule; gated-wall negative control keeps
bit-identical `~r²` balls with collapsed cuts. Noisy-grid disorder
control MEASURED (q=0.10 edge deletion: jittered shells, `p = 1.909`,
linear cuts — statistical pins, no lattice law); rewired-grid
fragility control MEASURED (20 degree-preserving swaps: identical
degrees, balls accelerated past `~r²` — V14 ~909 vs 421, `p ~ 2.6` —
the opposite failure from gated-wall bottlenecks).

**Close criterion (staged):** (1) `U → T_U, ≺_U`: stated local
update rule + counterfactual-influence machinery:
`δ_U(s,v;n) = D(R_v[X_n^{(s)}], R_v[X_n])` from a do-intervention at
`s` (minimal standardized perturbation; graph, `U`, boundaries, and
noise realization held fixed — paired randomness for stochastic `U`),
influence ball `B_U(s,n;ε)` with `V_U(s,n;ε) = |B_U|` plus integrated
`Ṽ_U(s,n) = Σ_v f(δ_U)` so ε-sensitivity is signal, not embarrassment
(`D`, `f` unfrozen); `V_U ≠ V_BFS` by construction. Order
`s ≺_U (v,n)` from intervention, not correlation. Required controls:
null (no intervention → δ = 0), disconnected (paths cut → δ = 0),
speed-limit (radius-`q` `U`: `d_hop > qn` → δ = 0) — the last giving
analytic `C_U^max` against which measured `C_U^influence` can be
narrower; (2) `(≺_U, M_O) → cone`: observed causal cone compatible
with the *same* `M_O` producing `R³`, order-dimension agreeing with
`d_eff` (1+3 output, not input); (3) clocks: internal-cycle clock with
`dτ/dt(χ)` reproducing the T9 profile from capacity/congestion,
unimported; (4) interval: `g_μν` from `(≺_U, V_U, M_O)`
(Malament-shaped: order fixes the conformal class, the stage-1
influence volume `V_U` (event counts in causal balls) fixes the
factor; spatial `V(r)` is reachability, not event volume) reproducing the T8–T11 battery. Each
stage closes independently; GR is
the check, never the input, and only at stage 4. (5) dispersion /
isotropy (QUEUED behind a local propagation law): same law on all
Tier-1 candidates, measure `ω(k)` — IR `ω² = c²k² + a_4k⁴ + …`,
angular `c(θ)`, anisotropy/birefringence-like corrections;
selection criterion minimize-observable-preferred-frame-structure
under coarse-graining (variational form: maximize macroscopic
symmetry subject to minimum microscopic structure). Static
precursor runnable now: diffusion-anisotropy tensor of `K(t)`
(D10 spectral leg). Tier-2 static members (Kagome/Dice, Penrose,
stealthy HU) CANCELLED per direction: Tier-1 already spans
topology × degree × order, further static d_G adds no axis.

**Over-arching falsifier (C1–C5, essay §8):** `M_O ∘ U ≃ U_eff ∘ M_O`
with coherence → locality → autonomy → universality → GR limit, each
level presupposing the previous (C4 quantifies C1–C3 across `A_macro`).
Autonomy-before-GR: snapshots resembling GR whose next step needs hidden
`G_n` fail. Operational form: twin histories (`M_O(G_a) = M_O(G_b)` ⇒
`M_O(U(G_a)) ≃ M_O(U(G_b))`, ε–δ in macro-profile distance, RG-weakened
`ΔM → 0` in the IR); presupposes D12 fiber control. Roof: macro-states
as `~_macro` dynamical-equivalence classes; factoring `M_O` through
them does NOT imply autonomy (two-bit swap counterexample: singleton
classes, failing twins — essay §8), so the twin criterion stays
defining. Stage 4 vs C5: stage 4 reconstructs
the interval from `(≺_U, V_U, τ, M_O)`; C5 demands that interval's
*evolution* match GR — reconstruction vs dynamics, tested separately.

**Kill relevance:** feeds D1 (dynamics) and D12 (same-`M_O` falsifier: the
interval map must coincide with the spatial `M_O`). No direct kill wire
until stage 3+.
