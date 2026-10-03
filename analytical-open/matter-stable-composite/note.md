# A non-radiating composite needs an eigenvalue below the band

On infinite J2 the essential spectrum of \(H=-A\) is \([-8,8]\) together with
the flat band at \(0\). A finite set of extra edges is a finite-rank
perturbation and does not move the essential spectrum (Weyl). Discrete
eigenvalues may split off below \(-8\).

**Theorem.** If a node subset induces a clique \(K_n\) with \(n\ge 10\), the
normalized indicator of that subset has Rayleigh quotient \(-(n-1)\) for
\(H\). Hence the lowest eigenvalue satisfies \(E_0\le -(n-1)\le -9\), and
the gap to the essential-spectrum edge obeys

\[
m=-8-E_0\ge n-9.
\]

Attachment to the surrounding graph can only push \(E_0\) further down or
leave the variational bound unsaturated from above; it cannot put \(E_0\)
back into \([-8,8]\) while the test vector still scores \(\le -(n-1)\).

For \(n\le 9\) this test vector does not clear the band edge. Small motifs
are not forbidden from binding by some other trial vector, but the clique
argument does not give them a gap. A triangle scores \(-2\), deep inside
the band.

Modes inside the essential spectrum hybridize with the continuum. In two
dimensions the edge density of states is finite
(`why-three-dimensions/note.md`), so a shallow resonance has a width that
does not shut off as it approaches \(-8\). On J3 the width can. The first
stable-particle test is therefore spectral, not a long-time integration:
the eigenvalue of a candidate motif relative to \(-8\) on J2 and to \(-12\)
on J3. A motif with no eigenvalue outside the band is a resonance. Its
decay is unitary radiation under the earned \(H\), and it does not need a
split, a store entry, or a stochastic law.

The flat band is a protected kernel on pure J2, extensive and
non-propagating in the quotient. A localized flat-band packet is hidden
charge, not a moving particle. Motion in the quotient requires a
dispersive-band component, and that component is stable only if it sits
below the edge.
