# Kerr multipoles: exploration report (D2 scaffold, no derivation claimed)

Status: **exploration only**. Nothing in this note, in `src/bh_graph/kerrquad.py`,
or in `src/bh_graph/kerraniso.py` derives any Kerr multipole from the graph. The model's claim remains exactly what
supplement S1/S3 says: area (hence `T_H`, `Omega_H`) is assumed from the Kerr–Newman
formula; `M_2`, `g_tphi`, ISCO, and the QNM spectrum are open (D2 in
`docs/DEFERRED.md`). The `|delta_Q| >= 0.17` kill wire is unchanged.

This note records what exists, what the data actually constrain, and four concrete
routes toward a future derivation, ordered by how invasive they are. It is the
written companion to the D2 scaffold module (`kerrquad`: GR reference formulas,
kill-wire checkers, and explicitly-labeled toy scalings).

## 1. What exists today (ground truth, with pointers)

| Sector | State | Where |
|---|---|---|
| Horizon area `A(M,a,Q)` → leg budget `k_eff = A/4ln2` | **assumed** (ratios extremal-Kerr 1/2, extremal-RN 1/4 tested) | `kerr`, `test_kerr` |
| Kerr thermodynamics `T_H(M,J)`, `Omega_H(M,J)`, first law | **conditional consistency** (imports `S(M,J)`, differentiates; super-extremal → NaN) | `thermo`, `test_thermo` |
| Kerr Page curve (spin sheds faster, turnover later) | **toy trajectory** (`M(t)`, `J(t)` imposed, Page 1976–inspired) | `kerrpage`, `test_kerrpage` |
| Spin-induced quadrupole `M_2 = -Ma^2` | **not derived** | D2 (this note) |
| Frame dragging `g_tphi` / Lense–Thirring `2J/r^3` | **not derived** | D2 (this note) |
| ISCO `r(M,J)` | **not derived** | D2 (this note) |
| Kerr QNM spectrum `{220, 221, 440}` | **not derived** (fundamental damping calibrated; overtone ladder Schwarzschild-like toy; footprint corrections `1/2k`, `1/√k` unobservable) | `overtones`, `qnmfoot`, `qnmlegs`, `gw250114` |
| Weak-field gravity to 1PN (`1/r^2`, bending `4M/b`, Shapiro, `γ = 1`, Mercury `43″`) | **derived modulo labeled inputs** (equipartition, Bekenstein, tortuosity now BV-derived) | `entropic`, `lensing`, `shapiro`, `strain`, `uvscatter` |
| 2PN (`p = 0.913 ± 0.049`, J0737 `0.1σ`) | **measured** (`κ → c2` map + `w`, `β(N)` open: D3/D4) | `pulsar`, `orici`, `shellscale` |

Depth ladder: **area → thermodynamics → multipoles**. Area counts legs; thermodynamics
differentiates the imported `S(M,J)`; multipoles ask whether the *same wiring* that
produces `A ∝ M² + √(M⁴−J²)` also forces `M₂ = −Ma²`. That is the whole question.

## 2. What the data actually constrain (and what they don't)

- **GW241011** (high primary spin `χ₁ ≈ 0.78`, unequal mass ratio, high SNR):
  `δκ₁ = 0.10^{+0.82}_{−0.82}` (primary), `δκ_s ≈ 0.10^{+0.09}_{−0.11}`
  (symmetric combination under `κ₁ = κ₂`). Tightest spin-quadrupole bound to
  date; first spin-octupole constraints. Consistent with Kerr (`κ = 1`).
- **GW250114** (SNR ~80): area law + Kerr ringdown benchmark —
  `δf₂₂₀ ~ 2%`, `δτ₂₂₀ ~ 10%`, `δf₂₂₁ ~ 30%`, `δf₄₄₀ ~ tens%`.
- **Pre-registered wire (unchanged):** a future graph-derived
  `Q = −Ma²(1 + δ_Q)` with `|δ_Q| ≳ 0.17` is ruled out at
  symmetric-combination level (factor ~2 single-object vs ~10% symmetric by
  parametrization, LIGO-P2500402). Checker: `kerrquad.is_quadrupole_ruled_out`.

Two honesty notes that must survive any future work:

1. The symmetric-combination bound (`δκ_s`) assumes `κ₁ = κ₂`; a model that
   predicts strongly mass- or spin-dependent `κ(M, χ)` must be compared
   per-object, not against the symmetric number. The checker takes an explicit
   threshold argument for exactly this reason.
2. GW241011/GW250114 are currently consistent **by construction** (area-only
   import), not passed predictions. Do not reword this until a derivation exists.

