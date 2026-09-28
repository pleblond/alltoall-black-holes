# The model, stated first (v0.2)

**Status:** draft, model-first companion to the v5 paper. No new physics, no new
numbers: every value below is quoted from `paper/v5/main.tex`,
`paper/v5/supplement.tex`, `docs/DEFERRED.md`, the cited `src/bh_graph/`
module, or committed `data/` artifacts. Where the code and the paper disagree,
the code wins and the disagreement is flagged.

**v0.2 audit release.** Every symbol → module → test citation resolved; every
load-bearing literal recomputed or test-pinned (suite: 398 collected,
396 passed, 2 torch/GPU-only skipped); kill wires aligned across paper,
protocol, and code. Fixes vs v0.1: TeV absolutes corrected to post-BS values
(v5 prose preserves pre-BS numbers with identical ratios — flagged
paper-side), Kerr leg normalization stated explicitly, `pheno` restored to the
module map, D-tag collision disambiguated. Two code-side flags (comment-only
notes added, zero behavior change): `evaporate()["radius"]` legacy convention,
`kerr_newman_k` patch-1 units. See §8 provenance layers and §9.

**What this document is:** the definition of the model — primitives, postulates,
theorems, calibrations, open maps, and non-claims — in that order. Tests,
figures, and measurements are cited as *evidence about* the model, never as its
definition.

**What this document is not:** a tutorial (see `docs/model-explained.md`), an
observation plan (see `docs/observation-protocol.md`), or the paper (see
`paper/v5/`). It does not re-derive anything; it states what is assumed, what
follows, and what is still missing.

**How to read it:** three layers, in hardening order.

- **L0 — Graph kinematics.** The robust core. Almost everything here is a theorem
  of the wiring, not a fit.
- **L1 — Spacetime interface.** The robust core plus a small list of explicit
  imports from GR/thermodynamics. All weak-field gravity and QI results live here
  *conditionally* on those imports.
- **L2 — Compact-object phenomenology.** Calibrated, not core. Fitted numbers,
  a solved weight, one ansatz map, and one extrapolation prescription. Killing L2
  must not kill L0/L1.

Open derivations (D1–D8 in `docs/DEFERRED.md`) are fenced in §5 and referenced
from the exact postulate or theorem they would promote. Nothing in §2–§4 depends
on them silently.

Conventions: Planck units `G = c = 1` unless stated; `l_p` written explicitly at
physical interfaces. `N` = interior node count, `k` = exterior leg count,
`e_int ∈ [0,1]` = interior entanglement fraction, `e_ext ∈ [0,1]` = exterior
budget fraction. Status words follow the S1 audit: **input** (assumed),
**fit** (calibrated), **measured** (output of code), **derived** (follows from
stated premises).

---

## 1. Primitives (L0)

These are undefined terms. Everything else is built from them.

| Symbol | Meaning | Notes |
|---|---|---|
| node | indivisible Planck-scale element | lives at `~1e-35` m; no internal structure |
| edge | unit of entanglement between nodes | cut edge-count bounds entanglement entropy across the cut |
| `G_N` | interior graph on `N` nodes | the object under study; boundary between interior and ambient is the cut |
| ambient graph | the rest of the network | exterior legs terminate here |
| `k` | exterior leg count (edges crossing the cut) | the model's central quantity; `k << N²` for black holes |
| `e_int`, `e_ext` | interior / exterior entanglement fractions | normalized wiring budgets; see P3 |
| `K_max` | max exterior budget (normalization) | toy-level; physical predictions must be `K_max`-independent where claimed |
| `H_graph,k`, `H_leg` | graph / leg Hilbert spaces | used only where unitarity is explicitly constructed (qubit toy, see T7); no general graph Hamiltonian is postulated |

What is **not** primitive: mass, radius, temperature, metric, area. Those enter
in L1 as interface maps, each labeled.

---

## 2. L0 postulates and theorems

### P1 (wiring postulate). Black-hole interiors are almost-perfect all:all graphs.

The interior `G_N` is the complete graph `K_N` up to a sparse exterior:
`N(N-1)/2` internal edges, `k << N²` exterior legs. "Almost" is the entire
observable content: area, temperature, and radiation live in the failure to be
perfect. (`graphs`, `scrambling`.)

### P2 (edge postulate). An edge is a unit of entanglement; cut size bounds entropy.

Entanglement across any cut is bounded above by the edge count across it.
No specific state is postulated at L0; specific families appear only as
witnesses for monogamy (see T3).

### P3 (monogamy postulate, two versions).

- **Linear toy** (used for bookkeeping): `e_int + e_ext ≤ 1`. Remaining legs
  `k = K_max(1 − e_int)`. (`horizon.monogamy_frontier`, `exterior_budget`.)
- **Exact frontier** (the real constraint): the Coffman–Kundu–Wootters inequality
  `τ_A|BE − C²_AB − C²_AE ≥ 0`, verified on a 25-point grid on the explicit
  state family `|ψ(θ)⟩ = cosθ|Φ+⟩_AB|0⟩_E + sinθ|00⟩_AB|1⟩_E`. The exact frontier
  lies strictly below the linear bound (e.g. `x + y = 0.70` at `t = 0.3`; exterior
  one-tangle peaks at `0.5`, not `1`). (`monogamy`.)

