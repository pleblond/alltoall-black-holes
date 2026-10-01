"""D15.1: unitary scalar-walk positive control on J2 (S3 rung).

D15.0 banked the null: phase-free DIFFUSIVE scalar updates (S0/S1 states,
averaging dynamics) collapse the J2 cell onto the symmetric channel --
rank-1 sheet-blind blocks, one live band + one dead band, k-independent
eigenvectors. This module is the detector calibration: it implements the
D'Ariano-Erba-Perinotti construction (Phys Rev A 100, 012105 (2019)) --
a scalar (s = 1) UNITARY walk on J2 -- and shows the same coarse-graining
apparatus firing on it: two unit-modulus bands, k-dependent eigenvectors,
Dirac cone with velocity 1/sqrt(2).

Derivation chain (nothing hand-tuned):
1. Isotropic 2D coin walk, Eq. A4 of the paper, at alpha = 1/sqrt(2)
   (the Weyl member): weyl_isotropic_matrices().
2. Hadamard basis change H (the paper's claim is up to unitary
   equivalence): in the H-rotated basis the Weyl matrices fit the J2
   coarse pattern A_{+y} = sigma_x A_{+x} sigma_x (verified in-module).
3. Read off the 8 scalar transition amplitudes z_h from that pattern:
   z_{h1} = z_{h1c} = z_{h2^-1} = 1/2, z_{h2^-1 c} = -1/2, rest 0.
4. Verify the z's satisfy the scalar unitarity constraints Eq. 9 on J2
   group arithmetic (both hh'^-1 and h^-1 h' families) -- independent
   of any coarse-graining convention.
5. Propagate psi'(p) = sum_s z_s psi(p.s) on the J2 torus (finite,
   boundary-free, exactly unitary) and extract coarse blocks by complex
   impulse response; they match the H-rotated Weyl matrices to 1e-12.

Two subtleties, both pinned in tests/test_j2qw.py:
- The Weyl z-set is REAL-signed (+-1/2, 0): no complex on-site phases
  are needed in this basis; complex structure enters via the Bloch
  phases e^{ik.d} and the matrix structure. The operative distinction
  vs D15.0 is the UPDATE algebra (unitary vs diffusive) at least as
  much as the STATE algebra (C vs R).
- Individual coarse blocks are rank 1 here too (paper Eq. 13: each
  A_{+-h} is rank 1 by unitarity). "Rank-2 blocks" is the wrong
  detector; the live detectors are TWO UNIT-MODULUS BANDS (|lam| = 1
  for both, vs {decaying, 0} in D15.0) and K-DEPENDENT EIGENVECTORS
  ([P_sym, M(k)] != 0, vs exactly 0.0 in D15.0).

Honest labels: this control ASSUMES complex amplitudes + unitarity (the
paper's starting point), so it calibrates the detector and reproduces
the precedent -- it does not derive quantum phase. Derivation (S2 -> S3
emergence) is queued as D15.2.
"""
from __future__ import annotations

import networkx as nx
import numpy as np

from bh_graph.j2excitation import (
    J2_DISPLACEMENTS,
    bloch_eigenvalues,
    bloch_matrix,
    commutator_norm,
    symmetric_projector,
)

#: Walk-graph generator set (degree 8, inverse-closed).
J2_GENS: tuple[tuple[int, int, int], ...] = (
    (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0),
    (1, 0, 1), (-1, 0, 1), (0, 1, 1), (0, -1, 1),
)


def j2_mul(p, s):
    """J2 = Z^2 rtimes Z2 (swap action): (x,y,b).(u,v,d)."""
    (x, y, b), (u, v, d) = p, s
    a1, a2 = (u, v) if b == 0 else (v, u)
    return (x + a1, y + a2, (b + d) % 2)


def j2_inv(p):
    """Inverse: (-x,-y,0) on sheet 0; (-y,-x,1) on sheet 1 (swap)."""
    x, y, b = p
    return (-x, -y, 0) if b == 0 else (-y, -x, 1)


