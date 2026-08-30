%% xfail: RunMat requires the struct to exist before a field is assigned
s.a = 1;
fprintf('%d\n', s.a);