At `e_int → 1`, `k → 0`: the subgraph decouples as a closed graph — the
**baby-universe limit**. Black holes live in the almost-perfect corner
`e_int ≲ 1`, small nonzero `k`. (`horizon.is_baby_universe_limit`.)

### T1 (no interior distance). `K_N` has diameter exactly 1 at every `N`.

Mean distance 1, spectral gap `N`. Deterministic SI/operator spread covers `K_N`
in 1 step for any `N`, versus `~N/2` for a chain `P_N`, `~2√N` for a
`√N×√N` grid, and `~log N` for a random 3-regular expander. **Derived**, zero
tuning. (`graphs`, `scrambling`.)

### T2 (fast scrambling). Finite-speed circuits give `t_* ~ log N` on all:all.

One 2-qubit interaction per qubit per step with random perfect matching
(all:all) versus dimer covering (chain) and per-encounter success `p` gives
`t_*(N) ≈ log₂N / log₂(1+p)`, exactly `log₂N` at `p = 1`, versus ballistic
`t_* ~ N/v` on the chain. Measured over 25 trials per `N`, `N = 8…128`; the
chain is already `> 5×` slower at `N = 64`. OTOC form `C(t) ~ e^{λt}/N`,
`t* = logN/λ`. **Derived** from P1 plus the stated circuit rule.
(`circuits`, `otoc`, `krylov`, `syk`, `bigsyk`, `sparse24`.)

### T3 (decoupling). Maximal interior entanglement forces exterior decoupling.

At `t = 0` the witness family has interior concurrence 1 and exterior tangle 0
(baby-universe endpoint); at `t = π/2` it is fully product `(0,0)`. This is a
theorem of quantum mechanics applied to the wiring, not an extra postulate.

### Explicitly not in L0.

No Hamiltonian, no graph dynamics, no Lorentz invariance, no mass map, no
continuum limit. Any result needing those lives in L1 or L2 and says so.

---

## 3. L1: the spacetime interface

L1 adds a short list of imports. Everything in this section is of the form
"**given** L0 + imports I1–I7, **then** T4–T14." The imports are the price;
the theorems are what the price buys.

### Imports (inputs, all labeled)

| ID | Import | Status | Source |
|---|---|---|---|
| I1 | Patch postulate: each exterior leg costs `4ln2 ≈ 2.77` Planck patches; `A(k) = 4ln2·k·l_p²`, `R(k) = √(A/4π)` | **derived** (BS: from measured von Neumann leg entanglement `η_vN = ln2` per leg with Planck-bits equipartition, closing the Jacobson chain at `G = 1`; legs saturate) | `horizon`, S1 |
| I2 | Embedding rule: `k` legs need `k` Planck patches of ambient surface; interior size `N` buys no area | postulate (Bekenstein–Hawking / LQG-puncture picture in graph language) | `horizon`, `micro` |
| I3 | Mass map `k(M) = A/4ln2·l_p² = (4π/ln2)M²/l_p² ∝ M²` (Schwarzschild units), i.e. `k = 1.51e77(M/M☉)²` | **input** (GR-consistency, not derived). BM reduction: given I1 + sphere geometry, `k(M)` is fixed iff `R_s(M)` is given; the circle is shrunk to the single statement `R_s = 2M`, whose derivation from wiring is open (D6) | `horizon.k_from_mass_via_rs`, `data.k_schwarzschild_sun`, S1 |
| I4 | Verlinde equipartition + Bekenstein bound (`E = M`, `dS = 2πM₂dr`) | **input** (postulated) | `entropic`, S1 |
| I5 | Equivalence principle (Newtonian potential → `g_00`, redshifts) | **input** (postulated) | `redshift`, S1 |
| I6 | Continuum limits (heat-kernel, Ollivier–Ricci → Ricci, Raychaudhuri for leg bundles where invoked) | **input** (postulated) | `heatker`, `orici`, `jacobson`, S1 |
| I7 | Gap coefficient, crossover scales (`r_point`, `α = 1` congestion calibration, `A_min`) | heuristic / calibrated (see T6, T9) | `micro`, `redshift`, S1 |

Consequences of I1–I3 worth stating plainly:

- Adding interior nodes without exterior legs changes nothing observable from
  outside. The horizon is an *empty routing buffer*.
- Mass enters only indirectly, through I3. "Massive ⇒ large" is a derived
  statement about wiring budgets, not bulk volume.
- Kerr–Newman enters only as `A(M,a,Q) = 4π(r+²+a²)` with
  `r+ = M+√(M²−a²−Q²)` setting `k_eff = A/4ln2` (**input**). Spin orders legs
  smoothly: extremal Kerr carries exactly half, extremal Reissner–Nordström
  exactly one quarter, the Schwarzschild budget at fixed `M` (patch-independent
  ratios). Normalization (audit v0.2): `kerr.kerr_newman_k` returns `A/lp²`
  (patch-`1` units, exactly `PATCH_AREA`× the I1 leg count) and is consumed only
  by a monotonicity test; absolute leg counts use `data.k_schwarzschild_sun`.
  Nothing else about Kerr is assumed here — and nothing else about Kerr
  is claimed (see §5/D2).

### T4 (area law). Horizon area counts exterior legs, independent of `N`.

`A(k) = 4ln2·k·l_p²` by I1; `R(k)` follows. Evaporation shrinks the horizon even
if `N` stays fixed: wiring-only (`N` const) and standard (`N` shrinks with `k`)
give identical `A(t)`. **Derived** given I1–I2. (`horizon`, `evaporation`.)

