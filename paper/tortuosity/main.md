# The Spatial Metric as Tortuosity: Deriving γ=1, Mercury, and the J0737 2PN Lock from Entanglement-Defect Scattering

**Tentative working draft v0.1 — branch `cursor/tortuosity-paper-aff8`, do not circulate.**
**L0+L1 only, no compact-object claims. No PDF; `.tex` and this `.md` are the draft.**

Model source: `docs/model.md` v0.6. No new numbers: every literal below is quoted
from `model.md`, `paper/v5/`, `docs/DEFERRED.md`, `src/bh_graph/`, or committed
`data/`. Open derivations D3/D4/D9/D10 stay open and labelled.

> **Draft status.** Working scaffold, not a submission. TODOs marked `[DRAFT-TODO]`.
> No L2 content (shedding, kilonovae, gap/BBH rates) appears by design.

---

## Abstract

We isolate the weak-field gravity core of an entanglement-graph model in which
a mass is a bundle of exterior legs and show that the spatial metric follows
from leg thermodynamics plus line-defect scattering. Three parts:

1. **No-go with a constructive exit.** Degree-biased and persistent walks on
   flux-conserved pileup give drift ∝ 1/r³ (slope ≈ −3; every smooth weight
   rule stays cubic, no-go −2.99), so bare graph diffusion cannot source
   Newton. Newton F = M₁M₂/r² (log-log slope to 1e−9, closed orbits,
   T² ∝ r³) emerges only when equipartition temperature over an r-dependent
   screen multiplies the Bekenstein entropy gradient. Ollivier–Ricci curvature
   with the canonical uniform measure is then radially negative in every
   tested configuration, attachment mode, and seed — the sign of attraction
   with zero tuning.
2. **Micro-derivation of the radial sector.** Legs of cross-section
   σ = 4ln2·l_p² and cost s_leg = ln2 per encounter make radial rulers
   tortuous: dl/dr = 1 + c·x, h = (1+c·x)², x = R_s/r, hence p = 2c and
   γ = 2c. Lattice Dijkstra/BFS on L³ defect media measures c ≈ 0.44–0.60
   with zero tuning (target 0.456, geometric 1/√π = 0.564), replacing the
   fitted 1/2 (preserved in history). Yields γ = 1 exactly, b_crit back to
   3√3M, full bending 4M/b, Cassini-grade Shapiro to 5%, GPS +5.29e−10,
   Pound–Rebka 2.55e−15, Mercury 42.99″/cy by direct integration.
3. **2PN lock.** Model c₁ = 3.36 vs GR 1.94 cancelled at p = 0.92 via
   c₂(p) = p(2p−1), w = 1.953, c_tot = 4.8693 vs GR 4.8695 (0.00σ fixed-M).
   Gradient-shell Ollivier–Ricci gives p = 0.913 ± 0.049 (80 graphs,
   N = 1020, SEM 0.0055, stacked 0.911, R² = 0.956; 0.93/0.94/0.91 at
   4k/8k/16k), landing J0737 at 0.1σ and B1913 at 0.01σ.

Jacobson closes at η = ln2/PATCH = 1/4, G = 1, conditional on Raychaudhuri
for leg bundles (open, D9). No β, no Kerr M₂/g_tφ/ISCO/QNM, no NICER, no
compact-object unification claimed. Falsifiers: p outside 0.92 ± 0.056,
finite linear LIV scale, |γ−1| ≳ 1e−5, UV OR sign flip.

---

## 1. Why a second paper

V5 is an L2 bet (one k ∝ M² family, AT2017gfo calibration, gap kilonovae
~1/yr vs ≤0.3/yr standard, ten-miss kill rule). Its gravity sections are a
~2-page credibility battery for that astro claim.

This draft inverts the priority: L0 (P1–P4) + L1 imports (thermodynamics,
equivalence, OR limit) already entail diffusion-ruled-out → Newton-with-sign
→ light → Mercury → measured 2PN lock, with no shedding, no kilonova, no
q-law, no rates. Per `model.md` §9, killing L2 must not kill L0/L1 — this
paper makes that independence checkable.

New relative to v5 main text:

- perwalk no-go (−2.99) as a theorem about weight rules + labelled μ(χ) escape;
- BV scattering derivation of c ≈ 0.44–0.60 (p = 2c, γ = 2c) as the spine,
  with hard/soft/mixed modes, Boltzmann/Dijkstra ladder, graph-distance
  re-analysis, pop scan;
- OR sign + UV spot-check as a falsifier, not a remark;
- 2PN lock with full N-scaling (1020 → 16000), CSR cross-check (0.9107 vs
  0.9134), local-p turnover (0.63–0.69 → 1.26–1.46), pre-registered hiding
  analysis for bending/Mercury 2PN pieces;
- Jacobson given-I1b with D9 fenced (no double-counted 1/4).

`[DRAFT-TODO: dependency diagram L0 → L1 ⇒ §3–§6, D3/D4/D9/D10 as open inputs.]`

## 2. What is assumed vs derived

Planck units G = c = 1 unless stated. N = interior nodes, k = exterior legs,
e_int/e_ext ∈ [0,1].

**L0 inputs.** P1 (almost-perfect all:all K_N, k ≪ N²); P2 (cut size bounds
entropy); P3 (linear toy e_int + e_ext ≤ 1, k = K_max(1−e_int), plus exact
CKW frontier on 25-point grid, strictly below linear, x+y = 0.70 at t = 0.3,
exterior one-tangle peak 0.5; k → 0 baby-universe limit); P4 (OR measure
uniform, idleness p = 0.0; e_int-weighted alternative degrades p 0.94 → 0.84).
Used theorems: T1 (diameter exactly 1, gap N, 1-step SI cover) and T2
(t_* ≈ log₂N/log₂(1+p), exactly log₂N at p = 1 vs ballistic N/v; 25 trials,
N = 8…128).

**L1 inputs used.** I1a (saturation, η_vN = ln2 by definition; BN S/k
constancy < 0.8%); I1b (S = A/4; matching k·ln2 = A/4 ⇒ A = 4ln2·k·l_p²,
PATCH = 4ln2); I2 (k legs need k patches; N buys no area); I3 (k(M) via BM
reduction k(M) ⟺ R_s(M); circle is exactly R_s = 2M, open D6); I4a
(equipartition T(r) = M₁/2πr²); I4b (Bekenstein dS = 2πM₂dr, F = T·dS/dr);
I5 (potential → g_00); I6a (heat-kernel, cited, load none); I6b (OR → Ricci
with P4 measure, load-bearing); I6c (Raychaudhuri, open D9, gates nothing in
T8–T11); I7 (gap/crossover heuristics).

**Not imported.** No F1–F6 as inputs; F1–F4 appear only as labelled targets
(§6, queued D3/D4). No Kerr multipoles, no NICER/Λ, no kilonova physics.

**Vacuum note (v0.5/v0.6).** P0 (all:all vacuum) retired for P0′ (relaxed
isostatic 2D fabric, ⟨z⟩ = 4); K_N is the maximum-tension extreme, T1–T3
untouched. §5 treats legs as line defects in ambient fabric and is compatible
with either kinematics. D10 (d-dip + tension→κ; D10a tense-plug pin: bare
shortest-path rejected for tense regions) is compatibility, not dependency.
`[DRAFT-TODO: expand once emergent_dim N-scan lands.]`

| item | value | status / module |
|---|---|---|
| P1–P4, I1 matching, I2–I5, I6a/b | wiring, 4ln2, T·dS/dr, g_00, OR limit | postulated (I6a cited) |
| OR sign | negative, every config/seed | measured, zero tuning (`weakfield`) |
| perwalk no-go | 1/r³, −2.99 all smooth rules | measured (`perwalk`) |
| Newton chain | F = M₁M₂/r², slope 1e−9 | derived given I4a+I4b (`entropic`) |
| c (BV) | 0.44–0.60 vs 0.456 / 0.564 | measured, zero tuning (`uvscatter`) |
| p (BU) | 0.913 ± 0.049, SEM 0.0055 | measured (`orici`/`sinkor`) |
| β(N), w, κ→c₂ | 1.5…0.74; 1.953; p(2p−1) | fitted/solved/ansatz (D3/D4) |
| Raychaudhuri | focusing for leg bundles | open (D9) |

