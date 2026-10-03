# WEAVE0-PREREG — Emergent 3D Geometry from Randomly Interwoven 2D Sheets (FROZEN PRE-DATA)

Campaign: WEAVE-0. This document predates ALL WEAVE-0 headline measurements.
No WEAVE-0 construction, pilot, or measurement exists at freeze time. All bars
are inherited from banked campaigns, derived from the locked dispersion law or
the frozen construction math below — none are fit to WEAVE-0 data. Where
DIM-3-0 invalidated an estimator (d*, threshold-arrival volume, static range),
this prereg either ports the validated replacement or gates control-relative
readouts only. Control-relative gates compare headline legs against frozen
controls run through the SAME code; no headline datum enters any calibration.

Frozen law (firewall): `H = -A`, `J = 1` headline, no onsite term, no edge
weight, no retuned source strength, no observer prior. No coordinates enter
dynamics; coordinates appear only as readout labels (blind/intrinsic joins
happen strictly after blind artifacts freeze + hash). No claim of literal
physical sheets, Lorentz invariance, GR, quantum gravity, or fundamental J2.

## 0. Mission and mechanism (pre-data derivation)

Mission: test whether a disordered ensemble of locally 2D/J2-like sheets can
generate large-scale 3D operational geometry without an ordered stack or an
explicitly cubic microscopic substrate:

```text
local 2D sheets + irregular weaving -> statistical 3D geometry.
```

### M0. Dimensional accounting (frozen mechanism, tested not assumed)

Let sheets be 2D (intrinsic volume `V_s(r) ~ r^2`) joined by a sheet-meeting
graph `M` (vertices = sheets, edges = meeting pairs carrying stitches). A
ball of radius `r` covers the sheets within stitch-mediated reach:

```text
V(r) ~ (sheets within r) x r^2,  sheets-within-r ~ min(S, (r/l_W)^d_M),
```

where `l_W` is the crossover scale (M1) and `d_M` the meeting-graph growth
dimension. Consequences (frozen predictions, one per meeting class):

- chain/ring meeting (`d_M = 1`): `V ~ r^3/l_W` for `l_W << r << S*l_W`
  (3D window), re-entrant thick-2D (`V ~ S*r^2`) for `r >> S*l_W`.
- dense (all-pairs) meeting (`d_M = inf`): NO 3D window; `V ~ S*r^2`
  (thick 2D) directly above `l_W`.
- 3-regular random meeting (locally tree-like, diameter `~ log S`):
  brief expansion then thick 2D; no stable 3D window predicted.
- overconnected (stitch stubs everywhere): expander-like; estimators REFUSE.

The headline (C2, chain meeting + disordered orientation) is predicted to
show a stable `2D -> 3D` crossover; the dense/ER3 legs are load-bearing
DISCRIMINATORS of this mechanism (predicted 2D, not 3D). If chain legs also
read 2D, the mechanism is wrong (WEAVE0-2D). The re-entrant `-> 2D` tail at
`r >> S*l_W` is part of the prediction, not a failure.

### M1. Crossover scale from frozen intersection statistics (derived, not fit)

`K = round(lam*N)` stitches; `2K` endpoints uniform over `S` sheets x `L^2`
cells. Per-cell endpoint density `rho = 2K/(S*L^2) = 4*lam` (using `N=2*S*L^2`,
`K=lam*N`). Mean endpoint spacing (2D Poisson heuristic, frozen):

```text
l_W^pred(lam) = rho^(-1/2) = 1/(2*sqrt(lam))   [sheet cells]
```

Balls with `r << l_W` are sheet-local (2D); `r >> l_W` is stitch-mediated.
`l_W^pred` enters window rules and the monotonicity test; it is NEVER fit to
`V(r)`. Diffusion-time mirror (diffusive scaling, frozen): `t_W^pred = l_W^2`.

### M2. Why stitches are not ordinary random rewiring (frozen distinction)

REWIRE-0 rewiring deletes + re-pairs existing edges (degree-preserving,
progressively destroys the local motif). Weaving ADDS inter-sheet edges while
preserving EVERY intra-sheet edge exactly (Stage-A pin: induced subgraph of
each sheet is the intact J2 torus). Local sheet motif preservation is exact
(`stub fraction = 1 - exp(-2*lam) <= 15%` at headline `lam <= 0.08`: fraction
of nodes touching any stitch, frozen formula), not statistical.

## 1. Frozen constructions

