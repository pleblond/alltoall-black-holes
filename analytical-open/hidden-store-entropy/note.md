# Isolated boundary information from the bond

Status of each step is marked **theorem** (follows from the frozen
definitions) or **identification** (extra, not in the earned ledger).

Frozen inputs used:

- \(B_{ij}=\Re(\psi_i^*\psi_j)\) (`bond_B` in `backreaction.py`).
- Sum-map contraction, \(\Delta\|\psi\|^2=2B_{ij}\) (`event_ledger`,
  `dQ_formula`).
- \(\Delta E_\psi=2B_{ij}-2\Sigma_{\mathrm{cross}}\), common-neighbor
  collapse energy-neutral.
- Fiber coordinates \(s=p+q_{\mathrm{daughter}}\), \(d=p-q_{\mathrm{daughter}}\)
  (`split0.fiber_point`).
- I1a: a saturated leg carries \(\ln 2\) nats; matching gives
  \(A=4\ln 2\cdot k\,\ell_P^2\).

## 1. Bond, sum, difference

**Theorem.** Let \(s=\psi_i+\psi_j\), \(d=\psi_i-\psi_j\), and
\(q_{ij}=|\psi_i|^2+|\psi_j|^2\). Then

\[
|s|^2=q_{ij}+2B_{ij},\qquad
|d|^2=q_{ij}-2B_{ij},
\]

\[
|s|^2-|d|^2=4B_{ij},\qquad
|s|^2+|d|^2=2q_{ij}.
\]

Proof. Expand \(|\psi_i\pm\psi_j|^2\). The cross term is
\(2\Re(\psi_i^*\psi_j)=2B_{ij}\).

**Theorem.** \(|B_{ij}|\le q_{ij}/2\), because
\(|\Re(\psi_i^*\psi_j)|\le|\psi_i||\psi_j|\le q_{ij}/2\).

**Theorem.** For \(q_{ij}>0\),

\[
P_-=\frac{|d|^2}{|s|^2+|d|^2}
=\frac12-\frac{B_{ij}}{q_{ij}},\qquad
P_+=\frac12+\frac{B_{ij}}{q_{ij}}.
\]

The same \(P_-\) is obtained from the unitary \(\pm\) modes
\(\alpha=s/\sqrt{2}\), \(\beta=d/\sqrt{2}\), since the factors of \(2\) cancel.

**Theorem.** \(B_{ij}=0\iff|s|=|d|\iff P_+=P_-=1/2\), provided \(q_{ij}>0\).

**Theorem.** \(B_{ij}=0\iff\Delta\|\psi\|^2=0\) for the sum-map contraction
of that pair. This is norm neutrality. It is not energy neutrality in
general:

\[
\Delta E_\psi\big|_{B=0}=-2\Sigma_{\mathrm{cross}}.
\]

On \(K_N\) the exclusive sets are empty (every third node is a common
neighbor), so \(\Sigma_{\mathrm{cross}}=0\) and \(B=0\) is energy-neutral
as well. On a cut leg, exclusive neighbors remain and the two statements
diverge.

If \(q_{ij}=0\), both amplitudes vanish, \(B_{ij}=0\), and there is no
channel. Exclude those edges. The formula \(P_-\) is undefined there; the
information of an empty pair is \(0\), not the limit of \(h_2\), which
depends on the direction of approach.

## 2. Binary entropy of the weight

**Identification, not a ledger theorem.** Assign to a single occupied pair
the Shannon entropy of its \(\pm\) Bernoulli weight,

\[
s_e=h_2(P_-),\qquad
h_2(p)=-p\log_2 p-(1-p)\log_2(1-p).
\]

This is the uncertainty of a projective \(\pm\) measurement on that pair.
It is not the von Neumann entropy of the global pure state, which is \(0\).
It does not score the relative phase of \(d\) against \(s\). At \(B=0\) the
bond is a pure current,

\[
\big|\Im(\psi_i^*\psi_j)\big|=|\psi_i||\psi_j|,
\]

so the unscored datum is exactly the sign and the occupancy of that current.
I1a also counts one bit per saturated leg, not one bit plus a phase. The
continuous-fiber count \(\dim_{\mathbb R}=2\) scores both the magnitude and
the phase and is a different quantity (see `bhq-boundary-scaling/note.md`).