## 3. Diffusion cannot be gravity; temperature with the right sign can

**No-go** (`perwalk`, Fig. `fig57_perwalk.png`): hop-budget dilation √(1−v²)
(linear 1−v excluded by 3-4-5 triangle), degree-biased hopping on d ∝ 1/r²
pileup → drift ∝ 1/r³ (slope ≈ −3); all smooth weight rules cubic (−2.99).
1/r² from pure statistics would need 1/r pileup, forbidden by flux
conservation. μ(χ) escape (1−μ = c√χ) reaches −1.95 ≈ −2 modulo labelled √χ.

**Newton by exact algebra given I4a+I4b** (`entropic`, Fig. `fig43_newton.png`):
F = M₁M₂/r² by exact chain multiplication (`test_chain_multiplies_to_newton`,
`==`); slope to 1e−9, closed leapfrog orbits, T² ∝ r³. Link-flux ∝ 1/r² would
give 1/r³ as energy; T-factor over r-dependent screen corrects to 1/r² (both
implemented, checkable).

**Sign, zero tuning** (`orici`, `weakfield`, Fig. `fig59_weakfield.png`): OR
with P4 measure radially negative everywhere tested. UV spot-check
(`uvscatter.uv_or_sign`) on defect-pierced graphs must stay negative — flip
kills attraction where χ ~ 1 (falsifier, §8).

## 4. Light: bending, Shapiro, chroma, isotropic dies

(`lensing`, `chroma`, `shapiro`, `bcrit`, `redshift`; Fig. `fig49_lensing.png`.)
c_eff = 1−x Fermat → full 4M/b (naive 2M/b bet lost on record). Chromatic
extension uses phase 1/24, not group 1/8: r-independent factor drops out of
Born → 1e−56 (optical) to 1e−32 (10 TeV). Shapiro R_s·ln(4r₁r₂/b²) to 5%,
Cassini γ = 1. Redshifts z = M(1/r₁−1/r₂): GPS +5.29e−10, Pound–Rebka
2.55e−15, no new parameters. Congestion freezing c_eff → 0; α = 1 matches
dr/dt = 1−R_s/r exactly (calibration), α = 2 qualitative. Redshift robust to
profile; exact exponent open.

Isotropic b_crit = 8M is 54% above GR 3√3M, excluded by EHT ~3.6σ — the
isotropic reading dies, not the core (transverse propagation unimpeded, as
all:all demands). Purely temporal models give 0 vs 43″/cy: light never needed
g_rr, orbits do (§5).

## 5. Spatial sector from line-defect scattering (spine)

(`uvscatter`; Figs. `fig70_uv_c.png`, `fig71_uv_pop.png`.) BH fitted 1/2 →
derived: legs as radial line defects σ = 4ln2·l_p², cost s_leg = ln2 per
encounter (BN). Dilute tortuosity:

> dl/dr = 1 + c·x, h = (1+c·x)², x = R_s/r = √χ, χ = kσ/4πr² (identity).

PPN g_rr = (1+U)^{2p} ≈ 1+p·x gives p = 2c, γ = 2c. Pop at χ = 1
(k_crit = 4πr²/σ, BK) appears as graph disconnection — horizon without metric
input. BU/BT IR anchors are comparison targets only, never inputs.

**Modes on L³:** hard (BFS, c ~ 1.2, overshoots); soft (Dijkstra Gaussian
w = 1+α·exp(−d²/2r_e²), α = ln2, r_e = √(σ/π), c ~ 0.43–0.54); mixed
(0.75·r_e hard core + soft, dilute c ~ 0.5, rise before pop, disconnect at
k ~ k_crit). Cross-checks: Boltzmann/MFP analytics, MC ray + lattice
transport (Boltzmann → Dijkstra as T → 0), bridge ladder (point 0 / line 1 /
area 2; BU β = 1.24 between line- and area-like). Straight-ray bounds Dijkstra
3–6× above (no-detour); drifted finite-T transport recovers Dijkstra ~2× at
all T. Graph-distance re-analysis (r_phys = d_clean/T₀) agrees with
Euclidean-r c (no background coordinate needed).

