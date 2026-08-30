A = [4 1; 2 3];
[V, D] = eig(A);
fprintf('%d\n', norm(A * V - V * D) < 1e-10);
