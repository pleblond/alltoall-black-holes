# First-order continuity already constrains a spontaneous split

Notation: exclusive neighbor sets \(X_i\), \(X_j\), common neighbors \(C\),
\(s=\psi_i+\psi_j\) at the event, merged node \(k\) carrying the same \(s\).
Evolution \(i\partial_t\psi=-A\psi\), so \(\partial_t\psi=iA\psi\).

**Theorem.** Across a sum-map split, \(\mu=s_{\mathrm{split}}-s_{\mathrm{merged}}\)
vanishes at the event for every fiber point. Its first derivative does not
depend on \(d=\psi_i-\psi_j\):

\[
\dot\mu(t_0)=i\Big(s+\sum_{v\in C}\psi_v\Big).
\]

Proof. On the split graph,
\((A\psi)_i=\psi_j+\sum_{X_i}\psi+\sum_C\psi\) and
\((A\psi)_j=\psi_i+\sum_{X_j}\psi+\sum_C\psi\), so

\[
\partial_t(p+q)=i\Big(s+\sum_{X_i}+\sum_{X_j}+2\sum_C\Big).
\]

On the merged graph, \(\partial_t s=i(\sum_{X_i}+\sum_{X_j}+\sum_C)\).
Subtract. The exclusive sums cancel and \(d\) never enters, because only
\(p+q=s\) appears.

**Corollary.** If \(s+\sum_C\psi\neq 0\), no choice of the continuous fiber
coordinate restores \(C^1\) continuity of the summed amplitude. The cover
enters only through \(C\). Uniform JOINT states with \(s\neq 0\) and
\(|C|\ge 0\) fail this condition on every cover: the sum is
\(s(1+|C|)\) times the uniform amplitude, up to normalization, and is not
zero. Spontaneous splits of a uniform vacuum are inadmissible under this
continuity requirement. Stored splits are not spontaneous: STORE0 returns
the true predecessor, whose trajectory matches at every order by
construction.

The second derivative does see \(d\). Differentiating the exclusive sums
brings down \(|X_i|p\) and \(|X_j|q\). The \(d\)-dependent piece of
\(\ddot\mu\) is

\[
-\frac{d}{2}\big(|X_i|-|X_j|\big),
\]

so an asymmetric cover that has already passed the first-order test fixes
at most one \(d\). Higher orders then overdetermine that value. Symmetric
covers (\(|X_i|=|X_j|\)) do not fix \(d\) at this order.

This is a filter on the JET-0 battery, not a replacement for it. Any
candidate filed as a genuine jet match must have
\(s+\sum_C\psi=0\) at the event, or the match is not \(C^1\) for the summed
amplitude. Checking that complex scalar before a long Krylov comparison
empties most of the fiber without a new campaign. The vacuum-uniform cells
should come back empty for spontaneous splits and nonempty only for the
STORE replay, which is the identity match already classified as trivial by
the JET preregistration.
