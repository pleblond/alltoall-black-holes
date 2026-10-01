# Stern–Gerlach phenomenology campaign (SG)

Physical experiment: a beam of silver atoms through a non-uniform magnetic
field separates into two discrete components — a field gradient converts an
internal two-state spin projection into spatially separated trajectories.
The phenomenology is internal state + inhomogeneous coupling → discrete
trajectory splitting.

This campaign is stacked on the PR #65 tail (`ac6a140`, P1 wave apparatus
+ one-way derivation + amendments 1–7). It inherits all P1 locked
conventions and ban-lists, cited read-only; sibling tracks are cited
read-only (no code copied except where noted with provenance).

---

## SG-PREREG (FROZEN pre-data; this commit predates ALL SG runs)

### 0. Admission gate (SG-GATE): does an independently discovered two-state sector exist?

The splitter must not create the two states it is supposed to detect.
Admission audit (all sibling inputs read-only, PR tails as of 2026-10-01):

| # | Candidate sector | Source | Verdict | Admissible? |
|---|---|---|---|---|
| 1 | Polarity pair (pure-D5∞ types) | P-track P0/P0b, PR #64 | NULL (D5∞-single-type, 64 runs; mobility continuum + bursty, 48 runs; pure-D5∞ polarity PAUSED) | NO |
| 2 | Handed pair (K+ψ winding) | P3-A, PR #66 | NULL (rung-1 linear test-wave chirality EXCLUDED: planted τ=2.0 0/16, dephasing half-life ~0.25; P3-D nonlinear design frozen, UNRUN) | NO |
| 3 | Bare-J2 sheet sym/anti | MALUS-0, PR #67 | DEAD ([H,S]=0, H·P_anti=0 exact; anti frozen disp=0, sym ballistic; ONE propagating sector) | NO — explicitly banned (see §2) |
| 4 | J2 excitation sector | D15, PR #63 | CLOSED (constraint map: diffusive null, Weyl control, compass ablation, memoryless/time-horn no-go's) | NO |
| 5 | Phase-coherence doublet | COH, PR #70 | PASS with firewall (C=1, τ~1/ΔE) — establishes coherent phase transport ONLY; explicitly NOT discrete detection / Born / entanglement | NO (not a two-state sector) |
| 6 | Path-record qubit | SLIT-2, PR #69 | PASS with external-unitary entangler; path-record degree NOT derived | NO (external, not internal) |
| 7 | Finite K+ψ composites | FEP-0, PR #71 | Pre-data prereg only; no composites banked | NO (nothing discovered yet) |
| 8 | Bound/scattering object | P1 B0/B1, PR #65 | In flight / not fired | NO |

SG-GATE VERDICT: **FAILS — no independently discovered two-state sector
exists.** Consequence (locked): **no SG physics campaign.** SG-2/SG-3/SG-4
are NOT run (designs frozen in §6 for re-entry only). This campaign banks
**SG-0**: apparatus + detector calibration + bare-wave null (SG0-vs-SG1
classification of the only currently-earned physics) + frozen staged design.

Re-entry rule (locked): SG-2 opens ONLY on a future P-track positive
(polarity pair, handed pair, conjugate composite pair, or other), with PI
sign-off that the sector was discovered WITHOUT the splitter and that SG
labels come from the independent discovery (blinded through the splitter).

### 1. Question (load-bearing framing)

NOT "can a graph gradient split trajectories" (any inhomogeneous coupling
deflects or broadens) BUT "does an independently-earned internal two-state
sector predict discrete trajectory classes under a sector-blind
inhomogeneous coupling". While the gate fails, the asked question narrows
to: "what does the currently-earned single-sector wave do in the splitter"
(SG0 vs SG1), with the detector calibrated to prove it COULD see splitting.

### 2. Locked conventions + ban-list

Inherit (P1-PREREG, P1-A1..A7): H hopping-only; Krylov exact-unitary with
norm gates; Gaussian k-packets (σ≪L/6 gated); COM-circular-mean + unwrap +
MSD-bins + C_v + v-fit detectors; background coords as readout basis only
(Stage-0 precedent); partner momenta (k, k+Q), Q=(π,π); mixing as
deviation-from-initial (exact-zero free null, construction not statistics).

