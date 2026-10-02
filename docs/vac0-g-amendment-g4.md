# VAC-0G Amendment G4 (pre-data: G campaign not launched)

## G4.1 Interior κ (correction to G3)

Per `interior_slope`'s locked docstring ("no single-slope prediction is
locked"), the quantitative κ test lives on the WIDTH LAW, not the
interior fit. Interior readouts (`interior_asym`) are gated as
evanescent-shape (mono + asym) only:

- LB ∈ {4,5,6,8}: `monotonic` True AND `asym > 3` (theory floor:
  `e^{2κ(LB-1)} ≥ 62` at the smallest campaign κ = 0.69 — gate has
  >20× margin, frozen here).

## G4.2 Width-law κ (replaces G3 κ-fit sentence)

- J2/square (analytic `T_pred` port): per-LB `|T - T_pred|/T_pred`
  ≤ 5% (J2 regression) / ≤ 15% (square port) + log-slope
  `d lnT/dLB` within 10% of predicted slope.
- tri/hex (no analytic-T port): monotone decrease + `T(LB=8)<T(LB=1)/2`
  + log-slope within 25% of `-2κ_chain`, `κ = arccosh(|E0|/2)`.

## G4.3 Finite-T gate (replaces absolute 1e-6)

Absolute thresholds are meaningless under k-averaged transmission.
Gate: `T > 0` strictly + `T+R+B = 1` accounting (exact) + control
cell transmits (`T_control > 0.5`, propagating check) + width-law /
strength-law shape gates per G3/G4.2.
