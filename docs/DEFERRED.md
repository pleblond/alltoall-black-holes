# Deferred derivations (v5+)

Single tracker for open derivations deliberately **not** claimed in v5.
Each item: what is missing, why it matters, what would close it.
Honesty ledger in `paper/v5/supplement.tex` S1 points here.

## D1 — Evaporation isometry V_k (Page/QES) — P0 next cycle

**Missing:** unitary/isometric evaporation map from graph dynamics:
`V_k: H_graph,k -> H_graph,k-1 ⊗ H_leg`.
Current status: `k -> k-1` surgery is imposed; `S_rad = min(t, Neff-t)`
with 0.72-bit dip is imposed/sampled (`evaporation`, `haar`); QES crossing
is a two-saddle competition + discrete min-cut analogue (`qes`), not
`S_gen = A/4G + S_matter` extremized from a gravitational path integral.

**Close criterion:** construct `V_k`, prove it preserves inner products,
show the reduced radiation spectrum follows the claimed Page curve under
all:all dynamics. Then "Page curve is a theorem of graph dynamics".

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
`c2 = p_OR(2 p_OR-1)` is ansatz; power-law vs `1/r^2` disagree cross-applied
(`0.82` vs `3.14`).
`p_OR` (radial exponent `|κ| ~ r^-p_OR`) enters only at 2PN; the 1PN
coefficient is held at unity (`γ = 1`) from the BH sector and is not refit
by `p_OR`. BV's `c = 0.44–0.60` brackets the BH `1/2` at ~20%
(`γ = 2c = 0.88–1.2`), a consistency check, not Cassini-precision.
See supplement S4 / BU. Kill wire `p_OR = 0.92 ± 0.056` held to N=16000.

## D4 — β(N), w from geometry — ongoing

**Missing:** bridge exponent `β(N)` (log-linear over 6 points, recalibrated
per N) and 2PN weight `w = 1.953` (solved from cancellation) derived from
graph Laplacian / Damour-Schafer from wiring. Gradient slope `0.015`
likewise fitted.

## D5 — NICER M-R-Λ + tidal deformability + surface — P1

**Missing:** `R_1.4`, `M-R`, tidal `Λ` from routing stiffness, plus the
stellar-surface definition and shed-leg hadronisation chemistry (`Y_e`, Sr).
Sharpest near-term test after kilonova rate (2-3 yr timeline).

Current tension (stated, not hidden): `k(M)` gives a would-be horizon radius
`R_s(1.4 M_sun) ≈ 4.1 km`, well inside the observed `R_1.4 ≈ 11–13 km`.
Low-`k` objects are horizonless (`χ < 1`, delocalized phase); their ~12-km
photosphere must come from routing stiffness, which is underived. Targets:
`R_1.4 = 11.5 ± 0.9 km`, `Λ_1.4 = 265^{+238}_{-104}` (joint GW+NICER) or
`Λ_1.4 = 190^{+390}_{-120}` (GW170817 alone); Sr II in AT2017gfo (Watson+19).

**Close criterion:** derive `R(M)`, `Λ(M)` from leg response to tidal fields;
reproduce `R_1.4` at 5% and `Λ_1.4` at 90%, or BU is killed (v5 kill table).

## D6 — Mass-radius from wiring — long-term

**Missing:** `R_s = 2M` (BM reduction: `k(M)` iff `R_s(M)` given).
Single GR input; derivation from wiring alone open.

## D7 — Kilonova radiative transfer — queued

**Missing:** POSSIS refinement; i-band not claimed (one-zone κ=10
over-traps). g-band verdicts robust; gap-KN ~1/yr O5 prediction stands.
Shed-leg hadronisation chemistry (`Y_e`, Sr II) open — folded here.

## D8 — Mass-ratio-dependent shedding + per-event Foucart baseline — queued (v5 review)

**Missing:** (a) `q`-dependent shed fraction `frac(q)` — current law is
equal-mass leading order `M_ej = 0.0168 M_tot` in all rows by construction
(`collapse.leg_shedding_ejecta`), so unequal-mass pairs at fixed `M_tot`
give identical ejecta; (b) per-event standard-model baseline via the Foucart
et al. (2018) `M_rem(q, C_NS, χ_BH)` formula evaluated over LVK posteriors
(`collapse.foucart_m_rem` stub, not yet implemented).

**Close criterion:** (a) `frac(q)` ∝ `4q/(1+q)^2` (or graph-derived
equivalent) normalised to the AT2017gfo point, with the brightness table
gaining a `q` column; (b) every O5 gap trigger auto-classified into
Category B (decisive: `m2 > 2.5` or Foucart `M_rem = 0` at 90%) vs Category A
(ambiguous gap+NS). Kill rule counts B only (see `observation-protocol.md`).

**Kill relevance:** sharpens the gap-KN falsifier so a bright gap+NS
disruption (Foucart-allowed) cannot be miscounted as killing NS EOS models.
