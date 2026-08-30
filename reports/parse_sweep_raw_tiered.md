# Tiered parse sweep — reports/parse_sweep_raw.json

- Files: **1056**
- Fully clean under `runmat check`: **63** (6.0%)
- Parse without a syntax error: **221** (20.9%)
- Of the 993 failures:

  - **835** — Syntax — RunMat cannot read the file
  - **60** — Static analysis — parsed fine, refused by a rule MATLAB lacks
  - **6** — Lowering/MIR — parsed, failed to compile
  - **44** — Semantics — undefined names, shape and type mismatches
  - **48** — Unclassified


## Upper bound on what each blocker is worth

Each file reports only its first error, so a file counted here may
have further problems behind it. Read these as an ordering, not a
promise.

| First blocker | Files | Clean rate if fully fixed |
| --- | ---: | ---: |
| syntax | 834 | 85% |
| definite assignment (includes `global`) | 60 | 12% |
| undefined name (often a missing builtin) | 42 | 10% |
| brace indexing on a non-cell | 31 | 9% |

## Syntax — RunMat cannot read the file (835)

- 779 x — expected 'end'
    - `+backward_model/dynamic_model.m`
    - `+backward_model/forecast.m`
    - `+backward_model/initialize.m`
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
- 1 x — Syntax error at position 2765: expected '}' to close cell literal (found: ''='') (expected
    - `+pruned_SS/allVL1.m`

## Static analysis — parsed fine, refused by a rule MATLAB lacks (60)

- 44 x — local may be read before it is assigned
    - `+backward_model/simul_static_model.m`
    - `+gui/+perfect_foresight/run.m`
    - `+heterogeneity/check_steady_state_input.m`
- 16 x — local may be read before assignment on some control-flow paths
    - `+identification/checks_via_subsets.m`
    - `+occbin/IVF_core.m`
    - `+occbin/match_function.m`

## Lowering/MIR — parsed, failed to compile (6)

- 6 x — feval: function argument cannot be a comma-list expansion
    - `+backward_model/simul_nonlinear_model.m`
    - `ols/dyn_ols.m`
    - `olsgibbs.m`

## Semantics — undefined names, shape and type mismatches (44)

- 18 x — undefined variable 'filesep'
    - `+occbin/smoother_plots.m`
    - `estimation/posterior_analysis.m`
    - `estimation/smc/hssmc.m`
- 7 x — undefined variable 'isoctave'
    - `+occbin/+ppf/engine.m`
    - `ms-sbvar/delete_dir_if_exists.m`
    - `ms-sbvar/plot_ms_variance_decomposition.m`
- 3 x — undefined variable 'ispc'
    - `perfect-foresight-models/@pardiso/pardiso.m`
    - `reporting/@report_graph/writeGraphFile.m`
    - `reporting/@report_series/writeSeriesForGraph.m`
- 2 x — undefined variable 'skipline'
    - `+heterogeneity/load_steady_state.m`
    - `model_info.m`
- 2 x — undefined variable 'remove_fractional_xticks'
    - `+heterogeneity/plot_irfs.m`
    - `+heterogeneity/plot_simulation.m`
- 2 x — tensor literal rows must have consistent column counts
    - `+identification/get_jacobians.m`
    - `discretionary_policy/discretionary_policy_engine.m`
- 1 x — undefined variable 'warning_config'
    - `dynare.m`
- 1 x — undefined variable 'gcp'
    - `estimation/posterior_sampler_core.m`
- 1 x — undefined variable 'funobj'
    - `estimation/smc/dime.m`
- 1 x — undefined variable 'Gamma_t_t'
    - `kalman/likelihood/kalman_filter_pruned_skewed.m`
- 1 x — undefined variable 'log_dF'
    - `kalman/likelihood/missing_observations_kalman_filter.m`
- 1 x — undefined variable 'Fhat'
    - `ms-sbvar/ms_sbvar_setup.m`

## Unclassified (48)

- 31 x — brace indexing requires a cell-like value
    - `+heterogeneity/simulate_irfs.m`
    - `+heterogeneity/simulate_news_shocks.m`
    - `+heterogeneity/simulate_stochastic_shocks.m`
- 15 x — (no message)
    - `+identification/get_minimal_state_representation.m`
    - `cherrypick.m`
    - `distributions/gaussian/gaussian_log_mvncdf_mendell_elston.m`
- 1 x — index for dimension 2 is outside the proven bound 0
    - `+occbin/kalman_update_algo_3.m`
- 1 x — operator is not defined for the proven operand value category
    - `kalman/kalman_smoother_pruned_skewed.m`
