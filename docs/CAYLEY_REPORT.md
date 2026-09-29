# Cayley-growth probe — report

**Branch:** `cursor/cayley-growth-736b` · **Prereg:**
`docs/cayley-prereg.md` (committed BEFORE any compute; no amendments) ·
**Date:** 2026-09-29. **Compute:** $0 local, 0.4 s + tests.

**Verdict: 3/3 PASS.** Volume-growth degrees (OLS log|B| vs log r,
r ∈ [5, 11], exact BFS to R = 12):

| Group | Predicted (Bass–Guivarc'h) | Measured d | R² | N(R=12) | Verdict |
|---|---|---|---|---|---|
| Klein ⟨x,y\|xyx⁻¹=y⁻¹⟩ | 2 (virtually Z²) | 1.864 | 0.9999 | 313 | PASS |
| Z³ (calibration) | 3 | 2.769 | 0.9999 | 2625 | PASS → METHOD-OK |
| Heisenberg UT₃(Z) | 4 (ranks (2,1)) | 3.866 | 0.9999 | 8871 | PASS |

All read slightly low (Δ ≈ −0.14…−0.23) — finite-radius transient
approaching from below, identical signature across all three (ordering
2 < 3 < 4 exact). Calibration holds: the method resolves growth
degrees, so K/H verdicts carry weight.

## D10 consequences (listing, not selecting)

- **Heisenberg is OUT as a 3D homogeneous vacuum.** Hirsch length 3
  but metrically 4D — the concrete d_G≠d_obs instance: topological 3D,
  growth/measure 4D (Pansu Carnot cone). Any "nilpotent = 3D" hope dies
  here; only the growth-3 subclass survives (Z³ confirmed).
- **Open census case:** Bass–Guivarc'h allows growth 3 via ranks
  (r_1,r_2) = (1,1) (class-2, ab-rank 1, commutator-rank 1) alongside
  (3) = Z³-like. Existence/identity of (1,1) groups is UNRESOLVED here
  — explicit follow-up (literature + construction, same probe shape).
- D10 stays open: this probe narrows the homogeneous candidate list,
  it does not select. No minimization, no selection principle tested.

## κ exploratory (no bar): short-cycle story corroborated

Exact P4 Ollivier-κ, 20 seeded interior edges of r ≤ 8 balls:

| Graph | (d_growth, κ) | Short cycles? |
|---|---|---|
| Z³ | (3, 0.000 ± 0.000) | squares → flat |
| Klein | (2, 0.000 ± 0.000) | squares → flat |
| Heisenberg | (4, −1.000 ± 0.000) | none visible → −1 (cf. diamond girth-6 → −1, annealer round 1) |

Uniform −1.000 on all 20 Heisenberg edges (zero spread): no short
cycles ⇒ κ = −1 exactly, matching diamond's girth-6 reading. Combined
record so far — cubic/FCC/Z³/Klein (flat, cycles) vs diamond/Heisenberg
(−1, no short cycles) vs expanders (negative) — flatness tracks
short-cycle structure, not dimension. (Descriptive; no verdict weight.)

## Reproduce

`PYTHONPATH=src python3 -m pytest tests/test_cayley_growth.py -q`
(6 passed) → `PYTHONPATH=src python3 scripts/run_cayley_probe.py`
→ `results/cayley/{klein,z3,heis,verdicts}.json`.
