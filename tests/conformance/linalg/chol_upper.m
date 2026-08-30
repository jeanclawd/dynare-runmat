R = chol([4 2; 2 3]);
fprintf('%d\n', norm(R' * R - [4 2; 2 3]) < 1e-10);
