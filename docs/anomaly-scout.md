# Anomaly scout: what *new* anomalies could this model explain? (Sep 2026)

**Question:** after the five BU anomalies (gap, sub-minimum, super-TOV,
AT2017gfo, gap-kilonova prediction), what else is in reach?
**Short answer:** nothing cosmological — and that includes dark matter
(agreeing with the review). The reachable set is compact-object
structure and dynamics: glitches/FRBs (defensive must-do), NICER+GW
radius/tidal joint (needs the routing-stiffness derivation first), and
gap-competitor discrimination (protocol strengthening, no new claim).
Everything else surveyed here is explicitly **not** claimed, with reasons.

This note is exploration only: no paper claims, no new modules, no tuning.
Each candidate gets a 2026 status, what observable it needs, what the model
gives, and a verdict. Falsifiers stay armed; debts stay labeled.

## 0. The filter: what the model gives vs what a claim needs

The model today gives, per compact object or merger:

- leg count $k(M)$ (BS patch), exterior fraction $e_{ext}$, shed fraction;
- radial exponent $p$ (BU measured, BV predicted) and 2PN combination $c_{tot}$;
- ringdown damping $\alpha = 11.24$, PT overtone tower ($\sim 8\%$ vs Kerr),
  echo energy $\sim 10^{-160}$, tidal $k_2 \sim (l_p/R)^2 \sim 10^{-76}$;
- lensing/shapiro/redshift/Mercury at 1PN (GR-identical), dispersion
  quadratic-only ($E_{QG,2} = \sqrt{8}\,E_P$);
- kilonova ejecta $M_{ej}(M_{tot})$, band mags, O5 yield arithmetic.

It does **not** give: halo profiles $\rho_{DM}(r)$, relic densities
$\Omega_{DM}$ from a production mechanism, expansion/growth $H(a)$ /
$f\sigma_8$, particle cross sections, or formation rates from stellar
evolution. Rule used below:

- **Reachable in principle:** observable is a function of $(k, e_{ext}, p,
  shedding, leg dynamics)$ for individual objects or mergers.
- **Out of reach:** needs cosmology, populations-from-formation, or particle
  content the model has no sector for — unless a new sector is derived first
  (then it is a derivation project, not an explanation).

## 1. Dark matter: agree — do not claim (review point 6)

**2026 status.** The direction in the literature is DM $\to$ BHs, not the
reverse: Ge et al., JCAP 01(2026)052 — DM capture in main-sequence stars
induces $3$–$5\,M_\odot$ low-mass-gap BHs at LVK-consistent rates; PRL 135,
191401 (Nov 2025) — premature collapse from captured smaller (possibly
primordial) BHs makes both upper- and lower-gap BHs, with rapid spins from
stellar rotation as a GW231123 signature; transmutation-timescale papers
constrain $m_\chi$–$\sigma_{n\chi}$ from old MSPs/WDs surviving.

**Why we agree.** A DM claim needs $\rho_{DM}(r)$ (profiles, core/cusp,
lensing substructure, dwarf kinematics) **and** $\Omega_{DM}$ from a
production+survival story, plus direct/indirect bounds. The model gives a
microscopic description of compact objects — $k$-counts, $p$, shedding —
none of which is a density profile or a relic abundance. The $\sim 4\times
10^5$ g EMD remnant window (AR) is abundance-only: $\max\Omega \approx 0.12$
in a $\sim 0.4$-dex sliver, with no profile, no clustering, no formation
mechanism, and poltergeist-GW + $\Delta N_{eff}$ checks still open. It stays
on the record as a viability sliver, not an explanation.

**What would ever change this:** a derived halo profile from delocalized-leg
statics (AK concentration has no metric, no CMB/lensing pass — the gaps are
named there) **plus** a production mechanism with $\Omega$ arithmetic. Neither
exists. Until both do, dark matter is a non-claim — same box as H0/S8 (§5).

## 2. Lower-gap competitors: strengthen the protocol, don't expand the claim

The two 2025–2026 competitor channels both fill the $2.5$–$5\,M_\odot$ gap
without new compact-object physics:

