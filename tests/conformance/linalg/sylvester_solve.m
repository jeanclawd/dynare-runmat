%% xfail: sylvester() missing — used for second-order solution terms
X = sylvester([1 0; 0 2], [3 0; 0 4], [1 1; 1 1]);
fprintf('%d\n', size(X, 1));
