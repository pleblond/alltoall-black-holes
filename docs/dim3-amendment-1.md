# DIM3 Amendment-1 (PRE-GRID, post-smoke): window-validity rule, far-shell sizes, forerunner legs

Status: apparatus-validation amendment. The full 76-task grid has NOT run;
only cheap smokes (spread/packet/pot0/switch/sector/vacuum singles) informed
this amendment. No blind data, no reveal, no verdict exists. The frozen
prereg (docs/dim3-prereg.md) is NOT modified; this file records apparatus
rules derived from the banked protocol + pre-data mathematics. All level
choices below (threshold decades, window ratios) are fixed here BEFORE the
grid runs.

## A1. Interior-peak validity rule (E/F peak fits)

Banked RESPONSE-0 fits windowed first-passage peaks
(R.peak_in_window over the causal window). A windowed "peak" is only a
peak if it sits STRICTLY INSIDE its window; a maximum at the window edge
is a rising-trace cutoff, not data. Rule (frozen):

```text
peak(s) VALID iff (tstar(s), hi(s)] holds grid points  (room past the max)
                AND min tr over them < peak(s)          (strict falloff: true local max)
                AND peak(s) > theta                     (above detection floor)
```

Rationale: edge maxima are rising-trace cutoffs; pre-arrival window
maxima are precursor noise. Both must be excluded (v2 tightens the v1
interior-only rule after the j3-L16 smoke admitted a cutoff (r=6) and a
noise peak (r=9)).

- J2-L28 validation: all 9 shells interior (banked n=9 preserved exactly;
  v=7.947/r2=0.984/a_psi=0.50 replicate to all digits through campaign code).
- J3-L16 smoke: shells 2,3,4 interior; shell 5+ edge-hit (excluded).
- Fits run over interior-valid shells in 2..10 only; `n` filed per record.
- Records with n<3 have NO fit (alpha NaN, filed as UNMEASURABLE, never
  imputed, never gated as fail).

## A2. Far-shell spread sizes (window math, pre-data)

Necessary validity (rigorous bound only, no measured numbers): first-passage
peaks need tstar(r) < (L-r)/Vmax with tstar >= r/Vmax, i.e. r < L/2. Full
shells-2..10 fits hence need L > 20. The prereg size list {8,12,16}(+20)
therefore yields partial ranges (filed n); the full-range legs are ADDED:

```text
spread J3 sizes: 8, 12, 16 (prereg) + 20 (prereg leg) + 24, 28, 32 (A2 legs)
```

- Expected valid counts (interior rule): L16 ~3-4, L20 ~5-6, L24 ~6-7,
  L28 ~8, L32 ~9 shells. L8/L12 exponents expected UNMEASURABLE (n<3);
  their FRONTS (arrival-only, no window) remain measurable and gated.
- Cubic controls (L10/15/20) and j2-L28 unchanged.
- Cost: L32 (N=65536) ~1-2 min/task (Krylov + vectorized shell loop).

## A3. Forerunner-diagnosis legs (tladder task, characterization)

Smoke finding: J3 threshold-front rides at v~8 (cubic ~4 = same 2/3 of
its bound; J2 rides at ~8 = its bound). Packets (threshold-free) ride at
Bloch speed on all families. Ad-hoc decade ladder (1e-2/1e-3/1e-4,
pre-amendment) showed strong threshold dependence (6.7/7.9/9.4),
i.e. the E-a readout samples a dimension-diluted forerunner, not the
bulk band edge. To freeze this diagnosis into the campaign record, ONE
characterization task is added (no gate changed, levels fixed here):

```text
tladder --tag {j3-L16, cb-L20, j2-L28}: front fits at rel-theta {1e-2, 1e-3, 1e-4}
```

The preregistered E-a gate (1e-3 level) is untouched; the ladder only
diagnoses its threshold-robustness. Filed in verdict JSON under "tladder".

## A4. Packet/pot0 (sigma, T, L) validity rule (already implemented)

