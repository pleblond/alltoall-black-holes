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
to control (relaxed-near-tension pin). `emergent_dim` protocol +
two-distance bracket ready; shell no-emergence pin shows what failure looks like.

**Close criterion:** (a) measured `d_eff(l)` profile around a tensed region
matches the GR fingerprint *shape* (dip, overshoot, asymptote) after the
simulator mapping is fixed, with amplitude scaling in the tension; relaxed
control regions show `d = 2` fabric scaling; (b) `κ` vs `(z−4)` fitted with
stated residuals on the same graphs. Both (a) and (b) must output their
curves from graph construction + dynamics, not take GR as input.

**Kill relevance:** P0' first quantitative wire. Failure of the (a)
shape-match after the mapping is fixed refutes the relaxed-vacuum postulate;
success promotes curvature-as-self-stress from ontology to measurement and
feeds D3 (κ→c₂ via tension) and D6 (R_s from the tension profile).
