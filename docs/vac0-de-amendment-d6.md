# VAC-0D/E Amendment D6 (pre-data: no phenomenology opened)

## D6.1 Validity gates (bug-catchers, not verdicts)

- `S1_trans`: translated-packet prep on every translation-invariant cell must
  reproduce `mean_D`/`mean_J` exactly (same theorem as POT-0 S1_trans,
  generic shift implementation per family). If it fails, the cell's ports
  are buggy → cell marked INVALID (rerun after fix), never FAIL.
- `S3_phase`: global-phase prep must leave `prep_D`/`prep_C`/`mean_D`
  invariant (exact). Same INVALID rule.
- `wrap`: `disp < L/2` (2D) / `< N/2` (ring) required for the B verdict to
  be drawn; violation → INVALID (T was mis-budgeted), never FAIL.

## D6.2 Ring ports (frozen formulas)

- Flux: `J_net = Σ_e J_e dx_e` (minimal-image `dx ∈ {-1,0,1}`),
  `S = Σ_e |J_e|`, `D = |J_net|/S` (`S == 0 → D = 0`).
- Coherence: 1D FFT peak fraction `C = Pmax/Psum`, `M_eff` same formula.
- Aperture: interval mask `|x - x0| <= R` minimal-image, renormalized.
- `B_rev` port: `sign(J+_net) != sign(J-_net)` and `D`-match 10%
  (replaces `cos_between`, which needs 2-vectors).

## D6.3 Intrinsic `delta` arm (all cells, filed not verdict-bearing)

Single-node start at the packet center node, same `(T, dt)` as the cell:
shell peak-time linear fit (`v_shell`, `R2_shell`), `IPR(t)` trace,
return probability `P0(t)`. Gives a coordinate-free propagation readout
on every substrate including RR (headline UNDEFINED there, intrinsic filed).

## D6.4 Filed secondaries (not verdict-bearing)

`C_constancy` (POT-0 formula) per cell; purified-arm B-set; `w0`/mixing
anatomy per ±k prep; null `(mean, std)` per cell; per-case `norm_dev`.
