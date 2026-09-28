# D7 POSSIS RunPod kit (CPU pods; no GPU)

Staged pipeline for full 3D Monte Carlo RT on graph-predicted ejecta.
Pre-registration: `docs/possis-preregistration.md` (grid + statistic +
thresholds). Mapping: `docs/possis-mapping.md`. Survey/costs:
`docs/possis-survey.md`. Bookkeeping module: `src/bh_graph/possis.py`.

## Gate (do not skip)

Production is gated on ALL of (§6 of the pre-registration):

- G1 mapping review accepted, G2 POSSIS source access (version pinned),
  G3 opacity tables pinned (hashes in `possis_Dockerfile`),
  G4 user budget approval (high-end CPU only — POSSIS is CPU Monte Carlo,
  GPU buys nothing).

The pilot (1 model × 3 angles, ~$1–2 CPU) needs G1 + G4-pilot.

## Files

- `possis_Dockerfile` — image with `gcc/make` + POSSIS binary + opacity
  tables baked (~10–20 GB once). STAGED: G2/G3 URLs+hashes are TODOs.
- `possis_launch.sh` — one model per CPU pod (16 vCPU), proxy-SSH pipe
  (same as `launch.sh`), artifacts catted back to `data/possis_*.json`
  with the run config stamped inside. `--pilot` = `N_ph=1e5/N_obs=3`;
  default = `N_ph=1e6/N_obs=11`. First live run: `--keep`, confirm the
  `ASSUMPTION` REST/CLI shapes, then `--terminate` production.
- `possis_remote.py` — pod entry point (same code path as tests):
  builds the pre-registered config, runs the binary, writes the artifact.
  `--allow-mock` permits the MOCK surrogate for plumbing only (flagged
  `MOCK-NOT-RT`, never feeds a verdict).

## Artifacts

`data/possis_<model>_<config>_nph<N>.json` (production) and
`data/possis_pilot_<model>_<config>.json` (pilot): `{"config": {...},
"lightcurves": {...}, "MOCK-NOT-RT": bool}`. Exploratory runs outside
the pre-registered grid carry `_exploratory` in the filename + an
in-payload flag (pre-reg §5).

## Cost model (survey §5, validate with the pilot)

Pilot ~1–3 CPUh (~$1–2 wall); production ~20–60 CPUh/model
(~$3–8 for the 3-model null, ~$8–25 full 12-model grid on 16 vCPU).
Report the pilot's measured CPUh + seed-split noise (<0.15 mag bar)
before launching production.