Sheets: J2-`L` torus (`formation.j2_torus_graph`, 8-regular, `2L^2` nodes).
Weave node id = `s*M + v` (`M = 2L^2`, `s` = sheet, `v` = J2 id); coords map
`id -> (s, x, y, b)`. Square-sheet leg: square torus `LxL` (4-regular, `L^2`
nodes, `vacfield.square_torus_substrate` graph). All graphs simple/undirected.

- C0 frozen 2D: single J2 torus at sheet `L` (+ J2-L28 banked spread leg).
- C1 ordered stack: `S` sheets + vertical edges `(s,v)-(s+1 mod S,v)` all `v`.
  Degree 10, aligned, periodic. Bipartition `(x+y+s)&1` (staggered frame).
- C2 headline (random weave, chain meeting): ring order = random permutation
  `pi` of sheets (seeded); meeting pairs = consecutive in `pi` (periodic).
  `K = round(lam*N)` stitches: each picks a uniform ring edge, then a uniform
  A-node on one sheet + uniform B-node on the other (COMMON `(x+y)&1` frame,
  bipartite-preserving by construction), added iff absent (seeded retries,
  cap `20*K`; actual `K` recorded; `K/K_target >= 0.99` gate, Stage A).
  Per-sheet orientation record `(dx_s, dy_s, tau_s)` (random cyclic shifts +
  axis-transpose flag, seeded; uniform-equivalent endpoint sampling).
- C2-dense: same but meeting = uniform random sheet pair per stitch.
- C2-ER3: meeting = `random_regular_graph(3, S, seed)` edges (S even); uniform
  meeting edge per stitch.
- C2-sq: square-torus sheets + C2 chain meeting (universality leg).
- C2-nb: C2 chain meeting, stitches WITHOUT A-B restriction (robustness leg).
- C3: J3 torus (`dim3`, frozen: L12/L16).
- C4: cubic torus (`dim3`, frozen: L16 headline match `N = 4096`).
- C5: configuration model with the EXACT degree sequence of the matched C2
  instance (seeded; simplified to simple graph; self-loops removed; resample
  `seed+1...` up to 20 tries for connected, else largest-component analysis
  with REFUSE flag filed). Same `N`, same degrees, no sheet structure.

Frozen sizes: headline `(S,L) = (8,16)`, `N = 4096`; scale legs `(8,24)`
(`N = 9216`) and `(16,16)` (`N = 8192`). C4-L16 `N = 4096` exact-matches the
headline. C0 blind cell J2-L44 (`N = 3872`, even `L` = bipartite).

Frozen `lam` ladder (stitches/node): `(0.001, 0.005, 0.01, 0.02, 0.04, 0.08)`
(+ `0.16` overconnected leg on headline size only), `l_W^pred` = `(15.8,
7.07, 5.0, 3.54, 2.5, 1.77)` (+ `1.25`) cells. Per-ring-edge stitches at
`(8,16)`: `lam*512` = `(0.5, 2.6, 5.1, 10.2, 20.5, 41.0)` (+ `82`).

Frozen ensemble: `WEAVE_SEEDS = (7, 17, 27, 37, 47, 57, 67, 77)` (8 seeds;
C2/C5 headline legs run all 8; discriminator legs run seeds `(7, 37, 67)`;
scale legs run seeds `(7, 37)`; vacuum/hidden/packet stages run seed `7` +
one replication seed `37` where stated).

### Regime classification (frozen, from graph observables only)

Per `(leg, lam, seed)` instance, before any operational probe:

```text
DISCONNECTED: > 1 component, or a sheet isolated (0 stitches).
MARGINAL:     connected, but a ring/meeting edge carries 0 stitches.
WOVEN:        connected, every meeting edge carries >= 1 stitch,
              stub fraction < 0.25.
OVERCONNECTED: stub fraction >= 0.25, or diameter <= 6 at N >= 4096.
```

Estimators may return UNMEASURABLE (no scaling window / no fit) on any
instance; UNMEASURABLE is filed, never imputed, never gated as fail
(DIM3-Amd-1 A5 precedent). REFUSE/NONGEOMETRIC verdicts are permitted.

## 2. Stage A — construction exactness (gates, all campaign graphs)

- N/E exact (`2SL^2` / sheet edges + `K`; C1 `+ S*M` verticals); degrees
  (C2: 8 + stubs; C1: exactly 10; C5: exact sequence match).