### T5 (micro-hole pop). Pointlike below `k_crit`, horizon above — discontinuously.

A point region of radius `r_point` embeds `k` legs without a surface while
Planck-density packing succeeds:

```
R_obs(k) = r_point                          k ≤ k_crit
         = √(4ln2·k·l_p²/4π)                k > k_crit
k_crit   = 4π·r_point² / 4ln2·l_p²
```

Default `r_point = √(4ln2)` (one leg cell, Planck units). Packing theorem (BK):
given I1, no embedding exists for `k > ⌊4πr_foot²/4ln2·l_p²⌋` — the pop is
forced. With an LQG-style minimal-area gap, area is `0` below threshold and
`≥ A_min` above: no 0.2-Planck-area hole. **Derived** given I1–I2 plus the
stated `r_point`. (`micro`: `critical_k`, `is_pointlike`, `packing_kmax`,
`pop_forced`, `embedding_radius`, `quantized_area`.)

### T6 (island-like turnover). Two-saddle competition crosses iff legs are rich enough.

`S_no = k·s_leg` versus `S_isl = k·ln2·l_p² + max(S₀ − k·s_leg, 0)` cross at
`k_page = S₀/(2·s_leg − ln2·l_p²)`, which exists iff `s_leg > ln2·l_p²/2`
(BS form: `> PATCH/8`). Saturated vacuum legs (`s_leg = ln2`) give
`k_page = S₀/ln2`. A discrete min-cut analogue (all:all core + `k` leg
capacities) mirrors the jump. **This is a two-saddle competition plus a min-cut
analogue — not** `S_gen = A/4G + S_matter` extremized from a gravitational path
integral. Genuine QES extremization and the graph-dynamics evaporation isometry
are open (D1). (`qes`, `micro`.)

### T7 (Page curve, scoped). Leg surgery reproduces Page with Haar-typical fluctuations.

Imposed surgery `k → k−1` per step gives `S_rad = min(t, N_eff − t)` with the
exact Page dip `0.72` bits and Haar-typical spread, identically in wiring-only
and `N`-shrinking modes. Scope, stated exactly:

- **Imposed**: the `min()` curve in `evaporation` (honest toy).
- **Done**: the qubit-toy unitary completion `evaporation_unitary` — per-step
  `V_t` with `V_t†V_t = I` verified (including a composed-map inner-product
  test), `S_rad` computed from `ρ_rad` (tracks Haar/Page to `0.002` bits at
  `N = 8`), finite-depth all:all circuits converging to Page by depth `~5`/step
  without assuming Haar.
- **Open**: the graph instance `V_k: H_graph,k → H_graph,k−1 ⊗ H_leg` derived
  from graph dynamics (D1). "Page curve is a theorem of graph dynamics" is the
  close criterion, not the current claim.

QEC mirror: recovery error `err(k) = min(1/2, 2^{N/2+1−k})` reaches 99% at
`k ≥ N/2+1+log₂100`, sealing at `k → 0` (Hayden–Preskill primitive).
(`evaporation`, `evaporation_unitary`, `haar`, `qec`, `kerrpage`.)

### T8 (Newton + Kepler + sign). `F = M₁M₂/r²` exact, orbits close, attraction signed.

Leg screens + I4 give `F = M₁M₂/r²` exact to `1e−9` in log-log slope, with
closed leapfrog orbits and `T² ∝ r³`. Raw link-flux scales as channels
(`∝ 1/r²`) and would give `1/r³` as energy; the temperature factor over the
`r`-dependent screen corrects it to `1/r²` — both implemented so the
distinction is checkable. Ollivier–Ricci curvature is radially negative in
every tested configuration, attachment mode, and seed: the sign of attraction,
zero tuning. Micro-walks alone do **not** give Newton (persistent walks yield
drift `∝ 1/r³`, slope `≈ −3`; every smooth weight rule stays cubic, no-go
`−2.99`; `μ(χ)` fluctuation escape to `−1.95 ≈ −2` is modulo the labeled `√χ`
assumption). Conclusion: temperature (AS), not bare graph diffusion, carries
Newton. **Derived** given I4. (`entropic`, `weakfield`, `perwalk`.)

### T9 (redshifts + freezing). GPS and Pound–Rebka with no new parameters.

I3's potential plus I5 give `z = M(1/r₁ − 1/r₂)`: GPS `+5.29e−10`,
Pound–Rebka `2.55e−15` over 22.5 m. Congestion fronts give tortoise-like
freezing (`c_eff → 0`); `α = 1` matches Schwarzschild coordinate light speed
`dr/dt = 1 − R_s/r` **exactly** (calibration); `α = 2` is qualitative only.
Redshift itself is robust to the profile; the exact exponent is open
microphysics. (`redshift`.)

### T10 (light: bending + Shapiro + chroma). Full `4M/b`, Cassini-grade delay, achromatic.

Fermat ray-tracing with `c_eff = 1 − x` (`x = R_s/r`) gives full first-order
bending `4M/b` (the naive `2M/b` bet was lost on the record). Chromatic
extension uses *phase* velocity `1/24`, not group `1/8`: the `r`-independent
factor drops out of the Born integral, leaving fractional chromaticity
`~1e−56` (optical) to `~1e−32` (10 TeV). Shapiro delay reproduces
`R_s·ln(4r₁r₂/b²)` to 5%, passing Cassini with `γ = 1` exactly. An isotropic
reading would give `b_crit = 8M`, 54% above GR's `3√3M` and excluded by EHT at
`~3.6σ`: the isotropic reading dies, not the core — transverse propagation must
be essentially unimpeded, as an all:all interior demands. (`lensing`, `chroma`,
`shapiro`, `bcrit`.)

