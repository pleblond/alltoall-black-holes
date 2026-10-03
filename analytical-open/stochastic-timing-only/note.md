# Timing on a bond threshold is a root of a known function

A real admissibility condition \(B_{ij}(t)=B_*\) is one real constraint.
Along the unitary orbit, \(B_{ij}(t)=\Re(\psi_i(t)^*\psi_j(t))\) is an
almost-periodic function whose frequencies are eigenvalue differences of
\(H\). For a two-mode state

\[
B(t)=B_0+C\cos(\omega t+\varphi)
\]

the crossings of a level \(B_*\) exist if and only if \(|B_*-B_0|\le|C|\),
at

\[
t=\frac{1}{\omega}\Big(\pm\arccos\frac{B_*-B_0}{C}-\varphi\Big)+\frac{2\pi n}{\omega}.
\]

That is a deterministic comb. It is not an exponential waiting time.

The complex condition \(s+\sum_C\psi=0\) from
`dynamical-jet-admissibility/note.md` is two real constraints. A
one-dimensional orbit misses a codimension-2 submanifold for generic
initial data. Exact jet continuity of that strength predicts no
spontaneous events, which matches the earned statements that the unitary
flow does not fire (BR-2.7) and that small perturbations do not grow into
events (VACSTAB). Stochastic timing is not required to explain the
absence.

Stochastic timing becomes necessary only if several edges satisfy a
codimension-1 condition in the same window and a tie-break among them is
unfixed. That tie-break is the same measure debt as rewire
(`rewire-as-weak/note.md`), not a property of the clock. The clock on each
edge is the arccos formula, or its almost-periodic generalization, once
\(B_*\) is given. BR-2.6 leaves the ratios inside \(B_*\) unfixed, so the
level is not known. Measuring the spectrum of \(B_{ij}(t)\) on a fixed
graph tells the crossing times for every candidate level in one stroke.
A stochastic scheduler on top of that spectrum is a second object and
should not be fitted first.
