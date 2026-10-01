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

## Amendments (pre-data only; numbered; none yet)

## Verdicts (filed post-data; SG-0 bank gated on prereg commit)

SG-0 bank: NOT RUN (awaiting prereg commit + beast staging).
