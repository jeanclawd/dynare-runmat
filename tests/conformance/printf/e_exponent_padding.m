%% xfail: %e prints 'e3' instead of the signed two-digit 'e+03'
fprintf('[%e]\n', 1234.5);
