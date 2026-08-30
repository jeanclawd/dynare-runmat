%% xfail: regexp(...,'tokens') does not return MATLAB's nested cell structure
t = regexp('x=12', '(\\w+)=(\\d+)', 'tokens');
fprintf('%s %s\n', t{1}{1}, t{1}{2});