## 3. Why the quadrupole is the right next depth

1. **Observationally live.** Any `δ_Q(χ)` lands immediately on the GW241011
   bound; LVK O5 will tighten it further on high-spin unequal-mass events.
2. **Conceptually adjacent.** The model already converts `(M, a)` into a leg
   budget. Spin "orders legs" (fewer independent legs at fixed `M`). The
   multipole question is whether that ordering has a *shape* — an axisymmetric
   deformation of the exterior routing field whose far-field expansion is the
   Kerr tower — or is just a scalar budget cut.
3. **Falsifiable on a useful timescale.** `|δ_Q| ~ 0.17` is a coarse target by
   theory standards; a derivation has room to land inside it, and overshooting
   kills the sector cleanly rather than lingering.
4. **Linked to the rest of the program.** The exterior legs define the horizon
   geometry; the 2PN sector already measures radial curvature (`p`) from
   Ollivier–Ricci. Multipoles are the axisymmetric (`θ`-dependent) counterpart
   of that radial measurement.

## 4. Four concrete routes (ordered by invasiveness)

### Route A — Axisymmetric leg anisotropy → `M₂` (least invasive; start here)

**Idea.** Keep the existing scalar budget `k_eff(M,a)` and add one
axisymmetric deformation field: polar vs equatorial leg density
`σ(θ) = σ₀(1 + ε P₂(cosθ))`, with `ε(χ)` to be measured or derived from
graph statistics. The scaffold quantifies the target: a thin Newtonian shell
gives `Q = m r²ε/5` (`kerrquad.toy_oblate_shell_quadrupole`), so mimicking
Kerr needs `ε_Kerr = −5a²/r²` (`kerrquad.required_anisotropy_for_kerr`).

**First computable (no new physics):** build the existing gradient-shell
graphs (`orici.gradient_shell_graph`), impose a latitude label on shell nodes,
measure Ollivier–Ricci separately on polar vs equatorial radial edges, and
report `ε_OR(χ_proxy)` where the spin proxy is an imposed polar/equatorial
bridge-density ratio. This does not derive spin — it calibrates the map
"wiring anisotropy → curvature anisotropy", the same role the `p` measurement
played for the radial sector.

**Sign story (corrected during scaffolding — read carefully, two spaces).**
In the shell-density convention (`σ = σ₀(1+εP₂)`, `P₂(pole) = 1`),
Kerr's `Q < 0` needs `ε < 0`: equatorial leg-density excess (oblate). The
naive "spin flings legs outward" story therefore gives the RIGHT sign in
*density* space. But the Route A calibration (§4b) measures the response in
*curvature* space and finds a NEGATIVE slope (connectivity dilutes `|κ|`):
polar bridge excess produces oblate *curvature* (`|κ|` relatively larger at
the equator). If the future axisymmetric `κ → metric` map tracks `|κ|` the
way the radial sector does, then Kerr-oblate wants polar bridge excess —
i.e. equatorial *correlation* (fewer independent equatorial bridges, exactly
the "spin orders legs" micro-story) gives the right sign. The sign flips
between density space and curvature space; any future Route A proposal must
state which space its `ε` lives in. This flip is the calibration's sharpest
conceptual output.

**Scale warning:** at horizon radius and extremal spin, `ε_Kerr ~ −5` is
order unity, not a perturbation. Either the horizon wiring is strongly
anisotropic (a sharp, testable micro-picture) or the quadrupole is generated
non-locally by the exterior routing field rather than a literal shell. Both
outcomes are interesting; the shell toy's job is to force the choice.

**Closes D2-quadrupole when:** `ε(χ)` is *measured from spin-labeled graph
dynamics* (not imposed), its far-field quadrupole is extracted through the
same `κ → c₂`-style map the 2PN sector uses, and the result matches
`−Ma²` within the wire (or misses it, killing the route).

### Route B — Oriented / chiral edges → `g_tphi` and frame dragging

**Idea.** The current graph is undirected; frame dragging is chiral. Add
oriented edges (or directed routing weights) with an azimuthal bias `b(χ)`
and ask what bias reproduces the weak-field Lense–Thirring rate
`Ω_LT = 2J/r³` (`kerrquad.lense_thirring_omega`) for equatorial random walks /
harmonic potentials. The existing walk no-go (all smooth weight rules give
drift slope `−3`; temperature carries Newton) is the baseline this route must
beat *in the azimuthal channel*: radial drift stays thermodynamical while
azimuthal circulation picks up the chiral piece.

