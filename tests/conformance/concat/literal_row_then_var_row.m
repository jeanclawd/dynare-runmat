%% xfail: a bare variable row is counted as one column against a multi-element literal row
a = [3 4];
M = [1 2; a];
fprintf('%d %d\n', size(M, 1), size(M, 2));
