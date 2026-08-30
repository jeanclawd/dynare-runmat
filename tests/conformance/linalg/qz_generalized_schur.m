%% xfail: qz() missing — this is Dynare's first-order perturbation solver
A = [4 1; 2 3];
B = eye(2);
[AA, BB, Q, Z] = qz(A, B);
fprintf('%d\n', norm(Q * A * Z - AA) < 1e-8);
