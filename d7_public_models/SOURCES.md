# D7 public-model pins (deliverable C)

Every external dataset used by milestones 1–4. Nothing here is vendored
into git (550 MB); `fetch_models.sh` reproduces the acquisition and
`SHA256SUMS` verifies it. Retrieval date for all files: 2026-09-28.

## NMMA framework

- Package: `nmma` 1.0.1 via `pip install nmma`
  (repo: https://github.com/nuclear-multimessenger-astronomy/nmma).
- System deps encountered: `python3-dev` (for the `sncosmo` C build).
- Reference: Dietrich et al. 2020 (NMMA framework); Bulla 2019 MNRAS 489,
  5037 (Bu2019 grids); Kasen et al. 2017 (Ka2017 grid).
- Used strictly as a local grid interpolator (`SVDLightCurveModel`,
  `interpolation_type='sklearn_gp'`, `local_only=True`): no sampling, no
  inference, no refit. Filter names use NMMA's double-colon convention
  (`ps1::g` ↔ file `ps1__g.joblib`).

## SVD model grids (GitLab model repo)

- Source: `https://gitlab.com/Theodlz/nmma-models/raw/main/models/`
  (NMMA's public model store; no auth required).
- Files (core + per-filter GP interpolators, `ps1::griz` only):

| File | Bytes | Role |
|---|---|---|
| `Bu2019nsbh.joblib` | 10,817,998 | E0 bases + training grid (891 pts) |
| `Bu2019nsbh/ps1__{g,r,i,z}.joblib` | ~31 MB each | E0 GP interpolators |
| `Ka2017.joblib` | 9,635,000 | E1/E2 bases + training grid (329 pts) |
| `Ka2017/ps1__{g,r,i,z}.joblib` | ~4.3 MB each | E1/E2 GP interpolators |
| `Bu2019lm.joblib` | 12,775,867 | bounds audit only (excluded, spec §2.1) |

- Empirical training bounds (read from shipped `param_mins/param_maxs`,
  `docs/D7_TRANSPORT_SPEC.md` §2):
  - nsbh: dyn/wind 0.01–0.09 M☉, θ 0–90°, t 0–21 d.
  - Ka2017: total 0.001–0.1 M☉, vej 0.03–0.3c, Xlan 1e-9–0.1, t 0–21 d.
- Bandpass note: PS1 griz are approximations to CFHT-MegaCam-g /
  DECam-i / protocol-griz (spec §2, `bandpass: ps1-approx` flag).

## Verification

```bash
bash d7_public_models/fetch_models.sh /tmp/nmma_models   # download
cd /tmp/nmma_models && sha256sum -c $OLDPWD/d7_public_models/SHA256SUMS
```
