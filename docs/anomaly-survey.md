# New-anomaly survey: what this model should and should not chase (Sep 2026)

**Question:** we are looking for new anomalies to explain. Which ones are
natural for this model — and which would be patches?

**Short answer:** most "big anomalies" in the news are either already owned
(lower mass gap), already explained by standard astrophysics (upper gap,
little red dots, FRB rotation jumps, magnetar QPOs, glitches), GR
confirmations (GW250114 nonlinear ringdown), nulls the model already holds
(LIV, LHC, EHT), or out-of-scope cosmology (Hubble, S8, PTA background,
lensing substructure). The genuine in-scope opportunities are **precision
frontiers, not anomalies**: routing-stiffness M–R–Λ, isolated gap lenses in
Gaia DR4, the armed gap-kilonova rate, α-universality monitoring, and the lab
scrambling hierarchy. Machine-readable table + scoring:
`src/bh_graph/anomaly_survey.py` (11 tests).

---

## 1. Scope: entanglement → compact objects → geometry

The model derives, from interior all:all wiring + exterior legs `k`:

- fast scrambling, Page/QES/island, Hayden–Preskill, Kerr budgets;
- weak-field gravity to 1PN (Newton, Kepler, redshift, bending, Shapiro,
  γ = 1, Mercury) + 2PN cancellation at `p = 0.92` (BU, BV to N = 16000);
- horizon pop at `k_crit`, leg-shedding kilonovae, α = 11.24 ringdown damping.

It has **no**: cosmological sector (no Friedmann-from-legs, no H0 map), no
formation/population mechanism (no mass or spin functions), no
magnetosphere/crust/plasma physics, no nonlinear-GR dynamics (the QNM sector
is a calibrated toy: τ fitted to GR, Pöschl–Teller stand-in, footprint
corrections 40+ orders below sensitivity).

**Naturalness rule (tested in `naturalness_score`):** a candidate is natural
only if it can be addressed with in-repo machinery (`k`, patch `4 ln 2`,
`s_leg`, `p`, leg-shedding, α) plus **zero** new postulates. Each missing
sector/derivation adds one to `mechanism_distance`; score starts at
`10 − 3·distance` and is capped by tier. Tier 2 (in-scope opportunity) is the
only actionable tier.

## 2. Verdict on Hubble tension (§5 of the review): agree — do not touch

> "I don't see a clean route from your current model to H0 … You don't
> currently have a cosmological sector … Trying to explain it now would look
> like adding a cosmological patch to an otherwise tightly scoped model."

**Agreed, on all three points.** Concretely (`hubble_scope_check`):

1. No Friedmann expansion from leg thermodynamics exists in-repo (AB/X
   translate a *given* ΛCDM background into wiring language; they do not
   derive expansion).
2. No cosmological sector: no growth rate, no distance ladder, no `H0` map
   from any leg quantity to km/s/Mpc.
3. Mechanism distance 3 — the same as inventing a new model.

The tight scope is the model's strength (every claim ships with code, tests,
falsifiers). A cosmology patch would dilute exactly that. The same refusal
covers S8, DESI evolving dark energy, and CMB anomalies: one missing sector,
same verdict.

## 3. Already owned / already held (do not relitigate)

| item | status Sep 2026 | model position |
|---|---|---|
| Lower mass gap (GW230529 2.5–4.5 M☉, GW190814 2.6) | gap filling confirmed; GWTC-4 finds no dearth 3–5 M☉, peak ~8–10 M☉ | **owned (BU)**: continuous `k`, gap must flash |
| HESS J1731-347 (~0.77 M☉) | still debated (quark/hybrid/slow-cooling NS all fit) | owned as low-`k` tail; note the degeneracy, not uniqueness |
| Heavy pulsars (J0740 2.14, J0952 2.35) | EOS + NICER converging with systematics understood | owned (more legs, no EOS) |
| AT2017gfo (0.05 M☉ blue+red) | anchor event | owned (0.047 M☉ shed, `m_g` 18.0 vs 17.5) |
| LIV (LHAASO GRB 221009A) | linear `E_QG,1 > 5×10^19` GeV, quadratic `> 10^13` GeV — nulls | **held**: linear forbidden by symmetry, quadratic `√8·E_P` safe by ~10^6–10^7 (`liv_margins_lhaaso`) |
| LHC thermal BHs, EHT shadows, PBH broad-DM | nulls / excluded on record | held (T, V, AE/AR) |

## 4. Tempting but standard explanation wins (survive, do not claim)

**Upper (PISN) gap.** GWTC-4 confirms the edge at ~44 M☉ *and* its
astrophysical fill: a high-spin isotropic population occupies the gap =
hierarchical mergers, with a nuclear-rate (`12C(α,γ)16O`) link. Continuous
`k ∝ M²` predicts **no** 1G edge (`upper_gap_leg_ratio`: `k(44)/k(10) = 19.6`,
feature 0.0) — claiming the upper gap would *mispredict* the confirmed
cutoff. The model's correct posture is survival: hierarchical mergers create
legs (Q/W pipeline), the edge itself is stellar astrophysics.

**Little red dots / overmassive high-z BHs.** Softening fast toward AGN
cocoons/envelopes: electron-scattering line cores revise masses down ~2 dex
to 10^5–10^7 M☉, super-Eddington envelopes explain the red colors and X-ray
weakness. AO/AQ sketches already label the missing formation story +
constraint pass. Keep them sketches; do not promote.

