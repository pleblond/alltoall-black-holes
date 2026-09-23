from bh_graph.monitor import (
    combined_alive, alpha_from_dtau, universality_chi2, universality_verdict,
)


def test_combined_currently_alive():
    assert combined_alive()
    assert not combined_alive(0.05, 0.2)  # hypothetical excluding zero


def test_alpha_conversion():
    assert alpha_from_dtau(0.0) == 11.24
    assert alpha_from_dtau(-0.2) < 11.24 < alpha_from_dtau(0.1)


def test_empty_is_awaiting_not_pass():
    assert universality_verdict([]) == "awaiting O4/O5 per-event ringdown rows"


def test_scatter_kills_consensus_lives():
    good = [
        {"name": "a", "mf_msun": 60.0, "tau_s": 0.0033, "sigma_s": 0.0005},
        {"name": "b", "mf_msun": 40.0, "tau_s": 0.0022, "sigma_s": 0.0004},
        {"name": "c", "mf_msun": 80.0, "tau_s": 0.0044, "sigma_s": 0.0006},
    ]
    assert universality_verdict(good).startswith("alive")
    bad = [dict(good[0]), dict(good[1]),
           {"name": "c", "mf_msun": 80.0, "tau_s": 0.0090, "sigma_s": 0.0006}]
    assert universality_verdict(bad).startswith("KILL")
