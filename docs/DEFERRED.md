# Deferred derivations (v5+)

Single tracker for open derivations deliberately **not** claimed in v5.
Each item: what is missing, why it matters, what would close it.
Honesty ledger in `paper/v5/supplement.tex` S1 points here.

**Tag note (audit v0.2):** `Dn` below means DEFERRED item n. The appendix-letter
tag (D2) (= module `evaporation_unitary`, the closed qubit-toy instance under
D1) is unrelated to DEFERRED-D2 (Kerr multipoles); `docs/model.md` always
writes the module name. `supplement.tex` S1/S3 still uses bare (D2) for both —
flagged for the paper flow (needs PDF rebuild).

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

**Close criterion:** define `A_macro(G)` = {`M_O` : graph-internal
admissibility/access criteria satisfied} — the access floor is part of
the definition (a single-node "observer" recovers nothing), and neither
"3D" nor "Lorentzian" may occur in it. Target: ∀ `M_O ∈ A_macro(G)`,
`M_O(G) ∼ M` up to coordinate/coarse-graining equivalence.
Partial-credit ladder:
(i) criterion stated + non-circularity argued; (ii) two instances agree on
vacuum fabric; (iii) agreement extends to tensed regions (fingerprint
shape under both).

**Kill relevance:** none directly — a meta-criterion over D3/D4/D6/D10.
But a second admissible `M_O` giving robustly non-3D IR on relaxed fabric
refutes the P0' reconstruction program (same-`M_O` falsifier, essay §8).

## D13 — Emergent causal order: update rule → cone → clocks → interval (staged)

**Missing:** the temporal half of "why spacetime?". L0 has no dynamics
(D1); D1's scope now includes time itself, not just evaporation/QES.
Target, split by level (corrected): `V_G ~ t²` at substrate, `V_O ~ R³`
after `M_O`; microscopic index `n`, causal order `≺`, and clock time `τ`
are three distinct orderings (`n ≠ t_obs` as `d_G ≠ d_obs`).

**Close criterion (staged):** (1) substrate cone: stated local update rule
+ measured universal finite cone on relaxed fabric with `V(t) ~ t²`
(trivial-dynamics baseline PINNED: SI shells `p = 1.920`,
`test_scrambling`); (2) order dimension: causal-order dimension measured
independently, agreeing with spatial `d_eff` (1+3 output, not input);
(3) clock rate: internal-cycle clock with `dτ/dt(χ)` reproducing the T9
redshift profile from capacity/congestion, unimported; (4) interval:
reconstructed `g_μν` from causal relations + `V(r)` (Malament-shaped)
reproducing the T8–T11 battery. Each stage closes independently; GR is
the check, never the input.

**Over-arching falsifier (C1–C5, essay §8):** `M_O ∘ U ≃ U_eff ∘ M_O`
with coherence → locality → autonomy → universality → GR limit, each
level presupposing the previous (C4 quantifies C1–C3 across `A_macro`).
Autonomy-before-GR: snapshots resembling GR whose next step needs hidden
`G_n` fail. Operational form: twin histories (`M_O(G_a) = M_O(G_b)` ⇒
`M_O(U(G_a)) ≃ M_O(U(G_b))`, ε–δ in macro-profile distance, RG-weakened
`ΔM → 0` in the IR); presupposes D12 fiber control. Roof: macro-states
as `~_macro` dynamical-equivalence classes; `M_O` must factor through
them (well-definedness ⟺ C3).

**Kill relevance:** feeds D1 (dynamics) and D12 (same-`M_O` falsifier: the
interval map must coincide with the spatial `M_O`). No direct kill wire
until stage 3+.
