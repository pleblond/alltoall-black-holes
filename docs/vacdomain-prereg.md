# VACDOMAIN0-PREREG — Interfaces between disconnected joint-vacuum components (FROZEN PRE-DATA)

**Status:** apparatus + grids + bars + gates + ladder frozen; campaign NOT
YET RUN. Commit predates ALL VAC-DOMAIN-0 campaign runs.

## Mission

Study fixed-geometry interfaces between disconnected JOINT components
(VAC-COMP-0 manifold, even L: VPLUS-ray, VPI-ray, hidden RP^1 circle x R+)
and determine whether interfaces are stationary, radiative, dispersive
(broadening), or ordinary spectral beating.

For even L, compare V+|Vpi, V+|Vhidden, and Vpi|Vhidden, using
preregistered points on the hidden RP^1 component.

## Frozen inputs (read-only, never modified)

VAC-FIELD-0 (JOINT ladder, BARS, candidate shapes, relational readouts);
VAC-COMP-0 (hidden circle, VSTAG, ledger signatures, component inventory);
SYM-0 (X/(R x U(1))); MALUS/QUOT ([H,S]=0, H P_-=0, square-walk symmetric
sector); HIDDEN-0/HIDDEN-BR (virtual ledger apparatus, descriptive use);
ZERO-0 (protection form, cited); EM-0 (Bloch spectrum, cited); RESPONSE-0
(banked front speeds v_field=7.95, v_quad~5.94, cited); FIELD-0 (witness
I=0 null form); P1 ballistic (Krylov evolve_fixed, H=-A).

## Frozen ontology and firewall

H = -A on the frozen J2 torus (J=1, hbar=1). No H modification, no onsite
terms, no edge weights, no vacuum potential, no geometry-update rule, no
amplitude tuning, no post-data profile tuning (joins are sharp stitches,
fixed below), no matter/particle/defect language, no cosmology,
phase-transition, geometry-dynamics, or vacuum-preference claims. Virtual
HIDDEN-BR ledgers are anatomy only: never select, fire, or rank.

## Join construction (frozen, sharp, no smoothing)

- Slab stitch: psi_join[v] = psi_A[v] if cell(v) in A else psi_B[v],
  normalized to unit norm. A = {x < L/2} (x-cut) or {y < L/2} (y-cut);
  FRAC = 1/2 frozen (single frozen width; two cuts on the torus).
- Both sheets of a cell share one region, so P_- joins stay exactly P_-
  pure (D-FLAT premise).
- Bulks: VPLUS, VPI (vf.candidate_shape), H0..H3 = hidden-circle points
  cos(a) VMINUS + sin(a) VSTAG at a = 0, pi/6, pi/3, pi/2
  (H0=VMINUS, H3=VSTAG; interiors JOINT by VACCOMP 0H).
- Pairs: 9 disconnected (VPLUS|VPI, VPLUS|H*, VPI|H*), 2 hidden-hidden
  same-component (H0|H3, H1|H2), 3 same-vacuum (no-interface controls).
- Sizes: L = 4 (exact), 8 (diag), 28 (headline Krylov); even only.
- Orientations: x, y. DT = 0.02 (resolves dE<=16 beats, period>=0.39).
- T_CLEAN(L) = 0.9 (L/4)/8 (bulk-pristine horizon); T_MEAS(L) =
  min(L/8, 4.0) (interface/front horizon; wrap flagged, not gated).
- V_MAX = 8.0 frozen reference; V_QUAD = 5.94 banked quadratic front.

## Pre-data analytic results (proofs in vacdomain.py, pinned in tests)

- D-NOGO: E_A != E_B forbids stationary joins (interior nodes demand both
  eigenvalues; needs slab width >= 4, i.e. L >= 8; L=4 slabs are
  all-interface and are settled by direct evolution + best residual).
  All 9 disconnected pairs: dE = 8 or 16 -> no stationary join exists.
- D-FLAT: any P_- join is an exact E=0 eigenstate (H P_- = 0 banked), so
  hidden-hidden joins are exactly stationary (frozen, zero drift).
- D-SWAP: (x,y,b)->(y,x,b) is an exact J2 automorphism mapping x-cut joins
  to y-cut joins; orientation covariance is exact (bar 1e-9).
