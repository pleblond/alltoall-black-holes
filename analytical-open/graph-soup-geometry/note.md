# Geometry is the window between a tree and an expander

Two unstructured graphs are not geometric, for different reasons.

- A sparse tree (configuration model below the plaquette scale) has
  exponential volume growth in the branching, \(V(r)\sim (z-1)^r\), until
  the finite size cuts it off. The spectral dimension of a critical
  branched polymer is \(4/3\), not an integer embedding dimension. There is
  no \(d_{\mathrm{eff}}\to 2\) or \(3\) plateau.
- An Erdős–Rényi graph above the connectivity threshold, or a
  configuration model with excess degree and no short cycles, is an
  expander: diameter \(\sim\log N\), and every transport estimator that
  assumes a polynomial ball will refuse or return a large dimension.

The geometric graphs in the earned set sit between these. J2 and the square
have a density of 4-cycles of order one per vertex. The chain weave adds a
thin set of stitches and keeps the sheet cycles. The order parameter that
separates the regimes is the fraction of edges that lie in a 4-cycle,
\(f_\square\). It is \(0\) on a tree, \(O(1)\) on the square and on J2, and
small on a dilute random regular graph of large girth.

**Test.** Plot \(d_{\mathrm{eff}}\) against \(f_\square\) on one
configuration-model family as short cycles are added, holding the degree
sequence fixed. The soup hypothesis is the claim that a plateau at \(2\),
and then a weave window at \(3\), turns on when \(f_\square\) becomes
order one, and that the expander side (\(f_\square\to 0\), degree high)
does not pass through \(3\) on the way. A single random graph with a
reported dimension, and no \(f_\square\), does not locate the transition.
