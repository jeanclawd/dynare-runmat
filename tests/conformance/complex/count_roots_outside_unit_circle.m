A = [2 0; 0 0.5];
d = eig(A);
fprintf('%d\n', sum(abs(d) > 1));
