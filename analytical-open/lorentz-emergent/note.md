# Quartic obstruction to emergent rotation and Lorentz symmetry

Earned dispersions (`continuum.py`, `dim3.py`), \(J=1\):

\[
\varepsilon_{J2}(q)=-4(\cos q_x+\cos q_y)
=-8+2|q|^2-\frac16(q_x^4+q_y^4)+O(q^6),
\]

\[
\varepsilon_{J3}(q)=-4(\cos q_x+\cos q_y+\cos q_z)
=-12+2|q|^2-\frac16\sum_i q_i^4+O(q^6).
\]

Cross terms \(q_i^2 q_j^2\) are absent because each dispersion is a sum of
functions of a single momentum component. The Hessian at the band bottom is
\(4I\), so the quadratic symbol is isotropic and can be matched to
\(p^2/2m\) with \(m=1/4\).

## 1. The invariant that fails

Write the quartic part as

\[
\beta\sum_i q_i^4+\gamma\sum_{i<j}q_i^2 q_j^2.
\]

A quartic that is a function of \(|q|^2\) comes from \(\beta|q|^4\), and
\(|q|^4=\sum_i q_i^4+2\sum_{i<j}q_i^2 q_j^2\), so

\[
\frac{\gamma}{\beta}=2.
\]

The same ratio is required by the \(O(|p|^4)\) term in
\(\sqrt{m^2c^4+c^2 p^2}\). Both J2 and J3 have \(\beta=-1/6\) and
\(\gamma=0\), hence

\[
\frac{\gamma}{\beta}=0.
\]

**Theorem.** No choice of \(m\), \(c\), or \(J\) makes the quartic symbol of
axis-aligned nearest-neighbor \(H=-A\) rotationally invariant. The first
anisotropic correction and the first departure from the relativistic series
sit at the same order, \(O(q^4)\), which is \(O((a/\lambda)^2)\) relative to
the quadratic term.

EM-0E already records that anisotropy enters at quartic order. The ratio
\(\gamma/\beta\) is the coordinate-free form of that fact, and it is also
the Lorentz obstruction. Tuning the quadratic mass term does not move it.

## 2. What a test can still decide

The long-wave packet propagates under the quadratic symbol, which is
isotropic. A test of arrival direction at small \(k\) will look radial.
That does not touch \(\gamma/\beta\). The observable that carries the
obstruction is the angular dependence of the \(O(k^4)\) correction: the
speed deficit along an axis versus along a diagonal, at fixed \(|k|\).

On J2, \(v_i=\partial_{q_i}\varepsilon=4q_i-(2/3)q_i^3+\cdots\), so

\[
\frac{v_x}{v_y}
=\frac{q_x}{q_y}
\cdot
\frac{4-(2/3)q_x^2}{4-(2/3)q_y^2}.
\]

The ray is parallel to \(q\) only on the axes and on the diagonals. The
angular deflection is \(O(q^2)\).

Substrates whose hoppings are not axis-aligned (triangular, honeycomb) can
produce \(\gamma\neq 0\). Those graphs already fail the VAC-0 interference
class. A search for emergent Lorentz on the square-class vacuum is a search
on the separable side of this identity.

The band-edge Schrödinger group is the symmetry that the quadratic symbol
does have. It is not a partially broken Poincaré symmetry waiting at the
next order; the next order breaks rotations.