**First computable:** extend `weakfield.weak_field_graph` with a directed
azimuthal overlay (each grid edge gets forward/backward weights
`1 ± b·φ̂·ê`), compute the circulation of the hitting probability /
harmonic potential around the hub, and fit `Ω_graph(b, r)` vs `2J/r³`.
Report the required `b(χ)` curve. Again: calibration first, derivation later.

**Risk:** directed Ollivier–Ricci and directed harmonic theory are less
standard than their undirected counterparts; the continuum theorems the 2PN
sector leans on may not transfer. Budget a literature check (directed OR
curvature, magnetic Laplacians) before heavy numerics.

### Route C — Axisymmetric Ollivier–Ricci → ISCO and QNMs (most ambitious)

**Idea.** Generalize the gradient-shell `p` measurement to an axisymmetric
measurement: `p(r, θ)` or equivalently a `θ`-dependent `g_rr` and an
off-diagonal `g_tphi` sector, then propagate test-particle geodesics (ISCO)
and scalar perturbations (QNM toy) through the reconstructed metric.
Success looks like: `r_ISCO(χ)` within tens of percent of Bardeen
(`kerrquad.kerr_isco_radius`) and `δω/ω` inside the GW250114 tolerances
(`kerrquad.is_qnm_deviation_ruled_out`) — or a clean miss.

**Why this is third, not first:** it inherits *all* of D3/D4
(`κ → c₂` map, `w`, `β(N)`) plus axisymmetry. Attempting it before Route A
produces an under-constrained fit with too many knobs to be informative.
Do A first; C is the payoff, not the entry point.

### Route D — Finite-`N` / finite-`e_int` null scalings (parallel, cheap)

**Idea.** Even without a positive derivation, bound the size of *any*
graph correction: `δ_Q ~ 1/k^α` (`kerrquad.toy_delta_q_finite_k`) and
`δ_Q ~ (1 − e_int)` (`kerrquad.toy_delta_q_eint`). For astrophysical
`k ~ 10⁷⁷` every `1/k` tail is `~10⁻⁷⁷` — forty orders below the wire. The
content of Route D is negative but useful: **a derivation that overshoots
0.17 cannot be a `1/k` tail; it must be an order-unity wiring effect.**
That trims the hypothesis space: look for qualitative wiring changes with
spin (correlation structure, orientation), not large-`k` asymptotics.

**First computable (already shipped):** `kerrquad.toy_kerr_deviation_summary`
evaluates both toys against the wire for any `(m, χ, k, e_int)`. Wire it into
`app.py` / a figure only if a future measurement gives `e_int(χ)` something
to chew on; until then it is a guardrail, not a result.

## 4b. Route A calibration: first measurement (this branch)

Shipped: `src/bh_graph/kerraniso.py` + `tests/test_kerraniso.py` (9 checks) +
`data/kerraniso_calibration.json`. Method: latitude-labeled gradient shells
(zone split 50/50, P2-mirroring bridge weights `w_pol = 1+ε`,
`w_eq = 1−ε/2`), exact Ollivier–Ricci per zone, `ε_OR =
(|κ_pol| − |κ_eq|)/|κ_all|`. The imposed `ε_bridge` is a hand-set spin proxy —
this is calibration, not derivation.

| curve | imposed ε | measured ε_OR ± SEM | bridge polar frac | n_ok |
|---|---|---|---|---|
| N=90 (15×6, 16 graphs) | −0.5 | +0.054 ± 0.025 | 0.31 | 15 |
| | 0.0 | +0.006 ± 0.013 | 0.54 | 16 |
| | +0.5 | −0.037 ± 0.023 | 0.70 | 16 |
| | +1.0 | −0.053 ± 0.037 | 0.81 | 13 |
| N=160 (20×8, 8 graphs) | −0.5 | +0.047 ± 0.025 | 0.32 | 8 |
| | 0.0 | +0.014 ± 0.010 | 0.51 | 8 |
| | +0.5 | −0.044 ± 0.019 | 0.69 | 8 |

Findings:

1. **Zero at zero.** Both curves pass through the origin within SEM — no
   systematic offset from the zone labeling. (`ε = 0` edge sets are
   bit-identical to `orici`, tested.)
2. **Negative slope ≈ −0.07 to −0.14.** Zones with MORE bridges show SMALLER
   `|κ|`: connectivity dilutes curvature magnitude. The response strengthens
   outward with bridge density (per-shell check at N=90: inner `+0.03`,
   outer `−0.06`), consistent with a dilution mechanism.
