# PATCH resuscitate-no-neutrons (vs 55fb5a2)

Applied on top of `55fb5a2` (post-v3.11). Full diff via
`git diff 55fb5a2..cursor/resuscitate-no-neutrons-bddc`. Key hunks:

## 1. `src/bh_graph/orici.py` — gradient shells + exact EMD

```python
# NEW constants
P_ADJ_BASE = 0.85; P_ADJ_SLOPE = 0.015
BRIDGE_ALPHA = 1.3; BRIDGE_BETA_OLD = 1.0; BRIDGE_BETA_NEW = 1.5
BRIDGE_C = 8.0 / (30.0**1.3)

def p_adj_of_shell(s, gradient=True):
    return 0.85 + 0.015*s if gradient else 0.85

def n_bridges_for_pair(r_mid, per_shell, beta):
    return round(C * per_shell**1.3 * (r_mid/2)**beta)

def gradient_shell_graph(per_shell=30, n_shells=10, gradient=True, beta=None, seed=0):
    # intra: ER(p_adj(s)) per shell; inter: exactly n_bridges, random placement
    ...

def shell_kappa_profile(g, n_shells, max_per_shell=8):
    # exact ollivier_curvature (linprog, full neighborhoods) on radial edges
    ...

def fit_scaling_power(profile):  # |k| ~ r^-p
    ...
def measure_p(...):  # per-graph + stacked fits
    ...
```

- Old: BI grid+hub, 3 shells, 6 graphs, $\sigma_p = 0.48$.
- New: 8–10 shells, deterministic bridges, exact LP → per-graph
  $\sigma \approx 0.06$, SEM $\approx 0.02$ (8 graphs).

## 2. `src/bh_graph/pulsar.py` — NEW: 2PN vs TOAs

Iorio direct + total, $c_2(p)$, $w = 1.953$, Kepler inversion
$R+\dot\omega\to M$, $p$-precision bar. No GR masses in inversion path.

## 3. `src/bh_graph/collapse.py` — leg-shedding

```python
E_EXT_INIT = 0.5; E_EXT_FINAL = 0.416  # frac 0.168
SHED_EFFICIENCY = 0.1
def leg_shedding_ejecta(m1, m2, ...):
    k_tot = k(m1)+k(m2); dK = 0.168*k_tot
    M_ej = 0.168*(m1+m2)*0.1  # 0.047 Msun at 1.4+1.4
```

## 4. Tests / figures / docs

- `tests/test_pulsar.py` (12), `tests/test_kilonova.py` (6),
  `tests/test_orici.py` (+4 incl. `p_precision`).
- `scripts/generate_figures.py`: fig66/67/68 + `fig_orici_p_fit.png`,
  `fig_kilonova_gap.png` aliases.
- `docs/resuscitate-no-neutrons.md` (this branch README), README/CHANGELOG.

## Honesty

Fitted: slope $0.015$, $\beta = 1.5$, $w = 1.953$, shed $e$ + efficiency.
Derived: $p$ from OR, $M(c_1,c_2)$, $M_{ej}(M_{tot})$.
Armed: $p\notin0.92\pm0.056$ @ N=1024; gap rate $=0$.