### T11 (spatial sector + Mercury). `γ = 1` exactly, `42.99″`/cy by direct integration.

Purely temporal models give closed Newtonian ellipses (`0` vs `43″`/cy): light
never needed `g_rr`, orbits do. Tortuosity `dl = (1+√χ/2)dr` gives
`h = (1+x/2)² ≈ 1+x`, `γ = 1`, `c_eff = √(f/h) = 1−x` matching the light sector
to first order, and `b_crit` back to `3√3M`. Direct geodesic integration
(`φ`-domain, complex-step) yields GR `42.99″`/cy and model `42.99″`/cy; a
flat-`h` hybrid gives `28.7″`/cy (PPN `2/3`). Second-order peel-off
`(ours−GR)/GR = −0.75·M/a` runs from 4.1% at `20M` to `2e−8` at Mercury.
Coefficient history, preserved: `1/2` was **fitted** to enforce `γ = 1` (BH,
unique coefficient, labeled fit); BV then **derived** `c ≈ 0.44–0.60` from
`ln2` line-defect scattering with zero tuning (target `0.456`, geometric
`1/√π = 0.564`), predicting `p = 2c` and `γ = 2c`. Both determinations agree;
the micro-derivation is adopted with the fit preserved in history.
(`strain`, `uvscatter`; PPN: `γ = 1` claimed, `β` unresolved and not quoted,
`α₁,₂/ξ`/Nordtvedt untouched.)

### T12 (Kerr thermodynamics, conditional). `T_H`, `Ω_H`, first law — given `A(M,J)`.

With `S = k·ln2` (saturated legs) and I1, `S = A/4`; importing `A(M,J)` gives
`S(M,J) = 2π[M²+√(M⁴−J²)]`, whose derivatives return the textbook `T_H` and
`Ω_H = a/(r+²+a²)`, i.e. `dM = T·dS + Ω_H·dJ` (identities `< 1e−6`, independent
finite-step `ΔM = TΔS + Ω_HΔJ` to `O(d²)`; super-extremal `|J| > M²` returns NaN,
never clamped). Per-leg reading `T_H = (dM/dk)/ln2`; finite-step shift `−1/4k`
(`~1e−77` stellar-mass). Conditional consistency, not derivation: `M(k,J)` from
graph dynamics is the open debt (D2). (`thermo`, `kerr`.)

### T13 (UV dispersion). Quadratic-only by symmetry; `E_QG,1 = ∞`.

Tight-binding hopping `ω = 2J|sin ka/2|` has group velocity even in `k`: no
linear term, so Fermi's linear bound (`E_QG,1 > 9.3e19` GeV; GRB 090510
`> 1.2·E_P`) is evaded by symmetry. Leading correction
`v(E) = c(1 − E²/E_QG,2²)` with `E_QG,2 = √8·E_P ≈ 3.4e19` GeV, safe by `~1e8`
against Fermi's quadratic bound (`1.3e11` GeV): a 10 GeV GRB photon over 3 Gpc
delays by `~1e−20` s. Foamgrid FDTD confirms unbiased centroids with
transmission deficit `∝ ω²` (`16% → 4% → 0.2%` for `λ = 8 → 32` cells at
`ε = 0.25`), bounding per-Planck-edge defect density to `ε ≲ 1e−3`
(optical/Gpc) and `1e−14` (TeV/Gpc) for independent edges. Caveats:
regular-lattice result, near-horizon running open, scalar sector only (no
birefringence claimed); the universal-GW extrapolation (`~1e−82` at 100 Hz,
LVK `α = 4` safe by `~1e60`) is a recorded null, not a falsifier — no GW sector
derived. (`dispersion`, `foamgrid`.)

### T14 (merger battery + nulls held). Area theorem in wiring language; nulls, not anomalies.

All 32 confident GWTC-3 BBH medians (live GWOSC fetch; 8-event bundled fallback
offline) satisfy `k_f > k₁+k₂` (median fractional
creation `0.77` at `0.04` radiated; spin neglected but `a_f ~ 0.7` costs `~13%`
against a `77%` margin). GW150914 posteriors (8350 samples, spin-aware both
ends) give `P(Δk > 0) = 100%`, median `0.57`. Healing `dA/dt` with
`τ = 11.24M` (3.5 ms at GW150914 mass); ladder healing/scrambling/Page/
evaporation separated by `~66×` to `1e80` s; MSS `λ/2πT = 0.50–0.68`
(`α ∈ [9.0,12.4]`, `11.24` inside). Nulls held: no LHC thermal black holes
(`k ≈ 4.0–6.1` at 3–13 TeV vs `k_crit ≈ 18.1` at `r = 2l_D`, `M_D = 1` TeV,
`n = 6`, ratios `0.22–0.33`, onset `~550` TeV; recomputed from `tev.k_add` /
`k_crit_tev` — v5 prose preserves the pre-BS absolutes `11–17` vs `50` with
identical ratios, flagged paper-side), no lattice echoes
(amplitude `R ~ (ω/ω_P)² ~ 1e−80`, energy `~1e−160` at 100 Hz — dimensional
estimate, not a leg S-matrix derivation), no EHT shadow shift (`1e−48`, 47
orders below sensitivity). Remnant dark matter excluded on the record except a
narrow `~0.4`-dex window at `~4e5` g. (`data`, `gwdata`, `posteriors`,
`healing`, `mss`, `tev`, `lhc`, `echoes`, `bounds`, `remnant`, `emd`.)

