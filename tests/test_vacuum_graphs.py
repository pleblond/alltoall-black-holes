"""Vacuum graphs: regularity, counts, excursions, wrap control (prereg §1)."""
from itertools import pairwise

import networkx as nx

from bh_graph import vacuum_graphs as V


def test_family_validity_and_a15_excluded():
    for fam in ("cubic", "bcc", "fcc", "kelvin"):
        assert V.is_valid_family(fam)
    assert not V.is_valid_family("a15")
    assert not V.is_valid_family("weaire-phelan")
    assert not V.is_valid_family("")
    assert not V.is_valid_L("cubic", 4)  # below wrap-safe minimum
    assert V.is_valid_L("cubic", 5)
    assert not V.is_valid_L("a15", 8)


def test_builders_k_regular_and_counts():
    cases = [("cubic", 6, 6, 216), ("bcc", 5, 8, 250),
             ("fcc", 4, 12, 256), ("kelvin", 5, 14, 250)]
    for fam, L, k, n in cases:
        b = V.build_vacuum(fam, L)
        assert b["ok"], fam
        assert b["N"] == n == b["graph"].number_of_nodes(), fam
        assert b["k"] == k == V.K_VAC[fam], fam
        assert V.is_k_regular(b["graph"], k), fam
        assert b["center"] in b["graph"]
    assert V.build_vacuum("a15", 6)["ok"] is False
    assert V.build_vacuum("cubic", 2)["ok"] is False
    # BCC(k=8) != Kelvin(k=14) on the same sites: kelvin has more edges.
    b8 = V.build_vacuum("bcc", 5)["graph"]
    b14 = V.build_vacuum("kelvin", 5)["graph"]
    assert b8.number_of_nodes() == b14.number_of_nodes() == 250
    assert b14.number_of_edges() > b8.number_of_edges()
    assert b14.number_of_edges() == 250 * 14 // 2


def test_fcc_bcc_counts_scale():
    assert V.build_vacuum("bcc", 6)["N"] == 2 * 6 ** 3
    assert V.build_vacuum("fcc", 5)["N"] == 4 * 5 ** 3
    assert V.build_vacuum("cubic", 7)["N"] == 7 ** 3


def test_unwrapped_radius_monotone_and_pinned():
    # Pins from the shell-count isometry check (cubic: L/2 - 1).
    assert V.max_unwrapped_radius(V.build_vacuum("cubic", 6)) == 2
    assert V.max_unwrapped_radius(V.build_vacuum("cubic", 8)) == 3
    assert V.max_unwrapped_radius(V.build_vacuum("cubic", 10)) == 4
    assert V.max_unwrapped_radius(V.build_vacuum("cubic", 12)) == 5
    # Monotone in L for every family; prereg test-(ii) sizes clear r>=4.
    for fam, Ls in (("cubic", [6, 8, 10, 12]), ("bcc", [5, 6, 7, 8]),
                    ("fcc", [4, 5, 6, 7])):
        rs = [V.max_unwrapped_radius(V.build_vacuum(fam, L)) for L in Ls]
        assert all(b >= a for a, b in pairwise(rs)), (fam, rs)
    assert V.max_unwrapped_radius(V.build_vacuum("bcc", 8)) >= 4
    assert V.max_unwrapped_radius(V.build_vacuum("fcc", 7)) >= 4
    assert V.max_unwrapped_radius({"ok": False}) == 0


def test_e1_excursion_degrees_and_targets():
    b = V.build_vacuum("cubic", 8)
    e = V.apply_excursion(b, "E1", delta=2, seed=0)
    assert e["ok"]
    g = e["graph"]
    assert g.degree(e["center"]) == 6 + 2
    assert len(e["added"]) == 2
    # Targets sat at unperturbed distance >= 3 (locality of the protocol).
    d0 = dict(nx.single_source_shortest_path_length(b["graph"], e["center"]))
    for c, v in e["added"]:
        assert c == e["center"] and d0[v] >= 3
        assert g.degree(v) == 7
    assert V.apply_excursion(b, "E3")["ok"] is False  # no third protocol
    assert V.apply_excursion({"ok": False}, "E1")["ok"] is False


def test_e2_excursion_shell_plus_one():
    b = V.build_vacuum("cubic", 8)
    e = V.apply_excursion(b, "E2", seed=1)
    assert e["ok"]
    g = e["graph"]
    ball = [e["center"]] + list(b["graph"].neighbors(e["center"]))
    assert len(ball) == 7  # closed 1-ball on k=6
    for u in ball:
        assert g.degree(u) == 7  # each +1 edge


def test_radial_bins_structure():
    b = V.build_vacuum("cubic", 8)
    e = V.apply_excursion(b, "E1", delta=2, seed=0)
    bins = V.radial_bins(e["graph"], e["center"], 3)
    assert set(bins) == {1, 2, 3}
    assert len(bins[1]) == 8  # 6 lattice + 2 excursion edges
    # Radiality: endpoints differ in r by exactly 1.
    dist = nx.single_source_shortest_path_length(e["graph"], e["center"])
    for r, edges in bins.items():
        for u, v in edges:
            assert abs(dist[u] - dist[v]) == 1
            assert max(dist[u], dist[v]) == r
    assert V.radial_bins(e["graph"], e["center"], 0) == {}
