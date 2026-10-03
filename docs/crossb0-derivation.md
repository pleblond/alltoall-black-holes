# CROSSB0-DERIVATION — Two-Stitch Finite-Rank Analysis (FROZEN PRE-DATA)

Self-contained derivation for CROSS-IMPL-B under the repository
normalization `H = -A`, `J = 1`. Section 2 proves the TRUE secular form
and the falsity of the spec form; sections 4--10 prove the qualitative
distinction and locate every sharp spec constant as held or debt.

## 1. Model and conventions

Single substrate: `Hd` on `l^2` of the J2 (J3) Cayley graph, `Hd = -A`.
Dispersive bands `eps(k) = -4 (cos kx + cos ky (+ cos kz))`, edges
`+-8` (`+-12`); flat band at 0. Symmetric sector (banked MALUS/DIM3):
with `U phi = phi/sqrt2` on both sheets, `H U = U H_Q`,
`H_Q = -2 A_square/cubic` on cells.

Micro resolvent entries for `E` outside the band, `r != 0`:
`Gd(E) = <0,b|(E-H)^-1|0,b> = (G_Q(0;E) + 1/E)/2`,
`Gam_r(E) = <r,b'|(E-H)^-1|0,b> = G_Q(r;E)/2`, sheet-blind off-cell
(the `P_anti/E` term is on-cell only). Both real for real `E`.

Bilayer: `H0 = Hd (+) Hd`, `V = -t(|a1><a2| + h.c. + |b1><b2| + h.c.)`,
`a = 0`, `b = r != 0`, sheet bit 0, `t` real nonzero. `V` has rank 4,
eigenvalues `+-t` (x2), norm `|t|`.

## 2. Exact secular: true form and falsity of the spec form

On the support basis `(a1, b1, a2, b2)`,
`G0 = diag(g, g)` with `g = [[G, Gam],[Gam, G]]`, and `V = -t` times the
layer-exchange. Bound states outside `spec(H0)` are exactly zeros of
`det(I - G0 V)`. With `I - G0 V = [[I, t g],[t g, I]]`, Schur gives
`det = det(I - t^2 g^2)`. Since `g^2` has eigenvalues `(G +- Gam)^2`:

TRUE: `(1 - t^2 (G+Gam)^2) (1 - t^2 (G-Gam)^2) = 0`.

Layer-sector route (same result): even/odd layer combos decouple to
`Hd +- t(|a><a| + |b><b|)`; each rank-2 secular is
`(1 -+ t(G+Gam))(1 -+ t(G-Gam))`; the product over sectors is the TRUE
form above.

SPEC (`t^2 G (G +- Gam) = 1`) differs by `t^2 Gam (Gam +- G)` per
channel. It coincides with TRUE for all `E, t` iff
`Gam (Gam +- G) == 0`, false (`Gam != 0`, `G +- Gam != 0` generically;
pinned numerically on finite controls where the finite-substrate `g`
makes both determinants exactly evaluable). No rank-4 `V` of the frozen
stitch form yields the spec combination: both elimination orders give
`g^2`, never `G g`. The det battery files `|det TRUE| ~ 1e-13` and
spec residual `>= 1e-3` at every finite-control level.

## 3. Spectral symmetry and parity mapping