SG ban-list (stands for the whole campaign):
- (a) No +/− label anywhere in the coupling law (splitter weights depend
  ONLY on bond midpoint transverse coordinate; sheet-blind and sector-blind
  by construction — pinned).
- (b) No detector-side classifier (no fitting, training, or tuning on
  outputs; split thresholds frozen in §4 pre-data).
- (c) No core-detector / distance-to-core / binding-potential / force-law /
  radiation-pressure (P1 ban-list stands; nothing to ban in, filed anyway).
- (d) No bare-J2 sheet sym/anti decomposition as an SG input sector
  (MALUS-0 dead: H·P_anti=0, anti frozen — §5/S4 re-uses it ONLY as a
  banned-input demonstration, never as a discovery channel).
- (e) No coin (P1-A1 reason stands: coin undefined on irregular graphs).
- (f) SELF-CREATION BAN (load-bearing): any internal difference that appears
  ONLY under the splitter (e.g. sym/anti mobility differences induced by
  H_SG) is splitter-induced by definition and can NEVER be an SG-2 input.
  The splitter is a detector of an already-earned degree, never its source.
- (g) Splitter is APPARATUS (externally imposed inhomogeneous field,
  graph-intrinsic in form), not dynamics: H_SG is used ONLY for ψ evolution
  inside SG runs, never feeds formation, never claimed as emergent from U.

### 3. Apparatus (this commit: `src/bh_graph/stern_gerlach.py` + pins)

Substrate (headline): J2 torus L28 (1568 nodes; matches P1.1b/MALUS-0 L28).
Secondary: torus-grid-30 (single-sheet sanity, P1.1a substrate).
Geometry: longitudinal x = P1.1b-validated axis (packets k=(+0.3,0) minus
branch + partner (π+0.3,π) plus branch + zero-k null; σ=4; launched at
(x0,y0)=(L/2,L/2) (center: the ± branches move ∓x by conjugation
v_+(k+Q)=−v_-(k), so both need ±12 runway — a quarter-point launch would
wrap the plus partner)); transverse y carries the gradient. T=10, dt=0.1
(P1.1b window; disp≈12<L/2=14 no-wrap).

Splitter (frozen form): H_SG = −Σ_{e∈E} J_e |u⟩⟨v| + h.c. with
- J_e = J0·(1+g·ȳ_e) for y-bonds (endpoints differ in y under minimal
  image), J_e = J0 otherwise (x-bonds + pure sheet-flip bonds untouched,
  so P1.1b v_x survives at leading order);
- ȳ_e = minimal-image bond-midpoint transverse coordinate relative to
  launch center y0 (uniform gradient across the packet; seam at ±L/2
  documented, policed by the no-wrap validity gate);
- J0=1 (P1 units), g ladder {0, ±g0/2, ±g0, ±2g0}, g0=0.02 (weak-gradient:
  ±8% weight variation across σ=4; linearity checked, not assumed — §5/S3).

Algebra (pinned, not fitted): H_SG Hermitian + hopping-only (zero diagonal)
for all g; g=0 reduces to −J·A EXACTLY; [H_SG,S]=0 exactly (sheet-blind
weights + S-invariant edge set, MALUS-0 edge-set result reused);
H_SG·P_anti=0 is NOT assumed (bare-H theorem may break under modulation —
S4 measures it; either outcome is filed, neither is SG-2, ban (f)).

Exact nulls (theorems of the frozen form, pinned on small graphs, verified
as campaign validity gates): with R = transverse reflection about y0,
R·H(g)·R = H(−g) and R|ψ0⟩=|ψ0⟩ (symmetric launch) ⟹ Δy(g=0)=0 exactly and
Δy(−g)=−Δy(+g) exactly (Krylov noise ~1e-12; campaign validity tolerance
1e-6 absolute). S1's |Δy(+g0)| is therefore THE measurement (SG0 vs SG1).

Readouts (per run): Δy (unwrapped transverse COM shift), transverse profile
P(y)=Σ_{x,b}|ψ|², width growth vs matched free flight, norm/accounting
(hard 1e-9), split statistic (§4) at final frame + last-20% persistence,
free-flight replication (v_x within 10% of banked P1.1b 1.2110 at g=0).