- Induced subgraph of each sheet == intact J2 torus (edge-set equality).
- Bipartite: C0/C1/C2/C2-dense/C2-ER3/C2-sq/C3/C4 exact (frozen frames);
  C2-nb/C5 filed (no gate).
- Meeting graph exact (ring permutation / dense pairs / ER3 edges recorded).
- `K/K_target >= 0.99`; seeds/frames recorded. A failure here = INCOMPLETE.

## 3. Stage B — intrinsic volume growth (headline geometry channel)

`V(r) = |B_r(v)|` BFS balls (no coordinates). Origins per graph (frozen):
4 far-from-stitch (`d_to_stub >= l_W^pred`, or max-distance nodes if none),
2 near-stitch (stub endpoints), 2 uniform random (seeded) = 8 origins.
Full `d_eff(r) = d lnV/d lnr` curves filed (all `r`).

Frozen windows, headline `(S,L)=(8,16)` (per-size table; `D` = measured
graph diameter from node 0, wrap cap `D/2 - 1` applies to every hi edge):

```text
LOCAL:  r in [2, 4]            (below l_W for lam <= 0.04)
GLOBAL: r in [7, 11]           (above l_W for lam >= 0.01; inside S*l_W)
```

Scale legs: same LOCAL; GLOBAL `[7, 13]` (`(8,24)`), `[7, 15]` (`(16,16)`).
Fits: log-log OLS exponent + `r2 >= 0.90` quality (filed; `r2 < 0.90` =
UNMEASURABLE for that origin). Per-graph exponent = median over origins
(far-origin median filed separately; gate uses all-origin median).

Control-relative gates (same code, same windows):

- B-val-2D: C0 reads LOCAL `|d-2| <= 0.30` AND GLOBAL `|d-2| <= 0.30`
  (validates: no spurious 3 anywhere on 2D).
- B-val-3D: C4 reads GLOBAL `d in [2.20, 3.30]` (finite-size
  approach-from-below precedent: grid3d L=21 reads 2.63; bar is sanity,
  not equality) AND C3 reads GLOBAL `d > 2.20`.
- If either validation fails, Stage B is apparatus-invalid (no headline gate).
- B-head (per `(lam, seed)` C2 instance): LOCAL `|d - d_C0_local| <= 0.20`
  AND `|d-2| <= 0.30` (local 2D); GLOBAL `|d - d_C4_global| <= 0.25` AND
  `d - 2 > 0.30` (matches known-3D, excludes 2D).
- B-disc: C2-dense GLOBAL reads `|d-2| <= 0.35` (thick-2D mechanism check,
  `>= 2/3` seeds); C2-ER3 GLOBAL reads `< 2.60` (`>= 2/3` seeds).
- B-mono: crossover radius `r_c` (first `r` where far-origin-median `d_eff`
  crosses 2.5 upward; UNMEASURABLE if never) decreases monotonically over
  WOVEN-regime `lam` (Spearman `<= -0.70` over measurable `lam`), and
  `|r_c - l_W^pred|/l_W^pred <= 0.60` (median over WOVEN `lam`, measurable).

## 4. Stage C — spectral/diffusion dimension (PRIMARY operational channel)

Dense-eig heat-trace `d_s` (`obs0.heat_trace_ds` math) + per-origin return
`d_s` (`obs0.origin_return_ds` math) over a frozen dense `t`-grid
`t = 2^k, k = 0..10` (+ `t = 48, 96, 192, 384` scale legs). Sliding
3-point log-window `d_s(t)` curves filed. Frozen windows (headlice `(8,16)`):

```text
T-LOCAL:  t in [2, 8]     (below t_W = l_W^2 for lam <= 0.04: 6.25..250)
T-GLOBAL: t in [64, 192]  (above t_W for lam >= 0.005; below t_sat ~ 256)
```

Scale legs: same T-LOCAL; T-GLOBAL `[64, 256]` (`(8,24)`, `(16,16)`).
Window fit = log-log OLS over grid points in window (`n >= 3` else
UNMEASURABLE); heat-trace (mean) is the gated readout, origin-return filed.

- C-val-2D: C0 T-LOCAL and T-GLOBAL both `|d-2| <= 0.30`.
- C-val-3D: C4 T-GLOBAL `d in [2.20, 3.30]`; C3 T-GLOBAL `d > 2.20`.
- C-head: same control-relative form as B-head (LOCAL `|d-d_C0| <= 0.20` +
  `|d-2| <= 0.30`; GLOBAL `|d-d_C4| <= 0.25` + `d-2 > 0.30`).