| channel | mechanism | EM prediction for gap mergers |
|---|---|---|
| DM-capture collapse (Ge et al.) | endoparasitic BH eats host | BH–BH-like: **dark** |
| premature capture (PRL) | captured small BH triggers early collapse | BH–BH-like: **dark** (+ rapid spins) |
| this model (BU) | gap objects are low-$k$ graphs that shed legs | **must flash** ($m_g \sim 21$ at 200 Mpc, $\sim 1$/yr O5) |

The existing O5 protocol (`docs/observation-protocol.md`) already
discriminates: one gap kilonova kills the dark-merger channels for that
event class; ten clean non-detections kill BU instead. Recommended action is
editorial, not scientific: cite both competitors in the protocol as named
alternative hypotheses with distinct predictions. No new claim needed — the
test got sharper because the alternatives got concrete.

## 3. Tier 1 — in reach (one defensive, one offensive)

### 3a. Glitches, anti-glitches, FRB-magnetar coincidences — DEFENSIVE, must-do

**2026 status.** SGR 1935+2154: two large spin-up glitches bracketing an FRB
with an intervening rapid spin-down wind phase (Nature 2023–2024 series); a
large spin-down glitch ($|\Delta\nu/\nu| \approx 5.8\times10^{-6}$) followed
by FRB-like bursts + month-long pulsed radio (Nature Astron.); anti-glitches
now seen beyond magnetars, driving magnetism-powered starquake models
(arXiv:2607.12285) since gravity-only quakes can only spin up.

**Why it is Tier 1.** This is not optional anomaly-hunting — it is a
consistency debt. No-neutron-stars deletes crust quakes **and** superfluid
vortex unpinning, i.e. every standard glitch mechanism. The paper's pointer
("FRBs, magnetar flares, glitches as $e_{ext}$ leg-reconnection", §5-implications)
has zero code behind it. A model with no crust that cannot sketch a glitch
is incomplete on its own terms.

**What is needed:** order-of-magnitude leg-reconnection sketch hitting, with
no tuning: glitch sizes $\Delta\nu/\nu \sim 10^{-9}$–$10^{-5}$ (both signs),
glitch activity vs characteristic age, ms-duration $\sim 10^{39}$ erg FRB
energy scale, and the glitch–FRB temporal association (minutes–hours). Both
signs are the sharp edge: leg-reconnection must naturally increase *or*
decrease the effective moment of inertia, the way magnetic starquakes do.

**Honest risk:** if the sketch needs a tuned energy-per-reconnection or a
hand-set timescale to land in band, record it as open debt — do not claim.
Success criterion (pre-register before coding): sizes + energy + association
window from $(k, e_{ext}, s_{leg})$ with the same two shedding numbers or
fewer new ones, else no claim.

### 3b. NICER radii vs GW tidal deformability — OFFENSIVE, derivation-gated

**2026 status.** Live, genuinely bifurcated tension: GW170817 favors soft EOS
/ compact $R_{1.4} \approx 11$–$12$ km and low $\Lambda_{1.4}$; NICER
pulse-profile modeling returns $12$–$14$ km for the same mass range, with
new J0437-4715 posteriors in tension with older NICER data and hybrid EOSs
slightly preferred in some Bayesian comparisons — while EOS-insensitive
joint analyses (Huang et al.) find GW+NICER agreement with no twin-star or
phase-transition preference. This is a real anomaly candidate precisely
because the community has not converged.

**Why it is Tier 1.** The model's prediction is already staked and already
directional: compact low-$\Lambda$ graphs, no EOS to tune — the GW-soft side
favors it, large NICER radii challenge it, and the falsifier is armed
($\Lambda(1.4) > 500$ with small radius, or $R_{1.4} = 11$–$13$ km at $5\%$
unreproducible by routing stiffness, kills). This is the highest-value
derivation in the program: one $M$–$R$ curve + one $\Lambda(1.4)$ number from
leg-routing stiffness, confronted jointly with GW170817 + NICER.

**What is needed:** derive equilibrium size and tidal response from graph
statics (leg-routing cost under self-gravity / $k$-budget), not from an EOS.
Until that derivation exists, the NICER tension is a **target**, not an
explanation — claim nothing. Note the asymmetry that makes this a good bet
either way: the derivation either explains the soft side (and must then
survive NICER radii quantitatively) or dies on the record like remnant DM,
which is also progress.