- Sector weights of joins: VPLUS|VPI w_sym=1; hidden-hidden w_anti=1;
  mixed-sector joins exact halves (equal slab weights).
- Same-vacuum joins equal the global vacuum exactly (no interface).
- VPLUS|VPI S-profile plateaus 8/N -> -8/N; H0|H3 S-blind (both 0) with
  B_SX plateaus +1/N -> -1/N. VPLUS|H0 is B_SX-blind (+1/N both sides):
  B_SX is filed everywhere, gated nowhere.

## Observables (frozen estimators, no tuning)

- Interface band: nodes within 2 cells of either cut; band edges have >=1
  end in band. Interface-local rho/B/J drifts vs t=0 (bar 1e-8).
- Bulk centers: nodes at maximal cut distance (L=28: 7 cells).
- Sector trace (conserved), P_- frozen check, energy + excess vs
  volume-average bulk prediction.
- 1D transverse-averaged profiles S / B_SX / rho; plateaus from slab
  mid-columns; width = pooled 10-90 count + gradient RMS (anatomy).
  Step ratio + plateau drifts decide RADIATIVE vs MIXING (below).
- Disturbance front of |drho| from the cuts; thresh =
  max(1e-8, 0.05 global max); linear fit -> v, R^2, reach (frozen).
- Dense spectral superposition vs Krylov (L<=8), linearity witness
  I = ||U(a+b)-Ua-Ub|| (FIELD-0 form), |c_k| support constancy.
- Ledger anatomy (B, L landscapes + band/off means): recorded only.

## Gates (applied by scripts/vacdomain_analyze.py)

- G0 BULK: all 6 bulks x 3 L re-ladder JOINT (all 10 checks).
- G1 NOGO: analytic no_go for all 9 disconnected (dE 8/16), none for
  hidden-hidden; numeric: L>=8 interior medians match bulk energies
  (dev<1e-9) + best residual >1e-6; L=4 empty interiors + residual>1e-6;
  hidden-hidden residual <1e-9 (exact eigenstates).
- G2 FLAT: hidden-hidden joins stationary + P_- pure + frozen (all L,
  both orientations).
- G3 NONSTAT: all 9 disconnected joins nonstationary (all L, both ori).
- G4 SPECTRAL: L=4/8 dense match <1e-8, I<1e-10, support drift<1e-9;
  sector conserved <1e-9, P_- frozen <1e-9, energy drift <1e-9;
  mixed-sector P_- weight exactly 1/2.
- G5 RADIATIVE (L=28 headline, per disconnected pair x orientation):
  fronts moving + reach>=3 cells + R^2>0.8 AND S-step ratio>0.5 AND both
  plateau drifts <20% of step. Speed filed vs V_QUAD (no gate). Width
  growth filed as broadening anatomy (a radiating sharp step widens the
  disturbed zone ~2vt, so growth never gates).
- C controls: same-vacuum stationary + zero width; global-phase
  invariance <1e-9 (L=4/28); x/y covariance <1e-9 + equal initial widths;
  wrap-free at L=28 (bulk <10% of interface, or both <1e-8);
  ledgers finite. L=4/8 bulk drifts filed (no tail-free bulk exists).

## Ladder (all four verdicts data-reachable)

- VACDOMAIN-NOJOIN iff G0 or G4 or C fail (bulk/apparatus failure).
- Else VACDOMAIN-STATIONARY iff G3 fails (a disconnected join is still).
- Else VACDOMAIN-RADIATIVE iff G2 and G5 pass for every pair.
- Else VACDOMAIN-MIXING (broadening/beating without clean radiative
  signature: fronts absent, or step/plateaus erode).

## Pre-prereg calibration (apparatus checks, not campaign data)

Smoke runs during development (local, /tmp only, never in data/) fixed
three estimator choices before freezing: (1) bulk centers strict d==dmax
(L=4 has no true bulk -> Cclean at L=28 only); (2) width-growth-bound
replaced by step/plateau persistence (radiation widens the disturbed zone
by construction); (3) front reference V_QUAD=5.94 (quadratic readouts)
with R^2>0.8 + reach>=3, speed filed not gated. Bars frozen above; no
post-data changes permitted.

## Records

204 tasks (bulk 18, nogo 66, evolve 84, spectral 18, phase 18):
data/vacdomain/*.json + data/vacdomain/verdict.json.
