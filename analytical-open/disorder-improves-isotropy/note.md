# Chain-weave isotropy is a different regime from the 3D window

WEAVE-0's chain construction (prereg M0–M1) joins sheets along a
one-dimensional meeting graph and predicts

\[
\ell_W=\rho^{-1/2}=\frac{1}{2\sqrt{\lambda}}
\]

in sheet cells, from endpoint density \(\rho=4\lambda\). Local balls with
\(r\ll\ell_W\) are two-dimensional. Balls with
\(\ell_W\ll r\ll S\ell_W\) grow as \(r^3/\ell_W\). That volume exponent can
equal \(3\) on an ellipsoid.

## 1. Metric in the window

A transverse step costs an in-plane walk of typical length \(\ell_W\) to the
next stitch, plus one stitch edge. In coordinates \((x,y,z)\) with \(z\) the
sheet index,

\[
ds^2=dx^2+dy^2+\ell_W^2\,dz^2
\]

is the Riemannian approximation consistent with that shortest-path cost.
The linear axis ratio is \(\ell_W\). Random in-plane shifts and a transpose,
which is the orientation record in the preregistration, act on \((x,y)\).
They do not rotate \(z\) into the sheet. The eigenvalue \(\ell_W^2\) is
untouched.

J2's own quadratic symbol is already isotropic in the sheet
(\(\mathrm{Hess}=4I\)). Orientation disorder has nothing left to isotropize
inside a sheet at that order, and it cannot equalize the transverse
eigenvalue.

## 2. The isotropic point is overconnected

\(\ell_W=1\) forces \(\lambda=1/4\). The frozen stub fraction is
\(1-\exp(-2\lambda)\). At \(\lambda=1/4\),

\[
1-e^{-1/2}\approx 0.393>0.25,
\]

which the preregistration labels OVERCONNECTED. Every WOVEN ladder value
\(\lambda\le 0.08\) has \(\ell_W\ge 1/2\sqrt{0.08}\approx 1.77\). A 3D
volume gate can pass there while the axis ratio stays at least \(1.77\).

## 3. What to report beside \(d_{\mathrm{eff}}\)

On each WOVEN cell, the ratio of in-plane to transverse graph-ball radii
(sheet coordinates are known at reveal) should track \(\ell_W(\lambda)\),
not \(1\). A WEAVE0-3D verdict that does not publish this ratio has not
tested isotropy.

The ledger's \(M_{ab}=\langle n_a n_b\rangle\to I/3\) describes a different
ensemble: sheets whose normals are random in an ambient three-dimensional
space. The chain construction has no such normals. Passing chain-weave
gates neither supports nor kills that average. An isotropic infrared
three-space, if it is wanted from sheets, needs a meeting complex whose
transverse and in-plane costs match, which for this metric means giving up
the scale separation the 2D-to-3D crossover is built on.
