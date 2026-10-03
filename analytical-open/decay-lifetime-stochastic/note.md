# Lifetimes are stochastic only after the deterministic channels are subtracted

Three clocks are already determined, and they should be removed before any
hazard is fitted.

1. **Radiative width.** For an in-band resonance, \(\Gamma=2\pi|V|^2\rho(E)\)
   with \(\rho\) fixed by the dimension (`why-three-dimensions/note.md`).
   The survival probability in the golden-rule regime is exponential with
   that \(\Gamma\). The randomness is the usual continuum branching, and
   the rate is not free.

2. **Bond-threshold crossings.** For a codimension-1 condition the hitting
   times are the roots in `stochastic-timing-only/note.md`. On a few-mode
   parent the pattern is a comb. VACSTAB recurrence that grows with \(L\)
   is this regime. Fitting an exponential to a short segment of a comb
   produces a rate that depends on the window.

3. **Codimension-2 jet condition, exact.** The orbit misses the surface.
   The lifetime against spontaneous structural splits is infinite. An
   exponential fit will report a rate consistent with zero if the run is
   long enough, and a noise rate if it is not.

An exponential structural lifetime is the right description only in a
mixing regime where \(B(t)-B_*\) is well approximated by a Gaussian process
and events are counted as upcrossings of a thickened surface. The Rice
rate of a stationary process \(X(t)\) at level \(a\) is

\[
\lambda=\frac{1}{2\pi}\sqrt{\frac{m_2}{m_0}}\,
\exp\Big(-\frac{a^2}{2m_0}\Big),
\]

with \(m_0=\mathrm{Var}\,X\) and \(m_2=\mathrm{Var}\,\dot X\). Both moments
are integrals of the spectral measure of \(B_{ij}(t)\), hence of the
eigenvalue differences of \(H\) weighted by the mode overlaps on the edge.
Given \(B_*\), \(\lambda\) is determined. The unfixed ratios inside \(B_*\)
(`accounting.b_star`) are the only free parameters, and they are already
flagged as a debt. A one-parameter exponential fit that ignores \(m_0\) and
\(m_2\) is a fit to those ratios in disguise.

Order the analysis as: classify the parent (bound vs resonance, empty \(Q\)
vs stored \(Q\)), subtract clocks 1–3, and only then compare a residual to
the Rice formula. The residual is the part that could still be a new
stochastic law.
