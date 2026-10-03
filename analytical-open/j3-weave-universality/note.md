# J3 and a scale-separated weave share a quadratic form only after a rescaling that removes the weave

J3 at the band bottom:

\[
\varepsilon=-12+2(q_x^2+q_y^2+q_z^2)-\frac16\sum_i q_i^4+\cdots,
\qquad\mathrm{Hess}=4I_3.
\]

A chain weave of J2 sheets, stitches of transverse scale \(t_\perp\) in the
sheet-index Brillouin zone, has

\[
\mathrm{Hess}=\mathrm{diag}(4,4,t_\perp)
\]

at quadratic order, and the in-plane quartic remains \(-(1/6)(q_x^4+q_y^4)\)
with no \(q_x^2 q_y^2\) term. Rescaling \(z'=z\sqrt{t_\perp/4}\) matches the
quadratic forms and does not match the quartic, nor the flat band.

J3's flat band is exact: \(H(k)\propto\begin{pmatrix}1&1\\1&1\end{pmatrix}\)
has a structural zero eigenvalue at every \(k\). A stitch between sheets
that mixes the sheet-antisymmetric vector with the symmetric one lifts that
zero. The preregistered mixing norm \(\|P_-HP_+\|\) on meeting pairs is the
matrix element of that lift. At small \(\lambda\) the flat-band splitting is
linear in the stitch amplitude for a coherent stack, and of order the
bandwidth of the random transverse hopping for a disordered weave. J3's
nullity at linear size \(L\) is \(L^3\) plus the touching count. A woven
stack of \(S\) sheets of size \(L\) starts from \(S L^2\) flat zeros before
stitches and should not keep them.

**Test, before any propagator comparison.** Nullity versus \(\lambda\) on
the woven graph, next to the disjoint-union count \(S L^2\). If the zero
band survives, the stitches are not doing what the chain construction
says. If it lifts, the spectra are not in one class with J3, even when a
rescaled quadratic packet looks similar. Matching propagators after
fitting three anisotropic lengths is a test of the quadratic symbol only.
