# Internal levels are the discrete eigenvalues below the edge

A finite motif on \(n\) nodes has at most \(n\) eigenvalues. Those that lie
below the essential-spectrum edge are stable against radiative decay; those
inside the band are resonances whose widths track the density of states
(`why-three-dimensions/note.md`).

For an isolated clique the spectrum of \(H=-A\) is one level \(-(n-1)\) and
an \((n-1)\)-fold level \(+1\). Only the ground level can sit below \(-8\),
and only for \(n\ge 10\). The excited clique level \(+1\) is inside
\([-8,8]\) and is not a stable internal excitation. Coupling to the lattice
splits the degenerate \(+1\) multiplet into resonances, not into a tower of
bound states, unless the coupling pushes some of them below the edge.
Variational room below the edge is not automatic for those excited vectors:
the all-ones direction is the one that scores \(-(n-1)\).

**Test.** For each candidate motif, list eigenvalues of the decoupled
motif, then the eigenvalues of the motif plus its lattice attachment that
fall below \(-8\) (below \(-12\) on J3). The count of those eigenvalues is
the internal spectrum. A dense set of levels inside the band is a
continuum resonance spectrum and should not be binned as particle lines.
Selection rules are the commutant of the motif's automorphism group with
\(H\); they can be read off before any time evolution.