3. **Magnitude channel carries the signal; exponent does not.** Zonal `p`
   fits (`p_pol` vs `p_eq`) show no trend with imposed ε at this precision,
   while `ε_OR` is monotone. Future axisymmetric work should fit magnitudes
   first, exponents second.
4. **Weak response, limited range.** `|ε_bridge| ≳ 1` starves a zone (`n_ok`
   collapses; the `ε = −0.9`/`+1.5` points are unreliable and excluded
   above). Max reachable `|ε_OR| ~ 0.05–0.08` — far below Kerr-scale
   order-unity *curvature* anisotropy. Whether that suffices depends on the
   open axisymmetric `κ → metric` map (gain unknown): either the map
   amplifies ~10–50×, or the deformation must be stronger than bridge
   placement (e.g. latitude-dependent intra-shell completeness — a larger
   neighborhood change). A continuous-latitude (P2-weighted) estimator would
   also extend dynamic range beyond the binary-zone starvation limit.

Net for D2: the imposed→measured map exists, is monotone, and its sign flip
(density-oblate ⟺ curvature-prolate and vice versa) is now a measured
constraint any derivation must route through — see the sign story in Route A.
Spin-from-dynamics (work-order step 4) remains the hard, open step.

## 5. Suggested work order

1. **Scaffold (done, this branch):** `kerrquad` + tests + this note. No paper
   changes; no claim changes.
2. **Route A calibration (done, this branch):** `kerraniso` + artifact above;
   `ε_OR` vs `ε_Kerr` comparison now quantitative (weak-response caveat applies).
3. **Route B calibration:** directed azimuthal overlay → `Ω_graph(b, r)` fit
   → required-`b(χ)` curve.
4. **Spin-labeled dynamics (the hard step):** replace imposed anisotropy/bias
   with a graph-dynamical spin proxy (e.g. conserved circulation of a routing
   field, angular-momentum-weighted leg measure) and re-measure. This is where
   "calibration" becomes "derivation" — and where the wire starts to bite.
5. **Route C reconstruction:** only once A/B give stable maps.
6. **Paper update:** only on a positive result inside the wire (or a clean
   kill, recorded the same way the remnant-DM and `γ = 2` kills were).

## 6. Guardrails (do not erode these)

- Keep "area only" + the `|δ_Q| ≳ 0.17` wire exactly as written until a
  positive derivation exists. Do not claim consistency beyond what is derived.
- Every new function that is not derived from graph dynamics must say so in
  its docstring (reference / checker / toy), following `kerrquad`'s convention.
- `β(N)`-style per-`N` recalibration is acceptable for *measurement* but a
  spin-sector recalibration per-`χ` would be a fit, not a derivation — the
  close criterion (§7) requires `χ`-dependence as output.
- Super-extremal inputs return NaN, never clamped (repo convention, kept in
  `kerrquad`).

## 7. Close criterion for D2 (quadrupole part; unchanged in spirit)

Derive `Q = −Ma²(1 + δ_Q)` **without assuming Kerr** — i.e. from graph
dynamics + the same labeled inputs the 1PN sector uses — then compare `δ_Q`
to GW241011 via `kerrquad.is_quadrupole_ruled_out`. `|δ_Q| ≳ 0.17` (at the
appropriate parametrization level) kills the sector; landing inside promotes
D2-quadrupole from open to derived. ISCO / `g_tphi` / QNM close separately
against Bardeen / Lense–Thirring / GW250114.

## 8. Pointers

- Scaffold: `src/bh_graph/kerrquad.py`, `tests/test_kerrquad.py`.
- Route A calibration: `src/bh_graph/kerraniso.py`, `tests/test_kerraniso.py`,
  `data/kerraniso_calibration.json`.
- Area/thermo baseline: `src/bh_graph/kerr.py`, `src/bh_graph/thermo.py`,
  `src/bh_graph/kerrpage.py`.
- Radial-sector template to imitate: `src/bh_graph/orici.py`
  (`gradient_shell_graph`, `shell_kappa_profile`, `measure_p`),
  `src/bh_graph/pulsar.py`, `src/bh_graph/shellscale.py`.
- Walk baseline to beat (azimuthal channel): `src/bh_graph/perwalk.py`,
  `src/bh_graph/weakfield.py`.
- Ringdown benchmark: `src/bh_graph/gw250114.py`, `src/bh_graph/overtones.py`,
  `src/bh_graph/qnmfoot.py`, `src/bh_graph/qnmlegs.py`.
- Ledger: `docs/DEFERRED.md` (D2), `paper/v5/supplement.tex` S1/S3,
  `paper/v5/main.tex` kill table.
