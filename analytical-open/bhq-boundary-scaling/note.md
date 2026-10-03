# Why a dimension-versus-area test is the wrong first entropy measurement

H3 and BH-Q-ENT-0 ask whether

\[
D_Q(R)=\dim_{\mathbb R}\{Q\text{ exterior-blind for }R\}
\]

scales as area. The information in `hidden-store-entropy/note.md` scales as
the number of channels you choose to sum, with at most one bit each. Those
are different functions. A pass or fail on \(D_Q\) does not certify
\(S_Q=\sum h_2(P_-)\).

## 1. What one sum-map hides

**Theorem.** The sum map \((p,q)\mapsto s=p+q\) has kernel the complex line
\(d=p-q\), hence real dimension \(2\), for every \(s\) including \(s=0\)
(`split0.fiber_dims`). After the \(U(1)\) quotient the physical dimension
drops to \(1\) only for the all-zero merged state
(`physical_fiber_dims`). Swap \(d\to -d\) is discrete and does not halve
the continuous dimension.

A tree of \(n-1\) interior merges therefore carries naive continuous
dimension \(2(n-1)\), minus at most a finite set of all-zero exceptions.
The ledger formula \(D_Q=2N_d+D_c\) is this count. It is a dimension, and
the note on isolated channels does not convert it into \(h_2\).

## 2. Volume lower bound for any boundary-sized readout

**Theorem.** Suppose each merge contributes an independent complex
coordinate, and the exterior imprint of those coordinates factors through a
complex boundary space of dimension \(\le b=|\partial R|\). Then the real
kernel satisfies

\[
D_Q\ge 2(N_Q-b).
\]

For a space-filling collapse, \(N_Q=n_R-1\) and \(n_R\) grows as volume
while \(b\) grows as area, so the lower bound is volume-leading.

A pure area law for \(D_Q\) contradicts the lower bound unless the number of
free store entries itself scales as area (only cut-adjacent merges left
unfixed) or the imprint rank is volume-sized and tuned so that the kernel
is a boundary layer. Neither tuning is implied by \(H=-A\) or by the sum
map.

If the exterior evolution is the collapsed graph alone, \(Q\) is not in the
Hamiltonian (Q-DYN-0b: \(Q\) is frozen and does not back-react). The
Jacobian of every \((G,\psi)\)-channel on the \(d\)-coordinates is then
identically zero and

\[
D_Q=2(n_R-1)
\]

exactly, a volume law, up to the all-zero reduction. Blindness here is
complete because the coordinates were removed from the state the exterior
evolves, not because of a holographic cancellation.

## 3. Consequence for the queue

Running the BH-Q-ENT-0 ladder first answers whether that kernel is volume
or area. The calculation above says the generic answers are "volume" or
"identically the full \(2(n-1)\)". Neither number is \(h_2\), and neither
is \(k\) bits.

The measurement that lines up with I1 is the sum of \(h_2(1/2-B_e/q_e)\)
over the \(k\) cut legs, after the histogram controls in
`REPORT-test-first.md`. Dimension scaling can wait until that sum is known,
because a volume law for \(D_Q\) is compatible with an area law for the cut
sum: one counts interior relative modes, the other counts leg channels.

## 4. Factor two versus one bit

The factor \(2\) in \(D_Q=2N_d\) is \(\dim_{\mathbb R}\mathbb C\). Promoting
it to two bits per merge double-counts relative to I1a, which assigns one
bit per saturated leg. The binary entropy corrects in the other direction:
at most one bit per channel, and that bit is present only when \(B=0\) (or
on Haar average, \(1/(2\ln 2)\) of a bit). A fit of \(D_Q\) to \(A/4\) has
no algebraic path to the I1 coefficient. The cut sum does, and only when
\(\bar h=1\).