Transverse-spread formula s(T) = s*sqrt(1+(T/2m*s^2)^2), m* = 1/4 (J3),
1/2 (cubic), both prereg-derived (B). Circular-mean COM readout requires
s(T) <= L/4 (else wrap-teleport: diagnosed on J3-L12/L16 smokes, where
narrow packets veered off-axis with r2~0.85). Frozen configs:

```text
packet J3: sigma = L/6, T = 4, k = 0.3 (L16: 25% + L20: 21% of L)
packet cb: sigma = L/8, T = 8 (validated passing, unchanged)
pot0 both: sigma = 4.0 (banked verbatim), T = 10, KX = 0.3, C_GRID banked
pot0 sizes: j3-L24 (27%), cb-L20 (24%) -- minimal L with s(10) <= L/4
```

Gates unchanged (prereg G-a/G-b verbatim). Different masses need different
exposures; identical bars.

## A5. Measurability-aware E/F/J evaluation (unmeasurable != fail)

- E_tags/F_tags per record as preregistered where n>=3.
- Records with n<3 (peak fits) are UNMEASURABLE: excluded from E_PASS/F_PASS
  conjunctions, filed explicitly (expected: j3-L8/L12 exponents).
- Fronts (E-a, arrival-only) gated on all J3 spread sizes as preregistered.
- J-a exponent consistency evaluated across MEASURABLE J3 sizes (filed
  which); J does not gate the headline (prereg ladder).
- E-a's literal bar vs the forerunner diagnosis (A3) is resolved at
  verdict time under the banked QUOT-0 design-error-bar precedent
  (pot_far: bar wrong, physics confirmed); both the literal and the
  diagnosed readings are filed.

## A6. Hidden port: banked-verbatim battery + H-g VMINUS-state correction

Two apparatus defects in the pre-grid hidden task (found in smoke review
against the banked HIDDEN-0/HBR-0 runners, NOT fit to DIM-3-0 data):

1. Amplitude-leg rescaling was non-banked: a geometric-mean Q-match on
   both members injects symmetric leakage on unequal-norm pairs. Banked
   legs are RAW (matched_pair, dQ filed) plus the HAMP-Q control
   (qmatch_pair rescales P_+ ONLY). Fixed: all legs via
   hidden.matched_pair verbatim; amp_raw(2.0) RAW + amp_q(0.5) HAMP-Q
   control (expected C1+C2 fail at predicted c^2 values, excluded with
   cause, never gated). Diffusion readouts use unnormalized |psi|^2
   (banked-verbatim; RAW mass-difference signal is physical).
2. H-g gated >100 flips on the LOCAL uniform+delta sign pair. Banked
   precedent: B:sign:uniform has flips = 0 (lc_n = 16) -- the campaign
   smoke's flips = 0/6144 REPRODUCES the banked value exactly (apparatus
   confirmed). The 1346 precedent is the battery total, dominated by the
   VMINUS-based GLOBAL sign pair (1276). Fixed: H-g runs the VMINUS
   global pair (uniform + VMINUS shape, sign mode; banked L:vminus
   analog) with the >100 gate; local-pair flip counts filed, never
   gated. No remote legs on the global pair (banked L:vminus files none).

Gating table (HBR-0 C0, frozen): sign/phase legs gate pmatch + E_ok +
E_free + dQ + local + sodd + wave + diff + pot + pot_support;
shape/amp_raw gate the same MINUS diff (sodd False filed per HBR-0
Amendment-1: the |psi_-|^2 S-even part diffuses -- VISIBLE-expected,
never gated) MINUS dQ on amp_raw (RAW variant). Neighborhood R_PREP=2
(banked convention). Uniform background = VPLUS shape.

## Task count

76 = 30 stations + 25 spread + 3 tladder + 3 packet + 2 pot0 + 3 pot1
+ 2 switch + 3 sector + 1 bilayer + 1 hidden + 3 vacuum.
