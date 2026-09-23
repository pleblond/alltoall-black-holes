"""All:all entanglement graph model of black holes."""
from bh_graph.graphs import build_complete, build_chain, build_grid_2d, build_random_regular
from bh_graph.scrambling import infection_time, scrambling_scaling, graph_diameter, mean_path_length, spectral_gap
from bh_graph.horizon import horizon_area, horizon_radius, k_from_mass_schwarzschild, monogamy_frontier
from bh_graph.micro import critical_k, embedding_radius, is_pointlike, quantized_area, growth_trajectory
from bh_graph.circuits import circuit_cover_time, mean_cover_time, predicted_alltoall_log, circuit_scaling
from bh_graph.maxent import (
    maxent_k_linear, selfconsistent_k_quadratic, legs_per_node,
    fixed_point_iteration, random_tensor_page_saturation, bekenstein_check,
)
from bh_graph.qes import (
    qes_candidates, qes_page_k, qes_dominant, has_qes_transition,
    build_core_boundary_flow, min_cut_value, min_cut_scaling,
)
from bh_graph.evaporation import page_curve_bits, page_time, evaporate, is_evaporated
from bh_graph.qec import recovery_error, recovery_fidelity, recovery_threshold, is_recoverable
from bh_graph.robustness import log_slope_vs_p, quadratic_coefficient, qes_phase_boundary, all_quadratic
from bh_graph.kerr import kerr_newman_area, kerr_newman_k, spin_budget_fraction, is_subextremal, is_extremal
from bh_graph.haar import (
    harmonic, page_entropy_exact_nats, page_entropy_exact_bits, page_curve_exact_bits,
    page_deficit_at_turnover, haar_state, subsystem_entropy_bits, haar_entropy_samples,
)
from bh_graph.monogamy import (
    psi_family, rho_ab, concurrence_2qubit, one_tangle, interior_pairwise_c2,
    exterior_tangle, ckw_deficit, frontier,
)
from bh_graph.otoc import (
    otoc_alltoall, otoc_chain_avg, scrambling_time_lyapunov,
    scrambling_time_ballistic, early_growth_rate,
)
from bh_graph.pheno import (
    pbh_lifetime_planck, pbh_mass_evaporating_today, echo_delay_toy,
    echo_delay_from_legs, is_pointlike_pbh, shadow_deviation_bound,
    eht_consistent,
)
from bh_graph.tn import (
    min_rule, minimal_k_for_bulk, random_star_boundary_entropy,
    mean_star_entropy, eps_from_qes_matching, eps_from_crossover, crossover_scale,
)
from bh_graph.kerrpage import trajectories, kerr_page, page_time_fraction, peak_entropy
from bh_graph.syk import (
    majoranas, syk_hamiltonian, ising_chain_hamiltonian, otoc_curve,
    scrambling_time_threshold,
)
from bh_graph.data import (
    M_SUN_PLANCK, BUNDLED_EVENTS, m_sun_to_planck, k_schwarzschild_sun,
    leg_creation, area_theorem_holds, fetch_catalog_events, load_events,
    catalog_leg_audit,
)
from bh_graph.litcompare import (
    LITERATURE, grid_diameter_prediction, head_to_head, hierarchy_holds,
)
from bh_graph.tev import (
    l_d_meters, rs_add_meters, k_add, k_crit_tev, is_pointlike_lhc,
    thermal_null_scan,
)
from bh_graph.echoes import (
    echo_delay_sec, echo_delay_from_k, inside_typical_window, event_echo_table,
)

__all__ = [
    "build_complete", "build_chain", "build_grid_2d", "build_random_regular",
    "infection_time", "scrambling_scaling", "graph_diameter", "mean_path_length", "spectral_gap",
    "horizon_area", "horizon_radius", "k_from_mass_schwarzschild", "monogamy_frontier",
    "critical_k", "embedding_radius", "is_pointlike", "quantized_area", "growth_trajectory",
    "circuit_cover_time", "mean_cover_time", "predicted_alltoall_log", "circuit_scaling",
    "maxent_k_linear", "selfconsistent_k_quadratic", "legs_per_node",
    "fixed_point_iteration", "random_tensor_page_saturation", "bekenstein_check",
    "qes_candidates", "qes_page_k", "qes_dominant", "has_qes_transition",
    "build_core_boundary_flow", "min_cut_value", "min_cut_scaling",
    "page_curve_bits", "page_time", "evaporate", "is_evaporated",
    "recovery_error", "recovery_fidelity", "recovery_threshold", "is_recoverable",
    "log_slope_vs_p", "quadratic_coefficient", "qes_phase_boundary", "all_quadratic",
    "kerr_newman_area", "kerr_newman_k", "spin_budget_fraction", "is_subextremal", "is_extremal",
    "harmonic", "page_entropy_exact_nats", "page_entropy_exact_bits", "page_curve_exact_bits",
    "page_deficit_at_turnover", "haar_state", "subsystem_entropy_bits", "haar_entropy_samples",
    "psi_family", "rho_ab", "concurrence_2qubit", "one_tangle", "interior_pairwise_c2",
    "exterior_tangle", "ckw_deficit", "frontier",
    "otoc_alltoall", "otoc_chain_avg", "scrambling_time_lyapunov",
    "scrambling_time_ballistic", "early_growth_rate",
    "pbh_lifetime_planck", "pbh_mass_evaporating_today", "echo_delay_toy",
    "echo_delay_from_legs", "is_pointlike_pbh", "shadow_deviation_bound",
    "eht_consistent",
    "min_rule", "minimal_k_for_bulk", "random_star_boundary_entropy",
    "mean_star_entropy", "eps_from_qes_matching", "eps_from_crossover", "crossover_scale",
    "trajectories", "kerr_page", "page_time_fraction", "peak_entropy",
    "majoranas", "syk_hamiltonian", "ising_chain_hamiltonian", "otoc_curve",
    "scrambling_time_threshold",
    "M_SUN_PLANCK", "BUNDLED_EVENTS", "m_sun_to_planck", "k_schwarzschild_sun",
    "leg_creation", "area_theorem_holds", "fetch_catalog_events", "load_events",
    "catalog_leg_audit",
    "LITERATURE", "grid_diameter_prediction", "head_to_head", "hierarchy_holds",
    "l_d_meters", "rs_add_meters", "k_add", "k_crit_tev", "is_pointlike_lhc",
    "thermal_null_scan",
    "echo_delay_sec", "echo_delay_from_k", "inside_typical_window", "event_echo_table",
]
