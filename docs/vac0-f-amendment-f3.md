# VAC-0F Amendment F3 (pre-data: F/G campaigns not launched)

Apparatus-validation on campaign geometries (smoke runs, not campaign
data) showed the SLIT argmax-T* clock is fragile on slow packets
(dispersive leading edge wins over main arrival) and L28/D=7 gives
~2 fringes (nmax gate edge-sensitive). This amendment freezes a
uniform, theory-grounded port BEFORE any campaign run:

## F3.1 Uniform headline port (all torus cells)

- `k = (0.5, 0)`, `σ = 2`, `dt = 0.1` everywhere (P2.2 uniform).
- Clean families on L=40: `xb = 16`, slits `(12, 28)` (d=16 about
  yc=20), mouths `(17, 12)/(17, 28)`, `xd = 27` (D=10),
  window `|y-20| ≤ 16`, wrap margin 13.
- Hostile rewires stay L=28: `xb = 12`, slits `(8, 20)`, mouths
  `(13, 8)/(13, 20)`, `xd = 20` (D=7), window `|y-14| ≤ 12`.
- Clock: FIXED `T* = D / v_pred` (center arrival, frozen per family):
  v_pred from closed-form bands — J2 `4 sin k`, square/j2quot
  `2 sin k`, tri `4 sin k` (axial Bloch), hex brick-wall Bloch
  (`f = 1+e^{-i(k1+k2)}+e^{-ik2}`, `E = -|f|`, numeric gradient;
  v(0.5) = 0.959), rewires J2 budget. L40: J2/tri 5.2, sq/j2quot/hex
  10.4. L28 rewires: 3.6.
- Validity adds: `detW(T*) > 0.5%` (packet actually at detector) else
  INVALID (port broken, never FAIL). Argmax-T* filed as secondary.
- Purified-mouth diagnostic (filed, not verdict-bearing) on bipartite
  cells (J2, square, j2quot, hex): same 0a metrics on P_+-purified
  mouths (band-splitting diagnosis, frozen here).

## F3.2 Regression arm (C1, exact banked params, separate cells)

- open-70x61 exact (`V = 0.678`, T*∈[0,60] argmax — banked rule kept
  for the banked geometry).
- j2_L28 exactly banked (`k = 0.3`, fixed `T = 6.0`, `V = 0.853`).
- MZ len-14 exact (banked gates).
