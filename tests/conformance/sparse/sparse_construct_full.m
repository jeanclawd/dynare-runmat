S = sparse([1 2], [2 1], [3 4], 2, 2);
F = full(S);
fprintf('%d %d %d\n', F(1, 2), F(2, 1), nnz(S));