Validity gates (run INVALID if violated, filed not tuned): norm/accounting
1e-9; COM within L/4 of launch + transverse 1D RMS width<L/4 + seam-region
weight<1% (no-wrap/seam; the seam-weight gate is load-bearing, the width
gate is backstop — set at L/4 so a genuine SG1-broadening outcome ≤75%
cannot void its own run); raw branch purity ≥80% (P1.1b rule); R²>0.99
displacement fit (±k packets).

### 4. SG detector (frozen primary + ladder mapping)

Primary SPLIT statistic on smoothed P(y) (Gaussian σ_smooth=1 site): take
the top two local maxima with separation >3σ0 (σ0 = launch σ; threshold
achievable on L28: 3σ0=12 < L/2=14); depth = 1 − valley/min(peaks) with
valley = min over the shorter arc; minority weight = weight within
±1.5σ0 of the smaller peak (windows disjoint at threshold separation).
SPLIT-FIRES ⟺ depth>0.5 AND separation>3σ0 AND minority weight>20%
(all three; firing must persist over the last 20% of the window, else
transient — prevents single-frame flukes).

Ladder mapping (frozen):
- SG0: no firing AND |Δy|<0.5σ0 AND width growth <25% vs free (splitter
  does nothing measurable).
- SG1: no firing BUT (|Δy|≥0.5σ0 OR broadening ≥25%) (common-mode and/or
  broadening response — expected physics of a sector-blind gradient).
- SG2: SPLIT-FIRES with branch COMs predicted by independently-known
  sectors (≥90% label purity per branch) — REQUIRES admission; while the
  gate fails this cell is VOID and any firing = apparatus artifact to be
  owned as such, never a discovery.
- SG3: SG2 + reversal (g→−g swaps branch Δy's within 20%) + removal (g=0
  → single peak) — GATED on SG2.
- SG4: sequential SG_A→SG_B→SG_A with independently defined, pre-frozen
  analyzer orientations (gradient-axis rotation is a legitimate distinct
  orientation ONLY with pre-frozen axes; criterion is nontrivial basis
  dependence — middle analyzer changing outer correlation — not mere
  re-splitting) — GATED on SG2 + orientation derivation (NOT designed here
  beyond this paragraph).

Calibration (detector validation, NOT physics — must pass or detector is
invalid, STOP): synthetic two-Gaussian P(y) on a length-64 ring
(σ=4, separation 6σ0=24) MUST fire; single Gaussian MUST NOT fire; flat
profile MUST NOT fire; free-flight P(y) (g=0) MUST NOT fire.

### 5. SG-0 bank (runs AFTER this prereg commit; beast; script `scripts/sg0_bank.py`)

- S0 free-flight replication (g=0; 3 headline packets): P1.1b-class gates
  (v/α/R²/purity/mixing) + Δy=0 exact-null + no-split. Must pass or STOP.
- S1 splitter response (g=+g0; 3 headline + full 5-packet robustness at
  {0,+g0}): file Δy, width, split statistic → SG0-vs-SG1 per packet
  (descriptive classification; no fire role beyond the ladder).
- S2 reversal (g=−g0, −g0/2, −2g0): |Δy(+g)+Δy(−g)|<max(0.2|Δy(+g)|,0.1σ0)
  (exact-theorem validity check with measurement slack; SG3-analog for
  common mode — filed as CONTROL, never called SG3).
- S3 linearity (+2g0, +g0/2): |Δy(2g)−2Δy(g)|<max(0.25|2Δy(g)|,0.1σ0)
  (weak-gradient check; if violated, gradient is strong — filed, and SG1
  claims weaken to qualitative).
- S4 banned-input demonstration (sheet sym/anti/sheet0 through g=+g0,
  MALUS-0 family port): file anti mobility (MALUS-0 replication test under
  the splitter) + sym/anti Δy signs (both common-mode or anti frozen).
  Explicitly NOT SG2 regardless of numbers (bans (d)+(f)).
- S5 torus-grid-30 secondary (P1.1a packet k=(0.5,0) σ=4 T=25): S0–S2 at
  reduced scope (common-mode universality across substrates).