**UV running:** p(s) = 2c(s), s = r−R_s, flat p ~ 1 dilute, then c rises before
paths vanish — replaces fitted p_adj(s). Target: shellscale local-p turnover
0.63–0.69 → 1.26–1.46. `[DRAFT-TODO: overlay BV running-p with shellscale.]`

**History preserved:** BH fitted 1/2 (unique, labelled) → BV derived 0.44–0.60
(zero tuning). Interval honestly broad (γ ≈ 0.88–1.20 at ends); tighten to
±0.03 before submission (§8).

## 6. Mercury to J0737 with no new knobs

**Mercury** (`strain`, Fig. `fig58_strain.png`): dl = (1+√χ/2)dr → h = (1+x/2)²
≈ 1+x, γ = 1, c_eff = √(f/h) = 1−x, b_crit → 3√3M. φ-domain complex-step:
GR 42.99″/cy and model 42.99″/cy; flat-h 28.7″/cy (PPN 2/3). Peel-off
(ours−GR)/GR = −0.75·M/a: 4.1% at 20M → 2e−8 at Mercury. PPN: γ = 1 claimed,
β unresolved/not quoted, α₁,₂/ξ/Nordtvedt untouched.

**2PN lock** (`pulsar`, `orici`, `sinkor`, `shellscale`; Figs.
`fig67_orici_p_fit.png`, `fig66_pulsar_2pn.png`): g_rr = (1+U)^{2p},
c₂ = p(2p−1), c_tot = c₁+w·c₂, w = 1.953, GR 4.8695. Model c₁ = 3.36 vs
1.94 (73% excess) cancels at p = 0.92 (c₂ = 0.7728, c_tot = 4.8693,
0.00σ fixed-M). Self-consistent R+ω̇ → M: ΔM = −11.2 ppm naive (−4.5 ppm
with GR g_rr), Δsin i = 3.7e−6; J0737 16.899323(13) deg/yr at 0.1σ,
sin i 0.36σ; B1913 0.01σ. Shells p_adj(s) = 0.85+0.015s, 8–10 shells, exact
EMD, n ∝ r^β(N): 1.5@300, 1.28@600, 1.24@1020, 0.99@4k, 0.87@8k, 0.74@16k
(log-linear, recalibrated per N, drift faster than 1/N). p = 0.913 ± 0.049
(80 graphs N = 1020, ~545 s Floyd+LP; SEM 0.0055, stacked 0.911, R² = 0.956,
80/80 ok, range 0.79–1.05); N-scale 0.9315 ± 0.0032 (4k), 0.9382 ± 0.0030
(8k), 0.9137 ± 0.0022 (16k); CSR 0.9107 vs 0.9134. Distance to 0.92: 0.007
(0.24σ in p, ~0.09σ in ω̇), 5× margin (0.0055 vs 0.028). Flat p = 0.49 is
−10σ dead. Bending/Mercury 2PN pieces below VLBI/astrometry (pre-registered).

**Still fitted/solved/ansatz:** slope 0.015 (F1 fitted); β(N) per N (F2,
D4 queued); w = 1.953 (F3 solved, D4 queued); c₂(p) = p(2p−1) (F4 ansatz;
power-law R² 0.91 vs 0.81 but cross-applied c₂ 0.82 vs 3.14, open D3).
Measure postulated in P4, so only the map is open.

## 7. Jacobson closure, conditionally

(`jacobson`, Fig. `fig62_eta.png`.) Complete except Raychaudhuri: dQ = ε·dk,
T = κ/2π (input), dS = ln2·dk, Clausius ε = κ·ln2/2π, measured
η = ln2/PATCH = 1/4 → G = 1 (`clausius_leg_energy`,
`measured_eta_closure`, tested). Given I1b, no second 1/4 (I6c guarded).
T8–T11 independent of I6c. D9 close criterion: derive (not cite) focusing
for fronts on leg networks (AT congestion seed). Gates nothing in §3–§6.

## 8. Falsifiers, open maps, vacuum compatibility