`U = S_stag x sigma_z^layer` with `(S_stag psi)(x) = (-1)^|x| psi(x)`
satisfies `U (H0+V) U* = -(H0+V)`: `S_stag` negates each `Hd`
(bipartite) and commutes with `H0` up to sign, while the layer-antisym
phase negates the inter-layer `V` (`(-1)^{2a} = 1` phases cancel on
`V`'s support pairs, the layer sign flips). Hence `E <-> -E` exactly;
upper/lower partners are never independent evidence. Under `E -> -E`,
`(G, Gam)(E) -> -(G, Gam)(-E)` up to the staggered phase, which swaps
the `+sigma/-sigma` channel labels when `sigma = -1` and preserves them
when `sigma = +1` (parity enters only through the frozen `sigma`).

## 4. J2 edge theorem: lam_inf integral, positivity, 1/16, nn 1/8

`lam_inf(r) = lim_{E v 8} (G - sig Gam)` (micro). With
`G_Q(r;E) = int e^{ik.r}/(E - eps(k)) dk`:

`lam_inf(r) = (1/2)[ int (1 - sig cos k.r)/(8 - eps(k)) dk + 1/8 ]`.

Numerator `1 - sig cos k.r >= 1 - |cos| >= 0`, strictly positive off a
measure-zero set (`sig cos k.r = 1` on nodal lines only); denominators
increase as `E v 8`, so monotone convergence gives the limit as the
(nonnegative, nonzero) integral. Hence `lam_inf(r) > (1/2)(0 + 1/8) =
1/16` for every `r != 0`, with no tune. The divergent combo
`G + sig Gam` has numerator `-> 2` at `(pi,pi)` hence `-> +inf`
logarithmically.

Nearest neighbor (`sig = -1`): the exact resolvent identity
`E G_Q(0) + 8 G_Q(nn) = 1` (coordination 4, hopping 2) gives at `E = 8`
`G_Q(0) + G_Q(nn) = 1/8` with no continuity input, so
`lam_inf(nn) = (1/2)(1/8 + 1/8) = 1/8` exactly.

## 5. J2 existence: one channel always binds; the second has a cut

For fixed nonzero `u`, `f(E) = <u|G(E)|u>` on `(8, inf)` is continuous,
strictly decreasing (`df/dE = -||G u||^2 < 0`), `-> 0` at infinity.
With `u = (d_0 + sig d_r)/sqrt2`, `f = G + sig Gam`: `-> +inf` at the
edge, so `|t| f = 1` has exactly one root for every `t != 0`. The J2
first-binding cut is therefore `tc = 0` for every `r != 0` (one pair).

With `u = (d_0 - sig d_r)/sqrt2`, `f = G - sig Gam`: `-> lam_inf > 0`,
so a root exists iff `|t| > 1/lam_inf` (nn: `|t| > 8`). The spec claim
that EACH channel binds for every `t != 0` is FALSE; the cancelled
channel has a finite cut. The nn `t = 2` cert (`n_above = 1`, not 2)
files this directly.

## 6. J2 divergent asymptotic: true 8 pi, not 8 pi sqrt2

Near `(pi,pi)`, `eps = 8 - 2 q^2 + O(q^4)` (Hessian `diag(-4,-4)`,
curvature 2 per direction; pinned via the banked Bloch apparatus).
`G_Q(0) + sig G_Q(r) ~ 2 int d^2k/(2pi)^2 1/(Delta + 2q^2)
= (1/(4pi)) ln(1/Delta)`, so micro `G + sig Gam ~ (1/(8pi)) ln(1/Delta)`
and `|t| ln(1/Delta) -> 8 pi`, `r`-independent at leading level
(`r` enters only the subleading constant). The spec `8 pi sqrt2` would
need curvature `2 sqrt2` (Hessian `4 sqrt2 != 4`) and is FALSE.
Direct log-slopes converge too slowly for feasible grids
(`C/ln(1/Delta)` corrections), so the battery files the frozen
two-point difference slope (exact linear algebra on two frozen
evaluations, not a tune), which kills the constant and reads `1/(8pi)`
within 10% for all `r`, `>= 27%` from the spec value.

## 7. J2 cancelled channel: spec log law is vacuous

Since the cancelled channel has no root for `|t| < 1/lam_inf`
(section 5), there is no small-`t` `Delta(t)` and the spec law
`t^2 ln(1/Delta) -> 16 pi/lam_inf` (nn: `128 pi`) has an empty domain:
vacuous/false. The `lam_inf` values themselves (including nn `1/8`)
are correct and pinned; only the binding claim built on them fails.

## 8. J3 uniform exclusion: |t| <= 24/sqrt(55)

For `E > 12`, `G(E)` is a positive operator: `|Gam| <= Gd` by
Cauchy-Schwarz, and `Gd(E)` strictly decreases to `Gd(12+)`. On the
support, `||g|| <= |Gd| + |Gam| <= 2 Gd(12+)`, `||V|| = |t|`, so no
zero of `det(I - G0 V)` for `|t| < 1/(2 Gd(12+))`, uniformly in `r > 0`
and `E > 12` (mirror below `-12`).

Numerical lemma (27% margin, N-converged to `6e-5`, `d`-flat):
`Gd,J3(12+) <= 0.13` (measured `~0.1026`). Chain: `1/(2 x 0.13) = 3.85
> 24/sqrt(55) = 3.24`, so `|t| <= 24/sqrt(55)` is non-binding for every
positive separation; in particular `t = 1` is inside. Full interval
certification of the lemma is follow-up debt; the distinction itself
(qualitative uniform interval, e.g. `|t| <= 2` at 144% margin) is robust.
No equality of the true cut is claimed.

## 9. J3 nearest neighbor: C1 = 1/12 held; spec formulas loose

`E G_Q(0) + 12 G_Q(nn) = 1` gives at `E = 12` (cancellation explicit)
`G_Q(0) + G_Q(nn) = 1/12` (quotient) and micro
`C1 := Gd + Gam_nn = (1/2)(1/12 + 1/12) = 1/12`. With frozen
`I := 4(G_Q(0) - G_Q(nn))(12+)`, `C2 := Gd - Gam_nn = (I/4 + 1/12)/2`,
i.e. the quotient-level `I/4` by construction. Both TRUE products
`(Gd +- Gam) = <u_+-|G|u_+->` decrease strictly from finite edge values
to 0, giving exact TRUE nn cuts `|t| > 12` and `|t| > 1/C2 ~ 7.94`.

The spec threshold formulas `t^2 > 12/G3`, `t^2 > 4/(I G3)` are built on
the false secular (section 2) and do not match the true cuts; the spec
`sqrt(128/11) ~ 3.41` exclusion is valid but LOOSE (true nn cut `~7.94`,
green-pinned minus-combo `< 0.25`), so its claimed sharpness is debt.

## 10. Earned distinction (PARTIAL core)

J2: first-binding cut `0` for every `r != 0` (divergent channel,
section 5) with true `8 pi` law (section 6). J3: uniform non-binding
interval `|t| <= 24/sqrt(55)` for every positive separation
(section 8). The dimension/substrate-dependent binding distinction
holds; the sharp spec extras (secular form, `8 pi sqrt2`,
cancelled log, two-channel binding, `sqrt(128/11)` sharpness) are
theorem debt. No bound state is identified with matter, a force, or
an event.

## 11. Finite-size resolution (why Green data drive the ladder)

J2 small-`t` binding has `xi ~ 1/sqrt(Delta_inf)` with
`Delta_inf ~ exp(-8 pi/t)`: for `t <= 2`, `xi` is `10^2--10^5+`,
so feasible-`L` levels sit at `Delta_L ~ 1/L^2` (pre-asymptotic,
particle-in-box-like) and `Y` validity (`L >= 4/sqrt(Delta)`) is
unreachable. J3 small-`t` shifts are perturbative (`~t/N ~ 1/L^3`,
decaying to the edge). Hence finite-`L` counts show `1/1` in both
phases and cannot adjudicate; the battery uses Green
(infinite-volume) data for distinction/sharpness and finite-`L`
records for exact-algebra consistency (det pins, pairing, decay).
`Y1/Y2` are filed with validity flags, descriptive only.
