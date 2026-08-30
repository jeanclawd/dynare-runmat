%% xfail: %e prints 'e3' instead of MATLAB's signed 2-digit 'e+03' exponent
fprintf('%5.3f|%e|%g\n', 3.14159, 1234.5, 0.0001);
