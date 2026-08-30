%% xfail: mldivide() rejects sparse operands
S = sparse([1 1; 0 1]);
b = [2; 1];
x = S \ b;
fprintf('%.1f\n', x);
