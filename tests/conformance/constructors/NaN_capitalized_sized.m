%% xfail: NaN(...) is not callable as a constructor though nan(...) is; 188 Dynare files use the capitalized spelling
fprintf('%d %d\n', size(NaN(2, 3), 1), size(NaN(2, 3), 2));
