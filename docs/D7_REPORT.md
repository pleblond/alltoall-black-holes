# D7 Report — public-data surrogate transport (EXPLORATORY, SURROGATE-NOT-RT)

Date: 2026-09-28. Branch: `cursor/d7-possis-rt-3175` (PR #38 line).
Parent pre-reg frozen at `c869e16`; deltas filed as amendments A1–A3.
Model definition: `docs/model.md` v0.4 §4 (F5/F6), cited, not merged.

One-line verdict: **the analytic GW190814 conclusion (tension, not
exclusion) stands.** Transport at 0.43 M☉ is outside every published
grid (4–17×), so no headline verdict can move; the anchor-passing E0
family bounds the surrogate direction, and gap50 predictions
(headline-eligible, inside grids) corroborate the analytic g-band to
~0.2 mag while confirming the ~3 mag analytic i-band over-trapping bias.

## 1. What public model was used?

NMMA 1.0.1 built-in SVD grids (local-only, sklearn-GP backend) from
`https://gitlab.com/Theodlz/nmma-models` (retrieved 2026-09-28, pinned
in `d7_public_models/SHA256SUMS`): **Bu2019nsbh** (E0; 891 training
points, dyn/wind 0.01–0.09 M☉, θ 0–90°) and **Ka2017** (E1/E2; 329
points, total 0.001–0.1 M☉, vej 0.03–0.3c, Xlan 1e-9–0.1), PS1 griz.
Bu2019lm audited and **excluded** (dyn cap 0.02 excludes every event).

## 2. How was it mapped to F5/F6 (including VEL-1)?

F5/F6 preserved exactly: `M_ej = 0.0168 M_tot`, 0.2/0.8 split, 0.3c/0.1c
scalars (invariants tested, §9). Mapping: red→dyn, blue→wind (E0);
total→mej (E1/E2). **VEL-1**: characteristic velocities read as
mass-weighted ⟨v⟩ (central 0.14c, bracket [0.1, 0.3]); E0 velocities
are grid-fixed (EXTERNAL). Full math in `docs/D7_TRANSPORT_SPEC.md`.

## 3. What was externally assumed?

E0: toroidal geometry + fixed Bulla velocity structure/Ye/heating
(**violates the spherical null** — viewing dependence entirely
external). E1/E2: spherical Kasen geometry/heating, Xlan↔Ye endpoint
correspondence (order-of-magnitude). PS1≈CFHT/DECam bandpasses
(`ps1-approx` flag, no correction). GP interpolation within grids.

## 4. What did transport predict?

- **Anchor (0.047, gate)**: E0 peak g 18.00/18.32 (pole-near) — PASS;
  E1 18.94–19.27 — FAIL (fixed Xlan=1e-3 too red, 2/3 cells outside);
  E2 bracket [16.98, 22.63] contains 18.0 but fails strict all-cells.
  E0 i-decline 1.5–2 d (target 3–5 d) — no i promotion.
- **GW190814 (0.433, sensitivity-only, 3.9–4.3× outside grids)**: E0
  g@1.7d 21.98→22.72 pole→equator (analytic 21.16, depth 22.8);
  P_comb_g 0.543→0.382 (analytic 0.68); 9/11 thetas survive at <0.5.
  E0 g+i 0.90–0.98 computed but UNCLAIMED (i not promoted).
  E1/E2 0.43 cells computed-but-inadmissible (gate failed).
- **gap50 (0.084, headline-eligible)**: E0 pole g 19.9/19.7 @1–2d/100Mpc.

## 5. How did g compare with the existing analytic result?

Control at anchor: E0 RT brackets analytic at 1 d (median +0.17 mag,
viewing range 1.5 mag); RT brighter by ~1.1 mag at 2 d, ~4.6 mag at
4 d — the analytic exp(−t/t_p) tail falls far too steeply vs the RT
diffusion+reprocessing floor. Peak/early light (which drives P_detect)
agrees; late epochs diverge with analytic UNDERSTATING brightness
(conservative direction for late detectability).

## 6. Direct i-band: predicted and claimed?

Predicted everywhere; **claimed nowhere**. E0's anchor i fades 1 mag in
1.5–2 d, missing the 3–5 d promotion bar (§10 rule applied as written).
Notable: surrogate i is ~3 mag brighter than analytic at 1–2 d,
independently confirming the documented one-zone over-trapping bias in
the predicted direction and size. i stays unclaimed; all verdicts g-only.

## 7. Morphology/composition/velocity-structure sensitivity?

- Morphology (E0 wedge vs E1 sphere @gap50): ~1 mag in g at 1–2 d.
- Viewing (E0 pole→equator): 1.8 mag @1.7d growing to 4+ late (anchor);
  1.4–2.4 mag for gap50 g — time-dependent, vs the flat A_g=1.25 surrogate.
- Composition (E2 Xlan 1e-5→1e-2): ~6 mag in g — the dominant uncertainty.
- Velocity (E1 0.1→0.3c): ~0.3 mag — subdominant. VEL-1 shape risk bounded.

## 8. Did the GW190814 conclusion change?

**No.** Every 0.43 cell exceeds the §7 2× bound (3.9–17×), so the §12
named outcome applies: transport cannot adjudicate GW190814 at headline
level; the verdict stands on analytic + surrogate. Supporting evidence
that the extrapolation is untrustworthy (not just out-of-policy): at
0.43 the extrapolated E0 late decline goes FAINTER than analytic
(g6.6 25.4–27.0 vs 23.66), the opposite sign of the in-grid anchor
behavior (RT brighter late) — the GP visibly misbehaves 4× outside its
box. Directionally (weight zero): extrapolated E0 g gives P 0.38–0.54
vs analytic 0.68 — less tension, not more.

## 9. What did gap50 predict?

E0 (admissible, in-grid): g ≈ 19.9/19.7 (pole) and 21.3/22.1 (equator)
at 1–2 d / 100 Mpc; +1.5 mag at 200 Mpc → 21.2–21.4 pole (analytic 21.2
✓). i ≈ 19.1–19.4 pole (~3 mag brighter than analytic 22.1). Full
griz×{0.5,1,2,5}d×{100,200Mpc} tables in
`results/d7/gap50_predictions.json`. E2 composition bracket spans ~6 mag
in g — reported as the honest uncertainty, not averaged away.

## 10. What remains genuinely unresolved?

1. Real 3-D RT at 0.43 M☉ (needs G2 source + G3 tables; essentially
   unprecedented regime — optical-depth/thermalization validation
   required before trusting any 0.4+ run from any code).
2. A spherical-blue public grid matching the L2 null (none found; E0
   carries wedge systematics by necessity).
3. i-band promotion (needs a pipeline passing the decline gate).
4. E1-class fixed-composition 1-D mapping (failed gate as specified;
   two-component 1-D sums are Bulla-Fig.4-wrong, so no rescue attempted).
5. Full leave-one-out surrogate errors (gradient×spacing bound used;
   conservative by construction) and Bu2019lm-φ / Bulla-2023 extensions
   (milestone 5, post-§12).

## Reproduce

```bash
pip install nmma  # 1.0.1 + python3-dev; isolated venv recommended
bash d7_public_models/fetch_models.sh /tmp/nmma_models
D7_NMMA_MODELS=/tmp/nmma_models python scripts/run_d7_surrogate.py  # ~1 min
python scripts/plot_d7_results.py
pytest tests/test_d7.py  # pure tests; NMMA-gated tests run with the env set
```

Provenance chain (F5/F6 → public model → deterministic map → transport →
frozen observation operator) is complete, tested, and committed. The
frozen analytic + pre-registered verdicts are untouched; this report adds
a bounded exploratory layer beside them, per package §19.