- C-disc: C2-dense/ER3 same form as B-disc. C-mono: same as B-mono on
  `t_c` (first upward 2.5-crossing of `d_s(t)`) vs `t_W^pred = l_W^2`.

Stage B AND C must validate on controls for any 3D headline (two independent
channels; both were validated 2D-side by OBS-0 precedent and 3D-side here).

## 5. Stage D — blind observer reconstruction (validated legs only)

`obs1` apparatus VERBATIM (same module, opaque stations S0..S63, 3 sets,
`rng(9100 + 100*cell + set)`, W/D/P instruments via Krylov + CG statics;
grids: wave `dt=0.05, Tmax=D`; diffusion `dt=0.25, Tmax=3(D/2)^2`; static
gap-matched `omega = -(zmax+0.5)` with `zmax` = measured max degree, gap 0.5
below the Gershgorin edge — frozen rule, graph-adaptive like-for-like).
Sheet labels stripped before evolution/readout (stations are opaque ints;
no sheet id enters any instrument). Blind cells (frozen order):

```text
0 c0-j2L44  1 c1-S8L16  2 c2-lam001-s7  3 c2-lam002-s7  4 c2-lam004-s7
5 c3-j3L12  6 c4-cbL16  7 c5-match4-s7  8 c2dense-lam004-s7  9 c2sq-lam004-s7
```

(`c2-lamXXX` = headline `(8,16)` chain meeting at `lam`, seed 7; `c5-match4`
= C5 matched to cell-4 degrees; `lam` shorthand `001 = 0.01` etc.)

Gated legs (DIM-3-0-validated ONLY):

- D-chart (PRIMARY): local-chart dimensionality. For each set: MDS-3 ball
  charts `< 0.30` + MDS-2 charts `>= 0.30` = 3D signature (DIM-3-0 D-c
  pattern: J3/cubic pass-3D fail-2D); MDS-2 `< 0.30` = 2D signature.
  Validation: cell 6 (C4) shows 3D signature `>= 2/3` sets; cell 0 (C0)
  shows 2D signature `>= 2/3` sets. Headline: cell 4 (C2 `lam=0.04`)
  shows 3D signature `>= 2/3` sets; cells 2/3 filed (ladder trend).
  `select_dimension` d* is FILED, never gated (structurally forced to 2;
  DIM-3-0 diagnosis). Raw vol dimension filed; gamma-corrected vol
  (SECONDARY gate): `gamma_cal` = median W-arrival `tau ~ d_graph^gamma`
  exponent over control cells 0/5/6 (graph-distance fit at reveal time,
  frozen procedure); `d_gamma = gamma_cal * vol_d`; gate
  `|d_gamma(cell4) - 3| <= 0.50` + `|d_gamma(cell0) - 2| <= 0.50`
  (validates the correction 2D-side).
- D-dist: DIST match `< 0.30` vs hidden reference where a reference exists
  (cells 0/1/5/6: sheet/quotient coords; C1 ref = stack coords). Cells
  2/3/4/7/8/9 have NO ground-truth reference: chart legs only (no DIST
  gate — honest absence of ground truth).
- D-locality/sheet: locality `> 0.70` gated on cells 0/5/6 only
  (reference cells); sheet contrast filed everywhere (C2 "sheets" =
  construction labels, reveal-only, filed not gated).

## 6. Stage E/F — spreading crossover (RESPONSE port, intrinsic shells)

Point R/I impulse (unit, `eps=1e-3` battery legs), BG0, `T=16/dt=0.05`
(RESPONSE-0 verbatim), INTRINSIC shells (graph-distance layers from source;
no quotient exists). Shell-peak fits with the Amendment-1 A1 interior-peak
validity rule verbatim (`n >= 3` else UNMEASURABLE). Frozen windows from
`l_W^pred` (rule, not fit): NEAR shells `2..floor(l_W)` (min 3 shells else
UNMEASURABLE), FAR shells `ceil(2*l_W)..10`. Per record `n` filed.

- E-val: C0 (J2-L28 leg) NEAR/FAR-equivalent window `2..10`: `alpha_psi`
  in `[0.40, 0.60]` (banked 2D replication); C4-L16: `alpha_psi` in
  `[0.80, 1.20]` (3D control).
- E-head (C2 WOVEN `lam`, seed 7 + 37): NEAR `|alpha - 0.5| <= 0.15`,
  FAR `|alpha - 1.0| <= 0.20`, `r2 > 0.9` both; `>= 3/4` records pass.
