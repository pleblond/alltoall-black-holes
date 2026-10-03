# The hazard is the Rice rate of \(B(t)\), up to the unfixed level

The ledger asks for a waiting-time law derived rather than assumed. For a
codimension-1 bond condition the derivation is the Rice formula in
`decay-lifetime-stochastic/note.md`:

\[
\lambda(B_*)
=\frac{1}{2\pi}\sqrt{\frac{m_2}{m_0}}
\exp\Big(-\frac{(B_*-\mu)^2}{2m_0}\Big).
\]

Here \(\mu\), \(m_0\), and \(m_2\) are the mean, variance, and derivative
variance of \(B_{ij}(t)\) along the unitary orbit. They are computable from
the spectral decomposition of the parent without a stochastic model.

Special cases that should be checked before the general formula:

- Two-mode parent: \(\lambda\) is a sum of deltas at the arccos roots, not a
  constant hazard. The survival curve is a step train.
- Haar-static snapshot, no preferred time: the distribution of \(B/q\) is
  known (`hidden-store-entropy/note.md`), but a single Haar vector is not a
  process. A hazard requires the process, not the snapshot.
- Exact codimension 2: \(\lambda=0\).

\(B_*\) is not fixed by the ontology (two ratios free in the conditional
conservation identity). The family \(\lambda(B_*)\) is the prediction.
Estimating a single \(\lambda\) and comparing it to \(\ln 2\) or to a
lifetime in seconds skips the shape of \(\lambda(B_*)\), which is the
falsifier. A Gaussian dependence on the level, with width \(\sqrt{m_0}\)
taken from the same trajectory that supplies the crossings, is the test.
A level-independent rate falsifies the Rice picture and would be new.