def torus_mul(period: int):
    """Right-multiplication closure with x, y taken mod period."""
    def _mul(p, s):
        x, y, b = j2_mul(p, s)
        return (x % period, y % period, b)
    return _mul


def build_j2_torus(period: int) -> nx.Graph:
    """Finite J2 Cayley graph: (Z_period x Z_period) rtimes Z2, degree 8.

    Boundary-free (every node has all 8 successors), so the scalar walk
    is EXACTLY unitary on it. Quotient is the period x period torus grid
    with micro-multiplicity 4 per coarse edge.
    """
    if period < 3:
        raise ValueError("period must be >= 3 (else generator images collide)")
    mul = torus_mul(period)
    g = nx.Graph()
    nodes = [(x, y, b) for x in range(period) for y in range(period) for b in (0, 1)]
    g.add_nodes_from(nodes)
    for p in nodes:
        for s in J2_GENS:
            g.add_edge(p, mul(p, s))
    return g


def is_closed_under_successors(nodes, mul, gens=J2_GENS) -> bool:
    """Boolean check: p.s is in the node set for every node p and generator s."""
    return all(mul(p, s) in nodes for p in nodes for s in gens)


def hadamard() -> np.ndarray:
    """H = (sigma_x + sigma_z)/sqrt(2): maps the Weyl basis onto the J2 pattern."""
    return np.array([[1.0, 1.0], [1.0, -1.0]]) / np.sqrt(2.0)


def weyl_isotropic_matrices(alpha: float | None = None) -> dict[str, np.ndarray]:
    """Paper Eq. A4: isotropic 2D coin walk; alpha = 1/sqrt(2) is the Weyl member."""
    if alpha is None:
        alpha = 1.0 / np.sqrt(2.0)
    beta = np.sqrt(1.0 - alpha * alpha)
    return {
        "+x": np.array([[alpha * alpha, 0.0], [alpha * beta, 0.0]]),
        "-x": np.array([[0.0, -alpha * beta], [0.0, alpha * alpha]]),
        "+y": np.array([[beta * beta, 0.0], [-alpha * beta, 0.0]]),
        "-y": np.array([[0.0, alpha * beta], [0.0, beta * beta]]),
    }


def weyl_coarse_blocks(alpha: float | None = None) -> dict[tuple[int, int], np.ndarray]:
    """H-rotated Weyl matrices in J2-delta order: the target coarse operator."""
    h_mats = weyl_isotropic_matrices(alpha)
    h = hadamard()
    rot = {k: h @ m @ h for k, m in h_mats.items()}
    return {(1, 0): rot["+x"], (-1, 0): rot["-x"], (0, 1): rot["+y"], (0, -1): rot["-y"]}


def weyl_z_set(alpha: float | None = None) -> dict[tuple[int, int, int], complex]:
    """Scalar amplitudes z_h read off the J2 pattern in the H-rotated basis.

    A_{+x} = [[z_x, z_xc], [z_yc, z_y]] (paper Sec. V, J2 case); the
    companion constraint A_{+y} = sigma_x A_{+x} sigma_x is verified
    (not assumed) before read-off.
    """
    blocks = weyl_coarse_blocks(alpha)
    sx = np.array([[0.0, 1.0], [1.0, 0.0]])
    for plus, minus in (((1, 0), (0, 1)), ((-1, 0), (0, -1))):
        if np.max(np.abs(blocks[minus] - sx @ blocks[plus] @ sx)) > 1e-12:
            raise ValueError("Weyl matrices do not fit the J2 pattern in this basis")
    px, mx = blocks[(1, 0)], blocks[(-1, 0)]
    return {
        (1, 0, 0): complex(px[0, 0]),
        (1, 0, 1): complex(px[0, 1]),
        (0, 1, 1): complex(px[1, 0]),
        (0, 1, 0): complex(px[1, 1]),
        (-1, 0, 0): complex(mx[0, 0]),
        (-1, 0, 1): complex(mx[0, 1]),
        (0, -1, 1): complex(mx[1, 0]),
        (0, -1, 0): complex(mx[1, 1]),
    }