SG-0 bank COMPLETE ⟺ S0 passes + S1–S5 filed with validity gates green.
Bare-wave verdict is SG0 or SG1 (either consistent with gate-fails;
NEITHER is SG2 and nothing here is called spin).

### 6. Gated stages (NOT run; frozen for re-entry)

SG-2 (opens ONLY on a future earned sector + PI sign-off): sector-labeled
preparations (labels from the independent discovery, blinded through the
splitter); protocol mirrors S1; FIRES ⟺ split + label-side prediction
(each sector → predicted branch, ≥90% purity per branch) + branch-level
S2/S3 analogs. SG-3: SG-2 + reversal/removal on branches (thresholds §4).
SG-4: sequential analyzers per §4 (orientations derived independently and
frozen pre-data in the re-entry amendment). Re-entry REQUIRES a new
pre-data amendment naming the sector, its independence proof, and the
blinding protocol — this prereg does not pre-approve any sector.

### 7. Non-interference (locked)

No U modifications; no formation runs; no ψ→G channel; no D1 runs; no
electron constants anywhere; P1/P2/P3/D15 read-only (cited, untouched);
no new law (splitter = apparatus per ban (g)); no P3-D / FEP inputs.

---

## Amendments (pre-data only; numbered)

SG-AMENDMENT-1 (weak-gradient ladder + gate recalibration; PRE-RERUN:
pilot-1 opened below, pilot-1 Δy-verdict SUPERSEDED (gate-miss class,
P1-A3 precedent), rerun cells gated on this amendment commit).
PILOT-1 DISPOSITION (beast, `sg0_bank.py`, L28/T=10 + TG30/T=25):
- BANKED: Scal PASS (two-Gaussian depth 0.97 fires; single/flat silent);
  exact theorems in campaign conditions (Δy(0)=0 to 1e-13 all packets;
  Δy(−g)=−Δy(+g) to 4 decimals all 6 pairs — S2 6/6 TRUE); P1.1b
  replication to 4 decimals (v=1.2039/1.2110 symmetric pair, α=2.07/2.09,
  R²≥0.9997, purity 99.999%, mixing ≤1e-12, zero-k exact null); S4
  (anti EXACTLY frozen disp=0 at BOTH g=0 and g=+g0 — H_SG·P_anti=0
  survives sheet-blind modulation, stronger than prereg assumed;
  sheet0 50/50 at g=0 (disp 2.24), common-mode dy=+6.27 at +g0);
  NO SPLITTING in all 30+ pilot cells including wrap-void ones
  (detector robustness: split=False everywhere, 0/30+ firings).
- SUPERSEDED (gate-miss, owned): (i) seam<1% set blind — free transverse
  spread (w 4→6.5 over T=10, 11% seam even at g=0 where NO discontinuity
  exists) voids S0's seam sub-gate while every physics sub-gate passes;
  (ii) g0 ladder assumed perturbative — response is non-perturbative and
  non-monotonic in g (dy: +8.46→+10.95→+4.96 over g0/2→g0→2g0;
  S3 linearity 0/4; several cells wrap-void with disp up to 16.3>14).
  Character: large-amplitude coherent transverse motion (Bloch-like
  oscillation phase samples, NOT steady deflection); minus/plus-branch
  dy IDENTICAL to 4 decimals every cell (filed; possible exact
  transverse branch-blindness — followup, not pursued here).
GATE CHANGES (cause shown, conclusions threshold-independent):
- (A1.1) S0 seam bar → filed-spread (no bar at g=0: uniform H has no
  seam discontinuity; COM exact by theorem; transverse spread is free
  dispersion, measured not barred). All other S0 sub-gates stand;
  S0 re-gated on FILED pilot numbers (no rerun — deterministic).
- (A1.2) g≠0 seam bar 1%→5% (discontinuity-sampling guard; no-split
  conclusion holds in every cell incl. 56%-seam ones, so the bar binds
  only Δy-precision, never Q1). disp<L/2 + wT<L/4 stand.
RERUN CELLS (script `scripts/sg0b_weak.py`, this commit):
- (A1.3) S1b/S2b/S3b weak ladder: J2 L28 minus/plus × {±g0/8, ±g0/4}
  (same prep/readouts/T); S2b reversal (same tolerance); S3b linearity
  over weak pairs (|Δy(g0/4)−2Δy(g0/8)|<max(0.25|·|,0.1σ0)).
