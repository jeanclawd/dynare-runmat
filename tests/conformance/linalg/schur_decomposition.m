%% xfail: schur() is not implemented in RunMat 0.6.2
A = [4 1; 2 3];
[U, T] = schur(A);
fprintf('%d\n', norm(U * T * U' - A) < 1e-10);
