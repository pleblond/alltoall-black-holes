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
from bh_graph.posteriors import (
    z_from_dl, kerr_legs_msun, load_overall_posterior,
    source_masses_and_spins, delta_legs_posterior, median_analysis,
    GW150914_FILE,
)
from bh_graph.ds import (
    lambda_planck, ds_entropy, ds_legs, stellar_bh_total_legs,
    smbh_total_legs, nariai_radius_planck, cosmic_budget_dominates,
)
from bh_graph.krylov import (
    lanczos, spread_complexity, peak_time, initial_rise_slope,
)
from bh_graph.collapse import (
    collapse_graph, order_parameters, collapse_sweep, erasure_lcc_diameter,
    is_fast_scrambler,
)
from bh_graph.cosmic import (
    scale_factor, event_horizon_meters, cosmic_legs, ds_scrambling_gyr,
    universe_scrambled,
)
from bh_graph.lunch import lunch_trajectory, lunch_overtake_step, lunch_diverges
from bh_graph.remnant import (
    pbh_lifetime_s, evaporation_temp_ev, omega_remnant,
    required_beta_for_dm, remnant_dm_viable,
)
from bh_graph.bounds import (
    t_form_s, t_form_temp_ev, f_to_beta, load_bound, bound_envelope_beta,
    remnant_exclusion_ratio, remnant_ruled_out_everywhere, EVAPORATION_BOUNDS,
)
from bh_graph.healing import (
    tau_heal_sec, relax_area, merger_step_response, scrambling_time_s,
    timescale_ladder, healing_energy_fraction, is_adiabatic,
    alpha_heal_bounds, alpha_allowed,
)
from bh_graph.mss import (
    lmg_hamiltonian, thermal_otoc, fit_lyapunov, mss_ratio, mss_scan,
)
from bh_graph.bigsyk import (
    sparse_majoranas, sparse_syk, sparse_ising, typicality_otoc, scaling_big,
)
from bh_graph.mp import (
    mp_edges, mp_density, star_spectrum, spectrum_moments, mp_predicted_var,
)
from bh_graph.greybody import (
    transmission, leg_emission, suppression_ratio, is_unsuppressed,
)
from bh_graph.congestion import (
    congestion, needs_bubble, bubble_radius, k_crit_footprint, phase,
    footprint_needed,
)
from bh_graph.charge import (
    protected_legs, evaporate_charged, endpoint, remnant_mass_planck,
    respects_extremality_bound,
)
from bh_graph.bandwidth import (
    remaining_info, info_per_leg, evacuates_cleanly, baby_inventory,
    evacuation_trajectory,
)
from bh_graph.gridcirc import (
    grid_cover_time, grid_mean_cover, quench_prediction, af_verdict,
)
from bh_graph.monitor import (
    combined_alive, alpha_from_dtau, universality_chi2, universality_verdict,
)
from bh_graph.selfattack import (
    violation_scan, violations_grow, s_leg_random, s_leg_ising,
    qes_assumption_holds,
)
from bh_graph.lhc import (
    regime, thermal_onset_mass, predicted_spectrum, hardness_ratio,
    lhc_kill_check, BENCHMARKS,
)
from bh_graph.concentration import (
    mass_from_k_msun, freefall_myr, eddington_myr, footprint_track,
    pop_event, pop_beats_eddington,
)
from bh_graph.ps import (
    growth_factor, sigma_mz, ps_cumulative, supply_vs_demand,
    structure_kills, occupation_fraction,
)
from bh_graph.emd import (
    t_form_s, t_form_temp_ev, m_to_planck, beta_domination, omega_rd,
    omega_emd, omega, required_beta_rd, emd_sweet_spot, remnant_status,
)
from bh_graph.viability import (
    evaporated, allowed_omega, viability, viability_curve,
)
from bh_graph.scatter import (
    mock_catalog, overmassive_fraction, tail_vs_fw, fw_required_for_tail,
    channel_killed_by_null, tail_slope,
)
from bh_graph.entropic import (
    screen_legs, screen_temperature, entropy_gradient, newton_force,
    newton_potential, link_flux, force_slope, kepler_period,
    leapfrog_orbit, orbit_closes,
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
    "z_from_dl", "kerr_legs_msun", "load_overall_posterior",
    "source_masses_and_spins", "delta_legs_posterior", "median_analysis",
    "GW150914_FILE",
    "lambda_planck", "ds_entropy", "ds_legs", "stellar_bh_total_legs",
    "smbh_total_legs", "nariai_radius_planck", "cosmic_budget_dominates",
    "lanczos", "spread_complexity", "peak_time", "initial_rise_slope",
    "collapse_graph", "order_parameters", "collapse_sweep", "erasure_lcc_diameter",
    "is_fast_scrambler",
    "scale_factor", "event_horizon_meters", "cosmic_legs", "ds_scrambling_gyr",
    "universe_scrambled",
    "lunch_trajectory", "lunch_overtake_step", "lunch_diverges",
    "pbh_lifetime_s", "evaporation_temp_ev", "omega_remnant",
    "required_beta_for_dm", "remnant_dm_viable",
    "t_form_s", "t_form_temp_ev", "f_to_beta", "load_bound", "bound_envelope_beta",
    "remnant_exclusion_ratio", "remnant_ruled_out_everywhere", "EVAPORATION_BOUNDS",
    "tau_heal_sec", "relax_area", "merger_step_response", "scrambling_time_s",
    "timescale_ladder", "healing_energy_fraction", "is_adiabatic",
    "alpha_heal_bounds", "alpha_allowed",
    "lmg_hamiltonian", "thermal_otoc", "fit_lyapunov", "mss_ratio", "mss_scan",
    "sparse_majoranas", "sparse_syk", "sparse_ising", "typicality_otoc", "scaling_big",
    "mp_edges", "mp_density", "star_spectrum", "spectrum_moments", "mp_predicted_var",
    "transmission", "leg_emission", "suppression_ratio", "is_unsuppressed",
    "congestion", "needs_bubble", "bubble_radius", "k_crit_footprint", "phase",
    "footprint_needed",
    "protected_legs", "evaporate_charged", "endpoint", "remnant_mass_planck",
    "respects_extremality_bound",
    "remaining_info", "info_per_leg", "evacuates_cleanly", "baby_inventory",
    "evacuation_trajectory",
    "grid_cover_time", "grid_mean_cover", "quench_prediction", "af_verdict",
    "combined_alive", "alpha_from_dtau", "universality_chi2", "universality_verdict",
    "violation_scan", "violations_grow", "s_leg_random", "s_leg_ising",
    "qes_assumption_holds",
    "regime", "thermal_onset_mass", "predicted_spectrum", "hardness_ratio",
    "lhc_kill_check", "BENCHMARKS",
    "mass_from_k_msun", "freefall_myr", "eddington_myr", "footprint_track",
    "pop_event", "pop_beats_eddington",
    "growth_factor", "sigma_mz", "ps_cumulative", "supply_vs_demand",
    "structure_kills", "occupation_fraction",
    "mock_catalog", "overmassive_fraction", "tail_vs_fw", "fw_required_for_tail",
    "channel_killed_by_null", "tail_slope",
    "t_form_s", "t_form_temp_ev", "m_to_planck", "beta_domination", "omega_rd",
    "omega_emd", "omega", "required_beta_rd", "emd_sweet_spot", "remnant_status",
    "evaporated", "allowed_omega", "viability", "viability_curve",
    "screen_legs", "screen_temperature", "entropy_gradient", "newton_force",
    "newton_potential", "link_flux", "force_slope", "kepler_period",
    "leapfrog_orbit", "orbit_closes",
]
