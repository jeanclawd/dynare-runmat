%% xfail: ispc()/isunix() are not implemented
fprintf('%d\n', (ispc + isunix) >= 1);
