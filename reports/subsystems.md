# Dynare subsystems by RunMat parse rate

Source: `reports/parse_sweep_shimmed.json`. Directories with at least 8 files.

| Subsystem | Clean | Files | Rate | Most common blocker |
| --- | ---: | ---: | ---: | --- |
| `AIM` | 7 | 10 | 70% |  |
| `distributions` | 13 | 26 | 50% | local may be read before it is assigned |
| `utilities` | 26 | 52 | 50% | local may be read before assignment on some control-flow pat |
| `ms-sbvar` | 22 | 46 | 48% | undefined variable 'filesep' |
| `moments` | 5 | 13 | 38% | brace indexing requires a cell-like value |
| `+identification` | 11 | 29 | 38% | local may be read before assignment on some control-flow pat |
| `nonlinear-filters` | 9 | 25 | 36% | local may be read before assignment on some control-flow pat |
| `reporting` | 22 | 62 | 35% | brace indexing requires a cell-like value |
| `missing` | 19 | 56 | 34% | local may be read before it is assigned |
| `(root)` | 46 | 158 | 29% | local may be read before it is assigned |
| `optimization` | 10 | 35 | 29% | local may be read before assignment on some control-flow pat |
| `stochastic_solver` | 5 | 18 | 28% | local may be read before it is assigned |
| `@dprior` | 8 | 29 | 28% | local may be read before it is assigned |
| `perfect-foresight-models` | 8 | 31 | 26% | local may be read before assignment on some control-flow pat |
| `+occbin` | 12 | 48 | 25% | local may be read before it is assigned |
| `shock_decomposition` | 3 | 13 | 23% | local may be read before it is assigned |
| `ep` | 4 | 19 | 21% | local may be read before it is assigned |
| `kalman` | 5 | 26 | 19% | local may be read before it is assigned |
| `+gsa` | 5 | 27 | 19% | local may be read before assignment on some control-flow pat |
| `estimation` | 23 | 127 | 18% | undefined variable 'filesep' |
| `accessors` | 3 | 20 | 15% | local may be read before it is assigned |
| `+mom` | 2 | 16 | 12% | brace indexing requires a cell-like value |
| `parallel` | 3 | 24 | 12% | undefined variable 'ispc' |
| `+backward_model` | 1 | 9 | 11% | local may be read before it is assigned |
| `partial_information` | 1 | 9 | 11% | tensor literal rows must have consistent column counts |
| `+heterogeneity` | 1 | 10 | 10% | local may be read before it is assigned |
| `+pruned_SS` | 1 | 10 | 10% | local may be read before assignment on some control-flow pat |
| `backward` | 1 | 10 | 10% | local may be read before it is assigned |
| `+pac` | 1 | 12 | 8% | local may be read before it is assigned |
| `cli` | 0 | 11 | 0% | local may be read before it is assigned |
| `ols` | 0 | 12 | 0% | local may be read before it is assigned |
