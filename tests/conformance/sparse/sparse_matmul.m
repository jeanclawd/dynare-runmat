%% xfail: mtimes() rejects sparse operands
S = sparse(eye(3));
fprintf('%d\n', norm(full(S * S) - eye(3)) < 1e-12);
