# COH: phase coherence of the scalar J2 wave (bare-J2 characterization)

Fork from the validated P1.1 bare-J2 wave apparatus (PR #65 tail): scalar
complex psi, continuous-time evolution under H = -A, exact J2 torus,
analytically calibrated packet propagation, norm conservation, validated
momentum preparation. No D5inf formation, no DNLS nonlinearity, no detector
model, no new internal degree of freedom, no which-path ancilla enters
COH-0/1/2/3. This file is the COH ledger (preregs + verdicts). Sibling
tracks P1 (ballisticity, PR #65) and P3 (handedness, PR #66) share the base
only; no cross-branch imports. D14 sections in docs/DEFERRED.md are FROZEN
(P3 precedent); COH does not edit them.

Question: does the independently validated complex scalar J2 wave preserve a
predictable relative phase across separated propagation paths, and what
intrinsic coherence time/length follows from its dynamics? This is a
wave-sector characterization experiment, not a test of the Born rule or
quantum measurement.

Charter (locked):

- One law for all arms: both paths evolve under the SAME H = -A on the SAME
  bare J2 torus. The only arm differences are preparation (position/momentum)
  and the imprinted relative phase phi. Any loss of phase predictability is
  therefore propagation physics, never law asymmetry.
- Split = prepared superposition, recombination = linear addition. There is
  no physical beamsplitter on bare J2; the reflection-symmetric construction
  is psi_AB = psi_A + exp(i*phi)*psi_B (unnormalized, definition-literal)
  with psi_A/psi_B identical-k Gaussians at mirror positions (R in Aut(J2),
  pinned). This tests propagation coherence, not splitter physics; a
  physical Y-junction interferometer is QUEUED as followup, not claimed.
- Normalized headline: raw fringe visibility confounds envelope overlap
  (kinematic) with dephasing. The headline dephasing observable is normalized
  coherence C = V_meas / V_pred with V_pred = |<psi_A|psi_B>| from the
  INDEPENDENTLY evolved single arms (parameter-free). Unitary bare-J2
  predicts C ~= 1 everywhere; the operational (l, tau) scales come from the
  V curves and are compared to the independently measured spectral spread.
- No tuning after curves: sigma set, phi set, grids, regions, windows, and
  all verdict thresholds below are frozen here. Amendments are numbered,
  pre-data, and committed before the runs they govern (D14 discipline).

## Geometries (locked)

Substrate: j2_torus_graph(28) (N = 1568, P1.1b substrate), H = -A, J = 1,
dt = 0.1 (P1 precedent), packets via ballistic.gaussian_packet on
2D-projected J2 coords (P1.1b precedent), prep point (x0, y0) = (7, 14).

- G-long (longitudinal pair): A at (7+Dl/2, 14), B at (7-Dl/2, 14), both
  k = (+0.3, 0). Symmetric under R_x about x0 = 7 (midpoint). Primary for
  COH-2 V(Dl). Dl grid {0,2,4,6,8,10,12} (frozen, all even: midpoint exact).
- G-trans (transverse pair): A at (7, 14+d/2), B at (7, 14-d/2), both
  k = (+0.3, 0). Symmetric under R_y about y0 = 14. COH-0 geometry
  (d = sigma). Swap/symmetry demo.
- G-counter (counter-propagating): both at (7, 14), k_A = (+0.3, 0),
  k_B = (-0.3, 0) (both P1.1b-validated, branch-minus-pure). R_x about 7
  maps each arm to itself-position with flipped momentum, i.e. swaps arms.
  COH-1 spatial-fringe geometry (standing-wave spacing pi/k ~= 10.47).

Phase set: 8 phases {j*pi/4, j = 0..7} for all V fits; the 4-subset
{0, pi/2, pi, 3pi/2} embedded for the COH-1 shift/conjugation test.
Max/min over 4 phases is never used; V always comes from the least-squares
fit I(phi) = A + B*cos(phi+delta), V = B/A (exact linear lstsq).

Readout regions (locked): PRIMARY is whole-graph summed intensity (no
region tuning possible). SECONDARY axis region = torus-ball radius 1
around the comoving axis point (fixed rule: x_com = COM_x of arm A at
readout, y0 = 14; coherence.axis_region). Fringe profiles (G-counter)
use the x-axis row (y = 14, both sheets summed).

Validity gates (every evolved run): norm-drift < 1e-8 (relative; unnormalized
states: preservation, not == 1); per-arm wrap disp < L/2 = 14 (P1.1b rule);
per-arm branch mixing < 1e-6 in the bare-J2 branch basis (P1.1b threshold).
Purity/w0 per arm filed, NO gate (broadband packets carry flat-band weight
by construction; that is the COH-3 point). Determinism: no RNG anywhere;
one bitwise-rerun check filed in COH-0.

## COH-0 -- interferometer calibration (prereg, FROZEN pre-data)

Cells: G-trans, d = sigma = 4, T in {0, 5} (T = 0 prep-only, T = 5 evolved).

1. Linearity (HEADLINE): ||U psi_AB - (U psi_A + e^{i phi} U psi_B)|| /
   ||U psi_AB|| < 1e-8 for all 8 phi at T = 5 (joint evolutions run only
   here; COH-1/2/3 recombine mathematically on banked linearity).
2. I_int identity: max|I_AB - I_A - I_B - 2 Re(e^{i phi} psi_A* psi_B)|
   < 1e-12 pointwise, T = 0 and T = 5, all 8 phi (psi_A/B = independently
   evolved arms).
3. Swap/symmetry: scalar observables (V, |S|, sums) invariant under A<->B
   exchange to < 1e-9; prep symmetry ||R_* psi_A - psi_B|| < 1e-12;
   R_x/R_y edge-set invariance verified on L = 28 (pins cover L = 4/6).
4. Single-path: arm evolved alone from joint-prep storage is bitwise
   identical to fresh-prep evolution (bookkeeping check); I_A with B
   blocked reproduces independent I_A.
5. Determinism: one full rerun bitwise identical.

COH-0-PASS <==> all checks pass at T = 0 and T = 5. Else APPARATUS-FAILURE
(not physical decoherence). COH-1/2/3 gated on COH-0-PASS.

## COH-1 -- controlled relative phase (prereg, FROZEN pre-data)

Cells: G-counter at T = 0 (spatial fringes) + G-long Dl = 4 at T = 0
(breathing) + one linearity spot-check per geometry (all 8 phi, T = 5,
same 1e-8 bar as COH-0: banked linearity extends across geometries).

1. G-counter fringe fit (HEADLINE): per phi, x-axis profile fit
   I/I_sum - 1 = V_sp cos(2 k x + theta) with k by grid scan: V_sp > 0.9,
   k_fit within 10% of 0.3, fit R2 > 0.999 (all 8 phi); fringe-phase slope
   d theta/d phi = 1 within [0.95, 1.05] (unwrapped linear fit). The
   pattern shifts continuously with phi at unit slope.
2. G-long sinusoid: whole-graph I(phi) fit R2 > 0.999; V within 5% of
   |S|_pred computed at prep; delta within 0.1 rad of arg(S)_pred
   (parameter-free phase prediction).
3. Conjugation: I(x; -phi) = R-mapped I(x; +phi) to < 1e-9 pointwise
   (all phi in the 4-subset, both geometries; R = geometry symmetry).

COH-1-PASS <==> all bar items pass. Else APPARATUS-FAILURE (the readout
does not measure relative phase). Establishes phase readout vs focusing.

## COH-2 -- coherence vs path/time separation (prereg, FROZEN pre-data)

Cells: G-long, sigma = 4, T_read = 5 (fixed), Dl in {0,2,4,6,8,10,12}
(7 cells); T-sweep Dl = 0, T in {0,2,4,6,8,10} (6 cells); Dt set {0,2,4}
at T = 5 (B evolved T+Dt, A evolved T, recombined mathematically).

Per Dl cell: 8-phase sweep (mathematical recombination of the evolved
arms), whole-graph I(phi) sinusoid fit (R2 > 0.999 required; cell invalid
otherwise) -> V_meas; V_pred = |<psi_A|psi_B>| from the same evolved arms
-> C = V_meas / V_pred.

1. C gate (HEADLINE): |C - 1| < 0.05 in all 7 Dl cells (phase
   predictability preserved; no anomalous dephasing on bare J2).
2. V(Dl) scale: Gaussian fit V = exp(-Dl^2/2 l^2) R2 > 0.95; l filed as
   the operational coherence length (includes spreading at T_read).
3. C(T) gate: |C - 1| < 0.05 at all 6 T-sweep cells (propagation itself
   preserves coherence) + wrap/norm/mixing validity gates each cell.
4. Dt-consistency: V(Dt) vs V(Dl = v*Dt) interpolated agree within 10%
   (v = measured single-arm speed; Dt and Dl are the same knob on fixed H).

COH-2-PASS <==> items 1-4 pass. Deviation taxonomy (locked): C deviating
systematically with healthy norms/wrap = ANOMALOUS-DEPHASING (physical,
file the scale); norm/wrap/mixing failure = APPARATUS-FAILURE. For
monochromatic unitary propagation no V decay is required; finite-bandwidth
V loss is compared to spectral spread (COH-3), never auto-interpreted as
environmental decoherence (there is no environment).

## COH-3 -- spectral-spread test (prereg, FROZEN pre-data)

Cells: COH-2 Dl sweep repeated at sigma in {2, 3} (sigma = 4 banked from
COH-2 and REUSED for the ratios -- filed reuse, deterministic-identical;
no rerun); T = 0 anchor per sigma in {2, 3, 4} (prep-only, no evolution).

Per sigma: dE(sigma) = spectral_spread at prep (exact); v(sigma) =
single-arm COM speed (P1.1b protocol, T = 10 rerun per sigma; sigma = 4
cross-checked against banked P1.1b 1.2110187 within 1e-9); l(sigma) from
the Gaussian V fit (R2 > 0.95 required per sigma, else that sigma is
excluded from ratios WITH filed reason -- pre-registered handling, not
shopping); tau(sigma) = l(sigma) / v(sigma).

1. T = 0 anchor (VALIDITY): tau*dE ratios tau(2)dE(2)/tau(4)dE(4) and
   tau(3)dE(3)/tau(4)dE(4) within [0.8, 1.25] (near-algebraic at prep;
   failure = apparatus failure in the dE ruler or overlap math, COH-3
   invalid).
2. T_read headline (PHYSICS): the same two ratios at T_read = 5 within
   [0.67, 1.5] (window allows differential spreading across the x2
   bandwidth range; absolute scale never fitted). tau_coh ~ 1/dE holds
   across frozen bandwidths.
3. P3-A anchor (DESCRIPTIVE, no verdict weight): file tau*dE vs the P3-A
   point (spread 2.95, half-life 0.2-0.3, product ~0.6-0.9). Different
   preparation class (localized multimode vs narrowband packets); agreement
   is mechanistic corroboration, disagreement is filed without penalty.

COH-3-PASS <==> anchor validity + both headline ratios in range. Else NULL
(the V-decay scale is not set by dE alone; file the measured scaling).
Bandwidths were frozen above; no sigma tuning after seeing curves.

## Later controls -- queued, no prereg weight in the initial verdict

Only after bare-J2 coherence is banked:

1. COH-F: repeat on frozen D5inf formed graphs (formation-induced
   coherence loss; own formation prereg when queued).
2. COH-N: compare with nonlinear P3-D states IF that campaign
   independently establishes phase locking (gated on P3-D verdict).
3. Path-record/decoherence: only after an existing model degree of freedom
   is shown to carry path information. No artificial which-path ancilla is
   introduced solely to destroy interference.

Physical Y-junction (splitter physics) queued as apparatus followup.

## Interpretation (locked)

COH-PASS (initial) <==> COH-0 AND COH-1 AND COH-2 AND COH-3 all PASS.
It establishes coherent phase transport and an operational coherence scale
for the scalar graph wave. It does NOT establish: photons; discrete
detection; the Born rule; wave-function collapse; entanglement; uniquely
quantum interference. The strongest result is mechanistic agreement between
independently measured spectral spread and loss of relative-phase
predictability.

## Verdicts (append below; nothing above changes post-freeze except via
numbered pre-data amendments)

## Amendment-1 (slope-magnitude convention, committed PRE-data, pre-run)

Seed: writing the COH-1 analysis I found the fringe-phase slope sign is a
fit-convention artifact (model V cos(2kx+theta) vs physics cos(2kx-phi)):
the apparatus reports theta(phi) = -phi + const, i.e. slope -1 for perfect
unit-shift response. Fix (locked): the COH-1 slope bar is |slope| in
[0.95, 1.05] (magnitude; sign filed). All other bars stand.