- F-head: `delta-rho` NEAR `|alpha - 1.0| <= 0.25`, FAR `|alpha - 2.0| <= 0.30`
  (quadratic dilution conditioned on geometry); `delta-J` same windows filed
  (chirp artifact precedent: J exponent may read low — gate is `rho` only,
  `J` filed); `delta-B = 0` exact legs on bipartite cells (theorem leg).
- E-mono: FAR-window onset (first shell with valid peak usable in FAR fit)
  moves inward monotonically over WOVEN `lam` (filed + Spearman gate
  `<= -0.50`).

## 7. Stage G — packets, transverse transport, anisotropy, switch

- G-a in-sheet packets: Gaussian on sheet quotient coords (`sigma = L/6`,
  `T = 4`, `k = 0.3` along x; J2 Bloch velocity `v_B = 4*sin(k)` — J2
  dispersive band `eps = -2J*f`... exact J2 Bloch velocity pinned in tests
  from `continuum`/banked law; gate `|v - v_B|/|v_B| <= 0.10`, reversal
  under `k -> -k` (cos `< -0.95`), norm to `1e-9`). Run on C0, C1 (one
  sheet), C2 (`lam = 0.04`, seeds 7/37, two sheets each).
- G-t transverse transport (C1 vs C2 washout): first threshold-crossing
  (`1e-3` relative, frozen) arrival from a sheet-0 delta to sheet-`k`
  (`k = 1..4` along stack/ring order), Krylov exact. C1: ballistic fit
  `t(k)` exponent `1.0 +- 0.25` (ordered stack conducts coherently).
  C2: washout inequality `t_C2(4)/t_C1(4) > t_C2(1)/t_C1(1)` (disorder
  penalty grows with distance) + exponent filed. In-sheet velocity vs
  transverse effective velocity ratio filed both (anisotropy magnitude).
- G-aniso: in-plane directional spread: packets along `+x/-x/+y/-y` on one
  sheet; `A_in = std(v)/mean(v)`; gate `A_in(C2) <= A_in(C1)` (random
  weaving does not ADD in-plane anisotropy; equality expected near zero —
  J2 `x<->y` symmetric — so this is a non-regression gate, filed values).
- G-d switch: source-switch front `v/vmax_bound` filed (`vmax` = measured
  max group proxy: in-sheet Bloch max; forerunner precedent — filed, no
  gate beyond `v < vmax_bound` physicality).

## 8. Stage H — hidden/null sector (derived decomposition, no global J2)

No global `P_+ (+) P_-` is assumed. Instruments are per-sheet LOCAL sectors
(preparations/readouts supported on one sheet); the GLOBAL decomposition is
derived from the woven graph spectrum:

- H-der: null-space census (dense eig, headline `(8,16)` C2 `lam = 0.04`
  seeds 7/37 + C0/C1/C4): nullity, null-vector IPR, max overlap with any
  per-sheet `P_-` sector (filed; gate: nullity + IPR + overlaps FILED with
  existence bar — census completes, no physics bar pre-data).
- H-mix: stitch-induced sector mixing: `||P_-^{(s)} H P_+^{(s')}||` operator
  norms for meeting/non-meeting sheet pairs (filed matrix; gate: meeting
  pairs mix `> 0` — stitches couple sectors, non-meeting `== 0` exact).
- H-bat (HIDDEN-0 port, banked bars): matched hidden pair on ONE sheet far
  from stitches (`d_to_stub >= l_W`): locally distinguishable
  (`D > 1e-6`), remote wave/diff shells blind (`< 1e-9`, shells `r >= 2`
  intrinsic), POT remote exactly `0.0`. Run C0 + C1 + C2 (`lam = 0.04`).
- H-xbat (cross-sheet blindness): same pair, remote readout on OTHER sheets
  (all nodes with sheet `!= s`): blind `< 1e-9` wave/diff (gate on C2).
- H-g (ledger census): virtual sign-reversal census, banked HBR-0 rules:
  global bipartition-sign pair (VPI-analog, exists: bipartite) gate `> 100`
  flips; local-pair flips filed. Background = G-a packet (Amd-1 A6 rule).

## 9. Stage I — vacuum compatibility (JOINT port, no J2-manifold identity)

