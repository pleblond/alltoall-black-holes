# DIM31 Amendment-4 (PRE-J3): J3 spread/packet gate scoping

Status: prereg-compliance correction to pre-data J3-phase code.
No J3 data exists (J3 grid not run). No estimator, tolerance, or
verdict criterion is weakened: the fix restricts two legs to
their preregistered scope.

## A4.1 The deviation

Prereg section 5 scopes the metric legs:

- Spreading "on J3-L20+ and cubic controls"; "near-field-only
  (n < 4) legs UNMEASURABLE, never gated."
- The frozen battery (`PACKET_TAGS`, `SPREAD_TAGS`) provides
  J3 legs at L20/L24 only (plus banked cubic/J2 controls).

The pre-data `cmd_j3` (never executed) gated spread-R
measurability + pass and packet pass at ALL THREE J3 sizes.
At J3-L16 no legs exist in the frozen battery, so the gate
would fail L16 on missing records regardless of the physics
-- a certain spurious GEOMETRIC cause. It further failed
present-but-near-field-only legs, contradicting "never
gated" verbatim.

## A4.2 The fix (`cmd_j3` only; controls untouched)

- Spread/packet gates apply at j3-L20/j3-L24 (prereg "J3-L20+").
  J3-L16 has no spread/packet legs: absent records there are
  expected, not failures.
- Within scope: measurable legs must pass; present-but-n<4
  legs are filed, never gated (prereg verbatim).
- Missing L20+ record file -> failure (battery integrity: the
  deterministic grid must produce it; absence means grid
  failure, caught first by GRID_DONE rc).

## A4.3 Ordering note (seal sequencing)

The campaign docstring asks for `--allow-j3` "only after the
blind seal is written", but the seal binds the blind artifact
over ALL cells, which requires J3 measurement files to exist.
Coherent order (firewall-preserving): freeze committed
(debt = 0, estimators + tolerances frozen) -> J3 grid
(mechanical generation, no reads) -> blind over all cells
(frozen D bars) -> seal (binds blind + freeze + rev) ->
`cmd_j3` (hash-verified; the single sanctioned J3 read).
A preseal anchor (`data/dim31_preseal.json`, untracked)
records freeze sha + rev + timestamp before J3 generation,
proving the apparatus predates J3 data.
