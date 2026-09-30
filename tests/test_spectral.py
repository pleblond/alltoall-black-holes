"""Spectral dimension: second universality leg (D10 spectral leg).

Combinatorial-Laplacian heat trace + Weyl counting fits under one frozen
rule. Torus anchor pins the method (wide plateau at 2, boundary-free);
every Tier-1 member lands in one band -- including k-NN, whose slow
diffusive crossover reads 1.51 at N=1600 but converges to ~1.93+ at
N=6400 (clustering-trap transient, not a split). Lloyd excluded: the
unclipped relaxation coalesces points above its validated regime
(graphs.py documents; boundary-clipped Lloyd queued).
"""
import networkx as nx
import numpy as np

from bh_graph.graphs import (
    build_gabriel,
    build_hex_lattice,
    build_knn,
    build_medial_quad,
    build_poisson_delaunay,
    build_torus_grid,
    build_triangular_lattice,
)
from bh_graph.spectral import counting_ds, heat_ds, low_spectrum


def test_torus_heat_plateau_is_2():
    # Method anchor: boundary-free 60x60 torus holds d_s(t) in
    # (1.95, 2.05) over a full decade t in [10, 100] (measured
    # 2.02 -> 1.99); finite-size falloff only past t ~ 150.
    g = build_torus_grid(60)
    ts = np.unique(np.logspace(0.5, 3.2, 30).astype(int)).astype(float)
    ds = heat_ds(g, ts)
    band = ds[(ts >= 10) & (ts <= 100)]
    assert len(band) >= 8, (len(band), ts)
    assert all(1.95 < d < 2.05 for d in band), (ts, ds)


def test_counting_ds_agrees_across_family():
    # Universality: lattices, Delaunay, Gabriel, k-NN, medial quad
    # all land in (1.90, 2.15) at matched fit window -- same frozen
    # rule, one band (measured 1.926 .. 2.103).
    members = {
        "torus": build_torus_grid(60),
        "open": nx.convert_node_labels_to_integers(nx.grid_2d_graph(60, 60), ordering="sorted"),
        "tri": build_triangular_lattice(40),
        "hex": build_hex_lattice(40),
        "del": build_poisson_delaunay(6400, 80.0, 0),
        "gab": build_gabriel(6400, 80.0, 0),
        "knn": build_knn(6400, 80.0, 6, 0),
        "medial": build_medial_quad(1600, 40.0, 0),
    }
    for name, g in members.items():
        ds = counting_ds(low_spectrum(g))
        assert 1.90 < ds < 2.15, (name, ds)


def test_counting_ds_deterministic():
    # Seeded ARPACK start vector: bitwise-repeatable spectrum fits.
    g = build_poisson_delaunay(1600, 40.0, 0)
    a = low_spectrum(g, k=200)
    b = low_spectrum(g, k=200)
    assert np.max(np.abs(a - b)) == 0.0
    assert counting_ds(a) == counting_ds(b)
