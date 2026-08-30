%% xfail: filesep() is not implemented — used in 118 Dynare files
s = filesep;
fprintf('%d\n', ischar(s) && numel(s) == 1);