def scalar_unitarity_report(
    z: dict[tuple[int, int, int], complex], gens=J2_GENS
) -> dict[str, float]:
    """Paper Eq. 9 (s = 1) on J2 group arithmetic, both difference families.

    Returns worst |sum - delta_{g,e}| over all g in {h h'^-1} and
    {h^-1 h'} plus the family sizes (18 each for the Weyl z-set).
    """
    out: dict[str, float] = {}
    for tag, combine, conj_first in (
        ("a", lambda h, hp: j2_mul(h, j2_inv(hp)), False),
        ("b", lambda h, hp: j2_mul(j2_inv(h), hp), True),
    ):
        fams: dict = {}
        for h in gens:
            for hp in gens:
                fams.setdefault(combine(h, hp), []).append((h, hp))
        worst = 0.0
        for g, pairs in fams.items():
            if conj_first:
                s = sum(np.conj(z[h]) * z[hp] for h, hp in pairs)
            else:
                s = sum(z[h] * np.conj(z[hp]) for h, hp in pairs)
            want = 1.0 if g == (0, 0, 0) else 0.0
            worst = max(worst, abs(s - want))
        out[f"n_g_{tag}"] = float(len(fams))
        out[f"worst_{tag}"] = float(worst)
    return out


def qw_step(psi: dict, z: dict, mul, gens=J2_GENS, only=None) -> dict:
    """One scalar-walk tick: psi'(p) = sum_s z_s psi(p.s).

    Precondition: psi covers all successors of the updated nodes (torus:
    always; ball: pass only = strict-interior nodes). With only=None the
    whole field is updated.
    """
    targets = psi if only is None else only
    return {p: sum(z[s] * psi[mul(p, s)] for s in gens) for p in targets}


def qw_norm(psi: dict) -> float:
    """Total probability sum |psi|^2 (conserved under unitary evolution)."""
    return float(sum(abs(v) ** 2 for v in psi.values()))


def impulse_blocks_qw(nodes, mul, key, center: tuple[int, int], z: dict) -> dict:
    """Coarse blocks by complex impulse response at a translation-invariant cell.

    key(x, y, b) maps cell+sheet to a node (identity on the ball,
    mod-period on the torus); center is (x, y). Impulse on sheet j of
    cell center+delta; column j of A_delta is read off the two sheets
    of center after one tick. Precondition: all probed nodes exist and
    the centre's successors are closed (torus: always; ball: strict
    interior centre).
    """
    dest = [key(center[0], center[1], 0), key(center[0], center[1], 1)]
    blocks = {}
    for dx, dy in J2_DISPLACEMENTS:
        cols = []
        for j in (0, 1):
            psi = dict.fromkeys(nodes, 0j)
            psi[key(center[0] + dx, center[1] + dy, j)] = 1.0 + 0j
            nxt = qw_step(psi, z, mul, only=dest)
            cols.append([nxt[dest[0]], nxt[dest[1]]])
        blocks[(dx, dy)] = np.array(cols, dtype=complex).T
    return blocks


def cone_velocity(blocks: dict[tuple[int, int], np.ndarray], direction, q: float = 0.05) -> float:
    """Dirac-cone slope omega(|k| = q along direction)/q from M(k) eigenphases."""
    d = np.asarray(direction, dtype=float)
    d = d / np.linalg.norm(d)
    w = bloch_eigenvalues(blocks, float(q * d[0]), float(q * d[1]))
    return float(np.max(np.abs(np.angle(w))) / q)


__all__ = [
    "J2_GENS",
    "bloch_eigenvalues",
    "bloch_matrix",
    "build_j2_torus",
    "commutator_norm",
    "cone_velocity",
    "hadamard",
    "impulse_blocks_qw",
    "is_closed_under_successors",
    "j2_inv",
    "j2_mul",
    "qw_norm",
    "qw_step",
    "scalar_unitarity_report",
    "symmetric_projector",
    "torus_mul",
    "weyl_coarse_blocks",
    "weyl_isotropic_matrices",
    "weyl_z_set",
]