| wire | threshold | now | timeline |
|---|---|---|---|
| 2PN exponent | p outside 0.92 ± 0.056 (N = 1024 class, 80 graphs) | 0.913 ± 0.049, 5× margin | held to 16k; blind next |
| linear LIV | finite E_QG,1 or Δt ∝ E | Fermi kills linear; we predict ∞ by k↔−k | archival + CTA |
| PPN γ | \|γ−1\| ≳ 1e−5 (Cassini/BepiColombo) | γ = 1 (BV median) | BepiColombo |
| OR sign (UV) | radial κ ≥ 0 on defect graphs | all-negative held | each BV run |
| tortuosity c | dilute c outside 0.456 ± 0.10 fixed-L | 0.44–0.60, broad pass | tighten ±0.03 |
| lab quench (context) | grid→all:all t* ratio < 1.3 (predict 2–3×) | untested | when run |

**Blind protocol (P0 pre-submission).** Pre-register β(N), slope, seeds,
shells, dilute-χ cut; run N = 16000 once; no post-hoc β. Pre-register L,
k-grid, r_e, α = ln2, dilute estimator for BV; report c per mode + orientation
spread. `[DRAFT-TODO: two pre-registration sheets as appendices.]`

**Open maps touching this paper.** D3 (κ→c₂), D4 (β(N), w; Damour–Schäfer from
wiring), D6 (R_s = 2M), D9 (Raychaudhuri). D1/D2/D5/D7/D8 do not touch it. D10
(d-dip + tension→κ; D10a tense-plug: bare shortest-path rejected for tense
regions) is compatibility: D10b costs must reproduce P4-p and §5-c where both
apply. Closing rule: output the number/location, never insert it (precedent:
44 M☉ refused).

**Non-claims.** Not UV-complete QG. No β/α₁,₂/ξ/Nordtvedt. No linear LIV
(finite E_QG,1 kills legs). No Kerr M₂/g_tφ/ISCO/QNM from graph. No NICER/Λ.
No 44 M☉ graph feature (positive null). Dead on record, kept visible:
isotropic b_crit = 8M, naive γ = 2, linear LIV, flat p = 0.49.

## 9. Conclusion

Almost-perfect all:all wiring + borrowed thermodynamics give: diffusion ruled
out (1/r³ no-go), Newton with sign (1/r² + negative OR, zero tuning), light
and redshifts to Cassini/GPS with isotropic dead, spatial sector from ln2
scattering (c ≈ 0.44–0.60 ⇒ p = 2c, γ = 2c), Mercury 42.99″/cy, J0737 0.1σ
via measured p = 0.913 ± 0.049 — L2 never invoked. Price: four imports, one
measure, three open maps, one broad interval. Reward if blinds hold: first
emergent model with quantitative g_rr micro-derivation + 2PN number. If L2
fails, v5's title reverts and this core stands; Table above decides.

**Methods.** Shells p_adj(s) = 0.85+0.015s, exact EMD, n ∝ r^β(N); p from
\|κ\| ∼ r^{−p} + stacked; 2PN Iorio direct+total, R+ω̇ → M; BV L³
hard/soft/mixed Dijkstra/BFS, dilute median + regression, MC ladder,
graph-distance; Fermat c_eff = 1−x; φ-domain complex-step geodesics. Seeded;
tolerances in-test. `[DRAFT-TODO: supplement S1–S6 once main stabilises.]`

**Reproduce.** Code MIT (`src/`, `scripts/`, `tests/`, `app.py`); text/figs
CC BY 4.0. `pip install -e .`, `pytest tests/ -q`,
`python scripts/generate_figures.py`, `streamlit run app.py`. Model source:
`docs/model.md` v0.6.

---

## References (working set; mirrors v5 + PPN/OR/2PN)

- V5 draft, `paper/v5/main.tex` + supplement.
- Sekino–Susskind JHEP 08; Van Raamsdonk; Maldacena–Susskind; Bekenstein;
  Hawking; Coffman–Kundu–Wootters; Kramer et al. (J0737 16.899323(13));
  Weisberg–Huang (B1913); Verlinde; Jacobson; Will (PPN); Bertotti et al.
  (Cassini); EHT; Fermi/GRB 090510; Ollivier (JFA 2009); Damour–Deruelle /
  Damour–Schäfer (2PN); Iorio (2PN periastron).
