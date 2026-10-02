# VAC-0A — Universal algebraic identities (LAW layer)

All identities below hold for EVERY simple undirected graph `G` (connected or
not) with the frozen field law `H = -A`, `J = 1`, `hbar = 1`, and the frozen
node field `psi_u = r_u + i s_u`. Nothing about J2 enters. Proofs are
three-line consequences of Hermiticity + the adjacency form; each is pinned
by `tests/test_vac0a_identities.py` on hostile graphs (star, complete,
disconnected, random, small J2 ball).

## A1. Norm conservation

`H = -A` is real-symmetric, hence Hermitian. `U(t) = exp(-iHt)` is unitary,
so `Q_psi = sum_u |psi_u|^2` is exactly conserved along every trajectory.
Test: `evolve_fixed` norms pinned to 1 on all hostile graphs.

## A2. Bond current and exact continuity

Schrodinger equation: `d psi_u / dt = -i (H psi)_u = +i (A psi)_u`.
With `rho_u = |psi_u|^2 = psi*_u psi_u`:

```
d rho_u / dt = 2 Re[psi*_u dpsi_u/dt] = 2 Re[i psi*_u (Apsi)_u]
             = -2 Im[psi*_u (Apsi)_u] = -2 Im[sum_v A_uv psi*_u psi_v].
```

Define the bond current `J_{u->v} = 2 Im(psi*_u psi_v)` (antisymmetric:
`J_{v->u} = -J_{u->v}`). Then exactly, per node:

```
d rho_u / dt + sum_v A_uv J_{u->v} = 0.
```

Test: `continuum.continuity_residual` (rhodot via `rho_dot_via_h` plus
`div_J` via bond currents) is exactly ~0 on all hostile graphs.

Convention note (pinned in tests): banked code carries TWO current
normalizations. `potential.bond_current(a, b) = 2*Jcoup*Im(conj(a)*b)` is
the true continuity current above (this is what `div_J` uses). By contrast
`phase.bond_J = Im(C)` and `driven.bilinears["J"] = Im(C)` are the BARE
quadrature (half the continuity current at `Jcoup = 1`). VAC-0 LAW
statements use the brief's `J = 2 Im`; the bare quadrature is related by
an exact factor of 2, never a contradiction.

## A3. Bond coherence and energy

Energy: `E_psi = <psi|H|psi> = -sum_{u,v} psi*_u A_uv psi_v`.
Pairing `(u,v)` with `(v,u)` (undirected, `A` symmetric):

```
E_psi = -sum_{(uv) in E} [psi*_u psi_v + psi*_v psi_u]
      = -2 sum_{(uv) in E} Re(psi*_u psi_v).
```

Define `B_uv = Re(psi*_u psi_v)` (symmetric). Then:

```
E_psi = -2 sum_{(uv) in E} B_uv.
```

Test: `backreaction.energy_full == energy_edge_sum` on all hostile graphs
(complex random states, including disconnected graphs).

## A4. Energy-conjugacy: dE/dA = -2B

Treat the adjacency as continuous edge weights `w_uv` (`H = -W`,
`W` symmetric). `E` is linear in each `w_uv` with slope
`-(psi*_u psi_v + c.c.) = -2 B_uv`. Hence:

```
dE_psi / dw_uv = -2 B_uv.
```

Test: centered finite difference of `energy_full` under single-edge weight
perturbation matches `-2 B_uv` on small hostile graphs. (On simple graphs
this is the virtual-work identity behind BR-0's `delta_e_local`.)

## A5. Quadrature structure

With `C_uv = psi*_u psi_v`: `B_uv = Re C_uv`, `J_{u->v} = 2 Im C_uv`, so
`(B, J/2)` are the exact quadrature components of the bond correlator:
`B ~ cos(Delta theta)`, `J/2 ~ sin(Delta theta)` for
`Delta theta = arg(psi_v) - arg(psi_u)`. Algebraic (no substrate content);
the SUBSTRATE-dependent part is only which `(B, J)` patterns actual
dynamics produce (VAC-0J). Pinned: `bond_B`/`bond_J` symmetry checks +
stagger-scan quadrature on ring/torus/J2 (vendored `test_phase.py`).

## A6. Branch weights (bipartite graphs)

On bipartite graphs the chiral operator anticommutes with `H`, so the
spectral projectors `P_+/-` commute with `H` and branch weights are exactly
preserved (vendored `branch_projectors` + `branch_mixing` null). This is
CLASS-level (needs bipartiteness), not LAW: non-bipartite graphs (triangular
torus, odd cycles) have no chiral symmetry. VAC-0A pins the LAW part
(projector validity + weight accounting on any graph) and files bipartiteness
as the class gate. Pinned in `tests/test_vac0a_identities.py`.