---

## 4. L2: compact-object phenomenology (calibrated)

L2 is one law plus two shedding numbers, calibrated **once** on AT2017gfo, with
everything else forward. It is the most testable layer and the least derived.
Its claims must be defeasible without touching L0/L1.

### The one law

`k = 1.51e77·(M/M☉)²` with no matter phases (I3 evaluated in solar masses).
Pulsars (`1.1–2.3 M☉`, `k ~ 1e77`), gap objects (`2.5–5 M☉`,
`k = 1.0–2.0e78`), and black holes are the same low-`k` all:all graphs at
different sizes. Consequences, stated bluntly: stable nuclear matter ends at
`~1e15` g/cc with no hyperon/quark branch realized in nature; `r`-process
yields through AT2017gfo neutron ejecta are reinterpreted as shed-leg
hadronisation. The gap is *described* (not derived) as the regime
`e_int ~ e_ext`; that interpretation inherits its calibration from AT2017gfo
and its mass-independence has not been derived from graph dynamics (D8).

### L2 calibrations (fits, all labeled)

| ID | Calibration | Value | Status |
|---|---|---|---|
| F1 | gradient slope | `p_adj(s) = 0.85 + 0.015·s`, 8–10 shells, exact EMD on full neighborhoods | **fitted**, labeled |
| F2 | bridge exponent | `β ≈ 1.5@300; 1.28@600; 1.24@1020; 0.99@4k; 0.87@8k; 0.74@16k`, deterministic `n ∝ r^β(N)`; log-linear over 6 points; recalibrated per `N` (drift faster than `1/N`; pre-run `1/N` extrapolation predicted `β(16000) ≈ 1.18`, measured `0.74`) | **fitted** per `N`; derivation from `N(r)` geometry queued (D4) |
| F3 | 2PN weight | `w = 1.953`, `c_tot = c₁ + w·c₂` | **solved** from the cancellation condition, not tuned — but not derived from the graph Laplacian either (D4) |
| F4 | `κ → c₂` map | `c₂(p) = p(2p−1)` | **ansatz** (open derivation D3): power-law fits better on these profiles (`R² 0.91` vs `0.81`) but the two maps disagree cross-applied (`c₂ 0.82` vs `3.14`); uniform measure is principled (continuum theorems) and required (`e_int` weighting *lowers* `p`: `0.94 → 0.84` at `0.9`, `0.78` at `0.99`) |
| F5 | shedding | `e: 0.5 → 0.416` (fraction `0.168`) + `10%` efficiency + `blue_frac 0.2` (`v_blue 0.3c κ 0.5`, `v_red 0.1c κ 10`) | **calibrated once** on AT2017gfo; `M_ej` exactly `k`-normalization-independent (`M_ej = frac·M_tot·ε`) |
| F6 | `q`-independence | `M_ej = 0.0168·M_tot` exactly flat in mass ratio (machine precision) | **prescription**, not derived from `V_k` (D1/D8): `q ~ 0.11` (GW190814) flashing at the same fraction as `q = 1` (GW170817) is the model's biggest theory bet |

### L2 measurements (outputs, not inputs)

- **Radial exponent**: `p = 0.913 ± 0.049` (80 graphs, `N = 1020`, exact
  Floyd+LP `~545` s; SEM `0.0055`, stacked `0.911` with `R² = 0.956`, 80/80 fits
  ok, range `0.79–1.05`). Distance to the GR-cancellation point `0.92` is
  `0.007` (`0.24σ` in `p`, `~0.09σ` in `ω̇`), with `5×` precision margin
  (`0.0055` vs `0.028`). N-scale: `0.9315 ± 0.0032` (4k), `0.9382 ± 0.0030`
  (8k), `0.9137 ± 0.0022` (16k); CSR-direct cross-check `0.9107` vs `0.9134`;
  local-`p` turnover `0.63–0.69 → 1.26–1.46` measured. Flat control `p = 0.49`
  is `−10σ` dead. (`orici`, `sinkor`, `shellscale`.)
- **2PN lock**: model `c₁ = 3.36` vs GR `1.94` (73% excess) is cancelled at
  `p = 0.92` (`c₂ = 0.7728`, `c_tot = 4.8693` vs GR `4.8695` → `0.00σ`
  fixed-`M`). Self-consistent `R+ω̇ → M`: `ΔM = −11.2` ppm naive (`−4.5` ppm
  with GR `g_rr`), `Δsin i = 3.7e−6`; J0737 `ω̇ = 16.899323(13)` deg/yr at
  `0.1σ`, `sin i` at `0.36σ`; B1913 at `0.01σ`. Bending/Mercury 2PN pieces hide
  below VLBI/astrometry. (`pulsar`.)
- **AT2017gfo anchor**: `1.4+1.4` gives `0.047 M☉` (blue `0.009` + red `0.038`),
  `m_g ~ 18.0` at 40 Mpc vs observed `17.5` (inside the `±1` analytic
  tolerance). Gap events are *brighter* at fixed distance. Band mags assume
  `BC = 0` and per-component peaks; `g`-band verdicts robust, `i`-band NOT
  claimed (one-zone `κ = 10` over-traps: `t_red ~ 10` d vs observed `~4` d
  decline, `m_i` faint by `~2–3` mag — conservative for gap-`g`
  detectability). (`collapse`.)
