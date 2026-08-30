%% xfail: ordqz() missing — required to split stable/unstable roots (Blanchard-Kahn)
A = [4 1; 2 3];
B = eye(2);
[AA, BB, Q, Z] = qz(A, B);
[~, ~, ~, Z2] = ordqz(AA, BB, Q, Z, 'udo');
fprintf('%d\n', size(Z2, 1));