- (A1.4) S5b: torus-grid-30 × {±g0/4} (same readouts); S5 re-gated per A1.2.
VERDICT RULE (locked): Q1 (splitting?) over ALL cells ever run (pilot +
rerun, valid or void — 0 firings required); Q2 (SG0-vs-SG1) over VALID
weak-ladder cells only, per-regime labels filed separately (weak-gradient
label is the bare-wave headline; strong-gradient pilot cells filed as
large common-mode oscillation, SG1-class response, void-for-Δy-precision).
Both S3b outcomes allowed: linearity-pass → perturbative SG1/SG0 per bar;
linearity-fail → "no linear regime down to g0/8; oscillatory common-mode"
(SG1-class by response magnitude). No further cells without Amendment-2.

## Verdicts (filed post-data; SG-0 bank gated on prereg commit)

SG-0 pilot-1: RAN (beast; disposition per Amendment-1 above — Scal/S2/S4/
no-split banked; Δy-verdict superseded). Rerun (S1b/S2b/S3b/S5b): RAN
(beast; disposition per Amendment-2 above — S2b/S3b pattern + no-split
banked; Δy-verdict superseded). Sine rerun (S1c/S2c/S3c/S5c): RAN (beast;
verdict below).

SG-AMENDMENT-2 (seam-free sine apparatus; PRE-RERUN: S1b opened below,
S1b Δy-verdict SUPERSEDED (same gate-miss class), S1c gated on this
amendment commit).
S1b DISPOSITION (beast, `sg0b_weak.py`, linear gradient):
- BANKED: S2b reversal 4/4 TRUE (exact to 4 decimals: ±2.5553, ±4.3988);
  S3b linearity 2/2 TRUE (dy +2.56→+4.40 over g0/8→g0/4;
  |4.40−2×2.56|=0.71<1.28 — linear-response regime FOUND); no-split in
  all 10 rerun cells (40+ cells total, 0 firings — robustness extended);
  minus/plus dy identical to 4 decimals again (third replication).
- SUPERSEDED: valid=False 10/10 (seam 9–15% vs A1.2 5% bar; disp<14 and
  wT<L/4 pass — ONLY the seam binds). The seam bar binds Δy-precision
  legitimately here (defect sampling O(seam·L/2)~1.3 confounds the
  |Δy|≥2 bar), so the bar must NOT be relaxed again (no shopping).
OWNED ERROR: a linear λ(ȳ) on a torus FORCES a seam discontinuity, and
free transverse spread (w→6.5) guarantees the packet samples it. Fix the
APPARATUS, not the bar (TUN-A2 precedent: geometry change after a
wrap-contamination void).
APPARATUS CHANGE (this commit, pinned before any sine run):
- H_SG2 ("sine"): y-bond weights 1+g·(L/2π)·sin(2πȳ/L) — uniform gradient
  g at the packet, periodic, ZERO seam (same exact theorems: R·H(g)·R =
  H(−g) since sin is odd; [H_SG2,S]=0 since weights stay y-only;
  g=0 → bare exactly; all pinned + sine exact-nulls pinned, 18 pins).
- Nonlinearity across the packet filed (shape frozen; S3c still tests
  response-linearity in g, which holds for any fixed shape in weak-g).
- `splitter_hamiltonian(..., shape="linear"|"sine")` (default "linear":
  pilot cells reproducible); `run_cell(..., shape=...)` passthrough.
RERUN CELLS (script `scripts/sg0c_sine.py`, this commit):
- S1c/S2c/S3c: J2 L28 minus/plus × {±g0/8, ±g0/4} (sine; same prep/T);
  S2c reversal + S3c linearity (same tolerances); S5c: TG30 × {±g0/4}.
- S0c: NO rerun (H_sine(0)=H_linear(0)=bare — filed S0 stands as is).
- Validity (A2.3): disp<L/2 + wT<L/4 + norm/accounting 1e-9; seam filed
  as DIAGNOSTIC-only (no defect exists to sample). Verdict rule stands
  (Q1 all cells ever; Q2 valid sine weak cells; both S3c outcomes
  allowed per A1). No further cells without Amendment-3.