- **Gap prediction**: `M_tot → M_ej`: `2.8 → 0.047`, `5.0 → 0.084`,
  `7.2 → 0.121` (all `M☉`); `m_g ~ 21.2` at 200 Mpc (Rubin single-visit
  `r = 24.5`, DECam KN depth `23.5`); O5 yield `~1.05`/yr (ours, 1.5 gap/yr ×
  70% DECam-like) vs `≤ 0.3`/yr standard (literature `2–28%` mgNSBH input, not
  derived). Kill rule: 10 qualifying gap mergers (`< 200` Mpc, `< 100` deg²
  90%, multi-detector) with zero kilonovae to `m < 24` kills L2. One bright gap
  kilonova kills neutron-star EOS models instead. (`collapse`,
  `docs/observation-protocol.md`.)
- **Universal (BBH) shedding**: Eq. `M_ej = 0.0168·M_tot`, locked by the
  AT2017gfo calibration before anyone asked what it implies at `30+30 M☉`:
  nearby BBH must flash at `m_g ~ 22` (O5-testable). Kill accounting kept
  **separate** from the gap sample. (`massgaps`.)
- **GW190814 stress test**: `23.2+2.6 M☉` at `241^{+41}_{−45}` Mpc predicts
  `M_ej = 0.43 M☉` (blue `0.087`), `m_g ≈ 21.0` at `t ≈ 1.9` d. Epoch audit
  (CFHT MegaCam `g` + GROWTH DECam `i` detection limits) gives combined
  `P(detect) ≈ 0.68` (`g`-only, robust, no color term) to `0.88` (with
  `g−i = 0.7` systematic): non-detection at `p_miss ~ 0.32` down to `~0.12` —
  genuine pressure about one sigma from a kill, not exclusion. Analytic
  systematics (POSSIS-inspired viewing `0–1.25` mag + opacity `L ∝ κ^{−0.65}`,
  Fig. 75b) bound the hiding window: equatorial + lanthanide-mixed
  (`κ_blue = 2`) drops `P` to `~0.18`. Full 3D POSSIS queued (D7). Erratum on
  record: the first audit used a nominal ZTF depth, but ZTF ran no targeted
  GW190814 follow-up; superseded by CFHT/GROWTH epoch tables. (`massgaps`,
  Fig. 75/75b.)

### L2 positive null (upper gap)

No graph-scale feature at the `~44 M☉` pair-instability edge (GWTC-4:
`44.3^{+5.9}_{−3.5} M☉`, hierarchical transition at `46.2^{+12.6}_{−7.2} M☉` —
labeled literature inputs): `k(M) ∝ M²` has zero log-log curvature (`< 1e−9`
over `0.7–150 M☉`); spin orders legs smoothly (`1 → 0.857 → 0.5` at
`a = 0 → 0.7 → 1`); Love `k₂` runs slope `−2` with no break; the leg-quantum
line crossing 10 Hz at `~32 M☉` is energetically invisible (`dM/M ~ 1e−81`).
Congestion ladder seals the assignment: `χ ~ 1e−8` in He cores, `~1e−14` in
envelopes — graph corrections where pair-instability happens are negligible in
the model's own terms. The boundary belongs to stellar/nuclear physics, not the
graph; inserting `44 M☉` as a graph parameter is refused. (`massgaps`.)

---

## 5. Open maps (explicitly open)

Each item: what is missing, what would close it, what it gates. Tracked in
`docs/DEFERRED.md`; the paper's kill table wires the falsifiable ones.
Tag convention: D1–D8 here always mean DEFERRED items; the appendix-letter tag
(D2) (= module `evaporation_unitary`) is always written as the module name —
supplement.tex S1/S3 uses bare (D2) for both meanings (flagged paper-side).

| ID | Missing | Close criterion | Gates / kill relevance |
|---|---|---|---|
| D1 | Graph evaporation isometry `V_k: H_graph,k → H_graph,k−1 ⊗ H_leg` from graph dynamics; genuine QES extremization | derive (not choose) a scrambling `V_k` from the graph Hamiltonian/adjacency; reduced radiation spectrum follows Page under all:all dynamics; extremize `S_gen` from a path integral | promotes T6/T7 from scoped to full; no current falsifier (no observed BH Page curve) — referee-honesty issue |
| D2 | Kerr multipoles from the graph: `M₂ = −Ma²`, `g_tφ`, `r_ISCO(M,J)`, Kerr QNM spectrum | derive `Q = −Ma²(1+δ_Q)` without assuming Kerr; exterior perturbation `δω_nlm` vs Kerr | future wires: graph `|δ_Q| ≳ 0.17` ruled out by GW241011; QNM benchmark from GW250114 (`δf_220~2%`, `δτ_220~10%`, `δf_221~30%`, `δf_440~tens%`); GW250114/GW241011 currently consistent *by construction*, not passed predictions |
| D3 | Quantitative Ollivier–Ricci `κ → c₂` map | derive the map; resolve power-law vs `1/r²` disagreement | promotes F4 to derived; kill wire `p = 0.92 ± 0.056` at `N = 1024` class held to N=16000 |
| D4 | `β(N)` and `w` from geometry | derive `β(N)` from `N(r)` geometry, `w` from the graph Laplacian (Damour–Schäfer from wiring) | promotes F2/F3 to derived |
| D5 | NICER `M-R-Λ` + tidal deformability from routing stiffness | derive `R_1.4`, `M-R`, `Λ` | sharpest near-term test after kilonova rate (2–3 yr): `R_1.4` at 11–13 km, 5%, unreproducible by routing stiffness kills L2 compactness |
| D6 | Mass–radius from wiring | derive `R_s = 2M` from wiring alone | promotes I3 to derived (long-term) |
| D7 | Kilonova radiative transfer | full 3D POSSIS (morphology, Ye-dependent opacities, reprocessing); `i`-band direct | decides whether the GW190814 non-detection is compatible with universal shedding or falsifies it; `g`-band verdicts already robust |
| D8 | Shedding efficiency `ε(M,a,q)` + shutoff location | derive mass/spin/ratio dependence from `K_max(N)` combinatorics, spin-ordered reabsorption, or remnant-trap physics, with any shutoff location as *output* | highest-value attack surface on universal shedding; a derived shutoff between gap and BBH masses must land where it lands (same no-insertion rule as the 44 M☉ null) |