Candidates derived from the graph (no VPLUS/VPI/VMINUS identity assumed):
PERRON (ground state of `H = -A`, positive), STAG (bipartition-staggered,
unit), SHEET-UNIFORM (uniform on one sheet, 0 else; non-stationary probe).
Stages on C2 headline `lam = 0.04` seed 7 (+37 replication) and C0/C1/C4:

- I-a stationary: Krylov drift `stationarity < 1e-8` (inherited bar) for
  PERRON; eigen-residual `< 1e-9` (inherited).
- I-b JOINT rungs (inherited bars): current-free (`1e-12`, real states),
  phase-invariant (`1e-9`), amplitude-scaling (`0.01` slope tol); stress
  uniformity FILED (expected non-uniform on irregular graph — no gate).
- I-c ledger: PERRON ledger `(fneg, fpos, fzero)` + STAG ledger filed
  (patterns, no J2-pattern gate); gate: ledgers COMPLETE (all edges scored).
- I-d gap/stability (protected physics): spectral gap above ground state
  `> 1e-6` (gate: gapped); excitation stability: PERRON + vacexc-style
  local delta (`eps = 0.01`): evolved `T = 8`: perturbation stays
  `O(eps)`-bounded and norm-conserved to `1e-9` (gate: bounded + norm).
- I-e texture: per-sheet VMINUS-texture state (product of sheet `P_-`
  uniforms): stationarity drift FILED (expected drift: stitches break the
  sector — honest negative allowed).

## 10. Stage J — size scaling + universality

- J-a: headline `lam = 0.04` at `(8,24)` + `(16,16)`: Stage-B GLOBAL and
  Stage-C T-GLOBAL exponents move TOWARD 3 vs `(8,16)` (or stay within
  `|d - d_C4| <= 0.25` while the measurable window broadens: `n_global`
  shells/grid-points strictly larger). Gate: broadening + no retreat
  (`d_J >= d_headline - 0.10`).
- J-b: C2-sq (`lam = 0.04`, `(8,16)`, 3 seeds): B-head + C-head gates pass
  (exact J2 unnecessary). If C2-sq fails while C2 passes: J2 load-bearing
  (filed, verdict unaffected).
- J-c: C2-nb (2 cells): B/C exponents filed (robustness; no gate).

## 11. Verdict ladder (frozen decision tree)

Order of evaluation (first match fires):

1. Stage-A failure on any campaign graph, or full-suite red (minus
   `test_weighted.py`), or missing coverage -> WEAVE0-INCOMPLETE.
2. B-val/C-val fail (controls do not validate the windows) ->
   WEAVE0-INCOMPLETE (apparatus fails; no headline).
3. D-chart validation fails on control cells 0/6 -> blind stage INCOMPLETE
   (filed; non-blind stages still verdict).
4. C5 matches C4 on B+C GLOBAL (`|d_C5 - d_C4| <= 0.25` on both) AND C2
   also matches -> WEAVE0-RANDOM (sheet structure not load-bearing).
5. C2 shows no WOVEN `lam` with B-head + C-head jointly passing (majority
   of 8 seeds) -> WEAVE0-2D if C2 GLOBAL reads `|d-2| <= 0.35` stably, else
   WEAVE0-NONGEOMETRIC if estimators systematically UNMEASURABLE/refuse
   (C5-like profiles), else WEAVE0-INCOMPLETE (ambiguous apparatus).
6. C2 shows `>= 1` WOVEN `lam` with B-head + C-head passing (majority of
   seeds) + B-mono/C-mono pass + E-head/F-head pass + J-a broadening ->
   WEAVE0-3D core. Then: H-bat + H-xbat + H-g + I-a + I-b + I-d pass ->
   WEAVE0-3D-JOINT; else WEAVE0-3D. If G-t washout inequality FAILS (C2
   transverse as coherent as C1) but core passes -> WEAVE0-ANISOTROPIC
   only if additionally the transverse ratio shows a STRONG preferred
   direction (filed threshold: `v_plane/v_trans > 3` with ballistic
   transverse); else WEAVE0-3D stands (washout is characterization).
7. D-chart headline (cell 4, 3D signature `>= 2/3` sets) REQUIRED to
   upgrade a (5)-ambiguous case, SUPPORTING (not required) for the core:
   filed either way. If blind says 3D while B/C say 2D (or vice versa):
   both filed, verdict follows B/C (intrinsic channels primary), blind
   discrepancy noted (no post-data bar moves).