**Theorem, given the identification.** \(0\le s_e\le 1\), with \(s_e=1\)
iff \(B_{ij}=0\) and \(s_e=0\) iff \(|B_{ij}|=q_{ij}/2\).

**Theorem.** With \(x=B/q\) and \(|x|\le 1/2\),

\[
h_2\Big(\frac12-x\Big)
=1-\frac{2}{\ln 2}\,x^2-\frac{4}{3\ln 2}\,x^4+O(x^6).
\]

Proof. Let \(f(x)=(1/2-x)\ln(1/2-x)+(1/2+x)\ln(1/2+x)\). Then
\(h_2=-f/\ln 2\), \(f(0)=-\ln 2\), \(f'(0)=0\), \(f''(x)=4/(1-4x^2)\),
\(f''(0)=4\), \(f'''(0)=0\), \(f''''(0)=32\). The Taylor polynomial of \(f\)
through order \(4\) is \(-\ln 2+2x^2+(4/3)x^4\). Divide by \(-\ln 2\).

There is no odd term. A symmetric cloud of small signed bonds does not
move \(\bar h\) at first order.

## 3. Haar average, exact at finite \(N\)

**Theorem.** Let \(\psi\) be uniform on the unit sphere in \(\mathbb C^N\),
\(N\ge 2\), and let \(\{i,j\}\) be any fixed pair. Then

\[
P_-\sim\mathrm{Uniform}[0,1],
\]

and

\[
\mathbb E[h_2(P_-)]=\frac{1}{2\ln 2}.
\]

Proof. Squared moduli of a Haar vector are Dirichlet\((1,\ldots,1)\): they
have the law of \((e_1,\ldots,e_N)/\sum e_k\) with \(e_k\) i.i.d.
exponential. For any two coordinates,

\[
\frac{|\psi_i|^2}{|\psi_i|^2+|\psi_j|^2}
=\frac{e_i}{e_i+e_j}
\]

is uniform on \([0,1]\) and independent of the rest of the sample. The
change of basis

\[
\alpha=\frac{\psi_i+\psi_j}{\sqrt{2}},\qquad
\beta=\frac{\psi_i-\psi_j}{\sqrt{2}}
\]

is a global unitary (identity off the pair). Haar measure is invariant, so
\((|\alpha|^2,|\beta|^2)\) has the same two-coordinate law. Therefore

\[
P_-=\frac{|\beta|^2}{|\alpha|^2+|\beta|^2}
\]

is uniform on \([0,1]\) for every finite \(N\ge 2\).

The integral uses \(\int_0^1 -p\ln p\,dp=1/4\) and the symmetric partner:

\[
\int_0^1 h_2(p)\,dp
=\frac{1}{\ln 2}\cdot\frac12
=\frac{1}{2\ln 2}.
\]

Independence of the fraction and the pair-norm also says that weighting
edges by \(q_{ij}\) does not change the Haar mean: \(h_2(P_-)\) is a
function of the fraction alone.

## 4. The other two ensembles

**Theorem (real ground state).** The all-ones vector on \(K_N\), normalized,
has \(\psi_i=\psi_j=N^{-1/2}\) real, so \(B_{ij}=1/N\), \(q_{ij}=2/N\),
\(B/q=1/2\), \(P_-=0\), \(h_2=0\) on every edge. This is the ground state
of \(H=-A\) (eigenvalue \(-(N-1)\)).

**Theorem (arcsine).** If the relative phase is uniform and the two moduli
are equal, then \(P_-=(1-\cos\phi)/2\) with \(\phi\) uniform, which is
Beta\((1/2,1/2)\). The same law is the norm fraction of a real
two-dimensional Gaussian. Against the arcsine density
\(1/(\pi\sqrt{p(1-p)})\),

\[
\int_0^1 h_2(p)\,\frac{dp}{\pi\sqrt{p(1-p)}}
=2-\frac{1}{\ln 2}.
\]

Proof of the integral. Symmetry splits \(h_2\) into two equal terms. One of
them is

\[
\frac{1}{\pi\ln 2}
\int_0^1
\frac{-p\ln p}{\sqrt{p(1-p)}}\,dp
=\frac{1}{\pi\ln 2}
\Big(-\partial_a B(a,b)\Big)_{a=3/2,\,b=1/2}.
\]

\(B(3/2,1/2)=\pi/2\) and
\(\psi(3/2)-\psi(2)=1-2\ln 2\), so
\(-\partial_a B=(\pi/2)(2\ln 2-1)\). One term equals
\((2\ln 2-1)/(2\ln 2)\). Both terms give \(2-1/\ln 2\).

A control that randomizes phases at fixed equal magnitudes, or that draws
real amplitudes, is this row. It is not a finite-\(N\) correction to Haar.

## 5. Scale-separated endpoints

**Theorem.** Fix \(v>0\) and let \(\psi_i=\sigma g\) with \(g\) complex normal,
\(E|g|^2=1\), independent of a real endpoint \(\psi_j=v\). Set
\(\lambda=\sigma/v\). Then

\[
x=\frac{\lambda\,\Re g}{1+\lambda^2|g|^2}.
\]

As \(\lambda\to 0\) or \(\lambda\to\infty\), \(x\to 0\) in probability and
\(h_2(1/2-x)\to 1\) in probability.

For small \(\lambda\), \(x=\lambda\Re g+O(\lambda^3)\). With
\(E[(\Re g)^2]=1/2\),

\[
E[x^2]=\frac{\lambda^2}{2}+O(\lambda^4).
\]

The expansion of section 2 then gives

\[
1-E[h_2]=\frac{\lambda^2}{\ln 2}+O(\lambda^4).
\]

So a dynamical drive toward quadrature is unnecessary whenever the cut is
scale-separated. The ground-state row (\(h_2=0\)) and the Haar row
(\(h_2=1/(2\ln 2)\)) are both equal-amplitude ensembles. They are the wrong
baseline for a leg whose exterior end is a vacuum amplitude and whose
interior end is diluted over \(N\).

The kinematic special case \(\psi_j=0\), \(\psi_i\neq 0\) is exactly \(B=0\),
hence \(h_2=1\). That endpoint is the \(\psi=0\) limit, which the ledger
already distinguishes from the JOINT vacua. A numerical zero on the
exterior end will saturate \(s_e\) for a trivial reason; the amplitude
ratio has to be reported beside \(h_2\).

## 6. Area form, and what is already fixed

**Theorem, given the identification and an edge set \(\partial\) of
independent channels.** If correlations between channels are ignored,

\[
S_Q=\sum_{e\in\partial}h_2(P_{-,e})=N_\partial\,\bar h,
\qquad
0\le S_Q\le N_\partial,
\]

with equality to \(N_\partial\) iff \(B_e=0\) on every occupied channel.

**Theorem (I1 arithmetic).** \(S=k\ln 2\) nats means \(k\) bits, and
\(A/(4\ell_P^2\ln 2)=k\). If the channel set is exactly the cut,
\(N_\partial=k\), then

\[
S_Q=k\quad\Longleftrightarrow\quad\bar h=1,
\]

and the Bekenstein–Hawking coefficient in bits is reproduced with no free
\(\sigma_\partial\) and no free microscopic area. If instead the cut is Haar
on both ends,

\[
S_Q=\frac{k}{2\ln 2},
\]

which is short of \(k\) by the constant factor \(2\ln 2\). Adjusting
\(a_\partial\) to hide that factor removes the ability to tell the Haar row
from the quadrature row.

**Not a theorem.** That a formed horizon selects one of these rows. Section
5 says scale separation selects the quadrature row without a selection
principle. A measurement of \(\lambda\) and the histogram of \(x\) on the
cut decides. No graph evolution is required for that comparison.

Correlations between channels can change the coefficient and can add
subleading perimeter terms. They are not needed to choose which ensemble
baseline to subtract. The isolated sum is the object to measure first; a
mutual-information correction is a later difference from that sum.

## 7. BR-2 does not supply \(B=0\)

BR2-QUADRATURE says structural response tracks \(\cos\Delta\theta\) through
\(B\) and staggered flux tracks \(\sin\Delta\theta\) through the current. It
does not set \(\cos\Delta\theta=0\) on horizon edges. Sharing the word
"quadrature" with the condition \(B=0\) is a pun. The horizon condition is
the vanishing of \(B\), which is equivalent to a relative phase of
\(\pm\pi/2\) only after both amplitudes are nonzero. It is not implied by
the earned phase-response statement.