Rule for all D-items: the closing derivation must output the number or location,
not take it as input. Inserting an observed scale as a graph parameter is a fit,
not a prediction, and is refused (precedent: 44 M☉).

---

## 6. Non-claims (what the model does not say)

Stated so no reader misses them:

- Not a UV-complete quantum gravity: no Hamiltonian derivation of the mass map,
  no Lorentz-invariant dynamics.
- No `β` PPN parameter (coordinate-confused, not quoted); no `α₁,₂`, `ξ`,
  Nordtvedt; no linear LIV (forbidden: finite `E_QG,1` kills the discrete-leg
  picture outright).
- No Kerr `M₂`, `g_tφ`, ISCO, or QNM spectrum from the graph (overtone toy is
  Schwarzschild-like; fundamental damping `τ = 11.24M` calibrated).
- No NICER radii or tidal deformabilities yet (queued, D5).
- No `i`-band kilonova photometry claimed (one-zone red over-traps).
- No graph feature at 44 M☉ (positive null, §4).
- No explanation of FRBs, lensing oddities, or TeV transparency (examined, died
  on arithmetic, on the record). Pre-v4.0 "no standing anomaly" framing is
  superseded for exactly the five compact-object facts in §4 — nothing else.
- Ruled out on the record (kept visible): broad Planck-remnant dark matter
  (survives only in a `~0.4`-dex EMD window at `~4e5` g); isotropic
  `b_crit = 8M`; naive `γ = 2` strain; linear LIV; flat `p = 0.49`.

---

## 7. Symbol ledger

Single table; every symbol in §1–§4 appears here with its home.

| Symbol | Definition | Home |
|---|---|---|
| `N` | interior node count | §1, `graphs` |
| `k` | exterior leg count | §1, `horizon` |
| `e_int`, `e_ext` | interior / exterior entanglement fractions | P3, `horizon`/`monogamy` |
| `K_max` | max exterior budget (normalization) | §1, `horizon.exterior_budget` |
| `A(k)`, `R(k)` | `4ln2·k·l_p²`, `√(A/4π)` | I1, `horizon` |
| `PATCH_AREA` | `4ln2` Planck areas per leg | I1, `horizon.PATCH_AREA` |
| `r_point`, `k_crit`, `R_obs` | point radius, `4πr²/4ln2`, piecewise radius | T5, `micro` |
| `s_leg`, `η_vN` | per-leg entanglement (`ln2` saturated) | I1/T6, `qes` |
| `S₀`, `k_page` | bulk entropy, island crossing | T6, `qes` |
| `t_*`, `λ` | scrambling time, Lyapunov exponent | T2, `circuits`/`otoc` |
| `S_rad`, `N_eff` | radiation entropy, effective qubit count | T7, `evaporation` |
| `V_t`, `V_k` | qubit-toy isometry (done) / graph isometry (D1) | T7, `evaporation_unitary` |
| `a`, `Q`, `r+`, `k_eff` | Kerr spin, charge, outer horizon, effective legs | I3/T12, `kerr` |
| `T_H`, `Ω_H`, `S(M,J)` | Hawking temp, horizon velocity, entropy | T12, `thermo` |
| `k(r)`, `T(r)`, `Φ` | screen legs, equipartition temp, potential | T8, `entropic` |
| `z`, `c_eff`, `α` | redshift, front speed, congestion exponent | T9, `redshift` |
| `b_crit`, `γ` | photon capture impact parameter, PPN gamma | T10/T11, `bcrit`/`strain` |
| `h`, `χ`, `x`, `c` | radial metric factor, congestion, `R_s/r`, tortuosity | T11, `strain`/`uvscatter` |
| `σ`, `κ_blue/red` | leg cross-section `4ln2`, kilonova opacities | T11/§4, `uvscatter`/`collapse` |
| `E_QG,1`, `E_QG,2` | linear (`∞`) / quadratic (`√8·E_P`) LIV scales | T13, `dispersion` |
| `p`, `β(N)`, `c₁`, `c₂`, `w`, `c_tot` | radial exponent, bridge exponent, 2PN coefficients/weight | §4 F1–F4, `orici`/`pulsar` |
| `e_init/final`, `ε`, `M_ej` | shed fractions, efficiency, ejecta mass | §4 F5–F6, `collapse` |
| `m_g`, `m_i` | peak apparent mags (analytic, `BC = 0`) | §4, `collapse.peak_apparent_mags` |