Ensemble rule: "majority of 8 seeds" = `>= 5/8` instances pass at a `lam`
for a stage-head claim; means/spreads reported per `(leg, lam)` always; no
selected-seed headlines. All verdict inputs committed as
`data/weave0/` parts + `data/weave0_blind.json` (+ sha256, committed before
reveal) + `data/weave0_verdict.json` + `data/weave0_diagnosis.json`.

## 12. Controls summary

Frozen law `H = -A`; C0 2D (validates 2D, excludes spurious 3); C1 ordered
stack (validates sheet-built 3D CAN read 3D + anisotropy contrast); C3 J3 +
C4 cubic (validate 3D readings); C5 degree-matched random (load-bearing
sheet-structure control); C2-dense/ER3 (mechanism discriminators); J2-L28
banked replication; blind observer (opaque stations, hash-frozen reveal);
graph-intrinsic dynamics (no coordinates in evolution); 8-seed ensembles;
no post-data redesign (this file + code frozen before the grid; apparatus
amendments, if any, pre-grid with A-prefix like DIM3-Amd-1).

## 13. Sizes and compute

Exact/dense (tests + analysis): balls, torus L `<= 8`, weave `(2,4)` toys.
Campaign (beast, xargs-parallel, `nice`, `OMP_NUM_THREADS=1`, `JOBS <= 170`):
per Section task lists (`weave0_campaign.py --list`); dense eig only for
`N <= 9216`; full suite on beast (`-n 64`, skip `tests/test_weighted.py`
per standing instruction + `pyproject.toml` default ignore).

## 14. Amendment-0 (PRE-DATA clarifications; no WEAVE-0 measurement exists)

Code-level mechanism review before the grid. Nothing measured; all rules
below are derived from the frozen construction + banked precedent.

- A0-1 control sizes per stage (window-fit feasibility from construction
  diameters, no data): C0-dim = J2-L44 (GLOBAL `[7,11]` needs `D/2-1 >= 11`);
  C0-blind = J2-L44 (frozen cell 0); C0-spread = J2-L28 (banked replication);
  C0-packet/hidden/vacuum = J2-L16 (sheet-size local physics). C3-dim =
  J3-L16 (window fit); C3-blind = J3-L12 (frozen cell 5). C4 = cb-L16
  everywhere; C1 = S8L16 everywhere.
- A0-2 G-t instrument: CFD first-peak arrival (banked `cfd_first_peak`,
  frac 1/2 of global max, + interior-peak check; threshold-free — packet
  precedent: threshold-free readouts ride at true speed, DIM-3-0 tladder
  proved threshold arrivals carry the gamma artifact; global-window max
  rejected in smoke: late resonances, not first passage).
  Threshold-crossing (1e-3 relative) filed as secondary. The C1 ballistic
  gate (`1.0 +- 0.25`) and the washout inequality apply to peak arrivals.
- A0-3 hidden-sector exactness (derived): a sheet-0 hidden delta whose
  NEITHER bit is a stitch endpoint is an EXACT `E = 0` eigenstate of the
  woven `H` (J2 in-sheet death + no incident stitches), and its `Dp =
  |A|^2 - |B|^2` is an EXACT `Lrw` eigenmode (`lam = 1`, twin-pair
  mechanism: same-cell J2 bits have identical neighborhoods, banked
  `prob_diff_sodd_ok` doc) decaying `e^{-t}` in place. Hence C2
  wave/diff remote is predicted EXACTLY blind (in-sheet AND cross-sheet)
  for clean preps. C1: wave in-sheet blind (in-sheet death; verticals
  preserve b-character) but wave cross-sheet VISIBLE (`P_-` propagates
  along the stack) and diff in-sheet VISIBLE at `O(delta/10)` (vertical
  leak breaks the eigenmode). POT: gated `== 0.0` on C0 only (sector
  mixing lets statics leak on C1/C2; filed as mechanism data).
  Prep rule: sheet-0 cell maximizing `min(d_to_stub)` over both bits;
  analyzer requires `min >= 1` (else leg UNMEASURABLE, never fail).
  H gates (frozen): H-val (C0: pmatch + E_ok + local_ok + wave/diff
  in-ok + POT-in `== 0.0`); H-sect (C1: wave-in-ok + diff-in-VISIBLE
  `> 1e-9` + wave-x-VISIBLE + mix pattern adjacent `> 0` /
  non-adjacent `== 0`); H-weave (C2 both seeds: prep-clean + local_ok +
  wave-in-ok + wave-x-ok + diff-in-ok + diff-x-ok + H-g flips `> 100`);
  H-der census completes everywhere. Verdict step 6 JOINT clause reads
  "H-val + H-sect + H-weave + I-a + I-b + I-d pass".
