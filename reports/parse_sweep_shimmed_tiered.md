# Tiered parse sweep — reports/parse_sweep_shimmed.json

- Files: **1056**
- Fully clean under `runmat check`: **294** (27.8%)
- Parse without a syntax error: **998** (94.5%)
- Of the 762 failures:

  - **58** — Syntax — RunMat cannot read the file
  - **361** — Static analysis — parsed fine, refused by a rule MATLAB lacks
  - **11** — Lowering/MIR — parsed, failed to compile
  - **200** — Semantics — undefined names, shape and type mismatches
  - **132** — Unclassified


## Upper bound on what each blocker is worth

Each file reports only its first error, so a file counted here may
have further problems behind it. Read these as an ordering, not a
promise.

| First blocker | Files | Clean rate if fully fixed |
| --- | ---: | ---: |
| definite assignment (includes `global`) | 361 | 62% |
| undefined name (often a missing builtin) | 188 | 46% |
| brace indexing on a non-cell | 88 | 36% |
| syntax | 57 | 33% |

## Syntax — RunMat cannot read the file (58)

- 13 x — expected identifier
    - `+mom/objective_function.m`
    - `+occbin/IVF_posterior.m`
    - `estimation/dsge_conditional_likelihood_1.m`
- 11 x — expected '('
    - `collapse_figures_in_tabgroup.m`
    - `distributions/prior_dist_names.m`
    - `latex/collect_latex_files.m`
- 8 x — expected identifier or '~'
    - `+gsa/map_calibration.m`
    - `+gsa/map_identification.m`
    - `+gsa/monte_carlo_filtering.m`
- 4 x — expected '}' to close cell literal
    - `+bvar/forecast.m`
    - `check_matlab_path.m`
    - `ols/create_sur_report.m`
- 3 x — unexpected token: Minus
    - `+occbin/set_default_options.m`
    - `model_diagnostics.m`
    - `perfect-foresight-models/sim1.m`
- 2 x — unexpected token: RBrace
    - `+mom/run.m`
    - `estimation/dynare_estimation_1.m`
- 2 x — unexpected token: RBracket
    - `+pac/+estimate/iterative_ols.m`
    - `parallel/dynareParallelRmDir.m`
- 2 x — unexpected token: Newline
    - `convergence_diagnostics/mcmc_diagnostics.m`
    - `perfect-foresight-models/perfect_foresight_solver.m`
- 2 x — expected ']'
    - `estimation/compute_Pinf_Pstar.m`
    - `partial_information/PI_qzswitch.m`
- 2 x — expected '='
    - `missing/mex/local_state_space_iterations/local_state_space_iteration_2.m`
    - `missing/stats/wblinv.m`
- 2 x — expected 'end'
    - `octave_ver_less_than.m`
    - `writecellofchar.m`
- 1 x — Syntax error at position 2765: expected '}' to close cell literal (found: ''='') (expected
    - `+pruned_SS/allVL1.m`

## Static analysis — parsed fine, refused by a rule MATLAB lacks (361)

- 217 x — local may be read before it is assigned
    - `+backward_model/forecast.m`
    - `+backward_model/irf.m`
    - `+backward_model/simul_static_model.m`
- 144 x — local may be read before assignment on some control-flow paths
    - `+backward_model/dynamic_model.m`
    - `+backward_model/initialize.m`
    - `+bgp/write.m`

## Lowering/MIR — parsed, failed to compile (11)

- 7 x — feval: function argument cannot be a comma-list expansion
    - `+backward_model/simul_nonlinear_model.m`
    - `+equation/evaluate.m`
    - `ols/dyn_ols.m`
- 3 x — parallel-region MIR requires the structured scheduler lowering capability
    - `@dprior/densities.m`
    - `ep/extended_path_mc.m`
    - `estimation/smc/smc_samplers_initialization.m`
- 1 x — MIR workspace-first call fallback policy None is not supported for static callee BoundFunc
    - `estimation/prior_analysis.m`

## Semantics — undefined names, shape and type mismatches (200)

- 76 x — undefined variable 'filesep'
    - `+backward_model/shock_decomposition.m`
    - `+gsa/scatter_plots.m`
    - `+gsa/stability_mapping_bivariate.m`
- 46 x — undefined variable 'isoctave'
    - `+estimate/nls.m`
    - `+gsa/log_transform.m`
    - `+gsa/scatter_mcf.m`
- 12 x — tensor literal rows must have consistent column counts
    - `+identification/get_jacobians.m`
    - `accessors/set_shock_skew_value.m`
    - `discretionary_policy/discretionary_policy_engine.m`
- 12 x — undefined variable 'ispc'
    - `isolder.m`
    - `parallel/AnalyseComputationalEnvironment.m`
    - `parallel/GiveCPUnumber.m`
- 6 x — undefined variable 'remove_fractional_xticks'
    - `+heterogeneity/plot_irfs.m`
    - `+heterogeneity/plot_simulation.m`
    - `+mom/graph_comparison_irfs.m`
- 3 x — undefined variable 'skipline'
    - `+heterogeneity/load_steady_state.m`
    - `+mom/matched_irfs_blocks.m`
    - `model_info.m`
- 1 x — undefined variable 'model_moments'
    - `+mom/mode_compute_gmm_smm.m`
- 1 x — undefined variable 'prior_dist_names'
    - `+mom/mode_compute_irf_matching.m`
- 1 x — undefined variable 'all_simulated_regimes'
    - `+occbin/+ppf/simulated_density.m`
- 1 x — undefined variable 'do_resample'
    - `+occbin/+ppf/state_importance_sampling.m`
- 1 x — undefined variable 'skip'
    - `+occbin/irf.m`
- 1 x — undefined variable 'all_updated_regimes'
    - `+occbin/pkf_conditional_density.m`

## Unclassified (132)

- 88 x — brace indexing requires a cell-like value
    - `+backward_model/inversion.m`
    - `+forecasts/graph.m`
    - `+gsa/monte_carlo_moments.m`
- 34 x — (no message)
    - `+identification/checks.m`
    - `+identification/get_minimal_state_representation.m`
    - `+identification/legacy_idx.m`
- 2 x — index for dimension 2 is outside the proven bound 0
    - `+identification/legacy_dynamic_g2p.m`
    - `+occbin/kalman_update_algo_3.m`
- 2 x — operator is not defined for the proven operand value category
    - `estimation/check_for_calibrated_covariances.m`
    - `kalman/kalman_smoother_pruned_skewed.m`
- 1 x — index for dimension 2 is outside the proven bound 2
    - `+identification/legacy_dynamic_g1pp.m`
- 1 x — right-division column dimensions 1 and 2 do not agree
    - `convergence_diagnostics/geweke_chi2_test.m`
- 1 x — transpose requires a numeric, logical, or character value
    - `ep/ep_problem_0.m`
- 1 x — call requests 3 outputs but at most 1 are available
    - `optimal_policy/dyn_ramsey_static.m`
- 1 x — non-concatenated dimension 1 disagrees across inputs (0 versus 1)
    - `perfect-foresight-models/perfect_foresight_with_expectation_errors_setup.m`
- 1 x — member access requires a struct or object value
    - `utilities/general/clean_current_folder.m`
