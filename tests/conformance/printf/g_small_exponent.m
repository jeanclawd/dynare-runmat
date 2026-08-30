%% xfail: %g prints '1.00000e-5': keeps trailing zeros and omits the two-digit exponent padding
fprintf('[%g]\n', 0.00001);