- A0-4 H-g primary/secondary: primary = VMINUS-analog texture pair
  (`sheet_vminus_texture` on the G-a packet background; banked L:vminus
  precedent, gate flips `> 100`); staggered (VPI-analog) pair filed.
- A0-5 C5 RANDOM-step ensemble rule: step 4 fires iff a MAJORITY (`>= 5/8`)
  of the 8 C5 instances match C4 on B+C GLOBAL (`|d_C5 - d_C4| <= 0.25`
  both) while C2 also matches (else the C2/C5 comparison is filed
  descriptively and the ladder proceeds).
- A0-6 hidden remote-diff method: Krylov-exact TV under TRUE `Lrw`
  (irregular graphs have non-orthogonal Lrw eigendecompositions, so the
  banked eigen route is inexact there; Krylov coincides with banked eigen
  on regular graphs — pinned in tests on C0). Wave-remote stays
  banked-eigen (`H` symmetric, exact always).
- A0-7 V-fit small-r bias (derived from exact series, no data): `V(r)`
  log-log slopes approach `d` from BELOW at small `r` (source offset +
  discreteness: exact J2 arithmetic gives LOCAL `[2,4]` ~ 1.69, not 2.0).
  Hence ALL Stage-B/C LOCAL bounds become control-relative + sanity:
  B-val-2D: C0 LOCAL and GLOBAL both in `[1.50, 2.50]`; B-head LOCAL:
  `|d - d_C0local| <= 0.20` + sanity `[1.50, 2.50]`; C-val-2D and C-head
  T-LOCAL identically. GLOBAL bounds unchanged (already control-relative
  + exceed-2). B-disc/C-disc `|d-2|` tolerances unchanged (wide enough).
- A0-8 E/F-head lambda scope (window feasibility from `l_W^pred`, no data):
  NEAR = shells `2..floor(l_W)` needs `>= 3` shells, so E-head/F-head are
  evaluated on `lam in {0.01, 0.02}` (8 records: 2 lam x 2 seeds x 2
  kinds; `>= 6/8` pass). `lam = 0.04` spread = FAR-only filed leg (NEAR
  unmeasurable by construction there).
- A0-9 JOINT replication lambda: hidden + vacuum also run
  `c2-S8L16-lam002-s7`. Step-6 JOINT clause is satisfiable at EITHER
  `lam = 0.04` (H-weave both seeds + I both seeds) or `lam = 0.02`
  (H-weave + I at s7); both filed.
- A0-10 analyzer rule completions (pre-data; silences in sections 3-11):
  part-level Stage-B median needs `>= 4` ok origins (of 8) else
  UNMEASURABLE; F-head = same 8 records as E-head, `>= 6/8` pass; F-B
  theorem leg gates R-records (`bmax < 1e-9`) on bipartite tags, I-records
  filed; H-val POT-in `< 1e-9` (frozen remote bar; CG is iterative, never
  float-exact 0); G-t washout on s7 (gate; s37 filed), needs all `k = 1..4`
  peak arrivals else UNMEASURABLE; J-b `>= 2/3` seeds pass B-head+C-head;
  D-chart-op: `k = 16` NN balls in composite D, classical MDS, normalized
  raw stress, `R = med3/med2` (`R = 1.0` if `stress2 < 1e-9`), validity =
  strict separation `max R(C4 sets) < min R(C0 sets)`, `R_cal` = midpoint,
  headline `R(cell4) < R_cal` on `>= 2/3` sets; D-gamma: per control cell
  (0/5/6) pool directed W pairs over 3 sets, symmetrized tau, BFS graph
  distance, OLS log-log over `2 <= d <= D/2`, `gamma_cal` = median of 3,
  `d_gamma(cell) = gamma_cal x med_sets(W-vol d)`; D-dist refs: cell 0 J2
  quotient, cell 1 stack torus `(x,y,s)` periods `(16,16,8)`, cells 5/6
  dim3 quotient matrices; B/C-mono per-lambda = median over measurable
  seeds, need `>= 3` measurable WOVEN-majority lambdas; lambda regime =
  majority over seeds, headline-eligible iff `>= 5/8` WOVEN; G-a strict
  conjunction over all packet parts/pairs; G-aniso over the 4 direction
  speeds per instance; I gates on C2 tags (controls filed).
