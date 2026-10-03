# Nothing in the earned dynamics relaxes \(M_{ab}\)

The chain weave has no ambient normals, so \(M_{ab}=\langle n_a n_b\rangle\)
is not an observable of that ensemble
(`disorder-improves-isotropy/note.md`). On an ensemble that does assign
normals, the orientation of a sheet is a function of \(G\). Between events
\(G\) is fixed, so \(M_{ab}\) is fixed. Rewires that could rotate a local
frame are exactly the degenerate moves of REWIRE0: no bond, current, or
energy drift selects a rotation. The deterministic drift of \(M_{ab}\) is
zero. A diffusion in orientation space would be a measure on those ties,
which is the unearned history measure.

**Prediction.** Under every earned deterministic rule, the eigenvalue gap
of \(M_{ab}\) is constant in time. A numerical relaxation of that gap is a
signal that a measure or a firing rule has been inserted. That is worth
knowing, and it should be labeled as an insertion. It is not a consequence
of \(H=-A\) or of sum-map contraction.

Isotropy, when it is present, is a property of the initial ensemble (Haar
on orientations gives \(M_{ab}=I/3\) by symmetry) or of the construction
(J3's Hessian is \(4I\)). It is not an attractor of the present equations.
A test that evolves sheet angles under \(H=-A\) and watches \(M_{ab}\)
should see a flat line. A declining gap means the angle update was not
\(H\).
