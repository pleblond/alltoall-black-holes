# Dimensional mismatch does not add an energy beyond the missing bonds

Suppose a region refuses stitches and therefore keeps a local volume
exponent \(2\) inside a weave whose window has exponent \(3\). Every change
in ball growth of a simple graph is a change in the edge set. The field
energy changes only through

\[
E_\psi=-2\sum_{uv\in E}B_{uv}
\]

and through the rearrangement of \(\psi\) on the new graph. There is no
additional term in \(H=-A\) that couples to \(d_{\mathrm{eff}}\) directly.

**Theorem.** For two graphs on the same vertex set,

\[
E_\psi(G')-E_\psi(G)=-2\sum_{e\in E'\setminus E}B_e+2\sum_{e\in E\setminus E'}B_e,
\]

at fixed \(\psi\). A "frustration energy" proportional to
\(|d_{\mathrm{local}}-3|\) is a reparameterization of this bond sum only if
the missing stitches happen to have \(B_e\) correlated with that difference.
Nothing in the earned energy makes that correlation an identity. At
\(B=0\) on every refused stitch the field energy does not move at all,
while \(d_{\mathrm{eff}}\) still changes. Dimension and mass therefore
separate: the kinematic exponent can move at zero bond cost.

The mass that **is** defined is the spectral gap of
`mass-structural-distortion/note.md`. It should be computed from the
eigenvalue, not from a fit of local dimension. A campaign that correlates
local \(d_{\mathrm{eff}}\) with energy will mix the bond sum with the
exponent and can report a slope that is an accident of which edges were
cut. The controlled comparison is the same edge deletion at \(B=0\) and at
\(B\neq 0\): dimension changes in both, energy only in the second.
