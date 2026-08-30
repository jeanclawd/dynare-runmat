%% xfail: a bare variable row is counted as one column against a multi-element literal row
a = [3 4];
M = [a; 1 2];
fprintf('%d %d\n', size(M, 1), size(M, 2));