---

## SG-0 VERDICT (banked 2026-10-01; beast; scripts `sg0_bank.py` + `sg0b_weak.py` + `sg0c_sine.py`)

### Q1 (splitting?): NO — 0 firings in 50+ cells across all stages/shapes/gradients

Split=False in every cell ever run: pilot S0/S1/S1r/S2S3/S4/S5 (linear,
30+ cells incl. wrap-void), S1b/S5b (linear weak, 10 cells), S1c/S5c
(sine weak, 10 cells). S1c split details are exactly zero
(depth=sep=minority=0.0 — single transverse maximum, not a near-miss),
and no cell fired at ANY frame (tail_fires_any=False throughout).
Detector trust: Scal PASS (synthetic double depth 0.97 fires;
single/flat/free silent), so the null is detector-competent, not
detector-blind. The SG2 cell is VOID as gated (admission fails) — and
the data independently show no splitting to misread.

### Q2 (bare-wave ladder): SG1 — common-mode deflection, linear-response, reversal-exact

S1c (sine, 8/8 valid: disp 12.3–12.9<14, wT 5.6–6.1<7, norm ~1e-13):

| cell | Δy | wT (free 6.48) | split | ladder |
|---|---|---|---|---|
| minus/plus ±g0/8 | ±2.2957 | 6.11 | none | SG1 |
| minus/plus ±g0/4 | ±4.0980 | 5.61 | none | SG1 |

- S2c reversal 4/4 TRUE (Δy(−g)=−Δy(+g) exact to 4 decimals — theorem).
- S3c linearity 2/2 TRUE (|4.0980−2×2.2957|=0.49<1.15 — weak-g regime).
- SG1 via the Δy bar (|Δy|=2.30/4.10 ≥ 0.5σ0=2.0). Broadening: none —
  wT sits BELOW free (6.11/5.61 vs 6.48; gradient slightly focuses).
  Owned nuance: the bank script's ladder broadening term compares
  within-run growth (free-dispersion-dominated); the vs-free comparison
  above is the correct one and strengthens "deflection without
  broadening". Labels unaffected (Δy bar binds alone).
- Longitudinal: v=1.22–1.28 vs free 1.20–1.21 (≤6% speedup — filed).
- Bare-basis mixing O(1e-6) (splitter breaks translation invariance;
  apparatus characterization, not B0-mixing).
- Minus/plus-branch Δy IDENTICAL to 4 decimals (4th replication across
  pilot/S1b/S1c) — probable exact transverse branch-blindness of the
  sector-blind splitter (followup conjecture, not claimed here).

S5/S5b/S5c secondary (torus-grid-30): reversal TRUE + no-split TRUE at
every gradient (dy=±5.94 sine ±g0/4, ±9.35 pilot ±g0); valid=False under
A2.3 only via the disp<L/2=15 bar (disp≈25 — over-strict for T=25;
P1.1a-consistent no-wrap disp<L=30 holds). Filed as descriptive support
(SG1-class common-mode, substrate-universal); the bar stands, no
amendment spent on a secondary flag.

Strong-gradient pilot cells (linear, g0/2–2g0): large-amplitude coherent
transverse motion, non-monotonic in g (Bloch-like oscillation-phase
samples, several wrap-void) — SG1-class response, void-for-Δy-precision,
filed per Amendment-1. Not the headline regime.

### Gate status: STILL FAILS — SG-2/3/4 remain gated (no re-entry)

Nothing in SG-0 discovers a two-state sector (S4: anti frozen at both
g=0 AND g=+g0 — H_SG·P_anti=0 survives modulation; sheet0 50/50
common-mode). The bare wave is SG1: a sector-blind gradient deflects it
as a whole and never splits it — exactly what the design principle
predicts when no internal sector exists. No outcome here is called spin;
SG-2 opens only on a future P-track positive per the re-entry rule (§0).

### Non-interference audit: clean

No U/formation/D1 runs; no ψ→G channel; P1/P2/P3/D15 read-only;
no electron constants; no new law (splitter = apparatus, ban (g)).
Full suite: <see PR/suite log>.
