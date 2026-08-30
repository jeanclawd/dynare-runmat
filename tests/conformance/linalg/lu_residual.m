A = [4 3; 6 3];
[L, U, P] = lu(A);
fprintf('%d\n', norm(L * U - P * A) < 1e-10);
