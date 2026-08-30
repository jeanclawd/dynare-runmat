A = reshape(1:6, 2, 3);
fprintf('%d %d\n', A(2, 3), size(permute(A, [2 1]), 1));