## 4. Tier 2 — needs a new sector first (watch, don't claim)

- **Upper (pair-instability) gap + spins.** Effectively solved without us:
  Nature Astron. 2026 (GWTC-4) finds the gap edge at $44.3^{+5.9}_{-3.5}\,
  M_\odot$ in the low-spin 1G population plus a high-spin isotropic
  hierarchical population filling it (GW190521, GW231123 at $190$–$265\,
  M_\odot$ with $\chi \sim 0.8$–$0.9$). Our "continuous $k$, no gaps" is
  about *allowed* masses, not *formation* — a 1G formation gap is no
  conflict, but also no explanation. Competing would need a spin-population
  prediction from leg-ordering ($\chi_{eff}$ distribution from
  `spin_budget_fraction` + merger leg accounting). Not started; downgrade.
- **$r$-process without neutrons.** Shed legs "hadronize neutron-rich" is
  one clause with no nuclear sketch. A real claim needs: shed-leg to hadron
  chemistry, lanthanide fraction for the red component, and early
  enrichment in metal-poor stars without NSM delay times. Queued behind 3b.
- **kHz QPOs / magnetar giant flares.** No hook today. Only promote if a
  leg-oscillation frequency lands in band ($\sim 0.1$–$1$ kHz / $\sim 10^{46}$
  erg) with zero tuning — speculative until the 3a sketch exists.

## 5. Explicit non-claims (surveyed, rejected, with reasons)

| anomaly | 2026 status | why not us |
|---|---|---|
| Dark matter ($\rho_{DM}$, $\Omega_{DM}$) | DM $\to$ BH capture channels active | §1: no profile, no production, wrong direction |
| H0 ($7.1\sigma$) / S8 (DES $2.7\sigma$ vs KiDS $<1\sigma$) | H0 persists; S8 fractured by survey systematics | needs $H(a)$/growth sector; model is GR-identical cosmologically by construction |
| LRD / overmassive high-$z$ BHs | dying: gas-reddening + electron-scattering revise masses down $\sim 2$ dex to $10^{5-7}\,M_\odot$ ("black-hole stars", super-Eddington cocoons) | repo already flagged softening (AO); keep f_w tail rule, invest nothing |
| PTA nHz background (2 nHz dip, 16 nHz bump, 26 nHz knee) | explained by discreteness / loud binary, no new physics | honest null stands: EMD peak at GHz, $\sim 18$ orders above band |
| Ringdown deviations (GW250114: $\delta f_{220} = 0.02\pm0.02$, $\delta f_{221} \sim 0.09\pm0.29$) | Kerr holds; most stringent single-event GR test | benchmark to survive, not anomaly to explain; PT $8\%$ stays a LISA test |
| EHT shadows / lensing flux ratios / 511 keV / $g-2$ | unchanged | GR-identical sky / no particle sector (App S stands) |

## 6. Recommended next actions (smallest first)

1. **Glitch-replacement sketch (3a, defensive).** Pre-register size/energy/
   association targets, then order-of-magnitude leg-reconnection model. If it
   misses without tuning, log the debt — the no-crust model owes this
   calculation regardless.
2. **Routing-stiffness $M$–$R$–$\Lambda$ derivation (3b, offensive).** One
   curve + $\Lambda(1.4)$ vs GW170817 + NICER jointly. Decides whether the
   radius tension is our sixth anomaly or our second obituary.
3. **Protocol discriminator note (§2, editorial).** Add DM-capture and
   premature-capture as named dark-merger alternatives in
   `docs/observation-protocol.md`. Zero new physics, sharper test.

## 7. Ledger delta (this note)

- **Agreed (not derived):** dark matter non-claim (§1).
- **Downgraded:** upper gap (hierarchical solution), LRD/overmassive
  (gas-reddening revision) — scenario sketches only.
- **Promoted to Tier 1:** glitch/FRB replacement (debt), NICER+GW joint
  (derivation-gated target).
- **Unchanged:** PTA null, EHT null, H0/S8 out of scope, ringdown benchmark,
  remnant-window sliver, all armed falsifiers.
