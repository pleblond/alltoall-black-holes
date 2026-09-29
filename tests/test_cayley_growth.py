"""Tests for the Cayley-growth probe (group laws + exact small balls)."""
import numpy as np

from bh_graph.cayley_growth import ball_volumes, fit_growth_degree, neighbors


def test_klein_relation():
    """xyx^-1 = y^-1 on the frozen normal form (spot elements)."""
    rng = np.random.default_rng(0)
    for _ in range(50):
        k, m = (int(rng.integers(-5, 6)), int(rng.integers(-5, 6)))
        x = lambda t: (t[0] + 1, -t[1])  # noqa: E731
        xi = lambda t: (t[0] - 1, -t[1])  # noqa: E731
        y = lambda t: (t[0], t[1] + 1)  # noqa: E731
        yi = lambda t: (t[0], t[1] - 1)  # noqa: E731
        assert xi(y(x((k, m)))) == yi((k, m))
        assert x(xi((k, m))) == (k, m)


def test_heisenberg_inverses_and_assoc():
    def mul(p, q):
        return (p[0] + q[0], p[1] + q[1], p[2] + q[2] + p[0] * q[1])

    a, ai = (1, 0, 0), (-1, 0, 0)
    b, bi = (0, 1, 0), (0, -1, 0)
    e = (0, 0, 0)
    assert mul(a, ai) == mul(b, bi) == e
    assert mul(mul(a, b), bi) == a  # associativity spot
    assert mul(a, b) == (1, 1, 1) and mul(b, a) == (1, 1, 0)  # nonabelian


def test_neighbor_counts():
    assert len(neighbors("z3", (0, 0, 0))) == 6
    assert len(set(neighbors("heis", (0, 0, 0)))) == 4  # distinct gens
    assert len(set(neighbors("klein", (0, 0)))) == 4


def test_small_ball_exact_counts():
    assert ball_volumes("z3", 2) == {0: 1, 1: 7, 2: 25}
    assert ball_volumes("heis", 1) == {0: 1, 1: 5}
    assert ball_volumes("klein", 1) == {0: 1, 1: 5}


def test_fit_recovers_cubic():
    vols = {r: int(round(4.19 * r ** 3)) for r in range(1, 12)}
    vols[0] = 1
    out = fit_growth_degree(vols, 5, 11)
    assert abs(out["d"] - 3.0) < 0.05 and out["r2"] > 0.999


def test_bfs_deterministic():
    assert ball_volumes("heis", 6) == ball_volumes("heis", 6)