---

## 8. Map to code, tests, figures

- **L0**: `graphs`, `scrambling`, `circuits`, `otoc`+`pheno`, `krylov`, `syk`, `bigsyk`,
  `sparse24`, `monogamy`, `qec`, `robustness`, `fission`, `klanguage`,
  `collapse` (grid→complete part), `concentration`.
- **L1**: `horizon`, `micro`, `qes`, `evaporation`, `evaporation_unitary`,
  `haar`, `maxent`, `tn`, `kerr`, `kerrpage`, `thermo`, `entropic`, `redshift`,
  `heatker`, `orici` (AU signs), `jacobson`, `lensing`, `chroma`, `shapiro`,
  `bcrit`, `strain`, `weakfield`, `perwalk`, `legham`, `dispersion`, `foamgrid`,
  `data`, `gwdata`, `posteriors`, `litcompare`, `healing`, `mss`, `mp`,
  `greybody`, `congestion`, `charge`, `bandwidth`, `gridcirc`, `monitor`,
  `selfattack`, `lhc`, `ps`, `scatter`, `emd`, `viability`, `tension`,
  `tensionvol`, `overtones`, `qnmfoot`, `qnmlegs`, `gw250114`, `echoes`, `tev`,
  `bounds`, `remnant`, `cosmic`, `ds`, `lunch`, `uvscatter` (BV derivation of
  `c`), `sinkor`, `shellscale` (N-scale backends).
- **L2**: `pulsar`, `orici` (gradient shells), `collapse` (leg-shedding),
  `massgaps` (lower-gap continuity + upper-gap null + GW190814 audit).
- **Falsifiers**: AF quench ratio, `α ∈ [9.0,12.4]`, `A ∝ N` TN wire, LHC
  thermality below `k_crit`, `s_leg ≤ l_p²/4` wire, linear LIV, `p` wire, gap/BBH
  kilonova wires, NICER wire, Kerr-quadrupole future wire — see the v5 kill
  table (`paper/v5/main.tex` §6) and `docs/observation-protocol.md`.
- **Reproduce**: `pip install -e ".[dev]"`, `pytest tests/ -q` (398 tests),
  `python scripts/generate_figures.py` + `python scripts/generate_v5_figs.py`
  (81 figure files, Figs 1–75), `streamlit run app.py`.

Counts above are v5.0 (`main.pdf` 12pp + `supplement.pdf` 11pp, S1–S10, 46/46
references cited). The v4.1 living document stays archived as the extended
record; v5 is canonical.

**Provenance layers (v0.2 audit).** Checked numbers fall in three layers with no
contradictions except the TeV absolutes (fixed in T14): test-pinned exact
(shed `0.168`, `c₂(0.92) = 0.7728`, log-log slope `2.0`, `γ = 1` to `1e-6`,
`p = 0.913 ± 0.049` / SEM `0.0055` / 80-of-80 in `data/p80_n1020_beta124.json`),
test-pinned envelopes (B1913 `6.2σ` / J0737 `9.7σ` naive bands, J0737 `< 0.1σ`
resuscitated, GW190814 `P = 0.68 ± 0.02`, chromaticity `< 1e-50/1e-30`),
figure-computed (`25` trials `N = 8…128`, depth-`5` convergence scan,
deficit orderings), and paper-quoted (`0.002`-bit tracking, `42.99`,
`0.57`/`100%` posteriors, `32` live BBH, MSS `0.50–0.68`, `1e-80/1e-160`
dimensional estimate). Suite on this branch: 398 collected, 396 passed,
2 torch/GPU-only skipped.

---

## 9. Promotion rules (how this document changes)

- An **input** becomes **derived** only by a derivation from earlier layers plus
  a merged test — never by rewording. (Precedent: tortuosity `1/2` fit → BV
  `0.44–0.60` derivation, with the fit preserved in history.)
- An **L2 calibration** moves to L1 only when its value is output by graph
  dynamics or geometry, with its old fitted value kept as the target it had to
  hit. (Candidates: F2/F3 via D4, F4 via D3, F6 via D1/D8.)
- A **D-item** closes only by its stated close criterion in §5. Partial progress
  is recorded in `docs/DEFERRED.md`, not by softening the criterion here.
- A **killed** claim stays in §6 with its killer named. (Precedents: broad
  remnant DM, isotropic `b_crit`, naive `γ = 2`, linear LIV, flat `p = 0.49`.)
- This document versions with the paper: v0.2 tracks v5.0 (audit release).
  Any number changed here must change in the same PR in the S1 audit table or
  be flagged as a deliberate divergence. One deliberate divergence stands:
  T14 TeV absolutes follow the code (post-BS), not v5 prose (pre-BS).

---

*Index-card version: L0 says what the wiring is (all:all, monogamy, no interior
distance). L1 says what spacetime costs (4ln2 per leg, one GR input, borrowed
thermodynamics) and what that buys (scrambling, Page, Newton-to-Mercury,
quadratic-only UV). L2 says what compact objects are (one `k ∝ M²` family, shed
legs, flash in O5) and what kills it (ten clean misses). §5 lists exactly what
would turn calibrations into theorems. Everything else is evidence.*