**GW250114 nonlinear ringdown.** First quadratic QNMs at 3σ, Kerr to a few % —
the most stringent single-event GR confirmation to date. The model's QNM
sector cannot touch this (no nonlinear dynamics). Survive via α = 11.24
catalog monitoring (`monitor.py` + `alpha_cat`); do not claim
overtones/quadratic modes.

**Magnetar QPO intermittence/drifts, FRB RM jumps, pulsar glitches.** All
three now have working standard accounts: nonlinear axial-axial-polar mode
coupling (QPO appearance/disappearance + drifts), magnetar flare ejecta (RM
spike to ~2000 rad/m² without DM excess), superfluid vortex avalanches +
hydrodynamics (power-law sizes, cutoffs, 1% reservoir fraction). The model's
one-line "leg-reconnection" pointer has no crust, no plasma, no reservoir,
no waiting-time prediction — mechanism distance 3, no quantitative observable.
Keep as pointers, write no sections.

## 5. Genuine in-scope opportunities (ranked)

All tier-2, mechanism distance ≤ 1, each with a quantitative near-term test:

1. **Routing-stiffness M–R–Λ for low-k graphs (distance 1, highest priority).**
   The one queued derivation that independently kills or confirms
   no-neutron-stars. Targets (literature inputs, `lambda_target_table`):
   `R_1.4 = 11–13` km, `Λ_1.4 = 100–600`, and the EOS-insensitive
   `Λ_TOV ≥ 9.2` bound separating max-mass NSs from BHs (`Λ_BH = 0`).
   The model predicts compact, low-Λ objects; it must compute `Λ(k)` from
   graph response and show where low-`k` graphs land. Until then the NICER +
   GW tidal flank is open — this calculation outranks any new anomaly chase.
2. **Isolated gap lenses in Gaia DR4 (distance 0).** DR4 (late 2026) publishes
   astrometric time series: mocks predict ~300 events, ~8 stellar BHs.
   Same zero-knob continuity argument as BU, applied to isolated lenses:
   with `f_gap ~ 0.15` from the GWTC low-mass decline, `P(≥1 gap lens) ~ 0.73`
   (`gap_lens_probability`) — DR4 is informative. Gaia18ajz (4.9 M☉
   candidate) is a preview. Prediction: no 3–5 M☉ dearth in the DR4 remnant
   mass function after selection modeling.
3. **Gap kilonova rate/shape (distance 0, already armed).** ~1/yr O5 vs
   standard ≤0.3/yr; 10 clean non-detections kill. Refinement path (no new
   physics): unequal masses, spin dependence, POSSIS colors to fix the faint
   `i`-band. Highest sky leverage per unit work.
4. **α-universality catalog monitoring (distance 0).** Re-run the hierarchical
   `δτ_220` monitor on GWTC-4/4.1 + GW250114. The model fixes α = 11.24 with
   no freedom; per-event deviations outside [9.0, 12.4] kill the
   horizon-relaxation identification. Cheapest strong-field check.
5. **Lab scrambling hierarchy (distance 0).** Same-protocol all:all vs grid
   quench at 36+ qubits, predicted ratio 2–3×, kill if < 1.3. Cheapest
   kill-or-confirm overall; no sky needed (Quantinuum-class hardware).

## 6. Explicit do-not-touch list (tier 0)

Hubble H0, S8 / DESI dark energy, PTA nanohertz amplitude/slope (needs SMBH
population + environmental physics), strong-lensing flux-ratio anomalies
(needs subhalo population + formation story; lensing is achromatic GR by
construction), g−2/flavor (no particle sector). Each needs ≥3 new
ingredients — a new model wearing this one's name.

## 7. Recommended next actions

1. Derive `Λ(k)` (routing stiffness) — the single highest-value calculation;
   it converts NICER + GW tides from an open flank into a second kill-wire
   beside gap kilonovae.
2. Write the Gaia DR4 gap-lens prediction note (selection-aware, `f_gap`
   from GWTC-4 low-mass shape) so it is on record *before* DR4 lands.
3. Refresh `monitor.py` bounds on GWTC-4/4.1 + GW250114 medians.
4. Keep FRB/glitch/QPO/H0 as refused-with-reasons (this note), not as
   roadmap items — scope discipline is what makes BU falsifiable.

*Refs (Sep 2026 status): GWTC-4 PISN-edge + hierarchical fill (Nature Astron
2026, arXiv:2509.04637); GW230529 discovery (LIGO DCC P2300352); low-mass
spectrum no-gap + 8–10 M☉ peak (ApJ 2026 ae581e); GW250114 spectroscopy
(PRL 2025 + nonlinear-voice Jan 2026, Bayes 74, 3σ); LRD cocoons (Nature 649,
574–579; ApJ 2026 adea66/ae4101); NICER+χEFT convergence (ApJ 2024 ad5f02,
A&A 2026 aa59810-26); Λ_TOV ≥ 9.2 scaling (Jun 2026); nonlinear tides bias
(CQG 2026 ae76b5); LHAASO LIV (CPC Dec 2025, DisCan); magnetar QPO coupling
(ApJ 2025 adceee); FRB 20220529 ejecta (A&A 2025 aa54550-25); glitch
superfluid hydro (MNRAS series); PTA landscape (Nat Commun 2025 65450-3,
arXiv:2603.13643); lens flux WDM/FDM (JWST MIRI survey Aug 2026, cusp-FDM
Jan 2026); Gaia DR4 mocks (A&A 2025 aa51046-24, arXiv:2609.10705).*
